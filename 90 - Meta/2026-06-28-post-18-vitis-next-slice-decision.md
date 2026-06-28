---
type: decision
project: spatial-spec
date: 2026-06-28
status: current
related:
  - "[[2026-06-27-rust-spatial-rewrite-roadmap]]"
  - "[[84 - EE109 HLS Stability Matrix]]"
  - "[[progress-log]]"
---

# Post-18 Vitis Next Slice Decision

## Current Evidence

The Rust rewrite now has an 18-program Vitis 2025.1 checkpoint in
`/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-06-28-mem-reductions-v0/`.
All 18 programs passed `csim_design` and `csynth_design` on the EC2 Vitis host.

That evidence covers:

- the original accepted adapter baseline
- `ScalarExpr v0`
- `Dense1dScalarMul v0`
- `LutLookup v0`
- `Dram2dCopy v0`
- `ControlFsm v0`
- `Stencil2d v0`
- `ScalarReduce v0`
- `ScalarFold v0`
- the local all-ones `MemReduceFill v0` and `MemFoldFill v0` semantic canaries

The evidence does not prove board execution, Vivado implementation,
post-implementation timing closure, generic Spatial source compatibility,
generic streams, generic reductions/folds, fixed-point GEMM, or general
memory/effect scheduling.

## Options Reviewed

Six GPT-5.5 xhigh reviewers inspected the next-slice choice after the
18-program run.

1. FIFO/stream v0: closest remaining EE109 lab-facing feature. It should be a
   narrow local FIFO tile/copy or tile-scale slice using real `hls::stream`,
   not generic stream support.
2. GEMM/fixed-point: important milestone, but too broad now. Real Lab2 GEMM
   needs fixed-point types, rank-2 DRAM/SRAM, dynamic or tail dimensions,
   rank-2 memory folds, and eventually `par` policy.
3. Compiler foundation: a behavior-preserving classifier/HIR guardrail slice
   reduces risk before adding another semantic feature.
4. Synthetic int GEMM: backend-convenient because it can reuse pointer/local
   array HLS emission, but it does not directly support the real Lab2 GEMM
   source shape.

## Decision

Proceed in this order:

1. Refresh stale docs and record this post-18 decision.
2. Do one small compiler-foundation guardrail slice.
3. Implement FIFO v0 as the next user-visible lab-facing feature.
4. Run local gates, then a 19-program EC2 Vitis checkpoint for FIFO v0.
5. Return to fixed-point and GEMM after FIFO and classifier/module boundaries
   are boring.

The FIFO slice must be named narrowly, for example `FifoPipe16` or
`FifoTileScalarMul v0`. It must not claim generic streams, AXI stream ports,
LIFO, back-pressure modeling, `DATAFLOW`, `PIPELINE`, `UNROLL`, or arbitrary
producer/consumer scheduling.

The compiler-foundation slice should preserve the current 18-program behavior.
No new Vitis evidence is required if generated HLS membership and C++ output do
not change.

## Outcome

The planned order was followed. The classifier/HIR guardrail slice landed
without changing Vitis membership, then FIFO v0 landed as the narrow
`Fifo1dTileScalarMul v0` semantic slice with `FifoTileScale32` as the Rust-DSL
representative. The follow-up EC2 Vitis checkpoint on 2026-06-28 passed all 19
validation programs with `csim=true` and `csynth=true`; evidence is recorded in
`/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-06-28-fifo-v0/`.

Boundary after outcome: FIFO v0 proves narrow Rust-DSL tile-scale FIFO lowering
to vendor-accepted HLS C++; it still does not claim original Scala
`Lab1Part4FIFOExample` source compatibility, generic FIFO/streams, AXI stream
ports, LIFO, back-pressure modeling, `DATAFLOW`, `PIPELINE`, `UNROLL`,
arbitrary producer/consumer scheduling, board execution, Vivado implementation,
place-and-route, timing closure, or generic Spatial language coverage.

## Rationale

The project goal is a Rust compiler for a Spatial-like DSL that emits HLS C++,
not a collection of fixture templates. After the 18-program checkpoint, the
highest risk is classifier and HIR brittleness, followed by accidentally
overclaiming FIFO or GEMM support.

FIFO is the next natural EE109-facing feature because Lab1Part4 is close to the
already-working dense DRAM/SRAM tile shape. The honest HLS boundary is real
`hls::stream` emission with a local host-compile strategy and strict
enqueue/dequeue count checks.

GEMM remains a major milestone, but doing it next would combine too many new
subsystems. A tiny int GEMM would be useful as an HLS body probe, but it would
not satisfy the real fixed-point Lab2 GEMM direction.

## Immediate Work

- Update the Rust repo architecture docs so "current adapter set" language does
  not point at the old eight-adapter baseline.
- Update the research roadmap and stability matrix to mention the 18-program
  MemReduce/MemFold canary checkpoint.
- Write the compiler-foundation implementation plan in the Rust repo.
- Keep the next implementation fail-closed and evidence-driven.
