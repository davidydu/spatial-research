---
type: "research"
decision: "D-19"
angle: 7
topic: "fma-policy-provenance-schema"
---

# D-19 Research: FMA Policy Provenance Schema

## Decision Surface

[[D-19]] should make FMA precision a recorded mode, not a hidden optimization result. The queue asks whether Rust+HLS matches Scalagen unfused multiply-add precision or Chisel/HLS fused FMA precision (`20 - Research Notes/40 - Decision Queue.md:83-85`). The current metadata is too small for that decision: `CanFuseFMA(canFuse)` is only a mirrored eligibility bit, and the getter collapses absent metadata with explicit false (`src/spatial/metadata/rewrites/CanFuseFMA.scala:5-10`; `src/spatial/metadata/rewrites/package.scala:7-9`; [[B0 - Rewrites]]). Since fusion defaults on (`src/spatial/SpatialConfig.scala:75-76`), `RewriteAnalyzer` marks hardware add-of-mul patterns (`src/spatial/traversal/RewriteAnalyzer.scala:42-58`), and `RewriteTransformer` creates `FixFMA`/`FltFMA` (`src/spatial/transform/RewriteTransformer.scala:263-274`), provenance must separate source algebra, compiler rewrite, and backend contraction.

## Required Fields

Use `fma_policy` as the top-level mode:

- `unfused_two_round_v1`: Scalagen-compatible `mul` then `add`.
- `fused_single_round_v1`: exact product-plus-add with one final cast/pack.
- `backend_native_fma`: target native FMA, not yet proven bit-identical.
- `backend_native_mul_add`: target/native expression, contraction status unknown.
- `disabled_no_fma_rewrite`: source stayed as ordinary operators.
- `rejected_unsupported`: backend cannot satisfy the requested policy.

Add `fma_node_kind = FixFMA | FltFMA | RegAccumFMA | source_add_mul`, `fusion_origin = rewrite_analyzer | reduce_accum_specialization | backend_contraction | source_unfused`, and `fusion_eligibility_state = absent | explicit_true | explicit_false`. The last field fixes the current `canFuseAsFMA` ambiguity without changing old semantics. Add `fusion_decision_pass`, `source_add_sym`, `source_mul_sym`, `reduce_cycle_id`, and for `RegAccumFMA`, `first_signal_id`. The reduction path needs this because `AccumAnalyzer` recognizes `FixFMA`/`FltFMA` cycles as `AccumMarker.Reg.FMA`, and `AccumTransformer` lowers them to `RegAccumFMA` (`src/spatial/traversal/AccumAnalyzer.scala:187-210`; `src/spatial/transform/AccumTransformer.scala:44-47`, `:110-120`; [[60 - Counters and Primitives]]).

## Round and Reclamp Events

Record `fma_rounding_points` as an ordered list of event records: `stage`, `numeric_kind`, `format`, `rounding_policy`, `float_pack_policy`, `event_id`, and `reclamp_count_delta`. For fixed unfused mode, the product shifts and clamps, then the add clamps again (`emul/src/emul/FixedPoint.scala:14-16`; `emul/src/emul/FixedPoint.scala:203-208`). If a future unbiased FMA exists, it must reuse [[D-17]] event identity rules; current stochastic fixed rounding consumes four guard bits and a random threshold in `FixedPoint.unbiased` (`emul/src/emul/FixedPoint.scala:232-240`). For float unfused mode, `FloatPoint.*` and `FloatPoint.+` each call `clamped`, and `clamped` packs through `clamp` then converts back (`emul/src/emul/FloatPoint.scala:153-157`; `emul/src/emul/FloatPoint.scala:417-427`). Therefore `unfused_two_round_v1` has two [[D-18]] reclamp events, while `fused_single_round_v1` has one final event. Include `intermediate_pack_policy` and `final_pack_policy`; for Scalagen parity both should normally be `scalagen_legacy_clamp_v1`.

## Backend Capability and Fallback

Backend metadata should say what was requested, what was emitted, and what evidence supports it. Scalagen emits both `FixFMA` and `FltFMA` as `($m1 * $m2) + $add`, and `RegAccumFMA` as `m0 * m1 + reg.value` (`src/spatial/codegen/scalagen/ScalaGenFixPt.scala:150`; `src/spatial/codegen/scalagen/ScalaGenFltPt.scala:120`; `src/spatial/codegen/scalagen/ScalaGenReg.scala:57-64`). Cppgen also emits plain `a * b + c` (`src/spatial/codegen/cppgen/CppGenMath.scala:34-36`). ChiselGen, however, lowers `FixFMA` and `FltFMA` through `Math.fma`, with fixed point cast back afterward (`src/spatial/codegen/chiselgen/ChiselGenMath.scala:50-51`). Fringe float `Math.fma` delegates to `bigIP.ffma`; the base hook can throw, while Zynq instantiates Xilinx floating-point IP configured as `Operation_Type {FMA}` (`fringe/src/fringe/templates/math/Math.scala:671-677`; `fringe/src/fringe/BigIP.scala:88-89`; `fringe/src/fringe/targets/zynq/ZynqBlackBoxes.scala:1217-1219`).

Recommended fields: `backend_fma_capability = exact_unfused_control | exact_fused_custom | native_fma_unverified | native_mul_add_unverified | unsupported`, `hls_contraction_control = off_verified | off_unverified | on | not_applicable`, `fallback_policy = reject | split_mul_add_for_parity | native_fma_declared | native_mul_add_declared`, plus `fallback_reason`, `tool_report_id`, and `capability_evidence`.

## Test Comparison Contract

Tests should compare policy before value. Existing tests prove shape and broad behavior, not fused-versus-unfused float bits: `FMAInLoop` distinguishes should-fuse and should-not-fuse sites (`test/spatial/tests/feature/math/FMAInLoop.scala:17-29`), `ReduceSpecialization` requires `RegAccumFMA` writers (`test/spatial/tests/feature/memories/reg/ReduceSpecialization.scala:215-229`), and `FloatBasics2` compares FMA against the same host expression (`test/spatial/tests/feature/math/FloatBasics2.scala:55`, `:88`). Add `fma_compare_mode = policy_equal_then_bits | dual_expected_bits | tolerance_with_policy | expected_divergence`. Golden files should store `expected_bits_unfused`, `expected_bits_fused`, `selected_fma_policy`, `rounding_points`, `backend_fma_capability`, and `fallback_policy`. A mismatch with different provenance should report "incomparable policy" before reporting a numeric failure.
