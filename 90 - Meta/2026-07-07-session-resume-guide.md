---
type: runbook
project: spatial-spec
load_priority: high
date: 2026-07-07
---

# Session Resume Guide (Rust Rewrite, EE109-First Inversion)

For any Codex or Claude session picking up the Rust rewrite. Read this, then
[[2026-07-07-fundamental-design-review]], then the checklist. This
supplements, does not replace, [[workflow]] and [[progress-log]].

> [!important] 2026-07-07 route change (later session)
> David adopted the [[2026-07-07-fundamental-design-review|fundamental design review]]:
> the recognition/classifier architecture is being **inverted** into a
> compositional compiler (controller-tree IR + interpreter + structural
> backend). The "Do Next" list below was rewritten accordingly — the previous
> version (B2 classifier ingress → G7/G6/G9 perturbation slices) is
> superseded. MVP-B boxes and the evidence policy are unchanged; only the
> route changed. Authoritative plan:
> `spatial-rs/docs/superpowers/plans/2026-07-07-compositional-core-inversion-roadmap.md`.

## Where Things Stand (2026-07-09)

- Rust repo: `/Users/david/Documents/David_code/spatial-rs`, branch
  `David/HLS-spatial`, at `aa9839c5`
  (`Record raw Size syntax checkpoint`). Phase 0's normative
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
- Full local gates are green at the language-contract checkpoint: format,
  locked workspace tests, clippy with `-D warnings`, default examples,
  39-member dry-run/plan, and imported-evidence validation.
- **Inversion Phase 0 contract half: complete.** Language spec, 39-source
  compatibility crosswalk, restricted-const ADR, and file/runtime ADR are
  ratified. Source-spelling migration remains open; name/classifier retirement
  is tracked for Phase 2/3. C21 strict-versus-macro ingress is complete in
  `15321092`: direct `: =` is rejected without breaking `accel!`. No HLS,
  manifest, roster, or vendor-evidence payload changed. C01 Checkpoint 2A is
  also complete in `2ee3842d` + `8c814cae`: raw decimal tokens and the typed
  const-expression arena are landed, but evaluation/typed lowering are not.
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
   in checkpoint order. C21 and C01 Checkpoint 2A are complete; start 2B with
   ADR 0001 name resolution/evaluation and do not jump directly to the seven
   GEMMs. The remaining plan covers
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

- Host alias `[ec2-alias]` in `~/.ssh/config`
  (`[ec2-host — see private/ec2-lane.md]`, user `ubuntu`, key
  `[ssh-key — see private/ec2-lane.md]`). **Restored 2026-07-07 (later
  session): the old `[old-ec2-host — see private/ec2-lane.md]` / `[old-ssh-key]`
  entry was dead; the live us-west-2 host has Vitis 2025.1 at
  `/tools/Xilinx/2025.1`, cargo/rustc 1.75, and the bundle/run-script lane
  layout under `~/`. Stale `~/spatial-rs-runs` workspaces and old bundles
  (72G+) were deleted after confirming every checkpoint was already imported
  under `docs/vitis-validation/`; disk is now ~70% used with 74G free. The IP
  is still dynamic across stop/start unless an Elastic IP is attached.**
- Reachability check:
  `ssh [ec2-alias] "source /tools/Xilinx/2025.1/Vitis/settings64.sh; vitis-run --version"`.
  If the hostname changed, update `~/.ssh/config` first.
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
  subagent workflow. David explicitly overrode the model for the 2026-07-09
  session to `gpt-5.6-sol` with ultra reasoning and capped concurrency below
  the former six-agent waves; that session-local override does not silently
  rewrite future-session policy.
