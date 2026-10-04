---
type: reference
title: "Design refinement: decisions, evidence and remaining gates"
project: spatial-python
date: 2026-10-03
status: reviewed
adoption_status: proposed
implementation_status: not-implemented
baseline: a06ccfdf10780dc37f248a127df39d5b903677c6
---

## Recommendation

**Build the source frontend, compiler and reference simulator in Python. Store the checked program and initial hardware plan in immutable, compiler-owned Python records. Use xDSL only when a specific backend pipeline earns its conversion and validation cost.**

The student writes Spatial kernels using Python syntax. The compiler captures that source, checks Spatial's types, memories and control rules, then creates one checked program. Reference simulation and hardware planning consume that same program. HLS follows after the Python behavior is established. [[D-28]] records the revised architecture; professor adoption of the detailed proposal is still pending.

This revision follows [[09 - Fable Design Review]]. It replaces the mandatory xDSL representation, repairs the floating-status algorithm, completes the source-to-output host example, and specifies previously ambiguous protocol outcomes. It does not claim a production compiler, complete numerical conformance or a globally optimal architecture.

## How the iterations work

David authorized several rounds of Codex and Fable review. The stopping rule is concrete: each confirmed design defect needs an owning rule and a distinguishing example; architecture comparisons need measured evidence with limits; contradictory claims must be reconciled; remaining implementation experiments must be explicit. Reviewer agreement alone does not close a finding.

| Round | Work | Outcome |
|---|---|---|
| 1 — Repair and compare | Three Codex specialists worked on numeric semantics, source/host workflow, and compiler representations. The integrating agent examined protocol alternatives. Fable independently reviewed the frozen baseline | Separate status oracles, complete host workflow, an executable representation comparison, and explicit protocol choices |
| 2 — Challenge the repairs | Codex specialists cross-reviewed other areas. Fable received the revised numeric/surface documents and actual bounded probes. A fresh Codex reviewer challenged the integrated architecture | Closed shared-lowering risk, helper shape substitution, selector scope, conversion-mode normalization, and result/continuation contracts |
| 3 — Final acceptance | Fable challenged 14 frozen design documents; Codex independently checked the resulting repairs | Proposal supported for professor review; staged gates, early transform fixture, storage/output capabilities and stale prose corrected |

Three successful Fable sessions are text-only external reviews through the requested account, verified locally. The requested `fable` alias returned `claude-fable-5-1`. Reviewers received numbered, hashed documents and must not be credited with executing supplied probes. An initial attempt was blocked by automatic approval review over optional third-party logging and produced no completed review. Subsequent sessions disabled nonessential traffic and telemetry; local authentication reported analytics disabled. The blocked attempt is excluded from completed-round counts. Authentication details and raw model event streams are not public evidence.

## Decisions that changed

| Question | Revised proposal | Reason and limits |
|---|---|---|
| Who owns the compiler representation? | Immutable checked semantic records and immutable target-plan records; optional derived xDSL adapter | Spatial already owns the semantic verifier, canonical format, provenance and legal transformations. Direct record ownership is simpler. [[PY-R017 - Compiler Representation Comparison|The measured comparison]] supports the choice without establishing full compiler performance |
| How are floating underflow flags decided? | Compare the exact result against the precision-rounding boundary, independently of the final subnormal stored bits | The previous candidate and oracle agreed on the same wrong rule. [[PY-R015 - Numeric Status Repair and Independent Oracles|R015]] uses a separately derived oracle and preserves the old failure |
| How does a student run a program? | Capture raw source, specialize, check, bind typed inputs/backing views, prepare, simulate, inspect immutable complete outputs | [[PY-R016 - Source and Host Workflow Refinement|R016]] names the public forms. Only Completed exposes complete outputs; partial state cannot become success by serialization |
| How are signature dimensions resolved? | Allocate all formal identities in ABI order, then check category legality; substitute helper shape formals at each call | Forward signature references are allowed only for eligible categories. Body-local declarations still follow statement order |
| What does an all-false selector do? | Consuming queue selector faults with NoEnabledCandidate; pure selectors retain their explicit default; vector masks retain their all-invalid/no-action result | These are distinct operations. A single all-false rule would change existing semantics |
| What does an empty memory fold do? | Read and validate selected seeds; publish no destination writes | Different from disabled execution, empty destinations and empty lawful reductions. All four cases are stated separately |
| What initializes a bare register? | The descriptor registry's valid ZeroImage, otherwise require an explicit reset or reject | Compatible with the original numeric register default without inventing a reset for every possible type; SRAM remains uninitialized |
| What does resource round robin mean? | Exact cursor transitions over a semantic ordered endpoint table; abstract grants may be legally linearized within one physical clock | Task fairness and resource arbitration stay distinct. Same-clock optimizations need correspondence, not a change to the language |
| What checks lowering before HLS? | Verify the revision-bound continuation cache, then execute the finite ProtocolPlan records and compare projected semantic events | A direct-region fixture oracle addresses correlated continuation-lowering mistakes. Actual plan execution and vendor validation remain implementation gates |

[[PY-R018 - Protocol Policy Refinement]] owns the protocol alternatives and counterexamples. Soft `par` and `ii` preferences do not silently change the semantic stop-admission window.

## Review suggestions that were narrowed or rejected

- S0 retains minimal malformed-import and cache-trust checks. Comparing representations before S0 does not justify accepting unchecked artifacts until a later slice.
- Exact resource round robin remains the proposed policy. Multiple physical commits may share a clock when they have a legal semantic ordering; this does not silently widen the language to any fair arbiter.
- The empty-reduction rule was already present in R002. The second reviewer exposed a need to repeat its publication behavior in the owning numeric blueprint, not an absence from the whole design.
- Final floating quantization is nearest-even. This does not ban mathematical floor or ceiling intrinsics before that final quantization.
- A source parser can reject deeply nested syntax in several expected ways. The new byte-limit fixture guarantees rejection before parsing only because its explicit byte budget is exceeded; it does not promise that every deep expression raises the same exception.
- A graceful stop may still have admitted work to finish. The final Codex check caught overly broad cleanup-only wording; the package and state contracts now preserve those remaining effects across a budget pause without admitting new work.

The round-by-round reports and dispositions are preserved with their exact input snapshots in the evidence archive. They distinguish text inspection, bounded execution, research policy selection and future implementation obligations.

## Measured support for the representation choice

The bounded comparison uses equal structured/effectful workloads, the same semantic invariant checker through native adapters, malformed inputs, full-clone snapshots on both routes, record sharing as a separate policy, and both local and widespread identity removal. xDSL's extra structural checks are reported separately. It uses five warmups, 20 timing repetitions and three fresh-process RSS observations per case/policy.

At 100,000 logical operations, construction plus the bounded checker has p95 **0.375–0.384 seconds for records** and **4.168–4.559 seconds for xDSL** across two graph shapes. With an original and fully cloned candidate alive, whole-process peak RSS is **116–126 MiB** and **364–377 MiB**, respectively. These measurements omit source capture, full alias/lifetime/provenance analyses, communicating tasks and HLS planning. The custom graph does not maintain xDSL's reverse-use index. They are not R007 end-to-end acceptance results or a universal speed ratio.

The strongest alternative remains xDSL's mature use tracking, cloning and potential external pass reuse. Before deep commitment, the first real slice must test structure-changing transformations, stale analysis rejection and provenance transfer. A named useful xDSL pipeline may justify an adapter; integrated evidence can reopen the representation choice. Full candidate reconstruction is acceptable initially; a sophisticated persistent graph library is not a prerequisite.

## Evidence and limits

| Evidence | What ran | What it does not establish |
|---|---|---|
| Numeric repair | 16,080 repaired arithmetic/FMA and 280 root comparisons, 168 signed boundaries, 48 algebraic boundaries, 4 interval obligations, 32 width descriptors, and 49 later mode/version/empty-operation checks | Production implementation, all-format conformance, compiled SoftFloat, certificate-parser or RTL correctness |
| Source and host contract | 51 initial checks, 55 second-round checks, 26 storage-capability checks, six output/view checks and 12 parsed Python blocks | An implemented source checker, real launch or simulator |
| Protocol examples | 642 round-robin readiness/cursor snapshots and 15 boundary examples | Generated-plan execution, general liveness or hardware behavior |
| Representation experiment | Six nested workloads at 1k/10k/100k operations, eight malformed invariants per workload on both routes, canonical/trace comparisons, clone isolation, local/dense transactions | Complete SpatialJSON, all compiler passes, full provenance or end-to-end budgets |
| Cross-review controls | 58 independent boundary checks and 924 additional precision-rounding comparisons | Independent coverage of the entire numeric library; the 924 checks cover status relations, not full value quantization |

The earlier arithmetic probe remains byte-for-byte historical evidence and is labeled incorrect at the underflow boundary. Likewise, the prior xDSL probes and wheel recipe remain useful dated evidence, without making xDSL a required core dependency.

## Final review disposition

[[12 - Final Fable Refinement Review]] preserves the final response. It supports submission for professor approval. Its six follow-ups were resolved as follows:

| Finding | Final disposition |
|---|---|
| F3-01 — First slice included later task/plan gates | Name separate S1, S5 and per-scope S6 obligations; no all-family claim from an S1 result |
| F3-02 — Harder representation test came too late | Add an ordered inlining/loop-expansion fixture at S1 exit, including real indices, provenance, stale-proof and failed-publication cases. It remains a designed implementation gate |
| F3-03 — Element storage capabilities unclear | Distinguish private typed state from packed Bits payloads. Preserve exact Index and masked-state semantics; require finite target proofs/layouts or report unsupported. A blanket Bits-only rule would remove existing structural/reference capabilities |
| F3-04 — Partial output and migration unclear | Empty uninitialized outputs need every selected cell written. Explicitly initialized owners preserve untouched cells, even under write-only Out. InOut is needed for reads. Six bounded owner/view examples pass; original Scala initialization evidence is source-inspected |
| F3-05 — Stale register/reset and research-status wording | Bare registers may use registered zero images; explicit resets remain available. R018 records a research conclusion, while all detailed contracts remain proposed |
| F3-06 — Alternative comparison required a preexisting winner | Attributed representation misses trigger a scoped comparison before further expansion. No invented percentage threshold, automatic framework replacement or approximation follows |

The detailed dispositions are archived. Proposed private Index state uses exact zero and unbounded integer semantics; masked state uses an all-invalid reset with registered zero payload and retains its guards. Neither choice silently creates a packed host ABI, finite hardware width or implicit materialization.

## Adoption and implementation gates

The detailed design remains a proposal. Its next step is professor review of the Python programming model and these architectural choices. After adoption, S0/S1 should establish source/builder/import parity, revision-safe checked publication, independent ordered execution checks, complete output snapshots and invalid-program diagnostics. Numeric and communication slices then implement their stated boundary cases. Before HLS acceptance, execute the actual finite plan and its negative mutants; vendor/RTL checks follow under an explicit capability profile. [[04 - Python Implementation Roadmap]] gives that order.

Research can recommend a design before these implementation tests run. It must not mark the tests passed or quietly replace a failed semantic obligation with a benchmark result.

## Reproduction and review archive

- [Refinement reports, exact review snapshots, final proposed documents and bounded probes](<50 - Python Rewrite/60 - Validation/assets/2026-10-03-design-refinement-probes.zip>). SHA-256: `cf5db65940a4c245d4d71e8891a9b8ad394cc5576216e0df99165832af617560`.
- [Separate compiler representation experiment with raw timings and RSS observations](<50 - Python Rewrite/60 - Validation/assets/2026-10-03-compiler-representation-probes.zip>). SHA-256: `7a0c8baf1a92f34d617ea7023364a58cff08db59e01645642aa7623d6fb30bd8`.

The refinement archive contains 113 files, including per-round manifests, unedited final Fable responses, all finding dispositions, independent Codex closure, portable checks and integrating rerun records. Its final-proposal snapshot records the 14 final reviewed design documents after closure; the exact round-three input is preserved separately. The representation archive has its own 83-file content manifest. Raw model event streams, hidden analysis and authentication metadata are excluded. The earlier 2 October review archive is unchanged.
