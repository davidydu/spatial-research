---
type: research
decision: D-10
angle: 6
title: HLS/hardware/BigIP implications for transcendental precision
date: 2026-04-27
---

# HLS/hardware/BigIP implications for transcendental precision

## 1. BigIP Is A Capability Boundary

`Math` says the arithmetic API should rely on target `BigIP` classes so hardware targets can customize implementations under a common API (`fringe/src/fringe/templates/math/Math.scala:9-12`). The abstract `BigIP` contract requires integer divide/mod/multiply and core floating add/sub/mul/div plus comparisons (`fringe/src/fringe/BigIP.scala:15-61`). Everything more transcendental-adjacent is optional by default: integer `sqrt`, fixed `sin/cos/atan/sinh/cosh`, `log2`, floating `fabs/fexp/ftanh/fsigmoid/fln/frec/fsqrt/frsqrt/ffma`, conversions, and `fltaccum` all throw `Unimplemented` unless a target overrides them (`fringe/src/fringe/BigIP.scala:22-104`). D-01 already frames this as a policy choice between rejecting, preserving placeholders, and lowering to vendor/HLS mechanisms (`20 - Research Notes/50 - Decision Records/D-01.md:13-21`).

## 2. Fixed-Point Reality

Fixed-point transcendental support is thin. `Math.sqrt(FixedPoint)` lowers to integer `bigIP.sqrt`, shifting around the binary point for fractional formats (`fringe/src/fringe/templates/math/Math.scala:59-72`). `Math.sin`, `cos`, `atan`, `sinh`, and `cosh` simply return the input with TODO comments before any target dispatch (`fringe/src/fringe/templates/math/Math.scala:74-88`). If the lower-level `BigIP` `UInt` methods are called directly, `BigIPSim` repeats that identity-pass-through pattern (`fringe/src/fringe/targets/BigIPSim.scala:82-96`), while hardware targets inherit the base throwing defaults unless they override them. Zynq/CXP do implement integer `sqrt` through `SquareRooter` (`fringe/src/fringe/targets/zynq/BigIPZynq.scala:90-95`; `fringe/src/fringe/targets/cxp/BigIPCXP.scala:90-95`), backed by Xilinx CORDIC Square_Root IP (`fringe/src/fringe/targets/zynq/ZynqBlackBoxes.scala:153-190`). ASIC does not override `sqrt` at all; `BigIPASIC` stops after core FP comparisons (`fringe/src/fringe/targets/asic/BigIPASIC.scala:75-143`).

## 3. Floating Support Splits By Family

Simulation is not a hardware precision oracle. `BigIPSim` implements `fsqrt` and `fdiv` with HardFloat `DivSqrtRecFN_small`, but validity, sqrt/div selection, rounding, and tininess settings are annotated TODO; rounding is hardwired to `0.U(3.W)` (`fringe/src/fringe/targets/BigIPSim.scala:125-134`, `fringe/src/fringe/targets/BigIPSim.scala:164-174`). It implements core add/sub/mul through `MulAddRecFN` and comparisons through `CompareRecFN` (`fringe/src/fringe/targets/BigIPSim.scala:136-235`), but does not override `fexp`, `fln`, `frec`, `frsqrt`, `ffma`, `ftanh`, or `fsigmoid`, so those still throw from `BigIP`.

Zynq and CXP are broader: they override `fabs`, `fexp`, `fln`, `fsqrt`, `frec`, `frsqrt`, `ffma`, conversions, and `fltaccum` (`fringe/src/fringe/targets/zynq/BigIPZynq.scala:168-272`; `fringe/src/fringe/targets/cxp/BigIPCXP.scala:168-272`). These are wrappers around Vivado `floating_point` IP. `FExp` and `FLog` emit Exponential and Logarithm IP, but the code selects `Half` only for 5/11 formats and otherwise selects `Single`, despite carrying custom width parameters (`fringe/src/fringe/targets/zynq/ZynqBlackBoxes.scala:262-287`, `fringe/src/fringe/targets/zynq/ZynqBlackBoxes.scala:313-337`). `FRec` and `FRSqrt` have the same half-or-single precision selection (`fringe/src/fringe/targets/zynq/ZynqBlackBoxes.scala:1090-1112`, `fringe/src/fringe/targets/zynq/ZynqBlackBoxes.scala:1139-1161`). `FSqrt` and `FFma` use custom precision IP (`fringe/src/fringe/targets/zynq/ZynqBlackBoxes.scala:364-386`, `fringe/src/fringe/targets/zynq/ZynqBlackBoxes.scala:1193-1219`). ASIC has black-box definitions for exp/log/sqrt, but `BigIPASIC` never wires them into overrides, so the target-level behavior is still throw for those ops (`fringe/src/fringe/targets/asic/ASICBlackBoxes.scala:142-230`; `fringe/src/fringe/targets/asic/BigIPASIC.scala:143`).

## 4. What HLS Matching Would Mean

Generic HLS math calls for `sqrt`, `exp`, `log`, `sin`, `cos`, `tanh`, `fma`, or reciprocal are plausible lowerings, but any statement that a vendor HLS tool will match Spatial's current IP bit-for-bit is `(unverified)`. The local evidence says matching synthesized hardware would mean matching the same capability table, the same IP family/version (`floating_point` v7.1, CORDIC v6.0), the same half/single/custom precision choices, and the same latency/enable protocol (`aclken`, `tvalid`, `TLAST` for accumulators) (`fringe/src/fringe/targets/zynq/ZynqBlackBoxes.scala:285-288`, `fringe/src/fringe/targets/zynq/ZynqBlackBoxes.scala:1270-1274`). For fixed casts, matching also means matching stochastic/unbiased rounding behavior: `fix2fixBox` adds PRNG low bits before shaving fractional bits (`fringe/src/fringe/templates/math/Converter.scala:32-44`).

## 5. D-10 Implications

D-10 should separate "operation available" from "precision-equivalent." A Rust/HLS port can reject unsupported defaults cleanly, as D-01 recommends for non-native or opt-in ops (`20 - Research Notes/50 - Decision Records/D-01.md:95-126`). For accepted transcendentals, the manifest should record whether the lowering is HardFloat-like, Vivado-IP-like, HLS-native `(unverified)`, or approximation. Otherwise `fexp/fln/frec/frsqrt` on custom float widths can silently become single-precision-ish on Zynq/CXP, while `sin/cos/atan/sinh/cosh` are either identity stubs in simulator paths or synthesis-time throws on hardware paths.
