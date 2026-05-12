---
type: "research"
decision: "D-20"
angle: 10
---

# Recommendation Matrix

## Decision Frame

[[D-20]] asks whether Rust simulation should treat `DelayLine` as the current Scalagen value alias or as cycle-aware retiming state. The source split is explicit: `ScalaGenDelays` emits no code for constant delay lines and emits `val lhs = data` for non-constant delay lines (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/scalagen/ScalaGenDelays.scala:9-13`), while `ChiselGenDelay` lowers `DelayLine(delay, data)` through `DL(...)` and updates `maxretime` (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/chiselgen/ChiselGenDelay.scala:16-30`). The user API also creates delay lines through `retime(delay, payload)` and marks them `userInjectedDelay` (`/Users/david/Documents/David_code/spatial/src/spatial/lang/api/MiscAPI.scala:23-31`).

## Option Matrix

| Option | Strength | Problem | D-20 disposition |
|---|---|---|---|
| Value-only Scalagen-compatible | Matches Scalagen, Cppgen, Roguegen, and legacy functional goldens. Cheap and deterministic. | Cannot expose wrong shift-register size, switch-case alignment, flow gating, reset/init, or user `retime` phasing. | Recommend as Rust reference/default. |
| Cycle-aware shift-register | Models Chisel/RTL timing state and can debug explicit `retime`, retime gates, streaming phasing, and stale values. | Requires a full tick/flow/backpressure model; partial modeling gives false precision and can break Scalagen parity. | Add as opt-in diagnostic mode. |
| Dual-mode value-default plus cycle-debug | Preserves value reference while providing a labelled cycle model for retiming bugs and HLS-adjacent checks. | Requires provenance, fixtures, and careful D-15/D-21/D-22 boundaries. | Recommend. |
| HLS-report authority only | Avoids writing a shadow scheduler; HLS reports/co-sim decide timing. | Too late for pre-HLS debugging and cannot explain explicit `retime` intent or Chisel parity. | Use for final timing authority, not simulator semantics. |

## Recommendation

Adopt **Dual-Mode DelayLine Semantics With Value-Only Reference Default**.

The Rust reference simulator should default to:

`delayline_policy = compat_value_elided`

In this mode, every `DelayLine(size, data)` has the same functional value as `data`, matching Scalagen's alias behavior. This is the correct compatibility oracle for existing functional tests and for the vault's Scalagen reference contract. It also avoids pretending that a functional Rust simulator has a complete controller/stream scheduler just because it can store a shift-register array.

Add a non-default diagnostic mode:

`delayline_policy = cycle_shift_register_debug`

This mode should model `DelayLine` as explicit temporal state only when the simulator also owns the tick policy, flow/backpressure gating, reset/init behavior, and controller step ordering. It should distinguish `origin = user_retime | compiler_retime`, record `size`, `trace`, producer/consumer symbols, `fullDelay`, and the chosen cycle model. User-injected `retime` should be especially visible because source code requested temporal behavior, even though value-mode still aliases it away.

For HLS, use report/co-simulation reconciliation as timing authority. HLS lowering may elide compiler-inserted DelayLines and rely on pipeline pragmas/scheduler registers, or emit explicit static shift-register arrays where source `retime` must be preserved. Either way, the artifact should declare `delayline_policy`, `hls_timing_authority`, requested/accepted II, and fallback.

## Rejected Alternatives

Reject **cycle-aware as the default Rust reference**. It would contradict Scalagen parity and requires D-15/D-22-style flow and backpressure semantics that are not settled enough to be implicit defaults.

Reject **value-only as the only supported mode**. It is too blind for retiming bugs, explicit `retime`, and Chisel parity diagnostics; tests already include IR-shape retiming sentinels such as `SimpleRetimePipe` rather than just final-value checks ([[03-tests-apps-usage]]).

Reject **HLS-report-only for all debugging**. Reports are the final synthesis authority, but they do not replace a pre-HLS diagnostic model for source-visible retiming directives.

Reject **unlabelled DelayLine behavior**. A simulator result should say whether it is value-elided or cycle-aware before anyone compares values, traces, or HLS timing reports.
