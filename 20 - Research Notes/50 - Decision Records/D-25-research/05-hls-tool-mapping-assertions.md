---
type: "research"
decision: "D-25"
angle: 5
topic: "hls-tool-mapping-assertions"
---

# D-25 Angle 5: HLS Tool Mapping And Assertions

## 1. Semantic Anchor

The local contract is intentionally unsettled. The API stages `oneHotMux` and `priorityMux` as separate IR nodes (`src/spatial/lang/api/MuxAPI.scala:26-32`). `OneHotMux.rewrite` only handles easy cases: one selector, any literal-true selector, or identical values; it warns if more than one literal selector is true, then still picks the first literal-true value (`src/spatial/node/Mux.scala:21-35`). Dynamic multi-true cases are not rejected there. Scalagen then lowers `OneHotMux` to `List(...).collect{case (sel, d) if sel => d}.reduce{_|_}` with no zero-true fallback (`src/spatial/codegen/scalagen/ScalaGenBits.scala:30-37`). `PriorityMux` is distinct: ordered `if` / `else if` with invalid fallback (`ScalaGenBits.scala:39-45`). `FixedPoint.|` is bitwise OR and `Bool.|` is logical OR (`emul/src/emul/FixedPoint.scala:23-25`; `emul/src/emul/Bool.scala:5-8`); `FloatPoint` has arithmetic and comparisons but no `|` operator in its runtime class (`emul/src/emul/FloatPoint.scala:141-217`). The unit test encodes the same split: one-hot gold is OR of enabled entries, priority gold is first enabled (`test/spatial/tests/feature/unit/MuxTest.scala:20-33`). Chisel emission uses `Mux1H` for `OneHotMux` and `PriorityMux` for `PriorityMux` (`src/spatial/codegen/chiselgen/ChiselGenMath.scala:226-232`).

## 2. Lowering Choices

`or_reduce_masked_values` is the closest Scalagen compatibility mode: compute each `sel_i ? data_i : zero`, then OR-reduce raw payloads. It preserves current integer/fixed/bit behavior for multi-true inputs, including strange bit unions. It is a poor default semantic contract because it makes "one-hot" a misnomer and has no source evidence for floats beyond bit reinterpretation.

`priority_if_else_chain` is deterministic and matches `PriorityMux`, not `OneHotMux`. It should be used only when D-25 deliberately redefines multi-true `OneHotMux` as priority, or when an earlier pass rewrites ambiguous selectors to `PriorityMux`. Otherwise it silently changes current Scalagen results, as the test distinguishes OR gold from priority gold.

`assume_or_assert_onehot_then_or_reduce` treats OR-reduce as an implementation of a proved one-hot select. That aligns with the IR name, Chisel `Mux1H` shape, and the data-types spec warning that OR-reduction is only semantically valid when exactly one lane is true (`10 - Spec/20 - Semantics/50 - Data Types.md:58-59`). It also exposes zero-true as a bug: Scalagen's `reduce` has no invalid default.

## 3. Static And Runtime Checks

Synthesis-time static checks should upgrade the existing literal multi-true warning to an error outside compatibility mode. Also reject statically zero-true `OneHotMux` unless the op is replaced with a `PriorityMux` or an explicit invalid/default policy. Switch lowering already warns when no case or multiple literal cases are enabled before building `oneHotMux` (`src/spatial/transform/SwitchOptimizer.scala:65-79`), so D-25 can make the HLS backend stricter without inventing a new analysis surface.

Runtime simulation should have labelled modes. `compat_scalagen_or_reduce` returns the OR-reduced value and records contamination on multi-true; it should also reproduce the zero-true failure or report it as a structured compatibility error. `debug_assert_onehot` checks `popcount(selects) == 1` before value selection. `assert_collect` can continue after recording failures, but final values must be marked non-golden. Hardware precedent for reporting assertions is local: Chisel `AssertIf` routes failed conditions into breakpoint wiring (`src/spatial/codegen/chiselgen/ChiselGenDebug.scala:29-34`), not into value recovery.

## 4. HLS Capability And Fallback Policy

Unverified HLS: a portable backend should not assume every tool has a trustworthy native one-hot mux, synthesizable C `assert`, or optimizer assumption primitive. Declare target capabilities instead: `raw_bit_or_reduce`, `priority_chain`, `debug_failure_signal`, `synth_assert`, and `optimizer_assume_onehot`. If native one-hot support is absent, emit an unrolled masked OR tree after proof/check. If `synth_assert` is absent, checked HLS builds should emit an explicit failure flag or refuse the checked profile. If `optimizer_assume_onehot` is absent, release builds can still omit dynamic checks only with a manifest waiver or static proof recorded beside the artifact.

## 5. Recommended Contract

Adopt `onehot_checked_or_reduce_v1` as the default HLS contract: exactly one selector is true; after proof or a debug assertion, lowering may use OR-reduce or any equivalent mux network. Keep `compat_scalagen_or_reduce_v1` for regression readback, and make `priority_multi_true_v1` a separate opt-in policy that rewrites the operation to priority semantics. For each emitted mux, record selector count, data type, zero-true policy, multi-true policy, static proof source, runtime assertion mode, and target fallback. Float `OneHotMux` should be rejected unless the decision explicitly adds a raw-bit reinterpretation rule.
