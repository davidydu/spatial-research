---
type: coverage
subsystem: Polyhedral + Models + DSE + support
paths:
  - "poly/src/"
  - "models/src/"
  - "src/spatial/dse/"
  - "src/spatial/lib/"
  - "src/spatial/executor/"
  - "src/spatial/model/"
  - "src/spatial/math/"
  - "src/spatial/issues/"
  - "src/spatial/report/"
  - "src/spatial/util/"
file_count: 93
date: 2026-04-21
verified:
  - 2026-04-21
---

## 1. Purpose

This coverage note is a heterogeneous catch-all bundle covering ten directories that together form the analytical and runtime-support backbone of Spatial outside the core IR, transforms, and codegen paths.

- **`poly/`** provides the polyhedral model used for affine memory-access analysis. It defines sparse-vector / sparse-matrix / constraint-matrix data structures for affine address expressions and drives an out-of-process ISL "emptiness" checker (C binary compiled from `emptiness.c` and linked against libisl). Downstream banking analysis uses it to decide whether two access index expressions can overlap.
- **`models/`** is the shared cost-model library. It defines `Model[T,F]` (a schema-plus-entries abstraction used uniformly for area and latency), `LinearModel` (affine expressions in named variables), area/latency field schemas, `CongestionModel` (lattice-regression DRAM-contention estimator) and the large DSE-time `RuntimeModel` runtime used inside the generated `model_dse.scala` jar.
- **`src/spatial/dse/`** implements design-space exploration. It discovers tunable parameters (tile sizes, par factors, outer-loop pipeline toggles), enumerates/samples the legal space, farms work out to worker threads that each run a light-weight scalar/memory/area/cycle analysis per point, and supports three modes: brute force, heuristic, HyperMapper (Bayesian optimizer via a Python subprocess).
- **`src/spatial/lib/`** hosts the user-facing *standard library*: staged BLAS, linear algebra, ML primitives, scan/filter, sort (mergeSort), low-precision conversion, and a meta-programming helper. These are DSL-level templates that users call in application code.
- **`src/spatial/executor/`** is the pure-Scala software simulator for the banked IR. `ExecutorPass` can be inserted mid-pipeline to interpret the `Accel` block cycle-by-cycle using `ControlExecutor`, `ExecPipeline`, `MemoryController`, and the resolver trait family — without doing chisel simulation.
- **`src/spatial/model/`** contains `RuntimeModelGenerator`, a codegen-style pass that writes `model_$version.scala`. This generated file, when compiled, instantiates the `models.RuntimeModel` API (`ControllerModel`, `CtrModel`, `CChainModel`) to symbolically execute the control hierarchy and report total cycles for a given set of tuneable bindings.
- **`src/spatial/math/`** is a tiny (one file) DSL-level math helper exposing `LinearAlgebra.transpose` and `LinearAlgebra.gemm` that stage `Blackbox.GEMM` calls.
- **`src/spatial/issues/`** defines four `Issue` subclasses that the checks passes raise: ambiguous metapipes, control/primitive mixing, potential buffer hazard, and unbankable groups.
- **`src/spatial/report/`** generates the two human-readable text reports Spatial emits: `Memories.report` (per-memory banking/area summary) and `Retime.report` (per-symbol latency/delay-line summary).
- **`src/spatial/util/`** is miscellaneous helper code: `spatial.util.modeling` is the single largest file (992 LOC) and is the *cycle/latency/II accountant* consumed by retiming, area, and DSE; plus the small staged helpers `math`, `memops`, `TransformUtils`, `VecStructType`, `IntLike`, `ParamLoader`, and `debug`.

## 2. File inventory

### `poly/src/poly/` — polyhedral model (8 files)

| path | purpose |
|---|---|
| `spatial/poly/src/poly/ISL.scala:13-175` | `trait ISL` — lazy-compiles `$HOME/bin/emptiness`, sends matrix to subprocess, `isEmpty` / `overlapsAddress` / `intersects` / `isSuperset` queries |
| `spatial/poly/src/poly/SparseVector.scala:15-66` | `SparseVector[K]` — coefficients of affine expr `a_1*k_1 + … + c`; `asMinConstraint`, `asMaxConstraint`, `span` (compute residual bank-access set) |
| `spatial/poly/src/poly/SparseVectorLike.scala:3-14` | shared accessor surface for vectors and constraints |
| `spatial/poly/src/poly/SparseConstraint.scala:13-26` | `SparseConstraint[K]` — vector plus `ConstraintType` (`>=0` / `==0`) |
| `spatial/poly/src/poly/SparseMatrix.scala:5-88` | `SparseMatrix[K]` — rows of `SparseVector`; `replaceKeys`, `expand`, `asConstraintGeqZero`, arithmetic |
| `spatial/poly/src/poly/ConstraintMatrix.scala:5-54` | set of constraints, with `domain` / `andDomain`, `toDenseString` for ISL emptiness protocol |
| `spatial/poly/src/poly/ConstraintType.scala:3-7` | enum `GEQ_ZERO = 1`, `EQL_ZERO = 0` (toInt used as first column of dense wire format) |
| `spatial/poly/src/poly/DenseMatrix.scala:3-5` | row/col dense int representation used in wire serialization |

### `models/src/models/` — shared cost models (13 files)

| path | purpose |
|---|---|
| `spatial/models/src/models/Model.scala:5-78` | `Model[T,F]` — named model with params and field entries |
| `spatial/models/src/models/Fields.scala:5-17` | `Fields`, `AreaFields[T]`, `LatencyFields[T]` schemas |
| `spatial/models/src/models/package.scala:3-85` | `type Area`, `type Latency`, `type NodeModel`, `NodeModelOps.eval`, `DoubleModelOps.cleanup`, `LinearModelAreaOps.++ / -- / apply / eval` |
| `spatial/models/src/models/LinearModel.scala:6-114` | `Prod(a, xs)`, `LinearModel` with `eval`, `partial`, `fractional`, `cleanup`, `fromString` |
| `spatial/models/src/models/AffArith.scala:3-23` | `AffArith[T]` type-class for Double and LinearModel |
| `spatial/models/src/models/AreaEstimator.scala:10-263` | loads PMML area models via `jpmml-evaluator`; `crudeEstimateMem` (rule-based fallback) |
| `spatial/models/src/models/CongestionModel.scala:10-124` | lattice-regression DRAM-contention model |
| `spatial/models/src/models/DenseLoadParams.scala`, `DenseStoreParams.scala`, `GatedDenseStoreParams.scala` | 3 giant hard-coded coefficient tables for the three transfer schedules |
| `spatial/models/src/models/ModelData.scala:3-74` | dispatcher selecting which `*Params` to read given a schedule string |
| `spatial/models/src/models/RuntimeModel.scala:9-405` | `object Runtime` — `CtrlSchedule`, `Ctx`, `Tuneable`, `Locked`, `Ask`, `Branch`, `CtrModel`, `CChainModel`, `ControllerModel` (core cycle-count equation `cycsPerParent`) |
| `spatial/models/src/models/Sensitivity.scala:5-90` | CSV post-processor for DSE outputs |

### `src/spatial/dse/` — design space exploration (18 files)

| path | purpose |
|---|---|
| `spatial/src/spatial/dse/DSEMode.scala:3-10` | `sealed abstract class DSEMode` — `Disabled`, `Heuristic`, `Bruteforce`, `HyperMapper`, `Experiment` |
| `spatial/src/spatial/dse/DSERequest.scala:3` | 1-line request wrapper |
| `spatial/src/spatial/dse/DesignPoint.scala:14-30` | `PointIndex(pt: BigInt)` (brute-force enumeration) and `Point(params)` (explicit assignments) |
| `spatial/src/spatial/dse/SpaceGenerator.scala:11-80` | `createIntSpace` (tile/par), `createCtrlSpace` (bool toggles); wraps each `Sym` param in a `Domain[_]` |
| `spatial/src/spatial/dse/ParameterAnalyzer.scala:12-194` | walks program, calls `TileSizes += p`, `ParParams += p`, `PipelineParams += lhs`, emits `Restrict` rules |
| `spatial/src/spatial/dse/ScalarAnalyzer.scala:17-140` | propagates bounds / global-ness |
| `spatial/src/spatial/dse/ContentionAnalyzer.scala:18-82` | per-symbol DRAM contention counter; dead-coded in current `DSEAnalyzer` but retained |
| `spatial/src/spatial/dse/LatencyAnalyzer.scala:10-64` | launches the compiled runtime-model jar as a subprocess, reads back `Total Cycles for App` |
| `spatial/src/spatial/dse/DSEAreaAnalyzer.scala:15-246` | AccelTraversal that aggregates per-symbol `Area`; handles reduction-tree area, delay-line area, cycle area |
| `spatial/src/spatial/dse/PruneWorker.scala:11-30` | one-shot runnable: enumerate a slice of indices, filter by single-param restrictions |
| `spatial/src/spatial/dse/DSEThread.scala:12-153` | per-worker runnable: takes batches, resets IR errors, runs area analyzer, returns CSV lines |
| `spatial/src/spatial/dse/DSEWriterThread.scala:6-53` | consumer thread that flushes result rows to `config.name + "_data.csv"` |
| `spatial/src/spatial/dse/DSEAnalyzer.scala:23-486` | top-level pass; `process` chooses mode; `threadBasedDSE` wires work/file queues and a thread pool |
| `spatial/src/spatial/dse/HyperMapperDSE.scala:12-202` | `trait HyperMapperDSE` — emits JSON config, spawns HyperMapper Python subprocess |
| `spatial/src/spatial/dse/HyperMapperReceiver.scala:14-122` | reads lines from HyperMapper stdout, parses header, enqueues `DesignPoint` batches |
| `spatial/src/spatial/dse/HyperMapperSender.scala:6-69` | writes per-request CSVs back to HyperMapper over stdin |
| `spatial/src/spatial/dse/HyperMapperThread.scala:1-148` | entirely commented out — vestigial, currently unused |
| `spatial/src/spatial/dse/Subproc.scala:9-77` | generic bidirectional subprocess wrapper |

### `src/spatial/lib/` — DSL standard library (9 files)

| path | purpose |
|---|---|
| `spatial/src/spatial/lib/package.scala:1-7` | `package object lib extends LinearAlgebra with LowPrecision with Scan` |
| `spatial/src/spatial/lib/BLAS.scala:6-212` | staged `Dot`, `Axpy`, `Gemv`, (etc.) |
| `spatial/src/spatial/lib/LinearAlgebra.scala:7-430` | `matmult`, `gemm` (scalar / vector / matrix broadcast via `BoxedC`) |
| `spatial/src/spatial/lib/LowPrecision.scala:6-329` | `ConvertTo8Bit`, quantization kernels |
| `spatial/src/spatial/lib/Scan.scala:6-40` | staged `filter`, `filter_fifo` |
| `spatial/src/spatial/lib/Sort.scala:6-137` | `mergeSort` using `MergeBuffer` primitive |
| `spatial/src/spatial/lib/ML.scala:11-305` | staged `dp_flat`, `dp_tiled`, `sum_flat`, `sum_tiled`, `denselayer` |
| `spatial/src/spatial/lib/HostML.scala:6-187` | unstaged Scala reference implementations (`unstaged_dp`, `unstaged_denselayer`) |
| `spatial/src/spatial/lib/MetaProgramming.scala:9-120` | `withEns` rewriter — auto-injects enable bits into accessors in a scope |

### `src/spatial/executor/scala/` — Scala cycle simulator (24 files total)

| path | purpose |
|---|---|
| `spatial/src/spatial/executor/scala/ExecutorPass.scala:10-106` | `case class ExecutorPass` (pass; invoked from `Spatial.scala:129`), drives per-`AccelScope` cycle loop |
| `spatial/src/spatial/executor/scala/ExecutionState.scala:50-107` | `MemTracker`, `CycleTracker`, `class ExecutionState` (values map + IR + memory controller) |
| `spatial/src/spatial/executor/scala/OpExecutorBase.scala:3-20` | sealed `Status`; trait `OpExecutorBase` — `tick`, `status`, `print` |
| `spatial/src/spatial/executor/scala/ControlExecutor.scala:16-1069` | factory `ControlExecutor.apply` dispatching by op/schedule; concrete executors for all controller types |
| `spatial/src/spatial/executor/scala/ExecPipeline.scala:12-323` | pipeline stage abstraction |
| `spatial/src/spatial/executor/scala/FringeNodeExecutor.scala:11-169` | DRAM-transfer simulators |
| `spatial/src/spatial/executor/scala/MemoryController.scala:11-64` | request queue with `bytesPerTick`, `responseLatency`, `maxActiveRequests` throttles |
| `spatial/src/spatial/executor/scala/EmulVal.scala:7-24` | `trait EmulResult`, `EmulVal[+VT]`, `SimpleEmulVal`, `EmulUnit`, `EmulPoison` |
| `spatial/src/spatial/executor/scala/SimulationException.scala:3` | 1-line custom exception |
| `spatial/src/spatial/executor/scala/ExecUtils.scala:8-37` | parse/serialize `EmulVal[_]` for File-backed streams |
| `spatial/src/spatial/executor/scala/package.scala:3-5` | `type SomeEmul = F forSome {type F <: EmulResult}` |
| `spatial/src/spatial/executor/scala/resolvers/OpResolver.scala:43-50` | `object OpResolver` mix-in of 11 resolver traits |
| `spatial/src/spatial/executor/scala/resolvers/*Resolver.scala` (11 files) | one per IR node family |
| `spatial/src/spatial/executor/scala/memories/*.scala` (4 files) | simulator memory backing stores (Reg, flat tensor, FIFO, struct) |

### `src/spatial/model/` (1 file)

| path | purpose |
|---|---|
| `spatial/src/spatial/model/RuntimeModelGenerator.scala:18-422` | `case class RuntimeModelGenerator extends FileDependencies with ControlModels` — emits `model_$version.scala` |

### `src/spatial/math/` (1 file)

| path | purpose |
|---|---|
| `spatial/src/spatial/math/LinearAlgebra.scala:6-…` | `transpose`, `gemm` — stage `Blackbox.GEMM` calls |

### `src/spatial/issues/` (4 files)

| path | purpose |
|---|---|
| `spatial/src/spatial/issues/AmbiguousMetaPipes.scala:7-43` | raised from banking when one mem is referenced by multiple metapipes |
| `spatial/src/spatial/issues/ControlPrimitiveMix.scala:6-15` | raised when an outer control body mixes control and primitive stmts |
| `spatial/src/spatial/issues/PotentialBufferHazard.scala:7-27` | read-before-write buffer hazard warning |
| `spatial/src/spatial/issues/UnbankableGroup.scala:7-20` | raised from `MemoryConfigurer` when no banking scheme satisfies all `AccessMatrix`es |

### `src/spatial/report/` (2 files)

| path | purpose |
|---|---|
| `spatial/src/spatial/report/MemoryReporter.scala:13-108` | Pass gated by `config.enInfo`, writes `Memories.report` |
| `spatial/src/spatial/report/RetimeReporter.scala:10-66` | AccelTraversal gated by `config.enInfo && spatialConfig.enableRetiming`; writes `Retime.report` |

### `src/spatial/util/` (10 files)

| path | purpose |
|---|---|
| `spatial/src/spatial/util/package.scala:7-90` | `spatialConfig(state)` accessor, `canMotionFromConditional`, `reductionTreeDelays`, `crossJoin`, `roundUpToPow2`, `computeShifts`, `oneAndOthers` |
| `spatial/src/spatial/util/modeling.scala:26-992` | **the big one**: `mutatingBounds`, `consumersDfs/Bfs`, `getAllNodesBetween`, `areaModel`, `latencyOf`, `latencyOfPipe`, `latenciesAndCycles`, `findAccumCycles`, `pipeLatencies` |
| `spatial/src/spatial/util/math.scala:17-…` | `selectMod`, `constMod`, `staticMod` (mod-of-pow2 rewrites) |
| `spatial/src/spatial/util/memops.scala:18-…` | `AliasOps` enrichment: `sparseStarts/Steps/Ends/Pars/Lens/Origins`, `rawStarts`, `rawDims` |
| `spatial/src/spatial/util/IntLike.scala:8-107` | type-class `IntLike[A]` for `Int`, `I32`, `Idx` |
| `spatial/src/spatial/util/ParamLoader.scala:13-90` | `loadParam`, `loadParams(path)` — typesafe-config based param file loader |
| `spatial/src/spatial/util/TransformUtils.scala:14-…` | `isFirstIter`, `isLastIter`, `isFirstIters`, `isLastIters`, `makeIter(s)` helpers |
| `spatial/src/spatial/util/VecStructType.scala:11-…` | general-purpose Bits-packed struct type builder |
| `spatial/src/spatial/util/debug.scala:7-14` | `tagValue` — stage a `Reg[T]` with `dontTouch` for debug observation |

## 3. Key types / traits / objects

- **`poly.ISL`**: self-initializing trait managed as a state-held singleton. Key methods: `isEmpty(constraints)` / `nonEmpty`, `overlapsAddress(a,b)`, `domain[K](key)` (abstract — instantiator provides domain-per-iterator).
- **`poly.SparseMatrix[K]`, `SparseVector[K]`, `SparseConstraint[K]`, `ConstraintMatrix[K]`**: the affine-algebra algebra that banking uses. `SparseVector.span(N, B)` computes residual bank-access sets via `gcd` and `allLoops`.
- **`models.Model[T,F[A]<:Fields[A,F]]`**: parametric cost carrier; methods `+`, `-`, `*`, `/`, `<`, `<=` lift `AffArith[T]` / `Numeric[T]`. Implementations: `Area = Model[Double, AreaFields]`, `Latency = Model[Double, LatencyFields]`, `NodeArea = Model[NodeModel, AreaFields]`.
- **`models.AreaEstimator`**: PMML-backed ML area prediction for memories; `startup`, `shutdown`, `crudeEstimateMem` fallback.
- **`models.Runtime`**: the *runtime* library linked into the generated DSE model jar. Key types inside: `ControllerModel(id, level, schedule, cchain, L, II, ctx, bitsPerCycle)`, `CtrModel`, `CChainModel`, plus `Tuneable[V]`, `Locked`, `Ask`, `Branch`. `ControllerModel.cycsPerParent` is *the* cycle equation.
- **`models.CongestionModel`**: `evaluate(RawFeatureVec, CtrlSchedule): Int` calibrates then hypercube-interpolates across a 6-D {loads, stores, gateds, outerIters, innerIters, bitsPerCycle} lattice.
- **`spatial.dse.DSEAnalyzer`**: the pass object itself; entry is `process[R]` which dispatches over `spatialConfig.dseMode`. Uses `SpaceGenerator` and `HyperMapperDSE` mixins.
- **`spatial.dse.Domain[T]`** — lives in `spatial.metadata.params` but is central here.
- **`spatial.executor.scala.ControlExecutor`** and subclasses (22+ specializations in the same file) implement per-op `tick()`.
- **`spatial.executor.scala.resolvers.OpResolverBase`**: `run[U,V](sym, execState): EmulResult` — the dispatch-by-Op pattern match.
- **`spatial.model.RuntimeModelGenerator`**: extends `argon.codegen.FileDependencies`, emits Scala source that references `models.Runtime.*`.
- **`spatial.util.modeling`** object — `latencyOf(sym)`, `latencyOfPipe(block)`, `latenciesAndCycles(block)`, `findAccumCycles(schedule)`; reused by `RetimingAnalyzer`, `InitiationAnalyzer`, `AreaAnalyzer`, `DSEAreaAnalyzer`, `RetimeReporter`, `MemoryReporter`.
- **Issue case classes** (four of them) — each extends `argon.Issue` and overrides `onUnresolved(traversal: String): Unit`.

## 4. Entry points

- **ISL** is obtained implicitly and consumed inside `traversal/banking/*`.
- **`AreaEstimator`** is created once in `Spatial.scala` and threaded into `ResourceReporter`, `MemoryReporter`, and all `AreaModel` subclasses in `src/spatial/targets/*`.
- **`DSEAnalyzer`** is instantiated at `Spatial.scala:92` and gated by `spatialConfig.enableArchDSE`.
- **`ParameterAnalyzer`** runs before DSE.
- **`ExecutorPass`** is inserted at `Spatial.scala:207` gated by `spatialConfig.enableScalaExec`.
- **`MemoryReporter`** at `Spatial.scala:237`; **`RetimeReporter`** at `Spatial.scala:229`.
- **`RuntimeModelGenerator`** runs twice: `dseRuntimeModelGen` (pre-DSE) and `finalRuntimeModelGen` (post-retiming).
- **`spatial.lib.*`** is consumed by user apps only, not compile-pipeline.
- **`spatial.math.LinearAlgebra`** similarly is user-facing glue for `Blackbox.GEMM`.
- **Issues** are raised by `MemoryConfigurer`, `FIFOConfigurer`, and `metadata.control.package`.
- **`spatial.util.modeling`** is imported almost universally by analyses, transforms, reports, and DSE.

## 5. Dependencies

**Upstream (what this bundle uses from elsewhere):**

- `argon.*` (IR), `argon.passes.Traversal`, `argon.codegen.FileDependencies`, `argon.Issue`, `argon.node.*`.
- `emul.*` (for `FixedPoint`, `FloatPoint`, `Bool`, `ResidualGenerator`).
- `utils.process.BackgroundProcess` (used by `poly.ISL`, `HyperMapperDSE`, `Subproc`).
- `utils.implicits.collections`, `utils.math` (gcd, allLoops, log2).
- `utils.io.files._`.
- `spatial.node.*` (IR op definitions) and `spatial.metadata.*` (memory, params, control, access, retiming, types, bounds, transform, debug).
- `spatial.lang.*`, `spatial.dsl._`, `spatial.libdsl._`, `spatial.rewrites._` (for lib and math).
- `spatial.SpatialConfig`, `spatial.traversal.*`, `spatial.targets.*`.
- `models.*` (this bundle's own `models/`) is depended upon by every `spatial.dse.*`, `spatial.model.RuntimeModelGenerator`, `spatial.report.MemoryReporter`, `spatial.targets.*AreaModel`.
- `poly.*` depended upon by `spatial.dse.DSEAnalyzer`, `DSEThread`, `HyperMapperThread`, plus `spatial.traversal.banking.*`.
- External: `org.jpmml-evaluator` (AreaEstimator), `com.typesafe.config` (ParamLoader), Python + HyperMapper on `$PATH` (HyperMapperDSE), `gcc + libisl` (ISL setup).

**Downstream (what else uses this bundle):**

- `poly/` is used by `spatial.traversal.banking.MemoryConfigurer`, `FIFOConfigurer`, `MemoryAnalyzer`, `MemoryAllocator`.
- `models/` is used by the entire target-specific area/latency model tree under `spatial.targets.*`, plus by `ResourceReporter`, `MemoryReporter`, and the `Spatial.scala` main pipeline.
- `spatial.dse.*` is a leaf: only `Spatial.scala` instantiates `DSEAnalyzer` and `ParameterAnalyzer`.
- `spatial.executor.*` has just one user: `Spatial.scala`.
- `spatial.model.RuntimeModelGenerator` has just one user: `Spatial.scala`.
- `spatial.report.*` has just one user: `Spatial.scala`.
- `spatial.issues.*` types are constructed from banking/checks (outside this bundle) and their `onUnresolved` method is invoked by `argon.State.report` machinery.
- `spatial.util.modeling` is the most referenced subsystem member — imported by analyses, transforms, codegen/resourcegen, and reports.
- `spatial.lib.*` and `spatial.math.*` are user-facing: they have no consumers inside the compiler.

## 6. Key algorithms

- **Out-of-process ISL emptiness dispatch** — `spatial/poly/src/poly/ISL.scala:46-153`: file-locked compile of `emptiness.c` then send/recv loop to the `$HOME/bin/emptiness` subprocess (one char '0'/'1' per query).
- **Residual bank-set computation** — `spatial/poly/src/poly/SparseVector.scala:54-64`: affine coefficients → per-bank reachable residuals via `gcd`, `allLoops`, and `N*B/gcd(N, posV)`.
- **Dense string protocol** — `spatial/poly/src/poly/ConstraintMatrix.scala:30-34`: line format consumed by the C subprocess.
- **Lattice-regression congestion** — `spatial/models/src/models/CongestionModel.scala:54-113`: 1-D piecewise-linear calibration per feature, then 6-D hypercube interpolation on a lattice of 3^6=729 parameters.
- **Controller cycle equation** — `spatial/models/src/models/RuntimeModel.scala:313-338`: `cycsPerParent` per (CtrlLevel × CtrlSchedule); 11 cases covering Sequenced, Pipelined, Streaming, ForkJoin, Fork, DenseLoad, DenseStore, GatedDenseStore, SparseLoad, SparseStore.
- **Area summation with delay lines** — `spatial/src/spatial/dse/DSEAreaAnalyzer.scala:71-107`: per-block critical-path delay-line area.
- **Reduction-tree area** — `DSEAreaAnalyzer.scala:164-180`: L-1 reduction units for L map-lane leaves, plus tree delay-lines computed by `util.reductionTreeDelays(nLeaves)`.
- **Heuristic DSE sampling pipeline** — `DSEAnalyzer.scala:149-283`: (1) prune singleton-param restrictions; (2) parallel `PruneWorker` enumeration of legal points; (3) shuffle to 75k; (4) feed workers over a `LinkedBlockingQueue[Seq[DesignPoint]]`.
- **HyperMapper client-server loop** — JSON config emit → Python subprocess → line-based request/response over buffered pipes.
- **Pipe latency and cycle identification** — `util/modeling.scala:101-199`: `latencyAndInterval`, `latenciesAndCycles`, `findAccumCycles`, `getAllNodesBetween`, `brokenByRetimeGate`.
- **Cycle-level scala simulation** — `executor/scala/ControlExecutor.scala:16-…`: factory-dispatched per-schedule executor with `tick()` progressing iteration and pipeline state.
- **DRAM request modeling** — `executor/scala/MemoryController.scala:37-…`: `activeRequests`/`backlog` throttle with `bytesPerTick` drain.
- **Generated runtime model** — `RuntimeModelGenerator.scala:300-400`: `visit` per control op emits a `new ControllerModel(...)` plus child registrations.

## 7. Invariants / IR state read or written

- `poly/` is IR-agnostic except through the `K` type-parameter supplied by callers.
- `models.*` is IR-agnostic.
- `DSE` reads param metadata: `p.paramDomain`, `p.name`, `p.setIntValue`, `p.intValue`, `p.ctx`. Consumes `TileSizes`, `ParParams`, `PipelineParams`, `Restrictions`, `TopCtrl`, `LocalMemories`, and `IgnoreParams` from `spatial.metadata.params`. Writes final param values via `makeFinal` / `makeFinalSched`.
- `DSEAreaAnalyzer` reads `latencyOf`, `isRerun`, `scopeArea`; writes `scopeArea`, `savedArea`, `totalArea`.
- `ExecutorPass` reads `IR.runtimeArgs`, `IR.config.genDir`; writes nothing to IR — only to `ExecutionState`.
- `RuntimeModelGenerator` reads `bodyLatency`, `II`, `rawSchedule`, `level`, `children`, `loweredTransfer`, `loweredTransferSize`.
- `MemoryReporter` reads `duplicates`, `readers`, `writers`, `ports`, `dispatches`, `resource`, `isCtrlBlackbox`; writes the `Memories.report` file.
- `RetimeReporter` reads `isInCycle`, `getReduceCycle`, `latencyModel.requiresRegisters`, `builtInLatencyOfNode`, consumers/delays.
- `util.modeling.findAccumCycles` reads `AccessMatrix`, `Reader`/`Writer`/`BankedReader`/`BankedWriter` patterns, `nonConflictSet`, `isArgIn`, `isLockSRAM`, `isRetimeGate`.

## 8. Notable complexities or surprises

- **`poly.ISL` is a process-level singleton with file locking.** The `lazy val proc` block owns `$HOME/bin/emptiness.lock` across *JVM* boundaries. TODO comments reveal `isSuperset` and `intersects` are currently stubs (`return false` / `return true`).
- **`DSEAnalyzer.compileLatencyModel` shells out `bash scripts/assemble.sh`** at compile time. The "SO DIRTY" comment nearby acknowledges this.
- **`HyperMapperThread.scala` is entirely commented out.** All 148 lines are `//`-prefixed.
- **`ContentionAnalyzer` is dead-coded in `DSEThread`.** `contentionAnalyzer.init() / run()` calls are all commented out.
- **Area estimator Python pre-check is commented out.** The whole thing is gated away. `useML` is effectively always `true`.
- **`RuntimeModel` uses interactive console input by default.** `AskBase.lookup` falls back to `scala.io.StdIn.readLine` if `interactive=true`.
- **`CongestionModel.evaluate` hard-clamps the result to `170 max result.toInt`** with TODO "Model is naughty if it returns <170".
- **`CongestionModel.lazy val params` are sensitive to `model: String` var assignment order.**
- **`ControlExecutor.scala` is 1069 lines of inline classes.**
- **`OpResolver` trait mix-in order matters.** `DisabledResolver` is listed first after `OpResolverBase` "This way it runs (almost) last" — because `trait` linearization inverts perceived order.
- **`RuntimeModelGenerator.quote` has dead code but always takes the tuneable branch.**
- **`AreaEstimator.crudeEstimateMem` rule-based penalty constants** (mulCost=6, divCost=20, modCost=20, muxCost=6) are magic numbers.
- **`DSEAreaAnalyzer.pipeDelayLineArea`** contains an explicit 30-line imperative rewrite "(it's a groupByReduce! plus a map, plus a reduce)" commented above it.
- **`Sensitivity.around` (referenced `DSEAnalyzer.scala:438`) is not in the visible `Sensitivity.scala:5-90` range.**
- **`ExecutorPass` executes for every runtime-arg config.**
- **`MetaProgramming.withEns` mutates `IR.rewrites` globally** using a mutable rewrite rule added via `IR.rewrites.addGlobal`.
- **Hard-coded coefficient tables.** `DenseLoadParams.scala` alone is a single ~700-element `Seq(-2218.05, …)` literal.
- **Issues contain formatting side-effects that use state-held `argon` mutable context.** `onUnresolved` calls `error(...)` which both prints and increments `state.hadErrors`.

## 9. Open questions

- What is the precise guarantee provided by `ISL.overlapsAddress` vs. `intersects` vs. `isSuperset`? Only `overlapsAddress` is implemented; the other two are stubs. How does banking tolerate this?
- Are the `SparseVector.allIters` metadata kept consistent across transforms?
- The relationship between **`models.Area`** (this bundle) and **`spatial.targets.*.AreaModel`** (another bundle): is `AreaModel.areaOf(sym, …)` the only caller that produces `Model[Double, AreaFields]`?
- How does `DSEAreaAnalyzer` reuse banking results between points?
- Is the `ExecutorPass` known to diverge on any op family?
- How does `RuntimeModelGenerator` reconcile with `RetimingAnalyzer`? It runs **twice** (pre-DSE and post-retiming).
- Is there a conceptual layering: are `spatial.util.modeling` primitives the canonical source that `models.LinearModel` evaluations are *fit* to?
- What is the relationship between `spatial.math.LinearAlgebra` and `spatial.lib.LinearAlgebra`?
- How is `Sensitivity.around` used by DSE?
- Is the HyperMapper integration still exercised in practice?
- Why does `PotentialBufferHazard` warn rather than erroring unambiguously?
- Why does `ISL.nonEmpty` run through `isEmpty` (double negation) rather than having an independent fast-path?
- What is the status of the Serializable IR attempt (`DSEAnalyzer.scala:33-57`) — abandoned, or deferred?

## 10. Suggested spec sections

Splitting by logical subsystem, this bundle's content should feed approximately the following leaves of `10 - Spec/`:

- **poly/** → `10 - Spec/04 - Analyses/Polyhedral Model.md`. Key content: the sparse-matrix algebra, ISL out-of-process protocol, `overlapsAddress` semantics, residual-set computation, `ConstraintType` wire format.
- **models/** → `10 - Spec/08 - Models/`:
  - `10 - Spec/08 - Models/Area Model.md` — `Model[T,F]`, `AreaFields`, `AreaEstimator` + `crudeEstimateMem` fallback.
  - `10 - Spec/08 - Models/Latency Model.md` — `LatencyFields`, `NodeModel`, `LinearModel`.
  - `10 - Spec/08 - Models/Congestion Model.md` — lattice regression and calibration.
  - `10 - Spec/08 - Models/Runtime Model.md` — `ControllerModel.cycsPerParent` cycle equation.
- **src/spatial/dse/** → `10 - Spec/09 - Design Space Exploration/`:
  - `Overview.md` — `DSEMode`, pipeline integration, parameter discovery via `ParameterAnalyzer`.
  - `Space Generation.md` — `SpaceGenerator`, `Domain`, pruning.
  - `Heuristic DSE.md` — `heuristicDSE` flow with `PruneWorker` and shuffled sampling.
  - `Brute Force DSE.md`.
  - `HyperMapper Integration.md` — `HyperMapperDSE` + `HyperMapperSender/Receiver` + JSON config.
  - `Worker Architecture.md` — `DSEThread`, `DSEWriterThread`, `LatencyAnalyzer` (jar subprocess), `DSEAreaAnalyzer`.
- **src/spatial/lib/** → `10 - Spec/12 - Standard Library/`:
  - `BLAS.md`, `Linear Algebra.md`, `ML.md`, `Low Precision.md`, `Sort and Scan.md`, `Meta Programming.md`, and a `Host ML.md` for the unstaged reference primitives.
- **src/spatial/executor/** → `10 - Spec/11 - Runtime/Scala Executor.md`:
  - `Overview.md` — `ExecutorPass`, `ExecutionState`, `MemTracker`, `CycleTracker`.
  - `Control Execution.md` — `ControlExecutor` factory + 11 specialized executors.
  - `Pipeline Execution.md` — `ExecPipeline` and `PipelineStage`.
  - `Memory Simulation.md` — `MemoryController`, fringe transfer executors.
  - `Op Resolvers.md` — `OpResolver` trait-mixin design + per-family resolvers.
  - `Emul Values.md` — `EmulVal`, `SimpleEmulVal`, `EmulUnit`, `EmulPoison`.
- **src/spatial/model/** → `10 - Spec/08 - Models/Runtime Model Generator.md`.
- **src/spatial/math/** → fold into `10 - Spec/12 - Standard Library/Linear Algebra.md`.
- **src/spatial/issues/** → `10 - Spec/05 - Diagnostics/Issues.md` listing the four `Issue` subclasses.
- **src/spatial/report/** → `10 - Spec/13 - Reports/`:
  - `Memory Report.md` — what `Memories.report` contains.
  - `Retime Report.md` — what `Retime.report` contains.
- **src/spatial/util/** → `10 - Spec/14 - Utilities/`:
  - `Modeling Utilities.md` — the big `util/modeling` surface (`latencyOf`, `latenciesAndCycles`, `findAccumCycles`, `getAllNodesBetween`).
  - `Math Utilities.md` — `selectMod`, `constMod`, `staticMod`, plus `util.package.scala` helpers.
  - `Transform Utilities.md` — `TransformUtils.makeIter`, `isFirstIter`, etc.
  - `Other Utilities.md` — `IntLike`, `ParamLoader`, `VecStructType`, `debug.tagValue`, `memops`.
