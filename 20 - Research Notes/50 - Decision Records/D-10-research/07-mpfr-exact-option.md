---
type: research
decision: D-10
angle: 7
title: MPFR/per-format exact math option
date: 2026-04-27
---

# MPFR/per-format exact math option

## 1. What "Exact" Would Mean

D-10 / Q-130 explicitly offers MPFR/per-format exact math as the alternative to Scalagen f64 and synthesized-unit parity (`20 - Research Notes/40 - Decision Queue.md:47-49`; `20 - Research Notes/20 - Open Questions.md:1818-1836`). For Spatial, that would not mean "store values differently." `FixFormat(sign, ibits, fbits)` remains a scaled raw integer lattice, and `FltFormat(sbits, ebits)` remains a custom sign/exponent/significand format with subnormal and overflow rules (`emul/src/emul/FixFormat.scala:3-29`; `emul/src/emul/FltFormat.scala:3-29`; `10 - Spec/20 - Semantics/50 - Data Types.md:42-54`). The change is the evaluation oracle: compute the real-valued operation at enough precision, then round once into the destination `FixFormat` or `FltFormat`.

For fixed point, the hard choice is the final rounding rule. Current fixed construction from decimal scales by `2^fbits`, converts to `BigInt`, then wraps through `FixedPoint.clamped`; ordinary arithmetic uses truncating shifts/division and wraparound, while saturation and unbiased rounding are separate families (`emul/src/emul/FixedPoint.scala:14-23`, `emul/src/emul/FixedPoint.scala:156-165`, `emul/src/emul/FixedPoint.scala:203-241`). A mathematically exact fixed transcendental therefore needs a stated rule: preserve current truncation-plus-wrap after exact evaluation, or introduce round-to-nearest/other directed modes as a semantic change.

## 2. Operations Needing Correct Rounding

The exact option must cover every `Number.*` helper that currently crosses the `toDouble` boundary: fixed `sqrt`, `exp`, `ln`, fixed-only `log2`, `pow`, circular trig, hyperbolics, inverse trig, and their float peers, plus composed `recipSqrt` and `sigmoid` if the mode claims one-rounding semantics (`emul/src/emul/Number.scala:96-155`). Scalagen lowers fixed and float nodes to those helpers, except fixed reciprocal-square-root is emitted as `one / Number.sqrt(x)`, float reciprocal-square-root calls `Number.recipSqrt`, and sigmoid is emitted as an expression over `Number.exp` (`src/spatial/codegen/scalagen/ScalaGenFixPt.scala:137-152`; `src/spatial/codegen/scalagen/ScalaGenFltPt.scala:107-122`).

Correct rounding for custom floats means more than a high-precision function call. The final pack must produce the chosen `FltFormat` bit pattern, including NaN, signed infinities, signed zero, normal/subnormal transition, overflow, underflow, and tie behavior. Today that pack is `FloatPoint.clamp`, including the unresolved `x > 1.9` subnormal guard (`emul/src/emul/FloatPoint.scala:318-398`; `20 - Research Notes/20 - Open Questions.md:2065-2075`).

## 3. Difference From Number.scala

Current `Number.scala` is deliberately f64-backed: both fixed and float transcendental blocks say they rely on the Double implementation, call JVM `Math.*(x.toDouble)`, then rebuild the original format with `.withValid(x.valid)` (`emul/src/emul/Number.scala:96-114`; `emul/src/emul/Number.scala:139-155`). The Numeric Reference Semantics spec treats this as the current bit-level reference, and Data Types repeats that Scalagen wins when it differs from JVM or hardware intuition (`10 - Spec/50 - Code Generation/20 - Scalagen/20 - Numeric Reference Semantics.md:80-90`; `10 - Spec/20 - Semantics/50 - Data Types.md:36-39`).

MPFR/exact mode would intentionally break that reference. It would remove f64 double-rounding for f32-like formats and precision collapse for wider formats such as quad, but it would also stop matching Java `Math` special-case behavior, current `pow` validity asymmetry, and any tests whose golds were produced by Scalagen's f64 round trip (`emul/src/emul/Number.scala:103`, `emul/src/emul/Number.scala:145`).

## 4. Cost, Dependencies, And Build Risk

Implementation cost is high. The Rust runtime would need exact real evaluation, explicit rounding modes, domain/special-value tables, format-aware pack/unpack, and conformance tests for every supported `FixFormat`/`FltFormat`. Performance would be much slower than host f64, especially inside simulator loops, so this is more plausible as an opt-in verification oracle than the default compatibility runtime.

External dependency risk is also real. MPFR is a native C library commonly used with GMP, and Rust access usually means FFI crates, native library discovery, C compiler/toolchain assumptions, and cross-platform packaging work `(unverified)`. License review may matter, especially for static linking or redistribution of MPFR/GMP-linked binaries `(unverified)`. Version drift could also change last-bit results unless the runtime pins the library and rounding mode behavior `(unverified)`.

## 5. D-10 Implications

MPFR/exact is the cleanest mathematical oracle, but not the lowest-risk D-10 compatibility choice. If selected, D-10 should name it as a new reference mode and update `[[20 - Numeric Reference Semantics]]`, `[[50 - Data Types]]`, gold tests, and runtime manifests to say which operations are correctly rounded and which still match Scalagen composition.

It also couples tightly to D-18 and D-19. If D-18 preserves `FloatPoint.clamp` bit-for-bit, exact evaluation still ends in Scalagen's custom clamp heuristic, so the result is not a pure IEEE-style custom-float model. If D-18 replaces clamp with a cleaner packer, MPFR/exact becomes much more coherent, but diverges further from Scalagen. For D-19, exact transcendentals pair naturally with fused/correct-rounded FMA, while Scalagen-unfused FMA would leave a mixed policy: exact elementary functions beside multiply-then-add rounding (`20 - Research Notes/20 - Open Questions.md:2078-2088`; `10 - Spec/20 - Semantics/60 - Reduction and Accumulation.md:50-64`).
