---
type: spec
concept: Spatial IR Metadata - Control
source_files:
  - "src/spatial/metadata/control/ControlData.scala:7-287"
  - "src/spatial/metadata/control/Ctrl.scala:6-35"
  - "src/spatial/metadata/control/Scope.scala:5-24"
  - "src/spatial/metadata/control/Blk.scala:5-19"
  - "src/spatial/metadata/control/ControlSignalData.scala:5-60"
  - "src/spatial/metadata/control/streaming.scala:6-38"
  - "src/spatial/metadata/control/AccelScopes.scala:6-14"
  - "src/spatial/metadata/control/package.scala:25-1385"
source_notes:
  - "direct-source-reading"
hls_status: rework
depends_on:
  - "[[00 - Metadata Index]]"
status: draft
---

# Control

## Summary

Control metadata is Spatial's per-symbol control-plane layer: it records schedule, level, looping, hierarchy, timing, memory-touch sets, stream transfer side channels, and unroll directives for controller and controller-adjacent symbols (`src/spatial/metadata/control/ControlData.scala:7-287`). The type layer is intentionally small: `CtrlSchedule` enumerates `Sequenced`, `Pipelined`, `Streaming`, `ForkJoin`, `Fork`, and `PrimitiveBox`; `CtrlLevel` enumerates `Inner` and `Outer`; `CtrlLooping` enumerates `Single` and `Looped` (`src/spatial/metadata/control/ControlData.scala:7-36`). The hierarchy layer has three ADTs: `Ctrl` describes the hardware control stage, `Scope` describes exact stage/block scope, and `Blk` describes the raw IR block (`src/spatial/metadata/control/Ctrl.scala:6-35`, `src/spatial/metadata/control/Scope.scala:5-24`, `src/spatial/metadata/control/Blk.scala:5-19`).

## Syntax / API

The control metadata fields are exposed by `SymControlOps`, `CtrlControl`, `ScopeOperations`, and `ControlOpOps` in `control/package.scala` (`src/spatial/metadata/control/package.scala:25-121`, `src/spatial/metadata/control/package.scala:752-879`, `src/spatial/metadata/control/package.scala:882-961`). `rawLevel`, `rawSchedule`, `userSchedule`, `rawChildren`, `rawParent`, `rawScope`, `blk`, `bodyLatency`, `II`, `userII`, `compilerII`, `unrollBy`, and `progorder` are direct symbol metadata accessors (`src/spatial/metadata/control/package.scala:776-845`). The stream-facing API includes `listensTo`, `pushesTo`, `isAligned`, `loadCtrl`, `getFringe`/`setFringe`, and `argMapping` (`src/spatial/metadata/control/package.scala:649-711`). Global control stream sets are `StreamLoads`, `TileTransfers`, `StreamEnablers`, `StreamHolders`, and `StreamParEnqs`, all stored as `GlobalData.Flow` (`src/spatial/metadata/control/streaming.scala:6-38`).

## Semantics

`Ctrl.Node(sym, stg).master` collapses every stage-specific controller to `Ctrl.Node(sym, -1)`, and `Scope.Node(sym, stg, blk).master` collapses exact scope to `Scope.Node(sym, -1, -1)` (`src/spatial/metadata/control/Ctrl.scala:19-24`, `src/spatial/metadata/control/Scope.scala:15-18`). The `-1` convention is therefore the whole-controller identity, while non-negative stage ids address individual bodies (`src/spatial/metadata/control/Ctrl.scala:19-24`, `src/spatial/metadata/control/package.scala:886-903`). `Ctrl.SpatialBlackbox(sym).master` maps to `Ctrl.Node(sym, 0)`, but its `mayBeOuterBlock` is false, so blackbox controllers are treated as inner for level classification (`src/spatial/metadata/control/Ctrl.scala:32-35`, `src/spatial/metadata/control/package.scala:161-167`).

Effective `level` is derived from raw outer metadata plus the stage's `mayBeOuterBlock`; Host is outer, spatial blackboxes are inner, and everything else defaults inner (`src/spatial/metadata/control/package.scala:161-167`). Effective `looping` is `Looped` only when the op is a loop that will not fully unroll; fully unrolled loops are classified as `Single` (`src/spatial/metadata/control/package.scala:26-34`, `src/spatial/metadata/control/package.scala:188-192`). Effective `schedule` defaults to `Sequenced` if no raw schedule is present, and `Pipelined` collapses to `Sequenced` for `Single` controllers, including the requested `Single`/`Inner` case and the source's `Single`/`Outer` case (`src/spatial/metadata/control/package.scala:193-219`).

The master controller's `children` method expands real stages into `Ctrl.Node(sym, id)` and transparently replaces pseudostages with the raw children scoped under that stage (`src/spatial/metadata/control/package.scala:886-903`). The `nestedChildren` variant recursively expands pseudostage children, while Host children are `AccelScopes.all` (`src/spatial/metadata/control/package.scala:913-933`, `src/spatial/metadata/control/AccelScopes.scala:6-14`). `innerBlocks` and `outerBlocks` split a control op's bodies by stage outer-eligibility and effective level, so the same raw controller can expose different block sets depending on `Ctrl.Node` stage identity (`src/spatial/metadata/control/package.scala:169-186`).

## Implementation

Transfer policies are part of the spec because transformers use them. `ControlLevel`, `ControlSchedule`, and `Children` are `SetBy.Flow.Self`; `CounterOwner`, `ParentCtrl`, `ScopeCtrl`, `DefiningBlk`, `WrittenDRAMs`, `ReadDRAMs`, `WrittenMems`, and `ReadMems` are `SetBy.Flow.Consumer`; `IndexCounter`, `IterInfo`, `BodyLatency`, `InitiationInterval`, `CompilerII`, `TransientReadMems`, `ShouldNotBind`, `HaltIfStarved`, `LoweredTransfer`, `LoweredTransferSize`, `UnrollBy`, and `ProgramOrder` are `SetBy.Analysis.Self`; `UserScheduleDirective`, `UserII`, `UnrollAsPOM`, and `UnrollAsMOP` are `SetBy.User`; `ConvertToStreamed` is `Transfer.Mirror` (`src/spatial/metadata/control/ControlData.scala:47-287`). Stream control metadata is mixed: `ListenStreams`, `PushStreams`, and `LoadMemCtrl` are `Transfer.Remove`; `AlignedTransfer` and `ArgMap` are `Transfer.Mirror`; `Fringe` is `SetBy.Analysis.Consumer` (`src/spatial/metadata/control/ControlSignalData.scala:5-60`).

`rawSchedule_=` writes into `state.scratchpad`, while `finalizeRawSchedule` writes `ControlSchedule` into normal metadata; getters prefer scratchpad state over stored metadata (`src/spatial/metadata/control/package.scala:785-789`). This is transformer-time mutable state, not a pure field update, and a Rust port should keep the two-phase schedule path explicit (`src/spatial/metadata/control/package.scala:785-789`). Memory touch summaries have both direct and nested forms: nested variants combine the current controller with `nestedChildren`, then union each child's metadata (`src/spatial/metadata/control/package.scala:552-600`). `shouldNotBind`, `haltIfStarved`, lowered transfer metadata, unroll directives, and stream conversion flags are plain metadata lookups with defaults of false, `None`, or throwing getters where undefined (`src/spatial/metadata/control/package.scala:602-646`).

## Interactions

`ControlOpOps` defines the predicates used by later passes to recognize loops, controls, primitives, branches, reductions, FSMs, fringe loads/stores, and tile transfers (`src/spatial/metadata/control/package.scala:25-121`). `CtrlHierarchyOps.isCtrl` composes the three dimensions, and the convenience predicates `isInnerControl`, `isOuterControl`, `isPipeControl`, `isStreamControl`, `isOuterPipeLoop`, and related helpers are all projections of `looping`, `level`, and `schedule` (`src/spatial/metadata/control/package.scala:221-298`). Dataflow utilities such as `LCA`, `getStageDistance`, `getCoarseDistance`, `findAllMetaPipes`, and `computeMemoryBufferPorts` use this hierarchy to reason about stage distance and N-buffer ports (`src/spatial/metadata/control/package.scala:1121-1328`). Stream discovery uses memory reader/writer metadata and control parents to compute inbound, priority inbound, and outbound stream sets for a controller (`src/spatial/metadata/control/package.scala:1360-1380`).

## HLS notes

The hierarchy ADTs transfer cleanly as data structures, but effective schedule, retiming latency, stream-stall policy, and buffer-port policy should be re-derived for Rust+HLS rather than copied as Chisel-era decisions (inferred, unverified). Preserve `Ctrl.Node(sym, -1)` master semantics and transfer-policy categories, because many downstream queries assume those identities and transformer lifetimes (`src/spatial/metadata/control/Ctrl.scala:19-24`, `src/spatial/metadata/control/ControlData.scala:47-287`).

## Open questions

- Q-meta-01: What pass sequence guarantees `rawSchedule_=` scratchpad values are finalized by `finalizeRawSchedule`?
- Q-meta-02: Which pass consumes `ConvertToStreamed`, and should it remain `Transfer.Mirror` in the Rust port?
- Q-meta-03: Can `HaltIfStarved` be replaced with a derived stream dependency model instead of an analysis-set boolean?
