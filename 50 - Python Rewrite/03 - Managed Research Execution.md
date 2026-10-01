---
type: plan
title: "Managed Python Spatial research"
scope: "Complete pre-implementation research and professor-review package"
project: spatial-python
date: 2026-09-30
status: complete
---

## Mandate

David asked the main agent to manage the big picture and complete the research while he is away. Subagents must use **GPT-6.1 Sol with extra-high reasoning**, through Codex. This extends the current [[01 - Python Research Plan]] into an execution plan. It authorizes research, review, documentation, and publication; it does not report professor approval of a detailed architecture or begin production compiler implementation.

The objective is a complete, defensible design recommendation for pure Python Spatial: programming model, semantics, compiler architecture, HLS lowering strategy, validation, and an implementation sequence. The first three programs are an entry point. They do not define the scope of the whole rewrite.

## Baseline

At research-vault revision `7a15c26`, [[PY-R001 - Programming Model Study]] has six illustrative programs. They have passed Python syntax parsing, not compiler execution. Numeric and effect policy, diagnostics, composition, architecture, and HLS decisions remain open. The Python research section was published by [site run 36815858123](https://github.com/davidydu/spatial-research-site/actions/runs/36815858123); direct HTTP checks confirmed the new index, study, direction record, and homepage.

The current original-spec tree contains **106 documents whose frontmatter is `type: spec`**, across nine top-level subject areas. [[01 - Python Coverage Ledger]] accounts for them and the required source-family gap check. This is a fresh document inventory, not a count of supported language features or verified compiler behavior. Older dated coverage counts remain unchanged.

## Work sequence

| Wave | Work | Required result before advancing |
|---|---|---|
| 1. Language foundations | Numeric/reduction rules; control/memory/effects; capture/composition/diagnostics | Source-grounded alternatives, concrete proposed rules, discriminating cases, and a reviewed programming-model recommendation |
| 2. Compiler and full scope | Full source-spec crosswalk; program representation and passes; dependencies, host workflow, and validation | An architecture that represents the full intended language, with explicit staged support and no whole-program recognizer shortcut |
| 3. HLS design | Mapping numeric behavior, controllers, transfers, storage, streams, scheduling, and external interfaces | A semantic-preservation argument and capability/validation conditions for each family; unresolved vendor evidence labeled accurately |
| 4. Challenge and repair | Independent semantic and architecture reviews; bounded reproducible research probes where they settle a question | Material findings repaired; recommendations and their strongest objections documented |
| 5. Synthesis and publication | Decision proposal, proposed contracts, implementation sequence, professor brief, final evidence audit | A consistent review package, complete coverage/accounting, passing documentation checks and verified website deployment |

Run independent tasks concurrently within the available slots. Give each writer a separate file. The manager owns priorities, integration, cross-document consistency, and the final recommendation. A later wave may prepare an independent inventory while an earlier wave is running, but must not finalize choices that depend on unreviewed results.

## Study assignments

| Study | Responsibility | Dependency |
|---|---|---|
| PY-R001 | Initial paired programs; manager integrates later corrections and the surface recommendation | Existing draft |
| PY-R002 | Exact numeric, reduction, and fold semantics | Pinned original numeric and controller sources |
| PY-R003 | Control, memory, state, aliasing, and observable effects | Pinned original simulation and hardware paths |
| PY-R004 | Source capture, builders, composition, source provenance, and matched diagnostics | Both candidate surfaces and primary Python/compiler sources |
| PY-R005 | Full-language coverage and migration dispositions; complete the coverage ledger | Foundation studies plus all original-spec and source families |
| PY-R006 | Python compiler architecture, IR/pass contracts, framework/dependency comparison | Reviewed language foundations and selected surface |
| PY-R007 | Host/package workflow, reproducibility, conformance strategy, and feedback-time targets | The proposed language and compiler boundary |
| PY-R008 | Advanced state, communication, transfer, and termination semantics | Foundation control/numeric studies and full-language inventory |
| PY-R009 | HLS boundary, control routes, faults, and ABI | Reviewed program model and advanced protocols |
| PY-R010 | Memory, transfers, banking, scheduling, and DSE | Logical memory/protocol contracts and primary vendor evidence |
| PY-R011 | Numeric lowering, special values, intrinsic/RNG profiles | Exact numeric proposal and primary vendor evidence |

Identifiers reserve study scope, not a claim that the documents are complete. Publish only coherent batches with working links and clear current status. Reviewers must not certify their own study as an independent review.

## Completion requirements

| ID | Required artifact or evidence | Current status |
|---|---|---|
| R01 | Clear public programming-model recommendation, compared fairly with alternatives on the three cases, composition, and diagnostics | Research accepted; see completion audit |
| R02 | Numeric policy covering bounded integers, fixed point, floating point, literals, conversions, exceptional cases, reductions, and folds | Research accepted; see completion audit |
| R03 | Control, state, aliasing, memory/dimensions, queues/streams, ordering, termination, and simulation contract | Research accepted; see completion audit |
| R04 | Every one of the 106 original-spec documents accounted for in a crosswalk, plus a check against source language/node families for omissions | Research accepted; see completion audit |
| R05 | Python-owned source/unchecked/checked program representations, module boundaries, pass invariants, effects, provenance, and serialization/reproducibility strategy | Research accepted; see completion audit |
| R06 | Explicit framework/dependency choice and reasons, including the limits of native tools under the pure Python requirement | Research accepted; see completion audit |
| R07 | Host workflow, file/notebook ingestion, errors, packaging, invocation, and compatibility/migration strategy | Research accepted; see completion audit |
| R08 | HLS mapping and compiler-versus-vendor responsibilities across the full intended language; distinguish functionality, scheduling, resource fit, and timing evidence | Research accepted; see completion audit |
| R09 | Conformance and performance plan with independent references, boundary/composition/negative cases, declared workload targets, and reproducibility | Research accepted; see completion audit |
| R10 | Implementation plan in vertical slices that advances toward the full rewrite, with dependencies, entry/exit checks, and approval boundary | Research accepted; see completion audit |
| R11 | One coherent architecture recommendation, shared decision proposal, and a short professor brief explaining the big picture and tradeoffs | Research accepted; see completion audit |
| R12 | Independent review findings resolved, source checks documented, links/schemas/site build checked, commits pushed, live pages verified | Complete; checks passed and full package published |

Research completion means these artifacts answer the design questions with evidence and explicit limits. It does not mean a compiler exists or that unrun vendor experiments passed. Do not substitute an introductory subset for the full architecture. If a construct needs a later implementation stage, identify its representation, semantic obligations, intended lowering path, and acceptance evidence now. If a real research blocker prevents doing that, keep the requirement open.

## Decision authority and assumptions

[[D-27]] remains the accepted direction. The manager may select and defend research recommendations under this mandate. Record detailed architecture choices as **proposed for professor review**, with alternatives and reversal conditions; do not label them professor-approved. A complete proposed contract can be reviewed before becoming an adopted implementation contract.

Assume adequate engineering skills and implementation capacity. Favor semantic clarity and evidence over language familiarity or the amount of code already written. Keep compiler and simulator latency as measured engineering questions, separate from generated hardware behavior. Prefer explicit, explainable semantics where original simulation and hardware disagree; record any proposed divergence.

Use pinned local source first and primary external documentation when needed. Isolated research probes may investigate a stated question; their scope, inputs, environment, and observed results must be recorded. They do not become a production frontend or an implicit architecture approval.

## Durable work record

| Wave | Current state | Remaining action |
|---|---|---|
| 1 | R001–004 researched, source-checked, independently reproduced where bounded probes apply, integrated into proposed language/numeric/state contracts | Adoption and future executable conformance |
| 2 | Complete 106-document/124-path crosswalk, architecture/framework and host/validation proposals; manager acceptance recorded | Future implementation measurements and feature evidence |
| 3 | R008 advanced protocols and R009–011 full-family HLS mappings reviewed, with explicit target/profile gates | Locked tool/device, certificates, vendor/RTL/resource evidence during implementation |
| 4 | Independent architecture, numeric and protocol/HLS findings repaired and reread | Retain counterexamples as future acceptance cases |
| 5 | D-28, professor brief, four proposed contracts, S0–S9 roadmap and full requirement audit validated and published | Professor review before production implementation |

[[06 - Python Research Completion Audit]] records the requirement-by-requirement evidence. All detailed architecture/contracts remain proposed under D-28, and production implementation is not started. All R01–R12 research requirements are complete, including successful deployment and direct live-content checks recorded in the audit. Research acceptance does not substitute for implementation evidence.
