---
type: implementation-blueprint
title: "Proposed numeric engine implementation blueprint"
scope: python-rewrite
project: spatial-python
date: 2026-10-01
status: reviewed
adoption_status: proposed
implementation_status: not-implemented
depends_on:
  - "[[20 - Python Numeric Contract]]"
  - "[[PY-R002 - Numeric and Reduction Semantics]]"
  - "[[PY-R011 - Numeric Lowering and Intrinsic Profiles]]"
---

## Authority, result, and evidence

> [!bug] 2 October 2026 — confirmed underflow defect
> The finite-output UF predicate in floating-core step 5 and the recorded quantizer/oracle probes is incorrect at the minimum-normal boundary. [[09 - Fable Design Review#Confirmed numerical defect|The reproduced counterexample and correction obligation]] reopen this part of numeric readiness. The sqrt probe repeats the predicate by inspection. The algorithms and historical probe below are preserved pending repair; their agreement does not establish underflow correctness.

This is the implementation-readiness supplement to the proposed numeric contract, not professor adoption or production code. It fixes algorithms and records that R002/R011 deliberately left at the technique/certificate level. Python owns every semantic calculation and proof check. Native tools may provide independent vectors, and vendor implementations may become certified routes; neither determines language legality.

Read the complete R002/R011 special/domain tables with this blueprint. Full generic fixed/binary-floating formats and all original Num functions remain in scope. A target's finite capability domain and a reference run's resource budget are separate fields. A checked numeric node is representable without a hardware route. A reference resource limit reports unfinished computation, never a replacement arithmetic result or a language-domain fault.

The implementation-readiness review used research HEAD `b56a49630f22b204ab1a4f0c531adf3647ac1639` and reopened original `spatial@e7a8f2f7f776dd0c5ac7fc03f16b3ed4d97021f0`. Original `argon/src/argon/lang/types/Num.scala:30-50` enumerates the math/cast scope; `emul/src/emul/Number.scala:96-114,139-155` establishes the old Double-backed/composed routes; `argon/src/argon/lang/Fix.scala:76-87,117-129` establishes stochastic multiply/divide scope. Those old implementations are evidence of scope, not StrictNum oracles. The earlier [[04 - Independent Numeric Review]] remains dated corroboration. The new bounded probes below do not run Spatial, a production library, C++, RTL, or a vendor tool.

The analysis closes four method gaps: concrete intrinsic recipes and equality decisions; certificate rules/checker; an exact finite generic-float HLS fallback; and numeric operation/law/RNG records. Existing fixed formulas, contribution/fault order, Philox rounds, and rational stochastic probabilities remain the selected semantics.

## Module boundary and records

Use small modules with explicit contracts:

| Module | Inputs and result | Responsibility |
|---|---|---|
| `numeric/formats` | checked descriptor, normalized bits | validate format; bounds; sign/exponent/fraction classification; exact dyadic decode |
| `numeric/rational` | signed integers and positive denominators | normalized rational arithmetic; floor/trunc/ceil/nearest-even; integer log-two comparisons; integer roots |
| `numeric/fixed` | typed bits and operation attributes | declared raw calculation, rounding, overflow, exact fixed result/fault |
| `numeric/float_core` | typed bits and op ID | special dispatch; exact finite arithmetic; destination rounding; status |
| `numeric/math_intervals` | exact finite rational inputs, recipe version, budget | trusted interval recipes below; exact algebraic/identity cases; point derivation |
| `numeric/certificates` | data-only derivation and profile manifest | recompute proofs and finite-domain coverage; no submitted code execution |
| `numeric/random` | resource state and request captures | Philox words, atomic draws, committed rejection attempts, stochastic selection |
| `numeric/reductions` | checked regions, tree/law descriptor, invocation | reference contribution/combine sequencing, private state and publication |
| `lowering/numeric_helpers` | operation and admitted target record | bounded raw-bit helper graph or verified table/component route |

`FixType={signed:Bool,I:Index,F:Index}` satisfies I,F>=0 and W=I+F>=1. `FltType={P:Index,E:Index}` satisfies P,E>=2. `NumericValue={type_ref,bits}` has 0<=bits<2^storage_width; no host float, invalid-value sentinel, or implicit extra precision is stored. `ExactRational={numerator:Int,denominator:PositiveInt}` is reduced, denominator positive; sign of a floating zero is carried separately. A decoder may retain `Dyadic={sign,magnitude,exponent}` before materializing a rational, so enormous generic exponents can be budget-checked before allocating a shifted integer.

The parent artifact blueprint owns canonical encoding/hashing and profile references. The numeric record payload is closed:

```text
NumericOpSpec {
  op_id, operand_type_refs, result_type_refs,
  numeric_profile_ref,
  rounding: OperatorDefined | Floor | TowardZero | NearestEven | Ceil,
  overflow: Wrap | Saturate | Checked | FloatingNearestEven,
  status_visibility: Diagnostic | Observed | None,
  rng_resource_operand?, status_resource_operand?,
  math_recipe_ref?, point_certificate_ref?, target_capability_ref?,
  origin_span
}
NumericEvaluation = Value(bits, status_mask, point_derivation?)
                  | LanguageFault(code, origin_span, operand_bits, diagnostic_status_mask)
                  | ResourceLimit(operation, origin_span, budget_kind, usage)
```

Required IDs and matching rules are finite, versioned registry entries; an unknown ID rejects. Fixed arithmetic IDs include `fix.add/sub/neg/mul/div_trunc/div_floor/mod_floor/rem_trunc/abs/min/max/and/or/xor/not/shl/shr_arith/shr_logical/floor/ceil/sqrt/rsqrt/fma/eq/ne/lt/le/gt/ge`. Floating IDs include `fp.add/sub/mul/div/fma/sqrt/rsqrt/fmod/remainder/min/max/eq/ne/lt/le/gt/ge/floor/ceil`, bit-preserving `fp.neg/abs/copysign/classify`, and `num.cast/num.bool_to_numeric/bits.reinterpret`. Math IDs are `math.recip/exp/ln/log2/sin/cos/tan/sinh/cosh/tanh/asin/acos/atan/sigmoid/pow_real/powi`. Random IDs are `rng.bits/uniform01/bounded/random_scaled` and `fix.stochastic_mul/div/cast`. An observed operation is the same arithmetic ID with an explicit status-resource operand and value/status result; it consumes/produces the resource token exactly once. Comparison result type is Bool; every ordinary binary numeric operand has exactly the same numeric type. Unlike types require an explicit cast. FMA has three equal numeric operands. Surface generic sqrt/rsqrt resolves to the fixed/floating ID from its exact input type; it never invokes host math.

Shift counts, `powi` exponents and bounded-sampling N use a registered integral operand category. Runtime fixed integers require F=0; structural/runtime Index stays distinct from accelerator Int32. `num.embed_index` explicitly converts an Index to an integral fixed type with named checked/wrapping overflow. Arithmetic, stores and helper calls do not implicitly embed indices. Literal context flows only through literal-only trees or from an already typed numeric sibling, as R002 specifies; an assignment destination cannot recast typed operands. The source/checker blueprint owns the traversal and exact grammar.

## Exact fixed and ingress algorithms

Implement `decode_fix(bits)` as bits minus 2^W when signed and the top bit is set. `encode_fix(r,mode)` first compares the unbounded integer r with raw bounds; Checked faults if outside, Saturate clips, Wrap masks with 2^W-1. Return normalized bits. All arithmetic uses decoded raw integers; each node calls this helper once after its declared rounding.

For denominator d>0, `floor(n/d)` is Python integer `n//d`; truncation is `sign(n)*(abs(n)//d)`; ceil is `-((-n)//d)`; nearest-even uses floor k and remainder r=n-k*d, choosing k+1 iff 2r>d or 2r=d and k is odd. Normalize a negative divisor by negating both n and d first. Do not use host floating division. The R002 raw operator table supplies n,d for every fixed arithmetic/cast. Fixed floor/ceil respectively use floor(a/2^F)*2^F and ceil(a/2^F)*2^F. Saturating/checked attributes act after this calculation.

Fixed comparisons compare decoded raw integers (identical scale), and fixed min/max select the numerical operand. Explicit `fix.fma(a,b,c)` computes floor((a*b+c*2^F)/2^F) then one declared overflow action. Wrap/floor matches separate ordinary multiply/add by R002's proof; saturation/checked contraction has no such permission. Int4 saturating 7*7 followed by adding -7 returns zero, whereas single-final-saturation FMA returns seven. This explicit operation/mode distinction is a proposed descriptor refinement; an ordinary expression retains two operation/fault boundaries. `num.bool_to_numeric` maps false/true to exact zero/one, then destination normalization; a fixed destination requires an explicit overflow mode because fractional-only formats may not contain one. Float zero/one is exact. No reverse numeric-to-Bool truth conversion is inserted.

Decimal ingress parses sign, integral/fractional digits, and decimal exponent with the closed source grammar; form exact numerator digits and denominator 10^scale, reducing by gcd. Reject Bool through exact host type checks. Check fixed literal numeric range before floor; float literals use the core quantizer and reject finite-to-Inf ingress. Explicit binary-float ingress accepts only the pinned host binary-float category, extracts its exact ratio/sign/special classification, and records that already-rounded provenance. `from_bits` rejects excessive width rather than masking. Reinterpretation checks equal widths and returns identical bits.

`powi` is distinct from real power: require a representable typed numeric one and nonnegative integral exponent. Start at typed one; scan exponent bits least significant first; multiply accumulator if that bit is one; shift exponent; square base only if any bits remain. Each multiplication has normal typed rounding/overflow and its own fault boundary. This fixes order even for nonassociative fractional/float multiplication.

## Generic floating core and status

Let q=P-1, b=2^(E-1)-1, emin=1-b, emax=b, s=emin-q. Decode finite normal bits `(sign,e,f)` to `(-1)^sign*(2^q+f)*2^(e-b-q)`, and subnormal to `(-1)^sign*f*2^s`. Decode specials before finite arithmetic. Status bit positions are IV=1, DZ=2, OF=4, UF=8, NX=16. R011's canonical NaN, sNaN, signed zero, infinities and independently invalid FMA rules are mandatory dispatch; test independently invalid FMA even if another operand is qNaN. Bit-preserving copy/sign/classification operations never quiet sNaN; arithmetic/casts do.

The one rational quantizer is:

1. Save sign and handle exact zero with the operation's zero-sign rule. For positive n/d, find e=floor(log2(n/d)): start `bit_length(n)-bit_length(d)` and correct by one through an integer comparison with 2^e. No host logarithm.
2. If e>emax, return signed Inf, OF|NX. Otherwise choose quantum exponent t=max(s,e-q); compute exact u=(n/d)/2^t by shifting the numerator or denominator, then quotient k and remainder r.
3. Choose k+1 by the integer nearest-even rule. If rounding produces 2^(emax+1), return Inf, OF|NX. This includes the exact overflow midpoint H=max_finite+2^(emax-q-1): H rounds to Inf; values below H can still round to max-finite. There is no rule that every exact result above max-finite immediately overflows.
4. A rounded value below 2^emin encodes with exponent field zero; otherwise determine its new exponent and repack its P-bit significand, allowing carry. Preserve the input/result sign when rounding to zero.
5. For a finite output y, NX iff exact rational result differs from y; UF iff NX and abs(y)<2^emin, including zero. Exact subnormals set neither. Core overflow sets OF|NX. Domain/special tables set IV/DZ independently of these finite rules.

Add/subtract combine exact rationals, multiply multiplies them, divide forms a rational, FMA computes exact product plus addend before a single quantizer call. Fmod and remainder calculate the integral quotient by truncation or nearest-even, then exact a-q*b. Same-format finite binary remainders are representable exactly; the zero sign is dividend sign. Float floor/ceil return mathematical integral values in the same type; fractional loss sets NX and a zero result keeps input sign. Floating `%`/`//` stay explicitly rejected under the existing contract.

For `sqrt(x)` with positive exact x=n/d, compute e=floor(log2(x)), t=max(s,floor(e/2)-q). Find k=floor(sqrt(x)/2^t) using integer square root of the scaled rational's floor. Compare x exactly with `(k+1/2)^2*2^(2t)` to choose k/k+1, including parity on equality. NX iff the returned finite y satisfies y*y!=x. `rsqrt(x)` is the same algorithm on d/n, with NX iff y*y*x!=1. Sqrt has no approximate intermediate; rsqrt is one-round sqrt of reciprocal, not two rounded nodes. For fixed sqrt, raw floor is `isqrt(a*2^F)`; fixed rsqrt raw floor is `isqrt((2^(3F))//a)`, then the declared overflow action. Negative inputs and zero reciprocal-sqrt follow R011.

## Strict math recipes and convergence

These recipes are intentionally simple exact-rational algorithms. They establish a correct implementation path; faster polynomial/range-reduction libraries are later refinements requiring proofs. Each recipe builds a checked point derivation and refines until its interval lies wholly within one final rounding cell. Fixed floor must establish one unwrapped raw integer before wrap. Floating NX is decided by the complete equality rules below, not guessed from endpoint rounding.

Rational closed interval arithmetic uses exact endpoint addition/subtraction, four endpoint products for multiply, and reciprocal/division only when zero is excluded. Intersect only with a separately proved enclosing bound. A `ScaledInterval={lo,hi,binary_exponent}` means `[lo*2^k,hi*2^k]`; it prevents overflow from a huge exp result. A scaled value's comparisons and float rounding use integer exponent comparisons/shifted significands before materialization. Resource checks occur before every shift/product and rational-operation allocation.

Use deterministic refinement p=32,64,128,...; at stage p every requested constant/series has rational enclosure width <=2^-p unless the caller requests a smaller width explicitly. The implementation may round interval endpoints outward to a p-bit dyadic grid by exact floor/ceil to keep fractions small. Compute reductions at p, recompute them at the next stage if their integer choice is undecided, and never reuse an uncertified quotient/quadrant. For each series choose the smallest N>=1 whose stated rational tail <=2^-p, testing N in increasing order. This is a finite test, not an empirical error estimate.

### Trusted constants and series

For 1<=m<=2, z=(m-1)/(m+1), 0<=z<=1/3. Define

```text
L_N(m)=2*sum[j=0..N-1] z^(2j+1)/(2j+1)
0 <= ln(m)-L_N(m) <= 2*z^(2N+1)/((2N+1)*(1-z^2)).
```

The tail bound follows by replacing all tail denominators with 2N+1 and summing a geometric series. This selected series is [NIST DLMF 4.6.4](https://dlmf.nist.gov/4.6.E4); the explicit checker inequality is derived here. Set m=2 for ln2. Positive rational x is decomposed exactly as 2^k*m, 1<=m<2, using integer comparisons. Then ln(x)=k*ln2+ln(m); request each enclosure width <=2^-p/(abs(k)+1) so the combined width shrinks. `log2(x)=ln(x)/ln2`, using a positive ln2 enclosure. Recognize x=2^k first and return exact k.

For rational 0<=t<=1,

```text
E_N(t)=sum[j=0..N-1] t^j/j!
0 <= exp(t)-E_N(t) <= (t^N/N!)/(1-t/(N+1)).
```

All remaining term ratios are at most t/(N+1); the geometric bound proves the enclosure. The power series is [DLMF 4.2.19](https://dlmf.nist.gov/4.2.E19); its bounded rational tail is the proposed checker rule. For exp(x), certify a single integer k=floor(x/ln2) from the directed quotient interval; x=0 is handled exactly. Form r=x-k*ln2, intersect with the proved [0,1] enclosure, evaluate the monotone endpoint exp bounds, and return the interval times 2^k. Do not materialize 2^k merely to discover floating overflow.

For rational |t|<=1/2, the alternating atan partial sum A_N=sum[j=0..N-1] (-1)^j*t^(2j+1)/(2j+1) lies between A_N and A_N+(-1)^N*t^(2N+1)/(2N+1). The next term gives the exact remainder bound; handle negative t by oddness. See [DLMF 4.24.3](https://dlmf.nist.gov/4.24.E3). Define pi by the Machin identity `16*atan(1/5)-4*atan(1/239)`. Its identity check uses the rational tangent addition formula and the interval `3<pi<4` to choose the correct branch; pi proof records include both. A reviewer can rederive the identity: tan(2*atan(1/5))=5/12, tan(4*atan(1/5))=120/119, then subtract atan(1/239) to obtain tangent one, so that angle is pi/4 in its certified range.

For arbitrary rational atan input, use oddness. On [0,1/2] use the series; on (1/2,1] use pi/4+atan((x-1)/(x+1)), whose argument has magnitude <=1/3; on (1,+Inf) use pi/2-atan(1/x), recursively reducing the argument. Rational endpoint interval evaluation uses atan monotonicity. Exact zero is handled before this recipe.

### Trigonometric and inverse functions

Certify k=nearest_integer(x/(pi/2)) using directed pi bounds, requiring the quotient interval to lie in a single half-open nearest-integer cell. For nonzero rational x it cannot lie exactly on a half-integer boundary. Compute r=x-k*pi/2 and its exact rational interval, intersect with the proved [-1,1] enclosure (the exact |r|<=pi/4<1). Evaluate interval polynomials:

```text
S_N(r)=sum[j=0..N-1] (-1)^j*r^(2j+1)/(2j+1)!
C_N(r)=sum[j=0..N-1] (-1)^j*r^(2j)/(2j)!
|sin(r)-S_N(r)| <= rho^(2N+1)/(2N+1)!
|cos(r)-C_N(r)| <= rho^(2N)/(2N)!,  rho=max(abs(lo),abs(hi))<=1.
```

Use exact interval Horner evaluation; widen by the stated Taylor bound, whose real derivatives have magnitude <=1. The series are [DLMF 4.19.1–2](https://dlmf.nist.gov/4.19). Apply k modulo four to exchange/negate sine/cosine: sin maps to S,C,-S,-C; cos to C,-S,-C,S. Tan divides these enclosures only after its denominator excludes zero. Finite rational arguments cannot equal a nonzero integer multiple of pi/2; correct reduction and division eventually resolve. Zero sin/tan and zero cos are exact handlers. A large argument requires more pi precision, not a host remainder.

For asin, handle 0 and ±1 first; ±1 uses ±pi/2 enclosure. For abs(x)<1 use monotone atan of `x/sqrt(1-x*x)`, with sqrt rational intervals obtained by dyadic integer-root enclosure. For acos, handle ±1 first (0/pi). If x>=0 use `2*atan(sqrt((1-x)/(1+x)))`; if x<0 use `pi-2*atan(sqrt((1+x)/(1-x)))`. This avoids needless near-one subtraction. All intermediate operations are rational interval operations; only the final function result is typed-rounded. The principal real branches and endpoint values are supported by [DLMF 4.23](https://dlmf.nist.gov/4.23); these computational formulas follow by elementary half-angle identities.

To enclose sqrt(u) at dyadic resolution h=2^-p, compute j=`isqrt(floor(u*2^(2p)))`; return [j*h,(j+1)*h], or a singleton if j*j==u*2^(2p). For interval u use lower/upper endpoint sqrt enclosures. Refine whenever a denominator interval includes zero. This fully specifies the sqrt subroutine used by the inverse functions.

### Hyperbolic, sigmoid, and real power

Use exp intervals and exact rational operations: for a=abs(x), u=exp(a), v=exp(-a), sinh(x)=sign(x)*(u-v)/2, cosh(x)=(u+v)/2. Stable tanh is sign(x)*(1-w)/(1+w), w=exp(-2a). Stable sigmoid is 1/(1+exp(-x)) for x>=0 and exp(x)/(1+exp(x)) for x<0. Zero sinh/tanh, zero cosh, and zero sigmoid are exact handlers. Exp's scaled interval arithmetic prevents an intermediate host overflow; float overflow/underflow and fixed normalization happen once at the final result. The defining hyperbolic relations are [DLMF 4.28](https://dlmf.nist.gov/4.28). The logistic and stable branch formulas are the proposed mathematical definition, directly algebraically equivalent.

All finite real-power exponents are rational m/d in lowest terms, d>0. Handle R011 NaNs/zero/infinities/one/exponent zero before finite computation. Negative finite bases require d=1 and use exponent parity; no complex branch is introduced. For positive rational base A/B, form exact rational T=(A/B)^abs(m), swapping numerator/denominator for m<0. Use integer binary exponentiation with budget checks. The result is the positive d-th root of T. Perfect d-th roots of the reduced numerator and denominator decide whether the result is rational; otherwise it is irrational. Test integer roots by binary search in `[0,2^ceil(bit_length(n)/d)]`, comparing powers by repeated squaring with early stop when they exceed n. Return the exact rational root if both are perfect, and quantize it with all tie/status rules. This catches `pow(9,1/2)=3` and every rational rounding midpoint, rather than merely some named examples.

For an irrational root, start rational bounds `[0,max(1,T)]`; bisect, comparing mid^d with T by exact integer cross-products. Stop at a final rounding-cell certificate. Each refinement shrinks width, so it cannot become permanently stuck on a rational rounding threshold. The large exact T route can be optimized by comparing unmaterialized integer powers; that is optional, not a missing method. Budget exhaustion before forming T is a resource outcome; with sufficient resources T and each root test are finite. This algebraic route covers real pow for all finite typed inputs, instead of using a potentially double-rounded exp(log(x)*y) composition.

### Complete exactness and midpoint handling

Every finite typed input is rational. The following equality classification is part of the trusted recipe, so reference refinement is not a heuristic that may remain undecided at an exact boundary.

| Function | Exact rational-output handlers | All remaining admitted finite cases |
|---|---|---|
| reciprocal, div, core arithmetic, fmod/remainder, floor/ceil | compute the exact rational directly | no unresolved equality |
| sqrt/rsqrt | rational square/perfect-root or exact squared-boundary comparison | irrational algebraic result cannot equal rational output/midpoint |
| real pow | numerator/denominator perfect d-th-root test above | irrational algebraic root cannot equal rational output/midpoint |
| exp | x=0 gives one | nonzero rational input gives a transcendental result |
| ln | x=1 gives zero | other positive rational input gives transcendental result |
| log2 | x=2^k gives integer k | other positive dyadic input gives an irrational result |
| sin/tan; cos | x=0 gives zero; x=0 gives one | nonzero rational input gives transcendental result |
| sinh/tanh; cosh | x=0 gives zero; x=0 gives one | nonzero rational input gives transcendental result |
| asin/atan; acos | x=0 gives zero; acos(1)=0 | other real-domain rational input gives a nonzero transcendental result, including ±pi/2 and pi endpoints |
| sigmoid | x=0 gives one half | nonzero rational input gives transcendental result |

The relevant primary theorem is that exp(a) is transcendental for nonzero algebraic a; [Popescu, arXiv:2306.14352v2, Theorem 3.2 and its n=2 consequence](https://arxiv.org/html/2306.14352v2), accessed 2026-10-01, provides a proof of Lindemann–Weierstrass. The following consequences are independently derived here. If ln(x) were nonzero algebraic, its exponential x would be transcendental, contradicting rational x. Algebraic sin/cos(x) would make exp(ix) a root of a quadratic with algebraic coefficients; algebraic tan(x) would make exp(2ix)=(1+i*tan(x))/(1-i*tan(x)) algebraic. The hyperbolic analogues use exp(x) and exp(2x). Algebraic sigmoid(x) would make exp(-x)=(1-y)/y algebraic. A nonzero algebraic inverse-trig result would give transcendental sin/cos/tan of that angle, contradicting the algebraic input. These arguments cover negative and complex algebraic exponents used in the proof; the computed functions remain real.

For log2, suppose log2(x)=m/n in lowest terms. Dyadic x=A/2^k with odd positive A would imply x^n=2^m. Unique factorization requires A=1 and an integer power of two; conversely every such input is handled exactly. Thus there is no rational midpoint for the remaining inputs. No general algebraic-equality solver or Gelfond–Schneider assumption is needed.

Finite floating output values and their nearest-even boundaries, and fixed unwrapped integral raw boundaries, are rational. The exact handlers settle every possible equality; each remaining function has a result unequal to every such boundary. Convergent rigorous enclosures therefore eventually fit a single rounding cell for each fixed input. This is a pointwise termination proof with unbounded available resources, not a practical uniform precision/time bound. Real finite tan never has a pole at a rational input. Reduction quotients against pi/ln2 likewise cannot equal undecided integer/half-integer boundaries unless the handled input is zero. NX for the nonrational cases is always set when a floating numerical result is returned; exact rational cases compare with the returned value. UF/OF still follow the returned result/range rules, and specials follow R011.

### Huge fixed wrapping results and reference budgets

For fixed exp/pow/sinh/cosh under Wrap, final tiny width does not excuse loss of the integer part: floor(y*2^F) modulo 2^W needs the actual unwrapped floor or an equivalent modular certificate. The selected initial method obtains that floor from a certified interval, then masks. If exp is represented as `[l,h]*2^k`, endpoint floors at raw scale F must be identical; the relative enclosure may need roughly k+F bits to make its absolute width below one. Before materializing endpoints, the budget checks the required shift/limb bound. An excessive requirement returns ResourceLimit rather than max-finite, zero, saturation, or guessed low bits. With sufficiently large resources the above nonrational/equality proof guarantees a finite floor decision. This is expensive but an explicit complete method.

Checked/Saturate can stop as soon as the entire interval's rounded unwrapped output provably lies outside one bound; Checked returns the declared overflow fault, Saturate returns the bound. Do not use exact-value range instead of the operation's round-then-overflow rule. Floating exp can return Inf once its lower bound is >=H, or a signed zero once its upper bound is strictly below half-min-subnormal; a tie boundary still uses exact equality policy. Scale-only range shortcuts are separately checked derivation rules.

`ReferenceBudget={max_integer_bits,max_rational_ops,max_series_terms,max_refinements,max_certificate_nodes}` uses nonnegative finite machine-representable administrative counters. A named default is an execution configuration, not a semantic type limit. Check estimated result bit lengths before integer products/shifts/powers, count every rational operation/series term, and stop before exceeding a cap. A failed point computation retains prior program effects and committed RNG draws, but publishes no numerical result. Retrying is a new reference execution or resumed pure computation with an explicit larger budget; it cannot replay committed contribution effects. A complete profile's point proof must exclude ResourceLimit for its admitted domain and declared bound.

Reference math is a resumable helper: `NumericHelperState={request_id,method_version,typed_input_bits,recipe_pc,precision_stage,series_index,root_search_bounds,interval_accumulators,proof_nodes,budget_counters}`. `step(max_local_ops)` performs at most that many budget-checked rational/bit helper operations, then returns InternalProgress or Ready(value/proof), a numeric LanguageFault, or ResourceLimit. It retains all private counters/accumulators before yielding. An independent scheduler observation quantum/budget end returns an incomplete snapshot and can resume unchanged; it does not consume the numeric proof budget again or redo series terms. A strict refinement loop cannot be one opaque unbounded task call. Pending cancellation discards private numeric computation at the protocol's checkpoint; it never undoes a prior input consume or adds a cutoff inside a logical result commit. Primitive integer operations are themselves bounded by max_integer_bits; a target helper additionally has the statically bounded microstep schedule in its plan.

## Certificates and profile registry

Certificates are immutable data, never callbacks, Python source, pickles, or unvalidated self-reported error claims. Use a topologically ordered proof DAG, indices only to earlier nodes. Rational fields obey normalized numerator/positive-denominator invariants and the artifact's size limits. The fixed set of versioned proof rules is:

```text
exact_input_decode, rational_arithmetic, fixed_quantize, float_quantize,
special_case, exact_identity, sqrt_boundary, rational_power_root,
ln_series_tail, exp_series_tail, atan_alternating_tail,
machin_pi, exp_reduce, trig_reduce, sin_taylor, cos_taylor,
interval_add/sub/mul/div/scale/intersect,
atan_transform, inverse_trig_transform, hyperbolic_transform,
sigmoid_transform, root_bisection, exactness_class,
rounding_cell, overflow_cell, fixed_floor_cell, approximation_neighbor
```

Each rule has a closed parameter schema, operand-node IDs, and a claimed conclusion. `ProofNode={rule_id,parent_ids,parameters,conclusion}` permits only the tagged parameter cases below; rule-specific arity and fields reject missing/extra entries. Rational or bit values in a conclusion are claims to recompute, never trusted inputs. The checker recomputes every conclusion using exact integers/rationals and the fixed analytic inequality above; no imported endpoint, tail, 'exact' Boolean, midpoint decision, quadrant, or error bound is trusted. Transformation rules match the registered intrinsic and exact argument expression, so a valid ln proof cannot be attached to exp. `exactness_class` checks the function/input conditions and exact identity/perfect-root classification above; it does not accept arbitrary irrationality assertions. Analytic lemmas are trusted versioned numeric code/theorem facts with pinned tests and review, not proved by a producer-supplied floating calculation.

| Parameter tag | Closed fields and checker action |
|---|---|
| Input | input ordinal; decode the certificate's exact bits/type, no supplied replacement rational |
| Rational arithmetic / interval | registered arithmetic selector, parent IDs; add/sub/mul/div compute exact result/enclosure; scale has integer exponent; intersection names its separately proved bound parent |
| Series | exact rational argument parent, positive N; ln/exp/atan/sin/cos selector is fixed by rule ID; recompute every term and tail from the stated formula |
| Reduction | argument parent, pi/ln2 constant parent, integer k; recompute quotient enclosure and certify its floor/nearest-integer cell, then exact residual enclosure |
| Function transform | registered intrinsic/branch ID and argument parent(s); recompute the exact rational composition, domain and monotonic endpoint choice |
| Exact / algebraic | registered identity ID or root degree d with numerator/denominator parents and integer-root witnesses; recompute equality/perfect-root tests; no user theorem string |
| Quantize / cell | destination descriptor, rounding/overflow modes, exact/enclosure parent, claimed output bits; derive raw floor or both endpoint output bits plus sign; exactness uses the approved class/equality test |
| Approximation | output descriptor/bits, enclosing-result parent, neighbor-code pair; decode finite neighbor values, prove consecutive codes and exact bracketing, or require singleton/exact Strict result |

An interval straddling zero cannot certify the sign of a rounded zero from its numeric magnitude alone; require an exact zero handler or a sign enclosure, refining until resolved for every nonzero result. The producer never chooses zero sign to make endpoint outputs match.

```text
PointCertificate {
  schema_version, numeric_profile_ref, recipe_ref,
  op_id, input_type_refs, input_bits, output_type_ref,
  outcome: Value(output_bits,status_mask_or_unavailable)
         | LanguageFault(fault_code,diagnostic_status_mask),
  proof_nodes, final_outcome_node, final_exactness_node?,
  checked_cost_summary
}
MathProfileManifest {
  profile_id, version, recipe_ref, intrinsic_ids, format_refs,
  domain: ExplicitSortedBitTuples | CartesianBitRanges,
  mode: Strict | CertifiedAdjacentTable,
  point_certificates_or_checked_coverage_refs,
  deterministic_output_table?, observed_status_available,
  declared_reference_bounds?, target_helper_ref?, content_hash
}
```

To check a point: verify descriptors/input/output widths, profile and operation binding; recompute each proof node in order; derive final bits/fault/special case and status; compare to the record; recompute counters/max bit sizes; require final claimed budget >= the checked cost. The checked reference trace includes every attempted refinement stage, series term, integer allocation and arithmetic operation, not just the final proof's shortest DAG. A profile implemented by direct table lookup has its own bounded lookup trace rather than claiming the generation trace runs at lookup. Certificate verification itself has separate size/cost limits. Failure rejects the certificate/profile; it is never an alternative numerical answer.

For Strict tables, each output is the unique StrictNum rounded value and its status. For CertifiedAdjacentTable, the proof identifies the two finite representable neighbors surrounding the exact value and proves the chosen output equals one neighbor. An exactly representable result has a singleton permitted set. Fixed unwrapped neighbors must both satisfy the finite raw range. For results outside that admitted range or special/domain inputs, require the exact StrictNum result/fault rather than arbitrary clipping or an Inf/max-finite choice. Approximation v1 exposes no observed status. A point whose exact algebraic handler finds a midpoint still permits either enclosing neighbor only if the selected approximation profile allows that entry; Strict nearest-even remains unique.

The complete finite-domain generation algorithm is concrete: enumerate the declared input tuples in increasing unsigned-bit lexicographic order; classify/domain-dispatch each; compute the exact handler or refine the selected intervals until its point proof is obtained; choose the table's deterministic neighbor by an explicit producer policy; verify each point independently; serialize unique sorted keys; derive maximum checked point costs; verify coverage by merging the domain enumeration with the sorted keys. Recompute the final content hash. Cartesian ranges describe finite bit-code sets, not approximate real inequalities; forbidden/uninitialized encodings are explicit exclusions. Exhaustiveness takes resources but is decidable. A generation ResourceLimit leaves the profile uncertified; it does not erase that operation from the language.

A full-domain bounded HLS certificate needs this complete coverage or a separately checked structural proof with explicit finite loop/bit bounds. In the initial design, enumerate points; compressed analytic coverage is a future profile version. Unary F16 tables are finite; binary/F64/custom tables may be unreasonable for a target and fail its resource gate. No small table or bounded reference probe certifies F64/full generic widths. Reference point certificates and full-domain completion/target certificates are distinct schema variants, resolving R011's earlier ambiguous 'accepted format/domain' wording without weakening the strict definition.

## Generic numeric HLS fallback with finite widths

Use raw unsigned bit vectors and explicit sign decoding; HLS C++ native signed overflow, signed division/shift, host floating math and implicit `ap_fixed` expression rounding are not semantic helpers. For fixed add/sub/neg use W+2 signed temporary bits; multiply uses 2W+2 then floor rescale; fixed FMA holds a*b+(c<<F) in 2W+2 signed bits before its single floor rescale/overflow action; `/` uses W+F unsigned numerator bits n=abs(a)<<F and W denominator bits d=abs(b), hence W+F restoring-division iterations and W+F+2 signed quotient/adjustment bits. `//` divides unscaled magnitudes then floor-adjusts and shifts its integral quotient by F, in the same conservative quotient width. Mod/rem retain W+2 signed remainder/adjustment bits. Fixed rounding/overflow comes last. Dynamic shifts guard negative/oversized k before issue.

For floats, select a deliberately simple exact lattice route as the universal fallback. Let b,q,s be as above and B=P+2b-1=P+2^E-3. Every finite magnitude has an integer lattice coefficient Z with B unsigned bits and exact value Z*2^s. A normal decoder shifts its P-bit significand by e_field-1; a subnormal decoder uses its fraction directly. Sign uses a separate bit, or a B+1 signed value. This finite route is exponential in E and may be expensive; resource admission is honest, and future narrow GRS helpers must prove equivalence separately.

| Operation | Exact intermediate and width |
|---|---|
| add/sub | signed Za±Zb times 2^s; B+2 signed bits |
| multiply | signed Za*Zb times 2^(2s); 2B+2 signed bits |
| FMA | signed `Za*Zb+(Zc<<(-s))` times 2^(2s); 2B+2 signed bits, because -s<=B and B-s<=2B |
| divide | positive ratio abs(Za)/abs(Zb), sign XOR; numerator/denominator B bits after zero/special guards |
| reciprocal | positive ratio 2^(-s)/abs(Za), sign inherited; numerator <=B bits |
| fmod/remainder | unsigned restoring divide of abs(Za) by abs(Zb), <=B iterations, restore quotient sign or nearest-even quotient, exact lattice subtraction |
| casts | exact dyadic source; explicitly shift/rescale to destination, inspect whole rounded raw result before overflow; equal-width reinterpret is wiring |

Generic final rounding uses ordered positive finite output encodings, avoiding an unspecified align/GRS algorithm. There are A=(2^E-1)*2^q nonnegative finite encodings 0..A-1, strictly increasing by real value. Binary search this code interval for the largest y<=exact magnitude, at most ceil(log2(A+1))<=E+q iterations. If exact value exceeds the max-finite code, compare with the overflow midpoint H against a conceptual next value 2^(b+1). Otherwise compare against `(y+next(y))/2`; equality chooses the output whose significand low bit is even. Apply saved sign and exactness/tininess flags. Each search step contains one bounded exact comparator; no early rounding occurs before cancellation.

For a rational intermediate n/d*2^t and candidate c=Y*2^v, compare n shifted by max(t-v,0) with d*Y shifted by max(v-t,0). The helper-plan width is

```text
C = 1 + max(N_bits+max(t-v,0),
            D_bits+Y_bits+max(v-t,0)).
```

Use v=s for finite candidates and v=s-1, Y=Zlo+Zhi for midpoint candidates, including conceptual top; Y has at most B+1 bits. Arithmetic graphs carry N_bits,D_bits,t explicitly and calculate C at planning time. Sign handling occurs before this positive comparison. All shift counts are compile-time nonnegative and every signed temporary has a proved guard bit. The plan verifier checks width rules, operand ranges and finite iteration bounds; emitter truncation is permitted only at the final declared normalization node.

For sqrt, binary search the same finite output codes and compare candidate c by c*c against exact input x; midpoint comparison uses its square. Exactness compares y*y to x. Squared midpoint lattice coefficient takes <=2B+2 unsigned bits; compare against `abs(Za)<<(2-s)`. For rsqrt, compare c*c*x to one, and exactness likewise; the product coefficient is <=3B+2 bits, compared to `1<<(2-3s)`. These compile-time constants fit those bounds for b>=1,q>=1. R011 signed-zero/Inf/invalid/DZ dispatch precedes this search. Unlike a naming convention, these are finite bit algorithms for every declared descriptor.

A B-bit restoring division executes i=B-1..0: shift remainder/add numerator bit; subtract denominator and set quotient bit if remainder>=denominator. Use B+1 remainder bits; denominator zero faults before reservation/issue. Integer square root uses the digit-pair recurrence over the compile-time source width, ceil(width/2) iterations, with exact trial/subtraction and one guard bit. Generic float code search executes <=E+q compare iterations plus one midpoint/status check. These are logical iteration bounds, not a claimed target cycle latency or II. The selected target graph provides its own bounded microstep schedule and may pipeline or iterate it; hard requested II/resource constraints still require evidence.

A Strict transcendental hardware route initially uses a finite certified input/output table, implemented by a deterministic lookup/ROM plan with exact guard, or an interval/helper graph whose full domain bound is certified as above. A table answers every admitted tuple with finite latency after handshake; synthesis determines fit. Philox uses the ten fixed integer rounds or a ten-round sequential helper. Nondyadic stochastic rejection deliberately has no bounded success latency; it needs the resumable protocol. Vendor floating/math routes require a verified mapping record with input AND result domains/status, plus an exact fallback for excluded cases. A flushing operator with only special-input classification cannot repair finite cancellation/underflow. Missing helper cost, vendor parity, RTL validation and achieved timing are later target gates, not undefined algorithms.

## Bounded scale ratios for quantization libraries

[[50 - Library and Migration Recipes]] uses exact quantization/dequantization and calibrated scales. A runtime scale is a registered immutable aggregate, not an arbitrary rational accelerator scalar:

```text
ScaleRatioType = quant.scale_ratio.v1(N,D,K,L,U)
ScaleRatioValue = {
  sign:Bool, numerator:UIntW(N), denominator:UIntW(D), exponent:IntW(K)
}
represented_value = (-1)^sign * numerator/denominator * 2^exponent
```

Require positive denominator and exponent in the declared inclusive [L,U], which must fit IntW(K). A scale additionally requires sign=false and numerator>0. Canonical stored scales have coprime odd numerator/denominator after moving all factors of two into exponent; internal signed zero ratio is exactly sign=false,numerator=0,denominator=1,exponent=0. Scale one is numerator=denominator=1,exponent=0, including all-zero calibration. A frozen literal rational scale is a separate descriptor ingested by the same exact rules; it does not consume a runtime record or require host Fraction at hardware execution.

For calibration maxabs/Qmax, first scan every finite input in logical order; maxabs may be the magnitude of signed minimum, so use unsigned magnitude W bits rather than checked typed abs. All-zero selects scale one. For floating source Flt(P,E), the significand has <=P bits, original exponent t in [s,b-q]; with D=bit_length(Qmax), conservative normalized bounds are N=P and exponent [s-D,b]. For fixed source, N=W,D=bit_length(Qmax), exponent [-F-D,max(0,W-1-F)]; the upper-bound zero explicitly includes all-zero scale one in fractional-only formats. After gcd reduction, removing factors of two cannot exceed these bounds. K is the smallest signed width containing the entire interval. Calibration for arbitrary custom types stays representable; an HLS plan can reject overly wide required integers without replacing the scale.

Products of canonical ScaleRatio(N1,D1,L1,U1) and ScaleRatio(N2,D2,L2,U2) use numerator N1+N2 bits, denominator D1+D2 bits and exponent bounds [L1+L2,U1+U2], followed by canonicalization. Their odd factors remain odd after gcd reduction, so no further power-of-two exponent change occurs. Exact sums first choose e=min(e1,e2) and cross-multiply denominators: signed numerator is `n1*d2*2^(e1-e)+n2*d1*2^(e2-e)`. Maximum alignment delta is `max(0,U1-L2,U2-L1)`; allocate C=max(N1+D2,N2+D1)+delta+2 signed bits, D1+D2 denominator bits, and raw e bounds [min(L1,L2),min(U1,U2)]. After sum canonicalization, an even numerator can increase exponent: its conservative bounds become [min(L1,L2),min(U1,U2)+C-1], additionally including zero for canonical zero. Carry/sign and subtraction are explicit. Quantized represented values `(q-zero_point)*scale` widen the integer subtraction by two signed guard bits, multiply its exact magnitude into the scale numerator, then use these same sum/product bounds with canonicalization bounds applied.

Quantization of dyadic source m*2^t divided by positive n/d*2^e forms `(m*d)/n * 2^(t-e)`. If source magnitude uses M bits and t in [Tlo,Thi], numerator requires M+D+max(0,Thi-L) bits, denominator N+max(0,U-Tlo) bits after an explicit guarded dynamic shift. Run restoring unsigned division for the declared numerator width, retaining quotient k and remainder r. For positive source, floor/trunc choose k, ceil chooses k+[r>0]; for negative source, trunc/ceil choose -k, floor chooses -k-[r>0]. Nearest-even is sign*(k+increment), increment iff 2r>denominator or equality with odd k. Then add zero-point in max(quotient_bits,storage_width)+2 signed bits and apply the storage overflow mode. Dequantization is an exact product plus one output quantizer. Scale validation precedes arithmetic, so denominator zero/negative scale faults before division or output writes.

Canonicalization uses gcd on positive integer magnitudes by Euclid: `(a,b)->(b,a%b)` while b!=0, with unsigned restoring division and a fixed <=2*max(N,D)+1 remainder-step bound (every two nonterminal steps at least halve the remainder). Divide numerator/denominator by gcd, count trailing zeros in each by a width-bounded scan, shift them out, and adjust exponent with widened checked integer arithmetic. For a general raw ratio with N-bit magnitude,D-bit denominator and e in [L,U], conservative normalized exponent bounds are [L-(D-1),U+(N-1)], with zero included if numerator can be zero. Canonical-input product and odd-denominator sum routes use the tighter bounds above. The plan derives each canonical output exponent bound before emission; an insufficient declared output record rejects at planning or an explicit active guard, never silently wraps its exponent. Bit-width/loop bounds are part of the helper plan. These concrete finite helpers support exact library scales and cross-sums without a hidden unbounded runtime rational type.

## Reduction laws and reference interpreter

`LawDescriptor={law_id,op_id,type_ref,rounding,overflow,admitted_domain_ref,associative,commutative,identity_bits?,proof_ref}` is checker-owned. Built-in IDs match R002: wrapping raw fixed add; F=0 wrapping multiply; fixed min/max; raw bitwise AND/OR/XOR; Bool all/any/xor. Derive neutral bits mechanically: zero, raw one, fixed extrema, all-ones, or Bool constants. Signed W=1 integer product uses raw one representing -1, whose modular neutrality is still valid. Fractional multiply, ordinary float arithmetic, signed saturation, checked arithmetic and arbitrary lambda get no associativity from their names. No frontend Boolean can manufacture a law.

An arbitrary pure combine still works through ordered fold/fixed tree. If custom freely regroupable reduction is requested, initial certification exhausts the finite admitted domain: totality/fault freedom, closure, all triple associative comparisons with typed normalization, every pair commutative comparison when requested, and every identity pair. A subset domain must additionally be closed under combine and its membership proven/guarded for leaves. This costly finite procedure is a concrete certificate method; a rejected resource budget diagnoses the requested law, not the lambda's fold/tree capability. A later proof language can add whitelisted algebraic derivations, but untrusted theorem text or sample tests are insufficient.

Interpret enabled folds with PC states Seed -> Contribution(j) -> Combine(j) -> Contribution(j+1) -> Publish. Save init once; contribution effects commit at their own declared boundaries; a combine fault stops before the next contribution. Interpret trees as Collect ordered leaves -> an explicit postorder list of `(left,right,parent)` combine nodes -> Publish. Build default topology by adjacent pairing/carrying odd final leaf at each level; store the topology in checked meaning, independent of scheduling par. Lawful total reduction chooses a recorded tree (sequential is a valid reference witness) and preserves ordered contribution effects. Zero/singleton/identity/nonempty rules are handled before unnecessary combines.

For memory fold: snapshot initialized destination seeds in destination-index order; for each map index invoke mapper once, snapshot selected cells in destination order, combine/update private cells in that same order, then advance map index. For memory tree: collect these snapshots first, then each destination cell's tree in destination order. Publish destination cells only after all success; mapper effects already committed are not rolled back. An empty destination domain makes no destination cell access but still invokes the mapper once per active map index, preserving its effects/faults; there are zero snapshots/combines/publication. Disabled invocation evaluates nothing, including seed. Owned-accumulator alias checks precede execution.

The exact state transition order is already specified in R002; this decomposition makes the interpreter method concrete. Do not coalesce publish with combine or collect contributions eagerly in a fold. The FIFO checked-Int8 example consumes its first token only before faulting; the intentional tree variant collects both before combining.

## RNG state and resumable requests

Keep the R011 Philox algorithm verbatim. Represent committed word position t in 0..2^66 inclusive, where t=2^66 means exhausted. Derive block ordinal=t//4 and cursor=t%4 for a nonexhausted state; seed/stream ID are checked 64-bit integers. This removes ambiguity at the last block's final word without wrapping a 64-bit block ordinal. Stream IDs are explicit source/builder bindings checked unique within the frozen program composition; a shared resource is one explicit stream, not duplicate declarations. Canonical IDs are never object identities.

```text
StreamState {algorithm_version,seed,stream_id,committed_word_position:t}
PendingDraw {request_id,owner,stream_resource,generation,
             start_t,k,required_words,next_word,private_accumulator,
             phase:Reserved|Computing|Ready|Committed|Abandoned}
```

For `rng_bits(k)`, require k>0, n=ceil(k/32); compare n with 2^66-t before reserving. Too large faults without state change. Reserve exclusive predecessor token; calculate each word from counter `(ordinal_lo,ordinal_hi,id_lo,id_hi)` and seed key, append little-endian to private accumulator; retain next_word/accumulator across wait. At Ready return low k bits, discard padding, then atomically commit t+n, result, and exactly one next token. Cancel before commit abandons local state/releases reservation without t advance. A later request cannot overtake a held reservation. At exhaustion no counter is evaluated or wrapped.

Bounded sampling validates N>0 before a draw. N=1 consumes one word and returns zero. Otherwise k=bit_length(N-1); each complete `rng_bits(k)` is its own commit, followed by the pure compare U<N. Reject keeps that attempt's advance and repeats; cancellation/exhaustion retains all prior committed attempts. No finite successful-attempt bound is asserted. This agrees with the protocol blueprint's Captured/Reserved/Issued/Committing/Done/Abandoned helper ABI: numeric internal steps are private until Commit; no external issued obligation exists for a local RNG draw.

Uniform/stochastic formulas stay R011's. Compute exact rational raw value l+m/d, reduced 0<=m<d. Integral results consume one word; a dyadic denominator uses low k-bit threshold; nondyadic uses bounded rejection U<d then selects upper iff U<m. Zero/nonfinite invalidity faults before the draw, selected rounding then overflow after committed draw. Checked overflow retains draw advance. A multiword draw that cannot fit is rejected atomically, while previously completed rejection attempts remain consumed. Float/fixed uniform grid representability is checked from the entire grid, not one lucky sample.

## Acceptance evidence and cross-blueprint review

This bounded probe uses Python standard-library integers/Fraction and an independently structured enumerator: the candidate quantizer chooses exponent/quantum and rounds quotient/remainder; the oracle enumerates every representable finite nonnegative value and compares exact distances, separately applying the overflow threshold. It checks value and NX/UF/OF for 16,080 finite arithmetic/FMA results in Flt(3,2); four format-lattice bounds; independent rational ln2, Machin pi and exp-one enclosures; an exact sqrt midpoint; and seeded stochastic/bounded sampling first draws. An independently structured squared-midpoint enumerator checks another 280 sqrt/rsqrt input/status decisions, including a custom format with rsqrt overflow; 9,216 exact scale-ratio alignment cases verify conservative numerator/exponent bounds; 65,025 unsigned-8-bit Euclid pairs have maximum 12 remainder steps against the conservative bound 17. Another 11,520 fixed calibration cases check scale numerator/denominator/exponent bounds, including the all-zero scale-one branch for fractional-only formats. It does not exhaust NaN/signed-zero dispatch, verify all analytic recipes, or certify full-domain transcendental/HLS support.

The acceptance ledger must add: all sNaN/qNaN/signed-zero precedence; FMA 0*Inf+qNaN IV; cancellation/two-round discriminator; min-sub exact/half-min-sub UF; max-finite overflow midpoint; exact pow root/log2-power handlers; huge rational trig reduction; inverse endpoints; fixed fractional-only formats; malformed/tampered proofs/coverage; ResourceLimit without guessed bits or replayed effects; observed NX; final RNG exhaustion/multiword cancel/rejected prefix; every fold/memory empty/disabled/fault trace. Core small-format probes, standard-format independent vectors and recipe proofs are different evidence classes. SoftFloat remains a pinned external validation oracle for standard core operations, never a semantic native dependency; its [3e interface](https://www.jhauser.us/arithmetic/SoftFloat-3/doc/SoftFloat.html) supplies independently documented FMA/tininess/remainder conventions.

The cross-blueprint review selected the explicit empty-destination refinement: the memory mapper executes once per active map index, including its effects/faults, even when the selected destination domain has zero cells. There are zero snapshots/combines/publication and no destination cell access. R002 and the condensed contract must carry this same selected policy. A faulting mapper in a three-index map and empty destination stops at its faulting map index; eliminating the mapper would change the trace.

The remaining work is production implementation/review and conformance, complete selected math profile certification, helper emission, target resource/vendor/RTL evidence and timing. There is now a fully specified method for each finite mathematical result, equality/status case and conservative hardware fallback. No practical uniform transcendental bound or achieved hardware result is claimed.

## Reproducible bounded probe

Executed on 2026-10-01 with `python3 /private/tmp/spatial_numeric_readiness_probe.py`; no packages required. Full input is reproduced below so the temporary file is not required for reproduction. The exact observed output was:

```text
small_format_exact_value_status_checks 16080
lattice_width_formats_passed 4
ln2_f32_bits 0x3f317218 interval_width_lt_2^-100 True
pi_f64_bits 0x400921fb54442d18 interval_width_lt_2^-140 True
exp1_f32_bits 0x402df854
sqrt_exact_midpoint_tie sqrt(81/64)=9/8 -> 1.0 in Flt(3,3)
stochastic_raw_minus_1_25 -1 committed_words 1
bounded_N3_seed0_stream0 1 committed_words 1
sqrt_rsqrt_exact_boundary_checks 280
scale_ratio_alignment_cases 9216
euclid_u8_pairs 65025 maximum_remainder_steps 12 bound 17
fixed_calibration_scale_bounds_cases 11520 all_zero_scale_one_included True
```

```python
from fractions import Fraction as Q
from itertools import product
from math import factorial, isqrt


def two(k):
    return Q(1 << k) if k >= 0 else Q(1, 1 << -k)


def lg(x):
    e = x.numerator.bit_length() - x.denominator.bit_length()
    return e - (x < two(e))


def decode(bits, p, e):
    q, bias = p - 1, (1 << (e - 1)) - 1
    sign = bits >> (p + e - 1)
    ef, f = (bits >> q) & ((1 << e) - 1), bits & ((1 << q) - 1)
    if ef == (1 << e) - 1:
        return None
    v = f * two(1 - bias - q) if ef == 0 else ((1 << q) + f) * two(ef - bias - q)
    return -v if sign else v


def quant(x, p, e, zero_sign=0):
    q, bias = p - 1, (1 << (e - 1)) - 1
    sign = int(x < 0) if x else zero_sign
    sign_bits = sign << (p + e - 1)
    if not x:
        return sign_bits, 0
    x = abs(x)
    s, top = 1 - bias - q, bias
    k = lg(x)
    if k > top:
        return sign_bits | (((1 << e) - 1) << q), 0b10100
    t = max(s, k - q)
    z = x / two(t)
    n, r = divmod(z.numerator, z.denominator)
    n += 2 * r > z.denominator or (2 * r == z.denominator and n % 2 == 1)
    y = n * two(t)
    if y >= two(top + 1):
        return sign_bits | (((1 << e) - 1) << q), 0b10100
    nx = y != x
    uf = nx and y < two(1 - bias)
    status = int(nx) * 16 | int(uf) * 8
    if y == 0:
        return sign_bits, status
    if y < two(1 - bias):
        return sign_bits | int(y / two(s)), status
    ey = lg(y)
    mant = int(y / two(ey - q))
    return sign_bits | ((ey + bias) << q) | (mant - (1 << q)), status


def enum_quant(x, p, e):
    # Independent method: enumerate representable values and compare exact distances.
    sign = int(x < 0)
    sign_bits = sign << (p + e - 1)
    x = abs(x)
    q, bias = p - 1, (1 << (e - 1)) - 1
    positive = [(b, decode(b, p, e)) for b in range(1 << (p + e - 1))]
    positive = [(b, v) for b, v in positive if v is not None]
    maximum = positive[-1][1]
    threshold = maximum + two(bias - q - 1)
    if x >= threshold:
        return sign_bits | (((1 << e) - 1) << q), 0b10100
    b, y = min(positive, key=lambda bv: (abs(x - bv[1]), bv[0] & 1))
    nx = x != y
    uf = nx and y < two(1 - bias)
    return sign_bits | b, int(nx) * 16 | int(uf) * 8


def ln_m(m, n):
    z = (m - 1) / (m + 1)
    s = 2 * sum((z ** (2 * j + 1) / (2 * j + 1) for j in range(n)), Q(0))
    tail = 2 * z ** (2 * n + 1) / ((2 * n + 1) * (1 - z * z))
    return s, s + tail


def atan_small(x, n):
    s = sum(((-1) ** j * x ** (2 * j + 1) / (2 * j + 1) for j in range(n)), Q(0))
    nxt = (-1) ** n * x ** (2 * n + 1) / (2 * n + 1)
    return min(s, s + nxt), max(s, s + nxt)


def exp_small(x, n):
    s = sum((x ** j / factorial(j) for j in range(n)), Q(0))
    tail = (x ** n / factorial(n)) / (1 - x / (n + 1))
    return s, s + tail


def philox(c, k):
    mask = (1 << 32) - 1
    for r in range(10):
        a, b = 0xD2511F53 * c[0], 0xCD9E8D57 * c[2]
        c = [(b >> 32) ^ c[1] ^ k[0], b & mask,
             (a >> 32) ^ c[3] ^ k[1], a & mask]
        if r != 9:
            k = [(k[0] + 0x9E3779B9) & mask, (k[1] + 0xBB67AE85) & mask]
    return c


p, e = 3, 2
finite = [decode(b, p, e) for b in range(1 << (p + e))]
finite = [v for v in finite if v is not None]
checks = 0
for a, b in product(finite, repeat=2):
    vals = [a + b, a - b, a * b]
    if b:
        vals.append(a / b)
    for v in vals:
        assert quant(v, p, e) == enum_quant(v, p, e)
        checks += 1
for a, b, c in product(finite, repeat=3):
    v = a * b + c
    assert quant(v, p, e) == enum_quant(v, p, e)
    checks += 1
print('small_format_exact_value_status_checks', checks)

# Independent exact lattice width check on every finite encoding of several formats.
for p, e in [(2, 2), (3, 2), (3, 3), (4, 3)]:
    bias, q = (1 << (e - 1)) - 1, p - 1
    s, width = 1 - bias - q, p + 2 * bias - 1
    zs = []
    for b in range(1 << (p + e)):
        v = decode(b, p, e)
        if v is not None:
            z = v / two(s)
            assert z.denominator == 1
            assert abs(z.numerator).bit_length() <= width
            zs.append(z.numerator)
    for a, b, c in product([min(zs), 0, max(zs)], repeat=3):
        fma = a * b + (c << -s)
        assert -(1 << (2 * width + 1)) <= fma < (1 << (2 * width + 1))
print('lattice_width_formats_passed', 4)

lo, hi = ln_m(Q(2), 32)
assert Q(6931471805599453094, 10**19) < lo < hi < Q(6931471805599453095, 10**19)
assert quant(lo, 24, 8) == quant(hi, 24, 8)
print('ln2_f32_bits', hex(quant(lo, 24, 8)[0]), 'interval_width_lt_2^-100', hi - lo < two(-100))

a, b = atan_small(Q(1, 5), 32), atan_small(Q(1, 239), 32)
plo, phi = 16 * a[0] - 4 * b[1], 16 * a[1] - 4 * b[0]
assert Q(3141592653589793238, 10**18) < plo < phi < Q(3141592653589793239, 10**18)
assert quant(plo, 53, 11)[0] == quant(phi, 53, 11)[0]
print('pi_f64_bits', hex(quant(plo, 53, 11)[0]), 'interval_width_lt_2^-140', phi - plo < two(-140))

elo, ehi = exp_small(Q(1), 48)
assert Q(2718281828459045235, 10**18) < elo < ehi < Q(2718281828459045236, 10**18)
assert quant(elo, 24, 8)[0] == quant(ehi, 24, 8)[0]
print('exp1_f32_bits', hex(quant(elo, 24, 8)[0]))

midpoint = Q(81, 64)
assert isqrt(midpoint.numerator) ** 2 == midpoint.numerator
assert quant(Q(9, 8), 3, 3)[0] == quant(Q(1), 3, 3)[0]
print('sqrt_exact_midpoint_tie', 'sqrt(81/64)=9/8 -> 1.0 in Flt(3,3)')

words = philox([0, 0, 0, 0], [0, 0])
u = words[0] & 3
assert u == 1
print('stochastic_raw_minus_1_25', -1 if u < 3 else -2, 'committed_words', 1)
assert words[0] & 3 == 1  # first N=3 rejection attempt accepted
print('bounded_N3_seed0_stream0', words[0] & 3, 'committed_words', 1)


def sqrt_quant(arg, p, e):
    if not arg:
        return 0, 0
    q, bias = p - 1, (1 << (e - 1)) - 1
    t = max(1 - bias - q, lg(arg) // 2 - q)
    z = arg / two(2 * t)
    k = isqrt(z.numerator // z.denominator)
    boundary = Q(2 * k + 1, 2) ** 2
    k += z > boundary or (z == boundary and k % 2 == 1)
    bits, status = quant(k * two(t), p, e)
    y = decode(bits, p, e)
    if y is None:
        return bits, 20
    nx = y * y != arg
    uf = nx and y < two(1 - bias)
    return bits, int(nx) * 16 | int(uf) * 8


def enum_sqrt_quant(arg, p, e):
    # Independent root oracle compares input to every squared midpoint.
    q, bias = p - 1, (1 << (e - 1)) - 1
    vals = [(b, decode(b, p, e)) for b in range(1 << (p + e - 1))]
    vals = [(b, v) for b, v in vals if v is not None]
    for j, (b, y) in enumerate(vals):
        nxt = vals[j + 1][1] if j + 1 < len(vals) else two(bias + 1)
        h2 = ((y + nxt) / 2) ** 2
        if arg < h2 or (arg == h2 and b % 2 == 0):
            nx = y * y != arg
            uf = nx and y < two(1 - bias)
            return b, int(nx) * 16 | int(uf) * 8
    return ((1 << e) - 1) << q, 20


root_checks = 0
for p, e in [(2, 2), (3, 2), (3, 3), (6, 2)]:
    for b in range(1 << (p + e - 1)):
        arg = decode(b, p, e)
        if arg is None:
            continue
        assert sqrt_quant(arg, p, e) == enum_sqrt_quant(arg, p, e)
        root_checks += 1
        if arg:
            assert sqrt_quant(1 / arg, p, e) == enum_sqrt_quant(1 / arg, p, e)
            root_checks += 1
print('sqrt_rsqrt_exact_boundary_checks', root_checks)

ratio_checks = 0
width = 4
lower, upper = -4, 4
delta = upper - lower
carrier = 2 * width + delta + 2
for n1, d1, e1, sign1, n2, d2, e2, sign2 in product(
        [1, 3, 7, 15], [1, 3, 7, 15], [-4, 0, 4], [-1, 1],
        [1, 3, 7, 15], [1, 3, 7, 15], [-4, 0, 4], [-1, 1]):
    chosen_e = min(e1, e2)
    numerator = sign1 * n1 * d2 * (1 << (e1 - chosen_e)) + sign2 * n2 * d1 * (1 << (e2 - chosen_e))
    denominator = d1 * d2
    assert -(1 << (carrier - 1)) <= numerator < (1 << (carrier - 1))
    assert denominator.bit_length() <= 2 * width
    expected = sign1 * Q(n1, d1) * two(e1) + sign2 * Q(n2, d2) * two(e2)
    assert Q(numerator, denominator) * two(chosen_e) == expected
    if expected:
        rn, rd = abs(expected.numerator), expected.denominator
        canonical_e = 0
        while rn % 2 == 0:
            rn //= 2
            canonical_e += 1
        while rd % 2 == 0:
            rd //= 2
            canonical_e -= 1
        assert lower <= canonical_e <= upper + carrier - 1
    ratio_checks += 1
print('scale_ratio_alignment_cases', ratio_checks)

maximum_steps = 0
for a, b in product(range(1, 256), repeat=2):
    steps, x, y = 0, a, b
    while y:
        x, y = y, x % y
        steps += 1
    assert steps <= 17
    maximum_steps = max(maximum_steps, steps)
print('euclid_u8_pairs', 255**2, 'maximum_remainder_steps', maximum_steps, 'bound', 17)

calibration_checks = 0
for width in range(1, 7):
    for frac in range(width + 1):
        for qmax in range(1, 16):
            dwidth = qmax.bit_length()
            lower, upper = -frac - dwidth, max(0, width - 1 - frac)
            for magnitude in range(1 << width):
                ratio = Q(magnitude, qmax) * two(-frac) if magnitude else Q(1)
                n, d, exponent = ratio.numerator, ratio.denominator, 0
                while n % 2 == 0:
                    n //= 2
                    exponent += 1
                while d % 2 == 0:
                    d //= 2
                    exponent -= 1
                assert n.bit_length() <= width
                assert d.bit_length() <= dwidth
                assert lower <= exponent <= upper
                assert Q(n, d) * two(exponent) == ratio
                calibration_checks += 1
print('fixed_calibration_scale_bounds_cases', calibration_checks, 'all_zero_scale_one_included', True)
```
