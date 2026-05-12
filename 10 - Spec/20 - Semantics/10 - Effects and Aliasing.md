---
type: spec
status: draft
concept: effects-and-aliasing-semantics
source_files:
  - "argon/src/argon/Effects.scala:20-96"
  - "argon/src/argon/Op.scala:48-104"
  - "argon/src/argon/Aliases.scala:1-5"
  - "argon/src/argon/NestedInputs.scala:1-3"
  - "argon/src/argon/Consumers.scala:1-3"
  - "argon/src/argon/static/Staging.scala:39-75"
  - "argon/src/argon/static/Staging.scala:202-261"
  - "argon/src/argon/static/Implicits.scala:153-170"
  - "argon/src/argon/schedule/Scheduler.scala:14-26"
  - "argon/src/argon/Config.scala:46-47"
source_notes:
  - "[[30 - Effects and Aliasing]]"
  - "[[20 - Ops and Blocks]]"
  - "[[50 - Staging Pipeline]]"
  - "[[60 - Scopes and Scheduling]]"
  - "[[40 - Metadata Model]]"
  - "[[90 - Transformers]]"
hls_status: clean
depends_on:
  - "[[30 - Effects and Aliasing]]"
  - "[[20 - Ops and Blocks]]"
  - "[[50 - Staging Pipeline]]"
  - "[[60 - Scopes and Scheduling]]"
  - "[[40 - Metadata Model]]"
  - "[[10 - Symbols and Types]]"
---

# Effects and Aliasing

## Summary

Spatial inherits Argon's effect and alias semantics. The lower-level entries [[30 - Effects and Aliasing]], [[20 - Ops and Blocks]], [[50 - Staging Pipeline]], and [[60 - Scopes and Scheduling]] define one contract: every staged symbol has a local `Effects` value; staging expands it through mutable inputs and alias-write propagation; the scheduler and CSE use the resulting `Impure` record to preserve observable behavior. For the Rust+HLS rewrite, this is one of the cleanest pieces to port because the data model is explicit: a boolean lattice plus read/write sets and anti-dependencies (`argon/src/argon/Effects.scala:20-96`). The key risk is not the lattice itself, but preserving the exact alias closure and the exact staging order that fills it (`argon/src/argon/static/Staging.scala:93-153`, `argon/src/argon/static/Staging.scala:230-261`).

## Formal Semantics

An effect is a tuple `(unique, sticky, simple, global, mutable, throws, reads, writes, antiDeps)`. The named constants are abbreviations over that tuple: `Pure` is all false and empty; `Sticky`, `Unique`, `Simple`, `Global`, `Mutable`, and `Throws` set exactly their corresponding boolean; `Reads(xs)` and `Writes(xs)` set only the relevant set field (`argon/src/argon/Effects.scala:20-30`, `argon/src/argon/Effects.scala:77-85`). `isIdempotent` is true exactly when `simple`, `global`, `mutable`, `throws` are false and `writes` is empty; reads alone do not make an op non-idempotent (`argon/src/argon/Effects.scala:47-53`). `mayCSE` is `isIdempotent && !unique`, so `Unique` is not "impure"; it is a CSE opt-out.

`sticky` is preserved in the lattice even though the default `SimpleScheduler` does not currently motion statements; it is still part of the effect contract because other schedulers or transformer phases may use it as a code-motion barrier. `simple` is stronger than `sticky` for ordering because it participates in `effectDependencies` by depending on the most recent prior simple effect (`argon/src/argon/static/Staging.scala:223-226`).

Composition is defined by `combine(that, m1, m2)`. All boolean flags except `mutable` are ORed, `reads` and `writes` are unioned, and `antiDeps` is reset to `Nil`; the only distinction between `andAlso`, `andThen`, and `orElse` is whether left and/or right mutability is preserved (`argon/src/argon/Effects.scala:32-44`). `andAlso` preserves both allocations, `andThen` preserves only the right allocation, and `orElse` preserves neither allocation. `star` is `copy(mutable = false)`, equivalent to the optional-effect shape described in [[30 - Effects and Aliasing]] (`argon/src/argon/Effects.scala:45`).

Scheduling sees only non-pure effects or explicit anti-dependencies through `Impure(sym, effects)`. `Impure.unapply` returns a match when the stored effect is non-pure or its `antiDeps` is nonempty (`argon/src/argon/Effects.scala:90-96`). During staging, `computeEffects` first propagates writes through aliases, then adds `Reads(d.mutableInputs)`, then scans prior impure statements for WAR, RAW/WAW, allocation-before-access, simple, and global hazards (`argon/src/argon/static/Staging.scala:202-234`). A global effect depends on all prior impure statements; a non-global effect depends only on the hazards that the scanner finds. This is the bridge from [[50 - Staging Pipeline]] to [[60 - Scopes and Scheduling]]: source order is not preserved by fiat; it emerges from `antiDeps`.

Alias semantics have three relevant closures. `ShallowAliases` and `DeepAliases` are per-symbol metadata, both ignored by transfer and set during register (`argon/src/argon/Aliases.scala:1-5`). `NestedInputs` records nested block inputs and is removed on transfer, then recomputed lazily by symbol ops (`argon/src/argon/NestedInputs.scala:1-3`, `argon/src/argon/static/Implicits.scala:143-151`). `Op.shallowAliases` is `aliases.shallowAliases union extracts.deepAliases`; `Op.deepAliases` is `aliases.deepAliases union copies.deepAliases union contains.allAliases union extracts.deepAliases` (`argon/src/argon/Op.scala:85-95`). The `contains.allAliases` clause is important: if a result contains a mutable object, every alias reachable through that contained object becomes a deep alias of the result.

After staging a symbol, the staging pipeline writes effects and alias metadata, then adds the new symbol to every alias's shallow-alias set, making the alias graph bidirectional for later checks (`argon/src/argon/static/Staging.scala:126-132`). `sym.shallowAliases` and `sym.deepAliases` include `sym` itself; `sym.mutableAliases` filters `allAliases` by `isMutable`, where `isMutable` is just `sym.effects.isMutable` (`argon/src/argon/static/Implicits.scala:153-170`).

Atomic-write propagation is part of the semantics. If `enableAtomicWrites` is false, each written symbol expands to all aliases. If it is true, each written symbol is first passed through `extractAtomicWrite`, which recognizes an `AtomicRead` and rewrites the write to the collection it dereferenced before expanding aliases (`argon/src/argon/static/Staging.scala:236-261`, `argon/src/argon/Config.scala:46-47`). The lower-level entry [[30 - Effects and Aliasing]] notes that the lookup is only one level deep despite the recursive name; this synthesis preserves that behavior and files it as an unresolved semantics question.

Mutable-alias legality is checked after flows run. `checkAliases` rejects any mutable aliases not being written by the current op unless `enableMutableAliases` is true, and always rejects writes to immutable symbols (`argon/src/argon/static/Staging.scala:39-75`). The mutable-alias contract is therefore: multiple mutable aliases may exist only when explicitly configured, and mutation is legal only for symbols whose allocation effect made them mutable. This contract crosses into [[40 - Metadata Model]] because transfer policies determine whether alias facts are mirrored, removed, or recomputed during transformation.

## Reference Implementation

No Scalagen runtime overrides this model; the reference is Argon staging. The source of truth is `Effects.scala`, `Op.scala`, and `Staging.scala`, with `Scheduler.summarizeScope` defining how a block summarizes internal impure statements for its parent (`argon/src/argon/schedule/Scheduler.scala:14-26`). `summarizeScope` folds `andThen` over impure statements, records mutable allocations, then subtracts allocation-local reads and writes from the external block effect while preserving the whole impure list as `antiDeps`. [[50 - Staging Pipeline]] is normative for when this information is created; [[60 - Scopes and Scheduling]] is normative for when it is consumed.

## HLS Implications

The Rust port should implement `Effects` as an ordinary struct and the three composition operators as pure functions. `Impure` can be a `(SymId, Effects)` record. Alias closures should not be replaced by borrow-checker intuition: Spatial's alias model is graph metadata, not Rust ownership. Atomic-write propagation, mutable-alias errors, and allocation-local effect subtraction should be preserved before any HLS-specific simplification. HLS memory dependence pragmas can be derived later from `reads`, `writes`, and `antiDeps`, but those sets first need to match Argon exactly.

## Open questions

- [[open-questions-semantics#Q-sem-01 - 2026-04-25 Atomic write recursion depth]] tracks the one-level `recurseAtomicLookup` behavior in `argon/src/argon/static/Staging.scala:245-250`.
- [[open-questions-semantics#Q-sem-02 - 2026-04-25 Mutable aliases in Rust ownership terms]] tracks whether the Rust implementation should preserve the `enableMutableAliases` escape hatch or encode it as a hard compile-time error.
