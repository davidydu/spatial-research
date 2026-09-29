---
type: "research"
decision: "D-26"
angle: "13"
discriminates: both
sources:
  - "exo@defe172:src/exo/API.py:35-49"
  - "exo@defe172:src/exo/API.py:168-173"
  - "exo@defe172:src/exo/frontend/pyparser.py:37-90"
  - "exo@defe172:src/exo/frontend/typecheck.py:144-154"
  - "exo@defe172:src/exo/backend/LoopIR_compiler.py:323-348"
  - "exo@defe172:src/exo/frontend/boundscheck.py:818-840"
  - "pymtl3@c8b349f:pymtl3/passes/rtlir/behavioral/BehavioralRTLIRGenL1Pass.py:47-80"
  - "pymtl3@c8b349f:pymtl3/passes/rtlir/errors.py:26-62"
  - "amaranth@90449f1:amaranth/hdl/_ast.py:627-639"
  - "calyx@d6bcdc8:calyx-py/calyx/py_ast.py:63-101"
  - "spatial-rs@eb49d8b:crates/spatial-rs-core/src/compiler.rs:30-67"
  - "spatial-rs@eb49d8b:crates/spatial-rs-core/src/validate.rs:34-64"
  - "spatial-rs@eb49d8b:docs/language-spec.md:481-505"
  - "spatial-rs@eb49d8b:docs/language-spec.md:682-710"
  - "spatial-rs@eb49d8b:docs/language-spec.md:831-837"
  - "spatial-rs@eb49d8b:docs/language-spec.md:987-1028"
  - "spatial-rs@eb49d8b:docs/language-spec.md:1074-1115"
  - "https://docs.python.org/3/library/ast.html#ast.AST (accessed 2026-09-28)"
  - "https://docs.python.org/3/reference/expressions.html#evaluation-order (accessed 2026-09-28)"
  - "https://pymtl3.readthedocs.io/en/latest/ref/passes-translation-intro.html (accessed 2026-09-28)"
verified: ["2026-09-28"]
status: draft
---

> [!note] Scenario assumption updated
> This steelman preserves its original Python-maintainer scenario. David subsequently specified equal necessary team skills. The selected proposal and response to this case are in [[D-26-final-architecture]]; this note is historical argument, not the current recommendation.
## Scope

Choose **P-E: a Python compiler core with one restricted Python AST surface** for the stipulated undergraduate FPGA course. Staff already use Python for vendor orchestration, students know Python, and TAs patch the compiler between offerings. These are scenario assumptions, not measured staffing or learning facts. The positive case is sustained course ownership: put the student language, semantic implementation, and course integration within the maintainers' existing working language.

This independent argument uses notes 1a, 1c, 2, 3, 5 and 8, all thirteen construct mappings, directly reopened pinned sources, and official pages fetched on 2026-09-28. Source inspection here is distinguished from angle 3's recorded executions. No new compiler, student, simulator, or productivity experiment was run.

## Findings

[judgment] **P-E aligns the compiler's change authority with the teaching team.** A TA correcting a legality rule or adding a lab construct must understand semantic code, not merely invoke a wrapper. Python orchestration alone cannot establish Python compiler expertise, but the stipulated maintenance pattern makes that expertise a plausible continuation of existing practice. A single implementation language lets the course invest its training in hardware semantics, regression cases, and compiler structure. This is the strongest forward-looking advantage over R-E, where student Python familiarity is already available; it is not a measured productivity ratio. See [[D-26-08-cost]].

[precedent-measured] **A Python core can be a real compiler.** Inspected Exo source parses Python into its own representation, performs type, bounds and alias checks, and emits C/header strings from Python (`exo@defe172:src/exo/API.py:35-49`; `exo@defe172:src/exo/API.py:168-173`; `exo@defe172:src/exo/backend/LoopIR_compiler.py:323-348`). Generated C is output, not evidence that Exo's compiler core is implemented in a compiled language. Its Python checker also aggregates source-labelled failures (`exo@defe172:src/exo/frontend/typecheck.py:144-154`).

[precedent-measured] Inspected PyMTL3 source independently constructs behavioral RTLIR in Python and formats syntax/type failures with source lines and carets (`pymtl3@c8b349f:pymtl3/passes/rtlir/behavioral/BehavioralRTLIRGenL1Pass.py:47-80`; `pymtl3@c8b349f:pymtl3/passes/rtlir/errors.py:26-62`). Its official documentation explicitly separates the translatable subset from arbitrary Python calls and containers ([translation contract](https://pymtl3.readthedocs.io/en/latest/ref/passes-translation-intro.html), accessed 2026-09-28). This supports the feasibility of a deliberately bounded language, not automatic Spatial diagnostic coverage or measured course success.

[designed] **Choose AST transformation within E.** The thirteen mappings rate builder forms expressible throughout, while tracing/operators need extensions for controllers and cannot observe native rebinding sufficiently for Spatial scope. Their AST forms can retain spans, literal types, Size/Int distinctions, scope and order across all thirteen entries, conditional on implementation. They require a closed resolver, original tokens, deterministic declaration IDs and ordered effects. These are representability designs, not present error parity. The case therefore does not depend on making unrestricted Python executable as hardware. See [[00 - Python Mapping Overview]], [[90 - Python Naming and Scoping]] and [[D0 - Python Declaration Order]].

[judgment] **The course should reuse familiarity, without claiming fewer concepts.** Angle 2's final constructed counts are Scala 14, external 6, tracing 13, builder 11 and AST 12, including postponed annotation evaluation. They favor the external form under that rubric. Yet a familiar function or import and an unfamiliar declaration convention each count once; there is no weighting by prior knowledge or measured repair difficulty. The stipulated Python background is therefore a reason to prefer familiar forms despite the count, not permission to rename twelve concepts as six. The three designed lab ports also leave buffering equivalence and numerical execution unverified. See [[D-26-02-student-surface-comparison]].

[precedent-measured] **Rust's current artifact does not settle the future-core decision.** Direct inspection shows parse → constant evaluation → HIR → accepted-adapter classification (`spatial-rs@eb49d8b:crates/spatial-rs-core/src/compiler.rs:30-67`). The current validator checks accepted adapter shape, kind and canonical name (`spatial-rs@eb49d8b:crates/spatial-rs-core/src/validate.rs:34-64`); it is not the planned general obligation calculus. Canonical reductions, several other frontend forms, and the calculus remain specified rather than generally implemented (`spatial-rs@eb49d8b:docs/language-spec.md:1074-1115`). Python must do substantial semantic work, but so must the retained Rust path; shared specifications, corpus and expected results deserve credit in both.

[precedent-measured] Angle 3's inspected execution record supplies stronger evidence than source representability: Exo rejected an unbounded table read with a counterexample and accepted its bounded control; the current external checker accepted the unbounded counterpart and rejected its `requires` repair. Exo's opened bounds-check implementation explains the counterexample path (`exo@defe172:src/exo/frontend/boundscheck.py:818-840`). These are analogous obligations, not identical-language parity. Exo also accepted the uninitialized examples at its frontend; Allo remained source-only because its native module was unavailable. The record refutes an inherent Python diagnostic barrier, not all objections to P-E. See [[D-26-03-error-paths]].

## Implications

### R-X

P-E wins when long-term TA ownership and reuse of student Python conventions matter more than retaining the existing implementation. R-X can legitimately offer I0 CLI, I1 Python/JSON testbenches, I1-prime CLI-in-wheel distribution and In notebook magic; students need not learn Rust. Those alternatives remove installation and hosting objections, but leave compiler changes in Rust and kernel syntax external. See [[D-26-01c-precedent-external-dsl-over-core]].

### R-E

This is the strongest rival: it gives students the same surface and retains reusable Rust analysis. I2 bindings are optional; a shallow ingress can work. P-E's advantage is direct Python ownership of semantic patches and the absence of a required cross-language program/provenance boundary. It wins only if that recurring benefit exceeds Rust reuse; bindings or JSON transport alone cannot decide the comparison. See [[D-26-05-boundary-design]].

### R-B

P-E concentrates course materials and maintenance on one public surface. Sharing a checker can prevent semantic duplication, but two frontends still need capture/parser behavior, diagnostics, examples and release coverage. In this scenario, a second student language lacks an established audience sufficient to justify those continuing obligations.

### P-X

P-X captures the Python ownership benefit and the external rubric's lower concept count. P-E additionally reuses students' familiar file structure, expressions, annotations and surrounding testbench conventions. That is a positive educational hypothesis, not a demonstrated advantage. Choose P-E because the stipulated familiarity gives it a concrete constituency; P-X should win if actual learners find the explicit external boundary substantially clearer.

### P-E

Commit to a bounded hardware language inside Python, with a Python semantic implementation that TAs can inspect alongside lab tests. Keep static legality authoritative before emission and retain the same semantic acceptance contract. The absence of a mandatory Rust boundary reduces one maintenance category; it does not remove compiler engineering. Research acceptance must cover source-labelled negative cases and valid controls, exact numeric/effect behavior, and representative simulator performance.

### P-B

P-B retains Python core ownership but adds the external frontend without demonstrated course demand. P-E better spends a limited teaching team's attention on one documented contract and its diagnostics. A common IR is compatible with P-E; it does not require promising two supported student languages.

## Evidence against

**“Python-looking syntax conceals different semantics.”** This is the strongest surface objection. Python evaluates an assignment RHS before its target, whereas Spatial evaluates target indices first; FIFO consumption makes that difference observable ([Python evaluation order](https://docs.python.org/3/reference/expressions.html#evaluation-order), accessed 2026-09-28; `spatial-rs@eb49d8b:docs/language-spec.md:831-837`). AST interpretation can preserve the contract, but the divergence must be taught. Pure operator tracing is not the answer: even Amaranth deliberately rejects symbolic truth conversion (`amaranth@90449f1:amaranth/hdl/_ast.py:627-639`). If students repeatedly transfer incorrect Python intuitions despite instruction, P-X defeats this case.

**“Embedding cannot retain precise errors.”** It can retain their raw material: Python exposes node positions, and Exo reconstructs original file offsets ([AST documentation](https://docs.python.org/3/library/ast.html#ast.AST), accessed 2026-09-28; `exo@defe172:src/exo/frontend/pyparser.py:37-90`). That falls short of complete provenance. Calyx's inspected builder uses stack-derived filename/line information, illustrating a different, coarser mechanism (`calyx@d6bcdc8:calyx-py/calyx/py_ast.py:63-101`). P-E must preserve literal tokens, declaration/use links, secondary spans, poison suppression and deterministic ordering; a decorator does not supply these (`spatial-rs@eb49d8b:docs/language-spec.md:987-1028`).

**“Rust is faster and already paid for.”** There is no measured Rust/Python simulator ratio here. Keep **k=10 as an unmeasured decision threshold**, never a benchmark result. Compare equivalent semantics, workloads and absolute feedback times. Existing Rust assets lower migration cost, but the incomplete canonical frontend and general interpreter/checker work prevent treating retention as free. If representative Python simulation misses the agreed gate, or measured delivery effort strongly favors Rust, R-E wins.

**“Python weakens compiler correctness.”** Familiarity is insufficient: Python's unbounded integers and host floats cannot substitute for Spatial literal typing, wrapping or proof rules (`spatial-rs@eb49d8b:docs/language-spec.md:682-710`). The closed obligation calculus must remain exact, including its restriction against a stronger solver changing acceptance (`spatial-rs@eb49d8b:docs/language-spec.md:481-505`). P-E's answer is explicit semantic implementation and conformance evidence, not trust in host behavior. If the actual TAs cannot maintain that implementation reliably, the ownership premise fails.

## Open questions

- Do actual maintainers support the stipulated Python ownership premise when repairing a semantic bug, rather than only editing orchestration scripts?
- Do students write and repair the three lab patterns more successfully with the restricted Python contract? No student trial exists.
- Can provenance survive generated helpers, notebook cells and multiple expressions on one line without losing secondary labels?
- What do equivalent simulator runs and a timed maintenance exercise show? Current precedent runs are diagnostic evidence, not performance or productivity measurements.

## Confidence

Medium that P-E is the strongest choice **under this scenario**: it aligns future semantic ownership and student familiarity while preserving a credible compiler architecture. Low confidence in comparative delivery time, learner benefit and simulator cost until measured. This is a positive selection case with explicit falsifiers, not a claim of an existing conforming Python implementation.
