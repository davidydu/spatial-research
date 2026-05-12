---
type: handoff
date: 2026-04-28
workflow: architectural-decision-research
status: queue-complete
---

# Codex Decision Handoff - 2026-04-28

## Decisions completed

All 25 architectural decision records now exist in `20 - Research Notes/50 - Decision Records/` and are awaiting user confirmation.

- D-01: BigIP arithmetic policy.
- D-02 through D-16: completed before this continuation.
- D-17: Canonical unbiased rounding policy. Recommendation: `seeded_stochastic_legacy_away`.
- D-18: FloatPoint clamp heuristics. Recommendation: dual-mode float packing with `scalagen_legacy_clamp_v1` as reference default.
- D-19: Fused versus unfused FMA precision. Recommendation: `scalagen_unfused_two_round_v1` as reference default, fused as opt-in.
- D-20: DelayLine semantics. Recommendation: dual-mode delay lines with `compat_value_elided` as reference default and `cycle_shift_register_debug` as opt-in.
- D-21: HLS accepted-II reconciliation. Recommendation: dual-record II ledger with report-backed reconciliation.
- D-22: FIFO/LIFO/stream back-pressure. Recommendation: dual-mode queue semantics with `compat_scalagen_elastic` and `bounded_hls_cycle`.
- D-23: Rust/HLS host ABI manifest. Recommendation: explicit versioned `abi_manifest_v1` as source of truth.
- D-24: Fixed-point host conversion. Recommendation: dual-mode conversion with `bit_exact_scaled_integer_v1` as Rust default and `cppgen_fractional_double_shift_v1` as legacy compatibility.
- D-25: Multi-true `OneHotMux`. Recommendation: `strict_onehot_v1` default plus `compat_scalagen_or_reduce_v1` legacy mode.

## Decisions remaining

None. The queue stop condition is satisfied: `D-01.md` through `D-25.md` are present.

## Blockers and surprises

- No hard blockers encountered.
- D-24 and D-25 were synthesized with 9 research angle files each, above the workflow's 8/10 threshold. Their missing angle slot did not block synthesis because the recommendation matrices and core source surveys were present.
- D-22, D-23, D-24, and D-25 strongly depend on explicit policy labels. Several legacy behaviors are useful as compatibility modes but unsafe as unlabelled defaults.
- The recurring pattern is dual-mode semantics: preserve Scalagen/Cppgen compatibility for readback, but make Rust/HLS defaults stricter, manifest-labelled, and reportable.

## Recommended user action items

1. Confirm or alter D-21 through D-25 first; they define shared policy names that future implementation notes will reuse.
2. Review D-23 and D-24 together. D-23 records `conversion_policy`; D-24 chooses the fixed-point default that should populate that field.
3. Review D-22 before any cycle/debug simulator work. D-15 and D-20 depend on its queue/back-pressure mode labels.
4. Review D-25 before HLS mux lowering. The recommendation deliberately changes the default away from Scalagen OR-reduce while preserving OR-reduce as a legacy mode.
5. For implementation planning, prioritize schema work first: latency/II reconciliation, queue policy, ABI manifest, conversion policy, and mux policy labels should be defined before backend-specific lowering.
