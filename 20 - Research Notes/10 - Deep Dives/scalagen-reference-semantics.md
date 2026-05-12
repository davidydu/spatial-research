---
type: deep-dive
topic: scalagen-reference-semantics
source_files:
  - "spatial/src/spatial/codegen/scalagen/ScalaCodegen.scala"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenSpatial.scala"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenBits.scala"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenBit.scala"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenFixPt.scala"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenFltPt.scala"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenController.scala"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenControl.scala"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenCounter.scala"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenMemories.scala"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenSRAM.scala"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenRegFile.scala"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenLUTs.scala"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenLineBuffer.scala"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenDRAM.scala"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenReg.scala"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenFIFO.scala"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenLIFO.scala"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenStream.scala"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenVec.scala"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenStructs.scala"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenArray.scala"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenSeries.scala"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenDebugging.scala"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenDelays.scala"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenFileIO.scala"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenText.scala"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenVar.scala"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenVoid.scala"
  - "spatial/emul/src/emul/Number.scala"
  - "spatial/emul/src/emul/FixFormat.scala"
  - "spatial/emul/src/emul/FixedPoint.scala"
  - "spatial/emul/src/emul/FltFormat.scala"
  - "spatial/emul/src/emul/FloatPoint.scala"
  - "spatial/emul/src/emul/Bool.scala"
  - "spatial/emul/src/emul/Memory.scala"
  - "spatial/emul/src/emul/BankedMemory.scala"
  - "spatial/emul/src/emul/ShiftableMemory.scala"
  - "spatial/emul/src/emul/LineBuffer.scala"
  - "spatial/emul/src/emul/OOB.scala"
  - "spatial/emul/src/emul/Counter.scala"
  - "spatial/emul/src/emul/Stream.scala"
  - "spatial/emul/src/emul/Ptr.scala"
  - "spatial/emul/src/emul/DRAMTracker.scala"
  - "spatial/emul/src/emul/StatTracker.scala"
  - "spatial/emul/src/emul/ResidualGenerator.scala"
  - "spatial/emul/src/emul/implicits.scala"
  - "spatial/emul/src/emul/Warn.scala"
  - "spatial/argon/src/argon/codegen/Codegen.scala"
  - "spatial/src/spatial/Spatial.scala"
session: 2026-04-23
status: ready-to-distill
feeds_spec:
  - "[[10 - Overview]]"
  - "[[20 - Numeric Reference Semantics]]"
  - "[[30 - Memory Simulator]]"
  - "[[40 - FIFO LIFO Stream Simulation]]"
  - "[[50 - Controller Emission]]"
  - "[[60 - Counters and Primitives]]"
---

# Scalagen — Reference Semantics Anchor

## The "reference semantics" claim

The load-bearing claim of this note: **scalagen, together with the `emul` runtime, is the de facto reference implementation of Spatial's dynamic semantics.** When two backends disagree on the behavior of a Spatial program, the Scala simulator is the ground truth. Any Rust-plus-HLS rewrite of Spatial must match the bit-level outputs of the Scala simulator, for every construct where the Scala simulator is defined.

Four structural facts support this claim:

1. **Scalagen is the only backend that emits a directly executable program modeling the full IR**. The Chisel backend emits RTL that requires Verilator or an FPGA to execute; the C++ backend emits a host shell around a foreign hardware; pirgen emits PIR DSL for Plasticine; tsthgen and roguegen emit scaffolding for other runtimes. Only the output of `ScalaGenSpatial(state)` (`spatial/src/spatial/Spatial.scala:153`, `spatial/src/spatial/codegen/scalagen/ScalaGenSpatial.scala:5-38`) is runnable on any machine with a JVM.

2. **`emul` is a hand-written bit-accurate numeric runtime**, not an off-the-shelf library. `FixedPoint` is implemented on top of `BigInt` with explicit rounding-mode constructors (`FixedPoint.clamped`, `FixedPoint.saturating`, `FixedPoint.unbiased` at `spatial/emul/src/emul/FixedPoint.scala:203-241`); `FloatPoint` is implemented on top of `BigDecimal` with a tagged-union `FloatValue` that distinguishes `NaN`/`Inf`/`Zero`/`Value` and with an explicit `clamp` routine that performs sign/mantissa/exponent packing including subnormal flushing (`FloatPoint.scala:318-398`). The `Bool` type is three-valued: `(value, valid)` with `X` for `!valid` (`Bool.scala:3-17`). These are deliberate modeling choices, not incidental artifacts of JVM arithmetic.

3. **Scalagen's lowering rules are one-liners**. Most `ScalaGen*.scala` case clauses look like `case FixAdd(x,y) => emit(src"val $lhs = $x + $y")` (`ScalaGenFixPt.scala:75`). The semantic weight lives in the `emul` types, not in the codegen. This makes scalagen an *unusually readable* ground truth: the meaning of `FixAdd` is exactly what `FixedPoint.+` does in `FixedPoint.scala:14`.

4. **Resource accounting is wired through the same path**. When `--resource-reporter` is set, every fixed-point op emits a `StatTracker.change(("FixPt", nbits), 1)` side-effect inline with the emitted `+`/`-`/`*`/etc. (`ScalaGenFixPt.scala:62-69`, `StatTracker.scala:5-26`). The simulator is also the cost model.

Phrased differently: if a Rust implementer wants to know "what does `FixRecip` return when `x == 0`?", the honest answer is "look at `Number.recip`, which returns `FixedPoint(1,x.fmt) / x`, which at `FixedPoint.scala:17` calls `valueOrX { ... / 0 }`, which catches `ArithmeticException` and returns `FixedPoint.invalid(fmt)` with `valid=false` (`FixedPoint.scala:102-104`, `161`)." There is no separate English-language spec for this behavior. The Scala code is the spec.

## Reading log

Files read in the following order (all paths relative to `spatial/`):

### Codegen core

1. `argon/src/argon/codegen/Codegen.scala` — the base `Codegen` trait. `process[R]` (`Codegen.scala:75-82`) writes `emitHeader`, `emitEntry(block)`, `emitFooter` into `Main.$ext` per the `out`/`entryFile` defaults. `javaStyleChunk` at `Codegen.scala:107-199` is the three-level method-size workaround that scalagen inherits.
2. `src/spatial/codegen/scalagen/ScalaCodegen.scala` — the scalagen base trait. Sets `lang="scala"`, `ext="scala"` (lines 14-15), overrides `emitHeader` to emit `import emul._` + `import emul.implicits._` (lines 28-33), overrides `emitEntry` to wrap user code in `object Main { def main(args: Array[String]): Unit = { ... } }` (lines 64-73), overrides `gen(block)` to dispatch through `javaStyleChunk` at depth `log_{CODE_WINDOW}(total_weight)` (lines 37-56), and layers `emitPreMain`/`emitPostMain` hooks that downstream traits chain.
3. `src/spatial/codegen/scalagen/ScalaGenSpatial.scala` — the 22-trait composition (`ScalaGenSpatial.scala:5-29`), plus dependency copies (`sim.Makefile`, `run.sh`, `build.sbt`, `build.properties` at lines 31-37).

### Emul numeric layer

4. `emul/src/emul/Number.scala` — `abstract class Number` with `bits`/`bitString`/`toByteArray` (`Number.scala:3-77`) and `object Number` with transcendentals delegating through `Math.*` via `toDouble` round-trips (`Number.scala:79-156`). Note that `Number.sigmoid` for `FixedPoint` is `1/(exp(-x)+1)`, not a dedicated approximation (`Number.scala:114`).
5. `emul/src/emul/FixFormat.scala` — `(sign, ibits, fbits)` with cached `MAX_VALUE`/`MIN_VALUE`/etc. (`FixFormat.scala:10-16`). Note `MAX_VALUE` treats the entire `ibits+fbits` envelope as one two's-complement number: signed `2^{ibits+fbits-1}-1`, unsigned `2^{ibits+fbits}-1`. Format combination (`FixFormat.scala:21-28`) takes the max widths and OR's the sign bits.
6. `emul/src/emul/FixedPoint.scala` — BigInt-backed with separate operator families:
   - standard `+`/`-`/`*`/`/`/`%` using `clamped` semantics (wrap on overflow, `:14-22`)
   - saturating `+!`/`-!`/`*!`/`/!` via `FixedPoint.saturating` (`:47-50`, `:218-222`)
   - unbiased `*&`/`/&`/`*&!`/`/&!` via `FixedPoint.unbiased` with RNG rounding (`:52-63`, `:232-241`)
   - logical shift `>>>` implemented by manual bit-manipulation (`:67-77`, since `BigInt` has no unsigned right-shift)
   - three factory methods — `clamped`/`saturating`/`unbiased` (`:203-241`) — that correspond to the three hardware rounding modes.
   - `valueOrX` catches `Throwable` (typically `ArithmeticException` on divide-by-zero) and returns `FixedPoint.invalid` (`:102-104`, `:161`).
7. `emul/src/emul/FltFormat.scala` — `(sbits, ebits)` with `bias=2^{ebits-1}-1`, `MIN_E`, `MAX_E`, `SUB_E=MIN_E-sbits` (`FltFormat.scala:5-8`). `MAX_VALUE_FP` built by setting the "all-ones except second-to-top" pattern (`:10-14`).
8. `emul/src/emul/FloatPoint.scala` — the most complex file. `FloatValue` is a sealed hierarchy (`NaN`, `Inf(neg)`, `Zero(neg)`, `Value(BigDecimal)`) with full IEEE-754 case tables for `+`/`-`/`*`/`/`/`%`/`<`/`<=`/`===` (`FloatPoint.scala:3-83`). Special `Zero(_)` carries sign. `FloatPoint.clamp` (`:318-398`) is the mantissa-exponent packing routine. Subnormal flushing happens at `:386-391` — when the shifted mantissa is 0, the value underflows to signed `Zero`.
9. `emul/src/emul/Bool.scala` — `(value, valid)` with propagation rule `this.valid && that.valid` on every op (`:5-11`). `toValidBoolean` gates on both `value && valid` (`:14`).

### Emul memory layer

10. `emul/src/emul/Memory.scala` — flat `Array[T]` with lazy initialization and global `DRAMTracker` accounting (`:4-25`).
11. `emul/src/emul/BankedMemory.scala` — the `Array[Array[T]]` representation where outer index is bank-index and inner is offset-in-bank. `apply` iterates lanes, wrapping each in `OOB.readOrElse` (`:28-35`). `flattenAddress` (`:23-26`) computes the bank-address using `Seq(dims...)` as the stride array.
12. `emul/src/emul/ShiftableMemory.scala` — single flat `Array[T]` but with a `shiftInVec` that walks an axis, shifting existing entries down and inserting new elements (`:15-23`). Used for `RegFile` and `LUT` via `emitBankedInitMem`'s `isRegFile || isLUT` branch (`ScalaGenMemories.scala:103`).
13. `emul/src/emul/LineBuffer.scala` — circular line buffer with internal `bufferRow`, `readRow`, `wrCounter`, `lastWrRow` state (`:14-17`). `swap()` decrements `bufferRow`/`readRow` by `stride` with positive modulus (`:21-25`). Write uses `(stride-1-row.toInt) + bufferRow` mod `fullRows` — reversed relative to index, which is the "bottom row is newest" convention.
14. `emul/src/emul/OOB.scala` — `readOrElse`/`writeOrElse` wrap a thunk in a `try`/`catch ArrayIndexOutOfBoundsException` block (`:19-38`). Writes the access to `./logs/reads.log` or `./logs/writes.log`. On OOB, returns the caller-provided `invalid` value (which for `FixedPoint` is `FixedPoint.invalid`, with `valid=false`).

### Emul control layer

15. `emul/src/emul/Counter.scala` — `Counterlike` abstract trait with two methods: `foreach` and `takeWhile(continue: =>Bool)` (`:5-8`). `Counter(start,end,step,par)` builds a `Array[FixedPoint]` of `par` lane-offsets and iterates `start until end by fullStep=par*step`, calling `func(vec, valids)` where `valids(i) = (start+i*step < end)` (`:10-34`). `Forever()` is a counter-like that never terminates (`:36-53`).
16. `emul/src/emul/Stream.scala` — `StreamIn[T]` and `StreamOut[T]` both extend `scala.collection.mutable.Queue[T]`. `StreamIn.initMem()` reads a filename from `StdIn`, reads each line, applies the supplied `elemFromString` parser, enqueues (`:5-25`). `StreamOut.initMem` opens a filename-read `PrintWriter` (`:27-42`). `BufferedOut[T:ClassTag](name, size, zero, elemToString)` backs a fixed-size array (`:53-79`).
17. `emul/src/emul/Ptr.scala` — a scalar container. `Ptr[T](var x: T)` with `set`, `value`, `reset`, `initMem(init)` (`:5-16`). This is the generated type for `Reg`/`ArgIn`/`ArgOut`/`HostIO`.

### Auxiliary

18. `emul/src/emul/DRAMTracker.scala` — a single global `mutable.Map[Any,Int]` counting `(ClassTag, bits, "read"|"write")` tuples (`:5-11`).
19. `emul/src/emul/StatTracker.scala` — a stack-controlled global `mutable.Map[Any,Int]`. `pushState(true)` enables; `popState()` restores (`:5-26`).
20. `emul/src/emul/ResidualGenerator.scala` — `ResidualGenerator(A,B,M)` with `expand(max)` returning the enumerated bank list (`:5-19`). Mirrors compiler-side `spatial.metadata.memory.ResidualGenerator`.
21. `emul/src/emul/implicits.scala` — `intToFixedPoint`/`fixedPointToInt`/`booleanToBool`/`boolToBoolean` implicit conversions (`:6-9`), `BoolArrayOps.toStr`/`toFmtStr` pretty-printers (`:11-25`).

### Scalagen controller and memory layers

22. `src/spatial/codegen/scalagen/ScalaGenController.scala` — the kernelization layer. `emitControlObject(lhs, ens, func*)` wraps each controller in a top-level `object X_kernel { def run(captured inputs): returnTp = if (ens) { body } else null.asInstanceOf[T] }` (`:108-139`). This is the file-per-controller pattern that lets chunked emission work across controller boundaries. Handles AccelScope/UnitPipe/ParallelPipe/UnrolledForeach/UnrolledReduce/Switch/SwitchCase/StateMachine/IfThenElse.
23. `src/spatial/codegen/scalagen/ScalaGenMemories.scala` — the banking/OOB wrapper. `flattenAddress(dims, indices, ofs?)` emits `idx*stride + ... + ofs` (`:26-34`). `emitBankedInitMem` emits `ShiftableMemory(...)` for `isRegFile||isLUT` and `BankedMemory(...)` otherwise (`:92-162`). `oob(...)` emits `try { body } catch { case err: java.lang.ArrayIndexOutOfBoundsException => ... }` (`:36-50`).

## Observations

### Every backend is a second-class citizen

A common reading of "Chisel is the production backend, scalagen is the toy" gets the relationship backward. The sequence of operations during compilation, per `Spatial.scala:241-252`, is `treeCodegen ==> irCodegen ==> (enableFlatDot ? dotFlatGen) ==> (enableDot ? dotHierGen) ==> (enableSim ? scalaCodegen) ==> (enableSynth ? chiselCodegen) ==> ...`. `--sim` and `--synth` are mutually exclusive command-line flags (`Spatial.scala:281-290`): `--sim` sets `enableSim=true` and `enableSynth=false`; `--synth` sets the opposite. The IR going into scalagen versus chiselgen is the same post-retiming, post-banking, post-unrolling IR (`Spatial.scala:209-238`). The IR is upstream of both — it's the specification, not the Chisel output.

This means scalagen has an advantage that the production backend does not: it does not need to model low-level timing. Where Chisel emits pipelined RTL and so must track per-cycle behavior, scalagen runs a controller to completion in one logical step, drains streams before advancing, and uses Scala references as memory. The semantic consequences of this simplification are listed under "Surprises" below.

### The three-rounding-modes contract

`FixedPoint` has three constructors beyond the raw `new FixedPoint(value, valid, fmt)`:

1. `FixedPoint.clamped(bits, valid, fmt)` (`FixedPoint.scala:203-209`) — wraps on overflow by masking with `fmt.MAX_VALUE` (unsigned) or OR'ing with `fmt.MIN_VALUE` when the top bit is set (signed). This is the default rounding mode; every unmarked op (`FixAdd`, `FixMul`, ...) uses `clamped`.
2. `FixedPoint.saturating(bits, valid, fmt)` (`FixedPoint.scala:218-222`) — clips to `MIN_VALUE_FP` / `MAX_VALUE_FP`. Used by `SatAdd`, `SatSub`, `SatMul`, `SatDiv`, the `+!`/`-!`/`*!`/`/!` operator family.
3. `FixedPoint.unbiased(bits, valid, fmt, saturate=false)` (`FixedPoint.scala:232-241`) — expects 4 extra fractional bits on input, computes a pseudo-random threshold using `Random.nextFloat()`, and rounds up or down based on `rand + remainder >= 1`. Used by `UnbMul`, `UnbDiv`, `UnbSatMul`, `UnbSatDiv`, `*&`/`/&`/`*&!`/`/&!`.

Rounding mode 3 is **non-deterministic**: `Random.nextFloat()` uses the default `scala.util.Random` object, which has a JVM-seeded RNG unless the user explicitly calls `Random.setSeed(...)` at program start. Two successive simulator runs of the same program will produce different rounded results at the LSB for every unbiased op. The comment at `FixedPoint.scala:235` ("RNG here for unbiased rounding is actually heavier than it needs to be") acknowledges this. For an HLS port, this semantics is either (a) irreducibly a hardware rounding mode that must be implemented with a dithered LSB, or (b) something the Rust simulator should replace with a deterministic tie-break. I flag this as a spec question.

### The three-valued Bool as a cross-cutting invariant

Every `emul` numeric type carries a `valid` bit that propagates through every operation. `FixedPoint.+` is `FixedPoint.clamped(this.value + that.value, this.valid && that.valid, fmt)` (`FixedPoint.scala:14`). `Bool.&&` is `Bool(this.value && that.value, this.valid && that.valid)` (`Bool.scala:5`). This means:

- Reading an OOB address returns `FixedPoint.invalid(fmt)` with `valid=false` (`OOB.scala:25-28`, `FixedPoint.scala:161`).
- Any arithmetic on that value produces `valid=false` output.
- `Bool.toString` prints `"X"` for invalid values (`Bool.scala:16`), and `FixedPoint.toString` prints `"X"` for invalid values (`FixedPoint.scala:112`).
- `assert($cond.toValidBoolean)` in `ScalaGenDebugging.scala:12-13` only fires when the condition is both valid and true.

This is a deliberate three-valued logic, consistent with chisel's `Wire` semantics. The Rust port must preserve this.

### The "outer-stream HACK"

`ScalaGenController.emitControlBlock` at lines 22-49 has an explicit `HACK` comment (line 32): for streaming outer controllers, each child is pumped by `while (hasItems_parent_child) { visit(child) }`, where `hasItems_parent_child` is `stream1.nonEmpty || stream2.nonEmpty || ...` (line 34). The hardware executes these children concurrently, but scalagen runs them serially to exhaustion per invocation, which "won't work for cases with feedback, but this is disallowed for now anyway" (line 33). 

This means scalagen does not faithfully simulate stream-coupled outer controllers with data-dependent cycles. A Rust simulator either needs to (a) replicate this hack and document the limitation, or (b) actually model per-cycle stream flow to support feedback. The deep-dive note flags this as a known divergence.

### Controller kernelization

Every controller is emitted as a separate `X_kernel.scala` file containing an `object X_kernel { def run(captured: Tp1, ..., captured: TpN): T = if (en) { body } else null.asInstanceOf[T] }` (`ScalaGenController.scala:108-139`). The captured-input set is computed at line 111 as `(nonBlockInputs ++ block.nestedInputs) diff op.binds`, minus memory syms and compile-time values (line 113). The enclosing scope then emits `val $lhs = $lhs_kernel.run($inputs)` (line 138). 

This is not purely cosmetic. It is how scalagen stays under JVM method-size limits even for large apps: each controller becomes a compilation unit. Large inner blocks are then further chunked inside their kernel via `javaStyleChunk`. The `scoped` map (`Codegen.scala:95`) records cross-chunk references so that later chunks can reach into earlier chunks' `Map[String,Any]` by string key (`Codegen.scala:100`).

### Memory objects are pre-declared at file scope

`SRAMNew`, `RegFileNew`, `LUTNew`, `LineBufferNew`, `RegNew`, `FIFONew`, `LIFONew`, `StreamInNew`, `StreamOutNew` all call `emitMemObject(lhs){ ... }` (`ScalaGenMemories.scala:61-67`), which emits the memory as a top-level `object lhs extends BankedMemory(...)` (or similar) in a file `lhs_kernel.scala`. The `globalMems` flag flips between "val"-style emission (inside `AccelScope`) and "if (lhs == null) x"-style initialization guards (globally, `:24`). Since Scala `object` singletons are lazily initialized on first access and may be referenced from multiple kernels, they must live outside the controller.

The `emitBankedInitMem` dispatches on memory kind:

- `isRegFile || isLUT` → emits a flat `ShiftableMemory` with the padded-flat `Array[T]` (`ScalaGenMemories.scala:103-119`)
- everything else (SRAM, most DRAM) → emits a `BankedMemory` with a 2D `Array[Array[T]]` built by `multiLoopWithIndex(dims).groupBy(bankAddr)` (`:133-143`)
- When there's no initializer, the SRAM case falls through to `Array.fill(banks){Array.fill(bankDepth)(invalid)}` (`:144-148`).

The initializer padding logic at `expandInits` (`:69-90`) handles the case where the memory has padding beyond its `constDims`: non-padded positions take the original init value, padded positions fall back to `inits.get.head` (line 85) — a quirk worth flagging. Arguably should be `invalid(tp)` instead.

### FIFO and LIFO are raw mutable Queues and Stacks

`ScalaGenFIFO` remaps `FIFO[A] -> scala.collection.mutable.Queue[A]` (`:12-15`) and emits `object $lhs extends scala.collection.mutable.Queue[A]` for `FIFONew` (`:18`). There is no size enforcement at enqueue — `FIFOIsFull(fifo)` emits `fifo.size >= stagedSize` but `FIFOBankedEnq` just calls `fifo.enqueue` unconditionally (`:41-44`). A banked FIFO dequeue on empty falls back to `${invalid(op.A)}` (`:34-37`), producing a value with `valid=false` that propagates downstream. LIFO is a `mutable.Stack` with `push`/`pop` (`ScalaGenLIFO.scala:31-44`), same semantics.

This means **the simulator does not detect overflow on enqueue**. A FIFO is silently elastic. This is a real difference from synthesized RTL, which back-pressures. For an HLS port, the choice is whether to (a) match scalagen (elastic), (b) match chiselgen (fixed-size, back-pressure), or (c) assert on overflow.

### Transcendentals route through Double

Every transcendental in `Number` (`sqrt`, `recip`, `exp`, `ln`, `log2`, `pow`, `sin`, `cos`, `tan`, and the `h` variants) converts to `Double` via `x.toDouble`, applies `Math.*`, and converts back via `FixedPoint(v, fmt)` or `FloatPoint(v, fmt)` (`Number.scala:97-114`, `140-156`). The accuracy is limited by IEEE double precision regardless of the `FltFormat` bits or `FixFormat` fbits. The Rust simulator can choose (a) match this (fast, potentially slightly off for high-precision formats), or (b) produce per-format bit-exact results using a higher-precision library like MPFR.

### The `FloatPoint.clamp` algorithm

`FloatPoint.clamp(value, fmt): Either[FloatValue, (Boolean, BigInt, BigInt)]` at lines 318-398 of `FloatPoint.scala` is the core float-packing routine. Walkthrough:

1. If `value == 0`, return `Left(Zero(negative=false))` (`:320-321`). Note: always positive-zero on round-to-zero from a positive input.
2. Compute `y = floor(log2(|value|))` (the raw exponent, `:324`) and `x = |value| / 2^y` (the raw mantissa in [1, 2), `:325`).
3. If `y < SUB_E && x > 1.9`: treat as subnormal-almost-saturation — set `y += 1, x = 1` (`:335-339`). The magic number 1.9 is a heuristic; I cannot justify it from first principles and flag this for the open-questions file.
4. If `x >= 2`, bump `y` and recompute `x` (`:340-343`). Handles the case where initial `x` rounds to 2.0.
5. Compute `cutoff`. If `x < cutoff`, decrement `y` and recompute (`:344-351`).
6. If `y > MAX_E`, return `Left(Inf(negative = value < 0))` — overflow to infinity (`:358-360`).
7. If `y >= MIN_E` (normal range): pack the mantissa as `mantissaP1 = floor((x-1) * 2^{sbits+1})`, round to even by adding the LSB as a rounding bit, shift right 1 (`:362-363`). Return `Right((value < 0, mantissa, y + bias))`.
8. If `y < MIN_E && y >= SUB_E` (subnormal range): build the mantissa, compute shift `MIN_E - y + 1`, shift right with rounding bit (`:372-391`). If the shifted mantissa is zero, underflow to `Zero` with the correct sign. Otherwise return `Right((sign, shiftedMantissa, 0))`.
9. Otherwise underflow → `Left(Zero(negative = value < 0))` (`:393-394`).

The matching `convertBackToValue` at lines 399-415 is the inverse: given a packed `(sign, mantissa, exp)`, it reconstructs the `BigDecimal` by `(m / 2^sbits + 1) * 2^{e - bias}` in the normal range and `(m / 2^{sbits-1}) * 2^{MIN_E - 1}` in the subnormal range. `new FloatPoint(convertBackToValue(clamp(v, fmt)), valid, fmt)` is the full round-trip (`:423-432`).

**Subnormal handling is non-trivial.** The Rust port cannot just cast to f32/f64 without losing the subnormal range of a custom format (e.g., 8-bit exponent has a subnormal range below 2^-126 that is representable in the format but not in f64 without gradual underflow). Producing bit-exact `FloatPoint` for custom formats requires replicating the `clamp` algorithm in Rust.

### The OOB semantics is "log and continue"

`OOB.readOrElse` catches `ArrayIndexOutOfBoundsException`, logs `"Mem: $mem; Addr: $addr [OOB]"` to `./logs/reads.log`, and returns the caller-provided `invalid` value (`OOB.scala:19-29`). `writeOrElse` catches the exception, logs `"Mem: $mem; Addr: $addr; Data: $data [OOB]"` to `./logs/writes.log`, and discards the data (`OOB.scala:30-38`). The scalagen memory codegen additionally wraps accesses in a nested `try { body } catch { case err: java.lang.ArrayIndexOutOfBoundsException => System.out.println("[warn] ... Memory ... Out of bounds $op at address " + $addr); ${invalid(tp)} }` (`ScalaGenMemories.scala:36-50`). So OOB accesses print both a stdout warning and append to the logfile.

**Gotcha.** `OOB.writeStream` and `OOB.readStream` are `lazy val`s constructed by `new PrintStream("./logs/writes.log")` (`OOB.scala:7-8`). If `./logs/` doesn't exist, the stream fails to open. `OOB.open()` (`:9-13`) is responsible for `mkdirs` on `./logs/`. The scalagen `emitPreMain` includes `OOB.open()` (`ScalaGenMemories.scala:14-17`) to guarantee this. Running the generated code outside the generated Makefile (e.g., piping into `sbt run` from an arbitrary cwd) may fail if `./logs/` is missing.

### Counter semantics are parallel-lane by default

`Counter(start, end, step, par)` is **not** a sequential counter — it is a par-lane vectorized counter. Each invocation of `foreach(func)` iterates `start until end by par*step`, and in each step passes `func` a `(vec: Array[FixedPoint], valids: Array[Bool])` where `vec(i) = start + (iter*par + i)*step` and `valids(i) = (vec(i) < end)` (`Counter.scala:10-23`). The generated scalagen code at `ScalaGenController.scala:94-97` destructures these into `is(j)` and `vs(j)` per lane.

This means the `valid` bit distinguishes "this lane's iterator is in bounds" from "this lane's iterator is beyond end". In hardware, out-of-range lanes are disabled. In scalagen, they still run — the emitted body sees `vs(j) == false` but still evaluates — and the *memory writes* gated on `vs(j)` will log a skipped access.

### Stream stdin-prompting is a real ergonomic wart

`StreamIn.initMem()` contains `print(s"Enter name of file to use for StreamIn $name: "); val filename = scala.io.StdIn.readLine()` (`Stream.scala:6-8`). `StreamOut` is the same (`:30-35`). `BufferedOut` same (`:58-60`). Running a generated simulator requires manually typing the filenames at the console per stream. This is the main reason simulator-driven tests have a `run.sh` harness that pipes filenames via stdin.

### Delay lines are elided

`ScalaGenDelays.scala:10` is `case DelayLine(size, data@Const(_)) => // Don't emit anything here (NamedCodegen takes care of this)`. Constant-valued delay lines are handled by `NamedCodegen`'s aliasing mechanism; non-constant delay lines (`DelayLine(size, data)`) emit a trivial `val $lhs = $data` (`:12`). The simulator does not model retiming latency — a `DelayLine(3, x)` produces the same value as `x` in the same logical step.

## Surprises

1. **Unbiased rounding uses a global RNG.** Two runs of the same simulator produce different bit-exact outputs on any program that hits `*&` / `/&` / `UnbMul` / `UnbDiv` / `FixToFixUnb` / `FixToFixUnbSat`. This breaks reproducibility.

2. **FIFO overflow is silent.** `FIFOBankedEnq` unconditionally enqueues, so a FIFO emulated as `mutable.Queue` grows without bound. Real RTL back-pressures.

3. **Subnormals are flushed to zero after round-trip through `FloatPoint.clamp`.** Specifically, when the shifted mantissa rounds to zero, the result is `Zero(sign)`. The sign is preserved but the value is signed-zero, not the smallest subnormal. For an HLS port this is compatible with denormal-flush-to-zero mode but differs from strict IEEE-754.

4. **`BankedMemory.initMem` is a no-op.** `BankedMemory.initMem(size, zero) { needsInit = false }` (`BankedMemory.scala:46-48`). The init data is injected via the constructor `data` parameter (the emitted `Array[Array[T]](...)` at `ScalaGenMemories.scala:143-147`), not via `initMem`. So `DRAM.initMem(size, zero)` from `Memory.scala:8-15` is the actual init call, while the scalagen-emitted `$lhs.initMem($size, $zero)` for a `BankedMemory` does nothing.

5. **Outer-stream loops are hand-pumped.** `while (hasItems_parent_child) { visit(child) }` loops per-child until streams are exhausted (`ScalaGenController.scala:32-38`). Concurrent streaming with feedback is unsupported.

6. **`DRAMTracker` is JVM-global.** Two simulations in the same JVM (e.g., a `sbt run` loop) accumulate counts across runs unless `DRAMTracker.accessMap.clear()` is explicitly called between runs.

7. **`emul.Counter.takeWhile` prints the `continue?` expression on every iteration.** `Counter.scala:27` has `Console.println(s"continue? $continue")` in the loop body — looks like leftover debug. If this path is hit (breakable counters), simulation floods stdout.

8. **`FloatPoint.clamp`'s "x > 1.9" heuristic at line 335** is a magic number without a documented justification. Flagged as an open question.

9. **`FixedPoint.toShort` shifts by `fmt.bits`, not `fmt.fbits`** (`FixedPoint.scala:81`). Inconsistent with `toByte`/`toInt`/`toLong` which all shift by `fbits`. This looks like a bug; flagging for the open-questions file.

10. **RegAccum throws on `AccumFMA` and `AccumUnk`.** `ScalaGenReg.scala:49-50` has `throw new Exception("This shouldn't happen!")` for both cases. Relies on upstream passes (accumAnalyzer/accumTransformer) to split these into `RegAccumFMA` or leave them as non-specialized accumulation. If accumTransformer is disabled and a program reaches codegen with `AccumFMA`, it crashes.

## Distillation plan

- **10 - Overview.md**: file-level structure, `ScalaCodegen` trait, `ScalaGenSpatial` composition, the `Main.scala` + `X_kernel.scala` file layout, `javaStyleChunk` adaptation, the `import emul._` header, the `emitEntry` → `object Main { def main ... }` wrapping. Flag ground-truth-for-Rust explicitly.
- **20 - Numeric Reference Semantics.md**: FixedPoint / FloatPoint / Bool / Number. The three rounding modes (clamped/saturating/unbiased). `FixFormat`/`FltFormat` precise semantics. `FloatPoint.clamp` line-by-line. Transcendentals routing through Double. The three-valued Bool propagation rule.
- **30 - Memory Simulator.md**: Memory / BankedMemory / ShiftableMemory / LineBuffer / OOB. Address flattening. OOB-checked access. Line-buffer circular logic. `emitBankedInitMem`/`emitBankedLoad`/`emitBankedStore`/`emitVectorLoad`. `DRAMTracker`.
- **40 - FIFO LIFO Stream Simulation.md**: the mutable.Queue/Stack mapping, status readers, FIFOReg, StreamIn/StreamOut/BufferedOut, `bitsFromString`/`bitsToString` encoders, the "silent overflow" surprise.
- **50 - Controller Emission.md**: controller kernelization, outer-stream HACK, AccelScope/UnitPipe/ParallelPipe/UnrolledForeach/UnrolledReduce/Switch/SwitchCase/StateMachine emission rules, `breakWhen` warning.
- **60 - Counters and Primitives.md**: Counter / Counterlike / Forever / takeWhile, RegAccumOp/RegAccumFMA, Mux/OneHotMux/PriorityMux, Vec as Array, Structs into Structs.scala, DelayLine elision.

## Open questions

Logged to `open-questions-scalagen.md`:

- Q-scal-01 — Unbiased rounding's nondeterminism (`Random.nextFloat` per op).
- Q-scal-02 — FIFO/LIFO elastic-vs-fixed-size. Expected HLS behavior?
- Q-scal-03 — `FloatPoint.clamp`'s "x > 1.9" magic heuristic.
- Q-scal-04 — `FixedPoint.toShort`'s apparent bit-shift bug.
- Q-scal-05 — Outer-stream HACK: what's the intended behavior for stream-feedback loops?
- Q-scal-06 — Scalagen delay line elision: does the simulator ever need to model latency?
- Q-scal-07 — `BankedMemory.initMem` being a no-op for the banked case — why the asymmetry with `Memory.initMem`?
- Q-scal-08 — `RegAccumOp` throwing on `AccumFMA` — what are the exact accumulation passes that guarantee this never reaches codegen?
- Q-scal-09 — `expandInits`' padding fallback to `inits.get.head` (`ScalaGenMemories.scala:85`) — why not `invalid(tp)`?
- Q-scal-10 — `DRAMTracker` global state: is a global map intentional, or should it be per-simulation?
