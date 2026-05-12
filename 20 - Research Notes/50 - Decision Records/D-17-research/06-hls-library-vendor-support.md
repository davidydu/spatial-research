---
type: "research"
decision: "D-17"
angle: 6
---

# HLS Library and Vendor Support for Unbiased Rounding

## Vendor Library Baseline [source]

Mainstream HLS fixed-point libraries make deterministic rounding cheap and explicit. AMD Vitis `ap_[u]fixed` exposes quantization modes including `AP_RND_CONV`, documented as nearest with ties forced to even, plus `AP_TRN` and `AP_TRN_ZERO` truncation modes ([AMD UG1399 quantization modes](https://docs.amd.com/r/en-US/ug1399-vitis-hls/Quantization-Modes)). Microchip SmartHLS `hls::ap_fixpt` has the same style of template quantization and overflow parameters, with examples using `AP_RND_CONV`, default truncation/wrapping, and assignment-time quantization ([SmartHLS user guide](https://microchiptech.github.io/fpga-hls-docs/2021.1.2/userguide.html)). Intel/Altera `ac_fixed<N,I,S,Q,O>` similarly makes `Q` the quantization mode and `O` the overflow mode, although the public docs point to the bundled AC datatype reference for the full mode table ([Altera HLS ac_fixed](https://docs.altera.com/r/docs/683349/24.1/altera-high-level-synthesis-compiler-pro-edition-reference-manual/declaring-ac_fixed-data-types?contentId=qohq2Nz_d5Dpm26aYhH~BA)).

None of those fixed-point type surfaces advertises stochastic rounding as a built-in quantization mode. For floating-point IP, the picture is even more deterministic: Intel floating-point IP documents only round-to-nearest-even as the supported IP-core rounding mode ([Intel floating-point IP rounding](https://www.intel.com/content/www/us/en/docs/programmable/683750/20-1/rounding.html)). Therefore deterministic RNE/truncation can be delegated to vendor/library types; stochastic `Unbiased` cannot be treated as a normal HLS type parameter.

## Stochastic Lowering Shape [source + inference]

Spatial's current `Unbiased` is stochastic, not convergent RNE. The Scala reference shifts away four guard bits, computes a 1/16-granularity remainder, draws `scala.util.Random.nextFloat()`, and steps farther from zero when `rand + remainder >= 1` before wrap or saturation (`emul/src/emul/FixedPoint.scala:232-241`; [[D-17-research/01-d09-handoff-scope]]). The Chisel/Fringe path is already hardware-shaped: `Unbiased` selects an LFSR-like `PRNG`, adds low PRNG bits before fractional shaving, and then applies wrap/saturate overflow logic (`fringe/src/fringe/templates/math/Converter.scala:32-44`; [[D-09-research/05-hls-hardware-implications]]).

[HLS inference] A portable HLS implementation should mirror that structure as a Spatial rounding primitive, not as vendor fixed-point assignment. Generate the full-width multiply/divide/cast result, add or compare against PRNG-derived discarded bits, shift to the destination format, then apply the chosen overflow mode. Intel/Altera does provide an FPGA-optimized RNG library with seedable uniform integer/float generators ([Altera HLS random library](https://docs.altera.com/r/docs/683349/24.1/altera-high-level-synthesis-compiler-pro-edition-reference-manual/random-number-generator-library?contentId=~VKAKqt_Yax0QVMy9q1lfA)), but relying on that library would make semantics vendor-specific. A local LFSR or counter/hash PRNG with manifest-recorded seed and algorithm is more portable.

## Area, Latency, and II Cost [inference]

Deterministic truncation is essentially a slice plus sign/zero handling. RNE/convergent rounding adds guard/round/sticky logic and a conditional incrementer; the cost scales with discarded-bit reduction width and destination width, but HLS tools normally pipeline it as ordinary add/compare logic. It should not require vendor IP or a DSP beyond the producer arithmetic.

Stochastic rounding adds state and replay policy. At minimum each independent stream needs PRNG registers, XOR/update logic, seed/reset plumbing, and either an adder of random low bits or a comparator against the discarded remainder. The stochastic rounding hardware literature frames the cost similarly: software SR is expensive because it needs a PRNG, masking/shifting, and addition, motivating hardware support for fixed-point multiplier outputs ([Mikaitis 2020](https://arxiv.org/abs/2001.01501)). [HLS inference] II=1 is feasible when the PRNG emits one word per valid operation and the random-add/compare stage is pipelined. The real risk is not throughput but determinism: a free-running PRNG advances on stalls and schedule changes, while a valid-gated PRNG preserves event replay but must be wired through pipeline enables. Per-lane PRNGs preserve independence under unrolling but area scales with lanes; shared PRNGs save LUTs/registers but introduce correlation and schedule sensitivity.

## Compatibility and Recommendation [recommendation]

D-01 compatibility favors a split contract. Deterministic rounding modes belong in the HLS-native library tier, like other fixed-point type behavior. Stochastic `Unbiased` should be a mandatory Spatial primitive only if D-17 canonizes stochastic semantics; otherwise it should be rejected or lowered only under an explicit compatibility mode, following D-01's reject/opt-in discipline.

D-10 compatibility is clean if rounding metadata follows the same provenance style as precision metadata: record `rounding_policy`, `rng_algorithm`, `seed`, and `advance_policy`, just as D-10 records transcendental precision mode and backend. Do not let a hardware-correlated stochastic run masquerade as `scalagen_f64_reclamp`.

D-19 is the main precision interaction. If FMA is unfused for Scalagen parity, `Unbiased` events occur at the multiply/cast boundaries Scalagen exposes. If HLS uses fused FMA precision, the rounding point changes and stochastic rounding after the fused result is a different distribution. D-19 must therefore name whether fused arithmetic also fuses stochastic rounding events.

Canonical recommendation: keep `Unbiased` as **seedable stochastic rounding**. Vendor RNE/truncation support makes deterministic replacement attractive for cost, but it would redefine an existing stochastic source and hardware contract. Deterministic RNE should be a separate named mode, not the canonical meaning of `Unbiased`.
