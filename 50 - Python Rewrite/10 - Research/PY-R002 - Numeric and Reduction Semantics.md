---
type: deep-dive
title: "PY-R002 — Numeric and reduction semantics"
topic: python-numeric-and-reduction-semantics
project: spatial-python
session: 2026-09-30
status: draft
source_files:
  - "spatial@e7a8f2f:argon/src/argon/lang/Aliases.scala:8-112"
  - "spatial@e7a8f2f:src/spatial/lang/Aliases.scala:157-165"
  - "spatial@e7a8f2f:argon/src/argon/lang/Fix.scala:8-208"
  - "spatial@e7a8f2f:argon/src/argon/lang/Flt.scala:9-122"
  - "spatial@e7a8f2f:argon/src/argon/Cast.scala:60-85"
  - "spatial@e7a8f2f:argon/src/argon/Ref.scala:50-105"
  - "spatial@e7a8f2f:argon/src/argon/node/Fix.scala:64-167"
  - "spatial@e7a8f2f:argon/src/argon/node/Fix.scala:313-359"
  - "spatial@e7a8f2f:emul/src/emul/FixFormat.scala:3-27"
  - "spatial@e7a8f2f:emul/src/emul/FixedPoint.scala:3-104"
  - "spatial@e7a8f2f:emul/src/emul/FixedPoint.scala:149-240"
  - "spatial@e7a8f2f:emul/src/emul/FltFormat.scala:3-27"
  - "spatial@e7a8f2f:emul/src/emul/FloatPoint.scala:3-207"
  - "spatial@e7a8f2f:emul/src/emul/FloatPoint.scala:318-459"
  - "spatial@e7a8f2f:emul/src/emul/Number.scala:79-155"
  - "spatial@e7a8f2f:src/spatial/lang/control/ReduceClass.scala:17-96"
  - "spatial@e7a8f2f:src/spatial/lang/control/MemReduceClass.scala:96-103"
  - "spatial@e7a8f2f:src/spatial/node/Control.scala:57-101"
  - "spatial@e7a8f2f:src/spatial/transform/unrolling/ReduceUnrolling.scala:35-237"
  - "spatial@e7a8f2f:src/spatial/transform/unrolling/MemReduceUnrolling.scala:310-371"
  - "spatial@e7a8f2f:utils/src/utils/math/ReduceTree.scala:3-12"
  - "spatial@e7a8f2f:src/spatial/codegen/scalagen/ScalaGenFixPt.scala:72-152"
  - "spatial@e7a8f2f:src/spatial/codegen/scalagen/ScalaGenFltPt.scala:63-122"
  - "spatial@e7a8f2f:src/spatial/codegen/scalagen/ScalaGenReg.scala:14-64"
  - "spatial@e7a8f2f:src/spatial/transform/RewriteTransformer.scala:263-274"
  - "spatial@e7a8f2f:fringe/src/fringe/templates/math/Math.scala:271-363"
  - "spatial@e7a8f2f:fringe/src/fringe/templates/math/Math.scala:671-677"
  - "spatial@e7a8f2f:fringe/src/fringe/templates/math/Math.scala:844-867"
feeds_spec: []
---

## Question, authority, and result

This study addresses the numeric and reduction part of PY-Q003 in [[02 - Python Open Questions]] and supplies semantic constraints for [[PY-R001 - Programming Model Study]]. The target is a compiler whose semantic code and reference simulator are Python. A hidden Rust numeric evaluator is outside that direction. This is a proposed contract, not an adopted specification or a claim of compiler support.

The original revision is `spatial@e7a8f2f7f776dd0c5ac7fc03f16b3ed4d97021f0`. All source citations below use its unambiguous short SHA. Files were retrieved with `git show` at that revision; current checkout contents were not used as the authority. The original [[50 - Data Types]], [[60 - Reduction and Accumulation]], and [[20 - Numeric Reference Semantics]] supplied a reading map. Their Rust-port prescriptions are historical recommendations, not authority for Python. [[B0 - Python Literal Typing]] describes a previous Rust-language contract and surface comparison; its rules are not automatically inherited here.

**Recommendation.** Preserve explicit fixed widths and normalization after each typed operation. Use one pure Python arithmetic contract for checking constants and executing programs. Define binary floats by bits and an exact rounding algorithm. Separate an ordered fold from a reassociation-safe reduction and from a reduction with an explicitly fixed tree. Preserve the distinction between identity, initial seed, and existing destination state. Fix the legacy simulator's inconsistent rounding, comparison, conversion, and empty-domain behavior through explicit Python decisions; keep legacy expectations visible in conformance cases.

Evidence labels in this note have narrow meanings:

- **Source fact:** directly inspected original code, with a pinned citation.
- **Proposed policy:** a Python design choice, including every illustrative API name below.
- **Calculated expectation:** arithmetic derived from a listing or source path, without running Spatial.
- **Executed arithmetic probe:** the bounded Python experiment reproduced in this note. It is neither an execution of the original Scala compiler nor a Python Spatial implementation.

## Original numeric behavior

### Widths, signedness, and aliases

**Source fact.** Original `Int` is signed fixed point with 32 integer bits and no fractional bits; `Long` is the corresponding 64-bit type. The original type family also has signed and unsigned widths through 1024 bits. `Fix[S,I,F]` counts a total of `I+F` bits, with the sign bit inside that total. `Flt[M,E]` counts the implicit leading significand bit in `M`, while its emulator receives `M-1` explicit fraction bits. Half, Float, and Double use `(M,E)=(11,5),(24,8),(53,11)` respectively. (`spatial@e7a8f2f:src/spatial/lang/Aliases.scala:157-165`; `spatial@e7a8f2f:argon/src/argon/lang/Aliases.scala:8-112`; `spatial@e7a8f2f:argon/src/argon/lang/Fix.scala:8-16`; `spatial@e7a8f2f:argon/src/argon/lang/Flt.scala:9-15`.)

**Source fact.** A fixed value is an integer payload `r` representing `r/2^F`. Signed raw bounds are `[-2^(I+F-1), 2^(I+F-1)-1]`; unsigned bounds are `[0, 2^(I+F)-1]`. `FixFormat.combine` constructs a widened format, but the staged binary operators themselves take and return the same `Fix[S,I,F]` type. The existence of `combine` is not evidence for implicit expression promotion. (`spatial@e7a8f2f:emul/src/emul/FixFormat.scala:3-27`; `spatial@e7a8f2f:emul/src/emul/FixedPoint.scala:80-95`; `spatial@e7a8f2f:argon/src/argon/lang/Fix.scala:45-61`.)

### Fixed arithmetic and conversions

**Source fact.** Ordinary addition and subtraction operate on raw integers and wrap to the declared width. Multiplication uses `(a.raw*b.raw) >> F`; negative products therefore round downward when discarded low bits are nonzero. Division uses `(a.raw << F)/b.raw`, with BigInt integer division, before wrapping. Ordinary division and modulus catch any thrown `Throwable` through `valueOrX` and produce an invalid value. Saturating division at line 50 is not wrapped in that helper. `%` first takes the integer remainder and adds the divisor if the remainder is negative, without requiring a positive divisor. (`spatial@e7a8f2f:emul/src/emul/FixedPoint.scala:14-25`; `spatial@e7a8f2f:emul/src/emul/FixedPoint.scala:47-63`; `spatial@e7a8f2f:emul/src/emul/FixedPoint.scala:102-104`; `spatial@e7a8f2f:emul/src/emul/FixedPoint.scala:203-221`.)

**Calculated expectation.** With a signed integer type, ordinary runtime `-3 / 2` is `-1`. However, a nonconstant numerator divided by a positive constant power of two can be rewritten to `FixDivSRA`, emitted as arithmetic right shift, giving `-2` for `-3`. Both-constant division is evaluated earlier as `q/r`, giving `-1`. Thus source form can select different answers. This is an identified source-path disagreement, not an original compiler execution. (`spatial@e7a8f2f:argon/src/argon/node/Fix.scala:133-155`; `spatial@e7a8f2f:src/spatial/codegen/scalagen/ScalaGenFixPt.scala:78-89`.)

**Source fact.** Literal/host ingress and fixed-to-fixed casts are not uniformly rounded. `FixedPoint(BigDecimal/String, fmt)` multiplies by `2^F` and converts to BigInt, discarding toward zero; narrowing a fixed value uses arithmetic right shift. The constructor uses `Math.pow` for scale, whereas the cast uses integer shifts. The staged `Fix.value` calculates exactness, and `ExpType.from` can ignore loss, warn, or emit an error according to its arguments. `Lifter.apply` requests a warning, not an unconditional rejection. Scala primitive lifts choose I32/I64/F32/F64 from their primitive type. (`spatial@e7a8f2f:emul/src/emul/FixedPoint.scala:90-95`; `spatial@e7a8f2f:emul/src/emul/FixedPoint.scala:149-166`; `spatial@e7a8f2f:argon/src/argon/lang/Fix.scala:149-165`; `spatial@e7a8f2f:argon/src/argon/Ref.scala:50-105`; `spatial@e7a8f2f:argon/src/argon/Cast.scala:60-68`; `spatial@e7a8f2f:argon/src/argon/lang/api/Implicits.scala:129-137`.)

**Calculated expectation.** In a destination with one fractional bit, ingress of `-0.75` produces raw `-1` (`-0.5`), while narrowing an exact two-fractional-bit `-0.75` produces raw `-2` (`-1`). The Python recommendation deliberately unifies those paths under declared quantization instead of reproducing this distinction.

**Source fact.** Saturating/unbiased casts have another constant-versus-runtime discrepancy. Their constant rewrites call ordinary `toFixedPoint`; runtime Scalagen emits `saturating(x.value, target_fmt)` or `unbiased(x.value, target_fmt)` directly, without the source-to-target fractional rescaling performed by ordinary `toFixedPoint`. Saturation beyond a bound returns `fmt.MIN_VALUE_FP` or `MAX_VALUE_FP`, whose validity is true, even if the input validity is false. (`spatial@e7a8f2f:argon/src/argon/node/Fix.scala:326-359`; `spatial@e7a8f2f:src/spatial/codegen/scalagen/ScalaGenFixPt.scala:107-114`; `spatial@e7a8f2f:emul/src/emul/FixedPoint.scala:218-221`; `spatial@e7a8f2f:emul/src/emul/FixFormat.scala:13-16`.)

**Calculated expectation.** Converting exact `1.5`, source `F=2` raw `6`, to destination `F=1` by an ordinary cast yields raw `3` (`1.5`). The inspected runtime saturating cast feeds raw `6` directly to the target and yields `3.0` if it fits. A constant saturating cast goes through ordinary rescaling instead. This example must be tested separately in any eventual legacy harness.

### Rounding helpers and stochastic rounding

**Source fact.** The emulator's fixed `floor` and `ceil` first remove low bits with an arithmetic right shift. `floor` then subtracts one for a negative fractional value; `ceil` adds one only for a positive fractional value. The comments do not establish correct mathematical floor/ceiling for negative values. (`spatial@e7a8f2f:emul/src/emul/Number.scala:79-90`.)

**Calculated expectation.** With enough range, `floor(-0.5)` follows the inspected code to `-2`, and `ceil(-0.5)` to `-1`. Proposed mathematical results are `-1` and `0`. These are source calculations, not observed Scala results.

**Source fact.** The operation named `unbiased` consumes four extra fractional bits, calls global `scala.util.Random.nextFloat()`, and either retains `bits >> 4`, increments a nonnegative base, or decrements a negative base. This is not a specified reproducible stream, and the negative branch is not rounding to the two neighboring representable values. (`spatial@e7a8f2f:emul/src/emul/FixedPoint.scala:232-240`.)

**Calculated expectation.** For extended raw `-20`, the exact target raw value is `-1.25`. The source base is `-2`, remainder `12/16`; it returns `-3` when `rand>=1/4`, otherwise `-2`. Correct stochastic rounding between adjacent raw values would return `-1` with probability `3/4` and `-2` with probability `1/4`. Merely seeding the old helper would reproduce a biased rule.

### Floating values and packing

**Source fact.** The original emulator stores tagged NaN, infinity, signed zero, and finite BigDecimal values, then reclamps arithmetic results. Its format has a sign bit, an explicit fraction of `M-1` bits, a biased exponent, and subnormal exponent limits. NaN/Inf/Zero bypass finite clamping. (`spatial@e7a8f2f:emul/src/emul/FloatPoint.scala:3-46`; `spatial@e7a8f2f:emul/src/emul/FloatPoint.scala:84-110`; `spatial@e7a8f2f:emul/src/emul/FloatPoint.scala:144-165`; `spatial@e7a8f2f:emul/src/emul/FloatPoint.scala:417-432`; `spatial@e7a8f2f:emul/src/emul/FltFormat.scala:3-8`.)

**Source fact.** The normal packer calculates an extra fraction bit, then uses `(mantissaP1 + low_bit) >> 1`. It does not inspect parity of the retained significand at a tie. Subnormal rounding likewise adds the first discarded bit; very small values encounter an `x>1.9` heuristic or flush to zero. A rounded significand carry is returned without a corresponding explicit exponent carry in the tuple. (`spatial@e7a8f2f:emul/src/emul/FloatPoint.scala:318-395`.)

**Calculated expectation.** In a format with precision `M=3`, `1.125` is halfway between `1.0` and `1.25`. The original normal formula chooses `1.25`; nearest/ties-to-even chooses `1.0`. Therefore the existing original note's description of this formula as round-to-even is incorrect. Underflow of a result that is smaller than half the minimum subnormal is ordinary rounding to zero; it is not evidence that *all* subnormals are flushed.

**Source fact.** Several special-value paths also disagree internally. `FloatValue.===` explicitly handles NaN as unequal and signed zeros as equal, but `FloatPoint.===/!==` use host equality/inequality on tagged values. The `(_:Inf,b)` less-than case uses `b.negative`, rather than the infinity's sign. Adding two zeros always returns positive zero. `isPosZero` and `isNegZero` test the opposite sign names. `fromBits` creates a valid value regardless of input bit validity. (`spatial@e7a8f2f:emul/src/emul/FloatPoint.scala:12-22`; `spatial@e7a8f2f:emul/src/emul/FloatPoint.scala:57-82`; `spatial@e7a8f2f:emul/src/emul/FloatPoint.scala:167-183`; `spatial@e7a8f2f:emul/src/emul/FloatPoint.scala:220-224`; `spatial@e7a8f2f:emul/src/emul/FloatPoint.scala:435-459`.)

**Calculated expectation.** The inspected FloatPoint equality path can treat its single tagged NaN as equal to itself and distinguish the zero tags; the lower-level FloatValue method states the opposite. These expectations need a Scala harness before being reported as executed behavior. Their presence rules out describing the emulator as uniformly IEEE compliant.

**Source fact.** Float-to-fixed conversion maps NaN to zero, infinities to destination extrema, and finite values through fixed constructors. Finite out-of-range values therefore follow wrapping construction, not general range clipping. Shared transcendental helpers use host Double math for square root, exp, logarithms, powers, and trig; reciprocal and sigmoid are instead built from typed division/arithmetic. (`spatial@e7a8f2f:emul/src/emul/FloatPoint.scala:202-207`; `spatial@e7a8f2f:emul/src/emul/FixedPoint.scala:156-166`; `spatial@e7a8f2f:emul/src/emul/Number.scala:96-114`; `spatial@e7a8f2f:emul/src/emul/Number.scala:139-155`.)

## Original reductions and accumulation

### Identity is not a seed

**Source fact.** Scalar `OpReduce` stores `ident: Option[A]` and `fold: Option[A]`; memory `OpMemReduce` stores `ident: Option[A]` and `fold: Boolean`. Scalar construction with a constant creates a register initialized to that constant, then places it either in `ident` for Reduce or in `fold` for Fold. A scalar explicit-accumulator Reduce carries neither option. There is also an overload disagreement: `FoldClass.apply(Lift)` requests `isFold=true`, but `FoldClass.apply(Sym)` requests `isFold=false`. `FoldClass.apply(Reg)` delegates to MemFold. (`spatial@e7a8f2f:src/spatial/node/Control.scala:57-101`; `spatial@e7a8f2f:src/spatial/lang/control/ReduceClass.scala:38-62`; `spatial@e7a8f2f:src/spatial/lang/control/ReduceClass.scala:78-96`.)

**Source fact.** A fully unrolled scalar fold prepends its initial value to the input list and applies the reduction tree. A partially unrolled scalar fold combines `reduce(treeResult, init)` on the first group and `reduce(treeResult, priorAccumulator)` on later groups. Ordinary Reduce discards the old accumulator on the first group. The tree replaces invalid lanes with an explicit identity, or propagates validity with an assumption that invalid lanes are trailing. The source itself flags this assumption as questionable for parallelization outside the innermost iterator. (`spatial@e7a8f2f:src/spatial/transform/unrolling/ReduceUnrolling.scala:55-76`; `spatial@e7a8f2f:src/spatial/transform/unrolling/ReduceUnrolling.scala:152-168`; `spatial@e7a8f2f:src/spatial/transform/unrolling/ReduceUnrolling.scala:194-224`.)

**Source fact.** `ReduceTree` combines adjacent pairs, carries an odd last element to the next level, and throws for an empty input sequence. Nothing in that helper proves the supplied lambda associative. Original fixed multiplication advertises `isAssociative=true` even when it discards fractional bits. (`spatial@e7a8f2f:utils/src/utils/math/ReduceTree.scala:3-12`; `spatial@e7a8f2f:argon/src/argon/node/Fix.scala:112-125`.)

**Calculated expectation.** For mapped values `[1,2]`, seed `10`, combine `a-b`, the fully unrolled tree over `[10,1,2]` yields `(10-1)-2=7`. Partially unrolled groups of one yield `1-10=-9`, then `2-(-9)=11`. A proposed ordered left fold yields `7` independently of the parallel annotation. Calling that proposed fold a preservation of every original Fold result would be false.

**Source fact.** Memory Reduce/Fold operate elementwise over the destination's reduction domain. Memory Reduce initially discards the old cell; MemFold always combines with the existing cell. The memory Fold `zero` argument supplies the tree's invalid-lane identity, not a replacement seed for the destination. The `ignoreParEdgeCases` configuration can make memory Reduce take the fold accumulation path too. (`spatial@e7a8f2f:src/spatial/lang/control/MemReduceClass.scala:96-103`; `spatial@e7a8f2f:src/spatial/transform/unrolling/MemReduceUnrolling.scala:310-358`.)

### Empty and disabled domains

**Source fact.** The default original register constructor initializes to `zero[A]`; a provided reset initializes to that value. Partially unrolled Scalagen executes a counter body only while its bound condition holds. If no group executes, no reduction store in that body occurs and the register retains its existing initialization/state. Scalar constant Reduce/Fold initialization is outside the reduction body. (`spatial@e7a8f2f:src/spatial/lang/Reg.scala:48-57`; `spatial@e7a8f2f:src/spatial/lang/control/ReduceClass.scala:55-62`; `spatial@e7a8f2f:emul/src/emul/Counter.scala:15-22`; `spatial@e7a8f2f:src/spatial/codegen/scalagen/ScalaGenController.scala:87-104`; `spatial@e7a8f2f:src/spatial/codegen/scalagen/ScalaGenReg.scala:14-17`.)

**Calculated expectation.** A dynamically empty explicit-accumulator Reduce retains old state, while a fresh implicit identity-free scalar Reduce can expose its register's default zero. Those are storage consequences, not proof that the reducing function has zero as an identity. The static fully unrolled path instead builds a lane tree. Known zero iteration counts satisfy the inspected `par>=nIter` selection, and invalid lane inputs may be supplied, rather than an empty list reaching ReduceTree. Static empty, dynamic empty, disabled controller, and all lanes invalid must therefore be separate cases; this study does not claim that every original path returns one universal answer. (`spatial@e7a8f2f:src/spatial/metadata/control/package.scala:1051-1065`; `spatial@e7a8f2f:src/spatial/transform/unrolling/UnrollingBase.scala:494-513`; `spatial@e7a8f2f:src/spatial/transform/unrolling/ReduceUnrolling.scala:55-76`; `spatial@e7a8f2f:src/spatial/transform/unrolling/ReduceUnrolling.scala:152-168`.)

### Specialized accumulators and FMA

**Source fact.** Scalagen specialized register accumulation is enabled conditionally. `first` writes the new input directly for add/multiply/min/max; otherwise it combines old state with the input. `RegAccumFMA` writes a product on first and product plus prior state afterward. Disable preserves state. These behaviors must survive any Python accumulator specialization. (`spatial@e7a8f2f:src/spatial/codegen/scalagen/ScalaGenReg.scala:41-64`.)

**Source fact.** Both fixed and float Scalagen FMA nodes emit ordinary multiply followed by add. The compiler can replace multiply-plus-add with FMA under fusion checks. The inspected fixed Chisel Math FMA also calls a truncating, wrapping multiply and adds the retimed addend; it does not establish a fused-precision fixed operation. Floating Chisel Math calls target `bigIP.ffma`; a Zynq implementation delegates to an FFma module. Target module naming/delegation is not an executed guarantee of its numerical configuration. (`spatial@e7a8f2f:src/spatial/codegen/scalagen/ScalaGenFixPt.scala:150-151`; `spatial@e7a8f2f:src/spatial/codegen/scalagen/ScalaGenFltPt.scala:120-121`; `spatial@e7a8f2f:src/spatial/transform/RewriteTransformer.scala:263-274`; `spatial@e7a8f2f:fringe/src/fringe/templates/math/Math.scala:671-677`; `spatial@e7a8f2f:fringe/src/fringe/templates/math/Math.scala:844-867`; `spatial@e7a8f2f:fringe/src/fringe/targets/zynq/BigIPZynq.scala:203-209`.)

**Calculated proof.** For the same fixed format, floor multiplication, and modular overflow, early product normalization has no precision effect on the final FMA value:

$$
\operatorname{wrap}_W\!\left(\operatorname{wrap}_W\!\left(\left\lfloor\frac{ab}{2^F}\right\rfloor\right)+c\right)
=\operatorname{wrap}_W\!\left(\left\lfloor\frac{ab+c2^F}{2^F}\right\rfloor\right).
$$

The addend raw `c` is an integer. The bounded probe below exhaustively checks this identity for small formats. It does not establish target RTL correctness, latency, saturation equivalence, mixed-format equivalence, or rounding toward zero. Floating multiply-plus-add does have two roundings and can differ from a one-rounding FMA.

### Hardware discrepancies still matter

**Source fact.** The fixed hardware rounding mode named Truncate is documented as rounding toward negative infinity. Hardware fixed division can generate an extra fractional bit then convert back, whereas the emulator directly integer-divides its scaled numerator. The hardware modulus path passes unsigned raw operands. Those paths warrant negative-operand differential cases; emulator agreement cannot be assumed. (`spatial@e7a8f2f:fringe/src/fringe/templates/math/RoundingMode.scala:3-8`; `spatial@e7a8f2f:fringe/src/fringe/templates/math/Math.scala:289-323`; `spatial@e7a8f2f:fringe/src/fringe/templates/math/Math.scala:337-363`.)

**Source fact.** BigIPSim explicitly supplies hardfloat rounding mode `0` for float division and conversions, and the included hardfloat constants identify `0` as nearest-even. Its add/multiply paths instead initialize their modules with DontCare and do not explicitly supply rounding mode in the inspected bodies. This evidence is specific to BigIPSim; it is not a claim about all FPGA targets. (`spatial@e7a8f2f:fringe/src/fringe/targets/BigIPSim.scala:136-173`; `spatial@e7a8f2f:fringe/src/fringe/targets/BigIPSim.scala:275-291`; `spatial@e7a8f2f:fringe/src/fringe/templates/hardfloat/common.scala:42-52`.)

## Proposed Python numeric contract

Every rule in this section is **proposed policy**. Names such as `Fix`, `Flt`, `cast`, and `tree_reduce` describe semantic operations; they are not implemented APIs or a final surface decision.

### Types and representation

Use `Fix(signed,I,F)`, with integer format parameters `I>=0`, `F>=0`, and total width `W=I+F>=1`. Signedness is explicit. Interpret its integer raw payload as `raw/2^F`; fixed values always store a normalized W-bit pattern, and signed interpretation uses two's complement. `Int` is an alias for signed `(32,0)`, with explicit `IntW(W)` and `UIntW(W)` families. No semantic 64-bit ceiling is introduced. Signed formats with `I=0` are fractional formats whose sign still occupies a bit; they must not assume `1` is representable. Hardware/backend format support is a separate capability check.

Use `Flt(P,E)`, where P includes the hidden leading bit, `P>=2`, and `E>=2`. Store a normalized bit pattern, not a host float or a decimal approximation. With `q=P-1` fraction bits and `bias=2^(E-1)-1`, exponent field zero represents zero/subnormal, fields `1..2^E-2` represent normals, and the all-ones field represents infinity/NaN. The storage width is `P+E`. Standard aliases are F16 `(11,5)`, F32 `(24,8)`, F64 `(53,11)`, and BF16 `(8,8)`. BF16 is a proposed extension, not an original alias. Other formats use the descriptor without silently claiming compatibility with a vendor's FP8 or alternate exponent encoding.

`Bool` is distinct from integers. Host `True` must not enter numeric ingress as `1` because Python's host type hierarchy happens to permit it. Numeric conversion of Bool requires an explicit operation. Arbitrary-precision compile-time sizes/format parameters are distinct from wrapping accelerator data; Python host integer evaluation does not turn an accelerator expression into a size proof.

### Literals and host ingress

Keep integer/decimal spelling and source span until typing. Parse finite decimal tokens as exact rationals, including exponent notation. Do not pass through Python float or `math.pow(2,F)`. The official Fraction documentation demonstrates the distinction between a string decimal and an already evaluated binary float. ([Python rational-number documentation](https://docs.python.org/3/library/fractions.html), accessed 2026-09-30.)

A context-free integer literal synthesizes Int32 and must fit; `-2147483648` is checked as a signed literal, without first rejecting the positive magnitude. A larger integer requires a wider annotation or constructor. A context-free decimal has an ambiguity between a fixed format and several float formats, so require a type annotation/constructor instead of a default. This is a proposed redesign; the original primitive-lift behavior above and the historical Rust no-default rule are separate evidence. The reason is to expose the representation at the first decimal use, not to make the compiler implementation easier.

Expected type flows through literal-only expression trees and through literal operands beside a typed operand. It does not recast an already typed variable or infer a wider expression type from the destination. Check each literal in that chosen format, then evaluate every operator in that format. A decimal literal checked as fixed is quantized with floor; one checked as Flt is rounded nearest/ties-even. A fixed literal outside the destination's numeric representable range is an error before quantization, even if floor would bring it back inside; negative unsigned literals are errors. A finite float literal which rounds to infinity is an ingress error; infinity and NaN remain expressible explicitly through dedicated constructors or bits.

For example, in `Fix(True,4,1)`, contextual `0.75*2` becomes `0.5*2=1.0`. Evaluating `0.75*2` on the host first would instead ingest `1.5`. Source capture must retain the tree; a builder needs token-backed literal nodes. A captured host float may enter only through an explicit `from_binary_float` operation that records its exact binary ratio and provenance. That operation does not reconstruct the original decimal token. Exact integer, string decimal, rational, and Decimal ingress may be supported by separate constructors with the same declared rounding contract.

### Fixed operators and overflow

For raw integers `a,b`, define these results before normalization:

| Operation | Raw result | Default overflow |
|---|---|---|
| add/subtract/negate | `a+b`, `a-b`, `-a` | wrap modulo `2^W` |
| multiply | `floor(a*b/2^F)` | wrap |
| divide `/` | `trunc_zero(a*2^F/b)` | wrap; active zero divisor faults |
| floor quotient `//` | `floor(a/b)*2^F` | wrap; active zero divisor faults |
| floor modulo `%` | `a-floor(a/b)*b` | wrap; active zero divisor faults |
| truncating `rem` | `a-trunc_zero(a/b)*b` | wrap; active zero divisor faults |
| bitwise and/or/xor/invert | operate on W-bit representations | normalize to W bits |
| left shift | `a*2^k` | wrap |
| arithmetic right shift | `floor(a/2^k)` | normalize |
| logical right shift | shift the unsigned W-bit pattern | normalize |

Division retains the numeric type, including for Int, as in Spatial. `//` computes the mathematical floor of the rational quotient and represents that integral result in the same type before the declared overflow action. `%` follows that floor quotient and has the divisor's sign; its negative-divisor behavior deliberately revises the original helper. `rem` uses a truncating *integer* quotient. No operator defers width normalization until assignment.

For unnormalized integer raw values, the paired equations are `a=q_t*b+r_t`, with `q_t=trunc_zero(a/b)` and `r_t=rem(a,b)`, and `a=q_f*b+r_f`, with `q_f=floor(a/b)` and `r_f=a%b`. For integer formats F=0, `/` represents q_t and `//` represents q_f; these equations also hold modulo the width after ordinary wrapping. The signed cases are explicit:

| Int operands a,b | `a/b` | `rem(a,b)` | `a//b` | `a%b` |
|---|---|---|---|---|
| -3, 2 | -1 | -1 | -2 | 1 |
| 3, -2 | -1 | 1 | -2 | -1 |
| -3, -2 | 1 | -1 | 1 | -1 |
| 3, 2 | 1 | 1 | 1 | 1 |

For fractional formats, `/` is a quantized fractional quotient and must not be substituted for the integer q_t in the remainder equation. In W=4,F=1, `-1.5/2=-0.5`, `-1.5//2=-1.0`, floor modulo is `0.5`, and truncating rem is `-1.5` because its integer quotient is zero. The exact remainder equations use the mathematical integer quotient; evaluating a reconstructed fixed expression can also lose equality through intermediate overflow. These distinctions are part of the language, not an accidental discrepancy between simulator helpers.

All four fixed operations fault on an active zero divisor. Type checking still checks captured inactive bodies, but numeric evaluation/faults are guarded by execution: an untaken runtime branch or invalid tail must not run a zero-divisor arithmetic operation. A constant evaluator must preserve a guarded fault rather than eagerly execute it; a required compile-time constant expression that actually evaluates division by zero reports the source diagnostic. Float division follows the separate special-value table below.

Shift amount is an integer value with a nonnegative runtime check. Negative shifts are a diagnostic, rather than a request to reverse direction. For `k>=W`, left/logical-right shift returns zero and arithmetic-right shift returns all sign bits. This revises inconsistent legacy rewrite cases. The checker may require/prove a target-specific bound before hardware emission; an unsupported dynamic shift is a capability error, not a different simulation value.

Saturating and checked variants are explicit operation attributes, not an implicit promotion. Compute the declared rounding first, then clip or range-check the resulting raw integer. `checked` reports overflow with the responsible operation and operand origins; `saturate` clips; ordinary arithmetic wraps. Constant folding uses exactly these steps. `abs(min_signed)` consequently wraps under ordinary arithmetic, saturates under a saturating absolute-value operation, and faults under checked absolute value.

Fixed `floor` and `ceil` are mathematical floor and ceiling of the rational value, returned in the same type with the operation's declared overflow. Conversion to an integer is not a call to either helper unless the declared conversion rounding requests it.

### Numeric conversion versus bit reinterpretation

A numeric fixed-to-fixed cast computes `r'=round(raw*2^(Fdst-Fsrc))`, then normalizes/clips/checks at the destination width. Default explicit fixed cast uses floor and wrapping; alternate modes are `toward_zero`, `nearest_even`, `ceil`, and checked/saturating overflow. Literal ingress remains stricter about range because it is a value declaration, whereas an explicit wrapping cast declares a lossy conversion.

A fixed-to-float or float-to-float cast performs one destination nearest-even rounding of the exact source value. A float-to-fixed cast uses a declared rounding mode, default toward zero, then a declared overflow mode, default checked. NaN and infinity cannot silently become integer zero/extrema. Checked and wrapping casts from nonfinite values fault; an explicitly saturating cast maps infinities to extrema but still faults on NaN. An application that wants NaN-to-zero must explicitly select/map that case.

`reinterpret_bits` requires equal storage widths and preserves bits, without quantization. `from_bits` checks payload width; bit vectors are low-bit first as an indexing convention, with byte serialization specified separately. NaN payload and signed-zero bits round-trip under reinterpretation; arithmetic may canonicalize NaNs as stated below. No numeric cast is used as a substitute for reinterpretation.

### Floats, rounding, and FMA

For finite arithmetic, decode bits to an exact rational, perform the operation exactly, then round once to the output format using nearest/ties-to-even. Find the binary exponent through integer bit lengths and comparisons; do not estimate it with host logarithms. Handle significand carry by renormalizing the exponent. Subnormals have uniform spacing `2^(1-bias-q)` and use the same tie rule; preserve gradual underflow and the sign of rounded zero. Overflow rounds to signed infinity. The proposal does not inherit the original `1.9` heuristic.

IEEE-like special values are part of the numeric contract: NaN arithmetic produces a canonical positive quiet NaN; ordered comparisons and equality with NaN are false, inequality is true; signed zeros compare numerically equal; infinities compare in numerical order. Under nearest-even, exact finite cancellation returns +0, `-0 + -0` returns -0, and multiplication/division zero signs use XOR. `min`/`max` propagate a NaN and choose -0/+0 respectively on a zero tie. A separate `minimum_number` operation could later specify NaN-eliding behavior. NaN payload preservation is promised only for bit operations, not arithmetic. Signaling NaN input is quieted by arithmetic with an invalid status.

Each arithmetic evaluation may return diagnostic status such as inexact, overflow, underflow, divide-by-zero, or invalid alongside bits; status is part of the simulation trace, not a global mutable rounding mode. Ordinary float division by zero produces the specified infinity/NaN and status rather than a fixed-number divide-by-zero fault. Absence of a hardware status output does not change the specified value. This is an IEEE-like subset proposal; it is not a claim of full IEEE-754 conformance.

Ordinary `a*b+c` preserves its two rounding points. Explicit `fma(a,b,c)` performs exact multiplication and addition followed by one rounding, with a separately specified special-value table. The SoftFloat primary documentation defines one-rounding FMA and nearest-even rounding; it can supply an independent test oracle for standard formats later, without becoming the Python implementation. ([Berkeley SoftFloat interface, sections 6.1 and 8.5](https://www.jhauser.us/arithmetic/SoftFloat-3/doc/SoftFloat.html), accessed 2026-09-30.)

A transform may contract multiply-plus-add only after proving identical results under the actual format/modes or after an explicit relaxed-numeric policy is adopted. No general fast-math flag is proposed here. Same-format wrap/floor fixed arithmetic has the equality proved above; saturating multiplication followed by addition can differ from one final saturation because an addend can undo a large product overflow. Such an operation needs its own descriptor and acceptance cases.

For float `%`, require an explicitly named semantic operation rather than accidentally inheriting host Python modulo: `fmod` uses a truncating integer quotient, `remainder` uses the nearest integer quotient with ties even, and a later `floor_mod` can specify sign-of-divisor behavior. The first two handle zero divisor/infinite dividend as NaN with invalid status and preserve dividend zero sign. Floating `//` is not implied by this design. An unsupported operation reports a typed capability diagnostic.

### Randomness and mathematical intrinsics

A stochastic-rounding operation must specify adjacent-value probability, RNG input/state, seed, stream identity, and consumption order. For raw exact value `k+f`, `k=floor(value)` and `0<=f<1`, choose `k+1` with probability f, otherwise k; this works for negative values too. A seed alone is not a complete reproducibility contract. The program should expose the random stream as an effect dependency or an explicit bit input, so scheduling cannot silently redraw or duplicate it. Until a versioned stream algorithm is adopted, stochastic operations are represented by the architecture but rejected as unsupported; the old four-bit algorithm is available only as a named compatibility experiment. This is a numerical correctness dependency, not a scarcity argument.

Pure Python integer/rational arithmetic can specify exact `sqrt` by comparing the candidate rounding boundaries after squaring; it need not use host Double as the authority. Fixed negative square root faults; float negative finite square root produces NaN with invalid status. Integer exponentiation uses typed operations and a specified evaluation order, or an explicitly widened exact-power operation. Reciprocal is typed division. Exp, log, trig, hyperbolic, and their inverses need separately declared approximation/range contracts; there is no universal claim that host `math` results are bit-exact for custom floats. Reject an intrinsic lacking an approved profile, retaining its node/type/span for a later extension. A compatibility host-math profile can record the original Double round-trip, but is not an exact Python numeric profile.

## Proposed reduction contract

### Three operations with different permissions

All combining regions are typed and pure: `(T,T)->T`, with numeric normalization after each combine. Contribution regions may have reads, writes, FIFO consumes, and runtime branches under the control/effect contract. Evaluate every active contribution exactly once in declared logical order; regrouping values never licenses regrouping, duplicating, or dropping contribution effects. A requested parallel schedule that conflicts with those effects must be proved legal or diagnosed. Silently serializing requested concurrent effects would hide a constraint failure.

| Proposed operation | Meaning | Permission to regroup | Empty enabled domain |
|---|---|---|---|
| `fold(init, values, combine)` | `s0=init`; `s[j+1]=combine(s[j],v[j])` in logical order | none without an equivalence proof | returns init |
| `reduce(values, op, identity)` | reduction under a recognized associative operator and valid typed identity | may regroup; may reorder only if commutativity also holds | returns identity |
| `tree_reduce(values, combine, identity?, tree)` | explicit ordered-leaf tree; default adjacent-pair balanced tree | must preserve the chosen tree | identity if supplied, otherwise domain fault |

The ordered fold is a deliberate redesign of the legacy arbitrary-lambda Fold behavior. It should not inherit the old spelling's false implication of unroll-invariant left-fold behavior. These meanings apply elementwise for memory variants, with destination initialization/reads and visible updates governed explicitly below.

An identity is neutral for the combine operation; a seed is included exactly once even when it is not neutral. In a no-padding tree_reduce, an identity parameter means the empty-domain result, not an instruction to insert one identity leaf per lane. A backend may pad only with a proven neutral identity. `reduce` uses built-in/verified identities, rather than trusting an arbitrary constant labeled `zero`. A declared empty result for an arbitrary tree should be named `empty_result` if it is not proved neutral.

### Associativity depends on format and mode

| Family under this proposal | Safe initial regrouping policy | Identity |
|---|---|---|
| Wrapping fixed add, including Int and fractional formats | associative and commutative: addition of raw integers modulo `2^W` | zero |
| Wrapping integer multiply (`F=0`) | associative and commutative: multiplication modulo `2^W` | raw bit pattern 1; in signed W=1 it denotes -1 |
| Fixed multiply with `F>0` | not generally associative; fold or explicit tree | numeric 1 only if representable, with its neutrality separately checked |
| Fixed numeric min/max on valid values | associative and commutative | maximum/minimum representable value |
| Raw bitwise AND/OR/XOR | associative and commutative | all-ones / zero / zero |
| Bool all/any/xor | associative and commutative | true / false / false |
| Signed saturating add/multiply; checked arithmetic | no generic permission; intermediate clipping/faults can depend on grouping | only after operation-specific proof |
| Float add/multiply/FMA, including standard formats | no generic associative permission; use fold or explicit tree | empty result distinct from proof of neutrality over all special values |
| Arbitrary user lambda | no permission from the word Reduce alone | cannot establish a law by a name or a few examples |

Unsigned saturating addition is a candidate later extension because `min(a+b,max)` is associative over nonnegative inputs; it requires a dedicated proof and tests rather than expanding the signed rule by analogy. NaN-sensitive float min/max need a separate proof that includes canonicalization and signed-zero tie behavior. Algebraic permissions belong to the typed operator descriptor, not a frontend-provided `isAssociative` boolean.

A fold or tree_reduce can still be parallelized when the emitted computation preserves its dependency graph; a sequential recurrence is not permission to silently replace a requested parallel combination tree. For a recognized associative reduction, `par` changes scheduling, not result bits or contribution order. For an explicit tree policy, `par` must not change the tree. If a user deliberately requests the original lane-group-dependent tree, changing its grouping is a semantic change and must be explicit.

### Initialization, destination state, and emptiness

Ordinary value-returning Reduce does not include previous register state. A `reduce_into` destination is written once with the reduction result, including the identity on an enabled empty invocation; a missing-identity empty invocation faults before the destination write. A controller disabled by its enable performs no invocation, contribution effect, initializer evaluation, or destination write. A enabled zero-count domain does invoke the operation and follows its empty rule. A selected branch decides whether the operation is invoked at all. These distinctions must be visible in the effect model.

`fold(init, ...)` evaluates init once for each enabled invocation and includes it exactly once. `fold_into(destination, ...)` explicitly snapshots the existing initialized value as its seed; it is not inferred because a Reg happened to be supplied. An empty fold_into retains that snapshot. Ownership checks reject contribution effects that mutate/read the owned accumulator in ways not represented by the fold state dependency. Memory fold_into snapshots and folds each selected destination cell, while an empty destination index domain performs no cell access. Map-domain emptiness and destination-domain emptiness are different tests.

A no-identity tree_reduce reports a static domain diagnostic when empty is known, and a source-aware domain fault when a runtime count is zero. It returns the sole value without combining for a singleton. It cannot return an arbitrary register reset because storage was allocated earlier. A fixed identity is quantized/type-checked before use; a floating identity/empty result preserves declared signed-zero and NaN behavior. An accumulator specialization must retain first/enable/init semantics and the chosen combination order.

### What source compatibility requires

For recognized modulo sum/product reductions, the proposed regrouping contract preserves the arithmetic result on nonempty, valid original cases, including ReduceTiny's expected sum `120`. That example alone does not test identity, state, emptiness, floating reassociation, or effects. The old constructor initializes the identity register separately, while the new semantic identity determines the empty result deliberately. (`spatial@e7a8f2f:test/spatial/tests/feature/control/ReduceTiny.scala:7-15`; construction and unrolling citations above.)

An explicit original-tree/init policy is necessary to reproduce arbitrary-lambda legacy programs: record fully versus partially unrolled structure, lane grouping, leaf order, invalid-lane handling, seed position, `reduce(newGroup,prior)` operand order, memory-fold behavior, and relevant compiler configurations. It should be represented as imported semantic metadata, not silently selected by a performance annotation on a new program. The subtraction example shows why an ordered fold is insufficient for that compatibility requirement.

Retaining a tree policy alone is insufficient for full old-program fidelity: original casts, floating packing, overload choices, specialized accumulation, and hardware targets disagree. An optional **legacy Scalagen fidelity profile** is an alternative only if a separate compatibility scope is adopted and a pinned original execution contract can be stated. The default migration should instead list deliberate numeric/control divergences under the coherent Python profile above; this study does not require a second compiler contract. Do not describe the legacy profile as a single hardware parity guarantee. A full compatibility requirement remains an explicit adoption question, rather than an excuse to make core numeric behavior depend on unstated target/compiler options.

## Alternatives and reasons

| Alternative | Benefit | Why it is not the primary recommendation |
|---|---|---|
| Native Python int/float plus cast at stores | compact host execution | misses intermediate overflow/rounding, arbitrary custom float widths, signed zero/NaN policies, and preserved literal trees |
| Exact clone of the original Scalagen/emul code | direct legacy expectation reproduction within a pinned path | preserves source-form bugs and still does not establish original hardware behavior; useful as a separate oracle/profile |
| Inherit the Rust-v1 numeric and purity contract | existing historical prose and tests to consult | that contract is a redesign, not original language authority; each desired rule must be adopted independently |
| Widen all intermediates and round only once | more accurate mathematical sums/products | changes declared fixed arithmetic, overflow, FMA, and reduction answers; offer explicit widened accumulate operations later |
| Permit arbitrary reduction lambda and let `par` choose the tree | resembles original flexibility | makes numeric results tuning-dependent without an explicit semantic tree |
| Strict ordered fold for every reduction | deterministic for every combine | prevents lawful reassociation and does not reproduce original grouped arbitrary-lambda reductions; three explicit meanings retain both capabilities |
| Fixed overflow traps by default | catches unintended overflow | changes the accelerator's wrapping arithmetic; explicit checked operators retain the diagnostic choice without changing existing modular algorithms |

## Executed arithmetic probe

The following exact-rational/integer probe was executed on 2026-09-30 with local Python. It creates no compiler module. It tests arithmetic claims and the proposed distinctions, not source capture, Python Spatial APIs, original Scala execution, HLS, or hardware. The helper `normal_quant` covers finite normal values and the zero results in these cases; it is **not** a complete float implementation. The old normal tie formula and scalar unrolling formulas are source-derived translations, not independent Scala observations.

```python
from fractions import Fraction as Q
from itertools import product


def wrap(x, w):
    x %= 1 << w
    return x - (1 << w) if x >= (1 << (w - 1)) else x


def trunc(x):
    return x.numerator // x.denominator if x >= 0 else -((-x.numerator) // x.denominator)


def mul(a, b, w, f):
    return wrap((a * b) // (1 << f), w)


def div(a, b, w, f):
    return wrap(trunc(Q(a * (1 << f), b)), w)


def even(x):
    lo = x.numerator // x.denominator
    r = x - lo
    return lo + (r > Q(1, 2) or (r == Q(1, 2) and lo % 2 == 1))


def normal_quant(x, p):
    if x == 0:
        return Q(0)
    s = -1 if x < 0 else 1
    x = abs(x)
    e = 0
    while x < 1:
        x *= 2
        e -= 1
    while x >= 2:
        x /= 2
        e += 1
    return s * Q(even(x * (1 << (p - 1))), 1 << (p - 1)) * Q(2) ** e


w, f = 4, 1
left = mul(mul(1, 1, w, f), 4, w, f)
right = mul(1, mul(1, 4, w, f), w, f)
print("fixed_mul_associativity", Q(left, 2), Q(right, 2))
print("fixed_negative_mul_div", Q(mul(-1, 1, w, f), 2), Q(div(-3, 4, w, f), 2))
print("integer_wrap", wrap(2147483647 + 1, 32), wrap(-(-2147483648), 32), wrap((-2147483648) // -1, 32))
print("division_constant_shift", trunc(Q(-3, 2)), -3 >> 1)
print("literal_and_cast_negative", trunc(Q(-3, 4) * 2), (-3) >> 1)
print("signed_mod_original_and_proposed", -1 + (-2), (-3) % (-2))
print("normal_tie_old_and_rne", Q((1 + 1) >> 1, 4) + 1, normal_quant(Q(9, 8), 3))
print("float_reassociation", normal_quant(normal_quant(Q(2) ** 24 + 1, 24) - Q(2) ** 24, 24), normal_quant(Q(2) ** 24 + normal_quant(1 - Q(2) ** 24, 24), 24))
a = Q(1) + Q(1, 1 << 23)
b = Q(1) - Q(1, 1 << 23)
print("float_fma", normal_quant(normal_quant(a * b, 24) - 1, 24), normal_quant(a * b - 1, 24))
count = 0
for w in range(1, 7):
    for f in range(w + 1):
        rs = range(-(1 << (w - 1)), 1 << (w - 1))
        for a, b, c in product(rs, repeat=3):
            assert wrap(mul(a, b, w, f) + c, w) == wrap((a * b + c * (1 << f)) // (1 << f), w)
            count += 1
print("same_format_wrap_floor_fma_exhaustive_cases", count)


def tree(xs, op):
    if not xs:
        raise ValueError("empty")
    while len(xs) > 1:
        xs = [op(xs[i], xs[i + 1]) for i in range(0, len(xs) - 1, 2)] + ([xs[-1]] if len(xs) % 2 else [])
    return xs[0]


print("scalar_fold_unroll", tree([10, 1, 2], lambda a, b: a - b), 2 - (1 - 10), 10 - 1 - 2)
print("seed_vs_identity", tree([1, 2, 3, 4], lambda a, b: a + b), 10 + sum([1, 2, 3, 4]))
```

Observed output:

```text
fixed_mul_associativity 0 1/2
fixed_negative_mul_div -1/2 -1/2
integer_wrap -2147483648 -2147483648 -2147483648
division_constant_shift -1 -2
literal_and_cast_negative -1 -2
signed_mod_original_and_proposed -3 -1
normal_tie_old_and_rne 5/4 1
float_reassociation 0 1
float_fma 0 -1/70368744177664
same_format_wrap_floor_fma_exhaustive_cases 2054352
scalar_fold_unroll 7 11 7
seed_vs_identity 10 20
```

The fixed multiplication example is `(0.5*0.5)*2 = 0`, versus `0.5*(0.5*2)=0.5`, in signed W=4,F=1. It refutes the original node's universal fixed-multiplication associativity annotation. The Float32 example uses exact inputs `1+2^-23` and `1-2^-23`; two-rounding multiply/add gives zero, while fused gives `-2^-46`. The exhaustive fixed-FMA check covers 2,054,352 signed raw triples at W=1..6,F=0..W; the algebraic proof, not this finite enumeration alone, supports arbitrary widths.

## Compiler architecture consequences and full-domain roadmap

These are **proposed architectural requirements**, not production module names.

Typed numeric descriptors must include family/format; each operation must carry output type, rounding, overflow, special-value policy, and provenance. A checked reduction carries combination order/tree, identity/seed distinction, destination-state policy, contribution effects, and algebraic permissions. None can be recovered safely from an already evaluated Python result. Both frontends in PY-R001 must produce the same typed contract before simulation or lowering.

Use a pure Python semantic arithmetic layer for typed constant evaluation and reference simulation. Fixed arithmetic uses Python integers, rational ingress, and explicit normalization; floats use bit decoding and exact integer/rational quantization. Program values remain tagged typed values; host int/float operators do not become the semantic authority. A Python simulator interprets the checked operations and effect trace. Frontend construction, constant folding, simulation, and backend verification all record the same numeric-profile version.

Sharing constant/simulation arithmetic prevents one important class of divergence, but does not prove correctness. Validate against independent hand calculations, exhaustive small formats, independently structured rational calculations, and standard-format external oracle data. SoftFloat would be a differential oracle for validation, not a C/Rust core of the compiler. The current probe does not measure compilation or simulation performance; later absolute-time tests must state workloads and limits. Format/resource limits must report explicit capability/resource diagnostics without silently reducing width or using host Double.

| Roadmap stage | Scope to define and validate | Completion evidence before claiming support |
|---|---|---|
| A. Common descriptor and exact fixed family | Bool, signed/unsigned widths, I/F parameters, >64-bit cases, raw bits, ingress, all fixed operators/casts, wrap/saturate/checked modes | independent expected values, exhaustive small formats, wide boundary cases, constant/runtime parity, fault spans |
| B. Controller arithmetic | ordered fold, associative reduce, deterministic tree, scalar/memory initialization, singleton/empty/disabled/tails, effectful contributions | value and effect traces under multiple scheduling annotations; no hidden change of tree |
| C. Generic binary floating core | F16/F32/F64/BF16 and small custom descriptors, every finite/special encoding, casts, arithmetic, comparisons, signed zeros, subnormals, FMA, remainder operations | exhaustive small formats and standard-format oracle vectors; no assumption that native host arithmetic covers the domain |
| D. Math/random extensions | correctly rounded sqrt; explicit power order; RNG/stochastic profile; per-intrinsic approximation contracts | adopted profile/version, reproducible streams, domain/boundary tests, declared error bounds, source diagnostics |
| E. Hardware/HLS profiles | target format limits, primitive rounding/overflow/subnormal/FMA support, saturation/conversion paths, numeric ABI/serialization | generated-code validation, vendor simulation/synthesis separately, backend-specific compatibility evidence |

These stages are a dependency roadmap across the full numeric domain, not an Int32-only language definition or approval to implement stage A immediately. A stage may report partial support per operation/format while the semantic descriptor remains general. Unsupported formats/operations must fail at a defined checking stage.

## Proposed rules to distill after review

1. Typed operations normalize at every step; fixed format includes sign/width/fraction, float format includes precision/exponent, and large widths remain semantically meaningful.
2. Exact token/rational ingress and contextual literal trees survive both frontends; fixed floor and float nearest-even are declared quantization rules. No pre-evaluated host value is silently treated as an unevaluated DSL tree.
3. Wrapping, saturating, checked, division/remainder, shifts, numeric casts, and bit reinterpretation have distinct rules. Active numeric faults identify the original operation and inputs; float NaN/Inf remain specified values.
4. FMA and ordinary multiply/add are distinct. Algebraic rewrites require a proof for the actual format and modes; fixed fractional multiply and floating add do not receive generic associativity permission.
5. Ordered fold includes its seed once; associative reduce uses a proved typed identity; tree_reduce fixes grouping for arbitrary numeric combination. Contribution effects retain their explicit ordered exactly-once semantics independently of pure numeric regrouping.
6. Empty enabled invocations follow identity/seed/domain-error rules; disabled controllers perform no invocation. Previous destination state is included only by an explicit fold_into contract.
7. Legacy behavior is evidence; a named pinned fidelity profile is optional and needs separately adopted scope. Its source-path discrepancies are not implicit default policies for new Python programs.

## Unresolved evidence limitations

- No original Scala program, complete emul build, HLS simulation, synthesis, or board run was executed. Source calculations about overload dispatch, constant/runtime differences, special-value equality, and empty full-unroll paths still need direct original harnesses.
- Static/full-unroll empty results, negative-step full-unroll validity, outer-dimension invalid lanes, and `ignoreParEdgeCases` require configuration-specific original traces. The inspected source comments are a reason to test, not a completed proof.
- The fixed FMA precision-divergence claim in the original spec is not supported by the inspected fixed Math implementation. Numerical equality for same-format wrap/floor is proved here, but target multiplier/converter implementations and specialized accumulator RTL have not been validated.
- Float hardware behavior depends on target IP/configuration. BigIPSim's explicit and omitted rounding assignments do not establish all-target parity. Vendor FP format limits, flush behavior, FFma precision, and status outputs remain HLS dependencies.
- A complete special-value/exception-status table, especially signaling NaNs, min/max, FMA, conversion, and remainder, must become a reviewable Python specification. This note selects the policy but does not claim full IEEE compliance.
- RNG algorithm/version and approximation profiles for nonalgebraic intrinsics remain adoption dependencies. The design can represent them and diagnose unavailable profiles; seed reproducibility and bit-exact transcendental results are not established by the probe.
- The required extent of old-program compatibility remains a user/design decision. Ordered fold deliberately changes arbitrary-lambda legacy Fold answers; explicit original tree/init metadata is necessary if that behavior must be preserved.

## Acceptance cases

All entries are **proposed expected behavior**, except rows explicitly linked to observed arithmetic probe output. None is an accepted Python Spatial test or original end-to-end result. `T(...)` means contextual numeric ingress; it is illustrative notation.

| ID | Case | Expected result or diagnostic | Discriminates |
|---|---|---|---|
| N01 | Int32 max + 1; negate Int32 min; Int32 min / -1 | each yields Int32 min under wrap; checked forms fault | per-operation wrap, overflow modes; arithmetic probe observed |
| N02 | UInt8 `255+1`; signed Int128 `(2^127-1)+1` | `0`; `-2^127` | unsigned/wide support, no host-width truncation |
| N03 | Signed literal `-2147483648`; bare positive `2147483648` | accepted Int32 min; range diagnostic unless wider annotation | signed token handling |
| N04 | UInt8 `-1`, Bool used as numeric, mixed typed I16/I32 add | ingress/type diagnostics at offending token/operand | no accidental host coercion/promotion |
| N05 | `Fix(True,4,1)` contextual `0.75*2` | `1.0`; host-first `1.5` is a different program | contextual tree/per-literal quantization |
| N06 | `Fix(True,4,1)` literal `-0.75`, cast exact F=2 `-0.75` | both `-1.0` under proposed floor; explicit toward-zero cast gives `-0.5` | revised consistent fixed rescale |
| N07 | W=4,F=1 multiply grouping `(0.5*0.5)*2` versus `0.5*(0.5*2)` | `0` versus `0.5`; generic associative product rejected | probe observed fractional nonassociativity |
| N08 | Int32 runtime `-3/2`, both constants, or constant denominator optimization | always `-1`; signed shift substitution rejected without proof | fixes legacy constant/runtime disagreement; probe observed formula difference |
| N09 | four signed Int operand pairs and fractional -1.5/2 cases in the quotient table above | `/`, `//`, `%`, rem exactly match the listed values and paired raw equations | no hidden quotient/remainder mismatch |
| N10 | fixed `/0` in active contribution; same inactive branch/tail | source-aware numeric fault; inactive arithmetic/effects not evaluated | no invalid numeric sentinel leaking into live output |
| N11 | fixed `floor(-0.5)`, `ceil(-0.5)` | `-1`, `0` | revises double-adjustment helper |
| N12 | cast F=2 `1.5` to F=1 under saturation, constant/runtime | raw `3`, value `1.5` on both paths | rescale before clip |
| N13 | UInt8 `1<<8`; Int8 `-1>>8`; logical shift of Int8 -1 by 8; negative shift | `0`; `-1`; `0`; shift diagnostic | width-boundary and negative-shift semantics |
| N14 | custom Flt(P=3,E=3) ingress `1.125`, `1.375` | `1.0`, `1.5` | even/odd retained-significand tie; first probe observed |
| N15 | F32 minimum subnormal `2^-149`, half `2^-150`, three-halves `3*2^-150` | bits `0x00000001`, `0x00000000`, `0x00000002` | gradual underflow and tie-even; calculated, unexecuted |
| N16 | F32 finite max times 2; negative tiny value rounded to zero | +Inf with overflow; -0 with underflow/inexact where applicable | carry/range/sign rules |
| N17 | F32 `-0 == +0`, `NaN == NaN`, `NaN != NaN`, `-Inf < 1`, `-0 + -0` | true, false, true, true, -0 | revised original special-value paths |
| N18 | F32 `1/+0`, `-1/+0`, `0/0`; float-to-fixed NaN conversion | +Inf, -Inf, NaN with status; conversion fault | float specials distinct from fixed zero divisor |
| N19 | F32 `(2^24+1)-2^24` versus `2^24+(1-2^24)` | `0` versus `1`; generic associative sum rejected | probe observed float reassociation |
| N20 | F32 `(1+2^-23)*(1-2^-23)-1` versus explicit fma | `0` versus `-2^-46` | probe observed FMA distinction |
| N21 | same-format wrap/floor fixed FMA versus multiply/add | equal for all values under the proved contract; saturation/mixed-format requires separate proof | algebraic proof plus 2,054,352 probe cases |
| N22 | F16/F32/F64/BF16 and custom float bits round-trip, including NaN payload/-0 | identical bits under reinterpretation; arithmetic NaNs canonicalize | family breadth and bit/numeric distinction |
| N23 | source decimal `0.1` versus explicit already-evaluated binary-float ingress | both provenance classes preserved; no invented source token | frontend ingress contract |
| R01 | mapped `[1,2,3,4]`, sum identity 0 versus ordered fold seed 10 | `10` versus `20` | probe observed identity/seed distinction |
| R02 | ordered fold seed 10, values `[1,2]`, subtraction | `7` for every permitted schedule; cannot replace with legacy groups yielding `11` | redesign versus source compatibility |
| R03 | associative sum/product and explicit tree across several `par` factors | identical bits under the declared policy; unsupported concurrency diagnostic | schedule cannot choose numeric meaning |
| R04 | empty sum with identity 0; empty fold seed 10; empty tree without identity | `0`; `10`; static diagnostic/runtime domain fault | explicit empty behavior |
| R05 | Reduce destination initialized 99, enabled empty identity-0 invocation versus disabled controller | write 0 versus preserve 99 with no invocation | empty versus disabled/state |
| R06 | memory fold_into initial cells `[10,20]`, contributions `[1,2]` then `[3,4]` | cells `[14,26]`; empty map preserves old cells, empty destination touches none | memory seed and dual-domain emptiness |
| R07 | singleton no-identity tree; identity-free dynamic zero count | sole input without combining; domain fault | no register-reset-as-identity |
| R08 | tail lanes/all-false contribution filter with effectful FIFO map | active contributions run once; inactive lanes consume nothing; declared empty result | contribution validity separate from arithmetic validity |
| R09 | effectful contributions with pure associative add, requested conflicting parallel effects | effect trace preserved for a proved schedule; otherwise diagnostic | no purity ban on all contributions/no silent serialization |
| R10 | non-neutral supplied sum identity 10 for regroupable reduce | identity-law diagnostic; use seed 10 in fold or named empty_result in a tree | identity cannot be arbitrary init |
| R11 | initializer with an effect under disabled/enabled empty invocation | zero executions/one execution, respectively | invocation/effect contract |
| R12 | stochastic negative raw -1.25 under an adopted stream | only adjacent -2/-1 with declared probabilities; reproducible stream trace | correct negative rounding and explicit RNG effect |

## Next dependencies

The integrating reviewer should independently reopen the citations behind width interpretation, scalar fold options/overloads, first-group accumulation, float tie rounding, saturating cast rescaling, and fixed FMA before adopting rules. During this study the manager independently verified scalar fields/overloads/unrolling and generic FMA sources, then added dated corrections to [[60 - Reduction and Accumulation]] and [[60 - Counters and Primitives]]; see [[02 - Python Research Review Log]]. The earlier scalar Boolean/fixed Chisel precision assertions are therefore historical corrected text, not present findings against the corrected note. Further correction targets remain in `10 - Spec/50 - Code Generation/20 - Scalagen/20 - Numeric Reference Semantics.md`: line 66 called the normal formula round-to-even; lines 72 and 78 overgeneralized subnormal flushing and float-to-fixed clipping when inspected. This study itself edits only PY-R002 and leaves frozen historical decision/experiment artifacts unchanged.

The next semantic study must settle controller invocation, effect ordering, accumulator ownership, and runtime-domain faults with these numeric meanings. PY-R001 then needs matched overflow/rounding/reduction examples and diagnostics for both source capture and builder forms. Compiler architecture must retain exact literal tokens and numeric operation attributes, and the validation plan must turn the acceptance rows into independently computed cases before production implementation is approved. Later HLS research checks target capabilities against this contract, preserving explicit tree/rounding/FMA behavior or rejecting a lowering that cannot do so.
