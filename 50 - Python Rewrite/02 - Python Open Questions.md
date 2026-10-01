---
type: open-questions
title: "Python Spatial open questions"
project: spatial-python
date_started: 2026-09-30
---

These questions belong to the Python rewrite. The original [[20 - Open Questions]] remains source-research evidence; [[40 - Decision Queue]] is the shared register for earlier and current decisions. Resolved questions stay here with their decision and date; identifiers are never reused.

| ID | Question | Evidence needed | Status |
|---|---|---|---|
| PY-Q001 | Source-captured kernel syntax or an explicit Python builder? | The same three complete programs under both approaches, including capture/runtime behavior and diagnostic locations | Source-first recommendation under review; [[PY-R001 - Programming Model Study]], [[PY-R004 - Capture Composition and Diagnostics]] |
| PY-Q002 | Which original Spatial behaviors are preserved, revised, or excluded? | A source-grounded semantic inventory; explicit treatment of simulation/backend disagreements and previous Rust redesigns | Open; Phase 2 |
| PY-Q003 | What do integers, fixed-point values, literals, and reduction order mean? | Exact boundary examples and an independent arithmetic reference; identify conversion and normalization points | Proposed contract; [[PY-R002 - Numeric and Reduction Semantics]] |
| PY-Q004 | How do names, state writes, memory aliases, and consuming FIFO operations behave? | Branch/effect examples, lexical visibility, operation order, initialization, and error policy | Foundation proposal; advanced protocols still in research; [[PY-R003 - Control Memory and Effects]] |
| PY-Q005 | Which program objects and checks should the Python compiler own? | Candidate representations that explain all initial examples without recognizing whole-program families | Open; Phase 3 |
| PY-Q006 | How should files and notebook cells reach the compiler, and how are errors reported? | Source capture contract, original locations, explicit host/capture/runtime distinction, and repair examples | Capture/diagnostic proposal; host packaging still in research; [[PY-R004 - Capture Composition and Diagnostics]] |
| PY-Q007 | What feedback time is acceptable for simulation and compiler runs? | Representative workload sizes and user-facing latency targets fixed before performance measurements | Open; validation design |
| PY-Q008 | Which hardware semantics can the later HLS backend preserve? | Per-operation lowering and behavioral checks after the Python programming model is reviewed | Deferred to Phase 4 |
| PY-Q009 | How does the full original language fit the rewrite, beyond the three examples? | Complete source-spec crosswalk, source-family gap check, and a staged path for every intended capability | Open; full-scope research |
| PY-Q010 | Which compiler framework and dependencies should we choose? | Compare custom Python structures and Python-native frameworks against semantic ownership, effects, diagnostics, and HLS requirements | Open; Phase 3 |
| PY-Q011 | What are the host API, package, reproducibility, and migration contracts? | End-to-end user workflows, immutable inputs and artifacts, provenance, and compatibility policy | Open; Phase 3 |
| PY-Q012 | How should banking, scheduling, optimization, and design-space exploration divide between Spatial and HLS? | Legality versus optimization responsibilities, preserved directives, analysis boundaries, and report-based validation | Open; Phases 3–4 |

## Resolved direction

The compiler implementation language and research order are settled by [[D-27]]. The open questions above do not reopen that choice. Neither a preferred sketch nor a drafted specification resolves an entry automatically.
