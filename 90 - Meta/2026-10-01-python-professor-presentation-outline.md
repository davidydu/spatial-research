---
type: presentation-outline
title: "Python Spatial — professor presentation and script"
project: spatial-python
date: 2026-10-01
updated: 2026-10-07
status: meeting-ready
scope: "Six-slide architecture discussion: what a Python version of Spatial looks like"
---

# What does a Python version of Spatial look like?

[Open the presentation](https://davidydu.github.io/spatial-research-site/presentation/python/). Six architecture slides, about ten minutes before discussion. Press **N** for the current script, **E** for its sources, and the arrow keys to move. Slide 3 embeds the Excalidraw overview; **Explore engineering map** opens section navigation, zoom, panning and the editable source.

The professor knows Spatial. The talk answers what the Python system would be: its language boundary, compiler representation, reference execution and later HLS path. It does not walk through a Spatial program. EE 109 examples, generality checks, implementation progress and the documentation repositories are supporting material.

The pure Python direction is accepted. The architecture and deliberate semantic changes in [[D-28]] remain proposed for review. David authorized the initial implementation experiment on 4 October; that authorization is separate from adoption of the complete architecture.

## Six questions and timing

| Slide | Main question | Navigation label | Time | Elapsed |
|---|---|---|---|---|
| 1 | What does a Python version of Spatial look like? | The whole system | 1:15 | 1:15 |
| 2 | What does “Python” mean for the language? | The language boundary | 1:30 | 2:45 |
| 3 | What does the Python compiler build? | Inside the compiler | 2:00 | 4:45 |
| 4 | How would it execute in Python? | Running it in Python | 1:45 | 6:30 |
| 5 | Where does HLS fit? | The later HLS path | 1:45 | 8:15 |
| 6 | Does this capture the Python Spatial we want to build? | The design to review | 1:45 | 10:00 |

**Total: 10 minutes.** The scripts reproduce the webpage notes with HTML whitespace normalized. Timing is a delivery target, not a measured rehearsal. Keep detailed syntax, module APIs and implementation evidence for questions.

## 1. What does a Python version of Spatial look like? · 1:15

**Main idea:** Python implements the language frontend, compiler and reference engine. Spatial keeps explicit types, storage, control and parallel work.

**On screen:** Use Write, Compile and Execute to explain the proposed system. Point out which Spatial concepts stay and which implementation layers are rebuilt.

### Spoken script

The answer I’m proposing is a complete Python implementation of Spatial: a language people write through Python, a compiler written in Python, and a Python engine that runs the program’s defined behavior.

The Spatial concepts stay recognizable: explicit memory, control, parallel work, reductions and communication. We would rebuild the machinery that reads, represents, checks and executes those concepts.

The compiler would produce a structured, checked description of the program. We could run that description in Python first. A later backend would use the same description to build a hardware implementation.

I want to focus this discussion on the shape of that system: what Python means at the language boundary, what sits inside the compiler, how execution works, and where HLS fits. Detailed syntax examples and implementation evidence are linked for follow-up.

### Evidence

[Proposed architecture and design decisions](https://davidydu.github.io/spatial-research-site/20---Research-Notes/50---Decision-Records/D-28.html)

[Professor discussion brief](https://davidydu.github.io/spatial-research-site/50---Python-Rewrite/05---Python-Professor-Brief.html)

[Full language coverage](https://davidydu.github.io/spatial-research-site/50---Python-Rewrite/60---Validation/01---Python-Coverage-Ledger.html)


## 2. What does “Python” mean for the language? · 1:30

**Main idea:** Ordinary Python runs host experiments; captured kernel source follows Spatial rules. Compile-time choices and runtime inputs remain distinct.

**On screen:** Point across host Python and captured kernel source, then down to compile time and run time. Keep this at the language boundary; no kernel walkthrough.

### Spoken script

Python has two roles. On the host side, it is the normal Python environment for data and experiments. Inside a kernel, Python syntax expresses a defined Spatial language.

The compiler reads the kernel source. It does not execute the kernel’s decorators, annotations or body to discover what the program is. That lets it inspect retained branches, scopes and storage relationships before a run.

We also keep compile time and run time explicit. Source, dependencies and chosen meta parameters are fixed for compilation. Actual input values and supported runtime dimensions belong to a run. A runtime branch still chooses its path when the program executes.

This is a deliberate language boundary. Spatial defines numeric precision, memory and control behavior even though the program is written with Python syntax. General Python libraries belong on the host unless we explicitly add their operations to the kernel language.

### Evidence

[Source acquisition and language model](https://davidydu.github.io/spatial-research-site/50---Python-Rewrite/10---Research/PY-R001---Programming-Model-Study.html)

[Source and checker blueprint](https://davidydu.github.io/spatial-research-site/50---Python-Rewrite/30---Implementation-Design/10---Source-Checker-and-IR-Blueprint.html)

[Complete proposed host API](https://davidydu.github.io/spatial-research-site/50---Python-Rewrite/10---Research/PY-R016---Source-and-Host-Workflow-Refinement.html)


## 3. What does the Python compiler build? · 2:00

**Main idea:** Source, generators and imported artifacts reach one checker and one immutable program model. Helpers and libraries compose the same operations.

**On screen:** Follow the input routes through the checker to the shared model. Open Explore engineering map for the original Excalidraw overview and zoomable details. The map describes proposed responsibilities, not implementation status.

### Spoken script

At the center is a program representation that we own in Python. You can think of it as typed records of operations, control regions and storage, with explicit links between them.

It carries the information needed to preserve Spatial’s behavior: the type of a value, whether two views share memory, where local storage lives, which region owns an operation, and which state changes must happen in order.

Written source, generated programs and imported artifacts reach the same checking boundary. The compiler first resolves and normalizes them into its common model. Only a fully verified candidate becomes a checked program. Helpers and libraries compose the same operations. A builder is another way to supply a program, not another set of language rules. Checked programs can retain declared input conditions and supported runtime checks; not every property must be proved statically.

The accepted records are immutable. An optimization or structural edit makes a new candidate, repairs its references and checks it before use. That gives checking, simulation and hardware planning one common meaning to work from.

The Excalidraw map shows this design at both levels. Its top row is the whole system; the detailed sections assign responsibilities to the frontend, verifier, execution engine and backend. We can zoom into those during discussion. The full architecture remains proposed.

### Evidence

[Editable engineering architecture map](https://davidydu.github.io/spatial-research-site/50---Python-Rewrite/30---Implementation-Design/70---Engineering-Architecture-Map.html)

[Source, verifier and representation rules](https://davidydu.github.io/spatial-research-site/50---Python-Rewrite/30---Implementation-Design/10---Source-Checker-and-IR-Blueprint.html)

[Why compiler-owned Python records](https://davidydu.github.io/spatial-research-site/50---Python-Rewrite/10---Research/PY-R017---Compiler-Representation-Comparison.html)


## 4. How would it execute in Python? · 1:45

**Main idea:** A reusable checked program is separate from the mutable state of each invocation. Reference execution preserves values, state changes and faults.

**On screen:** Show one immutable program serving Run A and Run B. Explain why inputs, storage contents and active control belong to a run. Mention explicit sessions only if persistent state comes up.

### Spoken script

The reference engine is a Python interpreter for our checked representation. It implements Spatial’s numeric, memory and control rules.

The program and the execution state are separate. The same checked program can be used for several runs. Each invocation has its inputs, values, memory contents, active control and pending operations. Views that share storage keep that relationship. Persistent state, when requested, belongs to an explicit session.

This matters because Spatial behavior includes state and effects. The engine must take only the selected branch, respect the required order of operations, and preserve memory lifetimes. For later communicating programs, waiting and resumable work must also have defined behavior.

A completed run exposes complete outputs. A fault or suspended run has a different result. We can compare outputs and observable effects with independent expectations, then use this behavior as a reference for transformations and hardware plans.

This engine tells us what the program does. It does not yet tell us its cycle count or the quality of a hardware implementation.

### Evidence

[Reference execution, state and hardware design](https://davidydu.github.io/spatial-research-site/50---Python-Rewrite/30---Implementation-Design/30---State-Simulator-and-HLS-Blueprint.html)

[Invocation APIs and outcomes](https://davidydu.github.io/spatial-research-site/50---Python-Rewrite/30---Implementation-Design/40---Package-and-Conformance-Blueprint.html)

[Numeric engine design](https://davidydu.github.io/spatial-research-site/50---Python-Rewrite/30---Implementation-Design/20---Numeric-Engine-Blueprint.html)


## 5. Where does HLS fit? · 1:45

**Main idea:** Planning introduces hardware choices and checks target obligations before HLS emission. Reference validity does not imply target eligibility.

**On screen:** Follow the checked program through planning, plan checks and HLS emission. Explain that a runtime loop can have a variable iteration count while simultaneous hardware state and storage remain bounded.

### Spoken script

HLS comes after the language has a defined meaning. The Python compiler takes the checked program and builds a target-specific implementation plan.

That plan introduces hardware choices: storage and banking, work mapping, scheduling constraints, interfaces and realizations of numeric operations. Those choices must satisfy target requirements and preserve the program’s allowed observable behavior. A program can be valid for reference execution and still lack a legal implementation for a particular target. Unknown required target facts block emission. Runtime loops need not have a fixed iteration count, but simultaneous hardware state and storage must be bounded.

We would check the plan and execute its modeled behavior in Python against the reference. Then the backend emits HLS C++ and any required interface components. Vendor simulation and synthesis give us separate evidence about the generated hardware.

So pure Python describes our compiler and reference engine. It does not mean the eventual FPGA executes Python. The HLS code is an output of the compiler.

The split also lets us start hardware work on an accepted subset while the rest of the language grows. We should establish the Python language and reference path first, then use that stable meaning to guide lowering.

### Evidence

[Target planning and HLS responsibilities](https://davidydu.github.io/spatial-research-site/50---Python-Rewrite/30---Implementation-Design/30---State-Simulator-and-HLS-Blueprint.html)

[Compiler and HLS contract](https://davidydu.github.io/spatial-research-site/50---Python-Rewrite/40---Specification/40---Python-Compiler-and-HLS-Contract.html)

[Staged implementation roadmap](https://davidydu.github.io/spatial-research-site/50---Python-Rewrite/04---Python-Implementation-Roadmap.html)


## 6. The proposed Python Spatial system · 1:45

**Main idea:** Review the language boundary, the Python-owned representation and the split between reference execution and hardware planning.

**On screen:** Ask whether these choices capture the Python Spatial the professor wants. Open Research, progress & next experiment only for supporting questions; documentation and implementation progress do not lead the talk.

### Spoken script

These are the three design choices I would like to review. First, capture source as the main interface so the compiler can inspect the program before execution. Generated programs still use the same checking rules.

Second, keep the language representation and its rules under our control in Python. That gives us a shared foundation for checking, transformations, execution and backends.

Third, separate the reference behavior from hardware choices. The simulator defines the execution reference. Target planning adds implementation decisions that must preserve it.

The tradeoff is that accelerator kernels follow a defined Python subset. We still need to measure compiler throughput and hardware quality; choosing Python does not settle those engineering questions. Where old Spatial implementations disagree, the proposed behavior changes remain explicit review items.

This is the research result I want feedback on: does this language boundary and system structure match the Python Spatial we want to build? The research notes, current implementation evidence and next experiment are available here if useful. They support the design discussion rather than setting the agenda.

### Evidence

[Architecture recommendation and unresolved obligations](https://davidydu.github.io/spatial-research-site/20---Research-Notes/50---Decision-Records/D-28.html)

[Professor discussion brief](https://davidydu.github.io/spatial-research-site/50---Python-Rewrite/05---Python-Professor-Brief.html)

[Current component evidence and acceptance criteria](https://davidydu.github.io/spatial-research-site/50---Python-Rewrite/30---Implementation-Design/80---Initial-Compiler-Goal.html)

## Questions to be ready for

**Does “pure Python” include the eventual hardware?** Python implements the compiler and reference engine. The hardware backend emits HLS C++ and interface descriptions; the FPGA does not execute Python.

**Why capture source?** It preserves the kernel structure, literal text and source locations before a run. Static parameters specialize the program; runtime branches and values remain part of its checked meaning.

**Why one shared representation?** Source, builders, libraries and imported programs use the same operations and verifier. Simulation and hardware planning consume the same accepted meaning. Optional framework adapters remain derived views.

**Does “checked” mean every condition is proved statically?** No. The design distinguishes proved facts, declared invocation conditions and supported runtime guards. A hardware plan has additional obligations; unknown required target facts block emission.

**Must simulator and hardware use the same schedule?** They must preserve allowed observable behavior. Communicating programs may permit several valid traces. Reference simulation does not predict hardware cycle timing.

**How do we avoid a compiler for only the known examples?** Libraries and helpers compose reusable language operations. The initial experiment adds an independent unfamiliar program after freezing a compiler revision, along with expected values, effects and faults. That acceptance gate remains ahead.

**What is implemented?** The committed `f8a993b` checkpoint has 236 passing component tests for records, numeric primitives, input/type/layout rules, scalar normalization and structural checks. The full source-to-simulation path, verifier and memory execution are unfinished. [[80 - Initial Compiler Goal]] owns the detailed scope.

## Supporting material

The final slide’s **Research, progress & next experiment** drawer contains implementation evidence and the next composed-memory experiment. Use the linked documentation for EE 109 syntax examples, generality acceptance and the research history. These support the architecture discussion; they are not additional main slides.

[[05 - Python Professor Brief|Discussion brief]] · [[70 - Engineering Architecture Map|Editable engineering map]] · [[D-28|Architecture decision]] · [[00 - Implementation Design Index|Implementation blueprints]] · [[80 - Initial Compiler Goal|Implementation evidence and acceptance]] · [[60 - Course Syntax and Compiler Trace|EE 109 examples]] · [[PY-E002 - Spatial to Python Syntax Atlas|Syntax atlas]] · [[04 - Python Implementation Roadmap|Roadmap]]

[Research repository](https://github.com/davidydu/spatial-research) · [Documentation website](https://davidydu.github.io/spatial-research-site/) · [Website repository](https://github.com/davidydu/spatial-research-site)
