---
type: open-questions
title: "Python Spatial open questions"
project: spatial-python
date_started: 2026-09-30
---

These questions belong to the Python rewrite. The original [[20 - Open Questions]] remains source-research evidence; [[40 - Decision Queue]] is the shared register for earlier and current decisions. Resolved questions stay here with their decision and date; identifiers are never reused.

| ID | Question | Proposed research answer | Status/evidence |
|---|---|---|---|
| PY-Q001 | Source-captured kernel syntax or an explicit Python builder? | Source-first; builder for generators/tooling, one unchecked model and checker. Raw-source acquisition is a separate initial workflow choice | Proposed in [[D-28]]; [[PY-R001 - Programming Model Study]], [[PY-R004 - Capture Composition and Diagnostics]] |
| PY-Q002 | Which original behaviors are preserved, revised, or excluded? | Preserve language responsibilities, explicitly revise inconsistent semantics, replace old compiler/runtime mechanisms, name legacy backend exclusions | Proposed crosswalk; [[PY-R005 - Full Language Coverage and Migration]], [[01 - Python Coverage Ledger]] |
| PY-Q003 | What do numbers, literals, conversions, random/math operations, and reductions mean? | Exact typed bits and per-operation normalization; strict default and named profiles; ordered fold/lawful reduce/fixed tree remain distinct | Proposed; [[20 - Python Numeric Contract]], R002/R011 studies |
| PY-Q004 | How do state, aliases, effects, and communication behave? | Backing identities and lifetimes; ordered effects plus bounded communicating tasks; explicit stop/drain/cancel and allowed traces/progress | Proposed; [[30 - Python State and Protocol Contract]], R003/R008 studies |
| PY-Q005 | Which program objects and checks should the compiler own? | Immutable source/unchecked records, private checked semantic and implementation dialects, Spatial verifier, per-pass invariants and invalidation | Proposed; [[PY-R006 - Compiler Architecture and Framework Choice]] |
| PY-Q006 | How do files/cells and errors reach the compiler? | Immutable text/origin bundles, explicit frozen meta/dependencies, raw-cell/file adapters, structured phase/code/spans/repairs | Proposed; [[10 - Python Language Contract]], R004/R007 studies |
| PY-Q007 | What feedback time is acceptable? | Predeclared workload/latency/memory targets with warm/cold and repeated measurements; profile misses before changing architecture | Targets proposed, compiler measurements unrun; [[PY-R007 - Host Workflow Reproducibility and Validation]] |
| PY-Q008 | Which hardware semantics can HLS preserve? | Per-family checked routes, numeric adapters, memory/protocol plans, explicit target capability rejection; safety and progress obligations | Research mappings proposed, vendor evidence unrun; [[PY-R009 - HLS Boundary and Control Lowering]], R010/R011 |
| PY-Q009 | How does the full language fit beyond three examples? | All 106 original-spec documents mapped to 18 substantive families; exact 124-path source baseline and G01–G18 gates | Research accounting checked; [[PY-R005 - Full Language Coverage and Migration]], [[01 - Python Coverage Ledger]] |
| PY-Q010 | Which framework/dependencies should we use? | Spatial dialects on xDSL, Python-owned semantics and private snapshots; custom IR reversal option; optional native adapters | Proposed with bounded framework probes; [[PY-R006 - Compiler Architecture and Framework Choice]] |
| PY-Q011 | What are the host, package, reproducibility, and migration contracts? | Ordinary Python host work; typed alias-preserving snapshots/sessions; canonical identities; versioned model registry and explicit migration | Proposed; [[PY-R007 - Host Workflow Reproducibility and Validation]], R005/R006 |
| PY-Q012 | How do banking, scheduling, and DSE divide between Spatial and HLS? | Spatial verifies layout/order/protocol and hard constraints; HLS realizes and reports. DSE rechecks candidates and preserves semantic capacities/admission | Proposed; [[PY-R010 - Memory Scheduling and Design Space Exploration]] |

## Resolved direction

The compiler implementation language and research order are settled by [[D-27]]. The open questions above do not reopen that choice. The table now records concrete research answers. They remain proposed under [[D-28]] until professor review; adoption and executable support are separate decisions. Target version/device selection and the unrun conformance/performance/vendor gates are implementation evidence obligations, not hidden completed results.
