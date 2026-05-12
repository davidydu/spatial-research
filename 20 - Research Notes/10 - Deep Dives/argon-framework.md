---
type: deep-dive
topic: argon-framework
source_files:
  - "argon/src/argon/Ref.scala"
  - "argon/src/argon/Def.scala"
  - "argon/src/argon/Op.scala"
  - "argon/src/argon/Block.scala"
  - "argon/src/argon/BlockOptions.scala"
  - "argon/src/argon/Effects.scala"
  - "argon/src/argon/Freq.scala"
  - "argon/src/argon/State.scala"
  - "argon/src/argon/Data.scala"
  - "argon/src/argon/Mirrorable.scala"
  - "argon/src/argon/Consumers.scala"
  - "argon/src/argon/Aliases.scala"
  - "argon/src/argon/NestedInputs.scala"
  - "argon/src/argon/Rewrites.scala"
  - "argon/src/argon/Flows.scala"
  - "argon/src/argon/Config.scala"
  - "argon/src/argon/GlobalMetadata.scala"
  - "argon/src/argon/Invalid.scala"
  - "argon/src/argon/package.scala"
  - "argon/src/argon/static/Staging.scala"
  - "argon/src/argon/static/Scoping.scala"
  - "argon/src/argon/static/Implicits.scala"
  - "argon/src/argon/schedule/Scheduler.scala"
  - "argon/src/argon/schedule/SimpleScheduler.scala"
  - "argon/src/argon/schedule/Schedule.scala"
  - "argon/src/argon/transform/Transformer.scala"
  - "argon/src/argon/transform/SubstTransformer.scala"
  - "argon/src/argon/transform/ForwardTransformer.scala"
  - "argon/src/argon/transform/MutateTransformer.scala"
  - "argon/src/argon/transform/TransformerInterface.scala"
  - "argon/src/argon/node/DSLOp.scala"
  - "argon/src/argon/node/Enabled.scala"
  - "argon/src/argon/node/Var.scala"
session: 2026-04-23
status: ready-to-distill
feeds_spec:
  - "[[10 - Symbols and Types]]"
  - "[[20 - Ops and Blocks]]"
  - "[[30 - Effects and Aliasing]]"
  - "[[50 - Staging Pipeline]]"
  - "[[60 - Scopes and Scheduling]]"
  - "[[90 - Transformers]]"
---

# Argon Framework — Deep Dive

## Reading log

Read in the following order (all paths relative to `argon/src/argon/`):

1. `Ref.scala` — the base of the type/expression hierarchy. Three traits: `ExpType[C,A]` (type evidence, `Ref.scala:17-107`), `Exp[C,A]` (expression carrier, `Ref.scala:119-137`), `Ref[C,A]` (mixes both, adds equality, `Ref.scala:145-180`).
2. `Def.scala` — the sealed ADT for a symbol's right-hand side. Six cases (`TypeRef`, `Error`, `Bound`, `Const`, `Param`, `Node`) at `Def.scala:19-42`.
3. `Op.scala` — the `Op[R]` base class (`Op.scala:13-109`) and the arity helpers `Op2`/`Op3`/`Op4` (`Op.scala:111-113`), plus the `AtomicRead` mixin (`Op.scala:115-117`).
4. `Block.scala` — `Block[R]` (`Block.scala:6-65`) and the sealed lambda subclasses `Lambda1/2/3` (`Block.scala:67-94`).
5. `BlockOptions.scala` — carrier for block `temp`/`sched` overrides, with `Normal`/`Sealed` presets (`BlockOptions.scala:5-12`).
6. `Effects.scala` — the seven-field `Effects` case class (`Effects.scala:20-75`) and the `Impure` wrapper (`Effects.scala:90-96`).
7. `Freq.scala` — the three-valued enum used for code-motion hints (`Freq.scala:3-14`).
8. `State.scala` — the compilation context. `BundleHandle` / `ScopeBundle` / `ScopeBundleRegistry` (`State.scala:9-53`), the `State` class itself (`State.scala:55-252`).
9. `Data.scala` — `SetBy`/`GlobalData`/`Transfer` enumerations + the `Data[T]` base class + the `metadata`/`globals` accessors.
10. `Consumers.scala` / `Aliases.scala` / `NestedInputs.scala` — thin case-class `Data` subclasses.
11. `Rewrites.scala` / `Flows.scala` — per-compilation registries for stage-time rewrite and flow rules.
12. `static/Staging.scala` — the real workhorse. The 9-step `register` algorithm (`Staging.scala:93-153`), `stage`/`restage`/`stageWithFlow`, effect dependency computation, atomic-write plumbing.
13. `static/Scoping.scala` — `stageScope`, `stageBlock`, `stageLambda{1,2,3}`, scheduler integration (`Scoping.scala:16-117`).
14. `static/Implicits.scala` — the infix ops on `Sym`/`ExpType` (`Implicits.scala:36-184`).
15. `schedule/Scheduler.scala` / `SimpleScheduler.scala` / `Schedule.scala` — scheduler contract and the default implementation.
16. `transform/Transformer.scala` / `SubstTransformer.scala` / `ForwardTransformer.scala` / `MutateTransformer.scala` / `TransformerInterface.scala` — the full transformer stack.
17. Supporting files read for cross-reference: `Config.scala`, `Invalid.scala`, `GlobalMetadata.scala`, `package.scala`, `node/DSLOp.scala`, `node/Enabled.scala`, `node/Var.scala` (for the `VarRead.rewrite` example).

## Observations

### Staged values are half-initialized during construction

Every `Exp[C,A]` is a thin wrapper around five `var`s — `_tp`, `_rhs`, `_data`, `_name`, `_ctx`, `_prevNames` (`Ref.scala:123-130`). `ExpType._new` (`Ref.scala:42-48`) constructs a raw value via `fresh`, then writes `tp`/`rhs`/`ctx` onto it after the fact. Between `fresh` and the three field writes, the object is live but `_tp` and `_rhs` are `null`. The `tp`/`rhs` getters in `Implicits.scala:84-95` explicitly guard against the null-tp case and throw "Val references to tp in ${exp.getClass} should be lazy" — a strong hint that user-defined `@ref` classes must lazily evaluate any type-dependent fields.

### Six-case `Def` ADT, each with two different ID regimes

`Def[A,B]` (`Def.scala:5-45`) has six cases: `TypeRef` (singleton, `Def.scala:19-21`), `Error(id, msg)` (`Def.scala:22-24`), `Bound(id)` (`Def.scala:25-28`), `Const(c)` (`Def.scala:29-32`), `Param(id, c)` (`Def.scala:33-37`), `Node(id, op)` (`Def.scala:38-42`). The crucial observation is that only four of these carry an ID (`Error`, `Bound`, `Param`, `Node`); `TypeRef` and `Const` do not. Consequently, `Ref.hashCode` (`Ref.scala:148-155`) hashes by value for `Const` (using `c.hashCode()`), by ID for `Param`/`Node`/`Bound`/`Error`, and by `(_typePrefix, _typeArgs)` for `TypeRef`. Equality follows the same partition (`Ref.scala:159-170`).

IDs are monotonically issued from the global counter `State.nextId()` (`State.scala:72-74`) which starts at `-1` and increments on each call. Calls to `nextId` happen inside `_param` (`Staging.scala:20-21`), `err`/`err_` (`Staging.scala:23-24`), `boundVar` (`Staging.scala:26`), and `symbol` (`Staging.scala:28-32`). `Const` does NOT go through `nextId` — this is how CSE becomes useful: two `Const(c)` with the same `c` and the same `tp` compare equal.

### `Op` has eight default "category" computations

On `Op[R]` (`Op.scala:13-109`) every subclass inherits nine computed sets — but three are a no-op default:

- `inputs` (dataflow deps, default `syms(productIterator).toSeq`, `Op.scala:26`)
- `reads` (symbols dereferenced, default `= inputs`, `Op.scala:30`)
- `freqs` (code-motion hints, default from `blocks`, `Op.scala:35`)
- `blocks` (scopes, default from `collectBlocks(productIterator)`, `Op.scala:39`)
- `binds` (symbols bound, default from block anti-deps, `Op.scala:46`)
- `aliases` (default: same-type inputs, `Op.scala:52`)
- `contains` (default empty, `Op.scala:57`)
- `extracts` (default empty, `Op.scala:62`)
- `copies` (default empty, `Op.scala:67`)

The four `{contains, extracts, copies}` defaults are empty, making their override a conservative choice — most nodes omit them. But `aliases` defaults to the non-trivial set of same-type inputs: a plain `Primitive[A]` with `A`-typed inputs will silently report them as aliases. `VarNew` explicitly overrides `aliases = Nul` (`node/Var.scala:9`) for that reason.

The derived methods are `aliasSyms`/`containSyms`/`extractSyms`/`copySyms` which filter out primitive (never-mutable) types via `noPrims` (`Op.scala:106`), and `shallowAliases`/`deepAliases`/`allAliases`/`mutableAliases`/`mutableInputs` (`Op.scala:85-104`) compose them. `deepAliases` is the interesting one: it unions `aliasSyms ∪ copySyms ∪ containSyms ∪ extractSyms` but pulls `deepAliases` from each, except for `containSyms` which pulls `allAliases`. The asymmetry reflects the different containment semantics: "y contains x" means x is reachable deep from y, so y's deep aliases include everything x aliases, shallow or deep.

### Block equality compares inputs+result+effects+options, not statements

`Block.equals` (`Block.scala:43-48`) checks `result`, `effects`, `inputs`, `options`. The statement list `stms` is deliberately excluded. This means two scheduler runs producing different schedules but the same result/effects are equal blocks. `Block.hashCode` matches (`Block.scala:42`). This has implications for `blockSubst` in `SubstTransformer`: two semantically-equivalent schedules will collide in the `blockSubst` map.

### Effects has semi-lattice structure but `andAlso`/`andThen`/`orElse` differ only in mutable

All three combinators call `combine(that, m1, m2)` with different `m1/m2` flags (`Effects.scala:32-44`):

- `andAlso(that) = combine(m1=true, m2=true)` — both retain `mutable`
- `andThen(that) = combine(m1=false, m2=true)` — only the right side retains `mutable`
- `orElse(that)  = combine(m1=false, m2=false)` — neither retains `mutable`

All six boolean fields (`unique`/`sticky`/`simple`/`global`/`throws`) are OR'd regardless. `reads` and `writes` are unioned regardless. So the three combinators' only behavioral difference is in the `mutable` field — which represents "allocates a mutable structure". The semantics: if we sequence `andThen`, the right-hand-side op follows the left and can preserve its own allocation status; the left's allocation status is "absorbed" since we no longer need it. `andAlso` is for parallel composition (both allocations must be preserved). `orElse` is for merging (neither side's allocation is authoritative). There is also `star` (`Effects.scala:45`) which is "`Pure orElse this`": drops mutability. This matches the behavior described in `Scheduler.summarizeScope` which folds `andThen` across impure statements.

### `register`: rewrite fires BEFORE effects are computed

The ordering inside `register` (`Staging.scala:93-153`) is:

1. Validity check (`state != null`, etc.) at `Staging.scala:94-101`.
2. **Rewrite** (`rewrite(op)`) at `Staging.scala:103`. If a rule fires, the subgraph is returned directly — we do NOT proceed to the rest of the steps.
3. `sAliases = op.shallowAliases` / `dAliases = op.deepAliases` at `Staging.scala:106-107`.
4. `computeEffects(op)` at `Staging.scala:109`, which itself computes `propagateWrites(d.effects) andAlso Effects.Reads(d.mutableInputs)` then attaches `antiDeps` via `effectDependencies` (`Staging.scala:230-234`).
5. CSE check: `state.cache.get(op).filter{s => mayCSE && s.effects == effects}` at `Staging.scala:113`.
6. If cache miss: create symbol (`symbol()` at `Staging.scala:117`), box it (`Staging.scala:118`), push onto scope at `Staging.scala:121`, add to CSE cache (`Staging.scala:122`), add to impure list if impure (`Staging.scala:125`), set effects/aliases (`Staging.scala:126-128`), register reverse aliases (`Staging.scala:129`), set consumers (`Staging.scala:132`), run immediate flow (`Staging.scala:136`), run registered `@flow` PFs (`Staging.scala:140`), check mutable aliases (`Staging.scala:148`).

Key observation: the rewrite step runs first, with no access to the `effects` or `aliases` of the op. A rewrite rule that wants to inspect aliasing cannot do so — the sym doesn't exist yet. This is intentional: rewrites are "syntactic" rules. The example in `VarRead.rewrite` (`node/Var.scala:22-36`) gets around this by looking at `state.impure`, not at the would-be sym's effects.

### Aliasing: eight sets, three of them recursive

The alias computation involves three levels:

- Per-op: `aliases`/`contains`/`extracts`/`copies` (set of immediate input syms).
- Per-op derived: `aliasSyms`/etc. = `noPrims(aliases)` etc. (primitives filtered out at `Op.scala:80-83, 106`).
- Recursive: `shallowAliases`/`deepAliases`/`allAliases`/`mutableAliases`/`mutableInputs` (`Op.scala:85-104`).

The recursion is broken by looking up `sym.shallowAliases` and `sym.deepAliases` from metadata (`Implicits.scala:160-167`). These metadata get SET in `register` step 5 (`Staging.scala:127-128`). So `shallowAliases`/`deepAliases` metadata for a new sym depends on the already-computed metadata of its inputs.

Reverse-alias registration is at `Staging.scala:129`: `sym.allAliases.foreach{alias => alias.shallowAliases += sym}`. This means after staging, for any alias relation x→y, both y's alias set contains x and x's alias set contains y. This is what lets `checkAliases` (`Staging.scala:39-75`) test `sym.mutableAliases` (the transitive closure) against `effects.writes`.

### `checkAliases`: two distinct errors, one flag

`checkAliases` (`Staging.scala:39-75`) raises two error classes:

1. **Mutable aliasing**: if `(sym.mutableAliases diff effects.writes) diff Set(sym)` is non-empty, the sym has ≥2 mutable aliases that aren't being simultaneously written. Gated by `config.enableMutableAliases` (`Staging.scala:52`): if the flag is TRUE, we silently allow; if FALSE, we emit an error.
2. **Mutation of immutable**: if `effects.writes.filterNot(_.isMutable)` is non-empty, we're writing a sym whose `effects.mutable` flag is false. Always emits an error.

Note the subtraction `sym.mutableAliases diff effects.writes`: if this op is itself writing the alias, we don't complain.

### `propagateWrites` and atomic-writes: one toggle, two behaviors

`propagateWrites` (`Staging.scala:252-261`) is gated by `config.enableAtomicWrites`:

- **false**: `effects.copy(writes = writes.flatMap{s => s.allAliases})`. Every write propagates to all its aliases — conservative but dumb.
- **true**: `effects.copy(writes = writes.flatMap{s => extractAtomicWrite(s).allAliases})`. For each written sym, walk the `AtomicRead` chain (`recurseAtomicLookup`, `Staging.scala:245-247`) to the outermost mutable object, then propagate its aliases.

`extractAtomicWrite(s)` (`Staging.scala:248-250`) takes the atomic-read chain's head via `syms(recurseAtomicLookup(s)).headOption.getOrElse(s)`. `recurseAtomicLookup` recurses on `d.coll` if `d: AtomicRead[_]`, else returns `e`. Note the misnomer — "recurse" is misleading; it's one level only. (If the `AtomicRead[_].coll` is itself a node whose op is an `AtomicRead`, a second call to `recurseAtomicLookup` on that new sym would be needed, but `recurseAtomicLookup` stops after one level.)

### Scope bundles: the global bundle registry leaks

`ScopeBundleRegistry` (`State.scala:23-53`) is a `Map[BundleHandle, ScopeBundle]` that grows monotonically. A comment at `State.scala:24` acknowledges the issue: "`TODO(stanfurd): Replace these with weakreferences so that we don't cause a memory leak.`" Each call to `CreateNewBundle` (`State.scala:33-38`) allocates a new bundle and never frees it, even after the bundle's scope has been popped. For long compilations (e.g., Spatial's test suite) this could be a significant memory footprint.

`State.withScope` (`State.scala:124-138`) saves the current bundle, clears it (asserting it was non-null — `State.scala:94`), sets the new bundle (asserting the slot is empty — `State.scala:101`), runs the block, clears again, and restores the saved bundle. Two assertions guard correctness. `State.withNewScope` (`State.scala:140-146`) creates a fresh bundle; if `motion=true` it carries the outer CSE cache forward, otherwise it starts with `Map.empty` (so CSE does not cross scope boundaries unless motion is permitted).

### SimpleScheduler DCE has the `s != result` guard; "motion" ternary is a no-op

`SimpleScheduler.apply` (`SimpleScheduler.scala:10-31`) walks the scope in reverse, adding symbols to an `unused` set when they meet three conditions (`SimpleScheduler.scala:23-26`): (1) `s != result` (the block's result sym is protected), (2) their consumer set minus already-dropped syms is empty, (3) `s.effects.isIdempotent` (only pure-ish statements can be dropped), gated on `enableDCE`. The filter at `SimpleScheduler.scala:27` keeps only syms not in `unused`. This is strict idempotent-only DCE: no speculative or effect-preserving optimization.

`Scoping.scala:62` contains a conspicuous ternary: `lazy val defaultSched = if (state.mayMotion) SimpleScheduler else SimpleScheduler`. Both branches are identical. At some past point there must have been a "motion-capable scheduler" that this branch chose, but it is gone now. The result is that `defaultSched` is always `SimpleScheduler` regardless of `state.mayMotion`. Code motion itself is still performed when `motion=true` via `stageScope_Schedule` (`Scoping.scala:27-30`) appending `schedule.motioned`/`schedule.motionedImpure` to the outer scope — but `SimpleScheduler` always returns `Schedule(block, Nil)` (no motioned syms, `SimpleScheduler.scala:30`). So motion is effectively a no-op with the default scheduler.

### Transformer.apply: reflective walk, with two throws

`Transformer.apply[T]` (`Transformer.scala:40-70`) dispatches on `x` with 14 cases:

1. `Mirrorable[_]` → `mirrorMirrorable` (`Transformer.scala:42`).
2. `Sym[_]` → `substituteSym` (subclass-defined, `Transformer.scala:43, 73`).
3. `Lambda1/2/3[_]` → `substituteBlock(x).asLambda{1,2,3}` (`Transformer.scala:44-46`).
4. `Block[_]` → `substituteBlock` (`Transformer.scala:47`).
5. `Option[_]` / `Seq[_]` / `Map[_,_]` / `mutable.Map[_,_]` / `Iterable[_]` → recursive mapping.
6. `Product` → `mirrorProduct` (reflective, `Transformer.scala:52`).
7. `Char`/`Byte`/`Short`/`Int`/`Long`/`Float`/`Double`/`Boolean`/`String` → identity.
8. Otherwise: a warning if `config.enDbg`, and passed through as-is.

After substitution, if the result is `Invalid`, `usedRemovedSymbol` is thrown (`Transformer.scala:68`). `mirrorProduct` (`Transformer.scala:163-178`) reflects on the first constructor and calls `newInstance` with substituted productIterator values — but only "works if the case class has no implicit parameters" (comment at `Transformer.scala:164`). This is the contract for `@op`: it generates a `mirror` override so that reflective construction is never needed. Without `@op`, `Op.mirror` throws (`Op.scala:73`).

### SubstTransformer: isolateSubst is subtractive; excludeSubst is inverse

`isolateSubst(escape*)(scope)` (`SubstTransformer.scala:105-122`) saves `subst`, runs `scope`, then restores `save ++ subst.filter{case (s1,_) => escape.contains(s1)}`. That is: all substitutions made inside the scope are discarded except those keyed by escape syms (plus all substitutions from before the scope). This is the "reset with opt-in keep" semantics.

`excludeSubst(exclude*)(block)` (`SubstTransformer.scala:131-136`) is the dual: runs `block`, then restores `save ++ subst.filterNot{case (s,_) => exclude.contains(s)}`. All substitutions made inside are kept except those in `exclude`.

`blockToFunction0` default (`Transformer.scala:222`) is just `inlineBlock(b).unbox`. `SubstTransformer.blockToFunction0` (`SubstTransformer.scala:139-143`) wraps that in `isolateSubst()` with no escapees — so every block inline scope resets subst rules after. The `lambda{1,2,3}ToFunction{1,2,3}` variants (`SubstTransformer.scala:145-170`) register `input -> a` rules before invoking `blockToFunction0`.

### ForwardTransformer's `createSubstRule` is subtle

The pre-transformed case (`ForwardTransformer.scala:36-51`) has two sub-cases in the comment:

- **Case 1** (multiple traversals in different scopes, e.g., CSE across two scopes): "Keep substitution rule".
- **Case 2** (transformer has already visited this scope once, e.g., higher scope pre-transformed): "Mirror the existing symbol, scrub previous substitution from context to avoid having it show up in effects summaries."

The implementation is:
```
val lhs2: Sym[A] = f(lhs)
val lhs3: Sym[A] = mirrorSym(lhs2)
if (lhs3 != lhs2 && lhs != lhs2) removeSym(lhs2)
lhs3
```

So if `f(lhs)` already maps to some `lhs2`, mirror `lhs2` to `lhs3`. If mirroring actually changed `lhs2` (`lhs3 != lhs2`) and the lhs itself had moved (`lhs != lhs2`), remove the intermediate `lhs2`. This is a three-way dance — errors in the removal condition could silently leak stale symbols.

### MutateTransformer: `copyMode` toggles default between update and mirror

`MutateTransformer.transform` (`MutateTransformer.scala:32-34`) calls `update(lhs, rhs)`. `update` (`MutateTransformer.scala:43-54`) checks `copyMode`: if `true`, delegates to `mirror(lhs, rhs)` (inherited from Transformer); otherwise, calls `updateNode(rhs)` (`MutateTransformer.scala:56-61`) which special-cases `Enabled[_]` to `updateEn(f, f(enables))` and otherwise calls `node.update(f)`. Then `restageWithFlow(lhs)` (`Staging.scala:158-165`) pushes the updated sym back onto the current scope's `state.scope`.

Crucially, `blockToFunction0` in `MutateTransformer` (`MutateTransformer.scala:36-40`) forces `copyMode = true` inside. So when the user invokes `lambda.toFunction0()()` inside a MutateTransformer, the inline is a copy, not an update. This is asymmetric and easy to forget: the outer transformer updates in place, but block-inlining within it copies.

### Metadata model: Data + SetBy + Transfer = 3-axis cube

`Data[T]` (`Data.scala:71-83`) carries a `transfer: Transfer.Transfer` which is `Remove`, `Mirror`, or `Ignore` (`Data.scala:47-60`). `SetBy` (`Data.scala:8-26`) is a semantic layer: `User`, `Flow.Self`, `Flow.Consumer`, `Analysis.Self`, `Analysis.Consumer`, plus `GlobalData.{User, Flow, Analysis}`. `Transfer(src: SetBy)` (`Data.scala:51-60`) maps SetBy categories to Transfer semantics:

- `User` / `Flow.Self` / `Analysis.Self` → `Mirror` (preserved across transforms, but reconstructed).
- `Flow.Consumer` / `Analysis.Consumer` / `GlobalData.Flow` / `GlobalData.Analysis` → `Remove`.
- `GlobalData.User` → `Mirror`.

`Transfer.Ignore` is only reached by direct-specify (like `Effects` at `Effects.scala:30` or `ShallowAliases`/`DeepAliases` at `Aliases.scala:3-5`). During `Transformer.transferData` (`Transformer.scala:99-109`), each metadata entry's transfer decides its fate:

- `Mirror` → `metadata.add(dest, k, mirror(m))` (mirror rule runs).
- `Remove` → `metadata.remove(dest, k)` (explicitly drop).
- `Ignore` → do nothing (stays on dest if it was already there somehow).

The comment at `Transformer.scala:106` calls out that `Remove` is "very bug prone" because memories are visited before their users, so clearing memory metadata wipes the readers/writers lists too.

## Open questions

Filed as:

- **Q-007**: `recurseAtomicLookup` is one-level only, despite the name (`Staging.scala:245-247`). Is this intentional, or should it recurse through nested `AtomicRead` chains?
- **Q-008**: Why does `stageScope_Start` still check `state.mayMotion` (`Scoping.scala:62`) when both branches return `SimpleScheduler`? Was an alternate scheduler removed? Is code motion dead code?
- **Q-009**: `Block.equals` omits `stms` (`Block.scala:43-48`). Is this relied on by `blockSubst`, or does it break identity tracking when two schedulers produce different statement orders for the same result/effects/inputs?
- **Q-010**: `ForwardTransformer.createSubstRule`'s "pre-transformed" case (`ForwardTransformer.scala:36-51`) uses `removeSym(lhs2)` only when `lhs3 != lhs2 && lhs != lhs2`. Could the edge case `lhs == lhs2` with `lhs3 != lhs2` leak the intermediate?
- **Q-011**: `MutateTransformer.mirrorNode`'s `Enabled` branch (`MutateTransformer.scala:63-66`) uses `mirrorEn(f, f(enables))`, but `updateNode`'s `Enabled` branch (`MutateTransformer.scala:56-59`) passes `addEns = f(enables)` — if an already-mirrored lhs gets re-mirrored, does `enables` double-apply?
- **Q-012**: `ScopeBundleRegistry.bundles` never removes entries (`State.scala:25`). Is there any pathway that prunes it, or is this a memory leak scaled to the compile's scope count?

## Distillation plan

This deep-dive feeds six spec entries:

1. **`10 - Symbols and Types.md`** — all material from sections "Staged values are half-initialized" and "Six-case `Def` ADT".
2. **`20 - Ops and Blocks.md`** — material from "Op has eight default category computations" and "Block equality compares inputs+result+effects+options, not statements", plus `BlockOptions`/`Lambda`/`AtomicRead`.
3. **`30 - Effects and Aliasing.md`** — material from "Effects has semi-lattice structure", "Aliasing: eight sets, three of them recursive", "`checkAliases`: two distinct errors", and "`propagateWrites` and atomic-writes".
4. **`50 - Staging Pipeline.md`** — the full "register: rewrite fires BEFORE effects are computed" narrative plus effect-dep computation and the `stage`/`restage`/`stageWithFlow` variants.
5. **`60 - Scopes and Scheduling.md`** — the full "Scope bundles leak" + "SimpleScheduler DCE has the `s != result` guard" material, plus `Scheduler` contract and `summarizeScope`.
6. **`90 - Transformers.md`** — "`Transformer.apply`: reflective walk", "SubstTransformer: isolateSubst is subtractive", "ForwardTransformer's `createSubstRule` is subtle", "MutateTransformer: `copyMode` toggles default".

Metadata model material ("Metadata model: Data + SetBy + Transfer") is partial distillation for spec `40 - Metadata Model.md` (not in this round's deliverables but referenced as `depends_on` context where relevant).
