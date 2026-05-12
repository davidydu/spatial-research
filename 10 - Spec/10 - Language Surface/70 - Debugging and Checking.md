---
type: spec
concept: debugging-and-checking-language-surface
source_files:
  - "src/spatial/lang/api/DebuggingAPI.scala:1-231"
  - "src/spatial/lang/api/StaticAPI.scala:7-36"
  - "src/spatial/dsl.scala:6-46"
  - "src/spatial/SpatialTestbench.scala:1-16"
  - "argon/src/argon/DSLTestbench.scala:1-31"
  - "argon/src/argon/static/Printing.scala:227-232"
  - "utils/src/utils/io/CaptureOutputStream.scala:1-21"
source_notes:
  - "[[language-surface]]"
hls_status: "clean for textual prints; rework for printSRAM/approxEql/checkGold"
depends_on:
  - "[[60 - Host and IO]]"
  - "[[90 - Aliases and Shadowing]]"
status: draft
---

# Debugging and Checking

## Summary

Spatial splits debugging into an internal surface and a shadowing-only user surface. `DebuggingAPI_Internal` simply extends argon's internal debugging API (`src/spatial/lang/api/DebuggingAPI.scala:9`). `DebuggingAPI_Shadowing` extends that internal layer plus argon's shadowing debugging layer, but it has a structural self-type `this: StaticAPI_Shadowing =>`, so the helpers in this file are only mixable into `StaticAPI_Shadowing` (`src/spatial/lang/api/DebuggingAPI.scala:11-13`, `src/spatial/lang/api/StaticAPI.scala:35-36`). Since `spatial.dsl` mixes `StaticAPI_Shadowing` and `spatial.libdsl` does not, app code under `dsl` sees `printArray`, `approxEql`, `checkGold`, `r"..."`, and `sleep`, while library code under `libdsl` must use lower-level argon printing APIs instead (`src/spatial/dsl.scala:6-46`). See [[90 - Aliases and Shadowing]] for the `dsl`/`libdsl` distinction.

## Syntax or API

```scala
sleep(cycles)                                  // DebuggingAPI.scala:15-16
printArray(a, "A"); printMatrix(m, "M")       // DebuggingAPI.scala:18-36
printTensor3(t3); printTensor4(t4); printTensor5(t5)
printSRAM1(s1); printSRAM2(s2); printSRAM3(s3)

r"value = $x"                                  // DebuggingAPI.scala:139-149
approxEql(a, b); approxEql(a, b, margin)       // DebuggingAPI.scala:152-179
checkGold(dram1, gold); checkGold(reg, gold)  // DebuggingAPI.scala:181-213
If(cond){ ... }; IfElse(cond){ a }{ b }        // DebuggingAPI.scala:215-229
```

## Semantics

`sleep(cycles)` is not a host sleep; it emits a `Pipe.NoBind.Foreach(cycles by 1)` whose body prints `i` when `i == 0`, so the staged program consumes cycles through a no-bind controller (`src/spatial/lang/api/DebuggingAPI.scala:15-16`). The host tensor printers use virtualized Scala ranges over host tensors: `printArray` prints a header, then each array element plus a space, then a newline (`src/spatial/lang/api/DebuggingAPI.scala:18-24`). `printMatrix` nests row and column loops over `matrix.rows` and `matrix.cols`, prints elements separated by tabs, and prints a newline at each row boundary (`src/spatial/lang/api/DebuggingAPI.scala:26-36`). `printTensor3`, `printTensor4`, and `printTensor5` extend the same textual format to three, four, and five dimensions and add separator rows made of `"--\t"` at inner dimension boundaries (`src/spatial/lang/api/DebuggingAPI.scala:38-96`).

The SRAM printers use accelerator `Foreach` loops, not host collection loops. `printSRAM1` prints each SRAM element in a single `Foreach(0 until array.length)` (`src/spatial/lang/api/DebuggingAPI.scala:98-104`). `printSRAM2` nests `Foreach` over rows and columns, and `printSRAM3` nests three `Foreach` loops plus separator rows (`src/spatial/lang/api/DebuggingAPI.scala:106-132`). The local `I32Range` implicit class redirects `Series[I32].foreach` to `Foreach(x){i => func(i)}`, which supports the virtualized loop syntax used by the debug printers (`src/spatial/lang/api/DebuggingAPI.scala:134-136`).

The `r"..."` interpolator is implemented by `implicit class Quoting(sc: StringContext)`. It maps `Top[_]` arguments through `toText`, maps other arguments through `Text(t.toString)`, interleaves text parts and quoted args, and stages `TextConcat` (`src/spatial/lang/api/DebuggingAPI.scala:139-149`). This makes `r"..."` a staged text builder rather than a Scala string interpolator in `dsl` scope (`src/spatial/lang/api/DebuggingAPI.scala:139-149`).

`approxEql` has scalar and tensor overloads. For scalar `T: Bits`, it inspects `Type[T]`; if the type is numeric, it casts the evidence to `Num[T]` and checks `abs(a - b) <= margin.to[T] * abs(a)`, otherwise it falls back to `a === b` (`src/spatial/lang/api/DebuggingAPI.scala:152-160`). `Tensor1`, `Tensor2`, and `Tensor3` overloads check length equality and reduce pairwise `approxEql` results with bitwise AND (`src/spatial/lang/api/DebuggingAPI.scala:162-179`). `checkGold` for `DRAM1` calls `getMem`, prints result and gold arrays, and returns `approxEql(result, gold, margin)` (`src/spatial/lang/api/DebuggingAPI.scala:181-192`). `checkGold` for `DRAM2` calls `getMatrix`, prints both matrices, and returns approximate equality (`src/spatial/lang/api/DebuggingAPI.scala:194-205`). `checkGold` for `Reg` calls `getArg`, prints result/gold text, and returns scalar approximate equality (`src/spatial/lang/api/DebuggingAPI.scala:207-213`).

`If` and `IfElse` are explicitly unstaged helpers. `If(cond: scala.Boolean)` pattern matches on a Scala boolean and either executes the block at staging time or does nothing (`src/spatial/lang/api/DebuggingAPI.scala:215-221`). `IfElse[T](cond: scala.Boolean)` similarly selects between two by-name Scala blocks at staging time (`src/spatial/lang/api/DebuggingAPI.scala:223-229`). These are not virtualized Spatial control flow; virtualized `if` lowering belongs to `SpatialVirtualization` (`src/spatial/lang/api/SpatialVirtualization.scala:71-101`).

## Implementation

The visibility boundary is structural. `StaticAPI_Internal` mixes `DebuggingAPI_Internal`, while `StaticAPI_Shadowing` mixes `DebuggingAPI_Shadowing` (`src/spatial/lang/api/StaticAPI.scala:7-22`, `src/spatial/lang/api/StaticAPI.scala:35-36`). `libdsl` extends only `SpatialDSL`, whose base is `StaticAPI_Frontend`, while `dsl` extends `SpatialDSL with StaticAPI_Shadowing` (`src/spatial/dsl.scala:6-46`). Because `DebuggingAPI_Shadowing` declares `this: StaticAPI_Shadowing =>`, code that only imports `libdsl` cannot reach the shadowing-only debug helpers through normal trait composition (`src/spatial/lang/api/DebuggingAPI.scala:11-13`, `src/spatial/dsl.scala:8-29`).

The testbench warning capture path lives in argon and utils, but Spatial opts into it through `SpatialTestbench extends argon.DSLTestbench` (`src/spatial/SpatialTestbench.scala:7-16`). `DSLTestbench.reqWarn` creates a `CaptureStream(state.out)`, runs `calc` inside `withOut(capture)`, splits captured output by newline, and requires a line containing both `"warn"` and the expected substring (`argon/src/argon/DSLTestbench.scala:20-25`). `withOut(stream)` temporarily routes `state.out` through `inStream` and closes the stream afterward (`argon/src/argon/static/Printing.scala:227-232`). `CaptureOutputStream` stores bytes in a `ByteArrayOutputStream`, exposes UTF-8 `dump`, and `CaptureStream` wraps it as a `PrintStream` (`utils/src/utils/io/CaptureOutputStream.scala:5-17`).

## Interactions

The tensor printers depend on host tensor accessors from [[60 - Host and IO]], because `printArray`, `printMatrix`, and `printTensor3-5` use `length`, `rows`, `cols`, `dimN`, and `apply` methods from host collections (`src/spatial/lang/api/DebuggingAPI.scala:18-96`). `checkGold` depends on transfer APIs because it calls `getMem`, `getMatrix`, and `getArg` before comparing values (`src/spatial/lang/api/DebuggingAPI.scala:181-213`). `approxEql` depends on the math helper `abs` and numeric casts through `Num[T]` and `margin.to[T]` (`src/spatial/lang/api/DebuggingAPI.scala:152-160`).

## HLS notes

`hls_status: "clean for textual prints; rework for printSRAM/approxEql/checkGold"`. Textual host prints are straightforward as simulation/debug output because they are already expressed through staged `println`/`print` and host tensor traversal (`src/spatial/lang/api/DebuggingAPI.scala:18-96`). `printSRAM1-3` are accelerator-side loops over SRAM, so an HLS port must decide whether they become simulation-only diagnostics, synthesized debug ports, or are rejected outside software simulation (`src/spatial/lang/api/DebuggingAPI.scala:98-132`). `approxEql` and `checkGold` mix transfer, printing, and staged comparison, so they should be treated as test/debug utilities rather than synthesizable datapath constructs (inferred, unverified; source behavior at `src/spatial/lang/api/DebuggingAPI.scala:152-213`).

## Open questions

- See `[[open-questions-lang-surface]]` Q-lang-13 (`printSRAM` HLS/debug policy) and Q-lang-14 (`approxEql` relative-error behavior near zero).
