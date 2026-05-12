---
type: spec
concept: Argon Scopes and Scheduling
source_files:
  - "argon/src/argon/State.scala:9-53"
  - "argon/src/argon/State.scala:55-252"
  - "argon/src/argon/static/Scoping.scala:7-119"
  - "argon/src/argon/schedule/Scheduler.scala:1-38"
  - "argon/src/argon/schedule/SimpleScheduler.scala:1-34"
  - "argon/src/argon/schedule/Schedule.scala:1-14"
  - "argon/src/argon/BlockOptions.scala:1-12"
source_notes:
  - "[[argon-framework]]"
hls_status: rework
depends_on:
  - "[[50 - Staging Pipeline]]"
  - "[[30 - Effects and Aliasing]]"
  - "[[20 - Ops and Blocks]]"
status: draft
---

# Argon Scopes and Scheduling

## Summary

Every block in Argon is staged inside an isolated scope. The scope is a three-part mutable tuple `(scope: Vector[Sym[_]], impure: Vector[Impure], cache: Map[Op[_], Sym[_]])` held in a `ScopeBundle`, and the active bundle is tracked on `State.currentBundle`. Nested scopes stack via `State.withNewScope` / `State.withScope`. When the user's staging code finishes, the scheduler is called to turn the raw bundle into a structured `Block[R]` — with linearization, optional code motion, and optional dead-code elimination. Argon ships one scheduler (`SimpleScheduler`), used by default. Its DCE is idempotent-only; its code-motion output is always empty. The `stageScope` / `stageBlock` / `stageLambda{1,2,3}` helpers encapsulate the full pattern for the user.

## Syntax / API

### State-level scope management

- `State.withScope[R](handle: BundleHandle)(block: => R): R` at `argon/src/argon/State.scala:124-138`. Switches to an existing bundle for the duration of block.
- `State.withNewScope[R](motion: Boolean)(block: => R): (R, BundleHandle)` at `argon/src/argon/State.scala:140-146`. Creates a fresh bundle (inheriting CSE cache iff `motion`), runs block, returns (result, new handle).
- `State.getBundle(h: BundleHandle): Option[ScopeBundle]` at `argon/src/argon/State.scala:114`. Look up a bundle by handle.
- `State.getCurrentHandle(): BundleHandle` at `argon/src/argon/State.scala:115`. Current bundle handle.
- `State.scope` / `State.impure` / `State.cache` at `argon/src/argon/State.scala:105-112` — accessors that forward to the current bundle.

### User-level scoping helpers

- `stageScope[R](inputs: Seq[Sym[_]], options: BlockOptions = BlockOptions.Normal)(block: => Sym[R]): Block[R]` at `argon/src/argon/static/Scoping.scala:88-96`. The all-purpose scope driver. Creates a new bundle, runs `block`, schedules the resulting scope into a `Block`.
- `stageScopeIf[R](en, inputs, options)(block)` at `argon/src/argon/static/Scoping.scala:98-104`. Conditionally stage — either returns `Left(Block)` or `Right(Sym)`.
- `stageBlock[R](block, options)` at `argon/src/argon/static/Scoping.scala:106-108`. Shorthand for `stageScope(Nil, options)(block)`.
- `stageLambda1[A,R](a: Sym[A])(block, options)` at `argon/src/argon/static/Scoping.scala:109-111`. `stageScope(Seq(a))` + `asLambda1[A]`.
- `stageLambda2[A,B,R](a, b)(block, options)` at `argon/src/argon/static/Scoping.scala:112-114`.
- `stageLambda3[A,B,C,R](a, b, c)(block, options)` at `argon/src/argon/static/Scoping.scala:115-117`.

### Lower-level building blocks

- `stageScope_Start[R](inputs, options)(block): (R, Seq[Sym[_]], Seq[Impure], Scheduler, Boolean)` at `argon/src/argon/static/Scoping.scala:56-78`. Creates a bundle, runs `block`, returns the raw scope contents.
- `stageScope_Schedule[R](inputs, result, scope, impure, options, motion, scheduler): Block[R]` at `argon/src/argon/static/Scoping.scala:16-48`. Calls the scheduler on raw contents, handles motioned-out symbols, returns a `Block`.

### Scheduler contract

- `Scheduler` trait at `argon/src/argon/schedule/Scheduler.scala:6-38`. Abstract members: `mustMotion: Boolean`, `apply[R](inputs, result, scope, impure, options, allowMotion): Schedule[R]`. Concrete member: `summarizeScope(impure)`.
- `Schedule[R](block: Block[R], motioned: Seq[Sym[_]], motionedImpure: Seq[Impure] = Nil)` at `argon/src/argon/schedule/Schedule.scala:9-13`.
- `SimpleScheduler(enableDCE: Boolean = true)` class at `argon/src/argon/schedule/SimpleScheduler.scala:6-32`. `SimpleScheduler` object singleton at `argon/src/argon/schedule/SimpleScheduler.scala:34`.

## Semantics

### `ScopeBundle` + `ScopeBundleRegistry`

`ScopeBundle` (`argon/src/argon/State.scala:14-21`) is a mutable triple + handle: `(scope: Vector[Sym[_]], impure: Vector[Impure], cache: Map[Op[_], Sym[_]], handle: BundleHandle)`. It supports a shallow `copy()` (returns a new bundle with the same three fields and handle).

`ScopeBundleRegistry` (`argon/src/argon/State.scala:23-53`) owns a `Map[BundleHandle, ScopeBundle]` and an integer `nextHandle` (starts at `-1`). `CreateNewBundle(impure, scope, cache)` allocates a new bundle with a freshly-issued handle, stores it, and returns it. `GetBundle(h)` is a lookup with an assertion that `h != BundleHandle.InvalidHandle`.

Critical observation: the registry's `bundles` map is **never pruned**. A comment at `argon/src/argon/State.scala:24` reads `"TODO(stanfurd): Replace these with weakreferences so that we don't cause a memory leak."`. For a long-running compilation every bundle ever created stays alive — this is a known unresolved leak.

### `withScope` and `withNewScope`

`withScope[R](handle)(block)` at `argon/src/argon/State.scala:124-138`:
```
val savedBundle = currentBundle
clearBundle()                                            // asserts currentBundle != null
setBundle(scopeBundleRegistry.GetBundle(handle).get)     // asserts currentBundle == null
val result = block
clearBundle()
setBundle(savedBundle)
assert(savedBundle == scopeBundleRegistry.GetBundle(savedBundle.handle).get)
result
```

Two invariants are asserted: `clearBundle` requires non-null; `setBundle` requires null. Violating either is a bug. The final assert checks that bundle identity was preserved across the nested call.

`withNewScope[R](motion)(block)` at `argon/src/argon/State.scala:140-146`:
```
val newBundle = scopeBundleRegistry.CreateNewBundle(
  Vector.empty, Vector.empty,
  if (motion) currentBundle.cache else Map.empty
)
(withScope(newBundle.handle){ block }, newBundle.handle)
```

If `motion=true`, the new bundle inherits the outer CSE cache; if `motion=false`, it starts empty. This is the only point CSE crosses scope boundaries.

### `stageScope_Start` → `stageScope_Schedule`

`stageScope_Start` at `argon/src/argon/static/Scoping.scala:56-78`:

1. Choose scheduler: `options.sched.getOrElse(defaultSched)` where `defaultSched = if (state.mayMotion) SimpleScheduler else SimpleScheduler` (`argon/src/argon/static/Scoping.scala:62`). **Both branches are identical** — the ternary is a no-op (see Q-008).
2. Compute `motion = state.scope != null && (scheduler.mustMotion || state.mayMotion)` (`argon/src/argon/static/Scoping.scala:66`). `SimpleScheduler.mustMotion = false` (`argon/src/argon/schedule/SimpleScheduler.scala:7`), so motion is only true when `state.mayMotion` is true.
3. Call `state.withNewScope(motion){ reify(block) }` (`argon/src/argon/static/Scoping.scala:71-73`) where `reify` just increments the log tab during staging.
4. Get the populated bundle via `state.getBundle(handle).get`.
5. Return `(result, bundle.scope, bundle.impure, scheduler, motion)`.

`stageScope_Schedule` at `argon/src/argon/static/Scoping.scala:16-48`:

1. Call `scheduler(inputs, result, scope, impure, options, motion)` → `Schedule[R]`.
2. If `motion=true`, append `schedule.motioned` and `schedule.motionedImpure` to the **outer** scope (which is now `state.scope` because we're back outside the inner `withNewScope`).
3. Return `schedule.block`.

The `stageScope` function (`argon/src/argon/static/Scoping.scala:88-96`) is simply these two called in sequence. The split exists because `Compiler.stageProgram` uses `stageScope_Start` directly to get the top-level scope for the app.

### `Scheduler.summarizeScope`

Folds `andThen` across the scope's impure statements, then subtracts allocation-local reads/writes (`argon/src/argon/schedule/Scheduler.scala:14-26`). See `[[30 - Effects and Aliasing]]` for the detailed walk.

The result is what gets attached to the block as `block.effects`. This is the EXTERNAL effect summary — internal allocations (`eff.isMutable`) are filtered out of reads/writes. `antiDeps = impure` is preserved so outer scopes can use it for their own hazard checks.

### `SimpleScheduler.apply`: linear DCE

`SimpleScheduler.apply[R]` at `argon/src/argon/schedule/SimpleScheduler.scala:10-31`:

```
val effects = summarizeScope(impure)
val unused = mutable.HashSet.empty[Sym[_]]

scope.reverseIterator.foreach{s =>
  val uses = s.consumers diff unused
  if (s != result && uses.isEmpty && s.effects.isIdempotent && enableDCE) unused += s
}
val keep  = scope.filter{s => !unused.contains(s) }

val block = new Block[R](inputs, keep, result, effects, options)
Schedule(block, Nil)
```

Three conditions for a sym to be dropped (`argon/src/argon/schedule/SimpleScheduler.scala:23-26`):

1. `s != result` — the block's result sym is protected. Even if nothing uses it, we keep it.
2. `s.consumers diff unused` is empty — no live consumer in this scope OR any outer scope.
3. `s.effects.isIdempotent` — the sym has no side effects (see `[[30 - Effects and Aliasing]]`).

Plus `enableDCE` must be true.

The reverse iteration is important: by the time we examine a sym, we've already decided the fate of all its consumers. If a consumer was dropped (added to `unused`), it doesn't count against this sym.

`Schedule(block, Nil)` (`argon/src/argon/schedule/SimpleScheduler.scala:30`) — no motioned syms. Despite the scheduler being invoked with `motion=true` possibly, `SimpleScheduler` never produces motioned output. Code motion is effectively a no-op with the default scheduler (see Q-008).

### Motion semantics and CSE isolation

The `motion` flag plays three roles:

1. **CSE inheritance** (`argon/src/argon/State.scala:140-146`): if true, inner scope inherits outer CSE cache.
2. **Motion output** (`argon/src/argon/static/Scoping.scala:27-30`): if true, scheduler-returned `motioned` syms are appended to the outer scope. With `SimpleScheduler`, this is always a no-op.
3. **Scheduler behavior** (`argon/src/argon/schedule/Scheduler.scala:35`): the `allowMotion: Boolean` parameter. `SimpleScheduler` ignores it.

`BlockOptions.Sealed = BlockOptions(Freq.Cold, None)` (`argon/src/argon/BlockOptions.scala:11`) combined with `scheduler.mustMotion = false` produces `motion = state.mayMotion` which is likely false during most staging — so Sealed blocks have no CSE inheritance from outer.

### Nested scopes and `logTab`

`reify[R](block)` at `argon/src/argon/static/Scoping.scala:9-14` increments `state.logTab` during staging and decrements afterward. This is purely for logging; the indentation in debug output shows nesting depth.

## Implementation

### `State.init`

`State.init()` at `argon/src/argon/State.scala:153-155`:
```
setBundle(scopeBundleRegistry.CreateNewBundle(Vector.empty, Vector.empty, Map.empty))
```

Creates the initial (top-level) bundle and installs it. Called from `Compiler.stageApp` before the user's `main` code runs.

### `State.reset`

`State.reset()` at `argon/src/argon/State.scala:217-233` calls `resetBundles()` (`argon/src/argon/State.scala:148-151`) which sets `currentBundle = null` and allocates a new `ScopeBundleRegistry`. This drops all bundles — the ONE path that prunes the leak, but only at full state reset (between compilations).

### `State.copyTo`

`State.copyTo(target)` at `argon/src/argon/State.scala:235-251` copies the registry using `ScopeBundleRegistry.copyTo` (`argon/src/argon/State.scala:45-52`) which clones every bundle into the target. `target.currentBundle = scopeBundleRegistry.GetBundle(currentBundle.handle).get` ensures the target's current handle points to the corresponding new bundle. This is used for compilation forking in testing.

### `Scheduler.summarizeScope` — allocation subtraction

```
var effects: Effects = Effects.Pure
val allocs = mutable.HashSet[Sym[_]]()
val reads  = mutable.HashSet[Sym[_]]()
val writes = mutable.HashSet[Sym[_]]()
impure.foreach{case Impure(s,eff) =>
  if (eff.isMutable) allocs += s
  reads ++= eff.reads
  writes ++= eff.writes
  effects = effects andThen eff
}
effects.copy(reads = effects.reads diff allocs, writes = effects.writes diff allocs, antiDeps = impure)
```

The local `reads`/`writes` HashSets are accumulated but ONLY used via `effects.reads`/`effects.writes` (the union from `andThen`) minus `allocs`. The fold correctly captures `reads` and `writes` because `andThen` unions them. But the local `reads`/`writes` accumulation at `argon/src/argon/schedule/Scheduler.scala:21-22` appears to be dead code — the values are never used. (Only `allocs` is used in the final diff.)

## Interactions

- **Staging Pipeline** (see `[[50 - Staging Pipeline]]`): `register` writes to `state.scope`/`state.impure`/`state.cache`. These are the bundle's fields. Every `stage`/`restage` is scoped to the current bundle.
- **Transformers** (see `[[90 - Transformers]]`): `Transformer.preprocess` clears `state.cache` before every transformer run. Transformers that call `stageScope`/`stageBlock` during mirroring create nested bundles.
- **Blocks and Lambdas** (see `[[20 - Ops and Blocks]]`): the returned `Block[R]` from `stageScope` is what gets embedded inside parent ops' `blocks` fields.
- **Compiler driver** (separate spec): calls `stageScope_Start` once for the top-level app block; that bundle becomes the initial scope for `runPasses`.

## HLS notes

The `ScopeBundleRegistry` model is fine for an interpreter; it needs tuning for a long-lived compiler. Tagged `hls_status: rework` because:

1. **Memory leak in `bundles`**: an HLS port should use arena allocation or explicit drop. Use `Vec<Option<ScopeBundle>>` with slot-reuse, or just `Vec<ScopeBundle>` with stack-like push/pop if scope lifetimes are strictly nested (which they are in practice).
2. **Ternary no-op**: `defaultSched = if (state.mayMotion) SimpleScheduler else SimpleScheduler` should either pick a motion-aware scheduler or delete the branch. Either way, the HLS rewrite should clarify motion semantics.
3. **`SimpleScheduler` motion output always empty**: Suggests code motion is implemented elsewhere (possibly `spatial/src/`). HLS should verify whether motion is actually used anywhere in Spatial and port only the machinery that matters.
4. **CSE cache inheritance** (`argon/src/argon/State.scala:142`): the `if (motion) currentBundle.cache else Map.empty` rule is sensible but needs to be preserved verbatim — it is the ONLY way CSE crosses scope boundaries.

The scheduler contract itself (`mustMotion`, `apply`, `summarizeScope`) translates cleanly to a Rust trait. `Schedule<R>` is a struct with three fields. `SimpleScheduler::apply` is a straightforward `fn` over slices.

## Open questions

- See `[[20 - Open Questions]]` Q-008: `defaultSched` ternary is identical on both branches (`argon/src/argon/static/Scoping.scala:62`). Intentional? Dead code?
- See `[[20 - Open Questions]]` Q-012: `ScopeBundleRegistry.bundles` grows unboundedly. Is this a real memory leak in practice?
