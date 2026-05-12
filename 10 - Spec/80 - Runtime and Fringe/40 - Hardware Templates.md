---
type: spec
concept: Hardware Templates
source_files:
  - "fringe/src/fringe/templates/memory/MemParams.scala:7-54"
  - "fringe/src/fringe/templates/memory/MemInterfaceType.scala:12-220"
  - "fringe/src/fringe/templates/memory/MemPrimitives.scala:17-157"
  - "fringe/src/fringe/templates/memory/MemPrimitives.scala:303-436"
  - "fringe/src/fringe/templates/memory/NBuffers.scala:10-322"
  - "fringe/src/fringe/templates/memory/RegFile.scala:15-112"
  - "fringe/src/fringe/templates/memory/Accum.scala:16-193"
  - "fringe/src/fringe/templates/memory/MergeBuffer.scala:10-140"
  - "fringe/src/fringe/templates/memory/DRAMAllocator.scala:9-89"
  - "fringe/src/fringe/templates/counters/Counter.scala:24-563"
  - "fringe/src/fringe/templates/counters/FringeCounter.scala:11-44"
  - "fringe/src/fringe/templates/Controllers.scala:9-332"
  - "fringe/src/fringe/templates/retiming/RetimeShiftRegister.scala:6-59"
  - "fringe/src/fringe/templates/retiming/Offset.scala:5-14"
source_notes:
  - "[[fringe-and-targets]]"
hls_status: chisel-specific
hls_reason: "These are reusable hardware semantics but implemented as Chisel templates and black boxes"
depends_on:
  - "[[30 - Ledger and Kernel]]"
  - "[[10 - Fringe Architecture]]"
status: draft
---

# Hardware Templates

## Summary

Fringe templates are the Chisel hardware library that generated controllers instantiate for memories, counters, state machines, retiming, accumulators, allocators, and merge structures. They are not a general HDL-independent standard library: most templates assume Chisel `Module`, `Bundle`, `Decoupled`, `DontCare`, `RegInit`, and target globals. Still, they define important behavior for the current Spatial backend and therefore form the reference for HLS replacement designs.

## Memory templates

Memory construction is parameter-driven. `MemParams` records interface type, logical dimensions, bit width, banks, blocks, neighborhood, write/read access mappings, banking mode, initialization values, sync-memory flag, fractional bits, buffer status, number of active signals, and module name; `NBufParams` wraps a memory type and `MemParams` for N-buffered memories (`fringe/src/fringe/templates/memory/MemParams.scala:7-54`). Memory interfaces define read/write port bundles, standard SRAM-style interfaces, shift-register file interfaces, FIFO interfaces, N-buffer interfaces, accumulator bundles, and helper methods that use Ledger when connections cross kernel boundaries (`fringe/src/fringe/templates/memory/MemInterfaceType.scala:12-220`).

The connection helpers are part of the template semantics, not just boilerplate. `MemInterface.connectWPort` looks up the write base from an access hash, assigns banks/offset/data/reset, selects either shift-enable or normal enable based on the access mapping, and records the exposed write port in Ledger (`fringe/src/fringe/templates/memory/MemInterfaceType.scala:80-95`). `connectRPort` similarly wires banks, offsets, backpressure, and non-broadcast enables, records a read-port exposure, and returns the read outputs (`fringe/src/fringe/templates/memory/MemInterfaceType.scala:97-113`). FIFO and N-buffer interfaces extend that pattern with active loopbacks and stage-control exposure (`fringe/src/fringe/templates/memory/MemInterfaceType.scala:137-201`).

`MemPrimitive` selects its IO shape from `p.iface`, initializes the concrete interface to `DontCare`, and provides masked buffer read/write connection helpers (`fringe/src/fringe/templates/memory/MemPrimitives.scala:17-48`). `BankedSRAM` creates one `Mem1D` per physical bank, computes bank coordinates, routes writes to banks whose visible-bank sets can see the physical bank, uses `fatMux("PriorityMux", ...)` for conflicting write choices, routes reads through bank-match and sticky-select logic, forwards broadcast/castgroup outputs, and retimes read bank selection by target SRAM load latency (`fringe/src/fringe/templates/memory/MemPrimitives.scala:51-157`). Register-like memories include scalar `FF`, `FIFOReg`, full FIFO, and LIFO templates deeper in the same file (`fringe/src/fringe/templates/memory/MemPrimitives.scala:303-436`).

`RegFile` is the host-visible scalar storage. It computes target-specific address width, splits arg-in and arg-out register ranges, creates one `FringeFF` per register, supports host writes and accelerator arg-out writes, includes a ZCU-specific doubled register ID path, muxes readback, and returns `argIns` by filtering registers in the arg-in range (`fringe/src/fringe/templates/memory/RegFile.scala:15-112`). This register layout is consumed by the common Fringe shell and AXI-Lite bridges.

N-buffering is handled by `NBufController` and `NBufMem`. The controller latches stage enables and dones, emits a swap pulse when every enabled buffer stage is done, and maintains per-writer and per-reader buffer-state counters (`fringe/src/fringe/templates/memory/NBuffers.scala:10-60`). `NBufMem` instantiates the physical memory for each buffer for SRAM, dual-read SRAM, FF, shift-register file, or line-buffer cases, routes write/read ports through buffer-state masks, and contains line-buffer-specific row/column correction logic (`fringe/src/fringe/templates/memory/NBuffers.scala:63-280`). `RegChainPass` is a small N-buffered FF wrapper for passing counter values between metapipe stages (`fringe/src/fringe/templates/memory/NBuffers.scala:284-322`).

## Specialized memory structures

`Accum` defines `Add`, `Mul`, `Min`, and `Max` modes, while `FixFMAAccum` and `FixOpAccum` build fixed-point accumulation hardware with lane counters, active-lane selection, first-round/reset/drain state, per-lane FF banks, retimed writes, and a retimed drain reduction (`fringe/src/fringe/templates/memory/Accum.scala:16-193`). `FixFMAAccum` explicitly calls `Math.fma`, so it depends on the target `BigIP` arithmetic backend (`fringe/src/fringe/templates/memory/Accum.scala:80-94`).

`MergeBuffer` supplies utilities for merge-heavy templates: `UpDownCounter`, `BarrelShifter`, `FIFOPeek`, and `SortPipe` implement saturating up/down counts, power-of-two barrel shifts, peekable FIFO buffering, and bitonic-sort-like stage generation (`fringe/src/fringe/templates/memory/MergeBuffer.scala:10-140`). Later classes in that file implement the recursive merge buffer and Ledger-aware IO connections (see `fringe/src/fringe/templates/memory/MergeBuffer.scala:306-369`). `DRAMAllocator` serializes valid app allocation/deallocation requests, stores the most recent alloc/size/dims/addr state, and emits heap requests with either requested size or remembered address (`fringe/src/fringe/templates/memory/DRAMAllocator.scala:9-89`).

## Counters, controllers, and retiming

The counter file contains several unrelated counter families. `NBufCtr` is a wrapping pointer counter for buffer state, `IncDincCtr` and `CompactingIncDincCtr` track FIFO occupancy under push/pop activity, `IICounter` enforces initiation interval and carries a TODO about first-cycle issue semantics, `CompactingCounter` counts enabled lanes, `SingleCounter` handles static and dynamic start/stop/stride with parallel lanes and out-of-bound checks, signed counter variants serve FILO-style structures, and `CounterChain` composes nested counters with innermost-fastest enable propagation (`fringe/src/fringe/templates/counters/Counter.scala:24-563`). `FringeCounter` is a simpler unsigned counter used by the shell timeout path (`fringe/src/fringe/templates/counters/FringeCounter.scala:11-44`).

Controller templates are specified in [[30 - Ledger and Kernel]], but they also belong to this hardware-template layer: `ControlInterface`, `ControlParams`, schedule singleton objects, `OuterControl`, and `InnerControl` define the reusable state-machine hardware (`fringe/src/fringe/templates/Controllers.scala:9-332`). Retiming uses `RetimeWrapper` and `RetimeWrapperWithReset` to wrap a `RetimeShiftRegister` black box with Chisel clock/reset wiring; the black box carries `WIDTH` and `STAGES` parameters (`fringe/src/fringe/templates/retiming/RetimeShiftRegister.scala:6-59`). `Offset.scala` is explicitly marked unused and wraps a legacy Chisel `Pipe` (`fringe/src/fringe/templates/retiming/Offset.scala:5-14`).

## HLS notes

Most templates should be re-expressed as HLS constructs or small runtime-independent libraries, not mechanically translated from Chisel. The semantic units to preserve are memory banking visibility, N-buffer swap rules, scalar register layout, accumulator drain timing, counter-chain done/noop/out-of-bound behavior, controller schedules, and retiming delays. The HLS backend should also decide which templates disappear into compiler scheduling or vendor HLS pragmas rather than becoming handwritten RTL.

## Open questions

- [[open-questions-fringe-targets#Q-ft-12 - 2026-04-25 IICounter first-cycle issue dependency|Q-ft-12]]
