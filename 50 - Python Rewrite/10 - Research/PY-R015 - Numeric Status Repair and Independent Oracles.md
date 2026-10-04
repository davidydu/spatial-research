---
type: deep-dive
title: "PY-R015 — Numeric status repair and independent oracles"
topic: python-numeric-status-and-independent-validation
project: spatial-python
session: 2026-10-03
status: research-conclusion
adoption_status: proposed
implementation_status: not-implemented
source_files:
  - "50 - Python Rewrite/30 - Implementation Design/20 - Numeric Engine Blueprint.md"
  - "50 - Python Rewrite/40 - Specification/20 - Python Numeric Contract.md"
  - "50 - Python Rewrite/50 - HLS Lowering/PY-R011 - Numeric Lowering and Intrinsic Profiles.md"
  - "50 - Python Rewrite/60 - Validation/09 - Fable Design Review.md"
feeds_spec:
  - "[[20 - Python Numeric Contract]]"
  - "[[20 - Numeric Engine Blueprint]]"
  - "[[PY-R011 - Numeric Lowering and Intrinsic Profiles]]"
---

## Question, evidence, and authority

[designed] Repair the confirmed underflow defect before production implementation, retaining pure Python ownership of the frontend, compiler, and reference simulator. This note supplies evidence and alternatives before focused proposed-contract edits. [[09 - Fable Design Review]] and its archive remain historical evidence; neither their code nor their output is silently repaired.

[precedent-measured] The [SoftFloat FAQ, dated 2018-06-02](https://www.jhauser.us/arithmetic/SoftFloat-3/doc/SoftFloat-FAQ.html) and [Release 3e interface §6.2](https://www.jhauser.us/arithmetic/SoftFloat-3/doc/SoftFloat.html#underflow) (accessed 2026-10-03) distinguish after-rounding tininess from checking the stored exponent. Tininess uses destination precision with unbounded exponent range; underflow also requires inexactness. The FAQ gives a binary64-to-binary32 case whose stored result is minimum normal while underflow is set. These are primary documentation checks, not execution of a SoftFloat binary.

[measured] The current numeric blueprint's finite-output step 5 and its `quant`, `enum_quant`, `sqrt_quant`, and `enum_sqrt_quant` all test the stored value against minimum normal. Thus independent value-search structure does not provide an independent status oracle. The existing numeric contract already requires an explicit Bool-to-fixed overflow mode only when exact one is outside the destination range; the blueprint's unconditional wording is drift.

## Alternatives and proposed repair

| Alternative | Assessment |
|---|---|
| Keep stored-result tininess | Rejected: the archived minimum-normal counterexamples require UF and NX together. |
| Set UF for every inexact exact value below minimum normal | Rejected: this is before-rounding tininess and misclassifies the exact threshold control. |
| Perform an unbounded-exponent P-bit rounding for status | Correct selected semantics; used as the independently derived research oracle. |
| Compare the exact magnitude with a derived nearest-even threshold | Equivalent for the selected rounding mode; selected candidate/helper method because it is an exact rational comparison. |

[designed] Let `m=2^emin` and precision be `P>=2`, with `emin=1-(2^(E-1)-1)`. Immediately below m, the unbounded-exponent P-bit lattice has predecessor `m-2^(emin-P)`. Their midpoint is `T=m-2^(emin-P-1)`. At T the even significand is m. Therefore for nonzero exact real result z, after-rounding tininess is exactly `abs(z)<T`. For a finite stored result y, `NX=(z!=y)` and `UF=NX and 0<abs(z)<T`; zero and exact subnormals set neither. Infinity from finite overflow sets OF and NX separately. This formula is specific to nearest/ties-even and must not be generalized silently to other rounding modes.

[designed] The precision-only rounding is a status definition, never an intermediate value fed to final subnormal rounding: final bits come directly from z, preventing double rounding. For sqrt(a), compare `a<T*T`; for rsqrt(a), compare `a*T*T>1`, after the positive-finite domain guard. Exactness uses `y*y==a` or `y*y*a==1`, respectively. Negative-input and signed-zero dispatch remains R011's rule.

## Interval and finite-helper obligations

[designed] Matching endpoint output bits establishes a value cell only. For finite floating output, the checker must separately prove NX, output sign including signed zero, and tininess. After establishing the result's sign, a positive magnitude enclosure [L,U] proves tiny when `U<T`, and non-tiny when `L>=T`; otherwise refine or invoke an exact algebraic/equality handler. Exactness suppresses UF even when tiny. The exact threshold T is rational, so the blueprint's rational/nonrational classification also settles equality to T. A proof that omits this status obligation is incomplete even if both endpoints round to minimum normal.

[designed] A finite hardware fallback carries exact intermediates through a threshold comparator and budgets its width separately from the finite-output search. Reference refinement that runs out of resources returns ResourceLimit and publishes no value/status; rejected or unfinished profile certification admits no hardware route. Neither fallback converts uncertainty into zero, NX-only, or a guessed flag. Production, full intrinsic-domain, vendor, RTL, and practical resource-fit claims remain outside this study.

## Validation plan and limits

[designed] Freeze and rerun the historical full probe unchanged, then run a separately labelled repaired probe. Candidate status uses T; the oracle independently rounds to an unbounded-exponent precision lattice and compares that temporary result to m. Reuse the historical operation tuples and count all 16,080 arithmetic/FMA and 280 root decisions. Require the old implementation to fail the minimum-normal counterexamples, and test signed magnitudes, exact subnormals, zero, T±epsilon/T, root squared thresholds, overflow, and incomplete interval status evidence. Original and repaired results remain distinguishable.

## Executed repair evidence — 3 October 2026

[measured] The original full standard-library probe was extracted from the archived frozen blueprint and executed unchanged. Its Python-block SHA-256 is `ccddeb2ab424c4b6880636ee94bfc5d2fa3f41b79c191759f5aba3690920b4ca`. All original assertions and printed counts reproduced, including the defective agreement. A separate AST copy replaced the four UF assignments only: the candidates use the derived rational/squared threshold, while the oracles use independent unbounded-exponent rounding. All unrelated original checks also ran in that repaired copy. This is execution of research probes, not a production numeric library.

| Executed check | Result |
|---|---|
| Frozen historical arithmetic/FMA domain | 16,080 agreements reproduced; shared-predicate defect intentionally retained |
| Repaired same arithmetic/FMA domain | 16,080 value/status agreements; 228 decisions change UF from clear to set |
| Frozen historical sqrt/rsqrt domain | All 280 agreements reproduced with old predicate |
| Repaired same root domain | All 280 pass; no sqrt cases change status; three rsqrt cases change status |
| Signed, zero, subnormal, T-neighbor/equality, overflow vectors | 168 pass across (P,E)=(2,2),(3,2),(3,3),(6,2),(24,8),(53,11) |
| Required failures of frozen old quantizer | All 12 signed minimum-normal carry cases fail their independently specified expected status |
| Synthetic exact root-boundary comparisons | 48 pass, including equality and both sides of T² and the reciprocal-input expression |
| Interval tininess proof obligations | Four pass, including an unresolved interval with equal output bits |
| Finite status-helper width checks | 32 descriptors, P=2..9 and E=2..5, pass exact coefficient/constant bit-length bounds |
| Primary FAQ binary64 input `0x380fffffe1000000` | Exact Python decode/conversion gives binary32 `0x00800000`, status 24; frozen status is 16 |

[measured] The changed root decisions are all reciprocal square roots returning minimum normal, with old/new status 16/24:

| Format | Representable input a | Stored value |
|---|---|---|
| Flt(2,2) | 3/2 | 1 |
| Flt(3,2) | 5/4 | 1 |
| Flt(6,2) | 33/32 | 1 |

[judgment] No ordinary-sqrt discrepancy occurred in the historical tested domain. That observation does not prove a general absence across every descriptor or helper input. The additional root tests use exact rational radicands near T², not necessarily representable same-format source operands. The four interval checks exercise the proof-obligation arithmetic, not a completed certificate parser/checker; no malformed-certificate integration or scheduling/ResourceLimit execution is claimed.

## Reproduction and independent oracle construction

[designed] Preserve the frozen probe in the existing review archive. The separately labelled `repaired_probe.py` reads that frozen blueprint through `--blueprint`, writes historical/repaired outputs plus `results.json`, and never changes its source. Running it also reproduces the original ln2/pi/exp, stochastic, lattice, scale and Euclid checks. Only the four UF assignments in the executed AST copy change. The script uses Python integers and Fraction; no external numerical library is imported.

[designed] The oracle's rational-status method normalizes the exact magnitude into [1,2) by repeated exact powers of two, finds its two neighboring P-bit significands, chooses the closer value by exact distance and parity, and tests that precision-rounded value against minimum normal. Its root-status method normalizes the radicand into [1,4), binary-searches adjacent P-bit root significands, chooses using an exact squared midpoint comparison and parity, then tests the chosen unlimited-exponent root against minimum normal. Neither method knows T, calls the candidate status predicate, or infers tininess from final stored bits. Shared exact decode/power-of-two primitives remain a limitation; primary-source vectors provide another evidence class, not complete external conformance.

[designed] The candidate-only changes are small enough to audit directly:

```python
# In quant(x,p,e), after x has become a positive magnitude and NX is known:
uf = nx and x < two(1 - bias) - two(1 - bias - p - 1)

# In sqrt_quant(arg,p,e), where arg is the exact positive radicand:
uf = nx and arg < (two(1 - bias) - two(1 - bias - p - 1)) ** 2

# In enum_quant / enum_sqrt_quant, use the independently constructed
# precision-rounding methods, not either threshold expression above.
uf = nx and oracle_precision_tiny(x, p, e)
uf = nx and oracle_root_tiny(arg, p, e)
```

## Focused proposed-design changes and remaining gates

[designed] [[20 - Numeric Engine Blueprint]], [[20 - Python Numeric Contract]], and [[PY-R011 - Numeric Lowering and Intrinsic Profiles]] now state the corrected threshold, squared root comparisons, separate interval status proof, and finite threshold-helper widths. Certificates require a checked status derivation in addition to value; the repaired schema/rule version must reject old incomplete records. The code at the end of the blueprint remains explicitly historical and unrepaired.

[designed] The finite helper uses `T=Yt*2^(s-2)` with `Yt=2^(P+1)-1`, where `s=emin-(P-1)`. Rational helper comparison includes the new coefficient/exponent in its existing width formula. For a positive lattice input `a=Za*2^s`, sqrt tininess compares `Za<<(4-s)` with `Yt^2` using `max(B+4-s,2P+2)` unsigned bits; rsqrt compares `Za*Yt^2` with `1<<(4-3s)` using `max(B+2P+2,5-3s)` unsigned bits. Subtraction requires a guard bit. These are finite mathematical bounds; resource admission and generated-helper validation remain future work.

[designed] The Bool wording now follows the pre-existing owning contract. Int32 contains exact one, so Bool conversion needs no named overflow action. Unsigned Fix(False,0,4) does not: omission rejects by descriptor; true with Wrap gives zero, Saturate gives 15/16, Checked faults. False still requires the mode for that descriptor, although its value is exact zero; this avoids value-dependent legality and does not introduce an implicit Bool conversion.

[judgment] The defect is repaired in the proposed design and bounded research probes. The production Python engine, complete certificate schema/checker, external standard-format conformance suite, all special-value dispatch, full transcendental profiles, reference-budget/protocol integration, generated HLS/C/RTL helpers, and practical target costs remain unimplemented or unverified by this study. Do not turn the repaired counts into those stronger claims.

## Second review: explicit record and publication boundaries

[judgment] Fable's second review accepts the threshold, root comparisons and finite widths by hand, while identifying missing gates and record fields. Its statement that empty reduction publication was absent everywhere is too broad: R002 already says an enabled empty `reduce_into` writes its identity, and discriminator R05 distinguishes writing zero from retaining 99 when disabled. The improvement is to make the numeric blueprint/condensed contract independently explicit, including the tree and memory cases; no new empty-lawful-reduction policy is inferred from that mistaken absence claim.

[designed] Final floating quantization and its status/certificate rules accept only NearestEven with FloatingNearestEven overflow. Operator semantics remain separate: `fp.floor`/`fp.ceil` still compute mathematical floor/ceil and report fractional-loss NX from the input, while `OperatorDefined` resolves through its registered intrinsic. A final encoding quantizer cannot turn that operator into another function or discard its required status. Reject a forged Floor-mode float quantization/certificate before deriving T.

[designed] Bool conversion records always contain an overflow field. A fixed descriptor containing exact one defaults to Checked; explicitly supplied Wrap/Saturate/Checked are validated first and all canonicalize to Checked because both Bool images are exact. Unknown or inapplicable modes reject. If exact one is unrepresentable, require and retain an explicit fixed mode even for a false source. Floating Bool conversion uses FloatingNearestEven, and rejects fixed-overflow modes. This chooses one artifact identity for semantically identical accepted representable conversions.

[designed] An enabled empty lawful reduction publishes its identity, and an enabled empty tree reduction publishes its declared identity or empty_result. A scalar destination is written once; each selected memory destination cell is written once in destination order, without reading old destination values as seeds. Missing required empty results fault before writes. Empty folds retain seed evaluation/validity reads and perform no writes/publication. A zero-cell destination has no cell access/publication, while every active mapper still executes and operation-level empty-domain validation remains required. Disabled invocations do no seed/contribution/publication work.

[designed] The repaired certificate tokens are `schema_version="spatial.numeric.point/2"` and `proof_rule_set="spatial.numeric.rules/2"`; both are mandatory in the proposed PointCertificate. Missing, earlier or unknown tokens reject before proof interpretation. Reissue an old certificate only by recomputation under the repaired rules; hashes or matching output bits confer no exemption. StrictNum-v1 still names the intended arithmetic policy; the repaired certificate version records how its proof obligations are checked.

[designed] The outer host outcome for an internal numeric ResourceLimit is BudgetExhausted, with a continuation retaining the helper before the next unperformed action and a diagnostic naming the numeric cap/usage. Explicit typed ReferenceBudget overrides can raise caps on resume while preserving counters and committed effects; an omitted override retains existing limits. No numeric value/status is published on exhaustion. This follows the package owner's second-review outcome matrix; it is a proposed continuation contract, not a successful scheduler test.

[measured] The revised repaired probe now reads arithmetic/root counts from the executed suite output and checks them against a separate domain recount: both give 16,080 and 280. It asserts exactly one replaced UF assignment in each of the four named functions. All previous numeric checks pass again with 228 arithmetic/FMA and three rsqrt status changes; no sqrt cases change status. The frozen historical Python block retains its original SHA-256. A separate second-round boundary probe passes 11 final-quantizer/certificate-header cases, six mathematical floor/ceil cases, 21 Bool record/value cases, and 11 empty-operation trace cases. These execute small policy/header/trace models with handwritten expectations, not a production certificate parser, canonical artifact importer, complete reducer, scheduler or source compiler. The first-round scratch probe/results were retained separately before updating the probe.

[measured] A text check of R002 and the dated [[04 - Independent Numeric Review]] found no remaining final-stored-value underflow predicate governing current behavior. R002 gives exact nearest-even/subnormal values without a competing detailed UF rule; the dated review names after-rounding tininess without replacing its definition. Both remain preserved historical research context.
