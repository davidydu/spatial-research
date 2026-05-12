---
type: spec
concept: scalagen-numeric-reference-semantics
source_files:
  - "spatial/emul/src/emul/Number.scala:1-156"
  - "spatial/emul/src/emul/Bool.scala:1-45"
  - "spatial/emul/src/emul/FixFormat.scala:1-29"
  - "spatial/emul/src/emul/FixedPoint.scala:1-260"
  - "spatial/emul/src/emul/FltFormat.scala:1-29"
  - "spatial/emul/src/emul/FloatPoint.scala:1-501"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenFixPt.scala:1-157"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenFltPt.scala:1-129"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenBit.scala:1-40"
source_notes:
  - "[[scalagen-reference-semantics]]"
hls_status: rework
depends_on:
  - "[[10 - Overview]]"
  - "[[30 - Memory Simulator]]"
status: draft
---

# Numeric Reference Semantics

## Summary

This entry defines the bit-level meaning of Spatial's numeric primitives. **Together with the `emul` runtime, this is the ground-truth semantics that the Rust+HLS reimplementation must match.** Scalagen one-line lowerings such as `case FixAdd(x,y) => emit(src"val $lhs = $x + $y")` (`spatial/src/spatial/codegen/scalagen/ScalaGenFixPt.scala:75`) delegate directly to the `emul` operator definitions, so the meaning of every IR node *is* the meaning of the corresponding `emul` operator.

Three structural facts shape the semantics: (1) all numeric types carry a `valid` bit that propagates through every op (`spatial/emul/src/emul/FixedPoint.scala:14`, `Bool.scala:6`); (2) fixed-point has three rounding modes — `clamped`/`saturating`/`unbiased` — at `spatial/emul/src/emul/FixedPoint.scala:203-241`, each invoked by a different IR node family; (3) `FixedPoint` uses `BigInt` and `FloatPoint` uses `BigDecimal` with a tagged-union `FloatValue = NaN | Inf(neg) | Zero(neg) | Value(BigDecimal)` (`spatial/emul/src/emul/FloatPoint.scala:3-83`) — neither uses native `Long`/`Double` for storage.

## `FixFormat(sign, ibits, fbits)` and `FltFormat(sbits, ebits)`

`FixFormat` (`spatial/emul/src/emul/FixFormat.scala:3-29`) caches: `bits = ibits + fbits` (no separate sign bit; MSB of `ibits` when `sign=true`); `MAX_VALUE = if (sign) (1 << (ibits+fbits-1)) - 1 else (1 << (ibits+fbits)) - 1`; `MIN_VALUE = if (sign) -(1 << (ibits+fbits-1)) else 0` (`:10-11`). `combine(other)` (`:21-28`) takes max widths and ORs sign bits, bumping unsigned `ibits` by 1 when the result is signed — the format-promotion rule used by IR bit-width inference.

`FltFormat` (`spatial/emul/src/emul/FltFormat.scala:3-29`) treats `sbits` as the significand bits *excluding the implicit leading 1*, with implicit sign bit. So single-precision is `FltFormat(23, 8)`. Cached: `bits = sbits + ebits + 1`, `bias = 2^(ebits-1) - 1`, `MIN_E = -bias + 1`, `MAX_E = bias`, `SUB_E = MIN_E - sbits` (`:4-8`). `MAX_VALUE_FP` is built via `FloatPoint.fromBits` (`:10-14`); `MIN_POSITIVE_VALUE` is the smallest subnormal (`:17-22`).

## Three-valued `Bool` and three rounding modes

`Bool` is `(value: Boolean, valid: Boolean)` (`spatial/emul/src/emul/Bool.scala:3`). Logical ops propagate validity (`:5-11`): `Bool(this.value && that.value, this.valid && that.valid)` for `&`/`&&`/`||`/`^`/`===`/`!==`. `toString` prints `"X"` for `!valid` (`:16`); `toBoolean` returns `value` regardless of validity; `toValidBoolean` returns `value && valid` (`:13-14`). `ScalaGenDebugging`-emitted asserts use `toValidBoolean`, so X-valued conditions do not fire. `FALSE`/`TRUE` are pre-built valid singletons (`:33-34`).

`FixedPoint` has three constructors corresponding to three hardware rounding modes (`spatial/emul/src/emul/FixedPoint.scala:203-241`):

1. **`clamped`** (`:203-209`) — wraps on overflow. When `fmt.sign && bits.testBit(fmt.bits-1)`, OR with `fmt.MIN_VALUE`; else AND with `fmt.MAX_VALUE`. Default for `FixAdd/FixSub/FixMul/FixDiv` (`ScalaGenFixPt.scala:75-82`).
2. **`saturating`** (`:218-222`) — clips to `MIN_VALUE_FP`/`MAX_VALUE_FP`. Used by `SatAdd/SatSub/SatMul/SatDiv` and `+!`/`-!`/`*!`/`/!` (`:47-50`, `ScalaGenFixPt.scala:92-95`); also `FixToFixSat`.
3. **`unbiased(bits, valid, fmt, saturate=false)`** (`:232-241`) — RNG-based round-to-nearest. Input `bits` carries 4 extra fractional bits; extracts `biased = bits >> 4` and `remainder = (bits & 0xF) / 16.0f`, draws `rand = scala.util.Random.nextFloat()` (`:236`), rounds up if `rand + remainder >= 1`. Used by `UnbMul/UnbDiv/UnbSatMul/UnbSatDiv` and `*&`/`/&`/`*&!`/`/&!` (`:52-63`, `ScalaGenFixPt.scala:96-99`); also `FixToFixUnb/FixToFixUnbSat`.

**`unbiased` is non-deterministic.** `scala.util.Random` uses a JVM-seeded default RNG; two runs produce different bit-exact LSBs for every unbiased op. Author comment at `:235`: `TODO[5]: RNG here for unbiased rounding is actually heavier than it needs to be`. See Q-scal-01.

## `FixedPoint` operator semantics

Standard arithmetic operators delegate to `clamped` after raw `BigInt` arithmetic (`spatial/emul/src/emul/FixedPoint.scala:14-26`): `+`/`-`/`&`/`^`/`|` are direct; `*` does `(value * that.value) >> fmt.fbits` to restore Q-format scaling; `/` does `(value << fmt.fbits) / that.value` wrapped in `valueOrX{...}`; `%` adds a positive-modulus correction `if (result < 0) result + that.value` (`FixedPoint.scala:18-22`). Comparisons return `Bool(value-comparison, this.valid && that.valid)` (`:27-32`).

`valueOrX(thunk)` (`FixedPoint.scala:102-104`) catches any `Throwable` (typically `ArithmeticException` on divide-by-zero) and returns `FixedPoint.invalid(fmt) = new FixedPoint(-1, valid=false, fmt)` (`:161`). So `FixDiv(x, 0)` returns X-valued and propagates downstream. Logical right shift `>>>` is manual bit-manipulation (`:67-77`) since `BigInt` has no unsigned right shift.

## `FloatPoint.clamp` algorithm

The mantissa-exponent packing routine at `spatial/emul/src/emul/FloatPoint.scala:318-398` has signature `clamp(value: BigDecimal, fmt): Either[FloatValue, (Boolean, BigInt, BigInt)]`. Walkthrough:

1. **Zero check** (`:320-321`): always returns `Left(Zero(negative = false))` from value-zero input (even from `-0.0` BigDecimal, which BigDecimal cannot represent distinctly).
2. **Decomposition** (`:324-325`): `y = floor(log2(|value|))`, `x = |value| / 2^y`. `log2BigDecimal` (`:300-309`) chooses integer vs reciprocal based on `|value| >= 1`.
3. **Subnormal-saturation guard** (`:335-339`): `if (y < SUB_E && x > 1.9) { y += 1; x = 1 }`. The `1.9` is undocumented; see Q-scal-03.
4. **Mantissa overflow guard** (`:340-343`): `if (x >= 2) { y += 1; x = |value| / 2^y }`. Handles BigDecimal-precision cases where mantissa rounds to 2.0.
5. **Cutoff guard** (`:344-351`): `cutoff = if (y < 0) 1 - 2^(-sbits) else 1`; if `x < cutoff`, decrement `y`.
6. **Range dispatch** (`:358-395`):
   - `y > MAX_E` → `Left(Inf(negative = value < 0))` (overflow).
   - `y >= MIN_E` (normal) → build `mantissaP1 = floor((x-1) * 2^(sbits+1))`, round-to-even via `(mantissaP1 + lsb) >> 1`, return `Right((value < 0, mantissa, y + bias))`.
   - `y >= SUB_E && y < MIN_E` (subnormal) → build `mantissa = floor(x * 2^(sbits+1))`, `shift = MIN_E - y + 1`, get `shiftedMantissa = (mantissa >> shift) + lsbRoundBit`. If `> 0`, return `Right((sign, shiftedMantissa, 0))`; else underflow to `Left(Zero(negative = value < 0))`.
   - `y < SUB_E` → underflow to `Left(Zero(negative = value < 0))`.

`convertBackToValue` (`:399-415`) is the inverse. `clamped(value, valid, fmt)` (`:417-433`) does the round-trip on `Value(_)`; `NaN`/`Inf`/`Zero` bypass.

**Subnormal flushing**: custom-format subnormals that round to a zero shifted-mantissa underflow to signed `Zero` (`:386-391`) — denormal-flush-to-zero. A Rust port targeting custom formats cannot just cast to `f32`/`f64` because those have a different subnormal range; matching scalagen requires reimplementing `clamp`.

## `FloatValue` algebra and `FloatPoint` operators

`FloatValue` is a sealed hierarchy at `spatial/emul/src/emul/FloatPoint.scala:3-83`. `+`/`-`/`*`/`/`/`%` are pattern-match case tables encoding IEEE rules: `NaN` propagates, `Inf+(-Inf) = NaN`, `Inf*Zero = NaN`, `Zero/Zero = NaN`, `x/0 = Inf` with sign of `x` XOR sign of divisor (`FloatPoint.scala:12-56`). `<` and `===` return raw `Boolean` with `NaN`-comparisons-to-anything as `false` (`FloatPoint.scala:57-81`). `Zero(negative)` carries sign, so `+0.0` and `-0.0` are distinguishable. `bits(fmt)` packs IEEE-754 bit-arrays per variant (`FloatPoint.scala:88-110`).

`FloatPoint.+`/`-`/`*`/`/`/`%` delegate to `FloatValue` arithmetic, then call `FloatPoint.clamped` for format-rounding (`FloatPoint.scala:154-165`). `toFixedPoint(fmt)` performs IEEE-style range-clipping (`FloatPoint.scala:202-207`): `NaN -> 0` (matches `Double.NaN.toInt`); `Inf(neg) -> MIN/MAX_VALUE_FP`; `Zero -> 0`; `Value(v) -> FixedPoint(v, fmt)`.

## Number transcendentals and lowering

`Number` (`spatial/emul/src/emul/Number.scala:79-156`) provides shared transcendentals; **every one routes through `Double`** — e.g., `sqrt(x) = FixedPoint(Math.sqrt(x.toDouble), x.fmt).withValid(x.valid)` (`:98`); same for `recip/exp/ln/log2/pow/sin/cos/tan/sinh/cosh/tanh/asin/acos/atan` (`:97-112`, `:140-154`). Accuracy is bounded by IEEE double regardless of source format. `recip(x) = 1 / x` goes through `valueOrX`, so `recip(0)` is X-valued. `sigmoid(x) = 1/(exp(-x) + 1)` (`:114`, `:155`).

`ScalaGenFixPt` (`ScalaGenFixPt.scala:31-156`) maps each IR node to a one-liner: arithmetic ops use bare operators (`:75-82`); `SatAdd/SatSub/SatMul/SatDiv` use `+!`/`-!`/`*!`/`/!` (`:92-95`); `UnbMul/UnbDiv/UnbSatMul/UnbSatDiv` use `*&`/`/&`/`*&!`/`/&!` (`:96-99`); transcendentals delegate to `Number.*` (`:79`, `:137-148`); `FixToFix(x, fmt)` becomes `$x.toFixedPoint(...)` which shifts and re-clamps (`:107-108`, `FixedPoint.scala:90-94`); `FixFMA` is emitted **unfused** as `($m1 * $m2) + $add` (`:150`) — *not* a fused-precision FMA. `ScalaGenFltPt` is structurally identical for floats with `FltIsPosInf/FltIsNegInf/FltIsNaN` reading `FloatPoint.value` directly (`ScalaGenFltPt.scala:64-66`). `ScalaGenBit` maps `Not/And/Or/Xor/Xnor` to `!`/`&&`/`||`/`!==`/`===` (`ScalaGenBit.scala:27-39`).

`StatTracker.change` emits inline when `--resource-reporter` is set (`ScalaGenFixPt.scala:62-69`, `ScalaGenFltPt.scala:53-60`), tracking `(("FixPt", nbits), 1)`. `pushState`/`popState` gated by `AccelScope` (`ScalaGenController.scala:144-145`, `:172`).

## Ground-truth status

This entry is the bit-level reference for every numeric IR node. The Rust port must provide a `BigInt`-backed `FixedPoint` with `clamped`/`saturating`/`unbiased` constructors and `valueOrX` divide-by-zero handling; a `FloatPoint` with `FloatValue` tagged-union and the custom `clamp` (with subnormal flushing); a three-valued `Bool` with `(value, valid)` propagation; and `Number` transcendentals routed through `f64` (or higher precision if an MPFR path is preferred — but `f64` is the reference).

## HLS notes

`rework`. The `emul` numeric layer is pure Scala using `BigInt`/`BigDecimal`. An HLS target uses fixed bit-widths in synthesized hardware; the simulator-side replica uses arbitrary-precision integers (e.g., Rust's `num-bigint`) and must match scalagen bit-for-bit on every op family.

## Interactions

- **Upstream**: IR nodes from `spatial.node` (FixAdd/FixMul/FltAdd/Mux/etc.) and the type system in `spatial.lang` (Fix/Flt/Bit). Format inference passes (`spatial/src/spatial/transform/`) determine the `FixFormat`/`FltFormat` on each typed op.
- **Downstream**: every other scalagen entry that uses these types — [[30 - Memory Simulator]] (memories store `Number` subclasses), [[40 - FIFO LIFO Stream Simulation]] (streams parse strings into `FixedPoint`/`FloatPoint`), [[50 - Controller Emission]] (counter iters are `FixedPoint`).
- **Sibling**: `StatTracker` and `DRAMTracker` global counters are emitted alongside numeric ops.

## Open questions

- Q-scal-01 — Unbiased rounding's `Random.nextFloat()` nondeterminism.
- Q-scal-03 — `FloatPoint.clamp`'s `x > 1.9` heuristic.
- Q-scal-04 — `FixedPoint.toShort` shift-by-`bits` apparent bug.
- Q-scal-13 — Whether transcendentals should be format-exact (MPFR) or match scalagen's f64 round-trip.

See `open-questions-scalagen.md`.
