---
type: guide
title: "FIFOs"
project: spatial-python
updated: 2026-11-19
status: preview
---

# FIFOs

A FIFO is a bounded queue local to a kernel: values go in at the back and come out at the front, oldest first. This page covers declaring one, its three actions, moving a whole memory in or out, asking a queue how full it is, and the faults a queue can raise. Read [[30 - Writing a Kernel]] first.

> [!note] Checked against the compiler
> Every example, output and diagnostic code on this page was run against the compiler's `main` at `f2ea92b` on 19 November 2026: captured, checked and run on both reference engines. The compiler repository is private; its links need collaborator access.

> [!warning] Reference engines only
> Queue programs check and run on the compiler's Python reference engines. Native C++ and the hardware routes refuse them today, so the functional test below uses the reference engine directly. That is a developer route; students will normally run generated C++ once native queues exist.

## Syntax

| EE 109 Spatial | Python Spatial | Result |
|---|---|---|
| `val q = FIFO[Int](n)` | `q: Fifo[Int, n]` | An empty queue of capacity `n`. |
| `q.enq(x)` | `q.enq(x)` | Unit. Adds `x` at the back. |
| `val v = q.deq()` | `v: Int = q.deq()` | `Int`. Removes and returns the oldest value. |
| `q.peek()` | `q.peek()` | `Int`. Returns the oldest value and leaves it there. |
| `q load dram(i::i+n)` | `load(q, a[i:i + n])` | Enqueues the view's cells in order. |
| `dram(i::i+n) store q` | `store(a[i:i + n], q)` | Dequeues one value into each cell, in order. |
| `q.isEmpty` | `q.is_empty()` | `Bool`. |
| `q.isFull` | `q.is_full()` | `Bool`. |
| `q.numel` | `q.occupancy()` | `Index`: how many values the queue holds. |

`n` is a positive static size: a literal, a `Meta[Size]`, a `Const[Size]`, or arithmetic on them.

## Meaning

- **Declaration and lifetime.** A queue can be declared wherever an SRAM can in a kernel body. One declared before a loop keeps its values across iterations; one declared in a loop body starts empty in every iteration. Values left when the queue's block ends are dropped; that is not a fault ([rules 1 to 7](https://github.com/davidydu/spatial-py/blob/main/docs/lab-language-contract.md#lab-1-fifo-slice-a1-12-november-2026)).
- **Actions.** `enq`, `deq` and `peek` run where they stand, in the usual evaluation order: an operand such as `b.deq()` in `a.enq(b.deq() * x)` runs first. A bare `q.deq()` statement still removes a value, and a bare `q.peek()` still checks (rules 8 to 12, 18).
- **Transfers.** `load(q, view)` and `store(view, q)` move as many values as the view has cells. That count must not exceed the capacity: otherwise the transfer faults `SHAPE` and moves nothing. Unlike a memory transfer, a queue transfer moves one item at a time, so a fault part-way keeps the items already moved (rules 13 to 17).
- **Observations.** `is_empty()`, `is_full()` and `occupancy()` read the queue at that point and change nothing. They never fault. `occupancy()` is an `Index`: use it as a loop bound, an address or a slice bound, and write `embed(Int, q.occupancy())` for an `Int` (rules 35 to 40).
- **Faults.** `deq` or `peek` on an empty queue is `QUEUE_EMPTY`; `enq` on a full one is `QUEUE_FULL`. Every effect before the fault stays (rules 21 to 23). The checker never decides a queue fault in advance: a program that will certainly fault still checks, then faults when run (rule 24). An observation does not change this: under `if q.is_empty():` a later `deq` still keeps its run-time check.
- **`par`** never reorders queue actions (rule 19).
- **Not yet.** A queue cannot be a port, and it cannot reach a helper: declared in one, captured by one or passed to one (rule 28, until slice A2b). Passing a value is fine: `h(q.deq())`.

## Example

`first_positives.py` keeps the first four positive values of `src`, in order. The guard `not chosen.is_full()` stops a fifth value from faulting `QUEUE_FULL`; because `and` is lazy, `is_full()` runs only for positive values. The final `store` moves exactly the values the queue holds. `dst` is `InOut`, so cells the store does not reach keep the values the host supplied.

```python
@kernel
def first_positives(src: In[Dram[Int, 8]], dst: InOut[Dram[Int, 4]],
                    kept: Out[Int], full: Out[Int]):
    incoming: Fifo[Int, 8]
    load(incoming, src)
    chosen: Fifo[Int, 4]
    for i in sequential(0, 8):
        v: Int = incoming.deq()
        if v > 0 and not chosen.is_full():
            chosen.enq(v)
    kept = embed(Int, chosen.occupancy())
    full = 1 if chosen.is_full() else 0
    store(dst[0:chosen.occupancy()], chosen)
```

| `src` | `dst` (seeded with zeros) | `kept` | `full` |
|---|---|---|---|
| 3, −1, 4, 0, 1, −5, 9, 2 | 3, 4, 1, 9 | 4 | 1 |
| −1, −2, 7, −3, 0, −4, −5, −6 | 7, 0, 0, 0 | 1 | 0 |

`neighbour_sums.py` uses `peek` to see the next value without taking it, and a lazy `if` expression so the last `deq` runs only when a value is left.

```python
@kernel
def neighbour_sums(src: In[Dram[Int, 6]], dst: Out[Dram[Int, 5]], last: Out[Int]):
    q: Fifo[Int, 6]
    load(q, src)
    for i in sequential(0, 5):
        first: Int = q.deq()
        dst[i] = first + q.peek()
    last = 0 if q.is_empty() else q.deq()
```

With `src` = 1, 10, 100, 1000, −5, 7, both engines give `dst` = 11, 110, 1100, 995, 2 and `last` = 7. Without its last line the program still completes; the queue's one remaining value, 7, is dropped when the kernel ends, and the trace's `deallocate` event lists it.

Lab 1 Part 4 ([handout, "Using FIFO"](https://github.com/kelayamatoz/Digital-Systems-Design-Lab/blob/b4896abffd19bcc3f319a49d7a919e1cf70d5221/lab1_part1_spatial.md#L411-L448)) asks for Part 2's scaling with queues in place of SRAMs. The handout puts it in one line: "A FIFO can be thought of as a queue." Its Python form runs on both engines ([FIFO A1 evidence](https://github.com/davidydu/spatial-py/blob/main/docs/evidence/lab1-fifo-a1.md)).

## Functional test

The expected values come from plain Python: the positive values, the first four of them, and wrapped neighbour sums. The second `neighbour_sums` case wraps.

```python
from pathlib import Path
import spatial
from spatial.runtime.reference import run_reference  # developer route: native C++ refuses queues today


def wrap_i32(value):
    return ((value + (1 << 31)) % (1 << 32)) - (1 << 31)


def checked(path, entry):
    unit = spatial.SourceUnit(module_id='guide', text=Path(path).read_text(), label=path)
    template = spatial.capture(spatial.CaptureBundle(
        entry=('guide', entry), sources=(unit,), dependencies=(), prelude=spatial.core_prelude()))
    result = spatial.check(spatial.specialize(template, {}), 'reference.guarded.v1')
    assert isinstance(result, spatial.Ok), result.diagnostics
    return result.value


def memory(name, values, access):
    return spatial.Backing.from_ints(name=name, shape=(len(values),), values=tuple(values)).view(access=access)


def run(program, bindings):
    invocation = spatial.prepare(program, bindings)
    assert isinstance(invocation, spatial.Ok), invocation.diagnostics
    return run_reference(invocation.value)


def test_first_positives():
    program = checked('first_positives.py', 'first_positives')
    for src in ((3, -1, 4, 0, 1, -5, 9, 2), (-1, -2, 7, -3, 0, -4, -5, -6)):
        kept = [x for x in src if x > 0][:4]
        seed = (0, 0, 0, 0)
        result = run(program, {'src': memory('src', src, 'read'),
                               'dst': memory('dst', seed, 'readwrite')})
        assert result.outcome == 'Completed'
        assert result.complete_outputs['dst'].to_ints() == tuple(kept) + seed[len(kept):]
        assert result.complete_outputs['kept'].to_int() == len(kept)
        assert result.complete_outputs['full'].to_int() == (1 if len(kept) == 4 else 0)


def test_neighbour_sums():
    program = checked('neighbour_sums.py', 'neighbour_sums')
    for src in ((1, 10, 100, 1000, -5, 7), (2147483647, 1, -2147483648, -1, 0, 0)):
        result = run(program, {'src': memory('src', src, 'read'),
                               'dst': spatial.Backing.empty(name='dst', shape=(5,)).view(access='write')})
        assert result.outcome == 'Completed'
        assert result.complete_outputs['dst'].to_ints() == tuple(wrap_i32(src[i] + src[i + 1]) for i in range(5))
        assert result.complete_outputs['last'].to_int() == src[5]
```

`spatial.runtime.direct.run_direct`, the second reference engine, gives the same results. A run consumes its invocation, so each engine needs its own `prepare`.

## What runs where

| Route | Status at `f2ea92b` |
|---|---|
| Source and checker | Declaration, `enq`, `deq`, `peek` and queue transfers (FIFO slice A1, 13 November); `is_empty`, `is_full` and `occupancy` (slice A2a, 16 November). |
| Reference engines (`run_reference`, `run_direct`) | All of the above; the two engines give equal results. A developer route. |
| Native C++ (`compile_native`) | Refused: `CPP.UNSUPPORTED` at the first queue declaration. Planned as slice B. |
| HLS and F2 | Refused: the F2 bundle route gives the same `CPP.UNSUPPORTED`. Vendor and device work is slice C, not started. |

## Common errors

Each was measured on both reference engines. The first four are faults when the program runs; the last two are refused by `check`.

| You wrote | Code | Cause |
|---|---|---|
| `q.enq(x)`, `a: Int = q.deq()`, then `q.deq()` again | `RUNTIME.QUEUE_EMPTY` | The second `deq` found the queue empty. |
| `q.enq(x)`, `a: Int = q.deq()`, then `q.peek()` | `RUNTIME.QUEUE_EMPTY` | `peek` also needs a value. |
| Three `q.enq(…)` into `q: Fifo[Int, 2]` | `RUNTIME.QUEUE_FULL` | The third value has no room; the first two stay. |
| `load(q, src)` with `q: Fifo[Int, 4]` and an 8-cell `src` | `RUNTIME.SHAPE` | The count exceeds the capacity; nothing moves. |
| `out = q.occupancy()` with `out: Out[Int]` | `NORMALIZE.TYPE` | An occupancy is an `Index`; the message suggests `embed(Int, q.occupancy())`. |
| `out = take(q)`, passing the queue to a helper | `NORMALIZE.UNSUPPORTED` | No queue reaches a helper yet; pass `q.deq()`. The message still names slice A1. |

## Links

- Contract: [FIFO slice A1, rules 1 to 34](https://github.com/davidydu/spatial-py/blob/main/docs/lab-language-contract.md#lab-1-fifo-slice-a1-12-november-2026); [slice A2a, rules 35 to 40](https://github.com/davidydu/spatial-py/blob/main/docs/lab-language-contract.md#lab-1-fifo-slice-a2a-queue-observations-14-november-2026).
- Evidence: [FIFO A1](https://github.com/davidydu/spatial-py/blob/main/docs/evidence/lab1-fifo-a1.md); [FIFO A2a](https://github.com/davidydu/spatial-py/blob/main/docs/evidence/lab1-fifo-a2a.md); [support ledger, lab features](https://github.com/davidydu/spatial-py/blob/main/docs/support-ledger.md#lab-language-features).
- Vault: [[00 - Python Spatial Student Guide]] · [[30 - Writing a Kernel]] · [[PY-E003 - EE109 Feature Coverage]] · [[30 - Python State and Protocol Contract]]

Next: [[41 - Registers]]
