---
type: "research"
decision: "D-09"
angle: 8
---

# Reproducibility, Debugging, and Testing Risks

## Baseline Risk Surface

The local specs make `emul` the simulator ground truth: Numeric Reference Semantics says Scalagen and `emul` define bit-level numeric meaning, and Data Types says Scalagen wins when native Scala, JVM, or hardware expectations disagree (`10 - Spec/50 - Code Generation/20 - Scalagen/20 - Numeric Reference Semantics.md:27-29`; `10 - Spec/20 - Semantics/50 - Data Types.md:38`). The unresolved part is `FixedPoint.unbiased`: it expects four extra fractional bits, computes `biased` and a 1/16 remainder, calls `scala.util.Random.nextFloat()`, then rounds away from zero before clamping or saturating (`emul/src/emul/FixedPoint.scala:224-240`). Arithmetic operators feed that helper for `*&`, `/&`, `*&!`, and `/&!` (`emul/src/emul/FixedPoint.scala:52-63`), and Scalagen preserves those nodes or calls `FixedPoint.unbiased` directly for unbiased casts (`src/spatial/codegen/scalagen/ScalaGenFixPt.scala:96-114`).

Testing is already statistical, not bit-sequence based. `SpecialMath` runs 256 identical unsigned and signed `*&` operations, checks the output means against exact products within `2^-4`, and separately checks saturated endpoints for `*&!` (`test/spatial/tests/feature/math/SpecialMath.scala:36-94`). Its own final print says subtraction and division still need checking (`test/spatial/tests/feature/math/SpecialMath.scala:106-107`). The test harness converts `"PASS: true"`/`"PASS: false"` into pass/fail, so CI expects a stable boolean even when the underlying arithmetic is random (`argon/src/argon/DSLTest.scala:120-123`).

## JVM-Like Nondeterminism

Keeping JVM-like nondeterminism is the narrowest match to today's reference wording: Numeric Reference Semantics explicitly calls `unbiased` nondeterministic because of `scala.util.Random.nextFloat()` (`10 - Spec/50 - Code Generation/20 - Scalagen/20 - Numeric Reference Semantics.md:45-47`). The debugging cost is high. A failing low-bit result may not replay, and a marginal `SpecialMath` failure can disappear on rerun. If a future Rust simulator consumes a single RNG stream while evaluating independent lanes in parallel, results can become schedule/order-sensitive (unverified). This is especially awkward because current generated Scala emits sequential `.foreach` loops for unrolled controls, while the Scala executor models multiple shifted pipelines and ticks them by iterating a map (`src/spatial/codegen/scalagen/ScalaGenController.scala:88-103`; `src/spatial/executor/scala/ControlExecutor.scala:364-386`). Treating the stream order as semantic would freeze incidental traversal choices.

CI is only partly protected today. SBT test concurrency defaults to one test thread unless `maxthreads` is set (`build.sbt:179-181`), but Spatial also has a `threads` tuning knob and mutable config copied into worker states (`src/spatial/SpatialConfig.scala:12-13`; `src/spatial/SpatialConfig.scala:102-113`). Relying on process-global RNG behavior therefore creates fragile assumptions around future parallel test and simulator runners (unverified).

## Seedable Deterministic Stochastic Rounding

Seedable stochastic rounding keeps the local probability rule while making failures replayable. The seed must be explicit simulator state, not a hidden JVM artifact: `Spatial.scala` already shows the CLI pattern for `--threads` and `--sim`, and `SpatialConfig.copyTo` is the path that would need to carry any seed into cloned worker configs (`src/spatial/Spatial.scala:273-286`; `src/spatial/SpatialConfig.scala:102-113`). Tests could then assert exact replay for a fixed seed and keep statistical mean checks under deterministic samples.

The main design risk is stream sensitivity. A single sequential RNG stream is easy to implement but changes downstream decisions whenever an earlier rounding call is inserted, removed, or reordered (unverified). A stable derivation from `(seed, operation id, dynamic instance, lane)` is more robust for parallel execution and CI replay (unverified), but it requires generated Rust to preserve enough source/IR identity. This aligns better with hardware intent than JVM parity: Fringe labels `Unbiased` as LFSR stochastic rounding, and its converter instantiates a seeded `PRNG` that advances when enabled (`fringe/src/fringe/templates/math/RoundingMode.scala:3-8`; `fringe/src/fringe/templates/math/Converter.scala:36-43`; `fringe/src/fringe/templates/math/PRNG.scala:6-16`).

## Deterministic Arithmetic Rounding

Deterministic arithmetic rounding gives the cleanest debugger and CI story: no random seed, no distributional flakes, and no execution-order dependence. But it is not an implementation detail. It replaces the current `FixedPoint.unbiased` contract, the Scalagen lowering contract, and the Data Types HLS note that says the Rust port must decide whether unbiased remains nondeterministic, becomes seeded, or becomes exact/deterministic (`10 - Spec/20 - Semantics/50 - Data Types.md:64-66`). It would also require rewriting tests that currently check statistical mean behavior rather than deterministic nearest-even or threshold behavior. General HLS library availability for deterministic fixed-point quantization modes is plausible but not locally sourced (unverified).

## Recommendation Implication

For D-09, choose seedable deterministic stochastic rounding as the Rust simulator policy. Default CI to a fixed seed and stable per-event derivation; expose an opt-in auto-seed mode that records the resolved seed. Do not promise JVM RNG sequence compatibility. Reserve deterministic arithmetic rounding for D-17 as a cross-backend semantic replacement, not a Rust-only testing convenience.
