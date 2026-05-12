# D-08 Angle 8: Cost And Risk Analysis For HLS DSE Latency Source

## Baseline Cost Shape

Spatial DSE is built around a fast, batchable latency oracle: generate `model/model_dse.scala`, compile it once, then query a `RuntimeModel-assembly` jar for many retuned points. `DSEAnalyzer` compiles the latency model before dispatching to heuristic, brute force, experiment, or HyperMapper modes (`src/spatial/dse/DSEAnalyzer.scala:71-80`), and `compileLatencyModel` requires `model_dse.scala`, takes a lock, runs `bash scripts/assemble.sh`, and releases the lock (`src/spatial/dse/DSEAnalyzer.scala:90-147`). `LatencyAnalyzer.test` then groups rewrites by `batchSize = 1000`, shells out to `java -jar ... ni tune ...`, and parses `"Total Cycles for App"` lines (`src/spatial/dse/LatencyAnalyzer.scala:14`, `src/spatial/dse/LatencyAnalyzer.scala:35-46`). The DSE spec captures the implication: HLS should keep the parameter/domain/evaluate/CSV architecture, but HLS cycle estimation should not depend on the old Scala runtime jar (`10 - Spec/70 - Models and DSE/40 - Design Space Exploration.md:62-64`).

## Option Costs And Throughput

Preserving the old Spatial Scala runtime model as the HLS authority is the cheapest implementation path and has excellent throughput, because the batching and CSV contract already exist. Its cost is hidden correctness debt: the generated model is a Spatial controller hierarchy. `RuntimeModelGenerator` emits `AppRuntimeModel_dse`, applies `tune` maps, executes the model, and prints total cycles (`src/spatial/model/RuntimeModelGenerator.scala:111-153`); most controllers receive `L` from `lhs.bodyLatency.sum` and `II` from `lhs.II` (`src/spatial/model/RuntimeModelGenerator.scala:261-284`). That gives parity with legacy tests, not HLS scheduling, binding, or partitioning.

Using HLS reports as authoritative for every point has the opposite profile. Correctness is stronger after synthesis because reports can expose accepted II and scheduled latency, which matches D-06's rule that backend accepted II is authoritative when available (`D-06.md:45-47`, `D-06.md:65-69`). But throughput is poor: current heuristic mode enumerates legal points and samples up to 75,000, while experiment mode caps each trial at 100,000 (`src/spatial/dse/DSEAnalyzer.scala:238-278`). Running HLS for each point would replace one jar query per thousand candidates with many tool invocations.

Simulation or co-simulation for every point is even more expensive. It can validate concrete behavior and measured transaction latency, but it needs generated testbenches, input vectors, run management, timeout handling, and result attribution. It also does not naturally provide per-loop accepted II, so it still depends on report parsing for the schedule fields D-06 wants.

Building a new fast HLS estimator has the highest compiler-side design cost among the fast options: it must model HLS-visible loops, accepted/requested II, operator latency, memory-port limits, and D-07 partition plans. Its throughput, however, can match or exceed the old jar path because it can stay in-process and batch over DSE points without invoking HLS tools.

## Correctness Risk

The runtime-model authority option has the highest semantic risk. `RuntimeModel.cycsPerParent` uses Spatial schedule cases and fixed overhead constants; inner non-sequenced controls are `(cchainIters - 1)*II + L + startup + shutdown + dpMask`, while dense transfers call a congestion model and sparse transfers return placeholder `1` values (`models/src/models/RuntimeModel.scala:205-212`, `models/src/models/RuntimeModel.scala:312-338`). D-06 already rejects letting Spatial's collapsed schedule evidence override HLS backend truth or decide final DSE latency after reports exist (`D-06.md:85-90`). D-07 adds another coupling: latency must be interpreted against the actual HLS partition plan and tool-accepted partition feedback (`D-07.md:85-104`, `D-07.md:141-148`).

Report authority has lower modeling risk but higher availability risk: reports may be missing, tool-rejected, schema-shifted, or unmappable to compiler loops. Simulation has high concrete fidelity only for the tested vectors; it is weak as a general DSE objective. A new fast estimator has medium correctness risk at first, because it must rebuild loop, memory, II, and transfer assumptions, but it can be designed around HLS-visible constructs rather than retrofitting Chisel-era constants.

## Maintenance Burden

Keeping the Scala model preserves the most legacy code: generator, SBT assembly, jar discovery, stdout parsing, ask maps, and Spatial-only equations. Reports-everywhere pushes maintenance into vendor parsers, naming reconciliation, cache invalidation, and failure-state taxonomy. Simulation-everywhere adds the largest operational burden because failures are often environmental, vector-dependent, or timeout-driven. A new estimator is nontrivial to build, but it localizes maintenance in one HLS latency module and can use reports as calibration data instead of making every DSE point a tool run.

## Recommendation

Choose the hybrid: a fast HLS estimator for broad search, HLS reports for calibration and final authority, and simulation/co-simulation for validation. This has medium implementation cost, high search throughput, and the best correctness/maintenance tradeoff. It follows D-06's requested-versus-accepted reconciliation model and D-07's explicit partition-plan feedback, while avoiding the DSE throughput collapse of report or simulation authority on every point. Preserve the old Spatial runtime model only as a parity baseline and diagnostic fallback; do not make it the HLS authority.
