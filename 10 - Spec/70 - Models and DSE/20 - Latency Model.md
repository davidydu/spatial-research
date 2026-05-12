---
type: spec
concept: Latency Model
source_files:
  - "src/spatial/targets/LatencyModel.scala:10-67"
  - "src/spatial/targets/generic/GenericLatencyModel.scala:11-68"
  - "src/spatial/targets/generic/TileLoadModel.scala:16-109"
  - "models/src/models/CongestionModel.scala:10-124"
  - "models/src/models/ModelData.scala:3-74"
  - "models/src/models/RuntimeModel.scala:251-338"
source_notes:
  - "[[poly-models-dse]]"
hls_status: rework
depends_on:
  - "[[10 - Area Model]]"
status: draft
---

# Latency Model

## Summary

Spatial's latency model combines CSV-backed per-node latency lookup, hand-coded formulas for controller schedules, and special transfer/congestion models. `LatencyModel` is a `SpatialModel[LatencyFields]` whose file name is `<target>_Latency.csv`, resource name is `"Latency"`, and fields come from the target latency schema (`src/spatial/targets/LatencyModel.scala:10-16`). It exposes node latency, reduce-context latency, retime-register predicates, built-in template latency, and controller-level composition models (`src/spatial/targets/LatencyModel.scala:17-67`). The framework is portable, but the numeric data and transfer formulas should be treated as target-specific.

## Syntax or API

`latencyOf(s, inReduce)` returns forced latency when present, otherwise chooses `latencyInReduce(s)` or `latencyOfNode(s)` based on the reduce flag (`src/spatial/targets/LatencyModel.scala:17-23`). `latencyOfNode(s)` is a CSV lookup for `"LatencyOf"`, `latencyInReduce(s)` is `"LatencyInReduce"`, and `builtInLatencyOfNode(s)` is `"BuiltInLatency"` (`src/spatial/targets/LatencyModel.scala:22-46`). The retime-register predicate is split by context: `requiresRegistersInReduce` checks `spatialConfig.addRetimeRegisters && model(s,"RequiresInReduce") > 0`, and `requiresRegisters` checks the same config flag against `"RequiresRegs"` (`src/spatial/targets/LatencyModel.scala:25-34`).

The controller composition API has four formulas. `parallelModel(stages,lhs)` is `stages.max + latencyOfNode(lhs)` (`src/spatial/targets/LatencyModel.scala:48-50`). `streamingModel(N,ii,stages,lhs)` is `stages.max * (N - 1) * ii + latencyOfNode(lhs)` (`src/spatial/targets/LatencyModel.scala:52-55`). `metaPipeModel` adds `stages.sum` to the streaming form, and `sequentialModel` is `stages.sum * N + latencyOfNode(lhs)` (`src/spatial/targets/LatencyModel.scala:56-61`). `outerControlModel` dispatches to metapipe for outer pipe controls, sequential for sequential loops, and streaming otherwise (`src/spatial/targets/LatencyModel.scala:62-66`).

## Semantics

`GenericLatencyModel` overrides `latencyOfNode` only for `DenseTransfer` nodes and delegates all other nodes to the base CSV model (`src/spatial/targets/generic/GenericLatencyModel.scala:37-66`). For stores, it reads contention `c`, transfer parallelism `p`, lens bounds, last-dimension size, and outer iteration product; the base cycles are `size / p`, and overhead is piecewise: below `p < 8`, `1.0 + smallOverhead*p`; otherwise `oFactor*p + (1 - 8*oFactor) + smallOverhead*8`, where `oFactor = 0.02*c - 0.019` and `smallOverhead = 0.0175` only when `c >= 8` (`src/spatial/targets/generic/GenericLatencyModel.scala:37-52`). For loads, it computes dimensions similarly and returns `memoryModel(c,r,b,p) * iters`, with `r` currently hard-coded to `1.0` and `b` set to the last dimension size (`src/spatial/targets/generic/GenericLatencyModel.scala:53-64`).

`memoryModel(c,r,b,p)` applies a logistic overhead by command width: for 96-bit columns the bound is `0.307/(1+exp(-0.096*r+0.21))`, for 192-bit columns the bound is `0.185/(1+exp(-0.24*r-0.8))`, otherwise it uses `0.165` (`src/spatial/targets/generic/GenericLatencyModel.scala:20-28`). It computes `base = ceil((1+overhead)*(110 + r*(53 + cols)))`, then multiplies by `memModel.evaluate(c,r,cols,p)` (`src/spatial/targets/generic/GenericLatencyModel.scala:27-35`). The `memModel` is `TileLoadModel`, whose training imports and model body are entirely commented out and whose `evaluate` method always returns `0.0` (`src/spatial/targets/generic/TileLoadModel.scala:16-27`, `src/spatial/targets/generic/TileLoadModel.scala:68-108`). Therefore, as implemented, load `memoryModel` returns zero regardless of the logistic base calculation (`src/spatial/targets/generic/GenericLatencyModel.scala:30-35`, `src/spatial/targets/generic/TileLoadModel.scala:102-108`).

## Implementation

`CongestionModel` is a separate lattice-regression object over six raw features: loads, stores, gated stores, outer iterations, inner iterations, and bits per cycle (`models/src/models/CongestionModel.scala:10-23`). It defines six feature dimensions, lattice rank six, and lattice size `Seq(3,3,3,3,3,3)`, so there are `3^6 = 729` parameters per lattice (`models/src/models/CongestionModel.scala:24-38`). The parameters and calibrator keypoints are lazily loaded from `ModelData` by schedule string (`models/src/models/CongestionModel.scala:39-52`, `models/src/models/ModelData.scala:3-74`).

Calibration is one-dimensional piecewise-linear interpolation per feature: values below the first input clamp to the first output, values at or above the last input clamp to the last output, and intermediate values linearly interpolate between bracketing keypoints before clamping into `[0, max_dim-1]` (`models/src/models/CongestionModel.scala:54-67`). `calibrate_features` applies that routine to the six features; the `bitsPerCycle` path passes `lattice_size(4)` even though it is the sixth feature, which is harmless for the current uniform shape but fragile if lattice sizes diverge (`models/src/models/CongestionModel.scala:69-79`). `hypercube_features` builds 64 interpolation hypervolumes from residual pairs, computes a flat lattice index for each corner from the calibrated integer origin, and returns the weighted sum of lattice parameters (`models/src/models/CongestionModel.scala:81-113`). `evaluate` stores `typ.toString` in the mutable `model` field, calibrates, interpolates, and hard-clamps to `170 max result.toInt` with the source TODO `"Model is naughty if it returns <170"` (`models/src/models/CongestionModel.scala:115-124`).

The runtime model contains another congestion path. `ControllerModel.congestionModel` has the lattice-regression call commented out, then uses `ModelData.curve_fit(schedule)` and a 15-parameter `fitFunc4` to combine counter contribution, load/store/gated congestion contribution, bits-per-cycle scaling, and a floor of `170 + numel/ticksToDeq` (`models/src/models/RuntimeModel.scala:251-277`, `models/src/models/ModelData.scala:69-73`). This means the standalone `CongestionModel.evaluate` is still real source code, but the generated runtime model path currently uses the curve-fit function instead of the lattice call (`models/src/models/RuntimeModel.scala:251-260`, `models/src/models/RuntimeModel.scala:262-277`).

## Interactions

`DSEThread` obtains latency by calling the target cycle analyzer's `test(paramRewrites)` and then reading `cycleAnalyzer.totalCycles`; the concrete `LatencyAnalyzer` shells out to the compiled runtime-model jar and parses `"Total Cycles for App"` lines (`src/spatial/dse/DSEThread.scala:130-134`, `src/spatial/dse/LatencyAnalyzer.scala:29-47`). Retiming and area interact through `DSEAreaAnalyzer`: delay-line area calls `latenciesAndCycles`, checks `latencyModel.requiresRegisters`, and uses per-node latency to size inserted delay lines (`src/spatial/dse/DSEAreaAnalyzer.scala:66-108`). Thus the latency CSV fields influence both cycle prediction and area overhead from retiming.

## HLS notes

The base API and controller composition are reusable, but the numerical models require rework. CSV node latency fields need HLS operator and schedule latencies, the dense-transfer formulas encode old transfer behavior, the tile-load model is disabled, and congestion coefficients are trained constants in Scala source (`src/spatial/targets/LatencyModel.scala:36-67`, `src/spatial/targets/generic/GenericLatencyModel.scala:20-64`, `src/spatial/targets/generic/TileLoadModel.scala:102-108`, `models/src/models/ModelData.scala:69-73`). The HLS rewrite should either remove the dead tile-load path or replace it with a measured HLS transfer model.

## Open questions

- [[open-questions-poly-models-dse#Q-pmd-06 - 2026-04-24 Dense load latency model replacement|Q-pmd-06]]
- [[open-questions-poly-models-dse#Q-pmd-07 - 2026-04-24 Congestion model source of truth|Q-pmd-07]]
