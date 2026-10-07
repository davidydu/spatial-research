---
type: reference
title: "Python Spatial — professor discussion brief"
project: spatial-python
date: 2026-10-01
updated: 2026-10-07
---

<a href="https://davidydu.github.io/spatial-research-site/presentation/python/" data-router-ignore target="_blank" rel="noopener noreferrer">Open the six-slide presentation</a> · [[2026-10-01-python-professor-presentation-outline|Full speaker notes and evidence]].

**A Python version of Spatial would include the language frontend, compiler and reference execution engine in Python.** Spatial retains explicit types, memories, control, parallel work, reductions and communication. HLS is already the agreed hardware destination.

The ten-minute talk covers the system, Python feasibility, the implementation plan, tested foundations and next milestones. The professor knows Spatial; the presentation does not walk through a program or explain HLS again.

## Why Python is feasible

The compiler’s main work is representing programs, analyzing structure, checking rules and transforming records. We can implement these data structures and algorithms in Python. Spatial’s arithmetic, memory identities, lifetimes and state-change order remain explicit compiler rules. For example, Python integers can be used to implement fixed-width arithmetic without inheriting arbitrary-precision behavior for Spatial data.

Ordinary Python handles host data and experiments. Kernels use a defined subset that the compiler reads as source without executing decorators, annotations or bodies. [[10 - Source Checker and IR Blueprint]] and [[PY-R016 - Source and Host Workflow Refinement]] specify this boundary.

The practical questions are compilation time, reference execution speed and memory use on useful workloads. The [[PY-R007 - Host Workflow Reproducibility and Validation|workflow study]] defines measurement targets. Component tests and representation experiments do not establish complete-workflow performance. The proposed compiler has no Rust core; team capability is assumed available.

## The shared architecture

One immutable checked representation describes values, types, storage, views, lifetimes, control regions and ordered effects. Source files, generators and imported artifacts reach the same verifier. Helpers and libraries compose the same operations. Some checked conditions may remain declared input requirements or supported runtime guards.

The reference engine executes this model with separate state for each invocation. A transformation creates and checks a new candidate before publication; its behavior must also be validated. Later lowering uses the same accepted meaning. Slide 3 embeds the [[70 - Engineering Architecture Map|Excalidraw map]] with both the overview and detailed module responsibilities. The drawing describes the proposed full system, not completed implementation.

## How we will build the first complete path

The first milestone is a reusable subset of composed memory programs: Int32 data, exact Index values, strict Bool control, typed inputs, SRAM/DRAM views and transfers, runtime shapes, nested loops, branches and helpers. Aliases, initialization, lifetimes and fault order are included. This is an initial portion of S1, not all Spatial or all EE 109 labs.

1. **Finish verification for that subset.** Complete memory, alias, lifetime, initialization and remaining whole-program checks, then publish checked programs.
2. **Connect source and host inputs.** Capture the defined grammar, specialize parameters and lower through shared rules. Validate typed inputs and preserve shared backing identities when preparing a run.
3. **Complete reference execution and the public workflow.** Add invocation-owned memory and ordered execution, diagnostics, the API and saved artifacts. Source, generated programs and imported artifacts must agree.
4. **Test composition and structural change.** Use independent values, effects and fault expectations; exercise an actual region edit and an unfamiliar composition after freezing the compiler.

The [[80 - Initial Compiler Goal|authorized initial goal]], [[40 - Package and Conformance Blueprint|package and conformance blueprint]] and [[30 - State Simulator and HLS Blueprint|execution blueprint]] hold the detailed requirements. Every admitted feature must work through the full path, including errors and artifacts.

## What works today

At committed checkpoint `spatial-py@f8a993b`, **236 component tests pass**. The source suite was rechecked on 7 October. Implemented foundations include immutable records and real use/ownership indices, numeric primitives, input validation and provenance, type/layout rules, scalar normalization and bounded structural checks.

The complete subset verifier, memory checking and execution, source capture and source-to-simulation workflow remain unfinished. Artifacts, actual structural editing, unfamiliar-composition acceptance and complete-workflow measurements also remain open. These are tested compiler components; they do not establish a working complete compiler or hardware support.

The research repository and website connect the contracts, [[D-28|architecture decision]], [[00 - Implementation Design Index|engineering blueprints]] and progress evidence. They let the professor inspect the work beyond the slides.

## What comes next

First complete the memory subset. Then freeze a compiler revision and have an independent author write a structurally unfamiliar valid program. It must use the same compiler rules. A repaired case becomes a regression and acceptance needs a fresh unseen case. A finite suite tests generality; it does not prove every possible combination.

Test a real structural edit as well. References, memory relationships and source information must remain correct, independent expectations must agree, and a failed edit must leave the old program usable. Measure the actual supported capture, checking and execution paths at this milestone.

Next extend whole families: reductions and numeric formats, then additional stateful and communicating constructs. Each family adds source support, checking, reference behavior, diagnostics, artifacts and tests together. The [[04 - Python Implementation Roadmap|roadmap]] owns the dependencies; [[60 - Course Syntax and Compiler Trace|EE 109 patterns]] and the [[PY-E002 - Spatial to Python Syntax Atlas|syntax atlas]] provide coverage targets. The agreed HLS work can begin from a validated subset while the remaining language grows.

**For professor discussion:** does composed memory test enough of Spatial’s core before wider implementation, and which missing capability should follow it? David authorized the bounded initial experiment on 4 October. Adoption of the full architecture and its proposed semantic changes remains separate.

## Useful links

[[00 - Python Rewrite Index|Research home]] · [[01 - Python Coverage Ledger|Coverage ledger]] · [[07 - Python Implementation Readiness Audit|Readiness review]] · [[11 - Design Refinement Iterations|Design refinement]] · [[02 - Python Research Review Log|Review findings]] · [[80 - Initial Compiler Goal|Current implementation and acceptance]]

[Research repository](https://github.com/davidydu/spatial-research) · [Documentation website](https://davidydu.github.io/spatial-research-site/) · [Website repository](https://github.com/davidydu/spatial-research-site) · [Implementation repository](https://github.com/davidydu/spatial-py/tree/work/initial-reference) (requires repository access)
