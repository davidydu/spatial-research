---
type: design
project: spatial-spec
date: 2026-09-25
status: approved
approved_by: "David (2026-09-25 session, after a four-reviewer pass: rigor, domain, vault-fit, professor's advocate)"
revision: 2
related:
  - "[[2026-06-26-rust-first-spatial-dsl-overlay]]"
  - "[[2026-07-07-fundamental-design-review]]"
  - "[[2026-07-07-session-resume-guide]]"
  - "[[40 - Decision Queue]]"
---

# Design — D-26 Host-Language Architecture Research (Rust / Python)

## 0. Decisions taken 2026-09-25

| # | Decision | Decided |
|---|---|---|
| 1 | Pre-registration and meeting format | **Internal pre-registration** (David + the Rust-leaning instructor record weights before Wave 1; sensitivity reported), **single meeting** with the professor. His stated position from prior discussion is only "Python is easy to teach and easy for students to pick up" — a claim about the student surface, so a weights-and-falsifiers negotiation with him is disproportionate. |
| 2 | One code exception | **Build a thin `spatial-rs check <file>`** (ADR 0002 shape; text output with file:line and help) over the existing compile entry point, so the error-path study is real terminal output. Everything else stays no-code; throwaway spikes live in the scratchpad only. |
| 3 | Publication gate | **Scrub + rewrite history**: EC2 details to gitignored `private/`, redact the four tracked files, rewrite the never-pushed 349 commits with `git filter-repo`, verify, then push. Repo stays public. Separate gated task (§10); blocks any push. |
| 4 | Lab repositories | **Never enter the vault** (no path, hash, author, filename, or quoted line). David may consult them privately to confirm the mistake list and the Scala error baseline, recorded as "(confirmed against private course material; not cited)". |
| 5 | Models | **Claude general-purpose agents write** research notes and mapping entries; **Codex reviewers audit** citations and inference. |
| 6 | Scope | **Meeting cut first** (≈9 agent runs, §9); remaining angles continue after the meeting. |

## 1. Purpose

Ground the host-language decision in the discipline the vault applied to the
Scala→Rust mapping: pre-registered question, cited research, decision record,
then implementation. The output must (a) be able to settle the question in
*either* direction before anything is presented as a plan, and (b) serve as the
build spec for whichever surface/integration is chosen.

### The gap this closes

- 25 decision records (D-01..D-25) exist, each with ~10 cited research angles.
  The host-language question has none.
- `90 - Meta/2026-06-26-rust-first-spatial-dsl-overlay.md` lists "Do not use
  Python as the compiler-core owner" as a non-goal with no research behind it.
- `90 - Meta/2026-07-07-fundamental-design-review.md` asserts "The external-DSL
  choice itself is right for teaching … diagnostics are fully owned" without a
  comparison.
- Precedent coverage is two 27-line notes, every sentence tagged
  `(unverified)`, no URLs.
- `03-mvp-subset-recommendation.md` has said "Rust/Python+HLS rewrite" since
  May: the door was kept open at the framing level and never researched.

### What is true of the prototype today (stated up front in D-26 and on the site)

Verified 2026-09-25 against `spatial-rs` at `29f7bad8` (branch `David/HLS-spatial`):

- There is no `.spatial` file and no compiler command. The 45 programs live
  inside a Rust `accel! { … }` macro in `examples/ee109/src/lib.rs`, in the
  pre-canonical spelling (`usize` ×223, `sequential_foreach` ×8; the spec's
  `Size` and `seq foreach` ×0). A student can run nothing outside Cargo.
- The semantic core is a whole-program recognizer (`ProgramKind`, 22.5K lines
  of classifiers); the inversion into a compositional compiler is adopted but
  Phase 1 has not landed. The 39-program Vitis evidence is evidence for the
  *backend idioms and the verification harness*, not for a general compiler.
- 44 diagnostic codes exist; 13 are canonical (`E0300–E0304`, `E0309`,
  `E0500–E0506`: parse and `Size` evaluation). The legality codes students hit
  in week 3 (`E0311–E0315`: bounds, `par`, schedule) are specified, not
  emitted. Macro-path diagnostics carry the source name
  `<accel-macro-stringify>`, not a file and line.
- No CI, no release, no wheel: "students never need a Rust toolchain" is a
  goal, not a fact.

### Non-goals

- No production Python or Rust code, with the single exception in decision 2.
  Throwaway spikes live in the scratchpad, never the vault or the repos.
- The deck is not revised until the meeting cut of D-26 is audited.
- The July 7 inversion decision is not re-litigated; D-26 produces *inputs* to
  its Phase 1 (see §7), not changes to it.
- The vault's 23 pre-existing duplicate stems and 45 broken wikilinks are a
  separate cleanup.

## 2. The question and the option space

**D-26 — Which language hosts the compiler core, which surface do students
write, and how does Python integrate?**

Two axes, all six cells evaluated with the same angles; neutral labels, no
"status quo" or "baseline":

| | Surface: external DSL (X) | Surface: Python-embedded (E) | Surface: both (B) |
|---|---|---|---|
| **Core: Rust (R)** | R-X | R-E | R-B |
| **Core: Python (P)** | P-X | P-E | P-B |

P-E is the professor's stated lean; R-E is the compromise the two instructors
are circling; R-X is what exists in part today.

**Integration depth** (orthogonal, applies to every R-* cell; evaluated in
angles 5/6/9/11 and folded into the cell's row):

- I0 — CLI only (ADR 0002 `check`/`build`/`run`, JSON in/out).
- I1 — I0 + Python testbenches over the JSON envelopes; zero bindings.
- I1′ — the CLI shipped **as a wheel** (`maturin bindings = "bin"`, Ruff's
  model): `pip install`, no PyO3, no Rust toolchain for students.
- I2 — PyO3 bindings over exactly `check`/`build`/`run` with the ADR 0002
  envelopes (the Rust library API is a V1 deferral, so nothing else is bound).
- In — external DSL hosted in notebooks via a `%%spatial` cell magic / string
  API: the zero-frontend notebook path.

**Teachability has two audiences** and D-26 keeps them apart: students (the
surface — the professor's stated concern) and rotating maintainers/TAs (the
compiler). P-* cells can only win on the second.

### Embedding styles (evaluated, not pre-chosen; real systems are hybrids)

1. **Tracing / operator overloading** — the Python function runs and records
   staged ops. `__getitem__`/`__setitem__`/`+=` are interceptable; bare-name
   binding, `is`, and loop *structure* are not. `not`/`and`/`or`/`if`/`while`
   *do* reach `__bool__` — the hazard is the inverse of "cannot overload":
   objects are truthy by default, so an undefined `__bool__` **silently traces
   one branch** (Amaranth and JAX raise here — verify at pinned commits).
2. **Builder / context-manager API** — explicit construction
   (`with Foreach(0, N) as i:`; calyx-py). Verbose, fully explicit; control
   flow always ends up here under tracing (JAX `lax.cond`).
3. **AST transform** — parse the decorated function's source with `ast` and
   lower it (Allo, Exo, Taichi, Triton, PyMTL3 `@update`). Full syntax control,
   needs a real frontend, source-span mapping, and produces the recurring
   "looks like Python but isn't" complaint.

**Silently-divergent hazard class** (applies to 1 and partly 3): Python folds
all-literal subexpressions with Python semantics before any overload fires —
`-7 % 2 == 1` (spec: dividend sign), `7 / 2 == 3.5`, no fixed-width wrap,
`0 <= i < N` desugars to `and`. Every mapping entry records this class
separately from "not expressible".

Precedent relabels from the domain review: HeteroCL is a hybrid (tracing inside
`hcl.compute` + `with hcl.for_/if_` builders); Numba compiles bytecode; Chisel
is overloading + `when` closures. Angle 1 verifies each at the pinned commit.

## 3. Vault changes

All stems are unique vault-wide (the vault already has 23 duplicate stems that
Quartz resolves arbitrarily on the public site; this plan adds none).

| Path | Type | Purpose |
|---|---|---|
| `20 - Research Notes/50 - Decision Records/D-26.md` | `decision-record` | Pre-registration first (`status: pre-registered`), then findings, two sub-matrices + combination, recommendation, rejected alternatives, answers to the "case for" notes, Decision |
| `…/D-26-research/D-26-01a-precedent-python-over-core.md`, `D-26-01b-precedent-all-python.md`, `D-26-01c-precedent-external-dsl-over-core.md`, `D-26-02-…` … `D-26-13-…` | `research` | One note per angle (schema in §4) |
| `35 - Python Surface Mapping/00 - Python Mapping Overview.md` | `python-mapping-index` | Labels, method, coverage table (deferred entries listed as rows), embedding-style summary (no separate file) |
| `35 - Python Surface Mapping/NN - Python <Construct>.md` (8 construct entries + 5 cross-cutting entries) | `python-mapping` | Schema in §5 |
| `90 - Meta/reference-clones.md` | `reference` (new type) | Manifest: name, upstream URL, full SHA, tag, clone date, licence |
| `90 - Meta/plans/2026-09-25-d26-research-dispatch.md` | `plan` | Waves, framing-blind prompts, post-wave checklist |
| `90 - Meta/2026-09-25-check-cli-slice-contract.md` | `design` | Slice contract for the `check` subcommand (decision 2), per the "slice contract before coding" convention |
| `private/` (gitignored) | — | EC2 lane details moved out of the four tracked files (§10) |

Not created (reviewers found them redundant): a "Start Here" page (a
"For reviewers" block goes in `index.md`, the Quartz landing page); a new
overlay (a dated callout in the 2026-06-26 overlay points at D-26); a separate
Embedding Styles note.

Edits:

- `conventions.md`: add every type already in use (`decision-record`,
  `research`, `research-note`, `decision-queue`, `decision`, `handoff`) plus
  `python-mapping-index`, `python-mapping`, `reference`. The `research` row
  marks `sources`, `evidence_kind`, `verified` as required from D-26 onward.
  New "External citations" paragraph: `<repo>@<7-char sha>:<path>:<L1-L2>`
  resolvable through `reference-clones.md`; `URL (accessed YYYY-MM-DD)` for
  docs and papers; `/Users/…` paths are forbidden in new notes; `spatial-rs`
  citations use the same form and the overview states the repo is not public.
- `20 - Research Notes/20 - Open Questions.md`: file
  `Q-NNN — Host-language architecture asserted, not researched` (sources: the
  overlay non-goal line; the design-review sentence) before D-26 exists.
- `40 - Decision Queue.md`: D-26 entry with `[Q-NNN]`.
- `00 - Index.md`, `index.md`, `2026-07-07-session-resume-guide.md`,
  `progress-log.md`: pointers and a log entry.
- `.gitignore`: add `private/`.

External material:

- `/Users/david/Documents/David_code/reference/` (outside vault and repos),
  shallow clones at pinned commits: **calyx** (+ calyx-py), **dahlia**,
  **allo**, **exo**, **pymtl3**, **amaranth**, **polars** (I2 exemplar only).
  By docs/paper URL, not cloned: HeteroCL, JAX (`TracerBoolConversionError`),
  Taichi (Python-scope/Taichi-scope), Triton, TVMScript (round-trippable
  printer), MLIR `Location`, Chisel `SourceInfo` (cited from the local
  `spatial` clone), Ruff (`bindings = "bin"`), IPython cell magics. Dropped:
  Halide, Mojo, pydantic-core.
- **Lab repositories** (`lab-{1,2,3}-accelerator-bandits*`): GitHub Classroom
  repos with three other students' names and course handouts. Hard rule
  (decision 4): no path, hash, author, filename, or quoted line appears in any
  vault file. Leak grep in every wave check (§9).

## 4. Pre-registration, then the research angles

### Pre-registration (`D-26.md` at `status: pre-registered`, committed before Wave 1)

1. **Hypotheses from the professor's stated claim** ("Python is easy to teach
   and easy for students to pick up" — his full position as of the prior
   discussion), each with its measure. The claim is about the student surface,
   so it discriminates only the X/E axis; the R/P axis is decided by the
   remaining angles, and D-26 says so explicitly.
   - H1 "easy to pick up": hardware concepts exposed per lab vs. non-hardware
     host constructs a student must learn (angle 2, the same tally applied to
     Scala, the external DSL, and the Python hybrid); install-to-first-`check`
     (angle 11).
   - H2 "easy to teach": error-path comparison on the fixed mistake list —
     which surface catches a mistake earlier and which explains it better
     (angle 3); precedent teaching reports (angle 1); reader study if run.
   - H3 (steelman, not his words) "Python is already the course's tooling
     language and TAs can fix a Python compiler": scenario cost (angle 8) and
     what catches a TA's mistake (angle 7). Written to win in angle 13.
2. **Audience**: students by his own framing; maintainers evaluated separately
   and labelled as such.
3. **Decision rule**: angle weights from David and the Rust-leaning
   instructor, recorded before Wave 1; D-26 reports the winner under each
   weighting, under equal weights, and under a "surface-only" weighting that
   mirrors the professor's stated concern.
4. **Reversal conditions per cell** (finalized in the pre-registration):
   R-* cells lose if every discriminating construct is `expressible: yes` with
   `info_preserved` intact under some Python style, Python error paths reach
   parity on the mistake list, and a Python interpreter runs Tier-0 within k×
   of the Rust one. P-* cells lose if any pre-registered obligation cannot be
   enforced before lowering, or the simulator is slower than the pre-agreed
   bound for a lab-session loop.
5. **Fixed lists**: the Tier-0 programs for angle 2 (from the spec's canonical
   fragments and `testdata/ee109/*.scala`, not the pre-canonical `accel!`
   corpus); the top-5/top-8 mistakes for angle 3 (confirmed privately against
   course material; not cited).
6. **Guarantees any B/E cell must meet to be recommended**: one IR, one
   diagnostic catalog, "same mistake, same message" in both surfaces as a
   golden test, every lab maintained in both surfaces, wheels with no Rust
   toolchain, CI releases, a message catalog a TA can edit without rebuilding
   the core.
7. **Stopping rule**: the meeting cut ends when angles 1a/1c/2/3/5/8/10/13 are
   audited; the full plan ends when every angle is audited or its owner records
   "not decisive" with a reason.

### Sub-note schema (`type: research`)

```yaml
---
type: "research"
decision: "D-26"
angle: "<id>"
discriminates: core-language | surface-embedding | integration-depth | both | neither
sources:
  - "<repo>@<sha>:<path>:<L1-L2>"
  - "<URL> (accessed YYYY-MM-DD)"
verified: []
status: draft
---
## Scope
## Findings              # each claim tagged [measured] [precedent-measured] [designed] [judgment]
## Implications          # one subsection per cell: R-X R-E R-B P-X P-E P-B
## Evidence against      # mandatory: the strongest counter-evidence for the note's own leaning
## Open questions
## Confidence            # high / medium / low, with the reason
```

Prompts are framing-blind: cells named only by label, no plan or preferred
outcome, no "status quo"; the vault's Phase 1 rules apply (write only to your
one output path; do not delegate; do not cite what you did not open; 5
spot-checks, re-dispatch on ≥2 failures).

### Angles

| Id | Angle | Question | Primary sources | Kind |
|---|---|---|---|---|
| 1a | Precedent: Python frontend over a compiled core | allo, exo, calyx-py, PyMTL3: where the boundary sits, how errors reach the user, teaching use, maintenance | clones + papers | precedent-measured |
| 1b | Precedent: all-Python | pymtl3, amaranth (+ HeteroCL by URL): same questions; simulator speed reports | clones + papers | precedent-measured |
| 1c | Precedent: external DSL over a compiled core | dahlia (affine types *are* the legality checker, emits Calyx), Calyx-as-target, Ruff CLI-as-wheel, `%%magic` hosting | clones + docs | precedent-measured |
| 2 | Student-surface comparison | Each fixed Tier-0 program in Scala / external DSL / Python hybrid: a **concept-introduction table** (concept, lab day introduced, hardware meaning yes/no) applied identically to all three surfaces — no line counts as a measure | spec canonical fragments, `testdata/ee109/*.scala`, precedent syntax | designed + measured |
| 3 | Error-path study | Fixed mistake list → the exact message per surface. External DSL: **real `check` output** (decision 2) against the canonical catalog only; Scala: sbt on mutated copies of the `testdata` originals; Python: the same mistake written in allo/exo/calyx-py/pymtl3 and the real message recorded. Per mistake: which surface catches it *earlier* and which *explains it better*; false rejections on the labs plus five variants; which layer reports under R-B (Python-time vs Rust check) | canonical diagnostic contract in `language-spec.md`, precedent tools | measured / precedent-measured |
| 4 | Calculus inputs and the metaprogramming stance | The Rust design already replaced Argon staging with parse-then-analyze (closed grammar, ADR 0001 const-eval, Rules 1–11, lexical order). So: (a) which calculus inputs each Python style loses — spans, literal types and check-mode propagation, `Size`-vs-`Int` (E0506), scopes and ancestor-shadowing, declaration-ID order, `deq()` evaluation-time consumption; (b) an explicit sub-decision: forbid host metaprogramming (Exo), const-only (ADR 0001), or allow with a round-trip requirement (TVMScript) | `language-spec.md` obligation calculus, ADR 0001, Taichi/Amaranth/TVMScript docs | designed |
| 5 | Boundary design | Python↔Rust at the **unchecked surface AST** (`spatial.ast.v1`, JSON of the closed EBNF, every node carrying `SourceSpan`) or `.spatial` text plus a source map — *not* the checked controller-tree IR, which would either bypass `E03xx/E05xx` or force a second checker (Calyx's profile; Dahlia is a full type checker). `SourceFile` must admit non-`.spatial` origins so span-sorted diagnostic ordering survives. ADR 0002 envelopes for I1/I2. Output: a Phase 1 requirement (§7) | ADR 0002, `frontend/source.rs`, roadmap Phase 1, calyx-py, MLIR `Location` | designed |
| 6 | Tooling | Notebooks (incl. `%%spatial`), completion, type hints, LSP/tree-sitter effort for the external DSL, debugging | precedent editor support | precedent-measured |
| 7 | What catches a maintainer's mistake | For the compiler's own code under R vs P: static checks available, what replaces them, test-authoring language for TAs; the one-author bus factor sits on the risk line next to dynamism | `spatial-rs` history, precedent contributor patterns | judgment + measured |
| 8 | Forward-looking cost | Same milestone (Phase-1 parity on the 39 programs) under the same architecture for every cell; shared assets (corpus, goldens, Vitis evidence, JSON/Tcl) credited to all; proxies (`validate.rs` size for the calculus; Exo `pyparser` and Allo builder sizes for a Python frontend; the second corpus); **three scenarios**: "a message is wrong in week 3", "add a construct for a new lab", "Vitis version bump" — who, in what language, shipped how. Kept-lines is a footnote, not a criterion | measured LOC (81.8K; ~32K slated for replacement), clones | measured + designed |
| 9 | Risks and failure modes | Two-frontend drift; diagnostic regression; abi3 wheels vs per-version; PyO3 lagging CPython releases (pin the course Python); wheels-only, no sdist (an sdist silently demands Rust); `interp` needs no C++ compiler, `host-cpp` does; Python-environment burden on lab machines as the mirror of the Rust-toolchain burden; sandboxing — embedded Python runs student code at trace time, an external DSL is inert data | maturin/PyO3 docs, precedent issue trackers | precedent-measured |
| 10 | Recommendation | Two sub-matrices (core language; surface embedding) + a combination table with integration depth; recommendation; rejected alternatives; answers to angle 13; the pre-registered reversal conditions re-evaluated | angles 1–9, 11–13 | judgment |
| 11 | Course operations | Install-to-first-`check` on macOS arm64 / WSL / the AWS F2 image with Vitis 2025.1; autograder path (JSON diagnostics); readability of generated Lab1Part2 C++ vs the staff `vadd.cpp` (students answer pragma questions on it); TA onboarding between offerings; what breaks when staff changes; GitHub Classroom skeletons | ADR 0002, course structure as David describes it (not the lab repos) | designed; measured after decision 2 |
| 12 | Simulator performance | Precedent numbers (PyMTL3, Amaranth `pysim`); toy-vs-toy spike in the scratchpad (~200 lines each) on one lab, since the Rust interpreter is Phase 1 work | papers, spike | measured-toy |
| 13 | Case for each losing cell | Written *to win* by a framing-blind agent for every cell the draft recommendation rejects — starting with P-E ("Python is already the course's tooling language: every lab part ships `design_top/synth.py`; NumPy golden model beside the kernel; `pip install`; TAs patch in Python; Allo/HeteroCL/PyMTL3 are course-proven; AST style removes the overloading objection") — and D-26 answers point by point | all notes | judgment |
| (14) | Reader study | Three TAs, three students, 30 minutes: read lab 2 in each surface, predict behaviour, count misreadings; time to first successful `check`. Needs the professor's cooperation: after the meeting | — | measured |

Angles 8, 10 and the D-26 synthesis are written by the main session; the
citation audit and angle 13 by fresh agents with no session context.

## 5. The Python surface mapping (`35 - Python Surface Mapping/`)

Derived from the closed EBNF in `language-spec.md`, not from a hand list
(`mux` is not in the grammar; `if` expressions are; `reset`/`shift`/`enq`/
`deq`/`.value`/`requires`/`tail`/`ii`/view slices are).

**Meeting cut — 8 construct entries** (the discriminators): `foreach`/`reduce`
bodies with `yield`; `if` expressions; `:=`; `fsm`; `FixPt` + compile-time
`Size`; `load`/`store` arrows and views; `par` + `pipe`/`seq`; kernel + ports
+ `requires`.

**5 cross-cutting entries** (things per-construct entries cannot see): naming
and scoping (ancestor shadowing forbidden, sibling reuse allowed; tracing
cannot observe rebinding; AST style meets function scoping and leaking `for`
variables; Amaranth's frame-inspection naming); the `Size`→`Int` checked
embedding (E0506; Taichi's scope confusion as the teaching hazard);
bidirectional literal typing (Python evaluates bottom-up, so check-mode
propagation is unavailable under tracing); `deq()` consuming at evaluation with
statement-end commit; declaration-ID order (Rule 4's substitution depends on
it).

Remaining constructs are rows in the overview's coverage table marked
"deferred until D-26 selects an E or B cell"; the folder becomes the build spec
only on that branch.

Entry schema (`type: python-mapping`):

```yaml
---
type: "python-mapping"
construct: "<name>"
spec_entry: "[[<10 - Spec entry>]]"
grammar_rule: "<EBNF nonterminal in docs/language-spec.md>"
external_dsl:            # the same rubric applied to the external DSL
  concepts_without_hardware_meaning: ["let", "yield", "using"]
per_style:               # tracing | builder | ast | hybrid-<name>
  tracing:
    expressible: yes | awkward | no
    info_preserved: [spans, literal_types, size_vs_int, scope, order]   # subset kept
    error_locus: python-time | ir-check | runtime | silent
    silently_divergent: [ "<hazard>" ]
  builder: { … }
  ast: { … }
obligations_at_risk:
  - "<obligation> — under <cell>: <who enforces, when>"
raters: []               # two independent ratings recorded; agreement reported in the overview
verified: []
status: draft
---
## External DSL form        # verbatim from language-spec.md
## Python forms             # one per style, or "not expressible" with the data-model citation
## Assessment               # option-qualified: what is lost under R-B vs P-E, and who reports the error
## Precedent                # which precedent does the equivalent, cited repo@sha
```

`expressible`, `info_preserved`, `error_locus` replace a single fitness label:
expressibility, information loss, and enforcement locus are separate facts and
were being conflated. `awkward` is operational: the form requires a construct
outside the pre-listed allowed-Python subset for that style. Two independent
raters (main session + a framing-blind agent) rate every entry; agreement and
adjudication are recorded in the overview.

## 6. Synthesis, verification, decision, publication

1. Main session writes `D-26.md` (findings by angle, sub-matrices, combination
   table, recommendation, rejected alternatives, answers to angle 13, the
   pre-registered reversal conditions re-evaluated, and a **spillover list**:
   findings about the DSL's own design — e.g. three keywords for a sum,
   `Size` vs `Int` on day one, `requires` for runtime bounds — that are
   host-language-neutral and go to the syntax teachability review, not D-26).
2. **Citation audit** (fresh Codex agent; the April method): every
   `repo@sha:path:L1-L2` resolves in the manifest, exists in the clone,
   `L2 ≤ wc -l`; every URL fetched; leak grep empty.
3. **Inference audit** (angle 13, Codex): the best case for each losing cell,
   answered in D-26.
4. `D-26.md` → `status: awaiting-user-confirmation`. David decides.
5. Only then: the 2026-06-26 overlay callout, index/resume-guide/progress-log
   updates, and the "For reviewers" block in `index.md`.
6. Publication is a separate gated task (§10).

## 7. Outputs that feed spatial-rs Phase 1 (recommendations, not actions)

- The Python↔Rust boundary at the unchecked surface AST with `SourceSpan` on
  every node and a `SourceFile` registry that admits non-`.spatial` origins
  (MLIR `Location` model) — a Phase 1 IR-definition bullet now, an every-node
  retrofit after Phase 3.
- The metaprogramming stance (angle 4b) as an explicit decision.
- The "same mistake, same message" golden test as a Phase 5 acceptance
  criterion if a B cell is chosen.
- The `check` renderer contract (file:line, primary/secondary labels, help)
  from decision 2 as the ADR 0002 text format.

## 8. How D-26 feeds the presentation

- **One meeting**: the deck opens with the honest prototype status (§1), then
  answers "easy to teach, easy to pick up" directly with the meeting-cut
  evidence — labs side by side as a concept table (angle 2), the top mistakes
  as real terminal output in each surface (angle 3), install-to-first-`check`
  (angle 11), and what course-proven Python DSLs actually do (angle 1). It
  then separates the core language as an engineering choice he has not
  expressed a view on, cites the pre-registration, and shows the R-E/R-B
  guarantees as commitments if a Python surface is recommended. If a P cell
  wins on the evidence, the deck says so.
- **Fallback**: if he engages more deeply than expected, the pre-registration
  is already written and can be put in front of him as-is.
- No dates anywhere.

## 9. Execution shape

**Wave 0 (main session + David):** Q-NNN filed; conventions edit;
`.gitignore` + `private/`; clones + `reference-clones.md`; mapping skeleton
(13 entries, frontmatter only) and `D-26.md` pre-registration **committed
before dispatch** so `git status` is the audit; extend
`90 - Meta/scripts/validate_coverage_note.py` to the `research` and
`python-mapping` schemas; the `check` subcommand (own slice contract + plan,
red-first TDD, full local gates).

**Meeting cut (≈9 runs):** Wave 1 — 1a, 1c; Wave 2 — 2, 3, 5, mapping-A
(controllers/expressions + naming/order), mapping-B (types/ports/IO +
Size/Int, literal typing, deq); Wave 3 — citation audit, angle 13 for P-E;
main: 8, 10, `D-26.md` draft.

**Full plan (≈17 runs, after the meeting):** adds 1b, 4, 6, 7, 9, 11, 12,
second rater, angle 13 for the remaining losing cells, and the reader study.

Agents: Claude general-purpose for writing (they must write; `Explore` has no
Write) — recorded as a deviation from `workflow.md`; Codex for audits. Prompts
carry the schema in full, the citation rule, the pinned SHAs, the output path,
"replace the body only; frontmatter keys fixed except the rating fields", and
the framing-blind rule.

**Post-wave checklist** (from `/Users/david/Documents/Spatial Research`):

- Only expected paths changed:
  `git status --porcelain | grep -vE '(D-26|35 - Python Surface Mapping)'` → empty.
- Schema + YAML: run the extended validator over every new note; assert every
  item of `sources`/`obligations_at_risk`/`related-questions` is a string and
  `spec_entry` starts with `[[` (the unquoted-wikilink hazard).
- Stems unique: `find . -name '*.md' -not -path './.git/*' -exec basename {} .md \; | sort | uniq -d`
  → no entries beyond the 23 legacy ones.
- Leak grep (must be empty):
  `grep -rnE 'accelerator-bandits|EE109-Spr-2026|/Users/david/|\.pem|ec2-|us-west-2' "35 - Python Surface Mapping" "20 - Research Notes/50 - Decision Records/D-26"*`
- Citation density: ≥ 8 `repo@sha:` or URL citations per note; `(inferred,
  unverified)` count reported; angle-1 claims without a citation fail the
  spot-check.
- Bounds script over every `repo@sha:path:L1-L2`.
- Wikilinks: every new `[[stem]]` resolves; baseline 45 broken, new notes add
  zero.
- Workflow rule: 5 claims per note, `verified: [2026-09-25]` on pass, ≥2
  failures → re-dispatch quoting the failed claims.

## 10. Publication gate (separate task; blocks any push)

Verified 2026-09-25: `davidydu/spatial-research` is **public**; the local vault
is `main…origin/main [ahead 349]`; `origin/main` is at 2026-05-14; the site's
daily cron runs successfully (it only looks stale because the source never
moved); the unpushed diff has 145 lines matching `\.pem|ec2-[0-9]|ssh ee109|
us-west-2`; four tracked files carry EC2 host/user/key-path details
(`30 - HLS Mapping/84 - EE109 HLS Stability Matrix.md`,
`90 - Meta/2026-07-07-rust-gemm-dynamic-dimension-slice-contract.md`,
`90 - Meta/2026-07-07-session-resume-guide.md`, `90 - Meta/progress-log.md`);
the vault `.gitignore` does not exclude `private/` (Quartz `ignorePatterns`
and the site's `.gitignore` already do).

Decided (decision 3): scrub + rewrite history, repo stays public. The
step-by-step runbook is `private/plans/2026-09-25-vault-publication-gate.md`
— it contains the real values, so it is never tracked.

1. Back up the vault (`git clone --mirror` to a local path) before anything.
2. Move the EC2 lane block to `private/ec2-lane.md`; add `private/` to
   `.gitignore`; point the resume guide at the private file; commit.
3. Rewrite the never-pushed history with `git filter-repo --replace-text`
   **and `--replace-message`** (commit messages carry the strings too) over
   the identifying literals only: the two hostnames in every form, the two
   IPs, the two key filenames, the SSH alias, and the `user@host` form. Bare
   region names and file extensions are not scrubbed; they identify nothing
   and appear as regex text in tracked scripts.
4. Blob-level and message-level scans over `origin/main..HEAD` for the
   identifying literals → 0; `origin/main` still an ancestor; upstream
   tracking restored; `ls -la spatial-research-site/content` → symlink to the
   vault; `npx quartz build` locally.
5. Push (force is not needed: `origin/main` is an ancestor). The cron
   publishes within 24 h (or `workflow_dispatch`). The log entry for this
   task describes the checks generically and never quotes the patterns.

## 11. Open questions

1. Whether the Rust-leaning instructor is willing to record weights before
   Wave 1 (if not, David alone, with sensitivity reported).
2. Whether the reader study (angle 14) is feasible this term.
