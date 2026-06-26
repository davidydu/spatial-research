---
type: hls-mapping
construct: ee109-abi-manifest-v0
category: rework
date: 2026-06-25
status: draft
---

# EE109 ABI Manifest v0

## ABI scope for EE109 MVP

`ee109_abi_manifest_v0` is a small, explicit host/HLS boundary contract for the selected EE109 HLS MVP. It is intentionally narrower than the broader D-23 `abi_manifest_v1`: D-23 recommends a manifest with kernel identity, host ABI slots, memories, numeric formats, lifecycle, and diagnostics, but this v0 keeps only the fields needed to compile Lab1Part1 first and to extend cleanly to dense DRAM and matrix return for Lab3 (`/Users/david/Documents/Spatial Research/20 - Research Notes/50 - Decision Records/D-23.md:52-63`).

The MVP ladder starts with `Lab1Part1RegExample.scala`, whose required surface is `runtimeArgs`, two `ArgIn`s, one `ArgOut`, `setArg`, `getArg`, an `Accel`, register reads, assignment, and integer add (`/Users/david/Documents/Spatial Research/90 - Meta/plans/2026-06-25-ee109-hls-mvp-plan.md:48-57`). The Lab1 source provides `runtimeArgs = "3 5"`, parses `N` and `M`, writes two ArgIns, assigns `argRegOut := argRegIn0Value + argRegIn1Value`, reads the ArgOut, and checks against `M + N` (`/Users/david/Documents/David_code/lab-1-accelerator-bandits-1/Lab1Part1RegExample/src/Lab1Part1RegExample.scala:5-29`).

For the first HLS projection, one Spatial `Accel` becomes one generated HLS top function. The plan already sketches the Lab1 behavioral target as `extern "C" void Lab1Part1RegExample_kernel(int argRegIn0, int argRegIn1, int *argRegOut)` with AXI-Lite control pragmas and `*argRegOut = argRegIn0 + argRegIn1` (`/Users/david/Documents/Spatial Research/90 - Meta/plans/2026-06-25-ee109-hls-mvp-plan.md:220-234`). This manifest records that logical ABI first; the C++ spelling is a projection.

Current Spatial Cppgen already has an implicit host ABI: `ArgInNew`, `HostIONew`, and `ArgOutNew` append symbols to `argIns`, `argIOs`, and `argOuts`, while `DRAMHostNew` appends to `drams`, allocates host memory through `c1->malloc`, and writes the pointer through `c1->setArg(..._ptr, ...)` (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenInterface.scala:20-40`). Its generated `ArgAPI.hpp` orders ArgIns first, DRAM pointers next, ArgIOs next, ArgOuts next, then optional instrumentation counters and early exits (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenInterface.scala:138-164`). Cppgen also sets runtime counts for ArgIns plus DRAM plus ArgIOs, ArgIOs, ArgOuts, instrumentation, and early exits before calling `c1->run()` (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenAccel.scala:24-36`).

Current Chiselgen has the corresponding hardware-side projection: `ArgInNew` records an ArgIn index and reads `accelUnit.io.argIns(api.<id>_arg)`, `HostIONew` records ArgIOs and wires a `MultiArgOut`, and `ArgOutNew` records ArgOuts after ArgIOs (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/chiselgen/ChiselGenInterface.scala:18-39`). Chiselgen records host DRAMs into `hostDrams`, connects their DRAM streams, creates a 64-bit pointer wire, and reads it from `accelUnit.io.argIns(api.<id>_ptr)` (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/chiselgen/ChiselGenDRAM.scala:17-23`). Its `ArgAPI.scala` emits ArgIns, DRAM pointers, ArgIOs, ArgOuts, instrumentation counters, and early exits as named API values (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/chiselgen/ChiselGenInterface.scala:156-187`).

## Manifest schema fields

The v0 manifest is a YAML-compatible logical schema. A later generator can serialize the same records as JSON.

| Field | Required content | EE109 v0 policy |
|---|---|---|
| `abi_schema` | Literal schema name and version | `ee109_abi_manifest_v0` |
| `kernel.name` | Stable Spatial kernel/test name | Use the `@spatial` class name, such as `Lab1Part1RegExample` |
| `kernel.entry_symbol` | Generated HLS top-level function name | `<kernel.name>_kernel` unless the source has a collision |
| `kernel.source_file` | Local source path | Absolute path for traceability |
| `kernel.source_refs` | Source line anchors for host/test and accelerator body | Include at least one source range per example |
| `scalar_inputs[]` | `ArgIn` records with name, Spatial type, HLS type, direction, ordinal, HLS port, conversion policy, and test value | For `Int`, use `raw_scalar_integer_v1`; keep the legacy Cppgen slot as a projection |
| `scalar_outputs[]` | `ArgOut` records with name, Spatial type, HLS type, direction, ordinal, HLS port, conversion policy, and expected value or comparator | For `Int`, use `raw_scalar_integer_v1`; represent HLS output as a writable scalar endpoint |
| `dram_buffers[]` | DRAM records with name, Spatial type, HLS pointer type, element type, rank, dimensions, layout, direction, transfer API, HLS bundle, conversion policy, and pointer slot projection | v0 supports dense row-major buffers only |
| `dimensions[]` | Runtime dimensions and constants used by DRAM buffers or loops | Store both symbolic names such as `R`, `C` and example values such as `16` |
| `transfers[]` | Host boundary actions such as `setArg`, `getArg`, `setMem`, `getMem`, and `getMatrix` | Preserve action order when it affects allocation or test harness shape |
| `conversion_policies[]` | Named conversion rules used by entries | `raw_scalar_integer_v1` for integer registers, `raw_memcpy_v1` for integer DRAM, `bit_exact_scaled_integer_v1` for future fixed-point default, and `cppgen_fractional_double_shift_v1` only for legacy compatibility |
| `test_inputs` | CLI args, scalar values, host array or matrix generator, and dimensions | Include concrete Lab1 and Lab3 test values |
| `expected_outputs` | Scalar values, matrix shape, checksum, or exact comparator | Prefer exact equality for integer examples |
| `hls_interface` | Vitis-compatible C++ top signature, port pragmas, memory bundles, and control bundle | `s_axilite` for control scalars and scalar result endpoints; `m_axi` plus AXI-Lite pointer control for DRAM buffers |
| `legacy_projection` | Cppgen/Chiselgen slot order and compatibility notes | Treat legacy `ArgAPI.hpp` and `ArgAPI.scala` as projections, not the portable source contract |

Conversion policy is explicit per entry. D-24 recommends bit-exact scaled integers as the canonical fixed-point default and keeps Cppgen's double/shift behavior as an explicit compatibility lane (`/Users/david/Documents/Spatial Research/20 - Research Notes/50 - Decision Records/D-24.md:42-56`). Cppgen's current fractional fixed-point host representation maps fractional `FixPtType` to `double`, while its register and memory transfer code shifts values into raw integer transport (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenCommon.scala:75-90`; `/Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenInterface.scala:42-80`; `/Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenInterface.scala:85-130`). Lab1 and Lab3 use `Int`, so v0 uses raw integer policies without fixed-point scaling.

## Lab1Part1 concrete manifest example

```yaml
abi_schema: ee109_abi_manifest_v0
kernel:
  name: Lab1Part1RegExample
  entry_symbol: Lab1Part1RegExample_kernel
  source_file: /Users/david/Documents/David_code/lab-1-accelerator-bandits-1/Lab1Part1RegExample/src/Lab1Part1RegExample.scala
  source_refs:
    host_setup: /Users/david/Documents/David_code/lab-1-accelerator-bandits-1/Lab1Part1RegExample/src/Lab1Part1RegExample.scala:5-16
    accel_body: /Users/david/Documents/David_code/lab-1-accelerator-bandits-1/Lab1Part1RegExample/src/Lab1Part1RegExample.scala:17-21
    oracle: /Users/david/Documents/David_code/lab-1-accelerator-bandits-1/Lab1Part1RegExample/src/Lab1Part1RegExample.scala:23-32

scalar_inputs:
  - name: argRegIn0
    spatial_role: ArgIn
    spatial_type: Int
    hls_type: int
    direction: host_to_kernel
    group_ordinal: 0
    legacy_arg_slot_projection: 0
    hls_port: argRegIn0
    conversion_policy: raw_scalar_integer_v1
    test_value: 3
  - name: argRegIn1
    spatial_role: ArgIn
    spatial_type: Int
    hls_type: int
    direction: host_to_kernel
    group_ordinal: 1
    legacy_arg_slot_projection: 1
    hls_port: argRegIn1
    conversion_policy: raw_scalar_integer_v1
    test_value: 5

scalar_outputs:
  - name: argRegOut
    spatial_role: ArgOut
    spatial_type: Int
    hls_type: int
    direction: kernel_to_host
    group_ordinal: 0
    legacy_arg_slot_projection: 2
    hls_port: argRegOut
    conversion_policy: raw_scalar_integer_v1
    expected_value: 8
    comparator: exact_equal

dram_buffers: []
dimensions: []

transfers:
  - api: setArg
    target: argRegIn0
    value_ref: test_inputs.argv[0]
  - api: setArg
    target: argRegIn1
    value_ref: test_inputs.argv[1]
  - api: getArg
    target: argRegOut
    result_ref: expected_outputs.argRegOut

conversion_policies:
  raw_scalar_integer_v1:
    storage: signed twos-complement integer
    host_value: exact integer
    scaling: none

test_inputs:
  argv: ["3", "5"]
  scalars:
    argRegIn0: 3
    argRegIn1: 5

expected_outputs:
  argRegOut: 8
  pass_condition: argRegOut == argRegIn0 + argRegIn1

hls_interface:
  signature: extern "C" void Lab1Part1RegExample_kernel(int argRegIn0, int argRegIn1, int *argRegOut)
  pragmas:
    - "#pragma HLS INTERFACE s_axilite port=argRegIn0 bundle=control"
    - "#pragma HLS INTERFACE s_axilite port=argRegIn1 bundle=control"
    - "#pragma HLS INTERFACE s_axilite port=argRegOut bundle=control"
    - "#pragma HLS INTERFACE s_axilite port=return bundle=control"
  body_equation: "*argRegOut = argRegIn0 + argRegIn1"

legacy_projection:
  cppgen_order_ref: /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenInterface.scala:138-147
  chiselgen_order_ref: /Users/david/Documents/David_code/spatial/src/spatial/codegen/chiselgen/ChiselGenInterface.scala:156-166
```

The Lab1 slot projection follows current Cppgen and Chiselgen user-visible ordering: ArgIns first, no DRAM pointers, no ArgIOs, then the single ArgOut (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenInterface.scala:138-147`; `/Users/david/Documents/David_code/spatial/src/spatial/codegen/chiselgen/ChiselGenInterface.scala:156-166`). The HLS projection does not need `FringeContext`: current Cppgen generates a host `TopHost.cpp` that includes `FringeContext.h`, `ArgAPI.hpp`, constructs `FringeContext("./verilog/accel.bit.bin")`, and loads it before running, but the HLS kernel signature records the boundary directly (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppFileGen.scala:59-98`; `/Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenAccel.scala:24-36`).

## Lab3 projected manifest example, enough to show 2D DRAM pointers and dimensions

Lab3's `convolve` creates two runtime scalar dimensions `R` and `C`, writes them from `image.rows` and `image.cols`, allocates two 2D DRAMs as `DRAM[T](R, C)`, calls `setMem(img, image)`, and returns `getMatrix(imgOut)` (`/Users/david/Documents/David_code/spatial/test/spatial/tests/ee109/Lab3.scala:11-24`; `/Users/david/Documents/David_code/spatial/test/spatial/tests/ee109/Lab3.scala:78-79`). Its concrete test uses `R = 16`, `C = 16`, and `border = 3`, builds a generated input matrix, computes a gold matrix, and checks `gold_sum == output_sum` (`/Users/david/Documents/David_code/spatial/test/spatial/tests/ee109/Lab3.scala:81-126`).

```yaml
abi_schema: ee109_abi_manifest_v0
kernel:
  name: Lab3Part1Convolution
  entry_symbol: Lab3Part1Convolution_kernel
  source_file: /Users/david/Documents/David_code/spatial/test/spatial/tests/ee109/Lab3.scala
  source_refs:
    host_setup: /Users/david/Documents/David_code/spatial/test/spatial/tests/ee109/Lab3.scala:11-24
    accel_body: /Users/david/Documents/David_code/spatial/test/spatial/tests/ee109/Lab3.scala:25-76
    matrix_return: /Users/david/Documents/David_code/spatial/test/spatial/tests/ee109/Lab3.scala:78-79
    oracle: /Users/david/Documents/David_code/spatial/test/spatial/tests/ee109/Lab3.scala:81-126

scalar_inputs:
  - name: R
    spatial_role: ArgIn
    spatial_type: Int
    hls_type: int
    direction: host_to_kernel
    group_ordinal: 0
    legacy_arg_slot_projection: 0
    hls_port: R
    conversion_policy: raw_scalar_integer_v1
    test_value: 16
  - name: C
    spatial_role: ArgIn
    spatial_type: Int
    hls_type: int
    direction: host_to_kernel
    group_ordinal: 1
    legacy_arg_slot_projection: 1
    hls_port: C
    conversion_policy: raw_scalar_integer_v1
    test_value: 16

scalar_outputs: []

dram_buffers:
  - name: img
    spatial_role: DRAM
    spatial_type: DRAM[Int]
    hls_type: const int *
    element_type: Int
    rank: 2
    dimensions: [R, C]
    example_shape: [16, 16]
    layout: row_major_dense
    flat_index: r * C + c
    direction: host_to_kernel
    transfer_api: setMem
    pointer_group_ordinal: 0
    legacy_arg_slot_projection: 2
    hls_port: img
    hls_bundle: gmem0
    conversion_policy: raw_memcpy_v1
  - name: imgOut
    spatial_role: DRAM
    spatial_type: DRAM[Int]
    hls_type: int *
    element_type: Int
    rank: 2
    dimensions: [R, C]
    example_shape: [16, 16]
    layout: row_major_dense
    flat_index: r * C + c
    direction: kernel_to_host
    transfer_api: getMatrix
    pointer_group_ordinal: 1
    legacy_arg_slot_projection: 3
    hls_port: imgOut
    hls_bundle: gmem1
    conversion_policy: raw_memcpy_v1

dimensions:
  - name: R
    source: image.rows
    hls_port: R
    example_value: 16
  - name: C
    source: image.cols
    hls_port: C
    example_value: 16
  - name: Kh
    source: class constant
    example_value: 3
  - name: Kw
    source: class constant
    example_value: 3
  - name: Cmax
    source: class constant
    example_value: 16

transfers:
  - api: setArg
    target: R
    value_ref: image.rows
  - api: setArg
    target: C
    value_ref: image.cols
  - api: setMem
    target: img
    value_ref: test_inputs.image
    shape_ref: [R, C]
  - api: getMatrix
    target: imgOut
    result_ref: expected_outputs.matrix
    shape_ref: [R, C]

conversion_policies:
  raw_scalar_integer_v1:
    storage: signed twos-complement integer
    host_value: exact integer
    scaling: none
  raw_memcpy_v1:
    storage: contiguous row-major elements
    host_value: exact integer elements
    scaling: none

test_inputs:
  scalars:
    R: 16
    C: 16
    border: 3
  image_generator: "image(i,j) = if (j > border && j < C-border && i > border && i < C-border) i*16 else 0"

expected_outputs:
  matrix:
    shape: [16, 16]
    element_type: Int
    comparator: exact_equal_after_getMatrix
  checksum:
    gold_sum: 44928
    output_sum: 44928
    comparator: exact_equal

hls_interface:
  signature: extern "C" void Lab3Part1Convolution_kernel(int R, int C, const int *img, int *imgOut)
  pragmas:
    - "#pragma HLS INTERFACE s_axilite port=R bundle=control"
    - "#pragma HLS INTERFACE s_axilite port=C bundle=control"
    - "#pragma HLS INTERFACE m_axi port=img offset=slave bundle=gmem0"
    - "#pragma HLS INTERFACE s_axilite port=img bundle=control"
    - "#pragma HLS INTERFACE m_axi port=imgOut offset=slave bundle=gmem1"
    - "#pragma HLS INTERFACE s_axilite port=imgOut bundle=control"
    - "#pragma HLS INTERFACE s_axilite port=return bundle=control"

legacy_projection:
  cppgen_order_ref: /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenInterface.scala:138-147
  chiselgen_order_ref: /Users/david/Documents/David_code/spatial/src/spatial/codegen/chiselgen/ChiselGenInterface.scala:156-166
  chisel_dram_pointer_ref: /Users/david/Documents/David_code/spatial/src/spatial/codegen/chiselgen/ChiselGenDRAM.scala:17-23
```

The Lab3 pointer slots are a projection of current Spatial ordering: two ArgIns occupy slots 0 and 1, then the two host DRAM pointers occupy slots 2 and 3 in the legacy Cppgen and Chiselgen API layouts (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenInterface.scala:138-147`; `/Users/david/Documents/David_code/spatial/src/spatial/codegen/chiselgen/ChiselGenInterface.scala:156-166`). Current Chiselgen connects dense load and store stream records for each DRAM through `accelUnit.io.memStreams.loads` and `.stores` and records `StreamParInfo` for those streams; v0 uses that as evidence that dense memory traffic is the relevant projection, while it does not expose the Fringe stream machinery in the HLS top signature (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/chiselgen/ChiselGenCommon.scala:416-435`).

## HLS C++ interface policy

Assume Vitis-compatible HLS pragmas for v0. The ABI manifest is the source contract; the generated C++ top function is one projection of it.

- Generate one `extern "C"` HLS top function per Spatial `Accel` chosen for the EE109 MVP.
- Lower `ArgIn[Int]` to `int` value parameters with `s_axilite` control ports.
- Lower `ArgOut[Int]` to one writable scalar endpoint, spelled as a pointer or reference according to the HLS tool's accepted form, with an `s_axilite` control port. The manifest records `direction: kernel_to_host`, so this spelling can change without changing the logical ABI.
- Lower host DRAM buffers to `const T *` for host-to-kernel buffers and `T *` for kernel-to-host buffers. Attach `m_axi` pragmas for the data port and `s_axilite` pragmas for pointer/control registration.
- Keep runtime dimensions as scalar `s_axilite` ports when they appear as `ArgIn`s or shape parameters. Lab3 uses `R` and `C` both as ArgIns and as DRAM dimensions (`/Users/david/Documents/David_code/spatial/test/spatial/tests/ee109/Lab3.scala:14-23`).
- Use row-major dense layout for `Matrix` and 2D DRAM buffers in v0. The Host-Accel Boundary note describes higher-rank tensor variants as flattening on set and reconstructing views on get (`/Users/david/Documents/Spatial Research/10 - Spec/20 - Semantics/90 - Host-Accel Boundary.md:42-45`).
- Treat current Cppgen/Chiselgen `ArgAPI` files as compatibility projections. Cppgen currently emits `ArgAPI.hpp` in the order ArgIns, DRAM pointers, ArgIOs, ArgOuts, instrumentation, exits (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenInterface.scala:138-164`), and Chiselgen emits `ArgAPI.scala` with the same user-visible groups before instrumentation and exits (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/chiselgen/ChiselGenInterface.scala:156-187`).
- Keep instrumentation counters, early exits, and stream metadata out of required v0 HLS signatures. Cppgen and Chiselgen both emit counters and early-exit API entries today, but Lab1Part1 and the projected Lab3 ABI do not need those entries for functional correctness (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenInterface.scala:148-164`; `/Users/david/Documents/David_code/spatial/src/spatial/codegen/chiselgen/ChiselGenInterface.scala:167-187`).

## Deferred ABI features

- Streams, external buses, blackboxes, floating point, file I/O, and explicit banking hints stay outside v0 because the EE109 plan explicitly excludes them unless a selected example requires them (`/Users/david/Documents/Spatial Research/90 - Meta/plans/2026-06-25-ee109-hls-mvp-plan.md:58-63`; `/Users/david/Documents/Spatial Research/90 - Meta/plans/2026-06-25-ee109-hls-mvp-plan.md:87-99`).
- Gather/scatter and sparse memory transfers stay outside v0. The MVP plan starts with contiguous dense slices and rejects gather/scatter first (`/Users/david/Documents/Spatial Research/90 - Meta/plans/2026-06-25-ee109-hls-mvp-plan.md:68-78`; `/Users/david/Documents/Spatial Research/90 - Meta/plans/2026-06-25-ee109-hls-mvp-plan.md:265-274`). Current Chiselgen has separate load, store, gather, and scatter stream maps, so v0's dense-only decision is a conscious subset rather than a claim that Spatial lacks sparse machinery (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/chiselgen/ChiselGenCommon.scala:22-26`; `/Users/david/Documents/David_code/spatial/src/spatial/codegen/chiselgen/ChiselGenCommon.scala:416-451`).
- Fixed-point host conversion is schema-ready but not active in Lab1Part1 or Lab3. If a later EE109 example adds fixed-point data, use `bit_exact_scaled_integer_v1` as the default and record any legacy Cppgen replay under `cppgen_fractional_double_shift_v1` (`/Users/david/Documents/Spatial Research/20 - Research Notes/50 - Decision Records/D-24.md:42-56`; `/Users/david/Documents/Spatial Research/20 - Research Notes/50 - Decision Records/D-24.md:78-86`).
- HostIO/ArgIO loopback, counters, early exits, and stale-manifest diagnostics remain diagnostic records rather than required HLS ports in v0. D-23 includes those in the broader manifest direction, but this MVP keeps the functional ABI small enough for the Lab1 tracer bullet (`/Users/david/Documents/Spatial Research/20 - Research Notes/50 - Decision Records/D-23.md:57-67`; `/Users/david/Documents/Spatial Research/90 - Meta/plans/2026-06-25-ee109-hls-mvp-plan.md:208-243`).
- Multiple kernels, dynamic accelerator-side DRAM allocation, Frames, FileBus/FileEOFBus, noninteractive file replay, and multiple AXI streams remain outside this manifest. Current Chiselgen has an explicit guard limiting AXI stream inputs and outputs to one each, which is another reason not to include external stream ABI in v0 (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/chiselgen/ChiselGenStream.scala:181-190`).
