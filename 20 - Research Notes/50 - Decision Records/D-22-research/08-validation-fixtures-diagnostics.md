---
type: "research"
decision: "D-22"
angle: 8
topic: "validation-fixtures-diagnostics"
---

# D-22 Angle 8: Validation Fixtures and Diagnostics

## Existing Evidence To Reuse

D-22 needs fixtures that make queue policy observable, because current ScalaGen evidence mostly protects values. The source baseline is elastic: FIFO and StreamIn/StreamOut remap to `mutable.Queue`, LIFO remaps to `mutable.Stack`, status readers inspect size, and enabled writes still enqueue or push without capacity checks (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/scalagen/ScalaGenFIFO.scala:12-44`, `/Users/david/Documents/David_code/spatial/src/spatial/codegen/scalagen/ScalaGenLIFO.scala:12-44`, `/Users/david/Documents/David_code/spatial/src/spatial/codegen/scalagen/ScalaGenStream.scala:12-97`; [[40 - FIFO LIFO Stream Simulation]]). The current corpus has useful seeds: `FIFOBanking2` overfills `FIFO[Int](5)` with 32 values but asserts only true (`/Users/david/Documents/David_code/spatial/test/spatial/tests/feature/banking/FIFOBanking.scala:33-46`); `FSMFIFOStack` checks `isFull`, `isEmpty`, almost predicates, FIFO last-out, and LIFO last-out (`/Users/david/Documents/David_code/spatial/test/spatial/tests/feature/control/fsm/FSMFIFOStack.scala:21-128`); `MemCopyLIFO` proves reverse ordering through a LIFO load/store (`/Users/david/Documents/David_code/spatial/test/spatial/tests/feature/transfers/MemCopyLIFO.scala:15-41`).

## Core Queue Fixtures

Add small deterministic fixtures for overflow, underflow, full/empty/valid, depth one, and multi-lane atomicity. Each fixture should run in `compat_scalagen_elastic` and `bounded_backpressure`. Overflow should intentionally push `depth + 1` into FIFO and LIFO; elastic mode records `overflow_observed=false`, `max_occupancy=depth+1`, while bounded mode records either `stall_on_full` or `overflow_error`. Underflow should deq/pop/read an empty structure; elastic mode expects `invalid` from FIFO/stream/LIFO reads (`ScalaGenFIFO.scala:33-39`, `ScalaGenLIFO.scala:31-37`, `ScalaGenStream.scala:84-90`), while bounded mode expects a stall or labelled underflow. Depth-one should cover same-cycle enqueue/dequeue and push/pop to force the D-15 tick rule: pre-state, post-state, or snapshot/commit cannot be left implicit. LIFO needs a separate fixture with pushes `0,1,2`, pops `2,1,0`, and overflow/underflow diagnostics that never relabel stack behavior as FIFO behavior.

## Flow, Rate, And Deadlock Fixtures

Producer-faster and consumer-faster cases should be separate. A faster producer can be derived from `FIFOBanking2` or `StreamPipeFlush` by giving the producer II 1, consumer II 4, and depth 2; expected bounded output is a full-stall trace, not elastic growth. A faster consumer can be minimized from `ContinualStreaming`, whose producer is explicitly slow and causes receive-side starves (`/Users/david/Documents/David_code/spatial/test/spatial/tests/compiler/ContinualStreaming.scala:18-42`); expected bounded output is empty-stall cycles and no invalid data use. Add a two-node cyclic dataflow fixture: process A waits to read B before writing A, process B waits to read A before writing B. Bounded mode should terminate with `deadlock`, listing both wait reasons; elastic mode should be blocked from claiming liveness. This is also the [[D-20]] boundary: delay lines advance only on the same accepted controller step as queue transfers, and [[D-21]] requires the trace to name its `ii_source`.

## Stream Host Protocol Fixtures

Stream fixtures need host protocol evidence, not only queue behavior. ScalaGen `StreamIn` prompts for a filename, reads lines containing digits, parses them through `bitsFromString`, and enqueues them; `StreamOut` prompts for an output file and dumps queued elements on exit (`/Users/david/Documents/David_code/spatial/emul/src/emul/Stream.scala:5-51`; `/Users/david/Documents/David_code/spatial/src/spatial/codegen/scalagen/ScalaGenStream.scala:23-57`). The Rust/HLS fixtures should replace stdin prompts with explicit host manifests while preserving parse/serialize goldens. Use `FrameLoadTest`, `FrameStoreTest`, and `FrameLoadStoreTest` as seeds for AxiStream frame IO and FIFO depth smaller than frame length (`/Users/david/Documents/David_code/spatial/test/spatial/tests/feature/transfers/LoadStoreUnitTests.scala:8-72`). Add ready/valid cases for host stalls: input unavailable, output not ready, TLAST observed, and sideband mismatch for AxiStream packets.

## Diagnostic Contract And Labels

Every result should emit a compact machine-readable record: `queue_policy`, `scheduler_policy`, `depth`, `occupancy_before`, `occupancy_after`, `max_occupancy`, `event` (`enq`, `deq`, `push`, `pop`, `read`, `write`), `blocked_reason`, `cycle`, `controller_path`, `memory_name`, `producer`, `consumer`, `ii_source`, and `policy_mismatch`. Chisel pressure already distinguishes stream valid/ready and FIFO empty/full (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/chiselgen/ChiselGenCommon.scala:247-278`), and Fringe FIFO/LIFO primitives expose finite empty/full/numel state (`/Users/david/Documents/David_code/spatial/fringe/src/fringe/templates/memory/MemPrimitives.scala:380-541`). Label mismatches explicitly: `elastic_overflow_hidden`, `invalid_on_empty_vs_stall`, `fifo_depth_requires_backpressure`, `lifo_not_hls_stream`, `host_prompt_vs_manifest`, and `accepted_ii_mismatch`. Those labels let [[D-15]], [[D-20]], and [[D-21]] consume the same trace without mistaking ScalaGen compatibility for HLS liveness evidence.
