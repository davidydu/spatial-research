---
type: deep-dive
title: "PY-R004 — Capture, composition, and diagnostics"
topic: python-capture-composition-diagnostics
project: spatial-python
session: 2026-09-30
status: research-conclusion
source_files:
  - "exo@defe172:src/exo/API.py:35-49"
  - "exo@defe172:src/exo/frontend/pyparser.py:37-90"
  - "exo@defe172:src/exo/frontend/pyparser.py:172-202"
  - "exo@defe172:src/exo/frontend/pyparser.py:678-738"
  - "exo@defe172:src/exo/frontend/pyparser.py:1215-1252"
  - "exo@defe172:src/exo/frontend/pyparser.py:1296-1312"
  - "exo@defe172:tests/test_metaprogramming.py:11-45"
  - "allo@094ab41:allo/ir/utils.py:31-98"
  - "allo@094ab41:allo/ir/utils.py:144-161"
  - "allo@094ab41:allo/customize.py:1332-1382"
  - "calyx@d6bcdc8:calyx-py/calyx/py_ast.py:56-109"
  - "calyx@d6bcdc8:calyx-py/calyx/builder.py:1700-1707"
  - "amaranth@90449f1:amaranth/hdl/_ast.py:627-639"
  - "spatial-rs@eb49d8b:docs/language-spec.md:831-837"
feeds_spec:
  - "[[10 - Python Language Contract]]"
---

## Question, conclusion, and authority

[judgment] Recommend **source capture as the first public kernel surface**, with immutable file/cell source, explicit compile-time bindings, and a common Python semantic checker. Keep an explicit builder capable of constructing the same programs for generators and compiler tooling; decide the size of its public API separately. This recommendation is about the relationship between written programs, staging, and diagnostics. It does not select a Rust core, depend on scarce maintenance skill, or infer learning outcomes from syntax length. Both alternatives here own their semantic compiler in Python.

[designed] This is a research proposal for PY-Q001, PY-Q004, PY-Q005, PY-Q006, and PY-Q011 in [[02 - Python Open Questions]]. Neither surface is adopted. All API names and errors below are illustrative and unimplemented. [[D-27]] settles the Python direction; it does not authorize this staging boundary or diagnostic architecture. [[PY-R001 - Programming Model Study]] supplies the three initial equal-semantic programs; this note supplies the previously missing acquisition, composition, and failure contracts without rewriting those examples.

[judgment] The strongest objection is that an explicit builder fits arbitrary host program generation more directly. Source-first users must learn that a kernel file or cell is a compiler input, and general Python computation belongs outside it. A rich quotation language could reduce that friction, but would expand the staging semantics and complicate the promise that capture has no incidental execution. This objection is substantial; a generator-heavy workload could justify a builder-first decision. No workload distribution or learner evidence has been measured here.

## Evidence boundaries

| Class | Evidence used | What it establishes |
|---|---|---|
| Original Spatial | [[PY-E001 - Initial Example Corpus]] and the pinned source readings in [[PY-R001 - Programming Model Study]] | Starting programs and source-derived expectations; this note adds no original-compiler execution result |
| Current semantic studies | [[PY-R002 - Numeric and Reduction Semantics]] and [[PY-R003 - Control Memory and Effects]] | Source-grounded candidate numeric, reduction, memory, controller, and effect contracts; proposed rather than adopted |
| Earlier surface study | [[10 - Python Controller Bodies]], [[20 - Python If Expressions]], [[30 - Python Assignment]], [[90 - Python Naming and Scoping]], [[B0 - Python Literal Typing]], [[D0 - Python Declaration Order]] | Previously identified representation hazards; old Rust scope, literal, proof-order, and effect policies remain candidates to reconsider |
| Pinned precedent | Source ranges below, resolved through [[reference-clones]] | Concrete acquisition, metaprogramming, region, and location mechanisms; not Spatial semantic conformance |
| Official Python/IPython documentation | Versioned Python 3.14 pages and IPython's documented cell-magic interface, accessed 2026-09-30 | Host-language behavior and raw materials for adapters |
| Isolated execution | The AST/literal probe reproduced at the end | Behavior of local CPython 3.14.5 on one short snippet |
| Proposed design | All candidate contracts, programs, diagnostic records, and repairs below | Reviewable alternatives; no implemented compiler, simulator, learner study, or HLS result |

## What the precedents actually show

[source-inspected] These claims are from pinned source inspection, not running the projects. Each comparison separates the demonstrated mechanism from the policy proposed for Spatial.

| Precedent | Verified mechanism | Consequence and limit |
|---|---|---|
| Exo acquisition | `proc` receives a Python function, obtains its AST, passes source information and a parent scope to the parser, and constructs a `Procedure`: `exo@defe172:src/exo/API.py:35-49`. Its function-source path uses `inspect.getsource`, dedents, parses, and records offsets: `exo@defe172:src/exo/frontend/pyparser.py:73-90`. | A real decorator-based source frontend exists. This particular acquisition path starts from an already defined function; it does not establish a no-execution file/cell contract. |
| Exo source locations and lexical regions | `SourceInfo` maps start and end offsets back to original source: `exo@defe172:src/exo/frontend/pyparser.py:37-65`. Its loop parser pushes/pops a local environment, and its two `if` arms each receive a separate environment: `exo@defe172:src/exo/frontend/pyparser.py:1215-1252`. | Source capture can retain locations and construct DSL lexical scopes. Neither mechanism automatically adopts the earlier Rust shadowing or definite-assignment policy. |
| Exo composition and host quotation | Test source contains host `range` and conditionals inside `with python`, inserting statements through `with exo`: `exo@defe172:tests/test_metaprogramming.py:11-45`. Another test captures statement fragments and inserts a selected fragment twice: `exo@defe172:tests/test_metaprogramming.py:329-345`. The unquote machinery executes constructed host code: `exo@defe172:src/exo/frontend/pyparser.py:432-445`, `exo@defe172:src/exo/frontend/pyparser.py:570-587`. Procedure calls become `UAST.Call` after checking the called object: `exo@defe172:src/exo/frontend/pyparser.py:1296-1312`. | AST capture does not imply an inability to generate or compose code. Exo's explicit host stages are a stronger metaprogramming design than the restricted specialization recommended here, with a different execution boundary. The tests were not run in this study. |
| Allo string acquisition and environments | `parse_ast` accepts a string directly; the alternate callable route uses `inspect.getsourcelines`: `allo@094ab41:allo/ir/utils.py:144-161`. `customize` accepts callable/string and optional `global_vars`, then performs type inference before IR construction: `allo@094ab41:allo/customize.py:1332-1386`. Its environment helper copies function globals, visits outer frames, and reads closure cells: `allo@094ab41:allo/ir/utils.py:31-98`. | Callable introspection is not the only source-acquisition route. Environment discovery is an actual design choice, rather than a requirement of Python capture. Spatial can instead require explicit bindings. These sources do not show an immutable notebook provenance contract. |
| Calyx builder structure and locations | Explicit width/value constants exist: `calyx@d6bcdc8:calyx-py/calyx/builder.py:1700-1707`. Ordered control uses lists or `seq`: `calyx@d6bcdc8:calyx-py/calyx/builder.py:1108-1141`, `calyx@d6bcdc8:calyx-py/calyx/builder.py:1757-1766`. Its position table scans for an external construction frame and registers filename/line: `calyx@d6bcdc8:calyx-py/calyx/py_ast.py:56-109`. | A builder can preserve explicit types, order, and useful locations. This locator stores a file/line pair, not a complete expression span or every generator origin. Calyx's compiler architecture does not determine Spatial's implementation language. |
| Amaranth truth conversion | Symbolic `Value.__bool__` always raises: `amaranth@90449f1:amaranth/hdl/_ast.py:627-639`. | A builder can guard accidental Python truth selection. This does not inspect arbitrary host control or stop general host actions during construction. |

[documented] Python AST nodes expose start/end locations with UTF-8 byte columns; end positions can be absent. `Constant.value` is the represented Python object. `ast.parse` does not perform scoping checks, and `ast.unparse` need not reproduce the input spelling. These are reasons to retain source alongside AST and implement DSL resolution separately. [Python 3.14 AST](https://docs.python.org/3.14/library/ast.html#ast.AST), [parse](https://docs.python.org/3.14/library/ast.html#ast.parse), [unparse](https://docs.python.org/3.14/library/ast.html#ast.unparse) (accessed 2026-09-30).

[documented] Under ordinary Python execution, defining a function evaluates/applies its decorators, while the body waits until a call. Python 3.14 annotations are lazy by default, so it is inaccurate to claim that every annotation executes at definition time. Introspection can nevertheless execute annotation code. A source-as-data path avoids both mechanisms rather than relying on annotation timing. [Python function definitions and annotations](https://docs.python.org/3.14/reference/compound_stmts.html#function-definitions), [inspect annotation caution](https://docs.python.org/3.14/library/inspect.html#inspect.get_annotations) (accessed 2026-09-30).

## Common semantic contract for the comparison

[designed] Both frontends must describe the same ordered region program. The common contract in this note is deliberately narrower than a final language specification:

1. Runtime loop domains, branches, storage operations, and helper returns become compiler-owned objects. Capture/construction does not run their represented trip counts or consume a physical/software FIFO.
2. Runtime `if` preserves two regions. Reference execution selects one region; the other performs no read, write, or consuming FIFO operation. Pure selection and effectful branch execution are separate operations.
3. Scalar type compatibility is explicit. `Int` and `FixPt[Signed, 24, 8]` are distinct types for the incompatible-use case; no implicit conversion resolves their addition. [[PY-R002 - Numeric and Reduction Semantics]] now supplies the candidate explicit widths, per-operation normalization, exact ingress, and reduction-topology contract for PY-Q003. Use that study's proposed contract for both surfaces rather than deriving a different numeric rule from their syntax; adoption remains pending.
4. Local SRAM begins uninitialized, whereas a freshly allocated FIFO begins empty under the illustrative sequential reference model. Reading an unwritten SRAM element rejects in the constant-index example below. Unknown dynamic initialization requires a later specified proof/guard policy.
5. Runtime regions have lexical ownership. A declaration in a branch is not visible outside it. A loop index, local memory/view, pending effect expression, or helper-local value cannot escape its owning region merely because a Python object still exists.
6. Ordered attachment determines semantic declaration/effect order. Allocating a Python wrapper does not assign normative proof order. The older greatest-ID proof algorithm is not adopted here.
7. Helpers have typed parameters and explicit effect intent. Checking derives actual effects; a claimed `pure` helper containing a dequeue rejects. All runtime branches are checked, including those untaken by a particular runtime input.
8. Ordinary captured assignment evaluates RHS effects before target-address/index effects, then checks/commits the write. Augmented assignment is a separate read-modify-write form with a target evaluated once and read before RHS effects. The builder expresses the same sequence through explicit temporaries; no old target-before-RHS convention is inherited silently.

[judgment] These are comparison assumptions and recommended boundaries, not new descriptions of every original Spatial program. [[PY-R003 - Control Memory and Effects]] now supplies the source-grounded E3 effect review, ordered exactly-once contribution proposal, and distinction between functional execution and scheduled communicating hardware. [[PY-R002 - Numeric and Reduction Semantics]] supplies the corresponding numeric/reduction proposal. Their identified original-path disagreements and remaining evidence limits remain visible; a surface preference adopts neither contract by itself.

## Acquisition and staging: a concrete candidate contract

### Immutable source units

[designed] A `SourceUnit` stores source text/encoding, a stable source identity, content digest, line starts, and an optional origin map. A `CaptureBundle` stores those units, the entry name, declarative module dependencies, a grammar/profile version, and explicit meta bindings. The acquisition result is a **template**, not an executable Python function. Specialization must supply any missing meta parameters before a checked program can exist.

[designed] Files use a dedicated source-only module: the compiler reads it and its declared DSL-library dependencies as text. It does not import that module, instantiate its annotation objects, call default expressions, apply decorators, or call a kernel/helper body. `@kernel` and recognized `@helper(...)` forms are syntax markers interpreted by the compiler. Unsupported decorators, annotation calls, top-level host statements, or dynamic imports produce a surface diagnostic without evaluating them. Declarative imports refer to a resolved source module/manifest, not ordinary Python module execution. A mixed host/kernel file is outside this initial contract; put ordinary host work in a host module and pass its explicit results.

[designed] Illustrative host entry points are `Capture.file("tiles.py", entry="tiled_scale")` and `Capture.text(text, source_id="generated:tiles", entry="tiled_scale", origins=map)`. Only the host calls these APIs. A displayed `@kernel` function is never sent through ordinary Python definition execution in this route. An optional future callable/decorator adapter would be a separate contract, and could not claim retroactively that already executed decorator/default/annotation work had never occurred.

[documented] `inspect.getsource` can fail when source cannot be retrieved; its contract does not guarantee notebook capture. [Python inspect source retrieval](https://docs.python.org/3.14/library/inspect.html#inspect.getsource) (accessed 2026-09-30). This limitation motivates the explicit text route; it does not prove that notebook source is unavailable.

### Notebook source without function introspection

[designed] Recommend a cell adapter such as `%%spatial --module tiles --entry tiled_scale --bind config`. The installed adapter receives the raw cell body, captures it as a `SourceUnit`, and returns template/program objects to the host namespace. It must not forward the kernel cell body to ordinary execution. The magic header is excluded from the DSL source with a recorded line map. Each capture records notebook identity, stable cell identity when available, capture revision, raw body digest, and a display label. An unsaved cell gets a session-local immutable ID rather than an invented persistent notebook ID.

[documented] IPython documents cell-magics as callbacks receiving `line` and `cell`; the extension itself chooses what to do with those arguments. [Defining custom magics](https://ipython.readthedocs.io/en/stable/config/custommagics.html) (accessed 2026-09-30). This is sufficient precedent for passing cell text to a compiler. A Spatial magic, source registry, and editor-link protocol have not been implemented.

[designed] The same source manager can read a selected code cell from a saved notebook as text, without executing other cells, or receive text through an editor adapter. Explicit `Capture.text(...)` works without a notebook extension. Do not reconstruct source from `inspect.getsource`, bytecode, execution counts, or a current mutable history entry when original cell text is already available. A kernel-cell re-execution creates a new revision. Existing program objects retain their old text and meta snapshot; later host-variable or cell edits cannot silently change them.

### Host values, closures, and restricted specialization

[documented] A Python function's `__globals__` refers to its module-global dictionary; `__closure__` contains cells for its code object's free variables, whose contents can change. These are live host bindings rather than an immutable compile artifact. [Python function attributes](https://docs.python.org/3.14/reference/datamodel.html#user-defined-functions) (accessed 2026-09-30).

[designed] The proposed source route creates no Python function, so it has no Python closure to inspect. A nested DSL helper may capture surrounding **DSL** symbol identities, including memory handles, subject to region lifetime and effect checks. External source names must resolve to a declared source constant, a meta parameter, a registered intrinsic/type/helper, or a named frozen binding. Undeclared globals reject with the unresolved-name location and a suggestion to add a port or meta binding. Neither the current host stack nor the entire notebook namespace is implicitly captured.

[designed] `Meta[Size]`, `Meta[Bool]`, and registered numeric/type descriptors distinguish compile-time choices from runtime ports such as `In[Int]`. Freeze explicit bindings when specializing: accept a closed schema of builtin integers/booleans/strings, exact decimal records, immutable tuples/records, and registered DSL descriptors. Use exact type checks where booleans and integers have different meanings. Reject arbitrary user objects, live buffers, callables, descriptors, and mutable containers as meta inputs. Do not try arbitrary deep copying, conversion hooks, or annotation evaluation to turn them into constants. Runtime arrays and scalars go through typed host ports, with their own later execution contract.

[designed] The 2026-10-03 refinement in [[PY-R016 - Source and Host Workflow Refinement]] supersedes this note's earlier meta-only prebinding rule. Allocate **all signature formal identities** in ABI order before resolving dependent annotations, then validate each stage/category and dependency. N/TILE meta formals and an immutable `n: In[Index]` may therefore appear after `src: In[Dram[Int,n]]`. Eligible extent inputs are exact integer constants, Meta[Size]/Meta[Integer], immutable In[Index], and helper/component Index value formals; mutable/output/storage/endpoint values and ordinary In[Int] are ineligible. Specialization binds meta values; preparation/call entry snapshots runtime shape arguments and validates extents/bounds before body effects. Type widths, fixed capacities and static expansion remain meta-only. Duplicates, cyclic dependencies and unknown names reject. The source/builder checker shares this rule; ordinary body declarations still bind in statement order.

[designed] Type-valued constants have an explicit spelling: `T: Const[Type] = Fix[True,16,16]`. The existing meta.descriptor schema admits only recursively checked registered value-type descriptors in a Type slot, with each use-site capability checked separately. Module constant dependencies must be acyclic; body-local type constants use in-scope meta data and bind from their declaration onward. Runtime-dependent types, resource/profile/port descriptors, arbitrary Python classes and callable factories reject without execution. This is a narrow source registration, not general Python type evaluation; the source blueprint owns its complete rule.

[designed] Specialization has a compiler-owned evaluator over the meta AST: exact integer arithmetic, boolean operations/comparisons, registered type/shape constructors, and bounded explicit static choices/expansion. For example, `if static(FAST):` is a compile-time branch and `for lane in static_range(LANES):` is compile-time expansion; plain `if flag:` and `foreach` remain represented runtime control. Neither intrinsic calls arbitrary Python. File/network access, arbitrary method calls, host callbacks, implicit truth conversion of runtime values, and evaluation of unknown names are outside this evaluator. Division-by-zero, an unbound meta name, and excessive expansion have diagnostics at the meta expression and the binding/instantiation that supplied it.

[designed] Validate the supported source syntax before specialization, including statically discarded branches; unknown host escapes must not disappear behind a static condition. Type/effect checks apply to the specialized program, while both sides of a runtime branch survive. Static dead branches may disappear from that program. Frozen inputs, compiler/profile version, source/dependency digests, and deterministic expansion order identify a specialization. No artifact key relies on Python object identity or a process-randomized hash.

[designed] General computation remains ordinary host Python outside the captured unit. A host generator may compute a configuration, write/construct a `SourceUnit` with origins, or request builder nodes. Its execution is intentional and distinct from capture and represented runtime execution. No general host-execution sandbox, purity proof, or automatic dependency discovery is claimed by this boundary.

### The strongest builder under the same contract

[designed] A builder runs ordinary Python **construction** code. Host loops and conditionals may generate program structure; `k.foreach`, `k.if_else`, and reduction contexts record symbolic regions once. Closing a context closes construction, not represented execution. Operators build literal/expression trees and handles retain declaration, backing-object, and region identities. `finish()` freezes an unchecked program; `check(...)` independently returns a checked program or diagnostics. A source template ultimately produces the same unchecked representation.

[designed] The builder can take the same frozen meta bindings and type descriptors, construct first-class reusable helper templates, and use explicit exact literals. It has no need to introspect function annotations or execute captured decorators. Ordinary Python imports, factory calls, decorators on host factories, and arbitrary work written inside its construction blocks execute under ordinary host semantics. Those actions are intentional host execution in this surface; the semantic checker cannot undo them or prove host-generator purity. A runtime-value `__bool__`, `__int__`, or iteration conversion must reject rather than silently select or expand a hardware path.

[designed] Region ownership is checked even when Python keeps a handle alive. Builder host rebinding changes which handle a subsequent constructor receives; it does not rename or mutate an existing DSL declaration. Explicit declarations and ordered region attachment establish identities. The common checker must verify all resulting structure and effects, rather than trusting a Python constructor because it returned an object.

## Reuse, composition, and generated kernel families

### One shared helper, one kernel, two equal-semantic spellings

[designed] The following extends E1 only by factoring scalar multiplication into an acyclic pure helper and replacing its fixed dimensions with explicit meta parameters. Specialize with `N=32`, `TILE=16`. Both forms retain two local SRAM tiles and the same ordered load/compute/store regions. Apply the candidate `Int` contract in [[PY-R002 - Numeric and Reduction Semantics]] equally to both; factoring introduces no separate numeric policy. The helper's body is represented once as a definition and calls reference that definition; compilation may later inline it while preserving origins. This listing is not an executed compiler example.

```python
# Source-only tiles.py: captured as text, never imported as host Python.
@helper(effects="pure")
def scaled(x: Int, gain: Int) -> Int:
    return x * gain

@kernel
def tiled_scale(src: In[Dram[Int, N]], gain: In[Int],
                dst: Out[Dram[Int, N]], N: Meta[Size], TILE: Meta[Size]):
    for base in sequential(0, N, step=TILE):
        tile_in: Sram[Int, TILE]
        tile_out: Sram[Int, TILE]
        load(tile_in, src[base:base + TILE])
        for i in foreach(0, TILE):
            tile_out[i] = scaled(tile_in[i], gain)
        store(dst[base:base + TILE], tile_out)
```

```python
# Builder construction: runs once in host Python; no represented tile executes.
h = Helper("scaled", effects="pure")
x = h.param("x", Int)
g = h.param("gain", Int)
h.return_(x * g)
scaled = h.finish()

def make_tiled_scale(meta):
    N, TILE = meta.size("N"), meta.size("TILE")
    k = Kernel("tiled_scale", meta=meta)
    src = k.input_memory("src", Int, N)
    gain = k.input_scalar("gain", Int)
    dst = k.output_memory("dst", Int, N)
    with k.sequential(0, N, step=TILE) as base:
        tile_in = k.sram(Int, TILE)
        tile_out = k.sram(Int, TILE)
        k.load(tile_in, src[base:base + TILE])
        with k.foreach(0, TILE) as i:
            tile_out.at(i).write(k.call(scaled, tile_in[i], gain))
        k.store(dst[base:base + TILE], tile_out)
    return k.finish()
```

[designed] The builder factory is a host function and executes to generate nodes. Its `scaled` object is a DSL helper template, not an arbitrary callback the checker calls numerically. Source helper calls also resolve to template IDs, not Python invocation. A source-library import can register a helper from another source unit; a builder can register the corresponding helper object from a library registry. Registration identifies the module revision/digest and parameter/effect contract. Builtin compiler intrinsics are distinguished from user helpers by identity, not solely by a convenient name.

[designed] An effectful helper may take explicit memory/FIFO parameters and contain controllers. At a call, arguments bind to the same backing objects; the checker substitutes the callee's read/write/consume summary and retains controller nesting and ordering. New callee-local allocations receive fresh identities per represented call instance, with allocation lifetime owned by the call region. A source closure over a surrounding DSL FIFO is represented as an explicit environment argument before checking. A builder helper must pass the equivalent handle or declared environment explicitly. Neither form silently copies a FIFO or treats a consuming helper as pure arithmetic.

[designed] Kernel composition has two separate meanings. **Within one represented accelerator**, a kernel body can be extracted/reused as a typed component template; a `call_component` node binds its input/output handles in a caller region and owns fresh local allocations. First construct `scale_component = as_component(scale_template, interface=...)` in the host with borrowed src Read[Dram], gain value:Int, dst Write[Dram], and N/TILE meta formals. An illustrative source call is `call_component(scale_component, src=src, gain=gain, dst=tmp)` followed by `call_component(scale_component, src=tmp, gain=gain, dst=dst)`; the matching builder calls are `k.call_component(scale_component, src=src, gain=gain, dst=tmp)` and `k.call_component(scale_component, src=tmp, gain=gain, dst=dst)`. `tmp` is explicitly allocated initialized-by-first-call storage, not an implicitly connected port. The first call's writes must establish the second call's reads, and the common checker verifies shapes, aliasing, effects, and region order. Top-level host launch ports are not automatically eligible as component-local interfaces; [[10 - Source Checker and IR Blueprint#Helpers, components and declarative library callbacks|the proposed component signature and borrowing rule]] now defines that projection, formal modes, summary substitution and return-lifetime checks. It still requires adoption and implementation before this API exists.

[designed] **Across host launches**, ordinary host code runs one checked entry and passes declared buffers/results to the next launch. That is not the same as a nested controller call. Both source capture and builder construction support this host orchestration through the same future execution API. Neither syntax decides FPGA resource sharing, parallelism, or whether two bodies become one device program.

### Generated families and provenance

[designed] For the simple family, host code specializes the source template or runs the builder factory with the same explicit configurations:

```python
source_template = Capture.file("tiles.py", entry="tiled_scale")
for n in (32, 64):
    meta = FrozenMeta({"N": n, "TILE": 16})
    source_member = specialize(source_template, meta, name=f"scale_{n}")
    builder_member = make_tiled_scale(meta).renamed(f"scale_{n}")
    # Each member still needs the common check; these are no validation results.
```

[designed] These family members share the same template semantics; generation changes dimensions, not the runtime staging boundary. A source-first design can additionally accept generated source/AST plus an origin map. This does not run the generated kernel. A builder can produce arbitrary graphs directly, with stable generator-instance IDs. For both, each generated node records the source/template definition, generator invocation/configuration, expansion ordinal, and semantic region; generated declarations attach in deterministic order. No source correspondence is invented when the host generator supplied none.

[designed] Acyclic reusable helper/component calls are the initial recommendation. Reject reachable DSL helper/component recursion with a call-cycle diagnostic, including indirect cycles; do not rely on Python's recursion limit or a backend eventually failing. Apply that rule to the reachable definition graph before meta expansion so a recursive DSL definition does not masquerade as unrestricted compile-time evaluation. Ordinary host generators may use recursion outside the DSL and submit a finite graph, subject to explicit construction/expansion limits. Structurally decreasing meta recursion could be a later language feature; it is not admitted implicitly here.

[designed] A helper-cycle report labels the call that closes `a → b → a`, then the earlier call and both definitions. An expansion-limit report labels the static expansion or generated request, then the specialization bindings and host factory invocation. Repair examples are to factor an acyclic helper chain, replace a recursion with a supported bounded controller, or generate the finite structure in explicit host code. None is an automatic semantics-preserving rewrite for an arbitrary recursive program.

## Exact literals and source provenance

[measured] The isolated probe below parsed `0.10000000000000001` as a `Constant` whose Python value printed `0.1`, while `ast.get_source_segment` retained the original token. It also retained `0.75 * 2` as a binary expression and represented `-2147483648` as unary minus applied to positive `2147483648`. These observations justify preserving token spelling and expression structure; they establish no Spatial numeric result.

[designed] The source frontend keeps the original numeric segment/tokens, sign/operator structure, and expected-type context. It parses supported numeric spellings into exact integer/rational ingress records using its own declared grammar; it does not rebuild a decimal from `Constant.value`, `str(float)`, or `ast.unparse`. Allowed exponent/base/underscore forms still need an adopted grammar. The source literal's exact value and the eventual hardware quantization are different records. Type/shape constants are distinguished from runtime numeric literals before folding.

[designed] Give the builder an equally exact path: `literal("0.10000000000000001")`, `literal("0.75") * literal("2")`, and a unary-minus expression node. An exact Python integer may enter as an explicitly tagged value, but its presence does not recover a previously folded expression. Bare Python floats at exact-literal ingress should reject with a repair to an exact string/rational constructor. A user who intentionally wants a binary floating value must name that import/conversion operation and its type; it is distinct from decimal-token ingress.

```python
# Same literal tree; apply the proposed numeric contract in PY-R002 to both.
# Source capture:
@kernel
def literal_tree():
    gain: FixPt[Signed, 4, 1] = 0.75 * 2

# Builder construction:
gain = k.let("gain", k.literal("0.75") * k.literal("2"),
             type=FixPt(Signed, 4, 1))
```

[judgment] The earlier floor-ingress candidate in [[B0 - Python Literal Typing]] identified the contextual per-literal versus host-first folding discriminator. [[PY-R002 - Numeric and Reduction Semantics]] now provides the current proposed exact-ingress and per-operation numeric contract, replacing reliance on that older Rust prescription. Preserve the token/tree information so both surfaces apply the current proposal consistently if it is adopted. A bare builder `0.75 * 2` has already become a host value before a call receives it; an exact wrapper/tree avoids that loss.

[designed] Every declaration, expression, region, and effect carries an `Origin`: primary `SourceRef`, related definition/call/instantiation locations, and whether a location is exact, line-only, generated, or unavailable. A `SourceRef` references immutable source identity/digest plus start/end byte offsets; rendering converts to the editor's column convention. A node retains its origin through helper expansion, specialization, checking, optimization, and lowering. Generated source spans describe generated text; related labels expose the template and generator that produced it. These locations are not substitutes for symbol/region/backing-object identities.

[designed] A builder can supply exact `SourceRef`s explicitly, for example through `k.at(origin)` or an operation's `origin=` argument. A source-aware file/cell construction adapter could attach locations to constructor/operator calls while preserving ordinary host construction semantics. Such an adapter is an additional proposal, not automatic behavior of overloaded operators. Plain arbitrary builder execution may offer only a construction callsite, a stack of helper calls, or an unavailable-source label. Retain that degraded quality honestly; do not underline a full expression inferred from a line number alone. A provided source map can give the builder equally precise diagnostics, with extra author/adapter responsibility.

## Diagnostic architecture and responsibilities

[designed] Use stable structured diagnostics from each phase. Rendering is separate from checking. A record contains code, severity, phase, message, primary location/quality, labeled related locations, semantic subject IDs, and repair suggestions with applicability. The checker reports semantic facts, not just an exception string or a Python traceback. Internal failures and host-factory exceptions remain distinguishable from invalid Spatial programs. A host exception may be wrapped with its construction/capture context, but is never presented as a successful language check.

| Phase | Source frontend | Builder frontend | Shared responsibility |
|---|---|---|---|
| A. Acquisition | Read source/cell/dependency and register immutable text | Optionally register construction text/origins before execution | Missing source, stale/mismatched origin, encoding/dependency failures; never substitute different text silently |
| B. Surface and binding | Closed syntax visitor and DSL resolver; no Python execution | Constructor/region attachment contract and forbidden symbolic host conversions | Stable intrinsic/helper/type identity; lexical binding and explicit unsupported-form diagnostics |
| C. Meta specialization | Closed evaluation and bounded static expansion | Validate/freeze meta inputs; receive host-generated graph | Meta domain/type checks, missing values, construction/expansion budgets, deterministic instances |
| D. Types and numeric ingress | Check token-backed expression/declaration tree | Check explicit literal/expression/declaration tree | Port/operator/result types, exact literal range/conversion policy, helper signature/effect intent |
| E. Regions, initialization, and effects | Check normalized ordered program | Check the same normalized ordered program | Dominance/lifetime, memory initialization/coverage, lazy branch effects, alias and consuming-operation legality |
| F. Reference execution | Run only a checked program under declared host inputs | Same | Guard failures or dynamic input faults retain originating operation and relevant host input; no successful simulation inferred from a listing |

[designed] Early builder checks may reject while constructing, but freeze/normalization rechecks their invariants. A malformed imported builder graph must not bypass common checks. Source scope errors can occur before a complete graph exists; keep failed lookup information and hidden declaration locations for useful related labels. Do not let a first early error erase the caller/definition or suppress an independent relevant issue. Avoid cascading type/effect messages from a node already marked invalid.

[designed] Diagnostics should state what failed and one concrete path to repair. An exact-origin file/cell may receive a suggested edit. Generated/ambiguous/line-only origins receive explanatory repairs rather than a blind edit. Host-configuration repairs should name the meta key; runtime repairs should name the port/precondition or represented operation. A type mismatch does not justify automatically inserting a cast; the explicit rounding/overflow modes proposed in [[PY-R002 - Numeric and Reduction Semantics]] must be selected intentionally and remain pending adoption.

## Matched invalid cases and intended repairs

[designed] Each pair below is one common semantic request. Code blocks are independent illustrative inputs. Locations use `(line, UTF-8 column)` with one-based lines, zero-based columns, and an exclusive end. For builder examples, the exact locations assume supplied `SourceRef`s/source-aware construction metadata; the bare APIs do not promise those spans automatically. Diagnostic text is designed, not observed compiler output.

### U — Read before initialization

```python
@kernel
def uninitialized(out: Out[Int]):
    m: Sram[Int, 1]
    out = m[0]
```

```python
k = Kernel("uninitialized")
out = k.output_scalar("out", Int)
m = k.sram(Int, 1)
out.write(m[0])
```

| Field | Source capture | Builder |
|---|---|---|
| Phase/code | E / `E-INIT-READ` | E / `E-INIT-READ` |
| Primary | `m[0]`, `(4,10)–(4,14)` | `m[0]`, `(4,10)–(4,14)` |
| Related | Declaration `m`, `(3,4)–(3,19)`; no preceding write in this path | SRAM allocation, `(3,4)–(3,18)`; no preceding write in this region |
| Intended message | `SRAM m[0] is read before initialization` | Same, using registered display name or memory ID |
| Repair | Insert `m[0] = 0` before the read, or perform an explicit load that covers index 0 | Insert `m.at(0).write(0)` before the read, or the equivalent explicit load |

[designed] Declaration alone is not initialization. A scalar `x: Int` without an initializer would instead reject as an incomplete scalar declaration under this candidate; it is not automatically a mutable register or an initialized zero. Do not conflate that surface error with the SRAM initialization proof.

### T — Incompatible numeric operands

```python
@kernel
def incompatible(a: In[Int], gain: In[FixPt[Signed, 24, 8]], out: Out[Int]):
    out = a + gain
```

```python
k = Kernel("incompatible")
a = k.input_scalar("a", Int)
gain = k.input_scalar("gain", FixPt(Signed, 24, 8))
out = k.output_scalar("out", Int)
out.write(a + gain)
```

| Field | Source capture | Builder |
|---|---|---|
| Phase/code | D / `E-TYPE-OPERANDS` | D / `E-TYPE-OPERANDS` |
| Primary | `a + gain`, `(3,10)–(3,18)` | `a + gain`, `(5,10)–(5,18)` |
| Related | Parameter declarations `a`, `(2,17)–(2,27)`, and `gain`, `(2,29)–(2,59)` | Input constructors `(2,4)–(2,28)` and `(3,7)–(3,51)` |
| Intended message | `addition requires compatible operands; received Int and FixPt[Signed,24,8]` | Same |
| Repair | Declare both ports with the intended common type; otherwise select an explicit conversion with the modes proposed in PY-R002 | Change the corresponding port descriptors, or request that same explicit conversion |

[designed] The output annotation is useful context, but does not license silently converting either operand. The repair must acknowledge any changed host interface. An incompatible branch-yield pair would use the same type rules with both yield sites as related labels.

### C — Unsupported runtime control

```python
@kernel
def unsupported(flag: In[Bool], out: Out[Int]):
    while flag:
        out = 1
```

```python
k = Kernel("unsupported")
flag = k.input_scalar("flag", Bool)
out = k.output_scalar("out", Int)
while flag:
    out.write(1)
```

| Field | Source capture | Builder |
|---|---|---|
| Phase/code | B / `E-CONTROL-UNSUPPORTED` | B during host construction / `E-STAGE-TRUTH` |
| Primary | `while flag`, header `(3,4)–(3,14)` | `flag`, `(4,6)–(4,10)`, where Python requests a truth value |
| Related | Runtime parameter declaration `flag`, `(2,16)–(2,30)` | Runtime input constructor `(2,7)–(2,35)`; construction context |
| Intended message | `runtime while is outside this supported controller subset` | `runtime Bool flag cannot choose host control; this request does not construct a runtime loop` |
| Repair | Use a supported bounded/FSM controller with an explicit domain/state policy, or move a truly static choice to meta specialization | Use the matching explicit supported controller; if the condition is truly a host choice, use a validated meta Bool rather than the runtime handle |

[designed] Both reject the same requested runtime while. Their first diagnostic phases differ because the builder reaches Python truth conversion. A native host `while` over ordinary host data may be valid program generation; the builder does not promise to inspect or reject all Python statements. A runtime-while constructor, if later proposed, must reject through the controller registry until that controller's meaning is specified. An incidental `AttributeError` from a nonexistent method is not the designed semantic diagnostic.

### B — Stateful branch laziness, including a meaningful negative

[designed] In the valid pair, the candidate sequential reference model begins with an empty local FIFO, records one enqueue of `7`, and consumes only when the runtime `take` input is true. This is a written effect trace, not an observed result.

```python
@kernel
def guarded(take: In[Bool], out: Out[Int]):
    q: Fifo[Int, 2]
    q.enq(7)
    if take:
        out = q.deq()
    else:
        out = 0
```

```python
k = Kernel("guarded")
take = k.input_scalar("take", Bool)
out = k.output_scalar("out", Int)
q = k.fifo(Int, 2)
q.enq(7)
with k.if_else(take) as choice:
    with choice.then_():
        out.write(q.deq())
    with choice.else_():
        out.write(0)
```

| Runtime input | Required output | Required final FIFO state |
|---|---|---|
| `take=False` | `0` | `[7]`; no consuming operation |
| `take=True` | `7` | `[]`; exactly one consuming operation |

[designed] A bad implementation that eagerly consumes an untaken arm can still return `0` for `False`, but leaves the wrong queue state. A later unconditional dequeue distinguishes it further: the correct false path can still return `7`, while the eager version has emptied the queue. This is why checking the sum/output alone is insufficient.

[designed] Now replace the branch with an explicitly **pure** `select` request in each style:

```python
@kernel
def eager(take: In[Bool], out: Out[Int]):
    q: Fifo[Int, 2]
    q.enq(7)
    chosen: Int = select(take, q.deq(), 0)
    out = chosen
```

```python
k = Kernel("eager")
take = k.input_scalar("take", Bool)
out = k.output_scalar("out", Int)
q = k.fifo(Int, 2)
q.enq(7)
chosen = k.let("chosen", k.select(take, q.deq(), 0), type=Int)
out.write(chosen)
```

| Field | Source capture | Builder |
|---|---|---|
| Phase/code | E / `E-BRANCH-EFFECT` | E, optionally also an early constructor report / `E-BRANCH-EFFECT` |
| Primary | Direct effectful argument `q.deq()`, `(5,31)–(5,38)` | Direct effectful argument `q.deq()`, `(6,40)–(6,47)` |
| Related | `select`, `(5,18)–(5,42)`; FIFO declaration `(3,4)–(3,19)` and enqueue `(4,4)–(4,12)` | `k.select`, `(6,25)–(6,51)`; FIFO allocation `(4,4)–(4,18)` and enqueue `(5,0)–(5,8)` |
| Intended message | `pure select cannot contain a consuming FIFO operation; place the dequeue in a runtime branch region` | Same |
| Repair | Restore the statement `if` and its two writes, as in the valid pair | Restore `if_else` and put the consuming operation inside `then_`, as in the valid pair |

[designed] To make this negative equally detectable, the builder represents unbound stateful expressions as pending effect trees with their creation-region identity. A sequencing operation such as `let` or `write` attaches their effects exactly once to that region. Pure `select` rejects a direct pending consuming operand rather than hoisting it, moving it into a branch, or inferring laziness from a host call. Region movement and duplicate consumption of a pending effect reject too. This is an explicit recommendation for builder representation, not a claim about the earlier sketches' implementation.

[designed] Construction maintains an outstanding-effect ledger independent of Python variable lifetime. If a pending effect expression remains unattached at region/program freeze, reject with `E-EFFECT-UNATTACHED`, primary at its creation and related at the owning region/freeze call. A bare unused `q.deq()` or a handle abandoned through host rebinding/garbage collection must not silently disappear. An intentional consume-without-result uses an explicit sequencing statement such as `k.discard(q.deq())`; this commits the consuming operation and discards only its returned scalar. Source expression statements that intentionally discard a consuming result normalize to that same statement. Pure unused expressions may be dropped; intended state changes may not.

[designed] An intentionally unconditional read followed by selection is different and may be legal: source `v: Int = q.deq(); chosen: Int = select(take, v, 0)`, or builder `v = k.let("v", q.deq(), type=Int); chosen = k.let("chosen", k.select(take, v, 0), type=Int)`. Sequencing the read makes `v` a pure scalar reference. The checker must not reject every value transitively produced by a dequeue. It reports the direct effect context/region, not speculative programmer intent. Ordinary builder `if take:` has the separate truth-conversion error; neither form performs both dequeues at construction time.

### S — Escaped lexical declaration or handle

```python
@kernel
def escaped(flag: In[Bool], out: Out[Int]):
    if flag:
        tmp: Int = 1
    out = tmp
```

```python
k = Kernel("escaped")
flag = k.input_scalar("flag", Bool)
out = k.output_scalar("out", Int)
with k.if_else(flag) as choice:
    with choice.then_():
        tmp = k.let("tmp", 1, type=Int)
out.write(tmp)
```

| Field | Source capture | Builder |
|---|---|---|
| Phase/code | B DSL resolution / `E-SCOPE-ESCAPE` | B handle attachment, rechecked in E / `E-SCOPE-ESCAPE` |
| Primary | Use `tmp`, `(5,10)–(5,13)` | Use `tmp`, `(7,10)–(7,13)` |
| Related | Branch-local declaration `(4,8)–(4,20)`; owning branch header `(3,4)–(3,11)` | `let`, `(6,14)–(6,39)`; `then_` region entry `(5,9)–(5,23)` |
| Intended message | `tmp belongs to the then region and is not visible here` | Same; a retained Python handle does not extend DSL lifetime |
| Repair | Write the output within both runtime branches, or explicitly merge values from two complete branch yields | Perform the two writes inside branch contexts, or consume an explicit branch-result handle after both branches yield |

[designed] A declaration before the branch plus only a then-path assignment does not repair definite assignment on the false path. A legal merge exports a newly defined result from a structured branch node; it does not export either branch's local storage/view. Loop binders and helper-local SRAM/views use the same ownership principle, with declaration/allocation and consuming callsite as related labels. The source diagnostic comes from DSL scope rules, not Python's function-wide local-variable rule.

### O — Ordinary assignment and augmented assignment have different effect order

[documented] Ordinary Python assignment evaluates its RHS before its targets; a subscription target then evaluates its primary and subscript before setting the item. Augmented assignment evaluates the target once, reads it before the RHS, performs the operation, and writes back. These forms cannot generally be exchanged. [Python evaluation order](https://docs.python.org/3.14/reference/expressions.html#evaluation-order), [assignment](https://docs.python.org/3.14/reference/simple_stmts.html#assignment-statements), [augmented assignment](https://docs.python.org/3.14/reference/simple_stmts.html#augmented-assignment-statements) (accessed 2026-09-30).

[source-inspected] The earlier Rust DSL instead specifies lvalue-index effects before RHS effects: `spatial-rs@eb49d8b:docs/language-spec.md:831-837`. [[30 - Python Assignment]] rates Python forms against that earlier contract. That is a Rust design choice, not sufficient evidence for original Scala behavior or a rule the Python rewrite must preserve.

[judgment] Recommend preserving the ordinary Python evaluation order for captured `=`. Reversing a familiar statement's consuming effects needs a compelling semantic reason and explicit adoption; none is established here. This recommendation aligns source and builder on one ordered IR sequence rather than treating host argument order or a previous Rust rule as canonical. It does not claim to inherit all Python mutation, aliasing, or numeric behavior.

```python
@kernel
def assignment_order():
    q: Fifo[Int, 2]
    dst: Sram[Int, 2]
    q.enq(0)
    q.enq(5)
    dst[0] = 10
    dst[1] = 20
    dst[q.deq()] = q.deq()
```

```python
k = Kernel("assignment_order")
q = k.fifo(Int, 2)
dst = k.sram(Int, 2)
q.enq(0)
q.enq(5)
dst.at(0).write(10)
dst.at(1).write(20)
value = k.let("value", q.deq(), type=Int)
index = k.let("index", q.deq(), type=Int)
dst.at(index).write(value)
```

[designed] After setup, both represented queues contain `[0,5]` and the destination contains `[10,20]`. The explicit builder temporaries sequence the RHS read first and target-index read second; they do not pop a host queue during construction. The following is a derived reference trace of the ordered operations, **not** an executed Spatial program. A static rejection means no represented execution or FIFO mutation actually starts.

| Step under the proposed ordinary-assignment rule | Value/state |
|---|---|
| Evaluate RHS dequeue | `value=0`; queue becomes `[5]` |
| Evaluate target-index dequeue | `index=5`; queue becomes `[]` |
| Check destination index | `5` is outside `[0,2)`; the write fails and destination remains `[10,20]` |

[designed] A precise-value checker can reject this case in phase E with `E-BOUNDS`, primary source target dequeue `(9,8)–(9,15)` or builder target use `index` `(10,7)–(10,12)`. Related labels identify the `dst` extent, the enqueue of `5`, the RHS dequeue `(9,19)–(9,26)` or builder `value` binding, and the index binding. Message: `assignment target index is 5 after RHS evaluation; expected 0 <= index < 2`. If the chosen analysis does not track FIFO payload values, it must report an unproved bounds obligation rather than invent this exact fact or accept unchecked code. Phase F may retain a defensive bounds guard, but does not turn this known invalid fixture into a successful check.

[designed] Repair the source by naming the two dequeues explicitly in the intended order, then proving/checking the second value as an index or fixing the input contract. The matching builder already makes those roles explicit. If `[0,5]` means **index then value**, intentionally write an index-first two-statement source sequence and the matching builder sequence; that is a changed program, not a lowering of the original `=`. Merely swapping compiler traversal order would instead produce the old rule's `dst[0]=5` and hide the bounds failure. With a six-element destination, RHS-first would validly write `dst[5]=0`, making the difference observable without a fault.

[designed] If augmented assignment is supported, `dst[q.deq()] += q.deq()` on the same initialized two-element destination first captures index `0`, reads `dst[0]=10`, then captures delta `5`, adds, and writes `15` back to that same address. The matching builder must explicitly bind index, bind the destination read, bind delta, then write their addition. The target is not re-evaluated; it is not two dequeues for address generation. A write-only output or uninitialized SRAM destination rejects the read-modify-write in phase D/E, with the augmented target as primary and port/allocation/initialization location as related. Augmented assignment is consequently no repair for an ordinary store's ordering problem.

[designed] Compact builder `dst.at(q.deq()).write(q.deq())` may request/address its target before its RHS under ordinary host call evaluation, depending on the adopted constructor sequencing contract. The checker cannot assume it has the source assignment's order. Until that compact effectful form is specified, use the explicit temporaries above. Pure indices in E1 need no such rewrite. Normalize accepted forms to ordered effect steps before initialization/bounds reasoning and preserve those steps through scheduling.

## Comparison after giving both alternatives their best case

| Dimension | Source capture, strongest form | Explicit builder, strongest form |
|---|---|---|
| File/cell acquisition | Immutable text + compiler marker recognition; raw cell adapter; no kernel definition execution | Ordinary host construction with optional original source registry and explicit origins |
| Staging | Closed meta evaluator; both runtime branches survive; external values explicit | Arbitrary host generation; runtime regions explicit; symbolic host coercions guarded |
| Composition | Reusable captured helper/component templates; generated source/AST and host-driven specialization | Reusable helper/component objects; direct graph factories and general host composition |
| Numeric fidelity | Original token/operator tree naturally available, retained deliberately | Explicit literal trees preserve the same information; bare folded host values do not |
| Scope/effects | DSL resolver/regions interpret ordinary statements before execution | Explicit handles/regions encode ownership; common checker still required |
| Diagnostics | Exact source/cell segments plus expansion origins available from acquisition | Equally precise with explicit/source-aware metadata; plain construction may provide a weaker callsite |
| Best-fit workflow, as judgment | Writing/reviewing kernels where original statements and repairs should stay close together | Algorithmic generators, factories, data-driven program graphs, or users who prefer explicit IR construction |
| Principal unresolved cost | Teaching source-as-data and delimiting the Python-looking subset; no automatic host interoperability | Teaching expression wrappers/region constructors and supplying provenance; host computations can erase intent before the checker sees it |

[judgment] Source-first is preferable for the initial study because its core artifacts already include source statements, literal tokens, runtime branch bodies, and their locations before host evaluation. That supplies a direct substrate for the paired errors and repairs above. This is a representation/diagnostic argument, not proof that novices learn it faster or that builders cannot preserve the same information.

[judgment] The recommendation should be reconsidered if reviewed use cases need pervasive dynamic host callbacks within kernels, if a source-backed builder meets the same diagnostic/fidelity contract with acceptable notation, or if actual users find explicit construction clearer. Adequate Python implementation capability makes either feasible; feasibility alone does not settle the public programming model. Exo specifically weakens any argument that AST-based source must be noncomposable. Giving source an unrestricted host quotation system is possible, but should be evaluated as a third staging design rather than silently added to the restricted proposal.

## Isolated AST/literal probe: exact execution record

[measured] Executed 2026-09-30 using `python3` with CPython `3.14.5 (main, May 10 2026, 10:21:34) [Clang 21.0.0 (clang-2100.0.123.102)]`, Darwin, arm64. The probe used only the standard library. It parsed source and printed AST/value/source-segment facts; it did not execute/import the captured snippet or run a compiler frontend.

```python
import ast
import platform
import sys
from fractions import Fraction
source = '@explode()\ndef f(x: explode()):\n    é = 0.10000000000000001\n    return -2147483648 + (0.75 * 2)\n'
tree = ast.parse(source, filename='probe.py', mode='exec')
function = tree.body[0]
assignment = function.body[0]
print('environment:', sys.version.splitlines()[0], platform.system(), platform.machine())
print('parse: succeeded; explode is undefined; no exec/eval/import of the snippet')
print('decimal segment:', ast.get_source_segment(source, assignment.value))
print('decimal Python value:', repr(assignment.value.value))
print('decimal float rational:', Fraction(assignment.value.value))
print('name span:', assignment.targets[0].lineno, assignment.targets[0].col_offset, assignment.targets[0].end_lineno, assignment.targets[0].end_col_offset)
print('decimal span:', assignment.value.lineno, assignment.value.col_offset, assignment.value.end_lineno, assignment.value.end_col_offset)
print('return tree:', ast.dump(function.body[1].value))
print('unparsed decimal:', ast.unparse(assignment.value))
```

```text
environment: 3.14.5 (main, May 10 2026, 10:21:34) [Clang 21.0.0 (clang-2100.0.123.102)] Darwin arm64
parse: succeeded; explode is undefined; no exec/eval/import of the snippet
decimal segment: 0.10000000000000001
decimal Python value: 0.1
decimal float rational: 3602879701896397/36028797018963968
name span: 3 4 3 6
decimal span: 3 9 3 28
return tree: BinOp(left=UnaryOp(op=USub(), operand=Constant(value=2147483648)), op=Add(), right=BinOp(left=Constant(value=0.75), op=Mult(), right=Constant(value=2)))
unparsed decimal: 0.1
```

[measured] Parsing succeeded although no `explode` binding was supplied; this short experiment exercised neither decorator nor annotation call. The non-ASCII identifier occupies two UTF-8 bytes in the AST's name span. These are local observations, not a complete no-execution/capture guarantee; the recommended compiler needs its own fail-closed syntax, binding, meta, and provenance contracts.

## Remaining review and validation before adoption

[designed] Required next evidence is bounded and shared between both alternatives:

1. Review the source-grounded candidate contracts and remaining limits in [[PY-R002 - Numeric and Reduction Semantics]] and [[PY-R003 - Control Memory and Effects]]; adopt the numeric/effect profile and resolve component-call lifetime/effects before implementation acceptance cases are frozen.
2. Review the exact supported source grammar, meta schema, helper-recursion policy, and host/runtime input separation. Decide whether mixed files, a callable adapter, or explicit host quotation are separate supported surfaces.
3. Specify the common unchecked/checked program invariants and origin schema, including pending effect ownership and result merging. Test both producers against identical valid/invalid normalized programs once implementation is authorized.
4. Define file, raw-cell, unsaved-cell, edited-cell, generated-source, source-unavailable builder, and supplied-origin builder diagnostic acceptance cases. Check phase/code, primary segment, related definition/instantiation labels, and repair applicability; never score quality solely by whether some error string appeared.
5. Use effect-sensitive traces for the guarded FIFO case and exact token/tree-sensitive cases for numeric ingress. Record actual execution evidence only after a real frontend/checker/simulator exists. No syntax parse is a semantic conformance run.

[designed] Distill reviewed conclusions into proposed contracts with explicit `adoption_status: proposed` and `implementation_status: not-implemented`. Adoption requires a decision naming its scope and authority. A completed research note can have `status: research-conclusion` before adoption; link its proposed contracts through `feeds_spec`. The source-first recommendation remains revisable during professor review.
