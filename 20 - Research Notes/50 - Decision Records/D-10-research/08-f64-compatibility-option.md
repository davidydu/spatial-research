---
type: research
decision: D-10
angle: 8
title: f64 compatibility option and divergence labels
date: 2026-04-27
---

# f64 compatibility option and divergence labels

## 1. Compatibility Contract

Treating f64 compatibility as a deliberate D-10 policy means the Rust runtime is not asked to compute "the best" fixed- or float-format transcendental. It is asked to reproduce the Scalagen/emul path: generated fixed operations call `Number.ln/exp/sqrt/sin/.../pow`, and generated float operations call the parallel `Number.*` set (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/scalagen/ScalaGenFixPt.scala:137-149`, `/Users/david/Documents/David_code/spatial/src/spatial/codegen/scalagen/ScalaGenFltPt.scala:107-119`). `Number` itself marks both blocks as Double-backed TODOs and implements them by `x.toDouble`, `Math.*`, reconstructing the source format, and copying `x.valid` (`/Users/david/Documents/David_code/spatial/emul/src/emul/Number.scala:96-114`, `/Users/david/Documents/David_code/spatial/emul/src/emul/Number.scala:139-155`). The policy label should therefore be `scalagen_f64_compat`, not `exact` or `hardware`.

## 2. Storage And Conversion Requirements

Rust must model the storage boundary before it models the math call. `FixedPoint` stores raw scaled bits as `BigInt`, plus `valid` and `FixFormat` (`/Users/david/Documents/David_code/spatial/emul/src/emul/FixedPoint.scala:3`). Its f64 ingress goes through `toBigDecimal` divided by `2^fbits`, then `toDouble` (`/Users/david/Documents/David_code/spatial/emul/src/emul/FixedPoint.scala:86-88`). Re-entry from `Double` uses `BigDecimal(x) * Math.pow(2, fmt.fbits)`, converts to integer bits through `clamped(BigDecimal).toBigInt`, and wraps by sign extension or masking (`/Users/david/Documents/David_code/spatial/emul/src/emul/FixedPoint.scala:156-166`, `/Users/david/Documents/David_code/spatial/emul/src/emul/FixedPoint.scala:203-208`). A Rust MPFR or rational implementation would diverge unless it deliberately rounds down to this f64-and-truncate path.

For floats, Rust must preserve the current `FloatValue` representation: `NaN`, signed `Inf`, signed `Zero`, or finite `Value(BigDecimal)` (`/Users/david/Documents/David_code/spatial/emul/src/emul/FloatPoint.scala:84-112`). `FloatPoint.toDouble` maps those cases to JVM doubles, including signed zero, while `FloatPoint(Double, fmt)` rebuilds a `FloatValue` and `clamped` either keeps specials or rounds finite values into the target `FltFormat` (`/Users/david/Documents/David_code/spatial/emul/src/emul/FloatPoint.scala:190-195`, `/Users/david/Documents/David_code/spatial/emul/src/emul/FloatPoint.scala:275-277`, `/Users/david/Documents/David_code/spatial/emul/src/emul/FloatPoint.scala:417-427`). This is double rounding for f32/half-like formats and precision collapse for formats wider than binary64.

## 3. Specials, Validity, And Quirks

Compatibility also includes the uncomfortable propagation rules. Float arithmetic has explicit `NaN`, infinity, zero, and comparison cases before finite `BigDecimal` arithmetic (`/Users/david/Documents/David_code/spatial/emul/src/emul/FloatPoint.scala:12-82`). Invalid fixed values are `value = -1, valid = false`, while invalid floats are `NaN` with `valid = false` (`/Users/david/Documents/David_code/spatial/emul/src/emul/FixedPoint.scala:161`, `/Users/david/Documents/David_code/spatial/emul/src/emul/FloatPoint.scala:287`). Unary transcendentals restore only the input validity after constructing a fresh result, and `pow` is asymmetric: it uses both operands' `toDouble` values but only copies base validity (`/Users/david/Documents/David_code/spatial/emul/src/emul/Number.scala:98-103`, `/Users/david/Documents/David_code/spatial/emul/src/emul/Number.scala:141-145`). Scalagen's `FltIsPosInf`, `FltIsNegInf`, and `FltIsNaN` likewise return `Bool(predicate, x.valid)` rather than treating specials as validity failures (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/scalagen/ScalaGenFltPt.scala:64-66`).

Operation quirks should receive divergence labels in tests. Fixed `log2` exists only as a helper and is `Math.log(x.toDouble) / Math.log(2)` reclamped to fixed format (`/Users/david/Documents/David_code/spatial/emul/src/emul/Number.scala:102`); the float `Number` block and Scalagen float lowering have no `log2` peer (`/Users/david/Documents/David_code/spatial/emul/src/emul/Number.scala:140-155`, `/Users/david/Documents/David_code/spatial/src/spatial/codegen/scalagen/ScalaGenFltPt.scala:104-122`). Fixed `recipSqrt` lowers as `one / Number.sqrt(x)`, while float lowers through `Number.recipSqrt`; both sigmoids are emitted as an expression around `Number.exp`, not as a primitive call (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/scalagen/ScalaGenFixPt.scala:151-152`, `/Users/david/Documents/David_code/spatial/src/spatial/codegen/scalagen/ScalaGenFltPt.scala:121-122`).

## 4. Java Math Boundary

Local source proves only that Scalagen uses JVM `Math.*` calls through Scala source spelling (`/Users/david/Documents/David_code/spatial/emul/src/emul/Number.scala:98-113`, `/Users/david/Documents/David_code/spatial/emul/src/emul/Number.scala:141-154`). It does not prove Rust `f64` intrinsics or Rust `libm` are bit-identical to Java `Math` for every transcendental, platform, NaN payload, signed-zero edge, or libm version. They may agree for many ordinary inputs, but bit identity is `(unverified)`. A serious compatibility mode should therefore route Rust math through a `jvm_math_compat` shim boundary: either a tested per-op implementation, a JNI/golden-test oracle during migration, or a manifest that marks results as `rust_libm_approx_scalagen` when exact matching has not been proven.

## 5. Recommendation Implication

Choose f64 compatibility as the baseline regression policy, not as the final numeric truth. D-10 should define three explicit divergence labels: `scalagen_f64_compat` for current behavior, `format_exact_mpfr` for per-format oracle work, and `hardware_unit_match` for synthesized or HLS-lowered units. Rust should default golden tests for legacy parity to `scalagen_f64_compat`, including BigInt/BigDecimal storage, `toDouble`, JVM `Math`, reclamping, specials, validity quirks, and fixed-only `log2`. Any MPFR or hardware result that differs is not necessarily a bug, but it must be reported as a policy divergence rather than hidden under the word "correct."
