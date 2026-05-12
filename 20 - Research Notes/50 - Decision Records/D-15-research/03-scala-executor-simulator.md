---
type: "research"
decision: "D-15"
angle: 3
---

# D-15 Angle 3: Scala Executor and Simulator Infrastructure

## Executor Entry Point

The source-level Scala executor is a different reference point from ScalaGen text emission. `ControlResolver` executes a control by constructing a `ControlExecutor` and repeatedly calling `tick()` until the executor reports a finished status (`src/spatial/executor/scala/resolvers/ControlResolver.scala:12-19`). The dispatcher treats `ParallelPipe` specially: ordered `Pipelined`/`Sequenced` schedules select the ordinary `UnitPipeExecutor` for `UnitPipe`, but `ParallelPipe` is always routed to `StreamUnitPipeExecutor` (`src/spatial/executor/scala/ControlExecutor.scala:19-32`). This ignores the hardware schedule tag at dispatch time: flow rules set every `ParallelPipe` to `ForkJoin` (`src/spatial/flows/SpatialFlowRules.scala:317-333`), while the executor branch just pattern-matches the node shape.

## What ParallelPipe Ticks

`StreamUnitPipeExecutor` pattern-matches either a streaming `UnitPipe` or a `ParallelPipe`; for `ParallelPipe` it extracts enables and block and assigns no `stopWhen` (`src/spatial/executor/scala/ControlExecutor.scala:207-215`). Its lazy `executors` list walks `blk.stms`: child controls become child `ControlExecutor`s over the same `ExecutionState`, fringe nodes become `FringeNodeExecutor`s, and simple non-control statements run immediately via `execState.runAndRegister(simple)` (`src/spatial/executor/scala/ControlExecutor.scala:217-226`). On each parent tick, it increments its own cycle tracker and then calls `tick()` on every child executor in source order (`src/spatial/executor/scala/ControlExecutor.scala:228-235`). Completion is an all-child predicate over child status: `Done`, `Disabled`, and `Indeterminate` count as complete; any `Running` child keeps the parent running (`src/spatial/executor/scala/ControlExecutor.scala:237-249`).

So the executor does support cooperative per-cycle interleaving of child controllers, but not tasks, threads, futures, or a scheduler queue. A child may remain live across ticks while siblings also tick. Non-control statements are not interleaved; they execute during lazy child-list construction.

## Pipelines and Queues

The related `ExecPipeline` machinery is where the executor models staged execution and local queue stalls. A pipeline tick advances each stage, removes completed work from the last stage, and moves completed work forward only when the later stage is empty (`src/spatial/executor/scala/ExecPipeline.scala:24-51`). A stage only ticks when it is not done and will not stall (`src/spatial/executor/scala/ExecPipeline.scala:96-101`). Inner pipeline stages collect FIFO/stream accesses, pre-evaluate enables by peeking instead of dequeuing, count enabled enqueues and dequeues per `ScalaQueue`, and stall unless queue size/capacity can satisfy the whole stage transaction (`src/spatial/executor/scala/ExecPipeline.scala:140-247`). `ScalaQueue` itself is a mutable queue with capacity checks on `enq` and empty checks on `deq` (`src/spatial/executor/scala/memories/ScalaQueue.scala:8-25`).

For `ParallelPipe`, however, no enclosing `ExecPipeline` is built. Queue pressure can still emerge inside child executors, but there is no central `ParallelPipe` task queue, ready/valid arbiter, mask table, or parent-controlled child issue protocol.

## ScalaGen and Chisel Contrast

ScalaGen remains serial for `ParallelPipe`: its case emits a wrapper, calls `gen(func)`, then emits control-done (`src/spatial/codegen/scalagen/ScalaGenController.scala:187-191`). The Scala block generator walks `b.stms` through `javaStyleChunk(...)(visit _)`, preserving ordinary statement visitation order (`src/spatial/codegen/scalagen/ScalaCodegen.scala:37-53`). Even ScalaGen's nearby outer-stream hack is serial: for streaming children with external FIFO/stream inputs, it emits a `while (hasItems_child)` around one child before moving on (`src/spatial/codegen/scalagen/ScalaGenController.scala:22-45`).

Chisel/Fringe is the other pole. ChiselGen instantiates a controller kernel with `lhs.rawSchedule`, child count, and child signal vectors (`src/spatial/codegen/chiselgen/ChiselGenController.scala:250-276`, `src/spatial/codegen/chiselgen/ChiselGenController.scala:333-358`). Fringe `ForkJoin` defines synchronization as the AND of all child `iterDone` latches and can activate every child under the same parent enable/back-pressure window (`fringe/src/fringe/templates/Controllers.scala:141-154`). Kernel wiring carries `enableOut`, child done/mask, back-pressure, and counter enable signals between parent and children (`fringe/src/fringe/SpatialBlocks.scala:117-158`).

## Rust Simulator Implication

For D-15, these are three distinct contracts. `compat_scalagen_serial` should execute `ParallelPipe` statements textually. A Scala-executor-parity mode would create all child control executions, poll/tick them once per parent cycle in deterministic source order, and rely on each child pipeline for queue stalls. A hardware-oriented Rust mode should instead model ForkJoin peer issue, skipped masks, all-child join, and pressure-gated counter advance. Inference unverified: I inspected source, not tests or traces, so the tick executor should be validated before treating it as canonical simulator behavior.
