---
type: spec
concept: DRAM Arbiter and AXI
source_files:
  - "fringe/src/fringe/Fringe.scala:79-105"
  - "fringe/src/fringe/FringeBundles.scala:39-89"
  - "fringe/src/fringe/FringeBundles.scala:107-184"
  - "fringe/src/fringe/templates/dramarbiter/DRAMArbiter.scala:13-266"
  - "fringe/src/fringe/templates/dramarbiter/StreamController.scala:9-219"
  - "fringe/src/fringe/templates/dramarbiter/StreamArbiter.scala:10-74"
  - "fringe/src/fringe/templates/dramarbiter/AXIProtocol.scala:9-88"
  - "fringe/src/fringe/templates/dramarbiter/GatherBuffer.scala:9-122"
  - "fringe/src/fringe/templates/dramarbiter/FIFOWidthConvert.scala:7-119"
  - "fringe/src/fringe/templates/axi4/AXI4Parameters.scala:6-33"
  - "fringe/src/fringe/templates/axi4/Parameters.scala:74-131"
  - "fringe/src/fringe/templates/axi4/Bundles.scala:57-169"
  - "fringe/src/fringe/templates/axi4/MAGToAXI4Bridge.scala:9-75"
  - "fringe/src/fringe/templates/axi4/AXI4LiteToRFBridge.scala:5-120"
  - "fringe/src/fringe/targets/zynq/FringeZynq.scala:79-139"
source_notes:
  - "[[fringe-and-targets]]"
hls_status: chisel-specific
hls_reason: "Current implementation is a Chisel AXI/DRAM shell; HLS should preserve stream semantics while using HLS-native interfaces"
depends_on:
  - "[[10 - Fringe Architecture]]"
  - "[[50 - Streams and DRAM]]"
status: draft
---

# DRAM Arbiter and AXI

## Summary

Fringe translates generated accelerator memory streams into target DRAM traffic through a per-channel `DRAMArbiter`, command split/issue modules, and target AXI bridges. The common `Fringe` first asks `channelAssignment.assignments` for each channel's load/store stream IDs, partitions load and store streams, creates one `DRAMArbiter` per channel, wires assigned load/store streams into that arbiter, and wires all gather/scatter streams to every arbiter (`fringe/src/fringe/Fringe.scala:79-105`). The app-level stream types are `LoadStream`, `StoreStream`, `GatherStream`, and `ScatterStream`, grouped in `AppStreams` over `StreamParInfo(w, v, memChannel)` (`fringe/src/fringe/FringeBundles.scala:39-89`).

## Stream surface

The internal DRAM protocol is not AXI yet. A `DRAMCommand` carries `addr`, `size`, `rawAddr`, `isWr`, and a 32-bit tag; `DRAMStream` exposes decoupled command and write-data channels plus flipped read and write response channels (`fringe/src/fringe/FringeBundles.scala:107-152`). `DRAMAddress` interprets addresses using `globals.target.burstSizeBytes`, exposing `burstTag`, `wordOffset`, and `burstAddr` helpers (`fringe/src/fringe/FringeBundles.scala:154-173`). `DRAMTag` splits the tag into `uid`, `cmdSplitLast`, and an 8-bit `streamID`; the comment states that `streamID` must remain at bits `[7:0]` so narrower AXI IDs still see it (`fringe/src/fringe/FringeBundles.scala:175-184`).

`DRAMArbiter` receives load/store/gather/scatter metadata, AXI parameters, and an `isDebugChannel` flag (`fringe/src/fringe/templates/dramarbiter/DRAMArbiter.scala:13-20`). Its IO contains enable/reset, app streams, one `DRAMStream(EXTERNAL_W, EXTERNAL_V)`, debug signals, and AXI probe bundles (`fringe/src/fringe/templates/dramarbiter/DRAMArbiter.scala:25-36`). When there are streams, it asserts the stream tag width fits in `DRAMTag.streamID`, creates one controller per stream, fan-ins controllers in load/gather/store/scatter order with `StreamArbiter`, runs `AXICmdSplit`, then runs `AXICmdIssue` before driving `io.dram` (`fringe/src/fringe/templates/dramarbiter/DRAMArbiter.scala:53-99`). The final command and write-data valids are gated by arbiter enable (`fringe/src/fringe/templates/dramarbiter/DRAMArbiter.scala:97-101`).

## Controllers and arbitration

`StreamController` converts app byte counts to DRAM burst counts by shifting by `log2Ceil(target.burstSizeBytes)` (`fringe/src/fringe/templates/dramarbiter/StreamController.scala:9-23`). Dense loads FIFO commands, mark them as reads, and width-convert DRAM read responses back to app lane width (`fringe/src/fringe/templates/dramarbiter/StreamController.scala:25-60`). Dense stores FIFO commands, mark them as writes, width-convert app write lanes to external DRAM lanes, reverse strobes, and FIFO write responses back to the app (`fringe/src/fringe/templates/dramarbiter/StreamController.scala:62-109`). Gather splits sparse vector addresses into lane FIFOs, uses `GatherBuffer` to coalesce by burst tag, puts the coalesced UID into `DRAMTag.uid`, and emits one-beat read commands (`fringe/src/fringe/templates/dramarbiter/StreamController.scala:111-156`). Scatter stores sparse lanes one burst at a time, computes byte strobes from word offsets, replicates a selected lane's data across the external beat, and FIFOs write responses (`fringe/src/fringe/templates/dramarbiter/StreamController.scala:158-219`).

`GatherAddressSelector` prioritizes unissued lanes to avoid starvation and marks every lane with the same burst tag as issued together (`fringe/src/fringe/templates/dramarbiter/GatherBuffer.scala:9-47`). `GatherBuffer` stores per-lane metadata, suppresses duplicate issue when an outstanding bank already matches the selected burst, scatters returning burst data to per-lane words, and asserts app data valid only when all lanes are done (`fringe/src/fringe/templates/dramarbiter/GatherBuffer.scala:49-122`). `FIFOWidthConvert` handles narrow-to-wide, wide-to-narrow, and same-width conversion, asserting multiplicity constraints and warning for sub-byte strobe cases (`fringe/src/fringe/templates/dramarbiter/FIFOWidthConvert.scala:7-119`).

`StreamArbiter` priority-encodes valid commands but keeps servicing the retimed selected stream if it remains valid, so a request is not interleaved with another stream mid-command (`fringe/src/fringe/templates/dramarbiter/StreamArbiter.scala:10-22`). It writes the selected stream index into the command tag, uses pipelined muxes for command and write-data paths, counts write-data elements until the command size is satisfied, and routes read/write responses back by tag stream ID (`fringe/src/fringe/templates/dramarbiter/StreamArbiter.scala:24-73`).

## AXI command formation

`AXICmdSplit` splits commands larger than `target.maxBurstsPerCmd`, advances the address by burst bytes, writes `cmdSplitLast` only on the final split command, and only forwards a write response to the app for that final split response (`fringe/src/fringe/templates/dramarbiter/AXIProtocol.scala:9-48`). `AXICmdIssue` tracks write data beats for the current command, asserts `wlast` on the final beat, issues a write command only once, and keeps the input command queued until its write data is complete; read commands complete on the command handshake (`fringe/src/fringe/templates/dramarbiter/AXIProtocol.scala:50-88`).

AXI constants are centralized in `AXI4Parameters` (`lenBits=8`, `sizeBits=3`, `burstBits=2`, cache/prot/qos/resp widths and enum values), but that file uses legacy `Chisel._` imports (`fringe/src/fringe/templates/axi4/AXI4Parameters.scala:6-33`). `AXI4BundleParameters` validates address, data, and ID widths and imports the constant widths; `AXI4StreamParameters.asDummyAXI4Bundle` creates fake address bits so AXI streams can reuse the generic bundle base (`fringe/src/fringe/templates/axi4/Parameters.scala:74-131`). `AXI4Bundle` uses decoupled `Irrevocable` channels, while `AXI4Inlined` flattens the same interface into uppercase Vivado-recognized signal names (`fringe/src/fringe/templates/axi4/Bundles.scala:57-123`).

`MAGToAXI4Bridge` asserts the AXI data width equals `EXTERNAL_W * EXTERNAL_V`, maps DRAM command tags to AXI IDs, sets `ARSIZE/AWSIZE` to `6` for 64-byte beats, uses INCR burst mode, chooses cache value `15` for ZCU and `3` otherwise, reverses write data/strobes and read data word order, and maps AXI R/B IDs back to DRAM response tags (`fringe/src/fringe/templates/axi4/MAGToAXI4Bridge.scala:9-75`). `FringeZynq` inserts one such bridge per channel (`fringe/src/fringe/targets/zynq/FringeZynq.scala:134-139`). Host scalar control is separate: `AXI4LiteToRFBridge` and its ZCU/KCU variants wrap AXI-Lite black boxes and expose register-file `raddr`, `wen`, `waddr`, `wdata`, and `rdata` to `FringeZynq` (`fringe/src/fringe/templates/axi4/AXI4LiteToRFBridge.scala:5-120`, `fringe/src/fringe/targets/zynq/FringeZynq.scala:79-114`).

## HLS notes

The HLS port should preserve the app stream semantics, burst sizing, per-stream response routing, command splitting, final-write-response behavior, sparse gather coalescing, and scatter strobe semantics. The Chisel modules, `Decoupled` plumbing, Vivado signal-name flattening, and AXI-Lite black boxes are backend-specific and should become HLS top-function ports and host ABI code rather than literal Chisel structures.

## Open questions

- [[open-questions-fringe-targets#Q-ft-02 - 2026-04-25 magPipelineDepth consumer|Q-ft-02]]
- [[open-questions-fringe-targets#Q-ft-09 - 2026-04-25 DRAM debug-register cap|Q-ft-09]]
