# ScalaGen ParallelPipe Semantics

## Claim for this angle

ScalaGen simulation treats `ParallelPipe` as sequential Scala execution of its block, not as a parallel interleaving or a back-pressure network. For D-15 angle 1, the Rust simulator should follow ScalaGen parity by executing `ParallelPipe` children in ordinary block order unless we explicitly choose a non-ScalaGen, RTL-like mode. The vault spec already flags this distinction: `UnitPipe` goes through `emitControlBlock`, while `ParallelPipe` calls `gen(func)` directly (`Spatial Research/10 - Spec/50 - Code Generation/20 - Scalagen/50 - Controller Emission.md:50-52`).

## Kernel wrapper shape

All three relevant controls are emitted through `emitControlObject`, so the first semantic layer is kernelization, not scheduling. The helper computes captured inputs from `lhs.nonBlockInputs ++ block.nestedInputs`, removes symbols bound by the op, then filters memories and values (`spatial/src/spatial/codegen/scalagen/ScalaGenController.scala:108-113`). If enables are present, it wraps the body in an `if (${and(ens)}) ... else null.asInstanceOf[T]` gate (`ScalaGenController.scala:117-118`). The actual body is emitted into a separate `${lhs}_kernel.scala` stream via `inGen(kernel(lhs))`, with `object ${lhs}_kernel { def run(...) = ... }` around the supplied body (`ScalaGenController.scala:123-134`; `spatial/argon/src/argon/codegen/Codegen.scala:201-202`). The caller then emits a plain `val $lhs = ${lhs}_kernel.run($inputs)` (`ScalaGenController.scala:138`). This wrapper is a compile-size workaround and closure boundary; it does not introduce concurrency.

## AccelScope and UnitPipe context

`AccelScope` uses that wrapper with no enable gate, enters a `try`, optionally pushes resource tracking, sets `globalMems = true`, and currently always emits `gen(func)` because the alternative forever-loop path is behind `if (true)` (`ScalaGenController.scala:142-150`). After the block, it dumps non-DRAM stream outputs, calls `emitControlDone(lhs)`, closes buffered outputs, and exits the tracker/catch wrapper (`ScalaGenController.scala:165-178`).

`UnitPipe` is the important contrast. Its body is `emitControlBlock(lhs, func); emitControlDone(lhs)` (`ScalaGenController.scala:180-184`). `emitControlBlock` has the outer-stream HACK: for `lhs.isOuterStreamControl`, it walks `block.stms`, detects child controllers, computes external stream/FIFO inputs, and repeatedly `visit(stm)` while those inputs are non-empty (`ScalaGenController.scala:22-45`). Non-outer-stream controls fall back to `gen(block)` (`ScalaGenController.scala:46-48`). The vault note summarizes the same drain-each-child behavior and warns it is not hardware-like feedback semantics (`Spatial Research/10 - Spec/50 - Code Generation/20 - Scalagen/50 - Controller Emission.md:71-82`).

## ParallelPipe visit order

`ParallelPipe` has no analogous special case: `case ParallelPipe(ens, func) => emitControlObject(lhs, ens, func){ gen(func); emitControlDone(lhs) }` (`ScalaGenController.scala:187-191`). That means the block is emitted exactly through normal Scala block generation. `ScalaCodegen.gen` converts `b.stms` into weighted statements, passes them to `javaStyleChunk`, and supplies `visit _` as the per-statement rule (`spatial/src/spatial/codegen/scalagen/ScalaCodegen.scala:37-54`). The base codegen `visit` simply delegates to `gen(lhs,rhs)` (`spatial/argon/src/argon/codegen/Codegen.scala:89-93`). Chunking may split source into helper objects, but the emitted chunk/subchunk calls are ordinary Scala calls in generated order (`Codegen.scala:163-195`).

So the simulator does not launch threads, futures, child kernels, or a scheduler for `ParallelPipe`. It evaluates one statement/controller emission after the previous one returns. FIFO and stream operations reinforce this non-back-pressure model: ScalaGen FIFOs are mutable queues, reads return invalid when empty, and writes enqueue when enabled (`spatial/src/spatial/codegen/scalagen/ScalaGenFIFO.scala:17-44`); stream reads/writes are the same queue-style dequeue/enqueue pattern (`spatial/src/spatial/codegen/scalagen/ScalaGenStream.scala:84-97`).

## Done and schedules

The apparent "done marking" is only a hook in current ScalaGen. `ScalaGenControl.emitControlDone` is empty (`spatial/src/spatial/codegen/scalagen/ScalaGenControl.scala:6-10`), and `ScalaGenStream.emitControlDone` just calls `super` (`spatial/src/spatial/codegen/scalagen/ScalaGenStream.scala:18-20`). Therefore `ParallelPipe` completion is the Scala method returning after sequential block execution; no done register or completion token is emitted.

Schedules are also not consulted by ScalaGen simulation of `ParallelPipe`. The branch receives only `(ens, func)` and uses only `gen(func)` plus the done hook (`ScalaGenController.scala:187-191`). By contrast, schedule metadata is consumed in other backends/tools: the runtime model emits `ControllerModel(... Left(${lhs.rawSchedule.toString}) ...)` for `ParallelPipe` (`spatial/src/spatial/model/RuntimeModelGenerator.scala:305-309`), and PIR calls `createCtrl(schedule=${lhs.sym.schedule})` (`spatial/src/spatial/codegen/pirgen/PIRGenController.scala:31-35`). That contrast supports treating parallel interleaving/back-pressure as a deliberate RTL/modeling extension, not as current ScalaGen reference semantics.
