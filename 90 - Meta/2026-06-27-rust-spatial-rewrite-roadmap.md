---
type: design
project: spatial-spec
date: 2026-06-27
status: active
related:
  - "[[2026-06-26-rust-first-spatial-dsl-overlay]]"
  - "[[2026-06-26-rust-ee109-mvp-design]]"
  - "[[2026-06-27-rust-lab3-convolution-slice-contract]]"
  - "[[84 - EE109 HLS Stability Matrix]]"
  - "[[60 - EE109 HLS Lowering Map]]"
---

# Rust Spatial Rewrite Roadmap

## Framing

The long-term goal is a Rust rewrite of Spatial with HLS C++ as the primary backend. EE109 labs are the first acceptance ladder because they are concrete teaching examples, but they are not the final compiler boundary.

The current `spatial-rs` work should therefore be treated as a tracer slice:

- keep the working host-C++ fixture adapters as regression evidence
- avoid growing the compiler by adding endless exact lab recognizers
- promote lab adapters into reusable frontend, HIR, IR, lowering, and HLS modules
- preserve fail-closed diagnostics until a construct has a selected semantic and HLS story

## Current Position

`spatial-rs` currently has accepted fixture adapters for scalar add, dense 1-D DRAM/SRAM multiply, LUTs, one exact FSM, rank-2 copy groundwork, and one direct Lab3 convolution semantic adapter.

This proves useful local compiler plumbing:

- checked Rust construction
- ABI manifest emission
- independent oracles
- HLS-style C++ emission
- local host-C++ harness compile/run
- explicit rejection of unsupported forms

It does not yet prove:

- general Spatial parsing
- reusable lowering for `LineBuffer`, `RegFile`, `Reduce`, `par`, FIFO, or GEMM
- vendor Vitis/Vivado `csim` or `csynth`
- timing, resource, RTL, or board readiness

## Architecture Target

```text
accel! DSL source
  -> lexer/parser
  -> AST with spans
  -> typed Spatial HIR
  -> subset classifier and validators
  -> checked semantic IR
  -> manifest, ABI, partition, schedule, and provenance ledgers
  -> HLS lowering passes
  -> HLS C++ kernel and harness emission
  -> local host-C++ gate
  -> Vitis/Vivado csim and csynth gates
```

The student surface should remain a hardware DSL island. Rust is the compiler implementation language, not the language students need to master before learning hardware design.

## Vocabulary

- `accepted fixture adapter`: exact lab-shaped program accepted and checked through host-C++.
- `supported feature`: reusable semantic module with lab and non-lab tests, legal parameter perturbations, fail-closed negatives, and non-template HLS lowering.
- `host_cpp_structural_gate`: generated kernel and harness compile/run with the local system compiler.
- `vitis_csim_validated`: generated Vitis/Vivado project runs `csim_design`.
- `vitis_csynth_validated`: generated Vitis/Vivado project runs `csynth_design`, and reports record tool version, part, clock, latency, resource use, and accepted II.

Use `accepted fixture adapter` for the current `ProgramKind::LabX...` style cases unless a feature has graduated through reusable semantics.

## Feature Ladder

1. Scalar integer ports and arithmetic.
2. Dense 1-D DRAM/SRAM load-compute-store.
3. LUT lookup and row-major indexing.
4. FIFO and stream lowering.
5. Scalar `Fold` and `Reduce`.
6. `MemReduce` and `MemFold`.
7. FSMs with conditions, state updates, SRAM writes, and mux-like expressions.
8. 2-D DRAM/SRAM, fixed-point types, dynamic dimensions, and GEMM tiling.
9. Local-window/stencil lowering for `LineBuffer`, `RegFile`, `Reduce`, `mux`, `abs`, and `par`.
10. HLS performance surface: `PIPELINE`, `UNROLL`, `ARRAY_PARTITION`, vector ports, project Tcl, and report parsing.

## Near-Term Manager Plan

1. Reword repo docs so they describe the Rust rewrite correctly and stop overclaiming fixture adapters as general support.
2. Add a source model for `parse_accel(&str)`: source id, byte ranges, line/column lookup, and diagnostic labels. Keep `macro_rules! accel` on `stringify!` until a proc-macro is worth its cost.
3. Add a real frontend path: tokenization, AST, source spans, and typed HIR for scalar ports, LUTs, dense 1-D DRAM/SRAM, expressions, loops, loads, and stores.
4. Add a first-class EE109 subset classifier that consumes HIR and produces checked semantic modules or fixture adapters.
5. Decouple semantic feature identity from lab kernel names before adding non-lab semantic-equivalent tests.
6. Route scalar/LUT/dense accepted adapters through `AST -> HIR -> EE109 subset classifier -> checked Program` while keeping current host-C++ outputs stable.
7. Keep Lab3 convolution explicitly transitional and opaque until reusable local-window/stencil lowering exists.
8. Add HLS project artifact generation in dry-run mode: top name, part, clock, kernel/harness paths, and `run_hls.tcl`.
9. Add optional Vitis/Vivado `csim_design` execution once a machine has the toolchain.
10. Add `csynth_design` and report parsing for scalar/LUT/dense before claiming Lab3-style performance or synthesis readiness.

## Guardrails

- No new `compact_source(EXACT_FIXTURE)` cases outside a clearly named fixture-adapter layer.
- No new `ProgramKind::LabX...` without a retirement criterion.
- No generic support claim until there is at least one non-lab semantic test.
- No vendor HLS claim without fresh tool evidence.
- No direct port of Scala `HLSGen`; preserve its useful semantics and fixtures, but design Rust modules around frontend, HIR, validation, manifests, lowering, diagnostics, and HLS emission.
