---
type: moc
title: "Python Spatial research"
project: spatial-python
date_started: 2026-09-30
---

Research before implementation: establish what Spatial programs mean in Python, decide how the compiler represents and checks them, then study HLS lowering.

**Current phase:** full-language architecture research and the [[07 - Python Implementation Readiness Audit|implementation-readiness review]] are complete as proposed research. [[00 - Implementation Design Index]] now supplies concrete algorithms, interfaces and acceptance cases for every family. Pure Python is the agreed direction. The proposed architecture uses captured kernels, Python-owned semantics and simulation, custom Spatial dialects on xDSL, and a checked HLS backend. [[D-28]] records the recommendation for professor review. No Python compiler implementation is claimed.

## Read first

<a href="presentation/python/index.html" data-router-ignore target="_blank" rel="noopener noreferrer">Open Spatial in Python — seven-slide presentation</a> · [[2026-10-01-python-professor-presentation-outline|Ten-minute outline and full speaker notes]]. The presentation explains the proposed program and compiler path; it is not an implementation demonstration.

1. [[D-27|Direction and authority]] — what the professor and David have settled.
2. [[05 - Python Professor Brief|Professor brief]] — the proposal, progress, main tradeoff, and approval boundary.
3. [[D-28|Architecture recommendation]] — selected design, alternatives, and reversal conditions.
4. [[00 - Implementation Design Index|Implementation design]] — concrete algorithms, interfaces, libraries, and independent acceptance cases.
5. [[04 - Python Implementation Roadmap|Implementation sequence]] — complete vertical paths, dependencies, and evidence gates after approval.
6. [[02 - Python Open Questions|Question register]] — research answers, adoption status, and remaining evidence.

[[03 - Managed Research Execution|Managed research execution]] records the completed research package, parallel work, and completion evidence.

[[01 - Python Research Plan|Research method]] · [[PY-R001 - Programming Model Study|Paired Python programs]] · [[PY-E001 - Initial Example Corpus|Shared example cases]]

## Foundation studies

- [[PY-R002 - Numeric and Reduction Semantics]] — exact arithmetic, literals, reductions, folds, and disagreements in the original implementation.
- [[PY-R003 - Control Memory and Effects]] — operation order, lazy branches, state lifetime, aliases, and the need for communicating tasks.
- [[PY-R004 - Capture Composition and Diagnostics]] — source versus builder, reusable kernels, notebook/file capture, and matched errors.

## Full language and compiler

- [[PY-R005 - Full Language Coverage and Migration]] — 18 language/infrastructure families and their migration and acceptance gates.
- [[PY-R006 - Compiler Architecture and Framework Choice]] — representations, xDSL comparison/probes, semantic ownership, and pass invariants.
- [[PY-R007 - Host Workflow Reproducibility and Validation]] — input preparation, packaging, artifact identity, diagnostics, and measured-workload targets.
- [[PY-R008 - Advanced State and Communication Protocols]] — queues, locks, windows, streams, transfers, FSMs, and cancellation.

## Proposed contracts

[[10 - Python Language Contract|Language and capture]] · [[20 - Python Numeric Contract|Numbers and reductions]] · [[30 - Python State and Protocol Contract|State and communication]] · [[40 - Python Compiler and HLS Contract|Compiler and HLS boundary]]

These distill the studies for review. Document review, design adoption, and implemented support have separate status fields.

## HLS studies

- [[PY-R009 - HLS Boundary and Control Lowering]] — compiler/vendor responsibilities, control routes, faults, ABI, and evidence levels.
- [[PY-R010 - Memory Scheduling and Design Space Exploration]] — physical memory, transfers, banking, scheduling, and legal tuning.
- [[PY-R011 - Numeric Lowering and Intrinsic Profiles]] — numeric profiles, random/math operations, and vendor primitive compatibility.

## Documentation structure

| Location | What belongs here |
|---|---|
| `10 - Research/` | Questions, source readings, alternatives, experiments, limitations, and proposed conclusions |
| `20 - Examples/` | Shared example cases: source programs, intended behavior, expected outputs and effects; competing Python forms stay in the linked studies |
| Shared `20 - Research Notes/50 - Decision Records/` | Proposed and adopted choices with authority, alternatives, and reversal conditions; continue the existing D-number sequence |
| `30 - Implementation Design/` | Concrete algorithms, records, APIs, module ownership, library recipes, and implementation acceptance cases |
| `40 - Specification/` | Proposed Python language/compiler contracts for review, then adopted contracts with explicit authority |
| `50 - HLS Lowering/` | Mapping the checked Python program to hardware plans, HLS, and target validation |
| `60 - Validation/` | How claims will be checked; later, reproducible results and their limits |

[[00 - Python Validation Plan|Validation plan]] · [[01 - Python Coverage Ledger|Full-scope coverage ledger]] · [[02 - Python Research Review Log|Source checks and reviews]]

[[03 - Independent Architecture Review|Architecture review]] · [[04 - Independent Numeric Review|Numeric review]] · [[05 - Independent Protocol and HLS Review|Protocol/HLS review]] · [[06 - Python Research Completion Audit|Requirement-by-requirement audit]]

**Specification status:** proposed contracts; no detailed contract adopted. **HLS status:** research mappings and target gates; no Python-generated vendor run. Create new topic pages for substantive work, and link evidence rather than copying status claims between pages.

## How the earlier work fits

- `10 - Spec/` documents original Spatial. It is source evidence for this rewrite, not automatically the Python contract.
- `20 - Research Notes/` keeps the earlier research and the dated [[2026-09-30-pure-python-programming-model|direction]] and [[2026-09-30-pure-python-feasibility|feasibility]] notes. Their existing URLs remain valid.
- `30 - HLS Mapping/` contains earlier backend research. Recheck it against the eventual Python contract before adopting it.
- `35 - Python Surface Mapping/` contains the D-26 comparisons against the earlier external DSL. Use their findings and examples while reviewing any inherited Rust-specific policies.
- The frozen D-26 record, earlier decisions, presentation, and Rust prototype remain historical artifacts. New Python studies, examples, and questions use `PY-` identifiers; decisions continue in the shared D-number sequence with an explicit scope.

The vault is the source of truth; the website renders the same files. Progress stays in [[progress-log]]. Research conclusions must be traceable to inspected sources or recorded experiments; a subagent's opinion is not evidence by itself.
