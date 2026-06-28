---
type: plan
project: spatial-spec
date: 2026-06-28
---

# Post-FIFO Compiler Foundation Plan

## Current Truth

The Rust rewrite is on branch `David/HLS-spatial` with a 19-program Vitis 2025.1 checkpoint recorded under `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-06-28-fifo-v0/`.

The newest supported semantic slice is narrow `Fifo1dTileScalarMul v0` through the Rust-DSL representative `FifoTileScale32`. This proves Vitis `csim_design` and `csynth_design` for the current validation lane, not original Scala `Lab1Part4FIFOExample`, generic FIFO/streams, AXI streams, back-pressure, board execution, Vivado implementation, timing closure, or broad Spatial language coverage.

## Manager Decision

The next phase is compiler foundation, not another ad hoc feature promotion.

Six GPT-5.5 xhigh reviewers converged on this framing:

- keep checked `Program` as the HLS contract
- make source-to-HIR-to-Program an explicit compiler spine
- add crate-private HIR facts before building a full typed `ResolvedHir`
- use FIFO v0 as the first vertical proof for local memory/effect facts
- keep HLS backend templates closed and Vitis-stable
- postpone generic FIFO, generic reductions, generic FSM, fixed-point, GEMM, and board/timing claims

## First Slice

Implement a behavior-preserving post-FIFO foundation slice:

1. Add `compiler::compile_source(&SourceFile)` returning both `HirProgram` and checked `Program`.
2. Add `hir::facts::HirFacts` for constants, ports, loop-local memories, and FIFO enqueue/dequeue effects.
3. Make `classify_fifo_tile_scalar_mul` consume the HIR facts index for FIFO local-memory/effect discovery.
4. Add regression tests for the compiler spine and FIFO facts.
5. Update repo docs to point future agents away from the stale pre-FIFO 14-program frontend/HIR plan.

This slice intentionally claims no new Spatial syntax and no new Vitis evidence.

## Next Slice

The stage-aware `parse_accel` route is now complete: parser entry now calls the compiler spine and preserves current fail-closed diagnostics across parse, HIR-lowering, and classification failures.

The remaining next slice is to replace string-based candidate exceptions with HIR-recursive feature signals. Only after that should the project design and implement a larger typed `ResolvedHir` pass with symbol IDs, scoped lookups, expression types, loop-domain facts, memory references, and effect summaries.

Suggested semantic diagnostics for that later pass:

- `spatial:E0301` unresolved symbol
- `spatial:E0302` duplicate or unsupported shadowing
- `spatial:E0303` type or lvalue mismatch
- `spatial:E0304` memory rank or index mismatch
- `spatial:E0305` non-static or invalid dimension/domain
- `spatial:E0306` unsupported memory kind/rank in current subset
- `spatial:E0307` unsupported scalar expression/operator/call
- `spatial:E0308` unsupported loop domain, step, or par factor
- `spatial:E0309` unsupported or imbalanced FIFO effect
- `spatial:E0310` side effect in unsupported context

## Verification Standard

For behavior-preserving compiler-foundation slices:

```sh
cargo fmt --all -- --check
cargo test --locked
cargo clippy --all-targets --locked -- -D warnings
cargo run -p ee109-examples --locked --bin run-vitis-validation -- --plan-only --mode both --out target/vitis-validation-post-fifo-foundation-plan
git diff --check
```

Fresh EC2 Vitis execution is required only when emitted C++, manifest semantics, validation membership/order, checked `Program` shape, or a documented vendor-HLS claim changes.
