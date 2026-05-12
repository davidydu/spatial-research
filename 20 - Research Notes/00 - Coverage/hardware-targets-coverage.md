---
type: coverage
subsystem: Hardware targets
paths:
  - "src/spatial/targets/"
file_count: 27
date: 2026-04-21
verified:
  - 2026-04-21
---

## 1. Purpose

The `spatial.targets` package defines the hardware-target abstraction layer that parameterizes Spatial's area/latency estimation, memory-allocation heuristics, and codegen choice. A `HardwareTarget` bundles: a resource-capacity vector (e.g., BRAM/DSP/Regs), a DRAM `burstSize`, a `clockRate`, a set of `MemoryResource` kinds with their minimum-depth cutoffs, and factories for per-target `AreaModel` and `LatencyModel`. The subsystem sits between two places in the pipeline: the CLI/top-level driver in `spatial/Spatial.scala` selects a concrete target object (default `xilinx.Zynq`) and stores it on `spatialConfig.target`, and DSE/analysis passes (`DSEAreaAnalyzer`, `LatencyAnalyzer`, `MemoryAllocator`, `BankingData.resource`) and codegens (`ChiselCodegen`, `ScalaGenDRAM`, cpp/rogue host codegens) read the target for resource counts, memory assignment, and host-code dispatch. It does no IR transformation itself — it is pure configuration data plus estimation logic keyed off the node IR.

## 2. File inventory

| Path | Purpose |
| --- | --- |
| `src/spatial/targets/HardwareTarget.scala` | Abstract base class defining the target interface: capacity, burstSize, clockRate, memoryResources, areaModel/latencyModel factories, analyzer constructors. |
| `src/spatial/targets/AreaModel.scala` | Abstract area model: `areaOf`, `areaOfMem`, `areaOfReg`, banked-memory raw-area helpers, delay-line model, and `summarize` contract. |
| `src/spatial/targets/LatencyModel.scala` | Concrete base latency model: latencyOfNode, parallel/streaming/metaPipe/sequential control-loop models, retime-register predicates. |
| `src/spatial/targets/MemoryResource.scala` | Abstract `MemoryResource(name)` with `area(width,depth)`, `summary(area)`, `minDepth` — the unit of the memory-allocator packing problem. |
| `src/spatial/targets/NodeParams.scala` | `trait NodeParams`: maps each `Op[_]` to a `(name, params)` tuple used as the key/args into the per-target CSV model tables. |
| `src/spatial/targets/SpatialModel.scala` | Generic CSV-backed model base (parent of AreaModel and LatencyModel). Loads `models/*.csv` at init, memoizes, reports missing entries. |
| `src/spatial/targets/package.scala` | Package-object target registry: `fpgas`, `all`, `Default = xilinx.Zynq`, convenience aliases. |
| `src/spatial/targets/xilinx/XilinxDevice.scala` | Base class for Xilinx FPGAs: 28 AFIELDS (LUT1–6, SLICEL/M, RAM18/36, BRAM/URAM, DSPs, etc.), four MemoryResource objects (URAM, BRAM, URAM_OVERFLOW, LUTs), BRAM/URAM/distributed analytical models. |
| `src/spatial/targets/xilinx/XilinxAreaModel.scala` | Xilinx `summarize`: aggregates LUTs into slices, rolls RAM18/36 into BRAM count, emits breakdown report vs. capacity. |
| `src/spatial/targets/xilinx/{Zynq, ZCU, ZedBoard, AWS_F1, KCU1500}.scala` | Five concrete Xilinx FPGA objects, each defining `name`, `burstSize`, and a `capacity` Area vector. `KCU1500` overrides `host = "rogue"`; `AWS_F1` adds URAM capacity. |
| `src/spatial/targets/altera/AlteraDevice.scala` | Altera base — near-duplicate of `XilinxDevice` (same AFIELDS, same BRAM/URAM/LUT memory models). TODO comments flag that fields need Altera-correct values. |
| `src/spatial/targets/altera/AlteraAreaModel.scala` | Altera `summarize` — duplicates XilinxAreaModel but adds `+ model("Fringe")()` and gates the breakdown on `config.enInfo`. |
| `src/spatial/targets/altera/{Arria10, DE1}.scala` | Two Altera target objects with empty `capacity` (stubs). |
| `src/spatial/targets/euresys/EuresysDevice.scala` | Euresys base — another near-duplicate of XilinxDevice. |
| `src/spatial/targets/euresys/EuresysAreaModel.scala` | Euresys `summarize` — same body as Altera version (adds Fringe, gates on `config.enInfo`). |
| `src/spatial/targets/euresys/CXP.scala` | Euresys CoaXPress target object. |
| `src/spatial/targets/generic/GenericDevice.scala` | Generic-FPGA base — same Xilinx-style AFIELDS plus an extra `SRAM_RESOURCE` (unused in its default list). Uses `GenericLatencyModel`. |
| `src/spatial/targets/generic/GenericAreaModel.scala` | Generic `summarize` — body identical to XilinxAreaModel (report gated `false`). |
| `src/spatial/targets/generic/GenericLatencyModel.scala` | Extends `LatencyModel` to override `latencyOfNode` for `DenseTransfer` load/store with a hand-tuned memory-transfer formula; delegates other nodes to `super`. |
| `src/spatial/targets/generic/TileLoadModel.scala` | Placeholder for an Encog neural-net model of tile-load latency — body is commented out, `evaluate` returns `0.0`. |
| `src/spatial/targets/generic/ASIC.scala` | ASIC target: empty AFIELDS, DSP_CUTOFF=0, uses `GenericAreaModel` but `LatencyModel(xilinx.Zynq)` (note: borrows Zynq's latency data), SRAM_RESOURCE. |
| `src/spatial/targets/generic/VCS.scala` | Simulation target: extends GenericDevice with effectively infinite capacity. |
| `src/spatial/targets/plasticine/Plasticine.scala` | Plasticine CGRA target: empty AFIELDS, DSP_CUTOFF=0, clockRate=1000 MHz, empty capacity, SRAM_RESOURCE. |
| `src/spatial/targets/plasticine/PlasticineAreaModel.scala` | Trivial `summarize` returning `(area, "")`. |

## 3. Key types / traits / objects

### `abstract class HardwareTarget` — `spatial/targets/HardwareTarget.scala:7-50`

The core abstraction. Subclasses must supply:
- `name: String` (FPGA name), `burstSize: Int` (DRAM burst bits).
- `val AFIELDS: Array[String]` — per-device area resource names fed to the CSV model schema.
- `val DSP_CUTOFF: Int` — smallest integer-add width that goes to DSP instead of LUTs.
- `def capacity: Area` — device resource maxima keyed by AFIELDS name.
- `val memoryResources: List[MemoryResource]`, `val defaultResource: MemoryResource`.
- `protected def makeAreaModel(mlModel: AreaEstimator): AreaModel`, `protected def makeLatencyModel: LatencyModel`.

Cross-subsystem-visible methods (`spatial/targets/HardwareTarget.scala:35-48`):
- `final def areaModel(mlModel)`, `final def latencyModel` — memoized singletons.
- `@stateful final def areaAnalyzer(mlModel): DSEAreaAnalyzer` and `@stateful final def cycleAnalyzer: LatencyAnalyzer` — produce the two DSE traversals. Callers: `spatial/Spatial.scala:637-638` (init) and DSE drivers (`DSEThread`, `HyperMapperThread`).

Fixed per-target default: `clockRate = 150.0f` MHz, `baseCycles = 43000`, `host = "cpp"` (Xilinx `KCU1500` overrides to `"rogue"` at `spatial/targets/xilinx/KCU1500.scala:7`; Plasticine overrides clockRate at `plasticine/Plasticine.scala:13`).

The companion `object HardwareTarget` exposes the five `LFIELDS` string constants (`RequiresRegs`, `RequiresInReduce`, `LatencyOf`, `LatencyInReduce`, `BuiltInLatency`) that parameterize the latency CSV schema (`spatial/targets/HardwareTarget.scala:52-58`).

### `abstract class SpatialModel[F[_]<:Fields[_,_]]` — `spatial/targets/SpatialModel.scala:11-117`

Shared base for `AreaModel` and `LatencyModel`. Key methods:
- `init()` — lazy one-shot CSV load via `loadModels()`.
- `loadModels()` at `SpatialModel.scala:74-112` — reads `models/<FILE_NAME>` either via `Source.fromResource` or `$SPATIAL_HOME/models/<FILE_NAME>`; parses `Param…` columns plus the FIELDS columns into `Model.fromArray`.
- `model(sym: Sym[_])` at `SpatialModel.scala:55-61` — routes through `NodeParams.nodeParams(sym, op)` to produce `(name, args)` then looks up `models(name).eval(args)`.
- `miss(str)` / `reportMissing()` — accumulates CSV-miss warnings.

Callers: both `AreaModel` and `LatencyModel` inherit; `Spatial.scala:637-638` triggers `areaModel.init()` / `latencyModel.init()`.

### `abstract class AreaModel(target, mlModel)` — `spatial/targets/AreaModel.scala:15-208`

Subsystem-visible API:
- `@stateful areaOf(e, inHwScope, inReduce): Area` at `AreaModel.scala:29-35` — dispatch: inside-reduce calls `areaInReduce`, outside calls `areaOfNode`.
- `@stateful areaOfNode(lhs, rhs): Area` at `AreaModel.scala:161-191` — per-node area pattern match (`Transient`, `DelayLine`, `FixMul/Div/Mod`, `MemAlloc`, `Accessor`, default falls through to `model(lhs)`).
- `@stateful areaOfMem(mem, name, dims): Area` at `AreaModel.scala:60-92` — computes banking-histogram features and calls `mlModel.estimateMem` for LUTs/FFs plus analytical RAM36 count.
- `@stateful rawMemoryArea/rawMemoryBankArea` at `AreaModel.scala:119-154` — used by `DSEAreaAnalyzer` for per-instance cost.
- `@stateful summarize(area): (Area, String)` — abstract, each device subclass rolls up its resource breakdown and optionally builds a human-readable report.

The `mlModel: AreaEstimator` (from `models.AreaEstimator`) is an injected ML area estimator for memory-area queries — only used for SRAM/RegFile/LineBuffer via `areaOfMem`.

### `class LatencyModel(target)` — `spatial/targets/LatencyModel.scala:10-67`

Non-abstract. Key methods:
- `@stateful latencyOf(s, inReduce): Double` at `LatencyModel.scala:17-20` — honors `s.hasForcedLatency`, else dispatches in/out of reduce.
- `@stateful requiresRegisters(s, inReduce): Boolean` at `LatencyModel.scala:25-34` — retime-register gate, controlled by `spatialConfig.addRetimeRegisters`.
- `@stateful builtInLatencyOfNode(s): Double` at `LatencyModel.scala:46` — used for templates that hard-wire an internal delay register (e.g., FIFODeq) so the retimer injects one fewer.
- Four loop-schedule models — `parallelModel` (`LatencyModel.scala:48-50`), `streamingModel`, `metaPipeModel`, `sequentialModel`, `outerControlModel` — consumed by `LatencyAnalyzer`.

`GenericLatencyModel` at `generic/GenericLatencyModel.scala:11-67` overrides `latencyOfNode` for `DenseTransfer` to plug in the logistic-based memory-transfer formula `memoryModel(c, r, b, p)`.

### `abstract class MemoryResource(name)` — `spatial/targets/MemoryResource.scala:6-10`

Two abstract members — `area(width, depth): Area`, `summary(area): Double` — plus a concrete default `minDepth: Int = 0` (overridable by subclasses). Concrete objects (defined *inside* each device subclass) include `URAM_RESOURCE`, `BRAM_RESOURCE`, `URAM_RESOURCE_OVERFLOW`, `LUTs_RESOURCE`, and `SRAM_RESOURCE`. Callers: `MemoryAllocator` packs memories into `target.memoryResources` (`traversal/MemoryAllocator.scala:56-103`); `metadata/memory/BankingData.scala:186-187` stores the chosen `resourceType` per duplicate, falling back to `spatialConfig.target.defaultResource`.

### `trait NodeParams` — `spatial/targets/NodeParams.scala:16-70`

`nodeParams(s, op)` maps every IR op class to a `(csvKeyName, (paramName -> double) list)` signature used when interrogating the CSV-backed `model(name)(args)` lookup. Handles specialized cases: `RegAccumFMA` and `RegAccumOp` (with log2-corrected drain/layers), fixed/float ops, `DelayLine` (emits 0 for non-user-injected delays), `Mux`/`OneHotMux`/`PriorityMux`, `SpatialBlackboxUse`/`VerilogBlackbox` (pull body latency out of metadata), async SRAM reads gated on `spatialConfig.enableAsyncMem`, `Switch`, `CounterNew`/`CounterChainNew`, and outer control blocks (key = schedule style, param `n = children.length`).

### `package object spatial.targets` — `spatial/targets/package.scala:3-31`

The public target registry. `Default = xilinx.Zynq` (line 16); `fpgas = {Zynq, ZCU, ZedBoard, AWS_F1, KCU1500, CXP, DE1, Arria10, VCS}` (lines 4-14); `all = fpgas + Plasticine` (line 30). Also re-exports each concrete target as a lazy val. This is the name → object table consumed by `Spatial.scala:598`.

## 4. Entry points

The integration seam is narrow:

- **Target selection**: `Spatial.scala:264,594,598-618` — CLI `--fpga=<name>` triggers a case-insensitive lookup in `targets.all`; fallback to `targets.Default`. Result stored on `spatialConfig.target: HardwareTarget` (declared in `SpatialConfig.scala:10`).
- **Model init**: `Spatial.scala:637-638` — `spatialConfig.target.areaModel(mlModel).init()` and `.latencyModel.init()` before DSE.
- **Area/latency queries**: `util/modeling.scala:87-90` — helper accessors `target`, `areaModel(mlModel)`, `latencyModel`, which the rest of the compiler uses.
- **Analyzer constructors**: `HardwareTarget.areaAnalyzer` / `.cycleAnalyzer` — produce the two DSE passes (`DSEAreaAnalyzer`, `LatencyAnalyzer`).
- **Memory allocation**: `MemoryAllocator.scala:46,56` reads `target.capacity` and iterates `target.memoryResources`.
- **Resource assignment metadata**: `metadata/memory/BankingData.scala:186-187` — `resource` getter falls back to `spatialConfig.target.defaultResource`.
- **Codegen dispatch**: `Spatial.scala:247-248` uses `spatialConfig.target.host` to pick between C++ and Rogue host-codegens; `ChiselCodegen.scala:144-145` and `ScalaGenDRAM.scala:20` read `target.name` / `target.burstSize` for emitted constants.

## 5. Dependencies

**Upstream (what `spatial.targets` imports):**
- `models._` — the `models` subproject providing `Area`, `AreaFields`, `LatencyFields`, `Model`, `Fields`, `NodeModel`, `LinearModel`, `AreaEstimator` (`spatial/targets/HardwareTarget.scala:3`, `AreaModel.scala:7`, `SpatialModel.scala:4`).
- `argon._`, `argon.node._`, `forge.tags.stateful/rig` — IR symbols, op matching, effect tagging (`AreaModel.scala:3-5`, `NodeParams.scala:3-5`, `HardwareTarget.scala:4`).
- `spatial.lang._`, `spatial.node._` — pattern-match against `SRAMNew`, `RegFile`, `LineBufferNew`, `FixMul/Div/Mod`, `DRAMHostNew`, `DRAMAddress`, `DelayLine`, `RegAccumFMA/Op`, `Mux`, `OneHotMux`, `PriorityMux`, `SpatialBlackboxUse`, `VerilogBlackbox`, `SRAMRead`/`SRAMBankedRead`, `RegFileVectorRead`, `Switch`, `CounterNew`/`CounterChainNew`, `DenseTransfer` (`AreaModel.scala:9-10`, `NodeParams.scala:6-7`, `GenericLatencyModel.scala:4`).
- `spatial.metadata.control._`, `.memory._`, `.types._`, `.bounds._`, `.params._`, `.blackbox._`, `.retiming._` — consumes IR metadata (children/parent/schedule for `nStages`; `constDims`/`readers`/`writers`/`duplicates`/`getDuplicates`/`isRemoteMem`; `Bits`/`FixPtType`/`isBits`; `Expect`; `userInjectedDelay`, `bboxInfo`, `hasForcedLatency`, `forcedLatency`, `getRawSchedule`, `isOuterPipeControl`, `isSeqLoop`, `contention`).
- `spatial.util.spatialConfig` — `addRetimeRegisters`, `enableAsyncMem` gate a few model branches.
- `spatial.dse._` — `HardwareTarget` constructs `DSEAreaAnalyzer` and `LatencyAnalyzer`, creating a circular-looking dependency between `spatial.targets` and `spatial.dse` that resolves because the traversal classes are constructed, not defined here.

**Downstream (what uses `spatial.targets`):**
- `spatial.SpatialConfig` — holds `var target: HardwareTarget` (`SpatialConfig.scala:10`).
- `spatial.Spatial` — the driver (CLI parsing, init, codegen dispatch).
- `spatial.util.modeling` — helper accessors.
- `spatial.dse.{DSEAnalyzer, DSEAreaAnalyzer, LatencyAnalyzer, DSEThread, HyperMapperThread}` — consume `AreaModel`/`LatencyModel`.
- `spatial.traversal.MemoryAllocator` — reads `target.capacity` and `target.memoryResources`.
- `spatial.metadata.memory.BankingData` — `MemoryResource` type stored per duplicate.
- `spatial.codegen.{cppgen.CppCodegen, roguegen.RogueCodegen, tsthgen.TungstenHostCodegen, scalagen.ScalaGenDRAM, chiselgen.ChiselCodegen, chiselgen.ChiselGenCommon}` — each reads the target for name/burstSize/host branching.

## 6. Key algorithms

- **Memory resource packing (greedy, first-fit by cost)** — `MemoryAllocator.scala:56-104` uses `target.memoryResources` in order; hints at memoryResources list order meaning (URAM → BRAM → URAM overflow → LUTs). See Phase 2.
- **BRAM analytical area model** — `spatial/targets/xilinx/XilinxDevice.scala:62-77` computes RAM18/RAM36 column+row counts from width/depth via a table (`bramWordDepth`).
- **URAM analytical area model** — `spatial/targets/xilinx/XilinxDevice.scala:54-60` (cols = ceil(width/72), wordDepth=4096).
- **Distributed LUT-memory model** — `spatial/targets/xilinx/XilinxDevice.scala:79-83` (width/2 cols, depth buckets at 32 and 64).
- **Memory-area (ML-based)** — `AreaModel.scala:60-92` builds a `(dims, bitWidth, depth, B, N, alpha, P, hist)` feature vector and calls `mlModel.estimateMem("LUTs"|"FFs", …)`; RAM36 is computed analytically (`N * ceil(totalElems/(N*36000)) * (depth+1)`). Lines 87-89 note the ML estimator for RAM18/RAM36 "give wildly large numbers" so the analytical fallback is used.
- **Delay-line area heuristic** — `AreaModel.scala:197-205` returns registers-only; model for switching to BRAM for long delays is present in comments but unused.
- **Summarize / slice aggregation** — `xilinx/XilinxAreaModel.scala:11-107` rolls LUTs into SLICEL, memory LUTs into SLICEM, register surplus into regSlices (magic factor 1.9 and /8).
- **Fringe padding (Altera/Euresys only)** — `AlteraAreaModel.scala:12` and `EuresysAreaModel.scala:12` add `model("Fringe")()` to the design area; Xilinx/Generic do not.
- **Latency loop models** — `LatencyModel.scala:48-66` implements `parallelModel`, `streamingModel`, `metaPipeModel`, `sequentialModel`, `outerControlModel` dispatched by `isOuterPipeControl`/`isSeqLoop`.
- **DenseTransfer latency** — `GenericLatencyModel.scala:20-66` implements the tile-load/tile-store formulas with logistic overhead term parameterized on contention `c`, row count `r`, byte count `b`, parallelism `p`.
- **TileLoadModel (disabled)** — `generic/TileLoadModel.scala` — neural-net based tile-load predictor fully commented out; `evaluate` returns `0.0`. This is Phase 2 bait: all the Encog imports and training pipeline remain in comments.
- **NodeParams dispatch** — `NodeParams.scala:24-67` — mapping from IR op to CSV key (e.g., `RegAccumFMA` produces log2-corrected layer/drain parameters that the CSV model interpolates).

## 7. Invariants / IR state read or written

**Read (consumed):**
- Symbol type: `Bits(bt).nbits` via `nbits` (`NodeParams.scala:18`, `AreaModel.scala:38`), `FixPtType` sign.
- Memory metadata: `readers`, `writers`, `duplicates`, `getDuplicates`, `isRemoteMem`, `constDims`, `totalBanks`, `bankDepth`, `depth` (AreaModel.scala:60-154).
- Control metadata: `parent`, `ancestors`, `children`, `constPars` on `CounterChain`, `isOuterPipeControl`, `isSeqLoop`, `getRawSchedule`, `hasForcedLatency`, `forcedLatency`, `contention`.
- Retiming metadata: `userInjectedDelay` (NodeParams.scala:41), `addRetimeRegisters` config.
- Bounds metadata: `getBound`, `Expect` (`SpatialModel.scala:56`, `GenericLatencyModel.scala:42`).
- Blackbox metadata: `bbox.bodyLatency`, `bboxInfo.latency` (`NodeParams.scala:47-49`).

**Written:** This subsystem is pure *read* w.r.t. the IR during estimation. It does not mutate IR metadata. (Memory-resource assignment is written by `MemoryAllocator`, downstream of targets.)

**Invariants relied on:**
- `sym.parent` chains terminate before reaching `mem.parent` in `accessUnrollCount` (`AreaModel.scala:41-58`) — the try/catch on line 61 suggests this is not fully guaranteed.
- The CSV `FILE_NAME = <target.name>_Area.csv` / `<target.name>_Latency.csv` must exist under `SPATIAL_HOME/models/` or on the resource classpath (`SpatialModel.scala:18, 74-85`).
- `target.AFIELDS` must be a superset of the columns in the corresponding CSV (`SpatialModel.scala:90-95` warns but proceeds).

## 8. Notable complexities or surprises

- **Massive boilerplate duplication across vendors.** `XilinxDevice`, `AlteraDevice`, `EuresysDevice`, `GenericDevice` are 90%+ byte-identical (same AFIELDS, same BRAM/URAM/distributed memory models, same nested `URAM_RESOURCE`/`BRAM_RESOURCE` classes). `XilinxAreaModel.scala`, `AlteraAreaModel.scala`, `EuresysAreaModel.scala`, `GenericAreaModel.scala` are near-copies — only `+ model("Fringe")()` and the `if (false)`/`if (config.enInfo)` gate differ. This is a prime candidate for Phase 2 consolidation into a single parameterized device base.
- **ASIC borrows Zynq's latency model.** `generic/ASIC.scala:12` instantiates `new LatencyModel(xilinx.Zynq)` — the ASIC target has no Latency CSV of its own and silently pulls Zynq numbers.
- **Altera/DE1/Arria10 have empty capacities.** `altera/DE1.scala:11`, `altera/Arria10.scala:11`, `generic/ASIC.scala:26` all have `capacity: Area = Area(/* Fill me in */)` — DSE against these targets will treat every Area key as zero, which breaks memory-allocation packing.
- **VCS has pseudo-infinite resources.** `generic/VCS.scala:14-21` — `9999999` across the board to avoid any area-based rejection during simulation.
- **`AreaModel.areaOfMem` disables its own RAM18/RAM36 ML estimator.** Lines 87-90 in `AreaModel.scala` contain commented-out `mlModel.estimateMem("RAMB18"|"RAMB36", …)` calls with a note that "models give wildly large numbers" — RAM36 is computed analytically, RAM18 is forced to 0.
- **`accessUnrollCount` has a noted bug.** `AreaModel.scala:51-52` — the `OpMemReduce` case multiplies by `cchainMap.constPars.product + cchainRed.constPars.product`, with a TODO "This is definitely wrong, need to check stage of access."
- **`delayLine` area is register-only despite doc.** `AreaModel.scala:197-205` — the doc string says "Models delays as registers for short delays, BRAM for long ones" but the implementation only emits `Area("Regs" -> length * par)`; the BRAM branch is commented out.
- **`TileLoadModel` is fully commented.** `generic/TileLoadModel.scala:16-109` — the entire Encog neural-network training/inference body is commented out and `evaluate(...)` returns 0.0 literally. Instantiated as `lazy val memModel = new TileLoadModel` at `generic/GenericLatencyModel.scala:13` and called at line 30 but always returns 0.
- **Memory-resource list ordering is semantic.** `MemoryAllocator.scala:102` — the *last* element of `memoryResources` is used as the catch-all; for all FPGAs, that last element is `LUTs_RESOURCE`. This is load-bearing but implicit.
- **`HardwareTarget` depends on `spatial.dse._`.** `HardwareTarget.scala:5` imports `spatial.dse._` purely to construct `DSEAreaAnalyzer` and `LatencyAnalyzer`; the target package is otherwise self-contained. This is the only circularity in the dependency graph.
- **`KCU1500` quietly changes host codegen.** Overriding `host = "rogue"` at `xilinx/KCU1500.scala:7` diverts the whole host-codegen dispatch in `Spatial.scala:248` — easy to miss.
- **DSP_CUTOFF = 16 for all FPGAs.** Every FPGA target hard-codes `DSP_CUTOFF = 16` with a `TODO[4]: Not sure if this is right` comment — this value gates when `FixMul/Div/Mod` go to DSPs vs LUTs.

## 9. Open questions

- What is the *intended* semantic difference between the four Xilinx/Altera/Euresys/Generic device bases, given their near-identical implementations? Is Euresys just a vanity branding of a Xilinx FPGA?
- Should `AreaModel.accessUnrollCount`'s `OpMemReduce` branch be fixed, and does anything in the calling `areaOfMem` path depend on its current (TODO'd) output? (`AreaModel.scala:51-52`)
- What is the impact of `RAM18 = 0` in `AreaModel.areaOfMem` on XilinxAreaModel's BRAM rollup, which does `RAM18/2 + RAM36`? (`AreaModel.scala:90`, `XilinxAreaModel.scala:31`)
- Is the `TileLoadModel` intentional dead code (experimental branch left over) or a regression? (`generic/TileLoadModel.scala`) It is instantiated and called but always yields zero.
- What are the real `capacity` values for Altera `DE1`, `Arria10`, and `ASIC`? Are DSE runs against those targets meaningful today?
- How do the `AFIELDS` relate to `RESOURCE_FIELDS` at the model-plumbing level — which name is authoritative when both are declared? See `HardwareTarget.scala:14,22` vs `SpatialModel.scala:17-19`.
- `baseCycles = 43000` is fixed for all targets (`HardwareTarget.scala:18`). Where is it consumed, and does it represent startup cycles on a specific board?

## 10. Suggested spec sections

Content from this coverage note should feed the spec tree under `10 - Spec/`:

- `10 - Spec/Estimation/` — new subsection **Hardware target abstraction** describing `HardwareTarget` trait, the capacity/AFIELDS/memoryResources contract, and the target-selection flow from CLI (`--fpga`) through `spatialConfig.target` to model init.
- `10 - Spec/Estimation/Area model.md` — `AreaModel` API (`areaOf`, `areaOfMem`, `areaOfReg`), the CSV-backed `SpatialModel.model(sym)` dispatch, `NodeParams.nodeParams` op-to-key mapping, and the per-vendor `summarize` rollup (LUTs→slices, RAM18/36→BRAM, regSlices).
- `10 - Spec/Estimation/Latency model.md` — `LatencyModel` API (`latencyOfNode`, `parallelModel`/`metaPipeModel`/`sequentialModel`/`streamingModel`/`outerControlModel`), retime-register predicate, `GenericLatencyModel` tile-transfer overlays.
- `10 - Spec/Memory system/Memory resources and allocation.md` — `MemoryResource` trait, per-vendor `URAM_RESOURCE`/`BRAM_RESOURCE`/`URAM_RESOURCE_OVERFLOW`/`LUTs_RESOURCE`/`SRAM_RESOURCE`, and the ordering semantics relied on by `MemoryAllocator` (deep-dive covered by banking subsystem, but the resource taxonomy lives here).
- `10 - Spec/Targets/Supported hardware targets.md` — one-pager per target family (Xilinx, Altera, Euresys, Generic/ASIC/VCS, Plasticine) listing name, burstSize, capacity, resource families, host codegen, and clockRate. Flag stubs and incomplete values.
- `10 - Spec/Pipeline/` — cross-reference entry showing where `HardwareTarget` is resolved during compilation and which downstream passes consume it.

Phase 2 deep-dives to prioritize:
1. AreaModel memory-area formula and its interaction with banking analysis.
2. GenericLatencyModel's DenseTransfer formula (the only non-trivial non-CSV latency override).
3. The Altera/Euresys/Generic-vs-Xilinx device-class duplication — identify the real deltas.
4. TileLoadModel status — live or dead?
5. MemoryAllocator ordering invariants over `memoryResources` list.
