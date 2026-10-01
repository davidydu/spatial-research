---
type: moc
title: "Python Spatial research"
project: spatial-python
date_started: 2026-09-30
---

Research before implementation: establish what Spatial programs mean in Python, decide how the compiler represents and checks them, then study HLS lowering.

**Current phase:** language foundations reviewed; full-language architecture research underway. Pure Python is the agreed direction. Source capture is the current research recommendation for writing kernels, with a shared builder interface for generators. Detailed proposals remain subject to review and professor approval. No Python compiler implementation is claimed.

## Read first

1. [[D-27|Direction and authority]] — what the professor and David have settled.
2. [[01 - Python Research Plan|Research plan]] — study order, review criteria, and documentation rules.
3. [[PY-R001 - Programming Model Study|Current study]] — compare source capture and an explicit builder on the same programs.
4. [[PY-E001 - Initial Example Corpus|Example corpus]] — original sources, expected behavior, and cases that can distinguish designs.
5. [[02 - Python Open Questions|Open questions]] — unresolved choices and the evidence needed to resolve them.

[[03 - Managed Research Execution|Managed research execution]] tracks the full research package, parallel work, and completion criteria while David is away.

## Foundation studies

- [[PY-R002 - Numeric and Reduction Semantics]] — exact arithmetic, literals, reductions, folds, and disagreements in the original implementation.
- [[PY-R003 - Control Memory and Effects]] — operation order, lazy branches, state lifetime, aliases, and the need for communicating tasks.
- [[PY-R004 - Capture Composition and Diagnostics]] — source versus builder, reusable kernels, notebook/file capture, and matched errors.

## Documentation structure

| Location | What belongs here |
|---|---|
| `10 - Research/` | Questions, source readings, alternatives, experiments, limitations, and proposed conclusions |
| `20 - Examples/` | Shared example cases: source programs, intended behavior, expected outputs and effects; competing Python forms stay in the linked studies |
| Shared `20 - Research Notes/50 - Decision Records/` | Adopted choices and rejected alternatives; continue the existing D-number sequence |
| `40 - Specification/` — create when needed | Proposed Python language/compiler contracts for review, then adopted contracts with explicit authority |
| `50 - HLS Lowering/` — create when research begins | Later research connecting the Python program model to HLS |
| `60 - Validation/` | How claims will be checked; later, reproducible results and their limits |

[[00 - Python Validation Plan|Validation plan]] · [[01 - Python Coverage Ledger|Full-scope coverage ledger]] · [[02 - Python Research Review Log|Source checks and reviews]]

**Specification status:** no detailed Python language or compiler contract has been adopted. **HLS status:** deferred until the programming model is reviewed. Create these directories with their first substantive topic pages; do not populate placeholder specifications.

## How the earlier work fits

- `10 - Spec/` documents original Spatial. It is source evidence for this rewrite, not automatically the Python contract.
- `20 - Research Notes/` keeps the earlier research and the dated [[2026-09-30-pure-python-programming-model|direction]] and [[2026-09-30-pure-python-feasibility|feasibility]] notes. Their existing URLs remain valid.
- `30 - HLS Mapping/` contains earlier backend research. Recheck it against the eventual Python contract before adopting it.
- `35 - Python Surface Mapping/` contains the D-26 comparisons against the earlier external DSL. Use their findings and examples while reviewing any inherited Rust-specific policies.
- The frozen D-26 record, earlier decisions, presentation, and Rust prototype remain historical artifacts. New Python studies, examples, and questions use `PY-` identifiers; decisions continue in the shared D-number sequence with an explicit scope.

The vault is the source of truth; the website renders the same files. Progress stays in [[progress-log]]. Research conclusions must be traceable to inspected sources or recorded experiments; a subagent's opinion is not evidence by itself.
