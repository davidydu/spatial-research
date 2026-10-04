---
type: implementation-blueprint
title: "Proposed source, checker, and Spatial IR blueprint"
scope: python-rewrite
project: spatial-python
date: 2026-10-01
status: reviewed
adoption_status: proposed
implementation_status: not-implemented
decision_records:
  - "[[D-28]]"
depends_on:
  - "[[10 - Python Language Contract]]"
  - "[[40 - Python Compiler and HLS Contract]]"
  - "[[PY-R004 - Capture Composition and Diagnostics]]"
  - "[[PY-R006 - Compiler Architecture and Framework Choice]]"
  - "[[PY-R016 - Source and Host Workflow Refinement]]"
  - "[[PY-R017 - Compiler Representation Comparison]]"
---

## Purpose and authority

This selects concrete implementation rules where the reviewed contracts previously named a boundary without specifying its mechanism. It remains a proposal under [[D-28]]; it authorizes neither production code nor a claim of full support. Pure Python source acquisition, compiler semantics, and reference simulation remain the direction. The 2026-10-03 refinement in [[PY-R017 - Compiler Representation Comparison]] proposes custom transitively immutable Python records as the canonical checked semantic and first target-plan representations. xDSL becomes an optional derived backend adapter only when a named pipeline demonstrates benefit. This supersedes the earlier xDSL-default wording; historical framework probes below retain their original scope. Adequate team/coding capability is assumed.

The full language inventory in [[PY-R005 - Full Language Coverage and Migration]] remains in scope. This blueprint specifies reusable node families and a checker capable of extending through those families. It does not replace the language by S1's tiled kernel. The numeric and protocol implementation blueprints supply the closed operation/transition details referenced here; the package/conformance blueprint supplies artifact bytes, API result records, source-manager rules and diagnostic records. An unregistered operation is rejected, rather than executed as Python or given an arbitrary callback meaning.

## Readiness findings and selected refinements

| Baseline gap | Selected rule here | Consequence and independent acceptance |
|---|---|---|
| Language contract:46 names scalar assignment categories without defining them | Annotated scalar locals are immutable values; explicit Reg/storage/port writes mutate state | `x:Int=0; x=1` rejects; Reg recurrence succeeds. This is a proposed surface refinement, not removal of accelerator recurrence |
| Language contract:50/R004:534 name helper returns/merges without placement rules | Final return or exhaustive terminal returning if/else; structured typed results; no early return across a loop | Every terminal leaf yields exact result types; missing branch result and escaping local handle reject |
| R004:175 explicitly leaves component signatures to a separate rule | Components borrow explicit storage/endpoints and accept value/meta arguments; launch ports require explicit interface projection | Nested calls alias actual backing identities; no host launch or allocation is inferred |
| R004:105/109 leaves meta records/domains implicit | Closed immutable value algebra and typed exact evaluator below | Negative structural intermediate is legal; negative Size/extent conversion rejects; poison conversion hooks never execute |
| R006:66–105 names checked graph invariants without node schema | Closed family tags, owned descriptor IDs, isolated single-block structured regions, per-task tokens | Same-block forward use, token duplication, wrong yield, undeclared capture and malformed imported graph reject |
| Compiler contract:51/61 permits requirements/guards without an algorithm | Named reference profiles, closed requirement predicates, conservative abstract interpretation and explicit transfer evidence | Unknown never means proved; active guard may accept reference execution; target capability remains separate |

These rules need professor review with the rest of D-28. They must be incorporated into the proposed contracts before implementation starts; this new note does not silently rewrite the older examples.

## Closed source grammar v1

The parser is CPython 3.14.5's `ast.parse(text, filename=label, mode="exec", feature_version=(3,14))` plus the original UTF-8 text/token stream. The grammar version is explicit acquisition metadata, not whichever interpreter happens to be installed. The surface converter recognizes the following AST forms by explicit type, operator and field allowlists. It does not use a permissive generic visitor. Python parsing alone establishes no accepted Spatial program. Any nonlisted AST form or unexpected AST field produces a surface diagnostic, including in a statically discarded branch or unused reachable helper. `type_comment`/type-ignore mechanisms, host conversion hooks and Python AST serialization are excluded.

Before tokenization/AST parsing, enforce the configured per-unit and aggregate UTF-8 source-byte budgets; count with bounded chunks and stop at the first exceeded limit, before constructing another full encoded/token/AST copy. Caller-created host strings are already host allocations; this compiler check does not sandbox that host work. Reject embedded NUL and invalid Unicode scalar text as `SOURCE.INVALID_SOURCE`. Then parse, count AST nodes iteratively under the node budget, and normalize using the allowlist. Byte-limit and node-limit failures are `SOURCE.RESOURCE_LIMIT` with the named limit, not specialization success.

Within this acquisition phase, expected parser/tokenizer failures map as follows: SyntaxError and tokenizer syntax errors -> `SOURCE.SYNTAX`; ValueError from rejected source content -> `SOURCE.INVALID_SOURCE`; RecursionError -> `SOURCE.RESOURCE_LIMIT` with parser-depth cause; recoverable MemoryError -> best-effort `SOURCE.RESOURCE_LIMIT` with parser-memory cause. Do not misreport these as CompilerFailure. A deeply parenthesized but byte-admitted input may receive SyntaxError before recursion exhaustion; its exact parser exception class is not a language guarantee. Test a deliberately byte-over-budget nested input for the resource code, rather than promising all deep parentheses produce RecursionError. Process OOM/termination or inability to allocate a diagnostic remains a failed tool/process execution, not a guaranteed recoverable RunResult. Unexpected implementation exceptions still receive CompilerFailure.

| Position | Accepted forms and exact meaning |
|---|---|
| Source module | Optional string docstring; declarative imports; registered `Const[meta_type]` annotated definitions; typed kernel/helper/component definitions. No executable top-level assignment/call/class/with/if |
| Imports | `from spatial import NAME[, ...]`, finite registered `from spatial.math` / `from spatial.rng` imports, `from spatial.lib.MODULE import NAME[, ...]`, or manifest-named source-module imports, with optional explicit `as` alias. No star import, dynamic import, relative filesystem fallback or host module import. Imported names resolve exported definition/descriptor/intrinsic IDs |
| Markers | `@kernel`, `@component`, `@helper`, or `@helper(effects="pure"\|"ordered"\|"communicating")`. Marker arguments are closed literals/meta schema, never evaluated annotations. Nested typed `def` without marker is a helper with inferred effect bound `ordered` unless declared otherwise |
| Parameters | Positional-or-keyword named typed formals, named call arguments, and explicit `Meta[T]`. No defaults, `*args`, `**kwargs`, positional-only syntax, untyped parameter, duplicate formal or Python type parameter list |
| Numeric/scalar/handle declaration | `name: Const[meta_type] = meta_expr` for immutable meta declarations, including `Const[Type]`; `name: T = expr` for immutable values; `name: StorageDescriptor` for storage allocation with descriptor-defined initialization; or `name: StorageDescriptor = registered_initializer(...)`. Scalar declaration without initializer rejects. An annotation target must be a simple name |
| Writes | Single-target `name = expr`, `receiver[index] = expr`, or registered writable field assignment, only for an existing writable port/Reg/storage lvalue. Assignment to a value/meta/definition/endpoint name rejects. No implicit fresh name declaration; no chained/destructuring assignment. Augmented assignment permits the same readable/writable lvalues and registered arithmetic operators |
| Expressions | Resolved name, exact Bool/integer/decimal token, unary/binary registered operator, typed comparison, field/index/view projection, registered call, typed aggregate construction, lazy conditional expression. Tuple/list syntax is allowed only in a registered argument slot such as meta tuple, vector payload or index tuple; it never denotes a dynamic accelerator list |
| Bool | Bool-only `not`, `and`, `or`, comparison chains, conditional predicates. `and`/`or` lower to lazy regions and shared operands in comparison chains evaluate exactly once. No implicit truth conversion |
| Ordered control | `if/elif/else`; `for name in sequential(...)\|foreach(...)\|pipe_range(...)`; `with pipe(...)\|sequential_region(...)\|enabled(Bool)\|named(meta_string)\|parallel(...)\|stream(...)\|task(meta_name)\|forever(...)`. Only registered context binders exist; a descriptor states exactly which `as` names are bound |
| Static control | `if static(meta_bool): ...`; `for name in static_range(meta_start,meta_end,step=meta_step): ...`. Syntax in both branches validates; selected branch expands hygienically. No implicit static test by knowing a runtime value's current constant |
| Result | Kernel/component has no value return unless declared component result signature. Helper final `return expr`/`return` for Unit; or a last exhaustive if/else in which every terminal leaf returns. All earlier statements must fall through. Return inside loops/context bodies, before a following executable statement, or across a task boundary rejects |
| Explicit discard | Expression statement of an effectful registered operation commits it and discards scalar result; pure expression statement may be dropped. Function/descriptor names alone are not runtime expressions |
| Excluded | Ordinary while/break/continue, exceptions, comprehensions, lambda, walrus, delete, yield/await/async, arbitrary attribute/method lookup, generator, reflection, Python class creation, implicit iterator, unknown call and runtime recursion |

The return restriction accounts for original Spatial's helper capability by explicit structured results; original virtualization already disallowed ordinary return. Runtime dynamic exit remains expressible by the typed FSM/stop controllers and their versioned policies. Adding a convenience early return is a future surface change requiring a return/control algebra, not an implementer choice.

Source strings are only registered meta descriptors, acquired immutable content, debug format literals or constant record field labels. There is no accelerator heap-string type. A runtime debug format uses a fixed literal plus typed operands, never Python f-string execution. Byte literals are accepted only in a registered raw-content constructor with explicit encoding. Numeric lexemes follow the existing Language Contract's integer/base/exponent/underscore rule; source signs and operator trees are retained until numeric checking.

All syntax adapter outputs are versioned `SurfaceForm` records. Python minor grammar/runtime version belongs to acquisition provenance; a parser from another supported minor must produce the same SurfaceForm or explicitly reject the form. A supported newer AST node is never accidentally accepted by inheritance from an older node.

`parallel()` and `stream()` bodies contain only direct `with task(meta_name):` children with distinct names; shared resources are declared before the group. Each task owns its own ordered body and explicit captured capabilities. No ordinary state operation occurs in the group container, and a sequential list of function calls is not implicitly several tasks. Nested groups are allowed within a task. `forever()` is a task/control context with an explicit stop/environment/admission policy and no invented large finite range. The registered `fsm(start,test=...,action=...,next=...)` call takes statically bound typed DefinitionRefs and constructs the three region signatures described below. These forms express original fork/join/stream/FSM responsibilities without ambiguous implicit child discovery.

Controller domains are half-open: step>0 visits `start+k*step < end`, step<0 visits `start+k*step > end`, k starts at zero. Step zero is invalid. Exact trip count is `max(0,ceil((end-start)/step))` for positive step and `max(0,ceil((start-end)/(-step)))` for negative step. Par factors are positive meta sizes; active tail lanes are those with ordinal<trip_count. Iteration order is increasing ordinal, including a negative-step domain. Domain/enables are captured once per controller activation. Requested II/par are tuning preferences unless an explicitly admitted overlap/admission policy makes them semantic; they cannot alter masks or contribution order.

## Namespace, declarations and deterministic identity

`Symbol = (symbol_id, display_name, category, declaration_owner, declaration_ordinal, type_expr, origin_id)` with category `meta`, `value`, `storage`, `endpoint`, `output_port`, `definition`, `descriptor` or `intrinsic`. The identity comes from a deterministic declaration path within the source/dependency specialization, rather than name spelling, a mutable global counter or Python object identity. Artifact canonicalization alpha-renumbers those identities as specified by the package blueprint; diagnostic lineage retains the original declaration path.

Namespaces are distinct: source module exports, definition names, and a stack of lexical body scopes. An import/declaration collision in the same namespace rejects. Nested lexical shadowing of a value/meta name is permitted only through an explicit annotated declaration; it creates a fresh symbol. Shadowing a live storage/endpoint, a formal, a loop/state binder or a registered intrinsic by the same spelling rejects with both definitions as labels. Qualified imported names remain available through explicit aliases; they do not win an implicit precedence contest. A generated builder uses SymbolRefs directly but is rechecked against the same owner/category rules.

Module dependency manifests provide `module_id`, exact content digest, grammar/profile versions, exported IDs and dependency edges. Source acquisition resolves only those entries. Missing/mismatched imports diagnose before specialization. Source module cycles are allowed only for prebinding definitions/descriptors; cyclic meta-constant evaluation rejects. Reachable helper/component calls must be acyclic before static elimination. This allows two source libraries to refer to exported acyclic definitions without using Python's import system; cyclic execution definitions still reject. Source dependencies are frozen once, including library text and content-hashed LUT/text acquisitions, and cannot read a later notebook value.

Top-level and nested definition headers prebind their **definition IDs**, then bodies resolve calls. All signature formal identities prebind in declared ABI order before any dependent annotation or result type is interpreted. Category/type validation follows identity allocation: prebinding never permits an arbitrary runtime value in a shape/type expression. The whole-signature algorithm below supersedes the earlier meta-only formulation. Ordinary value/storage declarations bind in statement order only. A nested definition captures a surrounding runtime symbol only if that symbol exists at its definition statement; later runtime declarations are not forward captured. Static expansion copies the selected region into a fresh expansion owner, so repeated iteration-local declarations receive fresh IDs. Header prebinding never grants a body-local value forward use.

### Whole-signature dependency validation

The proposed refinement and alternatives are in [[PY-R016 - Source and Host Workflow Refinement]]. Apply the same algorithm to kernel/helper/component source and to explicit builder formals:

1. Allocate all formal IDs from the definition identity plus declaration ordinal; retain declared ABI order and reject duplicate spellings. Resolve registered annotation heads and aliases without evaluating Python.
2. Bind and schema-check supplied meta arguments, including `Meta[Type]`; instantiate their closed descriptors. Normalize every formal to its stage/category/type, retaining unresolved dependent shape expressions as references to the already allocated IDs.
3. Validate the annotation dependency graph. Logical extents admit exact integer constants, `Meta[Size]`/`Meta[Integer]`, immutable kernel `In[Index]`, and helper/component `Index` value formals. A kernel runtime value formal must have a registered launch annotation: bare `n: Index` is not a kernel port and rejects with a kernel-category diagnostic. Helpers/components use `n: Index` value formals and reject `n: In[Index]` (and other In/Out/InOut launch annotations); borrowed storage instead uses Read/Write/ReadWrite. Reject cycles, unresolved IDs and dependencies on Out/InOut cells, ordinary accelerator Int inputs, storage, endpoints or body locals. No state read, call with effects or implicit Int projection enters a signature. Reading another port's shape does not infer a new dependency.
4. Type/width parameters, finite local capacities and static expansion remain meta-only. Runtime Index formals may describe logical interface extents; this does not give them compile-time values or waive finite target bounds. The closed pure Index-expression grammar and its domain obligations govern extent arithmetic.
5. At `prepare`, snapshot each runtime shape input once and validate nonnegative extents, descriptor/buffer agreement and declared bounds before an invocation exists. At helper/component entry, do the analogous substitution/check before body effects. Record those validated preconditions in the checked invocation/call contract.

Thus `def copy(src: In[Dram[Int,n]], dst: Out[Dram[Int,n]], n: In[Index]): ...` is a valid proposed header regardless of formal order. Replacing n by `InOut[Index]`, `Out[Index]`, `In[Int]`, a Reg or an endpoint rejects. A negative n fails preparation; dynamic n in `Fix[True,n,0]` fails the meta-only type rule. Body statements still bind in order: `x:Int=y` before `y:Int=1` rejects, and nested helpers cannot capture later runtime declarations.

The resolver maintains hidden declarations by scope/name for diagnostics, but a lookup failure never returns a hidden symbol as if it were visible. Poison symbols can suppress dependent error cascades; they cannot enter a checked graph. At most one primary binding diagnostic per failed lookup node is emitted, with independently valid neighboring statements still checked.

Every CaptureBundle names the version/digest of a fixed **core language prelude** consisting exactly of the `spatial` core registrations below. Thus an illustrative `@kernel`/`Int` snippet does not require a host import to give those words meaning; the prelude is frozen language syntax, not an ambient Python namespace. Declarative imports of the same prelude ID under the same spelling are idempotent; a different ID collision rejects. No `spatial.lib.*`, acquired dataset, user descriptor or notebook variable enters that prelude implicitly. Artifact dependencies record its registry digest.

## Meta value schema and evaluator

Meta values are closed tagged records, not arbitrary Python objects:

| Tag | Payload/invariant |
|---|---|
| `meta.integer` | Arbitrary signed integer; exact host `type(x) is int`, excluding Bool |
| `meta.size` | Integer value >=0 at conversion/binding boundary; physical positive-capacity obligation is separate |
| `meta.bool` / `meta.string` | Exact builtin Bool/string; strings retained as exact UTF-8 scalar text, with no implicit normalization or object conversion |
| `meta.rational` | Coprime integer numerator/positive denominator, canonical zero denominator 1 |
| `meta.tuple` | Immutable ordered tuple of closed MetaValues and a declared element/schema type |
| `meta.record` | Registered record schema ID/version plus exactly its named immutable fields; unknown/missing/duplicate fields reject |
| `meta.descriptor` | Registered type/domain/profile/shape/model ID/version and closed parameter payload; no descriptor/callable hooks |

No `getattr`, `__iter__`, `__int__`, `__float__`, `__deepcopy__`, dataclass reflection, closure introspection or live buffer conversion runs on supplied bindings. Reject list/dict/user object payloads except a host API's separately validated mapping of binding **names** to closed values. Record construction uses the registered schema, not whatever attributes an object happens to have.

### Type-valued source constants

Use `T: Const[Type] = Fix[True,16,16]` or `T: Const[Type] = Int`. `Type` is a closed meta-schema registration, **not** Python `type`/`typing.Type`. It accepts the existing `meta.descriptor` payload only when its descriptor category is a registered value type: Bool, Fix, Flt, Bits, Index, Unit, Vec, MaskedVec, Tuple or Record, including canonical aliases. Recursively validate parameters, numeric widths, schema IDs/versions and registry digest. No Python class, callable, conversion/reflection hook, foreign model, profile, port, controller or resource descriptor qualifies. In particular, `T: Const[Type] = Dram[Int,32]`, invalid widths and `make_type()` reject before producing a type descriptor.

Module constants may refer to other module constants through an acyclic closed dependency graph; they cannot refer to a formal or body-local symbol. A body-local `T: Const[Type] = ...` is an immutable meta declaration in statement order and may use already in-scope meta formals/constants. Runtime inputs cannot determine its descriptor. All existing collision/shadowing rules apply. Aliases canonicalize to the same descriptor, retaining declaration/use origins rather than creating nominally distinct arithmetic types. `Meta[Type]` uses the same value-descriptor schema for explicit specialization inputs.

Descriptor formation and use-site capabilities are separate checks. A valid Index descriptor does not become a fixed-width Bits value, and a memory, aggregate, ABI, numeric operation or target slot must verify the capability it requires. Zero/default initialization also requires the resource descriptor's registered reset policy; a type alias does not manufacture a zero image. `Const[Type]` itself grants no allocation or runtime value capability. Arbitrary Python `T = ...` and Python `type T = ...` remain excluded source forms.

`MaskedVec[N,T]` is a nameable value descriptor and is admitted in Const[Type] and typed helper signatures. N is an exact nonnegative meta size, never a Bool or runtime extent; T is a recursively checked payload descriptor. Naming the type grants no ordinary Bits, arithmetic or inactive-payload access capability: `M: Const[Type] = MaskedVec[4,Int]` is valid, while `pack(m)` for m:M rejects until explicit materialization. A negative/runtime N rejects at descriptor construction.

User record schemas have one closed source constructor: `Packet: Const[Type] = Record(fields=(("count",Int),("valid",Bool)))`. The fields argument is exactly an immutable tuple of `(literal_name,value_type_expression)` pairs in declared order; empty tuples are allowed. Names must be distinct valid non-keyword source identifiers. Missing/extra constructor keywords, duplicate fields, mutable payloads, handles/leases or non-type field expressions reject. The compiler interns the validated structural schema under `source.record.v1/<canonical-field-schema-digest>`; aliases with the same ordered fields canonicalize together, not to nominal Python classes. Existing library semantic record IDs such as quant.scale_ratio.v1 remain separate registered schemas with their additional checked constraints. `record(Packet,count=3,valid=True)` uses that declared descriptor, requires exactly those fields, and preserves source argument effect order independently of storage field order. No Python class statement, metaclass, annotation introspection or user factory executes. Nested field capabilities are checked recursively; a masked/Index field does not make the enclosing Record ordinary Bits-capable.

## Source operation registrations

Every accepted call/operator/annotation resolves an immutable `SourceRegistration(id,version,export_module,spelling,ast_form,meta_formals,runtime_signature,named_defaults,evaluation_order,lazy_region_slots,semantic_tag,descriptor_ref,effect_bound)`. Parsing/binding uses this table, and checking verifies its descriptor/signature before constructing a semantic operation. Defaults below are compiler-owned data; function default expressions in captured source remain forbidden. An alias points to the same registration ID, not copied semantics. Builder registrations additionally declare pending attachment order rather than inheriting Python host call argument timing.

| Registration group | Export/spelling and exact destination |
|---|---|
| Value formats | `spatial.Bool,Int,IntW,UIntW,Fix,Flt,F16,F32,F64,BF16,Bits,Index,Vec,MaskedVec,Tuple,Record,Unit`. `FixPt[Signed,I,F]`/`FixPt[Unsigned,I,F]` are admitted syntax aliases for Fix; scalar descriptor applications contain only meta/type expressions. Fix/Flt/type validation is the numeric blueprint |
| Stage/ports | `spatial.Meta,Size,Integer,Rational,Type,Const,In,Out,InOut,Read,Write,ReadWrite,Produce,Consume,Observe,Def`; these are annotation constructors, never runtime values. In scalar is immutable ingress, Out scalar is writable result, InOut scalar explicitly wraps mutable ingress/result cell; memory modes normalize to borrowed handles |
| Storage descriptors | `spatial.Reg,Sram,Dram,RegFile,Lut,LineBuffer,Fifo,Lifo,FIFOReg,Channel,MergeBuffer,Lock,StreamIn,StreamOut,FieldStreams,RecordStream,View,Permit,Lease,TransferHandle`; lowercase registered initializer `reg(reset=typed_value)` supplies Reg reset. Constructors use closed resource/endpoint descriptor schema from state blueprint, with explicit element/shape/capacity/lifetime/reset fields. Declaration-only allocating descriptors install their stated default image; View/Permit/Lease/TransferHandle are borrowed/action-result annotations requiring an initializer and never allocate an implicit resource. No Python constructor executes |
| Exact ingress/conversion | `spatial.literal,from_bits,from_binary_float,cast,reinterpret,embed`; exact arguments and operation IDs/modes follow numeric registry. Source numeric literal tokens do not need a literal call. Host binary-float ingress is available only as frozen explicit typed input/constructor data, never by evaluating host expressions in captured code |
| Arithmetic/comparison | Syntax `+,-,*,/,//,%,&,\|,^,~,<<,>>,==,!=,<,<=,>,>=`; registered typed numeric/Bool/Bits/Index IDs only. `//`/`%` on Flt reject as specified; right-shift follows the declared fixed type. Named `logical_shift`, `rem`, `fma`, saturation/checked/stochastic constructors use exact numeric op IDs. `spatial.math.*`/`spatial.rng.*` resolve the finite lists in numeric blueprint, no dynamic member lookup |
| Values/aggregates | `spatial.vec,record,pack,unpack,bit_slice,concat,popcount,select,priority_select,one_hot_select,shuffle,compress,gather_values,vector_map,vector_zip,masked_materialize`; signatures/policies below. Field/index source projection resolves corresponding aggregate/storage registration after receiver typing |
| Views/transfers | `spatial.series,wildcard,view,load,store,gather,scatter,allocate,free,join_transfer,address`; explicit endpoint/alias/snapshot/ordered stream descriptor. `load(dst,src)`/`store(dst,src)` both normalize to transfer.copy with destination first in signature, but evaluate arguments left-to-right at capture. `address(handle)` returns the declared address value type, never a dereference capability |
| Controllers | `spatial.sequential,foreach,pipe_range,pipe,sequential_region,enabled,named,parallel,stream,task,forever,fsm,static,static_range`; region/domain signatures are fixed in this note. Controller semantic policies reference admitted state schemas; hard/soft tuning request annotations are closed data |
| Reductions | `spatial.reduce,fold,tree_reduce,mem_reduce,mem_fold,mem_tree_reduce`; typed contribution/combine DefinitionRefs or admitted numeric combine ID; policy, identity/seed/destination, enable/empty/disabled and map/reduction domains explicitly instantiate reduction schemas. No arbitrary lambda/callback/string-op guessing |
| Calls/contracts/debug | `spatial.call_component,requires,ensures,debug_print,assert_that,breakpoint,exit,request_stop,cancel,checkpoint`; component/requirement/policy schema determines types/effects. `requires`/`ensures` occur at definition header/body contract positions, not arbitrary runtime Python asserts |
| Resource method syntax | Type-resolved `.value,.read,.write,.enq,.deq,.send,.receive,.push,.pop,.peek,.is_empty,.is_full,.occupancy,.close,.reset,.shift,.publish,.acquire,.release` bind only to the exact receiver kind and registered transition ID/mode; no method discovery. FIFOReg `.value` is consume and assignment to it is produce. Published lease `.read` requires live version/owner. Protected memory operations take an explicit registered Permit operand |

The course-facing supplement [[60 - Course Syntax and Compiler Trace]] fixes exact common call signatures, adds Unit/lut/Contribution/contribute/disjoint registrations, and specifies transfer/window/plan-request instances. Its named operations select reduction policy; `policy` is an internal descriptor field, not an extra source keyword.

Exact numeric/transition subregistry rows belong to their owning blueprints; the parser does not invent signatures from these spelling lists. All original callable aliases/migration replacements are mapped in the library/migration recipe blueprint or receive a named source diagnostic. An unimplemented optional transition can remain a typed registered reference with capability error, but an unregistered semantic rule cannot be accepted as a blackbox.

Fifo/Lifo/FIFOReg declarations default to Ordered actions; Channel declares Communicating protocol and send/receive endpoints explicitly. A task's scheduling context does not convert an ordered empty dequeue into blocking receive. A registered descriptor may explicitly choose a different admitted mode, which is semantic/profile data. Endpoint role/capacity/readiness is checked against the state blueprint's transition schema. Annotated `p:Permit[LockSchema] = lock.acquire(keys)` and `l:Lease[PublicationSchema] = buffer.acquire(...)` bind typed action results; their release/cleanup is registered and generation/owner checked. Async transfers return `TransferHandle`, whose ownership/visibility obligation persists through `join_transfer`; a handle cannot be treated as a scalar or discarded without registered cleanup.

`for` binds one Index. `with` contexts in the controller group bind no `as` value; task names are meta strings. FSM uses helper signatures `test(state:S)->Bool`, `action(state:S)->Unit`, `next(state:S)->S`, S Bits-capable, with captures closure-converted. Reduction contributions bind Index (or the explicitly declared map coordinate tuple), combines bind exactly two numeric/aggregate values of the declared accumulator type. Component/helper calls check named arguments by formal identity; positional call arguments are assigned in declared signature order; missing/extra/duplicate keywords and `**` expansion reject. A source nested helper may receive captured read/write/endpoint capabilities; typed callback slots are DefinitionRefs, never ordinary runtime values.

Builder receiver `.at(index)` creates an immutable unsequenced LValuePlan. To avoid the R004 compact-call ambiguity, `k.write(plan,value)` and `plan.write(value)` attach value pending effects before receiver/address pending effects, then write. Merely constructing the plan commits nothing. This is an explicit proposed builder attachment rule; it is not a claim about ordinary Python argument evaluation. `k.aug_write(plan,op,value)` instead attaches address/read before RHS as the source augmented assignment does. Test compact effectful addresses against explicit-temporary forms; freeze still rejects duplicate/moved/dropped leaves.

Meta expression typing/evaluation is table driven. Integer `+,-,*,//,%`, unary signs, comparison and bit operations use exact signed integers; division/remainder require nonzero denominator; `//` is floor and `% = a-floor(a/b)*b`, including negative divisor. Integer shifts require nonnegative counts. `/` is unavailable on structural integers; explicit `rational(n,d)` makes exact rational data. Rational arithmetic is permitted only in registered rational slots/constructors. Bool short-circuit is lazy, comparisons Bool-valued, and no integer truth conversion occurs. `Size` operands promote to mathematical Integer for arithmetic; only `size(expr)`, binding to Meta[Size], and shape/domain validation enforce nonnegative Size. Thus `N-1` can be -1 as an intermediate without silently wrapping, while using it as an extent fails. Registered record field access is schema checked. A constructor's registry entry fixes formal types, result tag, validation and profile ID; unknown constructor rejects without evaluation.

Budgets count source bytes, nodes, maximum integer bit length, definition/call depth, and static expansion nodes. Limits are explicit profile integers stored in acquisition/specialization metadata. Source-byte and parser/node admission use the preparse rules above; exceeding a later evaluator/expansion bound yields a specialization resource-limit diagnostic, distinct from a numeric language fault. Before computing multiplication/power/expansion, conservatively estimate growth and check the budget; every recursive evaluator step consumes fuel. Do not allocate a gigantic intermediate and only then diagnose it. Meta powers require nonnegative bounded exponent; runtime transcendental semantics belong to the numeric registry, not this evaluator.

## Runtime types and bidirectional checking

Owned descriptor algebra:

```text
ValueType = Bool | Fix(signed,I,F) | Flt(P,E) | Bits(W) | Index
          | Vec(N,ValueType) | MaskedVec(N,ValueType) | Tuple(ValueType*)
          | Record(schema_id, ordered(field_name,ValueType)*) | Unit
HandleType = Storage(kind,element_type,logical_shape,capability,lifetime_schema)
           | View(storage_ref,coordinate_map,logical_shape,capability,lifetime_schema)
           | Endpoint(protocol_id,payload_type,role,capability)
           | Permit(lock_schema,owner_domain) | Lease(publication_schema,owner_domain)
           | TransferHandle(transfer_schema,owner_domain,borrowed_domains)
CompilerType = DefinitionRef(signature_id) | OrderToken(domain_id)
```

All descriptor parameters validate before value checking. Shapes are tuples of closed structural expressions, with static capacity separate from dynamic logical extents. A signature extent refers to an eligible formal ID: an immutable invocation Index port or a helper/component Index value formal, as well as its declared bounds. At a helper/component call, substitute each formal extent reference with the already captured actual Index value reference for that call activation; retain the caller's value identity and range obligations, and check the actual borrowed view against the substituted shape before body effects. Actual Index argument expressions execute once in normal caller argument order, never by reevaluating an annotation. For example, `copy(src: Read[Dram[Int,n]], n: Index)` can receive different immutable local n values at different call sites; it does not require n to be a top-level port or specialize the helper globally to the first call's extent. A target must derive a finite representation for runtime Index values from the required range/ABI contract; Python's unbounded interpretation is the reference meaning and is not a promise of unbounded hardware storage. Handle types cannot enter ordinary numeric, comparison, packed aggregate or implicit truth slots. Permits/leases cannot be copied into value aggregates or escape their owner; their acquire/release protocol is verified separately from numeric SSA use.

Vec length/tuple or record field count may be zero. Bits(W) permits W>=0 for empty aggregate packing, while numeric Fix/Flt retain their positive-width format rules. Bits(0) has one value, represented by the empty bit string and zero-byte ABI slot; ordinary dynamic extraction from an empty Vec always faults. A target without zero-width fields omits that field under a verified ABI mapping or diagnoses capability; it must not silently invent a numerical element. Record field order is declaration order, and field names must be unique even if two have equal types.

MaskedVec owns N payload lanes plus N validity Bools. Inactive raw payload is canonical zero solely for storage/serialization determinism, **not usable data**. `masked[i]` returns T only after active bounds and validity proof/guard; false validity faults `E-LANE-INACTIVE`. `masked_materialize(masked,default:T)` explicitly fills inactive lanes and returns Vec(N,T). Ordinary arithmetic, Bits pack/reinterpret, FSM state or `.values` projection of MaskedVec reject until materialized, unless a registered mask-preserving operation has its own validity rule. Raw artifact serialization preserves the MaskedVec descriptor/mask; it cannot confer ordinary Vec authority. Empty aggregate storage still retains backing identity, lifetime and per-axis/init meaning despite zero byte span.

### Storage and representation capabilities

The proposed registered reference profile separates typed local cells from a packed byte ABI; descriptor validity alone grants neither. Its closed capability ledger is:

| Use site | Admitted descriptor and obligation |
|---|---|
| Private Reg/RegFile/Sram cell | The state's closed ValueStorage union: Bool, numeric/raw Bits, exact Index, recursively typed Vec/Tuple/Record, MaskedVec and Unit. No handles, callbacks or arbitrary host objects. Reads/writes retain the complete typed value, including lane validity; SRAM initialization stays per logical cell |
| Bare Reg/RegFile reset | Registered ZeroImage(T): the existing numeric/Bool/Bits/aggregate images, exact mathematical 0 for Index, and all-invalid MaskedVec lanes with recursively registered zero payloads. An unavailable image requires explicit supported reset or TYPE.RESET_IMAGE. The selected checked image is stored in the allocation |
| Byte-backed Dram/host Backing and packed queue payload/ABI slot | Bits-capable descriptor with a registered finite layout; Index and MaskedVec, including nested occurrences, reject with TYPE.STORAGE_ELEMENT_CAPABILITY at source checking. Explicit embed or masked_materialize produces a suitable value only when its resulting descriptor has Bits; neither conversion is inserted |
| Structural In[Index] scalar port | Exact IndexInput ingress and structural bounds checks, independently of the byte ABI; it remains an eligible immutable shape input |
| Target local typed-cell realization | Proved finite range/invariant and checked width/conversion for every stored Index, and a layout preserving every MaskedVec validity bit/guard. Absent range/layout yields a scoped target capability diagnostic; semantic reference acceptance does not imply a plan |

For example, bare `r:Reg[Index]` starts at exact 0, and a loop-carried `r.value = r.value + 1` uses the Index destination context without 32-bit wrapping. A bounded reference run may exceed 2**31-1 or 2**32-1. A target must prove an inductive range for every reachable stored value; a forever increment with no finite invariant has no finite Index plan, even if one short simulation fits. A `Reg[MaskedVec[4,Int]]` starts as an initialized typed cell whose four lanes are invalid; storing/loading a masked value preserves those guards. Reading an inactive lane still faults. Materializing with an explicit default returns a Vec and does not mutate the original mask. This does not grant MaskedVec ordinary Bits, FSM-state, or packed-channel capability. Other resource profiles must declare their own closed element capability rather than inherit every ValueType automatically.

Ordinary numeric operands require exact equal descriptors. The numeric blueprint owns operation IDs/modes and contextual literal quantization. The checker implements two mutually supporting functions:

```text
check(expr,expected,slot):
  if literal-only numeric tree: check every leaf/operator under expected and slot
  elif Bool/relational tree: require Bool result; synth/check numeric leaves separately
  elif typed expression: t = synth(expr,slot); require t == expected
  elif registered call: instantiate registry signature; check named arguments
  else: diagnostic; never insert a numeric cast

synth(expr,slot):
  resolved typed name/projection -> declared result type
  context-free integer/signed integer literal -> Int32, range checked
  context-free decimal -> ambiguous literal diagnostic
  binary expression with typed sibling -> check literal-only other side in sibling type
  fully literal expression without context -> synth default integer if all integral
  registered operation -> match its exact signature and return instantiated result type
```

Destination context flows through a literal-only numeric subtree; it never widens or recasts an already typed operand. Bool-result comparisons are checked separately: `check(1<2,Bool)` synthesizes Int32 operands and never tries to quantize 1 or 2 as Bool. A context-free decimal comparison needs an explicit operand format. Unary sign is part of literal ingress, so Int32 `-2147483648` does not reject the positive magnitude first. Comparison-chain operands use one common compatible numeric/ordered type, pairwise comparisons Bool, and operand evaluation retains lazy shared-middle structure. Aggregate constructors supply each field/lane expected type; aggregate joins require identical full descriptor, not only identical packed width. The admitted quantization scale is `Record(quant.scale_ratio.v1)` with typed sign/numerator/denominator/exponent fields and numeric-blueprint positivity/bounds checks; it is not an arbitrary runtime rational type.

`Index` is a separate structural/runtime category. Registered address/domain/shift/exponent slots accept Index; integral Fix with F=0 can be projected to exact signed/unsigned mathematical value in an **index slot** without changing its existing numeric operation history. Fractional/floating/Bool indices reject. An index is not implicitly a numeric data value: use `embed(T,index,overflow="checked"|"wrap")`, operation `num.embed_index`, only for integral Fix target. Its default is checked. Ordinary numeric casts and bits reinterpretation remain named numeric registry operations.

Index expression IDs are the finite `index.add/sub/neg/mul/div_floor/mod_floor/min/max/and/or/xor/not/shl/shr/eq/ne/lt/le/gt/ge` registry with exact mathematical integer results, Bool comparisons, floor division/remainder and nonnegative shift counts. Divide-by-zero/negative shifts carry fault tokens. `/` on Index rejects. An explicitly annotated Index declaration initializer, including an alias resolving to Index, is an Index expression slot. A literal-only integer subtree there uses exact structural arithmetic: `x:Index=2147483647+1` is 2147483648, not wrapped Int32. Bool/fractional/decimal initializers reject; an already typed Int expression keeps its original typed arithmetic and only then permits the ordinary integral-to-Index slot projection. In an Index expression slot, meta Integer/Size constants lift exactly to Index; outside that slot they cannot silently change a typed accelerator operand. Runtime Index values store exact signed integers, not the numeric engine's fixed-width payload. This closes source `base+TILE` and domain arithmetic without choosing a platform index width.

This deliberately repairs illustrative R001 E2's `values[0,i]=i` to `values[0,i]=embed(Int,i)` and `contribution(i:Int)` to `contribution(i:Index)`. The source/builder acceptance corpus must record those repairs. It must not let one frontend insert a hidden embedding while the other rejects it. All original numeric index-as-data capability remains expressible with an explicit policy.

Required traits (`Bits`, `Order`, `Num`, etc.) are table-derived capabilities of owned types/registered operations, not Python `isinstance` checks on arbitrary external objects. User-extensible numeric semantics require a versioned admitted type/operation profile and conformance evidence; a class overload cannot become semantic authority.

## Writes, scalar outputs and structured result merging

An annotated scalar/value declaration defines one immutable SSA identity after its initializer finishes. Annotated Reg/storage creates a handle. `x=...` to an immutable value is `E-VALUE-ASSIGN`; recurrence uses `r:Reg[T]` with its registered ZeroImage or `r:Reg[T]=reg(reset=...)` with an explicit supported reset, registered `r.value` reads/writes, or indexed storage. No untyped first assignment infers a new local. Shadowing and declaration remain distinct from mutation.

Ordinary write normalization is RHS ANF evaluation, then receiver/address ANF evaluation exactly once, then capability/bounds/initialization checks, then write. Augmented assignment is receiver/address capture, active read, RHS evaluation, typed operation, write to the captured address. Lvalues are typed `LValuePlan(receiver,coordinates,field,read_cap,write_cap,origin)`. The plan is immutable; its evaluation yields a captured runtime address, not a delayed closure. A write-only output cannot be read by `+=`. Faulting writes commit nothing themselves; earlier ordered operand effects remain committed.

Scalar output ports begin uninitialized and are mutable ordered external-result cells. Multiple ordered writes are legal and last successful write is the value at successful completion. Success requires every declared scalar output initialized on every reached successful exit. A branch intersects output initialization; a possible zero-trip loop contributes no unconditional guarantee. Partial outputs in a fault/wait/cancel result remain incomplete, as the host contract requires. Concurrent writes to the same output require explicit adopted ownership/arbitration; accidental scheduler order is insufficient.

A terminal returning if/else normalizes to `control.if` with declared result tuple and token; each arm independently produces values with exactly the signature types. Its result identity belongs to the outer owner. Arm-local storage/endpoint/permit/lease cannot be yielded unless a separately admitted borrowed-result signature explicitly permits it. A conditional **value** expression lowers similarly and executes only the chosen arm's effects/faults. There is no hidden export of branch locals or source function-wide Python variable scope.

`select(flag,a,b)` is a total-pure value selector of already evaluated equal-type values. A direct pending effect in a pure-selector operand rejects; a named value previously obtained by consume is legal. `with enabled(flag)` gates its entire body, including effectful operand evaluation. Function keyword `enable=`/`active_mask=` affects only its descriptor's action on already captured operands; it does not make ordinary call argument evaluation lazy. Source sugar that promises lazy enabled operands must normalize to an explicit region by a registry entry marked `lazy_region_args`. Loop inactive lanes gate their whole body before any address/value/effect operation. This prevents inactive-lane claims from contradicting ordinary left-to-right expression evaluation.

## Aggregate and view algorithms

`vec(T,[e0,...,eN-1])` fixes length N and checks each expression against T in order; `record(Schema,field=value,...)` requires exactly the schema fields and stores them in schema declaration order, while argument effects retain written call order. Tuple is a fixed aggregate, never a dynamic iterable. Equality compares every declared field/lane by its type's equality and combines Bool results; NaN/signed-zero behavior therefore follows the numeric profile. Handles/leases are not aggregate fields. Dynamic Vec extraction checks `0<=i<N`; fixed Index slots are exact mathematical projections, with no element-zero fallback.

Pack concatenates each declared field/lane raw bits at increasing low-bit offsets; unpack requires exact aggregate total width and partitions those offsets without arithmetic NaN canonicalization. `bit_slice(x,lo,width)` uses half-open `[lo,lo+width)`, requires nonnegative lo/width and endpoint<=W, and permits width0. Concat's first argument occupies low bits. Popcount returns Index (or explicitly embedded numeric result); shift operands use the numeric/Bits registry's declared total behavior.

`priority_select(flags,values,default)` chooses the lowest true index; no true flag returns the required explicit default. `one_hot_select` requires at most one true flag, faults on conflict, and uses explicit default on zero; the optional `empty="fault"` replaces default with a fault. Its already evaluated values have equal types. `compress(values,valid)` returns a registered record `{values:Vec(N,T),count:Index}`: stable increasing-index active values occupy low positions, remaining positions are **defined all-zero raw values** recursively by type, count is the number of true flags. This value operation is distinct from a queue receive's masked unusable output. `shuffle(values,permutation,default)` checks every active source Index; a registered `None` meta lane maps to explicit default, never to stale storage.

`vector_map(values,body=DefinitionRef)` and `vector_zip(a,b,body=DefinitionRef)` use a structured lane region with ascending Index and the selected typed element(s). Lengths must match for zip. Callback effect bound may be total-pure or ordered; lanes execute in increasing ordinal and yield the typed result/token. Communicating callbacks reject here; explicit tasks/stream controllers express that concurrency. An active-mask variant gates the callback region before operand/body effects and produces a MaskedVec, with no fabricated usable inactive result. Pure variants carry no token only when the callback graph is proved total-pure. This supports compositional vector functions without eager source expansion or host callbacks.

View normalization composes mathematical coordinate maps and logical extents, not flat pointers. A source slice `start:end:step` has the same signed-step half-open domain/trip count as controllers; omitted positive-step start/end are 0/axis_extent, omitted negative-step start/end are axis_extent-1/-1. No Python negative-index adjustment or clipping occurs. Each retained axis maps its local coordinate k to start+k*step; an integer index drops that axis and fixes its source coordinate. Wildcard retains the full axis with origin0/step1. Axis-count mismatch and step0 reject. Endpoints are captured once; pure view creation does not itself read or initialize memory. Every active eventual access checks its own view extent and all composed underlying logical coordinates before flattening. Thus an empty view grants no access, and an unused nonempty out-of-backing view cannot prove safe reads merely from its local extent. Transfers preflight all selected coordinates/init maps according to the state blueprint before destination writes.

## Debug formatting, assertions and observation hooks

`debug_print(template,*values)` is a registered variadic intrinsic, not a captured variadic function definition. The template is an acquired literal string; positional payload expressions evaluate left-to-right once and the resulting event is ordered by its token. The event contains exact template bytes plus typed bits/Bool/Index/aggregate payloads and origins. The reference run records this event rather than calling host `print`/`__format__` inside the kernel; an explicitly selected host renderer projects events afterward. A target needs a bounded packet/trace adapter with that event projection or reports unsupported debug capability.

Closed template grammar: ordinary literal Unicode scalar text, doubled `{{`/`}}` for braces, and placeholders `{i}` or `{i:tag}`, where i is canonical nonnegative decimal argument index and tag is one of `bits,int,fixed,float,bool`. No automatic index, field/member access, conversion flag, nested format, width, precision or alignment. Lone/malformed brace, nonexistent index, unknown tag or tag/type mismatch rejects at source check. Placeholders may repeat a captured value without re-evaluating it. The schema identifies `debug.format.v1`; source f-strings and Python Formatter are never invoked.

Deterministic renderer:

- `bits` (default for Numeric/Bits/ordinary packed aggregates): print canonical type descriptor label, `:0x`, then exactly ceil(W/4) lowercase hex digits with zero high padding. W0 has empty digits. Aggregate packing is the declared low-field-first layout; MaskedVec/handles/permits/leases reject this format.
- `int` (default for Index): print exact mathematical signed decimal for Index or decoded integral Fix(F=0), with minus only for a negative value. No host float conversion. A fractional Fix rejects.
- `fixed`: decode signed/unsigned raw r. Form integer `abs(r)*5^F`, write decimal digits padded to at least F+1 positions and insert the radix F digits from the right; trim trailing fractional zeros/radix, prepend minus iff r<0. F=0 is ordinary integer decimal. This is the exact value r/2^F, without approximation or Python `__format__`.
- `float`: decode bits using numeric profile without arithmetic/NaN quieting. Print signed zeros `+0`/`-0`, infinities `+inf`/`-inf`, NaN as `nan:0x` plus full bits. For finite nonzero value sign*M*2^e, remove every factor of two from positive integer M, then print optional minus, `0x` plus lowercase M hex, `p`, and a signed decimal exponent (including + for nonnegative). This unique dyadic rendering is exact for generic formats and does not promise shortest decimal formatting.
- `bool` (default for Bool): `true` or `false`; integers cannot acquire this format by truth conversion.

Rendering has explicit output/decimal-bit budgets; exceeding a host rendering budget yields a rendering resource-limit record while preserving the original event bytes. It is not a source arithmetic fault or permission to drop the event. Formatter tests use handwritten fixed negative/fraction, float subnormal/signed zero/NaN, repeated placeholders, braces, Unicode and invalid MaskedVec cases.

`assert_that(predicate,message=literal)` requires Bool, observes it at its token point and faults before the next effect if false. Its message is literal data, not executable Python exception formatting. `breakpoint(label=literal)` records a debug observation event and returns the reference RunResult Breakpoint outcome with its observation-pause continuation; resumption advances after the event, never re-evaluates operands. This host debugger pause is an explicit observation boundary, not a language deadlock. A hardware debugger hook has a declared adapter/control protocol or capability error. `exit(code=Index_literal,reason=literal)` begins declared invocation/subtree stop/drain and yields Stopped with incomplete outputs; a separately declared successful-completion policy may instead produce Completed only after its normal completion/output checks; it never throws a host exception that bypasses cleanup.

## Helpers, components and declarative library callbacks

Definitions use `Signature(meta_formals,value_formals,borrowed_formals,result_types,effect_bound,requires,borrowed_results)` with closed formal modes:

| Mode | Check and call behavior |
|---|---|
| `value:T` | Immutable argument checked exactly against T; no hidden address/reference conversion |
| `storage:Read[M]`, `Write[M]`, `ReadWrite[M]` | Borrow caller handle with element/rank/shape/capability requirements; actual backing identity and coordinate map remain shared |
| `endpoint:Produce[P]`, `Consume[P]`, `Observe[P]` | Borrow typed protocol role; communicating use requires task context and correct owner/arbiter |
| `meta:T` | Freeze/specialize before runtime signature instantiation |
| `template:Def[Sig,EffectBound]` | Closed acyclic DefinitionRef selected statically; exact signature/effect bound; no runtime dispatch or Python callable |

Kernel `In/Out/InOut` annotations describe a host launch contract. `as_component(kernel_template,interface=...)` is an explicit **host construction** projection that maps its formals to the component roles above. It verifies that each mapped port has a legal borrowed/value role and names result/capability behavior. `call_component` in a represented region binds that ComponentRef; it never launches another host program or allocates a new port backing implicitly. Component local allocations have fresh call activation IDs and die at call completion unless a defined publication/lease protocol extends them. Reusing a kernel as a component is not merely renaming its ports.

Nested helpers become closure-converted definitions with explicit environment formals in deterministic first-use order. A captured storage/endpoint stays borrowed, with owner lifetime no shorter than call. Every call gets an activation path; each local allocation's runtime identity is `(allocation_site_id,activation_path,generation)`. Helpers are checked in reverse topological order of the reachable call graph per specialization/type signature. Calls use summaries rather than eager whole-program inline expansion; inlining is an optional verified pass.

`pure` means total-pure value computation: no allocation/state/environment/RNG/observable status or possible language fault, including callee effects. `ordered` permits finite ordered effects/faults but no suspend/fork/forever; `communicating` permits declared task/protocol effects and therefore requires a communicating call context. A reduction combine uses a separate numeric effect bound permitting specified arithmetic faults in declared topology order; it is not mislabeled total-pure. An ordinary helper that may divide by zero cannot claim `pure` unless its precondition/proof makes that operation total for every admitted call.

Each definition has a derived summary, never a trusted author's declaration alone:

```text
CallSummary = (
  signature_id, specialized_definition_digest,
  effect_tree, formal_access_regions, required_capabilities,
  initialization_preconditions, definitely_initialized_postregions,
  returned_borrow_maps, allocation_sites, fault_suspend_termination_kinds,
  requirement_templates, proof_dependencies)
```

Effect trees retain sequence/choice/loop/task structure. Access regions use formal backing IDs with coordinate expressions or UnknownRegion. Guards depending only on formal pure expressions can be substituted; unresolved callee-local guards become conservative alternatives, not assumed false. Guaranteed post-initialization intersects all successful exits. An admitted `ensures(initialized(view))` is a verified proof or an active exit guard that faults before successful completion; it is never trusted documentation.

Call instantiation substitutes actual formal handles and coordinate maps **before** checking conflicts/init effects. Two formal arguments aliasing the same backing coalesce; their writes affect each other's reads. A helper returning a borrowed view must list the formal that owns it and retain that formal's lifetime/capability. Initially only views into declared borrowed formals may escape a helper/component; callee-local allocation, endpoint, permit and lease results reject unless a versioned publication protocol explicitly transfers ownership. Memory-reduction contributions are a distinct registered region contract: the mapper's temporary memory remains leased through that contribution's element reads/combine stage, then releases before the next activation; it does not become a general escaping local return.

Declarative `spatial.lib.*` modules are source templates using these same signatures. Map/activation/comparator/gradient helper arguments are typed DefinitionRefs selected at specialization; their bodies are checked through the same call DAG. There is no whole-application recognizer, hidden native kernel meaning or arbitrary host callback. A library recipe must specify its callback effect bound and numeric modes, rather than assuming every callback is pure.

## Owned unchecked records and builder effect ledger

The common unchecked representation is a frozen sum-of-products with tuples and admitted immutable descriptors only. Source acquisition and builder do not create alternative semantic IRs.

```text
UncheckedProgram(schema,profiles,definitions,exports,entry_id,meta_snapshot,
                 dependency_refs,symbols,origins,requirements_requested)
Definition(def_id,signature_expr,environment_formals,root_region,origin_id)
Region(region_id,parent_owner,kind,binders,captures,statements,terminator,origin_id)
Statement(tag,symbol_or_lvalue,expressions,owned_regions,attributes,origin_id)
Expr(tag,operands,closed_attributes,symbol_ref_or_literal,creation_owner,origin_id)
Literal(kind,token_or_exact_record,unary_sign_tree,origin_id)
PendingEffect(effect_id,registered_op_id,operand_tree,creation_owner,origin_id)
```

Expression tags are `ref,literal,unary,binary,bool_lazy,compare_chain,if_expr,call,field,index,view,aggregate`. Statement tags are `declare,write,aug_write,discard,if,loop,context,call,return,requires,ensures`. Definition/type/intrinsic refs carry kind-specific IDs, not arbitrary string lookup at execution. A builder may submit malformed records; freeze/check revalidates every ID/owner/arity rather than trusting constructor success.

Pending expressions have immutable leaf effect IDs. Every builder constructor recursively collects pending leaves but does not commit them. A sequencing constructor owns their attachment in declared left-to-right expression order. The outstanding ledger is independent of Python object lifetime. Freeze checks that each pending leaf has exactly one attachment in its creation owner; v1 admits no pending-effect capture exception, including dropped garbage-collected wrappers. `e=q.deq(); let(v,e+e)` repeats the same leaf and rejects; `v=let(q.deq()); use(v+v)` is a single consume and legal. A repeated expression tree is not silently memoized into a consume, nor duplicated into two consumes. `discard(q.deq())` explicitly attaches then discards result. Moving a pending leaf into another branch/owner rejects rather than inferring programmer laziness.

Source normalization generates the same literal/expression tree and ordered effect attachments without a host wrapper ledger. Compare normalized source and builder meaning with independently generated origin maps; matching result values alone cannot establish parity.

## Canonical immutable records and checked ownership

These are proposed internal records and algorithms, not implemented classes or a new public host API. [[PY-R017 - Compiler Representation Comparison]] contains the alternatives, bounded measurements and strongest objection: real use-heavy and plan transformations may make index/editor costs substantial. The first implementation must measure those costs with actual provenance and requirements; a small-record benchmark does not remove them.

Use frozen, slotted Python records with tuples, exact builtin scalar fields and recursively validated registered descriptor payloads. Records have no mutable parent/use lists, invocation state, analysis cache, user callback or arbitrary object field. Lists/dictionaries may be temporary construction workspaces; validation copies their accepted contents into the closed owned representation before publication. `frozen=True` alone neither checks transitive ownership nor creates a security boundary against arbitrary Python code, which runs outside the captured-language guarantee. The trusted checker constructs the owning records; callers cannot supply a checked flag or bypass it by instantiating a similarly named dataclass.

The minimum semantic storage spine is:

```text
SemanticRecords(schema_version, exports, types, functions, resources,
                profiles, requirements, model_refs)
FunctionRecord(def_id, signature, environment_formals, body_region, origin_id)
RegionRecord(region_id, signature, arguments, operations, origin_id)
OperationRecord(op_id, family_tag, operand_refs, result_types,
                registered_attributes, owned_regions, origin_id, requirement_ids)
ValueRef = RegionArgument(region_id, ordinal) | OpResult(op_id, ordinal)
PlanRecords(schema_version, semantic_digest, target_digest, binding_contract,
            machine_graph, storage_plan, numeric_realizations, abi,
            constraints, correspondence, obligations)
```

Every plural collection is an immutable tuple of its registered record type, except an explicitly declared closed scalar payload. The family table below fixes operation payload alternatives; a free-form attribute dictionary is not admitted. A region's ordered operations include exactly one final registered terminator. An argument/result's type comes from its region signature/result_types and type table, not an unchecked hint on a use. Function/resource/type references have separate ID kinds. `PlanRecords` uses the state/HLS blueprint's machine/transition schemas and references checked semantic meaning; it is not admitted as a source operation family.

IDs identify declarations/operations **within a revision** and are distinct from Python identity and artifact numbering. Preserve surviving IDs across an edit; generated IDs use a deterministic pass/owner/local-ordinal namespace checked for collisions. A copied owned region receives fresh region/op IDs and remapped argument/result references. Each owned operation/region occurs at exactly one position within a revision: sharing immutable records between revisions is legal, inserting the same owned region twice in one revision is not. Resources duplicated by a transform require fresh allocation-site identities and the existing activation/generation rules. Canonical artifact numbering remains the package blueprint's deterministic traversal; diagnostic lineage retains source and transformation origins separately.

`CandidateProgram` owns SemanticRecords plus source/provenance/dependency records and is **untrusted**. The trusted `check` path validates exact schemas, transitive ownership, unique IDs, references, signatures, regions/tokens, types/effects/capabilities/lifetimes, requirement dispositions and the requested profile, then constructs a private `CheckedProgram` wrapper over the accepted immutable root. The wrapper exposes the existing query/export/simulate/plan interface and no mutable graph. Its checked revision records semantic/provenance/registry/profile/schema and checker-rule identities. Freezing, deserialization or a cast only produces a candidate; artifact import always reruns this gate. A valid semantic revision still grants no target eligibility. `CandidatePlan` similarly passes plan-specific correspondence, physical/resource/ABI/protocol and requirement verification before becoming the existing public ImplementationPlan result.

### Traversal indices and minimum rewrite operations

Build `RecordIndex` by one deterministic traversal of a candidate/revision: `node_by_id`, `parent_region_and_ordinal`, `value_definition`, `value_users` as ordered `(user_op_id, operand_slot)` tuples, and `definition_callers`. Include control-operation capture operands in the use index; nested bodies refer only to their own declared arguments/results. Duplicate ownership, unresolved references and invalid result slots diagnose before analysis. Index construction is O(nodes + operand uses); it is required work for passes that need those lookups, not a zero-cost property of frozen records. Indexes live in private revision-scoped side tables and are never serialized as trusted analyses or attached to shared semantic nodes. Public queries return immutable views/records.

The initial internal `RecordRewriter` needs only three operations: replace an operation with an ordered tuple plus an explicit old-result-to-new-ValueRef map; replace a region with a candidate region and explicit binder/capture map; and clone an owned region with fresh IDs and complete local remapping. Empty replacement is deletion and requires no remaining live value/token use, plus the requirement/provenance transfer below. Replacing a value rewrites actual recorded use slots, checks types, and updates enclosing capture operands without introducing implicit ancestor uses. Cloning remaps owned region arguments and internal results; external values remain explicit captures. Unknown or cross-owner substitutions reject.

A rewriter may rebuild the whole candidate initially. A later local implementation rebuilds affected regions and ancestors and shares untouched immutable records; it must preserve the same checks. During editing, use transaction-local mutable maps if useful, then rebuild/validate the complete candidate index before publication. Do not maintain a supposedly current global index while an old revision remains queryable. A failed rewrite discards its candidate/maps and leaves the input revision untouched. No general persistent-graph library, generic CFG support or incremental proof updater is required for the first slice.

The state blueprint may derive an `ExecutionProgram` with resolved dispatch/slots/continuations from a CheckedProgram. It is a revision- and executor-version-keyed execution cache, not a second language or canonical artifact. Retain correspondence to semantic operation/region IDs and their guards, effect order and source origins. Any prebound dispatch selects trusted registered numeric/protocol handlers; it cannot import host callbacks from source/artifacts. Mutable Frames/requests/state belong to each Invocation. A changed checked revision, registry/profile or executor schema invalidates the derived cache; reference execution and planning still share the same canonical meaning.

## Closed semantic operation families

Checked semantic IR uses only the following tags and their admitted descriptor references. The table is the finite top-level sum. A registry ref below must point to a versioned closed descriptor with exact fields and a checked implementation; it cannot contain Python callbacks or arbitrary opcode strings. Unknown family/tag/version/field rejects at import/check. Numeric and protocol registries may add versioned entries only through a reviewed specification and acceptance cases.

All operations carry `op_id`, exact typed operands/results, immutable semantic attributes, `origin_id`, and `requirement_ids`; effectful/faulting operations additionally consume/produce an OrderToken in their owning task domain. Attributes include semantic profile/transition/policy refs, never analysis `proved=True` or invocation state.

| Family/tag | Operands/results and closed semantic attributes |
|---|---|
| `value.constant` | Exact typed bits/Bool/Index/aggregate value; no effect token; numeric ingress record retained in lineage |
| `index.eval` | Closed exact structural integer ID, Index operands/results or Bool comparison, captured zero/shift fault rules and token when may-fault; no wrapping platform-width arithmetic |
| `numeric.eval` | Numeric registry `op_id`, exact type descriptors, overflow/rounding/profile/certificate refs, typed value operands/results. May-fault/RNG/observed-status entries take token and explicit resource operands |
| `aggregate.build/extract/update` | Vec/Tuple/Record schema ID, static lane/field or checked dynamic Index; complete result descriptor; dynamic bounds/fault token where needed |
| `bits.pack/unpack/slice/concat/popcount` | Fixed ordered bit layout, checked slice bounds, typed results; low-word-first layout is semantic, byte ABI separate |
| `aggregate.select/priority/one_hot` | Bool selectors, already computed typed values, explicit empty default/fault policy; direct pending effect forbidden. One-hot conflict/default fault carries token |
| `aggregate.shuffle/compress/gather` | Typed lanes and mask/permutation; stable increasing-lane packing, valid-count result and explicit inactive lane value policy; no consuming action inferred |
| `aggregate.map/zip` | Vec length(s), statically bound callback DefinitionRef, lane/capture region, optional active mask; exact result Vec/MaskedVec and ordered callback token when effectful |
| `aggregate.masked_extract/materialize` | MaskedVec, captured Index/default value; extraction bounds/validity guard with token, or explicit default fill returning ordinary Vec; no raw payload bypass |
| `storage.allocate` | Allocation site, kind, element/shape/capacity, initializer/reset image, owner lifetime; produces Handle + token. Persistent declarations link session schema and explicit reset trigger |
| `storage.view` | Borrowed Handle, coordinate map, retained/dropped axes, logical extents and capability; preserves backing/generation. Conditional view selects among declared alternatives with guards, never creates fresh backing |
| `storage.read/write/observe/reset/shift` | Handle, captured Index coordinates, payload/mask, operation/profile ID; exact active bounds/init/update rules; token and typed value/status where applicable |
| `transfer.copy/gather/scatter` | Typed endpoint Handles/views, count/order/address stream, completion/alias/snapshot policy and captured payload; token. Array copy snapshots source before writes; FIFO endpoints consume/produce in order |
| `memory.dynamic_allocate/free` | Closed bounded-pool protocol ref, shape/lease/capacity requirement, ownership generation; token plus Handle/Unit; no unbounded Python allocation meaning |
| `state.action` | Versioned protocol transition descriptor from state blueprint; explicit resource/generation/mode/capability, captured payload/address/mask, typed result/outcome, checkpoint policy and token |
| `control.if` | Bool condition, explicit value/handle captures, parent token; exactly two isolated regions, same result tuple + selected token |
| `control.loop` | Domain(start,end,nonzero signed step), mode Sequential/Foreach/Pipe, enable/admission/stop refs, par/II preferences, captures and optional explicit carry tuple; body binder Index + carries + task token; yields carries/token; parent completion token |
| `control.region` | Ordered Pipe/Sequential/Named/Enabled wrapper; explicit captures/enable/schedule intent, single region and result/token tuple; no accidental child concurrency |
| `control.task_group` | Parent token/captures, child/task IDs, fork/join/stream start policy, resource ownership/arbitration, admission/stop/cancel policy; N child regions with distinct task domains; joined values + parent token |
| `control.forever` | Task domain, captures, adopted stop/environment/admission policy, repeated body region and checkpoint; no fabricated finite domain or universal completion claim |
| `control.fsm` | Bits-capable state type/start value; Test, Action and Next regions with explicit state/captures and effect bounds; activation/stop policy; typed final state + token |
| `reduction.scalar` | Numeric policy lawful/fixed_tree/ordered_fold, map domain, identity/seed/destination/disabled/empty policy, contribution region, combine DefinitionRef/law/topology, completion publication; value + token |
| `reduction.memory` | Separate map and destination coordinate domains, destination Handle, leased contribution-memory schema, identity/seed/old-cell policy, effect order and typed combine; token/completion. No general local-memory escape |
| `call.helper/component` | DefinitionRef, instantiated signature, explicit environment/borrowed/value operands and token if required; typed values/borrowed results + token; local activation identities and summary refs |
| `environment.receive/send/close` | Endpoint/environment trace schema, framing/field/record semantics, readiness/close protocol, captured payload and task token; result/outcome schema |
| `foreign.value/actor` | Model/manifest/interface/profile refs, explicit state/input/environment/resource operands, declared reset/fault/suspend behavior and token as required; no live closure payload |
| `diagnostic.print/assert/breakpoint` | Literal format/typed arguments or Bool predicate, observable/fault/hook policy, token; unsupported target hook is capability error |
| `control.exit/stop/cancel/checkpoint` | Declared target task/controller and admission/drain/fault policy, token; state blueprint defines action outcome and issued obligation handling |
| `requirement.guard` | Closed predicate, activation guard, disposition/evidence refs, failure kind and token; executes only at declared active point, never hoisted as total-pure |
| `region.yield/return/task_complete` | Exact typed result tuple followed by domain token when region signature has one; no successor instructions in block |

`state.action` admits exactly registered variants of FIFO/LIFO/vector batch/peek/status, queue-register, priority/rotation/RR arbitration, merge begin/push/receive/close, lock acquire/release, line-buffer fill/publication/lease operations, RegFile reset/shift, and other state transitions named in the protocol blueprint. FIFOReg is a capacity-one queue-register, initialized/reset empty: `.value` consumes, assignment produces; payload reset image is not an available token, and an explicitly declared seed is separate. Its detailed divergence/transition is in the state blueprint. The family is parametric data, not an escape hatch. Its descriptor specifies operand evaluation/action order, old-state/batch atomicity, success/fault/wait outcomes, capacity and permit/lease obligations. Vector consumes return MaskedVec in original active-lane positions. A reference backend can diagnose a missing implementation for an otherwise typed version; target eligibility separately names the unsupported realization.

Target-plan record tags are separately `implementation.controller`, `continuation`, `storage`, `bank_port`, `lane_mask`, `channel`, `arbiter`, `numeric_realization`, `transfer_route`, `fault_route`, `abi`, and `correspondence`. They consume the checked plan schema from the state/HLS blueprint. Generic physical lowering tags are never accepted as source semantic operations or used to erase source capacity/lifetime.

## Regions, explicit captures and token verification

Semantic regions are single-block structured regions. A definition body, branch, loop, FSM stage or task body has an immutable `RegionSignature(kind,arg_types,result_types,task_domain,allowed_effect_bound)`. Every externally needed value/handle is passed through parent operation operands and matching block arguments. The Spatial record verifier enforces isolation for definitions and structured owners: every nonlocal reference must match an explicit parent operand/block argument capture, and no implicit ancestor value reference survives closure conversion. An optional xDSL adapter may additionally use IsolatedFromAbove, but that framework trait is not the canonical check. Definitions reference other definitions by admitted symbol/DefinitionRef, not a runtime SSA handle.

The token slots described below are present when the derived region/op summary requires ordered effects, faults or control/resource lifecycle. A structurally total-pure helper/if/map/call may have a tokenless signature, verified only when every nested operation/callee is total-pure. The verifier checks that condition independently; an author cannot omit a token from a state/fault operation by claiming purity. Task/group/FSM/forever lifecycle remains tokenful. This permits a pure arithmetic conditional helper without inventing a state effect.

Ordinary total-pure values may have many uses. OrderToken is linear **within its structured domain**, with parent transfer rules rather than global use-count folklore:

- An ordered block starts with exactly one token argument and keeps `current`. Every stateful/may-fault op consumes exactly current and defines the next token. Its non-token results are immutable values. The terminator yields exactly current. A dangling, reused or different-domain token rejects.
- `control.if` consumes current once. Each arm receives its own conditional region token argument. Both static arms validate, but runtime selects one; its yielded token becomes the parent's single result token. Passing the parent token directly into both bodies or executing both yields is invalid.
- A loop consumes parent current once and gives its body an iteration token argument plus Index/carries. Its yield advances the next activation; this is structured operational recurrence, not a static cyclic SSA edge. On zero iterations, parent output represents input continuation. Loop-local resources get an iteration activation generation.
- A helper/component call consumes current at the call if effectful; the callee starts a mapped call-domain token and completion returns the next caller token. A total-pure call has no token. Caller continuation cannot bypass an effectful call.
- A task group consumes one parent current and owns N child-region token domains. Child `task_complete` yields each completion internally. The group produces a new parent token only after its adopted join condition. Runtime retains a parent join barrier; it does **not consume the pre-fork SSA token a second time**. Machine lowering can split spawn/join with a typed JoinHandle.
- FSM Test/Next may read/observe under the permitted state-blueprint bound but cannot mutate/consume/suspend. Action owns resumable effects. Faulting reads still thread their phase token. Next begins only after Action completion.

The immutable semantic records have no pending request state or live PC. The simulator derives its ExecutionProgram from those records and allocates invocation-owned Frames/continuations as the state blueprint describes. Blocking state/environment/foreign calls capture operands once at their ordered token point, then suspend; resume binds the outcome and continues. Reentering source expression evaluation on resume is invalid.

Canonical Spatial record verifier pseudocode (also required around any optional adapter):

```text
verify_region(region,signature):
  require exactly one block; arg count/types == signature
  seen = set(block_args); current = designated token argument
  for op in block_order:
    validate registry ID/version, arity, payload ownership, result types
    for operand in op.operands: require operand in seen  # no ancestor implicit capture
    reject token operand outside the declared token slot
    if op has token: require op.token_in == current; current = op.token_out
    verify borrowed handle/permit/lease ownership and allowed effect bound
    recursively verify owned regions against op-specific signatures
    check every nested capture matches a parent operand/block arg by type/identity map
    seen += op.results
  require exactly one final legal terminator; no operation after it
  require terminator value tuple == signature.result_types
  require terminator token == current with matching task domain
```

Single-block isolation deliberately avoids needing a full CFG dominance solver for this semantic layer. A future multi-block plan/adapter representation needs a separately specified dominator tree plus same-block ordinal checks and reachability; adding one is not permission to weaken the current structured semantic checks. Imported graphs always rerun the complete Spatial verifier and then profile-specific requirements; a semantic hash or generic text roundtrip does not grant checkedness.

## Requirement algebra, checker profiles and conservative analyses

Requirements use closed records:

```text
Requirement(id,kind,predicate,activation_guard,subject_refs,origin_id,
            assumptions,disposition,evidence_ref,guard_op_ref,dependencies)
Predicate = true | false | all(P*) | any(P*) | not(P)
          | compare(IndexExpr,relation,IndexExpr)
          | initialized(HandleRef,AccessRegion)
          | shape_equal(Shape,Shape) | disjoint(AccessRegion,AccessRegion)
          | capacity(ResourceRef,transition,captured_count)
          | capability(HandleRef,role) | nonempty(Domain)
          | lifetime_covers(owner,consumer) | ownership(task,resource,permit)
          | profile_supports(profile,closed_operation_or_transition)
```

`IndexExpr` uses typed pure structural arithmetic/registered projections with preserved normalization boundaries. `AccessRegion` is Point, Rectangle with signed strides, AffineImage(domain,coordinate_map), guarded finite union, or UnknownRegion. Coordinate composition preserves each logical axis before physical flattening; integral half-open bounds and retained/dropped axes are explicit. Nonaffine expressions can still be evaluated by active reference guards even when static analysis returns Unknown.

Reference checking profiles:

| Profile | Check success rule |
|---|---|
| `reference.guarded.v1` | Every requirement is proved, validated preparation/call precondition, or lowered to an implemented active runtime guard. Unsupported guard predicate or unresolved Unknown rejects check |
| `reference.static.v1` | Every requirement proved or validated invocation precondition; no dynamic safety guard accepted |
| `target.PROFILE` | Starts from a checked reference revision, then every semantic guard/operation/protocol has proved impossibility, validated precondition or legal target implementation. Unknown target mapping rejects eligible emission |

Invalid known syntax/type/capability/lifetime or statically certain active failure receives rejection rather than a guard that pretends it is valid. A false predicate under a proved-unreachable activation is discharge by an explicit reachability proof. A potential dynamic failure can remain a guard and lead to a source-located runtime fault. An unsupported analysis diagnostic is separate from proof of an invalid program.

Minimum pure-Python analyses are sound and conservative:

1. Numeric types/ranges use exact constants and intervals with wrapping operations producing conservative full-domain intervals unless a tighter proof is sound. Affine Index forms are coefficient maps plus constant; comparisons prove by constant evaluation, interval implication and normalized affine cancellation. Nonaffine/over-budget returns Unknown. A native solver may propose a certificate, but only the Python verifier can discharge it.
2. Alias identity indexes accesses by declared backing/generation, then composes views. Known disjoint rectangles/constant points prove disjointness. Conditional handles retain guarded alternatives. Unknown overlap preserves order or requires adopted ownership/arbitration; it never licenses concurrency.
3. Initialization state per backing is a canonical union of definitely written Point/Rectangle/AffineImage regions. Ordered writes/transfer completion add regions; resets install their declared image. Read inclusion checks exact cells/normalized affine region containment. Branch joins intersect definitely initialized sets across all feasible arms. Unknown intersection loses the fact, never adds initialization. Runtime simulation maintains cell/region initialization bits shared by aliases and guards reads.
4. A possibly zero-trip loop intersects the entry path with iterative exit guarantees. Recognize a fully covering affine fill only by a checked domain-to-coordinate certificate; helpers/aliases share that reusable rule. Other loops use a finite monotone worklist with explicit invariant/summary assumptions and widening that loses facts. No FIFOBranch/tiled-scale recognizer is permitted.
5. Summary preconditions/postregions and effects substitute formal backing/coordinate maps at call. Guaranteed writes from all successful exits contribute caller initialization; conditional/unknown writes contribute only under proved matching guard. Distinct formal names are not disjointness evidence.
6. Queue occupancy/status, permit/lease, task protocols and stop/admission obligations use the state blueprint's transition summaries. A bounded exact abstract queue/stack list is retained when allocation/fills/consumes have known literal payloads and control is statically determined; dequeue updates that list and propagates the exact returned value. Branch joins or unknown payloads widen to conservative occupancy/value facts. This reusable constant-state rule statically rejects R004's `[0,5]` RHS-first assignment target5 into extent2 without recognizing the fixture. If relational proof is unavailable for dynamic data, reference active transition checks may accept under guarded profile; exact trace evidence does not become a universal proof.

Runtime predicates cannot repeat effectful operands: guards reference captured address/value/state version at the token point. Guard evaluation of initialization/capacity occurs as an observation in the operation's order domain. Bounds checks happen before flattening; uninitialized check after legal address capture; mutation occurs only after those checks. A source-size/resource budget outcome is separate from language failure and records exact implementation limits.

## Pass manager and requirement transfer

`CheckedProgram` queries the immutable canonical records through the private checked wrapper above. Source/provenance and requirement information remain owned alongside that revision; indices, inferred facts and execution caches are private side tables keyed by its complete dependencies. Optional xDSL graphs are derived adapter state, never the checked program's hidden mutable owner.

Each pass declares `input_schema/profile`, registered allowed operation set, prerequisites, its concrete rewrite rules and semantic side conditions, preserved properties, invalidated analyses and postchecks. A pass transaction is:

1. Read an accepted revision and its matching index; allocate a private candidate editor and a requirement/provenance transfer ledger. The pass cannot mutate the input records.
2. Apply only its registered rewrites, recording result/binder/capture substitutions, fresh IDs, created/deleted origins, and the preservation evidence required by each rule. Full rebuild is the initial correct implementation; structural sharing is optional.
3. Close the edit workspace into owned candidate records, rebuild the candidate index, and run the **full** Spatial verifier and profile checks. Validate all requirement transfers, origin lineage and declared semantic-preservation side conditions. Well-typed output alone does not prove that an arbitrary rewrite preserves program meaning.
4. On success, construct the checked revision wrapper, publish it atomically to the caller/cache, and invalidate dependent analyses/callers/execution caches. A no-change pass may explicitly return the input revision. On failure, publish nothing; retain the old checked revision and return an internal defect/failed optimization result, never a fabricated source error.

Requirement correspondence is explicit:

```text
old_requirement_id -> retained(new_id,same_predicate_under_substitution)
                   | replaced(new_ids,checked_implication_certificate)
                   | discharged(checked_proof_of_predicate_or_unreachable_guard)
```

Deleting an operation does not merely delete its requirements. A total-pure DCE may remove no observable requirement; removing a statically untaken branch requires a reachability certificate for its guarded obligations. Replacing a guarded division by a constant requires an equivalence/totality proof retaining faults where applicable. Inlining substitutes origins/activation/formal resources and transfers requirement IDs; repeated call allocations remain distinct activations. Every surviving/new node must have valid source/generated origins. Deleted nodes retain lineage with the responsible rewrite and its correspondence/proof, so a discarded instruction cannot silently discard a diagnostic or guard. Requirement and origin ledger completeness are publication checks, not optional pretty-printing metadata.

Analysis cache entry is `(analysis_id,revision_digest,input_op_or_region_ids,descriptor/profile_digests,assumptions,options,result)` with exact declared dependency closure. A pass invalidates affected entries/callers; an entry is never reused only because it says "proved". Semantic fields such as admission window, fixed tree, logical capacity and numeric modes remain in the graph. Analysis-specific inferred ranges/ports/latencies stay in side tables.

Initial record CSE/DCE uses only approved total-pure registered nodes and checked numerical/effect side conditions, preserving unknown/effectful containers. No state.action, faulting read, runtime guard, RNG, observed status, foreign model or protocol operation acquires purity from its class name or an unused result. Totality certificates and their exact revision dependencies are revalidated or invalidated with the rewrite.

An optional xDSL backend adapter must name its actual dialect/pass/tool pipeline and demonstrate end-to-end benefit including conversion, verification, correspondence, provenance, indices, retained snapshots and dependencies. Conversion starts from an accepted semantic/plan revision and preserves a complete source/requirement map. If framework passes alter physical plan decisions, their output must return through candidate PlanRecords and the full plan/correspondence publication gate; unsupported records/changes diagnose rather than becoming an opaque alternate plan. Generic CSE/DCE, if selected, is restricted to approved total-pure representations with Spatial preservation rules; framework effect traits do not establish those rules. The adapter's private mutable graph is discarded on failure and never exported as a canonical checked flag. No particular beneficial xDSL pipeline has been demonstrated by the current comparison.

## Full family crosswalk and readiness acceptance

| R005 gate | Represented by this schema; additional owner |
|---|---|
| G01 capture/helpers | Surface, closed meta/symbols, definitions/calls/closures, unchecked ledger, origins; source manager/package blueprint |
| G02 numerics | numeric.eval, value.constant, Bits/Num/Order descriptor registry; numeric blueprint exact algorithms/profiles |
| G03 vectors/records | aggregate/bits schemas, typed callback DefinitionRefs, stable mask/lane/field layout |
| G04 storage/windows | allocation/view/read/write/reset/shift and state.action leases; state blueprint transitions |
| G05 control | if/loop/region/task_group/forever/FSM/checkpoint, typed domains and record state |
| G06 reductions | scalar/memory region signatures, mapper lease, lawful/tree/fold policy and effects; numeric blueprint |
| G07 transfers/dynamic DRAM | transfer/dynamic allocation, coordinate maps/pool ownership, captured completion; state/HLS blueprint |
| G08 queues/arbiters/merge | closed state.action variants/modes and task token; state blueprint full transition table |
| G09 streams/frames/buses | endpoints/environment/foreign, declared field versus record framing, termination/close outcomes |
| G10 locks | Permit type + lock acquire/release transition, deduplicated keys, owner domains and protected writes |
| G11 components/blackboxes | component signature projection/call, closed manifest/model registry, task Actor model |
| G12 host arrays/tensors/files | launch interface/dynamic shape requirements, acquired dependencies; package/buffer/session blueprint |
| G13 libraries/meta | declarative spatial.lib.* templates, typed DefinitionRef callbacks, exact specialize/check path; library recipe blueprint |
| G14 debug/effects/reference | diagnostic/fault/exit ops, semantic token/effect tree, origins; simulator/package blueprints |
| G15 passes | private snapshots, requirement correspondence, pass wrappers and dependency-keyed analyses |
| G16 dependence/storage plans | AccessRegion/alias predicates and implementation dialect + correspondence; state/HLS blueprint |
| G17 Params/DSE/models | closed meta choices/constraints, target-independent variants, parameter digest/analysis schema; plan/report blueprint |
| G18 backend/infrastructure | target.PROFILE requirement gate and implementation schema; explicit adapter/replacement/exclusion from coverage ledger |

The existing 106-document/124-path coverage ledger must add a registered family/template/host-adapter/exclusion reference for each row before implementation claims. The table above defines reusable representation routes, not proof that every operation in each route is implemented. A full-language readiness audit checks that every concrete opcode/transition/template referenced by those rows has a closed signature/rule in its owning blueprint, even when production support arrives later.

Minimum independent fixtures before adopting this blueprint:

- Host poison decorators/defaults/annotations/meta conversion hooks are never invoked; unsupported syntax behind a false static choice still rejects. Imported dependency/version mismatch rejects.
- Canonical record construction rejects mutable/callback payloads, duplicate owned nodes and invalid ValueRefs; a frozen wrapper is never checkedness. Failed pass publication leaves old records, query indices and provenance usable; changed revisions invalidate use/analysis/execution caches.
- Rewriter fixtures cover deletion with live uses, nested capture remapping, fresh allocation identities, requirement/origin loss and an invalid imported checked flag. Source, builder and artifact import converge on the same verified record program; a derived ExecutionProgram or xDSL graph cannot override its semantics.
- Storage-capability fixtures retain exact Index across 32-bit boundaries, preserve masked guards through local cell writes/reads, reject Index/MaskedVec in packed byte/queue slots, and refuse finite target plans based only on initial zero rather than an invariant. Bare and explicit-zero Reg[Int] allocations have identical semantic reset data with distinct provenance.
- Whole-signature prebinding accepts a later immutable In[Index] shape formal and later Meta[Type]/Size formals; rejects mutable/output/storage shape dependencies, duplicate/cyclic dependencies and body-local forward use. Source and builder share those formal identities/category checks.
- Const[Type] accepts closed canonical value descriptors and preserves alias origins; rejects arbitrary Python types/callbacks, resource/profile descriptors, invalid widths and a descriptor used without its required capability.
- Local value reassignment, undeclared write, intrinsic shadow, escaped loop binder, forward value capture and missing final return reject; terminal returning if yields exact typed results. Same kernel through source/builder yields equal semantic canonical content with different honest origins.
- Exact literal tree, Index embedding, comparison-chain shared operand and lazy Bool fault/consume cases have handwritten bits/effect traces, including untaken faults and already-sequenced values accepted by select.
- Helper fill/read through two aliased formals updates common initialization; helper-local allocation is fresh on every call/loop activation; borrowed input view return succeeds; local view/permit/lease escape rejects.
- Scalar output multiple ordered writes succeeds with last value; missing else write and zero-trip-only output initialization do not claim success. Concurrent output writers need ownership/arbitration.
- Branch double-token flow, wrong result arity/type, same-block use-before-definition, implicit ancestor capture, cross-task token, duplicate pending leaf, unmatched permit/lease and imported unknown registry tags reject.
- Loop affine fill certificate is checked independently; a nearly matching off-by-one/strided/zero-trip fill fails proof or receives active guard. Conditional alias writes do not initialize the untaken backing.
- Failed pass leaves prior revision byte-identical/usable; dropped requirement needs checked reachability/implication evidence; profile/admission/capacity changes invalidate corresponding analyses.

These fixture expectations are designed acceptance rules, not observed Spatial compiler results. The only executed new evidence below is framework mechanics.

## Historical bounded structured xDSL mechanics probe — 1 October 2026

The following unchanged evidence established framework mechanisms under the earlier xDSL-default proposal. It does not select the current canonical representation or establish a useful optional backend pipeline; [[PY-R017 - Compiler Representation Comparison]] records the 3 October comparison and revised proposal.

On 2026-10-01, executed the pinned xDSL source at `0b107461b3bfcd353d949fe00d3d1623bd6c826a` in the isolated environment already used by R006. CPython `3.14.5 (main, May 10 2026, 10:21:34) [Clang 21.0.0.123.102]`, macOS `26.6.2`, arm64. Base dependencies were `immutabledict==4.3.1`, `ordered-set==4.1.0`, `typing-extensions==4.15.0`. No optional backend/framework packages or Spatial compiler were used.

The standalone probe is `/private/tmp/spatial-readiness-structured-probe.py`, SHA-256 `ae836392c8f684033d19297c9062530a925db2371888cf68a799a0ec20ba3054`. Results are `/private/tmp/spatial-readiness-structured-probe-results.txt`. It defines a toy Token type, isolated scope operation, write-effect step and terminator; nested scope roles are helper, if, loop and task group. Role attributes deliberately are not Spatial semantics: no real controller/queue/numeric or task interpreter is implemented. The test resolves whether xDSL supports nested isolated typed region storage/cloning/text at this pin, while showing which Spatial checks it cannot supply.

```text
valid_nested_helper_if_loop_task_group accepted
clone_operands_remapped True
candidate_attribute_replacement_keeps_original True
generic_text_nested_roundtrip True
effect_steps_before_after_CSE_DCE 4 4
implicit_ancestor_capture rejected
same_block_use_before_definition accepted
duplicated_order_token accepted
yield_arity_mismatch accepted
```

Interpretation: explicit nested capture storage, cloning/remapping, immutable-attribute replacement and generic nested text roundtrip work in this bounded case. xDSL isolation checks ancestor capture; it does not supply Spatial value-order, linear-token or typed-yield rules. The Spatial-specific verifier above remains necessary on either representation route. Four explicit write effects survive generic CSE/DCE in this probe; this does not license arbitrary generic optimization of real Spatial operations. Private cloning still needs owned immutable attributes, because core cloning shallow-copies attribute/property dictionaries.

Reproduce without changing the vault or original repository:

```sh
/private/tmp/spatial-pyr006-xdsl/bin/python \
  /private/tmp/spatial-readiness-structured-probe.py \
  /Users/david/Documents/David_code/reference/xdsl
```

For a clean source-import environment, create a venv with CPython 3.14.5, install the three exact base dependency versions above, check out the exact xDSL pin and run the standalone input with that source directory. The independent clean installed-package check is now recorded in [[40 - Package and Conformance Blueprint]]; it reran this probe with matching results against the curated installed wheel. This source-import probe itself is not a wheel-build/reproducibility benchmark. [[07 - Python Implementation Readiness Audit]] preserves the evidence archive and exact reproduction inputs, so temporary files are not the sole record.

Pinned source cross-checks: xDSL `xdsl/traits.py:266-301` verifies IsolatedFromAbove; `xdsl/irdl/dominance.py:4-97` is block dominance rather than operation/value ordering; `xdsl/ir/core.py:1246-1323` shows clone mapping and shallow attribute/property dictionaries. Exo `src/exo/frontend/pyparser.py:1063-1084,1160-1189` and `frontend/typecheck.py:17-26` provide precedent for explicit source binding and separate type/bounds/race stages. They are implementation evidence, not semantic authority for this proposed language. Original Spatial's explicit contribution/combine/FSM regions and view aliases remain grounded at the pins cited in R006.


## Baseline example migration and cross-review record

Reviewed all Python blocks in R001/R004 and the E001 corpus at baseline b56a496. E001 contains no Python implementation listing; its independently derived outputs remain unchanged. The source snippets use the fixed core prelude described above. Historical comparisons/probes retain their dated status and do not become accepted compiler examples merely because Python can parse them.

| Baseline example/reference | Classification under this blueprint | Exact repair or preserved rejection |
|---|---|---|
| R001 E1 source:47–59; builder:65–78 | Accepted form after ordinary manifest/prelude acquisition | No algorithm change; Index `base+16` view arithmetic and pure indexed writes follow registered structural slots |
| R001 E2 source:93–105 | Migration required | `values[0,i] = embed(Int,i)`; `def contribution(i:Index)->Int`. Identity0 is contextual Int; `combine="add"` resolves the admitted wrapping Int addition ID/law rather than arbitrary string lookup |
| R001 E2 builder:111–123 | Migration required | `values.at(0,i).write(k.embed(Int,i))`; reduction.index remains Index. All other construction is the same shared unchecked request |
| R001 E3 source:141–163 | Index embedding/binder migration required; explicit reset optional | Bare `accumulator:Reg[Int]` uses registered zero; `= reg(reset=0)` is an equivalent explicit choice, not a required repair. Both `fifo.enq(embed(Int,i))` and `contribution(i:Index)` remain required migrations. Optional header `requires(0<=count1<=128)`/same count2 and `requires(count1+count2>0)` make intended count/nonempty invocation contract explicit |
| R001 E3 builder:169–192 | Migration required | Both fills use `fifo.enq(k.embed(Int,i))`. `k.reg(Int,reset=0)` already matches explicit reset constructor. Add corresponding bound/nonempty request/precondition records if static/invocation-only checking is requested |
| R004 tiled helper source:129–145; builder:147–169 | Accepted form | scaled helper is total-pure Int wrapping multiplication; whole-signature prebinding allows later N/TILE, with category-checked annotation dependencies. Bounds/initialization are checked, not implied by spelling |
| R004 component fragment:175 | Needs explicit interface projection | Construct `scale_component = as_component(scale_template,interface=...)` in the host with src Read[Dram], gain value:Int, dst Write[Dram], N/TILE meta; tmp caller allocation required. The two call_component requests then bind the same borrowed handles and preserve first-call init before second-call reads |
| R004 generated host family:183–190 | Ordinary host work | Host Capture/specialize/FrozenMeta/factory names map to the package API; host loop/string formatting is not captured grammar |
| R004 literal source/builder:206–216 | Accepted form | FixPt alias canonicalizes to Fix; token trees remain exact and contextual. Decimal builder uses literal strings, not bare host floats |
| R004 U uninitialized:247–259 | Intentional rejection | E-INIT-READ at m[0], allocation related; declaration is not initialized |
| R004 T incompatible:273–285 | Intentional rejection | E-TYPE-OPERANDS; no implicit Int/Fixed cast |
| R004 C while:299–312 | Intentional rejection | Source E-CONTROL-UNSUPPORTED; builder E-STAGE-TRUTH when symbolic Bool enters host while |
| R004 B guarded:328–350 | Accepted form | One selected dequeue only; false path leaves [7]. Ordinary statement condition does not execute during capture |
| R004 eager pure select:361–378 | Intentional rejection | E-BRANCH-EFFECT for direct pending consume; previously sequenced v then select is accepted |
| R004 S escaped:396–412 | Intentional rejection | E-SCOPE-ESCAPE with branch-local declaration; no function-wide Python binding |
| R004 O assignment:432–454 | Intentional rejection for extent2 | Exact constant queue abstract state derives target5 after RHS consume. Extent6 succeeds with dst[5]=0; augmented form succeeds with dst[0]=15 and one target capture |
| R004 CPython AST probe:494–512 | Evidence-only host probe | Runs ordinary Python parsing code outside Spatial. Its captured @explode/annotation calls are unsupported source markers; no claim of accepted Spatial source or numeric conformance |

Cross-review on 2026-10-01:

- Numeric owner independently confirmed contextual typing, explicit Index embedding and immutable locals. Their review corrected Bool-result comparisons so `check(1<2,Bool)` synthesizes numeric operands rather than propagating Bool into them. The registered ScaleRatio aggregate is shared with library recipes; no runtime Fraction type was added.
- State/HLS owner independently confirmed single-block region/call/resume semantics and the parent-token-once task group. Their review added FIFOReg cap-one empty reset/seed distinction and ContributionLease transfer. Reading their blueprint exposed the missing MaskedVec validity type and runtime Index storage; both owners adopted guarded lane extraction, explicit default materialization and exact Index reference values. No `.values` bypass is permitted.
- Package owner reviewed artifact/interface fields and independently reran the same structured probe against the installed curated xDSL wheel in a fresh runtime-only environment. Results matched the source-import run. The unchecked artifact kind and Bits(0)/zero-span identity were added to package schemas. Source prelude/registry identity is a dependency, never an ambient host module.
- Framework mechanics evidence resolves a bounded representation uncertainty only. Dynamic proof precision, performance targets, vendor capability evidence and full compiler conformance remain implementation/validation work after approval; no framework claim is inflated into those results.

## Complete standalone structured probe source

This is the exact standalone input whose digest and result are recorded above. It is included so a temporary filesystem path is not the only way to reproduce the evidence. It does not implement any production Spatial language rule.

```python
"""Bounded xDSL mechanics probe; NOT a Spatial compiler or semantic dialect.
Usage: PINNED_VENV/bin/python spatial-readiness-structured-probe.py XDSL_REPO
"""
import io, sys, platform, hashlib
sys.path.insert(0, sys.argv[1])
from xdsl.ir import Dialect, Block, Region, Attribute, ParametrizedAttribute, TypeAttribute
from xdsl.irdl import (IRDLOperation, irdl_op_definition, irdl_attr_definition,
    var_operand_def, var_result_def, var_region_def, traits_def, attr_def)
from xdsl.dialects.builtin import ModuleOp, Builtin, StringAttr, i32
from xdsl.traits import IsolatedFromAbove, IsTerminator, MemoryWriteEffect
from xdsl.context import Context
from xdsl.parser import Parser
from xdsl.printer import Printer
from xdsl.transforms.common_subexpression_elimination import CommonSubexpressionElimination
from xdsl.transforms.dead_code_elimination import DeadCodeElimination
from xdsl.utils.exceptions import VerifyException

@irdl_attr_definition
class Token(ParametrizedAttribute, TypeAttribute):
    name = 'probe.token'

@irdl_op_definition
class Scope(IRDLOperation):
    name = 'probe.scope'
    ins = var_operand_def(Attribute)
    outs = var_result_def(Attribute)
    bodies = var_region_def('single_block')
    kind = attr_def(StringAttr)
    traits = traits_def(IsolatedFromAbove())

@irdl_op_definition
class Step(IRDLOperation):
    name = 'probe.step'
    ins = var_operand_def(Attribute)
    outs = var_result_def(Attribute)
    traits = traits_def(MemoryWriteEffect())

@irdl_op_definition
class Yield(IRDLOperation):
    name = 'probe.yield'
    values = var_operand_def(Attribute)
    traits = traits_def(IsTerminator())

T = Token()
def step(t, v):
    return Step(operands=[[t,v]], result_types=[[T,i32]])
def end(*vals):
    return Yield(operands=[list(vals)])
def scope(kind, operands, body_blocks, types=(T,i32)):
    return Scope(operands=[list(operands)], result_types=[list(types)],
        regions=[[Region(b) for b in body_blocks]], attributes={'kind':StringAttr(kind)})
def leaf_body():
    b=Block(arg_types=[T,i32]); s=step(*b.args); b.add_ops([s,end(*s.results)]); return b

def make_valid():
    helper=scope('helper_definition', [], [leaf_body()], types=())
    b=Block(arg_types=[T,i32])
    choice=scope('if', b.args, [leaf_body(),leaf_body()])
    b.add_ops([choice,end(*choice.results)])
    loop_body=b
    child=Block(arg_types=[T,i32]); loop=scope('loop',child.args,[loop_body])
    child.add_ops([loop,end(*loop.results)])
    parent=Block(arg_types=[T,i32]); group=scope('task_group',parent.args,[child,leaf_body()])
    parent.add_ops([group,end(*group.results)])
    entry=scope('entry',[],[parent],types=())
    return ModuleOp([helper,entry])

def verify_result(m):
    try: m.verify(); return 'accepted'
    except VerifyException: return 'rejected'
def dump(m):
    buf=io.StringIO(); Printer(stream=buf,print_generic_format=True).print_op(m); return buf.getvalue()

m=make_valid(); m.verify(); clone=m.clone(); clone.verify()
original_ops=list(m.walk()); cloned_ops=list(clone.walk())
original_values={r for o in original_ops for r in o.results}
original_values.update(a for o in original_ops for reg in o.regions for b in reg.blocks for a in b.args)
no_original_refs=all(v not in original_values for o in cloned_ops for v in o.operands)
cloned_scopes=[o for o in clone.walk() if isinstance(o,Scope)]
cloned_scopes[0].attributes['kind']=StringAttr('changed_candidate')
old_unchanged=next(o for o in m.walk() if isinstance(o,Scope)).kind.data=='helper_definition'
ctx=Context(); ctx.load_dialect(Builtin); ctx.load_dialect(Dialect('probe',[Scope,Step,Yield],[Token]))
roundtrip=Parser(ctx,dump(m)).parse_module(); roundtrip.verify()
copy=m.clone(); before=sum(isinstance(o,Step) for o in copy.walk())
CommonSubexpressionElimination().apply(ctx,copy); DeadCodeElimination().apply(ctx,copy); copy.verify()
after=sum(isinstance(o,Step) for o in copy.walk())

# Invalid implicit ancestor capture: an isolated child body reaches parent args.
outer=Block(arg_types=[T,i32]); bad_inner=Block(arg_types=[T,i32]); s=step(*outer.args)
bad_inner.add_ops([s,end(*s.results)]); inner=scope('if',outer.args,[bad_inner,leaf_body()])
outer.add_ops([inner,end(*inner.results)]); bad_capture=ModuleOp([scope('entry',[],[outer],types=())])
# Invalid same-block value order: Step consumes results defined by a later Step.
b=Block(arg_types=[T,i32]); later=step(*b.args); early=step(*later.results)
b.add_ops([early,later,end(*early.results)]); bad_order=ModuleOp([scope('entry',[],[b],types=())])
# Invalid token fork: two ordinary effect steps consume same entry token.
b=Block(arg_types=[T,i32]); a=step(*b.args); c=step(*b.args)
b.add_ops([a,c,end(*c.results)]); bad_token=ModuleOp([scope('entry',[],[b],types=())])
# Invalid region results: no custom verifier ties declared results to yields.
b=Block(arg_types=[T,i32]); b.add_op(end(b.args[1])); bad_yield=ModuleOp([scope('entry',[],[b],types=())])
print('python',sys.version.splitlines()[0]); print('platform',platform.platform())
print('probe_sha256',hashlib.sha256(open(__file__,'rb').read()).hexdigest())
print('valid_nested_helper_if_loop_task_group',verify_result(m))
print('clone_operands_remapped',no_original_refs)
print('candidate_attribute_replacement_keeps_original',old_unchanged)
print('generic_text_nested_roundtrip',dump(roundtrip)==dump(m))
print('effect_steps_before_after_CSE_DCE',before,after)
print('implicit_ancestor_capture',verify_result(bad_capture))
print('same_block_use_before_definition',verify_result(bad_order))
print('duplicated_order_token',verify_result(bad_token))
print('yield_arity_mismatch',verify_result(bad_yield))

```
