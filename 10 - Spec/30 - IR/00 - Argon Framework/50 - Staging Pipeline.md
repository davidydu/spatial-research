---
type: spec
concept: Argon Staging Pipeline
source_files:
  - "argon/src/argon/static/Staging.scala:28-32"
  - "argon/src/argon/static/Staging.scala:39-75"
  - "argon/src/argon/static/Staging.scala:77-78"
  - "argon/src/argon/static/Staging.scala:80-92"
  - "argon/src/argon/static/Staging.scala:93-153"
  - "argon/src/argon/static/Staging.scala:155-165"
  - "argon/src/argon/static/Staging.scala:168-182"
  - "argon/src/argon/static/Staging.scala:184-192"
  - "argon/src/argon/static/Staging.scala:194-234"
  - "argon/src/argon/static/Staging.scala:236-261"
  - "argon/src/argon/State.scala:105-115"
  - "argon/src/argon/Rewrites.scala:50-59"
  - "argon/src/argon/Flows.scala:36-41"
source_notes:
  - "[[argon-framework]]"
hls_status: clean
depends_on:
  - "[[10 - Symbols and Types]]"
  - "[[20 - Ops and Blocks]]"
  - "[[30 - Effects and Aliasing]]"
  - "[[60 - Scopes and Scheduling]]"
status: draft
---

# Argon Staging Pipeline

## Summary

The Argon staging pipeline turns a call to `stage(op)` into a staged `Sym[R]` carrying effect and alias metadata, registered in the current scope, and possibly rewritten or CSE'd. The core is `register`, a 9-step algorithm that runs a rewrite rule, computes effects, checks CSE, and pushes the new symbol into `state.scope`/`state.impure`/`state.cache`. Three public entry points (`stage`, `restage`, `stageWithFlow`) all funnel through `register`. The per-op effect calculation — `computeEffects` — attaches the symbol's anti-dependencies by scanning `state.impure` for WAR/RAW/WAW/simple/global hazards. The algorithm is the one point in Argon where every new IR node is born: it is the substrate every DSL constructor ultimately touches.

## Syntax / API

The three entry points all take an `Op[R]` and return an `R` (which is the staged Scala type, e.g. `Fix[...]`, `Bit`, `Var[A]`):

- `stage[R](op: Op[R])` at `argon/src/argon/static/Staging.scala:172` — the common case.
- `stageWithFlow[R](op: Op[R])(flow: Sym[R] => Unit)` at `argon/src/argon/static/Staging.scala:180-182` — same, plus a per-symbol flow callback that runs before registered `@flow` PFs.
- `restage[R](sym: Sym[R])` at `argon/src/argon/static/Staging.scala:158` — re-run staging on an existing sym (used by `MutateTransformer.update` at `argon/src/argon/transform/MutateTransformer.scala:47`). Extracts the existing op and calls `register` with `symbol = () => sym.unbox`. Only works for `Def.Node` symbols; returns `sym` for constants/params/bounds.
- `restageWithFlow[R](sym: Sym[R])(flow: Sym[R] => Unit)` at `argon/src/argon/static/Staging.scala:160-165` — the restage variant with an extra flow callback.

Supporting functions:

- `rewrite[R](op: Op[R]): Option[R]` at `argon/src/argon/static/Staging.scala:77` — delegates to `state.rewrites.apply(op)`.
- `runFlows[A](sym: Sym[A], op: Op[A]): Unit` at `argon/src/argon/static/Staging.scala:78` — delegates to `state.flows.apply(sym, op)`.
- `withFlow[A](name, flow, prepend)(scope)` at `argon/src/argon/static/Staging.scala:184-192` — scoped flow-rule registration. Saves the current `Flows` state, adds the rule, runs scope, restores.
- `computeEffects(d: Op[_]): Effects` at `argon/src/argon/static/Staging.scala:230-234`.
- `propagateWrites(effects: Effects): Effects` at `argon/src/argon/static/Staging.scala:252-261`.
- `extractAtomicWrite(s: Sym[_]): Sym[_]` at `argon/src/argon/static/Staging.scala:248-250`.
- `checkAliases(sym, effects)` at `argon/src/argon/static/Staging.scala:39-75`.
- `parameter`/`const`/`uconst`/`_const`/`_param`/`err`/`err_`/`boundVar` — see `[[10 - Symbols and Types]]`.

## Semantics

### The nine-step `register` algorithm

`register[R](op: Op[R], symbol: () => R, flowImmediate: Sym[R] => Unit): R` at `argon/src/argon/static/Staging.scala:93-153`:

**Step 0 — Validity check** (`argon/src/argon/static/Staging.scala:94-101`). If `state` is null, or `state.scope` is null, or `state.impure` is null (i.e. we are not inside any staging scope), emit an error `"Only constant declarations are allowed in the global namespace."` and return `err_[R](op.R, "Invalid declaration in global namespace")`. This enforces that every stage call must be inside a `stageScope`/`stageBlock`/`stageLambda{1,2,3}` call.

**Step 1 — Rewrite** (`argon/src/argon/static/Staging.scala:103`). `rewrite(op)` checks (a) `op.rewrite` (the node-level override at `argon/src/argon/Op.scala:72`), (b) per-class rewrite rules in `state.rewrites`, (c) global rewrite rules in `state.rewrites.globals` (see `argon/src/argon/Rewrites.scala:50-53`). If ANY returns a non-null result whose `tp <:< op.R` (type subtyping check at `argon/src/argon/Rewrites.scala:44-47`), that result is returned directly — the remaining steps do NOT run. The CSE cache, effects computation, scope push, and flow rules are all skipped. Any effect of the rewritten subgraph has already been captured by the staged ops it produced.

**Step 2 — Alias categories** (`argon/src/argon/static/Staging.scala:106-107`). Compute `sAliases = op.shallowAliases` and `dAliases = op.deepAliases` using the recursive definitions in `Op` (see `[[20 - Ops and Blocks]]`). These walk the already-staged input symbols' metadata.

**Step 3 — Effect computation** (`argon/src/argon/static/Staging.scala:109`). `effects = computeEffects(op)`. See the subsection below.

**Step 4 — CSE check** (`argon/src/argon/static/Staging.scala:113-114`). Look up the op in `state.cache`. Two conditions must both hold for a cache hit:

1. `effects.mayCSE` — the op is idempotent and not `unique`.
2. `s.effects == effects` — the cached sym's effects match exactly (including anti-deps).

If both hold AND `s.tp <:< op.R`, return `s.asInstanceOf[R]`. Otherwise, fall through.

**Step 5 — Create new symbol** (`argon/src/argon/static/Staging.scala:117-118`). Invoke the `symbol()` factory (`() => symbol(op.R, op)` for `stage`; `() => sym.unbox` for `restage`). The factory calls the private `symbol(tp, op)` at `argon/src/argon/static/Staging.scala:28-32` which creates `Def.Node(state.nextId(), op)` and calls `tp._new(def, ctx)`. The boxed result is `op.R.boxed(lhs)`.

**Step 6 — Push to scope / CSE cache / impure list** (`argon/src/argon/static/Staging.scala:121-125`):
```
state.scope :+= sym
if (effects.mayCSE)  state.cache += op -> sym
if (!effects.isPure) state.impure :+= Impure(sym, effects)
```

Note: `state.scope` always receives every new sym; `state.cache` only if CSE-eligible; `state.impure` only if effects are non-Pure.

**Step 7 — Set effects & aliases** (`argon/src/argon/static/Staging.scala:126-129`):
```
sym.effects = effects
sym.deepAliases = dAliases
sym.shallowAliases = sAliases
sym.allAliases.foreach{alias => alias.shallowAliases += sym}
```

The last line is the **reverse-alias registration**: every sym this op aliases gets us added to its shallow-alias set. After this, the alias graph is bidirectional.

**Step 8 — Consumer metadata** (`argon/src/argon/static/Staging.scala:132`). `op.inputs.foreach{in => in.consumers += sym}`. Each input is told that `sym` now consumes it.

**Step 9 — Immediate flow** (`argon/src/argon/static/Staging.scala:136`). `flowImmediate(sym)` runs the per-call callback. For `stage` this is just `{t => t.ctx = ctx}` (set `_ctx`); for `stageWithFlow` it's `{t => t.ctx = ctx; flow(t)}` (the user flow on top). For `mirror` in transformers it's `{lhs2 => transferDataIfNew(lhs, lhs2)}` (see `[[90 - Transformers]]`). This runs BEFORE registered `@flow` rules, so immediate flow sets up metadata that registered flows can depend on.

**Step 10 — Registered flows** (`argon/src/argon/static/Staging.scala:140`). `runFlows(sym, op)` iterates over all rules registered in `state.flows` (via `state.flows.add`/`prepend`), applying each PF if `isDefinedAt((sym, op, ctx, state))` (see `argon/src/argon/Flows.scala:36-41`).

**Step 11 — Mutable-alias check** (`argon/src/argon/static/Staging.scala:148`). `checkAliases(sym, effects)` — see `[[30 - Effects and Aliasing]]`. This runs AFTER flow rules, so flow rules that modify effects/aliases will be visible here.

(The subsections 0-11 above match the "9-step" phrasing by collapsing: Step 0 = validity; Steps 1-2 = pre-register; Step 3 = effects; Step 4 = CSE; Steps 5-6 = create; Step 7 = aliases; Step 8 = consumers; Step 9 = immediate; Step 10 = flows; Step 11 = checks. The source comment at `argon/src/argon/static/Staging.scala:80-92` numbers these 0-9 but folds some together; the actual code has more fine-grained ordering.)

### `computeEffects`

`computeEffects(d: Op[_]): Effects` at `argon/src/argon/static/Staging.scala:230-234`:

```
val effects = propagateWrites(d.effects) andAlso Effects.Reads(d.mutableInputs)
val deps = effectDependencies(effects)
effects.copy(antiDeps = deps)
```

Three steps:

1. **Propagate writes through aliases**: `propagateWrites(d.effects)` (see `[[30 - Effects and Aliasing]]`) — expand each write to include its aliases (with atomic-write rewriting if enabled).
2. **Add mutable-input reads**: `andAlso Effects.Reads(d.mutableInputs)` (`argon/src/argon/Op.scala:100-104`) — the op implicitly reads every mutable input it touches, even if the node declaration doesn't mention it.
3. **Attach anti-deps**: compute `effectDependencies(effects)` and store as `antiDeps`.

### `effectDependencies`: the hazard scanner

`effectDependencies(effects)` at `argon/src/argon/static/Staging.scala:202-228`:

```
if (effects.global) state.impure
else {
  val read = effects.reads
  val write = effects.writes
  val accesses = read ++ write

  def isWARHazard(u: Effects) = u.mayRead(write)

  var unwrittenAccesses = accesses
  def isAAWHazard(u: Effects) = {
    if (unwrittenAccesses.nonEmpty) {
      val (written, unwritten) = unwrittenAccesses.partition(u.writes.contains)
      unwrittenAccesses = unwritten
      written.nonEmpty
    } else false
  }

  val hazards = state.impure.filter{case Impure(s,e) =>
    isWARHazard(e) || isAAWHazard(e) || (accesses contains s)
  }
  val simpleDep = if (effects.simple) state.impure.find{case Impure(s,e) => e.simple} else None
  val globalDep = state.impure.find{case Impure(_,e) => e.global}

  hazards ++ simpleDep ++ globalDep
}
```

Key behaviors:

- If `effects.global` is true, **all** prior impure statements are anti-deps. No filtering.
- Otherwise, scan `state.impure` (which is a `Vector[Impure]` in insertion order — i.e. program order within this scope).
- WAR: any `u` that `mayRead` what we write is a hazard.
- AAW (access-after-write): walk `state.impure` in order tracking `unwrittenAccesses`. When we encounter a statement that writes to one of our accesses, that access is no longer "unwritten" — we've found its most recent writer. This ensures we attach anti-deps only to the MOST RECENT writer of each read access, not to all prior writers.
- The `(accesses contains s)` condition attaches an anti-dep to any statement whose sym is in our access set — i.e. if we read/write sym `x`, we depend on the statement that created `x` (allocation-before-access).
- Simple ordering: depend on the most recent prior simple effect (if we are ourselves simple).
- Global ordering: ALWAYS depend on the most recent prior global (regardless of our own effects).

Note: `simpleDep` is only added if `effects.simple`; `globalDep` is added unconditionally. This models: "global effects act as memory barriers" but "simple effects only order among themselves."

### `stage` vs `stageWithFlow` vs `restage`

- `stage[R](op)` (`argon/src/argon/static/Staging.scala:172`): creates a fresh sym and sets `.ctx = ctx`.
- `stageWithFlow[R](op)(flow)` (`argon/src/argon/static/Staging.scala:180-182`): creates a fresh sym, sets `.ctx = ctx`, then runs the user `flow(t)` callback BEFORE the registered flows.
- `restage[R](sym)` / `restageWithFlow[R](sym)(flow)` (`argon/src/argon/static/Staging.scala:158-165`): extracts `rhs` from the sym via `case Op(rhs) => ...`, calls `register` with `symbol = () => sym.unbox` (reusing the existing sym's identity), and re-runs the pipeline. This means: rewrites can still fire (replacing the sym), but typically restage is used after in-place `update(f)` to re-register the sym with updated effects/consumers.

### Scope-aware CSE

CSE cache `state.cache` is per-`ScopeBundle` (`argon/src/argon/State.scala:111-112`). Each scope has its own cache, but `withNewScope(motion=true)` (`argon/src/argon/State.scala:140-146`) inherits the outer scope's cache, allowing CSE across the boundary. `withNewScope(motion=false)` starts with `Map.empty`, isolating CSE. This is why `BlockOptions.Sealed` (with `Freq.Cold`) and explicit scheduler override use have no CSE across the boundary — see `[[60 - Scopes and Scheduling]]`.

## Implementation

### The `@rig` annotation contract

`register`, `rewrite`, `runFlows`, `stage`, `restage`, `stageWithFlow`, `checkAliases`, `computeEffects`, `recurseAtomicLookup`, `extractAtomicWrite`, `propagateWrites` are all marked `@rig` (except the pure `propagateWrites` which is `@stateful`). This is the Forge macro that injects implicit `SrcCtx` (ctx) and `State` parameters — every staging call implicitly passes both.

### The rewrite trampoline

`rewrite[R](op: Op[R])` at `argon/src/argon/static/Staging.scala:77` delegates to `state.rewrites.apply(op)(op.R, ctx, state)`. The internals of `Rewrites.apply` (`argon/src/argon/Rewrites.scala:50-59`) try in sequence:
1. `Option(op.rewrite)` — the node's own `@rig` override.
2. `rules.getOrElse(op.getClass, Nil)` — per-class registered rules.
3. `globals` — registered global rules.

The first `Some(s)` wins. Rules are registered via `state.rewrites.add[O<:Op]` / `addGlobal` (see `[[70 - Rewrites and Flows]]` for detail, not in this spec round).

### Why step order matters

The ordering "rewrite → aliases → effects → CSE → symbol → scope → effects metadata → aliases metadata → consumers → immediate → flows → checkAliases" has three load-bearing dependencies:

1. **Rewrite before effects**: a rewrite rule might replace `x + 0` with `x`, avoiding the need to compute effects at all. Running effects first would be wasted work.
2. **CSE cache match requires effects equality**: two ops with different anti-deps (from different scopes) must not collide.
3. **checkAliases after flows**: a flow rule might attach metadata that changes what counts as an alias. `checkAliases` must see the final state.

### `state.scope`/`state.impure`/`state.cache` mutation

All three are mutated in place during `register` (`argon/src/argon/static/Staging.scala:121-125`). `state.scope` is a `Vector[Sym[_]]`; `state.impure` is a `Vector[Impure]`; `state.cache` is a `Map[Op[_], Sym[_]]`. The `Vector` choice preserves insertion order (important for `effectDependencies`) while still supporting `:+=` in amortized `O(log n)`. The `Map` choice is a standard `HashMap`.

## Interactions

- **Scoping** (see `[[60 - Scopes and Scheduling]]`): `stageScope_Start` creates a new `ScopeBundle` and calls the user's block; that block's stage calls mutate the new bundle. `stageScope_Schedule` turns the resulting scope into a `Block` via the scheduler.
- **Transformers** (see `[[90 - Transformers]]`): `Transformer.mirror` calls `stageWithFlow(mirrorNode(rhs)){lhs2 => transferDataIfNew(lhs, lhs2)}`. `MutateTransformer.update` calls `restageWithFlow`.
- **Rewrites**: user-registered rewrite rules via `state.rewrites.add[O]` fire at step 1.
- **Flows**: user-registered flow rules via `state.flows.add` fire at step 10.

## HLS notes

The 9-step pipeline has no inherent ties to Scala or JVM. Three concerns when porting:

1. **Scala `Op` reflection via `productIterator`**: the default `inputs`/`blocks` computations walk `Product.productIterator` reflectively. In Rust, each op must declare its inputs/blocks via derive macro or explicit method; derive-macro-based `#[op]` is the natural analog to `@op`.
2. **`@rig` implicit parameter injection**: Rust equivalents need explicit `ctx: SrcCtx` and `state: &mut State` parameters, or a thread-local context. Thread-local is simpler but global.
3. **`state.cache` as `HashMap<Op, SymId>`**: requires `Op` to be `Hash + Eq`. In Scala, structural equality comes "for free" from case classes; in Rust, `#[derive(Hash, PartialEq, Eq)]` on each op suffices.

The rewrite+CSE+flow ordering is the substrate every staging engine needs; the algorithm translates 1:1 to Rust.

## Open questions

- See `[[20 - Open Questions]]` Q-007: `recurseAtomicLookup` is one-level only despite the name.
