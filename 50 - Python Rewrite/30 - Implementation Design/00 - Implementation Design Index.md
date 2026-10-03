---
type: moc
title: "Python Spatial implementation design"
project: spatial-python
date: 2026-10-01
status: proposed
adoption_status: proposed
implementation_status: not-implemented
---

The studies explain the choices. The contracts say what a program means. These blueprints say how to build the compiler that enforces those contracts.

The full path is captured Python source → checked Spatial program → Python reference simulation or a checked hardware plan → HLS and interface components. Python owns the language rules throughout. xDSL supplies Python compiler infrastructure. No Python compiler or Python-generated hardware result is claimed yet.

## Read by responsibility

| Blueprint | What an implementer gets |
|---|---|
| [[10 - Source Checker and IR Blueprint|Source, checker and IR]] | Accepted syntax, names and types, component signatures, graph records, effects, verifier algorithms and pass rules |
| [[20 - Numeric Engine Blueprint|Numeric engine]] | Exact fixed/float algorithms, math recipes and equality cases, certificates, reductions, RNG state and finite hardware methods |
| [[30 - State Simulator and HLS Blueprint|State, simulator and HLS]] | Resumable tasks, fair arbitration, cancellation and cleanup, memory/allocation plans, interface records and lowering routes |
| [[40 - Package and Conformance Blueprint|Package and validation]] | Modules, public APIs, dependency pins, saved program formats, buffers, diagnostics, fixtures and the first implementation steps |
| [[50 - Library and Migration Recipes|Libraries and migration]] | Named library operations expanded into ordinary checked templates, with explicit shapes, arithmetic order and legacy differences |

Start with the package API and source/checker design, then implement the first complete kernel path in [[04 - Python Implementation Roadmap]]. Numeric and state work extend that same path. Hardware planning can begin once the first semantic path is checked and independently tested; it need not wait for the whole library.

The course-based supplement [[60 - Course Syntax and Compiler Trace]] supplies exact common operation signatures, a tile/GEMM/convolution trace and schedule-request records. Read it beside [[PY-E002 - Spatial to Python Syntax Atlas]]. It refines the five blueprint responsibilities above and records gaps exposed by writing complete programs.

## Evidence and status

[[09 - Fable Design Review]] is the latest cross-design review. Read its confirmed numeric erratum and binding/API follow-ups before using these blueprints as implementation instructions. Optional reviewer proposals have not been adopted.

[[07 - Python Implementation Readiness Audit]] records the gaps found, review discussion, experiments, repairs and remaining execution gates. [[01 - Python Coverage Ledger]] preserves all 106 original spec documents and their 18 family destinations. It links into this design without treating a document count as implemented feature coverage.

These are proposed designs for professor review. Adoption, a working reference compiler, a working target backend, and measured hardware results are separate milestones. Research experiments test individual methods; they do not complete those milestones.
