---
type: "research"
decision: "D-15"
angle: 5
---

# D-15 Angle 5: FIFO/Stream Back-Pressure and D-22 Overlap

## Current Split

The immediate D-15 question is not whether `ParallelPipe` exists in the IR; it is which simulator contract should be attached to it. ScalaGen serializes it: the `ParallelPipe` case just emits the wrapper, calls `gen(func)`, and marks done (`src/spatial/codegen/scalagen/ScalaGenController.scala:187-191`). The underlying Scala block emitter also walks `b.stms` in order through `javaStyleChunk(...)(visit _)`, so this is deterministic source-order execution, not task interleaving (`src/spatial/codegen/scalagen/ScalaCodegen.scala:37-53`). The open question states the mismatch plainly: ScalaGen emits `ParallelPipe` bodies sequentially, while hardware treats parallelism structurally, so Rust must choose serial compatibility or interleaving/back-pressure (`20 - Research Notes/20 - Open Questions.md:2014-2024`).

## Where Parallel Children Come From

`ParallelPipe` is broader than an explicit user `Parallel { ... }`. The surface `Parallel.apply` stages `ParallelPipe(Set.empty, block)` directly (`src/spatial/lang/control/Parallel.scala:9-13`), but compiler passes also synthesize it. Binding groups consecutive child controllers when it sees no conflicting memory/stream/break constraints, then wraps groups larger than one in a `ParallelPipe` (`src/spatial/transform/BindingTransformer.scala:21-42`, `src/spatial/transform/BindingTransformer.scala:68-83`). Controller unrolling similarly duplicates controller lanes and wraps multiple lanes in a `ParallelPipe` under MoP (`src/spatial/transform/unrolling/UnrollingBase.scala:147-165`). This matters because a Rust simulator policy will affect both user-authored parallel regions and compiler-created parallel children.

## Chisel Pressure Semantics

The Chisel path makes `ParallelPipe` schedule-bearing. Flow rules assign every `ParallelPipe` to `ForkJoin` (`src/spatial/flows/SpatialFlowRules.scala:317-333`). In Fringe, `ForkJoin` increments only when `synchronize` is true, and `synchronize` is the AND of all child `iterDone` bits; each child may become active in the same parent enable/backpressure window (`fringe/src/fringe/templates/Controllers.scala:141-154`). Kernel wiring then feeds the state machine with `backpressure`, gates enable by `forwardpressure`, and enables counter chains with `forwardpressure` (`fringe/src/fringe/SpatialBlocks.scala:132-158`). Chisel codegen computes those pressure signals from stream/FIFO readiness: reads require stream valid, FIFO non-empty or inactive read, and priority-read group availability; writes require stream ready, FIFO not full or inactive write, and merge-buffer space (`src/spatial/codegen/chiselgen/ChiselGenCommon.scala:247-279`). The generated controller wires those expressions into `backpressure` and `forwardpressure` (`src/spatial/codegen/chiselgen/ChiselGenController.scala:304-309`).

## Why D-22 Matters

D-22 is the queue-semantics half of the same problem. ScalaGen maps FIFO and Stream types to `mutable.Queue`, LIFO to `mutable.Stack`, and enqueue/write paths push when enabled without checking staged capacity (`src/spatial/codegen/scalagen/ScalaGenFIFO.scala:12-44`, `src/spatial/codegen/scalagen/ScalaGenLIFO.scala:12-44`, `src/spatial/codegen/scalagen/ScalaGenStream.scala:12-97`). The spec calls this silent elastic enqueue and warns that overflow can look fine in Scala while failing in synthesized hardware (`10 - Spec/50 - Code Generation/20 - Scalagen/40 - FIFO LIFO Stream Simulation.md:138-149`). Hardware FIFOs are explicitly bounded: the Fringe FIFO template builds counters with `p.volume`, physical memories sized from `p.volume`, and `empty/full` outputs from the element counter (`fringe/src/fringe/templates/memory/MemPrimitives.scala:380-399`, `fringe/src/fringe/templates/memory/MemPrimitives.scala:436-442`). Therefore an interleaved `ParallelPipe` simulator cannot honestly claim back-pressure unless it also has bounded FIFO/LIFO/stream state, stall rules, and deadlock/overflow diagnostics. The decision queue also separates these: D-15 chooses `ParallelPipe` simulation semantics, while D-22 chooses elastic versus bounded queue semantics (`20 - Research Notes/40 - Decision Queue.md:67-69`, `20 - Research Notes/40 - Decision Queue.md:95-97`).

## Decidable Now and Risks

What can be decided now is the mode boundary, not the final D-22 policy. A ScalaGen-compatible Rust mode can run `ParallelPipe` serially and keep elastic queues; it should be labelled value-compatibility only. A hardware-facing mode can require the `ForkJoin` child-start/join shape, but its back-pressure behavior should be blocked on D-22 until bounded queues are specified. Pretending back-pressure exists on top of unbounded queues is the worst middle state: producers never stall, consumer starvation becomes invalid-value propagation rather than a cycle stall, overflow bugs disappear, and deadlock cases become ordinary completion. It would also desynchronize simulator and model expectations, because the runtime model prices `ForkJoin` as max-child parallel cost rather than serial sum (`models/src/models/RuntimeModel.scala:313-322`).
