---
type: "research"
decision: "D-05"
angle: 5
---

# Rust/HLS Top-Level Manifest Schema

## Replacement Boundary

D-05 should replace the implicit constructor-time mutation of `fringe.globals` with an explicit top-level manifest. The current Chisel path computes argument counts, stream lists, allocator counts, instrumentation counts, and then writes them into globals immediately before constructing the accelerator interface (`src/spatial/codegen/chiselgen/ChiselCodegen.scala:198`, `src/spatial/codegen/chiselgen/ChiselCodegen.scala:203`, `src/spatial/codegen/chiselgen/ChiselCodegen.scala:213`, `src/spatial/codegen/chiselgen/ChiselCodegen.scala:215`). The same file passes those values into `SpatialIP` and `AccelUnit`, so the manifest is a constructor contract, not a loose preferences file (`src/spatial/codegen/chiselgen/ChiselCodegen.scala:239`, `src/spatial/codegen/chiselgen/ChiselCodegen.scala:245`, `src/spatial/codegen/chiselgen/ChiselCodegen.scala:263`). `SpatialIP` then maps a target name to a target implementation and uses the global target to create the final IO/IP shell (`fringe/src/fringe/SpatialIP.scala:18`, `fringe/src/fringe/SpatialIP.scala:36`, `fringe/src/fringe/SpatialIP.scala:39`).

## Manifest Shape

The Rust source of truth should be:

```rust
pub struct TopManifest {
    pub schema_version: u32,
    pub app_name: String,
    pub target: TargetSpec,
    pub host_abi: HostAbi,
    pub interfaces: InterfaceLayout,
    pub allocators: AllocatorInfo,
    pub instrumentation: Instrumentation,
    pub control: ControlFlags,
    pub assumptions: AssumptionSet,
    pub artifacts: ArtifactPaths,
}
```

`schema_version` must gate every reader. `app_name` corresponds to the emitted root-controller app comment (`src/spatial/codegen/chiselgen/ChiselGenController.scala:551`). Every nested struct should use enums for closed choices, stable numeric indexes for generated ABI order, and strings only for user-visible names or emitted artifact paths.

## Required Payloads

`TargetSpec` should require `target_name`, `target_kind`, optional `device_part` for HLS backend selection (unverified), and derived widths: `addr_width`, `data_width`, `words_per_stream`, `external_w`, `external_v`, `target_w`, `num_channels`, plus top-level `io_w` and `io_v`. These replace target-derived global accessors and generated target-width conditionals (`fringe/src/fringe/globals.scala:15`, `fringe/src/fringe/globals.scala:18`, `fringe/src/fringe/globals.scala:24`, `src/spatial/codegen/chiselgen/ChiselCodegen.scala:144`).

`HostAbi` should require ordered `arg_ins`, `arg_outs`, `arg_ios`, `mem_arg_ins`, and `arg_out_loopbacks`. Each argument entry should carry `index`, `name`, `kind`, `value_type`, `bit_width`, and `direction`. This preserves the current zip-with-index ordering and loopback map while making the layout available to Rust host stubs and HLS top signatures (`src/spatial/codegen/chiselgen/ChiselGenInterface.scala:125`, `src/spatial/codegen/chiselgen/ChiselGenInterface.scala:128`, `src/spatial/codegen/chiselgen/ChiselGenInterface.scala:131`, `src/spatial/codegen/chiselgen/ChiselGenInterface.scala:138`).

`InterfaceLayout` should require `memory_streams.load/store/gather/scatter: Vec<StreamParInfo>` and `axi_streams.in/out: Vec<AxiStreamSpec>`, with explicit defaults only after validation. The current globals store these lists and synthesize fallback stream parameters if they are empty (`fringe/src/fringe/globals.scala:53`, `fringe/src/fringe/globals.scala:62`, `fringe/src/fringe/globals.scala:67`). The manifest should also record generated mux lane assignments for stream and buffer lanes because the Chisel wrapper allocates them by mutable maps (`src/spatial/codegen/chiselgen/ChiselCodegen.scala:218`, `src/spatial/codegen/chiselgen/ChiselCodegen.scala:224`, `src/spatial/codegen/chiselgen/ChiselCodegen.scala:230`).

`AllocatorInfo` should require `num_allocators` and a vector of allocator descriptors with `id`, `memory_space`, `channel`, and `scope` when the IR can name them. The current boundary only exposes the count, but it is already passed into both globals and `AccelUnit` (`fringe/src/fringe/globals.scala:60`, `src/spatial/codegen/chiselgen/ChiselCodegen.scala:213`, `src/spatial/codegen/chiselgen/ChiselCodegen.scala:269`).

## Instrumentation And Assumptions

`Instrumentation` should require `counter_arg_count`, `controller_count`, `breakpoint_count`, and a list of named breakpoints. Chisel currently emits instrumentation counters, controller count, and early-exit breakpoint count as top-level values, then folds instrumentation and breakpoints into argument outputs (`src/spatial/codegen/chiselgen/ChiselGenController.scala:558`, `src/spatial/codegen/chiselgen/ChiselGenController.scala:561`, `src/spatial/codegen/chiselgen/ChiselCodegen.scala:199`, `src/spatial/codegen/chiselgen/ChiselCodegen.scala:244`).

`ControlFlags` should require `retime`, `perpetual_ip`, `channel_assignment`, `enable_modular`, `enable_verbose`, and `enable_debug_regs`; `AssumptionSet` should require `max_latency`, operation latencies for fixed-point add/sub/mul/div/mod/eql, `mux_latency`, `sram_load_latency`, `sram_store_latency`, `cheap_srams`, and `sram_threshold`. These fields replace mutable globals and target fields set by controller codegen (`fringe/src/fringe/globals.scala:26`, `fringe/src/fringe/globals.scala:31`, `src/spatial/codegen/chiselgen/ChiselGenController.scala:564`, `src/spatial/codegen/chiselgen/ChiselGenController.scala:566`, `src/spatial/codegen/chiselgen/ChiselGenController.scala:579`).

## Rust And Sidecar Contract

`ArtifactPaths` should require generated paths for `accel_wrapper`, `instantiator`, `arg_interface`, `accel_unit`, `controllers`, `manifest_json`, and optional `manifest_toml`. Those names mirror the generated files today (`src/spatial/codegen/chiselgen/ChiselCodegen.scala:129`, `src/spatial/codegen/chiselgen/ChiselCodegen.scala:148`, `src/spatial/codegen/chiselgen/ChiselCodegen.scala:175`, `src/spatial/codegen/chiselgen/ChiselCodegen.scala:251`, `src/spatial/codegen/chiselgen/ChiselCodegen.scala:287`).

Rust structs should be the canonical API used by the HLS top builder, host ABI generator, and artifact emitter. A JSON sidecar should be the canonical serialized interchange because it is straightforward for generated tools to consume (unverified). A TOML sidecar is useful as a review/debug view because humans can scan sections and comments more easily (unverified), but it should be derived from the same Rust structs to avoid a second schema. The migration rule is simple: no HLS or host code may read mutable process-global state; it receives `&TopManifest` or a validated deserialized copy.
