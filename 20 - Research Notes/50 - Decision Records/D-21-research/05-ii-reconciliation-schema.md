---
type: "research"
decision: "D-21"
angle: 5
topic: "ii-reconciliation-schema"
---

# D-21 Research: II Reconciliation Schema

## Decision Surface

[[D-21]] should define a per-loop schedule record rather than adding one more scalar to existing controller metadata. Spatial already keeps three local concepts separate: user `II`, selected `II`, and `compilerII` (`src/spatial/metadata/control/ControlData.scala:153-177`; `src/spatial/metadata/control/package.scala:832-839`). `InitiationAnalyzer` computes outer controller `compilerII` from child intervals and inner controller `compilerII` from block interval, blackbox II, `iterDiff`, and latency, then chooses effective `II` from user override, sequenced schedule, or `min(compilerII, latency)` (`src/spatial/traversal/InitiationAnalyzer.scala:14-41`). D-21 adds the backend fact that an HLS tool may accept, relax, or reject the emitted request, so the schema must preserve all four stages without overwriting the old evidence ([[20 - Open Questions#Q-149 - 2026-04-25 Target accepted II versus compilerII (originally Q-sem-14)]]).

## Proposed Loop Identity

Every row should be keyed by `loop_identity`, not by a report string alone. Use `controller_uid` as the compiler-stable id, formed from `kernel_id`, IR symbol, parent-controller path, block index, source span, and a deterministic ordinal among sibling loops. Store `source_sym`, `source_ctx_line`, `source_ctx_text`, `ir_statement`, `controller_level`, `schedule_kind`, `parent_controller_uid`, and `loop_mapping_status`. Keep `hls_loop_label` and `hls_report_path` as backend aliases, because report labels can change with inlining, flattening, or tool version. The current runtime model already carries `id`, `level`, `schedule`, `L`, `II`, and `Ctx(id,line,info,stm)` (`models/src/models/RuntimeModel.scala:77-86`; `models/src/models/RuntimeModel.scala:192-200`), but it uses `lhs.hashCode` in generated controller ids (`src/spatial/model/RuntimeModelGenerator.scala:261-284`). D-21 should prefer deterministic identity over process-local hashes.

## Required Fields

- `user_requested_ii`: optional record from explicit user syntax, not a backend promise. Store `raw_value`, `normalized_positive_int`, `source = user_ii | absent`, `source_ctx`, and `validity = absent | accepted | invalid_fractional | invalid_nonpositive`. Spatial stores this as `UserII(interval: Double)`, while HLS pragmas normally need an integer request.
- `compiler_ii`: Spatial diagnostic estimate from `InitiationAnalyzer`, equivalent to existing `compilerII`/`spatial_compiler_ii` vocabulary. Store `value`, `estimate_status = computed | unavailable_fsm | defaulted`, `formula_version`, `interval`, `min_iter_diff`, `force_ii_1`, `slowest_blackbox_ii`, `body_latency`, and `dependence_evidence_ids`. This aligns with [[D-06]], which keeps Spatial `iterDiff` as explanation/request evidence, not final HLS authority.
- `selected_ii`: the old effective controller `II` used by Spatial control generation and runtime-model parity. Store `value`, `selection_reason = user_override | sequenced_latency | compiler_min_latency | outer_child_interval | state_machine_rule`, and `selected_by_pass`. This field is intentionally pre-HLS and should remain comparable to TreeGen's existing `II`/`CompilerII` mismatch display (`src/spatial/codegen/treegen/TreeGen.scala:126-131`).
- `hls_requested_ii`: the actual emitted request. Store `value`, `request_source = user_requested_ii | compiler_ii | selected_ii | conservative_fallback | hls_estimator`, `directive_kind`, `emission_location`, `backend`, `tool_profile`, and `request_status = emitted | suppressed | rejected_before_emit`.
- `hls_accepted_ii`: nullable post-tool result. Store `value`, `evidence_source = schedule_report | synthesis_report | tool_api | cosim_metadata`, `report_id`, `tool_name_version`, `parse_status`, and `accepted_status = unknown | accepted | accepted_higher | accepted_lower | tool_rejected | not_reported`.
- `latency_source`: enum matching [[D-08]]: `spatial_parity_fallback`, `hls_estimate`, `hls_report`, `simulation_validation`, or `unknown`. Include `latency_cycles`, `latency_status`, `confidence`, `estimator_version`, and `calibration_id` when present.
- `schedule_status`: reconciliation enum: `not_run`, `request_only`, `matched`, `accepted_higher`, `accepted_lower`, `tool_rejected`, `report_missing`, `report_unparseable`, `loop_mapping_ambiguous`, or `stale_report`. This is the user-facing summary for DSE, diagnostics, and decision records.
- `diagnostics`: list of structured messages with `severity`, `code`, `field`, `reason`, `source_span`, `evidence_ids`, and `suggested_action`. Initial codes should cover user-II normalization, unknown `iterDiff`, missing HLS loop mapping, report parse failure, accepted/requested mismatch, and latency-source fallback.

## Provenance Contract

Do not collapse `selected_ii`, `hls_requested_ii`, and `hls_accepted_ii` into one "current II." Pre-HLS consumers may rank by `selected_ii` or `compiler_ii` only when `latency_source = spatial_parity_fallback`; post-HLS consumers should prefer `hls_accepted_ii` when `schedule_status` is report-backed. This matches [[D-08]]'s hybrid report-calibrated estimator and [[D-20]]'s warning that delay-line cycle modes must state whether they assume compiler II, user request, estimated HLS II, or parsed accepted II. The migration rule is simple: write new evidence beside older evidence, never mutate away the reason a value was chosen.
