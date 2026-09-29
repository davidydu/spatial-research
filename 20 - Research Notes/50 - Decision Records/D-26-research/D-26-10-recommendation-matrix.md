---
type: "research"
decision: "D-26"
angle: "10"
discriminates: both
sources:
  - "spatial-rs@eb49d8b:crates/spatial-rs-core/src/compiler.rs:30-67"
  - "spatial-rs@eb49d8b:docs/superpowers/plans/2026-07-07-compositional-core-inversion-roadmap.md:101-153"
  - "spatial-rs@eb49d8b:docs/language-spec.md:385-420"
  - "spatial-rs@eb49d8b:docs/language-spec.md:634-718"
  - "spatial-rs@eb49d8b:docs/language-spec.md:831-837"
  - "spatial-rs@eb49d8b:docs/language-spec.md:987-1028"
  - "spatial-rs@eb49d8b:docs/language-spec.md:1069-1115"
  - "spatial-rs@eb49d8b:docs/adr/0002-file-cli-host-runtime.md:504-557"
  - "spatial-rs@eb49d8b:crates/spatial-rs-cli/src/lib.rs:12-77"
  - "exo@defe172:src/exo/frontend/pyparser.py:38-91"
  - "exo@defe172:src/exo/frontend/boundscheck.py:818-840"
  - "calyx@d6bcdc8:calyx-py/calyx/py_ast.py:56-150"
  - "allo@094ab41:allo/ir/builder.py:93-114"
verified: ["2026-09-28"]
status: draft
---

## Scope

Synthesize the meeting cut without treating student syntax, compiler implementation language and Python tooling as one choice. This is a provisional engineering recommendation for the next milestone, not a completed course adoption decision. Evidence comes from the other D-26 notes and mappings. No personal weights, quantitative utility scale, simulator comparison, install study or novice repair study was supplied or measured.

## Findings

### Compiler-core sub-matrix

[judgment] Hold the target controller-tree/checker/interpreter architecture fixed. The present parse/const/HIR/classifier route supplies working assets but is not the completed general compiler; moving to Python need not throw away its specification, oracles or backend evidence. See [[D-26-08-cost]] and `spatial-rs@eb49d8b:crates/spatial-rs-core/src/compiler.rs:30-67`, `spatial-rs@eb49d8b:docs/superpowers/plans/2026-07-07-compositional-core-inversion-roadmap.md:101-153`.

| Core | Strength | Problem | Disposition |
|---|---|---|---|
| Rust | Existing implementation, diagnostics and evidence can be adapted; current CLI is directly usable | General semantics still incomplete; actual TA maintenance advantage and simulator speed unmeasured | Provisional continuity choice for the next implementation milestone, not a demonstrated educational or speed winner |
| Python | AST compiler precedents establish feasibility; one staff language may lower maintenance friction | General semantics still require implementation; staff advantage and k-bound unmeasured | Serious alternative; no language-impossibility argument excludes it |

[precedent-measured] Exo's Python source recovery and checking and Allo's Python AST-to-MLIR construction refute the shortcut “Python is only a wrapper, therefore cannot own the compiler.” They do not benchmark Spatial's exact interpreter or obligation calculus. See [[D-26-01a-precedent-python-over-core]], `exo@defe172:src/exo/frontend/pyparser.py:38-91`, `exo@defe172:src/exo/frontend/boundscheck.py:818-840`, `allo@094ab41:allo/ir/builder.py:93-114`.

### Student-surface sub-matrix

| Surface/style | Strength | Problem | Disposition |
|---|---|---|---|
| External DSL | Explicit hardware constructs and source ownership; no host execution before capture | Additional language-only concepts; all three canonical labs currently hit parser barriers | Keep as the reference input during generalization; do not claim proven teaching superiority |
| Python tracing | Compact arithmetic and explicit method operations | Native binding/control cannot preserve the full contract; host folding, truth testing and evaluation order can diverge | Do not choose unrestricted tracing as the sole faithful surface |
| Python builder | All 13 mapped constructs have designed expressible forms; explicit regions can retain DSL scope | Extra API concepts; source spans and literal provenance require deliberate work | Viable controlled construction interface, not automatically the easiest teaching surface |
| Python AST | All 13 first ratings have a designed form retaining all five information categories | Requires a real frontend, token retention and DSL rules that sometimes differ from Python | Best candidate for a faithful Python student-surface experiment |
| Both surfaces | Lets a course compare and support both ways into one checker | Paired labs, releases and diagnostic parity are recurring obligations | Defer adoption until teaching benefit justifies maintaining both |

[judgment] The mapping inventory establishes design plausibility, not completed parity. Scope, fixed-point literals and consuming FIFO order need explicit treatment (`spatial-rs@eb49d8b:docs/language-spec.md:385-420`, `spatial-rs@eb49d8b:docs/language-spec.md:634-718`, `spatial-rs@eb49d8b:docs/language-spec.md:831-837`). [[D-26-02-student-surface-comparison]] applies the same concept rubric to each surface; concept counts are not measured learning times. [[D-26-03-error-paths]] finds both helpful Exo checks and current external gaps, without a fair complete eight-error comparison.

### Combinations and integration depth

[designed] The table describes proposed deployment paths. Only I0 `check` with text diagnostics is currently implemented in the new CLI; ADR JSON commands, wheel shipping, bindings and notebook integration are not delivered by this research (`spatial-rs@eb49d8b:crates/spatial-rs-cli/src/lib.rs:12-77`; `spatial-rs@eb49d8b:docs/adr/0002-file-cli-host-runtime.md:504-557`). I1, I1′ and In do not require an embedded Python frontend.

| Cell | Integration path | Disposition |
|---|---|---|
| R-X | I0 now; implement I1 host contract; consider I1′ wheel/In notebook after course-platform validation | Provisional next-milestone baseline |
| R-E | I1 or I2 plus Python AST ingress; I1′/In optional | Candidate if student-surface evidence favors Python and all E guarantees can be met |
| R-B | Same mechanisms with both frontends converging before semantic checking | Conditional future option; not the default merely for optionality |
| P-X | Python package and the same external-file/host-data contract | Consider if staff needs favor Python while surface evidence favors external syntax |
| P-E | Python package with closed AST frontend and internal shared checker | Strongest alternative under the stipulated Python-maintainer course scenario |
| P-B | Python package, both frontends and parity corpus | Requires a demonstrated need for both surfaces |

[judgment] For R-E/R-B, prefer an unchecked surface AST with precise origins over already-checked IR if shared semantic diagnostics are the goal. Python still owns its syntax/subset errors. A line-only text map loses expression precision; merely carrying metadata does not prove that downstream errors render it. See [[D-26-05-boundary-design]], `calyx@d6bcdc8:calyx-py/calyx/py_ast.py:56-150` and `spatial-rs@eb49d8b:docs/language-spec.md:987-1028`.

### Decision-rule sensitivity

[judgment] David's and the instructor's weight columns remain blank, so their personalized rankings are omitted exactly as pre-registered. Equal weighting has no defensible numerical winner: the angles supply heterogeneous qualitative evidence and important missing measures, not calibrated utilities. A numeric total would invent scores. The provisional R-X disposition is continuity under uncertainty, not a result attributed to equal weights.

[judgment] Surface-only H1+H2 likewise identifies no measured winner. The comparative listings and error transcripts expose tradeoffs, but no learner study measures pickup, explanation quality or repair success, and Python error cases do not implement every identical Spatial rule. Evidence against the current external frontend is substantial; it must not be hidden by the preference to retain existing core work. See [[D-26-02-student-surface-comparison]] and [[D-26-03-error-paths]].

### Pre-registered reversals, evaluated separately

| Registered condition | Evidence and result |
|---|---|
| Every mapping has one yes/all-five style | Met at the level of 13 first-rating designs under token-backed AST; not an implemented or independently double-rated frontend |
| Python error parity on the whole fixed list | Not established. Examples are analogues; Scala is source-only, Allo runtime unavailable, and row5 is legal under the external spec (Q166) |
| Python simulator within k× Rust, k=10 | Unknown: no matched general interpreter benchmark. No bound may be inferred from frontend acceptance or repository language |
| Conjunction makes R-* lose | Not triggered by this meeting cut; this is not proof that Rust wins |
| An obligation cannot be enforced before lowering under every Python style | No such impossibility established; explicit AST designs preserve each mapped category in principle |
| Simulator exceeds k=10, making P-* lose | Unknown; not triggered |
| E/B recommendation guarantees | Not implemented: one shared IR/catalog, paired same-mistake/message goldens and labs, no-toolchain wheels, CI releases, TA-editable catalog remain required commitments |

[judgment] The row5 conflict is recorded without changing the frozen experiment: direct writable DRAM assignment is legal. A future re-registered list needs an invalid replacement or an explicit valid control. The current catalog's incomplete implementation is independently documented (`spatial-rs@eb49d8b:docs/language-spec.md:1069-1115`). Missing parity evidence cannot honestly be converted into either a passed reversal or an architectural disqualification.

## Implications

### R-X

Retain provisionally for the next general-compiler milestone. Finish canonical syntax and obligation checks before claiming student diagnostic benefits. Python host tooling can be added independently.

### R-E

A plausible route to a Python student surface without moving the semantic core. Select only after a bounded frontend comparison and explicit delivery of all E guarantees.

### R-B

Do not commit to two public surfaces until the course will use both and maintain their parity. A shared checked IR alone is too late to share all early diagnostics.

### P-X

A coherent combination, rather than a contradiction: core maintainability and syntax preference are independent. Current evidence does not establish that its migration cost is worthwhile.

### P-E

Retain as the leading challenger under Python-staff assumptions. It is semantically plausible and may be operationally preferable; the full case must be answered on staffing, parity and measured performance.

### P-B

Viable if Python ownership and dual-surface demand are both established. It combines rather than removes their implementation obligations.

## Evidence against

The provisional Rust choice can overvalue current author familiarity. The general architecture still needs major work, Exo demonstrates real early checking, and a source-backed AST has no identified preservation impossibility across the 13 mappings. If the enduring teaching team works effectively in Python, P-E can be preferable before a Rust core accumulates further migration cost. Conversely, the current Rust parser gaps do not prove that Python syntax teaches better. These are the reasons to keep the recommendation conditional and to answer the fresh P-E case in [[D-26]].

## Open questions

Confirm the future maintaining team and student baseline; settle Q166 for a revised study; implement comparable semantic/error probes; benchmark matched Tier-0 interpreters at k=10; test packaging on course platforms; obtain a second mapping rating and novice repair evidence. None is represented as completed by the meeting cut.

## Confidence

Medium in separating the axes and identifying necessary guarantees; low in a final core or teaching-surface winner. The next-milestone recommendation is an explicit judgment under incomplete evidence.
