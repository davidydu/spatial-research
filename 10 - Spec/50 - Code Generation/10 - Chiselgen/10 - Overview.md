---
type: spec
concept: chiselgen-overview
source_files:
  - "spatial/src/spatial/codegen/chiselgen/ChiselGen.scala:1-18"
  - "spatial/src/spatial/codegen/chiselgen/ChiselCodegen.scala:17-302"
  - "spatial/src/spatial/codegen/chiselgen/ChiselCodegen.scala:482-489"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenCommon.scala:17-47"
  - "spatial/src/spatial/codegen/chiselgen/AppProperties.scala:1-27"
  - "spatial/src/spatial/codegen/chiselgen/RemapSignal.scala:1-34"
  - "spatial/argon/src/argon/codegen/Codegen.scala:10-202"
  - "spatial/src/spatial/codegen/naming/NamedCodegen.scala:13-107"
  - "spatial/src/spatial/Spatial.scala:136-147"
  - "spatial/src/spatial/Spatial.scala:241-252"
source_notes:
  - "[[chiselgen]]"
hls_status: chisel-specific
depends_on:
  - "[[00 - Codegen Index]]"
  - "[[argon-framework]]"
status: draft
---

# Chiselgen — Overview

## Summary

Chiselgen is the Spatial compiler's FPGA RTL backend. It turns a fully-lowered, banked, retimed, unrolled Spatial IR into a tree of Chisel Scala files rooted at four entry files (`AccelWrapper.scala`, `Instantiator.scala`, `ArgInterface.scala`, `AccelUnit.scala`), plus one `sm_<lhs>.scala` per controller, one `m_<lhs>.scala` per memory allocation, one `bb_<lhs>.scala` per blackbox, and a terminal `Main.scala` / `Controllers.scala` / `Instrument.scala` / `ArgAPI.scala`. The generated code targets the `fringe` Chisel template library and is compiled separately into a bitstream by downstream tooling. Chiselgen is invoked once, as a single terminal pass, when `spatialConfig.enableSynth` is set.

## Syntax / API

Not a user-facing concept. The user surface is instead `spatialConfig.enableSynth` + the per-target settings in `spatialConfig.target`.

## Semantics

Chiselgen is a pure reader of IR. It mutates no IR metadata (except for the cosmetic `setSrcType` in a few `Math.fix2fix`/`fix2flt` emitters in `ChiselGenMath`). It consumes:

- Retiming metadata (`lhs.fullDelay`, `lhs.II`, `lhs.bodyLatency`, `lhs.compilerII`) to emit `getRetimed` / `.DS` wrapping and per-controller latency arguments.
- Banking metadata (`mem.instance.{depth, nBanks, Bs, Ps, alphas}`, `mem.constDims`, `mem.getPadding`) for every memory allocation.
- Control metadata (`isInnerControl`, `isOuterControl`, `isBranch`, `isOuterStreamLoop`, `rawSchedule`, `level`) to pick the correct Chisel `InnerControl`/`OuterControl`/`Sequenced`/`ForkJoin`/etc. template.
- Access metadata (`port.muxPort`, `port.muxOfs`, `port.bufferPort`, `port.castgroup`, `port.broadcast`, `accessWidth`, `shiftAxis`, `residualGenerators`) for every memory read and write.
- Blackbox metadata (`lhs.bboxInfo` = `BlackboxConfig(file, moduleName, _, _, params)`) for Verilog wrappers.
- Register specialization (`lhs.optimizedRegType = Some(AccumAdd | AccumMul | AccumMin | AccumMax | AccumFMA)`) to select `FixOpAccum` / `FixFMAAccum` over the standard `Reg` template.

## Implementation

### Composite structure

`case class ChiselGen(IR: State)` at `spatial/src/spatial/codegen/chiselgen/ChiselGen.scala:5-17` is the concrete pass. It mixes 13 trait layers on top of the `ChiselCodegen` base:

```scala
case class ChiselGen(IR: State) extends ChiselCodegen
  with ChiselGenController
  with ChiselGenBlackbox
  with ChiselGenCounter
  with ChiselGenDebug
  with ChiselGenDelay
  with ChiselGenDRAM
  with ChiselGenInterface
  with ChiselGenMath
  with ChiselGenMem
  with ChiselGenStream
  with ChiselGenStruct
  with ChiselGenVec
```

Each `ChiselGen*` trait extends `ChiselGenCommon`, which itself extends `ChiselCodegen` (`spatial/src/spatial/codegen/chiselgen/ChiselGenCommon.scala:17`). The trait stack uses Scala's linearization: every trait's `gen(lhs, rhs)` override pattern-matches its own cases and falls through to `super.gen(lhs, rhs)` for everything else, which eventually reaches `Codegen.gen`'s "no codegen rule" exception at `spatial/argon/src/argon/codegen/Codegen.scala:89-91`.

### ChiselCodegen base

`trait ChiselCodegen extends NamedCodegen with FileDependencies with AccelTraversal` at `spatial/src/spatial/codegen/chiselgen/ChiselCodegen.scala:17` sets `lang = "chisel"`, `ext = "scala"`, `backend = "accel"` at lines 18-20. `CODE_WINDOW` is pulled from `spatialConfig.codeWindow` at line 21 and drives the chunker's branching factor.

Instance state at lines 22-36 includes `globalBlockID` (chunker label counter), `ensigs` (per-chunk dedup table for enable signal strings), `controllerStack`, `bufMapping` (NBuffered-memory LCA → `List[BufMapping(mem, lane)]`), `regchainsMapping` (regchain LCA → buffer ports), and `cchainCopies` (stream-counter-chain → list of child controllers that own a `_copy<c>` suffix).

`emitHeader()` at lines 64-89 emits the fixed Chisel/Fringe import preamble at the top of every generated file: `package accel`, `import fringe._`, `import fringe.templates.memory._`, `import fringe.templates.math._`, etc.

### The four entry files

`emitPreMain()` at `ChiselCodegen.scala:129-193` opens three of the four entry files:

- `AccelWrapper.scala` (line 130): opens `trait AccelWrapper extends Module {` with `io_w` and `io_v` constants set per-target ("VCS" or "ASIC" → 8/64 bit, else 32/16 bit).
- `Instantiator.scala` (line 148): opens `object Instantiator extends CommonMain { type DUTType = SpatialIP; def dut = () => {` plus a wrapping `class SpatialIPUnitTester(c: SpatialIP)` declaration.
- `ArgInterface.scala` (line 175): opens `object Args {` inside the `package accel` namespace.

`emitPostMain()` at lines 194-291 closes all three and additionally writes:

- `AccelUnit.scala` (line 251): `class AccelUnit(top_w, numArgIns, numArgOuts, numArgIOs, numArgInstrs, numAllocators, loadStreamInfo, storeStreamInfo, gatherStreamInfo, scatterStreamInfo, streamInsInfo, streamOutsInfo) extends AbstractAccelUnit with AccelWrapper { … Main.main(this) }`.
- `Controllers.scala` (line 287): footer only.

The fourth file, `ArgAPI.scala`, is written by `ChiselGenInterface.emitPostMain` at `ChiselGenInterface.scala:156-188` as a flat listing of `val <SYM>_arg = <N>` constants for every registered ArgIn, DRAM pointer, ArgIO, ArgOut, instrumentation counter, and breakpoint.

`emitEntry(block)` at `ChiselCodegen.scala:293-302` wraps the traversal in `object Main { def main(accelUnit: AccelUnit): Unit = { … outsideAccel{gen(block)} … } }`. The Chisel elaboration entry point is `Main.main(accelUnit)`.

### javaStyleChunk and isLive

Chisel targets the JVM, which caps per-method bytecode size at 64 KB. A deeply unrolled outer controller with thousands of reads/writes can emit a single block body that exceeds this limit. `javaStyleChunk` at `spatial/argon/src/argon/codegen/Codegen.scala:107-199` splits the body into `CODE_WINDOW`-weighted chunks, each wrapped in a synthetic `object Block<N>Chunker<M> { def gen(): Map[String, Any] = { … } }`. The per-chunk `Map` contains every "live" sym (those referenced by downstream chunks), and later references into a chunk dereference the map via `ScopeInfo.assemble(sfx)` at lines 97-102.

`gen(b)` at `ChiselCodegen.scala:106-127` calls `javaStyleChunk` with the Chisel-specific `isLive(s, remaining) = (b.result == s || remaining.nestedInputs.contains(s) || bufMapping[x].mem.contains(s))` predicate at line 110, plus a Chisel `arg(tp, node)` string for the map-value cast. Hierarchy depth is `(log(totalWeight max 1) / log(CODE_WINDOW)).toInt` at line 114 — 0 for small bodies (no chunking), 1 for medium, 2 for the largest. The two-level path (lines 156-198 of the base chunker) nests `Block<N>Chunker<M>Sub<K>` inside the outer chunker.

### Live-value detection across chunks

A sym is "live" (escaping the chunk) if:

1. It is the block's return value, or
2. Any remaining stmt in the block references it via `nestedInputs`, or
3. Any remaining stmt has it in its `bufMapping` entry (i.e. is an NBuffered memory whose LCA includes `s`).

Live syms are registered in `Codegen.scoped: mutable.Map[Sym[_], ScopeInfo]` at `spatial/argon/src/argon/codegen/Codegen.scala:95-102`. Downstream `quote(s)` calls hit the `scoped.contains(s)` branch at `ChiselCodegen.scala:51` and resolve to `scoped(s).assemble()` — a `block<N>chunk<M>("<name>").asInstanceOf[<tp>]` map lookup instead of a local val reference.

### `markCChainObjects` and `_copy<c>` suffix

`markCChainObjects(b)` at `ChiselCodegen.scala:100-104` walks every stmt before chunking and registers each counter-chain owned by an outer-stream loop: for each child `c` of the owning controller, `cchainCopies(x) += c`. Later emission uses this to decide whether a counter chain needs one instance or N copies (one per child), with the copies named `<cchain>_copy<c>`. See `writeKernelClass` at `ChiselGenController.scala:127-130` where `cchainCopies.contains(ins.head)` drives a fan-out in the kernel constructor parameter list.

### `createDump(n)` and intermediate IR snapshots

`createDump(n: String)` at `spatial/src/spatial/Spatial.scala:136` returns `Seq(TreeGen(state, n, s"${n}_IR"), HtmlIRGenSpatial(state, s"${n}_IR"))`. It is invoked at six pipeline checkpoints (`PreEarlyUnroll`, `PreFlatten`, `PostStream`, `PostInit`, `PreExecution`, `PostExecution`) to generate HTML IR snapshots. Note that `ChiselGen` itself is **not** part of `createDump` — Chiselgen runs exactly once, as a terminal pass at `Spatial.scala:246` gated by `spatialConfig.enableSynth`.

### `AppProperties` — 23 feature flags

`sealed trait AppProperties` at `spatial/src/spatial/codegen/chiselgen/AppProperties.scala:3` with 23 case objects: `HasLineBuffer`, `HasNBufSRAM`, `HasNBufRegFile`, `HasGeneralFifo`, `HasTileStore`, `HasTileLoad`, `HasGather`, `HasScatter`, `HasLUT`, `HasBreakpoint`, `HasAlignedLoad`, `HasAlignedStore`, `HasUnalignedLoad`, `HasUnalignedStore`, `HasStaticCtr`, `HasVariableCtrBounds`, `HasVariableCtrStride`, `HasFloats`, `HasVariableCtrSyms`, `HasBroadcastRead`, `HasAccumSegmentation`, `HasDephasedAccess`, `HasFSM` (`AppProperties.scala:4-26`). These accumulate into `ChiselGenCommon.appPropertyStats: Set[AppProperties]` at `ChiselGenCommon.scala:32`. The current set is emitted as a comment in `AccelWrapper.scala` at `ChiselGenController.scala:557` via `appPropertyStats.toList.map(_.getClass.getName.split("\\$").last.split("\\.").last).mkString(",")`. Registered call sites in chiselgen:

- `HasTileLoad` / `HasTileStore` / `HasAlignedLoad` / `HasUnalignedLoad` / `HasAlignedStore` / `HasUnalignedStore` at `ChiselGenInterface.scala:103-113`.
- `HasGather` at `ChiselGenInterface.scala:108`; `HasScatter` at `ChiselGenInterface.scala:116`.
- `HasBreakpoint` at `ChiselGenController.scala:399`.
- `HasFSM` at `ChiselGenController.scala:470`.
- `HasAccumSegmentation` at `ChiselGenMem.scala:74, 94`.
- `HasBroadcastRead` at `ChiselGenMem.scala:156`.
- `HasNBufSRAM` at `ChiselGenMem.scala:150`.
- `HasDephasedAccess` at `ChiselGenMem.scala:136`.

Several flags (`HasLineBuffer`, `HasNBufRegFile`, `HasGeneralFifo`, `HasLUT`, `HasStaticCtr`, `HasVariableCtrBounds`, `HasVariableCtrStride`, `HasFloats`, `HasVariableCtrSyms`) are declared but **never registered** in this subdirectory — they exist in the enum for future use or are set by another subsystem (inferred, unverified).

### `RemapSignal` — 29 controller-signal objects

`sealed trait RemapSignal` at `spatial/src/spatial/codegen/chiselgen/RemapSignal.scala:3` with 29 case objects: `En`, `Done`, `BaseEn`, `Mask`, `Resetter`, `DatapathEn`, `CtrTrivial` (marked "Standard Signals" at `RemapSignal.scala:4`), then `DoneCondition`, `IIDone`, `RstEn`, `CtrEn`, `Ready`, `Valid`, `NowValid`, `Inhibitor`, `Wren`, `Chain`, `Blank`, `DataOptions`, `ValidOptions`, `ReadyOptions`, `EnOptions`, `RVec`, `WVec`, `Latency`, `II`, `SM`, `Inhibit`, `Flow` (marked "A few non-canonical signals" at `RemapSignal.scala:12`). Full list at `RemapSignal.scala:5-34`. A grep for `RemapSignal` across `src/spatial/codegen/chiselgen/` turns up no use-site: the enum is shipped but not consumed inside this directory. It is presumably consumed by downstream fringe templates or by the scalagen mirror (inferred, unverified).

### `ledgerized(node)` — partial-IO discrimination

`ledgerized(node)` at `ChiselCodegen.scala:482-489` returns `true` when the node is a non-DRAM / non-ArgIn / non-stream memory, a `DRAMAccel`, a `CtrlBlackbox`, a bound sym inside a blackbox impl, or a `BlackboxUse`. This decides whether `connectWires<i>` at `ChiselGenController.scala:163-177` calls `$in.connectLedger(module.io.in_$in)` (with follow-up `<>` wiring specific to the interface kind) versus a plain `module.io.in_$in <> $in`. The "ledger" is a Chisel runtime registry that tracks partial IO connections across kernels and validates them at elaboration time.

### Named symbol mapping

`NamedCodegen.named(s, id)` at `spatial/src/spatial/codegen/naming/NamedCodegen.scala:23-107` maps each IR sym to a human-readable Scala identifier, case by case: `AccelScope` → `"<s>_[inr|outr]_RootController<name>"`; `UnitPipe` → `"<s>_[inr|outr]_UnitPipe<name>"`; `UnrolledForeach` → `"<s>_[inr|outr]_Foreach<name>"`; `CounterNew` → `"<s>_ctr"`; `SRAMNew` → `"<s>_<sramname>sram"` (plus `_dualread` suffix if `spatialConfig.dualReadPort || s.isDualPortedRead`); `FIFONew` → `"<s>_<fifoname>fifo"`; etc. `ChiselCodegen.named` at `ChiselCodegen.scala:38-53` additionally renames the accel root to `"RootController"` (no `inr`/`outr` prefix) and collapses constant `DelayLine` nodes.

## Interactions

- **Reads** retime metadata, banking metadata, control metadata, access metadata, blackbox metadata, and register-specialization metadata. No writes back.
- **Depends on** the Fringe Chisel template library (`fringe.templates.memory._`, `fringe.templates.math._`, `fringe.templates.counters._`, etc.) and the `Kernel` / `InputKernelSignals` / `OutputKernelSignals` / `Ledger` / `ModuleParams` / `ControllerStack` runtime objects. Not an IR dependency; a Chisel-template dependency.
- **Pairs with** `CppGen` to produce a matching C++ host driver. The two codegens share the argument indexing conventions in `ArgAPI.scala` (Chisel) and the matching `ArgAPI.hpp` (C++).
- **Orthogonal to** `ScalaGenSpatial` (the simulation backend), `DotFlatGenSpatial` / `DotHierarchicalGenSpatial` (visualization), `TreeGen` (controller tree HTML), `HtmlIRGenSpatial` (per-symbol IR HTML), `ResourceReporter` (area model), `ResourceCountReporter` (count-only JSON), `PIRGen` (Plasticine), `TungstenHostGen` (alt host).

## HLS notes

The entire Chiselgen stack is `chisel-specific`: every emission path is tailored to the Fringe template library's Chisel API. An HLS reimplementation needs to preserve the semantic contract (controller per lexical region, one kernel-module per controller, per-memory instantiation with banking/depth/width parameters, latency-aware retiming of datapath arithmetic, FIFO back-pressure composition) while replacing the textual Chisel emission with either C++-HLS template instantiation or direct bitstream generation. See `30 - HLS Mapping/codegen-chiselgen.md` (pending) for the mapping plan.

## Open questions

See `20 - Research Notes/10 - Deep Dives/open-questions-chiselgen.md` — in particular: whether `RemapSignal` is dead code inside chiselgen, whether `AppProperties` flags that are never registered are live, and whether the two-level chunker path has ever triggered in practice.
