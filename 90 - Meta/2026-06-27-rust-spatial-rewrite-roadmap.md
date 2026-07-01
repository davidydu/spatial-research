---
type: design
project: spatial-spec
date: 2026-06-27
status: active
related:
  - "[[2026-06-26-rust-first-spatial-dsl-overlay]]"
  - "[[2026-06-26-rust-ee109-mvp-design]]"
  - "[[2026-06-27-rust-lab3-convolution-slice-contract]]"
  - "[[84 - EE109 HLS Stability Matrix]]"
  - "[[60 - EE109 HLS Lowering Map]]"
---

# Rust Spatial Rewrite Roadmap

## Framing

The long-term goal is a Rust rewrite of Spatial with HLS C++ as the primary backend. EE109 labs are the first acceptance ladder because they are concrete teaching examples, but they are not the final compiler boundary.

The current `spatial-rs` work should therefore be treated as a tracer slice:

- keep the working host-C++ fixture adapters as regression evidence
- avoid growing the compiler by adding endless exact lab recognizers
- promote lab adapters into reusable frontend, HIR, IR, lowering, and HLS modules
- preserve fail-closed diagnostics until a construct has a selected semantic and HLS story

## Current Position

`spatial-rs` currently has accepted fixture adapters for scalar add, dense 1-D DRAM/SRAM multiply, LUTs, one exact FSM, rank-2 copy groundwork, and one direct Lab3 convolution semantic adapter.

Current Vitis status: the latest Rust rewrite Vitis checkpoint is still the
2026-07-01 refreshed 26-program lane through `Dense2dTileKMemFold v0`. It
validates the original adapter baseline plus the reusable
scalar/dense/LUT/rank-2-copy/control/stencil/scalar-reduction/scalar-fold
representatives, the local all-ones `MemReduceOnes16` / `MemFoldOnes16`
canaries, `FifoTileScale32`, rank-2 tiled GEMM precursors, fixed-point MemFold,
tail/min MemFold, explicit-inout C MemFold, and the static exact outer-K
in-place C canary through Vitis 2025.1 `csim_design` and `csynth_design`.
Exact raw wrappers now exist for Lab1 Part4 FIFO, Lab2 Part1/Part2
MemReduce/MemFold, and fixed Lab2 Part5, and those canonicalize to existing
canaries without adding validation-program membership or new Vitis evidence.
The exact raw Lab1 Part6 wrapper is different: it canonicalizes to the new
`SramTileFoldSum32` / `ScalarSramTileFold v0` structural canary, so the local
validation list is now 27 programs with host-C++ and plan-only coverage. EC2
Vitis for that 27-program lane is pending.
These wrappers are not generic Spatial `FIFO`, `Fold`, `MemReduce`, `MemFold`,
GEMM, `par`, scheduling, banking, board execution, timing closure, or broad
Scala source compatibility.

`ScalarExpr v0` is the first reusable supported feature rather than an exact
fixture adapter. It covers one scalar integer assignment over 1-4 scalar inputs
with nonnegative literals, `+`, `*`, and parentheses. The non-lab
`ScalarAffine4` representative has passed local host-C++ and Vitis
`csim_design`/`csynth_design`.

`Dense1dScalarMul v0` is the second reusable supported feature. It covers one
rank-1 DRAM input, one scalar multiplier, one rank-1 DRAM output, two rank-1
SRAM tiles, positive static `N`/`TILE` with `N % TILE == 0`, and unit-stride
tiled load/compute/store. The non-lab `DenseScale64` representative has passed
local host-C++ and Vitis `csim_design`/`csynth_design`.

Dense 1-D DRAM/SRAM syntax no longer enters HIR as a fused whole-kernel marker.
The accepted dense path now parses and lowers through generic
`SequentialForeach`, loop-local SRAM, load, inner `Foreach`, indexed
assignment, and store nodes before the classifier reconstructs the same checked
dense adapter/feature programs. This is a frontend/HIR foundation step, not
generic loop scheduling or arbitrary memory lowering.

`LutLookup v0` is the third reusable supported feature. It covers one 2-D
integer LUT, scalar bias/row/column inputs, one scalar output, a rectangular
row-major literal payload, and exactly `out := bias + table[row, col]`. The
non-lab `LutBiasLookup` representative has passed local host-C++ and Vitis
`csim_design`/`csynth_design`.

`Dram2dCopy v0` is the fourth reusable supported feature. It covers one rank-2
DRAM input, one matching rank-2 DRAM output, nested static row/column
`foreach` loops, and exactly `out[row, col] := in[row, col]`. The non-lab
`MatrixCopy4x6` representative has passed local host-C++ and Vitis
`csim_design`/`csynth_design`, and the original
`Lab3Part0MatrixCopyRowMajor` adapter now routes through the
frontend/HIR/classifier path instead of compact-source equality.

`spatial_rs_core::memory::Access` is the first shared checked memory-access
primitive. It centralizes rank-1/rank-2 positive-shape validation, index-rank
matching, and row-major C offset rendering for the rank-2 DRAM copy emitter.
This is an architectural foundation step only; it does not yet provide generic
effect scheduling, alias analysis, FSM/control lowering, stencil lowering, or
broad memory lowering.

Rank-2 copy is also the first path lowered through a crate-private
`HlsKernelPlan` before C++ rendering. The plan uses manifest-derived ABI facts
and the shared row-major index expression, but it is not yet a generic HLS MIR
or scheduler.

This proves useful local compiler plumbing:

- checked Rust construction
- ABI manifest emission
- independent oracles
- HLS-style C++ emission
- local host-C++ harness compile/run
- Vitis C simulation and HLS synthesis for the original adapter baseline,
  `ScalarExpr v0`, `Dense1dScalarMul v0`, `LutLookup v0`, `Dram2dCopy v0`,
  `ControlFsm v0`, `Stencil2d v0`, `ScalarReduce v0`, `ScalarFold v0`, and
  the local `MemReduceFill v0` / `MemFoldFill v0` canaries
- explicit rejection of unsupported forms

It does not yet prove:

- general Spatial parsing
- reusable lowering for generic `LineBuffer`, `RegFile`, generic reductions,
  generic memory folds/reductions, `par`, FIFO/streams, fixed-point, or GEMM
- generic memory/effect lowering beyond the selected dense and rank-2 copy
  shapes
- timing, resource, RTL, or board readiness

## Architecture Target

```text
accel! DSL source
  -> lexer/parser
  -> AST with spans
  -> typed Spatial HIR
  -> subset classifier and validators
  -> checked semantic IR
  -> manifest, ABI, partition, schedule, and provenance ledgers
  -> HLS lowering passes
  -> HLS C++ kernel and harness emission
  -> local host-C++ gate
  -> Vitis/Vivado csim and csynth gates
```

The student surface should remain a hardware DSL island. Rust is the compiler implementation language, not the language students need to master before learning hardware design.

## Vocabulary

- `accepted fixture adapter`: exact lab-shaped program accepted and checked through host-C++.
- `supported feature`: reusable semantic module with lab and non-lab tests, legal parameter perturbations, fail-closed negatives, and non-template HLS lowering.
- `host_cpp_structural_gate`: generated kernel and harness compile/run with the local system compiler.
- `vitis_csim_validated`: generated Vitis/Vivado project runs `csim_design`.
- `vitis_csynth_validated`: generated Vitis/Vivado project runs `csynth_design`, and reports record tool version, part, clock, latency, resource use, and accepted II.

Use `accepted fixture adapter` for the current `ProgramKind::LabX...` style cases unless a feature has graduated through reusable semantics.

## Feature Ladder

1. Scalar integer ports and arithmetic.
2. Dense 1-D DRAM/SRAM load-compute-store.
3. LUT lookup and row-major indexing.
4. FIFO and stream lowering.
5. Scalar `Fold` and `Reduce`.
6. `MemReduce` and `MemFold`.
7. FSMs with conditions, state updates, SRAM writes, and mux-like expressions.
8. 2-D DRAM/SRAM, fixed-point types, dynamic dimensions, and GEMM tiling.
9. Local-window/stencil lowering for `LineBuffer`, `RegFile`, `Reduce`, `mux`, `abs`, and `par`.
10. HLS performance surface: `PIPELINE`, `UNROLL`, `ARRAY_PARTITION`, vector ports, project Tcl, and report parsing.

## Near-Term Manager Plan

Post-FIFO decision: the narrow FIFO v0 slice is complete with fresh
19-program Vitis evidence, so the next phase is compiler foundation rather
than another ad hoc feature promotion. The active plan is
`[[2026-06-28-post-fifo-compiler-foundation-plan]]`: add an explicit
source-to-HIR-to-checked-`Program` compiler spine, add crate-private HIR facts
for local memories and effects, use FIFO as the first production consumer of
those facts, then route parser diagnostics through stage-aware compiler
errors. Generic FIFO/streams, GEMM, fixed-point, broader reductions, and board
or timing claims should wait until the HIR facts and future `ResolvedHir`
boundary are stable.

ResolvedHir update: the reviewed design now lives in the Rust repo as
`docs/superpowers/specs/2026-06-28-resolved-hir-design.md`. It preserves checked
`Program` as the HLS contract, reserves resolver diagnostics to
`spatial:E0301` through `spatial:E0310`, and makes the next implementation slice
crate-private and test-first so HLS output and validation membership stay
unchanged.

The already-completed foundation items below remain useful historical context:

1. Reword repo docs so they describe the Rust rewrite correctly and stop overclaiming fixture adapters as general support.
2. Add a source model for `parse_accel(&str)`: source id, byte ranges, line/column lookup, and diagnostic labels. Keep `macro_rules! accel` on `stringify!` until a proc-macro is worth its cost.
3. Add a real frontend path: tokenization, AST, source spans, and typed HIR for scalar ports, LUTs, dense 1-D DRAM/SRAM, expressions, loops, loads, and stores.
4. Add a first-class EE109 subset classifier that consumes HIR and produces checked semantic modules or fixture adapters.
5. Decouple semantic feature identity from lab kernel names before adding non-lab semantic-equivalent tests.
6. Route scalar/LUT/dense/rank-2 copy accepted adapters through `AST -> HIR -> EE109 subset classifier -> checked Program` while keeping current host-C++ outputs stable.
7. Keep Lab3 convolution explicitly transitional and opaque until reusable local-window/stencil lowering exists.
8. Add HLS project artifact generation in dry-run mode: top name, part, clock, kernel/harness paths, and `run_hls.tcl`.
9. Use the EC2 Vitis lane as a regular gate for every promoted supported-feature slice.
10. Extend the new memory foundation toward checked `Shape`/effect/layout views
   shared by validation, manifesting, and HLS lowering.
11. Extend the new HLS plan seam beyond rank-2 copy to dense/LUT/scalar only
   after exact output-preservation tests are in place.
12. Factor shared loop, memory, expression, and control structure before promoting FIFO, reductions, FSM variants, or Lab3-style performance/synthesis readiness.

## Guardrails

- No new `compact_source(EXACT_FIXTURE)` cases outside a clearly named fixture-adapter layer.
- No new `ProgramKind::LabX...` without a retirement criterion.
- No generic support claim until there is at least one non-lab semantic test.
- No vendor HLS claim without fresh tool evidence.
- No direct port of Scala `HLSGen`; preserve its useful semantics and fixtures, but design Rust modules around frontend, HIR, validation, manifests, lowering, diagnostics, and HLS emission.
