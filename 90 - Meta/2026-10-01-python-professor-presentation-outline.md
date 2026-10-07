---
type: presentation-outline
title: "Python Spatial — professor presentation and script"
project: spatial-python
date: 2026-10-01
updated: 2026-10-07
status: meeting-ready
---

# Python Spatial: professor presentation and script

[Open the presentation](https://davidydu.github.io/spatial-research-site/presentation/python/). Seven slides, about ten minutes before discussion. Press **N** for the current slide’s script, **E** for its evidence, and the arrow keys to move. Slide 4 embeds the Excalidraw overview: choose **Explore engineering map** for section navigation, zoom, panning and the editable source.

The professor knows Spatial. This talk explains the Python programming model, the architecture, the evidence so far, and the next research result. The initial experiment was authorized on 4 October. The full architecture in [[D-28]] and proposed semantic changes remain for review. Component tests do not establish complete source-to-simulation execution or hardware results.

## Talk at a glance

| Slide | Headline | Navigation label | Time | Elapsed |
|---|---|---|---|---|
| 1 | Spatial in Python. | The idea | 0:45 | 0:45 |
| 2 | A familiar Spatial program | The program | 1:30 | 2:15 |
| 3 | Python for the experiment. Spatial for the kernel. | The Python boundary | 1:00 | 3:15 |
| 4 | One checked program, two uses | The architecture | 1:45 | 5:00 |
| 5 | A compiler must handle new combinations | Test generality | 1:30 | 6:30 |
| 6 | What now works | Progress & documentation | 2:00 | 8:30 |
| 7 | The next result: a complete, reusable path | Next result & discussion | 1:30 | 10:00 |

**Total: 10 minutes.** The spoken scripts below reproduce the webpage notes, with only HTML whitespace normalized. The talk includes brief visual interactions and a short documentation tour; the timing is a target, not a measured rehearsal. Keep detailed API, numeric-policy and module questions for the linked documentation or map discussion.

## 1. Spatial in Python. · 0:45

**Main idea:** The compiler and the programs use Python; Spatial retains precise meaning.

**On screen:** Use the opening picture to distinguish the program from the compiler. Do not imply the picture is a live compiler result.

### Spoken script

After our last discussion, I worked through what a Python rewrite would look like. We would write Spatial programs in Python, and build the compiler and reference simulator in Python too. Spatial still has explicit memories, control and parallel work.

The important question is how we preserve what each program means, and then turn that meaning into hardware. Python is capable of expressing the compiler algorithms. We still need precise rules and independent checks of the results.

We have moved from research into an initial implementation experiment. Today I’ll show the proposed user experience, the architecture, what is implemented, and how we will test whether it handles new programs. The complete workflow is still in progress.

### Evidence

- [Professor discussion brief](https://davidydu.github.io/spatial-research-site/50---Python-Rewrite/05---Python-Professor-Brief.html)
- [D-27: accepted pure Python direction](https://davidydu.github.io/spatial-research-site/20---Research-Notes/50---Decision-Records/D-27.html)
- [D-28: proposed compiler architecture](https://davidydu.github.io/spatial-research-site/20---Research-Notes/50---Decision-Records/D-28.html)

## 2. A familiar Spatial program · 1:30

**Main idea:** The proposed code exposes ports, storage and control.

**On screen:** Click Load, Compute, Store, then the second tile. The animation illustrates behavior; it is not an execution trace from the compiler.

### Spoken script

This program reads 32 values, multiplies each by a scale, and writes the results. It works in two tiles of 16. The picture follows the same code.

At the top are the input memory, the scale and the output memory. Inside the outer loop, we declare two local buffers. One holds the input tile; the other holds the result.

First we load a tile. The inner loop multiplies each value. Then we store the result back to external memory and move to the next tile.

We still tell the compiler about memory and control. Those annotations describe Spatial objects; ordinary Python does not allocate SRAM by running this function. The foreach loop gives the hardware planner work it can parallelize. It does not promise sixteen hardware lanes or a particular cycle count.

For this illustration, the inputs are one through 32 and the scale is two. The expected outputs are two through 64. This is an animation of the intended behavior, not a compiler run.

Click Load, Compute, Store, then choose the second tile.

### Evidence

- [E1: exact proposed source and builder spellings](https://davidydu.github.io/spatial-research-site/50---Python-Rewrite/10---Research/PY-R001---Programming-Model-Study.html#e1-two-proposed-spellings-of-tiled-scale)
- [Source capture, declarations and checking](https://davidydu.github.io/spatial-research-site/50---Python-Rewrite/30---Implementation-Design/10---Source-Checker-and-IR-Blueprint.html)

## 3. Python for the experiment. Spatial for the kernel. · 1:00

**Main idea:** Host Python runs the experiment; kernel source is checked as Spatial.

**On screen:** Explain the boundary before mentioning the three workflow stages. The complete host API is linked for questions.

### Spoken script

There are two roles for Python here. Normal Python handles data, files and experiments. The kernel is a piece of source that the compiler reads as Spatial. It uses a defined subset of Python syntax with Spatial’s types and storage.

This boundary lets us know what the whole kernel means before we run it. We do not discover the program by executing one sample input. We can inspect both branches, track storage and explain errors at their source.

The intended workflow is straightforward: read and specialize the source, check the program, bind typed inputs, then simulate. Complete results are available only after a completed run. We have specified this API; the complete path is still being built.

### Evidence

- [Complete proposed host example](https://davidydu.github.io/spatial-research-site/50---Python-Rewrite/10---Research/PY-R016---Source-and-Host-Workflow-Refinement.html)
- [Public API and result contracts](https://davidydu.github.io/spatial-research-site/50---Python-Rewrite/30---Implementation-Design/40---Package-and-Conformance-Blueprint.html)

## 4. One checked program, two uses · 1:45

**Main idea:** Simulation and hardware planning share one checked meaning.

**On screen:** Point across the overview. If asked for detail, open the map and use Compiler, Execution & HLS or Lab roadmap. Colors show responsibilities, not completion.

### Spoken script

This is the main architecture decision. One checked representation owns the meaning of the program. It records the values, memories, control and order of operations.

The Python simulator runs that meaning. Hardware planning then decides how to realize it: where data lives, how work is scheduled, and what interfaces we need. These paths must agree about the program’s behavior.

That gives us a stable reference when we change the hardware implementation. A transformation creates a new candidate and checks it before use. Changing a schedule should preserve the observable results and state changes.

The Excalidraw map connects this big picture to the engineering details. We can zoom into checking, execution or the lab roadmap during discussion. The map is the proposed architecture. Its colors describe responsibilities, not what is already implemented.

### Evidence

- [Editable engineering map and linked blueprints](https://davidydu.github.io/spatial-research-site/50---Python-Rewrite/30---Implementation-Design/70---Engineering-Architecture-Map.html)
- [Architecture decision for review](https://davidydu.github.io/spatial-research-site/20---Research-Notes/50---Decision-Records/D-28.html)
- [State, simulator and HLS design](https://davidydu.github.io/spatial-research-site/50---Python-Rewrite/30---Implementation-Design/30---State-Simulator-and-HLS-Blueprint.html)

## 5. A compiler must handle new combinations · 1:30

**Main idea:** New combinations must work through reusable rules.

**On screen:** Walk through freeze, independent unfamiliar program, unchanged compiler. This gate is still ahead.

### Spoken script

The earlier risk was a compiler that looked successful because it recognized the examples we gave it. We want reusable language rules that work when someone combines the constructs in a new way.

Our first scope is small memory programs with exact integers, loops, branches, helpers and shared views. We have written down that scope. We should vary several of those features together, including how helpers share storage.

The important test comes after we freeze a compiler revision. An independent reviewer writes a valid program with an unfamiliar structure and independent expected results. It must run without adding a special compiler path.

If the new case exposes a bug, we fix it and keep the case as a regression. Then we need a fresh unseen program for acceptance. A finite test suite cannot prove every possible combination, but this tests something much stronger than resizing or renaming a known lab. We have not reached this gate yet.

### Evidence

- [Frozen initial scope and acceptance obligations](https://davidydu.github.io/spatial-research-site/50---Python-Rewrite/30---Implementation-Design/80---Initial-Compiler-Goal.html)
- [Language-wide coverage ledger](https://davidydu.github.io/spatial-research-site/50---Python-Rewrite/60---Validation/01---Python-Coverage-Ledger.html)

## 6. What now works · 2:00

**Main idea:** There is committed component progress, with the unfinished workflow clearly stated.

**On screen:** Mention 236 tests once, explain what they establish, then briefly open the progress page and show the research/site repository links.

### Spoken script

We have started building the foundations, and there is committed code behind this slide. The first group handles exact numeric values. The next checks program records, types, layouts and which values are visible in nested regions. Structural checking also tracks the required order of effects.

The committed checkpoint passes 236 component tests. The source suite was rerun on October 7 from an isolated copy of that commit. The checkpoint also has earlier source and installed-package checks and independent specification and code-quality reviews. These tests give evidence for those components; they do not establish a working end-to-end compiler.

The full verifier, memory rules and execution path are still unfinished. We cannot yet take the displayed source program through checking and simulation, and the unfamiliar-program acceptance test has not happened.

We have also built a documentation system for reviewing the work. The research repo holds the notes, contracts and evidence. The website publishes those files with links between them. This progress page says exactly what works and what remains. The course page connects EE 109 patterns to proposed Python. The architecture decision keeps unresolved obligations visible.

For the meeting, I would open the progress page briefly and show how it links back to the design. The private implementation repo is also linked there for people with access.

### Evidence

- [Committed implementation evidence and remaining gates](https://davidydu.github.io/spatial-research-site/50---Python-Rewrite/30---Implementation-Design/80---Initial-Compiler-Goal.html)
- [Private implementation checkpoint — repository access required](https://github.com/davidydu/spatial-py/tree/f8a993b)
- [Documentation source repository](https://github.com/davidydu/spatial-research)

## 7. The next result: a complete, reusable path · 1:30

**Main idea:** Finish a reusable memory-program path, then begin HLS for that accepted subset.

**On screen:** Ask about architecture, acceptance criteria and next course-pattern priority. Separate language behavior, compiler quality and hardware quality.

### Spoken script

The next deliverable is a complete path through the declared memory-program subset: read source, check it, run it and return a reproducible result. It also has to explain invalid programs and handle new combinations through the same rules.

We will test an actual structural edit as well. When we duplicate or move part of a program, references, storage identities and effect order must still be right. A failed candidate must leave the old program intact.

Once that subset is accepted, we can start hardware planning for it while the rest of the language grows. We should check the plan’s behavior against the reference, generate HLS, and then use the vendor tools to establish hardware correctness, resources and timing. Python simulation alone does not establish any of those hardware results.

The initial implementation experiment is already authorized. What I would like your feedback on is the shared checked-program architecture, whether these acceptance criteria make a useful first research result, and which EE 109 pattern should come next. Proposed semantic changes remain explicit review items.

### Evidence

- [Initial experiment and acceptance criteria](https://davidydu.github.io/spatial-research-site/50---Python-Rewrite/30---Implementation-Design/80---Initial-Compiler-Goal.html)
- [Language and hardware roadmap](https://davidydu.github.io/spatial-research-site/50---Python-Rewrite/04---Python-Implementation-Roadmap.html)
- [Architecture and proposed semantic changes](https://davidydu.github.io/spatial-research-site/20---Research-Notes/50---Decision-Records/D-28.html)

## Questions to be ready for

**Why pure Python?** The compiler algorithms and explicit representations can be implemented in Python. We assume the team has the necessary capability. Correctness comes from specified rules, checked representations and independent evidence. Compiler throughput still needs measurement on real supported workloads.

**Is this arbitrary Python to hardware?** The host is ordinary Python. Accelerator kernels use a defined Spatial subset with explicit types, storage and control. Source is read without executing kernel bodies or decorators.

**What is implemented today?** Core records and indices, exact stateless numeric rules, input validation, shared type/layout rules, scalar normalization and structural checking at `f8a993b`. The 236 component tests are scoped evidence. [[80 - Initial Compiler Goal]] lists the unfinished parts.

**How do we avoid another special-case compiler?** Use operation-level rules, a frozen supported subset, independent expectations and an unfamiliar composition written after freezing the implementation. If it requires a fix, it becomes a regression and acceptance needs a fresh unseen case.

**When does HLS start?** For a subset that has passed its reference and representation gates, build and check its implementation plan and execute the plan against the reference. Then generate HLS and collect vendor evidence. Later language families can grow in parallel.

**What is being requested from the professor?** Review the shared checked-program architecture and proposed semantic changes, assess the first subset’s acceptance criteria, and choose the next EE 109 pattern priority. The initial implementation experiment already has David’s authorization; full architecture adoption is separate.

## Meeting links

[[05 - Python Professor Brief|One-page brief]] · [[70 - Engineering Architecture Map|Editable engineering map]] · [[80 - Initial Compiler Goal|Implementation evidence]] · [[60 - Course Syntax and Compiler Trace|EE 109 examples]] · [[D-28|Architecture decision]] · [[04 - Python Implementation Roadmap|Roadmap]]
