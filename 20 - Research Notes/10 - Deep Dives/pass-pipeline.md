---
type: deep-dive
topic: pass-pipeline
source_files:
  - "src/spatial/Spatial.scala"
  - "src/spatial/flows/SpatialFlowRules.scala"
  - "src/spatial/rewrites/SpatialRewriteRules.scala"
  - "src/spatial/transform/PipeInserter.scala"
  - "src/spatial/transform/unrolling/UnrollingBase.scala"
  - "src/spatial/transform/RetimingTransformer.scala"
  - "src/spatial/traversal/RetimingAnalyzer.scala"
  - "src/spatial/traversal/MemoryAnalyzer.scala"
  - "src/spatial/traversal/MemoryAllocator.scala"
  - "src/spatial/traversal/banking/MemoryConfigurer.scala"
  - "src/spatial/traversal/banking/ExhaustiveBanking.scala"
session: 2026-04-23
status: ready-to-distill
feeds_spec:
  - "[[10 - Flows and Rewrites]]"
  - "[[50 - Pipe Insertion]]"
  - "[[70 - Banking]]"
  - "[[80 - Unrolling]]"
  - "[[C0 - Retiming]]"
---

# Pass Pipeline — `Spatial.runPasses` Walkthrough

This note traces the full 24-step Spatial pass pipeline as expressed in the `Spatial.runPasses` method. The pipeline is a single lazy-val + `==>` chain expression: every pass is lazily allocated first (`src/spatial/Spatial.scala:65-136`), then composed in `val result = { block ==> … }` (`src/spatial/Spatial.scala:164-253`). Each arrow in that chain is a tight coupling of metadata flow: later passes consume metadata written by earlier passes, and skipping or reordering passes silently breaks downstream analyses.

## Reading log

Read files in order: `Spatial.scala` (specifically lines 56-257 for `flows()`, `rewrites()`, and `runPasses`), `SpatialFlowRules.scala`, `SpatialRewriteRules.scala`, the four rewrite-rule trait files, `PipeInserter.scala`, `UnrollingBase.scala`, `ForeachUnrolling.scala`, `ReduceUnrolling.scala`, `MemReduceUnrolling.scala`, `MemoryUnrolling.scala`, `SwitchUnrolling.scala`, `AccessAnalyzer.scala`, `MemoryAnalyzer.scala`, `MemoryAllocator.scala`, `banking/MemoryConfigurer.scala`, `banking/ExhaustiveBanking.scala`, `banking/FullyBanked.scala`, `banking/CustomBanked.scala`, `banking/FIFOConfigurer.scala`, `RetimingAnalyzer.scala`, `RetimingTransformer.scala`, `DuplicateRetimeStripper.scala`, `AccumTransformer.scala`.

## The lazy-val block (setup, `Spatial.scala:60-163`)

Inside `runPasses`, Spatial allocates ~60 `lazy val` passes in categorical groups: Debug (2), Checking (4), Analysis (11), DSE (2), Reports (2), Transformer (24), Executor (1), Stripper (1), and Codegen (13). `lazy val` semantics mean that if a config flag disables a pass (e.g. `enableRetiming=false`), the pass object is never constructed, which matters because pass constructors can be expensive (`MemoryAnalyzer` builds an HTML emitter, `ExecutorPass` allocates the simulator state).

Two sub-sequences are reused:
- `retimeAnalysisPasses = Seq(printer, duplicateRetimeStripper, printer, retimingAnalyzer)` — `Spatial.scala:140`. Note the embedded `DuplicateRetimeStripper`: every retime analysis run is preceded by collapsing back-to-back `RetimeGate()` nodes.
- `bankingAnalysis = retimeAnalysisPasses ++ Seq(accessAnalyzer, iterationDiffAnalyzer, printer, memoryAnalyzer, memoryAllocator, printer)` — `Spatial.scala:142`. Banking runs retime analysis first because it needs provisional cycle counts for `requireConcurrentPortAccess`.
- `fifoInitialization = Seq(fifoInitializer, pipeInserter, MetadataStripper(state, S[FifoInits]))` — `Spatial.scala:138`. This is where `pipeInserter` runs a *second* time (the first is at `Spatial.scala:190`).
- `streamify = ...` — `Spatial.scala:144`. The gate is `spatialConfig.streamify`.

`DCE = Seq(useAnalyzer, transientCleanup, printer, transformerChecks)` — `Spatial.scala:162` — a reusable DCE recipe.

## The `==>` chain (execution order, `Spatial.scala:164-253`)

I walk through each step. Config-gated steps use the `? :` ternary form: `(cond) ? pass` or `(cond) ? pass1 : pass2` (implemented in argon's `Pass`). When `cond` is false the right-hand side is `Nil`.

### Step 1 — Entry + CLI naming (`:166-167`)

```scala
block ==> printer     ==>
cliNaming           ==>
```

`CLINaming` (`traversal/CLINaming.scala`) walks `ArgIn`/`InputArguments` references and tags them with `CLIArgs` names from the Scala-level array accesses. Reads nothing, writes `metadata.access.CLIArgs`.

### Step 2 — Friendly transformer (`:168`)

```scala
(friendlyTransformer) ==> printer ==> transformerChecks ==>
```

`FriendlyTransformer` (`transform/FriendlyTransformer.scala`) is the first mutating pass. It scans the outer `AccelScope` for bit-valued Scala-level references that were not wrapped in `ArgIn`, auto-creates `ArgInNew` + `setArg`, and dedupes DRAM dimension values. The `friendly` naming is literal: the pass exists so that new-users' apps compile without forcing explicit `ArgIn` everywhere.

### Step 3 — User sanity checks (`:169`)

```scala
userSanityChecks    ==>
```

`UserSanityChecks` gate: `enable = !spatialConfig.allowInsanity` (`Spatial.scala:71`). Emits user-facing errors (ArgOut-read-in-Accel, width mismatches).

### Step 4 — First lowering round (`:171-175`)

```scala
(switchTransformer)   ==> printer ==> transformerChecks ==>
(switchOptimizer)     ==> printer ==> transformerChecks ==>
(blackboxLowering1)   ==> printer ==> transformerChecks ==>
(blackboxLowering2)   ==> printer ==> transformerChecks ==>
```

- `SwitchTransformer` flattens nested `IfThenElse` into `Switch` + `SwitchCase`.
- `SwitchOptimizer` simplifies trivial switches (`FALSE` selectors, single-case) and records `hotSwapPairings` via `markHotSwaps`.
- `BlackboxLowering` runs **twice**: first with `lowerTransfers=false` (`Spatial.scala:103`), second with `lowerTransfers=true` (`Spatial.scala:104`). The first pass lowers non-transfer things (variable-shift patterns like `FixSLA`/`FixSRA`/`FixSRU` with non-constant shifts); the second pass lowers `DenseTransfer`/`SparseTransfer`/`FrameTransmit` to `Fringe*` ops. Running twice allows the first pass's rewrites to simplify the inputs to the second pass's lowering.

### Step 5 — Optional text cleanup (`:176`)

```scala
(spatialConfig.textCleanup) ? textCleanup ==>
```

Gate: `--textCleanup` flag. Drops symbols with `canAccel=false` inside the Accel.

### Step 6 — Optional DSE (`:178-183`)

```scala
((spatialConfig.enableArchDSE) ? paramAnalyzer) ==>
((spatialConfig.enableRuntimeModel) ? retimeAnalysisPasses) ==>
((spatialConfig.enableRuntimeModel) ? initiationAnalyzer) ==>
((spatialConfig.enableRuntimeModel) ? dseRuntimeModelGen) ==>
(spatialConfig.enableArchDSE ? dsePass) ==>
```

`paramAnalyzer` runs when DSE is on. The retime-analysis-then-initiation-analysis pair runs only under `enableRuntimeModel` (set by `--runtime` or the various `--tune`/`--bruteforce`/`--heuristic`/`--experiment`/`--hypermapper` flags: `Spatial.scala:268-272` + `549-551`). `dseRuntimeModelGen` emits a Scala model at this point for the DSE kernel. `dsePass` does the search.

### Step 7 — Second lowering round (`:185-188`)

```scala
switchTransformer   ==> printer ==> transformerChecks ==>
switchOptimizer     ==> printer ==> transformerChecks ==>
memoryDealiasing    ==> printer ==> transformerChecks ==>
((!spatialConfig.vecInnerLoop) ? laneStaticTransformer)   ==>  printer ==>
```

Important subtlety: `switchTransformer` and `switchOptimizer` are **re-run** because DSE may have introduced new decision branches. `MemoryDealiasing` resolves `MemDenseAlias`/`MemSparseAlias` into muxed reads of the underlying DRAM — this must happen **before** unrolling. `LaneStaticTransformer` gates on `!spatialConfig.vecInnerLoop`: PIR/Plasticine vectorizes inner loops, which already handles lane broadcast, so the pre-unroll `FixMod/iter` → `LaneStatic` rewrite would be redundant.

### Step 8 — Pipe insertion #1 (`:190`)

```scala
pipeInserter        ==> printer ==> transformerChecks ==>
```

First invocation of `PipeInserter`. Post-condition: no outer control has a mix of primitives and controllers (the pass sets `spatialConfig.allowPrimitivesInOuterControl = false` in `postprocess`, `transform/PipeInserter.scala:319-320`).

### Step 9 — CSE + DCE (`:192-194`)

```scala
regReadCSE          ==>
DCE ==>
```

`RegReadCSE` dedupes `RegRead` inside inner controllers. `DCE` runs the 4-pass DCE recipe.

### Step 10 — Optional streamify (`:196`)

```scala
spatialConfig.streamify ? streamify ==>
```

Gate: `--streamify`. Runs `dependencyGraphAnalyzer`, `initiationAnalyzer`, `HierarchicalToStream`, a post-streamify `switchTransformer`, and a second `pipeInserter`. (Yes: this is the *second* `pipeInserter` invocation in the pipeline.)

### Step 11 — Optional stream counter distribution (`:198`)

```scala
(spatialConfig.distributeStreamCtr ? streamTransformer) ==> printer ==>
```

Gate: `--distributeStreamCtr` (default on unless `--noModifyStream` was passed: `Spatial.scala:346-348`). `StreamTransformer` distributes a `Stream.Foreach`'s counter chain into its child controllers.

### Step 12 — FIFO initialization (`:200-201`)

```scala
fifoInitialization ==> printer ==>
spatialConfig.streamify ? createDump("PostInit") ==>
```

`fifoInitialization` runs `fifoInitializer`, `pipeInserter` (**third** invocation), and a `MetadataStripper` clearing `FifoInits` metadata so it doesn't re-trigger. The streamify-only dump is a tree + HTML IR snapshot.

### Step 13 — Banking analysis (`:203`)

```scala
bankingAnalysis ==>
```

Expanded = `retimeAnalysisPasses ++ Seq(accessAnalyzer, iterationDiffAnalyzer, printer, memoryAnalyzer, memoryAllocator, printer)`. So the sub-sequence is:
1. `printer` (dump)
2. `DuplicateRetimeStripper` (collapse back-to-back `RetimeGate`s)
3. `printer`
4. `RetimingAnalyzer` (first run — compute provisional `fullDelay`, `inCycle`, `bodyLatency` for use in banking's concurrency rule)
5. `AccessAnalyzer` (`Affine.unapply` walks all accesses; writes `accessPattern`, `affineMatrices`)
6. `IterationDiffAnalyzer` (writes `iterDiff` for reduce cycles)
7. `printer`
8. `MemoryAnalyzer` (per-memory `MemoryConfigurer.configure()`; writes `Duplicates`/`Dispatch`/`Ports`/`GroupId`; also emits `decisions_<pass>.html`)
9. `MemoryAllocator` (greedy first-fit assignment of each duplicate to a physical `MemoryResource`)
10. `printer`

### Step 14 — Counter synchronization + checkpoint (`:204-207`)

```scala
counterIterSynchronization ==>
createDump("PreExecution") ==>
transformerChecks ==>
(spatialConfig.enableScalaExec ? (Seq(executor) ++ createDump("PostExecution"))) ==>
```

`CounterIterSynchronization` re-establishes `IndexCounterInfo(ctr, 0 until par)` on each counter's iter. The `PreExecution` dump is a tree+HTML snapshot for debugging. `executor` runs under `--scalaExec`.

### Step 15 — Unrolling (`:209`)

```scala
unrollTransformer   ==> printer ==> transformerChecks ==>
```

`UnrollingTransformer` is a trivial composition mixing `UnitUnroller` / `LoopUnroller` / `ForeachUnrolling` / `ReduceUnrolling` / `MemReduceUnrolling` / `MemoryUnrolling` / `SwitchUnrolling` / `BlackBoxUnrolling` traits over `UnrollingBase`. Post-condition: all loop controllers are `UnrolledForeach` / `UnrolledReduce`; memory allocations are duplicated per `Duplicates`.

### Step 16 — Post-unroll cleanup (`:211-213`)

```scala
regReadCSE          ==>
DCE ==> Seq(retimingAnalyzer, printer, streamChecks) ==>
```

Second `retimingAnalyzer` invocation (inside the inline seq). Unrolling created new `RetimeGate`s and changed latencies, so retiming metadata must be recomputed.

### Step 17 — Hardware rewrites (`:215-218`)

```scala
rewriteAnalyzer     ==>
(spatialConfig.enableOptimizedReduce ? accumAnalyzer) ==> printer ==>
rewriteTransformer  ==> printer ==> transformerChecks ==>
memoryCleanup  ==> printer ==> transformerChecks ==>
```

`RewriteAnalyzer` sets `canFuseAsFMA` on `FixAdd`/`FltAdd` nodes. The optional `accumAnalyzer` runs first to identify accumulation cycles so that `rewriteTransformer`'s FMA fusion can mark them. `rewriteTransformer` then does pow2-multiplies, Crandall mod/div, FMA fusion, reg-write-of-mux → enabled RegWrite, sqrt/recip fusion. `memoryCleanup` drops local memories with no readers AND no writers (post-rewrite).

### Step 18 — Flattening + binding (`:220`)

```scala
flatteningTransformer ==> bindingTransformer ==>
```

`FlatteningTransformer` inlines outer `UnitPipe` with a single non-stream child. `BindingTransformer` bundles consecutive non-conflicting sibling controllers into a `ParallelPipe`.

### Step 19 — Buffer recompute (`:222`)

```scala
bufferRecompute     ==> printer ==> transformerChecks ==>
```

`BufferRecompute` recomputes `depth = max(bufPort)+1` per memory using `computeMemoryBufferPorts`. This is needed because post-unroll / post-`MemReduce`-unrolling can produce different N-buffer depths than what banking computed.

### Step 20 — Optional accumulator specialization (`:224-225`)

```scala
(spatialConfig.enableOptimizedReduce ? accumAnalyzer) ==> printer ==>
(spatialConfig.enableOptimizedReduce ? accumTransformer) ==> printer ==> transformerChecks ==>
```

`AccumAnalyzer` runs **again** (second run under this flag). `AccumTransformer` replaces marked WAR cycles with `RegAccumOp` / `RegAccumFMA` single-node accumulators (II=1).

### Step 21 — Retiming (`:227-229`)

```scala
retimingAnalyzer    ==> printer ==>
retiming            ==> printer ==> transformerChecks ==>
retimeReporter      ==>
```

Third `RetimingAnalyzer` invocation. Then `RetimingTransformer` actually inserts `DelayLine` nodes and rewires consumers. `RetimeReporter` writes the retiming report.

So `RetimingAnalyzer` runs **three** times in total:
1. Inside `retimeAnalysisPasses` at step 13 (banking analysis).
2. Inside the post-unroll DCE chain at step 16.
3. Just before `RetimingTransformer` at step 21.

### Step 22 — Broadcast cleanup + finalization (`:231-238`)

```scala
broadcastCleanup    ==> printer ==>
initiationAnalyzer  ==>
((spatialConfig.enableRuntimeModel) ? finalRuntimeModelGen) ==>
memoryReporter      ==>
finalIRPrinter      ==>
finalSanityChecks   ==>
```

`BroadcastCleanupAnalyzer` walks reverse stmt order per inner controller and propagates `isBroadcastAddr=false` where appropriate. `InitiationAnalyzer` computes `II`/`compilerII`/`bodyLatency` per controller. `finalSanityChecks` is un-gated (`enable = !spatialConfig.allowInsanity`, `Spatial.scala:73`).

### Step 23 — Codegens (`:241-252`)

Tree+HTML IR always emit. `dotFlatGen`/`dotHierGen` under `--dot`/`--fdot`. `scalaCodegen` under `--sim`. `chiselCodegen` + `cppCodegen` under `--synth`. `rogueCodegen` if `target.host == "rogue"`. `resourceReporter` + `ResourceCountReporter` under `--reportArea`/`--countResources`. `pirCodegen` + `tsthCodegen` under `--pir`/`--tsth`.

## Observations

### Observation 1 — flows and rewrites are registered, not invoked

`override def flows(): Unit = SpatialFlowRules(state)` (`Spatial.scala:57`) and `override def rewrites(): Unit = SpatialRewriteRules(state)` (`Spatial.scala:58`) construct the rule sets during argon compiler initialization. The `@flow` methods in `SpatialFlowRules` (`flows/SpatialFlowRules.scala:14, 21, 44, 69, 289, 305, 331, 389, 406`) fire **every time a new symbol is staged** (argon's staging pipeline invokes all registered `@flow` callbacks after creating the symbol). The `@rewrite` definitions and `IR.rewrites.add[...]` / `IR.rewrites.addGlobal` calls in the rewrite-rule files (`rewrites/AliasRewrites.scala:68, 72, …, 103`, `rewrites/CounterIterRewriteRule.scala:18`, `rewrites/LUTConstReadRewriteRules.scala:13`, `rewrites/VecConstRewriteRules.scala:13`) fire at **register time** — i.e., when staging creates a symbol matching the pattern, it's rewritten before being added to the IR.

Flow rules are ordered by definition: `memories` → `accesses` → `accumulator` → `controlLevel` → `blackbox` → `blockLevel` → `controlSchedule` → `streams` → `globals`. The `controlSchedule` rule's 6-case priority (documented `flows/SpatialFlowRules.scala:317-330`) deserves special call-out: it is the only place where the Spatial scheduler imposes hardware-specific defaults (UnitPipe → Sequenced by default; everything else → Pipelined; inner controllers can't be Streaming; single-child outer controllers can't be Pipelined).

### Observation 2 — `PipeInserter` runs three times

Line numbers: `190` (first), `144` (second, inside streamify block), and `138` (third, inside `fifoInitialization`). This is surprising but intentional: each lowering or transformer that introduces new primitive/controller mixes requires pipe re-insertion to re-establish the outer-mix invariant. The `fifoInitializer` specifically introduces new `UnitPipe`s for FIFO init, which then need `pipeInserter` to wrap properly.

### Observation 3 — `RetimingAnalyzer` runs three times

Sequence: inside `retimeAnalysisPasses` (banking needs provisional cycle info), after DCE (after unrolling changes the schedule), before `RetimingTransformer` (final authoritative pass). See `Spatial.scala:140, 213, 227`. Each invocation clears `fullDelay` in `preprocess` (`traversal/RetimingAnalyzer.scala:21-24`) before recomputing, so later invocations don't silently accumulate bias from earlier ones.

### Observation 4 — `MemoryAnalyzer` is a `Codegen`, not a `Pass`

`case class MemoryAnalyzer(IR: State)(implicit isl: ISL, areamodel: AreaEstimator) extends Codegen` (`traversal/MemoryAnalyzer.scala:17`). Override: `override val ext: String = "html"` (`:22`), `override def entryFile: String = s"decisions_${state.pass}.html"` (`:24`). This pass produces an HTML report as a side effect of performing the analysis. The `run()` method at `:141-167` iterates over `LocalMemories.all`, picks a configurer per memory type (`:125-139`), and calls `conf.configure()` which drives the banking search.

### Observation 5 — `AccumAnalyzer` runs up to twice under `enableOptimizedReduce`

First invocation: inside `rewriteAnalyzer` block (`Spatial.scala:216`). Second invocation: before `accumTransformer` (`:224`). Why twice? Because `rewriteTransformer` changes the IR shape (e.g. FMA fusion mutates the cycle), so the accumulator analysis must re-run on the updated graph to get valid `AccumMarker.Reg.Op` / `AccumMarker.Reg.FMA` tags for `accumTransformer` to match against.

### Observation 6 — `MemoryAllocator` returns `process` with `block` unchanged

The pass mutates `dup.resourceType` on each memory's duplicates (`traversal/MemoryAllocator.scala:87, 102-103`) but returns the input block unchanged. Flow: (1) filter `LocalMemories.all` into "SRAM-able" and non-SRAM partitions (`:36`); (2) iterate `target.memoryResources` in order (URAM → BRAM → LUTRAM, drop last), sorting unassigned instances by `-rawCount` (largest first); (3) greedy first-fit — assign to this resource iff `area ≤ capacity && depth ≥ resource.minDepth` (`:85`); (4) any remaining unassigned go to `resources.last` (default LUT); (5) all non-SRAM-able mems get `resources.last` unconditionally.

### Observation 7 — `FIFOConfigurer.requireConcurrentPortAccess` has 5 cases (not 7)

In the FIFO subclass (`traversal/banking/FIFOConfigurer.scala:20-26`):
```scala
(a.access == b.access && (a.unroll != b.unroll || a.access.isVectorAccess)) ||
  lca.isPipeLoop || lca.isOuterStreamLoop ||
  (lca.isInnerSeqControl && lca.isFullyUnrolledLoop) ||
  lca.isParallel
```
Five disjuncts. The *general* `MemoryConfigurer.requireConcurrentPortAccess` (`traversal/banking/MemoryConfigurer.scala:427-437`) has 7 disjuncts. Coverage note §6 says "7-case rule"; this is accurate for the general case but `FIFOConfigurer` uses a simpler rule. If the 5-case FIFO rule rejects a group, `bankGroups` raises `UnbankableGroup` (`:67`) rather than guessing.

### Observation 8 — `ExhaustiveBanking` has nested caching at two levels

`solutionCache` (`traversal/banking/ExhaustiveBanking.scala:45`) keys on `(regroupedAccs, nStricts, aStricts, axes)`. `schemesFoundCount` (`:47`) tracks per-(view, regroup) counts for `wantScheme` throttling based on `mem.bankingEffort`. The outer `wantScheme` gate (`:188-198`) implements the 3-level effort semantics: 0 = quit after first solution; 1 = 4 regions (flat, hierarchical, flat+full_duplication, hierarchical+full_duplication); 2 = each (view, regroup) gets at most 2 solutions.

### Observation 9 — `MemoryConfigurer` is 818 lines but the search is a ~40-line outer loop

The orchestrator (`traversal/banking/MemoryConfigurer.scala:55-83`) does: `resetData` → extract read/write matrices → `bank(readers, writers)` → `summarize` → `finalize` → `pirCheck`. The real complexity is in `bankGroups` (`:610-682`) which builds the candidate `BankingOptions` grid, calls `strategy.bankAccesses`, scores each via `cost`, picks the minimum, and packages into `Instance`s. `mergeReadGroups` (`:748-806`) then greedily attempts to merge each newly-banked group into existing instances, invoking `bankGroups` again to see if the merged group still has a valid scheme.

### Observation 10 — Unrolling's MoP-vs-PoM gate lives in `Unroller.vectorize` and the per-controller unrollers

`LoopUnroller.vectorize = isInnerLoop && spatialConfig.vecInnerLoop` (`transform/unrolling/UnrollingBase.scala:434`). When `vectorize` is true, `P = 1` and `V = Ps.product` (`:252-253`) — one "lane" containing all vectorized copies. When false, `P = Ps.product` and `V = 1` — one lane per copy.

MoP (default) wraps ≥2 copies in a `ParallelPipe` inside `duplicateController` (`UnrollingBase.scala:152-164`): `val lhs2 = stage(ParallelPipe(enables, block))`. PoM uses `crossSection` (`:100-112`) to generate per-lane sub-counterchains and wraps differently. Gates: `--mop` (default) vs `--pom` (`Spatial.scala:404-438`).

### Observation 11 — `RetimingTransformer.precomputeDelayLines` handles cross-block sharing

`precomputeDelayLines` (`transform/RetimingTransformer.scala:111-126`) is called in `updateNode` (`:127-130`) only when `inInnerScope` is true. For each block in `op.blocks`, it calls `findDelayLines(block.nestedStms)`, filters to lines whose `hierarchy < hierarchy` (i.e. need to exist above the current block), and creates them if they don't exist. This is the mechanism that prevents multiple blocks from each trying to create their own copy of the same delay line — the line is materialized at the outermost needed hierarchy level.

### Observation 12 — `DuplicateRetimeStripper` runs inside `retimeAnalysisPasses`, not standalone

`Spatial.scala:140`: `lazy val retimeAnalysisPasses = Seq(printer, duplicateRetimeStripper, printer, retimingAnalyzer)`. The stripper only mutates inner-control blocks (`transform/DuplicateRetimeStripper.scala:27-32`) and collapses `RetimeGate() → RetimeGate()` pairs into a single `RetimeGate()`. This matters because each `retimingAnalyzer` run is preceded by a fresh stripping pass, ensuring the second and third retiming analyses see a canonical form.

## Metadata flow summary

Consumed/produced by pass (a subset of the major ones):

| Pass | Reads | Writes |
|---|---|---|
| `SpatialFlowRules` | structural properties (`isUnitPipe`, `isAccel`, etc.) | `rawChildren`, `rawLevel`, `rawParent`, `rawScope`, `blk`, `rawSchedule`, `accumType`, `isGlobal`, `isFixedBits`, `writtenMems`, `readMems`, `writtenDRAMs`, `readDRAMs`, `readers`, `writers`, `resetters` |
| `PipeInserter` | `isOuterControl`, `isParallel`, `isStreamControl`, `inHw`, `isTransient`, `isPrimitive`, `isControl`, `isFringeNode` | (no new metadata — only IR shape; post-condition: `allowPrimitivesInOuterControl = false`) |
| `AccessAnalyzer` | `accessIterators`, `ctrStart`, `ctrStep`, `ctrPar`, `consumers`, `writers`, `readers` | `accessPattern`, `affineMatrices` |
| `MemoryAnalyzer` (via `MemoryConfigurer`) | `accessPattern`, `affineMatrices`, `explicitBanking`, `explicitNs`, `explicitAlphas`, `nConstraints`, `alphaConstraints`, `bankingEffort` | `Duplicates`, `Dispatch`, `Ports`, `GroupId`, `isDephasedAccess`, `isUnusedAccess` |
| `MemoryAllocator` | `duplicates`, `target.memoryResources`, `target.capacity` | `dup.resourceType` |
| `UnrollingTransformer` | `Duplicates`, `Dispatch`, `Ports`, `unrollBy`, `isInnerControl`, `willUnrollAsPOM`, `cchain.pars`, `rawSchedule` | new `UnrolledForeach`/`UnrolledReduce`/`UnrolledAccessor` nodes with `ports`, `dispatches`, `unrollBy`, `originalSym` |
| `RetimingAnalyzer` | `pipeLatencies` output (via `util.modeling`) | `fullDelay`, `inCycle`, `bodyLatency` |
| `RetimingTransformer` | `fullDelay`, `inCycle`, `delayLines`, `delayConsumers`, `latencies`, `cycles` | new `DelayLine` nodes (substituted for bit-valued inputs to consumers) |
| `AccumTransformer` | `reduceCycle`, `marker` (`AccumMarker.Reg.Op` / `.FMA`), `isInCycle` | replaces reader/writer pair with `RegAccumOp` / `RegAccumFMA` |

## Distillation plan

This note feeds five spec entries:

- `10 - Spec/40 - Compiler Passes/10 - Flows and Rewrites.md` — flow-rule dispatch, `@rewrite`/`IR.rewrites.add` registration, four rewrite-rule trait files.
- `10 - Spec/40 - Compiler Passes/50 - Pipe Insertion.md` — the stage/bind/wrap algorithm with the `Stage(inner/outer)` classification.
- `10 - Spec/40 - Compiler Passes/80 - Unrolling.md` — `Unroller` hierarchy, per-controller unrolling, MoP-vs-PoM, vectorization.
- `10 - Spec/40 - Compiler Passes/70 - Banking.md` — access analyzer → memory analyzer → banking strategies → memory allocator.
- `10 - Spec/40 - Compiler Passes/C0 - Retiming.md` — the retime trifecta (analyzer, transformer, stripper).

## Open questions filed

- Q-007 — Why does `PipeInserter` need a special case for `Switch` with `isOuterControl` (`transform/PipeInserter.scala:46-67`)? The code handles primitives+controllers inside SwitchCase bodies specially (`requiresWrap = primitives.nonEmpty && controllers.nonEmpty`, `:52`), wrapping in a `Pipe` inside `wrapSwitchCase` (`:100-106`).
- Q-008 — What is the relationship between `fifoInitialization`'s embedded `pipeInserter` run (third invocation) and the second `pipeInserter` inside the streamify block? They both run under different config gates; is it possible both fire on the same compile? (`--streamify` + default FIFO init.)
- Q-009 — The `FIFOConfigurer.requireConcurrentPortAccess` has 5 cases vs the general 7 cases. What are the 2 dropped cases semantically? (Reading the code: dropped are `(lca.isOuterPipeLoop && !isWrittenIn(lca))` and the `delayDefined` / `parent == parent` pair. Dropped because FIFOs can't be N-buffered, so no "write reaches buffer port" question arises.)
- Q-010 — `MemoryAnalyzer` being a `Codegen` that writes HTML as a side-effect of doing the analysis is architecturally surprising. Is the HTML emission actually reused by anything downstream, or is it pure debugging? (Grep says it's not consumed.)
