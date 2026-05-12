---
type: "research"
decision: "D-15"
angle: 9
---

# D-15 Angle 9: Risk Analysis and Failure Modes

## Semantic Split Risks

The main risk is choosing one simulator semantics and letting it masquerade as the other. ScalaGen `ParallelPipe` is a deterministic block walk: the controller case wraps the kernel, calls `gen(func)`, and marks done, while the underlying block generator visits statements in order (`spatial/src/spatial/codegen/scalagen/ScalaGenController.scala:187-191`; `spatial/src/spatial/codegen/scalagen/ScalaCodegen.scala:37-53`; [[01-scalagen-parallelpipe-semantics]]). Hardware-facing `ForkJoin` is different: children can be peer-issued, masked children can count as skipped-done, and the parent advances only after synchronization and back-pressure permit it (`fringe/src/fringe/templates/Controllers.scala:141-154`, `212-215`; [[02-hardware-forkjoin-contrast]]).

A serial Rust simulator therefore risks hiding exactly the bugs D-15 is supposed to surface: child races, producer/consumer phasing, dataflow deadlocks, queue overflow, join-time stalls, and memory port conflicts. It can also impose a side-effect order that no hardware implementation promises. Prints, ArgOut updates, DRAM writes, stream writes, and debug counters may appear stable only because child 0 always ran before child 1. The mitigation is mode honesty: name this path `compat_scalagen_serial`, keep it deterministic, and classify its pass/fail results as value and legacy-golden evidence, not as liveness, schedule, or HLS dataflow evidence.

## Parallel Mode Risks

A parallel/interleaving simulator has the opposite failure mode: it can create nondeterminism before the language contract says which interleavings are observable. If child scheduling is arbitrary, a test may fail because the simulator chose a legal but unhelpful interleaving, because the program has a real race, or because the simulator invented hardware behavior not supported by Chisel/HLS lowering. That ambiguity is especially sharp for side effects and shared memories: two children writing the same SRAM address, enqueuing to the same FIFO, or updating a host-visible result need a conflict rule, not just a thread scheduler.

Back-pressure makes the risk larger. ScalaGen queues are elastic mutable collections, so enqueue does not block on capacity (`spatial/src/spatial/codegen/scalagen/ScalaGenFIFO.scala:17-44`; `spatial/src/spatial/codegen/scalagen/ScalaGenStream.scala:84-97`; [[05-stream-backpressure-overlap]]). HLS streams, by contrast, can be modeled as unbounded in C but implemented as bounded FIFOs whose depth affects stalls and deadlocks; AMD's Vitis documentation and dataflow tutorial both tie stream depth, full/empty handshakes, stalls, and deadlock diagnosis together ([UG1399 HLS Stream Library](https://docs.amd.com/r/2024.1-English/ug1399-vitis-hls/HLS-Stream-Library); [FIFO sizing and deadlocks](https://xilinx.github.io/Vitis-Tutorials/2022-1/build/html/docs/Hardware_Acceleration/Feature_Tutorials/03-dataflow_debug_and_optimization/fifo_sizing_and_deadlocks.html)). Enabling a bounded `ParallelPipe` mode before D-22 decides queue semantics would create premature failures against old goldens and false positives for overflow/deadlock.

## Golden and DSE Failure Modes

Existing tests mostly constrain final values, not interleavings. The D-15 test survey found many `Parallel`, FIFO, stream, and unrolling examples whose assertions compare arrays, scalars, or checksums; several schedule-sensitive tests have disabled or weak assertions (`test/spatial/tests/feature/control/ParallelPipeInsertion.scala:22-43`; `test/spatial/tests/feature/dense/MatMult_systolic.scala:93-108`; [[04-tests-apps-evidence]]). Serial mode may therefore pass the corpus while still hiding races and deadlocks. Parallel mode may fail the same corpus without proving a semantic bug, because the golden never specified the side-effect order being exercised.

DSE adds a second false-confidence path. The current DSE contract wants ordered numeric `Cycles` values, but D-08 says simulation is validation and triage, not the hot-loop objective for every point (`D-08.md:49-67`). A serial simulator can suggest sum-child behavior, while the runtime model's `ForkJoin` equation uses max-child latency plus synchronization (`models/src/models/RuntimeModel.scala:301-321`; [[06-runtime-model-latency]]). A bounded interleaving simulator can expose stalls, but only for a workload and queue policy. Mitigation: never emit simulator-derived DSE numbers without provenance fields for mode, queue policy, seed, workload, timeout, confidence, and whether reports or accepted II have overridden them (`D-08.md:69-90`; [[06-runtime-model-latency]]).

## Diagnostics and Guardrails

The practical guardrail is a two-lane test contract. `compat_scalagen_serial` should be the default regression lane for old ScalaGen goldens and should record child order explicitly. A future `parallel_backpressure` lane should be opt-in until D-22, deterministic by default with a replayable scheduler seed, and optionally randomized for race hunting. Every divergent test should say whether the expected result is value-only, ordered-side-effect, liveness, queue-capacity, or latency evidence.

Diagnostics should make stalls explainable. Record per-cycle or per-step events with controller id, child id, iteration, enable/mask/done, queue occupancy and high-water mark, read-empty/write-full attempts, memory name, bank/port/lane, and side-effect timestamp. On timeout, emit a wait-for graph: which child is waiting on which FIFO, memory port, parent acknowledgement, or masked/done condition. On memory conflict, classify the event as same-address race, port over-subscription, unresolved banking, or legal multi-reader. On golden mismatch, print both mode and first divergent side effect rather than only final value.

The final mitigation is policy separation. Serial success should not bless HLS liveness. Parallel success should not rewrite ScalaGen compatibility. Bounded-channel failure should be blocked or marked provisional until D-22. DSE should consume simulator output only as labelled evidence, with report-backed reconciliation remaining the authority when available.
