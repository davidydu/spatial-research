---
type: guide
title: "Writing a kernel"
project: spatial-python
updated: 2026-11-19
status: preview
---

# Writing a kernel

A kernel is the accelerator part of a Python Spatial program. It is a typed Python function that the compiler reads, checks and runs; it is never imported or executed as ordinary Python. This page covers ports, sizes, `Int` and `Index`, SRAMs and transfers, loops, branches, helpers, and the faults a run can stop with. Queues and registers have their own pages: [[40 - FIFOs]] and [[41 - Registers]].

> [!note] Checked against the compiler
> Every example, output and diagnostic code on this page was run against the compiler's `main` at `f2ea92b` on 19 November 2026: captured, checked and run on both reference engines, and as native C++ where the page says so. The compiler repository is private; its links need collaborator access.

## Syntax

| EE 109 Spatial | Python Spatial | Notes |
|---|---|---|
| `Accel { … }` | `@kernel` on a function | Its parameters are its ports. |
| `ArgIn[Int]` | `x: In[Int]` | Read by its name. Also `flag: In[Bool]` and `n: In[Index]`. |
| `ArgOut[Int]` | `y: Out[Int]` | Written with `y = …`; never read. |
| `HostIO` | `y: InOut[Int]` | Read and written. |
| `DRAM[Int](N)` | `a: In[Dram[Int, N]]`, `Out[…]`, `InOut[…]` | Any rank: `Dram[Int, R, C]`. |
| `val N = 32` | `N: Meta[Size]` | A size fixed before checking. |
| `Int` | `Int` | Signed 32 bits, wrapping. |
| — | `Index` | An exact integer for counters, sizes and addresses. |
| — | `embed(Int, i)` | Turns an `Index` into an `Int`. |
| `val v = e` | `v: Int = e`, `i: Index = e` | Every new name is declared with a type, once. |
| `SRAM[Int](n)`, `SRAM[Int](m, n)` | `t: Sram[Int, n]`, `t: Sram[Int, m, n]` | Starts with every cell unset. |
| `sram(i)`, `sram(i) = v` | `t[i]`, `t[i] = v`, `t[i, j]` | |
| `sram load dram(k::k+n)` | `load(t, a[k:k + n])` | Destination first. |
| `dram(k::k+n) store sram` | `store(a[k:k + n], t)` | Destination first. |
| 2-D tile | `load(t, a[r:r + 2, c:c + 3])` | |
| `Foreach(N by B) { i => … }` | `for i in foreach(0, N, step=B):` | `step` may be negative. |
| `Sequential.Foreach(N by B)` | `for i in sequential(0, N, step=B):` | |
| `Foreach(N by 1 par P)` | `for i in foreach(0, N, par=P):` | `P` is a static positive size. |
| `if` / `else` | `if` / `elif` / `else`; `a if c else b` | Conditions are `Bool`. |
| a Scala function | `@helper(effects="pure")` or `@helper` | Typed, never recursive. |

## Meaning

- **Ports.** A kernel's parameters are its interface. Reading an `Out` port or writing an `In` port is refused before anything runs ([initial contract, ports](https://github.com/davidydu/spatial-py/blob/main/docs/initial-language-contract.md#ports-shape-and-memory)).
- **`Int` and `Index`.** `Int` wraps at 32 bits; `/` truncates toward zero, `//` floors, `%` follows `//`. `Index` never wraps and has no `/`. The two do not mix in arithmetic: write `embed(Int, i)`. An `Int` may stand where an `Index` is needed in an address, an `Index` declaration or a loop bound ([numeric types](https://github.com/davidydu/spatial-py/blob/main/docs/initial-language-contract.md#program-and-numeric-types); [[20 - Python Numeric Contract]]).
- **Locals are immutable.** `v: Int = e` names a value once. A value that changes over time lives in an SRAM cell, an `InOut` port or a [[41 - Registers|register]].
- **`Meta[Size]`** values are supplied by `specialize`, before `check`. They can size memories and be a `par`.
- **SRAM.** A new SRAM has every cell unset. An SRAM declared in a loop body is a fresh one in every iteration.
- **Transfers** name the destination first. A memory transfer checks its shapes and every cell before it writes anything, then copies in order.
- **Loops** read their bounds once, at entry. Today every route runs `foreach` iterations in order, exactly as `sequential` does. `par` is a request recorded for a later hardware plan; it never changes results.
- **Branches.** `if`/`elif`/`else`, `a if c else b`, `and` and `or` run only the selected side.
- **Helpers.** `@helper(effects="pure")` computes a value from its arguments and touches no memory. A helper that reads or writes memory it is given uses plain `@helper`. Helpers are never recursive.

The full rules are in the [initial language contract](https://github.com/davidydu/spatial-py/blob/main/docs/initial-language-contract.md#source-grammar) and [[10 - Python Language Contract]].

## Example

`spread.py` moves each element away from zero by its position, then clamps it to `[-limit, limit]`. It works in tiles of `TILE`; with `N = 10` and `TILE = 4` the last tile has two elements. It has the shape of Lab 1 Part 2 ([handout, "Using DRAM and SRAM"](https://github.com/kelayamatoz/Digital-Systems-Design-Lab/blob/b4896abffd19bcc3f319a49d7a919e1cf70d5221/lab1_part1_spatial.md#L289-L410)), with an edge tile, a helper and a branch added.

```python
@helper(effects="pure")
def clamp(v: Int, lo: Int, hi: Int) -> Int:
    if v < lo:
        return lo
    elif v > hi:
        return hi
    else:
        return v


@kernel
def spread(N: Meta[Size], TILE: Meta[Size],
           src: In[Dram[Int, N]], limit: In[Int], dst: Out[Dram[Int, N]]):
    for base in sequential(0, N, step=TILE):
        width: Index = min(TILE, N - base)
        tile: Sram[Int, TILE]
        load(tile[0:width], src[base:base + width])
        for j in foreach(0, width, par=2):
            pos: Int = embed(Int, base + j)
            moved: Int = tile[j] + pos if tile[j] >= 0 else tile[j] - pos
            tile[j] = clamp(moved, -limit, limit)
        store(dst[base:base + width], tile[0:width])
```

With `src` = 5, −3, 0, 40, −50, 7, −1, 2, 100, −100 and `limit` = 20, both reference engines and native C++ give `dst` = 5, −4, 2, 20, −20, 12, −7, 9, 20, −20. Writing `par=4`, or no `par`, gives the same output.

`transpose.py` uses 2-D tiles: it copies a 4 × 6 matrix into its 6 × 4 transpose, one 2 × 3 tile at a time.

```python
@kernel
def transpose(a: In[Dram[Int, 4, 6]], b: Out[Dram[Int, 6, 4]]):
    for r in sequential(0, 4, step=2):
        for c in sequential(0, 6, step=3):
            t_in: Sram[Int, 2, 3]
            t_out: Sram[Int, 3, 2]
            load(t_in, a[r:r + 2, c:c + 3])
            for i in foreach(0, 2):
                for j in foreach(0, 3):
                    t_out[j, i] = t_in[i, j]
            store(b[c:c + 3, r:r + 2], t_out)
```

With `a[r][c] = 10r + c`, both reference engines give `b[c][r] = 10r + c`. Native C++ refuses it (below).

## Functional test

Students normally run generated C++. `compile_native` compiles a checked kernel once; the handle then runs many inputs. It needs a C++17 compiler (`CXX` selects it). The expected values come from a plain-Python statement of the algorithm, with no tiles and with 32-bit wrapping at each `Int` operation, as [[20 - Testing Your Own Project]] describes. The second case wraps.

```python
from pathlib import Path
import spatial
from spatial.runtime.reference import run_reference  # developer route, used for the 2-D test only


def wrap_i32(value):
    return ((value + (1 << 31)) % (1 << 32)) - (1 << 31)


def checked(path, entry, meta):
    unit = spatial.SourceUnit(module_id='guide', text=Path(path).read_text(), label=path)
    template = spatial.capture(spatial.CaptureBundle(
        entry=('guide', entry), sources=(unit,), dependencies=(), prelude=spatial.core_prelude()))
    result = spatial.check(spatial.specialize(template, meta), 'reference.guarded.v1')
    assert isinstance(result, spatial.Ok), result.diagnostics
    return result.value


def spread_expected(src, limit):
    lo, hi = wrap_i32(-limit), limit
    out = []
    for i, x in enumerate(src):
        moved = wrap_i32(x + i) if x >= 0 else wrap_i32(x - i)
        out.append(lo if moved < lo else hi if moved > hi else moved)
    return tuple(out)


def test_spread_native():
    meta = {('spread', 'N'): spatial.MetaSize(10), ('spread', 'TILE'): spatial.MetaSize(4)}
    built = spatial.compile_native(checked('spread.py', 'spread', meta))
    assert isinstance(built, spatial.Ok), built.diagnostics
    cases = [((5, -3, 0, 40, -50, 7, -1, 2, 100, -100), 20),
             ((0, 0, 0, 2147483647, -2147483648, 1, 2, 3, 4, 5), 2147483647)]
    assert spread_expected(*cases[0]) == (5, -4, 2, 20, -20, 12, -7, 9, 20, -20)  # by hand
    with built.value as kernel:
        for src, limit in cases:
            result = kernel.run({
                'src': spatial.Backing.from_ints(name='src', shape=(10,), values=src).view(access='read'),
                'limit': spatial.ScalarInput.from_int(value=limit),
                'dst': spatial.Backing.empty(name='dst', shape=(10,)).view(access='write')})
            assert isinstance(result, spatial.Ok), result.diagnostics
            assert result.value.outcome == 'Completed'
            assert result.value.outputs['dst'] == spread_expected(src, limit)


def test_transpose_reference():
    a = tuple(10 * r + c for r in range(4) for c in range(6))
    invocation = spatial.prepare(checked('transpose.py', 'transpose', {}), {
        'a': spatial.Backing.from_ints(name='a', shape=(4, 6), values=a).view(access='read'),
        'b': spatial.Backing.empty(name='b', shape=(6, 4)).view(access='write')})
    run = run_reference(invocation.value)
    assert run.outcome == 'Completed'
    assert run.complete_outputs['b'].to_ints() == tuple(a[r * 6 + c] for c in range(6) for r in range(4))
```

The 2-D test imports the reference engine directly. That is a developer route, used here only because native C++ does not yet admit rank-2 memory.

## Faults

A fault stops the run. It returns no outputs, and every write made before it stays, visible in the result's snapshot (native: `buffers` and `initialized`). Each row was measured on both reference engines and as native C++.

| Fault | Example | Reference engines | Native C++ | Refused at check instead when |
|---|---|---|---|---|
| Out of range | `dst[i + 1] = src[i]` for `i` in 0 to 3, a 4-cell `dst` | `RUNTIME.BOUNDS` at `i = 3`; `dst[1]` to `dst[3]` written | `bounds`, the same cells | never |
| Unset cell | write `t[0]` and `t[1]`, then copy `t[0]` to `t[3]` out | `RUNTIME.UNINITIALIZED` at `t[2]`; `dst[0]`, `dst[1]` written | `uninitialized` | a top-level read of a fresh SRAM at a constant address: `CHECK.UNINITIALIZED` |
| Zero divisor | `out = a // b` with `b = 0` | `RUNTIME.ZERO_DIVISOR` | `zero_divisor` | `out = x // 0` before any other statement: `GUARD_LOWERING.ACTIVE_FALSE` |
| Shapes differ | `load(t, src[0:3])` into a 4-cell `t` | `RUNTIME.SHAPE`; nothing written | `shape` | never |

## What runs where

| Route | Status at `f2ea92b` |
|---|---|
| Source and checker | Every form on this page. |
| Reference engines (`run_reference`, `run_direct`) | Every form on this page; both engines give equal results for these examples. A developer route. |
| Native C++ (`compile_native`) | `Int` and `Bool` input ports, scalar `Out`/`InOut`, rank-1 memories with fixed extents, loops, branches and scalar helpers: `spread` runs. Refused with `CPP.UNSUPPORTED`: rank-2 memory (`transpose`, "Only rank-one memory is admitted"), an `In[Index]` port, queues and registers. |
| HLS and F2 | Developer tools, no student command yet. Saved bundles passed Vitis synthesis and RTL co-simulation on the Z020 profile ([ledger](https://github.com/davidydu/spatial-py/blob/main/docs/support-ledger.md)); the F2 bundle for Lab 1 Part 2 passed the F2 kit's simulation on 16 November and ran on an F2 FPGA in experiments from 12 November, not yet an acceptance ([evidence](https://github.com/davidydu/spatial-py/blob/main/docs/evidence/f2-device-experiment/README.md)). The F2 route refuses a scalar `Out` port (`VITIS_F2.UNSUPPORTED_PORT`). No backend uses `par` yet. |

## Common errors

Each was measured; the stage is where it is refused.

| You wrote | Code | Stage | Cause |
|---|---|---|---|
| `y: Int = out` with `out: Out[Int]` | `NORMALIZE.CAPABILITY` | check | An `Out` port is never read. |
| `v = v + 1` after `v: Int = x` (or `x = 3` on an `In` port) | `NORMALIZE.IMMUTABLE` | check | Locals and `In` ports cannot be rebound; use a register. |
| `dst[i] = src[i] + i` | `NORMALIZE.TYPE` | check | `Int` plus `Index`; write `embed(Int, i)`. |
| `y = x + 1` with no `y: Int` | `SOURCE.BINDING` | capture | Every new name needs a typed declaration. |
| `if x:` with `x: In[Int]` | `NORMALIZE.TYPE` | check | A condition is a `Bool`; write `if x != 0:`. |
| `@helper(effects="pure")` on a helper that reads an SRAM | `LAYOUT.TOKEN` | check | A pure helper touches no memory; use `@helper`. The message does not say this. |

## Links

- Contract: [initial language contract](https://github.com/davidydu/spatial-py/blob/main/docs/initial-language-contract.md) (numeric types, grammar, ports, transfers, the static-certainty clarification of 3 November).
- Status: [support ledger](https://github.com/davidydu/spatial-py/blob/main/docs/support-ledger.md); [E1 public workflow evidence](https://github.com/davidydu/spatial-py/blob/main/docs/evidence/e1-public-workflow.md); [Lab 1 Part 1 ports](https://github.com/davidydu/spatial-py/blob/main/docs/evidence/lab1-reg-a0.md).
- Course: Lab 1 Part 1, ports ([handout, "Using Registers"](https://github.com/kelayamatoz/Digital-Systems-Design-Lab/blob/b4896abffd19bcc3f319a49d7a919e1cf70d5221/lab1_part1_spatial.md#L162-L288)).
- Vault: [[00 - Python Spatial Student Guide]] · [[10 - Testing a Spatial Program]] · [[PY-E003 - EE109 Feature Coverage]] · [[PY-E002 - Spatial to Python Syntax Atlas]] · [[80 - Initial Compiler Goal]]

Next: [[40 - FIFOs]] · [[41 - Registers]]
