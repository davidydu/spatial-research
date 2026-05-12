---
type: "research"
decision: "D-05"
angle: 8
---

# Cost And Risk Alternatives For D-05

## Baseline Risk Surface

The replacement must remove order-sensitive top-level state, not just rename it. Today `fringe.globals` owns the mutable target, build flags, channel assignment, scalar counts, stream lists, AXI stream lists, allocator count, and default fallbacks (`fringe/src/fringe/globals.scala:10`, `fringe/src/fringe/globals.scala:26`, `fringe/src/fringe/globals.scala:31`, `fringe/src/fringe/globals.scala:47`, `fringe/src/fringe/globals.scala:53`, `fringe/src/fringe/globals.scala:62`). Target selection is split: Spatial CLI or app settings select a compiler target (`src/spatial/Spatial.scala:264`, `src/spatial/Spatial.scala:587`, `src/spatial/Spatial.scala:598`), while generated Chisel instantiation separately maps a string to a Fringe `DeviceTarget` and writes `globals.target` (`fringe/src/fringe/SpatialIP.scala:18`, `fringe/src/fringe/SpatialIP.scala:19`). The implementation risk is therefore divergence between compiler target, generated HLS target, host ABI, and runtime shell.

## Reject Mutable Context And Constants-Only

Preserving a mutable singleton/context has the lowest short-term port cost, because it mirrors `globals.target`, `globals.retime`, `globals.perpetual`, `globals.channelAssignment`, and mutable target latency fields (`fringe/src/fringe/globals.scala:10`, `fringe/src/fringe/globals.scala:26`, `src/spatial/codegen/chiselgen/ChiselGenController.scala:566`, `src/spatial/codegen/chiselgen/ChiselGenController.scala:580`). Reject it as the main design: it keeps the same lifecycle hazard, especially because scalar and stream counts are assigned only after codegen has accumulated IR facts (`src/spatial/codegen/chiselgen/ChiselCodegen.scala:197`, `src/spatial/codegen/chiselgen/ChiselCodegen.scala:203`, `src/spatial/codegen/chiselgen/ChiselCodegen.scala:207`). In Rust this would likely become `static` or interior-mutability state, which is easy to misuse across tests and multi-artifact builds (unverified).

A generated Rust constants module is attractive for HLS specialization, since arg counts and stream shapes are compile-time interface facts (`src/spatial/codegen/chiselgen/ChiselGenInterface.scala:125`, `src/spatial/codegen/chiselgen/ChiselGenInterface.scala:134`, `fringe/src/fringe/AccelTopInterface.scala:22`, `fringe/src/fringe/AccelTopInterface.scala:41`). Reject it as the only mechanism. Constants do not explain provenance, defaults, schema version, target choice, or host ABI indexing, and they cannot replace host-side generated `ArgAPI.hpp` definitions (`src/spatial/codegen/cppgen/CppGenInterface.scala:139`, `src/spatial/codegen/cppgen/CppGenInterface.scala:141`, `src/spatial/codegen/cppgen/CppGenInterface.scala:147`).

## Reject Serialized-Only Authority

A serialized manifest only, such as JSON/TOML, has low integration cost and good reviewability (unverified), but should not be the authority. The current path has typed-ish construction pressure from Scala constructors: `AccelUnit` takes scalar counts, allocator count, stream lists, and AXI stream lists as parameters (`src/spatial/codegen/chiselgen/ChiselCodegen.scala:263`, `src/spatial/codegen/chiselgen/ChiselCodegen.scala:269`, `src/spatial/codegen/chiselgen/ChiselCodegen.scala:270`). A stringly manifest alone would move validation to consumers and could silently preserve fallback behavior such as default stream descriptors when lists are empty (`fringe/src/fringe/globals.scala:62`, `fringe/src/fringe/globals.scala:67`). Keep serialization as an emitted artifact for debugging, caching, and host/bitstream compatibility checks, but not as the builder API.

## Recommend Typed Builder Plus Artifacts

The best core is a typed manifest builder plus generated artifacts. Implementation cost is moderate: it must gather the same fields now emitted across Chisel interface, controller, and codegen finalization, then validate them once before generation (`src/spatial/codegen/chiselgen/ChiselGenInterface.scala:121`, `src/spatial/codegen/chiselgen/ChiselGenController.scala:537`, `src/spatial/codegen/chiselgen/ChiselCodegen.scala:238`). Risk reduction is high because one `TopManifest` can feed the HLS top signature, Rust constants, serialized sidecar, and host ABI headers. It should model channel assignment as a checked enum because Fringe currently uses a global strategy object whose assignments depend on global stream counts and target channel count (`fringe/src/fringe/ChannelAssignment.scala:3`, `fringe/src/fringe/ChannelAssignment.scala:14`, `fringe/src/fringe/ChannelAssignment.scala:25`, `fringe/src/fringe/Fringe.scala:80`). It should also require explicit latency and control assumptions, because arithmetic and SRAM latency knobs are written into mutable target fields during controller post-generation (`fringe/src/fringe/targets/DeviceTarget.scala:20`, `fringe/src/fringe/targets/DeviceTarget.scala:29`, `src/spatial/codegen/chiselgen/ChiselGenController.scala:575`, `src/spatial/codegen/chiselgen/ChiselGenController.scala:579`).

## Combine With A Narrow Handshake

The two-phase host/HLS handshake should be combined as a guardrail, not a structural source of truth. Host code already configures counts and then runs through command/status registers (`src/spatial/codegen/cppgen/CppGenAccel.scala:24`, `src/spatial/codegen/cppgen/CppGenAccel.scala:31`, `resources/synth/zynq.sw-resources/FringeContextZynq.h:254`, `resources/synth/zynq.sw-resources/FringeContextZynq.h:288`). Register offsets and debug ranges depend on the same counts (`resources/synth/zynq.sw-resources/FringeContextZynq.h:308`, `resources/synth/zynq.sw-resources/FringeContextZynq.h:365`). Add a manifest hash/schema/ABI-version check before launch, but reject a dynamic handshake that discovers arg or stream topology at runtime: HLS top-level ports still need fixed shapes before synthesis (unverified).

Recommendation: reject mutable singleton/context, constants-only, and serialized-only as primary designs. Use a typed Rust manifest builder as the source of truth, emit constants and serialized artifacts from it, and add a narrow host/HLS compatibility handshake.
