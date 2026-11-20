---
type: guide
title: "Registers"
project: spatial-python
updated: 2026-11-19
status: preview
---

# Registers

A register holds one `Int` inside a kernel. Unlike a local such as `v: Int = e`, which names a value once, a register can be read and written as the kernel runs. Use one for a running sum, a count or a best-so-far value. Read [[30 - Writing a Kernel]] first.

> [!note] Checked against the compiler
> Every example, output and diagnostic code on this page was run against the compiler's `main` at `f2ea92b` on 19 November 2026: captured, checked and run on both reference engines. The compiler repository is private; its links need collaborator access.

> [!warning] Reference engines only
> Register programs check and run on the compiler's Python reference engines. Native C++ and the hardware routes refuse them today, so the functional test below uses the reference engine directly. That is a developer route; students will normally run generated C++ once native registers exist.

## Syntax

| EE 109 Spatial | Python Spatial | Meaning |
|---|---|---|
| `val acc = Reg[Int](0)` | `acc: Reg[Int] = 0` | A register with starting value 0. |
| `acc.value` | `acc.value` | Reads it: an `Int`. |
| `acc := e` | `acc.value = e` | Writes it. |
| `acc := acc + e` | `acc.value += e` | Reads once, adds, writes. Any `Int` operator: `-=`, `*=`, `//=`, `<<=`, … |
| `ArgIn[Int]`, `ArgOut[Int]` | `x: In[Int]`, `y: Out[Int]` | Ports, not registers: read `x`, write `y = …`. |

The starting value is a plain number (`0`, `-1`, `-2147483648`) or `embed(Int, e)` of a static value such as a `Meta[Size]`: `acc: Reg[Int] = embed(Int, N)`.

## Meaning

- **Declaration.** `acc: Reg[Int] = v` creates a register holding `v`. The element type is `Int` only, and the starting value is required and fixed when the program is checked. To start from a run-time value, declare with `0` and write `acc.value = x` next ([rules 51 to 54](https://github.com/davidydu/spatial-py/blob/main/docs/lab-language-contract.md#lab-1-reg-slice-a1-local-registers-14-november-2026)).
- **Access.** `.value` is a register's only attribute. A read gives the current value; a write stores an `Int`; `acc.value op= e` reads once, then evaluates `e`, then writes. Arithmetic wraps at 32 bits as everywhere (rules 60 to 63).
- **Lifetime.** A register declared before a loop keeps its value across the iterations. One declared inside a loop body starts over at its starting value in every iteration. One declared at the top of the kernel is fresh in every run (rule 56).
- **Original Spatial differs here.** Its simulator also restarts a register declared in a loop body, but its hardware generator, read from its code and not run, keeps the previous iteration's value. Python Spatial restarts it on every route. To keep a value across iterations, declare the register before the loop (rule 56).
- **Faults.** A register read or write never faults. The arithmetic of `acc.value //= d` can, with `d = 0`; then the write does not happen and the register keeps its old value (rules 67 and 71).
- **Order.** Reads and writes happen where they stand. `par` never reorders register updates: `foreach(0, n, par=4)` gives the sequential result (rules 64 and 65).
- **Use as an address.** `acc.value` is an `Int`, so it may be an address or a loop bound, as any `Int` may. It is not a condition: write `if acc.value != 0:` (rule 63).
- **Not a port and not a value.** `Out[Reg[Int]]` is refused: Lab 1 Part 1's ArgIn and ArgOut stay `In[Int]` and `Out[Int]` ports. The bare name `acc` is not a value: `acc + 1` and `h(acc)` are refused (rules 57 and 58).
- **Not in helpers yet.** A register cannot be declared in a helper, captured by one or passed to one until slice A2. Passing its value is fine: `h(acc.value)` (rule 76).

## Example

`tile_sums.py` sums 12 values in three tiles of four. `part` is declared in the loop body, so it starts at 0 for each tile; `grand` is declared before the loop and keeps the running total.

```python
@kernel
def tile_sums(src: In[Dram[Int, 12]], sums: Out[Dram[Int, 3]], total: Out[Int]):
    grand: Reg[Int] = 0
    for base in sequential(0, 12, step=4):
        part: Reg[Int] = 0
        tile: Sram[Int, 4]
        load(tile, src[base:base + 4])
        for j in foreach(0, 4):
            part.value += tile[j]
        sums[base // 4] = part.value
        grand.value += part.value
    total = grand.value
```

| `src` | `sums` | `total` |
|---|---|---|
| 1, 2, …, 12 | 10, 26, 42 | 78 |
| 2147483647, 1, 0, 0, −7, 7, −7, 7, 5, −6, 0, 0 | −2147483648, 0, −1 | 2147483647 |

The second row wraps twice: the first tile overflows to −2147483648, and adding −1 wraps the total back. If `part` restarted only once, before the loop, `sums` would be 10, 36, 78 in the first row.

`largest.py` finds the largest value and its first position, then passes the register's value, not the register, to a helper.

```python
@helper(effects="pure")
def at_least(v: Int, floor: Int) -> Int:
    return v if v > floor else floor


@kernel
def largest(src: In[Dram[Int, 6]], floor: In[Int], best: Out[Int], where: Out[Int]):
    top: Reg[Int] = -2147483648
    spot: Reg[Int] = -1
    for i in sequential(0, 6):
        if src[i] > top.value:
            top.value = src[i]
            spot.value = embed(Int, i)
    best = at_least(top.value, floor)
    where = spot.value
```

With `src` = 4, −2, 9, 9, 3, 8 and `floor` = 0, both engines give `best` = 9 and `where` = 2.

Lab 1 Part 6 ([handout, "Using Controllers"](https://github.com/kelayamatoz/Digital-Systems-Design-Lab/blob/b4896abffd19bcc3f319a49d7a919e1cf70d5221/lab1_part1_spatial.md#L449-L548)) sums an array with `Reduce` or `Fold` into a `Reg`. Python Spatial has no `Reduce` or `Fold` yet; they are planned next. Written with a register and two loops, like `tile_sums` above, Part 6's sum runs on both engines ([Reg A1 evidence](https://github.com/davidydu/spatial-py/blob/main/docs/evidence/lab1-reg-a1.md)).

## Functional test

The expected values are plain Python sums with 32-bit wrapping, and `max` with `index` for the first position of the largest value.

```python
from pathlib import Path
import spatial
from spatial.runtime.reference import run_reference  # developer route: native C++ refuses registers today


def wrap_i32(value):
    return ((value + (1 << 31)) % (1 << 32)) - (1 << 31)


def checked(path, entry):
    unit = spatial.SourceUnit(module_id='guide', text=Path(path).read_text(), label=path)
    template = spatial.capture(spatial.CaptureBundle(
        entry=('guide', entry), sources=(unit,), dependencies=(), prelude=spatial.core_prelude()))
    result = spatial.check(spatial.specialize(template, {}), 'reference.guarded.v1')
    assert isinstance(result, spatial.Ok), result.diagnostics
    return result.value


def run(program, bindings):
    invocation = spatial.prepare(program, bindings)
    assert isinstance(invocation, spatial.Ok), invocation.diagnostics
    return run_reference(invocation.value)


def test_tile_sums():
    program = checked('tile_sums.py', 'tile_sums')
    for src in (tuple(range(1, 13)), (2147483647, 1, 0, 0, -7, 7, -7, 7, 5, -6, 0, 0)):
        result = run(program, {
            'src': spatial.Backing.from_ints(name='src', shape=(12,), values=src).view(access='read'),
            'sums': spatial.Backing.empty(name='sums', shape=(3,)).view(access='write')})
        assert result.outcome == 'Completed'
        assert result.complete_outputs['sums'].to_ints() == tuple(wrap_i32(sum(src[b:b + 4])) for b in (0, 4, 8))
        assert result.complete_outputs['total'].to_int() == wrap_i32(sum(src))


def test_largest():
    program = checked('largest.py', 'largest')
    for src, floor in (((4, -2, 9, 9, 3, 8), 0), ((-8, -3, -5, -9, -4, -6), 0), ((-8, -3, -5, -9, -4, -6), -10)):
        result = run(program, {
            'src': spatial.Backing.from_ints(name='src', shape=(6,), values=src).view(access='read'),
            'floor': spatial.ScalarInput.from_int(value=floor)})
        assert result.outcome == 'Completed'
        assert result.complete_outputs['best'].to_int() == max(max(src), floor)
        assert result.complete_outputs['where'].to_int() == src.index(max(src))
```

`spatial.runtime.direct.run_direct`, the second reference engine, gives the same results. A run consumes its invocation, so each engine needs its own `prepare`.

## What runs where

| Route | Status at `f2ea92b` |
|---|---|
| Source and checker | Declarations, reads, writes and augmented writes (Reg slice A1, merged 19 November). |
| Reference engines (`run_reference`, `run_direct`) | All of the above; the two engines give equal results. A developer route. |
| Native C++ (`compile_native`) | Refused: `CPP.UNSUPPORTED` at the first register declaration. Planned as slice B. |
| HLS and F2 | Refused: the F2 bundle route gives the same `CPP.UNSUPPORTED`, and the Z020 route takes only native output. Vendor and device work is slice C, not started. |

## Common errors

Each was measured. All six are refused before anything runs.

| You wrote | Code | Stage | Cause |
|---|---|---|---|
| `acc += src[i]` | `NORMALIZE.IMMUTABLE` | check | Forgot `.value`: write `acc.value += src[i]`. |
| `acc: Reg[Int]` | `NORMALIZE.INITIALIZER` | check | A register needs a starting value: `acc: Reg[Int] = 0`. |
| `acc: Reg[Int] = seed` with `seed: In[Int]` | `NORMALIZE.STATIC` | check | The starting value is fixed at check time; write `acc.value = seed` after the declaration. |
| `out = double(acc)` | `NORMALIZE.UNSUPPORTED` | check | No register reaches a helper yet; pass `acc.value`. |
| `acc.reset()` | `SOURCE.UNSUPPORTED` | capture | `.value` is the only attribute; write `acc.value = 0`. |
| `out: Out[Reg[Int]]` as a kernel parameter | `NORMALIZE.TYPE` | check | A register is never a port; use `out: Out[Int]` and `out = …`. |

## Links

- Contract: [Reg slice A1, rules 51 to 81](https://github.com/davidydu/spatial-py/blob/main/docs/lab-language-contract.md#lab-1-reg-slice-a1-local-registers-14-november-2026), with the rejected-forms table of rule 75.
- Evidence: [Reg A1](https://github.com/davidydu/spatial-py/blob/main/docs/evidence/lab1-reg-a1.md); [Lab 1 Part 1 ports](https://github.com/davidydu/spatial-py/blob/main/docs/evidence/lab1-reg-a0.md); [the Part 6 example](https://github.com/davidydu/spatial-py/blob/main/examples/run_lab1_reg_reference.py); [support ledger, lab features](https://github.com/davidydu/spatial-py/blob/main/docs/support-ledger.md#lab-language-features).
- Course: Lab 1 Part 1, ArgIn and ArgOut ([handout, "Using Registers"](https://github.com/kelayamatoz/Digital-Systems-Design-Lab/blob/b4896abffd19bcc3f319a49d7a919e1cf70d5221/lab1_part1_spatial.md#L162-L288)).
- Vault: [[00 - Python Spatial Student Guide]] · [[30 - Writing a Kernel]] · [[40 - FIFOs]] · [[PY-E003 - EE109 Feature Coverage]]

Back to: [[00 - Python Spatial Student Guide]]
