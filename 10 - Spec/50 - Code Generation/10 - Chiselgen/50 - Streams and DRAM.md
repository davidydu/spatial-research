---
type: spec
concept: chiselgen-streams-and-dram
source_files:
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenDRAM.scala:1-87"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenStream.scala:1-200"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenCommon.scala:23-26"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenCommon.scala:35-40"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenCommon.scala:215-280"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenCommon.scala:416-453"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenInterface.scala:17-30"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenInterface.scala:31-39"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenInterface.scala:102-117"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenInterface.scala:121-190"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenController.scala:362-413"
source_notes:
  - "[[chiselgen]]"
hls_status: chisel-specific
depends_on:
  - "[[10 - Overview]]"
  - "[[20 - Types and Ports]]"
  - "[[40 - Controller Emission]]"
status: draft
---

# Chiselgen — Streams and DRAM

## Summary

Streams and DRAM are the boundary between the accelerator's internal datapath and the outside world (host, off-chip memory, AXI peripherals). `ChiselGenDRAM` handles the DRAM allocation/deallocation/address ops and dispatches `connectDRAMStreams(dram)` to wire each `FringeTransfer` into the Fringe `accelUnit.io.memStreams.{loads,stores,gathers,scatters}` AXI ports. `ChiselGenStream` handles per-bus stream emission for `BurstCmdBus`, `BurstFullDataBus`, `BurstDataBus`, `BurstAckBus`, `GatherAddrBus`, `GatherDataBus`, `ScatterCmdBus`, `ScatterAckBus`, and three AXI4-Stream widths (64/256/512). `ChiselGenInterface` handles ArgIn / ArgOut / HostIO scalar I/O and emits the boundary metadata in `Instantiator.scala` and `ArgAPI.scala`. The cross-cutting forward/back-pressure system lives in `ChiselGenCommon` and is the way every controller computes its run-condition: composing FIFO `~empty` / `~full`, merge-buffer status, stream-in `valid`, stream-out `ready`, priority-deq groups, and blackbox per-field pressures.

## Semantics

### `connectDRAMStreams(dram)` — wiring DRAM transfers to Fringe

`connectDRAMStreams(dram)` at `ChiselGenCommon.scala:416-453` is called once per DRAM allocation (from `DRAMHostNew` and from the `AccelScope` walker that handles `DRAMAccelNew`). For each kind of side-channel — load, store, gather, scatter — it walks the DRAM's transfer records (`dram.loadStreams`, `dram.storeStreams`, etc.), each of which exposes `addrStream` / `dataStream` / `ackStream` (some kinds omit `ackStream`).

For each transfer, it forces emission of the wire bindings:

```scala
forceEmit(src"val ${f.addrStream} = accelUnit.io.memStreams.loads(${loadStreams.size}).cmd  // StreamOut")
if (enableModular)
  forceEmit(src"""ModuleParams.addParams("${f.addrStream}_p", ${param(f.addrStream).get})""")
forceEmit(src"val ${f.dataStream} = accelUnit.io.memStreams.loads(${loadStreams.size}).data // StreamIn")
RemoteMemories += f.addrStream; RemoteMemories += f.dataStream
val par = f.dataStream.readers.head match {
  case Op(e@StreamInBankedRead(strm, ens)) => ens.length
}
loadStreams += (f -> (s"""StreamParInfo(${bitWidth(dram.tp.typeArgs.head)}, $par, 0)""", loadStreams.size))
```

The four maps (`loadStreams`, `storeStreams`, `gatherStreams`, `scatterStreams` declared at `ChiselGenCommon.scala:23-26`) are keyed by the Spatial transfer sym, with values `(StreamParInfo("…"), index)`. The `StreamParInfo` string is later dropped into `Instantiator.scala` (per `ChiselGenInterface.scala:134-137`):

```
val loadStreamInfo = List(StreamParInfo(64,16,0), StreamParInfo(64,16,0), …)
```

The streams are also inserted into `RemoteMemories` (the Spatial-level escape set) so downstream `getInputs` walks find them.

`storeStreams` differ from `loadStreams` only in shape: there's also an `ackStream` wired to `accelUnit.io.memStreams.stores(<N>).wresp`, and the parallelism is computed from the *writer* (not reader): `f.dataStream.writers.head match { case Op(e@StreamOutBankedWrite(_, _, ens)) => ens.length }`. Gather streams have no `ackStream`. Scatter streams have an `ackStream` from the scatter command bus and the par is computed from `f.addrStream.writers`, not the data stream.

### `ChiselGenDRAM.gen` — DRAM allocator dispatch

`ChiselGenDRAM` at `ChiselGenDRAM.scala:1-87`:

- **`DRAMHostNew(_,_)`** (lines 17-22): registers the DRAM into `hostDrams`, calls `connectDRAMStreams(lhs)`, then emits a `Wire(new FixedPoint(true, 64, 0))` whose `.r` is connected to `accelUnit.io.argIns(api.<sym>_ptr)`. The DRAM pointer is therefore an ArgIn (assigned an ArgIn slot) consumed at the accelerator side.
- **`DRAMAccelNew(dim)`** (line 26): explicitly empty here. The `DRAMAllocator` module is instantiated *inside* the `AccelScope` dispatch at `ChiselGenController.scala:362-413` (lines 363-376), which walks `RemoteMemories.all` for accel-side DRAMs and emits `Module(new DRAMAllocator($dim, $reqCount)).io` for each one. This separation is important: per-allocator state needs to live inside the accelerator's reset/clock domain, not in the post-main wiring.
- **`DRAMAlloc(dram, dims)`** (lines 28-38): if `dram` is an `AccelNew`, allocate a request id (`requesters.size`), compute `invEnable = DL($datapathEn & $iiIssue, lhs.fullDelay, true)`, and emit `<dram>.connectAlloc($id, List(<dim0>.r, …), $invEnable)`. Updates `requesters += (lhs -> id)`.
- **`DRAMIsAlloc(dram)`** (lines 40-47): for an accel-DRAM, `val $lhs = $dram.output.isAlloc`. For a host-DRAM, `val $lhs = true.B` (host-allocated DRAM is always live).
- **`DRAMDealloc(dram)`** (lines 49-58): same shape as `DRAMAlloc` but emits `<dram>.connectDealloc($id, $invEnable)`.
- **`DRAMAddress(dram)`** (lines 60-67): for accel-DRAM, `val $lhs = <dram>.output.addr`. For host-DRAM, `val $lhs = $dram` (the wire is the address).

### `ChiselGenStream` — per-bus emission

`ChiselGenStream` at `ChiselGenStream.scala:1-200`:

- **`StreamInNew(bus)` / `StreamOutNew(bus)`** (lines 18-32): for AXI4-Stream buses, register the index into `axiStreamIns`/`axiStreamOuts` and emit `val $lhs = accelUnit.io.axiStreamsIn(<n>)` (or `axiStreamsOut`). For non-AXI buses, do nothing — those streams are wired by `connectDRAMStreams` instead.

- **`StreamOutBankedWrite(stream, data, ens)`** (lines 34-136): the bus-specific write-side emission. The valid signal is set per-lane: `${stream}.valid := DL($datapathEn & $iiIssue, fullDelay, true) & $en & $backpressure`. Then dispatched on bus type:
  - `BurstCmdBus`: extract `addr` and `size` bitfields from `data` (via `getField`).
  - `BurstFullDataBus`: extract `wdata` (`_1`) and `wstrb` (`_2`). Single-lane writes set `bits.wdata(0)`/`bits.wstrb` directly; multi-lane writes set `bits.wdata(i)` per lane and concat-reduce strb fields.
  - `GatherAddrBus`: per-lane `bits.addr(i) := $d.r`.
  - `ScatterCmdBus`: per-lane `bits.addr.addr(i)` and `bits.wdata(i)` from the packed data tuple `(_1 = data, _2 = addr)`.
  - `AxiStream{64,256,512}Bus`: two paths per width. If the data is the full `AxiStream<W>` type, copy all eight TDATA/TSTRB/TKEEP/TID/TDEST/TLAST/TUSER fields. If not, only set TDATA, zero-fill TSTRB/TKEEP, set TID/TDEST from the bus parameters, TLAST=0, TUSER=4 (or 0 for 64-bit). The "full type" path emits a `warn(...)` because `tid`/`tdest` from the bus declaration are ignored.

- **`StreamInBankedRead(strm, ens)`** (lines 139-175): mirror of `StreamOutBankedWrite`. `strm.ready := and(ens.flatten) & $datapathEn`. Dispatch on bus type:
  - `BurstDataBus`: `lhs(i).r := strm.bits.rdata(i).r`.
  - `GatherDataBus`: `lhs(i).r := strm.bits(i).r`.
  - `AxiStream<W>Bus` "full" path: `lhs(i) := Cat(TUSER, TDEST, TID, TLAST, TKEEP, TSTRB, TDATA)`.
  - `AxiStream<W>Bus` "TDATA-only" path: `lhs(i).r := strm.TDATA.r` plus a stricter ready: `strm.ready := and(ens) & $datapathEn & (strm.TID === tid.U) & (strm.TDEST === tdest.U)`. The TID/TDEST mask makes a single physical AXI stream demultiplex to multiple Spatial `StreamIn`s by route.

`emitPostMain` at lines 181-199 enforces a hard limit of 1 AxiStream In and 1 AxiStream Out: `if (axiStreamIns.size > 1) error(...)` (line 185). The error message says "easy to support more, we just haven't implemented it yet" — see open question Q-cgs-11.

### `getForwardPressure` / `getBackPressure` — composing run-conditions

These are the controller-level run-condition functions at `ChiselGenCommon.scala:249-279`. They return a single `Bool` expression that ANDs across the controller's read or write streams (per-controller, not per-stream).

`getForwardPressure(sym)` (lines 249-264) splits into "regular" and "priority" sources. Each contributing element:

- `StreamInNew(bus)` → `$fifo.valid`.
- `FIFONew` / `FIFORegNew` → `(~$fifo.empty.D(II-1) | ~FIFOForwardActive(sym, fifo))` — either there's data, or the controller isn't trying to read it this cycle. `D(II-1)` is the inter-iteration delay so the controller looks at the future-state of the FIFO.
- `MergeBufferNew` → `~$merge.output.empty.D(II-1)`.
- `CtrlBlackboxUse` and `StreamStruct`-bound syms with non-empty used-fields → `$bbox.getForwardPressures([f1,f2,…]).D(II-1)`.

Priority-deq groups (FIFOs that participate in a single arbitrated group) contribute as `or` within each group, AND'd across groups.

`getBackPressure(sym)` (lines 266-279) is the mirror for write-side: `StreamOutNew → ready`, `FIFONew → (~full.D(II-1) | ~currently_enqueueing)`, `MergeBufferNew → ~output.full(<way>).D(II-1)` keyed on the writer's lane. CtrlBlackbox back-pressures are commented out (line 277) — see Q-cgs-12.

`hasForwardPressure(sym)` and `hasBackPressure(sym)` at lines 247-248 are the predicates that gate whether instrumentation emits stalls/idles counters and whether `forwardpressure` enters the `DL` retiming wrapper. `FIFOForwardActive(sym, fifo)` (lines 215-223) OR-aggregates `fifo.active(<lane>).out` over all readers of `fifo` whose parent is `sym.s.get`. The activity lane index comes from `activesMap` (populated in `ChiselGenMem` per FIFO/LIFO/FIFOReg access).

### `argIns` / `argOuts` / `argIOs` — scalar boundary registration

`ChiselGenInterface.scala:17-39` handles scalar I/O:

- **`InputArguments()`** (line 17): no-op.
- **`ArgInNew(init)`** (lines 18-21): registers `(lhs -> argIns.size)` into `argIns`. Force-emits `val $lhs = accelUnit.io.argIns(api.<id>_arg)`.
- **`HostIONew(init)`** (lines 22-30): registers into `argIOs`. Maps each writer to a `MultiArgOut` port slot. Emits the `MultiArgOut` wire plus the Mux1H wiring that picks one writer's value based on its `valid`.
- **`ArgOutNew(init)`** (lines 31-39): registers into `argOuts`. Same `MultiArgOut` setup as HostIO. The post-host argument index is `accelUnit.io_numArgIOs_reg + argOuts(lhs)`.

`RegRead`/`RegWrite` for ArgIn / ArgOut / HostIO are specialized at lines 51-100. The signed 64-bit ArgOut path with `d+f < 64` sign-extends via `util.Cat(util.Fill(64-d-f, $v.msb), $v.r)` (lines 73-83). Other widths just pad.

`FringeDenseLoad`/`FringeSparseLoad`/`FringeDenseStore`/`FringeSparseStore` at lines 102-117 register `HasTileLoad`/`HasTileStore`/`HasGather`/`HasScatter`/`HasAlignedLoad`/`HasUnalignedLoad`/`HasAlignedStore`/`HasUnalignedStore` into `appPropertyStats` but emit no code — the actual transfer logic is wired elsewhere via `connectDRAMStreams`.

### `ArgAPI.scala` — the argument-index manifest

`emitPostMain` at `ChiselGenInterface.scala:121-190` writes three files:

- **`Instantiator.scala`** (lines 122-139): emits `numArgIns_reg`, `numArgOuts_reg`, `numArgIOs_reg`, `numArgIns_mem`, the four `*StreamInfo` lists (sorted by index), and per-arg comments mapping each sym to its `argIns(i)`.
- **`AccelWrapper.scala`** (lines 141-154): same shape with `io_*` prefixes.
- **`ArgAPI.scala`** (lines 156-188): the canonical argument-index manifest:

```scala
package accel
object api {
  // ArgIns
  val <ID0>_arg = 0
  val <ID1>_arg = 1
  …
  // DRAM Ptrs:
  val <DRAM0>_ptr = N
  …
  // ArgIOs
  val <IO0>_arg = N+M
  …
  // ArgOuts
  val <OUT0>_arg = N+M+P
  …
  // Instrumentation Counters
  val numCtrls = …
  val <CTRL>_instrctr = …
  val <CTRL>_cycles_arg = …
  val <CTRL>_iters_arg = …
  // (if has back/forward pressure)
  val <CTRL>_stalled_arg = …
  val <CTRL>_idle_arg = …
  // Breakpoints
  val <SYM>_exit_arg = …
}
```

The address layout is fixed: `[0 … numArgIns_reg)` are ArgIns, `[numArgIns_reg … numArgIns_reg + hostDrams.size)` are DRAM pointers, then ArgIOs, then ArgOuts, then per-controller instrumentation counters (2 or 4 per controller — the last two are emitted only if the controller has back- or forward-pressure), then breakpoints. The `instrumentCounterIndex(s)` helper at `ChiselGenCommon.scala:49-55` does the layout math.

## Interactions

- **`RemoteMemories`** is the Spatial-level escape set. `connectDRAMStreams` adds DRAM streams to it; `getInputs` (used by `writeKernelClass`) consults it. This is the cross-trait coupling that lets a deeply-nested controller transparently reach a DRAM transfer at the accel root.
- **`activesMap`** is populated by `ChiselGenMem.emitMem` for FIFO/FIFOReg/LIFO and consumed by `FIFOForwardActive`/`FIFOBackwardActive` in `getForwardPressure`/`getBackPressure`.
- **`appPropertyStats`** is updated by `FringeDenseLoad`/etc. and emitted as the `App Characteristics` comment in `AccelWrapper.scala` (see `[[10 - Overview]]`).
- **`hasForwardPressure(sym)` / `hasBackPressure(sym)`** are queried by `ChiselGenController.createAndTieInstrs` to decide whether to emit `stalls_<lhs>` / `idles_<lhs>` instrumentation counters.

## HLS notes

The forward/back-pressure composition is the most semantically rich part of this layer. Every FIFO contributes `(~empty.D(II-1) | ~currently_dequeueing)`, which is the standard "empty-with-grace-period" predicate that lets a controller not stall when it's not actually trying to read. An HLS port must preserve this composition to match controller scheduling. The AXI4-Stream `TID`/`TDEST` filtering for non-full-AXI streams is a multiplexing convention that lets one physical AXI port serve multiple `StreamIn`s — this is a host-side Fringe convention, not a DSL concept, and an HLS reimplementation has freedom to use a different demultiplexing scheme. The 1-AXI-stream-in / 1-AXI-stream-out limit (`ChiselGenStream.scala:185-186`) is purely a current-implementation guard, not a semantic property.

## Open questions

See `20 - Research Notes/10 - Deep Dives/open-questions-chiselgen.md`:
- Q-cgs-11: Is the 1-stream-in / 1-stream-out limit a hard runtime/RTL constraint or just plumbing?
- Q-cgs-12: `getBackPressure` for `CtrlBlackboxUse` is commented out (`ChiselGenCommon.scala:277`). Does this mean a controlled blackbox can't backpressure the kernel that contains it?
