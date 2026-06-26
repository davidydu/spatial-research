---
type: hls-mapping
construct: stage0-harness-build-flow
category: rework
status: draft
date: 2026-06-25
---

# Stage0 Harness And Build Flow

Stage 0 validates only the `Lab1Part1RegExample` scalar-add path. The check should use standalone generated C++ plus a tiny host harness, not the current `TopHost.cpp` path that depends on `FringeContext`, `ArgAPI.hpp`, VCS resources, or an accelerator bitstream.

The acceptance target is the Lab1Part1 manifest slice: `argRegIn0 = 3`, `argRegIn1 = 5`, one writable `argRegOut`, and exact result `8`.

## Generated files for Stage 0

Generate two C++ source files for the first target:

| File | Role | Required contents |
|---|---|---|
| `Lab1Part1RegExample_kernel.cpp` | HLS-facing kernel file | One `extern "C"` top function named `Lab1Part1RegExample_kernel`, two scalar integer inputs, one writable scalar output pointer, AXI-Lite HLS pragmas, and the scalar add body. |
| `Lab1Part1RegExample_harness.cpp` | Ordinary local test harness | A `main` function that calls the generated kernel with `3`, `5`, checks `argRegOut == 8`, prints a compact pass/fail line, and returns `0` on pass or `1` on mismatch. |

The kernel file should be generated as:

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

The harness file should be generated as:

```cpp
#include <iostream>

extern "C" void Lab1Part1RegExample_kernel(
    int argRegIn0,
    int argRegIn1,
    int *argRegOut);

int main() {
  constexpr int argRegIn0 = 3;
  constexpr int argRegIn1 = 5;
  constexpr int expected = 8;
  int argRegOut = 0;

  Lab1Part1RegExample_kernel(argRegIn0, argRegIn1, &argRegOut);

  if (argRegOut != expected) {
    std::cerr << "FAIL: expected argRegOut=" << expected
              << ", got " << argRegOut << "\n";
    return 1;
  }

  std::cout << "PASS: argRegOut=" << argRegOut << "\n";
  return 0;
}
```

The harness is intentionally separate from the kernel file so the same kernel source can be passed to an HLS tool later while the local harness remains a software-only oracle.

## Local compile command with ordinary C++ compiler

Run the first local check from the generated C++ directory:

```bash
cd /Users/david/Documents/David_code/lab-1-accelerator-bandits-1/gen/HLS/Lab1Part1RegExample/cpp
c++ -std=c++17 -O0 -g -Wall -Wextra -Wno-unknown-pragmas \
  Lab1Part1RegExample_kernel.cpp \
  Lab1Part1RegExample_harness.cpp \
  -o Lab1Part1RegExample_stage0
./Lab1Part1RegExample_stage0
```

Expected pass behavior:

```text
PASS: argRegOut=8
```

The executable must return exit code `0` only when the generated kernel writes `8`.

Expected fail behavior:

- A missing file, misspelled top symbol, incompatible function signature, or C++ syntax error fails at compile or link time with a nonzero compiler exit.
- A semantic mismatch, such as writing `7` or leaving `argRegOut` unchanged, prints `FAIL: expected argRegOut=8, got <value>` and returns exit code `1`.
- This local check does not require `sbt`, `make`, VCS, `FringeContext`, `run.sh`, or a generated bitstream.

## Optional Vitis/Vivado HLS project hook

Vitis or Vivado HLS project generation is not required for the first pass. Stage 0 acceptance is the ordinary C++ compile-and-run check above.

After the software check is stable, a generated HLS hook can live beside the C++ files as `run_hls.tcl` and use the same kernel and harness:

```tcl
open_project Lab1Part1RegExample_hls
set_top Lab1Part1RegExample_kernel
add_files cpp/Lab1Part1RegExample_kernel.cpp
add_files -tb cpp/Lab1Part1RegExample_harness.cpp
open_solution solution1
set_part {xc7z020clg484-1}
create_clock -period 10 -name default
csim_design
exit
```

That hook is a convenience for HLS `csim_design`; it must not become a gate for Stage 0 until the local compiler check already passes. Board part selection belongs to the chosen EE109 HLS tool flow, not to the scalar-add semantic oracle.

## Where outputs should live under existing generated directory conventions

The observed generated Lab1Part1 layout uses target-named lanes under the lab repository, such as:

- `/Users/david/Documents/David_code/lab-1-accelerator-bandits-1/gen/CS217/Lab1Part1RegExample/`
- `/Users/david/Documents/David_code/lab-1-accelerator-bandits-1/logs/CS217/Lab1Part1RegExample/`
- `/Users/david/Documents/David_code/lab-1-accelerator-bandits-1/reports/CS217/Lab1Part1RegExample/`

Use the same shape for the HLS lane:

```text
/Users/david/Documents/David_code/lab-1-accelerator-bandits-1/
  gen/HLS/Lab1Part1RegExample/
    cpp/
      Lab1Part1RegExample_kernel.cpp
      Lab1Part1RegExample_harness.cpp
      Lab1Part1RegExample_stage0
    hls/
      run_hls.tcl
  logs/HLS/Lab1Part1RegExample/
    stage0_compile.log
    stage0_run.log
  reports/HLS/Lab1Part1RegExample/
    stage0_harness.json
```

The required Stage 0 generated sources are the two C++ files in `gen/HLS/Lab1Part1RegExample/cpp/`. The executable, logs, report JSON, and HLS script are build products or optional flow hooks. Keeping them under the generated Lab1Part1 tree avoids source-tree churn in `/Users/david/Documents/David_code/spatial/src/` and keeps the HLS path parallel to the existing `CS217` generated output.
