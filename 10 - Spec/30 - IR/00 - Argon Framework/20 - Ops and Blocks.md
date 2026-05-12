---
type: spec
concept: Argon Ops and Blocks
source_files:
  - "argon/src/argon/Op.scala:13-125"
  - "argon/src/argon/Block.scala:6-94"
  - "argon/src/argon/BlockOptions.scala:5-12"
  - "argon/src/argon/Freq.scala:3-14"
  - "argon/src/argon/static/Staging.scala:263-293"
  - "argon/src/argon/static/Implicits.scala:122-131"
source_notes:
  - "[[argon-framework]]"
hls_status: clean
depends_on:
  - "[[10 - Symbols and Types]]"
  - "[[30 - Effects and Aliasing]]"
status: draft
---

# Argon Ops and Blocks

## Summary

`Op[R]` is the base class for every staged operation in Argon: every node in the IR graph is an instance of some `Op` subclass. Each `Op` is a Scala `case class` whose constructor fields carry the dataflow dependencies of the operation. The `Op` trait defines a rich API that every subclass inherits — inputs, reads, frequency hints, alias categories, effects, and the `rewrite`/`mirror`/`update` hooks used by staging and transformers. The `Block[R]` class represents a schedulable sequence of statements with a typed result; `Lambda1/2/3` are sealed subclasses of `Block` that bind explicit input parameters. `BlockOptions` carries per-block scheduler/frequency overrides.

## Syntax / API

Users almost never construct `Op`s directly; the `@op` macro annotation generates `mirror`/`update` overrides for every node class. The core surface:

- `Op[R:Type]` — extend this. Use `Op2[A,R]`, `Op3[A,B,R]`, `Op4[A,B,C,R]` arity helpers (`argon/src/argon/Op.scala:111-113`) when a node's arguments need type-evidence carriers available at runtime for substitution / casting.
- Constructor fields of a case class subclass become both Scala-level parameters and the `productIterator` used for the default `inputs` / `blocks` / `freqs` computations.
- Override any subset of: `inputs`, `reads`, `freqs`, `blocks`, `binds`, `aliases`, `contains`, `extracts`, `copies`, `effects`, `rewrite`, `mirror`, `update`, `shallowAliases`, `deepAliases`.
- Mix in `AtomicRead[M]` (`argon/src/argon/Op.scala:115-117`) for a node that dereferences a collection: it exposes `coll: Sym[M]`, which the atomic-write machinery walks to find the outermost mutable container.
- `Op.unapply` / `Stm.unapply` (`argon/src/argon/Op.scala:119-125`) are pattern extractors for `Sym[_]`.

Blocks are created by the scoping API (`stageBlock`, `stageLambda{1,2,3}`, see `[[60 - Scopes and Scheduling]]`). Users consume blocks through `Block[R]` methods:

- `inputs: Seq[Sym[_]]` — external bound inputs (lambda parameters).
- `stms: Seq[Sym[_]]` — linearized statement list.
- `result: Sym[R]` — the symbolic result (has tp).
- `effects: Effects` — the block's summarized external effects.
- `options: BlockOptions` — frequency + scheduler override carrier.
- `temp: Freq` — shortcut for `options.temp`.
- `nestedStms: Seq[Sym[_]]` — transitive closure of statements across nested blocks.
- `nestedInputs: Set[Sym[_]]` — external symbols referenced by any nested statement.
- `asLambda1[A]` / `asLambda2[A,B]` / `asLambda3[A,B,C]` — unsafe casts when `inputs.length` matches.

## Semantics

### `Op`'s default category computations

Every `Op` inherits nine computable sets that classify its symbol relationships (`argon/src/argon/Op.scala:13-109`):

| Field | Default | Purpose |
|---|---|---|
| `inputs` | `syms(productIterator).toSeq` | Dataflow deps. |
| `reads` | `= inputs` | Symbols dereferenced. |
| `freqs` | `blocks.flatMap{blk => syms(blk).map(_ -> blk.temp)}.toSet` | Code-motion hints. |
| `blocks` | `collectBlocks(productIterator)` | Nested scopes. |
| `binds` | `blocks.flatMap(_.effects.antiDeps.map(_.sym)).toSet` | Bound syms (scope roots). |
| `aliases` | `inputs.collect{case s if s.tp =:= R => s}.toSet` | May-alias inputs. |
| `contains` | `Set.empty` | Inputs held inside the result. |
| `extracts` | `Set.empty` | Inputs produced by dereferencing result. |
| `copies` | `Set.empty` | Inputs whose deref gives the same pointer. |

The `aliases` default is non-trivial: every input with a type matching `R` is considered a potential alias. A node like `VarNew[A]` (`argon/src/argon/node/Var.scala:7-14`) explicitly overrides `aliases = Nul` to opt out; otherwise the init value would be reported as an alias of the resulting `Var[A]`.

`Op.expInputs`/`blockInputs`/`nonBlockExpInputs`/`nonBlockSymInputs` (`argon/src/argon/Op.scala:18-21`) give different projections of the productIterator for use by transformers and flow rules.

### Derived alias sets

The recursive alias closures at `argon/src/argon/Op.scala:85-104` are:

- `shallowAliases = aliasSyms.flatMap(_.shallowAliases) ∪ extractSyms.flatMap(_.deepAliases)` (`argon/src/argon/Op.scala:85-88`).
- `deepAliases = aliasSyms.flatMap(_.deepAliases) ∪ copySyms.flatMap(_.deepAliases) ∪ containSyms.flatMap(_.allAliases) ∪ extractSyms.flatMap(_.deepAliases)` (`argon/src/argon/Op.scala:90-95`).
- `allAliases = deepAliases ∪ shallowAliases` (`argon/src/argon/Op.scala:97`).
- `mutableAliases = allAliases.filter(_.isMutable)` (`argon/src/argon/Op.scala:98`).
- `mutableInputs = (reads.toSet diff bounds).flatMap(_.mutableAliases) diff bounds` (`argon/src/argon/Op.scala:100-104`).

The primitive filter `noPrims` (`argon/src/argon/Op.scala:106`) removes syms whose `tp.neverMutable` is true — this prunes `Bit`, `Fix`, `Flt` and other value types from alias computations. `aliasSyms`/`containSyms`/`extractSyms`/`copySyms` (`argon/src/argon/Op.scala:80-83`) are the `noPrims`-filtered versions used in the recursive calls above.

Asymmetry: `containSyms.flatMap(_.allAliases)` in `deepAliases` uses `allAliases`, not `deepAliases`. This is deliberate: "y contains x" (like `Array(x)`) means x is reachable through y, so y's deep aliases include everything x aliases at any level.

### `effects`, `rewrite`, `mirror`, `update`

Four staging-relevant methods:

- `effects: Effects` (`argon/src/argon/Op.scala:70`) — default is the fold `blocks.map(_.effects).fold(Effects.Pure){(a,b) => a andAlso b}`. Pure nodes keep the default. Effectful nodes override (e.g. `VarAssign.effects = Effects.Writes(v)` at `argon/src/argon/node/Var.scala:40`).
- `rewrite: R` (`argon/src/argon/Op.scala:72`) — default is `null.asInstanceOf[R]`, meaning "no rewrite". If overridden, staging calls it first in `register` and returns the rewritten subgraph if non-null (see `[[50 - Staging Pipeline]]`). The `@rig` annotation on this method injects an implicit `SrcCtx` and `State` — rewrites are stateful transforms, not pure functions.
- `mirror(f: Tx): Op[R]` (`argon/src/argon/Op.scala:73`) — default throws `"Use @op annotation or override mirror method..."`. The `@op` macro generates the correct override that walks constructor args and substitutes each.
- `update(f: Tx): Unit` (`argon/src/argon/Op.scala:74`) — default throws the same exception. The `@op` macro generates the mutating variant that re-substitutes fields in place.

The `Tx = TransformerInterface` alias (`argon/src/argon/Op.scala:14`) is a tiny single-method interface (`def apply[T](x: T): T`) that breaks a Scala-level cyclic dependency between `Op` and `transform.Transformer` (see `argon/src/argon/transform/TransformerInterface.scala:1-5`).

### Frequency hints (`Freq`)

`Freq` is a three-valued enum (`argon/src/argon/Freq.scala:3-14`): `Cold`, `Normal`, `Hot`. Meaning (from `Op.scala:32-34`): hot syms are preferred for early scheduling (moved out of blocks when possible); cold syms are preferred for late scheduling (kept inside blocks when possible); normal is the default. `Freq.combine` (`argon/src/argon/Freq.scala:7-13`) is asymmetric:

- `(Cold, _) → Cold`
- `(_, Cold) → Cold`
- `(Hot, _) → Hot`
- `(_, Hot) → Hot`
- `(Normal, Normal) → Normal`

The asymmetry is intentional but surprising when merging frequencies across multiple scopes. The `cold`/`normal`/`hot` helpers on `Op` (`argon/src/argon/Op.scala:76-78`) let an override tag specific inputs.

### `AtomicRead` mixin

`AtomicRead[M]` (`argon/src/argon/Op.scala:115-117`) is a marker trait with one field: `coll: Sym[M]`. It does not extend `Op` itself; it's mixed into node classes that "read through" a collection. The staging code at `argon/src/argon/static/Staging.scala:245-250` uses this to walk the dereference chain to the outermost mutable container when computing atomic-write propagation — see `[[30 - Effects and Aliasing]]`.

### Block structure and equality

`Block[R]` (`argon/src/argon/Block.scala:6-65`) is a `sealed class` with five fields: `inputs`, `stms`, `result`, `effects`, `options`. The constructor does not enforce any invariant on statement order (that's the scheduler's responsibility); it merely carries the result of scheduling.

`Block.equals` (`argon/src/argon/Block.scala:43-48`) compares `result`, `effects`, `inputs`, `options` — `stms` is deliberately excluded. `hashCode` (`argon/src/argon/Block.scala:42`) uses `(inputs, result, effects, options).hashCode`. Two blocks produced by different scheduler runs, with the same result/effects/inputs/options, are equal even with different statement orders.

### `Lambda1/2/3` subclasses

The three lambda classes (`argon/src/argon/Block.scala:67-94`) are `case class` subclasses of `Block[R]` that hoist the block's input syms into named fields:

- `Lambda1[A,R](input: Sym[A], stms, result, effects, options)` — exactly one input.
- `Lambda2[A,B,R](inputA, inputB, stms, result, effects, options)` — two inputs.
- `Lambda3[A,B,C,R](inputA, inputB, inputC, stms, result, effects, options)` — three inputs.

The lambda constructor passes `Seq(input...)` as the `inputs` parameter to the parent `Block` constructor. `asLambda1`/`asLambda2`/`asLambda3` on `Block` (`argon/src/argon/Block.scala:50-64`) are unsafe downcasts that assert `inputs.length == n` by indexing.

### `nestedStms` and `nestedInputs`

`Block.nestedStms` (`argon/src/argon/Block.scala:16-18`) is the transitive closure of statements: `stms ++ stms.flatMap{s => s.op.map{o => o.blocks.flatMap(_.nestedStms)}.getOrElse(Nil)}`.

`Block.nestedStmsAndInputs` (`argon/src/argon/Block.scala:22-37`) computes the (stms, nestedInputs) pair in one pass: `used = stms.flatMap{stm => stm.inputs ++ stm.blocks.map(_.result)} ++ inputs ++ syms(result)`; `made = stms.flatMap{s => s.op.map(_.binds).getOrElse(Set.empty) + s}`; `ins = (used diff made).filterNot(_.isValue)`. The `filterNot(_.isValue)` step strips `Const` and `Param` symbols from the input set — they are always "free" and do not need to be threaded in.

### `BlockOptions`

`BlockOptions(temp: Freq.Freq = Freq.Normal, sched: Option[Scheduler] = None)` (`argon/src/argon/BlockOptions.scala:5-8`). Two presets (`argon/src/argon/BlockOptions.scala:10-11`):

- `Normal = BlockOptions(Freq.Normal, None)` — default.
- `Sealed = BlockOptions(Freq.Cold, None)` — cold block where no motion should escape.

When `sched` is `Some(sched)`, that scheduler is used; otherwise the default (`SimpleScheduler`) is used. `temp = Freq.Cold` is also the signal `stageScope_Start` uses to suppress CSE across the block boundary — see `[[60 - Scopes and Scheduling]]`.

## Implementation

The helper functions used by `Op` for collecting syms / exps / blocks live in `argon/src/argon/static/Staging.scala:263-293`:

- `exps(a: Any*): Set[Sym[_]]` (`argon/src/argon/static/Staging.scala:263-272`) — walks nested Products, Iterables, Iterators, `Impure`, and `Block` result/antiDeps to collect all non-type exp syms.
- `syms(a: Any*): Set[Sym[_]]` (`argon/src/argon/static/Staging.scala:274-284`) — similar but includes bound syms and excludes type refs.
- `collectBlocks(a: Any*): Seq[Block[_]]` (`argon/src/argon/static/Staging.scala:286-293`) — similar, but returns `Block`s.

Each walks structurally. The crucial semantic for `Op.inputs` default is that `syms(productIterator)` traverses every constructor argument (via `Product.productIterator`) and every element of any `Iterable`/`Iterator` / `Product` inside. This means a node like `case class Foo(xs: Seq[Sym[_]])` correctly exposes each element of `xs` as an input.

`ExpMiscOps.inputs`/`blocks`/`nonBlockInputs` at `argon/src/argon/static/Implicits.scala:122-125` lift the `Op` methods to `Sym`-level, returning `Nil` when the sym has no op (constants/params/bounds have no `op`).

## Interactions

- **Symbols and Types** (see `[[10 - Symbols and Types]]`): an `Op[R]` is wrapped in `Def.Node(id, op)` at stage time. `Op.unapply` / `Stm.unapply` invert this (`argon/src/argon/Op.scala:119-125`).
- **Effects and Aliasing** (see `[[30 - Effects and Aliasing]]`): the alias categories drive `propagateWrites` and `checkAliases`; `effects` drives CSE eligibility and scheduling.
- **Staging Pipeline** (see `[[50 - Staging Pipeline]]`): `Op.rewrite` is invoked first in `register`; `Op.effects` is consumed in `computeEffects`; alias categories are consumed in the sym's metadata writes.
- **Transformers** (see `[[90 - Transformers]]`): `Op.mirror(f)` is the key extension point for IR traversal. `Op.update(f)` is used by `MutateTransformer` for in-place rewrite. Both are macro-generated by `@op`.

## HLS notes

The `Op` contract maps cleanly to a Rust `trait Op` or a sealed enum of ops. The reflective `productIterator` walk for defaults is not portable — Rust should require nodes to explicitly declare inputs / blocks via a derive macro or explicit method. The nine category methods all have clean Rust analogs (slices of `SymId`). `Freq`'s asymmetric combine is a small enum; reimplementation is trivial. `AtomicRead` becomes a trait bound or a separate classification.

Block equality excluding statements is usable if and only if the scheduler is deterministic (same inputs + result + effects + options ⇒ same stms). The current Argon scheduler (`SimpleScheduler`) is deterministic by construction.

## Open questions

- See `[[20 - Open Questions]]` Q-009: `Block.equals` excludes stms — is this relied on by `blockSubst` in `SubstTransformer`, or could it cause identity confusion in pipelines that swap schedulers?
