---
type: "research"
decision: "D-20"
angle: 5
---

# D-20 Angle 5: Simulator Semantics Options

## Frame

D-20 should separate value reference behavior from timing evidence. The current `DelayLine` node is a primitive with only one local rewrite: size 0 returns the original data (`src/spatial/node/DelayLine.scala:8-10`). ScalaGen then erases the timing effect: constant delay lines emit nothing and non-constant delay lines emit only `val lhs = data` (`src/spatial/codegen/scalagen/ScalaGenDelays.scala:9-13`; [[open-questions-scalagen]]). CppGen and RogueGen do the same value aliasing (`src/spatial/codegen/cppgen/CppGenDebug.scala:55`; `src/spatial/codegen/roguegen/RogueGenDebug.scala:33`). The hardware path is different: ChiselGen lowers `DelayLine(delay, data)` through `DL(...)` and records `maxretime` (`src/spatial/codegen/chiselgen/ChiselGenDelay.scala:16-30`), while the shared blackbox is a `STAGES`-deep register array that advances only when `flow` is true and resets to `init` (`resources/synth/vcs.hw-resources/RetimeShiftRegister.sv:22-39`).

## Option Comparison

| Option | Strength | Risk | Fit |
|---|---|---|---|
| Value-only elision | Matches today's Scala/C++/Rogue simulator behavior and keeps automatic retiming invisible to functional goldens. It is cheap, deterministic, and consistent with the [[C0 - Retiming]] HLS note that `DelayLine` is Chisel-specific, not a Vitis HLS primitive. | It cannot expose wrong flow gating, reset/init behavior, latency alignment, or user-injected `retime(delay, payload)` phasing. The API marks user retimes with `userInjectedDelay = true` (`src/spatial/lang/api/MiscAPI.scala:23-31`), and area/modeling can distinguish them (`src/spatial/targets/NodeParams.scala:41`), but the value simulator still aliases them away. | Best reference-value mode. Weak timing/debug mode. |
| Cycle-aware shift-register simulation | Directly models the existing RTL template: per-delay state, reset initialization, and advance on controller flow. It can test explicit retime use and can explain why Chisel values differ from value-only order under cycle inspection. | It is only honest if the simulator also knows the controller tick/flow policy. `RetimingTransformer` inserts and substitutes delay lines using `fullDelay`, `latencyOf`, cycle membership, and lazy `ValueDelay` creation (`src/spatial/transform/RetimingTransformer.scala:32-39`, `:68-87`, `:205-219`; `src/spatial/util/modeling.scala:570-648`). Without D-15's simulator-mode discipline, a shift register inside a serial block is fake precision. With D-22 unresolved, bounded stalls remain out of scope. | Useful validation mode, not the default semantic reference. |
| Dual-mode | Preserve `compat_value_elided` for old goldens and add `cycle_shift_register` or `retime_cycle_debug` for selected tests. Compare mode can report first final-value or trace divergence and whether the divergence is expected. | More implementation surface: every output needs `delayline_mode`, tick policy, reset/init policy, retiming-source version, and whether queues are elastic or bounded. | Best migration posture, mirroring [[D-15]]: compatibility stays available, while HLS-facing diagnostics stop pretending that value-only simulation proves timing. |
| HLS-only modeling | Skip `DelayLine` in Rust simulation and let HLS scheduling, reports, and co-sim establish timing. This aligns with [[C0 - Retiming]], where HLS relies on pipeline pragmas and scheduler-inserted registers rather than Spatial's retiming trio. | Too late for pre-HLS debugging and poor for explaining source-level retime intent. It also cannot replace D-21: Spatial computes `compilerII` and selected `II` in `InitiationAnalyzer` (`src/spatial/traversal/InitiationAnalyzer.scala:23-40`), but the HLS tool may accept, relax, or reject that request. | Good synthesis authority, bad standalone simulator semantics. |

## Interactions

D-15 matters because a cycle-aware delay line needs a meaningful notion of logical time. In `compat_scalagen_serial`, a `DelayLine` should remain value-transparent unless explicitly running a debug mode, because ScalaGen has no child scheduler or flow token. In `hls_semantic` or future bounded modes, delay advancement should be tied to the same deterministic parent/child step policy and blocked-reason diagnostics as `ParallelPipe` [[D-15]].

D-21 matters because shift-register simulation must not become a shadow HLS scheduler. It can validate phasing under an assumed `II`, but accepted II and final latency should come from report-backed fields such as `hls_requested_ii`, `compiler_ii`, `hls_accepted_ii`, `latency_source`, and reconciliation status [[D-21]]; [[D-08]]. A mismatch between `cycle_shift_register` and HLS reports is evidence for triage, not proof that reports are wrong.

## Preliminary Recommendation

Choose **dual-mode with value-only reference default**. Use `compat_value_elided` for functional regression and legacy ScalaGen parity. Add `cycle_shift_register` as an opt-in diagnostic mode for explicit `retime`, Chisel parity tests, and D-15 HLS-semantic simulations, but label it as a model of Spatial/Chisel retiming, not an HLS timing authority. For HLS, omit `DelayLine` lowering by default and rely on requested-II metadata plus D-21 report reconciliation for accepted II and latency. This keeps the old simulator honest, gives developers a way to debug retiming bugs, and avoids treating Chisel register insertion as the Rust/HLS reference semantics.
