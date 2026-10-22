---
type: implementation-checkpoint
title: "Scalar state and shifts pass HLS and RTL checks"
project: spatial-python
date: 2026-10-22
status: vendor-validated-bounded-subset
---

**The existing Python compiler now has a second, wider hardware checkpoint.**
All 12 saved scalar/shift projects passed Vitis C simulation, synthesis and
Verilog RTL co-simulation against 32 independently specified cases. This covers
seeded sums, tiled dot products, order-sensitive state, integer shifts and tiled
memory transfers. The compiler, generated programs and expected answers were
unchanged for this run.

The result supports the current architecture: the same checked program can reach
reference execution, generated C++ and a bounded HLS path. It also exposed a
specific interface issue to resolve before integrating the generated IP into a
larger system. Functional agreement does not establish that Vitis implemented
every requested interface directive.

## What passed

| Evidence | Result and scope |
|---|---|
| Vendor C simulation | All 12 projects, 32 cases |
| HLS synthesis | All 12 projects produced RTL |
| Verilog RTL co-simulation | All 32 cases passed the C post-check of RTL results |
| Expected outcomes | 27 successful completions and five intentional faults |
| Production revision | `1e55eb8f5a20c11c1cd4a17010b6fa6cd4332e99`, unchanged |
| Preserved inputs | 133 original saved files matched all 133 staged vendor input files |
| Evidence integrity | 110 production files, 287 execution files and all 680 downloaded evidence files matched their manifests; 668 vendor files retained byte-for-byte in the repository |

The checks compare returned values, initialization state, fault status and fault
owner with expectations written independently of execution. Fault cases also
check the writes completed before the fault. Passing includes the expected
faults; it does not mean all 32 cases should return successfully.

The 11 development projects retain their 28 cases. The separate directional
follower contributes four more, including a late division fault and an incomplete
output. That program was authored after the earlier production freeze and passed
its first local execution without compiler repair. This vendor run extends its
evidence to RTL; it is not a newly authored holdout. The formerly rejected shift
program remains regression evidence.

Settings were Vitis 2025.1, device `xc7z020clg400-1`, a 10 ns clock and 2.7 ns clock
uncertainty. Automatic loop pipelining was disabled. This is the experimental
sequential IP profile used for the [[2026-10-21-vitis-rtl-checkpoint|earlier four-kernel checkpoint]].

The complete **1,329 source tests and 1,329 isolated-package tests** remain the
earlier local results in [[2026-10-21-scalar-target-checkpoint]]. They were not
rerun for this vendor-only checkpoint. No compiler behavior changed.

Twelve redundant simulator logs contained private infrastructure headers and are
omitted from the repository. Their hashes and exclusion record preserve the
inventory; the raw archive remains private. The retained logs and reports include
the RTL result post-checks.

## What the interface reports revealed

Scalar cells have one data value and one initialization value in the generated
C++ interface. The saved wrapper requested depth-one `ap_memory` ports for those
values. Vitis issued warning **HLS 207-5572**: a size-one array cannot use that
interface, so the directive was ignored.

In the saved `scalar-sum` synthesis report, the scalar InOut data and initialization
ports use `ap_ovld`; the scalar Out ports use `ap_vld`. Its array input still uses
`ap_memory`. Thus the logical data/initialization behavior passed, but the
manifest's requested memory-port protocol is not an accurate description of the
generated scalar hardware interface. The generated testbench handled the
tool-selected interfaces during co-simulation; a future system integrator needs
an explicit, verified contract.

Source direction alone cannot select that contract: in the fresh-composition
report, scalar Out result `p7` uses `ap_vld` for data but `ap_ovld` for its
initialization flag, which completion checking reads. Each test invocation has
its own explicit seed. The observed pointer interface does not establish
automatic state persistence or output-to-input feedback between invocations.

The next bounded implementation step is to choose a supported scalar interface
policy and check generated interface reports against the manifest. It must cover
both data and initialization signals, including unwritten outputs and fault
prefixes. Preserve this warning and the exact original bundle as evidence; do not
rewrite its requested protocol to make the record appear consistent.

## First measurements

These are measured RTL transaction latencies and HLS resource estimates for
successful cases. They are a baseline for a matched comparison, not optimized
hardware results.

| Program | Length / tile capacity | RTL cycles | Estimated LUT / FF / DSP |
|---|---|---:|---:|
| Seeded scalar sum | 5 / — | 17 | 196 / 52 / 0 |
| Tiled map | 8 / 4 | 149 | 1,047 / 898 / 0 |
| Tiled map | 32 / 4 | 581 | 1,058 / 908 / 0 |
| Tiled map | 32 / 16 | 767 | 1,069 / 320 / 0 |
| Tiled map | 33 / 16 | 819 | 1,401 / 652 / 0 |
| Tiled map | 128 / 16 | 3,053 | 1,075 / 332 / 0 |
| Tiled dot product | 16 / 8 | 485 | 2,614 / 2,100 / 3 |
| Tiled dot product | 33 / 8 | 1,004 | 2,871 / 2,133 / 3 |

At length 32, increasing tile capacity from 4 to 16 reduced estimated flip-flops
but increased latency from 581 to 767 cycles. Larger tiles alone did not make
this sequential mapping faster. The length-33 case also exposes tail handling
that a tile-aligned case would miss. These observations motivate inspecting
initialization, snapshots and access schedules in matched programs before
choosing an optimization; they do not isolate any one loop as the cause.

The reported top-level pipeline type is `no`. Transaction interval is not loop
initiation interval. HLS reports zero BRAM/URAM for these kernels, but external
port memories are outside those resource totals. Estimated clock periods are
not routed timing or achieved board frequency. Fault-case latencies stay separate
from successful-path scaling.

## Next steps and limits

1. Make the scalar interface policy explicit and validate the actual synthesized
   interfaces against the artifact manifest before broader integration.
2. Finish the matched cost study, then choose one general storage or scheduling
   improvement. Preserve aliases, snapshots, initialization, fault order and
   earlier writes, and repeat the independent functional and RTL checks.
3. Continue the [[04 - Python Implementation Roadmap|Labs 1–3 progression]] and
   [[00 - Python Spatial Student Guide|student documentation]] in bounded increments.
   The convenient student C++ test runner and case exporter remain planned.

This checkpoint does not complete Reg, Reduce/Fold, multidimensional target
memory, the original reference acceptance goal, public check/prepare, real
simulation resumption, full checked target planning, board/AXI integration or
parallel performance work. It adds no new language feature or student API.

## Exact evidence

The compiler evidence checkpoint is `c45654f`, committed and pushed on
`work/initial-reference`. Production remains `1e55eb8`. The compiler repository
is private; these links require repository access:

- [Vendor checkpoint and limitations](https://github.com/davidydu/spatial-py/blob/work/initial-reference/docs/evidence/task-06d-scalar-vendor.md).
- [Machine-readable verification and per-case measurements](https://github.com/davidydu/spatial-py/blob/work/initial-reference/docs/evidence/task-06d-scalar-vendor-verification.json).
- [Exact input bundles, logs, reports and generated RTL](https://github.com/davidydu/spatial-py/tree/work/initial-reference/docs/evidence/scalar-vitis-demo).

[[80 - Initial Compiler Goal]] owns the remaining implementation obligations;
[[project-handoff]] owns the current restart route. David supplied the running
host and authorized this saved batch after the earlier meeting pause. Publication
and repository checkpoint status are recorded separately from the vendor result.
