---
type: spec
concept: virtualization-language-surface
source_files:
  - "src/spatial/lang/api/SpatialVirtualization.scala:1-153"
  - "src/spatial/lang/api/Implicits.scala:1-79"
  - "src/spatial/lang/api/UserData.scala:1-13"
source_notes:
  - "[[language-surface]]"
hls_status: rework
depends_on:
  - "[[50 - Math and Helpers]]"
  - "[[90 - Aliases and Shadowing]]"
  - "[[10 - Spec/30 - IR/00 - Argon Framework/C0 - Macro Annotations]]"
status: draft
---

# Virtualization

## Summary

Spatial's user syntax relies on virtualization hooks that `@virtualize` rewrites into methods such as `__newVar`, `__assign`, `__use`, and `__ifThenElse`. `SpatialVirtualization` imports `forge.tags._`, defines these hooks, and requires `this: Implicits with MiscAPI`, so virtualization is part of the same StaticAPI stack that supplies casts, muxes, and `void` (`src/spatial/lang/api/SpatialVirtualization.scala:3-8`, `src/spatial/lang/api/SpatialVirtualization.scala:18-20`). The supported core is staged variable allocation, staged assignment, staged var use, and virtualized `if`/`else` over `Bit` conditions (`src/spatial/lang/api/SpatialVirtualization.scala:40-101`). The unsupported core is equally important: `return`, `while`, and `do while` all emit user-facing errors, and `throw` is not staged into Spatial IR (`src/spatial/lang/api/SpatialVirtualization.scala:103-116`).

## Syntax or API

```scala
var x = 0.to[I32]                // __newVar; SpatialVirtualization.scala:40-45
x = x + 1                        // __assign; SpatialVirtualization.scala:48-65
if (bit) a else b                // __ifThenElse; SpatialVirtualization.scala:71-101

bound.update(x, 1024)            // UserData.scala:9-10
val p: I32 = 1 (1 -> 5)          // Implicits.scala:18-39
r :+= 1; r :-= 1; r :*= 2        // Implicits.scala:60-69
```

## Semantics

> [!warning] User-facing limitation
> `return`, `while`, and `do while` are not supported in Spatial applications. The hooks emit explicit errors saying `return is not yet supported within spatial applications`, `while loops are not yet supported within spatial applications`, and `do while loops are not yet supported within spatial applications` (`src/spatial/lang/api/SpatialVirtualization.scala:103-114`). The HLS port must either inherit these limitations or intentionally add semantics for them.

`LowPriorityVirtualization.__newVar[T](init)` returns a plain `forge.Ptr[T]`, which is the low-priority fallback for non-Spatial values (`src/spatial/lang/api/SpatialVirtualization.scala:12-16`). `SpatialVirtualization.__newVar[A <: Top[A]: Type](init)` allocates an argon `Var` initialized with the staged value, while the overloaded lifted form converts the Scala value through `Lifting[A,B]` and allocates a `Var[B]` (`src/spatial/lang/api/SpatialVirtualization.scala:40-45`). `__valName` attaches a source-level value name to a staged `Sym` only when `state.isStaging` is true (`src/spatial/lang/api/SpatialVirtualization.scala:35-38`).

`__assign(lhs, rhs)` is macro-routed through `forge.EmbeddedControls.assignImpl`, then implemented for `VarLike[T]` in the Spatial trait (`src/spatial/lang/api/SpatialVirtualization.scala:48-52`). If the target is an argon `Var`, assignment accepts a `Top[_]` whose type conforms to the var type, rejects mismatched staged types with an error, or converts non-staged data through `v.A.from(data)` (`src/spatial/lang/api/SpatialVirtualization.scala:51-58`). If the target is any other `VarLike`, it tries `v.__assign(rhs.asInstanceOf[T])` and reports a type mismatch from runtime class names if that cast path fails (`src/spatial/lang/api/SpatialVirtualization.scala:59-65`). `__use` reads `Ptr` through `__read` and staged `Var` through `__sread()` (`src/spatial/lang/api/SpatialVirtualization.scala:67-70`).

Virtualized `if` is supported for `Bit` conditions through seven overloads of `__ifThenElse`, covering lifted values, mixed `Sym`/`Literal` arms, raw `Sym` arms, and `Void` arms (`src/spatial/lang/api/SpatialVirtualization.scala:71-91`). The shared `ifThenElse` helper constant-folds literal true/false conditions by executing only the selected branch, otherwise stages both branch blocks and emits `IfThenElse[A](cond, blkThen, blkElse)` (`src/spatial/lang/api/SpatialVirtualization.scala:93-101`). This is the staged control-flow integration; the `If`/`IfElse` helpers in debugging are separate unstaged Scala-boolean utilities (`src/spatial/lang/api/DebuggingAPI.scala:215-229`).

`__return`, `__whileDo`, and `__doWhile` are hard errors, not delayed warnings (`src/spatial/lang/api/SpatialVirtualization.scala:103-114`). `__throw` is also not a staged Spatial construct in this file: it delegates to `forge.EmbeddedControls.throwImpl` instead of staging an IR node (`src/spatial/lang/api/SpatialVirtualization.scala:116`; inferred external macro behavior, unverified here). This means exception syntax does not have a defined accelerator semantics in the Spatial surface (inferred, unverified; source hook at `src/spatial/lang/api/SpatialVirtualization.scala:116`).

## Implementation

`Implicits` fills in the syntax that makes virtualized code compact. `Bit` and `Fix` casts are two-way: `Bit` to `Fix` uses `mux(x, 1.to[Fix], 0.to[Fix])`, and `Fix` to `Bit` checks `x !== 0` (`src/spatial/lang/api/Implicits.scala:11-16`). `IntParameters` lets a Scala `Int` literal become an `I32` parameter through syntax such as `1 (1 -> 5)`, `1 (1 -> 2 -> 8)`, or `1 (1,2,4,8,16)` (`src/spatial/lang/api/Implicits.scala:18-39`). `createParam` stores either a range domain or explicit alternatives in parameter metadata (`src/spatial/lang/api/Implicits.scala:46-55`).

Register ergonomics are implicit. `regRead[A](x: Reg[A])` auto-reads a `Reg[A]` as `x.value`, and `regNumerics` adds `:+=`, `:-=`, and `:*=` by rewriting to `reg := reg.value op data.unbox` (`src/spatial/lang/api/Implicits.scala:60-69`). A `Wildcard` converts to `ForeverNew()`, so `*`-style ranges can become counters, and a `Series[Fix[...]]` converts to `Counter.from(x)` (`src/spatial/lang/api/Implicits.scala:72-77`). `UserData.bound.update(x, bound)` boxes the value and writes `UpperBound(bound)` metadata, giving users a direct upper-bound annotation hook (`src/spatial/lang/api/UserData.scala:7-10`).

## Interactions

`SpatialVirtualization` is mixed into `StaticAPI_Internal`, so every external and shadowing API layer inherits the same virtualized control hooks (`src/spatial/lang/api/StaticAPI.scala:7-22`). Its `ifThenElse` emits argon's `IfThenElse` node after staging both blocks, so it interacts with control-flow lowering and block scheduling downstream (`src/spatial/lang/api/SpatialVirtualization.scala:93-101`). The `@virtualize` macro itself comes from `forge.tags`; this entry only documents Spatial's hook implementations and links to [[10 - Spec/30 - IR/00 - Argon Framework/C0 - Macro Annotations]] for macro mechanics (`src/spatial/lang/api/SpatialVirtualization.scala:3-8`).

## HLS notes

`hls_status: rework`. The supported hooks map cleanly to a Rust/HLS frontend as mutable staged variables, assignment, and conditional expressions or control blocks (`src/spatial/lang/api/SpatialVirtualization.scala:40-101`). The unsupported hooks are a real language limitation, not a documentation gap: `return`, `while`, and `do while` emit errors today (`src/spatial/lang/api/SpatialVirtualization.scala:103-114`). If the HLS surface adds `while`, it must define scheduling, termination, and effect semantics that current Spatial deliberately avoids (inferred, unverified).

## Open questions

- See `[[open-questions-lang-surface]]` Q-lang-15 (`throw` hook is not staged), Q-lang-16 (`whether HLS should preserve or lift the no-while/no-return limitation), and Q-lang-17 (`parameter-domain metadata shape for Rust/HLS`).
