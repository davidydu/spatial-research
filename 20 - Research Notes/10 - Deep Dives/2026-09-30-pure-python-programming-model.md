---
type: deep-dive
topic: pure-python-programming-model
title: "Pure Python Spatial — programming model first"
date: 2026-09-30
session: 2026-09-30
status: exploratory
feeds_spec: []
source_files:
  - "spatial@e7a8f2f:test/spatial/tests/ee109/Lab1Part2DramSramExample.scala:6-43"
  - "spatial@e7a8f2f:test/spatial/tests/feature/control/ReduceTiny.scala:7-37"
  - "spatial@e7a8f2f:test/spatial/tests/feature/control/FIFOBranch.scala:9-31"
related:
  - "[[00 - Python Mapping Overview]]"
  - "[[D-26-02-student-surface-comparison]]"
  - "[[D-26-final-architecture]]"
---

# Pure Python Spatial — programming model first

Continue from [[00 - Python Rewrite Index|Python Spatial research]] and [[PY-R001 - Programming Model Study|the paired programming-model study]]. This dated note preserves the initial discussion; [[D-27]] records the agreed direction.

## Professor feedback

On 30 September 2026, David reported that the professor wants a **pure Python rewrite of Spatial**. The next step is to understand what that rewrite looks like in Python, then investigate lowering it to HLS.

This replaces the Python-frontend/Rust-core recommendation in [[D-26-final-architecture]]. The implementation language is now a requirement: the Spatial compiler and its semantic logic should be Python. This is not merely a Python wrapper around the Rust compiler. HLS remains a later target; invoking vendor tools later does not make them the compiler's semantic core.

The feedback selects a direction and an order of work. It does not settle the Python API, source capture method, supported subset, internal representation, or HLS strategy. The sketches below are research proposals, not implemented APIs or an approved detailed design.

David subsequently clarified that the professor assumes abundant coding-agent capability, so Rust's implementation type-safety and development-discipline advantages should not decide the language choice. [[2026-09-30-pure-python-feasibility|The feasibility assessment]] concludes that a Python implementation can supply the full compiler; correctness and performance remain properties to validate in the chosen implementation.

## First deliverable

Prepare a small set of readable Python Spatial programs, with a plain explanation of what each statement means. Use them to decide how programmers express memory, loops, reductions, branches, and state. Describe enough of the Python compiler to show how it would understand those programs.

The review should answer: **Can we express the important Spatial ideas clearly in Python, and can we explain exactly what these programs do?** HLS pragmas, vendor scheduling, and resource tuning come afterward.

## A first program to discuss

The original tiled-scale lab reads 32 values in two tiles of 16, uses separate input and output SRAMs, multiplies each value by a scalar, and stores the result. The host compares the output with an elementwise reference. Source: `spatial@e7a8f2f:test/spatial/tests/ee109/Lab1Part2DramSramExample.scala:6-43`.

This sketch adapts the earlier source-capture example in [[D-26-02-student-surface-comparison]]. Names and syntax remain open for discussion. **It is not runnable against an existing Spatial Python package.**

```python
@kernel
def tiled_scale(src: In[Dram[Int, 32]],
                scale: In[Int],
                dst: Out[Dram[Int, 32]]):
    for base in sequential(0, 32, step=16):
        tile_in: Sram[Int, 16]
        tile_out: Sram[Int, 16]

        load(tile_in, src[base:base + 16])
        for i in foreach(0, 16):
            tile_out[i] = tile_in[i] * scale
        store(dst[base:base + 16], tile_out)
```

- The function describes the accelerator. Its arguments describe input and output ports.
- `Dram` means external memory; `Sram` means local storage in the accelerator.
- The outer loop visits the tiles in order. The inner loop describes work within one tile.
- `load` and `store` keep data movement visible.
- `Int` must have a defined Spatial numeric meaning. It cannot silently mean Python's unbounded integer arithmetic.

Under the source-capture option, the compiler reads this function as source text. `@kernel` and the annotations are syntax it recognizes; this sketch does not require importing the file and executing its decorators or body. Ordinary Python can separately prepare input data and check results. How files and notebook cells provide source is part of the design work.

This example deliberately fixes the size and tile width. Runtime dimensions, tail handling, and requests for parallel execution need their own examples; their absence here is not an exclusion from the eventual language.

## Two ways to express the programs

| Approach | What the programmer writes | Main design cost |
|---|---|---|
| Source capture | Python function syntax, ordinary-looking `for` / `if`, annotations, and explicit Spatial operations | Define the supported Python subset and explain where its meaning differs from ordinary Python execution |
| Explicit Python builder | Python calls and control contexts that construct Spatial program objects | More explicit syntax for control, writes, literals, and source locations |

**Initial research preference:** start with source-captured examples because they let us discuss the whole program in familiar statement form. Compare all three programs in both source-capture and builder forms before deciding; [[PY-R001 - Programming Model Study]] maintains that comparison. Both the reader and the semantic checker can be implemented in Python. This is a starting hypothesis, not a final architecture choice.

Plain operator-overloading traces alone are insufficient as the complete design: executing Python control flow can choose one branch or run a loop before the compiler has preserved its hardware meaning. An explicit builder can avoid this with its own control constructs. The existing mappings document these hazards and possible remedies; they do not prove all tracing designs impossible. See [[10 - Python Controller Bodies]], [[20 - Python If Expressions]], and [[90 - Python Naming and Scoping]].

Python's standard `ast` module provides a source tree, including statement structure and positions. It does not provide Spatial's type checker, memory rules, or simulator. Original source and literal spelling may also need to be retained. [Python AST documentation](https://docs.python.org/3/library/ast.html) (checked 30 September 2026).

Python truth testing and `with` statements have their own execution rules. A builder must deliberately define which work constructs a program and which work describes runtime hardware behavior. [Python data model](https://docs.python.org/3/reference/datamodel.html#object.__bool__), [Python compound statements](https://docs.python.org/3/reference/compound_stmts.html#the-with-statement) (checked 30 September 2026).

## Example set for the next review

| Example | What it should make clear |
|---|---|
| Tiled scale | Ports, external/local memory, transfers, sequential traversal, and elementwise work |
| Small scalar reduction | Initial accumulator value, contribution expression, result lifetime, and the difference between an ordered fold and a reduction |
| Runtime branch with state or FIFO effects | Both possible paths, when state changes or FIFO reads happen, and which values are visible afterward |

Concrete starting points are `spatial@e7a8f2f:test/spatial/tests/feature/control/ReduceTiny.scala:7-15`, whose initialized array contributes the values 0 through 15 to a sum, and `spatial@e7a8f2f:test/spatial/tests/feature/control/FIFOBranch.scala:9-31`, whose branch selects a FIFO to consume. Expected small-case results derived from those sources are 120 for the reduction and 378 for FIFO counts 13 and 25. These are reference expectations, not results from a new Python implementation.

Use small invalid variants too: a read before a write, an unsupported construct, and an incompatible numeric type. Show what a useful Python-source error would say. These examples should test a programming model, not grow into a catalog of hardcoded whole-program recognizers.

## What the Python implementation might contain

The initial concept is:

**Python program description → Python checks → structured program objects → Python functional simulation.**

The structured objects would describe loops, conditions, memory operations, expressions, and effects. This would let us inspect a program's meaning and simulate it before introducing code generation. The exact object model and the split between unchecked and checked forms remain design questions.

Simulation should reproduce the chosen numeric and state behavior. It would not establish cycle timing, parallel throughput, or device resource use. Once representative programs have a clear meaning and checked representation, investigate how those same operations map to HLS C++.

## What carries forward

The original Spatial specification, source examples, semantic mapping notes, diagnostic cases, and historical HLS experiments remain useful evidence. The Rust prototype remains a reference and comparison artifact. Reuse its findings and test ideas where applicable; a Rust executable is not a dependency of the new Python compiler.

Do not automatically promote every choice in the Rust rewrite's language contract to a requirement of the Python rewrite. Separate original Spatial behavior, deliberate earlier redesigns, and Python API choices. In particular, [[30 - Python Assignment]], [[B0 - Python Literal Typing]], [[C0 - Python Fifo Deq Timing]], and [[D0 - Python Declaration Order]] identify questions that deserve explicit answers.

The [[D-26-12-simulator-spike|old interpreter measurements]] remain dated evidence about the implementations tested. They neither change the professor's new requirement nor establish the performance of this unbuilt Python compiler. Measure useful example runtimes when there is an implementation to measure.

## Research sequence

1. Write the three representative programs and their intended behavior.
2. Compare source capture and a builder on those same programs; choose the public programming model.
3. Sketch the Python checker, program representation, and reference simulator needed to explain those examples.
4. After reviewing that programming model, investigate HLS lowering from the representation. A complete Python compiler is not a prerequisite for this discussion. Implementation follows design review; later HLS correctness checks should compare with the reference simulation.

No new compiler implementation or HLS validation is claimed by this note. The immediate deliverable is a reviewable Python programming model.
