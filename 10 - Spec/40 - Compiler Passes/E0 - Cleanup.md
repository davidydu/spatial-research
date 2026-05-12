---
type: spec
concept: cleanup
source_files:
  - "src/spatial/transform/TransientCleanup.scala:18-196"
  - "src/spatial/transform/MemoryCleanupTransformer.scala:10-25"
  - "src/spatial/transform/RegReadCSE.scala:9-48"
  - "src/spatial/transform/FIFOAccessFusion.scala:15-96"
  - "src/spatial/transform/MetadataStripper.scala:6-32"
  - "src/spatial/transform/UnitIterationElimination.scala:12-58"
  - "src/spatial/transform/ForeachToUnitpipeTransformer.scala:10-34"
  - "src/spatial/transform/UnitPipeToForeachTransformer.scala:11-39"
  - "src/spatial/transform/DuplicateRetimeStripper.scala:9-36"
  - "src/spatial/traversal/UseAnalyzer.scala:11-153"
  - "src/spatial/Spatial.scala:107-122"
  - "src/spatial/Spatial.scala:138-162"
  - "src/spatial/Spatial.scala:190-218"
source_notes:
  - "[[pass-pipeline]]"
hls_status: clean
depends_on:
  - "[[60 - Use and Access Analysis]]"
  - "[[C0 - Retiming]]"
status: draft
---

# Cleanup

## Summary

Cleanup in Spatial is not one pass; it is a wave of small canonicalizers that remove unused IR, move or duplicate transient values into legal blocks, deduplicate register reads, strip stale metadata, fuse FIFO enqueues, and collapse redundant retime gates (`src/spatial/Spatial.scala:107-122`, `src/spatial/Spatial.scala:138-162`). The canonical chain uses `RegReadCSE` before each DCE wave, defines `DCE = Seq(useAnalyzer, transientCleanup, printer, transformerChecks)`, runs `memoryCleanup` after hardware rewrites, and embeds `MetadataStripper` in FIFO initialization and banking cleanup contexts (`src/spatial/Spatial.scala:138-162`, `src/spatial/Spatial.scala:190-218`). `DuplicateRetimeStripper` is also part of the cleanup wave even though [[C0 - Retiming|retiming]] covers it: every `retimeAnalysisPasses` sequence runs printer, stripper, printer, and `RetimingAnalyzer` (`src/spatial/Spatial.scala:140`).

## Pass list and roles

`UseAnalyzer` feeds DCE by clearing and rebuilding `Users`, marking unused registers as `isUnusedMemory`, marking breakWhen values as breakers, and propagating pending uses for transient symbols and counters (`src/spatial/traversal/UseAnalyzer.scala:14-27`, `src/spatial/traversal/UseAnalyzer.scala:43-68`, `src/spatial/traversal/UseAnalyzer.scala:100-153`). `TransientCleanup` consumes that use metadata: it duplicates transient primitives per consumer block when users span blocks or leave the current block, removes unused transient primitives in hardware, drops unused counters/counterchains with no owner, and removes unused register writes/register allocations (`src/spatial/transform/TransientCleanup.scala:18-40`, `src/spatial/transform/TransientCleanup.scala:53-60`, `src/spatial/transform/TransientCleanup.scala:62-132`). `MemoryCleanupTransformer` is narrower: after unrolling and rewrites, it drops non-DRAM memory allocations that are not `keepUnused`, are in hardware, and have no readers and no writers (`src/spatial/transform/MemoryCleanupTransformer.scala:10-25`).

`RegReadCSE` is a local CSE pass for `RegRead` inside inner-controller blocks. It creates a transformed `RegRead(f(reg))`, computes effects, then reuses a cached symbol only if the cache entry is still in scope and has identical effects, which protects against intermediate writes/anti-dependencies (`src/spatial/transform/RegReadCSE.scala:9-35`). `FIFOAccessFusion` batches consecutive `FIFOEnq` and `FIFOVecEnq` operations by FIFO and identical enable set, then flushes them as one `FIFOVecEnq` when there is more than one element, as a scalar `FIFOEnq` for one element, at `RetimeGate`, or at block end (`src/spatial/transform/FIFOAccessFusion.scala:15-63`, `src/spatial/transform/FIFOAccessFusion.scala:65-85`). `MetadataStripper` is a generic `Traversal`: `Stripper[M]` clears one metadata class on each symbol, and `MetadataStripper(state, strippers*)` applies all requested strippers during visit (`src/spatial/transform/MetadataStripper.scala:6-32`).

## Algorithms

The transient duplication algorithm is delayed and per-block. For each transient primitive requiring move or duplication, `TransientCleanup` groups non-prior users by `Blk`, records a delayed mirror for each target block, adds transient-read memories to the target control's `transientReadMems`, and installs substitution rules keyed by `(use, block)` (`src/spatial/transform/TransientCleanup.scala:29-40`, `src/spatial/transform/TransientCleanup.scala:46-83`). When a later statement is updated in the matching block, `updateWithContext` activates those delayed substitutions, mirrors the producer once for that block through `completedMirrors`, and otherwise updates normally (`src/spatial/transform/TransientCleanup.scala:135-152`). `inlineBlock` advances block context before transforming block inputs and applies block substitutions both around statements and around the block result, so reduce/block-result uses see the duplicated transient rather than an illegal outer symbol (`src/spatial/transform/TransientCleanup.scala:154-195`).

`UnitIterationElimination` rewrites `OpForeach` nodes that have at least one unit counter. If all counters are `isUnit && ctrParOr1 == 1`, it substitutes every iterator with its counter start and stages a `UnitPipe`; otherwise it drops only transformable counters, remakes the remaining counter chain and iterators, and restages an `OpForeach` (`src/spatial/transform/UnitIterationElimination.scala:12-48`, `src/spatial/transform/UnitIterationElimination.scala:50-57`). `ForeachToUnitpipeTransformer` is the older single-iteration version: it only handles static `OpForeach` with `approxIters == 1`, substitutes each iterator with `ctrStart`, and stages a `UnitPipe` (`src/spatial/transform/ForeachToUnitpipeTransformer.scala:10-29`). `UnitPipeToForeachTransformer` performs the opposite conversion for hardware `UnitPipe`s by creating a one-iteration counter, counter chain, bound iterator, and pipelined `OpForeach` wrapper (`src/spatial/transform/UnitPipeToForeachTransformer.scala:11-35`).

`DuplicateRetimeStripper` canonicalizes inner-control blocks by staging the first `RetimeGate()` in a run and dropping subsequent adjacent `RetimeGate()` nodes until a non-retime statement appears (`src/spatial/transform/DuplicateRetimeStripper.scala:9-24`, `src/spatial/transform/DuplicateRetimeStripper.scala:27-35`). This cleanup is intentionally placed before retiming analysis in `retimeAnalysisPasses`, so the analyzer sees a block without duplicate back-to-back retime markers (`src/spatial/Spatial.scala:140`).

## Metadata produced/consumed

Cleanup consumes `Users`, `PendingUses`, `readers`, `writers`, `isUnusedMemory`, `keepUnused`, `effects`, FIFO `fifoInits`, and retiming/control metadata (`src/spatial/traversal/UseAnalyzer.scala:19-39`, `src/spatial/transform/TransientCleanup.scala:53-132`, `src/spatial/transform/RegReadCSE.scala:21-35`, `src/spatial/transform/FIFOAccessFusion.scala:67-83`). It produces substitutions and new mirrors for transient values, clears metadata classes through `MetadataStripper`, adds `transientReadMems` to controls when duplicated transient readers read memories, and invalidates removed nodes (`src/spatial/transform/TransientCleanup.scala:73-83`, `src/spatial/transform/TransientCleanup.scala:86-132`, `src/spatial/transform/MetadataStripper.scala:6-32`). `FIFOInitializer` is related because the canonical chain strips `FifoInits` after initializer insertion; the initializer itself emits a run-once pipe that enqueues initialization vectors before visiting the rest of the block (`src/spatial/transform/streamify/FIFOInitializer.scala:11-39`, `src/spatial/Spatial.scala:138`).

## Invariants established

After the DCE wave, hardware transient primitives are either duplicated into the blocks that consume them or removed if unused, and unused register storage/writes can be invalidated (`src/spatial/transform/TransientCleanup.scala:62-132`). After `RegReadCSE`, duplicate register reads inside inner controls share a cached read only when effects are identical (`src/spatial/transform/RegReadCSE.scala:21-35`). After `FIFOAccessFusion`, adjacent FIFO enqueues with the same enable set are represented as vector enqueues when possible and are never fused across a `RetimeGate` flush (`src/spatial/transform/FIFOAccessFusion.scala:20-48`, `src/spatial/transform/FIFOAccessFusion.scala:76-83`). After retime stripping, inner blocks do not contain adjacent `RetimeGate()` runs longer than one (`src/spatial/transform/DuplicateRetimeStripper.scala:10-24`).

## HLS notes

Most cleanup patterns transfer cleanly to HLS: dead storage removal, local CSE with effect checks, FIFO enqueue batching, unit-iteration loop collapse, and metadata stripping are compiler-neutral transformations (`src/spatial/transform/MemoryCleanupTransformer.scala:18-19`, `src/spatial/transform/RegReadCSE.scala:21-35`, `src/spatial/transform/FIFOAccessFusion.scala:20-48`, `src/spatial/transform/UnitIterationElimination.scala:12-48`, `src/spatial/transform/MetadataStripper.scala:21-31`). The HLS caution is around transient duplication and retime gates: Spatial's legality is block-context and retiming-marker aware, so an HLS implementation should preserve consumer-block placement and timing barriers rather than running a generic DCE/CSE pass blindly (`src/spatial/transform/TransientCleanup.scala:154-195`, `src/spatial/transform/DuplicateRetimeStripper.scala:9-35`).

## Open questions

No new source-blocking cleanup question is filed here. The notable caveat is chain membership: `UnitPipeToForeachTransformer`, `FIFOAccessFusion`, and `UnitIterationElimination` are constructed as lazy vals but are not visible in the canonical chain excerpt, while `ForeachToUnitpipeTransformer` exists as a file-level transformer but is not shown in that lazy-val block (`src/spatial/Spatial.scala:107-122`, `src/spatial/Spatial.scala:164-235`, `src/spatial/transform/ForeachToUnitpipeTransformer.scala:10-34`).
