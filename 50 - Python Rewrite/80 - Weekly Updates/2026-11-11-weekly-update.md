---
type: weekly-update
title: "Weekly update — 11 November 2026"
project: spatial-python
date: 2026-11-11
---

**Two weeks in one update: a Lab 1 program written in Python Spatial now goes through the class's own AWS F2
flow. It passes simulation against the F2 shell and builds for the FPGA with timing met. The compiler's core
safety checks and fast simulation are finished, and along the way we found and isolated a bug in Vitis HLS.**

## What's new

**1. Python Spatial on the class's FPGA flow.** We took Lab 1's tiled scale (32 elements times 5), compiled it
from Python Spatial, and ran it through the same `make` steps students use, on an F2 instance with the newest AWS
image (Vivado and Vitis 2025.2). For comparison we ran the course's own handwritten HLS for the same lab part
beside it, on the same machine.

| Step | Course's handwritten HLS | Compiled from Python Spatial |
|---|---|---|
| HLS to RTL | Passed | Passed |
| Simulation against the F2 shell | Passed, 77 compute cycles | Passed, 294 compute cycles |
| FPGA build | Timing met, slack +0.106 ns | Timing met, slack +0.308 ns |
| Run on the chip | next | next |

- The Python Spatial design returned the right 32 values and a clean status on its first simulation.
- It takes about 3.8 times as many cycles. Most of that is memory traffic, not computing: the design makes six
  memory transfers (data and "initialized" flags, in for both arrays and out for the result) where the
  handwritten one reads one array and writes one. The synthesis report puts the computation itself at about 45
  cycles. Nothing has been tuned yet.
- The course's Lab 1 runs unchanged on the newest image through simulation and build, so the class could move to it.

**2. A Vitis HLS bug, found and reduced to about 40 lines.** A pipelined loop that can exit early, contains a
division, and is followed by more code is compiled wrongly:
- under Vitis HLS 2025.1 the hardware simulation never finishes;
- under 2025.2 it finishes with one wrong output word, and only the test bench notices.

The C simulation is correct in both. Rewriting the loop with a single exit avoids it, and our compiler will emit
every loop that way. A report for AMD is prepared.

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

- **Lab features start now:** FIFO first, then Reg, then Reduce and Fold. Lab 2 and Lab 3 features follow.
- **Target:** students and TAs use Python Spatial in April 2027.
- **Hardware in parallel:** run on the chip itself, then emit single-exit loops, then cut the memory traffic.

## Next week

- Run Lab 1 on the FPGA itself and report the on-chip cycle counts beside the handwritten version's.
- Emit single-exit loops, and re-run the hardware tests under both Vitis releases.
- Start Lab 1's FIFO.

## Questions

1. We plan to build FIFO first, then Reg, then Reduce and Fold. Is that the right order for Lab 1?
2. Our generated design needs three small edits to the course's `design_top.sv` (a wider control address, a stricter
   start-register match and no separate scalar ports). Should generated designs drop into the unmodified course wrapper, or may the wrapper be
   generated?
3. Python Spatial checks every memory access and tracks which elements are initialized, which costs cycles today
   (294 against 77). How much of the labs' speed and parallelism must the generated hardware show in the first
   release?
4. May the next iteration of the class use the newest AWS image (Vivado and Vitis 2025.2)? The course's Lab 1 flow
   ran on it unchanged.
