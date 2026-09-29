---
type: design
project: spatial-spec
date: 2026-06-26
status: accepted-framing
m1_resolution: "[[2026-06-26-rust-ee109-mvp-design]]"
supersedes:
  - "[[2026-04-21-spatial-spec-design]]"
  - "[[2026-06-25-ee109-hls-mvp-plan]]"
related:
  - "[[84 - EE109 HLS Stability Matrix]]"
  - "[[04-ee109-hls-target-corpus]]"
  - "[[55 - EE109 ABI Manifest v0]]"
  - "[[60 - EE109 HLS Lowering Map]]"
---

> [!note] Historical framing; architecture proposal updated
> The June framing remains historical. [[D-26-final-architecture|The September proposal]] selects source-captured Python kernels over a Rust semantic core, pending professor approval. Its surface recommendation replaces the earlier research position; it does not retroactively claim an approved implementation change.

# Rust-First Spatial DSL Overlay

## Purpose

This overlay reconciles three framings that now coexist in the vault:

1. The original long-term goal: a Rust rewrite that targets HLS instead of Chisel.
2. The June EE109-first implementation pivot: prove selected lab examples can compile to HLS-style C++ before settling full-language design.
3. The current decision: use Rust as the compiler substrate while preserving a Spatial-like pedagogical DSL surface.

The active framing is now:

> Build a Rust-hosted Spatial-like DSL and compiler for the EE109 subset. Rust owns the IR, validation, manifests, lowering, diagnostics, and HLS C++ emission. The student-facing surface should expose hardware concepts, not ordinary Rust complexity.

This does not discard the existing Spatial research. The spec and mapping work remain the semantic reference for the Rust design.

## Non-Goals

- Do not make students learn idiomatic Rust before learning hardware design.
- Do not attempt source-compatible Scala Spatial syntax.
- Do not claim full Spatial compatibility in the first milestone.
- Do not claim Vitis/Vivado synthesis readiness until an actual vendor HLS gate exists.
- Do not encode every hardware property into Rust generics or trait bounds.
- Do not use Python as the compiler-core owner. Python remains useful for golden models, notebooks, orchestration, or comparison tests.

## Design Decision

Use a hybrid Rust architecture:

| Layer | Decision |
|---|---|
| Student accelerator surface | A small `accel! { ... }` DSL island for hardware code. |
| Host/test surface | Normal Rust host code, with optional Python utilities for golden data. |
| Compiler core | Rust typed IR, validators, lowering passes, ABI manifest, C++ HLS emitter. |
| Backend target | Generated Vitis-oriented HLS-style C++ pending vendor gates, not Rust HLS. |
| Verification | Local host-C++ compile/run first; Vitis `csim_design` and `csynth_design` later. |

The macro island exists to prevent Rust details from dominating the teaching surface. Rust closures and builders remain useful internally and for tests, but the student examples should read as hardware:

```rust
accel! {
  sequential_foreach i in (0..32).step(16) {
    let b1 = Sram<Int>(16);
    load b1 <- src[i..i + 16];

    let b2 = Sram<Int>(16);
    foreach ii in 0..16 {
      b2[ii] = b1[ii] * x;
    }

    store dst[i..i + 16] <- b2;
  }
}
```

This syntax is intentionally a DSL, not ordinary Rust. The compiler should parse it into a Spatial AST with source spans and issue domain diagnostics before obscure Rust trait, borrow, or lifetime errors become the main feedback loop.

## Research Portability

The existing vault work is still valuable for Rust.

| Artifact group | Rust-first use |
|---|---|
| `10 - Spec/10 - Language Surface/` | Defines the student-visible hardware concepts to preserve. |
| `10 - Spec/20 - Semantics/` | Defines the behavioral contract: effects, scheduling, memory, data types, host boundary. |
| `10 - Spec/30 - IR/` | Provides the conceptual staged IR and node families to re-express in Rust. |
| `10 - Spec/40 - Compiler Passes/` | Provides invariants and pass ideas; port selectively, not wholesale. |
| `30 - HLS Mapping/` | Provides backend lowering policy and deferral boundaries. |
| `20 - Research Notes/30 - MVP Examples Analysis/` | Provides the EE109 feature floor and teaching corpus. |
| Scalagen notes | Reference semantics only, especially for future compatibility mode. |
| Chiselgen/Fringe notes | Reference-only for legacy behavior; not the Rust/HLS contract. |

The old labels `clean` and `rework` are too coarse for the Rust design. Future notes should distinguish:

- `surface-clean`: the hardware idea maps cleanly to a Rust DSL surface.
- `semantic-portable`: the Spatial meaning can be preserved.
- `backend-pending`: HLS lowering still needs work.
- `reference-only`: useful for understanding old Spatial, not something to port.

## Student Surface Rules

The teaching surface should expose:

- `ArgIn`, `ArgOut`
- `Dram`, `Sram`, `Reg`, `Lut`
- `Accel`
- `foreach`, `sequential_foreach`
- `load`, `store`
- integer arithmetic, comparisons, `mux`, `abs`
- `par` later, once partition planning exists

The teaching surface should hide:

- lifetimes, borrowing, `&mut`, and ownership puzzles
- trait bounds, `where` clauses, associated types, and turbofish syntax
- proc-macro internals
- vendor pragmas
- raw `Result` and `Option` ceremony in examples
- advanced const-generic encodings of rank, banks, and schedules

Internal Rust can still use strong types, enums, traits, arenas, `serde`, and exhaustive matches. The rule is about what students see.

## Compiler Architecture

The Rust rewrite should be manifest-first and fail-closed.

| Module | Responsibility |
|---|---|
| `frontend` | Parse the Rust DSL surface into a Spatial-like AST/HIR with spans. |
| `ir` | Store symbols, blocks, ops, memory records, controller trees, and expression DAGs. |
| `validator` | Enforce the EE109 subset, type rules, memory shape rules, and unsupported-feature diagnostics. |
| `lower` | Normalize host/kernel boundary, dense transfers, loops, LUTs, and simple local memories. |
| `abi` | Produce `ee109_abi_manifest_v0`-style records for scalar args, outputs, DRAM buffers, dimensions, transfers, and tests. |
| `hls_emit` | Emit C++ kernels, pragmas, local arrays, and helper code. |
| `harness` | Emit local host-C++ harnesses with independent oracles where possible. |
| `diagnostics` | Own stable error codes, spans, help text, and fail-closed unsupported-feature messages. |

The first implementation should not be a direct port of the current Scala `HLSGen`. The current HLS work is useful as an acceptance baseline and C++ shape reference, but the Rust code should split validation, manifests, emission, and testing into separate modules.

## Backend Policy

Generate C++ HLS from Rust IR.

Initial interface subset:

- one `extern "C"` top function per selected `Accel`
- `s_axilite` ports for scalar inputs, scalar output endpoints, pointer control, and return
- `m_axi` ports for DRAM pointer data paths
- local C++ arrays for SRAM/LUT
- `ARRAY_PARTITION`, `UNROLL`, and `PIPELINE` only when the selected subset proves they are safe

Verification order:

1. Rust IR/manifest validator accepts only selected shapes.
2. Generated C++ kernel plus harness compiles locally with ordinary `c++`/`clang++` and runs.
3. Vitis `csim_design` runs from generated Tcl.
4. Vitis `csynth_design` runs and reports interface/latency/resource status.
5. RTL cosim and board integration remain later work.

The existing local HLS lane is a host-C++ sanity gate, not proof of vendor synthesis. `[[84 - EE109 HLS Stability Matrix]]` remains the boundary statement until a Vitis gate exists.

## First Milestone

Milestone M1 is an EE109 teaching subset, not a full rewrite.

M1 positive examples:

1. Lab1Part1 two-input scalar add.
2. Lab1Part1 three-input scalar add.
3. Lab1Part2 fixed `N = 32`, `tileSize = 16` dense DRAM/SRAM multiply.
4. Lab2 square LUT.
5. Lab2 non-square LUT stride check.

M1 negative examples must fail closed:

- FSM/state-machine lowering
- FIFO/LIFO
- Fold/Reduce/MemReduce
- RegFile/LineBuffer/Lab3 local-memory surfaces
- sparse gather/scatter
- non-integer fixed/floating point
- explicit banking hints and full DSE/II parity
- claims of Vitis/Vivado readiness

Passing M1 means:

> The Rust rewrite has a usable EE109 teaching slice for scalar, dense memory, and LUT concepts, with local C++ HLS-style harnesses and stable diagnostics.

It does not mean:

> Full Spatial compatibility, Lab3 readiness, vendor synthesis success, or board integration.

## Diagnostics Contract

Diagnostics must use hardware-language terms first.

Bad:

```text
the trait bound Expr<Int>: IndexMut<_> is not satisfied
```

Good:

```text
[spatial:E0104] staged SRAM writes are only allowed inside accel! blocks
help: move this assignment inside accel! or use host-side vector code
```

Required diagnostic classes:

- unsupported control form
- unsupported memory kind
- unsupported rank or dynamic shape
- illegal host/kernel boundary use
- unsupported HLS target feature
- verifier/oracle mismatch
- vendor HLS gate failure

Rust errors will still exist, but the design should make domain diagnostics the normal path for student mistakes.

## Decisions Resolved For M1

`[[2026-06-26-rust-ee109-mvp-design]]` resolves the implementation-cut decisions for the first Rust milestone:

1. `accel!` uses a constrained Spatial-like DSL island captured by `stringify!` for M1.
2. Internal builders are allowed for tests, but canonical M1 examples must pass through `accel!`.
3. Manifest serialization is JSON for M1, with exact fields tested before C++ emission.
4. The workspace starts as core plus HLS crates; CLI is deferred.
5. HLS output is host-C++ checked and structurally asserted, not Vitis/Vivado proven.
6. Python is not required for M1; independent oracles live in Rust core.

## Next Action

Implement the M1 plan in `[[2026-06-26-rust-ee109-mvp-implementation-plan]]`, then open a separate post-M1 design record for the next EE109 feature slice.
