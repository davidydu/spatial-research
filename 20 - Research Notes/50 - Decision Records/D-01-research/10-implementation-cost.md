---
type: research
decision: D-01
angle: 10
---

## 1. Option A: Reject — Rust+HLS implementation cost, user-facing error path, static vs per-target unsupported set, risks.

`BigIP.scala` exposes 38 `def` lines: one helper, `getConst`, and 37 operation signatures. Because `divide`, `mod`, and `multiply` each have `UInt` and `SInt` overloads, the operation surface is 34 unique operation names. Sixteen operation signatures are abstract: signed/unsigned divide, mod, multiply, plus floating add, subtract, multiply, divide, and six floating comparisons. Twenty-one signatures have default bodies that throw `Unimplemented(op)`.

Reject is low implementation cost. The Rust+HLS compiler needs a support check before HLS emission and a diagnostic with op name, result type, target, and source location (inferred). The existing Scala error text already has the intended user-facing shape: "`op` is not implemented for the given target."

The cheapest support model is a static unsupported set matching the 21 default-unimplemented signatures: `sqrt`, trig/hyperbolic integer ops, `log2`, advanced floating ops, conversions, and `fltaccum`. Per-target unsupported sets cost more because target descriptions need a support matrix and diagnostics must know the selected target before rejecting. Static sets can be too conservative; per-target sets can drift from the Rust frontend or HLS emitter (inferred).

## 2. Option B: Preserve placeholders — cost estimate, what a placeholder looks like in HLS C++, does it compile, risks (silent wrong-answer bugs).

Preserve placeholders is the smallest codegen change if the HLS backend already knows result widths (inferred). Unsupported `UInt` or `SInt` operations can lower to typed zero expressions; unsupported `Bool` results can lower to `false`. In HLS C++, that means something like `ap_uint<W>(0)`, `ap_int<W>(0)`, or `false`, with inputs, `latency`, `flow`, and `myName` ignored (inferred). Returning the input would be ambiguous for `sqrt`, `sin`, `fexp`, conversions, and `fltaccum`; zero is the clearer placeholder (inferred).

This should compile if the backend can materialize width-correct constants and tolerate unused inputs (inferred). It is cheap for the 21 default-unimplemented signatures and scales cheaply because the fallback is uniform.

The operational risk is high. Placeholders preserve simulator compatibility per the candidate description, but HLS output can be silently wrong. This is especially sharp for conversion and accumulation paths: `flt2fix`, `fix2flt`, `fix2fix`, `flt2flt`, and `fltaccum` can affect representation or state, not just numeric quality. The maintenance cost shifts from implementation into debugging and user support (inferred).

## 3. Option C: Lower to vendor IP — cost estimate, how big is the IP map, per-target maintenance burden, pluggable-backend design implications.

Lowering to vendor IP is the largest implementation. The observed map is at least 34 unique operation names, or 37 entries if signed/unsigned overloads are modeled separately. The map is not flat: many methods carry `latency`, `flow`, `myName`, and floating format parameters `m` and `e`; conversion methods also carry fixed-point sign, decimal, fractional widths, `RoundingMode`, and `OverflowMode`. A registry entry therefore needs more than a vendor symbol: it needs signature adaptation, width rules, includes, pragmas, and target-specific latency behavior (inferred).

Per-target maintenance is substantial. Each backend must answer whether it supports integer IP, floating arithmetic, floating comparisons, transcendental functions, reciprocal/square-root variants, fused multiply-add, fixed/floating conversions, and accumulation. Some operations have likely vendor-library analogues; `fsigmoid`, `ftanh`, and `fltaccum` may require wrappers or macro pipelines rather than direct primitives (inferred).

This pushes the Rust+HLS port toward a pluggable backend boundary now: operation key, typed operands, format metadata, requested latency/flow, and an emitter result. That is useful long term, but every target adds mapping data and verification cases (inferred).

## 4. Hybrid options — Reject + opt-in IP, Placeholder + opt-in IP. Which combinations are sensible?

Reject + opt-in IP is the sensible hybrid. The default path rejects unsupported calls, while selected targets can register known-good lowerings for a subset of the 21 default-unimplemented signatures. This allows incremental vendor support without committing to a complete 34-name registry immediately.

Placeholder + opt-in IP is weaker. It is useful only when simulator parity is more important than hardware correctness, or for explicitly marked bring-up modes (inferred). If kept, placeholders should require an opt-in flag and emit warnings listing each placeholder op. Silent default placeholders are not a good production policy.

## 5. Recommendation — based purely on cost/maintenance trade-offs, which option is cheapest to ship in v1 of the Rust+HLS port?

Option A is cheapest to ship and maintain for v1. Option B is likely the fewest lines of initial code, but its silent wrong-answer failure mode creates downstream support cost. Option C is the most expensive because the map spans 34 unique names with target-specific parameter handling. Ship Reject as the default, preferably with a thin registry seam so specific vendor IP lowerings can be added later under an opt-in path (inferred).
