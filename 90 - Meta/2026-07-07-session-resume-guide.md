---
type: runbook
project: spatial-spec
load_priority: high
date: 2026-07-07
---

# Session Resume Guide (Rust Rewrite, MVP-B)

For any Codex or Claude session picking up the Rust rewrite. Read this, then
the checklist, then the flagship contract. This supplements, does not replace,
[[workflow]] and [[progress-log]].

## Where Things Stand (2026-07-07)

- Rust repo: `/Users/david/Documents/David_code/spatial-rs`, branch
  `David/HLS-spatial`, clean tree at commit `e934bd71`. (`.codex/` is an
  untracked local loop artifact; leave it untracked unless David says
  otherwise.)
- **MVP-A (every lab program → Vitis-validated): complete.** 39-program roster,
  anchor `docs/vitis-validation/2026-07-05-current-head-76158dd7-39-program/`,
  `resource_fit=37/39`, `over_budget=2`, `ii_caveated=14`.
- **MVP-B (lab functionality/knobs): open.** Tracked by
  `docs/lab-functionality-mvp-checklist.md` sections G1-G11. G1 complete;
  G2 complete; the rest open.
- Full suite green: 15 suites, 1068 tests, 0 failures.

## The One Definition That Matters

"MVP done" = the MVP-B checklist. Do not treat any single lab program passing
Vitis as "done" — that is MVP-A and it is already finished. Every new slice
must close a named checklist box under the six-point graduation standard in
the checklist doc.

## Do Next (priority order)

1. **G8 GEMM dynamic dimensions** — the flagship, the only checked-lab-source
   gap. Execute [[2026-07-07-rust-gemm-dynamic-dimension-slice-contract]] from
   Stage A (static shape freedom), then Stage B (dynamic dims), then Stage C
   (par legality). Highest value; also the real test of whether the proof-fact
   infrastructure generalizes.
2. **G7 LUT value/dim freedom, G6 FSM constant freedom, G9 stencil
   coefficient/dim freedom** — parameterize the exact-constant families. Each
   is a bounded, non-speculative slice with clear acceptance criteria in the
   checklist.
3. **G10 compile CLI** — `spatial-rs build <file>`; today the only entry
   points are cargo test binaries. Needed for an actual student-facing MVP.
4. **G11 evidence tier** — add `cosim_design` and one implementation/export
   run on EC2 to convert csynth acceptance into board-fit truth.

Deliberately **not** next: more source-spelling alias pins, more no-HLS-drift
refactors, speculative body generalizations the labs do not exercise. The
iteration log already concluded the bottleneck is frontend/HIR interface
expansion, not DSP tuning.

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
- Keep gpt-5.5 xhigh reviewers in the loop when executing under a subagent
  workflow (project rule). The 2026-07-07 session ran solo on Claude Fable 5
  at David's explicit direction.
