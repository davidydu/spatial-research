---
type: "research"
decision: "D-09"
angle: 7
---

# Deterministic Rounding Alternatives

## Baseline Rule And Scope

D-09/Q-118 is the Rust simulator choice: match JVM RNG nondeterminism, use a seedable deterministic RNG, or replace unbiased rounding with deterministic rounding (`20 - Research Notes/40 - Decision Queue.md:43-45`). D-17/Q-144 overlaps at the canonical policy layer (`20 - Research Notes/40 - Decision Queue.md:75-77`; `20 - Research Notes/20 - Open Questions.md:2052-2062`), but this angle focuses on Rust simulator consequences.

The current helper is not simply "nearest even." `FixedPoint.unbiased` receives `bits` with four extra fractional bits, computes `biased = bits >> 4`, computes `remainder = (bits & 0xF) / 16.0f`, draws `scala.util.Random.nextFloat()`, and if `rand + remainder >= 1` steps to `biased + 1` for nonnegative `biased` or `biased - 1` for negative `biased` (`emul/src/emul/FixedPoint.scala:224-240`). Unbiased multiply/divide operators call this helper (`emul/src/emul/FixedPoint.scala:52-63`), and Scalagen emits those operators and casts (`src/spatial/codegen/scalagen/ScalaGenFixPt.scala:96-114`). The spec records this as a nondeterministic fixed-point mode (`10 - Spec/50 - Code Generation/20 - Scalagen/20 - Numeric Reference Semantics.md:41-47`; `10 - Spec/20 - Semantics/50 - Data Types.md:48`).

## Nearest-Even

Round-to-nearest-even would convert the four guard bits into a deterministic nearest representable value: below half stays at the lower candidate, above half goes to the upper candidate, and exactly half chooses the candidate with an even least-significant target bit. Against the current stochastic rule, all non-tie remainders become fixed decisions rather than probabilities. For nonnegative values, current stochastic rounding has expectation `biased + remainder`; nearest-even has bounded per-operation error but deterministic low-bit patterns. Its aggregate error is usually expected to cancel when fractional residues and even/odd targets are well distributed (unverified).

For negative values, nearest-even should be defined over mathematical candidates, not over the current `biased - 1` branch. With `biased = bits >> 4` and `remainder > 0`, the exact scaled value lies between `biased` and `biased + 1`; a mathematical nearest rule therefore sometimes moves toward zero. Current code instead moves from negative `biased` to `biased - 1` on threshold, farther from zero (`emul/src/emul/FixedPoint.scala:232-238`). So nearest-even is not just deterministic; it would also repair or intentionally diverge from the current negative-side behavior.

## Half Rules And Truncation

Round-half-up, half-away-from-zero, and half-toward-zero differ only at `remainder == 8` if all non-ties use nearest. Half-up creates a positive tie drift when ties are common (unverified). Half-away-from-zero is sign-symmetric in magnitude but increases absolute-value error at ties (unverified). Half-toward-zero does the opposite, pulling exact halves inward (unverified). These are easier to explain than nearest-even, but they embed a visible tie policy in kernels that repeatedly land on half-LSB products or casts.

Always-truncate is cheaper still: return `biased` and ignore the guard nibble. If implemented exactly as `bits >> 4`, this is floor-like for signed `BigInt`, not true truncation toward zero for negative fractional values. It therefore has negative error for positive values and also pushes negative fractional values more negative than their exact scaled value. A true "toward zero" truncation would need an explicit negative correction when `remainder != 0`. Either truncation variant abandons the statistical intent currently tested by `SpecialMath`, where unbiased products are checked by comparing the mean of 256 samples to the real product within one LSB (`test/spatial/tests/feature/math/SpecialMath.scala:51-88`).

## Stable-Hash Rounding

Deterministic pseudo-random rounding can avoid a mutable RNG while preserving the current threshold form. Instead of `Random.nextFloat()`, derive a stable threshold from operation identity, dynamic instance, lane/index, and optionally a seed; then round when `threshold + remainder >= 1`. This is deterministic for replay, order-insensitive if IDs are stable, and statistically close to the current nonnegative rule when the hash is uniform and uncorrelated with data (unverified). It also makes the sign question explicit: Rust can preserve the current `biased - 1` negative branch for compatibility, or use the same hashed threshold with mathematical candidates to make the policy genuinely unbiased for signed values.

This option is closest to the existing tests because it still makes nonzero remainders probabilistic over a population. It is less like ordinary "deterministic rounding," but closer to the source contract than nearest-even or truncation. It also aligns with the prior seedable-RNG recommendation that stable per-operation derivation is preferable to a sequential shared stream (`20 - Research Notes/50 - Decision Records/D-09-research/06-seedable-rng-policy.md:21-31`).

## D-09 Recommendation Implication

For D-09, do not choose plain truncation or half-up as the Rust simulator default. They are deterministic, but they discard the mean-preserving intent of the current nonnegative stochastic rule and would force broad golden-output churn. If D-09 must become fully deterministic without pseudo-random thresholds, prefer mathematical round-to-nearest-even and document that it is a canonical semantic change to be ratified under D-17/Q-144. If D-09 is allowed a deterministic pseudo-random mechanism, prefer stable-hash threshold rounding with an explicit policy bit for `signed_negative_behavior = legacy_away | mathematical_nearest`. That gives Rust reproducibility while preserving the current stochastic surface closely enough for simulator migration.
