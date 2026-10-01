---
type: implementation-blueprint
title: "Python package, artifacts and conformance blueprint"
project: spatial-python
date: 2026-10-01
status: reviewed
adoption_status: proposed
implementation_status: not-implemented
---

## Purpose

This proposed implementation design closes interfaces left to S0 in [[04 - Python Implementation Roadmap]]. It refines [[D-28]] and [[PY-R007 - Host Workflow Reproducibility and Validation]]. It specifies what contributors will implement after approval; none of the package below exists yet. The independent audit is [[07 - Python Implementation Readiness Audit]].

## Repository and module ownership

Use a new repository with working project name `spatial-python`, import package `spatial`, and a `src/` layout. These are local project names, not a claim of available or published package-registry names. Keep Scala and Rust repositories as reference checkouts. The documentation vault remains the authoritative reviewed design; the implementation repository links to the exact adopted document revision and includes executable fixtures and implementation records.

| Module under `src/spatial/` | Owns | May depend on |
|---|---|---|
| `schema/` | Frozen type, value, symbol, origin, operation-registry and capability descriptors | Python standard library |
| `source/` | Source units, manifest resolution, token/AST normalization, grammar, frozen meta specialization | `schema` |
| `builder/` | Owned unchecked records, scoped attachments and freeze | `schema`; no checker authority |
| `numeric/` | Exact arithmetic, bit encodings, profiles, interval/certificate evaluation and RNG transitions | `schema`; no compiler or simulator state |
| `protocol/` | Resource records and pure request/commit transition functions | `schema`, `numeric` |
| `ir/` | Spatial xDSL semantic and implementation dialects, adapters, private snapshot ownership | `schema`, xDSL |
| `check/` | Binding/type/effect/capability/lifetime checks, obligations and verification | `schema`, `source`, `ir`, `numeric`, `protocol` |
| `analysis/`, `passes/` | Revision-keyed analyses, transaction wrapper and named transformations | Checked IR interfaces; no host bindings |
| `runtime/` | Invocation state, continuations, scheduler, environments, replay and session snapshots | Checked IR queries, `numeric`, `protocol` |
| `plan/` | Target-neutral physical-plan construction, target capability checks and DSE | Checked IR, analyses, verified numeric/protocol realizations |
| `backend/hls/` | Typed C++ emission, helper selection, interface manifests and source maps | Checked implementation plan; never source AST or raw unchecked input |
| `host/`, `artifacts/` | Public workflow, typed buffers, registry lookup, canonical import/export and identities | Public boundaries of the modules above |
| `adapters/` | Notebook, arrays, vendor invocation and device drivers | Public host/artifact interfaces; optional dependencies loaded on explicit selection |
| `lib/` | Versioned declarative source templates and explicit host utilities | Same language frontend as user programs; no whole-program recognizers |
| `cli.py`, `diagnostics/` | Command/API projection and common structured diagnostics | Public host API and immutable records |

Test folders mirror boundaries: `tests/{source,check,numeric,protocol,runtime,passes,artifacts,plan,hls,composition}`. Keep data-only expected results in `tests/fixtures/`; separate vendor tests under `tests/vendor/`. `tools/conformance.py` reads the manifest below. `profiles/` contains versioned semantic and target descriptors, and `locks/` contains exact dependency/tool manifests. Documentation examples are copied into fixtures with source-document revision and example ID so drift is visible.

No module retrieves a global current compiler, interpreter or target. A compilation context owns immutable registries plus per-revision analysis caches. An invocation owns mutable state. The checker may share numeric functions with runtime, but acceptance oracles are separate. Code review checks this dependency direction and rejects circular imports resolved through ambient mutable state.

## Public workflow and failures

The following names are the proposed host API. Kernel syntax and its registered operations are defined in [[10 - Source Checker and IR Blueprint]]. API calls return immutable result records; they do not expose mutable xDSL objects.

| Call | Input and result |
|---|---|
| `capture(bundle)` | A `CaptureBundle` containing the entry module/export and all source/dependency contents → syntax-validated `Template`. No source execution or semantic support claim |
| `specialize(template, meta)` | Exact named frozen values → `UncheckedProgram`; validate reachable source grammar before static branch elimination |
| `check(program, profile)` | Unchecked program and semantic profile ID → `Result[CheckedProgram]`; profile distinguishes guarded reference validity from statically discharged requirements |
| `prepare(program, bindings, session=None)` | Checked program, typed port/environment descriptors, optional exclusively owned session → `Result[Invocation]` |
| `simulate(invocation, environment, budget)` | One prepared invocation or saved continuation → `RunResult`; budget includes steps, numeric work and trace storage |
| `plan(program, target, binding_contract)` | Checked meaning, target descriptor and invocation-specialization assumptions → `Result[ImplementationPlan]` |
| `emit(plan)` | Verified eligible implementation plan → `Result[Project]` with file bytes, hashes, source maps and manifest |
| `validate(project, toolchain)` | Generated project and explicit installed toolchain → evidence records with commands, exit status and report hashes |
| `export_artifact(value)` / `import_artifact(bytes, registry)` | Canonical data format below; import reconstructs a candidate and verifies it, never trusts a stored checked flag |

`Result` is either `Ok(value, diagnostics)` or `Error(diagnostics, inspectable_partial=None)`. A failed plan can be inspected but cannot be passed to `emit` or reused as an eligible cache entry. Internal exceptions become `CompilerFailure` with reproduction IDs; they never masquerade as an ordinary source diagnostic. Public argument misuse receives a structured `HOST.INVALID_ARGUMENT` diagnostic. Unexpected process termination remains a failed tool execution.

`RunResult` has `outcome`, `complete_outputs`, `partial_state`, `trace`, `continuation`, `diagnostics`, and `run_identity`. Only successful completion populates `complete_outputs`. WaitingEnvironment, QuiescentUnknown, budget, breakpoint and supported cancellation/drain states can carry resumable continuations. QuiescentUnknown means no enabled transition is known but the evidence cannot establish an enabling environment path or a closed deadlock; it does not claim either. Semantic fault and cancellation retain committed partial effects; a completed fault cannot be resumed as if it had succeeded. Session state is serializable only at a quiescent declared checkpoint or with every outstanding request and environment obligation represented.

The CLI mirrors these calls as `spatial check`, `simulate`, `plan`, `emit`, `validate`, and `inspect`, added with their real feature slice. Structured stdout is one JSON result; human logs go to stderr. Exit 0 means that command's requested stage succeeded, 1 a source/invocation/runtime failure, 2 an unmet capability/requirement, 3 a vendor or external failure, and 4 a compiler defect. A successful `emit` never claims RTL validation. Host observation limits return an explicit incomplete outcome, not success or a deadlock proof.

## Runtime and dependency baseline

The proposed reproducible development baseline is **CPython 3.14.5**, the interpreter used by current local framework probes, with source syntax fixed to the reviewed 3.14 grammar. Supporting another Python minor requires the grammar/capture and artifact suite; xDSL's wider declared support does not establish Spatial support. Deployment platform support is separately tested; this baseline is not a claim that every operating system has been validated.

Pin xDSL to `0b107461b3bfcd353d949fe00d3d1623bd6c826a`, runtime dependencies `immutabledict==4.3.1`, `ordered-set==4.1.0`, and `typing-extensions==4.15.0`. Use `setuptools.build_meta` with build dependencies `setuptools==84.0.0`, `setuptools-scm==9.2.2` for the xDSL snapshot, and `packaging==25.0`. The Spatial package can use a static version and needs no SCM version generator at runtime. These are reproducibility choices, not a claim that newest versions are necessary. Optional solver, array, notebook, LLVM and vendor dependencies stay out of the core lock.

R006 already checked core imports against three runtime dependencies. This review also checks building/installing the pinned xDSL wheel in a disposable environment and records wheel digests below. The original dependency declarations are `xdsl@0b10746:pyproject.toml:1-32`. The Python [packaging specification](https://packaging.python.org/en/latest/specifications/pyproject-toml/) defines build-system requirements separately from project dependencies (accessed 2026-10-01). Do not mutate the system environment or publish a package during this research.

## Canonical data format

Define **SpatialJSON-v1**, an explicitly restricted format, not an assertion of compliance with another canonical-JSON standard. The allowed tree contains exact builtin strings, Booleans, null, lists, and string-keyed objects. JSON number tokens are forbidden. Every structural integer is a canonical decimal string (`0` or optional minus followed by a nonzero leading digit); negative zero and leading zeros reject. Semantic integer values use `{"kind":"integer","value":"-3"}`. Typed bits use `{"kind":"bits","type":"t0","hex":"ff"}` with exactly `ceil(W/4)` lowercase hex digits and zero unused high bits. MaskedVec records retain a validity vector and canonical zero payload for inactive lanes, which remain unreadable until guarded extraction or explicit materialization. Unchecked artifact pending attachments are rechecked against the frozen effect ledger, including dropped/duplicate leaves. Rationals use reduced signed numerator and positive denominator strings. Floats use typed bits, preserving signed zeros and NaN encodings; host JSON floats never carry numeric semantics.

Schema field names are ASCII identifiers. User strings retain exact Unicode scalar values; reject lone surrogates and do not normalize source/provenance text. Arrays preserve semantic order. Objects sort keys by ASCII order. Encode UTF-8 with no BOM or trailing newline, no whitespace between tokens, compact JSON separators, literal Unicode and ordinary JSON escaping of quotes, backslash and controls. This is precisely `json.dumps(tree, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')` **after** recursive exact-type/schema validation. No `default` callback or user object's serialization method is called.

Decoder requirements: enforce byte, nesting, object-count and string-length budgets; require UTF-8; reject duplicate keys through `object_pairs_hook`; reject raw number tokens through `parse_int`, `parse_float` and `parse_constant`; validate all tags/fields/IDs and re-encode to require canonical bytes. Limits produce `ARTIFACT.RESOURCE_LIMIT`. Huge decimal integers use bounded chunk conversion rather than changing the interpreter's process-wide digit limit. Re-encoding is not a substitute for semantic or reference validation. Python's [JSON documentation](https://docs.python.org/3.14/library/json.html) documents the decoding hooks and nonfinite-value behavior; those hooks support this stricter project format (accessed 2026-10-01).

An artifact envelope has exactly `schema`, `kind`, `payload`, `provenance`, and `dependencies`; unknown fields or major versions reject. Each kind defines a closed payload schema. Optional fields are explicitly null rather than silently omitted. Human pretty printing is an export view, not canonical bytes.

| Kind / schema ID | Required payload fields |
|---|---|
| Template / `spatial.template/1` | `entry`, `source_units`, `dependency_manifest`, `grammar_version`, `meta_formals` |
| Unchecked / `spatial.unchecked/1` | `profiles`, `definitions`, `exports`, `entry_id`, `meta_snapshot`, `dependency_refs`, `symbols`, `origins`, `requirements_requested`, `pending_attachments`; nested region/expression records from the source blueprint |
| Semantic / `spatial.semantic/1` | `exports`, `types`, `functions`, `resources`, `profiles`, `requirements`, `model_refs` |
| Plan / `spatial.plan/1` | `semantic_digest`, `target_digest`, `binding_contract`, `machine_graph`, `storage_plan`, `numeric_realizations`, `abi`, `constraints`, `correspondence`, `obligations` |
| Project / `spatial.project/1` | `plan_digest`, `files`, `entry_symbol`, `build_recipe`, `toolchain_requirements`, `source_map`, `capabilities` |
| Invocation / `spatial.invocation/1` | `semantic_digest`, `port_bindings`, `backings`, `session_state`, `environment_contract`, `initial_rng`, `budgets` |
| Run / `spatial.run/1` | `invocation_digest`, `scheduler_profile`, `environment_events`, `outcome`, `outputs`, `partial_state`, `trace_digest`, `continuation`, `diagnostics` |
| Evidence / `spatial.evidence/1` | `project_digest`, `stage`, `tool_identity`, `commands`, `exit_status`, `reports`, `metrics`, `assumptions` |

The frontend blueprint defines function/operation/type records; numeric and protocol blueprints define their payloads; the table above fixes their containers. Each nested record carries a registered tag and schema version, not arbitrary dictionaries. Type tables sort canonical descriptor bytes. Exports retain declared ABI order; reachable private functions are numbered by deterministic first-use traversal from those exports. Blocks, operations and arguments use preorder positions with explicit operand/result indices. Local user names and source offsets are provenance. No process address, Python object hash, absolute path or xDSL pointer enters canonical semantics. This canonicalizes the same normalized ordered graph and alpha-renamed locals, not all mathematically equivalent programs.

Import order is bytes → strict tree/schema → unresolved owned records → ID/type/reference validation → frozen candidate IR → full Spatial verifier, including profile/model checks and obligations. A hash or signed cache entry never substitutes for that verifier. A failed or unknown requirement remains ineligible at the corresponding stage. Recompute rather than deserialize analysis caches initially.

## Identities, cache transactions and provenance

Use SHA-256 over `b'spatial/' + kind + b'/1\x00' + canonical_payload_bytes`. Kinds domain-separate acquisition, semantic, plan, build, invocation, run and provenance. Acquisition includes exact source/dependency contents and parser identity. Semantic identity includes canonical meaning, profiles, admitted invocation requirements and foreign-model code/dependency digests. Plan adds target/binding assumptions. Build adds compiler/framework versions, pipeline/options, helper contents, generated files and tool profile. Run includes exact typed input backing snapshots, session/RNG state, environment events and scheduler/budget identity. An incomplete environment records an open tail; its prefix never identifies a completed run.

Paths, labels, source text and expanded origin chains belong to a separately hashed provenance table keyed by canonical node IDs. Semantically equal artifacts can share checked meaning while diagnostics bind to their own provenance. A cache lookup never attaches another user's source map merely because semantic digests match. Public API/export names and external ABI names remain semantic when renaming them changes the interface.

Publish a cache entry only after its stage completes: write a unique temporary directory, validate file hashes/manifest, then atomically rename on the same filesystem. Readers require a complete manifest and check all referenced hashes. Cache keys include every upstream dependency; a missing optional model/profile is a cache miss or diagnostic, not a guessed replacement. Concurrent writers of identical bytes may converge; differing payloads under one key are a compiler/storage defect. Never unpickle or import code from an artifact.

## Buffers, packing and session ownership

`Backing` explicitly owns bytes/bytearray plus an invocation-local ID. `BufferView` has backing ID, byte offset, shape, byte strides, element type, access capability and logical origin. Core constructors take explicit descriptors; automatic NumPy/memoryview inspection belongs to an adapter. One preparation registry identifies common owners across views. Unknown owner/offset cannot establish disjointness; an adapter must provide a checked mapping or make an explicit copy and retain its changed alias contract.

For a nonempty view, check the minimum/maximum reachable byte address using each `(extent-1)*stride` contribution and the element slot width. Empty dimensions perform no element access. Negative/zero strides are representable; writable overlap requires the declared alias/order contract. An interval-overlap test is conservative: it cannot prove overlap or disjointness of all strided sets. Use exact finite enumeration under a budget or the verified affine method; otherwise retain `unknown` and reject a requested disjointness precondition. Copy each backing allocation once for default reference preparation and recreate every view on that copy. Do not snapshot each port separately.

The portable host ABI uses little-endian bytes, one `ceil(W/8)`-byte slot per scalar/aggregate element, with unused high bits zero. Aggregate fields in declaration order and vector element zero occupy successive low-bit ranges; nested layout recurses. Packed off-chip hardware words have a separate physical mapping and cannot silently change this host ABI. Scalars travel as exact typed bits; source-visible DRAM address bits are explicit environment/binding inputs, never Python object IDs. The invocation address table maps backing IDs to supplied base-address bits; a view offset uses the declared address arithmetic. Reference/target comparison must use matched allocation responses or an explicit virtual-address adapter. A slot with nonzero padding or wrong byte count rejects before execution.

Empty aggregates have `Bits(0)`: their canonical hex is the empty string and their portable byte slot has length zero. Their logical cells, bounds, initialization, lifetime and backing identity still exist. Reads/writes can therefore perform logical checks or effects without a physical byte access. Keep logical coordinate maps alongside byte views; two zero-byte elements cannot be distinguished by byte offset alone. Never divide by a zero slot width or infer disjoint logical objects from empty address intervals. Target routes erase only the zero data wires, retaining required validity/control state; a foreign ABI that cannot represent this must report a scoped capability error.

A session records semantic interface/state-schema digests, backing/resource generations, initialized cells, numeric/profile IDs and explicit RNG states. `prepare` acquires exclusive session ownership; success/fault/cancel releases it only after the protocol declares quiescence. `reset` waits for or cancels/drains outstanding obligations before installing reset images. An observation timeout leaves ownership held by the resumable invocation. Hardware partial writes remain incomplete outputs; a host cannot relabel them as a successful result.

## Diagnostics and conformance fixtures

Diagnostic fields are `code`, `phase`, `severity`, `message`, `primary`, `related`, `obligation`, `repair`, and `reproduction`. `primary` contains source-unit digest plus half-open UTF-8 byte offsets; presentation converts to character columns using the frozen line map. Related locations carry roles such as declaration, instantiation and conflicting access. Codes use a stable namespace (`SOURCE`, `BIND`, `TYPE`, `EFFECT`, `LIFETIME`, `NUMERIC`, `PROTOCOL`, `HOST`, `ARTIFACT`, `TARGET`, `VENDOR`, `INTERNAL`) and a named rule, never a source-line number. Messages may improve without changing rule identity. A builder without source has generated origin plus instantiation chain; it does not fabricate a file span.

Define `spatial.fixture/1` with fields `id`, `families`, `stage`, `source_bundle`, `meta`, `profile`, `bindings`, `environment`, `expected`, `oracle`, `variations`, and `provenance`. `expected` is a tagged union: diagnostic records; exact output bits plus ordered effects; allowed finite trace graph plus terminal classification; canonical artifact bytes/hash; or target evidence constraints. The `oracle` names hand derivation, independent algorithm, pinned upstream vector, or separately validated protocol model. Shared simulator/checker functions cannot supply their own independent expected answer.

Every fixture has at least a positive case and a distinguishing negative/boundary variation, unless intrinsically a failure-only regression. Trace comparison projects to declared observable events while preserving causal predecessors and terminal/progress requirements. Do not compare only final values, require a single canonical schedule from every backend, or accept an arbitrary prefix as a completed result. Bounded interleaving exploration records bounds and fairness assumptions. Hardware report parsers retain raw report hashes and separate requested, estimated, synthesized and implemented values.

The conformance manifest maps every F01–F18 family and G01–G18 gate to fixture IDs and implementation stages. A check rejects orphan features, duplicate IDs, missing oracle provenance and support claims lacking their required stage. This accounting checks references; it cannot certify expected values. Numeric vectors, scheduler models and source-level counterexamples receive independent review.

## Concrete S0 and S1 implementation order

S0 commits, after approval: (1) package/layout/locks and immutable descriptors; (2) SourceUnit/CaptureBundle plus grammar/meta normalization and origin tests; (3) unchecked builder and complete registry schema; (4) canonical import/export with malformed-input negatives; (5) private dialect snapshot plus Spatial verifier and diagnostic rendering. Each is usable through one `check` workflow before expanding CLI commands. Pin the adopted documentation SHA in the package; do not invent missing rules during coding.

S1 then adds integer numeric primitives, backing/view preparation, structured control and composed helpers, followed by the reference interpreter and end-to-end fixtures. Required discriminators include the exact literal tree, Unicode origin, uninitialized/aliased storage, inactive divide-by-zero, RHS-before-target assignment, augmented target-once assignment and malformed serialized graphs. Run the same normalized program from source and builder through checking, artifact reload and simulation. S2–S9 retain the roadmap's full-family scope and cross-layer support criteria.

## Research probe record

The packaging probe built the pinned xDSL snapshot twice from separate fresh Git archives with `SOURCE_DATE_EPOCH=1790713391` and explicit SCM version `0.1.dev1+g0b107461b.spatial1`. A recorded packaging-only patch changes `packages.find = {}` to `packages.find = { include = [ "xdsl", "xdsl.*" ] }`. The resulting 1,169,644-byte wheels are identical. Their 459 entries contain only xDSL and distribution metadata. An earlier unfiltered build included tests/docs and a repeated dirty-tree build included `build/lib`; the clean-archive and package-filter requirements address that observed failure. No semantic xDSL source is patched.

Installed the curated wheel in a fresh CPython 3.14.5 environment with only the three base runtime dependencies, then independently reran the frontend reviewer's structured helper/if/loop/task probe without a source checkout on its import path. Nested cloning and text roundtrip passed, four effect operations survived CSE/DCE, and implicit ancestor capture rejected. Framework structural verification still accepted use-before-definition, duplicate order-token use and mismatched yield arity. These remain required Spatial-verifier checks; this probe does not implement them.

| Locked wheel | SHA-256 |
|---|---|
| `xdsl-0.1.dev1+g0b107461b.spatial1-py3-none-any.whl` | `7ba55df59ac1c85aaf7775526eb8cd95e72b89170c359fe461e0746b4f069183` |
| `immutabledict-4.3.1-py3-none-any.whl` | `c9facdc0ff30fdb8e35bd16532026cac472a549e182c94fa201b51b25e4bf7bf` |
| `ordered_set-4.1.0-py3-none-any.whl` | `046e1132c71fcf3330438a539928932caf51ddbc582496833e23de611de14562` |
| `packaging-25.0-py3-none-any.whl` | `29572ef2b1f17581046b3a2227d5c611fb25ec70ca1ba8554b24b0e69331a484` |
| `setuptools-84.0.0-py3-none-any.whl` | `51a52592b3b99e102b609654876bd65f19f999935166d1352678931132b0c670` |
| `setuptools_scm-9.2.2-py3-none-any.whl` | `30e8f84d2ab1ba7cb0e653429b179395d0c33775d54807fc5f1dd6671801aef7` |
| `typing_extensions-4.15.0-py3-none-any.whl` | `f0fa19c6845758ab08074a0cfa8b7aecb71c999ca73d62883bc25cc018c4e548` |

The standalone SpatialJSON mechanics probe matched a handwritten canonical-byte fixture and an independent OpenSSL SHA-256 result (`13b07ee2e432519e375b94547f2f901bca62214d4ac3871dab1b450f16e6ed3d` with its probe domain tag), rejected 18 malformed/type/decimal cases, round-tripped a 20,000-bit integer without changing process digit limits, preserved distinct Unicode spellings and UTF-8 spans, and checked an alias-preserving snapshot copy producing `[1,1,2,3]`. The probe covers format mechanics and selected boundary cases, not complete schema decoding, canonical graph numbering, cache publication or compiler correctness. Those algorithms are specified above and remain implementation tests.

The readiness evidence archive linked from [[07 - Python Implementation Readiness Audit]] contains the exact probe sources, results and reproduction instructions. Source inspection, packaging experiments and format tests establish these bounded claims only; no Python Spatial compiler, target code generator or vendor run was executed.
