---
type: "research"
decision: "D-02"
angle: 6
---

## Current key construction

The priority-dequeue APIs do not create an explicit group node. Each `FIFOPriorityDeq` staged inside the API call gets `prDeqGrp` metadata, and the value is the hash of the first FIFO's string form: `fifo.head.toString.hashCode()` for both priority overloads and `fifos.head.toString.hashCode` for round-robin (`src/spatial/lang/api/PriorityDeqAPI.scala:15-18`, `src/spatial/lang/api/PriorityDeqAPI.scala:44-48`, `src/spatial/lang/api/PriorityDeqAPI.scala:94-98`). The nearby `ctx.line` group id is still present but commented, with a source comment calling it "probably an unsafe way to compute a group id" (`src/spatial/lang/api/PriorityDeqAPI.scala:10-17`, `src/spatial/lang/api/PriorityDeqAPI.scala:25-27`). Thus the active compatibility surface is not source line identity; it is "same first FIFO string hash."

The metadata itself is just an `Int` wrapper: `PriorityDeqGroup(grp: Int)` (`src/spatial/metadata/access/AccessData.scala:37-43`), with accessors `sym.prDeqGrp` and `sym.prDeqGrp_=` (`src/spatial/metadata/access/package.scala:121-123`).

## What string identity is likely used

For ordinary FIFO allocation, `FIFO.apply` stages `FIFONew(depth)` (`src/spatial/lang/FIFO.scala:86-88`). `FIFO` is a `@ref` class extending `Ref[Queue[Any], FIFO[A]]` (`src/spatial/lang/FIFO.scala:10-12`), and `Ref.toString` is final. For node-backed symbols it prints `x$id`; for bound symbols it prints `b$id`; for params it prints `p$id (...)`; for constants it prints `Const(...)` (`argon/src/argon/Ref.scala:172-179`). Staging a node uses `Def.Node(state.nextId(), op)` (`argon/src/argon/static/Staging.scala:28-31`), and `nextId()` increments a private integer counter (`argon/src/argon/State.scala:71-74`).

So, for the normal `FIFO(...)` case, the group seed is likely a string such as `x42`, not the user's variable name, object address, memory contents, or FIFO type. This is local source evidence for the symbol-string part. The behavior of `String.hashCode`, including exact algorithm, width, determinism across JVMs, and collision properties, is JVM/Scala general knowledge and remains (unverified) here.

## Mirroring and stability

Once the `Int` is assigned, current Spatial tends to preserve it as metadata rather than recompute it from a mirrored FIFO. `PriorityDeqGroup` is `SetBy.Analysis.Self` (`src/spatial/metadata/access/AccessData.scala:43`), and `SetBy.Analysis.Self` maps to `Transfer.Mirror` (`argon/src/argon/Data.scala:51-56`). The default metadata mirror returns the same value (`argon/src/argon/Data.scala:78-79`), and transformer metadata transfer copies mirrored metadata to the destination symbol (`argon/src/argon/transform/Transformer.scala:99-106`). Memory unrolling also manually copies `lhs.prDeqGrp` onto the replacement symbol after creating banked accesses (`src/spatial/transform/unrolling/MemoryUnrolling.scala:303-306`), including the conversion from `FIFOPriorityDeq` to `FIFOBankedPriorityDeq` (`src/spatial/transform/unrolling/MemoryUnrolling.scala:523-524`).

This means "stable across mirroring" is true for the stored group integer, not for the expression `fifo.head.toString.hashCode` if recomputed later. A mirrored FIFO can receive a fresh node id because node staging uses `state.nextId()` (`argon/src/argon/static/Staging.scala:28-31`), and `toString` for a node is tied to that id (`argon/src/argon/Ref.scala:172-176`). Any Rust/HLS port that recomputes from post-mirror textual IDs would only accidentally match old grouping.

## Collision and absence failure modes

The group is consumed by `getReadPriorityStreams`: it filters inbound local memories whose readers include `FIFOBankedPriorityDeq`, then `groupBy`s those FIFOs using the first such reader's `prDeqGrp.get` (`src/spatial/metadata/control/package.scala:1368-1375`). Generated forward-pressure treats each group as an OR of available FIFOs, then ANDs the groups together (`src/spatial/codegen/chiselgen/ChiselGenCommon.scala:258-263`). TreeGen also prints these grouped streams as `prDeq[...]` (`src/spatial/codegen/treegen/TreeGen.scala:159-166`).

If two distinct logical dequeue groups hash to the same `Int`, they collapse into one `groupBy` bucket. The forward-pressure condition then changes from roughly `(one-ready-in-A) && (one-ready-in-B)` to `(one-ready-in-A-or-B)`, weakening the readiness gate. The local source directly shows the OR-per-group/AND-across-groups structure; the exact runtime symptom after a too-weak gate depends on downstream Chisel/Scala mux behavior and is (unverified). A missing group tag is another hard failure mode: the source uses `x.prDeqGrp.get` with no fallback (`src/spatial/metadata/control/package.scala:1374`); Scala `Option.get` throwing on `None` is (unverified), but the unchecked assumption is source-visible.

## Compatibility implication

Hash-compatible behavior would mean preserving the same partition of `FIFOBankedPriorityDeq` readers that the current `groupBy(prDeqGrp)` would produce, including intentional grouping by the same first FIFO string and accidental grouping by hash collision. That is a narrow and brittle compatibility target, because it depends on pre-transform symbol numbering plus JVM string hashing (unverified) rather than an IR fact.

For D-02, the safer compatibility line is semantic rather than hash-exact: preserve the intended grouping of the `FIFOPriorityDeq`s created by one priority/round-robin API expansion, and decide explicitly whether separate API expansions that share the same first FIFO should also share a group. An explicit grouped-dequeue IR or explicit group token can encode that contract directly. A legacy bridge could still import old `PriorityDeqGroup(Int)` metadata for existing Scala passes, but new IR should not treat hash collisions as behavior worth preserving.
