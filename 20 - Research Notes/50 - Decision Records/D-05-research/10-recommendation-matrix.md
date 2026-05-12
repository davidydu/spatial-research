---
type: "research"
decision: "D-05"
angle: 10
---

# D-05 Research Angle 10: Recommendation Matrix

## Decision Frame

The current top-level contract is not one contract: target selection mutates `globals.target` inside `SpatialIP`, generated wrapper code then mutates app-specific globals, and `Instantiator` passes a parallel set of constructor constants into `AccelUnit` (`fringe/src/fringe/SpatialIP.scala:19`, `src/spatial/codegen/chiselgen/ChiselCodegen.scala:203`, `src/spatial/codegen/chiselgen/ChiselCodegen.scala:245`). The replacement should make target facts, host ABI, accelerator IO shape, and build overrides explicit before any Rust/HLS top is emitted. HLS toolchains generally reward compile-time-visible constants and simple top signatures (unverified), but this codebase evidence mainly shows that hidden ordering and duplicate sources of truth are the immediate hazards.

## Candidate Matrix

| Candidate | Determinism | Source compatibility | Host ABI safety | HLS friendliness | Implementation cost |
|---|---|---|---|---|---|
| Mutable global context | Poor: repeats today's singleton mutation and fallback defaults (`fringe/src/fringe/globals.scala:10`, `fringe/src/fringe/globals.scala:62`). | High: mirrors `SpatialIP`/`AccelWrapper` order (`fringe/src/fringe/SpatialIP.scala:36`, `src/spatial/codegen/chiselgen/ChiselCodegen.scala:215`). | Low: ABI offsets remain scattered across generated API code (`src/spatial/codegen/chiselgen/ChiselGenInterface.scala:160`). | Medium-low: HLS would depend on process state (unverified). | Low first step, high long-term. |
| Generated constants only | Medium: constants in `Instantiator` and `AccelWrapper` are stable per emission, but duplicated (`src/spatial/codegen/chiselgen/ChiselGenInterface.scala:125`, `src/spatial/codegen/chiselgen/ChiselGenInterface.scala:143`). | High: closest to current generated Scala. | Medium: offsets can be emitted, but no schema validates relationships (`src/spatial/codegen/chiselgen/ChiselGenInterface.scala:162`, `src/spatial/codegen/chiselgen/ChiselGenInterface.scala:166`). | High for simple scalar constants (unverified). | Medium. |
| Serialized sidecar only | Medium-high: one JSON/TOML file can be canonical (unverified). | Medium: requires new readers while preserving current emitters. | Medium: safer than globals, but stringly typed fields can drift (unverified). | Medium: HLS still needs generated headers/constants derived from the sidecar. | Medium. |
| Typed manifest plus generated artifacts | High: Rust structs validate once, then emit sidecar, host ABI, and HLS constants from one value. | Medium: maps cleanly to existing generated constants and constructor args (`src/spatial/codegen/chiselgen/ChiselCodegen.scala:263`, `src/spatial/codegen/chiselgen/ChiselCodegen.scala:276`). | High: arg classes, DRAM pointer offsets, loopbacks, instrumentation, and breakpoints can be checked together (`src/spatial/codegen/chiselgen/ChiselGenInterface.scala:131`, `src/spatial/codegen/chiselgen/ChiselGenController.scala:559`). | High: generated artifacts give HLS plain constants while Rust keeps type safety (unverified). | Medium-high. |
| Split target profile/app manifest | Highest: immutable platform profile plus app instance prevents target defaults from being overwritten by app codegen (`fringe/src/fringe/targets/DeviceTarget.scala:20`, `src/spatial/codegen/chiselgen/ChiselGenController.scala:566`). | Medium-low initially: requires disentangling `globals.target` from app fields (`fringe/src/fringe/globals.scala:18`, `fringe/src/fringe/globals.scala:47`). | Highest: host ABI lives with app, bus/shell facts live with target. | Highest: target headers and app headers can be regenerated independently (unverified). | High. |

## Recommendation

Adopt **typed manifest plus generated artifacts**, shaped so it can naturally split into **target profile** and **application manifest**. This is the best first deliverable because it replaces mutable globals without forcing every consumer to understand serialization. It also preserves the generated-artifact workflow: today `AccelUnit` already receives counts, stream lists, allocator count, and AXI stream lists as constructor parameters (`src/spatial/codegen/chiselgen/ChiselCodegen.scala:263`, `src/spatial/codegen/chiselgen/ChiselCodegen.scala:275`). The manifest should be the only source of truth; JSON/TOML sidecars and HLS/Rust constants are derived artifacts, not independent schemas.

The target part should own canonical target id, shell/fringe binding, BigIP-equivalent integration, widths, stream geometry, and channel count now exposed through `globals` accessors (`fringe/src/fringe/globals.scala:13`, `fringe/src/fringe/globals.scala:18`, `fringe/src/fringe/globals.scala:24`). It should also own latency/SRAM defaults currently mutable on `DeviceTarget` (`fringe/src/fringe/targets/DeviceTarget.scala:20`, `fringe/src/fringe/targets/DeviceTarget.scala:31`). The app part should own logical ABI and IO shape: arg counts, DRAM pointer args, loopbacks, memory streams, AXI streams, allocators, instrumentation, breakpoints, and wrapper lane allocation.

## Migration Plan

1. **Inventory and freeze fields.** Add a Rust `TopManifest` with `TargetProfile`, `ApplicationTop`, `HostAbi`, `InterfaceLayout`, `AllocatorInfo`, `Instrumentation`, and `BuildOptions`. Populate it from the same IR facts that now fill mutable maps in `ChiselGenCommon` (`src/spatial/codegen/chiselgen/ChiselGenCommon.scala:35`, `src/spatial/codegen/chiselgen/ChiselGenCommon.scala:44`).

2. **Move globals into manifest fields.** Target-derived `bigIP`, widths, stream words, external/target widths, and channel count move to `TargetProfile` (`fringe/src/fringe/globals.scala:13`, `fringe/src/fringe/globals.scala:24`). Flags and overrides move to `BuildOptions`: retime/perpetual/modular/debug/channel assignment plus operation, SRAM, and mux latencies (`fringe/src/fringe/globals.scala:26`, `src/spatial/codegen/chiselgen/ChiselGenController.scala:572`, `src/spatial/codegen/chiselgen/ChiselGenController.scala:580`).

3. **Replace generated `Instantiator`/`AccelWrapper` constants.** Emit `ApplicationTop` from the current scalar, DRAM, stream, AXI, allocator, instrumentation, and breakpoint emit sites (`src/spatial/codegen/chiselgen/ChiselGenInterface.scala:125`, `src/spatial/codegen/chiselgen/ChiselGenDRAM.scala:76`, `src/spatial/codegen/chiselgen/ChiselGenStream.scala:189`, `src/spatial/codegen/chiselgen/ChiselGenController.scala:540`). Keep generated HLS headers or Rust constants as derived files for source compatibility.

4. **Make ABI validation mandatory.** Validate ordered ArgIns, DRAM pointer offsets, ArgIOs, ArgOuts, instrumentation outputs, and breakpoints against the layout currently emitted in `ArgAPI.scala` (`src/spatial/codegen/chiselgen/ChiselGenInterface.scala:160`, `src/spatial/codegen/chiselgen/ChiselGenInterface.scala:185`). Record logical counts separately from padded hardware counts because `AccelWrapper` pads to one while `Instantiator` does not (`src/spatial/codegen/chiselgen/ChiselCodegen.scala:198`, `src/spatial/codegen/chiselgen/ChiselCodegen.scala:240`).

5. **Remove construction-order dependencies.** The Rust/HLS builder should validate the manifest, derive default stream policies explicitly, emit top constants/sidecar, then build the top signature. Only after that should shell/fringe integration run, replacing the current hidden sequence of target mutation, IO creation, and app generation (`fringe/src/fringe/SpatialIP.scala:19`, `fringe/src/fringe/SpatialIP.scala:39`, `src/spatial/codegen/chiselgen/ChiselCodegen.scala:279`).
