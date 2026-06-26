---
type: hls-mapping
construct: stage1-ee109-hls-expansion-plan
category: rework
status: draft
date: 2026-06-25
stage: 1
depends_on:
  - "[[70 - Lab1Part1 Tracer Bullet]]"
  - "[[72 - Stage0 HLS Emitter Design]]"
  - "[[74 - Stage0 Harness And Build Flow]]"
  - "[[75 - Stage0 Tests And Verification]]"
  - "[[76 - Stage0 Implementation Risk Review]]"
---

# Stage1 EE109 HLS Expansion Plan

## Purpose

Stage 1 should expand the now-passing Stage 0 HLS tracer without turning it into a generic Spatial backend. The goal is to support the next EE109 examples in order: first the lab-root three-input scalar add, then a scout of the Lab1Part2 DRAM/SRAM/Foreach shape.

The expansion stays fail-closed. Every accepted construct must be tied to a selected EE109 example, and every unsupported memory, controller, or ABI shape must produce a clear diagnostic before partial HLS output is treated as valid.

## Starting Point

- Stage 0 exists and passes `Lab1Part1RegExample` for the nested two-input scalar add source.
- The Stage 0 contract is two `ArgIn[Int]`, one `ArgOut[Int]`, one `AccelScope`, two kernel `RegRead`s, one integer `FixAdd`, and one `RegWrite`.
- Generated HLS C++ is checked through an ordinary host compiler and harness before any Vitis/Vivado flow.
- The key known ambiguity is source selection: the nested `Lab1Part1RegExample/src/Lab1Part1RegExample.scala` is two-input, while lab-root `/Users/david/Documents/David_code/lab-1-accelerator-bandits-1/src/test/scala/Lab1.scala` contains a same-named three-input variant.

## Target Examples

| Stage | Example | Required new surface | Oracle |
|---|---|---|---|
| 1A | `Lab1Part1RegExample` in lab-root `Lab1.scala` | Three `ArgIn[Int]`, one `ArgOut[Int]`, nested integer add tree | Runtime args `3 5 7`, expected scalar `15` |
| 1B | Negative regression set | Explicit rejection for non-selected or not-yet-supported shapes | No generated partial success on unsupported input |
| 1C | `Lab1Part2DramSramExample` in lab-root `Lab1.scala` | `DRAM[Int](32)`, `SRAM[Int](16)`, `setMem`, `getMem`, dense load/store, `Sequential.Foreach`, inner `Foreach` | Runtime arg `3`, expected 32-element vector `src(i) * 3` for `src(i) = i % 256` |

## Stage 1A: Scalar Generalization

Promote the scalar extractor from "exactly two inputs" to "selected scalar add manifest" while keeping the first implementation pinned to the three-input Lab1Part1 variant.

Accepted shape:

- Exactly three `ArgIn[Int]` nodes before the `AccelScope`.
- Exactly three matching host `SetReg` calls with runtime values `3`, `5`, and `7`.
- Exactly one `ArgOut[Int]` and one post-accelerator `GetReg`.
- Exactly one top-level `AccelScope`.
- Kernel body consists of `RegRead` from the three inputs, a nested `FixAdd` tree, and one unconditional `RegWrite` to the output.

Generated C++ target:

```cpp
extern "C" void Lab1Part1RegExample_kernel(
    int argRegIn0,
    int argRegIn1,
    int argRegIn2,
    int *argRegOut) {
  *argRegOut = argRegIn0 + argRegIn1 + argRegIn2;
}
```

The Stage 0 two-input case must remain a regression, not be replaced. The current lightweight harness may compute its expected scalar from the same accepted expression tree so that runtime argument parsing and kernel invocation stay checked. A later manifest-backed harness should make the source path, input count, runtime values, and independent expected scalar explicit before this becomes more than a tracer-bullet gate.

## Stage 1B: Negative Regression Harness

Add negative tests before broadening into memory. These tests should prove that the HLS path rejects unsupported input with a stage-specific diagnostic and does not leave behind generated kernel/harness files that look valid.

Minimum negative cases:

- Missing runtime value for one scalar input.
- Three scalar inputs with no single `ArgOut` write.
- Host `setArg` or `getArg` used inside `Accel`.
- `DRAM`, `SRAM`, dense transfer, `Foreach`, `Sequential.Foreach`, `FIFO`, `Reduce`, or `FSM` before its stage is enabled.
- Source-path mismatch where the manager expected the two-input nested file but compiled the lab-root three-input file, or the reverse.

This harness should run beside the positive scalar tests and assert the exact diagnostic category, not just "throws some exception."

## Stage 1C: DRAM/SRAM/Foreach Scout

Scout Lab1Part2 without committing to full memory lowering in the same patch. The scout should collect the staged IR and produce a short implementation note or manifest draft for the selected shape:

- Host ABI: one scalar `ArgIn[Int]` named like `x`, one input DRAM pointer, one output DRAM pointer, `setMem(srcFPGA, srcHost)`, and `getMem(dstFPGA)`.
- Constants: `N = 32`, `tileSize = 16`, runtime `value = 3`.
- Controller shape: `Sequential.Foreach(N by tileSize)` containing dense load, inner `Foreach(tileSize by 1)`, and dense store.
- Local memories: `b1 = SRAM[Int](16)` and `b2 = SRAM[Int](16)`.
- Kernel operation: `b2(ii) = b1(ii) * x`.
- Oracle: output buffer equals `[0, 3, 6, ..., 93]`.

The scout should answer whether the existing Stage 0 traversal can see enough IR structure to separate host transfers, top-level pointers, local SRAM arrays, dense range loops, and nested controller bodies. If not, Stage 1C ends with named blockers rather than speculative C++.

## Non-Goals

- No Lab2, Lab3, convolution, line buffer, RegFile, LUT, FSM, Reduce, Fold, MemReduce, FIFO, streams, or blackbox support.
- No full Spatial banking search, alpha/N/B banking model, or explicit `.bank` policy.
- No Vitis/Vivado synthesis, RTL simulation, timing closure, or board integration gate.
- No changes to legacy Cppgen, Chiselgen, Fringe host runtime, or CS217 behavior as part of scalar generalization.
- No generic arithmetic backend beyond selected integer add and the Lab1Part2 scout's integer multiply evidence.

## Verification Gates

1. Baseline gate: the existing Stage 0 two-input scalar test still emits, host-compiles, and runs to expected value `8`.
2. Stage 1A positive gate: the lab-root three-input scalar add emits a three-scalar kernel, host-compiles, and runs to expected value `15`.
3. Stage 1A ABI gate: the generated manifest records all scalar ports, runtime values, output comparator, and source path used for the test.
4. Stage 1B negative gate: each unsupported case fails with the expected diagnostic and produces no accepted generated artifact.
5. Stage 1C scout gate: a written IR/manifest scout for `Lab1Part2DramSramExample` names the accepted nodes, unsupported nodes, proposed C++ skeleton, and remaining blockers.

## Manager Notes

- Treat concurrent HLS work in `/Users/david/Documents/David_code/spatial` as shared state. Inspect before editing and do not overwrite another agent's changes.
- Decide source ownership explicitly: nested two-input Lab1Part1 remains the Stage 0 regression; lab-root three-input Lab1Part1 is the Stage 1A target.
- Keep Stage 1A small enough that a failed Lab1Part2 attempt cannot be hidden by scalar success.
- Require exact commands and captured output in the eventual implementation report, including the host compiler invocation and the scalar harness result.
- If Stage 1C reveals that memory/control traversal requires a new abstraction, split that into the next planning artifact before touching code.
