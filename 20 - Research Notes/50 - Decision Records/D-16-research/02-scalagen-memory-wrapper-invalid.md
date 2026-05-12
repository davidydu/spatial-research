# D-16 Research: ScalaGen Memory Wrapper and Invalid Propagation

## Scope

This angle asks whether Rust out-of-bounds handling should match ScalaGen's log-and-invalid behavior, use synthesis assertions, or expose separate modes. The evidence here is limited to the Scala simulator surface: `ScalaGenMemories`, the emitted `emul` memory classes, and type-directed `invalid(tp)`. It does not decide the D-16 policy.

ScalaGen wires OOB logging into generated execution by emitting `OOB.open()` before main and `OOB.close()` after main (`src/spatial/codegen/scalagen/ScalaGenMemories.scala:14-21`). `OOB.open()` creates `./logs/` and initializes `reads.log` / `writes.log` streams (`emul/src/emul/OOB.scala:6-13`).

## Load/Store Wrapper Shape

For local SRAM-style memories, ScalaGen does not inline a `try` around each emitted banked access. `SRAMBankedRead` and `SRAMBankedWrite` lower to `$mem.apply(...)` and `$mem.update(...)` through `emitBankedLoad` / `emitBankedStore` (`src/spatial/codegen/scalagen/ScalaGenSRAM.scala:15-17`, `src/spatial/codegen/scalagen/ScalaGenMemories.scala:164-185`). RegFile and LUT vector reads/writes similarly call `ShiftableMemory.apply/update` through `emitVectorLoad` / `emitVectorStore` (`src/spatial/codegen/scalagen/ScalaGenRegFile.scala:25-26`, `src/spatial/codegen/scalagen/ScalaGenLUTs.scala:14-15`, `src/spatial/codegen/scalagen/ScalaGenMemories.scala:172-193`).

The actual array exception boundary lives inside the runtime classes. `BankedMemory.apply` computes a bank index and offset, then calls `OOB.readOrElse`; `BankedMemory.update` calls `OOB.writeOrElse` (`emul/src/emul/BankedMemory.scala:28-43`). `ShiftableMemory.apply/update` does the same for a flat row-major address (`emul/src/emul/ShiftableMemory.scala:34-64`). Disabled lanes are guarded inside the by-name thunk: disabled reads return invalid without touching the backing array, and disabled writes skip the update.

DRAM copies and fringe dense/sparse transfers use a separate `ScalaGenMemories.oob` helper, which emits generated `try { ... } catch { case err: java.lang.ArrayIndexOutOfBoundsException => ... }` (`src/spatial/codegen/scalagen/ScalaGenDRAM.scala:30-83`, `src/spatial/codegen/scalagen/ScalaGenMemories.scala:36-50`). On a read catch, it prints a stdout warning and emits `invalid(tp)`; on a write catch, it prints the warning and discards the write (`src/spatial/codegen/scalagen/ScalaGenMemories.scala:41-49`). Both layers catch only `ArrayIndexOutOfBoundsException`, not arbitrary failures.

## Meaning of Invalid

`invalid(tp)` is an X-value, represented as an ordinary runtime value plus a validity bit where possible. Bits emit `Bool(false,false)` (`src/spatial/codegen/scalagen/ScalaGenBit.scala:21-23`); `Bool` operations combine validity with `&&`, and print invalid as `X` (`emul/src/emul/Bool.scala:3-17`). Fixed point emits `FixedPoint.invalid(FixFormat(...))`, implemented as value `-1` with `valid=false`; arithmetic and comparisons usually propagate invalid by ANDing operand validity, and divide/mod helpers convert thrown arithmetic into invalid (`src/spatial/codegen/scalagen/ScalaGenFixPt.scala:26-28`, `emul/src/emul/FixedPoint.scala:14-32`, `emul/src/emul/FixedPoint.scala:102-103`, `emul/src/emul/FixedPoint.scala:161`). Floating point emits `FloatPoint.invalid(FltFormat(...))`, implemented as `NaN` with `valid=false`; arithmetic and comparisons likewise AND validity and print invalid as `X` (`src/spatial/codegen/scalagen/ScalaGenFltPt.scala:32-34`, `emul/src/emul/FloatPoint.scala:144-172`, `emul/src/emul/FloatPoint.scala:256-287`).

Vectors are arrays, not validity-carrying containers. The intended invalid vector is an array filled with invalid elements, but `ScalaGenVec.invalid` appears malformed: `Array.fill(${tp.nbits}(${invalid(tp.A)})` is missing a parenthesis and uses `nbits`, not lane count (`src/spatial/codegen/scalagen/ScalaGenVec.scala:9-16`). Rust should treat vector invalid semantics as a compatibility hazard to test, not as a clean spec sentence.

## Policy Axes for Rust

A ScalaGen-compatible Rust simulator mode would bounds-check every enabled access, log normal and OOB events, return type invalid on OOB reads, and discard OOB writes. That mode should preserve the disabled-lane convention: no log, no array touch, invalid read result only because the disabled read path explicitly returns invalid.

Synthesis assertions would be a stricter contract than ScalaGen emulation. They may be useful for hardware-facing validation, but they change observable simulator behavior by turning currently logged invalid/discard cases into failures. A separate-mode design would let Rust keep ScalaGen compatibility for simulation while allowing assertion-oriented synthesis or debug runs. The open question is whether D-16 values compatibility, early bug surfacing, or mode separation more highly.
