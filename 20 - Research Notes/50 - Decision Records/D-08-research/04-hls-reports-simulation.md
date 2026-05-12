---
type: "research"
decision: "D-08"
angle: 4
---

# HLS Reports And Simulation As DSE Latency Sources

## Current DSE Baseline

Spatial DSE currently has a cheap, batchable latency source: compile a generated Scala runtime model, run it with many candidate parameter settings, and parse one total-cycle line per point. `DSEAnalyzer.compileLatencyModel` requires `model/model_dse.scala`, guards compilation with a file lock, then shells out to `bash scripts/assemble.sh` from `gen_dir` (`src/spatial/dse/DSEAnalyzer.scala:96-128`, `src/spatial/dse/DSEAnalyzer.scala:137-147`). `LatencyAnalyzer.test` finds the `RuntimeModel-assembly` jar, groups rewrite points in batches of 1000, invokes `java -jar ... ni tune ...`, and extracts only lines containing `"Total Cycles for App"` (`src/spatial/dse/LatencyAnalyzer.scala:35-46`). The generated model emits exactly that total-cycle string after each tune point (`src/spatial/model/RuntimeModelGenerator.scala:145-153`).

That baseline is high-throughput but not HLS-grounded. It consumes Spatial `bodyLatency` and `II` when constructing controller models (`src/spatial/model/RuntimeModelGenerator.scala:261-284`), so any HLS path that chooses reports/simulation must replace or reconcile this source rather than pretend the current model already reflects HLS scheduling.

## Schedule And Synthesis Reports

HLS schedule/synthesis reports are the strongest report-backed candidate for D-08. D-06 already says v1 should record `hls_accepted_ii` from reports or tool APIs and treat it as unknown before reports exist, not silently equal to requested II (`D-06.md:62-69`). It also recommends that post-synthesis backend accepted II become authoritative for scheduling/performance once parsed (`D-06.md:45-47`). For latency, the corresponding report fields should be per-loop accepted II, per-loop latency, top-kernel latency, report source, and reconciliation status.

The fidelity advantage is that reports sit after HLS scheduling and resource binding decisions (unverified). They can expose accepted II and per-loop latency where the current DSE path only sees total app cycles (`src/spatial/dse/LatencyAnalyzer.scala:42-45`). The weakness is that report latency is still tool-estimated rather than execution-trace latency for specific input data (unverified). Reports also inherit D-07's partition dependency: accepted II and latency are only meaningful against the emitted HLS partition plan, because D-07 requires tool feedback such as `tool_accepted_partition` and report fields for requested versus accepted partition (`D-07.md:85-104`, `D-07.md:141-148`).

## C/RTL Simulation And Co-Simulation

C simulation is mainly a behavioral validation source, not a latency authority, unless the generated HLS C includes explicit cycle instrumentation (unverified). RTL simulation can count cycles for a concrete testbench and is therefore higher fidelity for that input set (unverified), but it does not naturally provide per-loop accepted II unless paired with report parsing or extra instrumentation (unverified). Co-simulation can compare C and RTL behavior and may report transaction latency for a testbench (unverified), but it is still vector-dependent and likely too expensive for hot-loop DSE (unverified).

For D-08, this means simulation should be calibration and failure triage, not the primary DSE latency source. Use it to validate representative design points, catch deadlocks or protocol mismatches, and sanity-check top latency against synthesis reports. Do not require full C/RTL or co-simulation for every candidate unless the search space is tiny, because the current local model batches 1000 candidates per process call (`src/spatial/dse/LatencyAnalyzer.scala:14`, `src/spatial/dse/LatencyAnalyzer.scala:37-39`).

## Cost, Batching, And Failure Modes

Report-backed DSE has much worse batching than the current model unless the HLS backend can synthesize many parameter points in one generated project. Spatial currently pays one model compile guarded by a lock, then many fast jar evaluations (`src/spatial/dse/DSEAnalyzer.scala:106-128`, `src/spatial/dse/LatencyAnalyzer.scala:37-41`). HLS reports usually require a tool run per generated design point or per small batch (unverified). That makes report latency high-fidelity but expensive.

Failure modes should be first-class statuses. Local D-06 already names `tool-rejected` and `unknown-report-format` reconciliation states (`D-06.md:65-69`). D-08 should add report-specific causes: synthesis did not run, report missing, parser schema mismatch, loop-name mapping failed, accepted II unavailable, latency range not scalar, partition report disagrees with D-07 plan, simulation timeout, and co-sim mismatch. Broad HLS report formats and directory names are vendor-specific (unverified), so parsing must be isolated behind a backend adapter rather than hard-coded into the DSE loop.

## D-08 Implication

If D-08 chooses "HLS reports/simulation," the best interpretation is **schedule/synthesis reports as the primary post-tool latency source, simulation/co-simulation as validation, and Spatial runtime-model parity only as the pre-report fallback**. This matches D-06's v1 hybrid: keep Spatial estimates for requested II and diagnostics, but prefer accepted II in runtime/DSE summaries after reports are available (`D-06.md:119-126`). It also matches D-07's posture that partition choices must be explicit before D-08/D-21 can reconcile latency and accepted II (`D-07.md:24-25`, `D-07.md:141-148`).

The required DSE contract is therefore two-tiered: before HLS, use the existing model or a conservative estimator for search pruning; after HLS, parse reports into authoritative `hls_accepted_ii`, per-loop/top latency, and source metadata. Simulation should gate confidence, not dominate the search loop.
