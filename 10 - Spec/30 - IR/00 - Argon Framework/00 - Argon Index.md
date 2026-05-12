---
type: moc
project: spatial-spec
date_started: 2026-04-23
---

# Argon Framework — Index

Generic staged-IR substrate on which Spatial is built. Target-agnostic. Lives in `argon/src/argon/`.

## Sections

- `10 - Symbols and Types.md` — `Exp`/`Ref`/`ExpType`, the `Def[A,B]` ADT (`TypeRef`/`Error`/`Bound`/`Const`/`Param`/`Node`), sym-id semantics, equals/hashCode rules.
- `20 - Ops and Blocks.md` — `Op` base trait (inputs/reads/binds/aliases/contains/extracts/copies/effects/rewrite/mirror/update), arity helpers `Op2`/`Op3`/`Op4`, `AtomicRead` mixin, `Block`/`Lambda{1,2,3}`, `BlockOptions`.
- `30 - Effects and Aliasing.md` — `Effects` lattice (`Pure`/`Sticky`/`Unique`/`Simple`/`Global`/`Mutable`/`Throws`), `Impure` wrapper, `ShallowAliases`/`DeepAliases`/`NestedInputs`, atomic-write propagation, mutable-alias checks.
- `40 - Metadata Model.md` — `Data[T]` base, `SetBy`/`Transfer`, `metadata`/`globals`/`scratchpad` maps, `Consumers`, `Mirrorable`.
- `50 - Staging Pipeline.md` — the 9-step `register` algorithm (rewrite → CSE → new sym → scope push → aliases → reverse aliases → consumers → flow rules → mutable-alias check); `stage`/`restage`/`stageWithFlow`.
- `60 - Scopes and Scheduling.md` — `State`, `ScopeBundle`/`ScopeBundleRegistry`, `stageScope`/`stageBlock`/`stageLambda{1,2,3}`, `Scheduler`/`Schedule`/`SimpleScheduler`, effect summarization.
- `70 - Rewrites and Flows.md` — `Rewrites` per-class + global registry, `Flows` ordered partial functions.
- `80 - Passes.md` — `Pass`/`Traversal`/`RepeatableTraversal`/`RepeatedTraversal`, `IRPrinter`.
- `90 - Transformers.md` — `Transformer` base (apply, mirror, mirrorProduct, `transferData`), `SubstTransformer` (subst/isolateSubst), `ForwardTransformer`, `MutateTransformer`.
- `A0 - Codegen Skeleton.md` — `Codegen`, `src""` interpolator, `javaStyleChunk` hierarchical chunking, `StructCodegen`, `FileDependencies`.
- `B0 - Compiler Driver.md` — `Compiler` trait, `stageApp`/`runPasses`/`runPass`, CLI parsing, `==>` combinator, exception handling, `DSLApp`, `DSLRunnable`, `DSLTest`.
- `C0 - Macro Annotations.md` — `@ref`, `@op`, `@api`, `@rig`, `@stateful`, `@struct`, `@virtualize`, `@flow`, `@rewrite` (definitions in `forge/`, consumers under Argon).
- `D0 - DSL Base Types.md` — `Top`, `Bits`/`Arith`/`Num`/`Order` typeclasses, the base DSL types `Bit`/`Fix[S,I,F]`/`Flt[M,E]`/`Vec`/`Struct`/`Text`/`Tup2`/`Var`/`Void`/`Series` and their aliases.

## Source

- `argon/src/argon/` (95 files)
- [[argon-coverage]] — Phase 1 coverage note, verified 2026-04-21
