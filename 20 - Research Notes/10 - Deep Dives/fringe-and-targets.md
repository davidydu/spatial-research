---
type: deep-dive
topic: fringe-and-targets
source_files:
  - "fringe/src/fringe/Fringe.scala"
  - "fringe/src/fringe/SpatialIP.scala"
  - "fringe/src/fringe/AccelTopInterface.scala"
  - "fringe/src/fringe/FringeBundles.scala"
  - "fringe/src/fringe/globals.scala"
  - "fringe/src/fringe/ChannelAssignment.scala"
  - "fringe/src/fringe/SpatialBlocks.scala"
  - "fringe/src/fringe/BigIP.scala"
  - "fringe/src/fringe/targets/DeviceTarget.scala"
  - "fringe/src/fringe/targets/BigIPSim.scala"
  - "fringe/src/fringe/targets/zynq/Zynq.scala"
  - "fringe/src/fringe/targets/zynq/FringeZynq.scala"
  - "fringe/src/fringe/targets/aws/BigIPAWS.scala"
  - "fringe/src/fringe/templates/dramarbiter/DRAMArbiter.scala"
  - "fringe/src/fringe/templates/dramarbiter/StreamController.scala"
  - "fringe/src/fringe/templates/dramarbiter/StreamArbiter.scala"
  - "fringe/src/fringe/templates/dramarbiter/AXIProtocol.scala"
  - "fringe/src/fringe/templates/dramarbiter/FIFOWidthConvert.scala"
  - "fringe/src/fringe/templates/dramarbiter/GatherBuffer.scala"
  - "fringe/src/fringe/templates/axi4/AXI4Parameters.scala"
  - "fringe/src/fringe/templates/axi4/Parameters.scala"
  - "fringe/src/fringe/templates/axi4/Bundles.scala"
  - "fringe/src/fringe/templates/axi4/MAGToAXI4Bridge.scala"
  - "fringe/src/fringe/templates/axi4/AXI4LiteToRFBridge.scala"
  - "fringe/src/fringe/templates/Ledger.scala"
  - "fringe/src/fringe/templates/ModuleParams.scala"
  - "fringe/src/fringe/templates/Controllers.scala"
  - "fringe/src/fringe/templates/counters/Counter.scala"
  - "fringe/src/fringe/templates/counters/FringeCounter.scala"
  - "fringe/src/fringe/templates/retiming/RetimeShiftRegister.scala"
  - "fringe/src/fringe/templates/retiming/Offset.scala"
  - "fringe/src/fringe/templates/memory/MemPrimitives.scala"
  - "fringe/src/fringe/templates/memory/NBuffers.scala"
  - "fringe/src/fringe/templates/memory/MergeBuffer.scala"
  - "fringe/src/fringe/templates/memory/Accum.scala"
  - "fringe/src/fringe/templates/memory/DRAMAllocator.scala"
  - "fringe/src/fringe/templates/memory/SRAM.scala"
  - "fringe/src/fringe/templates/memory/RegFile.scala"
  - "fringe/src/fringe/templates/SystolicArray.scala"
  - "fringe/src/fringe/templates/heap/DRAMHeap.scala"
  - "fringe/src/fringe/templates/math/Math.scala"
  - "fringe/src/fringe/templates/math/FixedPoint.scala"
  - "fringe/src/fringe/templates/hardfloat/MulAddRecFN.scala"
  - "src/spatial/targets/HardwareTarget.scala"
  - "src/spatial/targets/AreaModel.scala"
  - "src/spatial/targets/LatencyModel.scala"
  - "src/spatial/targets/MemoryResource.scala"
  - "src/spatial/targets/NodeParams.scala"
  - "src/spatial/targets/SpatialModel.scala"
  - "src/spatial/targets/package.scala"
  - "src/spatial/targets/xilinx/XilinxDevice.scala"
  - "src/spatial/targets/xilinx/XilinxAreaModel.scala"
  - "src/spatial/targets/xilinx/Zynq.scala"
  - "src/spatial/targets/xilinx/ZCU.scala"
  - "src/spatial/targets/xilinx/ZedBoard.scala"
  - "src/spatial/targets/xilinx/AWS_F1.scala"
  - "src/spatial/targets/xilinx/KCU1500.scala"
  - "src/spatial/targets/altera/AlteraDevice.scala"
  - "src/spatial/targets/altera/AlteraAreaModel.scala"
  - "src/spatial/targets/altera/Arria10.scala"
  - "src/spatial/targets/altera/DE1.scala"
  - "src/spatial/targets/euresys/EuresysDevice.scala"
  - "src/spatial/targets/euresys/EuresysAreaModel.scala"
  - "src/spatial/targets/euresys/CXP.scala"
  - "src/spatial/targets/generic/GenericDevice.scala"
  - "src/spatial/targets/generic/GenericAreaModel.scala"
  - "src/spatial/targets/generic/GenericLatencyModel.scala"
  - "src/spatial/targets/generic/ASIC.scala"
  - "src/spatial/targets/generic/VCS.scala"
  - "src/spatial/targets/generic/TileLoadModel.scala"
  - "src/spatial/targets/plasticine/Plasticine.scala"
  - "src/spatial/targets/plasticine/PlasticineAreaModel.scala"
session: 2026-04-23
status: ready-to-distill
feeds_spec:
  - "[[10 - Fringe Architecture]]"
  - "[[20 - DRAM Arbiter and AXI]]"
  - "[[30 - Ledger and Kernel]]"
  - "[[40 - Hardware Templates]]"
  - "[[50 - BigIP and Arithmetic]]"
  - "[[30 - Target Hardware Specs]]"
---

# Fringe and Hardware Targets — Deep Dive

## Reading log

Read in this order:
1. `fringe/src/fringe/SpatialIP.scala` — stagemost entry point; confirms `globals.target` is assigned by string-match in the `SpatialIP` constructor and must therefore be written before any downstream Chisel module elaborates.
2. `fringe/src/fringe/Fringe.scala` — common shell. Contains the `bug239_hack` at line 123 and the canonical IO layout.
3. `fringe/src/fringe/AccelTopInterface.scala` — the abstract accel-facing contract.
4. `fringe/src/fringe/globals.scala` — the mutable singleton; `tclScript` is eagerly opened as a side effect of class load.
5. `fringe/src/fringe/FringeBundles.scala` — `AppStreams`, `DRAMStream`, `DRAMCommand`, `DRAMTag`, `HeapIO`.
6. `fringe/src/fringe/ChannelAssignment.scala` — the four assignment strategies, `AdvancedColored` still a stub.
7. `fringe/src/fringe/targets/DeviceTarget.scala` — abstract per-target contract. TODO-laden constants.
8. `fringe/src/fringe/targets/zynq/{Zynq, FringeZynq}.scala` — representative per-target shell.
9. `fringe/src/fringe/templates/dramarbiter/*` all 9 files.
10. `fringe/src/fringe/templates/axi4/*` all 5 files.
11. `fringe/src/fringe/templates/Ledger.scala` — port-boring registry.
12. `fringe/src/fringe/templates/ModuleParams.scala` — insert-once parameter map.
13. `fringe/src/fringe/templates/Controllers.scala` — `GeneralControl`/`OuterControl`/`InnerControl`/`Sched`.
14. `fringe/src/fringe/templates/counters/{Counter, FringeCounter}.scala`.
15. `fringe/src/fringe/templates/retiming/{RetimeShiftRegister, Offset}.scala`.
16. `fringe/src/fringe/templates/memory/*` key files (`MemPrimitives`, `NBuffers`, `RegFile`, `Accum`, `MergeBuffer`, `DRAMAllocator`, `SRAM`).
17. `fringe/src/fringe/templates/math/Math.scala` + a sampling of HardFloat directory (verbatim Berkeley; see note below).
18. `fringe/src/fringe/BigIP.scala` + `targets/BigIPSim.scala` + `targets/aws/BigIPAWS.scala` (one-line delegating subclass).
19. `fringe/src/fringe/SpatialBlocks.scala` — `Kernel`, `CtrObject`, `CChainObject`, input/output kernel signals.
20. `src/spatial/targets/*` — `HardwareTarget`, `AreaModel`, `LatencyModel`, `MemoryResource`, `NodeParams`, `SpatialModel`, `package.scala`.
21. All per-vendor device files (`xilinx/*`, `altera/*`, `euresys/*`, `generic/*`, `plasticine/*`) — compared for duplication (confirmed).

## Observations

### 1. Two-layer target abstraction

There are *two separate* target abstractions:
- **`fringe.targets.DeviceTarget`** (`fringe/src/fringe/targets/DeviceTarget.scala:7-67`) — hardware-shim side. Governs Chisel parameterisation: `addrWidth`, `dataWidth`, `burstSizeBytes=64`, `maxBurstsPerCmd=256`, `num_channels`, op-latency defaults, and factories for `BigIP` + `addFringeAndCreateIP`.
- **`spatial.targets.HardwareTarget`** (`src/spatial/targets/HardwareTarget.scala:7-50`) — compiler-side. Governs DSE: `capacity: Area`, `AFIELDS`, `DSP_CUTOFF`, `clockRate`, `baseCycles`, `memoryResources`, `host`, `areaModel`/`latencyModel` factories.

These are not the same classes, not in the same class hierarchy, and not linked by inheritance. The compiler-side `HardwareTarget` produces area/latency numbers; the hardware-side `DeviceTarget` is what `globals.target` points at and what every Chisel module reads from. An HLS rewrite must preserve both layers: the area model drives DSE decisions that the HLS backend must honor, and the shim side drives codegen constants.

### 2. `SpatialIP` is the single entry point

`fringe/src/fringe/SpatialIP.scala:18-41` — the generated `Instantiator` creates one `SpatialIP(targetName, accelGen)`. The constructor:
1. String-matches `targetName` to a `DeviceTarget` subclass and assigns `globals.target` (lines 19-34). Unknown target throws.
2. Sets `globals.target.makeIO` to a closure capturing the module's `IO` apply (line 36) — a hack to let the device target register IO bundles outside of its scope.
3. Calls `accelGen()` to build the `AbstractAccelUnit` (line 37).
4. Delegates IP creation to `target.addFringeAndCreateIP(reset, accel)` (line 39).

This means: the target, not the SpatialIP module, decides the top-level IO shape. `ZynqInterface`, `ZCUInterface`, `AWSInterface`, etc. differ per-target — same Fringe underneath, different peripheral wiring.

### 3. Common shell: `Fringe.scala` and `FringeZynq`

`fringe/src/fringe/Fringe.scala:20-218` is the common shell. Key observations:

- IO is a flat bundle with host scalar interface (`raddr/wen/waddr/wdata/rdata`), accel control (`enable/done/reset`), accel scalar (`argIns/argOuts/argEchos`), `memStreams: AppStreams`, `dram: Vec[NUM_CHANNELS, DRAMStream]`, `heap: Vec[numAllocators, HeapIO]`, `aws_top_enable` (`Fringe.scala:36-74`).
- Creates `NUM_CHANNELS` `DRAMArbiter` modules based on `globals.channelAssignment.assignments` (lines 82-105). Each channel gets its own partition of load/store stream indices.
- `DRAMHeap` arbitrates allocator requests across accel heap IO (lines 107-110).
- `RegFile` is sized `NUM_ARGS + 2 - NUM_ARG_INS + numDebugs` registers (line 113) where `numDebugs = 500` is hard-coded in `DRAMArbiter.scala:22`.
- **`bug239_hack`** at `Fringe.scala:122-129`: on all targets *except* `AWS_Sim`, `VCS`, `ASIC`, the rdata is *not* shift-registered (direct `io.rdata := regs.io.rdata`); on those three it *is* shift-registered by 1. Comment says "Fix this bug asap so that the axi42rf bridge verilog anticipates the 1 cycle delay of the data". This has been known-wrong for 7 years per the file history implied in the coverage note.
- The command/status layout: `command = regs.io.argIns(0)`; `curStatus = regs.io.argIns(1).asTypeOf(new StatusReg)` where `StatusReg` packs `sizeAddr:59b, allocDealloc:3b, timeout:1b, done:1b` (lines 27-32, 132-133).
- 40-bit `FringeCounter` with `max = 12e9` as a hardware timeout (lines 142-150). `timeoutCycles = 12000000000L` means roughly 80 seconds at 150 MHz.
- `Depulser` converts the accel's single-cycle `done` pulse into a steady status-register bit observed by the host over AXI-Lite (lines 153-163).
- `argOuts` are `Decoupled`, but `ready` is deliberately ignored: lines 165-167 say "we do not care about [ready]". Valid is driven but ready is dropped.
- Per-target reset/enable routing: if target is `AWS_F1` or `AWS_Sim`, DRAM arbiters use `io.aws_top_enable` instead of `localEnable` (lines 188-193). Everyone else uses the command-register-derived `localEnable`.

`fringe/src/fringe/targets/zynq/FringeZynq.scala:1-145` wraps `Fringe` for the zynq-like family. Notable:
- Despite the name, `FringeZynq` is *the* common shell for Zynq, ZCU, ZedBoard, KCU1500, AWS_F1, AWS_Sim — its logic branches on `target.isInstanceOf[...]` (lines 80-116) to pick between three AXI-Lite bridge variants (`AXI4LiteToRFBridge`, `AXI4LiteToRFBridgeZCU`, `AXI4LiteToRFBridgeKCU1500`).
- The DRAM-side wraps `fringeCommon.io.dram(i)` with one `MAGToAXI4Bridge` per channel (lines 135-139).

### 4. Mutable globals: `fringe.globals`

`fringe/src/fringe/globals.scala:1-79` is a Scala `object` (singleton) with *mutable* vars:

- `var target: DeviceTarget = _` (line 10) — must be set before any module is elaborated.
- `var numArgIns/numArgOuts/numArgIOs/numArgInstrs: Int` — set by the `Instantiator`.
- `var loadStreamInfo/storeStreamInfo/gatherStreamInfo/scatterStreamInfo: List[StreamParInfo]` — populated by `Instantiator` from compile-time stream metadata.
- `var numAllocators: Int` — counts DRAMAllocators the accel owns.
- `var retime: Boolean`, `var perpetual: Boolean`, `var enableModular: Boolean = true`, `var enableDebugRegs: Boolean = true`, `var enableVerbose: Boolean = false`.
- `var channelAssignment: ChannelAssignment = AllToOne`.
- `var argOutLoopbacksMap: Map[Int,Int]`.
- `private var _tclScript: PrintWriter` — **opened eagerly on object init** (lines 34-38), creating `bigIP.tcl` in cwd even if never written. Side effect on import.

Default fallbacks for empty stream-info lists (lines 62-68): if `loadStreamInfo` is empty, `LOAD_STREAMS` returns `List(StreamParInfo(DATA_WIDTH, WORDS_PER_STREAM, 0))`. Same for store/gather/scatter. So single-stream synthesis still works.

This is *not reentrant*: running two `SpatialIP`s in one Chisel elaboration shares `globals.target`, which makes Fringe a process-level singleton. For Rust + HLS, we should thread a proper context through the IR instead of reviving this.

### 5. `DeviceTarget` boilerplate and per-target overrides

`DeviceTarget.scala:7-67` sets defaults that per-target classes often override:
- `addrWidth: Int = 32`, `dataWidth: Int = 32`, `wordsPerStream: Int = 16`, `external_w = 32`, `external_v = 16`, `target_w = 64`, `num_channels = 1`.
- `burstSizeBytes = 64`, `maxBurstsPerCmd = 256`, `bufferDepth = 64`.
- `magPipelineDepth = 1` (note: `MAGToAXI4Bridge.scala:20` reads this but never uses the resulting `numPipelinedLevels` — dead code path).
- Several `var` op-latency defaults (`fixmul_latency = 0.03125`, etc.). These influence `Math.mul`/`div`/etc. latency choices via `globals.target.fixmul_latency * b.getWidth`.
- `regFileAddrWidth(n: Int): Int = log2Up(n) + 1` — Zynq overrides to `32` (`Zynq.scala:11,65`).

Multiple TODO comments: `// TODO: What is this?` next to `addrWidth`, `dataWidth`, `wordsPerStream`, `external_w`, `external_v`, `target_w` (lines 33-55). The original authors themselves did not document these fields.

`Zynq.scala:63-71` overrides `addrWidth=32, dataWidth=32, wordsPerStream=16, num_channels=4, magPipelineDepth=0, regFileAddrWidth=32`. The naming is confusing: `Zynq` here (under `fringe.targets.zynq`) is the *Chisel-side* target; the `xilinx.Zynq` object (under `spatial.targets.xilinx`) is the *compiler-side* target. Same logical FPGA, two classes.

### 6. DRAM arbiter pipeline

`fringe/src/fringe/templates/dramarbiter/DRAMArbiter.scala:13-266` is the per-channel fan-in. Pipeline:

```
app loads/stores/gathers/scatters
  → StreamControllerLoad/Store/Gather/Scatter (per-stream FIFO + width convert)
    → StreamArbiter (priority encode + full-request-tracking)
      → AXICmdSplit (splits commands > maxBurstsPerCmd, tags last with cmdSplitLast)
        → AXICmdIssue (gates wdata, asserts wlast on final beat)
          → io.dram
```

Observations:
- `DRAMArbiter.scala:22` — hard-coded `val numDebugs = 500`. If more debug signals get registered, they silently drop (the `connectDbgSig` logic only increments `dbgCount` up to 500, but nothing asserts this bound).
- `DRAMArbiter.scala:46-51` — the debug header file path is `cpp/generated_debugRegs.h` (relative to cwd); opened *only* when `isDebugChannel=true`. In `Fringe.scala:81`, `val debugChannelID = 0`, so channel 0 is always the debug channel.
- `DRAMArbiter.scala:54-55` — `assert(streamTagWidth <= (new DRAMTag(64)).streamID.getWidth)` where `streamID` is 8 bits wide (`FringeBundles.scala:181`). So the arbiter can handle up to 256 streams per channel.

**Scatter strobe generation** (`StreamController.scala:193-201`): `strobeDecoder = UIntToOH(cmd.io.in.bits(0).wordOffset(info.w))`. Each stored element gets its byte-level strobe computed from the lane's word offset within the DRAM burst.

**Gather coalescing** (`GatherBuffer.scala:10-122`): `GatherAddressSelector` priority-encodes unissued lanes to prevent starvation (lines 20-34). The gather buffer piggybacks the coalesced burst UID on `DRAMTag.uid` (`StreamController.scala:149-152`), then scatters the rresp back to lanes by burstTag match (`GatherBuffer.scala:93-100`).

### 7. AXI4 bundles and the MAG-to-AXI4 bridge

`AXI4Parameters.scala:1-34` — constant widths (`lenBits=8, sizeBits=3, burstBits=2, cacheBits=4, respBits=2`). Notable: this file uses the **legacy `Chisel._` import** rather than `chisel3._`. Diplomacy subset uses the same legacy import. A Rust port needs to pick one naming convention and stick with it.

`Parameters.scala:74-107` — `AXI4BundleParameters(addrBits, dataBits, idBits)` with asserts `dataBits >= 8 && isPow2(dataBits) && addrBits >= 1 && idBits >= 1`. `AXI4StreamParameters.asDummyAXI4Bundle` (line 130) is a hack that returns `AXI4BundleParameters(32, dataBits, idBits)` with fake addr bits, so `AXI4Stream` can extend `AXI4BundleBase(params.asDummyAXI4Bundle)` for cloneType reuse (`Bundles.scala:125`).

`Bundles.scala:57-66` — `AXI4Bundle` uses Chisel `Irrevocable[BundleAR/AW/W/R/B]` (decoupled). `AXI4Inlined` (lines 71-123) is the **same interface but flat** with uppercase names like `AWID`, `AWADDR` — used on the Vivado-facing shell because Vivado's AXI auto-detection scans for those literal signal names.

`MAGToAXI4Bridge.scala:1-75` converts `DRAMStream` into `AXI4Inlined`. Key hard-codings:
- `ARSIZE = 6` (i.e. 2^6 = 64 bytes per beat) — lines 28, 42.
- `ARBURST = AWBURST = 1` (INCR mode) — lines 29, 43.
- `ARCACHE = AWCACHE = 15` on ZCU, `3` elsewhere — lines 31-32, 45-46. `3` is the Xilinx-recommended cached/bufferable. `15` enables write-back plus read/write allocate.
- `ARSIZE_BITS` assumes `p.dataBits == EXTERNAL_W * EXTERNAL_V` (line 11 assert). Non-512-bit external buses will fail this check — comment calls this out at line 10.
- Read data is reversed word-by-word (`rdataAsVec`, lines 59-61); wdata and wstrb are also reversed (lines 52-53). This is endianness gymnastics between fringe's big-endian-ish concat and AXI4's little-endian wire layout.

`AXI4LiteToRFBridge.scala:1-120` — the AXI-Lite slave that maps host writes/reads into RegFile indices. Three subclasses (`AXI4LiteToRFBridge`, `AXI4LiteToRFBridgeZCU`, `AXI4LiteToRFBridgeKCU1500`) wrap near-identical BlackBoxes (`AXI4LiteToRFBridgeVerilog`, `AXI4LiteToRFBridgeZCUVerilog`). Lines 124-238 contain a commented-out Chisel-native reimplementation that was abandoned. `~reset.toBool` is used at lines 41, 87, 113 — active-low reset from a Chisel active-high reset.

### 8. DRAMTag layout

`FringeBundles.scala:175-184`:
```
class DRAMTag(w: Int = 32) extends Bundle {
  val uid = UInt((w - 9).W)
  val cmdSplitLast = Bool()                // 1 bit
  val streamID = UInt(8.W)                 // 8 bits at LSB
}
```
Ordering is deliberate: `streamID` at `[7:0]` so every target sees it even when AXI ID width is narrower. `uid` may be truncated. `cmdSplitLast` is set by `AXICmdSplit` on the final split command of a burst that was too big, so that only that final wresp is propagated to the app (`AXIProtocol.scala:32-34, 44-47`).

### 9. Ledger — cross-kernel port registry

`fringe/src/fringe/templates/Ledger.scala:1-326` is a mutable object (Scala `object Ledger`) acting as a pass-by-implicit registry. Conceptually:

- Each memory op has an `OpHash` (Scala `.hashCode`).
- Each controller kernel has a `KernelHash` (also `.hashCode`).
- `Ledger.connections: HashMap[OpHash, BoreMap]` where `BoreMap = HashMap[KernelHash, ExposedPorts]`.
- `ExposedPorts` tracks 14 port categories (rPort, wPort, structPort, broadcastR/W, reset, output, accessActivesIn, stageCtrl, mergeEnq/Deq/Bound/Init, allocDealloc) — `Ledger.scala:88-154`.
- `ControllerStack.stack: Stack[KernelHash]` tracks which kernels we're nested inside — `Ledger.scala:67-69`.
- `enter(ctrl, name)` pushes; `exit()` pops — lines 315-323.
- `connectRPort/WPort/…` — each records "at this kernel stack, op X uses port Y" by iterating the current stack and appending the port to each kernel's exposed set — lines 193-290.

The docstring at lines 8-65 has an extensive ASCII diagram walking through a 7-kernel tree with cross-kernel boring. The accumulation is inclusive: every ancestor kernel on the stack sees the port, because the IR needs to know which ports are exposed at each level for later "boring" through module boundaries.

`globals.enableModular` gates the entire Ledger subsystem — every `connect*` method checks `if (globals.enableModular)` first (e.g. line 194). Disabling it reverts to naive inlined generation.

`substitute(oldHash, newHash)` (lines 181-190) re-keys the `connections` map when the chiselgen emits a module under a different hash than originally planned — a fixup for hash instability across transformation phases.

`connectInstrCtrs` (line 300) and `connectBreakpoints` (line 310) use the same stack-based pattern but for instrumentation counter IDs and breakpoint IDs instead of port IDs.

### 10. `Kernel` scaffolding

`fringe/src/fringe/SpatialBlocks.scala:96-172` — the abstract `Kernel` class:
- Holds `sigsIn: InputKernelSignals` and `sigsOut: OutputKernelSignals` — `Bundle`s with the FSM/counter communication signals (lines 47-72).
- `configure(n, signalsFromParent, signalsToParent, isSwitchCase)` wires:
  - Counter values → kernel (line 119).
  - Select vectors → kernel (for switches, line 121).
  - SM's control outputs → kernel (lines 123-136).
  - II counter enable/reset/done/issue (line 157).
  - Counter chain enable/reset (line 158).
  - **Special case for streaming outer controllers** (lines 159-166): `sm.io.ctrCopyDone` ties to `mySignalsOut.smCtrCopyDone`; each child counter chain sees `smCtrCopyDone` as its done.
  - Parent relationship: if parent is streaming with a cchain, `signalsToParent.cchainEnable(childId) := done` (line 168). Otherwise `smCtrCopyDone(childId) := done` (line 170).

`CtrObject` (lines 20-31) wraps a counter spec (start/stop/step can be `Either[Option[Int], FixedPoint]` — Left for static, Right for dynamic). `CChainObject` (lines 33-44) builds a `CounterChain` from a list of `CtrObject`.

### 11. `ModuleParams` — insert-once parameter map

`fringe/src/fringe/templates/ModuleParams.scala:1-16`: a Scala `object` with a mutable `HashMap[String, Any]`.
```
def addParams(name: String, payload: Any): Unit = if (!mapping.contains(name)) mapping += (name -> payload)
def getParams(name: String): Any = mapping(name)
```
`addParams` is a no-op if the name exists — insert-once semantics. Generated chiselgen code writes once, then module elaboration reads. Like `Ledger`, it's process-global mutable state.

### 12. Hardware templates

Memory primitives (`fringe/src/fringe/templates/memory/MemPrimitives.scala:1-924`):
- `MemPrimitive(p: MemParams)` — base with dispatch on `p.iface` (`StandardInterfaceType`, `ShiftRegFileInterfaceType`, `FIFOInterfaceType`) — lines 17-28.
- `BankedSRAM` (line 51) — builds `numMems` `Mem1D` instances, routes writes/reads by `canSee`/`lanesThatCanSee` (visible-banks intersection) — lines 60-150.
- `Mem1D`, `FF`, `FIFO`, `LIFO`, `LineBuffer`, `ShiftRegFile` — the core bank primitives used by NBufMem.
- `StickySelects` (line 124) handles a bug in scatter-gather SRAM access.

`NBuffers.scala:63-321` — `NBufMem` with `NBufController` tracking W/R pointer counters (`NBufCtr`). Handles double/triple/N-buffered memories where swap happens when all enabled stages have signaled done.

`RegFile.scala:15-112` — the host-visible register file. `addrWidth = globals.target.regFileAddrWidth(d)`. Layout: row 0 is command, row 1 is status, `pureArgIns = numArgIns - numArgIOs` follows, then pureArgOuts, then debug slots. ZCU quirk: register IDs are doubled (`i*2`) at line 65, and rport indexing is `raddr/2` at line 99 — Xilinx ZynqMP address step is 4 bytes but we use 8-byte regs.

`Accum.scala:1-193` — `FixFMAAccum` (multi-lane fused-multiply-add accumulator with pipelined drain), `FixOpAccum` (add/mul/min/max variants). `Accum` is a sealed abstract with case-object variants `Add/Mul/Min/Max`.

`MergeBuffer.scala:1-369` — k-way merge with `UpDownCounter`, `BarrelShifter`.

`DRAMAllocator.scala:1-89` — per-DRAM handshake with `DRAMHeap`. `connectAlloc`/`connectDealloc` methods use the Ledger to track `allocDealloc` port lanes (lines 39-50).

Counters (`fringe/src/fringe/templates/counters/Counter.scala:1-564`):
- `NBufCtr` (line 24) — wrapping counter for N-buffer pointer tracking.
- `IncDincCtr`, `CompactingIncDincCtr` — fifo element tracking (push/pop).
- `IICounter` (line 121) — initiation-interval enforcement. Comment at lines 136-137 flags uncertainty about whether `cnt == 0` or `cnt == ii-1` is the correct issue condition.
- `SingleCounter` (line 232) — the workhorse. Handles static and dynamic start/stop/stride with `par` lanes. 4-bit `defs` dispatch on which of `start/stop/stride` are statically known (line 314).
- `SingleSCounter`, `SingleSCounterCheap` — signed counters for FILO.
- `CompactingCounter` (line 186) — signed wrapping.
- `CounterChain` (line 500) — stacks counters with done-gated enable chain (innermost ticks fastest).

Controllers (`fringe/src/fringe/templates/Controllers.scala:1-333`):
- `ControlParams` case class with `sched: Sched, depth, isFSM, isPassthrough, stateWidth, cases, latency, myName`.
- `sealed trait Sched` with five objects: `Sequenced`, `Pipelined`, `Streaming`, `Fork`, `ForkJoin` (lines 62-67). **Not case objects** — bare `object`. This matters because pattern matching on them is reference-based and no automatic `toString`.
- `OuterControl.sched` pattern match (lines 95-210) has five cases plus FSM fallback. Each case wires `active`, `done`, `iterDone` SRFFs differently. The Streaming case (lines 156-171) uses `ctrCopyDone` instead of the synchronized `doneIn` chain.
- `InnerControl` (line 256) — simpler SRFF pair for `active` and `done`, no per-stage tracking.

Retiming (`fringe/src/fringe/templates/retiming/*`):
- `RetimeWrapper(width, delay, init)` — wraps `RetimeShiftRegister` BlackBox with a Chisel shim that wires clock/reset.
- `RetimeWrapperWithReset` — adds an external `rst` OR'd with module reset.
- `RetimeShiftRegister` — BlackBox with Verilog parameters `WIDTH`, `STAGES` (lines 45-50 in `RetimeShiftRegister.scala`). Assumes a Verilog file of the same name exists.
- `Offset.scala:5` explicitly marked `// NOTE: This is unused`. Dead code.

`SystolicArray.scala:1-225` — `SystolicArray2D` templated by dims, neighborhood, movement_scalars, self_position, inits, operation mode. Five operation modes: `Sum`, `Product`, `MAC`, `Max`, `Min` (sealed trait `OperationMode`).

### 13. BigIP and Math

`fringe/src/fringe/BigIP.scala:1-105` — abstract class with 45+ methods. Required (no default): `divide` (UInt/SInt), `mod` (UInt/SInt), `multiply` (UInt/SInt), `fadd`, `fsub`, `fmul`, `fdiv`, `flt/fgt/fge/fle/fne/feq`. Optional (default: `throw Unimplemented`): `sqrt`, `sin`, `cos`, `atan`, `sinh`, `cosh`, `log2`, `fabs`, `fexp`, `ftanh`, `fsigmoid`, `fln`, `frec`, `fsqrt`, `frsqrt`, `ffma`, `fix2flt`, `fix2fix`, `flt2fix`, `flt2flt`, `fltaccum`.

Subclasses: `BigIPSim`, `BigIPZynq`, `BigIPZCU` (via ZynqLike), `BigIPAWS` (one-line `class BigIPAWS extends BigIPZynq`), `BigIPAWS_Sim`, `BigIPArria10`, `BigIPASIC`, `BigIPCXP`, `BigIPVCS`, `BigIPVCU1525`, `BigIPKCU1500`, `BigIPZedBoard`, `bigIPDE1SoC` (lowercase `b` in class name — inconsistency).

`fringe/src/fringe/templates/math/Math.scala:13` is a plain Scala `object`. Every arithmetic op dispatches through `globals.bigIP`. For example:
```
def mul(a: UInt, b: UInt, delay: Option[Double], flow: Bool, myName: String): UInt = {
  val latency = delay.getOrElse(globals.target.fixmul_latency * b.getWidth).toInt
  globals.bigIP.multiply(a, b, latency, flow, myName)
}
```
The default latency is `target.fixmul_latency * bitWidth` — a linear latency model. Overridable by `delay: Option[Double]`.

### 14. HardFloat — verbatim Berkeley import

**`fringe/src/fringe/templates/hardfloat/*` is Berkeley HardFloat verbatim**, not Spatial-specific. 21 files total. Every file leads with the Berkeley copyright notice (confirmed in `MulAddRecFN.scala:1-30`, `DivSqrtRecF64_mulAddZ31.scala:1-30`). The library provides recoded-format IEEE-754 floating point with `MulAddRecFN`, `DivSqrtRecF64_mulAddZ31`, `DivSqrtRecFN_small`, `CompareRecFN`, `RecFNToRecFN`, `rawFloatFromFN`, `recFNFromFN`, `RoundAnyRawFNToRecFN`, `INToRecFN`, `RecFNToIN`, `classifyRecFN`, `fNFromRecFN`, `resizeRawFloat`. There are also 7 `ValExec_*` verification harnesses.

**Rule for the spec**: do not re-spec the HardFloat files. Reference the upstream library. Any HLS port should likely bring in the upstream library (or a Vivado/HLS equivalent) rather than port these 21 files.

### 15. `spatial.targets.HardwareTarget` — the compiler-side model

`src/spatial/targets/HardwareTarget.scala:7-50` defines the DSE-facing contract. Required by subclasses:
- `name: String`, `burstSize: Int` (**in bits**, not bytes — note asymmetry with DeviceTarget).
- `AFIELDS: Array[String]` — area resource names, used as CSV column keys.
- `DSP_CUTOFF: Int` — fixed-mul cutoff above which ops go to DSPs.
- `capacity: Area` — the `Area` case class from `models.*` is a map of AFIELDS name → Double.
- `makeAreaModel(mlModel)` / `makeLatencyModel`.
- `memoryResources: List[MemoryResource]`, `defaultResource: MemoryResource`.

Defaults:
- `host: String = "cpp"` — override to `"rogue"` for KCU1500 (`xilinx/KCU1500.scala:7`). This is the switch that routes host codegen to `RogueCodegen` instead of `CppCodegen`.
- `clockRate: Float = 150.0f` — overridden only by Plasticine (`plasticine/Plasticine.scala:13` sets `1000.0f`).
- `baseCycles: Int = 43000` — not overridden anywhere. This is the "startup cycles" for latency-prediction bookkeeping. I did not find its consumer in the read pass — likely in DSE or reporting.

`LFIELDS` constants at `HardwareTarget.scala:52-58`: `RequiresRegs, RequiresInReduce, LatencyOf, LatencyInReduce, BuiltInLatency` — the latency-CSV columns.

### 16. `AreaModel` and per-vendor `summarize`

`AreaModel.scala:29-35` — `areaOf` dispatches: in-hw-scope calls `areaInReduce` (same as `areaOfNode` by default) or `areaOfNode`. Not-in-hw-scope returns `NoArea`.

`areaOfNode` pattern match (lines 161-191) — `Transient`, `DRAMHostNew`, `DRAMAddress`, `SwitchCase` → `NoArea`. `MemAlloc` (non-remote) → `areaOfMem`. `Accessor`/`UnrolledAccessor`/`StatusReader` → `NoArea` ("Included already in MemAlloc model"). `DelayLine` → `areaOfDelayLine`. `FixMul`/`FixDiv`/`FixMod` with non-constant non-pow2 operand → `Area("DSPs" -> 1)`.

`areaOfMem` (lines 60-92) — builds a banking-histogram feature vector and calls the ML `mlModel.estimateMem(...)` for LUTs/FFs. But the RAM18/RAM36 ML estimator is disabled:
```
// val ram18 = scala.math.ceil(mlModel.estimateMem("RAMB18", ...)).toInt
// val ram36 = scala.math.ceil(mlModel.estimateMem("RAMB36", ...)).toInt
val ram36 = N.head * (1 max scala.math.ceil((dims.product / (N.head * 36000))).toInt) * (depth + 1)
val ram18 = 0
```
Lines 87-90. Comment: "models give wildly large numbers, ram = N should be more realistic for now". **So RAM18 is always 0, and RAM36 is an analytical estimate.**

`accessUnrollCount` (lines 41-58) iterates up the parent chain counting `OpForeach`/`OpReduce` `cchain.constPars.product`, and for `OpMemReduce` multiplies by `cchainMap.constPars.product + cchainRed.constPars.product` with `// TODO: This is definitely wrong, need to check stage of access`.

`areaOfDelayLine` (lines 197-205) — **register-only**, despite a docstring saying "Models delays as registers for short delays, BRAM for long ones". The BRAM branch was never implemented. The function returns `Area("Regs" -> length * par)`.

Per-vendor `summarize`:
- `XilinxAreaModel.summarize` (lines 11-107) — rolls LUTs into slices (LUT1/LUT2/LUT3 each count as 0.5 LUT for slice packing; LUT4/5/6 count as 1), memory LUTs into SLICEM, register surplus into regSlices with magic factor 1.9. RAM18/2 + RAM36 → BRAM. Report is gated `if (false)` — always off.
- `AlteraAreaModel.summarize` (`altera/AlteraAreaModel.scala:11-107`) — identical to Xilinx except:
  1. Adds `+ model("Fringe")()` to the design area (line 12).
  2. Report gating is `if (config.enInfo)` (line 40) instead of `if (false)`.
- `EuresysAreaModel.summarize` — **identical to Altera.** Same two deltas vs Xilinx.
- `GenericAreaModel.summarize` — identical to Xilinx (no Fringe add, report gated false).
- `PlasticineAreaModel.summarize` — trivial: returns `(area, "")`.

So four vendor bases (Xilinx, Altera, Euresys, Generic) and their AreaModels are 90%+ byte-identical. `XilinxDevice.scala`, `AlteraDevice.scala`, `EuresysDevice.scala`, and most of `GenericDevice.scala` have the same AFIELDS array, same memoryResources list, same `bramWordDepth`, same `uramMemoryModel`, same `bramMemoryModel`, same `distributedMemoryModel`. `GenericDevice` adds an `SRAM_RESOURCE` inside-class object but does not use it in `memoryResources`.

### 17. Per-target descriptors

All per-target objects carry essentially just a `name`, `burstSize`, and `capacity`:

| target | name | burstSize | Special | capacity |
|---|---|---|---|---|
| `xilinx.Zynq` | "Zynq" | 512 | — | full 6-field Area |
| `xilinx.ZCU` | "ZCU" | 512 | "Cut in half for DSE" comment | full |
| `xilinx.ZedBoard` | "ZedBoard" | 512 | (identical to Zynq's capacity) | full |
| `xilinx.AWS_F1` | "AWS_F1" | 512 | Adds URAM→960 | full + URAM |
| `xilinx.KCU1500` | "KCU1500" | 512 | `host = "rogue"` | full |
| `altera.Arria10` | "Arria10" | 512 | Empty capacity (stub) | `Area()` |
| `altera.DE1` | "DE1" | 512 | Empty capacity (stub) | `Area()` |
| `euresys.CXP` | "CXP" | 512 | — | full (copy of Zynq) |
| `generic.ASIC` | "ASIC" | 512 | `AFIELDS=Array(); DSP_CUTOFF=0; borrows xilinx.Zynq's LatencyModel` | `Area()` |
| `generic.VCS` | "VCS" | 512 | 9999999 pseudo-infinite | all 9999999 |
| `plasticine.Plasticine` | "Plasticine" | 512 | `clockRate=1000; AFIELDS=Array(); DSP_CUTOFF=0` | `Area()` |

`ASIC.scala:12` uses `new LatencyModel(xilinx.Zynq)` — **the ASIC target quietly borrows Zynq's latency CSV.**

`package.scala:1-31` registers the public set:
```
fpgas = { Zynq, ZCU, ZedBoard, AWS_F1, KCU1500, CXP, DE1, Arria10, VCS }
all   = fpgas + Plasticine
Default = xilinx.Zynq
```
Note `ASIC` is not in `fpgas` and not in `all` — not selectable by CLI.

### 18. `TileLoadModel` dead code

`generic/TileLoadModel.scala:16-109`: the entire neural-network training/inference body is commented out. `evaluate(c, r, b, p)` returns `0.0` literally. `init()` does nothing. Yet `GenericLatencyModel.scala:13` instantiates `lazy val memModel = new TileLoadModel` and calls `memModel.evaluate(c, r, cols, p)` at line 30. **The call always returns 0, silently contributing nothing to the latency estimate.**

### 19. Memory resource ordering is semantic

`memoryResources: List[MemoryResource]` order is load-bearing. In all four vendor bases, the list is:
```
List(URAM_RESOURCE, BRAM_RESOURCE, URAM_RESOURCE_OVERFLOW, LUTs_RESOURCE)
```
`MemoryAllocator` walks this list in order; the **last element is the catch-all**. For Xilinx/Altera/Euresys/Generic, that's `LUTs_RESOURCE`. For ASIC, `VCS` (via Generic), `Plasticine`, it's `SRAM_RESOURCE`. The coverage note called this out: invariant is implicit, not asserted.

## Open questions

Filed to `[[open-questions-fringe-targets]]`:
- Q-010: What consumes `baseCycles = 43000`?
- Q-011: What consumes `magPipelineDepth`? (`MAGToAXI4Bridge.scala:20` reads it, discards it.)
- Q-012: `AdvancedColored` channel assignment is a stub; does any codepath select it?
- Q-013: `argOutLoopbacksMap` — populator and semantics unknown.
- Q-014: Is `ASIC` borrowing `xilinx.Zynq`'s latency model intentional or an oversight?
- Q-015: Why are `Altera DE1`, `Arria10`, and `ASIC` capacities empty? Can DSE run meaningfully against them?
- Q-016: `accessUnrollCount` `OpMemReduce` has a "definitely wrong" TODO; what's the actual fix?
- Q-017: Is `TileLoadModel` dead code permanent, or a disabled-experimental state?
- Q-018: Does anything assert the 500-signal debug cap in `DRAMArbiter`?
- Q-019: `FringeZynq` branches on target type but there's no default `else` — what happens on an unlisted target?

## Distillation plan

This deep-dive feeds six spec entries:
1. `[[10 - Fringe Architecture]]` — SpatialIP top, Fringe shell, accel interface, DeviceTarget, globals.
2. `[[20 - DRAM Arbiter and AXI]]` — DRAMArbiter pipeline, stream controllers, AXI4 bundles, MAGToAXI4Bridge, AXI4LiteToRFBridge, DRAMTag.
3. `[[30 - Ledger and Kernel]]` — Ledger port-boring, Kernel.configure, ModuleParams.
4. `[[40 - Hardware Templates]]` — Memory primitives, counters, controllers, retiming, systolic, shuffle.
5. `[[50 - BigIP and Arithmetic]]` — BigIP abstraction, Math object, HardFloat reference-only.
6. `[[30 - Target Hardware Specs]]` — per-vendor device bases, per-FPGA descriptors, area-model duplication, capacity stubs.
