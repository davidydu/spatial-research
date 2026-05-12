---
type: "research"
decision: "D-23"
angle: 5
topic: "stream-file-hostio-d22-overlap"
---

# D-23 Angle 5: Stream/File Host IO Overlap With D-22

## 1. Stream Endpoints Are ABI Records

`StreamInNew[A](bus)` and `StreamOutNew[A](bus)` carry a `Bus` descriptor but only a placeholder dimension `Seq(I32(1))` (`src/spatial/node/StreamIn.scala:7-9`; `src/spatial/node/StreamOut.scala:7-9`). The language types are both local and remote memories, which is the key ABI hint: accelerators read/write them locally, but the host/fringe owns their lifetime (`src/spatial/lang/StreamIn.scala:9-28`; `src/spatial/lang/StreamOut.scala:10-29`; [[Streaming]]). D-23 should therefore make every stream endpoint a manifest item with `id`, `symbol`, `direction = in|out`, `element_type`, `element_bits`, `bus_kind`, `bus_bits`, `access_widths`, `producer`, `consumer`, and `endpoint_role = host_file|axi_stream|dram_app_stream|pin|sim_only`. The manifest must not infer stream shape from default globals: current Fringe globals silently provide default memory and AXI stream descriptors when lists are empty (`fringe/src/fringe/globals.scala:53-68`), while `CustomAccelInterface` takes explicit memory stream and AXI stream lists (`fringe/src/fringe/AccelTopInterface.scala:22-58`).

## 2. FileBus, Filenames, And Frame Sizes

File-backed IO is a simulator/testbench contract, not an HLS port contract. `FileBus[A](fileName)` records a filename and bit width; `FileEOFBus[A](fileName)` additionally requires a struct whose last field is `Bit`, interpreted as an end marker (`src/spatial/lang/Bus.scala:59-76`). ScalaGen still prompts interactively for stream filenames, reads lines containing digits, parses values through `bitsFromString`, queues them, and dumps `StreamOut` contents on accelerator exit (`spatial/emul/src/emul/Stream.scala:5-51`; `src/spatial/codegen/scalagen/ScalaGenStream.scala:23-82`; `src/spatial/codegen/scalagen/ScalaGenController.scala:165-168`; [[40 - FIFO LIFO Stream Simulation]]). The Scala executor path does use `FileBus(filename)` directly for file read/write queues (`src/spatial/executor/scala/resolvers/MemoryResolver.scala:28-32`).

Recommended fields: `file_path`, `file_path_source = bus|manifest|stdin_compat`, `file_mode = read|write`, `encoding = scalar|csv_vec|semicolon_struct`, `skip_line_policy`, `eof_policy = none|last_bit_field`, and `dump_timing = accel_scope_exit|streaming`. Frames need a second linkage record: `FrameHostNew` carries `dims`, `zero`, and the associated stream symbol (`src/spatial/node/Frame.scala:9-12`), and `FrameTransmit` derives transfer count from `len.head`, wraps local addresses if local storage is smaller, and sets packet `last` on `i == len.head - 1` (`src/spatial/node/FrameTransmit.scala:60-85`; [[20 - Memories]]). Add `frame_dims`, `frame_elements`, `local_wrap_policy`, and `frame_stream_id`.

## 3. AXI Stream Packet Shape

AXI streams need packet-level sideband fields, not just payload width. Spatial defines 64/256/512-bit AXI structs with `TDATA`, `TSTRB`, `TKEEP`, `TLAST`, `TID`, `TDEST`, and `TUSER`; bus descriptors store width plus `tid` and `tdest` (`src/spatial/lang/Bus.scala:28-50`). ChiselGen registers AXI StreamIn/Out endpoints, maps them to `accelUnit.io.axiStreamsIn/Out`, emits `AXI4StreamParameters(width, 8, 32)`, and currently errors above one AXI input or output (`src/spatial/codegen/chiselgen/ChiselGenStream.scala:17-32`, `:181-198`). For payload-only writes, ChiselGen fills sidebands with defaults; for full AXI payloads, it copies user-supplied fields and warns that bus `tid`/`tdest` are ignored (`src/spatial/codegen/chiselgen/ChiselGenStream.scala:81-131`). Reads filter payload-only streams by `TID` and `TDEST`, while full AXI reads concatenate all fields (`src/spatial/codegen/chiselgen/ChiselGenStream.scala:150-167`).

D-23 fields: `axi_width`, `tid`, `tdest`, `tstrb_policy`, `tkeep_policy`, `tlast_policy`, `tuser_policy`, `packet_mode = payload_only|full_axi_struct`, `max_endpoint_count`, and `unsupported_reason` for multi-endpoint cases.

## 4. Ready/Valid Policy Reuses D-22

D-22 already names the semantic split: `compat_scalagen_elastic` preserves mutable queues, advisory full, invalid-on-empty, and no deadlock claim; `bounded_hls_cycle` uses finite capacity, stalls/errors on full or empty, and records liveness diagnostics ([[D-22]]; [[04-hls-stream-fifo-mapping]]). D-23 should not invent fresh stream labels. It should attach `queue_policy`, `capacity_source`, `ready_valid_policy`, `backpressure_policy`, `underflow_policy`, `overflow_policy`, `deadlock_policy`, and `mode_label` to every stream/file endpoint. The source contrast is direct: ScalaGen stream writes enqueue without capacity checks and reads return invalid when empty (`src/spatial/codegen/scalagen/ScalaGenStream.scala:84-97`), while Chisel drives `valid`, `ready`, and controller forward/back pressure from stream valid/ready and FIFO empty/full (`src/spatial/codegen/chiselgen/ChiselGenStream.scala:34-175`; `src/spatial/codegen/chiselgen/ChiselGenCommon.scala:249-279`; [[Streaming]]). Manifest mode labels should be `sim_compat_file_elastic` for ScalaGen/FileBus replay and `hls_ready_valid_bounded` for HLS or RTL-facing evidence.
