---
type: "research"
decision: "D-03"
angle: 8
---

## Finding

For v1, preserving Spatial's current restrictions exactly is the lower-risk option: reject HLS-visible `while`, `do while`, and early `return`, then require users to spell hardware loops as existing Spatial controllers. The source boundary is explicit. The virtualizer rewrites Scala `return`, `while`, and `do while` into `__return`, `__whileDo`, and `__doWhile` hook calls (`forge/src/forge/tags/Virtualizer.scala:153-165`), and Spatial implements those hooks as staging errors with the messages "return is not yet supported within spatial applications," "while loops are not yet supported within spatial applications," and "do while loops are not yet supported within spatial applications" (`src/spatial/lang/api/SpatialVirtualization.scala:103-114`). That makes acceptance in the Rust/HLS frontend a new semantic feature, not just syntax parity (unverified).

## User Impact And Compatibility

The downside is real but bounded. Users cannot directly port source patterns like `while cond { ... }` or early `return value`; they must rewrite into counted loops, explicit state machines, branches, accumulator values, side-effecting memories, or controller-local early exits. That is migration friction (unverified), especially for imperative algorithms whose exit condition depends on loop-carried state.

The compatibility upside is stronger. Existing legal Spatial programs already use controller APIs, so preserving the restriction should not change their staged IR or generated hardware (unverified). Existing illegal programs continue to fail at the same semantic boundary instead of silently acquiring Rust-only behavior. This matters because Spatial's supported loops carry hardware structure: `Foreach` builds a `CounterChain`, binds iterator symbols, stages the body block, and emits `OpForeach(..., opt.stopWhen)` (`src/spatial/lang/control/ForeachClass.scala:26-33`). Counters carry explicit start, end, step, and parallelism before staging `CounterNew` (`src/spatial/lang/Counter.scala:15-23`).

## Diagnostics

The current diagnostic quality is clear but not very helpful. Spatial points at source context because `SrcCtx` records file, line, column, content, and previous context (`forge/src/forge/SrcCtx.scala:5-12`), and `error(ctx, msg)` prints the message, logs the error, then staging exits on accumulated errors (`argon/src/argon/static/Printing.scala:71-76`, `argon/src/argon/Compiler.scala:100-112`). The exact restriction therefore gives users an early compile-time failure before passes, simulation, or codegen.

The v1 improvement opportunity is diagnostic text, not semantics (unverified). A Rust frontend can preserve the rejection while saying which replacement to consider: `Foreach` for counted loops, `FSM` for state-dependent termination, `Stream.Foreach(*)` for forever streaming loops, or `breakWhen` only for local controller termination. That would improve usability without defining new HLS-visible control behavior (unverified).

## Divergence Risk

Preserving the restriction also avoids a new simulator/synthesis divergence surface. Spatial already has one narrow early-exit caveat: Scala generation warns that `breakWhen` breaks at the end of the loop in Scala while `--synth` breaks immediately (`src/spatial/codegen/scalagen/ScalaGenController.scala:74-93`). In Chisel generation, the controller's `stopWhen` flag is wired to the state machine `break` input and reset on done (`src/spatial/codegen/chiselgen/ChiselGenController.scala:312-315`). If Rust `while` were lowered casually through `breakWhen`, users might read it as ordinary source-language loop semantics while getting controller-local hardware termination semantics (unverified).

Early `return` is even riskier. Spatial's blocks are staged regions captured by `stageScope` / `stageBlock`, which reify a by-name block into scheduled statements (`argon/src/argon/static/Scoping.scala:50-60`, `argon/src/argon/static/Scoping.scala:88-108`). A return that unwinds nested staged regions or skips later effects would need explicit IR and effect rules rather than just a frontend rewrite (unverified).

## Extensibility And Alternatives

Keeping the restriction for v1 does not close the door. The syntax-to-hook split means the frontend can reject now and later give `while` a deliberate lowering once the semantics are designed (`forge/src/forge/tags/Virtualizer.scala:153-165`, `src/spatial/lang/api/SpatialVirtualization.scala:103-114`). The existing IR already covers many intended cases: `Stream.apply(*)` delegates to `Foreach(*)`, the wildcard becomes `ForeverNew`, and `Accel(*)` wraps a forever stream loop (`src/spatial/lang/control/Control.scala:35-46`, `src/spatial/lang/api/Implicits.scala:72-73`, `src/spatial/lang/control/AccelClass.scala:11-14`). `FSM` stages `notDone`, `action`, and `nextState` lambdas into `StateMachine` (`src/spatial/lang/control/FSM.scala:18-24`), and the executor checks `notDone`, runs one action iteration, then computes the next state (`src/spatial/executor/scala/ControlExecutor.scala:1033-1053`).

So `while` is representable today only when the user chooses the matching Spatial form: counted `while` as `Foreach`, forever/streaming `while` as `Stream.Foreach(*)`, stateful pre-test loops as `FSM`, and local early exit as `breakWhen`. Arbitrary source `while` and early `return` are not represented as such today, and v1 should preserve that fact.
