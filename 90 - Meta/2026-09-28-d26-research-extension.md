---
type: design
title: "D-26 follow-up — decision method, debate and evidence"
date: 2026-09-28
status: research-complete
related:
  - "[[D-26-final-architecture]]"
  - "[[D-26-professor-brief]]"
  - "[[D-26]]"
  - "[[D-26-12-simulator-spike]]"
---

## Scope and authority

On 2026-09-28 David requested continued research and Codex-only debate to produce one final architecture proposal for professor approval, consolidate the research and update the documentation website. This extends the earlier meeting-cut stopping point. He also specified that maintenance skills are not a concern: assume the team has the necessary skills.

The selected proposal is [[D-26-final-architecture|R-E: source-captured Python kernels over one Rust semantic core]]. Architecture implementation remains pending professor approval. Existing documents are historical evidence, not additional user instructions. In particular, the older Claude-writer assignment and the meeting-cut stop are superseded by the current request.

No weights were filled in retroactively. The original D-26 question, protocol, k=10 threshold and mistake list are unchanged. The new source-only Python workflow is a design refinement, not an undisclosed replacement of the old examples or their concept counts. The original audit remains scoped to its original files and claims; it is not automatically an audit of this extension.

## Decision method

The engineering decision applies these priorities openly:

1. Preserve the specified hardware meaning, exact arithmetic, effect order, proof rules and actionable diagnostics.
2. Keep one authoritative semantic implementation and one public student surface.
3. Address the professor's expressed interest in familiar student authoring; do not confuse that interest with a confirmed Python-only requirement or a measured learning result.
4. Retain useful implementation assets and native runtime headroom without treating repository size as sunk-cost justification.
5. Accept bounded frontend/provenance/packaging work, with explicit conformance gates.

These are stated product priorities, not pre-registered numerical weights. They support a firm architecture choice under incomplete empirical evidence. They do not prove that one architecture dominates under every possible course objective.

## Debate and resolution

| Review round | Strongest challenge | Resolution in the proposal |
|---|---|---|
| Independent architecture ranking, drafted before reading the earlier recommendation | R-X avoids a cross-language source boundary and makes independent semantics visible | Accepted as R-X's real advantage. Rejected any inference that it necessarily checks hardware better or teaches better. |
| Independent Python-surface case | A closed token-backed AST retains the same hardware information; R-X still owes a complete parser | Chose R-E to prioritize familiar authoring. Capture files/cells without executing functions, imports, annotations or defaults. Rust alone resolves and checks Spatial meaning. |
| Direct challenge between reviewers | Python-looking scope and effect order can mislead; internal external fixtures still cost work | Preserve explicit intrinsics and a differences guide. Budget the internal parser, every paired lab and all six original E guarantees. One reviewer retains R-X's simplicity preference; no artificial unanimity is claimed. |
| Independent plan review | Thirteen mappings are not exhaustive frontend coverage; nonexecution must be tested; implicit capture errors could accidentally duplicate name resolution | Require a complete canonical construct inventory, adversarial nonexecution fixtures and shared-Rust unresolved-name rejection. Add direct-DRAM valid controls and precise approval/status language. |
| Independent benchmark reproduction and protocol review | Small toy ratios can be overstated; the original protocol expressly allows toy spike evidence | Recomputed all ten outputs and rebuilt/repeated both runtimes. Report absolute times and confounds. Count the observed k=10 breach under the registered toy-spike rule without turning it into a universal Python-core prohibition. |

The discussions are part of the review process. Technical claims are grounded in pinned source, executed experiments and the linked research, not in a subagent's authority.

## New empirical evidence and protocol correction

[[D-26-12-simulator-spike]] adds a preregistered, bounded comparison of two recursive interpreters over identical runtime-loaded IR. Primary cases are dense32, nested-fold32 and fixed-point GEMM32, with tile16. Declared scaling probes are dense256, fold256 and GEMM64. Exact independent scalar oracles and overflow/fraction cases pass in both runtimes; a separate reviewer freshly rebuilt and reproduced them.

The primary Python/Rust execution ratios are 21.75×, 23.42× and 51.20×. GEMM32 is 67.315 ms versus 1.315 ms; GEMM64 is 545.894 ms versus 10.517 ms. These are steady-state interpreter times on one arm64 macOS host, excluding source processing, startup and transport. Allocation policy, timer/lifetime asymmetry, fixed language order and limited operation coverage are disclosed in the note. Small absolute times matter as much as the ratios for interactive use.

**Interpretation correction after measurement:** the first draft said that a full competing compiler was needed before the registered k=10 condition could count. That was too strong: the original research design's angle 12 explicitly permits a toy-versus-toy spike on one lab, and D-26 accepts spike evidence. The tested pure-CPython interpreter route therefore **triggers the registered negative performance condition** and counts against P-* under that rule. We do not add a full-compiler prerequisite after seeing the result. The threshold, workloads, code and primary results are unchanged.

That registered result is an engineering selection rule applied to this measured route. It is not proof that every Python compiler must be slow: Python semantic ownership with a coarse native executor or generated simulation remains an unmeasured alternative. It does not distinguish R-X from R-E. The opposite conjunction making R-* lose is not met: full error parity is still absent and the measured interpreter is outside the bound.

The archive preserves the experimental sources, preregistration, shared IR, raw results, hashes and independent audit evidence. Its README carries the interpretation correction separately from the unchanged frozen preregistration. Packaging a downloadable research artifact is a follow-up documentation deliverable; it does not add the throwaway interpreter to the production compiler or alter its architecture. The earlier scratch-only experiment rule remains visible as historical protocol; the public archive is explicitly an extension for reproducibility.

## What remains unmeasured

No novice learning/repair trial, timed staff productivity trial, cross-platform wheel test, full Python frontend, complete shared checker, end-to-end latency measurement, new Vitis run or cycle-accurate simulator is supplied by this research. First-rating mapping designs and an independent citation audit are not two independent mapping ratings. The benchmark does not fill those gaps.

These limits affect the claims and release gates. They do not require another open-ended architecture survey before selecting an implementation direction. The professor can approve the concrete plan knowing which evidence exists and which acceptance work follows approval.

## Source trail

- [[D-26-05-boundary-design]]: unresolved AST versus text/checked IR, semantic ownership and provenance.
- [[00 - Python Mapping Overview]]: thirteen first-rated designs and deferred constructs; no implementation parity claim.
- [[D-26-02-student-surface-comparison]] and [[D-26-03-error-paths]]: unchanged listings, concept rubric, real error transcripts and limits.
- [[D-26-08-cost]]: useful assets versus incomplete general compiler; no invented person-weeks.
- [[D-26-12-simulator-spike]] and [reproduction archive](assets/d26-interpreter-spike.zip): new execution evidence and independent repeat.
- `spatial-rs@eb49d8b:crates/spatial-rs-core/src/compiler.rs:30-67`: current classifier pipeline.
- `spatial-rs@eb49d8b:docs/language-spec.md:424-443`, `spatial-rs@eb49d8b:docs/language-spec.md:682-710`, `spatial-rs@eb49d8b:docs/language-spec.md:816-841`: normative proof, literal and effect constraints.
- [Python AST](https://docs.python.org/3/library/ast.html), [Exo tutorial](https://exo-lang.dev/tutorial.html), [Maturin binary wheels](https://www.maturin.rs/bindings.html) (accessed 2026-09-28): syntax/source mechanisms, a real Python-syntax compiler precedent and executable packaging. These establish mechanisms, not Spatial release readiness or learner outcomes.

## Documentation consolidation

The homepage and top-level index now lead with the professor brief, selected architecture, research method and implemented/proposed distinction. D-26, the provisional recommendation, older overlays and the resume guide point to the follow-up without rewriting historical findings. The website excludes internal validator scripts and deliberately malformed fixtures. Its README now describes the actual public-clone deployment workflow.

Publication and local build verification are recorded in [[progress-log]] after they run; this method note does not itself assert a successful public deployment.
