---
type: "research"
decision: "D-17"
angle: 1
source_decision: "D-09"
---

# D-09 Handoff and Scope Separation

## D-09's Rust-Simulator Layer

[[D-09]] already scoped Q-118 as a Rust simulator determinism problem, not as the final language meaning of `Unbiased`. Its recommendation is **Seeded Stable Stochastic Rounding**: preserve the existing stochastic probability law for Rust simulation, make it replayable with explicit seed/policy/algorithm metadata, and reject bit-for-bit compatibility with Scala's process-global RNG stream. The key compatibility label is statistical Spatial parity, not JVM sequence parity. That keeps Rust useful for CI and debugging without pretending that `scala.util.Random.nextFloat()` is itself a portable semantic object.

The source behavior being preserved at this layer is the current `FixedPoint.unbiased` helper: shift away four guard bits, compute a sixteenth-granularity remainder, draw `scala.util.Random.nextFloat()`, then step farther from zero when `rand + remainder >= 1`, before choosing clamped or saturating construction (`/Users/david/Documents/David_code/spatial/emul/src/emul/FixedPoint.scala:232-241`). [[20 - Numeric Reference Semantics]] records this as one of the three fixed-point constructor families and explicitly marks it nondeterministic under Scalagen/emul.

## Why D-09 Stops There

The handoff matrix [[10-recommendation-matrix-d17-handoff]] is explicit that D-09 should not rename, deprecate, or globally redefine `Unbiased`. D-09 answers how Rust should simulate today's behavior under a replayable policy. It does not decide whether all Spatial backends must share one seed derivation contract, whether stochastic rounding remains the canonical language rule, or whether the word "unbiased" should be reassigned to deterministic arithmetic rounding.

This separation matters because [[D-09]] is anchored in simulator operations: stable event identities, default CI seeds, algorithm labels, legacy-stream debugging modes, and recorded run metadata. Those are implementation-contract details for Rust simulation. They are necessary for a simulator, but they are too narrow to settle Scala emul, Scalagen tests, HLS lowering, and hardware-generated randomness as one canonical semantic surface.

## D-17's Canonical Question

[[D-17]] inherits Q-144: choose the canonical unbiased rounding policy. The decision queue states the canonical criteria as: unbiased rounding matches nondeterministic Spatial behavior, becomes seedable, or is replaced by deterministic rounding. That is deliberately broader than D-09's Q-118 Rust simulator framing, even though both originate from the same source call to `FixedPoint.unbiased`.

D-17 therefore must decide what `Unbiased` means across the language and reference stack. The candidate outcomes include canonizing stochastic rounding as the semantic intent, standardizing seedable stochastic derivation across relevant backends, allowing a simulator seed policy while hardware remains stochastic by construction, or replacing the stochastic rule with a deterministic rule such as round-to-nearest-even. Each option has cross-backend consequences for [[20 - Numeric Reference Semantics]], Scala emul, Rust, Scalagen regression expectations, and HLS or Fringe lowering.

## What Cannot Be Duplicated

D-17 should not re-litigate D-09's Rust-only default as if it were still open. Unless D-09 is explicitly reopened, Rust simulator v1 has a scoped answer: seed-controlled stable stochastic rounding, no JVM global RNG sequence guarantee, preserve the four-guard-bit probability law and legacy signed step behavior for compatibility. D-17 may later replace or ratify that policy canonically, but it should not duplicate the D-09 matrix by selecting a second Rust-specific default in isolation.

D-17 also should not duplicate D-09's simulator metadata design. Fields such as `sim_rng_policy`, `sim_rng_seed`, `sim_rng_algorithm`, `rng_compatibility`, and stable event IDs are D-09 implementation artifacts unless D-17 intentionally promotes them into canonical semantics. If promoted, they need language-wide wording, not another Rust simulator note.

Finally, D-17 should not treat "seedable" as already fully specified just because D-09 chose a seedable Rust policy. D-09 seedability answers replay. D-17 seedability would answer semantics: which events are identified, whether operation order may affect results, what hardware must expose, and whether Scala's current ambient RNG remains acceptable. This angle is only the boundary map; it is not the final D-17 synthesis.
