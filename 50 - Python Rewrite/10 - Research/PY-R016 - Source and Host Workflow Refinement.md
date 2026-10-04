---
type: deep-dive
title: "PY-R016 — Source and host workflow refinement"
topic: python-source-and-host-workflow-refinement
project: spatial-python
scope: python-rewrite
session: 2026-10-03
status: research-conclusion
adoption_status: proposed
implementation_status: not-implemented
source_files: []
feeds_spec:
  - "[[10 - Python Language Contract]]"
  - "[[10 - Source Checker and IR Blueprint]]"
  - "[[40 - Package and Conformance Blueprint]]"
related:
  - "[[09 - Fable Design Review]]"
  - "[[PY-R004 - Capture Composition and Diagnostics]]"
  - "[[PY-R012 - Lab1 Syntax and Host Mapping]]"
---

# A complete proposed Python experience

## Question and evidence boundary

[judgment] The smallest coherent improvement is to keep the raw-source frontend, bind whole signatures before interpreting their dependent annotations, spell a type constant explicitly, and finish the ordinary Python host workflow. The professor already knows Spatial; the useful review artifact is a concrete program and launch sequence with visible stage boundaries. This proposal changes neither the Python-owned compiler/reference-simulator direction nor the later HLS boundary.

[measured] At the reviewed baseline, [[10 - Python Language Contract]] and [[PY-R004 - Capture Composition and Diagnostics]] prebind only meta formals, while [[60 - Course Syntax and Compiler Trace]] Trace 2 prebinds the entire GEMM signature. [[PY-R012 - Lab1 Syntax and Host Mapping]] supplies complete kernel source but labels its launch sequence record pseudocode; [[40 - Package and Conformance Blueprint]] names the stages without all constructors/decoders. [[09 - Fable Design Review]] identifies these as contract gaps. These are documentation findings, not failures of an implemented compiler.

[designed] This note supplies evidence and alternatives before the owning proposed documents are corrected. All registrations and API forms below remain proposed and unimplemented pending professor adoption. No kernel is imported or executed to obtain its source; syntactic validity and mock contract checks are not compiler conformance.

## Alternatives and selection

| Question | Alternative | Benefit | Cost and disposition |
|---|---|---|---|
| Dependent signatures | Require dimensions before memory ports | One-pass annotation lookup | Reorders existing course signatures for an incidental parser restriction; reject |
| Dependent signatures | Prebind every identity, permit arbitrary runtime expressions in annotations | Maximally flexible spelling | Stateful reads/calls make interface shape depend on execution order; reject |
| Dependent signatures | Prebind every formal identity; admit only closed immutable shape expressions | Keeps the course signatures and a stable invocation interface | Requires category validation after binding; **select** |
| Type aliases | Ordinary assignment `T = Int` | Familiar Python spelling | Ambiguous with forbidden executable top-level assignment and value bindings; reject |
| Type aliases | Python `type T = ...` / Python classes | Familiar Python typing machinery | New AST/type-parameter semantics and misleading host-type interpretation; defer |
| Type aliases | `T: Const[Type] = Int` | Reuses the existing Const/meta-descriptor path and states the stage | One explicit annotation; **select** |
| Host workflow | Only low-level byte/view records | Small implementation surface | The student must reconstruct every constructor and output decoder; insufficient |
| Host workflow | Import kernel and call `kernel.run(...)` | Familiar function-call experience | Violates raw-source acquisition unless a separate adapter states definition-time execution; defer |
| Host workflow | Existing five stages plus a few typed host constructors | Concrete source/input/run/output path and independent diagnostics | A small public data API must be frozen; **select** |

[judgment] Do not add implicit Index embedding, lambdas, arbitrary Python type evaluation, or mutable-local/SSA merging as part of this repair. Each would change a separate semantic boundary without being necessary for the complete lab workflow.

## Whole-signature binding without body forward references

[designed] For each kernel, helper or component, allocate deterministic identities for **all** formals in declared ABI order before resolving any annotation or result type. Recognize registered outer annotation categories, bind meta values, then validate type/shape dependencies. ID allocation is not permission to read every formal in every annotation. Reject duplicates, unresolved names, cyclic dependencies and category-ineligible references with both use/declaration origins.

[designed] A dependent logical extent may use exact integer literals/constants, `Meta[Size]`/`Meta[Integer]` formals, and immutable runtime `In[Index]` kernel ports or ordinary `Index` helper/component value formals. The spellings are definition-kind-specific: a kernel rejects bare Index as a non-port; a helper/component rejects launch In/Out/InOut annotations and uses value or borrowed-capability formals. Arithmetic is the closed pure structural expression grammar; no state read, effectful call, arbitrary method, Python evaluation or implicit accelerator-Int conversion occurs. Whole-signature prebinding also resolves meta type descriptors such as `T: Meta[Type]`, but runtime Index values cannot determine numeric widths or types, static expansion, or fixed resource capacities. Those slots remain meta-only.

```python
# Proposed source-only module. Identities for src and n exist before annotations.
@kernel
def copy(src: In[Dram[Int, n]], dst: Out[Dram[Int, n]], n: In[Index]):
    for i in foreach(0, n):
        dst[i] = src[i]
```

[designed] `prepare` validates n's exact structural input, nonnegative extent, buffer shape agreement and any declared bound before creating an invocation. Helper/component call entry snapshots its immutable Index arguments once and validates substituted shape obligations before body effects. A hardware plan additionally requires finite declared/proved bounds; a reference-valid dynamic shape does not establish target capacity.

[designed] Matched negatives: replacing `n: In[Index]` by `InOut[Index]`, `Out[Index]`, `In[Int]`, `Reg[Index]` or an endpoint makes it ineligible for a signature extent. This shape-category rejection does not forbid a private Index register in the body. `src.shape[0]` does not implicitly derive another formal's type. A negative runtime n fails preparation. In a body, `x: Int = y; y: Int = 1` still fails forward lookup; a nested helper cannot capture a later body-local runtime declaration. The builder binds the same explicit formal IDs and must pass the same dependency/category checker.

## Explicit type-valued constants

```python
# Proposed declarative source, not Python annotation evaluation.
T: Const[Type] = Fix[True, 16, 16]
N: Const[Size] = 32

@kernel
def scale(src: In[Dram[T, N]], gain: In[T], dst: Out[Dram[T, N]]):
    for i in foreach(0, N):
        dst[i] = src[i] * gain
```

[designed] `Type` is a meta-schema registration for a **value-type descriptor**, represented by the existing `meta.descriptor` tag. It is not Python's `type` or `typing.Type`. Its closed tags are the registered Bool, fixed, floating, Bits, Index, Unit, Vec, MaskedVec, Tuple and Record value descriptors and canonical aliases. Their recursive parameters use closed immutable schemas and exact numeric validation; registration/version/digest must match the frozen registry. Source lookup can use another acyclic type constant or `Meta[Type]`; no `getattr`, subclass conversion, callable, imported Python class or user descriptor hook runs.

[designed] Module constants may depend on other declared module constants with an acyclic evaluation graph, never a formal or body-local runtime value. Body-local `T: Const[Type] = ...` is an immutable meta declaration visible from that statement onward; it may use in-scope meta formals/constants, never runtime values. The existing collision/shadowing rules apply: nested value/meta shadowing needs an explicit annotated declaration; formals, live resources/endpoints, binders and registered intrinsics cannot be shadowed. An alias has no distinct nominal numeric type: it resolves to the canonical descriptor and preserves its own diagnostic origin.

[designed] Descriptor validity and use-site capability are separate. `T: Const[Type] = Index` is a valid structural descriptor, but `x: T = 1` is Index-valued and cannot enter ordinary Int arithmetic without `embed`. A registered memory/port slot validates its required storable/reference/target capability against the descriptor; it cannot assume every Type is Bits-capable. `Const[Type]` excludes storage/port/controller/profile/foreign-model descriptors even though those use other `meta.descriptor` schemas. `T: Const[Type] = Dram[Int,32]`, a negative Fix width, and `T: Const[Type] = make_type()` reject. This does not add arbitrary host type aliases.

[designed] The round-two review closes the remaining Type spellings: `M: Const[Type] = MaskedVec[4,Int]` is nameable but remains non-Bits until explicit materialization; `Packet: Const[Type] = Record(fields=(("count",Int),("valid",Bool)))` declares a closed structural user schema with unique source-identifier fields. No class or factory executes. An annotated Index initializer is explicitly an Index expression slot, so literal-only arithmetic there stays structural; typed accelerator expressions keep their original arithmetic before any admitted index projection. [[10 - Source Checker and IR Blueprint]] owns the exact constructor/capability rules and negative cases.

[designed] Round three makes storage capabilities explicit without replacing them by a blanket Bits requirement. The existing reference ValueStorage union supplies private Reg/RegFile/Sram typed cells, including exact Index and MaskedVec payload/validity. ZeroImage(Index) is exact mathematical zero; ZeroImage(MaskedVec(N,T)) has all lanes invalid and recursively registered zero payloads. Reading that initialized register returns a masked value, not readable inactive lanes. SRAM still begins uninitialized. Byte-backed Dram/Backing and packed queue/ABI slots require Bits; use explicit Index embedding or masked materialization for those slots. In[Index] keeps its structural IndexInput route. A finite hardware realization additionally requires sound Index range/invariant and mask-preserving layout evidence; absent evidence is a target capability diagnostic, never implicit wrapping or mask erasure. This is a proposed capability clarification, not implemented storage support.

[designed] Output initialization belongs to the backing owner, not its port direction. A partially written Out view over Backing.empty fails completion with HOST.OUTPUT_UNINITIALIZED; the same selected view over an initialized owner may complete with untouched cells preserved, although Out still forbids kernel reads. InOut is required when the kernel reads old cells. A selected view with zero logical cells satisfies its buffer initialization check vacuously; a zero-bit element in a nonempty view still requires initialization. This is an explicit proposed initialized-output policy, not a claim about every original Spatial hardware route.

[designed] Acquisition enforces UTF-8 source-byte budgets before parsing/tokenization, fixes `feature_version=(3,14)` under the CPython 3.14.5 baseline, and maps expected syntax/content/recursion/recoverable allocation errors to SOURCE diagnostics. A byte-admitted deeply parenthesized input may raise SyntaxError instead of RecursionError; actual process OOM is not promised recoverable. These limits do not make arbitrary host source-generation code a sandbox.

## Small public host construction contract

[designed] The owning API is [[40 - Package and Conformance Blueprint]]. The chosen conveniences construct the same explicit frozen data records already required there. They live in the ordinary host package `spatial`; importing that package does not import a captured kernel. All names in the following table are public proposals, not existing library objects.

| Public form | Exact boundary |
|---|---|
| `SourceUnit(module_id=..., text=..., label=...)` | Exact builtin strings; freeze UTF-8 text, digest and line map; label is diagnostic display text, not a source location claim or module to import; exact spans are derived from acquired text |
| `core_prelude()` | Return the installed immutable core registry descriptor, including version and digest; bundle/artifacts retain that exact choice |
| `CaptureBundle(entry=(module_id, export), sources=(unit,...), dependencies=(), prelude=...)` | Finite immutable source/dependency snapshot; entry resolves an export; missing dependencies reject rather than import |
| `ScalarInput.from_int(dtype=Int, value=3)` | Exact builtin integer in an integral fixed type's range; no Bool, float, subclass conversion, wrap or saturation; freeze canonical typed bits |
| `IndexInput(value=32)` | Exact builtin structural integer, frozen without hardware-bit conversion; preparation validates the port and its nonnegative extent/bound obligations |
| `Backing.from_ints(name=..., dtype=Int, shape=(32,), values=tuple(...))` | Exact tuple of exact integers; count equals product of nonnegative extents; validate range and freeze row-major little-endian slots; every logical cell initially initialized |
| `Backing.empty(name=..., dtype=Int, shape=(32,))` | Typed owned allocation; physical zero bytes, **no initialized logical cells** |
| `backing.view(access="read" / "write" / "readwrite")` | Whole-owner contiguous BufferView with explicit byte and logical coordinate maps, shape, format and capability; aliases retain owner identity |
| `Environment.closed_memory()` | Frozen deterministic local-memory environment; no unprovided stream/device/foreign events; incompatible environment requirements reject |
| `Budget(steps=..., numeric_work=..., trace_bytes=..., numeric_limits=None)` | Nonnegative exact administrative counters plus optional typed ReferenceBudget override; snapshot all selected numeric sublimits. Aggregate/per-helper limits map to BudgetExhausted with a retained continuation, never successful output |
| `run.complete_outputs[name].to_int()` / `.to_ints()` | Scalar or row-major buffer decoder for completed integral fixed output; exact integers, with dtype/shape available on the immutable output record |

[designed] The integral constructors/decoders are deliberately narrow convenience functions; the general typed-bits and BufferView record routes remain available for other formats and views. A supplied Python list/generator is not implicitly iterated by these closed constructors; the host explicitly makes the tuple. Logical initialization and alias identity belong to the backing, not the view or physical zero-fill. Two separate backing objects using the same name are an error in one preparation registry; making two views of one backing preserves aliasing.

[designed] Uniform Result returns for all five stages would be a reasonable larger API revision. This refinement preserves the already specified direct-return acquisition/specialization signatures and Ok/Error check/preparation signatures to avoid changing every caller while closing the constructor gap. The asymmetry is deliberate and confined to these public boundaries: `capture` and `specialize` retain direct successful returns; expected source/specialization failure raises the public `DiagnosticError` carrying immutable diagnostics and no candidate Template/Program. Invalid constructor arguments use the same exception with `HOST.INVALID_ARGUMENT`. `check` and `prepare` retain `Ok`/`Error`; simulator terminal outcomes remain `RunResult`. Unexpected compiler exceptions become the separately classified CompilerFailure. There is no implicit `.unwrap()` or launch on construction.

## Complete proposed host program

[designed] Save the unchanged E1 `tiled_scale` listing from R012 as `lab1.py`. The following is **syntactically valid proposed ordinary Python**, not record pseudocode and not executable against an existing Spatial package. Every Spatial name it uses is specified above or in the package blueprint. The source file is read as text and is never imported. A source/argument exception terminates this script with its structured diagnostics; failed Result stages terminate before launch. The illustrative budget is not a measured interpreter bound.

```python
from pathlib import Path
from spatial import (
    Int, SourceUnit, CaptureBundle, core_prelude, capture, specialize,
    check, prepare, simulate, Error, ScalarInput, Backing, Environment, Budget,
)

unit = SourceUnit(
    module_id="lab1", text=Path("lab1.py").read_text(encoding="utf-8"),
    label="lab1.py",
)
bundle = CaptureBundle(
    entry=("lab1", "tiled_scale"), sources=(unit,), dependencies=(),
    prelude=core_prelude(),
)
template = capture(bundle)
program = specialize(template, {})
checked_result = check(program, profile="reference.guarded.v1")
if isinstance(checked_result, Error):
    raise RuntimeError(checked_result.diagnostics)
checked = checked_result.value

values = tuple(i % 256 for i in range(32))
src = Backing.from_ints(name="input", dtype=Int, shape=(32,), values=values)
dst = Backing.empty(name="output", dtype=Int, shape=(32,))
bindings = {
    "src": src.view(access="read"),
    "scale": ScalarInput.from_int(dtype=Int, value=2),
    "dst": dst.view(access="write"),
}
prepared_result = prepare(checked, bindings, session=None)
if isinstance(prepared_result, Error):
    raise RuntimeError(prepared_result.diagnostics)
run = simulate(
    prepared_result.value, environment=Environment.closed_memory(),
    budget=Budget(steps=100_000, numeric_work=100_000, trace_bytes=1_048_576),
)
if run.outcome != "Completed":
    raise RuntimeError((run.outcome, run.diagnostics, run.run_identity))
output = run.complete_outputs["dst"]
assert output.dtype == Int and output.shape == (32,)
got = output.to_ints()
gold = tuple(((x * 2 + (1 << 31)) % (1 << 32)) - (1 << 31) for x in values)
assert got == gold
print("PASS", run.run_identity)
```

[designed] `Completed` is the closed successful outcome name for this public API. Only declared Out/InOut ports appear in `complete_outputs`, as immutable completed snapshots in logical order. A completed buffer exposes dtype and shape and its decoder reads the snapshot, not the original `dst` object: default reference preparation copied backing storage. A fault, cancellation, observation pause or budget result has `complete_outputs=None`, with no complete output map to decode. Raw committed partial state remains inspectable separately.

[designed] For scalar addition, select entry `("lab1", "scalar_add")` from the R012 scalar module, keep the same five stages and use bindings `{"a": ScalarInput.from_int(dtype=Int,value=3), "b": ScalarInput.from_int(dtype=Int,value=5)}`. A scalar `Out[Int]` has no seed/binding entry. After `Completed`, `run.complete_outputs["result"].to_int()` must equal 8. Duplicate/unknown/missing input names and attempts to bind a scalar output reject before launch.

[designed] A distinguishing host failure is `Backing.empty(name="wrong",dtype=Int,shape=(31,))` bound to tiled_scale's dst. Its constructor succeeds, but `prepare` returns `Error` with `HOST.SHAPE_MISMATCH`, primary port `dst`, expected `(32,)`, actual `(31,)`, and the source declaration as a related origin. Supplying `value=1 << 31` to the Int scalar constructor instead raises `DiagnosticError(HOST.INVALID_ARGUMENT)` before `prepare`. Neither is silently truncated, wrapped or treated as a successful run.

## Bounded validation and remaining implementation gate

[designed] Acceptance cases are: later eligible shape formal versus later mutable shape formal; type alias versus resource descriptor/callback/invalid width; body forward reference versus signature forward reference; ordinary host source read versus poisoned definition-time execution; complete scalar/buffer output versus fault or wrong-shape binding. The builder must reuse the same checked identity/category rules when implemented.

[designed] The bounded research probe parses the proposed source and host listings without importing them, checks a small declarative formal/type schema, and checks typed packing/shape/output gating with mock records. It must not implement a fake `capture`/`simulate` that computes the expected fixture and call that compiler evidence. Independent oracle values are `(8,496,497)` and the 32-cell scale sequence; the mock is limited to record construction and terminal-result inspection.

[judgment] Working support still requires the real source checker, canonical descriptors, alias-preserving preparation and reference interpreter, with source/builder differential fixtures and independent outputs. The current refinement removes specific documentation ambiguities; it does not validate those future components.

[measured] On 2026-10-03, the initial standalone standard-library probe ran under CPython 3.14.5 and passed **48 bounded checks**. It parsed all **12 Python blocks** in R012/R016 without importing or executing their source; exercised whole-signature identity allocation and eligible/ineligible extent inputs in a deliberately small header model; distinguished body statement order; validated closed scalar/Vec descriptor data and use-site Bits capability; rejected poison objects without invoking hooks; checked 128-byte Int32 packing, owner-sharing between snapshot views, uninitialized zero-filled outputs, wrong shape and scalar range; and refused completed-output inspection for five incomplete outcomes. Explicit scalar/memory output fixtures tested decoding only. No capture/check/prepare/simulate implementation, dynamic-shape evaluator, full type registry, builder frontend or HLS route was exercised. The probe source and JSON result are retained with this refinement's research evidence.

[measured] The second review exposed a gap in that initial mock: it did not distinguish kernel and helper definition kinds for Index formals. The corrected header model passes **51 checks**, including the complementary kernel-bare-Index and helper-In[Index] rejections and a component positive case. A separate **55-check** probe exercises the newly specified MaskedVec/Record/Index contexts, real CPython preparse-byte/grammar behavior, injected parser failure classification, the exact RunResult payload matrix, retained checkpoint state across aggregate/per-helper budget limits, and a zero-byte/logical-state resource discriminator. Injected MemoryError classification is not a real OOM-recovery test. The pause fixture has two hand-declared transitions and no source program, compiler or public simulate shim. These remain bounded schema/AST/mock-state evidence, not working Spatial support.

[measured] The third-round storage clarification has **26 bounded typed-cell/capability checks** under CPython 3.14.5: exact Index increments across 2**31 and 2**32, all-invalid masked reset and retained extraction guards after a model store/load, explicit materialization, packed-slot negatives for Index/MaskedVec including nesting, and toy finite-range/mask-layout acceptance/rejection. A forever increment with only an initial bound rejects the toy target gate. These are small independent data/transition models, not compiler, reference-simulator or target-lowering tests.
