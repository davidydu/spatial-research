---
type: deep-dive
title: "PY-R006 — Compiler architecture and framework choice"
topic: python-compiler-architecture
project: spatial-python
session: 2026-09-30
status: research-conclusion
source_files:
  - "spatial@e7a8f2f:src/spatial/Spatial.scala:71-145"
  - "spatial@e7a8f2f:src/spatial/Spatial.scala:168-230"
  - "spatial@e7a8f2f:src/spatial/node/Control.scala:33-143"
  - "spatial@e7a8f2f:src/spatial/node/HierarchyMemory.scala:28-98"
  - "spatial@e7a8f2f:argon/src/argon/Effects.scala:5-50"
  - "spatial@e7a8f2f:argon/src/argon/Data.scala:36-79"
  - "spatial@e7a8f2f:argon/src/argon/transform/Transformer.scala:94-108"
  - "xdsl@0b10746:pyproject.toml:1-43"
  - "xdsl@0b10746:xdsl/ir/core.py:538-628"
  - "xdsl@0b10746:xdsl/ir/core.py:850-909"
  - "xdsl@0b10746:xdsl/ir/core.py:1178-1235"
  - "xdsl@0b10746:xdsl/irdl/operations.py:1164-1212"
  - "xdsl@0b10746:xdsl/traits.py:551-705"
  - "xdsl@0b10746:xdsl/traits.py:755-803"
  - "xdsl@0b10746:xdsl/passes.py:27-70"
  - "xdsl@0b10746:xdsl/passes.py:142-177"
  - "xdsl@0b10746:xdsl/pattern_rewriter.py:225-275"
  - "xdsl@0b10746:xdsl/interpreter.py:637-695"
  - "https://docs.xdsl.dev/reference/traits/ (accessed 2026-09-30)"
  - "https://mlir.llvm.org/docs/Bindings/Python/ (accessed 2026-09-30)"
feeds_spec:
  - "[[40 - Python Compiler and HLS Contract]]"
---

## Recommendation and authority

Recommend **transitively immutable Python records for source/unchecked data, the canonical checked semantic program, and the initial checked implementation plan**. Source capture and the builder normalize to the same unchecked model; checking publishes one semantic program consumed by reference simulation and hardware planning. Python owns numeric evaluation, effects, aliases, lifetimes, protocols, transformations and target eligibility. xDSL is an optional derived lowering/interop representation, not a required semantic store; native MLIR remains an optional backend adapter.

This revised default follows the bounded paired experiment and ownership analysis in [[PY-R017 - Compiler Representation Comparison]]. The selected isolated structured-region grammar already requires Spatial-owned semantic verification, canonical artifacts and provenance. Immutable records directly express the published-revision contract and permit sharing unchanged structure; mandatory xDSL graphs add mutable ownership and clone/publication boundaries without replacing those obligations. The measured records are faster and smaller on the tested workloads, but the experiment does not prove end-to-end compiler superiority or complete R007 acceptance. Adequate coding and maintenance capability are assumed.

The strongest objection is the custom route's still-unmeasured production use indices, complex graph editing and implementation-plan transforms. Preserve the pinned xDSL evidence and admit a derived adapter when a named reused pipeline demonstrates a whole-workflow benefit with equivalent correctness and provenance. Reopen the core choice if actual representation requirements conflict with records, or attributed record/index/transaction costs miss an existing R007 target that a comparable xDSL implementation meets. R017 specifies the early gate; it introduces no arbitrary winning ratio.
This addresses R05/R06 in [[03 - Managed Research Execution]], **proposed for professor review**, not adopted or implemented. It depends on [[PY-R001 - Programming Model Study]], [[PY-R002 - Numeric and Reduction Semantics]], [[PY-R003 - Control Memory and Effects]], and [[PY-R004 - Capture Composition and Diagnostics]]. [[PY-R007 - Host Workflow Reproducibility and Validation]] supplies workflow and performance targets. Full coverage and protocol studies populate the architecture; representation alone does not establish feature support.

## Evidence and framework decision

The xDSL source readings and original probes below remain evidence for the optional framework route. The 3 October comparison in [[PY-R017 - Compiler Representation Comparison]] supersedes the earlier recommendation to make xDSL the canonical checked representation; it does not erase those executed observations.

Original source was inspected through `git show` at `e7a8f2f7f776dd0c5ac7fc03f16b3ed4d97021f0`. The official [xDSL repository](https://github.com/xdslproject/xdsl) was cloned under `reference/xdsl` and inspected at `0b107461b3bfcd353d949fe00d3d1623bd6c826a`; citations abbreviate pins. The manager owns manifest updates. The [traits documentation](https://docs.xdsl.dev/reference/traits/) was retrieved on 2026-09-30; decisive claims were checked against pinned code.

Source facts, proposals, observed probes, and designed acceptance expectations are separate. No original application, production compiler, native MLIR installation, HLS/RTL, or board run occurred. Rust history supplies no unnamed semantic policies.

Original source separates contribution/load/combine/store regions, identity/fold fields, memory-reduction domains, and generic FSM condition/action/next-state regions: `spatial@e7a8f2f:src/spatial/node/Control.scala:33-117`. Its pipeline separates analyses and transformations around banking, unrolling, buffering, and retiming: `spatial@e7a8f2f:src/spatial/Spatial.scala:71-145`, `spatial@e7a8f2f:src/spatial/Spatial.scala:168-230`. These motivate explicit representations and invariants; copying the old pass order is not proposed.

| Option | Advantage | Ownership/cost and decision |
|---|---|---|
| Custom immutable Python IR throughout | One immutable revision/ownership discipline, explicit structured graph order, compact storage, and canonical schema correspondence | **Default for semantic and initial implementation programs**. Supply and test required indices/editors/inspection; do not infer future complex-pass performance from R017 |
| Spatial dialects on xDSL | Python IRDL, regions/SSA, attributes/traits, rewrite/pass infrastructure, parser/printer, interpreter hooks | **Optional derived lowering/interop route** after a named reuse and correspondence gate. Spatial still owns legality, rich effects, laws, snapshots and cache identity |
| Native MLIR Python bindings | Native IR/optimization ecosystem, including current Python-defined dialects/passes/patterns | Python could still own Spatial semantics while native code stores the IR. We prefer inspectable Python infrastructure here; native MLIR remains an optional backend integration |

xDSL source establishes typed SSA and operation regions/properties/locations, plus IRDL constraints and custom verification: `xdsl@0b10746:xdsl/ir/core.py:538-618`, `xdsl@0b10746:xdsl/ir/core.py:850-909`, `xdsl@0b10746:xdsl/irdl/operations.py:1164-1212`, `xdsl@0b10746:xdsl/irdl/operations.py:2207-2237`. Rewriting maintains uses, not semantic equivalence: `xdsl@0b10746:xdsl/pattern_rewriter.py:225-275`.

At the pin, base dependencies are `immutabledict<4.3.2`, `ordered-set==4.1`, and `typing-extensions>=4.13,<5`; Python `>=3.10` is declared. `cffi`/`llvmlite` belong to optional `llvm`; GUI/HEIR/dev/benchmark groups are separate: `xdsl@0b10746:pyproject.toml:1-69`. The isolated probe below actually imported the tested IRDL/parser/printer/CSE/DCE paths with only three base dependencies. It does not establish all optional dialects or packaging tools. Pin the adopted revision/reviewed release and wheel hashes; do not follow rolling main.

Native MLIR documentation describes native-extension/C-API layering **and** Python-defined dialects, pass callables, and patterns. Claiming custom MLIR logic must always be C++ would be wrong. Native storage alone also does not make Python-defined Spatial rules native. [MLIR Python bindings](https://mlir.llvm.org/docs/Bindings/Python/#loader), [Python extensions](https://mlir.llvm.org/docs/Bindings/Python/#extending-mlir-in-python) (accessed 2026-09-30). Keeping the core IR infrastructure in Python is this proposal's design preference, not an additional restriction attributed to the professor. Reconsider it if measured native interoperability or performance benefits outweigh packaging and inspection costs while Spatial semantic ownership stays in Python. The current custom-record default and optional xDSL-adapter gate follow R017, including representative region/task/provenance cases and the unchanged R007 targets. Optional backend interoperability need not reverse the decision; xDSL itself pins supported MLIR interoperability: `xdsl@0b10746:README.md:61-63`.

## Representations and module boundaries

| Representation | Required contents and meaning |
|---|---|
| Source/template | Immutable text/tokens/digests/spans/origin maps, accepted surface AST, declarations, unresolved meta expressions, explicit dependency contents; capture executes no decorators/annotations/bodies |
| Unchecked | Frozen ordered declarations/regions/literal trees, stable symbols/handles/views, meta values, pending-effect attachments, helper instances, schedule intent, complete origins; constructor success proves no legality |
| Candidate semantic IR | Typed immutable Spatial operation/region/value records, ordered effects, backing identities, obligations, task/protocol descriptors; not publicly executable |
| Checked semantic program | Private verified snapshot/revision, semantic/profile/schema IDs, requirements/guards/proofs, supported reference capabilities, origins; no backend/II/resource/termination claim implied |
| Checked implementation program | Separate immutable plan schema with lanes/masks, controllers/continuations, channels/arbiters, banks/ports/versions, numeric realizations, and semantic correspondence; optional derived framework representation |

The source reader/meta evaluator and builder depend on shared source/origin, descriptor, and unchecked-record modules. The checker depends on those and the closed semantic schema. Numeric/protocol rules are separate Python modules used by checking and simulation. Analyses/pass management depend on the semantic/implementation schemas; backend emitters consume the checked implementation program. Host adapters depend on declared checked interfaces, not compiler internals.

Normalize before SSA: recover decimal lexemes from tokens, bind meta formals before signature dimensions, contextualize literals, and attach pending effects exactly once. Helpers/components have typed arguments, explicit capabilities/environments, initially acyclic calls, and hygienic local identities. Summary checking need not eagerly inline everything. Nested components and host launches remain distinct.

A storage handle identifies backing object, generation/activation, capability, and owner lifetime; SSA values describe immutable values, not storage contents. Views preserve backing identity and per-axis coordinate maps/extents. Original dense/sparse views alias backing memories: `spatial@e7a8f2f:src/spatial/node/HierarchyMemory.scala:28-98`. Different port names do not establish disjointness; invocation validation checks actual aliases.

Checked wrappers expose queries/export/simulate/compile over immutable owned records. Distinct unchecked, candidate and checked types prevent constructor success from granting legality. Passes build candidates, verify them and publish new revisions; failure leaves the previous revision usable. Rebuild changed records/ancestors and share only transitively immutable unchanged payloads, or conservatively rebuild the whole unit. Requirement transfer, deleted-operation lineage and revision-dependent fact invalidation remain explicit. Simulation retains one revision with separate runtime state. Analysis and use/parent indices belong to revision-scoped side tables, never mutable fields on shared records.

An optional xDSL adapter must keep its mutable graph private and prove correspondence to its canonical record input. Clone/transform/verify/publication rules apply within that adapter. Framework cloning copies attribute/property dictionaries shallowly, so it still requires immutable owned payloads: `xdsl@0b10746:xdsl/ir/core.py:1246-1323`, `xdsl@0b10746:xdsl/passes.py:60-70`. No adapter graph becomes a second language authority.

Foreign reference models cross this boundary by **model ID**, not a callable payload. A manifest pins the model/schema version, Python implementation digest, transitive declared dependency digests, numeric/protocol versions, and explicit state/input/environment interface. A reviewed registry resolves that ID outside serialized IR. Model state belongs to the invocation; mutable host globals, live closures, ambient randomness, and undeclared files are forbidden model dependencies. Registration is a trusted extension boundary requiring audit and independent conformance, not an automatic purity proof for arbitrary Python. Changing model code/dependencies changes semantic identity and invalidates cached results; missing or mismatched models diagnose.

Spatial supplies canonical IDs/lineage and R004 origin chains; optional xDSL locations are projections. Framework SSA hashing uses process object identity and cannot identify cached semantics: `xdsl@0b10746:xdsl/ir/core.py:620-628`.

## Semantic properties, effects, and tasks

Define `Bool`, generic `Fix(sign,I,F)`, `Flt(P,E)`, vectors/structs/storage/endpoints, and structural size/index descriptors. Structural integers are independent of accelerator wrapping formats/platform index width. Resolve Num/Bits/Order through a typed registry. Retain rounding, overflow, exceptions, conversion/ingress kind, and approved intrinsic/RNG/profile versions as semantic properties. Ordinary multiply/add stays two operations; FMA stays one. Generic xDSL arithmetic/host floats replace them only with an equivalence rule. R002's Python numeric functions serve checking/simulation; independent vectors remain necessary.

**Floating status distinction.** Ordinary FP special results follow the adopted numeric policy; diagnostic operation/status records are non-observable metadata and may change count under legal optimization. They do not make every ordinary float operation impure. Checked overflow, division-by-zero faults, and other language faults constrain DCE/speculation even if their result is unused. A future explicitly observed FP-status operation names a status resource/event and is effectful; it is separate from ordinary FP evaluation. No implicit global flag register is introduced. R011 now supplies the proposed exact status/intrinsic/RNG contract, with adoption and execution still separate.

Reduction properties distinguish contribution order/effects, pure combine/law, identity, seed, empty behavior, fixed topology, accumulator publication, and separate memory domains. Wrapping addition can permit lawful pure combining changes while contributions execute exactly once in declared order. Generic floating addition cannot become associative automatically. Ordered fold is a proposed redesign distinct from original Fold. Storage reset, identity, seed, and old state never collapse into one field.

Spatial effects include allocation, read/write/observe, consume/produce, acquire/release, RNG/environment, fault, suspend, cancel/reset, and completion/join. They name resources/generations, access regions/unknowns, guards, task/region, and ordering domain. Guarded branch summaries describe alternatives, not eager execution.

Normalize ordered stateful/faulting evaluation to explicit SSA order tokens. Branches yield selected value/token; loops/helpers carry tokens. Ordinary assignment orders RHS before target address/write; augmented assignment evaluates target once, then read/RHS/combine/write. Per-task chains coexist in concurrent groups; they are not silently chained globally. Verified independence may justify splitting order, but requested conflicting concurrency needs ownership/arbitration or a diagnostic.

xDSL effects expose Read/Write/Allocate/Free and resource/value identity; unknown is conservative. `Pure` means no memory effects **plus always speculatable**: `xdsl@0b10746:xdsl/traits.py:551-705`, `xdsl@0b10746:xdsl/traits.py:755-803`. Keep richer Spatial effects authoritative. Faulting/blocking/RNG/consuming operations expose unknown generic effects where memory traits cannot represent them; do not label them Pure or faulting reads merely read-only. Generic CSE treats reads specially and DCE can discard reads: `xdsl@0b10746:xdsl/transforms/common_subexpression_elimination.py:155-204`, `xdsl@0b10746:xdsl/transforms/dead_code_elimination.py:22-68`. On an optional xDSL route, allow generic optimization only through Spatial wrappers over approved total-pure operations; observation elimination needs resource-version/order/alias evidence.

Coordinated with PY-R008: tasks retain task/activation ID, continuation/PC, live values/local lifetimes, captured pending operands, and stop state. Resources retain generation, capacity/token order, endpoint roles/close/reset state, arbitration/fairness, and versioned transitions. Request/Grant/Commit actions carry epoch/snapshot and causal predecessors. Capture effectful send operands once and retain them across suspension; blocked requests mutate nothing. Explicit batch/barrier defines simultaneity. Untimed tasks denote allowed traces; deterministic arbitration given pending state does not make async contender arrival unique. Canonical simulation is one replayable witness, not hardware parity. Reject unsynchronized racing memory absent defined ordering/ownership.

Stop-sensitive controllers also retain semantic admission policy/window, fork or batch boundaries, and completion/refill checkpoints. The coordinated R008 default counted Sequential/Pipe `breakWhen` proposal uses window1; explicit concurrent windowW admits up toW and graceful stop drains the admitted set. Changing overlap can change committed effects. Admission/stop policy belongs in the semantic snapshot/cache key; par/II preferences are value-neutral only when they do not change that contract. This is a proposal, not measured original behavior.

## Verification and pass contracts

Spatial structural and semantic checks are mandatory. If a framework adapter is used, its additional structure checks are necessary but not sufficient. The observed probe accepted same-block use-before-definition despite `ModuleOp.verify()`. Its inspected checks concern erased operands, successors/terminators, nesting, and parents; block dominance is a separate utility: `xdsl@0b10746:xdsl/ir/core.py:1178-1235`, `xdsl@0b10746:xdsl/ir/core.py:1921-1939`, `xdsl@0b10746:xdsl/irdl/dominance.py:4-72`.

Spatial verifies numeric properties, region yields, value dominance/capture, token linearity/joins, capability escape, lifetime, aliases/access overlap, initialization/bounds, contribution policies, and task protocols. Obligations retain IDs/origins/assumptions and dispositions: proved, invocation requirement, supported runtime guard, unknown analysis, or rejected. Guarded reference validity does not establish hardware eligibility. Budgets returning unknown cannot authorize unsafe lowering; deleted nodes cannot erase unmet requirements.

| Stage/pass | Required invariant | Invalidation |
|---|---|---|
| Acquire/bind/specialize | Closed syntax, frozen meta, deterministic hygienic expansion, no host escapes | Source/meta-dependent binding/types/shapes/summaries |
| Freeze/normalize/type | Shared ordered form; effects attached once; exact contextual ingress/conversions | All graph facts initially; numeric changes invalidate range/law facts |
| Build/check semantic IR | Dominance/order/lifetime/effects/protocol and requirement ledger valid | Establish analyses for this revision |
| Summarize/simplify | Valid call summaries; lawful folding/CSE/DCE; observable effects/faults/origins preserved | Uses/liveness/dependence/init/occupancy of changed regions/callers |
| Plan/legalize target | Explicit task/storage model; approved realizations; requests separate from achievements | Target capabilities/access/protocol/schedule facts |
| Lower domains/lanes/reductions | Exact active masks; contribution order and combine law/topology preserved | Bounds/init/access/bank/latency and correspondence |
| Bank/buffer/allocate | Physical reuse preserves logical generation/lifetime/hazards/capacity | Ports/dependences/resource/schedule facts |
| Build controllers/handshakes | Continuation/readiness/arbitration/reset/cancel/drain refine semantic transitions | Protocol/liveness/refinement/latency/II feasibility |
| Emit | No unresolved semantic operations/requirements; structured code/origins/manifest | Build/emitted hashes; vendor reports stay separate |

Each pass declares stage/capabilities, prerequisites, changes, preserved properties/facts, invalidations, and checks. xDSL's pipeline does not automatically verify between passes: `xdsl@0b10746:xdsl/passes.py:27-35`, `xdsl@0b10746:xdsl/passes.py:142-177`. Scheduling/banking may iterate using new implementation revisions. Semantic properties stay in IR; inferred bounds/alias/occupancy/access/banking facts stay in versioned side tables. Reuse requires dependencies, not `proved=true`. Original metadata transfer's own memory-invalidation warning supports this separation: `spatial@e7a8f2f:argon/src/argon/transform/Transformer.scala:94-108`.

## Representative lowering and full families

Original FIFOBranch has lazy consuming contributions in explicit-register Reduce: `spatial@e7a8f2f:test/spatial/tests/feature/control/FIFOBranch.scala:16-27`. Proposed migration freezes two capacity128 backing IDs, ordered fills, no-identity/nonempty requirement, and two branch regions. Typing selects Int wrapping addition. Checked form is explanatory notation:

```text
fill Q1(count1); complete; fill Q2(count2); complete
reduce domain=[0,count1+count2), identity=none, requires_nonempty,
       contribution_order=increasing, pure_combine=wrap_add:
  contribution(k, token):
    empty, observed = observe_empty(Q1, token)
    value, next = if_region(empty, observed):
      then(t): yield consume(Q2,t)
      else(t): yield consume(Q1,t)
    yield_contribution value,next
publish result/completion; write output
```

Expected counts13/25 give378, 38 observations/selected consumes, Q1 then Q2, no untaken consume. A pure adder tree may regroup legally; arbitrary parallel mapper consumes may not. Zero total fails its requirement. Hardware branch enables/masks preserve effects/faults, completion, and contribution order. Floating combine requires ordered fold/fixed tree or a separately approved relaxed law. These are designed expectations, not executed Spatial lowering.

A communicating discriminator has two tasks sharing capacity1: producer sends11,22; consumer receives twice and ordered-folds from0. Checked tasks retain pending operands/continuations. One allowed witness sends11, blocks a second send, receives11, sends22, receives22, joins with33. Implementation uses independently advancing controllers/backpressure, not whole-producer serial replay or capacity inflation. Ordered FIFO full enqueue faults; task send suspends. Same handles/effects do not erase that protocol distinction.

| Full family | Representation → lowering obligation |
|---|---|
| Numeric/Bits/Num/Order/math/RNG | Full descriptors/policies/profiles → exact bits or approved approximation; width/resource eligibility separate |
| Vec/Shuffle/compress/gather/Struct | Lane/field/packing order/masks → checked permutation/packing realization |
| Counters/controllers/reductions/FSM/forever/enables | Domains/regions/state/order/tasks/checkpoints → lanes/controllers/completion/cancel |
| Reg/SRAM/RegFile/LineBuffer/windows/buffering | Backing/generation/init/coordinate/shift/version facts → banks/ports/reuse preserving identity |
| Dense/sparse/Series/Wildcard/DRAM/dynamic/transfers | Views/extents/address streams/ownership/alias/completion → transactions; padding is not logical bounds |
| FIFO/LIFO/vector/priority/RR/MergeBuffer/locks | Capacity/way/bound/key/arbiter/epoch/visibility → explicit queue/lock arbitration and simultaneous rules |
| Streams/StreamStruct/Frame/image/video/controller blackbox | Environment/framing/field endpoints/close/readiness/model version → validated interface protocol |
| Functional blackboxes/library templates | Typed signature/effects/profiles/call origins → checked expansion or validated primitive |
| Text/debug/assert/exit/breakpoint/testbench | Ordered observable/fault/termination/host boundary → explicit hook or capability error |
| Params/DSE/affine/residual analyses; host tensors/files; BLAS/ML/quantization/Sort/Scan | Frozen choices/versioned unknown facts; host-only APIs vs accelerator templates → ordinary host adapters and compositional specialization |

The coverage crosswalk governs the complete inventory. Each family requires semantics, interpreter/external model, verifier, backend eligibility, and discriminators before support claims. Unknown protocols remain unsupported, not opaque vendor-owned meanings. Merge vector packing uses committed token consumes and explicit atomic publication; semantic publication-slot capacity remains separate from physical storage. Original lock operands, merge variants, and function/control blackbox forms illustrate distinct required capabilities: `spatial@e7a8f2f:src/spatial/node/LockMem.scala:19-38`, `spatial@e7a8f2f:src/spatial/node/MergeBuffer.scala:8-28`, `spatial@e7a8f2f:src/spatial/node/Blackbox.scala:8-61`.

## Reproducibility, execution, and scaling

Use a closed Spatial canonical schema, not pickle/Python AST or generic text as authority. Encode descriptors plus normalized raw bits, arbitrary integers as canonical strings, and required regions/tasks/resources/policies/requirements/origins. Reject unknown tags/missing IDs, reverify imports, and version explicit migrations. Generic xDSL text is inspection/round-trip evidence. SemanticKey covers normalized content/profiles/dependencies/order/admission; BuildKey adds pipeline/target/tool constraints; RunKey adds inputs/aliases/session/environment/RNG/replay. Provenance has its own digest for exact diagnostic rebinding; machine paths/object IDs do not identify semantics.

Python reference execution consumes one checked semantic revision, with separate runtime storage and task continuations. On the optional framework route, xDSL interpreter registration/listeners are reusable hooks, not numeric/platform-index or blocking-task semantics: `xdsl@0b10746:xdsl/interpreter.py:637-695`. Preserve committed observable events, causal predecessors, origins/activation/lane/resource, state changes, faults/wait/cancel/completion, and replay metadata. Diagnostic FP operation counts need not survive optimization. Untimed epoch/ordinal differs from cycle.

The backend consumes a checked implementation graph and explicit capability profile. Python decides numerical modes, lazy branches, reduction topology, masks, identity/lifetime, and protocols; vendor tools realize emitted structure and report functionality/resources/timing. Generation/synthesis success is not semantic equivalence. Optional native solvers can provide certificates verified in Python, candidate results independently checked in Python, or independent test vectors. A trusted native legality oracle would change the ownership boundary and is not adopted. No hidden Rust/native semantic core is proposed.

Keep loops/helpers structured, intern immutable descriptors, index accesses by backing ID, use worklists/call summaries, and cache analyses by revision/dependencies/options. Avoid whole-program all-pairs access checks and eager unrolling. Relational FIFO safety may need reusable invariants/preconditions or guards, not fixture recognition. R007 benchmarks capture/check/optimization/simulation separately, including aliases/nesting/tasks/wide arithmetic and trace/exploration costs. The appendix's one-run arithmetic timings are not those acceptance measurements.

## Proposed rules, acceptance, and remaining work

Propose one unchecked model, one Python semantic checker, immutable custom semantic/implementation records, privately published verified revisions, explicit effects/protocols and per-pass invalidation, canonical schema/cache identity, and a checked backend handoff. An optional derived xDSL adapter follows the named reuse/correspondence gate in R017. These remain research proposals.

Designed acceptance must reject malformed dominance/lifetime/token imports; preserve two consumes when one result is unused; keep untaken queue/division faults lazy; retain checked overflow/divzero despite unused values; preserve exact literal/conversion/FMA bits and fold/tree order; update backing reads through helper aliases; distinguish loop-local/outer/persistent state across invocations; resume capacity-one tasks without repeating operand effects; diagnose unsupported requested concurrency; invalidate capacity/profile/arbiter caches; retain prior snapshots after failed passes; and separate legal reference formats from target capability errors. Matched source/builder programs should share semantic content with honest origin differences.

Completed evidence supports tested framework mechanics, optional-dependency distinction, and the bounded representation/invariant experiments in R017. Remaining evidence concerns nested/task mutation/provenance stress, real semantic analysis/snapshot scaling, protocol/proof serialization, executable numeric special/status/RNG/intrinsic conformance, and backend safety/progress refinement. Native/vendor interoperability remains unmeasured. After adoption, S1 should complete capture→unchecked→checked→reference→diagnostics→serialization→one verified transform for composed memory code, with lazy faulting branches and alias/lifetime negatives. S4 adds consuming-queue branch cases and S5 adds communicating continuations, following the shared roadmap. The first three fixtures never define the full language.

## Reproducible bounded framework probes

On 2026-09-30, used a fresh virtual environment under `/private/tmp/spatial-pyr006-xdsl`, CPython 3.14.5, Darwin 25.6.0, arm64. CPU model and RAM were not obtained because the environment denied the attempted system query. Installed only `immutabledict==4.3.1`, `ordered-set==4.1.0`, and `typing-extensions==4.15.0`, whose downloaded wheels were `py3-none-any`. Read/imported the pinned source directly through `sys.path`; xDSL was not installed as a built distribution. Thus this tests source imports, not packaging/build metadata or all installed console tools.

To reconstruct, check out the exact xDSL pin in a reference directory, create an isolated Python 3.14.5 environment, install those three versions, and run the following standalone input with the repository directory as its argument. No Spatial code is involved. The probe operation uses an integer handle only to exercise framework mechanics; it is not a proposed FIFO dialect definition.

```python
import sys, io, importlib.metadata
sys.path.insert(0, sys.argv[1])
from xdsl.ir import Dialect
from xdsl.irdl import IRDLOperation, irdl_op_definition, operand_def, result_def, traits_def
from xdsl.dialects.builtin import Builtin, ModuleOp, i32
from xdsl.dialects.arith import Arith, AddiOp, ConstantOp
from xdsl.traits import MemoryWriteEffect, is_side_effect_free, is_speculatable
from xdsl.context import Context
from xdsl.parser import Parser
from xdsl.printer import Printer
from xdsl.transforms.common_subexpression_elimination import CommonSubexpressionElimination
from xdsl.transforms.dead_code_elimination import DeadCodeElimination
from xdsl.utils.exceptions import VerifyException

@irdl_op_definition
class Consume(IRDLOperation):
    name = "probe.consume"
    handle = operand_def(i32)
    value = result_def(i32)
    traits = traits_def(MemoryWriteEffect())
    def __init__(self, handle):
        super().__init__(operands=[handle], result_types=[i32])

ctx = Context()
for dialect in (Builtin, Arith, Dialect("probe", [Consume], [])):
    ctx.load_dialect(dialect)
c = ConstantOp.from_int_and_width(7, 32)
a, b = Consume(c.result), Consume(c.result)
m = ModuleOp([c, a, b]); m.verify()
print("consume traits:", is_side_effect_free(a), is_speculatable(a))
copy = m.clone()
CommonSubexpressionElimination().apply(ctx, copy)
DeadCodeElimination().apply(ctx, copy)
copy.verify()
print("consume count after CSE+DCE:", sum(isinstance(o, Consume) for o in copy.walk()))
print("original count after cloned passes:", sum(isinstance(o, Consume) for o in m.walk()))
out = io.StringIO(); Printer(stream=out, print_generic_format=True).print_op(copy)
parsed = Parser(ctx, out.getvalue()).parse_module(); parsed.verify()
print("generic text roundtrip:", copy.is_structurally_equivalent(parsed))
bad_t = Consume(ConstantOp.from_int_and_width(7, 64).result)
try:
    bad_t.verify(); print("bad operand type: accepted")
except VerifyException:
    print("bad operand type: rejected")
late = ConstantOp.from_int_and_width(1, 32)
early = AddiOp(late.result, late.result)
bad_order = ModuleOp([early, late])
try:
    bad_order.verify(); print("use before definition structural verify: accepted")
except VerifyException:
    print("use before definition structural verify: rejected")
names = {d.metadata["Name"].lower() for d in importlib.metadata.distributions()}
print("optional packages installed:",
      [n for n in ("cffi", "llvmlite", "heir-py", "textual", "numpy") if n in names])
print("python:", sys.version.split()[0])
print("base packages:", [(n, importlib.metadata.version(n))
      for n in ("immutabledict", "ordered-set", "typing-extensions")])
```

Observed output:

```text
consume traits: False False
consume count after CSE+DCE: 2
original count after cloned passes: 2
generic text roundtrip: True
bad operand type: rejected
use before definition structural verify: accepted
optional packages installed: []
python: 3.14.5
base packages: [('immutabledict', '4.3.1'), ('ordered-set', '4.1.0'), ('typing-extensions', '4.15.0')]
```

The second standalone input measures a flat arithmetic chain, then structural verify, cloning, and generic CSE with Python allocation tracing. Run in the same isolated environment with the reference repository argument. Reported peak is traced Python allocation for that iteration, **not process RSS**. Each size was run once, without warmups; the result is not statistically characterized.

```python
import sys, time, tracemalloc, platform
sys.path.insert(0, sys.argv[1])
from xdsl.dialects.arith import ConstantOp, AddiOp
from xdsl.dialects.builtin import ModuleOp
from xdsl.context import Context
from xdsl.transforms.common_subexpression_elimination import CommonSubexpressionElimination
print("machine", platform.machine(), platform.system(), platform.release())
for n in (1000, 10000, 30000):
    tracemalloc.start(); start = time.perf_counter()
    one = ConstantOp.from_int_and_width(1, 32); ops = [one]; value = one.result
    for _ in range(n - 1):
        add = AddiOp(value, one.result); ops.append(add); value = add.result
    m = ModuleOp(ops); built = time.perf_counter()
    m.verify(); verified = time.perf_counter()
    copy = m.clone(); cloned = time.perf_counter()
    CommonSubexpressionElimination().apply(Context(), copy); optimized = time.perf_counter()
    _, peak = tracemalloc.get_traced_memory(); tracemalloc.stop()
    print(n, "build/verify/clone/CSE seconds",
          *(round(t, 4) for t in (built-start, verified-built, cloned-verified, optimized-cloned)),
          "traced_peak_MiB", round(peak / 2**20, 2))
```

Observed first-run measurements:

| Operations | Build seconds | Verify seconds | Clone seconds | CSE seconds | Traced peak MiB |
|---|---:|---:|---:|---:|---:|
| 1,000 | 0.0587 | 0.0293 | 0.0308 | 0.0240 | 2.81 |
| 10,000 | 0.6156 | 0.2880 | 0.3206 | 0.2546 | 27.99 |
| 30,000 | 1.9393 | 0.9254 | 1.0959 | 0.7649 | 84.36 |

Neither probe verifies Spatial token linearity, alias safety, faults, lazy task scheduling, numeric descriptors, full semantic serialization, arbitrary dialect interoperability, or HLS. Those remain acceptance obligations, not inferred successes.

## Implementation-readiness supplement — 1 October 2026

[[10 - Source Checker and IR Blueprint]] now defines closed operation/type/region registries, exact token/dominance verification, requirements, conservative analyses and pass transfer. [[40 - Package and Conformance Blueprint]] records the runtime baseline and reproducible curated xDSL experiment wheel; R017 makes the framework an optional adapter dependency rather than a core requirement. Nested-region framework and installed-wheel probes add bounded evidence; the framework still does not verify Spatial semantics.
