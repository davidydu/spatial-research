---
type: "research"
decision: "D-17"
angle: 7
---

# Cross-Backend Provenance Schema

## Current Constraint

D-17 should make `Unbiased` portable by specifying provenance, not just math. Today the reference helper has only `bits`, `valid`, `fmt`, and `saturate`; it shifts four guard bits, computes a 1/16 remainder, draws `scala.util.Random.nextFloat()`, steps to `biased + 1` or `biased - 1` when the threshold fires, then wraps or saturates (`emul/src/emul/FixedPoint.scala:232-240`). The arithmetic surface reaches this helper through `*&`, `/&`, `*&!`, and `/&!` (`emul/src/emul/FixedPoint.scala:52-63`), and Scalagen emits those operators plus direct unbiased fixed casts (`src/spatial/codegen/scalagen/ScalaGenFixPt.scala:96-114`). [[20 - Numeric Reference Semantics]] calls Scalagen plus `emul` the bit-level reference and explicitly marks `unbiased` nondeterministic (`10 - Spec/50 - Code Generation/20 - Scalagen/20 - Numeric Reference Semantics.md:27-29`, `10 - Spec/50 - Code Generation/20 - Scalagen/20 - Numeric Reference Semantics.md:41-47`). [[D-09]] already recommends seeded stable stochastic rounding for Rust, but [[D-17]] owns the canonical cross-backend contract.

## Schema

Use one `rounding_provenance` object per compiled artifact, plus per-event IDs in debug/mismatch records:

```yaml
rounding_provenance:
  schema_version: "spatial.rounding.v1"
  rounding_policy: "seeded_stochastic_legacy_away"
  seed:
    mode: "explicit|fixed_default|auto_recorded|none"
    value_u64: "0x0000000000000000"
    scope: "program|kernel|op"
  algorithm:
    name: "spatial-unbiased-threshold"
    version: 1
    guard_bits: 4
    threshold_bits: 64
  signed_negative_behavior: "legacy_away_from_zero"
  stochastic_source:
    kind: "stable_event_hash|sequential_prng|hardware_lfsr|host_global_rng|none"
    version: "spatial-threshold-hash-v1"
  event_identity:
    static_op_id: "xNN"
    source_ctx: "file:line"
    dynamic_instance: ["controller", "iteration_vector", "invocation"]
    lane_or_element: "lane/index"
  backend:
    name: "rust-sim|scala-compat|hls|rtl"
    capability: "canonical|statistical_equivalent|legacy_nondeterministic|deterministic_only|unsupported"
    fallback: "none|reject|legacy_stream|deterministic_rne|host_rng"
    fallback_reason: ""
```

`rounding_policy` is the semantic label. For v1, prefer `seeded_stochastic_legacy_away`: preserve the four-guard-bit threshold law and the current signed negative branch, because line 238 steps negative `biased` values farther from zero. A future policy may choose `seeded_stochastic_symmetric` or `deterministic_rne`, but that must be a D-17 migration, not a backend-local optimization.

## Event Identity

Stable event IDs should be derived from existing IR identity plus dynamic context. Argon already issues monotonically increasing IDs through `State.nextId()` and wraps staged ops as `Def.Node(id, op)` (`argon/src/argon/State.scala:72-74`, `argon/src/argon/static/Staging.scala:28-31`). Codegen names nodes as `x$id`, so `static_op_id` can reuse the same identifier (`argon/src/argon/codegen/Codegen.scala:43-50`). Keep `source_ctx` as diagnostic provenance because symbols carry `_ctx` and `_name` fields (`argon/src/argon/Ref.scala:127-129`). `dynamic_instance` must include loop/controller invocation data; Scalagen counters are lane-vectorized and pass both iter values and valid bits to bodies, so `lane_or_element` is required for parallel lanes (`emul/src/emul/Counter.scala:15-21`; [[60 - Counters and Primitives]]). The canonical threshold is then a pure function of `(seed, algorithm.version, static_op_id, dynamic_instance, lane_or_element)`.

## Backend Rules

Rust simulator: implement `canonical` with `stable_event_hash`, require seed/algorithm in run metadata, and allow `legacy_stream` only as an explicit fallback for Scala debugging. Scala compatibility: current generated Scala is `legacy_nondeterministic` because it calls the seedless helper; compatibility can either add a context-aware `FixedPoint.unbiased` overload or emit a sidecar declaring `host_global_rng` with `seed.mode = none`. HLS lowering: the [[50 - BigIP and Arithmetic]] spec says the rewrite needs an explicit numeric policy, so HLS must either implement the stable threshold source or reject canonical stochastic rounding rather than silently selecting vendor deterministic quantization (`10 - Spec/80 - Runtime and Fringe/50 - BigIP and Arithmetic.md:55-57`). Hardware/RTL: Chisel already lowers unbiased fixed nodes to `Unbiased` rounding (`src/spatial/codegen/chiselgen/ChiselGenMath.scala:33-40`, `src/spatial/codegen/chiselgen/ChiselGenMath.scala:75-78`), Fringe documents `Unbiased` as LFSR stochastic rounding, and `fix2fixBox` adds PRNG low bits before shaving fraction bits (`fringe/src/fringe/templates/math/RoundingMode.scala:3-8`, `fringe/src/fringe/templates/math/Converter.scala:36-43`). A seeded LFSR is `statistical_equivalent` only if seed, enable/advance policy, and event mapping are recorded; otherwise it is a non-canonical hardware source.

## Recommendation

D-17 should standardize the schema above and require every backend artifact to declare capability and fallback. Default conformance is `seeded_stochastic_legacy_away` with `stable_event_hash`. Deterministic round-to-nearest-even can remain a named fallback or future policy, but any result produced under it must carry `fallback = deterministic_rne` and must not be compared as canonical stochastic parity. This keeps [[D-09]] replay guarantees, Scalagen compatibility, HLS lowering, and hardware stochastic sources visible in one audit trail.
