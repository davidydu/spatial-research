---
type: deep-dive
title: "Independent review of Python architecture and contracts"
topic: python-independent-architecture-review
project: spatial-python
session: 2026-09-30
status: research-conclusion
source_files:
  - "xdsl@0b10746:xdsl/ir/core.py:1178-1235"
  - "xdsl@0b10746:xdsl/ir/core.py:1246-1323"
  - "spatial@e7a8f2f:src/spatial/node/StreamStruct.scala:12-20"
  - "https://mlir.llvm.org/docs/Bindings/Python/#extending-mlir-in-python (accessed 2026-09-30)"
  - "https://docs.python.org/3.14/reference/expressions.html#evaluation-order (accessed 2026-09-30)"
feeds_spec: []
---

## Scope, independence, and result

Reviewed R001/R004 surface recommendations, R006 architecture, R007 workflow, R009 HLS boundary, [[04 - Python Implementation Roadmap]], and proposed contracts [[10 - Python Language Contract]], [[30 - Python State and Protocol Contract]], and [[40 - Python Compiler and HLS Contract]]. Consulted R008 for imported protocol definitions. Re-read manager repairs, [[D-28]], [[05 - Python Professor Brief]], and the condensed [[20 - Python Numeric Contract]] for consistency. The detailed PY-R011 profile study was not yet on disk at this review; its numerical completeness is outside this certification.

**Authorship overlap:** this reviewer authored R004 and R005/coverage ledger. Review of R004 is self-review, not independent support for source capture, its examples, or its usability judgment. No architecture authoring overlap applies to R006/R007/R009 or the condensed contracts. No learner, native-MLIR, Spatial compiler, original application, HLS, RTL, or board experiment was performed here.

The proposed division is plausible for the whole language: owned semantic verification and transition models precede target planning; xDSL stores explicit Spatial operations; target capability rejection cannot redefine a language family. The three findings below were repaired by the manager and re-read by this reviewer. They are **resolved at the proposed-contract level**; their executable gates remain open. No observed compiler defect or universal hardware feasibility result is claimed.

## AR-01 — P1: progress refinement must accompany trace safety

**Resolved in proposal, 2026-09-30.** Initially [[PY-R009 - HLS Boundary and Control Lowering#Order, nondeterminism, and trace refinement]] stated event-membership without a complete progress check. Its repaired section and state/compiler contracts now explicitly require termination/deadlock/fair-progress refinement, prohibit infinite internal stutter where progress is owed, and preserve permitted indefinite external waits. The capacity-one discriminator is retained in R009.

**Counterexample:** capacity-one producer sends 11 then 22; consumer receives twice and joins with 33. Hardware commits the first send, then spins internally forever without advancing the enabled consumer. Every finite observed prefix is source-allowed. Hiding internal steps therefore passes a prefix-safety check while introducing noncompletion in a closed graph whose fair executions finish. The same issue can prevent lock release or cancellation drain indefinitely without an illegal output token.

**Repair:** distinguish prefix/event safety from maximal outcomes and fair progress. The implementation correspondence must prohibit new closed-system deadlock, preserve the adopted resource/task fairness under stated environment assumptions, and discharge completion/drain obligations. Identify which guarantees follow from structure/invariants, which require a selected scheduled profile or component guarantee, and which remain unproved. Include an adversarial stalled-consumer implementation and a drain that never acknowledges. Bounded RTL exploration is evidence for its finite model; a timeout alone remains insufficient proof. This extends the existing policy rather than demanding one universal latency bound.

## AR-02 — P2: foreign reference models need a canonical registry boundary

**Resolved in proposal, 2026-09-30.** Initially R008's foreign descriptor allowed a reference function without an explicit canonical registry boundary. Repaired R006/R008 and state/compiler contracts now serialize model IDs/versions/code and transitive dependency digests, resolve them through a reviewed registry, prohibit undeclared live captures, and expose state/environment inputs. Registry admission is correctly described as a trusted audited extension, not automatic proof of arbitrary Python purity.

**Counterexample:** a registered reference model computes `gain * x` using a live host configuration object. Change gain after checking or reload a different implementation under the same name. Identical checked/build/run inputs then produce different reference values; cloning a graph or hashing its component name cannot freeze that behavior. A stateful model could similarly hide undeclared instance state.

**Repair:** canonical IR/manifests store a stable model ID, version/content digest, typed signature, declared state/effects/protocol, and closed configuration/dependency digests. An explicit invocation/runtime registry resolves that descriptor to the validated Python implementation or replay oracle; no callable belongs in serialized IR. Undeclared live captures reject, or are explicit environment inputs whose version/trace enters run identity. State belongs to the identified component instance and follows reset/serialization rules. Add cache reload, changed model, mutable-capture, and repeated-instance tests. This preserves foreign components while making the trust boundary reviewable.

## AR-03 — P2: distinguish failed planning from eligible emitted artifacts

**Resolved in proposal, 2026-09-30.** Initially R007's Compile row returned artifacts plus unresolved obligations, unlike the compiler contract's complete Emission boundary. The repaired row distinguishes eligible emitted success from failed/incomplete planning, explicitly ineligible for emission/build reuse.

**Counterexample:** a valid reference program uses an unsupported floating format. A project plus unresolved numeric mapping must not be reused as an eligible build simply because files exist. **Repair:** specify failed/draft planning output with named obligations versus successful checked emission with a complete capability record. Neither label implies vendor/RTL validation. Test cache/CLI/API behavior for unsupported numeric and protocol routes.

## Resolved concerns and evidence checks

- **Source-first versus raw-source-only:** the language contract now explicitly separates them. A callable adapter can preserve a body AST; raw file/cell acquisition is a reproducibility/dependency/provenance preference, not a necessity of AST compilation. Strong builder generation and exact literal/origin support remain acknowledged. R004's conclusion remains self-authored judgment, not independent learner evidence.
- **Native-framework fairness:** current R006 correctly allows Python-owned Spatial semantics on native MLIR storage. Python-defined dialects, passes and patterns are documented; inspectable Python infrastructure is a preference, not an extra professor requirement. Rechecked [official MLIR extension documentation](https://mlir.llvm.org/docs/Bindings/Python/#extending-mlir-in-python), accessed 2026-09-30. No native performance/interoperability result was inferred.
- **Order and field identity:** contracts agree on ordinary RHS-before-target and target-once augmented assignment. Rechecked [Python evaluation order](https://docs.python.org/3.14/reference/expressions.html#evaluation-order), accessed 2026-09-30. Atomic value-record tokens remain distinct from independently consumed StreamStruct fields; the latter is directly evidenced by `spatial@e7a8f2f:src/spatial/node/StreamStruct.scala:12-20`.
- **Framework evidence:** reran R006's first standalone `Consume` probe unchanged, against `xdsl@0b107461b3bfcd353d949fe00d3d1623bd6c826a`, in its existing isolated environment: CPython 3.14.5, immutabledict 4.3.1, ordered-set 4.1.0, typing-extensions 4.15.0. Exit 0; complete stdout matched R006. Two consumes survived CSE/DCE, original clone source retained two, text round-trip passed, wrong operand type rejected, and same-block use-before-definition passed framework verification. This bounded framework execution supports the separate Spatial verifier requirement; it proves no task/protocol legality. Inspected `xdsl@0b10746:xdsl/ir/core.py:1178-1235`, `xdsl@0b10746:xdsl/ir/core.py:1246-1323`.

## Strongest objection and implementation gates

The strongest objection is architectural breadth: exact numerics, arbitrary structured state, bounded communication, versioned memory and component integration require substantial custom verification and runtime machinery even with xDSL/HLS. A flat arithmetic framework probe cannot establish their scaling or target feasibility. The proposal is credible because it names these responsibilities and S0–S9 integrates each family's checker, simulator, diagnostics and evidence; this remains a hypothesis until representative composed slices and attributed measurements pass.

Before adoption, retain AR-01–03 as executable discriminators, finish/review the detailed numeric-profile dependency, and choose explicit migration/profile scope. Before support claims, test source/builder normalization, aliases and generations, total-pure versus faulting/blocking operations, stop admission windows, publication credits, independent fields, foreign model identity, and actual target routes. Preserve separate reference, plan, vendor, RTL and device statuses. Benchmark the R007 workloads as specified; neither the one-run framework timings nor documentation validation satisfies those gates. D-28/brief accurately keep the detailed architecture proposed and compiler/HLS unimplemented; this review supplies no professor approval.
