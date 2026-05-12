---
type: "research"
decision: "D-02"
angle: 3
---

## Scope

Search scope was `src/spatial`, `fringe/src`, and tests for `prDeqGrp`, `PriorityDeqGroup`, `FIFOBankedPriorityDeq`, `getReadPriorityStreams`, priority inbound stream grouping, and Chisel pressure generation. The only backend/codegen consumers I found are the stream-info tree generator and Chisel forward-pressure generation; FIFO priority dequeue emission consumes the banked priority node but not the group tag directly. The runtime FIFO templates consume the resulting read-port enables and active loopbacks, not `PriorityDeqGroup` metadata.

## Group Creation

The frontend represents logical grouped dequeue as multiple per-FIFO dequeue nodes, not as one grouped IR node. `FIFOPriorityDeq` is the scalar node and `FIFOBankedPriorityDeq` is the unrolled/banked form (`src/spatial/node/FIFO.scala:24`, `src/spatial/node/FIFO.scala:67`). Both `priorityDeq` overloads stage one `FIFOPriorityDeq` per FIFO, then return a `PriorityMux` over the candidate data (`src/spatial/lang/api/PriorityDeqAPI.scala:15`, `src/spatial/lang/api/PriorityDeqAPI.scala:20`, `src/spatial/lang/api/PriorityDeqAPI.scala:46`, `src/spatial/lang/api/PriorityDeqAPI.scala:50`). `roundRobinDeq` follows the same shape after computing rotated priorities (`src/spatial/lang/api/PriorityDeqAPI.scala:71`, `src/spatial/lang/api/PriorityDeqAPI.scala:96`, `src/spatial/lang/api/PriorityDeqAPI.scala:101`).

The group is an integer metadata tag: `PriorityDeqGroup(grp: Int)` exists only to identify which priority dequeues belong together (`src/spatial/metadata/access/AccessData.scala:37`, `src/spatial/metadata/access/AccessData.scala:43`). The current API assigns every lane in a call the hash of the first FIFO's string form (`src/spatial/lang/api/PriorityDeqAPI.scala:17`, `src/spatial/lang/api/PriorityDeqAPI.scala:47`, `src/spatial/lang/api/PriorityDeqAPI.scala:97`). There is an unused `ctx.line` group id and a TODO saying that line-based grouping is probably unsafe (`src/spatial/lang/api/PriorityDeqAPI.scala:11`, `src/spatial/lang/api/PriorityDeqAPI.scala:16`).

## Metadata Flow

Memory unrolling is the bridge from scalar API nodes to backend-visible priority dequeue nodes. It rewrites `FIFOPriorityDeq` to `FIFOBankedPriorityDeq` (`src/spatial/transform/unrolling/MemoryUnrolling.scala:523`, `src/spatial/transform/unrolling/MemoryUnrolling.scala:524`) and copies `prDeqGrp` from the old access symbol to the new symbol when present (`src/spatial/transform/unrolling/MemoryUnrolling.scala:303`, `src/spatial/transform/unrolling/MemoryUnrolling.scala:304`). This means downstream consumers assume the tag lives on the banked read access, not on the FIFO memory or on a separate grouped node.

`getReadStreams` deliberately excludes `FIFOBankedPriorityDeq` from ordinary inbound stream reads (`src/spatial/metadata/control/package.scala:1360`, `src/spatial/metadata/control/package.scala:1362`). Priority reads are instead collected by `getReadPriorityStreams`, which filters local memories whose readers include a banked priority dequeue in the controller, then groups those memories by the first such reader's `prDeqGrp.get` (`src/spatial/metadata/control/package.scala:1367`, `src/spatial/metadata/control/package.scala:1371`, `src/spatial/metadata/control/package.scala:1374`). The `.get` is a hard assumption that every banked priority dequeue has metadata by this point.

## Backend Consumers

Tree generation consumes the grouping for display. It renders each priority group as `prDeq[...]` and merges those grouped listens with ordinary stream listens (`src/spatial/codegen/treegen/TreeGen.scala:159`, `src/spatial/codegen/treegen/TreeGen.scala:161`, `src/spatial/codegen/treegen/TreeGen.scala:165`, `src/spatial/codegen/treegen/TreeGen.scala:167`). This is diagnostic/backend visualization only.

Chisel generation consumes the grouping semantically in forward-pressure. For ordinary inbound FIFOs, forward pressure requires each read stream to be non-empty or not actively being read (`src/spatial/codegen/chiselgen/ChiselGenCommon.scala:250`, `src/spatial/codegen/chiselgen/ChiselGenCommon.scala:252`). For priority groups, it computes `and(groups.map(or(groupFifos)))`: each logical group needs at least one eligible FIFO, not all FIFOs in the group (`src/spatial/codegen/chiselgen/ChiselGenCommon.scala:258`, `src/spatial/codegen/chiselgen/ChiselGenCommon.scala:260`, `src/spatial/codegen/chiselgen/ChiselGenCommon.scala:263`). That is the core same-group assumption: ports in the same group are alternatives for one dequeue decision. Splitting one logical group across ids makes pressure too strong; merging unrelated groups by hash collision makes pressure too weak. Hash collision risk is general hash behavior (unverified), but the code's equality contract is just integer equality.

Back-pressure does not consult priority groups; it is derived from write streams (`src/spatial/codegen/chiselgen/ChiselGenCommon.scala:266`, `src/spatial/codegen/chiselgen/ChiselGenCommon.scala:270`). Controllers still wire both generated pressures into the Chisel block signals (`src/spatial/codegen/chiselgen/ChiselGenController.scala:308`, `src/spatial/codegen/chiselgen/ChiselGenController.scala:309`), and top-level enable gates on forward pressure (`src/spatial/codegen/chiselgen/ChiselGenController.scala:390`).

## FIFO Emission Implications

The FIFO priority-dequeue emitter uses the banked priority node to call `emitRead` with an extra `&& !$fifo.empty` enable guard, then marks the FIFO active when any lane enable is true (`src/spatial/codegen/chiselgen/ChiselGenMem.scala:324`, `src/spatial/codegen/chiselgen/ChiselGenMem.scala:325`, `src/spatial/codegen/chiselgen/ChiselGenMem.scala:326`). `emitRead` also masks read enables with delayed `forwardpressure`, the implicit datapath enable, and `backpressure` via `connectRPort` (`src/spatial/codegen/chiselgen/ChiselGenMem.scala:87`, `src/spatial/codegen/chiselgen/ChiselGenMem.scala:89`). The FIFO primitive advances tail and numel counters from `io.rPort.flatMap(_.en)` (`fringe/src/fringe/templates/memory/MemPrimitives.scala:381`, `fringe/src/fringe/templates/memory/MemPrimitives.scala:384`, `fringe/src/fringe/templates/memory/MemPrimitives.scala:392`, `fringe/src/fringe/templates/memory/MemPrimitives.scala:395`), so the codegen empty guard is what prevents an enabled priority lane from consuming an empty FIFO. Tests document the behavioral hazard: priority dequeue must not dequeue a lane unless its paired payload queue also has data, or it hangs (`test/spatial/tests/feature/dynamic/PriorityDeq.scala:105`).

For D-02, explicit grouped-dequeue IR would need to preserve this consumer contract or update it: unrolling must attach group identity to banked priority accesses, `getReadPriorityStreams` must still recover logical alternatives, and Chisel forward-pressure must remain OR-within-group / AND-across-groups.
