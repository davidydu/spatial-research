---
type: spec
concept: spatial-ir-counters-iterators
source_files:
  - "src/spatial/node/Control.scala:9-19"
  - "src/spatial/node/LaneStatic.scala:1-15"
  - "src/spatial/lang/Counter.scala:1-29"
  - "src/spatial/lang/CounterChain.scala:1-13"
  - "src/spatial/lang/control/ForeachClass.scala:26-33"
  - "src/spatial/lang/control/ReduceClass.scala:38-51"
  - "src/spatial/lang/control/MemReduceClass.scala:55-91"
  - "src/spatial/metadata/control/ControlData.scala:38-39"
  - "src/spatial/metadata/control/ControlData.scala:128-142"
  - "src/spatial/metadata/control/package.scala:980-1001"
  - "src/spatial/metadata/control/package.scala:1003-1083"
  - "src/spatial/metadata/control/package.scala:1086-1102"
  - "src/spatial/transform/unrolling/UnrollingBase.scala:455-487"
  - "src/spatial/transform/unrolling/UnrollingBase.scala:100-112"
  - "src/spatial/rewrites/CounterIterRewriteRule.scala:1-51"
  - "src/spatial/traversal/CounterIterSynchronization.scala:13"
  - "src/spatial/transform/UnitPipeToForeachTransformer.scala:23"
  - "src/spatial/transform/UnitIterationElimination.scala:13"
  - "src/spatial/util/TransformUtils.scala:48"
  - "src/spatial/node/HierarchyControl.scala:50-52"
  - "argon/src/argon/node/DSLOp.scala:29-37"
source_notes:
  - "[[spatial-ir-nodes]]"
hls_status: rework
depends_on:
  - "[[10 - Controllers]]"
status: draft
---

# Counters and Iterators (IR nodes)

## Summary

Spatial's loop iteration space is built from three IR allocation nodes — `CounterNew`, `CounterChainNew`, `ForeverNew` (all in `src/spatial/node/Control.scala:9-19`) — plus the per-iterator metadata `IndexCounterInfo` (`src/spatial/metadata/control/ControlData.scala:38-39`) which binds a loop-induction variable (`I32` symbol) to the counter that produces it. A counter expresses a `start`/`end`/`step`/`par` parametric range; a counter chain bundles counters in lexicographic-outer-to-inner order; an iterator is a fresh `boundVar[I32]` paired with one counter via `IndexCounterInfo`. After unrolling, the per-lane index identity is captured by `LaneStatic` (`src/spatial/node/LaneStatic.scala:1-15`), a transient primitive that names a lane's static slot in the post-unroll IR. For the HLS rewrite, the `start/end/step/par` shape is HLS-friendly but the iter ↔ counter binding metadata is Spatial-specific and must be reproduced as either a typed iterator handle or per-controller schedule annotations.

## Syntax / API

- `Counter[A](start, end, step = one, par = I32(1))` (`src/spatial/lang/Counter.scala:14-23`) → `stage(CounterNew[A](start, end, stride, par))`. `step` defaults to `Num[A].one`; `par` defaults to `I32(1)`.
- `Counter.from(series)` (`Counter.scala:25-28`) — destructures a `Series[A]` into the four-arg form.
- `CounterChain(ctrs)` (`src/spatial/lang/CounterChain.scala:11-12`) → `stage(CounterChainNew(ctrs))`.
- `Forever()` (no DSL constructor in `Counter.scala`; produced internally for unbounded streams) → `ForeverNew()`. Returns a `Counter[I32]` whose `start`/`step`/`end` are virtual: see `src/spatial/metadata/control/package.scala:1010-1015` (`start = I32(0)`, `step = I32(1)`, `end = boundVar[I32]`, `ctrPar = I32(1)`, `ctrWidth = 32`).
- Iterators are minted by each control DSL helper: `iters = ctrs.map{_ => boundVar[I32]}` (`src/spatial/lang/control/ForeachClass.scala:27`), then bound via `i.counter = IndexCounterInfo(ctr, Seq.tabulate(ctr.ctrParOr1){i => i})` (line 29). Same pattern in `ReduceClass.scala:44`, `MemReduceClass.scala:61-62`.
- `LaneStatic[A](iter, elems: Seq[Int])` (`src/spatial/node/LaneStatic.scala:7`) — a primitive that names the per-lane static value of an iterator after unrolling. Produced by the `CounterIterRewriteRule` (`src/spatial/rewrites/CounterIterRewriteRule.scala:18-37`) when it spots `(iter % par)` patterns over a fully-bound iterator.

## Semantics

### `CounterNew[A:Num]`

```scala
@op case class CounterNew[A:Num](start: Num[A], end: Num[A], step: Num[A], par: I32) extends Alloc[Counter[A]] {
  val A: Num[A] = Num[A]
  override def effects: Effects = Effects.Unique
}
```
(`src/spatial/node/Control.scala:9-12`).

- `start`, `end`, `step`: typed `Num[A]` symbols. `A` is the counter's element numeric type — typically `I32` but `Num[_]` lets fixed-point widths through.
- `par: I32` — parallelization factor. `par > 1` means the iterator should produce `par` lanes simultaneously when the loop is unrolled.
- `Effects.Unique` — the allocation must survive CSE (`Control.scala:11`). Two textually-identical counters with the same `start/end/step/par` must remain as distinct nodes; identity matters for downstream metadata (counter ↔ iter binding, counter ↔ owner controller).
- Extends `argon.node.Alloc[Counter[A]]` (`argon/src/argon/node/DSLOp.scala:29-31`) — so a counter is an allocation, not a primitive. The DSL surface type `Counter[A]` is `Top[Counter[A]] with Ref[FixedPointRange, Counter[A]]` (`src/spatial/lang/Counter.scala:9`).

### `ForeverNew()`

```scala
@op case class ForeverNew() extends Alloc[Counter[I32]] {
  override def effects: Effects = Effects.Unique
}
```
(`src/spatial/node/Control.scala:13-15`).

A nullary counter representing an unbounded loop. The `isForever` predicate (`src/spatial/metadata/control/package.scala:304-306`) detects when a control or counterchain contains a `ForeverNew`. When `isForever`, every per-counter metadata accessor short-circuits to a synthetic value (`start = I32(0)`, `step = I32(1)`, `end = boundVar[I32]`, `ctrPar = I32(1)`, `ctrWidth = 32`, `ctrParOr1 = 1`; see `package.scala:1010-1015, 1082-1083`). Forever counters never fully unroll (`willFullyUnroll = false`; `package.scala:1060-1066`).

### `CounterChainNew(counters: Seq[Counter[_]])`

```scala
@op case class CounterChainNew(counters: Seq[Counter[_]]) extends Alloc[CounterChain] {
  override def effects: Effects = Effects.Unique
}
```
(`src/spatial/node/Control.scala:17-19`).

A chain holds counters in **outer-to-inner lexicographic order**: index 0 is the outermost loop dimension. `CounterChain` is the surface type; each control node references a `(CounterChain, Seq[I32])` pair via `cchains` (`src/spatial/node/HierarchyControl.scala:51`). The iterators in the second slot must be 1-1 with the counters: `cchain.counters.zip(iters)` is the canonical pairing pattern (every site in `src/spatial/lang/control/*` and `src/spatial/transform/StreamTransformer.scala:45,62`).

`Effects.Unique` — same rationale as `CounterNew`. Banking analysis keys off counter-chain identity, not structural equality.

### Iterators (loop-induction variables)

An iterator is a `boundVar[I32]` produced by the DSL helper for each loop dimension. It carries no syntactic IR node of its own — the symbol is bound, not staged. Its identity-binding to the counter is via metadata:

```scala
case class IndexCounterInfo[A](ctr: Counter[A], lanes: Seq[Int])
case class IndexCounter(info: IndexCounterInfo[_]) extends Data[IndexCounter](SetBy.Analysis.Self)
case class IterInfo(iter: Sym[_]) extends Data[IterInfo](SetBy.Analysis.Self)
```
(`src/spatial/metadata/control/ControlData.scala:38-39, 136, 142`).

The bidirectional setter (`src/spatial/metadata/control/package.scala:1086-1102`) writes both directions atomically:
```scala
def counter_=(info: IndexCounterInfo[_]): Unit = {
  metadata.add(i, IndexCounter(info))
  metadata.add(info.ctr, IterInfo(i))
}
```

`IndexCounterInfo.lanes: Seq[Int]` is the **lane-index map**. Pre-unroll, `lanes = Seq.tabulate(ctr.ctrParOr1){i => i}` — the identity map `[0, 1, …, par-1]`. Post-unroll, the unroller rewrites it to a per-lane subset (see [Implementation](#implementation)).

`Control.binds = super.binds ++ iters.toSet` and `Control.inputs = super.inputs diff iters` (`src/spatial/node/HierarchyControl.scala:48-49`) — iterators are bound at the controller scope and are not dataflow inputs of the container.

### `LaneStatic[A](iter, elems)`

```scala
@op case class LaneStatic[A:Bits](iter: A, elems: Seq[scala.Int]) extends Primitive[A] {
  override val isTransient: Boolean = true

  @stateful def simplify[A:Bits](x: A, value: scala.Int): A = x.from(value)

  @rig override def rewrite: A = if (elems.size == 1) simplify(iter, elems.head) else super.rewrite
}
```
(`src/spatial/node/LaneStatic.scala:7-15`).

`elems` is a sequence of integer constants — one per lane. After unrolling, `LaneStatic(iter, Seq(0, 1, 2, 3))` represents "this iterator's lane index is one of 0, 1, 2, 3". The rewrite rule folds the single-lane case to a constant via `iter.from(elems.head)`. `isTransient = true` means the node disappears after retiming/codegen.

The `CounterIterRewriteRule` (`src/spatial/rewrites/CounterIterRewriteRule.scala:18-37`) inserts `LaneStatic` for three modular-arithmetic patterns over a fully-bound pre-unroll iterator:
1. `iter % par` when `start == 0` and `step == 1`.
2. `(iter / step) % par` when `start == 0`.
3. `((iter - start) / step) % par` (general case).
Each match stages `LaneStatic(iter, List.tabulate(par){i => i})`. The matcher requires the iterator to satisfy `PreunrollIter` (lines 42-50): bound, with an `IndexCounterInfo` whose lanes count equals `par`.

## Implementation

### Class hierarchy

```
argon.node.DSLOp[T]               (argon/src/argon/node/DSLOp.scala:6-9)
  argon.node.Alloc[T]             (argon/src/argon/node/DSLOp.scala:29-31)
    spatial.node.CounterNew[A]    (Control.scala:9-12)
    spatial.node.ForeverNew       (Control.scala:13-15)
    spatial.node.CounterChainNew  (Control.scala:17-19)

argon.node.Primitive[A]
  spatial.node.LaneStatic[A]      (LaneStatic.scala:7)
```

All three counter-family allocations declare `Effects.Unique`. `LaneStatic` is `Primitive` with `isTransient = true`.

### Helper accessors

`src/spatial/metadata/control/package.scala:980-1001` (CounterChain) and `1004-1083` (Counter) define the canonical accessor surface:

- `cchain.counters: Seq[Counter[_]]` (line 986) — destructures the `CounterChainNew.counters`.
- `cchain.pars: Seq[I32]`, `cchain.parsOr1: Seq[Int]` (lines 987-988).
- `cchain.willFullyUnroll`, `cchain.willUnroll`, `cchain.isUnit`, `cchain.isStatic`, `cchain.approxIters` (lines 991-1000).
- `ctr.start`, `ctr.step`, `ctr.end`, `ctr.ctrPar`, `ctr.ctrParOr1`, `ctr.ctrWidth` (lines 1010-1015).
- `ctr.isStatic`, `ctr.isStaticStartAndStep` (lines 1016-1028).
- `ctr.isFixed(forkedIters)` (lines 1030-1049) — returns true if the counter's iteration count is invariant of a given iterator set; used by streamification analyses.
- `ctr.nIters: Option[Bound]` (lines 1051-1059) — folds (start, step, end) to a static iteration count when possible.
- `ctr.willFullyUnroll` (lines 1060-1066) — `par >= nIter` when both are constant.
- `ctr.isUnit` (lines 1067-) — single-iteration counter.

For iterators: `IndexCounterOps[A]` (lines 1086-1093) and `BitsCounterOps` (lines 1095-1102) provide `i.counter`, `i.getCounter`, and the bidirectional setter. `IndexCounterIterOps` (lines 1078-1084) gives `i.ctrStart`, `i.ctrStep`, `i.ctrEnd`, `i.ctrPar`, `i.ctrParOr1` by delegating to the bound counter.

### Iter ↔ counter binding sites

The pre-unroll binding `IndexCounterInfo(ctr, Seq.tabulate(ctr.ctrParOr1){i => i})` — i.e., the identity lane map of width `par` — appears at every controller-staging site:

- `src/spatial/lang/control/ForeachClass.scala:29`
- `src/spatial/lang/control/ReduceClass.scala:44`
- `src/spatial/lang/control/MemReduceClass.scala:61-62` (one for `itersMap`, one for `itersRed`)
- `src/spatial/util/TransformUtils.scala:48` (when re-staging a controller during transformation)
- `src/spatial/transform/StreamTransformer.scala:45, 62` (after streamification)
- `src/spatial/traversal/CounterIterSynchronization.scala:13` (a sanity-check pass that re-binds iter ↔ counter when metadata is missing)

Special cases:
- `src/spatial/transform/UnitPipeToForeachTransformer.scala:23` uses `Seq(0)` (single lane) when synthesizing a unit foreach from a unit pipe.
- `src/spatial/transform/UnitIterationElimination.scala:13` checks `ctr.isUnit && ctr.ctrParOr1 == 1` to decide whether a counter can be removed entirely.

### Post-unroll lane bookkeeping

The unroller (`src/spatial/transform/unrolling/UnrollingBase.scala:455-487`) rewrites the lane map per duplicate. In `LoopUnroller.createBounds`:
- **MoP (Metapipelined-on-Multi)** path (lines 460-469): each counter spawns `par` (or `1` when `vectorize`) bound symbols. The lane-index list is either `[i]` (scalar) or `[parAddr(p)(ci) for p in 0..V-1]` (vectorized).
- **PoM (Parallel-of-Multi)** path (lines 470-486): each parallel duplicate `p` spawns one bound per counter dimension, with the lane index being `[parAddr(p)(i)]` — a single-element list.

Both paths invoke `b.counter = IndexCounterInfo(ctr, ctrIdxs)` (lines 466, 481) — so the post-unroll iterator's `lanes` field is the ordered list of which logical lanes that physical bound covers.

The `crossSection` helper (lines 100-112) generates a fresh `CounterChainNew` for a POM cross-section with `newStep = step * ctr.ctrParOr1` — collapsing `par` into the step. It throws if `start` or `step` aren't constant-foldable, signalling that POM unrolling needs static counter bounds.

### Pre-unroll vs post-unroll iterator handling

Pre-unroll iterators have `lanes.length == ctr.ctrParOr1` — the identity map. The `PreunrollIter` extractor (`CounterIterRewriteRule.scala:42-50`) gates rewrites on `lanes.size == par`, treating any non-identity lane map as already-unrolled. Post-unroll, `lanes` is a subset (size 1 for scalar duplicates; size V for vector lanes).

Transient pre-unroll handling: `LaneStatic.isTransient = true` (`LaneStatic.scala:8`) and counters are `Alloc` not `Primitive` — so `Transient.unapply` (`src/spatial/node/Transient.scala:14-18`) matches `LaneStatic` symbols but not counter symbols. This means retiming and DCE treat counters as live allocations and `LaneStatic` as a typing-only wrapper.

### Effect classification

| Node | Effects |
|---|---|
| `CounterNew[A]` | `Effects.Unique` (`Control.scala:11`) |
| `ForeverNew` | `Effects.Unique` (`Control.scala:14`) |
| `CounterChainNew` | `Effects.Unique` (`Control.scala:18`) |
| `LaneStatic[A]` | inherits `Primitive` (pure) |

Iterators carry no effects — they're `boundVar`s, not staged ops.

## Interactions

**Written by:**
- DSL controller helpers (`ForeachClass.scala:27-29`, `ReduceClass.scala:38-44`, `MemReduceClass.scala:55-62`, `Counter.scala:14-23`, `CounterChain.scala:11-12`).
- `transform/unrolling/UnrollingBase.scala:455-487` re-allocates per-lane bound iterators with subset `lanes`.
- `transform/StreamTransformer.scala:45,62` re-binds during streamification.
- `transform/UnitPipeToForeachTransformer.scala:23` synthesizes a unit-iteration counter when promoting `UnitPipe` → `OpForeach`.
- `traversal/CounterIterSynchronization.scala:13` repairs missing iter ↔ counter metadata.
- `rewrites/CounterIterRewriteRule.scala:18-37` stages `LaneStatic` for modular-arithmetic patterns.

**Read by:**
- `traversal/AccessExpansion.scala:75` reads `is.map(_.ctrParOr1)` to compute access matrices.
- `traversal/IterationDiffAnalyzer.scala:35` reads `i.ctrParOr1` for iteration-difference analysis.
- `transform/UnitIterationElimination.scala:13` reads `ctr.isUnit && ctr.ctrParOr1 == 1`.
- `transform/streamify/EarlyUnroller.scala:57, 113, 118` reads `ctrParOr1` to compute par factors and tile counts.
- `executor/scala/ControlExecutor.scala:97, 273, 458, 678` reads `ctrParOr1` to compute lane shifts during simulation.
- `transform/unrolling/UnrollingBase.scala:108` reads `ctr.ctrParOr1` to compute new step.
- `codegen/chiselgen/*` reads counter parameters per-controller to emit the appropriate counter chain RTL.

**Key invariants:**
- `cchain.counters.length == iters.length` at every staging site — the pairing is always 1-1.
- Pre-unroll: `i.counter.lanes == [0, 1, …, ctr.ctrParOr1 - 1]` (identity).
- Post-unroll: `i.counter.lanes` is a non-empty subset of `[0, …, par-1]` whose length equals 1 (scalar dup) or V (vector dup).
- `Forever` counters short-circuit every accessor in `package.scala:1010-1015, 1082-1083`; consumers must check `ctr.isForever` before reading concrete bounds.
- `Counter`, `CounterChain`, `Forever` allocations all carry `Effects.Unique` — never CSE them.
- `LaneStatic.isTransient = true` and `elems.size == 1` folds via `rewrite` to a constant.
- The `IterInfo` and `IndexCounter` metadata are kept in sync atomically by the `counter_=` setter (`package.scala:1089-1101`); a Rust rewrite must enforce both directions.

## HLS notes

`hls_status: rework`. HLS targets express counters via:
- C++ `for(int i = start; i < end; i += step)` loops — Spatial's `start`/`step`/`end` map directly.
- `#pragma HLS UNROLL factor=N` — Spatial's `par`. HLS doesn't have a first-class lane-index notion; it's emergent from the unroll factor.

The Rust-over-HLS rewrite needs:
1. A `Counter { start: Idx, end: Idx, step: Idx, par: u32 }` representation per loop dimension.
2. A typed iterator handle that explicitly references the counter — Rust's lifetime/borrow system can encode the binding rather than the metadata-table approach.
3. `Forever` is a Spatial-specific construct — HLS-equivalent is a `while(true)` with a `dataflow` pragma. Map to a "no static bound" counter kind.
4. `LaneStatic` is a post-unroll Spatial idiom — HLS doesn't have it; the lane index in HLS is implicit from the unrolled loop body. The Rust IR should normalize this away during HLS lowering.
5. Counter chain identity (`Effects.Unique`) is an IR-bookkeeping concern; HLS sees only the loop nest. Identity matters only inside the Rust IR.

See `30 - HLS Mapping/` for the per-construct categorization once the Rust skeleton is sketched.

## Open questions

- Q-irn-01 in `[[open-questions-spatial-ir]]` — Is `IterInfo` ever queried independently of `IndexCounter`, or could the bidirectional metadata be collapsed to a single direction (counter → iter via a controller's `iters` field)?
- Q-irn-02 — `LaneStatic` is only inserted by the `CounterIterRewriteRule` for `iter % par`-pattern modular arithmetic. Are there other lane-index expressions (e.g., `(iter / par) % submap`) that should also fold to `LaneStatic` but currently don't?
- Q-irn-03 — Post-unroll, `IndexCounterInfo.lanes` carries a list of physical lane indices. Is the ordering significant (e.g., does lane index 0 always correspond to the lowest-id iterator), or is it a set that happens to be encoded as a `Seq`?
