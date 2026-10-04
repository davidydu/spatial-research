---
type: implementation-goal
title: "Initial compiler goal: composed memory programs"
project: spatial-python
date: 2026-10-04
status: active
authority: user-authorized-initial-implementation
implementation_status: in-progress
---

# Initial compiler goal: composed memory programs

David authorized this initial implementation goal on 4 October 2026: compile and simulate a declared subset of small memory programs, including a new valid composition written after the implementation is frozen. The purpose is to test the architecture through reusable language rules. A successful lab demonstration alone does not complete the goal.

This authorization covers the initial implementation experiment. It does not record professor adoption of the entire detailed architecture in [[D-28]]. The initial goal is an Int32 portion of S1 with the necessary S0 foundations; the full language and hardware milestones remain in [[04 - Python Implementation Roadmap]].

## What must work

The complete route is captured Python source → specialization → untrusted records → checking → prepared bindings → reference execution. Programmatic construction and imported artifacts reach the same checker and execution machinery.

The frozen subset includes Int32 arithmetic, exact Index values and strict Bool control; scalar ports; local SRAM and DRAM views; load/store; nested ordered loops; lazy runtime branches; and typed helpers with borrowed storage and fresh local state for each activation. Runtime shapes, multidimensional and signed-stride views, shared aliases, initialization and precise fault order are part of the goal. They cannot be removed to make a fixture pass.

The compiler repository's `docs/initial-language-contract.md` contains the exact operators, grammar, shape rules, host API, resource budgets, exclusions and acceptance obligations. It pins research baseline `db30739`. The contract also documents the missing Bool host ingress constructor as an explicit `BoolInput` addition; it does not treat Bool as integer ingress.

## Acceptance gates

| Gate | Required evidence |
|---|---|
| General composition | After a compiler revision is frozen, an independent reviewer writes a structurally unfamiliar valid program. It runs without a new compiler path. Vary dimensions, helper boundaries, loop nesting, branches and aliases. |
| Memory and faults | Independent expected outputs and observable effects establish snapshot transfers, shared aliases, fresh local lifetimes, initialization, lazy invalid accesses and committed prefixes before faults. |
| Common checked meaning | Equivalent normalized source, builder and artifact-import programs agree; malformed candidates and forged checked status reject through the same verification boundary. |
| Actual structural editing | REP-EDIT duplicates/remaps owned regions, captures, results and tokens; rebuilds the real index; transfers origins and requirements; preserves borrowed backing; rejects stale facts; and leaves the old revision intact after a failed candidate. |
| Scope and usability | Every supported construct has positive, negative and composition evidence. Measure actual supported R007 workloads separately from small representation/edit experiments; keep unmet targets visible. |

Development fixtures are independently derived before production code. They are not held-out evidence. A repaired holdout becomes a regression test, and acceptance requires a fresh unseen composition. Source renaming or resizing one known kernel is insufficient. Tests supplement the checked grammar and architecture review; a finite suite does not prove unrestricted generality.

Handlers for language operations, control and storage are expected. Dispatch based on kernel names, lab numbers, fixture IDs or whole-program shapes is excluded. An optional validation-specific transformation fixture may select which edit to exercise; checking and execution remain general.

## Infrastructure

The reference milestone runs locally on the pinned CPython baseline and standard-library semantic core. The stopped HLS instance is not needed. Keep it stopped until scoped S6/S7 work has an eligible plan and generated code ready for vendor validation. At that point, record the actual installed toolchain, device, clock and dependency versions before using it as evidence.

No FPGA resource, timing, RTL or hardware-support claim follows from local simulation.

## Implementation and evidence

The implementation lives in the separate `spatial-py` repository. Its active plan is `docs/plans/2026-10-04-initial-reference.md`; its support ledger and task evidence distinguish completed foundations from the full goal. Historical Scala/Rust repositories remain evidence and are not modified to supply a Python result.

Current checkpoint: the closed record/schema/index foundation (`spatial-py@2109a84`) and stateless numeric primitives (`5126ed9`) are implemented on `work/initial-reference`. Independent specification and code-quality reviews passed after malformed-input defects were repaired with failing-then-passing regressions. All 74 tests pass both from source and from an installed wheel: 44 foundation tests plus 30 numeric tests. This is component evidence, not completion of the compiler goal.

The independent development data includes 12 memory/effect cases and 133 successful numeric expression observations, plus numeric/type/host/preparation rejection cases. The numeric leaves now replay 116 value observations and 12 direct fault causes. Source-context and lazy-expression rows, fault prefixes, memory execution, host ingress and preparation still require their actual workflow tests. The negative Index bitwise interpretation was recorded explicitly before dependent code. Numeric resource limits are separate from arithmetic faults and retain a named implementation allocation ceiling; no machine-width wrap is imposed on Index.

The checker boundary is in progress. Its reviewed design (`2f922d4`) preserves the baseline's common source/builder UncheckedProgram, including exact literal/sign trees and unresolved closed arguments, until checking normalizes it. Canonical CandidateProgram inputs then join the same full verifier. The design also retains dynamic branch faults at their selected effect points, rejects recursion across all retained definitions, and keeps Out DRAM initialization dependent on the supplied owner. It must derive obligations from operations/signatures and publish a checked program only after the entire candidate passes. No checked program, source/check/simulation path or post-freeze unfamiliar-composition pass is claimed yet. The [implementation repository](https://github.com/davidydu/spatial-py/tree/work/initial-reference) and its [support ledger](https://github.com/davidydu/spatial-py/blob/work/initial-reference/docs/support-ledger.md) require repository access.

[[70 - Engineering Architecture Map]] shows the full architecture. [[10 - Source Checker and IR Blueprint]], [[40 - Package and Conformance Blueprint]] and [[PY-R017 - Compiler Representation Comparison]] own the verification and representation obligations behind this goal.
