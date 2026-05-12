---
type: spec
status: draft
concept: control-semantics
source_files:
  - "src/spatial/node/HierarchyControl.scala:1-85"
  - "src/spatial/node/Control.scala:21-143"
  - "src/spatial/node/Switch.scala:11-70"
  - "src/spatial/lang/control/Control.scala:9-72"
  - "src/spatial/lang/control/CtrlOpt.scala:8-27"
  - "src/spatial/metadata/control/ControlData.scala:7-287"
  - "src/spatial/metadata/control/package.scala:161-219"
  - "src/spatial/traversal/InitiationAnalyzer.scala:12-101"
  - "src/spatial/transform/RetimingTransformer.scala:205-220"
  - "src/spatial/targets/LatencyModel.scala:48-66"
source_notes:
  - "[[10 - Controllers]]"
  - "[[10 - Control]]"
  - "[[C0 - Retiming]]"
  - "[[10 - Controllers]]"
  - "[[50 - Controller Emission]]"
  - "[[20 - Latency Model]]"
hls_status: rework
depends_on:
  - "[[10 - Controllers]]"
  - "[[10 - Control]]"
  - "[[C0 - Retiming]]"
  - "[[20 - Latency Model]]"
  - "[[80 - Unrolling]]"
  - "[[50 - Controller Emission]]"
---

# Control Semantics

## Summary

Spatial control semantics are defined by three layers: the IR controller nodes in [[10 - Controllers]], control metadata in [[10 - Control]], and timing/II analysis in [[C0 - Retiming]]. A controller is not just a loop node. It binds iterators, owns one or more bodies, carries a raw and effective schedule, has an inner or outer level, exposes child stages, and participates in retiming and initiation analysis. The DSL entry [[10 - Controllers]] writes user schedule and user II through `CtrlOpt.set`; later passes compute effective schedule, collapse some schedules for single controllers, unroll lane parallelism, and assign compiler II.

## Formal Semantics

Every Spatial controller is a `Control[R]` with `iters`, `cchains`, and `bodies`; `Control.inputs` excludes bound iterators and `binds` includes them (`src/spatial/node/HierarchyControl.scala:47-53`). Body shape is part of the semantics. `PseudoStage` may be an outer stage for metadata but does not become a real hardware stage, `OuterStage` is a real outer-stage body, and `InnerStage` is a real inner-stage body (`src/spatial/node/HierarchyControl.scala:17-44`). `OpReduce` uses a pseudo map stage plus an inner stage containing load/reduce/store blocks; `OpMemReduce` uses a pseudo map stage plus an inner stage with four sub-blocks and different iterator visibility (`src/spatial/node/Control.scala:57-101`). This is why downstream passes must inspect body block indices rather than assume one controller has one body.

The schedule domain is the closed enum `Sequenced`, `Pipelined`, `Streaming`, `ForkJoin`, `Fork`, and `PrimitiveBox` (`src/spatial/metadata/control/ControlData.scala:7-14`). Formally, a raw schedule is a tag stored on a control symbol; effective schedule is a derived value. If no raw schedule exists, effective schedule is `Sequenced`. If a controller is `Single`, `Pipelined` collapses to `Sequenced`; this collapse applies to both inner and outer single controllers in the current metadata entry (`src/spatial/metadata/control/package.scala:193-219`). For looped controllers, `Sequenced` means no pipeline overlap is requested, `Pipelined` means loop iterations may overlap subject to II, `Streaming` means dataflow/stream-driven execution, `ForkJoin` means child controls are coordinated as a fork with a join, `Fork` means forked control without the same join semantics, and `PrimitiveBox` identifies primitive blackbox-like scheduling (the last three are defined by their enum membership and codegen/pass consumers; detailed operational rules beyond that are inferred, unverified).

The raw schedule is also two-phase metadata: setters can write to scratchpad state and `finalizeRawSchedule` writes normal metadata later, with getters preferring scratchpad values while present (`src/spatial/metadata/control/package.scala:785-789`). A Rust implementation should not treat schedule assignment as a single immutable field write during transformations.

User directives enter at the language surface. `Pipe` constructs `CtrlOpt(..., Some(Pipelined), ii, mop, pom, nobind, haltIfStarved)`, `Stream` constructs `Some(Streaming)`, and `Sequential` constructs `Some(Sequenced)` (`src/spatial/lang/control/Control.scala:22-57`). `CtrlOpt.set` writes `userSchedule`, `userII`, `unrollAsMOP`, `unrollAsPOM`, `shouldNotBind`, and `haltIfStarved` onto the staged symbol (`src/spatial/lang/control/CtrlOpt.scala:8-27`). Thus user II is a request, not the compiler's computed result.

II semantics are fixed by `InitiationAnalyzer`. For outer controllers, `compilerII` is the maximum of child IIs and at least `1.0`; the effective `II` is `userII.getOrElse(compilerII)` (`src/spatial/traversal/InitiationAnalyzer.scala:14-21`). For inner controllers, the analyzer computes body latency and interval, reads positive `iterDiff`s, sets `compilerII` to `1.0`, `interval`, or `ceil(interval / minIterDiff)` depending on reduction distance, then sets effective `II` to either full latency for user-sequenced controls or `userII.getOrElse(min(compilerII, latency))` (`src/spatial/traversal/InitiationAnalyzer.scala:23-41`). The distinction must be preserved: `compilerII` is the compiler's feasibility estimate; `II` is the selected schedule interval after user overrides and sequenced collapse.

Pipeline fill and drain are described by latency model composition. `parallelModel` is `max(stage latencies) + node latency`; `streamingModel(N, ii, stages)` is `stages.max * (N - 1) * ii + node latency`; `metaPipeModel` adds `stages.sum`; and `sequentialModel` is `stages.sum * N + node latency` (`src/spatial/targets/LatencyModel.scala:48-66`). These formulas are not a replacement for controller execution, but they define how the model accounts for fill/drain and overlapped iterations in [[20 - Latency Model]].

Parallelization is `par x lanes`. Counters carry `par`; unrolling maps each lane to iterator substitutions and lane-valid bits, and `UnrolledLoop` flattens `iterss` and `validss` into bound inputs (`src/spatial/node/HierarchyControl.scala:72-85`). Scalagen counters confirm the runtime shape: a counter iteration produces arrays of lane values and valid bits, not a scalar iterator (`spatial/emul/src/emul/Counter.scala:5-53`). In hardware, those lanes are parallel datapaths; in Scalagen they are processed by emitted loops over arrays in [[60 - Counters and Primitives]].

Inner vs outer is derived, not simply declared. Effective level combines raw outer metadata with whether a stage may be an outer block; Host is outer, spatial blackboxes are inner, and everything else defaults inner (`src/spatial/metadata/control/package.scala:161-167`). Effective looping is `Looped` only for loops that will not fully unroll; fully unrolled loops collapse to `Single` (`src/spatial/metadata/control/package.scala:188-192`). The master/child hierarchy uses `Ctrl.Node(sym, -1)` as whole-controller identity and stage ids for real bodies; pseudostages expand into their raw children (`src/spatial/metadata/control/package.scala:886-933`). This collapse rule is central to [[80 - Unrolling]] and [[50 - Controller Emission]].

## Reference Implementation

The reference behavior is distributed. The IR node constructors define the binding and body shapes (`src/spatial/node/Control.scala:21-143`). Control metadata defines effective level/schedule/looping (`src/spatial/metadata/control/package.scala:161-219`). Retiming computes body latencies and delay requirements for inner controls (`src/spatial/transform/RetimingTransformer.scala:205-220`). Scalagen then emits controllers as kernel objects and runs `ParallelPipe` children sequentially for simulation, a known simulation-vs-hardware distinction recorded in [[50 - Controller Emission]] (`spatial/src/spatial/codegen/scalagen/ScalaGenController.scala:180-191`).

## HLS Implications

The Rust+HLS target should treat controller schedule as a structured enum plus derived effective schedule. `Pipelined` maps naturally to `#pragma HLS pipeline II=N`, `Streaming` and `ForkJoin` to HLS dataflow regions, and lane parallelism to unrolled loops or duplicated tasks. Retiming's Chisel delay lines should not be copied directly, but `compilerII`, `userII`, and pipeline fill/drain formulas are still needed to decide HLS pragmas and to predict performance.

## Open questions

- [[open-questions-semantics#Q-sem-05 - 2026-04-25 Operational meaning of Fork, ForkJoin, and PrimitiveBox]] tracks the gap between enum membership and fully documented execution semantics.
- [[open-questions-semantics#Q-sem-06 - 2026-04-25 Scalagen parallel pipe serial execution]] tracks whether the Rust simulator should match Scalagen's sequential `ParallelPipe` execution or model parallel interleaving.
