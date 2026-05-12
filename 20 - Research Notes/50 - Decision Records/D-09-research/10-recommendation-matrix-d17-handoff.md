---
type: "research"
decision: "D-09"
angle: 10
---

# Recommendation Matrix and D-17 Handoff

## Decision Boundary

D-09 should decide the Rust simulator behavior now, not the final language-wide meaning of "unbiased." The queue frames D-09 as a Rust simulator choice among JVM RNG nondeterminism, seedable deterministic RNG, or deterministic rounding, while D-17 repeats the same alternatives as the canonical unbiased-rounding policy (`20 - Research Notes/40 - Decision Queue.md:43-45`, `20 - Research Notes/40 - Decision Queue.md:75-77`). Q-118 explains the immediate problem: `FixedPoint.unbiased` calls `scala.util.Random.nextFloat()` on every use, so consecutive simulator runs can differ on `*&`, `/&`, unbiased casts, and saturating unbiased variants (`20 - Research Notes/20 - Open Questions.md:1595-1602`). Q-144 should own the broader semantic question: whether Spatial's canonical policy remains nondeterministic, becomes seedable, or is replaced by deterministic rounding (`20 - Research Notes/20 - Open Questions.md:2057-2062`).

## Evidence Anchors

The current spec says Scalagen plus `emul` is the bit-level reference for Rust, and lists `unbiased` as one of the three fixed-point constructor families (`10 - Spec/50 - Code Generation/20 - Scalagen/20 - Numeric Reference Semantics.md:27-29`, `10 - Spec/50 - Code Generation/20 - Scalagen/20 - Numeric Reference Semantics.md:41-47`). Source confirms the stochastic rule: arithmetic operators manufacture four guard bits before calling `FixedPoint.unbiased`, and the helper shifts by four, computes a 1/16 remainder, samples `Random.nextFloat`, then rounds away from zero before clamping or saturating (`/Users/david/Documents/David_code/spatial/emul/src/emul/FixedPoint.scala:52-63`, `/Users/david/Documents/David_code/spatial/emul/src/emul/FixedPoint.scala:232-240`). Scalagen directly emits the unbiased operator/cast calls (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/scalagen/ScalaGenFixPt.scala:96-114`). Tests check statistical behavior, not JVM sequence parity: `SpecialMath` fills 256 samples with `*&`, compares means against exact products within `2^-4`, and asserts saturation endpoints exactly (`/Users/david/Documents/David_code/spatial/test/spatial/tests/feature/math/SpecialMath.scala:51-61`, `/Users/david/Documents/David_code/spatial/test/spatial/tests/feature/math/SpecialMath.scala:74-94`).

## Option Matrix

| Option | Reproducibility, CI stability, user control | Statistical unbiasedness and Scalagen parity | HLS/hardware implementability | D-17 compatibility |
|---|---|---|---|---|
| JVM-like nondeterminism | Weak: no stable replay, poor CI, little user control. | Good distribution and closest generated-Scala behavior, but overfits a process-global JVM artifact. | Poor: hardware cannot depend on host JVM RNG. | Compatible only if D-17 canonizes nondeterminism, which would make later debugging harder. |
| Seedable deterministic stochastic rounding | Strong: fixed seed plus algorithm label gives replayable CI and user-selected fuzz modes. | Preserves the stochastic law from `FixedPoint.unbiased` without requiring JVM sequence parity. | Best fit to existing hardware intent: Chiselgen passes `Unbiased`, Fringe defines it as LFSR stochastic rounding, and `Converter` adds PRNG bits before shaving fractional bits (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/chiselgen/ChiselGenMath.scala:34-40`, `/Users/david/Documents/David_code/spatial/fringe/src/fringe/templates/math/RoundingMode.scala:3-8`, `/Users/david/Documents/David_code/spatial/fringe/src/fringe/templates/math/Converter.scala:36-44`). | Most flexible: D-17 can ratify it as canonical or replace it later with a deliberate migration. |
| Deterministic round-to-nearest-even | Excellent replay and CI. | Not current Scalagen behavior and not stochastic, though HLS libraries expose ties-to-even style modes (`20 - Research Notes/50 - Decision Records/D-01-research/07-hls-native-math.md:21-23`). | Easy for HLS fixed-point assignment, but it changes the semantic contract. | Good only if D-17 chooses to redefine unbiased as deterministic RNE. |
| Deterministic truncation or nearest-away | Excellent replay, CI, and implementation simplicity. | Fails statistical unbiasedness; truncation is already a different Spatial mode, and nearest-away would keep only the current signed direction without its probability law. | Cheapest to synthesize, but semantically misleading for `Unb*` nodes. | Poor unless D-17 deprecates or renames unbiased operations. |

## Handoff to D-17

D-09 should not rename, deprecate, or globally redefine `Unbiased`. It should record that Rust simulator parity means "statistical Spatial parity with controlled replay," not bit-for-bit `scala.util.Random` parity. D-17 should decide whether the canonical spec later requires stochastic rounding in every backend, standardizes seed derivation across Scala/Rust/HLS, or replaces stochastic rounding with deterministic RNE or another deterministic rule. If D-17 changes the canonical policy, it should update the numeric spec, JVM `emul`, Scalagen tests, and hardware lowering together.

## Named Recommendation

**Recommendation D-09: Seeded Stable Stochastic Rounding.** Choose seedable deterministic stochastic rounding for the Rust simulator, with a fixed default seed for CI, explicit seed/policy/algorithm metadata for user control, and no promise to match the JVM global RNG sequence. Defer the canonical meaning of unbiased rounding across Spatial to D-17.
