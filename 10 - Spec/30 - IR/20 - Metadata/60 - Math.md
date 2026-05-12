---
type: spec
concept: Math metadata
source_files:
  - "src/spatial/metadata/math/MathData.scala:6-41"
  - "src/spatial/metadata/math/package.scala:16-40"
source_notes:
  - "No prior deep-dive note; written directly from source."
hls_status: rework
depends_on:
  - "[[00 - Metadata Index]]"
status: draft
---

# Math

## Summary

Math metadata stores small analysis facts around modulo arithmetic, residual sets, cycle membership, and numeric source types. `Modulus` records the modulus on `FixMod` and lowered nodes according to its source comment, and `Residual` records a `ResidualGenerator` equation whose residual set is described as values congruent to `(A*k + B) mod M` (src/spatial/metadata/math/MathData.scala:6-22). `InCycle` marks whether a node participates in an accumulation cycle, and its comment gives FMA rewrites as the motivating case for avoiding inconsistent rewrites across a cycle (src/spatial/metadata/math/MathData.scala:24-32). `SrcType` records the original type for conversion nodes such as `FixToFix`, with the stated purpose of making data scraping easier (src/spatial/metadata/math/MathData.scala:34-41).

## Fields

- `Modulus(mod)` has transfer policy `SetBy.Analysis.Self`, and its accessors are `getModulus`, `modulus`, and `modulus_=` (src/spatial/metadata/math/MathData.scala:6-12; src/spatial/metadata/math/package.scala:17-19).
- `Residual(equ)` has transfer policy `SetBy.Analysis.Self`, and `getResidual` reads a `ResidualGenerator` from metadata on `s.trace` rather than directly from `s` (src/spatial/metadata/math/MathData.scala:14-22; src/spatial/metadata/math/package.scala:27).
- `InCycle(is)` has transfer policy `SetBy.Analysis.Self`, and `inCycle` defaults to `false` when metadata is absent (src/spatial/metadata/math/MathData.scala:24-32; src/spatial/metadata/math/package.scala:21-22).
- `SrcType(typ)` has transfer policy `SetBy.Analysis.Self`, and the package exposes `getSrcType` plus `setSrcType` rather than a Scala setter named `srcType_=` (src/spatial/metadata/math/MathData.scala:34-41; src/spatial/metadata/math/package.scala:24-25).

## Implementation

The package object imports bounds, retiming, type helpers, and control metadata, which makes the math helper layer dependent on other metadata categories even though the data case classes are small (src/spatial/metadata/math/package.scala:5-8). `modulus` returns `-1` when no `Modulus` metadata is stored, so absence is observable through the non-optional getter (src/spatial/metadata/math/package.scala:17-19). `residual_=` writes an explicit `Residual(equ)` on the symbol, but `getResidual` later looks up `Residual` on `s.trace`, so rewrites that change trace relationships can change the lookup target (src/spatial/metadata/math/package.scala:27-40).

When no explicit residual is stored, `residual` first returns `ResidualGenerator(s.traceToInt)` for traced constants (src/spatial/metadata/math/package.scala:28-30). If the traced numeric symbol has a counter and the counter has static start and step, `residual` extracts `Final(start)` and `Final(step)`, reads counter parallelism and lanes, computes `A = par * step`, computes `B = lanes.map { lane => start + lane * step }`, and constructs `ResidualGenerator(A, B, 0)` (src/spatial/metadata/math/package.scala:30-38). If neither explicit metadata, constant tracing, nor static counter structure applies, `residual` falls back to `ResidualGenerator(1,0,0)` (src/spatial/metadata/math/package.scala:39).

## Interactions

The residual path depends on bounds because static counter start and step are pattern-matched with `Final(start)` and `Final(step)` (src/spatial/metadata/math/package.scala:31-32). The residual path depends on type helpers and the numeric counter API because it casts the trace to `Num[_]`, checks `getCounter`, and reads `counter.ctr` and `counter.lanes` (src/spatial/metadata/math/package.scala:30-34). The `InCycle` flag overlaps conceptually with retiming and rewrite metadata, but this file only proves the stated FMA-rewrite motivation and the boolean accessors (src/spatial/metadata/math/MathData.scala:24-32; src/spatial/metadata/math/package.scala:21-22).

## HLS notes

The residual generator logic is a compiler-side banking and modulo analysis helper, so the Rust+HLS rewrite should preserve the `A = par * step`, lane-start `B`, and `C = 0` derivation before deciding how much of it survives into HLS scheduling (src/spatial/metadata/math/package.scala:30-38). Mapping `InCycle` to HLS FMA legality is likely a rewrite-policy concern rather than a hardware field (inferred, unverified).

## Open questions

- Q-meta-14 asks whether `getResidual` intentionally reads `Residual` from `s.trace` while `residual_=` writes `Residual` on `s` (src/spatial/metadata/math/package.scala:27-40).
