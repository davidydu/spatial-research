---
type: "research"
decision: "D-02"
angle: 1
---

# API Surface and Staging Semantics

## Decision Frame

D-02 / Q-038 is about the contract behind one source-level operation that expands into several IR reads. The decision queue states the fork directly: preserve the current hash-based compatibility behavior, or introduce an explicit grouped-dequeue IR construct for priority and round-robin dequeue grouping (`20 - Research Notes/40 - Decision Queue.md:15-17`). The open question names the current risk: all staged priority dequeue nodes get `prDeqGrp = fifo.head.toString.hashCode()`, and unrelated calls can be conflated if their group IDs collide (`20 - Research Notes/20 - Open Questions.md:565-577`). Because the surface API returns one `T`, the user-visible model is "choose one element from this call's FIFO set," not "manually coordinate several destructive reads."

## Public Overloads

The API exposes three helpers. The variadic `priorityDeq[T:Bits](fifo: FIFO[T]*)` takes only FIFOs and gives earlier arguments higher priority (`src/spatial/lang/api/PriorityDeqAPI.scala:10-23`). For fifo `i`, it stages `FIFOPriorityDeq(f, Set(prefixEmpty))`, where `prefixEmpty` is the AND of every prior FIFO's `isEmpty`; fifo 0 therefore has unconditional dequeue intent, while fifo `i` is intended only after all earlier FIFOs are empty (`src/spatial/lang/api/PriorityDeqAPI.scala:13-18`). The comment says the enable "should also have a !f.isEmpty" but this is deferred to codegen because it hurts II analysis (`src/spatial/lang/api/PriorityDeqAPI.scala:14-15`).

The conditional overload `priorityDeq[T:Bits](fifo: List[FIFO[T]], cond: List[Bit])` asserts equal lengths, computes `deqEnabled = !isEmpty && cond` for prior FIFOs, prefix-ORs those enables with `scanLeft(false)(_ || _)`, and uses `shouldDequeue = !priorEnabled && cond` (`src/spatial/lang/api/PriorityDeqAPI.scala:25-50`). Its final `PriorityMux` selector restores the current FIFO's non-empty guard with `!f.isEmpty && c` (`src/spatial/lang/api/PriorityDeqAPI.scala:50`). `roundRobinDeq` takes `fifos`, `ens`, and `iter`, assigns priority `(iter + idx) % N`, and dequeues a lane only when its enable is true and no enabled lane has a strictly lower rotated priority (`src/spatial/lang/api/PriorityDeqAPI.scala:55-104`).

## Staged Shape

None of the helpers stages a fused group node today. Each stages one scalar `FIFOPriorityDeq` per candidate FIFO and one `PriorityMux` over the candidate data (`src/spatial/lang/api/PriorityDeqAPI.scala:15-20`, `src/spatial/lang/api/PriorityDeqAPI.scala:44-50`, `src/spatial/lang/api/PriorityDeqAPI.scala:94-103`). The FIFO IR confirms `FIFOPriorityDeq` is just another `Dequeuer[A,A]`, with a separate banked form `FIFOBankedPriorityDeq` used later (`src/spatial/node/FIFO.scala:22-24`, `src/spatial/node/FIFO.scala:67-71`). `PriorityMux` itself is a primitive node; the Scala backend emits an `if` / `else if` chain in selector order, and Chiselgen emits Chisel `PriorityMux(List(sels), List(opts))` (`src/spatial/node/Mux.scala:39-57`, `src/spatial/codegen/scalagen/ScalaGenBits.scala:39-45`, `src/spatial/codegen/chiselgen/ChiselGenMath.scala:230-232`).

All three helpers wrap the staging block in `ForcedLatency(0.0)` (`src/spatial/lang/api/PriorityDeqAPI.scala:12`, `src/spatial/lang/api/PriorityDeqAPI.scala:28`, `src/spatial/lang/api/PriorityDeqAPI.scala:56`). `ForcedLatency` installs a staging flow that writes `forcedLatency = latency` onto each staged symbol, and `fullDelay` prefers this metadata over analyzed delay (`src/spatial/lang/Latency.scala:7-10`, `src/spatial/metadata/retiming/package.scala:17-20`, `src/spatial/metadata/retiming/package.scala:33-35`). The implied API contract is same-cycle arbitration: the FIFO emptiness checks, destructive reads, and muxed result should not be separated by retiming.

## Grouping Metadata

The grouping mechanism is metadata, not type structure. `PriorityDeqGroup(grp: Int)` exists solely to tag which priority dequeues belong together (`src/spatial/metadata/access/AccessData.scala:37-43`), and `sym.prDeqGrp` is an optional `Int` getter/setter (`src/spatial/metadata/access/package.scala:121-123`). Each helper assigns that field from the first FIFO's `toString.hashCode`; the file even computes `gid = ctx.line` with a TODO saying it is unsafe, but leaves it unused (`src/spatial/lang/api/PriorityDeqAPI.scala:10-17`, `src/spatial/lang/api/PriorityDeqAPI.scala:25-28`, `src/spatial/lang/api/PriorityDeqAPI.scala:96-98`). A 32-bit hash collision cannot be ruled out by construction (unverified).

Downstream passes make the metadata load-bearing. Memory unrolling copies `prDeqGrp` from the scalar access to the replacement access, and lowers `FIFOPriorityDeq` to `FIFOBankedPriorityDeq` (`src/spatial/transform/unrolling/MemoryUnrolling.scala:303-304`, `src/spatial/transform/unrolling/MemoryUnrolling.scala:523-524`). Control metadata excludes banked priority dequeues from regular read streams and then groups priority input FIFOs by `prDeqGrp.get` (`src/spatial/metadata/control/package.scala:1360-1374`). Chisel forward pressure then ORs FIFO availability within a priority group and ANDs across groups, so the grouping affects controller run conditions (`src/spatial/codegen/chiselgen/ChiselGenCommon.scala:249-263`). Codegen also adds the deferred `&& !fifo.empty` guard for `FIFOBankedPriorityDeq` reads (`src/spatial/codegen/chiselgen/ChiselGenMem.scala:324-326`).

## Contract Implication

For the DSL API, the strongest source-backed contract is call-scoped grouped dequeue: one API call stages multiple destructive read candidates, one result mux, one zero-latency arbitration scope, and one shared group tag. Hash identity is compatibility behavior, not an expressible user feature. Preserving it would reproduce accidental cross-call grouping when IDs match; explicit grouped-dequeue IR would encode the surface contract directly and can still lower to today's per-FIFO nodes plus stable group metadata for legacy passes.
