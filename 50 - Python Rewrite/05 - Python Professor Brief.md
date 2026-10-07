---
type: reference
title: "Python Spatial — professor discussion brief"
project: spatial-python
date: 2026-10-01
updated: 2026-10-07
---

<a href="https://davidydu.github.io/spatial-research-site/presentation/python/" data-router-ignore target="_blank" rel="noopener noreferrer">Open the six-slide architecture presentation</a> · [[2026-10-01-python-professor-presentation-outline|Full speaker notes and evidence]].

**What would a Python version of Spatial look like?** A language expressed through Python, a compiler written in Python, and a Python reference engine for Spatial’s behavior. A later backend builds a hardware plan and emits HLS C++.

The ten-minute presentation answers that system-design question. The professor knows Spatial; program examples, implementation progress and the documentation repositories are supporting material.

## What stays, and what changes

Spatial retains explicit types, memories, controllers, parallel work, reductions and communication. Python replaces the implementation of source handling, program representation, checking, transformations and reference execution. Ordinary Python supplies the host environment for files, data and experiments. The proposed compiler has no Rust core.

## The language boundary

Host Python prepares experiments. Kernel source uses a defined Python subset with Spatial’s numeric, memory and control rules. The compiler reads that source without executing its decorators, annotations or body. Source, dependencies and chosen meta parameters are fixed for compilation; actual inputs and supported runtime dimensions belong to a run.

This gives the compiler the program’s retained structure before execution. General Python libraries remain host-side unless their operations are explicitly admitted to the kernel language. [[10 - Source Checker and IR Blueprint]] and [[PY-R016 - Source and Host Workflow Refinement]] specify the boundary.

## The compiler’s central object

One immutable checked representation describes typed values, operations, control regions, storage identities, views, lifetimes and ordered effects. Written source, generated programs and imported artifacts reach the same verifier. Helpers and libraries compose the same operations, so their behavior does not depend on a separate compiler path.

A transformation creates a candidate and checks it before publication. Simulation and hardware planning use the accepted program. Python owns these records and language rules; an optional framework adapter may serve a particular backend without becoming a second authority.

Slide 3 embeds the [[70 - Engineering Architecture Map|Excalidraw architecture map]]. Its overview shows the whole system; the full canvas connects that view to module responsibilities. Its colors identify responsibilities, not implementation progress.

## Reference execution

The program and each run’s state are separate. One checked program can serve several invocations, each with its inputs, memory contents, active control and pending operations. Shared views retain their common backing. Persistent state, when requested, belongs to an explicit session.

The Python reference engine executes Spatial’s rules for values, memory, selected branches and effects. Completion, faults and suspended runs have distinct outcomes. This behavior provides a reference for transformations and hardware plans; it does not predict hardware cycle timing. [[30 - State Simulator and HLS Blueprint]] and [[40 - Package and Conformance Blueprint]] define these responsibilities.

## The later HLS path

The planner adds storage and banking, work mapping, scheduling constraints, interfaces and numeric realizations. It checks the resulting implementation plan before the backend emits HLS C++ and required interfaces. Plan execution in Python and vendor validation supply separate evidence.

**Reference validity differs from target eligibility.** A checked program may retain declared input conditions and supported runtime guards. A hardware plan must also satisfy the target’s required obligations; unknown required facts block emission. Runtime loops can have variable iteration counts while simultaneous hardware state and storage remain bounded.

HLS can begin for an accepted subset while later language families grow. Compiler throughput and hardware correctness, resources and timing still need measurement. The [[04 - Python Implementation Roadmap|roadmap]] records the staged gates.

## The design to review

The recommendation in [[D-28]] combines source capture, Python-owned immutable program records, one checking boundary, invocation-owned execution state and explicit hardware plans. The meeting should assess whether those boundaries capture the Python Spatial we want to build.

Where legacy implementations disagree, the proposed behavior changes remain explicit decisions for review. The pure Python direction is accepted; professor adoption of the detailed architecture and its semantic changes remains separate.

## Supporting evidence, if useful

The [[00 - Implementation Design Index|implementation blueprints]], [[11 - Design Refinement Iterations|design reviews]] and [[01 - Python Coverage Ledger|language coverage ledger]] hold the research behind the proposal. The [[PY-E002 - Spatial to Python Syntax Atlas|syntax atlas]] and [[60 - Course Syntax and Compiler Trace|EE 109 mapping]] show proposed source examples; the main presentation does not walk through them.

David authorized the [[80 - Initial Compiler Goal|initial implementation experiment]] on 4 October. The committed `spatial-py@f8a993b` foundations pass 236 component tests. The complete verifier, memory checking and execution, source-to-simulation workflow and unfamiliar-composition acceptance gate remain unfinished. No Python-generated HLS, RTL or hardware result is claimed.

The initial experiment tests a reusable subset of composed memory programs. After a compiler revision is frozen, an independently written unfamiliar program must work through the same language rules. A repaired case becomes a regression; acceptance then needs a fresh unseen case. This supplements independent expected values, effects, faults and structural-edit checks.

## Useful links

[[00 - Python Rewrite Index|Research home]] · [[07 - Python Implementation Readiness Audit|Readiness review]] · [[02 - Python Research Review Log|Review findings]] · [[70 - Engineering Architecture Map|Engineering map]] · [[D-28|Architecture decision]] · [[80 - Initial Compiler Goal|Current implementation and acceptance]]

[Research repository](https://github.com/davidydu/spatial-research) · [Documentation website](https://davidydu.github.io/spatial-research-site/) · [Website repository](https://github.com/davidydu/spatial-research-site) · [Implementation repository](https://github.com/davidydu/spatial-py/tree/work/initial-reference) (requires repository access)
