---
type: spec
concept: Cppgen host code generation
source_files:
  - "/Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGen.scala:5-13"
  - "/Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppCodegen.scala:9-82"
  - "/Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppFileGen.scala:11-148"
  - "/Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenCommon.scala:13-149"
  - "/Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenAccel.scala:16-101"
  - "/Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenInterface.scala:19-166"
  - "/Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenArray.scala:1-433"
source_notes:
  - "[[other-codegens]]"
hls_status: rework
depends_on:
  - "[[20 - Scalagen]]"
status: draft
---

# Cppgen

## Summary

Cppgen is Spatial's synthesis host-driver backend: `CppGen` composes `CppCodegen`, `CppFileGen`, `CppGenCommon`, `CppGenInterface`, `CppGenAccel`, `CppGenDebug`, `CppGenMath`, `CppGenArray`, and `CppGenFileIO` into one host code generator, so behavior is distributed across trait overrides rather than centralized in one emitter /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGen.scala:5-13. The base `CppCodegen` declares `lang = "cpp"`, `ext = "cpp"`, and `entryFile = "TopHost.cpp"`, while `CppFileGen` sets `backend = "cpp"` /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppCodegen.scala:9-13 /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppFileGen.scala:7-10. This backend is not accelerator RTL: it is the C++ host program that allocates memories, marshals arguments, starts the generated accelerator through `FringeContext`, and reads results /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppFileGen.scala:95-99 /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenAccel.scala:24-36.

## Syntax or API

Cppgen emits six named support files before visiting the entry block: `cpptypes.hpp`, `functions.hpp`, `functions.cpp`, `structs.hpp`, `ArgAPI.hpp`, and `TopHost.cpp` /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppFileGen.scala:13-99. `structs.hpp` carries the standard library includes, `Fixed.hpp`, `using std::vector`, and a non-Zynq `int128_t` typedef /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppFileGen.scala:29-52. `TopHost.cpp` includes `FringeContext.h`, `functions.hpp`, `ArgAPI.hpp`, and `Fixed.hpp`, declares `printHelp`, opens `Application`, constructs `FringeContext("./verilog/accel.bit.bin")`, and calls `load()` /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppFileGen.scala:59-99. The footer closes `Application`, deletes the context, emits `printHelp`, parses `argv` into `vector<string>`, honors `--help` and `-h`, reads `DELITE_NUM_THREADS`, and calls `Application(numThreads, args)` /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppFileGen.scala:106-148.

## Semantics

The host-visible ABI is a flat register and pointer map. `ArgInNew`, `HostIONew`, and `ArgOutNew` record symbols into `argIns`, `argIOs`, and `argOuts`; `DRAMHostNew` records a DRAM, emits `c1->malloc`, and registers the pointer through `c1->setArg(<handle>_ptr, ...)` /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenInterface.scala:20-40. `SetReg` shifts fractional fixed-point values left by `f` bits before writing the arg register, while floating-point values are copied into an `int64_t` and masked to the declared mantissa-plus-exponent width /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenInterface.scala:42-61. `GetReg` sign-extends fixed-point results when needed and divides by `1 << f` before exposing the host value /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenInterface.scala:64-80. `SetMem` and `GetMem` bulk-copy vectors, but fractional fixed-point data of width at least 8 is rawified through a shifted integer vector; fractional fixed-point payloads below 8 bits throw an exception /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenInterface.scala:85-131.

## Implementation

`CppGenCommon` owns the mutable collections used by the footer and accelerator launcher: `instrumentCounters`, `earlyExits`, `controllerStack`, `argOuts`, `argIOs`, `argIns`, and `drams` /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenCommon.scala:13-34. It maps integer fixed-point types to sized C integer names when `f == 0`, but maps fixed-point values with fractional bits to `double`, which means host expressions are approximate even though register and memory transfers use bit shifts /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenCommon.scala:75-100. `toTrueFix` and `toApproxFix` are the shared conversions used by struct packing, register marshalling, file I/O, and math emission /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenCommon.scala:36-49.

`CppGenAccel` is the accelerator launch sequence. For `AccelScope`, it visits the block inside `inAccel`, sets the number of arg-ins, arg-IOs, arg-outs, instrumentation arg-outs, and early exits, flushes cache, records `time(0)`, calls `c1->run()`, reports elapsed time, and flushes cache again /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenAccel.scala:16-36. If instrumentation is enabled, it emits `instrumentation.txt`, reads cycles and iteration counters, computes iterations per parent, and prints stalled/idle counters when the controller has stream pressure /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenAccel.scala:58-101.

`CppGenArray` is the largest cppgen file at 433 source lines and handles host arrays, vectors, structs, map/reduce/filter/zip/fold, host-side conditionals, and non-hardware unrolled loops /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenArray.scala:1-433 /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenArray.scala:221-351. Its `SimpleStruct` case emits packed C++ structs into `structs.hpp`, field setters using `toTrueFix`, `toString` using `toApproxFix`, `toRaw`, and a raw-bit constructor /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenArray.scala:153-198. `CppGenMath` maps fixed and floating math to C/C++ expressions; `FixFMA` emits `a * b + c`, `FixMod` normalizes through a positive-mod expression, and fractional shifts use `pow(2., y)` rather than integer shifts /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenMath.scala:20-58 /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenMath.scala:144-156. `CppGenFileIO` lowers binary and CSV file operations to `fstream`, vectors, raw integer buffers, `memcpy`, and fixed-point conversion loops /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenFileIO.scala:35-86 /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenFileIO.scala:92-136. `CppGenDebug` handles text conversions, `PrintIf`, `DelayLine`, and host `Var` operations /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenDebug.scala:10-61.

## Interactions

`copyDependencies` always registers `synth/datastructures`, `synth/SW`, `synth/scripts`, `build.sbt`, and `run.sh`, then branches by hardware target to copy a software resources directory, a hardware resources directory, and a per-target Makefile /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppCodegen.scala:20-82. The target fan-out covers VCS, Zynq, ZedBoard, ZCU, CXP, AWS_F1, DE1, Arria10, and ASIC /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppCodegen.scala:38-75. `ArgAPI.hpp` is generated after traversal, assigning ArgIns first, DRAM pointers next, ArgIOs, ArgOuts, optional instrumentation counters, and early exits /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenInterface.scala:138-164.

Cppgen is scheduled from the main Spatial pipeline only after Chisel codegen when synthesis is enabled and the selected target reports a C++ host, so the emitted C++ and the generated Chisel/Fringe register layout are expected to agree on argument ordering /Users/david/Documents/David_code/spatial/src/spatial/Spatial.scala:246-247 /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenInterface.scala:138-164. This is why `CppGenInterface` and `CppGenAccel` share the same mutable `argIns`, `drams`, `argIOs`, `argOuts`, instrumentation, and early-exit collections from `CppGenCommon` /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenCommon.scala:13-34 /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenAccel.scala:24-29.

## HLS notes

For a Rust+HLS rewrite, the stable conceptual boundary is "host driver plus ABI map," not the C++ text itself: this boundary is evidenced by `FringeContext` allocation, register writes, memory copies, and the generated `ArgAPI.hpp` offsets /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppFileGen.scala:95-99 /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenInterface.scala:138-164. Fixed-point host semantics need rework because local host values become `double` for fractional fixed-point while device transfers use shifted raw integers /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenCommon.scala:75-100 /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenInterface.scala:42-80.

## Open questions

See [[open-questions-other-codegens#Q-oc-05]] for the resource-path rewrite question that affects Cppgen target packaging.
