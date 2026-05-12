---
type: spec
concept: chiselgen-memory-emission
source_files:
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenMem.scala:19-38"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenMem.scala:40-59"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenMem.scala:73-106"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenMem.scala:108-132"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenMem.scala:134-208"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenMem.scala:210-374"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenMem.scala:227-276"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenMem.scala:281-292"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenMem.scala:350-371"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenCommon.scala:347-358"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenCommon.scala:111-123"
  - "spatial/src/spatial/codegen/chiselgen/ChiselCodegen.scala:482-489"
source_notes:
  - "[[chiselgen]]"
hls_status: chisel-specific
depends_on:
  - "[[10 - Overview]]"
  - "[[20 - Types and Ports]]"
status: draft
---

# Chiselgen — Memory Emission

## Summary

`ChiselGenMem` emits one Chisel file `m_<lhs>.scala` per memory allocation, plus per-access wiring at the use site. Every memory class — `SRAMNew`, `RegNew`, `FIFONew`, `LIFONew`, `RegFileNew`, `LineBufferNew`, `LUTNew`, `MergeBufferNew`, `FIFORegNew` — flows through a common `emitMem(lhs, init)` that materializes a `Module(new <Template>(dimensions, depth?, bitWidth, numBanks, blockCycs, neighborhood, writers, readers, BankedMemory, init?, retime, fracBits, ports, myName))` in a wrapper `class <lhs> { … }` and registers per-port `Access` objects. Per-access banking parameters (banks, offsets, enables, data) are routed through `splitAndCreate`, a chunker that breaks JVM-line-length limits by emitting helper `def create_<port>(): List[<tp>] = { … }` methods. Optimized accumulator registers (`AccumAdd`/`Mul`/`Min`/`Max`/`FMA`) bypass `emitMem` and instantiate `FixOpAccum` or `FixFMAAccum` directly. MergeBuffer is the most special case — it has its own `connectMergeEnq`/`connectMergeDeq`/`connectMergeBound`/`connectMergeInit` API.

## Semantics

### `createMemObject(lhs)(contents)` — per-memory wrapper

Every memory allocation is wrapped in a separate Chisel file via `createMemObject` at `ChiselGenCommon.scala:347-358`:

```scala
inGen(out, src"m_$lhs.scala") {
  emitHeader()
  open(src"class $lhs {")
    contents
    if (param(lhs).isDefined && spatialConfig.enableModular) {
      emit(src"""ModuleParams.addParams("${lhs}_p", ${param(lhs).get})""")
    }
  close("}")
}
emit(src"val $lhs = (new $lhs).m.io${ifaceType(lhs)}")
```

The wrapper class name matches the memory's symbol name. The user-supplied `contents` block emits per-port `Access` registrations and the actual `m = Module(new <Template>(…))`. `ModuleParams.addParams` is conditionally registered (modular only) so the runtime parameter registry can be looked up by other generated kernels that import this memory. The use-site reference `(new <lhs>).m.io<ifaceSuffix>` is a one-liner that constructs the wrapper, pulls the underlying module's `m.io`, and casts it to the interface bundle expected by the `arg`/`port` remappers (see `ifaceType` at `ChiselGenCommon.scala:111-123`: `NBufInterface`, `FixFMAAccumBundle`, `FixOpAccumBundle`, `StandardInterface`, `ShiftRegFileInterface`, `FIFOInterface`, etc.).

### `emitMem(lhs, init)` — the universal allocator

`emitMem` at `ChiselGenMem.scala:134-208` builds the parameters for a generic `Module(new <Template>(…))` call regardless of memory class. The template name is constructed at lines 148-155:

```scala
val dualsfx = if (mem.isDualPortedRead) "DualRead" else ""
val templateName =
  if (!mem.isNBuffered && name != "LineBuffer") s"$name$dualsfx("
  else { /* register HasNBufSRAM, register swappers into bufMapping */
         s"NBufMem(${name}${dualsfx}Type, " }
```

Where `name` comes from `mem.memName` (a Spatial metadata field like `"SRAM"`, `"FF"`, `"FIFO"`, `"LUT"`, `"RegFile"`, `"LineBuffer"`, `"FIFOReg"`). NBuffered memories and LineBuffers always go through the `NBufMem` template wrapper, with a `${name}DualRead?Type` enum argument selecting which underlying core to instantiate. The dual-read suffix is set when `spatialConfig.dualReadPort || mem.isDualPortedRead`.

### Banking-parameter marshalling

Banking parameters come from the memory's `BankedMemory` instance metadata at lines 162-170:

- `dimensions = paddedDims(mem, name).mkString("List[Int](", ",", ")")` — full physical dimensions including padding (see `paddedDims` at lines 108-112: `dims.zip(padding).map{case (d,p) => d+p}`).
- `numBanks = inst.nBanks` for SRAM/FIFO/etc., or just `dims` for LUT and RegFile (those are directly addressed by their natural dim, no banking decomposition).
- `blockCycs = inst.Bs` (B-vector, the block cycles per dim) — for LUT/RegFile, `List.fill(dims.size)(1)`.
- `neighborhood = inst.Ps` (P-vector, the neighborhood factor) — for LUT/RegFile, just `dims`.
- `bankingMode = "BankedMemory"` (hardcoded with `// TODO: Find correct one` comment at line 166 — see open question Q-cgs-04).
- `ofsWidth` for `LineBuffer` is `utils.math.ofsWidth(paddedDims(mem,name).last, Seq(inst.nBanks.last))`; for everything else, `utils.math.ofsWidth(volume(nBanks, Bs, Ps, paddedDims), nBanks)` (line 167-169).
- `banksWidths = utils.math.banksWidths(inst.nBanks)`.

`alphas` (the per-dimension memory phase-shift vector) is implicitly tracked through `inst.Ps` and the per-access `castgroup`/`broadcast` indices on each port — alphas don't appear directly in the template constructor.

### Per-port `Access` registration

Inside the `m_<lhs>.scala` wrapper class body at lines 174-183, each writer and reader gets a `lazy val w<i> = Access(hashCode, muxPort, muxOfs, castgroup, broadcast, shiftAxis, PortInfo(bufferPort, accessWidth, ofsWidth, banksWidths, bitWidth, residuals))`. The `Access` object packs the metadata required by the runtime template: a hashCode for ledger-side identification, muxPort/muxOfs from banking analysis, castgroup and broadcast indices for bank-resolution math, the optional shift axis (RegFile shifters), the buffer port (which N-buffer slot this access lives in), the access width (parallelism), the offset width, per-bank-axis widths, the data bit-width, and the residual generators (modular-arithmetic expressions that resolve the bank from iteration variables). Memories with zero readers/writers get an `AccessHelper.singular(32)` placeholder (lines 178, 184).

### `Module(new <Template>(…))` call

At lines 186-200, the emission is `lazy val m = Module(new $templateName($dimensions, $depth $bitWidth, $numBanks, $blockCycs, $neighborhood, $writers, $readers, $bankingMode, $initStr, $retime, $fracBits, $numPorts, myName = "$mem"))`, followed by `m.io${ifaceType(mem)} <> DontCare`. The retime parameter is `!spatialConfig.enableAsyncMem && spatialConfig.enableRetiming` — async mems disable internal retiming (Q-cgs-09). `depth` is empty unless `mem.isNBuffered` (line 158). For FIFO/FIFOReg, writers/readers are registered into `activesMap` (lines 202-205) so `connectAccessActivesIn` calls have stable lane indices. If the memory has no resetters and isn't a breaker, `m.io.reset := false.B` is emitted (line 206).

### `splitAndCreate` — JVM line-length workaround

`splitAndCreate(lhs, mem, port, tp, payload)` at `ChiselGenMem.scala:19-38` solves a practical Scala/JVM problem: a heavily-banked SRAM with 64 banks and 8 readers can produce a `List[UInt](b00.r, …, b63.r)` literal that exceeds the JVM's per-method bytecode size. If the total payload stays under `zipThreshold` (150 chars or the smallest individual element), emit a single `val <port> = List[<tp>](<payload>)`. Otherwise emit a `def create_<port>(): List[<tp>] = { … List0 ++ List1 ++ … }` helper containing smaller sub-lists, then `val <port> = create_<port>()`.

Called from `emitRead`/`emitWrite`/`emitReadInterface` for `<lhs>_banks`, `<lhs>_ofs`, `<lhs>_en`, `<lhs>_data`. MergeBuffer ops do *not* use it (lines 350-371) — see Q-cgs-06.

### Banked read/write emission

`emitRead(lhs, mem, bank, ofs, ens, enString)` at lines 73-91 generates: an output wire (`Vec(N)` if access width >1, else scalar); `<lhs>_banks`/`<lhs>_ofs`/`<lhs>_en` lists via `splitAndCreate` (broadcast addresses become `"0.U"`); a shared `<lhs>_shared_en = nonlut_mask && implicitEnableRead && commonEns` wire; and the call `$lhs.toSeq.zip($mem.connectRPort(${lhs.hashCode}, <lhs>_banks, <lhs>_ofs, $backpressure, <lhs>_en.map(_ && <lhs>_shared_en), ${!mem.broadcastsAnyRead}))`. LUTs skip the forward-pressure mask (`nonlut_mask = "true.B"`, line 87).

`emitWrite` (lines 93-106) is mirrored: `<lhs>_data` is appended via `splitAndCreate`, and the call becomes `$mem.connectWPort(${lhs.hashCode}, <lhs>_banks, <lhs>_ofs, <lhs>_data, <lhs>_en.map(_ && <implicitEnableWrite> && <commonEns>))`.

`implicitEnableRead` (lines 40-43) is `~$break && ~$forwardpressure & DL($datapathEn & $iiIssue, fullDelay, true)` for normal mems, or `~$break && $done` for FIFOReg in an outer controller (with explicit "Don't know why this is the rule, but this is what works" comment — see Q-cgs-07). `implicitEnableWrite` (lines 45-51) always includes `$flowEnable = ~$break && $backpressure`, plus `$forwardpressure` if `haltIfStarved`.

### `optimizedRegType` — accumulator specialization

`RegNew` at `ChiselGenMem.scala:227-276` dispatches on `lhs.optimizedRegType: Option[AccumType]`. `None` → falls through to `emitMem(lhs, Some(List(init)))` (the standard register path). `AccumAdd`/`AccumMul`/`AccumMin`/`AccumMax` emit `Module(new FixOpAccum(Accum.<Op>, numWriters, cycleLatency, opLatency, s, d, f, init))` directly inside `createMemObject(lhs) { … }`. `opLatency = max(1.0, latencyOption("Fix<Op>", Some(d+f)))`. `cycleLatency = opLatency + RegRead + RegWrite` latencies. `AccumFMA` emits `Module(new FixFMAAccum(...))`. `AccumUnk` throws (line 275).

The optimized path replaces `StandardInterface` with `FixOpAccumBundle` or `FixFMAAccumBundle` in both `arg` and `port` (see `[[20 - Types and Ports]]`). `RegAccumOp` (lines 281-286) calls `reg.connectWPort(idx, data.r, en && invisEn, DL($ctrDone, fullDelay, true), first)` — same as a normal register write but with an explicit `first` flag. `RegAccumFMA` (lines 287-292) takes two data fields.

### Per-class dispatch tour

The dispatch at `ChiselGenMem.scala:210-374` is class-by-class:

- **SRAM** (213-215): `emitMem(lhs, None)` + `emitRead`/`emitWrite`.
- **FIFOReg** (218-224): `emitMem(lhs, Some(List(init)))` + `emitWrite`/`emitRead` + `connectAccessActivesIn(activesMap(lhs), <ens>)`.
- **Reg** (227-292): see optimizedRegType section above.
- **RegFile** (296-303): vector reads/writes, banked shift-in with explicit axis-of-shift forwarded into `emitWrite`.
- **LineBuffer** (306-308): only valid if N-buffered (throws at line 145).
- **FIFO** (311-331): status reads (`empty`/`full`/`almostEmpty`/`almostFull`/`numel`) as direct field reads. `FIFOBankedDeq`/`FIFOBankedPriorityDeq` use `emitRead` + per-lane `connectAccessActivesIn` keyed on the OR of all enable sets. `FIFODeqInterface` calls `emitReadInterface`. `FIFOBankedEnq` uses `emitWrite` + actives registration.
- **LIFO** (334-343): same shape as FIFO with `Pop`/`Push`.
- **LUT** (346-347): `LUTNew` carries `init` into `emitMem`. `LUTBankedRead` is normal `emitRead`.
- **MergeBuffer** (350-371): unique. `MergeBufferNew` emits `Module(new MergeBuffer(ways, par, bitWidth, readers))` directly (no `emitMem`). Per-op wrappers call `connectMergeEnq(way, dataList, enList)`, `connectMergeDeq(readerIdx, en)`, `connectMergeBound(way, data.r, en & invEn)`, `connectMergeInit(data.r, en & invEn)`. `MergeBufferBankedDeq` looks up its reader index via `merge.readers.collect{...}.indexOf(lhs)` (line 361).

### `ledgerized(node)` and per-controller wiring

`ledgerized(node)` at `ChiselCodegen.scala:482-489` returns true for a memory iff it is not a DRAM, ArgIn, StreamIn, or StreamOut. This drives the `connectWires<i>(module)` emission at `ChiselGenController.scala:163-177`: for ledgerized memories, `<mem>.connectLedger(module.io.in_<mem>)` is called (the runtime ledger fans the partial IO connections from each kernel back into the central memory module), with extra `<>` lines for special interfaces (`MergeBuffer.output`, `Breaker.rPort`). Non-ledgerized memories get `module.io.in_<mem> <> <mem>` directly.

## Interactions

- **Banking metadata source**: `mem.instance.{depth, nBanks, Bs, Ps, alphas}`, `mem.constDims`, `mem.getPadding` — all populated by upstream banking analysis.
- **Retiming metadata**: `lhs.fullDelay` for the `DL` wrapper inside `implicitEnableRead`/`implicitEnableWrite`. `lhs.II` for the per-lane datapath enable.
- **Activity tracking**: `connectAccessActivesIn(activesMap(lhs), …)` ties FIFO/FIFOReg/LIFO accesses to a controller-stack activity lane used by `getForwardPressure`/`getBackPressure` (see `[[50 - Streams and DRAM]]`).
- **NBufMem swappers**: `mem.swappers.zipWithIndex` (line 151) populates `bufMapping` so the parent pipeline-stage controller emits `connectStageCtrl(done, baseEn, port)` (see `[[40 - Controller Emission]]`'s `connectBufs`).

## HLS notes

The `Module(new …)` wrapper class structure does not transfer to HLS directly, but the parameter set does: dimensions, depth, bitWidth, banks, blockCycs (Bs), neighborhood (Ps), retime, fracBits, port count, and per-port (muxPort, muxOfs, castgroup, broadcast, shiftAxis, bufferPort, accessWidth, ofsWidth, banksWidths, residual generators) is the canonical representation a Rust/HLS reimplementation must consume. `splitAndCreate` is irrelevant in HLS because there's no JVM line-length limit. `optimizedRegType`'s collapse of accumulator+register into a single `FixOpAccum` template is a meaningful DSL-level optimization that should survive in HLS — accumulators with 1-cycle II are a common pattern that benefits from the fused implementation.

## Open questions

See `20 - Research Notes/10 - Deep Dives/open-questions-chiselgen.md`:
- Q-cgs-04: `bankingMode` is hardcoded to `"BankedMemory"` with a TODO. What are the valid alternative modes?
- Q-cgs-06: Why doesn't `MergeBufferNew` use `splitAndCreate`?
- Q-cgs-07: `FIFORegNew` read in an outer controller uses `~$break && $done` with a "Don't know why this is the rule, but this is what works" comment. What's the semantic justification?
- Q-cgs-09: `enableAsyncMem` disables retiming for *all* memories. Is that correct?
