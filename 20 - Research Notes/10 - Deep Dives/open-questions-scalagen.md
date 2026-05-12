---
type: open-questions
topic: scalagen
session: 2026-04-23
date_started: 2026-04-23
---

# Open Questions — Scalagen Reference Semantics Session

Questions raised while documenting the Scala simulation backend + `emul` runtime. To be escalated to `20 - Open Questions.md` by the main session.

## Q-scal-01 — Unbiased rounding determinism

`FixedPoint.unbiased` at `spatial/emul/src/emul/FixedPoint.scala:232-241` calls `scala.util.Random.nextFloat()` on every invocation. Two consecutive runs of the same simulator produce different bit-exact outputs on any program that hits `*&` / `/&` / `UnbMul` / `UnbDiv` / `FixToFixUnb` / `FixToFixUnbSat`.

**Spec question.** Is the nondeterminism load-bearing (modeling a real hardware dithered-LSB behavior) or an accident of implementation? For the HLS port: should the Rust simulator match the JVM RNG behavior (difficult), use a seedable but deterministic RNG, or substitute a deterministic round-to-nearest-even?

**Source.** `spatial/emul/src/emul/FixedPoint.scala:232-241`, `ScalaGenFixPt.scala:111-114`.

Status: open.

## Q-scal-02 — FIFO / LIFO elastic semantics

`ScalaGenFIFO` emits `object $lhs extends scala.collection.mutable.Queue[A]` with no enqueue-side size check. `FIFOBankedEnq` just calls `fifo.enqueue(...)` unconditionally (`ScalaGenFIFO.scala:41-44`). The FIFO grows without bound. The same is true for LIFO (`ScalaGenLIFO.scala:39-44`) and Stream queues (`ScalaGenStream.scala:92-97`).

**Spec question.** In synthesized hardware, `FIFOEnq` on full FIFOs either back-pressures or asserts. Scalagen silently elastic-enqueues. Is the HLS simulator expected to match scalagen (let tests discover the bug via assertion failures), or to emulate back-pressure in simulation too?

**Source.** `spatial/src/spatial/codegen/scalagen/ScalaGenFIFO.scala:41-44`, `spatial/src/spatial/codegen/scalagen/ScalaGenLIFO.scala:39-44`, `spatial/src/spatial/codegen/scalagen/ScalaGenStream.scala:92-97`.

Status: open.

## Q-scal-03 — `FloatPoint.clamp` magic "x > 1.9" heuristic

At `spatial/emul/src/emul/FloatPoint.scala:335-339`:

```scala
if (y < fmt.SUB_E && x > 1.9) {
  y += 1
  x = 1
}
```

The `1.9` is undocumented. The comment at `:327-330` is cut out, so there is no inline justification. Conjecture: this is guarding the edge case where rounding a near-subnormal `BigDecimal` to 2.0 would escape the subnormal range and we want to bump the exponent to normal range with mantissa 0.

**Spec question.** Document the intended behavior. Is `1.9` a tolerance threshold (possibly equal to some `1 - 2^{-sbits}` value for typical sbits), or is it arbitrary? The Rust port needs to reproduce this exactly.

**Source.** `spatial/emul/src/emul/FloatPoint.scala:335-339`.

Status: open.

## Q-scal-04 — `FixedPoint.toShort` shift-by-`bits` bug

`spatial/emul/src/emul/FixedPoint.scala:81` is:

```scala
def toShort: Short = (value >> fmt.bits).toShort
```

Every sibling conversion shifts by `fbits`:

```scala
def toByte: Byte   = (value >> fmt.fbits).toByte
def toInt: Int     = (value >> fmt.fbits).toInt
def toLong: Long   = (value >> fmt.fbits).toLong
def toBigInt       = value >> fmt.fbits
```

Shifting by `fmt.bits` zeros out the entire value on most formats, returning zero. This looks like a typo.

**Spec question.** Is `toShort` intentionally broken, or is this a real bug? Does it affect any code? The `FixPtType(...).toShort` pipeline likely goes through `FixToFix(fmt = FixFormat(true, 16, 0))` at the language level instead of `toShort` directly, so the bug may be unreachable.

**Source.** `spatial/emul/src/emul/FixedPoint.scala:80-84`.

Status: open.

## Q-scal-05 — Outer-stream HACK and feedback loops

`ScalaGenController.emitControlBlock` at `spatial/src/spatial/codegen/scalagen/ScalaGenController.scala:22-49` contains an explicit `HACK` comment: for `isOuterStreamControl` controllers, each child is drained to completion before the next child runs. The comment at line 33 says "this won't work for cases with feedback, but this is disallowed for now anyway".

**Spec question.** What exactly is "disallowed"? Where in the compiler is the check that rejects stream-feedback? And — more importantly — what's the intended semantics for stream-coupled outer loops? The Rust port either matches scalagen's hand-pumped drain-per-child semantics (non-general) or does something different.

**Source.** `spatial/src/spatial/codegen/scalagen/ScalaGenController.scala:22-49`.

Status: open.

## Q-scal-06 — Delay line semantics under `--sim`

`ScalaGenDelays.scala:10-14`:

```scala
case DelayLine(size, data@Const(_)) => // Don't emit anything here (NamedCodegen takes care of this)
case DelayLine(size, data) => emit(src"val $lhs = $data")
```

Constant delay lines are elided entirely. Non-constant delay lines become a trivial alias. The simulator treats a `DelayLine(3, x)` and `x` as semantically identical.

**Spec question.** In RTL, retiming moves pipeline registers around to match timing. In scalagen, the registers are gone. For the Rust HLS target, whether to honor retiming semantics at all depends on whether the Rust backend is (a) behavioral (ignore timing, match scalagen) or (b) cycle-accurate (honor retiming). The spec should be explicit about the "reference semantics" view here: scalagen says retiming is invisible.

**Source.** `spatial/src/spatial/codegen/scalagen/ScalaGenDelays.scala:9-14`.

Status: open.

## Q-scal-07 — `BankedMemory.initMem` no-op

`spatial/emul/src/emul/BankedMemory.scala:46-48`:

```scala
def initMem(size: Int, zero: T): Unit = if (needsInit) {
  needsInit = false
}
```

The function does nothing except flip a flag. Data is injected via the constructor's `data: Array[Array[T]]` parameter, which the emitted scalagen code builds in the `emitBankedInitMem` block (`ScalaGenMemories.scala:143-147`). Meanwhile `Memory.initMem` at `spatial/emul/src/emul/Memory.scala:8-15` actually allocates the backing array.

**Spec question.** Why is there a no-op `initMem` on `BankedMemory` at all? The emit pattern `$lhs.initMem($size, $zero)` for banked memories doesn't do anything; it could be removed. Is this a vestigial symmetry with `Memory`?

**Source.** `spatial/emul/src/emul/BankedMemory.scala:46-48`, `spatial/emul/src/emul/Memory.scala:8-15`.

Status: open.

## Q-scal-08 — `RegAccumOp` throws on `AccumFMA` / `AccumUnk`

`spatial/src/spatial/codegen/scalagen/ScalaGenReg.scala:49-50`:

```scala
case AccumFMA => throw new Exception("This shouldn't happen!")
case AccumUnk => throw new Exception("This shouldn't happen!")
```

`AccumFMA` is split off into `RegAccumFMA` by `accumTransformer` (per the coverage note); `AccumUnk` presumably never survives `accumAnalyzer`.

**Spec question.** What exactly guarantees these cases are unreachable? Can `--sim` be run without `enableOptimizedReduce`, and if so, does scalagen crash on FMA accumulation? Trace the invariant.

**Source.** `spatial/src/spatial/codegen/scalagen/ScalaGenReg.scala:41-65`, `spatial/src/spatial/Spatial.scala:224-225`.

Status: open.

## Q-scal-09 — `expandInits` padding fallback

`spatial/src/spatial/codegen/scalagen/ScalaGenMemories.scala:69-90` has `expandInits` which pads a memory's init array when `padding` is nonzero. Non-padded positions copy from the original init. Padded positions fall back to:

```scala
else
  inits.get.head
```

I would have expected `invalid(tp)` or the memory's zero. Using `inits.get.head` replicates the first init value into every padded slot, which is likely not semantically correct.

**Spec question.** Is this a bug, or does the memory allocator guarantee the padded region is read-masked before any access? The Rust port needs to decide.

**Source.** `spatial/src/spatial/codegen/scalagen/ScalaGenMemories.scala:74-87`.

Status: open.

## Q-scal-10 — `DRAMTracker` global state

`spatial/emul/src/emul/DRAMTracker.scala:6`:

```scala
val accessMap = mutable.Map[Any, Int]().withDefaultValue(0)
```

The map is a JVM-global singleton. Two simulations in the same JVM (e.g., an `sbt run` loop for a test suite) will accumulate counts across runs.

**Spec question.** Is this intentional (one JVM per simulation), or should the tracker be per-simulation? For Rust where there's no shared JVM, does the tracker matter at all beyond `StatTracker`?

**Source.** `spatial/emul/src/emul/DRAMTracker.scala:5-11`.

Status: open.

## Q-scal-11 — `LineBuffer.swap` and `wrCounter`/`lastWrRow` invariants

`spatial/emul/src/emul/LineBuffer.scala:21-25`:

```scala
def swap(): Unit = {
  bufferRow = posMod(bufferRow - stride, fullRows)
  readRow = posMod(readRow - stride, fullRows)
  wrCounter = 0
}
```

`swap` resets `wrCounter` but does not reset `lastWrRow`. Since the next write at line 44 uses `if (bank0 != lastWrRow) wrCounter = 0`, the post-swap state is `wrCounter = 0` and `lastWrRow = (some old row)`. If the post-swap first write happens to land on the old `lastWrRow`, the counter does not re-reset (already 0) — fine. If it lands elsewhere, `wrCounter` is reset to 0 (re-redundantly).

**Spec question.** Is `lastWrRow` intentionally not reset by `swap`? Could there be a case where the line buffer is in an inconsistent state across an outer-loop iteration boundary?

**Source.** `spatial/emul/src/emul/LineBuffer.scala:21-25`, `:43-46`.

Status: open.

## Q-scal-12 — Stream filename resolution in Rust port

Generated scalagen code prompts on stdin for stream filenames at simulator startup (`spatial/emul/src/emul/Stream.scala:6-8`, `:30-35`, `:58-60`). The standard harness pipes them in via `run.sh`. This is a usability wart.

**Spec question.** Should the Rust simulator (a) match scalagen and prompt on stdin, (b) accept filenames as constructor arguments at codegen time (requiring the codegen to know test-vector paths), (c) accept filenames as CLI flags at runtime (e.g., `--stream-in foo=in.txt`), or (d) accept a single config file mapping stream names to filenames?

Note: option (b) breaks separation between codegen (deterministic from IR) and test data; option (c) is closest to current `run.sh` behavior but more user-friendly.

**Source.** `spatial/emul/src/emul/Stream.scala:5-79`.

Status: open.

## Q-scal-13 — Transcendental precision for the Rust port

`spatial/emul/src/emul/Number.scala:97-156` routes every transcendental through `Math.*` over `Double`, regardless of the source format precision:

```scala
def sqrt(x: FloatPoint): FloatPoint = FloatPoint(Math.sqrt(x.toDouble), x.fmt).withValid(x.valid)
```

For a `FltFormat(52, 11)` (IEEE double), this is bit-exact. For `FltFormat(23, 8)` (IEEE single), the result is rounded twice (compute in double, then `clamp` to single — usually fine but not always bit-equivalent to a hardware single-precision sqrt). For wider formats like `FltFormat(112, 15)` (quad), the f64 round-trip *loses precision*.

**Spec question.** Should the Rust simulator (a) match scalagen and route through f64 (fast, occasionally lossy for wide formats), (b) use MPFR for per-format-exact transcendentals (slower, bit-exact), or (c) match the synthesized hardware unit (e.g., a Newton-Raphson iteration with N steps)? The spec needs to define the canonical transcendental for each format.

**Source.** `spatial/emul/src/emul/Number.scala:97-156`.

Status: open.

## Q-scal-14 — `LIFONumel` return type inconsistency

`spatial/src/spatial/codegen/scalagen/ScalaGenLIFO.scala:29`:

```scala
case LIFONumel(lifo,_) => emit(src"val $lhs = $lifo.size")
```

vs `spatial/src/spatial/codegen/scalagen/ScalaGenFIFO.scala:31`:

```scala
case FIFONumel(fifo,_)   => emit(src"val $lhs = FixedPoint($fifo.size,FixFormat(true,32,0))")
```

`FIFONumel` returns `FixedPoint`; `LIFONumel` returns raw `Int`. If the IR-level `LIFONumel` op has a `FixedPoint` return type, the emitted Scala would have a type mismatch at compile time. If the IR-level type is `Int`, there's an asymmetry between `FIFO` and `LIFO` that should be unified.

**Spec question.** Bug or intentional asymmetry? Check the IR definition of `LIFONumel.R`.

**Source.** `spatial/src/spatial/codegen/scalagen/ScalaGenLIFO.scala:29`, `spatial/src/spatial/codegen/scalagen/ScalaGenFIFO.scala:31`.

Status: open.

## Q-scal-15 — `breakWhen` end-of-iteration vs immediate semantics

`spatial/src/spatial/codegen/scalagen/ScalaGenController.scala:75-93` emits `while(hasItems_$lhs && !${stopWhen.get}.value)` for break-enabled loops, with an explicit warning at `:76`/`:79`/`:89`/`:92`: *"breakWhen detected! Note scala break occurs at the end of the loop, while --synth break occurs immediately"*.

This means scalagen sees one extra iteration's worth of memory writes / register updates compared to RTL. **For tests using `breakWhen`, scalagen and chiselgen produce different outputs.**

**Spec question.** Should the Rust simulator match scalagen (end-of-iteration) for parity with existing test results, or match RTL (immediate-break) for tighter HLS correspondence? The two are mutually exclusive.

**Source.** `spatial/src/spatial/codegen/scalagen/ScalaGenController.scala:74-93`.

Status: open.

## Q-scal-16 — `OneHotMux` reduce-with-`|` correctness

`spatial/src/spatial/codegen/scalagen/ScalaGenBits.scala:30-37`:

```scala
case op @ OneHotMux(selects,datas) =>
  open(src"val $lhs = {")
    emit(src"List(")
    selects.indices.foreach { i => emit(...) }
    emit(").collect{case (sel, d) if sel => d}.reduce{_|_}")
  close("}")
```

The `reduce{_|_}` assumes the data type defines `|`. For `FixedPoint`, this is bitwise-OR; for `Bool`, logical-OR; for `FloatPoint`, **there is no `|` operator** — `OneHotMux` over floats would fail to compile. Presumably rewrite passes guarantee this never happens.

**Spec question.** What guarantees this? If a one-hot mux over floats is needed (e.g., from optimization), what rewrites prevent the IR from reaching codegen with that shape? Also: if multiple selects are true, the OR-reduce produces a value that is the bitwise union — likely not a valid value of the source format. Is this acceptable (relying on caller for one-hotness) or should there be a runtime check?

**Source.** `spatial/src/spatial/codegen/scalagen/ScalaGenBits.scala:30-37`.

Status: open.

## Q-scal-17 — `Counter.takeWhile` debug println

`spatial/emul/src/emul/Counter.scala:24-33`:

```scala
def takeWhile(continue: => Bool)(func: ...): Unit = {
  var i = start
  while ({...} && continue) {
    Console.println(s"continue? $continue")  // <--
    val vec = ...
    ...
  }
}
```

The `Console.println` floods stdout when `takeWhile` is invoked (any `breakWhen`-flagged loop). Looks like leftover debug instrumentation.

**Spec question.** Drop the println in the Rust port. Is there any test that depends on this output?

**Source.** `spatial/emul/src/emul/Counter.scala:27`.

Status: open.

## Q-scal-18 — `ScalaGenVec.invalid` apparent typo

`spatial/src/spatial/codegen/scalagen/ScalaGenVec.scala:14-17`:

```scala
override def invalid(tp: Type[_]): String = tp match {
  case tp: Vec[_] => src"""Array.fill(${tp.nbits}(${invalid(tp.A)})"""
  case _ => super.invalid(tp)
}
```

Missing closing parenthesis: should likely be `Array.fill(${tp.nbits})(${invalid(tp.A)})`. As written, the emitted code is `Array.fill(N(X)` — invalid Scala. This means `invalid` for a `Vec` type either never gets called (only used in OOB and switch fallbacks) or always errors at compilation.

**Spec question.** Bug. When is `invalid(Vec[A])` reached? Are there any tests that produce a Vec invalid that would catch this?

**Source.** `spatial/src/spatial/codegen/scalagen/ScalaGenVec.scala:14-17`.

Status: open.
