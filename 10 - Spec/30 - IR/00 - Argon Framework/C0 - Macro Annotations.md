---
type: spec
concept: Argon and Forge Macro Annotations
source_files:
  - "forge/src/forge/tags/ref.scala:9-70"
  - "forge/src/forge/tags/op.scala:9-48"
  - "forge/src/forge/tags/api.scala:9-31"
  - "forge/src/forge/tags/ctx.scala:9-24"
  - "forge/src/forge/tags/stateful.scala:9-30"
  - "forge/src/forge/tags/rig.scala:7-16"
  - "forge/src/forge/tags/data.scala:9-23"
  - "forge/src/forge/tags/rewrite.scala:9-72"
  - "forge/src/forge/tags/globalRewrite.scala:9-73"
  - "forge/src/forge/tags/flow.scala:9-62"
  - "forge/src/forge/tags/virtualize.scala:7-42"
  - "forge/src/forge/tags/Virtualizer.scala:8-286"
  - "forge/src/forge/tags/curriedUpdate.scala:7-58"
  - "forge/src/forge/tags/AppTag.scala:6-31"
  - "forge/src/forge/EmbeddedControls.scala:42-88"
  - "forge/src/forge/EmbeddedControls.scala:124-149"
  - "argon/src/argon/tags/Structs.scala:9-134"
  - "argon/src/argon/tags/Bits.scala:8-67"
  - "argon/src/argon/tags/Arith.scala:8-57"
  - "utils/src/utils/tags/MacroUtils.scala:16-24"
  - "utils/src/utils/tags/MacroUtils.scala:61-64"
  - "utils/src/utils/tags/MacroUtils.scala:117-126"
  - "utils/src/utils/tags/MacroUtils.scala:191-230"
  - "spatial/src/spatial/tags/StreamStructs.scala:11-109"
source_notes:
  - "[[argon-framework]]"
hls_status: rework
depends_on:
  - "[[10 - Symbols and Types]]"
  - "[[20 - Ops and Blocks]]"
  - "[[40 - Metadata Model]]"
  - "[[70 - Rewrites and Flows]]"
status: draft
---

# Argon and Forge Macro Annotations

## Summary

Forge annotations generate much of Argon's apparent API surface at Scala compile time. `@ref` builds staged type boilerplate, `@op` builds IR-node case-class and transformer boilerplate, `@ctx` and `@stateful` inject implicit `SrcCtx` and `State`, `@api` and `@rig` compose those injections, `@rewrite` and `@flow` register staging-time rules, and `@virtualize` rewrites Scala syntax into overridable method calls (`forge/src/forge/tags/ref.scala:17-49`; `forge/src/forge/tags/op.scala:25-35`; `forge/src/forge/tags/api.scala:24-29`; `forge/src/forge/tags/Virtualizer.scala:138-283`). Argon adds `@struct`, while Spatial adds `@streamstruct`, both using `MacroUtils` helpers for class/object surgery (`argon/src/argon/tags/Structs.scala:27-134`; `spatial/src/spatial/tags/StreamStructs.scala:29-108`; `utils/src/utils/tags/MacroUtils.scala:191-230`).

## Syntax or API

`@ref` accepts a class, optionally with a companion object, and permits at most one explicit and one implicit constructor parameter list (`forge/src/forge/tags/ref.scala:22-26`; `forge/src/forge/tags/ref.scala:58-62`). It injects `cargs`, `fresh`, `__typePrefix`, `__typeArgs`, and `__typeParams`, then creates an implicit or non-implicit companion `tp` factory using `argon.proto(new Class(...))` depending on constructor shape (`forge/src/forge/tags/ref.scala:37-48`). The source contains only a TODO to check that the class mixes `Ref[?,A]`, so that requirement is a convention rather than an enforced macro check in this file (`forge/src/forge/tags/ref.scala:27`).

`@op` accepts a class, makes it a case class, converts constructor parameters to `var`, and injects `mirror($f: Tx)` plus `update($f: Tx)` (`forge/src/forge/tags/op.scala:19-35`). Those edits use `MacroUtils.asCaseClass`, `withVarParams`, and `injectMethod` (`utils/src/utils/tags/MacroUtils.scala:216-230`; `utils/src/utils/tags/MacroUtils.scala:173-175`). `@ctx` injects an implicit `ctx: forge.SrcCtx`, and `@stateful` injects an implicit `state: argon.State` into a def or every method of an object (`forge/src/forge/tags/ctx.scala:19-23`; `forge/src/forge/tags/stateful.scala:22-29`). `@api` applies `@ctx` then `@stateful` to defs, and `@rig` performs the same composition (`forge/src/forge/tags/api.scala:24-29`; `forge/src/forge/tags/rig.scala:11-16`). `@data` is object-only and delegates to `stateful.impl` (`forge/src/forge/tags/data.scala:13-21`).

## Semantics

`@rewrite` first applies `@api`, then enforces a single explicit parameter, two injected implicit parameters, no type parameters, and a match-expression body (`forge/src/forge/tags/rewrite.scala:33-46`). It emits a `PartialFunction[(Op[_],SrcCtx,State),Option[Sym[_]]]` that casts the op, installs implicit `ctx` and `state`, evaluates the user partial function only when defined, and returns `Some(sym)` or `None` (`forge/src/forge/tags/rewrite.scala:48-56`). It registers with `IR.rewrites.add[ParamType]` unless the parameter type text starts with `Op[`, in which case it registers globally (`forge/src/forge/tags/rewrite.scala:57-64`). `@globalRewrite` always registers with `core.rewrites.addGlobal`, but the generated PF does include an `__op.isInstanceOf[ParamType]` guard before casting (`forge/src/forge/tags/globalRewrite.scala:48-64`). This is source-correct and differs from summaries that describe it as unguarded.

`@flow` applies `@api`, requires explicit `(lhs: Sym[_], rhs: Op[_])`, and uses `MacroUtils.isWildcardType` to reject non-wildcard type arguments (`forge/src/forge/tags/flow.scala:27-36`; `utils/src/utils/tags/MacroUtils.scala:61-64`). It emits a PF over `(Sym[_],Op[_],SrcCtx,State)`, binds the user names, installs implicit `ctx` and `state`, runs the body, and registers with `IR.flows.add` (`forge/src/forge/tags/flow.scala:40-53`).

## Implementation

`@virtualize` constructs a `Virtualizer` and runs it on the first annottee unless the annottee is a parameter or type alias, in which case it warns and leaves inputs unchanged (`forge/src/forge/tags/virtualize.scala:14-37`). `AppTag` uses the same virtualizer after mixing the requested DSL app trait into classes or objects (`forge/src/forge/tags/AppTag.scala:6-31`). The virtualizer rewrites mutable `var` definitions to `__newVar`, registers names with `__valName`, rewrites plain `val` names, rewrites `Template`, `Block`, and `Function` bodies, and transforms `if`, `return`, `while`, `do while`, assignment, `throw`, string-literal `+`, and many `Any`/`AnyRef` methods into method calls such as `__ifThenElse`, `__return`, `__assign`, `__throw`, and `infix_$eq$eq` (`forge/src/forge/tags/Virtualizer.scala:100-181`; `forge/src/forge/tags/Virtualizer.scala:183-244`). `Try` emits a warning and falls back to `super.transform`, so try/catch is not staged by this virtualizer (`forge/src/forge/tags/Virtualizer.scala:167-170`). A match rewrite exists only as a commented-out block, with unsupported unapply cases inside that comment (`forge/src/forge/tags/Virtualizer.scala:247-279`). The default `EmbeddedControls` hooks lower `__return` to Scala `return` and `__throw` to Scala `throw`, so HLS behavior for return-from-virtualized-blocks and throws requires DSL-specific semantics (inferred, unverified) (`forge/src/forge/EmbeddedControls.scala:48-55`; `forge/src/forge/EmbeddedControls.scala:131-149`).

`@curriedUpdate` only applies to an `update` def with three parameter lists: non-empty indices, one value, and two implicit parameters (`forge/src/forge/tags/curriedUpdate.scala:17-29`). It renames the original method to `update$r`, emits an `update(values: Any*)` dispatcher macro, and rewrites calls to `self.update$r(..inds)(value)(ctx,state)` (`forge/src/forge/tags/curriedUpdate.scala:30-58`).

`@struct` rejects empty fields and `var` fields, injects field accessors, `fields`, `copy`, `box`, companion `apply`, user methods, derives `Bits`, then runs `forge.tags.ref.implement` (`argon/src/argon/tags/Structs.scala:29-34`; `argon/src/argon/tags/Structs.scala:63-123`). `Arith` derivation code exists separately, but this `@struct` implementation wires only `new Bits` in its `typeclasses` sequence (`argon/src/argon/tags/Structs.scala:29-32`; `argon/src/argon/tags/Arith.scala:8-57`). `@streamstruct` rejects methods, type parameters, and `var` fields, extends `spatial.lang.StreamStruct`, derives both `Bits` and `Arith`, and also finishes by invoking `forge.tags.ref.implement` (`spatial/src/spatial/tags/StreamStructs.scala:31-35`; `spatial/src/spatial/tags/StreamStructs.scala:53-61`; `spatial/src/spatial/tags/StreamStructs.scala:68-102`).

## Interactions

These annotations are the compile-time source of runtime contracts used elsewhere: `@op` supplies `mirror`/`update` required by transformers, `@ref` supplies type factories required by staging, `@rewrite` and `@flow` feed the registries in `[[70 - Rewrites and Flows]]`, and `@ctx`/`@stateful` make `SrcCtx` and `State` available to staging APIs (`forge/src/forge/tags/op.scala:32-35`; `forge/src/forge/tags/ref.scala:37-48`; `forge/src/forge/tags/rewrite.scala:57-64`; `forge/src/forge/tags/flow.scala:49-53`; `forge/src/forge/tags/ctx.scala:19-23`; `forge/src/forge/tags/stateful.scala:22-29`).

## HLS notes

This area is `rework` because Scala macro annotations, `blackbox.Context`, tree pattern matching, and Scala-Virtualized-style rewrites do not translate directly to an HLS implementation (`forge/src/forge/tags/Virtualizer.scala:76-86`; `utils/src/utils/tags/MacroUtils.scala:9-24`). A replacement should preserve the generated contracts, but should explicitly define whether try/catch, match, return, and throw are supported in staged HLS code (inferred, unverified) (`forge/src/forge/tags/Virtualizer.scala:167-172`; `forge/src/forge/tags/Virtualizer.scala:247-279`).

## Open questions

- See [[open-questions-argon-supplemental#Q-arg-07]]: `@globalRewrite` has an `isInstanceOf` guard in source, contrary to the unguarded behavior summary.
- See [[open-questions-argon-supplemental#Q-arg-08]]: `@struct` wires `Bits` only, while `Arith` exists and `@streamstruct` wires both.
- See [[open-questions-argon-supplemental#Q-arg-09]]: virtualized `return` and `throw` have hooks, but HLS semantics are not defined in Forge.
