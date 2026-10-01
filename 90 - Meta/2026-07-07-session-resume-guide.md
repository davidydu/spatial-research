---
type: runbook
project: spatial-spec
load_priority: high
date: 2026-07-07
---

# Session Resume Guide

This supplements [[workflow]] and [[progress-log]]. Use the current checkpoint below; the older Rust implementation queue is retained as history.

## Current research checkpoint — 30 September 2026

[[D-27]] records the **pure Python Spatial** direction reported after the professor discussion. Read [[00 - Python Rewrite Index]], [[01 - Python Research Plan]], and [[PY-R001 - Programming Model Study]]. Research the programming model before compiler design and HLS lowering. Use Codex-only agents and local-file checks. The Python API and detailed architecture remain open; do not resume the old Rust queue as current work.

The research vault and website have been published under `davidydu`; older credential-blocked entries below are historical. See [[progress-log]] for dated publication evidence.

## Historical Rust route

> [!important] 2026-07-07 route change (later session)
> David adopted the [[2026-07-07-fundamental-design-review|fundamental design review]]:
> the recognition/classifier architecture is being **inverted** into a
> compositional compiler (controller-tree IR + interpreter + structural
> backend). The "Do Next" list below was rewritten accordingly — the previous
> version (B2 classifier ingress → G7/G6/G9 perturbation slices) is
> superseded. MVP-B boxes and the evidence policy are unchanged; only the
> route changed. Authoritative plan:
> `spatial-rs/docs/superpowers/plans/2026-07-07-compositional-core-inversion-roadmap.md`.

## Historical research checkpoint (2026-09-28; superseded by D-27)

The final research recommendation is [[D-26-final-architecture|R-E: source-captured Python kernels over one Rust semantic core]]. Read [[D-26-professor-brief]] and [[2026-09-28-d26-research-extension]] first. Architecture implementation awaits professor approval; do not resume the historical implementation queue on the basis of this research proposal alone. Current compiler checkpoint is `eb49d8bc`; the thin CLI implements text `check`. The older checkpoints below are retained as history. Publication/build status is recorded in [[progress-log]].

## Historical implementation checkpoint (2026-07-12)

- **D-26 host-language research (2026-09-25):** design [[2026-09-25-python-rust-architecture-research-design]]; plan [[2026-09-25-d26-research-dispatch]]; record [[D-26]] (historical meeting cut audited 2026-09-28; final follow-up proposal linked above). Evidence and corrections: [[2026-09-25-d26-citation-audit]]. The professor brief now presents the final research recommendation; implementation still awaits approval. The vault's publication gate ran on 2026-09-25 (history scrubbed and verified); the push itself is pending a `davidydu` GitHub credential — see `private/plans/`.
- Rust repo: `/Users/david/Documents/David_code/spatial-rs`, branch
  `David/HLS-spatial`, at `2e6dba95`
  (`Record Size evaluation checkpoint`). Phase 0's normative
  contract is committed in `4505e7cf4fd463bdc7348c8e26478aa6ab489a2e`;
  its reviewed contract plan is `a6562ddd99272c10a0771d4c0f55cc8a7029ea0b`,
  and the implementation plan is
  `docs/superpowers/plans/2026-07-09-phase0-canonical-corpus-migration.md`.
  (`.codex/` remains an untracked local artifact; leave it untouched.)
- **MVP-A (every lab program → Vitis-validated): complete.** 39-program roster,
  anchor `docs/vitis-validation/2026-07-05-current-head-76158dd7-39-program/`,
  `resource_fit=37/39`, `over_budget=2`, `ii_caveated=14`.
- **MVP-B (lab functionality/knobs): open.** Tracked by
  `docs/lab-functionality-mvp-checklist.md` sections G1-G11. G1 complete;
  G2 complete; **G8 Stage A (serial static-shape family) ticked with four
  selected Vitis evidence dirs
  (`docs/vitis-validation/2026-07-07-selected-family-*-e2536a1b/`)**; the
  rest open.
- Full local gates are green at C01 Checkpoint 2B: format,
  locked workspace tests, clippy with `-D warnings`, default examples,
  39-member dry-run/plan, and imported-evidence validation.
- **Inversion Phase 0 contract half: complete.** Language spec, 39-source
  compatibility crosswalk, restricted-const ADR, and file/runtime ADR are
  ratified. Source-spelling migration remains open; name/classifier retirement
  is tracked for Phase 2/3. C21 strict-versus-macro ingress is complete in
  `15321092`: direct `: =` is rejected without breaking `accel!`. No HLS,
  manifest, roster, or vendor-evidence payload changed. C01 Checkpoint 2A is
  also complete in `2ee3842d` + `8c814cae`: raw decimal tokens and the typed
  const-expression arena are landed. C01 Checkpoint 2B is complete in
  `5295f5ce` + `b13600f4` + `73ceeae6` + `feb44688`: restricted `Size`
  evaluation, lexical/source-ordered names, E0500-E0505, poison handling,
  strict recovery, and sealed arena ownership are landed. Typed HIR/E0506 and
  corpus migration remain open.
  See
  [[2026-07-09-phase0-language-contract]].

## Two Completion Definitions

**EE109-first acceptance done** means the MVP-B checklist: every non-stretch
lab-functionality box closes under its six-point graduation standard, G10's
compile command exists, and current-roster Vitis evidence is refreshed where
required. This is the first acceptance ladder.

**Full Rust rewrite done** means the specified Spatial language families lower
compositionally through backend-neutral controller IR, classifiers/
`ProgramKind` are no longer the semantic boundary, the interpreter defines
reference behavior, and expansion is governed by the full Spatial requirements
corpus. MVP-B completion does not imply full-rewrite completion.

## Do Next (priority order — rewritten 2026-07-07 after the design review)

Execute `spatial-rs/docs/superpowers/plans/2026-07-07-compositional-core-inversion-roadmap.md`
in phase order:

1. **Finish Phase 0 -- execute the reviewed canonical-corpus plan.** Follow
   `spatial-rs/docs/superpowers/plans/2026-07-09-phase0-canonical-corpus-migration.md`
   in checkpoint order. C21 and C01 Checkpoints 2A-2B are complete; start 2C
   with typed HIR/fixed-width plumbing and checked E0506 embedding, then migrate
   all 33 affected sources in 2D. Do not jump directly to the seven GEMMs. The
   remaining plan covers
   active source-surface IDs C01-C13, C16, and C20a plus C22 parser negatives,
   with Program/HLS/manifest equality and exact legacy-negative closure. Begin
   Phase 1 afterward; C20b/C23 join shared invocation/manifest paths and
   C14/C15/C17/C18/C19/C24 retire later.
2. **Phase 1 — controller-tree IR + interpreter.** Backend-neutral core types
   (parametric FixPt; HLS strings out of `ir::Type`), controller-tree IR with
   static-or-runtime dimension bounds (absorbs the B1 design from
   [[2026-07-07-rust-gemm-dynamic-dimension-slice-contract]]), interpreter
   with oracle-parity tests over all 39 corpus programs. Dark-launched; no
   shipped-artifact change.
3. **Phase 2 — compositional backend, first family.** Structural C++
   emission behind a backend trait; route `Dense1dScalarMul` end-to-end;
   byte-equality or selected Vitis run per the unchanged evidence policy;
   retire the Dense1d classifier into diagnostics + fixtures.
4. **Phase 3+ — family-by-family migration** per the plan's order (scalar →
   reduce/fold → memreduce/memfold → FIFO → LUT → FSM → rank-2/Tile-K with
   runtime dims → stencil). G3-G9 boxes close as side effects; then Phase 4
   (par legality + resource model gates) and Phase 5 (CLI, `spatial-rs run`
   simulator, diagnostics catalog, tutorial).

**Paused in their old form** (do not pick up): G8 B2/B3 as classifier-ingress
slices, G6/G7/G9 perturbation slices against classifiers, new spelling
pins/bridges, no-HLS-drift refactors inside classifier modules slated for
deletion. B1's landed backend work and evidence carry over.

Still true from the earlier iteration log: the bottleneck is the
frontend/HIR/IR interface, not DSP tuning — the inversion is the systematic
answer to that finding.

## EC2 / Vitis Lane

- Host, user, key path, and the reachability check live in `private/ec2-lane.md`
  (gitignored; not on the public site). The host is an EC2 instance with Vitis
  2025.1 at `/tools/Xilinx/2025.1` and cargo/rustc 1.75; its IP is dynamic
  across stop/start unless an Elastic IP is attached.
- Any slice that changes generated HLS or adds a roster member needs a selected
  `run-vitis-validation --kernel ... --execute --mode both` run before its box
  is ticked; roster promotion needs a full-roster refresh. See the checklist
  Evidence Policy and the contract's EC2 steps.

## Conventions To Keep (so the next session can pick up)

- Red-first TDD; full local gates before commit: `cargo fmt --all --check`,
  `cargo test --locked`, `cargo clippy --all-targets --locked -- -D warnings`,
  the two `ee109-examples` binaries, evidence validate, `git diff --check`.
- Paired commits: Rust repo commit + vault progress-log entry with the exact
  commit hash and the verification transcript. New slices get a slice-contract
  note in `90 - Meta/` before coding.
- Honest boundaries: state what did NOT change (HLS/manifest/roster/evidence)
  and never tick a box on a claim — name the tests and, where required, the
  evidence directory.
- Keep the project-default reviewers in the loop when executing under a
  subagent workflow. David explicitly overrode the current July 9-12 session
  to `gpt-5.6-sol` with ultra reasoning and capped concurrency below the former
  six-agent waves; that session-local override does not silently rewrite
  future-session policy.
