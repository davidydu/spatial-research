---
type: reference
title: "Python Spatial — professor discussion brief"
project: spatial-python
date: 2026-10-01
updated: 2026-10-22
verified: 2026-10-22
---

**Latest:** [[2026-10-28-weekly-update|Weekly update — 28 October]].

<a href="https://davidydu.github.io/spatial-research-site/presentation/python/" data-router-ignore target="_blank" rel="noopener noreferrer">Open the seven-slide presentation</a> · [[2026-10-22-python-pipeline-presentation|October 22 speaker notes and evidence]].

**The Python rewrite now takes one existing Lab 1 example through the complete experimental path to simulated RTL.** This is the starting point for the next discussion with the professor, who asked for a fully Python compiler after the earlier Python-frontend/Rust-core proposal.

The ten-minute talk follows seven steps: direction, architecture, one Lab 1 result, reusable compiler rules, what the evidence tells us, next work, and records for discussion. Compiler and HLS work are paused for this meeting.

## Python owns the compiler

**Python Spatial program → Python compiler → generated C++ → vendor HLS → RTL.**

The frontend, checker, reference engine and C++ generator are implemented in Python. There is no Rust compiler core. C++ is the generated target program; the external HLS tool turns that program into hardware. The Python reference engine provides a separate way to check what the program means.

The [[70 - Engineering Architecture Map|full architecture map]] explains how these pieces fit into the proposed system. Its checked hardware planner, transformations, artifacts and resumable execution remain broader design work. The current hardware route is a direct, sequential C++ experiment.

## One Lab 1 example clears the pipeline

The tiled-scale example loads **32 Int32 values in two tiles of 16**, multiplies them, and stores the result. With input `0…31` and scale `2`, the expected output is **`0,2,…,62`**. A second case checks Int32 overflow.

On **21 October**, both the Python reference run and generated native C++ matched independent expected results. The saved vendor project then passed **Vitis C simulation, synthesis and Verilog RTL co-simulation**. The [[2026-10-21-vitis-rtl-checkpoint|hardware checkpoint]] records production `da4d35f`; [accepted evidence at `0ac7c00`](https://github.com/davidydu/spatial-py/blob/0ac7c00/docs/evidence/task-06b-vitis.md) preserves the results and reproduction details.

This shows that the implemented Python foundation can carry a real tiled-memory program into hardware and preserve its tested behavior. It is an initial result: the sequential IP used Vitis 2025.1, a Z020 target and a 10 ns clock. It has not run on an FPGA board, has no final AXI integration, and does not establish optimized parallel performance or full Lab 1 coverage.

## The compiler rules are reusable

The example uses general rules for memory, transfers, loops, arithmetic and checking. The compiler does not recognize a lab name or substitute a hand-written solution. Helpers, branches, views and compile-time settings compose through shared compiler machinery; supported target programs use the same C++ generator.

The wider vendor checkpoint covers four kernels and nine cases, including a separately authored program accepted after the implementation was frozen. This supports the generality claim within the admitted subset. The reference engine still supports more than the hardware route, and the full compiler remains unfinished.

The [[2026-10-21-scalar-target-checkpoint|newer scalar-state and shift extension]] then passed the same vendor stages on 22 October: **12 projects and 32 cases** ([[2026-10-22-scalar-vitis-checkpoint]]). That run showed Vitis ignoring the requested one-element memory interfaces. The [[2026-10-22-scalar-interface-checkpoint|explicit interface correction]] passes locally and awaits its own vendor run.

## Next steps — 26 October

After the corrected interface batch runs, the next milestone finishes the first slice's acceptance work: public checking and preparation, native execution for students, saved-program import with full rechecking, verified program editing with rollback, faster reference execution, resumable simulation and a fresh unseen program. New lab language families follow that milestone.

**Revised 28 October:** the two representation safety checks (builder/source/import agreement and safe program editing) and fast simulation come first; then Lab 1–3 features, each tested with the original lab programs; resumable simulation and the final audit follow the labs. The AWS F2 course flow, which the professor raised last week, runs in parallel. Students and TAs are expected to use Python Spatial in about six months.

The next hardware step targets the course's AWS F2 flow with loop pipelining enabled, so measurements can answer the labs' cycle and initiation-interval questions. Removing any safety check waits for a verified hardware-plan layer. The [[04 - Python Implementation Roadmap|roadmap]] records this order; board integration and measured performance still need their own evidence.

The meeting question is how to prioritize broader language coverage and measured hardware improvements from this working starting point. The [[2026-10-21-python-progress-presentation|October 21 reference-only briefing]] remains a dated record of the earlier state.

## Useful links

[[00 - Python Rewrite Index|Research home]] · [[70 - Engineering Architecture Map|Full architecture]] · [[80 - Initial Compiler Goal|Progress and acceptance]] · [[04 - Python Implementation Roadmap|Roadmap]] · [[01 - Python Coverage Ledger|Language coverage]]

[Research site](https://davidydu.github.io/spatial-research-site/) · [Compiler repository](https://github.com/davidydu/spatial-py/tree/work/initial-reference) · [Research repository](https://github.com/davidydu/spatial-research)
