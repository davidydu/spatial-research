---
type: "research"
decision: "D-21"
angle: 2
---

# HLS Report And Tool-Accepted II Sources

## Local Baseline

D-21 is the Q-149 contract question: where the Rust/HLS flow records and reconciles HLS tool-accepted II versus Spatial `compilerII` and requested II (`20 - Research Notes/40 - Decision Queue.md`). The local compiler already has two pre-tool II values. `InitiationAnalyzer` computes `compilerII` from block latency/interval, blackbox II, and `iterDiff`, then writes effective `II` after user-II and sequenced-schedule overrides (`src/spatial/traversal/InitiationAnalyzer.scala:23-41`). Outer controls use max child II plus any user II (`src/spatial/traversal/InitiationAnalyzer.scala:14-21`). `TreeGen` already exposes a mismatch when `compilerII != II`, printing `Latency`, `II`, and `CompilerII` for inner controls (`src/spatial/codegen/treegen/TreeGen.scala:126-131`). That is compiler intent, not target acceptance.

The specs already mark this boundary as HLS rework. [[70 - Timing Model]] says a target-imposed II can differ and that Rust should store compiler-requested and backend-accepted values separately. [[60 - Use and Access Analysis]] says HLS initiation analysis needs HLS-specific latency models because Spatial derives cycle lengths from retiming metadata and Spatial schedules. D-06 makes the same policy concrete: keep `spatial_compiler_ii`, `user_requested_ii`, `hls_requested_ii`, `hls_accepted_ii`, report source, and reconciliation status as distinct fields. D-08 then says reports should be the post-tool authority for accepted II and latency when they exist, while simulation/co-simulation is validation and triage rather than the default DSE objective.

## What Reports Should Provide

The normalized HLS schedule/synthesis report record should be keyed by stable controller/loop identity, design point, backend, tool version, target profile, and D-07 partition plan. At minimum it should provide:

- `hls_accepted_ii`: tool-achieved II per pipelined loop/controller, plus status `matched`, `accepted-higher`, `accepted-lower`, `not-pipelined`, `unknown`, or `rejected`.
- `achieved_latency`: top-kernel latency and per-loop/controller latency, preserving min/max/range if the tool reports a range rather than a scalar.
- `resource`: LUT, Reg/FF, BRAM, URAM when supported, DSP, LUT-as-logic, LUT-as-memory, and any backend-specific raw fields.
- `schedule_warnings`: dependence, memory-port, resource-sharing, unroll, dataflow, blackbox, clock-period, or unsupported-pragmas diagnostics.
- `failure_reason`: a structured cause when fields are absent or the run fails.

Local precedent for resource shape is narrower but useful. `ResourceReporter` summarizes LUT, Reg, BRAM, and DSP estimates (`src/spatial/codegen/resourcegen/ResourceReporter.scala:17-20`), while regression reporting stores LUT, Reg, BRAM/RAM, optional URAM, DSP, LUT-as-logic, LUT-as-memory, synth time, and timing-met status (`resources/regression/gdocs.py:291-347`). D-04 and D-07 add that resources and accepted schedules must be interpreted against requested storage classes and `tool_accepted_partition`, not as free-floating totals.

## Co-Simulation And Logs

Co-simulation should not be treated as the first source for accepted II. Local DSE currently evaluates latency by batching 1000 parameter rewrites through a generated runtime-model jar and parsing `"Total Cycles for App"` (`src/spatial/dse/LatencyAnalyzer.scala:29-47`); D-08 rejects replacing that hot loop with simulation for every point. Instead, co-sim/logs should provide validation status, observed cycle or transaction counts for the concrete testbench when available, mismatch/deadlock/timeout details, and enough workload identity to explain why a latency observation may not generalize.

The log contract should preserve every failure that prevents accepted-II trust: HLS not run, project generation failed, tool invocation failed, report missing, parser schema mismatch, controller/loop-name mapping failed, requested II not emitted, accepted II unavailable, accepted II conflicts across reports, latency missing or non-scalar, resource report missing, partition report disagrees with D-07, timing not met, C simulation failed, RTL simulation failed, co-simulation mismatch, timeout, or backend unsupported. Vendor-specific directory names and exact report field names are unverified here; the D-21 requirement is the normalized schema and provenance boundary, with backend adapters owning vendor parsing.

## Implication For D-21

The accepted-II source of truth should be report/tool feedback after HLS scheduling, not `compilerII`, effective Spatial `II`, or co-sim alone. Before reports exist, `hls_accepted_ii` must be unknown. After reports parse, DSE and timing summaries can prefer accepted II and achieved latency, while still retaining requested II, Spatial diagnostics, resources, warnings, and failure reasons for reconciliation.
