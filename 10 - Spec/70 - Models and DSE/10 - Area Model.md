---
type: spec
concept: Area Model
source_files:
  - "models/src/models/Model.scala:5-79"
  - "models/src/models/Fields.scala:5-17"
  - "models/src/models/package.scala:3-85"
  - "models/src/models/LinearModel.scala:6-114"
  - "models/src/models/AffArith.scala:3-23"
  - "models/src/models/AreaEstimator.scala:10-263"
  - "src/spatial/targets/SpatialModel.scala:11-117"
  - "src/spatial/targets/AreaModel.scala:15-208"
  - "src/spatial/targets/NodeParams.scala:16-70"
source_notes:
  - "[[poly-models-dse]]"
hls_status: rework
depends_on:
  - "[[30 - Banking Math]]"
status: draft
---

# Area Model

## Summary

Spatial's area model has two layers: generic model containers in `models`, and target-specific model loading and node dispatch in `spatial.targets`. `Model[T,F[A] <: Fields[A,F]]` is a schema-plus-entries record with a name, parameter list, output-field map, and implicit field configuration (`models/src/models/Model.scala:5-10`, `models/src/models/Fields.scala:5-17`). The package aliases define `Area = Model[Double,AreaFields]` and `NodeArea = Model[NodeModel,AreaFields]`, where `NodeModel = Either[LinearModel,Double]` allows CSV cells to be either symbolic linear expressions or constants (`models/src/models/package.scala:3-10`). The HLS rewrite should preserve this separation but retrain or replace the coefficients.

## Syntax or API

`Model` exposes `keys`, `nonZeroFields`, zero-default `apply(field)`, `toSeq`, `seq(keys*)`, `map`, `zip`, and pointwise arithmetic through `AffArith[T]` (`models/src/models/Model.scala:7-43`). Its comparison semantics are field-wise but asymmetric: `<` and `<=` require all fields to satisfy the relation, while `>` and `>=` require any field to satisfy the relation so that `!(a < b)` lines up with `a >= b` (`models/src/models/Model.scala:45-57`). `AffArith` has instances for `Double` and `LinearModel`, so area vectors can be combined whether they are numeric or symbolic (`models/src/models/AffArith.scala:3-23`).

`LinearModel` is a sum of `Prod(a, xs)` terms plus an explicit variable set (`models/src/models/LinearModel.scala:6-23`). Products multiply or divide by constants, append variables, and evaluate by multiplying all named variable values (`models/src/models/LinearModel.scala:6-18`). `LinearModel` supports scalar arithmetic, model addition/subtraction by merging like variable lists, `<->` for subtracting only overlapping terms from the left variable universe, `eval`, `exactEval`, `partial`, `fractional`, and `cleanup` (`models/src/models/LinearModel.scala:21-83`). `LinearModel.fromString` parses CSV expressions by splitting on `+` and `*`, separating numeric factors from variable names, and returning `Left(model)` when variables exist or `Right(sum)` when all terms are numeric (`models/src/models/LinearModel.scala:98-113`).

## Semantics

`SpatialModel[F]` is the abstract CSV-backed model loader used by both area and latency models. It derives a `FILE_NAME`, `RESOURCE_NAME`, and field definitions from the concrete subclass, then lazily calls `loadModels()` during `init()` (`src/spatial/targets/SpatialModel.scala:11-34`). Lookup can be direct by CSV name or by IR symbol; symbol lookup calls `nodeParams(sym, op)` to translate the IR node into a CSV row name plus numeric arguments (`src/spatial/targets/SpatialModel.scala:38-60`). Missing CSV rows are recorded through `miss`, and `reportMissing` prints a target-specific warning listing the missing models (`src/spatial/targets/SpatialModel.scala:24-29`, `src/spatial/targets/SpatialModel.scala:63-70`).

`loadModels()` first tries `Source.fromResource("models/" + FILE_NAME)` and then `$SPATIAL_HOME/models/<FILE_NAME>` (`src/spatial/targets/SpatialModel.scala:74-84`). It treats the first row as headings, finds parameter columns by locating the last heading starting with `Param`, finds output columns by matching `FIELDS`, parses each row into `Model.fromArray[NodeModel,F]`, and parses every output cell with `LinearModel.fromString` (`src/spatial/targets/SpatialModel.scala:86-107`). `AreaModel` sets `FILE_NAME` to `<target>_Area.csv`, uses target area fields, and defines `NoArea` as an empty area model (`src/spatial/targets/AreaModel.scala:15-28`).

## Implementation

`AreaEstimator` is the memory and arithmetic estimator behind target area. It caches PMML evaluators by `(nodetype, prop)` and records failed model loads in a mutable set (`models/src/models/AreaEstimator.scala:10-17`). PMML files are read from `$SPATIAL_HOME/models/resources/<nodetype>_<prop>.pmml` and loaded with `jpmml-evaluator` through `LoadingModelEvaluatorBuilder`, with evaluator verification before use (`models/src/models/AreaEstimator.scala:48-57`, `models/src/models/AreaEstimator.scala:171-180`). For memory estimates, it pads `dims`, `B`, `N`, `alpha`, and `P` to a node-type-specific width, truncates or pads read/write histograms to nine values, warns on impossible zero-bank histogram entries, and feeds the resulting vector to the evaluator (`models/src/models/AreaEstimator.scala:155-201`).

When ML is disabled or unavailable, `estimateMem` falls back to `crudeEstimateMem` (`models/src/models/AreaEstimator.scala:203-215`). The fallback uses fixed magic costs `mulCost=6`, `divCost=20`, `modCost=20`, `muxCost=6`, and `volumePenalty=1` (`models/src/models/AreaEstimator.scala:59-66`). It partitions access histograms into directly banked and crossbar-banked readers and writers, adds penalties for non-power-of-two offset dividers and multipliers, non-power-of-two bank multipliers and moduli, memory muxes, and physical size (`models/src/models/AreaEstimator.scala:68-131`). `estimateArithmetic` uses the same PMML-loading path for operation models and returns `0.0` on missing or failed models (`models/src/models/AreaEstimator.scala:217-263`).

`AreaModel.areaOfMem` currently estimates memories before full banking analysis by assuming flat banking with `B = Seq(1)`, `N = biggest unrolled reader/writer group`, `alpha = all ones`, and `P = all ones` (`src/spatial/targets/AreaModel.scala:60-85`). It calls the ML estimator for LUTs and FFs, then hard-codes RAM36 as `N.head * ceil(dims.product/(N.head*36000)) * (depth+1)` and RAM18 as zero because the comment says the trained RAM models gave unrealistically large results (`src/spatial/targets/AreaModel.scala:85-91`). `areaOfNode` returns no area for non-synthesizable or host/transient/accessor nodes, routes memory allocations to `areaOfMem`, models delay lines as registers, and counts one DSP for non-constant or non-power-of-two fixed multiply/divide/modulo cases (`src/spatial/targets/AreaModel.scala:161-190`). `areaOfDelayLine` computes a register-area value but returns only `Area("Regs" -> length * par)`, so bit width is logged but not reflected in the returned register count (`src/spatial/targets/AreaModel.scala:193-205`).

`NodeParams.nodeParams` is the op-to-CSV-key dispatch. It log2-corrects `RegAccumFMA` and `RegAccumOp` models through `layers`, `drain`, and `correction` parameters; fixed-point ops pass bit width as `b`, floating-point ops pass no params, and delay lines report `d` only for user-injected delays (`src/spatial/targets/NodeParams.scala:24-42`). It maps muxes, one-hot muxes, priority muxes, blackboxes, async SRAM reads, `Switch`, `CounterNew`, `CounterChainNew`, and generic controls to CSV keys, with outer controls keyed by raw schedule string and child-stage count `n` (`src/spatial/targets/NodeParams.scala:43-66`).

## Interactions

Banking cost calls `AreaEstimator.estimateMem` and `estimateArithmetic` using access histograms derived from `AccessMatrix.bankMuxWidth` and auxiliary arithmetic from `AccessMatrix.arithmeticNodes` (`src/spatial/traversal/banking/MemoryConfigurer.scala:448-487`). DSE area aggregation reruns `DSEAreaAnalyzer`, which calls target `areaModel.areaOf` throughout accelerator traversal and compares the summarized area against target capacity in `DSEThread` (`src/spatial/dse/DSEAreaAnalyzer.scala:62-67`, `src/spatial/dse/DSEThread.scala:119-123`).

## HLS notes

The schema, CSV loading, symbolic linear expressions, and per-node dispatch framework are reusable in HLS. The coefficients, PMML memory models, RAM heuristics, DSP assumptions, and delay-line accounting need HLS-specific retraining or replacement because they encode the old Spatial target and Chisel-era device assumptions (`models/src/models/AreaEstimator.scala:155-215`, `src/spatial/targets/AreaModel.scala:85-91`, `src/spatial/targets/AreaModel.scala:180-205`). The fallback magic constants should be documented as last-resort estimates, not design truths (`models/src/models/AreaEstimator.scala:59-66`).

## Open questions

- [[open-questions-poly-models-dse#Q-pmd-05 - 2026-04-24 HLS area model training corpus|Q-pmd-05]]
