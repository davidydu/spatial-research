---
type: "research"
decision: "D-06"
angle: 6
---

# Policy Options

## Baseline

Spatial currently treats `iterDiff` as both analysis metadata and an initiation-interval input. The metadata is `IterDiff(diff: Int)`, set by analysis with a default getter value of `1` (`src/spatial/metadata/memory/AccumulatorData.scala:82-87`, `src/spatial/metadata/memory/package.scala:26-29`). The main compiler flow runs `accessAnalyzer` before `iterationDiffAnalyzer` in `bankingAnalysis`, then runs final `initiationAnalyzer` after retiming and broadcast cleanup (`src/spatial/Spatial.scala:140-144`, `src/spatial/Spatial.scala:227-233`). That ordering matters: access analysis creates affine access matrices (`src/spatial/traversal/AccessAnalyzer.scala:215-225`), and iteration-diff analysis consumes those matrices when comparing reader/writer distances (`src/spatial/traversal/IterationDiffAnalyzer.scala:28-33`, `src/spatial/traversal/IterationDiffAnalyzer.scala:70-81`).

The current assumptions are narrow. Unknown counter bounds trigger warnings and either conservatism, `--looseIterDiffs`, or user-specified II (`src/spatial/traversal/IterationDiffAnalyzer.scala:37-56`, `src/spatial/Spatial.scala:440-442`). The code also has TODOs around writer-leading-reader cases, different control hierarchy levels, and lane-distance assumptions (`src/spatial/traversal/IterationDiffAnalyzer.scala:36`, `src/spatial/traversal/IterationDiffAnalyzer.scala:63-71`). Consumers are real: `InitiationAnalyzer` collects statement `iterDiff`s, derives `compilerII`, then sets `II` unless user schedule/user II overrides it (`src/spatial/traversal/InitiationAnalyzer.scala:29-40`). The tree report highlights `II` versus `CompilerII` mismatches (`src/spatial/codegen/treegen/TreeGen.scala:126-131`), and runtime-model generation serializes `lhs.II` into controller models (`src/spatial/model/RuntimeModelGenerator.scala:261-265`).

## Option A: Exact Reuse As Scheduler Authority

Exact reuse means the Rust/HLS scheduler ports Spatial's access matrices, accumulation-cycle finder, iteration-diff formulas, and `InitiationAnalyzer` equation, then treats the resulting II as authoritative. The strongest argument is compatibility: Spatial already distinguishes `userII`, `compilerII`, and final `II` (`src/spatial/metadata/control/ControlData.scala:153-177`), and user `Pipe.II(ii)` flows into `userII` through `CtrlOpt` (`src/spatial/lang/control/Control.scala:22-30`, `src/spatial/lang/control/CtrlOpt.scala:18-21`). Existing tests also encode expectations for conservative iteration-diff behavior (`test/spatial/tests/compiler/InitiationIntervals.scala:325-330`).

The weakness is that this would make old Spatial heuristics responsible for a new backend. The algorithm depends on Spatial-specific affine/lane metadata, local memory cycle discovery, and retiming gates (`src/spatial/util/modeling.scala:144-179`). It reduces recurrence distance to `ceil(interval / minIterDiff)` rather than modeling an HLS tool's actual dependence graph, array partitioning, or accepted pipeline result (`src/spatial/traversal/InitiationAnalyzer.scala:25-40`). General HLS compilers may reject, relax, or reinterpret requested pipeline II based on their own dependence and resource schedulers (unverified). Exact authority therefore maximizes parity but has the highest silent-divergence risk.

## Option B: Diagnostic-Only Carryover

Diagnostic-only carryover keeps `iterDiff` as a compatibility lint and explanatory signal, but removes it from the HLS scheduling contract. This preserves useful messages for unknown bounds, loose mode, and explicit user II (`src/spatial/traversal/IterationDiffAnalyzer.scala:42-53`) while avoiding the claim that Spatial's recurrence estimate is the backend truth. It also matches existing report plumbing: Spatial already has separate `compilerII` and final `II` presentation in controller-tree output (`src/spatial/codegen/treegen/TreeGen.scala:126-131`).

The cost is semantic clarity. In current Spatial, `II` is "used for control signal generation," not just a note (`src/spatial/metadata/control/ControlData.scala:153-159`). A diagnostic-only policy must introduce distinct fields such as `requested_ii`, `spatial_iter_diff`, and `hls_accepted_ii`, or it will accidentally preserve authority through old metadata names. It is low-risk for migration, but incomplete as the long-term scheduler.

## Option C: Replace With An HLS Dependence/Schedule Model

Replacement means `iterDiff` can be an input feature, but the authoritative scheduler models HLS-visible dependences, memory resources, partitions, pragmas, operator latencies, and backend reports. This is the cleanest semantic fit for Rust+HLS because Spatial schedules include `Sequenced`, `Pipelined`, `Streaming`, `ForkJoin`, `Fork`, and `PrimitiveBox` categories (`src/spatial/metadata/control/ControlData.scala:7-14`), while flow rules already rewrite default and illegal schedules before codegen (`src/spatial/flows/SpatialFlowRules.scala:317-370`). The HLS model should own the equivalent legality and requested-II decisions.

The downside is scope. Runtime and DSE currently consume controller `II` in schedule equations, especially inner controls where cycles are `(cchainIters - 1)*II + L + ...` (`models/src/models/RuntimeModel.scala:192-200`, `models/src/models/RuntimeModel.scala:334-337`). Replacing `iterDiff` therefore requires report parsing, simulator/DSE reconciliation, and tests across reductions, retiming, unrolling, and memory partitioning.

## Hybrid Recommendation

Do not choose exact reuse as final authority. Prefer replacement as the D-06 destination, with a staged hybrid: run Spatial-style `iterDiff` for conservative requested II and diagnostics, but make HLS backend reports authoritative for accepted II and final performance (unverified). In the hybrid, `iterDiff <= 0` and unknown-bound cases should still request conservative treatment or warn, following current behavior (`src/spatial/traversal/IterationDiffAnalyzer.scala:30-56`, `src/spatial/traversal/InitiationAnalyzer.scala:29-38`). However, the HLS path should record discrepancies rather than hiding them: `requested_ii`, `spatial_compiler_ii`, `hls_accepted_ii`, and reason/source. This keeps Spatial's useful transition signal while preventing old metadata from becoming a misleading scheduler oracle.
