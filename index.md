---
type: moc
title: "Spatial Research"
date: 2026-10-22
---

Research and implementation toward a pure Python rewrite of Spatial. A bounded compiler now takes Python Spatial programs through checking, generated C++ and HLS/RTL validation. This site connects the design, implementation evidence and remaining work to the original Spatial source.

> [!important] Current direction — professor feedback, 30 September 2026
> **Pure Python Spatial, including the compiler.** First work out what Spatial programs and their implementation look like in Python, then study HLS lowering. This replaces the earlier Python-frontend/Rust-core proposal. See [[2026-09-30-pure-python-programming-model|the new research direction and first program sketch]].

## Start with the Python rewrite

Start at [[00 - Python Rewrite Index|Python Spatial research]]. It connects the examples, studies, open questions, and decisions. The [[01 - Python Research Plan|research plan]] sets the order: programming model, semantics, compiler design, then HLS research and implementation planning.

The [[PY-R001 - Programming Model Study|programming-model study]] compares source capture and an explicit builder on the same [[PY-E001 - Initial Example Corpus|three example programs]]. The research includes [[00 - Implementation Design Index|five implementation blueprints]] and a [[07 - Python Implementation Readiness Audit|readiness review with bounded probes]]. [[D-27]] records the agreed pure Python direction; [[D-28]] proposes the full architecture for professor review. The separately authorized [[80 - Initial Compiler Goal|initial compiler implementation]] has its own support boundaries and acceptance gates.

**Latest local change:** [[2026-10-22-scalar-interface-checkpoint|Explicit scalar input seeds and output results]] now replace the inferred singleton interfaces. The wrapper and report checker pass local review, a fresh composition, and 1,351 tests per source/package route; fresh vendor validation is pending.

**Latest hardware result:** [[2026-10-22-scalar-vitis-checkpoint|12 saved projects and 32 independent cases]] pass Vitis C simulation, synthesis and RTL co-simulation without compiler changes. These cover scalar state, shifts, dot products, ordered updates and tiled memory programs. The next step is to validate the updated scalar wrapper against fresh vendor reports, then use matched cost measurements to choose an optimization. Full-language support, the student workflow and board integration remain unfinished.

For the concrete answer to “what would Python look like?”, open the [[PY-E002 - Spatial to Python Syntax Atlas|Spatial-to-Python course syntax atlas]]. It pairs familiar constructs with proposed Python forms and links complete programs from scalar arithmetic through GEMM and convolution. [[60 - Course Syntax and Compiler Trace]] explains the compiler those examples require.

The <a href="presentation/python/index.html" data-router-ignore target="_blank" rel="noopener noreferrer">Spatial in Python presentation</a> explains the fully Python compiler and one earlier Lab 1 success through C++, HLS and RTL in seven slides. Its [[2026-10-22-python-pipeline-presentation|ten-minute outline and full speaker notes]] preserve that meeting's evidence and scope. The newer scalar-batch result is in the checkpoint above; the slides have not been changed for this validation run.

The [[00 - Python Spatial Student Guide|student guide preview]] documents functional software tests and custom final-project tests. The intended default is generated C++ execution from ordinary Python tests; the convenient public runner and case exporter are planned.

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

Validate the prepared explicit scalar interfaces through HLS/RTL before broader IP integration, then compare matched variants before changing storage or scheduling. Continue the [[80 - Initial Compiler Goal|initial goal's remaining obligations]] and use the [[04 - Python Implementation Roadmap|Labs 1–3 progression]] to guide reusable language features.

Python owns source capture, the checked program, the reference engine and C++ generation. The implemented subset has bounded hardware evidence; the full [[D-28|architecture proposal]], checked target planner and broader language remain separate work. The existing specification and independent tests continue to constrain each increment.

## Current state

| Area | Verified state | Remaining work |
|---|---|---|
| Research | Full-language research, five implementation blueprints and bounded readiness probes complete as proposed research | Professor review of D-28 and deliberate semantic choices |
| Python compiler | Bounded source/check/reference and generated-C++ paths implemented; latest local interface checkpoint passed 1,351 tests per source/package route | Full initial-goal acceptance, public check/prepare, resumption and wider language coverage |
| Hardware evidence | Earlier four-kernel/nine-case checkpoint plus the newer 12-project/32-case scalar batch through HLS and RTL | Vendor validation of the new scalar interface, measured optimization, full checked target planning and board integration |
| Student delivery | Student guide and lab-style custom testing approach documented | Convenient generated-C++ runner, compile-once execution and concrete-case export |

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
