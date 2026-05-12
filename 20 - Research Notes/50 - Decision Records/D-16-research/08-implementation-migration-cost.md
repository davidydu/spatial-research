---
type: "research"
decision: "D-16"
angle: 8
title: "Implementation Cost and Migration Strategy"
date: 2026-04-27
---

# Implementation Cost and Migration Strategy

## Baseline Cost Surface

The implementation surface is wider than a single bounds check. ScalaGen opens OOB logs around generated execution, and `OOB.readOrElse` / `writeOrElse` catch `ArrayIndexOutOfBoundsException`; reads return the caller-provided invalid value, while writes log and disappear (`emul/src/emul/OOB.scala:19-38`; `src/spatial/codegen/scalagen/ScalaGenMemories.scala:14-21`). The generated wrapper repeats the read fallback by emitting `invalid(tp)` on caught OOB reads (`src/spatial/codegen/scalagen/ScalaGenMemories.scala:36-50`). The vault already treats this as normative simulator behavior but separates synthesis: HLS may assert or assume in-bounds access ([[40 - Memory Semantics]], lines 61-69; [[30 - Memory Simulator]], lines 104-116; [[20 - Open Questions]], lines 2027-2037).

Invalid values are therefore not optional runtime decoration. Fixed-point invalid is a real `FixedPoint(-1, valid=false, fmt)`, operations propagate validity, and invalid prints as `X`; `Bool` does the same validity propagation and `X` printing (`emul/src/emul/FixedPoint.scala:14-32`, `emul/src/emul/FixedPoint.scala:102-112`, `emul/src/emul/FixedPoint.scala:161`; `emul/src/emul/Bool.scala:3-17`). Any compatibility mode that returns invalid on OOB must implement typed validity, not `Option<T>` alone.

## Policy Cost Comparison

`sim_compat_log_invalid` as the default has the lowest migration cost for existing ScalaGen parity. It preserves old goldens, OOB write tolerance, logs, and downstream X propagation. Its implementation cost is medium: every SRAM, RegFile, LUT, LineBuffer, DRAM dense/sparse transfer, and alias-selected target needs a shared checked-access helper. Its strategic cost is that users may mistake it for hardware-faithful behavior.

`sim_strict_trap` as the default is simple mechanically but expensive socially: it breaks Scalagen-compatible programs and tests that intentionally rely on non-aborting OOB writes, such as `OOBTest`, which writes 15 elements into an SRAM of size 13 and expects only legal stores to survive (`test/spatial/tests/feature/unit/OOBTest.scala:8-18`). It is excellent for HLS-conformance CI once compatibility is separately available.

`split_modes` has the best cost/risk balance. Labels should be explicit: `sim_compat_log_invalid`, `sim_strict_trap`, `synth_checked_assert`, and `synth_assume_inbounds`. This is medium implementation cost because diagnostics, manifests, and tests must carry mode provenance, but it avoids hidden semantic drift.

`synth_checked_assert` is a synthesis policy, not a simulator replacement. Chisel memory emission wires banks, offsets, data, and enables into ports without logfile or invalid read fallback (`src/spatial/codegen/chiselgen/ChiselGenMem.scala:73-103`), while assertions already map to breakpoint wiring through `AssertIf` (`src/spatial/codegen/chiselgen/ChiselGenDebug.scala:29-34`). Cost is medium-to-high in hardware: comparators and enable-gated failure logic per address/lane.

`synth_assume_inbounds` is cheapest in generated hardware and highest in proof burden. It should require static proof or a recorded waiver. It must not call invalid constructors for OOB; violating the assumption yields no defined simulator value.

`dual_run_compare` is high operational cost but useful during migration: run ScalaGen and Rust `sim_compat_log_invalid`, compare outputs and OOB logs, then run `sim_strict_trap` to classify hardware hazards. It is a temporary confidence tool, not a user-facing semantic.

## Testing Strategy

Start with golden compatibility tests: OOB write discard from `OOBTest`, new OOB read-to-invalid tests, disabled-lane no-log/no-trap tests, and log-format mirrors for `reads.log` / `writes.log`. Add invalid propagation tests for fixed, float, bit, FIFO/stream empty reads, and vector invalid. The last one is important because Q-135 records a malformed `ScalaGenVec.invalid` emission and asks whether OOB or switch fallbacks can reach it ([[20 - Open Questions]], lines 1929-1949).

For synthesis modes, use negative tests that prove `synth_checked_assert` is enable-gated and lane-specific, plus proof/waiver tests for `synth_assume_inbounds`. Each test artifact should record the mode label so failures do not blur simulator parity with hardware legality.

## Migration Plan

Phase 1: implement typed invalid representation and checked memory helpers, then make `sim_compat_log_invalid` pass ScalaGen dual-run comparisons. Phase 2: add `sim_strict_trap` and use it in new Rust/HLS legality tests. Phase 3: lower `synth_checked_assert` into HLS debug builds and expose `synth_assume_inbounds` only behind static proof or manifest waiver. Phase 4: retire broad dual-run from normal CI, keeping it for regressions and known semantic hot spots.

Preliminary recommendation: adopt `split_modes` as the migration architecture, use `sim_compat_log_invalid` for initial parity, and make HLS release builds converge toward `synth_assume_inbounds` only after checked assertions and tests have earned trust. This is an angle recommendation, not final D-16.
