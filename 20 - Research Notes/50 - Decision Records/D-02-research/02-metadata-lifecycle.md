---
type: "research"
decision: "D-02"
angle: 2
---

# Scope

This angle traces `PriorityDeqGroup` as metadata rather than as first-class IR. The relevant lifecycle is small: definition/accessors, writers in the priority/round-robin dequeue API, mirroring defaults, explicit unrolling copy, and the downstream control query that groups inbound streams. Across the requested search terms, the group id appears only in those roles.

# Metadata Shape

`PriorityDeqGroup` is documented as a tag used to determine which priority dequeues are grouped together; its payload is a single `Int`, and the declared default is absent metadata rather than a sentinel value (`src/spatial/metadata/access/AccessData.scala:37-43`). The accessor surface is an `Option[Int]` getter, `prDeqGrp`, plus a setter that adds `PriorityDeqGroup(grp)` to symbol metadata (`src/spatial/metadata/access/package.scala:121-123`). There is no domain-specific clear/update API and no typed wrapper beyond the integer case class.

The metadata is declared with `SetBy.Analysis.Self` (`src/spatial/metadata/access/AccessData.scala:43`). In Argon, that set-by category maps to `Transfer.Mirror` (`argon/src/argon/Data.scala:51-56`), and the base `Data` constructor converts `SetBy` into that transfer policy (`argon/src/argon/Data.scala:71-79`). Because `PriorityDeqGroup` does not override `mirror`, the default mirror returns the same immutable data object (`argon/src/argon/Data.scala:78-79`). When a transformer explicitly calls `transferData`, mirrored metadata is added to the destination after applying `mirror(m)` (`argon/src/argon/transform/Transformer.scala:99-108`). So despite being named analysis metadata, this tag is generally transferable through normal transformer metadata transfer.

# Producers

The API writers currently use hash-based grouping. In the variadic `priorityDeq`, each staged `FIFOPriorityDeq` receives `fifo.head.toString.hashCode()` as its `prDeqGrp`; the nearby `ctx.line` group id is computed but commented as probably unsafe and not used (`src/spatial/lang/api/PriorityDeqAPI.scala:10-18`). The conditional-list overload repeats the same first-FIFO string hash assignment (`src/spatial/lang/api/PriorityDeqAPI.scala:25-50`). `roundRobinDeq` also stages `FIFOPriorityDeq` nodes and assigns `fifos.head.toString.hashCode` to each one (`src/spatial/lang/api/PriorityDeqAPI.scala:55-104`).

This means the group identity is not represented by the priority mux, the API call, or a group node. It is a side tag attached to each individual dequeue. All siblings created by one call share the first FIFO's current printed symbol string. No source in the searched sites guards against unrelated groups receiving the same integer or against the first FIFO's printed identity changing across transformations. Fixed-width hash collisions are possible in general (unverified).

# Consumer

The meaningful downstream consumer is `getReadPriorityStreams`. Regular read-stream collection explicitly excludes `FIFOBankedPriorityDeq` readers (`src/spatial/metadata/control/package.scala:1360-1364`). Priority stream collection then finds inbound memories whose readers include a banked priority dequeue in the same controller (`src/spatial/metadata/control/package.scala:1367-1373`) and groups those memories by the first banked priority dequeue reader's `prDeqGrp.get` (`src/spatial/metadata/control/package.scala:1374`).

That `.get` is important: by the time control metadata asks for priority streams, every relevant `FIFOBankedPriorityDeq` reader is expected to have a group id. Missing propagation is not treated as "ungrouped"; it is a runtime failure path. The grouping also happens from memory readers back to inbound FIFO sets, not from the original priority mux or API call structure.

# Propagation and Implication

Unrolling is the main explicit bridge from the source API nodes to the banked nodes consumed later. `FIFOPriorityDeq` is converted into `FIFOBankedPriorityDeq` in `bankedAccess` (`src/spatial/transform/unrolling/MemoryUnrolling.scala:523-524`), matching the source node definitions in `FIFO.scala` (`src/spatial/node/FIFO.scala:22-24`, `src/spatial/node/FIFO.scala:67-71`). During the broader unrolled-access rewrite, each generated symbol is assigned ports, dispatch/group metadata, `originalSym`, and then, if the original `lhs` has `prDeqGrp`, the new symbol receives the same integer (`src/spatial/transform/unrolling/MemoryUnrolling.scala:288-306`). The following `transferSyncMeta(lhs, s)` only copies wait/barrier synchronization metadata (`src/spatial/metadata/memory/package.scala:539-546`), so `prDeqGrp` preservation here is a deliberate separate copy rather than an incidental sync transfer.

For D-02, the compatibility story is therefore clear: preserving hash-based grouping requires keeping both the API assignment and the unrolling copy intact, because the current consumer expects metadata on banked priority-dequeue readers. The lifecycle is lightweight and already compatible with generic mirroring, but semantically brittle: group identity is an integer derived from a symbol string, not an explicit IR relationship. Explicit grouped-dequeue IR would remove the partial metadata dependency and make the grouping structural, but it would need to replace or adapt `getReadPriorityStreams` and the unrolling path that currently manufacture and preserve `FIFOBankedPriorityDeq` metadata.
