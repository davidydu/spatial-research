---
type: design
title: "Course syntax and architecture review"
project: spatial-python
date: 2026-10-01
status: reviewed
adoption_status: proposed
implementation_status: not-implemented
related:
  - "[[PY-E002 - Spatial to Python Syntax Atlas]]"
  - "[[60 - Course Syntax and Compiler Trace]]"
  - "[[07 - Python Implementation Readiness Audit]]"
---

# Course syntax and architecture review

This review answers David's follow-up: use the linked course examples to show what common Spatial syntax becomes in Python, then derive the compiler design. Earlier full-family and implementation-readiness audits remain dated checkpoints; they did not already establish these concrete course mappings.

## Requirement audit

| Requirement | Evidence and result |
|---|---|
| Inspect the supplied website and its actual examples | Read the public course pages and pinned repository b4896ab; all six lab pages have explicit dispositions in R012–R014. Homepage-linked reference files are separately inventoried |
| Show Spatial spelling next to Python spelling | [[PY-E002 - Spatial to Python Syntax Atlas]] supplies the direct table; R012 has 46 stable L1 IDs, R013 16 L2 IDs, R014 29 L3 IDs |
| Go beyond one tiled-scale sketch | Complete proposed scalar, SRAM, FIFO, Reduce/Fold, MemReduce/MemFold, original/alternative FSM, LUT, GEMM and convolution kernels; explicit host workflow |
| Preserve the course's incomplete examples as incomplete source evidence | Designed exercise completions are labeled; current Lab3 guide and older completed CS217 fixture stay separate |
| Explain the compiler required by that syntax | [[60 - Course Syntax and Compiler Trace]] covers exact source registrations, typed domains, aliases, init, effects, mapper lifetimes, windows and plan records; it traces tile, GEMM and convolution |
| Keep the full-language architecture | Existing 106-document/18-family ledger and five blueprints remain; new mappings refine their source/checker/state/numeric/package boundaries |
| Research before implementation | Source reading, proposed contracts and standalone mathematical probes only; no production Python compiler or HLS flow started |
| Use Codex discussion and review | Three scoped study authors, cross-author review and parent integration; all changes inspected and material findings repaired below |
| Maintain the research repository and website | Navigation and contracts updated; local validation and publication evidence recorded below |

The main corpus is the six lab pages and cheatsheet. Products.scala is read as a complete short file; UnitTests.scala and MachSuite.scala are construct inventories with selected inspected spans. The three reference files total 7,729 lines; no claim is made that all algorithms were translated, accepted by a compiler or executed. Hardware exercises, historical student reports and infrastructure setup are not counted as new successful kernels.

## Review findings and repairs

| Finding | Resolution |
|---|---|
| Exact reduction keywords were missing; generic policy fields could be mistaken for source API | Closed reduce/fold/tree/memory signatures, identity versus seed and empty/disabled behavior; no invented `policy=` source keyword |
| Memory fixed-tree semantics existed without a corresponding source form | Added `mem_tree_reduce` registration, with fixed topology and explicit empty-result rules; not claimed as an original course spelling |
| A mapper returned newly allocated SRAM through an ordinary helper return | `Contribution[M]`/`contribute` transfers ownership only at the memory mapper yield; keep lease through its read/combine obligations |
| `mux` and lazy source `if` were merged | Split eager-value `select` from lazy branches; operand effects cannot silently disappear |
| Queue transfers were briefly described as atomic batches | Restored R008 per-item capture/validate/issue/commit and retained prefixes on later fault; explicit vector batches remain a separate operation |
| FIFO status was shown as a property | Consistent `is_empty()`/`is_full()`/`occupancy()` observation methods |
| FSM action Unit and literal LUT/source intrinsic imports lacked explicit registry entries | Added Unit, nested literal lut initialization and finite frozen math/RNG imports |
| Generic GEMM wording claimed A/B padding was initialized | Only C/contribution padding is initialized; input reads are guarded within loaded rectangles |
| Distinct port names were treated as a possible substitute for noalias requirements | Explicit `requires(disjoint(...))` for accumulating GEMM and convolution; prepare verifies actual backing/view regions |
| Convolution read unavailable LineBuffer history before masking the output | Lazy guard before the read; RegFile retains the previously specified initialized reset image |
| Runtime LineBuffer logical width versus static capacity was left abstract | Registered invocation-width initialization and explicit active views; additional staging/version storage remains accounted separately |
| Buffering/parallel requests had no concrete attachment record | Versioned plan-request schema tied to checked program/subject identity; physical slots cannot increase semantic credits |
| Two extended-reference labels overstated their source | SpecialMath identified as saturating/stochastic operators; GEMM_NCubed identified as untiled dot-product GEMM |

All three reviewers separately noticed the strict-mux/lazy-branch distinction; two independently noticed the premature lease-release wording. The parent accepted those findings after checking the shared contracts. The queue-transfer challenge caught a further integration error. Review agreement is evidence of a review process, not proof that an unimplemented compiler is correct.

## Reproducible design probes

The parent ran [the standalone probe archive](<50 - Python Rewrite/60 - Validation/assets/2026-10-01-course-syntax-probes.zip>) on 1 October 2026. It contains `design_probes.py`, a README and the exact JSON result. Run `python3 design_probes.py`; only Python's standard library is needed.

Archive SHA-256: `0759163132f1ffc15b83bbbb4dc45d7b28a1409b9cd2c479809db1cf7362aba2`.

| Parent rerun | Observation |
|---|---|
| Fixed-point GEMM, direct dot products versus blocked outer products | 48 comparisons passed: zero M/N/K, nonzero initial C, 17×19×18 tails, four tile geometries and extreme raw bits |
| Int32 convolution, direct coordinates versus explicit window state | 73 matrices matched every output and signed gradient; includes 72 small rectangular/extreme-bit matrices and public 16×16 fixture |
| Public convolution fixture | 256 output cells, sum 44,928, maximum 1,088 |
| Original FSM | 32 cells matched the literal gold vector |
| Alternative FSM | 32 cells matched the piecewise exercise formula |
| LUT-add | 45 coordinate/base cases matched row-major formula with wrapping |
| Lazy FIFO branch | Trace `[0,1,2,10,20]`, both queues empty; nonselected queue is untouched at each consume |
| Scalar/fold arithmetic | Int32 overflow boundary, sum 496 and seeded fold 497 matched |

These are independently structured host models, not execution of the proposed kernels. The two GEMM models share the specified wrapping/multiply primitive; they do not independently prove that numeric primitive. The convolution models share wrapping but differ in state traversal versus direct coordinate indexing. Finite comparisons do not establish general equivalence, parser acceptance, simulator correctness, schedule legality or hardware quality. The recorded case construction makes the bounded evidence reproducible.

## Document validation and publication

Local checks passed for 14 changed/new Markdown files, 18 Python blocks parsed without importing them, 235 wikilinks and citation ranges across 35 distinct pinned source files. The parent also reconstructed and parsed the complete runtime-width convolution variant from its exact replacement table and verified E1 source equality with R001. AST parsing proves Python syntax only; registered Spatial meaning still needs implementation and conformance tests.

Quartz built 557 Markdown inputs into 1,203 files and copied the existing presentations. Rendered-link review caught an incorrectly resolved ZIP URL; it was changed to the repository's vault-root link convention. The rebuilt six new pages passed 277 internal file/anchor link checks on 2 October. A clean extraction and rerun of the downloadable archive matched its recorded JSON and SHA-256. The final Markdown check including the progress log passed 15 files, 18 Python blocks, 296 wikilinks and 35 distinct pinned source files. Counts concern the integrated snapshot before the publication entry.

## Remaining gates

- Professor adoption of D-28 and deliberate semantic changes.
- Implemented capture/check/prepare/simulator passing positive and negative fixtures, including aliases, faults and partial effects.
- Broader original-source compatibility fixtures where exact legacy behavior is desired; no universal old-backend parity claim.
- Hardware planning, generated HLS, vendor/RTL/board validation and measured performance.

The research outcome is a concrete language-and-compiler proposal. None of these later implementation or hardware gates is marked complete by a successful documentation build.
