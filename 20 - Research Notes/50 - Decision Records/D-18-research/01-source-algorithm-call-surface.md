---
type: "research"
decision: "D-18"
angle: 1
---

# Source Algorithm and Call Surface

## Decision Anchor

D-18 asks whether the Rust float packer should reproduce `FloatPoint.clamp` bit-for-bit, including its undocumented `x > 1.9` correction, or adopt a cleaner custom-float algorithm with accepted divergence (`20 - Research Notes/40 - Decision Queue.md:79-81`). This is part of [[20 - Numeric Reference Semantics]]: Scalagen floats are not native JVM `Float`/`Double` values, but `emul.FloatPoint` values carrying a tagged `FloatValue` plus a `FltFormat` (`/Users/david/Documents/David_code/spatial/emul/src/emul/FloatPoint.scala:3-144`, `/Users/david/Documents/David_code/spatial/emul/src/emul/FltFormat.scala:3-8`).

## Clamp Algorithm

`FloatPoint.clamp(value: BigDecimal, fmt)` returns either a special `FloatValue` or packed `(sign, mantissa, exponent)` bits (`/Users/david/Documents/David_code/spatial/emul/src/emul/FloatPoint.scala:318-398`). Zero exits immediately as positive zero (`FloatPoint.scala:320-321`). Otherwise it estimates `y = floor(log2(abs(value)))` and `x = abs(value) / 2^y`; `log2BigDecimal` uses integer `BigInt` paths for values above and below one (`FloatPoint.scala:300-309`, `FloatPoint.scala:324-325`).

After the heuristic checks, range dispatch is simple. If `y > fmt.MAX_E`, the result is signed infinity (`FloatPoint.scala:358-360`). If `y >= fmt.MIN_E`, it is normal: compute one guard bit of mantissa precision, round up when that guard bit is set, and encode exponent as `y + bias` (`FloatPoint.scala:361-370`). If `fmt.SUB_E <= y < fmt.MIN_E`, it is subnormal: exponent bits are zero, the mantissa is shifted by `MIN_E - y + 1`, one guard bit can round it up, and a zero shifted mantissa underflows to signed zero (`FloatPoint.scala:372-390`). If `y < fmt.SUB_E`, it underflows to signed zero (`FloatPoint.scala:393-395`). `clamped` then converts the packed result back into a representable `FloatValue`, so stored `Value` floats are rounded to the target format (`FloatPoint.scala:399-433`).

## `x > 1.9` Edge

The special block at `FloatPoint.scala:335-339` runs before ordinary `x >= 2` normalization. When `y < fmt.SUB_E` but `x > 1.9`, it increments `y` and forces `x = 1`. Inference: this rescues values just below the smallest subnormal exponent bucket from automatic zero underflow by snapping them to the minimum subnormal candidate. For example, when the original estimate is `y = SUB_E - 1`, forcing `y = SUB_E, x = 1` allows the later subnormal path to return mantissa `1` instead of falling into the final underflow arm. The exact `1.9` threshold is unverified; there is no source comment explaining it, and it is not the IEEE half-ulp threshold. It looks like a hand-tuned guard around the lower subnormal boundary, not a general rounding rule.

The surrounding guards are also part of the behavior to preserve. If `x >= 2`, the code bumps `y` and recomputes `x`, correcting exponent underestimates (`FloatPoint.scala:340-343`). Then `cutoff = if (y < 0) 1 - 2^-sbits else 1`; if `x < cutoff`, `y` is decremented and `x` recomputed (`FloatPoint.scala:344-351`). Inference: this cutoff tolerates near-one mantissas for negative exponents while still re-bucketing clear underestimates.

## Call Surface

Direct emul callers are broad. `Value.bits(fmt)` calls `clamp` to pack bits, and `isSubnormal` calls it to detect exponent zero (`FloatPoint.scala:120-126`, `FloatPoint.scala:225-229`). `FloatPoint.clamped` calls it for every finite `Value`, while `NaN`, `Inf`, and `Zero` bypass it (`FloatPoint.scala:417-433`). Operators `unary_-`, `+`, `-`, `*`, `/`, and `%` all call `clamped`; so does `toFloatPoint`, all numeric/string `FloatPoint.apply` constructors, and `random` through `FloatPoint(scala.util.Random.nextDouble(), fmt)` (`FloatPoint.scala:149-165`, `FloatPoint.scala:214`, `FloatPoint.scala:264-284`, `FloatPoint.scala:472-482`). `Number.ceil`/`floor` call `FloatPoint.clamped`, and `Number.sqrt`, `exp`, `ln`, `pow`, trig, hyperbolic, reciprocal, reciprocal-sqrt, and sigmoid construct or combine `FloatPoint`s, so finite results re-enter clamp (`/Users/david/Documents/David_code/spatial/emul/src/emul/Number.scala:116-155`).

The DSL path is equally exposed. User `Flt` APIs stage arithmetic, comparison, min/max, abs, ceil/floor, transcendental, random, text, fixed, and float casts (`/Users/david/Documents/David_code/spatial/argon/src/argon/lang/Flt.scala:33-123`); the IR nodes define unstaged float arithmetic and `Number.*` hooks (`/Users/david/Documents/David_code/spatial/argon/src/argon/node/Flt.scala:22-93`). Casts to floats come from generic `numericCast`, `CastFltToFlt`, `CastTextToFlt`, and `CastFixToFlt` (`/Users/david/Documents/David_code/spatial/argon/src/argon/lang/api/Implicits.scala:16-28`, `Implicits.scala:224-245`). ScalaGen lowers those nodes to the same emul methods: arithmetic operators, `toFloatPoint`, `FloatPoint(text, fmt)`, `FloatPoint.random`, `Number.*`, and unfused FMA as `($m1 * $m2) + $add` (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/scalagen/ScalaGenFltPt.scala:63-123`). Fixed-to-float emits `$x.toFloatPoint(...)`, whose emul implementation constructs `FloatPoint(this.toBigDecimal, fmt)` (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/scalagen/ScalaGenFixPt.scala:116-117`, `/Users/david/Documents/David_code/spatial/emul/src/emul/FixedPoint.scala:90-95`). Executor resolvers use the same cast methods (`/Users/david/Documents/David_code/spatial/src/spatial/executor/scala/resolvers/FixResolver.scala:53-55`, `/Users/david/Documents/David_code/spatial/src/spatial/executor/scala/resolvers/FltResolver.scala:26-27`).
