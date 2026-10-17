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

The reference milestone runs locally on the pinned CPython baseline and standard-library semantic core. On 17 October David confirmed that planned language/reference support should be completed before HLS work, with EE109 Labs 1–3 guiding the progression toward general student programs. [[04 - Python Implementation Roadmap#Current execution direction — 17 October 2026]] records the course families and ordering. The stopped HLS instance is not needed. Request it after the language milestone, once scoped S6/S7 work has an eligible plan, generated HLS source and a testbench ready for vendor simulation or synthesis. Record the actual installed toolchain, device, clock and dependency versions before using vendor results as evidence.

No FPGA resource, timing, RTL or hardware-support claim follows from local simulation.

## Implementation and evidence

The implementation lives in the separate `spatial-py` repository. Its active plan is `docs/plans/2026-10-04-initial-reference.md`; its support ledger and task evidence distinguish completed foundations from the full goal. Historical Scala/Rust repositories remain evidence and are not modified to supply a Python result.

Current execution checkpoint: **`spatial-py@1260959`**, verified on 17 October
with **938 tests from source and 938 from an isolated installed wheel** on
CPython 3.14.5. **The Lab 1 tiled DRAM/SRAM example now produces the expected output
through the Python compiler.** Lab 1's Reg, FIFO and Reduce/Fold families remain
ahead; this is not full lab coverage. The path is source → shared unchecked records → canonical
operations → checked publication → prepared inputs → reference execution.

Both independent Lab 1 vectors pass, including signed Int32 overflow. Each run
has four fresh local allocations, four snapshot copies, 96 writes and 32 reads.
The compiler proves seven conditions and inserts four ordered guards. Results
come from invocation-owned state; original host inputs remain unchanged.
See the [runnable example](https://github.com/davidydu/spatial-py/blob/d2460e3/examples/run_lab1_reference.py),
[recorded outputs](https://github.com/davidydu/spatial-py/blob/d2460e3/docs/evidence/lab1-reference-output.json)
and [execution evidence](https://github.com/davidydu/spatial-py/blob/d2460e3/docs/evidence/task-05a-reference-execution.md).

The important result is the shared mechanism. Independent programs use the same
checks and operation handlers for loops, signed multidimensional views, shared
storage, lazy expressions and faults after earlier writes. A fresh composition,
authored after the implementation froze, passed three cases combining reversed
copies, overlapping writes, partial local initialization and overflow. This is
intermediate evidence of composition, not the final unfamiliar-program gate.

Ordinary statement `if`/`elif`/`else` now uses the same canonical branch
machinery. The original conditional-fault and rank-2 recurrence programs run
unchanged, with exact branch/read/write/fault traces. Ascending recurrence yields
`[1,3,6,10,15,21]`; descending yields `[1,3,5,9,9,11]`. A separate fresh branch
composition passed three cases after the corrected compiler froze. Review also
found and repaired preparation accidentally evaluating another kernel's input
conditions. [Branch evidence](https://github.com/davidydu/spatial-py/blob/10cc1be/docs/evidence/task-05b-statement-branches.md)
records the independent tests, repair, frozen hashes and complete package checks.

**Helper functions now work with both scalar values and shared memory.** The
original tiled-tail example produces `[5,-7,-2147483645,3,1]`; the local-borrow
example produces `37` after six calls sharing caller storage. Each call gets
fresh local storage, checks its inputs and cleans up before returning. Calls
remain explicit operations in the compiler. Both examples run unchanged from
source and from independently written compiler records, with full ordered traces.

See the [source examples](https://github.com/davidydu/spatial-py/blob/aecacc0/examples/kernels/tiled_adjust.py),
[repeatable demo](https://github.com/davidydu/spatial-py/blob/aecacc0/examples/run_helpers_reference.py),
[recorded results](https://github.com/davidydu/spatial-py/blob/aecacc0/docs/evidence/helper-reference-output.json)
and [helper evidence](https://github.com/davidydu/spatial-py/blob/aecacc0/docs/evidence/task-05c-helper-execution.md).
A new program written after the implementation froze passed three cases combining
overlapping helper arguments, swapped aliases, fresh local memory and conditional
returns. Review also found and fixed a missing ordering check in the shared
checker. All 870 tests passed through both package routes on unchanged files.

**Nested helpers now capture surrounding values, memory, output cells and other
helpers.** These declarations work inside functions, loops and branches. Calls
preserve shared storage and view coordinates, check inputs and clean up their
local storage before returning. Source programs and independently written common
records agree on complete ordered traces. See the
[capture demo](https://github.com/davidydu/spatial-py/blob/1260959/examples/run_captures_reference.py),
[recorded results](https://github.com/davidydu/spatial-py/blob/1260959/docs/evidence/capture-reference-output.json)
and [capture evidence](https://github.com/davidydu/spatial-py/blob/1260959/docs/evidence/task-05d-lexical-captures.md).

Independent review caught a quadratic capture-ID search; a regression test now
checks proportional work. A fresh program, authored after the corrected compiler
froze, passed all three cases on its first run and parent replay: outputs 46/24,
or a bounds fault that preserves earlier writes. A previous test needed a Unit
observation-adapter correction and remains separate regression evidence. Both
938-test package suites passed with the frozen source and tests unchanged.

Next: [helpers returning borrowed memory views, together with named view locals](https://github.com/davidydu/spatial-py/blob/1260959/docs/reviews/2026-10-17-after-capture-execution.md).
A caller should be able to keep using a returned view of its own storage after
the helper finishes; returning the helper's temporary storage must reject.
Reuse the existing ownership analysis and call machinery. Meta/static forms,
true resumable budgets, artifact agreement and verified editing remain required.
Current private resource-limit results have no continuation. The full goal
remains open; HLS tools are not needed for this phase.

David accepted earlier source/runtime integration on 12 October. Each admitted
construct receives its complete checks while useful execution grows. The
[active execution plan](https://github.com/davidydu/spatial-py/blob/work/initial-reference/docs/plans/2026-10-13-reference-execution.md)
and [compiler restart state](https://github.com/davidydu/spatial-py/blob/work/initial-reference/PROJECT_STATE.md)
own the detailed next task and newest verified checkpoint.

## Earlier component checkpoints

The following records preserve the evidence and limitations at their original
freezes. Their statements about missing execution describe those earlier stages;
the current integrated result is above.

The independent development data includes 12 memory/effect cases and 133 successful numeric expression observations, plus numeric/type/host/preparation rejection cases. The numeric leaves now replay 116 value observations and 12 direct fault causes. Source-context and lazy-expression rows, fault prefixes, memory execution, host ingress and preparation still require their actual workflow tests. The negative Index bitwise interpretation was recorded explicitly before dependent code. Numeric resource limits are separate from arithmetic faults and retain a named implementation allocation ceiling; no machine-width wrap is imposed on Index.

The input boundary now preserves the common source/builder UncheckedProgram, including exact literal/sign trees and unresolved closed arguments, separately from canonical CandidateProgram records. It validates frozen source digests and UTF-8 spans, origin lineage, dependency availability and content correspondence, and explicit resource limits. Deep schema walks are iterative. Successful boundary validation grants no semantic proof or checked status. Independent specification and fresh code-quality review added 12 and 153 targeted probes respectively; these are component checks, not an unseen compiler-composition result.

Eleven independent decimal-ingress cases (`a614580`) pin the baseline's exact typed literal rules: range checking precedes floor quantization, signed literals retain their meaning, and host floating-point rounding cannot erase an out-of-range source value. Fifteen further cases (`b8d0276`) distinguish contextual Index literals/meta data from forbidden implicit helper-argument conversions. They now have common-record scalar tests; complete raw Python source conformance remains unfinished; the first source seam now covers selected literal cases. Dated clarifications (`6448cb7`) settled consecutive literal signs and the exact `embed`/`min`/`max` argument conventions before their implementation.

Shared descriptor rules now check every admitted operation family's argument/result/region layout and distinguish kernel launch ports from helper arguments. Known contradictory result representations reject. Actual transfer/helper input shape equality remains a separate safety obligation, so a later pass can distinguish inactive, dynamically selected and certainly active failures. Review caught and repaired a conflicting helper-result case and allocations that exceeded a pass's work allowance before it stopped. These checks confer no proof of dominance, token order, memory safety or whole-program validity.

Scalar normalization now converts closed unchecked expressions into ordinary canonical operations and regions. Lazy conditions, Boolean operators and comparison chains keep explicit captures and ordered effects; helper arguments retain source evaluation order. Exact literal handling shares the type rules, and optional constant facts preserve faults at the operation that would cause them. Reviews added regressions for unrelated type contexts, hostile domain payloads, identifier collisions and work limits. The result is still a provisional scalar fragment: full statement normalization, memory analysis and checked publication remain unfinished.

Structure checking now rebuilds the actual index and validates local value visibility, explicit captures, final terminators and current-token chains in every retained region. Independent reviews tested a separately written nested composition, inactive malformed branches, deep/wide graphs, all six revision dependencies and exhaustive token-source variants. Index traversal is iterative and stops at explicit work/depth limits. C2 adds contextual metadata checks below; memory safety, effects and fault totality remain unfinished.

The memory engineering plan (`96a9bf4`, clarified in `44a9380`) has passed independent review. It separates backing identity from lifetime guarantees and preserves distinct view maps. C1 admits a captured `Out`/`InOut[Int]` cell as an environment-only ABI operand, including nested helper writes and an `InOut` read under B1/B3. C2 derives private retained-call and contextual-metadata analysis: recursion rejects across all retained definitions, and Index metadata is checked at each signature, region, operation and call use against local scope and dominance. It also preserves explicit capture/ABI mappings, verifies loop-carry entry and backedge correspondence, and binds frozen query maps to the candidate, registry, formal witnesses and revision dependencies under explicit budgets. C3 derives persistent memory maps and ordered access plans, preserving signed and intermediate view bounds, allocation/use obligations and scalar-cell references across structured control. Identity reborrow retains the source bounds chain and its failure attribution. COPY plans retain shape and endpoint prerequisites, ordered per-item preflight, and snapshot/write phases. Independent specification review passed with 1,533 additional parent metadata observations. C4 derives actual owner roots for borrowed helper results, substitutes them through nested calls and loop recurrences, preserves view-map and cell identity, and checks returned guarantees against the actual handle and backing lifetimes. Its supplied-signature guarantee is validated separately. All eight borrowed-result fixture groups have structural projections, but no runtime writes were executed. C5 combines these results in one identity-bound report and accounts for every unresolved representation, metadata-totality, memory-safety, initialization and effect requirement with its later consumer. The reviewed general composition retains 26 access obligations, seven events and three helper-entry equalities: 36 items still need D/E dispositions. D1 now adds scalar/control facts and a generic condition inventory, but it does not dispose of those obligations. E owns effects and initialization. F normalization, G checked publication, source frontend, host and simulator remain unfinished. The C1–C5 analysis does not grant checked publication or execution.

D1 tracks signed Int32, exact Index and Bool facts within each definition and through branches, with conservative loop carries. Helper arguments and call results remain unknown. It records nonzero divisors, nonnegative shift counts, checked-embed range and nonzero loop-step conditions at their original operation points; for example, `x / 0` is known invalid even when `x` is unknown. Fault conditions and token locations are retained, but D1 does not choose rejection, guards or unreachable dispositions. D2a supplies scalar predicate evaluation and D2b supplies memory-state observations below. D3a now adds conservative exported-root/call reachability and scalar decisions. The full verifier, source execution, preparation and simulation remain later work. Independent Opus 5.5 review of the design, code and corrections accompanied specification and parent reviews; the review history is summarized in the implementation evidence.

The Lab 1 tiled-scale source and its independent expected vectors are recorded as development fixture specifications in `spatial-py@8f80b24`. The paired `tiled_adjust` helper/runtime-branch/tail/overflow case is also specified. The Lab 1 source now reaches canonical analyses through the shared path above. The companion still requires helper/branch support; neither fixture has been prepared or simulated. They remain development fixtures rather than holdouts.

Independent borrowed-result development cases (`14a074a`) cover conditional returns of distinct backing owners, distinct maps over one owner, actual aliases and nested helper environments. The associated clarification separates backing identity from the lifetime guarantee. These are expectations for future memory checking and execution, not a passed runtime milestone.

Seven further COPY cases (`a8a02dd`) fix competing-fault and empty-transfer expectations: shape first, then each logical item in order, checking destination bounds, source bounds and source initialization. Independent snapshot checks preserve prior writes and show no writes by a failed COPY. D2b now checks their preflight outcomes against supplied memory snapshots. Source-value transfer, destination writes and committed runtime state remain future work.


D2a connects every D1 scalar condition and the supported C5 extent, step, helper-shape and metadata-totality requirements to an evaluation request. Compile-time parameters stay fixed; runtime values come from the correct local scope. Every remaining memory obligation stays visible for later enforcement. Boolean conditions short-circuit arithmetic while still validating all captured inputs; shape checks preserve dimension evaluation order. Independent specification and parent quality reviews passed, including fixes for two malformed-report cases. The 22 dedicated tests are supplemented by 938 parent scalar observations and 34 contextual and obligation-retention cases. These establish component behavior, not whole-program execution or a safety proof. The [checkpoint evidence](https://github.com/davidydu/spatial-py/blob/cb868d6/docs/evidence/task-02d2a-predicates.md) requires implementation-repository access.

D2b checks every logical view layer before the backing address, so a valid final address cannot hide an invalid intermediate view. Aliases share one initialization state; a write-only output can retain cells initialized before the call. Allocation generation is separate from contents version, so ordinary writes do not invalidate existing views. COPY checks shape first, then both lifetimes, then each logical item’s destination bounds, source bounds and source initialization. Empty copies still require live endpoints. No transfer or output publication occurs in this checkpoint.

The compiler bridge groups related checks at their original access or COPY point, preserves all prior numerical requests, and keeps every deferred initialization/effect consumer visible. Independent specification and parent quality reviews passed after four reproduced boundary fixes. The 24 dedicated tests cover the 16 memory snapshot cases and seven COPY groups; parent probes add 405 view/completion and 648 COPY/alias observations. All are component evidence. The [D2b checkpoint evidence](https://github.com/davidydu/spatial-py/blob/db792fb/docs/evidence/task-02d2b-memory-predicates.md) requires implementation-repository access.

D3a distinguishes reachable code from a point that execution certainly reaches. An unconditional `x / 0` at a prepared kernel’s entry receives a rejection decision. The same operation under a runtime branch needs a selected-path check. After a possibly failing memory operation, it keeps its later position. A helper stays generic across all callers, and selecting one kernel cannot hide a second exported kernel. At that D3a checkpoint, every memory and authored requirement remained explicitly deferred.

The 32 new tests cover these decisions, 1,100 nested regions, shared helpers, call order and multiple exports. Independent specification and parent code reviews passed after two resource-accounting fixes. Independent probes include 36 control-flow graphs checked against a separate path enumerator and a further unfamiliar component composition. That checkpoint passed all 454 tests from source and an isolated installed wheel. The [D3a evidence](https://github.com/davidydu/spatial-py/blob/704c190/docs/evidence/task-02d3a-decisions.md) records the checks and limitations; repository access is required. This is decision planning, not inserted guards or a completed execution.

D3b adds a decision for every derived memory or metadata request. A known shape calculation can be proved without pretending that a particular runtime buffer has that shape. Reads, writes, scalar cells, extent queries and copies retain checks for the state they will actually encounter. Even an empty copy keeps its lifetime checks. Two calls to one generic helper retain their distinct shape-check results.

Entry checks are separate from body checks: successful entry cannot be used to prove that entry itself succeeds. Reaching an operation also does not prove that every internal check is reached; an earlier check may fail. D3b keeps those phases conservative and preserves false results, arithmetic faults and analysis limits separately. Tokenless unresolved operations remain unsupported. Descriptor correspondence, effect and initialization work, and authored requirements stay explicit; a planned check is not an inserted guard.

The 17 new tests include three independent review cases retained as regressions: different shapes at two calls, a shape-evaluation fault that must precede a mismatch, and a valid calculation returning zero. Independent specification and parent code reviews passed. Ten additional probe methods exercise composed memory/control programs, entry rules, malformed inputs and cumulative budgets; a new composition after production freeze combines helpers, an ordered region, a signed loop and a runtime branch. These are component checks. The [D3b evidence](https://github.com/davidydu/spatial-py/blob/1feb2ac/docs/evidence/task-02d3b-memory-decisions.md) records the 471-test source and installed-package results and the remaining boundaries.

D3c compares each pending shape or capacity description with its defining recipe. For example, a view selecting positions 0, 2 and 4 has three elements; advertising two is a contradiction. That contradiction remains visible even inside a branch that never executes. Equal recipes can agree while their separate evaluation or memory-safety checks still need enforcement.

The pass uses existing contextual substitutions and the existing arithmetic evaluator. Generic helper parameters remain generic across calls, and a loop's initial value does not become an assumption about every iteration. Unknown extent queries also stay unknown; a declared shape cannot certify itself. Every earlier safety decision and unfinished effect or initialization requirement is retained.

The 23 new test methods include 24 independently specified candidates and a new composition written after production freeze: a reverse multidimensional view, captures, a false branch, a zero-trip loop and a borrowed helper result. Independent specification and parent quality reviews passed. Parent checks add 360 signed/empty view observations, 102 malformed-boundary rejections and a 1,100-level expression. The [D3c evidence](https://github.com/davidydu/spatial-py/blob/6d098ea/docs/evidence/task-02d3c-descriptor-correspondence.md) records the 494-test source and installed-package results. These are compiler-component checks; no complete program has been simulated yet.

D3d checks that each authored requirement attaches exactly once to its declared owner and refers to values available immediately before that operation. It reuses the existing rules for local captures and compile-time parameters. A request on a helper call uses the caller's scope. Memory coordinates must match the storage rank; mutable scalar cells stay distinct from arrays.

This admits a request's structure, not its claims. A supplied false activation cannot silence a compiler-derived divide-by-zero finding. Asking for a check at preparation time does not move it ahead of earlier writes. Existing guards retain their actual operands and failure tags, with correctness still pending. Every request keeps its unfinished semantic, placement, enforcement and execution-order checks visible.

The 26 new test methods include 47 independently specified variants and a new composition authored after production freeze: a helper with an earlier write, nested captures and branches, a zero-trip loop, two calls, six authored requests and an incomplete guard. Independent Codex specification review and parent quality review passed. Parent probes add 37 malformed-boundary rejections and 25 resource/depth observations, including a 1,100-level expression. The [D3d evidence](https://github.com/davidydu/spatial-py/blob/c27f6f1/docs/evidence/task-02d3d-authored-admission.md) records the 520-test source and installed-package results. These remain component checks, not an executed program.

D4a adds the closed canonical guard-demand language. Every condition the checker derives (nonzero divisors and loop steps, shift counts, embed ranges, metadata totality, entry and allocation extents, view steps, helper entry shapes, access and COPY preflight, liveness) and every authored condition is now one closed predicate with explicit typed subjects, and each guard declares the closed set of fault kinds it may report. A requirement row says whether it was authored or compiler-derived, and the verifier checks that claim in both directions: a derived row must match the demand it enforces exactly, and an authored row is only ever an additional condition.

The pass orders the checks of one operation as the 12 October contract clarification fixes them (descriptor metadata, then contract checks, then operand conditions, then memory preflight, with authored conditions first) and decides each check at its position: a check certain to fail at a certainly reached position is rejected even when a guard already exists, because a guard cannot make a certainly failing program valid; everything after an unproved check keeps unknown activation. An allocation whose runtime extent is known to exceed its capacity, a view with a known zero step and a helper call with a known shape mismatch are now rejected statically, as the language contract requires. Identical derived demands at one owner merge, a resource-limited unknown yields to a known truth, and tokenless owners keep their unsupported status. Guards must form one contiguous block immediately before their owner with exact operands and signatures.

Independent Opus design review and an inventory audit corrected the first draft before code; an independent specification review and a quality review of the frozen implementation found reproduced defects (a resource limit reported as a disagreement, authored conditions outside the activation chain, memory signatures missing coordinate faults, a reference cycle, an uncharged quadratic scan), all fixed and re-verified. 43 independent test methods over 149 hand-derived table cases independent executable cases and a fresh post-freeze composition accompany 29 dedicated test methods. The [D4a evidence](https://github.com/davidydu/spatial-py/blob/48687f3/docs/evidence/task-02d4a-guard-demands.md) records the 613-test source and installed-package results.

A subsequent Codex review reproduced an ordering defect: authored predicates could spend the shared evaluation allowance in owner order instead of declaration order. The [repair at b11ebde](https://github.com/davidydu/spatial-py/blob/b11ebde/docs/evidence/task-02d4a-observation-order-repair.md) now observes eligible authored conditions in declaration order before owners reuse the results. Seven new regression methods and independent review cover inactive conditions, derived mirrors, phase order and cumulative limits.

The private source seam uses generic syntax and binding rules, with explicit lexical captures and exact UTF-8 source locations. It does not execute Python decorators, annotations or kernel bodies. Review found and repaired borrowed-handle shadowing, late core aliases, generated Boolean depth, exception classification and identifier amplification; independent tests include a new three-level composition. CPython's own parser limits still apply: a 5,000-digit decimal literal reports a source-syntax failure. Helpers, meta/static expansion, branch statements and the full capture/template API remain outside this first seam.

Shared normalization now connects declarations, loop domains, views and transfers to canonical operations. Reviews repaired child descriptor remapping, missing lexical captures hidden by aliases, typed literal lineage and known-sign slice defaults. A fresh post-freeze composition passed without a new compiler path. Next, connect ordered guards, effects/initialization, complete checking/publication and prepared reference execution for the admitted constructs. The Lab 1 result comes before expanding through its tail/helper/branch companion and the full original acceptance matrix. Guard insertion and successful-prefix recomputation remain required work on this route.

At the earlier component checkpoint, the full verifier remained unimplemented. Its reviewed design (`2f922d4`) requires both input routes to converge after unchecked normalization, keeps dynamic branch faults at their selected effect points, rejects recursion across all retained definitions, and keeps Out DRAM initialization dependent on the supplied owner. It must derive obligations from operations/signatures and publish a checked program only after the entire candidate passes. That component checkpoint did not claim checked publication or execution. The current private execution result is recorded above; the final whole-compiler unfamiliar-composition gate remains open. The [implementation repository](https://github.com/davidydu/spatial-py/tree/work/initial-reference) and its [support ledger](https://github.com/davidydu/spatial-py/blob/work/initial-reference/docs/support-ledger.md) require repository access.

[[70 - Engineering Architecture Map]] shows the full architecture. [[10 - Source Checker and IR Blueprint]], [[40 - Package and Conformance Blueprint]] and [[PY-R017 - Compiler Representation Comparison]] own the verification and representation obligations behind this goal.
