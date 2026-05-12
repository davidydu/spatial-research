---
type: spec
concept: scalagen-counters-and-primitives
source_files:
  - "spatial/emul/src/emul/Counter.scala:1-53"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenCounter.scala:1-22"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenReg.scala:1-69"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenBits.scala:1-79"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenVec.scala:1-47"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenStructs.scala:1-48"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenDelays.scala:1-16"
source_notes:
  - "[[scalagen-reference-semantics]]"
hls_status: rework
depends_on:
  - "[[10 - Overview]]"
  - "[[20 - Numeric Reference Semantics]]"
  - "[[30 - Memory Simulator]]"
  - "[[50 - Controller Emission]]"
status: draft
---

# Counters and Primitives

## Summary

This entry covers the remaining scalagen primitives: counters (`Counter`/`Counterlike`/`Forever`/`takeWhile`), register-accumulation operators (`RegAccumOp`/`RegAccumFMA`), bit selectors (`Mux`/`OneHotMux`/`PriorityMux`), vectors (`Vec` as `Array[A]`), structs (single shared `Structs.scala` file), and delay-line elision. **These are the reference semantics for control flow primitives that the Rust+HLS reimplementation must match.** Two structural facts to flag:

1. Scalagen counters are *parallel-lane vectorized* by construction. `Counter(start, end, step, par)` does not iterate scalar-by-scalar; each iteration produces an `Array[FixedPoint]` of `par` lane values plus a parallel array of `Bool` valid bits. The body must explicitly handle disabled lanes.
2. `RegAccumOp` throws `"This shouldn't happen!"` on `AccumFMA`/`AccumUnk`. The invariant is enforced upstream by `accumTransformer` and `accumAnalyzer`. If an unmodified `AccumFMA` reaches scalagen, the simulator crashes at the line `case AccumFMA => throw new Exception("This shouldn't happen!")` (`spatial/src/spatial/codegen/scalagen/ScalaGenReg.scala:49`).

## `Counterlike`, `Counter`, and `Forever`

`spatial/emul/src/emul/Counter.scala:5-53`. `Counterlike` declares two methods (`:5-8`): `foreach(func: (Array[FixedPoint], Array[Bool]) => Unit)` and `takeWhile(continue)(func)`. Both pass `(vec, valids)` arrays to the body.

`Counter(start, end, step, par)` precomputes `vecOffsets = [0, step, 2*step, ..., (par-1)*step]` (`:13`) and `fullStep = par * step` (`:12`). Each iteration step (`:15-23`): compute `vec(i) = i + vecOffsets(i)` per lane; compute `valids(i) = (vec(i) < end)` for forward step (or `> end` for backward); call `func(vec, valids)`; advance `i += fullStep`.

This is **not** a scalar counter. The body — emitted by `ScalaGenController.emitUnrolledLoop` (`spatial/src/spatial/codegen/scalagen/ScalaGenController.scala:94-97`) — destructures `(is, vs)` per lane: `val $iter = is($j)`, `val $valid = vs($j)`. Each lane `j` gets its own iter/valid symbol. Memory writes within the body must be enable-gated by `valid_j`; otherwise the body executes for out-of-range lanes but writes are discarded by the OOB-or-disable path in [[30 - Memory Simulator|BankedMemory.update]].

`Forever()` (`Counter.scala:36-53`) is the no-end counter. Its `foreach` runs `while (true) { func(vec, valids) }` with `vec = [0]` and `valids = [Bool(true)]`. Used inside a stream-driven outer loop, it relies on the outer `hasItems` predicate to terminate (see `ScalaGenController.emitUnrolledLoop:60-72`). Standalone `Forever` would loop infinitely.

### `takeWhile` variant

`Counter.takeWhile(continue: => Bool)(func)` (`Counter.scala:24-33`) is the break-enabled iteration; evaluates `continue` at the top of each iteration. **The body contains a debug println** at `:27`: `Console.println(s"continue? $continue")` floods stdout when any `breakWhen`-flagged loop runs. Likely leftover debug; the Rust port should drop it. `Forever.takeWhile` (`:45-52`) is symmetric.

## Counter codegen

`ScalaGenCounter` (`spatial/src/spatial/codegen/scalagen/ScalaGenCounter.scala:7-22`) is a four-line dispatch: `remap` rewrites `Counter[_] -> Counterlike` and `CounterChain -> Array[Counterlike]` (`:9-12`); `CounterNew(start, end, step, par) -> Counter(...)`, `CounterChainNew(ctrs) -> Array[Counterlike]($ctrs)`, `ForeverNew() -> Forever()` (`:15-19`). The IR-level `Counter[_]` becomes `Counterlike` so a `CounterChain` can mix `Counter` and `Forever`. The chain is indexed via `$cchain($i)` in `emitUnrolledLoop` (`ScalaGenController.scala:90`/`:94`).

## Register accumulation

`RegAccumOp(reg, in, en, op, first)` (`spatial/src/spatial/codegen/scalagen/ScalaGenReg.scala:41-55`) dispatches `op match`: `AccumAdd -> reg.value + in`, `AccumMul -> reg.value * in`, `AccumMax -> Number.max(reg.value, in)`, `AccumMin -> Number.min(reg.value, in)`. When enabled, write `if (first) $in else $input` to the register; otherwise unchanged. Read `$reg.value` is the resulting value (post-write if enabled). `first` is the "first-iteration" flag from the unroll-reduce transform — on first iter, the register takes the input directly; on subsequent iters, it combines.

**`AccumFMA` and `AccumUnk` throw `Exception("This shouldn't happen!")`** (`:49-50`). The invariant: `accumTransformer` splits FMA-shaped accumulation into `RegAccumFMA` before scalagen, and `accumAnalyzer` rejects `AccumUnk` earlier. If an unsplit `AccumFMA` reaches scalagen, **the simulator crashes**. See Q-scal-08.

`RegAccumFMA(reg, m0, m1, en, first)` (`ScalaGenReg.scala:57-64`) is the FMA-shaped accumulator: on first iter `m0 * m1`; subsequent `m0 * m1 + reg.value`, then `reg.set(...)`. **Note**: like `FixFMA` (`ScalaGenFixPt.scala:150`), this is *not* a fused-precision FMA — the multiply rounds before the add. Hardware FMA preserves intermediate precision; scalagen does not.

## Bit selectors — Mux, OneHotMux, PriorityMux

`ScalaGenBits` (`spatial/src/spatial/codegen/scalagen/ScalaGenBits.scala:28-46`) handles the three multiplexer families:

- **`Mux(sel, a, b)`** (`:29`): emits `if ($sel) $a else $b`. `sel` is a `Bool` with the `Bool->Boolean` implicit (`spatial/emul/src/emul/implicits.scala:8`) extracting `sel.value` — note **not** `toValidBoolean`, so an X-valued select picks `b`.
- **`OneHotMux(selects, datas)`** (`:30-37`): emits `List((sel0, d0), (sel1, d1), ...).collect{case (sel, d) if sel => d}.reduce{_|_}`. The `|` is bitwise-OR for `FixedPoint` (`FixedPoint.scala:25`) and logical-OR for `Bool` (`Bool.scala:7`); **no `|` exists for floats**, so `OneHotMux` over floats would fail to compile — rewrite passes presumably prevent this. Correctness requires exactly one `sel` true; multiple-true produces a bitwise union that may not be a valid value of the type. See Q-scal-16.
- **`PriorityMux(selects, datas)`** (`:39-45`): if-else cascade with first-true-wins; falls through to `invalid(R)` (X-valued).

## `DataAsBits` / `BitsAsData` / `Vec` / `Struct`

`ScalaGenBits.scala:47-74` handles bit-level reinterpret casts: `DataAsBits(a) -> $a.bits` for `FloatPoint`/`FixedPoint`, `Array[Bool]($a)` for `Bit` (`:47-51`); `BitsAsData(v, A) -> FloatPoint.fromBits(v, fmt)` / `FixedPoint.fromBits(v, fmt)` / `v.head` for Bit (`:53-57`); `DataAsVec`/`VecAsData` are Vec variants (`:59-74`). The `valid` bits propagate through `fromBits` / `bits`.

`ScalaGenVec` (`spatial/src/spatial/codegen/scalagen/ScalaGenVec.scala:7-47`) maps `Vec[A]` to `Array[A]`: `remap` (`:9-12`); `invalid(tp)` is `Array.fill(${tp.nbits}(${invalid(tp.A)})` — appears to have a missing close paren typo (Q-scal-18); `VecAlloc(elems) -> Array($elems)` (`:31`); `VecApply -> $vector.apply($i)` (`:32`); `VecSlice(vector, end, start) -> $vector.slice($start, $end+1)` (`:33-34`) since `end` is inclusive in Spatial; `VecConcat -> $vectors.mkString(" ++ ")` (`:36-39`) with zero-first lane ordering — `concat(c, b, a)` makes `v(12)` index into `a(1)`. `emitToString` handles `Vec[Bit]` specially (`:19-28`).

## Structs into `Structs.scala`

`ScalaGenStructs` (`spatial/src/spatial/codegen/scalagen/ScalaGenStructs.scala:9-48`) emits all encountered struct types into a single shared `Structs.scala` file. `emitDataStructures()` (`:27-36`) iterates `encounteredStructs` and emits each via `emitStructDeclaration` into `getOrCreateStream(out, "Structs.scala")` — using `out` (top-level scala/) rather than `kernel(lhs)`, so structs are visible across all kernels.

Each struct becomes a Scala `case class` with `var` fields (mutable, `:18-25`) and a `productPrefix` override so printing uses the IR-level `typeName` rather than the synthesized `Struct1`/`Struct2`. `StructAlloc/FieldUpdate/FieldApply` are direct mappings (`:39-44`): `StructAlloc(elems) -> new ${e.R}(${elems.map(_._2)})`; `FieldUpdate(struct, field, value) -> $struct.$field = $value`; `FieldApply(struct, field) -> $struct.$field`. `invalid` recurses on fields (`:11-13`).

## Delay line elision

`ScalaGenDelays` (`spatial/src/spatial/codegen/scalagen/ScalaGenDelays.scala:7-15`) handles the `DelayLine` IR node (a retiming-introduced register chain) by **eliding it entirely**: constant-valued delay lines are skipped (NamedCodegen aliases the symbol to the constant directly); non-constant delay lines emit a trivial `val $lhs = $data` alias.

**The simulator does not model retiming latency.** A `DelayLine(3, x)` produces the same value as `x` in the same logical step. Scalagen output cannot be cycle-accurate; for tests depending on per-cycle ordering, scalagen and chiselgen diverge. See Q-scal-06.

## Ground-truth status

The reference semantics defined here:

- **Counter**: par-lane vectorized, `(vec, valids)` tuple per iteration, `valids(j) = (vec(j) bound-check)`.
- **Forever**: infinite loop terminated by outer-controller `hasItems`.
- **`takeWhile`**: top-of-iteration break check.
- **`RegAccumOp`**: `if (first) input else op(reg.value, input)`. AccumFMA/Unk forbidden.
- **`RegAccumFMA`**: `if (first) m0*m1 else m0*m1 + reg.value`. Multiply rounds before add (not fused-precision).
- **`Mux`**: 2-input if-else. **`OneHotMux`**: filter-and-OR-reduce. **`PriorityMux`**: if-else cascade.
- **`Vec` as `Array[A]`**: zero-first lane ordering for `VecConcat`.
- **`Struct` as case class**: shared `Structs.scala`, mutable `var` fields, `productPrefix` override.
- **`DelayLine`**: elided; no retiming latency in simulation.

## HLS notes

`rework`. Most of these primitives have direct hardware equivalents (counter as FSM-driven counter register; mux as multiplexer; struct as packed bit-vector). Differences from scalagen:

- Counter par-lane vectorization is implicit in scalagen but explicit unrolling in RTL. The HLS target should emit `par` parallel datapaths.
- Delay lines are concrete pipeline registers in RTL but elided in scalagen. The Rust simulator should match scalagen's elision; the HLS target generates the registers.
- `RegAccumOp`'s "first iteration" flag is a control signal in RTL; scalagen models it as a runtime predicate. Same semantics.
- `Forever` requires a `hasItems` predicate in scalagen but is naturally a free-running counter in RTL with stream stall.

## Interactions

- **Upstream**: the unroll transform produces `UnrolledForeach`/`UnrolledReduce` with per-lane iter symbols. The accum transform splits `AccumFMA` into `RegAccumFMA`. Format inference assigns the `FixFormat` on counter starts/ends/steps. The retiming pass introduces `DelayLine` nodes that scalagen then drops.
- **Downstream**: `Counter.foreach` is invoked from `emitUnrolledLoop` ([[50 - Controller Emission]]). `RegAccumOp/FMA` reads/writes a `Ptr[T]` ([[30 - Memory Simulator]]). Mux/OneHotMux/PriorityMux are used wherever conditional values are needed.
- **Sibling**: [[20 - Numeric Reference Semantics]] for the `FixedPoint`/`Bool` types these primitives operate on.

## Open questions

- Q-scal-06 — Delay line elision and cycle-accuracy for the Rust port.
- Q-scal-08 — `RegAccumOp`'s `AccumFMA`/`AccumUnk` invariant from upstream passes.
- Q-scal-16 — `OneHotMux` reduce-with-`|` correctness for non-bitwise-OR types.
- Q-scal-17 — `Counter.takeWhile`'s `Console.println(s"continue? ...")` debug leftover.
- Q-scal-18 — `ScalaGenVec.invalid` apparent typo `Array.fill(${tp.nbits}(${invalid(tp.A)})` (missing close paren).

See `open-questions-scalagen.md`.
