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

Current Vitis status: the latest Rust rewrite vendor checkpoint is the
2026-07-02 29-program named serial K-tail lane captured in
`/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-02-k-tail-29-program/`.
The earlier current-head Tile-K facts, partition-helper, schedule-profile,
scheduled Part6 canary, Lab3 raw-wrapper, post-refactor `ScalarSramTileFold v0`,
and refreshed 26-program block-comment/raw-Part5 lanes remain historical
evidence anchors.
It validates the original adapter baseline plus the reusable
scalar/dense/LUT/rank-2-copy/control/stencil/scalar-reduction/scalar-fold
representatives, the local all-ones `MemReduceOnes16` / `MemFoldOnes16`
canaries, `FifoTileScale32`, rank-2 tiled GEMM precursors, fixed-point MemFold,
tail/min MemFold, explicit-inout C MemFold, and the static exact outer-K
in-place C canary, the new exact scheduled Part6 outer-K canary, plus the
Lab1 Part6 `SramTileFoldSum32` SRAM-tile fold canary through Vitis 2025.1
`csim_design` and `csynth_design`.
Exact raw wrappers now exist for Lab1 Part4 FIFO, Lab2 Part1/Part2
MemReduce/MemFold, fixed Lab2 Part5, fixed Lab2 Part6, and the local Lab3
convolution teaching source. The Lab2 Part1/Part2 memory-reduction wrappers
now generate bounded Rust frontend source for `MemReduceOnes16` /
`MemFoldOnes16` and compile through the existing frontend/HIR/classifier path.
The Rust-subset `MemReduceFill v0` / `MemFoldFill v0` frontend now also
accepts literal fill `2` for local `MemReduceTwos16` / `MemFoldTwos16`
canaries with generated HLS C++ and host-harness coverage, while the raw Lab2
wrappers and vendor-proven validation lane remain the exact all-ones shape.
The classifier now also proves the same narrow rank-1 memory-reduction shape
through resolved HIR loop/symbol facts, so equivalent Rust-subset static
length/step aliases are accepted without changing raw Lab2 wrapper matching,
checked payloads, generated HLS, manifests, validation membership, or Vitis
evidence.
The serial Tile-K MemFold path now has a named local K-tail canary,
`MatrixTileMemFoldOuterKTailInPlaceFixPt32x32x34`: the Lab2-like offset-loop
`numel_k = min(TILE_K.to[Int], K - kk)` spelling is preserved as checked
`k_bound` for `K=34`, `K_TILES=3`, and `TILE_K=16`, and HLS emits runtime
bounded K loops while local A/B storage remains statically `TILE_K` wide. This
is now the 29th validation-program member with EC2/Vitis `csim_design` and
`csynth_design` evidence captured in
`/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-02-k-tail-29-program/`.
Except for wrappers that introduced or rode a new canonical validation payload,
these adapters route to existing canaries without adding validation-program
membership or new Vitis evidence. The fixed Lab2
Part5 wrapper canonicalizes to the serial outer-K canary. The fixed Lab2 Part6
wrapper now canonicalizes to
`MatrixTileMemFoldOuterKInPlacePart6ScheduledFixPt32x32x32`, preserving the
exact `par 2` / `par 16` source shape as checked schedule metadata and emitting
the corresponding HLS `PIPELINE`, `UNROLL`, and local-array partition pragmas.
The structural Lab2-like outer-K bridge now reaches that same scheduled Part6
payload for infix tile IO, static offset-loop, and exact static
`numel_k = min(TILE_K.to[Int], K - kk)` source shapes when the partial-tile fill
loops carry literal `par 2` / `par 16`. This remains an equality bridge with no
new validation-program member or emitted-HLS surface, but the exact bridge
commit now has a full 28-program EC2/Vitis refresh in
`/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-02-part6-structural-408e21c/`.
The next exact GEMM canary has landed locally as
`MatrixTileMemFoldOuterKTailInPlacePart6ScheduledFixPt32x32x34`, combining the
named `K=34` serial tail bound with the fixed Part6 `par 2` / `par 16`
schedule. It has parser, checked-IR, manifest, generated-HLS, and native
host-harness coverage, and the HLS emitter uses runtime `numel_k` for the K
load/fold loops while preserving the scheduled array partition, pipeline, and
unroll pragmas. It is not a validation-program member and has no separate
EC2/Vitis evidence yet.
As the next compiler-foundation slice, `ResolvedHir` now carries loop
schedule/identity/nesting facts and resolver-owned affine/index-use facts for
memory accesses, including access occurrence ids, parent-statement joins, and
const-backed affine stride provenance. These facts are observational and
crate-private. The Tile-K LHS-load, RHS-load, C-preload, final-store,
partial-product, and C-accumulation classifier submatchers now consume those
facts as narrow classifier-internal migrations while retaining the existing
syntax guards and exact access/parent-statement checks. The fixed Tile-K
phase-spine guard also cross-checks the recovered `kk_tile -> tile_r -> tile_c`
loop-domain chain, canonical schedule-bound symbols, hoisted or non-hoisted LHS
placement, and fold assignment ancestry through resolver-owned loop/effect
facts, while structural statement recovery remains private and fail-closed. The
C-preload migration is limited to the inout-C copy into `c_tile`, proving
`c_tile[ii, jj] := c[tile_r*TILE_R + ii, tile_c*TILE_C + jj]` through
local/global rank-2 access facts, loop-symbol identity, and const-backed
`TILE_R`/`TILE_C` coefficient-symbol provenance. The final-store migration is
limited to the inout-C writeback from `c_tile`, proving
`c[tile_r*TILE_R + ii, tile_c*TILE_C + jj] := c_tile[ii, jj]` through the same
resolver-owned access grouping, parent-statement, loop-symbol, and
coefficient-symbol provenance. The partial-product migration is limited to
`partial_tile[ii, jj] := lhs_tile[ii, k_idx] * rhs_tile[k_idx, jj]`, proving the
partial write, LHS read, and RHS read through resolver-owned access grouping,
same parent statement, and row/column/K lane symbol identity while retaining the
existing AST operator guard. The C-accumulation migration is limited to
`c_tile[ii, jj] := c_tile[ii, jj] + partial_tile[ii, jj]`, proving the C-tile
write, C-tile read, and partial-tile read through resolver-owned access grouping,
same parent statement, and row/column lane symbol identity while preserving the
existing AST operator guard and accepting the Lab2 MemFold sugar's same-span
sibling loop symbols. The fixed Tile-K phase spine is resolver-guarded, while
broader Tile-K phase recognition beyond that spine still remains unsupported.
The exact raw Lab1 Part6 wrapper is different: it canonicalizes to the new
`SramTileFoldSum32` / `ScalarSramTileFold v0` structural canary, the 27th local
validation member. The local validation list is 29 programs after the separate
scheduled Lab2 Part6 `MatrixTileMemFoldOuterKInPlacePart6ScheduledFixPt32x32x32`
member and the named serial K-tail
`MatrixTileMemFoldOuterKTailInPlaceFixPt32x32x34`, with the latest EC2/Vitis
`csim_design`/`csynth_design` evidence captured in
`docs/vitis-validation/2026-07-02-k-tail-29-program/`. The scheduled K-tail
`MatrixTileMemFoldOuterKTailInPlacePart6ScheduledFixPt32x32x34` remains a
local-only canary until a fresh vendor run promotes it.
These wrappers are not generic Spatial `FIFO`, `Fold`, `MemReduce`, `MemFold`,
GEMM, generic `par`, automatic banking inference, board execution, timing
closure, or broad Scala source compatibility.

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
  `ControlFsm v0`, `Stencil2d v0`, `ScalarReduce v0`, `ScalarFold v0`,
  `Fifo1dTileScalarMul v0`, `ScalarSramTileFold v0`, the local
  `MemReduceFill v0` / `MemFoldFill v0` canaries, including local literal-`2`
  host-HLS canaries outside the Vitis validation lane, and the exact scheduled
  Lab2 Part6 HLS canary
- explicit rejection of unsupported forms

It does not yet prove:

- general Spatial parsing
- reusable lowering for generic `LineBuffer`, `RegFile`, generic reductions,
  generic memory folds/reductions, generic `par`, FIFO/streams, fixed-point,
  or GEMM
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

Historical post-FIFO decision: after the narrow FIFO v0 slice completed with
fresh 19-program Vitis evidence, the next phase became compiler foundation
rather than another ad hoc feature promotion. Current status: the compiler spine
exists, `ResolvedHir` now carries loop/effect/affine/index facts, and the
Tile-K LHS/RHS loads, C-preload, final-store, partial-product, and
C-accumulation submatchers consume those facts. The fixed Tile-K phase spine has
a resolver-backed guard, while broader phase recognition and structural
statement recovery remain fail-closed/private. These fact-consumption slices do
not change generated HLS/manifest output or validation membership. The current
vendor-HLS anchor for the fact-migration line is the fresh 28-program
`docs/vitis-validation/2026-07-02-tile-k-facts-current-head/` current-head
refresh after Tile-K fact consumption and same-span loop-symbol cleanup. The
structural Part6 source bridge is a later equivalence slice over the same
scheduled HLS surface, and its exact commit has its own 28-program vendor-HLS
refresh in `docs/vitis-validation/2026-07-02-part6-structural-408e21c/`.

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
