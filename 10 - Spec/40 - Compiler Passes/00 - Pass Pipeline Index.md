---
type: moc
project: spatial-spec
date_started: 2026-04-23
---

# Compiler Passes — Index

The full pipeline from post-staging IR to codegen-ready IR. Canonical order lives in [[pass-pipeline-order]] and `src/spatial/Spatial.scala:60-257`.

## Canonical pipeline (abridged)

1. **CLI + orientation** — `cliNaming`, `friendlyTransformer`, `userSanityChecks`.
2. **First lowering round** — `switchTransformer`, `switchOptimizer`, `blackboxLowering1` (lowerTransfers=false), `blackboxLowering2` (lowerTransfers=true).
3. **DSE** (optional) — `paramAnalyzer`, retime-then-initiation analysis, `dsePass`.
4. **Second lowering round** — `switchTransformer`, `switchOptimizer`, `memoryDealiasing`, optional `laneStaticTransformer`.
5. **Pipe insertion** — `pipeInserter` (first).
6. **Cleanup + DCE** — `regReadCSE`, `useAnalyzer`, `transientCleanup`, `printer`, `transformerChecks`.
7. **Streamify** (optional) — `earlyUnroller`, `dependencyGraphAnalyzer`, `hierarchicalToStream`, `accelPipeInserter`, `forceHierarchical`.
8. **Stream distribution** (optional) — `streamTransformer`.
9. **FIFO init** — `fifoInitializer`, `pipeInserter`, strip FifoInits.
10. **Banking analysis** — `retimeAnalysisPasses`, `accessAnalyzer`, `iterationDiffAnalyzer`, `memoryAnalyzer`, `memoryAllocator`.
11. **Counter sync + checkpoints** — `counterIterSynchronization`, dump PreExecution, `transformerChecks`.
12. **Executor** (optional) — `executor` under `--scalaExec`.
13. **Unrolling** — `unrollTransformer`.
14. **Post-unroll cleanup** — `regReadCSE`, DCE, `retimingAnalyzer`, `printer`, `streamChecks`.
15. **Hardware rewrites** — `rewriteAnalyzer`, optional `accumAnalyzer`, `rewriteTransformer`, `memoryCleanup`.
16. **Flattening + binding** — `flatteningTransformer`, `bindingTransformer`.
17. **Buffer recompute** — `bufferRecompute`, `transformerChecks`.
18. **Accum specialization** (optional) — `accumAnalyzer`, `accumTransformer` under `enableOptimizedReduce`.
19. **Retiming** — `retimingAnalyzer`, `retiming`, `retimeReporter`.
20. **Final analyses** — `broadcastCleanup`, `initiationAnalyzer`, optional `finalRuntimeModelGen`, `memoryReporter`, `finalIRPrinter`, `finalSanityChecks`.
21. **Codegens**.

## Per-pass entries

- `10 - Flows and Rewrites.md` — `SpatialFlowRules` (staging-time metadata propagation) and `SpatialRewriteRules` (`AliasRewrites`, `CounterIterRewriteRule`, `LUTConstReadRewriteRules`, `VecConstRewriteRules`).
- `20 - Friendly and Sanity.md` — `FriendlyTransformer`, `TextCleanup`, `UserSanityChecks`, `CompilerSanityChecks`.
- `30 - Switch and Conditional.md` — `SwitchTransformer`, `SwitchOptimizer`, switch-to-mux path.
- `40 - Blackbox Lowering.md` — `BlackboxLowering` (two-phase), `MemoryDealiasing`, `LaneStaticTransformer`, `StreamTransformer`, `StreamConditionSplitTransformer`.
- `50 - Pipe Insertion.md` — `PipeInserter` algorithm (stage/bind/wrap).
- `60 - Use and Access Analysis.md` — `UseAnalyzer`, `AccessAnalyzer`, `AccessExpansion`, `AccumAnalyzer`, `IterationDiffAnalyzer`, `InitiationAnalyzer`, `RewriteAnalyzer`, `CounterIterSynchronization`, `BufferRecompute`, `BroadcastCleanup`, `PerformanceAnalyzer`.
- `70 - Banking.md` — `MemoryAnalyzer`, `MemoryConfigurer`, `BankingStrategy` (`ExhaustiveBanking`/`FullyBanked`/`CustomBanked`), `FIFOConfigurer`, `MemoryAllocator`.
- `80 - Unrolling.md` — `UnrollingBase`, `Unroller` hierarchy, `ForeachUnrolling`/`ReduceUnrolling`/`MemReduceUnrolling`/`MemoryUnrolling`/`SwitchUnrolling`.
- `90 - Rewrite Transformer.md` — Hardware rewrites (pow2-mul, Crandall mod/div, FMA fusion, reg-write-of-mux, shift combining).
- `A0 - Flattening and Binding.md` — `FlatteningTransformer`, `BindingTransformer`, `AllocMotion`.
- `B0 - Accum Specialization.md` — `AccumTransformer` (RegAccumOp / RegAccumFMA).
- `C0 - Retiming.md` — `RetimingAnalyzer`, `RetimingTransformer`, `DuplicateRetimeStripper`.
- `D0 - Streamify.md` — Experimental MetaPipe→Stream flow.
- `E0 - Cleanup.md` — `TransientCleanup`, `MemoryCleanupTransformer`, `RegReadCSE`, `FIFOAccessFusion`, `MetadataStripper`, `UnitIterationElimination`.

## Source

- `src/spatial/transform/`, `rewrites/`, `traversal/`, `flows/` (78 files)
- [[spatial-passes-coverage]] — Phase 1 coverage note, verified 2026-04-21
