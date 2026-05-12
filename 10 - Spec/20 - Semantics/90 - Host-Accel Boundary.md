---
type: spec
status: draft
concept: host-accelerator-boundary
source_files:
  - "src/spatial/node/Reg.scala:11-61"
  - "src/spatial/node/DRAM.scala:11-45"
  - "src/spatial/node/Frame.scala:11-36"
  - "src/spatial/lang/api/TransferAPI.scala:1-88"
  - "src/spatial/lang/host/Array.scala:1-231"
  - "/Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenInterface.scala:19-166"
  - "/Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenAccel.scala:16-101"
  - "/Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppFileGen.scala:59-148"
  - "src/spatial/codegen/chiselgen/ChiselGenInterface.scala:121-189"
  - "fringe/src/fringe/Fringe.scala:36-182"
  - "fringe/src/fringe/templates/axi4/AXI4LiteToRFBridge.scala:23-120"
source_notes:
  - "[[20 - Memories]]"
  - "[[30 - Memory Accesses]]"
  - "[[60 - Host and IO]]"
  - "[[10 - Cppgen]]"
  - "[[60 - Instantiation]]"
  - "[[50 - Streams and DRAM]]"
hls_status: rework
depends_on:
  - "[[20 - Memories]]"
  - "[[30 - Memory Accesses]]"
  - "[[60 - Host and IO]]"
  - "[[10 - Cppgen]]"
  - "[[60 - Instantiation]]"
  - "[[50 - Streams and DRAM]]"
---

# Host-Accel Boundary

## Summary

The host-accelerator boundary is the protocol connecting host tensors and scalar args to an `AccelScope`. [[20 - Memories]] defines boundary memories (`ArgIn`, `ArgOut`, `HostIO`, `DRAM`, `Frame`). [[60 - Host and IO]] defines the user transfer API. [[10 - Cppgen]] defines host-side C++ marshalling and accelerator launch. [[60 - Instantiation]] defines the Chisel/Fringe register and stream layout. The semantic sequence is: host allocates/marshals memories and scalar args, host starts the accelerator, accelerator reads args and remote memory streams, accelerator signals completion through Fringe/run completion, and host reads scalar and memory results.

## Formal Semantics

Scalar boundary memories are register-family allocations. `ArgInNew`, `ArgOutNew`, and `HostIONew` extend `RegAlloc`, carry an init value, and have `dims = Nil` (`src/spatial/node/Reg.scala:11-15`). `GetReg` and `SetReg` are host-side reader/writer nodes distinct from accelerator `RegRead`/`RegWrite`; they use empty addresses and empty enables (`src/spatial/node/Reg.scala:49-61`). `TransferAPI.setArg` stages `SetReg`, converting literals through the register's `Bits[A].from`; `getArg` stages `GetReg` (`src/spatial/lang/api/TransferAPI.scala:9-25`). Thus `setArg/getArg` are scalar host-register operations, not local datapath reads and writes.

Remote memory boundary nodes are explicit. `DRAMHostNew` allocates a host-owned DRAM with dimensions; `DRAMAccelNew` allocates rank-only accelerator-side DRAM; `DRAMAlloc`, `DRAMDealloc`, `DRAMAddress`, and `DRAMIsAlloc` manipulate allocation state; `SetMem` writes host tensor data into a DRAM; `GetMem` copies DRAM data into a host tensor (`src/spatial/node/DRAM.scala:11-45`). Frame nodes mirror that pattern around frame streams: `FrameHostNew` carries dimensions, zero value, and a stream symbol; `FrameAlloc`, `FrameDealloc`, `FrameAddress`, and `FrameIsAlloc` are frame boundary operations (`src/spatial/node/Frame.scala:11-36`). `TransferAPI.setMem/getMem` stage the corresponding nodes, with `getMem` allocating a `Tensor1.empty` of `dram.dims.prodTree`; higher-rank tensor variants flatten on set and reconstruct views on get (`src/spatial/lang/api/TransferAPI.scala:37-88`).

DRAM ownership transitions are therefore: host-side creation creates a host allocation and pointer; `setMem` moves or copies host tensor payload into the runtime's backing memory; accelerator transfer nodes read/write through Fringe streams during `AccelScope`; `getMem` copies the final payload back to a host tensor. Accelerator-side DRAM adds an allocation subprotocol: `DRAMAlloc` requests a device allocation and `DRAMDealloc` releases it. The current Chisel entry documents host DRAM as always allocated for `DRAMIsAlloc`, while accel DRAM exposes allocator output state (`spatial/src/spatial/codegen/chiselgen/ChiselGenDRAM.scala:17-67` as summarized by [[50 - Streams and DRAM]]).

Cppgen is the concrete host reference for synthesis runs. `DRAMHostNew` records the DRAM, emits `c1->malloc`, and writes the resulting pointer into an arg slot with `c1->setArg(<dram>_ptr, ...)` (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenInterface.scala:20-40`). `SetReg` shifts fractional fixed-point scalar values left before writing registers, while `GetReg` sign-extends and divides by `1 << f` for host exposure (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenInterface.scala:42-80`). `SetMem` and `GetMem` bulk-copy vectors, with fractional fixed-point data converted through shifted integer vectors and sub-8-bit fractional payloads rejected (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenInterface.scala:85-131`).

Cppgen also emits the host-side argument manifest. `ArgAPI.hpp` assigns scalar and memory argument offsets, writes one `#define` per register or pointer, and includes counters plus early-exit slots after user-visible arguments (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenInterface.scala:138-166`). This manifest is the host counterpart to Chisel `ArgAPI.scala`, and both must agree for `setArg`, `getArg`, and memory pointer traffic to be meaningful.

The accelerator transaction is emitted by `CppGenAccel`. For `AccelScope`, Cppgen visits the block, sets numbers of arg-ins, arg-IOs, arg-outs, instrumentation counters, and early exits, flushes cache, records time, calls `c1->run()`, reports elapsed time, and flushes cache again (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenAccel.scala:16-36`). That is the host-level trigger/done boundary: by the time `run()` returns, host reads of `ArgOut`, `HostIO`, DRAM, and instrumentation counters observe accelerator results.

Fringe/Chisel defines the register map that Cppgen and generated hardware must agree on. `ChiselGenInterface.emitPostMain` emits `ArgAPI.scala` with ArgIns first, DRAM pointers next, ArgIOs, ArgOuts, instrumentation counters, and early exits (`src/spatial/codegen/chiselgen/ChiselGenInterface.scala:156-187`). Fringe exposes scalar read/write ports, accelerator `argIns`, `argOuts`, and `argEchos`, and instantiates a `RegFile` sized by arg counts and debug outputs (`fringe/src/fringe/Fringe.scala:36-57`, `fringe/src/fringe/Fringe.scala:112-117`). AXI4-Lite bridges translate host AXI transactions to `raddr`, `wen`, `waddr`, `wdata`, and `rdata` signals (`fringe/src/fringe/templates/axi4/AXI4LiteToRFBridge.scala:23-120`).

The C++ host wrapper supplies process-level setup and teardown around that ABI. `TopHost.cpp` includes `FringeContext.h`, constructs `FringeContext("./verilog/accel.bit.bin")`, calls `load()`, parses command-line arguments and `DELITE_NUM_THREADS`, then calls the generated `Application` (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppFileGen.scala:59-148`). This is outside accelerator semantics but inside reproducible host-driver behavior.

Frame streaming follows the same boundary but with stream payloads. `FrameHostNew` binds a frame to a stream symbol, and `FrameTransmit` lowers to a `Stream.Foreach` AXI-stream protocol path in [[30 - Memory Accesses]]; Chisel and Scalagen each implement their own stream/file behavior through [[50 - Streams and DRAM]] and [[40 - FIFO LIFO Stream Simulation]]. For this semantic entry, the invariant is that a frame's host allocation and stream endpoint travel together.

Host collections are staged references, not plain arrays. `Tensor1` aliases `spatial.lang.host.Array`, whose `apply` and `update` stage `ArrayApply` and `ArrayUpdate`, and higher-dimensional tensors are row-major structs around host arrays (`src/spatial/lang/host/Array.scala:9-21`, `src/spatial/lang/host/Matrix.scala:7-63`). This matters because `setMem/getMem` consume and return staged host tensors. Host tensor combinators may stage additional host-side IR before the boundary copy occurs.

## Reference Implementation

For synthesis host behavior, [[10 - Cppgen]] and [[60 - Instantiation]] are normative. Cppgen owns host memory allocation, scalar conversion, `setArg/getArg`, `setMem/getMem`, and `c1->run()`. Chisel/Fringe owns the scalar register map, DRAM pointer slots, stream metadata, and AXI4-Lite bridge. For simulation, Scalagen replaces the hardware launch with JVM execution and `emul` memory objects, but the same high-level transfer API remains the user-visible boundary.

## HLS Implications

Rust+HLS should preserve the conceptual ABI rather than the exact Cppgen text: scalar register slots, remote memory pointer slots, bulk memory copies, start/done execution, and result readback. Fixed-point scalar and memory conversion should be made bit-exact rather than using Cppgen's approximate host `double` representation for fractional local expressions. HLS top functions may not use Fringe, but they still need an equivalent manifest for argument order, pointer ownership, and stream ports.

## Open questions

- [[open-questions-semantics#Q-sem-17 - 2026-04-25 HLS host ABI manifest]] tracks what replaces `ArgAPI.scala`/`ArgAPI.hpp` in the Rust+HLS flow.
- [[open-questions-semantics#Q-sem-18 - 2026-04-25 Fixed-point host conversion parity]] tracks whether to match Cppgen's `double` host approximation or enforce Scalagen/emul bit-exact host values.
