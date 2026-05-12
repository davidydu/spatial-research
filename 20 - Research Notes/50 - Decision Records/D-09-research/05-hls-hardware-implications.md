---
type: "research"
decision: "D-09"
angle: 5
---

# HLS Hardware Implications For D-09 Rounding

## Decision Surface

D-09 asks whether Rust simulator unbiased rounding should preserve JVM RNG nondeterminism, use a seedable deterministic RNG, or become deterministic rounding (`20 - Research Notes/40 - Decision Queue.md:43-45`). The linked open question is specifically about `FixedPoint.unbiased` calling `scala.util.Random.nextFloat()` and therefore making bit-exact results run-dependent (`20 - Research Notes/10 - Deep Dives/open-questions-semantics.md:82-87`). That sounds simulator-local, but the HLS/hardware mapping makes it architectural: the chosen simulator policy either follows Scala, follows current Fringe stochastic hardware, or defines a new fixed-point contract that HLS can implement with lower state cost (unverified).

## Current Spatial And Fringe Semantics

Scalagen has three fixed-point result families: wrapping `clamped`, `saturating`, and `unbiased`; the spec calls `unbiased` RNG-based round-to-nearest and notes its nondeterminism (`10 - Spec/50 - Code Generation/20 - Scalagen/20 - Numeric Reference Semantics.md:41-47`). Source confirms that `FixedPoint.unbiased` shifts away four fractional guard bits, samples `scala.util.Random.nextFloat()`, rounds away from zero when `rand + remainder >= 1`, then either wraps or saturates (`emul/src/emul/FixedPoint.scala:232-240`). Scalagen routes `UnbMul`, `UnbDiv`, and unbiased fixed casts to those operators/constructors (`src/spatial/codegen/scalagen/ScalaGenFixPt.scala:96-114`).

The Chisel path is related but not identical. Chiselgen lowers unbiased multiply/divide and fixed casts by passing `Unbiased` plus `Wrapping` or `Saturating` into `Math` (`src/spatial/codegen/chiselgen/ChiselGenMath.scala:33-40`, `src/spatial/codegen/chiselgen/ChiselGenMath.scala:75-78`). The Fringe spec says fixed conversion and rounding are split between `Math`, `BigIP`, and `fix2fixBox`, with only `Truncate`/`Unbiased` and `Wrapping`/`Saturating` as modes (`10 - Spec/80 - Runtime and Fringe/50 - BigIP and Arithmetic.md:49-57`; `fringe/src/fringe/templates/math/RoundingMode.scala:3-8`; `fringe/src/fringe/templates/math/OverflowMode.scala:3-8`). For non-literal fixed casts, `BigIPSim.fix2fix` instantiates `fix2fixBox`; for literals it enters a Scala branch that uses `scala.math.random` salt and is preceded by a “Likely that there are mistakes here” comment (`fringe/src/fringe/targets/BigIPSim.scala:237-253`).

## Hardware Shape

For non-literal hardware, `fix2fixBox` performs fractional bit shaving, and the `Unbiased` case instantiates `PRNG(scala.math.abs(scala.util.Random.nextInt))`, keeps it enabled, adds low PRNG bits to the input, then takes the shifted result (`fringe/src/fringe/templates/math/Converter.scala:32-44`). The PRNG itself is a register initialized from a seed and updated by xor/shift feedback when enabled (`fringe/src/fringe/templates/math/PRNG.scala:6-16`). Overflow is a separate decision: shrinking decimal bits either wraps by selecting low bits or saturates using sign/expected-direction checks (`fringe/src/fringe/templates/math/Converter.scala:58-78`).

This means current hardware-style unbiased rounding is already deterministic after elaboration but not reproducible across elaborations unless the generated seed is controlled. It is also cycle-sensitive because the converter ties `prng.io.en := true.B`, not to a per-operation valid handshake (`fringe/src/fringe/templates/math/Converter.scala:40-42`). Literal handling is worse for parity: constant folding can move a stochastic decision to elaboration/simulation time via `scala.math.random` (`fringe/src/fringe/targets/BigIPSim.scala:247-270`).

## D-09 Options In HLS

Matching JVM nondeterminism is the poorest HLS fit. Synthesized logic cannot rely on a host JVM RNG (unverified); stochastic rounding would require explicit RNG/dither hardware, state reset, seed plumbing, and enable semantics (unverified). Without that, the Rust simulator would match Scalagen but not the generated HLS kernel.

A seedable deterministic RNG maps best to current Fringe intent. HLS can model each unbiased operation as add-random-low-bits-before-shift, with a manifest assigning stable RNG seeds per operation or stream (unverified). The hard part is replay: if RNG advances per clock, stalls and scheduling change results; if it advances per valid operation, it diverges from current `fix2fixBox` unless Fringe parity is deliberately relaxed.

Deterministic rounding is the cheapest HLS contract (unverified). Vendor HLS fixed-point libraries often expose deterministic quantization modes such as truncation, saturation, and round-to-nearest-even (unverified); local HardFloat names `round_near_even = 000`, and BigIPSim passes `0.U(3.W)` for float conversions (`fringe/src/fringe/templates/hardfloat/common.scala:42-52`; `fringe/src/fringe/targets/BigIPSim.scala:275-291`). But Spatial fixed-point `Unbiased` is stochastic, not nearest-even, so this option is a semantic replacement, not an implementation detail.

## Simulator-Vs-HLS Parity

The parity implication is blunt: “unbiased” is not enough. If HLS parity is the goal, D-09 should choose either seedable stochastic rounding with explicit seed/advance policy, or deterministic rounding with a documented break from Spatial stochastic behavior. Keeping JVM nondeterminism only as the Rust simulator default would create a permanent simulator-vs-HLS mismatch and make bit-exact regression failures non-actionable.
