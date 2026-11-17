---
type: weekly-update
title: "Weekly update — 15 November 2026"
project: spatial-python
date: 2026-11-15
---

**This week was about speed. We measured where the compiled design loses its cycles, and a prototype of the
compiler now generates a Lab 1 design as fast as the staff's handwritten HLS: 75, 108 and 155 cycles at 32, 256 and
1,024 elements, against 77, 109 and 158. A second prototype shows that every memory check in the Lab 1 programs
can be decided before the run. The first step of the prototype is now in the compiler itself and measured (260, 692
and 1,858 cycles, where its output took 294, 1,198 and 3,910); the rest is not yet. On the chip, we found that the course's own Lab 1
design returns wrong data when its test is repeated without reloading the image, and why chip counts ran below
simulation.**

> [!note] Update, 16 November (afternoon): the plan below changed the same day
> - **The larger cost is lost parallelism, not the checks.** The synthesis reports of the first fix show that the
>   compiler states no parallelism: `par` is written out as a comment, so the vendor tool decides. At 256 and
>   1,024 elements it runs the compute loop one element a cycle, 71 % of the cycles at 1,024. Every check is an
>   early exit, which serializes the flag reads.
> - **David's decision:** the FPGA route now follows the original Spatial compiler. There are no run-time checks or
>   flags in hardware; faults are found in the reference simulators, which keep every check, as does the native
>   route. `sequential`, `foreach` and `par` have Spatial's meaning.
> - **The fair comparison.** The course's own Spatial for Lab 1 says `Sequential` and no `par`, so we wrote our own
>   Spatial version of what the staff's HLS does (`foreach` over tiles, `par=16` inside). We ran it in the course's
>   own unmodified flow.
> - **The result.** Built by hand that way, it measured 75 / 77 / 156 cycles against the staff's 77 / 109 / 158.
>   This is a prototype; the compiler change that generates it is in design review.
> - **What is superseded.** The prover (prototype 2, item 4 below) is no longer on the path to speed, and questions
>   1 and 2 below are replaced by the deck's questions.
> - [Revised deck](https://davidydu.github.io/spatial-research-site/presentation/efficiency/) ·
>   [[2026-11-16-compiler-efficiency-presentation|its script]] ·
>   [decision record](https://github.com/davidydu/spatial-py/blob/main/docs/reviews/2026-11-16-spatial-style-fpga-decisions.md)

## What's new

**1. The gap to handwritten HLS grows with the array.** Last week's comparison used 32 elements. We ran the same
Lab 1 program (tiled scale: load a tile of 16, multiply, store) at 256 and 1,024 elements in the F2 kit's
simulation, the `make hw_sim` step students use, beside the staff's handwritten HLS.

![Line chart on logarithmic axes: today's compiler output rises from 294 to 3,910 cycles between 32 and 1,024 elements; the staff's handwritten HLS rises from 77 to 158; three compiler prototypes sit between, the last one on the staff's line](<50 - Python Rewrite/50 - HLS Lowering/assets/2026-11-15-scaling.svg>)

| Elements | Staff's handwritten HLS | Today's compiler output | Times as many |
|---|---|---|---|
| 32 | 77 | 294 | 3.8 |
| 256 | 109 | 1,198 | 11.0 |
| 1,024 | 158 | 3,910 | 24.7 |

- Today's output costs about 3.6 cycles for each extra element. The staff's design costs 1 to 2 cycles for each
  extra block of 16.
- At 1,024 elements more than half the time is one check: the loop at the end that confirms every output element
  was written. It visits one element every two cycles.

![Bar split into parts: of 3,625 estimated cycles at 1,024 elements, 2,051 are the final check that every output was written, 1,110 the loop over the tiles, about 400 the six staged copies](<50 - Python Rewrite/50 - HLS Lowering/assets/2026-11-15-breakdown.svg>)

**2. Where the cycles go.** We changed today's generated design by hand, one cause at a time, and simulated each
version (32 elements):

| Version | Compute cycles |
|---|---|
| Today's compiler output | 294 |
| The final check written so the tool can evaluate it in parallel | 257 |
| and no "initialized" flags fetched for inputs the host says are fully set | 168 |
| and nothing copied in or written back that the run cannot change | 89 |
| and one pipelined loop that reads, multiplies and writes | 75 |
| Staff's handwritten HLS | 77 |

- The time goes to memory round trips. Thirty-two multiplications take about 7 cycles. Each separate memory
  transfer that must finish before the next begins costs about 27 cycles beyond the synthesis estimate. Today's
  design makes six; the staff's makes two, overlapped.
- The Vitis single-exit rewrite from last week does not make the design faster by itself: 297 cycles against 294.

**3. A prototype of the compiler generates each step.** The hand edits show what is possible. A throwaway
prototype of the code generator now emits the same designs itself, at all three sizes:

| What the compiler emits | What it must know first | 32 | 256 | 1,024 |
|---|---|---|---|---|
| Today's output | | 294 | 1,198 | 3,910 |
| Prototype 1: the final check folded into a copy loop that already visits every flag | nothing | 260 | 692 | 1,858 |
| Prototype 2: checks proved away, and no transfer the run cannot observe | no check can fail, every output is written, the host confirms the inputs are fully set | 87 | 147 | 289 |
| Prototype 3: one fused, pipelined loop | the same, and each tile is a whole number of memory beats | 75 | 108 | 155 |
| Staff's handwritten HLS | | 77 | 109 | 158 |

- Each prototype design gave the same outputs as today's design and as the reference simulator before it was
  simulated, and passed the kit's test at all three sizes.
- Three limits. This is one program. The facts in the middle column were handed to the prototype in a table, not
  proved by the compiler (item 4 is the proof step). And the numbers are from simulation.
- **Prototype 1 is now in the compiler** (added the evening of 15 November; pull request 4 of the compiler
  repository). The F2 route emits its own kernel without the per-cell "was every output written?" loop, and the
  wrapper decides it while it copies the flags back. It gives exactly the results it gave before: the generated
  hardware code, built on the Mac, matches both reference simulators on 116 hand-specified inputs and on two fresh
  test sets written after the code was frozen; 40 of 42 deliberately planted bugs are caught and the other two
  cannot change any result; 2,640 automated tests pass. **Measured on 16 November in the F2 kit simulation, on the
  compiler's own output: 260 / 692 / 1,858 cycles**, every test passing, where it took 294 / 1,198 / 3,910. The
  counts equal the prototype's.
- One intermediate design (input flags skipped, checks still in hardware) passed at 32 elements and never
  finished at 256 and 1,024. We have not explained it. Its kernel is identical to a design that does finish, so the
  cause is in how the top level supplies the flags. No planned step generates that design.

**4. Most memory checks can be decided before the run.** Python Spatial checks every memory access: in bounds,
never reading an element that was not set, every output written. Today all of these stay in the hardware. A second
throwaway prototype reads the checked program and tries to prove each one impossible with simple reasoning (loop
ranges, which elements a loop writes).

![Two stacked bars: across 104 test programs, 1,318 of 1,662 possible memory failures are proved impossible, 97 are impossible once the host confirms the inputs are set, 247 remain as hardware checks; for the three Lab 1 programs 39 of 43 are proved and 4 need the host's confirmation, none remain](<50 - Python Rewrite/50 - HLS Lowering/assets/2026-11-15-census.svg>)

| Programs | Ways a memory access can fail | Proved impossible | Impossible once the host confirms the inputs are set | Left as hardware checks |
|---|---|---|---|---|
| All 104 test programs | 1,662 | 1,318 (79 %) | 97 (6 %) | 247 (15 %) |
| The three Lab 1 programs | 43 | 39 | 4 | 0 |

- A wrong proof is the one error we cannot accept. The proved checks never fired in 1,120 runs of the reference
  simulator, and 20 programs written to mislead the prover produced no wrong proof.
- It does not yet follow helper functions or branches. Counted by program, 60 of 104 are fully decided, but only
  5 of the 26 larger example programs, mostly because those use helpers.
- Queue-full and queue-empty checks are not attempted. They are counted separately (252, eight of them in Lab 1's
  FIFO programs) and stay in the hardware for now.

**5. On the chip: wrong answers that come from the course's wrapper and host program, not from a design.** On
14 November we built two of the hand-edited designs for the F2 chip. The fused design was correct in 58 of 58 runs,
each after a fresh load of its image. A second variant gave one wrong answer in 58. To chase that, on 15 November
we ran each design's test over and over after a single load.

| Design | Host program | Runs | Wrong results | First wrong run |
|---|---|---|---|---|
| Staff's handwritten HLS, unmodified | the course's own | 101 | 46 | 53 |
| Fused loop (hand-edited) | the course's protocol | 224 | 218 | 7 |
| Fused loop (hand-edited) | the same, with pauses added | 112 | 81 | 32 |
| Second variant (flags in the data buffer) | the course's protocol | 519 | 472 | 26 |
| Today's compiler output | the course's protocol | 300 | 0 | none |
| Today's compiler output, 16 November | the course's protocol | 2,300 | 2 | 35 |
| Staff's handwritten HLS | every write confirmed | 400 | 0 | none |
| Fused loop (hand-edited) | every write confirmed | 400 | 0 | none |
| Today's compiler output | every write confirmed | 300 | 0 | none |
| Second variant (flags in the data buffer) | every write confirmed | 300 | 0 | none |

- **Every single-loop design fails this way, the course's own included.** The staff's handwritten design, wrapper
  and host program, byte-identical to the course repository, were correct for 48 runs and returned their first
  wrong data on run 53. No fault is reported, and from run 57 every run is wrong until the image is loaded again.
  Today's compiler output, which uses the memory in separate steps, did not fail that day. On 16 November it did,
  twice in 2,300 runs, and recovered each time (below).
- **Pauses between the program's phases do not help. Never having two writes in flight does.** With one added
  line, the host program reads back every word before it writes the next. In 1,400 runs of four designs that way,
  none returned a wrong result. A pause of 100 microseconds after every write, with nothing read back, does the
  same (16 November): 600 runs of two designs, none wrong.
- **What is wrong in the code** (added the same evening, after an independent analysis). The course's wrapper
  shares the memory between the host and the kernel through a small arbiter. It releases its write lock at the
  first acknowledgement without counting the writes still in flight, and it routes acknowledgements and write data
  by whoever is selected at that moment, not by owner. The AWS shell lets the host have 32 writes in flight, so
  this is wrong for ordinary traffic. A cycle-level model of those lines reproduces the kernel reporting "done"
  early and the exact layout of the first wrong outputs; both vanish, as on the chip, when the host confirms each
  write.
- **Confirmed on the chip (16 November).** The AWS shell keeps its own error counters. After a fresh load and one
  run of the course's unmodified test, the shell has recorded a host write that never received its
  acknowledgement, at the last address the program wrote. With every write confirmed, it records none.
- **Once it starts, only a reload clears it** (16 November). After the wrong results began we switched to the safe
  host program without reloading: 150 runs of 150 were still wrong. In that state the shell records dozens of
  timeouts a run and most host writes never reach the memory.
- **It starts well before the test notices** (16 November). We read the shell's counters after every run of the
  staff's unmodified design. Host writes began to go missing at run 5; the test kept passing until run 23. The test
  writes the same inputs every run, so a lost write usually leaves the right value in place. So "first wrong on
  run 53" above says when the damage became visible, not when it began, and a passing test alone does not show a
  healthy run. From now on every chip run reads these counters.
- **Our staged output is not immune** (16 November). In 2,000 further runs it returned two wrong results (runs 35
  and 116), each showing the host's own last writes landing after the kernel's output, and it passed through one
  stretch in which about 11,000 writes never reached the memory. Then it returned to normal by itself and ran
  1,750 more runs cleanly. The single-loop designs never recover without a reload.
- **What is still not explained.** Why our staged compiler output recovers without a reload and the single-loop
  designs do not. The bug has also not yet been reproduced in a hardware simulation, where the kit's test bench
  finishes each write before the next.
- **It explains a puzzle from last week.** Every design took fewer cycles on the chip than in simulation. With
  every host write confirmed, the two agree:

  | Design | Chip, course's host protocol | Chip, every write confirmed | Simulation |
  |---|---|---|---|
  | Staff's handwritten HLS | 58 to 62 | 80 | 77 |
  | Fused loop (hand-edited) | 60 | 78 | 75 |
  | Today's compiler output | 260 | 301 | 294 |

  So the chip counts we reported before compare designs fairly but are each too low. The simulation counts are the
  ones to quote.
- Separately, the host test program itself crashed in 4 of the 2,756 runs, two of them with the course's own
  program. Not explained.
- A correction: on 14 November we described the second variant as "every check kept at the staff's speed". It
  keeps only the one check that can fail for this program, plus the check that every output was written.

**6. Lab features.** The first FIFO slice is merged: declaring a queue, `enq`, `deq`, `peek`, loading and storing
through a queue, and the faults, in the source language, the checker and both reference simulators. Lab 1 Part 1
(ArgIn and ArgOut) already runs with no new feature. The FIFO's status queries (`is_empty`, `is_full`, the count)
are half built and paused for the speed work. Reg's contract and tests are written. 2,573 automated tests pass,
from source and as an installed package (2,640 with the first speed-up, item 3).

**7. Rules for every later hardware design.** So that FIFO, Reg and Reduce are fast from the start, each hardware
plan is now checked against eleven written rules, each tied to a measurement. The main ones:
- Count the memory round trips first. They cost more than the arithmetic.
- Move nothing the run cannot observe.
- No check whose cost grows with the number of elements.
- One pipelined loop for each stream of tiles.
- Measure at three sizes beside the staff's design, then with thousands of back-to-back runs on the chip.

## The plan

Speed work now runs beside the lab features instead of after them.

1. **Prototype 1 into the real compiler.** Done on 15 November and measured on the 16th: 1,024 elements go from
   3,910 cycles to 1,858. It needed no proof and no interface change.
2. **Reproduce the chip failure in simulation.** Until the compiler generates its own wrapper, every chip run
   uses a host program that confirms its writes.
3. **The prover as a real checker pass.** "Unknown" never counts as proved, and a program loaded from a file is
   proved again.
4. **The compiler's own wrapper and host program** (decided 12 November), with the host telling the hardware which
   inputs are fully set.
5. **Prototypes 2 and 3 into the compiler**, measured at three sizes and soaked on the chip.

Lab features continue in the same order: FIFO status queries, Reg, then Reduce and Fold.

## Questions

1. **Checks.** Our rule is "checked by default, proved away when the compiler can, no unchecked mode". A program the
   prover cannot handle keeps its hardware checks and runs slower. Is that the right trade for the class, or should
   students be able to switch checks off?
2. **One fused loop or streams.** To match handwritten HLS we fuse a load, a loop and a store into one pipelined
   loop when that is provably safe. The staff's FIFO design instead uses separate processes joined by streams.
   Which should the compiler aim at in general?
3. **What counts as fast enough.** We compare with the staff's handwritten HLS at 32, 256 and 1,024 elements. Are
   those the right programs and sizes, or should we also take benchmarks from the original Spatial work?
4. **The failure on the chip.** The course's own design returns wrong data when its test is repeated without
   reloading the image (`make run_fpga_test` again without `make program_fpga`). Who on the course staff should
   hear about it?
