---
type: deep-dive
title: "PY-R005 — Full language coverage and migration"
topic: python-full-language-coverage-and-migration
project: spatial-python
session: 2026-09-30
status: research-conclusion
source_files:
  - "spatial@e7a8f2f:src/spatial/lang/api/SpatialVirtualization.scala:93-116"
  - "spatial@e7a8f2f:argon/src/argon/lang/types/Num.scala:8-50"
  - "spatial@e7a8f2f:argon/src/argon/lang/Vec.scala:11-82"
  - "spatial@e7a8f2f:argon/src/argon/lang/Struct.scala:7-24"
  - "spatial@e7a8f2f:src/spatial/node/HierarchyMemory.scala:48-97"
  - "spatial@e7a8f2f:src/spatial/node/RegFile.scala:50-105"
  - "spatial@e7a8f2f:src/spatial/lang/LineBuffer.scala:16-38"
  - "spatial@e7a8f2f:src/spatial/node/LUT.scala:10-34"
  - "spatial@e7a8f2f:src/spatial/node/Control.scala:9-117"
  - "spatial@e7a8f2f:src/spatial/lang/control/FSM.scala:8-23"
  - "spatial@e7a8f2f:src/spatial/lang/control/MemReduceClass.scala:34-85"
  - "spatial@e7a8f2f:src/spatial/node/DenseTransfer.scala:34-63"
  - "spatial@e7a8f2f:src/spatial/node/SparseTransfer.scala:27-44"
  - "spatial@e7a8f2f:src/spatial/node/DRAM.scala:11-31"
  - "spatial@e7a8f2f:src/spatial/lang/api/PriorityDeqAPI.scala:10-21"
  - "spatial@e7a8f2f:src/spatial/lang/api/PriorityDeqAPI.scala:55-104"
  - "spatial@e7a8f2f:src/spatial/node/MergeBuffer.scala:8-15"
  - "spatial@e7a8f2f:src/spatial/node/StreamStruct.scala:8-22"
  - "spatial@e7a8f2f:src/spatial/node/FrameTransmit.scala:26-43"
  - "spatial@e7a8f2f:src/spatial/lang/Bus.scala:23-75"
  - "spatial@e7a8f2f:src/spatial/lang/LockMem.scala:54-62"
  - "spatial@e7a8f2f:src/spatial/lang/LockMem.scala:167-181"
  - "spatial@e7a8f2f:src/spatial/lang/Blackbox.scala:34-94"
  - "spatial@e7a8f2f:src/spatial/lang/api/FileIOAPI.scala:11-66"
  - "spatial@e7a8f2f:src/spatial/lib/MetaProgramming.scala:14-42"
  - "spatial@e7a8f2f:src/spatial/lib/Scan.scala:6-38"
  - "spatial@e7a8f2f:src/spatial/lib/Sort.scala:16-38"
  - "spatial@e7a8f2f:argon/src/argon/lang/api/DebuggingAPI.scala:7-34"
  - "spatial@e7a8f2f:argon/src/argon/Issue.scala:5-19"
  - "spatial@e7a8f2f:src/spatial/metadata/access/AffineData.scala:24-48"
  - "spatial@e7a8f2f:src/spatial/traversal/banking/BankingStrategy.scala:7-27"
  - "spatial@e7a8f2f:src/spatial/targets/HardwareTarget.scala:7-48"
  - "spatial@e7a8f2f:src/spatial/dse/DSEMode.scala:3-10"
  - "spatial@e7a8f2f:src/spatial/codegen/pirgen/PIRCodegen.scala:17-26"
  - "spatial@e7a8f2f:fringe/src/fringe/SpatialIP.scala:18-39"
feeds_spec:
  - "[[10 - Python Language Contract]]"
  - "[[20 - Python Numeric Contract]]"
  - "[[30 - Python State and Protocol Contract]]"
  - "[[40 - Python Compiler and HLS Contract]]"
---

## Recommendation and evidence boundary

Treat the Python rewrite as a full language and compiler project with incremental implementation. Account for every original construct now through an explicit semantic family, representation obligation, implementation stage, and evidence gate. An initial implementation may reject later-stage constructs with a precise capability diagnostic; that rejection does not remove them from the intended language. The three introductory examples do not bound this project.

This note supplies the substantive destinations for all **106 original `type: spec` documents** in [[01 - Python Coverage Ledger]]. The document inventory has nine subject areas and includes index pages; 106 is not a feature or support count. A separate pinned-source gap check covers **58 files under `src/spatial/lang/` and 33 under `src/spatial/node/`**, plus **24 Argon language files and nine Spatial library files**: 124 paths, each assigned below. `src/spatial/math/LinearAlgebra.scala`, compiler passes, emulation, models, and Fringe provide additional evidence outside that path baseline.

The source pin is `spatial@e7a8f2f7f776dd0c5ac7fc03f16b3ed4d97021f0`. The original notes are a research map whose claims require source inspection. Several old simulator notes call Scalagen universally authoritative; this project does **not** inherit that premise. Original APIs, generated simulation, the separate tick-driven executor, and hardware templates can disagree. [[PY-R002 - Numeric and Reduction Semantics]] and [[PY-R003 - Control Memory and Effects]] identify concrete discrepancies and propose explicit contracts. Earlier Rust decisions remain historical evidence, never Python validation.

All family policies and stage assignments below are **proposals for professor review**. Source citations establish the existence or shape of the original construct, not approval of the new rule. No original Scala build, Python Spatial compiler, migration translator, HLS synthesis, or learner study was executed for this note. The executed work is document accounting, pinned path/declaration inspection, and citation/link validation.

The surface recommendation in [[PY-R004 - Capture Composition and Diagnostics]] is source-first, with a compiler-owned builder for generated programs. [[PY-R001 - Programming Model Study]] contains the initial comparison; neither surface has been adopted. Both must express the same checked language. [[PY-R006 - Compiler Architecture and Framework Choice]] now proposes immutable checked Spatial records, with xDSL only as a justified derived adapter under [[PY-R017 - Compiler Representation Comparison]]; [[PY-R008 - Advanced State and Communication Protocols]] proposes explicit resumable transitions for the advanced families. [[PY-R007 - Host Workflow Reproducibility and Validation]] supplies the proposed host/run contract; [[PY-R009 - HLS Boundary and Control Lowering]] supplies proposed implementation-plan and HLS boundaries. These remain draft recommendations. This crosswalk references their candidate contracts without treating a framework, protocol, or hardware route as adopted or implemented.

## Dispositions, stages, and gates

Every ledger row uses one or more of these dispositions with a concrete explanation. A disposition is a research recommendation, not implemented support.

| Code | Meaning | Required accounting |
|---|---|---|
| P — preserve intent | Retain a language capability and its identified observable contract | State the contract, representation, and conformance cases; do not assume every old backend implements it identically |
| R — revise | Deliberately replace ambiguous, unsound, inconsistent, or Python-inappropriate behavior | Name the before/after distinction and migration diagnostic; require professor review |
| I — replace infrastructure | Replace Scala/Argon/compiler-global machinery with owned Python compiler services | Preserve the responsibility and necessary invariants, without porting the old mechanism literally |
| B — reference-only backend | Retain old vendor/backend code as evidence; a literal port is outside the proposed first backend scope | Route its language responsibilities to another family; list the excluded implementation and review condition |

Combined codes are intentional. A Chisel memory emitter is B as an emitter, P for memory behavior evidenced by it, and I for the physical mapping responsibility. Backend code cannot become B if that would silently erase a language capability.

Stage IDs are the shared vertical slices in [[04 - Python Implementation Roadmap]], not a second sequence defined here.

| Stage | Shared milestone | Coverage responsibility here |
|---|---|---|
| S0 | Reproducible contract and package | Typed schemas, source/builder acquisition, owned verifier and provenance |
| S1 | First complete kernel path | Fixed/Int, ports, SRAM/DRAM/views, transfers, loops, lazy branches and helpers |
| S2 | Complete reduction families | Scalar/memory reduce/fold, seeds/identity/tails and contribution effects |
| S3 | Full numeric profiles | Generic fixed/float, aggregates/packing, math/RNG contracts and exact ingress |
| S4 | Stateful local control | FIFO/LIFO, line/merge buffers, register files, masks, reset/lifetime and FSM |
| S5 | Communicating tasks | Bounded tasks, locks, environments, forever/stop/drain, fields/records and components |
| S6 | Hardware implementation planning | Storage/banks/ports/versions, legal overlap, protocol routes, ABI and constraints |
| S7 | First HLS path | One pinned vendor/profile and validated first composed kernel family |
| S8 | Full HLS family expansion | Per-family numeric/state/protocol/transfer/ABI refinements and component integration |
| S9 | Optimization and DSE | Legal search, calibrated models, caching, reports and attributed improvements |

Stages express dependencies, not a calendar or resource estimate. Later contracts are designed before implementation; S6/S7 can proceed for checked S1 programs while S2–S5 expand the language. Every family has a gate `Gxx` below. Passing a reference gate does not pass its hardware gate. A feature is represented, checked, reference-executed, lowered, vendor-tested, or device-tested only when evidence for that specific level exists. Keep these fields separate in later support reports.

## F01 — Capture, binding, helpers, and compiler objects

**Disposition: P/I/R.** Preserve reusable kernels, typed helper regions, lexical binders, source naming, and specialization; replace virtualization, Scala shadowing aliases, Forge annotations, mutable compiler globals, and staged Python operator execution. The original virtualization distinguishes constant branch choice from staged branch regions and rejects ordinary `return`/`while`/`do while`: `spatial@e7a8f2f:src/spatial/lang/api/SpatialVirtualization.scala:93-116`. That does not require Python to reproduce its macro implementation or forbid typed helper returns.

**Destination and representation.** Use R004's immutable SourceUnit/CaptureBundle, explicit FrozenMeta environment, typed surface tree, stable symbol/resource IDs, and region binders. Capture raw file/cell text without executing decorators, annotations, defaults, or kernel bodies. Bind all Meta formals before interpreting port annotations; allow helper `return` only as a region result. Host generation produces finite source or builder graphs outside captured code. Nested helpers can capture explicit DSL symbols, not arbitrary live Python closures. Initially require an acyclic helper/component call graph; host recursion may generate a finite checked graph.

**Stage and lowering.** S0 acquisition/freeze/check; S1 reusable helpers/components; S2–S3 typed library specialization. Both surfaces feed one unchecked model and the same semantic checks. Canonical schemas replace runtime Scala type reflection and implicit casts. Names and source origins survive normalization; physical IDs are distinct from user-visible names.

**G01.** Matched file/cell/generated-source/builder programs yield equivalent checked meaning. Undefined captured decorators/annotations are never invoked. Verify meta-formal ordering, shadowing, escaped binders, helper recursion rejection, generated provenance, and unattached builder consuming expressions rejected at freeze. Syntax acceptance alone is insufficient. Detailed repair examples are in R004.

## F02 — Numeric types, exact literals, math, and randomness

**Disposition: P/R.** Preserve arbitrary-width signed/unsigned fixed formats, floating descriptors, Bool, casts, bit operations, mathematical capabilities, and explicit saturation/stochastic variants. Revise inconsistent zero division, shifts, negative modulo, unsafe host ingress, accidental float precision, and unconstrained fusion. Original Num combines Order/Arith/Bits and exposes transcendental and conversion methods: `spatial@e7a8f2f:argon/src/argon/lang/types/Num.scala:8-50`. This is broader than Int32 or the introductory multiplication.

**Destination and representation.** R002's proposed normalized bit patterns, exact rationals/token-backed expression trees, declared rounding/overflow, explicit conversion versus reinterpretation, arithmetic status, and guarded fault nodes. Int is signed 32-bit data; meta sizes use separate unbounded integers. Represent named approximation profiles and RNG resources/consumption order. A not-yet-adopted transcendental or stochastic profile remains a typed operation with a precise profile diagnostic, not a host `math` substitution or invisible deletion.

**Stage and lowering.** S1 core Int/Bool; S3 full fixed/float/cast/bit/math/RNG contracts; S6 capability planning and S8 target arithmetic validation. Normalize at every declared operation, including emitted hardware helpers; vendor assignment rounding alone is insufficient. Keep two-rounding `a*b+c` distinct from explicit FMA and keep ordered folds distinct from reduction trees.

**G02.** Exact ingress, overflow, negative quotient/modulo, wide formats, inactive zero division, all shift boundaries, float special/subnormal/tie cases, conversion/packing round trips, and FMA counterexamples. Use independent integer/rational or standard-format oracles, then vendor/RTL cases per selected profile. An RNG gate additionally fixes algorithm/version, seed, stream identity, consumption trace, and redraw behavior under stalls. R002 supplies detailed candidate rules and its limited arithmetic probes.

## F03 — Vectors, records, tuples, packing, selectors, and shuffle

**Disposition: P/R.** Preserve finite vectors, record/tuple field typing, elementwise capabilities, bit slicing/concatenation/popcount, mux/priority/one-hot selection, and compress/shuffle operations. Original Vec maps/zips elementwise, reduces via ReduceTree, specifies index zero as the least significant word, and returns element zero for a nonconstant `I32` index: `spatial@e7a8f2f:argon/src/argon/lang/Vec.scala:11-63`. Struct exposes ordered typed fields and fieldwise equality: `spatial@e7a8f2f:argon/src/argon/lang/Struct.scala:7-24`.

**Destination and representation.** Owned aggregate type descriptors with fixed extent, ordered named fields, packed-bit layout, typed extraction/construction, and explicit element capability checks. Proposed runtime vector indexing is a checked dynamic select; never silently substitute index zero. Preserve low-word-first bit indexing while specifying byte serialization separately through the host/device ABI. Treat records as value aggregates here; independently consumed stream fields belong to F09. A pure `select` chooses already computed values; an effectful branch has regions and guards. One-hot selection requires at most one active selector plus a declared no-selection default or fault; priority selection defines lowest-position precedence and its empty case explicitly.

**Stage and lowering.** S3 aggregate reference operations; S6 vector lane/packing plan; S8 selected ABI validation. Distinguish ShuffleCompress's value/valid pairs from arbitrary vector indexing and from queue arbitration. Lane ordering and inactive lane bits/effects must be specified before vectorization.

**G03.** Pack/unpack nested records with mixed widths and signed zeros/NaNs, vector extent mismatch, dynamic index bounds, empty/single/odd vector reduction, conflicting/absent selector cases, and stable compress order/validity. Reject effectful pure selectors with R004's repair to guarded regions. Confirm ABI byte order independently from low-bit indexing.

## F04 — Registers, addressable storage, views, LUTs, shifts, and windows

**Disposition: P/R/I.** Preserve Reg, SRAM, rank-N storage, RegFile, LUT/FileLUT, LineBuffer, memory dimensions, conditional dense/sparse views, resets, and enabled accesses. Replace banked physical access nodes as semantic storage identities; revise uninitialized/OOB fallback and silent conflict-dropping policies. Dense aliases carry conditional backing choices and ranges; sparse aliases carry address storage, sizes, and origins: `spatial@e7a8f2f:src/spatial/node/HierarchyMemory.scala:48-97`. A view must not be treated as a new independent allocation.

**Destination and representation.** R003's stable backing identity, extent, lifetime, capability, view coordinate map, per-cell initialization and guarded effects. Reg reset value is separate from reduction identity. LUT is immutable typed content; a file LUT is a content-hashed acquired dependency with explicit parser/format, not a file read hidden inside capture. RegFile shift nodes include axis, addressed plane, scalar/vector values and guards (`spatial@e7a8f2f:src/spatial/node/RegFile.scala:50-105`). LineBuffer has enqueue/read and stride parameters (`spatial@e7a8f2f:src/spatial/lang/LineBuffer.scala:16-38`), so it requires a circular/window state transition with row/column origins rather than an ordinary SRAM alias.

**Stage and lowering.** S1 Reg/SRAM/views/initialization; S3 typed rank-N/LUT contents; S4 shifts/windows; S6 bank/duplicate/buffer/resource plan and S8 realization. R008 proposes zero-default RegFile reset images, snapshot shifts inserting active inputs in reverse chronological order into increasing coordinates, and explicit newest-first LineBuffer frame publication with initialization/lease tracking. These candidate policies distinguish RegFile from uninitialized SRAM/window history and physical reuse from logical versions. Preserve logical state while proving any physical duplication, versioning, or buffering refinement. Hardware mapping may serialize legal accesses; it may not erase a write through `conflictable`.

**G04.** Overlapping/conditional aliases, rank and dimension mismatch, zero-trip/branch initialization, active and inactive bounds faults, reset values, shift directions and multi-lane ordering, circular wrap/stride/window warmup, immutable LUT verification and missing/changed dependencies. Compare explicit small state transitions to the proposed contract, then banked realization. The legacy LUT nodes distinguish embedded elements from file path allocations: `spatial@e7a8f2f:src/spatial/node/LUT.scala:10-34`.

## F05 — Domains, controllers, FSMs, forever, and termination

**Disposition: P/R/I.** Preserve Accel, Pipe, Sequential, Foreach, Parallel, Stream, Named, explicit finite and forever domains, counter chains, FSMs, stop requests, and schedule directives. Original nodes distinguish domain start/end/step/par, ForeverNew, enabled pipes/loops, and FSM predicate/action/next regions: `spatial@e7a8f2f:src/spatial/node/Control.scala:9-54`, `spatial@e7a8f2f:src/spatial/node/Control.scala:103-117`. FSM state can be any Bits type, not merely an integer counter; its API separately captures predicate/action/next lambdas (`spatial@e7a8f2f:src/spatial/lang/control/FSM.scala:8-23`).

**Destination and representation.** Structured regions with lexical index/state binders, domain descriptors, lane validity, explicit enables, schedule requests, and task/termination metadata. Separate ordered statements, independent fork/join, pipelined iteration overlap, and blocking communication. Model forever as an unbounded activated task with external completion/stop/cancellation protocol, not a giant finite range. Proposed FSM order is test current state, execute action if enabled, then evaluate/commit next state; retain effect dependencies across these regions. R008 supplies proposed stop observation, draining and restart transitions; `haltIfStarved` must be translated into an explicit adopted policy rather than a simulator `break` convenience. Its candidate FSM restricts Test/Next to pure/read-only regions, with all consuming/mutating effects in resumable Action.

**Stage and lowering.** S1 ordered finite/runtime controllers and lanes; S4 FSM; S5 forever/concurrent activation and termination; S6 legal overlap and S8 validation. R009 proposes ordered loops, process networks, or explicit protocol machines according to checked obligations. A schedule preference cannot change values, contribution grouping, or consume counts. Ordinary runtime `while` is an explicit unsupported source form initially, with repair to an FSM; supporting FSM accounts for the original capability.

**G05.** Nested/runtime/empty domains, nonpositive parallel factors and zero steps, signed-step boundaries, nondivisible tails with inactive traps/effects, record-valued FSM state, action-to-next dependencies, fork/join completion, waiting versus starvation/completion, stop with in-flight work, restart/reset, and forever under a recorded environment. A timeout is not a termination or liveness proof.

## F06 — Scalar and memory reductions, folds, and accumulators

**Disposition: P/R/I.** Preserve contribution regions, scalar and elementwise memory destinations, explicit accumulator state, identities, fold seeds, and specialized accumulators. Revise schedule-dependent regrouping of a nonassociative combine and accidental FMA changes. Original OpReduce separately stores map/load/combine/store, identity and fold fields; OpMemReduce has separate map and reduction domains and a fold flag: `spatial@e7a8f2f:src/spatial/node/Control.scala:57-100`. Memory reduction's DSL construction separately captures contribution memory, result load, accumulator load, combine and store (`spatial@e7a8f2f:src/spatial/lang/control/MemReduceClass.scala:34-85`).

**Destination and representation.** R002's distinct ordered fold, lawful reduction, and explicit fixed tree; typed contribution and combine regions with captured resource identities, map/reduction domains, identity/seed/reset distinction, empty/disabled behavior, and exactly-once effects. A memory mapper result must outlive its element reads and cannot escape or alias an accumulator unsafely. Reject storage/RNG/consuming/external effects in a combine; arithmetic language faults remain represented and ordered by its fold/tree. Contribution consumes remain legal and ordered as specified. An identity-free lawful reduction requires nonemptiness or preserves its empty-domain fault.

**Stage and lowering.** S2 full scalar/memory fold/reduce and alias checks, with consuming-contribution tests dependent on S4; S6 legal trees/accumulator plan and S8 realization. Hardware accumulator replacement must preserve first-update, reset, disable and rounding points, not just the final algebraic expression.

**G06.** Identity versus old register versus seed, static/dynamic empty domains, disabled controller/all-invalid group, ordered subtraction/floating/saturating counterexamples, partial tails, irregular aliasing, memory mapper lifetime, FIFO contribution counts, and explicit FMA first/update behavior. Validate grouping and contribution trace separately. R002 derives original disagreements rather than promising compatibility with every original Fold schedule.

## F07 — Dense, sparse, gather/scatter, allocation, and addresses

**Disposition: P/R/I.** Preserve DRAM load/store, dense tile views, sparse address views, gather/scatter, dynamic accelerator allocation/deallocation/status, address access, masked tails and alignment requests. Original DenseTransfer records load/store, forceAlign and enables; SparseTransfer records gather/scatter and an address-backed DRAM view (`spatial@e7a8f2f:src/spatial/node/DenseTransfer.scala:34-63`, `spatial@e7a8f2f:src/spatial/node/SparseTransfer.scala:27-44`). DRAMAccelNew, allocation, deallocation and address nodes exist independently of host allocation (`spatial@e7a8f2f:src/spatial/node/DRAM.scala:11-31`).

**Destination and representation.** Typed transfer operations reference source/destination backing identities, coordinate mappings, logical length, enables, format, alignment and completion. Retain read and write effects even when an old node reports only destination writes. R008 proposes row-major dense array transfers with preflight address/type/initialization checks, a complete source snapshot, and ordered destination commits; overlapping views use that snapshot. Ordered scatter resolves repeated addresses by declared logical lane/iteration order. Concurrent scatter requires proven disjointness or an explicitly supported collision/atomic policy. Neither unordered last-writer accidents nor automatic reductions are acceptable. A target lacking the required snapshot/order route reports a capability rejection and may suggest explicit source staging; it cannot silently adopt forward-copy behavior. Stream-backed transfers have captured-prefix/fault rules instead of preflight over unknown future tokens.

Dynamic device memory uses a region/session-owned allocation handle and explicit valid/allocated state, extent, generation and failure policy. Address exposes a target-address capability, not a usable host pointer or evidence of alias disjointness. Allocator limits and supported allocation patterns are target capabilities. Deallocation invalidates views; delayed transfers retain ownership until completion.

**Stage and lowering.** S1 dense fixed tiles and logical views; S5 full sparse/repeated-address/async allocation-ownership semantics; S6 transfer plan and S8 DMA/allocator validation. Derive burst padding physically without enlarging legal source indices. Gather/scatter need independent capability gates, not the assumption that dense AXI support implies sparse support.

**G07.** Odd and zero lengths, offset/stride/unaligned tiles, disabled transfers, repeated scatter addresses, overlapping copies, aliasing through sparse address memory, allocation failure/use-after-free/reallocation generation, transfer completion versus host readback, and faults after partial commits. RTL gates check commands/data/acks under stalls and compare the same logical transfer contract.

## F08 — FIFO, LIFO, FIFO registers, priority, and merge buffers

**Disposition: P/R/I.** Preserve queue/stack order, consuming versus observing accesses, occupancy thresholds, vector/banked access, FIFOReg, multi-queue priority/round-robin, and merge-way control. Revise elastic simulation versus bounded hardware ambiguity and implicit consuming expressions. Original priorityDeq constructs enabled FIFO consuming nodes and a priority mux, with nonempty gating partly deferred to codegen; roundRobinDeq explicitly derives priorities from its `iter` argument (`spatial@e7a8f2f:src/spatial/lang/api/PriorityDeqAPI.scala:10-21`, `spatial@e7a8f2f:src/spatial/lang/api/PriorityDeqAPI.scala:55-104`). This is not evidence for an implicit persistent rotating pointer.

**Destination and representation.** Queue/stack resource state, depth, initialization/reset, ordered enqueue/dequeue/peek/status effects, lane sequence and arbitration operation IDs. R003 distinguishes an ordered diagnostic reference profile from blocking bounded protocols; full concurrent operation must use a bounded channel contract, not the unbounded Scala collection. Define first eligible nonempty queue for priority, explicit rotation state/input for round-robin, exactly one consume, and separate unavailable/wait/closed outcomes. Status reads depend on mutations and cannot be CSE'd across them.

MergeBuffer is a separate multiway resource with `enq(way)`, per-way bounds, init and consuming dequeue (`spatial@e7a8f2f:src/spatial/node/MergeBuffer.scala:8-15`). R008 proposes typed sorted runs with explicit frame/token counts, lowest-way precedence on equal keys, readiness from all nonexhausted heads, and a private vector packer that commits scalar consumes before atomic vector publication. Comparator, reset/init, capacity, close/mismatch and alternate concatenation mode remain explicit descriptors. Preserve that proposed capability, subject to adoption and trace validation; it cannot be reduced to an ordinary FIFO solely because both dequeue.

**Stage and lowering.** S4 ordered queues/vector/arbitration/merge; S5 bounded task-channel use; S6 storage/arbiter plan and S8 implementation evidence. FIFOReg retains consuming availability semantics despite its scalar storage shape.

**G08.** Under/overflow, full/empty/almost thresholds, vector enqueue/dequeue masks/order, same-step producer/consumer collisions, one-token capacity, guard selection, q=[0,5] RHS-before-target assignment discriminator, round-robin explicit rotation, all-empty/no-eligible, fairness assumptions, merge equal keys and bounded way exhaustion. Protocol/RTL gates compare observable traces and state transitions; a single deterministic simulation schedule does not prove all legal interleavings.

## F09 — External streams, stream fields, frames, and buses

**Disposition: P/R/I.** Preserve StreamIn/Out, StreamStruct, Frame transfer, pins and bus descriptors, file/EOF test inputs, frame markers and structured external payloads. Original FieldDeq is per-field and enabled; its source explicitly questions missing mutation effects (`spatial@e7a8f2f:src/spatial/node/StreamStruct.scala:8-22`). Original FrameTransmit is a separate enabled load/store early blackbox (`spatial@e7a8f2f:src/spatial/node/FrameTransmit.scala:26-43`). Bus definitions include AXI-style metadata fields, file buses and a last-Bit EOF convention (`spatial@e7a8f2f:src/spatial/lang/Bus.scala:23-75`).

**Destination and representation.** Distinguish **RecordToken stream** (one atomic typed record consume/produce) from **StreamStruct endpoint bundle** (independent named field endpoints with separate availability, ownership and Consume/Produce effects). An adapter may join/split records only with a declared coherence contract. Never silently make a legacy per-field bundle atomic, or decompose an atomic token into independently advancing fields. Frame describes payload dimensions, marker rules, endpoint identity and transfer completion; byte packing, strobes/keep/last/id/destination/user are protocol/ABI fields with an explicit layout, not vendor-name assumptions.

The environment provides offered tokens, readiness, close/EOF and cancellation as recorded inputs. End-of-stream, waiting, starvation, malformed frame and normal completion are distinct states. FileBus is a reference adapter over a host-acquired stream trace; EOF marker conversion is explicit. Pin/AXI choices are target binding descriptors and cannot dictate a universal stream semantic type.

**Stage and lowering.** S5 semantic environment, field/record/Frame protocols; S6 bus/ABI plan and S8 integration. Use checked process/channel or protocol-machine plans under R009. R008 supplies proposed activation, captured-operand continuation, close/End and drain transitions; selected scheduled adapters still need valid/data stability and RTL evidence.

**G09.** Asymmetric field consumption, record coherence, arbitrary output backpressure, finite/closed versus temporarily empty inputs, malformed/missing/early last, marker/payload alignment, reset midway through a frame, blocked field bundles, EOF translation, and ABI packing. Test both token order and protocol stability against the environment assumptions, with source origins for each field/transfer fault.

## F10 — Locks, keyed ownership, and locked memories

**Disposition: P/R/I.** Preserve Lock, LockWithKeys, LockSRAM and LockDRAM as capabilities, not ordinary arrays or host mutexes. Original `lock(elements*)` records a keyed operation (`spatial@e7a8f2f:src/spatial/lang/LockMem.scala:167-181`); locked DRAM reads/writes can carry a lock, while two public store overloads literally throw an unimplemented exception (`spatial@e7a8f2f:src/spatial/lang/LockMem.scala:54-62`). Thus existence in the API is not proof of complete original transfer support.

**Destination and representation.** Lock resource identity, typed key set, request/ownership permit, guarded protected access, completion/release, and cancellation state. Track aliasing through locked and unlocked views. R008 proposes atomic acquisition of the deduplicated key set, canonical increasing order for nested acquisition, nonreentrant ownership, capacity faults, stateful round-robin admission, and release only after protected writes complete. A nontransferable permit is tied to owner/task, address domain and active generation; cancellation drains issued writes before cleanup/release. These are candidate redesigns, not inferred guarantees of the legacy attached descriptor. Unprotected accesses cannot bypass an adopted lock discipline silently.

**Stage and lowering.** S5 explicit transition model plus checker; S6 ownership/arbiter plan and S8 locked-memory integration. Represent unsupported original store capability as a proposed extension requiring its own transfer/ownership contract, never as preserved executed behavior. Select target route based on actual required lock primitives and legal adapters.

**G10.** Disjoint and overlapping key sets, duplicate keys, reverse key-order deadlock scenarios, ownership misuse/escape, guard-false requests, simultaneous contenders, alias bypass, cancellation after acquisition, release/drain on fault, bounded request storage and fairness under stated assumptions. An unconstrained Python lock or serialized example cannot validate the hardware protocol.

## F11 — Spatial components, foreign blackboxes, and manifests

**Disposition: P/R/I/B.** Preserve reusable primitive/controller components, parameters, typed interfaces, latency/II constraints, and foreign-module integration. Replace absolute-file-path configuration and implicit target assumptions with versioned manifests. Original primitive blackboxes assume clock/reset and no enable, while controller blackboxes specify valid/ready, downstream-ready/done and immediate Stream placement (`spatial@e7a8f2f:src/spatial/lang/Blackbox.scala:34-94`). These are distinct contracts, not one universal opaque call.

**Destination and representation.** A Spatial component body uses the same checked language and helper rules as F01. A foreign component is a manifest-backed operation with content hashes, parameter schema, ordered typed ports/packing, clock/reset, state/lifetime, activation, latency/acceptance rate, effect/resource summary, completion/fault protocol and reference transition model. A function-like pure component must prove/declare statelessness; a controller cannot be classified pure because its output is a record. GEMMBox is a compositional library/lowering convenience whose math and memory effects remain explicit.

**Stage and lowering.** S1 pure DSL components; S5 stateful component protocol; S6 manifests and S8 selected vendor adapter. Legacy Verilog wrapper emission is B; component integration responsibility is P/I. No missing operator/profile/protocol is solved by attaching an arbitrary C callback. A reference model has a trust boundary and independent conformance evidence.

**G11.** Parameter/type mismatch, layout and width errors, reset/stall/latency/II traces, pure versus stateful reuse, multiple component instances sharing or isolating state, effect summary soundness, output stability, cancellation and component faults. Require selected vendor legality and RTL traces in addition to reference model tests; manifests must identify the actual dependency version.

## F12 — Host arrays, tensors, files, ports, and invocation

**Disposition: P/R/I/B.** Preserve user ability to prepare rank-1 arrays/matrices/tensors, parse/write data, set/get scalar and memory ports, launch kernels, inspect outputs and test them. Replace staged Scala host IR, CLI virtualization and generated C++/Rogue/Tungsten host programs with ordinary Python workflow plus selected device adapters. CSV parsing and typed struct parsing are visible original facilities (`spatial@e7a8f2f:src/spatial/lang/api/FileIOAPI.scala:11-66`); their bugs or delimiter limitations are not mandatory Python compatibility.

**Destination and representation.** R007's typed buffer descriptors, alias/range validation, preparation/launch/completion/fault results, snapshot versus adopted zero-copy ownership, fresh versus explicit persistent sessions, artifact keys and external environment traces. Host Array.map/zip/filter/reduce/flatMap/mkString and Matrix/Tensor3–5 constructors migrate to ordinary Python utilities with explicitly selected Spatial numeric conversion when required. Host Python evaluation remains separate from captured accelerator IR; a host reference may use an independent model. CSV/binary/file-LUT parsers fix delimiter, shape, exact numeric ingress, encoding/byte order and errors. Numpy placeholders become optional real adapters, not semantic dependence on NumPy or string evaluation.

**Stage and lowering.** S0 package/artifact contract; S1 host preparation/invocation and ports; S3 exact aggregate/file conversion; S5 persistent/external sessions; S7–S8 ABI/runtime adapters. ArgIn, ArgOut and HostIO preserve direction/visibility through manifest ports, rather than retain Reg syntax or board register numbers. File reads happen in authorized host preparation/acquisition with dependency hashes, never incidentally during capture.

**G12.** Shape/format/stride/alias errors, conversion exactness, file parse failures, buffer lifetime, input snapshots and output commit/incomplete markers, fresh/reset/repeated launches, concurrent ownership, persistent-state schema mismatch, cancellation and recorded environment replay. Separate semantic/build/run artifact identities and functional correctness from performance reports, as R007 proposes.

## F13 — Standard libraries and scoped metaprogramming

**Disposition: P/R/I.** Preserve BLAS Dot/Axpy/Gemm/Gemv/Ger/Scal/Axpby, on-chip linear algebra, ML dot/sum/dense/MLP, low-precision quantization/dequantization, sort/scan/filter, lane helpers and scoped enables. These are templates over core language capabilities, not handwritten compiler cases for particular applications. Source/library dependency evidence is collected in [[00 - Standard Library Index]]. Scan's mask-producing filter and compacted filter-plus-count are different operations (`spatial@e7a8f2f:src/spatial/lib/Scan.scala:6-38`). Sort's fixed-256 implementation uses MergeBuffer init and per-way bounds (`spatial@e7a8f2f:src/spatial/lib/Sort.scala:16-38`); Python need not present that fixed implementation as a universal length guarantee.

**Destination and representation.** Typed composable source/builder library definitions with explicit dimensions, element types, algebra/approximation profiles, layout, alias restrictions, tiles and tail policy. Scalar/vector/matrix coefficient variants preserve distinct signatures. HostML becomes ordinary independent reference helpers. Low-precision libraries must expose scale/zero-point/range/rounding and accumulation width; Num does not grant associative arithmetic automatically. Generalizing legacy fixed sizes or changing unused/ambiguous parameters is R with a migration note and reference cases.

Scoped `withEns` currently installs a compiler-global rewrite and mutates an enable buffer (`spatial@e7a8f2f:src/spatial/lib/MetaProgramming.scala:14-42`). Replace this with lexical guard composition on the represented region, including consuming effects, so nesting is deterministic and cannot leak to unrelated modules. ForeachWithLane/MReduce/FIFOs helpers expand finite typed graphs with stable lane/resource IDs, not mutable global callbacks.

**Stage and lowering.** S1 composed helpers, S2–S3 arithmetic/linear algebra templates, S4–S5 scan/sort/advanced templates, and S9 tile/parallel tuning; each depends on its constituent family gates. Compile library definitions through the same checker/transforms/backends as user kernels. No special whole-program recognition.

**G13.** Generic dimensions including tails/zero/odd sizes, alpha/beta and coefficient variants, alias restrictions, numeric quantization boundary cases, stable sort ties, scan count/output prefix versus untouched tail, nested enables and helper specialization. Compare independent host mathematical references plus bit/trace obligations of the selected numeric/protocol profile; an approximate ML score is not bit-exact arithmetic validation.

## F14 — Effects, diagnostics, debug, and reference execution

**Disposition: P/R/I.** Preserve readable diagnostics, assertions, printing, breakpoints/exits, testbench facilities, source naming and observable state/faults; replace Argon anti-dependency scheduling and deferred issue globals. Original debug operations include guarded print/assert/exit/breakpoint (`spatial@e7a8f2f:argon/src/argon/lang/api/DebuggingAPI.scala:7-34`); Issue fails if unresolved by the following pass (`spatial@e7a8f2f:argon/src/argon/Issue.scala:5-19`). The responsibility survives without reproducing that pass-count rule.

**Destination and representation.** R003 ordered region effects and active faults, alias-aware Read/Write/ObserveStatus/Consume/Produce/Allocate/Reset/Shift/RNG effects, plus Debug/Stop/External effects. R004 structured phase/code/primary span/related origins/repair diagnostics. Reference execution uses owned typed values and explicit resource state, never executes captured Python bodies or trusts host floats. Accelerator Text/debug formatting is an explicit typed operation/trace event with a declared formatting profile; host text, print, files and testbench use ordinary Python. A hardware profile may omit console printing or interactive suspension only as an explicit diagnostic/capability policy or source-approved debug-elision attribute. It cannot silently erase assertions, exit/stop, or stateful text-dependent control. Breakpoint is an observable suspension/debug request, exit a termination request subject to F05 drain rules. `sleep` is a timing request, not host wall-clock delay or the odd legacy print-based implementation.

**Stage and lowering.** S0 diagnostics/schema; S1 functional reference/trace; S4–S5 protocol execution; S6/S9 invariant and optimization diagnostics; S7–S8 hardware fault/debug mapping. Original Scalagen and executor remain distinct evidence implementations. Report invariant failures as compiler faults, not user syntax repairs. Partial effects before an active fault remain committed; outputs are marked incomplete as R007 proposes.

**G14.** Matched source/builder uninitialized, incompatible-type, unsupported-control, stateful-branch and escaped-scope diagnostics; ordinary RHS-before-target and augmented target-once order; guard-false assertions/consumes, status ordering, alias CSE/DCE counterexamples, stop/debug origin mapping, and transformed/generated provenance. Check message/code/phase/span/related location/repair, not only that an exception occurs. Independent reference traces must catch emitter/checker bugs rather than duplicate their implementation.

## F15 — Passes, rewrites, analysis state, and invariants

**Disposition: I/P/R.** Replace staging-time rewrite registries, flows, macro-generated mirrors, mutable metadata caches, Scala compiler driver, transformers and codegen skeletons. Preserve their responsibilities: checked boundaries, legal scope/substitution, DCE, conditional normalization, alias handling, controller formation, unrolling, accumulation specialization, cleanup and reporting. Original passes are evidence for obligations, not a required Python pass order.

**Destination and representation.** Versioned module schemas and explicit pass inputs/outputs with ownership, analysis invalidation, provenance transfer and deterministic iteration. Separate semantic properties (types, resource identity, branch guard, tree shape, program order) from derived analyses (bounds, affine residuals, critical paths) and target choices (banks, retiming, ports). Pipeline stages validate their own invariants. Cache keys include the relevant contract/module/profile versions. User requests, inferred facts, expected estimates and proven constraints have distinct types.

**Stage and lowering.** S0–S1 normalize/check/reference boundaries and helper/alias normalization; S6 legality and physical transforms; S9 broader optimization/search. A rewrite requires a stated precondition and semantic/trace preservation obligation. Never move untaken faulting/consuming work out of a branch or infer safe FMA from a historical `CanFuseFMA` flag alone. Transformations on communicating control retain task activation/capacity and cannot assume serial equivalence.

**G15.** Before/after independent execution for bounded cases, adversarial alias/fault/guard/lifetime tests, stale-analysis invalidation, provenance and stable identity preservation, substitution/dominance errors, idempotent normal forms where promised, and explicit legality certificates for schedule/resource changes. Golden textual IR alone does not prove semantic equivalence. R006/R017 propose compiler-owned immutable checked records, revision-scoped analyses and verified pass transactions; optional framework views are derived. That framework/pipeline recommendation remains unadopted; generic framework verification is not the Spatial legality gate.

## F16 — Dependence, polyhedral reasoning, banking, retiming, and physical storage

**Disposition: P/I/R/B.** Preserve proof of legal simultaneous accesses, storage versions/banks/ports, buffer depth, dependency distance, achieved scheduling constraints and latency alignment. Replace Scala affine algebra/ISL process bindings and Chisel-specific resource selection with owned Python analyses and a checked implementation plan. Original AccessMatrix describes affine addresses and asks overlap/intersection questions (`spatial@e7a8f2f:src/spatial/metadata/access/AffineData.scala:24-48`); BankingStrategy solves grouped reads/writes under directives and buffer depth (`spatial@e7a8f2f:src/spatial/traversal/banking/BankingStrategy.scala:7-27`). Neither proves every source index is affine.

**Destination and representation.** Exact integer affine constraints with declared bounded domains and conservative nonaffine/unknown results; optional solver adapter is a tool, not semantic authority. Canonical logical accesses remain separate from bank/lane/offset/port mappings, duplicates, storage resources and n-buffer versions. Distinguish same-operation collisions, overlapping iterations, and communicating resource conflicts. Retiming carries data/valid/guard alignment and latency constraints; functional operation order is not a cycle number. DelayLine/user latency directives need explicit timing semantics/profile and cannot silently affect functional traces.

**Stage and lowering.** S1 bounds/alias facts; S6 dependence, bank/version/port plan and unroll/pipe/retime legality; S7–S8 RTL validation; S9 improved mappings. Begin with conservative legal serialization/mappings where contract permits; that is an implementation choice, not inability to represent advanced constructs. Unsafe `conflictable`/buffer-ignore flags require proof, explicit relaxed contract, or rejection; never drop competing writes to satisfy a bank count.

**G16.** Affine/nonaffine/conditional alias access, negative/stride/modulo indices, bank conflicts and per-lane masks, physical duplicate coherence, n-buffer wrap, read/write collision profiles, transformed tails, false-path guards and retimed data/valid matching. Compare optimized versus logical semantics plus cycle/protocol checks; solver unknown is not proof of disjointness. Later memory/scheduling HLS studies must supply vendor-specific refinement evidence.

## F17 — Parameters, bounds, models, DSE, and reports

**Disposition: P/R/I/B.** Preserve finite tunable tile/par/pipeline domains, restrictions, deterministic specialization, target capability/resource descriptions and useful resource/latency/memory reports. Replace Scala generated search executors, global param sets, target CSV parsing and old fitted coefficients. HardwareTarget separately describes burst width, capacities, model factories and memory resources (`spatial@e7a8f2f:src/spatial/targets/HardwareTarget.scala:7-48`); DSE modes include disabled/heuristic/bruteforce/HyperMapper/experiment (`spatial@e7a8f2f:src/spatial/dse/DSEMode.scala:3-10`). Porting every search integration is not language coverage.

**Destination and representation.** Typed Meta/tuning parameters with finite domains, restriction expressions, specialization records, legality outcomes and canonical selected values. Separate exact proven bounds from user assumptions and model expectations; a claimed upper bound must be validated, proved or made an explicit invocation precondition, not treated as truth because metadata says so. Models carry schema, target/tool/device/version, training/calibration data, units, uncertainty and evidence class. Reports distinguish estimates, vendor synthesis results and physical implementation/device measurements.

**Stage and lowering.** S0 explicit meta values/domains; S6 legality, constraint and report schemas; S9 calibrated models, candidate search and selected external integrations. DSE may choose only among semantically legal implementation variants. Numeric rounding/grouping, source-visible channel capacity, or fault behavior cannot become silent tuning knobs. Old target constants/model CSVs are B as calibration data, retained for provenance and comparison rather than labeled accurate for HLS.

**G17.** Exhaust a tiny finite search domain and check restrictions/duplicates/cache identities, illegal versus failed-tool versus feasible points, parameter ordering and stable selected artifacts, proven/assumed/estimated bound distinctions, reproducible calibration input splits, unit consistency and attributable model error. Validate achieved II/resources/clock separately from functional equivalence; report provenance for every measured result. Resource/latency goals require explicit hard/soft classification.

## F18 — Backend boundaries, Fringe, packaging, and target exclusions

**Disposition: B/I/P/R.** The proposal does not literally port Chiselgen/Fringe, Scalagen/JVM packaging, Cppgen, Pirgen/Plasticine, Rogue/PyRogue, Tungsten, every board resource tree, or every BigIP target implementation. Their source-defined language responsibilities remain assigned to F02–F17. Pirgen declares a Scala PIR output and accel backend (`spatial@e7a8f2f:src/spatial/codegen/pirgen/PIRCodegen.scala:17-26`); Fringe SpatialIP string-selects board/simulator shells and installs global target IO (`spatial@e7a8f2f:fringe/src/fringe/SpatialIP.scala:18-39`). These are target mechanisms, not a reason to remove locks or external streams from Spatial.

**Destination and representation.** R009 proposes a checked Python implementation plan, HLS C++ emission and selected integration manifests. R007 proposes ordinary Python host adapters and canonical artifacts. The replacement boundary fixes kernel/argument ABI, exact packing, address/alias/transfer rules, activation/reset, channel/arbiter protocols, completion/fault/debug records, external component dependencies and hard/soft constraints before handing work to vendor tools. Graph/tree/HTML visualizations become reports over canonical objects; useful debugging information survives without the old output formats.

**Stage and lowering.** S1 owned reference runtime; S6 implementation graph/manifests; S7 first reviewed vendor/device path; S8 family expansion; S9 measured reports/optimization. No backend is implemented by this note. A selected HLS route must implement required semantics or return a capability diagnostic naming the missing contract and supported repair/profile. For advanced semantics it may require explicit protocol hardware/component integration; merely emitting vendor pragmas is not semantic compilation.

**G18.** Artifact reproducibility and dependency/tool lock, semantic versus implementation graph invariant checks, emitter compilation/structural checks, independent C/RTL/trace tests, achieved schedule/resource reports, physical timing/board evidence when claimed, and host ABI/fault/cancellation integration. Each level has its own status. Historical Rust or Scala executions cannot be relabeled Python/HLS evidence.

## Scope choices requiring professor review

| Proposed choice | What remains in the language | Review/reversal condition |
|---|---|---|
| One selected HLS vendor/device profile first; no literal Chisel/Fringe backend port | Exact arithmetic, checked memory/state, bounded protocols, external component/ABI contracts | Required protocols/operators lack a legal HLS/component route, or measured quality fails explicit workloads |
| No initial Plasticine/PIR, Tungsten or SLAC Rogue runtime port | Logical parallelism, stream/control capabilities and ordinary Python host workflow | A required research deployment targets those systems; add a backend/profile rather than weaken shared semantics |
| Do not copy old board resource trees/Makefiles/register addresses | Target descriptors, explicit ABI, launch/reset/completion/faults | Deployment requires a specific legacy board; adopt a separately checked adapter |
| Replace staged Scala host collections/files with ordinary Python utilities | Data preparation, rank/layout/type conversion, file input, launch/readback and reproducible references | A staged-host capability truly requires accelerator or device execution; model that operation explicitly |
| Revise runtime vector-index fallback, OOB fallback, silent dropped-write hints and legacy numeric disagreements | Dynamic selection, guarded faults, safe storage and declared arithmetic operations | A named compatibility profile is required; version and test it, never make it an accidental default |
| Distinguish atomic record tokens from independent StreamStruct fields | Both aggregate payloads and field endpoint bundles | Professor chooses a simplified public contract; document an explicit breaking migration/coherence adapter |
| Delay recursive DSL calls and unrestricted runtime `while`; retain finite host generation and typed FSM | Finite compositional helpers, explicit state-machine/forever control | A concrete workload needs recursion or richer dynamic control; define bounds/state/termination and target gates first |
| Replace fixed library tile sizes and compiler-global enable rewrites | Generic typed library templates, scoped guard and lane composition | Require exact legacy compatibility; freeze a named template/profile and validate its dimensions/parameters |

These are proposed infrastructure/API changes and implementation ordering. They are not approved deletions of language semantics. A later release scope report must list each represented family, adopted contract, implementation level and profile; it must not turn these reference-only backends into unexplained missing operations.

## Pinned source-family accounting

The following is the **exact 124-path baseline** inspected at the original SHA, grouped by primary family. Within each row, append every listed basename to its directory and `.scala`; nested names keep their directory. Each path appears once. A primary family is a research destination, not proof that all declarations in that file are already specified. Cross-family effects/types/ABI duties still apply.

| Directory and basenames | Primary destination | Paths |
|---|---|---:|
| `src/spatial/lang/`: Aliases, Box, package; `api/`: Implicits, SpatialVirtualization, StaticAPI, package; `control/`: SpatialModuleClass | F01; namespaces/macros/compiler services become owned schemas | 8 |
| `src/spatial/lang/api/`: MathAPI | F02; typed numeric capabilities/profiles | 1 |
| `src/spatial/lang/api/`: MuxAPI, ShuffleAPI; `src/spatial/node/`: Mux, Shuffle, LaneStatic | F03; selectors/value-valid lane operations | 5 |
| `src/spatial/lang/`: Reg, RegFile, SRAM, LUT, LineBuffer; `types/`: Mem; `src/spatial/node/`: Reg, RegFile, SRAM, LUT, LineBuffer, HierarchyMemory | F04; logical identities/views/reset/shift/window | 12 |
| `src/spatial/lang/`: Counter, CounterChain, Wildcard; `api/`: ControlAPI; `control/`: AccelClass, Control, CtrlOpt, FSM, ForeachClass, NamedClass, Parallel; `src/spatial/node/`: Control, HierarchyControl, Switch | F05; domains, guards, binders, activation, schedule and termination | 14 |
| `src/spatial/lang/control/`: ReduceClass, MemReduceClass; `src/spatial/node/`: Accumulator | F06; scalar/memory combine and storage state | 3 |
| `src/spatial/lang/`: DRAM; `api/`: TransferAPI; `src/spatial/node/`: DRAM, DenseTransfer, SparseTransfer, Fringe | F07; transfers/allocators with logical effects and target adapters | 6 |
| `src/spatial/lang/`: FIFO, LIFO, MergeBuffer; `api/`: PriorityDeqAPI; `src/spatial/node/`: FIFO, LIFO, MergeBuffer | F08; bounded state, consuming order, arbitration/merge | 7 |
| `src/spatial/lang/`: Bus, Frame, StreamIn, StreamOut, StreamStruct; `src/spatial/node/`: Frame, FrameTransmit, StreamIn, StreamOut, StreamStruct | F09; environment, fields/records/markers/protocol/ABI | 10 |
| `src/spatial/lang/`: LockMem; `src/spatial/node/`: LockMem | F10; keyed ownership/locked accesses | 2 |
| `src/spatial/lang/`: Blackbox; `src/spatial/node/`: Blackbox | F11; pure/stateful DSL components and foreign manifests | 2 |
| `src/spatial/lang/api/`: ArrayAPI, FileIOAPI, MiscAPI, TensorConstructorAPI; `host/`: Array, BinaryFile, CSVFile, Matrix, Tensor3, Tensor4, Tensor5, TensorData; `src/spatial/node/`: Array, FileIO | F12; ordinary host utilities/typed ingress/runtime | 14 |
| `src/spatial/lang/api/`: DebuggingAPI; `src/spatial/node/`: HierarchyAccess | F14; effect categories, diagnostics/debug | 2 |
| `src/spatial/node/`: Transient | F15; transient normalization, scope/metadata invalidation | 1 |
| `src/spatial/lang/`: Latency; `src/spatial/node/`: DelayLine, HierarchyUnrolled | F16; bank/lane/retime implementation responsibility | 3 |
| `src/spatial/lang/api/`: UserData | F17; assumed/proven bound distinction | 1 |
| **Subtotal: Spatial lang/node** | **58 language +33 node paths** | **91** |
| `argon/src/argon/lang/`: Aliases, Top, package, implicits; `api/`: Implicits, package | F01; type/namespace/implicit mechanism replacement | 6 |
| `argon/src/argon/lang/`: Bit, Fix, Flt; `types/`: Arith, Bits, CustomBitWidths, Num, Order | F02; exact descriptors and capability dispatch | 8 |
| `argon/src/argon/lang/`: Struct, Tup2, Vec; `api/`: BitsAPI, TuplesAPI | F03; typed aggregates and packing | 5 |
| `argon/src/argon/lang/`: Series | F05; range/view-domain representation | 1 |
| `argon/src/argon/lang/`: Text; `api/`: DebuggingAPI | F14; explicit formatting/debug events and host text boundary | 2 |
| `argon/src/argon/lang/`: Var, Void | F15; staged-variable/result representation and mutation checks | 2 |
| `src/spatial/lib/`: BLAS, HostML, LinearAlgebra, LowPrecision, ML, MetaProgramming, Scan, Sort, package | F13; typed templates and independent host references | 9 |
| **Subtotal: extensions** | **24 Argon language +9 library paths** | **33** |
| **Total baseline** | **Path/declaration accounting, not feature support** | **124** |

Additional pinned-source checks follow the 106 documents into `src/spatial/math/LinearAlgebra.scala`, `argon/src/argon/node/`, `src/spatial/metadata/`, traversal/transform/executor/report/codegen/targets/DSE, `emul/`, `poly/`, `models/`, and `fringe/`. Those families are substantive F02–F18 duties; the 124-path table is not a claim to inventory every repository file. FMA/RNG/math node variants are covered through R002 plus F02, rather than presumed absent because the core node directory lacks their names. The ledger maps all IR/pass/backend/runtime documents to their relevant family and its gates.

## Migration and closure protocol

Migrate by construct, then by vertical program, while preserving the distinction between source facts and an adopted Python contract. For each program record its original pin, used constructs and backend assumptions, selected numeric/state/protocol profile, host data/layout, expected values and observable effects, deliberate differences and repair, and achieved validation level. A guide links each Scala form to a proposed Python source and builder equivalent; it does not promise an automatic Scala translator or ordinary Python execution of captured kernels.

Use E1/E2/E3 to check the shared foundation, then add discriminators for every `G01`–`G18`: aggregate layouts/dynamic vectors, fixed/float edge cases, shifted windows, sparse collisions, identity/seed/lifetime, bounded producer-consumer traces, FSM stop/drain, independently consumed fields, merge ties, keyed ownership, external components, file/host aliasing, conservative analysis, DSE legality and target ABI. Libraries supply representative workloads after their constituent contracts are checked. Correct output on one introductory program cannot discharge a protocol, numeric or banking gate.

The coverage ledger is now a research crosswalk: 106 rows have explicit dispositions and substantive family destinations. **No row is a completed implementation claim.** Remaining closure requires professor review of R policies and backend scope choices, adoption of numeric/state/protocol contracts, architecture schema review, and execution evidence at the stage/profile actually claimed. In particular, R008 supplies proposed advanced lock/merge/stream/termination transitions; their adoption and executable conformance remain open. Vendor memory/scheduling/numeric refinements require later target evidence. All have representation obligations and concrete gates here rather than a generic pending folder.
