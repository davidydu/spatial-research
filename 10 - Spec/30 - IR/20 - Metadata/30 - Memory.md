---
type: spec
concept: Spatial IR Metadata - Memory
source_files:
  - "src/spatial/metadata/memory/BankingData.scala:17-662"
  - "src/spatial/metadata/memory/AccumulatorData.scala:5-103"
  - "src/spatial/metadata/memory/MemoryData.scala:6-116"
  - "src/spatial/metadata/memory/LocalMemories.scala:6-17"
  - "src/spatial/metadata/memory/RemoteMemories.scala:6-16"
  - "src/spatial/metadata/memory/Synchronization.scala:6-20"
  - "src/spatial/metadata/memory/BroadcastAddress.scala:1-5"
  - "src/spatial/metadata/memory/package.scala:14-553"
source_notes:
  - "direct-source-reading"
hls_status: rework
depends_on:
  - "[[00 - Metadata Index]]"
  - "[[10 - Control]]"
  - "[[20 - Access]]"
status: draft
---

# Memory

## Summary

Memory metadata is Spatial's largest metadata category: it stores local/remote memory sets, reader/writer/resetter links, banking and duplication decisions, buffer-port assignments, accumulator/reduction classification, user banking directives, stream-buffer annotations, synchronization tags, and miscellaneous memory identity flags (`src/spatial/metadata/memory/MemoryData.scala:6-116`, `src/spatial/metadata/memory/BankingData.scala:17-662`, `src/spatial/metadata/memory/AccumulatorData.scala:5-103`). The key distinction is between analysis-time `Instance`, which keeps access groups, controllers, metapipe, cost, ports, and chosen banking, and compact `Memory`, which stores the final banking/depth/padding/accumulator type per physical duplicate (`src/spatial/metadata/memory/BankingData.scala:108-185`). `Duplicates(Seq[Memory])` is the metadata carrier for pre-unrolling multiple physical duplicates and post-unrolling single memory instances (`src/spatial/metadata/memory/BankingData.scala:261-278`).

## Syntax / API

`Banking` is the abstract banking strategy with `nBanks`, `stride`, `axes`, `alphas`, `Ps`, diagnostic `hiddenVolume`, `numChecks`, `solutionVolume`, and `bankSelect(addr)` (`src/spatial/metadata/memory/BankingData.scala:17-28`). `UnspecifiedBanking` is a one-bank placeholder with unit stride, unit alphas/Ps, zero hidden volume, and a sum-tree bank select (`src/spatial/metadata/memory/BankingData.scala:30-47`). `ModBanking(N, B, alpha, axes, P, sv, checks)` implements `(alpha dot addr / B) mod N` and reports block-cyclic hidden volume from `P mod N` (`src/spatial/metadata/memory/BankingData.scala:49-70`). `Port(bufferPort, muxPort, muxOfs, castgroup, broadcast)` describes both N-buffer selection and time-multiplexed mux placement; `bufferPort = None` means the access is time-multiplexed outside the metapipeline buffer (`src/spatial/metadata/memory/BankingData.scala:76-105`).

`Memory.bankSelects` supports flat banking and one-bank-per-sparse-rank hierarchical banking, while `Memory.bankOffset` computes flat and hierarchical bank-local offsets, including intrablock offsets from alpha-weighted addresses modulo block size (`src/spatial/metadata/memory/BankingData.scala:202-254`). `Memory.resourceType` is a mutable `var`, and `resource` falls back to the target default resource when it is unset (`src/spatial/metadata/memory/BankingData.scala:186-188`). This is transformer-time mutable state, and the Rust port should avoid hiding it behind otherwise immutable `Memory` values (inferred, unverified) (`src/spatial/metadata/memory/BankingData.scala:180-188`).

## Semantics

The transfer-policy surface is broad. `Duplicates`, `Dispatch`, `GroupId`, and `Ports` are `Transfer.Mirror`; `Padding` is `SetBy.Analysis.Self`; user directives such as `EnableWriteBuffer`, `EnableNonBuffer`, `NoHierarchicalBank`, `NoBlockCyclic`, `OnlyBlockCyclic`, `NConstraints`, `AlphaConstraints`, `BlockCyclicBs`, `OnlyDuplicate`, `DuplicateOnAxes`, `NoDuplicate`, `NoFlatBank`, `MustMerge`, `KeepUnused`, `DualPortedRead`, `ShouldCoalesce`, `IgnoreConflicts`, `BankingEffort`, `ExplicitBanking`, `FullyBankDims`, and `ForceExplicitBanking` are `SetBy.User` (`src/spatial/metadata/memory/BankingData.scala:277-662`). `Readers`, `Writers`, and `Resetters` are `SetBy.Flow.Consumer`; `OriginalSym`, `Breaker`, `DephasedAccess`, `HotSwapPairings`, and `InterfaceStream` are `SetBy.Analysis.Self`; `UnusedMemory` is `SetBy.Analysis.Consumer`; `ExplicitName` and `StreamBufferAmount` are `SetBy.User`; `StreamBufferIndex`, `FifoInits`, and `FIFOType` are `Transfer.Mirror` (`src/spatial/metadata/memory/MemoryData.scala:6-116`). `LocalMemories` and `RemoteMemories` are global flow data (`src/spatial/metadata/memory/LocalMemories.scala:6-17`, `src/spatial/metadata/memory/RemoteMemories.scala:6-16`).

Banking search uses `SearchPriority` across `BankingOptions(view, N, alpha, regroup)`, where relaxed N or alpha choices mark the option as undesired (`src/spatial/metadata/memory/BankingData.scala:488-496`). `Flat(rank)` expands to one list containing all dimensions, while `Hierarchical(rank, view)` expands to one singleton list per selected dimension and tracks complement dimensions (`src/spatial/metadata/memory/BankingData.scala:510-530`). `NStrictness.expand` enumerates candidate bank counts from user-defined lists, powers of two, factor/best-guess heuristics, or the full relaxed range (`src/spatial/metadata/memory/BankingData.scala:532-569`). `AlphaStrictness.selectAs` generates coprime alpha vectors from a valid list, and concrete alpha strategies draw from user-defined vectors, powers of two, best-guess factors/dimension products/coprimes/easy sums, or relaxed modular values (`src/spatial/metadata/memory/BankingData.scala:571-635`).

Explicit banking is represented as `Seq[BankingScheme]`, one scheme per duplicate, where each scheme stores `Ns`, `Bs`, `Alphas`, and optional `Ps` (`src/spatial/metadata/memory/BankingData.scala:637-645`). `explicitSchemeDup` derives one flat `ModBanking` when the explicit scheme has one `N`, otherwise one hierarchical `ModBanking` per dimension; missing `P` values are computed by `computeP` and selected by `bestPByVolume` (`src/spatial/metadata/memory/package.scala:81-119`). LockDRAM has special fallback behavior: `instance` returns a zero-banking unit memory, `dispatch` and `gid` return `Set(0)`, and `port` returns `Port(None, 0, 0, Seq(0), Seq(0))` when the access reads or writes LockDRAM (`src/spatial/metadata/memory/package.scala:168-172`, `src/spatial/metadata/memory/package.scala:201-245`).

## Implementation

The accumulator lattice is source-sensitive. `AccumulatorType` is `Transfer.Mirror`, while `ReduceType`, `FMAReduce`, `IterDiff`, `SegmentMapping`, `InnerAccum`, and `InnerReduceOp` are `SetBy.Analysis.Self` (`src/spatial/metadata/memory/AccumulatorData.scala:49-103`). The source implements `Fold > all non-Fold`, `Buff > Reduce/None/Unknown`, `Reduce > None/Unknown`, `None > Unknown`, and `Unknown > nothing` through the `>` methods (`src/spatial/metadata/memory/AccumulatorData.scala:11-45`). That source order differs from the expected `Fold > Reduce > Buff > None > Unknown`, so Q-meta-07 tracks whether the implementation or expectation is authoritative. Both `None | Unknown` and `Unknown | None` evaluate to `None`, but they do so through different method bodies (`src/spatial/metadata/memory/AccumulatorData.scala:34-45`).

`AccumType` accessors default to `AccumType.Unknown` in `package.scala`, even though the `AccumulatorType` comment states default `AccumType.None`; this is another source-level discrepancy to preserve for porting review (`src/spatial/metadata/memory/AccumulatorData.scala:49-57`, `src/spatial/metadata/memory/package.scala:14-16`). `reduceType`, `fmaReduceInfo`, `iterDiff`, `segmentMapping`, `isInnerAccum`, `keepUnused`, and `isInnerReduceOp` are simple metadata wrappers with defaults of `None`, `1`, empty map, or false (`src/spatial/metadata/memory/package.scala:14-43`).

User directive accessors intentionally preserve several independent policy knobs rather than collapsing them into one banking mode. `isWriteBuffer`, `isNonBuffer`, `isNoHierarchicalBank`, `noBlockCyclic`, `onlyBlockCyclic`, `shouldIgnoreConflicts`, `bankingEffort`, `explicitBanking`, `fullyBankDims`, `forceExplicitBanking`, `isNoFlatBank`, `isMustMerge`, `isDualPortedRead`, `isFullFission`, `duplicateOnAxes`, `nConstraints`, `alphaConstraints`, `isNoFission`, and `shouldCoalesce` are all separate getters/setters (`src/spatial/metadata/memory/package.scala:45-149`). Defaults come from false, empty sets, empty sequences, `None`, or `spatialConfig.bankingEffort`; `isDualPortedRead` additionally requires the memory to be SRAM and can be enabled globally by `spatialConfig.dualReadPort` (`src/spatial/metadata/memory/package.scala:45-149`). The HLS port should therefore treat directives as composable constraints, not a single enum, until a compatibility layer proves which combinations are impossible (inferred, unverified).

Memory access metadata is mutated incrementally. `dispatches`, `gids`, and `Ports` are maps keyed by unroll uid and dispatch id; `addDispatch`, `addGroupId`, and `addPort` rebuild metadata maps by adding entries to the existing map or creating a new one (`src/spatial/metadata/memory/package.scala:201-249`). `setBufPort` removes existing `Ports` metadata, rebuilds a `Port` with a new `Some(p)` buffer port, and re-adds the rewritten map, so it is a destructive metadata rewrite rather than an immutable update (`src/spatial/metadata/memory/package.scala:250-258`). `swappers` finds buffered accesses, chooses an LCA, handles parallel LCAs specially, and maps buffer port spans to children controllers (`src/spatial/metadata/memory/package.scala:177-197`).

The remaining memory flags describe identity and stream behavior. `isLocalMem`, `isRemoteMem`, `isMem`, dense/sparse alias predicates, addressability, memory kind predicates, and `memName` are all symbol/op classifiers (`src/spatial/metadata/memory/package.scala:263-431`). Initial values are detected for `RegNew`, `RegFileNew`, `LUTNew`, and FIFO inits (`src/spatial/metadata/memory/package.scala:433-439`). `StreamBufferAmount` exposes amount/min/max, `StreamBufferIndex` stores the staged buffer index, and `FifoInits`/`FIFOType` store FIFO initialization/type metadata (`src/spatial/metadata/memory/MemoryData.scala:98-116`, `src/spatial/metadata/memory/package.scala:441-458`). `Barrier` and `Wait` are `SetBy.User`; `Wait` stores mutable `ListBuffer[Int]`, and `waitFor` mutates the existing buffer after creating metadata when absent (`src/spatial/metadata/memory/Synchronization.scala:6-20`, `src/spatial/metadata/memory/package.scala:503-514`). `BroadcastAddress` is a mirrored boolean metadata flag with accessors on memory access ops (`src/spatial/metadata/memory/BroadcastAddress.scala:1-5`, `src/spatial/metadata/memory/package.scala:490-492`).

## Interactions

Memory metadata depends on access matrices for `Instance` read/write groups and on control hierarchy for controllers, metapipe, LCA, and buffer swapping (`src/spatial/metadata/memory/BankingData.scala:108-124`, `src/spatial/metadata/memory/package.scala:177-197`). Banking options depend on staged dimensions, rank, and user directives exposed by `BankedMemoryOps` (`src/spatial/metadata/memory/package.scala:45-199`). Transfer synchronization is copied manually by `transferSyncMeta`, which moves wait and barrier metadata from one symbol to another by invoking the public setters (`src/spatial/metadata/memory/package.scala:539-547`). `internalMems` exposes block-local memory symbols for block-level traversals (`src/spatial/metadata/memory/package.scala:549-551`).

## HLS notes

Banking concepts transfer, but the selected schemes, buffer ports, duplication policy, and accumulator classification should be re-derived for the HLS memory system rather than treated as portable facts (inferred, unverified). Preserve the explicit `(N, B, alpha, P, axes)` model and the distinction between mirrored structural decisions and `SetBy.Analysis` products, because those are the hooks needed to compare Scala Spatial with a Rust/HLS search implementation (`src/spatial/metadata/memory/BankingData.scala:49-70`, `src/spatial/metadata/memory/BankingData.scala:277-662`).

## Open questions

- Q-meta-07: Is the intended accumulator order `Fold > Reduce > Buff > None > Unknown`, or should the port preserve the source behavior `Fold > Buff > Reduce > None > Unknown`?
- Q-meta-08: Should `AccumulatorType` default to `Unknown` as the package accessor does, or `None` as the metadata comment says?
- Q-meta-09: Can mutable memory metadata patterns (`Memory.resourceType`, `Wait.ids`, `setBufPort`) be replaced with explicit analysis-state updates in Rust?
- Q-meta-10: Are LockDRAM fallback banking/dispatch/port hacks required semantics or temporary compatibility behavior?
