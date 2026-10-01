---
type: moc
title: "Spatial Research"
date: 2026-10-01
---

Research toward a pure Python rewrite of Spatial. First establish the programming model and its meaning; then investigate lowering to HLS. This site connects that work to the original source, experiments, and specification.

> [!important] Current direction — professor feedback, 30 September 2026
> **Pure Python Spatial, including the compiler.** First work out what Spatial programs and their implementation look like in Python, then study HLS lowering. This replaces the earlier Python-frontend/Rust-core proposal. See [[2026-09-30-pure-python-programming-model|the new research direction and first program sketch]].

## Start with the Python rewrite

Start at [[00 - Python Rewrite Index|Python Spatial research]]. It connects the examples, studies, open questions, and decisions. The [[01 - Python Research Plan|research plan]] sets the order: programming model, semantics, compiler design, then HLS research and implementation planning.

The [[PY-R001 - Programming Model Study|programming-model study]] compares source capture and an explicit builder on the same [[PY-E001 - Initial Example Corpus|three example programs]]. The completed research now includes [[00 - Implementation Design Index|five implementation blueprints]] and a [[07 - Python Implementation Readiness Audit|readiness review with bounded probes]]. [[D-27]] records the agreed direction; [[D-28]] proposes the detailed architecture for professor review. No Python compiler implementation is claimed.

The <a href="presentation/python/index.html" data-router-ignore target="_blank" rel="noopener noreferrer">Spatial in Python presentation</a> follows one program through the proposed design in seven slides. Its [[2026-10-01-python-professor-presentation-outline|ten-minute outline and full speaker notes]] link each claim to the research. The [[05 - Python Professor Brief|professor brief]] is the short written version.

The <a href="presentation/index.html" data-router-ignore target="_blank" rel="noopener noreferrer">28 September presentation</a> and [[2026-09-28-spatial-professor-presentation-outline|speaking outline]] are historical. Their Rust-core recommendation was superseded by the professor's feedback.

## Earlier research and evidence

| Read | Purpose |
|---|---|
| [[D-26-professor-brief\|Earlier professor brief]] | The superseded recommendation and the evidence presented |
| [[D-26-final-architecture\|Earlier architecture proposal]] | Historical Rust-core design, retained for the research record |
| [[2026-09-28-d26-research-extension\|Research method and debate]] | Why the recommendation changed; competing case; measured versus inferred conclusions |
| [[D-26-12-simulator-spike\|Matched interpreter experiment]] | Exact-output checks, runtime measurements, independent repeat and reproducibility archive |
| [[D-26\|Original D-26 protocol and meeting cut]] | Frozen hypotheses, mistake list, historical recommendation and audit trail |

## What comes next

Review [[D-28|the proposed architecture and semantic choices]], then begin one complete path through source capture, checking, simulation and diagnostics for a composed memory kernel. The [[04 - Python Implementation Roadmap|implementation roadmap]] expands that path across numeric, stateful and communicating programs.

The compiler's checks, program representation and reference simulation are proposed in Python. HLS planning can start on the first checked subset while broader semantics develop. The existing specification and tests remain evidence to review and reuse. Fresh Python-generated target validation is a later gate.

## Current state

| Area | Verified state | Remaining work |
|---|---|---|
| Research | Full-language research, five implementation blueprints and bounded readiness probes complete as proposed research | Professor review of D-28 and deliberate semantic choices |
| Python compiler | Frontend, checker, program representation and simulator specified in proposed blueprints; no production implementation | After approval, build the first complete capture/check/simulation path |
| Hardware evidence | Historical 39-program backend corpus: 37 fit, 2 over budget, 14 initiation-interval caveats | Fresh evidence for changed HLS and the general backend before release |
| Student delivery | Proposed host workflow, package interfaces and validation gates documented | Implement and validate the package and composed program families |

See [[2026-06-27-rust-spatial-rewrite-roadmap|Historical Rust roadmap and backend evidence]], [[D-26-05-boundary-design|Earlier boundary study]], and [[progress-log|Verification history]]. Historical vendor results do not certify the future Python compiler.

## Explore the evidence

| Topic | Entry point |
|---|---|
| Original Spatial specification | [[10 - Spec/00 - Spec Index\|Specification index]] |
| Python construct and semantic mapping | [[00 - Python Mapping Overview\|Python mapping overview]] |
| Same-lab syntax comparison | [[D-26-02-student-surface-comparison\|Surface study]] |
| Real diagnostic transcripts | [[D-26-03-error-paths\|Error-path study]] |
| HLS mapping | [[10 - Clean Mappings\|Clean mappings]] |
| Scope and corpus | [[03-mvp-subset-recommendation\|MVP subset research]] |
| Current Python questions and shared decisions | [[02 - Python Open Questions\|Python questions]] · [[40 - Decision Queue\|Decision queue]] |
| Vault map and conventions | [[00 - Index\|Top-level index]] · [[workflow\|Research workflow]] |

Research notes distinguish measured results, inspected precedents, proposed designs and engineering judgments. Pinned code references resolve through [[reference-clones|the source manifest]]. An `awaiting-professor-approval` proposal is not an implemented feature or an approved course release.

The [research vault](https://github.com/davidydu/spatial-research) is the source of this site. [Quartz](https://quartz.jzhao.xyz/) renders it; website configuration lives in the [site repository](https://github.com/davidydu/spatial-research-site).
