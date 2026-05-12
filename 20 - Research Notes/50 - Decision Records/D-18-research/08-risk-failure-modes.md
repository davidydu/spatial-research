---
type: "research"
decision: "D-18"
angle: 8
---

# Risk and Failure Modes for FloatPoint Clamp Policy

## Decision Risk Frame

D-18 asks whether Rust float packing must reproduce `FloatPoint.clamp` bit-for-bit, including the `x > 1.9` subnormal guard, or adopt a cleaner custom-float algorithm with accepted divergence (`20 - Research Notes/40 - Decision Queue.md:79-81`). This is a [[20 - Numeric Reference Semantics]] and [[50 - Data Types]] risk because Scalagen maps every `FltPtType` to `FloatPoint`, emits `toFloatPoint`, `FloatPoint(...)`, and `FloatPoint.random`, and uses `.bits` / `FloatPoint.fromBits` for reinterpretation (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/scalagen/ScalaGenFltPt.scala:12-14`, `:84-102`; `/Users/david/Documents/David_code/spatial/src/spatial/codegen/scalagen/ScalaGenBits.scala:47-55`). The silent-failure mode is small: numerical tests pass, but packed mantissa/exponent/sign bits differ.

## Legacy Bit-For-Bit Reproduction

The legacy option minimizes migration surprise. `FloatPoint.clamp` owns zero, overflow-to-infinity, normal packing, subnormal packing, and signed-zero underflow, then `clamped` converts packed bits back into stored `FloatValue` after finite arithmetic (`/Users/david/Documents/David_code/spatial/emul/src/emul/FloatPoint.scala:318-398`, `:417-433`). Reproducing it preserves existing golden traces and supports [[01-source-algorithm-call-surface]]. The cost is maintenance: Rust must copy the `log2BigDecimal` approximation, one-discarded-bit rounding, `x >= 2` and cutoff repair, and the unexplained `x > 1.9` rule (`FloatPoint.scala:289-309`, `:335-351`). Failure mode: implementers "clean up" a branch, pass ordinary float tests, and only diverge around smallest subnormal, maximum normal, and decimal strings near powers of two.

## Cleaner Algorithm

A cleaner packer, as in [[06-cleaner-algorithm-candidates]], is easier to explain: exact normalization, explicit guard/round/sticky policy, direct overflow and subnormal thresholds from `FltFormat` (`/Users/david/Documents/David_code/spatial/emul/src/emul/FltFormat.scala:3-8`). Its risk is not correctness in the abstract; it is unannounced semantic migration. Users may see changed behavior for `Half`, custom `FltPt[M,E]`, `to[FltPt]`, packed bit views, and float-to-fixed casts even when printed decimal values look close. The worst user-surprise cases are signed zero preservation, NaN canonical payloads, subnormal rescue versus zero, and overflow at the max-normal boundary, because those affect equality, bits, and downstream memory data, not just toleranced comparisons (`FloatPoint.scala:84-126`, `:435-455`).

## Dual-Mode Compatibility

Dual mode reduces political risk but increases testing and provenance burden. A `legacy_clamp` mode can be the default for replay and Scalagen parity; a `clean_custom_float` mode can serve new reference semantics. The failure mode is mode leakage: tests generate goldens in one mode, HLS reports another, and users cannot tell which oracle produced a result. Mitigation requires metadata on every numeric run, source-compatible fixture names, and tests that assert both modes intentionally diverge on boundary cases. [[03-tests-apps-usage]] found that current tests do not directly call `FloatPoint.clamp`, `bits`, `fromBits`, or `isSubnormal`; D-18 therefore needs exact fixtures for NaN, +/- infinity, negative zero, min subnormal, underflow to signed zero, max normal to infinity, and the `x > 1.9` band.

## HLS and Native Approximation Risk

HLS/native approximations are useful implementation paths, not safe reference policies. Cppgen maps custom `FltPtType(g,e)` to native `float` and casts float/fix conversions directly, with no `FltFormat` or clamp model (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenCommon.scala:75-93`; `/Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenMath.scala:136-138`). Chisel/Fringe preserve custom widths but delegate runtime arithmetic and conversions to `Math.*` / `BigIP` hooks, while literal packing may still call emul bits (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/chiselgen/ChiselGenMath.scala:51-56`, `:92-102`; `/Users/david/Documents/David_code/spatial/fringe/src/fringe/templates/math/FloatingPoint.scala:91-124`). BigIPSim then uses recFN modules and hardcoded rounding-mode fields in several conversions (`/Users/david/Documents/David_code/spatial/fringe/src/fringe/targets/BigIPSim.scala:125-173`, `:275-291`). Using this as the default risks silent backend-specific divergence. Recommendation: choose dual-mode only if provenance is mandatory; otherwise pick legacy for compatibility or clean for migration, but do not let native/HLS approximation masquerade as [[D-18]] bit parity.
