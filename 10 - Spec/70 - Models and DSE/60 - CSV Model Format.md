---
type: spec
concept: CSV Model Format
source_files:
  - "src/spatial/targets/SpatialModel.scala:11-117"
  - "src/spatial/targets/AreaModel.scala:15-28"
  - "src/spatial/targets/LatencyModel.scala:10-67"
  - "src/spatial/targets/NodeParams.scala:24-67"
  - "src/spatial/targets/HardwareTarget.scala:14-26"
  - "models/src/models/Model.scala:5-79"
  - "models/src/models/Fields.scala:5-17"
  - "models/src/models/LinearModel.scala:6-114"
  - "models/src/models/package.scala:3-85"
source_notes:
  - "[[poly-models-dse]]"
hls_status: clean
hls_reason: "The framework transfers; cost data must be retargeted"
depends_on:
  - "[[10 - Area Model]]"
  - "[[20 - Latency Model]]"
status: draft
---

# CSV Model Format

## Summary

`SpatialModel[F]` is the shared CSV-backed loader for area and latency model tables, parameterized by a `Fields` family and mixed with `NodeParams` for IR-node dispatch (`src/spatial/targets/SpatialModel.scala:11-20`). It defines `ResModel = Model[NodeModel,F]`, where `NodeModel` is `Either[LinearModel, Double]`, so a CSV cell may be a symbolic linear expression or a constant (`src/spatial/targets/SpatialModel.scala:11-13`, `models/src/models/package.scala:3-9`). `AreaModel` sets `FILE_NAME` to `<target.name>_Area.csv`, `RESOURCE_NAME` to `"Area"`, and `FIELDS` to `target.AFIELDS` (`src/spatial/targets/AreaModel.scala:15-23`). `LatencyModel` sets `FILE_NAME` to `<target.name>_Latency.csv`, `RESOURCE_NAME` to `"Latency"`, and `FIELDS` to `target.LFIELDS` (`src/spatial/targets/LatencyModel.scala:10-16`).

## Mechanism

Model initialization is lazy and one-shot: `needsInit` starts true, `init()` calls `loadModels()` only while that flag is true, and the flag is then set false (`src/spatial/targets/SpatialModel.scala:24-34`). Direct name lookup calls `models.get(name).map(_.eval(args:_*))`, records a miss on absence, and returns `NONE` when the row is missing (`src/spatial/targets/SpatialModel.scala:38-52`). Symbol lookup ignores `Expect` placeholders, dispatches `Op(op)` through `nodeParams(sym, op)`, and evaluates the returned CSV key with the returned numeric arguments (`src/spatial/targets/SpatialModel.scala:53-61`). `miss(str)` accumulates warnings only while `recordMissing` is true, and `reportMissing()` warns with the target name, resource name, missing row strings, and target CSV file name (`src/spatial/targets/SpatialModel.scala:24-29`, `src/spatial/targets/SpatialModel.scala:63-70`).

`loadModels()` first tries `Source.fromResource("models/" + FILE_NAME)` and then tries `$SPATIAL_HOME/models/<FILE_NAME>` (`src/spatial/targets/SpatialModel.scala:74-84`). The first CSV row is treated as headings, `nParams` is computed as the last heading whose name starts with `Param` plus one, and output indices are headings whose names are contained in `FIELDS` (`src/spatial/targets/SpatialModel.scala:86-90`). The loader computes `FIELDS diff fields` and warns when expected target fields are absent from the CSV, then proceeds with whatever selected field columns exist (`src/spatial/targets/SpatialModel.scala:90-95`). Extra CSV headings outside `FIELDS` are ignored because they are not included in `indices` (`src/spatial/targets/SpatialModel.scala:87-101`). Each data row uses the first cell as the model name, cells `1 until nParams` as non-empty parameter names, selected output cells as `LinearModel.fromString` entries, and `Model.fromArray[NodeModel,F]` to build the row model (`src/spatial/targets/SpatialModel.scala:96-103`).

## Implementation

`Model[T,F]` stores `name`, `params`, and a field-keyed `entries` map under an implicit `Fields` config (`models/src/models/Model.scala:5-10`). `Model.apply(field)` returns the configured default when a field is absent, and `toSeq` serializes values in configured field order (`models/src/models/Model.scala:25-27`). `Model.fromArray` zips `config.fields` with the parsed entries array, so entry order is determined by the target field schema rather than the raw CSV column order after selection (`models/src/models/Model.scala:76-78`). `AreaFields` and `LatencyFields` are the two `Fields` implementations, each carrying an ordered field array and a default value (`models/src/models/Fields.scala:5-17`).

`LinearModel.fromString` parses a CSV cell by splitting on `+`, splitting each term on `*`, partitioning numeric factors from variable names, and producing `Left(LinearModel)` when any variables are present or `Right(sum)` when the cell is numeric-only (`models/src/models/LinearModel.scala:98-113`). A `Prod` evaluates by multiplying its coefficient by the supplied values for every variable name, and `LinearModel.eval` sums product evaluations (`models/src/models/LinearModel.scala:6-18`, `models/src/models/LinearModel.scala:55-58`). `NodeModelOps.eval` clamps both symbolic and numeric results to `Math.max(0.0, value)`, so negative CSV formulas are floored at zero during model evaluation (`models/src/models/package.scala:30-35`). `ModelNodeModelOps.eval` maps every field of a `Model[NodeModel,F]` through that node-model evaluation path (`models/src/models/package.scala:80-84`).

The latency field schema is fixed in `HardwareTarget` as `RequiresRegs`, `RequiresInReduce`, `LatencyOf`, `LatencyInReduce`, and `BuiltInLatency` (`src/spatial/targets/HardwareTarget.scala:14-16`, `src/spatial/targets/HardwareTarget.scala:52-58`). Area fields are target-specific through `AFIELDS`, and the target also builds implicit `AreaFields`, `LatencyFields`, `AreaFields[NodeModel]`, and `LatencyFields[NodeModel]` values from those arrays (`src/spatial/targets/HardwareTarget.scala:14-26`). `AreaModel` consumes CSV rows through helpers such as `RegArea`, `MuxArea`, and `areaOf(e,d,...)`, which route to `model("Reg")`, `model("Mux")`, and `areaOfNode` under hardware and reduce-context guards (`src/spatial/targets/AreaModel.scala:24-35`). `LatencyModel` consumes CSV rows through `latencyInReduce`, `requiresRegistersInReduce`, `requiresRegisters`, `latencyOfNode`, and `builtInLatencyOfNode`, each of which queries a named latency field through `model(sym, key)` (`src/spatial/targets/LatencyModel.scala:17-46`).

`NodeParams.nodeParams` is the source of most CSV row keys and parameter names. It maps `RegAccumFMA` to `op.name` with `b`, log2-scaled `layers`, `drain = 1`, and a small-bit `correction`; it maps multiply reductions to `op.name + "Mul"` with a different drain value; and it maps other reductions to `op.name` with a smaller log2-scaled layer model and `drain = nbits / 32` (`src/spatial/targets/NodeParams.scala:24-36`). It maps fixed-point ops to `op.name` with bit width `b`, floating-point ops to `op.name` with no params, user-injected delay lines to `DelayLine(d)`, mux families to bit-width or selector-count params, blackboxes to latency params, async SRAM reads to async row names, switches to `SwitchMux` or `Switch`, counters to `Counter` or `CounterChain`, controls to raw schedule names with stage count `n`, and all other ops to `op.productPrefix` (`src/spatial/targets/NodeParams.scala:37-67`).

## Interactions

The CSV file name is target-name-derived, so a target named `"Zynq"` expects `Zynq_Area.csv` and `Zynq_Latency.csv` on the resource classpath under `models/` or under `$SPATIAL_HOME/models/` (`src/spatial/targets/AreaModel.scala:18-23`, `src/spatial/targets/LatencyModel.scala:10-16`, `src/spatial/targets/SpatialModel.scala:74-84`). Missing rows return zero/default resource models but are accumulated for later reporting, so model coverage problems are warnings unless a downstream consumer treats zero area or zero latency as invalid (`src/spatial/targets/SpatialModel.scala:36-52`, `src/spatial/targets/SpatialModel.scala:63-70`). The loader's warning direction means target `FIELDS` should include all intended output columns, but source code warns about expected fields absent from the CSV rather than warning about CSV columns absent from the target field set (`src/spatial/targets/SpatialModel.scala:87-95`).

## HLS notes

The CSV framework is portable because it already separates file discovery, parameterized linear formulas, field schemas, and IR-node-to-row dispatch (`src/spatial/targets/SpatialModel.scala:74-103`, `models/src/models/LinearModel.scala:98-113`, `src/spatial/targets/NodeParams.scala:24-67`). The cost data is not portable because target names choose target-specific CSV files and target schemas choose the resource fields (`src/spatial/targets/AreaModel.scala:18-23`, `src/spatial/targets/LatencyModel.scala:10-16`, `src/spatial/targets/HardwareTarget.scala:14-26`). The HLS path should keep the loader and retarget CSV contents, row keys, and field schemas to HLS operator/resource reports (inferred, unverified).

## Open questions

- [[open-questions-models-dse-fringe-gaps#Q-mdf-03 - 2026-04-24 HLS CSV field schema and report mapping|Q-mdf-03]]
- [[open-questions-models-dse-fringe-gaps#Q-mdf-04 - 2026-04-24 CSV loader strictness for extra and missing fields|Q-mdf-04]]
