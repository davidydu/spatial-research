---
type: spec
title: "Proposed Python Spatial language contract"
concept: python-language-and-capture
scope: python-rewrite
source_files: []
source_notes:
  - "[[PY-R001 - Programming Model Study]]"
  - "[[PY-R004 - Capture Composition and Diagnostics]]"
  - "[[PY-R005 - Full Language Coverage and Migration]]"
decision_records:
  - "[[D-27]]"
  - "[[D-28]]"
hls_status: rework
depends_on: []
status: reviewed
adoption_status: proposed
implementation_status: not-implemented
---

## Scope and authority

This is a proposed contract for review under [[D-28]]. It describes a Python-syntax Spatial language and its Python compiler. It is not a claim that arbitrary Python programs synthesize, that these APIs exist, or that the professor has approved the details. The supporting studies retain alternatives, source evidence, and deliberate differences from original Spatial.

Ordinary Python handles data preparation, configuration, generation, tests, and launch. A captured Spatial kernel describes typed accelerator operations, storage, controllers, and communication. Both are Python-facing, but their execution stages are explicit.

## Acquisition and composition

The primary surface is captured source. The initial acquisition contract reads dedicated source files or raw notebook cells into immutable source units, with text, tokens, identity, digest, line map, and origins. It does not execute their markers, defaults, annotations, or bodies. Declarative DSL imports resolve source dependencies and manifests; they do not import a host module. Mixed host/kernel modules and callable introspection are separate possible adapters, not part of this initial contract.

This acquisition choice is narrower than the source-first choice. A decorator could acquire a function's source and preserve its body too. Raw source is recommended here for uniform file/cell/generated inputs and explicit dependency snapshots. The cost is a less familiar source-as-data workflow. A future callable adapter must state what host definition-time work occurs and how exact text and bindings are frozen; it can feed the same compiler without changing kernel semantics.

The builder is a generator/tooling interface to the same unchecked program. Its host code executes normally. Symbolic expressions preserve literal trees and pending effects; attachment is exactly once. Freeze rejects dropped or multiply attached consuming expressions, escaped binders, or incomplete regions. Builder constructor success is not semantic validation. A full second polished public API is not required for the first release.

Meta parameters contain only the closed immutable schema in R004: exact builtin scalar values, immutable tuples/records, and registered descriptors. Bind all signature meta formals before interpreting dependent port annotations. The compiler's bounded meta evaluator handles exact arithmetic, registered constructors, and explicit static choices/expansion; arbitrary computation occurs in the host generator. Validate source syntax even in discarded static branches, then type/effect-check the specialized program. Runtime branch alternatives both remain represented.

Helpers and components have typed arguments, region results, explicit dependencies, and hygienic local identities. Nested helpers capture DSL symbols subject to capability and lifetime checks. Calls are initially acyclic. Host recursion may generate a finite graph. General runtime recursion and unrestricted `while` have explicit diagnostics; typed FSM and forever controllers provide the corresponding bounded-state/dynamic-control model. Libraries compile through the same path as user code.

## Proposed source grammar boundary

This is the proposed accepted-form policy, not an implemented parser. [[10 - Source Checker and IR Blueprint]] now fixes the proposed grammar, parametric intrinsic families, signatures and checking algorithms. S0 implements that design after approval; earlier competing sketches retain explicit migration notes. Adding a syntactic form requires a meaning and diagnostic rule, not merely acceptance by Python's parser.

| Form | Contract |
|---|---|
| Modules and definitions | Declarative source dependencies, registered kernel/helper markers, typed parameters, explicit meta parameters, nested typed helpers, and registered immutable source constants |
| Declarations and writes | Immutable annotated scalar/value bindings; explicit storage/Reg allocation; mutation only through writable output ports, registers and indexed storage; augmented assignment retains its distinct order |
| Expressions | Names, exact numeric/Boolean literals, registered typed operations/calls, field/index/view access, typed aggregate construction, and lazy conditional expressions |
| Boolean control | Conditions require Bool; `and`/`or` short-circuit through regions, `not` negates Bool; no implicit integer/buffer truth conversion |
| Comparisons | Typed comparisons; chained comparisons evaluate shared middle operands once and later operands only while the chain remains true |
| Runtime regions | `if`/`else`, counted `for` over registered controller domains, and registered controller/context forms; helper `return` yields a typed region result |
| Static regions | Explicit `static` conditions and finite static expansion; no implicit conversion of runtime values into host control |
| Excluded ordinary Python mechanisms | Dynamic imports, arbitrary callbacks/method lookup, reflection, classes created inside kernels, generators/async, exception handling, comprehensions, arbitrary iterables, runtime recursion, and unconstrained `while` |

Initially require one assignment target per statement; destructuring/chained assignment can be expressed with explicit temporary values and writes. This is a surface limit, not removal of an original accelerator capability. Do not silently treat unsupported syntax as host execution. Registered source operations cover the full family inventory in R005; a feature may have a defined contract before its implementation stage.

Numeric tokens accept Python-style decimal/base-prefixed integer digits and valid digit-separator underscores; base prefixes are `0b`, `0o`, and `0x`. Decimal real forms include decimal points and base-ten `e`/`E` exponents, with separators only where Python permits them. Parse digits and powers into exact integers/rationals, retaining unary sign and expression structure. Hexadecimal floating literals, imaginary literals, and a bare NaN/infinity literal are excluded; use explicit typed special-value/bit constructors. Source-size and expansion budgets diagnose excessive inputs without silently rounding them. Strings are compile-time descriptors, formatting templates, or acquired host data; they do not imply dynamically allocated accelerator strings.

## Implementation-readiness refinements, 2026-10-01

The source/checker blueprint supplies the closed meta schema, name resolution, bidirectional type checks, helper/component signatures and owned graph records. Values are immutable; recurrence uses explicit Reg/storage. Helpers return at the final statement or through an exhaustive final if/else. Borrowed views may return only with declared owner/lifetime mapping; callee-local handles cannot escape ordinary calls. Index-to-accelerator integer conversion is explicit `embed(Int, index)`.

Empty Vec/Tuple/Record values have zero data bits while retaining type and logical identity. A masked queue result instead uses `MaskedVec(N,T)`: inactive lanes are unavailable, not numerical zeros. Extraction requires an active lane or faults; explicit `materialize(default)` supplies values before ordinary packing/arithmetic. Canonical zero payload for inactive serialized lanes grants no read permission. See the blueprint for exact registry rules and source/builder acceptance cases.

## Meaning of represented execution

Values have declared Spatial types. Meta/index quantities and accelerator `Int` are different categories. Integer, fixed, floating, conversion, random, and reduction rules belong to [[20 - Python Numeric Contract]]. A host float is an already rounded input kind; it is not the source decimal token.

Statements in an ordered region preserve evaluation and observable effect order. Ordinary assignment evaluates RHS before target address and write. Augmented assignment evaluates its target once, reads it, then evaluates RHS, combines, and writes. Lazy branches issue only selected effects and faults. A pure value selector chooses already evaluated values and cannot conceal a consume in an unselected argument. Source and builder forms must agree after normalization.

Storage declarations create logical objects with backing identity, generation, capability, lifetime, and initialization. Views preserve that identity. Distinct variable/port names do not establish disjointness. Runtime indexing checks logical per-axis bounds; physical burst padding grants no extra source access. Dynamic Vec access is checked selection, not element-zero fallback. One-hot selection requires at most one active selector and an explicit empty-case default or fault; priority selection uses lowest-position precedence.

[[30 - Python State and Protocol Contract]] defines stateful and concurrent execution. [[40 - Python Compiler and HLS Contract]] defines the check/simulation/target boundary. These rules are proposed together; unresolved contradictions must be repaired before adoption rather than resolved by whichever implementation happens to run first.

## Host workflow and evidence

The host captures, specializes, checks, prepares inputs, and then simulates or compiles the same checked meaning. Default reference input snapshots copy each backing allocation once and preserve views. Sessions distinguish invocation-fresh from explicit persistent state. Buffer shape, strides, exact format, aliases, and ownership are validated before launch. Fault results retain earlier committed effects and mark outputs incomplete.

Diagnostics share phase/code, primary span, related definition/instantiation origins, explanation, and repair. Notebook edits create new source revisions; old program objects retain their own source and bindings. Canonical semantic identity is separate from exact diagnostic provenance and build/run keys.

Acceptance uses the paired cases and matched negatives in R001/R004, then every G01–G18 family gate in R005. Include helper composition, alias changes, numeric token boundaries, short-circuit/chained-comparison effects, invalid syntax hidden in static branches, assignment order, and edited/generated source origins. Parsing the illustrative examples alone does not satisfy this contract.
