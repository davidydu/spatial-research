---
type: reference
title: "Fable design review: findings and disposition"
project: spatial-python
date: 2026-10-02
status: reviewed
adoption_status: proposed
implementation_status: not-implemented
reviewed_snapshot: 8e5dd54d7255899889123fb277ae09bb75f5784c
review_model: claude-fable-5-1
---

> [!info] Follow-up — 3 October 2026
> [[11 - Design Refinement Iterations]] records the proposed repairs and new measured representation comparison. The current architecture uses immutable compiler-owned records with optional xDSL adapters. Findings and results below remain the dated historical review; see the follow-up for current closure and implementation limits.


## Recommendation

**Keep the pure Python architecture. Correct the numerical defect, reconcile the contracts, and complete the student-facing workflow before treating the design as ready to implement. Keep xDSL provisional until a representative comparison tests its cost.**

The proposed path remains Python source → checked Spatial program → Python reference simulation or a checked hardware plan → HLS. Python owns the meaning of the program. The simulator and planner consume the same checked program, so they do not acquire separate language rules. The review found no reason to return to a Rust compiler core.

The four Fable passes support this direction after qualifications. They do not prove that it is universally optimal or that an unimplemented compiler is correct. The useful outcome is a set of verified defects, choices and experiments that can improve the plan. [[D-28]] remains proposed for professor review.

## Review method and evidence

David explicitly requested this Fable review through `claude2 -p`, using a specified account. The account was verified locally before and during the review. This request authorized the exception to the usual Codex-only research workflow. Account identifiers and authentication data are excluded from the published evidence.

Three separate Fable sessions reviewed language/host usability, semantic correctness, and compiler/HLS architecture. A fourth session received all **44 frozen documents**, all three reports, and the integrating agent's source checks and numerical reproduction. Each session used `--model fable --effort high`; the returned model was **`claude-fable-5-1`**. Safe mode, an empty tool list and empty MCP configuration made the reviews text-only. All four returned successfully. Separate sessions broadened review coverage; they are not independent proofs.

The reviewed research commit is `8e5dd54d7255899889123fb277ae09bb75f5784c`. The archive contains all 44 documents at that commit, their SHA-256 manifest, four unedited final responses, sanitized provenance and a portable defect reproduction. Line citations in the reports refer to that frozen snapshot, not later page edits.

- [[10 - Fable Reconciled Feedback|Read Fable's complete final response and the disposition of every original finding]]. Its recommendations remain reviewer proposals.
- [Download the review evidence and reproduction](<50 - Python Rewrite/60 - Validation/assets/2026-10-02-fable-design-review.zip>).
- Archive SHA-256: `b119830d9c7b1fdb2e20d03fa49f4c83a03697cca538317356dfe4b1e304823b`.

## What needs correction

| Priority | Finding | Evidence and consequence | Required next work |
|---|---|---|---|
| 1 | Floating underflow status is wrong at a normal/subnormal boundary | Independently reproduced against the frozen numeric probe. Candidate and comparison oracle share the bad predicate | Repair the quantizer/status rules and independently derived oracles; check sqrt, rsqrt and interval certificates before accepting floating conformance |
| 2 | Signature binding descriptions disagree | The source blueprint and language contract explicitly prebind meta formals; the newer course contract prebinds the whole signature, including later shape ports | Establish one normative whole-signature binding rule, preserve body statement order, and test both source and builder |
| 3 | The full host experience is not yet specified concretely enough | Lab 1 calls the host example record pseudocode and leaves constructor names open; the package blueprint specifies lower-level operations | Freeze public input/binding constructors and show one complete, ordinary Python launch workflow |
| 4 | Several small contract details need one owning rule | Bool-to-fixed overflow-mode wording differs. Type-valued aliases lack a frozen source spelling. Empty-fold publication and bare-register initialization need an explicit rule | Resolve each item with a positive and a negative/boundary example; do not infer policy from incidental Python behavior |
| 5 | Framework choice lacks a representative comparison | Existing xDSL experiments establish useful behavior and bounded timings, not complete compiler latency or superiority over a custom IR | Compare xDSL and frozen Python records on the same checked program and declared workloads before committing deeply to either substrate |

The source references are in the complete response. These findings reopen specific readiness claims in [[07 - Python Implementation Readiness Audit]]; they do not invalidate the source coverage ledger or demonstrate failures in a production compiler, which does not yet exist.

### Confirmed numerical defect

The numeric blueprint's finite-output rule sets underflow only when the **final stored value** is below the minimum normal value and the result is inexact. That is insufficient for the selected after-rounding convention. Tininess is determined after rounding to the format's precision with an unbounded exponent range; a later subnormal-grid rounding can produce the minimum normal value while underflow remains set. This distinction is explained in the [official SoftFloat FAQ](https://www.jhauser.us/arithmetic/SoftFloat-3/doc/SoftFloat-FAQ.html).

The integrating agent extracted the original `quant` and `enum_quant` functions from the frozen blueprint and compared them with two exact-arithmetic formulations of this rule. These are newly executed research checks, not a SoftFloat binary run.

| Case, nearest-even rounding | Stored bits | Old status | Required status |
|---|---|---|---|
| Binary32 exact product `(2^24−1) × 2^−150`, obtainable from two representable operands | `0x00800000`, minimum normal | NX | UF + NX |
| `Flt[3,2]`: `1.75 × 0.5` | `0x4`, value 1 | NX | UF + NX |
| `Flt[3,2]`: exact value `15/16`, control at the tininess threshold | `0x4`, value 1 | NX | NX |

Here the blueprint's status encoding is UF=8 and NX=16: the first two cases should return 24, not 16. Result bits are unchanged. The third case prevents an overcorrection that sets underflow for every inexact result rounded up to the minimum normal value.

For a positive exact result `x`, precision `P` and minimum normal exponent `emin`, the nearest-even tininess threshold is `2^emin − 2^(emin−P−1)`. The reproduction compares this inequality with a separately expressed precision-rounding calculation. Equality at that threshold rounds to a normal value for the tininess test.

The original 16,080-case arithmetic/FMA probe used the same wrong status predicate in its candidate and enumerating oracle. Agreement therefore did not establish underflow correctness. The sqrt candidate/oracle pair repeats the predicate by inspection; this review has not demonstrated a sqrt counterexample in those tested formats. The historical probes and archives are preserved with an erratum, rather than rewritten to look as if they caught the problem.

**Status: confirmed and flagged; the design algorithm and historical probe have not been repaired in this review task.** Repair must include status decisions for interval-based math recipes, since proving the returned bits alone does not determine the underflow flag at this boundary. Independently specified vectors and a separate status oracle are required before closing this finding.

### Signature binding

The latest course examples intentionally allow a runtime dimension port to appear after a memory annotation that uses it. The course contract says to prebind the whole signature. Earlier text only explicitly prebinds meta formals. This is documentation drift, not proof that the intended checker cannot support the examples.

The correction should prebind all formal identities before resolving annotations, then enforce which categories may occur in a shape. A later `In[Index]` dimension is admissible; an arbitrary `In[Int]` port is not. Body-local declarations still obey statement order. A review suggestion that reordering formals must preserve the artifact digest is rejected: positional export order can be part of the ABI.

## Choices that need discussion, not automatic fixes

| Topic | Integrating recommendation | What is still a choice |
|---|---|---|
| Type aliases | Add an explicit registered type-constant form; it makes GEMM and reusable libraries much clearer | Exact spelling and capability requirements. Fable's `Const[Descriptor]` is a proposal, not currently accepted syntax |
| Host API | Show source capture, typed buffers, binding, simulation and output inspection as one complete example | Convenience wrapper names can be chosen above the existing public core |
| Callable/decorator entry point | Retain raw-source capture as the initial core | A later prevalidated loader or trusted-host callable adapter must state its acquisition guarantees. Ordinary imports execute defaults/decorators before a later validator can reject them |
| Lambdas, implicit index embedding, branch-local result merging | Treat them as separate usability proposals with paired examples | None is required to repair the architecture. Implicit embedding must preserve the checked conversion operation; merging must preserve scope/effects |
| Resource arbitration | Make task scheduling, channel arbitration and explicitly named selectors distinct in the contract | Fable proposes allowing a fairness class for unnamed channel arbitration. Current R008 names stateful round robin; widening the allowed traces is a semantic decision, not a text-only repair |
| Permanently false selector conditions | Specify the outcome explicitly and test the value-returning selector separately from masked vector operations | Immediate infeasibility fault versus documented permanent wait/deadlock outcome. Fable recommends the former; it is not adopted here |
| Empty memory fold and bare register | Define observable write/publication behavior and the reset/default image, or explicitly reject missing initialization | Fable recommends no publication for an empty fold and typed zero for a bare register. Those recommendations need adoption |

Two qualifications to the final Fable response matter. First, its evidence that round robin is both a rule and “one witness” partly compares **task scheduling** with **resource selection**, which are different layers. Its broader fairness-class default must not silently replace the present named policy. Second, the course trace's addition example is incomplete as a registry overview, but it never says addition is the only lawful reduction. Widening that explanation is useful; it is not evidence that the numeric engine lacks multiply, min/max or bitwise laws.

## Feedback that did not hold up

The integrating review rejected or narrowed these claims after reading the owning documents:

- **All helpers require explicit effect annotations:** summaries are already derived for unmarked helpers. Lambda support is a separate surface choice.
- **Only addition can be lawful:** the numeric blueprint already registers other proven operations. An unproved `reduce` must reject; silently turning it into `fold` would change the requested operation.
- **Different atomicity policies contradict each other:** atomic vector batches, per-item streaming transfers and deferred fold publication are intentionally different operations. Hardware optimizations must prove equivalence, including visible partial state after faults.
- **Fixed-priority resources violate all fairness requirements:** task fairness and resource fairness are distinct. Explicit fixed priority permits resource starvation under the proposed rules.
- **The xDSL timing proves a much slower full compiler:** the old experiment does not justify linear extrapolation to a pass pipeline. Invented break-even thresholds were rejected.
- **A pinned dependency establishes an immovable fork:** a commit pin and project-built wheel do not establish that claim. Upgrade policy remains ordinary package design work.
- **Existing numeric tests are independent because the reviewers or algorithms differ:** shared assumptions can invalidate the comparison, as the reproduced underflow defect shows.

Claims about editor/linter behavior and student usability were not experimentally verified. A different model family can expose blind spots, but model agreement is not a correctness oracle.

## How to decide the remaining architecture question

The strongest alternative is a custom immutable Python IR: frozen records for operations, regions, binders, effects and order tokens, consumed by the same checker, interpreter and planner. Both alternatives satisfy the pure Python direction. Neither has demonstrated a complete compiler performance advantage.

Compare both behind the Spatial-owned API using the same representative program structure, workloads and targets from [[PY-R007 - Host Workflow Reproducibility and Validation]]. Include nested control, effects and realistic rewrites, not only a flat operation chain. Measure total latency and memory, with clone, verifier and publication costs attributed separately. Report warm/cold conditions and repetitions. Count the framework rewrite facilities the actual path uses.

Retain xDSL if it meets the declared targets and supplies useful infrastructure. Switch if a measured xDSL cost causes a relevant target miss that the custom representation avoids. Do not decide from a hypothetical ten-pass extrapolation. No universal “optimal” result is claimed before this experiment.

For HLS, preserve the professor's order: settle what Python programs look like first. Before freezing the backend design, test representative course kernels and protocol adapters on a locked target release. Record eligibility, correctness, achieved initiation interval and resource cost separately. This review ran no vendor tools and does not add hardware evidence.

## Next work

1. Repair the underflow rule and independent status checks; reconcile signature binding and the smaller contract inconsistencies. Keep an explicit before/after record.
2. Complete the public host example and type-constant proposal. Bring a short list of surface and protocol decisions to the professor, with concrete paired programs.
3. After adoption, build the first complete checked-source-to-Python-simulation path. Run the xDSL/custom-record comparison while changing substrate remains inexpensive.
4. Expand the numeric/state conformance corpus with genuinely independent expected results. Keep all language families in the ledger while implementing them in stages.
5. Probe the HLS routes before committing the backend design, then require conformance and measured target results before claiming hardware support.

This review updates the evidence and flags known defects. It does not adopt Fable's optional syntax/protocol changes, repair the full numeric engine, start a production compiler, or certify the plan as globally optimal.

## A short explanation for the professor

We asked another model to challenge the whole design, then checked its findings ourselves. The recommendation is still a pure Python compiler with one checked program used by both simulation and hardware planning. The review found a real floating-point flag error and showed that one of our tests repeated the same mistake. We also need to finish the public Python workflow and make several rules consistent across the documents. Before committing to the compiler framework and HLS backend, we will compare the concrete alternatives on the programs we expect to support.
