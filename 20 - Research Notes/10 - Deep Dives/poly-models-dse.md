---
type: deep-dive
topic: poly-models-dse
source_files:
  - "spatial/poly/src/poly/ISL.scala"
  - "spatial/poly/src/poly/SparseVector.scala"
  - "spatial/poly/src/poly/SparseVectorLike.scala"
  - "spatial/poly/src/poly/SparseConstraint.scala"
  - "spatial/poly/src/poly/SparseMatrix.scala"
  - "spatial/poly/src/poly/ConstraintMatrix.scala"
  - "spatial/poly/src/poly/ConstraintType.scala"
  - "spatial/poly/src/poly/DenseMatrix.scala"
  - "spatial/models/src/models/Model.scala"
  - "spatial/models/src/models/Fields.scala"
  - "spatial/models/src/models/package.scala"
  - "spatial/models/src/models/LinearModel.scala"
  - "spatial/models/src/models/AffArith.scala"
  - "spatial/models/src/models/AreaEstimator.scala"
  - "spatial/models/src/models/CongestionModel.scala"
  - "spatial/models/src/models/RuntimeModel.scala"
  - "spatial/models/src/models/ModelData.scala"
  - "spatial/models/src/models/DenseLoadParams.scala"
  - "spatial/models/src/models/DenseStoreParams.scala"
  - "spatial/models/src/models/GatedDenseStoreParams.scala"
  - "spatial/models/src/models/Sensitivity.scala"
  - "spatial/src/spatial/targets/SpatialModel.scala"
  - "spatial/src/spatial/targets/AreaModel.scala"
  - "spatial/src/spatial/targets/LatencyModel.scala"
  - "spatial/src/spatial/targets/NodeParams.scala"
  - "spatial/src/spatial/targets/HardwareTarget.scala"
  - "spatial/src/spatial/targets/generic/GenericLatencyModel.scala"
  - "spatial/src/spatial/targets/generic/TileLoadModel.scala"
  - "spatial/src/spatial/dse/DSEMode.scala"
  - "spatial/src/spatial/dse/DSERequest.scala"
  - "spatial/src/spatial/dse/DesignPoint.scala"
  - "spatial/src/spatial/dse/SpaceGenerator.scala"
  - "spatial/src/spatial/dse/ParameterAnalyzer.scala"
  - "spatial/src/spatial/dse/ScalarAnalyzer.scala"
  - "spatial/src/spatial/dse/ContentionAnalyzer.scala"
  - "spatial/src/spatial/dse/DSEAreaAnalyzer.scala"
  - "spatial/src/spatial/dse/LatencyAnalyzer.scala"
  - "spatial/src/spatial/dse/PruneWorker.scala"
  - "spatial/src/spatial/dse/DSEThread.scala"
  - "spatial/src/spatial/dse/DSEWriterThread.scala"
  - "spatial/src/spatial/dse/DSEAnalyzer.scala"
  - "spatial/src/spatial/dse/HyperMapperDSE.scala"
  - "spatial/src/spatial/dse/HyperMapperReceiver.scala"
  - "spatial/src/spatial/dse/HyperMapperSender.scala"
  - "spatial/src/spatial/dse/Subproc.scala"
  - "spatial/src/spatial/metadata/access/AffineData.scala"
  - "spatial/src/spatial/metadata/access/AccessPatterns.scala"
  - "spatial/src/spatial/metadata/params/DSEData.scala"
  - "spatial/src/spatial/metadata/memory/BankingData.scala"
  - "spatial/utils/src/utils/math/package.scala"
session: 2026-04-23
status: ready-to-distill
feeds_spec:
  - "[[10 - ISL Binding]]"
  - "[[20 - Access Algebra]]"
  - "[[30 - Banking Math]]"
  - "[[10 - Area Model]]"
  - "[[20 - Latency Model]]"
  - "[[40 - Design Space Exploration]]"
---

# Polyhedral Model + Area/Latency Models + DSE Engine — Deep Dive

## Reading log

Read in roughly the following order:

1. `poly/src/poly/ConstraintType.scala:3-7`, `SparseVectorLike.scala:3-14`, `DenseMatrix.scala:3-5` — the three trivial files that define the leaf types.
2. `poly/src/poly/SparseVector.scala:15-65` — `case class SparseVector[K]` for `a_1 k_1 + ... + c`, with `span(N,B)` residual-computation method.
3. `poly/src/poly/SparseConstraint.scala:13-26` — `SparseConstraint[K]` combines vector coefficients with `ConstraintType` and provides the `toDenseString` / `toDenseVector` serialization used by the ISL wire protocol.
4. `poly/src/poly/SparseMatrix.scala:5-88` — `SparseMatrix[K]` with `replaceKeys`, `prependBlankRow`, `sliceDims`, `expand` (Wang modulus enumeration via private `combs`/`allLoops`/`gcd`).
5. `poly/src/poly/ConstraintMatrix.scala:5-54` — `ConstraintMatrix[K]` (set of constraints) with `domain`/`andDomain` and the main `toDenseString`/`toDenseMatrix` serialization.
6. `poly/src/poly/ISL.scala:13-175` — trait `ISL` with lazy `BackgroundProcess` owning the `emptiness` subprocess; `isEmpty`/`overlapsAddress` implemented, `isSuperset`/`intersects` stubbed.
7. `models/src/models/Fields.scala:5-17`, `Model.scala:5-78`, `AffArith.scala:3-23`, `package.scala:3-85` — the `Model[T,F]` + `Fields[T,M]` + `AffArith[T]` triad, and the implicit-ops machinery for `DoubleModelOps`, `LinearModelAreaOps`, `NodeModelOps`.
8. `models/src/models/LinearModel.scala:6-114` — `Prod`/`LinearModel` symbolic affine algebra, `eval`/`partial`/`fractional`/`cleanup`/`fromString`.
9. `models/src/models/AreaEstimator.scala:10-263` — PMML-loaded `estimateMem`/`estimateArithmetic`, rule-based `crudeEstimateMem` fallback (magic constants).
10. `models/src/models/CongestionModel.scala:10-124` — 6-D lattice regression with per-feature PWL calibration; key points & params dispatched via `ModelData`.
11. `models/src/models/RuntimeModel.scala:9-405` — the biggest piece: `Runtime` object plus `ControllerModel`, `CtrModel`, `CChainModel`, the `cycsPerParent` equation (11 cases), plus the `Tuneable`/`Locked`/`Ask`/`Branch` model-value base.
12. `models/src/models/ModelData.scala:3-74`, `DenseLoadParams.scala:3-19`, `DenseStoreParams.scala:3-19`, `GatedDenseStoreParams.scala:3-19` — the three giant coefficient tables and the one-function-per-field dispatcher.
13. `models/src/models/Sensitivity.scala:5-90` — DSE-CSV post-processor; `around(file, params)` computes per-param cycle deltas.
14. `src/spatial/targets/HardwareTarget.scala:7-50` — the abstract target; lazy `areaModel`/`latencyModel` and field definitions.
15. `src/spatial/targets/SpatialModel.scala:11-117` — `abstract class SpatialModel[F]`, the CSV loader, `model(name)(args)`/`model(sym)`, `miss`/`reportMissing`.
16. `src/spatial/targets/AreaModel.scala:15-208` — `AreaModel` subclass; `areaOf`, `areaOfMem`, `areaOfReg`, `rawMemoryArea`, `areaOfDelayLine`, plus the DSP-heuristic case for `FixMul`/`FixDiv`/`FixMod`.
17. `src/spatial/targets/LatencyModel.scala:10-67` — `LatencyModel`: `latencyOfNode`, `builtInLatencyOfNode`, `requiresRegisters`, and the four mode-specific latency models (`parallelModel`, `streamingModel`, `metaPipeModel`, `sequentialModel`) plus `outerControlModel` dispatcher.
18. `src/spatial/targets/NodeParams.scala:16-70` — `nodeParams(s, op)`: the op-to-CSV-key dispatch, with log2-corrected `RegAccumFMA`/`RegAccumOp`, delay-line passthrough, Switch/CounterNew/Control key mapping.
19. `src/spatial/targets/generic/GenericLatencyModel.scala:11-67` — overrides `latencyOfNode` for `DenseTransfer`, with the logistic-overhead tile-transfer formula.
20. `src/spatial/targets/generic/TileLoadModel.scala:16-109` — entirely commented out; `evaluate` returns `0.0`.
21. `src/spatial/dse/DSEMode.scala:3-10`, `DesignPoint.scala:8-30`, `DSERequest.scala:3` — top-level enum/classes.
22. `src/spatial/dse/ParameterAnalyzer.scala:12-194` — walks IR collecting `TileSizes`/`ParParams`/`PipelineParams`/`TopCtrl` and emitting `Restrictions` for each counter shape.
23. `src/spatial/dse/SpaceGenerator.scala:11-80` — `createIntSpace`/`createCtrlSpace`, wraps each parameter `Sym` in a `Domain[_]`.
24. `src/spatial/metadata/params/DSEData.scala:91-219` — the `Domain[T]` class, the `Restrict` hierarchy.
25. `src/spatial/dse/PruneWorker.scala:11-30`, `DSEThread.scala:12-153`, `DSEWriterThread.scala:6-53` — the three runnables executed by the thread pool.
26. `src/spatial/dse/DSEAnalyzer.scala:23-486` — top-level DSE pass, `process[R]` dispatching by mode, `compileLatencyModel` (shells to `bash scripts/assemble.sh`), `heuristicDSE`, `bruteForceDSE`, `threadBasedDSE`.
27. `src/spatial/dse/DSEAreaAnalyzer.scala:15-247` — accelerator-scope traversal, `areaOfBlock`/`areaOfPipe`/`areaOfCycle`, reduction-tree area, delay-line area via `latenciesAndCycles`.
28. `src/spatial/dse/LatencyAnalyzer.scala:10-64` — shells the compiled runtime-model jar for each point batch; reads `Total Cycles for App` lines.
29. `src/spatial/dse/HyperMapperDSE.scala:12-202`, `HyperMapperReceiver.scala:14-122`, `HyperMapperSender.scala:6-69`, `Subproc.scala:9-77` — HyperMapper JSON config emit + Python subprocess + bidirectional pipes.
30. `src/spatial/dse/ContentionAnalyzer.scala:18-82`, `ScalarAnalyzer.scala:17-140` — contention counter (currently dead-coded in `DSEThread`) and bound-propagation analyzer.
31. `utils/src/utils/math/package.scala:1-233` — `computeP` (Wang et al. FPGA '14 corrigendum), `spansAllBanks`, `allLoops`, `hiddenVolume`, `volume`, `modifiedCrandallSW`, `isPow2`, `gcd`, `coprime`, `divisors`, `isMersenne`, `pseudoMersenneC`, `isSumOfPow2`/`asSumOfPow2`, `computeDarkVolume`, `bestPByVolume`, `log2Ceil`/`log2Up`, `nhoods`, `ofsWidth`, `banksWidths`, `elsWidth`.
32. `src/spatial/metadata/access/AffineData.scala:24-132` — `AccessMatrix` sym-paired `SparseMatrix[Idx]`, `overlapsAddress/isSuperset/intersects/isDirectlyBanked/bankMuxWidth/arithmeticNodes`.
33. `src/spatial/metadata/access/AccessPatterns.scala:14-269` — `Prod`/`Sum`/`Modulus`/`AffineComponent`/`AffineProduct`/`AddressPattern` with `getSparseVector` conversion.
34. `src/spatial/metadata/memory/BankingData.scala:540-635` — `NStrictness` / `AlphaStrictness` families; `NBestGuess.factorize` is O(N) per call, and is called O(N) times from `MemoryConfigurer` so overall the banking-enumeration is O(N^2) in memory size.

## Observations

### Polyhedral model

**Out-of-process emptiness checker.** `poly.ISL` holds a `lazy val proc` that compiles `emptiness.c` (loaded via `getClass.getClassLoader.getResourceAsStream("emptiness.c")`) into `$HOME/bin/emptiness` using `${CC ?: gcc} -xc -o ... -` piped with the source and `pkg-config --cflags --libs isl` flags (`ISL.scala:82-103`). It wraps the whole step in an `$HOME/bin/emptiness.lock` `FileLock` so that two concurrent Spatial JVMs do not race to compile; the lock is acquired in a busy `while (lock == null)` spin-loop (`ISL.scala:46-53`). Version mismatch is detected by parsing `emptiness_bin -version` output and comparing against a `float version = X.Y` line in the source (`ISL.scala:65-76`); any mismatch forces a recompile. Inside the JVM the resulting `BackgroundProcess` is a process-level singleton — all `isl` calls from banking go through a single subprocess via `proc.send(matrix)` → `proc.blockOnChar()`. `isEmpty` sends the matrix, reads one char `'0'` or `'1'`; anything else raises `"Failed isEmpty check"` (`ISL.scala:143-153`). Wire format is `ConstraintMatrix.toDenseString` which prints `"$nRows $nCols\n"` followed by one `"$tp $coeffs $mod $c"` line per constraint (`ConstraintMatrix.scala:30-34`; `SparseConstraint.toDenseString` at `SparseConstraint.scala:18`).

**`isSuperset`/`intersects` are TODOs.** At `ISL.scala:165-168` `isSuperset` returns `false`, and at `ISL.scala:171-174` `intersects` returns `true`. Both are flagged `TODO[3)`. Their callers are `AccessMatrix.isSuperset` and `AccessMatrix.intersects` (`AffineData.scala:45-48`). These in turn are called from `spatial.util.modeling` in the "reaching write" analysis — so the reaching-write analysis conservatively treats *every* pair of writes as *possibly* intersecting. This is unsound as an overapproximation of the "precisely statically known" direction and under-approximation of the other, but Spatial appears to tolerate it.

**Residual bank-set computation.** `SparseVector.span(N, B)` at `SparseVector.scala:54-64`: given coefficients `cols.values` and bank count `N`, block size `B`, this computes `P_raw = map(v => val posV = ((v % N) + N) % N; if (posV == 0 && B == 1) 1 else N*B/gcd(N, posV))`, then calls `utils.math.allLoops(P_raw, cols.values, B, Nil)` to enumerate all reachable `(loop × step)` sums, takes `%N`, and returns a `ResidualGenerator`. If all `N` banks are reachable → `ResidualGenerator(1, 0, N)` (stride 1 over all banks). Else if `stepSizeUnderMod(N)` exists → `ResidualGenerator(stepSize, 0, N)`. Else it returns `ResidualGenerator(0, allBanksAccessible, N)` — an explicit-set residual generator. This is the core equation that fingerprints a banking scheme as "touches banks {s, s+k, s+2k, ...} mod N".

**`SparseMatrix.expand`.** `SparseMatrix.scala:56-71`: for each row with a non-zero modulus, compute `a = row.cols.values.filter(_ != 0)`, `p = a.map(x => row.mod / gcd(row.mod, x))`. If `p` contains `row.mod` (degenerate case) → `Seq.tabulate(row.mod){i=>i}`, else recurse through `allLoops(p, a, Nil)` and take `% row.mod`. Each row becomes a list of possible concrete residuals; `combs` then produces every combination → a `Seq[SparseMatrix]` covering all concrete specializations of a modulo-symbolic access. The private `allLoops` here differs slightly from `utils.math.allLoops` — it does not divide by `B`.

**Access-to-sparse-vector conversion.** `AccessPatterns.scala:211-244`: `AddressPattern.getSparseVector` partially evaluates each product. If all multipliers are `isConst` or at least one is, and `ofs` is either const or `ps.forall(_.isSymWithMultiplier)`, it can produce a `SparseVector`; else falls back to `None`. `AddressPattern.toSparseVector(x)` at `247-254` falls all the way back to `SparseVector(Map(x -> 1), 0, ...)` (a fresh bound-var placeholder) — so for non-affine accesses the polyhedral model treats them as a random dimension that can alias anything.

### Cost models

**`Model[T, F[A] <: Fields[A,F]]`.** `Model.scala:5-78`: a `Model` is `name`, `params: Seq[String]`, `entries: Map[String, T]`, with `F[T]` as implicit config providing `fields: Array[String]` and `default: T`. Pointwise arithmetic lifts through `AffArith[T]` (`Model.scala:39-43`); pointwise ordering lifts through `Ordering[T]` (`Model.scala:47-57`) with *two* modes: `<`/`<=` are `zipForall` (every field less), while `>`/`>=` are `zipExists` (any field greater) — the "reversed asymmetry" preserves `!(a < b) == (a >= b)`. `<<`/`>>` reverse these. `AreaFields[T]` and `LatencyFields[T]` are the two instantiations (`Fields.scala:11-17`).

**`NodeModel = Either[LinearModel, Double]`.** `package.scala:4`. The "node model" is either a linear expression (when the CSV entry contains variable names like `32 * b`) or a plain double (when it's a pure number). `NodeModelOps.eval(args)` at `package.scala:30-35` dispatches on the `Either` and clamps to `Math.max(0.0, …)`. `LinearModel.fromString` at `LinearModel.scala:98-113` parses `"a*b*c + d*e + 12"` by splitting on `+`, then each term on `*`, separating numeric parts (`x.toDouble succeeds`) from variable parts. If no variables → `Right(sum of numerics)`; else `Left(LinearModel(prods, vars))`.

**`AreaEstimator`.** `AreaEstimator.scala:10-263`: loads PMML models from `$SPATIAL_HOME/models/resources/<nodetype>_<prop>.pmml` via `jpmml-evaluator`. Caches loaded evaluators in `openedModels: HashMap[(String,String), Evaluator]`, tracks failed `(nodetype,prop)` in `failedModels: Set`. For each query, pads `dims/B/N/alpha/P` to `padsize = {SRAMNew:5, RegFileNew:2, LineBufferNew:2, _:1}`, right-truncates or right-pads `histRaw` to 9 entries (warning if histograms entries with 0 banks but >0 users exist). Response string is parsed by regex `".*result=(-?\d+)\.(\d+).*"` (`AreaEstimator.scala:199`). On any exception → falls back to `crudeEstimateMem` with magic costs `mulCost=6, divCost=20, modCost=20, muxCost=6, volumePenalty=1` (`AreaEstimator.scala:62-66`). The fallback uses access histograms (3-wide groups: `(numBanksTouched, numReaders, numWriters)`) to partition direct vs. xbar banking, then multiplies per-class penalties. Python pre-check code is commented out at `AreaEstimator.scala:18-39`; `useML` defaults to `true` and the `startup` call never demotes it.

**`CongestionModel`.** `CongestionModel.scala:10-124` is a lattice-regression model. Feature dimensions = 6: `loads, stores, gateds, outerIters, innerIters, bitsPerCycle`. Lattice size = `3×3×3×3×3×3 = 729` points, so `params` has 729 doubles per schedule. Workflow: (1) `calibrate_features` applies per-feature piecewise-linear calibration via `calibrate(keypoint_inputs, keypoint_outputs, feature, max_dim)` — if `feature < inputs.head` returns `outputs.head`, if `>= inputs.last` returns `outputs.last`, else interpolates between bracketing keypoints (`CongestionModel.scala:55-66`). (2) `hypercube_features`: compute residual pairs `(x mod 1, 1 - (x mod 1))` per dim, then `CombinationTree` products them → 2^6 = 64 hypervolumes in binary counting order. Hypercube origin is `features.toSeq(x).toInt`. For each corner `c ∈ {0,1}^6`, compute the flat index `sum_i (origin_i + c_i) * product(lattice_size.drop(i+1))`. Weighted sum `hypervolumes dot params[indices]` → interpolated value. (3) `evaluate` sets `model = typ.toString` (which modifies the lazy `params` via `ModelData.params(model)`) then hard-clamps `170 max result.toInt` with a comment "TODO: Model is naughty if it returns <170". **Bug watching**: the `bitsPerCycle` calibration uses `lattice_size(4)` not `lattice_size(5)` (`CongestionModel.scala:76`). This looks like an off-by-one but `lattice_size` is uniformly 3, so the expression still produces the correct max value — just fragile to shape changes.

**`ModelData`.** `ModelData.scala:3-74` dispatches each of the 14 CongestionModel fields on schedule-string (`DenseLoad|DenseStore|GatedDenseStore`) and also hosts `curve_fit(schedule)` that returns 15 hard-coded doubles per schedule used by `ControllerModel.congestionModel` for the production path (lattice regression is commented out at `RuntimeModel.scala:254-260`). The three `*Params` files each contain a single `val params = Seq(…)` of 729 doubles + six `keypoints_inputs` arrays + six `keypoints_outputs` arrays.

**`RuntimeModel.Runtime`.** `RuntimeModel.scala:9-405`. Top-level object with global mutable state: `askMap`, `tuneParams`, `cliParams`, `interactive` flag. `ModelValue[K,V]` hierarchy has `Tuneable[V]`, `Locked`, `Ask`, `Branch` (subclasses of `AskBase`). `AskBase.lookup` falls back to `scala.io.StdIn.readLine` when `interactive = true` (`RuntimeModel.scala:128-137`), which is why the generated DSE model jar supports both batch (`tune` command line args) and REPL modes. `CtrModel[K1,K2,K3,K4]`: 16 apply-arity overloads (one for each subset of which of start/stop/stride/par is a `ModelValue` vs. a plain `Int`) at `RuntimeModel.scala:142-157`; `N` method rounds up via `((stop - start) / stride).ceil rounded up to the nearest par` then divides by par (`RuntimeModel.scala:165-175`). `CChainModel.N` = product of `ctrs.N` (`178-190`); `unroll` = 1 if `isFinal` else product of per-ctr par. `ControllerModel` has `id`, `level` (Inner/Outer), `schedule: Either[CtrlSchedule, Tuneable[String]]`, `cchain: List[CChainModel]`, `L`, `II`, `ctx`, `bitsPerCycle = 32.0`. Constants: `seqSync=1`, `metaSync=1`, `seqAdvance=2`, `dpMask=1`, `startup=2`, `shutdown=1` (`RuntimeModel.scala:207-212`).

**`cycsPerParent` cycle equation.** `RuntimeModel.scala:313-338` — 11 cases, 2 on outer (`OuterControl × {Sequenced, Pipelined, ForkJoin, Streaming, Fork, DenseLoad, DenseStore, GatedDenseStore, SparseLoad, SparseStore}`) × 2 on inner (`InnerControl × {Sequenced, _ ≡ Pipelined}`). Outer/Sequenced with a single-level cchain: `startup + shutdown + sumChildren * cchainIters + seqSync * children.size * cchainIters + cchainIters * seqAdvance`. Outer/Sequenced with a two-level cchain: `(sumChildren + cchain.last.N) * cchain.head.N + ...` (accounts for inner-cchain iterations). Outer/Pipelined single-level: `startup + shutdown + maxChild * (cchainIters - 1) + sumChildren + metaSync * cchainIters * children.size`. Outer/Pipelined two-level: replaces `maxChild` with `(maxChild max cchain.last.N)`. Outer/ForkJoin: `startup + shutdown + maxChild * cchainIters + metaSync`. Outer/Streaming mirrors ForkJoin modulo the cchain-size case. Outer/Fork: asks the user interactively for per-branch duty cycles via `Branch(c.hashCode, s"expected % of the time condition #$i will run (0-100)", ctx)` (`RuntimeModel.scala:325-327`). Outer/DenseLoad/DenseStore/GatedDenseStore: `congestionModel(competitors())`. Outer/SparseLoad/SparseStore: `1` (TODO). Inner/Sequenced: `cchainIters * L + startup + shutdown`. Inner anything else: `(cchainIters - 1) * II + L + startup + shutdown + dpMask`.

**`congestionModel` inside `ControllerModel`.** `RuntimeModel.scala:251-277`: the "production" path uses `ModelData.curve_fit(schedule)` to get 15 coefficients and calls the fitted `fitFunc4` that combines `countersContribution = outerIters * (innerIters + idle)`, `congestionContribution = (loads*a + stores*b + gateds*c) * congestion`, and `parallelizationScale = bitsPerCycle * parFactor` — see the closed-form on `RuntimeModel.scala:265-271`. The result is clamped to `170 + numel/ticksToDeq` as a floor. The lattice-regression path (`CongestionModel.evaluate`) is commented out at `RuntimeModel.scala:253-260`.

### Area and latency models

**`SpatialModel[F]`.** `SpatialModel.scala:11-117`: abstract base for both `AreaModel` and `LatencyModel`. `loadModels` reads either `Source.fromResource("models/" + FILE_NAME)` or `Source.fromFile("$SPATIAL_HOME/models/" + FILE_NAME)`. CSV layout: first row is column headings, with the first `lastIndexWhere(_.startsWith("Param")) + 1` columns as parameter slots, then `FIELDS` columns for the model output. Each subsequent row is `name,<Params>,<Fields>` and entries use `LinearModel.fromString` to parse expressions like `32 * b + 4`. `model(sym, key)` looks up via `nodeParams(sym, op)` (inherited from `NodeParams`) and returns the key-indexed double.

**`AreaModel`.** `AreaModel.scala:15-208`. `FILE_NAME = target.name.replaceAll(" ", "_") + "_Area.csv"`. Core switchboard `areaOfNode(lhs, rhs)` at `161-191`: `Primitive` nodes with `!canAccel` get `NoArea`; `Transient`, `DRAMHostNew`, `DRAMAddress`, `SwitchCase` get `NoArea`; `MemAlloc` routes to `areaOfMem(lhs, name, x.dims.toInt)` with name switch over `SRAMNew | RegFileNew | LineBufferNew | NoImpl`; `DelayLine(size, data)` routes to `areaOfDelayLine(size, nbits(data), 1)`. `FixMul`/`FixDiv`/`FixMod` with both operands non-const or with a non-pow2 const → `Area("DSPs" -> 1)`. `areaOfDelayLine` at `197-205` returns `Area("Regs" -> length * par)` (does not actually use `RegArea` despite computing it; deliberate simplification with the commented-out BRAM-for-long-delays alternative). `areaOfMem` at `60-92` computes a flat banking scheme (`N = max unrolled group`, `B = [1]`, `alpha = P = [1,1,...]`) since the area is called before banking analysis; invokes `mlModel.estimateMem` for LUTs and FFs, hard-codes `ram36 = N.head * ceil(dims.product / (N.head * 36000)) * (depth + 1)` and `ram18 = 0` because "models give wildly large numbers, ram = N should be more realistic for now" (`AreaModel.scala:89`).

**`LatencyModel`.** `LatencyModel.scala:10-67`. `latencyOfNode(s) = model(s, "LatencyOf")`, `latencyInReduce(s) = model(s, "LatencyInReduce")`, `requiresRegisters(s) = spatialConfig.addRetimeRegisters && model(s, "RequiresRegs") > 0`, `builtInLatencyOfNode(s) = model(s, "BuiltInLatency")`. The four overall-block latency functions all follow `stages.{sum|max} * N * ii + stages.sum + latencyOfNode(lhs)` with slight variations:
- `parallelModel: stages.max + latencyOfNode(lhs)`
- `streamingModel: stages.max * (N-1)*ii + latencyOfNode(lhs)`
- `metaPipeModel: stages.max * (N-1)*ii + stages.sum + latencyOfNode(lhs)`
- `sequentialModel: stages.sum * N + latencyOfNode(lhs)`
- `outerControlModel` dispatches among the three based on `lhs.isOuterPipeControl` / `lhs.isSeqLoop`.

**`GenericLatencyModel.latencyOfNode` override.** `GenericLatencyModel.scala:37-66` handles `DenseTransfer` specially: store case (`op.isStore`) uses per-element linear overhead model `overhead = if (p < 8) 1.0 + smallOverhead*p else oFactor*p + (1 - 8*oFactor) + smallOverhead*8` with `oFactor = 0.02*c - 0.019`. Load case calls `memoryModel(c, r, b, p)` (`GenericLatencyModel.scala:20-35`): `overhead12 = 0.307/(1 + exp(-0.096*r + 0.21))` for 96-bit, `0.185/(1 + exp(-0.24*r - 0.8))` for 192-bit, else `0.165`; final `base = ceil((1 + (1/log(12))*log(c))*overhead12 * (110 + r*(53 + cols)))`. Then `parSpeedup = memModel.evaluate(c, r, cols, p)` — and `TileLoadModel.evaluate` just returns `0.0` (entirely commented out). So `memoryModel` always returns zero and the store branch is the only active one. The retuning-network training code in `TileLoadModel.scala:27-101` uses `encog` and is all commented out.

**`NodeParams.nodeParams(s, op)`.** `NodeParams.scala:24-67`. This is the op-to-CSV-name translator. Key cases:
- `RegAccumFMA`: name = `op.name`, params = `[b->nbits, layers->log2(nbits*0.1875 + 1), drain->1, correction->(1 if nbits<6 else 0)]`.
- `RegAccumOp` with `AccumMul`: name = `op.name + "Mul"`, similar log2-corrected layers.
- `RegAccumOp` with anything else: `layers = log2(nbits*0.03125 + 1)`, `drain = nbits/32`, `correction = (1 if nbits<32 else 0)`.
- `FixOp`: `(op.name, Seq("b" -> op.fmt.nbits))`.
- `FltOp`: `(op.name, Nil)`.
- `DelayLine`: `("DelayLine", Seq("d" -> {if s.userInjectedDelay then d else 0}))` — user-injected delays report their delay; automatic retiming delays register as 0.
- `Mux`: `("Mux", Seq("b" -> nbits(s)))`.
- `OneHotMux`/`PriorityMux`: `(name, Seq("b" -> ceil(log2(sel.length))))`.
- `SpatialBlackboxUse`: `("SpatialBlackbox", Seq("lat" -> bbox.bodyLatency.head))`.
- `SRAMRead` if `spatialConfig.enableAsyncMem`: name rewritten to `"SRAMAsyncRead"` or `"SRAMBankedAsyncRead"`.
- `Switch` with bits: `("SwitchMux", Seq("n" -> op.selects.length, "b" -> nbits(s)))`. `Switch` w/o bits: `"Switch"`.
- `CounterNew`: `("Counter", Seq("b" -> op.A.nbits, "p" -> op.par.toInt))`.
- `CounterChainNew`: `("CounterChain", Seq("n" -> op.counters.length))`.
- `op.isControl`: name = `s.getRawSchedule.getOrElse(Sequenced).toString`, params = `[n -> nStages(s)]`.
- fallback: `(op.productPrefix, Nil)`.

### DSE engine

**`DSEMode`.** `DSEMode.scala:3-10`. Five values: `Disabled`, `Heuristic`, `Bruteforce`, `HyperMapper`, `Experiment`. Dispatched by `DSEAnalyzer.process` at `DSEAnalyzer.scala:74-80`.

**`ParameterAnalyzer`.** `ParameterAnalyzer.scala:12-194`. Walks the IR (using `argon.passes.Traversal`), collecting:
- `AccelScope` → sets `TopCtrl`.
- `SetReg(reg, x) if reg.isArgIn` → copies bound from `x` to each reader.
- `FIFONew(Expect(c))` → warns, adds to `IgnoreParams`.
- `SRAMNew(dims)` / `RegFileNew(dims, _)` → each `Expect` dim → `TileSizes += p`.
- `DenseTransfer` / `SparseTransfer` → `e.pars` non-param values get their int value set, params → `ParParams`.
- `CounterNew(start, end, step, par)` → collects params from all four; starts/ends/steps → `TileSizes`, pars → `ParParams`. Then adds `Restrictions` via a big pattern match over counter shapes — e.g. `CounterNew(Final(0), Parameter(e), Final(1))` adds `RLessEqual(par, e)` and `RDivides(par, e)`; other shapes generate `RDividesQuotient`, `RDividesConst`.
- `OpForeach`/`OpReduce`/`OpMemReduce` → `e.cchain.pars → ParParams`. If `lhs.isOuterControl && !lhs.getUserSchedule.isDefined` → `PipelineParams += lhs`.

**`SpaceGenerator`.** `SpaceGenerator.scala:11-80`. `createIntSpace` turns tile-size + par params into `Domain[Int]` objects (ordinal spaces). `createCtrlSpace` turns pipeline-toggle controllers into `Domain[Boolean]` with options `[false, true]`, setter writes `Pipelined` or `Sequenced` to the sym via `setSchedValue`, prior is `Categorical(Uniform)` (the HyperMapper config format interprets this). The private field `PRUNE = false` disables a prototype per-param single-restriction pruning step at `SpaceGenerator.scala:53-62`.

**`PruneWorker`.** `PruneWorker.scala:11-30`. One-shot runnable: for each index in `(start, start+size)`, uses the `(prods, dims)` helpers to decompose the linear index into per-domain values, calls `Domain.set`, then evaluates `restricts.forall(_.evaluate())`. Valid points are collected and shoved into a `LinkedBlockingQueue[Seq[Int]]`. Running the pruning in parallel with `T` threads, each handling a `BLOCK_SIZE = ceil(NPts / T)` stripe, then collecting via `workerIds.flatMap{_ => results.take()}.map{i => BigInt(i)}` (`DSEAnalyzer.scala:204-231`).

**Heuristic DSE pipeline.** `DSEAnalyzer.heuristicDSE` at `DSEAnalyzer.scala:149-283`:
1. Prune single-param restrictions via `space.zip(params).map{ case (d, p) => d.filter{state => restricts.filter(_.dependsOnlyOn(p)).forall(_.evaluate()(state)) } }`.
2. Compute `NPts = prunedSpace.map(_.len).product` — bail if > `Int.MaxValue` (error "Space size is greater than Int.MaxValue. Don't know what to do here yet…").
3. Parallel `PruneWorker` enumeration across `T = spatialConfig.threads` workers, each writing its legal-indices list into `results: LinkedBlockingQueue[Seq[Int]]`.
4. `val points = scala.util.Random.shuffle(legalPoints).take(75000)` — hard-coded 75k sample cap.
5. `threadBasedDSE(points.length, ..., program) { queue => points.sliding(BLOCK_SIZE, BLOCK_SIZE).foreach{ block => queue.put(block.map(PointIndex)) } }` with `BLOCK_SIZE = min(ceil(points.size / T), 500)` (`DSEAnalyzer.scala:270-271`).
6. After completion: `Sensitivity.around(filename, center.toMap)` at `DSEAnalyzer.scala:436-439` runs per-parameter ± sensitivity analysis on the written CSV.

**Experiment mode.** `DSEAnalyzer.scala:240-267` runs 10 trials of the same shuffled-75k sampling, each writing a separate CSV `${config.name}_trial_$i.csv`, then `sys.exit(0)`. Intended as a DSE-reproducibility harness.

**`threadBasedDSE`.** `DSEAnalyzer.scala:286-440`. Sets up two `LinkedBlockingQueue`s with capacity 5000: `workQueue: Seq[DesignPoint]` (input) and `fileQueue: Array[String]` (output). Creates `T` `DSEThread` workers and 1 `DSEWriterThread`. Each worker: takes a batch, evaluates latency via `cycleAnalyzer.test(paramRewrites)`, then for each request iterates `pt.set(indexedSpace, prods, dims)`, runs `areaAnalyzer.rerun(accel, program)`, computes `valid = area <= capacity && !state.hadErrors`, writes a CSV row. After `pointGen(workQueue)` exhausts, `workerIds.foreach{_ => workQueue.put(Seq.empty)}` poisons the work queue. Finally reads back the CSV and prints top + bottom rows sorted by `Cycles`. Profiling uses a per-phase `System.currentTimeMillis` accumulator (`bndTime/memTime/conTime/areaTime/cyclTime`). Memory/scalar/contention analyses are dead-coded in `DSEThread.evaluate` at `DSEThread.scala:136-151`.

**`DSEAreaAnalyzer`.** `DSEAreaAnalyzer.scala:15-247`. Mixes `RerunTraversal` and `AccelTraversal`; a fresh `preprocess` resets `scopeArea = Nil` and `savedArea = NoArea`. `visit[A]` has one case per controller:
- `AccelScope(block)` → `inAccel { savedArea = scopeArea.fold(_+_); areaOfBlock(block, false, 1) }`.
- `OpForeach`: `areaOfBlock(block, isInner = lhs.children.size > 0, P = cchain.constPars.product) + areaOf(lhs)`.
- `OpReduce`: map duplicated P times, reduction tree = `areaOfBlock(reduce, isInner=true, P-1)` (L-1 internal nodes for L leaves), `treeDelayArea = reductionTreeDelays(P).map(dly => areaModel.areaOfDelayLine(reduceLength*dly, op.A.nbits, 1)).fold(NoArea){_+_}`, plus `areaOfCycle(load, 1) + areaOfCycle(reduce, 1) + areaOfCycle(store, 1)`.
- `OpMemReduce`: `mapArea = areaOfBlock(map, ..., Pm)`, `treeArea = areaOfPipe(reduce, 1) * Pm * Pr`, `treeDelayArea = reductionTreeDelays(Pm)…`.
- `Switch`, `StateMachine` are handled similarly.
- Fallback: `areaOf(lhs) + rhs.blocks.map(blk => areaOfBlock(blk, isInner=false, 1)).fold(_+_)`.

**`pipeDelayLineArea`.** `DSEAreaAnalyzer.scala:71-108`. For each `(s@Def(d))` in `scope`, computes `criticalPath = delayOf(s) - latencyOf(s)`. For each bit-based input `in`: `size = retimingDelay(in, inReduce) + criticalPath - delayOf(in)`. If `size > 0`, records the *max* such size per input in `delayLines: mutable.HashMap[Sym, Long]`. Finally sums `areaOfDelayLine(len, nbits(e), par)` for each entry. Explicit comment above the impl: "Alternative (functional) implementation (it's a groupByReduce! plus a map, plus a reduce)" (`DSEAreaAnalyzer.scala:76-89`).

**`LatencyAnalyzer.test(rewriteParams)`.** `LatencyAnalyzer.scala:29-48`. Spatial compiles a runtime-model jar out-of-line (see `DSEAnalyzer.compileLatencyModel`) and stashes the jar in `$gen_dir/model/`. Here we `getListOfFiles(gen_dir + "/model").filter(_.contains("RuntimeModel-assembly")).head`. The compiled jar exposes a `tune <params>` CLI; `LatencyAnalyzer` builds `"java -jar $modelJar ni $batchedParams"` where `batchedParams = params.map(rp => "tune " + rp.mkString(" ")).mkString(" ")` and batches in sizes of 1000. Output is `grep "Total Cycles for App"` with a `"^.*: ".r.replaceAllIn(r, "")` stripping trailer; negative values → `Long.MaxValue` (invalid).

**`HyperMapperDSE`.** `HyperMapperDSE.scala:12-202`. Writes a JSON config to `$config.cwd/dse_hm/$config.name.json` with:
- `"application_name": "$config.name"`
- `"optimization_iterations": spatialConfig.hypermapper_iters`
- `"evaluations_per_optimization_iteration": spatialConfig.hypermapper_evalsPerIter`
- `"design_of_experiment.number_of_samples": spatialConfig.hypermapper_doeSamples`
- `"optimization_objectives": ["Slices", "Cycles"]`, `"feasible_output.name": "Valid"`, `"feasible_output.true_value": "true"`
- For each domain: `{ "parameter_type": d.tp, "values": [d.optionsString], "parameter_default": d.valueString, "prior": d.prior }`.
Then launches `BackgroundProcess(workDir, "python", "$HYPERMAPPER_HOME/scripts/hypermapper.py", jsonFile)`. Two communication threads: `HyperMapperReceiver` reads stdout line-by-line looking for `Request <n>` or `FRequest <n> <file>`, reads the follow-up CSV header + `n` point rows, enqueues a `DesignPoint` per row. `HyperMapperSender` reads from the worker result queue and writes CSV rows to HyperMapper stdin.

**`HyperMapperThread` and `ContentionAnalyzer` dead code.** `HyperMapperThread.scala:1-148` is all `//`-commented. `ContentionAnalyzer.init() / run()` calls inside `DSEThread.run`/`evaluate` are all commented out (`DSEThread.scala:59, 68, 73, 144-145`). The `ContentionAnalyzer` class itself still exists and is plausibly invokable, but no live call site instantiates it.

### Banking math in `utils.math`

**`computeP(n, b, alpha, stagedDims, errmsg)`.** `utils/src/utils/math/package.scala:134-209`. This is the paper corrigendum to Wang et al. FPGA '14 eqns: the paper assumed periodicity 1 in the leading dimension, which is wrong for e.g. `alpha=[1,2], N=4, B=1`. The correction introduces a per-dimension `P_raw_i = n*b / gcd(n*b, alpha_i)` (with `P_raw_i = 1` if `alpha_i = 0`). Then for each dim, `P_expanded_i = divisors(P_raw(i)) ++ {if P_raw(i) != 1 && b == 1 then [stagedDims(i)] else []}`. Candidates are Cartesian products filtered by: (a) `p.length == 1 && p == P_raw` OR (`p.length > 1 && p.product == b * P_raw.map(pr => n - (pr % n)).max`) — the volume constraint; (b) `spansAllBanks(p, alpha, n, b)` — the census constraint. Returns all candidates as `Seq[Seq[Int]]`.

**`spansAllBanks(p, a, N, B)`.** `utils/math/package.scala:112-115`. `allLoops(p, a, B, Nil).map(%N)` then checks every `0..N-1` occurs at most `B` times — if yes, every bank is reachable.

**`volume`/`hiddenVolume`/`numBanks`.** `package.scala:219-229`. `hiddenVolume(Ns, Bs, Ps, Ds)` estimates padding elements needed to pad `Ds` up to integer multiples of `Ps`, cell-by-cell. When `Ns.size == 1`: `Ds.product * Ps.map(x => ceil(Ns.head*Bs.head/x) - 1).max`. Else: product over dims of `Ds(i) * (ceil(Bs(i)*Ns(i)/Ps(i)) - 1)`. `volume = Ds.product + hiddenVolume(...)`. `numBanks(Ns) = Ns.product`.

**`modifiedCrandallSW(x, t, c)`.** `package.scala:73-101`. Software simulation of Crandall's algorithm for Mersenne division. `t + c` must be a power of 2 (asserted). Inner loop: `qs(i+1) = floor(qs(i) * c / m)`, `rs(i+1) = qs(i) % m`. Final adjustment: while `r >= t`, `r -= t; q += 1`. Prints "messed up" diagnostics if final `(q,r)` disagrees with naive `x/t, x%t`. Used to validate the hardware Crandall divider generator.

**`isPow2`, `gcd`, `coprime`, `divisors`.** `package.scala:7-37`. Standard implementations. `coprime(xs)` is `xs.size == 1 || !xs.forallPairs(gcd(_,_) > 1)`. `divisors(x) = (1 to x).collect{ case i if x % i == 0 => i }`.

### `AccessMatrix` banking bridge

**Type.** `AffineData.scala:24-29`. `case class AccessMatrix(access: Sym[_], matrix: SparseMatrix[Idx], unroll: Seq[Int], isReader: Boolean = false)` — pairs an access sym with a sparse-matrix affine representation and unroll indices. One matrix per unrolled access instance.

**`overlapsAddress / isSuperset / intersects`.** `AffineData.scala:42-48`. Delegate to `isl.overlapsAddress / isSuperset / intersects`. The first is implemented in the ISL subprocess; the other two are stubs (see above).

**`isDirectlyBanked / bankMuxWidth`.** `AffineData.scala:74-89`. For given `(N, B, alpha)` banking scheme: if `N.size == 1 && alpha.size > 1`, compute `bank = alpha flatMul matrix` → single `SparseVector[Idx]`, then `span = bank.span(N.head, B.head)` → `ResidualGenerator`, return `span.expand(N.head).distinct.size`. Else compute per-dim spans and take the product. `isDirectlyBanked = (bankMuxWidth == 1)`.

**`arithmeticNodes`.** `AffineData.scala:92-124`. Emits a list of `(opName, Option[operand1], Option[operand2])` tuples describing the arithmetic needed at runtime to resolve the bank. For single-bank `N.size == 1 && alpha.size > 1` the pattern is: one `FixAdd` per column in each row (to combine affine coefficients), plus one `FixAdd(_, c)` if row has a nonzero constant, then per-dim `FixMul` components (skipping pow2 multipliers), row combinations, then `FixDiv` by `B.head` if not pow2, then `FixMod` by `N.head` if not pow2. Used by `AreaModel` to estimate arithmetic cost of banking resolution.

## Interesting edge cases / bugs / bottlenecks

- **`NBestGuess.factorize`** at `BankingData.scala:550-552` is `List.tabulate(number){i => i + 1}.collect{case i if number % i == 0 => i}` — O(N) per call. It's invoked from `expand` at `BankingData.scala:560-563` over all axes, and `expand` itself is called across the full (N, B) search grid in `MemoryConfigurer` banking-scheme enumeration. Realistic sizes are 32–2048, not critical, but this is the simplest implementation of `divisors` one could write.
- **`DSEAreaAnalyzer.pipeDelayLineArea`** uses a `mutable.HashMap` to groupBy-max per-input delays instead of an idiomatic Scala `groupBy.mapValues.max`. The comment above the impl suggests this is an intentional performance rewrite — but with no benchmark data attached.
- **`CongestionModel.evaluate` hard clamp** at `CongestionModel.scala:121-123`: `170 max result.toInt` — any congestion under 170 cycles is "model is naughty" and gets snapped up.
- **`CongestionModel.lazy val params` field order.** All the `lazy val`s reference `model` as a captured `var` in the outer `CongestionModel` object. The first call to `evaluate` writes `model = typ.toString` before the `lazy val`s are forced, but if anyone else forces them earlier (e.g. via reflection or eager ScalaTest), `params` would be bound to `""`.
- **`DSEAnalyzer.compileLatencyModel`** shells out to `bash scripts/assemble.sh` at DSE compile time — not to an embedded classpath. `"sbt assembly"` would be the portable alternative and is preserved as a commented-out block at `DSEAnalyzer.scala:131-136`. Comment "(SO DIRTY)" at `DSEAnalyzer.scala:126` acknowledges.
- **`CtrModel` arity overloads.** 16 explicit apply overloads at `RuntimeModel.scala:142-157`. Makes debugger stack-traces messy.
- **`DSEThread.init` shares one `areaAnalyzer` across all workers.** The comment at `DSEAnalyzer.scala:349-350` says "Initializiation may not be threadsafe - only creates 1 area model shared across all workers". Each worker's `areaAnalyzer` is lazy and target-global. Bug if `areaAnalyzer.rerun` mutates shared state.
- **`ParameterAnalyzer.visit`** hack at `ParameterAnalyzer.scala:172-173`: `pars.foreach{x => dbgs(...); ParParams += _}` — the underscore captures the *local* `x` only if `dbgs` is well-behaved. Written idiomatically would be `ParParams += x`.
- **`OpForeach`** bug at `AreaModel.scala:51-52`: in `accessUnrollCount` the `OpMemReduce` case returns `par * (cchainMap.constPars.product + cchainRed.constPars.product)` with a `// TODO: This is definitely wrong, need to check stage of access` comment.

## Bottlenecks for DSE runtime

Ranked by likely cost per point:
1. **`areaAnalyzer.rerun(accel, program)`** at `DSEThread.scala:147` — this is the full area traversal of `Accel`. `DSEAreaAnalyzer.visit` recurses through every controller and calls `latenciesAndCycles(block)` (via `pipeDelayLineArea`) which itself walks the entire scope computing retiming. O(|scope|^2) in the worst case due to `latencyAndInterval` walking consumers.
2. **`LatencyAnalyzer.test`** at `LatencyAnalyzer.scala:37` — forks a `java -jar RuntimeModel-assembly…` subprocess per batch of up to 1000 points. JVM startup is ~200–500ms, amortized over 1000 points is cheap, but this is bounded by I/O of `java.lang.Process`.
3. **Bank-scheme enumeration in `MemoryConfigurer`** (outside this bundle, but a banking pass must run before or in parallel with DSE). `NBestGuess.factorize` is O(N), `AlphaBestGuess` uses `Seq.tabulate(factorize(N).length){ i => factorize(N).combinations(i+1).toList }.flatten.map(_.product)` — exponential in `factorize(N).length` in the worst case.
4. **`PruneWorker`** at `DSEAnalyzer.scala:204-231` linear in `BLOCK_SIZE`, one pass over all space points. If `NPts > Int.MaxValue` falls off a cliff — `heuristicDSE` errors.
5. **`HyperMapperDSE` polling loop.** The stdin/stdout buffered-pipe communication is line-by-line; large candidate batches from HyperMapper are bottlenecked on scheduling fairness between the Python and Scala sides.
6. **`CongestionModel.hypercube_features`** computes 64 hypervolumes by `CombinationTree[Double](...)` — O(2^D) in feature count, D=6 here. If scaled up this blows up fast.

## Distillation plan

This note feeds six spec entries. The mapping:

- `[[10 - ISL Binding]]` — ISL trait, subprocess lifecycle, wire format, `overlapsAddress`, the `isSuperset`/`intersects` stubs.
- `[[20 - Access Algebra]]` — `SparseVector`/`SparseMatrix`/`SparseConstraint`/`ConstraintMatrix`, affine algebra, `span`/`expand`/`replaceKeys`.
- `[[30 - Banking Math]]` — `AccessMatrix`, `AddressPattern`/`AffineProduct`/`Prod`/`Sum`/`Modulus`, `computeP`, `spansAllBanks`, `modifiedCrandallSW`, volume/hiddenVolume/numBanks.
- `[[10 - Area Model]]` — `Model[T,F]`, `Area = Model[Double, AreaFields]`, `AreaEstimator` + PMML + `crudeEstimateMem`, `SpatialModel` CSV loader, `AreaModel.areaOf`/`areaOfMem`/`areaOfDelayLine`, `NodeParams.nodeParams` dispatch table.
- `[[20 - Latency Model]]` — `LatencyModel` API, `requiresRegisters`, `builtInLatencyOfNode`, the four block-latency models, `GenericLatencyModel.latencyOfNode` DenseTransfer override, `TileLoadModel` dead code, `CongestionModel` 6-D lattice regression with PWL calibration, `RuntimeModel.ControllerModel.cycsPerParent` cycle equation.
- `[[40 - Design Space Exploration]]` — `DSEAnalyzer` + modes, `ParameterAnalyzer`, `SpaceGenerator`, `PruneWorker`, `DSEThread`/`DSEWriterThread`, heuristic/brute-force/HyperMapper pipelines, `DSEAreaAnalyzer` reductions, `LatencyAnalyzer` jar subprocess, `RuntimeModel` cycle equation.
