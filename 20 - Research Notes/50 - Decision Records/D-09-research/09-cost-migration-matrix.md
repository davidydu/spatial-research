---
type: "research"
decision: "D-09"
angle: 9
---

# Implementation Cost and Migration Matrix

## Baseline

D-09/Q-118 is the Rust simulator choice: match JVM RNG nondeterminism, use seedable deterministic RNG, or make unbiased rounding deterministic (`20 - Research Notes/40 - Decision Queue.md:43-45`). D-17/Q-144 repeats the same question as the future canonical policy, so any D-09 implementation should be labelled provisional until D-17 chooses the cross-backend rule (`20 - Research Notes/40 - Decision Queue.md:75-77`). The current Scala fact pattern is narrow but awkward: `FixedPoint.unbiased` shifts off four guard bits, computes a 1/16 remainder, calls `scala.util.Random.nextFloat()`, rounds away from zero if `rand + remainder >= 1`, then clamps or saturates (`emul/src/emul/FixedPoint.scala:232-240`). Scalagen reaches it from `UnbMul`, `UnbDiv`, `UnbSatMul`, `UnbSatDiv`, `FixToFixUnb`, and `FixToFixUnbSat` (`src/spatial/codegen/scalagen/ScalaGenFixPt.scala:96-114`).

## Cost Matrix

| Option | Rust simulator API | Tests | Manifest/config | HLS lowering | Compatibility |
|---|---|---|---|---|---|
| Exact JVM nondeterminism | Highest cost: clone or embed JVM RNG behavior, global stream state, and evaluation order (unverified). | Keeps statistical tests; bit-exact tests remain impossible across runs. | No seed field, but must record `rng_policy = jvm_global` for audit (unverified). | Poor fit: hardware cannot depend on host JVM RNG (unverified). Current Chisel hardware instead uses `PRNG` seeded at elaboration (`fringe/src/fringe/templates/math/PRNG.scala:6-16`). | Best legacy Scalagen behavior, worst reproducibility. |
| Seedable sequential RNG | Medium cost: add `RoundingContext` or simulator-wide RNG to every unbiased call (unverified). | Enables golden tests for one traversal order; fragile if operation order changes. | Add `sim_rng_policy`, `sim_rng_seed`, and algorithm version. Existing config/CLI style can carry simulator knobs (`src/spatial/SpatialConfig.scala:21-23`, `src/spatial/Spatial.scala:281-293`). | Maps to one stream or per-kernel stream; stalls/parallelism can shift consumption (unverified). | Preserves stochastic distribution but not JVM sequence. |
| Seedable stable per-operation/per-site RNG | Medium-high cost: derive random thresholds from seed plus stable op/site/dynamic/lane IDs (unverified). | Strongest tests: same seed remains stable under scheduling and thread-count changes (unverified). Existing `SpecialMath` checks means, not exact sequences (`test/spatial/tests/feature/math/SpecialMath.scala:75-93`). | Best manifest fit: emit simulator metadata, JSON sidecar, schema/hash/version from typed manifest artifacts (`20 - Research Notes/50 - Decision Records/D-05.md:78-87`). | Best stochastic HLS fit: one seed per site or counter-based dither, explicit advance policy (unverified). | Good migration: statistical Spatial compatibility without hidden JVM state. |
| Deterministic round-to-nearest-even | Low-medium cost in Rust arithmetic; no RNG state. | Replace stochastic goldens with exact boundary tests; app thresholds likely still need review (unverified). | Record `rounding_policy = nearest_even`; no seed. | Cheapest portable HLS rounding if target fixed-point supports it (unverified). | Semantic break: current spec calls `unbiased` RNG-based and nondeterministic (`10 - Spec/50 - Code Generation/20 - Scalagen/20 - Numeric Reference Semantics.md:41-47`). |
| Deterministic truncation / nearest-away variants | Lowest cost for truncation because Fringe already names `Truncate`; nearest-away needs a new mode beside `Truncate` and `Unbiased` (`fringe/src/fringe/templates/math/RoundingMode.scala:3-8`). | Update tests to exact outputs; loses statistical intent of `SpecialMath` (`test/spatial/tests/feature/math/SpecialMath.scala:51-88`). | Record deterministic variant and version. | Truncation is hardware-cheap; nearest-away is small compare/add logic (unverified). | Biggest semantic rename risk: truncation is not unbiased; nearest-away only mimics current signed direction after choosing a threshold. |

## Migration Work

All non-JVM options require splitting "compatibility" from "policy." Keep the current guard-bit arithmetic and signed away-from-zero branch as a reusable helper, because they are sourced behavior, not RNG policy (`emul/src/emul/FixedPoint.scala:224-240`). Add conformance tests for multiply, divide, saturating multiply/divide, and fixed-to-fixed casts; current focused coverage leaves division/cast gaps, and `SpecialMath` itself says subtraction and division still need checking (`test/spatial/tests/feature/math/SpecialMath.scala:106-107`). For manifest integration, treat rounding as simulator/build metadata, not host ABI: D-05 already routes simulator metadata, JSON sidecars, manifest hash, schema version, and compatibility checks through generated artifacts (`20 - Research Notes/50 - Decision Records/D-05.md:78-87`).

## HLS and D-17 Gate

Current hardware-style rounding is already not exact JVM behavior: non-literal fixed conversion instantiates `fix2fixBox`, whose `Unbiased` case creates a `PRNG(scala.util.Random.nextInt)` and adds low PRNG bits before shaving fractional bits (`fringe/src/fringe/targets/SimBlackBoxes.scala:41-47`). Literal `BigIPSim.fix2fix` uses `scala.math.random` salt and is explicitly preceded by "Likely that there are mistakes here" (`fringe/src/fringe/targets/BigIPSim.scala:247-253`). Therefore, D-09 should not bless JVM nondeterminism as canonical. It should implement a configurable simulator policy now, then let D-17 decide whether "unbiased" remains stochastic or becomes deterministic.

## Recommendation: Stable-Site Seeded Migration

Choose **Stable-Site Seeded Migration**: default the Rust simulator to seedable stable per-operation/per-site stochastic rounding, with explicit fields for policy, seed, algorithm version, and compatibility label. Provide `legacy_stream` only as a debugging mode and deterministic modes only behind named policy values. This gives reproducible CI and HLS-compatible seed plumbing while preserving the stochastic meaning that existing tests and apps actually exercise.
