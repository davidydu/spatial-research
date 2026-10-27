---
type: implementation-checkpoint
title: "Explicit scalar interfaces: local validation"
project: spatial-python
date: 2026-10-22
status: locally-validated-vendor-validated
---

> [!success] Vendor validated on 27 October
> All 15 projects / 46 cases passed Vitis C simulation, synthesis and RTL co-simulation: [[2026-10-27-scalar-interface-vitis-checkpoint]].

# Explicit scalar interfaces: local validation

We have corrected the boundary that carries scalar values into and out of HLS.
Each invocation now receives explicit starting values and produces separate
results. The Python language and generated C++ kernel are unchanged. This makes
the intended hardware connections explicit before broader integration.

The preceding [[2026-10-22-scalar-vitis-checkpoint|12-project, 32-case vendor run]]
passed functional checks, but Vitis ignored the requested one-element memory
interfaces. It inferred scalar handshakes from reads and writes. An output's
initialization flag could unexpectedly acquire an input because the kernel reads
that flag during completion checks. The old functional results remain valid for
their saved wrappers; they do not validate the changed interface below.

## What changes at the boundary

| Value | Starting state | Returned state |
|---|---|---|
| Scalar output | Uninitialized local cell | Value and initialization flag |
| Scalar input/output | Explicit input seed, initialized | Updated value and flag |
| One-element memory | Explicit input value and flag from its host buffer | Final value and flag |
| Larger memory | Existing memory interface | Existing behavior |

The wrapper creates fresh local cells for each call, invokes the unchanged C++
kernel, then copies every singleton value and flag to output-only ports. It does
this after faults too, so earlier writes remain observable. Reusing a caller's
output storage cannot supply hidden state to a later invocation.

Vitis output-valid signals mean that an output has been transmitted. Our separate
initialization flag means that the language value has been written. A transmitted
false initialization flag is a valid observation after an incomplete output;
these two meanings must stay distinct.

## What we checked

Production is frozen at `72fd513`. Independent specification and code-quality
reviews passed; all 103 backend tests pass. The saved development batch contains
14 projects and 40 literal-oracle cases: 12 existing Python programs/32 cases,
and two hand-authored C++ adapter fixtures/eight cases. The twelve original Python
sources and generated kernels remain byte-for-byte unchanged. Source cases pass
Python reference execution, native generated C++ and the exact saved wrapper.
Adapter fixtures establish wrapper behavior only.

Checks cover fresh seeds, reused output storage across success/fault/success,
uninitialized singleton memory, preserved output memory after a read fault,
integer overflow, fault ownership and committed writes. The report reader checks
actual signal names, direction, widths and handshakes against the requested
manifest, together with device and clock settings. Old real vendor reports reject
the new contract. Positive report fixtures are synthetic and establish only
reader behavior. Report/source hashes identify inspected files; the vendor run
must separately establish their provenance.

A separately authored post-freeze composition passed its first run without any
repair. Six literal-oracle cases combine singleton memories, scalar state, a
captured helper, branch choices, overflow and three kinds of fault. A separate
native-only seven-call harness reuses sinks through faults and a successful final
call. The complete prepared batch is **15 projects/46 cases**: 13 Python-source
compositions/38 cases and two adapter-only fixtures/eight cases.

Both complete source and isolated installed-wheel suites pass **1,351 tests**.
All 112 production files, 294 execution files,
81 installed modules and 188 saved artifact
files match their manifests. The wheel runs outside the checkout with source
imports disabled. New vendor synthesis and RTL evidence remain pending.

[Detailed verification and fresh acceptance](https://github.com/davidydu/spatial-py/blob/work/initial-reference/docs/evidence/task-06e-scalar-interface.md) require compiler repository access.

## What comes next

Run the prepared frozen bundles through Vitis C simulation, synthesis and RTL
co-simulation once the host is available. Check the new interface against actual
reports and preserve the exact staged inputs and resulting files. Until that
run passes, new physical-interface and RTL validation remain pending.

Afterward, compare matched copy/map/recurrence programs before selecting a
storage or scheduling optimization. The Python compiler, sequential target
profile, remaining language families and unfinished public student API are
unchanged. This increment adds no new verifier framework or board integration.

## Records

The compiler links require repository access:

- [Design and alternatives](https://github.com/davidydu/spatial-py/blob/work/initial-reference/docs/plans/2026-10-22-scalar-interface.md).
- [Current implementation evidence](https://github.com/davidydu/spatial-py/blob/work/initial-reference/docs/evidence/task-06e-scalar-interface.md).
- [Independent reviews](https://github.com/davidydu/spatial-py/blob/work/initial-reference/docs/reviews/2026-10-22-scalar-interface.md).
- [Prepared development cases](https://github.com/davidydu/spatial-py/tree/72fd513/docs/evidence/scalar-interface-demo).

[[80 - Initial Compiler Goal|Implementation status]] ·
[[00 - Python Spatial Student Guide|Student testing preview]] ·
[[project-handoff|Shared restart context]]
