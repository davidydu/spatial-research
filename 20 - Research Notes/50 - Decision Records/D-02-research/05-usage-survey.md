---
type: "research"
decision: "D-02"
angle: 5
---

# Usage Survey: Priority And Round-Robin Dequeue

## Scope And Corpus

I searched the Spatial source tree for `priorityDeq`, `roundRobinDeq`, `FIFOPriorityDeq`, `FIFOBankedPriorityDeq`, priority-dequeue metadata, and adjacent FIFO arbitration patterns. Direct application/test usage is concentrated in `test/spatial/tests/feature/dynamic`: `PriorityDeq.scala`, `StreamPipeFlush.scala`, and `PseudoCoprocTest.scala`. I did not find direct calls in `apps/src` during this pass. Library/codegen usage is centralized in the API, metadata, unrolling, and Chisel/tree codegen paths.

The corpus exercises both static-sized streams and dynamic `Foreach(*)` streams. The tests mostly assert liveness and coarse correctness, not exact output order: basic priority tests verify each packet appears either once or three times, depending on producer behavior (`test/spatial/tests/feature/dynamic/PriorityDeq.scala:82`); multi-priority tests explicitly accept "Just want the app to not hang" (`test/spatial/tests/feature/dynamic/PriorityDeq.scala:197`).

## API Semantics And Grouping

The varargs API stages one `FIFOPriorityDeq` per FIFO and enables FIFO `i` only when all earlier FIFOs are empty; the output `PriorityMux` is keyed by each FIFO's non-empty status (`src/spatial/lang/api/PriorityDeqAPI.scala:10`, `src/spatial/lang/api/PriorityDeqAPI.scala:15`, `src/spatial/lang/api/PriorityDeqAPI.scala:20`). This is fixed priority, not fairness. The conditional-list API takes parallel `List[FIFO[T]]` and `List[Bit]`, asserts equal sizes, computes whether earlier eligible FIFOs have already won, and muxes only `!empty && shouldDequeue` choices (`src/spatial/lang/api/PriorityDeqAPI.scala:25`, `src/spatial/lang/api/PriorityDeqAPI.scala:29`, `src/spatial/lang/api/PriorityDeqAPI.scala:41`, `src/spatial/lang/api/PriorityDeqAPI.scala:50`).

Existing grouping is implicit. Each staged priority dequeue stores `prDeqGrp` as `fifo.head.toString.hashCode()` or `fifos.head.toString.hashCode`, and the metadata type exists specifically "so we can figure out which PriorityDeqs are grouped together" (`src/spatial/lang/api/PriorityDeqAPI.scala:17`, `src/spatial/lang/api/PriorityDeqAPI.scala:47`, `src/spatial/lang/api/PriorityDeqAPI.scala:97`, `src/spatial/metadata/access/AccessData.scala:37`). During unrolling, `FIFOPriorityDeq` becomes `FIFOBankedPriorityDeq`, and the group metadata is copied to the new symbol (`src/spatial/transform/unrolling/MemoryUnrolling.scala:303`, `src/spatial/transform/unrolling/MemoryUnrolling.scala:524`). Control metadata then excludes banked priority deqs from ordinary read streams and groups inbound FIFOs by `prDeqGrp` (`src/spatial/metadata/control/package.scala:1360`, `src/spatial/metadata/control/package.scala:1374`).

## Direct Usage Patterns

Varargs usage covers simple fixed-priority worker queues, termination sentinels, and credit returns. `PriorityDeq` uses three worker FIFOs in the static case and adds a `doneQueue` sentinel in the dynamic case (`test/spatial/tests/feature/dynamic/PriorityDeq.scala:43`, `test/spatial/tests/feature/dynamic/PriorityDeq.scala:70`). `StreamPipeFlush` uses `priorityDeq(inFIFO, flushFIFO)` so real input beats the flush sentinel (`test/spatial/tests/feature/dynamic/StreamPipeFlush.scala:29`, `test/spatial/tests/feature/dynamic/StreamPipeFlush.scala:90`). `PseudoCoprocTest` uses varargs across credit FIFOs plus an initializer FIFO (`test/spatial/tests/feature/dynamic/PseudoCoprocTest.scala:65`).

Conditional-list usage gates ID queues on side conditions from payload or credit state. The multi-priority tests call `priorityDeq(List(...), List(!payload.isEmpty, ...))` because the ID FIFO must not advance unless the matching payload FIFO also has data (`test/spatial/tests/feature/dynamic/PriorityDeq.scala:105`, `test/spatial/tests/feature/dynamic/PriorityDeq.scala:144`, `test/spatial/tests/feature/dynamic/PriorityDeq.scala:184`). `PseudoCoprocTest` similarly builds `creditEnables = creditRegs map {_ > 0}` before selecting the next task (`test/spatial/tests/feature/dynamic/PseudoCoprocTest.scala:60`, `test/spatial/tests/feature/dynamic/PseudoCoprocTest.scala:61`).

## Nesting, Round Robin, And Adjacent Patterns

The main nested/adjacent case is `PriorityDeq2In1`: one varargs priority dequeue selects a token FIFO, and the next line uses conditional-list priority dequeue over worklists gated by token counters (`test/spatial/tests/feature/dynamic/PriorityDeq.scala:242`, `test/spatial/tests/feature/dynamic/PriorityDeq.scala:243`). This matters for D-02 because two grouped-dequeue operations can share a stream body while representing different FIFO groups.

`roundRobinDeq` uses the same `FIFOPriorityDeq` backend but computes a rotating priority from `(iter + idx) % fifos.size`; lower numeric priority wins (`src/spatial/lang/api/PriorityDeqAPI.scala:55`, `src/spatial/lang/api/PriorityDeqAPI.scala:65`, `src/spatial/lang/api/PriorityDeqAPI.scala:71`, `src/spatial/lang/api/PriorityDeqAPI.scala:77`). The only direct test passes a dynamic iteration expression `group * numFifos + fnum` over eight FIFOs and asserts dequeued values stay in the current group, which tests no cross-group leakage rather than exact fair order (`test/spatial/tests/feature/dynamic/PriorityDeq.scala:367`, `test/spatial/tests/feature/dynamic/PriorityDeq.scala:387`, `test/spatial/tests/feature/dynamic/PriorityDeq.scala:388`, `test/spatial/tests/feature/dynamic/PriorityDeq.scala:403`).

One adjacent non-API pattern manually interleaves three worker histories with explicit `if`/`else if` priority and `isEmpty` checks inside an FSM (`test/spatial/tests/feature/dynamic/DummyWorkload.scala:186`, `test/spatial/tests/feature/dynamic/DummyWorkload.scala:199`). It does not use grouped priority-dequeue IR, but it reflects the same user-level need: one consumer arbitrates among related FIFOs.

## Decision Signal

The usage surface is small but semantically rich: fixed priority, conditional dequeue tied to side FIFOs, dynamic stream termination, adjacent grouped arbiters, and rotating fairness all depend on a set of per-FIFO dequeue nodes behaving as one logical arbitration event. The implementation already treats these as special in codegen: banked priority dequeue reads add an `&& !fifo.empty` hack at Chisel emission (`src/spatial/codegen/chiselgen/ChiselGenMem.scala:324`, `src/spatial/codegen/chiselgen/ChiselGenMem.scala:325`), and forward pressure ORs each priority group so a stream can proceed when any member FIFO is ready (`src/spatial/codegen/chiselgen/ChiselGenCommon.scala:258`, `src/spatial/codegen/chiselgen/ChiselGenCommon.scala:260`).

For D-02, this points toward preserving source compatibility with current hash-based grouping while introducing an explicit grouped-dequeue IR or explicit group identity internally. The test corpus does not suggest broad app dependence on the hash itself; it suggests dependence on grouped behavior, stable side-condition semantics, and distinct logical groups when multiple arbiters appear in one stream body.
