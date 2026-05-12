---
type: "research"
decision: "D-21"
angle: 9
topic: "hls-backend-policy-options"
---

# D-21 Research: HLS Backend Policy Options

## Current Spatial Contract

Spatial already separates three pre-HLS notions of II. The metadata layer defines controller `II` as the interval used for control signal generation, `userII` as user-defined metadata, and `compilerII` as an analysis-written estimate (`src/spatial/metadata/control/ControlData.scala:153-177`; `src/spatial/metadata/control/package.scala:832-839`). User syntax enters through `CtrlOpt.ii`, which writes `x.userII = ii.map(_.toDouble)` (`src/spatial/lang/control/CtrlOpt.scala:8-21`).

`InitiationAnalyzer` then chooses the pre-HLS value. For outer controls, it visits children, takes the maximum child `II` and at least `1.0`, writes effective `II` from `userII.getOrElse(interval)`, and records `compilerII = interval` (`src/spatial/traversal/InitiationAnalyzer.scala:14-21`). For inner controls, it computes body latency, slowest blackbox II, `iterDiff`, and `compilerII`, then chooses effective `II` from sequenced latency, `userII`, or `min(compilerII, latency)` (`src/spatial/traversal/InitiationAnalyzer.scala:23-41`). Current Chisel consumption reads `lhs.II` for controller construction and timing delays (`src/spatial/codegen/chiselgen/ChiselGenController.scala:338`; `src/spatial/codegen/chiselgen/ChiselGenCommon.scala:252-256`), while TreeGen highlights `II` and `CompilerII` mismatches (`src/spatial/codegen/treegen/TreeGen.scala:126-131`). [[C0 - Retiming]] marks the HLS retiming path as different: Chisel delay lines should not be ported directly; HLS would rely on pipeline II pragmas and scheduler-inserted registers (`10 - Spec/40 - Compiler Passes/C0 - Retiming.md:307-311`).

## Policy Options

**Emit requested II pragma from Spatial metadata.** This is the strongest continuity policy. The HLS backend emits a pipeline request from the D-21 `hls_requested_ii` field, usually sourced from explicit `userII` when present, otherwise from `selected_ii` or `compiler_ii` according to the chosen scheduler policy. It preserves user intent and keeps DSE estimates explainable, but it must not claim the tool accepted the request.

**Parse accepted II after synthesis.** This is the strongest correctness policy for performance reporting. General tool claim, unverified: Vivado/Vitis-like and Intel-like HLS reports usually expose loop schedule tables with achieved or final II, sometimes alongside requested II, latency ranges, loop labels, and warnings. Because formats, labels, and fields are vendor- and version-specific, D-21 should treat parsing as backend-adapter evidence, not a universal schema guarantee.

**Fail versus warn on mismatch.** A mismatch is usually a performance reconciliation issue, not an automatic functional failure. Default policy should warn when `accepted_ii > requested_ii` or `accepted_ii < requested_ii`, store `schedule_status = accepted_higher | accepted_lower`, and make DSE consume accepted II when available. Fail only when the user or CI selects a strict-II mode, when a user-stated hard contract cannot be met, when the tool rejects synthesis, or when a final report is required but missing/unparseable.

**Trust estimates when no report.** This is necessary for early search, but only as a labelled fallback. D-08 already recommends `hls_estimate` and `spatial_parity_fallback` as pre-report sources, with reports overriding or calibrating estimates once available. The dangerous policy is silently setting accepted II equal to requested II; that erases the exact uncertainty D-21 exists to record.

**Let backend default.** Suppressing II pragmas gives the tool maximum freedom and avoids invalid requests, but it discards Spatial's dependence and latency evidence. Use this only when the schedule is unlowerable, the backend lacks a valid positive integer request, or a target profile explicitly prefers tool autonomy. Tag it as `request_status = suppressed` with a fallback reason.

## Provenance And Report Feedback

Accepted II must be provenance-tagged because the value is conditional on the emitted code, partition plan, binding choices, inlining/flattening decisions, tool version, and report parser. The same source loop can be renamed or fused by the tool, and accepted II for one partition plan does not authorize another. D-07 already requires requested-versus-tool-accepted partition feedback, and D-08 makes HLS reports the post-tool authority for latency and accepted II (`20 - Research Notes/50 - Decision Records/D-08.md:63`). D-20 adds the simulator angle: any cycle-aware delay or timing mode must declare whether it assumes compiler II, requested II, estimated HLS II, or parsed accepted II (`20 - Research Notes/50 - Decision Records/D-20.md:54-60`).

Therefore each loop record should keep `compiler_ii`, `selected_ii`, `hls_requested_ii`, and `hls_accepted_ii` as separate fields. Store `evidence_source`, `report_path`, `tool_name_version`, `parse_status`, `loop_mapping_status`, and `fallback_reason`. General claims about vendor reports should remain tagged unverified until backed by local parser fixtures.

## Recommendation

Use a hybrid policy: emit an explicit requested II pragma when Spatial can produce a valid HLS request; parse accepted II from schedule/synthesis reports after tool runs; warn by default on requested/accepted mismatch; fail only under strict policy or hard report/tool failures; and keep estimates only as labelled pre-report fallbacks. Backend-default scheduling is an escape hatch, not the normal path. The contract should never overwrite Spatial `compilerII` or selected `II`; it should add backend evidence beside them and make consumers choose by provenance.
