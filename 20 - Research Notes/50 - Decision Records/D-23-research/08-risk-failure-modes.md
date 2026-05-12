---
type: "research"
decision: "D-23"
angle: 8
topic: "risk-failure-modes"
---

# D-23 Angle 8: Risk And Failure Modes

## 1. No Manifest

No manifest is the highest risk option because the ABI is already real but distributed. Cppgen records ArgIns, ArgIOs, ArgOuts, DRAMs, counters, and exits in mutable buffers (`src/spatial/codegen/cppgen/CppGenCommon.scala:13-34`), then emits slot numbers in `ArgAPI.hpp` (`src/spatial/codegen/cppgen/CppGenInterface.scala:138-164`). Chisel emits parallel facts into `ArgAPI.scala`, `Instantiator.scala`, and wrapper globals (`src/spatial/codegen/chiselgen/ChiselGenInterface.scala:121-187`; `src/spatial/codegen/chiselgen/ChiselCodegen.scala:196-245`). If Rust/HLS regenerates those facts locally, shape/stride mismatch is likely: DRAM allocation keeps rank/dims (`src/spatial/lang/DRAM.scala:40-54`; `src/spatial/node/DRAM.scala:11-15`), dense transfers separately compute raw offsets, sparse ranks, lengths, strides, packing, and byte sizes (`src/spatial/node/DenseTransfer.scala:79-129`). Testability also collapses: a value mismatch cannot identify whether the fault was scalar conversion, pointer order, transfer layout, stream protocol, or counter/exit offset.

## 2. Cppgen-Compatible Ad Hoc ABI

Cppgen compatibility lowers migration cost but preserves accidental policy. Its scalar order is clear: ArgIns, DRAM pointers, ArgIOs, ArgOuts, counters, exits (`src/spatial/codegen/cppgen/CppGenInterface.scala:138-164`), and launch code sets counts before `run()` (`src/spatial/codegen/cppgen/CppGenAccel.scala:24-36`). The failure mode is that "compatible" mixes several ABIs. Fractional fixed-point host values are `double` in C++ expressions (`src/spatial/codegen/cppgen/CppGenCommon.scala:75-99`), but register writes multiply by `1 << f`, reads sign-extend and divide, and DRAM copies rawify or unpack vectors (`src/spatial/codegen/cppgen/CppGenInterface.scala:42-80`; `src/spatial/codegen/cppgen/CppGenInterface.scala:85-131`). Sub-byte integer packing is LSB-lane ordered, while sub-byte fractional fixed point throws (`src/spatial/codegen/cppgen/CppGenInterface.scala:95-128`). An ad hoc Rust clone could match old goldens while leaving endian, packing, rounding, saturation, and D-24 policy undefined.

## 3. Chisel/Fringe-Compatible ABI

Chisel/Fringe compatibility is better for hardware truth but risky as a Rust/HLS contract because it includes shell behavior. Fringe uses 64-bit scalar registers, reserves command/status slots, offsets ArgIns by two, and writes ArgOuts through decoupled channels (`fringe/src/fringe/Fringe.scala:24-32`; `fringe/src/fringe/Fringe.scala:36-57`; `fringe/src/fringe/Fringe.scala:112-181`). VCS `setArg` writes `arg+2`, while AWS splits 64-bit values into two 32-bit pokes and reads outputs at `arg - numArgIns` (`resources/synth/vcs.sw-resources/FringeContextVCS.h:422-434`; `resources/synth/aws.sw-resources/headers/FringeContextAWS.h:413-440`). Toolchain drift is baked in: Fringe globals carry mutable target widths, channel assignment, stream lists, AXI defaults, and allocator count (`fringe/src/fringe/globals.scala:18-31`; `fringe/src/fringe/globals.scala:45-68`). Blindly inheriting this ABI could force HLS to preserve one-cycle read timing quirks, default streams, and padded counts instead of declaring target-specific lowering rules.

## 4. Target-Native ABI

Target-native HLS ports are attractive for vendor pragmas, but they are the easiest way to lose Spatial semantics. Streams are not just pointers: memory streams have command/data/ack bundles and vector lane metadata (`fringe/src/fringe/FringeBundles.scala:39-88`; `fringe/src/fringe/FringeBundles.scala:145-152`), and Chisel derives stream pressure from valid/ready or FIFO empty/full (`src/spatial/codegen/chiselgen/ChiselGenCommon.scala:247-279`). ScalaGen, by contrast, treats streams as elastic queues whose reads can return invalid and whose writes always enqueue (`src/spatial/codegen/scalagen/ScalaGenStream.scala:12-16`; `src/spatial/codegen/scalagen/ScalaGenStream.scala:84-97`). AXI streams add sideband risk: Spatial declares TDATA, TSTRB, TKEEP, TLAST, TID, TDEST, and TUSER (`src/spatial/lang/Bus.scala:28-50`), while Chisel fills defaults, filters reads by TID/TDEST, and currently supports at most one AXI input/output (`src/spatial/codegen/chiselgen/ChiselGenStream.scala:81-167`; `src/spatial/codegen/chiselgen/ChiselGenStream.scala:181-197`). A native ABI must still name stream protocol, capacity, sidebands, and deadlock policy.

## 5. Explicit Manifest-First ABI

Manifest-first has the best failure containment, but only if it is treated as a compatibility contract, not documentation. The manifest should version ordered slots, logical counts versus padded hardware counts, pointer ownership, shape/stride/layout, numeric conversion policy, endian/packing, stream protocol, counter/exit offsets, target capabilities, and diagnostic IDs. It can separate legacy modes such as `cppgen_fractional_double_shift_v1`, `hls_ready_valid_bounded`, and `target_native_vitis_v1` while letting D-24 choose the default fixed-point policy (`20 - Research Notes/50 - Decision Records/D-23-research/04-fixed-point-d24-overlap.md:21`). The cost is migration churn: generators, host runtime, simulator, HLS top signature, and tests must consume the same artifact. The payoff is that test failures become local: a bad ArgOut, stale HLS report, shape mismatch, endian mismatch, stream underflow, or early exit can cite one manifest entry instead of reverse-engineering traversal order.
