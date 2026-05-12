---
type: coverage
subsystem: Compiler passes
paths:
  - "src/spatial/transform/"
  - "src/spatial/rewrites/"
  - "src/spatial/traversal/"
  - "src/spatial/flows/"
file_count: 78
date: 2026-04-21
verified:
  - 2026-04-21
---

## 1. Purpose

This is the main Spatial compilation pipeline: the sequence of transformers (mutating passes that rewrite the IR) and traversals (read-only analyses that attach metadata) that turn a just-staged Spatial IR block into a codegen-ready IR. It sits between DSL staging (the `lang/` / `node/` frontend) and the backend codegens (`codegen/`). The pass order is baked into `spatial/Spatial.scala:164-253` (the `block ==> pass ==> …` chain in `runPasses`) and is load-bearing: later passes rely on metadata written by earlier passes (access patterns, banking, retiming delays, schedules, II, duplicates, ports). `rewrites/` registers the initial local rewrite rules with Argon; `flows/SpatialFlowRules.scala` registers the metadata flow rules run on every `stage(...)`. `transform/` contains the ~25 whole-IR transformers; `transform/unrolling/` contains the unrolling base + per-controller unrollers composed by `UnrollingTransformer`; `transform/streamify/` contains the experimental MetaPipe-to-Stream flow (mostly gated on `--streamify`); `traversal/` contains the read-only analyses, including the banking analyzer (`banking/`) which is the most algorithmically heavy single pass.

## 2. File inventory

### `flows/`

| path | purpose |
| --- | --- |
| `flows/SpatialFlowRules.scala` | All Argon `@flow` rules registered by `override def flows()` in `Spatial.scala:57`. Runs on each staged symbol; sets control level, schedule, hierarchy (`rawChildren`, `rawLevel`, `rawSchedule`, `blk`), accumulator type, global-ness, reader/writer sets, hotswap and black-box uses. |

### `rewrites/`

| path | purpose |
| --- | --- |
| `rewrites/SpatialRewriteRules.scala` | Composition class registered via `Spatial.scala:58`; mixes in all trait-based rule sets. |
| `rewrites/AliasRewrites.scala` | Simplifies `MemDenseAlias`/`MemSparseAlias` projections. |
| `rewrites/CounterIterRewriteRule.scala` | Rewrites `iter % par` patterns on pre-unroll iterators to `LaneStatic` nodes (global rewrite rule `UnrollLane`). |
| `rewrites/LUTConstReadRewriteRules.scala` | Converts `LUTBankedRead` on an all-constant LUT with constant address into a `VecAlloc` of the literal values. |
| `rewrites/VecConstRewriteRules.scala` | `VecConst` constant propagation / broadcasting for binary ops and `FixSRA`. |

### `traversal/`

| path | purpose |
| --- | --- |
| `traversal/AccelTraversal.scala` | Mixin base: `inAccel`/`inBox`/`inHw` markers; `BlkTraversal` sub-trait adds current-`blk` tracking. |
| `traversal/AbstractSanityChecks.scala` | Shared helpers for sanity-check passes. |
| `traversal/UserSanityChecks.scala` | User-facing error reporting (reading ArgOut inside Accel, bus width mismatch, etc.). |
| `traversal/CompilerSanityChecks.scala` | Internal invariants — no undefined inputs, no duplicate staging, no unexpected primitive-in-outer-control after pipe insertion. |
| `traversal/CLINaming.scala` | Traces input-argument array-applys to record `CLIArgs` names. |
| `traversal/UseAnalyzer.scala` | Propagates `Users`, `readUses`, `PendingUses`; detects unused memories. |
| `traversal/AccessAnalyzer.scala` | Recursive affine-pattern extraction — the `Affine` unapply builds `AddressPattern` components for every memory access; feeds banking. |
| `traversal/AccessExpansion.scala` | Helpers shared by analyzer and banking for domain/constraint matrices and access-matrix unrolling. |
| `traversal/AccumAnalyzer.scala` | Detects accumulation cycles and tags `reduceCycle` / `AccumMarker.Reg.Op`/`.FMA` for later specialization by `AccumTransformer`. |
| `traversal/MemoryAnalyzer.scala` | Banking orchestrator — per memory picks a `MemoryConfigurer` variant + a `BankingStrategy` (`ExhaustiveBanking` / `FullyBanked` / `CustomBanked`) and emits an HTML decisions report. |
| `traversal/MemoryAllocator.scala` | Assigns each duplicate memory to a concrete `MemoryResource` (URAM/BRAM/LUT/…) subject to target capacity, using area metrics. |
| `traversal/RetimingAnalyzer.scala` | Computes `fullDelay`, `inCycle`, `bodyLatency` for nodes inside inner controllers and black boxes, guarded by `spatialConfig.enableRetiming`. |
| `traversal/IterationDiffAnalyzer.scala` | Computes loop-carry iteration differences; sets `iterDiff` used to bound II below. |
| `traversal/InitiationAnalyzer.scala` | Computes `II` / `compilerII` / `bodyLatency` on each controller; collapses inner-vs-outer control II differently. |
| `traversal/PerformanceAnalyzer.scala` | Optional runtime-cycle estimator; feeds `RuntimeModelGenerator`. |
| `traversal/BufferRecompute.scala` | Post-unroll recomputation of N-buffer depth from `Ports`; resolves port conflicts created by `MemReduce` unrolling. |
| `traversal/BroadcastCleanup.scala` | Propagates `isBroadcastAddr=false` for nodes feeding accumulators / status readers / banked accesses; final pass after retiming. |
| `traversal/RewriteAnalyzer.scala` | Sets `canFuseAsFMA` on `FixAdd`/`FltAdd` nodes by inspecting mul-consumer topology — must be a Traversal, not a rewrite, because `RewriteTransformer` is mutating. |
| `traversal/CounterIterSynchronization.scala` | After streamify, relinks each `Counter` to its iter's `IndexCounterInfo(ctr, 0 until par)`. |
| `traversal/RerunTraversal.scala` | Small trait: re-entry into a traversal with `isRerun=true`. |
| `traversal/AreaAnalyzer.scala` | Entirely commented out (old area-estimation pass, superseded by `dse/` + `MemoryAllocator`). |
| `traversal/banking/BankingStrategy.scala` | Abstract API: `bankAccesses(mem, rank, reads, writes, directives, depth)` returning banking choices per access group. |
| `traversal/banking/ExhaustiveBanking.scala` | Default banker for SRAM/LineBuffer/StreamIn/StreamOut/FIFO — tries `BankingView × NStrictness × AlphaStrictness × RegroupDims` combinations, caches solutions, enumerates viable `(α, N, B)` tuples. |
| `traversal/banking/FullyBanked.scala` | Simpler strategy for `Reg`/`RegFile`/`LUT`/`FIFOReg` — single `Hierarchical(rank)` view, fully relaxed. |
| `traversal/banking/CustomBanked.scala` | No-op strategy for user/backend-banked memories (`LockSRAM`, `MergeBuffer`). |
| `traversal/banking/MemoryConfigurer.scala` | Per-memory: group accesses by concurrency, drive the strategy, pick best cost, assign `Dispatch`/`Ports`/`Duplicates`. Largest single file in subsystem (818 lines). |
| `traversal/banking/FIFOConfigurer.scala` | FIFO-specialized subclass: no N-buffering, requires non-concurrent read/write groups. |
| `traversal/routing/UniformCostSearch.scala` | Generic UCS used by banking-related searches (not yet widely used). |

### `transform/` — non-unrolling, non-streamify

| path | purpose |
| --- | --- |
| `transform/FriendlyTransformer.scala` | Wraps the outer block — auto-creates `ArgIn`s for bits referenced inside `AccelScope`, dedupes DRAM dimension values, lifts `GetReg`/`SetReg` misuse. First pass in the chain. |
| `transform/TextCleanup.scala` | Optional — drops `DSLOp`s with `canAccel=false` from within Accel (removes print/text helpers). |
| `transform/SwitchTransformer.scala` | Converts nested `IfThenElse` chains inside Accel into a single `Switch` with `SwitchCase`s. |
| `transform/SwitchOptimizer.scala` | Eliminates switches whose selectors are constant, collapses single-case switches to `Mux`/`oneHotMux`, tags hot-swap Reg→Switch pairings via `hotSwapPairings`. |
| `transform/BlackboxLowering.scala` | Runs twice (once with `lowerTransfers=false`, once with `=true`): lowers `FixSLA`/`FixSRA`/`FixSRU` with non-constant shift to loop-based emulations; lowers `DenseTransfer`/`SparseTransfer`/`FrameTransmit` to their canonical `Fringe*` nodes. |
| `transform/MemoryDealiasing.scala` | Converts `MemDenseAlias`/`MemSparseAlias` reads/writes into muxed reads-from-all-branches on the underlying DRAM(s). |
| `transform/LaneStaticTransformer.scala` | Pre-unroll pass that folds `FixMod` / add / sub / mul / sla patterns on an iterator into `LaneStatic` nodes. |
| `transform/PipeInserter.scala` | Insert `UnitPipe`s between primitives and controllers — the core "outer stage" creation pass. |
| `transform/RegReadCSE.scala` | CSE for `RegRead` inside inner controllers. |
| `transform/TransientCleanup.scala` | Combined DCE + transient-node motion. |
| `transform/UnrollingTransformer.scala` | Trivial composition class mixing all `unrolling/*Unrolling` traits. |
| `transform/MemoryCleanupTransformer.scala` | Drops local memories with no readers AND no writers after unrolling. |
| `transform/RewriteTransformer.scala` | Hardware-specific rewrites: pow2-multiplies, Mersenne-based mod/div (Crandall's algorithm), FMA fusion, reg-write-of-mux → enabled `RegWrite`, sqrt/recip fusion, shift combining, `residual` metadata propagation. |
| `transform/FlatteningTransformer.scala` | Flattens inner-pipe switches into `Mux`/`oneHotMux`; inlines outer UnitPipes with a single non-stream, non-blackbox child. |
| `transform/BindingTransformer.scala` | Bundles consecutive non-conflicting sibling controllers into a `ParallelPipe`. |
| `transform/AccumTransformer.scala` | Replaces marked accumulation cycles with `RegAccumOp`/`RegAccumFMA` specializations (II=1 accumulator nodes). |
| `transform/RetimingTransformer.scala` | Inserts `DelayLine` nodes and rewires consumers to them. |
| `transform/AllocMotion.scala` | Inside outer Foreach/UnitPipe, moves memory allocations + their counter dependencies to the top of the block. |
| `transform/FIFOAccessFusion.scala` | Fuses consecutive `FIFOEnq`s (same mem, same ens) into a single `FIFOVecEnq`. |
| `transform/DuplicateRetimeStripper.scala` | Collapses back-to-back `RetimeGate()` nodes. |
| `transform/UnitIterationElimination.scala` | Converts foreaches where all counters are `isUnit && par==1` to UnitPipes. |
| `transform/ForeachToUnitpipeTransformer.scala` | Similar to above but for static single-iteration foreaches. Not in canonical chain. |
| `transform/UnitPipeToForeachTransformer.scala` | Converts UnitPipe to a 1-iteration `OpForeach`. Not in canonical chain. |
| `transform/StreamTransformer.scala` | `--distributeStreamCtr`: distribute a Stream.Foreach's counterchain into each child controller. |
| `transform/StreamConditionSplitTransformer.scala` | Stub — `transform` just calls `super`. Placeholder. |
| `transform/MetadataStripper.scala` | `Stripper[M]` + `MetadataStripper(state, strippers*)`: clears named metadata classes on every symbol. |
| `transform/LoopPerfecter.scala` | Entirely commented-out. |
| `transform/debug/SRAMDumper.scala` | Entirely commented-out. |

### `transform/unrolling/`

| path | purpose |
| --- | --- |
| `transform/unrolling/UnrollingBase.scala` | Abstract transformer plus the `Unroller` trait hierarchy: `UnitUnroller`, `LoopUnroller`, `PartialUnroller`, `FullUnroller`. |
| `transform/unrolling/ForeachUnrolling.scala` | `OpForeach` → `UnrolledForeach` / `UnitPipe` + `ParallelPipe`, MoP vs PoM branching. |
| `transform/unrolling/ReduceUnrolling.scala` | `OpReduce` → `UnrolledReduce`, partial and fully-unrolled variants. |
| `transform/unrolling/MemReduceUnrolling.scala` | `OpMemReduce` — four combinations of fully-unrolled map/reduce counterchains. |
| `transform/unrolling/MemoryUnrolling.scala` | Largest unroller (581 lines). Replicates local memories across lane duplicates. |
| `transform/unrolling/SwitchUnrolling.scala` | Duplicates `Switch` nodes per lane when inside an inner controller. |
| `transform/unrolling/BlackBoxUnrolling.scala` | Empty stub class. |

### `transform/streamify/`

| path | purpose |
| --- | --- |
| `transform/streamify/EarlyUnroller.scala` | A `ForwardTransformer` that pre-unrolls outer loops early. |
| `transform/streamify/DependencyGraphAnalyzer.scala` | Build a graph of `InferredDependencyEdge`s over controllers. |
| `transform/streamify/HierarchicalToStream.scala` | Main streamify transformer (~838 lines): wraps each inner controller in a `genToMain / mainToRelease / genToRelease` FIFO trio. |
| `transform/streamify/FlattenToStream.scala` | Entirely commented-out earlier approach. |
| `transform/streamify/StreamingControlBundle.scala` | Entirely commented-out helper for edge FIFO sizing. |
| `transform/streamify/AccelPipeInserter.scala` | Wraps the entire `AccelScope` block in a single `UnitPipe`. |
| `transform/streamify/FIFOInitializer.scala` | Emits init-controllers for any FIFO whose `fifoInits` metadata is set. |
| `transform/streamify/ForceHierarchical.scala` | Marks every `SRAM` as `hierarchical` for streamify-specific banking. |
| `transform/streamify/TimeMap.scala` | `TimeMap` / `TimeTriplet` value classes. |

## 3. Key types / traits / objects

- **`Spatial.runPasses`** (`Spatial.scala:60-257`) — builds a lazy-val for every transformer and traversal, then chains them with `==>`; the whole pipeline is one big expression.
- **`UnrollingBase.Unroller`** — the per-loop lane-context abstraction. Methods: `map`/`foreach`/`inLane`, `duplicate`, `unify`, `duplicateMem`.
- **`UnrollingBase.LoopUnroller`** / `PartialUnroller` / `FullUnroller` / `UnitUnroller` — Concrete lane-context shapes.
- **`BankingStrategy`** — Abstract API for picking banking schemes; three impls: `ExhaustiveBanking`, `FullyBanked`, `CustomBanked`.
- **`MemoryConfigurer[C[_]]`** — Per-memory orchestrator; derivable subclass `FIFOConfigurer`. Exposes `configure()`, `schemesInfo`, `cost()`, `bank()`, `requireConcurrentPortAccess()`.
- **`AccessExpansion`** — Mixin used by `AccessAnalyzer` and banking to materialize unrolled `AccessMatrix` sets from `AddressPattern`s and `AffineMatrices`.
- **`AccelTraversal` / `BlkTraversal`** — Base traits carrying `inAccel`/`inBBox`/`inHw`, and `inCtrl(sym)`/`advanceBlk()` for block tracking.
- **`SpatialFlowRules`** — Holds all `@flow` callbacks.
- **`SpatialRewriteRules`** — Composition trait; registered via `Spatial.rewrites()`.
- **`Stripper[M]` / `MetadataStripper`** — Generic metadata invalidator used between passes.

## 4. Entry points

From outside the subsystem, the seam is entirely `Spatial.runPasses` at `spatial/Spatial.scala:60`. `initConfig()` / `flows()` / `rewrites()` overrides at `Spatial.scala:56-58` register `SpatialConfig`, `SpatialFlowRules`, and `SpatialRewriteRules`. Each `case class` in this subsystem takes `IR: State` as its constructor. `dse/DSEAnalyzer`, `model/RuntimeModelGenerator`, `codegen/*`, and `report/*` consume the metadata established here.

## 5. Dependencies

**Upstream**
- `argon` — `MutateTransformer`, `ForwardTransformer`, `Traversal`, `Pass`, `RewriteRules`, `FlowRules`, `Codegen` base for `MemoryAnalyzer`. Subst, staging, `@flow`/`@rewrite`/`@rig` macros.
- `poly` — `ISL`, `ConstraintMatrix`, `SparseMatrix`, `SparseVector`, `SparseConstraint` used by the access analyzer, banking, and access expansion.
- `models` — `AreaEstimator` used by `MemoryAllocator`, `MemoryConfigurer`, `MemoryAnalyzer`.
- `spatial.node.*` — IR node definitions.
- `spatial.metadata.*` — every pass reads/writes `metadata.control`, `metadata.access`, `metadata.memory`, `metadata.retiming`, `metadata.bounds`, `metadata.math`, `metadata.rewrites`, `metadata.types`, `metadata.blackbox`, `metadata.transform`.
- `spatial.util.modeling` — `pipeLatencies`, `latencyAndInterval`, `latencyOf`, `computeDelayLines`, `findAccumCycles`, `reachingWritesToReg`.
- `spatial.util.TransformUtils` / `TransformerUtilMixin` — helpers for streamify passes.
- `spatial.issues.UnbankableGroup` — raised by banking on infeasible groups.
- `spatial.util.spatialConfig` — the global feature-flag bag.
- `spatial.targets.HardwareTarget` — consumed by `MemoryAllocator` and `MemoryConfigurer` via `models`.

**Downstream (within `spatial/`)**
- `spatial.codegen.*` — Chisel/Cpp/Rogue/Scala/PIR/Tsth/Tree/Dot/Html codegens all consume the final metadata set produced by this pipeline.
- `spatial.dse.*` — `ParameterAnalyzer`, `DSEAnalyzer` interleave with these passes.
- `spatial.model.RuntimeModelGenerator` — run after `initiationAnalyzer` when `enableRuntimeModel` is set.
- `spatial.report.*` — `MemoryReporter`, `RetimeReporter`, `ResourceReporter`, `ResourceCountReporter` read metadata this subsystem establishes.
- `spatial.executor.scala.ExecutorPass` — optional in-compiler executor invoked after banking analysis.

## 6. Key algorithms

- **Argon flow rules** — `SpatialFlowRules.controlLevel` sets `rawChildren`/`rawLevel`/`rawParent`/`rawScope`/`writtenMems`/`readMems`. `controlSchedule` picks a schedule per controller under a 6-rule priority. `accumulator` sets `accumType=Fold` where a writer feeds a reader of the same memory. `globals` propagates `isGlobal`/`isFixedBits`.
- **Argon rewrite rules** — `AliasRewrites.rewriteDenseAlias` flattens nested dense aliases. `CounterIterRewriteRule` recognizes `iter % par` and emits `LaneStatic`. `LUTConstReadRewriteRules` flattens constant LUT reads to `VecAlloc`. `VecConstRewriteRules.VecConstProp` is a global rule.
- **ArgIn injection** — `FriendlyTransformer.transform/AccelScope` scans `block.nestedInputs` for unreferenced bit values, wraps them in fresh `ArgInNew` + `setArg`.
- **If-then-else → Switch flattening** — `SwitchTransformer.extractSwitches` walks an else-chain, hoisting common statements per `shouldMotionFromConditional`, and emits a flat `Switch(selects, cases)` with pre-OR'd conditions.
- **Switch simplification** — `SwitchOptimizer.transform/Switch` drops `FALSE` selectors, collapses single-TRUE to inline, collapses 1-case to inline, converts to `Mux`/`oneHotMux` if all bodies motion-safe. Also calls `markHotSwaps`.
- **Blackbox lowering** — `BlackboxLowering` runs twice; `lowerSLA/SRA/SRU` builds shift-via-`Foreach` + reg fallbacks for non-constant shifts. `DenseTransfer.lower`/`SparseTransfer.lower`/`FrameTransmit.lower` are invoked only on the second pass.
- **DenseAlias de-aliasing** — `MemoryDealiasing.readMux`/`writeDemux`/`resetDemux` emit per-alias reads, then mux them on the condition vector.
- **LaneStatic folding** — `LaneStaticTransformer` catches `FixNeg`/`FixAdd`/`FixSub`/`FixMul`/`FixSLA` on existing `LaneStatic` nodes and resolves `FixMod(x, Final(y))` when the pre-unroll iter has par>1 and `staticMod(mul, iter, y)` returns true.
- **PipeInserter** — classifies each statement as `Transient`/`Alloc`/`Primitive`/`Control`/`FringeNode`; `computeStages` assigns to `Stage`s; `bindStages` bundles inner stages with the following outer stage when consumed; `wrapInner` emits a `Pipe { … resWrite(r, s) }` for each inner stage, replacing escaping values with register/FIFOReg holders.
- **Unrolling core** — `UnrollingBase.transform` dispatches every symbol through `unroll` which branches on `rhs.isControl` → `duplicateController` (wraps ≥2 copies in `ParallelPipe`) vs `lanes.duplicate` for primitives. `UnitUnroller`/`FullUnroller`/`PartialUnroller` differ in how they build `indices` and `indexValids`. `MemoryUnrolling.unrollMemory` duplicates memory allocations per dispatch.
- **Rewrite transformer** — `RewriteTransformer.transform` matches on `FixMul`/`FixDiv`/`FixMod` const ops to rewrite with `rewriteMul`/`rewriteDivWithMersenne`/`crandallDivMod`. FMA fusion guarded by `specializationFuse` + `canFuseAsFMA`. `RegWrite(reg, Op(Mux(sel, RegRead(reg), b)))` rewrites to an enabled `RegWrite`.
- **Flattening** — `FlatteningTransformer`. Three cases: inner-controller/innerStage switches are replaced with `Mux`/`oneHotMux`; single-child outer UnitPipe + UnitPipe-child is merged.
- **Binding (parallel grouping)** — `BindingTransformer.precomputeBundling` walks children left-to-right, maintaining `prevMems`/`prevWrMems`; a new group starts when the next child shares a non-singleton non-DRAM memory or hits other conditions. `applyBundling` wraps each >1 group in a `ParallelPipe`.
- **Accum specialization** — `AccumTransformer.optimizeAccumulators` partitions statements into pre-/in-/post-cycle groups, then for each cycle group matches `AccumMarker.Reg.Op`/`Reg.FMA` and replaces the reader/writer pair with a single `RegAccumOp` or `RegAccumFMA`.
- **Retiming** — `RetimingTransformer.retimeBlock` collects scope + result symbols, calls `pipeLatencies(result, scope)` to compute `(delays, cycles)`, then `retimeStms` mirrors each stmt inside an `isolateSubst` with delay-line substitutions from `registerDelays`. Switches have specialized handlers.
- **Reg-read CSE** — `RegReadCSE.transform` uses Argon's `state.cache.get(op2).filter(_.effects == effects)` to dedupe reads in inner controllers.
- **Transient cleanup** — `TransientCleanup` duplicates transient primitives per consumer block when `lhs.users` span multiple blocks. Also drops unused regs/writes/counters.
- **Access analysis** — `AccessAnalyzer.Affine.unapply` recognizes affine access via `Plus`/`Minus`/`Times`/`Read` unapplies, combining `AffineComponent` sequences via `combine`.
- **Banking grouping and search** — `MemoryConfigurer.bank` groups accesses, then `mergeReadGroups`/`mergeWriteGroups` search for feasible banking. `requireConcurrentPortAccess` captures the 7-case concurrency rule. `cost` computes LUT/FF/BRAM area estimates. `ExhaustiveBanking.bankAccesses` tries every `(BankingView, NStrictness, AlphaStrictness, RegroupDims)` tuple up to `bankingEffort` and `bankingTimeout`.
- **Memory allocation** — `MemoryAllocator.allocate` iterates `target.memoryResources` in order (URAM → BRAM → LUTRAM), sorting remaining duplicates by raw area; a duplicate is assigned to a resource iff `area ≤ capacity && depth ≥ resource.minDepth`.
- **Use analysis** — `UseAnalyzer.visitBlock` hooks block entry/exit to call `addUse` on the controller with block inputs/result's pending uses.
- **Retiming analysis** — `RetimingAnalyzer.retimeBlock` calls `pipeLatencies` and assigns `fullDelay = scrubNoise(l - latencyOf(s, inReduce=cycles(s)))`.
- **II computation** — `InitiationAnalyzer.visitInnerControl` computes `compilerII = ceil(interval/iterDiff)` with special cases.
- **Iter-diff analysis** — `IterationDiffAnalyzer.findCycles` finds reduce cycles via `findAccumCycles`, then for each cycle computes `selfRelativeTicks`.
- **Buffer recompute** — `BufferRecompute.visit/MemAlloc` recomputes `depth = max(bufPort)+1` using `computeMemoryBufferPorts`.
- **Broadcast cleanup** — `BroadcastCleanupAnalyzer` walks reverse stmt order in each inner controller and propagates `isBroadcastAddr=false`.
- **HierarchicalToStream** — creates per-controller FIFO triples and synchronizer controllers (`releaseGen`) that dequeue pseudo-iter tokens, write debug regs, enqueue FIFOs, compute `stopWhen`.

## 7. Invariants / IR state read or written

- **Reads** — `accessPattern`, `affineMatrices`, `residual`, `modulus`, `rawSchedule`, `rawLevel`, `rawChildren`, `rawParent`, `rawScope`, `blk`, `accumType`, `reduceCycle`, `marker`, `canFuseAsFMA`, `isInnerReduceOp`, `fullDelay`, `inCycle`, `II`, `compilerII`, `bodyLatency`, `unrollBy`, `explicitBanking`, `explicitNs`, `explicitAlphas`, `nConstraints`, `alphaConstraints`, `duplicates`, `instance`, `port`, `dispatch`, `isBroadcastAddr`, `writers`, `readers`, `writtenMems`, `readMems`, `writtenDRAMs`, `readDRAMs`, `transientReadMems`, `users`, `PendingUses`, `LocalMemories`, `RemoteMemories`, `fifoInits`, `keepUnused`, `hotSwapPairings`, `isDephasedAccess`, `iterDiff`, `counter`, `ctrStart/ctrEnd/ctrStep/ctrPar`, `shouldNotBind`, `freezeMem`, `isLoopControl`, `isInnerControl`, `isOuterControl`, `isPipeControl`, `isSeqControl`, `isFork`, `isStreamControl`, `hasStreamAncestor`, `isCtrlBlackbox`.
- **Writes** — Most of the above (each pass typically reads some and produces others). Notable: `SpatialFlowRules` populates the entire control hierarchy metadata on every staged symbol. `UseAnalyzer` writes `Users`, `PendingUses`, `transientReadMems`, `isBreaker`, `isUnusedMemory`. `AccessAnalyzer` writes `accessPattern`, `affineMatrices`. `AccumAnalyzer` sets `reduceCycle`. `MemoryConfigurer.finalize` writes `Duplicates`, `Dispatch`, `Ports`, `GroupId`. `RetimingAnalyzer` writes `fullDelay`, `inCycle`, `bodyLatency`. `InitiationAnalyzer` writes `II`, `compilerII`, `bodyLatency`. `RewriteAnalyzer` writes `canFuseAsFMA`. `RewriteTransformer` sets `residual`, `modulus` on rewritten nodes. `BufferRecompute` updates `duplicates` depth. `MetadataStripper` clears `Duplicates`/`Dispatch`/`Ports`/`GroupId`/`FifoInits`.
- **Invariants assumed / established** — (a) After `PipeInserter`, no outer control has a mix of primitives and controllers. (b) After `UnrollingTransformer`, loop controllers are `UnrolledForeach`/`UnrolledReduce`. (c) After `RetimingTransformer`, every bit-valued input's delay is a `DelayLine` node. (d) After `BankingAnalysis`, `mem.duplicates` is the authoritative set. (e) `AccelTraversal.inHw` is established by matching on `AccelScope`/`SpatialBlackboxImpl`/`BlackboxImpl`. (f) `CounterIterSynchronization` reasserts that every counter's `iter` has a valid `IndexCounterInfo(ctr, 0 until par)`.

## 8. Notable complexities or surprises

- **Pass order is canonical and load-bearing.** From `Spatial.scala:164-253`:
  1. `cliNaming` (pre-Accel traversal)
  2. `friendlyTransformer` (ArgIn wrapping)
  3. `userSanityChecks`
  4. `switchTransformer`; `switchOptimizer`; `blackboxLowering1` (lowerTransfers=false); `blackboxLowering2` (lowerTransfers=true) — first round of lowering.
  5. optional `textCleanup` if `--textCleanup`.
  6. DSE: optional `paramAnalyzer`, optional `retimeAnalysisPasses` + `initiationAnalyzer` + `dseRuntimeModelGen`, optional `dsePass`.
  7. Second round: `switchTransformer`; `switchOptimizer`; `memoryDealiasing`; optional `laneStaticTransformer`.
  8. **`pipeInserter`** — first control insertion pass.
  9. `regReadCSE`; DCE (`useAnalyzer`, `transientCleanup`, `printer`, `transformerChecks`).
  10. optional streamify block.
  11. optional `streamTransformer` (`--distributeStreamCtr`).
  12. `fifoInitialization` (= `fifoInitializer`, `pipeInserter`, stripper for `FifoInits`).
  13. **banking analysis** — `retimeAnalysisPasses`; `accessAnalyzer`; `iterationDiffAnalyzer`; `memoryAnalyzer`; `memoryAllocator`.
  14. `counterIterSynchronization`; dump `PreExecution`; `transformerChecks`.
  15. optional `executor` (`--scalaExec`).
  16. **`unrollTransformer`** — the unroller.
  17. `regReadCSE`; DCE; `retimingAnalyzer` + `printer` + `streamChecks`.
  18. `rewriteAnalyzer`; optional `accumAnalyzer`; `rewriteTransformer`; `memoryCleanup`.
  19. `flatteningTransformer`; `bindingTransformer`.
  20. `bufferRecompute`; `transformerChecks`.
  21. optional `accumAnalyzer`; optional `accumTransformer` (under `enableOptimizedReduce`).
  22. `retimingAnalyzer`; **`retiming`**; `retimeReporter`.
  23. `broadcastCleanup`; `initiationAnalyzer`; optional `finalRuntimeModelGen`; `memoryReporter`; `finalIRPrinter`; `finalSanityChecks`.
  24. Codegens.

- Several files are entirely commented out and should be treated as historical artifacts:
  - `transform/LoopPerfecter.scala` — Halide-style loop perfection, full file is `//`.
  - `transform/streamify/FlattenToStream.scala` — 1119 lines, all commented. Superseded by `HierarchicalToStream`.
  - `transform/streamify/StreamingControlBundle.scala` — 88/103 lines commented.
  - `transform/debug/SRAMDumper.scala` — entirely commented.
  - `traversal/AreaAnalyzer.scala` — entirely commented.
  - `transform/unrolling/BlackBoxUnrolling.scala` — empty stub class.
- **`pipeInserter` is run twice** (steps 8 and 10) and once more as part of `fifoInitialization` (step 12) before banking.
- **Unroller vectorization vs staged-lane** — `Ps.product` interpretation flips on `vectorize = isInnerLoop && spatialConfig.vecInnerLoop`; mop vs pom determines whether duplicated controllers are wrapped in a `ParallelPipe` or cross-sectioned.
- **Banking cost feedback loops** — `MemoryConfigurer` reruns up to `bankingTimeout` trials, memoizing via `solutionCache`.
- **Retiming vs. unrolling coupling** — `retimingAnalyzer` runs _three_ times (before banking, after unrolling, before the retiming transformer).
- **Reduce specialization gate** — `accumTransformer` is only invoked when `spatialConfig.enableOptimizedReduce` is on.
- **`Switch` primitivity** — retiming treats switches as _not_ inner controllers.
- **Iterator dephasing** — Banking analysis mutates access iterators via `generateSubstRules`/`rewriteAccesses` — the new access matrix may have fresh `boundVar[I32]` indices that later passes cannot re-resolve.
- **Hot-swap pairings** — `SwitchOptimizer.markHotSwaps` records (reader, conflicting-writers) on the memory's `hotSwapPairings` — used downstream during codegen/banking but set by a transformer, not an analyzer.
- **`LaneStaticTransformer` runs before unrolling but its effect is felt at banking**.
- **`FIFOConfigurer` refuses to bank concurrent groups** — raises `UnbankableGroup` rather than guessing a scheme.
- **`BindingTransformer` reorders sibling controllers** but never reorders across stream / break / shouldNotBind boundaries.
- **`MemoryDealiasing` runs before unrolling** but alias nodes for `Reduce`/`MemReduce` accumulator tracking are deliberately left in place for unrolling and cleaned later.
- **`EarlyUnroller`** mixes in `spatial.util.TransformerUtilMixin` _and_ `CounterIterUpdateMixin`. This is the only transformer in the subsystem that extends `ForwardTransformer` (not `MutateTransformer`), forced by the shape of the streamify transform.
- **Memory analyzer entry file** — `MemoryAnalyzer` is a `Codegen` (!), not a `Pass`. It emits an HTML report (`decisions_${state.pass}.html`) during analysis.

## 9. Open questions

- What invariants must `BindingTransformer` preserve vs. break?
- Is the `streamify` pipeline stable / supported?
- When does `RetimingTransformer.precomputeDelayLines` choose _not_ to create a delay line?
- How does `AccumAnalyzer` distinguish `Reduce` vs generic `Fold` accumulation in the presence of nested reduce cycles?
- `laneStaticTransformer` runs only when `!spatialConfig.vecInnerLoop` — why?
- Order of `rewriteAnalyzer` vs `accumAnalyzer` after unrolling: do we need both?
- `EarlyUnroller` uses a different `ForwardTransformer` + `TransformerUtilMixin`; is this a sign that a full migration of the unroller to `ForwardTransformer` is planned?
- What is the relationship between `AreaAnalyzer` (commented out) and the area estimation in `banking/MemoryConfigurer.cost`?
- How exactly does `FIFOAccessFusion` interact with retiming's `RetimeGate` boundaries?
- `MetadataStripper` usage is sparse in the canonical chain. When is `bankStrippers` actually applied?

## 10. Suggested spec sections

Under `10 - Spec/`:
- `10 - Spec/Passes/00 - Pipeline Order.md` — canonical enumeration of the `==>` chain and gate conditions.
- `10 - Spec/Passes/Flows.md` — `SpatialFlowRules` per-rule behavior and metadata contract.
- `10 - Spec/Passes/Rewrites.md` — the four rewrite-rule trait files.
- `10 - Spec/Passes/Friendly-and-Sanity.md` — `FriendlyTransformer`, `TextCleanup`, `UserSanityChecks`, `CompilerSanityChecks`, `AbstractSanityChecks`.
- `10 - Spec/Passes/Switch-and-Conditional.md` — `SwitchTransformer`, `SwitchOptimizer`, `FlatteningTransformer` (switch-to-mux path).
- `10 - Spec/Passes/Pipe-Insertion.md` — `PipeInserter` algorithm (the stage/bound/wrap dance).
- `10 - Spec/Passes/Unrolling.md` — UnrollingBase + per-controller unrollers + `MemoryUnrolling` mem-dispatch mapping.
- `10 - Spec/Passes/Rewrites-Transformer.md` — hardware rewrites, Crandall mod/div, FMA fusion.
- `10 - Spec/Passes/Retiming.md` — `RetimingAnalyzer` + `RetimingTransformer` + `DuplicateRetimeStripper` + retime-block trifecta.
- `10 - Spec/Passes/Access-and-Banking.md` — `AccessAnalyzer`, `AccessExpansion`, `MemoryAnalyzer`, `MemoryConfigurer`, `ExhaustiveBanking`, `FullyBanked`, `CustomBanked`, `FIFOConfigurer`, `MemoryAllocator`.
- `10 - Spec/Passes/Analyses.md` — `UseAnalyzer`, `AccumAnalyzer`, `IterationDiffAnalyzer`, `InitiationAnalyzer`, `PerformanceAnalyzer`, `BufferRecompute`, `BroadcastCleanup`, `RewriteAnalyzer`, `CLINaming`, `CounterIterSynchronization`.
- `10 - Spec/Passes/Cleanup.md` — `TransientCleanup`, `MemoryCleanupTransformer`, `AllocMotion`, `RegReadCSE`, `FIFOAccessFusion`, `MetadataStripper`, `UnitIterationElimination`, `ForeachToUnitpipe`, `UnitPipeToForeach`.
- `10 - Spec/Passes/Streamify.md` — `EarlyUnroller`, `DependencyGraphAnalyzer`, `HierarchicalToStream`, `StreamingControlBundle`, `AccelPipeInserter`, `FIFOInitializer`, `ForceHierarchical`, `TimeMap`; also call out the commented-out `FlattenToStream`.
- `10 - Spec/Passes/Binding-and-Accum.md` — `BindingTransformer`, `AccumTransformer`.
- `10 - Spec/Passes/Blackbox-Lowering.md` — `BlackboxLowering` (two-phase), `MemoryDealiasing`, `LaneStaticTransformer`, `StreamTransformer`, `StreamConditionSplitTransformer`.
