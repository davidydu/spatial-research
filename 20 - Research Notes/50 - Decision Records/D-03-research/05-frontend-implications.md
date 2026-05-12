---
type: "research"
decision: "D-03"
angle: 5
---

## Virtualization Boundary

Spatial's Scala frontend gets its semantics before normal Scala control flow can fully harden. The `@spatial` annotation is an `AppTag` wrapper in the DSL surface, and `AppTag` both mixes classes or objects into `SpatialApp` and runs the virtualizer on annotated definitions (`src/spatial/dsl.scala:35-38`, `forge/src/forge/tags/AppTag.scala:17-24`). The virtualizer's contract is explicit: surface `var`, `if`, `return`, assignment, `while`, and `do while` are rewritten to hook calls such as `__newVar`, `__ifThenElse`, `__return`, `__assign`, and `__whileDo` (`forge/src/forge/tags/Virtualizer.scala:13-21`). If a DSL does not override those hooks, `EmbeddedControls` falls back to ordinary Scala behavior by re-emitting `if`, assignment, `return`, and loops (`forge/src/forge/EmbeddedControls.scala:20-31`, `forge/src/forge/EmbeddedControls.scala:115-143`).

Implication for Rust: the frontend should not treat Rust syntax as directly equivalent to Spatial IR. It should parse into explicit HIR constructs that correspond to Spatial hooks. Rust syntax details here are general language knowledge (unverified), but the design principle is source-backed: semantics come from hook binding, not from the host language construct itself.

## Staged Regions

`@rig` is important because it expands methods with source context and staged state plumbing (`forge/src/forge/tags/rig.scala:7-16`). Spatial's staged blocks are also deliberate regions, not passive AST children. `stageScope` accepts a call-by-name block, starts a new scope, reifies the block, then schedules the captured statements into a `Block` (`argon/src/argon/static/Scoping.scala:50-60`, `argon/src/argon/static/Scoping.scala:88-108`). A `Block` stores inputs, linearized statements, result, effects, and scheduling options (`argon/src/argon/Block.scala:6-11`).

The control APIs use this machinery pervasively. `Accel` captures a by-name accelerator body into `AccelScope(stageBlock { ... })` (`src/spatial/lang/control/AccelClass.scala:17-19`). `Pipe` and `Sequential` share `unit_pipe(func: => Any)`, which builds a `UnitPipe` from `stageBlock` (`src/spatial/lang/control/Control.scala:16-27`, `src/spatial/lang/control/Control.scala:49-57`). `Foreach` creates bound iterator symbols and stages the loop body as a block (`src/spatial/lang/control/ForeachClass.scala:26-31`). `FSM` uses staged lambdas for `notDone`, `action`, and `nextState` (`src/spatial/lang/control/FSM.scala:18-23`).

## Why `if` Works

`if` is tractable because Spatial defines typed, block-local HLS semantics for a staged `Bit` condition. `SpatialVirtualization` overloads `__ifThenElse` for staged branch result combinations, delays branch evaluation with by-name parameters, captures both branches using `stageBlock`, and stages an `IfThenElse` node when the condition is not a literal (`src/spatial/lang/api/SpatialVirtualization.scala:71-100`). The IR node is simply condition plus two blocks, with aliases taken from the branch results (`argon/src/argon/node/IfThenElse.scala:7-8`).

Downstream passes recognize that node as control: metadata marks `IfThenElse` as control and branch-like (`src/spatial/metadata/control/package.scala:36-48`), flow rules collect branch children and give it `Fork` scheduling (`src/spatial/flows/SpatialFlowRules.scala:69-76`, `src/spatial/flows/SpatialFlowRules.scala:331-337`), and `SwitchTransformer` lowers it to `Switch`/`SwitchCase` within accelerator scopes (`src/spatial/transform/SwitchTransformer.scala:11-32`, `src/spatial/transform/SwitchTransformer.scala:77-85`). A Rust HIR can mirror this: staged `if` should be a typed branch-region node, distinct from host/control-time `if` (unverified).

## Vars, Assignment, And The Hard Part

Scala `var` is virtualized into `__newVar`, and assignment into `__assign` (`forge/src/forge/tags/Virtualizer.scala:101-126`, `forge/src/forge/tags/Virtualizer.scala:181`). Spatial then maps staged `__newVar` to `Var.alloc`, maps assignment on `VarLike` to staged writes, and maps `__use` on `Var` to staged reads (`src/spatial/lang/api/SpatialVirtualization.scala:40-69`). Argon represents this as `VarNew`, `VarRead`, and `VarAssign`; `VarNew` is mutable and `VarAssign` writes the variable (`argon/src/argon/node/Var.scala:7-14`, `argon/src/argon/node/Var.scala:38-45`).

The fragility is in `VarRead`: it rewrites to the most recent `VarAssign` in the current scope, with a comment noting that this assumes all statements in a block are always executed (`argon/src/argon/node/Var.scala:23-35`). `if` survives because branch bodies are isolated blocks. General `while` and early `return` break the straight-line assumption: a loop body may execute zero or many times, and a return may skip later effects. A Rust frontend therefore needs typed staged regions, dominance/effect tracking, and explicit loop or early-exit nodes before assigning HLS meaning to `let mut`, assignment, `while`, or `return` (unverified).

## Recommendation For D-03

Preserve Spatial's current unsupported behavior for HLS-visible `while`, `do while`, and early `return`. Spatial explicitly rejects `return`, `while`, and `do while` in staged applications (`src/spatial/lang/api/SpatialVirtualization.scala:103-114`). This is not a missing parser case; it is a semantic boundary. The existing loop forms are structured controls such as `OpForeach`, `UnitPipe`, and `StateMachine`, each with staged bodies and known scheduling structure (`src/spatial/node/Control.scala:33-54`, `src/spatial/node/Control.scala:103-118`).

For Rust HIR, allow only final-expression block results inside staged regions, reject early `return`, and reject staged `while` unless D-03 explicitly chooses a new design. If new semantics are desired, they should be designed as first-class HIR control regions that lower to `StateMachine`, `Foreach`, or another explicit Spatial loop node, with mutation/effect rules written before implementation.
