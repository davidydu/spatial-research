---
type: "research"
decision: "D-08"
angle: 7
---

# Spec/Open-Question Survey For HLS DSE Latency

## Decision Frame

D-08 is explicitly the choice of latency source for HLS DSE: the queue names the alternatives as Spatial runtime-model parity, HLS reports/simulation, or a new estimator (`20 - Research Notes/40 - Decision Queue.md:39-41`). Q-116 sharpens the same point: current DSE latency shells out to a compiled Scala runtime-model jar and parses `"Total Cycles for App"`, while HLS needs an equivalent cycle source from reports, simulation, or estimation (`20 - Research Notes/20 - Open Questions.md:1565-1575`). The spec confirms this is not an incidental implementation detail. Spatial DSE builds domains, evaluates area and latency, writes CSVs, and should carry that framework into HLS, but "the analyzers and runtime model need new HLS-specific estimators" (`10 - Spec/70 - Models and DSE/40 - Design Space Exploration.md:32`). It also says HLS cycle estimation should not depend on the old generated Scala runtime jar (`10 - Spec/70 - Models and DSE/40 - Design Space Exploration.md:62-64`).

## Current Spec Baseline

The existing latency source is high-throughput but detached from HLS tool feedback. `LatencyAnalyzer.test` finds a generated `RuntimeModel-assembly` jar, batches parameter rewrites, invokes Java, and parses total cycles; `compileLatencyModel` first builds `model_dse.scala` through a locked shell assembly step (`10 - Spec/70 - Models and DSE/40 - Design Space Exploration.md:52`). Each worker calls the cycle analyzer before evaluating per-point area, and runtime-model latency plus area rerun are the active per-point analyses (`10 - Spec/70 - Models and DSE/40 - Design Space Exploration.md:48`). The runtime model has rich controller equations for schedule cases, including inner sequenced and non-sequenced formulas over `L`, `II`, startup, shutdown, and masks, but sparse transfers still have TODO-like latency behavior (`10 - Spec/70 - Models and DSE/40 - Design Space Exploration.md:56`). So parity is useful as a compatibility baseline, not a complete HLS answer.

## Timing And II Dependencies

Timing is already split between compiler model and backend reality. The timing spec says cycle timing is introduced by Spatial retiming, latency models, and initiation analysis, while HLS has its own scheduler (`10 - Spec/20 - Semantics/70 - Timing Model.md:37`). Its controller formulas define model fill/drain behavior, not emitted RTL schedule by themselves (`10 - Spec/20 - Semantics/70 - Timing Model.md:41`). The II paragraph is decisive for D-08: `InitiationAnalyzer` writes compiler II, effective II incorporates user and schedule overrides, and a target-imposed II may differ at backend level; Rust should store both compiler-requested and backend-accepted values, with the HLS claim marked there as inferred/unverified (`10 - Spec/20 - Semantics/70 - Timing Model.md:57`). General HLS report latency and accepted-II fields are tool/vendor dependent (unverified), so D-08 should not assume one portable report schema.

## Coupling To D-06 And D-07

D-06 has already accepted a hybrid requested-II/report-reconciliation posture. It recommends preserving Spatial `iterDiff` as diagnostics and conservative requested-II evidence, but treating backend accepted II as authoritative once parsed (`20 - Research Notes/50 - Decision Records/D-06.md:45-47`). It explicitly says not to use the collapsed `iterDiff` scalar to decide final DSE latency after HLS reports are available (`20 - Research Notes/50 - Decision Records/D-06.md:85-90`), and follow-up work says runtime/DSE summaries should prefer `hls_accepted_ii` when available (`20 - Research Notes/50 - Decision Records/D-06.md:119-126`).

D-07 creates the parallel memory-side dependency. Its recommended HLS planner emits only HLS-lowerable complete/block/cyclic/reshape/duplicate/binding choices on the normal path (`20 - Research Notes/50 - Decision Records/D-07.md:52-81`) and requires an `HlsPartitionPlan` with partition, reshape, bank-depth, port, resource, evidence, fallback, and later `tool_accepted_partition` fields (`20 - Research Notes/50 - Decision Records/D-07.md:83-104`). It also adds report fields for requested versus accepted partition and connects them to D-08/D-21 latency and accepted-II reconciliation (`20 - Research Notes/50 - Decision Records/D-07.md:141-148`). Therefore latency cannot be only a scalar estimator; it must name the partition and II context that produced the number.

## Recommendation Implication

The spec survey points to a two-tier D-08 answer: keep Spatial runtime-model parity as a pre-tool fallback and regression baseline, but make report-calibrated HLS latency the destination. Pure HLS reports/simulation are too expensive for every hot DSE candidate (unverified), and pure simulation is input/testbench dependent rather than a broad estimator (unverified). A new estimator should therefore be the D-08 architecture, but it should consume D-06 accepted-II fields and D-07 partition-plan/report fields, then upgrade its confidence whenever HLS reports exist. Concise implication: choose **new HLS estimator with Spatial parity fallback and report/simulation calibration**, not old runtime-model parity as final authority.
