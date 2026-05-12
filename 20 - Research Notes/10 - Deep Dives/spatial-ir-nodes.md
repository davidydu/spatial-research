---
type: deep-dive
topic: spatial-ir-nodes
source_files:
  - "src/spatial/node/HierarchyControl.scala"
  - "src/spatial/node/HierarchyMemory.scala"
  - "src/spatial/node/HierarchyAccess.scala"
  - "src/spatial/node/HierarchyUnrolled.scala"
  - "src/spatial/node/Control.scala"
  - "src/spatial/node/Switch.scala"
  - "src/spatial/node/Reg.scala"
  - "src/spatial/node/SRAM.scala"
  - "src/spatial/node/RegFile.scala"
  - "src/spatial/node/FIFO.scala"
  - "src/spatial/node/LIFO.scala"
  - "src/spatial/node/LUT.scala"
  - "src/spatial/node/LineBuffer.scala"
  - "src/spatial/node/MergeBuffer.scala"
  - "src/spatial/node/DRAM.scala"
  - "src/spatial/node/LockMem.scala"
  - "src/spatial/node/StreamIn.scala"
  - "src/spatial/node/StreamOut.scala"
  - "src/spatial/node/StreamStruct.scala"
  - "src/spatial/node/Accumulator.scala"
  - "src/spatial/node/Fringe.scala"
  - "src/spatial/node/DenseTransfer.scala"
  - "src/spatial/node/SparseTransfer.scala"
  - "src/spatial/node/Frame.scala"
  - "src/spatial/node/FrameTransmit.scala"
  - "src/spatial/node/Blackbox.scala"
  - "src/spatial/node/Transient.scala"
  - "src/spatial/node/DelayLine.scala"
  - "src/spatial/node/LaneStatic.scala"
  - "src/spatial/node/Shuffle.scala"
  - "src/spatial/node/Mux.scala"
  - "src/spatial/node/Array.scala"
  - "src/spatial/node/FileIO.scala"
  - "argon/src/argon/Op.scala"
  - "argon/src/argon/node/DSLOp.scala"
  - "argon/src/argon/node/Enabled.scala"
session: 2026-04-23
status: ready-to-distill
feeds_spec:
  - "[[10 - Controllers]]"
  - "[[20 - Memories]]"
  - "[[30 - Memory Accesses]]"
  - "[[40 - Counters and Iterators]]"
  - "[[50 - Primitives]]"
  - "[[60 - Streams and Blackboxes]]"
---

# Spatial IR Nodes — Deep Dive

## Reading log

Order of files opened during this session and the questions each answered:

1. `argon/src/argon/Op.scala:13-126` — to understand the base class contracts (`Op[R]`, `Op2/3/4`, `AtomicRead` trait) that every node inherits. Key: `Op[R]` is not covariant in `R`; exposes `inputs`, `blocks`, `binds`, `aliases`, `contains`, `extracts`, `copies`, `effects`, `rewrite`, `mirror`, `update`. Defaults compute most fields from the Scala case-class `productIterator`.
2. `argon/src/argon/node/DSLOp.scala:6-37` — layers above `Op[R]`. `DSLOp[R]` adds `canAccel: Boolean = true`; `Primitive[R]` adds `isTransient: Boolean = false`; `EnPrimitive[R]` mixes in `Enabled`; `Alloc[T]` marks any boxed allocation. `Primitive` is flagged as "somewhat Spatial specific" in a TODO (line 11).
3. `argon/src/argon/node/Enabled.scala:6-21` — the `Enabled` trait carries a `var ens: Set[Bit]`, plus `mirrorEn` and `updateEn` overrides for pulling enables inward when mirroring.
4. `src/spatial/node/HierarchyControl.scala:1-85` — the control-node abstract stack: `FringeNode[A,R]`, `ControlBody` sum type (`PseudoStage`, `OuterStage`, `InnerStage`), `Control[R]`, `EnControl[R]`, `Pipeline[R]`, `Loop[R]`, `UnrolledLoop[R]`.
5. `src/spatial/node/HierarchyMemory.scala:1-120` — `MemAlloc[A,C]` base for every memory; `MemAlias`/`MemDenseAlias`/`MemSparseAlias`; dimension-query transients `MemStart`, `MemStep`, `MemEnd`, `MemPar`, `MemLen`, `MemOrigin`, `MemDim`, `MemRank`.
6. `src/spatial/node/HierarchyAccess.scala:1-156` — the pre-unroll access hierarchy: `Access`, `Read`, `Write`, `StatusReader`, `Resetter`, `Accessor`, `Reader`, `DequeuerLike`, `Dequeuer`, `VectorDequeuer`, `Writer`, `EnqueuerLike`, `Enqueuer`, `VectorEnqueuer`.
7. `src/spatial/node/HierarchyUnrolled.scala:1-154` — the post-unroll hierarchy: `UnrolledAccess`, `BankedRead`/`BankedWrite`, `VectorRead`/`VectorWrite`, `UnrolledAccessor`, `BankedAccessor`, `VectorReader`, `BankedReader`, `BankedDequeue`, `VectorWriter`, `BankedWriter`, `BankedEnqueue`, `Accumulator`.
8. Control node concretizations: `src/spatial/node/Control.scala:9-143` (`CounterNew`, `CounterChainNew`, `ForeverNew`, `AccelScope`, `UnitPipe`, `ParallelPipe`, `OpForeach`, `OpReduce`, `OpMemReduce`, `StateMachine`, `UnrolledForeach`, `UnrolledReduce`) and `src/spatial/node/Switch.scala:11-70` (`SwitchScheduler`, `SwitchCase`, `Switch`).
9. Memory-alloc concretizations: `src/spatial/node/Reg.scala:7-61` (`RegAlloc`, `RegNew`, `FIFORegNew`, `ArgInNew`, `ArgOutNew`, `HostIONew`, all register accessors), `src/spatial/node/SRAM.scala:10-70` (`SRAMNew`, `SRAMRead`, `SRAMWrite`, `SRAMBankedRead`, `SRAMBankedWrite`), `src/spatial/node/RegFile.scala:10-131` (scalar/vector reads+writes + shift-in variants + reset), `src/spatial/node/FIFO.scala:7-71` (`FIFONew` with `resize`, scalar/vector/banked/priority variants), `src/spatial/node/LIFO.scala:7-34`, `src/spatial/node/LUT.scala:10-49`, `src/spatial/node/LineBuffer.scala:7-30`, `src/spatial/node/MergeBuffer.scala:8-28`.
10. Off-chip & lock variants: `src/spatial/node/DRAM.scala:9-45`, `src/spatial/node/LockMem.scala:8-146`, `src/spatial/node/Frame.scala:9-35`.
11. Stream surfaces: `src/spatial/node/StreamIn.scala:7-20`, `src/spatial/node/StreamOut.scala:7-27`, `src/spatial/node/StreamStruct.scala:8-22`.
12. Transfer lowerings: `src/spatial/node/DenseTransfer.scala:34-394`, `src/spatial/node/SparseTransfer.scala:27-175`, `src/spatial/node/FrameTransmit.scala:26-89`, `src/spatial/node/Fringe.scala:7-66`.
13. Non-memory primitives: `src/spatial/node/Mux.scala:9-57`, `src/spatial/node/Shuffle.scala:8-26`, `src/spatial/node/DelayLine.scala:8-14`, `src/spatial/node/LaneStatic.scala:7-15`, `src/spatial/node/Transient.scala:10-19`.
14. Accumulators: `src/spatial/node/Accumulator.scala:9-57`.
15. Blackboxes: `src/spatial/node/Blackbox.scala:8-62`.
16. Host ops: `src/spatial/node/Array.scala:8-123`, `src/spatial/node/FileIO.scala:7-59`.
17. DSL layer for staging context: `src/spatial/lang/types/Mem.scala:9-50` (`Mem`, `TensorMem`, `RemoteMem`, `LocalMem`), selected `src/spatial/lang/Reg.scala`, `src/spatial/lang/SRAM.scala`, `src/spatial/lang/FIFO.scala`, `src/spatial/lang/Counter.scala`, `src/spatial/lang/CounterChain.scala`, `src/spatial/lang/control/*` (`AccelClass`, `ForeachClass`, `ReduceClass`, `MemReduceClass`, `FSM`, `Parallel`).
18. Metadata edges: `src/spatial/metadata/control/ControlData.scala:1-160` (for `rawSchedule`/`rawLevel`/`rawChildren`/etc. types) and `src/spatial/metadata/control/package.scala:773-824` (accessors).

## Observations

### 1. The three abstract stacks

Spatial's IR nodes sit on three parallel abstract hierarchies, each layered on top of `argon.node`:

**Controllers.**
```
argon.node.DSLOp[R]            (argon/src/argon/node/DSLOp.scala:6-9)
  └── spatial.node.Control[R]     (HierarchyControl.scala:47-53)
        └── EnControl[R]           (HierarchyControl.scala:62, mixes argon.Enabled)
              └── Pipeline[R]      (HierarchyControl.scala:65, executes ≥ 1 time)
                    └── Loop[R]    (HierarchyControl.scala:68, executes ≥ 1 iteration)
                          └── UnrolledLoop[R]  (HierarchyControl.scala:72-85, post-unroll form)
```
`Control` overrides `inputs` to *exclude* `iters` and `binds` to *include* them (`HierarchyControl.scala:48-49`) so the scheduler treats loop induction variables as bound, not as dataflow dependencies of the container. `UnrolledLoop` adds `validss` (per-lane valid bits), reshapes `iters` into `iterss: Seq[Seq[I32]]`, and removes valids+iters from `inputs` by the same mechanism (`HierarchyControl.scala:79-80`).

Every `Control` must expose `iters: Seq[I32]`, `cchains: Seq[(CounterChain, Seq[I32])]`, and `bodies: Seq[ControlBody]` (`HierarchyControl.scala:50-52`). The `ControlBody` ADT (`HierarchyControl.scala:17-44`) distinguishes three stage shapes:

- `PseudoStage` — present for scheduling/metadata but doesn't become a hardware stage (`mayBeOuterStage: true`, `isPseudoStage: true`). Most single-block controllers use this.
- `OuterStage` — real outer controller stage.
- `InnerStage` — real inner controller stage (can never be outer).

`OpMemReduce` illustrates the body-list protocol (`Control.scala:97-100`): `PseudoStage(itersMap -> map)` followed by `InnerStage(itersMap ++ itersRed -> loadRes, itersRed -> loadAcc, itersMap ++ itersRed -> reduce, itersRed -> storeAcc)`. Iterator visibility differs per sub-block — the reduction tree sees both `itersMap` and `itersRed`, the accumulator-load sees only `itersRed`.

**Memories.** The `MemAlloc[A,C]` abstract class (`HierarchyMemory.scala:9-20`) is the common superclass for every memory allocation. It extends `argon.node.Alloc` (not `Primitive`), exposes `dims: Seq[I32]`, `nbits`, `rank: Seq[Int]`, and declares `effects = Effects.Mutable` by default (overridable with `mutable=false`, used for LUTs). A side-ADT `MemAlias[A,Src,Alias]` (`HierarchyMemory.scala:28-38`) describes views/slices over an existing allocation; concrete subclasses `MemDenseAlias` and `MemSparseAlias` can bundle multiple `mem`/`addr` slots with a `cond: Seq[Bit]` union (`HierarchyMemory.scala:48-110`).

**Accesses.** The pre-unroll stack (`HierarchyAccess.scala`) is:
```
argon.node.EnPrimitive[R]
  └── Accessor[A,R]       (line 45-53)
        ├── Reader[A,R]    (line 65-68) — defines localRead = Some(Read(mem,addr,ens))
        │     └── Dequeuer[A,R]  (line 92-94) — addr = Nil, effects = Writes(mem)
        │           └── VectorDequeuer[A]  (line 104)
        └── Writer[A]       (line 116-122) — defines localWrite = Some(Write(mem,data,addr,ens))
              └── Enqueuer[A] (line 136-138) — addr = Nil
                    └── VectorEnqueuer[A]  (line 148)
```
Additional leaves: `StatusReader[R:Bits]` (`HierarchyAccess.scala:18-28`) for queue/buffer metrics (`FIFOIsEmpty`, `FIFONumel`, etc.), `Resetter[A]` for reset-the-memory ops (`HierarchyAccess.scala:31-42`).

The post-unroll stack (`HierarchyUnrolled.scala`) parallels but augments with banking:
```
EnPrimitive[R]
  └── UnrolledAccessor[A,R]   (line 22-40) — var enss: Seq[Set[Bit]]; var ens: Set[Bit] = Set.empty (line 27)
        ├── VectorReader[A]    (line 72-76)
        ├── VectorWriter[A]    (line 105-111)
        ├── BankedAccessor[A,R] (line 58-61) — bank: Seq[Seq[Idx]], ofs: Seq[Idx]
        │     ├── BankedReader[A]  (line 86-89)
        │     │     └── BankedDequeue[A] (line 99-103) — bank=Nil, ofs=Nil, effects=Writes
        │     └── BankedWriter[A]  (line 121-126)
        │           └── BankedEnqueue[A] (line 136-139)
        └── Accumulator[A]     (line 143-154) — data=Nil; enss=Seq(en)
```

The pre-unroll nodes are emitted by the DSL layer (`Reg.write`, `SRAM.read`, etc. — each `stage(…)` call in `src/spatial/lang/*` produces one of these). Unrolling rewrites pre-unroll accesses into `BankedRead`/`BankedWrite`/`VectorRead`/`VectorWrite` variants with lane-specific `enss` and banking-resolved `bank: Seq[Seq[Idx]]`.

### 2. Base-class inheritance matters for scheduling

The distinction between extending `Alloc`, `Primitive`, `EnPrimitive`, or `DSLOp[R]` directly controls multiple compiler behaviors:

- **`Alloc[T]`** (`argon/src/argon/node/DSLOp.scala:29-37`) — "Allocation of any black box"; no implicit effects; `MemAlloc[A,C]` extends this (`HierarchyMemory.scala:12`) and manually overrides `effects = Effects.Mutable` when `mutable=true` (the default). `CounterNew`/`CounterChainNew`/`ForeverNew` also extend `Alloc` (`Control.scala:9-19`) and declare `Effects.Unique` — they're allocations that must survive DCE because counter identity matters.
- **`Primitive[R]`** — combinational, stateless, predicatable. `Transient[R]` is a Spatial-specific subclass that forces `isTransient = true` (`Transient.scala:10-12`). `DelayLine`, `Mux`, `OneHotMux`, `PriorityMux`, `ShuffleCompress`, `DRAMAddress`, `FrameAddress`, `MemStart`/`MemStep`/… all extend `Primitive`. `SimpleStreamStruct` extends `Primitive` with `isTransient = true` (`StreamStruct.scala:8-10`).
- **`EnPrimitive[R]`** — primitive plus an `ens: Set[Bit]` field via the `Enabled` trait. Every `Reader`/`Writer`/`Accessor` ultimately extends this (via `HierarchyAccess.scala:45-53`). Several allocation-adjacent ops also extend it: `DRAMAlloc`, `DRAMDealloc`, `FrameAlloc`, `FrameDealloc` (`DRAM.scala:23-32`, `Frame.scala:19-27`).
- **`DSLOp[R]`** — the "can be used in Accel" contract. `Control` extends `DSLOp[R]` directly (`HierarchyControl.scala:47`). `FringeNode[A,R]` extends `DSLOp[R]` (`HierarchyControl.scala:7-9`) and is used by the `Fringe*` DMA nodes. Several pure-host ops go through `Op`/`Op2`/`Op3`/`Op4` instead (the Array and FileIO nodes).

### 3. The Stage id = -1 convention and Ctrl hierarchy

A key cross-cutting fact: every `Ctrl` reference carries a stage index `stg`, and `Ctrl.Node(sym, -1)` denotes the "master" form (whole controller) while `Ctrl.Node(sym, k)` for `k >= 0` refers to body `k`. `OpMemReduce` has `bodies.length == 2` with one `PseudoStage` then an `InnerStage` whose four sub-blocks are indexed further. The `ScopeCtrl` metadata (`src/spatial/metadata/control/ControlData.scala:101-111`) always points to the logical stage; `ParentCtrl` can be more granular (line 87-99).

### 4. Effects classification

A survey of the `effects` overrides:

- Allocs (mutable memories): `Effects.Mutable` via `MemAlloc.effects` (`HierarchyMemory.scala:19`).
- Counter allocs: `Effects.Unique` (`Control.scala:11, 14, 18`) — prevents CSE.
- Writers and Enqueuers: `Effects.Writes(mem)` (`HierarchyAccess.scala:117`).
- Dequeuers: also `Effects.Writes(mem)` because dequeue mutates the FIFO's state (`HierarchyAccess.scala:80`).
- Accumulators: `Effects.Writes(mem)` (`HierarchyUnrolled.scala:152`).
- `RegRead`/`FIFORegDeq`: `Effects.Unique` AND `isTransient = true` (`Reg.scala:30-31, 40-41`) — multiple syntactic reads map to one hardware read wire; unique prevents CSE collapsing distinct reads.
- `AccelScope`: `Effects.Simple` added (`Control.scala:30`) to prevent removal ("TODO[5]" about Accel not technically needing simple-effect).
- `FringeDenseLoad`: `Effects.Writes(dataStream)`; `FringeDenseStore`: `Effects.Writes(ackStream, dram)` (`Fringe.scala:12, 21`).
- `Blackbox` impls: `Effects.Unique` (`Blackbox.scala:39, 44, 47`).
- `RetimeGate`: `Effects.Simple` (`DelayLine.scala:13`) — acts as a scheduling barrier.

### 5. Transient and rewrite rules

`Transient[R]` (`Transient.scala:10-12`) is a Spatial-specific extension over `argon.node.Primitive` that forces `isTransient = true`. The `Transient.unapply` extractor (`Transient.scala:14-18`) matches *any* Primitive whose `isTransient` is true OR any sym matched by `Expect(_)`. Several unrolling/retiming passes use this to detect nodes that can inline away.

The `rewrite` method lets nodes constant-fold themselves during staging. Examples:
- `Mux.rewrite` (`Mux.scala:11-16`) folds when selector is literal-true/false or branches are equal.
- `OneHotMux.rewrite` (`Mux.scala:21-36`) handles single-select, statically-true selects (with warn on multiple), and all-identical-values cases.
- `PriorityMux.rewrite` (`Mux.scala:41-56`) has a similar pattern but with the literal-true short-circuit commented out.
- `DelayLine.rewrite` (`DelayLine.scala:9`) folds size-0 delays.
- `LaneStatic.rewrite` (`LaneStatic.scala:14`) folds single-element lane maps.

### 6. Enabled mixin and en/ens semantics

`Enabled` (`argon/src/argon/node/Enabled.scala:6-21`) requires `var ens: Set[Bit]`. The mirror override adds enables inward when mirroring (useful in `If/Switch` lowering and in unrolling when a lane inherits an outer condition). The `UnrolledAccessor.mirrorEn` override in `HierarchyUnrolled.scala:32-39` extends this to per-lane `enss`. Note: `UnrolledAccessor.ens` is held at `Set.empty` and `enss` is authoritative for lane-level enables (`HierarchyUnrolled.scala:27-28`).

Several Readers/Writers use mutable `var ens: Set[Bit] = Set.empty` and override `updateEn`/`mirrorEn` to no-op the add path because the op carries no real enable wire (`Reg.scala:33-36`, `Reg.scala:51-53`, `Reg.scala:58-60`).

### 7. DSL staging boundary

Looking at `src/spatial/lang/control/ForeachClass.scala:26-33`:
```scala
val iters  = ctrs.map{_ => boundVar[I32] }
val cchain = CounterChain(ctrs)
cchain.counters.zip(iters).foreach{case (ctr, i) =>
  i.counter = IndexCounterInfo(ctr, Seq.tabulate(ctr.ctrParOr1){i => i}) }
stageWithFlow(OpForeach(Set.empty, cchain, stageBlock{ func(iters); void }, iters, opt.stopWhen)){…}
```

Key point: **the DSL layer binds iterators and counters together via `IndexCounterInfo` metadata** (`src/spatial/metadata/control/ControlData.scala:136` + accessor in `src/spatial/metadata/control/package.scala:1088-1099`). The lanes argument in `IndexCounterInfo` is `Seq.tabulate(ctr.ctrParOr1){i => i}` (so `[0, 1, ..., par-1]`) — this is the *lane index* mapping used later by the unroller.

### 8. Fringe lowering and transfers

`DenseTransfer`/`SparseTransfer`/`FrameTransmit` are `EarlyBlackbox[Void]` — they get lowered in the `blackboxLowering1/2` passes before DSE. Each exposes a `lower(old)` method that re-stages a `Stream { ... }` controller body built from `Fringe.denseLoad`/`sparseLoad`/`denseStore`/`sparseStore`:

- `DenseTransfer.transfer` (`DenseTransfer.scala:66-392`) does extensive burst-size handling: computes `bytesPerWord`, enforces `A.nbits * lastPar % 8 == 0` (line 97), checks parallelism against burst (line 98), enumerates aligned vs. unaligned paths, and emits command/data/ack streams.
- `SparseTransfer.transfer` (`SparseTransfer.scala:49-173`) gathers/scatters with a multiple-of-16 padding for non-PIR targets (lines 66-73).
- `FrameTransmit.transfer` (`FrameTransmit.scala:46-89`) checks `A.nbits % 8 == 0`, pulls `len` from the `FrameHostNew` op, warns if the on-chip memory is smaller than the frame, and either reads from or writes to an `AxiStream64` stream.

### 9. Memory taxonomy (`Mem`, `LocalMem`, `RemoteMem`, `TensorMem`)

From `src/spatial/lang/types/Mem.scala:9-50`:
- `Mem[A,C]` — base type for any memory; requires `A: Bits`.
- `TensorMem[A]` — mixin providing `dims`, `size`, `dim0..dim4`.
- `RemoteMem[A,C]` — DRAM-like; does not expose `__read`/`__write`/`__reset`.
- `LocalMem[A,C]` — on-chip; requires `__read(addr, ens)`, `__write(data, addr, ens)`, `__reset(ens)`.

Concrete mappings (from the `lang/` files):
- `Reg[A]` extends `LocalMem0[A,Reg]` (`src/spatial/lang/Reg.scala:9`).
- `SRAM[A,C]` extends `LocalMem[A,C] with TensorMem[A]` (`src/spatial/lang/SRAM.scala:10`).
- `FIFO[A]` extends `LocalMem1[A,FIFO]` (`src/spatial/lang/FIFO.scala:10-12`).
- `DRAM[A,C]` extends `RemoteMem[A,C] with TensorMem[A]` (`src/spatial/lang/DRAM.scala:8`).
- `StreamIn[A]`/`StreamOut[A]` extend `LocalMem0[A,StreamIn]` AND `RemoteMem[A,StreamIn]` (`src/spatial/lang/StreamIn.scala:9`, `src/spatial/lang/StreamOut.scala:10`) — this dual mixin is unusual and reflects that streams are accessed locally but represent off-chip edges.

### 10. Surprises

Captured as the session went:

1. `Accumulator.data = Nil` (`HierarchyUnrolled.scala:145`) — there's no IR symbol for the value being accumulated. The comment says "We don't actually have a symbol for data being written to the memory". This means accumulator nodes can't be tracked by the usual `localWrite.data` pipeline; DCE has to handle them specifically.
2. `SRAMNew` has no `RegAlloc`-like subclass (`SRAM.scala:10-14`) — only one case class, parameterized by `C[T]` to cover `SRAM1..SRAM5`. `RegNew`/`ArgInNew`/`ArgOutNew`/`HostIONew` all share a `RegAlloc[A,C]` base (`Reg.scala:7-9`) because they all carry an `init` expression.
3. The `resize` method on `FIFONew` (`FIFO.scala:9-18`) mutates the node's `depth` in place via `update`. This lets a later pass (pipe insertion? memory dealiasing?) resize FIFO capacity after it's been staged.
4. `StreamIn[A]`/`StreamOut[A]` extend *both* `LocalMem0` and `RemoteMem` — they're local for access purposes but remote for allocation/lifetime (`StreamIn.scala:9`, `StreamOut.scala:10`).
5. `SwitchScheduler` is a custom scheduler (`Switch.scala:11-30`) that motions all operations *except* `SwitchCase` subtrees out of a `Switch` body. Any pass that re-schedules inside a switch must preserve `BlockOptions(sched = Some(SwitchScheduler))`.
6. `FieldEnq` (`StreamStruct.scala:19-22`) has a `// TODO: FieldEnq may not actually be used anywhere` comment — dead code candidate but currently live in the IR surface.
7. `FrameTransmit` hardcodes a fallback `(tid=0, tdest=0)` when the stream isn't an `AxiStream64Bus` (`FrameTransmit.scala:79`). Silent fallback rather than a warning.
8. The `data: Bits[A]` field in `Writer`-derived nodes (e.g., `SRAMWrite`, `RegWrite`) takes `Bits[A]` not `Sym[A]` — this is a typeclass-style constraint that happens to encompass both literals and symbols because `Bits[A]` is the boxed-value type.
9. `LockDRAM*` accesses carry `lock: Option[LockWithKeys[I32]]` (`LockMem.scala:19-103`). The locking semantics are attached via this opaque option, and the banking/dispatch analysis has hardcoded handling of these that returns empty banking and `dispatch = {0}` (per the coverage note).
10. `BankedDequeue` has `bank: Seq[Seq[Idx]] = Nil, ofs: Seq[Idx] = Nil` (`HierarchyUnrolled.scala:100-103`) — it inherits `BankedReader` but populates banking fields as empty, because dequeue has no address.
11. `SimpleStreamStruct` is `isTransient = true` (`StreamStruct.scala:9`) — it's a compile-time field grouping, not actual hardware.
12. `StateMachine.bodies` has `InnerStage` followed by two `PseudoStage`s (`Control.scala:113-117`) — only the condition check `notDone` is a real hardware stage; action and next-state are pseudo. This asymmetry must affect FSM codegen.
13. The `OneHotMux.rewrite` warn-on-multiple-true-selects fires *inside staging* (`Mux.scala:25-28`), which is unusual — most IR nodes defer diagnostics to an analyzer.
14. `GEMMBox` is a `FunctionBlackbox` (`Blackbox.scala:18-35`) staged by `Blackbox.GEMM` at `src/spatial/lang/Blackbox.scala:101-119`. It's a controller-node-like blackbox with a counterchain, and has `Effects.Writes(y)` — it doesn't lower, it stays as a blackbox.

## Open questions

Filed into `20 - Open Questions.md` as Q-007..Q-012 at the end of this session:

1. Is `FIFONew.resize` called elsewhere in the pipeline, and if so, does it race with already-analyzed banking of the FIFO?
2. `Accumulator.data = Nil` means the accumulator node has no syntactic `data` sym — is there any analysis/codegen that assumes `localWrite.map(_.data)` is populated for *all* writers? If so, accumulators silently break that assumption.
3. `StateMachine.bodies` has an `InnerStage` for the not-done condition but `PseudoStage` for action and next-state — is this intentional, and does any pass need to treat the three sub-blocks as one logical FSM rather than three distinct scopes?
4. `FieldEnq` (`StreamStruct.scala:19-22`) — confirm whether it's ever staged; if not, delete to reduce spec surface.
5. `FrameTransmit`'s silent fallback `(tid=0, tdest=0)` (`FrameTransmit.scala:79`) — should this be a user-visible warning or an error when the stream is not an AxiStream64Bus?
6. `SRAMBankedWrite` and `LockSRAMBankedWrite` take `data: Seq[Sym[A]]` (a sequence of *symbols*) whereas `SRAMWrite` takes `data: Bits[A]` (one boxed value). Is there a reason banked writes can't use `Seq[Bits[A]]`, or is `Sym[A]` always the post-unroll narrower type?

## Distillation plan

This deep-dive feeds six separate spec entries, one per node category:

- **[[10 - Controllers]]** covers `Control[R]`/`Pipeline[R]`/`Loop[R]`/`UnrolledLoop[R]` hierarchy; `AccelScope`, `UnitPipe`, `ParallelPipe`, `OpForeach`, `OpReduce`, `OpMemReduce`, `StateMachine`, `UnrolledForeach`, `UnrolledReduce`, `Switch`, `SwitchCase`, `SwitchScheduler`. Focuses on signatures, body-list protocol, effect classification, and metadata connections (rawSchedule/rawLevel/rawChildren/rawParent/blk).
- **[[20 - Memories]]** covers the `MemAlloc[A,C]` taxonomy, `RegAlloc`/`Reg*New`, `SRAMNew`, `FIFONew`, `LIFONew`, `RegFileNew`, `LUTNew`/`FileLUTNew`, `LineBufferNew`, `MergeBufferNew`, `DRAM*New`, `LockDRAM*New`/`LockSRAMNew`, `StreamInNew`/`StreamOutNew`, `FrameNew`/`FrameHostNew`, `LockNew`/`LockOnKeys`, plus `MemAlias`/`MemDenseAlias`/`MemSparseAlias`. Documents the `Mem`/`LocalMem`/`RemoteMem`/`TensorMem` taxonomy and per-kind dimensionality and effect conventions.
- **[[30 - Memory Accesses]]** covers the pre-unroll (`Reader`/`Writer`/`Dequeuer`/`Enqueuer`/`StatusReader`/`Resetter`/`VectorReader`/`VectorDequeuer`/`VectorWriter`/`VectorEnqueuer`) and post-unroll (`UnrolledAccessor`/`BankedReader`/`BankedWriter`/`BankedDequeue`/`BankedEnqueue`/`Accumulator`) hierarchies; per-memory concrete accessors; `SetReg`/`GetReg`; `DenseTransfer`/`SparseTransfer`/`FrameTransmit`; `MemDenseAlias`/`MemSparseAlias`.
- **[[40 - Counters and Iterators]]** covers `CounterNew`, `CounterChainNew`, `ForeverNew`, `IndexCounterInfo`, `LaneStatic`, and the iter ↔ counter metadata binding.
- **[[50 - Primitives]]** covers Spatial-specific primitives over argon.node: `Mux`, `OneHotMux`, `PriorityMux`, `DelayLine`, `RetimeGate`, `ShuffleCompress`/`ShuffleCompressVec`, `RegAccumOp`/`RegAccumFMA`/`RegAccumLambda`, `Transient`, and the rewrite rules.
- **[[60 - Streams and Blackboxes]]** covers `StreamInRead`/`StreamInBankedRead`/`StreamOutWrite`/`StreamOutBankedWrite`, `SimpleStreamStruct`/`FieldDeq`/`FieldEnq`, `FunctionBlackbox`/`EarlyBlackbox`/`PrimitiveBlackboxUse`/`CtrlBlackboxUse`/`BlackboxImpl`, `VerilogBlackbox`/`VerilogCtrlBlackbox`, `SpatialBlackboxImpl`/`SpatialBlackboxUse`/`SpatialCtrlBlackboxImpl`/`SpatialCtrlBlackboxUse`, `GEMMBox`, `FetchBlackboxParam`.

Array and FileIO nodes (host-side ops) are documented elsewhere (under `80 - Host Ops`); they're out of scope for these six Spatial-IR entries.
