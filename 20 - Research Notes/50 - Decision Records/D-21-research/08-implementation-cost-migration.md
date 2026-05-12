---
type: "research"
decision: "D-21"
angle: 8
topic: "implementation-cost-migration"
---

# D-21 Research: Implementation Cost And Migration

## Baseline Cost Frame

Spatial's current implementation cost is low because the contract is scalar and pre-tool. Control metadata already separates `bodyLatency`, selected `II`, `userII`, and `compilerII`, but all are local compiler facts (`src/spatial/metadata/control/ControlData.scala:144-177`; `src/spatial/metadata/control/package.scala:826-839`). `InitiationAnalyzer` writes outer `compilerII` from child selected II and inner `compilerII` from latency, interval, blackbox II, and `iterDiff`, then chooses selected `II` from sequenced scheduling, user override, or `min(compilerII, latency)` (`src/spatial/traversal/InitiationAnalyzer.scala:14-41`; `10 - Spec/40 - Compiler Passes/C0 - Retiming.md:239-266`). The pass pipeline runs final initiation analysis before final runtime-model generation and reports (`src/spatial/Spatial.scala:226-237`).

The migration cost appears when consumers need post-HLS truth. Runtime models serialize only selected `lhs.II` and `bodyLatency.sum` into `ControllerModel(L, II)` (`src/spatial/model/RuntimeModelGenerator.scala:261-284`), and the model equation uses `(cchainIters - 1)*II + L + startup + shutdown + dpMask` for inner pipelines (`models/src/models/RuntimeModel.scala:192-200`, `models/src/models/RuntimeModel.scala:334-337`). DSE currently batches 1000 runtime-model queries and parses `"Total Cycles for App"` (`src/spatial/dse/LatencyAnalyzer.scala:14-46`). TreeGen can display `compilerII != II`, but existing reports mostly omit II (`src/spatial/codegen/treegen/TreeGen.scala:126-131`; `src/spatial/report/RetimeReporter.scala:35-63`; `src/spatial/report/MemoryReporter.scala:99-100`).

## Policy Cost Matrix

**A. Keep compiler II only: low implementation, high semantic debt.** This preserves current metadata, tests, runtime model, and DSE throughput. It needs little more than HLS codegen choosing a pragma source. But it imports Spatial's retiming-era estimate as authority even though [[70 - Timing Model]] says backend-imposed II can differ and should be stored separately (`10 - Spec/20 - Semantics/70 - Timing Model.md:57-65`). It also contradicts D-08's report-calibrated latency direction, where reports can carry accepted II and latency while the old jar is only a compatibility fallback (`20 - Research Notes/50 - Decision Records/D-08.md:31-39`).

**B. Overwrite compiler II with HLS accepted II: medium implementation, high migration risk.** This adds report parsing and loop mapping, then mutates the existing scalar. It is tempting because old consumers keep reading `compilerII`, but it destroys the explanation for why the compiler emitted its request. It also breaks the existing diagnostic surface where TreeGen highlights `CompilerII` as different from selected `II` (`src/spatial/codegen/treegen/TreeGen.scala:126-131`). Pre-report states become awkward: before HLS runs, the field is compiler estimate; after parsing, it silently changes meaning.

**C. Dual-record requested/compiler/accepted II with reconciliation status: medium-high implementation, lowest semantic risk.** This requires a per-loop schedule record keyed by stable identity, with `user_requested_ii`, `compiler_ii`, `selected_ii`, `hls_requested_ii`, `hls_accepted_ii`, `latency_source`, `schedule_status`, and diagnostics (`D-21-research/05-ii-reconciliation-schema.md:16-27`). It touches the compiler metadata adapter, HLS directive emitter, report parser, DSE estimator, manifest schema, report schema, and tests. The cost is real, but it lets pre-HLS consumers keep using selected/compiler II while post-HLS consumers prefer accepted II only when provenance exists (`D-21-research/05-ii-reconciliation-schema.md:29-31`).

**D. Report-first authority with compiler fields retained as provenance: high initial integration, best final operating model.** D is C plus a default precedence rule: report-backed `hls_accepted_ii` wins for performance summaries, calibration, and DSE readback; compiler fields remain explanation and fallback. It requires tool-run caches, stale-report detection, loop-label reconciliation, and hard failure states listed by the report-source note (`D-21-research/02-hls-report-sources.md:17-31`). It also aligns with D-20: cycle-aware delay-line diagnostics must name whether they assume compiler, user-requested, estimated HLS, or parsed accepted II (`20 - Research Notes/50 - Decision Records/D-20.md:54-65`).

## Affected Surfaces

The source modules are `spatial.metadata.control` for legacy field export, `InitiationAnalyzer` for formula evidence, any Rust/HLS loop identity and pragma emission layer, report parsers, DSE latency/estimator code, and user diagnostics. Existing report surfaces should be extended rather than repurposed: resource reports already have a JSON-shaped resource precedent (`src/spatial/codegen/resourcegen/ResourceReporter.scala:17-24`), while `Retime.report` is human-readable retiming evidence (`src/spatial/report/RetimeReporter.scala:10-15`, `src/spatial/report/RetimeReporter.scala:48-59`). Manifest/report schemas need `controller_uid`, backend/tool/version, request source, accepted status, latency source, calibration id, and failure reason. Diagnostics need structured codes for user-II normalization, missing loop mapping, report parse failure, accepted-higher/lower mismatch, tool rejection, stale report, and fallback latency.

## Staged Migration Plan

Phase 1: add the schedule record as sidecar manifest/report data with `hls_accepted_ii = unknown`; populate compiler, selected, user, and request fields from existing analysis. Phase 2: emit stable loop labels and HLS requested II, then parse reports into accepted/status fields without changing old scalar consumers. Phase 3: update DSE and timing summaries to use report-first authority when `schedule_status` is report-backed, preserving numeric `Cycles` for compatibility with CSV and HyperMapper (`src/spatial/dse/HyperMapperDSE.scala:70`, `src/spatial/dse/HyperMapperDSE.scala:127`). Phase 4: add mismatch fixtures for requested 1 accepted 2, accepted lower, missing report, stale report, and ambiguous loop mapping; then deprecate any UI or API that calls a single scalar "current II" authoritative.
