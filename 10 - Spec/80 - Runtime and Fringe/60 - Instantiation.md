---
type: spec
concept: Instantiation
source_files:
  - "src/spatial/codegen/chiselgen/ChiselCodegen.scala:129-302"
  - "src/spatial/codegen/chiselgen/ChiselGenInterface.scala:121-189"
  - "src/spatial/codegen/chiselgen/ChiselGenStream.scala:181-198"
  - "src/spatial/codegen/chiselgen/ChiselGenDRAM.scala:72-85"
  - "src/spatial/codegen/chiselgen/ChiselGenController.scala:102-134"
  - "src/spatial/codegen/chiselgen/ChiselGenController.scala:362-397"
  - "src/spatial/codegen/chiselgen/ChiselGenController.scala:537-585"
  - "src/spatial/codegen/chiselgen/ChiselGenCommon.scala:416-453"
  - "fringe/src/fringe/SpatialIP.scala:18-40"
  - "fringe/src/fringe/AccelTopInterface.scala:9-64"
  - "fringe/src/fringe/FringeBundles.scala:39-88"
  - "fringe/src/fringe/globals.scala:7-79"
  - "fringe/src/fringe/CommonMain.scala:12-71"
  - "fringe/src/fringe/Fringe.scala:36-182"
  - "fringe/src/fringe/targets/zynq/FringeZynq.scala:79-114"
  - "fringe/src/fringe/templates/axi4/AXI4LiteToRFBridge.scala:23-120"
source_notes:
  - "[[fringe-and-targets]]"
hls_status: chisel-specific
hls_reason: "Rust and HLS will use different host-binding code, but this documents the existing Chisel pattern"
depends_on:
  - "[[10 - Fringe Architecture]]"
  - "[[40 - Controller Emission]]"
  - "[[50 - Streams and DRAM]]"
status: draft
---

# Instantiation

## Summary

The Chisel backend emits the top-level instantiation shape through `ChiselCodegen.emitEntry`, which opens generated `object Main`, defines `main(accelUnit: AccelUnit)`, assigns `accelUnit.io <> DontCare`, calls `emitPreMain()`, emits the accelerator block, and then calls `emitPostMain()` (`src/spatial/codegen/chiselgen/ChiselCodegen.scala:293-302`). `emitPreMain()` opens `AccelWrapper.scala`, `Instantiator.scala`, and `ArgInterface.scala`; `emitPostMain()` completes those files and writes `AccelUnit.scala` (`src/spatial/codegen/chiselgen/ChiselCodegen.scala:129-191`, `src/spatial/codegen/chiselgen/ChiselCodegen.scala:194-285`). The generated files sit on top of Fringe's `SpatialIP`, `AbstractAccelUnit`, `CustomAccelInterface`, mutable `globals`, and `CommonMain` entry framework (`fringe/src/fringe/SpatialIP.scala:18-40`, `fringe/src/fringe/AccelTopInterface.scala:22-64`, `fringe/src/fringe/globals.scala:7-79`, `fringe/src/fringe/CommonMain.scala:12-71`).

## Mechanism

`emitPreMain()` starts `AccelWrapper.scala` as package `accel`, imports Chisel, Fringe, and template packages, and opens `trait AccelWrapper extends Module` with target-dependent `io_w` and `io_v` values (`src/spatial/codegen/chiselgen/ChiselCodegen.scala:129-146`). `emitPostMain()` later writes combined scalar counts, assigns `globals.numArgIns`, `globals.numArgOuts`, `globals.numArgIOs`, `globals.numArgInstrs`, stream-info lists, AXI stream-info lists, and `globals.numAllocators`, and creates the `CustomAccelInterface` IO from those globals (`src/spatial/codegen/chiselgen/ChiselCodegen.scala:196-217`). `ChiselGenController.emitPostMain()` writes additional build globals into the same wrapper, including operation latencies on `globals.target`, `globals.perpetual`, `globals.channelAssignment`, `globals.retime`, and `globals.enableModular` (`src/spatial/codegen/chiselgen/ChiselGenController.scala:550-581`).

`emitPreMain()` starts `Instantiator.scala` as package `spatialIP`, imports `accel`, `fringe`, Chisel, iotesters, and AXI4 helpers, defines an empty `SpatialIPUnitTester`, and opens `object Instantiator extends CommonMain` with `type DUTType = SpatialIP` and `def dut = () => {` (`src/spatial/codegen/chiselgen/ChiselCodegen.scala:148-171`). `emitPostMain()` finishes that `dut` by computing scalar counts, constructing `new SpatialIP(this.target, () => Module(new AccelUnit(...)))`, closing `dut`, defining `tester`, and closing the object (`src/spatial/codegen/chiselgen/ChiselCodegen.scala:238-249`). The generated `Instantiator` passes `this.target` from `CommonMain`, and `SpatialIP` itself string-matches that target name to assign `globals.target`, installs `globals.target.makeIO`, calls the delayed accel generator, and delegates top-level IP creation to `globals.target.addFringeAndCreateIP(reset, accel)` (`src/spatial/codegen/chiselgen/ChiselCodegen.scala:245-249`, `fringe/src/fringe/SpatialIP.scala:18-40`).

## Implementation

`AccelUnit.scala` is generated as package `accel`, imports Chisel, Fringe, and template packages, and defines `class AccelUnit(...) extends AbstractAccelUnit with AccelWrapper` (`src/spatial/codegen/chiselgen/ChiselCodegen.scala:251-276`). Its constructor carries `top_w`, scalar counts, allocator count, load/store/gather/scatter `StreamParInfo` lists, and AXI stream parameter lists (`src/spatial/codegen/chiselgen/ChiselCodegen.scala:263-276`). The body defines `retime_released_reg`, defines `accelReset = reset.toBool | io.reset`, and invokes `Main.main(this)`, so the emitted accelerator body is elaborated inside this `AbstractAccelUnit` subclass (`src/spatial/codegen/chiselgen/ChiselCodegen.scala:276-280`, `fringe/src/fringe/AccelTopInterface.scala:62-64`).

Stream and scalar metadata are accumulated by other Chiselgen traits before the final `super.emitPostMain()` chain reaches `ChiselCodegen.emitPostMain()` (`src/spatial/codegen/chiselgen/ChiselGenInterface.scala:121-189`, `src/spatial/codegen/chiselgen/ChiselGenStream.scala:181-198`, `src/spatial/codegen/chiselgen/ChiselGenDRAM.scala:72-85`). `ChiselGenInterface.emitPostMain()` writes scalar counts and `loadStreamInfo`, `storeStreamInfo`, `gatherStreamInfo`, `scatterStreamInfo`, and `numArgIns_mem` into `Instantiator.scala`, and it writes corresponding `io_` values into `AccelWrapper.scala` (`src/spatial/codegen/chiselgen/ChiselGenInterface.scala:121-152`). `ChiselGenStream.emitPostMain()` emits AXI stream parameter lists for both `AccelWrapper.scala` and `Instantiator.scala` after checking that there is at most one AXI stream in and one AXI stream out (`src/spatial/codegen/chiselgen/ChiselGenStream.scala:181-198`). `ChiselGenDRAM.emitPostMain()` writes allocator counts to the wrapper and instantiator based on `accelDrams.size` (`src/spatial/codegen/chiselgen/ChiselGenDRAM.scala:72-85`).

The stream metadata type carried through those generated constructors is `StreamParInfo(w, v, memChannel)`, and `AppStreams` expands the load, store, gather, and scatter lists into typed stream bundles (`fringe/src/fringe/FringeBundles.scala:39-88`).

`ArgInterface.scala` is opened as package `accel`, imports Fringe utility/template packages and `api._`, and opens `object Args`, but the source only closes that object later and does not populate it in this file (`src/spatial/codegen/chiselgen/ChiselCodegen.scala:175-191`, `src/spatial/codegen/chiselgen/ChiselCodegen.scala:283-285`). The app-specific scalar register numbering is emitted instead into `ArgAPI.scala`: arg-ins start at their map index, host DRAM pointers follow arg-ins, arg-IOs follow host pointers, arg-outs follow arg-IOs, instrumentation counters follow arg-outs, and breakpoint outputs follow instrumentation counters (`src/spatial/codegen/chiselgen/ChiselGenInterface.scala:156-187`). Fringe's scalar bridge uses those counts at hardware level: `Fringe` exposes host scalar `raddr`, `wen`, `waddr`, `wdata`, `rdata`, accelerator `argIns`, `argOuts`, and `argEchos`, then instantiates `RegFile(regWidth, numRegs, numArgIns+2, numArgOuts+1+numDebugs, numArgIOs)` for command, status, scalar args, and debug registers (`fringe/src/fringe/Fringe.scala:36-57`, `fringe/src/fringe/Fringe.scala:112-117`). Zynq-like targets place an AXI4-Lite bridge between external `S_AXI` and Fringe's register-file ports, and the bridge modules translate AXI4-Lite into `raddr`, `wen`, `waddr`, `wdata`, and `rdata` signals (`fringe/src/fringe/targets/zynq/FringeZynq.scala:79-114`, `fringe/src/fringe/templates/axi4/AXI4LiteToRFBridge.scala:23-47`, `fringe/src/fringe/templates/axi4/AXI4LiteToRFBridge.scala:69-120`).

`writeKernelClass` emits each controller kernel into a separate `sm_<sym>.scala` file, writes the standard header, computes grouped inputs, and opens a `${lhs}_kernel` class extending `Kernel` (`src/spatial/codegen/chiselgen/ChiselGenController.scala:102-134`). The top accelerator case connects DRAM streams, creates DRAM allocators and heap wiring, instantiates the root kernel, and then writes the root kernel class (`src/spatial/codegen/chiselgen/ChiselGenController.scala:362-397`). `connectDRAMStreams` binds generated stream symbols to `accelUnit.io.memStreams.loads`, `stores`, `gathers`, and `scatters`, records `RemoteMemories`, and appends `StreamParInfo(width, par, 0)` entries to the corresponding stream-info maps (`src/spatial/codegen/chiselgen/ChiselGenCommon.scala:416-453`). This is the concrete source seam behind [[40 - Controller Emission|controller emission]] and [[50 - Streams and DRAM|stream and DRAM emission]].

## Interactions

`CommonMain` owns command-line splitting for generated top objects: it separates Chisel arguments from test arguments at `--testArgs`, stores test arguments in an implicit `args`, asserts the target is supported, and dispatches either an iotester run, Chisel verilog generation, or a normal tester run (`fringe/src/fringe/CommonMain.scala:12-71`). `globals` is the mutable singleton shared by SpatialIP and Fringe: it stores `target`, retiming/perpetual/channel-assignment flags, scalar counts, stream-info lists, allocator count, and fallback stream defaults (`fringe/src/fringe/globals.scala:7-79`). [[10 - Fringe Architecture]] covers the `SpatialIP` and Fringe wiring that consumes those globals (`fringe/src/fringe/SpatialIP.scala:18-40`, `fringe/src/fringe/Fringe.scala:36-182`).

## HLS notes

This instantiation path is Chisel-specific because it relies on generated Scala files, Chisel `Module` construction, `CommonMain`, and Fringe `globals` mutation during elaboration (`src/spatial/codegen/chiselgen/ChiselCodegen.scala:129-302`, `fringe/src/fringe/CommonMain.scala:12-71`, `fringe/src/fringe/globals.scala:7-79`). The HLS rewrite should preserve the conceptual inputs - target selection, scalar argument layout, stream/DRAM metadata, allocator metadata, and kernel composition - but implement them through Rust/HLS host-binding and top-function generation rather than `SpatialIP` and `AbstractAccelUnit` (inferred, unverified).

## Open questions

- [[open-questions-models-dse-fringe-gaps#Q-mdf-05 - 2026-04-24 HLS replacement for Chisel instantiation globals|Q-mdf-05]]
- [[open-questions-models-dse-fringe-gaps#Q-mdf-06 - 2026-04-24 ArgInterface versus ArgAPI scalar-layout ownership|Q-mdf-06]]
