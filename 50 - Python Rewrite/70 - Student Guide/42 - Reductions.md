---
type: guide
title: "Reductions"
project: spatial-python
updated: 2026-11-21
status: preview
---

# Reductions

A reduction combines one value per loop index into a single `Int`: a sum, a product, a checksum. EE 109 writes it with `Reduce` and `Fold` (Lab 1 Part 6). Python Spatial writes `reduce(…)` and `fold(…)`, two `Int` expressions. This page covers both forms, the five combiners, `step`, `par` and `schedule`, keeping a result in a register, and the errors a reduction is refused with. Read [[30 - Writing a Kernel]] and [[41 - Registers]] first.

> [!note] Checked against the compiler
> Every example, output and diagnostic code on this page was run against the compiler's `main` at `5cff363` (Reduce and Fold slice A1's merge) on 21 November 2026: captured, checked and run on both reference engines. The compiler repository is private; its links need collaborator access.

> [!warning] Reference engines only
> Reduction programs check and run on the compiler's Python reference engines. Native C++ and the hardware routes refuse them today, so the functional test below uses the reference engine directly. That is a developer route; students will normally run generated C++ once native reductions exist.

## Syntax

```
reduce(start, end, identity=e, body=h, combine=c, step=1, par=1, schedule="foreach")
fold(start, end, seed=x, body=h, combine=c, step=1, par=1, schedule="foreach")
```

`start` and `end` are positional; everything else is a keyword, in any order. `identity` (or `seed`), `body` and `combine` are required; `step`, `par` and `schedule` default as shown.

| EE 109 Spatial | Python Spatial | Notes |
|---|---|---|
| `Reduce(acc)(N by B){ i => … }{_+_}` | `acc.value = reduce(0, N, step=B, identity=0, body=h, combine="add")` | A value, written to the register once. `acc`'s old value is not used, as in EE 109 ([handout line 483](https://github.com/kelayamatoz/Digital-Systems-Design-Lab/blob/b4896abffd19bcc3f319a49d7a919e1cf70d5221/lab1_part1_spatial.md#L483)). |
| `Reduce(0)(N by 1){ i => … }{_+_}` | `reduce(0, N, identity=0, body=h, combine="add")` | No register needed: use it as any `Int`. |
| `Fold(acc)(N by B){ i => … }{_+_}` | `acc.value = fold(0, N, step=B, seed=acc.value, body=h, combine="add")` | The seed counts once. |
| `Sequential.Reduce(acc)(…)`, `Sequential.Fold` | `reduce(…, schedule="sequential")` | One iteration at a time; `par` must be 1. |
| `Reduce(acc)(N by 1 par P)` | `reduce(…, par=P)` | `P` is a static positive size. A request; it never changes the result. |
| the map body `{ i => … }` | `@helper` `def h(i: Index) -> Int:`, declared before the reduction, named by `body=h` | Exactly one `Index` formal and an `Int` result. |
| `{_+_}`, `{_*_}`, `{_&_}`, `{_\|_}`, `{_^_}` | `combine="add"`, `"mul"`, `"and"`, `"or"`, `"xor"` | The only five. |

`reduce` and `fold` come with the prelude, so no import is needed; `from spatial import reduce, fold` is accepted too. Both names are reserved: `reduce: Int = 1` is `SOURCE.BINDING`.

## Meaning

Each combiner is an `Int` operator you already have, with an identity that changes nothing ([rule 85](https://github.com/davidydu/spatial-py/blob/main/docs/lab-language-contract.md#lab-1-reduce-and-fold-slice-a1-scalar-reductions-19-november-2026)):

| `combine` | Operator | Identity |
|---|---|---|
| `"add"` | `+`, wrapping at 32 bits | 0 |
| `"mul"` | `*`, wrapping at 32 bits | 1 |
| `"and"` | bitwise `&` | −1 (all 32 bits set) |
| `"or"` | bitwise `\|` | 0 |
| `"xor"` | bitwise `^` | 0 |

Any other string is `NORMALIZE.MODE`, `"min"` and `"max"` included for now.

- **An ordered recurrence.** Start from the identity (`reduce`) or the seed (`fold`). For each index that `foreach(start, end, step=step)` visits, in order, call the body once and combine its result into the running value, the running value on the left. The result is the last running value. An empty domain calls nothing and gives the identity or the seed ([rules 84 and 88](https://github.com/davidydu/spatial-py/blob/main/docs/lab-language-contract.md#lab-1-reduce-and-fold-slice-a1-scalar-reductions-19-november-2026)).
- **Why the grouping never matters.** Each combiner never faults, is associative and commutative on every 32-bit word, and its identity changes nothing. So any grouping or order of the contributions (a tree over `par` lanes, partial sums merged at the end, a short last lane group padded with the identity) gives the ordered result bit for bit. That is why the set is closed: `"sub"` or a helper as the combiner could break it. Only values regroup; the body's calls and their effects keep their order (rule 86).
- **The identity is checked.** `identity=` is a static `Int` that must equal the combiner's identity as a 32-bit word, so `identity=-1` for `"and"`. Anything else is `NORMALIZE.NEUTRAL`. To start from another value, write `fold(…, seed=…)` (rule 87). EE 109's `Reduce(c)` with another `c` pads a partial lane group with `c`, so its result can depend on `par`; Python Spatial refuses that form (rule 112).
- **A reduction is a value.** It goes wherever an `Int` goes: `out = reduce(…) - fold(…)`, `total += reduce(…)`, an address `src[reduce(…)]`, `n: Index = reduce(…)`, a helper's `return`, another reduction's body. It is not a condition: write `if reduce(…) != 0:` (rules 89 and 95).
- **A register is read once and written once.** In `acc.value = fold(…, seed=acc.value, …)` the register is read, as the seed, before the first body call, and written once, after the last. If a body call faults, nothing is written: `acc` keeps its value, and the effects of earlier calls stay (rules 89 and 98). On an empty domain the write still happens: the identity for `reduce`, `acc`'s own value for `fold`.
- **Original Spatial differs here.** Its `Reduce(acc)` leaves `acc` unchanged on an empty domain, where `acc.value = reduce(…)` writes the identity, and its reductions store into `acc` at every iteration, where Python Spatial writes once. The values differ only on an empty domain (rule 112).
- **`par` and `schedule` are requests.** Results, faults and traces are the same for every `par` and both schedules: `par` never drops, adds or reorders a body call. `schedule="sequential"` with `par` other than 1 is refused (rule 94).
- **Each contribution is one helper call.** Every index makes one ordinary call of the body, with its own `call_enter` and `call_return` events, fresh locals and its own faults: an SRAM declared in the body is a new one in every call. A body may load, branch, loop and hold a reduction of its own (rules 90, 91 and 109). Use plain `@helper`: a pure body cannot read captured memory (`LAYOUT.TOKEN`) or hold a run-time check (`CHECK.UNDISCHARGED`), and even `embed(Int, i)` holds one. No register or queue reaches a body yet (rules 76 and 28): bring a register's value in as the seed, `seed=acc.value`.
- **The domain.** `start`, `end` and, where written, `step` and `seed` are evaluated once, in the order written, before the first body call; a body that changes what they read does not change the domain. `step` may be negative or known only at run time, and a zero step faults `RUNTIME.ZERO_STEP` (rules 92 and 93).

## Example

`l1_norm.py` has the shape of Lab 1 Part 6: it sums the absolute values of `src` in tiles of `TILE`. The outer reduction takes the tiles one at a time; its body loads a tile into an SRAM and sums it with an inner reduction, whose body is a helper nested in the outer body.

```python
@kernel
def l1_norm(N: Meta[Size], TILE: Meta[Size], src: In[Dram[Int, N]], norm: Out[Int]):
    @helper
    def tile_norm(base: Index) -> Int:
        tile: Sram[Int, TILE]
        load(tile, src[base:base + TILE])

        @helper
        def magnitude(j: Index) -> Int:
            return tile[j] if tile[j] >= 0 else -tile[j]

        return reduce(0, TILE, identity=0, body=magnitude, combine="add", par=4)

    norm = reduce(0, N, step=TILE, schedule="sequential", identity=0, body=tile_norm, combine="add")
```

With `N` = 12 and `TILE` = 4:

| `src` | `norm` |
|---|---|
| 3, −1, 4, −1, 5, −9, 2, −6, 5, 3, −5, 8 | 52 |
| −2147483648, 1, 0, 0, 2147483647, 0, 0, 0, −1, 0, 0, 0 | 1 |

The second row wraps: negating −2147483648 gives −2147483648 in 32 bits, and the total wraps round to 1. Each run makes 15 body calls, 3 of `tile_norm` and 12 of `magnitude`, and allocates the tile 3 times. The inner `par` written as 1, 2, `TILE` or 16, or left out, and the outer `schedule` written as `"foreach"`, give the same outputs and the same trace. `N` must be a multiple of `TILE`: with `N` = 10 the last load runs past `src` and faults `RUNTIME.BOUNDS`.

Lab 1 Part 6's demo ([handout, "Using Controllers"](https://github.com/kelayamatoz/Digital-Systems-Design-Lab/blob/b4896abffd19bcc3f319a49d7a919e1cf70d5221/lab1_part1_spatial.md#L485-L530)) has this shape, with a plain sum and the result kept in a register. Written with `reduce`, the demo and the Fold exercise run on both engines ([the compiler's Part 6 example](https://github.com/davidydu/spatial-py/blob/main/examples/run_lab1_reduce_reference.py)).

`ledger.py` folds a list of moves into a balance. The register cannot start from a port's value, since its starting value is fixed at check time, so it starts at 0 and takes `opening` next ([[41 - Registers]]); the `fold` then uses it as its seed.

```python
@kernel
def ledger(opening: In[Int], n: In[Index], moves: In[Dram[Int, 8]], closing: Out[Int]):
    balance: Reg[Int] = 0
    balance.value = opening

    @helper
    def move(i: Index) -> Int:
        return moves[i]

    balance.value = fold(0, n, seed=balance.value, body=move, combine="add")
    closing = balance.value
```

With `moves` = 5, −20, 7, 1, −3, 40, −2, 9:

| `opening` | `n` | `closing` |
|---|---|---|
| 100 | 8 | 137 |
| 100 | 0 | 100 |
| 2147483647 | 1 | −2147483644 |

With `n` = 0 no body call runs and the seed comes back. `balance`'s events are `allocate`, `write` (the opening), `read` (the seed), then the `n` body calls, one `write`, a `read` for `closing` and `deallocate`. Writing `seed=opening` and no register gives the same outputs.

`checks.py` makes three checks over eight words: an `xor` parity, a wrapping product and the bits common to all.

```python
@kernel
def checks(words: In[Dram[Int, 8]], parity: Out[Int], product: Out[Int], common: Out[Int]):
    @helper
    def word(i: Index) -> Int:
        return words[i]

    parity = reduce(0, 8, identity=0, body=word, combine="xor", par=4)
    product = reduce(0, 8, identity=1, body=word, combine="mul", par=4)
    common = reduce(0, 8, identity=-1, body=word, combine="and", schedule="sequential")
```

| `words` | `parity` | `product` | `common` |
|---|---|---|---|
| 3, 5, 7, 11, 13, 17, 19, 23 | 18 | 111546435 | 1 |
| 100000, 100000, 3, −1, 1, 1, 1, 1 | −4 | 64771072 | 0 |

The second product wraps: 100000 × 100000 × 3 × −1 is −30000000000, which is 64771072 modulo 2^32. Writing `par=1`, `par=3` (a short last lane group of two), `par=8`, no `par`, or `"foreach"` for `common`, gives the same outputs and the same trace on both engines.

## Functional test

The expected values come from plain Python with 32-bit wrapping, with no tiles and no lanes: `abs` and `sum` for the norm, the sum of the first `n` moves for the ledger, and `functools.reduce` and `math.prod` for the checks.

```python
import functools
import math
import operator
from pathlib import Path
import spatial
from spatial.runtime.reference import run_reference  # developer route: native C++ refuses reductions today


def wrap_i32(value):
    return ((value + (1 << 31)) % (1 << 32)) - (1 << 31)


def checked(path, entry, meta):
    unit = spatial.SourceUnit(module_id='guide', text=Path(path).read_text(), label=path)
    template = spatial.capture(spatial.CaptureBundle(
        entry=('guide', entry), sources=(unit,), dependencies=(), prelude=spatial.core_prelude()))
    result = spatial.check(spatial.specialize(template, meta), 'reference.guarded.v1')
    assert isinstance(result, spatial.Ok), result.diagnostics
    return result.value


def memory(name, values):
    return spatial.Backing.from_ints(name=name, shape=(len(values),), values=tuple(values)).view(access='read')


def run(program, bindings):
    invocation = spatial.prepare(program, bindings)
    assert isinstance(invocation, spatial.Ok), invocation.diagnostics
    result = run_reference(invocation.value)
    assert result.outcome == 'Completed', result.diagnostics
    return {name: value.to_int() for name, value in result.complete_outputs.items()}


def test_l1_norm():
    meta = {('l1_norm', 'N'): spatial.MetaSize(12), ('l1_norm', 'TILE'): spatial.MetaSize(4)}
    program = checked('l1_norm.py', 'l1_norm', meta)
    for src in ((3, -1, 4, -1, 5, -9, 2, -6, 5, 3, -5, 8), (-2147483648, 1, 0, 0, 2147483647, 0, 0, 0, -1, 0, 0, 0)):
        assert run(program, {'src': memory('src', src)}) == {'norm': wrap_i32(sum(abs(x) for x in src))}


def test_ledger():
    program = checked('ledger.py', 'ledger', {})
    moves = (5, -20, 7, 1, -3, 40, -2, 9)
    for opening, n in ((100, 8), (100, 0), (2147483647, 1), (-7, 5)):
        outputs = run(program, {'opening': spatial.ScalarInput.from_int(value=opening),
                                'n': spatial.IndexInput(value=n), 'moves': memory('moves', moves)})
        assert outputs == {'closing': wrap_i32(opening + sum(moves[:n]))}


def test_checks():
    program = checked('checks.py', 'checks', {})
    for words in ((3, 5, 7, 11, 13, 17, 19, 23), (100000, 100000, 3, -1, 1, 1, 1, 1)):
        assert run(program, {'words': memory('words', words)}) == {
            'parity': functools.reduce(operator.xor, words, 0),
            'product': wrap_i32(math.prod(words)),
            'common': functools.reduce(operator.and_, words, -1)}
```

`spatial.runtime.direct.run_direct`, the second reference engine, gives the same results. A run consumes its invocation, so each engine needs its own `prepare`.

## What runs where

| Route | Status at `5cff363` |
|---|---|
| Source and checker | `reduce` and `fold` over `Int`: the five combiners, `step`, `par`, `schedule` and nested reductions, in kernels and helpers (Reduce and Fold slice A1, merged 21 November). |
| Reference engines (`run_reference`, `run_direct`) | All of the above; the two engines give equal results. A developer route. |
| Native C++ (`compile_native`) | Refused with `CPP.UNSUPPORTED` at the first construct it cannot emit: a reduction's loop ("Loop carries are not admitted") in `l1_norm` and `checks`, the `In[Index]` port in `ledger`, the register's declaration in Lab 1 Part 6's demo. Planned as slice B. |
| F2 and Z020 | Refused: the F2 bundle route gives the same `CPP.UNSUPPORTED`, and the Z020 route takes only native output. The HLS and FPGA form is slice C, not started; there `par` and `schedule` will mean what Spatial's `Reduce` and `Sequential.Reduce` mean, with the same results (rule 112). |

## Common errors

Each was measured. All seven are refused before anything runs.

| You wrote | Code | Stage | Cause |
|---|---|---|---|
| `reduce(0, 8, body=word, combine="add")` | `NORMALIZE.ARGUMENTS` | check | No identity: the message says `reduce` requires `identity`. |
| `reduce(0, 8, identity=5, body=word, combine="add")` | `NORMALIZE.NEUTRAL` | check | The identity of `"add"` is 0 (of `"mul"`, 1); the message says a starting value belongs in `fold(..., seed=...)`. |
| `fold(0, 8, accumulator=acc, body=word, combine="add")` | `NORMALIZE.ARGUMENTS` | check | The message: "A reduction takes no accumulator=; it is a value: write acc.value = fold(..., seed=acc.value, ...)". |
| `body=word` with `def word(i: Int) -> Int` | `NORMALIZE.TYPE` | check | A body is `(i: Index) -> Int`; the message adds `word is (i: Int) -> Int`. |
| `combine="sum"` | `NORMALIZE.MODE` | check | The message names the five strings; write `"add"`. |
| `body=lambda i: words[i]` | `SOURCE.UNSUPPORTED` | capture | Declare a `@helper` and name it. The message does not say this. |
| `schedule="sequential", par=4` | `NORMALIZE.PARALLELISM` | check | A sequential reduction runs one iteration at a time, so its `par` is 1. The loop `sequential(0, 8, par=4)` is refused at capture instead (`SOURCE.ARGUMENTS`). |

## Links

- Contract: [Reduce and Fold slice A1, rules 82 to 112](https://github.com/davidydu/spatial-py/blob/main/docs/lab-language-contract.md#lab-1-reduce-and-fold-slice-a1-scalar-reductions-19-november-2026), with the rejected forms of rule 106 and the departures from Spatial in rule 112.
- Plan and evidence: [the Reduce and Fold plan](https://github.com/davidydu/spatial-py/blob/main/docs/plans/2026-11-16-lab1-reduce-fold.md); [the slice's evidence](https://github.com/davidydu/spatial-py/blob/main/docs/evidence/lab1-reduce-a1.md); [the Part 6 example](https://github.com/davidydu/spatial-py/blob/main/examples/run_lab1_reduce_reference.py); [the slice's API note](https://github.com/davidydu/spatial-py/blob/main/docs/evidence/lab1-reduce-a1-holdout-api.md); [support ledger](https://github.com/davidydu/spatial-py/blob/main/docs/support-ledger.md). The repository is private, and these links need collaborator access.
- Course: Lab 1 Part 6 ([handout, "Using Controllers"](https://github.com/kelayamatoz/Digital-Systems-Design-Lab/blob/b4896abffd19bcc3f319a49d7a919e1cf70d5221/lab1_part1_spatial.md#L449-L548)): `Reduce` at [lines 476 to 483](https://github.com/kelayamatoz/Digital-Systems-Design-Lab/blob/b4896abffd19bcc3f319a49d7a919e1cf70d5221/lab1_part1_spatial.md#L476-L483), the demo at [485 to 530](https://github.com/kelayamatoz/Digital-Systems-Design-Lab/blob/b4896abffd19bcc3f319a49d7a919e1cf70d5221/lab1_part1_spatial.md#L485-L530), `Fold` and the exercise at [532 to 545](https://github.com/kelayamatoz/Digital-Systems-Design-Lab/blob/b4896abffd19bcc3f319a49d7a919e1cf70d5221/lab1_part1_spatial.md#L532-L545).
- Vault: [[00 - Python Spatial Student Guide]] · [[30 - Writing a Kernel]] · [[41 - Registers]] · [[40 - FIFOs]] · [[PY-E003 - EE109 Feature Coverage]]

Back to: [[00 - Python Spatial Student Guide]]
