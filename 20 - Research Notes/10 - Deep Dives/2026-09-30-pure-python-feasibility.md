---
type: deep-dive
topic: pure-python-feasibility
title: "Can Spatial be implemented entirely in Python?"
date: 2026-09-30
session: 2026-09-30
status: research-conclusion
feeds_spec: []
source_files:
  - "exo@defe172:src/exo/API.py:168-173"
  - "exo@defe172:src/exo/frontend/typecheck.py:144-168"
  - "exo@defe172:src/exo/backend/LoopIR_compiler.py:323-348"
related:
  - "[[2026-09-30-pure-python-programming-model]]"
  - "[[D-26-13-case-for-p-e]]"
  - "[[D-26-12-simulator-spike]]"
---

## Conclusion

**Yes. A Spatial compiler implemented in Python is theoretically feasible.** Parsing, type checking, hardware-legality checks, program representations, transformations, reference simulation, and HLS code generation can all be Python code. No essential compiler capability identified in this research requires Rust.

On 30 September 2026, David clarified the professor's reasoning: assume coding agents provide abundant implementation capability, so the earlier arguments about Rust's type safety and implementation discipline should no longer determine the choice. We adopt that as a planning assumption, not a measured claim that agents produce error-free compilers.

Under this assumption, proceed with pure Python. Evaluate the design by whether it expresses Spatial clearly and preserves its meaning. Compiler and simulator performance remain questions to measure on representative workloads; they are not theoretical objections to Python.

## Compiler implementation types and Spatial types are different

Rust's type system can prevent classes of mistakes in the compiler implementation. It does not automatically establish that a Spatial type rule is correct or that an optimization preserves behavior.

A compiler written in Python can explicitly represent Spatial types and reject invalid programs before simulation or hardware generation. For example, it can check numeric widths, memory element types, initialization, and supported effects. The implementation language's own dynamic typing does not make the language being compiled dynamically typed.

Python annotations alone are not these checks: Python's runtime does not enforce them. The compiler must implement the Spatial checker, just as a Rust implementation must. Python static-analysis tools, checked program objects, invariant validation, and conformance tests can support that work; they do not become identical to Rust's static guarantees. [Python typing documentation](https://docs.python.org/3/library/typing.html) (checked 30 September 2026).

## Why feasibility is a firm conclusion

This is a constructive argument, not only an appeal to language generality. Python can store nodes describing operations, walk them, calculate types and effects, reject unsupported cases, transform the nodes, and emit source text. Any particular effective compiler algorithm used for these tasks can also be implemented in Python, given sufficient time and memory.

Exact hardware arithmetic is implementable too. Python integers have unlimited precision subject to available memory; the compiler or simulator can explicitly apply the chosen bit widths, signed interpretation, overflow rules, and fixed-point scaling. Native Python float arithmetic need not define Spatial arithmetic. This is an implementation obligation, not a missing language capability. [Python numeric types](https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex) (checked 30 September 2026). The earlier [[D-26-12-simulator-spike]] already records matched exact-output cases for a bounded Python interpreter, without establishing complete language coverage.

There are concrete precedents:

- Exo's Python API calls its type checker, bounds checker, and alias checks before accepting typed LoopIR: `exo@defe172:src/exo/API.py:168-173`.
- Its Python type checker collects source-labelled errors and checks index-expression types: `exo@defe172:src/exo/frontend/typecheck.py:144-168`.
- Its Python backend constructs C source and header strings: `exo@defe172:src/exo/backend/LoopIR_compiler.py:323-348`.
- xDSL describes itself as a Python-native compiler toolkit with pure Python development, custom intermediate representations, and lowering through multiple representation levels. [Official xDSL site](https://xdsl.dev/) (checked 30 September 2026).

These establish relevant implementation patterns, not ready-made Spatial support. Exo uses solver dependencies including Z3; it is evidence of Python-owned compiler semantics, not a claim that every dependency is Python. [Exo repository and dependency documentation](https://github.com/exo-lang/exo) (checked 30 September 2026). We have not selected Exo, xDSL, a native solver, or an MLIR backend for this rewrite.

## Compiler speed is separate from hardware speed

A Python compiler can emit the same HLS C++ as a Rust compiler. With identical emitted inputs, downstream tool versions, settings, and seeds where relevant, the HLS tool has no additional information about which implementation language produced them. Python therefore imposes no inherent performance penalty on the generated hardware. This is an inference from the compiler/output boundary, not a new synthesis measurement.

Practical limits can still matter. Python may take longer or use more memory to analyze a large program or explore optimization choices. A scalar Python simulator may be much slower than a native interpreter. More coding agents do not automatically remove those costs, although implementation and algorithm choices can change them.

The earlier interpreter study measured approximately 67 ms for one Python GEMM32 simulation and 1.3 ms for its Rust counterpart. Those are dated results for two specific node interpreters, not compilation times or hardware throughput. The original study's ratio gate and measurements remain unchanged. Under the professor's new direction, define useful absolute feedback-time targets and measure the new design against them. See [[D-26-12-simulator-spike]].

## What this conclusion does not promise

**A compiler written in Python does not require accepting every ordinary Python program as hardware.** The Spatial programming model can retain explicit memories, bounded numeric types, controllers, and a supported set of operations. Source capture and explicit builders remain alternative ways to express that model.

General termination, arbitrary semantic equivalence, and perfect optimization cannot be decided automatically for all unrestricted programs. A practical compiler defines its supported language and analyses, and rejects cases it cannot establish as legal. These limits apply regardless of whether the compiler is written in Python or Rust; additional coding capability does not remove them.

Likewise, implementing the compiler in Python does not resolve every original Spatial-to-HLS mapping. The meaning and representability of controllers, memory behavior, streams, and schedules still need research. Those are backend and language-design questions, to examine after the Python programming model is clear.

Here, pure Python means the Spatial compiler's own semantic implementation is Python. It does not require rewriting the Python runtime or a future vendor HLS tool. A native semantic core or native simulation engine is not assumed as a workaround.

## Research consequence

The implementation language is settled for this direction; [[D-27]] records that decision. Continue from [[00 - Python Rewrite Index]] and [[PY-R001 - Programming Model Study|the paired programming-model study]], then establish the exact semantics and Python representation/checking design. Investigate HLS lowering afterward. Retain correctness tests and measurements, but do not reopen Rust solely because Python lacks the same implementation-language type system.
