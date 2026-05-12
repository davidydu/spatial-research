---
type: coverage
subsystem: Spatial IR (nodes + metadata)
paths:
  - "src/spatial/node/"
  - "src/spatial/metadata/"
  - "src/spatial/tags/"
file_count: 79
date: 2026-04-21
verified:
  - 2026-04-21
---

## 1. Purpose

This subsystem defines the Spatial intermediate representation (IR) that sits between the user-facing DSL and all downstream analyses/transforms/codegens. Two pieces: (a) IR *node* classes under `spatial/node/` — typed, staged case classes annotated with `@op` that represent every hardware-relevant operation (control, memory alloc, accesses, DRAM transfers, fringe DMA nodes, blackboxes, streaming, shuffles, delay lines, arrays, file I/O); and (b) *metadata* classes under `spatial/metadata/` — serializable `Data[_]` case classes attached to symbols to record analysis results, user directives, and schedule/banking/buffer decisions. Nodes extend Argon's `Op[_]`, `Primitive[_]`, `Alloc[_]`, and `EnPrimitive[_]` base traits (`spatial/node/HierarchyControl.scala:47-84`, `spatial/node/HierarchyAccess.scala:9-156`). Metadata piggybacks on Argon's metadata facility and is grouped into sub-packages mirroring analysis concerns. In the pipeline: the front end stages user code into these nodes; analysis passes (bounds, control, access, memory/banking, retiming, modeling) attach metadata; transforms (unrolling, lowering, pipelining) rewrite nodes and migrate or discard metadata according to each field's `Transfer` policy; codegens read both to emit hardware. The `spatial/tags/` directory contributes only the `@streamstruct` macro annotation used by DSL types (`spatial/tags/StreamStructs.scala:12-109`).

## 2. File inventory

### `src/spatial/node/` — 33 files

| path | one-line purpose |
|------|------------------|
| `node/HierarchyControl.scala` | Abstract bases `Control`, `EnControl`, `Pipeline`, `Loop`, `UnrolledLoop`, plus `ControlBody`/`PseudoStage`/`OuterStage`/`InnerStage` sum type (`spatial/node/HierarchyControl.scala:17-85`) |
| `node/HierarchyMemory.scala` | `MemAlloc`, `MemAlias`, `MemDenseAlias`, `MemSparseAlias`, and dimension-query transients (`MemStart`, `MemStep`, `MemEnd`, `MemPar`, `MemLen`, `MemOrigin`, `MemDim`, `MemRank`) (`spatial/node/HierarchyMemory.scala:9-120`) |
| `node/HierarchyAccess.scala` | Abstract `Access`/`Read`/`Write`, `Accessor`, `Reader`, `Writer`, `Dequeuer`, `Enqueuer`, `StatusReader`, `Resetter`, plus vector variants (`spatial/node/HierarchyAccess.scala:9-156`) |
| `node/HierarchyUnrolled.scala` | Post-unroll access bases: `UnrolledAccessor`, `BankedReader`, `BankedWriter`, `VectorReader`, `VectorWriter`, `BankedEnqueue`/`BankedDequeue`, `Accumulator` (`spatial/node/HierarchyUnrolled.scala:7-154`) |
| `node/Control.scala` | `CounterNew`, `CounterChainNew`, `AccelScope`, `UnitPipe`, `ParallelPipe`, `OpForeach`, `OpReduce`, `OpMemReduce`, `StateMachine`, `UnrolledForeach`, `UnrolledReduce` (`spatial/node/Control.scala:9-143`) |
| `node/Switch.scala` | `Switch`, `SwitchCase`, custom `SwitchScheduler` (`spatial/node/Switch.scala:11-70`) |
| `node/Reg.scala` | `RegNew`, `FIFORegNew`, `ArgInNew`, `ArgOutNew`, `HostIONew`, `RegWrite`/`Read`, `FIFORegEnq`/`Deq`, `RegReset`, `GetReg`/`SetReg` (`spatial/node/Reg.scala:7-61`) |
| `node/SRAM.scala` | `SRAMNew`, `SRAMRead`, `SRAMWrite`, `SRAMBankedRead`, `SRAMBankedWrite` (`spatial/node/SRAM.scala:10-70`) |
| `node/RegFile.scala` | `RegFileNew`, scalar/vector reads+writes, shift-in variants per axis, reset (`spatial/node/RegFile.scala:10-131`) |
| `node/FIFO.scala` | `FIFONew` (with `resize`), enq/deq/peek, status readers, vector + banked variants, priority-deq variants (`spatial/node/FIFO.scala:7-71`) |
| `node/LIFO.scala` | `LIFONew`, push/pop/peek, status readers, banked variants (`spatial/node/LIFO.scala:7-34`) |
| `node/LUT.scala` | `LUTNew` (inline elems), `FileLUTNew` (from path), reads and banked reads (`spatial/node/LUT.scala:10-49`) |
| `node/LineBuffer.scala` | `LineBufferNew` plus enq/read and banked variants (`spatial/node/LineBuffer.scala:7-30`) |
| `node/MergeBuffer.scala` | `MergeBufferNew` with ways/par, enq/bound/init/deq, banked variants (`spatial/node/MergeBuffer.scala:8-28`) |
| `node/DRAM.scala` | `DRAMHostNew`, `DRAMAccelNew`, `DRAMAddress`, alloc/dealloc/is-alloc, `SetMem`/`GetMem`, lock DRAM transfer getters (`spatial/node/DRAM.scala:9-45`) |
| `node/LockMem.scala` | `LockDRAM*`, `LockSRAM*` read/write + banked + keyed variants, `LockNew`, `LockOnKeys` (`spatial/node/LockMem.scala:8-146`) |
| `node/StreamIn.scala` | `StreamInNew` on a `Bus`, scalar read, banked read (`spatial/node/StreamIn.scala:7-20`) |
| `node/StreamOut.scala` | `StreamOutNew`, write, banked write (`spatial/node/StreamOut.scala:7-27`) |
| `node/StreamStruct.scala` | `SimpleStreamStruct`, `FieldDeq`, `FieldEnq` (`spatial/node/StreamStruct.scala:8-22`) |
| `node/Accumulator.scala` | `Accum` enum (Add/Mul/Min/Max/FMA/Unk), `AccumMarker` types, `RegAccumFMA`/`Op`/`Lambda` (`spatial/node/Accumulator.scala:9-57`) |
| `node/Fringe.scala` | `FringeDenseLoad`/`Store`, `FringeSparseLoad`/`Store`, plus `Fringe` staging helpers (`spatial/node/Fringe.scala:7-66`) |
| `node/DenseTransfer.scala` | `DenseTransfer` EarlyBlackbox and lowering that builds DRAM command/data streams (`spatial/node/DenseTransfer.scala:34-63`, full lowering spans file) |
| `node/SparseTransfer.scala` | `SparseTransfer` EarlyBlackbox for gather/scatter and lowering (`spatial/node/SparseTransfer.scala:27-44`) |
| `node/Frame.scala` | `FrameNew`, `FrameHostNew`, address/alloc/dealloc, `SetFrame`/`GetFrame` (`spatial/node/Frame.scala:9-35`) |
| `node/FrameTransmit.scala` | `FrameTransmit` EarlyBlackbox for AXI-Stream frame I/O (`spatial/node/FrameTransmit.scala:26-43`) |
| `node/Blackbox.scala` | `FunctionBlackbox`, `EarlyBlackbox`, `GEMMBox`, primitive/ctrl Verilog/Spatial blackboxes, `BlackboxImpl`, `FetchBlackboxParam` (`spatial/node/Blackbox.scala:8-62`) |
| `node/Transient.scala` | `Transient[R]` base + `unapply` (marks primitives that should be inlined/removed) (`spatial/node/Transient.scala:10-19`) |
| `node/DelayLine.scala` | `DelayLine` (sized register shift) and `RetimeGate` (simple effect barrier) (`spatial/node/DelayLine.scala:8-14`) |
| `node/LaneStatic.scala` | `LaneStatic` — transient per-lane constant for unroller (`spatial/node/LaneStatic.scala:7-15`) |
| `node/Shuffle.scala` | `ShuffleCompress` / `ShuffleCompressVec` primitives over `Tup2[A,Bit]` (`spatial/node/Shuffle.scala:8-26`) |
| `node/Mux.scala` | `Mux`, `OneHotMux`, `PriorityMux` with literal-folding rewrites (`spatial/node/Mux.scala:9-57`) |
| `node/Array.scala` | Host-side array ops: `ArrayNew`, `ArrayMap`, `ArrayReduce`, `ArrayZip`, `ArrayFold`, `ArrayFilter`, `ArrayFlatMap`, `ArrayMkString`, `CharArrayToText`, `InputArguments` (`spatial/node/Array.scala:8-123`) |
| `node/FileIO.scala` | CSV and binary open/close/read/write, `NumpyArray`/`Matrix`, `LoadDRAMWithASCIIText` (`spatial/node/FileIO.scala:7-59`) |

### `src/spatial/metadata/` — 45 files (grouped by sub-package)

| group | files | purpose |
|-------|-------|---------|
| *root* | `SpatialMetadata.scala`, `types.scala`, `CLIArgs.scala`, `PendingUses.scala` | Marker trait, type/sym helpers (`isIdx`/`isBits`/`toInt`), CLI arg map, ephemeral-node pending-use tracker (`spatial/metadata/types.scala:1-44`, `spatial/metadata/CLIArgs.scala:17-47`, `spatial/metadata/PendingUses.scala:17-24`) |
| **access** | `AccessData.scala`, `AccessPatterns.scala`, `AffineData.scala`, `package.scala` | `UnusedAccess`, `Users`/`User`, `ReadUses`, `PriorityDeqGroup`, `DoesNotConflictWith`, `DependencyEdges`/`TimeStamp` plus affine IR (`Prod`/`Sum`/`Modulus`/`AffineComponent`/`AffineProduct`/`AddressPattern`/`AccessPattern`/`AccessMatrix`/`AffineMatrices`/`Domain`) and op helpers (`isParEnq`/`isStreamStageEnabler`/`accessIterators`/`reachingWrites`/`flatIndex`) |
| **control** | Many files | `CtrlSchedule` (`Sequenced`/`Pipelined`/`Streaming`/`ForkJoin`/`Fork`/`PrimitiveBox`), `CtrlLevel`, `CtrlLooping`, `Ctrl`/`Scope`/`Blk` hierarchy ADTs, `ControlLevel`, `ControlSchedule`, `UserScheduleDirective`, `Children`, `ParentCtrl`, `ScopeCtrl`, `DefiningBlk`, `IndexCounter`, `IterInfo`, `BodyLatency`, `InitiationInterval`/`UserII`/`CompilerII`, `WrittenDRAMs`/`ReadDRAMs`/`WrittenMems`/`ReadMems`/`TransientReadMems`, `ShouldNotBind`, `HaltIfStarved`, `LoweredTransfer`/`LoweredTransferSize`, `UnrollAsPOM`/`MOP`, `UnrollBy`, `ProgramOrder`, `ConvertToStreamed`; stream metadata; `ListenStreams`/`PushStreams`/`AlignedTransfer`/`LoadMemCtrl`/`ArgMap`/`Fringe`; large `package.scala` with `ControlOpOps` and `CtrlHierarchyOps` predicates |
| **memory** | Many files | `Readers`/`Writers`/`Resetters`, `OriginalSym`, `Breaker`, `UnusedMemory`, `DephasedAccess`, `HotSwapPairings`, `InterfaceStream`, `ExplicitName`, `StreamBufferAmount`/`Index`, `FifoInits`, `FIFOType`; banking types (`Banking`/`UnspecifiedBanking`/`ModBanking`, `Port`, `Instance`, `Memory`, `Duplicates`, `Padding`, `Dispatch`, `GroupId`, `Ports`, banking-search enums `BankingView`/`Flat`/`Hierarchical`/`NStrictness`/`AlphaStrictness`, `RegroupDims`, `BankingOptions`/`SearchPriority`, `ExplicitBanking`/`BankingScheme`, `FullyBankDims`, `ForceExplicitBanking`, user-directive flags); accumulator types (`AccumType` = `Fold`/`Buff`/`Reduce`/`None`/`Unknown`, `AccumulatorType`, `ReduceFunction` + `ReduceType`, `FMAReduce`, `IterDiff`, `SegmentMapping`, `InnerAccum`, `InnerReduceOp`); globals `LocalMemories`, `RemoteMemories`; synchronization `Barrier`/`Wait`; `BroadcastAddress` |
| **retiming** | `RetimingData.scala`, `ValueDelay.scala`, `package.scala` | `Cycle`/`WARCycle`/`AAACycle` reduction cycles, `FullDelay`, `UserInjectedDelay`, `ForcedLatency`; `ValueDelay` lazy delay-line holder; `RetimingOps` (`isInCycle`/`fullDelay`/`trace` through `DelayLine`) |
| **modeling** | `SavedArea.scala`, `SavedLatency.scala`, `package.scala` | Cached `Area` and `latency` on a symbol |
| **params** | `DSEData.scala`, `ParamDomain.scala`, `package.scala` | `IgnoreParams`, `TileSizes`, `ParParams`, `PipelineParams`, `TopCtrl`, `MemoryContention`, `Restrictions` + `Restrict` ADT, priors, `Domain[T]`, `SpaceType`; `RangeParamDomain`, `ExplicitParamDomain`, `IntParamValue`, `SchedParamValue`, `ParamPrior`; `ParamDomainOps` with `intValue`/`schedValue`/`prior` getters-setters |
| **blackbox** | `BlackboxData.scala`, `package.scala` | `BlackboxConfig`, `BlackboxInfo`, `BlackboxUserNodes`; ops `isCtrlBlackbox`/`isBlackboxImpl`/`isBlackboxUse`/`isSpatialPrimitiveBlackbox` |
| **bounds** | `BoundData.scala`, `package.scala` | `Bound`/`Final`/`Expect`/`UpperBound`, `SymbolBound`, `Global`, `FixedBits`, matchers `Final`/`Expect`/`Upper`/`Bounded`, `Count`, `VecConst` |
| **debug** | `DebugData.scala`, `package.scala` | `ShouldDumpFinal`, `NoWarnWriteRead`, `TreeAnnotations` |
| **math** | `MathData.scala`, `package.scala` | `Modulus`, `Residual` (ResidualGenerator for banking), `InCycle`, `SrcType` |
| **rewrites** | `CanFuseFMA.scala`, `package.scala` | `CanFuseFMA` flag + single op |
| **transform** | `TransformData.scala`, `package.scala` | `StreamPrimitive`, `FreezeMem`, stream-primitive ancestor walking |

### `src/spatial/tags/` — 1 file

| path | one-line purpose |
|------|------------------|
| `tags/StreamStructs.scala` | `@streamstruct` macro: generates `StreamStruct[T]` class/object with `Bits`/`Arith` typeclasses and `copy` method for stream-struct types (`spatial/tags/StreamStructs.scala:12-109`) |

## 3. Key types / traits / objects

- **`Control[R]`** (`spatial/node/HierarchyControl.scala:47-59`): root of all controllers. Contract: `iters`, `cchains`, `bodies: Seq[ControlBody]`. Overrides Argon's `inputs` to exclude `iters` and adds `iters` to `binds`. Consumed by every control-analysis pass and every codegen.
- **`ControlBody` / `PseudoStage` / `OuterStage` / `InnerStage`** (`HierarchyControl.scala:17-44`): describes a stage. Distinguishes "pseudo" stages (no hardware stage) from real outer/inner stages.
- **`MemAlloc[A,C]`** (`HierarchyMemory.scala:9-26`): abstract base for every on-chip/off-chip memory allocation. Subclassed by `SRAMNew`, `RegNew`, `FIFONew`, `LIFONew`, `RegFileNew`, `LineBufferNew`, `MergeBufferNew`, `LUTNew`, `FileLUTNew`, `DRAMNew`, `LockDRAMHostNew`, `LockSRAMNew`, `FrameNew`, `StreamInNew`, `StreamOutNew`, `LockNew`.
- **`Access` / `Read` / `Write`** (`HierarchyAccess.scala:9-15`): simple case classes capturing `mem`, `addr`, `ens`, (and `data` for writes).
- **`Accessor[A,R]` and specializations `Reader`, `Writer`, `Dequeuer`, `Enqueuer`, `StatusReader`, `Resetter`** (`HierarchyAccess.scala:45-156`). Extractors `Reader.unapply`, `Writer.unapply`, `Accessor.unapply`.
- **`UnrolledAccessor[A,R]` with subs `BankedReader`/`Writer`, `VectorReader`/`Writer`, `BankedEnqueue`/`Dequeue`, `Accumulator`** (`HierarchyUnrolled.scala:22-154`): post-unroll banking-aware access nodes with `mem`, `bank: Seq[Seq[Idx]]`, `ofs: Seq[Idx]`, `enss: Seq[Set[Bit]]`.
- **`FringeNode[A,R]`** (`HierarchyControl.scala:7-15`): base for DMA/fringe nodes.
- **`EarlyBlackbox[R]`** (`Blackbox.scala:11-16`): blackboxes that must be lowered early. Used by `DenseTransfer`, `SparseTransfer`, `FrameTransmit`.
- **`Ctrl`/`Scope`/`Blk` hierarchy ADTs**: `Ctrl.Node(sym,stg)`, `Ctrl.Host`, `Ctrl.SpatialBlackbox(sym)`; `Scope.Node(sym,stg,blk)`. `master` collapses a stage-specific controller to its whole-controller identity.
- **`CtrlSchedule`** enum with `Sequenced`, `Pipelined`, `Streaming`, `ForkJoin`, `Fork`, `PrimitiveBox`.
- **`AccumType`** ADT: lattice of accumulator flavor (`Fold`/`Buff`/`Reduce`/`None`/`Unknown`) with join `|`, meet `&`, partial order `>`.
- **`Banking` (abstract) → `UnspecifiedBanking`, `ModBanking`**: encodes an `(N,B,alpha,P,axes)` banking scheme; `bankSelect(addr)` computes bank index.
- **`Instance` and `Memory`**: banking/depth/padding/acc-type decision for one physical duplicate; `Duplicates(Seq[Memory])` is the actual metadata attached.
- **`AccessMatrix`**: pairs an access sym with a `SparseMatrix[Idx]` representing its affine address; supports `overlapsAddress`, `isSuperset`, `intersects`, `isDirectlyBanked`, `bankMuxWidth`, `arithmeticNodes`.
- **`AddressPattern`/`AffineProduct`/`Prod`/`Sum`/`Modulus`**: symbolic affine algebra with static-folding multipliers.
- **`Cycle`/`WARCycle`/`AAACycle`**: metadata summarizing detected reduction and AAA cycles used by retiming.
- **`Bound`/`Final`/`Expect`/`UpperBound`**: symbol-level integer bounds with meet; extractor objects let callers pattern-match static values.
- **`BankingOptions`, `BankingView`, `NStrictness`, `AlphaStrictness`, `RegroupDims`**: banking-search configuration consumed by the memory analysis DSE loop.
- **`Data[_]` envelope** (inherited from Argon): every metadata case class extends it with a `Transfer` policy (`Mirror`, `Remove`, `SetBy.*`, `GlobalData.*`).

## 4. Entry points

- **Node constructors (`@op case class ...`)**: staged via `stage(...)` from `spatial/lang/` API methods; they *are* the staging boundary.
- **Extractor objects**: `Control.unapply`, `MemAlloc.unapply`, `Accessor.unapply`, `Reader.unapply`, `Writer.unapply`, `Dequeuer.unapply`, `Enqueuer.unapply`, `UnrolledAccessor.unapply`, `BankedReader.unapply`, `FringeNode.unapply`, `Transient.unapply`.
- **Metadata ops (package objects)**: `sym.parent`/`scope`/`blk`/`schedule`/`level`/`children`/`ancestors`/`isCtrl(...)` (control), `sym.accumType`/`reduceType`/`duplicates`/`instance`/`padding`/`explicitBanking`/`banks`/`port`/`dispatch` (memory), `sym.accessPattern`/`affineMatrices`/`domain`/`users`/`readUses`/`isUnusedAccess` (access), `sym.bound`/`isGlobal`/`isFixedBits` (bounds), `sym.fullDelay`/`reduceCycle`/`isInCycle` (retiming), `sym.area`/`latency` (modeling), `sym.residual`/`modulus`/`srcType` (math), `sym.isStreamPrimitive`/`freezeMem` (transform), `sym.bboxInfo`/`isBlackboxImpl` (blackbox).
- **Globals**: `AccelScopes.all`, `LocalMemories.all`, `RemoteMemories.all`, `CLIArgs`, `PendingUses`, `StreamLoads`/`TileTransfers`/`StreamEnablers`/`StreamHolders`/`StreamParEnqs`, `IgnoreParams`/`TileSizes`/`ParParams`/`PipelineParams`/`TopCtrl`/`Restrictions`.
- **`SwitchScheduler`** (`spatial/node/Switch.scala:11-30`): custom `argon.schedule.Scheduler` that motions non-`SwitchCase` ops out of a Switch body.
- **`Fringe.denseLoad`/`denseStore`/`sparseLoad`/`sparseStore`**: staging wrappers used by `DenseTransfer`/`SparseTransfer` lowering.
- **`Switch.op_case`/`op_switch`**: staging entries for hardware case matching.
- **`@streamstruct` macro**: injected at user annotation sites; produces `StreamStruct[T]` class/object with Bits/Arith typeclasses.

## 5. Dependencies

**Upstream:**
- `argon._`, `argon.node._`, `argon.schedule.*` — base IR, `Op`/`Alloc`/`Primitive`/`EnPrimitive`/`DSLOp`/`StructAlloc`, effects, `Block`/`Lambda1/2`, `Data[_]`, metadata store, `Scheduler`.
- `argon.tags.{struct,Bits,Arith}` and `forge.tags.{op,rig,stateful,data,api,virtualize}` — staging macros and typeclass generation.
- `spatial.lang._` — user-facing types.
- `poly.{SparseMatrix, SparseVector, ConstraintMatrix, ISL}` — integer set library used by `AccessMatrix`/`Domain`.
- `emul.FixedPoint`, `emul.ResidualGenerator` — emulator types used by bounds and residuals.
- `models._` — area models (`SavedArea`).
- `spatial.targets.MemoryResource` — used by `Memory.resourceType`.
- `spatial.util.{memops, modeling, spatialConfig, VecStructType, IntLike}` — DRAM transfer helpers, target info, banking heuristics.
- `spatial.issues.{AmbiguousMetaPipes, PotentialBufferHazard}`.

**Downstream:**
- All of `spatial/transform/*` — unrolling, lowering, pipelining, retiming, memory/banking analysis rely on these nodes and metadata.
- `spatial/analysis/*` — bounds, access-pattern, control-sanity, modeling passes attach the metadata defined here.
- `spatial/codegen/*` — Chisel/PIR/Scala/C++/Dot/Tree codegens pattern-match on node types and read all the metadata.
- `spatial/dse/*` — DSE reads `params/*` metadata.
- `spatial/lang/*` — DSL API methods construct these nodes directly.
- `spatial/traversal/*` — hierarchy traversals consume `Ctrl`/`Scope`/`Blk` and the `CtrlHierarchyOps` predicates.

## 6. Key algorithms

- **`AccessMatrix.bankMuxWidth` and `arithmeticNodes`**: given `(N,B,alpha)` scheme, compute per-access conflict count and required arithmetic hardware cost (`AffineData.scala:74-125`).
- **`AddressPattern.getSparseVector` / `toSparseVector`**: convert symbolic affine sum to `SparseVector[Idx]` iff multipliers are constant (`AccessPatterns.scala:222-254`).
- **`reachingWrites` / `precedingWrites` / `isKilled`**: dataflow over `AccessMatrix` sets to find writes visible to a read and eliminate killed writes (`access/package.scala:396-452`).
- **`accessIterators`**: chooses the correct master/sub-controller scope when access and memory live in different sub-blocks of MemReduce (`access/package.scala:355-387`).
- **`dephasingIters` / `divergedIters`**: compute per-iterator lockstep-dephasing offsets for uids (`access/package.scala:324-349`).
- **`Memory.bankOffset` / `bankSelects`**: flat and hierarchical bank-address arithmetic including intrablock offset (`BankingData.scala:202-255`).
- **`ModBanking.bankSelect`**: `(alpha·addr / B) mod N` banking function (`BankingData.scala:62-65`).
- **`NStrictness.expand` / `AlphaStrictness.expand` / `selectAs`**: banking-search enumerations producing candidate `N`s and coprime `alpha` vectors (`BankingData.scala:533-634`).
- **`SwitchScheduler.apply`**: partitions a scope into `SwitchCase` (kept) and everything else (motioned out) (`Switch.scala:15-29`).
- **`DenseTransfer.transfer` / `SparseTransfer.transfer` / `FrameTransmit.transfer`**: lower an early-blackbox transfer to a `Stream { ... }` block over `Fringe*` nodes and bus packing.
- **`MathOps.residual`**: compute `ResidualGenerator(A=par·step, B=lane starts, C=0)` from a symbol's counter when an explicit `Residual` isn't stored (`math/package.scala:27-40`).
- **`CtrlHierarchyOps.schedule`**: resolves the effective schedule for a controller based on its `looping` × `level` × raw user schedule, collapsing unreachable combinations (`control/package.scala:193-219`).
- **`Mux.rewrite` / `OneHotMux.rewrite` / `PriorityMux.rewrite`**: literal-folding rewrites for select nodes (`Mux.scala:11-56`).
- **`accessPattern.bankMuxWidth`** with `span` over `ResidualGenerator`: uses emul residual math to decide whether an access is directly banked.

## 7. Invariants / IR state read or written

- Every `Control[_]` node's `binds` includes its `iters`; `inputs` excludes them. Unroller must preserve this.
- Every `Writer[_]`/`Enqueuer[_]`/`Accumulator[_]` declares `effects = Effects.Writes(mem)`; analyses assume all mutations are so-declared.
- `RegRead`, `FIFORegDeq` are marked `Unique` and `isTransient = true` — multiple syntactic reads represent one hardware read wire.
- `AccelScope` adds `Effects.Simple` to prevent removal; comment flags a TODO (`Control.scala:29-30`).
- `MemAlloc.effects = Effects.Mutable` when `mutable=true` (default) and respects a non-mutable flag (used for `LUTNew`).
- `CtrlSchedule.Streaming`, `ForkJoin`, `Fork`, `PrimitiveBox` are preserved across looping×level transitions; `Pipelined` collapses to `Sequenced` when level is `Inner` and `looping` is `Single`.
- Metadata transfer policies: `Transfer.Mirror` items survive mirroring; `Transfer.Remove` items are dropped; `SetBy.Flow.*`, `SetBy.Analysis.*`, `SetBy.User` items are rewritten only by the corresponding pass class.
- `AccumType` lattice: `Fold > Reduce > Buff > None > Unknown`; join `|` and meet `&` must be associative/commutative.
- `Memory.resourceType` is mutable (`var`) and optional; analyses must call `.resource` which defaults via `spatialConfig.target.defaultResource`.
- `UnrolledAccessor.ens` is a `var` assigned `Set.empty`; `enss` is the authoritative per-lane enables.
- `Bound.isFinal` is a mutable flag set by `makeFinal`.
- `Banking.numChecks` and `solutionVolume` are diagnostic-only counters and must not affect scheme equality.
- `Port` fields `bufferPort: Option[Int]` = `None` means time-multiplexed outside a pipeline buffer; codegen relies on this encoding.
- `DependencyEdges` carries pseudo-edges (`isPseudoEdge`) that must be excluded from certain dataflow queries.
- Many hidden invariants marked by TODO comments throughout.

## 8. Notable complexities or surprises

- **Stage id = -1 convention**: `Ctrl.Node(sym,-1)` is the "master" form; sub-stage ids reference individual bodies of `OpMemReduce` etc.
- **`OpMemReduce` body layout**: has `PseudoStage(itersMap -> map)` plus an `InnerStage` with four sub-blocks using mixed iterator sequences. Downstream code that iterates `ctrl.bodies` must know about this asymmetry.
- **`Switch` uses a custom scheduler**, not the standard Argon one — any pass that clones/rebuilds scopes inside a switch must preserve `BlockOptions(sched = Some(SwitchScheduler))`.
- **`MemSparseAlias` / `MemDenseAlias` carry `cond: Seq[Bit]` and multiple `mem`/`addr` slots** — they represent a *union* of aliases; most transforms only handle the singleton form.
- **`RegFile` shifts have an `axis` parameter**; unroller/codegen must handle all combinations of scalar/vector/banked shift-in on arbitrary axis.
- **`LockDRAM` / `LockSRAM` accesses carry `lock: Option[LockWithKeys[I32]]`** — serialization ordering is partially encoded in metadata, not structurally. Hardcoded hacks returning empty banking and dispatch=`{0}` for LockDRAM.
- **`Accumulator.data = Nil`** — there's no IR symbol for the data being written; this is intentional but surprising and likely affects DCE.
- **`Prod.canBeDividedBy(p)` treats shared symbols as cancelable** — silent algebraic correctness depends on `xs.diff(xs)` semantics.
- **`AccumType.None.|(Unknown) = None`** but `Unknown.|(None) = None` — asymmetric lattice operations.
- **`NBestGuess.factorize` and `AlphaBestGuess` enumerate `O(N²)`-sized candidate lists** — banking-search performance bottleneck.
- **`ExplicitBanking` has a commented-out earlier single-tuple representation**; current list form allows one scheme per duplicate.
- **`ValueDelay.value()` lazily stages a delay line via a closure** — a side-effectful memoization pattern that must be carefully ordered with transformer state.
- **`FrameTransmit.transfer` does byte-alignment check (`A.nbits % 8 != 0`) and may warn about wraparound**; non-`AxiStream64Bus` outputs silently fall back to `(0,0)` tid/tdest.
- **`@streamstruct` macro** rejects fields that are vars, any methods, or type parameters; errors are aborts at macro expansion.
- **Metadata sub-package `package.scala` files implement most operations** — many ops span 400+ lines and mix getters, setters, and computation. These files are the main API surface for the rest of the compiler.

## 9. Open questions

- How are `iterSynchronizationInfo`, `willUnrollAsPOM`, and `parent.s.get` (called in `dephasingIters` / `getDephasedUID`) defined?
- The `UserSchedule* / CompilerII / UserII / InitiationInterval` triplet overlaps — what is the precedence and who resolves conflicts?
- `Instance.cost: Double` is a free-form number; which analyses produce it and how is it combined across duplicates?
- `GroupId` is mutable per-uid via `addGroupId` — is it monotonic? Does banking analysis depend on order of insertion?
- `HotSwapPairings` comments imply an intricate transform; who reads this and which transform writes it?
- `ConvertToStreamed` is described only by its case class name; where is it consumed?
- `FrameHostNew(dims, zero, stream)` carries a `stream: Sym[_]` — how is that linked back to `InterfaceStream`?
- `DependencyEdges` is only ever attached/mirrored but no clear consumer inside this subsystem — which analysis reads it?
- `BroadcastAddress` has a single boolean; when is it set and consumed?
- `NoWarnWriteRead` flag's downstream consumer is not obvious.
- `FieldEnq` has a TODO comment "may not actually be used anywhere"; confirm whether it is safe to remove.
- Is it intentional that `FrameTransmit` does not have a dedicated "frame analysis" metadata set, while `DenseTransfer` relies on several access/bounds/control/memory metadata imports?

## 10. Suggested spec sections

- **`10 - Spec/IR/Nodes/Control.md`** — from `spatial/node/Control.scala` + `HierarchyControl.scala` + `Switch.scala` + `HierarchyUnrolled.scala`.
- **`10 - Spec/IR/Nodes/Memory.md`** — from `HierarchyMemory.scala`, `SRAM.scala`, `Reg.scala`, `RegFile.scala`, `FIFO.scala`, `LIFO.scala`, `LUT.scala`, `LineBuffer.scala`, `MergeBuffer.scala`, `LockMem.scala`, `Accumulator.scala`.
- **`10 - Spec/IR/Nodes/Access.md`** — from `HierarchyAccess.scala`, `HierarchyUnrolled.scala`.
- **`10 - Spec/IR/Nodes/Transfers.md`** — from `DRAM.scala`, `DenseTransfer.scala`, `SparseTransfer.scala`, `Frame.scala`, `FrameTransmit.scala`, `Fringe.scala`, `StreamIn.scala`, `StreamOut.scala`.
- **`10 - Spec/IR/Nodes/Primitives.md`** — from `Mux.scala`, `Shuffle.scala`, `Transient.scala`, `DelayLine.scala`, `LaneStatic.scala`, `Array.scala`, `FileIO.scala`, `StreamStruct.scala`, `Blackbox.scala`.
- **`10 - Spec/IR/Metadata/Access.md`** — from `metadata/access/**`.
- **`10 - Spec/IR/Metadata/Control.md`** — from `metadata/control/**`.
- **`10 - Spec/IR/Metadata/Memory-Banking.md`** — from `metadata/memory/BankingData.scala`, `MemoryData.scala`, `AccumulatorData.scala`, `LocalMemories.scala`, `RemoteMemories.scala`, `Synchronization.scala`, `BroadcastAddress.scala`, `package.scala`.
- **`10 - Spec/IR/Metadata/Retiming-Modeling.md`** — from `metadata/retiming/**` + `metadata/modeling/**`.
- **`10 - Spec/IR/Metadata/Params-DSE.md`** — from `metadata/params/**`.
- **`10 - Spec/IR/Metadata/Misc.md`** — `metadata/bounds/**`, `metadata/blackbox/**`, `metadata/debug/**`, `metadata/math/**`, `metadata/rewrites/**`, `metadata/transform/**`, `metadata/types.scala`, `metadata/CLIArgs.scala`, `metadata/PendingUses.scala`, `metadata/SpatialMetadata.scala`.
- **`10 - Spec/IR/Tags/StreamStructs.md`** — from `tags/StreamStructs.scala` (macro-generated type classes).
