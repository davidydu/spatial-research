---
type: research
decision: D-05
angle: 6
---

**Consumer matrix.**

The Chisel path uses `fringe.globals` as an elaboration-time scratchpad, not as mutable runtime state. `SpatialIP` first chooses a `DeviceTarget` from `targetName`, installs `globals.target`, then creates the accelerator and asks the target to add Fringe/IP wiring (`fringe/src/fringe/SpatialIP.scala:18`, `fringe/src/fringe/SpatialIP.scala:36`, `fringe/src/fringe/SpatialIP.scala:39`). `globals` then exposes target widths/channels, retiming/config flags, scalar counts, stream lists, AXI stream params, and heap allocator count (`fringe/src/fringe/globals.scala:18`, `fringe/src/fringe/globals.scala:26`, `fringe/src/fringe/globals.scala:47`, `fringe/src/fringe/globals.scala:53`, `fringe/src/fringe/globals.scala:57`, `fringe/src/fringe/globals.scala:60`).

| Consumer | Needs from replacement manifest | Evidence |
|---|---|---|
| HLS kernel/top | Target profile, scalar ABI shape, memory-stream/AXI-stream shape, heap allocator count, retime/math/SRAM/codegen flags as compile inputs. | Chisel bakes counts into `CustomAccelInterface` and `AccelUnit` constructors (`src/spatial/codegen/chiselgen/ChiselCodegen.scala:215`, `src/spatial/codegen/chiselgen/ChiselCodegen.scala:245`, `src/spatial/codegen/chiselgen/ChiselCodegen.scala:263`). |
| Host wrapper | Stable ArgAPI names and offsets, count setters, debug/instrument/early-exit partitions, run protocol. | `ArgAPI.scala` and C++ `ArgAPI.hpp` define offsets (`src/spatial/codegen/chiselgen/ChiselGenInterface.scala:156`, `src/spatial/codegen/cppgen/CppGenInterface.scala:139`); host code sets counts then runs (`src/spatial/codegen/cppgen/CppGenAccel.scala:24`, `src/spatial/codegen/cppgen/CppGenAccel.scala:32`). |
| Runtime/Fringe | Regfile dimensions, stream arbiter dimensions, channel assignment, heap ports, command/status behavior. | Fringe sizes arg vectors, streams, DRAM channels, heap, and RegFile from globals-derived values (`fringe/src/fringe/Fringe.scala:50`, `fringe/src/fringe/Fringe.scala:55`, `fringe/src/fringe/Fringe.scala:57`, `fringe/src/fringe/Fringe.scala:116`). |
| DSE/reports | Mostly target/model configuration and selected design point, not the Chisel global ABI; optional reconciliation with emitted HLS artifacts. | DSE evaluates latency and area through analyzers/models (`src/spatial/dse/DSEThread.scala:119`, `src/spatial/dse/DSEThread.scala:130`, `src/spatial/targets/HardwareTarget.scala:47`), while resource reporters walk IR metadata (`src/spatial/codegen/resourcegen/ResourceReporter.scala:61`). |
| Tests | Symbolic arg names, `setArg`/`getArg`, DRAM pointer ordering, exits/instrumentation observability. | Tests use user-level args and outputs, e.g. `setArg`, DRAMs, `getArg` (`test/spatial/tests/feature/dense/DotProduct.scala:29`, `test/spatial/tests/feature/dense/DotProduct.scala:32`, `test/spatial/tests/feature/dense/DotProduct.scala:55`) and HostIO/exit behavior (`test/spatial/tests/feature/control/Breakpoint.scala:8`, `test/spatial/tests/feature/control/Breakpoint.scala:23`). |

**Compile-time constants.**

Treat HLS-kernel structure as compile-time: target name/profile, address/data/external widths, channels, scalar/vector port counts, stream counts and `StreamParInfo`, AXI stream params, heap allocator count, `perpetual`, channel assignment, retiming, math latency knobs, `cheapSRAMs`, and `SramThreshold`. Chisel currently emits these before elaboration, then mutates globals so type-level bundle sizes and module bodies can read them (`src/spatial/codegen/chiselgen/ChiselCodegen.scala:203`, `src/spatial/codegen/chiselgen/ChiselCodegen.scala:216`; `src/spatial/codegen/chiselgen/ChiselGenController.scala:566`, `src/spatial/codegen/chiselgen/ChiselGenController.scala:581`). HLS pragmas and function signatures generally need static port and array interface structure (unverified), so the manifest should drive code generation rather than be loaded dynamically by the kernel.

**Build artifacts.**

Emit the ABI partition as a build artifact: ordered `arg_ins`, `dram_ptrs`, `arg_ios`, `arg_outs`, `instr_counters`, `early_exits`, and debug labels. Chisel and C++ already derive the same ordering: scalars first, DRAM pointers next, HostIOs next, ArgOuts next, then instrumentation and exits (`src/spatial/codegen/chiselgen/ChiselGenInterface.scala:159`, `src/spatial/codegen/chiselgen/ChiselGenInterface.scala:166`, `src/spatial/codegen/cppgen/CppGenInterface.scala:140`, `src/spatial/codegen/cppgen/CppGenInterface.scala:160`). Host contexts store counts because register offsets and debug dumps depend on them (`resources/synth/zynq.sw-resources/FringeContextZynq.h:288`, `resources/synth/zynq.sw-resources/FringeContextZynq.h:364`, `resources/synth/vcs.sw-resources/FringeContextVCS.h:452`, `resources/synth/vcs.sw-resources/FringeContextVCS.h:489`). This should become generated JSON plus language bindings, not handwritten globals.

**Runtime metadata.**

Runtime state is actual argument values, DRAM allocation addresses, command/status, debug counter values, and simulator-side memories. `setArg` writes registers and `getArg` computes offsets from the count metadata (`resources/synth/zynq.sw-resources/FringeContextZynq.h:308`, `resources/synth/zynq.sw-resources/FringeContextZynq.h:312`, `resources/synth/aws.sw-resources/headers/FringeContextAWS.h:414`, `resources/synth/aws.sw-resources/headers/FringeContextAWS.h:430`). The Rust simulator can load the same manifest at runtime to map names to slots; the HLS kernel should not. `argOutLoopbacksMap` should remain compatibility-only until proven live: it is declared and counted in globals, but the active uses found here are Chisel-side bookkeeping/comments rather than a live Fringe constructor input (`fringe/src/fringe/globals.scala:51`, `fringe/src/fringe/globals.scala:76`, `src/spatial/codegen/chiselgen/ChiselGenInterface.scala:62`, `src/spatial/codegen/chiselgen/ChiselCodegen.scala:245`).

**Decision posture.**

D-05 should define one immutable `TopManifest` with three views: `KernelShape` for compile-time HLS generation, `HostAbi` for emitted wrappers/tests, and `RunMetadata` for simulator/runtime values. This replaces global mutation with explicit dependency injection while preserving the current consumers' real contracts.
