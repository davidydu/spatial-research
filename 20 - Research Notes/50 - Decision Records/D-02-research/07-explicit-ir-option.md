---
type: "research"
decision: "D-02"
angle: 7
---

# Explicit grouped-dequeue IR option

## Contract

The explicit option is to keep the DSL calls but stage one grouped dequeue operation instead of a loose cluster of scalar dequeues plus a result mux. A minimal pre-unroll contract could be:

```scala
GroupedFIFODeq[A](
  fifos: Seq[FIFO[A]],
  conds: Seq[Bit],
  policy: PriorityOrder | RoundRobin(iter: I32),
  emptyGuard: PerFifoGuard,
  result: A
)
```

The node's semantic result is "select at most one FIFO, destructively read that FIFO, and return the selected value." `fifos` and `conds` are parallel lists; `policy` distinguishes fixed priority from the rotating priority now computed from `(iter + idx) % fifos.size` in `roundRobinDeq` (`src/spatial/lang/api/PriorityDeqAPI.scala:55-89`). `emptyGuard` is explicit because current priority code deliberately omits `!f.isEmpty` from each dequeue enable to avoid II-analysis problems, then restores emptiness in the mux and later in Chisel emission (`src/spatial/lang/api/PriorityDeqAPI.scala:14-20`, `src/spatial/codegen/chiselgen/ChiselGenMem.scala:324-326`).

## Memory-Access Fit

This should extend the [[30 - Memory Accesses]] contract rather than bypass it. Today a pre-unroll `Dequeuer` is read-shaped through `localRead = Some(Read(mem, addr, ens))`, but `DequeuerLike` overrides effects to `Effects.Writes(mem)` because a dequeue mutates FIFO state (`src/spatial/node/HierarchyAccess.scala:65-80`, `src/spatial/node/HierarchyAccess.scala:91-94`). The grouped node therefore needs a multi-access view: one local read record per FIFO candidate, no address, a per-lane enable expression, and `effects = Effects.Writes(fifos: _*)`. That is source-compatible with Argon's effects data model, where `Effects.Writes` accepts varargs and stores a set of written mutable symbols (`argon/src/argon/Effects.scala:20-29`, `argon/src/argon/Effects.scala:86`).

Post-unroll, the grouped node can lower to `GroupedFIFOBankedDeq` with per-FIFO `enss`, or to today's `FIFOBankedPriorityDeq` ports as a compatibility bridge. The critical invariant is that each candidate FIFO remains a destructive read for dependence analysis; staging dependencies are computed from read/write effect sets and anti-dependencies, not from the future mux result (`argon/src/argon/static/Staging.scala:202-233`).

## Current Shape

The current API has no grouped IR node. Fixed priority stages one `FIFOPriorityDeq` per FIFO and then stages a `PriorityMux` over non-empty selectors and those dequeue results (`src/spatial/lang/api/PriorityDeqAPI.scala:13-20`). The conditional overload repeats that shape with a computed `shouldDequeue` list and a mux guarded by `!f.isEmpty && c` (`src/spatial/lang/api/PriorityDeqAPI.scala:31-50`). Round-robin also stages per-FIFO `FIFOPriorityDeq` nodes after computing rotated priorities, then returns a `PriorityMux` (`src/spatial/lang/api/PriorityDeqAPI.scala:71-104`).

The only group identity is metadata. `PriorityDeqGroup(grp: Int)` is documented as a tag for determining which priority dequeues are grouped together (`src/spatial/metadata/access/AccessData.scala:37-43`), and the API assigns that tag from the first FIFO's string hash (`src/spatial/lang/api/PriorityDeqAPI.scala:16-17`, `src/spatial/lang/api/PriorityDeqAPI.scala:46-47`, `src/spatial/lang/api/PriorityDeqAPI.scala:96-97`). Whether a given hash collision occurs is (unverified), but downstream grouping sees only equal integers.

## What Becomes Explicit

Analyses and codegen would no longer infer group membership from `prDeqGrp`. Today unrolling copies the metadata from the scalar access to the banked access, then lowers `FIFOPriorityDeq` to `FIFOBankedPriorityDeq` (`src/spatial/transform/unrolling/MemoryUnrolling.scala:303-304`, `src/spatial/transform/unrolling/MemoryUnrolling.scala:523-524`). Control metadata later finds inbound FIFOs by scanning for `FIFOBankedPriorityDeq` readers and groups them with `x.prDeqGrp.get` (`src/spatial/metadata/control/package.scala:1367-1374`). With grouped IR, that pass should read `group.fifos` or the grouped banked node directly.

Codegen would also stop rediscovering the selection policy from the combination of per-FIFO enables and `PriorityMux` selectors. `PriorityMux` is a primitive result chooser, not a memory-access node (`src/spatial/node/Mux.scala:39-56`), and backends emit it as either an `if`/`else if` chain or Chisel `PriorityMux` (`src/spatial/codegen/scalagen/ScalaGenBits.scala:39-45`, `src/spatial/codegen/chiselgen/ChiselGenMath.scala:230-232`). A grouped node would carry the policy and selected FIFO directly, while still allowing the final result to lower to the same mux structure.

## Consequence

This option is not hash-compatible in the accidental sense. It preserves the intended call-scoped grouping, per-FIFO destructive effects, deferred empty guard, and current forward-pressure shape: Chisel now ORs FIFO readiness within each priority group and ANDs across groups (`src/spatial/codegen/chiselgen/ChiselGenCommon.scala:258-263`). The change is that grouping, policy, and result membership become IR facts. Legacy metadata can still be emitted as a bridge, but new analyses should treat it as derived, not authoritative.
