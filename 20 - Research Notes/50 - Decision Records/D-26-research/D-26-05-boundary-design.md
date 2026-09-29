---
type: "research"
decision: "D-26"
angle: "5"
discriminates: both
sources:
  - "spatial-rs@eb49d8b:docs/adr/0002-file-cli-host-runtime.md:142-223"
  - "spatial-rs@eb49d8b:docs/adr/0002-file-cli-host-runtime.md:504-569"
  - "spatial-rs@eb49d8b:docs/adr/0002-file-cli-host-runtime.md:65-110"
  - "spatial-rs@eb49d8b:docs/language-spec.md:56-175"
  - "spatial-rs@eb49d8b:docs/language-spec.md:987-1067"
  - "spatial-rs@eb49d8b:crates/spatial-rs-core/src/frontend/source.rs:1-108"
  - "spatial-rs@eb49d8b:crates/spatial-rs-core/src/compiler.rs:30-68"
  - "spatial-rs@eb49d8b:crates/spatial-rs-core/src/compiler.rs:414-487"
  - "spatial-rs@eb49d8b:crates/spatial-rs-cli/src/lib.rs:12-77"
  - "calyx@d6bcdc8:calyx-py/calyx/builder.py:26-42"
  - "calyx@d6bcdc8:calyx-py/calyx/py_ast.py:56-150"
  - "calyx@d6bcdc8:calyx-py/calyx/py_ast.py:655-679"
  - "calyx@d6bcdc8:calyx/ir/src/from_ast.rs:257-265"
  - "calyx@d6bcdc8:calyx/opt/src/passes/well_formed.rs:127-157"
  - "allo@094ab41:allo/customize.py:1351-1408"
  - "allo@094ab41:allo/ir/utils.py:136-161"
  - "allo@094ab41:allo/ir/builder.py:93-114"
  - "https://mlir.llvm.org/docs/Dialects/Builtin/#location-attributes (accessed 2026-09-28)"
  - "https://mlir.llvm.org/docs/Diagnostics/ (accessed 2026-09-28)"
verified: ["2026-09-28"]
status: draft
---
## Scope

This note compares diagnostic ownership at three Python-to-Rust ingress points, independently of transport. I1 means Python testbenches around file/JSON commands; I2 means an in-process binding. Neither inherently chooses where language checking happens. The evidence is pinned source and specification inspection on 2026-09-28, not compiler execution or a working Spatial Python frontend. “Retained” below describes a proposed compositional compiler, not functionality already complete in the prototype.

## Findings

### Diagnostic obligations and current implementation

[precedent-measured] The specification distinguishes parse, name, const-eval, type, typed-use, and legality diagnostics. It requires the smallest offending primary span, relevant declaration secondaries, poison-based cascade suppression, and deterministic ordering. Consequently, preserving a message string alone does not preserve the diagnostic contract. Source: `spatial-rs@eb49d8b:docs/language-spec.md:987-1028`, `spatial-rs@eb49d8b:docs/language-spec.md:1052-1057`.

[precedent-measured] The current compiler entry point executes parse → constant evaluation → HIR → accepted-program classifier; these implementation stages do not equal the normative diagnostic phases. A source-inspected test expects an E0506 typed-use error during `CompileStage::Const`, with `N` primary and its defining `0` secondary. This is test inspection, not a passing test run. Sources: `spatial-rs@eb49d8b:crates/spatial-rs-core/src/compiler.rs:30-68`, `spatial-rs@eb49d8b:crates/spatial-rs-core/src/compiler.rs:414-487`.

### Boundary comparison

| Boundary | Rust phases retained | Python re-implements | Span provenance | Precedent / evidence |
| --- | --- | --- | --- | --- |
| (i) Generated `.spatial` text + Python→line map | Parse of generated text; name, const-eval, type, typed-use, legality if unresolved constructs survive emission | Python syntax/subset recognition, staging, text generation; no necessary duplicate Spatial semantic checker | Rust bytes refer to generated text; map primary **and** secondary labels back. A line-only map cannot reproduce precise Python expression spans. | [judgment] Closest transport analogy is Calyx textual emission, although its language level is IR. `calyx@d6bcdc8:calyx-py/calyx/py_ast.py:128-150` |
| (ii) Unchecked surface AST serialized from closed EBNF | Name, const-eval, type, typed-use, legality; Rust validates AST schema/structure, but does not parse Python or `.spatial` tokens | Python parsing or builder capture, restricted-form recognition, construction and source capture; leave identifiers, raw literals and constant expressions unresolved | Every node/subexpression carries original Python source ID and byte span; retained declaration links permit secondary labels | [judgment] EBNF supplies the surface vocabulary, not an existing wire schema. `spatial-rs@eb49d8b:docs/language-spec.md:56-175` |
| (iii) Checked controller-tree IR after name/const/type resolution | IR verification and downstream legality; typed-use only if unresolved use obligations and provenance remain | Python parsing, names/scopes, constant rules and type resolution; any typed-use checks consumed before crossing | Python must retain origin, declaration and use spans through folding/lowering; locations cannot reconstruct discarded expressions | [judgment] Calyx is an IR-level construction precedent, not proof of Spatial diagnostic parity. `calyx@d6bcdc8:calyx-py/calyx/builder.py:26-42` |

[judgment] No boundary makes Rust diagnose a Python syntax error rejected before ingress. Only (i) literally reruns all six Rust phases, and its parse errors describe generated Spatial text. Recommend (ii) for preserving **every applicable Spatial semantic diagnostic** in one Rust implementation, with Python syntax/subset diagnostics explicitly owned by the frontend. Calling (ii) “every diagnostic unchanged” would conceal that parse distinction; calling (iii) equivalent would conceal duplicated semantic ownership. Basis: the phase catalog and span requirements in `spatial-rs@eb49d8b:docs/language-spec.md:997-1028`.

[designed] Consider a Python surface declaring `N = SizeConst(0)` and using `Dram(Int, N)`. The proposed AST sends the name use and definition separately, allowing Rust to label the use and definition. Sending only dimension `0` in checked IR loses the original name relationship unless explicitly carried. This is a constructed example, not implemented syntax; the diagnostic obligation is illustrated by `spatial-rs@eb49d8b:crates/spatial-rs-core/src/compiler.rs:427-487`.

[judgment] Tracing, operator overloading, builders and AST transforms can all target (ii), but must preserve unresolved DSL syntax. Eager Python evaluation of a DSL constant or identifier makes its error Python-owned regardless of whether the transport is JSON or PyO3. AST capture offers explicit syntax nodes; builder/tracing designs need symbolic references and an origin policy. These are design consequences of retaining the EBNF's identifiers and constant-expression structure, not measured embedding behavior. Basis: `spatial-rs@eb49d8b:docs/language-spec.md:149-175`.

### What the precedents actually preserve

[precedent-measured] Calyx-py creates a Python `Program` and components, emits Calyx text, and emits `sourceinfo` tables. `PosTable` scans the stack for a frame outside its library and records filename/line, skipping `<string>`; control nodes emit `@pos` attributes. The Rust context carries the source-information table. This is hardware-IR construction with provenance, not a Python frontend sharing a high-level checker. Sources: `calyx@d6bcdc8:calyx-py/calyx/builder.py:26-42`, `calyx@d6bcdc8:calyx-py/calyx/py_ast.py:56-150`, `calyx@d6bcdc8:calyx-py/calyx/py_ast.py:655-679`, `calyx@d6bcdc8:calyx/ir/src/from_ast.rs:257-265`.

[precedent-measured] Calyx's Rust well-formedness code still rejects incompatible invocation cell types with attached positions. Source: `calyx@d6bcdc8:calyx/opt/src/passes/well_formed.rs:127-157`.

[judgment] Those observations establish retained metadata and Rust IR checks, but not automatic Python-line rendering for every Rust diagnostic. That stronger claim needs an end-to-end failing example; a `sourceinfo` table alone is insufficient evidence. Basis: the separate metadata and positioned-error paths cited above.

[precedent-measured] Allo obtains a Python AST, adjusts its line numbers to the function's original file, runs Python `TypeInferer`, then constructs MLIR. Its builder uses `Location.file(file_name, node.lineno, node.col_offset)` where available, otherwise `Location.unknown()`. Its customization path catches inference/build exceptions and reports the current AST node. Thus locations coexist with Python-owned earlier checking. Sources: `allo@094ab41:allo/ir/utils.py:136-161`, `allo@094ab41:allo/customize.py:1351-1408`, `allo@094ab41:allo/ir/builder.py:93-114`.

[precedent-measured] MLIR documents file/range, callsite, fused, named and explicit unknown locations; fused locations can retain multiple origins. Operation diagnostics use the operation's location, and notes can carry different locations. `SourceMgrDiagnosticHandler` displays source lines and can filter framework frames. These are provenance/reporting mechanisms, not a substitute for language checks. Sources: [MLIR locations](https://mlir.llvm.org/docs/Dialects/Builtin/#location-attributes), [MLIR diagnostics](https://mlir.llvm.org/docs/Diagnostics/) (both accessed 2026-09-28).

### I1, I2 and the actual envelopes

[precedent-measured] ADR 0002 specifies the contracts below. However, the pinned CLI exposes only `Check(PathBuf)` and text rendering; it does not implement the ADR's full command set or JSON switch. Therefore these envelopes are today's **specified contract**, not demonstrated working I1/I2 support. Sources: `spatial-rs@eb49d8b:crates/spatial-rs-cli/src/lib.rs:12-77`, `spatial-rs@eb49d8b:docs/adr/0002-file-cli-host-runtime.md:18-29`.

| Direction/purpose | Specified payload | Evidence |
| --- | --- | --- |
| Python testbench → run/build-with-inputs | `spatial.run.v1`: exactly `schema`, `inputs`, `inouts`; named ports, Int integers, Bool booleans, exact decimal-string fixed-point, flat row-major buffers | [precedent-measured] `spatial-rs@eb49d8b:docs/adr/0002-file-cli-host-runtime.md:159-217` |
| Run → Python | `spatial.run.v1`: `schema`, `outputs`, `inouts`; optional `analysis` containing `spatial.analysis.v1` when requested | [precedent-measured] `spatial-rs@eb49d8b:docs/adr/0002-file-cli-host-runtime.md:177-258` |
| Diagnostics → Python | `spatial.diagnostics.v1`, diagnostic array; code/phase/severity/message/primary/secondary/help. Locations contain path/kind/span/pointer: source byte/line spans versus JSON pointers | [precedent-measured] `spatial-rs@eb49d8b:docs/adr/0002-file-cli-host-runtime.md:504-557` |
| Build artifacts → tooling | `manifest.json` uses `spatial.abi.v1`; `vitis-project.json` uses `spatial.vitis-project.v1`. These describe ABI/build artifacts, not unchecked programs | [precedent-measured] `spatial-rs@eb49d8b:docs/adr/0002-file-cli-host-runtime.md:65-110`, `spatial-rs@eb49d8b:docs/adr/0002-file-cli-host-runtime.md:260-272` |

[precedent-measured] `spatial.host-result.v1` is the host-child success/fault protocol consumed and compared by the Rust parent before `spatial.run.v1` serialization; it is not the Python testbench's normal return envelope. Source: `spatial-rs@eb49d8b:docs/adr/0002-file-cli-host-runtime.md:122-140`.

[designed] A future PyO3 API could expose `check(source, sources) → diagnostics`, `build(source, options, inputs?) → artifact metadata`, and `run(source, inputs, options) → outputs/inouts`, with structured exceptions retaining diagnostic records. Bind the same Rust pass pipeline and exact numeric validation. Choosing Python dictionaries, JSON bytes or buffer handles is a separate API decision; none exposes a checked-IR constructor automatically. Contract basis: `spatial-rs@eb49d8b:docs/adr/0002-file-cli-host-runtime.md:142-223`.

### Requirements on the future representation

[judgment] Boundary (ii) requires: a versioned, closed AST schema; spans on **every node and subexpression**, including identifiers, literal spellings and typed uses; declaration/use provenance; stable traversal order and poison semantics; and a source registry admitting Python files, generated text and notebook cells. Preserve source text or immutable snapshots, and distinguish generated nodes explicitly. Validate source IDs, UTF-8 boundaries and spans at ingress. Keep a checked controller-tree IR behind the shared semantic passes. Basis: `spatial-rs@eb49d8b:docs/language-spec.md:1025-1028`, `spatial-rs@eb49d8b:docs/language-spec.md:1052-1054`.

[precedent-measured] Existing `SourceSpan` already combines source ID and byte range, while `SourceFile` accepts arbitrary names and calculates one-based character columns from UTF-8 offsets. This supports the design vocabulary but does not implement a multi-origin registry or remapping pipeline. Source: `spatial-rs@eb49d8b:crates/spatial-rs-core/src/frontend/source.rs:1-108`.

## Implications

### R-X

Keep native parsing and semantic diagnostics in Rust. Python testbenches require the host contract, not a second language frontend.

### R-E

Prefer unchecked AST ingress for semantic ownership; budget Python syntax/capture diagnostics and source registration explicitly. I2 does not remove that work.

### R-B

Both parsers should converge before names/constants/types are checked. Converging only at checked IR duplicates the most student-visible checks.

### P-X

The Rust boundary is absent. The same provenance requirements remain relevant if later lowering discards surface expressions.

### P-E

One implementation language removes transport work, but host Python evaluation and DSL semantics still need distinct diagnostic ownership.

### P-B

Share an unchecked representation and checker between surfaces. This angle does not establish a performance advantage for either core language.

## Evidence against

The strongest counterargument to (ii) is integration cost: (i) can reuse the existing `compile_source` entry point immediately, whereas (ii) requires a new schema, ingress validation and semantic entry point. Calyx demonstrates useful IR-level construction with origins; Allo demonstrates Python-owned inference followed by located MLIR. A frontend-specific error vocabulary may be acceptable, making full cross-surface parity an unnecessary constraint. These are design judgments grounded in the cited entry points and precedents, not comparative usability measurements.

## Open questions

- Must parity include codes, secondary spans, recovery and ordering, or only understandable messages?
- Which typed-use obligations remain representable after the proposed checked-IR boundary?
- How will nested generators and notebook cells retain both callsite and definition origins?
- Can a source-map prototype preserve precise spans for multiple expressions on one Python line?
- Which ADR envelope operations will be implemented before promising an I1 or I2 package?

## Confidence

medium — Phase ownership follows directly from information retained at each boundary. Source evidence is strong, but no Spatial Python frontend, remapping failure test, or comparative diagnostic usability study was executed.
