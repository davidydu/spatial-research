---
type: "research"
decision: "D-03"
angle: 7
---

# Rust/HIR semantics for while and early return

## Current Spatial Baseline

Spatial's Scala frontend currently answers D-03 conservatively: `return`, `while`, and `do while` are intercepted by virtualization hooks and rejected with explicit errors, not lowered into the Spatial IR (`src/spatial/lang/api/SpatialVirtualization.scala:103-113`). By contrast, `if` is an expression-level staged construct: both branches are staged as `Block[A]`, the result type is taken from the then block, and an `IfThenElse[A]` node is emitted (`src/spatial/lang/api/SpatialVirtualization.scala:71-100`). Argon blocks are typed containers with inputs, linearized statements, a symbolic result, effect summary, and options (`argon/src/argon/Block.scala:6-13`). Therefore a Rust/HIR frontend should not accidentally preserve host-language control flow by running a Rust loop around staging; it must choose between "unsupported" and new, explicit HLS-visible IR semantics.

## Typing Obligations

For Rust `while` and `do while`, the default expression type should be unit unless the construct is statically divergent (Rust rule, unverified). In Spatial terms, a loop body is normally a `Block[Void]`: `Foreach` stages `func(iters); void` (`src/spatial/lang/control/ForeachClass.scala:26-31`), and unit controllers also stage `func; void` (`src/spatial/lang/control/Control.scala:16-18`). If Rust permits `return expr` inside a block, the frontend must model the enclosing function's result as a control-flow value: every path either yields the normal tail expression or an early-return payload. This likely requires an internal "returned flag + return value" join, because the current `IfThenElse[T]` only aliases branch results of the same `T` (`argon/src/argon/node/IfThenElse.scala:7-8`).

`do while` adds one obligation beyond `while`: the body must execute once before the guard is tested (unverified). If lowered to Spatial's `StateMachine`, that requires either a state bit indicating first entry or a separate pre-body stage, because `StateMachine` exposes `notDone`, `action`, and `nextState` lambdas (`src/spatial/node/Control.scala:103-118`).

## Effects and Loop-Carried State

Early return cannot be treated as Scala/Rust host `return`; Spatial already rejects that form (`src/spatial/lang/api/SpatialVirtualization.scala:103-105`). It is an effectful control result that gates later staged effects. Argon effects track unique, sticky, simple, global, mutable, throwing, read, write, and anti-dependency summaries (`argon/src/argon/Effects.scala:5-19`), and an operation's effects fold over its blocks (`argon/src/argon/Op.scala:69-70`). Thus the frontend must ensure statements after a possible return are conditionally disabled, not merely omitted during staging. Mutable writes already participate in effect summaries through read/write sets (`argon/src/argon/Effects.scala:52-53`).

Loop-carried Rust locals should lower to explicit state, not hidden host mutation. Spatial's existing dynamic-loop shape is `FSM`: it binds a current state variable, stages `notDone`, `action`, and `nextState`, then emits a `StateMachine` node (`src/spatial/lang/control/FSM.scala:18-23`). That is a natural target for `while` when the guard depends on values updated by the body. The Rust frontend must define phi-like joins for locals modified in the loop, for return flag/value, and for variables initialized only on some iterations (unverified).

## Boundedness and Controller Schedules

Spatial's HLS-friendly loops are normally counter-based: `Counter(start,end,step,par)` stages `CounterNew` (`src/spatial/lang/Counter.scala:14-23`), `Foreach` wraps a `CounterChain` and records iterator metadata (`src/spatial/lang/control/ForeachClass.scala:26-31`). The IR also has `ForeverNew`, and metadata explicitly distinguishes controllers statically known to run forever plus descendants that will run forever (`src/spatial/node/Control.scala:13-15`; `src/spatial/metadata/control/package.scala:302-314`). Some analyses only process loops whose counterchains are not forever (`src/spatial/traversal/AccessAnalyzer.scala:275-284`).

Therefore `while` support needs a boundedness policy: prove a counter-shaped bound, require an explicit max-iteration annotation, lower to `FSM` only in simulation/non-synth modes, or reject for HLS. If accepted, the loop must integrate with schedules. Spatial has named schedules such as `Sequenced`, `Pipelined`, and `Streaming` (`src/spatial/metadata/control/ControlData.scala:7-15`), and helper predicates distinguish looped, pipelined, streaming, and outer/inner controllers (`src/spatial/metadata/control/package.scala:244-299`). A Rust `while` must say which schedule it requests or infer one conservatively; early return inside a pipelined/streaming region is a controller-level break, not a branch-local expression.

## Parity and Diagnostics

Simulator/HLS parity is the sharp edge. Scala codegen already warns that `breakWhen` breaks at loop end in Scala while synthesis breaks immediately (`src/spatial/codegen/scalagen/ScalaGenController.scala:74-80`), while Chisel codegen wires a controller break signal from `stopWhen` and resets it on done (`src/spatial/codegen/chiselgen/ChiselGenController.scala:312-315`). FSMs have explicit Scala and Chisel lowering: Scala checks `notDone`, runs action, then updates state (`src/spatial/codegen/scalagen/ScalaGenController.scala:224-236`); Chisel drives next state and done condition from the staged lambdas (`src/spatial/codegen/chiselgen/ChiselGenController.scala:469-485`). The Rust frontend must either close this parity gap for `while`/`return` or diagnose constructs whose simulator and HLS timing would differ.

Diagnostics should name the semantic obligation that failed: non-HLS-visible host loop, unbounded loop, unsupported `do while` first-iteration semantics, early return crossing an `Accel`/controller boundary, return type join failure, effect after return that cannot be gated, or schedule conflict with streaming/pipelining. This keeps D-03 from silently expanding Spatial's language surface while inheriting unsupported behavior.
