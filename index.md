---
type: moc
title: "Spatial Research"
date: 2026-09-30
---

Research toward a pure Python rewrite of Spatial. First establish the programming model and its meaning; then investigate lowering to HLS. This site connects that work to the original source, experiments, and specification.

> [!important] Current direction — professor feedback, 30 September 2026
> **Pure Python Spatial, including the compiler.** First work out what Spatial programs and their implementation look like in Python, then study HLS lowering. This replaces the earlier Python-frontend/Rust-core proposal. See [[2026-09-30-pure-python-programming-model|the new research direction and first program sketch]].

## Start with the Python rewrite

[[2026-09-30-pure-python-programming-model|Programming model first]] records the feedback, a proposed tiled-scale example, source-capture and builder alternatives, and the next research steps. The direction is agreed; the detailed Python API and implementation design are still open.

The <a href="presentation/index.html" data-router-ignore target="_blank" rel="noopener noreferrer">28 September presentation</a> and [[2026-09-28-spatial-professor-presentation-outline|speaking outline]] are historical. Their Rust-core recommendation was superseded by the professor's feedback.

## Earlier research and evidence

| Read | Purpose |
|---|---|
| [[D-26-professor-brief\|Earlier professor brief]] | The superseded recommendation and the evidence presented |
| [[D-26-final-architecture\|Earlier architecture proposal]] | Historical Rust-core design, retained for the research record |
| [[2026-09-28-d26-research-extension\|Research method and debate]] | Why the recommendation changed; competing case; measured versus inferred conclusions |
| [[D-26-12-simulator-spike\|Matched interpreter experiment]] | Exact-output checks, runtime measurements, independent repeat and reproducibility archive |
| [[D-26\|Original D-26 protocol and meeting cut]] | Frozen hypotheses, mistake list, historical recommendation and audit trail |

## What we will study next

Start with three small programs: tiled scale, a scalar reduction, and a runtime branch with state. Use them to explain memory, control, numeric behavior, and mutation in Python. Compare reading kernel source with constructing programs through an explicit Python library.

The compiler's checks, program representation, and functional simulation should be Python. Once those have a clear design, study how the represented operations lower to HLS. The existing specification and tests are evidence to review and reuse, not a reason to retain Rust as the implementation language.

## Current state

| Area | Verified state | Remaining work |
|---|---|---|
| Research | Earlier D-26 studies retained; professor's pure Python direction recorded | Review representative Python programs and settle the programming model |
| Prototype compiler | Existing Rust prototype retained as a historical reference | Design the Python compiler, checker, program representation, and simulator |
| Hardware evidence | Historical 39-program backend corpus: 37 fit, 2 over budget, 14 initiation-interval caveats | Fresh evidence for changed HLS and the general backend before release |
| Student delivery | Earlier host and packaging studies available for reference | Decide the Python workflow after reviewing examples; no new package is implemented |

See [[2026-06-27-rust-spatial-rewrite-roadmap|Historical Rust roadmap and backend evidence]], [[D-26-05-boundary-design|Earlier boundary study]], and [[progress-log|Verification history]]. Historical vendor results do not certify the future Python compiler.

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
