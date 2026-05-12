---
type: open-questions
project: spatial-spec
date_started: 2026-04-21
---

# Open Questions

Unresolved issues encountered during research. IDs are zero-padded and stable.

## Format

```markdown
## Q-NNN — [YYYY-MM-DD] Short title

Description of the question.

Source: <file path>
Blocked by: <Q-ID or —>
Status: needs-architectural-decision | out-of-scope-for-v1 | minor-fix-pending | resolved-by-spec - <date> via [[entry-name]]
Decision criteria: (required only for needs-architectural-decision)
Resolution: (optional notes / audit trail)
```

## Status vocabulary

- `needs-architectural-decision` — load-bearing Rust+HLS semantic or architecture decision requiring human input
- `out-of-scope-for-v1` — real issue explicitly deferred past the v1 Rust+HLS port
- `minor-fix-pending` — documentation or small spec cleanup that does not block architecture
- `resolved-by-spec - <date> via [[entry-name]]` — answered by an existing spec entry

---

## Triage summary (2026-04-25)

- needs-architectural-decision: 25 questions
- out-of-scope-for-v1: 86 questions
- minor-fix-pending: 30 questions
- resolved-by-spec: 23 questions
- Total: 164

The `needs-architectural-decision` set is the user-action queue: each one requires explicit human input before the corresponding rewrite work can proceed. See [[40 - Open HLS Questions]] for cross-referenced HLS architecture questions.

## Q-001 — [2026-04-21] SimpleScheduler DCE range + missed guard (argon-coverage)

`argon-coverage.md` §6 cites `SimpleScheduler.scala:20-31` for the idempotent-only DCE, but the actual code is at lines 22-30 and has an additional guard `s != result` that the note omits. Not behaviorally wrong, but the prose implies DCE can drop the result symbol, which isn't what the code does.

Source: `argon/src/argon/schedule/SimpleScheduler.scala:22-30`
Blocked by: —
Status: resolved-by-spec - 2026-04-25 via [[60 - Scopes and Scheduling]]
Resolution: Updated argon-coverage.md §6 to cite lines 22-30 and note the `s != result` guard.

## Q-002 — [2026-04-21] Pipeline description omits passes between DSE and memoryDealiasing (spatial-lang-coverage)

`spatial-lang-coverage.md` §6 shows the pipeline as `blackboxLowering1/2 → DSE → memoryDealiasing → pipeInserter`. Actual pipeline (`Spatial.scala:164-253`) inserts a second `switchTransformer`/`switchOptimizer` pair plus `laneStaticTransformer` between DSE and `memoryDealiasing`. The `spatial-passes-coverage.md` §8 canonical-order list is correct; the `spatial-lang-coverage.md` summary is abbreviated.

Source: `src/spatial/Spatial.scala:164-253`
Blocked by: —
Status: resolved-by-spec - 2026-04-25 via [[00 - Pass Pipeline Index]]
Resolution: Inserted the second `switchTransformer`/`switchOptimizer` pair and `laneStaticTransformer` step into spatial-lang-coverage.md §6; added cross-reference to spatial-passes-coverage §8 for the canonical enumeration.

## Q-003 — [2026-04-21] RemapSignal object count off by 2 (codegen-fpga-host-coverage)

`codegen-fpga-host-coverage.md` says `RemapSignal` has 27 objects; actual count is 29. Missing from the note's enumeration: `CtrTrivial`, `RstEn`, `CtrEn`, `NowValid`, `Inhibitor`, `Wren`, `Chain`, `Blank`, `DataOptions`, `ValidOptions`, `ReadyOptions`, `EnOptions`, `RVec`, `WVec`, `Latency`.

Source: `src/spatial/codegen/chiselgen/RemapSignal.scala`
Blocked by: —
Status: resolved-by-spec - 2026-04-25 via [[20 - Types and Ports]]
Resolution: Corrected count to 29 in both the file inventory and key-types sections of codegen-fpga-host-coverage.md; added the missing object names to the listing.

## Q-004 — [2026-04-21] MemoryUnrolling "29k" size claim misleading (spatial-passes-coverage)

`spatial-passes-coverage.md` §2 calls `MemoryUnrolling` the "Largest unroller (29k)". "29k" has no unit and is inconsistent with adjacent line-count entries. Actual: 581 lines / ~16 KB. Either the unit was bytes (doesn't match ~16 KB) or a stale figure from an older file version.

Source: `src/spatial/transform/unrolling/MemoryUnrolling.scala`
Blocked by: —
Status: resolved-by-spec - 2026-04-25 via [[80 - Unrolling]]
Resolution: Changed "(29k)" to "(581 lines)" in spatial-passes-coverage.md §2.

## Q-005 — [2026-04-21] MemoryResource.minDepth is not abstract (hardware-targets-coverage)

`hardware-targets-coverage.md` §3 says `MemoryResource(name)` has "three abstract members: `area`, `summary`, `minDepth`". Actually `minDepth` has a concrete default `def minDepth: Int = 0` at `MemoryResource.scala:9`. Only `area` and `summary` are abstract.

Source: `spatial/src/spatial/targets/MemoryResource.scala:6-10`
Blocked by: —
Status: resolved-by-spec - 2026-04-25 via [[50 - Memory Resources]]
Resolution: Clarified hardware-targets-coverage.md §3 to distinguish the two abstract members from the concrete-default `minDepth`.

## Q-006 — [2026-04-21] 2 spot-check subagents rate-limited; manual 3-claim spot-checks performed

During Task 6 (Phase 1 content spot-checks), 2 of 10 subagents failed with "out of extra usage" rate-limit errors: `codegen-sim-alt` and `poly-models-dse`. Main session manually spot-checked 3 claims each from these notes — all 6 claims verified ✓. Remaining 8 subagents completed with ACCEPT verdicts (0-1 minor fails each; none contradicted architectural claims).

Source: Phase 1 execution log
Blocked by: —
Status: out-of-scope-for-v1
Resolution: Manual 3-claim verification recorded; fuller 5-claim subagent spot-checks can be re-run after token budget resets if desired.

## Consolidated Phase 2 Questions

## Q-007 — [2026-04-25] RepeatedTraversal uses the original block for inner pass runs (originally Q-arg-001)

Original ID: Q-arg-001
Original file: `open-questions-argon-supplemental.md`

`RepeatedTraversal.process` carries `var blk = block`, but each wrapped pass is invoked as `pass.run(block)` rather than `pass.run(blk)`. If any wrapped pass transforms the block, the next pass appears to receive the original input instead of the accumulated result.

Source: argon/src/argon/passes/RepeatedTraversal.scala:27-40
Blocked by: Need maintainer intent for repeated traversal fixed-point semantics.
Status: out-of-scope-for-v1
Resolution:

## Q-008 — [2026-04-25] Codegen chunking depth and backend size limits (originally Q-arg-002)

Original ID: Q-arg-002
Original file: `open-questions-argon-supplemental.md`

`javaStyleChunk` implements direct emission, one-level chunking, and a two-level fallback, then comments on the unimplemented case where a block exceeds `code_window * code_window * code_window`. Need to identify the real backend compiler limit and whether any current generated blocks can exceed the implemented hierarchy.

Source: argon/src/argon/codegen/Codegen.scala:156-158
Blocked by: Backend-specific codegen usage and generated-file size examples.
Status: out-of-scope-for-v1
Resolution:

## Q-009 — [2026-04-25] Flt-to-Fix saturating and unbiased conversions share the same node (originally Q-arg-003)

Original ID: Q-arg-003
Original file: `open-questions-argon-supplemental.md`

`Flt.__toFix`, `Flt.__toFixSat`, `Flt.__toFixUnb`, and `Flt.__toFixUnbSat` all stage `FltToFix` with the target `FixFmt`. Need to know whether saturation and unbiased rounding are intentionally no-ops for floating-to-fixed conversion or whether distinct nodes were omitted.

Source: argon/src/argon/lang/Flt.scala:109-119
Blocked by: Numeric conversion semantics expected by Spatial users.
Status: minor-fix-pending
Resolution:

## Q-010 — [2026-04-25] Dynamic Vec indexing falls back to index zero (originally Q-arg-004)

Original ID: Q-arg-004
Original file: `open-questions-argon-supplemental.md`

`Vec.apply(i: I32)` uses the constant index when `i` is a `Const`, but otherwise calls `this.apply(0)`. Need to know whether dynamic vector indexing is deliberately unsupported in Argon or whether a dynamic `VecApply` variant should exist.

Source: argon/src/argon/lang/Vec.scala:59-63
Blocked by: Backend support expectations for dynamic vector indexing.
Status: out-of-scope-for-v1
Resolution:

## Q-011 — [2026-04-23] `RemapSignal` is exported but unused inside chiselgen (originally Q-cgs-01)

Original ID: Q-cgs-01
Original file: `open-questions-chiselgen.md`

`sealed trait RemapSignal` at `spatial/src/spatial/codegen/chiselgen/RemapSignal.scala:1-34` declares 29 case objects — 7 "Standard Signals" (`En`, `Done`, `BaseEn`, `Mask`, `Resetter`, `DatapathEn`, `CtrTrivial`) plus 22 "non-canonical signals" (`DoneCondition`, `IIDone`, `RstEn`, `CtrEn`, `Ready`, `Valid`, `NowValid`, `Inhibitor`, `Wren`, `Chain`, `Blank`, `DataOptions`, `ValidOptions`, `ReadyOptions`, `EnOptions`, `RVec`, `WVec`, `Latency`, `II`, `SM`, `Inhibit`, `Flow`). A grep for `RemapSignal` across the chiselgen subdirectory turns up no use sites — it is shipped but not consumed inside this directory.

**Spec question.** Is `RemapSignal` consumed by the Fringe template library, by scalagen, or by some other downstream codegen? If unused, is it dead code?

**Source.** `spatial/src/spatial/codegen/chiselgen/RemapSignal.scala`.

Status: out-of-scope-for-v1

## Q-012 — [2026-04-23] Half of `AppProperties` flags are never registered (originally Q-cgs-02)

Original ID: Q-cgs-02
Original file: `open-questions-chiselgen.md`

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

Status: out-of-scope-for-v1

## Q-013 — [2026-04-23] Is the non-modular `enableModular = false` path legacy? (originally Q-cgs-03)

Original ID: Q-cgs-03
Original file: `open-questions-chiselgen.md`

`spatialConfig.enableModular` toggles between two textual emission paths for every kernel: modular wraps controller bodies in `<lhs>_module`/`<lhs>_concrete` abstract+concrete classes; non-modular inlines the body directly. Both paths are maintained in `ChiselGenController.scala:138-243`. However, `SpatialCtrlBlackboxImpl` at `ChiselGenBlackbox.scala:242` throws if `enableModular` is false: `"Cannot generate a Ctrl blackbox without modular codegen enabled!"`.

**Spec question.** Is the non-modular path actively maintained or legacy? If any non-trivial app uses ctrl blackboxes, the non-modular path is effectively unusable — should it be deprecated and removed?

**Source.** `ChiselGenController.scala:138-243`, `ChiselGenBlackbox.scala:242`, `ChiselGenCommon.scala:107-110`.

Status: out-of-scope-for-v1

## Q-014 — [2026-04-23] Hardcoded `bankingMode = "BankedMemory"` (originally Q-cgs-04)

Original ID: Q-cgs-04
Original file: `open-questions-chiselgen.md`

`ChiselGenMem.scala:166`:

```scala
val bankingMode = "BankedMemory" // TODO: Find correct one
```

This string is embedded literally in every memory's `Module(new <Template>(…, $bankingMode, …))` call. The TODO suggests there are valid alternative modes that would be picked based on per-memory metadata, but the dispatch isn't implemented.

**Spec question.** What are the valid alternative `bankingMode` values? Are they semantically distinguishable from `"BankedMemory"`, or is this a vestigial parameter?

**Source.** `ChiselGenMem.scala:166`.

Status: out-of-scope-for-v1

## Q-015 — [2026-04-23] Has the two-level `javaStyleChunk` been exercised? (originally Q-cgs-05)

Original ID: Q-cgs-05
Original file: `open-questions-chiselgen.md`

`hierarchyDepth = (log(weight.sum max 1) / log(CODE_WINDOW)).toInt` at `ChiselCodegen.scala:114`. For `hierarchyDepth >= 2`, the chunker enters a two-level nested `Block<N>Chunker<M>Sub<K>` structure (`Codegen.scala:156-198`). The TODO at `Codegen.scala:157` says "More hierarchy? What if the block is > code_window^3 size?" — implying nobody has tried.

**Spec question.** Has any real Spatial app produced a body large enough to trigger `hierarchyDepth = 2`? If so, does the two-level lookup `block<N>chunk<M>sub<K>("<sym>")` actually work end-to-end, or are there latent bugs?

**Source.** `spatial/argon/src/argon/codegen/Codegen.scala:107-199`, `ChiselCodegen.scala:106-127`.

Status: out-of-scope-for-v1

## Q-016 — [2026-04-23] `MergeBufferNew` doesn't use `splitAndCreate` (originally Q-cgs-06)

Original ID: Q-cgs-06
Original file: `open-questions-chiselgen.md`

`splitAndCreate` at `ChiselGenMem.scala:19-38` chunks long memory access lists to avoid JVM line-length limits. It's used in `emitRead`/`emitWrite`/`emitReadInterface` for SRAMs/FIFOs/etc. but not for `MergeBufferBankedEnq` or `MergeBufferBankedDeq` (lines 350-371) — those just do `data.map{quote}.mkString("List[UInt](", ",", ")")` directly.

**Spec question.** Is the merge buffer guaranteed to never produce a list large enough to overflow the JVM line-length limit? Or is this a missing optimization that would crash on a sufficiently parallel merge buffer?

**Source.** `ChiselGenMem.scala:19-38`, `ChiselGenMem.scala:350-371`.

Status: out-of-scope-for-v1

## Q-017 — [2026-04-23] `FIFORegNew` outer-controller read uses `~$break && $done` (originally Q-cgs-07)

Original ID: Q-cgs-07
Original file: `open-questions-chiselgen.md`

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

Status: out-of-scope-for-v1

## Q-018 — [2026-04-23] `getBackPressure` for `CtrlBlackboxUse` is commented out (originally Q-cgs-08)

Original ID: Q-cgs-08
Original file: `open-questions-chiselgen.md`

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

Status: out-of-scope-for-v1

## Q-019 — [2026-04-23] `enableAsyncMem` disables retiming for all memories (originally Q-cgs-09)

Original ID: Q-cgs-09
Original file: `open-questions-chiselgen.md`

`ChiselGenMem.scala:196` passes `!spatialConfig.enableAsyncMem && spatialConfig.enableRetiming` as the retime parameter to every memory's `Module(new …)` call. So enabling async memories disables the retime-aware path for all memories, not just the async ones.

**Spec question.** Is this the intended trade-off (async memories require their own clock domain and the retime path is incompatible)? Or is this an accidental coupling?

**Source.** `ChiselGenMem.scala:196`.

Status: out-of-scope-for-v1

## Q-020 — [2026-04-23] `lhs.II` forced to 1.0 for outer controllers (originally Q-cgs-10)

Original ID: Q-cgs-10
Original file: `open-questions-chiselgen.md`

`ChiselGenController.scala:338`:

```scala
val ii = if (lhs.II <= 1 | !spatialConfig.enableRetiming | lhs.isOuterControl) 1.0 else scrubNoise(lhs.II)
```

Outer controllers always get II=1 in `createSMObject` regardless of what the IR's `lhs.II` field says.

**Spec question.** Is this a hard constraint (outer controllers can never have II>1 in current Spatial) or a default that overrides user intent silently?

**Source.** `ChiselGenController.scala:338`.

Status: resolved-by-spec - 2026-04-25 via [[40 - Controller Emission]]

## Q-021 — [2026-04-23] 1-AxiStream-In / 1-AxiStream-Out hard limit (originally Q-cgs-11)

Original ID: Q-cgs-11
Original file: `open-questions-chiselgen.md`

`ChiselGenStream.scala:185-186`:

```scala
if (axiStreamIns.size > 1) error(s"We currently only support up to 1 AxiStream In.  Its easy to support more, we just haven't implemented it yet. …")
if (axiStreamOuts.size > 1) error(s"We currently only support up to 1 AxiStream Out. …")
```

The error message acknowledges the limit is "easy to support more" — implying it's plumbing, not a fundamental constraint.

**Spec question.** What's the actual blocker? Is it a Fringe-template limitation (the `accelUnit.io.axiStreamsIn(N)` indexing) or a downstream test infrastructure constraint?

**Source.** `ChiselGenStream.scala:185-186`.

Status: out-of-scope-for-v1

## Q-022 — [2026-04-23] Verilog blackbox requires `params: Map[String, chisel3.core.Param]` (originally Q-cgs-12)

Original ID: Q-cgs-12
Original file: `open-questions-chiselgen.md`

`ChiselGenBlackbox.scala:48`:

```scala
open(src"class $bbName(params: Map[String, chisel3.core.Param]) extends BlackBox(params) {")
```

`chisel3.core.Param` is the Chisel-internal API for blackbox parameters. The `paramString` is built from the user's `BlackboxConfig.params` map (line 38) which can contain any Spatial value. The conversion is `s\""${param}" -> IntParam($value)\"` — assuming all params are integers.

**Spec question.** Does Spatial's blackbox API actually only support integer parameters? What about string parameters (Verilog `parameter STRING_NAME = "value"`) or floating-point (Verilog `real`)?

**Source.** `ChiselGenBlackbox.scala:38, 48`.

Status: out-of-scope-for-v1

## Q-023 — [2026-04-23] `SpatialCtrlBlackboxImpl` requires `enableModular` (originally Q-cgs-13)

Original ID: Q-cgs-13
Original file: `open-questions-chiselgen.md`

Already covered by Q-cgs-03 in part — same root question, narrower symptom.

**Source.** `ChiselGenBlackbox.scala:242`.

Status: out-of-scope-for-v1

## Q-024 — [2026-04-23] `FixRandom` uses a host-time-dependent seed (originally Q-cgs-14)

Original ID: Q-cgs-14
Original file: `open-questions-chiselgen.md`

`ChiselGenMath.scala:155-168`:

```scala
val seed = (scala.math.random*1000).toInt
emit(src"""val ${lhs}_rng = Module(new PRNG($seed)); …""")
```

`scala.math.random` is the JVM's host-time-seeded RNG. Two compilations of the same Spatial app produce different bitstreams with different RNG sequences.

**Spec question.** Is the bitstream-time non-determinism intended (modeling a true random hardware source) or accidental? For a reproducible Rust port, this would need to be replaced with either a fixed seed or a user-controllable seed.

**Source.** `ChiselGenMath.scala:155-168`.

Status: out-of-scope-for-v1

## Q-025 — [2026-04-23] Kernel-class constructor parameter limit (100) (originally Q-cgs-15)

Original ID: Q-cgs-15
Original file: `open-questions-chiselgen.md`

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

Status: out-of-scope-for-v1

## Q-026 — [2026-04-25] Base-cycle consumer for compiler targets (originally Q-ft-01)

Original ID: Q-ft-01
Original file: `open-questions-fringe-targets.md`

`HardwareTarget` defines `baseCycles = 43000`, but the source pass for target specs did not identify a consumer. Need verify whether this startup-cycle constant still affects DSE/reporting or is dead compatibility state.

Source: src/spatial/targets/HardwareTarget.scala:17-18
Blocked by: target latency-model audit
Status: out-of-scope-for-v1
Resolution:

## Q-027 — [2026-04-25] magPipelineDepth consumer (originally Q-ft-02)

Original ID: Q-ft-02
Original file: `open-questions-fringe-targets.md`

`DeviceTarget.magPipelineDepth` is exposed through `globals.magPipelineDepth`, and `MAGToAXI4Bridge` reads it into `numPipelinedLevels`, but the bridge body does not use that value afterward. Need decide whether this was intended to insert AXI retiming and whether HLS should ignore or revive it.

Source: fringe/src/fringe/targets/DeviceTarget.scala:18; fringe/src/fringe/globals.scala:15-16; fringe/src/fringe/templates/axi4/MAGToAXI4Bridge.scala:20
Blocked by: AXI timing design
Status: out-of-scope-for-v1
Resolution:

## Q-028 — [2026-04-25] AdvancedColored channel assignment status (originally Q-ft-03)

Original ID: Q-ft-03
Original file: `open-questions-fringe-targets.md`

`AdvancedColored` claims to account for transfer intensity but has a TODO and currently returns the same round-robin assignment shape as `BasicRoundRobin`. Need verify whether any compiler path selects it and whether HLS channel assignment should include the intended advanced policy.

Source: fringe/src/fringe/ChannelAssignment.scala:30-34
Blocked by: channel-assignment selector audit
Status: out-of-scope-for-v1
Resolution:

## Q-029 — [2026-04-25] argOutLoopbacksMap ownership (originally Q-ft-04)

Original ID: Q-ft-04
Original file: `open-questions-fringe-targets.md`

`globals.argOutLoopbacksMap` is counted by `NUM_ARG_LOOPS` but the source pass did not find the writer or runtime semantics. Need identify whether it affects scalar echo/loopback behavior before redesigning the host ABI.

Source: fringe/src/fringe/globals.scala:47-78
Blocked by: chiselgen scalar-layout audit
Status: out-of-scope-for-v1
Resolution:

## Q-030 — [2026-04-25] ASIC latency model source (originally Q-ft-05)

Original ID: Q-ft-05
Original file: `open-questions-fringe-targets.md`

The compiler-side `ASIC` target uses `GenericAreaModel` but constructs its latency model from `xilinx.Zynq`. Need decide whether this is intentional reuse, placeholder behavior, or a bug before deriving HLS/ASIC latency defaults.

Source: src/spatial/targets/generic/ASIC.scala:8-13
Blocked by: target-model policy
Status: out-of-scope-for-v1
Resolution:

## Q-031 — [2026-04-25] Empty non-Xilinx target capacities (originally Q-ft-06)

Original ID: Q-ft-06
Original file: `open-questions-fringe-targets.md`

`Arria10`, `DE1`, and `ASIC` declare empty capacities. Need determine whether DSE can run meaningfully against these targets and whether HLS should fail fast when capacities are empty.

Source: src/spatial/targets/altera/Arria10.scala:11-13; src/spatial/targets/altera/DE1.scala:11-13; src/spatial/targets/generic/ASIC.scala:26-28
Blocked by: HLS target inventory
Status: out-of-scope-for-v1
Resolution:

## Q-032 — [2026-04-25] OpMemReduce access-unroll formula (originally Q-ft-07)

Original ID: Q-ft-07
Original file: `open-questions-fringe-targets.md`

`AreaModel.accessUnrollCount` multiplies by the sum of map and reduce counter-chain parallelism for `OpMemReduce`, with an inline comment saying this is definitely wrong. Need establish the correct formula before relying on memory-area estimates in HLS.

Source: src/spatial/targets/AreaModel.scala:41-58
Blocked by: banking and DSE area-model review
Status: out-of-scope-for-v1
Resolution:

## Q-033 — [2026-04-25] TileLoadModel disabled state (originally Q-ft-08)

Original ID: Q-ft-08
Original file: `open-questions-fringe-targets.md`

`GenericLatencyModel` calls `TileLoadModel.evaluate`, but `TileLoadModel` has the neural-network implementation commented out and returns `0.0`. Need decide whether this model is dead, temporarily disabled, or should be retrained/reimplemented for HLS.

Source: src/spatial/targets/generic/GenericLatencyModel.scala:11-68; src/spatial/targets/generic/TileLoadModel.scala:16-109
Blocked by: HLS latency-model training plan
Status: out-of-scope-for-v1
Resolution:

## Q-034 — [2026-04-25] DRAM debug-register cap (originally Q-ft-09)

Original ID: Q-ft-09
Original file: `open-questions-fringe-targets.md`

`DRAMArbiter` hard-codes `numDebugs = 500` and increments debug signal registration until labels are written, but no assertion was found for overflow beyond the vector size. Need verify whether debug signals can silently exceed the cap.

Source: fringe/src/fringe/templates/dramarbiter/DRAMArbiter.scala:22; fringe/src/fringe/templates/dramarbiter/DRAMArbiter.scala:103-118; fringe/src/fringe/templates/dramarbiter/DRAMArbiter.scala:255-263
Blocked by: debug-register stress test
Status: out-of-scope-for-v1
Resolution:

## Q-035 — [2026-04-25] FringeZynq bridge fallback behavior (originally Q-ft-10)

Original ID: Q-ft-10
Original file: `open-questions-fringe-targets.md`

`FringeZynq` selects AXI-Lite bridge variants for KCU1500, Zynq/ZedBoard, and ZCU, with no default branch for other target classes that may reuse the shell. Need determine whether every target using `FringeZynq` is covered or whether some shells leave register-file wiring unassigned.

Source: fringe/src/fringe/targets/zynq/FringeZynq.scala:79-117; fringe/src/fringe/targets/aws/AWS_F1.scala:9-40
Blocked by: target-shell elaboration audit
Status: out-of-scope-for-v1
Resolution:

## Q-036 — [2026-04-25] BigIP optional arithmetic behavior (originally Q-ft-11)

Original ID: Q-ft-11
Original file: `open-questions-fringe-targets.md`

Many `BigIP` operations default to throwing `Unimplemented`, and several simulation methods for trig/hyperbolic operations return the input with TODO comments. Need decide which operations the HLS rewrite must support, reject, or lower to vendor libraries.

Source: fringe/src/fringe/BigIP.scala:22-105; fringe/src/fringe/targets/BigIPSim.scala:82-96
Blocked by: HLS numeric-library policy
Status: needs-architectural-decision
Decision criteria: User decision: HLS port rejects unsupported BigIP operations, preserves current simulator placeholders, or lowers them to named vendor/library implementations.
Resolution:

## Q-037 — [2026-04-25] IICounter first-cycle issue dependency (originally Q-ft-12)

Original ID: Q-ft-12
Original file: `open-questions-fringe-targets.md`

`IICounter` has a TODO noting that old behavior issued done on the first cycle and the current switch to `cnt == 0` versus `cnt == ii-1` may break dependent logic. Need confirm the intended initiation-interval handshake before porting controller schedules.

Source: fringe/src/fringe/templates/counters/Counter.scala:121-150
Blocked by: controller timing regression tests
Status: out-of-scope-for-v1
Resolution:

## Q-038 — [2026-04-24] Hash-collision risk in `prDeqGrp` group-id assignment (originally Q-lang-01)

Original ID: Q-lang-01
Original file: `open-questions-lang-surface.md`

`priorityDeq` and `roundRobinDeq` (`src/spatial/lang/api/PriorityDeqAPI.scala:17, 47, 97`) tag every staged `FIFOPriorityDeq` with `prDeqGrp = fifo.head.toString.hashCode()`. The author's own `// TODO: this is probably an unsafe way to compute a group id` comment (`PriorityDeqAPI.scala:11, 26`) flags the risk: two unrelated dequeue calls whose head-fifo `toString` representations collide under `Int.hashCode()` would be grouped together by `MemoryUnrolling.scala:303-304`.

**Spec question.** What is the contract `prDeqGrp` is supposed to enforce? Is it "all dequeue ports of a single `priorityDeq` call form one group" (the documented intent), or "all dequeue ports across the whole program that share a group ID form one hardware unit" (the implemented behavior, with hash collisions as a footgun)? For the Rust port, this should be replaced with an explicit fused `PriorityDeqGroup(fifos, conds)` IR construct, but the spec needs to confirm the intended semantics first.

Source: `src/spatial/lang/api/PriorityDeqAPI.scala:11, 17, 26, 47, 97`, `src/spatial/metadata/access/AccessData.scala:43`, `src/spatial/transform/unrolling/MemoryUnrolling.scala:303-304`.
Blocked by: —
Status: needs-architectural-decision
Decision criteria: User decision: priority/round-robin dequeue grouping preserves hash-based compatibility or introduces an explicit grouped-dequeue IR construct.
Resolution: (empty)

## Q-039 — [2026-04-24] `FileBus` has no struct-shape check in source (originally Q-lang-07)

Original ID: Q-lang-07
Original file: `open-questions-lang-surface.md`

The language-surface request expected `FileBus` and `FileEOFBus` to check struct shape at construction time. The source confirms the check only for `FileEOFBus`: it pattern matches `Type[A]`, accepts a struct whose last field is `Bit`, and otherwise calls `state.logError()`. `FileBus[A]` only requires `Bits[A]` and returns `Bits[A].nbits`.

**Spec question.** Should plain `FileBus[A]` validate CSV struct shape, or is it intentionally permissive while `FileEOFBus[A]` is the checked EOF-delimited variant?

Source: `src/spatial/lang/Bus.scala:59-75`.
Blocked by: —
Status: minor-fix-pending
Resolution: (empty)

## Q-040 — [2026-04-24] Spatial blackbox uses attach empty file/module metadata (originally Q-lang-08)

Original ID: Q-lang-08
Original file: `open-questions-lang-surface.md`

`SpatialBlackbox.apply` and `SpatialCtrlBlackbox.apply` attach `BlackboxConfig("", None, 0, 0, params)` to use symbols. The empty file/module fields make sense for Spatial-defined blackboxes, but the zero latency and pipeline factor differ from the default `BlackboxConfig` values of `1` and `1`.

**Spec question.** Are zero latency and zero pipeline factor semantic for Spatial blackbox uses, or are they placeholders that downstream passes replace from implementation metadata?

Source: `src/spatial/lang/Blackbox.scala:15-18, 27-30`, `src/spatial/metadata/blackbox/BlackboxData.scala:6`.
Blocked by: —
Status: out-of-scope-for-v1
Resolution: (empty)

## Q-041 — [2026-04-24] `GEMV`, `CONV`, and `SHIFT` blackbox builtins are declared stubs (originally Q-lang-09)

Original ID: Q-lang-09
Original file: `open-questions-lang-surface.md`

`Blackbox.GEMM` stages a concrete `GEMMBox`, but `GEMV`, `CONV`, and `SHIFT(validAfter)` are declared as `???`.

**Spec question.** Should the HLS language surface expose only `GEMM`, or should it reserve names for `GEMV`, `CONV`, and `SHIFT` even though the current Scala implementation does not define them?

Source: `src/spatial/lang/Blackbox.scala:101-123`.
Blocked by: —
Status: out-of-scope-for-v1
Resolution: (empty)

## Q-042 — [2026-04-24] `Array.toeplitz` uses stride math despite a TODO saying stride is not incorporated (originally Q-lang-10)

Original ID: Q-lang-10
Original file: `open-questions-lang-surface.md`

`Array.toeplitz` has a `// TODO: Incorporate stride` comment, but the implementation uses `stride0` and `stride1` in padding, output rows, and slide offsets. It is unclear whether the remaining TODO refers to a missing stride case or stale documentation.

**Spec question.** What is the intended Toeplitz layout contract for strides greater than one?

Source: `src/spatial/lang/host/Array.scala:150-174`.
Blocked by: —
Status: minor-fix-pending
Resolution: (empty)

## Q-043 — [2026-04-24] `Tensor3.update` indexing differs from `Tensor3.apply` (originally Q-lang-11)

Original ID: Q-lang-11
Original file: `open-questions-lang-surface.md`

`Tensor3.apply(i,j,k)` indexes `data` with `i*dim1*dim2 + j*dim2 + k`. `Tensor3.update(i,j,k,elem)` indexes with `i*dim1*dim2 + j*dim1 + k`. For non-square `dim1`/`dim2`, these addresses differ.

**Spec question.** Is `Tensor3.update` a bug that should use `j*dim2`, or is there an undocumented storage-layout reason for the difference?

Source: `src/spatial/lang/host/Tensor3.scala:28-31`.
Blocked by: —
Status: minor-fix-pending
Resolution: (empty)

## Q-044 — [2026-04-24] `readBinary` accepts `isASCIITextFile` but does not use it (originally Q-lang-12)

Original ID: Q-lang-12
Original file: `open-questions-lang-surface.md`

`readBinary[A:Num](file, isASCIITextFile: Boolean = false)` stages `ReadBinaryFile(file)` and ignores the flag.

**Spec question.** Is `isASCIITextFile` obsolete, or should `ReadBinaryFile` carry the flag so binary loading can distinguish raw numeric binary from ASCII text?

Source: `src/spatial/lang/api/FileIOAPI.scala:98-100`.
Blocked by: —
Status: minor-fix-pending
Resolution: (empty)

## Q-045 — [2026-04-24] HLS policy for `printSRAM1/2/3` (originally Q-lang-13)

Original ID: Q-lang-13
Original file: `open-questions-lang-surface.md`

`printSRAM1`, `printSRAM2`, and `printSRAM3` emit `Foreach` loops over accelerator SRAMs. That differs from host tensor printing, which traverses host arrays and matrices.

**Spec question.** Should SRAM printing be simulation-only, synthesized as debug I/O, or rejected in HLS builds?

Source: `src/spatial/lang/api/DebuggingAPI.scala:98-132`.
Blocked by: —
Status: out-of-scope-for-v1
Resolution: (empty)

## Q-046 — [2026-04-24] `approxEql` relative-error behavior near zero (originally Q-lang-14)

Original ID: Q-lang-14
Original file: `open-questions-lang-surface.md`

Scalar numeric `approxEql(a,b,margin)` checks `abs(a - b) <= margin.to[T] * abs(a)`. When `a` is zero, the tolerance is zero regardless of `margin`.

**Spec question.** Is the asymmetric relative tolerance intentional, or should this use an absolute floor or `max(abs(a), abs(b))` style tolerance?

Source: `src/spatial/lang/api/DebuggingAPI.scala:152-160`.
Blocked by: —
Status: minor-fix-pending
Resolution: (empty)

## Q-047 — [2026-04-24] `throw` is not staged into Spatial IR (originally Q-lang-15)

Original ID: Q-lang-15
Original file: `open-questions-lang-surface.md`

`SpatialVirtualization.__throw` delegates to `forge.EmbeddedControls.throwImpl`; unlike `return`, `while`, and `do while`, it does not emit a Spatial-specific error in this file. The source also does not stage a Spatial IR node for exceptions.

**Spec question.** Should `throw` be considered unsupported user syntax like `while`, or should it remain a staging-time Scala exception escape hatch?

Source: `src/spatial/lang/api/SpatialVirtualization.scala:103-116`.
Blocked by: —
Status: resolved-by-spec - 2026-04-25 via [[80 - Virtualization]]
Resolution: (empty)

## Q-048 — [2026-04-24] Should HLS preserve Spatial's no-while/no-return limitation? (originally Q-lang-16)

Original ID: Q-lang-16
Original file: `open-questions-lang-surface.md`

`__return`, `__whileDo`, and `__doWhile` all emit explicit "not yet supported" errors. HLS C++ supports `while` and `return` syntactically, but Spatial currently avoids defining accelerator semantics for these virtualized constructs.

**Spec question.** Should a port inherit the current Spatial restriction exactly, or define new semantics for `while`/`return` in the HLS frontend?

Source: `src/spatial/lang/api/SpatialVirtualization.scala:103-114`.
Blocked by: —
Status: needs-architectural-decision
Decision criteria: User decision: Rust frontend preserves Spatial unsupported `while`/`return` restrictions or defines new HLS-visible semantics for them.
Resolution: (empty)

## Q-049 — [2026-04-24] Parameter-domain metadata shape for HLS/Rust (originally Q-lang-17)

Original ID: Q-lang-17
Original file: `open-questions-lang-surface.md`

`IntParameters` stores range domains with `(start, stride, end)` and explicit alternatives as parameter metadata on `I32.p(default)`.

**Spec question.** Should the port preserve this exact domain shape, or normalize range and explicit domains into a single parameter-domain enum?

Source: `src/spatial/lang/api/Implicits.scala:18-39, 46-55`.
Blocked by: —
Status: out-of-scope-for-v1
Resolution: (empty)

## Q-050 — [2026-04-24] `@streamstruct` parent classes are collected but not rejected (originally Q-lang-18)

Original ID: Q-lang-18
Original file: `open-questions-lang-surface.md`

The stream-struct macro collects parent names and has a TODO asking what to do if the class has parents, but it does not currently reject parent classes.

**Spec question.** Are parent classes meant to be allowed for `@streamstruct`, or should the macro reject them like methods, type parameters, and `var` fields?

Source: `src/spatial/tags/StreamStructs.scala:47-62`.
Blocked by: —
Status: minor-fix-pending
Resolution: (empty)

## Q-051 — [2026-04-24] Why do stream structs require both `Bits` and `Arith`? (originally Q-lang-19)

Original ID: Q-lang-19
Original file: `open-questions-lang-surface.md`

`StagedStreamStructsMacro` generates both Bits and Arith typeclasses and injects `box` evidence requiring `StreamStruct`, `Bits`, and `Arith`.

**Spec question.** Is `Arith` required for all stream structs, or is it generated for historical consistency even when a stream port is not arithmetically meaningful?

Source: `src/spatial/tags/StreamStructs.scala:32-35, 83-99`.
Blocked by: —
Status: out-of-scope-for-v1
Resolution: (empty)

## Q-052 — [2026-04-24] Duplicated macro declarations in `dsl` and `libdsl` (originally Q-lang-20)

Original ID: Q-lang-20
Original file: `open-questions-lang-surface.md`

`@spatial`, `@struct`, and `@streamstruct` are declared independently inside both `spatial.libdsl` and `spatial.dsl`.

**Spec question.** Is the duplication required by Scala annotation resolution, or can the declarations be factored while preserving both import scopes?

Source: `src/spatial/dsl.scala:14-25, 34-45`.
Blocked by: —
Status: out-of-scope-for-v1
Resolution: (empty)

## Q-053 — [2026-04-24] `log_taylor` lacks the domain guard that `exp_taylor` has (originally Q-lang-02)

Original ID: Q-lang-02
Original file: `open-questions-lang-surface.md`

`exp_taylor` (`src/spatial/lang/api/MathAPI.scala:81-85`) is a *piecewise* approximation: zero below `-3.5`, linear between `-3.5` and `-1.2`, fifth-order Taylor above `-1.2`. By contrast, `log_taylor` (`MathAPI.scala:88-91`) is a single fourth-order Taylor expansion of `ln(x)` around `x = 1`, with no range gate. Outside `(0, 2]` the error grows fast (the Taylor series diverges).

**Spec question.** Is the difference intentional (e.g. caller is expected to pre-clip the input to a known range), or is `log_taylor` an incomplete implementation that should follow the same piecewise pattern? The `sqrt_approx` author comment (`MathAPI.scala:105`) suggests these helpers are placeholders — see Q-lang-03.

Source: `src/spatial/lang/api/MathAPI.scala:81-91`.
Blocked by: —
Status: minor-fix-pending
Resolution: (empty)

## Q-054 — [2026-04-24] `sqrt_approx` "placeholder until floats" — what is the intended replacement? (originally Q-lang-03)

Original ID: Q-lang-03
Original file: `open-questions-lang-surface.md`

`sqrt_approx` (`MathAPI.scala:104-111`) carries the comment `// I don't care how inefficient this is, it is just a placeholder for backprop until we implement floats`. The implementation is a five-region piecewise fit. The comment implies that there will eventually be a float-native `sqrt` (presumably hardware-implemented, mapped to a Spatial primitive that lowers to a Xilinx CORDIC IP or similar).

**Spec question.** Is the planned replacement (a) a hardware sqrt primitive that lowers to vendor IP, (b) a higher-order Taylor expansion with float domain handling, or (c) something else? The Rust port needs to know whether to keep the piecewise approximation or to expose a single `sqrt` that dispatches to a float instruction.

Source: `src/spatial/lang/api/MathAPI.scala:104-111`, comment at line 105.
Blocked by: —
Status: out-of-scope-for-v1
Resolution: (empty)

## Q-055 — [2026-04-24] `AxiStream256` is promoted to `ShadowingAliases` but `AxiStream64`/`AxiStream512` are not (originally Q-lang-04)

Original ID: Q-lang-04
Original file: `open-questions-lang-surface.md`

`Aliases.scala:178-180` lifts three names — `AxiStream256`, `AxiStream256Bus`, `AxiStream256Data` — into the `ShadowingAliases` layer, but `AxiStream64`/`AxiStream512` (and their Bus/Data variants) remain only in `ExternalAliases`. So app code under `import spatial.dsl._` can write `AxiStream256` directly but must spell `spatial.lang.AxiStream64` for the 64-bit variant.

**Spec question.** Is 256-bit the canonical default bus width (justifying the special promotion), or is this an oversight that should be either (a) extended to all three widths or (b) demoted? The design implication for the Rust port is whether to expose all three at the same level or to single out 256-bit as canonical.

Source: `src/spatial/lang/Aliases.scala:178-180`, `src/spatial/lang/Bus.scala:28-50`.
Blocked by: —
Status: minor-fix-pending
Resolution: (empty)

## Q-056 — [2026-04-24] `Label` is the only Scala-native type promoted to the root of `ShadowingAliases` (originally Q-lang-05)

Original ID: Q-lang-05
Original file: `open-questions-lang-surface.md`

`Aliases.scala:169` declares `type Label = java.lang.String` at the same level as the *shadowed* names (`Int`, `Float`, `Boolean`). Other Scala types — `scala.Char`, `scala.Float`, `scala.Array`, etc. — are only available through `gen.*` (`Aliases.scala:184-197`). The asymmetry seems to exist because `String` is shadowed and there's no other way to get a host string for a name in `Reg[I32](0, "regName")`. But the same argument applies to other Scala types in some contexts.

**Spec question.** Is `Label` a one-off promoted name (justified by the `String → Text` shadowing being more disruptive than other primitives), or should other Scala types get equivalent shortcuts? For the Rust port, the convention should probably be a single `gen` namespace for *all* Scala-native escapes.

Source: `src/spatial/lang/Aliases.scala:168-169, 184-197`.
Blocked by: —
Status: out-of-scope-for-v1
Resolution: (empty)

## Q-057 — [2026-04-24] Empty `argon.lang.ShadowingAliases` — extension hook or vestigial? (originally Q-lang-06)

Original ID: Q-lang-06
Original file: `open-questions-lang-surface.md`

Argon defines its own `ShadowingAliases` trait (parallel to its `InternalAliases` and `ExternalAliases`) but it is empty (or near-empty). Spatial's `ShadowingAliases` extends `argon.lang.ExternalAliases` indirectly (via `InternalAliases extends argon.lang.ExternalAliases`, `Aliases.scala:7`), not argon's `ShadowingAliases`.

**Spec question.** Is argon's empty `ShadowingAliases` an intentional extension point (left empty so downstream DSLs like Spatial fill it via their own trait, as Spatial does with its own `ShadowingAliases`), or vestigial scaffolding from an earlier design? If intentional, what is the convention for downstream DSLs to layer their shadowing on top? If vestigial, can it be deleted?

Source: `argon/src/argon/lang/Aliases.scala`, `src/spatial/lang/Aliases.scala:7, 156`.
Blocked by: —
Status: out-of-scope-for-v1
Resolution: (empty)

## Q-058 — [2026-04-24] Raw schedule scratchpad finalization (originally Q-meta-01)

Original ID: Q-meta-01
Original file: `open-questions-metadata.md`

`rawSchedule_=` writes `ControlSchedule` to `state.scratchpad`, while `finalizeRawSchedule` writes normal metadata. What pass sequence guarantees scratchpad schedules are finalized before downstream readers stop checking scratchpad?

Source: src/spatial/metadata/control/package.scala:785-789
Status: out-of-scope-for-v1
Resolution:

## Q-059 — [2026-04-24] `ConvertToStreamed` ownership (originally Q-meta-02)

Original ID: Q-meta-02
Original file: `open-questions-metadata.md`

`ConvertToStreamed` is mirrored metadata, but the metadata source only exposes the getter/setter. Which pass consumes it, and should it remain mirrored in the Rust/HLS rewrite?

Source: src/spatial/metadata/control/ControlData.scala:287; src/spatial/metadata/control/package.scala:607-608
Status: out-of-scope-for-v1
Resolution:

## Q-060 — [2026-04-24] `HaltIfStarved` stream-stall model (originally Q-meta-03)

Original ID: Q-meta-03
Original file: `open-questions-metadata.md`

The source comment says the stream-control rule is confusing and needs redesign. Can this boolean be replaced by a derived stream dependency model?

Source: src/spatial/metadata/control/ControlData.scala:228-243
Status: out-of-scope-for-v1
Resolution:

## Q-061 — [2026-04-24] Pseudo-edge exclusion policy (originally Q-meta-04)

Original ID: Q-meta-04
Original file: `open-questions-metadata.md`

`DependencyEdge.isPseudoEdge` is defined in metadata, but the metadata package does not specify which queries must exclude pseudo-edges. Where should that policy live?

Source: src/spatial/metadata/access/AccessData.scala:49-60
Status: out-of-scope-for-v1
Resolution:

## Q-062 — [2026-04-24] Non-affine address fallback representation (originally Q-meta-05)

Original ID: Q-meta-05
Original file: `open-questions-metadata.md`

`AddressPattern.getSparseVector` maps partially non-affine components to a fresh `boundVar[I32]`. Should the Rust port make this an explicit random-dimension node instead?

Source: src/spatial/metadata/access/AccessPatterns.scala:232-242
Status: out-of-scope-for-v1
Resolution:

## Q-063 — [2026-04-24] `accessIterators` and MemReduce ownership (originally Q-meta-06)

Original ID: Q-meta-06
Original file: `open-questions-metadata.md`

`accessIterators` relies on scope iterator differences to handle MemReduce cross-subcontroller accesses. Should MemReduce stage ownership be modeled explicitly?

Source: src/spatial/metadata/access/package.scala:352-387
Status: out-of-scope-for-v1
Resolution:

## Q-064 — [2026-04-24] Accumulator lattice order (originally Q-meta-07)

Original ID: Q-meta-07
Original file: `open-questions-metadata.md`

The requested reading expected `Fold > Reduce > Buff > None > Unknown`, but source `>` methods appear to implement `Fold > Buff > Reduce > None > Unknown`. Which is intended?

Source: src/spatial/metadata/memory/AccumulatorData.scala:11-45
Status: resolved-by-spec - 2026-04-25 via [[30 - Memory]]
Resolution:

## Q-065 — [2026-04-24] `AccumulatorType` default (originally Q-meta-08)

Original ID: Q-meta-08
Original file: `open-questions-metadata.md`

The metadata comment says default `AccumType.None`, but the package accessor defaults to `AccumType.Unknown`. Which default should the Rust port preserve?

Source: src/spatial/metadata/memory/AccumulatorData.scala:49-57; src/spatial/metadata/memory/package.scala:14-16
Status: resolved-by-spec - 2026-04-25 via [[30 - Memory]]
Resolution:

## Q-066 — [2026-04-24] Mutable memory metadata state (originally Q-meta-09)

Original ID: Q-meta-09
Original file: `open-questions-metadata.md`

`Memory.resourceType`, `Wait.ids`, and `setBufPort` introduce mutable or destructive metadata patterns. Should these become explicit pass-state updates in Rust?

Source: src/spatial/metadata/memory/BankingData.scala:186-188; src/spatial/metadata/memory/Synchronization.scala:14-20; src/spatial/metadata/memory/package.scala:250-258
Status: out-of-scope-for-v1
Resolution:

## Q-067 — [2026-04-24] LockDRAM banking fallbacks (originally Q-meta-10)

Original ID: Q-meta-10
Original file: `open-questions-metadata.md`

LockDRAM accesses receive empty banking, `Set(0)` dispatch/group ids, and a default `Port(None, 0, 0, Seq(0), Seq(0))`. Are these semantic requirements or compatibility hacks?

Source: src/spatial/metadata/memory/package.scala:168-172; src/spatial/metadata/memory/package.scala:206-220; src/spatial/metadata/memory/package.scala:243-245
Status: out-of-scope-for-v1
Resolution:

## Q-068 — [2026-04-24] `FullDelay` transfer policy (originally Q-meta-11)

Original ID: Q-meta-11
Original file: `open-questions-metadata.md`

`FullDelay` is mirrored, but it is also overwritten by the retiming analyzer. Should HLS transforms mirror, invalidate, or always recompute this metadata?

Source: src/spatial/metadata/retiming/RetimingData.scala:43-49; src/spatial/metadata/retiming/package.scala:15-21
Status: out-of-scope-for-v1
Resolution:

## Q-069 — [2026-04-24] Pure delay-line planning (originally Q-meta-12)

Original ID: Q-meta-12
Original file: `open-questions-metadata.md`

`ValueDelay.value()` stages a delay line through a memoized closure. Can this be replaced by a pure allocation plan materialized in a deterministic transformer phase?

Source: src/spatial/metadata/retiming/ValueDelay.scala:13-18
Status: out-of-scope-for-v1
Resolution:

## Q-070 — [2026-04-25] Bounds `makeFinal` mutates one bound then stores another (originally Q-meta-13)

Original ID: Q-meta-13
Original file: `open-questions-metadata.md`

`makeFinal` sets `s.bound.isFinal = true` and then assigns `s.bound = Final(x)`, which appears to mark the previous bound object rather than the freshly stored `Final(x)`.

Source: src/spatial/metadata/bounds/package.scala:19; src/spatial/metadata/bounds/BoundData.scala:13-25
Blocked by: Search callers of `makeFinal` and `Final.unapply(Sym[_])`.
Status: minor-fix-pending
Resolution:

## Q-071 — [2026-04-25] Math residual reads `s.trace` but setter writes `s` (originally Q-meta-14)

Original ID: Q-meta-14
Original file: `open-questions-metadata.md`

`getResidual` reads `metadata[Residual](s.trace)`, while `residual_=` writes `Residual(equ)` on `s`.

Source: src/spatial/metadata/math/package.scala:27-40
Blocked by: Search all `residual_=` callers and trace-rewriting passes.
Status: minor-fix-pending
Resolution:

## Q-072 — [2026-04-25] Param value wrappers may be bypassed (originally Q-meta-15)

Original ID: Q-meta-15
Original file: `open-questions-metadata.md`

`IntParamValue` and `SchedParamValue` are declared metadata fields, but package accessors route integer values through bounds and schedule values through raw control schedule metadata.

Source: src/spatial/metadata/params/ParamDomain.scala:24-42; src/spatial/metadata/params/package.scala:31-41
Blocked by: Search repository-wide reads of `IntParamValue` and `SchedParamValue`.
Status: out-of-scope-for-v1
Resolution:

## Q-073 — [2026-04-25] Symbol type helpers test symbol object for `isNum` and `isBits` (originally Q-meta-16)

Original ID: Q-meta-16
Original file: `open-questions-metadata.md`

`SymUtils.isIdx` and `isString` inspect `x.tp`, but `isNum`, `isBits`, and `isVoid` use `x.isInstanceOf[...]`.

Source: src/spatial/metadata/types.scala:21-29
Blocked by: Verify intended Argon `Sym` class hierarchy and downstream callers.
Status: minor-fix-pending
Resolution:

## Q-074 — [2026-04-25] Blackbox config needs Rust+HLS ABI mapping (originally Q-meta-17)

Original ID: Q-meta-17
Original file: `open-questions-metadata.md`

`BlackboxConfig` is shaped around file/module/latency/pipeline-factor/parameter data, but the Rust+HLS ABI for external modules is not specified here.

Source: src/spatial/metadata/blackbox/BlackboxData.scala:6-15
Blocked by: HLS blackbox design decision.
Status: out-of-scope-for-v1
Resolution:

## Q-075 — [2026-04-25] `ShouldDumpFinal` comment appears stale (originally Q-meta-18)

Original ID: Q-meta-18
Original file: `open-questions-metadata.md`

The comment above `ShouldDumpFinal` describes "reader symbols for each local memory", which does not match the boolean dump-final flag name or wrapper.

Source: src/spatial/metadata/debug/DebugData.scala:5-11
Blocked by: Confirm intended UI/pass behavior for `shouldDumpFinal`.
Status: minor-fix-pending
Resolution:

## Q-076 — [2026-04-25] `CLIArgs.listNames` consumer is unclear (originally Q-meta-19)

Original ID: Q-meta-19
Original file: `open-questions-metadata.md`

The metadata source defines CLI argument names and dense listing behavior, but it does not identify the codegen or reporting path that consumes the names.

Source: src/spatial/metadata/CLIArgs.scala:8-17; src/spatial/metadata/CLIArgs.scala:35-46
Blocked by: Search codegen/reporting callers of `CLIArgs.listNames`.
Status: out-of-scope-for-v1
Resolution:

## Q-077 — [2026-04-25] Explicit false `CanFuseFMA` is indistinguishable from absence (originally Q-meta-20)

Original ID: Q-meta-20
Original file: `open-questions-metadata.md`

`canFuseAsFMA` uses `.exists(_.canFuse)`, so absent metadata and present `CanFuseFMA(false)` both read as false.

Source: src/spatial/metadata/rewrites/package.scala:8-9
Blocked by: Search callers that write `canFuseAsFMA = false`.
Status: minor-fix-pending
Resolution:

## Q-078 — [2026-04-25] `FreezeMem` comment is unfinished (originally Q-meta-21)

Original ID: Q-meta-21
Original file: `open-questions-metadata.md`

The `FreezeMem` comment says the flag prevents memory banking patterns from being analyzed or changed, then ends after "Generally useful for when".

Source: src/spatial/metadata/transform/TransformData.scala:14-19
Blocked by: Search downstream `freezeMem` consumers.
Status: minor-fix-pending
Resolution:

## Q-079 — [2026-04-24] HLS memory-resource taxonomy and catch-all order (originally Q-mdf-01)

Original ID: Q-mdf-01
Original file: `open-questions-models-dse-fringe-gaps.md`

Spatial's allocator treats `target.memoryResources` as an ordered priority list and assigns all unclaimed memories to the final list element. Need define the HLS resource list, minimum-depth rules, capacity fields, and catch-all behavior before porting allocation.

Source: src/spatial/targets/MemoryResource.scala:6-10; src/spatial/targets/HardwareTarget.scala:44-45; src/spatial/traversal/MemoryAllocator.scala:56-103
Blocked by: HLS resource-report schema
Status: needs-architectural-decision
Decision criteria: User decision: define the HLS memory-resource list, min-depth rules, capacity fields, and final catch-all allocation behavior.
Resolution:

## Q-080 — [2026-04-24] GenericDevice SRAM resource is defined but unselected (originally Q-mdf-02)

Original ID: Q-mdf-02
Original file: `open-questions-models-dse-fringe-gaps.md`

`GenericDevice` defines `SRAM_RESOURCE`, but its `memoryResources` list uses URAM, BRAM, URAM overflow, and LUTs, with BRAM as the default. Need decide whether this is dead compatibility code or a missed generic-target path before using Generic as an HLS template.

Source: src/spatial/targets/generic/GenericDevice.scala:13-44
Blocked by: generic-target audit
Status: out-of-scope-for-v1
Resolution:

## Q-081 — [2026-04-24] HLS CSV field schema and report mapping (originally Q-mdf-03)

Original ID: Q-mdf-03
Original file: `open-questions-models-dse-fringe-gaps.md`

The CSV loader framework transfers, but HLS needs a field schema that maps model outputs to HLS resources and schedule data. Need define area fields, latency fields, and target-specific CSV file names for the HLS backend.

Source: src/spatial/targets/SpatialModel.scala:74-103; src/spatial/targets/AreaModel.scala:18-23; src/spatial/targets/LatencyModel.scala:10-16; src/spatial/targets/HardwareTarget.scala:14-26
Blocked by: HLS report parser design
Status: out-of-scope-for-v1
Resolution:

## Q-082 — [2026-04-24] CSV loader strictness for extra and missing fields (originally Q-mdf-04)

Original ID: Q-mdf-04
Original file: `open-questions-models-dse-fringe-gaps.md`

`SpatialModel.loadModels` warns when expected target fields are missing from a CSV, but silently ignores CSV headings not included in `FIELDS`. Need decide whether the HLS loader should preserve this permissive behavior or fail fast on field-schema mismatches.

Source: src/spatial/targets/SpatialModel.scala:86-103
Blocked by: HLS model validation policy
Status: out-of-scope-for-v1
Resolution:

## Q-083 — [2026-04-24] HLS replacement for Chisel instantiation globals (originally Q-mdf-05)

Original ID: Q-mdf-05
Original file: `open-questions-models-dse-fringe-gaps.md`

The current instantiation path uses generated Scala, `SpatialIP`, `CommonMain`, and mutable Fringe globals to thread target selection, scalar counts, stream info, allocator count, retiming, and channel assignment. Need design the Rust/HLS equivalent without relying on Chisel elaboration-time mutation.

Source: src/spatial/codegen/chiselgen/ChiselCodegen.scala:129-302; src/spatial/codegen/chiselgen/ChiselGenInterface.scala:121-152; src/spatial/codegen/chiselgen/ChiselGenController.scala:550-581; fringe/src/fringe/SpatialIP.scala:18-40; fringe/src/fringe/globals.scala:7-79
Blocked by: HLS top-level generation design
Status: needs-architectural-decision
Decision criteria: User decision: define the Rust/HLS top-level manifest that replaces mutable Chisel/Fringe instantiation globals.
Resolution:

## Q-084 — [2026-04-24] ArgInterface versus ArgAPI scalar-layout ownership (originally Q-mdf-06)

Original ID: Q-mdf-06
Original file: `open-questions-models-dse-fringe-gaps.md`

The requested generated-file list names `ArgInterface.scala`, but source code opens only an empty `object Args` there while `ArgAPI.scala`, Fringe, RegFile, and target AXI4-Lite bridges carry the scalar-layout behavior. Need decide how the spec should name this boundary for the HLS port.

Source: src/spatial/codegen/chiselgen/ChiselCodegen.scala:175-191; src/spatial/codegen/chiselgen/ChiselCodegen.scala:283-285; src/spatial/codegen/chiselgen/ChiselGenInterface.scala:156-187; fringe/src/fringe/Fringe.scala:36-57; fringe/src/fringe/Fringe.scala:112-117; fringe/src/fringe/templates/axi4/AXI4LiteToRFBridge.scala:23-47
Blocked by: HLS host-argument ABI design
Status: resolved-by-spec - 2026-04-25 via [[90 - Host-Accel Boundary]]
Resolution:

## Q-085 — [2026-04-24] PIRGenSpatial active mixins versus 32-file scope (originally Q-oc-01)

Original ID: Q-oc-01
Original file: `open-questions-other-codegens.md`

The source directory has 32 PIR Scala files, but `PIRGenSpatial` actively mixes in `PIRCodegen` plus 21 traits; six traits are visibly commented out. Should the spec describe "32 trait mixins" as shorthand for directory scope, or should it use the source-verified active mixin list only?

Source: /Users/david/Documents/David_code/spatial/src/spatial/codegen/pirgen/PIRGenSpatial.scala:5-32
Blocked by: Historical intent for Plasticine backend documentation
Status: out-of-scope-for-v1
Resolution:

## Q-086 — [2026-04-24] PIR LineBuffer error trait is not mixed in (originally Q-oc-02)

Original ID: Q-oc-02
Original file: `open-questions-other-codegens.md`

`PIRGenLineBuffer` emits codegen-time `error` calls for line-buffer creation, enqueue, and read, but `PIRGenSpatial` does not mix in `PIRGenLineBuffer`. Should Pirgen fail explicitly on LineBuffer ops, or is fallback unmatched-node behavior intentional?

Source: /Users/david/Documents/David_code/spatial/src/spatial/codegen/pirgen/PIRGenLineBuffer.scala:13-20; /Users/david/Documents/David_code/spatial/src/spatial/codegen/pirgen/PIRGenSpatial.scala:5-32
Blocked by: Plasticine LineBuffer support policy
Status: out-of-scope-for-v1
Resolution:

## Q-087 — [2026-04-24] PIR VecSlice argument order and inclusive end (originally Q-oc-03)

Original ID: Q-oc-03
Original file: `open-questions-other-codegens.md`

`PIRGenVec` pattern matches `VecSlice(vector, end, start)` and emits `vector.slice(start, end+1)`, while the inline comment says "end is non-inclusive." Which convention should the Rust+HLS spec preserve?

Source: /Users/david/Documents/David_code/spatial/src/spatial/codegen/pirgen/PIRGenVec.scala:19-20
Blocked by: VecSlice IR semantics check outside codegen
Status: out-of-scope-for-v1
Resolution:

## Q-088 — [2026-04-24] NamedCodegen mixin list includes ScalaCodegen (originally Q-oc-04)

Original ID: Q-oc-04
Original file: `open-questions-other-codegens.md`

The requested note lists ChiselCodegen, ResourceReporter, and ResourceCountReporter as NamedCodegen users, but source also shows `ScalaCodegen extends Codegen with FileDependencies with NamedCodegen`. Should the final spec emphasize all source users or only the non-TreeGen users relevant to reports?

Source: /Users/david/Documents/David_code/spatial/src/spatial/codegen/scalagen/ScalaCodegen.scala:13-25; /Users/david/Documents/David_code/spatial/src/spatial/codegen/chiselgen/ChiselCodegen.scala:17-21; /Users/david/Documents/David_code/spatial/src/spatial/codegen/resourcegen/ResourceReporter.scala:22-24; /Users/david/Documents/David_code/spatial/src/spatial/codegen/resourcegen/ResourceCountReporter.scala:19-21
Blocked by: Spec scoping decision
Status: minor-fix-pending
Resolution:

## Q-089 — [2026-04-24] Cppgen target resource directories in Rust+HLS (originally Q-oc-05)

Original ID: Q-oc-05
Original file: `open-questions-other-codegens.md`

Cppgen hardcodes nine `<target>.sw-resources`, `<target>.hw-resources`, and `<target>.Makefile` dependency triples. Should the Rust+HLS rewrite preserve these directory names for compatibility, or replace them with typed target descriptors?

Source: /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppCodegen.scala:38-75
Blocked by: Rust+HLS packaging design
Status: out-of-scope-for-v1
Resolution:

## Q-090 — [2026-04-24] Treegen palette count differs from requested 23-color statement (originally Q-oc-06)

Original ID: Q-oc-06
Original file: `open-questions-other-codegens.md`

The prompt calls out an NBuf 23-color palette, but `TreeGen.memColors` contains 27 literal color strings. Should the spec retain the source-verified count or is there a historical 23-color palette elsewhere?

Source: /Users/david/Documents/David_code/spatial/src/spatial/codegen/treegen/TreeGen.scala:28-32
Blocked by: Historical visualization notes
Status: minor-fix-pending
Resolution:

## Q-091 — [2026-04-24] Rogue frame streams versus HLS host replacement (originally Q-oc-07)

Original ID: Q-oc-07
Original file: `open-questions-other-codegens.md`

Roguegen rejects `DRAMHostNew` but supports frame streams through `FrameMaster`, `FrameSlave`, and PyRogue connections. Should the HLS host rewrite model frames as streams, host buffers, or unsupported legacy behavior?

Source: /Users/david/Documents/David_code/spatial/src/spatial/codegen/roguegen/RogueGenInterface.scala:32-45
Blocked by: HLS host I/O design
Status: out-of-scope-for-v1
Resolution:

## Q-092 — [2026-04-24] ResourceReporter emits text with json extension (originally Q-oc-08)

Original ID: Q-oc-08
Original file: `open-questions-other-codegens.md`

`ResourceReporter` declares `ext = "json"` but emits textual controller and area lines, unlike `ResourceCountReporter`, which builds a JSON-shaped object. Should the spec call `ResourceReporter` a text report, a malformed JSON report, or an implementation bug?

Source: /Users/david/Documents/David_code/spatial/src/spatial/codegen/resourcegen/ResourceReporter.scala:22-24; /Users/david/Documents/David_code/spatial/src/spatial/codegen/resourcegen/ResourceReporter.scala:41-48; /Users/david/Documents/David_code/spatial/src/spatial/codegen/resourcegen/ResourceReporter.scala:183-190
Blocked by: Desired report format for rewrite
Status: minor-fix-pending
Resolution:

## Q-093 — [2026-04-24] MemoryAnalyzer-as-Codegen: is the HTML output consumed? (originally Q-pp-01)

Original ID: Q-pp-01
Original file: `open-questions-pass-pipeline.md`

`MemoryAnalyzer` extends `Codegen` (`traversal/MemoryAnalyzer.scala:17`) and emits `decisions_${state.pass}.html` per invocation. The HTML is purely a side effect of running the per-memory configurer. The deep-dive note flagged this as architecturally surprising.

Question: is anything downstream actually consuming `decisions_*.html` (e.g. external DSE feedback, a build dashboard, a verification harness), or is this strictly a debugging artifact? If purely debug, the codegen scaffolding adds noise — `MemoryAnalyzer` could be a regular `Pass` and the HTML logic could move to a dedicated reporter.

Source: `src/spatial/traversal/MemoryAnalyzer.scala:17, 22, 24, 111-123`
Blocked by: —
Status: out-of-scope-for-v1

## Q-094 — [2026-04-24] MemoryAllocator's "TODO: un-gut memory allocator" (originally Q-pp-02)

Original ID: Q-pp-02
Original file: `open-questions-pass-pipeline.md`

`MemoryAllocator.process` (`traversal/MemoryAllocator.scala:16`) starts with `println(s"TODO: un-gut memory allocator")`. The current pass body is the simple greedy first-fit.

Question: what is the intended functionality that's been "gutted"? Reading the surrounding code, it looks like the original allocator may have done backtracking / fractional assignment / cross-resource swaps. This matters for HLS planning — if Spatial's "real" allocator behaviour is what's documented, the spec is fine; if a more sophisticated allocator is supposed to be there, the spec is missing pieces.

Source: `src/spatial/traversal/MemoryAllocator.scala:15-17`
Blocked by: git log archeology
Status: out-of-scope-for-v1

## Q-095 — [2026-04-24] FIFOConfigurer drops 2 disjuncts vs general rule (originally Q-pp-03)

Original ID: Q-pp-03
Original file: `open-questions-pass-pipeline.md`

`MemoryConfigurer.requireConcurrentPortAccess` (`banking/MemoryConfigurer.scala:427-437`) has 7 disjuncts; `FIFOConfigurer.requireConcurrentPortAccess` (`banking/FIFOConfigurer.scala:20-26`) has 5. The 2 dropped:
1. `lca.isOuterPipeLoop && !isWrittenIn(lca)` — "OuterPipeLoop with no writes in LCA" (the buffer-port-no-conflict case).
2. The `delayDefined && fullDelay` pair — both same-parent-same-fullDelay and same-parent-diff-fullDelay-with-loopcontrolLCA.

The deep dive infers these are dropped because FIFOs aren't N-buffered, so "write reaches buffer port" is meaningless. But the source has no comment explaining the design choice.

Question: confirm via git blame that the dropped cases were intentional and not a stale-copy oversight.

Source: `src/spatial/traversal/banking/MemoryConfigurer.scala:427-437`, `banking/FIFOConfigurer.scala:20-26`
Blocked by: git blame
Status: resolved-by-spec - 2026-04-25 via [[70 - Banking]]

## Q-096 — [2026-04-24] Retiming-disabled compile path: do IterationDiff/Initiation still run? (originally Q-pp-04)

Original ID: Q-pp-04
Original file: `open-questions-pass-pipeline.md`

`RetimingAnalyzer.shouldRun = enableRetiming` (`traversal/RetimingAnalyzer.scala:14`) — when `--noretime` (which also disables `enableOptimizedReduce`) the analyzer no-ops. But `IterationDiffAnalyzer` and `InitiationAnalyzer` have no analogous `shouldRun` gate.

Question: when retiming is disabled, what happens to:
1. The `iterDiff` field — is it computed (junk metadata that nothing reads), or does some upstream check skip it?
2. The `compilerII = ceil(interval/iterDiff)` formula — does it compute meaningful values? The `latency` term inside `lhs.II = min(compilerII, latency)` may be wrong if `fullDelay` was never computed.

Source: `src/spatial/traversal/RetimingAnalyzer.scala:14`, `src/spatial/traversal/IterationDiffAnalyzer.scala:1-218`, `src/spatial/traversal/InitiationAnalyzer.scala:23-41`
Blocked by: —
Status: out-of-scope-for-v1

## Q-097 — [2026-04-24] BufferRecompute issue #98 muxPort-bump kludge (originally Q-pp-05)

Original ID: Q-pp-05
Original file: `open-questions-pass-pipeline.md`

`BufferRecompute` has a `Delete once #98 is fixed` comment (`traversal/BufferRecompute.scala:41`) before the muxPort-conflict workaround:

```scala
while (hasPortConflicts(lhs).size > 0) {
  val moveMe = hasPortConflicts(lhs).head
  val maxMuxPort = lhs.readers.map(_.port.muxPort).max
  moveMe.addPort(0, Seq(), Port(moveMe.port.bufferPort, maxMuxPort+1, …))
}
```

Question: what is issue #98 in the Spatial-lang/spatial repo, and what's the proper fix? This is referenced in the C0 - Retiming spec entry as an open question; a Rust+HLS reimplementation should know whether to inherit this kludge.

Source: `src/spatial/traversal/BufferRecompute.scala:41-47`
Blocked by: GitHub issue lookup
Status: out-of-scope-for-v1

## Q-098 — [2026-04-24] RetimingTransformer.precomputeDelayLines vs Switch case-trailing line (originally Q-pp-06)

Original ID: Q-pp-06
Original file: `open-questions-pass-pipeline.md`

`RetimingTransformer.precomputeDelayLines` (`transform/RetimingTransformer.scala:111-126`) materialises lines for every block in `op.blocks`. For `Switch` ops, `retimeSwitchCase` (`transform/RetimingTransformer.scala:156-178`) also adds a trailing `delayLine(size, body.result)` whose size is the sum of two `delayConsumers` lookups.

Question: are these materialisations always disjoint (precompute creates "shared across blocks" lines, retimeSwitchCase creates "case-trailing" lines), or can they double-count the same delay? If the same `(input, delay)` pair could match both, would that produce duplicate `DelayLine` nodes in the IR, or does `addDelayLine`'s SortedSet semantics dedupe them?

Source: `src/spatial/transform/RetimingTransformer.scala:111-126, 156-178`, `src/spatial/util/modeling.scala:589-616` (`createValueDelay`)
Blocked by: —
Status: out-of-scope-for-v1

## Q-099 — [2026-04-24] SwitchTransformer selector wording: AND-gated or "pre-OR'd"? (originally Q-pp-07)

Original ID: Q-pp-07
Original file: `open-questions-pass-pipeline.md`

The pass-writing work order described flattened switch selectors as "pre-OR'd conditions," but `SwitchTransformer.extractSwitches` computes `thenCond = cond2 & prevCond` and `elseCond = !cond2 & prevCond`. That source behavior is path-gating with conjunction, where `prevCond` represents the prior else path.

Question: was "pre-OR'd" shorthand for a different downstream representation, or should the spec consistently describe these selectors as path-qualified AND-gated conditions?

Source: `src/spatial/transform/SwitchTransformer.scala:52-70`
Blocked by: author confirmation
Status: resolved-by-spec - 2026-04-25 via [[30 - Switch and Conditional]]

## Q-100 — [2026-04-24] Direct consumers of `hotSwapPairings` (originally Q-pp-08)

Original ID: Q-pp-08
Original file: `open-questions-pass-pipeline.md`

`SwitchOptimizer.markHotSwaps` writes `mem.hotSwapPairings`, and the metadata comment says it suppresses RAW-cycle complaints for squashed if/else-if chains. Direct source reads found during this pass-entry write are `MemoryUnrolling.substHotSwap` and `modeling.protectRAWCycle`.

Question: is there a codegen or banking consumer that reads this metadata indirectly, or should the Switch spec call it retiming/modeling metadata rather than codegen/banking metadata?

Source: `src/spatial/transform/SwitchOptimizer.scala:16-30`, `src/spatial/metadata/memory/MemoryData.scala:67-78`, `src/spatial/transform/unrolling/MemoryUnrolling.scala:306-309`, `src/spatial/util/modeling.scala:474-483`
Blocked by: wider source audit / maintainer confirmation
Status: resolved-by-spec - 2026-04-25 via [[30 - Switch and Conditional]]

## Q-101 — [2026-04-24] Is `PerformanceAnalyzer` still active? (originally Q-pp-09)

Original ID: Q-pp-09
Original file: `open-questions-pass-pipeline.md`

`PerformanceAnalyzer` writes `lhs.latency` and `lhs.II` from `nestedRuntimeOfNode`, and it supports rerun through `RerunTraversal`. The canonical `Spatial.runPasses` chain constructs `RuntimeModelGenerator` directly but does not construct or invoke `PerformanceAnalyzer`.

Question: is `PerformanceAnalyzer` an older runtime-cycle estimator left for DSE experimentation, or is it invoked outside `Spatial.runPasses` in a path not covered by the pass-pipeline note?

Source: `src/spatial/traversal/PerformanceAnalyzer.scala:11-98`, `src/spatial/traversal/RerunTraversal.scala:6-13`, `src/spatial/Spatial.scala:76-88`, `src/spatial/Spatial.scala:154-155`, `src/spatial/Spatial.scala:180-182`, `src/spatial/Spatial.scala:233-235`
Blocked by: broader DSE/runtime-model audit
Status: out-of-scope-for-v1

## Q-102 — [2026-04-24] Stub and optional cleanup passes in HLS (originally Q-pp-10)

Original ID: Q-pp-10
Original file: `open-questions-pass-pipeline.md`

`TextCleanup` deletes accelerator-scope `DSLOp`s with `canAccel=false` only under the optional `textCleanup` flag, while `StreamConditionSplitTransformer` currently delegates directly to `super.transform` without adding behavior. Both are present in source but have ambiguous importance for a Rust+HLS compiler.

Question: should HLS planning preserve these as named passes for pipeline parity, collapse them into frontend cleanup, or drop `StreamConditionSplitTransformer` until it has semantics?

Source: `src/spatial/transform/TextCleanup.scala:9-20`, `src/spatial/Spatial.scala:176`, `src/spatial/Spatial.scala:361-362`, `src/spatial/transform/StreamConditionSplitTransformer.scala:7-11`
Blocked by: HLS pipeline design
Status: out-of-scope-for-v1

## Q-103 — [2026-04-24] HLS treatment of Spatial iteration-diff analysis (originally Q-pp-11)

Original ID: Q-pp-11
Original file: `open-questions-pass-pipeline.md`

`IterationDiffAnalyzer` computes `iterDiff` and `segmentMapping` from Spatial affine matrices and a Spatial-specific notion of ticks, lane distances, and accumulation cycles. HLS tools may serialize or pipeline loop-carried dependencies differently, especially when arrays are partitioned or when dependence pragmas are emitted.

Question: should the HLS reimplementation carry over Spatial's `iterDiff` algorithm exactly, use it only for diagnostics, or replace it with an HLS scheduler/dependence model?

Source: `src/spatial/traversal/IterationDiffAnalyzer.scala:17-169`, `src/spatial/traversal/InitiationAnalyzer.scala:23-41`
Blocked by: HLS scheduling design
Status: needs-architectural-decision
Decision criteria: User decision: HLS scheduling reuses Spatial `iterDiff`, keeps it diagnostic-only, or replaces it with an HLS dependence/schedule model.

## Q-104 — [2026-04-25] Crandall reference model vs staged rewrite (originally Q-pp-12)

Original ID: Q-pp-12
Original file: `open-questions-pass-pipeline.md`

The rewrite spec request mentioned Crandall's algorithm "via `modifiedCrandallSW` from `utils.math`." Direct source verification shows `RewriteTransformer` imports Mersenne helper predicates from `utils.math` and implements the staged hardware rewrite as `crandallDivMod`, but it does not call `modifiedCrandallSW`. The software helper lives in `utils/src/utils/math/package.scala` as a reference/test implementation.

Question: should the spec describe `modifiedCrandallSW` only as a software reference model for the staged `crandallDivMod` rewrite, or is there a historical code path where the transformer used that helper directly?

Source: `src/spatial/transform/RewriteTransformer.scala:21-23, 55-88, 173-184`; `utils/src/utils/math/package.scala:73-100`
Blocked by: git blame / test history
Status: resolved-by-spec - 2026-04-25 via [[90 - Rewrite Transformer]]

## Q-105 — [2026-04-25] Streamify helper passes constructed but omitted from sequence (originally Q-pp-13)

Original ID: Q-pp-13
Original file: `open-questions-pass-pipeline.md`

`Spatial.runPasses` constructs `earlyUnroller`, `accelPipeInserter`, `forceHierarchical`, and `dependencyGraphAnalyzer` as lazy vals, but the current `streamify` sequence only includes `dependencyGraphAnalyzer`, `initiationAnalyzer`, `HierarchicalToStream`, `switchTransformer`, `pipeInserter`, and checks/dumps. The sequence name still includes `PreEarlyUnroll`, which makes the omission especially ambiguous.

Question: were `EarlyUnroller`, `AccelPipeInserter`, and `ForceHierarchical` intentionally retired from the streamify chain, temporarily disabled, or accidentally omitted?

Source: `src/spatial/Spatial.scala:123-126, 144`; `src/spatial/transform/streamify/EarlyUnroller.scala:19-292`; `src/spatial/transform/streamify/AccelPipeInserter.scala:7-20`; `src/spatial/transform/streamify/ForceHierarchical.scala:7-14`
Blocked by: git blame / streamify test cases
Status: out-of-scope-for-v1

## Q-106 — [2026-04-25] Commented-out streamify files status (originally Q-pp-14)

Original ID: Q-pp-14
Original file: `open-questions-pass-pipeline.md`

`FlattenToStream.scala` is line-commented from the package declaration onward and appears superseded by `HierarchicalToStream`. `StreamingControlBundle.scala` is not literally entirely commented out: the package/import header is active, but the object and case-class definitions are commented.

Question: should the spec treat both files as retired design drafts, or does the active package/import header in `StreamingControlBundle.scala` have a build purpose?

Source: `src/spatial/transform/streamify/FlattenToStream.scala:1-43`; `src/spatial/transform/streamify/StreamingControlBundle.scala:1-29`; `src/spatial/transform/streamify/HierarchicalToStream.scala:151-838`
Blocked by: build/package behavior check
Status: out-of-scope-for-v1

## Q-107 — [2026-04-25] AllocMotion lazy val without pipeline invocation (originally Q-pp-15)

Original ID: Q-pp-15
Original file: `open-questions-pass-pipeline.md`

`AllocMotion` has concrete behavior for moving memories, counters, and counter chains to the top of outer `Foreach`/`UnitPipe` blocks, and `Spatial.runPasses` constructs `allocMotion` as a lazy val. The visible pass chain does not invoke `allocMotion`.

Question: is `AllocMotion` intentionally unused in the canonical pipeline, used by an alternate path not visible in `runPasses`, or stale?

Source: `src/spatial/Spatial.scala:118, 164-235`; `src/spatial/transform/AllocMotion.scala:11-58`
Blocked by: git blame / alternate pass entry-point search
Status: out-of-scope-for-v1

## Q-108 — [2026-04-25] AccumTransformer II=1 contract location (originally Q-pp-16)

Original ID: Q-pp-16
Original file: `open-questions-pass-pipeline.md`

The accumulator specialization spec describes `RegAccumOp` and `RegAccumFMA` as the II=1 accumulator replacement nodes. Source verification shows `AccumTransformer` replaces marked WAR-cycle writers with those nodes and Chisel codegen instantiates specialized accumulator modules, but `AccumTransformer` does not directly set controller `II` metadata.

Question: where is the II=1 guarantee formally enforced: in retiming/initiation analysis, in codegen's accumulator modules, or as an unstated convention on `RegAccum` nodes?

Source: `src/spatial/transform/AccumTransformer.scala:39-48, 96-122`; `src/spatial/node/Accumulator.scala:30-50`; `src/spatial/codegen/chiselgen/ChiselGenMem.scala:226-292`; `src/spatial/traversal/InitiationAnalyzer.scala:27-40`
Blocked by: codegen/runtime behavior check
Status: resolved-by-spec - 2026-04-25 via [[60 - Reduction and Accumulation]]

## Q-109 — [2026-04-24] ISL set-containment semantics (originally Q-pmd-01)

Original ID: Q-pmd-01
Original file: `open-questions-poly-models-dse.md`

`ISL.isSuperset` returns `false` and `ISL.intersects` returns `true`, even though both comments say they are used for reaching write calculation. Need decide whether the Rust+HLS rewrite should implement precise set containment/intersection or preserve current conservative behavior.

Source: poly/src/poly/ISL.scala:164-174; src/spatial/metadata/access/AffineData.scala:44-48
Blocked by: reaching-write analysis audit
Status: out-of-scope-for-v1
Resolution:

## Q-110 — [2026-04-24] External solver packaging boundary (originally Q-pmd-02)

Original ID: Q-pmd-02
Original file: `open-questions-poly-models-dse.md`

The current JVM path lazily compiles `$HOME/bin/emptiness` from `emptiness.c` and libisl, then talks to a singleton subprocess. Need decide whether the rewrite embeds ISL, vendors a solver binary, or keeps an external worker protocol.

Source: poly/src/poly/ISL.scala:14-117
Blocked by: Rust dependency and deployment decision
Status: out-of-scope-for-v1
Resolution:

## Q-111 — [2026-04-24] Constraint replaceKeys offset rule (originally Q-pmd-03)

Original ID: Q-pmd-03
Original file: `open-questions-poly-models-dse.md`

`ConstraintMatrix.replaceKeys` adds replacement offsets to constraint constants but carries a source TODO questioning whether that is correct. Need validate with examples before porting.

Source: poly/src/poly/ConstraintMatrix.scala:15-23
Blocked by: affine substitution tests
Status: minor-fix-pending
Resolution:

## Q-112 — [2026-04-24] Banking-search pruning strategy for HLS (originally Q-pmd-04)

Original ID: Q-pmd-04
Original file: `open-questions-poly-models-dse.md`

Banking search expands candidate views, `N` strictness, alpha strictness, duplication, block factors, and `P`, while `NBestGuess.factorize` uses direct divisor enumeration. Need a pruning or memoization plan before larger HLS DSE runs.

Source: src/spatial/metadata/memory/BankingData.scala:547-563; src/spatial/traversal/banking/ExhaustiveBanking.scala:392-431; src/spatial/traversal/banking/MemoryConfigurer.scala:610-633
Blocked by: HLS memory banking design
Status: needs-architectural-decision
Decision criteria: User decision: HLS banking search reuses Spatial alpha/N/B search, constrains it to HLS partition forms, or replaces it with a new planner.
Resolution:

## Q-113 — [2026-04-24] HLS area model training corpus (originally Q-pmd-05)

Original ID: Q-pmd-05
Original file: `open-questions-poly-models-dse.md`

The model container and CSV loader transfer, but PMML memory models, fallback constants, RAM heuristics, and DSP rules are target-specific. Need define the HLS measurement corpus and output fields.

Source: models/src/models/AreaEstimator.scala:59-215; src/spatial/targets/AreaModel.scala:85-91; src/spatial/targets/AreaModel.scala:180-205
Blocked by: HLS resource-report format decision
Status: out-of-scope-for-v1
Resolution:

## Q-114 — [2026-04-24] Dense load latency model replacement (originally Q-pmd-06)

Original ID: Q-pmd-06
Original file: `open-questions-poly-models-dse.md`

`TileLoadModel.evaluate` always returns `0.0`, so the dense-load `memoryModel` path computes a logistic base and then multiplies by zero. Need decide whether to delete, restore, or retrain this path.

Source: src/spatial/targets/generic/GenericLatencyModel.scala:20-35; src/spatial/targets/generic/TileLoadModel.scala:102-108
Blocked by: transfer benchmark data
Status: out-of-scope-for-v1
Resolution:

## Q-115 — [2026-04-24] Congestion model source of truth (originally Q-pmd-07)

Original ID: Q-pmd-07
Original file: `open-questions-poly-models-dse.md`

The standalone lattice-regression `CongestionModel.evaluate` exists, but `RuntimeModel.ControllerModel.congestionModel` comments out that call and uses `ModelData.curve_fit` instead. Need identify which model should become authoritative.

Source: models/src/models/CongestionModel.scala:115-124; models/src/models/RuntimeModel.scala:251-277; models/src/models/ModelData.scala:69-73
Blocked by: runtime-model validation
Status: out-of-scope-for-v1
Resolution:

## Q-116 — [2026-04-24] Runtime-model replacement for HLS DSE (originally Q-pmd-08)

Original ID: Q-pmd-08
Original file: `open-questions-poly-models-dse.md`

DSE latency shells out to a compiled Scala runtime-model jar and parses `"Total Cycles for App"`. HLS DSE needs an equivalent cycle source that may come from HLS scheduling reports, simulation, or a new estimator.

Source: src/spatial/dse/LatencyAnalyzer.scala:29-47; src/spatial/dse/DSEAnalyzer.scala:90-147
Blocked by: HLS latency source decision
Status: needs-architectural-decision
Decision criteria: User decision: HLS DSE latency comes from Spatial runtime-model parity, HLS reports/simulation, or a new estimator.
Resolution:

## Q-117 — [2026-04-24] DSE thread-safety of analyzer state (originally Q-pmd-09)

Original ID: Q-pmd-09
Original file: `open-questions-poly-models-dse.md`

`threadBasedDSE` creates per-worker states, but the source comments that initialization may not be thread-safe and each worker reruns mutable area/cycle analyzers. Need verify the thread-safety contract before carrying this worker model forward.

Source: src/spatial/dse/DSEAnalyzer.scala:320-350; src/spatial/dse/DSEThread.scala:56-77; src/spatial/dse/DSEThread.scala:136-151
Blocked by: parallel DSE stress test
Status: out-of-scope-for-v1
Resolution:

## Q-118 — [2026-04-23] Unbiased rounding determinism (originally Q-scal-01)

Original ID: Q-scal-01
Original file: `open-questions-scalagen.md`

`FixedPoint.unbiased` at `spatial/emul/src/emul/FixedPoint.scala:232-241` calls `scala.util.Random.nextFloat()` on every invocation. Two consecutive runs of the same simulator produce different bit-exact outputs on any program that hits `*&` / `/&` / `UnbMul` / `UnbDiv` / `FixToFixUnb` / `FixToFixUnbSat`.

**Spec question.** Is the nondeterminism load-bearing (modeling a real hardware dithered-LSB behavior) or an accident of implementation? For the HLS port: should the Rust simulator match the JVM RNG behavior (difficult), use a seedable but deterministic RNG, or substitute a deterministic round-to-nearest-even?

**Source.** `spatial/emul/src/emul/FixedPoint.scala:232-241`, `ScalaGenFixPt.scala:111-114`.

Status: needs-architectural-decision
Decision criteria: User decision: unbiased rounding matches JVM RNG nondeterminism, uses a seedable deterministic RNG, or becomes deterministic rounding.

## Q-119 — [2026-04-23] FIFO / LIFO elastic semantics (originally Q-scal-02)

Original ID: Q-scal-02
Original file: `open-questions-scalagen.md`

`ScalaGenFIFO` emits `object $lhs extends scala.collection.mutable.Queue[A]` with no enqueue-side size check. `FIFOBankedEnq` just calls `fifo.enqueue(...)` unconditionally (`ScalaGenFIFO.scala:41-44`). The FIFO grows without bound. The same is true for LIFO (`ScalaGenLIFO.scala:39-44`) and Stream queues (`ScalaGenStream.scala:92-97`).

**Spec question.** In synthesized hardware, `FIFOEnq` on full FIFOs either back-pressures or asserts. Scalagen silently elastic-enqueues. Is the HLS simulator expected to match scalagen (let tests discover the bug via assertion failures), or to emulate back-pressure in simulation too?

**Source.** `spatial/src/spatial/codegen/scalagen/ScalaGenFIFO.scala:41-44`, `spatial/src/spatial/codegen/scalagen/ScalaGenLIFO.scala:39-44`, `spatial/src/spatial/codegen/scalagen/ScalaGenStream.scala:92-97`.

Status: resolved-by-spec - 2026-04-25 via [[40 - FIFO LIFO Stream Simulation]]

## Q-120 — [2026-04-23] `FloatPoint.clamp` magic "x > 1.9" heuristic (originally Q-scal-03)

Original ID: Q-scal-03
Original file: `open-questions-scalagen.md`

At `spatial/emul/src/emul/FloatPoint.scala:335-339`:

```scala
if (y < fmt.SUB_E && x > 1.9) {
  y += 1
  x = 1
}
```

The `1.9` is undocumented. The comment at `:327-330` is cut out, so there is no inline justification. Conjecture: this is guarding the edge case where rounding a near-subnormal `BigDecimal` to 2.0 would escape the subnormal range and we want to bump the exponent to normal range with mantissa 0.

**Spec question.** Document the intended behavior. Is `1.9` a tolerance threshold (possibly equal to some `1 - 2^{-sbits}` value for typical sbits), or is it arbitrary? The Rust port needs to reproduce this exactly.

**Source.** `spatial/emul/src/emul/FloatPoint.scala:335-339`.

Status: resolved-by-spec - 2026-04-25 via [[20 - Numeric Reference Semantics]]

## Q-121 — [2026-04-23] `FixedPoint.toShort` shift-by-`bits` bug (originally Q-scal-04)

Original ID: Q-scal-04
Original file: `open-questions-scalagen.md`

`spatial/emul/src/emul/FixedPoint.scala:81` is:

```scala
def toShort: Short = (value >> fmt.bits).toShort
```

Every sibling conversion shifts by `fbits`:

```scala
def toByte: Byte   = (value >> fmt.fbits).toByte
def toInt: Int     = (value >> fmt.fbits).toInt
def toLong: Long   = (value >> fmt.fbits).toLong
def toBigInt       = value >> fmt.fbits
```

Shifting by `fmt.bits` zeros out the entire value on most formats, returning zero. This looks like a typo.

**Spec question.** Is `toShort` intentionally broken, or is this a real bug? Does it affect any code? The `FixPtType(...).toShort` pipeline likely goes through `FixToFix(fmt = FixFormat(true, 16, 0))` at the language level instead of `toShort` directly, so the bug may be unreachable.

**Source.** `spatial/emul/src/emul/FixedPoint.scala:80-84`.

Status: minor-fix-pending

## Q-122 — [2026-04-23] Outer-stream HACK and feedback loops (originally Q-scal-05)

Original ID: Q-scal-05
Original file: `open-questions-scalagen.md`

`ScalaGenController.emitControlBlock` at `spatial/src/spatial/codegen/scalagen/ScalaGenController.scala:22-49` contains an explicit `HACK` comment: for `isOuterStreamControl` controllers, each child is drained to completion before the next child runs. The comment at line 33 says "this won't work for cases with feedback, but this is disallowed for now anyway".

**Spec question.** What exactly is "disallowed"? Where in the compiler is the check that rejects stream-feedback? And — more importantly — what's the intended semantics for stream-coupled outer loops? The Rust port either matches scalagen's hand-pumped drain-per-child semantics (non-general) or does something different.

**Source.** `spatial/src/spatial/codegen/scalagen/ScalaGenController.scala:22-49`.

Status: out-of-scope-for-v1

## Q-123 — [2026-04-23] Delay line semantics under `--sim` (originally Q-scal-06)

Original ID: Q-scal-06
Original file: `open-questions-scalagen.md`

`ScalaGenDelays.scala:10-14`:

```scala
case DelayLine(size, data@Const(_)) => // Don't emit anything here (NamedCodegen takes care of this)
case DelayLine(size, data) => emit(src"val $lhs = $data")
```

Constant delay lines are elided entirely. Non-constant delay lines become a trivial alias. The simulator treats a `DelayLine(3, x)` and `x` as semantically identical.

**Spec question.** In RTL, retiming moves pipeline registers around to match timing. In scalagen, the registers are gone. For the Rust HLS target, whether to honor retiming semantics at all depends on whether the Rust backend is (a) behavioral (ignore timing, match scalagen) or (b) cycle-accurate (honor retiming). The spec should be explicit about the "reference semantics" view here: scalagen says retiming is invisible.

**Source.** `spatial/src/spatial/codegen/scalagen/ScalaGenDelays.scala:9-14`.

Status: resolved-by-spec - 2026-04-25 via [[70 - Timing Model]]

## Q-124 — [2026-04-23] `BankedMemory.initMem` no-op (originally Q-scal-07)

Original ID: Q-scal-07
Original file: `open-questions-scalagen.md`

`spatial/emul/src/emul/BankedMemory.scala:46-48`:

```scala
def initMem(size: Int, zero: T): Unit = if (needsInit) {
  needsInit = false
}
```

The function does nothing except flip a flag. Data is injected via the constructor's `data: Array[Array[T]]` parameter, which the emitted scalagen code builds in the `emitBankedInitMem` block (`ScalaGenMemories.scala:143-147`). Meanwhile `Memory.initMem` at `spatial/emul/src/emul/Memory.scala:8-15` actually allocates the backing array.

**Spec question.** Why is there a no-op `initMem` on `BankedMemory` at all? The emit pattern `$lhs.initMem($size, $zero)` for banked memories doesn't do anything; it could be removed. Is this a vestigial symmetry with `Memory`?

**Source.** `spatial/emul/src/emul/BankedMemory.scala:46-48`, `spatial/emul/src/emul/Memory.scala:8-15`.

Status: minor-fix-pending

## Q-125 — [2026-04-23] `RegAccumOp` throws on `AccumFMA` / `AccumUnk` (originally Q-scal-08)

Original ID: Q-scal-08
Original file: `open-questions-scalagen.md`

`spatial/src/spatial/codegen/scalagen/ScalaGenReg.scala:49-50`:

```scala
case AccumFMA => throw new Exception("This shouldn't happen!")
case AccumUnk => throw new Exception("This shouldn't happen!")
```

`AccumFMA` is split off into `RegAccumFMA` by `accumTransformer` (per the coverage note); `AccumUnk` presumably never survives `accumAnalyzer`.

**Spec question.** What exactly guarantees these cases are unreachable? Can `--sim` be run without `enableOptimizedReduce`, and if so, does scalagen crash on FMA accumulation? Trace the invariant.

**Source.** `spatial/src/spatial/codegen/scalagen/ScalaGenReg.scala:41-65`, `spatial/src/spatial/Spatial.scala:224-225`.

Status: resolved-by-spec - 2026-04-25 via [[60 - Reduction and Accumulation]]

## Q-126 — [2026-04-23] `expandInits` padding fallback (originally Q-scal-09)

Original ID: Q-scal-09
Original file: `open-questions-scalagen.md`

`spatial/src/spatial/codegen/scalagen/ScalaGenMemories.scala:69-90` has `expandInits` which pads a memory's init array when `padding` is nonzero. Non-padded positions copy from the original init. Padded positions fall back to:

```scala
else
  inits.get.head
```

I would have expected `invalid(tp)` or the memory's zero. Using `inits.get.head` replicates the first init value into every padded slot, which is likely not semantically correct.

**Spec question.** Is this a bug, or does the memory allocator guarantee the padded region is read-masked before any access? The Rust port needs to decide.

**Source.** `spatial/src/spatial/codegen/scalagen/ScalaGenMemories.scala:74-87`.

Status: minor-fix-pending

## Q-127 — [2026-04-23] `DRAMTracker` global state (originally Q-scal-10)

Original ID: Q-scal-10
Original file: `open-questions-scalagen.md`

`spatial/emul/src/emul/DRAMTracker.scala:6`:

```scala
val accessMap = mutable.Map[Any, Int]().withDefaultValue(0)
```

The map is a JVM-global singleton. Two simulations in the same JVM (e.g., an `sbt run` loop for a test suite) will accumulate counts across runs.

**Spec question.** Is this intentional (one JVM per simulation), or should the tracker be per-simulation? For Rust where there's no shared JVM, does the tracker matter at all beyond `StatTracker`?

**Source.** `spatial/emul/src/emul/DRAMTracker.scala:5-11`.

Status: out-of-scope-for-v1

## Q-128 — [2026-04-23] `LineBuffer.swap` and `wrCounter`/`lastWrRow` invariants (originally Q-scal-11)

Original ID: Q-scal-11
Original file: `open-questions-scalagen.md`

`spatial/emul/src/emul/LineBuffer.scala:21-25`:

```scala
def swap(): Unit = {
  bufferRow = posMod(bufferRow - stride, fullRows)
  readRow = posMod(readRow - stride, fullRows)
  wrCounter = 0
}
```

`swap` resets `wrCounter` but does not reset `lastWrRow`. Since the next write at line 44 uses `if (bank0 != lastWrRow) wrCounter = 0`, the post-swap state is `wrCounter = 0` and `lastWrRow = (some old row)`. If the post-swap first write happens to land on the old `lastWrRow`, the counter does not re-reset (already 0) — fine. If it lands elsewhere, `wrCounter` is reset to 0 (re-redundantly).

**Spec question.** Is `lastWrRow` intentionally not reset by `swap`? Could there be a case where the line buffer is in an inconsistent state across an outer-loop iteration boundary?

**Source.** `spatial/emul/src/emul/LineBuffer.scala:21-25`, `:43-46`.

Status: minor-fix-pending

## Q-129 — [2026-04-23] Stream filename resolution in Rust port (originally Q-scal-12)

Original ID: Q-scal-12
Original file: `open-questions-scalagen.md`

Generated scalagen code prompts on stdin for stream filenames at simulator startup (`spatial/emul/src/emul/Stream.scala:6-8`, `:30-35`, `:58-60`). The standard harness pipes them in via `run.sh`. This is a usability wart.

**Spec question.** Should the Rust simulator (a) match scalagen and prompt on stdin, (b) accept filenames as constructor arguments at codegen time (requiring the codegen to know test-vector paths), (c) accept filenames as CLI flags at runtime (e.g., `--stream-in foo=in.txt`), or (d) accept a single config file mapping stream names to filenames?

Note: option (b) breaks separation between codegen (deterministic from IR) and test data; option (c) is closest to current `run.sh` behavior but more user-friendly.

**Source.** `spatial/emul/src/emul/Stream.scala:5-79`.

Status: out-of-scope-for-v1

## Q-130 — [2026-04-23] Transcendental precision for the Rust port (originally Q-scal-13)

Original ID: Q-scal-13
Original file: `open-questions-scalagen.md`

`spatial/emul/src/emul/Number.scala:97-156` routes every transcendental through `Math.*` over `Double`, regardless of the source format precision:

```scala
def sqrt(x: FloatPoint): FloatPoint = FloatPoint(Math.sqrt(x.toDouble), x.fmt).withValid(x.valid)
```

For a `FltFormat(52, 11)` (IEEE double), this is bit-exact. For `FltFormat(23, 8)` (IEEE single), the result is rounded twice (compute in double, then `clamp` to single — usually fine but not always bit-equivalent to a hardware single-precision sqrt). For wider formats like `FltFormat(112, 15)` (quad), the f64 round-trip *loses precision*.

**Spec question.** Should the Rust simulator (a) match scalagen and route through f64 (fast, occasionally lossy for wide formats), (b) use MPFR for per-format-exact transcendentals (slower, bit-exact), or (c) match the synthesized hardware unit (e.g., a Newton-Raphson iteration with N steps)? The spec needs to define the canonical transcendental for each format.

**Source.** `spatial/emul/src/emul/Number.scala:97-156`.

Status: needs-architectural-decision
Decision criteria: User decision: Rust numeric runtime matches Scalagen f64 transcendentals, uses per-format MPFR/exact math, or matches synthesized hardware units.

## Q-131 — [2026-04-23] `LIFONumel` return type inconsistency (originally Q-scal-14)

Original ID: Q-scal-14
Original file: `open-questions-scalagen.md`

`spatial/src/spatial/codegen/scalagen/ScalaGenLIFO.scala:29`:

```scala
case LIFONumel(lifo,_) => emit(src"val $lhs = $lifo.size")
```

vs `spatial/src/spatial/codegen/scalagen/ScalaGenFIFO.scala:31`:

```scala
case FIFONumel(fifo,_)   => emit(src"val $lhs = FixedPoint($fifo.size,FixFormat(true,32,0))")
```

`FIFONumel` returns `FixedPoint`; `LIFONumel` returns raw `Int`. If the IR-level `LIFONumel` op has a `FixedPoint` return type, the emitted Scala would have a type mismatch at compile time. If the IR-level type is `Int`, there's an asymmetry between `FIFO` and `LIFO` that should be unified.

**Spec question.** Bug or intentional asymmetry? Check the IR definition of `LIFONumel.R`.

**Source.** `spatial/src/spatial/codegen/scalagen/ScalaGenLIFO.scala:29`, `spatial/src/spatial/codegen/scalagen/ScalaGenFIFO.scala:31`.

Status: minor-fix-pending

## Q-132 — [2026-04-23] `breakWhen` end-of-iteration vs immediate semantics (originally Q-scal-15)

Original ID: Q-scal-15
Original file: `open-questions-scalagen.md`

`spatial/src/spatial/codegen/scalagen/ScalaGenController.scala:75-93` emits `while(hasItems_$lhs && !${stopWhen.get}.value)` for break-enabled loops, with an explicit warning at `:76`/`:79`/`:89`/`:92`: *"breakWhen detected! Note scala break occurs at the end of the loop, while --synth break occurs immediately"*.

This means scalagen sees one extra iteration's worth of memory writes / register updates compared to RTL. **For tests using `breakWhen`, scalagen and chiselgen produce different outputs.**

**Spec question.** Should the Rust simulator match scalagen (end-of-iteration) for parity with existing test results, or match RTL (immediate-break) for tighter HLS correspondence? The two are mutually exclusive.

**Source.** `spatial/src/spatial/codegen/scalagen/ScalaGenController.scala:74-93`.

Status: needs-architectural-decision
Decision criteria: User decision: Rust simulation matches Scalagen end-of-iteration `breakWhen` or synthesized immediate-break behavior.

## Q-133 — [2026-04-23] `OneHotMux` reduce-with-`|` correctness (originally Q-scal-16)

Original ID: Q-scal-16
Original file: `open-questions-scalagen.md`

`spatial/src/spatial/codegen/scalagen/ScalaGenBits.scala:30-37`:

```scala
case op @ OneHotMux(selects,datas) =>
  open(src"val $lhs = {")
    emit(src"List(")
    selects.indices.foreach { i => emit(...) }
    emit(").collect{case (sel, d) if sel => d}.reduce{_|_}")
  close("}")
```

The `reduce{_|_}` assumes the data type defines `|`. For `FixedPoint`, this is bitwise-OR; for `Bool`, logical-OR; for `FloatPoint`, **there is no `|` operator** — `OneHotMux` over floats would fail to compile. Presumably rewrite passes guarantee this never happens.

**Spec question.** What guarantees this? If a one-hot mux over floats is needed (e.g., from optimization), what rewrites prevent the IR from reaching codegen with that shape? Also: if multiple selects are true, the OR-reduce produces a value that is the bitwise union — likely not a valid value of the source format. Is this acceptable (relying on caller for one-hotness) or should there be a runtime check?

**Source.** `spatial/src/spatial/codegen/scalagen/ScalaGenBits.scala:30-37`.

Status: resolved-by-spec - 2026-04-25 via [[60 - Counters and Primitives]]

## Q-134 — [2026-04-23] `Counter.takeWhile` debug println (originally Q-scal-17)

Original ID: Q-scal-17
Original file: `open-questions-scalagen.md`

`spatial/emul/src/emul/Counter.scala:24-33`:

```scala
def takeWhile(continue: => Bool)(func: ...): Unit = {
  var i = start
  while ({...} && continue) {
    Console.println(s"continue? $continue")  // <--
    val vec = ...
    ...
  }
}
```

The `Console.println` floods stdout when `takeWhile` is invoked (any `breakWhen`-flagged loop). Looks like leftover debug instrumentation.

**Spec question.** Drop the println in the Rust port. Is there any test that depends on this output?

**Source.** `spatial/emul/src/emul/Counter.scala:27`.

Status: minor-fix-pending

## Q-135 — [2026-04-23] `ScalaGenVec.invalid` apparent typo (originally Q-scal-18)

Original ID: Q-scal-18
Original file: `open-questions-scalagen.md`

`spatial/src/spatial/codegen/scalagen/ScalaGenVec.scala:14-17`:

```scala
override def invalid(tp: Type[_]): String = tp match {
  case tp: Vec[_] => src"""Array.fill(${tp.nbits}(${invalid(tp.A)})"""
  case _ => super.invalid(tp)
}
```

Missing closing parenthesis: should likely be `Array.fill(${tp.nbits})(${invalid(tp.A)})`. As written, the emitted code is `Array.fill(N(X)` — invalid Scala. This means `invalid` for a `Vec` type either never gets called (only used in OOB and switch fallbacks) or always errors at compilation.

**Spec question.** Bug. When is `invalid(Vec[A])` reached? Are there any tests that produce a Vec invalid that would catch this?

**Source.** `spatial/src/spatial/codegen/scalagen/ScalaGenVec.scala:14-17`.

Status: minor-fix-pending

## Q-136 — [2026-04-25] Atomic write recursion depth (originally Q-sem-01)

Original ID: Q-sem-01
Original file: `open-questions-semantics.md`

`recurseAtomicLookup` is named recursively but appears to peel only one `AtomicRead` level before alias expansion. Confirm whether nested atomic reads should recurse to the outermost mutable container.

Source: `argon/src/argon/static/Staging.scala:245-250`; [[30 - Effects and Aliasing]]
Blocked by: main-session source review
Status: minor-fix-pending
Resolution:

## Q-137 — [2026-04-25] Mutable aliases in Rust ownership terms (originally Q-sem-02)

Original ID: Q-sem-02
Original file: `open-questions-semantics.md`

Argon allows mutable alias errors to be disabled by `enableMutableAliases`. Decide whether the Rust port preserves this compatibility flag or makes mutable aliasing a hard error.

Source: `argon/src/argon/static/Staging.scala:39-75`; `argon/src/argon/Config.scala:46-47`; [[30 - Effects and Aliasing]]
Blocked by: Rust IR ownership design
Status: needs-architectural-decision
Decision criteria: User decision: Rust IR preserves the `enableMutableAliases` compatibility flag or makes mutable aliasing a hard error.
Resolution:

## Q-138 — [2026-04-25] Default scheduler motion semantics (originally Q-sem-03)

Original ID: Q-sem-03
Original file: `open-questions-semantics.md`

`SimpleScheduler` accepts `allowMotion` but always returns no motioned syms. The default scheduler branch also chooses `SimpleScheduler` on both sides. Decide whether to delete motion machinery or implement a real motion scheduler in Rust.

Source: `argon/src/argon/schedule/SimpleScheduler.scala:10-31`; `argon/src/argon/static/Scoping.scala:56-78`; [[60 - Scopes and Scheduling]]
Blocked by: scheduling design
Status: resolved-by-spec - 2026-04-25 via [[60 - Scopes and Scheduling]]
Resolution:

## Q-139 — [2026-04-25] Pipe holder observability in HLS (originally Q-sem-04)

Original ID: Q-sem-04
Original file: `open-questions-semantics.md`

`PipeInserter` routes escaping stage values through `Reg`, `FIFOReg`, or `Var` holders. Determine which holder effects must remain visible when HLS could otherwise schedule SSA values without explicit holders.

Source: `src/spatial/transform/PipeInserter.scala:170-209`; `src/spatial/transform/PipeInserter.scala:256-305`; [[50 - Pipe Insertion]]
Blocked by: HLS lowering design
Status: needs-architectural-decision
Decision criteria: User decision: HLS lowering must preserve `Reg`/`FIFOReg`/`Var` pipe holders as observable state or may optimize them to SSA where legal.
Resolution:

## Q-140 — [2026-04-25] Operational meaning of Fork, ForkJoin, and PrimitiveBox (originally Q-sem-05)

Original ID: Q-sem-05
Original file: `open-questions-semantics.md`

`CtrlSchedule` enumerates `ForkJoin`, `Fork`, and `PrimitiveBox`, but lower-level entries document mainly enum membership and consumers. Need a precise operational definition before treating these as first-class HLS schedules.

Source: `src/spatial/metadata/control/ControlData.scala:7-14`; `src/spatial/metadata/control/package.scala:193-219`; [[10 - Control]]
Blocked by: pass/codegen source review
Status: needs-architectural-decision
Decision criteria: User decision: define operational semantics for `Fork`, `ForkJoin`, and `PrimitiveBox` schedules in the Rust/HLS scheduler.
Resolution:

## Q-141 — [2026-04-25] Scalagen parallel pipe serial execution (originally Q-sem-06)

Original ID: Q-sem-06
Original file: `open-questions-semantics.md`

Scalagen emits `ParallelPipe` bodies sequentially, while hardware interprets parallelism structurally. Decide whether Rust simulation matches Scalagen source order or models parallel interleaving/back-pressure.

Source: `spatial/src/spatial/codegen/scalagen/ScalaGenController.scala:187-191`; [[50 - Controller Emission]]
Blocked by: simulator policy
Status: needs-architectural-decision
Decision criteria: User decision: Rust simulation follows Scalagen sequential `ParallelPipe` execution or models parallel interleaving/back-pressure.
Resolution:

## Q-142 — [2026-04-25] OOB simulator versus synthesized hardware (originally Q-sem-07)

Original ID: Q-sem-07
Original file: `open-questions-semantics.md`

Scalagen logs OOB reads/writes and returns invalid/discards writes; hardware behavior is not naturally the same. Decide whether Rust offers Scalagen-compatible OOB plus stricter synthesis assertions.

Source: `spatial/emul/src/emul/OOB.scala:19-38`; `spatial/src/spatial/codegen/scalagen/ScalaGenMemories.scala:36-50`; [[30 - Memory Simulator]]
Blocked by: simulator/synthesis mode split
Status: needs-architectural-decision
Decision criteria: User decision: Rust offers Scalagen-compatible OOB log/invalid behavior, synthesis assertions, or separate simulator/synthesis modes.
Resolution:

## Q-143 — [2026-04-25] LockDRAM fallback banking semantics (originally Q-sem-08)

Original ID: Q-sem-08
Original file: `open-questions-semantics.md`

LockDRAM accessors fall back to unit banking, dispatch `{0}`, and a default port. Clarify whether this is required semantics or a temporary compatibility path.

Source: `src/spatial/metadata/memory/package.scala:168-245`; [[30 - Memory]]
Blocked by: LockDRAM design review
Status: out-of-scope-for-v1
Resolution:

## Q-144 — [2026-04-25] Unbiased rounding nondeterminism (originally Q-sem-09)

Original ID: Q-sem-09
Original file: `open-questions-semantics.md`

`FixedPoint.unbiased` calls `scala.util.Random.nextFloat()`, so unbiased fixed-point operations are nondeterministic. Decide whether Rust matches nondeterminism, seeds it, or replaces it with deterministic rounding.

Source: `spatial/emul/src/emul/FixedPoint.scala:232-241`; [[20 - Numeric Reference Semantics]]
Blocked by: simulator reproducibility policy
Status: needs-architectural-decision
Decision criteria: User decision: unbiased rounding matches nondeterministic Spatial behavior, becomes seedable, or is replaced by deterministic rounding.
Resolution:

## Q-145 — [2026-04-25] FloatPoint clamp heuristics (originally Q-sem-10)

Original ID: Q-sem-10
Original file: `open-questions-semantics.md`

`FloatPoint.clamp` includes an unexplained `x > 1.9` subnormal guard. Confirm whether this heuristic is required for bit compatibility or can be replaced by a cleaner custom-float algorithm.

Source: `spatial/emul/src/emul/FloatPoint.scala:335-339`; [[20 - Numeric Reference Semantics]]
Blocked by: numeric conformance tests
Status: needs-architectural-decision
Decision criteria: User decision: Rust float packing reproduces the `x > 1.9` clamp heuristic bit-for-bit or adopts a cleaner custom-float algorithm with accepted divergence.
Resolution:

## Q-146 — [2026-04-25] FMA fused versus Scalagen unfused semantics (originally Q-sem-11)

Original ID: Q-sem-11
Original file: `open-questions-semantics.md`

Scalagen emits `FixFMA` and `RegAccumFMA` as multiply-then-add, while Chisel hardware FMA may preserve fused precision. Decide whether Rust simulator and HLS backend match Scalagen or hardware.

Source: `spatial/src/spatial/codegen/scalagen/ScalaGenFixPt.scala:150`; `spatial/src/spatial/codegen/scalagen/ScalaGenReg.scala:57-64`; [[60 - Counters and Primitives]]
Blocked by: numeric backend policy
Status: needs-architectural-decision
Decision criteria: User decision: HLS port matches Scalagen unfused multiply-add precision or Chisel/HLS fused FMA precision.
Resolution:

## Q-147 — [2026-04-25] AccumType lattice contradiction (originally Q-sem-12)

Original ID: Q-sem-12
Original file: `open-questions-semantics.md`

Requested semantics say `Fold > Reduce > Buff > None > Unknown`, but the metadata entry reports source behavior `Fold > Buff > Reduce > None > Unknown`. Decide which order is authoritative.

Source: `src/spatial/metadata/memory/AccumulatorData.scala:11-45`; [[30 - Memory]]
Blocked by: source intent review
Status: resolved-by-spec - 2026-04-25 via [[30 - Memory]]
Resolution:

## Q-148 — [2026-04-25] DelayLine simulator parity versus cycle accuracy (originally Q-sem-13)

Original ID: Q-sem-13
Original file: `open-questions-semantics.md`

Scalagen elides `DelayLine`, while Chisel retiming inserts real delay registers. Decide whether Rust simulation is value-only Scalagen-compatible or cycle-aware.

Source: `spatial/src/spatial/codegen/scalagen/ScalaGenDelays.scala:7-15`; `src/spatial/transform/RetimingTransformer.scala:205-220`; [[C0 - Retiming]]
Blocked by: simulator scope
Status: needs-architectural-decision
Decision criteria: User decision: Rust simulation is value-only and elides `DelayLine`, or is cycle-aware and models retiming registers.
Resolution:

## Q-149 — [2026-04-25] Target accepted II versus compilerII (originally Q-sem-14)

Original ID: Q-sem-14
Original file: `open-questions-semantics.md`

Spatial records `compilerII` and selected `II`, but an HLS tool may accept, relax, or reject the requested II. Decide where the Rust+HLS flow records target-accepted II.

Source: `src/spatial/traversal/InitiationAnalyzer.scala:14-41`; [[C0 - Retiming]]
Blocked by: HLS reporting integration
Status: needs-architectural-decision
Decision criteria: User decision: define where the flow records and reconciles HLS tool-accepted II versus Spatial `compilerII`/requested II.
Resolution:

## Q-150 — [2026-04-25] FIFO and LIFO elastic simulator versus back-pressure (originally Q-sem-15)

Original ID: Q-sem-15
Original file: `open-questions-semantics.md`

Scalagen FIFO/LIFO/Stream enqueues grow queues without size checks; RTL/HLS queues should be bounded and back-pressured. Decide simulator policy and test expectations.

Source: `spatial/src/spatial/codegen/scalagen/ScalaGenFIFO.scala:41-44`; `spatial/src/spatial/codegen/scalagen/ScalaGenLIFO.scala:39-44`; `spatial/src/spatial/codegen/scalagen/ScalaGenStream.scala:92-97`; [[40 - FIFO LIFO Stream Simulation]]
Blocked by: simulator policy
Status: needs-architectural-decision
Decision criteria: User decision: simulator and HLS semantics use Scalagen elastic queues or bounded FIFO/LIFO/stream back-pressure with overflow checks.
Resolution:

## Q-151 — [2026-04-25] FieldDeq missing write effect (originally Q-sem-16)

Original ID: Q-sem-16
Original file: `open-questions-semantics.md`

`StreamStruct.field` is documented as a dequeue, but `FieldDeq` does not currently declare `Effects.Writes(struct)`. Decide whether the effect system should model field dequeues as mutations.

Source: `src/spatial/node/StreamStruct.scala:12-16`; `src/spatial/lang/StreamStruct.scala:17-36`; [[60 - Streams and Blackboxes]]
Blocked by: effect-system/source review
Status: minor-fix-pending
Resolution:

## Q-152 — [2026-04-25] HLS host ABI manifest (originally Q-sem-17)

Original ID: Q-sem-17
Original file: `open-questions-semantics.md`

Cppgen and Chiselgen emit `ArgAPI` manifests for scalar args, DRAM pointers, ArgIOs, ArgOuts, instrumentation, and exits. Decide the equivalent manifest format for Rust+HLS.

Source: `/Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenInterface.scala:138-164`; `src/spatial/codegen/chiselgen/ChiselGenInterface.scala:156-187`; [[10 - Cppgen]]
Blocked by: host runtime design
Status: needs-architectural-decision
Decision criteria: User decision: define the Rust/HLS host ABI manifest for scalar args, DRAM pointers, ArgIO/ArgOuts, counters, exits, and streams.
Resolution:

## Q-153 — [2026-04-25] Fixed-point host conversion parity (originally Q-sem-18)

Original ID: Q-sem-18
Original file: `open-questions-semantics.md`

Cppgen maps fractional fixed-point host expressions to `double` while transfers use shifted raw integers. Decide whether the Rust host side should match Cppgen approximation or enforce bit-exact fixed-point values.

Source: `/Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenCommon.scala:75-100`; `/Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenInterface.scala:42-80`; [[10 - Cppgen]]
Blocked by: host numeric design
Status: needs-architectural-decision
Decision criteria: User decision: Rust host-side fixed-point conversions match Cppgen double approximations or enforce bit-exact shifted-integer values.
Resolution:

## Q-154 — [2026-04-25] OneHotMux multi-true semantics (originally Q-sem-19)

Original ID: Q-sem-19
Original file: `open-questions-semantics.md`

Scalagen implements `OneHotMux` by collecting true lanes and reducing data with bitwise OR. This is only valid when exactly one selector is true and can be semantically wrong for multiple true lanes. Decide whether Rust matches Scalagen or asserts one-hotness.

Source: `spatial/src/spatial/codegen/scalagen/ScalaGenBits.scala:30-37`; `src/spatial/node/Mux.scala:19-37`; [[60 - Counters and Primitives]]
Blocked by: primitive semantics policy
Status: needs-architectural-decision
Decision criteria: User decision: HLS `OneHotMux` with multiple true selectors matches Scalagen OR-reduce, asserts one-hotness, or defines priority semantics.
Resolution:

## Q-155 — [2026-04-24] `IterInfo` vs `IndexCounter` redundancy (originally Q-irn-01)

Original ID: Q-irn-01
Original file: `open-questions-spatial-ir.md`

The `counter_=` setter (`src/spatial/metadata/control/package.scala:1089-1091, 1098-1100`) writes both `IndexCounter(info)` on the iterator and `IterInfo(iter)` on the counter — a bidirectional binding. Is `IterInfo` ever queried independently of `IndexCounter`, or could the bidirectional metadata be collapsed to a single direction (counter → iter via a controller's `iters` field)?

Source: `src/spatial/metadata/control/ControlData.scala:136, 142`; `src/spatial/metadata/control/package.scala:1086-1102`
Blocked by: —
Status: out-of-scope-for-v1
Resolution: (empty until resolved)

## Q-156 — [2026-04-24] LaneStatic insertion coverage (originally Q-irn-02)

Original ID: Q-irn-02
Original file: `open-questions-spatial-ir.md`

`LaneStatic` is only inserted by `CounterIterRewriteRule` for three modular-arithmetic patterns (`iter % par`, `(iter / step) % par`, `((iter - start) / step) % par`). Are there other lane-index expressions (e.g., `(iter / par) % submap`) that should also fold to `LaneStatic` but currently don't? If so, are they handled at codegen instead?

Source: `src/spatial/rewrites/CounterIterRewriteRule.scala:18-37`
Blocked by: —
Status: minor-fix-pending
Resolution: (empty until resolved)

## Q-157 — [2026-04-24] `IndexCounterInfo.lanes` ordering significance (originally Q-irn-03)

Original ID: Q-irn-03
Original file: `open-questions-spatial-ir.md`

Post-unroll, `IndexCounterInfo.lanes: Seq[Int]` carries a list of physical lane indices. Is the ordering significant (e.g., does lane index 0 always correspond to the lowest-id iterator), or is it a set that happens to be encoded as a `Seq`? The unroller (`src/spatial/transform/unrolling/UnrollingBase.scala:455-487`) constructs both `[i]` (singleton) and `[parAddr(p)(ci) for p in 0..V-1]` (vector) lane lists, but it's unclear whether downstream consumers depend on a specific order.

Source: `src/spatial/metadata/control/ControlData.scala:39`; `src/spatial/transform/unrolling/UnrollingBase.scala:464, 466, 481`
Blocked by: —
Status: out-of-scope-for-v1
Resolution: (empty until resolved)

## Q-158 — [2026-04-24] PriorityMux warn asymmetry (originally Q-irn-04)

Original ID: Q-irn-04
Original file: `open-questions-spatial-ir.md`

`OneHotMux.rewrite` warns at staging time on multiple statically-true selects (`src/spatial/node/Mux.scala:25-28`). `PriorityMux` has the same warning code path but it's commented out (`Mux.scala:43-51`). Is the asymmetry intentional (priority muxes have well-defined precedence so multi-true is fine), or is the commented-out branch dead code that should be re-enabled with a different message?

Source: `src/spatial/node/Mux.scala:21-36, 41-56`
Blocked by: —
Status: resolved-by-spec - 2026-04-25 via [[50 - Primitives]]
Resolution: (empty until resolved)

## Q-159 — [2026-04-24] `RegAccumLambda` codegen complexity bound (originally Q-irn-05)

Original ID: Q-irn-05
Original file: `open-questions-spatial-ir.md`

`RegAccumLambda` takes a `Lambda1[A,A]` for arbitrary user-defined reductions. Codegen must support *any* lambda, but accumulator codegen relies on single-cycle RMW assumption (`#pragma HLS DEPENDENCE inter false` in HLS terms; equivalent retiming behavior in Chisel). Is there a complexity bound (latency, dependence) that the analyzer enforces, or does codegen just inline whatever lambda is given and hope for the best? If the lambda has long latency, what happens to the accumulator's first-iteration semantics?

Source: `src/spatial/node/Accumulator.scala:52-57`
Blocked by: —
Status: out-of-scope-for-v1
Resolution: (empty until resolved)

## Q-160 — [2026-04-24] `Transient[R]` cross-layer split (originally Q-irn-06)

Original ID: Q-irn-06
Original file: `open-questions-spatial-ir.md`

`Transient[R]` is a Spatial subclass that fixes `isTransient = true`, but `argon.node.Primitive[R]` already exposes `isTransient` as a `val`. The TODO in `src/spatial/node/Transient.scala:9` notes "This is a bit odd to have Primitive in argon and Transient in spatial." Could `Transient` be merged into argon as a renamed `Primitive` constructor flag, or is the cross-layer split load-bearing for some reason (e.g., `Transient.unapply`'s dependence on `spatial.metadata.bounds.Expect`)?

Source: `src/spatial/node/Transient.scala:9-19`; `argon/src/argon/node/DSLOp.scala:13-15`
Blocked by: —
Status: out-of-scope-for-v1
Resolution: (empty until resolved)

## Q-161 — [2026-04-24] `FieldDeq.effects` correctness (originally Q-irn-07)

Original ID: Q-irn-07
Original file: `open-questions-spatial-ir.md`

`FieldDeq.effects` is conservatively pure (inherits `Primitive` default), but the TODO at `src/spatial/node/StreamStruct.scala:14-15` says it should be `Effects.Writes(struct)`. The TODO also notes the obstacle: applying the effect to a bound symbol inside a `SpatialCtrl` blackbox body is ambiguous. What concrete bug would arise from setting the correct effect, and is the bound-sym issue the only obstacle?

Source: `src/spatial/node/StreamStruct.scala:12-16`
Blocked by: —
Status: minor-fix-pending
Resolution: (empty until resolved)

## Q-162 — [2026-04-24] `FieldEnq` reachability (originally Q-irn-08)

Original ID: Q-irn-08
Original file: `open-questions-spatial-ir.md`

`FieldEnq` carries a `// TODO: FieldEnq may not actually be used anywhere` comment (`src/spatial/node/StreamStruct.scala:18`) but is staged by `StreamStruct.field_update` (`src/spatial/lang/StreamStruct.scala:36`). Is `field_update` reachable from any DSL surface API, or is it dead code that the TODO predates? If unreachable, can `FieldEnq` be removed from the IR surface?

Source: `src/spatial/node/StreamStruct.scala:18-22`; `src/spatial/lang/StreamStruct.scala:36`
Blocked by: —
Status: out-of-scope-for-v1
Resolution: (empty until resolved)

## Q-163 — [2026-04-24] `SpatialCtrlBlackboxUse` rawLevel not set at staging (originally Q-irn-09)

Original ID: Q-irn-09
Original file: `open-questions-spatial-ir.md`

`VerilogCtrlBlackbox` sets `rawLevel = Inner` explicitly at staging (`src/spatial/lang/Blackbox.scala:93`); `SpatialCtrlBlackboxUse` does not (`src/spatial/lang/Blackbox.scala:28`). Should the Spatial form also set this directly, or is the flow rule that derives it for Spatial blackboxes load-bearing? If a Spatial-defined ctrl blackbox is staged outside a `Stream` controller, is the level resolution still correct?

Source: `src/spatial/lang/Blackbox.scala:28, 93`
Blocked by: —
Status: out-of-scope-for-v1
Resolution: (empty until resolved)

## Q-164 — [2026-04-24] `GEMMBox` direct-codegen vs `EarlyBlackbox` lowering (originally Q-irn-10)

Original ID: Q-irn-10
Original file: `open-questions-spatial-ir.md`

`GEMMBox` is the only `FunctionBlackbox` that doesn't extend `EarlyBlackbox` (`src/spatial/node/Blackbox.scala:18-35`) — codegen handles it directly without lowering. The DSL has stubbed `Blackbox.GEMV`/`CONV`/`SHIFT` (`src/spatial/lang/Blackbox.scala:121-123`). Will these follow the same direct-codegen pattern as GEMM, or will they go through `EarlyBlackbox` lowering with a `Stream { Fringe* }` synthesis?

Source: `src/spatial/node/Blackbox.scala:18-35`; `src/spatial/lang/Blackbox.scala:121-123`
Blocked by: —
Status: out-of-scope-for-v1
Resolution: (empty until resolved)
