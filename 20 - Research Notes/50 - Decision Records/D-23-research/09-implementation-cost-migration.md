---
type: "research"
decision: "D-23"
angle: 9
topic: "implementation-cost-migration"
---

# D-23 Angle 9: Implementation Cost and Migration Plan

## Policy Cost Matrix

**No manifest/ad hoc** is lowest immediate cost and highest migration risk. It preserves today's scattered mutable state: cppgen buffers counters, exits, ArgOuts, ArgIOs, ArgIns, and DRAMs in separate collections (`src/spatial/codegen/cppgen/CppGenCommon.scala:13-34`), then emits ordinal constants late in `ArgAPI.hpp` (`src/spatial/codegen/cppgen/CppGenInterface.scala:138-164`). Chisel repeats the pattern with separate maps and counters (`src/spatial/codegen/chiselgen/ChiselGenCommon.scala:34-44`; `src/spatial/codegen/chiselgen/ChiselGenInterface.scala:156-187`). Cost: low now, high debugging and Rust/HLS drift later.

**Cppgen-compatible manifest** is medium cost. It can mirror the stable legacy order, scalar ArgIns, DRAM pointers, ArgIOs, ArgOuts, counters, exits, because cppgen already registers DRAM pointers with `malloc` and `setArg` (`src/spatial/codegen/cppgen/CppGenInterface.scala:36-40`) and sets runtime counts before `run()` (`src/spatial/codegen/cppgen/CppGenAccel.scala:24-36`). It also matches host libraries: `FringeContextBase` exposes `load`, `malloc`, `memcpy`, `run`, `getArg`, `setArg`, count setters, and `flushCache` (`resources/synth/vcs.sw-resources/FringeContextBase.h:13-29`). The catch is D-24: fractional fixed values are host `double` but transported as shifted integers (`src/spatial/codegen/cppgen/CppGenCommon.scala:75-89`; `src/spatial/codegen/cppgen/CppGenInterface.scala:42-80`).

**Chisel/Fringe-compatible manifest** is medium-high. It captures hardware truth: command/status registers, 64-bit scalar bus, arg vectors, memory streams, heap, and DRAM channels (`fringe/src/fringe/Fringe.scala:21-57`, `fringe/src/fringe/Fringe.scala:112-181`). It also covers stream metadata emitted into wrappers (`src/spatial/codegen/chiselgen/ChiselGenInterface.scala:121-152`) and AXI sideband rules and one-stream limits (`src/spatial/codegen/chiselgen/ChiselGenStream.scala:17-31`, `src/spatial/codegen/chiselgen/ChiselGenStream.scala:181-197`). Cost is higher because Rust must consume Chisel-era globals, not just host slots (`fringe/src/fringe/globals.scala:45-78`).

**Target-native HLS ABI** is highest and target-multiplied. Existing generation selects VCS, Zynq, AWS, and other resource packages per target (`src/spatial/codegen/cppgen/CppCodegen.scala:37-80`), while runtimes disagree on register lowering: VCS offsets by `arg+2` (`resources/synth/vcs.sw-resources/FringeContextVCS.h:422-434`), AWS splits 64-bit writes and reads outputs at `arg - numArgIns` (`resources/synth/aws.sw-resources/headers/FringeContextAWS.h:413-440`). Native HLS pragmas would still need a schema to keep host, tests, and reports aligned.

**Explicit versioned manifest-first ABI** is high initial cost but lowest long-term risk: one `abi_manifest_v1` becomes the source for codegen, Rust host bindings, target adapters, reports, and compatibility checks.

## Affected Surfaces

Codegen needs a shared ABI collector before cppgen/chiselgen emit local APIs. The existing codegen framework already writes generated files through `inGen(out, entryFile)` (`argon/src/argon/codegen/Codegen.scala:14-21`, `argon/src/argon/codegen/Codegen.scala:75-80`), so adding `abi_manifest_v1.json` is mechanically small. Schema generation is less free: the build has `scala-xml` and `pureconfig`, but no JSON schema library (`build.sbt:17-24`), and the only JSON-like generator is manual string emission for HyperMapper (`src/spatial/dse/HyperMapperDSE.scala:52-104`). Runtime work is larger: Rust must model scalar writes, DRAM allocation/copy, run/poll, ArgIO/ArgOut readback, instrumentation, exits, and stream endpoints.

## Tests And Reports

Tests should become manifest readback tests, not only value tests. Representative coverage already exists for CLI args (`test/spatial/tests/compiler/CLITest.scala:6-18`), scalar/HostIO/DRAM flows (`apps/src/HelloSpatial.scala:6-17`, `apps/src/HelloSpatial.scala:24-35`, `apps/src/HelloSpatial.scala:73-78`), DRAM runtime transfer (`test/spatial/tests/feature/memories/dram/DRAMRuntime.scala:10-23`), and sub-byte packing (`test/spatial/tests/feature/transfers/TransferSubByteTypes.scala:13-29`, `test/spatial/tests/feature/transfers/TransferSubByteTypes.scala:45-63`). Add golden manifest fixtures and target adapter tests for VCS/AWS offsets. Reports should include manifest hash, slot table, stream table, and conversion policies beside existing report files such as `Memories.report` (`src/spatial/report/MemoryReporter.scala:26-105`) and cppgen `instrumentation.txt` (`src/spatial/codegen/cppgen/CppGenAccel.scala:58-100`).

## Backwards Compatibility

Compatibility should be explicit. Keep generating `ArgAPI.hpp` and `ArgAPI.scala` during transition (`src/spatial/codegen/cppgen/CppFileGen.scala:55-57`; `src/spatial/codegen/chiselgen/ChiselGenInterface.scala:156-187`). If no manifest exists, Rust may import a legacy layout named `cppgen_ordinal_v0`; if a manifest exists, generated constants should be derived from it. D-22 overlap requires stream policy labels, because cppgen currently ignores stream transport (`src/spatial/codegen/cppgen/CppGenInterface.scala:82-83`) while Chisel models AXI and memory streams. D-24 overlap requires a `conversion_policy` per scalar, DRAM, file, and stream payload, not a global default.

## Staged Rollout

Phase 0: document current cppgen and Chisel layouts as `legacy_cppgen_v0` and `legacy_fringe_v0`. Phase 1: emit manifest sidecar plus legacy APIs, with tests comparing manifests to generated constants. Phase 2: make Rust host bindings consume the manifest while cppgen remains the oracle. Phase 3: add HLS target adapters and report artifacts. Phase 4: require `abi_version`, `schema_version`, and `min_runtime`, then reject missing or stale manifests instead of guessing.
