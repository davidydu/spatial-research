---
type: spec
concept: BigIP and Arithmetic
source_files:
  - "fringe/src/fringe/BigIP.scala:6-105"
  - "fringe/src/fringe/targets/DeviceTarget.scala:10-31"
  - "fringe/src/fringe/targets/BigIPSim.scala:12-293"
  - "fringe/src/fringe/targets/zynq/BigIPZynq.scala:11-80"
  - "fringe/src/fringe/targets/aws/BigIPAWS.scala:1-5"
  - "fringe/src/fringe/targets/asic/BigIPASIC.scala:6-80"
  - "fringe/src/fringe/templates/math/Math.scala:9-820"
  - "fringe/src/fringe/templates/math/FixedPoint.scala:11-200"
  - "fringe/src/fringe/templates/math/FloatingPoint.scala:8-126"
  - "fringe/src/fringe/templates/math/Converter.scala:10-97"
  - "fringe/src/fringe/templates/math/RoundingMode.scala:3-8"
  - "fringe/src/fringe/templates/math/OverflowMode.scala:3-8"
  - "fringe/src/fringe/templates/hardfloat/MulAddRecFN.scala:2-80"
  - "fringe/src/fringe/templates/hardfloat/common.scala:2-80"
source_notes:
  - "[[fringe-and-targets]]"
hls_status: chisel-specific
hls_reason: "Arithmetic dispatch is target BigIP plus Chisel/HardFloat modules; HLS needs an explicit numeric library policy"
depends_on:
  - "[[40 - Hardware Templates]]"
  - "[[40 - Numeric Reference Semantics]]"
status: draft
---

# BigIP and Arithmetic

## Summary

Spatial's Chisel arithmetic path is mediated by `BigIP`, an abstract target-specific provider of arithmetic implementations. `DeviceTarget` keeps a lazy `BigIP` instance and exposes operation latency scalars used by the `Math` API (`fringe/src/fringe/targets/DeviceTarget.scala:10-31`). The generated hardware does not call target black boxes directly in most cases; it calls `fringe.templates.math.Math`, and `Math` dispatches multiply, divide, modulo, floating-point arithmetic, conversions, and some fixed-point casts through `globals.bigIP` with target-derived or caller-provided latency (`fringe/src/fringe/templates/math/Math.scala:9-50`, `fringe/src/fringe/templates/math/Math.scala:548-620`).

## BigIP contract

`BigIP` requires unsigned and signed divide, modulo, multiply, floating add/sub/mul/div, floating comparisons, and equality/inequality implementations (`fringe/src/fringe/BigIP.scala:15-61`). Many operations default to throwing `Unimplemented`, including integer sqrt, trig/hyperbolic functions, log2, floating abs/exp/tanh/sigmoid/log/reciprocal/sqrt/rsqrt/FMA, fixed/floating conversions, and floating accumulation (`fringe/src/fringe/BigIP.scala:22-105`). The helper `getConst` detects literal `UInt` or `SInt` operands so target implementations can constant-fold or choose cheaper paths (`fringe/src/fringe/BigIP.scala:9-13`).

`BigIPSim` is the simulation baseline. It implements integer divide/mod with Chisel arithmetic and optional retiming, constant-optimizes multiplications, implements log2/sqrt through simulation black boxes, leaves fixed-point trig/hyperbolic methods as TODO pass-throughs, and implements floating add/sub/mul/div/comparisons with Berkeley HardFloat modules (`fringe/src/fringe/targets/BigIPSim.scala:12-75`, `fringe/src/fringe/targets/BigIPSim.scala:77-134`, `fringe/src/fringe/targets/BigIPSim.scala:136-235`). It implements `fix2fix` with a hardware `fix2fixBox` for non-literals; for literals it performs Scala-side rounding/saturation and uses `scala.math.random` for unbiased rounding salt, with a comment saying mistakes are likely (`fringe/src/fringe/targets/BigIPSim.scala:237-273`). It maps fixed-to-float and float-to-fixed through HardFloat conversion modules (`fringe/src/fringe/targets/BigIPSim.scala:275-292`).

Zynq-like targets use `BigIPZynq`, which mirrors the simulation structure but instantiates target black boxes for non-constant divide, modulo, and multiply, naming modules with `suggestName(myName)` (`fringe/src/fringe/targets/zynq/BigIPZynq.scala:11-80`). AWS F1 simply subclasses `BigIPZynq` (`fringe/src/fringe/targets/aws/BigIPAWS.scala:1-5`). ASIC uses `BigIPASIC`, which instantiates ASIC black boxes for non-constant divide/mod/multiply and comments that constant divisors use combinational Verilog and ignore latency (`fringe/src/fringe/targets/asic/BigIPASIC.scala:6-80`). Several targets are thin aliases over `BigIPSim` or Zynq-style implementations, so the semantics are target-family rather than board-specific.

## Fixed-point and floating-point APIs

`Math` states its design intent directly: it should not define implementations, but should rely on `BigIP` so hardware targets can customize operations under a common API (`fringe/src/fringe/templates/math/Math.scala:9-13`). Unsigned and signed integer multiply/divide/modulo compute default latency from `globals.target.fixmul_latency`, `fixdiv_latency`, or `fixmod_latency` times operand width when no delay is supplied (`fringe/src/fringe/templates/math/Math.scala:19-50`). Fixed-point operations build wrapper modules for add/sub/mul/div/mod, upcast operands, dispatch primitive arithmetic, and downcast through `fix2fixBox` with rounding and overflow modes (`fringe/src/fringe/templates/math/Math.scala:118-373`). Multiplication uses target latency only when retiming is enabled or an explicit delay exists; otherwise it can use `0.0` latency (`fringe/src/fringe/templates/math/Math.scala:200-260`). Division includes a TODO that the denominator is not upcast in one path, and modulo has a TODO that no upcasting actually occurs (`fringe/src/fringe/templates/math/Math.scala:271-337`).

`FixedPoint` is a Chisel `Bundle` with sign/decimal/fraction widths, optional literal value, raw/decimal/fraction accessors, arithmetic operator overloads, comparison overloads, bitwise overloads, and conversion helpers (`fringe/src/fringe/templates/math/FixedPoint.scala:11-160`). Its companion builds fixed-point wires from Bool, UInt, SInt, Int, Double, or BigInt literals (`fringe/src/fringe/templates/math/FixedPoint.scala:163-200`). `FloatingPoint` similarly wraps a recoded-style bit vector, delegates arithmetic and comparisons to `Math`, throws for cast, and converts literal Float/Double values through the emulator bit encoder (`fringe/src/fringe/templates/math/FloatingPoint.scala:8-126`).

Conversion and rounding behavior is split between `Math`, `BigIP`, and `fix2fixBox`. `Math.fix2flt`, `fix2fix`, `flt2fix`, and `flt2flt` wrap their arguments in Chisel modules and dispatch to `globals.bigIP`, with fractional fixed-to-float and float-to-fixed conversions implemented by multiplying or dividing by powers of two around the BigIP conversion (`fringe/src/fringe/templates/math/Math.scala:680-799`). `fix2fixBox` implements bit shaving/extension, stochastic unbiased rounding through `PRNG`, wrapping versus saturating overflow, and retimed output assembly (`fringe/src/fringe/templates/math/Converter.scala:10-97`). The mode vocabulary is tiny: `Truncate` or `Unbiased` for rounding, and `Wrapping` or `Saturating` for overflow (`fringe/src/fringe/templates/math/RoundingMode.scala:3-8`, `fringe/src/fringe/templates/math/OverflowMode.scala:3-8`).

## HardFloat

The `fringe.templates.hardfloat` directory is not Spatial-specific arithmetic code. Representative files begin with the Berkeley HardFloat notice, identifying the package as a pre-release HardFloat IEEE floating-point arithmetic package by John R. Hauser with contributions from Yunsup Lee and Andrew Waterman (`fringe/src/fringe/templates/hardfloat/MulAddRecFN.scala:2-36`, `fringe/src/fringe/templates/hardfloat/common.scala:2-36`). Spatial uses modules such as `MulAddRecFN`, `DivSqrtRecFN_small`, `CompareRecFN`, `INToRecFN`, and `RecFNToIN` from that library through `BigIPSim` and related targets (`fringe/src/fringe/targets/BigIPSim.scala:125-292`). The spec should treat HardFloat as an imported library, not as behavior to rewrite line-by-line.

## HLS notes

The HLS rewrite needs a numeric policy: which operations use C/Rust operators, which use vendor HLS IP, which use an external HardFloat-equivalent library, and whether Chisel fused FMA or Scala reference unfused behavior is the source of truth. It should preserve target-dependent latency metadata only if HLS scheduling needs it. Current TODO pass-throughs for transcendental functions and questionable literal unbiased rounding should be resolved before calling the arithmetic layer a portable reference.

## Open questions

- [[open-questions-fringe-targets#Q-ft-11 - 2026-04-25 BigIP optional arithmetic behavior|Q-ft-11]]
- [[open-questions-scalagen#Q-scal-01 - 2026-04-24 Scalagen FMA precision divergence|Q-scal-01]]
