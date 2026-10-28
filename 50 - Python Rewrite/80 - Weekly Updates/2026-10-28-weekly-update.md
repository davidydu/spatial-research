---
type: weekly-update
title: "Weekly update — 28 October 2026"
project: spatial-python
date: 2026-10-28
---

**This week: the student workflow is real, programs can be saved and reloaded
safely, and the corrected hardware interfaces pass RTL simulation. A Python
program builder and the first AWS F2 bundle for Lab 1 reached reviewed
checkpoints.**

## What's new

**1. A public student workflow** (E1). From Python, a student checks a kernel,
compiles it once to native C++, and runs it on many test cases with their own
expected answers:

```python
checked = spatial.check(program, "reference.guarded.v1")
with spatial.compile_native(checked.value).value as kernel:
    result = kernel.run(bindings)        # outcome, outputs, every memory's contents
```

- Lab 1's tiled scale runs this way, through the student guide's
  `run(src=..., scale=...)` style.
- A wrong-size output is rejected before anything runs.
- A separate author, who never saw the implementation, wrote 47 black-box tests
  from the specification; all passed on their first run.

**2. Saving and loading programs** (E2). A program can be saved as a canonical
file and loaded back. A loaded program is never trusted: it is fully checked
again, so a forged file cannot pass. Fifteen independent tests passed on their
first run. Review fixes cut the worst-case memory for a large file from about
900 MB to 120–200 MB.

**3. Hardware: the corrected scalar interfaces work** ([[2026-10-27-scalar-interface-vitis-checkpoint]]).
- All 15 projects (46 test cases, including 12 intentional faults) pass Vitis C
  simulation, synthesis and RTL co-simulation.
- Scalar state now uses the interfaces we asked for (`ap_none` inputs, `ap_vld`
  outputs), and Vitis ignored no interface request.
- The RTL simulation's own output data shows every scalar result written
  correctly for every case.

Across both features, 1,555 automated tests pass, run both from source and as an
installed package.

## In progress: two reviewed checkpoints

**4. Building programs in Python** (E3). Tools and generators can build a
program through a Python API instead of source text, and the result has the same
checked identity as the source-written program. 117 tests pass, including a
table of every operator and form. The quality review planted 12 bugs, and the
tests now catch all of them.

**5. The first AWS F2 bundle for Lab 1** (F2 step 1). The compiler generates the
course-style `vadd` top level around our unchanged kernel: `kernel.cpp` is
byte-identical to the verified Z020 build. All 16 Lab 1 cases pass native checks,
with pipelining off and on. 42 tests pass, and all 12 planted bugs are caught.

Both are committed but not yet frozen, so their 159 new tests have so far run
from source only.

## The plan for the next six months

The plan targets student and TA use in about six months. In order:
1. **Two safety checks on the compiler's core.** The same program must come out
   identical whether it is written as source, built through a Python API or
   loaded from a file; and the compiler must be able to edit programs safely,
   which optimizations need.
2. **Fast simulation**, so Lab 2 and Lab 3 size inputs finish quickly.
3. **The Lab 1–3 features:** FIFO, Reg, Reduce and Fold; then reductions, state
   machines, fixed point and 2-D memories; then line buffers and convolution.
   Each is tested with the original lab programs and independent expected answers.

**AWS F2 runs in parallel.** The first Lab 1 bundle in the course's F2 format now
exists (item 5). Next, on our existing HLS server, we compare it with pipelining
off and on: achieved initiation interval, latency and resources. This first
needs the server to have the F2 chip's device files; if it does not, synthesis
needs another Vitis host. Running on the FPGA itself waits for an F2 instance,
which is being arranged.

## Next week

- **Finish the builder:** freeze it, then fresh black-box tests and both full
  test runs.
- **Finish F2 step 1,** then Vitis synthesis on our HLS server if it has the F2
  chip.
- **Start the first core safety check:** source, the builder and a saved file
  must give the identical program.

## Questions

1. After the core work, which Lab 1 capability should come first: FIFO, Reg, or
   Reduce/Fold?
2. For F2, we generate our own top level for now. Should generated designs later
   drop into the course's existing F2 lab skeleton?
