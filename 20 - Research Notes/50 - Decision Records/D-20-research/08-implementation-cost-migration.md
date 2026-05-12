---
type: "research"
decision: "D-20"
angle: 8
topic: "implementation-cost-migration"
---

# D-20 Research: Implementation Cost and Migration Plan

[[D-20]] is a cost decision because `DelayLine` has two existing meanings. ScalaGen treats it as a value alias: constants emit nothing and non-constants emit `val lhs = data` (`src/spatial/codegen/scalagen/ScalaGenDelays.scala:7-13`; [[60 - Counters and Primitives]]). Retiming and RTL treat it as timing state: `RetimingTransformer` recomputes per-block latencies, materializes `ValueDelay`s, and substitutes delayed inputs into consumers (`src/spatial/transform/RetimingTransformer.scala:205-220`; `src/spatial/metadata/retiming/ValueDelay.scala:13-18`; [[C0 - Retiming]]). Chisel then lowers delay lines through `DL(..., backpressure & forwardpressure)`, and Fringe exposes a flow-gated shift register (`src/spatial/codegen/chiselgen/ChiselGenCommon.scala:288-293`; `fringe/src/fringe/templates/retiming/RetimeShiftRegister.scala:8-21`; [[04-chisel-hls-backend-behavior]]).

## Cost Matrix

| Policy | Rust sim | HLS lowering | Tests | Reports and docs |
|---|---|---|---|---|
| Value-only default | Low. Implement `DelayLine(size, data)` as `data`, preserve the size-zero rewrite, and record `userInjectedDelay` only as provenance. This matches old goldens and [[05-simulator-semantics-options]]. | Low to medium if HLS also relies on scheduler registers instead of explicit shift-register code. The risk cost is high: user `retime(10, x)` becomes only a hint unless HLS reports prove equivalent timing. | Low for legacy parity, medium for guardrails. Existing tests mostly check final values or IR shape, such as `SimpleRetimePipe` counting three delay nodes (`test/spatial/tests/feature/retiming/SimpleRetimePipe.scala:14-23`; [[03-tests-apps-usage]]). | Low. Add `delayline_policy = compat_value_elided` to manifests and warnings that this is not cycle evidence. |
| Cycle-aware default | High. Needs a logical clock, per-delay queues/registers, reset/init values, flow gating, stalls, and alignment with controller issue policy. Without [[D-15]] and [[D-22]], it can manufacture false precision. | Medium to high. HLS must lower explicit retime state or emit pragmas/directives that force equivalent registers, then reconcile accepted II through [[D-21]]. | High. Requires trace fixtures for delays 0/1/3/10, automatic retiming, `retimeGate`, stream stalls, line buffers, and first-divergent-cycle expectations. | High. Reports must include delay identity, source automatic/user, size, producer, consumers, flow predicate, first active cycle, and timeout reason. Docs must explain divergence from ScalaGen. |
| Dual-mode | Medium-high. Keep `compat_value_elided` as default and add `cycle_retime_diagnostic` behind an explicit simulator policy. Shared IR/provenance work is real, but the cycle engine can start narrow. | Medium-high. HLS lowering can use value-only scheduling for automatic lines at first, while user retimes and selected diagnostics get explicit state or report checks. | High initially, then manageable. Every discriminator stores both value-only and cycle-aware expectations with policy labels. | Medium-high. More metadata fields, but the story is auditable: final-value success and timing success are different claims. |
| HLS-only timing | Low in Rust. The simulator elides delays and refuses to answer timing questions beyond provenance. | High. HLS, co-sim, and reports become the sole timing authority; all user retime intent, II acceptance, and pipeline latency must be recovered from tool artifacts. | Medium-high. Fewer Rust cycle tests, but more HLS smoke tests, report parsers, and tool-version fixtures. | High. Documentation must say "Rust is value reference only"; reports must carry `compiler_ii`, `hls_accepted_ii`, latency source, and delay-line reconciliation ([[70 - Timing Model]]). |

## Migration Plan

Phase 1 should choose `compat_value_elided` as the Rust default. This is the cheapest safe baseline: it matches ScalaGen, keeps current final-value goldens useful, and avoids claiming cycle accuracy before the simulator has a real flow model. Add a policy field to run manifests, goldens, and mismatch output: `delayline_policy`, `retime_source = automatic | user`, `delay_size`, and `timing_claim = value_only`.

Phase 2 should add report-only observability before adding cycle behavior. Reuse the shape of `RetimeReporter`, which already walks symbols, prints cycle membership, latencies, and found delay chains (`src/spatial/report/RetimeReporter.scala:11-60`). The Rust/HLS reports should list producer, consumers, size, automatic/user source, and whether the line was elided, explicitly lowered, or tool-scheduled.

Phase 3 should add `cycle_retime_diagnostic` as an opt-in lane, not the default. Start with explicit `retime` and a minimal automatic-retiming fixture, then add `retimeGate`, stream-starvation, and line-buffer boundary cases from [[03-tests-apps-usage]]. A mismatch should report "value matched, timing diverged" rather than failing as an ordinary value regression.

Phase 4 should wire HLS timing through [[D-21]]: requested II, compiler II, accepted II, latency source, and reconciliation status. Automatic `DelayLine`s can remain scheduling obligations; user-injected retimes need explicit lowering or an HLS proof artifact. Preliminary recommendation: dual-mode migration, with value-only as the compatibility default and cycle-aware diagnostics promoted only after D-15/D-21/D-22 stabilize.
