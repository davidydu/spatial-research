---
type: deep-dive
title: "PY-R009 — HLS boundary and control lowering"
topic: python-hls-boundary-and-control
project: spatial-python
session: 2026-09-30
status: research-conclusion
source_files:
  - "spatial@e7a8f2f:src/spatial/codegen/scalagen/ScalaGenController.scala:74-104"
  - "spatial@e7a8f2f:src/spatial/codegen/scalagen/ScalaGenController.scala:180-219"
feeds_spec:
  - "[[40 - Python Compiler and HLS Contract]]"
---

## Recommendation

Build an explicit hardware implementation plan in Python, then emit HLS C++ and its build manifest. Begin with AMD Vitis as the first backend family. Keep numerical behavior, state/effect rules, task protocols, interface contracts, and required schedule constraints owned by the Python compiler. Use the vendor tool to schedule and bind the concrete implementation, generate RTL, and report what it achieved.

This is a design recommendation, not a claim that every Spatial construct maps to a pragma or that a vendor release has validated it. Full-language semantics and a target's accepted capability set are separate. Ordinary arithmetic/loops can take a direct route; explicit communication requires process/channel planning; protocols the vendor cannot represent need a defined generated state machine or external component route and associated validation. A missing route is a capability error.

The earlier `30 - HLS Mapping/` studies and Rust evidence remain useful references, but the old selected-program recognizers are not the architecture for this rewrite. [[PY-R002 - Numeric and Reduction Semantics]], [[PY-R003 - Control Memory and Effects]], and [[PY-R007 - Host Workflow Reproducibility and Validation]] establish the current proposed boundaries.

## Evidence read and version limits

The following primary documents were read on 30 September 2026. AMD's unversioned URLs returned several releases; the displayed release is recorded rather than assumed current. A real build must lock one tool release and revalidate its feature profile. No vendor installation or synthesis run was performed for this study.

| Document | Source fact used | Design consequence |
|---|---|---|
| [C modeling and RTL implementation, UG1399, 2026.1](https://docs.amd.com/r/en-US/ug1399-vitis-hls/C-Modeling-and-RTL-Implementation) | Stream depth and task overlap can affect RTL completion; a non-dataflow producer can fill its FIFO before the consumer starts | C execution is insufficient evidence for bounded channel progress |
| [Canonical body, UG1399, displayed 2024.2](https://docs.amd.com/r/en-US/ug1399-vitis-hls/Canonical-Body) | Canonical dataflow imposes producer/consumer and outer-body restrictions; control belongs inside process functions; some FIFO feedback is described separately from array dependencies | Analyze process/channel shape and release support before choosing DATAFLOW; do not infer that all feedback is forbidden or supported |
| [Data-driven task parallelism, UG1399, 2026.1](https://docs.amd.com/r/en-US/ug1399-vitis-hls/Data-driven-Task-level-Parallelism) | Tasks and channels are instantiated explicitly; tasks persist and wait for data; `hls_thread_local` matters for C simulation lifetime | Always-running tasks are a distinct lowering class with explicit activation/reset semantics |
| [Adding RTL blackboxes, UG1399, displayed 2025.2](https://docs.amd.com/r/en-US/ug1399-vitis-hls/Adding-RTL-Blackbox-Functions?contentId=JUBdYjXi4lQLNDA83BPHJg) | The interface uses a C signature, JSON description, and Verilog IP; it has clock/reset/enable and protocol restrictions, including restrictions on structures and top-level I/O | External components require adapters and a checked manifest; “blackbox” is not a universal escape hatch |
| [Fixed-point identifier summary, UG1399, 2025.2](https://docs.amd.com/r/2025.2-English/ug1399-vitis-hls/Fixed-Point-Identifier-Summary) | Quantization/overflow settings apply at assignment/initialization rather than every intermediate calculation | The emitter must preserve Spatial's per-operation normalization explicitly |

Original source also warns that simulated `breakWhen` differs from synthesized behavior, while its generated `ParallelPipe` calls ordinary code generation and its `Switch` emits conditional branches: `spatial@e7a8f2f:src/spatial/codegen/scalagen/ScalaGenController.scala:74-104`, `spatial@e7a8f2f:src/spatial/codegen/scalagen/ScalaGenController.scala:180-219`. These facts motivate explicit cancellation and concurrent validation; they do not settle the proposed hardware contract.

## Compiler and vendor responsibilities

Everything in this table is a proposed division of work.

| Python Spatial must decide or verify | Vendor tool may choose within that contract |
|---|---|
| Types, rounding points, overflow, operation/fault guards, reduction tree | Matching operators and their legal implementation/latency |
| Logical allocation identity, alias relationships, reset and persistent lifetime | Physical memory/operator instances consistent with those identities |
| Dependency/order edges, branch selection, exactly-once consuming effects | Cycle scheduling that respects those edges |
| Task topology, FIFO capacity, arbitration and completion/cancellation protocol | Physical handshake/pipeline realization that refines the protocol |
| Required memory ports/banks/versions and permitted mappings | Supported RAM resources, binding, legal partition implementation |
| Host/device ABI, packing, transfers, memory ownership, external component contract | Interface adapters supported by the selected target flow |
| Hard constraints versus tuning preferences; source-level explanation of failures | Achieved II, latency, resource estimates, generated RTL, warnings |

The Python implementation plan carries proof obligations and required capabilities before C++ emission. Source schedule requests are classified as semantic constraints, hard hardware requirements, or soft preferences. A failed hard requirement fails hardware validation. A missed soft preference is reported with the achieved result. Neither category can change numerical grouping or FIFO semantics silently.

## Control mapping by semantic family

| Semantic family | Proposed implementation plan | Required preservation checks |
|---|---|---|
| Ordered region and sequential loop | Ordered statements/loops with explicit temporaries and dependence edges | Effects and active faults stay ordered; iterations declared sequential do not overlap observably |
| Pure scalar arithmetic | Typed helper calls or primitive expressions with explicit result normalization | No C++ promotion, signed-overflow behavior, or host literal conversion changes the value |
| Runtime branch | Branch regions with guarded effect issue; merge only selected results | Untaken reads/consumes/faulting operations do not execute |
| Pipelined loop | Loop plus legal overlap plan, dependence distances, guards, and storage versions | Preserve loop-carried dependencies, tails, lifetime and fault policy; inspect actual II |
| Lane parallelism | Explicit active-lane map and legal lane resource accesses; unroll only after checking | Inactive lanes emit no effects; vector FIFO order and shared accesses are defined |
| Associative reduction | Legal tree for the typed operator, separate contribution scheduling | Only lawful regrouping; contribution effects remain exactly once and ordered as required |
| Ordered fold | Recurrence preserving each operation and seed-once behavior | No automatic balanced-tree substitution; latency can constrain II |
| Fixed tree reduction | Materialized tree and leaf order independent of scheduling annotation | Padding only with a proven neutral value; preserve empty and disabled behavior |
| Independent fork/join | Concurrent processes with explicit start/completion tokens | All children complete before join; serial realization only when permitted by the schedule contract |
| Communicating task graph | Static process/channel network with bounded storage and explicit endpoint/arbiter contracts | Do not serialize a blocking producer before its consumer; compare allowed event traces |
| General FSM | State register/encoding plus condition, action, next-state regions under their specified order | General bit/record state retained; no assumption that the source FSM is merely an integer counter |
| Forever/stream controller | Persistent task network with environment and termination/cancellation channels | Waiting is distinct from completion; activation/reset and finite-input handling are explicit |
| Stop/cancellation | Stop observation, issue suppression, in-flight accounting, drain/ack, and restart state | No erase of already committed effects; bounded resources released only under the protocol |

These rows describe lowering strategies, not demonstrated support. Exact protocol transitions belong to the advanced state/communication study and must be preserved by the implementation plan. A pattern match on a language operation is appropriate; matching a complete lab program to handwritten C++ is not reusable lowering.

## Three routes for communicating control

Choose the route per checked task subgraph, with a recorded reason.

1. **Control-driven dataflow.** Use a statically instantiated set of process functions and channels for finite invocations that meet the chosen release's constraints. Represent start/join and producer/consumer ownership. Give conditional work a process-local condition or a valid/token protocol; do not simply omit a task call and hope remaining tasks can finish.
2. **Persistent data-driven tasks.** Use an explicitly supported task model for always-running stream graphs. Persistent local state, reset, offered input, readiness, and completion tokens remain visible. A library's available memory/scalar extensions require separate release-specific checks; a stream-only example does not prove arbitrary memory interfaces work.
3. **Explicit protocol machine or integrated component.** When a graph needs multiway arbitration, keyed ownership, cancellation, or interfaces outside the selected dataflow subset, lower its protocol to explicit state and handshake logic. A generated HLS state machine can handle supported ports/resources; otherwise emit an integration manifest for separately validated RTL/component logic. Preserve the compiler's Python ownership of that design and reject targets lacking a legal integration path.

The third route is an architectural obligation, not a claim that arbitrary legacy RTL can be imported unchanged. Its contract names data widths, clocks/resets, valid/ready stability, stalls, latency/ordering, storage capacity, error signals, and state reset. Require a Python transition model plus a vendor/RTL test harness and independent trace checks for every adopted component. A blackbox's C model is useful for a vendor testbench but cannot replace the Python semantic model.

For a capacity-one producer/consumer pair, a direct sequential call schedule may deadlock even though the communicating graph has a completing trace. The compiler must select a concurrent route or explicitly prove an alternative schedule legal. Replacing the FIFO with an unlimited software queue changes the progress model. This is a derived counterexample, not a vendor run.

## Order, nondeterminism, and trace refinement

Reference execution of an ordered region has a declared effect order. A communicating graph may allow several interleavings. Its protocol contract defines which orders are legal, with arbitration decisions taken from explicit request/readiness state. A deterministic reference scheduler records one reproducible witness; it does not prove all schedules converge or force that witness's global order onto hardware.

Hardware correctness therefore requires trace refinement: after hiding internal implementation steps, every observable hardware event sequence must be allowed by the source protocol under the same environment assumptions. For deterministic programs, outputs/effects must agree exactly. For intentionally schedule-dependent arbitration, compare against the allowed ordering rules and state transitions, not one convenient expected output. Bounded model exploration can test this obligation on finite instances; it is not a general liveness proof.

Trace membership alone establishes only safety: an implementation that stalls forever after a valid prefix could satisfy it. The target also owes **termination, deadlock, and fair-progress refinement** under the source's declared environment/fairness assumptions. Completion, fault, close, cancellation, and stable waiting/deadlock outcomes are observable classifications. Infinite internal stuttering cannot replace a source transition that must eventually progress; an infinite hardware execution must correspond to an allowed infinite source behavior or a permitted indefinite external wait. Temporary pipeline stalls are allowed. A stable target deadlock cannot be introduced where the corresponding source has an enabled internal action or a progress obligation whose assumptions are met.

For example, a capacity-one channel with a producer sending 11 then 22 and a consumer receiving twice must complete under a fair scheduler when both endpoints are active. Emitting only the first send and then remaining busy forever fails this contract despite its valid event prefix. If the environment may withhold input forever, waiting remains permitted; if the source itself permits deadlock, the compiler must not invent a general completion guarantee. Record progress arguments/assumptions per lowering route, and test bounded instances under adversarial stalls. Neither a timeout nor one successful run proves universal liveness.

False-path speculation, dead-code elimination of a consume, and CSE of queue status across mutation violate this obligation. So can a transform that increases queue depth when full/empty observations are source-visible. Capacity is a semantic property in such programs, not an unconditional tuning parameter.

## Faults and device interfaces

The reference language can report active bounds, initialization, or arithmetic faults with source context. A hardware profile must explain how those obligations are handled: static proof, validated invocation preconditions, or explicit runtime guard/error protocol. A simulation-only exception is insufficient. Fault guards that affect issue/drain behavior belong to the task protocol; a generated C++ `assert` is not a substitute for synthesizable error handling.

A device error record identifies the kernel/profile and operation ID, with a host map back to source. Earlier committed DMA writes or stream tokens remain committed. Mark outputs incomplete and drain or reset through the adopted protocol. If a target cannot preserve the required fault semantics, require proof that the fault is unreachable or reject that profile.

Host/device ABI manifests must fix argument order, numeric bit widths, byte order, memory extents/strides, alias requirements, stream fields and frame markers, alignment, initialization, and completion/error signals. Distinguish an atomic record-token channel from a bundle of independently consumed field endpoints. The original `StreamStruct` node has a named-field dequeue (`spatial@e7a8f2f:src/spatial/node/StreamStruct.scala:12-20`); a structure's shape alone does not establish atomic consumption. Explicit coherence adapters must state when fields are gathered, retained, or released, with readiness and cancellation behavior. Target-specific padding cannot enlarge the source's logical accessible region.

## Evidence required before claiming a hardware feature

| Evidence level | What it establishes | What it does not establish |
|---|---|---|
| Checked Python program and reference execution | Proposed language behavior for the executed inputs | HLS legality or hardware equivalence |
| Generated C++ structural/host checks | Emission consistency and ordinary compiled behavior where the harness models it | Arbitrary-precision vendor semantics, bounded concurrency, or timing |
| Vendor C simulation | Selected vendor C/library behavior | Bounded RTL progress or physical fit |
| C/RTL simulation and protocol traces | Tested RTL behavior and handshakes under recorded scenarios | All interleavings or all device conditions |
| HLS synthesis reports | Achieved schedule and estimated resources for that tool/part/constraint set | Final placement/routing timing or board behavior |
| Implementation reports and board tests | Reported physical results and observed device cases | General correctness outside their stated coverage |

Each result records tool release, device/clock, generated artifact hashes, input/environment trace, numeric/protocol profile, warnings, and whether constraints were met. Keep functional success, achieved II, resource fit, and timing closure as separate fields. Older Rust results cannot be relabeled as Python backend evidence.

## Alternatives and decision conditions

Directly emitting C++ from the captured AST would couple source syntax to target details and lose the common semantic checkpoint. Emitting generic MLIR arithmetic/control immediately would also erase needed information unless Spatial-specific effects, widths, trees, and protocols survive. A full new RTL backend could provide more control, but is a separate backend project; it is not required to make the compiler Python. The recommended implementation-plan boundary supports HLS first while keeping explicit component integration possible.

Choose the exact vendor release/board profile when the implementation environment is established, then lock and validate it before claiming any feature. Current documentation supports the architecture's routes; it does not prove a single release supports their unrestricted combination. Reconsider the backend family if required protocols repeatedly need unsupported integration, verified semantic adapters dominate emitted hardware cost, or achieved quality fails declared workloads after attributed optimization. Those are evidence-based reversal conditions, not reasons to postpone defining Spatial semantics.
