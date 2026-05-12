---
type: spec
status: draft
concept: streaming-semantics
source_files:
  - "src/spatial/node/StreamIn.scala:1-20"
  - "src/spatial/node/StreamOut.scala:1-27"
  - "src/spatial/node/StreamStruct.scala:8-22"
  - "src/spatial/Spatial.scala:144-144"
  - "src/spatial/lang/StreamIn.scala:9-28"
  - "src/spatial/lang/StreamOut.scala:10-29"
  - "src/spatial/lang/Bus.scala:13-87"
  - "src/spatial/transform/streamify/DependencyGraphAnalyzer.scala:17-199"
  - "src/spatial/transform/streamify/HierarchicalToStream.scala:65-838"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenFIFO.scala:1-59"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenLIFO.scala:1-48"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenStream.scala:1-102"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenStream.scala:1-200"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenCommon.scala:249-279"
source_notes:
  - "[[60 - Streams and Blackboxes]]"
  - "[[D0 - Streamify]]"
  - "[[40 - Streams and Blackboxes]]"
  - "[[40 - FIFO LIFO Stream Simulation]]"
  - "[[50 - Controller Emission]]"
  - "[[50 - Streams and DRAM]]"
hls_status: rework
depends_on:
  - "[[60 - Streams and Blackboxes]]"
  - "[[D0 - Streamify]]"
  - "[[40 - Streams and Blackboxes]]"
  - "[[40 - FIFO LIFO Stream Simulation]]"
  - "[[50 - Controller Emission]]"
  - "[[10 - Control]]"
---

# Streaming

## Summary

Streaming semantics combine stream memories, streaming controllers, streamification, and backend queue behavior. [[60 - Streams and Blackboxes]] defines `StreamIn`, `StreamOut`, `StreamStruct`, and controller blackboxes. [[40 - Streams and Blackboxes]] defines the DSL surface and bus descriptors. [[D0 - Streamify]] defines the experimental MetaPipe-to-Stream transform. [[40 - FIFO LIFO Stream Simulation]] is the Scalagen reference for FIFO/LIFO/stream runtime behavior. The key divergence is explicit: Scalagen uses elastic mutable queues with no enqueue back-pressure; Chisel/RTL stream and FIFO logic composes valid/ready and full/empty back-pressure. Rust+HLS must document which side the simulator and synthesis backend match.

## Formal Semantics

`StreamInNew[A](bus)` and `StreamOutNew[A](bus)` are memory allocations with `dims = Seq(I32(1))`, where `bus` carries the wire protocol (`src/spatial/node/StreamIn.scala:7-9`, `src/spatial/node/StreamOut.scala:7-9`). The language types extend both local and remote memory traits, so they can be accessed inside `Accel` while also participating in host/fringe lifetime (`src/spatial/lang/StreamIn.scala:9-28`, `src/spatial/lang/StreamOut.scala:10-29`). The `Bus` hierarchy includes burst command/data/ack, gather/scatter, file, pin, and AXI stream descriptors with widths 64/256/512 (`src/spatial/lang/Bus.scala:13-87`).

A `StreamInRead` is a pre-unroll dequeue and inherits `Effects.Writes(mem)` through `DequeuerLike`; a `StreamOutWrite` is a pre-unroll enqueue and inherits `Effects.Writes(mem)` through `Writer` (`src/spatial/node/StreamIn.scala:11-14`, `src/spatial/node/StreamOut.scala:11-15`, `src/spatial/node/HierarchyAccess.scala:79-148`). Post-unroll `StreamInBankedRead` and `StreamOutBankedWrite` are banked dequeue/enqueue forms with `bank = Nil`, `ofs = Nil`, and lane enable sets (`src/spatial/node/StreamIn.scala:16-20`, `src/spatial/node/StreamOut.scala:22-27`, `src/spatial/node/HierarchyUnrolled.scala:99-139`).

`StreamStruct` provides bundle-of-streams semantics. `SimpleStreamStruct` is transient field grouping; `FieldDeq` reads one field and is a real hardware op, while `FieldEnq` writes one field and declares `Effects.Writes(struct)` (`src/spatial/node/StreamStruct.scala:8-22`). A lower-level contradiction remains: `FieldDeq` has a source TODO saying it should be a mutation, but the effect override is commented out. This synthesis treats field reads as dequeue semantics at the language level, while preserving the current effect-system gap as an open question.

Streaming controllers are scheduled through `Streaming` control metadata. The language `Stream` directive writes `Some(Streaming)` but does not expose `.II`, `.POM`, `.MOP`, or `.NoBind`; it supports name, `stopWhen`, and `haltIfStarved` (`src/spatial/lang/control/Control.scala:35-48`). Effective control schedule is still derived by [[10 - Control]], including schedule collapse for `Single` controllers (`src/spatial/metadata/control/package.scala:193-219`).

Streamify is intended to preserve hierarchical execution while replacing direct dependencies with explicit FIFO tokens. `DependencyGraphAnalyzer` classifies edges between controller parents as `Inner`, `Backward`, `Forward`, or `Initialize` based on LCA/stage distance and source/destination predicates (`src/spatial/transform/streamify/DependencyGraphAnalyzer.scala:17-127`). `HierarchicalToStream` wraps the accelerator body in `Stream`, creates FIFO bundles for dependencies, and splits each inner controller into counter generation, main execution, and release controllers (`src/spatial/transform/streamify/HierarchicalToStream.scala:65-156`, `src/spatial/transform/streamify/HierarchicalToStream.scala:778-823`). For each transformed controller it creates `genToMain`, `genToRelease`, and `mainToRelease` FIFO channels with fixed depths and generated names (`src/spatial/transform/streamify/HierarchicalToStream.scala:82-92`, `src/spatial/transform/streamify/HierarchicalToStream.scala:683-734`). This is the formal equivalence claim: the same logical iterator/time tokens and dependency values are transported through FIFOs rather than through hierarchical memory visibility. The pass is experimental and gated by `--streamify`, so equivalence is a design target rather than a universally applied invariant.

The compiler pipeline reinforces that status: `HierarchicalToStream` is only inserted when `config.enGenStream` is enabled (`src/spatial/Spatial.scala:144-144`). Therefore ordinary Spatial compilation remains hierarchical unless that flag is set, and this entry treats streamification as an optional semantics-preserving transform whose preconditions are those documented in [[D0 - Streamify]].

Scalagen queue semantics are elastic. FIFO and Stream types remap to `scala.collection.mutable.Queue`, LIFO remaps to `mutable.Stack`, and enqueue/push/write operations call `enqueue` or `push` when enabled without checking staged size (`spatial/src/spatial/codegen/scalagen/ScalaGenFIFO.scala:12-44`, `spatial/src/spatial/codegen/scalagen/ScalaGenLIFO.scala:12-44`, `spatial/src/spatial/codegen/scalagen/ScalaGenStream.scala:12-97`). Status readers such as `isFull` compare size against staged size, but they do not constrain the enqueue side. Dequeue on empty returns `invalid(A)` for FIFO/stream and analogous invalid values for LIFO (`spatial/src/spatial/codegen/scalagen/ScalaGenFIFO.scala:33-39`, `spatial/src/spatial/codegen/scalagen/ScalaGenLIFO.scala:31-37`). This is the reference simulator behavior.

RTL stream semantics honor back-pressure. Chisel stream emission drives valid on writes, ready on reads, and composes controller run conditions from stream valid/ready and FIFO empty/full predicates (`spatial/src/spatial/codegen/chiselgen/ChiselGenStream.scala:34-175`, `spatial/src/spatial/codegen/chiselgen/ChiselGenCommon.scala:249-279`). `getForwardPressure` checks stream-in valid, FIFO non-empty or inactive read, merge-buffer non-empty, and grouped priority-deq sources; `getBackPressure` checks stream-out ready, FIFO not full or inactive write, and merge-buffer capacity (`spatial/src/spatial/codegen/chiselgen/ChiselGenCommon.scala:249-279`). This is the source-level evidence for the Scalagen-vs-RTL divergence.

AXI Stream wiring is bus-specific. Chisel `StreamInNew`/`StreamOutNew` registers AXI streams into `axiStreamIns`/`axiStreamOuts`; banked writes and reads copy full AXI fields when the payload type is full AXI, otherwise they route TDATA and set or filter TID/TDEST/TLAST/TUSER defaults (`spatial/src/spatial/codegen/chiselgen/ChiselGenStream.scala:18-32`, `spatial/src/spatial/codegen/chiselgen/ChiselGenStream.scala:34-175`). Current post-main code enforces at most one AXI stream input and one output (`spatial/src/spatial/codegen/chiselgen/ChiselGenStream.scala:181-198`).

File-backed streams are a simulator boundary, not hardware streaming semantics. Scalagen `StreamIn` prompts for a filename, loads non-empty lines that contain digits, parses scalars, vectors, and structs through `bitsFromString`, and queues them before accelerator execution. `StreamOut` accumulates queue contents and dumps them on `AccelScope` exit (`spatial/emul/src/emul/Stream.scala:5-51`, `spatial/src/spatial/codegen/scalagen/ScalaGenStream.scala:23-82`). This behavior is relevant for testbench parity but should not constrain HLS stream port design.

## Reference Implementation

For simulation, [[40 - FIFO LIFO Stream Simulation]] is normative: elastic queues, invalid-on-empty, and stdin-prompted file-backed stream setup. For hardware back-pressure, [[50 - Streams and DRAM]] and the Chisel stream source are normative. [[50 - Controller Emission]] adds one more Scalagen caveat: the outer-stream HACK drains child controllers to exhaustion and does not model feedback-coupled concurrent stream execution (`spatial/src/spatial/codegen/scalagen/ScalaGenController.scala:22-49`).

## HLS Implications

HLS should map streams to `hls::stream<T>` or equivalent valid/ready channels with bounded depth and back-pressure. The Rust simulator has a policy choice: match Scalagen elastic queues for historical tests or assert/back-pressure on full queues for hardware realism. StreamStruct likely needs an explicit bundle-of-streams representation. Streamify's token FIFO protocol could map to HLS dataflow tasks, but the omitted/experimental streamify passes must be resolved before treating it as the canonical lowering.

## Open questions

- [[open-questions-semantics#Q-sem-15 - 2026-04-25 FIFO and LIFO elastic simulator versus back-pressure]] tracks the Scalagen/RTL queue divergence.
- [[open-questions-semantics#Q-sem-16 - 2026-04-25 FieldDeq missing write effect]] tracks the StreamStruct effect contradiction.
