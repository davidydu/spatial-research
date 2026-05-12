---
type: open-questions
project: spatial-spec
date_started: 2026-04-24
---

# Open Questions — Pass Pipeline (banking + retiming spec entries)

## Q-pp-01 — [2026-04-24] MemoryAnalyzer-as-Codegen: is the HTML output consumed?

`MemoryAnalyzer` extends `Codegen` (`traversal/MemoryAnalyzer.scala:17`) and emits `decisions_${state.pass}.html` per invocation. The HTML is purely a side effect of running the per-memory configurer. The deep-dive note flagged this as architecturally surprising.

Question: is anything downstream actually consuming `decisions_*.html` (e.g. external DSE feedback, a build dashboard, a verification harness), or is this strictly a debugging artifact? If purely debug, the codegen scaffolding adds noise — `MemoryAnalyzer` could be a regular `Pass` and the HTML logic could move to a dedicated reporter.

Source: `src/spatial/traversal/MemoryAnalyzer.scala:17, 22, 24, 111-123`
Blocked by: —
Status: open

## Q-pp-02 — [2026-04-24] MemoryAllocator's "TODO: un-gut memory allocator"

`MemoryAllocator.process` (`traversal/MemoryAllocator.scala:16`) starts with `println(s"TODO: un-gut memory allocator")`. The current pass body is the simple greedy first-fit.

Question: what is the intended functionality that's been "gutted"? Reading the surrounding code, it looks like the original allocator may have done backtracking / fractional assignment / cross-resource swaps. This matters for HLS planning — if Spatial's "real" allocator behaviour is what's documented, the spec is fine; if a more sophisticated allocator is supposed to be there, the spec is missing pieces.

Source: `src/spatial/traversal/MemoryAllocator.scala:15-17`
Blocked by: git log archeology
Status: open

## Q-pp-03 — [2026-04-24] FIFOConfigurer drops 2 disjuncts vs general rule

`MemoryConfigurer.requireConcurrentPortAccess` (`banking/MemoryConfigurer.scala:427-437`) has 7 disjuncts; `FIFOConfigurer.requireConcurrentPortAccess` (`banking/FIFOConfigurer.scala:20-26`) has 5. The 2 dropped:
1. `lca.isOuterPipeLoop && !isWrittenIn(lca)` — "OuterPipeLoop with no writes in LCA" (the buffer-port-no-conflict case).
2. The `delayDefined && fullDelay` pair — both same-parent-same-fullDelay and same-parent-diff-fullDelay-with-loopcontrolLCA.

The deep dive infers these are dropped because FIFOs aren't N-buffered, so "write reaches buffer port" is meaningless. But the source has no comment explaining the design choice.

Question: confirm via git blame that the dropped cases were intentional and not a stale-copy oversight.

Source: `src/spatial/traversal/banking/MemoryConfigurer.scala:427-437`, `banking/FIFOConfigurer.scala:20-26`
Blocked by: git blame
Status: open

## Q-pp-04 — [2026-04-24] Retiming-disabled compile path: do IterationDiff/Initiation still run?

`RetimingAnalyzer.shouldRun = enableRetiming` (`traversal/RetimingAnalyzer.scala:14`) — when `--noretime` (which also disables `enableOptimizedReduce`) the analyzer no-ops. But `IterationDiffAnalyzer` and `InitiationAnalyzer` have no analogous `shouldRun` gate.

Question: when retiming is disabled, what happens to:
1. The `iterDiff` field — is it computed (junk metadata that nothing reads), or does some upstream check skip it?
2. The `compilerII = ceil(interval/iterDiff)` formula — does it compute meaningful values? The `latency` term inside `lhs.II = min(compilerII, latency)` may be wrong if `fullDelay` was never computed.

Source: `src/spatial/traversal/RetimingAnalyzer.scala:14`, `src/spatial/traversal/IterationDiffAnalyzer.scala:1-218`, `src/spatial/traversal/InitiationAnalyzer.scala:23-41`
Blocked by: —
Status: open

## Q-pp-05 — [2026-04-24] BufferRecompute issue #98 muxPort-bump kludge

`BufferRecompute` has a `Delete once #98 is fixed` comment (`traversal/BufferRecompute.scala:41`) before the muxPort-conflict workaround:

```scala
while (hasPortConflicts(lhs).size > 0) {
  val moveMe = hasPortConflicts(lhs).head
  val maxMuxPort = lhs.readers.map(_.port.muxPort).max
  moveMe.addPort(0, Seq(), Port(moveMe.port.bufferPort, maxMuxPort+1, …))
}
```

Question: what is issue #98 in the Spatial-lang/spatial repo, and what's the proper fix? This is referenced in the C0 - Retiming spec entry as an open question; a Rust+HLS reimplementation should know whether to inherit this kludge.

Source: `src/spatial/traversal/BufferRecompute.scala:41-47`
Blocked by: GitHub issue lookup
Status: open

## Q-pp-06 — [2026-04-24] RetimingTransformer.precomputeDelayLines vs Switch case-trailing line

`RetimingTransformer.precomputeDelayLines` (`transform/RetimingTransformer.scala:111-126`) materialises lines for every block in `op.blocks`. For `Switch` ops, `retimeSwitchCase` (`transform/RetimingTransformer.scala:156-178`) also adds a trailing `delayLine(size, body.result)` whose size is the sum of two `delayConsumers` lookups.

Question: are these materialisations always disjoint (precompute creates "shared across blocks" lines, retimeSwitchCase creates "case-trailing" lines), or can they double-count the same delay? If the same `(input, delay)` pair could match both, would that produce duplicate `DelayLine` nodes in the IR, or does `addDelayLine`'s SortedSet semantics dedupe them?

Source: `src/spatial/transform/RetimingTransformer.scala:111-126, 156-178`, `src/spatial/util/modeling.scala:589-616` (`createValueDelay`)
Blocked by: —
Status: open

## Q-pp-07 — [2026-04-24] SwitchTransformer selector wording: AND-gated or "pre-OR'd"?

The pass-writing work order described flattened switch selectors as "pre-OR'd conditions," but `SwitchTransformer.extractSwitches` computes `thenCond = cond2 & prevCond` and `elseCond = !cond2 & prevCond`. That source behavior is path-gating with conjunction, where `prevCond` represents the prior else path.

Question: was "pre-OR'd" shorthand for a different downstream representation, or should the spec consistently describe these selectors as path-qualified AND-gated conditions?

Source: `src/spatial/transform/SwitchTransformer.scala:52-70`
Blocked by: author confirmation
Status: open

## Q-pp-08 — [2026-04-24] Direct consumers of `hotSwapPairings`

`SwitchOptimizer.markHotSwaps` writes `mem.hotSwapPairings`, and the metadata comment says it suppresses RAW-cycle complaints for squashed if/else-if chains. Direct source reads found during this pass-entry write are `MemoryUnrolling.substHotSwap` and `modeling.protectRAWCycle`.

Question: is there a codegen or banking consumer that reads this metadata indirectly, or should the Switch spec call it retiming/modeling metadata rather than codegen/banking metadata?

Source: `src/spatial/transform/SwitchOptimizer.scala:16-30`, `src/spatial/metadata/memory/MemoryData.scala:67-78`, `src/spatial/transform/unrolling/MemoryUnrolling.scala:306-309`, `src/spatial/util/modeling.scala:474-483`
Blocked by: wider source audit / maintainer confirmation
Status: open

## Q-pp-09 — [2026-04-24] Is `PerformanceAnalyzer` still active?

`PerformanceAnalyzer` writes `lhs.latency` and `lhs.II` from `nestedRuntimeOfNode`, and it supports rerun through `RerunTraversal`. The canonical `Spatial.runPasses` chain constructs `RuntimeModelGenerator` directly but does not construct or invoke `PerformanceAnalyzer`.

Question: is `PerformanceAnalyzer` an older runtime-cycle estimator left for DSE experimentation, or is it invoked outside `Spatial.runPasses` in a path not covered by the pass-pipeline note?

Source: `src/spatial/traversal/PerformanceAnalyzer.scala:11-98`, `src/spatial/traversal/RerunTraversal.scala:6-13`, `src/spatial/Spatial.scala:76-88`, `src/spatial/Spatial.scala:154-155`, `src/spatial/Spatial.scala:180-182`, `src/spatial/Spatial.scala:233-235`
Blocked by: broader DSE/runtime-model audit
Status: open

## Q-pp-10 — [2026-04-24] Stub and optional cleanup passes in HLS

`TextCleanup` deletes accelerator-scope `DSLOp`s with `canAccel=false` only under the optional `textCleanup` flag, while `StreamConditionSplitTransformer` currently delegates directly to `super.transform` without adding behavior. Both are present in source but have ambiguous importance for a Rust+HLS compiler.

Question: should HLS planning preserve these as named passes for pipeline parity, collapse them into frontend cleanup, or drop `StreamConditionSplitTransformer` until it has semantics?

Source: `src/spatial/transform/TextCleanup.scala:9-20`, `src/spatial/Spatial.scala:176`, `src/spatial/Spatial.scala:361-362`, `src/spatial/transform/StreamConditionSplitTransformer.scala:7-11`
Blocked by: HLS pipeline design
Status: open

## Q-pp-11 — [2026-04-24] HLS treatment of Spatial iteration-diff analysis

`IterationDiffAnalyzer` computes `iterDiff` and `segmentMapping` from Spatial affine matrices and a Spatial-specific notion of ticks, lane distances, and accumulation cycles. HLS tools may serialize or pipeline loop-carried dependencies differently, especially when arrays are partitioned or when dependence pragmas are emitted.

Question: should the HLS reimplementation carry over Spatial's `iterDiff` algorithm exactly, use it only for diagnostics, or replace it with an HLS scheduler/dependence model?

Source: `src/spatial/traversal/IterationDiffAnalyzer.scala:17-169`, `src/spatial/traversal/InitiationAnalyzer.scala:23-41`
Blocked by: HLS scheduling design
Status: open

## Q-pp-12 — [2026-04-25] Crandall reference model vs staged rewrite

The rewrite spec request mentioned Crandall's algorithm "via `modifiedCrandallSW` from `utils.math`." Direct source verification shows `RewriteTransformer` imports Mersenne helper predicates from `utils.math` and implements the staged hardware rewrite as `crandallDivMod`, but it does not call `modifiedCrandallSW`. The software helper lives in `utils/src/utils/math/package.scala` as a reference/test implementation.

Question: should the spec describe `modifiedCrandallSW` only as a software reference model for the staged `crandallDivMod` rewrite, or is there a historical code path where the transformer used that helper directly?

Source: `src/spatial/transform/RewriteTransformer.scala:21-23, 55-88, 173-184`; `utils/src/utils/math/package.scala:73-100`
Blocked by: git blame / test history
Status: open

## Q-pp-13 — [2026-04-25] Streamify helper passes constructed but omitted from sequence

`Spatial.runPasses` constructs `earlyUnroller`, `accelPipeInserter`, `forceHierarchical`, and `dependencyGraphAnalyzer` as lazy vals, but the current `streamify` sequence only includes `dependencyGraphAnalyzer`, `initiationAnalyzer`, `HierarchicalToStream`, `switchTransformer`, `pipeInserter`, and checks/dumps. The sequence name still includes `PreEarlyUnroll`, which makes the omission especially ambiguous.

Question: were `EarlyUnroller`, `AccelPipeInserter`, and `ForceHierarchical` intentionally retired from the streamify chain, temporarily disabled, or accidentally omitted?

Source: `src/spatial/Spatial.scala:123-126, 144`; `src/spatial/transform/streamify/EarlyUnroller.scala:19-292`; `src/spatial/transform/streamify/AccelPipeInserter.scala:7-20`; `src/spatial/transform/streamify/ForceHierarchical.scala:7-14`
Blocked by: git blame / streamify test cases
Status: open

## Q-pp-14 — [2026-04-25] Commented-out streamify files status

`FlattenToStream.scala` is line-commented from the package declaration onward and appears superseded by `HierarchicalToStream`. `StreamingControlBundle.scala` is not literally entirely commented out: the package/import header is active, but the object and case-class definitions are commented.

Question: should the spec treat both files as retired design drafts, or does the active package/import header in `StreamingControlBundle.scala` have a build purpose?

Source: `src/spatial/transform/streamify/FlattenToStream.scala:1-43`; `src/spatial/transform/streamify/StreamingControlBundle.scala:1-29`; `src/spatial/transform/streamify/HierarchicalToStream.scala:151-838`
Blocked by: build/package behavior check
Status: open

## Q-pp-15 — [2026-04-25] AllocMotion lazy val without pipeline invocation

`AllocMotion` has concrete behavior for moving memories, counters, and counter chains to the top of outer `Foreach`/`UnitPipe` blocks, and `Spatial.runPasses` constructs `allocMotion` as a lazy val. The visible pass chain does not invoke `allocMotion`.

Question: is `AllocMotion` intentionally unused in the canonical pipeline, used by an alternate path not visible in `runPasses`, or stale?

Source: `src/spatial/Spatial.scala:118, 164-235`; `src/spatial/transform/AllocMotion.scala:11-58`
Blocked by: git blame / alternate pass entry-point search
Status: open

## Q-pp-16 — [2026-04-25] AccumTransformer II=1 contract location

The accumulator specialization spec describes `RegAccumOp` and `RegAccumFMA` as the II=1 accumulator replacement nodes. Source verification shows `AccumTransformer` replaces marked WAR-cycle writers with those nodes and Chisel codegen instantiates specialized accumulator modules, but `AccumTransformer` does not directly set controller `II` metadata.

Question: where is the II=1 guarantee formally enforced: in retiming/initiation analysis, in codegen's accumulator modules, or as an unstated convention on `RegAccum` nodes?

Source: `src/spatial/transform/AccumTransformer.scala:39-48, 96-122`; `src/spatial/node/Accumulator.scala:30-50`; `src/spatial/codegen/chiselgen/ChiselGenMem.scala:226-292`; `src/spatial/traversal/InitiationAnalyzer.scala:27-40`
Blocked by: codegen/runtime behavior check
Status: open
