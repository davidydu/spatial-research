---
type: "research"
decision: "D-19"
angle: 6
---

# HLS Toolchain Support and Cost for Fused vs Unfused FMA

## Local Baseline

[[D-19]] is a precision and toolchain decision, not only an optimization knob. Local source defaults `spatialConfig.fuseAsFMA = true`, and `RewriteAnalyzer` marks only hardware add-of-multiply patterns whose multiply has a safe consumer topology and matching reduce-cycle status (`src/spatial/SpatialConfig.scala:75-76`; `src/spatial/traversal/RewriteAnalyzer.scala:39-58`). `RewriteTransformer` then rewrites marked `FixAdd(FixMul, add)` and `FltAdd(FltMul, add)` into `FixFMA` or `FltFMA` (`src/spatial/transform/RewriteTransformer.scala:263-274`).

The reference side is different. Scalagen emits both `FixFMA` and `FltFMA` as `($m1 * $m2) + $add`, and Cppgen emits `a * b + c`, with no explicit `std::fma` call (`src/spatial/codegen/scalagen/ScalaGenFltPt.scala:120`; `src/spatial/codegen/scalagen/ScalaGenFixPt.scala:150`; `src/spatial/codegen/cppgen/CppGenMath.scala:34-36`). The `FloatPoint` emulator clamps after each `*` and after each `+`, so the local Scalagen-compatible float reference is unfused unless a new fused reference primitive is introduced (`emul/src/emul/FloatPoint.scala:153-157`, `emul/src/emul/FloatPoint.scala:417-433`). This links directly to [[20 - Numeric Reference Semantics]], [[50 - Data Types]], and [[D-18-research/07-hls-toolchain-implications]].

## Availability and Mapping

Floating fused FMA exists in current Chisel target plumbing, but not uniformly. `Math.fma` for `FloatingPoint` delegates to `globals.bigIP.ffma`; Zynq/CXP implement it with an `FFma` module, and the generated Xilinx floating-point IP is configured with `Operation_Type {FMA}`, `C_Mult_Usage {Full_Usage}`, `C_Latency {19}`, and `C_Rate {1}` (`fringe/src/fringe/templates/math/Math.scala:671-677`; `fringe/src/fringe/targets/zynq/BigIPZynq.scala:203-209`; `fringe/src/fringe/targets/zynq/ZynqBlackBoxes.scala:1217-1219`). `BigIPSim` implements float add/mul through HardFloat-style `MulAddRecFN`, but does not override `ffma`; Arria10 extends `BigIPSim`, so floating FMA availability is target-specific (`fringe/src/fringe/targets/BigIPSim.scala:136-162`; `fringe/src/fringe/targets/arria10/BigIPArria10.scala:1-6`).

Sourced vendor support is real but not identical to Spatial's old path. AMD Floating-Point Operator IP advertises fused multiply-add and configurable word length, latency, and implementation details.[^amd-fpo] Vitis HLS `bind_op` exposes floating add/mul/div/etc. with fabric and DSP-style implementations, but the listed `bind_op` operations do not name `fmadd`; FMA appears instead in the floats/doubles accumulation and multiply-add guidance.[^amd-bind][^amd-floats] Intel oneAPI documents floating-point contraction and says fast math enables double-precision FMA contraction by default; it also has local/global DSP preference controls for supported float add, subtract, and multiply operations.[^intel-fp][^intel-dsp]

## Latency, Area, and II

Local model costs already favor fused as a single scheduled operator for floating point: `FltMul` is 8 cycles, `FltAdd` is 12, and `FltFMA` is 19 in the Zynq latency table (`resources/models/Zynq_Latency.csv:103-126`). That is a small latency win over an unfused chain and preserves one operator identity for DSE/reporting. For fixed point, however, the local Chisel `Math.fma` wrapper computes a multiply plus retimed add, while the latency table prices `FixFMA` at the same `0.1875*b` as `FixMul`; treat that as a Spatial modeling convention, not proof of a true fixed-point fused primitive (`fringe/src/fringe/templates/math/Math.scala:843-868`; `resources/models/Zynq_Latency.csv:66-84`).

Vendor costs can move either direction. AMD says standard-precision accumulation/multiply-add is available across Versal and non-Versal devices, with II=1 on Versal and typically II 3-5 on non-Versal; its high-precision fused multiply-add is Versal-only, uses one extra precision bit, has a single final rounding, uses more resources than unfused multiply-add, and can cause C++/RTL cosim mismatches.[^amd-floats] Intel says double-precision contraction saves substantial FPGA area and improves performance/latency, but that is a sourced Intel compiler claim, not a Spatial report result.[^intel-fp] Exact area/II for D-19 still belongs in [[D-08]]-style report provenance.

## Disabling Contraction and Exact Emulation

To preserve unfused Scalagen parity, the HLS backend must force two rounding points: multiply result, then add result. Intel has direct controls: `#pragma clang fp contract(off)` prohibits fusing, and `-no-fma -fp-model=precise` restores GCC/older oneAPI-like precision behavior.[^intel-scope][^intel-fp] For AMD/Vitis, this pass found sourced controls for expression balancing and operator binding, but not a Vitis-specific guarantee that `#pragma STDC FP_CONTRACT OFF` prevents HLS FMA inference; mark that control path unverified until a report or RTL check proves it.[^amd-expr]

For fused exact reference, Rust `f32::mul_add` is a good native reference for IEEE `f32`: it guarantees the rounded infinite-precision fused result.[^rust-muladd] That does not automatically cover Spatial custom `FloatPoint`. Exact fused custom emulation would need full-precision product-plus-add followed by one clone of `FloatPoint.clamp`; exact unfused emulation needs a clamp after multiply and another after add. Any vendor-native HLS result should therefore be labelled `hls_native_fma` unless bit-tested against the Rust/Scala reference mode.

[^amd-fpo]: [AMD Floating-Point Operator IP](https://www.amd.com/en/products/adaptive-socs-and-fpgas/intellectual-property/floating_pt.html).
[^amd-bind]: [AMD Vitis HLS `bind_op`](https://docs.amd.com/r/2024.2-English/ug1399-vitis-hls/pragma-HLS-bind_op).
[^amd-floats]: [AMD Vitis HLS floats and doubles](https://docs.amd.com/r/2024.2-English/ug1399-vitis-hls/Floats-and-Doubles).
[^amd-expr]: [AMD Vitis HLS `expression_balance`](https://docs.amd.com/r/2024.2-English/ug1399-vitis-hls/pragma-HLS-expression_balance).
[^intel-scope]: [Intel HLS scoped floating-point pragmas](https://www.intel.com/content/www/us/en/docs/programmable/683349/22-4/pro-edition-scope-pragmas.html).
[^intel-fp]: [Intel oneAPI floating-point pragmas](https://www.intel.com/content/www/us/en/docs/oneapi-fpga-add-on/developer-guide/2024-2/floatng-point-prgmas.html).
[^intel-dsp]: [Intel oneAPI DSP usage control](https://www.intel.com/content/www/us/en/docs/oneapi-fpga-add-on/developer-guide/2024-2/control-dsp-usage.html).
[^rust-muladd]: [Rust `f32::mul_add`](https://doc.rust-lang.org/std/primitive.f32.html#method.mul_add).
