---
type: deep-dive
title: "PY-R017 — Compiler representation comparison"
topic: python-compiler-representation
project: spatial-python
session: 2026-10-03
status: research-conclusion
adoption_status: proposed
implementation_status: not-implemented
source_files:
  - "xdsl@0b10746:xdsl/ir/core.py:584-594"
  - "xdsl@0b10746:xdsl/ir/core.py:1255-1329"
  - "xdsl@0b10746:xdsl/ir/core.py:1854-1903"
  - "https://docs.python.org/3.14/library/dataclasses.html (accessed 2026-10-03)"
feeds_spec:
  - "[[40 - Python Compiler and HLS Contract]]"
  - "[[PY-R006 - Compiler Architecture and Framework Choice]]"
---

## Question and authority

Does the proposed checked Spatial program benefit enough from xDSL's representation to justify making that mutable framework graph its canonical semantic representation? Compare xDSL with custom frozen Python records under the same structured grammar, invariants and transformations. Both routes retain pure Python, one checked semantic program shared by reference simulation and hardware planning, and Python ownership of language meaning. Available coding skills and maintenance capacity do not decide the comparison.

This is a bounded research experiment responding to [[09 - Fable Design Review]], not production implementation or an integrated compiler benchmark. [[PY-R007 - Host Workflow Reproducibility and Validation]] continues to own the unchanged end-to-end targets. The numerical and host-interface reviews are separate work.

## Method fixed before interpreting results

The experiment uses the installed curated xDSL wheel already recorded in [[40 - Package and Conformance Blueprint]]: xDSL source `0b107461b3bfcd353d949fe00d3d1623bd6c826a`, distribution `0.1.dev1+g0b107461b.spatial1`, CPython 3.14.5, and base dependencies `immutabledict==4.3.1`, `ordered-set==4.1.0`, `typing-extensions==4.15.0`. The installed `xdsl/ir/core.py` was compared with the clean pinned source checkout; both hash to `e4a56ec3e51f856d02ee8230739b5024c91da00260d4bce7c125ff08a6f52c08`. No source checkout shadows the installed package.

The machine is an Apple M2 Pro with 16 GiB RAM, macOS 26.6.2 arm64. CPU and RAM were queried separately because the benchmark sandbox blocks those two system-information calls. The archived `machine.json` records that distinction. Each benchmark runs in one process, with no overlapping benchmark child. Five warmups precede 20 timed repetitions; median and nearest-rank p95 are reported. Timing uses a monotonic nanosecond clock with garbage collection enabled and a full collection outside each repetition. **Allocation tracing is never enabled during timing.** Memory uses three additional fresh processes per case/policy, reporting process peak RSS; it is not `tracemalloc` memory or incremental graph bytes. The neutral generator and both representations' imported modules contribute to that RSS.

| Workload | Logical operations | Structured regions | Storage descriptors | Two topology variants |
|---|---:|---:|---:|---|
| Small | 1,000 | 20 | 10 | Branching tree; deeper bounded chains |
| Medium | 10,000 | 200 | 100 | Same generators with increased breadth |
| Scale | 100,000 | 2,000 | 1,000 | Same generators, bounded depth |

The small and medium **counts** match R007. The scale region/storage counts are experiment choices, not extra R007 requirements. Logical operations include terminators and region-bearing controls; xDSL's enclosing module/entry wrappers are infrastructure and excluded. Dynamic loop iterations do not inflate compile-time counts. A deterministic neutral generator supplies exactly the same workload to both builders. Generator construction is outside measured representation construction for both. The two topologies avoid extrapolating from the earlier flat arithmetic chain; neither claims to cover all Spatial programs.

The grammar includes isolated single-block regions with explicit token/integer arguments, wrapped Int32 addition with shared operands, pure identity operations, ordered storage events, lazy two-arm branches, fixed two-iteration loops, and single-region helper-like scopes. Storage IDs, requirement IDs and origin strings accompany the graph. Region argument/result signatures are explicit. Helper-like scopes are not a call-summary implementation. This probe has no communicating tasks, alias intervals, views, faulting numeric primitives, full provenance chains, general CFG, interprocedural checking or hardware planner.

Custom records use `frozen=True, slots=True` dataclasses with tuples, strings and frozen value records. xDSL uses IRDL operations, immutable string attributes, explicit SSA values and isolated regions. Both have the same program-level storage and requirement tables. The shared verifier reads each native representation through a small adapter; it does **not** first copy either graph to a common intermediate graph. It checks local dominance/capture, types and arities, region ownership, exact token use counts, terminators, storage references, and complete/unique requirement accounting. xDSL's additional structural verification is timed separately and included in its checked transactions. This separation exposes the cost of the framework's extra checking instead of attributing all checking differences to Spatial rules.

## Transactions and fairness limits

Three local-transform cases remove the same identity operation at the same deepest selected region, replace its uses and run the same complete semantic verifier:

1. **Records, full clone:** recreate all operation/region/value records, then edit and verify.
2. **xDSL, full clone:** framework clone remaps SSA values, replace the identity's uses, erase the operation and verify.
3. **Records, persistent update:** rebuild the changed block and its ancestors, share unchanged immutable records, then verify the complete candidate.

The first two are the closest snapshot-policy comparison. The third is a different, useful architecture policy, explicitly not described as faster whole-graph cloning. Whole verification remains linear even when the edit is local. Immutable attribute/type payloads can be shared by both full clones; zero shared *operations* does not mean zero shared objects. xDSL has mutable parent/use links, so attaching one operation graph to two snapshots is not the equivalent of sharing frozen records. A carefully designed partitioned xDSL snapshot scheme remains possible and is **not measured here**.

A supplementary transaction on both 1k and 10k topologies removes every identity operation throughout the graph. The record implementation rebuilds affected regions with a local value-remapping map; the xDSL implementation clones once and uses its maintained reverse-use lists to perform replacements. Both reverify, retain the input snapshot, preserve effect/requirement operations and compare canonical output and interpreted observations. These supplementary local/dense timings collect garbage outside every timed transaction, preventing an earlier discarded clone measurement from shifting garbage-collection cost into the reported phase. The raw first-suite transaction samples remain archived with that caveat. This tests widespread edits as well as favorable local sharing. It is not generic CSE, scheduling, banking, unrolling or a complete optimization pipeline.

xDSL's native reverse-use lists and parent links are additional capabilities absent from the compact record storage. The record passes perform forward traversal/local remapping; the benchmark does not pretend they include a production reverse-use index. Conversely, no unused custom index is charged to a compiler that has not required one. Future use-heavy passes must include index construction, maintenance and revision invalidation on the custom route. Adapter field access and rich xDSL attributes also differ from direct record fields; timings include those chosen designs, not an inherent lower bound for every xDSL implementation.

## Correctness evidence

Both representations produce identical canonical projections of every generated input and the same rewritten projection for each equivalent transformation. Canonicalization is a probe tree encoding, **not full SpatialJSON-v1**. For three input seeds, before/after execution has identical Int32 outputs and ordered storage-event hashes/counts. That interpreter is shared through adapters; these checks are transformation comparisons, not independent proof of language semantics. A separate five-operation hand-derived control checks a final `3*x` value and one `2*x` storage write modulo 2^32 for three seeds, including overflow, on both representations and after identity elimination. It validates that small control only, not the complete generated grammar.

Each topology/size rejects eight deliberately malformed variants on both routes: duplicate token use, wrong operand type, unknown storage, missing operation requirement, forward value use, wrong yield arity, lost requirement ledger, and implicit ancestor capture. Original snapshot digests remain unchanged. Frozen record field assignment rejects; replacing an attribute in a cloned xDSL operation preserves the original; cloned xDSL operands do not reference the original graph's operation results. An additional nested isolation probe checks remapping of both original block arguments and operation results, then rejects a deliberately invalid candidate and verifies the old revision remains unchanged on each route. The archived cases state exactly what was checked. This is a limited invariant suite, not all G01–G18 families.

The probe preserves origin payloads on surviving operations; it does not implement the complete deleted-operation lineage/diagnostic-transfer ledger required by the design. Frozen dataclasses emulate read-only field assignment, not a hostile-code security boundary. Transitively owned closed payloads remain mandatory on either route: frozen wrappers containing lists or arbitrary callbacks would not establish immutable semantics. The official [Python dataclass documentation](https://docs.python.org/3.14/library/dataclasses.html#frozen-instances) makes the same distinction between emulated read-only fields and true immutability.

## Architectural comparison

| Choice | Substantive benefit | Cost and unresolved evidence |
|---|---|---|
| Canonical semantic and implementation graphs on xDSL | Already demonstrated region/SSA storage, native use replacement, structural verification, cloning and generic parser/printer; available typed rewrite/pass APIs | Mutable graph ownership requires private snapshots and clone/verification publication. Spatial still owns dominance, tokens, region results, effects, numeric semantics, canonical artifacts, provenance and requirement transfer. Generic arithmetic dialects and passes need semantic adapters and strict purity admission |
| Canonical immutable semantic records; optional xDSL lowering adapter | Direct fit for published immutable semantic revisions and structured isolated regions; source/builder checking, simulation and planning share one authority. A derived xDSL form can reuse a **named** backend pipeline without deciding language meaning | Conversion/correspondence validation is a new boundary if an adapter is enabled. No such useful pipeline, conversion cost or end-to-end benefit is demonstrated by this probe |
| Custom records through semantic and implementation planning | Uniform revision/ownership rules, direct schema correspondence, no mandatory second representation; custom structural sharing available | Must supply the indices, editors, printers and analyses actually needed. Persistent IDs and revision-scoped facts require careful design. Richer CFG/control lowering or broad transform reuse may eventually favor a framework |

The earlier R006/readiness probes genuinely demonstrated generic text roundtrip and conservative effect retention through CSE/DCE. They did not demonstrate generic optimization of Spatial floating operations, effectful controllers, storage scheduling or protocol machines. Generic text is not the accepted cache/interchange format. Native use replacement is exercised in this comparison; the custom transform's forward remapping is an alternative algorithm, not an assertion that use lists have no value. At the pinned xDSL revision, `replace_all_uses_with` updates each recorded use (`xdsl@0b10746:xdsl/ir/core.py:584-594`); cloning copies the outer attribute/property dictionaries and remaps nested SSA operands (`xdsl@0b10746:xdsl/ir/core.py:1255-1329`). These are concrete mechanisms to weigh against the selected grammar.

## Recorded results and recommendation

The method and proposed disposition were written before changing R006 or the compiler contract. The final measurement tables below use the archived raw observations. This note does not grant implementation approval.

Times below are **seconds, median / p95**, for representation construction plus the bounded checker. They exclude source capture and the other R007 work.

| Operations / topology (max depth) | Immutable records | xDSL |
|---|---:|---:|
| 1,000 / branching (3) | 0.0032 / 0.0033 | 0.0330 / 0.0346 |
| 1,000 / deep (11) | 0.0033 / 0.0035 | 0.0323 / 0.0328 |
| 10,000 / branching (5) | 0.0329 / 0.0336 | 0.3280 / 0.3354 |
| 10,000 / deep (12) | 0.0330 / 0.0339 | 0.3253 / 0.3368 |
| 100,000 / branching (7) | 0.3508 / 0.3751 | 4.3913 / 4.5589 |
| 100,000 / deep (12) | 0.3562 / 0.3840 | 3.9415 / 4.1677 |

The record advantage is consistent across these two shapes. It is not evidence of a universal ratio: the 100k case changes allocation/collection behavior, the record storage omits a maintained use index, and the xDSL path performs extra structural verification. The archive separates construction, framework checking, shared semantic checking, cloning and canonical projection. No operation is timed under allocation tracing.

The preferred isolated transaction measurements include candidate construction, rewrite and complete verification. **Seconds, median / p95**:

| Operations / topology | Records local full clone | Records local sharing | xDSL local full clone | Records dense rewrite | xDSL dense rewrite |
|---|---:|---:|---:|---:|---:|
| 1,000 / branching | 0.0040 / 0.0041 | 0.0020 / 0.0021 | 0.0233 / 0.0238 | 0.0030 / 0.0032 | 0.0219 / 0.0224 |
| 1,000 / deep | 0.0040 / 0.0041 | 0.0020 / 0.0021 | 0.0235 / 0.0238 | 0.0030 / 0.0032 | 0.0220 / 0.0228 |
| 10,000 / branching | 0.0400 / 0.0408 | 0.0193 / 0.0200 | 0.2422 / 0.2941 | 0.0302 / 0.0312 | 0.2293 / 0.3043 |
| 10,000 / deep | 0.0402 / 0.0417 | 0.0197 / 0.0211 | 0.2487 / 0.2777 | 0.0306 / 0.0337 | 0.2318 / 0.2674 |

For the local edit, records share 995/1,000 and 987/1,000 original operations at the two small topologies; at 100k they share 99,991 and 99,987. Both full-clone policies share zero operation objects. Sharing never skips full verification. The dense supplement removes 200 identity operations at 1k and 2,000 at 10k; its operation-sharing counts are recorded separately. It gives the custom route evidence beyond one favorable local path, but still tests only a simple pure rewrite.

Fresh-process **peak RSS ranges over three repetitions, MiB**, while original and locally rewritten candidate coexist:

| Operations / topology | Records full clone | Records sharing | xDSL full clone |
|---|---:|---:|---:|
| 1,000 / branching | 37.2–37.3 | 36.9–37.0 | 39.6–39.6 |
| 1,000 / deep | 37.2–37.3 | 37.0–37.1 | 39.5–39.7 |
| 10,000 / branching | 44.1–44.9 | 42.2–42.8 | 69.8–70.4 |
| 10,000 / deep | 44.2–44.9 | 42.1–42.7 | 69.5–70.1 |
| 100,000 / branching | 116.0–122.8 | 99.7–103.3 | 374.0–376.6 |
| 100,000 / deep | 122.9–126.1 | 100.2–103.6 | 363.5–368.0 |

These peaks include common imports, the neutral generator, checked graph, candidate and verification scratch; they are not deep object-size estimates. The pre-build high-water marks are in every memory record. Records processes import xDSL too for experimental symmetry, so this does not measure a minimal custom-only install or cold import. Cold process/check latency, complete Spatial checks and all R007 reference-execution targets remain unmeasured.


## Proposed default and strongest dissent

**Recommend custom transitively immutable Python records as the canonical checked semantic representation, and use custom immutable records for the first implementation-plan representation. Keep xDSL as an optional derived lowering/interop representation, enabled only for a named, evidenced reuse case.** This changes R006's default; it does not add a second semantic authority or authorize production implementation.

The deciding argument is the fit to the selected language and ownership contract. Spatial's required graph is structured and isolated; the project already owns its exact typing, effects, protocol rules, requirement ledger, canonical schema, source mapping and almost all semantic validation. Frozen records express the required published revision directly. xDSL would add a mutable owned graph plus clone/publication wrappers while leaving those language obligations in place. Measured construction, checking and snapshot costs support taking the simpler semantic ownership path. They are supporting evidence, not proof of globally fastest compilation, and the result is not derived from an invented winning speed ratio. Neither contributor scarcity nor lack of compiler skills is part of this recommendation.

“Custom” does not mean an untyped bag of dictionaries, arbitrary object hooks, or duplicating semantics between interpreter and planner. Preserve separate unchecked/candidate/checked types, closed operation/region/type registries, explicit value/resource IDs, full validation on import, and a private constructor/publication boundary for checked revisions. Checked status is a certificate for a particular immutable revision, semantic profile and requirement disposition. Analyses and optional use/parent indices are revision-owned side tables, not mutable payloads attached to shared nodes. Pure source records do not become checked merely by a cast or field flag.

For an initial pass, construct a candidate with owned immutable fields; rebuild affected records and ancestors where convenient, verify the entire candidate, then publish it with a new revision and explicit fact invalidations. Sharing is an optimization permitted by the ownership invariant, not a requirement to build a sophisticated persistent graph library before the first slice. A full rebuilt candidate remains correct. Requirement discharge/transfer, deleted-operation lineage, and all cache invalidations still need explicit implementation and tests. No benchmark exception relaxes them.

The strongest dissent is that this experiment favors the **current structured grammar and simple transformations**. It does not supply a production record editor/use-index implementation or test the harder implementation-plan transformations. xDSL's tested use-list maintenance, region cloning and mature generic representation may become decisive for broad CFG lowering, large unrolling/remapping workloads or a useful external dialect pipeline. A bespoke record system can accumulate hidden structural bugs and expensive index rebuilds even with excellent contributors. The faster current prototype is not evidence that those future costs are zero. That objection justifies an early discriminating gate and preserving the pinned xDSL evidence, rather than making its mutable semantic graph mandatory now.

## Adoption and reversal conditions

1. **Stage the representation obligations at their actual consumers.** `REP-S1` is an S1 exit gate: source, builder and artifact import converge on the same checked record program and reference behavior, including helper summaries, branch/loop yields, borrowed capability/alias/lifetime checks, faults and malformed imports. `REP-EDIT` is also required at S1 exit, before S2–S5 expand that representation: the ordered structure-changing fixture below checks real remapping, indices, requirement/provenance transfer, stale facts and failed publication. `REP-S5` is required before claiming communicating-task support or planning that family; it adds task-group parent-token-once, child domains and join/cancel obligations. `REP-S6(scope)` is required before any S7 emission for that scope; it checks CandidatePlan/PlanRecords correspondence, publication, execution and serialization. S6 for the S1 subset may proceed before S5; it cannot claim the S5 family. Record each named gate and linked fixture evidence separately; no unqualified “representation gate passed” follows from S1 alone. These are dependency-specific boundaries, not a universal “deep commitment = S7” rule. The present bounded experiment passes none of these implementation gates.
2. **Measure the declared workloads without changing the target.** Use R007's complete capture/check/optimization and diagnostic workloads, at least five warmups/20 repetitions, cold process startup separately, p95 and peak RSS. Include the real indices and provenance/correspondence tables used by each candidate. The unchanged targets are small warm p95 ≤1 s/cold ≤3 s, medium warm p95 ≤5 s/peak ≤1 GiB, and 100k capture/check/ordinary optimization ≤30 s/peak ≤4 GiB. These partial measurements satisfy no end-to-end gate, and leave reference-execution targets unmeasured.
3. **Named xDSL adapter gate.** Before adding a mandatory adapter, name the actual dialects, transformations or downstream tools it reuses; demonstrate why they preserve Spatial numeric/effect/protocol requirements; measure conversion, verification, provenance/correspondence, retained snapshots and package/startup cost together. Parser/printer availability or a pass's existence is not measured end-to-end benefit. Reuse may justify an optional derived plan adapter without changing the canonical semantic representation.
4. **Trigger comparison before requiring an alternative to exist.** If a supported integrated workload reproducibly misses an existing R007 target and profiling identifies the representation, required index or transaction design as a cause of that miss, open a bounded comparison task before extending the affected representation-dependent route. Record the workload, missed target and attribution; compare a scoped record repair with an xDSL candidate for the same semantic or plan slice, including their real indices, provenance, verification, retained snapshots and conversion/publication costs. The trigger does not depend on first building a winning alternative or on an invented percentage of the budget. A miss in exact arithmetic or protocol simulation alone does not trigger a representation replacement. Reopen the relevant default if an actual required graph/transform conflicts with closed records, the comparable alternative meets the failed target with the same correctness guarantees, or a named reused pipeline demonstrates whole-workflow benefit. A successful plan-layer adapter need not replace the canonical semantic records. If both satisfy budgets, decide on verified representation requirements and actual reuse, not toy timing ratios. An unresolved miss remains an unmet gate; it is not silently waived.


### Early ordered rewrite discriminator — REP-EDIT

This is a **designed S1 fixture, not an executed result or a general optimizer milestone**. Start with one ordered helper that borrows a caller SRAM, allocates a one-cell local SRAM, initializes it before reading, and performs an ordered write through the borrowed handle. Invoke it at two call sites and from a statically bounded four-iteration sequential loop. Vary the input/iteration values to expose value-remapping or ordering errors, and inspect logical identity/lifetime records separately for state isolation. A fixture-only registered inlining/ordered expansion rule duplicates owned regions and substitutes explicit captures, result binders and token chains. S1 need not implement a general inliner or unroller to exercise that candidate-editing mechanism. S2 extends the same fixture mechanism to reduction contribution effects and preservation of the declared tree; S9 still owns broad optimization/search.

- Rebuild the **actual** `RecordIndex` (definitions, ordered uses, parents and callers) and verify unique ownership, references, dominance, exact token threading, signatures and live borrowed capabilities. Generated region/op IDs are fresh within the candidate revision. Copying a local allocation operation creates a fresh compile-time allocation-site ID with source/transform lineage; substituting a borrowed handle preserves the caller's backing identity.
- A static rewrite records the correspondence of call/iteration activation paths; it does not allocate runtime activations or generations. On execution, each local resource is identified by `(allocation_site_id, activation_path, generation)` and has its own lifetime/state. Equal numeric generation counters at distinct sites/activation paths are legal. The negative is collapsing the **full identity or state** of two dynamic activations, not merely reusing the numeral `0`. Retain logical activation correspondence when inlining removes a physical call frame.
- Account for every old requirement as retained under substitution, replaced with checked implication, or discharged with a checked certificate. Deleted nodes retain origin/transform lineage. Compare independently specified outputs and ordered effects with the untransformed case, and check that invalid candidate publication leaves the old canonical bytes, provenance and query index usable and unchanged.
- Include a stale-fact mutant: keep an access operation ID but change its remapped view/extent dependency, then attempt to reuse the old revision's bounds/totality proof to remove its guard. The publication/cache checks must reject that reuse or recompute the obligation; matching an operation ID alone is insufficient. Include an alias mutant that gives a borrowed capture a fresh backing ID, and the activation-state collapse mutant above.

Report separate measured costs for editing/remapping, required index construction, requirement/provenance transfer, verification and publication, with the live revision/candidate footprint. Include any index omitted or reused and its dependency justification. These are attributed fixture costs; the small fixture does **not** satisfy the 100k “ordinary optimization” workload or any complete R007 budget. Run R007's actual supported workloads separately and report their complete costs; carry this fixture's invariants into the scaled workload rather than extrapolating its latency.

The roadmap owns the stage exits and per-scope claims. Its completion audit must reject a named gate without linked positive, negative/mutant and execution evidence, and reject an unqualified all-family representation claim while `REP-S5` or a required `REP-S6(scope)` remains pending.

Preserve xDSL's exact prior packaging/mechanics archive as optional-adapter research evidence. An experiment pin does not require a core dependency. The canonical Spatial schema, full intended language coverage, exact numeric/state contracts, HLS responsibility, and professor adoption boundary remain unchanged.

## Reproduction archive

[Download the runnable probes and machine-readable measurements](<50 - Python Rewrite/60 - Validation/assets/2026-10-03-compiler-representation-probes.zip>). Archive SHA-256: `7a0c8baf1a92f34d617ea7023364a58cff08db59e01645642aa7623d6fb30bd8`. The archive contains the generators, both representations, semantic verifier, local/dense transformations, hand-derived control, isolation checks, all timing samples, all fresh-process memory results, machine/dependency records, a summary and a per-file SHA-256 manifest. The README documents the pinned environment, sequential commands and limitations. It includes no production compiler or third-party package.
