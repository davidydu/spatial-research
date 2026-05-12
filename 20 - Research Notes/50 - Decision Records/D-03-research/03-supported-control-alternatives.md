---
type: "research"
decision: "D-03"
angle: 3
---

## Finding

Spatial already has HLS-visible alternatives for most practical `while` and early-exit patterns, but they are explicit Spatial controllers rather than virtualized Scala control. The compatibility baseline is still rejection: `__return` reports that return is not supported, and `__whileDo` / `__doWhile` report that while loops are not supported (`src/spatial/lang/api/SpatialVirtualization.scala:103-114`). Therefore the Rust/HLS frontend can preserve current Spatial behavior by rejecting source `while` and source `return`; accepting them would define new frontend semantics (unverified).

## Counted and Forever Iteration

`Foreach` is the main counted-loop replacement. Its API accepts one or more `Counter[I32]` domains, creates bound iterator variables, builds a `CounterChain`, and stages `OpForeach(..., cchain, block, iters, opt.stopWhen)` (`src/spatial/lang/control/ForeachClass.scala:10-33`). Counters carry explicit start, end, step, and parallelization, then stage `CounterNew` (`src/spatial/lang/Counter.scala:15-23`). The wildcard form is not a Scala `while`; `*` is converted to `ForeverNew`, and `Stream.Foreach(*)` or `Accel(*)` use that counter to express a forever/streaming controller (`src/spatial/lang/api/Implicits.scala:72-73`, `src/spatial/lang/control/Control.scala:39`, `src/spatial/lang/control/AccelClass.scala:11-14`).

`Reduce` and `MemReduce` cover common loop-carried accumulation without needing a `return`. `Reduce` stages a map block, accumulator load, reduction lambda, accumulator store, and returns the accumulator `Reg[A]` (`src/spatial/lang/control/ReduceClass.scala:37-52`). `MemReduce` similarly stages a map over the input domain plus a generated reduction counter chain over the sparse rank of the accumulator memory, then stores reduced values back to that memory (`src/spatial/lang/control/MemReduceClass.scala:33-93`). These constructs replace structured counted loops and reductions, not arbitrary mutable-condition loops.

## Explicit State Loops

`FSM` / `StateMachine` is the closest existing while-like construct. The frontend accepts an initial state plus `notDone`, `action`, and `next` lambdas, then stages `StateMachine(Set.empty, start, dBlk, aBlk, nBlk)` (`src/spatial/lang/control/FSM.scala:8-24`). The IR node stores those three blocks as `notDone`, `action`, and `nextState` (`src/spatial/node/Control.scala:103-118`). The Scala executor checks `notDone` between iterations, pushes one action iteration when it is true, and computes `nextState` after that action completes (`src/spatial/executor/scala/ControlExecutor.scala:1033-1053`). This covers pre-test loops with explicit state transitions, but not implicit Scala `while` mutation or arbitrary control escape.

## Composition and Branching

`Sequential`, `Pipe`, and `Stream` create `UnitPipe` controllers; `Sequential` is the sequenced unit controller, while `Pipe` and `Stream` select pipelined or streaming scheduling through `CtrlOpt` (`src/spatial/lang/control/Control.scala:16-65`). `Parallel` stages `ParallelPipe`, and flow rules assign it `ForkJoin`; `IfThenElse` and `Switch` are scheduled as forked branch controllers, while `SwitchCase` is sequenced (`src/spatial/lang/control/Parallel.scala:9-13`, `src/spatial/flows/SpatialFlowRules.scala:319-337`). Virtualized `if` is supported: literal conditions are folded, otherwise both branch blocks are staged as `IfThenElse`; in hardware scopes, `SwitchTransformer` converts `IfThenElse` to `Switch` / `SwitchCase` when needed (`src/spatial/lang/api/SpatialVirtualization.scala:93-101`, `src/spatial/transform/SwitchTransformer.scala:11-32`, `src/spatial/transform/SwitchTransformer.scala:77-85`). This provides conditional execution, not early function return.

## Early Exit Limits

Spatial's early-exit hook is controller-local `breakWhen`, stored internally as `stopWhen`. `Pipe`, `Stream`, and `Sequential` expose `apply(breakWhen: Reg[Bit])`, with comments saying the controller breaks immediately and resets the flag on finish for stream/sequential controllers (`src/spatial/lang/control/Control.scala:27`, `src/spatial/lang/control/Control.scala:41-56`). The IR carries `stopWhen` on `UnitPipe`, `OpForeach`, `OpReduce`, `OpMemReduce`, and unrolled loops, and metadata can recover it as the controller breaker (`src/spatial/node/Control.scala:33-50`, `src/spatial/node/Control.scala:57-92`, `src/spatial/node/Control.scala:121-140`, `src/spatial/metadata/control/package.scala:423-430`). Chisel generation wires that flag to the controller state-machine break input and resets it on done (`src/spatial/codegen/chiselgen/ChiselGenController.scala:312-315`). Scala codegen warns that Scala emulation observes the break at loop-end whereas synthesis breaks immediately (`src/spatial/codegen/scalagen/ScalaGenController.scala:75-93`).

What remains unsupported is source-level `while`, `do while`, and `return`, plus any early-exit semantics that require returning a value, unwinding nested scopes, or escaping an arbitrary block. Existing Spatial asks users to express those designs as counters, FSM state, branch controllers, accumulator results, memory side effects, or controller-local `breakWhen`. D-03 should treat HLS-visible `while`/`return` as new semantics unless it deliberately preserves the current reject-and-rewrite discipline.
