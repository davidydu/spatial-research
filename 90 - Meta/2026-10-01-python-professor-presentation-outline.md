---
type: design
title: "Spatial in Python — professor presentation and speaker notes"
project: spatial-python
date: 2026-10-01
updated: 2026-10-03
status: approved-presentation-outline
scope: "Seven-slide, ten-minute presentation of the proposed pure Python rewrite"
related:
  - "[[05 - Python Professor Brief]]"
  - "[[PY-R001 - Programming Model Study]]"
  - "[[D-27]]"
  - "[[D-28]]"
  - "[[11 - Design Refinement Iterations]]"
---

# Spatial in Python

## Purpose and authority

Answer **What would a Python rewrite of Spatial look like?** The professor knows Spatial. Start with the program and host workflow, show what the compiler owns, explain what the review changed, and ask for approval of the first implementation milestone.

David approved the seven-slide web presentation and requested this refresh after the Codex/Fable design refinement. Presentation approval is separate from architecture adoption. [[D-27]] accepts the pure Python direction; [[D-28]] remains the detailed proposal. The frontend, compiler and reference simulator are all Python, with no Rust core. The proposed checked program and first hardware plans use immutable Python records. xDSL remains optional for a specific pipeline that demonstrates a benefit.

<a href="presentation/python/index.html" data-router-ignore target="_blank" rel="noopener noreferrer">Open the refreshed Python presentation</a>. The <a href="presentation/index.html" data-router-ignore target="_blank" rel="noopener noreferrer">28 September presentation</a> remains historical at its existing route.

## Story and timing

| Slide | Headline | Main visual | Time | Elapsed |
|---|---|---|---|---|
| 1 | Spatial in Python. | Program → Python compiler → reference simulation | 0:45 | 0:45 |
| 2 | A familiar Spatial program | Exact tiled-scale source beside two tiles and two SRAM buffers | 1:45 | 2:30 |
| 3 | How you would run it | Capture → Specialize → Check → Bind inputs → Simulate → Read outputs | 1:30 | 4:00 |
| 4 | One checked program, two uses | Python source → immutable checked program → simulation or hardware planning | 1:30 | 5:30 |
| 5 | Values and state both matter | Expected scaled values beside a branch that consumes one queue | 1:15 | 6:45 |
| 6 | What changed after review | Three concrete findings, measured representation costs, and the documentation site | 1:45 | 8:30 |
| 7 | One complete program through Python | Read, check and simulate a composed program; then check an early transformation | 1:30 | 10:00 |

The scripts below match the webpage speaker notes. Italic paragraphs are presentation cues. Ten minutes includes brief interactions and a documentation tour; this is a delivery target, not a measured rehearsal. Use the notes and sources panels for details.

## Slide 1 — Spatial in Python.

**On screen:** Write Spatial programs in Python. Build the compiler in Python too. The opening identifies this as a proposed design for professor review. The program, semantic compiler and reference simulator are Python.

**Visual action:** Follow the program through checking to reference simulation. Keep HLS as the later destination.

**Full speaker script, 0:45:**

> After our last discussion, I worked through what a full Python rewrite would look like. The program, compiler and reference simulator would all be Python. We would keep Spatial’s explicit memories, control and parallel work.
>
> I’ll start with what someone writes and how they run it. Then I’ll show the compiler design, what changed after review, and the first implementation milestone.
>
> The Python direction is already agreed. Today I’m asking you to review this particular programming model and architecture. The compiler is still a proposal; the experiments test parts of the design.

**Evidence:** [[D-27|Accepted Python direction]], [[D-28|Proposed architecture]], [[05 - Python Professor Brief]].

**Boundary:** The working presentation and research experiments do not establish a working compiler.

## Slide 2 — A familiar Spatial program

**On screen:** The exact proposed E1 source from [[PY-R001 - Programming Model Study]], labeled as unimplemented syntax.

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

**Visual action:** Click Load, Compute and Store, then choose positions 16–31. The illustration uses inputs 1…32 and scale 2; the original E1 fixture uses 0…31 and scale 3. Both use the unchanged source above. Keep both local buffers visible.

**Full speaker script, 1:45:**

> This program reads 32 values, multiplies each by a scale, and writes the results. It works in two tiles of 16. The picture follows the same code.
>
> At the top are the input memory, the scale and the output memory. Inside the outer loop, we declare two local buffers. One holds the input tile; the other holds the result.
>
> First we load a tile. The inner loop multiplies each value. Then we store the result back to external memory and move to the next tile.
>
> We still tell the compiler about memory and control. Those annotations describe Spatial objects; ordinary Python does not allocate SRAM by running this function. The foreach loop gives the hardware planner work it can parallelize. It does not promise sixteen hardware lanes or a particular cycle count.
>
> For this illustration, the inputs are one through 32 and the scale is two. The expected outputs are two through 64. This is an animation of the intended behavior, not a compiler run.
>
> *Click Load, Compute, Store, then choose the second tile.*

**Evidence:** [[PY-R001 - Programming Model Study#E1: two proposed spellings of tiled scale]], [[PY-E001 - Initial Example Corpus]]. Original source: `spatial@e7a8f2f:test/spatial/tests/ee109/Lab1Part2DramSramExample.scala:6-43`.

**Boundary:** The animation illustrates intended behavior. It is not a compiler run or hardware cycle measurement. foreach does not promise sixteen hardware lanes.

## Slide 3 — How you would run it

**On screen:** The source panel on Slide 2 is labeled `lab1.py`, matching the host example. Six selectable stages expose the public API proposed in [[PY-R016 - Source and Host Workflow Refinement]]. Each stage has a short explanation and an exact API fragment. Imports and storage constructors are in the linked complete example. The source stays text; capture does not import or execute the kernel.

**Visual action:** Click Check to show the error guard, Bind inputs to show typed storage views, and Read outputs to show the Completed guard and output snapshot. Open the complete host example only if asked for details.

**Full speaker script, 1:30:**

> Here is how someone would run that program. Ordinary Python controls the experiment. The kernel stays in a source file that the compiler reads as text.
>
> First we capture the source and choose any compile-time parameters. Then we check the program. A checking error stops the workflow and gives us diagnostics.
>
> Next we bind typed inputs and an output buffer. The preparation step checks that their shapes and access permissions match the program. Then we run the Python reference simulator.
>
> We read results only after the run reports Completed. A fault gives us diagnostics to inspect. A wait or an exhausted budget can give us a continuation to resume. None of those is a successful output.
>
> The research now specifies these public names and a complete host example. The snippets here show that proposed API; there is no installed Spatial package behind these buttons.
>
> *Click Check, Bind inputs, then Read outputs. The complete example is linked below.*

**Evidence:** [[PY-R016 - Source and Host Workflow Refinement]], [[40 - Package and Conformance Blueprint]], [[10 - Source Checker and IR Blueprint]].

**Boundary:** These fragments explain a proposed API. They are not a runnable installed package or a recorded successful run. Reading the host output backing is not the result API; complete_outputs owns successful snapshots.

## Slide 4 — One checked program, two uses

**On screen:** A shared checked description retains types, memories, control and effects in compiler-owned immutable Python records. One branch runs the reference simulator; the other derives a checked hardware plan. The first plan representation also uses Python records. xDSL is optional for a specific useful backend pipeline.

**Visual action:** Switch between Simulate in Python and Plan hardware. The second view shows target capabilities, checked plan, Python plan execution and checks, then HLS and hardware validation.

**Full speaker script, 1:30:**

> The central object is a checked description of the Spatial program. It records the types, memories, control and order of effects in immutable Python records.
>
> Both the reference simulator and hardware planner start from that same program. The simulator tells us what it does. The planner chooses a hardware implementation and must show that it preserves the program’s meaning.
>
> We compared keeping this representation in our own Python records with using xDSL. We now recommend our own records for both the checked program and the first hardware plans. We already have to own the Spatial rules and checks, and this makes ownership direct.
>
> xDSL remains an option when a specific backend pipeline gives us a measured benefit. We do not need it to define the language.
>
> HLS comes after the checked hardware plan. It does not get to decide what our Python program means.
>
> *Switch between Simulate in Python and Plan hardware to show the two uses of the same program.*

**Evidence:** [[D-28]], [[PY-R017 - Compiler Representation Comparison]], [[30 - State Simulator and HLS Blueprint]].

**Boundary:** These are explanatory views. The representation comparison is bounded; full compiler performance, analyses and plan validation remain implementation work. A transformed candidate must be checked before use.

## Slide 5 — Values and state both matter

**On screen:** A scale slider updates four expected outputs. A separate queue example chooses A or B and consumes only that queue. A review lesson explains that the earlier numeric candidate and its test shared an incorrect assumption, so agreement alone was insufficient.

**Visual action:** Change the scale. Choose B and take one value: B loses 10 and A stays [3, 5, 7]. The queue example isolates the selected-branch rule; it does not reproduce the full E3 program.

**Full speaker script, 1:15:**

> Correctness includes both values and changes to state. The scale example gives us a simple independent expected answer. Int uses signed 32-bit wrapping arithmetic, so we must test that rule as well as these small values.
>
> The queue example shows why effect order matters. If a branch chooses B, it takes one value from B and leaves A alone. Evaluating both branches first would already change the wrong queue.
>
> The review also found a real weakness in our earlier numeric experiment. The candidate and its comparison check shared the same incorrect underflow assumption. They agreed, but that agreement did not prove correctness.
>
> We repaired the rule and used a separately derived status check. That is why the implementation plan calls for independent expected values and state traces.
>
> *Change the scale. Choose B and take a value. Keep the numerical-boundary details in the sources panel.*

**Evidence:** [[20 - Python Numeric Contract]], [[PY-R003 - Control Memory and Effects]], [[PY-R015 - Numeric Status Repair and Independent Oracles]], [[00 - Python Validation Plan]].

**Boundary:** These small numbers do not exercise overflow, and nonempty queues do not illustrate blocking or scheduling. The repaired research probe is not an implemented numeric compiler library.

## Slide 6 — What changed after review

**On screen:** Independent expectations; a complete host run with failure handling; and a comparison of compiler representations. The chart shows build plus bounded checks for a 100,000-operation branching graph: Python records 0.375 s and xDSL 4.559 s, both p95. The caveat states that this is not a full compiler benchmark and further indices, analyses and transformations need testing.

**Visual action:** Open the review and evidence page for a short tour. Follow one finding to its study, point out the research repository, and return. Keep the tour around 20–30 seconds. Links also expose the site repository, implementation blueprints and full speaker script.

**Full speaker script, 1:45:**

> We did three rounds of Codex and Fable review, with small experiments to check the claims. The useful result is what changed, not how many reviewers agreed.
>
> First, we repaired the numeric status rule and separated its expected answer from the candidate. Second, we completed the host workflow and made stopping, resuming and output completion explicit. Third, we compared the two compiler representations.
>
> This chart shows one bounded 100,000-operation workload. Building and checking the records took about 0.38 seconds at the 95th percentile, compared with about 4.56 seconds for xDSL. The full study includes another graph shape, snapshot and rewrite costs, and memory use.
>
> This is not a measurement of a full Spatial compiler. xDSL maintains use lists and does extra structural checking; our record prototype does not yet do that work. We still need real analyses and harder transformations. Our recommendation comes from the ownership design as well as these measurements.
>
> Everything is in the research repository, and the website connects the examples, decisions and evidence. I can open the review page here and follow a finding back to its study or reproducible check.
>
> *Open the review and evidence page for a short tour. Show the repository link, then return to this slide.*

**Evidence:** [[11 - Design Refinement Iterations]], [[PY-R015 - Numeric Status Repair and Independent Oracles]], [[PY-R016 - Source and Host Workflow Refinement]], [[PY-R017 - Compiler Representation Comparison]], [research repository](https://github.com/davidydu/spatial-research), [site repository](https://github.com/davidydu/spatial-research-site).

**Boundary:** The three review rounds provide findings, not a proof by reviewer agreement. The chart rounds R017 values 0.37512925 and 4.5589 seconds. Both implementations ran the stated workload; xDSL supplies extra structural checking and indices absent from the custom prototype. Ownership and measured costs jointly inform the choice. Historical Rust results remain separate.

## Slide 7 — One complete program through Python

**On screen:** Accept a composed memory program, explain errors, compare behavior with independent expectations and save reproducible inputs/results. Vary shapes, helpers and aliases and test an early rewrite. The meeting asks: Approve this model and first milestone? The later path is checked plan → plan execution → HLS.

**Visual action:** Refer back to the tiled program, then point to the checks on composition and transformations. Close by asking for approval of the programming model, shared checked-program architecture and first complete milestone.

**Full speaker script, 1:30:**

> If this programming model and architecture look right, the next step is one complete path through Python: read a composed memory program, check it, simulate it and return a reproducible result.
>
> We should test errors at the same time. A wrong shape or invalid name should produce a useful diagnostic. A fault or unfinished run should never look like a successful output.
>
> We should also change the program. Use different shapes, helpers and aliases, and try an early transformation that duplicates a helper or expands a short loop. Check that results, effects and storage identities are still right. That tests the compiler structure before we build many features on top of it.
>
> Once that subset works, we can build and execute its hardware plan, then lower it to HLS while the rest of the language grows. Broader numeric and communication support has its own later gates.
>
> What I’m asking you to approve is this programming model, the shared checked-program architecture, and that first complete milestone. The choice of Python itself is already settled.

**Evidence:** [[04 - Python Implementation Roadmap]], [[40 - Package and Conformance Blueprint]], [[D-28#Review and next action]].

**Boundary:** The pure Python direction is agreed. The detailed design and semantic changes remain proposed; refreshing or presenting this deck does not grant approval or start production implementation. First-slice success would not establish full language or hardware support.

## Presentation design and evidence rules

Keep the existing warm paper, serif headlines, readable dark text and muted blue. Each slide has one main idea. Use movement to explain data flow and state, and selectable diagrams to reveal detail without filling the screen.

Speaker notes contain the verbal script. The source panel links to the research behind each claim. Label proposed APIs, illustrative animation and bounded measurements where they appear. Preserve keyboard navigation, reduced-motion behavior and the historical `/presentation/` route.

Publication and verification are recorded in [[progress-log]] after they occur. The refreshed presentation remains at `/presentation/python/`.
