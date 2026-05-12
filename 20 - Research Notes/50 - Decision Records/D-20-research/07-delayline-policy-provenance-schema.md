---
type: "research"
decision: "D-20"
angle: 7
topic: "delayline-policy-provenance-schema"
---

# D-20 Research: DelayLine Policy Provenance Schema

## Decision Surface

[[D-20]] needs a provenance schema because `DelayLine` has two legitimate meanings today. In Scalagen it is value-transparent: constants emit nothing and non-constants emit only `val lhs = data` (`src/spatial/codegen/scalagen/ScalaGenDelays.scala:9-13`; [[60 - Counters and Primitives]]). In Chisel/RTL it is stateful timing: `ChiselGenDelay` emits a wire assigned through `DL(data.r, delay)` and updates `maxretime`, while `DL` gates the retimed value with backpressure and sometimes forward pressure (`src/spatial/codegen/chiselgen/ChiselGenDelay.scala:16-30`; `src/spatial/codegen/chiselgen/ChiselGenCommon.scala:288-293`; [[60 - Math and Primitives]]). The HLS mapping adds a third authority: [[C0 - Retiming]] says explicit Chisel delay-line insertion has no direct Vitis HLS analogue, so an HLS backend should rely on pipeline pragmas and scheduler-inserted registers rather than silently porting the retiming trio (`10 - Spec/40 - Compiler Passes/C0 - Retiming.md:307-311`; [[30 - Chisel-Specific]]).

## Required Fields

Use `delayline_policy` as the top-level semantic label:

- `compat_value_elided_v1`: `DelayLine(size, data)` is a value alias, matching Scalagen and Cppgen (`src/spatial/codegen/cppgen/CppGenDebug.scala:55`).
- `cycle_shift_register_v1`: model a Spatial/Chisel-style register chain.
- `hls_scheduler_authority_v1`: do not model explicit Spatial delay lines; record HLS schedule/report evidence instead.
- `rejected_unmodelled`: backend cannot satisfy the requested policy.

Each delay-line record should carry `delayline_origin = automatic_retiming | user_retime_api | backend_hls_schedule | imported_report`. The distinction is already in source: user calls to `retime(delay, payload)` reject negative delays, fold zero delay, stage `DelayLine`, and mark `userInjectedDelay = true` (`src/spatial/lang/api/MiscAPI.scala:23-31`), while automatic lines are created by `RetimingTransformer` from analyzer latencies (`src/spatial/transform/RetimingTransformer.scala:68-87`; `src/spatial/util/modeling.scala:570-649`). Keep `size_cycles`, `effective_size_cycles`, `size_source = user_api | computeDelayLines | hls_report | folded_zero`, and `size_status = exact | elided | estimated | backend_retimed`. `NodeParams` already treats non-user automatic delay depth as zero for modeling, so size provenance must not collapse user and compiler origins (`src/spatial/targets/NodeParams.scala:41`).

## Trace and Cycle Model

Add trace fields per static node: `delayline_sym`, `trace_root_sym`, `producer_sym`, `consumer_sym`, `reader_sym`, `hierarchy`, `value_delay_chain`, `prev_delayline_sym`, and `retiming_pass_id`. This mirrors `trace`, which recursively strips delay lines back to underlying data, and `ValueDelay.value()`, which memoizes shared or extended lines (`src/spatial/metadata/retiming/package.scala:23-31`; `src/spatial/metadata/retiming/ValueDelay.scala:13-18`). For switch and nested-block cases, also store `materialization_scope` and `case_alignment_delay`, because `precomputeDelayLines` and `retimeSwitchCase` can materialize shared outer lines or trailing case-result lines (`src/spatial/transform/RetimingTransformer.scala:102-130`, `:156-178`).

The run-level `cycle_model` should be `value_only | logical_cycle | rtl_flow_gated | hls_report_only`. If not `value_only`, require `advance_policy = always | controller_backpressure | backpressure_and_forwardpressure | accepted_ii_tick | valid_ready`, plus `reset_init_policy`, `initial_value_policy`, and `stall_policy`. This prevents a Rust cycle mode from claiming more than it models. The RTL template resets every stage to `init` and shifts only when `flow` is true (`resources/synth/vcs.hw-resources/RetimeShiftRegister.sv:22-39`), so a cycle-aware simulator must say whether it models flow, reset, and stalls.

## Backend Capability and HLS Evidence

Record `backend_delayline_capability = scalagen_alias | cpp_alias | chisel_flow_gated_shift_register | hls_native_scheduler | hls_manual_shift_register | unsupported`. Add `backend_emission = alias | explicit_register_chain | pragma_pipeline | tool_inferred_registers | none`, `fallback_policy = reject | elide_for_value | emit_manual_shift | rely_on_scheduler`, and `fallback_reason`.

HLS evidence belongs beside, not inside, the simulated value. Store `compiler_ii`, `user_ii`, `requested_hls_ii`, `hls_accepted_ii`, `accepted_ii_status`, `latency_estimate`, `latency_source`, `tool_name_version`, `schedule_report_id`, `cosim_trace_id`, and `report_parse_status`. `InitiationAnalyzer` already separates effective `II`, `compilerII`, `userII`, and body latency (`src/spatial/traversal/InitiationAnalyzer.scala:14-41`), and [[40 - Open HLS Questions]] elevates accepted-II reconciliation as Q-149. A `cycle_shift_register_v1` run may validate phasing under an assumed II, but `hls_scheduler_authority_v1` should win when report evidence exists.

## Comparison Contract

Golden files and mismatch reports should include `delayline_compare_mode = policy_equal_then_value | final_value_only | dual_expected_trace | expected_divergence | incomparable_policy`. In `policy_equal_then_value`, compare `delayline_policy`, `cycle_model`, origin, size, and backend capability before comparing outputs. In `dual_expected_trace`, store both `expected_value_elided` and `expected_cycle_trace` for targeted D-20 fixtures. A final-value pass under `compat_value_elided_v1` must not be reported as HLS timing proof; a cycle-trace pass under `cycle_shift_register_v1` must not rewrite legacy Scalagen goldens.
