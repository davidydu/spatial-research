---
type: "research"
decision: "D-10"
angle: 5
---

# D-10 Angle 5: Format Precision Effects

## Conversion Boundary

The emulator has arbitrary-ish formats, but the current transcendental path crosses an f64 boundary. `Number` requires every numeric emulation to expose `toDouble` and `toBigDecimal`, and defines `isExactDouble` by comparing a value against its own `toDouble` result (`emul/src/emul/Number.scala:70-76`). The main scalar math helpers are explicitly on the JVM `Math` path: fixed-point sqrt, exp, log, pow, and trig first call `x.toDouble`, then construct `FixedPoint(..., x.fmt)` (`emul/src/emul/Number.scala:96-113`). Float-point variants do the same with `FloatPoint(..., x.fmt)` (`emul/src/emul/Number.scala:139-155`). D-10 precision analysis should therefore treat these helpers as f64 reference-model calls with target-format re-quantization, not native fixed-point or custom-float operations.

## Float Formats and Double Rounding

`FltFormat` is parameterized by significand bits and exponent bits, deriving total bits, bias, min normal exponent, max exponent, and subnormal exponent (`emul/src/emul/FltFormat.scala:3-8`). `FloatPoint` defines half, float, and double as `FltFormat(10,5)`, `(23,8)`, and `(52,11)` (`emul/src/emul/FloatPoint.scala:259-263`). Numeric values are stored as `Value(BigDecimal)` (`emul/src/emul/FloatPoint.scala:112`), but `apply(Double, FltFormat)` first converts the JVM `Double` into a `FloatValue`, preserving NaN, infinity, and signed zero specially and otherwise wrapping `BigDecimal(x)` (`emul/src/emul/FloatPoint.scala:135-140`, `emul/src/emul/FloatPoint.scala:275-277`). `clamped` then calls `clamp`, converts mantissa/exponent bits back into a rounded `FloatValue`, and stores that rounded value (`emul/src/emul/FloatPoint.scala:417-427`).

For normal values, `clamp` forms one extra mantissa bit, rounds by adding 1 if the dropped bit is set, and shifts (`emul/src/emul/FloatPoint.scala:361-364`); subnormals use a similar single discarded-bit test (`emul/src/emul/FloatPoint.scala:372-388`). That is target-format rounding after any earlier f64 rounding. For f32-like formats, the stored operand is usually exactly representable in f64, but f64 math produces a rounded binary64 result before the final f32 clamp. For custom formats wider than `DoubleFmt`, `toDouble` collapses mantissas beyond 53 binary digits and can overflow or underflow the exponent range before `FloatPoint.apply(Double, fmt)` sees the value (`emul/src/emul/FloatPoint.scala:190-195`).

## Fixed-Point Scaling

`FixFormat` is a scaled integer format: total bits are `ibits + fbits`, with signed or unsigned min/max raw values derived in scaled units (`emul/src/emul/FixFormat.scala:3-11`). `FixedPoint` stores a raw `BigInt` plus `valid` and `fmt` (`emul/src/emul/FixedPoint.scala:3`). Its exact decimal view is `BigDecimal(value) / 2^fbits`, and `toDouble` is precisely where that decimal view is rounded to f64 (`emul/src/emul/FixedPoint.scala:86-88`). Construction goes the other direction by shifting integral inputs left by `fbits` (`emul/src/emul/FixedPoint.scala:150-155`), but `apply(Double)` and even `apply(BigDecimal)` scale through `Math.pow(2, fmt.fbits)`, after which `clamped(BigDecimal)` truncates with `.toBigInt` (`emul/src/emul/FixedPoint.scala:156-165`).

Thus BigDecimal source text can still lose precision at fixed-point ingress: first through the Double-valued scale factor for very large `fbits`, then through integer truncation. Later `toFixedPoint` shifts raw bits and drops fractional precision when reducing `fbits`, without unbiased rounding (`emul/src/emul/FixedPoint.scala:90-94`). Wraparound clamping is not saturation; it masks or sign-extends into the format (`emul/src/emul/FixedPoint.scala:203-208`), while saturation is a separate path (`emul/src/emul/FixedPoint.scala:218-221`).

## Invalids, Specials, and Stored Precision

Float specials stay special through clamping: NaN, infinities, and signed zero bypass numeric rounding in `clamped` (`emul/src/emul/FloatPoint.scala:417-422`). `clamp` maps overflow to signed infinity and underflow to signed zero (`emul/src/emul/FloatPoint.scala:358-360`, `emul/src/emul/FloatPoint.scala:390-394`). `toDouble` preserves NaN, infinities, and signed zero (`emul/src/emul/FloatPoint.scala:190-195`), while `toBigDecimal` throws for NaN/Inf (`emul/src/emul/FloatPoint.scala:185-189`) and `toFixedPoint` maps NaN to zero and infinities to fixed min/max (`emul/src/emul/FloatPoint.scala:202-207`). Invalid fixed values are represented as `value = -1, valid = false` (`emul/src/emul/FixedPoint.scala:161`); invalid floats are `NaN` with `valid = false` (`emul/src/emul/FloatPoint.scala:287`). The conversion methods themselves mostly ignore `valid`, so invalid data can still yield numeric `toDouble` or bits unless consumers check the flag. BigDecimal storage is therefore real only while staying in `Value(v)`, `FixedPoint.value`, or `toBigDecimal`; it is lost at `FloatPoint.toDouble`, `FixedPoint.toDouble`, and every `Number` helper that calls JVM `Math`.

## D-10 Policy Implication

D-10 should specify two precision modes. A compatibility mode may keep the current f64 path for Scala-emulator parity and fast host math, but reports should label it "f64-quantized then target-clamped." Any HLS/verification mode that claims target numeric semantics needs format-aware conversion: avoid `toDouble` for wide formats, define IEEE-style rounding policy for f32/half, preserve NaN/Inf/valid behavior explicitly, and replace fixed-point BigDecimal scaling with integer/rational `2^fbits` arithmetic plus a stated rounding/saturation contract.
