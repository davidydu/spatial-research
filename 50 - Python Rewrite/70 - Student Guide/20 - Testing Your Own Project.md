---
title: Testing your own project
type: guide
project: spatial-python
updated: 2026-10-22
status: preview
---

# Testing your own project

Start with [[10 - Testing a Spatial Program]]; return to [[00 - Python Spatial Student Guide]] for the guide index.

For a final project, you should be able to write your own functional tests: choose inputs, run your accelerator as generated C++, and check its answers. The tests are ordinary host Python. They are not part of the Spatial kernel and do not need to compile into hardware.

> [!important] Preview: the student wrapper is not shipped
> The examples below describe the intended workflow. `cpp_kernel` is an illustrative, project-provided pytest fixture whose `.run(...)` method would execute generated C++. Neither this fixture nor its convenient input conversion is available today. Ordinary pytest syntax is real. The compiler already has an internal native runner; its public student interface remains unfinished.

## Write an independent answer first

Keep the kernel and test in separate files. Calculate expected answers with a straightforward algorithm, even when the accelerator uses tiles, local memory, and a different execution order. For matrix multiplication, simple nested loops make a useful golden calculation.

Do not call the compiler's arithmetic helpers or Python reference interpreter to calculate your expected answers. The interpreter helps us verify the compiler internally; it is not an independent statement of what your project should compute.

Python integers have unlimited precision. Spatial `Int` uses signed 32-bit wrapping. This independently written host helper expresses that rule:

```python
def wrap_i32(value):
    return ((value + (1 << 31)) % (1 << 32)) - (1 << 31)

assert wrap_i32(2147483647 * 2) == -2
```

Apply the rule at the operations where the kernel uses `Int`. For algorithms involving division, shifts, comparisons, or conversions, wrapping only the final answer may change the result. Follow [[20 - Python Numeric Contract]] for the intended operation semantics and check the current implementation coverage separately.

## Test several cases with the same check

This preview assumes a kernel with 32-element `Int` input/output buffers and an `Int` scale input. The proposed fixture would validate those types and lengths, allocate output storage, and return the native runner's outcome and output tuples.

```python
import random
import pytest

rng = random.Random(109)
random_inputs = [rng.randint(-100, 100) for _ in range(32)]

@pytest.mark.parametrize("inputs,scale", [
    ([0] * 32, 7),
    (list(range(-16, 16)), -3),
    ([2147483647, -2147483648, -1, 1] * 8, 2),
    (random_inputs, 5),
])
def test_scale(cpp_kernel, inputs, scale):
    expected = tuple(wrap_i32(x * scale) for x in inputs)
    result = cpp_kernel.run(src=inputs, scale=scale)
    assert result.outcome == "Completed"
    assert result.outputs["dst"] == expected
```

Use asymmetric values, negative numbers, zeros, and boundary values. Where your kernel admits different shapes or partial tiles, cover those explicitly; passing a shorter list to a fixed 32-element input is an invalid binding, not a smaller valid test.

A seed makes generated cases repeatable. When a case fails, save the actual input vector, scalar arguments, expected answer, and compiler revision as a regression case. Keeping only the seed makes reproduction depend on the generator and its version.

Pytest is one optional way to organize project tests; its [parametrization guide](https://docs.pytest.org/en/stable/how-to/parametrize.html) explains this syntax. Plain Python assertions or `unittest` can express the same checks. This workflow does not require a new testing language, or pytest or Hypothesis as compiler dependencies.

## Add checks that matter to your algorithm

Custom assertions can check output lengths, unchanged inputs, invariants, or relationships between runs. For scaling, multiplying by one should preserve every input. Such properties supplement independently expected outputs; a weak property alone can accept a consistently wrong algorithm.

To detect a kernel writing to an input, inspect the native runner's returned input snapshot, `result.buffers["src"]`, and its initialization mask when relevant, or check the input inside the exported C++ testbench. The student wrapper should expose that inspection route. Checking only the original Python input object cannot detect such a write: the runner copies host storage before execution.

Using the same planned `cpp_kernel` fixture, a project-specific property test could be:

```python
def test_scaling_by_one(cpp_kernel):
    inputs = tuple(range(-16, 16))
    result = cpp_kernel.run(src=inputs, scale=1)
    assert result.outcome == "Completed"
    assert result.outputs["dst"] == inputs
```

Each current native invocation uses isolated host snapshots. Repeated calls test fresh invocations. They do not create a persistent device session, preserve SRAM between calls, or establish streaming/resumption support. If your algorithm passes state between invocations, supply that state explicitly through supported inputs and outputs.

## Keep failures specific

A successful test must check both completion and values. A zero process exit code alone is insufficient: the internal runner reports a language fault separately from process failure. An expected-fault case should name the particular fault it expects. Unsupported source syntax, an unsupported backend feature, invalid host bindings, compilation errors, crashes, and timeouts must not count as that expected language fault. Never catch every exception and call the test passed. See the [current result handling](https://github.com/davidydu/spatial-py/blob/9be9b9056b1c0b7af021a0e478ae9218dbfb1c7b/src/spatial/backends/cpp_run.py#L126-L178).

The current C++ backend supports a bounded sequential profile with rank-one Int32 memories, fixed external extents, and distinct contiguous external buffers. Local views have broader alias support than external ports. Rank-two target memory, Reg, Reduce/Fold, and other language families remain unfinished. Consult [[80 - Initial Compiler Goal|public implementation progress]] or the [detailed support ledger](https://github.com/davidydu/spatial-py/blob/work/initial-reference/docs/support-ledger.md). Compiler source links on this page require collaborator access to the private repository. Requesting C++ execution must never silently fall back to the Python interpreter.

## Carry concrete cases into hardware verification

The planned student workflow should export concrete inputs and independently expected outputs into a generated C++ testbench. Arbitrary Python callbacks and pytest assertions are not translated into hardware tests. Materialize their expected values first. The existing [vendor case representation](https://github.com/davidydu/spatial-py/blob/9be9b9056b1c0b7af021a0e478ae9218dbfb1c7b/src/spatial/backends/vitis.py#L24-L30) already carries bindings, expectations, and optional expected faults; the student export interface is still to be built.

Advanced projects should also be able to supply handwritten C++ checks through a documented generated interface. Today that interface is experimental, not a stable public ABI. Follow the generated argument layout, initialization masks, and status representation for the pinned compiler revision; a testbench must return failure on a mismatch even when C++ assertions are disabled.

Native C++ success establishes functional agreement for the tested cases. Vitis C simulation and RTL co-simulation require their own runs. None of these checks alone establishes board execution, achieved parallelism, or throughput.
