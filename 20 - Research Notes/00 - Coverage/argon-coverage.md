---
type: coverage
subsystem: Argon framework
paths:
  - "argon/src/argon/"
file_count: 95
date: 2026-04-21
verified:
  - 2026-04-21
---

## 1. Purpose

Argon is the generic staged-IR framework on which Spatial is built. It provides the universal substrate for a DSL compiler pipeline: a staged-expression representation (`Exp`/`Ref`/`Sym`), staging machinery that turns host-language Scala calls into IR nodes with effect tracking and CSE, a graph-with-metadata IR, pass and traversal infrastructure, transformer and substitution scaffolding, scheduling/code-motion, and a codegen skeleton. On top of that substrate Argon bundles a minimal DSL surface (`lang/`) supplying the shared base types (`Bit`, fixed/float, `Vec`, `Struct`, `Text`, `Tup2`, `Var`, `Series`, `Void`) and their IR nodes (`node/`). Spatial sits one layer above: `spatial/*` adds accelerator-specific nodes, metadata, analyses, transforms, and targets that extend `argon.passes.Pass`/`Traversal`, `argon.transform.Transformer`, and `argon.codegen.Codegen`. Argon itself is target-agnostic — `argon.Compiler` is the only driver, and `DSLApp`/`DSLTest` are the main entry-point traits that user apps extend.

## 2. File inventory

| path | one-line purpose |
|---|---|
| `argon/src/argon/package.scala` | Package object; exposes `Sym[A] = Exp[_,A]`, `Type[A] = ExpType[_,A]`, extends `static.Core`. |
| `argon/src/argon/Ref.scala` | Core `ExpType`/`Exp`/`Ref` traits — type evidence and staged-expression representation. |
| `argon/src/argon/Def.scala` | `Def[A,B]` sealed hierarchy (`TypeRef`, `Error`, `Bound`, `Const`, `Param`, `Node`) — what a symbol's RHS can be. |
| `argon/src/argon/Op.scala` | `Op[R]` base class (inputs/reads/binds/aliases/contains/extracts/copies/effects, `rewrite`/`mirror`/`update`); `Op2`–`Op4` arity helpers. |
| `argon/src/argon/Block.scala` | `Block[R]` with inputs/stms/result/effects/options; `Lambda1`/`Lambda2`/`Lambda3`; `nestedStms`/`nestedInputs`. |
| `argon/src/argon/BlockOptions.scala` | `BlockOptions(temp, sched)`; `Normal`, `Sealed`. |
| `argon/src/argon/Effects.scala` | `Effects` case class (unique/sticky/simple/global/mutable/throws/reads/writes/antiDeps) + `Impure` wrapper. |
| `argon/src/argon/Freq.scala` | `Freq` enum — `Cold`/`Normal`/`Hot` — for code-motion frequency hints. |
| `argon/src/argon/State.scala` | Mutable per-compilation `State`; `ScopeBundle`/`ScopeBundleRegistry`; scoping, IDs, metadata, streams, error counts. |
| `argon/src/argon/Config.scala` | `Config` (verbosity, paths, flags like `enableAtomicWrites`, `enableMutableAliases`, `max_cycles`). |
| `argon/src/argon/Compiler.scala` | `Compiler` trait — `stageApp`/`runPasses`/`runPass`, CLI parsing, pass orchestration, `==>` DSL, exception handling. |
| `argon/src/argon/DSLApp.scala` | `trait DSLApp extends Compiler` with `main = compile(args)`. |
| `argon/src/argon/DSLRunnable.scala` | Provides implicit `IR: State` for anything that stages; initializes config dirs. |
| `argon/src/argon/DSLTest.scala` | Test harness: `Backend` abstraction, compile/make/run flow, `IllegalExample`, staged `assert`/`require`. |
| `argon/src/argon/DSLTestbench.scala` | Testbench helpers `req`, `reqOp`, `reqWarn`, `checks()`. |
| `argon/src/argon/Error.scala` | Compile-time exceptions (`UnhandledException`, `EarlyStop`, `CompilerErrors`, `CompilerBugs`, `RequirementFailure`, timeouts). |
| `argon/src/argon/Issue.scala` | `Issue` trait — issues raised by one pass must be resolved by the next or become errors. |
| `argon/src/argon/Invalid.scala` | `@ref class Invalid` placeholder representing removed symbols. |
| `argon/src/argon/Data.scala` | `Data[T]` metadata base; `SetBy`/`GlobalData`/`Transfer`; `object metadata`/`object globals` accessors. |
| `argon/src/argon/Mirrorable.scala` | `Mirrorable[A]` — anything that can be mirrored through a `Transformer`. |
| `argon/src/argon/GlobalMetadata.scala` | Global per-compiler metadata map; transfer-driven invalidation before transformers. |
| `argon/src/argon/ScratchpadMetadata.scala` | Scratch per-`(Sym, Class)` metadata store used across passes. |
| `argon/src/argon/Consumers.scala` | `Consumers(users)` — reverse edges (who consumes a sym). |
| `argon/src/argon/NestedInputs.scala` | `NestedInputs(inputs)` — cached set of external inputs for a block tree. |
| `argon/src/argon/Aliases.scala` | `ShallowAliases`/`DeepAliases` metadata cases. |
| `argon/src/argon/Rewrites.scala` | `Rewrites` registry — per-class partial-function rewrite rules, plus `globals`; used by `register` during staging. |
| `argon/src/argon/Flows.scala` | `Flows` registry — ordered `@flow` PFs for dataflow analysis during staging; per-pass `save`/`restore`. |
| `argon/src/argon/Literal.scala` | `Literal`/`Const`/`Param`/`Value` extractors for pattern-matching on staged constants. |
| `argon/src/argon/Cast.scala` | `CastFunc`/`Cast2Way`/`Lifter`/`Lift` — type-conversion evidence between staged/unstaged values. |
| `argon/src/argon/Unary.scala` | `Unary[C,R]` op mixin with `unstaged` rewrite. |
| `argon/src/argon/Binary.scala` | `Binary[C,R]` op mixin with `absorber`/`identity`/`isAssociative`/`unstaged` rewrite. |
| `argon/src/argon/Comparison.scala` | `Comparison[C,R]` op mixin returning `Bit`. |
| `argon/src/argon/StagedVarLike.scala` | `StagedVarLike[A]` — staged mutable var adapter to `forge.VarLike`. |
| `argon/src/argon/static/package.scala` | Type aliases re-exported into `argon.static`. |
| `argon/src/argon/static/Core.scala` | Mixes `Casting`, `Printing`, `Scoping`, `Staging`, `Implicits` — the top-level facade the package object inherits. |
| `argon/src/argon/static/Staging.scala` | The staging engine: `stage`/`register`/`computeEffects`/`effectDependencies`/`checkAliases`/`propagateWrites`/`syms`/`exps`. |
| `argon/src/argon/static/Scoping.scala` | `stageScope`/`stageBlock`/`stageLambda{1,2,3}` — creates isolated staging scopes and calls the scheduler. |
| `argon/src/argon/static/Printing.scala` | Logging/debug/error/warn APIs, `stm`/`shortStm` rendering, stream management (`inLog`, `withGen`). |
| `argon/src/argon/static/Casting.scala` | `Cast[A,B]`-implicit machinery and infix `CastOps` (apply/saturating/unbiased/unchecked). |
| `argon/src/argon/static/Implicits.scala` | `ExpTypeMiscOps`/`ExpMiscOps` — type and symbol infix ops (`tp`/`rhs`/`name`/`ctx`/`inputs`/`effects`/`aliases`/`consumers`/`view`/`=:=`/`<:<`). |
| `argon/src/argon/passes/Pass.scala` | `Pass` trait: `run`/`execute`/`preprocess`/`process`/`postprocess` with per-pass logging and timing. |
| `argon/src/argon/passes/Traversal.scala` | `Traversal` trait extending `Pass`: `visit`/`visitBlock` and `Recurse` mode. |
| `argon/src/argon/passes/RepeatedTraversal.scala` | `RepeatableTraversal` (has a `converged` flag) and `RepeatedTraversal` wrapper running passes until fixed point. |
| `argon/src/argon/passes/IRPrinter.scala` | `IRPrinter` pass — dumps each `Sym`/`Op` with metadata and blocks. |
| `argon/src/argon/transform/Transformer.scala` | Base `Transformer` — apply-over-Product, `mirror`, `transferData[...]`, `blockToFunction{0,1,2,3}`, `removeSym`. |
| `argon/src/argon/transform/TransformerInterface.scala` | Tiny `TransformerInterface { def apply[T](x:T):T }` (break cycle with `Op`). |
| `argon/src/argon/transform/SubstTransformer.scala` | Substitution-based transformer with `subst`/`blockSubst` maps and `isolateSubst`/`excludeSubst` scopes. |
| `argon/src/argon/transform/ForwardTransformer.scala` | Forward, mirror-by-default transformer; `createSubstRule`/`visit`/`withEns`. |
| `argon/src/argon/transform/MutateTransformer.scala` | In-place-update transformer; `update`/`updateNode`; `copyMode` toggle; `Enabled` mirror/update dispatch. |
| `argon/src/argon/schedule/Scheduler.scala` | `Scheduler` trait: `summarizeScope`/`apply` computing schedules for a scope. |
| `argon/src/argon/schedule/Schedule.scala` | `Schedule[R](block, motioned, motionedImpure)` result container. |
| `argon/src/argon/schedule/SimpleScheduler.scala` | `SimpleScheduler` — linear schedule + idempotent-only DCE; the default scheduler. |
| `argon/src/argon/codegen/Codegen.scala` | `Codegen` base trait: `lang`/`ext`/`out`, `quote`/`quoteOrRemap`/`src` interpolator, `javaStyleChunk` hierarchy for large blocks. |
| `argon/src/argon/codegen/StructCodegen.scala` | `StructCodegen` — tracks encountered structs, emits data-structure prelude in `postprocess`. |
| `argon/src/argon/codegen/FileDependencies.scala` | `FileDependencies` — declares `FileDep`/`DirDep`, copies resource files alongside generated code. |
| `argon/src/argon/lang/package.scala` | `package object lang extends InternalAliases`. |
| `argon/src/argon/lang/Aliases.scala` | `InternalAliases`/`ExternalAliases`/`ShadowingAliases` — type aliases (e.g. `I32`, `U8`, `FixPt`, `FltPt`, `Arith`/`Bits`/`Num`/`Order`). |
| `argon/src/argon/lang/Top.scala` | `Top[A]` — root of all staged DSL types; `===`/`!==`/`++`/`toText`. |
| `argon/src/argon/lang/Bit.scala` | `@ref class Bit` staged Boolean; bit ops; `BitType` extractor. |
| `argon/src/argon/lang/Fix.scala` | `FixFmt[S,I,F]` and `@ref class Fix[S,I,F]` — the central fixed-point (and integer) staged type with operator overloads. |
| `argon/src/argon/lang/Flt.scala` | `FltFmt[M,E]` and `@ref class Flt[M,E]` — staged IEEE-like floating point. |
| `argon/src/argon/lang/Vec.scala` | `@ref class Vec[A]` — staged bit/value vector with `apply`/`concat`/`zip`/`reduce`. |
| `argon/src/argon/lang/Struct.scala` | `trait Struct[A]` — staged record; `SimpleStruct`/`FieldApply`/`FieldUpdate` dispatch. |
| `argon/src/argon/lang/Tup2.scala` | `@ref class Tup2[A,B]` — 2-struct with lifted Arith/Bits when components support them. |
| `argon/src/argon/lang/Text.scala` | `@ref class Text` — staged String. |
| `argon/src/argon/lang/Var.scala` | `@ref class Var[A]` — mutable staged variable (alloc/read/assign). |
| `argon/src/argon/lang/Void.scala` | `@ref class Void` — unit staged type. |
| `argon/src/argon/lang/Series.scala` | `Series[A]` — range value with `by`/`par`/`length`/`at`/`foreach` (used for counters). |
| `argon/src/argon/lang/implicits.scala` | `object implicits` mixes `api.Implicits` + `api.BitsAPI`. |
| `argon/src/argon/lang/types/{Bits,Arith,Num,Order}.scala` | Typeclass traits for `Bits`/`Arith`/`Num`/`Order` over staged values. |
| `argon/src/argon/lang/types/CustomBitWidths.scala` | `BOOL[T]` / `INT[T]` / `TRUE` / `FALSE` and numeric singletons `_0`..`_1024` used to parameterize `Fix`/`Flt`. |
| `argon/src/argon/lang/api/{package,Implicits,BitsAPI,DebuggingAPI,TuplesAPI}.scala` | User-facing implicit conversions (numeric casts, lifts), `zero`/`one`/`random`/`cat`/`popcount`, `println`/`assert`/`exit`/`breakpoint`, `pack`/`unpack`. |
| `argon/src/argon/node/DSLOp.scala` | `DSLOp[R]`/`Primitive[R]`/`EnPrimitive[R]`/`Alloc[T]` — Op categorizations used by downstream analyses. |
| `argon/src/argon/node/Enabled.scala` | `Enabled[R]` mixin: `ens: Set[Bit]`, `mirrorEn`/`updateEn` — predicated nodes. |
| `argon/src/argon/node/Bit.scala` | Bit nodes: `Not`/`And`/`Or`/`Xor`/`Xnor`/`BitRandom`/`TextToBit`/`BitToText`. |
| `argon/src/argon/node/Bits.scala` | `DataAsBits`/`BitsAsData`/`VecAsData`/`DataAsVec`/`BitsPopcount` (transient bit-view nodes). |
| `argon/src/argon/node/Fix.scala` | All fixed-point nodes (arith, shifts, comparisons, math, saturating/unbiased variants, conversions, FMA-like combos). |
| `argon/src/argon/node/Flt.scala` | All floating-point nodes (arith, comparisons, NaN tests, trig/exp/log, FMA). |
| `argon/src/argon/node/Vec.scala` | `VecAlloc`/`VecApply`/`VecSlice`/`VecConcat`/`VecReverse`. |
| `argon/src/argon/node/Struct.scala` | `StructAlloc`/`SimpleStruct`/`FieldApply`/`FieldUpdate`. |
| `argon/src/argon/node/Text.scala` | `TextConcat`/`TextEql`/`TextNeq`/`TextLength`/`TextApply`/`TextSlice`/`GenericToText`. |
| `argon/src/argon/node/Var.scala` | `VarNew`/`VarRead`/`VarAssign`. |
| `argon/src/argon/node/Series.scala` | `SeriesForeach` — iterate a `Series` with a lambda. |
| `argon/src/argon/node/IfThenElse.scala` | `IfThenElse[T](cond, thenBlk, elseBlk)`. |
| `argon/src/argon/node/Debugging.scala` | `PrintIf`/`AssertIf`/`BreakpointIf`/`ExitIf` enabled primitives with `Effects.Simple`/`Global`. |
| `argon/src/argon/tags/Bits.scala` | Macro `Bits` typeclass-derivation for `@struct` classes. |
| `argon/src/argon/tags/Arith.scala` | Macro `Arith` typeclass-derivation for `@struct` classes. |
| `argon/src/argon/tags/Structs.scala` | `@struct` annotation macro: injects field getters, `copy`, `box`, and the derived typeclass implementations. |

## 3. Key types / traits / objects

- `ExpType[C,A]` (`argon/src/argon/Ref.scala:17-107`). Staged-type evidence with constant type `C` and Scala rep `A`. Key methods: `fresh`/`_new` (creates a new symbol given a `Def` and `SrcCtx`, `argon/src/argon/Ref.scala:41-48`), `from`/`getFrom` (constant-conversion with exactness check, `argon/src/argon/Ref.scala:74-105`), `__typePrefix`/`__typeArgs`/`__typeParams` for type identity. Consumed by every staged type (`Bit`, `Fix`, etc.) and by casting.
- `Exp[C,A]` / `Ref[C,A]` (`argon/src/argon/Ref.scala:119-180`). `Exp` holds `_tp`, `_rhs: Def[C,A]`, `_data` (metadata map), `_name`, `_ctx`. `Ref` mixes in `ExpType` and supplies hashCode/equals/toString based on the `Def`.
- `Def[A,B]` (`argon/src/argon/Def.scala:5-45`). Sealed ADT: `TypeRef`, `Error(id,msg)`, `Bound(id)`, `Const(c)`, `Param(id,c)`, `Node(id,op)`. Predicates `isValue`/`isConst`/`isParam`/`isBound`/`isNode`/`isError`/`isType`.
- `Op[R]` (`argon/src/argon/Op.scala:13-109`). Every staged operation extends this. Methods the rest of the compiler relies on: `inputs`/`reads`/`freqs`/`blocks`/`binds`/`aliases`/`contains`/`extracts`/`copies`/`effects`/`rewrite`/`mirror`/`update`/`shallowAliases`/`deepAliases`/`mutableAliases`/`mutableInputs`. Specializations `Op2`/`Op3`/`Op4` just attach extra `Type` evidence. `AtomicRead[M]` is a mixin for nodes that dereference a collection sym.
- `Block[R]` (`argon/src/argon/Block.scala:6-65`) and `Lambda1/2/3` (lines 67–94). A scheduled scope with its `effects` and `options`; `nestedStms`/`nestedStmsAndInputs` walk sub-scopes.
- `Effects` (`argon/src/argon/Effects.scala:20-75`). Combinators `andAlso`/`andThen`/`orElse`/`star`; predicates `isPure`/`isIdempotent`/`mayCSE`/`mayRead`/`mayWrite`. Constants `Pure`/`Sticky`/`Unique`/`Simple`/`Global`/`Mutable`/`Throws`. `Impure(sym, effects)` wraps a sym with its effects.
- `State` (`argon/src/argon/State.scala:55-252`). Compilation-wide mutable context. Key members: `config`, `scope`/`impure`/`cache` (scoped via `ScopeBundle`), `nextId()`, `rewrites`, `flows`, `globals`, `scratchpad`, `streams`, `issues`, pass counter. Scope switching uses `withScope(handle)` / `withNewScope(motion)`.
- `Config` (`argon/src/argon/Config.scala`). Verbosity, output dirs, `enableAtomicWrites` (affects `propagateWrites` in staging), `enableMutableAliases`, `max_cycles`.
- `Compiler` (`argon/src/argon/Compiler.scala:10-317`). Orchestrates `stageProgram` then `runPasses`; provides the `==>` block-and-pass combinator (lines 205-218) and top-level `compile(args)` entry (line 307).
- `Pass` / `Traversal` / `RepeatableTraversal` / `RepeatedTraversal` (`argon/src/argon/passes/Pass.scala:14-75`, `Traversal.scala:9-50`, `RepeatedTraversal.scala:5-47`). The pass skeleton: each pass has `preprocess`/`process`/`postprocess`, logs per-pass, times, and may be gated by `shouldRun`. `RepeatedTraversal` re-runs a list of passes until all `RepeatableTraversal` children converge.
- `Codegen` / `StructCodegen` / `FileDependencies` (`argon/src/argon/codegen/*`). `Codegen` is a `Traversal` that emits to `genDir/<lang>/Main.<ext>`; overrides `visit` to call `gen(lhs,rhs)`. `src""` interpolator via `quoteOrRemap`. `javaStyleChunk` (`Codegen.scala:107-199`) splits large blocks into chunked Scala objects for backends that can't compile monolithic output.
- `Transformer` (`argon/src/argon/transform/Transformer.scala:22-235`). Defines `apply[T](x:T):T` that walks products, mirrors `Mirrorable`, substitutes `Sym`/`Block`, and recurses into collections. Handles `transferData` for metadata with `Transfer.{Mirror,Remove,Ignore}`.
- `SubstTransformer` (`argon/src/argon/transform/SubstTransformer.scala:19-177`). Adds `subst: Map[Sym[_], Substitution]` (`DirectSubst`/`FuncSubst`) and `blockSubst`; `isolateSubst`/`excludeSubst` manage scoped substitution rules. Converts `Lambda{1,2,3}` to Scala `Function{1,2,3}` via `lambda{N}ToFunction{N}`.
- `ForwardTransformer` (`argon/src/argon/transform/ForwardTransformer.scala:8-96`). `recurse = Never`; mirrors every statement by default. `createSubstRule` handles first and repeated visits; `withEns`/`enables` track enable signals.
- `MutateTransformer` (`argon/src/argon/transform/MutateTransformer.scala:8-67`). `recurse = Default`; updates nodes in place via `op.update(f)` unless `copyMode` is on. Special-cases `Enabled` for `updateEn`/`mirrorEn`.
- `Scheduler` / `Schedule` / `SimpleScheduler` (`argon/src/argon/schedule/*`). `summarizeScope` (`Scheduler.scala:14-26`) hides reads/writes of scope-internal allocations. `SimpleScheduler` (`SimpleScheduler.scala`) computes an idempotent-only DCE and returns the block as-is; it's the default (`Scoping.scala:62`).
- `metadata` (`argon/src/argon/Data.scala:88-123`) and `globals` (`Data.scala:125-132`) — generic typed metadata maps keyed by `Class[_]`. `Transfer.{Mirror,Remove,Ignore}` drives transformer behavior.
- `Rewrites` and `Flows` (`argon/src/argon/Rewrites.scala`, `Flows.scala`). Registries for per-class rewrite rules and staging-time dataflow rules, invoked from `register` in `Staging` (`argon/src/argon/static/Staging.scala:77-78, 140`).
- `Top[A]` (`argon/src/argon/lang/Top.scala`). Root of the DSL type hierarchy. Provides `===`/`!==`/`++`/`toText`.
- `Bits[A]`/`Arith[A]`/`Num[A]`/`Order[A]` (`argon/src/argon/lang/types/*`). Typeclass traits providing operations like `bit`/`msb`/`nbits`/`zero`/`one`/`random`/`add`/`mul`/`pow`/`min`/`max`.
- `Fix[S,I,F]`/`Flt[M,E]`/`Bit`/`Vec[A]`/`Struct[A]`/`Text`/`Tup2[A,B]`/`Var[A]`/`Void`/`Series[A]` — the DSL types under `lang/`.
- `@ref`, `@op`, `@api`, `@rig`, `@stateful`, `@struct` — Forge-driven macro annotations (the struct one lives in `argon/src/argon/tags/Structs.scala`). Many files rely on these to inject implicit `ctx`/`state` parameters.

## 4. Entry points

- `argon.Compiler.compile(args: Array[String])` (`argon/src/argon/Compiler.scala:307-316`) — "real" entry for every DSL app.
- `argon.DSLApp.main` (`argon/src/argon/DSLApp.scala:6`) — trait making an app object runnable.
- `argon.DSLTest` / `argon.DSLTestbench` — entry points for test flavors; define `backends`/`runtimeArgs` and exercise `compile`/`make`/`run` cycles.
- `argon.stage[R](op: Op[R])` and `stageWithFlow`/`restage` (`argon/src/argon/static/Staging.scala:172-182, 158`) — the only way to introduce a new `Node` symbol into the current scope (used via `@op` in node files and directly by DSL classes).
- `stageScope`/`stageBlock`/`stageLambda{1,2,3}` (`argon/src/argon/static/Scoping.scala:88-116`) — create a new isolated staging scope.
- `register` (`argon/src/argon/static/Staging.scala:93-153`) — the 9-step register pipeline; used by all staging paths (directly via `stage`, or indirectly via `restage`).
- `Traversal.visit`/`visitBlock` (`argon/src/argon/passes/Traversal.scala`) — override points for all analyses.
- `Transformer.apply[T](x: T)` (`argon/src/argon/transform/Transformer.scala:40-70`) — the polymorphic traversal that every downstream transformer calls as `f(...)`.
- `Codegen.emitEntry`, `Codegen.gen(lhs,rhs)`, `nameMap`/`remap`/`quoteConst` (`argon/src/argon/codegen/Codegen.scala`) — the hooks that every backend (Chisel, C++, etc.) overrides.
- `Rewrites.add[O<:Op]`/`Rewrites.addGlobal` (`argon/src/argon/Rewrites.scala:30-40`) and `Flows.add`/`prepend`/`remove` (`argon/src/argon/Flows.scala:21-34`) — runtime registration called from DSL `flows()`/`rewrites()` in `Compiler`.
- `@struct` (`argon/src/argon/tags/Structs.scala:10-12`) — used by Spatial user code to define DSL record types.

## 5. Dependencies

Upstream (Argon uses):
- `forge` (`forge.tags._`, `forge.SrcCtx`, `forge.AppState`, `forge.VarLike`, `forge.Ptr`) — macro annotations and source-context handling.
- `emul` — reference unstaged implementations (`FixedPoint`, `FloatPoint`, `Bool`, `FixFormat`, `FltFormat`, `Number`).
- `utils` — collections/terminal/IO helpers, `Instrument`, `Testbench`, `Args`, `MacroUtils`, `ReduceTree`.
- `scopt` — CLI parsing in `Compiler.defineOpts` (`argon/src/argon/Compiler.scala:178-186`).

Downstream (things under `spatial/src/` depend on Argon):
- Nearly every transform and analysis in `spatial/src/spatial/transform/` and `spatial/src/spatial/traversal/` extends `argon.transform.{ForwardTransformer,MutateTransformer,SubstTransformer}` or `argon.passes.Traversal`.
- Spatial metadata classes extend `argon.Data[T]` and use `argon.metadata`/`argon.globals`.
- Spatial IR nodes extend `argon.Op`, `argon.node.DSLOp`/`Primitive`/`EnPrimitive`/`Alloc`, and `argon.node.Enabled`.
- Backends under `spatial/src/spatial/codegen/` extend `argon.codegen.{Codegen,StructCodegen,FileDependencies}`.
- `SpatialApp` / Spatial test infrastructure extend `argon.DSLApp` / `argon.DSLTest`.
- All Spatial DSL types live under `argon.lang.*` aliases and subclass `Fix`/`Flt`/`Struct` etc.

## 6. Key algorithms

- Nine-step symbol registration (CSE + effect propagation + flow-rule pipeline) — `argon/src/argon/static/Staging.scala:93-153`. Rewrite first; then CSE if `effects.mayCSE`; otherwise new symbol, push on `state.scope`/`state.impure`, set aliases, register reverse aliases, attach consumers, run immediate + deferred flow rules, check mutable aliasing.
- Effect dependency computation — `argon/src/argon/static/Staging.scala:202-234`. Combines WAR/RAW/WAW hazard scans, simple and global deps, and anti-dep propagation via `propagateWrites`.
- Atomic-write recursion for nested mutable structures — `argon/src/argon/static/Staging.scala:245-261` (`recurseAtomicLookup`/`extractAtomicWrite`/`propagateWrites`).
- Scope-bundle scheduling model — `argon/src/argon/State.scala:14-155` and `argon/src/argon/static/Scoping.scala:56-96`. Each block gets its own `(scope, impure, cache)` bundle; `withNewScope(motion)` carries CSE cache forward only if motion is allowed.
- Simple dead-code elimination in scheduling — `argon/src/argon/schedule/SimpleScheduler.scala:22-30`. Reverse-iterate; drop idempotent symbols that are neither the block `result` nor have any used consumers (the `s != result` guard prevents the block's result symbol from being dropped).
- Effect summary for a scope — `argon/src/argon/schedule/Scheduler.scala:14-26`. Fold `andThen` across `impure`, then subtract allocation-local reads/writes.
- Transformer polymorphic mirror walk — `argon/src/argon/transform/Transformer.scala:40-70`. Uses `Mirrorable`/`Sym`/`Block`/`Lambda{1,2,3}`/`Product`/collection dispatch; the `Invalid` check throws `usedRemovedSymbol` on dangling references.
- Metadata transfer policy — `argon/src/argon/transform/Transformer.scala:99-134` and `argon/src/argon/Data.scala:36-61`. `Transfer.Mirror` copies via `m.mirror(f)`; `Transfer.Remove` drops on transform; `Transfer.Ignore` leaves alone.
- Substitution-scope isolation — `argon/src/argon/transform/SubstTransformer.scala:82-136`. `isolateSubst`/`isolateSubstWith`/`excludeSubst` implement stack-like semantics without actual stack allocation; used everywhere block inlining happens.
- Hierarchical chunked codegen — `argon/src/argon/codegen/Codegen.scala:107-199`. `javaStyleChunk` splits giant blocks into 1- or 2-level nested `Block{ID}Chunker{ID}` objects to keep backend Scala files under compiler limits.
- Rewrite-rule dispatch — `argon/src/argon/Rewrites.scala:42-59`. Per-class rules first, then global rules; each returns an `Option[A]` that staging substitutes when present.
- Flow-rule dispatch during staging — `argon/src/argon/Flows.scala:36-41`. Ordered partial functions applied in registration order.
- Node-level algebraic rewrites — e.g. `FixAdd` ("x - b + b = x", reassociation of constant `Add`/`Sub`) at `argon/src/argon/node/Fix.scala:65-84`; `FixMul` power-of-two to `FixSLA` at `argon/src/argon/node/Fix.scala:117-120`. `VarRead` rewrite: look backward through `state.impure` for the most recent matching `VarAssign` (`argon/src/argon/node/Var.scala:22-36`). `BitsAsData(Const(FixedPoint))` → constant-fold bits (`argon/src/argon/node/Bits.scala:31-45`).

## 7. Invariants / IR state read or written

Metadata consumed/produced by Argon core:
- `Effects` — attached to every symbol via `sym.effects`; computed at stage-time (`Staging.scala:109-150`). `Effects` is `Transfer.Ignore` so it is always kept.
- `Consumers(users)` — set by `register` via `in.consumers += sym` (`Staging.scala:132`). `SetBy.Flow.Consumer` so it is dropped during transforms.
- `ShallowAliases(aliases)` / `DeepAliases(aliases)` — set during `register` (`Staging.scala:127-129`). Transfer is `Ignore`.
- `NestedInputs(inputs)` — cached on demand by `expOps.nestedInputs` (`static/Implicits.scala:143-151`). `Transfer.Remove`.
- `_tp` / `_rhs` / `_name` / `_ctx` / `_prevNames` / `_data` are raw fields on every `Exp` (`Ref.scala:123-130`).
- Symbol IDs are monotonically issued from `State.nextId()` (`State.scala:72-74`). They underpin equals/hashCode for `Ref` (`Ref.scala:148-170`) and sorting of statements.
- Rewrite invariants: rewrite functions return a sym of subtype of the requested `Type[A]` (`Rewrites.scala:42-48`); otherwise the rule is considered a no-match.

Invariants assumed:
- "Only constant declarations are allowed in the global namespace" — `Staging.scala:97-101` enforces staging only inside a bundle.
- Bound symbols cannot be used as productIterator inputs and must be introduced via `boundVar` (`Staging.scala:26-27`).
- `Block` equality compares inputs/result/effects/options; schedulers must return a block whose result equals the original.
- Any node tagged `Effects.mayCSE` is eligible for CSE against `state.cache`.
- For `@struct` classes: one constructor args list is the fields, the second is implicits (`tags/Structs.scala:44-56`).

State written:
- `State.scope`/`State.impure`/`State.cache` — mutated during `register`/`restage`.
- `State.pass` — incremented inside `Pass.run` (`Pass.scala:41`).
- `State.issues`/`State.errors`/`State.warnings`/`State.bugs`/`State.infos` — accumulated by `error`/`warn`/`bug` in `Printing` (`static/Printing.scala:43-95`).
- `State.logTab` and stream maps — mutated by `indent`/`open`/`close`/`inLog`/`withGen`.

## 8. Notable complexities or surprises

- `Exp` is sealed only structurally: `_tp` and `_rhs` are mutable `var`s assigned during `ExpType._new` (`Ref.scala:42-48`). This means every staged value is in a half-initialized state momentarily during construction; the `tp` getter has an explicit null guard that recommends making `val tp` lazy (`static/Implicits.scala:85-95`). TODO-worthy for Phase 2: understand how this interacts with the `@ref` macro.
- `ScopeBundle`/`ScopeBundleRegistry` in `State.scala:9-53` carries an explicit `TODO(stanfurd): Replace these with weakreferences so that we don't cause a memory leak.` Bundles are never garbage-collected while the compiler runs.
- `State.withScope(handle)` stacks bundles using save/restore but relies on `setBundle`/`clearBundle` assertions (`State.scala:92-138`); misuse will trip the asserts. Relevant when transformers or analyses juggle scopes.
- `register`'s rewrite step (`Staging.scala:102-104`) fires before CSE and flow rules, so rewrites have no access to effects/aliases — surprising when writing a rule that wants to inspect them. Deep-dive should map this carefully.
- Atomic-write semantics are toggled by `config.enableAtomicWrites` (`Staging.scala:253-260`) and `enableMutableAliases` (`Staging.scala:52`). Changing these subtly alters hazard detection.
- `Transformer.apply` walks Products reflectively — `mirrorProduct` relies on case classes having no implicit parameters, otherwise constructor lookup will reject (`Transformer.scala:163-178`). `@op` annotation is the contract: without it, `mirror` throws (`Op.scala:73-74`).
- `Transformer.apply` throws `usedRemovedSymbol` if the substitution result is `Invalid` (`Transformer.scala:68`); removed symbols surviving past their replacement point is a persistent class of bug.
- `ForwardTransformer.createSubstRule` has a comment (`ForwardTransformer.scala:36-51`) flagging the "pre-transformed case" where CSE across scopes or outer-scope pre-transforms must be handled by mirroring once more. This is non-obvious and error-prone — a good Phase-2 target.
- `MutateTransformer` overrides `blockToFunction0` to force `copyMode = true` inside lambda inlining (`MutateTransformer.scala:36-40`). This asymmetry between update-in-place and copy-on-inline is easy to forget.
- `SimpleScheduler`'s DCE is "idempotent only" (`SimpleScheduler.scala:25`). Anything that throws or modifies global state remains, even if unused. The default `SimpleScheduler` is picked inside `stageScope_Start` with a conspicuous `if (state.mayMotion) SimpleScheduler else SimpleScheduler` ternary (`Scoping.scala:62`) — both branches identical. Surprise/bug-smell: deep-dive whether motion support was intentionally no-op.
- `Codegen.javaStyleChunk` (`Codegen.scala:107-199`) contains explicit TODO(s) about higher-depth hierarchies and speed. It imposes odd naming constraints (`Block{ID}Chunker{ID}`) that downstream backends must honor.
- `VarRead.rewrite` scans `state.impure` for a matching `VarAssign` (`node/Var.scala:22-36`). Comment explicitly says "this assumes that all statements in a block are always executed" — violation in the presence of `IfThenElse` would be a correctness bug.
- `Freq.combine` (`Freq.scala:7-13`) is not associative-with-the-expected-distribution: `(Cold, Hot) → Cold`, `(Hot, Cold) → Cold`. This is intentional but surprising when combining frequencies across multiple scopes.
- The `@struct` macro in `tags/Structs.scala:44-56` complains only if `constructorArgs.size > 2`; some hand-written DSL classes define more implicit blocks and must route through the secondary list.
- `DSLTest.Backend.compile` uses blocking `Future`s with `Await.result` and `makeTimeout` (`DSLTest.scala:134-165`). Indirect dependence on `scala.concurrent.ExecutionContext.Implicits.global`.
- `Config.reset` (`Config.scala:75-81`) resets only verbosity; other fields survive across compilations, which is called out as a `TODO[2]` in `DSLRunnable.scala:8`.
- Global metadata stability: `Transformer.preprocess` calls `globals.invalidateBeforeTransform()` (`Transformer.scala:229-233`) which drops any `GlobalData.Flow` / `GlobalData.Analysis` entries. Transformer authors relying on global metadata surviving across passes must mark it `SetBy` carefully.
- `checkAliases` special-cases `sym` out of the alias set (`Staging.scala:39-75`). Without the `enableMutableAliases` config flag, violations produce errors, not warnings — this can be surprising when porting code.

## 9. Open questions

- What is the precise contract between `@op`-generated `mirror`/`update` and `Transformer.mirrorProduct`'s reflective constructor fallback? How are implicits-in-constructor case classes handled?
- Why does `stageScope_Start` pick `SimpleScheduler` in both branches of the motion conditional (`Scoping.scala:62`)? Was an alternate motion scheduler removed or never merged?
- `Rewrites.apply` rejects results whose `tp` does not subtype the requested type (`Rewrites.scala:44-47`); are there rules in Spatial that silently fail because of this?
- `ScopeBundleRegistry` leaks bundles — what pathways prevent this from becoming fatal in long compile jobs or tests?
- `globals.invalidateBeforeTransform` is called once per `Transformer.preprocess`; are there transform sequences (nested substituteBlock?) where it should re-run?
- How does `recurseAtomicLookup` interact with mutable structs whose `AtomicRead` chain forms cycles? (The code uses `syms(...).headOption`, which hides multi-alias cases silently.)
- `MutateTransformer.copyMode` vs `ForwardTransformer.enables` — do they interact cleanly when a pass mixes both?
- `DSLTest`'s `genDir`/`logDir`/`repDir` per-backend layout vs. `Compiler.init`'s suffixing logic (`Compiler.scala:190-192`). Does it double-prefix under certain CLI invocations?
- The `CaptureStream` / `withOut` pair in `DSLTestbench.reqWarn` captures stdout only; does asynchronous Future logging ever race with this?
- `@struct` macro parent handling: the file contains `TODO[5]: What to do if class has parents? Error?` (`tags/Structs.scala:60-61`) — Spatial almost certainly has user `@struct` classes that extend traits; behavior is unclear.

## 10. Suggested spec sections

Mapping into the planned `10 - Spec/` tree:

- `10 - Spec/IR/01 - Symbols and Types.md` — `Exp`/`Ref`/`ExpType`, `Def` ADT, sym-id semantics, equals/hashCode rules.
- `10 - Spec/IR/02 - Ops and Blocks.md` — `Op` base (inputs/reads/binds/aliases/contains/extracts/copies/effects), `Block`/`Lambda`, `BlockOptions`.
- `10 - Spec/IR/03 - Effects and Aliasing.md` — `Effects` composition, `Impure`, alias propagation, mutable-alias checks.
- `10 - Spec/IR/04 - Metadata Model.md` — `Data[T]`, `SetBy`/`Transfer`, `metadata`/`globals`/`scratchpad`, `Consumers`/`ShallowAliases`/`DeepAliases`/`NestedInputs`.
- `10 - Spec/Staging/01 - The Staging Pipeline.md` — `register` and its 9 steps; `stage`/`restage`; rewrite vs. CSE vs. flow rules.
- `10 - Spec/Staging/02 - Scopes and Scheduling.md` — `ScopeBundle`/`ScopeBundleRegistry`; `stageScope`/`stageBlock`/`stageLambda`; `Scheduler`/`SimpleScheduler`; effect-driven scheduling.
- `10 - Spec/Staging/03 - Atomic Writes and Aliasing.md` — `recurseAtomicLookup`, `propagateWrites`, `checkAliases`.
- `10 - Spec/Passes/01 - Pass Infrastructure.md` — `Pass`/`Traversal`/`RepeatableTraversal`/`RepeatedTraversal`; logging and timing.
- `10 - Spec/Passes/02 - IRPrinter.md` — debug-dump formatting.
- `10 - Spec/Transforms/01 - Transformer Base.md` — `Transformer.apply` dispatch, metadata transfer policy, `mirror`/`mirrorProduct`/`mirrorMirrorable`.
- `10 - Spec/Transforms/02 - Substitution Transformers.md` — `SubstTransformer`, `isolateSubst`, `excludeSubst`, block-to-function conversion.
- `10 - Spec/Transforms/03 - Forward and Mutate Transformers.md` — `ForwardTransformer.createSubstRule`, `MutateTransformer.update`/`copyMode`, `Enabled` mirror/update.
- `10 - Spec/Codegen/01 - Codegen Base.md` — `Codegen`, `quote`/`quoteOrRemap`/`src""`, `emitEntry`/`emitHeader`/`emitFooter`, `javaStyleChunk` hierarchical split.
- `10 - Spec/Codegen/02 - Codegen Mixins.md` — `StructCodegen`, `FileDependencies`.
- `10 - Spec/Compiler/01 - Compiler Driver.md` — `Compiler.compile`/`runPasses`/`runPass`, CLI options, directives, exception handling.
- `10 - Spec/Compiler/02 - DSLApp, DSLTest, Backends.md` — `DSLApp`, `DSLRunnable`, `DSLTest.Backend`, `IllegalExample`.
- `10 - Spec/Compiler/03 - Rewrites and Flows.md` — `Rewrites`/`Flows` registries and their use in staging.
- `10 - Spec/DSL/01 - Shared Type Hierarchy.md` — `Top`, `Bits`/`Arith`/`Num`/`Order`, `Bit`/`Fix`/`Flt`/`Vec`/`Struct`/`Text`/`Tup2`/`Var`/`Void`/`Series` and their aliases.
- `10 - Spec/DSL/02 - Node Library.md` — `DSLOp`/`Primitive`/`EnPrimitive`/`Alloc`/`Enabled`, arithmetic/bit/Text/Var/Struct/Vec/IfThenElse/Debugging nodes.
- `10 - Spec/DSL/03 - Casting and Lifting.md` — `Cast`/`Cast2Way`/`Lifter`/`Lift`, numeric-cast implicits.
- `10 - Spec/DSL/04 - Macro Annotations.md` — `@struct`, `@ref`, `@op`, `@api`, `@rig`, `@stateful`, and the `Bits`/`Arith` typeclass-derivation macros.
