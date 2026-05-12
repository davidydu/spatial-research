---
type: spec
concept: Spatial IR Metadata - Retiming
source_files:
  - "src/spatial/metadata/retiming/RetimingData.scala:6-53"
  - "src/spatial/metadata/retiming/ValueDelay.scala:5-19"
  - "src/spatial/metadata/retiming/package.scala:9-49"
source_notes:
  - "direct-source-reading"
hls_status: rework
depends_on:
  - "[[00 - Metadata Index]]"
  - "[[10 - Control]]"
  - "[[30 - Memory]]"
status: draft
---

# Retiming

## Summary

Retiming metadata records detected reduction/access cycles, per-symbol delay from a controller start, user/compiler delay annotations, forced latency overrides, and lazy delay-line construction handles (`src/spatial/metadata/retiming/RetimingData.scala:6-53`, `src/spatial/metadata/retiming/ValueDelay.scala:5-19`). It is small but transformer-sensitive: `Cycle` is removed on transfer, `FullDelay` is mirrored, `UserInjectedDelay` is analysis-set, and `ForcedLatency` is user-set (`src/spatial/metadata/retiming/RetimingData.scala:13-53`). The API lives in `RetimingOps`, which provides cycle membership, delay lookup/update, delay-line tracing, user-injected-delay flags, forced-latency accessors, and constant trace conversion (`src/spatial/metadata/retiming/package.scala:9-42`).

## Syntax / API

`Cycle` is an abstract `Data[Cycle](Transfer.Remove)` with `length`, `symbols`, `marker`, `memory`, and `cycleID` fields (`src/spatial/metadata/retiming/RetimingData.scala:6-19`). `WARCycle(reader, writer, memory, symbols, length, marker, cycleID)` represents write-after-read accumulation cycles and overrides its metadata key to `classOf[Cycle]` (`src/spatial/metadata/retiming/RetimingData.scala:21-32`). `AAACycle(accesses, memory, length)` represents access-after-access cycles, exposes `accesses` as `symbols`, uses `AccumMarker.Unknown`, uses `cycleID = -1`, and also keys as `Cycle` (`src/spatial/metadata/retiming/RetimingData.scala:34-40`).

`FullDelay(latency)` is mirrored metadata whose comment defines it as the delay from the start of the parent controller and default `0.0` (`src/spatial/metadata/retiming/RetimingData.scala:43-49`). `UserInjectedDelay(flag)` is `SetBy.Analysis.Self`, and `ForcedLatency(latency)` is `SetBy.User` (`src/spatial/metadata/retiming/RetimingData.scala:51-53`). `ValueDelay(input, delay, size, hierarchy, prev, create)` is not `Data`; it is an analysis/transform helper that can hold a prior delay line and an optional closure for constructing the staged line (`src/spatial/metadata/retiming/ValueDelay.scala:5-12`).

## Semantics

`isInCycle` is true exactly when `metadata[Cycle](s)` is defined, and `reduceCycle` throws when cycle metadata is absent (`src/spatial/metadata/retiming/package.scala:9-13`). `fullDelay` gives priority to `ForcedLatency` when present; otherwise it reads mirrored `FullDelay` and defaults to `0.0` (`src/spatial/metadata/retiming/package.scala:15-21`). `forcedLatency` directly calls `.get.latency`, so callers must check `hasForcedLatency` before reading unless they know the metadata exists (`src/spatial/metadata/retiming/package.scala:33-35`). `trace` recursively strips `DelayLine(_, data)` nodes until it reaches a non-delay symbol, while `isDelayLine` and `isRetimeGate` classify the two retiming node forms (`src/spatial/metadata/retiming/package.scala:23-28`).

`ValueDelay.value()` is side-effectful memoization: the first call invokes `create`, stores the resulting staged symbol in the private mutable `reg`, and returns it; later calls return the memoized symbol (`src/spatial/metadata/retiming/ValueDelay.scala:13-18`). If `create` is absent, `value()` throws, so a `ValueDelay` can be a delayed reference only when the transformer supplied a creation closure (`src/spatial/metadata/retiming/ValueDelay.scala:15-18`). `ValueDelayOrdering` sorts by descending `delay`, which makes larger existing delay lines appear before smaller ones in sorted sets (`src/spatial/metadata/retiming/package.scala:44-46`).

## Implementation

`FullDelay` is immutable as a case class but mutable as metadata: `fullDelay_=` overwrites metadata with a new `FullDelay(d)` (`src/spatial/metadata/retiming/package.scala:15-21`). The current analyzer resets existing delays to `0.0` in block preprocess and then writes computed delays during block retiming, so the field is analysis-time mutable even though the carrier is mirrored metadata (`src/spatial/traversal/RetimingAnalyzer.scala:21-48`). This matters for Rust because recomputing retiming must have a clear pass-owned write phase rather than ambient symbol mutation (inferred, unverified).

The lazy delay-line pattern is ordered around transformer state. The transformer computes `ValueDelay` objects with a `createLine` closure, stores them in `delayLines` and `delayConsumers`, and later registers substitutions by calling `line.value()` (`src/spatial/transform/RetimingTransformer.scala:25-39`, `src/spatial/transform/RetimingTransformer.scala:78-99`). It also precomputes nested delay lines before symbol mirroring so that lines visible outside an inner block are staged in the outer block; this directly depends on `ValueDelay.alreadyExists` and `ValueDelay.value()` (`src/spatial/transform/RetimingTransformer.scala:102-123`, `src/spatial/metadata/retiming/ValueDelay.scala:13-18`). The helper that creates `ValueDelay` chains reuses existing lines when an existing delay is large enough, extends a prior line when more delay is needed, or creates a fresh line when no prior line exists (`src/spatial/util/modeling.scala:589-615`).

## Interactions

Retiming metadata interacts with control timing through `bodyLatency` and `fullDelay`: the retiming analyzer writes symbol delays and sets control body latency for spatial blackbox implementations from the result's full delay (`src/spatial/traversal/RetimingAnalyzer.scala:43-54`, `src/spatial/traversal/RetimingAnalyzer.scala:112-115`). It interacts with memory/accumulator analysis through `Cycle.memory`, `WARCycle.reader`, `WARCycle.writer`, and `AAACycle.accesses`, all of which keep symbol references to the memory cycle participants (`src/spatial/metadata/retiming/RetimingData.scala:21-40`). It interacts with latency modeling through `ForcedLatency`: `fullDelay` itself prioritizes forced latency, and downstream latency models also check `hasForcedLatency` before normal model lookup (`src/spatial/metadata/retiming/package.scala:17-20`, `src/spatial/targets/LatencyModel.scala:18`).

## HLS notes

Cycle classification and full-delay concepts transfer, but the actual delays, delay-line placement, and forced-latency semantics need HLS-specific re-derivation because HLS scheduling and pipeline insertion will not match Chisel delay-line insertion one-for-one (inferred, unverified). The Rust port should replace `ValueDelay`'s side-effectful closure with an explicit delay-line allocation plan, then materialize it in a deterministic transformer phase (`src/spatial/metadata/retiming/ValueDelay.scala:13-18`, `src/spatial/transform/RetimingTransformer.scala:102-123`).

## Open questions

- Q-meta-11: Should `FullDelay` stay mirrored across transforms, or should every Rust/HLS transform invalidate and recompute it?
- Q-meta-12: Can `ValueDelay` be replaced by a pure delay-line plan keyed by input/hierarchy/delay, avoiding closure-ordered staging side effects?
