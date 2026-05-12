---
type: "research"
decision: "D-15"
angle: 8
---

# D-15 Angle 8: Implementation Cost and Migration Strategy

## Baseline Cost Boundary

D-15 is expensive only if we make the Rust simulator more truthful than ScalaGen. The current ScalaGen behavior is cheap because it is not a scheduler: `ParallelPipe` emits `gen(func)` and then control-done, while block generation visits statements in source order (`spatial/src/spatial/codegen/scalagen/ScalaGenController.scala:187-191`; `spatial/src/spatial/codegen/scalagen/ScalaCodegen.scala:37-53`; [[01-scalagen-parallelpipe-semantics]]). The tests/apps survey is also mostly value-oriented rather than schedule-observing, which makes `compat_scalagen_serial` the lowest migration-risk v1 mode for legacy regression parity ([[04-tests-apps-evidence]]).

The risk is user interpretation. A serial-only v1 is low implementation cost, but it hides peer-start, all-child-join, queue-full, and deadlock behavior. It should therefore be labelled as **ScalaGen value compatibility**, not "parallel simulation" or "hardware simulation." The open-question note states the unresolved choice directly: Rust must choose ScalaGen sequential `ParallelPipe` execution or parallel interleaving/back-pressure ([[20 - Open Questions]]).

## Option Cost/Risk Comparison

`compat_scalagen_serial`: lowest cost. Reuse the ordinary evaluator, source-order child visitation, and ScalaGen-style elastic FIFO/stream behavior. It best protects existing goldens, but it should not claim HLS correlation. It can silently pass programs that would stall or overflow once queues become bounded; ScalaGen FIFO and stream writes enqueue when enabled without a capacity check (`spatial/src/spatial/codegen/scalagen/ScalaGenFIFO.scala:41-44`; `spatial/src/spatial/codegen/scalagen/ScalaGenStream.scala:92-97`; [[40 - FIFO LIFO Stream Simulation]]).

`hls_semantic_task_barrier`: medium cost. Model `ParallelPipe` as deterministic child tasks with a barrier: issue every enabled, masked-in child for the parent activation, count masked children as skipped-done, and complete only when all non-skipped children finish. This matches the structural direction: flow rules assign `ParallelPipe` to `ForkJoin`, and Fringe `ForkJoin` synchronizes over child `iterDone` bits while gating counter increment by back-pressure (`spatial/src/spatial/flows/SpatialFlowRules.scala:317-333`; `fringe/src/fringe/templates/Controllers.scala:141-154`; [[02-hardware-forkjoin-contrast]]). Risk: if it still uses elastic queues, it is task/barrier semantic only, not bounded back-pressure.

`fuzz_interleaving`: medium implementation cost, high debugging cost. It can be built on top of the task model by exploring legal child-step permutations with a recorded seed. Its value is finding schedule-sensitive races, not defining the reference answer. Without seed replay, trace shrinking, and clear failure categories, users will treat one random pass as hardware proof.

`cycle_bounded_backpressure`: high cost. It needs bounded FIFO/LIFO/stream state, valid/ready-style stall rules, cycle limits, deadlock diagnostics, and probably D-20/D-21/D-22 decisions before it can be honest. Chiselgen already composes stream/FIFO readiness into forward/back-pressure (`spatial/src/spatial/codegen/chiselgen/ChiselGenCommon.scala:247-279`; `spatial/src/spatial/codegen/chiselgen/ChiselGenController.scala:304-309`; [[80 - Streaming]]). Recreating enough of that in Rust is valuable, but false precision is a major risk unless the mode reports its assumptions.

`compare_serial_hls`: medium-high cost, high migration value. Run `compat_scalagen_serial` and either `hls_semantic_task_barrier` or `cycle_bounded_backpressure` on the same workload, then diff final memories, stream outputs, and diagnostics. The hard parts are snapshotting simulator state, aligning traces, and suppressing expected divergences. The payoff is controlled migration: old tests can keep passing while the new mode exposes programs whose apparent correctness depends on ScalaGen serialization.

## Migration and Testing Strategy

Phase 0 should tag existing simulator tests as `mode=compat_scalagen_serial` and add a small D-15 smoke suite that pins source-order behavior for legacy parity. Phase 1 adds `mode=hls_semantic_task_barrier` tests for independent children, masked children, child completion barriers, and simple shared FIFO producer/consumer cases. Divergent serial-vs-barrier outputs should be marked explicitly, not folded into one golden.

Phase 2 introduces `mode=fuzz_interleaving` only for race-oriented tests, with seed capture in failure output and a replay CLI. It should be opt-in or nightly at first. Phase 3 waits on D-22 before enabling `mode=cycle_bounded_backpressure` as anything stronger than experimental: tests need full FIFO, empty FIFO, deadlock, max-cycle, and stream ready/valid cases. `mode=compare_serial_hls` can enter CI as non-blocking telemetry before it becomes a gate.

## User-Facing Guardrails

Every run should print and persist the mode label in test artifacts. Recommended labels: `compat_scalagen_serial`, `hls_semantic_task_barrier`, `fuzz_interleaving_seeded`, `cycle_bounded_backpressure`, and `compare_serial_hls`. If `hls_semantic_task_barrier` uses elastic queues, emit a warning: "barrier semantics enabled; bounded queue back-pressure disabled." If `cycle_bounded_backpressure` lacks calibrated II or delay-line modeling, say so in the run summary.

The documentation should avoid the bare word "correct." Serial mode answers "what would ScalaGen do?" Task/barrier mode answers "what does the ForkJoin semantic model permit?" Fuzzing answers "can alternate legal interleavings expose a bug?" Cycle-bounded mode answers "what happens under this bounded pressure model?" That provenance prevents the v1-compatible path from misleading users while leaving room for a stricter HLS-facing simulator.
