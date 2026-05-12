---
type: "research"
decision: "D-10"
angle: 10
---

# Recommendation Matrix and Precision-Mode Schema

## Named Recommendation

**Recommendation D-10: Scalagen-Compatible Default with Declared Precision Modes.** Make `scalagen_f64_reclamp` the default Rust reference mode for v1, because the current spec already names Scalagen plus `emul` as the numeric reference and `Number` routes transcendentals through `Double` before rewrapping to the source format ([[20 - Numeric Reference Semantics]]; [[03-spec-open-question-survey]]). Add explicit precision-mode metadata so MPFR and synthesized-hardware matching can exist as opt-in verification modes, not silent changes to the oracle. This preserves compatibility while giving D-18 and D-19 a place to record intentional numeric divergence.

## Option Matrix

| Option | Compatibility | Format correctness | HLS/hardware fit | Cost and risk |
|---|---|---|---|---|
| **f64 Scalagen compatibility** | Best match to today's generated Scala: `Number.sqrt/exp/ln/pow/trig` call JVM `Math.*` on `toDouble`, then `FixedPoint`/`FloatPoint` reclamp ([[01-current-number-implementation]]; `emul/src/emul/Number.scala:97-156`). | Weak for wide custom floats and double-rounded for narrow floats, but those are current semantics ([[05-format-precision-effects]]). | Not a claim about hardware results. | Lowest risk for golden tests and Rust parity. |
| **MPFR/per-format exact** | Intentional semantic upgrade, not Scalagen parity. | Best mathematical oracle for arbitrary `FixFormat`/`FltFormat`; can avoid f64 loss and define rounding per target format. | Only indirectly related to synthesized IP. | Higher dependency, speed, and test-maintenance cost; requires D-18 packing policy. |
| **Synthesized-hardware matching** | Diverges from Scalagen whenever HLS/vendor IP differs. | Only as good as each unit's documented/observed behavior. | Best for bitstream correlation, but operation support is uneven: BigIP defaults throw, some simulator paths are TODO identity stubs, and Zynq/CXP bind Vivado IP with half/single/custom distinctions ([[06-hls-hardware-bigip-implications]]; [[50 - BigIP and Arithmetic]]). | High validation burden per tool/version/op/format. |
| **Hybrid selectable modes** | Default remains compatible while audits can expose divergence. | Allows exact and hardware modes where they matter. | Aligns with D-01 capability tiers: supported op availability is separate from precision oracle ([[D-01]]). | Moderate schema and reporting cost; best long-term posture. |

## Precision-Mode Schema

Record precision at both run level and per op, with per-op values overriding the run default:

```yaml
trans_precision_mode: scalagen_f64_reclamp | mpfr_per_format | hardware_matched | disabled
trans_backend: rust-libm | jvm-math-compatible | mpfr | hls-native | vivado-ip | hardfloat | custom
trans_algorithm: jvm_math_to_double_reclamp | correctly_rounded_mpfr | vendor_ip_v7_1 | newton_raphson_n | composed_exp_recip
compatibility_label: scalagen-compatible | exact-format | hardware-correlated | approximate | unsupported
mismatch_tolerance:
  metric: exact_bits | ulp | absolute | relative | application
  value: 0
supported_operation_set:
  - sqrt
  - recip_sqrt
  - exp
  - ln
  - pow
  - sin
  - cos
  - tan
  - sinh
  - cosh
  - tanh
  - asin
  - acos
  - atan
  - sigmoid
notes: "sigmoid and some reciprocal-sqrt lowerings may be composed, matching Scalagen emission."
```

For fixed-only internal helpers, include `log2` separately rather than pretending it is a public staged float op; the D-10 API survey found `Number.log2` only on `FixedPoint` and no staged `FltLog2` surface ([[02-api-scalagen-surface]]).

## Interactions

D-01 should answer whether an op is legal on a target; D-10 should answer which oracle validates its value. A Tier-1 HLS-native `sqrt` may be available by `hls::sqrt`, but its run record can still say `trans_precision_mode: scalagen_f64_reclamp` for simulator parity, or `hardware_matched` for post-synthesis correlation ([[07-hls-native-math]]). Tier-2 custom IP must declare `trans_backend` and `trans_algorithm` because otherwise an app cannot distinguish unsupported, approximate, and vendor-specific math.

D-18 is downstream of D-10 for floats: after any transcendental computes a real value, `FloatPoint.clamp` packing, including the `x > 1.9` subnormal heuristic, decides stored bits ([[20 - Numeric Reference Semantics]]; Q-145 in [[20 - Open Questions]]). MPFR mode is not complete unless it says whether it still uses Scalagen clamp or a cleaner packer. D-19 is the sibling arithmetic decision: FMA can be unfused for Scalagen compatibility or fused for HLS/Chisel precision (Q-146 in [[20 - Open Questions]]). Use the same `compatibility_label` vocabulary for FMA so reports do not mix compatible transcendentals with hardware-matched multiply-adds unnoticed.

## Synthesis Position

Choose the hybrid design, with **Scalagen f64 reclamp as the default and named precision modes as required metadata**. This keeps v1 Rust behavior faithful to the current reference, makes lossy f64 behavior explicit, and leaves a disciplined path for exact-format and hardware-correlation runs when D-18, D-19, and D-01 settle their adjacent policies.
