---
type: deep-dive
title: "PY-R007 — Host workflow, reproducibility, and validation"
topic: python-host-workflow-and-validation
project: spatial-python
session: 2026-09-30
status: research-conclusion
source_files:
  - "spatial@e7a8f2f:test/spatial/tests/ee109/Lab1Part2DramSramExample.scala:6-43"
feeds_spec:
  - "[[10 - Python Language Contract]]"
  - "[[40 - Python Compiler and HLS Contract]]"
---

## Recommendation and evidence boundary

Use ordinary Python for host work and explicit captured source for accelerator programs. A host loads a template, specializes it with immutable configuration, checks it, then chooses reference execution or hardware compilation. Those actions use the same semantic program. File and notebook adapters supply the same source object; a notebook is not a second language.

This note proposes a workflow and acceptance plan. The original tiled example supplies the host/input/output use case at `spatial@e7a8f2f:test/spatial/tests/ee109/Lab1Part2DramSramExample.scala:6-43`. [[PY-R004 - Capture Composition and Diagnostics]] supplies the source/builder and diagnostic evidence. [[PY-R002 - Numeric and Reduction Semantics]] and [[PY-R003 - Control Memory and Effects]] supply proposed data and effect rules. No package, compiler, hardware driver, or latency benchmark is implemented here.

## One end-to-end workflow

All names in this sequence are illustrative. The API contract matters more than spelling.

| Step | Host action | Result and required boundary |
|---|---|---|
| Capture | Read a kernel file, receive a raw notebook cell, or accept generated source with origins | Immutable source/template bundle; no execution of captured decorators, annotations, or bodies |
| Specialize | Supply named sizes, type descriptors, and tuning parameters | Frozen meta inputs; runtime data is not an implicit meta constant |
| Check | Resolve names, types, scopes, initialization, effects, protocols, and invocation requirements | Checked semantic program or structured diagnostics; check success names a capability profile |
| Prepare | Bind typed scalar/buffer/stream inputs and allocate explicit outputs | Validated invocation; dimensions, alias relationships, formats, and persistence agree with the checked interface |
| Simulate | Select reference execution and an environment trace | Outputs, committed effects, terminal/wait/fault state, and replay metadata; no hardware timing claim |
| Compile | Select a target/tool profile and request an HLS project | Success returns an eligible emitted project with no unresolved required target obligations. Failure returns diagnostics and an inspectable incomplete plan, explicitly ineligible for emission/build reuse; generation alone is not hardware validation |
| Validate hardware | Run the separately configured vendor flow | Separate simulation, synthesis, resource, timing, and board evidence records |
| Reuse | Load a checked artifact or cached result | Verify schema, dependency/profile digests, and input contract before reuse |

The host may use Python libraries to load datasets, generate configurations, compare results, plot traces, and launch experiments. That computation takes place outside the captured kernel. Ordinary host library objects do not acquire accelerator meaning through implicit conversion. A source template cannot silently read a later notebook-variable value.

The initial command-line interface should mirror these stages: inspect/check, simulate, emit, and validate. Commands take the same manifest and return the same diagnostic records as the Python API. The implementation plan should introduce each command with its underlying feature, rather than build an empty command suite first.

## Invocation, buffers, and state

Proposed scalar ingress follows the exact numeric constructors in PY-R002. A Python integer, decimal string, rational, already-rounded binary float, and raw bit pattern are different input kinds. Validation records the selected conversion; an array library dtype is not permission to change a declared fixed format.

Use a versioned buffer descriptor: element format, rank/extents, byte strides, logical origin, byte order, backing-object identity, accessible range, and read/write capability. The core representation must work without NumPy. A NumPy adapter is an optional host convenience and must produce the same descriptor. Reject negative-stride or noncontiguous buffers in a profile that does not support them, or use an explicit copy whose cost and alias behavior are recorded. Never silently flatten away per-axis bounds.

Distinct port names are not proof of distinct memory. Preparation must validate the declared alias groups against actual backing ranges. If the program requires disjoint ports and receives overlapping views, it fails before starting. If aliasing is declared, memory/effect analysis preserves it. Snapshot copying is an explicit invocation mode; it must not change an accepted alias contract accidentally.

The default reference invocation owns an input snapshot and private output storage. Snapshot each declared backing allocation once and preserve all views into it; copying each port independently would incorrectly break accepted aliases. This prevents concurrent host mutation from changing the run and makes a failure report reproducible. A later zero-copy mode requires exclusive host ownership during execution and a documented failure/partial-write contract. This is an interface choice, not a claim that the hardware can roll back transactions.

Invocation-local state is fresh on every call. Persistent state requires an explicit session handle, state schema, reset operation, and serialization policy. Repeated invocation tests must distinguish a register allocated inside a loop, outside the loop, and in a persistent session. A live invocation has exclusive ownership of its session; unsupported concurrent use is diagnosed. Separate sessions can run independently.

An unsuccessful run returns no successful output result. Its trace can still contain earlier committed writes or consumes. Hardware output buffers may already contain partial updates after a device fault; the host must mark them incomplete. This matches the no-rollback effect contract rather than promising transactional hardware.

External stream environments provide offered tokens, readiness, end-of-input events, and any time assumptions as an explicit trace or adapter. Waiting for an open environment, closed-input exhaustion, deadlock, cancellation, and successful completion are different outcomes. A timeout is a host observation limit; it is not by itself proof of deadlock or nontermination.

## Packaging and dependency boundary

Recommend one installable Python package with a small semantic core and optional notebook, array, visualization, solver, and vendor-tool adapters. The source reader, checker, numeric semantics, transformations, and reference execution must be inspectable Python code. The Python interpreter and its standard library are permitted infrastructure; “pure Python compiler” does not require rewriting CPython. Native synthesis tools remain external backends.

Use `pyproject.toml` for package metadata, build requirements, and optional dependencies. These are the roles described by the [Python packaging specification](https://packaging.python.org/en/latest/specifications/pyproject-toml/) (accessed 2026-09-30). Choose the compiler-framework dependency in the architecture study; do not place both custom and framework-owned semantic IRs on equal footing indefinitely.

Pin and test supported Python minor versions. The official [AST documentation](https://docs.python.org/3.14/library/ast.html) explicitly notes that the grammar can change between Python releases (accessed 2026-09-30). Therefore convert the accepted host AST into a versioned Spatial surface representation and reject unknown syntax. Do not serialize Python AST objects or rely on pickle as the compiler interchange format. Record the parser/runtime version even when two supported versions produce the same Spatial program.

Optional native libraries must not become the authority for typing, effect legality, or numeric answers. A solver can return a proof/certificate that Python verifies, or suggest a candidate that the Python analyses independently check. An unavailable solver yields a diagnosed unresolved obligation; it must not silently accept unsafe lowering. A trusted native legality oracle would change the proposed semantic-ownership boundary and is not adopted here. Native reference tools may generate test vectors without becoming production semantic dependencies.

## Reproducible artifacts and diagnostics

Separate semantic identity from build identity. The checked semantic key uses canonical checked meaning, frozen meta bindings, DSL/numeric/protocol versions, resolved semantic dependencies, and semantically significant schedules or tree policies. An earlier acquisition cache also keys exact source/template content and parser versions; it is not the checked semantic key. The build key adds compiler/framework versions, optimization pipeline, target capability file, vendor release, libraries, constraints, and generated-file hashes. Ordinary runtime input data is a run key, not a reason to compile a different kernel unless explicitly specialized. Source and origin digests separately retain the exact diagnostic provenance even when two source forms have equal checked meaning.

Use deterministic ordering, explicit integer/bit encodings, canonical record serialization, and content digests. Paths and notebook display names belong to provenance; machine-specific absolute paths must not make identical semantic programs different. Keep source digests and mappings so errors still show the exact source revision that produced an artifact. A cache entry with a mismatched schema/profile is rejected or recompiled through an explicit migration, never guessed compatible.

Each diagnostic contains a stable code, phase, severity, primary span, related spans, explanation, and any proof/capability obligation. Distinguish invalid source, unsupported feature, unproved requirement, runtime fault, and vendor failure. Compiler crashes are defects and retain reproduction metadata; they must not be presented as user type errors. Plain text, notebook display, and structured output render the same record.

## Conformance plan

The implementation must pass tests of composition and variations, not a list of recognized whole programs. Use the initial three programs as a readable entry point, then expand across the coverage ledger.

| Layer | Independent evidence | Required adversarial cases |
|---|---|---|
| Capture and diagnostics | Saved source segments and hand-written expected labels | Unicode, multiline expressions, unsaved/edited cells, unavailable builder source, malformed graphs, no decorator/body execution |
| Numeric semantics | Hand calculations, exhaustive small formats, independently structured rational algorithms, standard-format oracle vectors | Width boundaries, negative rounding/division, NaN/signed zero/subnormals, literal trees, intermediate overflow, FMA, empty reductions |
| State and effects | Explicit event/state expectations and small transition models independent of optimizer code | Untaken consumes, alias writes, invalid tails, assignment order, repeated invocation, contribution side effects |
| Concurrent protocols | Exhaustive bounded interleavings or protocol transition exploration | Capacity-one channels, competing requests, feedback, cancellation with in-flight actions, closed/open environments, fairness assumptions |
| Transformations | Before/after checked-program interpretation plus structural invariants | Branch/fault preservation, CSE/DCE around consumes, memory versioning, reduction tree preservation, source-origin retention |
| Original migration | Pinned original traces, when executed, plus explicit divergence records | Constant/runtime disagreement, old fold grouping, elastic queues, invalid-memory behavior; no automatic “old simulator wins” rule |
| HLS | Generated-code, vendor simulation, RTL/protocol checks, synthesis reports, hardware where needed | Unsupported numeric primitive, missing channel/storage mapping, concurrency mismatch, requested versus achieved II |

Shared constant-folding and simulator arithmetic is useful but not an independent oracle. Likewise, simulating both sides of a transform with the same incorrect primitive may miss a defect. Keep independently derived bit vectors and effect traces at those boundaries. Randomized testing records generator version and seed, and minimizes failures into durable examples. Passing random examples is not a proof of associativity, race freedom, or liveness.

## Feedback-time targets fixed before benchmarking

These are proposed engineering acceptance targets, **not measurements or theoretical limits**. Reference machine: one contemporary development laptop, with exact CPU/RAM/OS/Python/framework versions recorded before the first run. Use an isolated single process; record cold process startup separately. Run at least 20 timed repetitions after five warmups and report median, p95, peak resident memory, and the complete workload generator parameters. Do not combine warm cache hits with uncached runs.

| Workload | Initial target | Purpose |
|---|---|---|
| Capture and semantic check of 1,000 operations, 20 regions, and 10 storage objects | Warm p95 ≤1 second; cold end-to-end ≤3 seconds | Edit/check interaction |
| Capture and semantic check of 10,000 operations, 200 regions, and 100 storage objects | Warm p95 ≤5 seconds; peak process memory ≤1 GiB | Mid-sized composed kernel |
| Capture/check/ordinary optimization of 100,000 operations with bounded-depth regions | ≤30 seconds and ≤4 GiB peak memory | Scaling alarm, not an interactive promise |
| Reference execution of 100,000 Int32 arithmetic/state events with trace collection disabled | ≤5 seconds | Useful functional feedback |
| Reference execution of 10,000 generic F32 arithmetic operations or 10,000 communicating-task transitions | ≤5 seconds each, measured separately | Expose exact-arithmetic and protocol interpreter cost |
| Structured diagnostic after one local edit in the 1,000-operation case | ≤1 second warm, including capture/check | User-facing error latency |

Count logical operations and trace events explicitly; iterations must not inflate a compile-time node count without explanation. Add a full-trace benchmark separately. Exclude vendor synthesis, package installation, and network download from compiler timing, while reporting their wall time in end-to-end workflow studies.

If a target fails, profile the relevant stage and improve data layout, worklists, analysis invalidation, caching, or interpreter dispatch. Reconsider framework choices only with attributed measurements. Do not change the language to recognize the benchmark or relax semantic checks to hit a time target. A target change requires a dated reason and preserved previous results.

## Migration and acceptance

Provide a migration guide by construct and example. Each entry states the original source behavior, proposed Python meaning, preserved case, changed case, and expected diagnostic or explicit replacement. The coverage ledger accounts for old runtime/codegen infrastructure that is replaced rather than ported. Do not build an automatic Scala translator before the language contract exists.

The first usable vertical slice must complete capture, checking, reference execution, diagnostics, and reproducible invocation for a small composed kernel. Later slices add full numeric/state/protocol families and hardware evidence. A parser-only milestone can be useful progress, but it is not language support. Professor approval of the detailed proposal is the boundary before production compiler work.

## Implementation-readiness supplement — 1 October 2026

[[40 - Package and Conformance Blueprint]] now defines public workflow signatures, module ownership, SpatialJSON-v1 artifact kinds (including unchecked input), canonical identities, exact buffer ABI/session rules, diagnostics and fixture schema. [[30 - State Simulator and HLS Blueprint]] adds resumable QuiescentUnknown and explicit source-visible address bindings. [[07 - Python Implementation Readiness Audit]] records method experiments and the still-unrun production/performance gates.
