---
type: spec
concept: Argon Transformers
source_files:
  - "argon/src/argon/transform/Transformer.scala:22-235"
  - "argon/src/argon/transform/SubstTransformer.scala:6-176"
  - "argon/src/argon/transform/ForwardTransformer.scala:8-96"
  - "argon/src/argon/transform/MutateTransformer.scala:8-67"
  - "argon/src/argon/transform/TransformerInterface.scala:1-5"
  - "argon/src/argon/node/Enabled.scala:6-21"
  - "argon/src/argon/Invalid.scala:5-11"
  - "argon/src/argon/Data.scala:36-61"
  - "argon/src/argon/Mirrorable.scala:1-8"
source_notes:
  - "[[argon-framework]]"
hls_status: rework
depends_on:
  - "[[50 - Staging Pipeline]]"
  - "[[20 - Ops and Blocks]]"
  - "[[10 - Symbols and Types]]"
status: draft
---

# Argon Transformers

## Summary

Argon's transformer stack is a three-level hierarchy. `Transformer` (base) provides the polymorphic `apply[T](x: T): T` walk that substitutes syms, blocks, products, collections, and `Mirrorable` values. `SubstTransformer` adds scoped substitution maps (`subst: Map[Sym[_], Substitution]`, `blockSubst: Map[Block[_], Block[_]]`) with `isolateSubst` / `excludeSubst` scope helpers and lambda-to-function conversions. `ForwardTransformer` extends `SubstTransformer` with a visit rule that mirrors every statement by default (`createSubstRule`). `MutateTransformer` extends `ForwardTransformer` with an in-place `update` pathway (`copyMode` flag, `Enabled` node dispatch). Transformers are the primary way a pass rewrites the IR between pipeline stages in Spatial.

## Syntax / API

### `TransformerInterface`

A one-method trait at `argon/src/argon/transform/TransformerInterface.scala:1-5`:
```scala
trait TransformerInterface {
  def apply[T](x: T): T
}
```

Exists only to break a compile-time circular dependency between `Op` (which needs to refer to a transformer parameter type `Tx`) and `Transformer` (which depends on `Op`). `Op.Tx = TransformerInterface` at `argon/src/argon/Op.scala:14`.

### `Transformer`

Abstract class at `argon/src/argon/transform/Transformer.scala:22-235`. Extends `Pass with TransformerInterface`.

Key members:

- `f: Transformer = this` (`argon/src/argon/transform/Transformer.scala:23`) — reference-to-self for closures.
- `object F { def unapply[T](x: T): Option[T] = Some(f(x)) }` (`argon/src/argon/transform/Transformer.scala:26-29`) — pattern-match helper: `case F(y) => ...` equivalent to `val y = f(x)`.
- `usedRemovedSymbol[T](x: T): Nothing` (`argon/src/argon/transform/Transformer.scala:32-35`) — throws when an `Invalid` surfaces through substitution.
- `apply[T](x: T): T` (`argon/src/argon/transform/Transformer.scala:40-70`) — the polymorphic dispatcher (see below).
- `substituteSym[T](s: Sym[T]): Sym[T]` (abstract, `argon/src/argon/transform/Transformer.scala:73`) — subclass-defined per-sym substitution.
- `substituteBlock[T](b: Block[T]): Block[T]` (abstract, `argon/src/argon/transform/Transformer.scala:76`) — subclass-defined per-block substitution.
- `inlineBlock[T](b: Block[T]): Sym[T]` (abstract, `argon/src/argon/transform/Transformer.scala:91`) — subclass-defined "re-stage this block in the current scope".
- `inlineWith[T](b)(t)` (`argon/src/argon/transform/Transformer.scala:81-86`) — helper that indents the log and calls `t(b.stms)`.
- `transferData(src, dest)` / `transferDataToAll(src)(scope)` / `transferDataIfNew(src, dest)` / `transferDataToAllNew(src)(scope)` (`argon/src/argon/transform/Transformer.scala:99-134`).
- `mirror[A](lhs: Sym[A], rhs: Op[A]): Sym[A]` (`argon/src/argon/transform/Transformer.scala:146-156`) — re-stage a mirrored node.
- `mirrorNode[A](rhs: Op[A]): Op[A]` (`argon/src/argon/transform/Transformer.scala:158`) — default `rhs.mirror(f)`.
- `mirrorMirrorable(x: Mirrorable[_]): Mirrorable[_]` (`argon/src/argon/transform/Transformer.scala:160-162`).
- `mirrorProduct[T<:Product](x: T): T` (`argon/src/argon/transform/Transformer.scala:163-178`) — reflective case-class mirror.
- `removeSym(sym)` (`argon/src/argon/transform/Transformer.scala:183-186`).
- `preprocess[R](block)` (`argon/src/argon/transform/Transformer.scala:229-233`) — clears `state.cache`, invalidates `globals`.
- `blockToFunction0[R](b)` / `lambda{1,2,3}ToFunction{1,2,3}` (`argon/src/argon/transform/Transformer.scala:222-225`) — block-to-Scala-function conversion.

### `SubstTransformer`

Abstract at `argon/src/argon/transform/SubstTransformer.scala:19-177`. Adds:

- `var subst: Map[Sym[_], Substitution]` at `argon/src/argon/transform/SubstTransformer.scala:24`. `Substitution` is one of `DirectSubst(v: Sym[_])` or `FuncSubst(func: () => Sym[_])` (`argon/src/argon/transform/SubstTransformer.scala:6-16`).
- `var blockSubst: Map[Block[_], Block[_]]` at `argon/src/argon/transform/SubstTransformer.scala:21`.
- `register(orig, sub)` and overloads (`argon/src/argon/transform/SubstTransformer.scala:41-62`).
- `substituteSym[T](s)` concrete (`argon/src/argon/transform/SubstTransformer.scala:65-70`).
- `substituteBlock[T](b)` concrete (`argon/src/argon/transform/SubstTransformer.scala:72-79`) — uses `blockSubst` or falls through to `isolateSubst(b.result) { stageScope(f(b.inputs), b.options){ inlineBlock(b) } }`.
- `isolateSubst(escape*)(scope)` (`argon/src/argon/transform/SubstTransformer.scala:122`).
- `isolateSubstIf(cond, escape)(block)` (`argon/src/argon/transform/SubstTransformer.scala:105-116`).
- `isolateSubstWith(escape, rules*)(scope)` variants (`argon/src/argon/transform/SubstTransformer.scala:85-98`).
- `excludeSubst(exclude*)(block)` (`argon/src/argon/transform/SubstTransformer.scala:131-136`).
- `saveSubsts()` / `restoreSubsts(bundle)` (`argon/src/argon/transform/SubstTransformer.scala:38-39`).

### `ForwardTransformer`

Abstract at `argon/src/argon/transform/ForwardTransformer.scala:8-96`. Adds:

- `recurse = Recurse.Never` (`argon/src/argon/transform/ForwardTransformer.scala:9`) — visit drives traversal.
- `transform[A:Type](lhs, rhs)(ctx)` (`argon/src/argon/transform/ForwardTransformer.scala:22-24`) — default: `mirror(lhs, rhs)`.
- `createSubstRule[A:Type](lhs, rhs)(ctx)` final (`argon/src/argon/transform/ForwardTransformer.scala:26-53`).
- `inlineBlock[T](b)` (`argon/src/argon/transform/ForwardTransformer.scala:58-61`) — `stms.foreach(visit); f(b.result)`.
- `visit[A](lhs, rhs)` final (`argon/src/argon/transform/ForwardTransformer.scala:63-67`).
- `visitBlock[R](block)` final (`argon/src/argon/transform/ForwardTransformer.scala:69-74`).
- `withEns[T](ens: Set[Bit])(thunk)` (`argon/src/argon/transform/ForwardTransformer.scala:85-91`).
- `var enables: Set[Bit] = Set.empty` (`argon/src/argon/transform/ForwardTransformer.scala:83`).

### `MutateTransformer`

Abstract at `argon/src/argon/transform/MutateTransformer.scala:8-67`. Adds:

- `recurse = Recurse.Default` (`argon/src/argon/transform/MutateTransformer.scala:9`).
- `copyMode: Boolean = false` (`argon/src/argon/transform/MutateTransformer.scala:12`) — toggle: `true` → fall back to `mirror`; `false` → `update`.
- `inCopyMode[A](copy: Boolean)(block)` (`argon/src/argon/transform/MutateTransformer.scala:14-20`) — scoped copyMode toggle.
- `transform[A:Type](lhs, rhs)(ctx)` override (`argon/src/argon/transform/MutateTransformer.scala:32-34`): `update(lhs, rhs)`.
- `blockToFunction0[R](b)` override (`argon/src/argon/transform/MutateTransformer.scala:36-40`) — forces `copyMode = true`.
- `update[A](lhs, rhs)` final (`argon/src/argon/transform/MutateTransformer.scala:43-54`).
- `updateNode[A](node)` (`argon/src/argon/transform/MutateTransformer.scala:56-61`) — special-cases `Enabled[_]`.
- `mirrorNode[A](rhs)` override (`argon/src/argon/transform/MutateTransformer.scala:63-66`) — special-cases `Enabled[_]`.

## Semantics

### `Transformer.apply` — the polymorphic substitution walk

`apply[T](x: T): T` at `argon/src/argon/transform/Transformer.scala:40-70` dispatches on the runtime type of `x`:

| Case | Action |
|---|---|
| `Mirrorable[_]` | `mirrorMirrorable(x)` — delegates to `x.mirror(f)`. |
| `Sym[_]` | `substituteSym(x)` — abstract; `SubstTransformer` looks up in `subst`. |
| `Lambda1[a,_]` | `substituteBlock(x).asLambda1[a]`. |
| `Lambda2[a,b,_]` | `substituteBlock(x).asLambda2[a,b]`. |
| `Lambda3[a,b,c,_]` | `substituteBlock(x).asLambda3[a,b,c]`. |
| `Block[_]` | `substituteBlock(x)`. |
| `Option[_]` | `x.map{this.apply}`. |
| `Seq[_]` | `x.map{this.apply}`. |
| `Map[_,_]` | `x.map{case (k,v) => f(k) -> f(v)}`. |
| `mutable.Map[_,_]` | same. |
| `Product` | `mirrorProduct(x)` — reflective constructor invocation. |
| `Iterable[_]` | `x.map{this.apply}`. |
| primitives (`Char`/`Byte`/`Short`/`Int`/`Long`/`Float`/`Double`/`Boolean`/`String`) | identity. |
| otherwise | warn if `config.enDbg`, return `x` as-is. |

After the dispatch, if the result `y.isInstanceOf[Invalid]`, `usedRemovedSymbol(x)` throws (`argon/src/argon/transform/Transformer.scala:68`). This is the central safety net: no dead sym flows through silently.

### `mirrorProduct` and `@op`

`mirrorProduct[T<:Product](x)` at `argon/src/argon/transform/Transformer.scala:163-178` uses Java reflection to call the case class's first public constructor with each productIterator value substituted via `f(_)`. Comment: `"this only works if the case class has no implicit parameters!"`. This is the contract for `@op`: the macro generates a `mirror(f): Op[R]` override that does the substitution explicitly, avoiding reflection. Without `@op`, `Op.mirror` throws `"Use @op annotation or override mirror method..."` at `argon/src/argon/Op.scala:73`.

`mirror[A](lhs: Sym[A], rhs: Op[A])` at `argon/src/argon/transform/Transformer.scala:146-156`:
```
val op2 = mirrorNode(rhs)                      // = rhs.mirror(f)
tA.boxed( stageWithFlow(op2){lhs2 => transferDataIfNew(lhs, lhs2) } )
```

The staging trail: `mirrorNode` produces a substituted op, `stageWithFlow` registers it (possibly triggering CSE against existing syms), and `transferDataIfNew` copies metadata from the old lhs to the new lhs2 (see below).

### Metadata transfer: `Transfer.Mirror` / `Remove` / `Ignore`

`transferData(src, dest)` at `argon/src/argon/transform/Transformer.scala:99-109`:
```
dest.name = src.name
if (dest != src) dest.prevNames = (state.paddedPass(pass-1), s"$src") +: src.prevNames
metadata.all(src).toList.foreach{case (k,m) => m.transfer match {
  case Transfer.Mirror => metadata.add(dest, k, mirror(m))
  case Transfer.Remove => metadata.remove(dest, k)
  case Transfer.Ignore =>
}}
```

Three fates (defined at `argon/src/argon/Data.scala:47-60`):

- `Mirror` → `metadata.add(dest, k, mirror(m))` (the `Data[T].mirror(f)` rule runs; `Data.mirror` default is `this.asInstanceOf[T]`, unchanged).
- `Remove` → `metadata.remove(dest, k)` (drop it). Comment at `argon/src/argon/transform/Transformer.scala:106`: `"very bug prone -- Since memories are visited before their users, this wipes all relevant metadata (i.e. readers, writers)"`.
- `Ignore` → do nothing. `Effects`, `ShallowAliases`, `DeepAliases` all use `Ignore` because they are always set by `register` in `[[50 - Staging Pipeline]]`.

`transferDataIfNew(src, dest)` at `argon/src/argon/transform/Transformer.scala:120-129` adds an "only if `dest.id >= src.id`" guard (using `rhs.getID`) before calling `transferData`. This avoids transferring old metadata back onto a newly-CSE'd older sym.

`transferDataToAll(src)(scope)` / `transferDataToAllNew(src)(scope)` at `argon/src/argon/transform/Transformer.scala:111-134` install a temporary flow rule inside `scope` that runs `transferData(src, dest)` on every newly-staged sym. Handy for cloning metadata across an entire inlined block.

### `SubstTransformer.isolateSubst`: subtractive scope

`isolateSubstIf(cond, escape)(block)` at `argon/src/argon/transform/SubstTransformer.scala:105-116`:
```
val save = subst
val result = block
if (cond) subst = save ++ subst.filter{case (s1,_) => escape.contains(s1) }
result
```

Inside `block`, `subst` may be extended freely. After `block`, if `cond`:
- Any rules with keys NOT in `escape` are discarded (the `save` is restored first, then only `escape` keys from the inner state are kept).
- Any rules with keys in `escape` ARE preserved (opt-in export).

So `isolateSubst(b.result){ stageScope(f(b.inputs), b.options){ inlineBlock(b) } }` at `argon/src/argon/transform/SubstTransformer.scala:76-78` lets the block's internal substitutions flow out only for `b.result` — other internal subst rules are discarded.

`excludeSubst(exclude*)(block)` at `argon/src/argon/transform/SubstTransformer.scala:131-136`:
```
val save = subst
val result = block
subst = save ++ subst.filterNot{case (s,_) => exclude.contains(s)}
result
```

The dual: keeps EVERY rule added inside except those with keys in `exclude`.

### Lambda-to-function conversion

`SubstTransformer.lambda1ToFunction1` at `argon/src/argon/transform/SubstTransformer.scala:145-151`:
```
{a: A => isolateSubst() {
  register(lambda1.input -> a)
  val block = blockToFunction0(lambda1)
  block()
}}
```

Converts a `Lambda1[A,R]` to a `Scala` function `A => R`. Each call:
1. Opens a fresh `isolateSubst` (no escapees, so all inner subst is discarded after).
2. Registers `lambda1.input -> a` (the input becomes `a`).
3. Delegates to `blockToFunction0(lambda1)` (returns a `() => R`).
4. Invokes the resulting function.

Similarly for `lambda2ToFunction2` / `lambda3ToFunction3` at `argon/src/argon/transform/SubstTransformer.scala:152-170`.

### `ForwardTransformer.createSubstRule`

At `argon/src/argon/transform/ForwardTransformer.scala:26-53`:

```
val lhs2: Sym[A] = if (!subst.contains(lhs)) {
  // Untransformed case
  val lhs2 = transform(lhs, rhs)
  subst.get(lhs) match {
    case Some(DirectSubst(lhs3)) if lhs2 != lhs3 =>
      throw new Exception(s"Conflicting substitutions: ...")
    case _ => lhs2
  }
} else {
  // Pre-transformed case
  val lhs2: Sym[A] = f(lhs)
  val lhs3: Sym[A] = mirrorSym(lhs2)
  if (lhs3 != lhs2 && lhs != lhs2) removeSym(lhs2)
  lhs3
}
if (lhs2 != lhs) register(lhs -> lhs2)
```

Two cases:

1. **Untransformed**: no existing rule. Call `transform(lhs, rhs)` (default `mirror`) to get `lhs2`. If `transform` itself added a `DirectSubst(lhs3)` where `lhs3 != lhs2`, throw a conflict error. Otherwise, return `lhs2`.
2. **Pre-transformed**: the lhs already has a subst rule. Apply it (`f(lhs) = lhs2`), then mirror `lhs2` to `lhs3`. If mirroring actually changed `lhs2` (`lhs3 != lhs2`) AND the lhs itself moved (`lhs != lhs2`), remove the intermediate `lhs2`. The "pre-transformed case" exists because the same lhs can be visited multiple times — e.g. if a higher scope pre-transformed a nested block, the inner visit will find an existing rule.

Finally: if `lhs2 != lhs`, register `lhs -> lhs2`.

### `MutateTransformer.update`

At `argon/src/argon/transform/MutateTransformer.scala:43-54`:
```
if (copyMode) mirror(lhs, rhs) else {
  updateNode(rhs)
  restageWithFlow(lhs){lhs2 => transferDataIfNew(lhs, lhs2) }
}
```

If `copyMode` is on (e.g. inside a `blockToFunction0` inlining), fall back to `mirror` (`argon/src/argon/transform/MutateTransformer.scala:36-40` forces this during block-inline).

Otherwise: `updateNode(rhs)` mutates the op's fields in place, then `restageWithFlow(lhs)` re-registers the sym in the current scope (see `[[50 - Staging Pipeline]]`). The `transferDataIfNew` flow rule copies any missing metadata.

### `updateNode` and `mirrorNode` dispatch for `Enabled`

`Enabled[R]` at `argon/src/argon/node/Enabled.scala:6-22` is a trait mixed into nodes with `ens: Set[Bit]` (predicates):
```scala
trait Enabled[R] { this: Op[R] =>
  var ens: Set[Bit]

  def mirrorEn(f: Tx, addEns: Set[Bit]): Op[R] = {
    val saveEns = ens
    ens ++= addEns
    val op2 = this.mirror(f)
    ens = saveEns
    op2
  }

  def updateEn(f: Tx, addEns: Set[Bit]): Unit = {
    ens ++= addEns
    this.update(f)
  }
}
```

`MutateTransformer.updateNode` (`argon/src/argon/transform/MutateTransformer.scala:56-61`):
```
case enabled: Enabled[_] => enabled.updateEn(f, f(enables))
case _                    => node.update(f)
```

`MutateTransformer.mirrorNode` (`argon/src/argon/transform/MutateTransformer.scala:63-66`):
```
case en: Enabled[A] => en.mirrorEn(f, f(enables))
case _              => super.mirrorNode(rhs)  // = rhs.mirror(f)
```

The `f(enables)` call re-substitutes the current enables set (from `ForwardTransformer.enables`) through `f`, then unions with the node's existing `ens`. This is how control-dependent nodes inherit enabling predicates.

## Implementation

### `preprocess` clears global state

`Transformer.preprocess[R](block)` at `argon/src/argon/transform/Transformer.scala:229-233`:
```
state.cache = Map.empty              // Clear CSE cache prior to transforming
globals.invalidateBeforeTransform()  // Reset unstable global metadata
block
```

Two resets:

1. `state.cache = Map.empty` — CSE cache from the previous pipeline stage is thrown away. The new transformer's output uses a fresh cache, so CSE hits are only computed among syms from this pass's work.
2. `globals.invalidateBeforeTransform()` at `argon/src/argon/GlobalMetadata.scala:19-26` drops every `Data[_]` entry in `State.globals` whose `transfer == Transfer.Remove`. `Transfer.Mirror` and `Transfer.Ignore` entries stay.

`SubstTransformer.preprocess` (`argon/src/argon/transform/SubstTransformer.scala:172-175`) additionally resets `subst = Map.empty`.

### `removeSym`

`removeSym(sym)` at `argon/src/argon/transform/Transformer.scala:183-186`:
```
state.scope = state.scope.filterNot(_ == sym)
state.impure = state.impure.filterNot(_.sym == sym)
```

Surgically removes a sym from the CURRENT scope's bundle. Does not affect outer scopes. Used by `ForwardTransformer.createSubstRule` (`argon/src/argon/transform/ForwardTransformer.scala:49`) to clean up an intermediate sym that got re-mirrored.

### `blockToFunction0` override stack

Two different definitions, depending on the layer:

1. `Transformer.blockToFunction0[R](b): () => R = () => inlineBlock(b).unbox` (`argon/src/argon/transform/Transformer.scala:222`).
2. `SubstTransformer.blockToFunction0[R](b): () => R = () => isolateSubst(){ inlineBlock(b).unbox }` (`argon/src/argon/transform/SubstTransformer.scala:139-143`). Wraps in `isolateSubst()` (no escapees) so that every inline resets subst after.
3. `MutateTransformer.blockToFunction0[R](b): () => R = () => isolateSubst(){ inCopyMode(copy = true){ inlineBlock(b).unbox } }` (`argon/src/argon/transform/MutateTransformer.scala:36-40`). Additionally sets `copyMode = true` during the inline.

This asymmetry — outer updates in place, inline copies — is easy to miss. A `MutateTransformer` user who calls `lambda.toFunction0()()` from outside a block context expects UPDATE semantics but gets COPY semantics.

### `Mirrorable`

`trait Mirrorable[A] { type Tx = Transformer; def mirror(f: Tx): A }` at `argon/src/argon/Mirrorable.scala:1-9`. Note the `Tx = Transformer` here is the full `Transformer` class, NOT `TransformerInterface`. This is used for non-Op values that still need to participate in substitution (e.g., lambda carriers, pass-specific data structures). `Transformer.apply` dispatches `Mirrorable` before `Sym`, so the custom rule runs first.

## Interactions

- **Staging Pipeline** (see `[[50 - Staging Pipeline]]`): `mirror` calls `stageWithFlow(mirrorNode(rhs))`; `update` calls `restageWithFlow(lhs)`. Both go through `register`. `mirrorProduct` relies on `@op`-generated `Op.mirror` (or pure case-class construction).
- **Scopes and Scheduling** (see `[[60 - Scopes and Scheduling]]`): `substituteBlock` calls `stageScope(f(b.inputs), b.options){ inlineBlock(b) }` — this creates a new bundle. `preprocess` clears the outer CSE cache.
- **Ops and Blocks** (see `[[20 - Ops and Blocks]]`): `mirrorSym` is the Sym-level counterpart to `mirrorNode`. `Lambda1/2/3.asLambda{1,2,3}` casts after `substituteBlock`.
- **Spatial transforms** (downstream, separate spec): most Spatial transforms extend `ForwardTransformer` or `MutateTransformer`. `UnrollingTransformer`, `SwitchTransformer`, `RetimingTransformer`, etc.

## HLS notes

Three rework risks for HLS port (tagged `hls_status: rework`):

1. **Reflective `mirrorProduct`** (`argon/src/argon/transform/Transformer.scala:163-178`): uses JVM reflection. A Rust port must replace with derive-macro-generated `mirror` methods. The `@op` contract is what Scala relies on; Rust would use `#[derive(Op)]`.
2. **`Mirrorable.Tx = Transformer`** vs `Op.Tx = TransformerInterface`: two different `Tx` type aliases for what is effectively the same object. This circular-dependency workaround is Scala-specific.
3. **`subst: Map[Sym[_], Substitution]`**: the two-variant `Substitution` (`DirectSubst(sym)` or `FuncSubst(() => sym)`) is a fine design. Rust can use a `Substitution` enum trivially.

The `isolateSubst` / `excludeSubst` subtractive-scope pattern translates cleanly. The `Transfer.{Mirror, Remove, Ignore}` trichotomy also maps cleanly. The `ForwardTransformer.createSubstRule` dance, though, is subtle and needs careful review — the comment in the Scala code flagging the "pre-transformed case" should be transplanted verbatim.

## Open questions

- See `[[20 - Open Questions]]` Q-010: `createSubstRule` pre-transformed case removes the intermediate only under `lhs3 != lhs2 && lhs != lhs2`. Could the edge case `lhs == lhs2` with `lhs3 != lhs2` leak?
- See `[[20 - Open Questions]]` Q-011: `MutateTransformer.mirrorNode`/`updateNode` dispatch on `Enabled` uses `f(enables)` each time. Does double-mirroring accumulate enables unexpectedly?
