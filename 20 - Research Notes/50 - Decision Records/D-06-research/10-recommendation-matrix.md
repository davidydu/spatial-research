---
type: "research"
decision: "D-06"
angle: 10
---

# Recommendation Matrix And Migration Plan

## Recommendation

Choose the hybrid requested-II/model-report reconciliation path for v1, with an HLS dependence model as the destination. Exact reuse is too risky because `IterationDiffAnalyzer` is built around Spatial affine matrices, tick-space, lane-distance assumptions, and accumulation-cycle discovery (`src/spatial/traversal/IterationDiffAnalyzer.scala:28-33`, `src/spatial/traversal/IterationDiffAnalyzer.scala:63-71`, `src/spatial/traversal/IterationDiffAnalyzer.scala:107-168`). Diagnostic-only is safer but does not solve scheduling. The hybrid preserves Spatial's conservative signal without making old `iterDiff` metadata the HLS scheduler oracle.

`iterDiff` is authoritative today: metadata defaults to `1`, analysis writes per-memory/per-access values, and `InitiationAnalyzer` turns those values into `compilerII` and final `II` (`src/spatial/metadata/memory/package.scala:26-29`, `src/spatial/traversal/IterationDiffAnalyzer.scala:115-117`, `src/spatial/traversal/InitiationAnalyzer.scala:29-40`). Because controller `II` drives control-signal generation and runtime cycles, HLS needs separate requested, accepted, and diagnostic fields instead of overloading `II` (`src/spatial/metadata/control/ControlData.scala:153-177`, `models/src/models/RuntimeModel.scala:192-200`, `models/src/models/RuntimeModel.scala:334-337`).

## Compact Matrix

| Option | Correctness risk | Performance predictability | HLS tool fit | D-07/D-08/D-21 dependency | Implementation cost |
|---|---|---|---|---|---|
| Exact reuse | High. It ports TODO-covered assumptions about unknown bounds, writer/reader order, cross-hierarchy iterators, and lane corners into HLS authority (`src/spatial/traversal/IterationDiffAnalyzer.scala:36-56`, `src/spatial/traversal/IterationDiffAnalyzer.scala:63-71`). | Medium for Spatial parity, low for HLS reality: `ceil(interval / minIterDiff)` predicts compiler II before reports (`src/spatial/traversal/InitiationAnalyzer.scala:29-40`). | Weak. HLS tools may accept, relax, or reject requested II based on partitioning, resources, and dependence pragmas (unverified). | High. Needs D-07 banking, D-08 latency source, and D-21 accepted-II records (`20 - Research Notes/40 - Decision Queue.md:35-41`, `20 - Research Notes/40 - Decision Queue.md:91-93`). | Medium-high: port access matrices, cycle finding, segmentation, and II equation. |
| Diagnostic-only | Low because it stops short of authority. Unknown-bound warnings and loose/user-II behavior remain useful diagnostics (`src/spatial/traversal/IterationDiffAnalyzer.scala:42-53`). | Low. It explains risks but cannot predict throughput. | Good as lint, incomplete as scheduler. | Low-medium. D-21 still needs fields to avoid confusing `compilerII`, requested II, and accepted II (`20 - Research Notes/20 - Open Questions.md:2121-2126`). | Low: preserve analysis output and reporting only. |
| HLS dependence model | Medium during bring-up, lowest as final architecture. It models HLS-visible dependences, partitions, latencies, and reports directly (unverified). | High after calibration, because final cycles can use the same accepted II that reports and DSE consume. | Best. It aligns authority with the backend scheduler/reporting contract. | Very high. D-07 must define partition forms; D-08 must define cycle source; D-21 must define reconciliation (`20 - Research Notes/20 - Open Questions.md:1521-1526`, `20 - Research Notes/20 - Open Questions.md:1570-1575`, `20 - Research Notes/20 - Open Questions.md:2121-2126`). | Highest: new dependence graph, report parser, and validation suite. |
| Hybrid requested-II/model-report reconciliation | Medium-low. Spatial `iterDiff` requests conservative II and flags suspicious recurrences, but HLS accepted II becomes final truth. | Medium-high. Before synthesis, requested II gives a stable estimate; after reports, accepted II updates performance. | Strong. It mirrors existing mismatch reporting without pretending the pre-HLS estimate is final (`src/spatial/codegen/treegen/TreeGen.scala:126-131`). | Medium-high but staged: D-21 fields first, D-07/D-08 integrations later. | Medium: reuse enough analysis for requests, add report reconciliation, defer full model. |

## Coupling Notes

D-07 matters because banking search explores `N`, alpha, block factors, duplication, and buffer ports before memory instances are chosen (`src/spatial/metadata/memory/BankingData.scala:547-563`, `src/spatial/traversal/banking/MemoryConfigurer.scala:610-633`). Ignoring the final partition plan can misclassify port conflicts (unverified). D-08 matters because current DSE shells out to the Scala runtime model jar and parses `"Total Cycles for App"`; HLS needs a replacement source before report-backed II can guide search (`src/spatial/dse/DSEAnalyzer.scala:90-147`, `src/spatial/dse/LatencyAnalyzer.scala:35-46`). D-21 is the immediate schema dependency: Spatial distinguishes `compilerII`, user `II`, and final `II`, but HLS needs `requested_ii`, `hls_accepted_ii`, source, and discrepancy reason (`src/spatial/metadata/control/ControlData.scala:162-177`, `20 - Research Notes/20 - Open Questions.md:2121-2126`).

## Migration Plan

1. Freeze the Spatial baseline: preserve emitted `iterDiff`, `segmentMapping`, `compilerII`, and `II` for comparison, including reduce special cases where MemReduce writes `0` and Reduce writes `1` (`src/spatial/traversal/IterationDiffAnalyzer.scala:193-204`).
2. Add HLS scheduling metadata names before changing behavior: `spatial_iter_diff`, `spatial_compiler_ii`, `requested_ii`, `hls_accepted_ii`, `hls_report_source`, and `ii_reconciliation_status`.
3. In the first HLS backend, use Spatial `iterDiff` only for requested pipeline II and warnings. User II remains a request, not proof of acceptance (`src/spatial/traversal/InitiationAnalyzer.scala:37-40`).
4. After D-07, make the requested-II pass consume the HLS partition/banking plan rather than raw Spatial banking candidates.
5. After D-08 and D-21, parse HLS reports into accepted-II metadata and make DSE/runtime summaries prefer accepted II over requested II.
6. Replace the heuristic with a real HLS dependence model once reconciliation tests show the major mismatch classes: recurrence distance, memory-port conflict, operator latency, and pragma/tool override (unverified).

## Exit Criteria

D-06 is ready to close when every scheduled controller can report all three values: Spatial diagnostic `compilerII`, HLS requested II, and HLS accepted II. Mismatches should be visible in reports, not silently folded into `II`, matching the spirit of existing TreeGen mismatch display (`src/spatial/codegen/treegen/TreeGen.scala:126-131`).
