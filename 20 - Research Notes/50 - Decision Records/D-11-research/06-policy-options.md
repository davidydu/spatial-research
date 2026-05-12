---
type: "research"
decision: "D-11"
angle: 6
---

# Policy Options

## Decision Frame

D-11 asks whether the Rust simulator should match Scalagen's end-of-iteration `breakWhen` or synthesized immediate-break behavior (`20 - Research Notes/40 - Decision Queue.md:51-53`). Q-132 sharpens the problem: Scalagen emits `while(hasItems_$lhs && !${stopWhen.get}.value)` or `takeWhile(!stopWhen.value)`, and the source warning says Scala breaks at the end of the loop while `--synth` breaks immediately (`20 - Research Notes/20 - Open Questions.md:1863-1878`; `src/spatial/codegen/scalagen/ScalaGenController.scala:75-93`). The spec therefore treats this as a real divergence, not a naming issue: tests with `breakWhen` can observe different memory writes and register updates across backends (`10 - Spec/50 - Code Generation/20 - Scalagen/50 - Controller Emission.md:94-108`).

## Compatibility Default

The Scalagen-compatible option makes end-of-iteration the default. A loop iteration that sets `stopWhen` still completes its body; the next guard check prevents the following iteration. This matches the emitted Scala structure and `emul.Counter.takeWhile`, whose `continue` predicate is checked in the `while` condition before `func(vec, valids)` runs (`src/spatial/codegen/scalagen/ScalaGenController.scala:74-93`; `emul/src/emul/Counter.scala:24-32`). Its main advantage is test compatibility: existing Scala-simulator golden outputs and user workflows that have learned this behavior continue to pass (unverified). It also minimizes migration surprise for software-style debugging, where a loop guard at the top naturally lets the current body finish (unverified).

The cost is HLS correlation. Memory and write side effects after the `stopWhen` assignment remain visible in Rust simulation even if hardware would suppress or halt them sooner. Reset behavior is also less hardware-shaped: the simulator can model a normal loop exit, but it does not naturally express the Chisel path where `stopWhen` is read through the breaker's `rPort`, connected to `sm.io.break`, and `connectReset($done)` is emitted on the breaker memory (`src/spatial/codegen/chiselgen/ChiselGenController.scala:312-315`). This option is safest for legacy comparison, weakest for finding break-sensitive HLS mismatches.

## Immediate-Break Default

The HLS/RTL option makes immediate break the default. That better matches the Chisel state-machine contract: generated controllers OR break into backpressure/forwardpressure through `doneLatch`, wire `stopWhen` into `sm.io.break`, and leave breaker memories out of the "tie reset false" path so reset remains observable (`src/spatial/codegen/chiselgen/ChiselGenController.scala:306-315`; `src/spatial/codegen/chiselgen/ChiselGenMem.scala:200-206`). `UseAnalyzer` marks break memories as `isBreaker`, preventing unused-memory cleanup, and `BindingTransformer` refuses bindings that would hide break dependencies (`src/spatial/traversal/UseAnalyzer.scala:25-33`, `src/spatial/traversal/UseAnalyzer.scala:54-63`; `src/spatial/transform/BindingTransformer.scala:40-49`).

This policy gives the Rust simulator the strongest HLS-correlation story: side effects after the break point are treated as not committed, and reset of the break flag can follow the controller done/reset behavior. It also matches a user's hardware expectation that a break condition stops the controller promptly (unverified). The downside is legacy test churn. Break-heavy tests such as `Breakpoint.scala`, `StreamPipeFlush.scala`, `PriorityDeq.scala`, and `Rosetta.scala` use `breakWhen`, so any golden output that accidentally depends on the extra Scalagen iteration may change (`test/spatial/tests/feature/control/Breakpoint.scala:64-91`; `test/spatial/tests/feature/dynamic/StreamPipeFlush.scala:13-69`; `test/spatial/tests/feature/dynamic/PriorityDeq.scala:49-329`; `test/spatial/tests/apps/Rosetta.scala:560`).

## Dual Mode And Diagnostics

Dual-mode simulation exposes both policies, for example `compat_scalagen` and `hls_immediate`, with one named default. This is attractive because the two semantics are mutually exclusive in Q-132, but both are useful: Scalagen mode validates old tests, while HLS mode validates emitted hardware intent. The risk is user confusion if mode is implicit, inherited from build flags, or recorded only in logs (unverified). The mode must be part of the test artifact and mismatch report.

Diagnostic/error-on-divergent `breakWhen` is a stronger variant. Rust can run an analysis or shadow simulation that detects writes, enqueues/dequeues, register updates, or externally visible stream effects after `stopWhen` becomes true in the same logical iteration. In warning mode it reports "Scalagen and HLS differ here"; in strict mode it rejects programs whose result depends on the extra iteration. This has the best user-expectation story for new code because it refuses to bless ambiguous semantics (unverified), but it cannot be the only v1 behavior unless the test suite is triaged first.

## Recommendation Implication

Prefer **dual mode with HLS-immediate as the architectural default and Scalagen-compatible as an explicit legacy mode**. Add a diagnostic that flags post-break side effects, and allow strict error mode for HLS conformance tests. This preserves old test investigation without making Scalagen's known divergence the Rust simulator's silent contract. It also keeps reset behavior and memory/write side effects aligned with the Chisel/HLS path by default, while giving D-11 a migration lane for tests that intentionally encode the Scala simulator result.
