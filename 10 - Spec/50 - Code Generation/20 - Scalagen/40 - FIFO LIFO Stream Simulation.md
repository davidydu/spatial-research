---
type: spec
concept: scalagen-fifo-lifo-stream
source_files:
  - "spatial/src/spatial/codegen/scalagen/ScalaGenFIFO.scala:1-59"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenLIFO.scala:1-48"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenStream.scala:1-102"
  - "spatial/emul/src/emul/Stream.scala:1-80"
source_notes:
  - "[[scalagen-reference-semantics]]"
hls_status: rework
depends_on:
  - "[[10 - Overview]]"
  - "[[20 - Numeric Reference Semantics]]"
  - "[[30 - Memory Simulator]]"
status: draft
---

# FIFO, LIFO, and Stream Simulation

## Summary

FIFOs, LIFOs, and Streams in scalagen are mapped to standard Scala mutable collections — `scala.collection.mutable.Queue` for FIFO and StreamIn/StreamOut, `scala.collection.mutable.Stack` for LIFO. **This is a deliberate semantic choice with a surprising consequence: scalagen does not back-pressure on enqueue, so a FIFO/LIFO/Stream queue grows without bound.** This is the reference behavior that the Rust simulator must decide whether to match (silent elastic) or improve (fixed-size with assert/back-pressure). For the HLS port, this is one of the most consequential divergences between simulation and synthesized RTL.

This entry covers:

- `ScalaGenFIFO` mapping FIFO to `mutable.Queue` (`spatial/src/spatial/codegen/scalagen/ScalaGenFIFO.scala:1-59`).
- `ScalaGenLIFO` mapping LIFO to `mutable.Stack` (`spatial/src/spatial/codegen/scalagen/ScalaGenLIFO.scala:1-48`).
- `ScalaGenStream` mapping StreamIn/StreamOut/BufferedOut and the `bitsFromString`/`bitsToString` parsers (`spatial/src/spatial/codegen/scalagen/ScalaGenStream.scala:1-102`).
- The `emul.StreamIn`/`StreamOut`/`BufferedOut` runtime (`spatial/emul/src/emul/Stream.scala:1-80`).

## FIFO mapping

`ScalaGenFIFO.remap` rewrites the IR type `FIFO[A]` to `scala.collection.mutable.Queue[A]` (`spatial/src/spatial/codegen/scalagen/ScalaGenFIFO.scala:12-15`). `FIFONew(size)` emits an empty mutable Queue object at file scope:

```scala
case op@FIFONew(size) => emitMemObject(lhs){ emit(src"object $lhs extends scala.collection.mutable.Queue[${op.A}]") }
```

(`ScalaGenFIFO.scala:18`). The `size` argument is captured in metadata but not enforced at runtime.

### Status readers

The status predicates are size-comparisons against the staged size or against width metadata (`ScalaGenFIFO.scala:19-31`):

- `FIFOIsEmpty(fifo, _) -> $fifo.isEmpty`.
- `FIFOIsFull(fifo, _) -> $fifo.size >= ${fifo.stagedSize}` — note: this is *advisory* only; enqueue does not check it.
- `FIFOIsAlmostEmpty(fifo, _) -> $fifo.size <= rPar && $fifo.size > 0`, where `rPar = fifo.readWidths.maxOrElse(1)`.
- `FIFOIsAlmostFull(fifo, _) -> ($fifo.size >= stagedSize - wPar) && ($fifo.size < stagedSize)`, where `wPar = fifo.writeWidths.maxOrElse(1)`.
- `FIFOPeek(fifo, _) -> if ($fifo.nonEmpty) $fifo.head else ${invalid(op.A)}`.
- `FIFONumel(fifo, _) -> FixedPoint($fifo.size, FixFormat(true,32,0))`.

### Banked enqueue and dequeue

`FIFOBankedDeq(fifo, ens)` emits per-lane dequeues with `invalid(op.A)` fallback when disabled or empty (`ScalaGenFIFO.scala:33-39`):

```scala
case op@FIFOBankedDeq(fifo, ens) =>
  open(src"val $lhs = {")
  ens.zipWithIndex.foreach{case (en,i) =>
    emit(src"val a$i = if (${and(en)} && $fifo.nonEmpty) $fifo.dequeue() else ${invalid(op.A)}")
  }
  emit(src"Array[${op.A}](" + ens.indices.map{i => src"a$i"}.mkString(", ") + ")")
  close("}")
```

Dequeue-on-empty returns the type's `invalid` value (X-valued for `FixedPoint`/`FloatPoint`/`Bool`); this propagates through downstream arithmetic.

`FIFOBankedEnq(fifo, data, ens)` (`ScalaGenFIFO.scala:41-44`):

```scala
case FIFOBankedEnq(fifo, data, ens) =>
  open(src"val $lhs = {")
  ens.zipWithIndex.foreach{case (en,i) => emit(src"if (${and(en)}) $fifo.enqueue(${data(i)})") }
  close("}")
```

**Crucially, no size check.** Enqueue calls `$fifo.enqueue(...)` unconditionally when enabled. In synthesized hardware, enqueue on a full FIFO either back-pressures the producer or asserts; in scalagen, the queue silently grows. The author calls this out in the deep-dive note; see Q-scal-02.

### FIFOReg variants

`FIFORegNew` is a same-shape `mutable.Queue` (`ScalaGenFIFO.scala:46`). `FIFORegEnq` and `FIFORegDeq` are scalar versions of the banked operators (`ScalaGenFIFO.scala:47-52`). The `FIFOReg` type is the IR-level register-like FIFO with limited depth; scalagen does not distinguish it from a generic FIFO at runtime.

## LIFO mapping

`ScalaGenLIFO` is structurally identical, with `mutable.Stack` substituted for `mutable.Queue` (`spatial/src/spatial/codegen/scalagen/ScalaGenLIFO.scala:1-48`):

- Type remap to `scala.collection.mutable.Stack[A]` (`:12-14`).
- `LIFONew -> object $lhs extends scala.collection.mutable.Stack[A]` (`:18`).
- Status readers parallel FIFO's (`:19-29`):
  - `LIFOIsEmpty -> $lifo.isEmpty`.
  - `LIFOIsFull -> $lifo.size >= stagedSize`.
  - `LIFOIsAlmostEmpty -> $lifo.size === rPar` (note: triple-equals, equality-semantics).
  - `LIFOIsAlmostFull -> $lifo.size === stagedSize - wPar`.
  - `LIFOPeek -> if (nonEmpty) $lifo.head else invalid`.
  - `LIFONumel -> $lifo.size` (note: returns raw `Int`, not `FixedPoint` — inconsistent with FIFO; possibly a bug).
- `LIFOBankedPop` parallel to `FIFOBankedDeq` (`:31-37`).
- `LIFOBankedPush` parallel to `FIFOBankedEnq` (`:39-44`) — same silent-elastic enqueue.

## Stream mapping

`ScalaGenStream.remap` rewrites `StreamIn[A]` and `StreamOut[A]` to `scala.collection.mutable.Queue[A]` (`spatial/src/spatial/codegen/scalagen/ScalaGenStream.scala:12-16`). The runtime wrapper classes in `emul.Stream` extend `mutable.Queue[T]` and add file-IO methods.

### `StreamIn`, `StreamOut`, `BufferedOut`

`StreamIn[T]` (`spatial/emul/src/emul/Stream.scala:5-25`) extends `scala.collection.mutable.Queue[T]`. `initMem()` prompts on stdout `"Enter name of file to use for StreamIn $name: "`, reads a line from stdin (`:6-8`), opens the file, and enqueues every non-empty line through `elemFromString`. **This is an interactive prompt at simulator startup**, not a constructor argument — the `run.sh` harness pipes filenames via stdin. Lines without a digit (`!line.exists(_.isDigit)`) are silently skipped.

`StreamOut[T]` (`Stream.scala:27-51`) follows the same prompt-and-open pattern, with `dump()` called from `AccelScope` exit (`ScalaGenController.scala:166-168`) to flush accumulated contents in one batch. DRAMBus-typed streams skip this — they are handled via `FringeDenseLoad`/`FringeDenseStore` in `ScalaGenDRAM`.

`BufferedOut[T]` (`Stream.scala:53-79`) is a fixed-size mutable `Array[T]`, not a queue — used for output streams needing positional addressing. `close()` is called from `AccelScope` exit (`ScalaGenController.scala:170`).

### Stream codegen

`ScalaGenStream.gen` for `StreamInNew(bus)` (`ScalaGenStream.scala:60-70`) emits `object $lhs extends StreamIn[A]("$name", {str => bitsFromString(...) })` followed by `$lhs.initMem()` (only for non-DRAMBus). `StreamOutNew` is symmetric with `bitsToString` (`:72-82`). `StreamInBankedRead` and `StreamOutBankedWrite` use the same per-lane `enqueue`/`dequeue` patterns as FIFO (`:84-97`) — same silent-elastic enqueue.

## `bitsFromString` and `bitsToString` encoders

`bitsFromString(lhs, line, tp)` (`spatial/src/spatial/codegen/scalagen/ScalaGenStream.scala:23-40`) generates a Scala parser based on the IR type:

- `FixPtType(s,i,f) -> FixedPoint(line, FixFormat(s,i,f))`.
- `FltPtType(g,e) -> FloatPoint(line, FltFormat(g-1, e))`.
- `Bit -> Bool(line.toBoolean, true)`.
- `Vec[A] -> line.split(",").map(_.trim).map{elem => parse(elem) as A }.toArray`.
- `Struct[A] -> line.split(";").map(_.trim)` then per-field parses.

`bitsToString(lhs, elem, tp)` (`ScalaGenStream.scala:42-57`) is symmetric:

- Numeric types use `$elem.toString`.
- `Vec` -> `$elem.map{...}.mkString(", ")`.
- `Struct` -> per-field stringify, joined with `"; "`.

The line format is therefore: scalar types are bare strings, vectors are comma-separated, structs are semicolon-separated. The Vec-of-Struct case nests vector commas inside struct semicolons; the Struct-of-Vec case is unsupported in `bitsFromString` (no recursion path for that combination). Lines that would parse a Vec containing only zero digits would be skipped by `StreamIn.initMem`'s digit check.

## `getReadStreamsAndFIFOs` for outer-stream control

`ScalaGenController.getReadStreamsAndFIFOs(ctrl)` (`spatial/src/spatial/codegen/scalagen/ScalaGenController.scala:15-20`) collects all `LocalMemories` that are read by any descendant of `ctrl` and that are `StreamIn`, `FIFO`, or `MergeBuffer`. Used by the outer-stream HACK and by the `Forever` counter dispatch (`ScalaGenController.scala:34`, `:62-72`) to construct `def hasItems_$lhs: Boolean = stream1.nonEmpty || stream2.nonEmpty || ...`. See [[50 - Controller Emission]] for how this drives loop emission.

## Ground-truth status

This entry defines the reference simulation semantics of FIFOs, LIFOs, and Streams. **Two surprises must be reproduced or explicitly diverged from in the Rust port:**

1. **Silent elastic enqueue** (`ScalaGenFIFO.scala:41-44`, `ScalaGenLIFO.scala:39-44`, `ScalaGenStream.scala:92-97`). The simulator does not detect overflow. A test that overflows a FIFO will produce incorrect results in synthesis but correct (just slow) results in scalagen.
2. **Stdin-prompt for stream filenames** (`Stream.scala:6-8`, `:30-35`, `:58-60`). The generated simulator prompts for filenames at startup; the `run.sh` harness pipes them in via stdin. The Rust port should accept filenames as constructor arguments or CLI flags rather than reading stdin.

For the Rust simulator, the choice on (1) is a project-wide policy: match scalagen (lets tests find bugs only via output mismatch) or assert (stricter tests, possible test breakage).

## HLS notes

`rework`. In synthesized hardware, FIFOs and LIFOs are fixed-size with back-pressure on the producer (FIFO) or stack-overflow on the writer (LIFO). The HLS target should generate hardware FIFOs of the staged size, with back-pressure semantics, and rely on the simulator to detect overflow either as an assertion (stricter than scalagen) or as a separate verification mode.

The string-based stream encoding is scalagen-specific. In RTL, streams move bit-vectors over Decoupled handshake interfaces; the simulator's `bitsFromString`/`bitsToString` are only relevant for testbench wiring.

## Interactions

- **Upstream**: `LocalMemories` metadata (`mem.isStreamIn`, `mem.isFIFO`, `mem.isMergeBuffer`); IR nodes `FIFONew`/`LIFONew`/`StreamInNew`/`StreamOutNew`/`BufferedOutNew`/`FIFOBankedEnq`/etc.; `fifo.stagedSize`, `fifo.readWidths`, `fifo.writeWidths` from banking-and-sizing passes.
- **Downstream**: [[50 - Controller Emission]] uses `getReadStreamsAndFIFOs` to build outer-stream `hasItems` predicates. `AccelScope` triggers `dump()`/`close()` on stream outputs.
- **Sibling**: [[30 - Memory Simulator]] for memories that are not queue-shaped (SRAM/RegFile/LUT/LineBuffer use the `BankedMemory`/`ShiftableMemory`/`LineBuffer` classes, not `mutable.Queue`).

## Open questions

- Q-scal-02 — Silent elastic enqueue vs back-pressure semantics for HLS.
- Q-scal-12 — Whether Rust simulator should accept stream filenames as CLI args or configuration rather than stdin prompts.
- Q-scal-14 — `LIFONumel` returns raw `Int` while `FIFONumel` returns `FixedPoint`; bug or intentional?

See `open-questions-scalagen.md`.
