---
type: design
title: "Spatial in Python — professor presentation and speaker notes"
project: spatial-python
date: 2026-10-01
status: approved-presentation-outline
scope: "Seven-slide, ten-minute presentation of the proposed pure Python rewrite"
related:
  - "[[05 - Python Professor Brief]]"
  - "[[PY-R001 - Programming Model Study]]"
  - "[[D-27]]"
  - "[[D-28]]"
---

# Spatial in Python

## Purpose and authority

Answer one question: **What would a Python rewrite of Spatial look like?** The professor already knows Spatial. Start with the proposed program, follow it through checking and simulation, show the research behind the design, and end with the first implementation milestone.

David approved the seven-slide structure and requested a vivid web presentation. That approval concerns this presentation. [[D-27]] accepts the pure Python direction; [[D-28]] remains the detailed architecture proposal for professor review. The Python frontend, semantic compiler and reference simulator described below are proposed, with no Rust core. Neither research completion nor a working presentation establishes a working Python compiler.

<a href="presentation/python/index.html" data-router-ignore target="_blank" rel="noopener noreferrer">Open the Python presentation</a>. The <a href="presentation/index.html" data-router-ignore target="_blank" rel="noopener noreferrer">28 September presentation</a> remains a historical artifact at its existing route.

## Approved story and timing

| Slide | Headline | Main visual | Time | Elapsed |
|---|---|---|---|---|
| 1 | Spatial in Python. | Program → Python compiler → reference simulation | 0:45 | 0:45 |
| 2 | A familiar Spatial program | Exact proposed tiled-scale source beside two tiles and two SRAM buffers | 2:00 | 2:45 |
| 3 | Python around the kernel | Ordinary host Python beside captured kernel source | 1:30 | 4:15 |
| 4 | A program the compiler understands | Read source → resolve names → check meaning → checked program | 1:30 | 5:45 |
| 5 | Values and state both matter | Scale control and a separate two-queue branch illustration | 1:30 | 7:15 |
| 6 | Research and documentation | Research repository, website and five implementation blueprints | 1:15 | 8:30 |
| 7 | One complete program through Python | Accept the program, explain mistakes and check behavior; then HLS | 1:30 | 10:00 |

The scripts below mirror the presentation’s speaker notes. Italicized note paragraphs are presentation cues. They include room for pointing, interactive examples and one short documentation tour. Timing is a delivery target, not a measured rehearsal. Keep citations and detailed qualifications in the notes/source panel; retain the short status labels on screen.

## Slide 1 — Spatial in Python.

**On screen:** “Write Spatial programs in Python. Build the compiler in Python too.” Show the program, Python compiler and Python reference simulation in one vertical path. The opening status is **For professor review**, with **Proposed design. Compiler not yet implemented.** at the foot.

**Visual action:** Follow the short load/compute/store fragment down through “Read the program. Check its meaning.” to illustrative outputs `2, 4, 6, 8, …`. Keep the opening focused on Python source, checking and simulation; introduce the HLS path mainly on the last slide.

**Full speaker script, 0:45:**

> After our last discussion, I looked at what it would mean to write Spatial and its compiler in Python. The proposal is to keep the concepts that matter in Spatial: memories, control and parallel work. We would express them in Python syntax, and the compiler itself would also be Python.
>
> I’ll follow one small program through that system. The first goal is to understand the program and simulate its behavior. That gives us a checked program to lower to hardware later. Everything I’m showing here is a proposed design. We have research and small experiments, but we haven’t built this compiler yet.

**Evidence:** [[D-27#Decision and authority|Accepted direction]], [[D-28#Recommendation|Proposed architecture]], [[05 - Python Professor Brief#The proposal|Professor brief]].

**Boundary:** Do not present any pipeline box as an implemented Python compiler component.

## Slide 2 — A familiar Spatial program

**On screen:** The exact E1 source-capture sketch from [[PY-R001 - Programming Model Study#Source capture|PY-R001]], labeled **Proposed syntax · not implemented**:

```python
@kernel
def tiled_scale(src: In[Dram[Int, 32]],
                scale: In[Int],
                dst: Out[Dram[Int, 32]]):
    for base in sequential(0, 32, step=16):
        tile_in: Sram[Int, 16]
        tile_out: Sram[Int, 16]
        load(tile_in, src[base:base + 16])
        for i in foreach(0, 16):
            tile_out[i] = tile_in[i] * scale
        store(dst[base:base + 16], tile_out)
```

**Visual action:** Use the tile controls for positions `0–15` and `16–31`, then click **Load → Compute → Store** or **Play**. Keep the separate `tile_in` and `tile_out` SRAM buffers visible and highlight the matching source lines. The illustration uses input values `1…32` and scale `2`, giving expected outputs `2, 4, …, 64`. This is an explanatory input variant of the same proposed kernel. The original E1 fixture uses `0…31` and scale `3`; the source sketch above remains unchanged. Animation timing does not represent hardware cycles.

**Full speaker script, 2:00:**

> This example reads 32 values, scales each one, and writes the results out. It does that in two tiles of 16. The code on the left is the proposed spelling, and the picture on the right follows one tile.
>
> At the top, we declare the input memory, the scale and the output memory. These types tell the compiler what kind of data each port carries. Then we declare two local buffers. One holds the input tile and the other holds the result.
>
> First we load a tile. Then the inner loop multiplies each value. Finally we store the result back to external memory. The outer loop moves to the next tile. I can click through those operations here and show the corresponding line of code.
>
> The important point is that this still describes a Spatial program. We haven’t hidden the local memory or the loop structure. The compiler can see both. The foreach loop expresses work the hardware planner can parallelize. This picture doesn’t claim that every iteration executes in one cycle.
>
> The example is a design sketch from the research documents. These annotations have meaning in the language we are defining. They do not allocate SRAM through ordinary Python execution.
>
> *Click Load, Compute, Store, then choose 16–31. Allow time to read the code.*

**Evidence:** [[PY-R001 - Programming Model Study#E1: two proposed spellings of tiled scale|Exact source and interpretation]], [[PY-E001 - Initial Example Corpus|Source-derived E1 input and expected output]]. Original source reference: `spatial@e7a8f2f:test/spatial/tests/ee109/Lab1Part2DramSramExample.scala:6-43`.

**Boundary:** The walkthrough and expected values are explanatory, not a compiler execution recording or a hardware performance measurement. `foreach` does not establish that sixteen hardware lanes already exist.

## Slide 3 — Python around the kernel

**On screen:** **Host program — Python executes this** beside **Accelerator kernel — The compiler captures this**. The host example uses `inputs = list(range(1, 33))`, `scale = 2` and an ordinary Python expected-value calculation. The kernel fragment declares local memory and describes the work.

**Visual action:** Point from the host input and expected-value calculation to the separate captured kernel fragment. The takeaway says **The compiler reads kernel source without executing its body, decorators or annotations**. No normal call to `tiled_scale` is shown.

**Full speaker script, 1:30:**

> There are two roles for Python here. The host program is ordinary Python. It can read files, make input arrays, choose parameters and compare results. On the left, we make the 32 input values and a simple expected answer.
>
> The accelerator kernel has a different role. The compiler reads its source and recognizes the Spatial operations. It does not run the function to discover what happened. That means it can preserve a branch or loop as part of the program, even when the condition or trip count depends on an input.
>
> We need a defined set of supported Python statements and Spatial operations. The familiar syntax helps us write the program, but the compiler still controls its meaning. For example, Int has a specific width, and an SRAM declaration describes storage.
>
> For generated programs, the research also proposes a builder that constructs the same internal program and passes through the same checks. For the main user experience, I’m showing the source form.

**Evidence:** [[PY-R001 - Programming Model Study]], [[PY-R004 - Capture Composition and Diagnostics]], [[10 - Source Checker and IR Blueprint]], [[D-28#Decisions proposed together|Capture and semantic ownership]].

**Boundary:** Do not invent a currently working notebook magic, package import, kernel invocation or API transcript. The builder and source routes are both proposed.

## Slide 4 — A program the compiler understands

**On screen:** Four selectable stages: **Read source → Resolve names → Check meaning → Keep a checked program**. The detail panel follows the same tiled program with explanatory views of loops, declarations, types, shapes and effects.

**Visual action:** Click through the stages to change the explanation and simplified program view. The last stage is ready for reference simulation. The supporting line says Python owns the language rules and stores the checked program in immutable Python records. This follows the 3 October refinement in [[11 - Design Refinement Iterations]]. These views are explanatory notation, not actual compiler output.

**Full speaker script, 1:30:**

> Now we can look inside the compiler. It first reads the supported source and records the structure. It resolves names so each use of tile_in or scale points to the right declaration.
>
> Then it checks the meaning. Does this operation accept these types? Does the tile have the right shape for this transfer? Do these reads and writes happen in a valid order? If something is wrong, the compiler should explain it at the relevant source location.
>
> The output is a checked representation of the program. It still contains the memories and control structure. That representation is what the simulator would run.
>
> We now propose storing the checked program and hardware plan in our own immutable Python records. The simulator and hardware planner would use the same checked program. We compared this with xDSL; it remains an option if a specific backend needs it. We still have to implement and test the compiler.
>
> *Click through the stages. The right-hand view is explanatory notation, not actual compiler output.*

**Evidence:** [[10 - Source Checker and IR Blueprint]], [[PY-R006 - Compiler Architecture and Framework Choice]], [[40 - Python Compiler and HLS Contract]], [[07 - Python Implementation Readiness Audit]].

**Boundary:** The bounded records/xDSL comparison supports the representation choice; it is not a complete compiler benchmark or an implemented Spatial checker. Avoid claiming that all legal programs can be proved statically.

## Slide 5 — Values and state both matter

**On screen:** “Values and state both matter.” The left panel shows the first four input values `1, 2, 3, 4`, a scale control initially set to `2`, and expected outputs `2, 4, 6, 8`. The right panel is a separate branch illustration with queues `A = [3, 5, 7]` and `B = [10, 20, 30]`. Its controls choose a queue, take one value or reset.

**Visual action:** Change the scale to update the expected first four outputs. Then choose B and take one value: B consumes `10`, while A remains `[3, 5, 7]`. This miniature isolates a selected branch’s effect. It does not reproduce the full E3 fill/reduction program or its emptiness-controlled branch.

**Full speaker script, 1:30:**

> The simulator has to preserve more than the final number. For our scale example, we can calculate the expected answer independently with ordinary Python. We would compare all 32 values. The slide only shows the first four.
>
> We also need exact numeric rules. The proposal makes Int a signed 32-bit value with wrapping arithmetic. That is different from Python’s unbounded integers, so the simulator must implement the Spatial rule explicitly.
>
> State gives us another kind of test. Here is a small separate example. If a branch chooses queue B, it should take one value from B and leave A alone. Evaluating both branches and then choosing a result would already have changed the wrong state.
>
> So our reference tests need expected values and expected state changes. Those expectations should come from the language contract and independent examples. The animations here illustrate those expectations. They are not running the proposed compiler, and they do not measure hardware timing.
>
> *Change the scale. Then choose B and take one value to show A staying unchanged.*

**Evidence:** [[PY-R001 - Programming Model Study#Common functional model for discussion|E3’s underlying selected-branch rule and trace limits]], [[PY-R003 - Control Memory and Effects]], [[20 - Python Numeric Contract]], [[30 - State Simulator and HLS Blueprint]]. The presentation uses a smaller independent illustration of the branch rule.

**Boundary:** The scaled values and miniature queue transitions illustrate expected behavior; they are not results from an implemented Python Spatial compiler. The small arithmetic values do not exercise overflow. The queue controls operate on nonempty queues; blocking and scheduling are outside this illustration. The full E3 case and advanced concurrency contract remain in the linked research.

## Slide 6 — Research and documentation

**On screen:** “Research and documentation.” The review path is **What we write → What it means → How we would build it → What supports the proposal**. A documentation preview lists the five blueprints. The status distinguishes completed studies, proposed contracts and bounded research probes from the next implementation and validation work.

**Visual action:** Open the implementation-design page for a brief documentation tour, then return to the presentation tab. The visible links also lead to examples, contracts, evidence, both repositories and this full script. The tour illustrates traceability; avoid treating page count as support coverage.

**Full speaker script, 1:15:**

> This is where the research lives. We keep the source documents in a repository, and the site publishes those same documents in a form that is easier to read.
>
> There is a path through the material. Start with a Python example. Follow the links to the rules that define it. Then open the implementation design that explains how the compiler would enforce those rules.
>
> The research now includes five implementation blueprints. We have also reviewed the original Spatial behavior and run small probes to test particular design questions. Those probes give us evidence about individual methods. They do not amount to a working Python compiler.
>
> The earlier Rust work still gives us useful examples and validation experience. The compiler we are proposing here has a Python core.
>
> *Open the implementation design page for a short tour, then return to this tab. Keep the tour to about 30 seconds.*

**Evidence:** [[00 - Python Rewrite Index]], [[00 - Implementation Design Index]], [[07 - Python Implementation Readiness Audit]], [research repository](https://github.com/davidydu/spatial-research), [documentation website](https://davidydu.github.io/spatial-research-site/).

**Boundary:** The five blueprints and probe archive are completed research artifacts. Architecture adoption, production implementation, generated C++ and vendor/RTL results are distinct later gates. Do not show historical Rust results as Python results.

## Slide 7 — One complete program through Python

**On screen:** “One complete program through Python.” Three milestones: **Accept the program**, **Explain mistakes**, and **Check the behavior**. Compare outputs with an independent reference and test changed shapes, helpers and invalid cases. Save the checked program and results. The meeting question is **Does this match the Python Spatial we want?** A separate future step is **Hardware planning and HLS**, beginning with the checked subset while the language grows.

**Visual action:** Refer back to the tiled program while following its acceptance, diagnostic and behavior checks. Keep **For approval** and the boundary between the agreed Python direction and proposed detailed design visible. Close on a program we can read, explain and test, then point to the subsequent HLS path.

**Full speaker script, 1:30:**

> The first implementation milestone should be one complete program through the system. We should be able to give the compiler this tiled program, have it check the declarations and operations, and run a reference simulation.
>
> That milestone should include errors as well as successful runs. If I use the wrong memory shape or an undefined name, the compiler should explain the problem at the right place in the source. We should save the checked program and the results so another person can reproduce the run.
>
> We should also test supported changes in shape, helper composition, memory aliases and invalid cases. That checks that we have a compiler for the subset, rather than special handling for this one listing. We would then extend the same path to reductions, more numeric types and stateful programs.
>
> Once that first subset has a defined meaning and independent tests, we can begin hardware planning and HLS for it while the rest of the language grows.
>
> What I’d like to check with you today is whether this is the Python programming model you have in mind, and whether this is the right first milestone. The pure Python direction is already agreed. The detailed compiler design and proposed changes to behavior are what we are asking to review.

**Evidence:** [[04 - Python Implementation Roadmap#Slice sequence|S0–S9 sequence]], [[04 - Python Implementation Roadmap#Dependencies and useful parallel work|Early hardware feedback]], [[D-28#Review and next action|Approval boundary]], [[40 - Package and Conformance Blueprint]].

**Boundary:** This talk does not itself grant architecture approval or authorize production implementation. First-slice success would not establish full language support or validated hardware.

## Presentation design and evidence rules

Use warm paper, serif headlines, dark readable text and muted blue accents. Give each slide one main idea and one primary diagram or example. Vividness comes from a program the audience can follow: matching source highlights, visible data movement, a preserved capture boundary, and a branch that consumes exactly one queue.

Keep the full script in speaker notes and evidence links in a sources panel. Animation explains the proposed program; it must not look like a live compiler trace. Essential claims and state labels remain readable without animation. Respect reduced-motion preferences and provide keyboard navigation.

Retain the historical presentation at `/presentation/`. The new presentation lives at `/presentation/python/`, relative to the site root. Publication and deployment verification belong in [[progress-log]] after they occur; these notes do not assert a new deployment.
