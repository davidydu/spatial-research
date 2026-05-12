---
type: "research"
decision: "D-03"
angle: 9
---

# D-03 Angle 9: Precedent in DSL-to-HLS/compiler frontends

Spatial source citations are relative to `/Users/david/Documents/David_code/spatial`.

## Spatial Baseline

Spatial's current behavior is not an accidental backend limitation: the Scala virtualization layer intercepts host-language `return`, `while`, and `do while` and reports them as unsupported before they can become Spatial IR. The hooks are explicit: `__return` emits "return is not yet supported within spatial applications" and `__whileDo` / `__doWhile` emit analogous loop errors (`src/spatial/lang/api/SpatialVirtualization.scala:103`, `src/spatial/lang/api/SpatialVirtualization.scala:107`, `src/spatial/lang/api/SpatialVirtualization.scala:111`). By contrast, staged `if` is supported by staging both branches into blocks and creating an `IfThenElse` node (`src/spatial/lang/api/SpatialVirtualization.scala:93`). This establishes a precedent inside Spatial itself: host control that can be represented as structured IR is admitted; host control whose semantics would escape the staging model is rejected.

The supported alternatives are named control constructs. `Pipe`, `Stream`, and `Sequential` stage a `UnitPipe` with an optional `stopWhen` register (`src/spatial/lang/control/Control.scala:16`, `src/spatial/lang/control/Control.scala:22`). `Foreach` stages an `OpForeach` with a counter chain, staged block, bound iterators, and `opt.stopWhen` (`src/spatial/lang/control/ForeachClass.scala:26`). The IR makes these choices visible: `UnitPipe`, `OpForeach`, `OpReduce`, `OpMemReduce`, and unrolled forms all carry `stopWhen` fields, while `StateMachine` is a distinct loop node with `start`, `notDone`, `action`, and `nextState` lambdas (`src/spatial/node/Control.scala:33`, `src/spatial/node/Control.scala:45`, `src/spatial/node/Control.scala:103`).

## Precedent Classes

Structured control DSL precedent favors explicit control nodes over importing arbitrary host control (unverified). Spatial follows that pattern: a loop is not "whatever Scala while did"; it is a counter-chain controller, a unit pipe, a stream controller, or an FSM. FSM precedent is especially close to HLS: instead of giving users a source-language `while`, Spatial asks for a hardware-relevant transition system via `FSM(init)(notDone)(action)(next)`, then stages separate lambdas for done condition, action, and next state (`src/spatial/lang/control/FSM.scala:8`, `src/spatial/lang/control/FSM.scala:18`).

Dataflow-kernel precedent also argues for explicit protocols rather than early returns (unverified). Spatial's stream/dataflow surface names this directly. `Stream(breakWhen)` is documented as breaking immediately when a register is true and resetting that register when the controller finishes, with a warning that the behavior is tricky (`src/spatial/lang/control/Control.scala:41`). For controller black boxes, Spatial assumes ready/valid input and output ports, `ready_downstream`, and `done`; such a module is an inner controller under a `Stream` (`src/spatial/lang/Blackbox.scala:77`). This is closer to a handshake contract than to C-style local control flow.

## While/Return Comparison

C/HLS frontends commonly accept `while` and `return` because C is the source language whose control-flow graph the tool owns (unverified). That is a different contract from Spatial's current DSL. If the Rust/HLS frontend exposes Rust `while` or early `return` as synthesizable behavior, it is not merely preserving Spatial; it is defining new HLS-visible semantics and must specify lowering, scheduling, and interaction with streaming break/done signals.

Spatial already shows why this matters. Break behavior is a controller feature, not host-language control flow. Metadata can recover a controller's `breaker` from its `stopWhen` field (`src/spatial/metadata/control/package.scala:423`), and the use analyzer marks these registers as breakers (`src/spatial/traversal/UseAnalyzer.scala:57`). Backend behavior is specialized enough that Scala simulation warns that `breakWhen` occurs at the end of the Scala loop while synthesis breaks immediately (`src/spatial/codegen/scalagen/ScalaGenController.scala:75`). Chisel emission wires `stopWhen` into `sm.io.break` and resets the register on done (`src/spatial/codegen/chiselgen/ChiselGenController.scala:312`). A host-language `while` or `return` would have to decide whether it means Scala-simulation behavior, synthesis behavior, controller break, stream completion, or method exit.

## Implication for D-03 / Q-048

The precedent points toward preserving Spatial's rejection unless D-03 deliberately expands the language. Structured DSLs, FSM APIs, and dataflow controllers all push early-exit semantics into explicit IR nodes and handshake/control signals (unverified). Spatial's local source is consistent with that design: unsupported host `while`/`return` are rejected at virtualization, while supported dynamic termination is expressed as `FSM` or `breakWhen`.

Therefore the conservative Rust/HLS frontend choice is to reject Rust `while` and early `return` in Spatial application regions, and direct users to explicit structured controls or FSM-like constructs. Supporting them can be reasonable, especially if the new frontend wants C/HLS familiarity, but that should be recorded as a new semantic decision with tests for simulation/synthesis divergence, break timing, stream done/backpressure, nested controllers, and return values from staged blocks.
