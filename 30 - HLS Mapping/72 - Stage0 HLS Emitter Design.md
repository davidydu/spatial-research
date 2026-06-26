---
type: hls-mapping
construct: stage0-hls-emitter-design
category: rework
status: draft
date: 2026-06-25
---

# Stage 0 HLS Emitter Design

Stage 0 is a deliberately small HLS emitter for the Lab1Part1 scalar add tracer bullet. It should consume the existing staged IR, recognize one scalar ABI shape, emit a standalone HLS kernel plus a plain C++ harness, and fail loudly for every construct outside that shape.

The design follows the existing codegen style: a case-class generator composed from small traits, each trait pattern-matching `Op` nodes in `gen(lhs, rhs)`. Current `CppGen` is assembled this way in `/Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGen.scala:5-13`; `CppGenInterface`, `CppGenAccel`, and `CppGenMath` provide the closest conventions for ABI collection, accelerator traversal, and scalar math emission.

## Stage 0 supported nodes and generated C++

Stage 0 supports only the Lab1Part1 surface recorded in [[60 - EE109 HLS Lowering Map]] and [[70 - Lab1Part1 Tracer Bullet]]: two `ArgIn[Int]` values, one `ArgOut[Int]`, host `setArg` and `getArg`, one `AccelScope`, two `RegRead` nodes, one integer `FixAdd`, and one `RegWrite`.

| Surface | Accepted IR shape | Generated C++ policy |
|---|---|---|
| Test envelope | `@spatial`, `SpatialTest`, and `runtimeArgs` around the example | Do not lower into the kernel. Preserve `runtimeArgs = "3 5"` in the harness oracle. |
| Host print/assert | `println`, equality check, and `assert` after `getArg` | Keep out of the HLS kernel. Harness returns `0` on exact scalar match and `1` otherwise. |
| Scalar inputs | Exactly two `ArgInNew[Int]` symbols before the `AccelScope`; Lab1 names are `argRegIn0` and `argRegIn1` | Kernel value parameters `int argRegIn0` and `int argRegIn1`; each gets `#pragma HLS INTERFACE s_axilite port=<name> bundle=control`. |
| Scalar output | Exactly one `ArgOutNew[Int]` before the `AccelScope`; Lab1 name is `argRegOut` | Kernel output endpoint `int *argRegOut`; it gets `#pragma HLS INTERFACE s_axilite port=argRegOut bundle=control`. |
| Host writes | Exactly two `SetReg` calls before the `AccelScope`, each targeting one collected `ArgIn` | No kernel code. Harness supplies `3` and `5` in the collected input order. |
| Host read | Exactly one `GetReg` after the `AccelScope`, targeting the collected `ArgOut` | No kernel code. Harness compares the output to `8`. |
| Kernel boundary | Exactly one outer `AccelScope` | Emit one `extern "C"` top function named `Lab1Part1RegExample_kernel`. |
| Kernel reads | `RegRead` from each collected `ArgIn` inside the `AccelScope` | Map directly to the corresponding scalar parameter expression. |
| Integer add | One `FixAdd` whose operands are the two scalar read expressions and whose type is integer `Int` | Emit `argRegIn0 + argRegIn1`. Existing Cppgen emits `FixAdd` as `x + y` in `/Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenMath.scala:26`; `FixAdd` is defined in `/Users/david/Documents/David_code/spatial/argon/src/argon/node/Fix.scala:65-83`. |
| Kernel write | One unconditional `RegWrite` to the collected `ArgOut` | Emit `*argRegOut = argRegIn0 + argRegIn1;`. |

Generated kernel target:

```cpp
extern "C" void Lab1Part1RegExample_kernel(
    int argRegIn0,
    int argRegIn1,
    int *argRegOut) {
#pragma HLS INTERFACE s_axilite port=argRegIn0 bundle=control
#pragma HLS INTERFACE s_axilite port=argRegIn1 bundle=control
#pragma HLS INTERFACE s_axilite port=argRegOut bundle=control
#pragma HLS INTERFACE s_axilite port=return bundle=control

  *argRegOut = argRegIn0 + argRegIn1;
}
```

Generated harness target:

```cpp
#include <iostream>

extern "C" void Lab1Part1RegExample_kernel(
    int argRegIn0,
    int argRegIn1,
    int *argRegOut);

int main() {
  int argRegOut = 0;
  Lab1Part1RegExample_kernel(3, 5, &argRegOut);

  if (argRegOut != 8) {
    std::cerr << "FAIL Lab1Part1RegExample: expected 8, got "
              << argRegOut << std::endl;
    return 1;
  }
  return 0;
}
```

## Suggested Scala implementation shape, including package/classes/traits and matching cases

Add a new isolated package instead of extending legacy `cppgen`, because Stage 0 should not emit `FringeContext`, `TopHost.cpp`, `ArgAPI.hpp`, instrumentation counters, early exits, or platform dependency copies. The new package can still reuse the same Argon `Codegen` and `AccelTraversal` conventions.

Suggested package and trait layout:

```scala
package spatial.codegen.hlsgen

import argon._
import argon.node._
import argon.codegen.FileDependencies
import spatial.lang._
import spatial.node._
import spatial.traversal.AccelTraversal

case class HlsGen(IR: State) extends HlsCodegen
  with HlsFileGen
  with HlsGenCommon
  with HlsGenInterface
  with HlsGenAccel
  with HlsGenMath

trait HlsCodegen extends FileDependencies with AccelTraversal {
  override val lang: String = "hls"
  override val ext: String = "cpp"
  override def entryFile: String = "Lab1Part1RegExample_kernel.cpp"
}
```

`HlsGenCommon` owns the Stage 0 model and diagnostics:

- `scalarInputs: ArrayBuffer[Sym[_]]`, matching `CppGenCommon.argIns`.
- `scalarOutputs: ArrayBuffer[Sym[_]]`, matching `CppGenCommon.argOuts`.
- `hostSetArgs: LinkedHashMap[Sym[_], Sym[_]]` for `SetReg` values.
- `hostGetArgs: ArrayBuffer[Sym[_]]` for `GetReg` reads.
- `exprs: HashMap[Sym[_], String]` for kernel scalar expressions.
- `outputAssignment: Option[(Sym[_], String)]` for the single `RegWrite`.
- `seenAccel: Int` and `inKernel: Boolean` to enforce the one-accelerator shape.
- `hlsName(sym)` using `sym.name.getOrElse(quote(sym))`, sanitized as a C++ identifier, with collision checks. This mirrors the need served by `CppGenCommon.argHandle` in `/Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenCommon.scala:133-147`.
- `hlsScalarType(tp)` accepting only Spatial `Int`, projected as C++ `int`. Current `CppGenCommon.remap` maps `Reg[T]` through to `T` in `/Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenCommon.scala:75-99`; Stage 0 should use that idea but keep the accepted type set smaller.

`HlsGenInterface` handles host ABI collection:

```scala
override protected def gen(lhs: Sym[_], rhs: Op[_]): Unit = rhs match {
  case ArgInNew(init) if !inKernel =>
    recordArgIn(lhs, init)

  case ArgOutNew(init) if !inKernel =>
    recordArgOut(lhs, init)

  case SetReg(reg, value) if !inKernel =>
    recordSetArg(lhs, reg, value)

  case GetReg(reg) if !inKernel =>
    recordGetArg(lhs, reg)

  case other =>
    super.gen(lhs, other)
}
```

`HlsGenAccel` handles the kernel body and validates that `Reg` nodes are used only as the scalar ABI:

```scala
override protected def gen(lhs: Sym[_], rhs: Op[_]): Unit = rhs match {
  case AccelScope(func) =>
    seenAccel += 1
    enterKernel(lhs)
    visitBlock(func)
    leaveKernel(lhs)

  case RegRead(reg) if inKernel =>
    exprs(lhs) = scalarReadExpr(reg)

  case RegWrite(reg, value, ens) if inKernel =>
    recordOutputWrite(reg, value, ens)

  case other =>
    super.gen(lhs, other)
}
```

`HlsGenMath` handles exactly one arithmetic node family in Stage 0:

```scala
override protected def gen(lhs: Sym[_], rhs: Op[_]): Unit = rhs match {
  case FixAdd(x, y) if inKernel =>
    requireIntExpr(lhs, x)
    requireIntExpr(lhs, y)
    exprs(lhs) = s"${exprOf(x)} + ${exprOf(y)}"

  case other =>
    super.gen(lhs, other)
}
```

`HlsFileGen` performs a two-step `emitEntry`:

1. Traverse the staged block once to collect the Stage 0 model through the matching cases above.
2. Validate the full model, then write `Lab1Part1RegExample_kernel.cpp` and `Lab1Part1RegExample_harness.cpp` with `inGen(out, filename)`, following the multi-file emission convention used by `CppFileGen` in `/Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppFileGen.scala:11-120`.

This collector-first shape is safer than streaming C++ while visiting nodes, because the HLS top signature depends on ABI nodes seen before the `AccelScope`, and the harness depends on host nodes seen after it.

## Unsupported diagnostics and exact failure messages

All Stage 0 failures should throw `UnsupportedOperationException` with the prefix `Stage0HLS:`. The templates below are exact; braces indicate runtime substitutions.

| Condition | Failure message |
|---|---|
| Unsupported node in traversal | `Stage0HLS: unsupported node {op} at {ctx}; Stage 0 supports only ArgInNew, ArgOutNew, SetReg, GetReg, AccelScope, RegRead, FixAdd, and RegWrite.` |
| Wrong accelerator count | `Stage0HLS: expected exactly one AccelScope; found {count}.` |
| Wrong input count | `Stage0HLS: expected exactly 2 ArgIn[Int] nodes before the AccelScope; found {count}.` |
| Wrong output count | `Stage0HLS: expected exactly 1 ArgOut[Int] node before the AccelScope; found {count}.` |
| Wrong input transfer count | `Stage0HLS: expected exactly 2 SetReg calls feeding ArgIn inputs before the AccelScope; found {count}.` |
| Wrong output transfer count | `Stage0HLS: expected exactly 1 GetReg call reading the ArgOut after the AccelScope; found {count}.` |
| Unsupported scalar type | `Stage0HLS: unsupported scalar type {tp} for {name}; Stage 0 supports Int only.` |
| Unsupported initializer | `Stage0HLS: unsupported initializer for {name}; Stage 0 expects Const(0).` |
| Host transfer targets wrong role | `Stage0HLS: unsupported host transfer {op} for {name}; Stage 0 supports setArg on ArgIn and getArg on ArgOut only.` |
| Host transfer inside kernel | `Stage0HLS: unsupported host transfer {op} inside AccelScope.` |
| Read from unsupported register | `Stage0HLS: unsupported RegRead from {name}; Stage 0 reads only scalar ArgIn[Int] values inside AccelScope.` |
| Write to unsupported register | `Stage0HLS: unsupported RegWrite target {name}; Stage 0 writes only the single scalar ArgOut[Int].` |
| Conditional write | `Stage0HLS: unsupported RegWrite enable on {name}; Stage 0 requires an unconditional write.` |
| Missing or repeated output write | `Stage0HLS: expected one unconditional RegWrite to the ArgOut inside the AccelScope; found {count}.` |
| Unsupported add operand | `Stage0HLS: unsupported FixAdd operand {name}; Stage 0 operands must be scalar Int expressions from RegRead or FixAdd.` |
| Unsupported arithmetic | `Stage0HLS: unsupported arithmetic {op}; Stage 0 supports integer FixAdd only.` |
| Memory, stream, bus, FIFO, or LIFO node | `Stage0HLS: unsupported memory or stream node {op}; DRAM, SRAM, FIFO/LIFO, streams, and external buses start after Stage 0.` |
| Identifier collision | `Stage0HLS: C++ identifier collision after sanitizing {first} and {second}.` |
| Final shape mismatch | `Stage0HLS: expected Lab1Part1 scalar add shape; found {observed}.` |

Use `{op} = rhs.productPrefix`, `{ctx} = lhs.ctx.toString`, `{tp} = sym.tp.toString`, and `{name} = hlsName(sym)`. The `{observed}` value should be a compact structural summary, for example `2 inputs, 1 output, 1 AccelScope, writes argRegOut from FixAdd(RegRead(argRegIn0), RegRead(argRegIn1))`.

The default `Codegen` fallback currently throws a generic no-rule exception in `/Users/david/Documents/David_code/spatial/argon/src/argon/codegen/Codegen.scala:84-92`. Stage 0 should intercept unsupported cases before that fallback so every rejection explains the selected EE109 subset.

## Generated file layout for kernel and harness

Use the normal Argon generator output root with a new `hls` language directory:

```text
<config.genDir>/hls/
  Lab1Part1RegExample_kernel.cpp
  Lab1Part1RegExample_harness.cpp
```

`Lab1Part1RegExample_kernel.cpp` contains only the `extern "C"` HLS top function and Vitis-compatible AXI-Lite pragmas. It does not include `FringeContext.h`, `ArgAPI.hpp`, generated `functions.hpp`, platform makefiles, instrumentation code, or early-exit plumbing. The ABI manifest already identifies the kernel signature as the portable boundary, while current Cppgen's `ArgAPI.hpp` and `FringeContext` host flow are legacy projections rather than the HLS contract.

`Lab1Part1RegExample_harness.cpp` is a normal C++ executable harness. It declares the kernel prototype, calls `Lab1Part1RegExample_kernel(3, 5, &argRegOut)`, checks `argRegOut == 8`, prints a failure line only on mismatch, and returns process status for automation.

Recommended local compile check:

```bash
c++ -std=c++17 Lab1Part1RegExample_kernel.cpp Lab1Part1RegExample_harness.cpp -o Lab1Part1RegExample_harness
./Lab1Part1RegExample_harness
```

Vitis/Vivado HLS project generation should be layered after this C++ path is stable. Stage 0's first success condition is generated C++ that compiles with a normal host compiler and returns success for the Lab1Part1 oracle.
