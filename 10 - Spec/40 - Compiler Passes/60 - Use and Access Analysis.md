---
type: spec
concept: use-and-access-analysis
source_files:
  - "src/spatial/Spatial.scala:76-88"
  - "src/spatial/Spatial.scala:140-142"
  - "src/spatial/Spatial.scala:203-224"
  - "src/spatial/Spatial.scala:227-233"
  - "src/spatial/traversal/UseAnalyzer.scala:11-153"
  - "src/spatial/traversal/AccessAnalyzer.scala:19-322"
  - "src/spatial/traversal/AccessExpansion.scala:15-129"
  - "src/spatial/traversal/AccumAnalyzer.scala:14-244"
  - "src/spatial/traversal/IterationDiffAnalyzer.scala:15-217"
  - "src/spatial/traversal/InitiationAnalyzer.scala:12-101"
  - "src/spatial/traversal/RewriteAnalyzer.scala:11-63"
  - "src/spatial/traversal/CounterIterSynchronization.scala:9-17"
  - "src/spatial/traversal/PerformanceAnalyzer.scala:11-98"
  - "src/spatial/traversal/BufferRecompute.scala:13-54"
  - "src/spatial/traversal/BroadcastCleanup.scala:11-132"
  - "src/spatial/traversal/RerunTraversal.scala:6-13"
source_notes:
  - "[[pass-pipeline]]"
hls_status: rework
depends_on:
  - "[[50 - Pipe Insertion]]"
  - "[[70 - Banking]]"
  - "[[80 - Unrolling]]"
  - "[[C0 - Retiming]]"
status: draft
---

# Use and Access Analysis

## Summary

This entry covers the analysis passes that connect dead-code cleanup, banking, reduction specialization, initiation intervals, post-unroll repair, and final broadcast metadata cleanup. `UseAnalyzer`, `AccessAnalyzer`, `IterationDiffAnalyzer`, `InitiationAnalyzer`, `RewriteAnalyzer`, `BufferRecompute`, `AccumAnalyzer`, `CounterIterSynchronization`, and `BroadcastCleanupAnalyzer` are all constructed in the analysis block of `runPasses` (`src/spatial/Spatial.scala:76-88`, `src/spatial/Spatial.scala:127-128`). `UseAnalyzer` is part of the reusable `DCE` sequence, banking runs retime analysis then access/iteration/memory allocation, `RewriteAnalyzer` and `AccumAnalyzer` precede hardware rewrites, `BufferRecompute` runs after flattening/binding, and `BroadcastCleanupAnalyzer` runs just before final `InitiationAnalyzer` (`src/spatial/Spatial.scala:140-142`, `src/spatial/Spatial.scala:162`, `src/spatial/Spatial.scala:203-224`, `src/spatial/Spatial.scala:227-233`).

## Pass list and roles

- `UseAnalyzer` computes usage metadata for transient nodes, counters, and memory readers and warns about unused memories (`src/spatial/traversal/UseAnalyzer.scala:14-41`, `src/spatial/traversal/UseAnalyzer.scala:43-153`).
- `AccessAnalyzer` extracts affine `AddressPattern`s and unrolled `AccessMatrix` sets for memory accesses; `AccessExpansion` supplies the materialization logic used by banking (`src/spatial/traversal/AccessAnalyzer.scala:19-25`, `src/spatial/traversal/AccessAnalyzer.scala:215-259`, `src/spatial/traversal/AccessExpansion.scala:66-127`).
- `AccumAnalyzer` identifies write-after-read accumulation cycles and writes `reduceCycle` markers for `AccumTransformer` (`src/spatial/traversal/AccumAnalyzer.scala:38-103`, `src/spatial/traversal/AccumAnalyzer.scala:195-241`).
- `IterationDiffAnalyzer` computes loop-carried accumulation iteration distances and segment mappings from `findAccumCycles` plus affine matrices (`src/spatial/traversal/IterationDiffAnalyzer.scala:17-118`, `src/spatial/traversal/IterationDiffAnalyzer.scala:119-169`).
- `InitiationAnalyzer` computes `II`, `compilerII`, and `bodyLatency` for inner and outer controls (`src/spatial/traversal/InitiationAnalyzer.scala:14-45`).
- `RewriteAnalyzer` precomputes whether add/multiply shapes may be fused as FMA before `RewriteTransformer` mutates the IR (`src/spatial/traversal/RewriteAnalyzer.scala:11-16`, `src/spatial/traversal/RewriteAnalyzer.scala:39-59`).
- `CounterIterSynchronization`, `BufferRecompute`, `BroadcastCleanupAnalyzer`, `PerformanceAnalyzer`, and `RerunTraversal` are smaller repair/estimation utilities (`src/spatial/traversal/CounterIterSynchronization.scala:9-17`, `src/spatial/traversal/BufferRecompute.scala:13-54`, `src/spatial/traversal/BroadcastCleanup.scala:11-132`, `src/spatial/traversal/PerformanceAnalyzer.scala:11-98`, `src/spatial/traversal/RerunTraversal.scala:6-13`).

## Algorithms

`UseAnalyzer` resets global `PendingUses` in `preprocess` and then clears `Users` metadata on every visited node (`src/spatial/traversal/UseAnalyzer.scala:14-17`, `src/spatial/traversal/UseAnalyzer.scala:43-51`). At block entry it adds uses from block inputs to the owning controller, and at block exit it adds pending uses from the block result to the same controller (`src/spatial/traversal/UseAnalyzer.scala:70-89`). `checkUses` collects pending uses from non-block expression inputs; if the current node is transient or a counter in an outer scope, it propagates pending uses, otherwise it records direct uses on each consumed symbol (`src/spatial/traversal/UseAnalyzer.scala:100-146`). In `postprocess`, it marks unused registers as `isUnusedMemory = true` and warns for named local memories that are never read, except stream-outs and breakers (`src/spatial/traversal/UseAnalyzer.scala:19-41`). `readUses` itself is propagated by the accumulator flow rule, not by `UseAnalyzer`: readers add themselves, nodes union their inputs' read uses, and writers compare those reads against their written memory (`src/spatial/flows/SpatialFlowRules.scala:44-67`).

`AccessAnalyzer` maintains loop iterators, loop starts, loop owner symbols, per-iterator scopes, and most-recent register writes (`src/spatial/traversal/AccessAnalyzer.scala:19-25`). Its affine extractor has `Plus`, `Minus`, `Times`, `Divide`, `Mod`, `Index`, `LU`, and `Read` unapplies; `Times` treats `FixSLA(a, const)` as multiplication by `2^const`, and `LU`/`Read` substitute reaching register writes when known (`src/spatial/traversal/AccessAnalyzer.scala:75-88`). `Affine.unapply` maps a non-null loop iterator to an `AffineComponent(stride(i), i)`, cancels additive inverse components with `combine`, distributes invariant products, follows substituted reads, and treats unknown symbols as offset sums (`src/spatial/traversal/AccessAnalyzer.scala:125-177`). For ordinary accesses it writes `access.accessPattern` and `access.affineMatrices`; for streaming accesses it spoofs an N-D linear pattern over access iterators and vector lanes (`src/spatial/traversal/AccessAnalyzer.scala:215-259`, `src/spatial/traversal/AccessAnalyzer.scala:299-320`).

`AccessExpansion.getUnrolledMatrices` computes the access iterators and their parallelisms, builds a compact sparse matrix, iterates the cross-product of unroll ids with `multiLoop(ps)`, scales iterator columns by parallelism, offsets them by lane id, and substitutes non-iterator symbols either with `LaneStatic` constants or fresh random bound variables (`src/spatial/traversal/AccessExpansion.scala:26-31`, `src/spatial/traversal/AccessExpansion.scala:66-127`). `getOrAddDomain` materializes min/max constraints from counter starts and ends for each index symbol (`src/spatial/traversal/AccessExpansion.scala:36-55`).

`AccumAnalyzer.markBlock` calls `latenciesAndCycles(block, true)`, keeps `WARCycle`s, rejects overlapping or externally visible cycles, requires local memories with a single writer and no outer unit-pipe reduce writer, and then attaches a copied cycle to every symbol in the cycle through `s.reduceCycle = cycle` (`src/spatial/traversal/AccumAnalyzer.scala:38-103`). `AssociateReduce` recognizes `RegWrite` forms for add, multiply, min, max, and FMA, including mux-gated variants, and returns `AccumMarker.Reg.Op` or `AccumMarker.Reg.FMA` (`src/spatial/traversal/AccumAnalyzer.scala:195-241`).

`IterationDiffAnalyzer.findCycles` calls `findAccumCycles(stms).accums`, filters local-memory read/write triples under `ignoreAllConflicts`, and computes self-relative iterator exhaustion ticks, strides, global ticks, minimum ticks to overlap, and segment mappings for inter-lane conflicts (`src/spatial/traversal/IterationDiffAnalyzer.scala:17-68`, `src/spatial/traversal/IterationDiffAnalyzer.scala:70-118`, `src/spatial/traversal/IterationDiffAnalyzer.scala:119-169`). It also special-cases `OpMemReduce` iteration diff to zero and `OpReduce` iteration diff to one before visiting nested control (`src/spatial/traversal/IterationDiffAnalyzer.scala:193-210`).

`InitiationAnalyzer.visitInnerControl` computes per-block latency/interval, includes blackbox II, collects positive `iterDiff`s, forces II=1 when the largest iter diff is nonpositive, and otherwise sets `compilerII` to `interval`, `ceil(interval/minIterDiff)`, or one of the special cases before applying user-II and sequenced-schedule overrides (`src/spatial/traversal/InitiationAnalyzer.scala:23-41`). `visitOuterControl` uses the maximum child `II` and any user II for outer controllers (`src/spatial/traversal/InitiationAnalyzer.scala:14-21`).

`RewriteAnalyzer` must be a traversal because `RewriteTransformer` mutates the graph while consumer metadata can be stale; it sets `canFuseAsFMA` on `FixAdd` and `FltAdd` nodes when the multiply has either a single consumer or the reduce-specialization mux topology, reduce-op classification matches, and `spatialConfig.fuseAsFMA` is true (`src/spatial/traversal/RewriteAnalyzer.scala:11-16`, `src/spatial/traversal/RewriteAnalyzer.scala:26-59`). `CounterIterSynchronization` repairs each `Counter` to its bound iterator by assigning `IndexCounterInfo(ctr, Seq.tabulate(ctr.ctrParOr1)(i => i))`, which is needed after streamification and counter motion (`src/spatial/traversal/CounterIterSynchronization.scala:9-17`, `src/spatial/Spatial.scala:203-205`).

`BufferRecompute` visits memory allocations after unrolling/flattening, recomputes buffer ports with `computeMemoryBufferPorts`, updates duplicate depths to `max(bufferPort)+1`, and bumps conflicting mux ports as a temporary workaround (`src/spatial/traversal/BufferRecompute.scala:29-48`). `BroadcastCleanupAnalyzer` runs late, initializes memory allocations as non-broadcast, walks each inner controller block in reverse, and propagates `isBroadcastAddr` false or true through bank/offset/enable/data inputs depending on reader/writer port broadcast metadata (`src/spatial/traversal/BroadcastCleanup.scala:13-132`, `src/spatial/Spatial.scala:227-233`). `PerformanceAnalyzer` writes `latency` and `II` from runtime model helpers and implements rerun through `RerunTraversal`; the canonical `runPasses` path instead constructs `RuntimeModelGenerator` directly under `enableRuntimeModel` (inferred, unverified as a direct feed) (`src/spatial/traversal/PerformanceAnalyzer.scala:11-98`, `src/spatial/traversal/RerunTraversal.scala:6-13`, `src/spatial/Spatial.scala:154-155`, `src/spatial/Spatial.scala:180-182`, `src/spatial/Spatial.scala:233-235`).

## Metadata produced/consumed

This group writes `Users`, `PendingUses`, `accessPattern`, `affineMatrices`, index domains, `reduceCycle`, `iterDiff`, `segmentMapping`, `progorder`, `II`, `compilerII`, `bodyLatency`, `canFuseAsFMA`, memory duplicate depths, access ports, and `isBroadcastAddr` (`src/spatial/metadata/access/AccessData.scala:16-34`, `src/spatial/metadata/PendingUses.scala:8-24`, `src/spatial/traversal/AccessAnalyzer.scala:223-225`, `src/spatial/traversal/AccumAnalyzer.scala:96-101`, `src/spatial/traversal/IterationDiffAnalyzer.scala:115-168`, `src/spatial/traversal/InitiationAnalyzer.scala:36-40`, `src/spatial/traversal/BufferRecompute.scala:34-47`). Access metadata feeds [[70 - Banking|banking]], `reduceCycle` feeds accumulator specialization, `canFuseAsFMA` feeds hardware rewrites, and final `II/bodyLatency` feeds runtime model generation (`src/spatial/Spatial.scala:203-218`, `src/spatial/Spatial.scala:224-235`).

## Invariants established

After DCE's `UseAnalyzer`, transient and counter use chains are explicit enough for cleanup to distinguish real consumers from removable pending uses (`src/spatial/traversal/UseAnalyzer.scala:100-151`). After banking analysis, every non-frozen memory access that matched reader/writer/dequeuer/enqueuer patterns has affine matrices available for memory configuration (`src/spatial/traversal/AccessAnalyzer.scala:299-320`, `src/spatial/Spatial.scala:203`). After post-unroll repair, memory duplicate depths reflect the current buffer-port assignment rather than stale pre-unroll banking results (`src/spatial/traversal/BufferRecompute.scala:29-48`). After broadcast cleanup, broadcast-address metadata has been propagated backward from final banked access ports just before final initiation analysis and reporting (`src/spatial/traversal/BroadcastCleanup.scala:18-127`, `src/spatial/Spatial.scala:231-239`).

## HLS notes

HLS status is **rework**. The affine access and use analyses transfer conceptually, but HLS banking should rederive address matrices against the chosen HLS memory partitioning model rather than assume Spatial's `AccessMatrix`, `Port`, and `Duplicates` metadata (`src/spatial/traversal/AccessExpansion.scala:66-127`, `src/spatial/traversal/BufferRecompute.scala:34-47`). Accumulation and initiation analysis also need HLS-specific latency models because Spatial computes cycle lengths from `latenciesAndCycles`, retiming metadata, and Spatial controller schedules (`src/spatial/traversal/AccumAnalyzer.scala:38-42`, `src/spatial/traversal/InitiationAnalyzer.scala:23-41`). `RewriteAnalyzer`'s FMA flag is portable as a graph property, but the final decision should be coordinated with the HLS tool's own FMA inference (`src/spatial/traversal/RewriteAnalyzer.scala:39-59`).

## Open questions

- Q-pp-09 - whether `PerformanceAnalyzer` is still an active runtime-cycle estimator or an older rerunnable analysis left outside `runPasses`.
- Q-pp-11 - how much of `IterationDiffAnalyzer` should survive in HLS when the target scheduler may already serialize loop-carried dependencies.
