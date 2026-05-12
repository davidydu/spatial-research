---
type: open-questions
topic: metadata
session: 2026-04-24
date_started: 2026-04-24
---

# Metadata Open Questions

## Q-meta-01 -- [2026-04-24] Raw schedule scratchpad finalization
`rawSchedule_=` writes `ControlSchedule` to `state.scratchpad`, while `finalizeRawSchedule` writes normal metadata. What pass sequence guarantees scratchpad schedules are finalized before downstream readers stop checking scratchpad?

Source: src/spatial/metadata/control/package.scala:785-789
Status: open
Resolution:

## Q-meta-02 -- [2026-04-24] `ConvertToStreamed` ownership
`ConvertToStreamed` is mirrored metadata, but the metadata source only exposes the getter/setter. Which pass consumes it, and should it remain mirrored in the Rust/HLS rewrite?

Source: src/spatial/metadata/control/ControlData.scala:287; src/spatial/metadata/control/package.scala:607-608
Status: open
Resolution:

## Q-meta-03 -- [2026-04-24] `HaltIfStarved` stream-stall model
The source comment says the stream-control rule is confusing and needs redesign. Can this boolean be replaced by a derived stream dependency model?

Source: src/spatial/metadata/control/ControlData.scala:228-243
Status: open
Resolution:

## Q-meta-04 -- [2026-04-24] Pseudo-edge exclusion policy
`DependencyEdge.isPseudoEdge` is defined in metadata, but the metadata package does not specify which queries must exclude pseudo-edges. Where should that policy live?

Source: src/spatial/metadata/access/AccessData.scala:49-60
Status: open
Resolution:

## Q-meta-05 -- [2026-04-24] Non-affine address fallback representation
`AddressPattern.getSparseVector` maps partially non-affine components to a fresh `boundVar[I32]`. Should the Rust port make this an explicit random-dimension node instead?

Source: src/spatial/metadata/access/AccessPatterns.scala:232-242
Status: open
Resolution:

## Q-meta-06 -- [2026-04-24] `accessIterators` and MemReduce ownership
`accessIterators` relies on scope iterator differences to handle MemReduce cross-subcontroller accesses. Should MemReduce stage ownership be modeled explicitly?

Source: src/spatial/metadata/access/package.scala:352-387
Status: open
Resolution:

## Q-meta-07 -- [2026-04-24] Accumulator lattice order
The requested reading expected `Fold > Reduce > Buff > None > Unknown`, but source `>` methods appear to implement `Fold > Buff > Reduce > None > Unknown`. Which is intended?

Source: src/spatial/metadata/memory/AccumulatorData.scala:11-45
Status: open
Resolution:

## Q-meta-08 -- [2026-04-24] `AccumulatorType` default
The metadata comment says default `AccumType.None`, but the package accessor defaults to `AccumType.Unknown`. Which default should the Rust port preserve?

Source: src/spatial/metadata/memory/AccumulatorData.scala:49-57; src/spatial/metadata/memory/package.scala:14-16
Status: open
Resolution:

## Q-meta-09 -- [2026-04-24] Mutable memory metadata state
`Memory.resourceType`, `Wait.ids`, and `setBufPort` introduce mutable or destructive metadata patterns. Should these become explicit pass-state updates in Rust?

Source: src/spatial/metadata/memory/BankingData.scala:186-188; src/spatial/metadata/memory/Synchronization.scala:14-20; src/spatial/metadata/memory/package.scala:250-258
Status: open
Resolution:

## Q-meta-10 -- [2026-04-24] LockDRAM banking fallbacks
LockDRAM accesses receive empty banking, `Set(0)` dispatch/group ids, and a default `Port(None, 0, 0, Seq(0), Seq(0))`. Are these semantic requirements or compatibility hacks?

Source: src/spatial/metadata/memory/package.scala:168-172; src/spatial/metadata/memory/package.scala:206-220; src/spatial/metadata/memory/package.scala:243-245
Status: open
Resolution:

## Q-meta-11 -- [2026-04-24] `FullDelay` transfer policy
`FullDelay` is mirrored, but it is also overwritten by the retiming analyzer. Should HLS transforms mirror, invalidate, or always recompute this metadata?

Source: src/spatial/metadata/retiming/RetimingData.scala:43-49; src/spatial/metadata/retiming/package.scala:15-21
Status: open
Resolution:

## Q-meta-12 -- [2026-04-24] Pure delay-line planning
`ValueDelay.value()` stages a delay line through a memoized closure. Can this be replaced by a pure allocation plan materialized in a deterministic transformer phase?

Source: src/spatial/metadata/retiming/ValueDelay.scala:13-18
Status: open
Resolution:

## Q-meta-13 — [2026-04-25] Bounds `makeFinal` mutates one bound then stores another
`makeFinal` sets `s.bound.isFinal = true` and then assigns `s.bound = Final(x)`, which appears to mark the previous bound object rather than the freshly stored `Final(x)`.

Source: src/spatial/metadata/bounds/package.scala:19; src/spatial/metadata/bounds/BoundData.scala:13-25
Blocked by: Search callers of `makeFinal` and `Final.unapply(Sym[_])`.
Status: open
Resolution:

## Q-meta-14 — [2026-04-25] Math residual reads `s.trace` but setter writes `s`
`getResidual` reads `metadata[Residual](s.trace)`, while `residual_=` writes `Residual(equ)` on `s`.

Source: src/spatial/metadata/math/package.scala:27-40
Blocked by: Search all `residual_=` callers and trace-rewriting passes.
Status: open
Resolution:

## Q-meta-15 — [2026-04-25] Param value wrappers may be bypassed
`IntParamValue` and `SchedParamValue` are declared metadata fields, but package accessors route integer values through bounds and schedule values through raw control schedule metadata.

Source: src/spatial/metadata/params/ParamDomain.scala:24-42; src/spatial/metadata/params/package.scala:31-41
Blocked by: Search repository-wide reads of `IntParamValue` and `SchedParamValue`.
Status: open
Resolution:

## Q-meta-16 — [2026-04-25] Symbol type helpers test symbol object for `isNum` and `isBits`
`SymUtils.isIdx` and `isString` inspect `x.tp`, but `isNum`, `isBits`, and `isVoid` use `x.isInstanceOf[...]`.

Source: src/spatial/metadata/types.scala:21-29
Blocked by: Verify intended Argon `Sym` class hierarchy and downstream callers.
Status: open
Resolution:

## Q-meta-17 — [2026-04-25] Blackbox config needs Rust+HLS ABI mapping
`BlackboxConfig` is shaped around file/module/latency/pipeline-factor/parameter data, but the Rust+HLS ABI for external modules is not specified here.

Source: src/spatial/metadata/blackbox/BlackboxData.scala:6-15
Blocked by: HLS blackbox design decision.
Status: open
Resolution:

## Q-meta-18 — [2026-04-25] `ShouldDumpFinal` comment appears stale
The comment above `ShouldDumpFinal` describes "reader symbols for each local memory", which does not match the boolean dump-final flag name or wrapper.

Source: src/spatial/metadata/debug/DebugData.scala:5-11
Blocked by: Confirm intended UI/pass behavior for `shouldDumpFinal`.
Status: open
Resolution:

## Q-meta-19 — [2026-04-25] `CLIArgs.listNames` consumer is unclear
The metadata source defines CLI argument names and dense listing behavior, but it does not identify the codegen or reporting path that consumes the names.

Source: src/spatial/metadata/CLIArgs.scala:8-17; src/spatial/metadata/CLIArgs.scala:35-46
Blocked by: Search codegen/reporting callers of `CLIArgs.listNames`.
Status: open
Resolution:

## Q-meta-20 — [2026-04-25] Explicit false `CanFuseFMA` is indistinguishable from absence
`canFuseAsFMA` uses `.exists(_.canFuse)`, so absent metadata and present `CanFuseFMA(false)` both read as false.

Source: src/spatial/metadata/rewrites/package.scala:8-9
Blocked by: Search callers that write `canFuseAsFMA = false`.
Status: open
Resolution:

## Q-meta-21 — [2026-04-25] `FreezeMem` comment is unfinished
The `FreezeMem` comment says the flag prevents memory banking patterns from being analyzed or changed, then ends after "Generally useful for when".

Source: src/spatial/metadata/transform/TransformData.scala:14-19
Blocked by: Search downstream `freezeMem` consumers.
Status: open
Resolution:
