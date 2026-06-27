---
type: plan
project: spatial-spec
date: 2026-06-26
status: review-corrected
scope: rust-ee109-m1
depends_on:
  - "[[2026-06-26-rust-ee109-mvp-design]]"
---

# Rust EE109 M1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Rust-hosted EE109 M1 teaching tracer slice: scalar add, fixed dense DRAM/SRAM multiply, square LUT, and non-square LUT, with manifest-first validation, independent oracles, and local HLS-style C++ harness gates.

**Architecture:** Use a Cargo workspace with `spatial-rs-core` for `accel!`, parsing, IR, validation, JSON manifests, diagnostics, and independent oracles, plus `spatial-rs-hls` for generated C++ and local harness compilation. Scala Spatial is reference-only.

**Tech Stack:** Rust stable, Cargo workspace, standard library only for M1, system `c++` for local host compilation of generated harnesses.

---

## Execution Rules

Execute Tasks 1-8 strictly sequentially. Do not dispatch Tasks 2-6 in parallel because they share IR, parser, validator, manifest, and emitter files. Task 8 review subagents are read-only and must return findings only; the main agent applies accepted patches.

As of 2026-06-26 on this machine, `cargo` and `rustc` were not on PATH. Task 1 includes the environment gate; implementation verification is blocked until a Rust toolchain is installed or found.

## Files

Create under `/Users/david/Documents/David_code/spatial-rs`:

| Path | Purpose |
|---|---|
| `Cargo.toml` | Workspace definition. |
| `README.md` | Boundary statement and verification commands. |
| `.gitignore` | Target/generated artifact ignore rules. |
| `crates/spatial-rs-core/Cargo.toml` | Core crate manifest. |
| `crates/spatial-rs-core/src/lib.rs` | Core public API and `accel!` macro. |
| `crates/spatial-rs-core/src/diagnostics.rs` | Diagnostic types and stable error codes. |
| `crates/spatial-rs-core/src/ir.rs` | Program, port, memory, statement, expression records. |
| `crates/spatial-rs-core/src/manifest.rs` | Manifest records and deterministic JSON writer/checker. |
| `crates/spatial-rs-core/src/parser.rs` | M1 DSL parser for the accepted `accel!` grammar. |
| `crates/spatial-rs-core/src/validate.rs` | Fail-closed M1 subset validator. |
| `crates/spatial-rs-core/src/oracle.rs` | Independent scalar, vector, and LUT oracles. |
| `crates/spatial-rs-hls/Cargo.toml` | HLS crate manifest. |
| `crates/spatial-rs-hls/src/lib.rs` | HLS public API. |
| `crates/spatial-rs-hls/src/emit.rs` | C++ kernel and harness emitter. |
| `crates/spatial-rs-hls/src/hygiene.rs` | Leakage-string and artifact checks. |
| `crates/spatial-rs-hls/tests/m1_codegen.rs` | End-to-end generated C++ compile/run tests. |
| `examples/ee109/Cargo.toml` | Example crate manifest. |
| `examples/ee109/src/main.rs` | Student-shaped examples that construct the five M1 programs. |

## Task 1: Toolchain Gate And Workspace Scaffold

- [ ] **Step 1: Verify Rust toolchain**

Run:

```bash
command -v cargo
command -v rustc
```

Expected on a ready machine: both commands print executable paths.

Expected on the current machine before setup: both commands fail. If they fail, install or locate Rust before continuing. Do not write production Rust code before this gate is green unless the limitation is recorded in the progress log.

- [ ] **Step 2: Create directory structure**

Run:

```bash
mkdir -p /Users/david/Documents/David_code/spatial-rs/crates/spatial-rs-core/src
mkdir -p /Users/david/Documents/David_code/spatial-rs/crates/spatial-rs-hls/src
mkdir -p /Users/david/Documents/David_code/spatial-rs/crates/spatial-rs-hls/tests
mkdir -p /Users/david/Documents/David_code/spatial-rs/examples/ee109/src
```

Expected: all directories exist.

- [ ] **Step 3: Write skeletal manifests and libraries**

Create the root `Cargo.toml`:

```toml
[workspace]
members = [
  "crates/spatial-rs-core",
  "crates/spatial-rs-hls",
  "examples/ee109",
]
resolver = "2"
```

Create `crates/spatial-rs-core/Cargo.toml`:

```toml
[package]
name = "spatial-rs-core"
version = "0.1.0"
edition = "2021"
```

Create `crates/spatial-rs-hls/Cargo.toml`:

```toml
[package]
name = "spatial-rs-hls"
version = "0.1.0"
edition = "2021"

[dependencies]
spatial-rs-core = { path = "../spatial-rs-core" }
```

Create `examples/ee109/Cargo.toml`:

```toml
[package]
name = "ee109-examples"
version = "0.1.0"
edition = "2021"

[dependencies]
spatial-rs-core = { path = "../../crates/spatial-rs-core" }
```

Create skeletal `lib.rs` files with module declarations only.

- [ ] **Step 4: Verify baseline**

Run:

```bash
cd /Users/david/Documents/David_code/spatial-rs
cargo test
```

Expected: workspace builds with zero tests.

## Task 2: Core IR And Manifest JSON

- [ ] **Step 1: Write failing IR/manifest tests**

Add this test to `crates/spatial-rs-core/src/manifest.rs`:

```rust
#[cfg(test)]
mod tests {
    use crate::ir::*;
    use crate::manifest::Manifest;

    #[test]
    fn scalar_program_manifest_json_records_ports_in_order() {
        let program = Program::scalar_add2("Lab1Part1RegExample", "argRegIn0", "argRegIn1", "argRegOut");
        let manifest = Manifest::from_program(&program).expect("manifest");
        assert_eq!(manifest.abi_schema, "ee109_abi_manifest_v0");
        assert_eq!(manifest.kernel.name, "Lab1Part1RegExample");
        assert_eq!(manifest.kernel.entry_symbol, "Lab1Part1RegExample_kernel");
        assert_eq!(manifest.scalar_inputs[0].name, "argRegIn0");
        assert_eq!(manifest.scalar_inputs[0].ordinal, 0);
        assert_eq!(manifest.scalar_inputs[1].name, "argRegIn1");
        assert_eq!(manifest.scalar_inputs[1].ordinal, 1);
        assert_eq!(manifest.scalar_outputs[0].name, "argRegOut");
        assert_eq!(manifest.scalar_outputs[0].cpp_param_type, "int *");
        assert_eq!(manifest.scalar_outputs[0].endpoint_kind, "scalar_argout");
        assert_eq!(manifest.scalar_outputs[0].write_style, "deref_once");
        assert_eq!(manifest.support_status, SupportStatus::SupportedM1);
        let json = manifest.to_json();
        assert!(json.contains("\"abi_schema\":\"ee109_abi_manifest_v0\""));
        assert!(json.contains("\"generated_artifacts\":[\"manifest.json\",\"kernel.cpp\",\"harness.cpp\"]"));
        assert!(Manifest::check_json_shape(&json).is_ok());
    }

    #[test]
    fn dense_manifest_json_records_local_memories_and_dram_bundles() {
        let program = Program::lab1_part2_dense_multiply();
        let manifest = Manifest::from_program(&program).expect("manifest");
        assert_eq!(manifest.dram_buffers[0].name, "srcFPGA");
        assert_eq!(manifest.dram_buffers[0].cpp_param_type, "const int *");
        assert_eq!(manifest.dram_buffers[0].m_axi_bundle, "gmem0");
        assert_eq!(manifest.dram_buffers[0].offset_policy, "slave");
        assert_eq!(manifest.dram_buffers[1].name, "dstFPGA");
        assert_eq!(manifest.dram_buffers[1].cpp_param_type, "int *");
        assert_eq!(manifest.dram_buffers[1].m_axi_bundle, "gmem1");
        assert_eq!(manifest.local_memories.iter().map(|m| m.name.as_str()).collect::<Vec<_>>(), vec!["b1", "b2"]);
        assert!(Manifest::check_json_shape(&manifest.to_json()).is_ok());
    }

    #[test]
    fn lut_manifest_json_records_source_shape_and_row_major_values() {
        let program = Program::lut_non_square();
        let manifest = Manifest::from_program(&program).expect("manifest");
        assert_eq!(manifest.lut_tables[0].name, "lut");
        assert_eq!(manifest.lut_tables[0].rows, 2);
        assert_eq!(manifest.lut_tables[0].cols, 4);
        assert_eq!(manifest.lut_tables[0].values_row_major, vec![1, 2, 3, 4, 5, 6, 7, 8]);
        assert!(Manifest::check_json_shape(&manifest.to_json()).is_ok());
    }
}
```

Run:

```bash
cd /Users/david/Documents/David_code/spatial-rs
cargo test -p spatial-rs-core manifest::tests
```

Expected RED: compile failure naming missing `Program`, `Manifest`, or manifest fields.

- [ ] **Step 2: Implement minimal IR and manifest writer**

Implement only the records and builder helpers required by the tests:

```rust
pub struct Program { pub kernel_name: String, pub ports: Vec<Port>, pub memories: Vec<Memory>, pub body: Vec<Stmt> }
pub struct Port { pub name: String, pub role: PortRole, pub ty: Type, pub ordinal: usize, pub shape: Option<Vec<usize>> }
pub struct Memory { pub name: String, pub kind: MemoryKind, pub element_type: Type, pub dimensions: Vec<usize>, pub values_row_major: Vec<i32> }
pub enum PortRole { ScalarInput, ScalarOutput, DramInput, DramOutput }
pub enum MemoryKind { Sram, Lut }
pub enum Type { Int }
pub enum Stmt { ScalarAssign { dst: String, expr: Expr } }
pub enum Expr { Int(i32), Read(String), Add(Box<Expr>, Box<Expr>), Mul(Box<Expr>, Box<Expr>) }
```

Implement a deterministic manual `to_json()`; do not add external dependencies in M1.

- [ ] **Step 3: Verify green**

Run the same manifest tests. Expected: pass.

## Task 3: Parser And `accel!` Macro

- [ ] **Step 1: Write failing parser tests for all five M1 positives**

Add tests to `crates/spatial-rs-core/src/parser.rs` using these exact assertions:

```rust
#[test]
fn parses_all_five_m1_positive_examples() {
    let programs = [
        parse_accel(r#"kernel Lab1Part1RegExample { inputs { argRegIn0: Int, argRegIn1: Int } outputs { argRegOut: Int } argRegOut := argRegIn0 + argRegIn1; }"#),
        parse_accel(r#"kernel Lab1Part1RegThreeInputExample { inputs { argRegIn0: Int, argRegIn1: Int, argRegIn2: Int } outputs { argRegOut: Int } argRegOut := (argRegIn0 + argRegIn1) + argRegIn2; }"#),
        parse_accel(r#"kernel Lab1Part2DramSramExample { const N: usize = 32; const TILE: usize = 16; inputs { srcFPGA: Dram<Int>[N], x: Int } outputs { dstFPGA: Dram<Int>[N] } sequential_foreach i in 0..N step TILE { let b1 = Sram<Int>[TILE]; load b1 <- srcFPGA[i..i + TILE]; let b2 = Sram<Int>[TILE]; foreach ii in 0..TILE { b2[ii] := b1[ii] * x; } store dstFPGA[i..i + TILE] <- b2; } }"#),
        parse_accel(r#"kernel Lab2Part4LUT { const ROWS: usize = 3; const COLS: usize = 3; inputs { input: Int, i: Int, j: Int } outputs { out: Int } let lut = Lut<Int>[ROWS, COLS] = [[1,2,3],[4,5,6],[7,8,9]]; out := input + lut[i, j]; }"#),
        parse_accel(r#"kernel Lab2Part4LUTNonSquareExample { const ROWS: usize = 2; const COLS: usize = 4; inputs { input: Int, i: Int, j: Int } outputs { out: Int } let lut = Lut<Int>[ROWS, COLS] = [[1,2,3,4],[5,6,7,8]]; out := input + lut[i, j]; }"#),
    ];
    for program in programs {
        assert!(program.is_ok(), "{program:?}");
    }
}
```

Add macro coverage to `crates/spatial-rs-core/src/lib.rs`:

```rust
#[test]
fn accel_macro_uses_parser_path() {
    let program = crate::accel! {
        kernel Lab1Part1RegExample {
            inputs { argRegIn0: Int, argRegIn1: Int }
            outputs { argRegOut: Int }
            argRegOut := argRegIn0 + argRegIn1;
        }
    };
    assert!(program.is_ok());
    assert_eq!(program.unwrap().kernel_name, "Lab1Part1RegExample");
}
```

Run:

```bash
cd /Users/david/Documents/David_code/spatial-rs
cargo test -p spatial-rs-core parser::tests lib_tests::accel_macro_uses_parser_path
```

Expected RED: parser and macro do not exist.

- [ ] **Step 2: Write failing parser negative tests**

Add:

```rust
#[test]
fn rejects_unsupported_m1_constructs_with_stable_codes() {
    let cases = [
        ("kernel Bad { fsm(0) { } }", "spatial:E0200"),
        ("kernel Bad { while true { } }", "spatial:E0200"),
        ("kernel Bad { for i in 0..4 { } }", "spatial:E0200"),
        ("kernel Bad { return; }", "spatial:E0200"),
        ("kernel Bad { fifo q: Int; }", "spatial:E0201"),
        ("kernel Bad { reduce x; }", "spatial:E0202"),
        ("kernel Bad { let rf = RegFile<Int>[3, 3]; }", "spatial:E0203"),
        ("kernel Bad { let lb = LineBuffer<Int>[3, 16]; }", "spatial:E0203"),
        ("kernel Bad { inputs { img: Dram<Int>[R, C] } outputs { out: Dram<Int>[R, C] } }", "spatial:E0204"),
        ("kernel Bad { inputs { x: FixPt } outputs { y: FixPt } y := x; }", "spatial:E0205"),
    ];
    for (source, code) in cases {
        let err = parse_accel(source).unwrap_err();
        assert_eq!(err[0].code, code, "{source}");
    }
}
```

- [ ] **Step 3: Implement parser and macro**

Implement a deterministic parser that recognizes only the five M1 shapes and the unsupported-token pre-scan. It is acceptable for M1 to reject valid future syntax rather than silently accept it.

- [ ] **Step 4: Verify green**

Run:

```bash
cd /Users/david/Documents/David_code/spatial-rs
cargo test -p spatial-rs-core parser::tests
cargo test -p spatial-rs-core accel_macro_uses_parser_path
```

Expected: pass.

## Task 4: Validation And Independent Oracles

- [ ] **Step 1: Write failing oracle tests**

Add to `crates/spatial-rs-core/src/oracle.rs`:

```rust
#[test]
fn scalar_oracles_cover_adversarial_vectors() {
    let add2 = Program::scalar_add2("Add2", "a", "b", "out");
    assert_eq!(eval_scalar(&add2, &[("a", 3), ("b", 5)]), Ok(8));
    assert_eq!(eval_scalar(&add2, &[("a", -7), ("b", 12)]), Ok(5));
    assert_eq!(eval_scalar(&add2, &[("a", 0), ("b", -3)]), Ok(-3));
    let add3 = Program::scalar_add3("Add3", "a", "b", "c", "out");
    assert_eq!(eval_scalar(&add3, &[("a", 3), ("b", 5), ("c", 7)]), Ok(15));
    assert_eq!(eval_scalar(&add3, &[("a", 100), ("b", -40), ("c", -60)]), Ok(0));
    assert_eq!(eval_scalar(&add3, &[("a", -1), ("b", -2), ("c", -3)]), Ok(-6));
}

#[test]
fn dense_oracle_does_not_depend_on_emitted_loop_text() {
    let src_a: Vec<i32> = (0..32).map(|i| i % 256).collect();
    let src_b: Vec<i32> = (0..32).map(|i| if i % 2 == 0 { i as i32 } else { -(i as i32) }).collect();
    let src_c = vec![13, -2, 99, 0, 7, 7, -8, 4, 42, -42, 5, 6, 7, 8, 9, 10, -1, -3, -5, -7, 11, 12, 13, 14, 15, 16, 17, 18, -19, 20, -21, 22];
    assert_eq!(dense_multiply(&src_a, 3)[31], 93);
    assert_eq!(dense_multiply(&src_b, -2)[3], 6);
    assert_eq!(dense_multiply(&src_c, 0), vec![0; 32]);
}

#[test]
fn lut_oracle_uses_semantic_2d_table_not_emitter_flatten_helper() {
    let square = vec![vec![1, 2, 3], vec![4, 5, 6], vec![7, 8, 9]];
    assert_eq!(lut_add(&square, 10, 0, 0), Ok(11));
    assert_eq!(lut_add(&square, 10, 1, 1), Ok(15));
    assert_eq!(lut_add(&square, 10, 2, 2), Ok(19));
    let nonsquare = vec![vec![1, 2, 3, 4], vec![5, 6, 7, 8]];
    assert_eq!(lut_add(&nonsquare, 10, 1, 2), Ok(17));
    assert_ne!(wrong_row_stride_canary(&nonsquare, 10, 1, 2), 17);
}
```

Run:

```bash
cd /Users/david/Documents/David_code/spatial-rs
cargo test -p spatial-rs-core oracle::tests
```

Expected RED: oracle functions missing.

- [ ] **Step 2: Write failing validation tests**

Add to `crates/spatial-rs-core/src/validate.rs`:

```rust
#[test]
fn rejected_programs_never_become_supported_manifests() {
    for source in [
        "kernel Bad { fsm(0) { } }",
        "kernel Bad { fifo q: Int; }",
        "kernel Bad { reduce x; }",
        "kernel Bad { let rf = RegFile<Int>[3,3]; }",
        "kernel Bad { let lb = LineBuffer<Int>[3,16]; }",
        "kernel Bad { inputs { img: Dram<Int>[R,C] } outputs { out: Dram<Int>[R,C] } }",
        "kernel Bad { inputs { x: Float } outputs { y: Float } y := x; }",
    ] {
        let err = crate::parse_accel(source).unwrap_err();
        assert_eq!(support_status_from_diagnostics(&err), SupportStatus::RejectedUnsupported);
    }
}
```

- [ ] **Step 3: Implement validator and oracles**

Keep `oracle.rs` independent from `spatial-rs-hls`. Do not import emitter modules or helpers into core.

- [ ] **Step 4: Verify green**

Run:

```bash
cd /Users/david/Documents/David_code/spatial-rs
cargo test -p spatial-rs-core validate::tests oracle::tests
```

Expected: pass.

## Task 5: HLS Kernel, Harness, And Structural Assertions

- [ ] **Step 1: Write failing HLS emission tests**

Add to `crates/spatial-rs-hls/tests/m1_codegen.rs`:

```rust
#[test]
fn scalar_add2_kernel_has_exact_signature_and_pragmas() {
    let program = spatial_rs_core::Program::scalar_add2("Lab1Part1RegExample", "argRegIn0", "argRegIn1", "argRegOut");
    let cpp = spatial_rs_hls::emit_kernel(&program).expect("cpp");
    assert!(cpp.contains("extern \"C\" void Lab1Part1RegExample_kernel(int argRegIn0, int argRegIn1, int *argRegOut)"));
    assert!(cpp.contains("#pragma HLS INTERFACE s_axilite port=argRegIn0 bundle=control"));
    assert!(cpp.contains("#pragma HLS INTERFACE s_axilite port=argRegIn1 bundle=control"));
    assert!(cpp.contains("#pragma HLS INTERFACE s_axilite port=argRegOut bundle=control"));
    assert!(cpp.contains("#pragma HLS INTERFACE s_axilite port=return bundle=control"));
    assert!(cpp.contains("*argRegOut = argRegIn0 + argRegIn1;"));
}

#[test]
fn dense_kernel_has_exact_pointer_pragmas_and_local_arrays() {
    let program = spatial_rs_core::Program::lab1_part2_dense_multiply();
    let cpp = spatial_rs_hls::emit_kernel(&program).expect("cpp");
    assert!(cpp.contains("const int *srcFPGA"));
    assert!(cpp.contains("int *dstFPGA"));
    assert!(cpp.contains("#pragma HLS INTERFACE m_axi port=srcFPGA offset=slave bundle=gmem0"));
    assert!(cpp.contains("#pragma HLS INTERFACE s_axilite port=srcFPGA bundle=control"));
    assert!(cpp.contains("#pragma HLS INTERFACE m_axi port=dstFPGA offset=slave bundle=gmem1"));
    assert!(cpp.contains("#pragma HLS INTERFACE s_axilite port=dstFPGA bundle=control"));
    assert!(cpp.contains("#pragma HLS INTERFACE s_axilite port=return bundle=control"));
    assert!(cpp.contains("int b1[16];"));
    assert!(cpp.contains("int b2[16];"));
}

#[test]
fn nonsquare_lut_kernel_uses_cols_as_flatten_stride() {
    let program = spatial_rs_core::Program::lut_non_square();
    let cpp = spatial_rs_hls::emit_kernel(&program).expect("cpp");
    assert!(cpp.contains("static const int lut[8]"));
    assert!(cpp.contains("lut[(i * 4) + j]"));
    assert!(!cpp.contains("lut[(i * 2) + j]"));
}

#[test]
fn rejected_programs_have_no_kernel_artifact() {
    let diagnostics = spatial_rs_core::parse_accel("kernel Bad { fifo q: Int; }").unwrap_err();
    assert!(spatial_rs_hls::emit_rejected_kernel("Bad", &diagnostics).is_err());
}
```

Run:

```bash
cd /Users/david/Documents/David_code/spatial-rs
cargo test -p spatial-rs-hls --test m1_codegen scalar_add2_kernel_has_exact_signature_and_pragmas dense_kernel_has_exact_pointer_pragmas_and_local_arrays nonsquare_lut_kernel_uses_cols_as_flatten_stride rejected_programs_have_no_kernel_artifact
```

Expected RED: HLS crate API missing.

- [ ] **Step 2: Implement emitters**

Implement `emit_kernel`, `emit_harness`, and rejected-kernel behavior using validated IR plus manifest fields. Harness expected values must come from `spatial-rs-core::oracle`.

- [ ] **Step 3: Verify green**

Run:

```bash
cd /Users/david/Documents/David_code/spatial-rs
cargo test -p spatial-rs-hls --test m1_codegen
```

Expected: pass.

## Task 6: Local C++ Compile/Run Gate

- [ ] **Step 1: Add failing compile/run integration tests**

Extend `m1_codegen.rs`:

```rust
#[test]
fn generated_positive_harnesses_compile_and_run() {
    for program in [
        spatial_rs_core::Program::scalar_add2("Lab1Part1RegExample", "argRegIn0", "argRegIn1", "argRegOut"),
        spatial_rs_core::Program::scalar_add3("Lab1Part1RegThreeInputExample", "argRegIn0", "argRegIn1", "argRegIn2", "argRegOut"),
        spatial_rs_core::Program::lab1_part2_dense_multiply(),
        spatial_rs_core::Program::lut_square(),
        spatial_rs_core::Program::lut_non_square(),
    ] {
        let result = spatial_rs_hls::compile_and_run_harness(&program).expect("compile/run");
        assert!(result.stdout.contains("PASS"), "{}", result.stdout);
        assert_eq!(result.status_code, 0);
    }
}
```

Run:

```bash
cd /Users/david/Documents/David_code/spatial-rs
cargo test -p spatial-rs-hls --test m1_codegen generated_positive_harnesses_compile_and_run -- --nocapture
```

Expected RED: compile/run helper missing or artifacts not emitted.

- [ ] **Step 2: Implement compile/run helper**

Write generated artifacts under `/Users/david/Documents/David_code/spatial-rs/target/spatial-rs-hls/<kernel>/`. Invoke:

```bash
c++ -std=c++11 -Wall -Wextra -Wno-unknown-pragmas kernel.cpp harness.cpp -o harness
```

If `c++` is unavailable, fail with a clear error. Do not silently skip.

- [ ] **Step 3: Verify green**

Run the same compile/run test. Expected: all five generated harnesses compile, run, print `PASS`, and exit `0`.

## Task 7: Examples And README

- [ ] **Step 1: Write examples**

`examples/ee109/src/main.rs`:

```rust
use spatial_rs_core::accel;

fn main() {
    let examples = [
        accel! { kernel Lab1Part1RegExample { inputs { argRegIn0: Int, argRegIn1: Int } outputs { argRegOut: Int } argRegOut := argRegIn0 + argRegIn1; } },
        accel! { kernel Lab1Part1RegThreeInputExample { inputs { argRegIn0: Int, argRegIn1: Int, argRegIn2: Int } outputs { argRegOut: Int } argRegOut := (argRegIn0 + argRegIn1) + argRegIn2; } },
        accel! { kernel Lab1Part2DramSramExample { const N: usize = 32; const TILE: usize = 16; inputs { srcFPGA: Dram<Int>[N], x: Int } outputs { dstFPGA: Dram<Int>[N] } sequential_foreach i in 0..N step TILE { let b1 = Sram<Int>[TILE]; load b1 <- srcFPGA[i..i + TILE]; let b2 = Sram<Int>[TILE]; foreach ii in 0..TILE { b2[ii] := b1[ii] * x; } store dstFPGA[i..i + TILE] <- b2; } } },
        accel! { kernel Lab2Part4LUT { const ROWS: usize = 3; const COLS: usize = 3; inputs { input: Int, i: Int, j: Int } outputs { out: Int } let lut = Lut<Int>[ROWS, COLS] = [[1,2,3],[4,5,6],[7,8,9]]; out := input + lut[i, j]; } },
        accel! { kernel Lab2Part4LUTNonSquareExample { const ROWS: usize = 2; const COLS: usize = 4; inputs { input: Int, i: Int, j: Int } outputs { out: Int } let lut = Lut<Int>[ROWS, COLS] = [[1,2,3,4],[5,6,7,8]]; out := input + lut[i, j]; } },
    ];

    for program in examples {
        let program = program.expect("M1 example parses");
        println!("{} supported_m1", program.kernel_name);
    }
}
```

- [ ] **Step 2: Write README boundary**

README must state:

- Rust-hosted Spatial-like DSL.
- M1 supports scalar add, fixed dense DRAM/SRAM, and LUT examples.
- Scala is reference-only.
- Local C++ compile/run is not vendor HLS synthesis.
- Verification command is `cargo test`.

- [ ] **Step 3: Verify examples**

Run:

```bash
cd /Users/david/Documents/David_code/spatial-rs
cargo run -p ee109-examples
```

Expected: five lines ending in `supported_m1`.

## Task 8: Review, Commit, And Post-M1 Boundary

- [ ] **Step 1: Full verification**

Run:

```bash
cd /Users/david/Documents/David_code/spatial-rs
cargo test
cargo run -p ee109-examples
```

Expected: all tests and examples pass.

- [ ] **Step 2: Generated-artifact hygiene scan**

Run:

```bash
rg -n "FringeContext|TopHost|Chisel|Verilog|DRAMSim|vcs|instrument" /Users/david/Documents/David_code/spatial-rs/target/spatial-rs-hls -g '*.cpp' -g '*.hpp' -g '*.h'
```

Expected: no matches.

- [ ] **Step 3: Dispatch read-only subagent review**

Use GPT-5.5 xhigh subagents for:

- spec compliance against `[[2026-06-26-rust-ee109-mvp-design]]`
- code quality and API review
- generated C++/oracle independence review

- [ ] **Step 4: Commit M1 if reviewers approve**

Commit the Rust workspace and update the vault progress log with exact verification results and the host-C++ boundary.

- [ ] **Step 5: Stop M1 plan and open a separate next-slice record**

Do not extend this M1 plan into FSM, FIFO, reduction, or Lab3. Create a separate post-M1 design/plan for the next EE109 feature slice so the full-MVP loop can continue without blurring the M1 support claim.
