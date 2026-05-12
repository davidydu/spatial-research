---
type: "research"
decision: "D-22"
angle: 4
topic: "hls-stream-fifo-mapping"
---

# D-22 Angle 4: HLS Mapping and Tool Semantics

## 1. Spatial Contract To Preserve

Spatial exposes FIFO and LIFO as depth-parameterized local memories with status readers for empty, full, almost-empty, almost-full, and numel (`src/spatial/node/FIFO.scala:7-52`; `src/spatial/node/LIFO.scala:7-21`). StreamIn and StreamOut are bus-backed memories; Spatial also exposes FileBus/FileEOFBus and AxiStream64/256/512 bus types (`src/spatial/lang/Bus.scala:28-68`). ScalaGen then makes the compatibility contract intentionally elastic: FIFO is a `mutable.Queue`, LIFO is a `mutable.Stack`, and StreamIn/StreamOut are queues (`src/spatial/codegen/scalagen/ScalaGenFIFO.scala:12-44`; `ScalaGenLIFO.scala:12-44`; `ScalaGenStream.scala:12-97`; [[40 - FIFO LIFO Stream Simulation]]). Full predicates compare against staged size, but enabled enqueue, push, and stream write do not test full. Empty reads do not stall; FIFO, LIFO, and stream reads return `invalid` when empty.

The hardware-facing local evidence points the other way. Chisel forward pressure checks stream valid or FIFO not-empty; back-pressure checks stream ready or FIFO not-full (`src/spatial/codegen/chiselgen/ChiselGenCommon.scala:247-278`). Fringe FIFO and LIFO primitives allocate finite memories/counters and expose empty/full/almost/numel (`fringe/src/fringe/templates/memory/MemPrimitives.scala:380-442`, `:447-541`). D-15 and D-20 should therefore treat bounded queue semantics as a prerequisite for honest peer/barrier and cycle-delay simulation, not as a detail inside codegen.

## 2. hls::stream And Dataflow Channels

The closest HLS-facing mapping for internal FIFO and stream edges is an `hls::stream<T>`-like channel in a dataflow region (unverified). This matches the conceptual ready/valid model: producer and consumer communicate through a finite-depth channel, and the tool can insert scheduling stalls around reads and writes (unverified). It also matches the Chisel evidence better than ScalaGen: full and empty become liveness conditions rather than advisory predicates.

This option must be labelled `hls_bounded_stream`, not ScalaGen-compatible. A ScalaGen overflow silently grows the queue; a bounded HLS stream write on full must either stall or fail an assertion. A ScalaGen empty read returns `invalid`; HLS-facing read should stall, block, or report underflow (unverified). Depth must come from `FIFONew`/`LIFONew` for local memories, and from an explicit stream policy or host manifest for StreamIn/StreamOut. Deadlock is a real result: if every process is blocked on empty/full, the simulator should report first blocked channel, depth, occupancy, producer, consumer, and cycle bound.

## 3. Bounded Array Or Ring Buffer

A bounded array/ring-buffer lowering is the deterministic fallback for local FIFOs when dataflow streams are unavailable or too tool-specific. It can model `head`, `tail`, `count`, full, empty, almost predicates, vector enqueue/dequeue widths, and high-water marks in ordinary C/C++ before adding HLS pragmas. HLS tools can often synthesize static arrays into RAM/register storage with partitioning or resource pragmas (unverified).

The trap is that a ring buffer alone is not back-pressure. In sequential C, a full write can be guarded, asserted, dropped, or overwritten; only the first two are acceptable for HLS-bounded semantics. Similarly, an empty read cannot produce ScalaGen `invalid` and still claim bounded hardware meaning. This mapping is best for explicit local FIFO state, debug traces, and unsupported dataflow contexts. It should emit or simulate stall tokens when composed with D-15 peer/barrier execution, and it should feed D-21 with any II changes caused by stalls or array access conflicts.

## 4. AXI Streams And External IO

AXI streams should be reserved for external StreamIn/StreamOut buses that already opt into Spatial AxiStream types. Spatial defines AxiStream64/256/512 structs and bus cases, including TDATA, TSTRB, TKEEP, TLAST, TID, TDEST, and TUSER fields (`src/spatial/lang/Bus.scala:28-50`). ChiselGen maps those buses to `accelUnit.io.axiStreamsIn/Out`, fills default sideband fields when the user passes only payload data, and currently errors above one AXI stream input or output (`src/spatial/codegen/chiselgen/ChiselGenStream.scala:17-186`). Fringe generic streams are Decoupled ready/valid endpoints with data, tag, and last fields (`fringe/src/fringe/FringeBundles.scala:186-207`).

For HLS, AXI stream pragmas/interfaces are endpoint mappings, not a replacement for local FIFOs (unverified). FileBus/FileEOFBus remain simulator/testbench or host-file policies, not synthesized channel semantics.

## 5. LIFO Fallback And Recommendation

LIFO is the main rejection case. Spatial exposes LIFO as first-class stack state, and Fringe has a bounded LIFO primitive, but ordinary HLS stream channels are FIFO ordered, not stack ordered (unverified). Therefore HLS v1 should reject LIFO-as-stream lowering. Accept either an explicit bounded stack array implementation with overflow/underflow diagnostics, or a labelled `compat_scalagen_elastic_stack` fallback only in ScalaGen compatibility mode.

Recommendation: D-22 should define two explicit policies. `compat_scalagen_elastic` keeps Queue/Stack behavior, advisory full, invalid-on-empty, and no deadlock. `hls_bounded` uses finite depths, full/empty as stall or assertion conditions, no invalid-on-empty reads, no growth-on-full writes, occupancy tracing, and deadlock timeout diagnostics. HLS claims should remain tagged unverified until local fixtures prove tool behavior.
