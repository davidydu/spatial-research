---
type: "research"
decision: "D-18"
angle: 6
---

# Cleaner Algorithm Candidates for Custom-Float Packing

## Current Clamp Target [source]

Spatial's Scala float contract is not just "IEEE-like." `FloatPoint.bits` delegates every finite nonzero `Value` to `FloatPoint.clamp`, then emits mantissa bits, exponent bits, and sign as low-to-high arrays (`emul/src/emul/FloatPoint.scala:120-126`). The format object defines `sbits`, `ebits`, `bias`, `MIN_E`, `MAX_E`, and `SUB_E`; these constants control normal, subnormal, overflow, and underflow cutoffs (`emul/src/emul/FltFormat.scala:3-8`). Clamp estimates `y = floor(log2(abs(value)))`, computes `x = abs(value) / 2^y`, patches a few boundary cases, then chooses inf, normal, subnormal, or signed zero (`emul/src/emul/FloatPoint.scala:318-398`). Normal packing forms `mantissaP1 = ((x - 1) * 2^(sbits + 1)).toBigInt`, rounds by adding one when bit 0 is set, then shifts; subnormal packing shifts a scaled mantissa and rounds from the discarded bit (`emul/src/emul/FloatPoint.scala:361-387`). `clamped` immediately converts the packed result back to a rounded `FloatValue`, so arithmetic results are reclamped after every op (`emul/src/emul/FloatPoint.scala:153-157`, `emul/src/emul/FloatPoint.scala:417-433`). Scalagen preserves that path by remapping float types to `FloatPoint` and emitting `toFloatPoint` / `toFixedPoint` conversions (`src/spatial/codegen/scalagen/ScalaGenFltPt.scala:12-14`, `src/spatial/codegen/scalagen/ScalaGenFltPt.scala:84-88`).

## Candidate 1: Bug-Compatible Clamp Clone [source + inference]

The only credible bit-for-bit reproduction is a compatibility clone of the current algorithm, including the approximate `log2BigDecimal` helper and boundary patches (`emul/src/emul/FloatPoint.scala:289-309`, `emul/src/emul/FloatPoint.scala:335-351`). This is not clean, but it is testable: feed decimal constants, operation results, subnormal edges, powers of two, NaN/Inf/zero strings, and compare packed bits against `FloatPoint.bits`. The compatibility cost is that it bakes in Scala `BigDecimal`, `toBigInt` truncation, one-guard-bit rounding, and the current signed-zero behavior. Notice the code's own zero path returns positive zero for numeric zero, while string parsing can preserve "-0.0" (`emul/src/emul/FloatPoint.scala:278-284`, `emul/src/emul/FloatPoint.scala:320-322`). This candidate is the right escape hatch for Scalagen parity, not the best new semantic center.

## Candidate 2: Exact Normalization With Integer/BigDecimal Math [source + inference]

A cleaner packer would normalize exactly: represent finite input as sign plus exact decimal or rational magnitude, find exponent by exact comparisons against powers of two, compute a full scaled significand with guard/round/sticky bits, then encode normal/subnormal/overflow. It can intentionally emulate `clamp`'s half-up-ish behavior, but the moment it fixes `log2BigDecimal` estimation or uses sticky bits it may stop matching the legacy bits. Compared with Candidate 1, this is the best "clean custom float" implementation for a new reference library: deterministic, backend-independent, and easy to property-test against unpack/repack using `convertBackToValue` (`emul/src/emul/FloatPoint.scala:399-415`). It should still expose a mode flag because D-18 appears to care about both reproducibility and cleaner semantics.

## Candidate 3: IEEE-Like or MPFR Reference [source + unverified]

An IEEE-like packer means standard categories, exponent biasing, subnormals, and explicit rounding mode, probably round-to-nearest-even by default (unverified). It is conceptually aligned with the hardware side: Chisel `FloatingPoint` uses `m = sbits + 1`, `e = ebits`, and delegates arithmetic and conversions to `globals.bigIP` (`fringe/src/fringe/templates/math/FloatingPoint.scala:8-12`, `fringe/src/fringe/templates/math/Math.scala:548-678`). The simulator BigIP routes many ops through HardFloat-style `MulAddRecFN`, `DivSqrtRecFN_small`, `INToRecFN`, and `RecFNToIN`, with several conversion rounding modes hardcoded to `0.U` (`fringe/src/fringe/targets/BigIPSim.scala:125-173`, `fringe/src/fringe/targets/BigIPSim.scala:275-291`). MPFR could be an excellent oracle for host-side tests and arbitrary rounding modes (unverified), but it should be treated as a reference dependency, not as synthesizable HLS logic (unverified). Both options are cleaner than `clamp`, but they are semantic migrations unless proven against a generated corpus.

## Candidate 4: HLS-Native Conversions and Recommendation [source + inference]

HLS-native float/fixed conversion is the lowest implementation burden in generated C++ HLS: use vendor/native floating and fixed-point conversions where available (unverified). It also has the highest parity risk. Local Chisel already shows conversion policy drift: `FltToFix` emits `Math.flt2fix(..., Truncate, Wrapping, ...)`, while the BigIPSim implementation ignores those parameters and sends `roundingMode := 0.U` into `RecFNToIN` (`src/spatial/codegen/chiselgen/ChiselGenMath.scala:96-99`, `fringe/src/fringe/targets/BigIPSim.scala:285-291`). Fixed-point rounding has an explicit local stochastic `Unbiased` path using a PRNG in hardware (`fringe/src/fringe/templates/math/Converter.scala:37-44`; `fringe/src/fringe/templates/math/RoundingMode.scala:3-8`), but float packing does not expose an equivalent policy surface.

Recommendation: split the contract. Keep a bug-compatible `FloatPoint.clamp` reproduction only for "Scalagen parity / legacy replay" tests. Make exact integer normalization the clean custom-float packer for a portable reference. Allow IEEE/MPFR and HLS-native routes only behind named modes with provenance, because they are likely better engineering but not bit-for-bit reproduction (unverified).
