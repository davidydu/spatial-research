---
type: design
project: spatial-spec
date: 2026-07-09
status: active
---

# Phase 0 Language Contract

Related: [[2026-07-07-fundamental-design-review]],
[[2026-06-27-rust-spatial-rewrite-roadmap]],
[[2026-07-07-session-resume-guide]], [[progress-log]].

The project goal remains the full Spatial compiler rewrite in Rust with a
teachable high-level DSL; EE109 is the first acceptance ladder, not the final
boundary. The rewrite has completed the contract half of compositional-
inversion Phase 0. Authoritative repo artifacts:

- `spatial-rs/docs/language-spec.md`
- `spatial-rs/docs/compatibility-bridges.md`
- `spatial-rs/docs/adr/0001-restricted-const-eval.md`
- `spatial-rs/docs/adr/0002-file-cli-host-runtime.md`
- execution plan:
  `spatial-rs/docs/superpowers/plans/2026-07-09-phase0-language-contract.md`
- canonical-corpus implementation plan:
  `spatial-rs/docs/superpowers/plans/2026-07-09-phase0-canonical-corpus-migration.md`

Rust commits:

- `a6562ddd99272c10a0771d4c0f55cc8a7029ea0b` - plan checkpoint;
- `4505e7cf4fd463bdc7348c8e26478aa6ab489a2e` - four reviewed contract artifacts;
- `84991df280dc1248c96f3a2d4c3473ad3be8e1ee` - README/checklist/roadmap routing and checked plan state.
- `41cdfb7a` - reviewed Phase 0 canonical-corpus implementation plan.
- `15321092f08a50574892719072ca73a958b23e48` - C21 strict/macro ingress implementation.
- `7408ce9b` - C21 ledger, roadmap, and execution-plan checkpoint.

## Ratified Surface

- Domain syntax, not implementation-language witnesses: `Size` and
  `FixPt<Signed,24,8>` replace `usize` and `FixPt[TRUE,_24,_8]` canonically.
- One explicit accelerator body, lowercase controllers/commands, PascalCase
  hardware memories, half-open `..` ranges, and arrow transfers between views.
- `reduce`/`fold`/`memreduce` expose `init` plus `using`; `memfold` uses its
  existing accumulator plus `using`. Value blocks use `yield`.
- Statement `if` may omit an empty `else`; value-producing `if` requires it;
  `mux` is compatibility.
- Window operations are `reset ... when` and `shift ... <-`.
- Runtime DRAM extents link to scalar inputs and are checked against exact
  invocation buffer lengths.

## Ratified Compiler Boundaries

- Restricted target-independent `Size` const evaluation only; no staged
  Scala/Rust host language.
- File CLI: `check`, `build`, and `run`; `run` uses `spatial.run.v1` JSON and
  defaults to the controller-tree interpreter.
- Vitis remains explicit validation, never part of ordinary `run`.
- The manifest remains the ABI/evidence contract, not board runtime config.

## Review And Evidence

Two read-only Sol Ultra reviewers covered grammar, semantics, the 39-source
bridge crosswalk, const evaluation, CLI/runtime data, ABI, and pedagogy under
the reduced session concurrency cap. Every Critical and Important finding was
corrected and its owning lane rerun before commit.
The session-local model choice did not change the standing future-session default.

Local gates passed: format, the full locked test suite, clippy with `-D warnings`,
default examples, 39-member dry-run/plan, imported evidence validation, and
diff/path hygiene. Imported evidence remains
`2026-07-05-current-head-76158dd7-39-program` with
`resource_fit=37/39`, `over_budget=2`, `ii_caveated=14`.

## Open Phase 0 Work

The canonical-corpus spelling migration remains open and now has a reviewed
eleven-checkpoint execution plan in Rust commit `41cdfb7a`. C21 is complete:
strict text rejects direct `: =`, while a doc-hidden `accel!` transport ingress
normalizes only lexer-confirmed stringify spacing. Scalar and memory Program,
HLS, and v0 manifest parity are pinned. The remaining implementation surface
is C01-C13, C16, C20a, and C22 parser negatives, not only the seven legacy
GEMMs. The next checkpoint is ADR 0001 C01 `Size`.

Later checkpoints implement ADR 0001 `Size`, parametric fixed point, typed
requirements, canonical schedules/value blocks/stencil commands, typed memory
views and GEMM MemFold, mandatory `accel`, alias retirement, then the closed
C22 grammar. The seven GEMMs remain the highest-risk subset. After Phase 0,
begin controller-tree IR, interpreter, C20b shared invocation enforcement, and
C23 manifest adaptation. Name/classifier/manifest couplings
C14/C15/C17/C18/C19 and architecture-wide C24 remain later retirement debt.

Two reduced-concurrency audit agents mapped frontend and corpus/proof
dependencies; one focused reviewer cleared the final plan after corrections
for identifier freedom, harness-equality ownership, per-commit local gates,
and the explicit session model override. This session is capped at two
concurrent subagents using `gpt-5.6-sol` with ultra reasoning.

Boundary: normative docs changed; currently implemented compiler acceptance,
parser behavior, checked IR, generated HLS, manifests, roster membership, and
vendor evidence did not. No fresh EC2/Vitis run was required.
