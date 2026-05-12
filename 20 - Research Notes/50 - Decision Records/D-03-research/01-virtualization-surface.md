---
type: "research"
decision: "D-03"
angle: 1
---

# Spatial Virtualization Source Surface

## Scope

Spatial's virtualized frontend is concentrated in `SpatialVirtualization`, which is mixed into `StaticAPI_Internal` and therefore inherited by the external, frontend, and shadowing API views (`src/spatial/lang/api/StaticAPI.scala:7-35`). The file imports `argon.node.IfThenElse`, `forge.tags._`, and `forge.{Ptr, VarLike}`, then defines the hooks that Scala-Virtualized style rewriting targets: `__newVar`, `__assign`, `__use`, `__ifThenElse`, `__return`, `__whileDo`, `__doWhile`, and `__throw` (`src/spatial/lang/api/SpatialVirtualization.scala:3-10`, `src/spatial/lang/api/SpatialVirtualization.scala:35-116`). The adjacent spec already flags this as a rework area because HLS must either preserve current unsupported syntax or add new semantics (unverified).

## Supported Variable Hooks

The frontend supports mutable surface syntax, but with a split between plain Scala-like pointers and staged `Var`s. The low-priority fallback `__newVar[T](init)` returns a `forge.Ptr[T]`, whose implementation is just a mutable host box with `__read` returning `value` and `__assign` updating it (`src/spatial/lang/api/SpatialVirtualization.scala:12-16`, `forge/src/forge/Ptr.scala:3-5`). For staged values, `__newVar[A <: Top[A]: Type](init)` allocates an argon `Var` with `Var.alloc(Some(init))`; the lifted overload first converts through `Lifting[A,B]` and then allocates `Var[B]` (`src/spatial/lang/api/SpatialVirtualization.scala:40-45`). `Var.alloc`, `Var.read`, and `Var.assign` stage `VarNew`, `VarRead`, and `VarAssign` nodes respectively (`argon/src/argon/lang/Var.scala:16-19`).

Assignment is explicitly supported for `VarLike[T]`. If the left side is an argon `Var`, staged right-hand sides must conform to the variable's type, mismatches report a type error, and non-staged data is converted through the variable type's `from` method (`src/spatial/lang/api/SpatialVirtualization.scala:51-58`). Non-argon `VarLike`s fall back to `v.__assign(rhs.asInstanceOf[T])` with a runtime-class mismatch diagnostic if that cast path fails (`src/spatial/lang/api/SpatialVirtualization.scala:59-65`). Use sites are likewise explicit: `__use` reads `Ptr` through `__read` and staged `Var` through `__sread()` (`src/spatial/lang/api/SpatialVirtualization.scala:67-70`). In argon, staged var reads and writes are rejected outside a staging `State`, which makes these hooks a staging-time surface rather than free host mutation (`argon/src/argon/StagedVarLike.scala:11-25`).

## Supported Conditional Hook

Virtualized `if` is the supported control hook. `SpatialVirtualization` defines overloads for `Bit` conditions with lifted arms, `Sym`/`Literal` mixtures, plain `Sym` arms, and `Void` arms (`src/spatial/lang/api/SpatialVirtualization.scala:71-91`). The shared `ifThenElse` helper constant-folds literal `true` and `false` conditions by executing only the selected branch; otherwise it stages both branch blocks and emits `IfThenElse[A](cond, blkThen, blkElse)` (`src/spatial/lang/api/SpatialVirtualization.scala:93-101`). The argon node stores the `Bit` condition and the two `Block[T]` arms, and aliases the two block results (`argon/src/argon/node/IfThenElse.scala:7-8`). Downstream, `IfThenElse` is recognized as control metadata and hardware-scope conditionals may be transformed into `Switch`/`SwitchCase` form (`src/spatial/metadata/control/package.scala:36-47`, `src/spatial/transform/SwitchTransformer.scala:11-32`, `src/spatial/transform/SwitchTransformer.scala:77-85`).

## Rejected or Non-Staged Hooks

The strongest D-03 evidence is that `return`, Scala `while`, and Scala `do while` are not partial implementations. They are explicit frontend errors: `__return` emits `"return is not yet supported within spatial applications"`, `__whileDo` emits `"while loops are not yet supported within spatial applications"`, and `__doWhile` emits `"do while loops are not yet supported within spatial applications"` (`src/spatial/lang/api/SpatialVirtualization.scala:103-114`). Forge's default virtualized controls would macro-expand those constructs back to normal Scala `return`, `while`, and `do while`, so Spatial is intentionally overriding the default for accelerator applications rather than passively inheriting Scala behavior (`forge/src/forge/EmbeddedControls.scala:49-52`, `forge/src/forge/EmbeddedControls.scala:131-144`).

`__throw` is different. Spatial delegates it to `forge.EmbeddedControls.throwImpl` instead of producing a Spatial diagnostic or staging an IR node (`src/spatial/lang/api/SpatialVirtualization.scala:116`). Forge's macro expands that hook to a Scala `throw` (`forge/src/forge/EmbeddedControls.scala:146-149`). Therefore the current frontend does not define HLS-visible exception semantics; treating `throw` as accelerator control flow would be new behavior (unverified).

## D-03 Implication

The current supported surface is structured Spatial control such as `Pipe`, `Stream`, `Sequential`, `Foreach`, and `FSM`, not arbitrary virtualized Scala loops. `Foreach` stages `OpForeach` over counters and `FSM` stages `StateMachine` from explicit not-done, action, and next-state lambdas (`src/spatial/lang/control/Control.scala:22-72`, `src/spatial/lang/control/ForeachClass.scala:26-33`, `src/spatial/lang/control/FSM.scala:18-24`). For D-03, preserving Spatial means rejecting `return`, `while`, `do while`, and HLS-visible `throw` in the Rust frontend unless a separate design defines scheduling, termination, side effects, and codegen obligations for them (unverified). The source surface favors preserve-and-reject as the compatibility baseline.
