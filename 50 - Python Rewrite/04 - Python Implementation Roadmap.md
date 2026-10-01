---
type: plan
title: "Python Spatial implementation roadmap for review"
scope: "Proposed vertical slices after architecture approval; no implementation authorization"
project: spatial-python
date: 2026-09-30
status: proposed
---

## Approval boundary and intended result

This is the proposed implementation sequence following [[03 - Managed Research Execution]]. It is part of the research package for professor review. It does not authorize production compiler work or report that any slice exists.

The intended result is a Python language frontend, Python semantic compiler, and Python reference simulator, followed by a reusable HLS backend. Each slice must handle a family of composed programs and explain invalid cases. A handwritten recognizer for one complete application does not complete a slice.

The implementation contract will combine the reviewed programming-model recommendation, numeric/effect/protocol rules, compiler architecture, host workflow, and HLS studies. A later change to an adopted contract needs a dated decision and migration cases. Team capability is assumed adequate; the order below follows semantic dependencies and feedback value rather than scarce language expertise.

## Concrete design inputs, 2026-10-01

[[00 - Implementation Design Index]] now provides the implementation methods behind this roadmap. S0 follows [[40 - Package and Conformance Blueprint#Concrete S0 and S1 implementation order|the package entry checklist]] and [[10 - Source Checker and IR Blueprint]]: create the source-only package, implement owned schemas and canonical import, type/binding/effect checks, structured verifier and fixtures, then integrate S1. The CPython/xDSL dependency baseline and reproducible wheel route are specified. S2–S3 use the numeric blueprint; S4–S6 use the state/HLS blueprint; libraries expand through the explicit migration recipes.

The first proposed target is `vitis-2025.1-z020-10ns`; historical Rust logs establish its identifiers only. S7 must establish new Python-generated evidence. Larger-device or other-release profiles can be added without reducing the full language scope. [[07 - Python Implementation Readiness Audit]] records the stronger review, its repairs and the still-unrun production/target gates.

## Slice sequence

| Slice | User-visible result | Required scope | Exit evidence |
|---|---|---|---|
| S0. Reproducible contract and package | A contributor can check a saved source unit and obtain structured diagnostics | Versioned profiles/source manager; package/CLI; source-only capture; immutable meta bindings; numeric/type descriptors; unchecked program and common verifier boundary | No decorator/body execution; file/text/cell provenance; malformed builder/serialized input rejects; artifact determinism; chosen framework import boundary verified |
| S1. First complete kernel path | Capture, check, simulate, and explain a small composed memory kernel | Exact fixed/Int operations; scalar ports; SRAM/DRAM views; load/store; loops; lazy branches; helper composition; logical bounds/initialization; ordered effects | Tiled scale plus changed shapes, nested helpers, aliases and negative cases; independent values and traces; ordinary/augmented assignment order; same semantic form from source and generator builder |
| S2. Complete reduction families | Run scalar and memory reductions/folds with predictable arithmetic | Associative operators, ordered fold, fixed trees, identity/seed/destination state; empty/disabled/tails; effectful contributions; wider/fractional types and casts | Scalar/memory variants, subtraction/tree discriminator, overflow/rounding cases, FIFO contribution traces when queue slice is present; transformations preserve tree and effects |
| S3. Full numeric profiles | Explain and simulate generic fixed/binary-floating values and adopted math/random profiles | Special values, bit conversions, FMA, exact rounding, saturation/checked operations, intrinsics and explicit RNG dependencies | Exhaustive small formats, independent standard-format vectors, constant/runtime parity, source diagnostics, profile-version reproducibility |
| S4. Stateful local control | Run programs using queues, windows, register files, and general FSMs | FIFO/LIFO/vector operations, initialization/reset/lifetimes, line/merge buffers, masks/arbitration, typed FSM condition/action/next regions | Boundary transitions, sparse masks, loop-carried state, repeated invocation/persistence, effect-sensitive FSM and buffer examples |
| S5. Communicating tasks | Simulate bounded concurrent Spatial programs and explain wait/deadlock/cancel outcomes | Task/continuation graph, channels, explicit arbitration/locks, environment traces, forever/stop/drain, structured external streams and components | Capacity-one producer/consumer, feedback, competing requests, cancellation with in-flight effects, finite/closed input, bounded interleaving checks; record allowed versus witness traces |
| S6. Hardware implementation planning | Produce an inspectable legal target plan for composed programs | Storage/port/bank/version allocation; overlap legality; channels and protocol routes; ABI; numeric primitive capabilities; hard constraints and soft preferences | Fail-closed target obligations; original-to-plan semantic checks; source-linked resource/dependence explanations; deterministic plan serialization |
| S7. First HLS path | Generate and validate hardware for the first complete kernel family | Vitis release/part/clock profile; typed emission; memory/interface adapters; harness/report capture | Generated code checks, vendor C simulation, C/RTL simulation, synthesis and separate resource/II reports; no relabeling old Rust evidence |
| S8. Full HLS family expansion | Lower supported reductions, numeric, stateful, and communicating families through reusable routes | Per-family lowering and explicit component integration; HLS legality, numeric/protocol preservation, resets/faults, dense/sparse transfers | Every claimed capability has adversarial conformance and target evidence; missing capabilities diagnose at a named stage; integrated cancellation/stream behavior checked |
| S9. Optimization and design-space exploration | Tune legal programs without changing their declared meaning | Cost models, search, compiler caching, independent-kernel/process parallelism, report feedback, banking/scheduling improvements | Before/after semantics; reproducible Pareto results; measured compiler feedback targets; timing/resource evidence for selected designs |

Slices describe integration milestones, not isolated teams building disconnected layers. S1 includes its checker and simulator. S7 reuses the same semantic path instead of introducing a second frontend. Each later family must extend source, checking, simulation, diagnostics, serialization, and tests together before claiming language support.

## Dependencies and useful parallel work

S0 precedes a trusted vertical path. S1 establishes the common mechanism used by S2–S5. Numeric work and protocol work can then proceed independently within their assigned interfaces. S2's pure arithmetic tests can precede S4, while its consuming-contribution tests depend on S4. S5 depends on local state primitives and the adopted advanced protocols.

S6 can begin for the checked S1 subset while S2–S5 expand the language. S7 follows that bounded S6 plan; it need not wait for every advanced simulator feature. S8 advances family by family only after the corresponding semantic and implementation-plan contracts exist. S9 may optimize completed slices early, but broader search must never hide a missing semantic path. This allows early hardware feedback without redefining the whole language around the first hardware example.

Keep ownership by module/feature and give reviewers a different scope from their authored code. Agree on versioned node/diagnostic/profile interfaces before parallel writers edit dependent modules. Integration changes are reviewed against the shared contract, not accepted because two subagents happen to agree.

## Required artifacts at every slice

For each added construct, record its public form, unchecked representation, checked invariants, interpreter transition, intended lowering route, diagnostics, and independent acceptance cases. Add it to the coverage ledger with a linked implementation/evidence record; preserve the research disposition separately from support status.

Use four different statuses: proposed design, implemented reference semantics, implemented target lowering, and validated target capability. A feature may have a complete language contract and simulator while remaining unavailable on one target. The compiler must report that boundary accurately. General hardware support requires reusable non-example programs and negative tests, not just successful emission.

The fixture set must vary extents, nesting, types, helper boundaries, branch paths, alias relationships, masks, initial state, and scheduling annotations. Include a composition that was not in the initial corpus. Compare state/effect traces where final values can hide bugs. All source examples must become either accepted fixtures or documented intentional rejections under the adopted grammar.

## Gates before starting implementation

1. Professor review identifies the approved architecture/scope and any requested changes. The decision record names that authority; research recommendations do not silently change to adopted rules.
2. The proposed specification incorporates the reviewed rules and deliberate divergences from original Spatial. Initial release scope and full-rewrite milestones are explicit.
3. The dependency/runtime baseline and artifact schema are pinned. The selected framework probe is reproduced in a clean environment and its limitations become verifier tests.
4. Numeric, effect, and protocol examples have independent expected outcomes before optimizer/backend code exists. Feedback-time workloads and targets from [[PY-R007 - Host Workflow Reproducibility and Validation]] are preserved before measuring the implementation.
5. The first slice has a concrete entry/exit checklist and a reviewable repository plan. Existing Rust and Scala repositories remain evidence; creating a Python implementation repository is a separate approved implementation action.

## Acceptance and changes of direction

The whole rewrite is complete only when the adopted language coverage, reference execution, host workflow, diagnostics, and required backend profiles have evidence. The research completion audit is earlier: it checks that the proposed design answers the questions and identifies honest implementation gates. Neither audit is replaced by a green documentation build.

If measurements miss feedback targets, use attributed profiles before changing frameworks or representations. If a vendor route cannot preserve a required protocol, revise the target plan/component integration or report the missing capability; do not silently weaken the source language. If a proposed semantic redesign is rejected during professor review, update the contract and its discriminating examples before coding. Preserve superseded reasoning so later contributors can understand the change.
