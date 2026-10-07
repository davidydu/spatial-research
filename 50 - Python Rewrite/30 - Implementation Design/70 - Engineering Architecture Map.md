---
type: design
title: "Python Spatial engineering architecture map"
project: spatial-python
date: 2026-10-03
status: proposed
adoption_status: proposed
implementation_status: foundations-in-progress
updated: 2026-10-07
---

# Python Spatial engineering architecture map

One checked Spatial program is the center of the design. The Python reference simulator runs its meaning. The hardware planner assigns storage, scheduling, arithmetic realizations and interfaces while preserving that meaning. Both paths use the same compiler-owned immutable Python records.

[Download the editable Excalidraw canvas](<50 - Python Rewrite/30 - Implementation Design/assets/python-spatial-engineering-architecture.excalidraw>) · [Open the full vector diagram](<50 - Python Rewrite/30 - Implementation Design/assets/python-spatial-engineering-architecture.svg>) · [Download the full PNG](<50 - Python Rewrite/30 - Implementation Design/assets/python-spatial-engineering-architecture.png>)

Open the `.excalidraw` file in Excalidraw to pan, zoom and edit every element. The SVG stays sharp at any zoom. The top strip gives the professor the big picture; the rest of the canvas provides the engineering detail.

![Overview of the proposed Python Spatial architecture](<50 - Python Rewrite/30 - Implementation Design/assets/python-spatial-engineering-overview.png>)

## Read the map at three scales

| View | What to discuss |
|---|---|
| Top strip | Captured Python source becomes one checked program. Reference execution and hardware planning branch from it. Python owns the language rules throughout. |
| Middle, sections 01–04 | How source, generated programs and imported artifacts reach the checker; what records contain; how rewrites publish a new revision; where mutable execution state lives; how a target plan reaches HLS. |
| Bottom, sections 05–06 | The numeric, protocol, artifact and validation rules shared by those modules, followed by the EE109 patterns that drive implementation. |

Blue marks owned program meaning, green marks reference execution and results, amber marks verification, and dashed paths mark later or optional work. Colors do not mean that a component is implemented. The six source labels at the bottom are clickable in Excalidraw and the SVG.

## Boundaries that guide implementation

**Source is data.** Ordinary host Python prepares inputs and calls the public API. Captured kernels are parsed from a frozen source bundle; their bodies, decorators and annotations are not executed to discover the program. The scalar kernel on the map assumes the proposed fixed Spatial prelude. Generated programs and imported artifacts also enter as untrusted candidates.

**Only the checker publishes accepted meaning.** `CheckedProgram` wraps an immutable semantic root and an exact revision identity. Semantic records describe values, regions, resources, effects, requirements and origins. Requirements record whether they are proved, invocation preconditions or supported runtime guards; reference validity alone does not establish target eligibility. Indices, analysis facts and derived execution programs live in revision-bound side tables. A rewrite makes a candidate, remaps owned identities and references, and verifies it before publication. Failure retains the old revision.

**An invocation owns execution state.** Preparing a run checks bindings, shapes and aliases. Shared views preserve their common backing identity. Frames, requests, memory contents, queue state and RNG state belong to that invocation; they do not mutate the checked program. The run snippet checks preparation failure and shows a separate tiled-output example. The simulator preserves each task's effect order and schedules resumable continuations. Only `Completed` exposes complete outputs; other outcomes follow the exact diagnostic and continuation rules in the package blueprint.

**Hardware needs a checked plan.** Plan records add finite storage, scheduling, numeric realizations, interfaces and target obligations. Python plan execution is the S6 validation path for checking behavior against the semantic program. It does not imply that every `plan(...)` call runs exhaustive tests, or that a simulation proves all inputs correct. `plan(...)` returns an eligible checked `ImplementationPlan` only after its required checks; failed or unknown required target obligations block emission. Rejected candidates remain inspectable. Vendor simulation, synthesis and measured hardware results supply separate evidence. xDSL may be introduced as an adapter for a measured backend benefit; it does not own the canonical program.

The directory labels on the canvas are proposed module responsibilities from [[40 - Package and Conformance Blueprint]]. The CLI projects the same public API and diagnostics; it is not a second compiler path.

## Current implementation checkpoint

The map describes the proposed architecture, not completed components. As of 7 October, the initial implementation has committed records, numeric rules and several checking stages, with 236 passing component tests at `f8a993b`. The full verifier, memory rules, source-to-simulation workflow and unfamiliar-composition acceptance are still ahead. [[80 - Initial Compiler Goal]] records the evidence and remaining work. The [[2026-10-01-python-professor-presentation-outline|professor presentation]] embeds this map with section navigation and zoom.

## Start with the first complete path

The first implementation target is S0→S1: scalar ports and tiled SRAM/DRAM programs through capture, specialization, checking, preparation and reference simulation. Acceptance includes independently expected outputs and effects, invalid-program diagnostics, source/builder/import agreement, and the REP-EDIT rewrite fixture. This is the first slice of Lab 1, not a claim of full Lab 1 coverage.

Then add ordered FIFO and scalar reductions/folds; Lab 2 memory reductions, FSMs and LUTs; exact fixed-point GEMM; and Lab 3 line history and windows. The diagram groups features by the lab patterns they enable. The roadmap owns stage dependencies and acceptance gates. Lab 3 must keep the current guide and older public fixture profiles distinct, including signed gradients, row publication and warm-up behavior.

A scoped S6→S7 hardware track can start for accepted S1 programs while later language families grow. The lab subset does not need all floating-point/math profiles or communicating tasks before that work begins. The complete rewrite still retains those later capabilities.

## Documents behind the drawing

| Map label / detail | Owning document |
|---|---|
| A — source, trust boundary, records and safe edits | [[10 - Source Checker and IR Blueprint]] |
| B — modules, public API, outcomes, saved artifacts and conformance | [[40 - Package and Conformance Blueprint]] |
| C — invocation state, plan records, reference execution and hardware | [[30 - State Simulator and HLS Blueprint]] |
| D — proposed architecture and adoption boundary | [[D-28]] |
| E — S0–S9, REP-S1, REP-EDIT and scoped hardware gates | [[04 - Python Implementation Roadmap]] |
| F — immutable records and the optional xDSL adapter | [[PY-R017 - Compiler Representation Comparison]] |
| Shared numeric rules | [[20 - Numeric Engine Blueprint]], [[PY-R015 - Numeric Status Repair and Independent Oracles]] |
| Lab patterns and exact syntax | [[PY-R012 - Lab1 Syntax and Host Mapping]], [[PY-R013 - Controllers Reductions and Lab2 Mapping]], [[PY-R014 - Convolution Windows and Lab3 Mapping]], [[60 - Course Syntax and Compiler Trace]] |

This map presents the current proposal for review. The linked contracts and blueprints own the complete rules. Professor adoption, compiler implementation and target validation remain separate milestones.
