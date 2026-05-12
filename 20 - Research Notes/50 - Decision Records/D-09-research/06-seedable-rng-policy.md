---
type: "research"
decision: "D-09"
angle: 6
---

# Seedable RNG Policy

## Current Scala Contract

D-09 asks whether Rust simulator unbiased rounding should keep JVM nondeterminism, use a seedable deterministic RNG, or replace the behavior with deterministic rounding (`20 - Research Notes/40 - Decision Queue.md:43-45`). The Scala emulation path is probabilistic today: `FixedPoint.unbiased` shifts off four guard bits, turns the low nibble into a fractional remainder, calls `scala.util.Random.nextFloat()`, and rounds away from zero when `rand + remainder >= 1` before clamping or saturating (`emul/src/emul/FixedPoint.scala:232-240`). The fixed-point operators `*&`, `/&`, `*&!`, and `/&!` all delegate to that helper (`emul/src/emul/FixedPoint.scala:52-63`), and staged fix-to-fix casts also resolve to `FixedPoint.unbiased` in the Scala executor (`src/spatial/executor/scala/resolvers/FixResolver.scala:45-51`).

Generated Scala keeps this hidden. Scalagen emits one-line operator calls for unbiased multiply/divide and saturating variants (`src/spatial/codegen/scalagen/ScalaGenFixPt.scala:92-99`), and one-line direct calls to `FixedPoint.unbiased` for `FixToFixUnb` and `FixToFixUnbSat` (`src/spatial/codegen/scalagen/ScalaGenFixPt.scala:107-114`). The staged API describes `*&` and `/&` as probabilistically rounding after multiply/divide (`argon/src/argon/lang/Fix.scala:75-87`), while the current math test checks that the mean of 256 unbiased samples is near the real product, not that any particular bit sequence repeats (`test/spatial/tests/feature/math/SpecialMath.scala:51-88`).

## Seed Source And Run Reproducibility

The Rust policy should make seeded deterministic RNG the canonical reference mode, not a best-effort clone of `scala.util.Random`. Use a single explicit `u64` seed from config/CLI, with default seed `0` for CI and golden tests. A separate `auto` or `random` seed mode may be useful for fuzz-style runs, but it must print and persist the resolved seed in simulator output (unverified). Reproducibility should be scoped as: same Rust simulator version, same RNG algorithm label, same seed, same program, same inputs, and same stable operation IDs produce the same rounded results.

This fits the existing configuration shape: `SpatialConfig` is a mutable option bag with backend and simulator-related fields such as `enableSim`, `enableScalaExec`, and Scala execution latency/throughput knobs (`src/spatial/SpatialConfig.scala:21-23`, `src/spatial/SpatialConfig.scala:95-100`). CLI options are added with `cli.opt[...]("name").action{...}.text(...)`, as shown by `--threads`, `--sim`, and `--synth` (`src/spatial/Spatial.scala:273-293`). If the seed is carried through the Scala-fronted pipeline, it should be copied in `SpatialConfig.copyTo`, because threaded DSE creates fresh `State` objects and copies `SpatialConfig` into each worker (`src/spatial/SpatialConfig.scala:102-120`, `src/spatial/dse/DSEAnalyzer.scala:320-335`).

## Stable IDs Versus Sequential Streams

There are two plausible deterministic designs. A sequential stream seeded once per run is closest to the current Scala shape: every unbiased operation consumes the next random value. It is simple, but any inserted operation, changed traversal order, or parallel execution can shift the stream and change later results (unverified). Per-thread streams reduce lock contention but still make results sensitive to partitioning and scheduling unless dynamic work ownership is fixed (unverified).

Prefer a stable per-operation derivation. Each unbiased rounding event should derive its threshold from `(seed, rng_algorithm_version, static_op_id, dynamic_instance_id, lane_or_element_id)`. A counter/hash style derivation avoids shared mutable consumption and is order-insensitive when those IDs are stable (unverified). The cost is metadata discipline: current Scalagen one-liners do not expose RNG IDs (`src/spatial/codegen/scalagen/ScalaGenFixPt.scala:92-114`), so the Rust simulator needs IDs from the IR node, emitted source map, or an explicit generated tag. Sequential mode can remain as `legacy_stream` for debugging Scala-like consumption order, but it should not be the reference mode.

## API Surface And Tests

Expose three fields: `sim_rng_policy = seeded_stable | legacy_stream | auto_seeded`, `sim_rng_seed = u64`, and `sim_rng_algorithm = spatial-fixed-v1`. CLI aliases can be `--sim-rng-policy`, `--sim-rng-seed`, and `--sim-rng-algorithm`; `--sim-rng-seed` alone should imply `seeded_stable`. The simulator should print these fields into run metadata, and every mismatch report should include them.

Tests should separate statistics from determinism. Keep a mean-based unbiased rounding test like `SpecialMath` (`test/spatial/tests/feature/math/SpecialMath.scala:74-94`), but run it under a fixed seed to remove flakiness. Add golden tests that same seed plus same stable IDs reproduce exactly, different seeds can change threshold decisions, and changing thread count or evaluation order does not change `seeded_stable` results (unverified). Add a negative compatibility test or documentation fixture stating that `seeded_stable` does not match the JVM `Random.nextFloat()` sequence.

## Recommendation Implication

Select seedable deterministic RNG as D-09's Rust simulator policy. The decision should explicitly label divergence from Scala as `rng_compatibility = statistical-spatial, not-jvm-sequence`: Rust preserves the unbiased rounding probability rule grounded in `FixedPoint.unbiased`, but not the JVM global RNG stream (`emul/src/emul/FixedPoint.scala:232-240`). This gives reproducible debugging and CI while keeping the stochastic rounding contract visible instead of smuggled through a process-global Scala RNG.
