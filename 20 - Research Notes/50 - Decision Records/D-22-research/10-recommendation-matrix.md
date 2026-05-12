---
type: "research"
decision: "D-22"
angle: 10
topic: "recommendation-matrix"
---

# D-22 Recommendation Matrix

## Evidence Baseline

D-22 is not just choosing queue data structures; it is choosing what a simulator result is allowed to claim. ScalaGen lowers FIFO and StreamIn/StreamOut to `mutable.Queue` and LIFO to `mutable.Stack`; full is only a size predicate, while enabled enqueue, push, and stream write always mutate the host collection (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/scalagen/ScalaGenFIFO.scala:12-44`; `/Users/david/Documents/David_code/spatial/src/spatial/codegen/scalagen/ScalaGenLIFO.scala:12-44`; `/Users/david/Documents/David_code/spatial/src/spatial/codegen/scalagen/ScalaGenStream.scala:12-97`). Empty reads return `invalid`, not stalls (`ScalaGenFIFO.scala:33-39`; `ScalaGenLIFO.scala:31-37`; `ScalaGenStream.scala:84-90`). [[40 - FIFO LIFO Stream Simulation]] calls this "silent elastic enqueue" and warns that overflow can pass Scala simulation while failing synthesized hardware (`10 - Spec/50 - Code Generation/20 - Scalagen/40 - FIFO LIFO Stream Simulation.md:21-23`, `:140-149`).

RTL points the other way. Chisel forward pressure checks stream valid or FIFO non-empty, back pressure checks stream ready or FIFO non-full, and both are delayed by the controller II (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/chiselgen/ChiselGenCommon.scala:249-278`). Stream writes drive `valid` under `backpressure`, and stream reads drive `ready` (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/chiselgen/ChiselGenStream.scala:34-43`, `:139-167`). Fringe FIFO/LIFO templates use finite counters and expose `empty`, `full`, `almost*`, and `numel` (`/Users/david/Documents/David_code/spatial/fringe/src/fringe/templates/memory/MemPrimitives.scala:391-442`, `:463-541`).

## Decision Matrix

| Option | Correctness and parity | RTL/HLS fidelity and deadlock | Cost, tests, timing, overlaps | Disposition |
|---|---|---|---|---|
| Elastic-only | Best Scalagen parity and lowest migration cost. It preserves advisory full, invalid-on-empty, and existing value goldens (`ScalaGenFIFO.scala:19-44`; `ScalaGenStream.scala:84-97`). | Poor hardware truth: overflow is growth, underflow is a value, and deadlock is invisible. | Existing tests mostly validate final values, and some are elastic or ambiguous, such as overfilling a depth-5 FIFO with 32 values (`20 - Research Notes/50 - Decision Records/D-22-research/03-tests-app-usage.md:7-19`). It cannot satisfy D-15 bounded stalls or D-20 cycle gating. | Keep only as `compat_scalagen_elastic`. |
| Bounded-only | More correct for finite hardware queues, but it intentionally breaks ScalaGen behavior and may reclassify old value tests as stalls or overflow errors. | Strong liveness visibility if it defines capacity, same-cycle arbitration, timeout, and blocked reasons. | High cost: it needs new fixtures for overflow, underflow, same-cycle `isFull`/enqueue, stream ready/valid, and LIFO behavior (`03-tests-app-usage.md:17-19`). It also depends on D-15 tick order and D-21 II provenance. | Reject as the universal default. |
| Dual-mode elastic reference plus bounded/cycle/HLS mode | Correctly separates "what ScalaGen did" from "what HLS/RTL permits." | Bounded mode can expose overflow, starvation, and deadlock without corrupting compatibility results. | Fits D-15, which reserves bounded dataflow until D-22 (`20 - Research Notes/50 - Decision Records/D-15.md:44-56`); D-20, which requires queue policy and II source for cycle delay lines (`20 - Research Notes/50 - Decision Records/D-20.md:52-65`); and D-21, which keeps selected, requested, and accepted II separate (`20 - Research Notes/50 - Decision Records/D-21.md:46-70`). | Recommend. |
| HLS-native/report-only | Post-tool reports are the best accepted-II and latency authority. | Too late for source-level queue bugs; reports do not explain which enqueue, dequeue, or channel first blocked. | D-08 rejects single-source extremes: reports are authoritative but too slow for broad DSE, while simulation is validation and triage (`20 - Research Notes/50 - Decision Records/D-08.md:31-39`, `:61-67`). | Use as timing authority, not simulator semantics. |

## Recommended Contract

Adopt **dual-mode semantics**. `compat_scalagen_elastic` is the reference lane for legacy functional comparison: source/IR-order execution, Queue/Stack behavior, advisory full, invalid-on-empty, no cycle claim, no overflow failure, and no deadlock claim.

Add `bounded_hls_cycle` as the HLS-facing validation lane. It uses finite depths from staged size or explicit stream policy; full and empty cause stall or assertion, never silent growth or invalid values; same-cycle multi-lane enqueue/dequeue uses a deterministic snapshot/commit rule; every blocked step records channel, producer, consumer, occupancy, high-water mark, II source, and timeout/deadlock status. Delay lines advance only on the same accepted controller step as queues, matching Chisel `DL` gating by backpressure and sometimes forward pressure (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/chiselgen/ChiselGenCommon.scala:288-293`). Before HLS reports, timing claims are labelled estimates; after reports, DSE and summaries prefer accepted II and report latency under D-21 and D-08.

## Rejected Alternatives

Reject elastic-only as the D-22 answer: it is a compatibility oracle, not bounded hardware semantics. Reject bounded-only as the default: it would break Scalagen parity before the test suite has enough explicit back-pressure fixtures. Reject HLS-native/report-only: it is the right post-tool timing evidence, but it misses pre-tool liveness debugging. Reject any unlabelled mixed mode; a result must say `queue_policy`, `scheduler_policy`, `delayline_policy`, `ii_source`, and whether deadlock evidence is reference, diagnostic, or report-backed.
