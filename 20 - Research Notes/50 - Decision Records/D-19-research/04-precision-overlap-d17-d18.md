---
type: "research"
decision: "D-19"
angle: 4
topic: "precision-overlap-d17-d18"
---

# D-19 Research: Precision Overlap with D-17 and D-18

## Fusion Surface

Spatial recognizes FMA as a rewrite from `Add(Mul(...), add)` rather than as direct user syntax. `RewriteAnalyzer` marks fixed and float add-mul patterns fusible only in hardware, when the multiply has a forward-only or reduce-specialization consumer pattern and `spatialConfig.fuseAsFMA` is enabled (`/Users/david/Documents/David_code/spatial/src/spatial/traversal/RewriteAnalyzer.scala:42-58`). `RewriteTransformer` then replaces matching `FixAdd(FixMul(...), add)` and `FltAdd(FltMul(...), add)` with `FixFMA` or `FltFMA` (`/Users/david/Documents/David_code/spatial/src/spatial/transform/RewriteTransformer.scala:263-274`). This means D-19 owns an optimization boundary: the same source expression can either remain two ordinary operators or become one FMA node.

Scalagen currently does not exploit the semantic distinction. Both `FixFMA` and `FltFMA` emit `($m1 * $m2) + $add`, so generated Scala follows the ordinary operator sequence (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/scalagen/ScalaGenFixPt.scala:150`; `/Users/david/Documents/David_code/spatial/src/spatial/codegen/scalagen/ScalaGenFltPt.scala:120`). [inference] Therefore, any D-19 policy that says "fused single-rounding" cannot cite current Scalagen FMA emission as already implementing it; it would be a new reference rule or a backend capability.

## Fixed-Point Precision

For ordinary fixed point, unfused `a * b + c` has two truncation/wrap points. `FixedPoint.*` computes `(this.value * that.value) >> fmt.fbits` and immediately calls `FixedPoint.clamped`; `FixedPoint.+` then adds the already quantized product to `c` and calls `clamped` again. The clamp path wraps into the destination bit width (`/Users/david/Documents/David_code/spatial/emul/src/emul/FixedPoint.scala:14-16`; `/Users/david/Documents/David_code/spatial/emul/src/emul/FixedPoint.scala:203-208`). This is two-rounding in fixed-point terms, even though it is truncation plus wrap, not probabilistic rounding.

A true fixed FMA single-rounding rule would instead keep the full product, add aligned `c`, and cast once at the end. [inference] The visible Fringe fixed FMA implementation does not prove that rule today: `Math.fma` builds an `FMAWrapper`, but inside it calls `mul(..., Truncate, Wrapping, ...)` and then `+ getRetimed(add, ...)`; `FixedPoint.+` itself lowers to `Math.add(..., Truncate, Wrapping, ...)` (`/Users/david/Documents/David_code/spatial/fringe/src/fringe/templates/math/Math.scala:844-858`; `/Users/david/Documents/David_code/spatial/fringe/src/fringe/templates/math/FixedPoint.scala:60-77`). ChiselGen emits `Math.fma(...).toFixed(...)`, but that call stack still matters for precision (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/chiselgen/ChiselGenMath.scala:50`).

D-17 stochastic events occur only when the operation or cast is explicitly `Unbiased`. Scala emul `*&`, `/&`, `*&!`, `/&!`, and unbiased casts reach `FixedPoint.unbiased`, which consumes four guard bits, draws `scala.util.Random.nextFloat()`, and then wraps or saturates (`/Users/david/Documents/David_code/spatial/emul/src/emul/FixedPoint.scala:52-63`; `/Users/david/Documents/David_code/spatial/emul/src/emul/FixedPoint.scala:232-240`; [[D-17]]). Current FMA fusion matches `FixMul`, not `UnbMul`, so it does not remove a D-17 event today. [inference] If D-19 later adds "unbiased FMA," the stochastic event should be at the final FMA cast, not at the product, and must receive its own D-17 event identity.

## Float Precision

Float unfused behavior is sharper because every finite result reclamps through the D-18 packer. `FloatPoint.*` calls `FloatPoint.clamped(this.value * that.value, ...)`; `FloatPoint.+` calls `FloatPoint.clamped(this.value + that.value, ...)` (`/Users/david/Documents/David_code/spatial/emul/src/emul/FloatPoint.scala:153-157`). `clamped` calls `clamp`, then `convertBackToValue`, so the intermediate product may be rounded into the target `FltFormat` before the add sees it (`/Users/david/Documents/David_code/spatial/emul/src/emul/FloatPoint.scala:417-427`). That means unfused float multiply-add creates two D-18 reclamp events.

Those reclamps include the legacy edge behavior under debate in [[D-18]]: `clamp` patches `y < fmt.SUB_E && x > 1.9`, handles normal and subnormal one-discarded-bit rounding, and underflows to signed zero in the final arms (`/Users/david/Documents/David_code/spatial/emul/src/emul/FloatPoint.scala:335-395`). With fusion, `a*b+c` should produce one exact product-plus-add result and one final pack. [inference] This reduces the number of opportunities for the `x > 1.9` rescue, subnormal one-bit round, overflow-to-infinity, or signed-zero underflow to fire from two to one.

Hardware has a float FMA hook that is distinct from add and multiply. ChiselGen lowers `FltFMA` to `Math.fma`, `Math.fma` delegates to `globals.bigIP.ffma`, and Zynq/CXP targets instantiate `FFma` (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/chiselgen/ChiselGenMath.scala:51`; `/Users/david/Documents/David_code/spatial/fringe/src/fringe/templates/math/Math.scala:671-677`; `/Users/david/Documents/David_code/spatial/fringe/src/fringe/targets/zynq/BigIPZynq.scala:203-209`). [inference] The interface and module name imply fused hardware intent, but the local source does not audit the `FFma` internals or rounding mode, so D-19 should require a declared capability label rather than assuming all `ffma` implementations are bit-equivalent to a Rust reference.

## Overlap Rule

D-19 should record FMA precision as provenance, not just as an optimization flag. Recommended labels: `fma_policy = unfused_two_round` for current Scalagen-style reference emission, `fma_policy = fused_single_round` only where the backend/reference actually computes product-plus-add before one final cast, and `fma_policy = backend_native_fma` for target `FFma` or HLS behavior until proven bit-identical.

For [[D-17]], provenance must say whether stochastic rounding happened at an intermediate multiply/cast or at the final fused result. For [[D-18]], provenance must say whether float packing/reclamp ran once or twice. [inference] Without these labels, a Rust simulator could be "more accurate" by using fused FMA and still fail Spatial parity, while a hardware backend could be correctly fused but incomparable against an unfused Scalagen golden.
