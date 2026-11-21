---
type: reference
title: "EE 109's Spatial in Python Spatial: feature coverage"
project: spatial-python
date: 2026-11-16
updated: 2026-11-21
status: current
adoption_status: in-progress
implementation_status: partial
related:
  - "[[PY-E002 - Spatial to Python Syntax Atlas]]"
  - "[[PY-R012 - Lab1 Syntax and Host Mapping]]"
  - "[[PY-R013 - Controllers Reductions and Lab2 Mapping]]"
  - "[[PY-R014 - Convolution Windows and Lab3 Mapping]]"
  - "[[04 - Python Implementation Roadmap]]"
---

# EE 109's Spatial in Python Spatial: feature coverage

**Of the 32 Spatial constructs the Spatial parts of Labs 1 to 3 use, 20 run today**: from Python source, through the checker, on both reference engines, which must agree. Two are designed (the hardware for `par`, and `.buffer`, which becomes the compiler's choice). Ten are next, in lab order.

**Updated 21 November 2026.** `Reduce` and `Fold` (Reduce and Fold slice A1) now run, so Lab 1's four Spatial parts all run as the course writes them. Since 19 November `Reg` (slice A1) runs, and since 16 November the FIFO observations (slice A2a). The [[00 - Python Spatial Student Guide|student guide]] shows how to write and test each construct that runs.

This page is the reference behind the [language deck of 16 November 2026](https://davidydu.github.io/spatial-research-site/presentation/language/). It was taken from the Spring 2026 lecture slides (lectures 1 to 7) and the Lab 1 to 3 handouts and sources. Part 2 of each lab is HLS, not Spatial, and is not counted. Course code is referenced by name, never copied; the Spatial spellings below are the public API's. Python spellings marked *next* are the proposals of [[PY-E002 - Spatial to Python Syntax Atlas]]; those marked *designed* are the reviewed plan's.

States:
- **runs**: source, checker and both reference engines, with tests on the compiler's `main`.
- **in review**: written and tested on a branch, in the review before merging.
- **designed**: contract rules, fixtures and a blind oracle exist, or a reviewed plan.
- **next**: a proposed spelling; not started.
- **later**: taught in the slides but used by no lab.

## The 32 constructs the labs use

| # | Spatial (EE 109) | Lab parts | Python Spatial | State |
|---|---|---|---|---|
| 1 | `Accel { … }`, the host and accelerator split | every lab | `@kernel` on a typed function | runs |
| 2 | `ArgIn[Int]` | 1.3 onward | parameter `x: In[Int]` | runs |
| 3 | `ArgOut[Int]` | 1.3 onward | parameter `y: Out[Int]` | runs |
| 4 | `DRAM[Int](N)` | 1.4 onward | parameter `a: In[Dram[Int, N]]`, `Out`, `InOut` | runs |
| 5 | `setArg`, `getArg`, `setMem`, `getMem` | every lab | `check`, `prepare(program, bindings)`, typed outputs | runs |
| 6 | `SRAM[Int](n)` | 1.4 onward | `t: Sram[Int, n]` | runs |
| 7 | `SRAM[Int](m, n)` | 2.5, 3.1 | `t: Sram[Int, m, n]` | runs |
| 8 | `sram load dram(i::i+n)` | 1.4 onward | `load(t, a[i:i + n])` | runs |
| 9 | `dram(i::i+n) store sram` | 1.4 onward | `store(a[i:i + n], t)` | runs |
| 10 | 2-D tile slices | 2.5 | `a[r:r + m, c:c + n]` | runs |
| 11 | Edge tiles with `min` | 2.5 | `w: Index = min(TILE, K - k)` | runs |
| 12 | `Foreach(N by B)` | every lab | `for i in foreach(0, N, step=B):` | runs |
| 13 | `Sequential.Foreach` | 1.4 | `for i in sequential(0, N, step=B):` | runs |
| 14 | `if` / `else` | 2.3, 3.1 | `if` / `elif` / `else`; `a if c else b` | runs |
| 15 | `FIFO[Int](n)` with `enq`, `deq` | 1.5 | `q: Fifo[Int, n]`; `q.enq(x)`, `q.deq()`; also `q.peek()` | runs |
| 16 | FIFO `load` and `store` | 1.5 | `load(q, a[0:n])`, `store(a[0:n], q)` | runs |
| 17 | `Int` | every lab | `Int`, exactly 32 bits, wrapping | runs |
| 18 | `par` | 2.6, 3.1 | `foreach(…, par=P)`: accepted and recorded; the hardware that honors it is planned ([SS1](https://github.com/davidydu/spatial-py/blob/main/docs/plans/2026-11-16-f2-spatial-style.md)) | designed |
| 19 | `Reg[Int](0)`, `:=`, `.value` | 1.6 onward | `acc: Reg[Int] = 0`; `acc.value = e`, `acc.value += e` | runs |
| 20 | `SRAM(…).buffer` | 2.5 | none: results never depend on overlap, so buffering is the compiler's choice | designed |
| 21 | `Reduce` | 1.6, 3.1 | `reduce(0, N, identity=0, body=term, combine="add")`; `acc.value = reduce(…)` keeps it in a register | runs |
| 22 | `Fold` | 1.6 | `acc.value = fold(0, N, seed=acc.value, body=term, combine="add")` | runs |
| 23 | `MemReduce` | 2.1 | `mem_reduce(dst, 0, N, body=tile, combine="add")` | next |
| 24 | `MemFold` | 2.2, 2.5 | `mem_fold(dst, 0, N, body=tile, combine="add")` | next |
| 25 | `FSM` | 2.3 | `fsm(start, test=…, action=…, next=…)`, three typed helpers | next |
| 26 | `LUT` | 2.4, 3.1 | `w: Lut[Int, 3, 3] = lut(((…), (…), (…)))` | next |
| 27 | `FixPt[TRUE,_24,_8]` | 2.5 | `Fix[True, 24, 8]`, rounding stated | next |
| 28 | `LineBuffer` | 3.1 | `lb: LineBuffer[Int, 3, C]`; unpublished rows cannot be read | next |
| 29 | `RegFile` with the row shift `<<=` | 3.1 | `sr: RegFile[Int, 3, 3]`; `sr[i, :].shift(x)` | next |
| 30 | `Pipe { … }` with `sr.reset(c)` | 3.1 | `with pipe():`; `sr.reset(enable=c)` | next |
| 31 | `mux(c, a, b)` | 3.1 | `select(c, a, b)` | next |
| 32 | `abs` | 3.1 | `spatial.math.abs(x)` | next |

**By lab part.** 1.3 (registers), 1.4 (DRAM and SRAM) and 1.5 (FIFO) run; 1.4's tiled scale also runs as native C++; its F2 bundle passed the F2 kit's simulation (16 November) and ran on the F2 FPGA in experiments from 12 November, not yet an acceptance ([evidence](https://github.com/davidydu/spatial-py/blob/main/docs/evidence/f2-device-experiment/README.md)). 1.6 (controllers) runs as the course writes it, with `Reduce` and `Fold` ([Reduce and Fold evidence](https://github.com/davidydu/spatial-py/blob/main/docs/evidence/lab1-reduce-a1.md)). Lab 2 needs rows 23 to 27, and row 18 for its `par` study. Lab 3 needs rows 26 and 28 to 32 with row 21.

**The shapes already run.** The reference engines run a tiled GEMM with uneven edge tiles and a 3×3 window over a 2-D SRAM written with plain loops and SRAMs ([`tests/runtime/lab_sizes.py`](https://github.com/davidydu/spatial-py/blob/main/tests/runtime/lab_sizes.py)). What is missing is the constructs that let students write them the way the labs teach.

## Taught in the slides, used by no lab

| Spatial (lectures) | Python Spatial | State |
|---|---|---|
| FIFO `numel`, and `isEmpty` / `isFull` in the API | `q.occupancy()`, `q.is_empty()`, `q.is_full()` | runs (slice A2a) |
| `HostIO` | `InOut[Int]` | runs |
| `Parallel { … }` | `with parallel():` | next |
| `Pipe(ii = 2)` | `with pipe(ii=2):` | next |
| `FltPt`, `Float`, `Half` | `Float[24, 8]` profiles | later |
| `@struct`, `Vec`, bit views | records, vectors, packing | later |
| `gather`, `scatter` | indexed transfers with a rule for repeated indices | later |
| `StreamIn`, `StreamOut`, `Stream(*)`, `Stream.Foreach` | typed stream ports; `with stream():` and named tasks joined by channels | later |

Not taught in the course: LIFO, `Switch`, tuples, breakpoints.

## What Python Spatial changes on purpose

1. **Faults are part of the language.** An out-of-range index, a read of an unset cell, a `deq` from an empty queue, an `enq` to a full one and a zero divisor each stop the simulation with the fault's kind and source line. FPGA hardware checks nothing at run time, like Spatial's.
2. **Results never depend on the schedule.** Every program's results equal running it in order; `sequential`, `foreach`, `par` and later `pipe` choose overlap and lanes only.
3. **The interface is the signature.** Ports are typed parameters with a direction; reading an `Out` port or writing an `In` port is refused before anything runs. The host is ordinary Python.
4. **Transfers name the destination first** and check their whole range before moving anything.
5. **Counters and data are different types.** `Index` is exact; data is `Int`; `embed(Int, i)` joins them.
6. **Queue state is observed, never waited on.** Waiting belongs to streaming's channels.
7. **A reduction is a value.** `acc.value = reduce(…)` replaces `Reduce(acc)`, and `acc.value = fold(…, seed=acc.value, …)` replaces `Fold(acc)`. `reduce` must name its operation's identity (`identity=0` for add), checked; a starting value belongs in `fold(…, seed=…)`. Results never depend on `par`.

## Sources

- The compiler's [support ledger](https://github.com/davidydu/spatial-py/blob/main/docs/support-ledger.md) and [lab language contract](https://github.com/davidydu/spatial-py/blob/main/docs/lab-language-contract.md).
- Evidence: [Lab 1 Part 1](https://github.com/davidydu/spatial-py/blob/main/docs/evidence/lab1-reg-a0.md), [the FIFO, slice A1](https://github.com/davidydu/spatial-py/blob/main/docs/evidence/lab1-fifo-a1.md), [the FIFO observations, slice A2a](https://github.com/davidydu/spatial-py/blob/main/docs/evidence/lab1-fifo-a2a.md), [registers, slice A1](https://github.com/davidydu/spatial-py/blob/main/docs/evidence/lab1-reg-a1.md), [reductions, slice A1](https://github.com/davidydu/spatial-py/blob/main/docs/evidence/lab1-reduce-a1.md), [the Spatial-style hardware prototype](https://github.com/davidydu/spatial-py/blob/main/docs/evidence/hardware-performance-planning/spatial-style-2026-11-16/README.md).
- [[PY-E002 - Spatial to Python Syntax Atlas]] for the proposed spellings and complete example programs.
