---
type: "research"
decision: "D-17"
angle: 10
---

# Recommendation Matrix

## Decision Frame

[[D-17]] should choose the canonical meaning of `Unbiased`, not just the Rust simulator default already proposed by [[D-09]]. The queue frames D-17 as deciding whether unbiased rounding matches nondeterministic Spatial behavior, becomes seedable, or is replaced by deterministic rounding (`20 - Research Notes/40 - Decision Queue.md:75-77`). Current reference behavior is stochastic: `*&`, `/&`, `*&!`, and `/&!` manufacture four guard fractional bits before calling `FixedPoint.unbiased`, and the helper shifts by four, computes a 1/16 remainder, calls `scala.util.Random.nextFloat()`, then steps nonnegative values up or negative values down before wrapping or saturating (`/Users/david/Documents/David_code/spatial/emul/src/emul/FixedPoint.scala:52-63`, `/Users/david/Documents/David_code/spatial/emul/src/emul/FixedPoint.scala:232-240`). [[20 - Numeric Reference Semantics]] and [[50 - Data Types]] both treat Scalagen plus `emul` as the numeric reference.

## Option Matrix

| Option | Strength | Problem | D-17 disposition |
|---|---|---|---|
| Ambient JVM nondeterminism | Closest to today's Scala helper and generated Scalagen calls (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/scalagen/ScalaGenFixPt.scala:96-114`). | No explicit seed, algorithm, event identity, or replay contract; it canonizes a host artifact rather than a language rule. | Reject as canonical. Keep only as a legacy compatibility mode if needed. |
| Seeded stable stochastic | Preserves the probability law, signed legacy step, wrap/saturate split, and [[D-09]] replay goal while making sequence choice explicit. | Requires stable event IDs, seed provenance, and backend conformance metadata. | Recommend as canonical. |
| Deterministic RNE/half-up/trunc | Simple to test and likely cheaper for HLS libraries (unverified). `Truncate` already exists as a distinct Fringe mode (`/Users/david/Documents/David_code/spatial/fringe/src/fringe/templates/math/RoundingMode.scala:3-8`). | RNE is a clean deterministic replacement (unverified), but all deterministic choices redefine current stochastic `Unbiased`; half-up and trunc are not statistically unbiased (unverified). | Reject for `Unbiased`; expose as separate named modes or fallbacks. |
| Capability-gated HLS approximations | Lets HLS targets use native deterministic quantization or vendor primitives when stochastic support is absent (unverified). | Silent approximation would make HLS results incomparable to the reference. BigIP already has many target-dependent or unimplemented arithmetic paths, so fallback policy must be explicit (`/Users/david/Documents/David_code/spatial/fringe/src/fringe/BigIP.scala:22-105`; [[50 - BigIP and Arithmetic]]). | Allow only as declared non-canonical fallback. |

## Recommendation

Adopt **seeded stable stochastic rounding** as the canonical D-17 policy, specifically `seeded_stochastic_legacy_away` from [[07-cross-backend-provenance-schema]]. The canonical threshold is a pure function of `(seed, algorithm_version, static_op_id, dynamic_instance_id, lane_or_element_id)` and the current four-guard-bit remainder rule. The result should preserve current signed behavior: when the stochastic threshold fires, line 238 moves positive biased values to `biased + 1` and negative biased values to `biased - 1` (`/Users/david/Documents/David_code/spatial/emul/src/emul/FixedPoint.scala:238`).

This policy fits the evidence better than deterministic replacement. Chiselgen already distinguishes `Unbiased` from `Truncate` for multiply, divide, and fixed casts (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/chiselgen/ChiselGenMath.scala:33-40`, `/Users/david/Documents/David_code/spatial/src/spatial/codegen/chiselgen/ChiselGenMath.scala:75-78`). Fringe defines `Unbiased` as LFSR stochastic rounding and implements fractional shrink by adding PRNG low bits before shaving (`/Users/david/Documents/David_code/spatial/fringe/src/fringe/templates/math/RoundingMode.scala:3-8`, `/Users/david/Documents/David_code/spatial/fringe/src/fringe/templates/math/Converter.scala:36-44`). Existing tests also check distributional behavior, not JVM sequence parity: `SpecialMath` averages 256 `*&` samples and checks the mean within one `_4` LSB, while saturation endpoints are exact (`/Users/david/Documents/David_code/spatial/test/spatial/tests/feature/math/SpecialMath.scala:51-61`, `/Users/david/Documents/David_code/spatial/test/spatial/tests/feature/math/SpecialMath.scala:74-94`; [[05-tests-apps-statistical-expectations]]).

## Rejected Alternatives and Fallbacks

Reject ambient JVM nondeterminism because it blocks reproducible CI and does not map to HLS or hardware. Existing Fringe PRNG seeding is also ambient at elaboration time, and the PRNG advances when enabled; that is evidence for stochastic intent, not for accepting unrecorded randomness as semantics (`/Users/david/Documents/David_code/spatial/fringe/src/fringe/templates/math/Converter.scala:40-42`, `/Users/david/Documents/David_code/spatial/fringe/src/fringe/templates/math/PRNG.scala:13-25`; [[03-hardware-chisel-fringe-rounding]]).

Reject deterministic RNE, half-up, and truncation as the canonical meaning of `Unbiased`. If the project wants RNE, it should be a deliberate language migration that updates Scala emul, Rust, tests, and HLS together. Half-up and truncation should not inherit the name "unbiased"; truncation already has an IR/backend identity.

Allow capability-gated HLS approximations only with manifest fields such as `rounding_policy`, `rng_algorithm`, `seed`, `advance_policy`, `backend.capability`, and `fallback`. A target that cannot implement the stable stochastic rule should either reject canonical `Unbiased` or emit an auditable fallback such as `deterministic_rne`, never claim canonical parity. This is the clean handoff from [[D-09]] and [[10-recommendation-matrix-d17-handoff]]: seeded stochastic replay becomes the language rule, while nonconforming HLS paths are visible exceptions.
