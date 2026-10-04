---
type: reference
title: "Python implementation readiness audit"
project: spatial-python
date: 2026-10-01
status: reviewed
---

> [!info] Follow-up — 3 October 2026
> [[11 - Design Refinement Iterations]] records the proposed repairs and new measured representation comparison. The current architecture uses immutable compiler-owned records with optional xDSL adapters. Findings and results below remain the dated historical review; see the follow-up for current closure and implementation limits.


## Purpose and boundary

> [!warning] Subsequent review — 2 October 2026
> [[09 - Fable Design Review]] reopens the floating underflow/status-oracle part of IR03 and identifies contract consistency and public-workflow follow-ups. The dated results below record what was checked at the time; they do not override the new counterexample or establish current numeric readiness. Historical probe archives are preserved.

David requested a further Codex review and discussion to establish whether the research tells contributors how to implement the full Python rewrite. This is a stronger question than whether the architecture proposal is coherent. The completed, dated [[06 - Python Research Completion Audit]] remains evidence of that earlier review and publication; it is not proof of implementation readiness.

The baseline is research revision `b56a49630f22b204ab1a4f0c531adf3647ac1639`. The working tree was clean at the start. Pure Python frontend, semantic compiler, and reference simulator remain the accepted direction. The detailed architecture and semantic changes remain proposed for professor review. This work authorizes further research, bounded experiments, documentation and publication, not production compiler implementation.

## Acceptance test for the research

For each intended language or infrastructure family, a contributor must be able to identify its source/API form, owned representation, checking algorithm, execution transition, hardware-plan construction and lowering route, diagnostics, and independently specified acceptance cases. A future instruction to “prove,” “verify,” or “provide an adapter” is insufficient when the method or interface is missing. A defined algorithm awaiting implementation and measurement is a different evidence state.

Readiness requires all of the following, with exact artifact references and cross-author review:

| ID | Requirement | Baseline status |
|---|---|---|
| IR01 | Concrete source grammar, intrinsic inventory, binding/type/effect algorithms and shared builder boundary | Under review; source spellings and inventory still illustrative |
| IR02 | Typed semantic/implementation records, operation families, tokens, region invariants, pass order and analysis invalidation | Under review; architecture specifies responsibilities more than complete interfaces |
| IR03 | Implementable numeric, conversion, intrinsic and RNG algorithms, including exact reference oracles and termination/resource outcomes | Under review |
| IR04 | Implementable local/concurrent state machine, continuation/scheduler, alias/lifetime and external-environment rules | Under review |
| IR05 | Concrete hardware-plan construction, lowering algorithms, ABI and target-capability methods across every intended family | Under review |
| IR06 | Package/module ownership, public invocation API, dependency baseline, canonical artifact schema, diagnostics and fixture format | Missing concrete S0 deliverable at baseline |
| IR07 | Full-family mapping of the above, dependency-consistent implementation tasks, and independent acceptance cases | Existing 18-family/106-document accounting needs an implementation-level crosswalk |
| IR08 | Independent discussion, repaired findings, source/probe verification, integrated documentation checks and publication | Active |

The stopping rule is an evidence-backed disposition for every requirement and family, with no unresolved semantic, representation, algorithm or interface gap necessary to implement the proposed scope. Professor adoption, production tests, measured performance and target execution remain separate obligations. The audit must state exactly which of these remains unrun rather than treating a research experiment as a compiler result.

## Review ownership

Three new Codex reviewers use GPT-6.1 Sol at extra-high reasoning with separate initial contexts. The frontend reviewer examines capture, checking and IR; the numeric reviewer examines arithmetic, profiles and reductions; the protocol/HLS reviewer examines state, simulation and physical lowering. The manager owns cross-family integration, packaging/artifacts and the final audit. Initial findings are challenged across reviewers before accepting resolutions; agreement alone is not evidence.

## Iteration record

| Iteration | Inspected evidence | Finding and next action | State |
|---|---|---|---|
| 0 | Current roadmap, four contracts, R005/R006/R007, clean baseline | API inventory, canonical schema, dependency baseline and repository plan were deferred to S0 | Concrete package/source blueprints drafted |
| 1 | Three independent domain reviews | Scalar assignment/return/component rules, closed IR schemas, numeric recipes/equality/certificates, continuation/fairness/cleanup and HLS construction methods were insufficiently specified | Five implementation blueprints drafted and challenged |
| 2 | Parent review and cross-author discussion | Task-group token was at risk of double consumption; generic xDSL verification accepted forward uses/duplicate tokens/wrong yields; uncommitted external issue cannot be abandoned; open endpoints do not prove progress | Explicit region verifier, one parent token, issued obligations and wait certificates selected |
| 3 | Packaging and independent bounded models | Unfiltered upstream wheel packaged unrelated namespaces; dirty rebuild also included build/lib. Packed-data quota differed from portable byte address span. Inactive vector lanes lacked a validity type | Fresh pinned archive and packaging-only filter reproduced; quota/address span split; MaskedVec added |
| 4 | Contract/library integration and independent reruns | Empty destination mapper effects, FIFOReg reset, multi-producer close, zero-bit aggregates, exact quantization scales and numeric divisors needed explicit rules | Rules selected, main contracts/studies/examples updated; cross-review complete; integrated checks passed; publication verified |

## Full-family implementation crosswalk

Design references: **Source** = [[10 - Source Checker and IR Blueprint]], **Numbers** = [[20 - Numeric Engine Blueprint]], **State** = [[30 - State Simulator and HLS Blueprint]], **Package** = [[40 - Package and Conformance Blueprint]], **Libraries** = [[50 - Library and Migration Recipes]]. All are proposed and unimplemented. The table supplies the implementation destination for every matching gate in the 106-document ledger and R005's 124-path inventory. Source and State contain closed parametric registries; library callable inventory is separate from file counting.

| Gate/family | Source and representation | Check / execution method | Target construction method | Independent cases / failure boundary |
|---|---|---|---|---|
| G01 Capture/helpers | Source grammar, symbols, DefinitionRef, unchecked effect ledger | Manifest acquisition, lexical resolver, meta evaluator, bidirectional check, call-summary substitution | Calls/regions with explicit captures and lifetime; verified optional inline | Poison host hooks, dropped/duplicate effect, local escape, source/builder parity; source/type/lifetime errors |
| G02 Numbers | NumericOpSpec, typed raw bits, numeric/RNG resources | Exact integer/rational normalization, strict recipes/equality and proof checker; explicit committed draw state | Finite lattice/quotient/root helpers, certified tables or checked vendor adapter | Small-format exhaustive cases, signed zeros/sNaNs, FMA, rounding ties, tampered proofs, RNG prefix; numeric fault vs resource/capability outcome |
| G03 Aggregates | Vec/Tuple/Record/MaskedVec; closed lane/field/packing registry | Exact field/lane types, per-axis bounds, valid-lane guard; stable pack/shuffle/compress and explicit materialize | Finite bit slices/muxes and validity wires; zero-bit payload retains control | Endian/field order, empty aggregate, inactive lane, one-hot conflict, wrong callback result; aggregate/bounds faults |
| G04 Storage/windows | Handle/backing/generation/view/init and version leases | Composed coordinates, alias/init guards, reset/shift snapshots, publication credit transitions | Conservative one-cell map, bounded instances/versions, checked packing/banking/ports | Alias fills, warmup, held old version, masked shift, body/outer lifetimes; init/stale/capacity diagnostics |
| G05 Control | Structured if/loop/region/task_group/FSM/forever | Isolated typed regions and linear domain tokens; signed-step domains; resumable PC/frame execution | Structured ordered C++ or finite task-slot protocol machine | Branch lazy faults, negative step/tails, one parent join token, FSM old-state/post-action reads, stop W; malformed-region/control errors |
| G06 Reductions | Scalar/memory policy, topology, law and contribution lease | Fold contribution/combine sequence, fixed tree, exhaustive law certificate, private publication | Same topology/ordered contributions, bounded scratch and helper routes | Empty/disabled dual domains, first-combine fault, consuming mapper, one-cell lease; law/domain/alias diagnostics |
| G07 Transfers/allocation | Captured transfer plan, item PC, allocator profile and generations | Array preflight/full snapshot; streaming committed prefix; separate quota and first-fit address span | Explicit ownership/scratch/DMA request-response, bounded pools and virtual-address map | Overlapping copy, duplicate scatter, invalid streamed address, W4×33 quota/span, late response/reuse; allocation/ownership faults |
| G08 Queues/arbiters/merge | Closed state tags, masks, endpoints, FIFOReg, frame/packer | Unified resource/selector RR, old-state atomic batch, capacity-one FIFOReg, staged merge consumes | Single-owner finite resource machine, bounded packer, logical capacity preserved | Full/empty, sparse vector masks, competing compound requests, reset-empty FIFOReg, cap-one merge; fault vs wait |
| G09 Streams/frames/buses | Endpoint/field vs record schema, per-producer close | Exactly-once captures, explicit zip prefix, all-producer close/drain, wait dependency graph | Stable valid/payload/ready ports, request IDs/credits and concurrent adapters | Two independent field reads, partial tuple, unrelated open endpoint, unknown model, late completion; End/Wait/Deadlock/Unknown |
| G10 Locks | Key set/Permit, protected-domain and ownership records | Exact key equality, deduplicated atomic acquire, canonical nesting, visibility-before-release | Bounded exact comparator/table plus resource arbiter; permit independent of global scheduler | Alias bypass, duplicate keys, disjoint holders, fault/cancel drain; ownership/reentrancy diagnostics |
| G11 Components | Explicit as_component projection, borrowed signature, foreign model/manifest IDs | Call-summary substitution, lifetime check; registered explicit state/input model | ComponentPlan ports/reset/IDs/storage authority/event projection and artifact digests | Aliased formal fill/read, callee local escape, missing model, reset/late response; model/interface capability errors |
| G12 Host workflow | SourceBundle, BufferView/Backing, Invocation/Session | Exact ingress, shared-owner snapshots, byte/shape/stride bounds, session ownership | Portable typed ABI and explicit environment address bindings | Negative/zero stride, overlap, nonzero padding, zero-bit cell, timeout then resume; preparation/busy/schema errors |
| G13 Libraries/meta | Closed source templates, DefinitionRef callbacks, ScaleRatio record | Explicit per-callable recipes, exact shapes/order/aliases; finite scale arithmetic | Expand through ordinary checked operations; no whole-app recognizer | LIB01–12: coefficients/transposes/padding/training/quantization/stability/tails/order/caches; shape/profile diagnostics |
| G14 Debug/reference | Print/assert/breakpoint/exit tags, origin and event records | Closed formatter/typed operands, token order, explicit runtime hooks and incomplete outcomes | Encoded trace/fault route or named unsupported debug-hook capability | Untaken assertion, committed prefix, non-ASCII spans, breakpoint resume; fault vs internal defect |
| G15 Passes | Private revisions, requirement transfer and dependency side tables | Clone-transform-verify-publish, explicit discharge/substitution, conservative invalidation | Checked implementation revision before emission | Failed candidate retains old bytes; dropped guard/trait misuse/changed profile rejects; internal optimization defect |
| G16 Dependence/storage | AccessRegion, physical map/inverse, port/dependency graph | Constant/interval/affine proof, finite enumeration/matching, Unknown guards/rejection | Conservative injective map, complete RMW/coherence, finite issue groups and modulo checks | Packed word collision, two writes on mixed RAM_2P, overlapping lanes, version reuse; constraint/Unknown diagnostics |
| G17 Parameters/DSE | Frozen meta variants, target/candidate/proof identities | Stable candidate enumeration, check before cost, deterministic Pareto filtering by evidence level | Bounded controller/memory/helper choices; vendor reports later | Semantic capacity cannot become a tuning knob; stale proof and mixed evidence reject; hard vs soft constraints |
| G18 Backend/infrastructure | Closed plan/project/evidence schema and named target profile | Canonical import/recheck, source correspondence, explicit capability record | HLS manager/adapters or certified component; reproducible build/report pipeline | Unsupported route, dropped fault/response, source-invented ID, nonreproducible artifact; target/build/evidence failure |

Every row has a concrete method and named acceptance obligations. Implementation still has to execute those obligations. The design deliberately allows sound conservative rejection or runtime guards where a universal static analysis would be undecidable; it does not claim all legal programs are statically provable or every format fits one FPGA.

## Review findings and selected repairs

- **Frontend/IR:** immutable scalar bindings, exact return placement, explicit component borrowing and closed meta/operation/region schemas replace implementer discretion. Task-group parent tokens enter once. Spatial verifies same-block order, token uses and result signatures itself.
- **Numerics:** rigorous rational recipes plus exact identity/root cases settle midpoint/equality questions for finite typed inputs. Point proofs and full-domain completion/target certificates are distinct. The finite raw-bit float fallback is defined but can be extremely costly.
- **Execution:** fair action scheduling and one pending captured request per task preserve suspension. Resource and selector arbitration share one grant procedure. Issued external obligations survive cancellation, fault and restart until actual completion/abort.
- **State boundaries:** aggregate producer close, constructive wait/deadlock records, FIFOReg reset-empty behavior, MaskedVec validity, zero-bit identity, and separate allocator quota/address span now have explicit rules.
- **Libraries:** exported routines have ordinary-template recipes. ScaleRatio gives exact quantization a finite representation; sample counts require exact numeric conversion. BLAS coefficients, padding, training snapshots, sort stability and reduction order are explicit deliberate choices.
- **Packaging:** CPython/framework/dependencies, public workflow, SpatialJSON-v1 including unchecked input, provenance and buffer/session ownership are specified. A packaging-only xDSL discovery filter prevents unrelated namespace content from entering the core wheel.

## Cross-author discussion and disposition

| Review | Challenge and repair | Disposition |
|---|---|---|
| Frontend ↔ state | Parent token must enter task group once; total-pure regions carry no token; Index needs its own reference value; inactive vector results need MaskedVec; mapper-local storage needs a scoped contribution lease | Both blueprints use the same region/request/value rules |
| Numeric ↔ frontend | Bool-result comparisons cannot propagate Bool into numeric operands; Index embedding is explicit; observed status and possible faults are effects; exact scales use a bounded record | Type/effect and record interfaces aligned |
| Numeric ↔ libraries | Fixed fractional-only all-zero calibration still needs scale one; normalized exact sums can increase exponent; count conversion must not wrap; storage zero-point is integral | Conservative finite bounds and explicit divisor/storage checks added |
| State ↔ package/libraries | Unchecked artifact missing; zero-byte storage still has logical identity; read-only callbacks may fault but total-pure cannot; array-return helper needs caller allocation; filtering retains the value captured before predicate | Schema and recipes repaired without hidden ownership transfer |
| Parent ↔ all | Generic framework verifier misses Spatial checks; upstream wheel discovery/dirty rebuild changed contents; address span differs from quota; an unversioned AMD link displayed 2026.1 | Independent probes/source checks reproduced; installed wheel pinned; allocator corrected; vendor link replaced by verified 2025.1 URL |

The reviewers found no remaining necessary interface contradiction within their reviewed scope after these repairs. This is a review conclusion supported by named methods and counterexamples, not proof that every future program or target will work. The original architecture audit remains a separate dated result.

## Reproduced research experiments

The parent independently reran each probe. These are bounded method experiments, not production Spatial conformance or HLS results.

| Experiment | Observed evidence | Limit |
|---|---|---|
| Structured xDSL | Nested helper/branch/loop/task-group graph cloned and text-roundtripped; effect nodes survived CSE/DCE; implicit ancestor capture rejected | Framework alone accepted same-block forward use, duplicate order token and wrong yield arity; custom Spatial verifier required |
| Clean packaging | Two fresh pinned archives with fixed epoch/build dependencies and namespace filter produced the same 1,169,644-byte wheel SHA-256 `7ba55df59ac1c85aaf7775526eb8cd95e72b89170c359fe461e0746b4f069183`; installed core-only environment reran framework probe | One CPython/platform baseline; no whole compiler benchmark |
| Numeric | 16,080 small-format value/status comparisons, 280 sqrt/rsqrt boundaries, 9,216 scale alignments, 65,025 Euclid pairs, 11,520 calibration bounds, four lattice formats, rational constants, exact midpoint and seeded draws | Selected finite cases; no full intrinsic library certification or vendor parity |
| State | 28 RR cursor states, 54 compound-arbiter states, four cancellation phases, cap-one producer/consumer, 144 layout inverses, packed RMW, FIFOReg/close, allocator span and wait-graph cases | Small research models; not arbitrary liveness proof or RTL execution |
| Artifact | Handwritten canonical bytes, independent OpenSSL hash, 18 malformed-input rejections, 20,000-bit integer roundtrip, Unicode span and shared-backing snapshot | Format mechanics only; no production importer/cache |
| Libraries | Eleven independently calculated values/order discriminators | Expected fixtures only; LIB12 compiler cache/origin case remains future implementation acceptance |

Download the [complete research probes and recorded outputs](<50 - Python Rewrite/60 - Validation/assets/2026-10-01-implementation-readiness-probes.zip>). The archive includes six probe sources, results, reproduction instructions, dependency hashes and a manifest. SHA-256: `6b15db6aff089e2823aa933eefc0da23110a20ece3e549e5f69a34b74629eb17`. It contains no production compiler, third-party wheels or vendor artifacts.

## Remaining execution gates

Professor adoption of the architecture and deliberate semantic changes is still required. Production implementation, integrated source/builder/serialized-input conformance, the full numeric certificate corpus, compiler performance, generated C++, vendor/RTL validation and physical results are not run. The proposed `vitis-2025.1-z020-10ns` profile reuses identifiers from historical Rust evidence; those logs do not validate Python. Failure to fit an expensive generic helper on that device is a target constraint, not permission to change the language result.

The purpose of this review is to make implementation tasks concrete enough to begin after approval. It cannot guarantee that no future implementation defect, missed edge case or performance problem will be found. Any such discovery must update the contract/design and discriminating cases before a support claim is made.

## Final verification and publication

The three domain reviewers and parent completed their cross-checks and found no unresolved necessary design/interface blocker in the reviewed scope. This is acceptance of the proposed implementation design, not professor adoption or a guarantee about unimplemented code.

| Requirement | Current disposition |
|---|---|
| IR01 | Specified: closed source/prelude/registry, meta and binding/type/effect algorithms, component and builder rules in Source |
| IR02 | Specified: owned records, parametric operations, isolated regions, token verifier, requirement transfer and invalidation in Source/Package |
| IR03 | Specified: exact arithmetic/intrinsic/equality methods, certificate checking, finite helpers, laws and random state in Numbers; bounded probes reproduced |
| IR04 | Specified: continuation/frame construction, scheduler/resource grant, cleanup/close, ownership/lifetime and wait classification in State |
| IR05 | Specified: conservative memory/port/schedule algorithms, universal protocol route, complete adapter fields and initial target/profile gates in State/Numbers/Package |
| IR06 | Specified: module/public API, pinned dependencies and clean wheel, canonical formats, buffers/session, diagnostics and fixture records in Package |
| IR07 | Specified: all G01–G18 rows map to methods/cases; library callables have recipes; roadmap has concrete entry tasks |
| IR08 | Cross-author review and repairs complete; source/probe/archive/document/site checks passed; remote publication and live-page/archive checks verified |

Fresh local verification on 2026-10-01 passed 25 changed/new Markdown documents, 74 new wikilinks, 19 fully qualified pinned citation ranges and syntax parsing of 32 Python snippets. The ledger still accounts for all 106 original spec documents; frozen D-26 is byte-identical to the baseline. Independently inspected source/theorem/vendor claims are recorded above; citation bounds alone do not prove support.

The local site build processed 550 documents and emitted 1,188 files including the historical presentation. The targeted HTML audit passed 48 homepage/Python/shared-decision/workflow pages and 2,206 internal links/anchors. The evidence ZIP member hashes, embedded probe parity and download target passed. Original Spatial, Rust and xDSL tracked source revisions are unchanged; the Rust checkout's pre-existing untracked local files were preserved.

Research revision [`053b3be6c55535a5c69d185decf2c36fdcdb4082`](https://github.com/davidydu/spatial-research/commit/053b3be6c55535a5c69d185decf2c36fdcdb4082) was committed and pushed under davidydu. [Pages deployment 36887633973](https://github.com/davidydu/spatial-research-site/actions/runs/36887633973) completed successfully using site revision `f9d5e0b161d9f4bba8e3e4858fd1f8b1b1fbd7f7`. Fresh HTTP reads returned 200 and the expected new content for the research home, implementation index, all five blueprints and this audit. The live 19,442-byte ZIP matched SHA-256 `6b15db6aff089e2823aa933eefc0da23110a20ece3e549e5f69a34b74629eb17`.

**Implementation-readiness research review complete.** The proposed design and its evidence are published. Professor adoption and all production/target gates listed above remain open. This publication record identifies the checked content revision; later audit-only bookkeeping does not retroactively change its evidence.
