---
type: open-questions
topic: chiselgen
session: 2026-04-23
date_started: 2026-04-23
---

# Open Questions — Chiselgen Session

Questions raised while documenting the Chisel RTL backend. To be escalated to `20 - Open Questions.md` by the main session.

## Q-cgs-01 — `RemapSignal` is exported but unused inside chiselgen

`sealed trait RemapSignal` at `spatial/src/spatial/codegen/chiselgen/RemapSignal.scala:1-34` declares 29 case objects — 7 "Standard Signals" (`En`, `Done`, `BaseEn`, `Mask`, `Resetter`, `DatapathEn`, `CtrTrivial`) plus 22 "non-canonical signals" (`DoneCondition`, `IIDone`, `RstEn`, `CtrEn`, `Ready`, `Valid`, `NowValid`, `Inhibitor`, `Wren`, `Chain`, `Blank`, `DataOptions`, `ValidOptions`, `ReadyOptions`, `EnOptions`, `RVec`, `WVec`, `Latency`, `II`, `SM`, `Inhibit`, `Flow`). A grep for `RemapSignal` across the chiselgen subdirectory turns up no use sites — it is shipped but not consumed inside this directory.

**Spec question.** Is `RemapSignal` consumed by the Fringe template library, by scalagen, or by some other downstream codegen? If unused, is it dead code?

**Source.** `spatial/src/spatial/codegen/chiselgen/RemapSignal.scala`.

Status: open.

## Q-cgs-02 — Half of `AppProperties` flags are never registered

`AppProperties.scala:1-27` defines 23 case objects. Only ~12 are registered anywhere in chiselgen:

- `HasTileLoad`/`HasTileStore`/`HasAlignedLoad`/`HasUnalignedLoad`/`HasAlignedStore`/`HasUnalignedStore` (`ChiselGenInterface.scala:103-113`).
- `HasGather` (`ChiselGenInterface.scala:108`); `HasScatter` (`ChiselGenInterface.scala:116`).
- `HasBreakpoint` (`ChiselGenController.scala:399`).
- `HasFSM` (`ChiselGenController.scala:470`).
- `HasAccumSegmentation` (`ChiselGenMem.scala:74, 94`).
- `HasBroadcastRead` (`ChiselGenMem.scala:156`).
- `HasNBufSRAM` (`ChiselGenMem.scala:150`).
- `HasDephasedAccess` (`ChiselGenMem.scala:136`).

Never registered: `HasLineBuffer`, `HasNBufRegFile`, `HasGeneralFifo`, `HasLUT`, `HasStaticCtr`, `HasVariableCtrBounds`, `HasVariableCtrStride`, `HasFloats`, `HasVariableCtrSyms`.

**Spec question.** Are the unregistered flags reserved for future codegen or for an external reader? They are emitted as a comma-separated comment in `AccelWrapper.scala` — is something parsing that comment?

**Source.** `spatial/src/spatial/codegen/chiselgen/AppProperties.scala`, `ChiselGenController.scala:557`.

Status: open.

## Q-cgs-03 — Is the non-modular `enableModular = false` path legacy?

`spatialConfig.enableModular` toggles between two textual emission paths for every kernel: modular wraps controller bodies in `<lhs>_module`/`<lhs>_concrete` abstract+concrete classes; non-modular inlines the body directly. Both paths are maintained in `ChiselGenController.scala:138-243`. However, `SpatialCtrlBlackboxImpl` at `ChiselGenBlackbox.scala:242` throws if `enableModular` is false: `"Cannot generate a Ctrl blackbox without modular codegen enabled!"`.

**Spec question.** Is the non-modular path actively maintained or legacy? If any non-trivial app uses ctrl blackboxes, the non-modular path is effectively unusable — should it be deprecated and removed?

**Source.** `ChiselGenController.scala:138-243`, `ChiselGenBlackbox.scala:242`, `ChiselGenCommon.scala:107-110`.

Status: open.

## Q-cgs-04 — Hardcoded `bankingMode = "BankedMemory"`

`ChiselGenMem.scala:166`:

```scala
val bankingMode = "BankedMemory" // TODO: Find correct one
```

This string is embedded literally in every memory's `Module(new <Template>(…, $bankingMode, …))` call. The TODO suggests there are valid alternative modes that would be picked based on per-memory metadata, but the dispatch isn't implemented.

**Spec question.** What are the valid alternative `bankingMode` values? Are they semantically distinguishable from `"BankedMemory"`, or is this a vestigial parameter?

**Source.** `ChiselGenMem.scala:166`.

Status: open.

## Q-cgs-05 — Has the two-level `javaStyleChunk` been exercised?

`hierarchyDepth = (log(weight.sum max 1) / log(CODE_WINDOW)).toInt` at `ChiselCodegen.scala:114`. For `hierarchyDepth >= 2`, the chunker enters a two-level nested `Block<N>Chunker<M>Sub<K>` structure (`Codegen.scala:156-198`). The TODO at `Codegen.scala:157` says "More hierarchy? What if the block is > code_window^3 size?" — implying nobody has tried.

**Spec question.** Has any real Spatial app produced a body large enough to trigger `hierarchyDepth = 2`? If so, does the two-level lookup `block<N>chunk<M>sub<K>("<sym>")` actually work end-to-end, or are there latent bugs?

**Source.** `spatial/argon/src/argon/codegen/Codegen.scala:107-199`, `ChiselCodegen.scala:106-127`.

Status: open.

## Q-cgs-06 — `MergeBufferNew` doesn't use `splitAndCreate`

`splitAndCreate` at `ChiselGenMem.scala:19-38` chunks long memory access lists to avoid JVM line-length limits. It's used in `emitRead`/`emitWrite`/`emitReadInterface` for SRAMs/FIFOs/etc. but not for `MergeBufferBankedEnq` or `MergeBufferBankedDeq` (lines 350-371) — those just do `data.map{quote}.mkString("List[UInt](", ",", ")")` directly.

**Spec question.** Is the merge buffer guaranteed to never produce a list large enough to overflow the JVM line-length limit? Or is this a missing optimization that would crash on a sufficiently parallel merge buffer?

**Source.** `ChiselGenMem.scala:19-38`, `ChiselGenMem.scala:350-371`.

Status: open.

## Q-cgs-07 — `FIFORegNew` outer-controller read uses `~$break && $done`

`ChiselGenMem.scala:40-43`:

```scala
private def implicitEnableRead(lhs: Sym[_], mem: Sym[_]): String = {
  if (mem.isFIFOReg && lhs.parent.s.get.isOuterControl) src"~$break && $done"
  else                                                   src"""~$break && ${DL(src"$datapathEn & $iiIssue", lhs.fullDelay, true)}"""
}
```

The outer-FIFOReg read uses `done` instead of the standard `datapathEn & iiIssue` — with the comment `// Don't know why this is the rule, but this is what works`. The asymmetry suggests an interaction between FIFOReg's single-buffered semantics and outer-controller schedule semantics that's empirical rather than principled.

**Spec question.** What's the principled justification for this rule? Is it a workaround for a bug in another part of the pipeline?

**Source.** `ChiselGenMem.scala:40-43`.

Status: open.

## Q-cgs-08 — `getBackPressure` for `CtrlBlackboxUse` is commented out

`ChiselGenCommon.scala:266-279`:

```scala
def getBackPressure(sym: Ctrl): String = {
  if (sym.hasStreamAncestor || sym.isInBlackboxImpl) and(getWriteStreams(sym).collect{
    case fifo@Op(StreamOutNew(bus)) => src"$fifo.ready"
    case fifo@Op(FIFONew(_)) => src"(~$fifo.full.D(${sym.s.get.II}-1) | ~(${FIFOBackwardActive(sym, fifo)}))"
    case fifo@Op(FIFORegNew(_)) => src"(~$fifo.full.D(${sym.s.get.II}-1) | ~(${FIFOBackwardActive(sym, fifo)}))"
    case merge@Op(MergeBufferNew(_,_)) =>
      merge.writers.filter{ c => c.parent.s == sym.s }.head match {
        case enq@Op(MergeBufferBankedEnq(_, way, _, _)) =>
          src"~$merge.output.full($way).D(${sym.s.get.II}-1)"
      }
//      case bbox@Op(_:CtrlBlackboxUse[_,_]) => src"$bbox.getBackPressures(${getUsedFields(bbox, sym).map{x => s\"$x\"}}).D(${sym.s.get.II}-1)"
  }) else "true.B"
}
```

The blackbox case is commented out, while in `getForwardPressure` at line 255 it's active. This means a controlled blackbox can produce data with forward pressure but cannot back-pressure the kernel that contains it.

**Spec question.** Is this asymmetry intentional (a controlled blackbox produces data on demand and never has back-pressure to assert) or a missing implementation?

**Source.** `ChiselGenCommon.scala:266-279`.

Status: open.

## Q-cgs-09 — `enableAsyncMem` disables retiming for all memories

`ChiselGenMem.scala:196` passes `!spatialConfig.enableAsyncMem && spatialConfig.enableRetiming` as the retime parameter to every memory's `Module(new …)` call. So enabling async memories disables the retime-aware path for all memories, not just the async ones.

**Spec question.** Is this the intended trade-off (async memories require their own clock domain and the retime path is incompatible)? Or is this an accidental coupling?

**Source.** `ChiselGenMem.scala:196`.

Status: open.

## Q-cgs-10 — `lhs.II` forced to 1.0 for outer controllers

`ChiselGenController.scala:338`:

```scala
val ii = if (lhs.II <= 1 | !spatialConfig.enableRetiming | lhs.isOuterControl) 1.0 else scrubNoise(lhs.II)
```

Outer controllers always get II=1 in `createSMObject` regardless of what the IR's `lhs.II` field says.

**Spec question.** Is this a hard constraint (outer controllers can never have II>1 in current Spatial) or a default that overrides user intent silently?

**Source.** `ChiselGenController.scala:338`.

Status: open.

## Q-cgs-11 — 1-AxiStream-In / 1-AxiStream-Out hard limit

`ChiselGenStream.scala:185-186`:

```scala
if (axiStreamIns.size > 1) error(s"We currently only support up to 1 AxiStream In.  Its easy to support more, we just haven't implemented it yet. …")
if (axiStreamOuts.size > 1) error(s"We currently only support up to 1 AxiStream Out. …")
```

The error message acknowledges the limit is "easy to support more" — implying it's plumbing, not a fundamental constraint.

**Spec question.** What's the actual blocker? Is it a Fringe-template limitation (the `accelUnit.io.axiStreamsIn(N)` indexing) or a downstream test infrastructure constraint?

**Source.** `ChiselGenStream.scala:185-186`.

Status: open.

## Q-cgs-12 — Verilog blackbox requires `params: Map[String, chisel3.core.Param]`

`ChiselGenBlackbox.scala:48`:

```scala
open(src"class $bbName(params: Map[String, chisel3.core.Param]) extends BlackBox(params) {")
```

`chisel3.core.Param` is the Chisel-internal API for blackbox parameters. The `paramString` is built from the user's `BlackboxConfig.params` map (line 38) which can contain any Spatial value. The conversion is `s\""${param}" -> IntParam($value)\"` — assuming all params are integers.

**Spec question.** Does Spatial's blackbox API actually only support integer parameters? What about string parameters (Verilog `parameter STRING_NAME = "value"`) or floating-point (Verilog `real`)?

**Source.** `ChiselGenBlackbox.scala:38, 48`.

Status: open.

## Q-cgs-13 — `SpatialCtrlBlackboxImpl` requires `enableModular`

Already covered by Q-cgs-03 in part — same root question, narrower symptom.

**Source.** `ChiselGenBlackbox.scala:242`.

Status: open. Linked to Q-cgs-03.

## Q-cgs-14 — `FixRandom` uses a host-time-dependent seed

`ChiselGenMath.scala:155-168`:

```scala
val seed = (scala.math.random*1000).toInt
emit(src"""val ${lhs}_rng = Module(new PRNG($seed)); …""")
```

`scala.math.random` is the JVM's host-time-seeded RNG. Two compilations of the same Spatial app produce different bitstreams with different RNG sequences.

**Spec question.** Is the bitstream-time non-determinism intended (modeling a true random hardware source) or accidental? For a reproducible Rust port, this would need to be replaced with either a fixed seed or a user-controllable seed.

**Source.** `ChiselGenMath.scala:155-168`.

Status: open.

## Q-cgs-15 — Kernel-class constructor parameter limit (100)

`ChiselGenController.scala:163`:

```scala
inputs.filter(!_.isString).grouped(100).zipWithIndex.foreach{case (inpgrp, grpid) =>
  open(src"def connectWires$grpid(module: ${lhs}_module)(implicit stack: List[KernelHash]): Unit = {")
    …
}
```

Inputs are grouped by 100 to produce multiple `connectWires<i>` helpers. This suggests Scala/Chisel-elaboration has an issue with very large parameter lists; alternatively, the JVM bytecode method-size limit again.

**Spec question.** What's the actual blocker triggering this 100-parameter chunking? Is the limit verified, or is 100 a conservative default?

**Source.** `ChiselGenController.scala:163`.

Status: open.
