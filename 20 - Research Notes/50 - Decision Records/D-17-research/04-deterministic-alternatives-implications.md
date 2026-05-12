---
type: "research"
decision: "D-17"
angle: 4
---

# Deterministic Alternatives and Implications

## Current Contract And Decision Test

D-17 asks what Spatial should canonically mean by "unbiased" rounding. The current reference is stochastic, not round-to-nearest-even: `FixedPoint.unbiased` receives four guard fractional bits, shifts to `biased = bits >> 4`, computes a 1/16-granularity remainder, draws `scala.util.Random.nextFloat()`, and steps away from zero when `rand + remainder >= 1` before wrapping or saturating (`/Users/david/Documents/David_code/spatial/emul/src/emul/FixedPoint.scala:52-63`, `/Users/david/Documents/David_code/spatial/emul/src/emul/FixedPoint.scala:232-240`). Scalagen emits unbiased multiply/divide and unbiased casts directly to these helpers (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/scalagen/ScalaGenFixPt.scala:96-114`), while [[20 - Numeric Reference Semantics]] and [[50 - Data Types]] label Scalagen plus `emul` as numeric reference behavior.

The hardware story also points stochastic: Fringe defines `Unbiased` as LFSR stochastic rounding and `fix2fixBox` adds PRNG low bits before shaving fractional bits (`/Users/david/Documents/David_code/spatial/fringe/src/fringe/templates/math/RoundingMode.scala:3-8`, `/Users/david/Documents/David_code/spatial/fringe/src/fringe/templates/math/Converter.scala:36-44`). D-09 therefore recommends "Seeded Stable Stochastic Rounding" for the Rust simulator, with D-17 owning any canonical redefinition ([[D-09]], [[06-seedable-rng-policy]], [[10-recommendation-matrix-d17-handoff]]).

## Deterministic Arithmetic Rules

Round-to-nearest-even is the cleanest deterministic arithmetic replacement. It matches familiar IEEE/HLS naming: Intel documents IEEE default `roundTiesToEven`, and AMD Vitis HLS exposes `AP_RND_CONV` as ties-to-even convergent rounding ([Intel rounding schemes](https://www.intel.com/content/www/us/en/docs/programmable/683242/current/rounding-schemes.html), [AMD UG1399 quantization modes](https://docs.amd.com/r/en-US/ug1399-vitis-hls/Quantization-Modes)). It gives perfect bit reproducibility and cheap hardware lowering. It is not statistically equivalent to current Spatial: all non-tie fractional residues become fixed choices instead of distance-proportional probabilities. Its long-run bias depends on value distribution and tie/LSB patterns [numeric-claim: not source-grounded here]. Compatibility churn would be high: stochastic tests, golden outputs, and HLS parity language must all change.

Round-half-up and round-half-away are simpler to specify but weaker as "unbiased" candidates. Half-up privileges upward ties; half-away is sign-symmetric in magnitude but pushes exact halves outward [numeric-claim: not source-grounded here]. They are reproducible and hardware-cheap, but less standard than ties-to-even for canonical numeric semantics, and no local source suggests Spatial intended either one. They should be rejected unless the goal is an intentionally biased compatibility mode.

Truncation is cheapest and most reproducible, but it abandons the name "unbiased." AMD distinguishes `AP_TRN` from `AP_TRN_ZERO`, and current Spatial already has truncating/wrapping fixed operations separate from `Unb*`. If implemented as `bits >> 4`, truncation is floor-like for signed `BigInt`, not true toward-zero truncation. Its error is systematic for persistent fractional residues [numeric-claim: not source-grounded here]. Compatibility churn is therefore semantic, not just statistical.

## Deterministic Stochastic Rules

Stable-hash stochastic rounding is the strongest deterministic replacement if "unbiased" should remain statistical. Replace `Random.nextFloat()` with a threshold derived from `(seed, algorithm, static_op_id, dynamic_instance_id, lane_or_element_id)`, then keep the current threshold rule. With a uniform, value-independent hash, the expected rounded value matches distance-proportional stochastic rounding [numeric-claim: conditional on hash quality; stochastic rounding expectation is source-grounded by Connolly/Higham/Mary 2021, https://doi.org/10.1137/20M1334796]. It gives bit reproducibility, order independence, and CI replay. Hardware can implement it as combinational hashing or counter-based PRNG, but needs stable event IDs and a versioned algorithm manifest.

Per-op seeded PRNG is the hardware-friendlier sibling: assign each unbiased site its own seed/LFSR stream. This mirrors Fringe's PRNG shape more directly and avoids a process-global JVM stream. Its hazard is advance policy: if the PRNG advances by clock, stalls or scheduling can change results; if it advances by valid rounding event, hardware and simulator need explicit enable semantics. D-09 flags this as a reason to prefer stable per-event derivation over sequential streams ([[05-hls-hardware-implications]], [[06-seedable-rng-policy]]).

## Recommendation Implication

D-17 should not canonize truncation, half-up, or half-away as "unbiased." If the project wants deterministic arithmetic, choose round-to-nearest-even and state that `Unbiased` has been redefined away from current Spatial/Fringe stochastic behavior. That is a large but clean migration.

If the project wants continuity with existing semantics, canonize deterministic stochastic rounding: stable-hash threshold rounding as the reference rule, with per-op seeded PRNG allowed only when its event-advance contract is equivalent. This preserves the statistical intent, gives reproducible bits, maps to hardware with explicit seed/state, and minimizes compatibility churn relative to arithmetic replacement.
