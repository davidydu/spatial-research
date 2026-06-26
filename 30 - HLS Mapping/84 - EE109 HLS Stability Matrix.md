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

The next implementation slice should be one of:

1. FIFO for Lab1, if the research goal wants to expand breadth across early EE109 examples.
2. 2-D DRAM and nested-loop memory lowering, if the research goal wants to move toward convolution/GEMM-like Lab3 examples.

Do not implement reductions, LineBuffer, or RegFile next unless a selected EE109 target forces it; those features have higher semantic and scheduling risk.
