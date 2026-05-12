---
type: "research"
decision: "D-17"
angle: 2
---

# Current Spec and Call Surface

## Spec Anchor

The current canonical numeric reference is Scalagen plus `emul`, not a prose-only rule. [[20 - Numeric Reference Semantics]] states that fixed point has three constructor families, with `unbiased` as the stochastic one; [[50 - Data Types]] further says Scalagen/emul are the reference semantics for the Rust port when native Scala, JVM, or hardware intuitions disagree. In source, the ordinary fixed operators call `FixedPoint.clamped`, saturating operators call `FixedPoint.saturating`, and unbiased multiply/divide operators call `FixedPoint.unbiased` (`/Users/david/Documents/David_code/spatial/emul/src/emul/FixedPoint.scala:14-63`, `/Users/david/Documents/David_code/spatial/emul/src/emul/FixedPoint.scala:203-241`).

## Emulator Algorithm

`FixedPoint.unbiased(bits, valid, fmt, saturate=false)` expects `bits` to contain four extra fractional bits beyond the target representation. It computes `biased = bits >> 4`, extracts a sixteenth-granularity `remainder = (bits & 0xF) / 16.0f`, draws `scala.util.Random.nextFloat()`, and steps one unit farther from zero when `rand + remainder >= 1`; the result then either wraps through `clamped` or clips through `saturating` (`/Users/david/Documents/David_code/spatial/emul/src/emul/FixedPoint.scala:224-240`). For arithmetic, `*&` manufactures those four guard bits by left-shifting both operands by two before the product and final `>> fmt.fbits`; `/&` shifts the numerator by `fmt.fbits + 4`; `*&!` and `/&!` use the same raw preparation with `saturate = true` (`/Users/david/Documents/David_code/spatial/emul/src/emul/FixedPoint.scala:52-63`). This makes the present reference stochastic and process-global: no seed or event identity is part of the `FixedPoint.unbiased` signature.

## DSL and IR Surface

The user-facing `Fix` API exposes `*&`, `/&`, `*&!`, and `/&!` with comments describing probabilistic rounding, plus internal cast helpers `__toFixUnb` and `__toFixUnbSat` (`/Users/david/Documents/David_code/spatial/argon/src/argon/lang/Fix.scala:75-129`, `/Users/david/Documents/David_code/spatial/argon/src/argon/lang/Fix.scala:196-206`). The IR splits these into `UnbMul`, `UnbDiv`, `UnbSatMul`, `UnbSatDiv`, `FixToFixUnb`, and `FixToFixUnbSat` (`/Users/david/Documents/David_code/spatial/argon/src/argon/node/Fix.scala:338-358`, `/Users/david/Documents/David_code/spatial/argon/src/argon/node/Fix.scala:398-454`).

The constant-rewrite surface is not a clean policy oracle. Generic `Binary.rewrite` folds two constants by calling the op's `unstaged` implementation (`/Users/david/Documents/David_code/spatial/argon/src/argon/Binary.scala:34-40`), so constant `UnbMul`/`UnbDiv` can consume randomness at staging time through the same `FixedPoint` operators. But constant `FixToFixUnb` and `FixToFixUnbSat` rewrite to `c.toFixedPoint(f2.toEmul)`, the same expression used by wrapping and saturating casts, thereby bypassing both stochastic rounding and saturation for constants (`/Users/david/Documents/David_code/spatial/argon/src/argon/node/Fix.scala:313-358`). That mismatch is part of today's call surface.

## Lowering Surfaces

ScalaGen preserves the emulator contract directly: `UnbMul`/`UnbDiv`/`UnbSatMul`/`UnbSatDiv` emit `*&`, `/&`, `*&!`, `/&!`, while `FixToFixUnb` and `FixToFixUnbSat` emit `FixedPoint.unbiased($x.value, $x.valid, targetFmt, ...)` (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/scalagen/ScalaGenFixPt.scala:92-114`). The Scala executor is aligned for casts, and its generic n-ary resolver executes unbiased arithmetic through each IR node's `unstaged` fixed-point function (`/Users/david/Documents/David_code/spatial/src/spatial/executor/scala/resolvers/FixResolver.scala:37-51`, `/Users/david/Documents/David_code/spatial/src/spatial/executor/scala/resolvers/NaryResolver.scala:30-45`).

Chisel/Fringe encode a related but not identical stochastic surface. ChiselGen maps unbiased arithmetic and casts to `Math.mul`/`Math.div`/`Math.fix2fix` with `Unbiased` plus `Wrapping` or `Saturating` (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/chiselgen/ChiselGenMath.scala:33-40`, `/Users/david/Documents/David_code/spatial/src/spatial/codegen/chiselgen/ChiselGenMath.scala:75-78`). Fringe defines `Unbiased` as LFSR stochastic rounding, and `fix2fixBox` adds PRNG low bits before shaving fractional bits (`/Users/david/Documents/David_code/spatial/fringe/src/fringe/templates/math/RoundingMode.scala:3-8`, `/Users/david/Documents/David_code/spatial/fringe/src/fringe/templates/math/Converter.scala:36-44`). `BigIPSim` also has a literal fast path that uses `scala.math.random` salt for unbiased fractional shrink (`/Users/david/Documents/David_code/spatial/fringe/src/fringe/targets/BigIPSim.scala:237-270`).

## Test Evidence and Gaps

`SpecialMath` is the focused test: it repeats `*&` over 256 samples and checks mean error below one `_4`-fractional LSB, then checks `*&!` saturation endpoints (`/Users/david/Documents/David_code/spatial/test/spatial/tests/feature/math/SpecialMath.scala:36-93`). Its own print notes division still needs checking (`/Users/david/Documents/David_code/spatial/test/spatial/tests/feature/math/SpecialMath.scala:106-107`). Other hits, such as `SmallTypeTransfers`, use exactly representable `*&` cases and therefore do not constrain the stochastic policy (`/Users/david/Documents/David_code/spatial/test/spatial/tests/feature/transfers/SmallTypeTransfers.scala:20-35`, `/Users/david/Documents/David_code/spatial/test/spatial/tests/feature/transfers/SmallTypeTransfers.scala:60-69`). Current evidence therefore establishes a stochastic intent, not a canonical seed, sequence, cast, or constant-folding policy.
