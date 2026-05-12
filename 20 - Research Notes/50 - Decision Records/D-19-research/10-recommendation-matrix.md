---
type: "research"
decision: "D-19"
angle: 10
topic: "recommendation-matrix"
---

# Recommendation Matrix

## Decision Frame

[[D-19]] asks whether Rust+HLS treats FMA precision as Scalagen-compatible multiply-then-add or as fused hardware/HLS multiply-add. The queue frames the decision as matching Scalagen unfused precision or Chisel/HLS fused FMA precision (`20 - Research Notes/40 - Decision Queue.md:83-85`). The current source split is concrete: Scalagen emits `FixFMA` and `FltFMA` as `($m1 * $m2) + $add`, and `RegAccumFMA` writes `m0*m1` on first iteration or `m0*m1 + reg.value` afterward (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/scalagen/ScalaGenFixPt.scala:150`; `/Users/david/Documents/David_code/spatial/src/spatial/codegen/scalagen/ScalaGenFltPt.scala:120`; `/Users/david/Documents/David_code/spatial/src/spatial/codegen/scalagen/ScalaGenReg.scala:57-64`). [[20 - Numeric Reference Semantics]] and [[60 - Reduction and Accumulation]] therefore make the legacy reference unfused unless D-19 explicitly changes it.

## Option Matrix

| Option | Strength | Problem | D-19 disposition |
|---|---|---|---|
| Scalagen-unfused canonical | Best Scalagen parity. It preserves fixed multiply truncation before add and float reclamping after both multiply and add. | As a single policy, it blocks known hardware intent and useful HLS performance/resource choices. | Reject as the only policy; keep as the reference/default. |
| Fused-HLS canonical | Matches Chisel float FMA intent and many HLS optimization paths. `ChiselGenMath` lowers `FltFMA` to `Math.fma`, and Zynq BigIP exposes `ffma`/`FFma` (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/chiselgen/ChiselGenMath.scala:51`; `/Users/david/Documents/David_code/spatial/fringe/src/fringe/targets/zynq/BigIPZynq.scala:203-209`). | It changes current Scalagen goldens, reduces [[D-18]] float reclamp events from two to one, and can move [[D-17]] stochastic event boundaries if unbiased fused variants are added. | Reject as canonical reference. |
| Dual-mode with unfused reference and fused opt-in | Preserves Scalagen replay while allowing hardware-correlated FMA where declared. It matches the provenance pattern already recommended by [[D-17]] and [[D-18]]. | Requires explicit mode labels, tests, and mismatch reporting. | Recommend. |
| Tool-default contraction | Cheapest HLS implementation: let compiler flags and vendor defaults decide whether `a*b+c` contracts. | Non-portable and hard to audit; Intel and AMD controls/support differ, and current notes mark Vitis contraction-off proof as unverified. | Reject. |

## Recommendation

Adopt **dual-mode with unfused reference and fused opt-in**.

The canonical Rust reference mode should be:

`fma_policy = scalagen_unfused_two_round_v1`

In this mode, Rust reproduces current Scalagen behavior for scalar `FixFMA`/`FltFMA` and specialized `RegAccumFMA`: compute the multiply in the operand/result format, apply that operation's ordinary rounding, clamp, wrap, validity, or custom-float packing behavior, then add and apply the ordinary add behavior. For floats, this means `FloatPoint.clamped` can run once after multiply and once after add, so the [[D-18]] `float_pack_policy` must be recorded beside `fma_policy` (`/Users/david/Documents/David_code/spatial/emul/src/emul/FloatPoint.scala:153-157`; `/Users/david/Documents/David_code/spatial/emul/src/emul/FloatPoint.scala:417-433`; [[04-precision-overlap-d17-d18]]). For fixed point, it means preserving the current `FixedPoint.*` shift/clamp followed by `FixedPoint.+` clamp path (`/Users/david/Documents/David_code/spatial/emul/src/emul/FixedPoint.scala:14-17`; [[01-source-ir-scalagen-surface]]).

Add an explicit non-default opt-in:

`fma_policy = fused_single_round_v1`

This mode may use Rust `mul_add` for IEEE-native formats when that is the declared reference, or a custom exact product-plus-add followed by one final pack for Spatial custom floats/fixed formats. HLS may instead report `fma_policy = backend_native_fma` until the vendor result has been bit-tested against `fused_single_round_v1`. This distinction matters because [[06-hls-toolchain-support-cost]] shows real fused support and cost benefits, but also target-specific availability, II/resource tradeoffs, and possible C++/RTL mismatch risk.

Reject **Scalagen-unfused canonical as a single-mode mandate**. It is the right reference oracle, but forcing all HLS output to disable fusion would discard a hardware path the existing compiler already seeks by default through `fuseAsFMA` and `RewriteTransformer` (`/Users/david/Documents/David_code/spatial/src/spatial/SpatialConfig.scala:75-76`; `/Users/david/Documents/David_code/spatial/src/spatial/transform/RewriteTransformer.scala:263-274`).

Reject **fused-HLS canonical** because it would silently redefine current Scalagen arithmetic and invalidate tests that assume host-golden `a*b+c` behavior. Existing tests catch FMA-shaped programs, not fused-versus-unfused bit patterns, so canonical fusion would be under-tested ([[02-tests-apps-usage]]).

Reject **tool-default contraction** outright. Every simulator run, golden file, HLS artifact, report parser, and mismatch should record `fma_policy`, backend capability, contraction controls, and fallback. If a tool cannot guarantee the requested policy, the backend should emit a diagnostic or a named fallback, never claim reference parity.
