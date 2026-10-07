---
type: presentation-outline
title: "Python Spatial — professor presentation and script"
project: spatial-python
date: 2026-10-01
updated: 2026-10-07
status: meeting-ready
scope: "Six slides on the Python system, feasibility, implementation plan and next milestones"
---

# Python Spatial: system, feasibility and implementation plan

[Open the presentation](https://davidydu.github.io/spatial-research-site/presentation/python/). Six slides, about ten minutes before discussion. Press **N** for the current script, **E** for its sources, and the arrow keys to move. Slide 3 embeds the Excalidraw overview; **Explore engineering map** opens section navigation, zoom, panning and the editable source.

The professor knows Spatial, and HLS is already the agreed destination. This talk answers what a Python version of Spatial looks like, why it is feasible, how we will build it, what is implemented, and what we should validate next. It does not walk through a Spatial program or explain HLS again.

David authorized the initial composed-memory experiment on 4 October. The detailed architecture and semantic changes in [[D-28]], and expansion beyond the bounded initial goal, remain for review. The 236 component tests are scoped implementation evidence; they do not establish a working complete compiler.

## Story and timing

| Slide | Headline | Navigation label | Time | Elapsed |
|---|---|---|---|---|
| 1 | What does a Python version of Spatial look like? | The whole system | 1:15 | 1:15 |
| 2 | Yes, this is feasible in Python. | Why Python works | 1:30 | 2:45 |
| 3 | What does the Python compiler build? | Inside the compiler | 1:30 | 4:15 |
| 4 | Build one complete path, then expand it. | How we build it | 2:15 | 6:30 |
| 5 | The foundations are implemented. | What works today | 1:30 | 8:00 |
| 6 | Complete the core, then grow the language. | What comes next | 2:00 | 10:00 |

**Total: 10 minutes.** This is a pacing target, not a measured rehearsal. The scripts reproduce the current webpage notes with HTML whitespace normalized. Keep the map exploration and documentation tour brief; detailed syntax and API questions can use the linked notes.

## 1. What does a Python version of Spatial look like? · 1:15

**Main idea:** A Python frontend, compiler and reference engine preserve Spatial’s explicit concepts. HLS is the agreed destination.

**On screen:** Use Write, Compile and Execute to show the system. Briefly name what Spatial preserves and what Python rebuilds. HLS needs no separate explanation.

### Spoken script

The answer I’m proposing is a complete Python implementation of Spatial: a language people write through Python, a compiler written in Python, and a Python engine that runs the program’s defined behavior.

The Spatial concepts stay recognizable: explicit memory, control, parallel work, reductions and communication. We would rebuild the machinery that reads, represents, checks and executes those concepts.

The compiler would produce a structured, checked description of the program. We could run that description in Python first. The agreed HLS backend would use that description to build a hardware implementation.

HLS is already our agreed target. Today I want to explain why this system is feasible in Python, how we plan to build it, what we have completed, and what we should validate next.

### Evidence

[Proposed architecture and design decisions](https://davidydu.github.io/spatial-research-site/20---Research-Notes/50---Decision-Records/D-28.html)

[Professor discussion brief](https://davidydu.github.io/spatial-research-site/50---Python-Rewrite/05---Python-Professor-Brief.html)

[Full language coverage](https://davidydu.github.io/spatial-research-site/50---Python-Rewrite/60---Validation/01---Python-Coverage-Ledger.html)


## 2. Yes, this is feasible in Python. · 1:30

**Main idea:** Python can express the compiler algorithms and explicit Spatial rules. Practical throughput and memory use must be measured on the complete workflow.

**On screen:** Connect program records, explicit semantic rules and independent tests to feasibility. Separate the ability to implement these algorithms from the practical speed question.

### Spoken script

Yes. The compiler’s algorithms and data structures can all be implemented in Python. The main work is representing a program, analyzing its structure, checking rules and transforming it.

The important distinction is between the language we use to write the compiler and the behavior that compiler implements. For example, we can use Python integers while explicitly enforcing Spatial’s fixed-width arithmetic. We also define storage identity, lifetimes and the order of state changes.

Ordinary Python remains available for data preparation and experiments. Accelerator kernels use a defined subset that the compiler reads as source. That keeps their meaning under our control.

So my answer on feasibility is yes. The practical question is how well the complete implementation performs. We need to measure compilation time, simulator speed and memory use on useful workloads. Our existing components give us evidence for parts of the design; they do not yet establish the complete workflow.

### Evidence

[Python compiler architecture](https://davidydu.github.io/spatial-research-site/50---Python-Rewrite/10---Research/PY-R006---Compiler-Architecture-and-Framework-Choice.html)

[Explicit numeric behavior](https://davidydu.github.io/spatial-research-site/50---Python-Rewrite/10---Research/PY-R002---Numeric-and-Reduction-Semantics.html)

[Workflow and performance acceptance](https://davidydu.github.io/spatial-research-site/50---Python-Rewrite/10---Research/PY-R007---Host-Workflow-Reproducibility-and-Validation.html)


## 3. What does the Python compiler build? · 1:30

**Main idea:** One immutable program model and verifier serve source, generators, saved artifacts, execution and later lowering.

**On screen:** Follow the inputs through one verifier into the shared model. Open Explore engineering map only for a useful detail. Its colors show proposed responsibilities, not implementation status.

### Spoken script

The center of the design is one shared program model. It holds typed records for operations, control regions and storage, with explicit links between them.

The model keeps the facts that later stages need: the type of each value, which views share memory, where storage is valid, and which operations must happen in order. These facts should survive changes to the program.

Written source, generated programs and saved artifacts all reach the same verifier. A fully verified candidate becomes a checked program. Some conditions can remain as declared input requirements or supported runtime checks.

The reference engine runs those records with separate state for each invocation. Compiler transformations build a new candidate and check it before use. The later backend consumes the same meaning.

This Excalidraw map connects that overview to the detailed module responsibilities. We can zoom into the checker, runtime or roadmap during discussion. It shows the proposed full system; the progress slide will show which parts are implemented.

### Evidence

[Editable engineering architecture map](https://davidydu.github.io/spatial-research-site/50---Python-Rewrite/30---Implementation-Design/70---Engineering-Architecture-Map.html)

[Source, verifier and representation rules](https://davidydu.github.io/spatial-research-site/50---Python-Rewrite/30---Implementation-Design/10---Source-Checker-and-IR-Blueprint.html)

[Why compiler-owned Python records](https://davidydu.github.io/spatial-research-site/50---Python-Rewrite/10---Research/PY-R017---Compiler-Representation-Comparison.html)


## 4. Build one complete path, then expand it. · 2:15

**Main idea:** Finish one complete path for a reusable memory-program subset, including verification, source handling, prepared inputs, execution and artifacts.

**On screen:** Point to the declared memory subset, then follow the four implementation steps. Explain that complete verification means the initial subset’s verifier. Each admitted feature must work through the whole path.

### Spoken script

The implementation plan starts with a complete path for a limited but reusable language subset. The first family is memory programs using exact Int32 arithmetic, typed inputs, local and external storage, views, transfers, loops, branches and helpers.

We start by finishing the complete verifier for the initial subset. It needs to check memory relationships, lifetimes, initialization and the remaining whole-program obligations before it can publish a checked program. Several lower-level pieces already work.

Next we connect source capture and host inputs. The frontend reads the defined Python grammar and lowers it through general rules. A helper remains a helper, a loop remains a loop, and a memory operation remains a memory operation. Generated programs and imported artifacts use the same verifier.

Then we complete reference execution. Each run has its own values and memory state. The engine executes the selected control paths, preserves state-change order and reports faults. We connect that to a usable API and saved artifacts.

Finally, we test whether those pieces actually compose. After freezing the compiler, an independent author writes a structurally unfamiliar program within the supported subset. It must run without a special compiler path. We also make a real structural edit, recheck it and compare its behavior with independent expectations.

This is how we avoid repeating the earlier mistake. The implementation unit is a language feature working through the full pipeline. A successful application alone does not establish general support.

### Evidence

[Authorized first goal and its acceptance gates](https://davidydu.github.io/spatial-research-site/50---Python-Rewrite/30---Implementation-Design/80---Initial-Compiler-Goal.html)

[Frontend and verifier responsibilities](https://davidydu.github.io/spatial-research-site/50---Python-Rewrite/30---Implementation-Design/10---Source-Checker-and-IR-Blueprint.html)

[Execution APIs, artifacts and conformance](https://davidydu.github.io/spatial-research-site/50---Python-Rewrite/30---Implementation-Design/40---Package-and-Conformance-Blueprint.html)


## 5. The foundations are implemented. · 1:30

**Main idea:** There is tested component progress at a committed checkpoint. The complete source-to-simulation path and acceptance gates remain unfinished.

**On screen:** Mention 236 component tests once and explain their scope. Show the unfinished work beside it. Open the detailed progress page or research/site links if useful.

### Spoken script

We have moved beyond architecture notes into the foundations of the Python compiler. The committed checkpoint has 236 passing component tests. The source suite was rechecked on October 7.

The implemented pieces include immutable program records, indices that track actual uses and ownership, exact integer primitives, type and layout rules, scalar normalization, input validation and local structural checks.

These are useful pieces of a compiler, but we cannot yet take a Spatial Python source file through the complete checking and execution path. The full verifier and memory support are unfinished, and source capture and reference execution still need to be connected.

The next work is therefore concrete. Finish that path, then demonstrate shared behavior across source, generated programs and saved artifacts. The unfamiliar-composition test, structural editing test and workflow measurements remain open.

We have also organized the research as a versioned repository and a documentation website. The site connects the language decisions, architecture, implementation plan and evidence. These links let us inspect the reasoning or the exact progress record during discussion.

### Evidence

[Committed progress and unfinished acceptance gates](https://davidydu.github.io/spatial-research-site/50---Python-Rewrite/30---Implementation-Design/80---Initial-Compiler-Goal.html)

[Implementation checkpoint — requires repository access](https://github.com/davidydu/spatial-py/tree/f8a993b)

[Research documentation](https://davidydu.github.io/spatial-research-site/50---Python-Rewrite/00---Python-Rewrite-Index.html)


## 6. Complete the core, then grow the language. · 2:00

**Main idea:** Complete the subset, test new combinations and structural edits, measure the real workflow, then expand whole language families.

**On screen:** Follow Complete, Accept and Expand. Ask whether composed memory is a strong first milestone and which missing capability should come next. Keep HLS as the agreed destination at the bottom.

### Spoken script

The next milestone is a complete memory-program subset, with independently specified results, state changes and faults. That gives us something concrete to judge beyond a collection of compiler components.

Before expanding, we should show that the design handles a new combination of the supported features. We freeze the implementation and give an independent author the supported language contract. A renamed or resized development example is not enough. If the new program requires a special compiler case, we have found a gap in the general rules.

We also need a real structural transformation. It must preserve the intended behavior, keep memory relationships and source information intact, and leave the old program usable if validation fails. Passing the checker alone does not prove equivalent behavior, so we compare outcomes as well.

At the same milestone, we measure the actual supported capture, checking and execution paths. That turns the practical Python performance question into evidence.

After that, we extend whole feature families: reductions and numeric formats, then more stateful and communicating constructs. The EE 109 labs help us track which combinations matter. Each family gets source support, checking, reference behavior and tests together.

HLS remains the agreed destination. We can begin that work from a validated subset while the rest of the language grows.

The feedback I want is whether this first milestone tests enough of Spatial’s core, and which capability should come next. That would give us a clear implementation order after the meeting.

### Evidence

[Staged implementation roadmap](https://davidydu.github.io/spatial-research-site/50---Python-Rewrite/04---Python-Implementation-Roadmap.html)

[Generality and performance acceptance](https://davidydu.github.io/spatial-research-site/50---Python-Rewrite/30---Implementation-Design/80---Initial-Compiler-Goal.html)

[Language and lab coverage](https://davidydu.github.io/spatial-research-site/50---Python-Rewrite/60---Validation/01---Python-Coverage-Ledger.html)

## Questions to be ready for

**Why is Python feasible?** The required representations, graph analyses, checking rules and transformations are algorithms we can implement in Python. Spatial’s exact arithmetic and state rules are explicit. This does not claim that Python’s default arithmetic supplies those rules or that useful throughput has already been measured.

**What is the first supported scope?** A reusable subset of memory programs with Int32 data, exact Index values, strict Bool control, typed ports, SRAM/DRAM views and transfers, runtime shapes, nested loops, branches and helpers. Aliases, initialization, lifetimes and fault order are part of the scope. It is an initial portion of S1, not all Spatial or all EE 109 labs.

**Why finish the verifier before the source frontend?** We can establish the common record-level rules first. Captured source and generated programs then reach the same checked representation. Verification must cover the whole initial subset before publishing a checked program; individual checking stages are not enough.

**What makes the first milestone more than a demo?** Source, generated programs and artifact imports must agree. Independent expectations check values, state changes and faults. After freezing the implementation, an independent author supplies a structurally unfamiliar valid composition. If it requires a repair, keep the case as a regression and require a fresh unseen case for acceptance. A finite suite provides evidence, not a proof of every possible composition.

**Why test structural editing now?** It exercises ownership, references, indices, source information and memory identity before many passes depend on them. Compare behavior before and after the edit; successful rechecking alone does not establish equivalence. A failed edit must leave the old program usable.

**How will we assess performance?** Measure actual supported capture, checking and execution workloads, including latency and peak memory. The [[PY-R007 - Host Workflow Reproducibility and Validation|workflow study]] defines the targets and measurement method. The earlier representation experiment and current test-suite runtime do not satisfy those targets.

**What follows the first milestone?** Extend reductions and numeric formats, then additional stateful and communicating families under the [[04 - Python Implementation Roadmap|roadmap]]. Each family adds source support, checking, reference execution, diagnostics, artifacts and tests together. EE 109 supplies coverage targets. The agreed HLS work can begin on a validated subset while other families grow.

## Meeting links

[[05 - Python Professor Brief|Discussion brief]] · [[70 - Engineering Architecture Map|Editable engineering map]] · [[80 - Initial Compiler Goal|Implementation evidence and acceptance]] · [[04 - Python Implementation Roadmap|Full roadmap]] · [[D-28|Architecture decision]] · [[00 - Implementation Design Index|Engineering blueprints]] · [[60 - Course Syntax and Compiler Trace|EE 109 examples]] · [[PY-E002 - Spatial to Python Syntax Atlas|Syntax atlas]]

[Research repository](https://github.com/davidydu/spatial-research) · [Documentation website](https://davidydu.github.io/spatial-research-site/) · [Website repository](https://github.com/davidydu/spatial-research-site)
