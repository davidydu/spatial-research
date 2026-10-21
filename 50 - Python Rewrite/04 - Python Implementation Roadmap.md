---
type: plan
title: "Python Spatial implementation roadmap for review"
scope: "Proposed full roadmap; bounded initial implementation authorized 2026-10-04"
project: spatial-python
date: 2026-09-30
updated: 2026-10-21
status: proposed
---

## Approval boundary and intended result

This is the proposed full implementation sequence following [[03 - Managed Research Execution]]. It remains part of the research package for professor review; its stages describe intended results, not completed support.

**4 October authorization:** David authorized the [[80 - Initial Compiler Goal|bounded composed-memory implementation experiment]], an initial Int32 portion of S1 with the necessary S0 foundations. That work is underway in the separate implementation repository. This supersedes the earlier no-start wording for the initial experiment only. Professor adoption of the complete [[D-28]] architecture, the full roadmap and later support claims remain separate. The initial-goal page records implemented components and unfinished acceptance gates.

The intended result is a Python language frontend, Python semantic compiler, and Python reference simulator, followed by a reusable HLS backend. Each slice must handle a family of composed programs and explain invalid cases. A handwritten recognizer for one complete application does not complete a slice.

The implementation contract will combine the reviewed programming-model recommendation, numeric/effect/protocol rules, compiler architecture, host workflow, and HLS studies. A later change to an adopted contract needs a dated decision and migration cases. Team capability is assumed adequate; the order below follows semantic dependencies and feedback value rather than scarce language expertise.

## Current execution direction — 21 October 2026

David agreed to keep the Python compiler foundation and bring a bounded HLS
feasibility check forward. [[2026-10-21-hls-feasibility-checkpoint]] owns the
discussion and evidence limits. He then authorized starting the backend, with
functional C++ correctness before hardware simulation. The mapping audit and
first direct emitter are recorded in [[2026-10-21-generated-cpp-checkpoint]]:
the existing Lab 1 program and a harder helper/partial-tile program now execute
as generated native C++. The subsequent [[2026-10-21-vitis-rtl-checkpoint]] records four kernels and
nine cases passing vendor C simulation, synthesis and RTL co-simulation. This
supersedes the 17 October instruction to finish all planned language/reference
support before any HLS work.

The latest [[2026-10-21-scalar-target-checkpoint]] adds scalar Int32 Out/InOut
cells and signed Index shift counts through generated C++ and a depth-one vendor
interface. Eleven development projects (28 cases) and a separate fresh
directional-follower project (four cases) pass locally against independent
expectations. The original rejected shift program is now a regression, not fresh
acceptance. Only four backend modules changed; the language semantics are unchanged.

The saved 12-project/32-case bundle is ready; both complete source and installed-package
suites pass 1,329 tests. Next, ask David before reusing the stopped HLS host. Run vendor C simulation, synthesis and RTL co-simulation,
then use the size/tile measurements to select one general storage or scheduling
improvement while preserving memory and fault behavior. The scalar/shift extension
has no new vendor result; the earlier four-kernel evidence remains separate.

The three EE109 labs still guide progression toward general student programs.
They are coverage anchors; support must extend to other programs that compose
the same constructs. This sequence change does not record professor approval of
every proposed detail or change the frozen initial language contract.

| Course anchor | Language families to exercise | Current reference status and direction |
|---|---|---|
| Lab 1: scalar I/O, tiled DRAM/SRAM, FIFO, Reduce/Fold | Typed ports; ordered loads/stores; loops; reusable helpers; mutable registers; queues; scalar accumulation | Tiled DRAM/SRAM and scalar-cell accumulation execute, including local C++ checks with helpers, branches and faults. Sequential scalar accumulation does not complete Reg, FIFO or Reduce/Fold semantics. |
| Lab 2: MemReduce/MemFold, FSM, LUT, blocked outer-product GEMM | Memory contributions and accumulation; state transitions; read-only tables; multidimensional tiles and tails; fractional fixed-point arithmetic | Existing views, loops and helpers provide foundations. The named controller/storage families and the course's fixed-point profile remain later language work. |
| Lab 3: Sobel convolution | LineBuffer publication, RegFile shifts, LUT coefficients, nested reductions, borders/reset/initialization | Build on the earlier memory/control/numeric families, then execute complete window and convolution programs with independent full-output checks. |

The inventories are [[PY-R012 - Lab1 Syntax and Host Mapping]],
[[PY-R013 - Controllers Reductions and Lab2 Mapping]] and
[[PY-R014 - Convolution Windows and Lab3 Mapping]]. The pinned course index lists
three labs; David corrected the earlier “Lab 1 through Lab 4” wording to Labs 1–3.
Tutorial holes and designed completions remain labeled in those studies.

After the initial mapping audit and native C++ experiment, continue small complete
language increments alongside target validation, following the audit's dependencies:

1. Finish the current composed-memory path: public check/prepare, then genuine
   cumulative resumption before public simulate, and the remaining initial-contract
   acceptance work. Borrowed helper results and named view locals already execute;
   they support modular tile/window code beyond the tiled-scale example.
2. Expand toward Lab 1's registers, queues and scalar reductions/folds, then Lab 2's
   memory reductions, FSM/LUT and fixed-point tiled arithmetic, and Lab 3's windows.
   Follow shared semantic dependencies; do not require every exercise in one lab
   to finish before implementing a prerequisite used by another. Retain the wider
   adopted language families and explicit remaining coverage in the roadmap.
3. For each increment, name its course pattern, reusable language rule and runnable
   source examples. Check changed shapes, tails, helper boundaries, branch paths,
   aliases and faults, then a fresh independent composition. Avoid both application
   recognizers and unrelated verifier expansion. Implement the checks necessary
   for the constructs being admitted through the existing shared path.

An ordinary helper may return a view of surviving caller storage, but cannot
return its own dying SRAM. Lab 2's mapper-local tile contributions need the separate
reduction-owned contribution lifetime already designed in R013; borrowed helper
returns do not establish that support.

Full language/reference coverage remains required for the rewrite, but is no longer
a prerequisite for the bounded S6/S7 feasibility work. The current direct backend
does not complete checked target planning or REP-S6. Keep the stopped HLS host off
while preparing generated source and testbenches locally; ask David before reuse.
Local execution confers no new hardware evidence or board-integration support.

## Concrete design inputs, 2026-10-01

[[00 - Implementation Design Index]] now provides the implementation methods behind this roadmap. S0 follows [[40 - Package and Conformance Blueprint#Concrete S0 and S1 implementation order|the package entry checklist]] and [[10 - Source Checker and IR Blueprint]]: create the source-only package, implement owned schemas and canonical import, type/binding/effect checks, structured verifier and fixtures, then integrate S1. The CPython baseline and standard-library semantic core are specified; the former xDSL wheel remains an optional pinned research/backend dependency. The representation research in [[PY-R017 - Compiler Representation Comparison]] now precedes S0 rather than deferring a substrate choice until after framework-specific implementation. S2–S3 use the numeric blueprint; S4–S6 use the state/HLS blueprint; libraries expand through the explicit migration recipes.

The first proposed target is `vitis-2025.1-z020-10ns`; historical Rust logs establish its identifiers only. S7 must establish new Python-generated evidence. Larger-device or other-release profiles can be added without reducing the full language scope. [[07 - Python Implementation Readiness Audit]] records the stronger review, its repairs and the still-unrun production/target gates.

S0 establishes the schemas and trusted boundary needed for S1, with unknown/malformed inputs rejecting and no unchecked artifact published. It need not implement every later numeric/protocol family before a useful kernel runs. Each later slice adds its closed records, checker and independent fixtures together. Import rejection and provenance are not deferred merely to make S0 look smaller.

## Slice sequence

| Slice | User-visible result | Required scope | Exit evidence |
|---|---|---|---|
| S0. Reproducible contract and package | A contributor can check a saved source unit and obtain structured diagnostics | Versioned profiles/source manager; package/CLI; source-only capture; immutable meta bindings; numeric/type descriptors; unchecked program and common verifier boundary | No decorator/body execution; file/text/cell provenance; malformed builder/serialized input rejects; artifact determinism; chosen immutable record/query boundary verified; no optional framework import in the core |
| S1. First complete kernel path | Capture, check, simulate, and explain a small composed memory kernel | Exact fixed/Int operations; scalar ports; SRAM/DRAM views; load/store; loops; lazy branches; helper composition; logical bounds/initialization; ordered effects | Tiled scale plus changed shapes, nested helpers, aliases and negative cases; independent values and traces; ordinary/augmented assignment order; same semantic form from source and generator builder; direct-region fixture oracle agrees with continuation execution on assignment/branch/call traces; `REP-S1` source/builder/import agreement and `REP-EDIT` ordered region-remapping/index/provenance/stale-fact discriminator in R017 |
| S2. Complete reduction families | Run scalar and memory reductions/folds with predictable arithmetic | Associative operators, ordered fold, fixed trees, identity/seed/destination state; empty/disabled/tails; effectful contributions; wider/fractional types and casts | Scalar/memory variants, subtraction/tree discriminator, overflow/rounding cases, FIFO contribution traces when queue slice is present; transformations preserve tree and effects; extend `REP-EDIT` to contribution effects and declared reduction topology |
| S3. Full numeric profiles | Explain and simulate generic fixed/binary-floating values and adopted math/random profiles | Special values, bit conversions, FMA, exact rounding, saturation/checked operations, intrinsics and explicit RNG dependencies | Exhaustive small formats, independent standard-format vectors, constant/runtime parity, source diagnostics, profile-version reproducibility |
| S4. Stateful local control | Run programs using queues, windows, register files, and general FSMs | FIFO/LIFO/vector operations, initialization/reset/lifetimes, line/merge buffers, masks/arbitration, typed FSM condition/action/next regions | Boundary transitions, sparse masks, loop-carried state, repeated invocation/persistence, effect-sensitive FSM and buffer examples |
| S5. Communicating tasks | Simulate bounded concurrent Spatial programs and explain wait/deadlock/cancel outcomes | Task/continuation graph, channels, explicit arbitration/locks, environment traces, forever/stop/drain, structured external streams and components | Capacity-one producer/consumer, feedback, competing requests, cancellation with in-flight effects, finite/closed input, bounded interleaving checks; record allowed versus witness traces; `REP-S5` parent-token-once, child-domain and join/cancel fixtures before communicating-family support |
| S6. Hardware implementation planning | Produce an inspectable legal target plan for composed programs | Storage/port/bank/version allocation; overlap legality; channels and protocol routes; ABI; numeric primitive capabilities; hard constraints and soft preferences | Fail-closed target obligations; original-to-plan semantic checks and Python execution of generated transition records, including mask/publication/stall mutants; source-linked resource/dependence explanations; deterministic plan serialization; `REP-S6(scope)` with explicit supported-family scope before its S7 emission |
| S7. First HLS path | Generate and validate hardware for the first complete kernel family | Vitis release/part/clock profile; typed emission; memory/interface adapters; harness/report capture | Generated code checks, vendor C simulation, C/RTL simulation, synthesis and separate resource/II reports; no relabeling old Rust evidence |
| S8. Full HLS family expansion | Lower supported reductions, numeric, stateful, and communicating families through reusable routes | Per-family lowering and explicit component integration; HLS legality, numeric/protocol preservation, resets/faults, dense/sparse transfers | Every claimed capability has adversarial conformance and target evidence; missing capabilities diagnose at a named stage; integrated cancellation/stream behavior checked |
| S9. Optimization and design-space exploration | Tune legal programs without changing their declared meaning | Cost models, search, compiler caching, independent-kernel/process parallelism, report feedback, banking/scheduling improvements | Before/after semantics; reproducible Pareto results; measured compiler feedback targets; timing/resource evidence for selected designs |

Slices describe integration milestones, not isolated teams building disconnected layers. S1 includes its checker and simulator. S7 reuses the same semantic path instead of introducing a second frontend. Each later family must extend source, checking, simulation, diagnostics, serialization, and tests together before claiming language support.


## Representation gates at slice boundaries

[[PY-R017 - Compiler Representation Comparison#Adoption and reversal conditions|R017]] owns four named representation obligations. These proposed executable exits are separate from the completed research comparison:

| Gate | Earliest required exit and dependent work | Evidence required |
|---|---|---|
| `REP-S1` | S1 exit, before expanding its common checked-program mechanism in S2–S5 | Source/builder/artifact-import agreement; helper/branch/loop/alias/lifetime/fault cases and malformed inputs; independently specified values/effects |
| `REP-EDIT` | S1 exit, alongside `REP-S1`; extend for S2 reduction laws/effects | R017's two-call/four-iteration ordered helper fixture exercises owned-region duplication, capture/result/token remapping, actual index rebuilding and requirement/origin transfer. Failed candidates preserve the old revision; stale proof, borrowed-backing substitution and activation-state collapse mutants fail. Record attributed costs; this minimal fixture is not a complete R007 benchmark |
| `REP-S5` | Before communicating-task support is claimed or that family enters planning | Parent token enters a group once; child domains, joins and cancellation retain their obligations and ownership under checking/editing |
| `REP-S6(scope)` | Before S7 emits the named supported subset | PlanRecords correspondence, requirement/provenance transfer and failed publication; Python plan execution, deterministic artifacts and negative/mutant cases for that scope |

The architecture permits a scoped S6/S7 route for S1 independently of S5. The 21 October direction brings a bounded feasibility experiment forward after a hardware-mapping audit, superseding the earlier full-language prerequisite. Every family must still supply its applicable gate before entering target planning. The slice completion record names each applicable gate, fixture IDs, independent expected outcomes and execution evidence. It rejects missing evidence and any claim that all representation gates passed when `REP-S5` or a required scoped plan gate remains pending.

`REP-EDIT` checks the candidate-editing mechanism early, without requiring a production general-purpose inliner/unroller. Compile-time duplication gives owned region/op/allocation-site records fresh IDs and lineage while borrowed resources retain their backing identity. Runtime activation paths and generations remain runtime identity components; the rewrite records their correspondence. Distinct activations must not share lifetime/state merely because an operation/site ID or numeric generation is equal. Full optimization and design-space search remain S9 work.

## Dependencies and useful parallel work

S0 precedes a trusted vertical path. S1 establishes the common mechanism used by S2–S5. Numeric work and protocol work can then proceed independently within their assigned interfaces. S2's pure arithmetic tests can precede S4, while its consuming-contribution tests depend on S4. S5 depends on local state primitives and the adopted advanced protocols.

Current execution takes the locally validated scalar/shift extension through vendor stages, then uses scaling evidence to select one general storage or scheduling improvement. This continues the bounded lowering experiment alongside the remaining public workflow and language work. S8 still advances family by family only after the corresponding semantic and implementation-plan contracts exist. S9 may optimize completed slices early when measurements justify it, but broader search must never hide a missing semantic path.

Keep ownership by module/feature and give reviewers a different scope from their authored code. Agree on versioned node/diagnostic/profile interfaces before parallel writers edit dependent modules. Integration changes are reviewed against the shared contract, not accepted because two subagents happen to agree.

## Required artifacts at every slice

For each added construct, record its public form, unchecked representation, checked invariants, interpreter transition, intended lowering route, diagnostics, and independent acceptance cases. Add it to the coverage ledger with a linked implementation/evidence record; preserve the research disposition separately from support status.

Use four different statuses: proposed design, implemented reference semantics, implemented target lowering, and validated target capability. A feature may have a complete language contract and simulator while remaining unavailable on one target. The compiler must report that boundary accurately. General hardware support requires reusable non-example programs and negative tests, not just successful emission.

The fixture set must vary extents, nesting, types, helper boundaries, branch paths, alias relationships, masks, initial state, and scheduling annotations. Include a composition that was not in the initial corpus. Compare state/effect traces where final values can hide bugs. All source examples must become either accepted fixtures or documented intentional rejections under the adopted grammar.

## Authority and readiness gates

The initial experiment proceeds under the 4 October authorization above. These gates govern the reviewed scope and subsequent expansion; they do not reopen permission for that already-authorized work.

1. Professor review identifies the adopted full architecture/scope and any requested changes. The decision record names that authority; the bounded initial experiment does not by itself adopt the full roadmap.
2. The proposed specification incorporates the reviewed rules and deliberate divergences from original Spatial. Initial release scope and full-rewrite milestones are explicit.
3. The dependency/runtime baseline and artifact schema are pinned. The R017 comparison and its limitations inform the selected record structure before S0; reproduce the selected invariant tests in a clean environment. Any optional framework adapter has a named pipeline, pinned dependencies and explicit conversion/correspondence checks.
4. Numeric, effect, and protocol examples have independent expected outcomes before optimizer/backend code exists. Feedback-time workloads and targets from [[PY-R007 - Host Workflow Reproducibility and Validation]] are preserved before measuring the implementation.
5. Each slice has a concrete entry/exit checklist and a reviewable repository plan. The initial experiment has its own authorized Python repository and plan. Existing Rust and Scala repositories remain evidence, and their results do not establish Python implementation support.

## Acceptance and changes of direction

The whole rewrite is complete only when the adopted language coverage, reference execution, host workflow, diagnostics, and required backend profiles have evidence. The research completion audit is earlier: it checks that the proposed design answers the questions and identifies honest implementation gates. Neither audit is replaced by a green documentation build.

If measurements miss feedback targets, use attributed profiles before changing frameworks or representations. A reproducible miss on a supported R007 workload attributed to representation, required-index or transaction design triggers R017's bounded record-repair/xDSL comparison task before extending that affected route; no numeric budget-share threshold or pre-existing winning alternative is required. Keep capture/semantic analysis, required indices, remapping/snapshots, provenance/requirements, verification/publication and any adapter conversion costs visible. Numeric/protocol execution cost alone is not evidence for a representation replacement. The S1 implementation must measure R007's actual supported end-to-end paths separately from `REP-EDIT`; neither that minimal fixture nor the R017 representation experiment satisfies a complete target by itself. An optional framework adapter must show its benefit after conversion, verification and publication costs. If a vendor route cannot preserve a required protocol, revise the target plan/component integration or report the missing capability; do not silently weaken the source language. If a proposed semantic redesign is rejected during professor review, update the contract and its discriminating examples before coding. Preserve superseded reasoning so later contributors can understand the change.
