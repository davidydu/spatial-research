---
type: "research"
decision: "D-21"
angle: 6
topic: "risk-failure-modes"
---

# Risk and Failure Modes for II Authority

## Decision Risk Frame

D-21 is about avoiding a false single source of truth. Spatial already stores user-requested II, selected `II`, and `compilerII`; `CtrlOpt.set` writes `.II(n)` into `userII`, `InitiationAnalyzer` derives `compilerII` and selected `II`, and TreeGen already highlights `compilerII != II` mismatches (`/Users/david/Documents/David_code/spatial/src/spatial/lang/control/CtrlOpt.scala:18-22`; `/Users/david/Documents/David_code/spatial/src/spatial/traversal/InitiationAnalyzer.scala:14-41`; `/Users/david/Documents/David_code/spatial/src/spatial/codegen/treegen/TreeGen.scala:126-131`). HLS adds a fourth value: the tool-accepted II. The failure mode is not merely a bad label; it can corrupt [[D-06]], [[D-08]], [[D-20]], and [[70 - Timing Model]] by letting DSE, deadlock triage, performance prediction, user diagnostics, and tests talk about different schedules as if they were the same.

## Trusting Spatial Compiler II

Treating Spatial `compilerII` or selected `II` as authoritative has the best migration comfort and the worst HLS truth risk. It preserves current tests such as `FlatAffineAccess`, which asserts exact `x.II == 1.0`, and it respects explicit user syntax like `Pipe.II(1)` (`/Users/david/Documents/David_code/spatial/test/spatial/tests/compiler/InitiationIntervals.scala:81-84`; `/Users/david/Documents/David_code/spatial/test/spatial/tests/feature/control/ExplicitII.scala:5-19`). It also keeps DSE cheap because the runtime model already serializes `lhs.II` and uses `(cchainIters - 1)*II + L + startup + shutdown + dpMask` for inner non-sequenced controllers (`/Users/david/Documents/David_code/spatial/src/spatial/model/RuntimeModelGenerator.scala:261-284`; `/Users/david/Documents/David_code/spatial/models/src/models/RuntimeModel.scala:334-337`).

The risk is stale authority. `compilerII` is derived from Spatial latency/cycle analysis, `iterDiff`, blackbox pipeline factors, and user/sequenced overrides, not from an HLS scheduler (`/Users/david/Documents/David_code/spatial/src/spatial/traversal/InitiationAnalyzer.scala:25-40`; `/Users/david/Documents/David_code/spatial/src/spatial/util/modeling.scala:107-124`). If HLS can only achieve a higher II, DSE will over-rank a design, performance predictions will be optimistic, and tests will pass compiler metadata while synthesized hardware violates throughput expectations. If HLS achieves a lower II, the compiler may under-rank a good point. Deadlock analysis also becomes ambiguous because Chisel pressure logic uses `sym.s.get.II` to delay empty/full checks (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/chiselgen/ChiselGenCommon.scala:249-277`); using Spatial II to reason about an HLS dataflow schedule can invent or hide liveness failures.

## Trusting HLS Accepted II

The opposite policy makes parsed HLS reports final. This is the strongest post-tool performance source and matches [[D-08]], which says reports can carry accepted II and latency while simulation is better for validation and triage. It prevents user-II violations from being hidden: if a user requests II=1 and the tool accepts II=2 or rejects the loop, the artifact can say so.

The cost is timing and coverage. HLS accepted II is unavailable before synthesis/report generation, so broad [[40 - Design Space Exploration]] cannot depend on it for every candidate without breaking the existing worker/CSV/HyperMapper throughput contract (`/Users/david/Documents/David_code/spatial/src/spatial/dse/DSEThread.scala:109-151`; `/Users/david/Documents/David_code/spatial/src/spatial/dse/DSEAnalyzer.scala:286-360`). Reports can also fail to map cleanly back to Spatial controllers. A reports-only test policy would weaken pre-HLS regression tests and make simple compiler changes wait for tool runs.

## Dual-Record Reconciliation

Dual-record reconciliation is the lowest semantic risk. Keep `spatial_compiler_ii`, `user_requested_ii`, `hls_requested_ii`, `hls_accepted_ii`, report source, and `ii_reconciliation_status`, as proposed by [[D-06]] and [[D-08]]. DSE can rank with a labelled estimator or fallback before reports, then update or calibrate when accepted II is available. Performance prediction becomes explainable: every cycle number says whether it came from Spatial parity, HLS estimate, report exact, or simulation validation.

The main failure mode is implementation drift. Reconciliation only works if loop/controller identity is stable, report parsers distinguish `matched`, `accepted-higher`, `accepted-lower`, `tool-rejected`, and `unknown-report-format`, and tests cover mismatch cases. Deadlock triage improves because [[D-20]] can state which II source its cycle mode used, but only if queue/backpressure traces carry the same provenance.

## Tool-Default or No-Record Policy

Letting the HLS tool choose defaults and recording no II is the highest risk option. It is tempting for v1 because codegen can omit pipeline pragmas or trust tool messages, but it breaks the contract surface: user `.II` violations disappear, DSE sees either no cycles or unlabelled cycles, performance prediction cannot explain regressions, and tests cannot distinguish "Spatial estimate wrong" from "tool ignored request." It also destroys useful migration evidence from existing exact-II tests and stream kernels that force II=1 for scheduling reasons (`/Users/david/Documents/David_code/spatial/test/spatial/tests/feature/streaming/FilterStream1D.scala:87-96`; `/Users/david/Documents/David_code/spatial/test/spatial/tests/feature/streaming/FilterStream1D.scala:195-196`).

Recommendation for this angle: reject no-record, reject single-authority Spatial or HLS policies as complete answers, and require dual-record reconciliation as the risk control. Tests should include compiler-only II parity, user-II mismatch, accepted-II higher/lower, report-missing, DSE fallback provenance, and deadlock/timeout traces labelled by II source.
