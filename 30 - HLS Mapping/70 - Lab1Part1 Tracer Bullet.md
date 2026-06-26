---
type: hls-mapping
construct: lab1part1-tracer-bullet
category: rework
date: 2026-06-25
status: draft
depends_on:
  - "[[04-ee109-hls-target-corpus]]"
  - "[[ee109-frontend-to-ir-path]]"
  - "[[55 - EE109 ABI Manifest v0]]"
  - "[[60 - EE109 HLS Lowering Map]]"
---

# Lab1Part1 Tracer Bullet

This tracer bullet is the first end-to-end proof that the EE109 HLS path can compile a selected Spatial example into HLS C++ and verify the result. It intentionally covers only the scalar path before DRAM, SRAM, loops, partitioning, or Lab3 stencil behavior.

## Source Kernel

Target source:

`/Users/david/Documents/David_code/lab-1-accelerator-bandits-1/Lab1Part1RegExample/src/Lab1Part1RegExample.scala`

Selected source facts:

| Item | Source evidence | Tracer meaning |
|---|---|---|
| Runtime args | `runtimeArgs = "3 5"` and `args(0)`, `args(1)` become `N` and `M` (`Lab1Part1RegExample.scala:6-10`) | Host test inputs are fixed to `3` and `5` for the first oracle. |
| Scalar inputs | `argRegIn0 = ArgIn[T]`, `argRegIn1 = ArgIn[T]`, followed by `setArg` calls (`Lab1Part1RegExample.scala:11-14`) | Two scalar host-to-kernel ports. |
| Scalar output | `argRegOut = ArgOut[T]` (`Lab1Part1RegExample.scala:15`) | One scalar kernel-to-host endpoint. |
| Kernel boundary | `Accel { ... }` (`Lab1Part1RegExample.scala:17-21`) | One HLS top function body. |
| Kernel operation | Read two `.value`s, add them, assign to `argRegOut` (`Lab1Part1RegExample.scala:18-20`) | HLS body is `*argRegOut = argRegIn0 + argRegIn1`. |
| Oracle | `getArg(argRegOut)`, `gold = M + N`, equality check, `assert(cksum)` (`Lab1Part1RegExample.scala:23-32`) | Expected result is `8`; pass condition is exact scalar equality. |

## Minimal IR Pattern

The frontend deep dive records the staged pattern visible in the first IR log:

| IR role | Required node pattern | HLS role |
|---|---|---|
| Input allocation | Two `ArgInNew(Const(0))` nodes | Scalar input manifest records. |
| Host setup | `SetReg(argRegIn0, N)`, `SetReg(argRegIn1, M)` | Host harness values before kernel call. |
| Output allocation | One `ArgOutNew(Const(0))` node | Scalar output manifest record. |
| Kernel boundary | One `AccelScope` body | HLS top function body. |
| Kernel reads | Two `RegRead` nodes from the ArgIns | Scalar C++ parameters. |
| Operation | One `FixAdd` over the reads | Signed integer addition. |
| Kernel write | One `RegWrite` to the ArgOut | Scalar output assignment. |
| Host read | One `GetReg(argRegOut)` after the `AccelScope` | Host harness result read. |
| Oracle envelope | Print, compare, assert after `GetReg` | Verification harness, not kernel code. |

The Stage 0 extractor should fail fast unless it finds this shape inside one `AccelScope`. That keeps the first build target small and avoids silently accepting a broader Spatial program shape.

## ABI Manifest Slice

Logical manifest:

```yaml
abi_schema: ee109_abi_manifest_v0
kernel:
  name: Lab1Part1RegExample
  entry_symbol: Lab1Part1RegExample_kernel
scalar_inputs:
  - name: argRegIn0
    spatial_role: ArgIn
    hls_type: int
    hls_port: argRegIn0
    test_value: 3
  - name: argRegIn1
    spatial_role: ArgIn
    hls_type: int
    hls_port: argRegIn1
    test_value: 5
scalar_outputs:
  - name: argRegOut
    spatial_role: ArgOut
    hls_type: int
    hls_port: argRegOut
    expected_value: 8
    comparator: exact_equal
dram_buffers: []
```

The manifest is the source of truth. C++ spelling is a projection that can change if the chosen HLS tool wants an output reference instead of a pointer.

## HLS C++ Behavioral Target

```cpp
extern "C" void Lab1Part1RegExample_kernel(
    int argRegIn0,
    int argRegIn1,
    int *argRegOut) {
#pragma HLS INTERFACE s_axilite port=argRegIn0 bundle=control
#pragma HLS INTERFACE s_axilite port=argRegIn1 bundle=control
#pragma HLS INTERFACE s_axilite port=argRegOut bundle=control
#pragma HLS INTERFACE s_axilite port=return bundle=control

  *argRegOut = argRegIn0 + argRegIn1;
}
```

This C++ is the behavioral target for Stage 0. The implementation should generate it from the staged IR pattern, then compare it against the oracle below.

## Verification Oracle

| Field | Value |
|---|---|
| Input `argRegIn0` | `3` |
| Input `argRegIn1` | `5` |
| Expected `argRegOut` | `8` |
| Source gold expression | `M + N` |
| Pass condition | generated kernel output equals `8` |

Recommended first harness:

```cpp
int main() {
  int out = 0;
  Lab1Part1RegExample_kernel(3, 5, &out);
  return out == 8 ? 0 : 1;
}
```

For the first implementation wave, a normal C++ compile-and-run check is sufficient to validate the generated semantics. Vitis/Vivado HLS project generation can be added after the generated C++ is stable.

## Stage 0 Non-Goals

- No DRAM, SRAM, dense transfer, or local array lowering.
- No loop, `par`, partitioning, controller scheduling, or II policy.
- No print/assert emission inside the HLS kernel.
- No fixed-point, floating-point, FMA, rounding, stream, FIFO, blackbox, or external bus support.
- No attempt to match Chisel/Fringe host runtime APIs.

## Done Criteria

Stage 0 is complete when:

- the compiler can identify the Lab1Part1 staged scalar ABI and `AccelScope` body,
- the generated HLS C++ contains the scalar-add top function,
- the generated or generated-plus-wrapper C++ compiles with a normal C++ compiler,
- the harness returns success for `3`, `5`, and expected `8`,
- unsupported non-Stage-0 constructs fail with explicit diagnostics rather than partial output.
