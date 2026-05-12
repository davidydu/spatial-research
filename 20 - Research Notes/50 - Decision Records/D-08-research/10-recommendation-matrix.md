---
type: "research"
decision: "D-08"
angle: 10
---

# Recommendation Matrix And Migration Plan

## Decision Frame

D-08/Q-116 asks whether HLS DSE latency should come from Spatial runtime-model parity, HLS reports/simulation, or a new estimator (`20 - Research Notes/40 - Decision Queue.md:39-41`). The existing DSE path is optimized for throughput: it compiles `model_dse.scala` once, shells out to `bash scripts/assemble.sh`, then `LatencyAnalyzer` runs a `RuntimeModel-assembly` jar in batches of 1000 `tune` maps and parses `"Total Cycles for App"` (`src/spatial/dse/DSEAnalyzer.scala:90-147`, `src/spatial/dse/LatencyAnalyzer.scala:29-47`). `DSEThread` expects one cycle value per point and emits that as the `Cycles` column beside area and validity (`src/spatial/dse/DSEThread.scala:109-151`; `10 - Spec/70 - Models and DSE/40 - Design Space Exploration.md:48-52`). The replacement must preserve that batch contract or deliberately revise every CSV/HyperMapper consumer.

## Decision Matrix

Scores use 5 = best fit, 1 = weakest fit.

| Policy | DSE throughput | Semantic fidelity | HLS backend compatibility | D-06/D-21 accepted-II fit | D-07 partition fit | Implementation cost | Provenance/debuggability |
|---|---:|---:|---:|---:|---:|---:|---:|
| Spatial runtime-model parity | 5 | 2 | 2 | 2 | 2 | 5 | 3 |
| HLS reports-only | 1 | 5 | 3 | 5 | 5 | 2 | 4 |
| HLS simulation-only | 1 | 3 | 2 | 2 | 3 | 2 | 3 |
| New estimator-only | 4 | 3 | 3 | 3 | 4 | 1 | 4 |
| Hybrid report-calibrated estimator | 4 | 4 | 4 | 5 | 5 | 3 | 5 |

Spatial parity wins only on throughput and cost. The runtime model has a useful controller tree, with each controller carrying `L`, `II`, schedule, cchains, context, and fixed control overhead constants (`models/src/models/RuntimeModel.scala:192-212`). Its hot inner equation, `(cchainIters - 1)*II + L + startup + shutdown + dpMask`, is portable as a shape if HLS supplies the right `L` and accepted `II` (`models/src/models/RuntimeModel.scala:320-337`). But the generator serializes Spatial `bodyLatency` and `lhs.II`, not backend-accepted HLS schedules (`src/spatial/model/RuntimeModelGenerator.scala:261-284`), and the target latency model includes Spatial CSV fields, retime-register flags, and controller formulas whose numeric data are target-specific (`src/spatial/targets/LatencyModel.scala:17-67`; `10 - Spec/70 - Models and DSE/20 - Latency Model.md:23-35`).

## Policy Interpretation

Reports-only has the best post-tool truth value, especially for accepted II, but it is too slow as the inner search objective unless HLS synthesis can be cached or batched at a very different granularity. Simulation-only is even less suitable as the primary source: it can validate concrete workloads and expose wrapper/back-pressure behavior, but it is input-dependent and does not naturally produce per-loop accepted II. New-estimator-only is cleaner than runtime parity, but making it authoritative before calibration risks replacing one stale oracle with another.

D-06 and D-21 make a single unlabelled `Cycles` number unsafe. D-06 recommends preserving Spatial estimates for requested-II diagnostics, but treating backend accepted II as authoritative once reports exist (`20 - Research Notes/50 - Decision Records/D-06.md:45-48`). It also says not to use the collapsed Spatial scalar to decide final DSE latency after HLS reports are available (`20 - Research Notes/50 - Decision Records/D-06.md:85-90`), while D-21 is queued specifically to separate HLS accepted II from compiler/requested II (`20 - Research Notes/40 - Decision Queue.md:91-93`). D-07 adds the memory side: latency must be interpreted against an `HlsPartitionPlan` with partition kind, factor, duplicate count, port model, binding preference, fallback reason, and later `tool_accepted_partition` (`20 - Research Notes/50 - Decision Records/D-07.md:83-104`). That makes the hybrid the only option that scores well across accepted-II reconciliation and banking/partition interaction.

## Recommendation And Migration Plan

**Named recommendation: adopt the Hybrid Report-Calibrated Estimator policy.** Keep Spatial runtime-model parity as the labelled v1 pre-HLS fallback and regression baseline. Add an HLS estimator interface that returns `{cycles, confidence, latency_source, report_id, calibration_id, fallback_reason}` per point, while preserving the existing batch order and numeric `Cycles` column for current DSE/HyperMapper consumers. Its initial equation can reuse the runtime-model controller shape, but must take `hls_requested_ii`, `hls_accepted_ii` when known, HLS operator latency tables, and D-07 partition-plan features as inputs.

Migration steps: first, add provenance columns beside `Cycles`: `latency_source`, `latency_status`, `confidence`, `hls_report_source`, `ii_reconciliation_status`, and partition-plan id, without changing the minimization column. Second, parse HLS reports into accepted II, per-loop latency, top latency, and report-status records; use simulation/co-simulation only for sampled validation and mismatch triage. Third, calibrate estimator residuals by backend, tool version, target, controller signature, accepted II, and partition plan. Fourth, when confidence is `report_exact` or calibrated above threshold, rank DSE points by HLS-grounded latency; otherwise fall back to labelled Spatial parity. This matches the DSE spec's conclusion that the queue/writer architecture can carry over, but HLS cycle estimation should not depend on the old generated Scala runtime jar as final authority (`10 - Spec/70 - Models and DSE/40 - Design Space Exploration.md:60-64`).
