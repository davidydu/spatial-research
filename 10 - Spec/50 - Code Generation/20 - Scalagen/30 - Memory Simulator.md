---
type: spec
concept: scalagen-memory-simulator
source_files:
  - "spatial/emul/src/emul/Memory.scala:1-25"
  - "spatial/emul/src/emul/BankedMemory.scala:1-49"
  - "spatial/emul/src/emul/ShiftableMemory.scala:1-71"
  - "spatial/emul/src/emul/LineBuffer.scala:1-63"
  - "spatial/emul/src/emul/OOB.scala:1-40"
  - "spatial/emul/src/emul/DRAMTracker.scala:1-11"
  - "spatial/emul/src/emul/Ptr.scala:1-16"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenMemories.scala:1-196"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenSRAM.scala:1-20"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenRegFile.scala:1-37"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenLUTs.scala:1-19"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenLineBuffer.scala:1-83"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenDRAM.scala:1-107"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenReg.scala:1-69"
source_notes:
  - "[[scalagen-reference-semantics]]"
hls_status: rework
depends_on:
  - "[[10 - Overview]]"
  - "[[20 - Numeric Reference Semantics]]"
status: draft
---

# Memory Simulator

## Summary

This entry defines the runtime semantics of every Spatial memory primitive — `SRAM`, `RegFile`, `LUT`, `LineBuffer`, `DRAM`, `Reg`, `ArgIn`, `ArgOut`, `HostIO` — as modeled by the `emul` runtime and emitted by `ScalaGenMemories` and its sibling traits. **This is the reference semantics anchor for memory operations.** The Rust+HLS reimplementation must reproduce: address-flattening rules, bank-and-offset access patterns, OOB-checked access with logging-and-fallback behavior, and circular line-buffer state. Pre-banked memory layouts are baked into the emitted code at codegen time; the simulator does not re-bank dynamically.

The runtime classes live in `spatial/emul/src/emul/`:

- `Memory[T]` — flat lazy-init `Array[T]` with global access tracking, used by `DRAM` (`Memory.scala:4-25`).
- `BankedMemory[T]` — `Array[Array[T]]` (banks × offsets), used by `SRAM` (`BankedMemory.scala:5-49`).
- `ShiftableMemory[T]` — flat `Array[T]` with shift-along-axis support, used by `RegFile` and `LUT` (`ShiftableMemory.scala:5-71`).
- `LineBuffer[T]` — `Array[Array[T]]` with circular row state, used by `LineBuffer` (`LineBuffer.scala:5-63`).
- `Ptr[T]` — single-cell mutable container, used by `Reg`/`ArgIn`/`ArgOut`/`HostIO` (`Ptr.scala:5-16`).
- `OOB` — out-of-bounds access logger (`OOB.scala:6-39`).
- `DRAMTracker` — global access counter (`DRAMTracker.scala:5-11`).

## Address flattening

`ScalaGenMemories.flattenAddress` (`spatial/src/spatial/codegen/scalagen/ScalaGenMemories.scala:26-34`) emits row-major address arithmetic. The strides are computed as `[d_1*...*d_{n-1}, d_2*...*d_{n-1}, ..., 1]` — row-major for `dims = [d_0, d_1, ..., d_{n-1}]`. Result: `sum(idx_i * stride_i) + ofs`. Used in DRAM/SRAM offset emission and replicated at runtime in `BankedMemory.flattenAddress` (`BankedMemory.scala:23-26`) and `ShiftableMemory.flattenAddress` (`ShiftableMemory.scala:34-37`).

## OOB-checked access

Memory accesses are wrapped at two levels: the runtime `OOB` object catches `ArrayIndexOutOfBoundsException` and logs to file; the codegen additionally wraps in a try-catch that prints to stdout and substitutes `invalid(tp)` on read.

`OOB.readOrElse[T](mem, addr, invalid, en)(rd: => T): T` (`spatial/emul/src/emul/OOB.scala:19-29`) executes the read thunk inside a `try`; on success, logs `"Mem: $mem; Addr: $addr"` to `./logs/reads.log` (when `en`); on `ArrayIndexOutOfBoundsException`, logs `[OOB]` and returns the caller-provided `invalid` value. `writeOrElse` is symmetric (`:30-38`). **OOB does not abort** — reads return X-valued; writes are discarded; downstream arithmetic propagates the X.

The codegen wrapper at `ScalaGenMemories.scala:36-50` emits a `try { body } catch { case err: ArrayIndexOutOfBoundsException => System.out.println("[warn] ... Memory: Out of bounds $op at address ..."); ${invalid(tp)} }` around each memory op. Used by `ScalaGenDRAM` to wrap `SetMem`/`GetMem`/`FringeDenseLoad`/etc. (`spatial/src/spatial/codegen/scalagen/ScalaGenDRAM.scala:33-83`).

`OOB.open()` runs `new File("./logs/").mkdirs()` and forces the lazy `PrintStream` instances (`OOB.scala:9-13`); invoked from `ScalaGenMemories.emitPreMain` (`ScalaGenMemories.scala:14-17`). `OOB.close()` is in `emitPostMain` (`:19-22`).

## `Memory[T]` (DRAM)

`spatial/emul/src/emul/Memory.scala:4-25` is a flat lazy-init `Array[T]`. `initMem(size, zero)` allocates `Array.fill(size)(zero)` once via the `needsInit` flag (`:8-15`). `apply(i)` and `update(i, x)` each increment `DRAMTracker.accessMap((classTag[T], bits, "read"|"write"))` (`:17-23`), tracking per-type access counts globally.

`DRAM` allocations emit `object $lhs extends Memory[T]("name")` followed by `$lhs.initMem(size + elementsPerBurst, $zero)` (`spatial/src/spatial/codegen/scalagen/ScalaGenDRAM.scala:16-22`). The `+ elementsPerBurst` padding accommodates burst-aligned reads past the requested size. `DRAMAddress` returns `FixedPoint.fromInt(0)` (the simulator does not model physical addresses, `ScalaGenDRAM.scala:24-25`).

## `BankedMemory[T]` (SRAM)

`spatial/emul/src/emul/BankedMemory.scala:5-49` — backed by `Array[Array[T]]` indexed first by bank, then by within-bank offset. `apply(ctx, bank, ofs, ens)` (`:28-35`) returns `Array.tabulate(bank.length){i => OOB.readOrElse(...){if (ens(i).value) data.apply(flattenAddress(banks, bank(i))).apply(ofs(i).toInt) else invalid}}`. `update` is symmetric (`:37-44`). One element per lane of a banked read; each lane wraps in `OOB.readOrElse`; disabled lanes return `invalid` without touching `data`. `reset()` uses `resetValue` if `saveInit=true` (a deep clone made at construction); otherwise overwrites with `invalid` (`:16-21`).

**`BankedMemory.initMem` is a no-op** (`:46-48`) — data is injected via the constructor's `data: Array[Array[T]]`, built by codegen via `multiLoopWithIndex(dims).groupBy(bankAddr)` (`ScalaGenMemories.scala:133-143`). The emitted `$lhs.initMem(...)` call is vestigial; see Q-scal-07.

`ScalaGenMemories.emitBankedInitMem` (`ScalaGenMemories.scala:92-162`) dispatches: `mem.isRegFile || mem.isLUT` → `ShiftableMemory[T]` (`:103-119`); else → `BankedMemory[T]` (`:120-161`). For initialized memories, `multiLoopWithIndex(dims).map((is, i) => (elems(i), bankSelects(mem, is), bankOffset(mem, is))).groupBy(_._2).sortBy(_._1).map{...}` rebuilds the bank-major layout, padding with `invalid(tp)` where empty (`:131-143`). For uninitialized SRAMs, `Array.fill(banks){ Array.fill(bankDepth)(invalid) }` (`:144-148`).

`ScalaGenSRAM` lowers `SRAMNew -> emitBankedInitMem(lhs, None, op.A)` and `SRAMBankedRead`/`Write` via `emitBankedLoad`/`emitBankedStore` (`ScalaGenSRAM.scala:14-19`). Emitted call: `$mem.apply(ctx, bankAddr, ofsAddr, enables)` (`ScalaGenMemories.scala:164-170`).

## `ShiftableMemory[T]` (RegFile, LUT)

`spatial/emul/src/emul/ShiftableMemory.scala:5-71`. Single flat `Array[T]` with axis-shift support. `shiftInVec(ctx, inds, axis, elems)` (`:15-23`) walks `dims(axis)-1` down to 0, copying each cell from `j-len` to `j` along the axis: the bottom `len` entries (in reverse) overwrite the bottom of the axis — "shift in from the bottom" semantics matching hardware shift registers. `apply(ctx, addr, en)` and `apply(ctx, addr, ens)` wrap in `OOB.readOrElse` (`:39-52`); `update` is symmetric (`:54-65`).

`ScalaGenRegFile` lowers `RegFileNew -> emitBankedInitMem(lhs, inits, op.A)` (dispatches to `ShiftableMemory` because `mem.isRegFile`), `RegFileShiftIn`/`RegFileShiftInVector` to `$rf.shiftIn(...)`/`shiftInVec(...)`, and reads/writes via `emitVectorLoad`/`emitVectorStore` (`spatial/src/spatial/codegen/scalagen/ScalaGenRegFile.scala:14-32`). `ScalaGenLUTs` lowers `LUTNew(_, elems) -> emitBankedInitMem(lhs, Some(elems), op.A)` and `LUTBankedRead -> emitVectorLoad` (`spatial/src/spatial/codegen/scalagen/ScalaGenLUTs.scala:13-17`). Even though LUT is read-only semantically, scalagen represents it as a `ShiftableMemory` with init data baked in.

## `LineBuffer[T]`

`spatial/emul/src/emul/LineBuffer.scala:5-63` — circular row layout with internal counters: `bufferRow=0` (most-recently-written row), `readRow=stride` (reads), `wrCounter=0` (column-within-row), `lastWrRow=0` (previous-write row, for row-transition detection), `fullRows = dims.head + (depth-1)*stride` (total circular rows).

`swap()` (`:21-25`) decrements both pointers by `stride` with positive modulus: `bufferRow = posMod(bufferRow - stride, fullRows)`, `readRow = posMod(readRow - stride, fullRows)`, `wrCounter = 0`. `posMod(n, d) = ((n % d) + d) % d` (`:20`) handles negatives correctly. Swap is called at the end of each outer-controller body via `lineBufSwappers.getOrElse(lhs, Set()).foreach{x => emit(src"$x.swap()")}` (`ScalaGenController.scala:131`); the map is populated by `ScalaGenLineBuffer.connectBufSignals` (`ScalaGenLineBuffer.scala:77-81`).

`apply(ctx, bank, ofs, ens)` (`:31-41`) reads via `(bank(i)(0) + readRow) % fullRows` for row, then flattens `(bank(i)(1), ofs(i))`. `update(ctx, row, ens, elems)` (`:43-60`) writes at `bank0 = posMod((stride-1-row.toInt) + bufferRow, fullRows)` — `stride-1-row` reversal encodes "bottom row is newest". When `bank0 != lastWrRow`, `wrCounter` resets; `wrCounter` increments by `numWritten` after the loop.

`ScalaGenLineBuffer.LineBufferNew` (`ScalaGenLineBuffer.scala:21-39`) emits the constructor with `dims = Seq(rows, cols)`, `data = Array.fill(rows + (depth-1)*stride){ Array.fill(cols){ invalid } }`, plus `depth`, `stride`, `banks` from the memory instance.

## `Ptr[T]` (Reg, ArgIn, ArgOut, HostIO)

`spatial/emul/src/emul/Ptr.scala:5-16` is a single-cell mutable container with init-value memory: `case class Ptr[T](var x: T)` with `set`/`value`/`reset`/`initMem(init)`. `ScalaGenReg.RegNew/ArgInNew/HostIONew/ArgOutNew` all emit `object $lhs extends Ptr[T](null.asInstanceOf[T])` followed by `$lhs.initMem($init)` (`spatial/src/spatial/codegen/scalagen/ScalaGenReg.scala:14-29`). Reads use `$reg.value`, writes `$reg.set($v)`. The four `Reg` variants collapse to identical `Ptr[T]` shapes; the IR distinction is metadata for the host-device boundary.

## `RegAccumOp` and `RegAccumFMA`

`RegAccumOp(reg, in, en, op, first)` (`spatial/src/spatial/codegen/scalagen/ScalaGenReg.scala:41-55`) dispatches on `AccumOp`: `AccumAdd -> +`, `AccumMul -> *`, `AccumMax -> Number.max`, `AccumMin -> Number.min`. **`AccumFMA` and `AccumUnk` throw `Exception("This shouldn't happen!")`** (`:49-50`); the invariant is that `accumTransformer` splits `AccumFMA` into `RegAccumFMA` before codegen — see Q-scal-08. `RegAccumFMA` (`:57-64`) emits `if (first) m0*m1 else m0*m1 + reg.value`, then `reg.set(...)`.

## `DRAMTracker` and `StatTracker`

`spatial/emul/src/emul/DRAMTracker.scala:5-11` is a JVM-global `mutable.Map[Any, Int]` tracking `(ClassTag[T], bits, "read"|"write")` tuples, incremented inside `Memory.apply`/`Memory.update` (`Memory.scala:18-23`). Two simulations in the same JVM accumulate counts — never cleared automatically. See Q-scal-10. Printed at end of `Main.main` when `--resource-reporter` is set (`ScalaCodegen.scala:59-62`).

`StatTracker` (`spatial/emul/src/emul/StatTracker.scala`) is a parallel global with stack-controlled enable, used for fix/float op counting. Pushed `true` at `AccelScope` entry and popped at exit (`ScalaGenController.scala:144-145`, `:172`).

## Ground-truth status

Memory access semantics — including exact OOB behavior, address flattening, and circular line-buffer state — are anchored here. The Rust+HLS reimplementation must match:

- **Address flattening**: row-major with the same `strides = [d_1*...*d_{n-1}, ..., 1]` rule.
- **OOB on read**: return `invalid(tp)` (X-valued); log to file; do not abort.
- **OOB on write**: discard; log to file; do not abort.
- **LineBuffer**: `posMod` arithmetic on `bufferRow`/`readRow`/`wrCounter`/`lastWrRow`, `swap()` after every outer-controller iteration, "bottom row is newest" via `stride-1-row`.
- **Bank layout**: pre-baked at codegen time via `bankSelects`/`bankOffset` from the memory instance metadata. The runtime sees a 2D array indexed by `flattenAddress(banks, bank(i))` and `ofs(i)` directly.

## HLS notes

`rework`. Memory layouts in HLS will use BRAM/URAM/registers depending on banking; the simulator-side replica must match the same address-to-(bank, offset) mapping. The `OOB` log-and-fallback semantics is unusual for hardware (where OOB is undefined behavior); the Rust simulator should match scalagen for testing parity, and emit asserts in synthesis-mode.

## Interactions

- **Upstream**: memory instance metadata from `spatial.metadata.memory` (`mem.instance.nBanks`, `bankSelects(mem, is)`, `bankOffset(mem, is)`, `mem.constDims`, `mem.padding`); the IR nodes `SRAMNew`/`SRAMBankedRead`/`SRAMBankedWrite`/`RegFileNew`/etc.; the banking transform.
- **Downstream**: every controller body that reads or writes memory ([[50 - Controller Emission]]).
- **Sibling**: [[40 - FIFO LIFO Stream Simulation]] for FIFO/LIFO/Stream which use `mutable.Queue`/`Stack` rather than these classes.

## Open questions

- Q-scal-07 — `BankedMemory.initMem` no-op asymmetry with `Memory.initMem`.
- Q-scal-09 — `expandInits` padding fallback to `inits.get.head`.
- Q-scal-10 — `DRAMTracker` global state across simulations.
- Q-scal-11 — Whether `LineBuffer.swap()` should also reset `wrCounter`/`lastWrRow` invariants in edge cases (only `wrCounter` is reset).

See `open-questions-scalagen.md`.
