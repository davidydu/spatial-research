---
type: "research"
decision: "D-19"
angle: 9
topic: "implementation-cost-migration"
---

# D-19 Research: Implementation Cost and Migration Plan

## Cost Matrix

[[D-19]] has three viable implementation policies: keep the Scalagen-compatible unfused reference, make fused FMA canonical, or carry both with explicit provenance. The existing source argues against treating this as a spelling-only backend change. FMA creation is already default-on in hardware scope (`src/spatial/SpatialConfig.scala:75-76`; `src/spatial/traversal/RewriteAnalyzer.scala:42-58`), and `RewriteTransformer` rewrites both fixed and float add-of-mul forms into `FixFMA`/`FltFMA` (`src/spatial/transform/RewriteTransformer.scala:263-274`). But Scalagen emits those nodes as `($m1 * $m2) + $add`, and `RegAccumFMA` as `m0 * m1 + reg.value`, so the reference path remains two-step arithmetic (`src/spatial/codegen/scalagen/ScalaGenFixPt.scala:150`; `src/spatial/codegen/scalagen/ScalaGenFltPt.scala:120`; `src/spatial/codegen/scalagen/ScalaGenReg.scala:57-64`; [[01-source-ir-scalagen-surface]], [[60 - Counters and Primitives]]).

**Unfused reference default** is the cheapest simulator migration. Rust can dispatch `FixFMA`, `FltFMA`, and `RegAccumFMA` through the ordinary `mul` then `add` operators, reusing the `FixedPoint` wrap/truncate path and the `FloatPoint.clamped` path twice. Incremental Rust cost is low to medium, assuming [[D-18]] already implements custom float packing. HLS cost is medium to high because the backend must prevent tool contraction for exact parity: floating HLS must emit a materialized product, then add, and prove the report/RTL did not infer a fused primitive. Intel controls are known; the Vitis no-contraction proof is still unverified in [[06-hls-toolchain-support-cost]]. Tests are medium: add paired fixtures where two-round and one-round answers differ, then select the unfused expected bits. Metadata, reports, and docs are low to medium: add `fma_policy = unfused_two_round`, record that `FltFMA` reclamps twice, and explain that FMA-shaped IR does not imply fused precision.

**Fused canonical default** is cleaner for float hardware correlation but more expensive. Rust cost is medium to high: IEEE `f32::mul_add` helps native floats, but Spatial custom `Flt[M,E]` needs exact product-plus-add followed by one [[D-18]] pack, and true fixed-point FMA would require full-width product/add alignment followed by one final cast. HLS cost is medium on Zynq/CXP-like float targets, where Chisel lowers `FltFMA` to `Math.fma` and BigIP `ffma`, but high for portability because `BigIP` defaults `ffma` to unimplemented and fixed `Math.fma` still calls `mul(... Truncate, Wrapping)` before adding (`src/spatial/codegen/chiselgen/ChiselGenMath.scala:50-51`; `fringe/src/fringe/templates/math/Math.scala:671-677`; `fringe/src/fringe/templates/math/Math.scala:843-858`; [[03-chisel-fringe-hardware-path]]). Tests are high: existing app tolerances and checksum tests do not pin one-ulp differences ([[02-tests-apps-usage]]). Reports are medium to high: `ResourceReporter` and `ResourceCountReporter` cover fixed FMA more than float FMA, while latency CSVs name both `FixFMA` and `FltFMA` (`src/spatial/codegen/resourcegen/ResourceReporter.scala:157-163`; `src/spatial/codegen/resourcegen/ResourceCountReporter.scala:32-57`; `resources/models/Zynq_Latency.csv:83-126`; [[05-backend-variation]]).

**Dual-mode policy** has the highest upfront plumbing cost but the lowest migration risk. Rust cost is high but contained: implement `unfused_two_round`, `fused_single_round`, and `backend_native_fma` comparison labels behind a policy enum, then apply the same dispatch to scalar FMA and `RegAccumFMA`. HLS cost is high because each target must declare whether it supports exact unfused, exact fused, or native-only FMA. Tests are high initially: every sentinel should store both expected bit patterns plus an allowed backend label. Metadata/reports/docs are medium to high, but this work directly supports mismatch triage across [[D-17]], [[D-18]], and [[20 - Numeric Reference Semantics]].

## Migration Plan

Phase 1: make unfused the Rust reference default. Add policy metadata to run manifests, golden files, mismatch reports, and generated HLS artifacts: `fma_policy`, `rounding_event_policy`, `float_pack_policy`, and `backend_fma_capability`. Fix the Scala executor FMA bug or exclude it from D-19 parity, since `FixResolver` currently computes `(m0 * m1) * add` and `FltResolver` has no `FltFMA` case (`src/spatial/executor/scala/resolvers/FixResolver.scala:10-15`; `src/spatial/executor/scala/resolvers/FltResolver.scala:8-42`).

Phase 2: add deterministic D-19 fixtures: scalar `Float`, `Half`, custom `FltPt`, fixed-point truncation, `RegAccumFMA`, cancellation/subnormal cases, and GEMM/dot elementwise checks. These should verify both policy answers, not just tolerance pass/fail.

Phase 3: add fused as opt-in. Label vendor/tool results `backend_native_fma` until bit-tested against Rust `fused_single_round`; label exact split HLS `unfused_two_round` only when reports or RTL prove no contraction.

Phase 4: decide whether to promote fused canonical. Until then, the lowest-cost safe recommendation is dual-mode with `unfused_two_round` as the compatibility default and fused/native modes as explicit migration targets.
