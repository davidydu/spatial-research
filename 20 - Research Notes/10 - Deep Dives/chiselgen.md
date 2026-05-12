---
type: deep-dive
topic: chiselgen
source_files:
  - "spatial/src/spatial/codegen/chiselgen/ChiselGen.scala"
  - "spatial/src/spatial/codegen/chiselgen/ChiselCodegen.scala"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenCommon.scala"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenController.scala"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenCounter.scala"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenMem.scala"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenMath.scala"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenDRAM.scala"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenInterface.scala"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenStream.scala"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenBlackbox.scala"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenDebug.scala"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenDelay.scala"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenStruct.scala"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenVec.scala"
  - "spatial/src/spatial/codegen/chiselgen/AppProperties.scala"
  - "spatial/src/spatial/codegen/chiselgen/RemapSignal.scala"
  - "spatial/src/spatial/codegen/naming/NamedCodegen.scala"
  - "spatial/argon/src/argon/codegen/Codegen.scala"
  - "spatial/src/spatial/Spatial.scala"
session: 2026-04-23
status: ready-to-distill
feeds_spec:
  - "[[10 - Overview]]"
  - "[[20 - Types and Ports]]"
  - "[[30 - Memory Emission]]"
  - "[[40 - Controller Emission]]"
  - "[[50 - Streams and DRAM]]"
  - "[[60 - Math and Primitives]]"
---

# Chiselgen — Deep Dive

## Reading log

Read in priority order: `ChiselGen.scala` (composite), `ChiselCodegen.scala` (base trait, 492 lines), `ChiselGenCommon.scala` (shared state, 459 lines), `ChiselGenController.scala` (589 lines), `ChiselGenMem.scala` (378 lines), `ChiselGenMath.scala` (279 lines), `ChiselGenDRAM.scala` (87 lines), `ChiselGenStream.scala` (201 lines), `ChiselGenInterface.scala` (193 lines), `ChiselGenBlackbox.scala` (360 lines), `ChiselGenDebug.scala` (44 lines), `ChiselGenDelay.scala` (38 lines), `ChiselGenStruct.scala` (47 lines), `ChiselGenVec.scala` (44 lines), `ChiselGenCounter.scala` (25 lines), `AppProperties.scala` (27 lines, 23 objects), `RemapSignal.scala` (34 lines, 29 objects). Cross-referenced base chunker at `spatial/argon/src/argon/codegen/Codegen.scala:107-199` and naming mixin at `spatial/src/spatial/codegen/naming/NamedCodegen.scala:13-107`.

## Observations

### Composite structure

`case class ChiselGen(IR: State)` at `spatial/src/spatial/codegen/chiselgen/ChiselGen.scala:5-17` mixes 13 traits on top of the `ChiselCodegen` base: `ChiselGenController`, `ChiselGenBlackbox`, `ChiselGenCounter`, `ChiselGenDebug`, `ChiselGenDelay`, `ChiselGenDRAM`, `ChiselGenInterface`, `ChiselGenMath`, `ChiselGenMem`, `ChiselGenStream`, `ChiselGenStruct`, `ChiselGenVec`. All of these traits extend `ChiselGenCommon` (which itself extends `ChiselCodegen`). The composite is instantiated at `spatial/src/spatial/Spatial.scala:147` as `lazy val chiselCodegen = ChiselGen(state)` and gated by `spatialConfig.enableSynth` in the pass-pipeline chain at `spatial/src/spatial/Spatial.scala:246`.

### `ChiselCodegen` base (the spine)

At `spatial/src/spatial/codegen/chiselgen/ChiselCodegen.scala:17-20`, `ChiselCodegen` extends `NamedCodegen with FileDependencies with AccelTraversal`, sets `lang = "chisel"`, `ext = "scala"`, `backend = "accel"`. `CODE_WINDOW` is pulled from `spatialConfig.codeWindow` at line 21. Lines 23-36 allocate instance-level state: `globalBlockID` counter for chunker labels, `ensigs` for dedup'd enable signals, `boreMe` for `BoringUtils`, `blackBoxStreamInWidth`/`blackBoxStreamOutWidth`, `controllerStack`, `bufMapping` (LCA → `List[BufMapping]`), `regchainsMapping`, `cchainCopies` (counter chain → list of copy owners for stream controllers).

The `named(s, id)` override at lines 38-53 renames the accel root controller to `"RootController"` and collapses constant `DelayLine` nodes to their quoted data; otherwise it falls through to `NamedCodegen`. The scoped-map lookup at line 51 is what switches a local `val x123` reference into the chunker's map lookup (`blockNchunkM("x123").asInstanceOf[FixedPoint]`).

`emitHeader()` at lines 64-89 emits a fixed set of Chisel/Fringe imports at the top of every generated file. `emitPreMain()` at lines 129-193 creates four entry files inside `AccelWrapper.$ext` / `Instantiator.scala` / `ArgInterface.scala`, with `trait AccelWrapper extends Module {` opened but not closed (closed in `emitPostMain`), `object Instantiator extends CommonMain { … def dut = () => {` left open, and `object Args {` left open. `emitPostMain()` at lines 194-291 closes these and additionally emits `AccelUnit.scala` (the `class AccelUnit(…)` that extends `AbstractAccelUnit with AccelWrapper`, calling `Main.main(this)` at line 279) and `Controllers.scala` (footer only).

`emitEntry(block)` at lines 293-302 wraps everything in `object Main { def main(accelUnit: AccelUnit): Unit = { … outsideAccel{gen(block)} … } }`. So the generated RTL's entry point is `Main.main(accelUnit)`.

### The four type-remappers

This is one of the subtler design surfaces. In `ChiselCodegen`:

- `quoteConst(tp, c)` at lines 315-321 formats constants: fixed point becomes `"<c>.FP(s, d, f)"` with `"L"` suffix if `d+f >= 32 && f == 0`; float becomes `"<c>.FlP(g, e)"`; bits become `"<c.value>.B"`; text passes through.
- `remap(tp)` at lines 323-331 — the "data type" function — emits `"new FixedPoint(s, d, f)"`, `"new FloatingPoint(m, e)"`, `"Bool()"`, `"Vec(w, remap(inner))"`.
- `arg(tp, node)` at lines 336-391 — the "function argument type" function — used when passing nodes through Scala function calls (kernel modularization). Produces bare type names like `"FixedPoint"`, `"FloatingPoint"`, `"Bool"`, `"StandardInterface"`, `"NBufInterface"`, `"FIFOInterface"`, `"FixFMAAccumBundle"`, `"FixOpAccumBundle"`, `"AXI4Stream"`, `"DecoupledIO[AppLoadData]"`, etc.
- `port(tp, node)` at lines 394-455 — the "Chisel IO port" function — wraps with `Input(…)`, `Flipped(new NBufInterface(…))`, `Flipped(new StandardInterface(ModuleParams.getParams("<sym>_p").asInstanceOf[MemParams]))`, etc.
- `param(node)` at lines 457-480 — the "`ModuleParams.addParams` payload" function — produces e.g. `m.io.np` for NBuffered, `(m.io.ways, m.io.par, m.io.bitWidth, m.io.readers)` for MergeBuffer, `m.io.p` for primitive memories, `(x.rank, x.appReqCount)` for DRAMAccel, counter-chain `(par, widths)` tuples. Returns `Option[String]` because some nodes don't have parameter payloads.

There's a second `remap` override in `ChiselGenStruct` at `ChiselGenStruct.scala:11-14` that adds `case _: Struct[_] => "UInt(bitWidth.W)"`, demonstrating that the type remapper composition is trait-layered — traits only override the cases they care about, with `super.remap(tp)` falling through.

`ledgerized(node)` at lines 482-489: a node gets "ledgerized" (i.e. has a per-controller partial IO connected through a `connectLedger` call) if it's a non-DRAM/non-ArgIn/non-stream memory, a DRAMAccel, a Ctrl blackbox, a bound symbol inside a blackbox impl, or a blackbox use. This drives the `connectWires<i>` emission at `ChiselGenController.scala:163-177`.

### javaStyleChunk and `isLive`

The chunker lives at `spatial/argon/src/argon/codegen/Codegen.scala:107-199`. For `hierarchyDepth == 0` it just visits in place. For `hierarchyDepth == 1` (lines 132-155), it opens a synthetic `object Block${blockID}Chunker${chunkID} { def gen(): Map[String, Any] = { … } }` per chunk, emits the chunk body, then at the end emits a `Map[String, Any]` with one entry per "live" sym: for non-copy syms, the entry is `branchSfx(s, None)` which is `"quote(s)" -> s` or `"quote(s)" -> s.data` (for branches). Live syms are registered in the instance-level `scoped: mutable.Map[Sym[_], ScopeInfo]`. After each chunk closes, the caller emits `val block${blockID}chunk$chunkID: Map[String, Any] = Block${blockID}Chunker${chunkID}.gen()`.

Downstream references to a live sym then go through `ScopeInfo.assemble(sfx)` at `Codegen.scala:97-102` which produces `block<N>chunk<M>sub<K?>("<quote(s) + sfx>").asInstanceOf[<tp>]`. This is why `quote(s)` in `ChiselCodegen` at lines 38-53 falls back to `scoped(s).assemble()` when `scoped.contains(s)`: the sym's own quote resolves to the chunk map lookup instead of a local val.

`isLive(s, remaining)` at `ChiselCodegen.scala:110` is the Chisel-specific "escaping the chunk" predicate: a sym is live if it is the block result, or if any remaining stmt (the stmts that weren't yet written) references it via `nestedInputs`, or if any later stmt has it in its `bufMapping` list. For the 2-level chunker (lines 156-198), a three-level structure `block<N>chunk<M>sub<K>` is used, and there's a dance at lines 188-191 to rename keys in the outer map so subsequently emitted statements can reach into a sub-chunk through a two-hop map lookup.

`hierarchyDepth` is computed at `ChiselCodegen.scala:114` as `(log(printableStms.weight.sum max 1) / log(CODE_WINDOW)).toInt`. In practice this is 0 (no chunking) or 1 (one level) for small controllers, 2 for the largest ones (but see open Q about whether 2-level has ever triggered in real apps).

`printableStms` at line 109 filters out broadcast-addr stmts and weights each remaining sym by `parOrElse1` times the number of stream-counter copies (`cchainCopies`), the latter being the `_copy<c>` suffix. Host-scoped stmts get weight 0 (they emit textual-only output like `.hpp` constants).

`markCChainObjects(b)` at lines 100-104 walks the block pre-chunking and registers each child of an outer stream loop as an "owner" of a counter-chain copy, accumulating into `cchainCopies`.

### ChiselGenCommon — the per-controller bookkeeping

`ChiselGenCommon` at `ChiselGenCommon.scala:17-455` accumulates around 15 mutable maps/lists on the codegen instance. The most important:

- `loadStreams`, `storeStreams`, `gatherStreams`, `scatterStreams: HashMap[Sym[_], (String, Int)]` (lines 23-26) — per-DRAM side-channel accumulation. Key = the stream allocation sym, value = a pair of (`StreamParInfo("…")` string, index into the Fringe wire list).
- `argOuts`, `argIOs`, `argIns: HashMap[Sym[_], Int]` (lines 35-37) and `argOutLoopbacks: HashMap[Int, Int]` (line 38) — scalar interface registration.
- `accelDrams`, `hostDrams: HashMap[Sym[_], Int]` (lines 39-40) — DRAM allocator indices.
- `earlyExits: List[Sym[_]]` (line 42) — breakpoint / assert / exit nodes.
- `instrumentCounters: List[(Sym[_], Int)]` (line 44) — pairs of (controller sym, depth).
- `activesMap: HashMap[Sym[_], Int]` (line 47) — FIFO/LIFO/FIFOReg access → activity-lane index.
- `appPropertyStats: Set[AppProperties]` (line 32) — accumulator for the 23-object enum.

`enterCtrl(lhs)` at lines 72-82 pushes onto `controllerStack`, resets `ensigs`, appends to `instrumentCounters` if instrumentation is enabled and `inHw`, records `widthStats += lhs.children.size` for outer and `depthStats += controllerStack.length` for inner. `exitCtrl(lhs)` pops.

`getInputs(lhs, func*)` at lines 89-101 computes the transitive input closure: `lhs.nonBlockInputs ++ each block's nestedInputs ++ lhs.readMems`, minus counter chains, minus blackbox-impl bounds, plus `RemoteMemories` whose consumers have `lhs` in ancestors, plus stream mems if `hasStreamAncestor`, plus `bufMapping` entries keyed on `lhs`. Then subtract `lhs.op.binds &~ RemoteMemories.all` and drop values. `groupInputs(inss)` at lines 103-105 groups by `arg(tp, node)` so the kernel class constructor gets one `List[<type>]` parameter per type group — except counter-chain copies are emitted as individual params.

`iodot`/`dotio`/`cchainOutput` at lines 107-110 encode the `enableModular` toggle. With modular on, field access goes through `io.<…>`; without, the kernel has `cchain.head.output.done` directly available in scope.

`ifaceType(mem)` at lines 111-123 returns the `.asInstanceOf[<Interface>]` suffix used when a memory's `m.io` reference is cast back to its bundle type.

`DL(name, latency, isBit=false)` at lines 288-293 is the universal delay wrapper — emits `($name).DS($lat.toInt, rr, bp & fp)` for bit values or `getRetimed($name, $lat.toInt, bp & fp)` for arbitrary words. The forward-pressure term is only included when `controllerStack.head.haltIfStarved` is true. `DLo` at lines 296-300 is the same but reads `backpressure` off a different SM object (used when we're visiting children but emitting on a parent signal).

`getForwardPressure(sym)` at lines 249-264 composes stream-readability from `StreamInNew.valid`, `FIFONew ~empty`, `FIFORegNew ~empty`, `MergeBufferNew ~empty`, plus `bbox.getForwardPressures(fields)` and stream-struct fields that are bound — every piece `.D($II-1)` delayed. It also combines "priority dequeue groups" via `getReadPriorityStreams(sym)` with `or` inside each group, `and` across groups. `getBackPressure(sym)` at lines 266-279 is the mirror for writes (`StreamOutNew.ready`, `~full`, etc.).

`connectDRAMStreams(dram)` at lines 416-453 is called once per DRAM allocation. It walks `dram.loadStreams`, `dram.storeStreams`, `dram.gatherStreams`, `dram.scatterStreams` — each of these returns `FringeTransfer` records with `addrStream`/`dataStream`/`ackStream` — and emits `val <addrStream> = accelUnit.io.memStreams.loads(<N>).cmd`, etc. It registers the stream syms into `RemoteMemories` and populates `loadStreams`/etc with a `StreamParInfo(bitWidth, par, 0)` string that's later dropped into `AccelWrapper.scala`/`Instantiator.scala`.

`createCtrObject(lhs, start, stop, step, par, forever)` at lines 373-401 emits `val <lhs> = new CtrObject(Left(Some(s))|Right(expr), …, par, w, forever)`. `createCChainObject(lhs, ctrs, suffix)` at lines 408-414 emits `(new CChainObject(List[CtrObject](…), "<lhs><sfx>")).cchain.io`. `createStreamCChainObject(lhs, ctrs)` at lines 402-406 calls `createCChainObject` once per child of `lhs.owner`, each with its own `_copy<c>` suffix.

### ChiselGenController — one kernel class per controller

The heart of the backend. For every `EnControl` (AccelScope / UnitPipe / UnrolledForeach / UnrolledReduce / StateMachine / Switch / SwitchCase / ParallelPipe / IfThenElse), `writeKernelClass(lhs, ens, func*)` at `ChiselGenController.scala:102-243` emits `sm_<lhs>.scala` containing `class <lhs>_kernel(<grouped inputs>, parent, cchain, childId, nMyChildren, ctrcopies, ctrPars, ctrWidths, breakpoints, instrctrs?, rr: Bool) extends Kernel(…) { … def kernel(): <ret> = { … } }`.

Inside the `kernel()` body: emits `Ledger.enter(hashCode, "<lhs>")`; if `enableModular`, opens an inner `class <lhs>_concrete(depth: Int) extends <lhs>_module(depth) { … io.sigsOut := DontCare; val breakpoints = io.in_breakpoints; val rr = io.rr }` and the module body contains the actual logic; if not modular, the logic sits directly inside `kernel()`.

`createAndTieInstrs(lhs)` at `ChiselGenCommon.scala:190-206` emits `val cycles_<lhs> = Module(new InstrumentationCounter())`, same for `iters_<lhs>`, and if the controller has any back or forward pressure also `stalls_<lhs>` and `idles_<lhs>`. Then `Ledger.tieInstrCtr(instrctrs.toList, <LHS>_instrctr, cycles.count, iters.count, stalls.count, idles.count)`.

`emitItersAndValids(lhs)` at `ChiselGenController.scala:47-82` emits `val <iter> = <cchainOutput>.counts(<id>).FP(true, w, 0)` — each iter is a fixed-point view of the counter chain output at that index. For outer pipes with >1 children, also constructs a `RegChainPass` to daisy-chain the iterator through pipeline stages, using `regchainsMapping` to later tie each child's consumer to the right port. Reads go through `<iter>_chain_read_<port>`.

`emitItersAndValidsStream(lhs)` at lines 84-100 is the outer-stream variant: each child `c` gets its own `<iter>_copy<c>` read off of `cchainCopyOutput(ii)` where `ii` is the child's index. No daisy chain.

`instantiateKernel(lhs, ens, func*)(modifications)` at lines 250-330 emits the `val <lhs><swobj> = new <lhs>_kernel(<chainPassedInputs>, parent, cchain, childId, …, rr)` instantiation. `<swobj>` is `_obj` for branches (Switch/SwitchCase/StateMachine), empty otherwise. Then wires `sm.io.ctrDone` based on controller kind: for non-outer-stream cchain controllers it's `<lhs><swobj>.cchain.head.output.done` delayed by 1; for non-terminal switch cases it's the head child's `.done`; for state machines it's a variant of head-child or `iiDone.D(fullDelay)`. Then connects `backpressure := getBackPressure | sm.io.doneLatch`, `forwardpressure := getForwardPressure | sm.io.doneLatch`, and so on.

`createSMObject(lhs)` at lines 333-360 emits the core per-controller primitives: `val sm = Module(new <level>(<rawSchedule>, <constrArg>, <stateWidth?>, <isPassthrough?>, <cases?>, latency=<lat>.toInt, myName="<lhs>_sm"))` and `val iiCtr = Module(new IICounter(<ii>.toInt, 2 + log2Up(<ii>.toInt), "<lhs>_iiCtr"))`. `lhs.level.toString` is e.g. `"InnerControl"` or `"OuterControl"`.

The dispatch at lines 362-493: `AccelScope` is specialized at lines 363-413 with a retime_counter, `rr` (a delayed "retime released" bit), breakpoints wire, instrctrs vector, and a done_latch SRFF. It instantiates DRAM allocators for every accel DRAM in `RemoteMemories`. `EnControl` generic handler at lines 415-421 is the default for UnitPipe/UnrolledForeach/UnrolledReduce/ParallelPipe. Switch/SwitchCase at 424-467. StateMachine at 469-486 — with explicit `val state = notDone.input` wire and `gen(notDone); gen(action); gen(nState)` sequence, then `nextState := nState.result.r.asSInt; initState := start.r.asSInt; doneCondition := ~notDone.result`.

`emitPostMain()` at lines 495-586 writes `Instrument.scala` with the instrument-counter wiring routine (also chunked via `javaStyleChunk` because it can be huge — one group of 4 or 6 lines per counter), and appends post-body constants to `Instantiator.scala` and `AccelWrapper.scala`: `numArgOuts_instr`, `numCtrls`, `numArgOuts_breakpts`, the `/* Breakpoint Contexts */` comment block listing source contexts, and various target latencies via `latencyOption("FixMul", Some(1))` etc., `globals.target.cheapSRAMs`, `globals.target.sramload_latency`, `globals.retime`, `globals.enableModular`.

### ChiselGenMem — per-memory-class emission

For every `SRAMNew`/`RegNew`/`FIFONew`/`LIFONew`/`RegFileNew`/`LineBufferNew`/`LUTNew`/`MergeBufferNew`/`FIFORegNew`, `emitMem(lhs, init)` at `ChiselGenMem.scala:134-208` generates a per-mem Scala file `m_<lhs>.scala` with:

- Per-writer `lazy val w$i = Access(hashCode, muxPort, muxOfs, castgroup, broadcast, shiftAxis, PortInfo(bufferPort, 1 max accessWidth, 1 max ofsWidth, banksWidths, bitWidth, resids))`
- Per-reader `lazy val r$i = Access(…)` similar
- A single `lazy val m = Module(new <templateName>(dimensions, depth?, bitWidth, numBanks, blockCycs, neighborhood, List(w0, …), List(r0, …), BankedMemory, initStr, !enableAsyncMem && enableRetiming, fracBits, readers+writers, myName="<mem>"))`
- `m.io<ifaceSuffix> <> DontCare`
- For FIFO/FIFOReg, writer/reader → activity-lane registration via `activesMap`

`templateName` at lines 148-155: for non-NBuffered non-LineBuffer mems, `"<name><DualRead?>("`, where `name` comes from `mem.memName`. For NBuffered or LineBuffer, `"NBufMem(<name><DualRead?>Type, "`. NBuffered SRAM registers `HasNBufSRAM`; `broadcastsAnyRead` registers `HasBroadcastRead`.

`paddedDims(mem, name)` at lines 108-112 returns `constDims` zipped with padding (either `getPadding` or all zeros). `expandInits(mem, inits, name)` at lines 114-132 pads the init sequence: walks every padded coordinate, writes `0.0` outside the original dims.

Inputs to the `m = Module(new …)` call: `dimensions` = `List(d+p, …)`; `numBanks` = `inst.nBanks` (for LUT/RegFile: just `dims`); `blockCycs` = `inst.Bs` (Bs); `neighborhood` = `inst.Ps` (Ps); `bankingMode` = `"BankedMemory"` (TODO in source: "find correct one"). `ofsWidth` for LineBuffer is `utils.math.ofsWidth(paddedDims.last, Seq(inst.nBanks.last))`; for others, the full volume expression.

`splitAndCreate(lhs, mem, port, tp, payload)` at lines 19-38 handles the JVM line-length limit: if the total payload fits into ~150 chars, emit `val <port> = List[<tp>](<payload>)`; otherwise split into groups and emit helper `def create_<port>(): List[<tp>] = { … List0 ++ List1 ++ … }` and `val <port> = create_<port>()`. Called for `<lhs>_banks`, `<lhs>_ofs`, `<lhs>_en`, `<lhs>_data` lists in `emitRead`/`emitWrite`.

`emitRead(lhs, mem, bank, ofs, ens)` at lines 73-91 generates `$lhs.toSeq.zip($mem.connectRPort(hashCode, <lhs>_banks, <lhs>_ofs, backpressure, <lhs>_en.map(_ && <lhs>_shared_en), !broadcastsAnyRead)).foreach{case (a,b) => a.r := b.r}`. LUTs skip the forward-pressure gating (nonlut_mask = `true.B`).

`emitWrite(lhs, mem, data, bank, ofs, ens, shiftAxis?)` at lines 93-106 mirrors this with `connectWPort(hashCode, banks, ofs, data, en.map(_ && implicitEnableWrite && and(commonEns)))`.

`optimizedRegType` dispatch at lines 228-276: a `Reg` tagged with `AccumAdd`/`AccumMul`/`AccumMin`/`AccumMax`/`AccumFMA` generates a specialized `FixOpAccum(Accum.Add, numWriters, cycleLatency, opLatency, s, d, f, init)` or `FixFMAAccum(…)` instead of the standard memory. The opLatency is computed via `latencyOption("FixAdd", Some(d+f))` etc., and cycleLatency adds `RegRead`/`RegWrite` latencies. Per-reg-op dispatch: `RegAccumOp` at lines 281-286 and `RegAccumFMA` at lines 287-292 call `reg.connectWPort(idx, data.r, en && invisEn, DL(ctrDone, fullDelay, true), first)`.

MergeBuffer emission at lines 350-371 is unique — it uses `createMemObject` then has per-op wrappers that call `connectMergeEnq(way, d, en)` / `connectMergeDeq(idx, en)` / `connectMergeBound(way, data.r, en & invEn)` / `connectMergeInit(data.r, en & invEn)`.

### ChiselGenMath — latency-aware arithmetic

Every `Fix*`/`Flt*` op falls through `MathDL(lhs, rhs, nodelat)` at `ChiselGenMath.scala:24-105`. The latency passed in comes from `latencyOption("FixMul", Some(bitWidth(lhs.tp)))` etc. at the dispatch site (lines 107-275). `latencyOption` at `ChiselGenCommon.scala:63-70` pulls from `spatialConfig.target.latencyModel.exactModel(op)("b" -> b.get)("LatencyOf")` when retiming is enabled, else 0.0.

The emitted code is uniformly `$lhs.r := Math.<op>($x, $y, $lat, $backpressure, <Rounding?>, <Overflow?>, "$lhs").r`. Rounding and overflow modes are part of the op constructor name: `UnbMul` takes `Unbiased, Wrapping`; `SatMul` takes `Truncate, Saturating`; `UnbSatMul` takes `Unbiased, Saturating`.

The floating-point ops become `Math.fadd`/`fsub`/`fmul`/`fdiv`/`fsqrt`/`feql`/`flt`/`flte`/`fneq`/`frec`. Comparisons `FixLst`/`FixLeq`/`FixEql`/`FixNeq` become `Math.lt`/`lte`/`eql`/`neq`. Conversions `FixToFix` become `Math.fix2fix($x, sign, ibits, fbits, lat, bp, Truncate, Wrapping, "$lhs")`; `FixToFlt`/`FltToFix`/`FltToFlt` are similar.

`ensig` compression: `newEnsig(code)` at lines 17-22 checks if the backpressure string was already emitted in this chunk; if so, reuses `ensig<N>`, else emits `val ensig<N> = Wire(Bool()); ensig<N> := <code>`. Saves a ton of characters when many ops share a pressure computation.

Shifts are special: `FixSLA(x, y)` at lines 79-81 requires `y` to be constant (via `DLTrace`), then emits `Math.arith_left_shift($x, $shift, $lat, $backpressure, "$lhs")`. Trigonometry uses `Math.sin`/`cos`/`tan` (atan dispatches to tan). `FixRecipSqrt` at line 49 is nested: `(Math.div(<lhs>_one, Math.sqrt(x, latencyOption("FixSqrt", …), bp), …)`.

`FixRandom` at lines 155-168 synthesizes a `PRNG(<seed>)` instance at compile time with `<seed> = scala.math.random*1000`. `FixAbs` at lines 175-177 compiles to `Mux($x < 0, -$x, $x)`. `FltMax`/`FltMin` similarly.

### ChiselGenDRAM and ChiselGenStream

`ChiselGenDRAM.gen` at `ChiselGenDRAM.scala:16-70`: `DRAMHostNew` registers `hostDrams += (lhs -> N)`, calls `connectDRAMStreams(lhs)`, emits `val <lhs> = Wire(new FixedPoint(true, 64, 0)); <lhs>.r := accelUnit.io.argIns(api.<ID>_ptr)`. `DRAMAccelNew` is deliberately empty — the actual `DRAMAllocator` module is instantiated inside `AccelScope` at `ChiselGenController.scala:367-376`. `DRAMAlloc(dram, dims)` calls `<dram>.connectAlloc(id, List[UInt](…), invEnable)`. `DRAMIsAlloc(dram)` reads `<dram>.output.isAlloc`. `DRAMDealloc` emits `connectDealloc(id, invEnable)`.

`ChiselGenStream.gen` at `ChiselGenStream.scala:17-179`: `StreamInNew`/`StreamOutNew` for AXI streams register their index into `axiStreamIns`/`axiStreamOuts` and connect to `accelUnit.io.axiStreamsIn(<n>)` / `axiStreamsOut(<n>)`. For non-AXI buses, the stream allocation produced nothing here — the actual wiring was done in `connectDRAMStreams`.

`StreamOutBankedWrite` at lines 34-136 does the bus-specific emission: for `BurstCmdBus`, extracts `addr`/`size` bitfields from `data`; for `BurstFullDataBus`, extracts `wdata`/`wstrb` (per-lane if `ens.size > 1`); for `GatherAddrBus`, sets `stream.bits.addr(i) := d.r`; for `ScatterCmdBus`, sets both `addr(i)` and `wdata(i)` from the packed `data`. For AXI types, there are two paths per width (64/256/512): if the data is the full AXI stream type, copy all eight fields; if not, only `TDATA`, zero-fill strb/keep, constant `TID`/`TDEST` from the bus parameters, `TLAST := 0`.

`StreamInBankedRead` at lines 139-175 mirrors this: `BurstDataBus` reads `strm.bits.rdata(i).r` into `lhs(i).r`; AXI flavors either Cat all fields or just take `TDATA`, and for non-full-AXI the `ready` is AND'd with `TID === tid.U & TDEST === tdest.U`.

`emitPostMain` at lines 181-199 sanity-checks that there is at most 1 AxiStream In and 1 AxiStream Out — "its easy to support more, we just haven't implemented it yet" per line 185-186.

### ChiselGenInterface — scalar boundary

`ArgInNew`, `ArgOutNew`, `HostIONew` register into `argIns`/`argOuts`/`argIOs`. `HostIONew` additionally emits a `MultiArgOut` with one port per non-host-parent writer, plus the Mux1H logic to pick the valid writer. `RegRead`/`RegWrite` for `ArgIn`/`ArgOut`/`HostIO` are specialized to `reg.connectRPort()` / `reg.connectWPort(id, v.r, en & DL(datapathEn & iiIssue, fullDelay))`. For signed 64-bit ArgOut with `d+f < 64`, the value is sign-extended via `util.Cat(util.Fill(64-d-f, v.msb), v.r)`.

`FringeDenseLoad`/`FringeSparseLoad`/`FringeDenseStore`/`FringeSparseStore` at lines 102-117 register `HasTileLoad`/`HasTileStore`/`HasGather`/`HasScatter`/`HasAlignedLoad`/`HasUnalignedLoad`/`HasAlignedStore`/`HasUnalignedStore` into `appPropertyStats` but emit no code.

`emitPostMain` at lines 121-190 writes `ArgAPI.scala` (a pure constants file mapping symbol → API index). The argument-address allocation is: `ArgIns [0 … numArgIns_reg)`, `DRAM pointers [numArgIns_reg … +hostDrams.size)`, `ArgIOs`, `ArgOuts`, instrumentation counters (2 or 4 per controller — last two only if has back/forward pressure), then early-exit breakpoints.

### ChiselGenBlackbox

`VerilogBlackbox` at `ChiselGenBlackbox.scala:20-73` produces two nested classes: `<bbName>_<lhs>_wrapper()` as a Chisel `Module` with the user's input and output `UInt` ports, and underneath it the actual `BlackBox(params)` class named `<bbName>` that imports the user's Verilog file via `java.nio.file.Files.copy` at elaboration time. Only emits the `BlackBox` class once per unique `bbName`. Output bits are Cat'd together at the use site.

`VerilogCtrlBlackbox` at lines 74-165 is similar but the wrapper exposes an enable input and a done output, and uses `StreamStructInterface` for the input and output struct ports instead of `UInt` fields. Each input/output field gets its own `valid`/`ready` pair, plus an `enable` input and `done` output.

`SpatialBlackboxImpl` at lines 166-211 emits `bb_<lhs>.scala` with a Chisel `Module` whose body is `gen(func)` — the user-written blackbox function gets the full codegen treatment. The input is packed into a single UInt via `Cat(...)`, and the output is sliced back out with `$func.result($start, $end).r`.

`SpatialCtrlBlackboxImpl` at lines 240-314 mirrors the `writeKernelClass` pattern, with a similar `<lhs>_kernel(...) extends Kernel(…)` and inner `<lhs>_module` / `<lhs>_concrete` classes. Requires `enableModular` (throws otherwise).

### Debug / delay / struct / vec — short traits

`ChiselGenDebug` stubs out every text operation (`FixToText`, `TextConcat`, `PrintIf`, `BitToText`, `GenericToText`, `VarNew`, `VarRead`, `VarAssign`) as `val $lhs = ""`. `ExitIf`, `AssertIf`, `BreakpointIf` register into `earlyExits` and call `Ledger.tieBreakpoint(breakpoints, <N>, <en> & datapathEn.D(fullDelay))` (or with `& ~cond` for AssertIf).

`ChiselGenDelay.gen` emits `val $lhs = Wire(<tp>).suggestName("<lhs>_<dataname>_D<delay>")` and then `$lhs.r := DL(data.r, delay, false)` — bumping `maxretime` so `AccelWrapper` later records `val max_latency = <maxretime>`.

`ChiselGenStruct.gen` packs `SimpleStruct` fields into a UInt via `ConvAndCat(f0.r, f1.r, …)`. `SimpleStreamStruct` builds a `StreamStructInterface(Map)` wire with ready/valid/active plumbing per field. `FieldDeq` at lines 32-37 emits the `$struct.get("f").ready := (ens) & ~$break && DL(datapathEn & iiIssue, fullDelay, true)` plus a `Ledger.connectStructPort($struct.hashCode, "f")` registration. `FieldApply` is a plain bit-range extract via `$lhs.r := $struct($start, $end)`.

`ChiselGenVec.gen` emits `VecInit`, slice via zipWithIndex, concat via Seq.zip ++, apply via indexing. `ShuffleCompressVec` calls `Shuffle.compress(Vec(data), Vec(mask))` and recombines. `BitsPopcount` uses Chisel's `PopCount(Seq(data))`.

### AppProperties + RemapSignal

`AppProperties.scala:3-26` defines a sealed trait with 23 case objects: `HasLineBuffer`, `HasNBufSRAM`, `HasNBufRegFile`, `HasGeneralFifo`, `HasTileStore`, `HasTileLoad`, `HasGather`, `HasScatter`, `HasLUT`, `HasBreakpoint`, `HasAlignedLoad`, `HasAlignedStore`, `HasUnalignedLoad`, `HasUnalignedStore`, `HasStaticCtr`, `HasVariableCtrBounds`, `HasVariableCtrStride`, `HasFloats`, `HasVariableCtrSyms`, `HasBroadcastRead`, `HasAccumSegmentation`, `HasDephasedAccess`, `HasFSM`. These accumulate into `appPropertyStats: Set[AppProperties]` on the codegen instance and are emitted as the `"App Characteristics"` comment line in `AccelWrapper.scala` at `ChiselGenController.scala:557`. Not every flag is actually registered in the current codebase — `HasTileLoad`/`HasTileStore`/`HasAlignedLoad`/`HasUnalignedLoad`/`HasAlignedStore`/`HasUnalignedStore`/`HasGather`/`HasScatter` come from `ChiselGenInterface.scala:102-117`; `HasBreakpoint` from `ChiselGenController.scala:399`; `HasAccumSegmentation` from `ChiselGenMem.scala:74, 94`; `HasBroadcastRead` from `ChiselGenMem.scala:156`; `HasNBufSRAM` from `ChiselGenMem.scala:150`; `HasDephasedAccess` from `ChiselGenMem.scala:136`; `HasFSM` from `ChiselGenController.scala:470`. Many are defined but never referenced in this subdirectory.

`RemapSignal.scala:3-34` has 29 case objects: `En`, `Done`, `BaseEn`, `Mask`, `Resetter`, `DatapathEn`, `CtrTrivial`, `DoneCondition`, `IIDone`, `RstEn`, `CtrEn`, `Ready`, `Valid`, `NowValid`, `Inhibitor`, `Wren`, `Chain`, `Blank`, `DataOptions`, `ValidOptions`, `ReadyOptions`, `EnOptions`, `RVec`, `WVec`, `Latency`, `II`, `SM`, `Inhibit`, `Flow`. The file comments itself: `"Standard Signals"` (En, Done, BaseEn, Mask, Resetter, DatapathEn, CtrTrivial) and `"A few non-canonical signals"` (the rest). A grep for `RemapSignal` within the chiselgen directory turns up nothing — the enum is exported but no use-site in this subdir references it. That corresponds to the observation in the coverage note that `RemapSignal` "is shipped but not yet wired in."

### Compilation-pipeline integration

`ChiselGen` is instantiated at `spatial/src/spatial/Spatial.scala:147` and runs at line 246 (after treeCodegen, irCodegen, dotFlat, dotHier, scalaCodegen). `createDump(n)` at line 136 reads `Seq(TreeGen(state, n, s"${n}_IR"), HtmlIRGenSpatial(state, s"${n}_IR"))` and runs at several IR checkpoints (PreEarlyUnroll, PreFlatten, PostStream, PostInit, PreExecution, PostExecution) but `ChiselGen` itself is not part of `createDump` — it's a single terminal pass.

### Emission ordering

`emitEntry` calls `emitPreMain` (opens `AccelWrapper.scala`, `Instantiator.scala`, `ArgInterface.scala`), then `gen(block)` in the `outsideAccel` scope, then `emitPostMain`. `gen(block)` traverses the IR. For `AccelScope`, the dispatch calls `instantiateKernel` (emits the `<lhs>` kernel construction at the call site), then `writeKernelClass` (opens a new file `sm_<lhs>.scala` with `emitHeader` and emits the class definition). The kernel class's body recursively calls `gen(func)` which produces nested `writeKernelClass` for every child controller — so each controller lives in its own Scala file, with a chain of modular `sm_<c>.scala` files and the entry chain at `Main.scala`.

### `sm_<lhs>.scala` file shape

For an outer `UnrolledForeach`:

```
// imports...
class <lhs>_kernel(list_<in0>: List[FixedPoint], …, parent, cchain, childId, nMyChildren, ctrcopies, ctrPars, ctrWidths, breakpoints, instrctrs, rr: Bool) extends Kernel(parent, cchain, childId, nMyChildren, ctrcopies, ctrPars, ctrWidths) {
  val me = this
  val sm = Module(new OuterControl(Sequenced, <nChildren>, isFSM = false, latency = <lat>.toInt, myName = "<lhs>_sm"))
  val iiCtr = Module(new IICounter(<ii>.toInt, 2 + log2Up(<ii>.toInt), "<lhs>_iiCtr"))

  abstract class <lhs>_module(depth: Int)(implicit stack: List[KernelHash]) extends Module {
    val io = IO(new Bundle { val in_<in0> = Input(FixedPoint(...)); …; val sigsIn = Input(InputKernelSignals(…)); val sigsOut = Output(…); val rr = Input(Bool()); })
    def <in0> = { io.in_<in0> }
    …
  }
  def connectWires0(module: <lhs>_module)(implicit stack): Unit = { … module.io.in_<in> <> <in> … }

  def kernel(): Unit = {
    Ledger.enter(this.hashCode, "<lhs>")
    implicit val stack = ControllerStack.stack.toList
    class <lhs>_concrete(depth: Int) extends <lhs>_module(depth) {
      io.sigsOut := DontCare
      val breakpoints = io.in_breakpoints; breakpoints := DontCare
      val instrctrs = io.in_instrctrs; instrctrs := DontCare
      val rr = io.rr
      // instr counters, iters/valids, actual body via gen(func)…
      val cycles_<lhs> = Module(new InstrumentationCounter())
      // the controller body itself (child kernel instantiations, reads/writes, etc)
    }
    val module = Module(new <lhs>_concrete(sm.p.depth)); module.io := DontCare
    connectWires0(module)
    Ledger.connectInstrCtrs(instrctrs, module.io.in_instrctrs)
    Ledger.connectBreakpoints(breakpoints, module.io.in_breakpoints)
    module.io.rr := rr
    module.io.sigsIn := me.sigsIn
    me.sigsOut := module.io.sigsOut
    Ledger.exit()
  }
}
```

## Open questions

1. `RemapSignal` has 29 objects but no use site found in the chiselgen directory. Is it consumed by Fringe, or by a non-chiselgen codegen? If unused, is it dead code?
2. `AppProperties` has 23 flags but only ~12 of them are set anywhere in chiselgen — what is the intended use of the rest (`HasGeneralFifo`, `HasVariableCtrBounds`, `HasVariableCtrStride`, `HasVariableCtrSyms`, `HasStaticCtr`, `HasFloats`, `HasLineBuffer`, `HasLUT`, `HasNBufRegFile`)? Are they monitored by a downstream reader?
3. The `javaStyleChunk` two-level path (hierarchyDepth=2) is implemented but the chunker TODO at line 157 says "More hierarchy? What if the block is > code_window^3 size?" — has any actual user app ever exceeded a single level in practice?
4. `enableModular` toggles whether kernel bodies are emitted as a separate `<lhs>_module`/`<lhs>_concrete` pair or inlined. What's the rationale for keeping both code paths? Is modular always better, and is the non-modular path legacy?
5. `SpatialCtrlBlackboxImpl` explicitly requires `enableModular` — this implies `enableModular` is actually required to compile blackbox-containing apps. If so, why is the non-modular path preserved at all?
6. `MergeBufferNew` doesn't use `splitAndCreate` — does that imply merge buffers never hit the JVM line-length limit in practice? Or is it a missing optimization?
7. The `bankingMode = "BankedMemory"` string at `ChiselGenMem.scala:166` is hard-coded with a `// TODO: Find correct one` — what are the other valid modes and why is the selection not exposed?
8. `FIFORegNew` read/write for `lhs.parent.s.get.isOuterControl` uses `~$break && $done` (see `ChiselGenMem.scala:41`) with an explicit comment "Don't know why this is the rule, but this is what works". What's the semantic justification?
9. `enableAsyncMem` flips to `!spatialConfig.enableAsyncMem && spatialConfig.enableRetiming` as the "retime" parameter to every memory constructor at `ChiselGenMem.scala:196`. Does the async-mem path lose retiming support for all memories?
10. The two-stream-limit `if (axiStreamIns.size > 1) error(…)` at `ChiselGenStream.scala:185-186` is explicitly marked as "easy to support more" — is this a hard RTL constraint or just plumbing?

## Distillation plan

- `10 - Overview.md` — composite case class, 13 traits, entry files, chunker, live-value detection, `createDump` mention.
- `20 - Types and Ports.md` — the 4-way `remap`/`port`/`arg`/`param` split, FixPt/FltPt/Vec/Struct/mem-interface cases, `enableModular` code shape.
- `30 - Memory Emission.md` — `ChiselGenMem` per-class cases, `splitAndCreate`, `ModuleParams.addParams`, banking parameters, `optimizedRegType` specialization.
- `40 - Controller Emission.md` — `writeKernelClass`, iter/valid emission, `_copy<c>` stream suffix, dispatch for each control construct.
- `50 - Streams and DRAM.md` — `ChiselGenDRAM`, `ChiselGenStream`, `connectDRAMStreams`, `getForwardPressure`/`getBackPressure`, AXI stream specifics.
- `60 - Math and Primitives.md` — `ChiselGenMath`, `ChiselGenDelay`, `ChiselGenStruct`, `ChiselGenVec`, `ChiselGenBlackbox`, `ChiselGenDebug`.

The `AppProperties`/`RemapSignal` content fits best in the Overview entry since it's cross-cutting.
