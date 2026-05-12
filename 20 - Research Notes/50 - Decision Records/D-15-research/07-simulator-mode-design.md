---
type: "research"
decision: "D-15"
angle: 7
---

# D-15 Angle 7: Simulator Mode Design and Determinism

## Mode Boundary

The simulator choice should be exposed as a named mode, not hidden behind a global flag. The source evidence has two incompatible but useful baselines. ScalaGen `ParallelPipe` emits a kernel wrapper, then calls `gen(func)` directly, so statements run in block order with no child scheduler, interleaving, or done-token protocol (`src/spatial/codegen/scalagen/ScalaGenController.scala:187-191`; [[01-scalagen-parallelpipe-semantics]]; [[50 - Controller Emission]]). D-14, however, defines `ForkJoin` as peer child start plus an all-child join, and labels ScalaGen serialization as compatibility behavior rather than HLS semantics ([[D-14]]). D-22 is the queue half: elastic ScalaGen queues cannot honestly model bounded back-pressure ([[05-stream-backpressure-overlap]]; [[80 - Streaming]]).

Therefore every result should record `simulator_mode`, simulator version, queue policy, depth policy, tie-break policy, seed if any, max-cycle bound if any, and trace/provenance path. Determinism is not one policy; it is a reproducibility contract per mode.

## Compatibility And Semantic Modes

`compat_scalagen_serial` should execute `ParallelPipe` children in stable IR/source order and pair naturally with ScalaGen-style elastic FIFO/LIFO/stream behavior. It is fully deterministic for a fixed program and input, needs no seed, and is the right mode for historical value goldens. It can prove Rust value parity with ScalaGen's current simulator and catch ordinary side-effect regressions. It cannot prove child overlap, all-child join timing, full/empty stalls, deadlock freedom, max-child latency, or HLS dataflow correctness. Diagnostics should warn when a serialized `ParallelPipe` touches FIFOs, streams, `FIFOReg`, or shared memories whose behavior may change under peer execution.

`hls_semantic_step` should be the deterministic small-step form of D-14's `ForkJoin`: for each logical parent step, issue every enabled, masked-in child as a peer task, count masked-out children as skipped-done, and advance the parent only after every non-skipped child completes. Ties should resolve by stable symbol/controller identity so replay does not depend on host thread scheduling. This mode can validate masks, join barriers, branch of execution, and effect ordering under the chosen dependence model. Until D-22 settles bounded queues, it should not claim back-pressure fidelity; with elastic queues it proves schedule structure, not liveness under finite buffers.

## Exploration Modes

`randomized_interleaving` is a diagnostic stress mode, not a golden oracle. It should keep D-14 legality rules but randomly choose among currently enabled child/lane microsteps. Reproducibility comes from a required seed, a serialized interleaving trace, and ideally a minimized replay trace for failures. It can find accidental order dependence, missing memory dependences, consumer-before-producer assumptions, and bugs masked by source-order execution. It cannot prove absence of races after a finite seed set, and a passing randomized run must not be treated as HLS conformance. Failing seeds, however, are excellent regression tests.

`bounded_cycle/backpressure` is the high-fidelity mode implied by D-22: bounded FIFO/LIFO/stream state, ready/valid-style full/empty stalls, cycle or phase counters, and deadlock/overflow diagnostics. The Chisel path composes forward/back-pressure from FIFO non-empty, FIFO not-full, stream valid/ready, merge-buffer capacity, and grouped priority-dequeue availability (`src/spatial/codegen/chiselgen/ChiselGenCommon.scala:247-279`; [[80 - Streaming]]). This mode can expose concrete workload deadlocks, insufficient depths, overflow that ScalaGen hides, and producer/consumer phasing errors. It cannot prove all-depth or all-input liveness, and it should not replace HLS reports for accepted II or physical latency.

## Diagnostics And Reproducibility

All nontrivial modes need structured diagnostics rather than only pass/fail. The useful minimum is: per-step enabled set, chosen task, blocked reason (`empty`, `full`, `mask`, `join`, `memory_dependence`, `break`, `cycle_limit`), queue occupancies, side-effect log, state hash, and first divergence against `compat_scalagen_serial` when a comparison run is requested. For DSE or latency experiments, outputs must carry the same provenance discipline D-08 asks for: serial compatibility, semantic-step estimate, bounded simulation, HLS estimate, or report-backed measurement should not collapse into an unlabeled `Cycles` value ([[06-runtime-model-latency]]; [[D-08]]).

## Preliminary Recommendation

Start with two supported modes: `compat_scalagen_serial` as the default regression simulator, and `hls_semantic_step` as the default HLS-scheduler validation simulator. Add `randomized_interleaving` early as a seeded bug-finder because it is cheap and clarifies hidden order assumptions. Treat `bounded_cycle/backpressure` as experimental until D-22 defines finite queue semantics; after D-22, promote it to the liveness/back-pressure validation mode. This preserves ScalaGen parity without letting serial execution masquerade as HLS proof.
