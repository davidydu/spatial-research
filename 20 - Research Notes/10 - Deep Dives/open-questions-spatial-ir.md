---
type: open-questions
date_started: 2026-04-24
---

# Open Questions — Spatial IR Nodes

Per-entry open questions raised during distillation of [[spatial-ir-nodes]] into spec entries under `10 - Spec/30 - IR/10 - Spatial Nodes/`. IDs use the prefix `Q-irn-NN` (zero-padded). Resolved entries stay in this file with their resolution noted.

## Q-irn-01 — [2026-04-24] `IterInfo` vs `IndexCounter` redundancy

The `counter_=` setter (`src/spatial/metadata/control/package.scala:1089-1091, 1098-1100`) writes both `IndexCounter(info)` on the iterator and `IterInfo(iter)` on the counter — a bidirectional binding. Is `IterInfo` ever queried independently of `IndexCounter`, or could the bidirectional metadata be collapsed to a single direction (counter → iter via a controller's `iters` field)?

Source: `src/spatial/metadata/control/ControlData.scala:136, 142`; `src/spatial/metadata/control/package.scala:1086-1102`
Blocked by: —
Status: open
Resolution: (empty until resolved)

## Q-irn-02 — [2026-04-24] LaneStatic insertion coverage

`LaneStatic` is only inserted by `CounterIterRewriteRule` for three modular-arithmetic patterns (`iter % par`, `(iter / step) % par`, `((iter - start) / step) % par`). Are there other lane-index expressions (e.g., `(iter / par) % submap`) that should also fold to `LaneStatic` but currently don't? If so, are they handled at codegen instead?

Source: `src/spatial/rewrites/CounterIterRewriteRule.scala:18-37`
Blocked by: —
Status: open
Resolution: (empty until resolved)

## Q-irn-03 — [2026-04-24] `IndexCounterInfo.lanes` ordering significance

Post-unroll, `IndexCounterInfo.lanes: Seq[Int]` carries a list of physical lane indices. Is the ordering significant (e.g., does lane index 0 always correspond to the lowest-id iterator), or is it a set that happens to be encoded as a `Seq`? The unroller (`src/spatial/transform/unrolling/UnrollingBase.scala:455-487`) constructs both `[i]` (singleton) and `[parAddr(p)(ci) for p in 0..V-1]` (vector) lane lists, but it's unclear whether downstream consumers depend on a specific order.

Source: `src/spatial/metadata/control/ControlData.scala:39`; `src/spatial/transform/unrolling/UnrollingBase.scala:464, 466, 481`
Blocked by: —
Status: open
Resolution: (empty until resolved)

## Q-irn-04 — [2026-04-24] PriorityMux warn asymmetry

`OneHotMux.rewrite` warns at staging time on multiple statically-true selects (`src/spatial/node/Mux.scala:25-28`). `PriorityMux` has the same warning code path but it's commented out (`Mux.scala:43-51`). Is the asymmetry intentional (priority muxes have well-defined precedence so multi-true is fine), or is the commented-out branch dead code that should be re-enabled with a different message?

Source: `src/spatial/node/Mux.scala:21-36, 41-56`
Blocked by: —
Status: open
Resolution: (empty until resolved)

## Q-irn-05 — [2026-04-24] `RegAccumLambda` codegen complexity bound

`RegAccumLambda` takes a `Lambda1[A,A]` for arbitrary user-defined reductions. Codegen must support *any* lambda, but accumulator codegen relies on single-cycle RMW assumption (`#pragma HLS DEPENDENCE inter false` in HLS terms; equivalent retiming behavior in Chisel). Is there a complexity bound (latency, dependence) that the analyzer enforces, or does codegen just inline whatever lambda is given and hope for the best? If the lambda has long latency, what happens to the accumulator's first-iteration semantics?

Source: `src/spatial/node/Accumulator.scala:52-57`
Blocked by: —
Status: open
Resolution: (empty until resolved)

## Q-irn-06 — [2026-04-24] `Transient[R]` cross-layer split

`Transient[R]` is a Spatial subclass that fixes `isTransient = true`, but `argon.node.Primitive[R]` already exposes `isTransient` as a `val`. The TODO in `src/spatial/node/Transient.scala:9` notes "This is a bit odd to have Primitive in argon and Transient in spatial." Could `Transient` be merged into argon as a renamed `Primitive` constructor flag, or is the cross-layer split load-bearing for some reason (e.g., `Transient.unapply`'s dependence on `spatial.metadata.bounds.Expect`)?

Source: `src/spatial/node/Transient.scala:9-19`; `argon/src/argon/node/DSLOp.scala:13-15`
Blocked by: —
Status: open
Resolution: (empty until resolved)

## Q-irn-07 — [2026-04-24] `FieldDeq.effects` correctness

`FieldDeq.effects` is conservatively pure (inherits `Primitive` default), but the TODO at `src/spatial/node/StreamStruct.scala:14-15` says it should be `Effects.Writes(struct)`. The TODO also notes the obstacle: applying the effect to a bound symbol inside a `SpatialCtrl` blackbox body is ambiguous. What concrete bug would arise from setting the correct effect, and is the bound-sym issue the only obstacle?

Source: `src/spatial/node/StreamStruct.scala:12-16`
Blocked by: —
Status: open
Resolution: (empty until resolved)

## Q-irn-08 — [2026-04-24] `FieldEnq` reachability

`FieldEnq` carries a `// TODO: FieldEnq may not actually be used anywhere` comment (`src/spatial/node/StreamStruct.scala:18`) but is staged by `StreamStruct.field_update` (`src/spatial/lang/StreamStruct.scala:36`). Is `field_update` reachable from any DSL surface API, or is it dead code that the TODO predates? If unreachable, can `FieldEnq` be removed from the IR surface?

Source: `src/spatial/node/StreamStruct.scala:18-22`; `src/spatial/lang/StreamStruct.scala:36`
Blocked by: —
Status: open
Resolution: (empty until resolved)

## Q-irn-09 — [2026-04-24] `SpatialCtrlBlackboxUse` rawLevel not set at staging

`VerilogCtrlBlackbox` sets `rawLevel = Inner` explicitly at staging (`src/spatial/lang/Blackbox.scala:93`); `SpatialCtrlBlackboxUse` does not (`src/spatial/lang/Blackbox.scala:28`). Should the Spatial form also set this directly, or is the flow rule that derives it for Spatial blackboxes load-bearing? If a Spatial-defined ctrl blackbox is staged outside a `Stream` controller, is the level resolution still correct?

Source: `src/spatial/lang/Blackbox.scala:28, 93`
Blocked by: —
Status: open
Resolution: (empty until resolved)

## Q-irn-10 — [2026-04-24] `GEMMBox` direct-codegen vs `EarlyBlackbox` lowering

`GEMMBox` is the only `FunctionBlackbox` that doesn't extend `EarlyBlackbox` (`src/spatial/node/Blackbox.scala:18-35`) — codegen handles it directly without lowering. The DSL has stubbed `Blackbox.GEMV`/`CONV`/`SHIFT` (`src/spatial/lang/Blackbox.scala:121-123`). Will these follow the same direct-codegen pattern as GEMM, or will they go through `EarlyBlackbox` lowering with a `Stream { Fringe* }` synthesis?

Source: `src/spatial/node/Blackbox.scala:18-35`; `src/spatial/lang/Blackbox.scala:121-123`
Blocked by: —
Status: open
Resolution: (empty until resolved)
