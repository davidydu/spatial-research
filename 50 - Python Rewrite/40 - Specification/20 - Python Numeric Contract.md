---
type: spec
title: "Proposed Python Spatial numeric contract"
concept: python-numeric-and-reduction-semantics
scope: python-rewrite
source_files: []
source_notes:
  - "[[PY-R002 - Numeric and Reduction Semantics]]"
  - "[[PY-R011 - Numeric Lowering and Intrinsic Profiles]]"
  - "[[PY-R015 - Numeric Status Repair and Independent Oracles]]"
decision_records:
  - "[[D-28]]"
hls_status: rework
depends_on:
  - "[[10 - Python Language Contract]]"
status: reviewed
adoption_status: proposed
implementation_status: not-implemented
---

## Policy and authority

Use explicit typed bits and one Python arithmetic definition for constants and reference execution. Normalize at every declared operation. This is the proposed policy under [[D-28]], not automatic compatibility with all original Spatial paths. R002 preserves source evidence and calculated disagreement cases; R011 supplies complete floating special/status, intrinsic/random, and target-profile rules. Their detailed tables and discriminators are part of this proposed contract.

Compiler semantics do not depend on host float precision, platform integer width, or a vendor's default rounding mode. Reusing the same arithmetic functions in checking and simulation does not provide an independent test oracle.

The implementation methods are fixed in [[20 - Numeric Engine Blueprint]]: exact quantizers, per-intrinsic rational enclosures and equality handlers, certificate records/checking, finite raw-bit hardware algorithms, and resumable random draws. Pointwise reference termination with sufficient resources is distinct from a full-domain bounded target certificate. No completed numeric library or practical hardware fit is claimed.

## Types and ingress

`Fix(signed,I,F)` has `I>=0`, `F>=0`, total width `W=I+F>=1`, normalized W-bit storage, and value `raw/2^F` under the declared signedness. Signed interpretation is two's complement. `Int` is signed 32-bit fixed with F=0. Meta/index integers are a separate unbounded structural category. Signed I=0 formats are permitted; neither a multiplicative identity of numeric one nor arbitrary target support follows automatically.

`Flt(P,E)` uses P>=2 precision bits including the hidden bit and E>=2 exponent bits. Its storage width is P+E. Zero/subnormal, normal, and infinity/NaN encodings follow the R002 descriptor. Standard aliases include F16, F32, F64, and the proposed BF16 extension. Bool is distinct from numeric types; host True cannot silently enter as integer one.

Parse source numeric lexemes exactly. A context-free integer synthesizes Int32 and must fit, including a signed-literal check for the minimum negative value. A decimal without a numeric context requires a type. Expected type flows through literal-only trees and literals beside a typed operand; it does not recast already typed variables or widen an operation from its destination.

Fixed literal ingress uses floor quantization after a strict representable-range check. Floating literal ingress uses nearest/ties-even and rejects a finite literal that overflows to infinity. Exact decimal/rational input, raw bits, and an already rounded host binary float are distinct constructors. Preserve literal expression structure: in a format with one fractional bit, contextual `0.75*2` quantizes its operands and multiplies to 1.0, rather than evaluating host 1.5 first.

## Fixed arithmetic and conversions

For raw a,b, ordinary add/subtract/negate wrap modulo 2^W. Multiply computes `floor(a*b/2^F)` then wraps. `/` computes `trunc_zero(a*2^F/b)` then wraps. `//` represents the mathematical floor quotient in the same format. `%` uses `a-floor(a/b)*b`; `rem` uses `a-trunc_zero(a/b)*b`. For fractional formats the remainder's integer quotient is different from the quantized fractional `/` result.

All four fixed division/remainder operations fault on an active zero divisor. Untaken branches and inactive lanes do not evaluate that fault. An optimizer may not remove a language fault merely because its numerical result is unused.

Bit operations act on W-bit representations. Shift counts must be nonnegative; oversized left/logical-right shifts yield zero and arithmetic-right shifts yield sign bits. Arithmetic-right shift rounds downward. Explicit saturation or checked-overflow attributes apply after the operation's specified rounding. Floor/ceil are mathematical operations returned in the same type with their declared overflow policy.

Explicit fixed FMA computes floor((a*b+c*2^F)/2^F), then applies one declared overflow action. Its wrapping/floor result agrees with the proved separate-operation rule; saturation/checked modes do not permit automatic contraction. Explicit Bool-to-numeric maps false/true to exact zero/one and requires a named fixed overflow mode when one is outside the destination range. Neither operation changes ordinary expression boundaries or introduces implicit Bool conversion.

The checked Bool conversion record always has an overflow mode. A fixed destination containing exact one defaults to Checked; explicit Wrap/Saturate/Checked are validated and canonicalized to Checked, giving identical semantic records for those accepted spellings. Invalid modes reject. If one is unrepresentable, an explicit fixed mode is required and retained even for a false operand. Floating Bool conversion defaults to FloatingNearestEven and accepts only that overflow mode. Diagnostic provenance may retain source spelling independently of canonical semantics.

Fixed-to-fixed casts rescale exactly, then round and normalize. Default explicit casts use floor and wrapping; other named rounding/overflow modes are explicit. Fixed/float-to-float converts with one destination nearest-even rounding. Float-to-fixed defaults to truncation toward zero and checked overflow; nonfinite checked/wrapping casts fault. Saturating casts map infinities to bounds but still fault on NaN. Bit reinterpretation requires equal widths and preserves bits without numeric conversion.

## Floating values, status, and intrinsics

Default finite core arithmetic rounds its exact mathematical result once to the declared format, nearest/ties-even, with gradual underflow and correctly handled significand/exponent carry. Ordinary multiply-plus-add retains two rounding points; explicit FMA has one and follows R011's special-value table. No implicit fast-math mode or contraction is enabled.

Final floating quantization and its certificate rules accept only NearestEven with FloatingNearestEven overflow; other attributes reject before arithmetic/status derivation. This does not reject mathematical `fp.floor`/`fp.ceil` or registered OperatorDefined intrinsics: their function semantics and required operator-level flags apply first. In particular, floor/ceil fractional-loss NX cannot be erased merely because the resulting integer encodes exactly.

For nonzero finite exact result x and finite stored result y, NX means x differs from y. Let `emin=1-(2^(E-1)-1)` and `T=2^emin-2^(emin-P-1)`. After-rounding tininess means rounding x to P-bit precision with unbounded exponent range solely for the tininess test; equivalently for nearest/ties-even, `0<abs(x)<T`. UF is that condition together with NX. Equality at T is non-tiny, and exact subnormals do not set UF/NX. The final stored value may be minimum normal while UF remains set: Flt(3,2) exact 7/8 gives one with UF|NX, but 15/16 gives one with NX only. Final bits are rounded directly from x, never from a precision-only intermediate. Finite overflow to infinity sets OF|NX. Special/domain statuses remain R011's separate dispatch rules.

Sqrt and single-round rsqrt use exact algebraic comparisons for both rounding and status: for positive finite input a, tininess is `a<T*T` or `a*T*T>1`, respectively. Strict intrinsic certificates must prove value, sign, exactness and status separately; identical rounded endpoint bits do not settle UF. An unresolved status boundary requires refinement or a checked exact equality handler. A result/status is published only after all required proof obligations hold.

The repaired point-certificate schema is `spatial.numeric.point/2` with mandatory proof-rule set `spatial.numeric.rules/2`. Missing, earlier or unknown tokens reject before proof interpretation; old certificates require recomputation under the repaired rules. The intended StrictNum-v1 arithmetic policy is unchanged.

Arithmetic canonicalizes NaNs; reinterpretation preserves their bits. Signed zeros compare numerically equal, but sign-sensitive operations retain the specified sign. Min/max propagate NaN, retain same-sign zero pairs, and select -0/+0 respectively for mixed-sign zero ties. Ordered comparisons with NaN are false; inequality is true. Floating division by zero follows infinity/NaN/status rules, distinct from a fixed division fault. Explicit `fmod` and `remainder` use different quotient rules; float `%`/`//` are not silently borrowed from host Python.

Ordinary floating status is diagnostic metadata without a global mutable flag register. Optimizations may change diagnostic operation counts. A separately observed status operation returns/records its declared status and has the corresponding semantic/effect contract. Checked conversion faults remain observable regardless of whether diagnostic flags are exposed.

R011 defines the proposed versioned strict and explicit approximation profiles, special cases, intrinsic domain/range treatment, RNG algorithm/state/consumption, and stochastic rounding policy. A math profile must define reference results, not merely name a host library. A deterministic approximation implementation must also identify its algorithm/table and verified error bound; the bound alone does not determine downstream branches or consumes. No unspecified vendor approximation substitutes for the selected profile.

For stochastic rounding of exact raw k+f, with k=floor(value) and 0<=f<1, choose k+1 with nominal probability f and k otherwise under ideal uniform random bits. The versioned seeded generator defines deterministic replay; it does not prove those probabilities for each fixed seeded execution. Random streams are explicit resources with algorithm/version, seed/key, stream identity, counter, and consumption order. Blocking cannot redraw operands; optimization cannot duplicate or delete a random draw. Record generator and state in run identity. R011's concrete random-word and rejection/consumption rules govern reproducibility.

Strict mathematical definitions do not imply every format or intrinsic has a practical HLS realization. Finite-format/domain certificates, resource bounds, numerical adapters, and target capability checks remain required. A bounded reference evaluator reports a resource-limit outcome if it cannot certify a result within its declared budget; it does not return a guessed value. These limits are distinct from language domain faults.

## Reductions and folds

Contribution regions may have effects; active contributions execute exactly once in declared logical order. Combining regions are typed and state-free: no storage access, RNG draws, consume/produce, observed-status resource, or external effect. Arithmetic language faults are still possible and follow the declared fold/tree order; these operations are not generic total/speculatable Pure. Permission to regroup combine values never permits regrouping, duplicating, or dropping contribution effects or faults.

| Operation | Proposed meaning | Empty enabled invocation |
|---|---|---|
| Ordered fold | Start with explicit seed once; apply combine left to right | Return seed |
| Lawful reduce | Use a recognized/proved typed associative operator, with optional valid identity; reorder only with commutativity | Return identity if supplied, otherwise domain fault |
| Fixed-tree reduce | Fixed ordered leaves and topology; default adjacent pairs carrying an odd final leaf | Declared empty result/identity, otherwise domain fault |

An enabled empty lawful or fixed-tree reduction publishes its declared identity/empty result just as a completed scalar result: a supplied scalar destination is written once, and each selected memory destination cell is written once in destination order. No old destination seed is read and no contribution/combine runs. Empty mem_reduce with identity zero over destination [7,9] writes [0,0]; a missing required empty result faults before writes. This differs from the seed-read/no-write empty-fold rule below. With zero selected destination cells there are no cell accesses/publication, but operation-level empty-result/nonempty validation still applies and each active mapper still runs. Disabled invocations do none of this work.

Wrapping fixed addition is associative; integer wrapping multiplication and bitwise/Boolean operations have their typed laws. Fractional multiplication, floating addition/multiplication, signed saturation, checked arithmetic, and arbitrary user lambdas do not gain associativity from their names. Padding requires a proved neutral identity. Explicit fixed trees stay unchanged when a scheduling parameter changes.

Identity-free lawful reduction requires a proved/validated nonempty domain or an active empty-domain fault before result publication; a singleton returns its leaf. Faulting folds retain recurrence order; fixed trees evaluate left subtree, right subtree, then parent for observable faults. Checked Int8 fold of [1,-1] from seed 127 faults at the first combine; reassociation cannot turn it into a successful 127 result.

A fold evaluates contribution j and its combine before the next contribution; a FIFO mapper therefore leaves the second token unconsumed when the first combine faults. Fixed-tree reduction collects ordered contributions first, then evaluates its tree. Freely regroupable reduction requires a total combine on the admitted domain or a proof preserving fault/effect behavior. Memory mappers execute once per active map index even when the destination domain is empty; their effects/faults still occur, but no destination cells are touched in that case. Otherwise they snapshot selected cells in destination order, and fold private cells before the next map index; memory trees collect snapshots before combining cells. Publish destination results after success. R002 fixes the detailed order; a streaming optimization must preserve it.

Identity, seed, reset value, and old destination state are different fields. `reduce_into` writes its result once and does not include old state. `fold_into` explicitly snapshots an initialized destination as seed. Under the proposed refinement in [[PY-R018 - Protocol Policy Refinement]], an enabled empty fold still evaluates its seed and performs required initialization/validity reads; it returns the scalar seed or retains the seeded destination, with no combine or destination write/publication event. An empty memory-fold map domain still snapshots the destination seeds in order, so an uninitialized seed faults even when there are no contributions. Disabled controllers evaluate no seed/contribution and perform no write. An empty destination domain still executes each active mapper with zero destination cell accesses or publication. Other enabled empty reductions apply their declared empty rule. Memory variants enforce mapper lifetime/alias rules and preserve each selected cell's operation order. Accumulator specialization must preserve these boundaries and rounding points.

## Acceptance and target gates

R002 provides exact expected values, source disagreements, and a bounded fixed-FMA probe. R011 adds full special-value/status cases, random known-answer vectors, intrinsic-profile obligations, and per-operation lowering conditions. Validate small-format exhaustive cases, independently derived standard-format vectors, literal/constant/runtime parity, FMA and grouping counterexamples, active/inactive faults, exact random consumption, and empty/disabled/seed/destination variants.

[[PY-R015 - Numeric Status Repair and Independent Oracles]] preserves the failed historical UF predicate, requires it to fail minimum-normal counterexamples, and reports a separately repaired probe. Candidate and oracle must not share the status predicate: value-oracle independence alone is insufficient. The repaired bounded research checks are not production conformance or a full intrinsic-domain certificate.

For hardware, match primitive format/rounding/special behavior, prove a restricted-domain adapter, or use a checked bit/helper implementation. Otherwise report a named missing capability. Width limits, helper cost, achieved schedule, and resource fit are separate from reference semantics. No Python numeric conformance, vendor numerical parity, or hardware timing result is claimed by this document.
