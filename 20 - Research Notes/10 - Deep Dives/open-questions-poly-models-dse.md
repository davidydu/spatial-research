---
type: open-questions
topic: poly-models-dse
session: 2026-04-24
date_started: 2026-04-24
---

# Open Questions - Poly Models DSE

## Q-pmd-01 - 2026-04-24 ISL set-containment semantics

`ISL.isSuperset` returns `false` and `ISL.intersects` returns `true`, even though both comments say they are used for reaching write calculation. Need decide whether the Rust+HLS rewrite should implement precise set containment/intersection or preserve current conservative behavior.

Source: poly/src/poly/ISL.scala:164-174; src/spatial/metadata/access/AffineData.scala:44-48
Blocked by: reaching-write analysis audit
Status: open
Resolution:

## Q-pmd-02 - 2026-04-24 External solver packaging boundary

The current JVM path lazily compiles `$HOME/bin/emptiness` from `emptiness.c` and libisl, then talks to a singleton subprocess. Need decide whether the rewrite embeds ISL, vendors a solver binary, or keeps an external worker protocol.

Source: poly/src/poly/ISL.scala:14-117
Blocked by: Rust dependency and deployment decision
Status: open
Resolution:

## Q-pmd-03 - 2026-04-24 Constraint replaceKeys offset rule

`ConstraintMatrix.replaceKeys` adds replacement offsets to constraint constants but carries a source TODO questioning whether that is correct. Need validate with examples before porting.

Source: poly/src/poly/ConstraintMatrix.scala:15-23
Blocked by: affine substitution tests
Status: open
Resolution:

## Q-pmd-04 - 2026-04-24 Banking-search pruning strategy for HLS

Banking search expands candidate views, `N` strictness, alpha strictness, duplication, block factors, and `P`, while `NBestGuess.factorize` uses direct divisor enumeration. Need a pruning or memoization plan before larger HLS DSE runs.

Source: src/spatial/metadata/memory/BankingData.scala:547-563; src/spatial/traversal/banking/ExhaustiveBanking.scala:392-431; src/spatial/traversal/banking/MemoryConfigurer.scala:610-633
Blocked by: HLS memory banking design
Status: open
Resolution:

## Q-pmd-05 - 2026-04-24 HLS area model training corpus

The model container and CSV loader transfer, but PMML memory models, fallback constants, RAM heuristics, and DSP rules are target-specific. Need define the HLS measurement corpus and output fields.

Source: models/src/models/AreaEstimator.scala:59-215; src/spatial/targets/AreaModel.scala:85-91; src/spatial/targets/AreaModel.scala:180-205
Blocked by: HLS resource-report format decision
Status: open
Resolution:

## Q-pmd-06 - 2026-04-24 Dense load latency model replacement

`TileLoadModel.evaluate` always returns `0.0`, so the dense-load `memoryModel` path computes a logistic base and then multiplies by zero. Need decide whether to delete, restore, or retrain this path.

Source: src/spatial/targets/generic/GenericLatencyModel.scala:20-35; src/spatial/targets/generic/TileLoadModel.scala:102-108
Blocked by: transfer benchmark data
Status: open
Resolution:

## Q-pmd-07 - 2026-04-24 Congestion model source of truth

The standalone lattice-regression `CongestionModel.evaluate` exists, but `RuntimeModel.ControllerModel.congestionModel` comments out that call and uses `ModelData.curve_fit` instead. Need identify which model should become authoritative.

Source: models/src/models/CongestionModel.scala:115-124; models/src/models/RuntimeModel.scala:251-277; models/src/models/ModelData.scala:69-73
Blocked by: runtime-model validation
Status: open
Resolution:

## Q-pmd-08 - 2026-04-24 Runtime-model replacement for HLS DSE

DSE latency shells out to a compiled Scala runtime-model jar and parses `"Total Cycles for App"`. HLS DSE needs an equivalent cycle source that may come from HLS scheduling reports, simulation, or a new estimator.

Source: src/spatial/dse/LatencyAnalyzer.scala:29-47; src/spatial/dse/DSEAnalyzer.scala:90-147
Blocked by: HLS latency source decision
Status: open
Resolution:

## Q-pmd-09 - 2026-04-24 DSE thread-safety of analyzer state

`threadBasedDSE` creates per-worker states, but the source comments that initialization may not be thread-safe and each worker reruns mutable area/cycle analyzers. Need verify the thread-safety contract before carrying this worker model forward.

Source: src/spatial/dse/DSEAnalyzer.scala:320-350; src/spatial/dse/DSEThread.scala:56-77; src/spatial/dse/DSEThread.scala:136-151
Blocked by: parallel DSE stress test
Status: open
Resolution:
