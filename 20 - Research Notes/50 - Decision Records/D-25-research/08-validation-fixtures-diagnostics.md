---
type: "research"
decision: "D-25"
angle: 8
topic: "validation-fixtures-diagnostics"
---

# D-25 Angle 8: Validation Fixtures And Diagnostics

## 1. Baseline Fixture Matrix

Validation should make the semantic fork visible before choosing the final policy. The current API stages `OneHotMux` and `PriorityMux` as distinct nodes (`src/spatial/lang/api/MuxAPI.scala:26-31`). The IR rewrite warns on multiple literal-true `OneHotMux` selectors but still returns the first literal-true lane (`src/spatial/node/Mux.scala:21-35`). Scalagen, however, collects all true lanes and `reduce{_|_}`s them (`src/spatial/codegen/scalagen/ScalaGenBits.scala:30-37`), while Chisel emits `Mux1H` (`src/spatial/codegen/chiselgen/ChiselGenMath.scala:226-229`). Therefore every fixture should run under `compat_or_reduce`, `checked_onehot`, `priority_multi_true`, and `poison_on_violation` where available.

Core fixtures: `ohm_zero_true_i32`, `ohm_single_true_i32`, `ohm_static_multi_true_i32`, and `ohm_dynamic_multi_true_i32`. Expected observations are: zero-true fails or reports invalid because Scalagen has no empty reduce fallback; single-true agrees across policies; static multi-true must expose the existing warning plus first-true rewrite; dynamic multi-true must match the current `MuxTest` OR gold in compatibility mode and fail in checked mode. `MuxTest` already gives the priority contrast: one-hot gold ORs all enabled values, while priority gold selects the first enabled entry (`test/spatial/tests/feature/unit/MuxTest.scala:20-40`).

## 2. Payload And Validity Cases

Add `ohm_bool_validity` with invalid selectors and invalid true payloads. The spec notes that Scalagen selector tests use `Bool.toBoolean`, not `toValidBoolean` (`10 - Spec/50 - Code Generation/20 - Scalagen/60 - Counters and Primitives.md:60-64`), while `Bool.|` ORs values and conjuncts validity (`emul/src/emul/Bool.scala:5-14`). The fixture should record whether invalid selectors are treated as active by value and whether any invalid true payload poisons the result.

Add `ohm_fixed_raw_or` with disjoint and overlapping bit patterns, for example raw `0b0011` and `0b0101`, because `FixedPoint.|` is raw integer OR with validity conjunction (`emul/src/emul/FixedPoint.scala:23-25`). This is the best canary for silent corruption: OR gives `0b0111`, priority gives the first raw value, and checked mode reports multi-true.

Add compile-time or explicit-mode fixtures for `ohm_float_payload`, `ohm_struct_payload`, and `ohm_vec_payload`. The spec says float `OneHotMux` lacks Scalagen `|` support (`10 - Spec/50 - Code Generation/20 - Scalagen/60 - Counters and Primitives.md:62-64`). Structs and vectors need a declared raw-bit rule because `asBits`/recast are field and element based (`argon/src/argon/lang/types/Bits.scala:71-82`, `argon/src/argon/lang/types/Bits.scala:148-170`; `argon/src/argon/lang/Vec.scala:217-226`). Default checked mode should accept them only when exactly one selector is true.

## 3. Diagnostics Labels

Use stable labels so tests can assert diagnostics, not just values. `W-D25-OHM-STATIC-MULTI` reports multiple literal-true selectors at staging. `E-D25-OHM-ZERO` reports no true selector when the chosen policy requires exactly one true. `E-D25-OHM-MULTI` reports runtime multi-true in checked mode. `W-D25-OHM-COMPAT-OR` marks a compatibility run that intentionally returns OR-reduced data. `E-D25-OHM-PAYLOAD` rejects float, struct, or vector OR-reduce when no raw-bit policy is selected. `E-D25-OHM-HLS-ASSERT` reports that the selected HLS target cannot implement the requested assertion or failure flag.

Severity should be policy-dependent. Static multi-true is a warning in `compat_or_reduce`, an error in `checked_onehot`, and an info-level compatibility note only when the op has been explicitly rewritten to `PriorityMux`.

## 4. Report Fields

Every emitted mux should produce a readback record with: `op_id`, `source_span`, `policy`, `selector_count`, `selector_static_values`, `true_count_static`, `true_count_runtime_min`, `true_count_runtime_max`, `payload_type`, `payload_width_bits`, `zero_true_policy`, `multi_true_policy`, `validity_policy`, `raw_bit_or_enabled`, `priority_order`, `assertion_mode`, `proof_source`, `hls_capabilities_used`, `fallback_reason`, `fixture_id`, `golden_source`, `observed_scalagen`, `observed_hls`, and `mismatch_kind`. These fields make D-25 auditable against the data-semantics spec, which already says OR-reduction is only semantically valid under exact one-hotness (`10 - Spec/20 - Semantics/50 - Data Types.md:58-59`).

## 5. HLS Assertion Behavior

HLS checked builds should generate `popcount(selects) == 1` as either a synthesis assertion, a C/RTL simulation assertion, or an explicit failure output. Chisel's current assertion path routes failed conditions into breakpoint wiring (`src/spatial/codegen/chiselgen/ChiselGenDebug.scala:29-34`), so the HLS port should report assertion presence and failure observability separately. Required assertion fixtures: pass on single-true, fail on zero-true, fail on dynamic multi-true, and prove-static on mutually exclusive switch-derived selectors. If `synth_assert` is unavailable, checked HLS must either emit a failure flag or reject the profile with `E-D25-OHM-HLS-ASSERT`; it must not silently fall back to unchecked OR.
