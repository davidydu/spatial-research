---
type: design
project: spatial-spec
date: 2026-06-26
status: active-draft
review_state: corrected-after-subagent-no-go
depends_on:
  - "[[2026-06-26-rust-first-spatial-dsl-overlay]]"
  - "[[84 - EE109 HLS Stability Matrix]]"
  - "[[55 - EE109 ABI Manifest v0]]"
  - "[[60 - EE109 HLS Lowering Map]]"
---

# Rust EE109 MVP Design Record

## Decision Resolution

This record closes the open M1 decisions from `[[2026-06-26-rust-first-spatial-dsl-overlay]]` and starts the Rust rewrite in `/Users/david/Documents/David_code/spatial-rs`.

Reviewer concerns are incorporated as binding rules:

| Topic | Decision |
|---|---|
| Milestone name | Call the first milestone `M1 EE109 teaching tracer slice`, not `EE109 complete`. |
| Full MVP | The larger goal remains all selected EE109 lab features through Lab3. M1 is the first green slice, not the finish line. |
| Scala role | The Scala branch `David/HLS-spatial` is reference-only: generated C++ shape, existing fixtures, and fail-closed expectations. It is not a critical path dependency. |
| Rust layout | Use a Cargo workspace with separate core and HLS crates from the start. |
| CLI | Defer CLI until library APIs and tests are stable. |
| Macro path | M1 must expose a thin `accel!` path for canonical examples. Internal builders are allowed only as parser/test support. |
| Manifest | Emit manifest data from validated Rust IR before C++ emission. JSON is the M1 interchange format. |
| ABI | Scalar `ArgIn[Int]` becomes `int`; scalar `ArgOut[Int]` becomes `int *`; dense DRAM becomes `const int *` or `int *`. |
| HLS claim | Generated C++ is HLS-style and locally host-compiled. It is not Vitis/Vivado proven until a vendor gate runs. |
| Oracle | Harness expected results must be computed independently from the emitted C++ body. |

## Workspace

Create `/Users/david/Documents/David_code/spatial-rs` with:

| Path | Responsibility |
|---|---|
| `crates/spatial-rs-core` | DSL token capture, parser, typed IR, diagnostics, validation, manifest records, independent interpreter/oracles. |
| `crates/spatial-rs-hls` | ABI projection, HLS C++ kernel emitter, host harness emitter, hygiene checks, compile/run helpers for tests. |
| `examples/ee109` | Student-shaped Rust examples and generated artifact smoke tests. |

No external crate is required for M1. JSON can be emitted with a small owned writer until dependency policy is decided.

## M1 DSL Surface

M1 accepts this constrained `accel!` syntax. The macro captures tokens with `stringify!` and calls the Rust parser. It returns `Result<Program, Vec<Diagnostic>>`; tests and examples unwrap only after validation.

Scalar examples:

```rust
accel! {
  kernel Lab1Part1RegExample {
    inputs { argRegIn0: Int, argRegIn1: Int }
    outputs { argRegOut: Int }
    argRegOut := argRegIn0 + argRegIn1;
  }
}
```

Three-input scalar example:

```rust
accel! {
  kernel Lab1Part1RegThreeInputExample {
    inputs { argRegIn0: Int, argRegIn1: Int, argRegIn2: Int }
    outputs { argRegOut: Int }
    argRegOut := (argRegIn0 + argRegIn1) + argRegIn2;
  }
}
```

Dense DRAM/SRAM example:

```rust
accel! {
  kernel Lab1Part2DramSramExample {
    const N: usize = 32;
    const TILE: usize = 16;
    inputs { srcFPGA: Dram<Int>[N], x: Int }
    outputs { dstFPGA: Dram<Int>[N] }
    sequential_foreach i in 0..N step TILE {
      let b1 = Sram<Int>[TILE];
      load b1 <- srcFPGA[i..i + TILE];
      let b2 = Sram<Int>[TILE];
      foreach ii in 0..TILE {
        b2[ii] := b1[ii] * x;
      }
      store dstFPGA[i..i + TILE] <- b2;
    }
  }
}
```

LUT examples:

```rust
accel! {
  kernel Lab2Part4LUT {
    const ROWS: usize = 3;
    const COLS: usize = 3;
    inputs { input: Int, i: Int, j: Int }
    outputs { out: Int }
    let lut = Lut<Int>[ROWS, COLS] = [
      [1, 2, 3],
      [4, 5, 6],
      [7, 8, 9]
    ];
    out := input + lut[i, j];
  }
}
```

For M1, unsupported constructs must be rejected before C++ emission:

- `fsm`, `while`, native Rust `for`, `return`
- `fifo`, `lifo`, `stream`
- `reduce`, `fold`, `memreduce`
- `RegFile`, `LineBuffer`, 2-D `Dram`
- dynamic memory sizes
- non-unit dense ranges or sparse gather/scatter
- non-`Int` numeric types
- explicit banking, DSE, II tuning, or vendor synthesis claims

## M1 IR Contract

`spatial-rs-core` owns typed records with stable names:

| Record | Required fields |
|---|---|
| `Program` | kernel name, constants, ports, memories, statement tree, source text, diagnostics. |
| `Kernel` | one top-level accelerator body per program. |
| `Port` | name, role, type, direction, ordinal, optional shape. |
| `Memory` | name, memory kind, element type, rank, dimensions, layout, values for LUTs. |
| `Stmt` | scalar assignment, sequential loop, parallel-ish loop, load, store, SRAM declaration, SRAM write. |
| `Expr` | constants, ports, arithmetic, memory read, LUT read, index variables. |
| `Manifest` | ABI schema, kernel entry, scalar inputs, scalar outputs, DRAM buffers, local memories, LUT tables, generated artifacts, diagnostics. |
| `Oracle` | independent scalar, vector, or LUT expected-output computation used by harness tests. |
| `Diagnostic` | code, severity, message, span, help text. |

Validation is manifest-first:

1. Parse DSL into IR with source spans.
2. Validate the EE109 support subset.
3. Produce the manifest from validated IR.
4. Emit C++ only if validation has no errors.
5. Emit an independent oracle/harness from IR and manifest, not from generated kernel text.

## M1 JSON Manifest Schema

The M1 manifest is emitted as JSON with deterministic field order. Tests parse the emitted JSON text back through a tiny M1 JSON checker before any C++ emission test is allowed to pass.

Required top-level fields:

| Field | Type | M1 meaning |
|---|---|---|
| `abi_schema` | string | Literal `ee109_abi_manifest_v0`. |
| `kernel` | object | `name`, `entry_symbol`, `source_kind`, and optional `source_refs`. |
| `scalar_inputs` | array | Ordered scalar `ArgIn` records. |
| `scalar_outputs` | array | Ordered scalar `ArgOut` records. |
| `dram_buffers` | array | Dense DRAM pointer records. Empty for scalar and LUT-only kernels. |
| `local_memories` | array | SRAM records with element type, rank, dimensions, and layout. |
| `lut_tables` | array | LUT records with `rows`, `cols`, `values_row_major`, and source-table shape. |
| `generated_artifacts` | array | Planned artifact names such as `kernel.cpp`, `harness.cpp`, and `manifest.json`. |
| `diagnostics` | array | Validation diagnostics emitted before support is accepted. Empty for supported programs. |
| `support_status` | string | `supported_m1` or `rejected_unsupported`. |

Scalar input record:

| Field | Type | Required value policy |
|---|---|---|
| `name` | string | Stable source name. |
| `spatial_role` | string | `ArgIn`. |
| `spatial_type` | string | `Int`. |
| `hls_type` | string | `int`. |
| `direction` | string | `host_to_kernel`. |
| `ordinal` | number | Zero-based within scalar inputs. |
| `hls_port` | string | Same as `name` for M1. |
| `conversion_policy` | string | `raw_scalar_integer_v1`. |

Scalar output record:

| Field | Type | Required value policy |
|---|---|---|
| `name` | string | Stable source name. |
| `spatial_role` | string | `ArgOut`. |
| `spatial_type` | string | `Int`. |
| `cpp_param_type` | string | Literal `int *` for M1. |
| `endpoint_kind` | string | Literal `scalar_argout`. |
| `write_style` | string | Literal `deref_once`. |
| `direction` | string | `kernel_to_host`. |
| `ordinal` | number | Zero-based within scalar outputs. |
| `hls_port` | string | Same as `name` for M1. |
| `conversion_policy` | string | `raw_scalar_integer_v1`. |

DRAM buffer record:

| Field | Type | Required value policy |
|---|---|---|
| `name` | string | Stable source name. |
| `spatial_role` | string | `DRAM`. |
| `element_type` | string | `Int`. |
| `rank` | number | `1` for M1. |
| `dimensions` | array | Constant symbols or values, such as `N`. |
| `layout` | string | `row_major_dense`. |
| `direction` | string | `host_to_kernel` or `kernel_to_host`. |
| `cpp_param_type` | string | `const int *` for input, `int *` for output. |
| `m_axi_bundle` | string | `gmem0` for the first input buffer and `gmem1` for the first output buffer. |
| `control_bundle` | string | `control`. |
| `offset_policy` | string | `slave`. |
| `conversion_policy` | string | `raw_memcpy_v1`. |

This deliberately chooses separate `gmem0` and `gmem1` bundles for Rust M1 even though the current Scala reference lane has used a narrower shared-bundle shape in some generated examples. Host compilation cannot validate HLS interface quality, so the generated C++ tests must assert the exact manifest-backed pragma strings.

## Oracle Independence Contract

The oracle implementation lives in `spatial-rs-core::oracle` and must not depend on `spatial-rs-hls`, C++ emitter helpers, HLS pragma helpers, or generated kernel text.

Required separations:

- Scalar oracles evaluate the IR expression tree directly.
- Dense DRAM/SRAM oracles operate on host vectors and scalar multipliers, not emitted loop text.
- LUT oracles index the source 2-D table semantically as `table[row][col]`; they must not reuse the HLS emitter's flattened `row * COLS + col` string helper.
- Non-square LUT tests must include a canary that fails if both emitter and oracle accidentally use `row * ROWS + col`.
- Harnesses may embed concrete expected values computed by the Rust oracle, but they may not derive expected values from emitted C++.

## M1 HLS C++ Shape

Scalar:

```cpp
extern "C" void Lab1Part1RegExample_kernel(int argRegIn0, int argRegIn1, int *argRegOut) {
#pragma HLS INTERFACE s_axilite port=argRegIn0 bundle=control
#pragma HLS INTERFACE s_axilite port=argRegIn1 bundle=control
#pragma HLS INTERFACE s_axilite port=argRegOut bundle=control
#pragma HLS INTERFACE s_axilite port=return bundle=control
  *argRegOut = argRegIn0 + argRegIn1;
}
```

Dense memory:

- `srcFPGA` is `const int *`
- `dstFPGA` is `int *`
- both get `m_axi` data ports with `offset=slave` plus `s_axilite` control ports
- `srcFPGA` uses bundle `gmem0`; `dstFPGA` uses bundle `gmem1`
- local SRAMs emit fixed `int b1[16]` and `int b2[16]`
- transfer loops are explicit dense unit-stride loops

LUT:

- emit `static const int lut[ROWS * COLS]`
- row-major index is `i * COLS + j`
- non-square LUT tests must assert the stride is `COLS`, not `ROWS`

Generated positive C++ must not contain `FringeContext`, `TopHost`, `Chisel`, `Verilog`, `DRAMSim`, `vcs`, or instrumentation/runtime strings.

## Verification Ladder

M1 green requires:

| Gate | Required command or check |
|---|---|
| Rust unit tests | `cargo test` in `/Users/david/Documents/David_code/spatial-rs`. |
| Generated C++ compile | `c++ -std=c++11 -Wall -Wextra -Wno-unknown-pragmas` for every positive harness. |
| Generated harness run | Each harness prints a pass marker and exits `0`. |
| Negative fail-closed tests | Unsupported programs return diagnostics and produce no valid kernel C++ artifact. |
| Manifest checks | Port order, local memories, LUT row-major shape, generated artifacts, support status, and diagnostics are asserted. |
| Hygiene | No simulator/runtime leakage strings in supported generated C++. |

M1 positive vectors:

| Example | Required adversarial vectors |
|---|---|
| Two-input add | `(3, 5)`, `(-7, 12)`, `(0, -3)` |
| Three-input add | `(3, 5, 7)`, `(100, -40, -60)`, `(-1, -2, -3)` |
| Dense DRAM/SRAM | `src[i] = i % 256`, alternating signs, and sentinel non-monotone values; multipliers `3`, `-2`, `0` |
| Square LUT | corners, middle, and non-zero input offsets |
| Non-square LUT | all corners plus `(1, 2)` to prove row-major stride |

## Full EE109 MVP Ladder

After M1 is stable, continue in separate design/plan slices. The exact next slice is selected at the M1 checkpoint; the current stability matrix recommends either FIFO breadth or 2-D DRAM/Lab3 depth before spending too much on less common control features.

| Milestone | Adds | Representative lab target |
|---|---|---|
| Next candidate A | FIFO or Fold/Reduce if selected from Lab1 examples | Lab1 controller exercises |
| Next candidate B | 2-D DRAM, nested loops, and Lab3 memory layout groundwork | `Lab3Part1Convolution` groundwork |
| Later slice | FSM, `Reg`, conditional SRAM writes, dense store | `Lab2Part3BasicCondFSM` |
| Lab3 slice | `LineBuffer`, `RegFile`, nested `Reduce`, `par`, `mux`, `abs`, row-store | `Lab3Part1Convolution` |
| M5 | Vendor HLS scripts and optional Vitis gates | C simulation and synthesis, if toolchain is present |

The project is complete for the user's current research goal only when all selected EE109 lab features in this ladder are either supported with tests or explicitly marked out of scope by a later decision record.
