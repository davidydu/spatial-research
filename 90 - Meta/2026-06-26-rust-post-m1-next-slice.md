---
type: design
project: spatial-spec
date: 2026-06-26
status: active
depends_on:
  - "[[2026-06-26-rust-ee109-mvp-design]]"
  - "[[2026-06-26-rust-ee109-mvp-implementation-plan]]"
---

# Rust Post-M1 Next Slice Decision

## Current State

Rust M1 is implemented and committed in `/Users/david/Documents/David_code/spatial-rs` at `75131f9`.

Supported M1 examples:

- `Lab1Part1RegExample`
- `Lab1Part1RegThreeInputExample`
- `Lab1Part2DramSramExample`
- `Lab2Part4LUT`
- `Lab2Part4LUTNonSquareExample`

Verified gates:

- `cargo test`
- `cargo run -p ee109-examples`
- `cargo clippy --all-targets -- -D warnings`
- generated C++ hygiene scan over `target/spatial-rs-hls`

Boundary remains local host-C++ only, not vendor HLS synthesis.

## Subagent Recommendations

Three GPT-5.5 xhigh read-only subagents reviewed the next step.

| Reviewer angle | Recommendation | Rationale |
|---|---|---|
| EE109 feature ordering | Pick `Lab2Part3BasicCondFSM` next | Small real lab target that adds FSM, `Reg`, conditionals, SRAM writes, and dense store without Lab3 complexity. |
| Lab3 decomposition | Pick fixed non-square 2-D DRAM row-major copy next | Lab3 depends on trustworthy 2-D row-major DRAM/oracle/harness before LineBuffer, RegFile, reductions, or `par`. |
| Rust API/DSL architecture | Harden `Program` and parser before either feature | Public mutable IR and exact string parser will become a liability if the next feature is added directly. |

## Manager Decision

The next implementation slice is internal architecture hardening:

> Make the Rust compiler API use checked programs and a small structured parser path before adding Lab2 FSM or Lab3 2-D DRAM.

This does not change the lab-feature priority. It removes a known reliability risk first so the next feature slice does not add more support on top of public mutable IR and exact string matching.

## Hardening Acceptance Criteria

The hardening slice must:

1. Make `Program`, `Port`, and `Memory` fields private or crate-private.
2. Expose read-only accessors for kernel name, kind, ports, memories, and body.
3. Add a `ProgramKind` enum for current M1 kinds:
   - `ScalarAdd2`
   - `ScalarAdd3`
   - `Dense1dTileMultiply`
   - `Lut2dSquare`
   - `Lut2dNonSquare`
4. Route manifest and HLS emission through checked `Program` values instead of defending against arbitrary public mutation.
5. Add identifier-safety checks before HLS emission:
   - invalid kernel names
   - invalid port names
   - duplicate names
   - duplicate ordinals
   - malformed shapes
6. Replace exact whole-source matching with a tiny tokenizer plus shape recognizers for the five current M1 forms.
7. Preserve fail-closed diagnostics for generic FSM, FIFO, Reduce/Fold, rank-2 DRAM, RegFile, and LineBuffer until their selected slices are opened.

Required tests:

- Existing M1 tests remain green.
- External example code cannot construct or mutate raw `Program`, `Port`, or `Memory` fields.
- Parser accepts harmless whitespace/formatting variants of the five M1 forms.
- Parser rejects malformed near-misses with stable diagnostics.
- Manifest and HLS emission still check support before C++ text or artifacts.
- Full gate remains: `cargo test`, `cargo run -p ee109-examples`, `cargo clippy --all-targets -- -D warnings`, generated C++ hygiene scan.

## Feature Slice After Hardening

After the hardening slice is committed, choose one of:

1. `Lab2Part3BasicCondFSM`, if the priority is breadth across real EE109 lab examples.
2. `Lab3Part0MatrixCopyRowMajor`, if the priority is direct progress toward the Lab3 convolution stack.

The manager preference after hardening is `Lab2Part3BasicCondFSM`: it is a complete local EE109 test and gives the Rust compiler a controlled control-flow slice. The Lab3 path should start immediately after that with fixed 2-D row-major DRAM copy.
