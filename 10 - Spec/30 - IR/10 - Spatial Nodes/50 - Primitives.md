---
type: spec
concept: spatial-ir-primitives
source_files:
  - "src/spatial/node/Mux.scala:1-57"
  - "src/spatial/node/Accumulator.scala:1-57"
  - "src/spatial/node/Shuffle.scala:1-27"
  - "src/spatial/node/DelayLine.scala:1-14"
  - "src/spatial/node/LaneStatic.scala:1-15"
  - "src/spatial/node/Transient.scala:1-19"
  - "src/spatial/node/HierarchyMemory.scala:112-120"
  - "src/spatial/node/HierarchyUnrolled.scala:143-154"
  - "src/spatial/node/DRAM.scala:17-21"
  - "src/spatial/node/Frame.scala:1-36"
  - "src/spatial/node/StreamStruct.scala:8-22"
  - "argon/src/argon/node/DSLOp.scala:11-25"
  - "argon/src/argon/Op.scala:72"
source_notes:
  - "[[spatial-ir-nodes]]"
hls_status: clean
depends_on:
  - "[[20 - Memories]]"
  - "[[30 - Memory Accesses]]"
  - "[[40 - Counters and Iterators]]"
status: draft
---

# Primitives (IR nodes)

## Summary

Spatial layers a small set of hardware-flavored primitive nodes on top of argon's vanilla `Fix*`/`Flt*`/`Bit*` primitives. They are the IR ops that have no internal state, can be conditionally executed, but carry hardware-scheduling semantics that vanilla argon nodes don't model: muxes that fold via priority/one-hot rewrites (`src/spatial/node/Mux.scala`), retiming-aware delay lines and gate barriers (`src/spatial/node/DelayLine.scala`), valid-bit-aware compress shuffles (`src/spatial/node/Shuffle.scala`), per-lane static-index markers (`src/spatial/node/LaneStatic.scala`), the `Transient` extension over `argon.node.Primitive` (`src/spatial/node/Transient.scala`), and the in-place register-accumulator nodes (`RegAccumOp`/`RegAccumFMA`/`RegAccumLambda`) which are technically `Accumulator` (post-unroll accessor) but carry a Spatial-specific `Accum` reduction enum (`src/spatial/node/Accumulator.scala`). All of these inherit `Primitive[R]` from argon (`argon/src/argon/node/DSLOp.scala:11-15`), so they are stateless and predicatable; they differ from vanilla `Fix`/`Flt`/`Bit` ops by attaching `rewrite` rules, `isTransient` flags, or `Effects.Simple` scheduling barriers. For the HLS rewrite, this category is mostly `clean`: muxes and delay lines map straightforwardly to HLS C++ idioms, and the Spatial-specific accumulators desugar to HLS `+= operator` patterns with `#pragma HLS DEPENDENCE`.

## Syntax / API

There are no dedicated DSL constructors for most primitives — they are produced internally by the staging machinery, retiming, or rewrite rules. The exceptions:

- `Mux(s, a, b)` — emitted by `mux(...)` and `?` operator combinators in `src/spatial/lang/api/`.
- `OneHotMux(sels, vals)` / `PriorityMux(sels, vals)` — produced by `oneHotMux(...)` and `priorityMux(...)` API helpers and inserted by `Switch` lowering when collapsing case-arms.
- `DelayLine(size, data)` — inserted by retiming (`spatial.transform.RetimingTransformer`) and `RetimeGate()` is a manual barrier exposed to user via `retimeBlock { ... }`.
- `ShuffleCompress(in)` / `ShuffleCompressVec(in)` — emitted by streaming/vectorization passes for `(value, valid)` pair compression.
- `LaneStatic(iter, elems)` — inserted by `CounterIterRewriteRule` (see [[40 - Counters and Iterators]]).
- `RegAccumOp` / `RegAccumFMA` / `RegAccumLambda` — emitted by `traversal/AccumAnalyzer` when it detects a `RegRead → arith → RegWrite` cycle that fits an accumulator pattern.

## Semantics

### Argon baseline: `Primitive[R]`, `EnPrimitive[R]`, `Transient`

`argon.node.Primitive[R]` (`argon/src/argon/node/DSLOp.scala:13-15`) is the argon class for "non-zero latency, no internal state, conditionally executable" nodes. Two flags:
- `isTransient: Boolean = false` — when true, the node is a typing/wrapping construct that disappears after analysis (no RTL emission).
- `canAccel: Boolean = true` — inherited from `DSLOp`; whether the op is allowed inside `AccelScope`.

`EnPrimitive[R]` (`DSLOp.scala:24`) extends `Primitive[R] with Enabled[R]` — adds a `var ens: Set[Bit]` to gate execution.

`spatial.node.Transient[R]` (`src/spatial/node/Transient.scala:10-12`) is a Spatial-specific subclass that hardcodes `isTransient = true`:
```scala
abstract class Transient[R:Type] extends Primitive[R] {
  override val isTransient: Boolean = true
}
```
The TODO comment "This is a bit odd to have Primitive in argon and Transient in spatial" (line 9) flags the cross-layer awkwardness — `argon.Primitive` carries the `isTransient` knob but Spatial owns the abstract class that fixes it true.

`Transient.unapply` (`Transient.scala:14-18`) matches any Primitive whose `isTransient` is true OR any sym matched by `Expect(_)` (a bounded-constant marker from `spatial.metadata.bounds`). This means retiming/DCE treats both flagged transient primitives and constant-folded expressions uniformly.

The Spatial-specific transient memory-query primitives (`MemStart`, `MemStep`, `MemEnd`, `MemPar`, `MemLen`, `MemOrigin`, `MemDim`, `MemRank`) live in `src/spatial/node/HierarchyMemory.scala:112-120` and all extend `Transient[I32]` or `Transient[Ind[W]]`. They get inlined away once dimensions are resolved.

### Mux family (`Mux.scala`)

```scala
@op case class Mux[A:Bits](s: Bit, a: Bits[A], b: Bits[A]) extends Primitive[A] {
  @rig override def rewrite: A = s match {
    case Literal(true)  => a.unbox
    case Literal(false) => b.unbox
    case _ if a == b    => a.unbox
    case _ => super.rewrite
  }
}
```
(`src/spatial/node/Mux.scala:9-18`).

A standard 2:1 mux with three constant-folding rewrites: literal-true selector → `a`, literal-false → `b`, equal arms → `a`. All three rewrites fire during staging via `@rig override def rewrite`, before the node is added to the IR.

```scala
@op case class OneHotMux[A:Bits](sels: Seq[Bit], vals: Seq[Bits[A]]) extends Primitive[A] {
  @rig override def rewrite: A = {
    if (sels.length == 1) vals.head.unbox
    else if (sels.exists{case Literal(true) => true; case _ => false}) {
      val trues = sels.zipWithIndex.filter{case (Literal(true), _) => true; case _ => false }
      if (trues.lengthMoreThan(1)) {
        warn(ctx, "One-hot mux has multiple statically true selects")
        warn(ctx)
      }
      val idx = trues.head._2
      vals(idx).unbox
    }
    else if (vals.distinct.lengthIs(1)) vals.head.unbox
    else super.rewrite
  }
}
```
(`Mux.scala:19-37`).

Rewrites:
1. Single-selector → unwrap (line 22).
2. Any statically-true select → pick that arm; warn at staging time if multiple (lines 23-31). The warning fires inside `rewrite`, an unusual placement — most diagnostics defer to a later analyzer.
3. All `vals` identical → unwrap any (line 32).

`PriorityMux` (`Mux.scala:39-57`) has the same shape but the multiple-true rewrite branch is commented out (lines 43-51). The single-selector and all-identical rewrites are live; literal-true folding is not. The intuition: a priority mux with multiple statically-true selects has well-defined semantics (the highest-priority one wins) and doesn't need a warning.

All three mux nodes extend plain `Primitive[A]` — no enable; the selector encodes the predication.

### Delay line and retime gate (`DelayLine.scala`)

```scala
@op case class DelayLine[A:Bits](size: Int, data: Bits[A]) extends Primitive[A] {
  @rig override def rewrite: A = if (size == 0) data.unbox else super.rewrite
}

@op case class RetimeGate() extends Primitive[Void] {
  override def effects = Effects.Simple
}
```
(`src/spatial/node/DelayLine.scala:8-14`).

`DelayLine` is a synthetic register chain inserted by retiming to balance pipeline depths; `size` is the number of cycles. The size-0 case folds away (line 9) — retiming sometimes inserts a 0-cycle delay as a placeholder. Otherwise the node stays alive through codegen.

`RetimeGate` is a scheduling barrier with `Effects.Simple`. The `Simple` effect keeps it from being DCE'd or motioned across; codegen ignores it (no RTL is emitted for `RetimeGate`), but its presence forces the surrounding code motion to respect it as a fence.

Both nodes are plain `Primitive` — no enable, no transient flag. `DelayLine`'s `rewrite` rule is the only fold; `RetimeGate` has no rewrite.

### Shuffle compress (`Shuffle.scala`)

```scala
abstract class ShuffleOp[A:Bits] extends Primitive[Tup2[A, Bit]] {
  val A: Bits[A] = Bits[A]
  def in: Tup2[A, Bit]
}

abstract class ShuffleOpVec[A:Bits](implicit val vT: Type[Vec[Tup2[A, Bit]]]) extends Primitive[Vec[Tup2[A, Bit]]] {
  val A: Bits[A] = Bits[A]
  def in: Seq[Sym[Tup2[A, Bit]]]
}

@op case class ShuffleCompress[A:Bits](in: Tup2[A, Bit]) extends ShuffleOp[A]

@op case class ShuffleCompressVec[A:Bits](
  in: Seq[Sym[Tup2[A, Bit]]],
)(implicit val vA: Type[Vec[Tup2[A, Bit]]]) extends ShuffleOpVec[A]
```
(`src/spatial/node/Shuffle.scala:8-27`).

Both nodes operate on `(value, valid)` tuples and produce a contiguous-packed output. The scalar `ShuffleCompress` takes a single `Tup2[A, Bit]` and returns the same type; the vector form takes a `Seq[Sym[Tup2[A, Bit]]]` and produces a `Vec[Tup2[A, Bit]]`. There are no `rewrite` rules — they survive through codegen as primitive shuffle networks. They're hardware-flavored primitives with no enable: the valid bit *is* the predication.

### Accumulators (`Accumulator.scala`)

```scala
sealed abstract class Accum
case object AccumAdd extends Accum
case object AccumMul extends Accum
case object AccumMin extends Accum
case object AccumMax extends Accum
case object AccumFMA extends Accum
case object AccumUnk extends Accum
```
(`src/spatial/node/Accumulator.scala:9-16`).

A closed enumeration of in-place reduction kinds. `AccumUnk` is the fallback when the analyzer can't classify the cycle.

```scala
sealed abstract class AccumMarker {
  var control: Option[Ctrl] = None
  def first: Bit
}
object AccumMarker {
  object Reg {
    case class Op(reg: Reg[_], data: Bits[_], written: Bits[_], first: Bit, ens: Set[Bit], op: Accum, invert: Boolean) extends AccumMarker
    case class FMA(reg: Reg[_], m0: Bits[_], m1: Bits[_], written: Bits[_], first: Bit, ens: Set[Bit], invert: Boolean) extends AccumMarker
  }
  object Unknown extends AccumMarker { def first: Bit = null }
}
```
(`src/spatial/node/Accumulator.scala:18-28`).

`AccumMarker` is a *metadata-style* tag — not an IR op — that travels with a `RegRead`/`RegWrite` pair to mark them as participating in an accumulator pattern. The `control: Option[Ctrl]` field records which controller owns the cycle; `first: Bit` is the iteration-first signal that resets the accumulator.

The IR-level accumulator nodes:
```scala
abstract class RegAccum[A:Bits] extends Accumulator[A] {
  def bank = Nil
  def ofs = Nil
}

@op case class RegAccumFMA[A:Bits](mem: Reg[A], m0: Bits[A], m1: Bits[A], en: Set[Bit], first: Bit) extends RegAccum[A]
@op case class RegAccumOp[A:Bits](mem: Reg[A], in: Bits[A], en: Set[Bit], op: Accum, first: Bit) extends RegAccum[A]
@op case class RegAccumLambda[A:Bits](mem: Reg[A], en: Set[Bit], func: Lambda1[A,A], first: Bit) extends RegAccum[A]
```
(`Accumulator.scala:30-57`).

These extend `spatial.node.Accumulator[A]` (`src/spatial/node/HierarchyUnrolled.scala:143-154`), itself a `UnrolledAccessor[A,A]` with `data: Seq[Sym[_]] = Nil`. So technically they live in the post-unroll accessor hierarchy, not in "primitives." But they read like primitives: each is a single-step in-place reduction node with `bank = Nil, ofs = Nil` (because the underlying memory is a scalar `Reg`). They differ from vanilla `argon.node.Fix*` arithmetic in three ways:

1. **In-place mutation.** They carry `Effects.Writes(mem)` (inherited from `Accumulator.effects`, `HierarchyUnrolled.scala:152`) and an enable set — a vanilla argon arithmetic op is pure.
2. **First-iteration signaling.** The `first: Bit` field tells codegen when to clear the accumulator instead of reading the previous value. No vanilla argon node carries a "first" bit.
3. **Reduction enum.** `RegAccumOp` parameterizes over `Accum` (Add/Mul/Min/Max/FMA/Unk); the codegen pattern-matches on the enum to emit the right RTL operator. `RegAccumFMA` is hardcoded to FMA but takes two multiplicands. `RegAccumLambda` takes a `Lambda1[A,A]` for arbitrary user-defined reductions — an escape hatch from the closed `Accum` enum.

`data: Seq[Sym[_]] = Nil` (inherited from `Accumulator`, `HierarchyUnrolled.scala:145`) is the surprise: there is no syntactic `data` symbol attached to these accumulator nodes. The accumulated value is computed inside the codegen template, not represented as an IR sym. Any analysis that walks `localWrite.map(_.data)` for all writers must guard against this.

### LaneStatic

`LaneStatic[A](iter, elems: Seq[Int])` (`src/spatial/node/LaneStatic.scala:7`) is a transient primitive — see [[40 - Counters and Iterators]] for full semantics. Briefly: it tags an iterator symbol with the integer lane indices it represents post-unroll. `isTransient = true` (line 8); `rewrite` folds the single-element case to a constant via `iter.from(elems.head)` (line 14).

### Mux rewrite vs vanilla argon

Vanilla `argon.node.Fix*` and `argon.node.Bit*` primitives don't override `rewrite` for value folding — they rely on a separate `Rewrites` machinery in argon. Spatial's `Mux`/`OneHotMux`/`PriorityMux`/`DelayLine`/`LaneStatic` override `@rig def rewrite` directly on the case class, so the fold happens at staging time without going through the rewrite registry. This is functionally equivalent but lexically tighter — the rewrite rule lives next to the node definition.

## Implementation

### Class hierarchy

```
argon.node.DSLOp[R]                                (argon/src/argon/node/DSLOp.scala:6)
  argon.node.Primitive[R]                          (DSLOp.scala:13)
    spatial.node.Mux[A]                            (Mux.scala:9)
    spatial.node.OneHotMux[A]                      (Mux.scala:19)
    spatial.node.PriorityMux[A]                    (Mux.scala:39)
    spatial.node.DelayLine[A]                      (DelayLine.scala:8)
    spatial.node.RetimeGate                        (DelayLine.scala:12)
    spatial.node.LaneStatic[A]                     (LaneStatic.scala:7)
    spatial.node.ShuffleOp[A]                      (Shuffle.scala:8)
      spatial.node.ShuffleCompress[A]              (Shuffle.scala:20)
    spatial.node.ShuffleOpVec[A]                   (Shuffle.scala:14)
      spatial.node.ShuffleCompressVec[A]           (Shuffle.scala:24)
    spatial.node.Transient[R]                      (Transient.scala:10)
      MemStart, MemStep, MemEnd, MemPar, MemLen,   (HierarchyMemory.scala:112-120)
      MemOrigin, MemDim, MemRank
    spatial.node.SimpleStreamStruct[S]             (StreamStruct.scala:8 — isTransient = true)
    spatial.node.DRAMAddress[A,C]                  (DRAM.scala:17)
    spatial.node.DRAMIsAlloc[A,C]                  (DRAM.scala:21)
    spatial.node.FrameAddress[A,C]                 (Frame.scala:13)
    spatial.node.FrameIsAlloc[A,C]                 (Frame.scala:17)

argon.node.EnPrimitive[R]                          (DSLOp.scala:24)
  spatial.node.RegAccum[A] (extends Accumulator[A])  (Accumulator.scala:30)
    spatial.node.RegAccumOp[A]                     (Accumulator.scala:44)
    spatial.node.RegAccumFMA[A]                    (Accumulator.scala:36)
    spatial.node.RegAccumLambda[A]                 (Accumulator.scala:52)
```

### Effect classification

| Node | Effects |
|---|---|
| `Mux`, `OneHotMux`, `PriorityMux` | inherit `Primitive` (pure) |
| `DelayLine` | inherit `Primitive` (pure) |
| `RetimeGate` | `Effects.Simple` (`DelayLine.scala:13`) — scheduling barrier |
| `ShuffleCompress`, `ShuffleCompressVec` | inherit `Primitive` (pure) |
| `LaneStatic` | inherit `Primitive` (pure); `isTransient = true` |
| `Transient[R]` and all subclasses (Mem* dimension queries, `SimpleStreamStruct`) | inherit `Primitive` (pure); `isTransient = true` |
| `DRAMAddress`, `DRAMIsAlloc`, `FrameAddress`, `FrameIsAlloc` | inherit `Primitive` (pure) — they read DRAM/Frame metadata, not memory |
| `RegAccumOp`/`RegAccumFMA`/`RegAccumLambda` | `Effects.Writes(mem)` via `Accumulator.effects` (`HierarchyUnrolled.scala:152`) |

### Rewrite rules summary

| Node | Rewrite condition | Result |
|---|---|---|
| `Mux` | `s = Literal(true)` | `a` |
| `Mux` | `s = Literal(false)` | `b` |
| `Mux` | `a == b` | `a` |
| `OneHotMux` | `sels.length == 1` | `vals.head` |
| `OneHotMux` | any `Literal(true)` select | first true select's `vals(idx)` (warn if multiple) |
| `OneHotMux` | all `vals` identical | `vals.head` |
| `PriorityMux` | `sels.length == 1` | `vals.head` |
| `PriorityMux` | all `vals` identical | `vals.head` |
| `DelayLine` | `size == 0` | `data` |
| `LaneStatic` | `elems.size == 1` | `iter.from(elems.head)` (a constant) |

### Why these are not vanilla argon

Vanilla `argon.node.Fix*`/`Flt*`/`Bit*` are pure arithmetic primitives. Spatial's primitives layer hardware-specific behavior: the mux family carries hardware-design rewrites (the multi-true-select warning is a hardware concern), `DelayLine`/`RetimeGate` are pipeline-balancing artifacts that argon's combinational model doesn't represent, `ShuffleCompress` tracks `(value, valid)` tuples that argon vector ops don't, `LaneStatic` records post-unroll lane identity that has no argon concept, `Transient` is Spatial's class even though argon owns the `isTransient` flag, and `RegAccum*` encodes an in-place RMW cycle as a single node where argon would model it as value-flow with a separate write.

### Rewrite invocation point

The `@rig override def rewrite: A` methods run during `stage(...)` — before the node is added to the IR. If `rewrite` returns a non-null value, staging substitutes it. So `Mux(Literal(true), a, _)` never produces a `Mux` IR node. `super.rewrite` falls through to `argon.Op.rewrite`'s default `null.asInstanceOf[R]` (`argon/src/argon/Op.scala:72`), signalling "no rewrite".

## Interactions

**Written by:**
- Staging: `Mux` from `spatial.lang.api` mux helpers; `OneHotMux`/`PriorityMux` from `oneHotMux`/`priorityMux` API and `Switch.op_switch` lowering.
- `transform/RetimingTransformer` inserts `DelayLine`s; user code calls `retimeBlock` to insert `RetimeGate`.
- `rewrites/CounterIterRewriteRule.scala:18-37` stages `LaneStatic` for modular-arithmetic patterns.
- `traversal/AccumAnalyzer` classifies cycles and emits `RegAccumOp`/`RegAccumFMA`/`RegAccumLambda` to replace `RegRead → arith → RegWrite` triples.
- Streaming/vectorization passes emit `ShuffleCompress` / `ShuffleCompressVec`.

**Read by:**
- `transform/MemoryAnalyzer` / `traversal/AccessAnalyzer` — recognize `RegAccum*` to skip standard banking analysis (the accumulator is a single scalar; there's nothing to bank).
- `codegen/chiselgen/ChiselGenAccumulator` (and friends) — pattern-match on `RegAccumOp`'s `op: Accum` enum to pick the RTL operator.
- `codegen/chiselgen/ChiselGenDelayLine`, `ChiselGenMux` — emit per-node RTL.
- `transform/RetimingTransformer` reads `RetimeGate` as a fence.
- `Transient.unapply` (`Transient.scala:14-18`) — used everywhere DCE/retiming wants to recognize "this node disappears after analysis."

**Key invariants:**
- `Mux`/`OneHotMux`/`PriorityMux`'s rewrites fire at staging time; the IR never contains a literal-true `Mux` or single-selector mux — passes can assume well-formed muxes.
- `Transient[R].isTransient = true` is non-overridable (it's a `val` in the abstract); subclasses inherit the flag.
- `RetimeGate.effects = Effects.Simple` — code motion must not traverse it.
- `RegAccum*.data = Nil` — no syntactic data symbol; analyses must guard against this.
- `LaneStatic`'s `elems` count must equal the iterator's `par` factor at the time of insertion; the `PreunrollIter` extractor (`CounterIterRewriteRule.scala:42-50`) gates on this equality.
- `Mux`'s `a` and `b` are typed `Bits[A]` (not `Sym[A]`) — boxed values that may be literals or symbols. Equality (`a == b`) is structural at the boxed level.

## HLS notes

`hls_status: clean`. `Mux` → C++ ternary; `OneHotMux`/`PriorityMux` → priority `if/else` chains or `switch` with `#pragma HLS UNROLL`; `DelayLine` → static shift-register array or `#pragma HLS DEPENDENCE`; `RetimeGate` has no direct analog (HLS does its own retiming) and can be collapsed in the Rust IR before HLS emission; `ShuffleCompress`/`ShuffleCompressVec` → small unrolled compaction loop; `LaneStatic` constant-folds during HLS lowering. `RegAccumOp`/`RegAccumFMA`/`RegAccumLambda` map to `acc += x`, `acc = acc * m0 + m1`, etc., with `#pragma HLS DEPENDENCE inter false` for single-cycle RMW; the `first` bit becomes a conditional reset.

`Transient[R]` subclasses fold during analysis and never reach HLS. The Rust IR should treat transient as an analysis-only attribute and not emit those nodes.

See `30 - HLS Mapping/` for the per-construct categorization.

## Open questions

- Q-irn-04 in `[[open-questions-spatial-ir]]` — `OneHotMux.rewrite` warns at staging time on multiple statically-true selects; `PriorityMux` has the same warning commented out. Is the asymmetry intentional, or is `PriorityMux`'s warn dead code that should be re-enabled?
- Q-irn-05 — `RegAccumLambda` takes a `Lambda1[A,A]` for arbitrary reductions, but codegen must support *any* user-supplied function. Is there a complexity bound (latency, dependence) that the analyzer enforces, or does codegen just inline whatever lambda is given?
- Q-irn-06 — `Transient[R]` is a Spatial subclass that fixes `isTransient = true`, but `argon.node.Primitive[R]` already exposes `isTransient` as a `val`. Could `Transient` be merged into argon as a renamed `Primitive` with a constructor flag, or is the cross-layer split load-bearing for some reason?
