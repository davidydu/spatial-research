---
type: moc
project: spatial-spec
date_started: 2026-04-23
source_files:
  - "src/spatial/Spatial.scala:60-257"
---

# Pass Pipeline — Canonical Execution Order

Every pass in `Spatial.runPasses`, in the order they appear in the `==>` chain. Source: `src/spatial/Spatial.scala:60-257`. Reusable sub-sequences (`retimeAnalysisPasses`, `bankingAnalysis`, `DCE`, `fifoInitialization`, `streamify`, `createDump`) are inlined in the numbering below.

## Format

Each entry is:

`pass-name (category) — gate condition — file — one-line summary`

**Categories**: `transformer` (mutates IR or metadata), `analysis` (read-only; writes per-symbol metadata), `codegen` (emits output files such as `.html`/`.dot`/`.scala`/`.v`), `report` (logs/text reports), `sanity-check` (verification, fails compilation on error).

**Gate** is the condition that determines if the pass runs. `always` = unconditional (modulo `enable` parameter on the pass itself). Allocation-site `lazy val` means a `false` gate prevents construction.

Multi-invocation passes are tagged `[runs Nx]` where applicable.

## Canonical ordered list

1. **IRPrinter #1** (codegen) — `config.enDbg` — `argon/src/argon/passes/IRPrinter.scala` — first dump of the input block. Allocated `Spatial.scala:66`. [runs many times throughout]
2. **CLINaming** (analysis) — always — `traversal/CLINaming.scala` — tags input-argument array-applys with `CLIArgs` names from Scala-level array accesses.
3. **FriendlyTransformer** (transformer) — always — `transform/FriendlyTransformer.scala` — auto-wraps unreferenced bits as `ArgIn`; dedupes DRAM dimension values.
4. **IRPrinter** (codegen) — `enDbg` — dump.
5. **CompilerSanityChecks** (sanity-check) — `enLog && !allowInsanity` — `traversal/CompilerSanityChecks.scala` — verifier, allocated as `transformerChecks` at `Spatial.scala:72`. [runs after almost every transformer]
6. **UserSanityChecks** (sanity-check) — `!spatialConfig.allowInsanity` — `traversal/UserSanityChecks.scala` — user-facing error reporting (ArgOut-read-in-Accel, width mismatches).
7. **SwitchTransformer #1** (transformer) — always — `transform/SwitchTransformer.scala` — flattens nested `IfThenElse` into `Switch` + `SwitchCase`. [runs 3x: here, post-DSE, post-streamify]
8. **IRPrinter + CompilerSanityChecks**.
9. **SwitchOptimizer #1** (transformer) — always — `transform/SwitchOptimizer.scala` — simplifies trivial switches; records `hotSwapPairings` via `markHotSwaps`. [runs 2x: here, post-DSE]
10. **IRPrinter + CompilerSanityChecks**.
11. **BlackboxLowering1** (transformer) — always — `transform/BlackboxLowering.scala` — `lowerTransfers=false`; lowers non-constant `FixSLA`/`FixSRA`/`FixSRU`. Allocated `Spatial.scala:103`.
12. **IRPrinter + CompilerSanityChecks**.
13. **BlackboxLowering2** (transformer) — always — `transform/BlackboxLowering.scala` — `lowerTransfers=true`; lowers `DenseTransfer`/`SparseTransfer`/`FrameTransmit` to `Fringe*` nodes. Allocated `Spatial.scala:104`.
14. **IRPrinter + CompilerSanityChecks**.
15. **TextCleanup** (transformer) — `spatialConfig.textCleanup` (`--textCleanup`) — `transform/TextCleanup.scala` — drops symbols with `canAccel=false` inside Accel.
16. **ParameterAnalyzer** (analysis) — `spatialConfig.enableArchDSE` (`--tune`/`--bruteforce`/`--heuristic`/`--experiment`/`--hypermapper`) — `dse/ParameterAnalyzer.scala` — collects tunable parameters for DSE.
17. **retimeAnalysisPasses #1 (DSE prelude)** — `spatialConfig.enableRuntimeModel` — expands to 4 passes:
    - a. **IRPrinter**.
    - b. **DuplicateRetimeStripper** (transformer) — `transform/DuplicateRetimeStripper.scala` — collapses back-to-back `RetimeGate()` nodes inside inner-control blocks. [runs 3x as part of `retimeAnalysisPasses`]
    - c. **IRPrinter**.
    - d. **RetimingAnalyzer #1** (analysis) — `traversal/RetimingAnalyzer.scala` — `shouldRun = enableRetiming`. Computes `fullDelay = scrubNoise(l - latencyOf(s, inReduce=cycles(s)))`, `inCycle`, `bodyLatency`. [runs 3-4x]
18. **InitiationAnalyzer (DSE)** (analysis) — `spatialConfig.enableRuntimeModel` — `traversal/InitiationAnalyzer.scala` — computes `compilerII = ceil(interval/iterDiff)` per controller.
19. **RuntimeModelGenerator (dse)** (codegen) — `spatialConfig.enableRuntimeModel` — `model/RuntimeModelGenerator.scala` — emits Scala runtime-model code for DSE's cost model.
20. **DSEAnalyzer** (analysis) — `spatialConfig.enableArchDSE` — `dse/DSEAnalyzer.scala` — does the design-space search.
21. **SwitchTransformer #2** (transformer) — always — `transform/SwitchTransformer.scala` — re-flatten after DSE.
22. **IRPrinter + CompilerSanityChecks**.
23. **SwitchOptimizer #2** (transformer) — always — `transform/SwitchOptimizer.scala` — re-simplify after DSE.
24. **IRPrinter + CompilerSanityChecks**.
25. **MemoryDealiasing** (transformer) — always — `transform/MemoryDealiasing.scala` — resolves `MemDenseAlias`/`MemSparseAlias` into muxed reads of underlying DRAM. Must run before pipe insertion.
26. **IRPrinter + CompilerSanityChecks**.
27. **LaneStaticTransformer** (transformer) — `!spatialConfig.vecInnerLoop` — `transform/LaneStaticTransformer.scala` — folds `FixMod/FixAdd/FixSub/FixMul/FixSLA` on pre-unroll iterators into `LaneStatic` nodes.
28. **IRPrinter**.
29. **PipeInserter #1** (transformer) — always — `transform/PipeInserter.scala` — classify stmts → compute stages → bind stages → wrap inner stages in `Pipe`. Sets `allowPrimitivesInOuterControl = false`. [runs 3x]
30. **IRPrinter + CompilerSanityChecks**.
31. **RegReadCSE #1** (transformer) — always — `transform/RegReadCSE.scala` — dedupes `RegRead` inside inner controllers via `state.cache.get(op2).filter(_.effects == effects)`. [runs 2x]
32. **DCE #1** — always — expands to 4 passes:
    - a. **UseAnalyzer** (analysis) — `traversal/UseAnalyzer.scala` — propagates `Users`, `readUses`, `PendingUses`; flags unused memories. [runs 2x]
    - b. **TransientCleanup** (transformer) — `transform/TransientCleanup.scala` — DCE + transient motion. [runs 2x]
    - c. **IRPrinter**.
    - d. **CompilerSanityChecks**.
33. **streamify block** — `spatialConfig.streamify` (`--streamify`) — expands to ~12 passes:
    - a. **TreeGen + HtmlIRGenSpatial** (codegen) — `codegen/treegen/TreeGen.scala`, `codegen/dotgen/HtmlIRGenSpatial.scala` — `createDump("PreEarlyUnroll")`.
    - b. **DependencyGraphAnalyzer** (analysis) — `transform/streamify/DependencyGraphAnalyzer.scala` — builds `InferredDependencyEdge`s.
    - c. **InitiationAnalyzer (streamify)** (analysis) — `traversal/InitiationAnalyzer.scala` — pre-streamify II.
    - d. **IRPrinter + CompilerSanityChecks** (`streamChecks`, allocated at `Spatial.scala:74` with `enable = true`).
    - e. **TreeGen + HtmlIRGenSpatial** — `createDump("PreFlatten")`.
    - f. **HierarchicalToStream** (transformer) — `transform/streamify/HierarchicalToStream.scala` — wraps each inner controller in FIFO trio (`genToMain`/`mainToRelease`/`genToRelease`).
    - g. **IRPrinter**.
    - h. **SwitchTransformer #3** (transformer) — re-flatten post-streamify.
    - i. **IRPrinter**.
    - j. **PipeInserter #2** (transformer) — pipe-insert post-streamify.
    - k. **IRPrinter + streamChecks**.
    - l. **TreeGen + HtmlIRGenSpatial** — `createDump("PostStream")`.
34. **StreamTransformer** (transformer) — `spatialConfig.distributeStreamCtr` (default on; disabled by `--noModifyStream`) — `transform/StreamTransformer.scala` — distributes a `Stream.Foreach`'s counter chain into each child controller.
35. **IRPrinter**.
36. **fifoInitialization** — always — expands to 3 passes:
    - a. **FIFOInitializer** (transformer) — `transform/streamify/FIFOInitializer.scala` — emits init-controllers for FIFOs with `fifoInits` set.
    - b. **PipeInserter #3** (transformer) — pipe-insert post-init.
    - c. **MetadataStripper\<FifoInits\>** (transformer) — `transform/MetadataStripper.scala` — clears `FifoInits` so it doesn't re-trigger.
37. **IRPrinter**.
38. **createDump("PostInit")** (codegen) — `spatialConfig.streamify` — `codegen/treegen/`, `codegen/dotgen/` — TreeGen + HtmlIRGenSpatial.
39. **bankingAnalysis** — always — expands to ~10 passes:
    - a. **IRPrinter**.
    - b. **DuplicateRetimeStripper #2** (transformer).
    - c. **IRPrinter**.
    - d. **RetimingAnalyzer #2 (banking)** (analysis) — `enableRetiming` — feeds banking concurrency rule (`requireConcurrentPortAccess` `delayDefined` cases).
    - e. **AccessAnalyzer** (analysis) — `traversal/AccessAnalyzer.scala` — `Affine.unapply` walks accesses; writes `accessPattern`, `affineMatrices`.
    - f. **IterationDiffAnalyzer** (analysis) — `traversal/IterationDiffAnalyzer.scala` — writes `iterDiff` for reduce cycles; `segmentMapping` per multi-lane reader.
    - g. **IRPrinter**.
    - h. **MemoryAnalyzer** (codegen) — `traversal/MemoryAnalyzer.scala` — extends `Codegen`! Per-memory `MemoryConfigurer.configure()`; writes `Duplicates`/`Dispatch`/`Ports`/`GroupId`; emits `decisions_${state.pass}.html`.
    - i. **MemoryAllocator** (analysis) — `traversal/MemoryAllocator.scala` — greedy first-fit assigns each duplicate to URAM/BRAM/LUTRAM in `target.memoryResources` order (last dropped, then assigned as fallback).
    - j. **IRPrinter**.
40. **CounterIterSynchronization** (analysis) — always — `traversal/CounterIterSynchronization.scala` — rebinds each counter's iter to `IndexCounterInfo(ctr, 0 until par)`.
41. **createDump("PreExecution")** (codegen) — always — TreeGen + HtmlIRGenSpatial.
42. **CompilerSanityChecks**.
43. **ExecutorPass** (analysis) — `spatialConfig.enableScalaExec` (`--scalaExec`) — `executor/scala/ExecutorPass.scala` — optional in-compiler Scala executor.
44. **createDump("PostExecution")** (codegen) — `enableScalaExec` — TreeGen + HtmlIRGenSpatial.
45. **UnrollingTransformer** (transformer) — always — `transform/UnrollingTransformer.scala` — composition class over `UnrollingBase` + `ForeachUnrolling`/`ReduceUnrolling`/`MemReduceUnrolling`/`MemoryUnrolling`/`SwitchUnrolling`/`BlackBoxUnrolling`. Post: loop controllers are `UnrolledForeach`/`UnrolledReduce`; memories duplicated per `Duplicates`.
46. **IRPrinter + CompilerSanityChecks**.
47. **RegReadCSE #2** (transformer) — always — re-dedupe after unrolling.
48. **DCE #2** — always — UseAnalyzer + TransientCleanup + IRPrinter + CompilerSanityChecks.
49. **RetimingAnalyzer #3 (post-unroll)** (analysis) — `enableRetiming` — inside inline `Seq(retimingAnalyzer, printer, streamChecks)` at `Spatial.scala:213`.
50. **IRPrinter + streamChecks**.
51. **RewriteAnalyzer** (analysis) — always — `traversal/RewriteAnalyzer.scala` — sets `canFuseAsFMA` on `FixAdd`/`FltAdd`.
52. **AccumAnalyzer #1** (analysis) — `spatialConfig.enableOptimizedReduce` — `traversal/AccumAnalyzer.scala` — identifies cycles; sets `reduceCycle`, `AccumMarker.Reg.Op`/`.FMA`. [runs 2x]
53. **IRPrinter**.
54. **RewriteTransformer** (transformer) — always — `transform/RewriteTransformer.scala` — pow2-mul, Mersenne mod, Crandall div/mod, FMA fusion (guarded by `specializationFuse` + `canFuseAsFMA`), reg-write-of-mux → enabled RegWrite, sqrt/recip fusion, shift combining, residual metadata.
55. **IRPrinter + CompilerSanityChecks**.
56. **MemoryCleanupTransformer** (transformer) — always — `transform/MemoryCleanupTransformer.scala` — drops local memories with no readers AND no writers.
57. **IRPrinter + CompilerSanityChecks**.
58. **FlatteningTransformer** (transformer) — always — `transform/FlatteningTransformer.scala` — inlines outer `UnitPipe` with a single non-stream, non-blackbox child; flattens inner-pipe switches.
59. **BindingTransformer** (transformer) — always — `transform/BindingTransformer.scala` — bundles consecutive non-conflicting sibling controllers into a `ParallelPipe`.
60. **BufferRecompute** (analysis) — always — `traversal/BufferRecompute.scala` — recomputes `depth = max(bufPort)+1` per memory via `computeMemoryBufferPorts`. Also resolves muxPort conflicts (kludge for issue #98).
61. **IRPrinter + CompilerSanityChecks**.
62. **AccumAnalyzer #2** (analysis) — `enableOptimizedReduce` — re-run after rewrites mutated cycles.
63. **IRPrinter**.
64. **AccumTransformer** (transformer) — `enableOptimizedReduce` — `transform/AccumTransformer.scala` — replaces marked WAR cycles with `RegAccumOp`/`RegAccumFMA` (II=1 specialized accumulators).
65. **IRPrinter + CompilerSanityChecks**.
66. **RetimingAnalyzer #4 (final)** (analysis) — `enableRetiming` — authoritative retime analysis before the transformer.
67. **IRPrinter**.
68. **RetimingTransformer** (transformer) — `enableRetiming` — `transform/RetimingTransformer.scala` — inserts `DelayLine(size, data)` nodes; rewires consumers via `precomputeDelayLines` (cross-block sharing) / `retimeBlock` (per-block) / `retimeStms` (per-stmt with `isolateSubst`).
69. **IRPrinter + CompilerSanityChecks**.
70. **RetimeReporter** (report) — always — `report/RetimeReporter.scala` — emits retiming report.
71. **BroadcastCleanupAnalyzer** (analysis) — always — `traversal/BroadcastCleanup.scala` — walks reverse stmt order in each inner controller; propagates `isBroadcastAddr=false`.
72. **IRPrinter**.
73. **InitiationAnalyzer (final)** (analysis) — always — `traversal/InitiationAnalyzer.scala` — final `II`/`compilerII`/`bodyLatency` per controller.
74. **RuntimeModelGenerator (final)** (codegen) — `enableRuntimeModel` — emits final Scala model code.
75. **MemoryReporter** (report) — always — `report/MemoryReporter.scala` — dumps final memory decisions.
76. **finalIRPrinter** (codegen) — always (`enable = true`) — `argon/src/argon/passes/IRPrinter.scala` — unconditional final IR dump. Allocated `Spatial.scala:67`.
77. **finalSanityChecks** (sanity-check) — `!spatialConfig.allowInsanity` — `traversal/CompilerSanityChecks.scala` — final verifier (different `enable` than `transformerChecks`). Allocated `Spatial.scala:73`.
78. **TreeGen** (codegen) — always — `codegen/treegen/TreeGen.scala` — final tree dump.
79. **HtmlIRGenSpatial (irCodegen)** (codegen) — always — `codegen/dotgen/HtmlIRGenSpatial.scala` — final HTML IR.
80. **DotFlatGenSpatial** (codegen) — `spatialConfig.enableFlatDot` (`--fdot`) — `codegen/dotgen/DotFlatGenSpatial.scala`.
81. **DotHierarchicalGenSpatial** (codegen) — `spatialConfig.enableDot` (`--dot`) — `codegen/dotgen/DotHierarchicalGenSpatial.scala`.
82. **ScalaGenSpatial** (codegen) — `spatialConfig.enableSim` (`--sim`) — `codegen/scalagen/ScalaGenSpatial.scala`.
83. **ChiselGen** (codegen) — `spatialConfig.enableSynth` (`--synth`) — `codegen/chiselgen/ChiselGen.scala`.
84. **CppGen** (codegen) — `enableSynth && target.host == "cpp"` — `codegen/cppgen/CppGen.scala`.
85. **RogueGen** (codegen) — `target.host == "rogue"` — `codegen/roguegen/RogueGen.scala`.
86. **ResourceReporter** (report) — `spatialConfig.reportArea` (`--reportArea`) — `report/ResourceReporter.scala`.
87. **ResourceCountReporter** (report) — `spatialConfig.countResources` (`--countResources`) — `report/ResourceCountReporter.scala`.
88. **PIRGenSpatial** (codegen) — `spatialConfig.enablePIR` (`--pir`) — `codegen/pirgen/PIRGenSpatial.scala`.
89. **TungstenHostGenSpatial** (codegen) — `spatialConfig.enableTsth` (`--tsth`) — `codegen/tsthgen/TungstenHostGenSpatial.scala`.

## Notable counts

- Total numbered steps with inline expansion: **89**.
- `PipeInserter` invocations: **3** (steps 29, 33j inside streamify, 36b inside fifoInitialization).
- `RetimingAnalyzer` invocations: up to **4** (step 17d under `enableRuntimeModel`, step 39d inside `bankingAnalysis`, step 49 post-DCE, step 66 final). The first is gated by DSE config; the latter 3 are typically all run together when retiming is on.
- `DuplicateRetimeStripper` invocations: matches `RetimingAnalyzer` count (each is preceded by a stripper, since `retimeAnalysisPasses = Seq(printer, duplicateRetimeStripper, printer, retimingAnalyzer)`).
- `SwitchTransformer` invocations: **3** (steps 7, 21, 33h inside streamify).
- `SwitchOptimizer` invocations: **2** (steps 9, 23).
- `BlackboxLowering` invocations: **2** (step 11 with `lowerTransfers=false`, step 13 with `lowerTransfers=true`).
- `AccumAnalyzer` invocations under `enableOptimizedReduce`: **2** (steps 52, 62).
- `IRPrinter` (debug `printer`) invocations: scattered throughout, gated by `config.enDbg`. `finalIRPrinter` (step 76) always runs (`enable = true`).
- `CompilerSanityChecks` (`transformerChecks`) invocations: after essentially every transformer, gated by `enLog && !allowInsanity`. `streamChecks` (`Spatial.scala:74`) is unconditionally enabled. `finalSanityChecks` (step 77) gates only on `!allowInsanity`.
- `InitiationAnalyzer` invocations: up to **3** (step 18 DSE-only, step 33c streamify-only, step 73 always).
- `MetadataStripper` invocations: **1** unconditional (inside `fifoInitialization`); plus a `bankStrippers` allocated at `Spatial.scala:132` but **not actually invoked in `runPasses`** (allocated but unused).

## Sub-sequence definitions

- `retimeAnalysisPasses` (`Spatial.scala:140`) = `Seq(printer, duplicateRetimeStripper, printer, retimingAnalyzer)`. **Used 3 places**: DSE prelude (step 17), banking prelude (step 39 a-d), and step 49 is the bare `retimingAnalyzer` only (not the full sub-seq).
- `bankingAnalysis` (`Spatial.scala:142`) = `retimeAnalysisPasses ++ Seq(accessAnalyzer, iterationDiffAnalyzer, printer, memoryAnalyzer, memoryAllocator, printer)`. **Used 1 place**: step 39.
- `fifoInitialization` (`Spatial.scala:138`) = `Seq(fifoInitializer, pipeInserter, MetadataStripper(state, S[FifoInits]))`. **Used 1 place**: step 36.
- `streamify` (`Spatial.scala:144`) = `createDump("PreEarlyUnroll") ++ Seq(dependencyGraphAnalyzer, initiationAnalyzer, printer, streamChecks) ++ createDump("PreFlatten") ++ Seq(HierarchicalToStream(state), printer, switchTransformer, printer, pipeInserter, printer, streamChecks) ++ createDump("PostStream")`. **Used 1 place**: step 33.
- `DCE` (`Spatial.scala:162`) = `Seq(useAnalyzer, transientCleanup, printer, transformerChecks)`. **Used 2 places**: steps 32 and 48.
- `createDump(n)` (`Spatial.scala:136`) = `Seq(TreeGen(state, n, s"${n}_IR"), HtmlIRGenSpatial(state, s"${n}_IR"))`. **Used 5 places**: streamify (PreEarlyUnroll, PreFlatten, PostStream), step 38 (PostInit), step 41 (PreExecution), step 44 (PostExecution).

## Cross-links

- Deep dive: `20 - Research Notes/10 - Deep Dives/pass-pipeline.md`
- Open questions: `20 - Research Notes/10 - Deep Dives/open-questions-pass-pipeline.md`
- Phase 1 coverage: `20 - Research Notes/00 - Coverage/spatial-passes-coverage.md`
- Spec entry index: `10 - Spec/40 - Compiler Passes/00 - Pass Pipeline Index.md`
- Source tree map: `40 - Cross References/source-tree-map.md`
- Per-pass spec entries: [[10 - Flows and Rewrites]], [[50 - Pipe Insertion]], [[70 - Banking]], [[80 - Unrolling]], [[C0 - Retiming]]
