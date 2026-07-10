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

Rust commits:

- `a6562ddd99272c10a0771d4c0f55cc8a7029ea0b` - plan checkpoint;
- `4505e7cf4fd463bdc7348c8e26478aa6ab489a2e` - four reviewed contract artifacts;
- `84991df280dc1248c96f3a2d4c3473ad3be8e1ee` - README/checklist/roadmap routing and checked plan state.

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

The canonical-corpus spelling migration remains open. It covers active source-
surface IDs C01-C13, C16, C20a, and C21, plus C22 parser negatives, not only
the seven legacy GEMMs. The seven GEMMs are still the highest-risk subset.
Migration must implement missing canonical ingress, apply each ledger row's
proof gate, and delete/demote migrated spelling bridges. Then begin Phase 1
controller-tree IR, interpreter, C20b shared invocation enforcement, and C23
manifest adaptation. Name/classifier/manifest couplings C14/C15/C17/C18/C19
and architecture-wide C24 remain later retirement debt.

Boundary: normative docs changed; currently implemented compiler acceptance,
parser behavior, checked IR, generated HLS, manifests, roster membership, and
vendor evidence did not. No fresh EC2/Vitis run was required.
