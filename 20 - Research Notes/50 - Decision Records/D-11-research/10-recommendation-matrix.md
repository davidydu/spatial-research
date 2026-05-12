---
type: "research"
decision: "D-11"
angle: 10
---

# Recommendation Matrix and Mode Schema

## Decision Frame

D-11 should not pretend there is only one observable `breakWhen` behavior. ScalaGen lowers break-enabled unrolled loops to top-tested guards, either `while(hasItems_$lhs && !stopWhen.value)` or `cchain.takeWhile(!stopWhen.value)`, and emits the warning that Scala break occurs at loop end while `--synth` breaks immediately (`src/spatial/codegen/scalagen/ScalaGenController.scala:75-93`; [[01-scalagen-current-semantics]]). The public API and Chisel path point the other way: `Stream` and `Sequential` comments promise immediate break and reset-on-finish (`src/spatial/lang/control/Control.scala:41-56`), while Chisel reads the breaker register, connects reset to controller done, and drives `sm.io.break` (`src/spatial/codegen/chiselgen/ChiselGenController.scala:312-315`; [[02-chisel-rtl-hls-semantics]]). The open question records this as a mutually exclusive simulator choice, not a cleanup issue (`20 - Research Notes/20 - Open Questions.md:1863-1877`).

## Matrix

| Option | Legacy Scalagen parity | HLS correlation | User API comments | Test churn | Side-effect predictability | Implementation cost | D-03 compatibility |
|---|---|---|---|---|---|---|---|
| Scalagen end-of-iteration default | Best: reproduces the current Scala loop guard. | Weak: can commit post-break writes RTL would suppress. | Weak: contradicts "break immediately." | Lowest for Scala-emulation goldens, but risky for synth-oriented tests. | Simple rule, misleading hardware model. | Lowest. | Acceptable only if labelled as compatibility, because D-03 favors loud, explicit control semantics. |
| HLS/RTL immediate default | Weak legacy parity. | Best: follows `sm.io.break`, reset, and `~break` memory gating (`src/spatial/codegen/chiselgen/ChiselGenMem.scala:40-46`). | Best. | Medium: break-sensitive Scala goldens need triage; `Breakpoint.scala` already expects immediate suppression before later stores (`test/spatial/tests/feature/control/Breakpoint.scala:64-115`; [[05-tests-app-usage]]). | Good if the cut point is formalized. | Medium. | Strong: keeps structured `breakWhen` as the sanctioned replacement for unsupported raw `while` / early `return` in [[D-03]]. |
| Dual-mode with provenance | Good: keeps Scalagen mode available. | Good: HLS mode remains available and comparable. | Good if HLS is named default. | Lowest migration risk: tests can declare intent. | Best for audits because result provenance is explicit. | Medium-high. | Best: mirrors D-03's "reject or label semantic extensions" posture. |
| Diagnostics/error mode | Not a simulator policy by itself. | Strongest conformance guard. | Strong: warns exactly where comments and ScalaGen diverge. | High if strict is default; low if opt-in. | Best: detects post-break writes, enqueues, stores, and register updates. | Medium-high analysis cost. | Strong as an opt-in hard error; too strict as the only v1 behavior. |

## Named Recommendation

Recommend **HLS-Default Dual Provenance**: make `hls_immediate` the architectural default, keep `scalagen_end_of_iteration` as an explicit compatibility mode, and add a divergence diagnostic that can escalate to error in conformance runs. This preserves the source/API contract and the Chisel/HLS intent without deleting the old Scala oracle. It also aligns with [[06-policy-options]], which recommends dual mode with HLS-immediate as the default rather than making ScalaGen's documented mismatch the silent Rust contract.

The key nuance is that "immediate" should mean "future controller work and `~break`-guarded effects are killed once the break signal is visible," not "all source-later statements are retroactively invalid." Existing tests include both patterns: `Breakpoint` expects a store after the break assignment to be suppressed, while some dynamic workloads use a break write as part of normal completion or drain protocol ([[05-tests-app-usage]]). The simulator therefore needs an explicit side-effect cut point and diagnostics for programs whose result depends on the difference.

## Mode Schema

Represent the policy in every simulator result, test manifest, and mismatch report:

- `break_when_mode`: enum `hls_immediate`, `scalagen_end_of_iteration`, `dual_compare`, `diagnostic_only`.
- `break_when_reset`: enum `on_controller_done`, `manual_legacy`, `compare_modes`; default `on_controller_done` because API comments and Chisel `connectReset($done)` agree.
- `compatibility_label`: enum `hls_default`, `scalagen_compat`, `migration_compare`, `strict_conformance`.
- `divergent_side_effect_policy`: enum `commit_scalagen_iteration`, `kill_hls_guarded_effects`, `warn_on_divergence`, `error_on_divergence`.
- `break_when_provenance`: controller id, breaker register id, source span, lowering stage, and whether the breaker was user-authored or compiler-inserted by streamification.

## Adoption Notes

Default test generation should emit `compatibility_label = hls_default` and `divergent_side_effect_policy = warn_on_divergence` until the corpus is triaged. Legacy differential tests can opt into `scalagen_compat`, but their outputs should carry that label so they are not mistaken for HLS predictions. Strict HLS suites should use `error_on_divergence`, especially where a write to a breaker register is followed by memory, FIFO, stream, or ArgOut effects in the same controller body. This is compatible with D-03 because it keeps early exit inside structured Spatial controllers, keeps unsupported raw control flow out of v1, and makes any divergence an explicit mode decision rather than hidden host-language behavior ([[D-03]]; `src/spatial/lang/api/SpatialVirtualization.scala:103-114`).
