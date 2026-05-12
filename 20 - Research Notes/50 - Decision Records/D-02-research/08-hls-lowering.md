---
type: "research"
decision: "D-02"
angle: 8
---

## Scope

D-02 / Q-038 asks whether priority and round-robin dequeue grouping should preserve current hash-based compatibility or introduce an explicit grouped-dequeue IR construct (`20 - Research Notes/40 - Decision Queue.md:15-17`). For HLS, the important compatibility target is not the hash itself; it is the observable single-source dequeue event that Spatial currently synthesizes out of several per-FIFO nodes.

## Spatial Semantics

The frontend has no first-class grouped node today. `priorityDeq(fifo*)` stages one `FIFOPriorityDeq` per FIFO, tags each staged symbol with `fifo.head.toString.hashCode()`, and returns a `PriorityMux` over non-empty sources (`src/spatial/lang/api/PriorityDeqAPI.scala:10-20`). The conditional overload does the same after computing `shouldDequeue` from side conditions and earlier eligible FIFOs (`src/spatial/lang/api/PriorityDeqAPI.scala:25-50`). `roundRobinDeq` keeps the same `FIFOPriorityDeq` backend, but computes priorities as `(iter + idx) % size`, with the source comment saying lower priority wins (`src/spatial/lang/api/PriorityDeqAPI.scala:55-77`), and suppresses a lane when another enabled lane has lower priority (`src/spatial/lang/api/PriorityDeqAPI.scala:78-104`).

FIFO status and dequeue are separate staged operations: `isEmpty` stages `FIFOIsEmpty`, while `deq` stages `FIFODeq` (`src/spatial/lang/FIFO.scala:16-17`, `src/spatial/lang/FIFO.scala:52-56`). Dequeues are destructive in the IR effect model because `DequeuerLike` overrides effects to `Effects.Writes(mem)` (`src/spatial/node/HierarchyAccess.scala:78-80`). The priority path relies on codegen to add the missing current-FIFO non-empty guard: `FIFOBankedPriorityDeq` emits a read with extra `&& !$fifo.empty` (`src/spatial/codegen/chiselgen/ChiselGenMem.scala:324-326`). Thus the effective read enable is `should_dequeue_i && !empty_i`, and exactly one non-empty source should advance for a successful group event.

## HLS Shape

An HLS lowering should model this as a two-phase handshake over `hls::stream`-like endpoints: first probe `empty_i`, then perform one selected `read()` only when the group and downstream are ready. The names and exact blocking behavior of `hls::stream::empty()` / `read()` are HLS library claims and remain (unverified). The Spatial-derived rule is stronger than "emit all candidate reads and mux data": because dequeue mutates queue state, only the selected lane may read (`src/spatial/node/HierarchyAccess.scala:78-80`).

For fixed priority, compute `eligible_i = !empty_i && cond_i`, with `cond_i = true` for the varargs overload, and select the lowest-index eligible lane. For round-robin, compute the same eligibility but choose the eligible lane with minimal `(iter + idx) % n`, preserving the API's explicit `iter` input rather than inventing an internal rotating pointer (`src/spatial/lang/api/PriorityDeqAPI.scala:71-89`). The emitted C++ should naturally be an unrolled priority scan or selected-index switch, followed by one guarded read. If no lane is eligible, the group produces no value and no FIFO advances.

## Pressure Mapping

Current Chisel forward pressure already treats grouped priority FIFOs as alternatives. Ordinary read streams exclude `FIFOBankedPriorityDeq` (`src/spatial/metadata/control/package.scala:1360-1364`), while priority streams are grouped by `prDeqGrp.get` (`src/spatial/metadata/control/package.scala:1367-1375`). Generated pressure then ANDs groups, but ORs FIFOs inside each group, so a controller can fire when each group has at least one available alternative (`src/spatial/codegen/chiselgen/ChiselGenCommon.scala:258-263`). Top-level controller enable gates on forward pressure (`src/spatial/codegen/chiselgen/ChiselGenController.scala:390`).

Back-pressure is separate and comes from outbound stream readiness or FIFO fullness (`src/spatial/codegen/chiselgen/ChiselGenCommon.scala:266-278`), with controllers wiring both pressure signals into the generated block (`src/spatial/codegen/chiselgen/ChiselGenController.scala:308-309`). The HLS implementation should therefore make `can_fire = downstream_ready && any_eligible_in_each_group`; the concrete HLS full/ready idiom is (unverified). This gives bounded queue behavior without speculative underflow or unbounded software buffering.

## IR Implication

Hash-compatible lowering makes HLS codegen rediscover a single arbitration event from scattered dequeue nodes, side-condition expressions, a `PriorityMux`, and an integer metadata tag. That is fragile: the tag is only an `Int` wrapper (`src/spatial/metadata/access/AccessData.scala:37-43`), unrolling must copy it onto the banked access (`src/spatial/transform/unrolling/MemoryUnrolling.scala:303-304`, `src/spatial/transform/unrolling/MemoryUnrolling.scala:523-524`), and consumers assume it is present via `.get` (`src/spatial/metadata/control/package.scala:1374`). Hash collision behavior and JVM string hashing are (unverified) and not worth preserving as semantics.

Explicit grouped-dequeue IR makes HLS simpler and safer: one node can carry sources, conditions, mode (`priority` or `round_robin`), rank expression, and result value. The API can remain source-compatible while lowering immediately to that node or to an explicit group token. A legacy bridge can still import existing `PriorityDeqGroup(Int)` metadata for old passes, but the HLS contract should preserve semantic grouping, exactly-one destructive read, and OR-within-group pressure rather than hash identity.
