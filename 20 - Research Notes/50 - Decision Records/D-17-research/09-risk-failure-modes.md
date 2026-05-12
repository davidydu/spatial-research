---
type: "research"
decision: "D-17"
angle: 9
---

# Risk and Failure Modes

## Baseline Risk Surface

[[D-17]] asks whether canonical `Unbiased` rounding should preserve nondeterministic Spatial behavior, become seedable, or be replaced by deterministic rounding (`20 - Research Notes/40 - Decision Queue.md:75-77`). The source surface is narrow but sharp: `*&`, `/&`, `*&!`, and `/&!` route through `FixedPoint.unbiased`, while Scalagen also emits unbiased fixed casts directly to that helper (`emul/src/emul/FixedPoint.scala:52-63`, `src/spatial/codegen/scalagen/ScalaGenFixPt.scala:96-114`). The helper shifts away four guard bits, uses a 1/16 remainder, draws `scala.util.Random.nextFloat()`, then steps positive `biased` values upward and negative `biased` values downward when the threshold fires (`emul/src/emul/FixedPoint.scala:232-240`). [[20 - Numeric Reference Semantics]] calls Scalagen plus `emul` ground truth, but also explicitly marks this path nondeterministic (`10 - Spec/50 - Code Generation/20 - Scalagen/20 - Numeric Reference Semantics.md:27-29`, `10 - Spec/50 - Code Generation/20 - Scalagen/20 - Numeric Reference Semantics.md:45-47`).

## Four Policy Risks

**Ambient nondeterminism** has the lowest migration cost for generated Scala and the highest operational risk. It preserves today's `Random.nextFloat()` call, but bit-exact failures may not replay, and execution-order changes can silently change low bits if the stream is treated as semantic (unverified). Existing tests are already exposed: `SpecialMath` samples 256 `*&` results and checks means within one `_4` LSB, then reduces all checks to `PASS: true/false` (`test/spatial/tests/feature/math/SpecialMath.scala:51-61`, `test/spatial/tests/feature/math/SpecialMath.scala:86-107`; `argon/src/argon/DSLTest.scala:120-123`). That test style tolerates stochastic noise, but not necessarily rare flakes or diagnosis after the run.

**Seeded stable stochastic** is the safest continuity choice from [[D-09]] and [[07-cross-backend-provenance-schema]], but it adds specification obligations. It preserves the probability law while replacing ambient RNG with event-derived thresholds. The failure mode shifts from flakiness to silent identity drift: if `static_op_id`, dynamic iteration identity, or lane identity is omitted or unstable, the same program can produce different "reproducible" results after harmless scheduling/codegen changes. It also has HLS area/performance cost because stable hashing or PRNG state, seed plumbing, and valid-event advance logic must be implemented (unverified); Fringe's current PRNG is at least a register plus XOR/shift feedback (`fringe/src/fringe/templates/math/PRNG.scala:13-16`).

**Deterministic replacement** gives the best replay and probably the smallest HLS logic if implemented as truncation or round-to-nearest-even through native fixed-point modes (unverified). Its main risk is semantic camouflage. The current language, Scalagen, and Fringe evidence all say stochastic: `RoundingMode.Unbiased` is documented as LFSR stochastic rounding, and `fix2fixBox` adds PRNG low bits before shaving fractional bits (`fringe/src/fringe/templates/math/RoundingMode.scala:3-8`, `fringe/src/fringe/templates/math/Converter.scala:36-44`). A deterministic replacement therefore must be named as a D-17 redefinition, not a backend optimization; otherwise tests and users can see silent numeric divergence while the result is still mislabeled "unbiased."

**HLS fallback or rejection** is a policy safety valve. The HLS spec already says the rewrite needs an explicit numeric policy, including whether Chisel fused behavior or Scala reference behavior wins (`10 - Spec/80 - Runtime and Fringe/50 - BigIP and Arithmetic.md:55-57`). Rejecting unsupported stochastic rounding prevents silent mismatch, but blocks designs that currently compile. Falling back to deterministic HLS rounding preserves implementation progress and area, but only if the artifact declares `fallback = deterministic_rne` or similar; otherwise the simulator and kernel can disagree without a visible provenance break.

## Signed And Backend Mismatch

Signed-negative behavior is a corner-case multiplier for every option. Scala's stochastic carry moves `biased < 0` to `biased - 1`, i.e. farther from zero (`emul/src/emul/FixedPoint.scala:238`). Stable stochastic can preserve that as `legacy_away_from_zero`; deterministic replacement must decide whether to keep, remove, or rename it. Hardware is not identical: Chisel passes `Unbiased` into `Math.mul`, `Math.div`, and `Math.fix2fix`, but Fringe's visible implementation is random-bit addition during fractional shrink, with PRNG enabled every cycle rather than by `flow` (`src/spatial/codegen/chiselgen/ChiselGenMath.scala:33-40`, `src/spatial/codegen/chiselgen/ChiselGenMath.scala:75-78`, `fringe/src/fringe/templates/math/Converter.scala:39-43`). That creates backend mismatch risk even under "stochastic" wording unless seed and advance policy are canonical.

## Risk Ranking

For D-17, the worst failure mode is not a visible rejection; it is silent numeric divergence under a familiar name. Ambient nondeterminism ranks worst for reproducibility and flaky tests. Deterministic replacement ranks best for replay and area, but worst for semantic continuity unless D-17 explicitly redefines `Unbiased`. HLS rejection is disruptive but honest. Seeded stable stochastic has the most moving parts, yet it is the only option that addresses replay, test stability, backend provenance, and the current stochastic contract together. It should be preferred if D-17 values continuity with [[20 - Numeric Reference Semantics]]; deterministic replacement should be treated as a deliberate language migration.
