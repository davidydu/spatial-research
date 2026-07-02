---
type: hls-mapping
construct: ee109-hls-stability-matrix
category: rework
status: current
date: 2026-07-02
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

Later raw-wrapper source-adapter updates:

On 2026-07-02, the Rust rewrite promoted the known local `Lab2Part6GEMM` lab
class from source-compatibility-only to a distinct scheduled HLS canary. The
exact fixed `32x32x32`, tile-16, `FixPt[TRUE,_24,_8]`, single-`Accel` token
stream with `par 2` / `par 16` partial-tile loops now canonicalizes to
`MatrixTileMemFoldOuterKInPlacePart6ScheduledFixPt32x32x32`, carrying checked
`partial_row_par = 2` and `partial_col_par = 16` schedule metadata. The HLS
branch emits local-array partition pragmas, `PIPELINE II=1`, and row/column
unroll pragmas for the partial-tile multiply and fold-update loops. A fresh
28-program EC2/Vitis 2025.1 run completed with return code 0 for every
validation program; evidence is captured under
`/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-02-lab2-part6-scheduled/`.
This proves the exact Part6 scheduled canary through `csim_design` and
`csynth_design`, but it does not claim generic Spatial `par`, automatic banking
inference, generic Spatial `MemFold`, dynamic/tail K, K tails, or broad Scala
source compatibility.

Later on 2026-07-02, the Rust rewrite added a local structural source bridge
for that same scheduled Part6 payload. The Lab2-like outer-K frontend/HIR path
now accepts infix tile IO, static offset-loop spelling, and the exact static
`numel_k = min(TILE_K.to[Int], K - kk)` spelling when the kernel name is the
scheduled Part6 canary and the partial-tile fill loops carry literal `par 2`
and `par 16`. Local parser/HIR/classifier tests prove equality with the raw
Part6 scheduled payload, and HLS tests prove generated C++ and manifest
identity. This bridge does not add validation-program membership or fresh
EC2/Vitis evidence because the emitted HLS surface is unchanged.

On 2026-07-01, the Rust rewrite added source adapters for the
known local `Lab2Part1SimpleMemReduce` and `Lab2Part2SimpleMemFold` lab
classes. These wrappers canonicalize to the existing `MemReduceOnes16` and
`MemFoldOnes16` payloads and local tests prove generated HLS/manifest equality.
The current adapter is accelerator-shape based rather than whole-file-token
based: it requires the exact class name, `out = DRAM[Int](16)` declaration, a
single exact all-ones `Accel` body, and explicit zero initialization for
`MemFold`, while allowing host-side print/gold scaffolding to vary. This is not
new Vitis evidence and does not broaden the historical MemReduce/MemFold Vitis
checkpoint. Changed output shape, changed accelerator body, generic Spatial
`MemReduce`/`MemFold`, arbitrary reducer/fold bodies, dynamic bounds, rank-2
reductions, scheduling, banking, broad Scala source compatibility, board
execution, Vivado implementation, place-and-route, and timing closure remain
unsupported.

On 2026-07-01, the Rust rewrite also added an exact raw source adapter for the
known local teaching `Lab3Part1Convolution` wrapper from
`/Users/david/Documents/David_code/lab-3-accelerator-bandits/src/test/scala/Lab3.scala`.
It canonicalizes to the existing fixed `Lab3Part1Convolution` / `Stencil2d`
payload and local tests prove parser equality plus generated HLS/manifest
equality. A fresh current-head 27-program EC2/Vitis run now also proves the
canonical Lab3 payload still passes `csim_design` and `csynth_design` with this
adapter code present; evidence is captured in
`/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-01-lab3-local-raw-wrapper/`.
This does not add a separate raw-wrapper validation program or broaden the
historical Lab3 payload claim. Changed dimensions, changed accelerator shape,
generic Scala `LineBuffer`, `RegFile`, `Reduce`, generalized rotated-kernel
handling, dynamic dimensions, optimized line-buffer scheduling, broad source
compatibility, board execution, Vivado implementation, place-and-route, and
timing closure remain unsupported.

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
not claim generic Scala FIFO source compatibility, generic FIFO/streams, AXI
stream ports, LIFO, back-pressure modeling, throughput optimization, board
execution, Vivado implementation, place-and-route, or timing closure. A later
exact raw `Lab1Part4FIFOExample` wrapper now token-matches only the known fixed
Lab1 Part4 source and canonicalizes to this same `FifoTileScale32` payload with
HLS/manifest equality; it is not new Vitis evidence and does not broaden the
historical FIFO Vitis checkpoint. The Scala HLS negative row below remains true
for the legacy Scala backend/source path.

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

Follow-up rank-2 tiled MemFold-style checkpoint:

On 2026-06-29, the Rust rewrite added `Dense2dTileMemFold v0` as a fixed-shape
Rust-DSL `Int` source-shape GEMM precursor. The validation list now contains
22 programs, adding `MatrixTileMemFold4x6x5` to the prior twenty-one-program
rank-2 dot-accum checkpoint. This checkpoint has local host-C++ harness
coverage and was later included in the 23-program EC2 Vitis execution run
recorded under
`/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-06-29-fixpt-memfold/`.

`Dense2dTileMemFold v0` covers three rank-2 input DRAMs `lhs[ROWS,K]`,
`rhs[K,COLS]`, and `cin[ROWS,COLS]`, one output DRAM `out[ROWS,COLS]`, four
SRAM tiles, C preload into `c_tile`, a `partial_tile = lhs_tile * rhs_tile`
phase, `c_tile += partial_tile` over one static K loop, and row-major flattened
HLS offsets. This moves closer to the EE109 Lab2 GEMM `tileC_sram.buffer` /
`MemFold` lifecycle, but it does not claim original Scala `Lab2Part5GEMM` or
`Lab2Part6GEMM` source compatibility, generic Spatial `MemFold`, fixed-point
arithmetic beyond the exact canary below, tail/min bounds, K tiling, `par`,
banking, performance scheduling, board execution, Vivado implementation,
place-and-route, or timing closure.

Follow-up exact fixed-point MemFold canary checkpoint:

On 2026-06-29, the Rust rewrite added exact `FixPt[TRUE,_24,_8]` support for
the same fixed-shape `Dense2dTileMemFold v0` GEMM precursor. The validation
list now contains 23 programs, adding `MatrixTileMemFoldFixPt4x6x5` after the
`Int` MemFold representative. This checkpoint has local Rust tests, local
host-C++ harness coverage through a host-only `ap_fixed` shim, Vitis
dry-run/plan-only sidecar coverage, and EC2 Vitis 2025.1 `csim_design` plus
`csynth_design` evidence.

The 23-program EC2 run completed with return code 0 on
`[ec2-host — see private/ec2-lane.md]` using
`/tools/Xilinx/2025.1/Vitis/settings64.sh`; every validation program reported
`csim=true` and `csynth=true`. `MatrixTileMemFoldFixPt4x6x5` passed C
simulation with `PASS MatrixTileMemFoldFixPt4x6x5`, finished synthesis, and
reported estimated Fmax 121.61 MHz, estimated clock 8.223 ns, latency 84
cycles, interval 60 cycles, and utilization estimate 6 BRAM_18K, 8 DSP, 6457
FF, and 5919 LUT.

The fixed-point slice widens the Rust frontend/HIR/IR/manifest/HLS type spine
by one concrete type only. All DRAM ports and local SRAM tiles in the accepted
MemFold GEMM canary must use the same element type, either `Int` or exact
`FixPt[TRUE,_24,_8]`; the HLS emitter lowers the latter to `ap_fixed<32, 24>`
with a stable local alias. This evidence does not claim generic fixed-point
widths, decimal fixed-point values, mixed `Int`/`FixPt` GEMM, original Scala
`Lab2Part5GEMM` or `Lab2Part6GEMM` source compatibility, generic Spatial
`MemFold`, tail/min bounds, K tiling, `par`, banking, performance scheduling,
board execution, Vivado implementation, place-and-route, or timing closure.

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
- For the Rust rewrite, the explicitly listed accepted adapters,
  supported-feature representatives, and canaries through the exact scheduled
  Lab2 Part6 canary have Vitis `csim_design` and `csynth_design` evidence
  through the current-head 28-program
  `docs/vitis-validation/2026-07-02-tile-k-facts-current-head/` checkpoint. The
  previous scheduled Part6, post-refactor SRAM-tile fold, and Lab3 raw-wrapper
  boundaries remain preserved under their earlier evidence folders. Board
  execution, Vivado implementation, timing closure, generic Spatial `Fold`,
  arbitrary local-memory folds/effects, dynamic/tail K tiling, K tails, generic
  `par`, broad Scala source compatibility, and broad Spatial coverage remain
  pending.
- The Lab1Part2 memory lowering is a narrow structural slice, not a general Spatial memory backend. It accepts the selected fixed shape: `N = 32`, `tileSize = 16`, one input DRAM, one output DRAM, two 16-element SRAM tiles, one scalar integer multiplier, and dense unit-stride transfers.
- The Lab1Part2 generated harness uses an independent vector oracle, but the source initialization is currently fixed to the selected EE109 shape `src(i) = i % 256`.
- FIFO outside the exact raw Lab1 Part4 wrapper / `FifoTileScale32` semantic
  shape, generic reductions/folds, generic memory reductions/folds, generic
  FSMs, generic RegFile/LineBuffer lowering, dynamic sizes, non-unit strides,
  and non-`Int` element types beyond the exact Rust
  `FixPt[TRUE,_24,_8]` MemFold canary remain unsupported in HLS mode and should
  stay fail-closed until selected intentionally.
- The exact local Lab3 teaching raw wrapper is a source-compatibility adapter
  only. It preserves the existing Vitis-proven `Lab3Part1Convolution` payload
  locally; the fresh current-head EC2/Vitis run proves the canonical payload
  with this adapter code present, not a distinct raw-wrapper validation program.
- The Scala runs still emit the existing `libisl appears to be missing` warning. That warning does not block these local regression results, but it is separate from vendor HLS readiness.

## Recommended Next Action

For the Rust rewrite, the clean current-head EC2/Vitis checkpoint has now been
refreshed after Tile-K fact consumption and same-span loop-symbol cleanup. The
fixed Tile-K phase-spine guard is also complete as local fail-closed classifier
hardening, with structural statement recovery still private and checked
payloads/HLS output/validation membership unchanged. The structural Part6
scheduled core is now complete locally, so the next implementation slice should
stay fail-closed and either choose another explicit GEMM canary/source shape or
deliberately widen one named syntax surface under the same equality discipline
before attempting broad Scala shell support. The main remaining EE109 gaps are
generic Spatial
`MemFold`/`Fold`, dynamic/tail K tiling, K tails, broader fixed-point/tail
semantics, generic `par` and banking inference beyond the fixed Part6 schedule,
and generic Lab3 local-window/stencil lowering beyond the exact local raw
wrapper.

## 2026-06-30 Rust Rewrite Bulk Tile IO Bridge

The Rust rewrite now has a parser-only source-spelling bridge for canonical
rank-2 GEMM tile IO:

- `load lhs_tile <- lhs[row_base..row_base + row_limit, 0..K];`
- `load rhs_tile <- rhs[0..K, col_base..col_base + col_limit];`
- `load c_tile <- cin[row_base..row_base + row_limit, col_base..col_base + col_limit];`
- `store out[row_base..row_base + row_limit, col_base..col_base + col_limit] <- c_tile;`

Status:
- Local parser equivalence tests prove the bulk spelling normalizes to the
  existing expanded `Dense2dTileMemFold` exact FixPt and Int-tail payloads.
- Local HLS/manifest equality tests prove generated C++ and manifest JSON are
  unchanged for those canaries.
- The exact `MatrixTileMemFoldFixPt4x6x5` validation example now exercises the
  bulk IO spelling plus body-local `partial_tile` spelling without changing
  validation-program membership.

Evidence boundary:
- No new Vitis run is claimed for this bridge.
- No generic DMA, raw Scala `::` ranges outside the later narrow infix tile-IO
  bridge, `SRAM[T](...)`, `val`, `par`, banking, K tiling, FixPt tail, board,
  or timing-closure claim was made at this bulk IO checkpoint; the later
  shell-alias bridge below narrows exact `SRAM[T]` and `val` support without
  changing the HLS evidence boundary.

## 2026-06-30 Rust Rewrite Lab2 Shell-Alias Buffer Bridge

The Rust rewrite now has a parser-only source-spelling bridge for the exact
FixPt `Dense2dTileMemFold` canary using selected Lab2-like shell names:

- input aliases `a`, `b`, and `c`
- local tile aliases `tileA_sram`, `tileB_sram`, and `tileC_sram`
- `.buffer` only on `tileC_sram`
- body-local `val partial_c = SRAM[T](TILE_R, TILE_C)`
- Scala-call `Foreach(end by 1) { idx => ... }`
- paren indexing/assignment such as
  `partial_c(ii, jj) = tileA_sram(ii, k_idx) * tileB_sram(k_idx, jj)`

Status:
- The parser canonicalizes those aliases to `lhs`, `rhs`, `cin`,
  `lhs_tile`, `rhs_tile`, `c_tile`, `partial_tile`, `r`, `c`, and `kk` before
  HIR/classification.
- Local parser equivalence proves the shell spelling normalizes to the
  existing expanded exact FixPt `Dense2dTileMemFold` payload.
- Local HLS/manifest equality proves generated C++ and manifest JSON are
  unchanged for `MatrixTileMemFoldFixPt4x6x5`.
- The validation-program list remains at 24 programs, and
  `Lab2Part5GEMM`/`Lab2Part6GEMM` remain absent.

Evidence boundary:
- No new Vitis run is claimed for this bridge.
- No raw Scala `@spatial` source, generic/raw Scala `::` ranges outside the
  later narrow infix tile-IO bridge, in-place `c`, `ArgIn`/`setMem`, outer K
  tiling, `numel_k` MemFold bounds, Part6 `par`, banking, generic Spatial
  `MemFold`, generic DMA, broader fixed-point widths, FixPt tail tiles, board
  execution, or timing-closure claim is made.

## 2026-06-30 Rust Rewrite Infix Tile IO Bridge

The Rust rewrite now has a parser-only source-spelling bridge for exact infix
rank-2 tile IO around the existing `Dense2dTileMemFold` canaries:

- `tileA_sram load a(row_base :: row_base + row_limit, 0 :: K)`
- `tileB_sram load b(0 :: K, col_base :: col_base + col_limit)`
- `tileC_sram load c(row_base :: row_base + row_limit, col_base :: col_base + col_limit)`
- `out(row_base :: row_base + row_limit, col_base :: col_base + col_limit) store tileC_sram`

Status:
- `::` is accepted only inside this infix tile IO parser bridge.
- The parser canonicalizes Lab2 shell aliases to the existing internal roles
  and desugars the IO ranges to the same nested copy loops used by prefix bulk
  IO before HIR/classification.
- Local parser equivalence proves the infix spelling normalizes to the
  existing exact FixPt and Int-tail `Dense2dTileMemFold` payloads.
- Local HLS/manifest equality proves generated C++ and manifest JSON are
  unchanged for `MatrixTileMemFoldFixPt4x6x5`.
- The validation-program list remains at 24 programs, and
  `Lab2Part5GEMM`/`Lab2Part6GEMM` remain absent.

Evidence boundary:
- No new Vitis run is claimed for this bridge.
- No raw Scala `@spatial` source, generic `::` ranges, in-place
  `c(...) store`, `ArgIn`/`setMem`, outer K tiling, `numel_k` MemFold bounds,
  Part6 `par`, banking, generic Spatial `MemFold`, generic DMA, broader
  fixed-point widths, FixPt tail tiles, board execution, or timing-closure
  claim is made.

## 2026-06-30 Rust Rewrite Infix Tile IO EC2 Vitis Validation

The parser-only infix tile IO checkpoint above now has fresh EC2 Vitis 2025.1
execution evidence at Rust commit `1756d4d`.

Command:
- `/home/ubuntu/.cargo/bin/cargo run --manifest-path /home/ubuntu/spatial-rs-runs/infix-tile-io-20260630-1756d4d/spatial-rs/Cargo.toml -p ee109-examples --locked --bin run-vitis-validation -- --execute --mode both --settings /tools/Xilinx/2025.1/Vitis/settings64.sh --out /home/ubuntu/spatial-rs-runs/infix-tile-io-20260630-1756d4d/spatial-rs/target/vitis-validation-infix-tile-io-20260630`

Result:
- All 24 validation programs completed with return code 0, `csim=true`, and
  `csynth=true`.
- `MatrixTileMemFoldFixPt4x6x5` passed C simulation with
  `PASS MatrixTileMemFoldFixPt4x6x5` and completed HLS synthesis.
- The FixPt canary reported estimated Fmax 121.61 MHz, estimated clock
  8.223 ns, latency 84 cycles, interval 60 cycles, and utilization estimate
  6 BRAM_18K, 8 DSP, 6457 FF, and 5919 LUT.
- Compact evidence is captured in
  `docs/vitis-validation/2026-06-30-infix-tile-io/`.

Scope:
- This evidence validates the current checked HLS payload after the source
  fixture moved to the narrow infix tile IO bridge.
- It does not promote `Lab2Part5GEMM` or `Lab2Part6GEMM`, does not prove
  original Scala source compatibility, and does not claim in-place `c`, outer K
  tiling, `numel_k`, Part6 `par`, banking, generic Spatial `MemFold`, generic
  DMA, board execution, Vivado implementation, or timing closure.

## 2026-06-30 Rust Rewrite In-Place C MemFold Canary

The Rust rewrite now has a separate narrow in-place `c` canary for the
fixed-shape FixPt `Dense2dTileMemFold` path:

- `inputs { a: Dram<FixPt[TRUE,_24,_8]>[ROWS,K], b: Dram<FixPt[TRUE,_24,_8]>[K,COLS] }`
- `inouts { c: Dram<FixPt[TRUE,_24,_8]>[ROWS,COLS] }`
- `tileC_sram load c(row_base :: row_base + TILE_R, col_base :: col_base + TILE_C)`
- `c(row_base :: row_base + TILE_R, col_base :: col_base + TILE_C) store tileC_sram`

Status:
- The parser, HIR, checked IR, manifest, HLS plan, C++ emitter, and host
  harness now model a single mutable `c` DRAM port for this canary.
- The manifest direction is `host_kernel_inout`, and generated HLS has a single
  mutable pointer parameter `spatial_fixpt_true_24_8_t *c`.
- The host harness seeds `actual` from the input `c` values before invoking the
  kernel and checks the mutated `c` buffer against the GEMM oracle.
- The local validation-program list is now 25 programs, with
  `MatrixTileMemFoldInPlaceFixPt4x6x5` added after the existing split
  `MatrixTileMemFoldFixPt4x6x5` canary.

Evidence:
- Local HLS/codegen/harness:
  `lab2_inplace_c_memfold_emits_single_mutable_c_pointer_and_harness`.
- Local fixture and plan-only lane:
  `cargo test -p ee109-examples --locked`.
- Local MemFold HLS regression:
  `cargo test -p spatial-rs-hls --locked --test m1_codegen memfold`.

Evidence boundary:
- At the initial local checkpoint this had host-C++ and Vitis plan-only
  evidence only. The follow-up EC2/Vitis checkpoint below covers the
  25-program lane including `MatrixTileMemFoldInPlaceFixPt4x6x5`.
- `Lab2Part5GEMM` and `Lab2Part6GEMM` remain rejected. This canary does not
  claim original Scala source compatibility, `ArgIn`/`setMem`, source-level
  Part5/Part6 shell extraction, outer K tiling, `numel_k`, Part6 `par`, banking,
  generic Spatial `MemFold`, generic DMA, board execution, Vivado
  implementation, or timing closure.

## 2026-06-30 Rust Rewrite In-Place C MemFold EC2 Vitis Validation

The explicit-inout C MemFold canary now has EC2 Vitis 2025.1 execution
evidence at Rust commit `79d1b67`.

Command:
- `/home/ubuntu/.cargo/bin/cargo run --manifest-path /home/ubuntu/spatial-rs-runs/inplace-c-memfold-20260630-79d1b67/spatial-rs/Cargo.toml -p ee109-examples --locked --bin run-vitis-validation -- --execute --mode both --settings /tools/Xilinx/2025.1/Vitis/settings64.sh --out /home/ubuntu/spatial-rs-runs/inplace-c-memfold-20260630-79d1b67/spatial-rs/target/vitis-validation-inplace-c-memfold-20260630`

Result:
- All 25 validation programs completed with return code 0, `csim=true`, and
  `csynth=true`.
- `MatrixTileMemFoldInPlaceFixPt4x6x5` passed C simulation with
  `PASS MatrixTileMemFoldInPlaceFixPt4x6x5` and completed HLS synthesis.
- The in-place FixPt canary reported estimated Fmax 123.77 MHz, estimated
  clock 8.080 ns, latency 111 cycles, interval 96 cycles, and utilization
  estimate 6 BRAM_18K, 8 DSP, 5496 FF, and 5072 LUT.
- Compact evidence is captured in
  `docs/vitis-validation/2026-06-30-inplace-c-memfold/`.

Scope:
- This evidence validates the exact Rust-subset explicit-inout C path with
  `inputs { a, b } inouts { c }`, one mutable HLS pointer `c`, preload from
  `c`, and store back to `c`.
- It does not promote `Lab2Part5GEMM` or `Lab2Part6GEMM`, does not prove
  original Scala source compatibility, and does not claim source-level
  Part5/Part6 shell extraction, outer K tiling, `numel_k`, Part6 `par`,
  banking, generic Spatial `MemFold`, generic DMA, board execution, Vivado
  implementation, or timing closure.

## 2026-06-30 Rust Rewrite Static Outer-K In-Place C MemFold Canary

The Rust rewrite now has one static exact outer-K in-place C canary for the
Lab2 Part5 GEMM direction:

- `MatrixTileMemFoldOuterKInPlaceFixPt32x32x32`
- `ProgramKind::Dense2dTileKMemFold`
- `K_TILES = 2`, `TILE_K = 16`, `K = 32`
- local A/B SRAMs are `[TILE_R,TILE_K]` and `[TILE_K,TILE_C]`
- global K DRAM indexing is `kk_tile*TILE_K + k_idx`
- `c` is one explicit `DramInOut`/mutable HLS pointer

Status:
- The local validation-program list is now 26 programs.
- Parser/classifier support is separate from the old full-K
  `Dense2dTileMemFold v0` payload.
- HLS codegen emits a real outer `kk_tile` loop and `TILE_K`-sized local
  A/B arrays.
- The host-C++ harness seeds `actual` from `c`, mutates `c` in place, and
  checks against the existing `C + A*B` oracle.
- Vitis dry-run/plan-only sidecars include the new canary.
- EC2 Vitis 2025.1 `csim_design` and `csynth_design` now pass for all 26
  validation programs, including this canary.

Evidence:
- `cargo test -p spatial-rs-core --locked outer_k -- --nocapture`
- `cargo test -p spatial-rs-hls --locked lab2_outer_k_inplace_c_memfold_emits_static_k_tile_loops_and_harness -- --nocapture`
- `cargo test -p ee109-examples --locked validation_programs_include_supported_features_after_adapter_baseline -- --nocapture`
- `cargo test -p ee109-examples --locked emit_vitis_dry_run_binary_generates_m1_frontend_bundles -- --nocapture`
- `cargo test -p ee109-examples --locked run_vitis_validation_plan_only_writes_sidecar_tcl_for_all_examples -- --nocapture`
- EC2 command:
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --execute --mode both --settings /tools/Xilinx/2025.1/Vitis/settings64.sh --out target/vitis-validation-outer-k-run`
- Durable evidence:
  `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-01-outer-k-memfold/`
- New canary Vitis result:
  `returncode=0`, `csim=true`, `csynth=true`, estimated Fmax 136.99 MHz.

Evidence boundary:
- EC2/Vitis `csim_design` and `csynth_design` are claimed for the exact
  26-program validation lane only.
- The EC2/Vitis run itself is not raw Scala `Lab2Part5GEMM` or
  `Lab2Part6GEMM` source compatibility. Exact fixed Part5 raw-wrapper support
  is tracked below as a local parser/HLS-equality bridge over the same canary.
- Dynamic `ArgIn` dimensions, dynamic/tail `numel_k`, K tails,
  generic/source-compatible Spatial `MemFold`, Part6 `par`, banking, board execution, Vivado
  implementation, and timing closure remain unsupported.

## 2026-07-01 Rust Rewrite Lab2-Like Outer-K Parser Bridge

The Rust rewrite now accepts a Lab2-like shell/infix spelling for the same
static exact outer-K canary:

- `inputs { a, b } inouts { c }`
- `tileA_sram`, `tileB_sram`, and `tileC_sram.buffer`
- outer tile loops spelled as `kk`, `mm`, and `nn`
- a hoisted A-tile load before the column tile loop
- infix rank-2 tile loads/stores using `::` ranges
- exact static offset loops such as `Foreach(K by TILE_K)`, canonicalized back
  to the existing tile-count loop payload
- `MemFold(tileC_sram)(0 until TILE_K by 1) { k_idx => ... }{_+_}`
- a declared static `numel_k` alias equal to `TILE_K` inside K tile ranges and
  the MemFold bound
- exact static `val numel_k = min(TILE_K.to[Int], K - kk);` spelling under the
  same offset-loop proof
- the exact fixed raw `@spatial class Lab2Part5GEMM` wrapper when `runtimeArgs`
  prove `M=N=K=32`, `tileM/tileN/tileK` are all `16`, the type alias is
  `FixPt[TRUE,_24,_8]`, and there is one matching `Accel` body. This raw-wrapper
  check is token-stream exact: comments and ordinary whitespace between tokens
  are allowed, while token-split identifiers/operators remain rejected.

Status:
- This is parser/source-spelling coverage only. It canonicalizes to the
  existing `Dense2dTileKMemFold` checked payload for
  `MatrixTileMemFoldOuterKInPlaceFixPt32x32x32`.
- The generated HLS and manifest match the expanded static outer-K canary
  exactly.
- The validation-program list remains 26 programs.
- No new EC2/Vitis evidence is claimed for this bridge because it does not
  change emitted HLS or validation membership.

Evidence boundary:
- Local proof is parser/classifier equivalence plus HLS/manifest equality:
  `cargo test -p spatial-rs-core --locked lab2_outer_k -- --nocapture`,
  `cargo test -p spatial-rs-core --locked raw_lab2_part5 -- --nocapture`, and
  `cargo test -p spatial-rs-hls --locked lab2_outer_k -- --nocapture`, plus
  `cargo test -p spatial-rs-hls --locked --test m1_codegen lab2_raw_part5 -- --nocapture`.
- Non-exact raw Scala `Lab2Part5GEMM` and all `Lab2Part6GEMM` forms still fail
  closed. The bridge also keeps full-K MemFold bounds, undeclared or mismatched
  `numel_k`, malformed or dynamic `numel_k = min(...)` variants, non-exact
  offset-loop steps, token-split identifiers/operators, dynamic/tail K tiling, hoisted
  B/C/fold/store phases, Part6 `par`, banking, generic Spatial `MemFold`, board
  execution, Vivado
  implementation, and timing closure unsupported.

## 2026-07-01 Rust Rewrite `a16401b9` EC2 Vitis Refresh

After the tokenized raw Part5 wrapper bridge and shared frontend nested block
comment support, the Rust rewrite re-ran the exact 26-program Vitis lane at
source commit `a16401b9c1699d8f92d7ec0a93b04ae608d90617` on
`David/HLS-spatial`.

Evidence:
- Remote host: `[ec2-host — see private/ec2-lane.md]`
  (`ip-172-31-37-7`)
- Remote run directory:
  `/home/ubuntu/spatial-rs-runs/block-comments-a16401b/spatial-rs`
- Command:
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --execute --mode both --settings /tools/Xilinx/2025.1/Vitis/settings64.sh --out target/vitis-validation-block-comments-a16401b`
- Durable evidence:
  `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-01-block-comments-refresh/`
- Result: all 26 programs reported `returncode=0`, `csim=true`, and
  `csynth=true`.
- `MatrixTileMemFoldOuterKInPlaceFixPt32x32x32` result: estimated Fmax
  136.99 MHz, estimated clock 7.300 ns, latency 41053 cycles, interval 41054
  cycles, and utilization estimate 41 BRAM_18K, 64 DSP, 8120 FF, and 5896 LUT.

Evidence boundary:
- This refresh proves Vitis C simulation and HLS synthesis for the exact
  `a16401b9` 26-program validation set only.
- It also confirms that frontend block-comment support did not perturb the
  generated validation kernels.
- It does not claim board execution, Vivado implementation/place-and-route,
  post-implementation timing closure, broad Scala source compatibility,
  structured Scala wrapper parsing, `Lab2Part6GEMM`, Part6 `par`,
  dynamic/tail K tiling, generic Spatial `MemFold`, banking, generic DMA,
  generic in-place alias analysis, FixPt tail tiles, or broader Spatial
  language coverage.

## 2026-07-01 Rust Rewrite Lab1 Part6 SRAM-Tile Fold Vitis Checkpoint

The Rust rewrite added `ScalarSramTileFold v0` and the non-lab
`SramTileFoldSum32` validation canary after the refreshed 26-program Vitis
checkpoint.

Status:
- The validation list now contains 27 programs and all 27 passed EC2/Vitis
  `csim_design` and `csynth_design`.
- `SramTileFoldSum32` covers one rank-1 `Dram<Int>[32]` input, one scalar
  output, one local `Sram<Int>[16]` tile, an explicit DRAM-to-SRAM tile load,
  an inner tile sum, and scalar accumulator writeback.
- The exact raw `Lab1Part6ReduceExample` token stream canonicalizes to
  `SramTileFoldSum32` with generated HLS/manifest equality.
- Local host-C++ harness, Vitis dry-run/plan coverage, and durable EC2/Vitis
  evidence are in place.

Evidence boundary:
- Durable evidence is captured in
  `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-01-lab1-part6-sram-hir-refactor/`
  at source commit `f0f3cb4ee03461fefacfeebc21dd8e4db38b8c51`.
- Generic Spatial `Fold`, arbitrary nested folds, arbitrary local-memory
  effects, tail tiles, dynamic bounds, non-`Int`, scheduling, banking, board
  execution, Vivado implementation, timing closure, and broad Scala source
  compatibility remain unsupported.

## 2026-06-30 Rust Rewrite Lab2 `numel_m`/`numel_n` Parser Bridge

The Rust rewrite now accepts one more Lab2 source-spelling detail in the
existing parser-only MemFold shell/infix bridge:

- `numel_m` may stand for the row tile extent.
- `numel_n` may stand for the column tile extent.
- Exact tile spellings normalize those names to the existing `TILE_R` and
  `TILE_C` extents.
- Tail spellings normalize those names to the existing `row_limit` and
  `col_limit` checked-payload names.

Status:
- This is a frontend canonicalization only. The checked IR payload remains the
  existing `Dense2dTileMemFold` payload.
- The validation-program list remains the same 25 programs.
- No generated HLS, manifest, harness, or Vitis evidence changed for this
  parser bridge.
- A new fail-closed parser guard keeps `numel_k` K tiling unsupported.

Evidence boundary:
- Local proof is parser regression only:
  `cargo test -p spatial-rs-core --locked lab2_infix_tile_io -- --nocapture`.
- This does not promote `Lab2Part5GEMM` or `Lab2Part6GEMM`, does not prove
  original Scala source compatibility, and does not claim source-level
  Part5/Part6 shell extraction, outer K tiling, `numel_k`, Part6 `par`,
  banking, generic Spatial `MemFold`, generic DMA, board execution, Vivado
  implementation, or timing closure.
