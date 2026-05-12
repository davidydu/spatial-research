---
type: spec
concept: unrolling
source_files:
  - "src/spatial/transform/UnrollingTransformer.scala"
  - "src/spatial/transform/unrolling/UnrollingBase.scala:1-527"
  - "src/spatial/transform/unrolling/ForeachUnrolling.scala:1-89"
  - "src/spatial/transform/unrolling/ReduceUnrolling.scala:1-266"
  - "src/spatial/transform/unrolling/MemReduceUnrolling.scala:1-377"
  - "src/spatial/transform/unrolling/MemoryUnrolling.scala:1-581"
  - "src/spatial/transform/unrolling/SwitchUnrolling.scala:1-20"
  - "src/spatial/Spatial.scala:209"
  - "src/spatial/Spatial.scala:108"
source_notes:
  - "[[pass-pipeline]]"
hls_status: rework
depends_on:
  - "[[70 - Banking]]"
  - "[[Counters and CounterChain]]"
  - "[[50 - Pipe Insertion]]"
status: draft
---

# Unrolling

## Summary

`UnrollingTransformer` replicates loop bodies according to the per-counter parallelism factors, per-memory dispatches computed by banking, and the MoP-vs-PoM user choice. It is a composition class — `UnrollingTransformer` has no body, it just mixes the 6 concrete trait unrollers over `UnrollingBase`. The dispatch is in `UnrollingBase.transform` which defers to `unroll(lhs, rhs)`; this branches on `rhs.isControl` (then `duplicateController` wraps ≥2 copies in a `ParallelPipe`) vs. `lanes.duplicate` for primitives. Four specialized `Unroller` subtypes (`UnitUnroller`, `LoopUnroller` with `PartialUnroller` and `FullUnroller`, and a vectorization mode controlled by `spatialConfig.vecInnerLoop`) handle the per-lane substitution bookkeeping.

Post-condition: loop controllers are `UnrolledForeach` / `UnrolledReduce`; local memories are duplicated per `Dispatch` metadata; banked access nodes are `SRAMBankedRead`, `FIFOBankedEnq`, etc.

## Class hierarchy

`src/spatial/transform/UnrollingTransformer.scala` (referenced at `Spatial.scala:108`) is a trivial case class:

```scala
case class UnrollingTransformer(IR: State) extends UnrollingBase
  with ForeachUnrolling with ReduceUnrolling with MemReduceUnrolling
  with MemoryUnrolling with SwitchUnrolling with BlackBoxUnrolling
```

Each trait specializes `unrollCtrl[A](lhs, rhs, mop)` or `unroll[T](lhs, rhs)` for a specific `Op` subtype.

`UnrollingBase` (`transform/unrolling/UnrollingBase.scala:27`) extends `MutateTransformer with AccelTraversal`. Key state:
- `enables: Set[Bit]` — the valid bits in scope.
- `unrollNum: Map[Idx, Seq[Int]]` — maps each pre-unroll iterator to the lane indices it covers (`:60`).
- `memories: Map[(Sym[_], Int), Sym[_]]` — the `(orig mem, dispatch) → new mem` substitution table (`:72`).
- `lanes: Unroller` — the current lane context (default `UnitUnroller("Accel", isInnerLoop=false)` at `:76`).
- `laneMapping: Map[(Unroller, Int), Seq[Block[_]]]` — maps each lane to per-lane body blocks (PoM only, `:79`).

## The `Unroller` trait and subclasses

`trait Unroller` (`UnrollingBase.scala:242-421`) is the lane-context abstraction. Per-instance:

- `def inds: Seq[Idx]` — pre-unroll iterators (empty for `UnitUnroller`).
- `def Ps: Seq[Int]` — parallelism factor per counter level.
- `def mop: Boolean` — metapipe-of-parallels (true, default) vs parallel-of-metapipes (false).
- `def vectorize: Boolean` — inner-loop vectorization mode.
- `def P: Int = if (vectorize) 1 else Ps.product` — number of physical lanes (1 if vectorized).
- `def V: Int = if (vectorize) Ps.product else 1` — vector width (Ps.product if vectorized).
- `def N: Int = Ps.length` — number of counter levels.

Three subclasses:

### `UnitUnroller(name, isInnerLoop)` (`:517-524`)

Single-lane, no iterators. `Ps = Seq(1)`, `inds = Nil`, `mop = false`, `vectorize = false`, `contexts` is a single empty substitution map. Used as the default outer-scope lane context.

### `LoopUnroller` base trait (`:423-487`)

Parameterized by `cchain: CounterChain`, `isInnerLoop: Boolean`, `mop: Boolean`. Adds:

- `val vectorize = isInnerLoop && spatialConfig.vecInnerLoop` (`:434`) — vectorization only fires on inner loops when the PIR/Plasticine flag is on.
- `val Ps = cchain.pars.map(_.toInt)` (`:435`) — parallelism from the counter chain.
- `protected def createLaneValids(): Seq[Seq[Bit]]` — builds per-lane valid-bit sequences via `ulanes.map { lane => ... }` at `:437-444`.
- `val contexts: Array[Map[Sym[_], Sym[_]]]` (`:447-454`) — one substitution map per ulane, each seeded with `inds.zip(inds2)` where `inds2` is computed from `parAddr(p)` for MoP or from `indices(p)` directly for PoM.
- `def createBounds[T](bound)` (`:459-486`) — creates bound vars (iterator indices) for every (counter, lane) pair, tagged with `IndexCounterInfo(ctr, ctrIdxs)`.

### `PartialUnroller` and `FullUnroller`

```scala
case class PartialUnroller(name, cchain, inds, isInnerLoop, mop) extends LoopUnroller {
  lazy val indices = createBounds { (ctr, lane) => boundVar[I32] }
  lazy val indexValids = createBounds { (ctr, lane) => boundVar[Bit] }
}
case class FullUnroller(name, cchain, inds, isInnerLoop, mop) extends LoopUnroller {
  lazy val indices = createBounds {
    case (ctr, List(i)) => I32(ctr.start.toInt + ctr.step.toInt*i)
    case (ctr, ctrIdxs) => val i = boundVar[I32]; i.vecConst = ctrIdxs.map{ i => FixedPoint.fromInt(ctr.start.toInt + ctr.step.toInt*i) }; i
  }
  lazy val indexValids = if (mop) indices.zip(cchain.counters).map{case (is,ctr) => is.map { case Const(i) => Bit(i < ctr.end.toInt); case VecConst(is) => ... }} else ... 
}
```

`PartialUnroller` (`:489-492`) creates fresh bound vars for each lane — iterators remain dynamic. `FullUnroller` (`:494-515`) materializes constants when possible — iterators become `Const(ctr.start + ctr.step*i)` (or `VecConst` of such when vectorized). Used when `cchain.willFullyUnroll`.

## MoP vs. PoM semantics

**Metapipe-of-Parallels (MoP)** — default, `--mop`. An outer loop with par=P unrolls into a single loop with a `ParallelPipe` body containing P copies of each stage. In `UnrollingBase.duplicateController` at `:150-178`:

```scala
if (lanes.size > 1) {
  val block = stageBlock {
    lanes.foreach{ lns =>
      val x = duplicate()
    }
  }
  val lhs2 = stage(ParallelPipe(enables, block))
  lanes.unify(lhs, lhs2)
}
```

The duplicated controllers are wrapped in a `ParallelPipe` scope.

**Parallel-of-Metapipes (PoM)** — `--pom`. The outer loop is split into P separate metapipes, each running `(0 until N) by P` starting from a different offset. PoM requires per-lane sub-counterchains via `crossSection(cchain, parAddr(p))` at `UnrollingBase.scala:100-112`:

```scala
def crossSection(cchain, addr: List[Int]): CounterChain = {
  val ctrs2 = cchain.counters.zip(addr).map{case (ctr, i) =>
    val start = ctr.start.asInstanceOf[I32] match { case Const(c) => c.toInt; ... }
    val step = ...
    val newStart = start + i.to[I32] * step
    val newStep = step * ctr.ctrParOr1
    Counter[I32](newStart, ctr.end, newStep, 1)
  }
  stage(CounterChainNew(ctrs2))
}
```

Throws if `ctr.start` is not a `Const`/`Final`/`Expect` (`:105`). Per-lane bodies are staged separately; this is used in `ForeachUnrolling.fullyUnrollForeach` at `:39-50` and `partiallyUnrollForeach` at `:72-85`.

Config gates at `src/spatial/Spatial.scala:404-438`. The `--mop` and `--pom` flags set `spatialConfig.unrollMetapipeOfParallels` and `spatialConfig.unrollParallelOfMetapipes`. The actual per-controller MoP/PoM decision is via `lhs.willUnrollAsPOM` (checked in `UnrollingBase.unroll` at `:128`: `val mop = !lhs.willUnrollAsPOM`).

## Vectorization

Inner-loop vectorization is guarded by `vectorize = isInnerLoop && spatialConfig.vecInnerLoop` (`UnrollingBase.scala:434`). Effects:

- `P = 1`, `V = Ps.product` — a single "vectorized lane" with width `Ps.product` (`:252-253`).
- `ulanes = List(List.tabulate(V)(i => i))` — one lane containing all vector slots (`:260-263`).
- `createBounds` in `FullUnroller` materializes `VecConst(ctrIdxs.map{i => FixedPoint.fromInt(ctr.start + ctr.step*i)})` for vectorized indices (`:497`).

`--pir` and `--tsth` flags both enable `vecInnerLoop = true` (`Spatial.scala:314, 332`). PoM is not supported under `enablePIR`: `if (spatialConfig.enablePIR) error(s"TODO: Plasticine doesn't support POM yet")` (`:471-474`).

## Per-controller unrollers

### `ForeachUnrolling` (`ForeachUnrolling.scala`)

`OpForeach` → `UnrolledForeach` or `UnitPipe` + optional `ParallelPipe`. Branch on `cchain.willFullyUnroll`:
- `fullyUnrollForeach` (`:21-51`) — builds a `FullUnroller`, then:
  - If `mop || unrLanes.size == 1 || lhs.isInnerControl`: emit a single `UnitPipe(newEns, blk, stopWhen)` with `unrollBy = unrLanes.Ps.product`.
  - Else (PoM on an outer foreach): emit a `ParallelPipe` of per-lane `UnitPipe`s, each with its own `crossSection` counter chain.
- `partiallyUnrollForeach` (`:53-86`) — similar structure but emits `UnrolledForeach(newEns, cchain, blk, is, vs, stopWhen)` preserving the counter chain.

### `ReduceUnrolling` (`ReduceUnrolling.scala`)

`OpReduce` → `UnrolledReduce` or `UnitPipe`. Branch on `cchain.willFullyUnroll`:
- `fullyUnrollReduce` (`:35-83`) — emits a nested `UnitPipe` around a `redLanes = UnitUnroller(...)` scope that stages the reduction tree via `unrollReduceTree` (`:152-168`). For inner-reduce, calls `pirUnrollInnerReduce` on PIR to match the PIR pattern (`:241-263`).
- `partiallyUnrollReduce` (`:85-128`) — stages a `UnrolledReduce` with its own `UnitPipe`-wrapped inner body. Sets `accum.accumType = AccumType.Reduce` (`:126`).
- `accumHack(orig, load)` (`:132-150`) — a hack to find the accumulator's post-unroll duplicate: finds the reader in the load block, extracts `reader.dispatches`, uses `memories((orig, dispatch))` to get the unrolled accumulator.

The reduction tree helper:
```scala
def unrollReduceTree[A:Bits](inputs, valids, ident, rfunc) = ident match {
  case Some(z) => inputs.zip(valids).map{case (in,v) => mux(v, in, z) }.reduceTree(rfunc)
  case None    => inputs.zip(valids).reduceTree{case ((x,x_en), (y,y_en)) => 
                    (mux(y_en, rfunc(x,y), x), x_en | y_en) }._1
}
```
(`:152-168`). With identity, invalid inputs become the identity value; without, a validity bit is propagated and multiplexed through the tree.

### `MemReduceUnrolling` (`MemReduceUnrolling.scala`)

Four combinations of fully-unrolled map/reduce counterchains, branching on `cchainMap.willFullyUnroll && cchainRed.willFullyUnroll` (`:20-31`):
- **Both full**: `fullyUnrollMemReduceAndMap` (`:36-89`) — nested `UnitPipe`s.
- **Map full only**: `fullyUnrollMemReduceMap` (`:156-212`) — outer `UnitPipe`, inner `UnrolledForeach(Set.empty, cchainRed, rBlk, isRed2, rvs, None)`.
- **Reduce full only**: `fullyUnrollMemReduce` (`:91-153`) — outer `UnrolledReduce(enables ++ ens, cchainMap, blk, isMap2, mvs, stopWhen)`, inner `UnitPipe`.
- **Neither full**: `partiallyUnrollMemReduce` (`:214-277`) — outer `UnrolledReduce`, inner `UnrolledForeach`.

`unrollMemReduceAccumulate` (`:280-375`) is the shared accumulation engine. Handles load-accumulator, reduction-tree construction, first-iteration handling via `isFirst = iters.map(_===start).andTree` (`:340`), and stores. On fully-unrolled reduce (`redLanes.isInstanceOf[FullUnroller]`), it explicitly removes segment mapping and iter-diff metadata from the accumulator, store result, and load result (`:298-308`) because the whole cycle will be unrolled out of existence.

### `MemoryUnrolling` (`MemoryUnrolling.scala`) — 581 lines

The largest single unroller. Handles `MemAlloc`, `StatusReader`, `Resetter`, `Accessor`, `ShuffleOp`. Top-level dispatch at `:15-38`:

```scala
override def unroll[T:Type](lhs, rhs) = rhs match {
  case _: MemAlloc[_,_] if lhs.isRemoteMem => unrollGlobalMemory(lhs, rhs)
  case _: MemAlloc[_,_] if lhs.isLocalMem  => unrollMemory(lhs)
  case op: StatusReader[_] => unrollStatus(lhs, op)
  case op: Resetter[_]     => unrollResetter(lhs.asInstanceOf[Sym[Void]], op)
  case op: Accessor[_,_]   => unrollAccess(lhs, op)
  case op: ShuffleOp[_]    => unrollShuffle(lhs, op)
  case _ => super.unroll(lhs, rhs)
}
```

- `duplicateMemory(mem)` (`:67-81`) — iterates `mem.duplicates.zipWithIndex`, mirrors each, sets `mem2.instance = inst`, renames via `mem2.name = Some(s"${x}_$d")`, copies `padding`, returns `Seq[(Sym[_], Int)]`.
- `unrollMemory(mem)` (`:86-93`) — calls `lanes.duplicateMem(mem){_ => duplicateMemory(mem)}`, which populates `lanes.memContexts` per lane with the `(orig, dispatch) → new mem` mapping. Returns `Nil` because there's no single default mem substitution (each access picks its own).
- `unrollAccess(lhs, rhs)` (`:165-340`) — the bulk of the file. For each required `UnrollInstance` (dispatched, laneIds, port, grpids, vecOfs), computes:
  - **Addresses** via `bankSelects` (`:342-363`) and `bankOffset` (`:365-382`), which call `inst.bankSelects(mem, laneAddr)` / `inst.bankOffset(mem, laneAddr)` using the per-instance banking from `MemoryConfigurer`.
  - **Enables** via `masters.map{t => lanes.inLanes(laneIds){p => f(rhs.ens) ++ lanes.valids(p)}(laneIdToChunkId(t))}` (`:229`).
  - **Banked-access node emission** via `bankedAccess(rhs, mem2, data2, bank, ofs, lock, ens2)` (`:509-577`). This is the big switch: `FIFODeq → FIFOBankedDeq`, `SRAMRead → SRAMBankedRead`, `SRAMWrite → SRAMBankedWrite`, `RegFileRead → RegFileVectorRead`, `LUTRead → LUTBankedRead`, `LineBufferEnq → LineBufferBankedEnq`, etc. Total ~40 cases.
  - **Port metadata** via `s.addPort(dispatch=0, Nil, port2)` and `s.addDispatch(Nil, 0)` (`:290-299`).
  - **Segment-mapping** for fractured accesses via `lhs.segmentMapping.groupBy(_._2).map{…}` (`:240-256`).
- `getInstances(access, mem, isLoad, len)` (`:395-487`) — critical helper. Iterates `lanes.map{lane => …}`, for each lane computes all `dispatches` via `access.dispatch(vid)` and grpids via `access.gid(vid)`, builds `UnrollInstance`s, then groups by memory duplicate and further by `(bufferPort, muxPort)`. Within each port group, merges contiguous vector sections into single vector accesses.

Key type `UnrollInstance` at `:133-140`:
```scala
case class UnrollInstance(
  memory: Sym[_], dispIds: Seq[Int], laneIds: Seq[Int],
  port: Port, grpids: Set[Int], vecOfs: Seq[Int]
)
```

### `SwitchUnrolling` (`SwitchUnrolling.scala`)

20 lines. Overrides `unroll` for inner-control `Switch`es: `lanes.map{p => val lhs2 = unrollCtrl(lhs, rhs, true); register(lhs -> lhs2); lhs2}` (`:10-16`). Each lane gets its own copy of the inner Switch.

### `BlackBoxUnrolling` (`transform/unrolling/BlackBoxUnrolling.scala`)

Empty stub trait (coverage §2). No overrides.

## Core dispatch

`UnrollingBase.transform` (`:180-187`):

```scala
final override def transform[A:Type](lhs, rhs)(implicit ctx): Sym[A] = rhs match {
  case _:AccelScope => inAccel{ super.transform(lhs, rhs) }
  case _:SpatialCtrlBlackboxImpl[_,_] => inBox{ super.transform(lhs, rhs) }
  case _ =>
    val duplicates: List[Sym[_]] = unroll(lhs, rhs)
    if (duplicates.length == 1) duplicates.head.asInstanceOf[Sym[A]]
    else Invalid.asInstanceOf[Sym[A]]
}
```

All non-Accel ops go through `unroll(lhs, rhs)`, which returns a List of duplicates. If length == 1, that's the substitution; else `Invalid` is returned and the caller (the substitution machinery) picks the right duplicate via `memories((orig, dispatch))` lookup.

`unroll` at `:126-133`:
```scala
def unroll[A:Type](lhs, rhs)(implicit ctx): List[Sym[_]] = {
  val mop = !lhs.willUnrollAsPOM
  val lhs2 = if (rhs.isControl) duplicateController(lhs, rhs, mop)
             else lanes.duplicate(lhs, rhs)
  lhs2
}
```

`lanes.duplicate` at `:360-374`:
```scala
final def duplicate[A](s: Sym[A], d: Op[A]): List[Sym[_]] = {
  if (size > 1 || copyMode) map{ lns => val s2 = mirror(s, d); register(s -> s2); s2 }
  else mapFirst { val s2 = mirror(s, d); register(s -> s2); List(s2) }
}
```

## Interactions

- **Pre-reqs**: `MemoryAnalyzer` must have set `Duplicates`/`Dispatch`/`Ports` on every local memory (`traversal/banking/MemoryConfigurer.finalize` at `traversal/banking/MemoryConfigurer.scala:115-163`). `PipeInserter` must have established the outer-mix invariant. `CounterIterSynchronization` must have set `IndexCounterInfo` on every iter (`Spatial.scala:204`).
- **Post-cleanup**: after unrolling, `regReadCSE` runs again (`Spatial.scala:211`) and `DCE` + `retimingAnalyzer` (`Spatial.scala:213`) recompute retime delays because the graph is entirely different.
- **`MemoryCleanupTransformer`** after `rewriteTransformer` drops any duplicates whose unrolling produced no readers/writers (`Spatial.scala:218`).
- **`BufferRecompute`** post-unrolling recomputes N-buffer depths based on new post-unroll port assignments (`Spatial.scala:222`).

## HLS notes

Unrolling is the most intricate pass in the pipeline. HLS status: **rework**. Key rewrite challenges:
1. The `Unroller` lane-context abstraction with `contexts: Array[Map[Sym[_], Sym[_]]]` is a classic compiler-time construct. Rust's borrow checker will demand extensive lifetime annotations.
2. Vectorization emits `VecConst` constant arrays — these map naturally to HLS `ap_int<N*W>` wide data types.
3. Per-lane-substitution via `isolateSubst` + `register(s → s2)` is argon-specific; a Rust IR will need an equivalent lane-scoped substitution table.
4. `MemoryUnrolling.bankedAccess` has ~40 cases, one per memory/access type pair. Porting requires mirroring every access node in the Rust IR.

## Open questions

- Q-010 (existing) — relationship between `EarlyUnroller` (used inside streamify) and the main unrolling transformer.
- Q-007 — whether `fullyUnrollForeach` and `partiallyUnrollForeach`'s `mop || isInnerControl || size == 1` short-circuit at `:33` always reaches the single-`UnitPipe`/`UnrolledForeach` path; specifically, the PoM path only fires on outer partially-unrolled loops.
