---
type: spec
status: draft
concept: data-types
source_files:
  - "argon/src/argon/lang/types/Bits.scala:8-171"
  - "argon/src/argon/lang/Bit.scala:9-51"
  - "argon/src/argon/lang/Fix.scala:8-224"
  - "argon/src/argon/lang/Flt.scala:9-157"
  - "argon/src/argon/lang/Vec.scala:11-228"
  - "spatial/emul/src/emul/FixFormat.scala:1-29"
  - "spatial/emul/src/emul/FixedPoint.scala:1-260"
  - "spatial/emul/src/emul/FltFormat.scala:1-29"
  - "spatial/emul/src/emul/FloatPoint.scala:1-501"
  - "spatial/emul/src/emul/Bool.scala:1-45"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenFixPt.scala:31-157"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenBits.scala:28-79"
source_notes:
  - "[[D0 - DSL Base Types]]"
  - "[[20 - Numeric Reference Semantics]]"
  - "[[60 - Counters and Primitives]]"
  - "[[50 - Math and Helpers]]"
  - "[[50 - Primitives]]"
  - "[[30 - Memory Simulator]]"
hls_status: rework
depends_on:
  - "[[D0 - DSL Base Types]]"
  - "[[20 - Numeric Reference Semantics]]"
  - "[[60 - Counters and Primitives]]"
  - "[[50 - Math and Helpers]]"
  - "[[50 - Primitives]]"
---

# Data Types

## Summary

Spatial data-type semantics are the combination of Argon's staged type surface and Scalagen's `emul` runtime. [[D0 - DSL Base Types]] defines `Bit`, `Fix`, `Flt`, `Vec`, `Struct`, `Text`, `Var`, and typeclasses such as `Bits`, `Arith`, `Order`, and `Num`. [[20 - Numeric Reference Semantics]] defines the bit-exact runtime behavior. When they disagree with native Scala, JVM, or hardware expectations, Scalagen wins for the simulator and is the reference semantics for the Rust port. The most important facts are fixed-point saturation boundaries, three rounding modes, `FloatPoint.clamp` packing, three-valued `Bool`, vector-as-bit-vector conversion, and the nondeterminism of unbiased fixed-point rounding.

## Formal Semantics

`Bits[A]` is the root bit-level typeclass. It supplies `nbits`, bit indexing, slices, reinterpret casts, zero/one/random, and conversions from constants (`argon/src/argon/lang/types/Bits.scala:8-101`). `Bit` is one-bit staged Boolean with boolean operations and `BitType` extraction (`argon/src/argon/lang/Bit.scala:9-51`). In Scalagen, a Boolean value is `Bool(value, valid)`, not a raw boolean. Logical operations combine host boolean values and AND their validity bits; `toString` prints `X` for invalid, and `toValidBoolean` returns `value && valid` (`spatial/emul/src/emul/Bool.scala:3-16`). This validity bit propagates through numeric and memory invalid values in [[30 - Memory Simulator]].

`Fix[S,I,F]` is staged integer/fixed-point. Its format is `FixFormat(sign, ibits, fbits)`, where `bits = ibits + fbits`; signed `MAX_VALUE` and `MIN_VALUE` are `2^(bits-1)-1` and `-2^(bits-1)`, and unsigned limits are `2^bits-1` and `0` (`spatial/emul/src/emul/FixFormat.scala:3-11`). Argon `FixFmt` converts singleton width evidence into the emulator format, while `Fix` stages arithmetic, bitwise ops, shifts, comparisons, casts, saturating variants, and unbiased variants (`argon/src/argon/lang/Fix.scala:8-147`, `argon/src/argon/lang/Fix.scala:193-208`).

Fixed-point runtime semantics are `BigInt`-backed and bit-exact. Standard `+`, `-`, `*`, `/`, `%`, bitwise ops, shifts, and comparisons all operate on raw fixed-point integer payloads and rewrap through the selected constructor (`spatial/emul/src/emul/FixedPoint.scala:14-77`). Multiplication shifts right by `fmt.fbits`; division shifts the numerator left by `fmt.fbits`; divide-by-zero is caught by `valueOrX` and returns invalid fixed-point (`spatial/emul/src/emul/FixedPoint.scala:18-23`, `spatial/emul/src/emul/FixedPoint.scala:102-104`).

There are three fixed-point rounding/wrapping modes. `clamped` wraps to the format, sign-extending or masking by format limits; it is the default for ordinary `FixAdd`, `FixSub`, `FixMul`, and `FixDiv` (`spatial/emul/src/emul/FixedPoint.scala:203-209`, `spatial/src/spatial/codegen/scalagen/ScalaGenFixPt.scala:75-82`). `saturating` clips to `MIN_VALUE_FP` and `MAX_VALUE_FP`; it backs `SatAdd`, `SatSub`, `SatMul`, `SatDiv`, and saturating casts (`spatial/emul/src/emul/FixedPoint.scala:218-222`, `spatial/src/spatial/codegen/scalagen/ScalaGenFixPt.scala:92-95`). `unbiased` uses four extra fractional bits, computes a fractional remainder, then calls `scala.util.Random.nextFloat()` to probabilistically round up (`spatial/emul/src/emul/FixedPoint.scala:232-241`). This is nondeterministic across runs and is explicitly a reference divergence to preserve or resolve in Rust.

`Flt[M,E]` is staged floating point with selectable mantissa and exponent widths (`argon/src/argon/lang/Flt.scala:9-157`). Runtime `FltFormat(sbits, ebits)` treats `sbits` as explicit significand bits excluding the implicit leading one, has one sign bit, and derives `bias`, normal exponent limits, and subnormal exponent (`spatial/emul/src/emul/FltFormat.scala:3-29`). Runtime `FloatPoint` stores a `FloatValue`: `NaN`, `Inf(negative)`, `Zero(negative)`, or `Value(BigDecimal)` (`spatial/emul/src/emul/FloatPoint.scala:3-83`).

`FloatPoint.clamp` is the formal packing function. It decomposes a `BigDecimal` value into sign, exponent, and mantissa; handles zero, overflow to infinity, normal values, subnormals, and underflow to signed zero; and rounds mantissa bits with a round-to-even style step (`spatial/emul/src/emul/FloatPoint.scala:318-398`). `convertBackToValue` defines the inverse path used after clamping (`spatial/emul/src/emul/FloatPoint.scala:399-433`). The implementation also contains a documented but unexplained subnormal guard using `x > 1.9`; this remains an open Scalagen question, but it is still part of current reference behavior.

Transcendental numeric helpers are not format-exact. Scalagen's shared `Number` helpers route fixed and floating square roots, exponentials, logs, trigonometric functions, and sigmoid through host `Double` math before reclamping to the target format (`spatial/emul/src/emul/Number.scala:79-156`). That is part of reference behavior for [[50 - Math and Helpers]].

Bit-vector semantics are exposed through `DataAsBits`, `BitsAsData`, `DataAsVec`, and `VecAsData`. Scalagen lowers fixed and floating values to their `.bits` arrays, a `Bit` to a one-element `Array[Bool]`, and vectors to `Array[A]`; reconstruction uses `FloatPoint.fromBits`, `FixedPoint.fromBits`, or the head bit (`spatial/src/spatial/codegen/scalagen/ScalaGenBits.scala:47-74`, `spatial/src/spatial/codegen/scalagen/ScalaGenVec.scala:7-47`). Argon `Vec` is also a staged vector abstraction with `asBits`, slicing, concatenation, packing, reverse, equality, zero/one, and random (`argon/src/argon/lang/Vec.scala:11-228`). [[60 - Counters and Primitives]] records the important zero-first lane ordering used by Scalagen vector concat.

Mux-family value selection is part of data semantics because it decides which typed value is observed. `Mux` is a normal if-else; `PriorityMux` is a first-true cascade with invalid fallback; `OneHotMux` is emitted by Scalagen as `collect{case (sel,d) if sel => d}.reduce{_|_}` (`spatial/src/spatial/codegen/scalagen/ScalaGenBits.scala:28-46`). That OR-reduction is only semantically valid when exactly one lane is true. The IR-level `OneHotMux` rewrite warns only when multiple literal-true selectors are statically visible, so dynamic multi-true cases can still reach Scalagen and produce a bitwise union rather than choosing one value (`src/spatial/node/Mux.scala:19-37`). This is a real divergence to settle for Rust.

## Reference Implementation

[[20 - Numeric Reference Semantics]] is normative. All one-line Scalagen lowerings delegate to `emul`; for example `FixAdd` emits `$a + $b`, `FixFMA` emits `($m1 * $m2) + $add`, and bit selectors emit `if`, OR-reductions, or priority cascades (`spatial/src/spatial/codegen/scalagen/ScalaGenFixPt.scala:75-150`, `spatial/src/spatial/codegen/scalagen/ScalaGenBits.scala:28-46`). Saturation boundaries, invalid values, NaN/infinity handling, and packing all come from `emul`, not host machine arithmetic.

## HLS Implications

HLS should map fixed-point and bit-vector types to target arbitrary-precision types, but the Rust simulator needs a `BigInt`/`BigDecimal` equivalent to match Scalagen. The port must decide whether unbiased rounding remains nondeterministic via RNG or becomes deterministic with a seeded or exact rule; until resolved, matching Scalagen means using nondeterministic random rounding. Floating custom formats cannot be delegated to native `f32`/`f64` if bit parity is required, because `FloatPoint.clamp` defines custom subnormal and overflow behavior.

## Open questions

- [[open-questions-semantics#Q-sem-09 - 2026-04-25 Unbiased rounding nondeterminism]] tracks whether Rust should match `Random.nextFloat()` or choose reproducible stochastic rounding.
- [[open-questions-semantics#Q-sem-10 - 2026-04-25 FloatPoint clamp heuristics]] tracks whether the `x > 1.9` subnormal guard is required semantics or an implementation artifact.
- [[open-questions-semantics#Q-sem-19 - 2026-04-25 OneHotMux multi-true semantics]] tracks Scalagen's OR-reduce behavior when more than one selector is true.
