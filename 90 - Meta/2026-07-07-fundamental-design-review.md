---
type: design
project: spatial-spec
date: 2026-07-07
status: active
approved_by: David (2026-07-07 session, "review the design fundamentally" → adopted)
repo_commit: f35a1bdb
related:
  - "[[2026-06-27-rust-spatial-rewrite-roadmap]]"
  - "[[2026-07-07-lab-functionality-mvp-checklist]]"
  - "[[2026-07-07-rust-gemm-dynamic-dimension-slice-contract]]"
  - "[[2026-07-07-session-resume-guide]]"
---

# Fundamental Design Review: Recognition Must Become Compilation

Full text lives in the repo:
`spatial-rs/docs/2026-07-07-fundamental-design-review.md`. Successor plan:
`spatial-rs/docs/superpowers/plans/2026-07-07-compositional-core-inversion-roadmap.md`.
This note is the vault-side decision record; the repo docs are authoritative
for details and citations. The reviewed checkpoint is committed on
`David/HLS-spatial` as `f35a1bdb` (`Adopt compositional core inversion`).

## Trigger

David asked for a design review **against the true goal** — a full Rust
rewrite of Spatial with teachable high-level abstraction syntax, EE109 labs
as priority functionality — deliberately setting aside the MVP-A/MVP-B
framing. He then adopted the findings and directed that they be recorded and
that stale plans be updated.

## Findings (summary)

1. **The semantic core is a program recognizer, not a compiler.**
   `ProgramKind` is a 25-variant whole-program enum (`ir.rs:29-55`); `Stmt`
   is an enum of feature payloads with `Lab3Part1Convolution` as a nullary
   variant (`ir.rs:150-185`); ~18K LOC of classifiers fail-close everything
   off-pattern. Patterns do not compose; Spatial is compositional. Marginal
   cost per accepted variation stays constant forever — visible as the
   alias/spelling-pin fraction of the 404 commits. Checklist items G6/G7/G9
   ("constant freedom") are symptoms: in a compiler, constants being
   changeable is what constants are.
2. **Surface syntax is drifting away from teachability.** The canonical
   Tile-K GEMM is seven nested `foreach` loops with manual index arithmetic
   (`examples/ee109/src/lib.rs:761-815`) — the Scala lab original says
   `MemFold` in a fraction of the lines, and the abstraction *is* the
   curriculum. Grammar has accreted via bridges instead of being designed.
   (The newer `memfold ... with ... over ...` + arrow bulk-IO forms are good
   and should become canonical.)
3. **HLS leaks into the core IR** (`Type::hls_value_type`, `ap_fixed`
   preludes in `ir.rs:105-117`) and emitters are per-family string templates
   — blocking composition and backend evolution, and re-importing HLS QoR
   unpredictability (observed 256 vs 220 DSP auto-unroll blowups).
4. **No executable reference semantics** — per-family `oracle.rs` functions
   instead of an IR interpreter (which would also be the fast teaching
   simulator; labs ask for cycles/II).
5. **No compile-time resource legality gate** (previously risk C1; two roster
   canaries + two Stage-A representatives over DSP budget, found only
   post-synthesis).
6. **No standalone compile entry point** (G10; cargo-test-only).

## Decision

**Invert, don't restart.** Keep wholesale: the verification stack (oracle,
goldens, Vitis evidence + validator), the 39-program corpus and all vendor
evidence, the `ResolvedHir` facts layer, fail-closed discipline, the vault
spec. Replace the load-bearing structure: controller-tree IR (Spatial's own
model) + IR interpreter as reference semantics + compositional backend behind
a backend-neutral boundary. Classifiers retire family-by-family into legality
diagnostics and regression fixtures. Surface syntax gets a written spec with
one canonical spelling per construct before the inversion starts.

The recognition phase is recorded as the **right tracer strategy that did its
job** (corpus, HLS idioms, evidence infrastructure in 11 days), not as an
error — the error would be leaving it load-bearing. This also honors the
2026-06-27 roadmap's own framing ("avoid growing the compiler by adding
endless exact lab recognizers"), whose mechanism never inverted.

## What changes in practice

- **Paused in their old form:** G6/G7/G9 perturbation slices against
  classifiers; G8 Stage B2/B3 as classifier-ingress extensions (B1 backend
  work + evidence carry over into runtime-valued bounds); new spelling
  pins/bridges; no-HLS-drift refactors inside classifier modules slated for
  deletion.
- **Unchanged:** MVP-B checklist boxes, graduation standard, evidence policy,
  EC2/Vitis lane, paired-commit + progress-log conventions.
- **Next work:** inversion roadmap Phase 0 (language spec + surface freeze)
  and Phase 1 (controller-tree IR + interpreter with oracle-parity over the
  39-program corpus).

## Artifacts written/updated 2026-07-07

- New: `spatial-rs/docs/2026-07-07-fundamental-design-review.md` (full review).
- New: `spatial-rs/docs/superpowers/plans/2026-07-07-compositional-core-inversion-roadmap.md`
  (successor plan, Phases 0-5, MVP-B route mapping).
- Updated: `spatial-rs/docs/superpowers/plans/2026-07-03-full-rust-spatial-rewrite-roadmap.md`
  (superseded-in-part banner; history preserved).
- Updated: `spatial-rs/docs/lab-functionality-mvp-checklist.md` ("2026-07-07
  Route Change" section; boxes and standards untouched).
- Updated: [[2026-07-07-session-resume-guide]] ("Do Next" now points at the
  inversion phases).
- Updated: [[2026-06-27-rust-spatial-rewrite-roadmap]] (status note).
- Logged: [[progress-log]] entry for 2026-07-07.
