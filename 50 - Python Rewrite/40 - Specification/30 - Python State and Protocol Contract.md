---
type: spec
title: "Proposed Python Spatial state and protocol contract"
concept: python-state-effects-and-communication
scope: python-rewrite
source_files: []
source_notes:
  - "[[PY-R003 - Control Memory and Effects]]"
  - "[[PY-R008 - Advanced State and Communication Protocols]]"
decision_records:
  - "[[D-28]]"
hls_status: rework
depends_on:
  - "[[10 - Python Language Contract]]"
status: reviewed
adoption_status: proposed
implementation_status: not-implemented
---

## Execution model

This proposed contract condenses R003 and R008. Their transition rules and numbered discriminators are part of the review package. None is a claim of an implemented Python simulator or proven original-backend equivalence.

An ordered region has a declared evaluation/effect order. A communicating region contains tasks, resources, arbitration, and an external environment. Tasks retain activation identity, continuation, live values, and captured pending operands. Resources retain generation, semantic capacity, token/state order, endpoint ownership, close state, and arbitration policy. Request, grant, and commit are distinct protocol steps.

A blocked operation does not repeatedly evaluate its operands or mutate storage. Evaluate operands once at the declared point, then retain the request until it commits, is cancelled before issue, or faults. Simultaneity exists only through explicit batch/barrier rules. Each task preserves its internal order while the graph may admit several interleavings. A canonical fair reference task scheduler records one replayable witness. Default channel resource selection separately follows exact stateful round robin over stable endpoint IDs with one shared admission cursor and one atomic request per resource epoch; a general fair selector does not automatically preserve this policy. Correct hardware traces must belong to the allowed set under the same environment assumptions; they need not match that witness's unrelated event order.

Correctness also preserves termination, deadlock, and fair progress under those assumptions. A valid event prefix followed by an added permanent hardware stall is insufficient. Internal implementation steps may delay a source transition finitely, but cannot stutter forever where the source owes progress. Waiting indefinitely for an unconstrained external environment remains permitted. R009 gives the full refinement condition and the finite capacity-one producer/consumer discriminator.

## Logical memory, lifetime, and effects

Each allocation has backing identity, generation, extent, element type, initialization, capabilities, and lifetime. A view adds coordinates/extents while retaining its backing. Track reads, writes, observations, consumes, produces, allocation/free, ownership, random/environment access, faults, suspension, reset/cancellation, completion, and debug events. Guarded effects describe alternatives rather than eager execution.

Iteration scratch, outer-loop-carried state, task-activation state, invocation state, and explicit persistent-session state are separate lifetimes. Handles cannot be used after their owner/generation ends; retaining an invalid descriptor grants no access. Initialization is per logical cell; inactive accesses do not fault or initialize. SRAM begins uninitialized unless initialized explicitly. Reg and RegFile use their explicit reset image, or registered ZeroImage(T) for a bare declaration. Missing registered zero requires an explicit supported reset or a source diagnostic. Private typed-cell Index has exact zero; private MaskedVec uses all-invalid lanes and recursively registered zero payload, retaining guardedness across reads/writes. This admits neither a raw Bits operation nor a packed host/channel slot. The source blueprint owns the separate ValueStorage/Bits capability ledger; target support requires a proved finite range/layout or scoped rejection. The checked allocation stores the selected image; no arbitrary host constructor or unchecked tagged bit pattern supplies it. A read of an uninitialized active cell faults. Reallocation cannot make an old view valid again.

Ordered conflicting memory effects preserve order. Concurrent tasks require proven disjointness, explicit ownership, or an adopted arbitration/atomic protocol. A software scheduler's accidental total order is not a race-resolution policy. Unknown alias/dependence results cannot justify parallel issue.

## Resource transition summary

| Resource or controller | Proposed rule |
|---|---|
| Ordered FIFO/LIFO | Bounded enqueue/dequeue; active overflow/underflow faults. FIFO removes oldest; LIFO removes newest. Observation does not consume |
| FIFOReg | Capacity-one queue, initially/reset empty; stored reset bits do not seed a token. Read consumes, write produces; ordered full/empty faults, communicating full/empty waits |
| Communicating channel | Same bounded storage with suspend/resume and explicit close. Open-empty means wait, not end. Capacity and source-visible status are semantic |
| Vector queue/stack operations | Compact active lanes in increasing lane order and commit an atomic batch. Scalar removal order determines returned vector order. Explicit simultaneous batches read old state, may reuse slots freed by their own pops, and do not invent empty bypass |
| Priority and round-robin | Priority selects the first eligible nonempty candidate; caller-index rotation and stateful round-robin are different operations. Exactly one selected consume. Conditions are captured once; readiness is checked at grant. All captured conditions false raises NoEnabledCandidate before queue observation/wait registration; an enclosing disabled region evaluates none. This differs from an all-false vector mask |
| MergeBuffer | Typed sorted input runs with declared frame counts; select among all nonexhausted heads, ties by input-way order. Vector output consumes tokens into an explicit packer before atomic publication, allowing progress with capacity-one inputs |
| Published windows/buffers | Publication credits and immutable version leases are explicit; default two publication slots in R008. Physical storage reuse waits for lease release and cannot silently change semantic capacity |
| LineBuffer | R×C newest-first published view with S-row staging and explicit begin/fill/publish. Partial publication requires a fill policy; uninitialized history stays invalid |
| RegFile shifts | Snapshot the source region; apply the declared axis/plane and active input order. Do not let implementation write order overwrite later shift inputs |
| Keyed lock region | Atomically acquire a deduplicated key set, canonical ordering for nested acquisitions, nonreentrant ownership, bounded request storage. Permit is tied to task/generation; release waits for protected writes to complete |
| Generic FSM | Initialize, read-only/pure test, resumable effectful action, then read-only/pure next-state evaluation using post-action memory and old state. State may be any supported finite Bits aggregate |
| Record stream versus field bundle | A record token advances atomically. A StreamStruct bundle has independent field endpoints. Joining/splitting requires an explicit coherence adapter |
| Foreign component | Manifest fixes interface, effects/state, reset, timing/protocol assumptions, dependencies, and reference transition model. Missing models diagnose; no fabricated zero result |

[[PY-R018 - Protocol Policy Refinement]] supplies the 3 October proposed selection, initialization and disabled-boundary clarifications and their evidence. These remain subject to professor adoption.

R008 fixes remaining edge transitions: all-false masks, oversize atomic batches, merge exhaustion/mismatch, lock cleanup, shift direction, window warmup, frame closure, and environment fairness. Its A-series cases are required acceptance discriminators. These policies intentionally resolve ambiguous or conflicting legacy behaviors; adoption includes their migration consequences.

Foreign model manifests carry an immutable model ID/version and code/dependency digests, not live Python callables or closures. A reviewed registry resolves the model, whose mutable state and environment inputs are explicit per invocation. No undeclared host globals or ambient randomness may change its behavior. Registry admission is an audited extension boundary with independent tests; model changes invalidate semantic caches.

## Transfers and dynamic allocation

Dense array-to-array transfer preflights logical bounds/initialization, snapshots the source values, and applies ordered writes under its ownership contract. Overlapping copies therefore have snapshot meaning. Hardware can use an equivalent proven traversal or explicit temporary storage; it cannot silently perform a different in-place copy.

Gather/scatter snapshot array-backed addresses and values as specified in R008. Duplicate ordered scatter destinations receive the last logical write. Stream-backed transfer operands are captured once per logical element; physical padding consumes no extra source tokens. Faults after committed streaming transactions retain prior commits. Target DMA issue/acknowledgement does not redefine the language's completion point.

Dynamic device allocation uses a declared bounded allocator service, request/response, quota/failure policy, and generation-bearing handles. New allocations use the proposed zero initialization policy. Free requires completion of outstanding operations and release of active ownership/read leases. Stored view descriptors may remain, but free invalidates their generation; subsequent use faults as stale, even if a new allocation reuses the address. A definitely stale source use may be diagnosed statically. Merely retaining an inert descriptor does not prevent free. An HLS target must provide a valid pool/service route or diagnose its missing capability. Host `malloc` is not an implicit device allocator.

## Stop, cancel, and completion

Graceful stop halts admission and drains already admitted work. Stop-sensitive Sequential/Pipe loops default to an admission window of one; an explicit concurrent window W is a semantic choice because it changes the possible committed set. A soft pipeline-II or parallelism request cannot silently change that window or its refill/checkpoint rules.

Cancellation withdraws unissued requests at defined checkpoints. Issued external transactions must complete/acknowledge or use a declared supported abort protocol. Already committed writes/tokens are not rolled back. Cleanup releases owned resources after drain, closes endpoints consistently, and uses new generations for restart. Immediate process termination is not a hardware cancellation model.

RunResult has the closed tags Completed, Fault, Cancelled, Stopped, End, WaitingEnvironment, QuiescentUnknown, BudgetExhausted, Breakpoint, and Deadlock, with the payload/resumption matrix in [[40 - Package and Conformance Blueprint#Public workflow and failures]]. Only Completed carries complete output snapshots; every other tag has outputs absent and explicit partial state. WaitingEnvironment needs an actual enabling dependency path; QuiescentUnknown records unresolved dependencies. End handled within a kernel need not end its invocation. Pending terminal cleanup retains its cause under an incomplete outcome until obligations quiesce. Graceful stop resumption completes already admitted body effects under the stop policy before terminal draining, with no new admission. Breakpoint resumes after the observation; a certified Deadlock allows only declared cleanup control without inventing an enabling event. Observation, aggregate numeric and per-helper resource exhaustion report BudgetExhausted with named limits and resumable state, not a language fault. All producers must close and drain accepted sends before the channel is closed; End also requires its committed tokens drained. Feedback requires explicit initial tokens/state. A timeout does not prove deadlock or nontermination. General liveness requires stated fairness/environment assumptions; bounded exploration supplies evidence only for its finite instances.

## Concrete implementation design

[[30 - State Simulator and HLS Blueprint]] specifies continuations, captured requests, unified arbitration, fair execution, cleanup obligations, exact address/quota allocation and finite memory/HLS planning algorithms. The package blueprint fixes invocation ownership and resumable outcomes. Zero-data-bit aggregates retain logical cells/init/lifetime without a physical byte access. Dynamic addresses use explicit environment values or the named first-fit reference profile; address bits alone never authorize access.

## Acceptance

Use R003's order/lifetime cases and R008's complete A-series. Independent reviewers must include the capacity-one merge/producer-consumer cases, pending operand exactly-once behavior, active/inactive faults, per-field stream consumption, cancellation after external issue, alias bypass of locks, stop windows, and persistent reset. Compare committed event traces and protocol state, not only final sums. Hardware evidence additionally needs stalled-interface/RTL tests and target capability checks from the HLS studies.
