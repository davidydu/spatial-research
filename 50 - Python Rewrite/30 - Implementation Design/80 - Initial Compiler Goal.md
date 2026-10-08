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

Current checkpoint: `spatial-py@62fe18b` follows the Lab 1 demo fixture-specification commit `8f80b24` on `work/initial-reference`. Earlier foundations through bounded ownership/dominance/token checks are in the history. The C1 memory-schema and ABI work adds closed structural scopes, formal meta witnesses, borrowed-result owner policies and environment-only capture of `Out`/`InOut[Int]` cells. Independent specification and code-quality reviews passed; all 258 source-tree tests pass. The earlier 236-test source and rebuilt-wheel result is a historical checkpoint; no 258-test installed-wheel result is claimed. These remain component results, not completion of the compiler goal.

The independent development data includes 12 memory/effect cases and 133 successful numeric expression observations, plus numeric/type/host/preparation rejection cases. The numeric leaves now replay 116 value observations and 12 direct fault causes. Source-context and lazy-expression rows, fault prefixes, memory execution, host ingress and preparation still require their actual workflow tests. The negative Index bitwise interpretation was recorded explicitly before dependent code. Numeric resource limits are separate from arithmetic faults and retain a named implementation allocation ceiling; no machine-width wrap is imposed on Index.

The input boundary now preserves the common source/builder UncheckedProgram, including exact literal/sign trees and unresolved closed arguments, separately from canonical CandidateProgram records. It validates frozen source digests and UTF-8 spans, origin lineage, dependency availability and content correspondence, and explicit resource limits. Deep schema walks are iterative. Successful boundary validation grants no semantic proof or checked status. Independent specification and fresh code-quality review added 12 and 153 targeted probes respectively; these are component checks, not an unseen compiler-composition result.

Eleven independent decimal-ingress cases (`a614580`) pin the baseline's exact typed literal rules: range checking precedes floor quantization, signed literals retain their meaning, and host floating-point rounding cannot erase an out-of-range source value. Fifteen further cases (`b8d0276`) distinguish contextual Index literals/meta data from forbidden implicit helper-argument conversions. They now have common-record scalar tests; raw Python source conformance remains future work. Dated clarifications (`6448cb7`) settled consecutive literal signs and the exact `embed`/`min`/`max` argument conventions before their implementation.

Shared descriptor rules now check every admitted operation family's argument/result/region layout and distinguish kernel launch ports from helper arguments. Known contradictory result representations reject. Actual transfer/helper input shape equality remains a separate safety obligation, so a later pass can distinguish inactive, dynamically selected and certainly active failures. Review caught and repaired a conflicting helper-result case and allocations that exceeded a pass's work allowance before it stopped. These checks confer no proof of dominance, token order, memory safety or whole-program validity.

Scalar normalization now converts closed unchecked expressions into ordinary canonical operations and regions. Lazy conditions, Boolean operators and comparison chains keep explicit captures and ordered effects; helper arguments retain source evaluation order. Exact literal handling shares the type rules, and optional constant facts preserve faults at the operation that would cause them. Reviews added regressions for unrelated type contexts, hostile domain payloads, identifier collisions and work limits. The result is still a provisional scalar fragment: full statement normalization, memory analysis and checked publication remain unfinished.

Structure checking now rebuilds the actual index and validates local value visibility, explicit captures, final terminators and current-token chains in every retained region. Independent reviews tested a separately written nested composition, inactive malformed branches, deep/wide graphs, all six revision dependencies and exhaustive token-source variants. Index traversal is iterative and stops at explicit work/depth limits. These checks establish structural rules; memory safety, contextual metadata, effects and fault totality remain later work.

The memory engineering plan (`96a9bf4`, clarified in `44a9380`) has passed independent review. It separates backing identity from lifetime guarantees, preserves distinct view maps and checks metadata in its actual use context. C1 now admits a captured `Out`/`InOut[Int]` cell as an environment-only ABI operand, including nested helper writes and an `InOut` read under B1/B3. This is a declaration and structural-composition result: context/dependency checks, actual provenance and cell identity at runtime, the complete verifier and execution remain unfinished. C2 context and call-graph work is ongoing; no C2 result is claimed.

The Lab 1 tiled-scale source and its independent expected vectors are recorded as development fixture specifications in `spatial-py@8f80b24`. The paired `tiled_adjust` helper/runtime-branch/tail/overflow case is also specified. Neither fixture has been captured, checked, prepared or simulated by a working compiler path; both are inputs for implementation, not demo results or holdouts.

Independent borrowed-result development cases (`14a074a`) cover conditional returns of distinct backing owners, distinct maps over one owner, actual aliases and nested helper environments. The associated clarification separates backing identity from the lifetime guarantee. These are expectations for future memory checking and execution, not a passed runtime milestone.

Seven further COPY cases (`a8a02dd`) fix competing-fault and empty-transfer expectations: shape first, then each logical item in order, checking destination bounds, source bounds and source initialization. Independent snapshot checks preserve prior writes and show no writes by a failed COPY. They remain future compiler/runtime expectations.

The full verifier remains unimplemented. Its reviewed design (`2f922d4`) requires both input routes to converge after unchecked normalization, keeps dynamic branch faults at their selected effect points, rejects recursion across all retained definitions, and keeps Out DRAM initialization dependent on the supplied owner. It must derive obligations from operations/signatures and publish a checked program only after the entire candidate passes. No checked program, source/check/simulation path or post-freeze unfamiliar-composition pass is claimed yet. The [implementation repository](https://github.com/davidydu/spatial-py/tree/work/initial-reference) and its [support ledger](https://github.com/davidydu/spatial-py/blob/work/initial-reference/docs/support-ledger.md) require repository access.

[[70 - Engineering Architecture Map]] shows the full architecture. [[10 - Source Checker and IR Blueprint]], [[40 - Package and Conformance Blueprint]] and [[PY-R017 - Compiler Representation Comparison]] own the verification and representation obligations behind this goal.
