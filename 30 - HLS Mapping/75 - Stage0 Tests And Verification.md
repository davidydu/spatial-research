---
type: hls-mapping
construct: stage0-tests-verification
category: rework
status: draft
date: 2026-06-25
depends_on:
  - "[[55 - EE109 ABI Manifest v0]]"
  - "[[60 - EE109 HLS Lowering Map]]"
  - "[[70 - Lab1Part1 Tracer Bullet]]"
---

# Stage0 Tests And Verification

Stage 0 should verify one thing with very little machinery: the compiler has emitted the Lab1Part1 scalar HLS kernel from the staged IR, and that emitted C++ behaves like the existing Spatial oracle for inputs `3` and `5`.

## Existing test harness patterns

The Spatial repo uses ScalaTest 3.0.5 through `build.sbt`, with tests collected by the `test` subproject from `/Users/david/Documents/David_code/spatial/test`. The main executable examples are `@spatial class ... extends SpatialTest`, not plain unit tests. They compile the DSL program through a selected backend and use staged `assert` nodes plus printed `PASS` lines as the runtime signal.

`SpatialTest` defines backend selection by JVM system property: `test.Scala`, `test.VCS`, `test.Zynq`, `test.ZCU`, `test.AWS`, `test.CXP`, `test.ZCUS`, `test.VCSTest`, and `test.CS217`. The `Scala` backend runs generated scalasim code and parses `PASS: true` or assertion failures. The `CS217` backend is useful for generation because it compiles with `--synth --instrument --runtime --scalaExec --scalaSimAccess=2 --countResources --fpga VCS`, but its current make and run commands are `echo "Skipping Make"` and `echo "Skipping Run"`, so it does not prove generated kernel behavior.

The EE109 examples follow the normal `SpatialTest` pattern:

| File | Harness pattern | Verification signal |
|---|---|---|
| `/Users/david/Documents/David_code/spatial/test/spatial/tests/ee109/Lab2Part4LUT.scala` | `runtimeArgs = "0 0 0"`, scalar `ArgIn` and `ArgOut`, `Accel`, host `gold` calculation | Prints `PASS: true(Lab2Part4LUT)` and asserts `gold == result`. |
| `/Users/david/Documents/David_code/spatial/test/spatial/tests/ee109/Lab2Part3BasicCondFSM.scala` | `DRAM`, local `SRAM`, `Reg`, `FSM`, `getMem`, array oracle | Prints `PASS: true (Lab2Part3BasicCondFSM)` and asserts the full array checksum. |
| `/Users/david/Documents/David_code/spatial/test/spatial/tests/compiler/FriendlyTest.scala` | Small scalar `ArgIn` to `ArgOut` example | Asserts `getArg(z) == 5`, close in shape to Lab1Part1. |

There is also a lighter ScalaTest/spec lane through `SpatialTestbench`. It is used for direct compiler/data-structure checks that do not need backend make/run. Examples include `/Users/david/Documents/David_code/spatial/test/spatial/tests/compiler/ConstantMatching.scala`, which uses `"MatchI32" should "match constants with Literal" in { ... }`, and `/Users/david/Documents/David_code/spatial/test/spatial/tests/compiler/AccessPatterns.scala`, which stages a block, runs analysis passes, and checks metadata with `shouldBe`. This is the right lane for generator contract tests when no generated application needs to run.

`SpatialTest` also exposes `checkIR(block: Block[_])`, as shown by `/Users/david/Documents/David_code/spatial/test/spatial/tests/compiler/CLITest.scala`. That seam can fail a normal Spatial test after compile if the staged IR shape is wrong. For Stage 0 it is a good guard for the extractor contract: exactly two `ArgInNew`s, one `ArgOutNew`, one `AccelScope`, two kernel `RegRead`s, one `FixAdd`, one `RegWrite`, and one host `GetReg`.

## Minimal automated verification for generated HLS C++

The smallest useful automated check is a two-layer seam:

1. A generator contract check in the ScalaTest lane.
2. A normal C++ compile-and-run smoke test for the emitted kernel.

The contract check should run after Lab1Part1 staging and before any HLS tool invocation. It should assert the generated Stage 0 artifact contains:

- `extern "C" void Lab1Part1RegExample_kernel(int argRegIn0, int argRegIn1, int *argRegOut)`.
- AXI-Lite interface pragmas for `argRegIn0`, `argRegIn1`, `argRegOut`, and `return`.
- The scalar assignment `*argRegOut = argRegIn0 + argRegIn1;`, after whitespace normalization.
- No `FringeContext`, `ArgAPI`, Chisel, Verilog, instrumentation counter, or generated host-runtime dependency in the HLS kernel file.
- A manifest or in-memory ABI record with two scalar inputs, one scalar output, test values `3` and `5`, and expected value `8`.

The smoke test should build the generated kernel as ordinary C++ with a tiny wrapper:

```cpp
extern "C" void Lab1Part1RegExample_kernel(int argRegIn0, int argRegIn1, int *argRegOut);

int main() {
  int out = 0;
  Lab1Part1RegExample_kernel(3, 5, &out);
  return out == 8 ? 0 : 1;
}
```

This check deliberately validates semantics without Vitis. The generated HLS pragmas are accepted by Vitis and ignored by common host compilers when treated as unknown pragmas, so `clang++` or `g++` is enough for the Stage 0 red/green loop. If the local compiler is configured to warn on unknown pragmas, compile with warning output allowed or add `-Wno-unknown-pragmas`.

The recommended implementation shape, once code edits are allowed, is a new ScalaTest file under `test/spatial/tests/hls/` that uses `SpatialTestbench` or a focused `SpatialTest` with `checkIR`. It should write generated C++ and the wrapper to a temporary directory created by the test process, run the host compiler, and assert exit code `0`. The generated file location in `gen/HLS/Lab1Part1RegExample/` can be checked separately when the backend integration exists.

## Commands likely to run locally, with expected outputs/limitations

Existing Spatial regression pattern:

```bash
cd /Users/david/Documents/David_code/spatial
sbt -Dtest.Scala=true "test/testOnly spatial.tests.ee109.Lab2Part4LUT"
```

Expected output includes a ScalaTest pass and the app-level line `PASS: true(Lab2Part4LUT)`. This proves the existing `SpatialTest` harness and scalar/LUT oracle pattern, not HLS generation.

Existing CS217-style generation pattern for the local Lab1 checkout:

```bash
cd /Users/david/Documents/David_code/lab-1-accelerator-bandits-1
sbt -Dtest.CS217=true "testOnly Lab1Part1RegExample"
```

The existing report at `/Users/david/Documents/David_code/lab-1-accelerator-bandits-1/target/test-reports/TEST-Lab1Part1RegExample.xml` records `test.CS217=true` and a passing test case. The current generated command logs say `Skipping Make` and `Skipping Run 3 5`, so this command confirms compilation and artifact generation, not behavioral execution.

Proposed Stage 0 HLS backend command after a backend flag or test class exists:

```bash
cd /Users/david/Documents/David_code/spatial
sbt -Dtest.HLS=true "test/testOnly spatial.tests.hls.Lab1Part1HLSGenSpec"
```

Expected output should include a ScalaTest pass, a message naming the generated kernel file, and a host compiler smoke-test pass. Until a concrete `HLS` backend or `Lab1Part1HLSGenSpec` exists, this is the command shape rather than a runnable command.

Standalone smoke check shape for a generated kernel:

```bash
clang++ -std=c++11 -Wno-unknown-pragmas Lab1Part1RegExample_kernel.cpp lab1part1_smoke.cpp -o lab1part1_smoke
./lab1part1_smoke
```

Expected output is no output and exit code `0`. A nonzero exit code means the emitted function did not produce `8` for `3 + 5`; a compile error means the Stage 0 C++ is not valid host C++.

## Red/green strategy that does not require installing Vitis

Start red with a focused generator test that asks for Lab1Part1 HLS output and fails on the first missing contract item: no `Lab1Part1RegExample_kernel`, wrong scalar ABI, missing output pointer, missing pragmas, missing scalar add, or a host smoke-test exit code other than `0`.

Turn green by implementing only the Stage 0 path described in [[70 - Lab1Part1 Tracer Bullet]]: identify the Lab1Part1 scalar IR shape, emit the kernel C++ body, and run the ordinary C++ smoke harness. Do not require `vitis_hls`, project Tcl, synthesis reports, RTL simulation, or timing estimates for this stage.

Keep the first negative check equally small: feed a non-Stage-0 pattern such as `Lab2Part4LUT` or `Lab2Part3BasicCondFSM` into the Stage 0 generator and assert that it fails with an explicit unsupported-construct diagnostic instead of writing partial C++. This prevents accidental expansion while the scalar path is still being stabilized.

The first durable pass condition is therefore:

```text
IR shape accepted -> HLS C++ emitted -> clang++ smoke harness exits 0
```

Vitis can be added later as a separate compatibility lane once the ordinary C++ behavior is stable.
