---
type: plan
title: "Managed Python Spatial research"
scope: "Complete pre-implementation research and professor-review package"
project: spatial-python
date: 2026-09-30
status: active
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
| PY-R008 onward | HLS families and any separately needed advanced semantic study | Reviewed program model; allocate scopes to avoid overlapping writers |

Identifiers reserve study scope, not a claim that the documents are complete. Publish only coherent batches with working links and clear current status. Reviewers must not certify their own study as an independent review.

## Completion requirements

| ID | Required artifact or evidence | Baseline |
|---|---|---|
| R01 | Clear public programming-model recommendation, compared fairly with alternatives on the three cases, composition, and diagnostics | Incomplete |
| R02 | Numeric policy covering bounded integers, fixed point, floating point, literals, conversions, exceptional cases, reductions, and folds | Incomplete |
| R03 | Control, state, aliasing, memory/dimensions, queues/streams, ordering, termination, and simulation contract | Incomplete |
| R04 | Every one of the 106 original-spec documents accounted for in a crosswalk, plus a check against source language/node families for omissions | Incomplete |
| R05 | Python-owned source/unchecked/checked program representations, module boundaries, pass invariants, effects, provenance, and serialization/reproducibility strategy | Incomplete |
| R06 | Explicit framework/dependency choice and reasons, including the limits of native tools under the pure Python requirement | Incomplete |
| R07 | Host workflow, file/notebook ingestion, errors, packaging, invocation, and compatibility/migration strategy | Incomplete |
| R08 | HLS mapping and compiler-versus-vendor responsibilities across the full intended language; distinguish functionality, scheduling, resource fit, and timing evidence | Incomplete |
| R09 | Conformance and performance plan with independent references, boundary/composition/negative cases, declared workload targets, and reproducibility | Incomplete |
| R10 | Implementation plan in vertical slices that advances toward the full rewrite, with dependencies, entry/exit checks, and approval boundary | Incomplete |
| R11 | One coherent architecture recommendation, shared decision proposal, and a short professor brief explaining the big picture and tradeoffs | Incomplete |
| R12 | Independent review findings resolved, source checks documented, links/schemas/site build checked, commits pushed, live pages verified | Incomplete |

Research completion means these artifacts answer the design questions with evidence and explicit limits. It does not mean a compiler exists or that unrun vendor experiments passed. Do not substitute an introductory subset for the full architecture. If a construct needs a later implementation stage, identify its representation, semantic obligations, intended lowering path, and acceptance evidence now. If a real research blocker prevents doing that, keep the requirement open.

## Decision authority and assumptions

[[D-27]] remains the accepted direction. The manager may select and defend research recommendations under this mandate. Record detailed architecture choices as **proposed for professor review**, with alternatives and reversal conditions; do not label them professor-approved. A complete proposed contract can be reviewed before becoming an adopted implementation contract.

Assume adequate engineering skills and implementation capacity. Favor semantic clarity and evidence over language familiarity or the amount of code already written. Keep compiler and simulator latency as measured engineering questions, separate from generated hardware behavior. Prefer explicit, explainable semantics where original simulation and hardware disagree; record any proposed divergence.

Use pinned local source first and primary external documentation when needed. Isolated research probes may investigate a stated question; their scope, inputs, environment, and observed results must be recorded. They do not become a production frontend or an implicit architecture approval.

## Durable work record

| Wave | Current state | Next action |
|---|---|---|
| 1 | Three Sol extra-high research writers dispatched; manager collecting the full-scope baseline | Verify decisive source claims and reconcile proposed rules |
| 2 | Not started | Begin after programming-model review; prepare the source inventory in parallel |
| 3 | Not started | Use the reviewed language/representation contract |
| 4 | Not started | Assign independent reviewers after a coherent draft exists |
| 5 | Not started | Audit R01–R12 against actual artifacts and external publication state |

Update this table and [[progress-log]] at coherent checkpoints. The goal remains active until the requirement-by-requirement completion audit passes. A returned subagent summary, a plausible proposal, or a green site build alone does not complete the research.
