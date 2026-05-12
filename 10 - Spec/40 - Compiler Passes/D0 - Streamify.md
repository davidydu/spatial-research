---
type: spec
concept: streamify
source_files:
  - "src/spatial/transform/streamify/DependencyGraphAnalyzer.scala:17-199"
  - "src/spatial/transform/streamify/HierarchicalToStream.scala:65-838"
  - "src/spatial/transform/streamify/EarlyUnroller.scala:19-292"
  - "src/spatial/transform/streamify/AccelPipeInserter.scala:7-20"
  - "src/spatial/transform/streamify/FIFOInitializer.scala:11-52"
  - "src/spatial/transform/streamify/ForceHierarchical.scala:7-14"
  - "src/spatial/transform/streamify/TimeMap.scala:7-35"
  - "src/spatial/Spatial.scala:123-126"
  - "src/spatial/Spatial.scala:144"
  - "src/spatial/Spatial.scala:196-201"
  - "src/spatial/Spatial.scala:350-356"
source_notes:
  - "[[pass-pipeline]]"
hls_status: rework
depends_on:
  - "[[50 - Pipe Insertion]]"
  - "[[70 - Banking]]"
  - "[[C0 - Retiming]]"
status: draft
---

# Streamify

## Summary

Streamify is Spatial's experimental MetaPipe-to-Stream conversion path. The user-facing gate is `--streamify`, which sets `spatialConfig.streamify = true`; `--nostreamify` clears it (`src/spatial/Spatial.scala:350-356`). The canonical `runPasses` chain invokes the `streamify` sequence only under that flag, before stream counter distribution and FIFO initialization (`src/spatial/Spatial.scala:196-201`). The current `streamify` sequence is source-visible as dumps plus `dependencyGraphAnalyzer`, `initiationAnalyzer`, `printer`, `streamChecks`, `HierarchicalToStream`, `switchTransformer`, `pipeInserter`, and another `streamChecks` (`src/spatial/Spatial.scala:144`). `EarlyUnroller`, `AccelPipeInserter`, and `ForceHierarchical` are constructed as lazy vals but are not present in that sequence, which is tracked as Q-pp-13 (`src/spatial/Spatial.scala:123-126`, `src/spatial/Spatial.scala:144`).

## Pass list and roles

`DependencyGraphAnalyzer` builds inter-controller dependency edges for each memory. It groups all accesses by parent, computes reaching writes for register and non-register memories, creates `InferredDependencyEdge(otherParent, parent, mem, EdgeType(otherParent, parent))`, adds initialize pseudo-edges when no forward dependency initializes a non-global memory, removes `Inner` edges, and stores `DependencyEdges` in globals during postprocess (`src/spatial/transform/streamify/DependencyGraphAnalyzer.scala:130-167`, `src/spatial/transform/streamify/DependencyGraphAnalyzer.scala:169-198`). `EdgeType` is determined from the LCA stage distance as `Inner`, `Backward`, or `Forward`, with `Initialize` as a pseudo-edge kind (`src/spatial/transform/streamify/DependencyGraphAnalyzer.scala:17-35`). `InferredDependencyEdge` implements source/destination iterator sets and `dstRecv`/`srcSend` predicates, using surrounding loops and first/last iterator tests to gate token movement (`src/spatial/transform/streamify/DependencyGraphAnalyzer.scala:35-127`).

`HierarchicalToStream` is the main transformer. It defines `PseudoIter`, `TokenWithValid`, `StreamBundle`, and `DependencyFIFOManager`, then turns each inner controller into a streaming `UnitPipe` containing counter generation, main work, and release controllers (`src/spatial/transform/streamify/HierarchicalToStream.scala:65-92`, `src/spatial/transform/streamify/HierarchicalToStream.scala:95-156`, `src/spatial/transform/streamify/HierarchicalToStream.scala:778-811`). `EarlyUnroller` is a `ForwardTransformer` that pre-unrolls `OpForeach`/`OpReduce`, substitutes shifted iterators, updates dispatch/port/gid/affine metadata, and rewrites `LaneStatic` values from the current lane map (`src/spatial/transform/streamify/EarlyUnroller.scala:19-23`, `src/spatial/transform/streamify/EarlyUnroller.scala:52-92`, `src/spatial/transform/streamify/EarlyUnroller.scala:95-203`, `src/spatial/transform/streamify/EarlyUnroller.scala:205-289`). Source verification shows it is one of several streamify files extending `ForwardTransformer`, not the only one; `AccelPipeInserter`, `FIFOInitializer`, and `HierarchicalToStream` also extend `ForwardTransformer` (`src/spatial/transform/streamify/AccelPipeInserter.scala:7-20`, `src/spatial/transform/streamify/FIFOInitializer.scala:11-52`, `src/spatial/transform/streamify/HierarchicalToStream.scala:151-151`).

## Algorithms

`HierarchicalToStream` first wraps the accelerator block in a `Stream { inlineBlock(accel.block) }`, identifies synchronization memories as memory nodes that are not internal to an inner-control LCA or stream-primitive ancestry, and creates FIFOs for all dependency edges (`src/spatial/transform/streamify/HierarchicalToStream.scala:737-767`, `src/spatial/transform/streamify/HierarchicalToStream.scala:674-679`). For each inner controller, `createInternalFIFOBundle` creates the FIFO trio requested by the design: `genToMainIters`/`genToMainTokens`, `genToReleaseIters`/`genToReleaseTokens`, and `mainToReleaseTokens`, with depths 8/16/8 and explicit names like `_g2mTokens`, `_g2rIter`, and `_m2rTokens` (`src/spatial/transform/streamify/HierarchicalToStream.scala:82-92`, `src/spatial/transform/streamify/HierarchicalToStream.scala:683-734`). `counterGen` walks the inner controller's ancestor stack, builds `TimeMap`s from counters, handles disabled branches by bypassing to release, enqueues pseudo-iterator vectors to both gen-to-main and gen-to-release, and enqueues intake tokens to `genToMainTokens` (`src/spatial/transform/streamify/HierarchicalToStream.scala:262-341`, `src/spatial/transform/streamify/HierarchicalToStream.scala:359-420`, `src/spatial/transform/streamify/HierarchicalToStream.scala:428-477`).

`mainGen` consumes `genToMainIters` and `genToMainTokens`, remaps iterators, replaces tokenized `RegRead`s with token values, mirrors the original inner-control statements, emits a `retimeGate`, and writes release tokens to `mainToReleaseTokens` (`src/spatial/transform/streamify/HierarchicalToStream.scala:480-599`). `releaseGen` runs forever, dequeues pseudo-iter tokens from `genToReleaseIters`, chooses between `mainToReleaseTokens` and `genToReleaseTokens` through a source FIFO, writes debug registers for each token, enqueues output dependency FIFOs when `edge.srcSend(tMap)` is true, emits another `retimeGate`, and writes `stopWhen` from the last pseudo-iterator flag or immediately when no time map exists (`src/spatial/transform/streamify/HierarchicalToStream.scala:601-672`). Accesses to synchronization memories are skipped during transformation, while outer hardware controls are wrapped into `UnitPipe`s marked `Streaming` (`src/spatial/transform/streamify/HierarchicalToStream.scala:770-823`).

## Metadata produced/consumed

The subsystem consumes access metadata (`readers`, `writers`, affine matrices, dispatches, ports, gids), control metadata (`ancestors`, `children`, `cchains`, `isInnerControl`, schedules), and the global `DependencyEdges` produced by `DependencyGraphAnalyzer` (`src/spatial/transform/streamify/DependencyGraphAnalyzer.scala:132-195`, `src/spatial/transform/streamify/EarlyUnroller.scala:215-276`, `src/spatial/transform/streamify/HierarchicalToStream.scala:156-156`). It produces explicit FIFO structures, `Streaming` schedules, stream wrapping, debug registers marked `dontTouch`, and stop registers for the generated streaming unit pipes (`src/spatial/transform/streamify/HierarchicalToStream.scala:624-631`, `src/spatial/transform/streamify/HierarchicalToStream.scala:778-811`, `src/spatial/transform/streamify/HierarchicalToStream.scala:814-823`). `TimeMap` and `TimeTriplet` are value classes over iterator time, first, and last flags, and `TimeMap.++` propagates nested first/last information into outer triplets (`src/spatial/transform/streamify/TimeMap.scala:7-35`).

## Invariants established

For each transformed inner controller, the original hierarchical execution is split into generated counter/token intake, main execution, and release/output synchronization controllers inside a streaming `UnitPipe` (`src/spatial/transform/streamify/HierarchicalToStream.scala:778-811`). Dependency values crossing controllers are sent through FIFOs rather than direct hierarchical memory visibility, except for memories classified as synchronization memories and skipped by the transformer (`src/spatial/transform/streamify/HierarchicalToStream.scala:737-775`). FIFO initializers are handled later by `FIFOInitializer`, which emits a run-once `UnitPipe` for FIFOs whose `fifoInits` metadata is defined (`src/spatial/transform/streamify/FIFOInitializer.scala:11-39`, `src/spatial/Spatial.scala:138`).

## HLS notes

This is rework for HLS. The source builds a custom streaming protocol with pseudo-iterator FIFOs, token structs, release synchronization, and retime gates, so a direct HLS port should first decide whether to preserve this protocol or map it to `hls::stream` channels with explicit producer/consumer tasks (`src/spatial/transform/streamify/HierarchicalToStream.scala:82-92`, `src/spatial/transform/streamify/HierarchicalToStream.scala:480-672`). `ForceHierarchical` marks every SRAM hierarchical for streamify-specific banking behavior, but it is not currently in the streamify sequence, so the HLS design should not assume that pass runs without resolving Q-pp-13 (`src/spatial/transform/streamify/ForceHierarchical.scala:7-14`, `src/spatial/Spatial.scala:144`).

## Open questions

Q-pp-13 asks whether `EarlyUnroller`, `AccelPipeInserter`, and `ForceHierarchical` are stale, optional, or accidentally omitted from the current `streamify` sequence (`src/spatial/Spatial.scala:123-126`, `src/spatial/Spatial.scala:144`). Q-pp-14 asks how to document superseded streamify files: `FlattenToStream.scala` is line-commented from the package onward, while `StreamingControlBundle.scala` has active package/imports but commented-out object/class definitions (`src/spatial/transform/streamify/FlattenToStream.scala:1-43`, `src/spatial/transform/streamify/StreamingControlBundle.scala:1-29`).
