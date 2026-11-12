---
type: weekly-update
title: "Weekly update — 11 November 2026"
project: spatial-python
date: 2026-11-11
---

**Two weeks in one update: a Lab 1 program written in Python Spatial now goes through the class's own AWS F2
flow and runs correctly on the FPGA itself. The compiler's core
safety checks and fast simulation are finished, and along the way we found and isolated a bug in Vitis HLS.**

## What's new

**1. Python Spatial on the class's FPGA flow.** We took Lab 1's tiled scale (32 elements times 5), compiled it
from Python Spatial, and ran it through the same `make` steps students use, on an F2 instance with the newest AWS
image (Vivado and Vitis 2025.2). For comparison we ran the course's own handwritten HLS for the same lab part
beside it, on the same machine. That handwritten HLS is the staff's hand translation of the Spatial exercise, the
version the class runs on the chip. It is not output of the original Spatial compiler, which the course only
simulates. The full case, with where the cycles go and what would close the gap, is in
[[2026-11-12-first-fpga-run-study|the first-run study]] (added 12 November).

![Diagram of the flow: Python Spatial source, compiler and checker, generated C++, then gen_rtl, hw_sim, fpga_build, the AWS image and the run on the chip, each passed](<50 - Python Rewrite/50 - HLS Lowering/assets/2026-11-12-f2-flow.svg>)

| Step | Course's handwritten HLS | Compiled from Python Spatial |
|---|---|---|
| HLS to RTL | Passed | Passed |
| Simulation against the F2 shell | Passed, 77 compute cycles | Passed, 294 compute cycles |
| FPGA build | Timing met (whole image, slack +0.106 ns) | Timing met (whole image, slack +0.308 ns) |
| Run on the FPGA, six runs each | Passed, 58 to 62 compute cycles | Passed, 256 to 354 compute cycles (four runs at 256 to 260, two near 350) |

![Dot plot of compute cycles on the FPGA: handwritten HLS 58 to 62 cycles, Python Spatial 256 to 354 with a median of 260](<50 - Python Rewrite/50 - HLS Lowering/assets/2026-11-12-f2-runs.svg>)

- The Python Spatial design returned the right 32 values and a clean status on its first simulation, and again in
  every run on the chip.
- It takes about four to five times as many cycles (3.8 times in simulation, about 4.5 times on the chip). Most
  of that is memory traffic, not computing: the design makes six
  memory transfers (data and "initialized" flags, in for both arrays and out for the result) where the
  handwritten one reads one array and writes one. Both designs multiply sixteen numbers at once. In the synthesis
  estimate the kernel takes 45 cycles: 7 for the multiplication and 34 for a final check that every output was
  written. Nothing has been tuned yet.
- The course's Lab 1 runs unchanged on the newest image through simulation and build, so the class could move to it.

![Timeline of one run: Python Spatial makes four copy-in transfers, runs the kernel and makes two copy-out transfers in about 260 cycles; the handwritten design is one pipeline of 58 cycles](<50 - Python Rewrite/50 - HLS Lowering/assets/2026-11-12-f2-timeline.svg>)

**2. A Vitis HLS bug, found and reduced to about 40 lines.** A pipelined loop that can exit early, contains a
division, and is followed by more code is compiled wrongly:

| Hardware simulation of | Vitis HLS 2025.1 | Vitis HLS 2025.2 |
|---|---|---|
| The design that exposed the bug | Never finishes | Never finishes |
| The reduced 40-line example | Never finishes | Finishes with one wrong output word, which only the test bench notices |
| The same loops rewritten with a single exit | Passes | Passes |

The C simulation is correct in both. Rewriting the loop with a single exit avoids it under both releases, and our
compiler will emit every loop that way. A report for AMD is prepared. (Corrected 12 November: this item first
described the 2025.2 behaviour from the reduced example alone.)

**3. Lab 1 on the F2 chip, synthesized** (3 November, before the device flow). With pipelining on, Lab 1 takes
131 cycles instead of 1,249, and the estimated clock is 2.19 ns against a 3 ns target. Five of six test projects
passed every rule; the sixth is the one that exposed the bug above.

**4. The compiler's core safety checks are done.**
- **One meaning, three ways in.** A program gives the identical checked result whether it is written as source,
  built through a Python API or loaded from a file. A forged or damaged file is rejected.
- **Safe editing.** The compiler can rewrite a program (for example, inline a helper). The rewritten program
  must pass the same checker again, and the test program behaves as before. A failed rewrite leaves the original
  untouched. Optimizations will build on this.

**5. Fast simulation.** Lab-size inputs now run quickly in the Python reference simulator: Lab 1 at 1,024 elements
in about 35 ms, and a 32×32×32 matrix multiply and a 3×3 window over a 48×48 image both complete with outputs equal
to separately written references.

**6. Tests.** 2,406 automated tests pass, both from source and as an installed package. Each increment was also
checked by a fresh test set written separately, after its code was frozen.

## The plan

![Diagram of the plan: lab features in order (Lab 1 DRAM and SRAM done, FIFO under way, Reg, Reduce and Fold, Lab 2 and Lab 3), hardware work in parallel, target April 2027](<50 - Python Rewrite/50 - HLS Lowering/assets/2026-11-12-plan.svg>)

- **Lab features start now:** FIFO first, then Reg, then Reduce and Fold. Lab 2 and Lab 3 features follow.
- **Target:** students and TAs use Python Spatial in April 2027.
- **Hardware in parallel:** emit single-exit loops, then cut the memory traffic.
- **One source file, as in original Spatial** (decided 12 November): the compiler will also generate the hardware
  wrapper (`design_top.sv`'s role) and the host program for each design, so students write only Python Spatial. In
  this experiment both were adapted by hand: the course's wrapper needed three small edits to fit our design's
  registers and ports.

## Next week

- Emit single-exit loops, and re-run the hardware tests under both Vitis releases.
- Start Lab 1's FIFO. Its design is drafted and under independent review.

## Questions

1. We plan to build FIFO first, then Reg, then Reduce and Fold. Is that the right order for Lab 1?
2. Python Spatial checks every memory access and tracks which elements are initialized, which costs cycles today
   (about 260 cycles on the chip, against 58 for the staff's handwritten HLS). We take the handwritten HLS on the
   chip as the target and today's count as our baseline; the [[2026-11-12-first-fpga-run-study|study]] estimates
   what closing the gap takes. Is that the right target, and how much of it must the first release reach?
3. May the next iteration of the class use the newest AWS image (Vivado and Vitis 2025.2)? The course's Lab 1 flow
   ran on it unchanged.
