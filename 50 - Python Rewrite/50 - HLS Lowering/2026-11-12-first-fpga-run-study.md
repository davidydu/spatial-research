---
type: implementation-checkpoint
title: "First run on the FPGA: Lab 1 from Python Spatial, and the path to handwritten-HLS speed"
project: spatial-python
date: 2026-11-12
status: experiment-one-program
---

**A Lab 1 program written in Python Spatial ran correctly on the AWS F2 FPGA on the evening of 11 November 2026,
Pacific time (12 November UTC). It is the project's first run on real hardware. It takes about 260 clock cycles
where the course's handwritten HLS takes about 58. This page records the case in full, shows where the cycles go, and sets out what it would take to reach
the handwritten design's speed.**

## Summary

- **What ran.** Lab 1's tiled scale (32 numbers, each multiplied by 5) was compiled from Python Spatial and taken
  through the same `make` steps students use, on an F2 instance with the newest AWS image.
- **Result.** It returned the right 32 values and a clean status in all six runs on the chip.
- **Baseline and target (David, 12 November).** Today's count is our baseline: 256 to 260 cycles in four runs and
  about 350 in two (median 260). The target is the staff's handwritten HLS measured on the same chip, 58 to 62
  cycles.
- **Why it is slower.** Not the arithmetic: both designs multiply sixteen numbers at once. Ours makes six separate
  trips to memory where the handwritten design makes two, and it spends 34 cycles on a final check that could take
  one.
- **Can it reach the target?** Probably yes for this case. Four changes, listed below, would bring the estimate
  from about 260 to between 60 and 70. Passing the handwritten design is realistic only on larger programs, and is unproven.
- **Limits.** One program, one test case, a hand-adapted wrapper, no tuning. This is an experiment, not an
  acceptance claim.

![Dot plot of compute cycles on the FPGA: handwritten HLS 58 to 62 cycles, Python Spatial 256 to 354 with a median of 260](<50 - Python Rewrite/50 - HLS Lowering/assets/2026-11-12-f2-runs.svg>)

![Timeline of one run: Python Spatial makes four copy-in transfers, runs the kernel and makes two copy-out transfers in about 260 cycles; the handwritten design is one pipeline of 58 cycles](<50 - Python Rewrite/50 - HLS Lowering/assets/2026-11-12-f2-timeline.svg>)

## What was compared

The course's Lab 1 has two halves, and the comparison only makes sense with both in view.

| Version of Lab 1's DRAM and SRAM part | Who wrote it | Where it runs | Cycles |
|---|---|---|---|
| Original Spatial (Scala) | Students, from the staff example | Simulation only; it never reaches the F2 chip | 556 simulated cycles, from original Spatial's Scala simulation (David's Spring 2026 run) |
| Handwritten Vitis HLS C++ | Course staff, converting the Spatial exercise by hand (the file starts from a Xilinx example) | The F2 chip | 58 to 62 (this experiment) |
| Python Spatial | Compiled by this project | The F2 chip | 256 to 354, median 260 (this experiment) |

- The course handout for the FPGA half says: "all the Spatial exercises have already been converted to C/C++ HLS
  for you". That hand translation is our control. **The 58 is not original Spatial's performance.**
- **The 556 is an estimate, not a measurement.** Original Spatial's Scala simulator adds up a modelled delay for
  each step of the program: 238 cycles for the two loads from off-chip memory, 54 for the multiplications, 242 for
  the two stores, and 22 of control overhead. No real memory or chip is involved, and a note in the course
  handout's source says cycle accuracy needs the other (VCS) simulation. It also multiplies one element per cycle,
  where both FPGA designs multiply sixteen at once. So it cannot be set beside the two FPGA counts. It does agree
  with them on one point: memory transfers are most of the time (480 of the 556 cycles).
- The handwritten count on the chip is not a constant either: David's Spring 2026 submission recorded 105 cycles
  for the same example, on the class instance under the 2024.1 tools. Its simulation count barely moved (78 then,
  77 now).

## The program

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

It reads 32 numbers from off-chip memory in two tiles of 16, multiplies each by `scale`, and writes the 32 results
back. This is the same task as the course's `Lab1Part2DramSramExample`.

## What the compiler generated

Three files, used byte for byte as the compiler wrote them. Two matter here; the third, `interface.hpp`, only
defines the 512-bit memory word.

- **`kernel.cpp`, the checked kernel.** Every memory access is checked for bounds and for reading a value that was
  never written. A failed check stops the kernel and reports a fault code and the number of the failing operation.
  The handwritten design has no such checks.
- **`wrapper.cpp`, the "staged" top.** It copies every array from off-chip memory into on-chip storage, calls the
  kernel, then copies the outputs back. Each array travels with a second array of "initialized" flags, one 32-bit
  word per element. Memory is read and written in 512-bit words, sixteen numbers at a time.

The top's control registers sit behind a 7-bit address: the addresses of `src`, its flags, `dst` and its flags
(0x10, 0x1c, 0x30, 0x3c), `scale` (0x28), and the status with its valid bit (0x48, 0x50).

## Which piece is which

A design on the F2 instance has four pieces. Only the last is generated today.

![Diagram of the four pieces: the host program on the instance CPU, and the AWS shell, the wrapper and the kernel on the FPGA, with off-chip memory attached to the wrapper](<50 - Python Rewrite/50 - HLS Lowering/assets/2026-11-12-f2-pieces.svg>)

| Piece | What it does | Where it runs | In this experiment |
|---|---|---|---|
| Host program | Fills memory with the inputs, writes the control registers, writes "start", then reads the results back and checks them | The instance's CPU | Written by hand for this test |
| Shell | AWS's fixed logic: the link to the CPU and the memory controller | The FPGA | AWS's, unchanged |
| Wrapper (`design_top.sv`) | Glue between the shell and the kernel: passes register writes to the kernel, catches the "start" write, connects the kernel to memory, counts cycles | The FPGA | The course's file with three edits |
| Kernel | The computation | The FPGA | Generated from Python Spatial |

- In the course, staff write the host program, the wrapper and the kernel by hand for each lab part. The wrapper
  names its kernel's ports and the host program holds its register addresses, so both differ between parts.
- In original Spatial the compiler produced all of it from one source file: code inside `Accel` became hardware,
  code outside it became the host program, and a library (Fringe) played the wrapper's role for each board.
- The generated file named `wrapper.cpp` is part of the kernel. It is not the wrapper in this table.

**Decision (David, 12 November):** the compiler should generate the wrapper and the host program for each design, as
original Spatial did. Not started.

## The machine and the flow

- **Machine:** an AWS f2.6xlarge (one VU47P FPGA, 24 vCPUs, 249 GB memory) with the newest AWS FPGA Developer image,
  1.19.2: Ubuntu 24.04.1, Vivado and Vitis 2025.2.
- **Kit:** `aws-fpga` at the class's pinned tag `v2.3.0`. It set up cleanly on the newer tools.
- **Control:** the course's `Lab1Part2DramSramExample`, unchanged, run beside ours on the same machine.

![Diagram of the flow: Python Spatial source, compiler and checker, generated C++, then gen_rtl, hw_sim, fpga_build, the AWS image and the run on the chip, each passed](<50 - Python Rewrite/50 - HLS Lowering/assets/2026-11-12-f2-flow.svg>)

| Step (`make` target) | What it does | Handwritten HLS | Python Spatial |
|---|---|---|---|
| `gen_rtl` | Vitis HLS turns the C++ into Verilog | Passed; estimated Fmax 456.62 MHz | Passed; estimated Fmax 456.62 MHz |
| `hw_sim` | Simulates the design inside a model of the F2 shell and its memory | **Passed**, 77 compute cycles | **Passed**, 294 compute cycles |
| `fpga_build` | Vivado places and routes the design for the chip | Timing met for the whole image (worst slack +0.106 ns); about 32 minutes | Timing met for the whole image (worst slack +0.308 ns); about 30 minutes |
| AFI registration | AWS turns the build into a loadable image | Loadable about 20 minutes after registration | Loadable about 20 minutes after registration |
| `program_fpga`, `run_fpga_test` | Loads the image and runs the host test on the chip | **Passed** six times | **Passed** six times |

Notes on this table:
- **Clock.** Vitis HLS was asked for a 3 ns clock. The F2 shell runs the design on its 4 ns main clock (250 MHz),
  so one cycle is 4 ns and 260 cycles is about one microsecond.
- **Slack** is for the whole image, AWS's shell included, so it does not compare the two designs. The worst path
  of the handwritten build is inside the shell's memory controller; ours is in the shell's protected logic.
- **Fmax** is the same line in both HLS logs. We did not look into why.
- **Build times** and the 20 minutes were noted at the time; their logs were not saved.

## How the course files were adapted

Our copy of the lab folder differs from the course's in four places:

1. `src/` holds the generated `wrapper.cpp`, `kernel.cpp` and `interface.hpp` in place of the handwritten `vadd.cpp`.
2. `synth.py` names `wrapper.cpp` and adds `-std=c++17`.
3. The course wrapper `design_top.sv` gets three small edits:
   - the control address is 7 bits wide instead of 6, because our top has more registers;
   - the start-register match compares the whole address, since a 6-bit compare would also match 0x40;
   - the two separate scalar ports are removed, because our scalar goes through the control registers.
4. The simulation test and the host program are our own, written to print the cycle counters in the course's form.

The course wrapper is under the Amazon Software License, so it is edited on the build machine by a script and never
copied into our repository.

## The test and the result on the chip

- **Input** (the course test's data): `src[i] = i + 1`, `scale = 5`, every `src` flag set. `dst` starts filled with
  the marker `a5a5a5a5` and no flag set.
- **Expected:** a valid status with fault 0, `dst[i] = 5 × (i + 1)`, and every `dst` flag equal to 1.
- **Each run loads the image again**, because the wrapper's cycle counters reset only on a load.

| Run, in order | Handwritten HLS | Python Spatial |
|---|---|---|
| 1 | Passed, 62 cycles | Passed, 349 cycles |
| 2 | Passed, 58 | Passed, 354 |
| 3 | Passed, 58 | Passed, 256 |
| 4 | Passed, 58 | Passed, 260 |
| 5 | Passed, 58 | Passed, 260 |
| 6 | Passed, 62 | Passed, 260 |
| **Median** | **58** | **260** |

- **A pass is not empty.** Each design's host program passes on its own image and fails on the other's (33 and 32
  mismatches).
- **The counts vary between loads, and ours fall into two groups.** The first two runs took about 350 cycles and
  the next four 256 to 260. The handwritten design varied by 4. We did not investigate, and the cause is unknown.
- The generated C++ was not changed at any point between the compiler and the chip.

## What this does and does not show

It shows that a program written in Python Spatial can go through the class's own flow, on the class's kind of
machine, compute correctly on the FPGA and report a clean status.

It does not show:
- that other programs work (one program, one test case, and no case that should report a fault);
- that the flow is ready for students (the wrapper was adapted by hand, and the image registration ran outside the
  instance);
- anything about tuned performance (nothing was optimized);
- that the known Vitis HLS loop bug is avoided. The generated loops still have the early-exit form that triggers
  it. Lab 1 passes anyway, as it did in co-simulation under 2025.1. The single-exit fix is written and reviewed on
  a branch, not yet merged, and waiting for its hardware run.

## Where the 260 cycles go

**What the counter measures.** "Compute cycles" are the clock cycles from the kernel's start to its done signal.
They include the kernel's own memory reads and writes.

**Both designs are sixteen wide.** The HLS logs show both reading and writing 512-bit words and both with the
16-step inner loop fully unrolled, so sixteen multiplies happen at once in each. The gap is not in the arithmetic.

**The synthesis estimate.** Vitis HLS estimates 129 cycles for our top when memory answers at once (the report is
from the 2025.1 run of the same sources; the 2025.2 log shows the same loops with the same depths):

| Part | Cycles | What it is |
|---|---|---|
| Four copy-in loops | 19 | `src` data, `src` flags, `dst` data, `dst` flags |
| Tile loop | 7 | The actual work: two tiles, sixteen multiplies each |
| Output-completion check | 34 | A loop that confirms all 32 outputs were written, one flag per cycle |
| Other kernel steps | 4 | |
| Two copy-out loops | 8 | `dst` data, `dst` flags |
| Rest of the top | 57 | Starting and finishing the six memory transfers (inferred) |
| **Total** | **129** | |

**On the chip.** The median run takes 131 cycles more than the estimate. Inferred, not measured: that excess is the
time memory takes to answer. Together with the 57 above, it puts each of the six memory transfers at about 31
cycles. The two slow runs took about 90 cycles more again, which this does not explain.

| Share of the 260 cycles (estimate) | Cycles | Share |
|---|---|---|
| Six memory transfers, waiting and handshakes | 188 | 72% |
| Output-completion check | 34 | 13% |
| Copy loops | 27 | 10% |
| The multiplication itself | 7 | 3% |
| Other | 4 | 2% |

**How far to trust this.** The same model predicts about 70 cycles for the handwritten design (two transfers and a
6-deep loop). It measured 58 to 62, which read the other way implies about 26 cycles per transfer. So the model is rough,
within about 20 per cent: good enough to rank the
problems, not to promise numbers. A waveform of one run would settle it.

## Problems and possible solutions

None of these is started. "Decision" marks changes to choices David confirmed for the first F2 bundle (staged
copies, and flags as one word per element).

| # | Problem | Evidence | Possible solution | What it needs |
|---|---|---|---|---|
| 1 | **Six memory transfers instead of two.** Each two-word transfer costs about 25 to 31 cycles (inferred) | Six bursts in the HLS log; the budget above | Solutions 3 and 4 below remove four of them | See 3 and 4 |
| 2 | **The completion check takes one cycle per output.** 34 cycles here; at 1,024 outputs it would take over 1,000 (extrapolated) | The synthesis report: a 32-trip loop at one cycle each | Check all flags in one step | A change to generated code only; no change of meaning |
| 3 | **`dst` is read before it is written.** The wrapper reads `dst` and its flags in (two transfers), so values the kernel does not overwrite survive | Two of the four copy-in loops | Skip the read when the compiler can see the kernel overwrites every element, as here; otherwise read only the part that is needed | Decision (changes the staged copy). Meaning is unchanged on runs without a fault. After a fault, unwritten values must still survive, so the write-back must then cover only written words or be preceded by a read |
| 4 | **Flags travel as full arrays.** One 32-bit word per element, for every array, in and out | Three of the six transfers carry only flags: `src` flags in, `dst` flags in, `dst` flags out | Pack flags as one bit each; or let the host declare "this whole input is initialized" in a control register, and report "all outputs written" in the status | Decision (changes the flag layout the host sees) |
| 5 | **The phases do not overlap.** Copy everything in, then compute, then copy everything out. The handwritten design reads, multiplies and writes in one pipeline | The top is a sequence of separate loops | Let `load` and `store` read and write off-chip memory directly inside the tile loop | Decision (replaces the staged copy for these transfers); a design review |
| 6 | **Staging does not scale.** Whole off-chip arrays are copied into on-chip registers, which only works for small arrays | The HLS log: the on-chip copies of `src` and `dst` are split completely into registers | The same change as 5 | As 5 |
| 7 | **Parallelism is an accident here.** `foreach` accepts a parallelism factor and the checker records it, but the generator only writes it as a comment. Vitis pipelined the short outer loop on its own, which unrolls the 16-step loop inside it | `kernel.cpp`: "requested foreach parallelism: 1"; the HLS log: automatic unrolling | Emit the requested factor as explicit unrolling and memory partitioning | A generated-code change with a design review |
| 8 | **Repeated and run-time checks in the generated code.** Each access is guarded two or three times. Vitis removes the guards whose bounds are constants. The checks on run-time flags remain as early exits, the loop form behind the Vitis bug | `kernel.cpp` | Single-exit loops (written and reviewed, waiting for hardware); emit each check once; drop checks the checker already proves | The first is approved; the others are generated-code changes |
| 9 | **The on-chip count is not stable.** 256 to 354 for the same image, in two groups. Separately, the same handwritten example measured 105 in Spring: one run, on another instance, with older tools | The run table; David's Spring submission | A fixed protocol: report the simulation count and the median of at least five loads | Agreement only |
| 10 | **The evidence is thin.** One program; the control's synthesis report and both designs' final utilization were not saved | This page | Save them at the next instance start; add a second program when FIFO lands | An hour of instance time |

## Can it reach or pass the handwritten design?

![Bar chart of the estimated path: 260 cycles today, then about 225, 155, 85 and 60 to 70, against 58 for the handwritten design](<50 - Python Rewrite/50 - HLS Lowering/assets/2026-11-12-f2-path.svg>)

**Reach it: probably yes for this case.** Applying the solutions in order, with the rough model above (estimates to
be measured, for the median run without a fault):

| After | Estimated cycles on the chip | Against the handwritten 58 |
|---|---|---|
| Today | 260 | 4.5 times |
| 2. Completion check in one step | about 225 | 3.9 times |
| 3. No read of `dst` (removes `dst` data in and `dst` flags in) | about 155 | 2.7 times |
| 4. No flag transfers for fully initialized arrays (removes `src` flags in and `dst` flags out) | about 85 | 1.5 times |
| 5. Reading and writing inside the tile loop | about 60 to 70 | about equal |

At that point the two designs would do the same thing: one read, sixteen multiplies per tile, one write. What is
left is the time memory takes to answer, which no compiler removes.

**Pass it: not on this case.** The handwritten design is already at that floor. A compiler could shave a few cycles
because it knows the array sizes when it compiles, while the handwritten code takes the size as a run-time value.
That is all.

**Pass it on larger programs: possible, unproven.**
- **For:** on larger designs, speed comes from choosing how much to unroll, how to split memories so parallel
  accesses do not collide, and how to overlap stages. A person writing HLS works these out by hand for each design.
  A compiler that knows the program's shapes and access patterns can generate them. The original Spatial paper
  reports programs 42% shorter and a mean speed-up of 2.9 times over SDAccel HLS on an AWS F1 FPGA
  ([Koeplinger et al., PLDI 2018](https://ppl.stanford.edu/papers/pldi18_koeplinger.pdf)).
- **Against:** that result came from a compiler that generated its own hardware description, with its own memory
  banking and automatic tuning. Python Spatial today emits C++ for Vitis HLS, so it can be no faster than the best
  C++ one could write for Vitis by hand. Matching careful handwritten HLS is a realistic goal. Beating it
  consistently would probably need our own hardware generation, which is a later research question.
- **What Python Spatial adds either way:** its designs are built to report bounds and initialization faults from
  the hardware. That is shown in co-simulation; no fault case has run on the chip yet. The aim is for those checks to cost logic, not cycles: a check proved when compiling is removed, and the rest run
  beside the data path.

## How to measure progress

- Report two numbers per design: the compute cycles in the shell simulation (repeatable) and the median of at
  least five loads on the chip.
- Always run the handwritten design beside ours, on the same image and the same day.
- Save the synthesis report and the routed utilization for both designs.
- Count memory transfers as well as cycles. At this size they are the cost.

## Proposed next steps

1. Run the single-exit loop fix on hardware (approved; needs the HLS host for about an hour).
2. At the next F2 instance start: save the missing reports, and capture a waveform of one run to confirm the cost
   of one memory transfer.
3. Plan problem 2 (the completion check). It is the cheapest change and changes no meaning.
4. Bring problems 3 to 6 to David as one design decision: how arrays and flags cross between the host, off-chip
   memory and the kernel.
5. Plan the generated wrapper and host program (decided 12 November). The plan must settle the licence route: the
   course's wrapper is under the Amazon Software License, so ours is either written from scratch against the kit's
   headers or produced by edits on the build machine.
6. Keep the lab features first (FIFO, then Reg). Hardware work runs beside them and must not delay them.

## Evidence

In the compiler repository `spatial-py`, branch `work/initial-reference`:

- `docs/evidence/f2-device-experiment/README.md`: results, logs for every step and every on-chip run, the test
  files and the scripts;
- `docs/evidence/f2-1-acceptance/lab1-on/`: the Python source and the generated C++;
- `docs/evidence/f2-1-acceptance-vitis/lab1-on/project/solution/syn/report/csynth.rpt`: the synthesis estimate;
- `docs/reviews/2026-11-11-ordering-decision.md`: what the course uses, and David's Spring 2026 figures.

Earlier pages: [[2026-11-11-weekly-update]] and [[2026-10-27-scalar-interface-vitis-checkpoint]].
