---
type: spec
concept: "Modeling Utilities"
source_files:
  - "src/spatial/util/modeling.scala:1-992"
  - "src/spatial/util/math.scala:1-77"
  - "src/spatial/util/memops.scala:1-93"
  - "src/spatial/util/IntLike.scala:1-107"
  - "src/spatial/util/TransformUtils.scala:1-187"
  - "src/spatial/util/VecStructType.scala:1-114"
source_notes:
  - "[[open-questions-infra]]"
hls_status: rework
depends_on:
  - "[[70 - Timing Model]]"
  - "[[10 - Area Model]]"
  - "[[C0 - Retiming]]"
status: draft
---

# Modeling Utilities

## Summary

`spatial.util.modeling` is the compiler's shared latency, cycle, retiming, area-model, and producer/consumer accounting helper. It is a 992-line singleton that imports Argon symbols, Spatial metadata for access/control/memory/retiming/types/debug/transform, Spatial nodes, target area/latency models, and collection helpers before defining graph traversals, latency accounting, cycle discovery, delay-line computation, and token communication utilities `src/spatial/util/modeling.scala:1-26`. It is infrastructure rather than a formal pass: traversal passes and reporters import it when they need a consistent view of critical paths, reduction cycles, memory conflicts, or target area models.

Among the requested helper files, this appears to have the broadest active import/use footprint. Active callers include `RetimingAnalyzer`, which calls `pipeLatencies` and adjusts full delays `src/spatial/traversal/RetimingAnalyzer.scala:35-49`; `InitiationAnalyzer`, which calls `latenciesAndCycles` for FSM action blocks `src/spatial/traversal/InitiationAnalyzer.scala:57-57`; `MemoryReporter`, which calls `areaModel` and `NoArea` for memory summaries `src/spatial/report/MemoryReporter.scala:21-27`; `MemoryAllocator`, which imports `target` and `areaModel` for raw memory area and bank depth `src/spatial/traversal/MemoryAllocator.scala:8-83`; and `DSEAreaAnalyzer`, the active area analyzer, which calls `latenciesAndCycles`, `latencyOf`, `latencyOfPipe`, and `areaModel` `src/spatial/dse/DSEAreaAnalyzer.scala:67-107`. The older `src/spatial/traversal/AreaAnalyzer.scala` has commented references to this API rather than active code (inferred from declaration/comment scan).

## API

The prompt's requested API list spans top-level helpers plus one nested guard:

- `areaModel(mlModel)`, `NoArea`, `target`, and `latencyModel` expose the selected hardware target's model objects `src/spatial/util/modeling.scala:87-90`.
- `latencyOf(e, inReduce)` wraps `latencyModel.latencyOf`, returning zero when retiming is disabled and the target would otherwise require registers `src/spatial/util/modeling.scala:92-96`.
- `latencyOfPipe(block)` calls `latencyAndInterval` and returns the critical latency component `src/spatial/util/modeling.scala:99-105`.
- `latenciesAndCycles(block)` extracts a nested schedule/result pair and delegates to `pipeLatencies` `src/spatial/util/modeling.scala:61-64` `src/spatial/util/modeling.scala:128-130`.
- `findAccumCycles(schedule)` finds memory read/write recurrence candidates and returns `ScopeAccumInfo` with grouped readers, writers, accumulation triples, and cycle membership `src/spatial/util/modeling.scala:136-199`.
- `brokenByRetimeGate(x1, x2, schedule)` is a nested helper inside `findAccumCycles`, not an object-level public method; it suppresses cycles whose read/write pair crosses a retime gate `src/spatial/util/modeling.scala:165-168`.
- `pipeLatencies(result, schedule, oos, verbose)` is the main critical-path and cycle accountant, returning per-symbol delays plus `Cycle` records `src/spatial/util/modeling.scala:201-560`.
- `mutatingBounds`, `consumersDfs`, `consumersBfs`, `consumersSearch`, and `getAllNodesBetween` are graph-search helpers used for bound mutation, dependency scope expansion, and path extraction `src/spatial/util/modeling.scala:28-85`.

Two details matter for readers trying to reimplement the behavior. First, `consumersSearch` is configuration-sensitive: it chooses DFS or BFS from `spatialConfig.dfsAnalysis`, so callers should not assume a stable traversal order unless they sort the result afterward `src/spatial/util/modeling.scala:50-58`. Second, `getAllNodesBetween` walks backward through inputs, but treats memories specially by following in-scope writers when it hits a memory symbol; this is how accumulation-cycle paths include memory-mediated dependencies instead of only pure dataflow edges `src/spatial/util/modeling.scala:70-84`.

## Implementation

The core latency flow is staged in three layers. `latencyAndInterval` computes `latenciesAndCycles`, takes the maximum symbol latency as the block latency, derives a compiler II from the largest cycle length, and has special handling for segmented WAR cycles by summing per-memory segment cycle lengths `src/spatial/util/modeling.scala:107-124`. `findAccumCycles` first collects reader-like and writer-like access nodes, groups them by memory, removes argument-input and lock SRAM cases, filters read/write pairs through `brokenByRetimeGate` and `independentOf`, then uses `getAllNodesBetween` to mark the symbols inside a recurrence path `src/spatial/util/modeling.scala:152-198`. `pipeLatencies` initializes mutable `paths` and `cycles`, calls `findAccumCycles`, computes dependency delays with a forward DFS, performs a reverse DFS to push unnecessary delays out of reduction cycles, finds pseudo WAR cycles, accounts for multiplexed accesses, protects RAW register cycles, handles segmentation, pushes retime gates, and returns recomputed AAA/WAR cycle records `src/spatial/util/modeling.scala:201-560`.

Retiming support continues after `pipeLatencies`. `computeDelayLines` uses per-symbol latencies, required retiming delay, built-in latency, and consumer critical paths to create or reuse `ValueDelay` records for missing alignment registers `src/spatial/util/modeling.scala:570-649`. Lower in the file, `MemStrategy`, `TokenComm`, and `computeProducerConsumers` compute memory-token communication edges between controller contexts for duplicated, buffered, FIFO, and custom memory strategies `src/spatial/util/modeling.scala:691-921`.

The nearby utility files are smaller support layers. `math.scala` rewrites modulo patterns with `selectMod`, constant residue sets with `constMod`, and static counter/modulo tests with `staticMod` `src/spatial/util/math.scala:15-50`. `memops.scala` adds sparse memory accessors such as `sparseStarts`, `sparseSteps`, `sparseEnds`, `sparsePars`, `sparseLens`, and `sparseOrigins`, each staging the corresponding `Mem*` node per sparse rank `src/spatial/util/memops.scala:16-40`. `IntLike.scala` defines a typeclass for integer-like arithmetic over `Int`, `I32`, `Idx`, and emulation `FixedPoint`, plus extension operators and reduction helpers `src/spatial/util/IntLike.scala:8-107`. `TransformUtils.scala` centralizes counter/iterator helpers, synthetic unit pipes, source context augmentation, and substitution-state utilities for transformers `src/spatial/util/TransformUtils.scala:14-187`. `VecStructType.scala` packs named fields into bit slices, unpacks them by recorded locations, and provides a `VFIFO` alias for vector-struct FIFOs `src/spatial/util/VecStructType.scala:11-113`.

The lower half of `modeling.scala` is not only latency accounting. `reductionTreeDelays` and `reductionTreeHeight` model uneven binary reductions, so reduction code can estimate inserted delay paths and tree depth without rebuilding the tree `src/spatial/util/modeling.scala:652-689`. The token communication utilities can also dump a Graphviz view of memory communication, which makes this file a diagnostic aid as well as an analysis helper `src/spatial/util/modeling.scala:924-990`.

## Interactions

Retiming consumes `pipeLatencies`, `latencyOf`, `scrubNoise`, and delay-line logic to annotate or transform latency metadata `src/spatial/traversal/RetimingAnalyzer.scala:35-49` `src/spatial/transform/RetimingTransformer.scala:214-215`. Accumulation and initiation analysis reuse the same cycle finder rather than recomputing recurrence semantics independently `src/spatial/traversal/AccumAnalyzer.scala:41-41` `src/spatial/traversal/InitiationAnalyzer.scala:57-57`. Memory diagnostics and allocation use `areaModel` and token/control helpers for resource summaries and memory bank decisions `src/spatial/report/MemoryReporter.scala:21-27` `src/spatial/traversal/MemoryAllocator.scala:8-83`.

Control metadata also calls into this utility layer. `mutatingBounds` is used to decide whether counter starts, steps, and conditions depend on mutating symbols when computing controller properties `src/spatial/metadata/control/package.scala:518-542` `src/spatial/metadata/control/package.scala:1031-1034`. Access analysis uses `modeling.consumersSearch` to expand consumer scopes from initial symbols `src/spatial/traversal/AccessAnalyzer.scala:10-36`. Those call sites are why changing traversal semantics or returned ordering in this file can affect more than retiming.

## HLS notes

This entry is `rework` for HLS. The compiler needs equivalent target latency and area models, but the current implementation assumes Spatial's metadata, target model API, and retiming strategy. An HLS port should decide whether this remains a target-specific analysis layer or becomes a narrower pragma/II estimator.

## Open questions

See [[open-questions-infra#Q-inf-01]] for the `brokenByRetimeGate` API mismatch and [[open-questions-infra#Q-inf-02]] for the active area-analyzer/caller naming question.
