---
type: hls-mapping
construct: ee109-hls-stability-matrix
category: rework
status: current
date: 2026-06-25
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

The `2026-06-27-runner` replay used the repo-local `run-vitis-validation`
command. It defaults to plan-only sidecar generation and requires `--execute`
to run Vitis. The EC2 host's system Cargo was 1.75.0, so the copied remote
bundle used a remote-only lockfile v4-to-v3 downgrade; the local Rust repo
lockfile was not changed.

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

- The HLS gate is still a local host-C++ gate. It does not invoke Vitis/Vivado HLS, synthesize RTL, check timing, or validate board integration.
- The Lab1Part2 memory lowering is a narrow structural slice, not a general Spatial memory backend. It accepts the selected fixed shape: `N = 32`, `tileSize = 16`, one input DRAM, one output DRAM, two 16-element SRAM tiles, one scalar integer multiplier, and dense unit-stride transfers.
- The Lab1Part2 generated harness uses an independent vector oracle, but the source initialization is currently fixed to the selected EE109 shape `src(i) = i % 256`.
- FIFO, reductions, FSMs, RegFile, LineBuffer, 2-D DRAM shapes, dynamic sizes, non-unit strides, and non-`Int` element types remain unsupported in HLS mode and should stay fail-closed until selected intentionally.
- The Scala runs still emit the existing `libisl appears to be missing` warning. That warning does not block these local regression results, but it is separate from vendor HLS readiness.

## Recommended Next Action

For the Rust rewrite, the next implementation slice should promote memory and
array behavior from fixture adapters into reusable frontend/HIR/lowering
support. Dense 1-D DRAM/SRAM load-compute-store is the natural next feature
candidate because it sits directly after scalar expressions and before higher
risk FIFO, reductions, LineBuffer, RegFile, or GEMM/stencil surfaces.
