---
type: spec
concept: "Scala Executor"
source_files:
  - "src/spatial/Spatial.scala:124-129"
  - "src/spatial/Spatial.scala:202-207"
  - "src/spatial/Spatial.scala:561-575"
  - "src/spatial/executor/scala/ExecutorPass.scala:1-106"
  - "src/spatial/executor/scala/ExecutionState.scala:1-107"
  - "src/spatial/executor/scala/OpExecutorBase.scala:1-19"
  - "src/spatial/executor/scala/ControlExecutor.scala:1-1069"
  - "src/spatial/executor/scala/ExecPipeline.scala:1-323"
  - "src/spatial/executor/scala/FringeNodeExecutor.scala:1-169"
  - "src/spatial/executor/scala/MemoryController.scala:1-64"
  - "src/spatial/executor/scala/EmulVal.scala:1-26"
  - "src/spatial/executor/scala/resolvers/OpResolver.scala:1-56"
  - "src/spatial/executor/scala/memories/ScalaReg.scala:1-17"
  - "src/spatial/executor/scala/memories/ScalaTensor.scala:1-106"
  - "src/spatial/executor/scala/memories/ScalaQueue.scala:1-61"
  - "src/spatial/executor/scala/memories/ScalaStruct.scala:1-8"
source_notes:
  - "[[open-questions-infra]]"
hls_status: rework
depends_on:
  - "[[20 - Scalagen]]"
  - "[[30 - Memory Simulator]]"
  - "[[50 - Controller Emission]]"
status: draft
---

# Scala Executor

## Summary

The Scala executor under `src/spatial/executor/scala/` is a reference interpreter for Spatial IR, not the same thing as the generated Scala backend. It is enabled by `--scalaExec`, which sets `spatialConfig.enableScalaExec` and optional DRAM timing knobs for latency, throughput, and maximum simultaneous requests `src/spatial/Spatial.scala:561-575`. `Spatial.scala` constructs `ExecutorPass(state, scalaExecThroughput, scalaExecLatency, scalaExecMaxSimultaneousRequests)` and inserts it after pre-execution dumping and transformer checks, before unrolling `src/spatial/Spatial.scala:124-129` `src/spatial/Spatial.scala:202-207`.

Architecturally, the executor is a tick-driven simulator. It carries host values, staged IR, emulated memories, controller-cycle counters, and a throttled memory controller in `ExecutionState`. Controller execution is dispatched through a large `ControlExecutor` factory, local operations are delegated to resolver mix-ins, pipelines are modeled with `ExecPipeline` stages, and host/fringe DRAM transfers are simulated by `FringeNodeExecutor` plus `MemoryController`.

## API

The public entry is `ExecutorPass(IR, bytesPerTick, responseLatency, activeRequests)` `src/spatial/executor/scala/ExecutorPass.scala:10-13`. `ExecutionState` exposes value lookup, typed extraction with `getValue`, tensor extraction with `getTensor`, registration, copying, and `runAndRegister`, which delegates to `OpResolver.run` `src/spatial/executor/scala/ExecutionState.scala:58-101`. `OpExecutorBase` defines the shared `tick`, `status`, and `print` contract; statuses are `Done`, `Indeterminate`, `Running`, `Disabled`, and the `Finished` marker reports `isFinished` `src/spatial/executor/scala/OpExecutorBase.scala:1-19`.

`ControlExecutor.apply(ctrl, execState)` is the controller factory. It dispatches on `AccelScope`, `OpForeach`, `UnitPipe`, `ParallelPipe`, `OpReduce`, `OpMemReduce`, `Switch`, `FringeNode`, and `StateMachine`, while also checking schedule categories such as `Pipelined` and `Sequenced` for outer controls `src/spatial/executor/scala/ControlExecutor.scala:16-47`. `ControlExecutor.scala` is 1069 lines and is the main cluster of controller executor implementations; the executor subtree has 22+ executor-related definitions when counting factories, base executor classes/traits, concrete controller executors, and fringe executors (inferred, unverified). The spec intentionally does not enumerate all specialized executors.

The memory API is request-based. `MemoryController.makeRequest(size)` returns a mutable `Request` handle; later ticks move it from pending, to transferring, to finished according to `responseLatency`, `bytesPerTick`, and `maxActiveRequests` `src/spatial/executor/scala/MemoryController.scala:5-53`. The value API is intentionally small: every resolved result is an `EmulResult`, either an `EmulVal` scalar/unit/poison value or an `EmulMem` backing store `src/spatial/executor/scala/EmulVal.scala:3-26`.

## Implementation

`ExecutorPass` runs once per runtime argument set. For each set, it splits the string arguments, creates an `ExecutionState` with an empty value map, `MemTracker`, `MemoryController`, and `CycleTracker`, then emits a simulation log and summary under generated output files named `SimulatedExecutionLog_*` and `SimulatedExecutionSummary_*` `src/spatial/executor/scala/ExecutorPass.scala:17-35` `src/spatial/executor/scala/ExecutorPass.scala:77-103`. Inside the pass, top-level `AccelScope` nodes create an `AccelScopeExecutor`; the pass repeatedly ticks the executor, prints optional logs, ticks `executionState.memoryController`, and accumulates elapsed cycles until the executor reports `Done` `src/spatial/executor/scala/ExecutorPass.scala:37-61`. Non-accelerator top-level host statements are evaluated immediately with `executionState.runAndRegister` `src/spatial/executor/scala/ExecutorPass.scala:68-71`.

`ExecutionState` is the simulator's mutable state object. It maps `Exp` values to `EmulResult`s, stores parsed runtime arguments, owns the host memory tracker, memory controller, cycle tracker, and implicit Argon `State`, and resolves constants to `SimpleEmulVal` on demand `src/spatial/executor/scala/ExecutionState.scala:1-72`. Copying shares the same memory controller and trackers while copying the value map handle, which is important for forked pipeline lanes (inferred from constructor use) `src/spatial/executor/scala/ExecutionState.scala:93-99`.

`MemTracker` is a host-side address allocator for Scala tensors. It records tensor start addresses, byte sizes, and a monotonically increasing `maxAddress`; fringe transfer commands later translate byte offsets back into tensor indices through this table `src/spatial/executor/scala/ExecutionState.scala:11-34` `src/spatial/executor/scala/FringeNodeExecutor.scala:19-45`.

`ControlExecutor` implements controller-level time. The abstract base increments per-controller cycle and iteration counts once an executor starts running, exposes `shouldRun`, and requires subclasses to report deadlock status `src/spatial/executor/scala/ControlExecutor.scala:52-83`. Helper methods compute foreach iteration maps and split outer-pipeline statements into transient operations plus nested controls before creating either inner or outer pipelines `src/spatial/executor/scala/ControlExecutor.scala:85-144`. Inner and outer foreach/reduce/mem-reduce, unit pipes, streaming pipes, switches, and FSMs then specialize the same tick/status pattern across the rest of the file `src/spatial/executor/scala/ControlExecutor.scala:147-1069`.

`ExecPipeline` is the pipeline-stage abstraction. It accepts new `ExecutionState` vectors only when stage zero is empty, ticks all stages, captures `lastStates` when the final stage completes, and shifts completed work into later empty stages `src/spatial/executor/scala/ExecPipeline.scala:12-83`. `PipelineStage` and `PipelineStageExecution` separate stage occupancy from execution behavior, with inner stages evaluating local symbols and outer stages wrapping child `ControlExecutor`s `src/spatial/executor/scala/ExecPipeline.scala:96-323`.

`FringeNodeExecutor` handles DRAM-transfer simulators. It dispatches fringe dense load/store nodes, decodes command structs into DRAM base/length/byte-size requests, and turns loads/stores into `MemoryController` requests plus stream enqueue/dequeue activity `src/spatial/executor/scala/FringeNodeExecutor.scala:11-169`. `MemoryController` keeps a backlog and active request queue, starts up to `maxActiveRequests`, honors a pending `responseLatency`, transfers at most `bytesPerTick` per tick, and marks requests finished when all bytes transfer `src/spatial/executor/scala/MemoryController.scala:1-64`.

Values are carried by `EmulVal`: `SimpleEmulVal` wraps valid values, `EmulUnit` models unit-producing symbols, `EmulPoison` throws on invalid access and marks `valid = false`, and `EmulMem` marks backing stores `src/spatial/executor/scala/EmulVal.scala:1-26`. `OpResolver` is the operation-level dispatcher; its object mixes `DisabledResolver` first with a source comment that this makes it run "almost last", then layers memory, n-ary, control, misc, IO, host, fixed, float, bit, FIFO, and struct resolvers `src/spatial/executor/scala/resolvers/OpResolver.scala:10-56`. Backing stores cover registers (`ScalaReg`), flat tensors/line buffers (`ScalaTensor` and `ScalaLB`), queues/FIFOs/file streams (`ScalaQueue`), and structs (`ScalaStruct`) `src/spatial/executor/scala/memories/ScalaReg.scala:1-17` `src/spatial/executor/scala/memories/ScalaTensor.scala:1-106` `src/spatial/executor/scala/memories/ScalaQueue.scala:1-61` `src/spatial/executor/scala/memories/ScalaStruct.scala:1-8`.

Dense fringe loads and stores use the same pieces in opposite directions. A load consumes command stream entries, creates a memory-controller request for the byte size, waits for `RequestFinished`, reads tensor values or poisons out-of-bounds/uninitialized values, and enqueues data-stream values `src/spatial/executor/scala/FringeNodeExecutor.scala:48-99`. A store waits until enough data-stream elements are available, records enabled payloads, creates a request, writes finished values into the tensor, and enqueues an acknowledgement `src/spatial/executor/scala/FringeNodeExecutor.scala:101-169`.

## Interactions

The executor depends heavily on metadata established by earlier compiler phases: controller schedule, `fullDelay`, II, parent/child control structure, memory metadata, and fringe transfer nodes. It shares conceptual ground with [[20 - Scalagen]] because both are Scala-side reference behavior, but this executor runs inside the compiler pipeline while the Scala codegen emits standalone Scala.

The command-line timing knobs wire directly into the executor constructor: `scalaExecLatency` is the memory response latency, `scalaExecThroughput` is bytes per tick, and `scalaSimAccess` sets maximum simultaneous requests `src/spatial/Spatial.scala:561-575` `src/spatial/Spatial.scala:124-129`. This makes the executor useful for coarse memory-system experiments, but those knobs are simulator parameters rather than target hardware metadata.

## HLS notes

This entry is `rework` for HLS. The executor is useful as a golden simulator and as a model of expected controller/memory timing, but its tick model, dynamic `ExecutionState`, Scala reflection/casts, and resolver trait stack are not synthesizable as HLS code.

## Open questions

See [[open-questions-infra#Q-inf-03]] for executor coverage and maintenance questions.
