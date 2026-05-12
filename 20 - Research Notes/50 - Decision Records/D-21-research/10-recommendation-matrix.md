---
type: "research"
decision: "D-21"
angle: 10
topic: "recommendation-matrix"
---

# D-21 Research: Recommendation Matrix

## Evaluation Frame

[[D-21]] decides schedule authority, not a scalar rename. Spatial already separates `userII`, selected `II`, and `compilerII` in metadata (`src/spatial/metadata/control/ControlData.scala:153-177`; `src/spatial/metadata/control/package.scala:832-839`). `InitiationAnalyzer` computes outer `compilerII` from child selected IIs and inner `compilerII` from block latency/interval, blackbox II, `iterDiff`, and latency before choosing selected `II` from sequenced override, user request, or `min(compilerII, latency)` (`src/spatial/traversal/InitiationAnalyzer.scala:14-41`). [[C0 - Retiming]] records the same formula and flags that backend-imposed II can differ (`10 - Spec/40 - Compiler Passes/C0 - Retiming.md:239-266`; `10 - Spec/20 - Semantics/70 - Timing Model.md:57-65`).

## Decision Matrix

| Policy | Correctness | Provenance | DSE compatibility | Cycle-model compatibility | Diagnostics | Migration cost | Future backend flexibility |
|---|---|---|---|---|---|---|---|
| Compiler-II-only | Low. It treats a Spatial estimate as target truth even though the model depends on Spatial cycles, `iterDiff`, and blackbox factors (`src/spatial/util/modeling.scala:107-124`; `src/spatial/traversal/InitiationAnalyzer.scala:25-40`). | Medium-low. TreeGen shows `compilerII != II`, but no HLS accepted mismatch (`src/spatial/codegen/treegen/TreeGen.scala:126-131`). | Medium pre-HLS, low post-report. The runtime model serializes selected `lhs.II`, but cannot consume D-08 report authority (`src/spatial/model/RuntimeModelGenerator.scala:261-284`; `20 - Research Notes/50 - Decision Records/D-08.md:47-90`). | Low. D-20 requires naming the II source (`20 - Research Notes/50 - Decision Records/D-20.md:50-65`). | Low. HLS user-II violations disappear. | Lowest. | Low. Backends must imitate Spatial timing or lie. |
| HLS-accepted-overwrites | Medium post-tool, low pre-tool. Accepted II is unknown before report parse (`20 - Research Notes/50 - Decision Records/D-21-research/02-hls-report-sources.md:17-35`). | Low. Overwriting `compilerII` or selected `II` destroys request cause. | Low for broad search. D-08 rejects reports/simulation as the hot-loop source for every point (`20 - Research Notes/50 - Decision Records/D-08.md:35-39`, `20 - Research Notes/50 - Decision Records/D-08.md:92-100`). | Medium only after reports; pre-report traces are ambiguous. | Medium. It catches final mismatch but hides who changed. | Medium. | Medium-low. Backend facts survive; compiler comparability does not. |
| Dual-record with reconciliation | High. It preserves `user_requested_ii`, `spatial_compiler_ii`, selected `II`, emitted `hls_requested_ii`, and nullable `hls_accepted_ii` as separate claims (`20 - Research Notes/50 - Decision Records/D-21-research/05-ii-reconciliation-schema.md:18-31`). | High. Evidence source, report id, parse status, fallback reason, and reconciliation status remain inspectable. | High. DSE can estimate before reports, then calibrate or override while keeping `Cycles` compatibility (`20 - Research Notes/50 - Decision Records/D-08.md:69-90`). | High. D-20 can label cycle-debug traces by II source (`20 - Research Notes/50 - Decision Records/D-20.md:54-65`). | High. It can report matched, accepted higher/lower, missing report, unmapped loop, or rejection. | Medium-high. Requires identity keys, parsers, and tests. | High. Backends add adapters without mutating compiler evidence. |
| Backend-native/no-contract | Low for the compiler contract. The flow cannot prove whether user or compiler requests were honored. | Very low. No stable II ledger means no D-06/D-08/D-20 cross-reference. | Low. DSE sees unlabelled or absent schedule facts. | Low. Cycle simulation cannot state the assumed issue interval. | Very low. Missing fields collapse into "tool did something." | Low initially. | Superficially high, practically low because cross-backend comparison is impossible. |

## Recommendation

Adopt **dual-record with reconciliation**. The contract should be a per-loop/controller schedule record keyed by stable compiler identity plus backend aliases. Required fields: `user_requested_ii`, `spatial_compiler_ii`, `selected_ii`, `hls_requested_ii`, `hls_accepted_ii`, `ii_reconciliation_status`, `latency_source`, report source, loop-mapping status, diagnostics, backend, tool version, and target profile. Before reports exist, `hls_accepted_ii = unknown`; after reports parse, accepted II becomes post-tool evidence, but must not mutate away the compiler estimate that produced the request (`20 - Research Notes/50 - Decision Records/D-21-research/04-overlap-d08-d20.md:10-20`).

This is the only policy that composes with overlapping decisions. [[D-08]] needs accepted II as calibration/report authority without breaking fast search (`20 - Research Notes/50 - Decision Records/D-08.md:47-67`). [[D-20]] needs the assumed II source for cycle-aware delay-line traces (`20 - Research Notes/50 - Decision Records/D-20.md:50-65`). [[C0 - Retiming]] says HLS should preserve `compilerII`, `userII`, `bodyLatency`, and latency composition while not porting Chisel delay-line timing as HLS authority (`10 - Spec/20 - Semantics/70 - Timing Model.md:63-65`).

## Rejected Alternatives

Reject **compiler-II-only** because it preserves migration comfort by converting a Spatial estimate into HLS truth. It is useful as a pre-HLS fallback and diagnostic baseline, not as accepted backend evidence.

Reject **HLS-accepted-overwrites** because it makes report data authoritative by erasing the causal trail. A higher accepted II should produce `accepted_higher`, not silently rewrite `compilerII` or selected `II`.

Reject **backend-native/no-contract** because it avoids schema work by removing the contract D-21 exists to define. It leaves DSE, diagnostics, delay-line debugging, and future backend comparison without a shared schedule ledger.
