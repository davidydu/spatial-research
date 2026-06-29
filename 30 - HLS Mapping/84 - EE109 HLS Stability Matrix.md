---
type: hls-mapping
construct: ee109-hls-stability-matrix
category: rework
status: current
date: 2026-06-29
stage: 1D
depends_on:
  - "[[80 - Stage1 EE109 HLS Expansion Plan]]"
  - "[[82 - Lab1Part2 DRAM SRAM Scout]]"
---

# EE109 HLS Stability Matrix

## Scope

This note records the local stability state after the first EE109 HLS expansion pass on the Spatial branch `David/HLS-spatial`.

The supported claim is deliberately narrow: the selected EE109 examples compile through the local Spatial `--hls` lane into HLS-style C++, host-compile with the system `c++`, and pass their generated harnesses. This is not yet a Vitis/Vivado synthesis result.

## Rust Rewrite Vendor HLS Update

On 2026-06-27, the Rust rewrite workspace
`/Users/david/Documents/David_code/spatial-rs` completed a separate Vitis
validation pass for the current accepted adapter set. This is not a Scala
Spatial branch result; it is the Rust rewrite's HLS C++ emitter output.

Environment:

- EC2 host: `[ec2-host — see private/ec2-lane.md]`
- OS: Ubuntu 22.04.5 LTS
- Vitis/Vivado: 2025.1
- Target part: `xc7z020-clg400-1`
- Clock target: 10 ns
- Rust source bundle on EC2:
  `/home/ubuntu/spatial-validation/vitis-20260627-1519/spatial-rs`
- Durable repo evidence:
  `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-06-27/`
- Durable runner replay:
  `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-06-27-runner/`

Rust adapters validated by Vitis `csim_design` and `csynth_design`:

| Adapter | Rust Vitis status | Fmax estimate |
|---|---|---|
| `Lab1Part1RegExample` | Pass | 219.68 MHz |
| `Lab1Part1RegThreeInputExample` | Pass | 156.96 MHz |
| `Lab1Part2DramSramExample` | Pass | 127.15 MHz |
| `Lab2Part3BasicCondFSM` | Pass | 136.99 MHz |
| `Lab2Part4LUT` | Pass | 150.65 MHz |
| `Lab2Part4LUTNonSquareExample` | Pass | 170.24 MHz |
| `Lab3Part0MatrixCopyRowMajor` | Pass | 136.99 MHz |
| `Lab3Part1Convolution` | Pass | 136.99 MHz |

Boundary: this validates exact Rust adapter bundles through Vitis C simulation
and HLS synthesis. It does not validate board execution, Vivado
implementation/place-and-route, post-implementation timing closure, or generic
Spatial feature support beyond these adapter shapes.

Follow-up supported-feature run:

On 2026-06-27, the Rust rewrite added `ScalarExpr v0` as the first reusable
supported feature and re-ran the Vitis lane. The validation list now contains
the same eight accepted adapters plus `ScalarAffine4`, a non-lab representative
for scalar integer expressions. All nine completed with return code 0,
`csim=true`, and `csynth=true`.

Additional repo evidence:

- `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-06-27-scalar-expr/`

`ScalarExpr v0` covers a narrow scalar language: 1-4 scalar `Int` inputs, one
scalar `Int` output, one assignment, declared-input reads, nonnegative integer
literals, `+`, `*`, and parentheses. It still excludes DRAM, memories, control
flow, comparisons, muxes, negative literals, subtraction, division, function
calls, multiple outputs, and multiple statements.

Follow-up dense-memory supported-feature run:

On 2026-06-27, the Rust rewrite added `Dense1dScalarMul v0` as the second
reusable supported feature and re-ran the Vitis lane. The validation list now
contains the same eight accepted adapters plus `ScalarAffine4` and
`DenseScale64`, a non-lab representative for rank-1 tiled DRAM/SRAM
scalar-multiply. All ten completed with return code 0, `csim=true`, and
`csynth=true`.

Additional repo evidence:

- `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-06-27-dense1d/`

`Dense1dScalarMul v0` covers one rank-1 `Dram<Int>[N]` input, one scalar `Int`
multiplier, one rank-1 `Dram<Int>[N]` output, two rank-1 `Sram<Int>[TILE]`
tiles, positive static `N`/`TILE` with `N % TILE == 0`, unit-stride load,
elementwise multiply, and unit-stride store. It still excludes generic memory
lowering, rank-2 DRAM, dynamic/tail tiles, non-unit strides, extra memories,
arbitrary expressions, FIFO/streams, reductions, aliasing/in-place claims, and
non-`Int` element types.

Follow-up LUT supported-feature run:

On 2026-06-27, the Rust rewrite added `LutLookup v0` as the third reusable
supported feature and re-ran the Vitis lane. The validation list now contains
the same eight accepted adapters plus `ScalarAffine4`, `DenseScale64`, and
`LutBiasLookup`, a non-lab representative for 2-D row-major LUT lookup. All
eleven completed with return code 0, `csim=true`, and `csynth=true`.

Additional repo evidence:

- `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-06-27-lut-lookup/`

`LutLookup v0` covers one 2-D `Lut<Int>[R, C]`, three scalar `Int` inputs
ordered as bias, row, and column, one scalar `Int` output, a rectangular
row-major literal payload, and exactly `out := bias + table[row, col]`. It
still excludes generic table/memory indexing, DRAM, multiple LUTs, computed
indices, swapped row/column roles, arbitrary scalar expressions around the
lookup, runtime bounds checks, dynamic dimensions, and non-`Int` element types.

Follow-up rank-2 copy supported-feature run:

On 2026-06-27, the Rust rewrite added `Dram2dCopy v0` as the fourth reusable
supported feature and re-ran the Vitis lane. The validation list now contains
the same eight accepted adapters plus `ScalarAffine4`, `DenseScale64`,
`LutBiasLookup`, and `MatrixCopy4x6`, a non-lab representative for rank-2
row-major DRAM copy. All twelve completed with return code 0, `csim=true`, and
`csynth=true`.

Additional repo evidence:

- `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-06-27-dram2d-copy/`

`Dram2dCopy v0` covers one rank-2 `Dram<Int>[ROWS, COLS]` input, one matching
rank-2 output, nested static `foreach` row/column loops, and exactly
`out[row, col] := in[row, col]`. It still excludes generic memory/effect
lowering, rank polymorphism, swapped or computed indices, mismatched shapes,
extra ports/statements, aliasing/in-place claims, stencils, reductions, `par`,
dynamic dimensions, and non-`Int` element types. The original
`Lab3Part0MatrixCopyRowMajor` adapter now routes through the
frontend/HIR/classifier path; `Lab3Part1Convolution` remains an explicit
opaque adapter.

The `2026-06-27-runner` replay used the repo-local `run-vitis-validation`
command. It defaults to plan-only sidecar generation and requires `--execute`
to run Vitis. The EC2 host's system Cargo was 1.75.0, so the copied remote
bundle used a remote-only lockfile v4-to-v3 downgrade; the local Rust repo
lockfile was not changed. The `2026-06-27-dram2d-copy` run used the same
remote-only lockfile adjustment.

Follow-up control, Lab3 frontend/HIR, and Stencil2d runs:

By 2026-06-28, the Rust rewrite had added three more relevant milestones:

- `ControlFsm v0`, represented by `ControlFsm32`, with evidence in
  `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-06-28-control-fsm-v0/`.
- Lab3 convolution frontend/HIR routing for the fixed adapter, with evidence in
  `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-06-28-lab3-frontend-hir/`.
- `Stencil2d v0`, represented by `SobelStencil12x20`, with fourteen-program
  Vitis `csim_design` and `csynth_design` evidence in
  `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-06-28-stencil2d-v0/`.

The `Stencil2d v0` run was executed from Rust commit `2ec05e6` on branch
`David/rust-ee109-mvp`, using EC2 host
`[ec2-host — see private/ec2-lane.md]`, Vitis/Vivado 2025.1, target
`xc7z020-clg400-1`, and 10 ns clock target. All fourteen validation programs
completed with return code 0, `csim=true`, and `csynth=true`; the new
`SobelStencil12x20` representative reported an estimated Fmax of 136.99 MHz.
The remote run again used a remote-only Cargo.lock v4-to-v3 compatibility
adjustment for Cargo 1.75; the local Rust repo lockfile was not changed.

`Stencil2d v0` covers a narrow Sobel-like rank-2 `Int` stencil: one input DRAM,
one matching output DRAM, two static 3x3 Sobel LUTs, one row scratch SRAM,
Lab3-style local-window source classification, top-left zero border, and
`abs(first) + abs(second)` arithmetic. It still does not claim generic
`LineBuffer`, `RegFile`, arbitrary `Reduce`, arbitrary `par`, arbitrary
coefficients, dynamic dimensions, optimized line-buffer scheduling, board
execution, Vivado implementation, place-and-route, or timing closure.

Follow-up scalar-reduction supported-feature run:

On 2026-06-28, the Rust rewrite added `ScalarReduce v0` as the seventh reusable
supported feature and re-ran the Vitis lane. The validation list now contains
the same eight accepted adapters plus `ScalarAffine4`, `ScalarReduceSum16`,
`DenseScale64`, `LutBiasLookup`, `MatrixCopy4x6`, `ControlFsm32`, and
`SobelStencil12x20`. All fifteen completed with return code 0, `csim=true`,
and `csynth=true`.

Additional repo evidence:

- `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-06-28-scalar-reduce-v0/`

`ScalarReduce v0` covers exactly one scalar `Int` output assigned by
`out := reduce i in 0..N par P { i }` with static `1 <= N <= 65536`,
`P == 1`, no inputs, no DRAM ports, and no local memories. It rejects
output-name collisions with generated HLS temporaries and overflow-sized `N`.
It still does not claim generic `Reduce`, `Fold`, `MemReduce`, `MemFold`,
arbitrary reduce bodies, input-DRAM reductions, non-unit `par`, unbounded `Int`
accumulation, board execution, Vivado implementation, place-and-route, or
timing closure.

Follow-up scalar-fold supported-feature run:

On 2026-06-28, the Rust rewrite added `ScalarFold v0` as the eighth reusable
supported feature and re-ran the Vitis lane. The validation list now contains
the same eight accepted adapters plus `ScalarAffine4`, `ScalarReduceSum16`,
`ScalarFoldTileSum32`, `DenseScale64`, `LutBiasLookup`, `MatrixCopy4x6`,
`ControlFsm32`, and `SobelStencil12x20`. All sixteen completed with return
code 0, `csim=true`, and `csynth=true`.

Additional repo evidence:

- `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-06-28-scalar-fold-v0/`

`ScalarFold v0` covers exactly one rank-1 `Dram<Int>[N]` input and one scalar
`Int` output assigned by a tiled fold around a rank-1 indexed reduction:
`out := fold outer in 0..N step TILE { reduce inner in 0..TILE par P { src[outer + inner] } }`.
It requires static `1 <= N <= 65536`, `TILE > 0`, `N % TILE == 0`, and
`P == 1`. It still does not claim generic `Fold`, generic `Reduce`,
`MemReduce`, `MemFold`, arbitrary bodies, tail tiles, rank-2 inputs,
non-unit `par`, unbounded `Int` accumulation, board execution, Vivado
implementation, place-and-route, or timing closure.

Follow-up memory-reduction semantic-canary run:

On 2026-06-28, the Rust rewrite added the local all-ones `MemReduceFill v0` and
`MemFoldFill v0` semantic canaries and re-ran the Vitis lane. The validation
list now contains 18 programs, adding `MemReduceOnes16` and `MemFoldOnes16` to
the prior sixteen-program ScalarFold checkpoint. All eighteen completed with
return code 0, `csim=true`, and `csynth=true`.

Additional repo evidence:

- `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-06-28-mem-reductions-v0/`

`MemReduceFill v0` and `MemFoldFill v0` cover narrow Rust-DSL all-ones local
SRAM accumulation shapes for the simple Lab2 memory-reduction behaviors. They
do not claim original Scala source compatibility, arbitrary reducer/fold
bodies, rank-2 memory reductions, GEMM, fixed-point arithmetic, banking,
streams, scheduling, board execution, Vivado implementation, place-and-route,
or timing closure.

Follow-up FIFO semantic-canary run:

On 2026-06-28, the Rust rewrite added `Fifo1dTileScalarMul v0` and re-ran the
Vitis lane. The validation list now contains 19 programs, adding
`FifoTileScale32` to the prior eighteen-program MemReduce/MemFold checkpoint.
All nineteen completed with return code 0, `csim=true`, and `csynth=true`.

Additional repo evidence:

- `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-06-28-fifo-v0/`

`Fifo1dTileScalarMul v0` covers a narrow Rust-DSL Lab1 Part4-style tile-scale
shape: one rank-1 DRAM input, one scalar multiplier, one rank-1 DRAM output,
two loop-local `FIFO<Int>[TILE]` memories, ordered enqueue/dequeue tile
scaling, and generated `hls::stream<int>` plus stream-depth pragmas. It does
not claim original Scala `Lab1Part4FIFOExample` source compatibility, generic
FIFO/streams, AXI stream ports, LIFO, back-pressure modeling, throughput
optimization, board execution, Vivado implementation, place-and-route, or
timing closure. The Scala HLS negative row below remains true for the legacy
Scala backend/source path.

Follow-up rank-2 tiled int scale run:

On 2026-06-29, the Rust rewrite added `Dense2dTileScalarMul v0` and re-ran
the Vitis lane. The validation list now contains 20 programs, adding
`MatrixTileScale4x6` to the prior nineteen-program FIFO checkpoint. All twenty
completed with return code 0, `csim=true`, and `csynth=true`.

Additional repo evidence:

- `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-06-29-rank2-tiled-int-scale/`

`Dense2dTileScalarMul v0` covers a narrow Rust-DSL rank-2 tiled local-SRAM
integer scale shape: one rank-2 input DRAM, one scalar multiplier, one matching
rank-2 output DRAM, two rank-2 SRAM tiles, exact row/column tile loops, and
load/compute/store phases. The `MatrixTileScale4x6` representative reported
`PASS MatrixTileScale4x6`, an estimated Fmax of 122.68 MHz, and an estimated
clock of 8.151 ns. This evidence does not claim GEMM, fixed-point arithmetic,
tail tiles, generic rank-2 tiling, arbitrary local-memory programs, Scala
source compatibility, board execution, Vivado implementation, place-and-route,
or timing closure.

Follow-up rank-2 tiled dot-accum run:

On 2026-06-29, the Rust rewrite added `Dense2dTileDotAccum v0` and re-ran the
Vitis lane. The validation list now contains 21 programs, adding
`MatrixTileAccum4x6x5` to the prior twenty-program rank-2 tile-scale
checkpoint. All twenty-one completed with return code 0, `csim=true`, and
`csynth=true`.

Additional repo evidence:

- `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-06-29-rank2-tiled-dot-accum/`

`Dense2dTileDotAccum v0` covers a fixed-shape Rust-DSL rank-2 tiled `Int`
dot-accumulation canary: two rank-2 input DRAMs `lhs[ROWS,K]` and
`rhs[K,COLS]`, one matching rank-2 output DRAM `out[ROWS,COLS]`, three SRAM
tiles, explicit accumulator zero-init, one static K reduction loop, and
row-major flattened HLS offsets. The `MatrixTileAccum4x6x5` representative
reported `PASS MatrixTileAccum4x6x5`, an estimated Fmax of 121.61 MHz, an
estimated clock of 8.223 ns, latency 84 cycles, and utilization estimate 4
BRAM_18K, 6 DSP, 5013 FF, and 4537 LUT. This evidence does not claim original
Scala `Lab2Part5GEMM`/`Lab2Part6GEMM` source compatibility, fixed-point
arithmetic, tail/min bounds, K tiling, buffered `MemFold`, `par`, generic
GEMM, board execution, Vivado implementation, place-and-route, or timing
closure.

## Stable Positive Examples

| Example | Surface covered | Local HLS status | Scala parity status |
|---|---|---|---|
| `spatial.tests.ee109.Lab1Part1RegExample` | Two scalar `ArgIn[Int]`, scalar `ArgOut[Int]`, integer add | Pass | Pass |
| `spatial.tests.ee109.Lab1Part1RegThreeInputExample` | Three scalar `ArgIn[Int]`, scalar `ArgOut[Int]`, nested integer add | Pass | Pass |
| `spatial.tests.ee109.Lab1Part2DramSramExample` | One input DRAM, one output DRAM, one scalar arg, fixed 32-element dense tiled load/compute/store | Pass | Pass |
| `spatial.tests.ee109.Lab2Part4LUT` | Constant 2-D integer LUT, row-major lookup, vector width one | Pass | Pass |
| `spatial.tests.ee109.Lab2Part4LUTNonSquareExample` | Non-square constant LUT stride check | Pass | Pass |

## Fail-Closed Negative Examples

| Example | Rejected surface | Expected status |
|---|---|---|
| `spatial.tests.compiler.HLSRejectsUnsupportedFSM` | Basic conditional FSM/control state machine | Fails with `[hlsgen]` diagnostics |
| `spatial.tests.compiler.HLSRejectsUnsupportedLab1FIFO` | FIFO construction, enqueue, dequeue | Fails with `[hlsgen]` diagnostics |
| `spatial.tests.compiler.HLSRejectsUnsupportedLab1Reduce` | Fold/reduction accumulator surface | Fails with `[hlsgen]` diagnostics |
| `spatial.tests.compiler.HLSRejectsUnsupportedLab3LocalMemories` | RegFile/local memory surface representative of later Lab3 work | Fails with `[hlsgen]` diagnostics |

## Verification Run

Positive and negative local HLS gate:

```bash
SBT_OPTS='-Xmx8G -XX:+UseG1GC' sbt -Dtest.HLS=true '; project spatial; compile; project test; testOnly spatial.tests.ee109.Lab1Part1RegExample spatial.tests.ee109.Lab1Part1RegThreeInputExample spatial.tests.ee109.Lab1Part2DramSramExample spatial.tests.ee109.Lab2Part4LUT spatial.tests.ee109.Lab2Part4LUTNonSquareExample spatial.tests.compiler.HLSRejectsUnsupportedFSM spatial.tests.compiler.HLSRejectsUnsupportedLab1FIFO spatial.tests.compiler.HLSRejectsUnsupportedLab1Reduce spatial.tests.compiler.HLSRejectsUnsupportedLab3LocalMemories'
```

Result: 9 suites completed, 9 tests succeeded, 0 failed.

Positive Scala parity gate:

```bash
SBT_OPTS='-Xmx8G -XX:+UseG1GC' sbt -Dtest.Scala=true '; project spatial; compile; project test; testOnly spatial.tests.ee109.Lab1Part1RegExample spatial.tests.ee109.Lab1Part1RegThreeInputExample spatial.tests.ee109.Lab1Part2DramSramExample spatial.tests.ee109.Lab2Part4LUT spatial.tests.ee109.Lab2Part4LUTNonSquareExample'
```

Result: 5 suites completed, 5 tests succeeded, 0 failed.

Generated-code hygiene:

- No empty generated HLS kernel files were found under `gen/HLS`.
- No positive HLSGen error logs were found for the five supported examples.
- Generated HLS C++ did not contain simulator-only strings such as `FringeContext`, `TopHost`, `Chisel`, `Verilog`, `DRAMSim`, `vcs`, or `instrument`.
- `git diff --check` passed in the Spatial repo.

## Current Limitations

- The original Scala Spatial HLS gate remains a local host-C++ gate. It does
  not invoke Vitis/Vivado HLS, synthesize RTL, check timing, or validate board
  integration.
- For the Rust rewrite, the selected accepted adapters, eleven reusable
  supported-feature representatives, and two local memory-reduction canary
  representatives now have Vitis `csim_design` and `csynth_design` evidence.
  Board execution, Vivado implementation, timing closure, and broad Spatial
  coverage remain pending.
- The Lab1Part2 memory lowering is a narrow structural slice, not a general Spatial memory backend. It accepts the selected fixed shape: `N = 32`, `tileSize = 16`, one input DRAM, one output DRAM, two 16-element SRAM tiles, one scalar integer multiplier, and dense unit-stride transfers.
- The Lab1Part2 generated harness uses an independent vector oracle, but the source initialization is currently fixed to the selected EE109 shape `src(i) = i % 256`.
- FIFO, generic reductions/folds, generic memory reductions/folds, generic
  FSMs, generic RegFile/LineBuffer lowering, dynamic sizes, non-unit strides,
  and non-`Int` element types remain unsupported in HLS mode and should stay
  fail-closed until selected intentionally.
- The Scala runs still emit the existing `libisl appears to be missing` warning. That warning does not block these local regression results, but it is separate from vendor HLS readiness.

## Recommended Next Action

For the Rust rewrite, the next action is to choose the next GEMM precursor on
top of `Dense2dTileDotAccum v0`: fixed-point arithmetic, tail/min bounds, a
narrow buffered `MemFold` tile, or a controlled `par` variant. Keep FIFO,
reduction, stencil, rank-2 tile-scale, and dot-accum surfaces as regression
anchors, and rerun Vitis only when generated HLS C++ or validation membership
changes.
