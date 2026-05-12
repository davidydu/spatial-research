---
type: spec
concept: pipe-insertion
source_files:
  - "src/spatial/transform/PipeInserter.scala:1-323"
  - "src/spatial/Spatial.scala:106"
  - "src/spatial/Spatial.scala:190"
  - "src/spatial/Spatial.scala:138"
  - "src/spatial/Spatial.scala:144"
source_notes:
  - "[[pass-pipeline]]"
hls_status: rework
depends_on:
  - "[[10 - Flows and Rewrites]]"
  - "[[Controllers]]"
status: draft
---

# Pipe Insertion

## Summary

`PipeInserter` is the structural pass that enforces the invariant **no outer control has a mix of primitives and controllers**. It classifies every statement in every outer control block as `Transient`, `Alloc`, `Primitive`, `Control`, or `FringeNode`; bundles runs of primitives into `Stage` buckets; possibly binds inner stages with a following outer stage when the outer stage consumes an inner value; and emits a `Pipe { ... resWrite(r, s) }` wrapper for each inner stage, replacing escaping bit-values with register / FIFOReg holders. The pass runs **three times** in the canonical pipeline: once as the main post-lowering structural pass, once inside the optional streamify block, and once inside `fifoInitialization` after the FIFO initializer emits new UnitPipes.

## Algorithm overview

`case class PipeInserter(IR: State) extends MutateTransformer with BlkTraversal` (`src/spatial/transform/PipeInserter.scala:15`). The algorithm has four phases per outer block: classify → compute stages → bind stages → wrap inner.

### Classification — 5 statement kinds

Each stmt in the block gets dispatched via pattern match at `:117-133`:

```scala
block.stms.foreach{
  case Transient(s)  => … stage.nodes += s …         // inline motion based on inputs
  case Alloc(s)      => nextOuterStage.nodes += s
  case Primitive(s)  => nextInnerStage.nodes += s
  case Control(s)    => nextOuterStage.nodes += s
  case FringeNode(s) => nextOuterStage.nodes += s
}
```

- **`Transient`** nodes (e.g. `RegRead` in many contexts) get attached to the *last* stage where their input-producers or their effect-writers live: `val i = stages.lastIndexWhere{stage => (stage.nodes ++ stage.nodes.flatMap(_.effects.writes) intersect s.inputs).nonEmpty}; if (i >= 0) stages(i) else stages.head` (`:118-126`). The comment (`:120-122`) explains this is specifically for `RegRead`: transient but ordered by memory dependency.
- **`Alloc`** — memory allocations go into the next outer stage.
- **`Primitive`** — pure compute goes into the next inner stage.
- **`Control`** — controllers go into the next outer stage (and each controller is a new outer stage).
- **`FringeNode`** — DRAM transfer nodes go into the next outer stage.

### `Stage` bucket

```scala
private class Stage(val inner: Boolean) { val nodes = ArrayBuffer[Sym[_]]() }
```
(`:27-38`). Two constructors: `Stage.outer` and `Stage.inner` (`:40-42`). `lazy val inputs: Set[Sym[_]]` at `:37` is the union of `nestedInputs` of all contained nodes.

### `nextInnerStage` and `nextOuterStage`

```scala
def nextInnerStage: Stage = { if (curStage.outer) stages += Stage.inner; curStage }
def nextOuterStage: Stage = { stages += Stage.outer; curStage }
```
(`:213-221`). Inner stages are *appended* only when the current stage is an outer (i.e. we're switching from controllers back to primitives). Outer stages are appended *always* — so every alloc / control / fringe gets its own outer stage, and primitives agglomerate within a single inner stage until broken by any outer-class stmt.

### Compute stages

`computeStages()` at `:116-134` drives the classification over `block.stms`. Starts with `stages += Stage.outer` (`:222`) so the first outer-class stmt goes into the pre-existing empty outer stage.

### Bind stages

`bindStages()` at `:135-168` is the tricky part. Two modes:

**Mode 1: parallel or stream control parent** (`:136-164`) — the parent is `ParallelPipe` or a stream-controlled block. Walks `stages.dropRight(1)` with index; for each inner stage, compute `escaping = stg.nodes.filter{s => !s.tp.isVoid && (s == block.result || s.consumers.diff(stg.nodes.toSet).nonEmpty)}` (`:142-145`) — values that escape this stage. Then intersect escaping-consumers with the *following* stage's contents (`val nextStageConsumes = escaping.flatMap(_.consumers).toSet intersect allStms(stages(i+1))`, `:152`). If the following stage is outer and consumes anything, bind this inner with the next outer: `boundStages += ArrayBuffer(stg, stages(i+1))` (`:155`). Else this inner gets its own bucket.

For outer stages, just wrap in their own bucket unless already consumed by a previous binding (`:158-161`). The last stage gets its own bucket if not already bound (`:163`).

**Mode 2: anything else** (`:165-167`) — `stages.foreach{stg => boundStages += ArrayBuffer(stg)}`. Each stage is its own bucket; no inner-outer binding.

### Wrap inner

`wrapInner(stgs, id)` at `:170-209`. For each stage in the bucket:
- **Outer** — just revisit each node (`stg.nodes.foreach(visit)`, `:207`).
- **Inner** — the critical case. Compute `escaping` just like in bind (`:174-182`). Allocate `escapingHolders` via `resFrom(s, parent)` for each escaping value — returns a `Reg` (or `FIFOReg` if `parent.isStreamControl`) for bit-valued escapees or a `Var` for non-bit types (`:256-260`). Then emit:
  ```scala
  Pipe {
    isolateSubst() {
      stg.nodes.foreach(visit)
      escaping.zip(escapingHolders).foreach{case (s, r) => resWrite(r, s)}
    }
  }
  ```
  (`:189-194`). After the Pipe, emit a `resRead(r)` in the parent scope and register `s -> resRead` for every escaping value, so downstream stmts see the post-read value (`:196-201`).

### Bucket emission

At `:232-241`, `boundStages` is iterated. For each bucket:
- **`stgs.size > 1`** (bind detected) — wrap both inner+outer stages in a single `Pipe` that executes `wrapInner(stgs, id)` inside.
- **`stgs.size == 1 && inner`** — emit a single inner wrap.
- **`stgs.size == 1 && outer`** — just visit the nodes directly.

## Switch specialization (`:46-67`)

When the pass hits a `Switch` whose LHS is `isOuterControl` and `inHw`:

```scala
case switch @ Switch(F(selects), _) if lhs.isOuterControl && inHw =>
  val res: Option[Either[LocalMem[A,C], Var[A]]] = 
    if (Type[A].isVoid) None else Some(resFrom(lhs, lhs))

  val cases = (switch.cases, selects, lhs.children).zipped.map { case (SwitchCase(body), sel, swcase) =>
    val controllers = swcase.children
    val primitives = body.stms.collect{case Primitive(s) => s }
    val requiresWrap = primitives.nonEmpty && controllers.nonEmpty

    () => withEnable(sel) {
      val body2: Block[Void] = {
        if (requiresWrap) wrapSwitchCase(body, lhs, res)
        else stageScope(f(body.inputs), body.options){ insertPipes(body, lhs, res, scoped = false).right.get }
      }
      Switch.op_case(body2)
    }
  }
```

Switch is handled specially because each `SwitchCase` can itself contain mixed primitives+controllers. If a case has both, `wrapSwitchCase` (`:100-106`) emits a `Pipe(enable, { insertPipes(...).right.get })` around the case body. Otherwise, `insertPipes` is called recursively on the case body.

The `enable` set is threaded via `withEnable(sel)` (`:18-24`) so that nested `Pipe`s inherit the SwitchCase selector.

The `res` handle is a `LocalMem` or `Var` allocated at the top of the Switch handling (`:47`). It's used as the unified return holder for all cases, so downstream consumers get a single `resRead(res)` regardless of which case fired.

## Post-processing

```scala
override def postprocess[R](block: Block[R]): Block[R] = {
  spatialConfig.allowPrimitivesInOuterControl = false
  super.postprocess(block)
}
```
(`:317-321`). This flips a global flag that every subsequent pass can read — `CompilerSanityChecks` uses it to enforce that no downstream pass accidentally reintroduces mixed primitives+controllers.

## Runs in the pipeline

The canonical pipeline runs `PipeInserter` three times:

1. **First run** (`src/spatial/Spatial.scala:190`): after the second lowering round (`switchTransformer`, `switchOptimizer`, `memoryDealiasing`, optional `laneStaticTransformer`). This is the primary run — most of the IR is freshly lowered and mixed.
2. **Second run** (`src/spatial/Spatial.scala:144` inside `streamify` block): gated on `spatialConfig.streamify`. After `HierarchicalToStream` rewrites outer controllers into streaming FIFO trios, some stream bodies end up with mixed content and need re-piping.
3. **Third run** (`src/spatial/Spatial.scala:138` inside `fifoInitialization = Seq(fifoInitializer, pipeInserter, MetadataStripper(state, S[FifoInits]))`): after `FIFOInitializer` emits init controllers for any FIFO whose `fifoInits` metadata is set.

All three runs set `allowPrimitivesInOuterControl = false` as their postcondition — the flag remains false for the rest of the pipeline.

## Holder allocation

`resFrom(s, parent)` (`:256-260`) picks the holder type:
```scala
def resFrom[A](s: Sym[A], parent: Sym[_]): Either[LocalMem[A,C], Var[A]] = s match {
  case b: Bits[_] if parent.isStreamControl => Left(memFrom(b, true))   // FIFOReg
  case b: Bits[_] =>                           Left(memFrom(b))          // Reg
  case _          =>                           Right(varFrom(s))         // Var
}
```

- For bit-valued escapees under a stream controller, allocate a `FIFOReg` with zero init (`:274`).
- For other bit escapees, allocate a `Reg` with zero init (`:275`).
- For non-bit escapees, allocate a Scala `Var` (`:298-305`).

`resWrite` / `resRead` (`:261-269`) dispatch on the holder type:
- FIFOReg: `fr.enq(data)` / `fr.deq()`.
- Reg: `reg.write(data)` / `reg.value`.
- Var: `Var.assign(x, data)` / `Var.read(x)`.

## Interactions

- Depends on **`SpatialFlowRules.controlLevel`** for `rawChildren`, `isOuterControl`, `rawLevel` (`flows/SpatialFlowRules.scala:165-173`).
- Depends on **`SpatialFlowRules.controlSchedule`** for `isParallel` / `isStreamControl` (`flows/SpatialFlowRules.scala:332`, `:389-396`).
- **`MemoryDealiasing`** must run before `PipeInserter` (`src/spatial/Spatial.scala:187`) so that alias-reads are already muxed DRAM accesses — otherwise `PipeInserter` would try to wrap alias reads as escaping values, which is meaningless.
- **`LaneStaticTransformer`** must run before `PipeInserter` (`src/spatial/Spatial.scala:188`) because `LaneStatic` nodes need to be in the pre-pipe block where the original iterator is still live.
- **`UnrollingTransformer`** runs after `PipeInserter` (`src/spatial/Spatial.scala:209`) and depends on the outer-mix invariant for its duplicate-controller vs. duplicate-primitive dispatch.
- **`RetimingTransformer`** reads the `Pipe`-emitted structure to compute delay-line placement (`transform/RetimingTransformer.scala:205-220`).

## HLS notes

Pipe insertion is **semantically structural** but **syntactically mutative**. A Rust+HLS reimplementation must:

1. Walk every outer-control block post-lowering and classify stmts.
2. Emit new `Pipe` / `UnitPipe` constructs around inner-stage runs.
3. Route escaping bit values through register-like holders — HLS synthesis tools often handle this automatically via static single-assignment, so the Rust side can emit raw SSA and let the HLS tool inject registers as needed.
4. Preserve the `enable` chain through nested `Pipe`s (critical for SwitchCase-wrapping).

HLS status: **rework**. The algorithm itself is clean (a ~150-line structural walk), but the `Reg`/`FIFOReg`/`Var` holder machinery is deeply tied to Spatial's IR. A Rust rewrite would likely emit HLS-native `hls::stream` or `ap_shift_reg` types for escapees instead.

## Open questions

- Q-007 — exact semantics of the `Switch` branch's `requiresWrap` guard when a case has primitives but no controllers: in that case, `insertPipes` is called with `scoped = false`, which means stmts are emitted directly into the enclosing scope. Is this always safe, or can it violate the outer-mix invariant of the enclosing controller?
