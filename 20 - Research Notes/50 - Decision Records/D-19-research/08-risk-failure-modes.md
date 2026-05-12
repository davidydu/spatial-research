---
type: "research"
decision: "D-19"
angle: 8
topic: "risk-failure-modes"
---

# Risk and Failure Modes for FMA Policy

## Decision Risk Frame

[[D-19]] chooses whether Rust+HLS treats FMA-shaped IR as Scalagen-compatible multiply-then-add or as fused hardware/HLS multiply-add. The risky part is that the compiler already rewrites source `a*b+c` into `FixFMA`/`FltFMA` by default: `fuseAsFMA` starts true, `RewriteAnalyzer` marks only hardware add-of-mul patterns, and `RewriteTransformer` creates the FMA nodes when the cycle/specialization test passes (`/Users/david/Documents/David_code/spatial/src/spatial/SpatialConfig.scala:75-76`; `/Users/david/Documents/David_code/spatial/src/spatial/traversal/RewriteAnalyzer.scala:42-58`; `/Users/david/Documents/David_code/spatial/src/spatial/transform/RewriteTransformer.scala:263-274`). So the failure mode is not just "which spelling should codegen print"; it is silent numeric divergence after a legal optimization.

## Scalagen-Unfused Reference

The Scalagen-unfused policy is the safest replay oracle. Scalagen emits both `FixFMA` and `FltFMA` as ordinary `($m1 * $m2) + $add`, while `RegAccumFMA` emits `m0*m1` on the first iteration and `m0*m1 + reg.value` later (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/scalagen/ScalaGenFixPt.scala:150`; `/Users/david/Documents/David_code/spatial/src/spatial/codegen/scalagen/ScalaGenFltPt.scala:120`; `/Users/david/Documents/David_code/spatial/src/spatial/codegen/scalagen/ScalaGenReg.scala:57-64`). That preserves two fixed-point clamp/truncation points and two float reclamp points because `FixedPoint.*`, `FixedPoint.+`, `FloatPoint.*`, and `FloatPoint.+` each call their ordinary clamp paths (`/Users/david/Documents/David_code/spatial/emul/src/emul/FixedPoint.scala:14-16`; `/Users/david/Documents/David_code/spatial/emul/src/emul/FloatPoint.scala:153-157`; `/Users/david/Documents/David_code/spatial/emul/src/emul/FloatPoint.scala:417-433`).

Its main risk is hardware mismatch. To keep unfused parity in HLS, the backend must defeat contraction and prove the multiply result is rounded or packed before the add. If a tool contracts `a*b+c` anyway, the run can still look numerically close while failing bit parity. Unfused is also the more pessimistic area/II stance: the Zynq table prices `FltMul` at 8 cycles and `FltAdd` at 12, versus `FltFMA` at 19, and reductions duplicate reduction bodies and delay trees across parallel lanes (`/Users/david/Documents/David_code/spatial/resources/models/Zynq_Latency.csv:103-126`; `/Users/david/Documents/David_code/spatial/src/spatial/dse/DSEAreaAnalyzer.scala:164-190`). See [[06-hls-toolchain-support-cost]].

## Fused-HLS Reference

The fused-HLS policy is attractive because it matches current hardware intent for float FMA. ChiselGen lowers `FltFMA` through `Math.fma`; Fringe delegates that to `globals.bigIP.ffma`; Zynq implements `ffma` with an `FFma` module and Xilinx IP configured as `Operation_Type {FMA}` with latency 19 and rate 1 (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/chiselgen/ChiselGenMath.scala:50-51`; `/Users/david/Documents/David_code/spatial/fringe/src/fringe/templates/math/Math.scala:671-677`; `/Users/david/Documents/David_code/spatial/fringe/src/fringe/targets/zynq/BigIPZynq.scala:203-209`; `/Users/david/Documents/David_code/spatial/fringe/src/fringe/targets/zynq/ZynqBlackBoxes.scala:1217-1219`). It can improve schedule correlation, reduce one rounding/packing event, and sometimes help II.

The risk is semantic migration under a familiar name. Existing tests mostly prove that FMA-shaped programs pass, not which precision rule is canonical: scalar tests often compare against the same host expression, while GEMM, SPMV, and ML apps use tolerances or checksums that can hide one-ulp or cancellation differences. [[02-tests-apps-usage]] is the warning label here. Fused-HLS also crosses [[D-17]] and [[D-18]]: fusion changes where stochastic or fixed rounding events occur, and it changes `FloatPoint.clamp` from two opportunities to one. Any D-17 event identity or D-18 `float_pack_policy` becomes incomplete unless it records the FMA policy too. See [[04-precision-overlap-d17-d18]], [[D-17]], and [[D-18]].

Reductions magnify the risk. `AccumAnalyzer` recognizes `FixFMA(..., RegRead(reg))` and `FltFMA(..., RegRead(reg))`, then `AccumTransformer` turns those cycles into `RegAccumFMA` (`/Users/david/Documents/David_code/spatial/src/spatial/traversal/AccumAnalyzer.scala:187-210`; `/Users/david/Documents/David_code/spatial/src/spatial/transform/AccumTransformer.scala:110-120`). A one-operator precision change is therefore repeated across lanes, tree nodes, and loop-carried accumulator state.

## Dual-Mode and Capability Gates

Dual mode has the best risk profile but only if provenance is mandatory. The safe split is `fma_policy = scalagen_unfused_two_round_v1` for Rust reference goldens, `fma_policy = fused_single_round_v1` for an exact fused reference, and `fma_policy = backend_native_fma` for vendor/HLS behavior until bit-tested. The new failure mode is mode leakage: goldens produced in one mode, HLS artifacts in another, and mismatch tools that only report "float difference." Mitigation requires every simulator run, golden file, HLS report, and diagnostic to record requested policy, actual backend capability, contraction controls, fallback, D-17 rounding policy, and D-18 float pack policy. Tool-default contraction should be rejected as unauditable; unsupported exact policy should produce a diagnostic or a named fallback, not silent success. This matches the recommendation direction in [[10-recommendation-matrix]].
