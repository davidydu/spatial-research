---
type: moc
title: "Spatial Research"
date: 2026-09-28
---

Research toward a teachable Spatial hardware language and a compositional compiler targeting HLS. This site connects the proposed architecture to its source evidence, experiments and implementation specification.

> [!important] Architecture proposal ready for professor review
> **Restricted Python kernel source over one Rust semantic core.** Capture source without execution, check one hardware contract, and lower a typed controller tree to functional simulation or HLS. Implementation of this architecture awaits professor approval.

## For reviewers

<a href="presentation/index.html" data-router-ignore target="_blank" rel="noopener noreferrer">Open the presentation</a> · [[2026-09-28-spatial-professor-presentation-outline|Screen outline and speaking plan]]

| Read | Purpose |
|---|---|
| [[D-26-professor-brief\|Professor approval brief]] | The recommendation, evidence, tradeoffs and decision to approve |
| [[D-26-final-architecture\|Final architecture plan]] | Source workflow, semantic ownership, delivery commitments and staged gates |
| [[2026-09-28-d26-research-extension\|Research method and debate]] | Why the recommendation changed; competing case; measured versus inferred conclusions |
| [[D-26-12-simulator-spike\|Matched interpreter experiment]] | Exact-output checks, runtime measurements, independent repeat and reproducibility archive |
| [[D-26\|Original D-26 protocol and meeting cut]] | Frozen hypotheses, mistake list, historical recommendation and audit trail |

## Research result

The architecture separates **student syntax**, **semantic implementation**, and **Python tooling**. A token-backed Python AST can preserve the required hardware information without a second checker. The chosen Rust core owns names, constants, types, legality and exact functional behavior. Python owns source capture and the host/testbench experience.

This is a selected engineering proposal. No learner study has established a universally best teaching syntax. The explicit tradeoff is additional frontend integration in exchange for familiar authoring; the full plan retains paired conformance labs and all original Python-surface guarantees.

## Current state

| Area | Verified state | Remaining work |
|---|---|---|
| Research | D-26 meeting cut audited; follow-up debate and bounded interpreter experiment documented | Learner outcomes and full-system acceptance remain unmeasured |
| Prototype compiler | Text `check` CLI and existing parser/constant/HIR/classifier infrastructure | General checker/controller interpreter, source-captured Python frontend and structural migration |
| Hardware evidence | Historical 39-program backend corpus: 37 fit, 2 over budget, 14 initiation-interval caveats | Fresh evidence for changed HLS and the general backend before release |
| Student delivery | Versioned host contracts and packaging mechanisms researched | Full JSON commands, tested wheels, notebook adapter and release CI |

See [[2026-06-27-rust-spatial-rewrite-roadmap|Backend evidence and implementation roadmap]], [[D-26-05-boundary-design|Boundary and implemented CLI limits]], and [[progress-log|Verification history]]. Historical vendor results do not certify the proposed general compiler.

## Explore the evidence

| Topic | Entry point |
|---|---|
| Full language specification | [[10 - Spec/00 - Spec Index\|Specification index]] |
| Python construct and semantic mapping | [[00 - Python Mapping Overview\|Python mapping overview]] |
| Same-lab syntax comparison | [[D-26-02-student-surface-comparison\|Surface study]] |
| Real diagnostic transcripts | [[D-26-03-error-paths\|Error-path study]] |
| HLS mapping | [[10 - Clean Mappings\|Clean mappings]] |
| Scope and corpus | [[03-mvp-subset-recommendation\|MVP subset research]] |
| Decisions and unresolved issues | [[40 - Decision Queue\|Decision queue]] · [[20 - Open Questions\|Open questions]] |
| Vault map and conventions | [[00 - Index\|Top-level index]] · [[workflow\|Research workflow]] |

Research notes distinguish measured results, inspected precedents, proposed designs and engineering judgments. Pinned code references resolve through [[reference-clones|the source manifest]]. An `awaiting-professor-approval` proposal is not an implemented feature or an approved course release.

The [research vault](https://github.com/davidydu/spatial-research) is the source of this site. [Quartz](https://quartz.jzhao.xyz/) renders it; website configuration lives in the [site repository](https://github.com/davidydu/spatial-research-site).
