---
type: implementation-checkpoint
title: "Explicit scalar interfaces pass HLS and RTL checks"
project: spatial-python
date: 2026-10-27
status: vendor-validated-bounded-subset
---

**The corrected scalar interface now passes vendor hardware checks.** On
27 October, all 15 projects of the frozen interface batch passed Vitis C
simulation, synthesis and Verilog RTL co-simulation. They cover 46 independently
specified cases: 34 successful completions and 12 intentional faults. The
compiler, generated programs and expected answers were unchanged for this run.
The same projects were validated locally in [[2026-10-22-scalar-interface-checkpoint]].

The [[2026-10-22-scalar-vitis-checkpoint|22 October run]] found that Vitis ignored
the requested depth-one memory interface for scalar state. This run shows the
explicit replacement working as specified:

| Logical value | Hardware interface Vitis built |
|---|---|
| Scalar seed (InOut), data and mask | Plain `ap_none` inputs (18 across 9 projects) |
| Scalar result data and initialization | `ap_vld` outputs with valid strobes (46 results) |
| Larger memories | Addressed `ap_memory` ports |
| Kernel control and status | `ap_ctrl_hs`, packed fault and operation status on `ap_return` |

No interface request was ignored: zero `HLS 207-5572` warnings in all 15
projects. A bounded reader matched all 110 scalar-interface signals in the
synthesis reports to their wrappers.

The testbench pre-fills result storage, so its own post-check cannot detect a
missing write. The acceptance rules therefore also read the RTL simulation's
recorded output for every transaction. All 46 scalar result arguments hold the
specified data and initialization values for every case, including the
committed prefixes before faults.

## Three runs, reported openly

The acceptance rules were written before any output existed. The first run
passed every per-project rule for all 13 Python-generated projects. It failed
one rule on the two hand-written adapter fixtures: their hardware completes in
zero cycles, so Vitis prints their progress as `[n/a]` instead of the
`[100.00%]` the rule required. Every other check passed for them, including the
RTL result check.

David chose to correct the rule and run again rather than re-judge the first
run's outputs. The second run was staged from the wrong specification path and
failed the provenance rule. The third run, staged from its own committed
specification under the corrected rules, passes all nine rules. All three runs
are kept.

Their generated Verilog and RTL result data are byte-identical. The pass reflects
the corrected rule, not different hardware behavior. The six memory-only
projects also reproduce the 22 October outputs byte for byte.

## Scope

This is C/RTL co-simulation agreement on 46 finite cases in Vitis's own
testbench, using the sequential Z020 profile: Vitis 2025.1, `xc7z020clg400-1`,
a 10 ns clock and 2.7 ns uncertainty, with automatic loop pipelining off. An
integrator must hold each seed for a whole transaction and capture results on
their valid strobes.

It is not a board or driver interface, routed timing or pipelined performance
result, and it is not the AWS F2 course flow, which is the next hardware
milestone. The compiler-side [vendor checkpoint](https://github.com/davidydu/spatial-py/blob/c922bebe84515c18444d632e24b15ac45c9fa024/docs/evidence/task-06f-scalar-interface-vendor.md)
holds the exact runs, hashes and verification records. Simulator logs carrying
infrastructure headers are kept out of the repository and recorded by hash.
