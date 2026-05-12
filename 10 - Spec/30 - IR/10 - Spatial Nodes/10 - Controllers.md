---
type: spec
concept: spatial-ir-controllers
source_files:
  - "src/spatial/node/HierarchyControl.scala:1-85"
  - "src/spatial/node/Control.scala:1-143"
  - "src/spatial/node/Switch.scala:1-70"
  - "argon/src/argon/node/DSLOp.scala:1-37"
  - "argon/src/argon/node/Enabled.scala:1-21"
  - "argon/src/argon/Op.scala:1-126"
  - "src/spatial/lang/control/AccelClass.scala:1-21"
  - "src/spatial/lang/control/ForeachClass.scala:1-35"
  - "src/spatial/lang/control/ReduceClass.scala:1-98"
  - "src/spatial/lang/control/MemReduceClass.scala:1-105"
  - "src/spatial/lang/control/Parallel.scala:1-15"
  - "src/spatial/lang/control/FSM.scala:1-26"
  - "src/spatial/metadata/control/ControlData.scala:7-160"
  - "src/spatial/metadata/control/package.scala:773-824"
source_notes:
  - "[[spatial-ir-nodes]]"
hls_status: rework
depends_on:
  - "[[40 - Counters and Iterators]]"
  - "[[20 - Memories]]"
  - "[[30 - Memory Accesses]]"
status: draft
---

# Controllers (IR nodes)

## Summary

Spatial's controller nodes — `AccelScope`, `UnitPipe`, `ParallelPipe`, `OpForeach`, `OpReduce`, `OpMemReduce`, `StateMachine`, `UnrolledForeach`, `UnrolledReduce`, `Switch`, `SwitchCase` — are the IR primitives that represent every stateful/cycle-aware region of hardware. They form a small class hierarchy rooted at `argon.node.DSLOp[R]` via `spatial.node.Control[R]` (`src/spatial/node/HierarchyControl.scala:47-53`), and serve as the anchor for all scheduling, banking, retiming, and codegen passes. For the HLS rewrite, the controller node surface is the backbone: it defines which values are bound iterators, which blocks are pseudo- vs real-stages, and what metadata (schedule, level, parent, children, block id) must be attached.

## Syntax / API

Users construct controllers through the DSL helpers (`src/spatial/lang/control/*`); each helper `stage(…)`s exactly one IR node:

- `Accel { ... }` → `AccelScope(block)` (`src/spatial/lang/control/AccelClass.scala:17-20`).
- `Pipe { ... }` / `Sequential { ... }` → `UnitPipe(ens, block, stopWhen)` (`src/spatial/lang/control/Control.scala:18`).
- `Parallel { ... }` → `ParallelPipe(ens, block)` (`src/spatial/lang/control/Parallel.scala:9-14`).
- `Foreach(ctrs){ ... }` → `OpForeach(ens, cchain, block, iters, stopWhen)` (`src/spatial/lang/control/ForeachClass.scala:26-33`).
- `Reduce(z)(ctrs)(map)(reduce)` → `OpReduce(ens, cchain, accum, map, load, reduce, store, ident, fold, iters, stopWhen)` (`src/spatial/lang/control/ReduceClass.scala:38-51`).
- `MemReduce(accum)(ctrs)(map)(reduce)` → `OpMemReduce(ens, cchainMap, cchainRed, accum, map, loadRes, loadAcc, reduce, storeAcc, ident, fold, itersMap, itersRed, stopWhen)` (`src/spatial/lang/control/MemReduceClass.scala:74-91`).
- `FSM(init)(notDone)(action)(next)` → `StateMachine(ens, start, notDone, action, nextState)` (`src/spatial/lang/control/FSM.scala:18-24`).
- `Switch.op_switch(selects, cases)` → `Switch(selects, body)` with inner `SwitchCase(body)` nodes (`src/spatial/node/Switch.scala:62-69`).

Unrolled variants (`UnrolledForeach`, `UnrolledReduce`) are produced by the unroller, not by the DSL directly.

## Semantics

### Base contract

Every `Control[R]` exposes three abstract members (`src/spatial/node/HierarchyControl.scala:50-52`):

```scala
def iters: Seq[I32]
def cchains: Seq[(CounterChain, Seq[I32])]
def bodies: Seq[ControlBody]
```

and overrides two `Op` defaults (`HierarchyControl.scala:48-49`): `inputs = super.inputs diff iters` and `binds = super.binds ++ iters.toSet`. This ensures iterators are scheduled as *bound* variables — they define the start of a scope, and the symbol-dataflow pass treats them as inputs to the block, not as inputs to the container.

`EnControl[R] extends Control[R] with Enabled[R]` (`HierarchyControl.scala:62`) adds `var ens: Set[Bit]` via the argon `Enabled` trait (`argon/src/argon/node/Enabled.scala:6-21`). `Pipeline[R] extends EnControl[R]` marks controllers whose body executes at least once (`HierarchyControl.scala:65`). `Loop[R] extends Pipeline[R]` marks controllers whose body may execute multiple iterations (`HierarchyControl.scala:68`).

### ControlBody taxonomy

Bodies are one of three shapes (`HierarchyControl.scala:17-44`):

- `PseudoStage(blks: (Seq[I32], Block[_])*)` — `isPseudoStage = true`, `mayBeOuterStage = true`, `isInnerStage = false`. Used for scheduling/metadata but does not become a hardware stage.
- `OuterStage(blks: (Seq[I32], Block[_])*)` — `mayBeOuterStage = true`, `isPseudoStage = false`, `isInnerStage = false`. Real outer-controller stage.
- `InnerStage(blks: (Seq[I32], Block[_])*)` — `isInnerStage = true`, `isPseudoStage = false`, `mayBeOuterStage = false`. Real inner-controller stage (never outer).

Each `blks` tuple pairs the iterator visibility (`Seq[I32]`) with the block itself (`Block[_]`). Most controllers have a single body with a single block; `OpReduce` and `OpMemReduce` have multi-block bodies (see below).

### Per-node constructor signatures

`AccelScope(block: Block[Void])` (`src/spatial/node/Control.scala:21-31`) — extends `Pipeline[Void]`; `iters = Nil`, `cchains = Nil`, `bodies = Seq(PseudoStage(Nil -> block))`; `ens` held at `Set.empty` with `updateEn`/`mirrorEn` overridden to not propagate. Adds `Effects.Simple` (line 30) to prevent DCE ("TODO[5]: Technically Accel doesn't need a simple effect").

`UnitPipe(ens: Set[Bit], block: Block[Void], stopWhen: Option[Reg[Bit]])` (`Control.scala:33-37`) — `Pipeline[Void]`, no counters, single pseudo-stage.

`ParallelPipe(ens: Set[Bit], block: Block[Void])` (`Control.scala:39-43`) — `Pipeline[Void]`, single pseudo-stage; no `stopWhen` (unlike `UnitPipe`).

`OpForeach(ens, cchain, block, iters, stopWhen)` (`Control.scala:45-54`) — `Loop[Void]`; `cchains = Seq(cchain -> iters)`, `bodies = Seq(PseudoStage(iters -> block))`.

`OpReduce[A](ens, cchain, accum, map, load, reduce, store, ident, fold, iters, stopWhen)(implicit A: Bits[A])` (`Control.scala:57-76`) — `Loop[Void]`. `binds` extended to include `reduce.inputs` (line 70). Two bodies: `PseudoStage(iters -> map)` then `InnerStage(Nil -> load, iters -> reduce, Nil -> store)` (lines 72-75) — the accumulator load/store run once per outer-iteration, the reduction tree runs per-iteration.

`OpMemReduce[A,C[T]](ens, cchainMap, cchainRed, accum, map, loadRes, loadAcc, reduce, storeAcc, ident, fold, itersMap, itersRed, stopWhen)(implicit A: Bits[A], C: LocalMem[A,C])` (`Control.scala:78-101`) — `Loop[Void]`. `iters` concatenates `itersMap ++ itersRed`. `cchains = Seq(cchainMap -> itersMap, cchainRed -> itersRed)`. Bodies: `PseudoStage(itersMap -> map)` then `InnerStage` with four blocks: `itersMap ++ itersRed -> loadRes`, `itersRed -> loadAcc`, `itersMap ++ itersRed -> reduce`, `itersRed -> storeAcc`. Iterator visibility differs per block — a consumer of `.bodies` must inspect the iterator sequence of each block individually.

`StateMachine[A](ens, start, notDone, action, nextState)(implicit A: Bits[A])` (`Control.scala:103-118`) — `Loop[Void]`. `iters = Nil`, `cchains = Nil`. Three bodies: `InnerStage(Nil -> notDone)`, `PseudoStage(Nil -> action)`, `PseudoStage(Nil -> nextState)`. `binds` extended by `notDone.inputs`.

`UnrolledForeach(ens, cchain, func, iterss, validss, stopWhen)` (`Control.scala:121-131`) — `UnrolledLoop[Void]`. `cchainss = Seq(cchain -> iterss)`, `bodiess = Seq(iterss -> Seq(func))`.

`UnrolledReduce(ens, cchain, func, iterss, validss, stopWhen)` (`Control.scala:133-143`) — `UnrolledLoop[Void]`. Identical shape to `UnrolledForeach` at this level; distinguished by its node identity (so downstream passes can pattern-match).

`SwitchCase[R:Type](body: Block[R])` (`Switch.scala:36-40`) — extends `Control[R]`; `iters = Nil`, `cchains = Nil`, `bodies = Seq(PseudoStage(Nil -> body))`. NOTE in source: "SwitchCase should never exist outside a Switch".

`Switch[R:Type](selects: Seq[Bit], body: Block[R])` (`Switch.scala:46-58`) — `Control[R]`. Body holds a scope of `SwitchCase` nodes. `cases: Seq[SwitchCase[R]]` helper (line 53-55) collects them by scanning `body.stms`. `aliases = syms(cases.map(_.body.result))` (line 51) — a switch result may equal any case result.

`SwitchScheduler` (`Switch.scala:11-30`) is a custom `argon.schedule.Scheduler` used when staging a Switch body via `Switch.op_switch` (line 66: `BlockOptions(sched = Some(SwitchScheduler))`). It partitions the scope into nodes that are `SwitchCase` (kept) and everything else (motioned out). Any pass that rebuilds scopes inside a switch must preserve this option; otherwise operations nested inside the cases will leak up to the switch scope.

### UnrolledLoop mechanics

`UnrolledLoop[R]` (`HierarchyControl.scala:72-85`) introduces:

```scala
def iterss: Seq[Seq[I32]]
def validss: Seq[Seq[Bit]]
def cchainss: Seq[(CounterChain, Seq[Seq[I32]])]
def bodiess: Seq[(Seq[Seq[I32]], Seq[Block[_]])]
```

with `iters = iterss.flatten`, `valids = validss.flatten`, `cchains` derived by flattening the iterss-per-chain, and `bodies` computed by wrapping each per-loop block in a `PseudoStage` using the flattened iter set. `inputs` is further reduced by `diff (iters ++ valids)` (line 79) and `binds` is augmented by `(iters ++ valids).toSet`.

## Implementation

### Class hierarchy

```
argon.node.DSLOp[R]   (argon/src/argon/node/DSLOp.scala:6-9)
  Control[R]          (HierarchyControl.scala:47-53)
    EnControl[R]      (HierarchyControl.scala:62)
      Pipeline[R]     (HierarchyControl.scala:65)
        Loop[R]       (HierarchyControl.scala:68)
          UnrolledLoop[R]  (HierarchyControl.scala:72-85)
```

`AccelScope`, `UnitPipe`, `ParallelPipe` extend `Pipeline[Void]` directly; `OpForeach`, `OpReduce`, `OpMemReduce`, `StateMachine` extend `Loop[Void]`; `UnrolledForeach`, `UnrolledReduce` extend `UnrolledLoop[Void]`. `Switch` and `SwitchCase` extend `Control[R]` directly (not `EnControl`) — they have no explicit `ens`.

### Metadata touch-points

Every controller participates in a metadata web, written by `flows/SpatialFlowRules.scala` and read by every subsequent pass. The accessors in `src/spatial/metadata/control/package.scala` define the canonical API (lines 773-824):

- `sym.rawLevel: CtrlLevel` (`Inner`/`Outer`) — stored as `ControlLevel(level)` with `SetBy.Flow.Self` (`src/spatial/metadata/control/ControlData.scala:29-47`).
- `sym.rawSchedule: CtrlSchedule` — one of `Sequenced`/`Pipelined`/`Streaming`/`ForkJoin`/`Fork`/`PrimitiveBox` (lines 7-14). Stored as `ControlSchedule(sched)`, `SetBy.Flow.Self` (lines 57-64). Read via `sym.rawSchedule` (package.scala:786). A separate `UserScheduleDirective` (lines 67-74) holds user annotations; `sym.userSchedule` returns it when present.
- `sym.rawParent: Ctrl` — stored as `ParentCtrl(parent)` with `SetBy.Flow.Consumer` (lines 87-99).
- `sym.scope: Scope` — stored as `ScopeCtrl(scope)` with `SetBy.Flow.Consumer` (lines 101-111).
- `sym.rawChildren: Seq[Ctrl.Node]` — stored as `Children(children)` with `SetBy.Flow.Self` (lines 77-85). Setter at package.scala:814.
- `sym.blk: Blk` — stored as `DefiningBlk(blk)` with `SetBy.Flow.Consumer` (lines 115-126). Block id semantics: pseudo-stages have different ids than real stages, and `OpMemReduce`'s inner-stage sub-blocks are each identified by their index into the block list.

Iterators carry `IndexCounter(info)` metadata (`src/spatial/metadata/control/ControlData.scala:129-136`) bound by the DSL layer — see [[40 - Counters and Iterators]].

### Staging flow

Each DSL controller helper uses `stageWithFlow` (see `src/spatial/lang/control/ForeachClass.scala:30-32`). The `flow` callback assigns `CtrlOpt` state (schedule hint, initiation interval, `stopWhen`, `mop`/`pom` toggles, `haltIfStarved`). For `AccelScope`, `src/spatial/lang/control/AccelClass.scala:17-18` wraps the scope in a `stageBlock` that appends `void` to force a `Block[Void]` result.

### Effect classification

- `AccelScope.effects = super.effects andAlso Effects.Simple` (`Control.scala:30`) — prevents DCE of Accel.
- `Control[R]`'s default `effects` (inherited from `Op`) aggregates block effects via `blocks.map(_.effects).fold(Effects.Pure)(_ andAlso _)` (`argon/src/argon/Op.scala:70`).
- `UnitPipe`/`ParallelPipe`/`OpForeach`/`OpReduce`/`OpMemReduce`/`StateMachine`/`UnrolledForeach`/`UnrolledReduce`/`Switch`/`SwitchCase` inherit default block-derived effects; they are mutable-or-pure depending on the body.

### Switch scheduling

The custom scheduler at `Switch.scala:11-30`:

```scala
override def apply[R](inputs, result, scope, impure, options, allowMotion) = {
  val (keep, motion) = scope.partition{_.op.exists(_.isInstanceOf[SwitchCase[_]])}
  val (keepI, motionI) = impure.partition(_.sym.op.exists(_.isInstanceOf[SwitchCase[_]]))
  val effects = summarizeScope(keepI)
  val result = keep.last.asInstanceOf[Sym[R]]
  val block = new Block[R](inputs, keep, result, effects, options)
  Schedule(block, motion, motionI)
}
```

`mustMotion = true` (line 12) forces code motion; `keep.last` becomes the block's result — so the last `SwitchCase` acts as the typed yield.

## Interactions

**Written by:** the front end's `stage(...)` call for each DSL entry point; `flows/SpatialFlowRules.scala` assigns `rawLevel`/`rawSchedule`/`rawParent`/`rawChildren`/`blk` reactively.

**Read by:**
- `traversal/` passes that walk the controller hierarchy (e.g., AccessAnalyzer, ControlSanityCheck).
- `transform/unrolling/` — consumes `OpForeach`/`OpReduce`/`OpMemReduce` and produces `UnrolledForeach`/`UnrolledReduce` with `iterss`/`validss` expanded.
- `transform/pipeInserter`, `transform/switchTransformer`, `transform/switchOptimizer`, `transform/laneStaticTransformer`, `transform/memoryDealiasing` — rewrite controller bodies.
- `transform/retiming` — reads `rawSchedule` to decide per-body retiming depth.
- `codegen/chiselgen/ChiselGenController.scala`, `codegen/scalagen`, `codegen/pirgen` — emit per-controller boilerplate keyed by `rawSchedule × rawLevel`.

**Invariants the Rust rewrite must preserve:**
- `Control.inputs` excludes `iters`; `binds` includes them.
- `UnrolledLoop.inputs` additionally excludes `valids`; `binds` includes them.
- `AccelScope` carries `Effects.Simple` so DCE cannot remove the accel scope.
- `Switch` bodies use a non-default scheduler (`SwitchScheduler`); re-staging must preserve `BlockOptions(sched = Some(SwitchScheduler))` (`Switch.scala:66`).
- `OpMemReduce.bodies(1)` is an `InnerStage` with four sub-blocks at specific indices; iterating `.bodies` and assuming one body = one block will misread `OpMemReduce`.
- Stage-id `-1` denotes the "master"/whole-controller form for `Ctrl.Node`; stage ids ≥ 0 index into the `bodies` list.

## HLS notes

`hls_status: rework`. HLS targets (Vitis HLS, Intel HLS) have their own controller metaphor (functions with pipeline/unroll pragmas, state machines driven by scheduling hints). The Rust-over-HLS path will need:

1. A surface that preserves Spatial's six control schedules (`Sequenced`/`Pipelined`/`Streaming`/`ForkJoin`/`Fork`/`PrimitiveBox`).
2. A lowering that maps each kind to HLS pragmas + dataflow regions.
3. `OpMemReduce`'s per-block iterator visibility is unusual; the HLS rewrite may want to normalize to a shape with a single reduce dimension per inner stage.
4. `AccelScope`'s `Effects.Simple` guard is a Spatial idiom; in HLS this maps to whichever "keep this function alive" directive the target uses.

See `30 - HLS Mapping/` for the per-construct categorization.

## Open questions

- Q-007 in `20 - Open Questions.md` — `StateMachine` three-body asymmetry (InnerStage + two PseudoStage) semantics.
- Q-011 — Is there a canonical stage-id numbering when a controller has multiple `OuterStage`s, or does each non-pseudo body get its own scope id?
