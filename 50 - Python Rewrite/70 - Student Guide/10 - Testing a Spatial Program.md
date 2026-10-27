---
type: guide
title: "Testing a Spatial program"
project: spatial-python
updated: 2026-10-27
status: preview
---

# Testing a Spatial program

A functional test supplies inputs, runs the accelerator, and checks its outputs against an independently specified answer. The accelerator runs as generated C++; the surrounding test can be ordinary Python.

> [!important] Planned student interface
> The `cpp_kernel` fixture below represents a project or course helper that compiles a chosen kernel and runs its generated C++. It is not shipped as a test fixture. A developer example now provides the same `.run(...)` call over an experimental public native handle; see [[#What exists today]].

## Write a test with a known answer

Consider the Lab 1 tiled-scale kernel: it reads 32 integers in tiles of 16, multiplies each element by an input factor, and writes 32 outputs. An illustrative test in `test_scale.py` is:

```python
def test_scale(cpp_kernel):
    inputs = (-3, 0, 2, 7) * 8
    expected = (-9, 0, 6, 21) * 8

    result = cpp_kernel.run(src=inputs, scale=3)

    assert result.outcome == "Completed"
    assert result.outputs["dst"] == expected
```

The helper would prepare typed input storage and fresh output storage, execute the compiled kernel, and return a result. The first assertion requires successful completion. The second checks every output, including its length. A correct prefix or a partial result is not a completed test.

These are ordinary Python assertions. A test runner such as [pytest](https://docs.pytest.org/en/stable/how-to/assert.html) reports a failed assertion with the relevant values. The test does not go through the Spatial compiler. A standard-library `unittest` test or another runner can use the same execution interface.

## Keep the expected answer independent

For a simple case, write the expected values directly. For a larger case, write a small reference calculation from the algorithm's specification. For matrix multiplication, that could be straightforward nested loops even when the accelerator uses tiled memories.

Do not generate expected answers by running the accelerator and saving whatever it returned. Do not use the compiler's Python reference interpreter as the student's only definition of a correct algorithm. That interpreter checks another execution of the same Spatial program; it cannot determine whether the student wrote the intended algorithm.

Use exact comparisons for the current Int32 profile. Python integers have no fixed width, while Spatial `Int` wraps at 32 bits. [[20 - Testing Your Own Project|The project testing guide]] shows how to handle overflow in an independent golden calculation.

## Reuse cases when checking hardware

Save concrete inputs and expected outputs for cases you want to repeat. The intended tooling will turn those cases into a self-checking C++ testbench for Vitis C simulation and RTL co-simulation. Ordinary Python input generators and assertions remain host code; exporting a case does not compile arbitrary Python test logic into C++.

Run checks against the generated kernel actually selected for HLS. When a source, specialization or lowering change produces a different artifact, rerun the relevant tests. Record which stage ran; a native C++ pass is not an RTL pass.

## What exists today

The compiler repository currently requires collaborator access. The pinned source links below are developer evidence; GitHub may show a 404 when you are not signed in with access. Public readers can use [[80 - Initial Compiler Goal|implementation progress]] and [[2026-10-21-generated-cpp-checkpoint|the native C++ checkpoint]]. This preview is not a public installation guide.

A public workflow exists as a developer preview. `spatial.check` and `spatial.prepare` return `Ok` or `Error`, and the experimental `spatial.compile_native` compiles a checked kernel once into a native handle that runs many times with different inputs. A run reports the outcome, the outputs only on completion, and every memory's contents and initialization. It never falls back to the compiler's Python reference interpreter.

The [public native example](https://github.com/davidydu/spatial-py/blob/a46f8068788bc7a39f4ed7f1877ce7009a28cecc/examples/run_public_native.py) checks Lab 1, compiles it once and runs every case against independent expected values. Its [`plain_bindings` adapter](https://github.com/davidydu/spatial-py/blob/a46f8068788bc7a39f4ed7f1877ce7009a28cecc/examples/run_public_native.py#L25-L59) provides the `cpp_kernel.run(src=..., scale=...)` call shown above from the handle's port list; the compiler's own interface takes typed input records. The [E1 evidence](https://github.com/davidydu/spatial-py/blob/a46f8068788bc7a39f4ed7f1877ce7009a28cecc/docs/evidence/e1-public-workflow.md) lists its checks and limits.

The [HLS bundle generator](https://github.com/davidydu/spatial-py/blob/9be9b9056b1c0b7af021a0e478ae9218dbfb1c7b/src/spatial/backends/vitis.py#L179-L215) already accepts explicit expectations and generates a C++ testbench that returns failure on a mismatch. Public case export and a convenient student test launcher remain to be implemented. These pages add no new compiler or hardware capability.

## Connection to the original labs

[Lab 1 Spatial](https://github.com/kelayamatoz/Digital-Systems-Design-Lab/blob/b4896abffd19bcc3f319a49d7a919e1cf70d5221/lab1_part1_spatial.md#L370-L393) calculates a separate gold result and asserts equality. [Lab 3 HLS](https://github.com/kelayamatoz/Digital-Systems-Design-Lab/blob/b4896abffd19bcc3f319a49d7a919e1cf70d5221/lab3_part2_f2_fpga.md#L38-L48) runs a native C++ testbench before synthesis; its [vector example](https://github.com/kelayamatoz/Digital-Systems-Design-Lab/blob/b4896abffd19bcc3f319a49d7a919e1cf70d5221/lab3_part2_f2_fpga.md#L95-L100) reuses inputs across software and hardware checks. Python Spatial keeps that testbench model while moving student host code to Python.

Next: [[20 - Testing Your Own Project]] · [[00 - Python Spatial Student Guide]]
