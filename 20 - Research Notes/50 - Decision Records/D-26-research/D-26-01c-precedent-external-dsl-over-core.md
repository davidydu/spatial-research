---
type: "research"
decision: "D-26"
angle: "1c"
discriminates: integration-depth
sources:
  - "dahlia@bd68b13:src/main/scala/Compiler.scala:156-189"
  - "dahlia@bd68b13:src/main/scala/common/Errors.scala:9-44"
  - "dahlia@bd68b13:src/main/scala/common/Errors.scala:52-216"
  - "dahlia@bd68b13:src/main/scala/passes/WellFormedCheck.scala:59-116"
  - "dahlia@bd68b13:src/main/scala/typechecker/TypeCheck.scala:147-163"
  - "dahlia@bd68b13:src/main/scala/passes/BoundsCheck.scala:55-84"
  - "dahlia@bd68b13:src/main/scala/passes/LoopCheck.scala:39-52"
  - "dahlia@bd68b13:src/main/scala/passes/DependentLoops.scala:67-75"
  - "dahlia@bd68b13:src/main/scala/typechecker/CapabilityChecker.scala:48-63"
  - "dahlia@bd68b13:src/main/scala/typechecker/AffineCheck.scala:126-151"
  - "dahlia@bd68b13:src/main/scala/typechecker/Info.scala:26-53"
  - "dahlia@bd68b13:src/main/scala/backends/calyx/Ast.scala:14-83"
  - "calyx@d6bcdc8:calyx/utils/src/position.rs:17-40"
  - "calyx@d6bcdc8:calyx/utils/src/errors.rs:9-75"
  - "calyx@d6bcdc8:calyx/frontend/src/source_info.rs:163-177"
  - "calyx@d6bcdc8:calyx/frontend/src/source_info.rs:681-706"
  - "calyx@d6bcdc8:calyx/opt/src/passes/well_formed.rs:233-259"
  - "https://raw.githubusercontent.com/astral-sh/ruff/4b84fcf6b9a0158d1b17c06730d58590352b8869/pyproject.toml#L1-L3 (accessed 2026-09-28)"
  - "https://raw.githubusercontent.com/astral-sh/ruff/4b84fcf6b9a0158d1b17c06730d58590352b8869/pyproject.toml#L47-L52 (accessed 2026-09-28)"
  - "https://raw.githubusercontent.com/astral-sh/ruff/4b84fcf6b9a0158d1b17c06730d58590352b8869/.github/workflows/build-binaries.yml#L81-L617 (accessed 2026-09-28)"
  - "https://raw.githubusercontent.com/astral-sh/ruff/4b84fcf6b9a0158d1b17c06730d58590352b8869/pyproject.toml (accessed 2026-09-28)"
  - "https://raw.githubusercontent.com/astral-sh/ruff/4b84fcf6b9a0158d1b17c06730d58590352b8869/.github/workflows/build-binaries.yml (accessed 2026-09-28)"
  - "https://docs.astral.sh/ruff/installation/ (accessed 2026-09-28)"
  - "https://www.maturin.rs/bindings.html (accessed 2026-09-28)"
  - "https://www.maturin.rs/distribution.html (accessed 2026-09-28)"
  - "https://ipython.readthedocs.io/en/stable/config/custommagics.html (accessed 2026-09-28)"
verified: ["2026-09-28"]
status: draft
---
## Scope

Assess external-language legality checking, downstream source mapping, pip distribution, and notebook hosting. Evidence was inspected on 2026-09-28 at the supplied Dahlia/Calyx commits; Ruff was additionally pinned to `4b84fcf6b9a0158d1b17c06730d58590352b8869`. No compiler, wheel installation, or notebook example was executed. All diagnostic strings below are **source-inspected**, with interpolation variables preserved, not captured execution results. This angle chiefly distinguishes integration depth; it does not establish a Rust-versus-Python implementation winner.

## Findings

### Dahlia: legality belongs before emission.

[precedent-measured] Dahlia runs well-formedness, type, bounds, loop, dependent-loop, capability, and affine checks before backend emission; Calyx is one selected backend. These are distinct compiler phases, not guarantees obtained merely by choosing an external grammar. (`dahlia@bd68b13:src/main/scala/Compiler.scala:116-119`, `dahlia@bd68b13:src/main/scala/Compiler.scala:156-189`.)

| Static-check family | Source-inspected behavior and message |
|---|---|
| Well-formedness | [precedent-measured] Restricts reductions and views inside unrolled contexts, array-argument calls there, and returns outside functions. Representative messages: `$op cannot be inside an unrolled loop`; `Cannot create view inside an unrolled context.` (`dahlia@bd68b13:src/main/scala/passes/WellFormedCheck.scala:59-116`; `dahlia@bd68b13:src/main/scala/common/Errors.scala:77-89`, `dahlia@bd68b13:src/main/scala/common/Errors.scala:207-208`.) |
| Types and shapes | [precedent-measured] Checks argument arity/subtyping, access dimensions, and literal lengths. Messages include `Application expected $exp arguments, received $actual.`, `Expected subtype of $exp in $con, received: $actual.`, and `Given type requires $expLen elements but literals has $acLen elements.` (`dahlia@bd68b13:src/main/scala/typechecker/TypeCheck.scala:147-163`, `dahlia@bd68b13:src/main/scala/typechecker/TypeCheck.scala:179-195`, `dahlia@bd68b13:src/main/scala/typechecker/TypeCheck.scala:309-320`; `dahlia@bd68b13:src/main/scala/common/Errors.scala:62-75`, `dahlia@bd68b13:src/main/scala/common/Errors.scala:238-241`.) |
| Bounds | [precedent-measured] Rejects excessive static/index-type maxima with ``Index out of bounds for `$id'. Memory size is $size, iterator max val is $mv``; potentially excessive sized-integer indices instead receive a warning ending `This might be out of bounds at runtime.` (`dahlia@bd68b13:src/main/scala/passes/BoundsCheck.scala:55-84`; `dahlia@bd68b13:src/main/scala/common/Errors.scala:98-102`.) |
| Loop dependence | [precedent-measured] Tracks use/definition states and rejects conflicts: `` `$id' cannot be used and then defined in an unrolled loop. `` The separate dependent-loop pass reports `Access depends on a loop iteration variable`, with the last-update location. (`dahlia@bd68b13:src/main/scala/passes/LoopCheck.scala:39-52`; `dahlia@bd68b13:src/main/scala/passes/DependentLoops.scala:67-75`; `dahlia@bd68b13:src/main/scala/common/Errors.scala:180-197`.) |
| Pipelining and views | [precedent-measured] Rejects sequenced pipelined bodies and invalid view shrink/alignment/split factors. Messages include `Pipelining is only allowed on non-sequenced loops.` and `Invalid shrinking factor for view. Expected factor of $bf (banking factor), received: $width`. (`dahlia@bd68b13:src/main/scala/typechecker/TypeCheck.scala:222-246`, `dahlia@bd68b13:src/main/scala/typechecker/TypeCheck.scala:258-263`, `dahlia@bd68b13:src/main/scala/typechecker/TypeCheck.scala:453-479`; `dahlia@bd68b13:src/main/scala/common/Errors.scala:154-159`, `dahlia@bd68b13:src/main/scala/common/Errors.scala:199-216`.) |
| Write capability | [precedent-measured] A repeated write capability produces `Already written to this expression in this context.` (`dahlia@bd68b13:src/main/scala/typechecker/CapabilityChecker.scala:48-63`; `dahlia@bd68b13:src/main/scala/common/Errors.scala:142-147`.) |
| Banking and affine resources | [precedent-measured] Checks banking divisibility, dynamic access to banked dimensions, available banks/ports, and unrolled write multiplicity. Messages include ``Invalid parallel access on `$arrId`. Banking factor ($bf) does not divide unrolling factor ($uf).``, ``Dynamic access of array `$id' requires unbanked dimension. Actual banking factor: $bf. Use a shrink view to create unbanked array.``, and ``Bank $bank for physical resource `$id' already consumed.`` (`dahlia@bd68b13:src/main/scala/typechecker/AffineCheck.scala:126-151`, `dahlia@bd68b13:src/main/scala/typechecker/AffineCheck.scala:177-192`; `dahlia@bd68b13:src/main/scala/typechecker/Info.scala:26-53`; `dahlia@bd68b13:src/main/scala/common/Errors.scala:33-43`, `dahlia@bd68b13:src/main/scala/common/Errors.scala:119-151`.) |

[precedent-measured] Dahlia formats positions as line/column plus a source excerpt; resource exhaustion adds earlier consumption locations, original resource count, and a gadget trace. Compilation classifies failures as type, parsing, impossible, or general errors. (`dahlia@bd68b13:src/main/scala/common/Errors.scala:9-44`; `dahlia@bd68b13:src/main/scala/Compiler.scala:188-205`.)

### Calyx: two position mechanisms.

[precedent-measured] Compiler diagnostics use `GPosIdx`: a global table holds file names, source text, and byte-span endpoints; parser nodes acquire spans, and attributes carry them. `Error` stores a primary span and additional annotations; formatting prints a filename, source line, and carets, or only the error kind when the span is unknown. (`calyx@d6bcdc8:calyx/utils/src/position.rs:17-40`, `calyx@d6bcdc8:calyx/utils/src/position.rs:203-230`; `calyx@d6bcdc8:calyx/frontend/src/parser.rs:142-146`; `calyx@d6bcdc8:calyx/frontend/src/attributes.rs:12-17`, `calyx@d6bcdc8:calyx/frontend/src/attributes.rs:81-84`; `calyx@d6bcdc8:calyx/utils/src/errors.rs:9-75`.)

[precedent-measured] Separately, IR context can hold `SourceInfoTable`: source-file paths without contents, position identifiers mapping to file/start-line/optional-end-line, and variable/memory mappings. Dahlia emits a `sourceinfo` table and `@pos`/group `"pos"` references, keyed by original line; its emitter does not preserve columns in that table. (`calyx@d6bcdc8:calyx/ir/src/context.rs:35-38`; `calyx@d6bcdc8:calyx/frontend/src/source_info.rs:163-177`, `calyx@d6bcdc8:calyx/frontend/src/source_info.rs:681-706`; `dahlia@bd68b13:src/main/scala/backends/calyx/Ast.scala:14-83`.)

[precedent-measured] Calyx's conflicting-assignment check attaches assignment attribute spans and secondary write locations. Its source-inspected width-mismatch expectation points to a `.futil` assignment. (`calyx@d6bcdc8:calyx/opt/src/passes/well_formed.rs:233-259`; `calyx@d6bcdc8:tests/errors/mismatch-widths.expect:1-6`.)

[judgment] Therefore, emitting source metadata does not establish automatic translation of every backend failure into an original DSL diagnostic. An external frontend needs a tested mapping contract across transformations and an explicit policy for generated nodes. The inspected diagnostic path uses spans, not the source-info lookup. (Same Calyx error/checker citations above.)

### Ruff/maturin: a wheel can contain the CLI.

[precedent-measured] Ruff's exact packaging configuration is below; the two excerpts are [pyproject.toml:L1–L3](https://raw.githubusercontent.com/astral-sh/ruff/4b84fcf6b9a0158d1b17c06730d58590352b8869/pyproject.toml#L1-L3) (accessed 2026-09-28) and [pyproject.toml:L47–L52](https://raw.githubusercontent.com/astral-sh/ruff/4b84fcf6b9a0158d1b17c06730d58590352b8869/pyproject.toml#L47-L52) (accessed 2026-09-28), opened from the [pinned official file](https://raw.githubusercontent.com/astral-sh/ruff/4b84fcf6b9a0158d1b17c06730d58590352b8869/pyproject.toml) (accessed 2026-09-28).

| Source line | Exact configuration |
|---|---|
| 1 | `[build-system]` |
| 2 | `requires = ["maturin>=1.9.3,<2.0"]` |
| 3 | `build-backend = "maturin"` |
| 47 | `[tool.maturin]` |
| 48 | `bindings = "bin"` |
| 49 | `manifest-path = "crates/ruff/Cargo.toml"` |
| 50 | `module-name = "ruff"` |
| 51 | `python-source = "python"` |
| 52 | `strip = true` |

[precedent-measured] Maturin documents `bin` as packaging executable scripts onto the installed environment's `PATH`; Ruff documents `pip install ruff`. ([Maturin bindings](https://www.maturin.rs/bindings.html), [Ruff installation](https://docs.astral.sh/ruff/installation/), accessed 2026-09-28.)

[judgment] Installing a matching prebuilt wheel consequently need not compile Rust on the student's machine. This is conditional on wheel availability and compatibility; source distribution fallback is different—Ruff's source-install smoke test explicitly provisions Rust. ([.github/workflows/build-binaries.yml:L63–L74](https://raw.githubusercontent.com/astral-sh/ruff/4b84fcf6b9a0158d1b17c06730d58590352b8869/.github/workflows/build-binaries.yml#L63-L74) (accessed 2026-09-28); [maturin distribution](https://www.maturin.rs/distribution.html), accessed 2026-09-28.)

[precedent-measured] Ruff's source-inspected build matrix is below. It describes configured builds, not verified published artifacts or locally executed CI. ([Pinned workflow](https://raw.githubusercontent.com/astral-sh/ruff/4b84fcf6b9a0158d1b17c06730d58590352b8869/.github/workflows/build-binaries.yml), accessed 2026-09-28.)

| Family | Configured targets and compatibility |
|---|---|
| macOS | [precedent-measured] x86_64 and aarch64. ([.github/workflows/build-binaries.yml:L96–L102](https://raw.githubusercontent.com/astral-sh/ruff/4b84fcf6b9a0158d1b17c06730d58590352b8869/.github/workflows/build-binaries.yml#L96-L102) (accessed 2026-09-28), [.github/workflows/build-binaries.yml:L157–L163](https://raw.githubusercontent.com/astral-sh/ruff/4b84fcf6b9a0158d1b17c06730d58590352b8869/.github/workflows/build-binaries.yml#L157-L163) (accessed 2026-09-28).) |
| Windows | [precedent-measured] MSVC x86_64, i686, aarch64. ([.github/workflows/build-binaries.yml:L197–L208](https://raw.githubusercontent.com/astral-sh/ruff/4b84fcf6b9a0158d1b17c06730d58590352b8869/.github/workflows/build-binaries.yml#L197-L208) (accessed 2026-09-28).) |
| Linux GNU | [precedent-measured] x86_64, i686, aarch64, armv7, s390x, powerpc64le use manylinux 2.17; riscv64 uses 2.31. ([.github/workflows/build-binaries.yml:L284–L323](https://raw.githubusercontent.com/astral-sh/ruff/4b84fcf6b9a0158d1b17c06730d58590352b8869/.github/workflows/build-binaries.yml#L284-L323) (accessed 2026-09-28), [.github/workflows/build-binaries.yml:L388–L396](https://raw.githubusercontent.com/astral-sh/ruff/4b84fcf6b9a0158d1b17c06730d58590352b8869/.github/workflows/build-binaries.yml#L388-L396) (accessed 2026-09-28), [.github/workflows/build-binaries.yml:L437–L461](https://raw.githubusercontent.com/astral-sh/ruff/4b84fcf6b9a0158d1b17c06730d58590352b8869/.github/workflows/build-binaries.yml#L437-L461) (accessed 2026-09-28).) |
| Linux musl | [precedent-measured] x86_64, i686, aarch64, armv7 use musllinux 1.2; an additional ARMv6 musl target specifies automatic compatibility. ([.github/workflows/build-binaries.yml:L452–L456](https://raw.githubusercontent.com/astral-sh/ruff/4b84fcf6b9a0158d1b17c06730d58590352b8869/.github/workflows/build-binaries.yml#L452-L456) (accessed 2026-09-28), [.github/workflows/build-binaries.yml:L524–L549](https://raw.githubusercontent.com/astral-sh/ruff/4b84fcf6b9a0158d1b17c06730d58590352b8869/.github/workflows/build-binaries.yml#L524-L549) (accessed 2026-09-28), [.github/workflows/build-binaries.yml:L587–L617](https://raw.githubusercontent.com/astral-sh/ruff/4b84fcf6b9a0158d1b17c06730d58590352b8869/.github/workflows/build-binaries.yml#L587-L617) (accessed 2026-09-28).) |

### IPython: notebook hosting without another compiler frontend.

[precedent-measured] IPython's custom-magic example receives `line` and `cell` in a `@register_cell_magic` function. A `Magics` class can access `self.shell.user_ns`; packaged extensions register through `load_ipython_extension`, loaded with `%load_ext`. ([Official custom-magics documentation](https://ipython.readthedocs.io/en/stable/config/custommagics.html), accessed 2026-09-28.)

[designed] A `%%spatial` adapter could pass the cell verbatim to the existing compiler, exchange named arrays through JSON, and display diagnostics/results. This is a proposed adapter, not a tested implementation. “Zero frontend” here means zero additional language frontend: the external parser and adapter still exist.

[judgment] Cell hosting does not itself establish DSL completion, formatting, refactoring, debugger mapping, or structured error navigation. Those remain acceptance criteria for the external-language toolchain; the documented magic callback supplies an entry point, not these services. ([IPython custom-magics API](https://ipython.readthedocs.io/en/stable/config/custommagics.html), accessed 2026-09-28.)

## Implications

### R-X

[judgment] I1′ offers pip-managed binary installation without a student Rust toolchain when compatible wheels exist. In adds notebook execution and Python testbench/data exchange while retaining external syntax. Neither supplies language tooling, source-map fidelity, or an in-process Python compiler API. Budget wheel CI and diagnostics alongside the parser.

### R-E

[judgment] The packaging precedent remains useful, but `bindings = "bin"` does not implement tracing, builders, AST transformation, or PyO3. Notebook availability alone provides little discrimination between this cell and R-X.

### R-B

[judgment] I1′ and In can serve the external surface independently. They do not demonstrate that two surfaces share equivalent legality rules or diagnostics; that needs common IR validation and explicit cross-surface tests.

### P-X

[judgment] The analogous I1′ benefit is pip distribution of the Python compiler/CLI; maturin's Rust-binary mechanism is not required for the Python core itself. Native downstream tools can still require platform packages. In gains the same cell adapter, Python data exchange, and notebook presentation as R-X. External grammar, tooling, and backend source mapping remain obligations.

### P-E

[judgment] This angle does not establish an implementation advantage for Python embedding. Dahlia illustrates the domain checks any chosen frontend may need; their existence does not determine which embedding style is easier to maintain.

### P-B

[judgment] The external half can gain pip and notebook access without proving the value of a second syntax. Evaluate the additional frontend against concrete teaching or metaprogramming needs.

## Evidence against

My leaning is that external syntax remains viable when Python installation and notebooks matter. The strongest counterevidence is that convenience adapters leave substantial compiler work intact: Dahlia's checks span multiple passes; some bounds risks only warn; its source-info emission is line-based and explicitly leaves function/parameter positions as future work (`dahlia@bd68b13:src/main/scala/backends/calyx/Backend.scala:1078-1082`). Ruff also maintains numerous platform builds, with some smoke tests conditional ([.github/workflows/build-binaries.yml:L258–L264](https://raw.githubusercontent.com/astral-sh/ruff/4b84fcf6b9a0158d1b17c06730d58590352b8869/.github/workflows/build-binaries.yml#L258-L264) (accessed 2026-09-28), [.github/workflows/build-binaries.yml:L483–L485](https://raw.githubusercontent.com/astral-sh/ruff/4b84fcf6b9a0158d1b17c06730d58590352b8869/.github/workflows/build-binaries.yml#L483-L485) (accessed 2026-09-28)). These precedents establish mechanisms, not affordable staffing, student usability, or complete error coverage.

## Open questions

- Which minimum OS/architecture/libc combinations require supported wheels, including downstream executables?
- Can a transformed Calyx failure recover the exact DSL expression and notebook-cell identity?
- Which checks must reject programs, versus warn or defer to runtime?
- What completion, formatting, interruption, and reproducibility behavior must the notebook adapter provide?
- Unavailable evidence: executed compiler diagnostics, fresh wheel installation, published-wheel completeness, notebook trials, and student outcomes were not measured. Initial web-tool fetches of pinned Ruff files failed; direct HTTPS reads of those exact files subsequently succeeded. No cited source remained blocked.

## Confidence

medium — Strong source evidence for checking, position structures, packaging configuration, and magic APIs; limited evidence for end-to-end reliability, educational usability, or comparative implementation cost.
