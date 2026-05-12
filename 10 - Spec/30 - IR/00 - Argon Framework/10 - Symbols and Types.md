---
type: spec
concept: Argon Symbols and Types
source_files:
  - "argon/src/argon/Ref.scala:17-180"
  - "argon/src/argon/Def.scala:5-45"
  - "argon/src/argon/State.scala:72-74"
  - "argon/src/argon/Invalid.scala:5-11"
  - "argon/src/argon/package.scala:1-14"
  - "argon/src/argon/static/Staging.scala:17-32"
  - "argon/src/argon/static/Implicits.scala:79-121"
source_notes:
  - "[[argon-framework]]"
hls_status: clean
depends_on:
  - "[[30 - Effects and Aliasing]]"
  - "[[20 - Ops and Blocks]]"
status: draft
---

# Argon Symbols and Types

## Summary

Argon's staged-IR representation is built from three traits — `ExpType[C,A]` (type evidence), `Exp[C,A]` (expression carrier), and `Ref[C,A]` (the combined staged-value class) — plus a six-case sealed ADT `Def[A,B]` describing the right-hand side of every staged expression. Type `A` is the Scala representation of a staged value (e.g. `Fix[TRUE, _32, _0]`), type `C` is the constant type used to represent it when it is a literal (e.g. `FixedPoint`). The type aliases `Sym[+S] = Exp[_, S]` and `Type[S] = ExpType[_, S]` in `argon/src/argon/package.scala:1-14` give the convenient narrow view used throughout the codebase. A global monotonic counter on `State` issues IDs that underpin equality for non-constant symbols.

## Syntax / API

All staged types subclass a concrete `Ref[C,A]` (via the `@ref` macro). Constructing a new symbol goes through one of the factory methods in `argon/src/argon/static/Staging.scala`:

- `const[A<:Sym[A]:Type](c: A#L)` and `parameter[A<:Sym[A]:Type](c: A#L)` — checked constant / parameter (`argon/src/argon/static/Staging.scala:9-12`).
- `uconst[A<:Sym[A]:Type](c: A#L)` — unchecked constant that does not require an implicit `State` (`argon/src/argon/static/Staging.scala:15`).
- `_const` / `_param` (private[argon]) — the low-level primitives that call `tp._new(Def.X, ctx)` (`argon/src/argon/static/Staging.scala:17-21`).
- `err[A:Type](msg)` / `err_[A](tp, msg)` — stage an error placeholder (`argon/src/argon/static/Staging.scala:23-24`).
- `boundVar[A:Type]` — allocate a bound symbol for use as a block/lambda input (`argon/src/argon/static/Staging.scala:26`).
- `symbol(tp, op)` — the private factory for `Def.Node` wrappers (`argon/src/argon/static/Staging.scala:28-32`).
- `proto[A](exp)` — sets `exp._rhs = Def.TypeRef` to mark a staged type prototype (`argon/src/argon/package.scala:13`).

Infix ops on `Sym`/`ExpType` are provided via `expOps`/`expTypeOps` implicit conversions (`argon/src/argon/static/Implicits.scala:37-38`) and expose `tp`, `rhs`, `ctx`, `name`, `isConst`/`isParam`/`isBound`/`isSymbol`/`isType`, `c` (the constant value, if any), `op` (the Op, if any), `inputs`, `blocks`, `consumers`, `=:=`/`<:<`, and the alias/metadata accessors.

## Semantics

### The six `Def` cases

`Def[A,B]` is sealed with six cases (`argon/src/argon/Def.scala:19-42`):

| Case | Carries ID? | Semantics |
|---|---|---|
| `TypeRef` | no | The symbol represents a staged type prototype (not a value). |
| `Error(id, msg)` | yes | Staging error; the symbol exists but should not flow. |
| `Bound(id)` | yes | Bound variable (block/lambda input). Not owned by any operation. |
| `Const(c)` | no | Immutable literal value of constant type `A`. |
| `Param(id, c)` | yes | Mutable literal (tunable for DSE). |
| `Node(id, op)` | yes | The symbol is the output of operation `op`. |

`Def` predicates `isValue`/`isConst`/`isParam`/`isBound`/`isNode`/`isError`/`isType` are the canonical per-symbol disambiguation API (`argon/src/argon/Def.scala:6-12`). `isValue = isConst || isParam` (`argon/src/argon/Def.scala:6`) is the test for "literal-ish" (no defining op, but carries a value). `Def.unapply` at `argon/src/argon/Def.scala:44` is a pattern-match shortcut: `case Def(op) => ...` extracts the op if the sym is a `Node`, matching the same path as `Exp.op` / `Op.unapply` (`argon/src/argon/Op.scala:119-121`).

### ID issuance

Four of the six `Def` cases carry an `id: Int`. IDs are monotonically issued from the global counter `State.nextId()` (`argon/src/argon/State.scala:72-74`) which starts at `-1` and increments on each call. Calls to `nextId` happen only at staging time inside `_param`, `err`, `err_`, `boundVar`, and `symbol` (`argon/src/argon/static/Staging.scala:20-31`). `Const(c)` does NOT get an ID: this makes two `Const(c)` with the same `c` and equal `tp` equal symbols, enabling constant folding and constant-based CSE.

### Equality / hashCode partitions by `Def` case

`Ref.hashCode` (`argon/src/argon/Ref.scala:148-155`) and `Ref.equals` (`argon/src/argon/Ref.scala:159-170`) dispatch on `this.rhs`:

- `Const(c)` compared by `tp =:= tp` AND `a == b` on the constant value, hashed by `c.hashCode()`.
- `Param`/`Node`/`Bound`/`Error` compared by `id`; hashed by `id`.
- `TypeRef` compared by `=:=` (structural type equality); hashed by `(_typePrefix, _typeArgs)`.

`Ref.canEqual` (`argon/src/argon/Ref.scala:157`) accepts any `Ref[_,_]`. `Ref.toString` follows the same case partition (`argon/src/argon/Ref.scala:172-179`): `Const(c)` → `"Const(escaped-c)"`, `Param(id,c)` → `"p$id (escaped-c)"`, `Node(id,_)` → `"x$id"`, `Bound(id)` → `"b$id"`, `Error` → `"<error>"`, `TypeRef` → `typeName` from the type ops.

A critical consequence: structurally-equal `Const`s with the same type compare equal, but structurally-equal non-`Const` symbols are equal only if they share the same issued ID. The compiler can never create two distinct symbols with the same non-`Const` `Def` — the ID is unique by construction.

### `ExpType.__value` and constant construction

`ExpType.value(c: Any): Option[(C, Boolean)]` handles boxed-Java-primitive unboxing and then delegates to an abstract `value(c)` (`argon/src/argon/Ref.scala:59-69`). The boolean in the returned pair indicates whether the conversion was **exact** (no loss of precision).

`ExpType.from(c, warnOnLoss, errorOnLoss, isParam, saturating, unbiased)` (`argon/src/argon/Ref.scala:74-94`) is the user-facing construction API. On non-exact conversion it can emit either a warning or an error depending on flags; on success it returns either `_const(this, v)` or `_param(this, v)` depending on `isParam`. `getFrom` (`argon/src/argon/Ref.scala:101-105`) is the exception-free variant.

## Implementation

### `Exp` is a var-heavy, half-initialized carrier

`Exp[C,A]` (`argon/src/argon/Ref.scala:119-137`) declares six `private[argon] var`s: `_tp: ExpType[C,A]`, `_rhs: Def[C,A]`, `_data: mutable.Map[Class[_],Data[_]]` (initialized empty), `_name: Option[String]` (initialized `None`), `_ctx: SrcCtx` (initialized `SrcCtx.empty`), `_prevNames: Seq[(String,String)]` (initialized `Nil`).

Construction goes through `ExpType._new` (`argon/src/argon/Ref.scala:42-48`):
```
val v = fresh
evRef(v).tp = this.tp
evRef(v).rhs = d
evRef(v).ctx = ctx
v
```

Between `fresh` and the three field writes, the returned instance has `_tp = null` and `_rhs = null`. `Implicits.scala:84-95` defines `ExpMiscOps.tp`/`rhs` getters that explicitly guard against these null states and throw `"Val references to tp in ${exp.getClass} should be lazy"`. This is a contract for user-defined `@ref` classes: any `val` field in the class that references `tp` or `rhs` must be lazily evaluated, or it will be read during the `fresh` call before `_new` finishes writing its `_tp`/`_rhs`.

### `Invalid`: the removed-symbol marker

`Invalid` (`argon/src/argon/Invalid.scala:5-11`) is an `@ref class` extending `Ref[Nothing, Invalid]`. The companion object is constructed as `Invalid("")` and its `rhs` is set to `Def.TypeRef` (`argon/src/argon/Invalid.scala:10`). Any substitution that resolves to `Invalid` triggers `Transformer.usedRemovedSymbol` (see `[[90 - Transformers]]`).

### The `Sym` and `Type` aliases

`argon/src/argon/package.scala:5-11` defines:
```
type Sym[+S] = Exp[_, S]
type Type[S] = ExpType[_, S]
object Type {
  def apply[A:Type]: Type[A] = implicitly[Type[A]]
  def m[A,B](tp: Type[A]): Type[B] = tp.asInstanceOf[Type[B]]
}
```

`Sym[+S]` abstracts over the constant type `C` — most of the compiler does not care about the constant representation and tracks only the Scala repr. `Type.m[A,B]` is an unsafe type cast used at staging time when the implementation knows the runtime class is right but the static types are too weak. `Type.apply[A:Type]` is the canonical summoner for an implicit `Type[A]`.

## Interactions

- **`Op`** (see `[[20 - Ops and Blocks]]`): every `Node(id, op)` symbol has its `op` retrievable via `sym.op` (`argon/src/argon/static/Implicits.scala:120`) or the `Op.unapply` pattern match (`argon/src/argon/Op.scala:119-121`). The `Def.unapply` on `argon/src/argon/Def.scala:44` exposes the same handle.
- **Effects and Aliasing** (see `[[30 - Effects and Aliasing]]`): each symbol stores its effects in metadata keyed off `Class[Effects]`. The `effects` getter returns `Effects.Pure` if unset (`argon/src/argon/static/Implicits.scala:153`).
- **Staging Pipeline** (see `[[50 - Staging Pipeline]]`): `symbol(tp, op)` at `argon/src/argon/static/Staging.scala:28-32` is the entry point for creating `Def.Node` symbols. All other `Def` cases are created via the helper methods above.
- **Transformers** (see `[[90 - Transformers]]`): `Ref.equals` by ID means two symbols created by sequential transformer passes are distinct. `mirror` must produce a new symbol; `update` preserves ID-identity.

## HLS notes

The `Sym` / `Def` separation translates directly to a Rust enum + pool-allocator pattern. The monotonic ID counter maps to a `SymId = u32` newtype. `Def::Const(c)` can remain a structural enum variant with content-based hashing; the four ID-bearing variants (`Error`, `Bound`, `Param`, `Node`) just hash by their ID. The half-initialized `Exp` problem disappears in Rust since we can construct the full struct literal in one expression. The `@ref` macro's contract (lazy tp/rhs evaluation) becomes a non-issue.

`Type[A]` as a Scala implicit is slightly awkward to replicate in Rust — a type-class via blanket impl or a runtime dictionary are two options. The `_typeArgs`/`_typeParams` reflection dance (`argon/src/argon/Ref.scala:31-38`) is used for structural type-equality; in Rust this would be replaced with a `TypeId`-style explicit tag or an interned type descriptor.

## Open questions

- See `[[20 - Open Questions]]` for related entries (Q-008, Q-009). The half-initialized `Exp` pattern deserves its own deep dive under the `@ref` macro umbrella (tracked for Phase 2 Forge work).
