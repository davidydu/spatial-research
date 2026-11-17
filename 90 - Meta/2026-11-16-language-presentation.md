---
type: reference
title: "Python Spatial — the language against EE 109, 16 November 2026"
project: spatial-python
date: 2026-11-16
verified: 2026-11-16
scope: "Thirteen slides comparing every Spatial construct EE 109 teaches with its Python Spatial spelling and state, for the professor"
related:
  - "[[PY-E003 - EE109 Feature Coverage]]"
  - "[[PY-E002 - Spatial to Python Syntax Atlas]]"
  - "[[2026-11-16-compiler-efficiency-presentation]]"
---

# Python Spatial: the language against EE 109

[Open the presentation](https://davidydu.github.io/spatial-research-site/presentation/language/) · [[PY-E003 - EE109 Feature Coverage|The full comparison]] · [[2026-11-16-compiler-efficiency-presentation|The efficiency deck]]

Thirteen slides, about sixteen minutes before discussion. The professor asked for a deck on the new language's features. It takes every Spatial construct that EE 109's Spring 2026 lectures (1 to 7) and Labs 1 to 3 use, gives its Python Spatial spelling, and says whether it runs, is designed, or comes next.

**How to read the states.**
- *Runs* means from Python source, through the checker, on both reference engines, with tests on the compiler's `main`. Of the 32 constructs the labs' Spatial parts use, 17 run.
- *In review* is the FIFO observations (slice A2a): written and tested on its branch, before its reviews and merge.
- *Designed* is `Reg` (contract, fixtures and blind oracle on `work/lab1-reg`), the hardware for `par` (the reviewed SS1 plan) and `.buffer` (the compiler's job, not a language construct).
- *Next* are the twelve proposals of [[PY-E002 - Spatial to Python Syntax Atlas]]; none is started.

**What is measured and what is a prototype.** Slide 8's rows: the staff's HLS and the compiler today are measured; the two Spatial-style rows are hand-written prototypes of what SS1 will emit, measured in the course's own unmodified flow. Quote 76 / 108 / 157 for our Spatial version (not 75 / 77 / 156, the earlier fused top).

**Course material.** The Scala on slide 2 was written for the deck in public Spatial syntax; it is not the course's source.

## Where we are: The Spatial EE 109 teaches, in Python (1:15)

You asked for the language itself. This deck takes every Spatial construct EE 109 uses, from the lectures and from Labs 1 to 3, and shows its Python Spatial spelling and where it stands.

Of the 32 constructs the three labs actually use, 17 run today: from Python source, through the checker, on both of our reference simulators, which must agree. Three of Lab 1's four Spatial parts run end to end; the controllers part needs Reg, Reduce and Fold. Reg is fully designed, with its tests' expected values already derived. Twelve constructs are next, in lab order.

And on hardware: Lab 1 written the Spatial way, with Foreach over tiles and par 16 inside, and lowered the way the original Spatial compiler would, matches the staff's handwritten HLS in the course's own flow. That is a hand-written prototype of what the compiler will emit; the compiler change is planned and reviewed.

## Side by side: One program, two spellings (1:15)

Here is the program every student meets first, written both ways. The Scala on the left is my own short version of the pattern, in public Spatial syntax. On the right is the Python program our tests run.

The structure is the same line for line: a sequential loop over tiles, two SRAMs, a load, an inner Foreach, a store. Two things differ. The ports are part of the function's signature, with their direction and type, instead of DRAM and ArgIn objects declared on the host. And a transfer names its destination first, like an assignment. This one runs today everywhere we have a route: both reference simulators, native C++, and the F2 FPGA.

## Program and host: The accelerator is a typed Python function (1:00)

The host and accelerator split stays, but the accelerator is a typed Python function. Its ports are its parameters: In, Out and InOut, for scalars and for DRAM arrays. The host is ordinary Python: you check the program, prepare it with your data, run it, and get typed outputs back, instead of setArg, setMem, getArg and getMem.

Functions become helpers, declared inside the kernel with their effects stated. Sizes you want to tune, like a tile size, are meta values fixed before checking, the role scala.Int plays in the course. Every row here runs today. The F2 route generates its own control registers, so students never write the MMIO layer.

## Types: Exact integer types now; fixed point next (1:00)

Types. Int is exactly Spatial's 32-bit integer, with wrapping arithmetic. Loop counters have their own exact type, Index, and turning one into data takes an explicit embed, which can wrap or check. Bool is its own type, which is what the course already teaches. These run today.

Fixed point is next: Lab 2's GEMM uses FixPt 24.8, and our spelling is Fix True 24 8 with the rounding stated. Floating point and the structs, vectors and bit views of lecture 3 come later; no lab uses them.

## Memories: SRAM and FIFO run; Reg is designed (1:30)

Memories. SRAM in one and two dimensions runs, and so does the FIFO with enq, deq and peek, including loads and stores to a queue. The FIFO observations, occupancy and empty and full, are written and tested and in review now. Reg is fully designed: its rules are written and its tests' expected values derived by a separate author.

LUT, LineBuffer and RegFile with its shift come next, for Labs 2 and 3. The .buffer annotation from Lab 2's GEMM is not needed in Python: a program's results never depend on overlap, so buffering is the compiler's decision.

The important difference: every memory tracks which cells have been written. Reading an unset cell, an index out of range, or a deq from an empty queue stops the simulation with the fault and its source line, where Spatial's simulator logs and continues.

## Transfers: Loads and stores, destination first (1:00)

Transfers keep Spatial's dense load and store with the same slicing, in Python's slice syntax, with the destination first. Two-dimensional tiles, views with steps, edge tiles with min, and FIFO loads and stores all run today; the reference simulators run a tiled GEMM with uneven edge tiles written this way.

The par on a transfer becomes a hardware rule: a transfer moves one 512-bit beat a cycle. Gather and scatter come later; no lab uses them. And a transfer checks its whole range before it moves anything, so a bad range never leaves half a tile written.

## Controllers: Loops and branches run; reductions are next (1:30)

Controllers. Foreach with par, Sequential.Foreach with a step, and branches, including the value form of if, run today. The par is accepted and recorded; making the hardware honor it is the compiler change I'll show on the next slide.

The reductions are next, right after Reg, because Lab 1's last part needs them: Reduce and Fold, then MemReduce and MemFold for Lab 2, then FSM. One difference by design: a reduction states its identity and its combining operation, so the compiler can check that the tree it builds with par gives the same answer as adding in order. Pipe, Parallel, mux and abs complete the list.

## par and hardware: Spatial's schedules become the hardware (1:30)

Parallelism is where the language meets the hardware, and since our last meeting we decided to follow the original Spatial compiler. Sequential runs tiles one at a time. Foreach pipelines: an inner loop at one iteration a cycle, and an outer loop over a load, a compute loop and a store overlaps its tiles. Par is lanes, and each memory is banked from the accesses that use it. Like Spatial's hardware, ours checks nothing at run time; the simulators keep every check.

The table is Lab 1 in the course's own wrapper and test. Written the Spatial way, with foreach over tiles and par 16, and lowered by hand the way the compiler will, it matches the staff's HLS. The course's own source, which says Sequential and no par, gets Spatial's sequential schedule. The compiler today is the last row. So once the compiler change lands, the schedules students write change the hardware the way the course teaches.

## Streaming: Streaming is designed for later (0:45)

Streaming, lecture 5, is designed but not started: typed stream ports, and stream regions with named tasks joined by channels. We put it after the labs for two reasons. No lab uses it. And in a stream a stage waits on an empty or full FIFO, so waiting, deadlock and stopping have to become part of the language's meaning, which is a bigger design than a queue. Today's FIFO is ordered and bounded and never blocks; a deq from an empty queue is a fault. Streaming will add channels that wait.

## What changes: Six deliberate differences (1:30)

Six differences, each on purpose. First, faults are part of the language: an index out of range, a read of an unset cell, a queue that is empty or full, a zero divisor, each stops the simulation and names the line. Second, results never depend on the schedule: in Spatial a Pipe with a hazard can change the answer; in Python Spatial every program's results are those of running it in order, and the schedule only chooses overlap and lanes.

Third, the interface is the function signature. Fourth, transfers name the destination first and check their whole range before moving anything. Fifth, counters and data are different types. Sixth, queue state is observed with methods and never waited on; waiting is streaming's job. The reason for all six: students see their mistake at the line that made it, and trying a schedule can change speed but never the answer.

## Lab by lab: What each lab needs, and what runs (1:30)

Lab by lab. Lab 1's registers, DRAM and SRAM, and FIFO parts run; DRAM and SRAM also runs on the F2 FPGA. Controllers needs Reg, which is designed, and Reduce and Fold, which are next. Lab 2 needs the memory reductions, FSM, LUT and fixed point; Lab 3 the window memories, LUT, Reduce, mux and abs.

The shapes themselves already run: our reference simulators run a tiled GEMM with uneven edge tiles and a three-by-three window over a two-dimensional SRAM, written with plain loops and SRAMs. What is missing is the constructs that let students write them the way the labs teach.

## How it is built: Each construct is specified first, then tested against the spec (1:00)

How each construct gets delivered, so you can judge what "runs" means. The rules go into the language contract first, including every form we refuse. A separate author, who never sees the code, derives the expected results by hand. Tests are written first, then the code, on two reference simulators that must agree with each other. Reviewers plant bugs that the tests must catch, and after the code is frozen another author writes fresh programs it has never seen.

For the FIFO that meant 80 programs with 115 input sets, 78 refused forms, and step counts derived by two authors separately. This week the FIFO observations went through the same steps: 71 runs against a blind oracle, and two charge derivations that agreed on every value. All 2,640 tests on main pass before every merge, from source and from the installed package.

## Plan and questions: The order of delivery, and four questions (1:45)

The order of delivery follows the labs. The FIFO observations are built and tested and in review now. Then Reg, Reduce and Fold, which completes Lab 1. Then the memory folds, FSM, LUT and fixed point for Lab 2, then the Lab 3 window memories with mux and abs. Alongside, the Spatial-style hardware route takes each family to the FPGA.

Four questions. Fixed point: Lab 2's GEMM uses 24.8 fixed point; which rounding and overflow behaviour should students see? Schedule names: should we keep Sequential, Pipe, Parallel and Stream as the Python spellings, with the rule that results never depend on them? Lab 1's own source says Sequential with no par; should the lab teach Foreach and par so the hardware matches the staff's HLS? And streaming: no lab uses it; is it needed by April, or can it follow?

