---
type: coverage
subsystem: Codegen A (FPGA + host)
paths:
  - "src/spatial/codegen/chiselgen/"
  - "src/spatial/codegen/cppgen/"
  - "src/spatial/codegen/dotgen/"
  - "src/spatial/codegen/naming/"
  - "src/spatial/codegen/resourcegen/"
  - "src/spatial/codegen/treegen/"
file_count: 38
date: 2026-04-21
verified:
  - 2026-04-21
---

## 1. Purpose

These six subdirectories hold the "non-Plasticine, non-sim" code generators of the Spatial compiler: the output stage that turns a fully-lowered, unrolled, retimed, banked Spatial IR into (1) Chisel RTL that runs on an FPGA (`chiselgen`), (2) a matching C++ host program for a CPU-plus-FPGA target such as AWS F1, Zynq, ZCU, or VCS simulation (`cppgen`), (3) visualization artefacts consumed by humans during debugging — `dotgen` for Graphviz of the IR, `treegen` for a collapsible HTML "controller tree", and `HtmlIRGenSpatial` (in `dotgen/`) for a linked per-symbol IR dump — and (4) resource/area reports for DSE feedback (`resourcegen`). The `naming/` directory is a tiny shared mixin — `NamedCodegen` — that every FPGA-side generator inherits to give memories, controllers, and IR ops the human-readable per-sym names shown in all of the above artefacts. All six sit in the final "Code generation" phase of the Spatial compiler pipeline (`spatial/Spatial.scala:241-252`), strictly after retiming, banking, unrolling, and buffer-depth recomputation have set the metadata these generators read.

## 2. File inventory

### chiselgen/ (17 files)

| path | one-line purpose |
| --- | --- |
| `chiselgen/ChiselGen.scala` | Top-level `case class ChiselGen(IR: State)` that mixes every `ChiselGen*` trait into one concrete pass (`chiselgen/ChiselGen.scala:5-17`). |
| `chiselgen/ChiselCodegen.scala` | Base trait: extends `NamedCodegen with FileDependencies with AccelTraversal`, sets `lang="chisel"`/`ext="scala"`/`backend="accel"`, and defines `remap`, `port`, `arg`, `param`, `ledgerized`, the chunked `gen(block)`, `emitPreMain`/`emitPostMain`/`emitEntry` which emit `AccelWrapper.scala`, `Instantiator.scala`, `ArgInterface.scala`, and `AccelUnit.scala` (`chiselgen/ChiselCodegen.scala:17-492`). |
| `chiselgen/ChiselGenCommon.scala` | Mixin with all per-controller helper state: `loadStreams`/`storeStreams`/`gatherStreams`/`scatterStreams` maps, `argIns`/`argOuts`/`argIOs`, `earlyExits`, `instrumentCounters`, `activesMap`, plus `enterCtrl`/`exitCtrl`, `getInputs`/`groupInputs`, `appendSuffix`, `DL`/`DLo` retiming helpers, `getForwardPressure`/`getBackPressure`, `connectDRAMStreams`, `createCChainObject`/`createStreamCChainObject`. |
| `chiselgen/ChiselGenController.scala` | Handles `AccelScope`, `UnitPipe`, `UnrolledForeach`, `UnrolledReduce`, `Switch`/`SwitchCase`, `StateMachine`, `IfThenElse`, `ParallelPipe`; emits `sm_<ctrl>.scala` per controller via `writeKernelClass` and wires up iter/valid/chain passing. |
| `chiselgen/ChiselGenCounter.scala` | Maps `CounterNew`/`CounterChainNew`/`ForeverNew` to `CtrObject`/`CChainObject` instantiations. |
| `chiselgen/ChiselGenMem.scala` | All memory allocations (`SRAMNew`, `RegNew`, `FIFONew`, `LIFONew`, `RegFileNew`, `LineBufferNew`, `LUTNew`, `MergeBufferNew`, `FIFORegNew`) and their banked reads/writes. |
| `chiselgen/ChiselGenMath.scala` | Every `Fix*`/`Flt*` arithmetic op translated into `Math.mul`/`Math.div`/`Math.fma`/`Math.sqrt`/etc calls with per-node latency lookup. |
| `chiselgen/ChiselGenDRAM.scala` | `DRAMHostNew`, `DRAMAccelNew`, `DRAMAlloc`, `DRAMIsAlloc`, `DRAMDealloc`; calls `connectDRAMStreams` to wire load/store/gather/scatter streams into the Fringe AXI interface. |
| `chiselgen/ChiselGenInterface.scala` | `ArgInNew`/`HostIONew`/`ArgOutNew`/`GetReg`/`SetReg` — bridges user registers to `accelUnit.io.argIns`/`argOuts`. |
| `chiselgen/ChiselGenStream.scala` | `StreamInNew`/`StreamOutNew` on `AxiStream64/256/512Bus`. |
| `chiselgen/ChiselGenBlackbox.scala` | Verilog and Spatial blackboxes — emits `bb_<sym>.scala` wrapper that instantiates user Verilog with the declared param map. |
| `chiselgen/ChiselGenDebug.scala` | Stubs out host-only text/print ops to empty strings, wires `BreakpointIf`/`AssertIf`/`ExitIf` into `Ledger.tieBreakpoint`. |
| `chiselgen/ChiselGenDelay.scala` | `DelayLine` → `getRetimed(...)` of configured depth, updates `maxretime`. |
| `chiselgen/ChiselGenStruct.scala` | `SimpleStruct`/`SimpleStreamStruct`/`FieldApply`/`FieldDeq` — packs struct fields into a single `UInt` with `ConvAndCat`. |
| `chiselgen/ChiselGenVec.scala` | `VecAlloc`, `VecApply`, `VecSlice`, `VecConcat`. |
| `chiselgen/AppProperties.scala` | Sealed trait enumeration — 23 objects flagging features the generated app uses (`HasLineBuffer`, `HasNBufSRAM`, `HasGather`, `HasScatter`, `HasFSM`, …) for selective template emission. |
| `chiselgen/RemapSignal.scala` | Sealed trait enumeration — 29 objects naming controller signals (`En`, `Done`, `DatapathEn`, `IIDone`, `Mask`, `Resetter`, `Flow`, `II`, `SM`, `CtrTrivial`, `RstEn`, `CtrEn`, `NowValid`, `Inhibitor`, `Wren`, `Chain`, `Blank`, `DataOptions`, `ValidOptions`, `ReadyOptions`, `EnOptions`, `RVec`, `WVec`, `Latency`, …) used as typed keys rather than raw strings. |

### cppgen/ (10 files)

| path | one-line purpose |
| --- | --- |
| `cppgen/CppGen.scala` | Top-level `CppGen(IR: State)` mixing every `CppGen*` trait. |
| `cppgen/CppCodegen.scala` | Base trait: `lang="cpp"`/`ext="cpp"`/entry `TopHost.cpp`; `copyDependencies` forks `synth/{aws,zynq,zcu,zedboard,vcs,cxp,de1,arria10,asic}.sw-resources` and `.hw-resources` dirs + per-target Makefile based on `spatialConfig.target`. |
| `cppgen/CppFileGen.scala` | `backend="cpp"`; emits boilerplate for `cpptypes.hpp`, `functions.hpp`, `functions.cpp`, `structs.hpp`, `ArgAPI.hpp`, and the `TopHost.cpp` `main()` skeleton. |
| `cppgen/CppGenCommon.scala` | Shared state: `argIns`/`argOuts`/`argIOs`/`drams` ArrayBuffers, `controllerStack`, `instrumentCounters`, `asIntType`, `toTrueFix`/`toApproxFix` helpers for fixed-point marshalling. |
| `cppgen/CppGenAccel.scala` | `AccelScope` — emits `c1->setNumArgIns`/`setNumArgOuts`/`run()`, instrumentation readout, and early-exit breakpoint dumping. |
| `cppgen/CppGenInterface.scala` | Host-side `ArgInNew`/`HostIONew`/`ArgOutNew`/`DRAMHostNew`/`SetReg`/`GetReg` — calls `c1->setArg`/`c1->getArg`/`c1->malloc` against the Fringe host driver. |
| `cppgen/CppGenArray.scala` | Host-side array, vec, and struct generation (433 lines — largest cpp file). |
| `cppgen/CppGenMath.scala` | Host-side arithmetic for argument precomputation — `pow`, `ceil`, `floor`, fix/float bit manipulation. |
| `cppgen/CppGenFileIO.scala` | Host-side `LoadDRAMWithASCIIText`, `OpenBinaryFile`, `ReadBinaryFile`, `WriteBinaryFile`. |
| `cppgen/CppGenDebug.scala` | Host `FixToText`/`FltToText`/`CharArrayToText`/etc. for `printf`-style debug output. |

### dotgen/ (7 files)

| path | one-line purpose |
| --- | --- |
| `dotgen/DotCodegen.scala` | Base trait: `lang="info"`/`ext="dot"`; Scope/Edge/Node bookkeeping and `postprocess` shells out to `dot -Tsvg` to turn each `.dot` into an HTML SVG. |
| `dotgen/DotFlatCodegen.scala` | One flat `Main.dot` using Graphviz `subgraph cluster_<lhs>` to nest controllers. |
| `dotgen/DotHierarchicalCodegen.scala` | One `.dot` per controller — `ancestors`/`ancestryBetween` find LCAs so cross-scope edges get extern-node stubs in every intermediate `Scope`. |
| `dotgen/DotGenSpatial.scala` | Spatial-specific `inputs`/`nodeAttr`/`label`/`inputGroups` overrides — colors SRAM green, Reg chartreuse, DRAM blueviolet, FIFO/Stream gold, Lock crimson. |
| `dotgen/DotHtmlCodegen.scala` | Standalone object that post-processes Graphviz-emitted HTML to inject tooltip attributes. |
| `dotgen/HtmlIRGen.scala` | `trait HtmlIRCodegen` — generic per-sym HTML dump with `<h3>$sym</h3>` headers and a metadata table. |
| `dotgen/HtmlIRGenSpatial.scala` | `case class HtmlIRGenSpatial(IR, filename="IR")` — Spatial-specific `quote` that hyperlinks symbol names; emits banking/duplicate/memory metadata. |

### naming/ (1 file)

| path | one-line purpose |
| --- | --- |
| `naming/NamedCodegen.scala` | Sole mixin — overrides `named(s, id)` so controllers become `<sym>_inr_Foreach<name>`, SRAMs become `<sym>_<memname>sram`, counters `<sym>_ctr`, etc. |

### resourcegen/ (2 files)

| path | one-line purpose |
| --- | --- |
| `resourcegen/ResourceReporter.scala` | Area estimator — walks the IR recursively inside `AccelScope`, calls `AreaEstimator.estimateMem`/`estimateArithmetic` per mem and per `Fix*Mul/Div/Add/Sub/FMA` node to sum `ResourceArea(LUT, Reg, BRAM, DSP)`. |
| `resourcegen/ResourceCountReporter.scala` | Simpler counter — tallies mems into `bram`/`reg` buckets and counts fixed-point ops; emits one JSON dictionary per mem-type to `reports/Main.json`. |

### treegen/ (1 file)

| path | one-line purpose |
| --- | --- |
| `treegen/TreeGen.scala` | `case class TreeGen(IR, filename="controller_tree", IRFile="IR")` — emits collapsible HTML (jQuery Mobile) with nested `<TD>` cells per controller showing schedule/II/latency, stream connections, NBuf memories color-coded from a 23-color palette. |

## 3. Key types / traits / objects

- **`trait NamedCodegen extends argon.codegen.Codegen`** (`naming/NamedCodegen.scala:13`) — the single Spatial-specific mixin that decorates Argon's generic `named(s, id)` with Spatial IR cases. Key method: `named(s: Sym[_], id: Int): String`. Callers: `ChiselCodegen`, `ResourceReporter`, `ResourceCountReporter`.
- **`trait ChiselCodegen extends NamedCodegen with FileDependencies with AccelTraversal`** (`chiselgen/ChiselCodegen.scala:17`) — the FPGA RTL codegen base. Key methods: `emitHeader` (fringe imports), `emitPreMain`/`emitPostMain`/`emitEntry` (generates `AccelWrapper.scala`, `Instantiator.scala`, `AccelUnit.scala`, `ArgInterface.scala`), `remap(tp)`/`port(tp)`/`arg(tp)`/`param(node)` (four separate type-remappers for different Chisel contexts), `ledgerized(node)`.
- **`trait ChiselGenCommon extends ChiselCodegen`** (`chiselgen/ChiselGenCommon.scala:17`) — accumulates all the per-controller state that every `ChiselGen*` trait needs.
- **`case class ChiselGen(IR: State)`** (`chiselgen/ChiselGen.scala:5`) — concrete pass mixing every `ChiselGen*` trait; instantiated at `spatial/Spatial.scala:147` and enabled when `spatialConfig.enableSynth`.
- **`trait CppCodegen extends FileDependencies with AccelTraversal`** (`cppgen/CppCodegen.scala:9`) — host-side base; `copyDependencies(out)` is the seam where it forks one of nine per-target resource trees.
- **`trait CppGenCommon extends CppCodegen`** (`cppgen/CppGenCommon.scala:11`) — mirror of `ChiselGenCommon` but simpler.
- **`case class CppGen(IR: State)`** (`cppgen/CppGen.scala:5`) — concrete pass, enabled when `enableSynth && target.host == "cpp"`.
- **`trait DotCodegen extends argon.codegen.Codegen`** (`dotgen/DotCodegen.scala:10`) — generic graphviz emitter.
- **`trait DotFlatCodegen`** / **`trait DotHierarchicalCodegen`** — two layout strategies; hierarchical uses LCA ancestry to project cross-scope edges through all intermediate scopes.
- **`trait DotGenSpatial extends DotCodegen`** — Spatial type overrides; composed with the two above to give `case class DotFlatGenSpatial(IR)` and `case class DotHierarchicalGenSpatial(IR)`.
- **`trait HtmlIRCodegen extends argon.codegen.Codegen`** / **`case class HtmlIRGenSpatial(IR, filename)`** — generic + Spatial-specialized HTML dumps of the IR, cross-linked to the graphviz SVGs.
- **`case class TreeGen(IR, filename, IRFile) extends AccelTraversal with argon.codegen.Codegen`** — note: `TreeGen` does *not* extend `NamedCodegen`; it is purely visual and builds its own controller tree from `isControl`/`isInnerControl`/`isOuterControl`/`children`/`cchains`/`II`/`bodyLatency` metadata.
- **`case class ResourceArea(LUT, Reg, BRAM, DSP)`** — simple additive record with `.and(other)` combinator.
- **`case class ResourceReporter(IR: State, areamodel: AreaEstimator) extends NamedCodegen with FileDependencies with AccelTraversal`** — area report; enabled by `spatialConfig.reportArea`.
- **`case class ResourceCountReporter(IR: State) extends NamedCodegen with FileDependencies with AccelTraversal`** — count-only report.
- **`sealed trait AppProperties`** — union of 23 `case object`s (`HasLineBuffer`, `HasNBufSRAM`, `HasGather`, `HasScatter`, `HasFSM`, `HasFloats`, `HasBreakpoint`, …); `ChiselGenCommon.appPropertyStats` accumulates into a `Set[AppProperties]`.
- **`sealed trait RemapSignal`** — union of 29 controller-signal objects (`En`, `Done`, `BaseEn`, `Mask`, `DatapathEn`, `IIDone`, `Flow`, `Inhibit`, `CtrTrivial`, `RstEn`, `CtrEn`, `NowValid`, `Inhibitor`, `Wren`, `Chain`, `Blank`, `DataOptions`, `ValidOptions`, `ReadyOptions`, `EnOptions`, `RVec`, `WVec`, `Latency`, …); used as typed keys rather than strings.

## 4. Entry points

The integration seam is narrow and all invoked from `spatial/Spatial.scala:146-252`:

- `ChiselGen(state)` — `spatial/Spatial.scala:147`, gated by `spatialConfig.enableSynth`.
- `CppGen(state)` — `spatial/Spatial.scala:149`, gated by `enableSynth && target.host == "cpp"`.
- `TreeGen(state)` — `spatial/Spatial.scala:151`, always run at line 241, and also wrapped by `createDump(n)` at `Spatial.scala:136` which runs it with `HtmlIRGenSpatial` at many intermediate points.
- `HtmlIRGenSpatial(state)` — `spatial/Spatial.scala:152`, always run at line 242.
- `DotFlatGenSpatial(state)` / `DotHierarchicalGenSpatial(state)` — `spatial/Spatial.scala:158-159`, gated by `spatialConfig.enableFlatDot` and `spatialConfig.enableDot`.
- `ResourceReporter(state, mlModel)` — gated by `spatialConfig.reportArea`.
- `ResourceCountReporter(state)` — gated by `spatialConfig.countResources`.

All seven are instances of `argon.codegen.Codegen`, which itself extends `argon.passes.Traversal`.

## 5. Dependencies

**Upstream (reads):**
- `argon.codegen.Codegen` / `argon.codegen.FileDependencies` / `argon.passes.Traversal`.
- `spatial.traversal.AccelTraversal` — provides `inAccel`/`inBBox`/`outsideAccel`/`inHw` scoping.
- `spatial.metadata.access`, `spatial.metadata.control`, `spatial.metadata.memory`, `spatial.metadata.retiming`, `spatial.metadata.blackbox`, `spatial.metadata.types`, `spatial.metadata.bounds`, `spatial.metadata.math`, `spatial.metadata.debug`, `spatial.metadata.CLIArgs`.
- `spatial.util.spatialConfig` — target selection, `enableModular`, `enableInstrumentation`, `enableRetiming`, `enableAsyncMem`, `codeWindow`, `dualReadPort`.
- `spatial.targets._` — the 10 targets enumerated in `CppCodegen.copyDependencies`.
- `models.AreaEstimator` — ML area model consulted by `ResourceReporter`.
- `emul.Bool`, `emul.FixedPoint`, `utils.io.files`, `utils.math._`, `utils.escapeString`.

**Downstream (consumers):**
- These are leaf passes — no other compiler pass reads their outputs. Their outputs are consumed by humans (HTML/SVG/JSON reports, text area estimates) and by external build tooling.

## 6. Key algorithms

- **Controller-per-module kernel emission** — `writeKernelClass(lhs, ens, func*)` in `chiselgen/ChiselGenController.scala`, one Scala file `sm_<lhs>.scala` per Spatial controller, with iter/valid chain passing for outer pipelines.
- **Code chunking ("javaStyleChunk")** — Chisel hits JVM method size limits; the chunker at `argon/src/argon/codegen/Codegen.scala:107-199` splits a block into `CODE_WINDOW`-weighted chunks.
- **Live-value detection across chunks** — `isLive` in `ChiselCodegen.gen`: a sym is "live" if `b.result == s` or any later stm in the block needs it.
- **Stream-controller cchain copies** — `markCChainObjects(b)` walks the block and registers each child as owner of a copy suffix `_copy<c>`.
- **Backpressure composition** — `getForwardPressure`/`getBackPressure` walks `getReadStreams`/`getWriteStreams` and combines FIFO `~empty`/`~full`, merge-buffer status, stream-in `valid`, stream-out `ready`, priority dequeue groups, and per-blackbox `getForwardPressures`.
- **Retimed delay insertion** — `DL(name, latency)` and `DLo` emit either `.DS(lat, rr, bp & fp)` for bits or `getRetimed(x, lat, bp & fp)` for words.
- **Memory banking → Chisel parameter object** — `ChiselGenMem.splitAndCreate` breaks long `List[MemParams]` payloads into `create_<port>()` helper methods.
- **Resource estimation** — `estimateArea(block)` recurses through controllers; for each `MemAlloc` builds a histogram of `residualGenerators` × `port.broadcast` filtered to non-broadcast, grouped by "muxwidth", then calls `areamodel.estimateMem`.
- **Resource histogram for tree view** — `TreeGen.emitFooter` builds the same R/W-lane-muxwidth histogram per mem and dumps it as an HTML 3-column grid.
- **LCA edge projection (hierarchical dot)** — `DotHierarchicalCodegen.addEdge`: when emitting an edge whose `from` escapes the current scope, it calls `ancestryBetween(from, to)` and registers the edge in every scope between the shared LCA and the two endpoints.
- **Per-target file-dep fan-out** — `CppCodegen.copyDependencies` pattern-matches `spatialConfig.target` and registers one `DirDep`/`FileDep` triple per target.

## 7. Invariants / IR state read or written

These generators are pure readers of prior metadata — they do not mutate IR. What they rely on:
- **Retiming**: every sym needs `lhs.fullDelay` for `DL(...)` wrapping; `lhs.II`/`lhs.bodyLatency`/`lhs.compilerII` for scheduling text.
- **Banking**: every mem needs `mem.instance.depth`/`Bs`/`alphas`/`nBanks`/`Ps`; readers/writers need `.residualGenerators` and `.port.broadcast`.
- **Control**: `isInnerControl`/`isOuterControl`/`isBranch`/`isSwitch`/`isBlackboxImpl`/`isOuterStreamLoop`.
- **Access metadata**: `lhs.segmentMapping` for segmentation, `lhs.parent`/`Ctrl.Host` for host-vs-accel membership.
- **Memory types / classifications**: `isMem`, `isSRAM`, `isRegFile`, `isReg`, `isLineBuffer`, `isFIFO`, `isLIFO`, `isFIFOReg`, `isLUT`, `isDRAM`, `isDRAMAccel`, `isStreamIn`, `isStreamOut`, `isMemPrimitive`, `isNBuffered`, `isArgIn`, `isHostIO`, `isDeqInterface`, `isDualPortedRead`, `isBroadcastAddr`, `isBound`, `isTileStore`, `isTileTransfer`, `isCtrlBlackbox`, `isBlackboxUse`.
- **Blackbox**: `lhs.bboxInfo` with `BlackboxConfig(file, moduleName, _, _, params)`.
- **Register optimization**: `lhs.optimizedRegType` drives the `FixFMAAccumBundle`/`FixOpAccumBundle` vs `StandardInterface` port choice.
- **Config flags written (side effects into state):**
  - `config.enGen` is toggled by `AccelTraversal.inAccel`/`inBox`/`outsideAccel` based on `backend`.
  - `spatialConfig.enGen` is forced true by `ResourceReporter`/`ResourceCountReporter` inside `AccelScope` so `gen` actually emits.

## 8. Notable complexities or surprises

- **ChiselGen is large (~3.8k LOC) and heterogeneous; the others are small.** The deep-dive effort in Phase 2 should be heavily weighted toward ChiselGen.
- **Four separate "type-to-Chisel-string" functions in `ChiselCodegen`**: `remap(tp)`, `port(tp, node)`, `arg(tp, node)`, `param(node)`. Each handles different edge cases. Easy to break subtly when adding a new mem type.
- **javaStyleChunk wraps every block into synthetic Scala `object`s.** Debugging generated code requires knowing that `x123` in a stack trace might live inside `Block7Chunker3.gen()`'s returned map rather than as a `val` in scope.
- **`_copy<c>` suffix for stream-controller counter chain instances** is a pervasive non-obvious rewrite.
- **Mixed assignment-by-side-effect state.** `ChiselGenCommon` holds ~15 mutable maps/buffers on the instance.
- **No per-target ChiselGen variant.** All per-target RTL customization lives in the `synth/<target>.hw-resources` directory templates.
- **`enableModular` is a global code-shape toggle.** When true, kernels are emitted with explicit `io.sigsIn.cchainOutputs.head` access and `ModuleParams.addParams`. When false, the Chisel is generated differently (inlined rather than modular).
- **`createDump(n)` runs `TreeGen` + `HtmlIRGen` at six different IR checkpoints.** Both generators therefore must work on partially-transformed IR.
- **`HtmlIRGenSpatial.gen` writes to `Mem.$ext` in addition to the main entry file.**
- **`DotHtmlCodegen` is a standalone `object` that is never referenced from the codegen pipeline** — may be dead code.
- **TreeGen generates mobile-web HTML** using `jQuery Mobile 1.4.5` — an unusual, possibly legacy choice.
- **`ChiselGenDebug` stubs out every text/print op as empty strings on accel.** Silent — a user-written `println` inside `Accel` will compile but produce nothing.

## 9. Open questions

1. What exactly does `enableModular` toggle and why are both code paths maintained?
2. Why does `TreeGen` not extend `NamedCodegen` when it prints the same IR symbols as the others?
3. How do the per-target `synth/<target>.sw-resources` and `synth/<target>.hw-resources` dirs relate to the resources lists?
4. `DotHtmlCodegen` appears unused — dead code, or invoked via reflection / external sbt task?
5. When `HtmlIRGenSpatial` runs on pre-banked IR from `createDump("PreEarlyUnroll")` etc., how does it safely access `Duplicates`/`Memory` metadata that doesn't exist yet?
6. What is the relationship between `ChiselGenCommon.instrumentCounters` and `CppGenCommon.instrumentCounters`? Are the indices they emit actually kept consistent between the two passes?
7. `ResourceReporter` depends on `models.AreaEstimator` — what is that model trained on, and is it kept in sync with the Chisel RTL actually emitted?
8. The JVM method-size workaround (`javaStyleChunk`) is called out as 2-level-only; has an app ever exceeded 2 levels?
9. What's the intended replacement of the 23-object `AppProperties` enum? Are the other 22 flags live?
10. `RemapSignal` is a sealed trait with 27 objects but I could not find its actual usage sites — is it shipped but not yet wired in?

## 10. Suggested spec sections

- **`10 - Spec/Codegen/ChiselGen/`** — the majority of findings. Sub-files:
  - `overview.md` — the trait-mixin pattern, `ChiselGen` as composite, chunker, per-controller module emission.
  - `types-and-ports.md` — `remap`/`port`/`arg`/`param` four-way split.
  - `memories.md` — `ChiselGenMem` per-mem-class emission, banking plumbing, `ModuleParams.addParams`.
  - `control.md` — `ChiselGenController` `writeKernelClass`, iter/valid chain passing, stream-copy `_copy<c>` mechanism.
  - `streams-and-dram.md` — `ChiselGenDRAM` + `ChiselGenStream` wiring to Fringe's `memStreams` and `axiStreams`.
  - `blackbox.md` — `ChiselGenBlackbox` Verilog wrapping.
  - `math.md` — `ChiselGenMath` latency-aware dispatch.
  - `app-properties-and-signals.md` — the `AppProperties` / `RemapSignal` enums.
- **`10 - Spec/Codegen/CppGen/`** — host-side. Sub-files:
  - `overview.md` — trait-mixin pattern mirroring ChiselGen.
  - `targets.md` — the 10-way fan-out in `copyDependencies`.
  - `interface.md` — `c1->setArg`/`c1->getArg`/`c1->malloc` marshalling.
  - `accel-driver.md` — `CppGenAccel` flow.
  - `fileio.md` — `CppGenFileIO` for binary/ASCII DRAM preloading.
- **`10 - Spec/Codegen/Visualization/`** — `dotgen/` + `treegen/`:
  - `controller-tree.md` — `TreeGen` schedule/II/latency view, NBuf coloring.
  - `ir-html.md` — `HtmlIRGenSpatial`, cross-linking to the memory-specific `Mem.html`.
  - `graphviz.md` — `DotFlat`/`DotHierarchical` layouts, LCA edge projection.
- **`10 - Spec/Codegen/Naming/`** — the single `NamedCodegen` mixin, its case grammar, and which generators use it.
- **`10 - Spec/Codegen/Resource/`** — `resourcegen/`:
  - `area-report.md` — `ResourceReporter` / `AreaEstimator` / `ResourceArea`, banking histogram derivation.
  - `count-report.md` — JSON counting variant.
- **`10 - Spec/Compilation pipeline/phase4-codegen.md`** — summarizes the final-phase pass ordering and which config flags activate which generator.
- **`10 - Spec/Argon framework/codegen-base.md`** — upstream interface the Spatial generators inherit.
