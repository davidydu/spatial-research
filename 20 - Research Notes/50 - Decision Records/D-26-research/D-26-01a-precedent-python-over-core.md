---
type: "research"
decision: "D-26"
angle: "1a"
discriminates: integration-depth
sources:
  - "allo@094ab41:allo/customize.py:1351-1408"
  - "allo@094ab41:allo/customize.py:176-197"
  - "allo@094ab41:allo/ir/utils.py:136-161"
  - "allo@094ab41:mlir/lib/Bindings/AlloTypes.cpp:21-54"
  - "allo@094ab41:allo/logging.py:10-46"
  - "allo@094ab41:tests/test_traceback.py:15-88"
  - "allo@094ab41:setup.py:99-112"
  - "https://github.com/cornell-zhang/allo-tutorials (accessed 2026-09-28)"
  - "exo@defe172:src/exo/API.py:35-49"
  - "exo@defe172:src/exo/API.py:168-173"
  - "exo@defe172:src/exo/frontend/pyparser.py:37-90"
  - "exo@defe172:src/exo/frontend/typecheck.py:144-154"
  - "exo@defe172:src/exo/frontend/typecheck.py:296-324"
  - "exo@defe172:src/exo/backend/LoopIR_compiler.py:323-348"
  - "exo@defe172:tests/test_typecheck.py:189-214"
  - "exo@defe172:tests/test_metaprogramming.py:11-45"
  - "https://exo-lang.dev/ (accessed 2026-09-28)"
  - "https://exo-lang.dev/tutorial.html (accessed 2026-09-28)"
  - "calyx@d6bcdc8:calyx-py/calyx/py_ast.py:21-27"
  - "calyx@d6bcdc8:calyx-py/calyx/py_ast.py:63-101"
  - "calyx@d6bcdc8:calyx-py/calyx/py_ast.py:134-150"
  - "calyx@d6bcdc8:calyx-py/calyx/builder.py:258-267"
  - "calyx@d6bcdc8:calyx-py/calyx/builder.py:1678-1683"
  - "calyx@d6bcdc8:calyx-py/calyx/builder.py:1728-1732"
  - "calyx@d6bcdc8:src/main.rs:79-106"
  - "calyx@d6bcdc8:calyx/frontend/src/parser.rs:78-102"
  - "calyx@d6bcdc8:calyx/frontend/src/attributes.rs:81-84"
  - "calyx@d6bcdc8:calyx/utils/src/errors.rs:29-55"
  - "calyx@d6bcdc8:calyx/opt/src/passes/well_formed.rs:324-351"
  - "calyx@d6bcdc8:runt.toml:214-240"
  - "calyx@d6bcdc8:calyx-py/test/numeric_types.py:79-101"
  - "https://docs.calyxir.org/builder/walkthrough.html (accessed 2026-09-28)"
  - "https://docs.calyxir.org/tutorial/frontend-tut.html (accessed 2026-09-28)"
  - "https://docs.calyxir.org/contributors.html (accessed 2026-09-28)"
  - "pymtl3@c8b349f:pymtl3/dsl/ComponentLevel2.py:102-111"
  - "pymtl3@c8b349f:pymtl3/passes/rtlir/behavioral/BehavioralRTLIRGenL1Pass.py:47-80"
  - "pymtl3@c8b349f:pymtl3/passes/rtlir/behavioral/BehavioralRTLIRGenL1Pass.py:470-477"
  - "pymtl3@c8b349f:pymtl3/passes/rtlir/errors.py:26-62"
  - "pymtl3@c8b349f:pymtl3/passes/rtlir/behavioral/test/BehavioralRTLIRL1Pass_test.py:302-314"
  - "pymtl3@c8b349f:pymtl3/passes/rtlir/behavioral/test/BehavioralRTLIRL1Pass_test.py:348-354"
  - "pymtl3@c8b349f:pymtl3/passes/rtlir/util/test_utility.py:18-33"
  - "pymtl3@c8b349f:pymtl3/passes/backends/verilog/import_/VerilogVerilatorImportPass.py:371-430"
  - "pymtl3@c8b349f:pymtl3/passes/backends/verilog/import_/verilator_wrapper_py_template.py:29-58"
  - "pymtl3@c8b349f:setup.py:43-51"
  - "https://pymtl.github.io/ (accessed 2026-09-28)"
  - "https://pymtl3.readthedocs.io/en/latest/ref/passes-translation-intro.html (accessed 2026-09-28)"
  - "https://www.csl.cornell.edu/~cbatten/pdfs/batten-pymtl3-nvidia2023.pdf (accessed 2026-09-28), slide 26, PDF page 27"
verified: ["2026-09-28"]
status: draft
---
## Scope

This note examines four precedents at the supplied commits, using source inspection and official public documentation accessed on 2026-09-28. No compiler, simulation, or test suite was executed; quoted diagnostics are **source-inspected message bodies or test expectations**, not observed terminal output. Primary discrimination is integration depth: what crosses the implementation boundary and who owns diagnostics. The comparison does not measure Rust versus Python performance, staffing effort, or student outcomes. My leaning is toward an explicit IR contract with tested source provenance; the evidence does not select a core language.

## Findings

| precedent | boundary artifact | style | error locus | teaching use (cited) | maintenance notes |
|---|---|---|---|---|---|
| Allo | [precedent-measured] Typed MLIR objects through native bindings, after Python AST inference (`allo@094ab41:allo/customize.py:1351-1408`; `allo@094ab41:mlir/lib/Bindings/AlloTypes.cpp:21-54`). | [precedent-measured] AST transformation plus a Python scheduling/builder API (`allo@094ab41:allo/customize.py:176-197`). | [precedent-measured] Python inference/build failures receive a source panel; schedule operations address IR handles (same two citations). | [precedent-measured] Maintainer catalogue documents a Georgia Tech ECE 8893 guest lecture, March 11, 2025 ([catalogue](https://github.com/cornell-zhang/allo-tutorials), accessed 2026-09-28). | [precedent-measured] Package credits “Allo Community”; native extension packaging is explicit (`allo@094ab41:setup.py:99-112`). |
| Exo | [precedent-measured] Python AST → UAST → typed LoopIR within Python; generated C/header text leaves that compiler (`exo@defe172:src/exo/API.py:35-49`; `exo@defe172:src/exo/API.py:168-173`; `exo@defe172:src/exo/backend/LoopIR_compiler.py:323-348`). | [precedent-measured] AST transformation, scheduling API, explicit host-code/quotation hybrid (`exo@defe172:tests/test_metaprogramming.py:11-45`). | [precedent-measured] Python type checker aggregates source-labelled errors (`exo@defe172:src/exo/frontend/typecheck.py:144-154`). | [judgment] Course adoption remains unverified; the opened [official case-study tutorial](https://exo-lang.dev/tutorial.html) establishes a tutorial only (accessed 2026-09-28). | [precedent-measured] Project identifies core developers at MIT and requests user feedback ([project site](https://exo-lang.dev/), accessed 2026-09-28). |
| calyx-py / Calyx | [precedent-measured] Python-built Calyx AST serializes to Calyx text; Rust parses and constructs its own IR (`calyx@d6bcdc8:calyx-py/calyx/py_ast.py:134-150`; `calyx@d6bcdc8:src/main.rs:79-106`). | [precedent-measured] Builder/context-manager API with assignment syntax, executing ordinary Python ([walkthrough](https://docs.calyxir.org/builder/walkthrough.html), accessed 2026-09-28). | [precedent-measured] Python builder exceptions precede Rust structural checks; Rust messages can name components/groups (`calyx@d6bcdc8:calyx-py/calyx/builder.py:258-267`; `calyx@d6bcdc8:calyx/opt/src/passes/well_formed.rs:324-351`). | [judgment] Course adoption remains unverified; maintainer [frontend tutorial](https://docs.calyxir.org/tutorial/frontend-tut.html) demonstrates compiler construction, not a documented course deployment (accessed 2026-09-28). | [precedent-measured] Calyx’s published team includes Adrian Sampson among current contributors ([list](https://docs.calyxir.org/contributors.html), accessed 2026-09-28). |
| PyMTL3 | [precedent-measured] Python block AST → Python RTLIR; optional Verilog/C++ simulator boundary is separate (`pymtl3@c8b349f:pymtl3/passes/rtlir/behavioral/BehavioralRTLIRGenL1Pass.py:47-80`; `pymtl3@c8b349f:pymtl3/passes/backends/verilog/import_/VerilogVerilatorImportPass.py:371-430`). | [precedent-measured] Python component elaboration/operator syntax plus AST-transformed update blocks ([quick start](https://pymtl.github.io/), accessed 2026-09-28; preceding RTLIR citation). | [precedent-measured] Python RTLIR errors format original filename, line, column, and caret (`pymtl3@c8b349f:pymtl3/passes/rtlir/errors.py:26-62`). | [precedent-measured] Maintainer reports architecture/chip-design courses using PyMTL for verification and PyMTL or Verilog for RTL ([2023 talk](https://www.csl.cornell.edu/~cbatten/pdfs/batten-pymtl3-nvidia2023.pdf), slide 26, accessed 2026-09-28). | [precedent-measured] Package identifies Batten Research Group (`pymtl3@c8b349f:setup.py:43-51`). |

[precedent-measured] **Allo’s boundary is substantial, not just Python syntax over a black box.** Python retrieves source, adjusts AST line numbers, performs type inference, and constructs MLIR; native bindings expose MLIR types (`allo@094ab41:allo/ir/utils.py:136-161`; `allo@094ab41:allo/customize.py:1351-1408`; `allo@094ab41:mlir/lib/Bindings/AlloTypes.cpp:21-54`). [precedent-measured] Two source-inspected expectations are “Unsupported type `Undefined`” and “Unsupported type `BadType`”; subprocess tests assert `Line: 5` and `Line: 6`, respectively, including the offending source (`allo@094ab41:tests/test_traceback.py:15-88`). [precedent-measured] The inspected implementation prints a traceback and exits on inference/build exceptions; its presentation reconstructs code with `ast.unparse`, searches statement text, and warns when matching fails (`allo@094ab41:allo/customize.py:1369-1408`; `allo@094ab41:allo/logging.py:10-46`). [judgment] Those mechanisms make notebook recovery and exact source fidelity explicit engineering obligations, not benefits obtained automatically from embedding (same citations).

[precedent-measured] **Exo is not evidence of a compiled compiler core.** Its inspected parsing, type checking, and C emission are Python; C is generated output (`exo@defe172:src/exo/API.py:35-49`; `exo@defe172:src/exo/API.py:168-173`; `exo@defe172:src/exo/backend/LoopIR_compiler.py:323-348`). [precedent-measured] The pinned version also contradicts a blanket “forbids host metaprogramming” characterization: golden tests use `with python`, `with exo`, host conditionals, and unrolling (`exo@defe172:tests/test_metaprogramming.py:11-45`). [precedent-measured] Two source-inspected message bodies are “expected a bool expression” and “expected loop bound to be indexable.”; corresponding negative tests match their text (`exo@defe172:src/exo/frontend/typecheck.py:296-324`; `exo@defe172:tests/test_typecheck.py:189-214`). [precedent-measured] Locations derive from original filename and AST line/column offsets and are attached to aggregated `TypeError` messages (`exo@defe172:src/exo/frontend/pyparser.py:37-90`; `exo@defe172:src/exo/frontend/typecheck.py:144-154`).

[precedent-measured] **Calyx supplies the clearest Python-over-Rust precedent, through text.** Its Python emitter prints the program; the CLI creates a Rust IR and runs passes (`calyx@d6bcdc8:calyx-py/calyx/py_ast.py:21-27`; `calyx@d6bcdc8:src/main.rs:79-106`). [precedent-measured] Two source-inspected builder messages are “Combinational components do not have groups.” and “assignment outside `with group`”; these are Python exceptions/assertions, not remapped Rust errors (`calyx@d6bcdc8:calyx-py/calyx/builder.py:258-267`; `calyx@d6bcdc8:calyx-py/calyx/builder.py:1728-1732`). [precedent-measured] Source metadata uses stack inspection to find an external caller and emits `FILES`/`POSITIONS` information (`calyx@d6bcdc8:calyx-py/calyx/py_ast.py:63-101`; `calyx@d6bcdc8:calyx-py/calyx/py_ast.py:134-150`). [precedent-measured] However, the inspected ordinary compiler-error path copies parser spans from attributes; parsing registers the Calyx input file (`calyx@d6bcdc8:calyx/frontend/src/parser.rs:78-102`; `calyx@d6bcdc8:calyx/frontend/src/attributes.rs:81-84`; `calyx@d6bcdc8:calyx/utils/src/errors.rs:29-55`). [judgment] Python metadata therefore does not establish end-to-end Python-line reporting for these compiler errors (same citations).

[precedent-measured] Calyx configures builder-output, simulation-correctness, and source-location suites; numeric-type tests also match expected exception messages (`calyx@d6bcdc8:runt.toml:214-240`; `calyx@d6bcdc8:calyx-py/test/numeric_types.py:79-101`). [judgment] These inspected tests establish useful coverage categories, but do not establish negative-test coverage for every builder exception or a passing suite at this commit (same citations).

[precedent-measured] **PyMTL3 separates executable Python models from translatable blocks.** It obtains block source/AST in Python, generates RTLIR, and optionally builds a Verilator model whose shared library is loaded through CFFI (`pymtl3@c8b349f:pymtl3/dsl/ComponentLevel2.py:102-111`; `pymtl3@c8b349f:pymtl3/passes/rtlir/behavioral/BehavioralRTLIRGenL1Pass.py:47-80`; `pymtl3@c8b349f:pymtl3/passes/backends/verilog/import_/verilator_wrapper_py_template.py:29-58`). [precedent-measured] Two source-inspected messages are “invalid operation: lambda function” and “invalid type: dict”, both covered by negative cases; the helper requires the expected exception and message substring (`pymtl3@c8b349f:pymtl3/passes/rtlir/behavioral/BehavioralRTLIRGenL1Pass.py:470-477`; `pymtl3@c8b349f:pymtl3/passes/rtlir/behavioral/test/BehavioralRTLIRL1Pass_test.py:348-354`; `pymtl3@c8b349f:pymtl3/passes/rtlir/util/test_utility.py:18-33`). [precedent-measured] Maintainers explicitly document a translatable subset excluding arbitrary calls; simulation success alone is not their translation criterion ([translation documentation](https://pymtl3.readthedocs.io/en/latest/ref/passes-translation-intro.html), accessed 2026-09-28).

[judgment] Teaching evidence is uneven: Allo’s documented guest lecture and PyMTL3’s maintainer-reported course use establish different levels of exposure, neither a controlled learning-outcome comparison ([Allo catalogue](https://github.com/cornell-zhang/allo-tutorials); [PyMTL3 talk](https://www.csl.cornell.edu/~cbatten/pdfs/batten-pymtl3-nvidia2023.pdf), accessed 2026-09-28).

## Implications

### R-X

[judgment] Compatible with a Calyx-like CLI boundary. Python testing or packaging can be added independently of embedding. These precedents do not establish that an external student language is harder to teach.

### R-E

[judgment] A serialized IR builder would resemble calyx-py; direct typed-IR bindings would resemble Allo’s integration depth, without implying the same binding technology. Known obligations include Calyx’s builder-context rules and source-span separation, or Allo’s frontend inference, native packaging, and exception presentation. The Python surface alone does not require I2.

### R-B

[judgment] Two surfaces converging on textual IR most closely resemble Calyx’s frontend ecosystem and builder. A bound shared IR resembles Allo more closely. Both require explicit provenance and one authoritative legality checker; sharing an IR does not automatically share frontend diagnostics. Calyx’s generated-input spans are a concrete warning for this cell.

### P-X

[judgment] Exo establishes that significant legality checking and code generation can reside in Python. Its embedded syntax supplies no direct evidence for the usability of an external surface. Core-language performance remains unmeasured.

### P-E

[judgment] Exo and PyMTL3 are direct precedents for Python compiler implementations with AST-based embedded surfaces. Budget for a constrained language, source recovery, and negative tests; do not promise arbitrary Python-to-hardware translation.

### P-B

[judgment] The inspected Python IR pipelines make a second parser plausible, but this study does not demonstrate equivalent dual student surfaces. Treat semantic parity, source maps, and duplicated frontend validation as additional work.

## Evidence against

[judgment] The strongest counterargument to preferring a shallow serialized boundary is Allo: native typed-IR handles support scheduling directly, while calyx-py still needs stack inspection and textual source metadata. Serialization does not eliminate diagnostics work (`allo@094ab41:allo/customize.py:176-197`; `calyx@d6bcdc8:calyx-py/calyx/py_ast.py:63-101`).

[judgment] Conversely, a preference for deep native integration cannot be justified by course evidence here: PyMTL3’s teaching report accompanies a Python compiler and optional compiled simulator. Its documented translation subset and source-labelled negative tests demonstrate substantial frontend engineering without a Rust core.

[precedent-measured] PyMTL3’s inspected tests also mark star-argument cases as expected failures on Python 3, cautioning against treating the existence of negative tests as universal diagnostic coverage (`pymtl3@c8b349f:pymtl3/passes/rtlir/behavioral/test/BehavioralRTLIRL1Pass_test.py:302-314`).

## Open questions

- Run the pinned negative suites and probe repeated statements, blank lines, nested generators, notebooks, and downstream failures; source inspection has not measured these paths.
- Obtain maintainer-confirmed Exo/Calyx course deployments and workload/outcome evidence; current findings leave these unverified.
- Determine which layer must own legality and which source identity survives each lowering for the proposed hardware language.
- Georgia Tech’s linked course page returned HTTP 502. Allo teaching evidence therefore uses its maintainer catalogue. The web reader rejected the 19 MB PyMTL3 talk; a direct in-memory fetch and text extraction successfully opened it. No unavailable source supports a positive claim.

## Confidence

medium — High confidence in the inspected boundary mechanisms and quoted strings; limited confidence in diagnostic behavior outside those source paths, maintenance capacity, and teaching effectiveness. No runtime or educational outcome measurements were collected.
