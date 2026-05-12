---
type: spec
concept: Fringe Architecture
source_files:
  - "fringe/src/fringe/SpatialIP.scala:5-39"
  - "fringe/src/fringe/AccelTopInterface.scala:9-64"
  - "fringe/src/fringe/targets/DeviceTarget.scala:7-67"
  - "fringe/src/fringe/Fringe.scala:20-218"
  - "fringe/src/fringe/FringeBundles.scala:39-89"
  - "fringe/src/fringe/FringeBundles.scala:91-96"
  - "fringe/src/fringe/FringeBundles.scala:145-152"
  - "fringe/src/fringe/globals.scala:8-79"
  - "fringe/src/fringe/ChannelAssignment.scala:3-34"
  - "fringe/src/fringe/targets/zynq/Zynq.scala:7-70"
  - "fringe/src/fringe/targets/zynq/FringeZynq.scala:31-145"
  - "fringe/src/fringe/targets/SimTarget.scala:8-50"
source_notes:
  - "[[fringe-and-targets]]"
hls_status: chisel-specific
hls_reason: "This is the Chisel/board-shell runtime architecture; HLS should preserve the ABI concepts, not the elaboration mechanism"
depends_on:
  - "[[60 - Instantiation]]"
status: draft
---

# Fringe Architecture

## Summary

Fringe is the Chisel-side runtime shell between generated accelerator hardware and a board or simulator target. The generated `Instantiator` creates one `SpatialIP`, and `SpatialIP` immediately string-matches the requested target, assigns `globals.target`, installs the target's `IO` factory hook, constructs the delayed `AbstractAccelUnit`, marks unused accelerator IO as `DontCare`, and delegates the real top-level shell to `globals.target.addFringeAndCreateIP(reset, accel)` (`fringe/src/fringe/SpatialIP.scala:18-39`). The base `SpatialIPInterface` is only a scalar register-file interface; concrete targets extend it with AXI, stream, debug, or simulator ports (`fringe/src/fringe/SpatialIP.scala:5-12`). This means the target, not the generated accelerator, owns the external pin shape.

## Core interfaces

The accelerator contract is split between `AccelInterface` and `AbstractAccelUnit`. `AccelInterface` names the control pins (`done`, `reset`, `enable`), scalar arguments, app memory streams, AXI streams, and heap IO; `CustomAccelInterface` assigns directions, using flipped app memory streams and flipped heap IO so generated accelerator modules see those as accelerator-local interfaces (`fringe/src/fringe/AccelTopInterface.scala:9-20`, `fringe/src/fringe/AccelTopInterface.scala:22-58`). `AbstractAccelUnit` is only a Chisel `Module` with an abstract `io: AccelInterface` (`fringe/src/fringe/AccelTopInterface.scala:62-64`).

`DeviceTarget` is the Chisel-side target abstraction. It lazily creates one `BigIP`, exposes target shape constants such as address width, data width, words per stream, external bus shape, burst bytes, max bursts per command, target word width, and channel count, and requires `addFringeAndCreateIP` to create target-specific top IO and Fringe wiring (`fringe/src/fringe/targets/DeviceTarget.scala:7-18`, `fringe/src/fringe/targets/DeviceTarget.scala:33-67`). It also carries timing defaults such as fixed multiply/divide/add/sub/mod latencies and SRAM load/store latencies (`fringe/src/fringe/targets/DeviceTarget.scala:20-31`).

## Common shell

The common `Fringe` module is shared below target wrappers. It exposes host scalar read/write ports, accelerator enable/done/reset, `argIns`, decoupled `argOuts`, arg echo wires, application load/store/gather/scatter streams, one `DRAMStream` per channel, heap ports, and an AWS-only top enable input (`fringe/src/fringe/Fringe.scala:36-74`). The app stream surface is carried by `StreamParInfo` and `AppStreams`, which expand load, store, gather, and scatter stream lists into typed HVec ports (`fringe/src/fringe/FringeBundles.scala:39-89`). The DRAM-facing side is a command/write-data/read-response/write-response bundle (`fringe/src/fringe/FringeBundles.scala:145-152`), while scalar arg outs use `ArgOut` with a decoupled data port and echo input (`fringe/src/fringe/FringeBundles.scala:91-96`).

`Fringe` uses `globals.channelAssignment.assignments` to partition load and store streams across `NUM_CHANNELS`, creates one `DRAMArbiter` per channel, and wires all gather/scatter streams to every arbiter while load/store streams are channel-partitioned (`fringe/src/fringe/Fringe.scala:79-105`). The host-visible scalar register file includes command/status registers, arg registers, and a debug-register tail sized from the debug channel's `numDebugs` (`fringe/src/fringe/Fringe.scala:112-117`). Command bit 0 drives local enable unless `globals.perpetual` is true, command bit 1 drives local reset, and the status register is fed by a depulsed done/timeout signal plus heap alloc/dealloc responses (`fringe/src/fringe/Fringe.scala:132-181`). AWS targets use external top enable for DRAM arbiters; other targets use the command-derived local enable (`fringe/src/fringe/Fringe.scala:185-195`).

The `bug239_hack` is part of the observable host ABI. For AWS simulation, VCS, and ASIC, host read data is delayed by one cycle; for all other targets, `io.rdata` is connected directly to `regs.io.rdata` (`fringe/src/fringe/Fringe.scala:122-129`). A rewrite that changes host read timing must intentionally re-specify this behavior rather than accidentally preserving or dropping it.

## Global state

`fringe.globals` is a process-global mutable singleton. It stores the selected `DeviceTarget`, target-derived dimensions, retiming/perpetual/modular/debug flags, channel assignment, scalar counts, stream metadata, AXI stream metadata, allocator count, and arg-out loopback metadata (`fringe/src/fringe/globals.scala:8-31`, `fringe/src/fringe/globals.scala:43-60`). It also opens `bigIP.tcl` as a `PrintWriter` when the singleton initializes, which creates a file as a side effect of loading the object (`fringe/src/fringe/globals.scala:33-40`). Empty load/store/gather/scatter metadata lists fall back to one default stream using the target data width and words per stream, and helper counts derive public architectural sizes from those lists (`fringe/src/fringe/globals.scala:62-79`).

Channel assignment has four policies: `AllToOne`, `BasicRoundRobin`, `ColoredRoundRobin`, and `AdvancedColored`. The first assigns every stream to channel 0, the second round-robins stream indices, the third uses compile-time `memChannel`, and `AdvancedColored` is a TODO that currently falls back to round-robin (`fringe/src/fringe/ChannelAssignment.scala:3-34`).

## Target wrappers

Zynq-like targets instantiate `FringeZynq`, connect AXI-Lite host control, AXI master DRAM ports, debug probes, scalar args, app streams, heap, and reset/control, and then return a target-specific `SpatialIPInterface` (`fringe/src/fringe/targets/zynq/Zynq.scala:13-60`). The concrete `Zynq` target uses 32-bit address/data, 16 words per stream, and four channels (`fringe/src/fringe/targets/zynq/Zynq.scala:63-70`). `FringeZynq` wraps the common `Fringe`, selects an AXI-Lite bridge for KCU1500, Zynq/ZedBoard, or ZCU, forwards common scalar/control/stream/heap ports, and inserts one `MAGToAXI4Bridge` per channel (`fringe/src/fringe/targets/zynq/FringeZynq.scala:31-65`, `fringe/src/fringe/targets/zynq/FringeZynq.scala:69-139`). Simulator-derived targets use `SimTarget`, which wires `VerilatorInterface`, the common `Fringe`, direct register-file host ports, DRAM streams, scalar args, control, memory streams, and heap without a board AXI shell (`fringe/src/fringe/targets/SimTarget.scala:8-50`).

## HLS notes

The HLS rewrite should keep the conceptual boundaries - target selection, scalar ABI, stream metadata, heap/DRAM interfaces, and channel assignment - but should not reproduce Chisel elaboration-time mutable globals. `globals`, target IO factories, `DontCare` cleanup, and `Module` construction are Chisel-specific mechanics (`fringe/src/fringe/SpatialIP.scala:18-39`, `fringe/src/fringe/globals.scala:8-79`, `fringe/src/fringe/targets/DeviceTarget.scala:61-67`).

## Open questions

- [[open-questions-fringe-targets#Q-ft-03 - 2026-04-25 AdvancedColored channel assignment status|Q-ft-03]]
- [[open-questions-fringe-targets#Q-ft-04 - 2026-04-25 argOutLoopbacksMap ownership|Q-ft-04]]
- [[open-questions-fringe-targets#Q-ft-09 - 2026-04-25 DRAM debug-register cap|Q-ft-09]]
- [[open-questions-fringe-targets#Q-ft-10 - 2026-04-25 FringeZynq bridge fallback behavior|Q-ft-10]]
