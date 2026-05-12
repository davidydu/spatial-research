---
type: "research"
decision: "D-10"
angle: 1
---

# Current Number.scala Transcendental Surface

## Decision Frame

D-10 / Q-130 asks whether the Rust numeric runtime should match Scalagen's current f64 transcendental behavior, switch to per-format exact math such as MPFR, or match synthesized hardware units (`20 - Research Notes/40 - Decision Queue.md:47-49`, `20 - Research Notes/20 - Open Questions.md:1818-1836`). The current implementation is intentionally simple: both fixed and floating paths have TODO comments saying the transcendental block relies on the Double implementation today (`/Users/david/Documents/David_code/spatial/emul/src/emul/Number.scala:96-103`, `/Users/david/Documents/David_code/spatial/emul/src/emul/Number.scala:139-145`).

## Number.scala Surface

For `FixedPoint`, `Number` defines context operations `ceil`, `floor`, `abs`, `min`, and `max` before the transcendental block. Fixed `ceil` and `floor` mask away fractional bits and add one or minus one when sign and remainder require it; `abs`, `min`, and `max` are wrappers over comparison/negation (`/Users/david/Documents/David_code/spatial/emul/src/emul/Number.scala:80-94`). The fixed transcendental surface covers `recip`, `sqrt`, `recipSqrt`, `exp`, `ln`, `log2`, `pow`, `sin`, `cos`, `tan`, `sinh`, `cosh`, `tanh`, `asin`, `acos`, `atan`, and `sigmoid` (`/Users/david/Documents/David_code/spatial/emul/src/emul/Number.scala:96-114`).

For `FloatPoint`, the context operations handle IEEE-like specials first: `ceil` and `floor` return `NaN`, `Inf`, and signed zero unchanged, otherwise reclamp a `Value` after integer adjustment (`/Users/david/Documents/David_code/spatial/emul/src/emul/Number.scala:116-133`). Float `abs`, `min`, and `max` mirror the fixed wrappers (`/Users/david/Documents/David_code/spatial/emul/src/emul/Number.scala:135-137`). The floating transcendental surface covers the same main set except `log2`: `recip`, `sqrt`, `recipSqrt`, `exp`, `ln`, `pow`, trig, hyperbolic trig, inverse trig, and `sigmoid` (`/Users/david/Documents/David_code/spatial/emul/src/emul/Number.scala:139-155`).

## Reclamp Path

The direct transcendental pattern is `x.toDouble -> java.lang.Math.* -> FixedPoint/FloatPoint(..., x.fmt) -> withValid(x.valid)`. Fixed `toDouble` first converts the stored scaled integer to `BigDecimal`, then to `Double` (`/Users/david/Documents/David_code/spatial/emul/src/emul/FixedPoint.scala:86-88`). The fixed `Double` constructor rescales by `2^fbits`, converts to integer bits, and wraps with `FixedPoint.clamped`; wrapping either sign-extends or masks to the format width (`/Users/david/Documents/David_code/spatial/emul/src/emul/FixedPoint.scala:156-158`, `/Users/david/Documents/David_code/spatial/emul/src/emul/FixedPoint.scala:162-166`, `/Users/david/Documents/David_code/spatial/emul/src/emul/FixedPoint.scala:197-208`). Thus fixed transcendentals are computed in f64, then rounded/truncated by `BigDecimal.toBigInt` and wrapped into the destination fixed format, not evaluated at fixed precision.

Float `toDouble` maps `NaN`, infinities, signed zero, and finite `Value` to the corresponding JVM double (`/Users/david/Documents/David_code/spatial/emul/src/emul/FloatPoint.scala:190-195`). `FloatPoint(Double, fmt)` converts the double into `FloatValue`, preserving JVM `NaN`, infinity, and signed zero cases, then `FloatPoint.clamped` either keeps specials or rounds finite values through `clamp` and `convertBackToValue` for the target `FltFormat` (`/Users/david/Documents/David_code/spatial/emul/src/emul/FloatPoint.scala:135-140`, `/Users/david/Documents/David_code/spatial/emul/src/emul/FloatPoint.scala:275-277`, `/Users/david/Documents/David_code/spatial/emul/src/emul/FloatPoint.scala:417-433`).

## Validity and Coverage Differences

Most direct unary transcendentals restore only the input's `valid` bit after constructing a fresh valid result (`/Users/david/Documents/David_code/spatial/emul/src/emul/Number.scala:98-112`, `/Users/david/Documents/David_code/spatial/emul/src/emul/Number.scala:141-154`). `pow` is asymmetric: it computes with both operands' `toDouble` values but calls `.withValid(x.valid)`, so the exponent's `valid` flag is not propagated (`/Users/david/Documents/David_code/spatial/emul/src/emul/Number.scala:103`, `/Users/david/Documents/David_code/spatial/emul/src/emul/Number.scala:145`). `recipSqrt` and `sigmoid` are composed from `sqrt`/`exp` plus arithmetic, so their final validity follows the arithmetic operators' `valid && valid` behavior after the inner helper has copied `x.valid` (`/Users/david/Documents/David_code/spatial/emul/src/emul/FixedPoint.scala:14-17`, `/Users/david/Documents/David_code/spatial/emul/src/emul/FloatPoint.scala:154-157`).

The sharpest coverage mismatch is `log2`: `Number.log2` exists only for `FixedPoint` and is implemented as `Math.log(x.toDouble) / Math.log(2)` reclamped to the fixed format (`/Users/david/Documents/David_code/spatial/emul/src/emul/Number.scala:102`). There is no `FloatPoint` overload in the float block (`/Users/david/Documents/David_code/spatial/emul/src/emul/Number.scala:141-155`), and Scalagen's float emission list likewise has no `FltLog2` case (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/scalagen/ScalaGenFltPt.scala:104-122`). Scalagen also expands fixed reciprocal square root as `one / Number.sqrt(x)` and expands sigmoid via `Number.exp`, while float emits `Number.recipSqrt` but still expands sigmoid (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/scalagen/ScalaGenFixPt.scala:137-152`, `/Users/david/Documents/David_code/spatial/src/spatial/codegen/scalagen/ScalaGenFltPt.scala:107-122`).

## D-10 Implications

Matching Scalagen means matching this f64 compute and reclamp behavior, including double rounding for narrower floats, precision loss for wider floats, fixed-format wrap/truncation, Java `Math` special-value behavior, and the current `valid` quirks. MPFR/exact math would be a semantic improvement, not a port of today's reference. Matching synthesized hardware is a third contract again, because hardware math units may use different approximations, latencies, domains, and rounding than JVM `Math`. The lowest-risk Rust compatibility target is therefore "Scalagen f64 plus current reclamp"; any move to MPFR or hardware-unit semantics should be recorded as an intentional D-10 semantic change with updated golden tests.
