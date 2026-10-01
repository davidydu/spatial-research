---
type: deep-dive
title: "PY-R011 — Numeric lowering and intrinsic profiles"
topic: python-numeric-lowering-and-intrinsic-profiles
project: spatial-python
session: 2026-09-30
status: research-conclusion
source_files:
  - "spatial@e7a8f2f:argon/src/argon/lang/types/Num.scala:8-50"
  - "spatial@e7a8f2f:argon/src/argon/node/Flt.scala:22-94"
  - "spatial@e7a8f2f:emul/src/emul/Number.scala:79-155"
  - "spatial@e7a8f2f:emul/src/emul/FixedPoint.scala:232-240"
  - "spatial@e7a8f2f:src/spatial/codegen/scalagen/ScalaGenFltPt.scala:120-122"
  - "spatial@e7a8f2f:argon/src/argon/node/Fix.scala:133-155"
feeds_spec:
  - "[[20 - Python Numeric Contract]]"
  - "[[40 - Python Compiler and HLS Contract]]"
---

## Recommendation and evidence boundary

Adopt **StrictNum-v1** as the default: the fixed arithmetic of [[PY-R002 - Numeric and Reduction Semantics]], exact binary floating arithmetic with nearest/ties-even rounding, and mathematical intrinsics with the precise rules below. Adopt **SpatialPhilox4x32-10-v1** for explicit random streams. Offer **CertifiedTableMath-v1** as one explicit, deterministic approximation mechanism. Each hardware mapping must preserve the selected profile or fail with a capability diagnostic. These are research proposals requiring adoption, not implemented compiler support.

The semantic target remains generic `Fix(sign,I,F)`, `W=I+F>=1`, and `Flt(P,E)`, `P>=2,E>=2`, including fractional-only fixed formats, arbitrary widths, BF16, and custom floats. A target may accept a smaller certified set. Python owns format decoding, normalization, profile checking, reference execution, and certificate verification. Native libraries may supply independent test vectors or candidates; they do not decide language legality.

**Source facts.** Original `Num` includes power, exp, ln, sqrt, trig, hyperbolic/inverse functions, sigmoid, and numeric/stochastic casts. Helpers additionally implement reciprocal, reciprocal square root, floor/ceil, and fixed log2. Most use host Double math; sigmoid and reciprocal square root are typed compositions. Original floating power rewrites specialize several literal exponents, and nested reciprocal can cancel. Original Scalagen FMA is multiply followed by add. These are inspected source paths, not executed original behavior. (`spatial@e7a8f2f:argon/src/argon/lang/types/Num.scala:8-50`; `spatial@e7a8f2f:emul/src/emul/Number.scala:79-155`; `spatial@e7a8f2f:argon/src/argon/node/Flt.scala:39-73`; `spatial@e7a8f2f:src/spatial/codegen/scalagen/ScalaGenFltPt.scala:120-122`.)

Primary documents were accessed 2026-09-30. [SoftFloat Release 3e, interface dated 2018-01-20](https://www.jhauser.us/arithmetic/SoftFloat-3/doc/SoftFloat.html) supplies independent conventions for one-rounding FMA, after-rounding tininess, and nearest-integer remainder. The policies below are Spatial choices, including quiet comparisons and NaN-propagating min/max; this note does not assert complete IEEE conformance.

## Strict floating values and statuses

Use R002's encoding and gradual subnormals. The canonical arithmetic NaN has sign zero, all-one exponent, and only the highest explicit fraction bit set. An sNaN has a nonzero fraction with that quiet bit clear; `P=2` has no sNaN encoding. Arithmetic/numeric casts quiet NaNs to the canonical value. Bit reinterpretation preserves every bit; copy, negation, absolute value, copySign, and classification manipulate/test bits without quieting sNaNs or reporting invalid.

Status bits are `IV` invalid, `DZ` divide by zero, `OF` overflow, `UF` underflow, and `NX` inexact. Finite operations first compute the exact result, then round once. `NX` means that result differs from the returned finite value; finite overflow to infinity sets `OF|NX`. Detect tininess **after** rounding: a tiny inexact result sets `UF|NX`, while an exact subnormal sets neither. Normalization handles carries across exponent boundaries. No implicit global flags or rounding-mode state exists.

Default simulator status records are non-observable diagnostics: legal optimization may change their count. A proposed explicit `observed_fp` operation returns value/status and orders a status effect through a supplied resource; transformations must preserve it. Ordinary float arithmetic remains eligible for pure optimization when its numerical proof holds. Checked fixed overflow, fixed division by zero, and failing numeric conversions are language faults even with unused results; they cannot be eliminated or speculated. [[PY-R006 - Compiler Architecture and Framework Choice]] carries that distinction.

The following table is **proposed policy**. Numeric-valued computations with an sNaN operand give canonical NaN and `IV`; ordinary qNaN gives canonical NaN without `IV`, except an independently invalid FMA case. Comparisons return the Boolean result stated below. Other unlisted finite cases use exact arithmetic and the normalization/status rules above.

| Operation | Special cases and zero rule |
|---|---|
| add/subtract | Opposing effective infinities: NaN, `IV`. Exact cancellation: `+0`; `-0 + -0` is `-0`. Subtraction applies the sign change before this rule. |
| multiply | `0*Inf`: NaN, `IV`. Otherwise infinite/zero result sign is operand-sign XOR. |
| divide/reciprocal | `0/0`, `Inf/Inf`: NaN, `IV`. Finite nonzero divided by zero: signed Inf, `DZ`. `Inf/0`: signed Inf without `DZ`; finite/Inf: signed zero. Reciprocal is exact `1/x` with the same rules. |
| sqrt / reciprocal sqrt | Negative nonzero input, including `-Inf`: NaN, `IV`. `sqrt(-0)=-0`, `sqrt(+Inf)=+Inf`; reciprocal sqrt of signed zero is corresponding signed Inf, `DZ`, and of `+Inf` is `+0`. |
| FMA | Exact product plus addend, one final rounding. `0*Inf` gives `IV` even with a qNaN addend; infinite product plus opposite Inf also gives `IV`. Zero sign follows adding the exact signed product to the addend; opposing exact zeros yield `+0`. |
| min/max | Propagate any NaN, with `IV` only for sNaN. Same-sign zero pairs retain their sign; mixed-sign zero ties choose `-0` for min, `+0` for max. No numeric-NaN selection variant is silently substituted. |
| equality/order | Quiet comparisons: NaN makes equality and ordered comparisons false, inequality true; only sNaN sets `IV`. Signed zeros compare equal. Bit equality is a separate operation. |
| floor/ceil | Preserve signed zero and infinity; qNaN propagates. Finite results are mathematical integral values in the same float format; a zero result keeps the input sign, and fractional loss sets `NX`. |
| float-to-float / fixed-to-float | Exact numerical conversion then nearest/ties-even; widening finite values is exact. Numeric NaN conversion canonicalizes; bit transport preserves payload. |
| float-to-fixed | Multiply by the exact target scale, truncate toward zero, then range-check. Nonfinite/out-of-range input faults with invalid diagnostic, not floating `OF`. Explicit saturation maps infinities to extrema; NaN still faults. |
| fmod / remainder | Infinite dividend or zero divisor: NaN, `IV`. Finite dividend and infinite divisor returns dividend. Zero result keeps dividend sign. `fmod`: `a-trunc(a/b)*b`; `remainder`: `a-nearest_even_integer(a/b)*b`. These remainders are exact for same-format finite binary operands. |

For example, `fmod(7,2)=1`, `remainder(7,2)=-1`, and `remainder(6,4)=-2` because the halfway quotient `1.5` chooses even integer two. Floating `%` and `//` remain rejected pending an explicitly named contract.

## Mathematical intrinsics and executable limits

StrictNum-v1 evaluates each named mathematical function from the exact input values and normalizes its result once. Floating results use nearest/ties-even; fixed results use floor then the operation's declared wrap/saturate/check action. **Fixed reciprocal is the exception:** truncate the exact scaled `1/x` toward zero, matching fixed division. Its internal mathematical unit is not a typed literal, so fractional-only formats remain meaningful. Fixed negative sqrt/rsqrt, invalid logarithm/power/inverse-trig domains, and reciprocal of zero fault.

Single-round reciprocal sqrt and sigmoid deliberately revise the original typed compositions and extend R002's provisional wording. `sigmoid` means `1/(1+exp(-x))` as a mathematical function, not separately normalized negation/exp/add/division. A user-written composition still has its original per-operation rounding. Similarly, real `pow` differs from proposed `powi`: the latter requires representable typed one and uses binary exponentiation, starting at one, scanning nonnegative exponent bits from least significant upward, conditionally multiplying the accumulator and squaring the base between remaining bits. Negative `powi` exponents are rejected; use explicit reciprocal or real power. Do not rewrite real power to a rounded composition without proof.

These rules cover every original Num math member and the helper extensions. NaNs follow the preceding table before other identities, so `pow(qNaN,0)` is NaN, while `pow(0,0)=1`; this deliberately limits original constant rewrites.

| Intrinsic family | Mathematical domain and floating special values |
|---|---|
| exp; ln; log2 | `exp(-Inf)=+0`, `exp(+Inf)=+Inf`, `exp(0)=1`. Logarithms: signed zero gives `-Inf,DZ`; negative nonzero input gives NaN, `IV`; `+Inf` gives `+Inf`; log of one is `+0`. |
| sin/cos/tan | Finite real arguments; infinite argument gives NaN, `IV`. sin/tan preserve signed zero; cos of either zero is one. |
| sinh/cosh/tanh | sinh preserves signed zero and signed infinity; cosh of zero is one and either infinity is `+Inf`; tanh preserves signed zero and maps signed infinity to signed one. |
| asin/acos/atan | asin/acos require `abs(x)<=1`, otherwise NaN, `IV`; asin preserves signed zero. acos(1) is `+0`, acos(-1) is rounded pi. atan preserves signed zero and maps signed infinity to rounded signed pi/2. |
| sigmoid | Both zeros give exactly one half; `-Inf` gives `+0`, `+Inf` gives one. Finite input uses the real logistic function without intermediate exp overflow. |
| real pow | Finite negative nonzero base requires integral exponent; parity supplies result sign. Zero with negative exponent gives Inf, `DZ`; sign is negative only for `-0` and an odd integral exponent. Zero with positive exponent gives zero by the same sign rule; zero exponent gives one. For infinite exponent compare `abs(base)` with one: greater gives Inf/+0 for positive/negative exponent, smaller reverses this, equal gives one. Infinite base with finite nonzero exponent gives Inf/zero according to exponent sign; negative infinite base still requires integral exponent. |

Exact division and reciprocal use integer quotient/remainder with guard information. Sqrt and rsqrt can compare squared rational rounding boundaries with the input, including exact midpoint equality. Integral/rational power can compare integer powers against candidate boundaries. These routes can terminate with exact integer decisions; vendor reciprocal accuracy is a different question.

Transcendentals need certified directed rational intervals. A proposed reference algorithm family uses pi/log-two bounds for range reduction, rational series with explicit remainder bounds, and increasing precision until both interval endpoints normalize to identical output bits. Exp stores `2^k * exp(r)` as a significand interval plus a separate integer exponent. Trig reduction must determine the quadrant from certified pi bounds even for huge arguments. Log decomposes the input's binary exponent/significand; sigmoid chooses a stable signed branch. Intermediate precision/exponent state is independently sized: no small fixed lattice can hold every argument or result.

**Strong limitation:** this study has not constructed or proved such a library. Increasing precision alone does not establish a usable worst-case bound near a rounding midpoint, or resolve equality automatically. Recognized exact identities/algebraic midpoint cases need separate handlers. Every accepted format/domain requires a certificate covering reduction error, series/polynomial error, final rounding decisions, unresolved hard cases, and maximum precision/iterations/storage. Reference budget exhaustion returns a tool resource-limit outcome with the operation/span; it supplies no fabricated result and is not a program arithmetic fault. Hardware acceptance additionally requires a finite implementation bound, possibly a certified hard-case table. Fixed exp/power can require enormous integer precision even when final wrapping uses few bits; their admitted ranges must account for that cost.

**CertifiedTableMath-v1** is the explicit approximation route with a concrete executable boundary. A manifest enumerates a finite accepted input-bit tuple set, intrinsic, format, exact output bits, version, and canonical content hash. Python executes that table, including its stated domain guard. Approximate entries require the exact real result inside the destination's finite numeric range and two finite representable neighbors bracketing it; an exactly representable result has only one permissible entry. Fixed entries require both unwrapped neighbors inside the numeric range. Outside that range, entries must equal exact StrictNum normalization, including its overflow action; an Inf neighbor does not authorize choosing max-finite versus Inf freely. Specials/domain errors also follow StrictNum. The table selects one neighbor once; downstream CSE, branches, and FIFO effects use that deterministic value. Observed FP status is unavailable in this approximation profile v1.

This bound is per operation, not an end-to-end program accuracy claim. Outside a declared table domain, an explicit profile-domain guard faults before lookup; otherwise the compiler must prove membership. A complete unary F16 table needs at most 65,536 two-byte result entries, before certificates/statuses; a binary table can be vastly larger. ROM/multiplexed lookup is a concrete synthesis route subject to resource gates. Larger polynomial/vendor routes require an additional versioned Python bit algorithm and verified certificate; a vendor one-ULP statement alone neither determines the table nor proves membership in this stricter bracket condition. No unnamed fast-math mode is adopted.

## Random stream and stochastic consumption

Original stochastic rounding uses global Scala Random and an incorrect negative-neighbor rule; original floating Random is effectful. (`spatial@e7a8f2f:emul/src/emul/FixedPoint.scala:232-240`; `spatial@e7a8f2f:argon/src/argon/node/Flt.scala:92-94`.) Use the [Random123 v1.14.0 Philox definition](https://raw.githubusercontent.com/DEShawResearch/random123/v1.14.0/include/Random123/philox.h), accessed 2026-09-30, solely as a pinned algorithm source.

Proposed **SpatialPhilox4x32-10-v1** has a checked 64-bit seed, default zero, and an explicit unique 64-bit stream ID. Key words are seed low/high words; counter words are block ordinal low/high, stream ID low/high. Each block performs the ten rounds reproduced below. Output word order is 0,1,2,3; ordinal starts at zero. State includes key, stream ID, block ordinal, and word cursor; exhaustion faults before counter wrap. Allocating stream IDs is frozen source/builder composition, never Python object identity. These choices define reproducibility, not a cryptographic guarantee.

`rng_bits(k)` consumes `ceil(k/32)` successive words, joins them little-endian, returns the low k bits, and discards padding; require `k>0`. `uniform01(Flt)` takes `P-1` bits and returns exact `u/2^(P-1)`. Fixed uniform takes F bits; for F=0 it consumes one word and returns zero. Reject a destination unable to represent the entire sampled grid. Bounded integer sampling below N uses `bit_length(N-1)` bits with rejection until `<N`; N=1 consumes one word and returns zero, N<=0 faults before consuming. No successful-sample draw bound is certified: rejection may continue until the finite stream exhausts and faults. Hardware needs a resumable protocol and may backpressure, or must reject a requested success-latency guarantee without a proof. `random_scaled(max)` explicitly means typed `uniform01*max`, including its rounding; negative/nonfinite max faults before drawing.

Each fixed-width draw preflights its complete required word count against remaining stream capacity. If only two words remain, `rng_bits(96)` faults without consuming either. An admitted draw owns the stream while its helper computes/resumes; partial internal words/accumulator are retained, and result plus cursor advance commit atomically. Cancellation before that commit releases the pending draw without a cursor advance; later ordered draws cannot overtake it. A rejection sampler commits each completed attempt separately, so exhaustion on a later unsatisfiable draw retains all earlier rejected-attempt advances. Stochastic rounding uses the same atomic fixed-width draw rule before its separately ordered conversion/overflow result.

For stochastic numeric-to-fixed conversion, decode the finite source exactly. Write target raw value as `l+m/2^k`, with l=floor and a reduced dyadic fraction. Consume `ceil(max(k,1)/32)` words even when m=0; choose l+1 if the low k-bit U is `<m`, otherwise l. Apply the declared overflow action afterward. Nonfinite ingress faults before consuming; a checked overflow after selection retains the already committed RNG draw. For raw `-1.25`, choices are -1 with probability 3/4 and -2 with probability 1/4. This defines ordinary/unbiased/saturating combinations across fixed and finite floating inputs.

Those probabilities describe the threshold rule under an ideal uniform k-bit input. The adopted pseudorandom stream with a fixed seed/ID is deterministic; this research does not prove independent uniform draws or unbiased error for every seeded execution. Seed zero/stream zero starts with low two bits equal to one, so this particular -1.25 conversion selects -1. Exact replay and statistical-quality claims are distinct. An explicit external random-bit source can carry its own declared probabilistic assumptions.

Stochastic fixed multiply and divide round the exact operation result, not an already floored/truncated result. In destination raw units use `a*b/2^F` for same-format multiplication and `a*2^F/b` for division. Reduce its fractional part to `m/d` above floor l, with positive d and `0<=m<d`. For power-of-two d use the dyadic rule; otherwise draw an integer U uniformly below d through the specified rejection sampler and select l+1 iff U<m. An integral result consumes one word. Thus raw `1/3` rounds to one for accepted U=0 and zero for U=1 or 2; replacing d=3 by a two-bit threshold without rejection would change the nominal probability. Active zero division faults before a draw; saturation/checked overflow follows the selected raw result and preserves committed draw attempts. Rejection suspension/exhaustion follows the same stream protocol. These rules cover the original stochastic multiply/divide/cast families, with deterministic seeded replay and conditional ideal-uniform probability claims. Unbiasedness, under those assumptions, concerns the adjacent pre-overflow selection; wrapping or clipping can change the expectation of the returned numeric value.

Draws are exactly-once effects on a stream resource. Untaken branches/inactive lanes consume none; blocked continuations preserve captured draws. Sharing requires declared order; parallel independent lanes/tasks need explicit distinct streams or checked arbitration. Forking never silently copies a stream cursor. [[PY-R008 - Advanced State and Communication Protocols]] supplies continuation and effect-commit boundaries.

## HLS mappings and acceptance gates

**Source facts.** AMD's [UG1399 fixed-point summary, displayed 2025.2](https://docs.amd.com/r/2025.2-English/ug1399-vitis-hls/Fixed-Point-Identifier-Summary) says quantization/overflow settings apply on assignment/initialization, not every intermediate calculation. [Floats and doubles, displayed 2026.1](https://docs.amd.com/r/en-US/ug1399-vitis-hls/Floats-and-Doubles) describes partial compliance. [PG060 v7.1, displayed 2020-12-16, printed pages 4–6](https://docs.amd.com/v/u/en-US/pg060-floating-point) documents most operators flushing subnormal operands/results, treating sNaNs as quiet, accumulator rounding toward zero, and float-to-fixed nearest rounding. Its reciprocal/rsqrt/log/exp accuracy differs from basic arithmetic; supported custom widths are restricted and operation-dependent. The same PG060 edition, printed page 13, also excludes invalid status for zero-times-infinity FMA with a quiet-NaN addend, unlike the proposed StrictNum observed-status rule. These documents describe different releases, not one verified installed configuration. No vendor or original compiler execution occurred here.

Use [[PY-R009 - HLS Boundary and Control Lowering]]'s implementation plan. Numeric descriptors carry profile/version, format, overflow/rounding action, fault/status visibility, domain certificate, and selected helper/table/component hash. Meaning-bearing fields enter the checked semantic key; implementation and tool manifests also pin mapping/build versions.

| Family | Proposed lowering and mandatory checks |
|---|---|
| Fixed/integer arithmetic | Raw unsigned W-bit carriers plus explicit signed decoding. Add/sub/neg normalize each node; multiply computes widened product then floor-rescales; checked/saturating helpers inspect widened results before clipping/wrapping. An `ap_fixed` expression alone is insufficient. |
| Signed division/remainder | Divide unsigned magnitudes, restore sign for truncation, adjust quotient/remainder for floor. `/` computes `trunc(a*2^F/b)`; `//` computes `floor(a/b)*2^F`; `%` is `a-floor(a/b)*b`; rem is `a-trunc(a/b)*b`. Guard zero before issue. Handle signed minimum/-1 without native signed overflow. |
| Shifts/casts/ingress | Negative shifts fault; k>=W produces zero or sign fill as specified, using guards rather than undefined native shifts. Preserve exact literal tokens until Python checking. Each cast emits its own rescale, quantization, and overflow action; no destination-only rounding. |
| Generic floats | Python-generated integer/bit circuits decode/classify, align/normalize, retain guard/round/sticky information, round and repack with subnormals. Division/sqrt use bounded integer algorithms. Parameter widths and iterative/pipelined implementations require target resource limits. |
| Vendor floating operators | Accept only after bit/status compatibility, wrappers, or proven input domains. Subnormal/sNaN classification wrappers alone cannot repair finite underflow/cancellation errors: route those cases to an exact helper. A domain proof must cover results as well as operands. |
| FMA/reduction | Ordinary multiply/add has two rounding nodes; explicit FMA has one. Fixed wrap/floor fusion requires the R002 proof; saturation needs another proof. Materialize ordered folds or fixed trees with seed/empty/active guards. FP accumulator IP is not automatically a semantic replacement. |
| Strict/approximate math | Strict certified algorithms or finite tables; explicit approximation table plus Python lookup/certificate. Reject missing full-domain evidence, excessive table/precision/state, or impossible II/resource requests. |
| RNG/stochastic | Ten-round integer Philox circuit or sequential helper with explicit cursor/commit. Keep draws and fault guards in the effect protocol; preserve rejected bounded samples and exact negative rounding. |

As calculated expectations, integer `-3/2=-1, rem=-1`, whereas `-3//2=-2, %=1`; for `3/-2`, corresponding pairs are `-1,1` and `-2,-1`. A power-of-two arithmetic shift cannot implement truncating negative division without correction; the original rewrite exists at `spatial@e7a8f2f:argon/src/argon/node/Fix.scala:133-155`. Fractional `/` is not the integer quotient in the remainder equation: R002's `-1.5/2=-0.5` versus `rem=-1.5` must remain distinct.

## Review gates and remaining dependencies

The proposed rules now select defaults, floating special/status behavior, deterministic approximation ownership, RNG algorithm/cursor, and stochastic consumption. They do **not** establish a completed correctly rounded transcendental library, vendor compatibility, throughput, or hardware resource fit. Those are capability/certificate obligations. No optional legacy-fidelity compiler contract is assumed.

| Acceptance case | Required evidence before adoption/lowering |
|---|---|
| Small generic FP formats | Exhaust all encodings for classifications/unary/casts and bounded binary pairs; distinguish sNaN, qNaN, signed zero, subnormal carry and after-rounding tininess. |
| F32 special arithmetic | `0*Inf+qNaN` gives NaN/IV; `1/0` gives Inf/DZ; minimum subnormal times one stays exact; half minimum subnormal gives +0/UF/NX. |
| FMA and observed effects | R002's `0` versus `-2^-46` example; preserve checked unused faults and explicit observed status, permit ordinary diagnostic count changes. |
| Math boundary/certificate | Domains, ±Inf/zeros, pow identities/parity, exact midpoint handlers, hardest reduction/rounding inputs, reference budget exhaustion; no rounded result without proof. |
| Approximation-controlled FIFO branch | Exact manifest lookup determines branch and consumes; target must match that value/trace, not merely final-output tolerance. |
| RNG and suspension | Official vectors below; stream/cursor round-trip; padding/exact stochastic draws; inactive path consumes none; suspension never redraws; rejection state survives. |
| Hardware | Generated helper/adapter tests, C simulation, synthesis capability/resource/II checks, and RTL numeric/effect validation against Python. Vendor reports alone do not validate the semantics. |

Next work is to adopt/review these contracts, define the certificate schema and Python checker, implement exact core normalization, then admit individually certified math/table and target profiles. Full format descriptors remain representable before every target has an eligible implementation.

## Reproducible bounded probe

**Executed 2026-09-30:** the standalone Python calculation below matched all three [official v1.14.0 known-answer vectors](https://raw.githubusercontent.com/DEShawResearch/random123/v1.14.0/tests/kat_vectors), accessed the same date. It tests the proposed round/word convention, not a Spatial RNG integration or RTL implementation. Run with `python3`; no packages or original compiler are needed.

```python
MASK = (1 << 32) - 1

def philox(counter, key):
    c, k = list(counter), list(key)
    for r in range(10):
        p0, p1 = 0xD2511F53*c[0], 0xCD9E8D57*c[2]
        c = [(p1 >> 32)^c[1]^k[0], p1&MASK,
             (p0 >> 32)^c[3]^k[1], p0&MASK]
        if r != 9:
            k = [(k[0]+0x9E3779B9)&MASK, (k[1]+0xBB67AE85)&MASK]
    return tuple(c)

cases = [
    ((0,0,0,0),(0,0),
     (0x6627e8d5,0xe169c58d,0xbc57ac4c,0x9b00dbd8)),
    ((MASK,)*4,(MASK,)*2,
     (0x408f276d,0x41c83b0e,0xa20bc7c6,0x6d5451fd)),
    ((0x243f6a88,0x85a308d3,0x13198a2e,0x03707344),
     (0xa4093822,0x299f31d0),
     (0xd16cfe09,0x94fdcceb,0x5001e420,0x24126ea1))]
for counter,key,expected in cases:
    got = philox(counter,key)
    assert got == expected, (counter,key,got,expected)
    print(' '.join(f'{x:08x}' for x in got))
print('three_official_vectors_passed')
```

Observed output:

```text
6627e8d5 e169c58d bc57ac4c 9b00dbd8
408f276d 41c83b0e a20bc7c6 6d5451fd
d16cfe09 94fdcceb 5001e420 24126ea1
three_official_vectors_passed
```
