---
type: "research"
decision: "D-22"
angle: 9
topic: "policy-options-contract"
---

# D-22 Angle 9: Policy Options And Semantic Contract

## Evidence Boundary

D-22 needs a semantic contract, not just a container implementation. ScalaGen is the elastic value reference: FIFO becomes `mutable.Queue`, LIFO becomes `mutable.Stack`, and StreamIn/StreamOut become queues (`src/spatial/codegen/scalagen/ScalaGenFIFO.scala:12-18`; `src/spatial/codegen/scalagen/ScalaGenLIFO.scala:12-18`; `src/spatial/codegen/scalagen/ScalaGenStream.scala:12-16`). It can observe capacity through `isFull`, `almostFull`, and `numel`, but enabled enqueue/push/write does not check full (`ScalaGenFIFO.scala:19-44`; `ScalaGenLIFO.scala:19-44`; `ScalaGenStream.scala:84-97`). Empty FIFO, LIFO, and stream reads return `invalid` instead of stalling (`ScalaGenFIFO.scala:30-39`; `ScalaGenLIFO.scala:28-37`; `ScalaGenStream.scala:84-90`). The spec names this "silent elastic enqueue" and warns that Scalagen can pass while synthesis overflows (`Spatial Research/10 - Spec/50 - Code Generation/20 - Scalagen/40 - FIFO LIFO Stream Simulation.md:140-149`; [[40 - FIFO LIFO Stream Simulation]]).

The bounded evidence points the other way. Chisel treats FIFO, FIFOReg, and LIFO as `FIFOInterface` memories (`src/spatial/codegen/chiselgen/ChiselGenCommon.scala:119-121`), reads/writes actual empty/full status (`src/spatial/codegen/chiselgen/ChiselGenMem.scala:310-343`), gates forward pressure on stream valid or FIFO non-empty, and gates back-pressure on stream ready or FIFO non-full (`ChiselGenCommon.scala:247-278`). Stream codegen drives `valid` and `ready` explicitly (`src/spatial/codegen/chiselgen/ChiselGenStream.scala:34-42`, `ChiselGenStream.scala:139-167`). The newer Scala executor also has a bounded queue and stall predicate, but not complete coverage: `ScalaQueue` throws on full/empty (`src/spatial/executor/scala/memories/ScalaQueue.scala:8-24`), `ExecPipeline.willStall` blocks over-capacity or over-dequeue stages (`src/spatial/executor/scala/ExecPipeline.scala:222-247`), while LIFO pop remains unimplemented there (`ExecPipeline.scala:179-180`).

## Candidate Policies

(A) `compat_scalagen_elastic` is the Scalagen reference only. It may claim ScalaGen value parity, source-order compatibility, and legacy golden compatibility. It may not claim boundedness, no-overflow safety, hardware liveness, deadlock detection, cycle accuracy, or HLS timing. Overflow is represented as `elastic_over_capacity` only if a diagnostic high-water mark is enabled; execution still accepts the write. Underflow is `invalid_value_returned`, matching ScalaGen. Deadlock is `not_claimed`, because ScalaGen stream controls run by input exhaustion hacks rather than wait-for analysis (`src/spatial/codegen/scalagen/ScalaGenController.scala:14-20`, `ScalaGenController.scala:62-72`, `ScalaGenController.scala:187-191`).

(B) `bounded_backpressure` is the simulator/HLS semantic model. It may claim finite-capacity protocol behavior only with declared scheduler, two-phase snapshot/commit, maximum-cycle bound, and II source. Full writes become `blocked_full`; empty reads become `blocked_empty`; neither commits. `overflow_contract_error` and `underflow_contract_error` are reserved for an implementation that commits past capacity or consumes absent data. Deadlock is `deadlock_timeout` with a wait-for set and last-progress cycle. This policy must compose with D-15's HLS scheduler mode, because `ParallelPipe` bounded behavior is not ScalaGen serial behavior (`Spatial Research/20 - Research Notes/50 - Decision Records/D-15.md:40-56`).

## Dual Mode Contract

(C) `dual_elastic_bounded` should be the named project policy. It contains `compat_scalagen_elastic` for value reference and `bounded_backpressure_diagnostic` for HLS-adjacent liveness. A run may claim "value matched" from the elastic lane and "bounded protocol passed/failed" from the bounded lane, but it must not merge the two into one unqualified pass. D-20 already requires cycle delay lines to declare queue policy, flow gating, and II source before timing claims (`Spatial Research/20 - Research Notes/50 - Decision Records/D-20.md:50-65`). D-21 likewise requires queue/backpressure traces to declare II provenance rather than overwriting compiler and HLS accepted II (`Spatial Research/20 - Research Notes/50 - Decision Records/D-21.md:46-70`, `D-21.md:86-95`).

Required fields: `queue_policy`, `simulator_mode`, `scheduler_policy`, `capacity_source`, `same_cycle_rule`, `overflow_policy`, `underflow_policy`, `deadlock_policy`, `max_cycles`, `ii_source`, `ii_value`, and `trace_provenance`. For `same_cycle_rule`, use snapshot/commit: all enabled reads and writes are evaluated against the pre-state, a queue commits only when aggregate dequeues fit current size and aggregate enqueues fit post-dequeue capacity, and the trace records accepted or blocked lanes. This avoids making D-22 depend on textual ordering.

## HLS Native And Recommendation

(D) `hls_native_report_only` is valid only as a final evidence tier. It may claim post-tool schedule or co-simulation results when reports map cleanly, but it cannot claim pre-HLS liveness, explain first blocked producer/consumer, or preserve ScalaGen goldens. D-08 treats reports as post-tool authority while keeping simulation for validation and triage (`Spatial Research/20 - Research Notes/50 - Decision Records/D-08.md:31-39`, `D-08.md:61-67`); D-21 names missing, unparseable, stale, and ambiguous reports as first-class reconciliation states (`D-21.md:57-70`).

Recommend (C). Reject (A) as the only policy because it hides overflow. Reject (B) as the only policy because it would break Scalagen reference tests and prematurely decide D-15/D-20 details. Reject (D) as the only policy because it arrives too late for simulator debugging. The contract should make every artifact say which claim it is making: `scalagen_value_reference`, `bounded_protocol_diagnostic`, `hls_report_authority`, or `incomparable_policy`.
