---
type: spec
concept: Design Space Exploration
source_files:
  - "src/spatial/dse/DSEMode.scala:3-10"
  - "src/spatial/dse/ParameterAnalyzer.scala:12-194"
  - "src/spatial/dse/SpaceGenerator.scala:11-80"
  - "src/spatial/metadata/params/DSEData.scala:9-219"
  - "src/spatial/dse/DSEAnalyzer.scala:23-486"
  - "src/spatial/dse/PruneWorker.scala:11-30"
  - "src/spatial/dse/DSEThread.scala:12-153"
  - "src/spatial/dse/DSEWriterThread.scala:6-53"
  - "src/spatial/dse/DSEAreaAnalyzer.scala:15-246"
  - "src/spatial/dse/LatencyAnalyzer.scala:10-64"
  - "src/spatial/dse/HyperMapperDSE.scala:12-202"
  - "src/spatial/dse/HyperMapperReceiver.scala:14-122"
  - "src/spatial/dse/HyperMapperSender.scala:6-69"
  - "models/src/models/RuntimeModel.scala:313-338"
source_notes:
  - "[[poly-models-dse]]"
hls_status: rework
depends_on:
  - "[[10 - Area Model]]"
  - "[[20 - Latency Model]]"
status: draft
---

# Design Space Exploration

## Summary

Spatial DSE discovers tunable parameters, builds finite domains, optionally prunes invalid combinations, evaluates area and latency for candidate points, and writes CSV results. The mode enum has five values: `Disabled`, `Heuristic`, `Bruteforce`, `HyperMapper`, and `Experiment` (`src/spatial/dse/DSEMode.scala:3-10`). `DSEAnalyzer.process` constructs integer and controller domains, compiles the generated runtime model, dispatches by mode, and finally freezes tile-size, parallelization, and pipeline parameters to concrete values (`src/spatial/dse/DSEAnalyzer.scala:23-88`). The framework should carry into HLS, but the analyzers and runtime model need new HLS-specific estimators.

## Syntax or API

`ParameterAnalyzer` is the discovery pass. It records the top accelerator controller at `AccelScope`, copies argument input bounds through `SetReg`, ignores parameterized FIFO depths with a warning, and adds SRAM and RegFile dimensions to `TileSizes` when they contain `Expect` parameters (`src/spatial/dse/ParameterAnalyzer.scala:44-67`, `src/spatial/metadata/params/DSEData.scala:9-31`). Dense and sparse transfers add parameterized parallelization factors to `ParParams`, while non-parameter parallelization values are written as int values (`src/spatial/dse/ParameterAnalyzer.scala:68-77`, `src/spatial/metadata/params/DSEData.scala:34-44`). `CounterNew` collects parameterized starts, ends, steps, and pars, and adds restrictions such as less-than-or-equal, divides, divides-constant, and divides-quotient according to counter shape (`src/spatial/dse/ParameterAnalyzer.scala:78-168`, `src/spatial/metadata/params/DSEData.scala:91-138`). `OpForeach`, `OpReduce`, and `OpMemReduce` add cchain parallelization parameters and add outer controls without user schedules to `PipelineParams` (`src/spatial/dse/ParameterAnalyzer.scala:170-189`, `src/spatial/metadata/params/DSEData.scala:46-56`).

`SpaceGenerator.createIntSpace` converts tile-size and parallelization params into `Domain[Int]` values and currently leaves its prototype single-parameter pruning disabled through `PRUNE = false` (`src/spatial/dse/SpaceGenerator.scala:11-63`). `createCtrlSpace` converts metapipe toggles into `Domain[Boolean]` over `[false,true]`, with setters that write `Pipelined` or `Sequenced` schedules and a categorical uniform prior for HyperMapper (`src/spatial/dse/SpaceGenerator.scala:65-79`). `Domain[T]` contains name, id, options, setter, getter, and space type; it can set by option index, set an unsafe value, filter options by a stateful predicate, and serialize option/default/prior strings for HyperMapper (`src/spatial/metadata/params/DSEData.scala:139-185`). `Domain.apply` builds ordinal domains from either ranges or explicit integer sequences, and `Domain.restricted` builds an already-filtered integer domain (`src/spatial/metadata/params/DSEData.scala:189-218`).

## Semantics

Heuristic DSE first prunes each domain by restrictions that depend only on that parameter, computes the Cartesian product size, and rejects spaces larger than `Int.MaxValue` (`src/spatial/dse/DSEAnalyzer.scala:149-186`, `src/spatial/dse/DSEAnalyzer.scala:280-282`). For legal spaces, it launches `PruneWorker` tasks across `spatialConfig.threads`; each worker maps a linear index into domain option indices, sets each domain, evaluates all multi-parameter restrictions, and pushes valid point indices into a `LinkedBlockingQueue[Seq[Int]]` (`src/spatial/dse/DSEAnalyzer.scala:204-231`, `src/spatial/dse/PruneWorker.scala:11-30`). The legal points are shuffled and capped at 75,000 for normal heuristic mode, while experiment mode runs ten shuffled trials capped at 100,000 and exits the process afterward (`src/spatial/dse/DSEAnalyzer.scala:238-278`).

`threadBasedDSE` performs the point evaluation. It creates a bounded work queue of `Seq[DesignPoint]`, a bounded output queue of CSV row arrays, a worker pool of `DSEThread`s, and a single `DSEWriterThread` (`src/spatial/dse/DSEAnalyzer.scala:285-363`). The caller fills the work queue with batches and then poisons it with empty sequences, and the master later poisons the file queue with an empty array (`src/spatial/dse/DSEAnalyzer.scala:369-397`). `DSEWriterThread` prints a header plus timestamp column, writes every row array, flushes, and reports progress every 5000 rows (`src/spatial/dse/DSEWriterThread.scala:18-52`). After completion, `threadBasedDSE` reloads the CSV, sorts rows by `Cycles`, prints top and bottom samples, and runs `Sensitivity.around` around the current parameter center when possible (`src/spatial/dse/DSEAnalyzer.scala:399-439`).

## Implementation

`DSEThread` precomputes capacity fields and domain products, lazily constructs scalar, memory, area, and cycle analyzers, and initializes them under a copied `State` (`src/spatial/dse/DSEThread.scala:48-77`). For each batch, it first builds param rewrite sequences, calls `cycleAnalyzer.test(paramRewrites)`, then for every point sets the domains, reruns area analysis, checks `area <= capacity && !state.hadErrors`, and emits parameters, selected area fields, cycles, validity, and elapsed timestamp (`src/spatial/dse/DSEThread.scala:109-151`). Scalar, memory, and contention reruns are commented out in `evaluate`, so area rerun and runtime-model latency are the active per-point analyses (`src/spatial/dse/DSEThread.scala:136-151`).

`DSEAreaAnalyzer` aggregates area through accelerator traversal. `preprocess` clears scope area, resets reduce state, and resets missing-area tracking; `postprocess` folds saved and scoped area, calls `areaModel.summarize`, and stores `totalArea` (`src/spatial/dse/DSEAreaAnalyzer.scala:43-60`). Inner blocks add delay-line area from `pipeDelayLineArea`, which computes latencies and cycles, derives per-input retiming sizes from critical path and required-register predicates, keeps the maximum delay per input, and sums `areaOfDelayLine` (`src/spatial/dse/DSEAreaAnalyzer.scala:66-124`). Reductions add map area, reduction-tree area, delay-line area from `reductionTreeDelays`, and load/reduce/store cycle areas; memory reductions do the analogous map/tree/cycle aggregation with map and reduce parallelism (`src/spatial/dse/DSEAreaAnalyzer.scala:157-213`).

`LatencyAnalyzer.test` locates a `RuntimeModel-assembly` jar under `$gen_dir/model`, batches parameter rewrites in groups of 1000, runs `java -jar <jar> ni <batched tune commands>`, and parses lines containing `"Total Cycles for App"` into `totalCycles`, mapping negative raw values to `Long.MaxValue` (`src/spatial/dse/LatencyAnalyzer.scala:10-47`). `DSEAnalyzer.compileLatencyModel` requires `model_dse.scala`, locks `model_dse.scala.lock`, runs `bash scripts/assemble.sh` in the generated directory, and releases the lock afterward (`src/spatial/dse/DSEAnalyzer.scala:90-147`). This makes DSE latency an out-of-process compiled model rather than an in-memory analyzer.

HyperMapper mode emits a JSON config into `config.cwd/dse_hm`, including application name, random-forest model settings, client-server mode, objective names `Slices` and `Cycles`, feasible output `Valid`, DOE sample count, and one JSON input-parameter block per `Domain` (`src/spatial/dse/HyperMapperDSE.scala:52-104`). It starts `python $HYPERMAPPER_HOME/scripts/hypermapper.py <json>` through `BackgroundProcess`, then launches receiver and sender communication threads over buffered pipes (`src/spatial/dse/HyperMapperDSE.scala:127-158`). The receiver reads `Request n` or `FRequest n file`, parses point CSV rows into `Point` objects, and poisons queues at end; the sender responds with the result header and rows, writing `.out` files and ACKs for file requests (`src/spatial/dse/HyperMapperReceiver.scala:27-112`, `src/spatial/dse/HyperMapperSender.scala:28-67`).

The generated runtime model's `ControllerModel.cycsPerParent` has 11 schedule cases across `CtrlLevel` and `CtrlSchedule`. Outer `Sequenced`, `Pipelined`, `ForkJoin`, `Streaming`, `Fork`, dense transfers, and sparse transfers each have explicit equations or calls; inner `Sequenced` is `cchainIters*L + startup + shutdown`, and inner non-sequenced is `(cchainIters - 1)*II + L + startup + shutdown + dpMask` (`models/src/models/RuntimeModel.scala:313-338`). Dense load, dense store, and gated dense store use `congestionModel(competitors())`, while sparse load/store return `1` with TODO comments (`models/src/models/RuntimeModel.scala:328-337`).

## Interactions

DSE uses area capacity from the target, latency from the compiled runtime model, and parameter metadata from `DSEData` globals (`src/spatial/dse/DSEThread.scala:48-61`, `src/spatial/metadata/params/DSEData.scala:9-88`). Runtime bottlenecks are explicit: heuristic mode enumerates all legal point indices before sampling, and banking search elsewhere remains exhaustive over view, `N`, alpha, duplication, and block choices before DSE reaches stable area estimates (`src/spatial/dse/DSEAnalyzer.scala:186-231`, `src/spatial/traversal/banking/MemoryConfigurer.scala:610-633`, `src/spatial/traversal/banking/ExhaustiveBanking.scala:392-431`). `NBestGuess.factorize` is O(N) per divisor list, and its repeated use inside banking candidate expansion is a known scaling risk for larger memories (`src/spatial/metadata/memory/BankingData.scala:547-563`).

## HLS notes

The DSE architecture is reusable: discover parameters, build domains, evaluate area/cycles, and write CSV or HyperMapper responses. The rework is in the analyzers and runtime model: HLS cycle estimation should not depend on the old generated Scala runtime jar, and HLS area should use HLS reports or HLS-trained resource estimators (`src/spatial/dse/LatencyAnalyzer.scala:29-47`, `src/spatial/dse/DSEAreaAnalyzer.scala:62-124`). The queue-based worker/writer design and HyperMapper pipe protocol can carry over (`src/spatial/dse/DSEAnalyzer.scala:312-397`, `src/spatial/dse/HyperMapperDSE.scala:127-158`).

## Open questions

- [[open-questions-poly-models-dse#Q-pmd-08 - 2026-04-24 Runtime-model replacement for HLS DSE|Q-pmd-08]]
- [[open-questions-poly-models-dse#Q-pmd-09 - 2026-04-24 DSE thread-safety of analyzer state|Q-pmd-09]]
