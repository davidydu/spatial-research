---
type: spec
concept: Argon Effects and Aliasing
source_files:
  - "argon/src/argon/Effects.scala:20-96"
  - "argon/src/argon/Aliases.scala:1-5"
  - "argon/src/argon/NestedInputs.scala:1-3"
  - "argon/src/argon/Consumers.scala:1-3"
  - "argon/src/argon/static/Staging.scala:39-75"
  - "argon/src/argon/static/Staging.scala:230-261"
  - "argon/src/argon/static/Implicits.scala:153-170"
  - "argon/src/argon/schedule/Scheduler.scala:14-26"
  - "argon/src/argon/Op.scala:48-104"
  - "argon/src/argon/Config.scala:46-47"
source_notes:
  - "[[argon-framework]]"
hls_status: clean
depends_on:
  - "[[20 - Ops and Blocks]]"
  - "[[10 - Symbols and Types]]"
status: draft
---

# Argon Effects and Aliasing

## Summary

Argon's effect system tracks, per staged symbol, the side effects of executing that operation. Effects drive three critical compiler behaviors: CSE eligibility (only idempotent ops are CSE-able), scheduling order (effectful ops carry anti-dependencies), and dead-code elimination (only idempotent syms are droppable). The `Effects` case class is the carrier; seven singleton constants (`Pure`/`Sticky`/`Unique`/`Simple`/`Global`/`Mutable`/`Throws`) cover the common patterns; three lattice-style combinators (`andAlso`/`andThen`/`orElse`) compose them. Aliasing is a separate but coupled system: each symbol carries `ShallowAliases` and `DeepAliases` metadata, and `checkAliases` runs at every register call to catch mutable-aliasing bugs. The `Impure` wrapper associates a symbol with its effects for storage in `State.impure`.

## Syntax / API

The `Effects` case class (`argon/src/argon/Effects.scala:20-30`) has nine fields:

```scala
case class Effects(
  unique:  Boolean = false,   // Should not be CSEd
  sticky:  Boolean = false,   // Should not be code motioned out of blocks
  simple:  Boolean = false,   // Requires ordering with respect to other simple effects
  global:  Boolean = false,   // Modifies execution of the entire program
  mutable: Boolean = false,   // Allocates a mutable structure
  throws:  Boolean = false,   // May throw exceptions
  reads:   Set[Sym[_]] = Set.empty,
  writes:  Set[Sym[_]] = Set.empty,
  antiDeps: Seq[Impure] = Nil
) extends Data[Effects](transfer = Transfer.Ignore) with Serializable
```

Five singleton `lazy val`s in the companion (`argon/src/argon/Effects.scala:77-85`):

- `Pure` — no effects.
- `Sticky` — `sticky = true`.
- `Unique` — `unique = true` (prevents CSE but otherwise idempotent).
- `Simple` — `simple = true`.
- `Global` — `global = true`.
- `Mutable` — `mutable = true`.
- `Throws` — `throws = true`.
- `Writes(x*)` — constructs `Effects(writes = x.toSet)`.
- `Reads(x)` — constructs `Effects(reads = x)`.

User-visible predicates (`argon/src/argon/Effects.scala:47-53`):

- `isPure` — equals `Effects.Pure`.
- `isMutable` — `mutable` field.
- `isIdempotent` — `!simple && !global && !mutable && writes.isEmpty && !throws`.
- `mayCSE` — `isIdempotent && !unique`.
- `mayWrite(ss)` — `global || ss.exists{s => writes contains s}`.
- `mayRead(ss)` — `global || ss.exists{s => reads contains s}`.

The `Impure` case class (`argon/src/argon/Effects.scala:90-96`) pairs a sym with its effects. `Impure.unapply(x: Sym[_])` returns `Some((x, effects))` if `!effects.isPure || effects.antiDeps.nonEmpty` — effectively "this symbol contributes to scheduling."

## Semantics

### The three combinators differ only in `mutable`

All three combinators delegate to the private `combine(that, m1, m2)` helper (`argon/src/argon/Effects.scala:32-44`):

| Combinator | `m1` | `m2` | Meaning |
|---|---|---|---|
| `andAlso(that)` | true | true | Parallel composition; both allocations preserved. |
| `andThen(that)` | false | true | Sequential composition; left's allocation absorbed. |
| `orElse(that)` | false | false | Alternative composition; neither allocation is authoritative. |

All six boolean fields (`unique`/`sticky`/`simple`/`global`/`throws`) are OR'd regardless. `reads` and `writes` are unioned regardless. So the only behavioral difference is in the `mutable` field. Semantically: `andAlso` is "both happen"; `andThen` is "this then that"; `orElse` is "one or the other".

`Effects.star` (`argon/src/argon/Effects.scala:45`) is `this.copy(mutable = false)` — drops mutability. Comment in the source reads "Pure orElse this" — the result of `Effects.Pure.orElse(this)` would indeed zero the `mutable` flag.

### Idempotence and CSE eligibility

`isIdempotent` requires ALL of: no simple ordering constraint, no global effect, no mutable allocation, empty `writes`, no throws (`argon/src/argon/Effects.scala:49`). Note: `reads` are allowed. A read-only op on mutable state is still idempotent if it has no other effects.

`mayCSE = isIdempotent && !unique` (`argon/src/argon/Effects.scala:50`). The `unique` flag is an opt-out: "I am pure but I don't want to be CSE'd" (useful when the same op could be stage-cached but the DSL semantics require distinct sym identity).

### Scheduling: `antiDeps` and effect hazards

The `antiDeps: Seq[Impure]` field (`argon/src/argon/Effects.scala:29`) holds the scheduling dependencies for a symbol. It is populated during `computeEffects` (see `[[50 - Staging Pipeline]]`). `effectDependencies(effects)` at `argon/src/argon/static/Staging.scala:202-228` computes four kinds of hazards by scanning `state.impure`:

- **Global effects** (`argon/src/argon/static/Staging.scala:203`) — if `effects.global`, depend on ALL prior impure statements.
- **WAR (Write-After-Read)** (`argon/src/argon/static/Staging.scala:209`) — any prior statement that may read what we're about to write.
- **RAW/WAW** / "AAW" (access-after-write, `argon/src/argon/static/Staging.scala:211-220`) — any prior write to a sym we read/write. Walks `state.impure` tracking `unwrittenAccesses`; as soon as we find a write to an access, it's removed from the tracking set (so we don't continue to report WAW against even earlier writes).
- **Alias on shared sym** (`argon/src/argon/static/Staging.scala:222`) — any prior statement whose `s` is contained in `accesses`.
- **Simple ordering** (`argon/src/argon/static/Staging.scala:223`) — if `effects.simple`, include the most recent prior simple.
- **Global ordering** (`argon/src/argon/static/Staging.scala:224`) — always include the most recent prior global (even if we are not global).

The returned `hazards ++ simpleDep ++ globalDep` (`argon/src/argon/static/Staging.scala:226`) becomes `effects.antiDeps`.

### Aliasing metadata

Three `Data[_]` subclasses carry alias information per symbol:

- `ShallowAliases(aliases: Set[Sym[_]])` (`argon/src/argon/Aliases.scala:3`) — `Transfer.Ignore`.
- `DeepAliases(aliases: Set[Sym[_]])` (`argon/src/argon/Aliases.scala:5`) — `Transfer.Ignore`.
- `NestedInputs(inputs: Set[Sym[_]])` (`argon/src/argon/NestedInputs.scala:3`) — `Transfer.Remove` (dropped on transform; recomputed lazily by `expOps.nestedInputs` at `argon/src/argon/static/Implicits.scala:143-151`).

A fourth, `Consumers(users: Set[Sym[_]])` (`argon/src/argon/Consumers.scala:3`), is `SetBy.Flow.Consumer`, which maps to `Transfer.Remove`.

Access is via `expOps` infix methods (`argon/src/argon/static/Implicits.scala:160-170`):

- `sym.shallowAliases` — includes `sym` itself (`argon/src/argon/static/Implicits.scala:160`).
- `sym.deepAliases` — includes `sym` itself (`argon/src/argon/static/Implicits.scala:166`).
- `sym.allAliases` = `shallowAliases ∪ deepAliases`.
- `sym.mutableAliases` = `allAliases.filter(_.isMutable)`.

Note: `sym.isMutable = sym.effects.isMutable` (`argon/src/argon/static/Implicits.scala:155`) — mutability is a property of the symbol's effects, not a separate flag.

The `Op`-level alias sets (`aliases`/`contains`/`extracts`/`copies`) flow into `shallowAliases`/`deepAliases` through the recursive definition at `argon/src/argon/Op.scala:85-95`. See `[[20 - Ops and Blocks]]` for the definition.

### `checkAliases`: two error paths

`checkAliases(sym, effects)` at `argon/src/argon/static/Staging.scala:39-75` raises errors in two cases:

**Mutable aliasing** (`argon/src/argon/static/Staging.scala:41-60`). Computes `aliases = (sym.mutableAliases diff effects.writes) diff Set(sym)`. If non-empty AND `!config.enableMutableAliases`, emits an error per alias: `"$sym has multiple mutable aliases. Mutable aliasing is disallowed."`. The diff-by-writes subtraction means: if this op is itself writing the alias, it's not flagged.

**Mutation of immutable** (`argon/src/argon/static/Staging.scala:40, 61-74`). Computes `immutables = effects.writes.filterNot(_.isMutable)`. If non-empty, ALWAYS emits an error per immutable: `"Illegal mutation of immutable $s"`. No config toggle.

### `propagateWrites` and atomic writes

`propagateWrites(effects)` at `argon/src/argon/static/Staging.scala:252-261` is gated by `config.enableAtomicWrites` (`argon/src/argon/Config.scala:46`, default `true`):

- **If disabled**: `effects.copy(writes = writes.flatMap{s => s.allAliases})` — every write propagates to all aliases, period.
- **If enabled**: `effects.copy(writes = writes.flatMap{s => extractAtomicWrite(s).allAliases})` — for each written sym, walk to the outermost atomic container first.

`extractAtomicWrite(s)` at `argon/src/argon/static/Staging.scala:248-250` is `syms(recurseAtomicLookup(s)).headOption.getOrElse(s)`. `recurseAtomicLookup(e)` at `argon/src/argon/static/Staging.scala:245-247` checks if the sym's op is `AtomicRead[_]`; if yes, returns `d.coll`, else returns `e`. Note this is a one-level walk despite the name — for deeply nested `AtomicRead` chains, this is technically insufficient (see Q-007).

The example from the source comment (`argon/src/argon/static/Staging.scala:236-244`):
```
val b = Array(1, 2, 3)
val a = MutableStruct(b, ...)
a.b(0) = 1
```
The write `a.b(0) = 1` should be reflected on `a`, not on the immutable result of `a.b`. Atomic-write walks `a.b` (an `AtomicRead`) back to `a`.

### Scope effect summary

`Scheduler.summarizeScope(impure: Seq[Impure])` at `argon/src/argon/schedule/Scheduler.scala:14-26` folds `andThen` over a scope's impure statements, then subtracts allocation-local reads/writes:

```
var effects: Effects = Effects.Pure
val allocs = HashSet[Sym[_]]()
val reads  = HashSet[Sym[_]]()
val writes = HashSet[Sym[_]]()
impure.foreach{case Impure(s,eff) =>
  if (eff.isMutable) allocs += s
  reads ++= eff.reads
  writes ++= eff.writes
  effects = effects andThen eff
}
effects.copy(reads = effects.reads diff allocs, writes = effects.writes diff allocs, antiDeps = impure)
```

Every mutable allocation inside the scope is removed from the returned reads/writes, so the block's external effect view excludes scope-local mutation. `antiDeps = impure` preserves the scope's ordering constraints for any parent scope that wants them.

## Implementation

### `Effects.combine`

Private helper (`argon/src/argon/Effects.scala:32-41`):
```
private def combine(that: Effects, m1: Boolean, m2: Boolean) = Effects(
  unique  = this.unique || that.unique,
  sticky  = this.sticky || that.sticky,
  simple  = this.simple || that.simple,
  global  = this.global || that.global,
  mutable = (m1 && this.mutable) || (m2 && that.mutable),
  throws  = this.throws || that.throws,
  reads   = this.reads union that.reads,
  writes  = this.writes union that.writes
)
```

Note the result has `antiDeps = Nil` — the default. Anti-deps are only set explicitly in `computeEffects` (`argon/src/argon/static/Staging.scala:230-234`).

### `Impure` pattern match

`Impure.unapply(x: Sym[_])` (`argon/src/argon/Effects.scala:92-95`) returns `Some((x, effects))` iff the symbol has non-trivial effects or anti-deps. This is the extractor used throughout `effectDependencies` and `SimpleScheduler`: `state.impure.find{case Impure(s,e) => e.simple}` looks for any simple-effect impure.

### Configuration toggles

Two `Config` flags affect effect semantics (`argon/src/argon/Config.scala:46-47`):

- `enableAtomicWrites: Boolean = true` — toggles `propagateWrites` to use `extractAtomicWrite` vs. plain `s.allAliases`.
- `enableMutableAliases: Boolean = false` — disables the mutable-aliasing error in `checkAliases`.

Both are read at every `register` call, so changing them mid-compile will have inconsistent results.

### `Data` integration

`Effects extends Data[Effects](transfer = Transfer.Ignore)` (`argon/src/argon/Effects.scala:30`) — never transferred across mirror (always recomputed). `Consumers` is `SetBy.Flow.Consumer` → `Transfer.Remove` (recomputed by flow rules after mirror). `ShallowAliases`/`DeepAliases` are `Transfer.Ignore` (recomputed during `register`). `NestedInputs` is `Transfer.Remove` (lazily recomputed in `expOps.nestedInputs`).

## Interactions

- **Staging Pipeline** (see `[[50 - Staging Pipeline]]`): `register` calls `computeEffects`, sets `sym.effects`, and calls `checkAliases` at step 9. CSE cache lookup checks `s.effects == effects` (`argon/src/argon/static/Staging.scala:113`).
- **Scheduling** (see `[[60 - Scopes and Scheduling]]`): `summarizeScope` computes the block-level effect summary. `SimpleScheduler` DCE requires `s.effects.isIdempotent` to drop a symbol.
- **Transformers** (see `[[90 - Transformers]]`): `Transfer.Remove` metadata (like `Consumers`, `NestedInputs`) is recomputed after mirror; `Transfer.Ignore` metadata (like `Effects`, `ShallowAliases`, `DeepAliases`) is left alone (since it's always set by `register`).
- **Op.effects default** (`argon/src/argon/Op.scala:70`): pure nodes inherit `blocks.map(_.effects).fold(Effects.Pure){(a,b) => a andAlso b}` which correctly captures block-nested effects.

## HLS notes

The effect system maps cleanly to a Rust `struct Effects` with `BitSet`/`HashSet` fields. `andAlso`/`andThen`/`orElse` are pure functions — trivial. `Impure` is a `(SymId, Effects)` tuple. The `enableAtomicWrites` / `enableMutableAliases` toggles should be consumed as part of compile-time feature flags or a runtime `CompilerConfig` struct passed to the staging engine.

One porting risk: `summarizeScope`'s `andThen` fold order must match the scope's declaration order. If Rust uses iterator combinators, `fold` starting from `Effects::pure()` and applying `and_then` left-to-right mirrors the behavior.

## Open questions

- See `[[20 - Open Questions]]` Q-007: `recurseAtomicLookup` is one-level only despite the name. Is this intentional? Nested mutable structs would need multi-level recursion.
