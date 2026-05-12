---
type: coverage
subsystem: Fringe
paths:
  - "fringe/src/"
file_count: 149
date: 2026-04-21
verified:
  - 2026-04-21
---

## 1. Purpose

Fringe is the Chisel3 hardware shim that wraps a generated Spatial accelerator and connects it to the host/FPGA environment. It is the lowest rung of the Spatial compilation pipeline: after `spatial` emits an `AccelUnit` (subclass of `AbstractAccelUnit`), Fringe provides the DRAM arbiter, AXI4 (full) memory-controller bridges, AXI4-Lite-to-register-file scalar-control bridge, scalar argument register file, heap allocator glue, CoaXPress/AXI-Stream bindings, per-target device shells (Zynq, AWS_F1, ZCU, ASIC, Verilator, VCS, XSim, ...), a reusable library of hardware primitives (SRAMs, N-buffers, register files, systolic arrays, counters, retiming wrappers, fixed/floating-point ALUs built on the Berkeley HardFloat library), and a metadata "Ledger" used by the generated accelerator to wire up cross-kernel memory ports. It is compiled into Verilog by Chisel and delivered as an IP core that Vivado/Quartus synthesis composes with each target's device-specific infrastructure.

## 2. File inventory

Files are grouped by directory / functional category to avoid listing 149 near-duplicate entries.

| path | one-line purpose |
|---|---|
| `fringe/src/fringe/Fringe.scala` | Top `Fringe` Chisel module: per-target common shell wiring host regs, DRAM arbiters, heap, timeout counter, status register. |
| `fringe/src/fringe/SpatialIP.scala` | `SpatialIP` top wrapper: instantiates Accel + target's `addFringeAndCreateIP`. |
| `fringe/src/fringe/AccelTopInterface.scala` | `AccelInterface` / `CustomAccelInterface` / `AbstractAccelUnit` — the accel-to-fringe IO contract. |
| `fringe/src/fringe/FringeBundles.scala` | `LoadStream`, `StoreStream`, `GatherStream`, `ScatterStream`, `AppStreams`, `DRAMStream`, `DRAMCommand`/`Wdata`/`Rresp`/`Wresp`, `DRAMAddress`, `DRAMTag`, `HeapIO`, `StreamIO`, `DebugSignals`, `ArgOut`, `InstrCtr`. |
| `fringe/src/fringe/globals.scala` | Mutable globals: active `DeviceTarget`, numArgIns/Outs, stream-info lists, retime/perpetual flags, channel-assignment strategy. |
| `fringe/src/fringe/BigIP.scala` | Abstract BigIP: target-pluggable div/mod/mul + all fp/fix conversion primitives. |
| `fringe/src/fringe/ChannelAssignment.scala` | `AllToOne`, `BasicRoundRobin`, `ColoredRoundRobin`, `AdvancedColored` stream-to-channel policies. |
| `fringe/src/fringe/CommonMain.scala` | `ArgsTester` + `CommonMain` trait for Chisel/Driver entry. |
| `fringe/src/fringe/SpatialBlocks.scala` | `CtrObject`, `CChainObject`, `InputKernelSignals`, `OutputKernelSignals`, abstract `Kernel` controller-harness. |
| **Target shells (`fringe/src/fringe/targets/*`), 39 files** — one subdir per platform: |  |
| `targets/DeviceTarget.scala` | Base trait: `addFringeAndCreateIP`, `makeBigIP`, burst/pipeline constants (`burstSizeBytes=64`, `maxBurstsPerCmd=256`, `addrWidth`, `dataWidth`). |
| `targets/FringelessTarget.scala`, `targets/SimTarget.scala`, `targets/BigIPSim.scala`, `targets/SimBlackBoxes.scala` | Shared simulator scaffolding + Chisel-pure implementations of fix/flt ops for sim. |
| `targets/verilator/{Verilator, VerilatorInterface, FringelessInterface}.scala` | Verilator simulator target + its top IO. |
| `targets/vcs/{VCS, BigIPVCS}.scala` | Synopsys VCS simulator target + BigIP. |
| `targets/xsim/XSim.scala` | Xilinx xsim target. |
| `targets/zynq/{Zynq, ZynqLike, ZynqInterface, ZynqBlackBoxes, BigIPZynq, FringeZynq}.scala` | Zynq shell; `FringeZynq` also reused by KCU1500, ZedBoard, AWS. |
| `targets/zedboard/{ZedBoard, ZedBoardInterface, ZedBoardBlackBoxes, BigIPZedBoard, FringeZedBoard}.scala` | ZedBoard shell. |
| `targets/zcu/{ZCU, ZCUInterface}.scala` | Xilinx ZynqMP (ZCU102/104) shell. |
| `targets/kcu1500/{KCU1500, KCU1500IPInterface}.scala` | Xilinx KCU1500 PCIe shell. |
| `targets/aws/{AWS_F1, AWS_Sim, AWSInterface, BigIPAWS, BigIPAWS_Sim}.scala` | Amazon EC2 F1 production + simulation shells. |
| `targets/cxp/{CXP, CXPInterface, CXPBlackBoxes, BigIPCXP, FringeCXP}.scala` | Euresys/CoaXPress image capture shell. |
| `targets/arria10/{Arria10, Arria10Interface, BigIPArria10, FringeArria10}.scala` | Intel/Altera Arria10 shell. |
| `targets/de1soc/{DE1SoC, DE1SoCInterface, bigIPDE1SoC}.scala` | Altera DE1-SoC shell. |
| `targets/asic/{ASIC, ASICBlackBoxes, BigIPASIC}.scala` | ASIC build target. |
| `targets/vcu1525/{VCU1525, BigIPVCU1525}.scala` | Xilinx VCU1525 shell. |
| **DRAM arbiter (`fringe/src/fringe/templates/dramarbiter/*`), 9 files** |  |
| `dramarbiter/DRAMArbiter.scala` | Top `DRAMArbiter`: per-channel fan-in of loads/stores/gathers/scatters into one DRAMStream; emits `generated_debugRegs.h`. |
| `dramarbiter/StreamController.scala` | `StreamControllerLoad/Store/Gather/Scatter` — per-stream FIFO + width converters. |
| `dramarbiter/StreamArbiter.scala` | Priority + full-request-tracking arbiter across streams. |
| `dramarbiter/AXIProtocol.scala` | `AXICmdSplit` splits oversized commands at `maxBurstsPerCmd`; `AXICmdIssue` gates wdata/wlast and issues commands once. |
| `dramarbiter/FIFO.scala`, `FIFOVec.scala`, `FIFOWidthConvert.scala`, `GatherBuffer.scala`, `Counter.scala` | Supporting buffers (word-width-converting, banked, vector FIFOs), gather address coalescing, simple counters. |
| **AXI4 (`fringe/src/fringe/templates/axi4/*`), 5 files** |  |
| `axi4/AXI4Parameters.scala` | AXI4 constant bit-widths (lenBits=8, sizeBits=3, burstBits=2, ...) and burst/cache constants. |
| `axi4/Parameters.scala` | `AXI4BundleParameters`, `AXI4SlaveParameters`, `AXI4MasterParameters`, `AXI4StreamParameters` case classes. |
| `axi4/Bundles.scala` | `AXI4Bundle` (decoupled), `AXI4Inlined` (flat signal names for Vivado auto-detection), `AXI4Lite`, `AXI4Probe`, `AXI4Stream`, `AvalonSlave`, `AvalonStream`. |
| `axi4/MAGToAXI4Bridge.scala` | DRAM-stream ⇒ M_AXI master (hardcodes 64-B burst size 6, INCR mode, CACHE=3/15 depending on ZCU). |
| `axi4/AXI4LiteToRFBridge.scala` | Three variants (Zynq, ZCU, KCU1500) of BlackBox AXI-lite slave that writes/reads the scalar register file. |
| **Diplomacy (`fringe/src/fringe/templates/diplomacy/*`), 5 files** | Rocket-chip-style LazyModule/Node/AddressDecoder/Parameters subset used by AXI4 parameters. |
| **Memory primitives (`fringe/src/fringe/templates/memory/*`), 14 files** |  |
| `memory/FringeFF.scala`, `SRFF.scala`, `TFF.scala` | Retimed edge-triggered FF, set/reset FF, toggle FF. |
| `memory/SRAM.scala` | BlackBox `SRAMVerilog[Sim\|DualRead]`, per-target pragma maps for Xilinx BRAM/URAM and Altera. |
| `memory/MemPrimitives.scala` | `BankedSRAM`, `Mem1D`, `FF`, `FIFO`, `LIFO`, `LineBuffer`, `ShiftRegFile` — the core physical-memory bank. |
| `memory/NBuffers.scala` | N-buffered memory controller for double/triple/N-buffered reads/writes. |
| `memory/RegFile.scala` | Host-visible register file: `command`, `status`, argIns, argOuts, argIOs, debug slots. |
| `memory/MergeBuffer.scala` | Merge network (k-way compare-and-route) + `UpDownCounter`, `BarrelShifter`. |
| `memory/Accum.scala` | Fix/Flt FMA/op accumulators used by reduction patterns. |
| `memory/DRAMAllocator.scala` | Per-DRAM handshake to `DRAMHeap` (alloc/dealloc with dims→size). |
| `memory/MemType.scala`, `MemParams.scala`, `MemInterfaceType.scala`, `BankingMode.scala` | Case-class ADTs distinguishing SRAM/FIFO/LIFO/LineBuffer/Shift and banking modes. |
| `memory/implicits.scala` | Empty implicits namespace (forward-compat). |
| **Heap (`fringe/src/fringe/templates/heap/DRAMHeap.scala`)** | 1 file, arbitrates `numAlloc` accel heap requests to the single host port. |
| **Counters (`fringe/src/fringe/templates/counters/*`), 2 files** |  |
| `counters/FringeCounter.scala` | Single-width counter with stride, done, saturate; used for the DRAMArbiter timeout. |
| `counters/Counter.scala` | `NBufCtr`, `IncDincCtr`, `SingleCounter`, `CompactingCounter`, `CounterChain`, `IICounter` — the per-stage iteration counter library used by `Kernel.configure`. |
| **Controllers (`fringe/src/fringe/templates/Controllers.scala`)** | `ControlInterface`, `ControlParams`, `GeneralControl`, `OuterControl`, `InnerControl`, `FSMControl`, `Switch*`; sealed `Sched` trait with `Sequenced`/`Pipelined`/`Streaming`/`Fork`/`ForkJoin`. |
| **Retiming (`fringe/src/fringe/templates/retiming/*`), 2 files** | `RetimeWrapper`, `RetimeWrapperWithReset`, `RetimeShiftRegister`, unused `Offset`. |
| **Systolic (`fringe/src/fringe/templates/SystolicArray.scala`)** | `SystolicArray2D` template parameterised by dims/neighborhood/movement. |
| **Vector (`fringe/src/fringe/templates/vector/Shuffle.scala`)** | Compress-network for vector shuffle lanes. |
| **Math (`fringe/src/fringe/templates/math/*`), 9 files** | `Math` dispatch object, `FixedPoint` / `FloatingPoint` types, `Converter`, `FullAdder` (unused), `PRNG`, rounding/overflow ADTs, `package.scala`. |
| **HardFloat (`fringe/src/fringe/templates/hardfloat/*`), 21 files** | Verbatim Berkeley HardFloat IEEE-754 library: `MulAddRecFN`, `DivSqrtRecF64*`, `DivSqrtRecFN_small`, `CompareRecFN`, `RecFNToRecFN`, `rawFloatFromFN`, `recFNFromFN`, `RoundAnyRawFNToRecFN`, `INToRecFN`, `RecFNToIN`, `classifyRecFN`, `fNFromRecFN`, `resizeRawFloat`, `tests.scala`, + 7 `ValExec_*` harnesses. |
| **Euresys (`fringe/src/fringe/templates/euresys/Bundles.scala`)** | CoaXPress `Metadata_rec` + `CXPStream` for CXP image capture. |
| **Ledger + ModuleParams (`fringe/src/fringe/templates/Ledger.scala`, `fringe/ModuleParams.scala`)** | Cross-kernel port-boring registry with `KernelHash`/`OpHash`; mutable shared `ModuleParams` map for generated code. |
| **Utils (`fringe/src/fringe/utils/*`), 12 files** |  |
| `utils/package.scala` | `mux`, `delay`, `getRetimed`, `getFF`, `pulse`, `risingEdge`, `streamCatchDone`, `canSee/lanesThatCanSee` banking-view helpers. |
| `utils/implicits.scala` | Postfix operators on `UInt`/`SInt`/`Bool`/`Vec`/`FixedPoint` — pervasive `a.D(lat)` retiming shortcut. |
| `utils/MuxN.scala`, `HVec.scala`, `GenericParameterizedBundle.scala` | Large-fan-in pipelined mux, heterogeneous vec, cloneType scaffolding. |
| `utils/Depulser.scala`, `Pulser.scala`, `StickySelects.scala` | Edge-detection + sticky arbitration. |
| `utils/Access.scala`, `Banks.scala` | Port metadata case classes tying generated code to memory primitives. |
| `utils/GCD.scala`, `UIntLike.scala` | Unused / helper types. |

## 3. Key types / traits / objects

- **`Fringe` (`fringe/src/fringe/Fringe.scala:20-218`)** — top common shell. IO exposes `raddr/wen/waddr/wdata/rdata`, `enable/done/reset`, `argIns`/`argOuts`/`argEchos`, `memStreams` (AppStreams), `dram: Vec[DRAMStream]`, `heap`, `aws_top_enable`. Callers: all per-target `Fringe<Target>` wrappers (`FringeZynq`, `FringeArria10`, `FringeCXP`, `FringeZedBoard`) and `SimTarget.addFringeAndCreateIP`.
- **`AbstractAccelUnit` / `AccelInterface` (`fringe/src/fringe/AccelTopInterface.scala:9-64`)** — The `spatial`-generated AccelUnit extends this. Exposes `done`, `enable`, `reset`, `argIns`, `argOuts`, `memStreams`, `axiStreamsIn/Out`, `heap`. Caller: `SpatialIP.accelGen` and every `addFringeAndCreateIP` implementation.
- **`DeviceTarget` (`fringe/src/fringe/targets/DeviceTarget.scala:7-67`)** — per-target strategy. Key methods: `makeBigIP`, `addFringeAndCreateIP(reset, accel)`, `makeIO`. Constants: `addrWidth`, `dataWidth`, `wordsPerStream`, `external_w`, `external_v`, `burstSizeBytes=64`, `maxBurstsPerCmd=256`, `bufferDepth=64`, `num_channels`, plus tunable op latencies (`fixmul_latency`, `fixdiv_latency`, ...).
- **`BigIP` (`fringe/src/fringe/BigIP.scala:6-105`)** — abstract numeric-kernel factory. 45+ methods (`divide`, `mod`, `multiply`, `fadd`, `fmul`, `fdiv`, `fltaccum`, `fix2flt`, `flt2fix`, `frsqrt`, `fsigmoid`, `ftanh`, ...). Subclassed by `BigIPSim`, `BigIPZynq`, `BigIPZCU`, `BigIPAWS*`, `BigIPArria10`, `BigIPASIC`, `BigIPAWS_Sim`, `BigIPZedBoard`, `BigIPCXP`, `BigIPVCS`, `BigIPVCU1525`, `BigIPKCU1500`, `bigIPDE1SoC`. Consumed via `globals.bigIP` in `templates/math/Math`.
- **`globals` object (`fringe/src/fringe/globals.scala:8-79`)** — singleton mutable configuration: `var target`, `numArgIns/Outs/IOs/Instrs`, `loadStreamInfo`/`storeStreamInfo`/`gatherStreamInfo`/`scatterStreamInfo`, `numAllocators`, `retime`, `perpetual`, `enableModular`, `enableDebugRegs`, `channelAssignment`, `tclScript`. Read by the top `Fringe`, every target shell, the DRAMArbiter, and the `spatial`-generated accel code. This global state is how `spatial` compiler output parameterises Fringe at Chisel-elaboration time.
- **`DRAMArbiter` (`fringe/src/fringe/templates/dramarbiter/DRAMArbiter.scala:13-266`)** — one instance per memory channel; wires loads/stores/gathers/scatters into `StreamArbiter` → `AXICmdSplit` → `AXICmdIssue`. Emits `cpp/generated_debugRegs.h` with ~500 signal labels when `isDebugChannel`.
- **`AppStreams` / `DRAMStream` / `DRAMCommand` / `DRAMTag` (`fringe/src/fringe/FringeBundles.scala:41-184`)** — the canonical bundles on the accel↔fringe boundary. `DRAMTag` packs `streamID(8b)`, `cmdSplitLast(1b)`, `uid` so AXI bus truncation preserves streamID across all targets.
- **`RegFile` (`fringe/src/fringe/templates/memory/RegFile.scala:15-…`)** — scalar register file with asymmetric argIn (parallel read) and argOut (Decoupled write) ports; row 0 is command, row 1 is status, additional rows are per-argIn/argOut/argIO/debug slots.
- **`Ledger` (`fringe/src/fringe/templates/Ledger.scala:71-326`)** — singleton for cross-kernel port "boring". Provides `connectRPort/WPort/StructPort/BroadcastR/BroadcastW/Reset/Output/AccessActivesIn/StageCtrl/MergeEnq/MergeDeq/MergeBound/MergeInit/AllocDealloc`, `enter/exit/substitute`, `connectInstrCtrs`, `connectBreakpoints`. Called by spatial-generated accelerator code via implicit `stack: List[KernelHash]`.
- **`GeneralControl` / `OuterControl` / `InnerControl` hierarchy (`fringe/src/fringe/templates/Controllers.scala:56-…`)** — `ControlInterface` carries `enable`, `done`, `datapathEn`, `ctrInc`, `ctrRst`, `doneIn`/`maskIn`/`ctrCopyDone` vectors, plus FSM `state/nextState/initState`. `sealed trait Sched` with `Sequenced`/`Pipelined`/`Streaming`/`Fork`/`ForkJoin`.
- **`Kernel` abstract (`fringe/src/fringe/SpatialBlocks.scala:96-172`)** — scaffolding spatial-generated code extends. `.configure(...)` wires control signals, counter chain, II counter, and mask/backpressure glue between parent/child kernels.

## 4. Entry points

Externally visible objects that `spatial` codegen and build scripts depend on:

- **`fringe.SpatialIP`** (`fringe/src/fringe/SpatialIP.scala:18-41`) — the synthesised top; generated Instantiator code instantiates it with a target name string and an `accelGen: () => AbstractAccelUnit` closure.
- **`fringe.AbstractAccelUnit` / `AccelInterface`** — generated AccelUnit subclasses this.
- **`fringe.globals`** — generated Instantiator sets `globals.target`, `globals.numArgIns`, `globals.numArgOuts`, `globals.loadStreamInfo`, `globals.storeStreamInfo`, `globals.gatherStreamInfo`, `globals.scatterStreamInfo`, `globals.numAllocators`, `globals.channelAssignment`, `globals.retime`, `globals.perpetual`.
- **`fringe.Ledger`** — implicit-imported `Ledger._` in generated kernel code (`connect*`, `enter`, `exit`, `KernelHash`, `OpHash`).
- **`fringe.templates.math.Math`** — every arith op in generated code dispatches through `Math.{mul,div,mod,fadd,fmul,fdiv,ffma,flt2fix,fix2flt,...}`, which routes to `globals.bigIP`.
- **`fringe.templates.memory.{BankedSRAM, Mem1D, FF, FIFO, LIFO, ShiftRegFile, LineBuffer, NBufMem, FixFMAAccum, FixOpAccum, RegFile, MergeBuffer, DRAMAllocator}`** — per-memory backend modules.
- **`fringe.templates.counters.{Counter, CounterChain, SingleCounter, NBufCtr, IICounter, CompactingCounter}`**.
- **`fringe.templates.Controllers.{OuterControl, InnerControl, FSMControl, SwitchControl, ControlParams, Sequenced, Pipelined, Streaming, Fork, ForkJoin}`**.
- **`fringe.templates.retiming.{RetimeWrapper, RetimeShiftRegister}`** and `fringe.utils.getRetimed`.
- **`fringe.templates.SystolicArray2D`**, `fringe.templates.vector.ShuffleCompressNetwork`.
- **`fringe.ModuleParams`** (`fringe/src/fringe/templates/ModuleParams.scala:9-16`) — a mutable `Map[String, Any]` used by generated code to share named-parameter payloads across elaboration phases.
- **`fringe.CommonMain`** (`fringe/src/fringe/CommonMain.scala:12-72`) — base for generated `Top` main objects; handles Chisel vs. test argument splitting.
- Via `DeviceTarget` implementations: Vivado/Quartus-level IP wrapping (each `Fringe<Target>` module emits a synth-ready shell).

## 5. Dependencies

Upstream (used by Fringe):
- `chisel3`, `chisel3.util`, legacy `Chisel._` (for Diplomacy subset).
- `emul.FixFormat`, `emul.FltFormat`, `emul.ResidualGenerator` — the scalar-emulation library providing pure-Scala number types and residual generators used for banking-view proofs.
- `utils.math.{log2Up, numBanks, elsWidth, ofsWidth, banksWidths, volume}` — shared math helpers outside Fringe.
- `java.io` for TCL script + debug header emission.

Downstream (callers of Fringe):
- `spatial.codegen.chiselgen` and the generated `Top.scala` / `Instantiator.scala` — these are the only external callers and they import `fringe._`, `fringe.templates.memory._`, `fringe.templates.counters._`, `fringe.templates.Controllers._`, `fringe.templates.math._`, `fringe.utils._`, `fringe.utils.implicits._`, `fringe.Ledger._`, `fringe.templates.retiming._`, `fringe.SpatialBlocks._`.
- Per-target build scripts (Makefiles under `fringe/` but not Scala) consume the generated Verilog + `bigIP.tcl` (written to disk by `globals.tclScript`).

No dependency on `argon` or the core `spatial/` IR — Fringe is strictly the hardware shim and is symbol-clean at its upward boundary.

## 6. Key algorithms

- **Per-channel stream arbitration** (`fringe/src/fringe/templates/dramarbiter/StreamArbiter.scala:17-74`): priority-encode valid commands, latch to serve full burst before switching, pipelined mux for high fanout.
- **AXI command splitting** (`fringe/src/fringe/templates/dramarbiter/AXIProtocol.scala:9-48`): any burst longer than `target.maxBurstsPerCmd` is split in-flight; tags the last split with `cmdSplitLast` so only the final `wresp` is propagated to the app.
- **AXI write issue gating** (`fringe/src/fringe/templates/dramarbiter/AXIProtocol.scala:50-88`): once-per-burst command emit; tracks wdata count to assert `wlast` on the final beat.
- **Width conversion FIFO** (`fringe/src/fringe/templates/dramarbiter/FIFOWidthConvert.scala:7-…`): two-way resizing between app (w,v) and DRAM (EXTERNAL_W, EXTERNAL_V).
- **Gather coalescing** (`fringe/src/fringe/templates/dramarbiter/GatherBuffer.scala:10-…`): `GatherAddressSelector` groups same-burst addresses; priority on unissued lanes to prevent starvation.
- **Scatter strobe generation** (`fringe/src/fringe/templates/dramarbiter/StreamController.scala:185-218`): word-offset computed per-element from `DRAMAddress.wordOffset`, encoded as one-hot `wstrb`.
- **DRAMTag layout** (`fringe/src/fringe/FringeBundles.scala:175-184`): `streamID` in low 8b so any FPGA target sees it; `cmdSplitLast` bit; variable `uid` that may be truncated when AXI ID width < 32.
- **Host register-file pulse-to-steady bridge** (`fringe/src/fringe/Fringe.scala:153-182`): `Depulser` converts the accel's single-cycle `done` pulse to a steady status-register bit consumed by the host over AXI-lite; a 40-bit `FringeCounter` with max=12e9 provides a hardware timeout flag.
- **Channel assignment strategies** (`fringe/src/fringe/ChannelAssignment.scala:10-34`): `AllToOne`, `BasicRoundRobin`, `ColoredRoundRobin` (uses `StreamParInfo.memChannel` mod numChannels), and a stub `AdvancedColored`.
- **Ledger port-boring** (`fringe/src/fringe/templates/Ledger.scala:160-326`): keyed by `(OpHash, KernelHash)`, accumulates all port kinds per-kernel as the elaboration visit bubbles up through the nested kernels.
- **Kernel control wiring** (`fringe/src/fringe/SpatialBlocks.scala:117-171`): `configure()` ties state-machine to counter chain, II counter, backpressure/forwardpressure, mask, handles streaming outer-controller special case (ctrCopyDone), wires cchainEnable for parent-streaming descendants.
- **Berkeley HardFloat** (`fringe/src/fringe/templates/hardfloat/*`): recoded-format IEEE fp, `MulAddRecFN`, `DivSqrtRecF64_mulAddZ31`, round-any-raw `RoundAnyRawFNToRecFN`. Unmodified library import.
- **AXI4-Lite slave register-file bridge** (`fringe/src/fringe/templates/axi4/AXI4LiteToRFBridge.scala:5-120`): three variants that wrap a Verilog BlackBox implementing AXI4-Lite read/write handshake on a 32- or 64-bit register file.
- **MAG→AXI4 protocol conversion** (`fringe/src/fringe/templates/axi4/MAGToAXI4Bridge.scala:9-75`): hard-codes ARSIZE=6 (64-B beat), BURST=INCR, CACHE=3 (or 15 on ZCU); byte-reverses wdata/wstrb; ties RID/BID to stream tag.

## 7. Invariants / IR state read or written

- `globals.target` must be set before any Chisel Module is elaborated; `SpatialIP` asserts this by assigning it in its constructor (`fringe/src/fringe/SpatialIP.scala:19-34`).
- `globals.numArgIns`, `numArgOuts`, `numArgIOs` — total register count is `NUM_ARG_INS + NUM_ARG_OUTS + 2` (two status/command regs); `RegFile` and `FringeZynq` assume this layout.
- `globals.{load,store,gather,scatter}StreamInfo` — empty lists fall back to a single synthetic stream using `DATA_WIDTH`/`WORDS_PER_STREAM` (`globals.scala:62-68`).
- `ADDR_WIDTH`, `DATA_WIDTH`, `EXTERNAL_W`, `EXTERNAL_V`, `TARGET_W`, `WORDS_PER_STREAM`, `NUM_CHANNELS` are all read from `target` at elaboration time; mutating `target` after elaboration is undefined.
- `DRAMCommand.size` is in **bursts** on the DRAM stream but in **bytes** on the app-side (`StreamController.sizeBytesToSizeBurst`), a well-known source of bugs (`StreamController.scala:20-22`).
- `DRAMTag.streamID` must be `≤ 8` bits wide; asserted in `DRAMArbiter.scala:55`.
- `AXI4BundleParameters` require `dataBits ≥ 8`, `addrBits ≥ 1`, `idBits ≥ 1`, `dataBits` is power-of-two (`axi4/Parameters.scala:74-83`).
- `Ledger.connections` is a mutable HashMap keyed by `OpHash`; relies on Chisel's `.hashCode` being stable during elaboration, and on the `ControllerStack` being maintained symmetrically (`Ledger.enter/exit`).
- `ModuleParams.mapping` — insert-once semantics (`addParams` is a no-op if key exists); generated code must not overwrite.
- The `tclScript` PrintWriter is opened eagerly on `globals` object init (`globals.scala:35-40`), even if not used — side effect of singleton object loading.
- `globals.bug239_hack` at `Fringe.scala:123-129` is a known-wrong behavior: rdata is shift-registered by 1 on all targets except AWS_Sim/VCS/ASIC to compensate for an axi4-to-rf bridge timing bug.
- `DeviceTarget.addFringeAndCreateIP` returns a `SpatialIPInterface` that must match the target's top-level Verilog pinout expected by the Vivado/Quartus project file.

## 8. Notable complexities or surprises

- **Mutable global `target`** (`globals.scala:10`) + singleton `bigIP` (lazy once set) means Fringe is not reentrant in a single Chisel elaboration pass; running multiple SpatialIP instantiations requires resetting globals.
- **bug239 workaround** in `Fringe.scala:122-129`: the comment "Fix this bug asap" is 7 years old.
- **Dual packages for AXI4 params**: `fringe.templates.axi4.AXI4Parameters` (constant widths) vs `AXI4BundleParameters` (per-bundle sizes) — easy to confuse. `AXI4Parameters.scala` uses the legacy `Chisel._` import while the rest uses `chisel3._`.
- **FringeZynq is the common-case target shell** — despite its name, it is reused by Zynq, ZCU, KCU1500, ZedBoard, AWS_F1, and AWS_Sim (via delegation in their `addFringeAndCreateIP`). Target-specific logic inside `FringeZynq` is driven by `target.isInstanceOf[...]` branches.
- **`argOuts` Decoupled but `ready` is ignored** — `Fringe.scala:165-182` hard-assigns `argOutReg.valid` and `argOutReg.bits` without a ready-valid handshake; comment at line 165-167 acknowledges this ("we do not care about [ready]").
- **`globals.tclScript`** is opened unconditionally on class load (`globals.scala:34-38`) and writes to `bigIP.tcl` in cwd — the side-effect on module import can interact badly with test frameworks.
- **`signalLabels`** list buffer only populates when `enableDebugRegs`; the same `connectDbgSig` is gated by both `isDebugChannel` (module-instance) and `enableDebugRegs` (global), so enabling one without the other is silently inert (`DRAMArbiter.scala:107-118`).
- **AXI4Lite bridge is a Verilog BlackBox** (`AXI4LiteToRFBridge.scala:5-19`); Chisel tests cannot verify the handshake. The commented-out Chisel implementation at lines 124-238 suggests an earlier attempt was abandoned.
- **`GatherBuffer` tag-sharing hack** (`StreamController.scala:149-152`): the gather-burst uid is piggybacked on `DRAMTag.uid`, relying on the arbiter not overwriting it.
- **HardFloat files include a verbatim Berkeley license** and are imported un-refactored; modifying them risks diverging from the upstream library.
- **Diplomacy subset** (`templates/diplomacy/*`) uses the legacy `Chisel._` import style, not `chisel3._`, and is imported into AXI parameter parsing — bridging the two import conventions is a minor source of `.U`/`.toBool` churn in target code.
- **`enableModular` global** gates all Ledger activity (`Ledger.scala:195, 202, …`). If false, no port boring happens — generated code must align naively by reference.
- **`bug239_hack`, `TODO: What is this?` comments** on `blockingDRAMIssue`, `magPipelineDepth`, `target_w`, `addrWidth`, `dataWidth`, `external_w`, `external_v`, `wordsPerStream`, `numArgInstrs`, `argOutLoopbacksMap`, `sqrt`, `fabs`, etc. (DeviceTarget.scala:33-55, BigIP.scala:22-23, Fringe.scala:17-19, globals.scala:45-51) are legitimate open questions left by the original authors.
- **`Offset.scala` and `FullAdder.scala` and `GCD.scala` are marked NOTE: unused** — dead code kept for documentation or future expansion (retiming/Offset.scala:5; math/FullAdder.scala:6; utils/GCD.scala:6).
- **`AXI4Stream` extends `AXI4BundleBase(params.asDummyAXI4Bundle)`** — hack to reuse the GenericParameterizedBundle cloneType; `asDummyAXI4Bundle` ignores all AXI4 fields except dataBits/idBits.

## 9. Open questions

- What is the precise semantics of `blockingDRAMIssue` in `Fringe`/`FringeZynq`? The parameter is threaded through but I did not find a consumer in the read pass.
- What does `magPipelineDepth` control — pipeline stages between the DRAMArbiter and the AXI master? `MAGToAXI4Bridge.scala:20` references `numPipelinedLevels = globals.magPipelineDepth` but never uses it.
- Is `AdvancedColored` ever selected by `spatial`? The comment flags it as `TODO` (`ChannelAssignment.scala:32-34`).
- What invariant ensures `globals.numAllocators == accel.io.heap.length`?
- The `numDebugs = 500` in `DRAMArbiter.scala:22` is a hard cap; what happens when more signals are registered?
- Why does `Fringe.commandReg = 0` / `statusReg = 1` at line 21-22 if the logic does not use them? The comment says "used in test only" — which test?
- Relationship between `spatial.SpatialBlocks.Kernel` (used by generated code) and the `spatial` IR's `Block`/`Lambda` representation is not visible from Fringe alone.
- Does `perpetual` mode disable the timeout counter as well, or only the `done`-gated enable (`Fringe.scala:134`)?
- `argOutLoopbacksMap: Map[Int,Int]` is an untouched global — who populates it and what is the loopback semantics?
- The AXI-lite bridge relies on `~reset.toBool` (`AXI4LiteToRFBridge.scala:41, 87`) — is active-high vs active-low reset consistent across targets?

## 10. Suggested spec sections

Content here will feed the spec tree under `10 - Spec/`:

- `10 - Spec/14 - Backend/01 - Fringe architecture.md` — top-level `SpatialIP`/`Fringe` module map, per-target shell overview, IO contract with Accel.
- `10 - Spec/14 - Backend/02 - DRAM arbiter and AXI protocol.md` — the DRAMArbiter/StreamArbiter/AXICmdSplit/AXICmdIssue pipeline; channel assignment; scatter/gather handling.
- `10 - Spec/14 - Backend/03 - AXI4 bundles and parameters.md` — AXI4Bundle vs AXI4Inlined, AXI4Lite, AXI4Stream, AXI4Probe, and the MAGToAXI4Bridge.
- `10 - Spec/14 - Backend/04 - Host-side scalar interface.md` — RegFile + AXI4LiteToRFBridge, argIn/argOut/argIO/status/command layout, Depulser, timeout counter.
- `10 - Spec/14 - Backend/05 - DRAM allocator and heap.md` — DRAMAllocator + DRAMHeap arbitration to the host alloc/dealloc path.
- `10 - Spec/14 - Backend/06 - Hardware primitives.md` — the memory/counters/controllers/retiming/systolic/vector template zoo.
- `10 - Spec/14 - Backend/07 - BigIP and arithmetic.md` — BigIP dispatch, per-target FP/fix implementations, HardFloat import.
- `10 - Spec/14 - Backend/08 - Ledger and modular elaboration.md` — cross-kernel port boring, ExposedPorts, enableModular flag, ModuleParams.
- `10 - Spec/14 - Backend/09 - Device targets.md` — per-target shell inventory, `addFringeAndCreateIP` protocol, which targets share `FringeZynq`.
- `10 - Spec/14 - Backend/10 - Debug infrastructure.md` — `generated_debugRegs.h`, `bigIP.tcl`, AXI4Probe, the 500-signal debug slot budget.
- Cross-references in `40 - Cross References/`: Fringe ↔ spatial chiselgen backend (DRAM interface, argIn/argOut binding, Ledger port boring).
- A Phase-2 deep-dive file for the HardFloat subtree is likely unnecessary — it is a verbatim import and not Spatial-specific.
