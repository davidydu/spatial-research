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

The full path is captured Python source → checked Spatial program → Python reference simulation or a checked hardware plan → HLS and interface components. Python owns the language rules throughout. Immutable compiler-owned records carry checked meaning and target plans. xDSL is an optional derived adapter when a named pipeline demonstrates value. No Python compiler or Python-generated hardware result is claimed yet.

[[70 - Engineering Architecture Map|Open the engineering architecture map]] for an editable Excalidraw view of the whole path, module contracts, state ownership, verification gates and EE109 implementation stages.

**Active work, 4 October:** [[80 - Initial Compiler Goal]] records David's authorization for the first composed-memory reference implementation, its frozen scope and evidence gates. It does not record adoption of the full architecture or completion of S1.

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

[[11 - Design Refinement Iterations]] records the current proposed refinements and their checks. The earlier [[09 - Fable Design Review]] is preserved as the starting critique; its numeric erratum is repaired by R015, and R016–018 record source/host, representation and protocol decisions. Professor adoption remains pending.

[[07 - Python Implementation Readiness Audit]] records the gaps found, review discussion, experiments, repairs and remaining execution gates. [[01 - Python Coverage Ledger]] preserves all 106 original spec documents and their 18 family destinations. It links into this design without treating a document count as implemented feature coverage.

These are proposed designs for professor review. Adoption, a working reference compiler, a working target backend, and measured hardware results are separate milestones. Research experiments test individual methods; they do not complete those milestones.
