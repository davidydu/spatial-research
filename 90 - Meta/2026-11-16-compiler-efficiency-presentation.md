---
type: reference
title: "Python Spatial — compiler efficiency, 16 November 2026"
project: spatial-python
date: 2026-11-16
verified: 2026-11-16 (revised in the afternoon)
scope: "Eight slides on where the compiled hardware loses its cycles, the first fix in the compiler, the parallelism the compiler never states, the Spatial-style design that matches the staff, and the course wrapper's bug (revised the afternoon of 16 November)"
---

# Python Spatial: making the compiler's hardware fast

[Open the presentation](https://davidydu.github.io/spatial-research-site/presentation/efficiency/) · [[2026-11-15-weekly-update|Weekly update, 15 November]] · [[05 - Python Professor Brief|Short professor brief]]

Eight slides, about eleven minutes before discussion, for the meeting of 16 November 2026. It answers the question from the last meeting: the compiled design was correct on the FPGA but several times slower than the staff's handwritten HLS. Every number on a slide is a saved measurement in the compiler repository; the deck's "Evidence" button lists the pages behind each slide.

**Revised the afternoon of 16 November.** Slides 5 and 6 replace the morning's "prototype" and "proofs" slides. David decided that day that the FPGA route follows the original Spatial compiler: no run-time checks or flags in hardware, and Spatial's schedules ([decision record](https://github.com/davidydu/spatial-py/blob/docs/parallelism-first/docs/reviews/2026-11-16-spatial-style-fpga-decisions.md)). Slides 1, 3 and 8 changed to match.

**What is real and what is a prototype.**
- The first fix (slide 4) is in the compiler, merged after the full review routine. It was measured in the F2 kit simulation on 16 November: 260, 692 and 1,858 compute cycles at 32, 256 and 1,024 elements, where the compiler's output took 294, 1,198 and 3,910.
- Every other design on slides 5 and 6 is a throwaway prototype, edited or written by hand.
- Slide 6's numbers were measured that afternoon in the course's own unmodified Lab 1 Part 2 flow, beside the staff's design re-run alone. The compiler change that generates that design is in design review.
- Do not quote 106 / 346 / 1,115 for the course's own source. That first run was not Spatial's `Sequential`, because the tool merged the two loops into one pipeline. It is being measured again.

**The course wrapper (slide 7).** Say "a definite bug in the arbiter, confirmed on the chip by the AWS shell's own counters". Do not say everything is explained: our staged design fails too (two wrong runs in 2,600) but recovers without a reload, and why it recovers is open; no hardware-language simulation of the bug has been run. Do not quote "first wrong on run 53" as when the trouble began: with the counters read after every run, the staff's design lost host writes from run 5 and passed until run 23, because the test writes the same data every run. A draft note for the course staff is in the compiler repository (`docs/evidence/hardware-performance-planning/wrapper-arbiter-analysis-2026-11-15.md`); sending it is David's decision.

The 22 October deck and [[2026-10-22-python-pipeline-presentation|its script]] remain the record of the first pipeline result.

## Story and timing

| Slide | Headline | Time | Elapsed |
|---|---|---|---|
| 1 | Making the compiler's hardware fast | 1:15 | 1:15 |
| 2 | The gap grows with the array | 1:15 | 2:30 |
| 3 | Memory traffic and one check, not arithmetic | 1:30 | 4:00 |
| 4 | The first fix is in the compiler | 1:30 | 5:30 |
| 5 | The compiler never states its parallelism | 1:30 | 7:00 |
| 6 | Following the original Spatial compiler | 1:45 | 8:45 |
| 7 | A bug in the course's wrapper | 1:30 | 10:15 |
| 8 | The plan, and four questions | 1:45 | 12:00 |

This is a pacing target, not a measured rehearsal. Spend the time on slides 5, 6 and 8. Slides 2 and 3 can go quickly if the gap is already understood, and slide 7 can be shortened to its first paragraph.

## 1. Making the compiler's hardware fast · 1:15

Last time I showed the first run on the FPGA: Lab 1 compiled from Python Spatial was correct but took about four times as many cycles as the staff's handwritten HLS. You asked about efficiency. This week was about that.

Four things happened. We measured where the cycles go, at larger sizes too, and the gap is worse than it looked. We put the first fix into the real compiler, under the full review routine, and measured it. Then today we found what the compiler really gets wrong: it never states its parallelism, so the vendor tool guesses, and at scale it guesses one lane. And we changed the design to follow the original Spatial compiler: no run-time checks in the hardware, and Spatial's schedules. Written that way and built by hand, Lab 1 matches the staff's design in the course's own flow. I'll also show a bug we found in the course's own wrapper.

## 2. The gap grows with the array · 1:15

This is the same Lab 1 program at 32, 256 and 1,024 elements, in the kit's simulation, the make hw_sim step students run. Orange is the staff's handwritten HLS. Blue is what our compiler generated before this week. Both axes are logarithmic.

At 32 elements we were 3.8 times slower. At 1,024 we were almost 25 times slower. Our design cost about three and a half cycles per extra element; theirs costs one or two per extra block of sixteen. So the single size we measured last week understated the problem, and we now measure at three sizes as a rule. The green lines are compiler prototypes from the weekend; the lowest one, on the staff's line, has the structure we are now building, slide 6.

## 3. Memory traffic and one check, not arithmetic · 1:30

Where does the time go? Not arithmetic. Both designs multiply sixteen numbers at once, and the multiplications take about seven cycles.

The bar is our design at 1,024 elements. More than half is one check: at the end the kernel confirms every output element was written, one element every two cycles. The next part is the loop over tiles, and then six staged copies in and out of memory, where the staff's design makes two transfers that overlap.

On the right we changed the generated design by hand, one cause at a time, at 32 elements. Writing the final check so the tool can evaluate it in parallel: 294 to 257. Not fetching flags for inputs the host says are fully set: 168. Not copying what the run can't change: 89. And one pipelined loop: 75, level with the staff's 77. So at this size two causes: memory round trips, and a check whose cost grows with the data. At larger sizes there is a bigger one, which I'll come to on slide 5.

## 4. The first fix is in the compiler · 1:30

This is the one that is real. As of last night the compiler itself generates this, merged after the full routine.

The change: the kernel no longer has a loop that checks, one element per trip, whether every output was written. The wrapper already runs a loop that copies the "written" flags back to memory, sixteen at a time, so the check now rides in that loop. The program's results are exactly what they were, including which fault is reported.

The numbers in blue were measured last night on the real compiler's output, in the kit simulation: 260, 692 and 1,858 cycles, where the old output took 294, 1,198 and 3,910. They equal the prototype's numbers exactly, and at 1,024 elements that is a little over twice as fast.

How do we know it's right? The generated hardware code, compiled on the Mac, gives the same results as both reference simulators on 116 inputs whose expected results were specified by hand. The tests and the code were written by separate authors from the plan and agreed the first time they met. Reviewers planted 42 bugs; 40 are caught and the other two can't change a result. And two fresh test sets were written after the code was frozen.

We did this one first because it needed nothing new: no proof, no change to the interface with the host. It is still 11.8 times the staff's design at 1,024 elements.

## 5. The compiler never states its parallelism · 1:30

After the first fix I had planned to prove checks away next. When I read the synthesis reports of the fixed design, the largest cost was somewhere else. Our C++ is a statement-by-statement translation of the program, and every bit of parallelism in the hardware is whatever the vendor tool infers. The language's par is parsed, checked, recorded, and then written out as a comment.

At 32 elements the tool happens to infer sixteen lanes for the compute loop. At 256 and 1,024 it infers one: the same loop is seventeen times slower per tile, and that is 71 percent of the cycles at 1,024. The schedule shows why. Every check is an early exit, so each flag read decides whether to leave the loop, and the tool reads a tile's sixteen flags one per cycle. The data reads, which no exit follows, all happen in one cycle.

So we tried prototypes that keep every check but change the structure. Recording a failed check instead of exiting: 1,858 down to 824. Streaming the tiles through one loop, still with every check: 737. The structure matters more than the checks. And the compiler has to decide it, as Spatial's compiler does with its unrolling and banking passes.

## 6. Following the original Spatial compiler · 1:45

So we changed the design to follow the original Spatial compiler, which our research notes document pass by pass. Spatial's hardware checks nothing at run time and keeps no per-element valid bits; only its simulator does, and it logs and continues. We now do the same on the FPGA: on any input the reference simulators run to completion, the hardware gives their answer; faults are found in the simulators. The native route and both simulators keep every check. And loops follow Spatial's schedules: Sequential runs one tile at a time, Foreach pipelines and, around loads and stores, overlaps tiles, par is lanes.

That raised a question about the comparison itself. The course's own Spatial source for this lab says Sequential over the tiles and no par. Read as Spatial reads it, that is a slow schedule. The staff's handwritten HLS does what Foreach with par 16 says. So we wrote our own Spatial version that says it, and compare that with the staff's design.

To keep the comparison fair we ran it in the course's own flow: our file replaces the staff's, with the same ports, the course's wrapper and the course's test, which compares every output word. Written by hand the way the compiler will emit it: 75, 77 and 156 cycles against the staff's 77, 109 and 158. The 77 at 256 is the simulator's memory model; from 32 to 1,024 both designs rise by the same 81 cycles. As three concurrent stages joined by streams: 80, 114, 161.

Two lessons from the runs. A top that the tool turns into a self-restarting pipeline starts again by itself in the course's wrapper; the compiler's tops must never be one. And the first measurement of the course's Sequential source turned out to be wrong: the tool merged the two loops into one pipeline, so it was not Spatial's schedule. It is being measured again. The compiler change that generates all this is written up and in design review.

## 7. A bug in the course's wrapper · 1:30

One finding that isn't about our compiler. On the chip, one of our variants gave a wrong answer once in 58 runs. Chasing that, we ran each design's test over and over after a single image load. Every single-loop design eventually returns wrong data and keeps doing so until the image is reloaded. That includes the course's own Lab 1 design, unmodified, with the course's own host program: wrong from run 53.

Pausing between the program's phases doesn't help. What helps is never having two host writes in flight. One added line does it: the host reads back each word before writing the next. With that, 1,400 runs of four designs, none wrong. Last night a short pause after every write did the same: 600 runs of two designs, none wrong.

The cause, as far as we can establish it: the wrapper has a small arbiter that shares the memory between the host and the kernel. It releases its lock at the first acknowledgement without counting the writes in flight, and it routes acknowledgements by whoever is selected, not by owner. The shell allows the host 32 writes in flight, so that is wrong for ordinary traffic. A cycle-level model of those lines reproduces the kernel reporting done early and the layout of the first wrong outputs. And last night we checked it on the chip with the AWS shell's own error counters: after a single run of the course's test, the shell records a host write that never received its acknowledgement, at the last address the program wrote. With the one-line change it records none.

Three more things from last night. Once the failure starts, switching to the safe host program does not help; only reloading the image does. It also starts earlier than the test shows: reading the counters after every run, the staff's design was losing host writes from run 5 and still passed until run 23, because the test writes the same data every time. And our own staged design is not immune, as I thought on Sunday: two wrong runs in 2,600, and one stretch of lost writes. But it recovered without a reload, and that we cannot yet explain.

A side effect matters for our numbers: with the course's host program the kernel reports done about fifteen cycles early. So the chip counts I showed last week were each too low; the simulation counts are the ones to quote. I have a short note drafted for the course staff if you think it should go to them.

One more from today, in simulation rather than on the chip. When one of our prototype tops restarted by itself, its second run's memory traffic overlapped the host reading results back, and the host received read data it had not asked for, the protocol checker flagging it. That fits the same arbiter routing replies by whoever is selected. It is an observation, not a reproduction: it was not set up on purpose.

## 8. The plan, and four questions · 1:45

The plan. The first fix is done and measured. The Spatial-style design is done by hand and matches the staff's in the course's own flow. Next, the compiler generates it: a new FPGA route that decides schedules, lanes and memory layouts before writing any C++, under the full review routine. Its plan was reviewed today and is being revised. Then we measure the compiler's own output in the course's flow, both Lab 1 versions at three sizes beside the staff's design. After that, stages joined by streams for the cases one fused loop cannot cover, and the first FPGA build and a long soak on the chip with a host program that avoids the wrapper bug.

We changed how we work, too. Every plan now states, for each loop, how many elements it handles a cycle and the memory layout that allows it, and the synthesis report is read at every size before anyone proposes a large mechanism. The proving work from the weekend is not lost; it can still serve the native route, but it is no longer on the path to speed.

Four questions. First: no checks in the hardware, as in Spatial, with faults found only in the simulators. Is that right for the class? Second: the course's Spatial for this lab says Sequential and no par, so we compare our own Spatial version with the staff's HLS. Is that the right comparison, or should the lab's Spatial change? Third: Spatial's double-buffered metapipelines don't map well onto Vitis for small tiles; would you start with stages that read tiles in order? Fourth: who on the staff should hear about the wrapper.

## If asked

- **"Why is the first fix only a factor of two?"** It removes one check loop. Most of what remains is a compute loop that the tool runs one element a cycle at larger sizes (slide 5) and six separate memory transfers; the Spatial-style design removes both.
- **"How long until the compiler does it?"** The compiler change is planned and its design review is back (adopt with named changes). It goes through the full routine: separate fixture and expected-value authors, tests first, planted bugs, a fresh holdout, then a measurement of the compiler's own output in the course's flow. My estimate is days rather than weeks for Lab 1's form; streams between stages and other labs' patterns follow.
- **"What happens on the FPGA if a program would fault?"** Its outputs are undefined, as in Spatial's hardware. The reference simulators and the native route keep every check, so a student runs there first, as Spatial users run its simulator. The design review asked for one extra guarantee, which the revised plan takes: every load and store is proved in range before the compiler accepts the program, so a faulting input cannot write outside its own buffer.
- **"Is the prover wasted?"** No. It is still the way to drop checks from the native route later, and its analyses (loop ranges, which elements a loop writes) are what the compiler uses to prove transfers aligned and in range.
- **"Why not show the course's own source?"** Its first measurement was not Spatial's schedule (the tool merged its loops). It is being re-measured with that merging turned off, and both versions will be measured from the compiler's own output.
- **"Is the wrapper bug certain?"** The defect in the code is certain, and the shell's timeout counter shows its direct effect after one run of the course's own test. What is not shown is a waveform of it, and why our staged design recovers from it without a reload when the single-loop designs do not.
- **"How do you know your own runs were healthy, if a passing test can hide lost writes?"** For the confirmed-write and spaced-write runs: the shell's counters showed no timeout and every write arriving in the runs where we read them, and the cycle counts sat a few above simulation in every run, which they do not when writes overlap. From now on every chip run reads the counters, and our own host program will change its inputs between runs.
- **"Did the chip numbers from last week change?"** Yes: they were taken with the course's host program, under which the kernel reports done about 15 cycles early per write phase. With host writes confirmed, the staff's design takes 80 cycles on the chip (77 in simulation), our earlier output 301 (294), the hand-edited fused design 78 (75). Comparisons between designs still hold.
