---
type: reference
title: "Python Spatial — first pipeline result, 22 October 2026"
project: spatial-python
date: 2026-10-22
verified: 2026-10-22
scope: "Seven slides on the fully Python compiler and one Lab 1 example through RTL simulation"
---

# Python Spatial: a first working path to RTL

[Open the presentation](https://davidydu.github.io/spatial-research-site/presentation/python/) · [[05 - Python Professor Brief|Short professor brief]] · [[80 - Initial Compiler Goal|Current implementation progress]] · [[70 - Engineering Architecture Map|Full architecture]].

Seven slides, about ten minutes before discussion. This follows the professor's request to move from a Python frontend with a Rust compiler to a compiler implemented entirely in Python. Python owns source processing, checking, reference execution and C++ generation. C++ is generated target code for vendor HLS.

**Meeting scope:** one existing Lab 1 tiled-scale example has passed reference execution, native C++, Vitis C simulation, synthesis and RTL co-simulation. That is the first working path, not full Spatial support or an optimized accelerator. All compiler and hardware results shown are saved results from 21 October. No compiler or vendor execution was performed while preparing this presentation.

**Pause:** compiler and HLS work are paused at David's request. The prepared scalar/shift batch remains pending vendor validation. Resume implementation only when he asks; ask before restarting or using the stopped HLS host.

The October 21 [[2026-10-21-python-progress-presentation|reference-only presentation record]] remains historical. The current deck and this script replace its meeting narrative. The main talk does not need a source-code walkthrough or another discussion of why HLS is the target.

## Story and timing

| Slide | Headline | Time | Elapsed |
|---|---|---|---|
| 1 | Python Spatial reaches RTL simulation | 1:15 | 1:15 |
| 2 | What the Python version looks like | 1:30 | 2:45 |
| 3 | One Lab 1 example clears the pipeline | 1:45 | 4:30 |
| 4 | The compiler uses reusable language rules | 1:15 | 5:45 |
| 5 | What this first result establishes | 1:30 | 7:15 |
| 6 | Next steps | 1:30 | 8:45 |
| 7 | A working pipeline to build on | 1:15 | 10:00 |

This is a pacing target, not a measured rehearsal. Pause on the compiler pipeline and Lab 1 result. Keep the full Excalidraw map and detailed evidence for questions.

## 1. Python Spatial reaches RTL simulation · 1:15

Since our last meeting, I changed the implementation from a Python frontend with a Rust compiler to a compiler written entirely in Python. That follows the direction we discussed. The Python compiler now generates C++, and that C++ has gone through Vitis HLS to RTL simulation.

The result I want to focus on is one small Lab 1 example. It loads values, works on them in local memory, and writes the results back. Both the ordinary and overflow cases pass through the complete path. This is an initial success, rather than completion of the rewrite. I’ll show the shape of the system, what this example establishes, and what I would build on next.

## 2. What the Python version looks like · 1:30

This is the main structure. A Spatial program is written in a defined Python subset. The Python compiler parses and checks it, then represents its operations in a structured program. From there, the current backend emits a sequential C++ program. Vitis handles C simulation, synthesis and RTL co-simulation.

There is also a Python reference engine beside that path. It runs the same program under Spatial’s arithmetic, memory and ordering rules, so we have a behavior check before the target runs. There is no Rust core in this implementation. The larger architecture map is still useful for orientation, but it includes work we have not built. The solid path here is the part demonstrated by the saved result.

## 3. One Lab 1 example clears the pipeline · 1:45

The example is deliberately small. There are thirty-two Int32 values, split into two tiles of sixteen. Each tile is loaded from DRAM into SRAM, multiplied by two, and stored back. With ordinary inputs zero through thirty-one, the answers are zero, two, four, up to sixty-two.

The second case includes integer boundary values. Those results must follow Int32 wraparound, including the negative result shown here. Both cases match independently written literal expectations. They passed Python reference execution, native C++, Vitis C simulation, synthesis and RTL simulation. These are saved results from twenty-one October. This establishes the first complete path for this example; we have not run it on a board, and it does not cover all of Lab 1.

## 4. The compiler uses reusable language rules · 1:15

The important question beyond this example is whether the compiler can handle another combination of the same language features. The implementation has rules for memory operations, control, helpers and compile-time configuration. It selects those rules from the operations in a program, rather than recognizing a lab or kernel name.

The broader saved hardware checkpoint covers four kernels and nine cases. It includes a composition written independently after the compiler was frozen, which passed without changing that frozen implementation. That gives some evidence that the path is reusable. It is still a small set. The reference implementation supports more features than the current C++ target, so I am not claiming that every working Python program already reaches hardware.

## 5. What this first result establishes · 1:30

I would separate the progress into three parts. First, we have demonstrated a bounded Python-to-C++-to-RTL path. Second, there is newer local work on scalar output and input-output cells, shifts, sums, dot products and ordered state. That batch covers twelve projects and thirty-two cases, but it has not gone through Vitis yet.

Third, the larger goals remain open: full language coverage, useful parallel performance, and board integration. The source and installed-package suites each passed thirteen hundred and twenty-nine tests on twenty-one October. Those tests help protect the implementation, but the hardware claim comes from the specific vendor runs. I want to keep that distinction clear when deciding what result to pursue next.

## 6. Next steps · 1:30

The immediate next step after this meeting is to run the prepared state and shift batch through HLS. That connects the newer local results back to the hardware path we already have.

For language coverage, the labs give us a concrete sequence. Lab 1 brings more state and reduction patterns. Lab 2 adds richer memory and control. Lab 3 brings buffers and convolution. At each step I want a general language rule, a new composition, and checks through reference execution, C++ and RTL. Alongside that, we should measure storage and scheduling costs and use those results to choose improvements. The current sequential implementation is a starting point for that work; useful parallel performance and the complete public workflow still need attention.

## 7. A working pipeline to build on · 1:15

The main takeaway is that the pure Python direction now has an initial hardware result. We can start with a small Spatial program, compile it to C++, and check its RTL behavior against expected answers. The Lab 1 example is the clearest way to show that progress.

I would build on it by broadening Lab 1 coverage and using hardware results to guide the compiler work. The prepared state and shift batch is the next concrete step. After that, I would like your input on which missing Lab 1 capability matters most. The links here lead to the architecture, dated progress, both repositories and the speaking script, so we can inspect any part that would help the discussion.

## Evidence to open during questions

- [Combined saved pipeline record](https://davidydu.github.io/spatial-research-site/presentation/python/assets/meeting-pipeline-record.json): outputs, expected answers, stage results, revisions and source-file hashes.
- [Exact Lab 1 RTL co-simulation report](https://davidydu.github.io/spatial-research-site/presentation/python/assets/lab1-rtl-cosim.rpt) and [RTL post-check excerpt](https://davidydu.github.io/spatial-research-site/presentation/python/assets/lab1-rtl-postcheck.txt): both ordinary and overflow cases pass after RTL execution.
- [Small Python source](https://davidydu.github.io/spatial-research-site/presentation/python/assets/lab1-pipeline-source.py), available for questions rather than a main-slide walkthrough.
- [Frozen vendor acceptance](https://github.com/davidydu/spatial-py/blob/0ac7c00/docs/evidence/task-06b-vitis.md): the wider result is four kernels and nine cases, including a new independent composition that passed after production freeze without repair. The first unsupported shift candidate remains negative evidence for that checkpoint.
- [[2026-10-21-scalar-target-checkpoint|Newer local scalar and shift result]]: 12 prepared projects and 32 cases; vendor execution remains pending. The 1,329 source and 1,329 installed-package test results are dated 21 October and do not establish hardware coverage.
- [Compiler repository](https://github.com/davidydu/spatial-py/tree/work/initial-reference) and [research repository](https://github.com/davidydu/spatial-research).

## Short answers for discussion

**Is the compiler now fully Python?** Yes, for the implemented subset: frontend, checking, reference execution and C++ generation are implemented in Python. There is no Rust compiler core. Vendor HLS consumes the generated C++.

**Does this mean ordinary Python runs on the FPGA?** The source uses a defined Spatial subset in Python syntax. The compiler gives its arithmetic, memory and control explicit rules. It does not compile arbitrary Python or run the Python interpreter in hardware.

**Why is one example useful?** It connects the language rules to generated C++, HLS and simulated RTL, with independent expected answers at each execution stage. It gives us a concrete starting point for adding reusable features and measuring hardware cost.

**What is the limit of that result?** It is a small sequential experimental IP. Board execution, AXI integration, routed timing, useful parallel performance and full language coverage remain open. Reference execution supports more than the current C++ target. The full architecture map includes a checked hardware planner that is not yet implemented.

**What comes next?** After work resumes, validate the prepared scalar/shift batch with vendor tools, then use size/tile measurements to choose a general storage or scheduling improvement. Continue language coverage from Labs 1–3, with unfamiliar feature combinations at each step. The public workflow and real resumption also remain unfinished.

## Review record — 22 October 2026

This is presentation verification using saved evidence, not a new compiler acceptance run.

- Read-only review checked the exact Lab 1 source, generated kernel and manifest hashes against the saved vendor bundle; native and reference outputs separately match independent expectations.
- Both Lab 1 case markers occur in the C post-check after RTL execution, followed by the two-case pass marker and the C/RTL co-simulation PASS. The copied report is byte-for-byte identical to the saved report.
- The slide output selector reads the same saved record linked above. The standalone script is extracted from the seven embedded speaker-note sections so its spoken wording agrees with the presentation.
- Layout, interactive controls, documentation build and publication are recorded in the shared progress log and compiler project-state publication record after review.
