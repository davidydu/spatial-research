---
type: deep-dive
title: Independent Numeric Review
topic: independent-python-numeric-review
project: spatial-python
source_files:
  - "50 - Python Rewrite/10 - Research/PY-R002 - Numeric and Reduction Semantics.md"
  - "50 - Python Rewrite/50 - HLS Lowering/PY-R011 - Numeric Lowering and Intrinsic Profiles.md"
  - "50 - Python Rewrite/40 - Specification/20 - Python Numeric Contract.md"
  - "spatial@e7a8f2f:argon/src/argon/lang/Fix.scala"
  - "spatial@e7a8f2f:argon/src/argon/node/Fix.scala"
  - "spatial@e7a8f2f:emul/src/emul/FixedPoint.scala"
  - "Random123 v1.14.0 philox.h and kat_vectors"
  - "Berkeley SoftFloat Release 3e interface"
  - "AMD PG060 v7.1, 2020-12-16; UG1399 displayed 2025.2/2026.1"
session: 2026-09-30
status: research-conclusion
feeds_spec: []
---

# Independent Numeric Review

## Scope and disposition

Independently reviewed [[PY-R002 - Numeric and Reduction Semantics]], [[PY-R011 - Numeric Lowering and Intrinsic Profiles]], and [[20 - Python Numeric Contract]]. This reviewer did not author those numeric studies or contract; the reviewer authored earlier control/memory studies, so this is independent of the numeric authors, not an independent organization. Reopened decisive primary sources and executed bounded arithmetic/RNG calculations. No original Spatial compiler, production numeric implementation, vendor tool, or RTL ran.

The proposal is coherent after the repairs below. Strict definitions, deterministic approximation tables, statistical assumptions, and executed capabilities remain separate. This review does not certify the unimplemented correctly rounded transcendental library or a hardware profile.

## Material findings and repairs

| Finding | Counterexample and required repair | Disposition |
|---|---|---|
| Optional reduction identity | R001/R006 use lawful `identity=None`; R002 initially required identity. A nonempty wrapping sum is well-defined, with singleton equal to its leaf. Permit absent identity with proved/validated nonemptiness or an active empty-domain fault before publication. Never use a register reset implicitly. | Verified in R002 and numeric contract. |
| State-free combine versus faults | Checked Int8 fold seed 127 over `[1,-1]` faults at the first addition; regrouping the values to zero would succeed with 127. “Pure” must exclude storage/RNG/consume/status effects without promising totality or speculation safety. Preserve arithmetic faults and declared tree/recurrence order. | Verified; total/fault-free admitted-domain requirement or separate fault/effect equivalence proof added. |
| Contribution/combine sequencing | With FIFO `[1,-1]`, the same checked fold consumes only 1 before faulting. Eagerly collecting both contributions consumes a different prefix. Fold must evaluate seed, contribution j, then combine j before j+1. Fixed tree intentionally collects ordered contributions first, then combines left/right/parent. Memory mapper snapshots and private-cell update/publication order must likewise be explicit. | Verified in R002 and contract, including memory order and no rollback of prior mapper effects. |
| Signed-zero min/max | Unconditional “min chooses -0, max +0” could manufacture -0 from two +0 inputs or +0 from two -0 inputs. Retain same-sign pairs; select -0/+0 only for mixed-sign ties. | Verified across R002, R011, and contract. |
| Stochastic probabilities | Seed/stream zero always starts with low two bits 1, so rounding raw -1.25 selects -1 on each reset. The 3/4 upper-neighbor probability is a threshold theorem under ideal uniform bits, not a theorem for each seeded replay. Overflow clipping/wrapping may also change final-value expectation. | Ideal-uniform versus deterministic replay distinction verified. |
| RNG exhaustion/partial draw | With two words remaining, `rng_bits(96)` needs three. Partial consumption would leave unspecified state. Preflight and atomically commit fixed-width draws; preserve helper state across suspension, cancel uncommitted draws without advancing, and retain completed rejected attempts. Rejection has no certified success bound before finite stream exhaustion. | Verified in R011 and linked contract. |
| Nondyadic stochastic arithmetic | Original UnbDiv exists, but a dyadic-cast rule alone cannot express exact raw 1/3. For quotient `l+m/d`, positive reduced d, sample U below d using rejection and choose l+1 iff U<m; d=1 still consumes one word. Zero faults before RNG, overflow follows the committed draw. UnbMul uses its exact dyadic product. | Verified in R011, including rejection, saturation, and pre-overflow probability scope. |

The last family is original language scope, not a new convenience: `spatial@e7a8f2f:argon/src/argon/lang/Fix.scala:76-87` and `spatial@e7a8f2f:argon/src/argon/lang/Fix.scala:117-129` expose ordinary/saturating unbiased multiply/divide. The old emulator uses four additional bits and the biased negative helper (`spatial@e7a8f2f:emul/src/emul/FixedPoint.scala:52-62`; `spatial@e7a8f2f:emul/src/emul/FixedPoint.scala:232-240`). Exact rational thresholds deliberately revise that implementation. For -1/3, floor -1 and fraction 2/3 give nominal neighbors 0 and -1 with probabilities 2/3 and 1/3 before overflow action.

## Independent probe and primary-source checks

Executed R011's printed Python probe directly with Python 3.12.7 on 2026-09-30, then compared an independently structured high/low-product round implementation on the three official vectors and 256 additional counter/key cases. All 259 matched. Independently retrieved [Random123 v1.14.0 round/constants](https://raw.githubusercontent.com/DEShawResearch/random123/v1.14.0/include/Random123/philox.h) and [known-answer vectors](https://raw.githubusercontent.com/DEShawResearch/random123/v1.14.0/tests/kat_vectors), accessed 2026-09-30.

```text
6627e8d5 e169c58d bc57ac4c 9b00dbd8
408f276d 41c83b0e a20bc7c6 6d5451fd
d16cfe09 94fdcceb 5001e420 24126ea1
```

The probe establishes the selected round/word convention, not statistical quality, stream sharing, suspension, or RTL parity. Enumerating ideal inputs independently confirmed neighbor counts 3:1 for -1.25, 1:2 for 1/3, and 2:1 for -1/3, and exact expectation before overflow. Integer checks confirmed all four signed quotient/remainder pairs. In particular -3/2 truncates to -1, while -3>>1 is -2; the original constant-power-of-two rewrite is directly visible at `spatial@e7a8f2f:argon/src/argon/node/Fix.scala:133-145`.

[SoftFloat 3e §§6.2, 8.5–8.6](https://www.jhauser.us/arithmetic/SoftFloat-3/doc/SoftFloat.html), accessed 2026-09-30, supports after-rounding tininess with inexactness, single-round FMA, invalid for zero×Inf even with a quiet-NaN addend, and exact nearest-even-integer remainder. R002's same-format wrap/floor fixed-FMA identity is algebraically sound; it establishes neither saturation/mixed-format equivalence nor target behavior. Ordinary floating multiply/add must retain two roundings.

Independently reopened [UG1399 fixed-point summary, displayed 2025.2](https://docs.amd.com/r/2025.2-English/ug1399-vitis-hls/Fixed-Point-Identifier-Summary), [Floats and Doubles, displayed 2026.1](https://docs.amd.com/r/en-US/ug1399-vitis-hls/Floats-and-Doubles), and [PG060 v7.1, 2020-12-16 PDF](https://docs.amd.com/api/khub/documents/ym1A7qsltTGP_saZFTrikQ/content), printed pages 5–6 and 13. The documented flushing, sNaN treatment, conversion/accumulator rounding, and approximate reciprocal/math accuracy do not provide StrictNum parity. PG060's FMA note excludes invalid status for zero×Inf+quiet-NaN, unlike StrictNum; matching NaN output alone is insufficient for observed status. R011 records this difference. These are mixed documented versions, not a tested installed configuration.

## Feasibility and residual gates

Strict core arithmetic can use finite exact integer decisions. Generic descriptors and exact real-function definitions do not establish practical termination/resource bounds. R011 correctly requires finite format/domain certificates for range reduction, interval error, midpoint/hard cases, maximum precision/iterations/storage, and returns a tool resource-limit outcome without fabricating a value. No completed certificate library is claimed.

CertifiedTableMath selects concrete output bits, with domain guards, hash/version, finite-neighbor restrictions, and exact StrictNum handling outside the approximation range. An error bound alone cannot choose a branch or FIFO consume. Larger tables, binary domains, and fixed exp/power may be infeasible; acceptance remains per certified profile. Observed status is explicitly unavailable in approximation v1.

Remaining implementation tests must cover inactive faults/draws, exact and rejected RNG consumption, counter exhaustion/cancellation, fractional-only formats, division minimum/-1, all signed zeros/NaNs, FMA status, seeded replay, identity-free emptiness, fault-sensitive mapper prefixes, and target domain/resource limits. The independent bounded probes do not close these execution gates.
