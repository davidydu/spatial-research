---
type: spec
concept: chiselgen-controller-emission
source_files:
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenController.scala:47-82"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenController.scala:84-100"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenController.scala:102-243"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenController.scala:250-330"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenController.scala:333-360"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenController.scala:362-493"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenController.scala:495-586"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenCommon.scala:72-87"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenCommon.scala:89-105"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenCommon.scala:190-206"
  - "spatial/src/spatial/codegen/chiselgen/ChiselCodegen.scala:91-104"
  - "spatial/src/spatial/codegen/chiselgen/ChiselCodegen.scala:106-127"
source_notes:
  - "[[chiselgen]]"
hls_status: chisel-specific
depends_on:
  - "[[10 - Overview]]"
  - "[[20 - Types and Ports]]"
status: draft
---

# Chiselgen — Controller Emission

## Summary

`ChiselGenController` emits one Scala file `sm_<lhs>.scala` per Spatial controller. Each file contains a `class <lhs>_kernel(<grouped inputs>, parent, cchain, …, rr) extends Kernel(…) { … def kernel(): <ret> = { … } }` where `kernel()` is invoked at the call site to elaborate the controller's body. Outer pipelines also emit a daisy-chain `RegChainPass` for each iterator/valid so that downstream pipeline stages can read the iter's stage-shifted value (`<iter>_chain_read_<port>`); outer-stream loops instead emit one cchain copy per child controller, named `<cchain>_copy<c>`. The dispatch at `gen(lhs, rhs)` covers `AccelScope`, `EnControl` (UnitPipe / UnrolledForeach / UnrolledReduce / ParallelPipe), `Switch`, `SwitchCase`, `StateMachine`, and lets `IfThenElse` and others fall through to other traits. `enterCtrl`/`exitCtrl` accumulate per-controller statistics and instrumentation counters into trait-level mutable state.

## Semantics

### Per-controller files: `sm_<lhs>.scala`

Each non-Accel controller produces a per-controller file via `writeKernelClass(lhs, ens, func*)(contents)` at `ChiselGenController.scala:102-243`. The file shape is:

```
package accel
class <lhs>_kernel(
  list_<in0>: List[FixedPoint],    // grouped by arg(tp, node) type
  list_<in1>: List[Bool],
  …                                // counter-chain copies emitted individually
  parent, cchain, childId, nMyChildren, ctrcopies, ctrPars, ctrWidths,
  breakpoints, instrctrs, rr
) extends Kernel(...) {
  val me = this
  val sm = Module(new <Level>(<RawSchedule>, <args>, latency = <lat>.toInt, myName = "<lhs>_sm"))
  val iiCtr = Module(new IICounter(<ii>.toInt, …, "<lhs>_iiCtr"))

  // (modular) abstract class <lhs>_module(depth: Int) extends Module {
  //   val io = IO(new Bundle { val in_<in> = …; val sigsIn = …; val sigsOut = …; val rr = … })
  //   def <in> = { io.in_<in> }
  // }
  // (modular) def connectWires0(module: <lhs>_module): Unit = { module.io.in_<in> <> <in> ; … }

  def kernel(): <ret> = {
    Ledger.enter(this.hashCode, "<lhs>")
    // (modular) class <lhs>_concrete(depth) extends <lhs>_module(depth) { … contents … }
    // body emitted via gen(func)
  }
}
```

The `<lhs>_module`/`<lhs>_concrete` split is gated by `spatialConfig.enableModular` (see `[[20 - Types and Ports]]`). Kernel constructor params come from `getInputs(lhs, func*)` at `ChiselGenCommon.scala:89-101` — the transitive input closure: `lhs.nonBlockInputs ++ block.nestedInputs ++ lhs.readMems` minus counter-chain syms minus blackbox-impl bounds, plus stream mems if `hasStreamAncestor`, plus `bufMapping(lhs)`.

`groupInputs(inss)` at `ChiselGenCommon.scala:103-105` groups by `arg(tp, node)` so each type kind becomes one `list_<in>: List[<type>]` parameter — *except* counter-chain copies, which are unrolled per-child via `cchainCopies.contains(ins.head)`. The constructor emission at `ChiselGenController.scala:127-130` walks the grouped map and emits either `list_<in>: List[<typ>],` or per-copy `<in>_copy<c>: <typ>,`. After the constructor, the body unpacks each non-cchain group with positional `val <in> = list_<in>(<i>)` (lines 180-182).

### Iter and valid emission for outer pipelines

`emitItersAndValids(lhs)` at `ChiselGenController.scala:47-82` emits one `val <iter> = $cchainOutput.counts(<id>).FP(true, <w>, 0)` per iterator and `val <v> = ~$cchainOutput.oobs(<id>)` per valid, with `w` the counter's typeArg width.

For outer pipelines with multiple children (`lhs.isOuterPipeLoop && lhs.children.count(_.s.get != lhs) > 1`), each iter and valid is wrapped in a `Module(new RegChainPass(nChildren, w, myName = "<iter>_chain"))` and `chain_pass`'d through `io.sigsOut.smDoneIn.head` (lines 60-66). `regchainsMapping` is populated so `connectChains` later emits `<iter>_chain.connectStageCtrl(<lhs.done>, <lhs.baseEn>, port)` (lines 40-45). Children with `port > 0` reach the iter via `<iter>_chain_read_<port>` — the `appendSuffix` rewrite at `ChiselGenCommon.scala:302-322` translates a bound iter ref to the chained version when the parent is an `OuterPipeLoop`.

### Stream-controller `_copy<c>` counter chain suffix

`emitItersAndValidsStream(lhs)` at lines 84-100 is the analogous emission for `lhs.isOuterStreamLoop` (no daisy chain — each child gets its own counter copy):

```scala
forEachChild(lhs){case (c, ii) =>
  iters.zipWithIndex.foreach{ case (iter, id) =>
    emit(src"val ${iter}_copy$c = ${cchainCopyOutput(ii)}.counts($id).FP(true, $w, 0)")
  }
  valids.zipWithIndex.foreach{ case (v,id) =>
    emit(src"val ${v}_copy$c = ~${cchainCopyOutput(ii)}.oobs($id)")
  }
}
```

The `cchainCopies` map (populated by `markCChainObjects(b)` at `ChiselCodegen.scala:100-104`) tracks which counter chains belong to outer-stream loops. `markCChainObjects` walks every block at the top of `gen(b)` (line 108) and, for each counter chain whose owner is an outer stream loop, registers each child as an "owner" of a copy: `cchainCopies += (x -> { existingList ++ List(c) })`.

This propagates downstream to `getForwardPressure`, `groupInputs`, the kernel-class constructor, and the `arg`/`port` remappers — anywhere that asks for a counter chain in this shape gets the `_copy<c>` per-child variant. `quoteCChainCopy(cchain, copy)` at `ChiselGenController.scala:245-248` produces the per-copy string, falling back to the chunk map if the copy is registered in `scoped`.

### `instantiateKernel` and the call site

`instantiateKernel(lhs, ens, func*)(modifications)` at lines 250-330 emits the kernel construction at the parent's call site (not inside the per-controller file). The structure: `val <lhs>_obj = new <lhs>_kernel(<chainPassedInputs>, params, parent, cchain, childId, …, rr)`, then a caller-supplied `modifications` block, `sm.io.ctrDone` wiring, `connectChains(lhs)`, `backpressure`/`forwardpressure := getBackPressure | sm.io.doneLatch`, `sm.io.break`, `mask := <noop> & <parentMask>`, and `<lhs>_obj.configure(...)` followed by `<lhs>_obj.kernel()`.

The `_obj` suffix is appended for branches (Switch / SwitchCase / StateMachine), empty otherwise (line 254). The `ctrDone` wiring at lines 279-300 dispatches by control kind:

- Has counter chain, not outer-stream → `DL($lhs$swobj.cchain.head.output.done, 1, isBit = true)`.
- Inner SwitchCase / StateMachine with children → `<headChild>.done`.
- Switch → not assigned (replaced with `doneIn(#)` at SM template level).
- Inner StateMachine with no children → `$lhs$swobj.iiDone`.
- Otherwise → `risingEdge($lhs$swobj.sm.io.ctrInc)`.

`<chainPassedInputs>` (lines 257-260) is the call-site argument list. Each non-cchain group becomes a `List(<x>, <y>, …)` literal; each cchain group becomes individual `<copy0>, <copy1>, …` strings produced by `quoteCChainCopy`.

### `createSMObject(lhs)` — sm + iiCtr instantiation

`createSMObject(lhs)` at lines 333-360 emits `val me = this`, `val sm = Module(new <Level>(<RawSchedule>, <constrArg> <stw> <isPassthrough> <ncases>, latency = $lat.toInt, myName = "<lhs>_sm"))`, and `val iiCtr = Module(new IICounter($ii.toInt, …, "<lhs>_iiCtr"))`. `lhs.level.toString` is `"InnerControl"` or `"OuterControl"`; `lhs.rawSchedule.toString` is `"Sequenced"`, `"Pipelined"`, `"Streaming"`, or `"ForkJoin"`. `constrArg` is `${lhs.isFSM}` for inner, `${nChildren}, isFSM = ${lhs.isFSM}` for outer. `stw` is the state-bit-width of a `StateMachine`'s `notDone` block. `isPassthrough` is set for inner switches and switch-cases. `lat = if (enableRetiming && isInnerControl) scrubNoise(lhs.bodyLatency.sum) else 0.0`. `ii = if (lhs.II <= 1 || !enableRetiming || lhs.isOuterControl) 1.0 else scrubNoise(lhs.II)` — outer controllers are forced to II=1 (Q-cgs-10).

### `enterCtrl` / `exitCtrl` and instrumentation

`enterCtrl(lhs)` at `ChiselGenCommon.scala:72-82` is called at the top of every controller's dispatch case (before `instantiateKernel` and `writeKernelClass`). It pushes `lhs` onto `controllerStack`, resets `ensigs` (the per-controller dedup table for enable signal strings — see `ChiselGenMath`), and if `enableInstrumentation && inHw` appends `(lhs, controllerStack.length)` to `instrumentCounters`. It also updates `widthStats` (for outer) or `depthStats` (for inner). `exitCtrl(lhs)` at lines 84-87 just pops the stack.

`createAndTieInstrs(lhs)` at lines 190-206 emits per-kernel `Module(new InstrumentationCounter())` instances for `cycles_<lhs>` and `iters_<lhs>`, plus `stalls_<lhs>` and `idles_<lhs>` if `hasBackPressure || hasForwardPressure`. The four counters are then registered with `Ledger.tieInstrCtr(instrctrs.toList, <LHS>_instrctr, cycles, iters, stalls, idles)` (or `0.U, 0.U` for the last two if no pressure).

### The dispatch in `gen(lhs, rhs)`

`ChiselGenController.scala:362-493`:

- **AccelScope** (363-413): root case. Walks `RemoteMemories.all` for `DRAMAccelNew` allocators, emits `DRAMAllocator(dim, reqCount)` for each, calls `connectDRAMStreams(x)`. Then `inAccel{ … }`: emits the `retime_counter` (whose `.output.done` becomes `rr`), `breakpoints` Vec, `instrctrs` list, `done_latch` SRFF. Calls `instantiateKernel`/`writeKernelClass`. Wires `done_latch` to `done | breakpoints.reduce{_|_}` if any early exits exist (registers `HasBreakpoint`).
- **EnControl** (415-421): generic path for UnitPipe / UnrolledForeach / UnrolledReduce / ParallelPipe. Just `enterCtrl`, `instantiateKernel`, `writeKernelClass`, `exitCtrl`.
- **Switch** (424-449): `selects` wired into `<lhs>_obj.sm.io.selectsIn(i)`; outer switches latch selects in `RegInit(false.B)` so the body can mutate the condition without changing selection. The body emits Mux1H over case-results if the switch returns bits.
- **SwitchCase** (452-467): inner switch cases override `baseEn := io.sigsIn.smSelectsOut(<obj>.childId)`. The body calls `gen(body)` and (if returning bits) wires `io.ret.r := <body.result>.r`.
- **StateMachine** (469-486): registers `HasFSM`. `notDone.input` becomes `state`, initialized from `io.sigsIn.smState.r`. Sequentially `gen(notDone)`, `gen(action)`, `gen(nState)`, then wires `nextState := nState.result.r.asSInt`, `initState := start.r.asSInt`, `doneCondition := ~notDone.result`.
- **SeriesForeach** (488-489): just unwraps to `gen(blk)`.

### `markCChainObjects(b)` — the cchain-copy registry

`markCChainObjects(b)` at `ChiselCodegen.scala:100-104` walks the block at the top of `gen(b)`:

```scala
b.stms.collect{case x if (x.isCounterChain && x.getOwner.isDefined && x.owner.isOuterStreamLoop) =>
  forEachChild(x.owner){case (c, _) =>
    cchainCopies += (x -> {cchainCopies.getOrElse(x, List()) ++ List(c)})
  }
}
```

Every counter chain owned by an outer-stream loop registers each of its children as a copy owner. The `cchainCopies` map persists for the rest of the block traversal (and downstream blocks), so subsequent emission knows to fan out the chain into per-child copies.

### `emitPostMain` — postscripts to entry files

`emitPostMain` at lines 495-586:

- **`Instrument.scala`** (497-535): a single object with `def connect(accelUnit, instrctrs)` that wires every instrumented controller's cycles/iters (and stalls/idles if applicable) to its allocated `argOuts(api.<sym>_cycles_arg)`. The body is chunked via `javaStyleChunk` because there can be hundreds of these wirings.
- **`Instantiator.scala`** (537-548): emits `numArgOuts_instr`, `numCtrls`, `numArgOuts_breakpts`, plus a `/* Breakpoint Contexts */` comment with each early-exit's source context.
- **`AccelWrapper.scala`** (550-583): emits widths/depths comment lines (`widthStats.sorted`, `depthStats.sorted`), the `App Characteristics` line listing `appPropertyStats`, `max_latency = $maxretime`, and a stack of target-latency settings via `latencyOption("FixMul", Some(1))` etc., plus `globals.target.cheapSRAMs`, `globals.target.SramThreshold`, `globals.retime`, `globals.enableModular`. These let the runtime Fringe templates parameterize themselves.

## Interactions

- **Reads** control metadata (`isInnerControl`, `isOuterControl`, `isBranch`, `isOuterStreamLoop`, `isOuterPipeLoop`, `rawSchedule`, `level`, `parent`, `children`, `siblings`).
- **Reads** retiming metadata (`bodyLatency`, `II`, `compilerII`, `fullDelay`).
- **Reads** banking metadata indirectly via `bufMapping` and `regchainsMapping` populated during `emitItersAndValids` and `emitMem`.
- **Writes** `controllerStack`, `ensigs`, `instrumentCounters`, `widthStats`, `depthStats`, `appPropertyStats`, `bufMapping`, `regchainsMapping`, `cchainCopies`, `earlyExits`.
- **Pairs with** `ChiselGenMem` for `bufMapping` (NBuffered swappers) and `regchainsMapping` (iter chains) — `connectBufs(lhs)` and `connectChains(lhs)` at lines 35-45 emit the `connectStageCtrl` calls that wire pipeline-stage control to the appropriate buffer port.

## HLS notes

The one-class-per-controller pattern is a Chisel-elaboration constraint, not a fundamental DSL property. An HLS port can collapse the kernel/module/concrete tier into a single function and still preserve the control-flow semantics: `sm.io.ctrDone` is a per-controller boolean, `getBackPressure`/`getForwardPressure` is per-controller, `bufMapping`/`regchainsMapping` is per-controller. The stream-controller `_copy<c>` fan-out is essentially a static unrolling of a parameterized counter chain — in HLS this can either stay as a fan-out at instantiation time or become a runtime-indexed counter array.

## Open questions

See `20 - Research Notes/10 - Deep Dives/open-questions-chiselgen.md`:
- Q-cgs-05: Is the two-level chunker (`hierarchyDepth = 2`) ever triggered on real apps? Has the dispatch-list lookup `block<N>chunk<M>sub<K>` been exercised?
- Q-cgs-10: `lhs.II` is forced to 1.0 for outer controllers in `createSMObject` (line 338). Is that a hard constraint or just a default?
