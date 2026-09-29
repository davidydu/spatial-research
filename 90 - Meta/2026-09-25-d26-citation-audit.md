---
type: research-note
project: spatial-spec
decision: D-26
status: complete
date: 2026-09-28
---

# D-26 meeting-cut citation and inference audit

All eight research notes and thirteen construct mappings were checked at their stated evidence levels. The writers and reviewers used Codex, following the user's explicit session override of the design's earlier model assignment. Two fresh citation auditors worked independently of the writers; a fresh P-E advocate supplied angle13, and a further fresh reviewer checked the final synthesis against the frozen pre-registration.

## Final result

| Scope | Code-citation occurrences checked | Supported | Incorrect remaining | Load-bearing claims re-derived |
|---|---:|---:|---:|---:|
| Eight research notes | 392 | 392 | 0 | 40/40 |
| Thirteen mappings, after correction | 291 | 291 | 0 | 65/65 |
| **Total** | **683** | **683** | **0** | **105/105** |

Counts include repeated frontmatter/prose citations, not only distinct anchors. There are 460 distinct anchors when deduplicated within each note and summed. All 96 URL occurrences were supported; the auditors fetched 47 globally distinct URL strings (15 in mappings, 34 in research, 2 shared), with access-method recoveries disclosed below. Every code citation was resolved against its manifest SHA, not only the current worktree.

The mapping audit initially found one partially false statement among 290 code occurrences: C0 incorrectly included masked-off lanes in FIFO conflicts. Q167 records the correction; the final entry adds an explicit tail citation. D0's preservation-rating basis was also clarified consistently with other designed extensions and independently rechecked. The research auditor found no substantive citation failure; an absolute system SDK path was replaced by portable discovery as a hygiene correction. No unresolved audit finding remains.

The independent research auditor reran all 24 external fixtures and all 10 Exo cases/controls; outcomes and transcripts matched exactly after only the disclosed path normalization. The main session had separately rerun selected cases, checked five claims per note/entry and recounted the concept inventory. These checks do not constitute student trials, exact cross-language semantic parity, simulator performance results, or a second independent mapping rating.

The final synthesis review found no substantive inference issue. Before the permitted final status change, the D-26 prefix preceding Research findings was byte-identical to the pre-research snapshot ae2f3fd (5,011 bytes, SHA-256 e6f57ab56559c4f95414c7681046caf539ba5a707b7658cfaf2e80b8b6a5cfda). The only later prefix change is status from pre-registered to awaiting-user-confirmation. Blank weights, k=10 and the original lists remain unchanged. A wording clarification in angle8 replaced ambiguous checked ingress with unchecked-AST ingress; it changes no evidence or recommendation.

The audit supports the epistemic limits in [[D-26]]: provisional R-X continuity is a judgment, Python AST preservation remains designed, whole-list error parity and k=10 are unmeasured, and the strongest P-E ownership case remains a viable basis for David's choice. Nothing here adopts the architecture or authorizes publication.

The detailed reports below preserve original findings and closure evidence. Scratch evidence filenames identify the session's raw records; the full programs/transcripts and the substantive audit derivations are retained in the vault notes themselves.

## Independent D-26 research-note audit

Audit date: 2026-09-28. Auditor: fresh Codex research-audit agent. Scope: angles 1a, 1c, 2, 3, 5, 8, 10 and 13, including angle 2's final per-lab appendix. No note was edited by this auditor. No Claude, delegated agent, vendor tool, compiler rebuild, or compiler mutation was used.

### Result and issues

**Pass for citation resolution and behavioral support at the notes' stated evidence levels.** All 392 explicit pinned code/spec citation occurrences resolve correctly; every distinct anchor was read for support, not merely checked for line bounds. No remaining incorrect citation or material unsupported behavioral conclusion was found. This does not certify an implemented Python frontend, full language conformance, student outcomes, simulator performance, or a final architecture winner.

One hygiene issue was reported immediately and corrected by the main agent before the final snapshot:

| Issue | Original text/source | Required fix | Final status |
|---|---|---|---|
| H1: literal absolute system path | Angle 3 reproduction paragraph specified an absolute macOS SDK path in `SDKROOT`. This was a public system path, not a private account identifier. | Replace the machine-specific spelling with SDK discovery while preserving the actual run description. | Main agent replaced it with `SDKROOT="$(xcrun --sdk macosx --show-sdk-path)"`; rechecked. Resolved hygiene issue, not a behavioral failure. |

There were no silent corrections. The final notes contain no user-home paths, private-course repository identifiers, credential-like strings or absolute local execution paths. Public contributor names and the intentionally named personal-weight owner are not treated as leaked private identifiers. Relative traceback paths are explicitly normalized, and the normalization preserves the recorded messages.

### Method and counts

The basic method in `30 - Adversarial Review.md` was strengthened to inspect every code anchor's adjacent claim. Citations were independently extracted from the final notes, without using the convenience inventory. Each repository name and full resolved SHA was matched against `90 - Meta/reference-clones.md`; source bytes were obtained with pinned Git reads. Every inclusive line range is positive and within EOF. Repeated ranges were read once at source level, then checked against every claim using them. Overlapping ranges were also reviewed as merged source intervals to avoid losing surrounding behavior.

An **occurrence** is one explicit `<name>@<sha>:<path>:<start>-<end>` citation in either frontmatter or prose. A **unique anchor within a note** is one distinct complete citation string, including its line range. Counts therefore retain overlaps and distinguish different ranges in the same file. Traceback frames are measured transcript text, not additional pinned-citation occurrences; they were checked against the raw recordings and reruns separately. URLs are counted separately, including frontmatter/prose repetitions and distinct fragments.

| Angle | Code occurrences checked | Correct | Incorrect | Unique anchors in note | URL occurrences | Unique URLs in note |
|---|---:|---:|---:|---:|---:|---:|
| 1a | 89 | 89 | 0 | 39 | 20 | 9 |
| 1c | 59 | 59 | 0 | 43 | 30 | 21 |
| 2 | 44 | 44 | 0 | 25 | 0 | 0 |
| 3 | 65 | 65 | 0 | 39 | 0 | 0 |
| 5 | 47 | 47 | 0 | 31 | 4 | 2 |
| 8 | 28 | 28 | 0 | 12 | 0 | 0 |
| 10 | 26 | 26 | 0 | 13 | 0 | 0 |
| 13 | 34 | 34 | 0 | 17 | 6 | 3 |
| **Total** | **392** | **392** | **0** | **219** | **60** | **35** |

There are **191 globally distinct code anchors**, **34 globally distinct URL strings**, and **19 HTTP resources after removing URL fragments**. The 219 and 35 column totals are sums of per-note unique counts, not global deduplicated totals. All 60 URL occurrences support the bounded adjacent claims. No cited HTTP resource remained unavailable after alternate read methods. Access failures and recoveries are recorded below.

All eight notes' final SHA-256 hashes, extraction results, source excerpts, URL fetch records and independent executions are retained in `audit-research-scratch/`. The final hash check is needed if authors change notes after this audit.

### Execution and example checks

- Independently re-executed **all 24 external fixtures** with the already-built check binary. All exit codes, stdout and stderr exactly match `binary-runs.json`. Its SHA-256 equals the note's recorded `73cabf0e77937a2b4294316010b9c457b6a01cc4f74a4d0a71add42c542c883a`.
- Independently re-executed **all 10 Exo fixtures** in the existing isolated Python environment, with bytecode writes disabled. All exit codes, stdout and stderr exactly match `python-runs.json`, including the bounds counterexample and valid controls. These are frontend/scheduling executions, not generated-C or hardware runs.
- Compared **34 complete fixture listings and published transcripts** against fixture files and raw records: all match after only the declared path normalization. All 24 Cargo/binary records also match after the input-path normalization. The additional Allo import-failure transcript matches `allo-probe.json`; no Allo compiler result was inferred beyond the failed import.
- Angle 2's three Scala blocks match their pinned sources byte-for-byte. Its nine proposed Python listings parse as Python syntax without importing or executing hypothetical packages. Their high-level operations remain designed APIs. The external compositions were checked against the canonical grammar and semantic rules; successful compilation or cross-language numerical/schedule parity is not claimed.
- The union concept table has exactly nineteen no-hardware rows. Recounted totals are **14/6/13/11/12** for Scala/external/tracing/builder/AST. The per-lab absences are consistent with the listings and yield **12/4/11/9/10**, **14/6/13/11/12**, and **14/5/12/10/11**. This validates the stated rubric arithmetic, not the rubric's educational predictive value.

### Five load-bearing claims re-derived per note

#### Angle 1a

1. **Allo owns substantial frontend work in Python — correct, source inspection.** `customize.py:1351-1408` obtains the AST, runs `TypeInferer`, then invokes `ASTTransformer`; `utils.py:136-161` adjusts original line numbers. Native `AlloTypes.cpp:21-54` exposes MLIR type constructors. This supports the stated integration depth without making a runtime or performance claim.
2. **Allo's error presentation can reconstruct rather than reproduce source — correct, source/test inspection.** `logging.py:10-46` uses `ast.unparse`, searches statement text and warns on a failed match. `test_traceback.py:15-88` contains the quoted line/message assertions. The note correctly calls them expectations and does not say this audit ran those tests.
3. **Exo is a Python compiler that supports explicit host metaprogramming — correct.** `API.py:35-49,168-173` parses, type-checks and invokes bounds/alias checks; `LoopIR_compiler.py:323-348` returns generated C/header strings. `test_metaprogramming.py:11-45` contains `with python`, `with exo`, unrolling and host conditionals. Generated C is not misidentified as Exo's compiler implementation language.
4. **Calyx-py emits text and source metadata, while ordinary Rust diagnostics use input spans — correct.** `py_ast.py:21-27,63-101,134-150`, `main.rs:79-106`, `parser.rs:78-102`, `attributes.rs:81-84` and `errors.rs:29-55` establish the distinct paths. The inference that metadata alone does not prove Python-line remapping is appropriately limited.
5. **PyMTL separates Python RTLIR/error handling from optional compiled simulation, and teaching evidence is reported rather than comparative — correct.** RTLIR generation and caret formatting are present in the cited Python sources; the wrapper uses CFFI `dlopen`. The fetched maintainer PDF's page 27, labelled slide 26, reports architecture/chip-design course use. The Allo catalogue independently reports a Georgia Tech guest lecture. Neither supports a controlled educational advantage, and the note does not claim one.

#### Angle 1c

1. **Dahlia checks legality before backend emission — correct.** `Compiler.scala:156-189` orders well-formedness, type, bounds, loop, dependent-loop, capability and affine checking before `codegen`; `:116-119` includes Calyx backend selection. All seven listed check families' implementing branches and message bodies were inspected.
2. **Dahlia's bounds policy is not uniformly rejecting — correct.** `BoundsCheck.scala:55-84` throws for excessive static/index maxima but warns for potentially excessive sized integers. The note preserves this distinction. Resource consumption, banking divisibility, repeated writes and loop-use conflicts also match their cited branches.
3. **Calyx has two distinct source-position mechanisms — correct.** `position.rs`, `attributes.rs` and `errors.rs` use file contents and spans; `SourceInfoTable` separately stores paths, line locations and variable/memory mappings. Dahlia's `Ast.scala:14-83` keys its emitted metadata by line. The width-error expectation targets `.futil`, supporting the warning against assumed original-DSL remapping.
4. **Ruff demonstrates CLI-in-wheel packaging and a configured platform matrix — correct, fetched pinned configuration.** The exact pyproject lines match the note. The workflow's target, manylinux/musllinux and conditional smoke-test branches match every listed family. The sdist smoke test provisions Rust. The conditional inference about installing a compatible prebuilt wheel is sound; published artifact completeness and install success were not claimed.
5. **IPython can host an external cell without adding a language frontend — correct as API plus proposed adapter.** The official page exposes `(line, cell)`, `self.shell.user_ns`, extension registration and `%load_ext`. JSON exchange and Spatial-specific behavior remain explicitly designed; completion/debugging services are not inferred from the callback.

#### Angle 2

1. **The three original workloads are characterized faithfully — correct.** The exact Scala sources show two-buffer scale, nested scalar `Fold`, and K/M/N tiled fixed-point `MemFold` with lane requests 2 and 16. The file called “reduce” actually contains Fold, as stated.
2. **The proposed ports retain the relevant algorithm structure without asserting schedule equivalence — correct at design level.** Each scale alternative keeps two SRAMs; fold alternatives keep ordered contribution structure; GEMM alternatives keep K/M/N tile order, load existing C and contribute one product per memfold iteration. The missing `.buffer` equivalence is explicit. These are not claims of executed bitwise parity.
3. **Active memfold views and explicit tails reflect the specification — correct.** `language-spec.md:868-910` requires initialized accumulator elements, fully written matching temporary views, no accumulator access in the body and masked partial lane groups. The constructed active slices respect the described obligations; actual proof/checker implementation remains unmeasured.
4. **The Python syntax precedents support mechanisms, not the invented APIs — correct.** Calyx's group/context and guard-expression code, Allo's typed blocked GEMM, Exo's decorator/loops and PyMTL's masked arithmetic match their descriptions. PyMTL arithmetic is explicitly not offered as symbolic-tracing evidence. The nine hypothetical listings are syntactically parsable only.
5. **The concept totals are reproducible but do not measure learning — correct.** Recounted all nineteen rows and the three per-lab absence sets. Scalar contribution handoff appears in Lab1Part6; GEMM memory writes are counted as mutation, not an invented extra handoff. The subjective granularity and familiarity limits are stated.

#### Angle 3

1. **M1 detects its tile divisibility mismatch — correct, independently executed.** N=30/TILE=16 returns E0403 with both sizes. `tiled1d.rs:570-581` contains the corresponding divisibility branch. The adapter-specific help is accurately criticized as a judgment.
2. **M2's rejection does not isolate nondivisibility — correct, independently executed.** P=3 and the dividing P=2 control both reject with E0408; `reductions.rs:142-162` specifically requires P=1. Exo's perfect loop division rejects 16/3 for the distinct stated obligation. No identical-construct equivalence is inferred.
3. **Direct writable DRAM assignment is legal under the external spec — correct.** `language-spec.md:777-791` permits indexed output/inout DRAM writes, and M5 exits zero. Treating row 5 as a valid control is justified; the frozen mistake list is not retroactively “fixed.”
4. **All eight canonical lab/variant inputs hit parser barriers — correct, independently executed.** L1/V1/V3 reject at `seq foreach`; L2/V2/V5 at `init`; L3/V4 at canonical FixPt spelling. The note distinguishes these from three accepted legacy controls and from semantic proof failures.
5. **Exo's bounds example rejects before code generation while the external LUT example accepts — correct, independently executed.** P8 produces the recorded negative-index counterexample; PC-lut accepts. M8 accepts and its requires control rejects lexically. `boundscheck.py:818-840` explains the counterexample path. Exo's uninitialized examples also accept at decoration, and the note correctly stops its claim there. Scala remains source-only, with supported Reduce omission distinguished from a nonexistent missing-init error.

#### Angle 5

1. **Normative diagnostics and implementation stages differ — correct.** The spec requires six semantic/parser categories, precise primaries/secondaries, poison handling and ordering. The current compiler's parse/const/HIR/classify chain is narrower. The inspected zero-dimension test specifically expects E0506 at `CompileStage::Const` with `N` and its defining `0`; no passing-test execution is claimed.
2. **An unchecked AST ingress preserves different responsibilities from text or checked IR — correct as design reasoning.** Text invokes token parsing on generated text; a closed unchecked AST can retain names/constants/types for shared passes; already-resolved IR cannot recover discarded syntax merely by carrying a final value. Python syntax errors remain frontend-owned. The note does not label the proposed ingress implemented.
3. **Calyx provenance plus IR verification does not establish full high-level diagnostic parity — correct.** Builder construction, stack-derived lines, emitted `@pos`, copied sourceinfo and positioned invocation-subtype errors are present. The separately inspected ordinary error path uses spans. The note's negative inference is appropriately narrower than “Calyx never remaps.”
4. **Allo/MLIR provide location machinery alongside frontend-owned checking — correct.** Allo's AST dispatch uses file locations or unknown locations after Python inference. Fetched MLIR documentation supports range/callsite/fused/named/unknown locations, operation locations, located notes, source-line display and framework-location filtering. None is presented as a replacement for semantic checks.
5. **ADR envelopes are specifications, not current CLI support — correct.** The pinned CLI admits only `Check(PathBuf)` and text output. The ADR defines `spatial.run.v1`, `spatial.diagnostics.v1`, ABI/build metadata and the separate host-child protocol. The report direction, exact number encoding and host-child/parent distinction match the cited sections. Future PyO3 calls are explicitly proposed.

#### Angle 8

1. **Retaining Rust does not mean Phase 1 is already complete — correct.** The existing entry is a classifier pipeline, while the cited roadmap requires generic controller-tree lowering, interpretation and equality over 39 corpus programs. The source supports a planned milestone, not an already-run 39-program general interpreter result.
2. **Existing assets remain useful under either implementation language — correct with judgment labelled.** Scalar/tiled oracle functions, port manifests and the no-execute driver branch are present. Reusing knowledge/results versus reusing implementation is a design/cost distinction, not a measured migration saving.
3. **Fresh backend evidence is a separate obligation — correct.** The roadmap's Phase 2 explicitly requires structural emission and fresh selected csim/csynth evidence when emitted HLS changes. No vendor run was performed by this audit or newly attributed to the note.
4. **The three maintenance scenarios identify real work without proving a staffing ranking — correct.** Diagnostic fields are structured but no external message catalogue is provided by that struct; new constructs still need semantics; the driver has explicit tool/log/report paths. Python familiarity and TA-editable catalogues remain assumptions or designs.
5. **The source-size inventory is exact but not a productivity ratio — correct.** Recounted pinned physical lines including comments/tests: `validate.rs` 5,363; Exo `pyparser.py` 1,754; Allo `builder.py` 3,778. The validator entry checks adapter shape/kind/name, so its size cannot be credited as a general obligation calculus. The note preserves that limitation.

#### Angle 10

1. **The synthesis separates core language, student surface and integration — supported.** Existing Rust continuity, Python compiler feasibility and the current check-only CLI are backed by the inspected sources and notes. R-X is explicitly a next-milestone judgment, not a measured educational/speed winner.
2. **The 13-style inventory is a first-rating design result — supported.** Independently aggregated every mapping frontmatter: tracing 6 yes/6 awkward/1 no, builder 13 yes, AST 13 yes with all five categories. The overview and mappings require source/token retention and a real DSL resolver. The synthesis does not promote these to implemented parity or two-rater agreement.
3. **Current surface-error evidence cannot select a measured teaching winner — supported.** The external parser false rejections and Exo successes are real, but examples are not equivalent across every rule, Scala was not executed and Allo was blocked. No novice repair/outcome measurements appear in the audited evidence.
4. **There is no defensible equal-weight numerical winner — supported as methodological judgment.** The notes contain heterogeneous qualitative mechanisms, concept inventory counts and missing simulator/staffing/install/learning measurements; no calibrated utility scale or normalized scores exist. The provisional recommendation is not misattributed to arithmetic. The requested blind audit did not reopen the architecture research-design/dispatch files, so historical fidelity of the personal-weight blanks is outside this check; the absence of a numerical ranking in the synthesis is verified.
5. **Every reversal's stated evidence status is coherent — supported.** Design-level all-five coverage is available; whole-list Python diagnostic parity is not; k=10 is unmeasured in both directions; the conjunction therefore has not fired; no all-styles impossibility was established; E/B delivery guarantees remain commitments. Missing evidence is not converted into Rust victory or Python disqualification. See the separate row audit below.

#### Angle 13

1. **Python can own parsing, type/bounds/alias checking and C emission — correct, source-backed.** The Exo pipeline and PyMTL RTLIR/error implementation directly support feasibility. Their different target semantics and optional native simulator/backend dependencies do not invalidate the limited compiler-core claim; the note does not claim identical Spatial conformance.
2. **AST can retain the mapped information only with additional frontend machinery — supported design claim.** All thirteen first ratings and the naming/order mappings require closed resolution, tokens, declaration identities and ordered effects. The note keeps these conditional, not present error parity.
3. **The existing Rust prototype leaves major general-compiler work — correct.** `compiler.rs`, `validate.rs` and the implementation-status table support the stated gap. Shared specifications/oracles remain assets in both alternatives; no reimplementation time is measured.
4. **Python-looking assignment can conceal a real evaluation-order difference — correct.** Fetched Python documentation specifies RHS-before-LHS assignment; Spatial `:831-837` specifies lvalue-index evaluation before RHS and immediate dequeue consumption. The AST remedy and teaching burden are explicitly design/judgment. Amaranth's `__bool__` rejection is present at the cited source.
5. **P-E is selected conditionally on the stipulated ownership scenario — epistemically sound judgment.** The note labels staff/student familiarity as assumptions, acknowledges the external rubric's lower count, preserves the unmeasured k=10 gate, exact literal/numeric rules and closed proof calculus, and states falsifiers favoring P-X or R-E. It does not claim measured productivity, learning benefit or simulator superiority.

### Angle 10 reversal-status audit

This checks support and logic for all seven stated rows; it does not reopen the prohibited original architecture-design/dispatch artifacts to authenticate historical registration wording.

| Stated condition | Evidence status checked | Audit result |
|---|---|---|
| Every mapping has one yes/all-five style | Thirteen token-backed AST first ratings, with five fields each | Correct at designed representability level only; explicit nonimplementation and single-rating caveats retained |
| Python parity across whole fixed error list | Angle 3's analogues, source-only Scala, unavailable Allo, valid row 5 | Correctly not established |
| Python simulator within 10× Rust | No matched general interpreter benchmark in the evidence | Correctly unknown, not inferred from frontend acceptance |
| Conjunction makes R-* lose | Missing diagnostic and simulator premises | Correctly not triggered; no Rust victory inferred |
| Some obligation impossible under every Python style | AST representations remain plausible; no impossibility evidence | Correctly not established |
| Python simulator exceeds 10× | No ratio measurement | Correctly unknown/not triggered |
| E/B guarantees | Shared IR/catalogue, paired labs/message goldens, wheels, releases and TA-editable catalogue are undelivered commitments | Correctly not claimed complete |

### URL access and support

All URL resources were opened on 2026-09-28. Normal HTTP fragment semantics apply: each Ruff fragment names a range in the same fetched pinned file; all fifteen line-range fragments were checked against its actual line count and their adjacent claims. The broad workflow inventory range was read as configuration, not CI execution proof.

Access-path limitations were recovered rather than silently ignored:

- The PyMTL talk failed in the web reader; direct HTTPS returned 200 and PDF text extraction recovered page 27/slide 26. The course statement matches that slide.
- Direct HTTPS returned 403 for PyMTL translation, Ruff installation and IPython custom-magics pages; the web reader successfully opened their text and the relevant sections.
- Both pinned Ruff raw files returned 200 through direct HTTPS. Their source lines were checked locally against all fragment references.
- Other resources opened successfully. No unavailable URL was counted as supporting a positive claim. The note's historical report that a separately linked Georgia Tech page failed is not a positive evidentiary premise and was not used to validate the guest-lecture claim; the fetched maintainer catalogue supports that claim directly.

The following ledgers enumerate every final unique URL and pinned anchor. “Correct” means both resolution and support at the evidence level stated in the note, not an execution guarantee.

### Exhaustive URL ledger

| URL | Angles; occurrences | Support/access result |
|---|---|---|
| [Allo tutorial catalogue](https://github.com/cornell-zhang/allo-tutorials) | 1a: 3 | Correct — Guest lecture, institution/course and date; direct 200 and web reader |
| [Exo project site](https://exo-lang.dev/) | 1a: 2 | Correct — MIT core developers and request for feedback; direct 200 and web reader |
| [Exo case study](https://exo-lang.dev/tutorial.html) | 1a: 2 | Correct — Tutorial only; no course deployment inferred; direct 200 and web reader |
| [Calyx builder walkthrough](https://docs.calyxir.org/builder/walkthrough.html) | 1a: 2 | Correct — Python component, group, assignment and control construction; direct 200 and web reader |
| [Calyx frontend tutorial](https://docs.calyxir.org/tutorial/frontend-tut.html) | 1a: 2 | Correct — Compiler construction tutorial; no course deployment inferred; direct 200 and web reader |
| [Calyx contributors](https://docs.calyxir.org/contributors.html) | 1a: 2 | Correct — Adrian Sampson listed among current contributors; direct 200 and web reader |
| [PyMTL quick start](https://pymtl.github.io/) | 1a: 2 | Correct — Component/update-block/operator syntax; direct 200 and web reader |
| [PyMTL translation contract](https://pymtl3.readthedocs.io/en/latest/ref/passes-translation-intro.html) | 1a: 2, 13: 2 | Correct — Restricted translatable subset excludes arbitrary calls and containers; web reader success after direct 403 |
| [PyMTL course-use talk](https://www.csl.cornell.edu/~cbatten/pdfs/batten-pymtl3-nvidia2023.pdf) | 1a: 3 | Correct — PDF page 27/slide 26 course-use statement; direct 200 plus text extraction after web-reader failure |
| [Pinned Ruff pyproject L1-L3](https://raw.githubusercontent.com/astral-sh/ruff/4b84fcf6b9a0158d1b17c06730d58590352b8869/pyproject.toml#L1-L3) | 1c: 2 | Correct — Exact maturin/bin packaging lines; direct 200; fragment in bounds |
| [Pinned Ruff pyproject L47-L52](https://raw.githubusercontent.com/astral-sh/ruff/4b84fcf6b9a0158d1b17c06730d58590352b8869/pyproject.toml#L47-L52) | 1c: 2 | Correct — Exact maturin/bin packaging lines; direct 200; fragment in bounds |
| [Pinned Ruff workflow L81-L617](https://raw.githubusercontent.com/astral-sh/ruff/4b84fcf6b9a0158d1b17c06730d58590352b8869/.github/workflows/build-binaries.yml#L81-L617) | 1c: 1 | Correct — Configured targets/compatibility or smoke-test condition, not published/run success; direct 200; fragment in bounds |
| [Pinned Ruff pyproject whole file](https://raw.githubusercontent.com/astral-sh/ruff/4b84fcf6b9a0158d1b17c06730d58590352b8869/pyproject.toml) | 1c: 2 | Correct — Exact maturin/bin packaging lines; direct 200; fragment in bounds |
| [Pinned Ruff workflow whole file](https://raw.githubusercontent.com/astral-sh/ruff/4b84fcf6b9a0158d1b17c06730d58590352b8869/.github/workflows/build-binaries.yml) | 1c: 2 | Correct — Configured targets/compatibility or smoke-test condition, not published/run success; direct 200; fragment in bounds |
| [Ruff installation](https://docs.astral.sh/ruff/installation/) | 1c: 2 | Correct — pip installation documented; web reader success after direct 403 |
| [Maturin bindings](https://www.maturin.rs/bindings.html) | 1c: 2 | Correct — bin packages executable scripts available on PATH; direct 200 and web reader |
| [Maturin distribution](https://www.maturin.rs/distribution.html) | 1c: 2 | Correct — Platform compatibility and source-build distinction; direct 200 and web reader |
| [IPython custom magics](https://ipython.readthedocs.io/en/stable/config/custommagics.html) | 1c: 3 | Correct — Cell payload, namespace and extension registration; web reader success after direct 403 |
| [Pinned Ruff workflow L63-L74](https://raw.githubusercontent.com/astral-sh/ruff/4b84fcf6b9a0158d1b17c06730d58590352b8869/.github/workflows/build-binaries.yml#L63-L74) | 1c: 1 | Correct — Configured targets/compatibility or smoke-test condition, not published/run success; direct 200; fragment in bounds |
| [Pinned Ruff workflow L96-L102](https://raw.githubusercontent.com/astral-sh/ruff/4b84fcf6b9a0158d1b17c06730d58590352b8869/.github/workflows/build-binaries.yml#L96-L102) | 1c: 1 | Correct — Configured targets/compatibility or smoke-test condition, not published/run success; direct 200; fragment in bounds |
| [Pinned Ruff workflow L157-L163](https://raw.githubusercontent.com/astral-sh/ruff/4b84fcf6b9a0158d1b17c06730d58590352b8869/.github/workflows/build-binaries.yml#L157-L163) | 1c: 1 | Correct — Configured targets/compatibility or smoke-test condition, not published/run success; direct 200; fragment in bounds |
| [Pinned Ruff workflow L197-L208](https://raw.githubusercontent.com/astral-sh/ruff/4b84fcf6b9a0158d1b17c06730d58590352b8869/.github/workflows/build-binaries.yml#L197-L208) | 1c: 1 | Correct — Configured targets/compatibility or smoke-test condition, not published/run success; direct 200; fragment in bounds |
| [Pinned Ruff workflow L284-L323](https://raw.githubusercontent.com/astral-sh/ruff/4b84fcf6b9a0158d1b17c06730d58590352b8869/.github/workflows/build-binaries.yml#L284-L323) | 1c: 1 | Correct — Configured targets/compatibility or smoke-test condition, not published/run success; direct 200; fragment in bounds |
| [Pinned Ruff workflow L388-L396](https://raw.githubusercontent.com/astral-sh/ruff/4b84fcf6b9a0158d1b17c06730d58590352b8869/.github/workflows/build-binaries.yml#L388-L396) | 1c: 1 | Correct — Configured targets/compatibility or smoke-test condition, not published/run success; direct 200; fragment in bounds |
| [Pinned Ruff workflow L437-L461](https://raw.githubusercontent.com/astral-sh/ruff/4b84fcf6b9a0158d1b17c06730d58590352b8869/.github/workflows/build-binaries.yml#L437-L461) | 1c: 1 | Correct — Configured targets/compatibility or smoke-test condition, not published/run success; direct 200; fragment in bounds |
| [Pinned Ruff workflow L452-L456](https://raw.githubusercontent.com/astral-sh/ruff/4b84fcf6b9a0158d1b17c06730d58590352b8869/.github/workflows/build-binaries.yml#L452-L456) | 1c: 1 | Correct — Configured targets/compatibility or smoke-test condition, not published/run success; direct 200; fragment in bounds |
| [Pinned Ruff workflow L524-L549](https://raw.githubusercontent.com/astral-sh/ruff/4b84fcf6b9a0158d1b17c06730d58590352b8869/.github/workflows/build-binaries.yml#L524-L549) | 1c: 1 | Correct — Configured targets/compatibility or smoke-test condition, not published/run success; direct 200; fragment in bounds |
| [Pinned Ruff workflow L587-L617](https://raw.githubusercontent.com/astral-sh/ruff/4b84fcf6b9a0158d1b17c06730d58590352b8869/.github/workflows/build-binaries.yml#L587-L617) | 1c: 1 | Correct — Configured targets/compatibility or smoke-test condition, not published/run success; direct 200; fragment in bounds |
| [Pinned Ruff workflow L258-L264](https://raw.githubusercontent.com/astral-sh/ruff/4b84fcf6b9a0158d1b17c06730d58590352b8869/.github/workflows/build-binaries.yml#L258-L264) | 1c: 1 | Correct — Configured targets/compatibility or smoke-test condition, not published/run success; direct 200; fragment in bounds |
| [Pinned Ruff workflow L483-L485](https://raw.githubusercontent.com/astral-sh/ruff/4b84fcf6b9a0158d1b17c06730d58590352b8869/.github/workflows/build-binaries.yml#L483-L485) | 1c: 1 | Correct — Configured targets/compatibility or smoke-test condition, not published/run success; direct 200; fragment in bounds |
| [MLIR locations](https://mlir.llvm.org/docs/Dialects/Builtin/#location-attributes) | 5: 2 | Correct — Range/callsite/fused/named/unknown location mechanisms; direct 200 and web reader |
| [MLIR diagnostics](https://mlir.llvm.org/docs/Diagnostics/) | 5: 2 | Correct — Operation/notes locations, source display and framework filtering; direct 200 and web reader |
| [Python AST locations](https://docs.python.org/3/library/ast.html#ast.AST) | 13: 2 | Correct — Node start/end source positions, byte offsets and optional end fields; web reader success |
| [Python evaluation order](https://docs.python.org/3/reference/expressions.html#evaluation-order) | 13: 2 | Correct — Assignment evaluates RHS before LHS; web reader success |

### Exhaustive code-anchor ledger

All entries below are correct for path/SHA/bounds and support. Line numbers in the last column are note locations, not source ranges. Repeated frontmatter/body occurrences are retained in the occurrence count.

#### Angle 1a — D-26-01a-precedent-python-over-core.md

| Unique pinned anchor | Occurrences | Note lines | Result |
|---|---:|---|---|
| `allo@094ab41:allo/customize.py:1351-1408` | 3 | 7, 65, 70 | Correct |
| `allo@094ab41:allo/customize.py:176-197` | 3 | 8, 65, 110 | Correct |
| `allo@094ab41:allo/ir/utils.py:136-161` | 2 | 9, 70 | Correct |
| `allo@094ab41:mlir/lib/Bindings/AlloTypes.cpp:21-54` | 3 | 10, 65, 70 | Correct |
| `allo@094ab41:allo/logging.py:10-46` | 2 | 11, 70 | Correct |
| `allo@094ab41:tests/test_traceback.py:15-88` | 2 | 12, 70 | Correct |
| `allo@094ab41:setup.py:99-112` | 2 | 13, 65 | Correct |
| `exo@defe172:src/exo/API.py:35-49` | 3 | 15, 66, 72 | Correct |
| `exo@defe172:src/exo/API.py:168-173` | 3 | 16, 66, 72 | Correct |
| `exo@defe172:src/exo/frontend/pyparser.py:37-90` | 2 | 17, 72 | Correct |
| `exo@defe172:src/exo/frontend/typecheck.py:144-154` | 3 | 18, 66, 72 | Correct |
| `exo@defe172:src/exo/frontend/typecheck.py:296-324` | 2 | 19, 72 | Correct |
| `exo@defe172:src/exo/backend/LoopIR_compiler.py:323-348` | 3 | 20, 66, 72 | Correct |
| `exo@defe172:tests/test_typecheck.py:189-214` | 2 | 21, 72 | Correct |
| `exo@defe172:tests/test_metaprogramming.py:11-45` | 3 | 22, 66, 72 | Correct |
| `calyx@d6bcdc8:calyx-py/calyx/py_ast.py:21-27` | 2 | 25, 74 | Correct |
| `calyx@d6bcdc8:calyx-py/calyx/py_ast.py:63-101` | 3 | 26, 74, 110 | Correct |
| `calyx@d6bcdc8:calyx-py/calyx/py_ast.py:134-150` | 3 | 27, 67, 74 | Correct |
| `calyx@d6bcdc8:calyx-py/calyx/builder.py:258-267` | 3 | 28, 67, 74 | Correct |
| `calyx@d6bcdc8:calyx-py/calyx/builder.py:1678-1683` | 1 | 29 | Correct |
| `calyx@d6bcdc8:calyx-py/calyx/builder.py:1728-1732` | 2 | 30, 74 | Correct |
| `calyx@d6bcdc8:src/main.rs:79-106` | 3 | 31, 67, 74 | Correct |
| `calyx@d6bcdc8:calyx/frontend/src/parser.rs:78-102` | 2 | 32, 74 | Correct |
| `calyx@d6bcdc8:calyx/frontend/src/attributes.rs:81-84` | 2 | 33, 74 | Correct |
| `calyx@d6bcdc8:calyx/utils/src/errors.rs:29-55` | 2 | 34, 74 | Correct |
| `calyx@d6bcdc8:calyx/opt/src/passes/well_formed.rs:324-351` | 2 | 35, 67 | Correct |
| `calyx@d6bcdc8:runt.toml:214-240` | 2 | 36, 76 | Correct |
| `calyx@d6bcdc8:calyx-py/test/numeric_types.py:79-101` | 2 | 37, 76 | Correct |
| `pymtl3@c8b349f:pymtl3/dsl/ComponentLevel2.py:102-111` | 2 | 41, 78 | Correct |
| `pymtl3@c8b349f:pymtl3/passes/rtlir/behavioral/BehavioralRTLIRGenL1Pass.py:47-80` | 3 | 42, 68, 78 | Correct |
| `pymtl3@c8b349f:pymtl3/passes/rtlir/behavioral/BehavioralRTLIRGenL1Pass.py:470-477` | 2 | 43, 78 | Correct |
| `pymtl3@c8b349f:pymtl3/passes/rtlir/errors.py:26-62` | 2 | 44, 68 | Correct |
| `pymtl3@c8b349f:pymtl3/passes/rtlir/behavioral/test/BehavioralRTLIRL1Pass_test.py:302-314` | 2 | 45, 114 | Correct |
| `pymtl3@c8b349f:pymtl3/passes/rtlir/behavioral/test/BehavioralRTLIRL1Pass_test.py:348-354` | 2 | 46, 78 | Correct |
| `pymtl3@c8b349f:pymtl3/passes/rtlir/util/test_utility.py:18-33` | 2 | 47, 78 | Correct |
| `pymtl3@c8b349f:pymtl3/passes/backends/verilog/import_/VerilogVerilatorImportPass.py:371-430` | 2 | 48, 68 | Correct |
| `pymtl3@c8b349f:pymtl3/passes/backends/verilog/import_/verilator_wrapper_py_template.py:29-58` | 2 | 49, 78 | Correct |
| `pymtl3@c8b349f:setup.py:43-51` | 2 | 50, 68 | Correct |
| `allo@094ab41:allo/customize.py:1369-1408` | 1 | 70 | Correct |

#### Angle 1c — D-26-01c-precedent-external-dsl-over-core.md

| Unique pinned anchor | Occurrences | Note lines | Result |
|---|---:|---|---|
| `dahlia@bd68b13:src/main/scala/Compiler.scala:156-189` | 2 | 7, 44 | Correct |
| `dahlia@bd68b13:src/main/scala/common/Errors.scala:9-44` | 2 | 8, 56 | Correct |
| `dahlia@bd68b13:src/main/scala/common/Errors.scala:52-216` | 1 | 9 | Correct |
| `dahlia@bd68b13:src/main/scala/passes/WellFormedCheck.scala:59-116` | 2 | 10, 48 | Correct |
| `dahlia@bd68b13:src/main/scala/typechecker/TypeCheck.scala:147-163` | 2 | 11, 49 | Correct |
| `dahlia@bd68b13:src/main/scala/passes/BoundsCheck.scala:55-84` | 2 | 12, 50 | Correct |
| `dahlia@bd68b13:src/main/scala/passes/LoopCheck.scala:39-52` | 2 | 13, 51 | Correct |
| `dahlia@bd68b13:src/main/scala/passes/DependentLoops.scala:67-75` | 2 | 14, 51 | Correct |
| `dahlia@bd68b13:src/main/scala/typechecker/CapabilityChecker.scala:48-63` | 2 | 15, 53 | Correct |
| `dahlia@bd68b13:src/main/scala/typechecker/AffineCheck.scala:126-151` | 2 | 16, 54 | Correct |
| `dahlia@bd68b13:src/main/scala/typechecker/Info.scala:26-53` | 2 | 17, 54 | Correct |
| `dahlia@bd68b13:src/main/scala/backends/calyx/Ast.scala:14-83` | 2 | 18, 62 | Correct |
| `calyx@d6bcdc8:calyx/utils/src/position.rs:17-40` | 2 | 19, 60 | Correct |
| `calyx@d6bcdc8:calyx/utils/src/errors.rs:9-75` | 2 | 20, 60 | Correct |
| `calyx@d6bcdc8:calyx/frontend/src/source_info.rs:163-177` | 2 | 21, 62 | Correct |
| `calyx@d6bcdc8:calyx/frontend/src/source_info.rs:681-706` | 2 | 22, 62 | Correct |
| `calyx@d6bcdc8:calyx/opt/src/passes/well_formed.rs:233-259` | 2 | 23, 64 | Correct |
| `dahlia@bd68b13:src/main/scala/Compiler.scala:116-119` | 1 | 44 | Correct |
| `dahlia@bd68b13:src/main/scala/common/Errors.scala:77-89` | 1 | 48 | Correct |
| `dahlia@bd68b13:src/main/scala/common/Errors.scala:207-208` | 1 | 48 | Correct |
| `dahlia@bd68b13:src/main/scala/typechecker/TypeCheck.scala:179-195` | 1 | 49 | Correct |
| `dahlia@bd68b13:src/main/scala/typechecker/TypeCheck.scala:309-320` | 1 | 49 | Correct |
| `dahlia@bd68b13:src/main/scala/common/Errors.scala:62-75` | 1 | 49 | Correct |
| `dahlia@bd68b13:src/main/scala/common/Errors.scala:238-241` | 1 | 49 | Correct |
| `dahlia@bd68b13:src/main/scala/common/Errors.scala:98-102` | 1 | 50 | Correct |
| `dahlia@bd68b13:src/main/scala/common/Errors.scala:180-197` | 1 | 51 | Correct |
| `dahlia@bd68b13:src/main/scala/typechecker/TypeCheck.scala:222-246` | 1 | 52 | Correct |
| `dahlia@bd68b13:src/main/scala/typechecker/TypeCheck.scala:258-263` | 1 | 52 | Correct |
| `dahlia@bd68b13:src/main/scala/typechecker/TypeCheck.scala:453-479` | 1 | 52 | Correct |
| `dahlia@bd68b13:src/main/scala/common/Errors.scala:154-159` | 1 | 52 | Correct |
| `dahlia@bd68b13:src/main/scala/common/Errors.scala:199-216` | 1 | 52 | Correct |
| `dahlia@bd68b13:src/main/scala/common/Errors.scala:142-147` | 1 | 53 | Correct |
| `dahlia@bd68b13:src/main/scala/typechecker/AffineCheck.scala:177-192` | 1 | 54 | Correct |
| `dahlia@bd68b13:src/main/scala/common/Errors.scala:33-43` | 1 | 54 | Correct |
| `dahlia@bd68b13:src/main/scala/common/Errors.scala:119-151` | 1 | 54 | Correct |
| `dahlia@bd68b13:src/main/scala/Compiler.scala:188-205` | 1 | 56 | Correct |
| `calyx@d6bcdc8:calyx/utils/src/position.rs:203-230` | 1 | 60 | Correct |
| `calyx@d6bcdc8:calyx/frontend/src/parser.rs:142-146` | 1 | 60 | Correct |
| `calyx@d6bcdc8:calyx/frontend/src/attributes.rs:12-17` | 1 | 60 | Correct |
| `calyx@d6bcdc8:calyx/frontend/src/attributes.rs:81-84` | 1 | 60 | Correct |
| `calyx@d6bcdc8:calyx/ir/src/context.rs:35-38` | 1 | 62 | Correct |
| `calyx@d6bcdc8:tests/errors/mismatch-widths.expect:1-6` | 1 | 64 | Correct |
| `dahlia@bd68b13:src/main/scala/backends/calyx/Backend.scala:1078-1082` | 1 | 133 | Correct |

#### Angle 2 — D-26-02-student-surface-comparison.md

| Unique pinned anchor | Occurrences | Note lines | Result |
|---|---:|---|---|
| `spatial@e7a8f2f:test/spatial/tests/ee109/Lab1Part2DramSramExample.scala:1-48` | 2 | 7, 140 | Correct |
| `spatial-rs@eb49d8b:crates/spatial-rs-core/testdata/ee109/lab1_part6_reduce.scala:1-43` | 2 | 8, 288 | Correct |
| `spatial-rs@eb49d8b:crates/spatial-rs-core/testdata/ee109/lab2_part6_gemm_fixed_32.scala:1-68` | 2 | 9, 434 | Correct |
| `spatial-rs@eb49d8b:docs/language-spec.md:22-53` | 1 | 10 | Correct |
| `spatial-rs@eb49d8b:docs/language-spec.md:263-348` | 2 | 11, 33 | Correct |
| `spatial-rs@eb49d8b:docs/language-spec.md:852-915` | 1 | 12 | Correct |
| `calyx@d6bcdc8:calyx-py/test/helloworld.py:6-32` | 3 | 13, 39, 243 | Correct |
| `calyx@d6bcdc8:calyx-py/calyx/builder.py:1314-1369` | 2 | 14, 39 | Correct |
| `calyx@d6bcdc8:calyx-py/calyx/builder.py:1588-1598` | 4 | 15, 39, 387, 597 | Correct |
| `allo@094ab41:examples/machsuite/gemm/gemm_blocked.py:12-37` | 2 | 16, 41 | Correct |
| `exo@defe172:examples/cursors/cursors.py:1-44` | 4 | 17, 41, 124, 267 | Correct |
| `exo@defe172:src/exo/API.py:35-49` | 3 | 18, 41, 411 | Correct |
| `pymtl3@c8b349f:pymtl3/datatypes/PythonBits.py:203-262` | 3 | 19, 43, 219 | Correct |
| `spatial@e7a8f2f:test/spatial/tests/ee109/Lab1Part2DramSramExample.scala:6-35` | 1 | 31 | Correct |
| `spatial-rs@eb49d8b:crates/spatial-rs-core/testdata/ee109/lab1_part6_reduce.scala:15-29` | 1 | 31 | Correct |
| `spatial-rs@eb49d8b:crates/spatial-rs-core/testdata/ee109/lab2_part6_gemm_fixed_32.scala:29-58` | 1 | 31 | Correct |
| `spatial-rs@eb49d8b:docs/language-spec.md:97-147` | 1 | 35 | Correct |
| `spatial-rs@eb49d8b:docs/language-spec.md:868-910` | 1 | 35 | Correct |
| `spatial-rs@eb49d8b:crates/spatial-rs-core/testdata/ee109/lab2_part6_gemm_fixed_32.scala:43-55` | 1 | 35 | Correct |
| `allo@094ab41:examples/machsuite/gemm/gemm_blocked.py:12-32` | 2 | 124, 637 | Correct |
| `spatial-rs@eb49d8b:docs/language-spec.md:1099-1107` | 1 | 126 | Correct |
| `spatial-rs@eb49d8b:docs/language-spec.md:35-53` | 1 | 195 | Correct |
| `spatial-rs@eb49d8b:docs/language-spec.md:263-281` | 1 | 338 | Correct |
| `spatial-rs@eb49d8b:docs/language-spec.md:303-348` | 1 | 509 | Correct |
| `spatial-rs@eb49d8b:docs/language-spec.md:886-903` | 1 | 509 | Correct |

#### Angle 3 — D-26-03-error-paths.md

| Unique pinned anchor | Occurrences | Note lines | Result |
|---|---:|---|---|
| `spatial-rs@eb49d8b:docs/language-spec.md:987-1028` | 1 | 7 | Correct |
| `spatial-rs@eb49d8b:docs/language-spec.md:1069-1107` | 1 | 8 | Correct |
| `spatial-rs@eb49d8b:docs/language-spec.md:769-791` | 1 | 9 | Correct |
| `spatial-rs@eb49d8b:docs/language-spec.md:158-167` | 1 | 10 | Correct |
| `spatial-rs@eb49d8b:docs/language-spec.md:263-348` | 2 | 11, 131 | Correct |
| `spatial-rs@eb49d8b:docs/language-spec.md:863-878` | 1 | 12 | Correct |
| `spatial-rs@eb49d8b:crates/spatial-rs-cli/src/lib.rs:88-118` | 2 | 13, 49 | Correct |
| `spatial-rs@eb49d8b:crates/spatial-rs-core/src/compiler.rs:34-67` | 2 | 14, 85 | Correct |
| `spatial-rs@eb49d8b:crates/spatial-rs-core/src/classifier/tiled1d.rs:570-581` | 2 | 15, 133 | Correct |
| `spatial-rs@eb49d8b:crates/spatial-rs-core/src/classifier/reductions.rs:142-162` | 2 | 16, 133 | Correct |
| `spatial-rs@eb49d8b:crates/spatial-rs-core/src/classifier/scalar.rs:425-434` | 2 | 17, 133 | Correct |
| `spatial-rs@eb49d8b:crates/spatial-rs-core/src/classifier/common.rs:78-91` | 2 | 18, 133 | Correct |
| `spatial-rs@eb49d8b:examples/ee109/src/lib.rs:20-34` | 2 | 19, 131 | Correct |
| `spatial-rs@eb49d8b:crates/spatial-rs-core/testdata/ee109/lab1_part6_reduce.scala:15-29` | 2 | 20, 131 | Correct |
| `spatial-rs@eb49d8b:crates/spatial-rs-core/testdata/ee109/lab2_part6_gemm_fixed_32.scala:29-59` | 2 | 21, 131 | Correct |
| `spatial@e7a8f2f:test/spatial/tests/ee109/Lab1Part2DramSramExample.scala:11-33` | 2 | 22, 131 | Correct |
| `spatial@e7a8f2f:test/spatial/tests/feature/dense/MatMult_systolic.scala:77-83` | 2 | 23, 1265 | Correct |
| `spatial@e7a8f2f:src/spatial/traversal/UserSanityChecks.scala:64-78` | 2 | 24, 1266 | Correct |
| `spatial@e7a8f2f:src/spatial/lang/api/SpatialVirtualization.scala:50-63` | 2 | 25, 1267 | Correct |
| `spatial@e7a8f2f:src/spatial/executor/scala/memories/ScalaTensor.scala:17-47` | 2 | 26, 1268 | Correct |
| `spatial@e7a8f2f:src/spatial/lang/DRAM.scala:90-104` | 2 | 27, 1269 | Correct |
| `spatial@e7a8f2f:src/spatial/lang/control/ReduceClass.scala:78-87` | 2 | 28, 1270 | Correct |
| `spatial@e7a8f2f:src/spatial/traversal/CompilerSanityChecks.scala:54-65` | 2 | 29, 1271 | Correct |
| `exo@defe172:src/exo/rewrite/LoopIR_scheduling.py:286-301` | 2 | 30, 1274 | Correct |
| `exo@defe172:src/exo/API_scheduling.py:1696-1742` | 1 | 31 | Correct |
| `exo@defe172:src/exo/API.py:157-171` | 2 | 32, 894 | Correct |
| `exo@defe172:src/exo/frontend/pyparser.py:1497-1511` | 2 | 33, 1274 | Correct |
| `exo@defe172:src/exo/frontend/boundscheck.py:818-840` | 2 | 34, 1274 | Correct |
| `exo@defe172:src/exo/libs/memories.py:85-112` | 2 | 35, 53 | Correct |
| `allo@094ab41:allo/ir/builder.py:547-581` | 2 | 36, 68 | Correct |
| `allo@094ab41:tests/test_types.py:65-81` | 3 | 37, 68, 1257 | Correct |
| `exo@defe172:src/exo/API_scheduling.py:1696-1718` | 1 | 53 | Correct |
| `spatial-rs@eb49d8b:docs/language-spec.md:777-791` | 1 | 72 | Correct |
| `spatial-rs@eb49d8b:docs/language-spec.md:164-167` | 1 | 72 | Correct |
| `spatial-rs@eb49d8b:docs/language-spec.md:1010-1023` | 1 | 72 | Correct |
| `spatial-rs@eb49d8b:docs/language-spec.md:1076-1107` | 1 | 72 | Correct |
| `exo@defe172:src/exo/libs/memories.py:110-112` | 1 | 894 | Correct |
| `allo@094ab41:allo/ir/builder.py:564-581` | 1 | 1257 | Correct |
| `spatial@e7a8f2f:src/spatial/executor/scala/memories/ScalaTensor.scala:26-46` | 1 | 1272 | Correct |

#### Angle 5 — D-26-05-boundary-design.md

| Unique pinned anchor | Occurrences | Note lines | Result |
|---|---:|---|---|
| `spatial-rs@eb49d8b:docs/adr/0002-file-cli-host-runtime.md:142-223` | 2 | 7, 80 | Correct |
| `spatial-rs@eb49d8b:docs/adr/0002-file-cli-host-runtime.md:504-569` | 1 | 8 | Correct |
| `spatial-rs@eb49d8b:docs/adr/0002-file-cli-host-runtime.md:65-110` | 2 | 9, 76 | Correct |
| `spatial-rs@eb49d8b:docs/language-spec.md:56-175` | 2 | 10, 46 | Correct |
| `spatial-rs@eb49d8b:docs/language-spec.md:987-1067` | 1 | 11 | Correct |
| `spatial-rs@eb49d8b:crates/spatial-rs-core/src/frontend/source.rs:1-108` | 2 | 12, 86 | Correct |
| `spatial-rs@eb49d8b:crates/spatial-rs-core/src/compiler.rs:30-68` | 2 | 13, 39 | Correct |
| `spatial-rs@eb49d8b:crates/spatial-rs-core/src/compiler.rs:414-487` | 2 | 14, 39 | Correct |
| `spatial-rs@eb49d8b:crates/spatial-rs-cli/src/lib.rs:12-77` | 2 | 15, 69 | Correct |
| `calyx@d6bcdc8:calyx-py/calyx/builder.py:26-42` | 3 | 16, 47, 57 | Correct |
| `calyx@d6bcdc8:calyx-py/calyx/py_ast.py:56-150` | 2 | 17, 57 | Correct |
| `calyx@d6bcdc8:calyx-py/calyx/py_ast.py:655-679` | 2 | 18, 57 | Correct |
| `calyx@d6bcdc8:calyx/ir/src/from_ast.rs:257-265` | 2 | 19, 57 | Correct |
| `calyx@d6bcdc8:calyx/opt/src/passes/well_formed.rs:127-157` | 2 | 20, 59 | Correct |
| `allo@094ab41:allo/customize.py:1351-1408` | 2 | 21, 63 | Correct |
| `allo@094ab41:allo/ir/utils.py:136-161` | 2 | 22, 63 | Correct |
| `allo@094ab41:allo/ir/builder.py:93-114` | 2 | 23, 63 | Correct |
| `spatial-rs@eb49d8b:docs/language-spec.md:987-1028` | 1 | 37 | Correct |
| `spatial-rs@eb49d8b:docs/language-spec.md:1052-1057` | 1 | 37 | Correct |
| `calyx@d6bcdc8:calyx-py/calyx/py_ast.py:128-150` | 1 | 45 | Correct |
| `spatial-rs@eb49d8b:docs/language-spec.md:997-1028` | 1 | 49 | Correct |
| `spatial-rs@eb49d8b:crates/spatial-rs-core/src/compiler.rs:427-487` | 1 | 51 | Correct |
| `spatial-rs@eb49d8b:docs/language-spec.md:149-175` | 1 | 53 | Correct |
| `spatial-rs@eb49d8b:docs/adr/0002-file-cli-host-runtime.md:18-29` | 1 | 69 | Correct |
| `spatial-rs@eb49d8b:docs/adr/0002-file-cli-host-runtime.md:159-217` | 1 | 73 | Correct |
| `spatial-rs@eb49d8b:docs/adr/0002-file-cli-host-runtime.md:177-258` | 1 | 74 | Correct |
| `spatial-rs@eb49d8b:docs/adr/0002-file-cli-host-runtime.md:504-557` | 1 | 75 | Correct |
| `spatial-rs@eb49d8b:docs/adr/0002-file-cli-host-runtime.md:260-272` | 1 | 76 | Correct |
| `spatial-rs@eb49d8b:docs/adr/0002-file-cli-host-runtime.md:122-140` | 1 | 78 | Correct |
| `spatial-rs@eb49d8b:docs/language-spec.md:1025-1028` | 1 | 84 | Correct |
| `spatial-rs@eb49d8b:docs/language-spec.md:1052-1054` | 1 | 84 | Correct |

#### Angle 8 — D-26-08-cost.md

| Unique pinned anchor | Occurrences | Note lines | Result |
|---|---:|---|---|
| `spatial-rs@eb49d8b:docs/superpowers/plans/2026-07-07-compositional-core-inversion-roadmap.md:101-132` | 2 | 7, 30 | Correct |
| `spatial-rs@eb49d8b:docs/superpowers/plans/2026-07-07-compositional-core-inversion-roadmap.md:134-153` | 2 | 8, 34 | Correct |
| `spatial-rs@eb49d8b:crates/spatial-rs-core/src/compiler.rs:30-67` | 3 | 9, 30, 38 | Correct |
| `spatial-rs@eb49d8b:crates/spatial-rs-core/src/validate.rs:34-64` | 2 | 10, 63 | Correct |
| `spatial-rs@eb49d8b:crates/spatial-rs-core/src/oracle.rs:5-81` | 2 | 11, 32 | Correct |
| `spatial-rs@eb49d8b:crates/spatial-rs-core/src/manifest.rs:7-38` | 2 | 12, 32 | Correct |
| `spatial-rs@eb49d8b:examples/ee109/src/bin/run-vitis-validation.rs:26-81` | 2 | 13, 32 | Correct |
| `spatial-rs@eb49d8b:crates/spatial-rs-core/src/diagnostics.rs:3-23` | 2 | 14, 53 | Correct |
| `spatial-rs@eb49d8b:docs/adr/0002-file-cli-host-runtime.md:454-504` | 2 | 15, 61 | Correct |
| `exo@defe172:src/exo/frontend/pyparser.py:38-91` | 4 | 16, 49, 55, 63 | Correct |
| `allo@094ab41:allo/ir/builder.py:93-115` | 4 | 17, 49, 55, 63 | Correct |
| `spatial-rs@eb49d8b:examples/ee109/src/bin/run-vitis-validation.rs:72-97` | 1 | 57 | Correct |

#### Angle 10 — D-26-10-recommendation-matrix.md

| Unique pinned anchor | Occurrences | Note lines | Result |
|---|---:|---|---|
| `spatial-rs@eb49d8b:crates/spatial-rs-core/src/compiler.rs:30-67` | 2 | 7, 32 | Correct |
| `spatial-rs@eb49d8b:docs/superpowers/plans/2026-07-07-compositional-core-inversion-roadmap.md:101-153` | 2 | 8, 32 | Correct |
| `spatial-rs@eb49d8b:docs/language-spec.md:385-420` | 2 | 9, 51 | Correct |
| `spatial-rs@eb49d8b:docs/language-spec.md:634-718` | 2 | 10, 51 | Correct |
| `spatial-rs@eb49d8b:docs/language-spec.md:831-837` | 2 | 11, 51 | Correct |
| `spatial-rs@eb49d8b:docs/language-spec.md:987-1028` | 2 | 12, 66 | Correct |
| `spatial-rs@eb49d8b:docs/language-spec.md:1069-1115` | 2 | 13, 86 | Correct |
| `spatial-rs@eb49d8b:docs/adr/0002-file-cli-host-runtime.md:504-557` | 2 | 14, 55 | Correct |
| `spatial-rs@eb49d8b:crates/spatial-rs-cli/src/lib.rs:12-77` | 2 | 15, 55 | Correct |
| `exo@defe172:src/exo/frontend/pyparser.py:38-91` | 2 | 16, 39 | Correct |
| `exo@defe172:src/exo/frontend/boundscheck.py:818-840` | 2 | 17, 39 | Correct |
| `calyx@d6bcdc8:calyx-py/calyx/py_ast.py:56-150` | 2 | 18, 66 | Correct |
| `allo@094ab41:allo/ir/builder.py:93-114` | 2 | 19, 39 | Correct |

#### Angle 13 — D-26-13-case-for-p-e.md

| Unique pinned anchor | Occurrences | Note lines | Result |
|---|---:|---|---|
| `exo@defe172:src/exo/API.py:35-49` | 2 | 7, 40 | Correct |
| `exo@defe172:src/exo/API.py:168-173` | 2 | 8, 40 | Correct |
| `exo@defe172:src/exo/frontend/pyparser.py:37-90` | 2 | 9, 82 | Correct |
| `exo@defe172:src/exo/frontend/typecheck.py:144-154` | 2 | 10, 40 | Correct |
| `exo@defe172:src/exo/backend/LoopIR_compiler.py:323-348` | 2 | 11, 40 | Correct |
| `exo@defe172:src/exo/frontend/boundscheck.py:818-840` | 2 | 12, 50 | Correct |
| `pymtl3@c8b349f:pymtl3/passes/rtlir/behavioral/BehavioralRTLIRGenL1Pass.py:47-80` | 2 | 13, 42 | Correct |
| `pymtl3@c8b349f:pymtl3/passes/rtlir/errors.py:26-62` | 2 | 14, 42 | Correct |
| `amaranth@90449f1:amaranth/hdl/_ast.py:627-639` | 2 | 15, 80 | Correct |
| `calyx@d6bcdc8:calyx-py/calyx/py_ast.py:63-101` | 2 | 16, 82 | Correct |
| `spatial-rs@eb49d8b:crates/spatial-rs-core/src/compiler.rs:30-67` | 2 | 17, 48 | Correct |
| `spatial-rs@eb49d8b:crates/spatial-rs-core/src/validate.rs:34-64` | 2 | 18, 48 | Correct |
| `spatial-rs@eb49d8b:docs/language-spec.md:481-505` | 2 | 19, 86 | Correct |
| `spatial-rs@eb49d8b:docs/language-spec.md:682-710` | 2 | 20, 86 | Correct |
| `spatial-rs@eb49d8b:docs/language-spec.md:831-837` | 2 | 21, 80 | Correct |
| `spatial-rs@eb49d8b:docs/language-spec.md:987-1028` | 2 | 22, 82 | Correct |
| `spatial-rs@eb49d8b:docs/language-spec.md:1074-1115` | 2 | 23, 48 | Correct |

### Final snapshot

The main agent clarified angle 8 R-E wording to “unchecked-AST ingress into the same semantic passes” after the initial read. This matches angle 5; the final phrase and unchanged citation counts were rechecked. No other note changed between the recorded snapshots.

| Note | SHA-256 |
|---|---|
| D-26-01a-precedent-python-over-core.md | `c903ad6fc7924e1c0575ec429c633d5ce813274bde9070db63369e8af8186216` |
| D-26-01c-precedent-external-dsl-over-core.md | `b1fdd7db63d4e711ed48076d852642d3c6aabb7381a0a93d2bba9b1e0596d243` |
| D-26-02-student-surface-comparison.md | `1f4ee3b321ec9089236e96a3e35e09263ed9f7bc27efcefc07d3ccf2e52bdcab` |
| D-26-03-error-paths.md | `f904acd887ff2ce53c5436c46f6453e3070c145282f7f662b3a733d8ef1a7b98` |
| D-26-05-boundary-design.md | `eda6a1b8ea8aa6a59608b44f68541a3cb4e8acda7bdd665534ae4a585ebb0bab` |
| D-26-08-cost.md | `610d4eee55a3c251338b630a1e4a20dc4f173c1bea79c474ee19f014f24343b7` |
| D-26-10-recommendation-matrix.md | `9b2f868e409926118e51a1e94fc86c2b35de4245263f309595333fc5f422a5b9` |
| D-26-13-case-for-p-e.md | `f66bcdd4b22fa277164d9859e80c58adc36cd1cdecf1b66d9802d67bf963804d` |


---

## Independent Python Surface Mapping audit

Audit date: 2026-09-28. Auditor: fresh Codex audit instance. Scope: all 13 mapping entries, excluding the overview. No architecture/synthesis notes, prior conversation, Claude, or delegated audit work were used. Entries were read-only for this auditor. The coordinator changed C0 during the audit; the original error and the verified correction are both retained below.

### Result and counting rules

- **13/13 entries reviewed; 65/65 load-bearing claims independently re-derived**, five per entry below.
- Original snapshot: **290 code-citation occurrences checked; 290 resolve and are numerically in bounds; 289 support their attached claims; 1 contradicts part of its attached claim** (C0 active-tail issue, Q167). This is 240 within-entry distinct citations, 196 globally distinct citations, across 18 pinned source files.
- Corrected C0 adds one code citation: **291 current occurrences; 291 supported; 0 remaining semantic citation failures**, after verifying its replacement wording against the pinned source. Original finding is not silently erased.
- **36 URL occurrences, 15 distinct URLs**: all 15 fetched successfully and inspected; all support their associated Python claims. They resolve to six official Python documentation pages, currently identifying themselves as Python 3.14.7. These URLs are live references, not pinned historical documentation.
- Original five-claim results: **64 pass, 1 fails in part** (C0 claim 4). With Q167's observed correction: **65 pass**. “Pass—design” validates representability/requirements and honest labeling; it is not a runtime implementation claim.
- **39 per-style expressibility ratings checked**: 6 tracing `yes`, 6 `awkward`, 1 `no`; 13 builder `yes`; 13 AST `yes`. No expressibility rating is disproved within the stated subsets. **One cross-entry preservation-rating inconsistency was identified and is now closed** after focused verification of D0's designed `scope`/`order` clarification (M2 below). No unresolved rating findings remain; this is distinct from implementation evidence.
- No private personal/account identifiers, credentials, absolute local paths, or local-machine URLs were found in the 13 entry texts. Generic example identifiers and public repository-relative paths are appropriate.

Each occurrence counts once, including repetitions. For multi-source paragraphs, a citation is judged against the part it actually supports; it need not independently prove the entire paragraph. A normative specification citation proves the stated contract, not deployed compiler behavior. Implementation-status paragraphs accurately reproduce the pinned specification's status table; this audit does not claim exhaustive tests of the implementation behind that table.

The independent extractor resolved every `<repo>@<sha>:<path>:<start>-<end>` with `git rev-parse` and `git show`, then checked 1-based inclusive bounds. It compared its independently extracted citation sets and exact excerpts with the convenience inventory: no differences. All 18 files were read at the cited revision; bounds alone were never treated as behavioral proof.

Pinned revisions independently resolved and matched the manifest:

| Repository | Full revision |
|---|---|
| spatial-rs | `eb49d8bc47bea46c83a7eb26f6a244f6303eebcb` |
| calyx | `d6bcdc8707fe2f024a7b18a86523bda6f770186a` |
| allo | `094ab4133e59edabc2911cc5c16a768e11772cbc` |
| exo | `defe17283d15553ca9d6ad70b2e9f4c22ff36ce2` |
| amaranth | `90449f1e6d5abdfb8cac7519ac7b34d83a9f42b7` |

### Per-entry counts

Counts describe the original read snapshot. C0's corrected current count is noted separately.

| Entry | Code checked | Bounds correct | Semantic correct | Semantic incorrect | URL occurrences | Five claims pass/fail |
|---|---:|---:|---:|---:|---:|---:|
| 10 Controller Bodies | 20 | 20 | 20 | 0 | 4 | 5/0 |
| 20 If Expressions | 25 | 25 | 25 | 0 | 4 | 5/0 |
| 30 Assignment | 22 | 22 | 22 | 0 | 4 | 5/0 |
| 40 FSM | 22 | 22 | 22 | 0 | 2 | 5/0 |
| 50 FixPt and Size | 25 | 25 | 25 | 0 | 2 | 5/0 |
| 60 Bulk IO and Views | 18 | 18 | 18 | 0 | 2 | 5/0 |
| 70 Par and Schedules | 20 | 20 | 20 | 0 | 2 | 5/0 |
| 80 Kernel Ports and Requires | 25 | 25 | 25 | 0 | 2 | 5/0 |
| 90 Naming and Scoping | 23 | 23 | 23 | 0 | 4 | 5/0 |
| A0 Size to Int Embedding | 21 | 21 | 21 | 0 | 2 | 5/0 |
| B0 Literal Typing | 23 | 23 | 23 | 0 | 2 | 5/0 |
| C0 Fifo Deq Timing | 20 | 20 | 19 | 1 | 2 | 4/1 |
| D0 Declaration Order | 26 | 26 | 26 | 0 | 4 | 5/0 |
| **Total** | **290** | **290** | **289** | **1** | **36** | **64/1** |

Current corrected C0: 21 code occurrences, 21 bounds correct, 21 semantically supported, 0 incorrect, 5/0 claims. Current aggregate: 291/291 supported and 65/0 claims. A rating clarification does not change code-citation counts.

### Concrete issues

#### M1 / Q167 — masked-off FIFO lanes were incorrectly included in conflicts

**Original claim, C0 Assessment:** “Rule 10 treats same-FIFO parallel consume/produce as conflicting, including masked-off lanes.”

**Contradicting cited source:** `spatial-rs@eb49d8b:docs/language-spec.md:583-593`, especially line 588, adds active-lane predicates before the distinct-lane check. The related contract at lines 871–874 and 975–976 forbids inactive lanes from performing FIFO effects. Thus a disabled lane is not an executed consume/produce participant. The separate claim that active same-FIFO lane effects conflict is correct.

**Required fix:** say conflicts are checked after adding each lane's active predicate; masked-off lanes execute no FIFO effects. Keep the independent obligation to prove inactive-tail safety.

**Status:** coordinator notified this auditor of Q167 before this focused check. This auditor then independently derived the contradiction from the pinned source. The coordinator's replacement was observed and verified: “after adding each tail mask's active-lane predicate. Masked-off lanes do not execute FIFO effects,” with an added `:863-878` citation. Fixed during audit; not an independent discovery credit.

#### M2 — D0 changes the preservation-rating basis from proposed form to implemented extension

**Original claim, D0 Python forms:** “The tracing `info_preserved` list deliberately does not credit `order` until the explicit registration extension is implemented.” The shown `T.declare("row", ...)` followed by `T.declare("col", ...)` is explicitly described as the declaration sequence determining DSL order, but frontmatter lists only `size_vs_int`.

**Evidence and inconsistency:** D0's ordered-registration design is sufficient to represent the desired declaration order, subject to its proposed checker. Entries 10, 20 and 40 credit the scope/order retained by their equally unimplemented callback/region extensions while rating them `awkward` for exceeding the base tracing subset. D0 instead uses implementation existence to withhold a designed preservation property. Neither the Python binding docs nor `spatial-rs@eb49d8b:docs/language-spec.md:393-397,445-459,489-499` establishes a reason to apply a different rating basis.

**Required clarification:** choose one consistent basis. Prefer rating the displayed proposed extension: add `order` for D0's explicit declaration events, and say bare expression tracing cannot infer source binding order. Keep `awkward`, since explicit declaration registration extends the stated tracing subset. Do not claim automatic native-binding capture or implemented preservation. Credit `scope` only if explicit lexical-region ownership is included in that rated design. Alternatively rate all entries' unextended tracing consistently, but do not switch criteria only here.

**Severity:** rating/documentation consistency, not a failed declaration-order proof. No demonstrated runtime equivalence or missing semantic implementation is inferred. The coordinator was notified.

**Closure verification:** on 2026-09-28 this auditor independently re-read the revised D0 frontmatter and corresponding explanation. It now credits `scope` and `order` for the displayed designed ordered lexical-registration extension, retains `expressible: awkward`, explicitly says bare tracing preserves neither, and labels the preservation as in-principle rather than implemented. Scope is justified by the explicitly described ordered lexical region. The original finding above is retained. The ordered list of all 26 code-citation occurrences is unchanged; no unrelated checks were rerun. **M2 closed.**

### Five load-bearing claims per entry

Here `S:L-L` abbreviates the pinned `spatial-rs@eb49d8b:docs/language-spec.md:L-L`, not an unpinned worktree file.

#### 10 — Controller Bodies

1. **Pass—specification:** statement blocks and mandatory-terminal-yield value blocks are distinct; the five quoted controller/reduction productions are exact. `S:99-100,117-123,164-167` matches every shown production. `S:882-884` requires every written identity to convert exactly to zero; it is not arbitrary host arithmetic.
2. **Pass—specification:** reduce and fold differ in ordering/effect permissions. `S:905-910` permits only reads/private locals for reduce, but ordered reads/writes for fold; the example contribution is compatible with the former when its operands are initialized.
3. **Pass—specification:** memory reductions reference existing accumulator/temporary views and logically clear temporary initialization each iteration. `S:414-420,886-903` requires live, disjoint, equal-shape/type views and complete temporary writes before combining. Neither view is a new binder.
4. **Pass—design:** complete multi-statement tracing needs an explicit capture extension; builder contexts/AST helpers can represent the regions but must preserve symbolic iteration, lexical ownership, and effect order. The `awkward/yes/yes` ratings match the examples and their stated subset boundaries; Python generator/lambda facts do not prove the proposed APIs exist.
5. **Pass—precedent/status:** Calyx's `builder.py:1157-1159,1757-1766` directly constructs repeat/sequence nodes; Allo `builder.py:518-532` recognizes the named loop iterators and its test performs GEMM accumulation. They do not establish Spatial reduction legality. `S:1101-1115` marks the canonical reductions and full obligation engine Specified.

#### 20 — If Expressions

1. **Pass—specification:** conditions are Bool, value branches have matching types, and exactly one value block executes. `S:678-685,818-824` supports the distinction between source syntax and the runtime branch contract.
2. **Pass—Python/design:** native conditional syntax truth-tests and chooses an arm; a function call receives already evaluated arguments. Therefore an eager mux cannot retroactively place a dequeue in a lazy branch region. The official references and Amaranth `_ast.py:627-639` support this; explicit callbacks are correctly rated an awkward extension.
3. **Pass—precedent/design:** Amaranth `_dsl.py:331-392` captures separate statement collections through context entry/yield/exit, and its ALU uses the displayed syntax. Host work runs while building these regions; that is not execution of both hardware arms. The proposed yielded-value builder is clearly additional work.
4. **Pass—precedent/design:** Allo `builder.py:2401-2416` builds true and false operands before `arith.SelectOp`, whereas `:2419-2453` creates statement branch regions. Its pure conditional expression is not evidence of lazy effectful value blocks; the proposed source helper must lower separate regions.
5. **Pass—specification/design:** Rules 2/4/6 and 5/7/11 require path facts, joins, initialization and FIFO proofs. An omitted else joins incoming state (`S:523-527`). Current if-statement support is Narrow, canonical value-yield if is Specified (`S:1098-1099,1114-1115`). AST all-five preservation is explicitly conditional on source/token retention and a resolver.

#### 30 — Assignment

1. **Pass—specification:** mutable identifier/indexed target categories and immutable lets/inputs/constants/binders exactly match `S:773-791`; hardware mutation is distinct from source binding.
2. **Pass—specification:** target indices precede RHS evaluation, and write commits afterward; dequeue is the immediate exception (`S:831-837`). This requires an address/target proxy rather than an uninitialized target read.
3. **Pass—Python/design:** native indexed assignment reverses target/RHS consuming order, while the receiver `.at(...).write(...)` and destination-first builder arguments can represent Spatial order. A local audit witness independently obtained native `(index=2,value=1)` versus method `(index=1,value=2)` for a two-item queue. Augmented assignment has additional read/operation/write behavior.
4. **Pass—precedent:** Amaranth `_ast.py:1335-1348` constructs `Assign` and explicitly extends/truncates widths; Allo assignment tests contain the shown syntax, while `builder.py:1161-1189` can build a call RHS before targets. Neither precedent proves Spatial's exact type/effect rules.
5. **Pass—design:** all three displayed explicit forms are expressible within their rated mechanisms; builder adds DSL scope, and AST needs a custom declaration/lvalue/effect transform. Checks and current-Narrow status are not presented as an implemented general Python frontend (`S:1097,1114-1115`).

#### 40 — FSM

1. **Pass—specification:** init occurs before state binding; state is otherwise immutable, may be negative/wrapping Int, and has no v1 schedule syntax. `S:393-397,917-924` explicitly separates FSM state from nonnegative controller indices.
2. **Pass—specification/design:** init/condition/step are observational; condition, body, then step execute in order; step observes body writes (`S:839-843,917-923`). Capturing runtime reads in distinct regions is necessary; host snapshots would be wrong.
3. **Pass—specification:** Rule 9 only admits its strict affine, exact-positive-step, no-wrap induction pattern. Other shapes provide limited facts/no post-FSM coverage rather than being categorically forbidden (`S:568-582`). The simple `0,<4,+1` fragment meets the admitted pattern with initialized/writable inputs as stated.
4. **Pass—design:** native while cannot become this symbolic FSM solely through value overloads. The callback extension is awkward, builder regions are expressible, and AST's final-state-assignment recognition is an explicit additional restriction rather than Python mutation semantics.
5. **Pass—precedent/status:** Amaranth `_dsl.py:450-505` allocates named states and checks undefined/duplicate labels; Allo `builder.py:2455-2490` builds while regions. These are partial precedents only. `S:1108-1115` supports the stated Narrow/Specified separation.

#### 50 — FixPt and Size

1. **Pass—specification:** Size is checked u64 compile-time arithmetic, with positive use-site requirements and a checked runtime embedding (`S:597-605`). Unbounded host integers cannot themselves discharge that contract.
2. **Pass—specification:** fixed parameters and total-width limits, sign-bit convention, exact-rational floor ingress, rejection versus arithmetic wrap, and explicit policy fields match `S:624-660`. Format/staging semantics are properly separated from spelling conventions.
3. **Pass—design:** explicit decimal-token strings and literal/Size nodes can preserve the rated numeric distinctions. Capturing only a Python float or `ast.Constant.value` loses source spelling; a local witness retained `0.7500` only through the original source segment. All-five AST preservation is a stated source-backed design.
4. **Pass—precedent:** Allo `types.py:215-255` uses total bits/fraction bits, requiring `bits=I+F`; its `test_types.py:287-298` expressly contains the unresolved fixed-lowering comment. Calyx `builder.py:614-650` constructs fixed primitives but proves no Spatial ingress/Size checker.
5. **Pass—status/design:** exact const/type rules and Rules 1/4 remain checker obligations in either proposed ownership model. `S:1078-1089,1114-1115` supports the stated Narrow const path and Specified E0506/full fixed/policy/obligation boundaries.

#### 60 — Bulk IO and Views

1. **Pass—specification:** scalar selectors drop axes, range selectors retain axes, exact selector count is required, and regular transfer element type/rank/extents must agree (`S:928-934,946-949`). The rank-2 snippets supply both axes explicitly.
2. **Pass—specification:** endpoint legality differs by ordinary/FIFO/LineBuffer operation. Regular transfers snapshot, FIFO transfers stream, and LineBuffer row loads shift after a source snapshot (`S:954-969`); a shape-only Python slice is insufficient.
3. **Pass—design:** destination-receiver calls and destination-first builder arguments respect destination-before-source capture (`S:963-969`). Custom subscription rules can create views rather than host array copies; AST must reject unsupported omissions, steps and broadcasting.
4. **Pass—specification/design:** per-axis positive factors, non-tail divisibility, independent tail masks and inactive-effect exclusion match `S:971-977`. Bounds, initialization, FIFO and lane proofs remain required in both proposed checker ownerships.
5. **Pass—precedent/status:** Exo `test_codegen.py:135-144,757-769` demonstrates aliasing windows, nested slicing, scalar-axis selection and omitted endpoints. It does not establish DMA or Spatial legality. `S:1109-1115` supports the narrower current implementation boundary.

#### 70 — Par and Schedules

1. **Pass—specification:** par groups ascending logical iterations; non-tail requires divisibility, tail masks the final partial group, and scalar reduction has no tail form (`S:868-878`). A lane request does not itself prove resource feasibility.
2. **Pass—specification:** Auto promises no overlap, Seq requires ordered groups, Pipe requests positive group II and may receive a backend failure/warning without changing functionality (`S:862-878`). The surface placement is syntax policy.
3. **Pass—specification:** Rule 8's dependence/monotonicity conditions and stateful Seq/Auto fallback are distinct from Pipe, which lacks that fallback (`S:533-567`). Rules 3/4/10 provide domain/divisibility/distinct-lane checks before scheduling.
4. **Pass—design:** a host for loop consumes an iterator; arbitrary controller bodies need the stated explicit body mechanism or AST capture. `awkward/yes/yes` matches the restricted tracing/body-builder/context/AST forms, and the text does not mistake a Python with-suite for a checked scope.
5. **Pass—precedent/status:** Allo `test_schedule_compute.py:391-431` asserts pipeline/unroll attributes, not measured timing; Calyx `builder.py:1739-1766` composes arms rather than iteration lanes. `S:1101-1105,1114-1115` supports current-Narrow par and Specified schedule/tail/proof status.

#### 80 — Kernel Ports and Requires

1. **Pass—specification:** one kernel, ordered port blocks, read/write directions and earlier-scalar runtime-dimension resolution match `S:58-75,201-209,724-725`. Runtime dimension arithmetic is not admitted by the bare-name exception.
2. **Pass—specification:** requires is observational Bool with the exact restricted normalized node set, and reads only constants/scalar inputs (`S:727-736`). Python syntax acceptance cannot enlarge this set.
3. **Pass—specification/design:** run-data shape/scalar validation precedes ordered requirement evaluation; false predicates yield E0607 before accelerator state creation. Static wrong-binding/requirement-type errors remain IR-check errors (`S:727-751`). The entry explicitly distinguishes these loci.
4. **Pass—Python/design:** chained comparisons/Boolean control can consume symbolic truth before a predicate graph is complete. Amaranth's truth guard is concrete; explicit separate requirements or a closed AST transform avoid that path. The local audit witness also raised during a chained symbolic comparison.
5. **Pass—precedent/status:** Calyx named-width ports and Exo dependent annotations/assertion are real inspected syntax, not evidence of Spatial nonaliasing or host checks. `S:1074-1082,1114-1115` supports the implementation boundary; `awkward/yes/yes` correctly distinguishes signature metadata from expression tracing.

#### 90 — Naming and Scoping

1. **Pass—specification:** one value namespace, child scopes, no duplicate/ancestor shadowing, sibling reuse and after-initializer visibility match `S:385-397`; ASCII/reserved-word claims match `S:188-218`.
2. **Pass—specification:** local allocations are per block/iteration, while outer memory is shared and requires dependence proof (`S:399-420`). This is stronger than attaching display names to Python objects.
3. **Pass—Python/style:** plain local rebinding has no overloaded object hook, and if/for/with suites do not provide the required lexical declarations. Complete capture is therefore `no` within the stated unextended tracing subset, with silent rebinding as a representative failure; it is not a claim about every possible Python hybrid.
4. **Pass—design:** explicit strings, symbol/region handles, delayed insertion and escaped-handle checks can represent the builder policy; an AST resolver can replace host name lookup. Neither shown form claims that these checks already exist. Scope/order preservation is conditional on that implementation.
5. **Pass—precedent:** Amaranth `tracer.py:16-69,72-77` infers names and file/line locations; Exo `pyparser.py:678-682,1160-1165,1215-1252` uses distinct environments/Sym creation, but permits policies different from Spatial. The cited Exo prelude excludes the standalone underscore name; no policy equivalence is claimed.

#### A0 — Size to Int Embedding

1. **Pass—specification/arithmetic:** `2147483648` lies in u64 and exceeds signed-32 maximum, so the shown Size succeeds statically but its proposed runtime use must fail E0506 (`S:597-605`). This was independently recomputed, not inferred from the proposed API running.
2. **Pass—specification:** one named constant remains Size in static positions and synthesizes Int in runtime expressions (`S:712-718`). The TILE sample therefore illustrates two separate typed uses, and its missing surrounding initialization is explicitly acknowledged.
3. **Pass—specification:** an outer FixPt expectation does not convert a named Size into a decimal/literal operand; the named use synthesizes Int, and mixed nonliteral numeric types have no implicit conversion (`S:643-648,666-718`).
4. **Pass—design/specification:** explicit embedding nodes or AST insertion can preserve origin/use-site information. Unbounded proof arithmetic, wrapping runtime Int and widened valid loop progression are separate domains (`S:445-458,470-480,854-860`); host conversion is insufficient.
5. **Pass—precedent/status:** Exo `typecheck.py:38-72,501-538` distinguishes sizing/indexing expressions and rejects nonconstant indexing multiplication. It does not establish u64-to-i32 E0506. `S:1078-1080` explicitly says that embedding is still open/Specified.

#### B0 — Literal Typing

1. **Pass—specification:** type checking is bidirectional; default integers synthesize Int and uncontextual decimals reject (`S:682-705`). Explicit token trees and AST-before-execution are suitable proposed representations.
2. **Pass—specification:** check mode propagates the expected type to both sides of literal-only arithmetic; synthesize mode uses the nonliteral operand's type where prescribed (`S:695-705`). Wrapping a final host result cannot reconstruct the original tree.
3. **Pass—independent arithmetic:** with one fraction bit, floor ingress maps 0.75 to 0.5, then multiplying by exactly representable 2 gives 1. Host-first 0.75×2 gives 1.5, which remains 1.5 on ingress. Recomputed with exact rational arithmetic; this is a specification witness, not a Spatial/Allo run (`S:634-648,695-705`).
4. **Pass—specification:** signed-literal handling admits -2147483648 as a whole value, rejects negative unsigned literals, and distinguishes nonliteral wrapping negation/mixed-type rejection (`S:643-648,687-720`). These are actual extra frontend obligations.
5. **Pass—precedent/design:** Allo `infer.py:176-189` initially assigns host constant categories int32/float32; Amaranth constants normalize to width; Calyx uses explicit width. None demonstrates Spatial ingress/check-mode parity. All-three `yes` and AST all-five remain designed strict-form ratings with explicit wrappers/source retention.

#### C0 — FIFO Dequeue Timing

1. **Pass—specification:** dequeue consumes during primary evaluation, while enclosing enqueue/write commits later (`S:831-837`); hardware backpressure/blocking timing is Deferred (`S:793-799`). Source sequencing does not claim a cycle protocol.
2. **Pass—Python/design:** native indexed assignment consumes RHS before its target, but the proposed method and destination-first argument forms can preserve Spatial order. Independent audit witness confirms the swapped queue-item roles; an AST frontend must deliberately lower indices first.
3. **Pass—specification/design:** empty `q.enq(q.deq())` fails at the dequeue; a full nonempty queue consumes before the append, so net-count cancellation is unsound for the empty case. This follows by applying immediate consumption to `S:528-532,793-799,831-837`. The entry labels ordered intra-statement proof handling as required design, not implemented behavior.
4. **Original fail in part; corrected pass—specification:** same-FIFO active lanes conflict, but masked-off lanes must be excluded by active predicates and execute no effects (`S:583-588,871-874,975-976`). See M1/Q167. The live replacement matches these rules.
5. **Pass—precedent/status:** Allo stream `put/get` appears in source plus generated-code assertions and a separate simulator test (`test_df_unit.py:13-31,42-62`), but those tests were not run for the entry and prove no Spatial occupancy/effect contract. Canonical Fifo spelling and general semantics remain Specified while current enq/deq representation is Narrow (`S:1093-1095,1114-1115`).

#### D0 — Declaration Order

1. **Pass—specification:** Rule 1 sorts affine terms by declaration ID; Rule 4 substitutes the greatest-ID symbol using earlier-ID bounds (`S:445-459,481-505`). Ordering therefore participates in the fixed proof calculus.
2. **Pass—specification:** only greatest-ID coefficient ±1 admits oriented bounds/exact substitutions; other comparisons remain direct facts (`S:496-499`). A stronger solver cannot widen acceptance (`S:424-443,504-505`).
3. **Pass—independent derivation:** given id(row)<id(col), `row<=col` has greatest symbol col and can orient its lower bound through row, not an upper bound of row through later col. The entry correctly avoids claiming a demonstrated acceptance difference: direct facts and alternate paths remain available (`S:487-505`).
4. **Pass—design, rating clarification now closed:** allocations/aliases/rebinding do not reveal every source declaration; explicit ordered lexical registration or AST traversal can represent the intended IDs. The original D0 implementation-threshold inconsistency is preserved in M2. The revised displayed-extension rating credits scope/order in principle, excludes bare tracing, and retains `awkward/yes/yes`, consistently with the other designed ratings.
5. **Pass—precedent/design:** Calyx appends port/control declarations in order; Exo `Sym` uses a class-wide increasing ID but compares `(name,id)` (`prelude.py:21-42`), so it is not evidence of source-local normative ordinal equivalence. AST all-five is explicitly source/token/resolver-backed design, and no proof-trace parity experiment is claimed.

### Per-style preservation and evidence discipline

Every entry's three examples and frontmatter were compared, including representative error loci. A locus is consistently described as a representative first report for the proposed form, not a universal phase for every misuse. The different runtime E0607 case in 80, silent host rebinding in 90 and early symbolic truth errors are adequately distinguished.

The 13 AST all-five lists consistently require unexecuted source, original token retention, lexical/type resolution and source mapping through lowering. Python AST locations alone are not represented as guaranteeing literal provenance, Size typing, scope policy, effect order or full spans in generated IR. End locations can be absent on constructed/transformed AST nodes; retaining/reconstructing them remains part of each proposed implementation.

Tracing `yes` entries use explicit methods, views or literal/Size trees; the six awkward cases need callback/controller/signature/declaration machinery beyond the stated expression-only core. Scope is withheld for bare object tracing. Builder `yes` means an explicit region/declaration/statement API can express the contract; Python context syntax by itself does not validate lifetime or type/effect obligations. D0's inconsistent implementation threshold was the one preservation-rating clarification identified; the focused follow-up verified its correction without changing the original finding or other audit results.

The inspected precedent code/tests were not executed. Small independent host-language/rational-arithmetic witnesses were run solely for assignment order, symbolic chained comparisons, scope visibility, token loss, numeric boundary and the B0 calculation; their results are in `audit-mapping-witnesses.json`. They are not performance, hardware, or exact Spatial-prototype parity measurements.

### URL-by-URL verification

All were fetched 2026-09-28; none was unavailable. The following terse support findings concern only the Python mechanisms, not DSL implementations.

| Distinct URL | Support finding |
|---|---|
| [Yield expressions](https://docs.python.org/3/reference/expressions.html#yield-expressions) | Generator suspension semantics; supports 10. |
| [Lambdas](https://docs.python.org/3/reference/expressions.html#lambda) | Expression bodies cannot contain statements; supports 10. |
| [AST nodes/locations](https://docs.python.org/3/library/ast.html#ast.AST) | AST fields/locations exist; end positions optional; exact decimal tokens require retained source. |
| [Calls](https://docs.python.org/3/reference/expressions.html#calls) | Arguments evaluate before invocation; supports eager-capture caveats. |
| [Conditional expressions](https://docs.python.org/3/reference/expressions.html#conditional-expressions) | Condition chooses one evaluated arm. |
| [Truth conversion](https://docs.python.org/3/reference/datamodel.html#object.__bool__) | Truth conversion requires a Boolean result; default truthiness exists without guards. |
| [Assignment](https://docs.python.org/3/reference/simple_stmts.html#assignment-statements) | Name rebinding versus item/attribute assignment are distinct mechanisms. |
| [Augmented assignment](https://docs.python.org/3/reference/simple_stmts.html#augmented-assignment-statements) | Target-first evaluation includes read/operation/write. |
| [Evaluation order](https://docs.python.org/3/reference/expressions.html#evaluation-order) | Expressions evaluate left-to-right; ordinary assignment evaluates RHS first. |
| [Numeric type hierarchy](https://docs.python.org/3/reference/datamodel.html#the-standard-type-hierarchy) | Integers have unbounded precision; floats are machine-level approximations. |
| [Subscriptions](https://docs.python.org/3/reference/expressions.html#subscriptions) | Subscription/slice descriptors reach user-defined methods. |
| [For statements](https://docs.python.org/3/reference/compound_stmts.html#the-for-statement) | Native iteration executes the suite for host iterator items. |
| [Comparisons](https://docs.python.org/3/reference/expressions.html#comparisons) | Chaining includes short-circuit truth control. |
| [Naming and binding](https://docs.python.org/3/reference/executionmodel.html#naming-and-binding) | Bindings belong to enclosing code blocks, not DSL child regions. |
| [Name resolution](https://docs.python.org/3/reference/executionmodel.html#resolution-of-names) | Function-wide locals and NameError/UnboundLocalError support the stated caveats. |

Independent scratch evidence: `audit-mapping-independent-citations.json`, `audit-mapping-independent-urls.json`, `audit-mapping-independent-external-excerpts.txt`, `audit-mapping-spec-numbered.txt`, and `audit-mapping-witnesses.json`. No entry corrections were made by this auditor.


---

## D-26 final synthesis review

Reviewed D-26, D-26-02, D-26-03, D-26-08, D-26-10, D-26-13, and the Python Mapping Overview. This was a fresh Codex-only synthesis review; no vault edits, delegation, or duplicate full citation audit were performed.

**Result: no substantive issue found in the requested review categories.**

- **Frozen protocol:** The current D-26 prefix before `## Research findings` is byte-identical to `git show ae2f3fd:'20 - Research Notes/50 - Decision Records/D-26.md'`: 5,011 bytes; SHA-256 `e6f57ab56559c4f95414c7681046caf539ba5a707b7658cfaf2e80b8b6a5cfda`.
- **Weights and reversals:** D-26:132, 166–186 and D-26-10:68–86 preserve blank personalized weights, do not invent an equal-weight winner, distinguish the first-rating mapping result from implementation, and leave parity and k=10 unmeasured. Neither missing evidence nor failure to trigger the conjunction is presented as a Rust victory. The row-5 mistake-list conflict is disclosed without rewriting the frozen list.
- **Evidence strength:** D-26:122–130 accurately limits concept counts to a constructed inventory, lab ports to unexecuted designs, and diagnostic findings to mixed/analogous results. It retains external parser failures and the Exo counterexample as counterevidence. The general Rust compiler is not represented as already completed or paid for.
- **Axes and availability:** D-26:138–172 separates core, surface, and integration. Current I0 text checking is distinguished from proposed JSON, wheels, bindings, notebooks, and AST ingress. No designed Python frontend, source-preservation guarantee, or release/catalog obligation is portrayed as currently delivered.
- **Strongest P-E case:** D-26:192–198 answers semantic-code ownership, genuine Python compiler capability, student familiarity despite higher raw counts, and the incomplete Rust starting point. It explicitly concedes that a wrapper does not transfer Rust semantic maintenance to Python TAs and that confirmed staffing priorities can justify P-E. The recommendation is a provisional continuity judgment pending David's decision, not an empirical or educational winner.

**Optional wording clarification, not a substantive blocker:** D-26-08:43 says R-E needs “checked ingress into the same semantic passes,” while D-26:126 and D-26-10:66 expressly prefer unchecked surface-AST ingress. The cost-table phrase can mean validated transport/schema ingress, so it does not overturn the synthesis. Replacing it with “unchecked surface-AST ingress into the shared semantic passes,” or explicitly naming schema validation, would prevent readers from mistaking it for semantically checked-IR ingress.

No change to the recommendation or frozen pre-registration is warranted by this synthesis review alone.



---

## Main-session D-26 spot checks, 2026-09-28

Pinned source read directly or through git show; URL text fetched from official Python docs. Counts below are substantive claims, not code-range existence checks. Each mapping has five load-bearing claims checked. The later fresh audit is additional and is not a second independent mapping rating.

| Entry | Five claims checked | Initial result |
|---|---|---|
| 10 Controllers | Spec value/reduction forms and region effects; zero identity and initialized memfold; Calyx static_repeat/seq; Allo range/grid/reduction dispatch; symbolic truth rejection in Amaranth | 5/5 |
| 20 If | Spec selected-only value branch; Amaranth Mux value construction; Amaranth contexts collect distinct branches; Allo IfExp builds both operands then SelectOp; Python conditional/call evaluation | 5/5 |
| 30 Assignment | Spec writable lvalues/immutable bindings; Spatial target-before-RHS order versus Python assignment; Amaranth eq width behavior; Allo transformed assignment syntax; Allo call RHS built before target loop | 5/5 |
| 40 FSM | Spec state/init/body/step lifetime and order; Rule9 strict-form induction versus fallback; Amaranth named-state construction and duplicate/undefined checks; Allo scf.WhileOp capture; symbolic truth rejection | 5/5 |
| 50 FixPt/Size | Checked Size embedding and width semantics; Fixed-point ingress/normalization; Allo Fixed total-bit API; Allo comparison test and lowering FIXME; AST positions are not literal token retention | 5/5 |
| 60 Views | Spec selector/rank rules; snapshot versus FIFO transfer; Python passes slices to subscription; Exo window callee syntax; Exo nested views and omitted endpoints | 5/5 |
| 70 Par/schedules | Canonical Scale par syntax; divisibility/tail/II specification; native Python for creates a host iterator; Calyx par control composition; Allo schedule attributes test | 5/5 |
| 80 Ports/requires | Requires restricted AST and invocation order; shape earlier-name/length contract; Calyx explicit named ports; Exo dependent shapes/asserts; symbolic truth/chained comparison boundary | 5/5 |
| 90 Naming | Spatial ancestor/sibling/initializer rules; Python assignment and block binding; Amaranth naming bytecode/line locator; Exo separate branch and loop environments; Exo symbol name policy | 5/5 |
| A0 Size→Int | u64 static versus i32 runtime bound; named Size synthesizes Int regardless of FixPt expectation; proof/runtime/progression domains differ; E0506 explicitly unimplemented; Exo size/index categories and nonaffine multiplication rejection | 5/5 |
| B0 Literals | Expected-type propagation; 0.75*2 at one fractional bit gives 1 under specified per-literal ingress; exact source token lost by host float; Allo int32/float32 constant defaults; Amaranth masks shaped constants rather than rejecting ingress | 5/5 |
| C0 FIFO | Immediate dequeue versus statement commit; target/RHS ordering; empty q.enq(q.deq()) cannot be legalized by net zero; Allo stream API/testing scope; Rule10 active-tail predicate | 4/5, masked-off-lanes clause incorrect; corrected and filed Q167; now 5/5 |
| D0 Declaration IDs | Rule1 declaration-order normalization; Rule4 greatest-ID/earlier-ID restriction; row<=col orientation example; Calyx append order; Exo counter identity and name-then-ID comparison | 5/5 |

Mapping total: 65 checked, 64 correct initially, 1 corrected (Q167), 65 supported after correction. No entry had two substantive failures at this stage.

Angle3 five checks: (1) reran all three canonical labs: E0002 seq/init/FixPt barriers; (2) reran external LUT and requires repair versus Exo unbounded/bounded pair; (3) reran tile failure/divisible controls and Exo uninitialized frontend acceptance; (4) opened Allo Int/Fixed cast map547–581; (5) opened Scala CompilerSanityChecks54–65 exact host-transfer message. 5/5 supported; selected raw recheck output saved in main-error-recheck.json. Also reconfirmed M5 accepted and normative DRAM legality; no erroneous rejection claim.

Angle8 five checks: compiler parse/const/HIR/classifier pipeline; roadmap Phase1 interpreter39 oracle versus separate Phase2 backend; validate.rs validates adapter shapes rather than general calculus; Exo/Allo source-location/frontend mechanisms and physical line counts; diagnostic structure plus ADR invocation/backend distinction. 5/5 supported as work decomposition, not timed cost evidence.

Angle2 five checks: all three complete Scala originals exactly match pinned git content; scalar fixture has nested Fold; GEMM kk/mm/nn/product memfold ordering and lane2/16 requests preserved in designed forms; normative initialized/active equal-view temp contract; collective and per-lab concept counts recomputed under the explicit inventory. 5/5 supported. Nine Python snippets also pass ast.parse only, not execution or semantic equivalence. .buffer and numerical/scheduling parity explicitly unverified.

Angle5 five checks: current compiler stage/test E0506 use+definition labels; SourceFile UTF8 span/one-based column behavior; Calyx stack locations and sourceinfo retention; Allo adjusted line origins and file/unknown MLIR locations; ADR run/diagnostic/host-child envelopes versus actual check-only CLI. 5/5 supported.

Angle10 five checks: current classifier versus Phase1 roadmap; AST ratings and designed all-five limitations; same current diagnostic/canonical gap versus Exo bounded control; ADR versus implemented integration; fixed pre-registration blank weights/k10/conjunctive reversal and deferred study availability. 5/5 supported; judgments not numeric utilities.

Angle13 five checks: Exo parser/checker and Python C emission; PyMTL RTLIR/source-labelled error implementation; official PyMTL translation subset; exact source/spec facts about adapter validator and full calculus status; prior run record for Exo table-bound and uninitialized outcomes. 5/5 supported; staffing and familiarity remain stipulated assumptions, not measured facts.


---

## Main-session Wave 1 checks

Angle1a: Exo host metaprogramming tests11–45; Allo customize inference/build; Calyx builder error construction; PyMTL source-labelled errors26–62; Exo typecheck296–324 with paired tests189–214. Five of five supported.

Angle1c: Dahlia Compiler.scala156–189 pass order; BoundsCheck.scala55–84 warning/rejection distinction; Calyx position.rs17–40,203–230 spans/rendering; Dahlia Calyx Ast.scala14–83 line metadata; fetched official maturin bin-binding installation documentation. Five of five supported. Structural/citation-format fixes were mechanical and recorded in the progress log.
