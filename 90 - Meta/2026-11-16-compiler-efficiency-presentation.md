---
type: reference
title: "Python Spatial — compiler efficiency, 16 November 2026"
project: spatial-python
date: 2026-11-16
verified: 2026-11-16
scope: "Eight slides on where the compiled hardware loses its cycles, the first fix in the compiler, the prototypes, and the course wrapper's bug"
---

# Python Spatial: making the compiler's hardware fast

[Open the presentation](https://davidydu.github.io/spatial-research-site/presentation/efficiency/) · [[2026-11-15-weekly-update|Weekly update, 15 November]] · [[05 - Python Professor Brief|Short professor brief]]

Eight slides, about eleven minutes before discussion, for the meeting of 16 November 2026. It answers the question from the last meeting: the compiled design was correct on the FPGA but several times slower than the staff's handwritten HLS. Every number on a slide is a saved measurement in the compiler repository; the deck's "Evidence" button lists the pages behind each slide.

**What is real and what is a prototype.** The first fix (slide 4) is in the compiler, merged after the full review routine, and measured in the F2 kit simulation on 16 November: 260, 692 and 1,858 compute cycles at 32, 256 and 1,024 elements, where the compiler's output took 294, 1,198 and 3,910. The designs at 87 / 147 / 289 and 75 / 108 / 155 (slide 5) are a throwaway prototype's, given its facts in a table. The prover (slide 6) is a second throwaway prototype.

**The course wrapper (slide 7).** Say "a definite bug in the arbiter, confirmed on the chip by the AWS shell's own counters". Do not say everything is explained: our staged design fails too (two wrong runs in 2,600) but recovers without a reload, and why it recovers is open; no hardware-language simulation of the bug has been run. Do not quote "first wrong on run 53" as when the trouble began: with the counters read after every run, the staff's design lost host writes from run 5 and passed until run 23, because the test writes the same data every run. A draft note for the course staff is in the compiler repository (`docs/evidence/hardware-performance-planning/wrapper-arbiter-analysis-2026-11-15.md`); sending it is David's decision.

The 22 October deck and [[2026-10-22-python-pipeline-presentation|its script]] remain the record of the first pipeline result.

## Story and timing

| Slide | Headline | Time | Elapsed |
|---|---|---|---|
| 1 | Making the compiler's hardware fast | 1:15 | 1:15 |
| 2 | The gap grows with the array | 1:15 | 2:30 |
| 3 | Memory traffic and one check, not arithmetic | 1:30 | 4:00 |
| 4 | The first fix is in the compiler | 1:30 | 5:30 |
| 5 | A compiler prototype reaches the staff's speed | 1:15 | 6:45 |
| 6 | Most memory checks can be decided before the run | 1:15 | 8:00 |
| 7 | A bug in the course's wrapper | 1:30 | 9:30 |
| 8 | The plan, and four questions | 1:30 | 11:00 |

This is a pacing target, not a measured rehearsal. Spend the time on slides 4, 5 and 7; slides 2 and 3 can go quickly if the gap is already understood.

## 1. Making the compiler's hardware fast · 1:15

Last time I showed the first run on the FPGA: Lab 1 compiled from Python Spatial was correct but took about four times as many cycles as the staff's handwritten HLS. You asked about efficiency. This week was about that.

Three things happened. We measured where the cycles go, at larger sizes too, and the gap is worse than it looked. We put the first fix into the real compiler, under the full review routine, and measured it. And a throwaway prototype of the code generator reaches the staff's speed at every size we tried, which tells us the remaining gap is closable and what it takes. I'll also show a bug we found in the course's own wrapper along the way.

## 2. The gap grows with the array · 1:15

This is the same Lab 1 program at 32, 256 and 1,024 elements, in the kit's simulation, the make hw_sim step students run. Orange is the staff's handwritten HLS. Blue is what our compiler generated before this week. Both axes are logarithmic.

At 32 elements we were 3.8 times slower. At 1,024 we were almost 25 times slower. Our design cost about three and a half cycles per extra element; theirs costs one or two per extra block of sixteen. So the single size we measured last week understated the problem, and we now measure at three sizes as a rule. The green lines are the compiler prototypes I'll come to.

## 3. Memory traffic and one check, not arithmetic · 1:30

Where does the time go? Not arithmetic. Both designs multiply sixteen numbers at once, and the multiplications take about seven cycles.

The bar is our design at 1,024 elements. More than half is one check: at the end the kernel confirms every output element was written, one element every two cycles. The next part is the loop over tiles, and then six staged copies in and out of memory, where the staff's design makes two transfers that overlap.

On the right we changed the generated design by hand, one cause at a time, at 32 elements. Writing the final check so the tool can evaluate it in parallel: 294 to 257. Not fetching flags for inputs the host says are fully set: 168. Not copying what the run can't change: 89. And one pipelined loop: 75, level with the staff's 77. So three causes: memory round trips, a check whose cost grows with the data, and nothing proved before the run.

## 4. The first fix is in the compiler · 1:30

This is the one that is real. As of last night the compiler itself generates this, merged after the full routine.

The change: the kernel no longer has a loop that checks, one element per trip, whether every output was written. The wrapper already runs a loop that copies the "written" flags back to memory, sixteen at a time, so the check now rides in that loop. The program's results are exactly what they were, including which fault is reported.

The numbers in blue were measured last night on the real compiler's output, in the kit simulation: 260, 692 and 1,858 cycles, where the old output took 294, 1,198 and 3,910. They equal the prototype's numbers exactly, and at 1,024 elements that is a little over twice as fast.

How do we know it's right? The generated hardware code, compiled on the Mac, gives the same results as both reference simulators on 116 inputs whose expected results were specified by hand. The tests and the code were written by separate authors from the plan and agreed the first time they met. Reviewers planted 42 bugs; 40 are caught and the other two can't change a result. And two fresh test sets were written after the code was frozen.

We did this one first because it needs nothing new: no proof, no change to the interface with the host. It is still far from the staff's 158.

## 5. A compiler prototype reaches the staff's speed · 1:15

The hand edits show what is possible; the compiler has to produce them. So we built a throwaway prototype of the code generator that emits each faster design itself, at any of the three sizes, when it is handed facts about the program.

The second row is the fix that is now real. The third row removes the checks and the transfers the run can't observe; it needs to know that no check can fail, that every output is written, and that the host has set the inputs. That gets within a factor of two. The fourth row fuses the load, the loop and the store into one pipelined loop, and that matches the staff's design at every size: 75, 108, 155 against 77, 109, 158.

Three honest limits. It is one program. The facts were given to the prototype in a table; proving them is the next slide. And these are simulation numbers. Also, one intermediate design we tried never finished at the larger sizes and we haven't explained it, so we won't generate that one.

## 6. Most memory checks can be decided before the run · 1:15

Where do those facts come from? Python Spatial checks every memory access: in bounds, never reading an element that wasn't set, every output written. Today all of those checks stay in the hardware.

A second throwaway prototype reads the checked program and tries to prove each possible failure impossible, with simple reasoning: loop ranges, and which elements a loop writes. Across 104 test programs it proves 79 percent, another 6 percent follow once the host confirms its inputs are fully set, and 15 percent are left as hardware checks. For the three Lab 1 programs nothing is left.

The one error we can't accept here is a wrong proof, because it silently removes a check. The proved checks never fired in over a thousand runs of the reference simulator, and thirty-one programs written to trick it produced no wrong proof. It doesn't yet follow helper functions or branches, which is why only five of the twenty-six larger examples are fully decided. This will be built as a real checker pass with its own reviews.

## 7. A bug in the course's wrapper · 1:30

One finding that isn't about our compiler. On the chip, one of our variants gave a wrong answer once in 58 runs. Chasing that, we ran each design's test over and over after a single image load. Every single-loop design eventually returns wrong data and keeps doing so until the image is reloaded. That includes the course's own Lab 1 design, unmodified, with the course's own host program: wrong from run 53.

Pausing between the program's phases doesn't help. What helps is never having two host writes in flight. One added line does it: the host reads back each word before writing the next. With that, 1,400 runs of four designs, none wrong. Last night a short pause after every write did the same: 600 runs of two designs, none wrong.

The cause, as far as we can establish it: the wrapper has a small arbiter that shares the memory between the host and the kernel. It releases its lock at the first acknowledgement without counting the writes in flight, and it routes acknowledgements by whoever is selected, not by owner. The shell allows the host 32 writes in flight, so that is wrong for ordinary traffic. A cycle-level model of those lines reproduces the kernel reporting done early and the layout of the first wrong outputs. And last night we checked it on the chip with the AWS shell's own error counters: after a single run of the course's test, the shell records a host write that never received its acknowledgement, at the last address the program wrote. With the one-line change it records none.

Three more things from last night. Once the failure starts, switching to the safe host program does not help; only reloading the image does. It also starts earlier than the test shows: reading the counters after every run, the staff's design was losing host writes from run 5 and still passed until run 23, because the test writes the same data every time. And our own staged design is not immune, as I thought on Sunday: two wrong runs in 2,600, and one stretch of lost writes. But it recovered without a reload, and that we cannot yet explain.

A side effect matters for our numbers: with the course's host program the kernel reports done about fifteen cycles early. So the chip counts I showed last week were each too low; the simulation counts are the ones to quote. I have a short note drafted for the course staff if you think it should go to them.

## 8. The plan, and four questions · 1:30

The plan. The first fix is done. Next is confirming the wrapper bug in simulation, because every single-loop design depends on a wrapper we can trust. Then the prover as a real checker pass, the compiler's own wrapper and host program, which also gives us the interface where the host says which inputs are fully set, and then the proved design and the fused loop. About two to three weeks, most of it the review work that makes the result trustworthy, not the code.

We also changed how we work: every feature plan now carries a hardware sketch, a throwaway prototype is measured before a hardware slice starts, and there is a performance table we keep current. So FIFO, Reg and Reduce are designed for speed from the start.

Four questions for you. First, on checks: no unchecked mode, with checks proved away where the compiler can. Is that right for the class? Second, fusing into one loop against generating streaming processes as the staff's FIFO design does. Third, what counts as fast enough: these three sizes, or benchmarks from the original Spatial work as well. Fourth, who should hear about the wrapper.

## If asked

- **"Why is the first fix only a factor of two?"** It removes one check loop. The remaining cost is six separate memory transfers and a tile loop that the tool schedules at 17 cycles a tile at larger sizes; the proved design and the fused loop remove those, and they need the prover and the new interface.
- **"How long for the rest?"** Two to three weeks: the prover as a checker pass (4 to 5 days, in two parts), the compiler's own wrapper and host program (3 to 4 days and two sessions on the F2 instance), the proved staged design (2 days), the fused loop (2 to 3 days). The code is the small part; the prototypes took about two hours each. The time goes into the independent tests and reviews that make the result trustworthy.
- **"Could students just turn the checks off?"** That is question 1. Today's decision is no unchecked mode: checks are proved away where the compiler can and kept otherwise.
- **"Is the wrapper bug certain?"** The defect in the code is certain, and the shell's timeout counter shows its direct effect after one run of the course's own test. What is not shown is a waveform of it, and why our staged design recovers from it without a reload when the single-loop designs do not.
- **"How do you know your own runs were healthy, if a passing test can hide lost writes?"** For the confirmed-write and spaced-write runs: the shell's counters showed no timeout and every write arriving in the runs where we read them, and the cycle counts sat a few above simulation in every run, which they do not when writes overlap. From now on every chip run reads the counters, and our own host program will change its inputs between runs.
- **"Did the chip numbers from last week change?"** Yes: they were taken with the course's host program, under which the kernel reports done about 15 cycles early per write phase. With host writes confirmed, the staff's design takes 80 cycles on the chip (77 in simulation), our earlier output 301 (294), the hand-edited fused design 78 (75). Comparisons between designs still hold.
