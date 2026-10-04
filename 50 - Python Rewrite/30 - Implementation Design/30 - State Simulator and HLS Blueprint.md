---
type: implementation-blueprint
title: "State simulator, memory planning, and HLS implementation blueprint"
project: spatial-python
date: 2026-10-01
status: reviewed
adoption_status: proposed
implementation_status: not-implemented
source_notes:
  - "[[PY-R003 - Control Memory and Effects]]"
  - "[[PY-R005 - Full Language Coverage and Migration]]"
  - "[[PY-R008 - Advanced State and Communication Protocols]]"
  - "[[PY-R009 - HLS Boundary and Control Lowering]]"
  - "[[PY-R010 - Memory Scheduling and Design Space Exploration]]"
  - "[[30 - Python State and Protocol Contract]]"
  - "[[40 - Python Compiler and HLS Contract]]"
  - "[[05 - Independent Protocol and HLS Review]]"
feeds_spec:
  - "[[30 - Python State and Protocol Contract]]"
  - "[[40 - Python Compiler and HLS Contract]]"
---

# State simulator, memory planning, and HLS implementation blueprint

## Purpose and authority

R008 specifies the intended resource values and transitions; R009/R010 specify preservation obligations. This note fixes the target-neutral construction algorithms needed to implement those rules. It does not approve production implementation, report an implemented Spatial simulator, or claim vendor synthesis/RTL support. The full intended language remains the scope, with finite hardware bounds and unsupported target capabilities reported separately.

The reviewed baseline was clean vault commit `b56a49630f22b204ab1a4f0c531adf3647ac1639`. The original source pin remains `spatial@e7a8f2f7f776dd0c5ac7fc03f16b3ed4d97021f0`. Source inspection confirms `DRAM.address: I64` at `src/spatial/lang/DRAM.scala:23–24` and `DRAMAddress` at `src/spatial/node/DRAM.scala:17–19`; therefore address values cannot be dismissed as unobservable implementation metadata. Other original-source facts and vendor documentation are inherited only with the evidence boundaries in R003/R008/R009/R010. No fresh vendor or board result is claimed.

The companion frontend/checker blueprint owns the closed semantic operation/region schema and order-token rules. The numeric blueprint owns exact value recipes, normalization/fault guards, RNG words/attempts, and helper certificates. The package/conformance blueprint owns canonical serialization, diagnostic/artifact/run envelopes, dependency locks, and evidence IDs. This note supplies records that those schemas reference; it does not introduce an alternate source parser or numeric evaluator.

## Closed state-operation interface

Every state operation resolves a compiler-owned `TransitionSpec` by `(transition_id, version)`. This is a closed tagged union, not an arbitrary Python function name, callback, or serialized closure. Component extensions resolve immutable registered model IDs through the reviewed extension boundary already required by R008. Unknown transition IDs or malformed shapes reject during import/checking.

| Record | Exact payload and checks |
|---|---|
| `TransitionSpec` | Resource kind; operand/result type schemas; ordered operand names; mode `Ordered` or `Communicating`; effect kinds; capability requirements; guarded fault checks in order; pending/commit/cleanup state layouts; readiness dependencies; reset/close rules; whether an external issue is irrevocable; permitted outcomes. Version contributes to semantic identity. |
| `ResourceRef` | Logical resource/backing ID, generation value or activation-bound generation argument, view map if applicable, endpoint ID, and a capability reference. Resource IDs identify language objects; physical addresses do not create authority. |
| `PendingRequest` | Request ID; task slot/activation generation; source operation/span; transition ID/version; predecessor order-token runtime ID; immutable typed captured payload/address/mask/count/conditions; resource generations; requested capability/domain; continuation PC and result destinations; phase; private helper/packer state; obligation IDs. No unevaluated source expression remains. |
| `GrantRecord` | Request and contender-snapshot IDs; selected resource endpoint; old resource version/generation; reservation domain; selected queue/selector decision; captured return bits or helper state; commit predicate. A proposal is not a consume and does not update a pointer. |
| `Obligation` | Activation/request/resource generation; issue ID; response endpoint; captured transaction; accepted/issued/response/visibility state; completion accounting; abort capability; source operation/span. A response may discharge only its exact live obligation. |
| `TaskState` | Stable bounded slot or reference task ID; activation generation; parent/join ID; frame stack; runnable/waiting/draining/terminal state; one currently pending source operation; issued obligation set; local resource roots; cleanup stack; stop/cancel/fault cause. |
| `ResourceState` | Kind/version; generation; logical capacity/shape; initialized cells; token/cell data; endpoint states; arbiter cursor; ownership/leases; pending request IDs; in-progress transaction; family-specific metadata. Its mutable state is invocation/session-owned, never stored in the immutable checked program. |

Operation inventory is parametric rather than a whole-program recognizer:

| Family | Closed transition tags |
|---|---|
| Reg/SRAM/RegFile/LUT/ROM | allocate; read; write; observe; reset; RegFile shift; lifetime-end. LUT/ROM reject mutation. Active bounds/init/generation faults are ordered effects; total-pure bit operations remain numerical operations. |
| FIFO/LIFO/FIFOReg | produce; consume; peek; occupancy observation; width readiness; explicit same-resource atomic batch; producer close. FIFOReg is scalar capacity one with consuming availability, defined below. Masked vector operations compact active lanes, keep original result-lane positions, and commit as specified in R008. |
| Selectors | fixed-priority, caller-rotation, stateful-RR receive. Captured conditions/iteration are immutable while pending; queue readiness is sampled for the grant. |
| Locks | acquire whole deduplicated key set; protected region entry; release-after-visibility; cleanup release. A descriptor carries an explicit key-to-protected-domain mapping. |
| Merge | begin frame; accept way tokens; framed output receive/packer step; way close; end frame. Each input consume is a separate committed protocol event even when the source vector receive is incomplete. |
| Line/published buffers | begin staging frame; fill row; publish; acquire-next-version; lease read; release lease; explicit fill/reset. |
| Streams/components | receive/tagged receive; send; producer close; record zip/coherence adapter; foreign primitive issue/complete; foreign actor transition/reset/close. Bundle fields are individual endpoints. |
| Transfers/allocation | array dense/gather/scatter begin/preflight/snapshot/write/complete; streaming address/data capture/item issue/complete; async join; allocate request/response/initialize; free drain/response. |
| Control | FSM initialize/test/action/next/complete; structured task group; task completion; explicit checkpoint; stop observation/admission; cancel delivery; drain; restart/reset. |

The inventory does not invent aliases, ownership, reset defaults, or numerical laws: those are inputs from the checked semantic program. A resource may have many issued implementation obligations while a task has one unfinished source operation; completion of that operation produces its one successor order token.

Vector receives with inactive lanes return `MaskedVec(N,T)`, a semantic descriptor containing validity Bool lanes and packed payload lanes. Invalid raw payload is canonical typed zero only for deterministic internal storage/serialization; it is never ordinary usable `Vec` data. Indexed extraction returns T only after an active-lane proof or runtime `InactiveLane` guard. `materialize(default:T)` explicitly fills invalid lanes and returns Vec. Plain Bits packing/reinterpretation, FSM embedding and ordinary arithmetic reject MaskedVec until materialized or an admitted mask-preserving operation applies. No raw `.values` bypass exists. Plans retain and cost these validity bits, and must gate effects/faults in masked operations before executing invalid lanes.

Reg/RegFile declaration resolves its reset image during checking. A bare declaration requires a registered ZeroImage for the element descriptor; otherwise require an explicit supported reset. Runtime allocation uses that checked typed reset image and the declared lifetime, never a Python constructor or target-dependent default. Under the source blueprint's closed ValueStorage capability, private Index cells reset to exact integer zero; private MaskedVec cells reset to all-invalid lanes with a recursively registered canonical zero payload, preserving validity guards on every load/store. Neither gains packed Bits or an implicit finite-width ABI. Target planning must prove a finite Index range and preserve mask semantics in a registered layout, otherwise reject that scoped target route.

## Region-to-continuation construction

Compile the checked structured regions once into an immutable `ExecutionProgram`. A block is a sequence of closed instructions plus one terminator. Each instruction records semantic operation ID, source span, explicit operand value IDs, result destinations, and effect-token binding where applicable. PCs are `(block_id, instruction_index)`, never Python code objects. `ValueStorage` is a closed union: normalized numeric/raw Bits; Bool; exact signed mathematical Index; recursively typed Vec/Tuple/Record values; MaskedVec payload/validity; Unit. Handles remain separate typed descriptors. Finite target Index storage uses a proved range/ABI width and checked conversion, never an implicit reference wrap; unknown finite bounds fail that target capability.

| Execution instruction/terminator | Construction rule |
|---|---|
| `Value` | Only adopted total-pure numerical/aggregate operations. Read result operands from the current frame. A potentially faulting numeric operation is a token-carrying guarded operation, not this instruction. |
| `BeginRequest` | Read already evaluated operand values in their declared order, freeze the request payload, and set `resume_pc` to the result-binding continuation. Creating a pending request does not re-execute operand producers. |
| `SelectedRegion` | Evaluate the already captured predicate once and push only its selected region frame. The selected region's yield supplies values/token to the parent continuation. Untaken frames are not created. |
| `Loop` | Retain captured start/end/step/domain, iteration/lane counters, loop-carried values, admission policy and body completion state. Push a fresh body frame at admission; on yield assign carried values and advance checked mathematical shape counters. Never reinitialize an enclosing allocation at a loop tick. |
| `CallRegion` | Push checked callee region with explicit actual values/capabilities and a return continuation; no Python host call. Pop on typed yield/return. Callee-local resources are cleaned before return; illegal local handle escape has already rejected. |
| `TaskGroup` | Consume the parent operation's input order token once. Create all declared child activations/capture frames with distinct child order domains and a `JoinRecord`; park the parent at a join continuation. Each child emits `task_complete(values, child_token)` once. Parent result/token appears only after all children complete/drain under the group's policy. A split spawn/join implementation uses a typed join handle; it never consumes the pre-fork token a second time. |
| `Yield/Complete` | Bind declared results and terminal token to the parent continuation/join; run required local cleanup; then pop/complete exactly once. A task with outstanding obligations cannot complete successfully. |

Total-pure helper/conditional regions have tokenless signatures and frame continuations; token storage exists only when the derived effect/fault/control-lifecycle summary requires it. Every state operation and task/FSM lifecycle remains tokenful. The reference interpreter does not manufacture a token edge for a pure value call merely because its engine uses a control PC.

The frontend's single-block structured semantic regions need not become single flat execution blocks. Split at every token-carrying operation, helper entry/return, selected-region boundary, loop admission/completion, fork/join, explicit checkpoint, and terminal cleanup. Liveness analysis computes values crossing each split; a simple reference implementation retains the whole frame value environment first, while hardware allocates only proved live captures.

Each activation-local declaration creates a fresh logical resource generation. A body-local declaration creates a fresh generation on body entry. The checked lifetime tag determines which frame owns it. Ending that frame invalidates its capability/generation only after its cleanup obligations drain. Persistent state roots live in an explicit session object; invocation frames do not own or silently reset them.

Memory-reduction mapper temporaries use an explicit `ContributionLease`: the mapper's typed region yield transfers its temporary resource root to this registered contribution owner before the mapper frame closes. It remains live through the contribution's element reads/combine obligations and then releases/invalidate its generation. This is a special region result and lifetime extension, not permission for ordinary helpers to return their local memory/permits/leases. Candidate pipelining must retain enough contribution storage/credits for every admitted live lease; it cannot prematurely recycle a completed mapper's array.

An empty destination memory domain does not erase an active mapper invocation: execute it once for each admitted map-domain index in the declared contribution order, retaining its effects/faults and temporary lifetime, then perform zero destination-cell reads/combines/writes and release the contribution lease. Disabled/all-invalid map bodies execute nothing. Map-domain emptiness and destination-cell emptiness are distinct controller facts.

Ordinary assignment subexpressions have already been lowered in RHS-before-target order; augmented assignment retains one target capture before the RHS. A blocked `BeginRequest` consumes no source expression again. Source-generated request phases and source/builder parity are compared before simulator/backend optimizations.

## Canonical fair event loop

Before execution, verify the derived ExecutionProgram against the checked semantic revision and its lowering-table version: block/PC targets, frame argument/result types, token/control correspondence, exactly one request boundary per dynamic execution of a request-producing primitive, and exactly one completed return/pop for each entered frame. Structured control has its own fork/join/loop transitions; it must not be forced into the primitive-request invariant. The source span/event mapping covers every operation preserved by lowering. This derived program is an execution cache with explicit dependencies, not a new authority for language meaning. A small direct region evaluator supplies independent ordered-subset fixture traces for assignment order, lazy branches and nested calls/loops. Queue branch cases extend that oracle at the queue slice. Neither evaluator may create its expected trace by invoking the same continuation-lowering routine.

Use a stable ring of action slots and a retained cursor. In reference execution IDs are stable lexicographic tuples; in hardware they are bounded slot numbers, with separate activation generation preventing reuse confusion. Slots exist for runnable task steps, resource grant/commit/helper steps, delivered environment events, issued-response processing, and cleanup actions. Finite hardware profiles declare slot maxima; reference profiles can grow the table deterministically, retaining fair queue tickets for existing actions.

At each turn:

1. Admit recorded environment deliveries in replay order into their typed endpoint/response buffers. Delivery is not automatically a source receive. Do not fabricate an event because fairness says it ought to arrive.
2. Calculate enabled actions from current task/resource state and exact readiness dependencies. Discard stale activation/generation request IDs only according to the declared response/error policy; never credit them to a new activation.
3. Starting at the cursor, choose the first enabled action; execute one finite quantum; set the cursor to the slot after that action. A task quantum ends at its next effect/control boundary. A pure segment also yields at the interpreter instruction budget, retaining its PC. A resource helper quantum does bounded local work and yields; waiting for an external response never occupies the execution arbiter.
4. Record request/grant/commit/control/cause events, then resnapshot readiness. A commit advances the resource version and the request's terminal order token exactly once. Failed/abandoned operations produce their terminal diagnostic/cancel path, not a successful value.
5. If no action is enabled, classify quiescence below. If the observation budget is exhausted while runnable, return a resumable incomplete snapshot. Numeric helpers advance through bounded local work quanta with explicit counter/private state, or through an independent request/response unit. A strict-math refinement loop cannot become one opaque unbounded scheduler call; its precision/interval work and suspension budget are governed by the numeric blueprint.

Round robin over a finite stable continuously enabled slot set gives a concrete weak-fairness witness. Sorting eligible IDs and always selecting the first is forbidden: a lower-ID forever task would starve another task or response action. When reference slots grow, append new tickets after the existing queue; a self-replenishing task cannot jump ahead of existing tickets. Fairness applies to task execution; an explicitly fixed-priority resource retains its permitted starvation behavior. Do not infer a latency bound for readiness that is only intermittent.

## Request arbitration, atomic batches, and selectors

The proposed default resource policy is **stateful round robin with one resource admission cursor** over stable endpoint IDs and at most one committed atomic request for that resource in an epoch. That request may include an explicitly declared same-resource read/write batch. Successful endpoint j advances the cursor to the following endpoint; disabled, infeasible, cancelled or uncommitted requests do not. This resource-selection rule is distinct from the task scheduler witness. An alternate directional/banked realization must preserve selection for the same visible request history and progress assumptions; general fairness alone is insufficient. [[PY-R018 - Protocol Policy Refinement]] records the decision and alternatives.

The ordered endpoint table is semantic policy data, preserved by source/builder normalization and artifact import. Canonical renumbering must preserve this order; arbitrary line hashes, Python object IDs or backend discovery order cannot decide a winner. The abstract epoch is not a clock cycle. Multiple physical commits per clock are permitted when their projected events linearize to allowed transitions with the same readiness, cursor updates, token/visibility and progress rules. Retain the explicit-batch no-bypass rule; do not reject a legal same-cycle dequeue/enqueue merely because the reference executor takes two steps.

For each scheduling snapshot:

1. A disabled enclosing region has already skipped its operands. For an enabled vector operation with an all-false lane mask, skip resource lookup/readiness/arbitration and return Unit or an all-invalid MaskedVec as its signature requires; do not observe occupancy or move a cursor. A consuming queue selector with all captured conditions false instead raises NoEnabledCandidate, after the condition effects and before resource observation/wait registration. It cannot return an ordinary fabricated value or be treated as a vector no-op.
2. Validate active structural counts and generations. An atomic request wider than semantic capacity is permanently infeasible and faults; it never joins a wait list.
3. A pending compound selector reads its captured conditions and the current candidate occupancy, computes the priority/rotation/RR winner specified by R008, and enters **exactly that queue's** endpoint contender set. Losing on that queue does not fall through to a different priority candidate in the same snapshot. A subsequent snapshot may choose differently if readiness changed. There is one request identity, never one clone per candidate queue.
4. Each resource proposes its first feasible contender in cyclic endpoint order. The global action scheduler chooses one proposal for commitment; proposals that are not selected do not reserve tokens or update pointers.
5. Revalidate generation/version/readiness at actual reservation. If changed, resnapshot. Reserve the selected resource transaction, snapshot all old data required by its transition, and perform its bounded internal steps. No observer of that resource sees a partially committed vector/shift/batch. Other resources/tasks can still run.
6. Commit once. Update token order, occupancy, initialized cells/version, endpoint RR cursor, and the selector's own pointer only where its rule requires. Return active lane values to their original result lanes; inactive lanes remain masked unusable values. Release the implementation reservation.

For a simultaneous queue batch, require `m <= q` and `q-m+n <= C`, read all pops from the common old state, remove them, and append active pushes in lane order. Newly pushed tokens never satisfy an empty-old-state pop. Independent requests may commit push then pop in different epochs. A transfer/zip/merge that intentionally has committed prefix steps uses explicit subtransition events; it is not misrepresented as one rollback-capable atomic mutation.

Lock acquisition's key set is one lock-resource request. The execution arbiter is released after granting key permits; ownership stays in the key table until visibility-complete release. Disjoint keys can both be held while their tasks wait on different channels. Do not serialize entire keyed regions behind a global lock. All protected accesses, including through aliases, validate compatible capability/domain metadata; a coincidental simulator execution order cannot legitimize an unchecked race.

## Resource implementations from the transition tables

| Family | First correct data structure and transition implementation |
|---|---|
| Queue/stack | Packed Bits token list/deque in reference; bounded array plus head/size or top/size in hardware. Request masks compact to an index list; validate counts before mutation. Attach monotonically identified tokens for trace accounting. Peek/status have versions but reserve nothing. |
| FIFOReg | A scalar capacity-one queue with reset payload bits but occupancy zero at construction/reset. `.value`/read consumes; assignment/enq produces. Payload reset image never synthesizes an available token; an explicit seed operation is separate. Full/empty ordered actions fault, communicating actions wait. After enq7, one read returns7 and a second cannot repeat7; reset returns empty, not a zero token. This is the declared bounded redesign of original empty elastic Scalagen versus one-register valid-bit RTL (`ScalaGenFIFO.scala:46–52`; `MemPrimitives.scala:339–365`). |
| Selector | Captured condition vector/iteration, candidate endpoint vector, policy, optional RR pointer. The shared resolution procedure above performs its observation-and-consume; there is no independent peek-then-later-pop helper. |
| Lock | Exact packed key→owner map, live-key capacity, pending endpoint RR, and capability-owned protected domains. Canonical key ordering is `(lock_id, type_id, packed_bits)`. Track completion/visibility before release; canonical nested ordering and nonreentrancy are checked at acquisition. Finite hardware keys use a bounded associative table or exact comparator network, never hash equality without collision resolution. |
| Merge | Frame ID/counts, per-way accepted/remaining/delivered counters, sortedness last key, token queues, comparator profile, and one private output packer. Consume the least available head only after every nonexhausted way has a head. Each scalar consume commits and frees its way's capacity. Publish a captured vector only once the packer is complete; cancellation traces discarded staged tokens. |
| Line/published window | Staging rows with per-row cursors and init maps; immutable logical version images/leases; explicit next-version delivery state per consumer; semantic free-credit counter. Reference may copy snapshots. Hardware ring slots use refcounts/undelivered bits and retain old initialized cells until every relevant lease releases. Default two semantic credits remain two even with more physical slots. |
| RegFile | Logical cell/init/reset images; shift captures the full selected old slice, then commits R008's exact `new[j]` formula. Implement bounded register assignment or a multicycle scratch transaction hidden from observers. |
| FSM | Frame phase `Init/Test/Action/Next`, packed state, immutable old-state capture, Action continuation, completion dependency. Test/Next read effects retain their token/order semantics; any permitted observation is evaluated once in that phase. No effectful dequeue/call is hidden in repeated combinational evaluation. |
| Components | Transition/model ID and digest, explicit instance state, typed environment inputs, readiness/result/event outputs. Registry resolves the model, then invocation state owns all mutation. Missing/incomplete reference behavior is a capability diagnostic, never zero. |

## Cancellation, faults, cleanup, and restart

Cancellation checkpoints are: before entry into a new token-carrying operation; before a reversible reservation first issues an external effect or commits a logical mutation; controller admission/completion boundaries; explicit source checkpoints. Effectful operand subexpressions are separate token-carrying operations, so cancellation can occur between their already committed captures. Pure/helper microsteps may poll a pending cancel flag but do not add a cutoff inside an indivisible logical commit. A scheduled cycle cutoff is a separate profile.

| Request phase at checkpoint | Cancel/fault action |
|---|---|
| `Captured` | Withdraw pending request, emit Abandon for private captures, no resource mutation. |
| `Reserved`, no external issue or logical commit | Finish/release reversible internal reservation or abandon it without state change. A fixed RNG draw can discard private accumulator and release its token without advancing the committed word position. |
| `Issued` or external acceptance completed | Retain obligation. Stop further user issues; receive actual completion or invoke the declared abort protocol. Visibility/response completes according to that external contract. No synthetic acknowledgment. |
| Incomplete prefix operation | Preserve committed dequeues/zip members/merge packer consumes/RNG attempts and prior writes; abandon only remaining private captured state. Trace identifies the prefix and discarded staged tokens. |
| `Done` | No rollback; proceed to cleanup. Duplicate terminal events reject. |

A fault cancels the faulting activation's declared subtree, prevents successful result publication, retains all issued obligations, then drains cleanup and reports Fault with its already committed effect trace. An enclosing task-group policy determines sibling cancellation; root invocation failure defaults to cancelling its admitted subtree. Cancellation is delivered as a scheduler event, never a host exception that skips the cleanup stack. Fault precedence, source operation order, and committed prefixes stay recorded even if drain itself later stalls/fails.

Cleanup stack entries are closed tags: join descendants; drain issued operations; close owned producer; release protected capability after writes visible; release version/transfer leases; free owned dynamic allocations; invalidate local generations; notify parent/join. Dependencies among cleanup entries form a DAG/explicit wait relation; they are not merely executed in arbitrary destructor order. Releasing ownership or freeing storage is disabled while its obligation set is nonempty. Draining tasks run only obligation and cleanup transitions, with no new user work/admission.

An accepted send is already a source commit at acceptance even when its adapter still has delivery obligations. A DMA issue is not its destination-visibility commit. These distinct phase flags avoid treating every external effect as one identical transaction. Reset/restart waits for prior drain unless the target's declared session-reset/abort protocol safely invalidates it. Activation generations and request IDs prevent a late response from releasing new credits or writing a reused allocation.

Graceful stop observes the stop value before admission and after completed bodies. Retain the checked admission set/window W and fork grouping; once stop is observed, admit no new body and finish every admitted body's effects and cleanup. W=1 is the stop-sensitive Sequential/Pipe default. No II/unroll optimization enlarges W or changes its refill boundaries. Reset of an owned breaker occurs after drain; a shared/external stop signal is not automatically written.

## Close, waits, and deadlock certificates

Each declared producer endpoint has `Open/Closing/Closed` and accepted-send obligations. `close` captures a source close operation, stops new endpoint sends, drains its accepted sends, then commits Closed. A channel is input-closed only when every declared producer has Closed and all admitted sends have completed; End additionally requires its committed token store drained. P0 closing cannot end a channel while P1 remains open. Task exit does not infer close from empty storage: the task descriptor explicitly lists producer endpoints whose structured exit emits close, otherwise source must close them. Cancellation cleanup closes owned producers by the same transition.

At no-enabled-action quiescence, construct a wait graph. Nodes identify live tasks/requests, queue token/space conditions, lock keys, publication credits/leases, join children, transfer ownership, external responses/ready/input events, and cleanup obligations. Edges identify the exact dependency and generation. Internal primitive readiness dependencies are complete and explicit; no opaque FIFO/lock dependency is deferred to a future solver.

- `WaitingEnvironment`: provide a concrete dependency path from a blocked live operation to a permitted external event whose model can enable progress. Preserve a resumable snapshot; no event is fabricated.
- `Deadlock`: provide a finite closed wait graph with no enabled action and no permitted enabling external root reachable from the blocked component. The certificate includes resource state/occupancies/owners and the complete readiness dependency table used.
- `QuiescentUnknown`: resumable incomplete state when an external model's permitted enabling dependencies or the required analysis are not established. This is a proposed API refinement; it does not claim that an enabling event exists or that deadlock is proven.
- `BudgetExhausted`: incomplete snapshot when a supplied observation/exploration budget ends. It is not a language termination condition or deadlock proof.

An unrelated open endpoint cannot excuse a closed blocked component. A blocked component and a separately waiting external task may coexist; report component classifications plus the incomplete invocation outcome. Reachability is a constructive certificate over declared transition dependencies, not an algorithm deciding arbitrary Python model liveness. Unknown model dependencies must diagnose or produce QuiescentUnknown, rather than claim universal deadlock freedom. The exact public RunResult tags are Completed, Fault, Cancelled, Stopped, End, WaitingEnvironment, QuiescentUnknown, BudgetExhausted, Breakpoint, and Deadlock. [[40 - Package and Conformance Blueprint#Public workflow and failures|The public core API]] owns their complete-output, partial-state and continuation matrix. Only Completed exposes complete outputs. Breakpoint resumes after its observation event; Deadlock permits only declared cancellation/drain control in the unchanged closed state. An endpoint End handled by the kernel is not automatically a terminal RunResult. Pending fault/stop/cancel/end cleanup that cannot yet quiesce returns the applicable incomplete outcome with pending_terminal retained, rather than falsely declaring terminal cleanup complete. For a graceful stop, finish the body effects of already admitted iterations before terminal draining; resume cannot admit new iterations but must not discard that required admitted work. Internal numeric ResourceLimit maps to BudgetExhausted with named limit and preserved helper state; resumption cannot replay committed operand or RNG effects.

## Exact transfers, views, and allocation services

Normalize a view into `(backing_id,generation,rank,logical_extents,origin,stride_map,accessible_domain)`. Compute addresses with mathematical integers and perform per-axis logical bounds before checked conversion to bus/index widths. Explicit stride maps may be affine or an adopted checked index expression; an unknown alias result is not independence. Caller-owned storage/address bindings are explicit invocation inputs.

For arrays, capture endpoint/count descriptors, acquire the declared ownership domains, preflight all selected coordinates/init requirements, snapshot the complete selected source values/address list, then write in row-major/list order. A preflight fault precedes every transfer destination write. Full snapshot scratch is the initial correct implementation; directional or dependence-scheduled copies are candidate optimizations with a whole-transfer certificate, not tile-local guesses. Duplicate scatter addresses create ordered write dependencies. Gather duplicates may reuse only one stable snapshot value with preserved logical result/event accounting.

For streams, use an item PC sequence `capture address → capture value → validate → issue → commit/ack → next item`; the selected source kind fixes which steps occur. Capture each token/read once, retaining it while blocked. Invalid streamed addresses fault after their specified captures; prior item commits persist. Limit outstanding requests and drain responses throughout, rather than issue an arbitrary request batch before processing any response. Physical padding consumes no logical items. Async transfer handles hold their ownership domains until join and required visibility/ack.

An `AllocatorProfile` declares address width/unit, base, address-arena span, quota, alignment, quota-charge rule, address-span rule, admission order, free policy, initialization, failure behavior, response endpoint and algorithm/version. Standalone default reference profile `first_fit_bytes_v1` is:

1. Addresses are unsigned 64-bit **byte-address bits**, base `0x1000`; quota Q, address-arena span M and positive power-of-two alignment A are explicit invocation-profile values. Address arena `[base,base+M)` must fit mathematically in the address width and be disjoint from live borrowed/static address bindings. Storage authority still comes from the typed generation-bearing handle, never these bits.
2. Quota charge is `ceil(product(dims) * element_bits / 8)`; all dimensions are nonnegative checked shape integers. Address span is **separately** `product(dims) * ceil(element_bits/8)` using the portable element-slot ABI, with dense row-major strides. Physical bank/packing padding is a third quantity. Hardware must reserve enough physical storage without changing either quota or virtual address success/failure policy. A different charge/span policy is a separately identified allocator profile. For W=4,N=33, charge is 17 bytes but the address interval spans 33 bytes; advancing the next base by 17 would create an illegal live address overlap.
3. Keep sorted half-open free **address** intervals and a separate used-quota total. A request queue uses stable endpoint RR. At a grant, first fail `QuotaExhausted` if charge exceeds remaining Q, then choose the first interval whose aligned start and address span fit. Allocate that address range, split it, charge quota, and return its start. If none fits, fail `AddressSpaceExhausted`; invalid/out-of-width structural address arithmetic faults `AddressOverflow` before issue. These are distinct AllocationFailed reasons, not indefinite memory-full waits. Alignment gaps remain free. Zero-extent allocations are Live empty objects with fresh identity/generation, return the aligned base sentinel without consuming quota/address span, and cannot authorize an access. An adopted zero-bit element type similarly has no physical byte access but retains its logical cell/init/capability meaning.
4. Each success creates a fresh backing identity and generation and initializes every logical cell to typed zero before Live/response completion. Service success and promised initialization are both required; issue does not make is_allocated true. Static host/borrowed DRAM obtains base-address bits from its explicit invocation address table under the same observable-value rule.
5. Free drains active transfer/ownership/read leases, invalidates the generation, returns its address range, decrements its exact recorded quota charge, and coalesces adjacent free intervals. Inert stored view descriptors do not block free and remain stale. Double-free/use-after-free faults; same-address reuse never revives a descriptor. Pending external transactions carry their old allocation generation. If cancellation/fault arrives after allocator issue, retain the response obligation; a later successful allocation is released through cleanup even if its handle was never published to user code.

Allocation request/response records include request ID, dimensions/footprint, policy/profile ID, allocation handle/generation, address bits, response result and initialization completion. Device or host allocator services may provide environment-supplied address bits instead of the deterministic reference service. Reference/hardware parity then requires matched service/address responses or a validated virtual-address map. Source may perform raw Bits/integer arithmetic on returned address values under the declared type, but bare bits never create a dereference/foreign-component memory capability. Foreign manifests distinguish address values from authorized memory regions and declare any virtual/physical translation. Never compare arbitrary reference defaults with arbitrary platform bus addresses as if equal.

## Target-neutral HLS route selection and universal machine

Construct a checked `ProtocolPlan` from the execution program rather than from source syntax. It contains task/frame/PC layouts; bounded activation/capture slots; resource descriptors; endpoint/arbitration tables; order/join/admission relations; cleanup/response obligations; interface records; and the semantic-event projection of each machine transition. Unbounded reference loops are permitted; the finite target profile bounds simultaneous live state/storage, not total iteration count. Profiles with unbounded simultaneous allocation/task creation require an external bounded service/arena or receive a scoped hardware capability diagnostic.

The 3 October refinement requires these same finite transition records to execute in a Python plan runner before vendor C simulation. The runner uses the recorded guards, captures, commits and projected semantic events; it does not acquire source or define a second language. Compare its projected traces and finite wait/termination outcomes with independent acceptance cases under the same environment assumptions. Include mutants that lose a vector mask, publish early, return credits early or introduce an internal stall. Shared numeric helpers remain a common dependency, so this comparison does not replace independent numerical oracles. Passing it establishes a plan-level check, not vendor scheduling, RTL protocol correctness or timing. See [[PY-R018 - Protocol Policy Refinement]].

Route selection is deterministic:

1. Partition only along verified resource ownership/interface boundaries. Build the actor/resource incidence graph and identify shared arbiters, feedback, joins, external interfaces, and stop/cancel groups. A shared resource stays owned by one process/component or an explicit arbiter; never split its mutable state between processes.
2. Try direct ordered C++ only where there are no source-blocking cross-task dependencies and the memory/fault protocol can be implemented without freezing needed concurrent actions. Hard overlap requirements cannot take a serial route.
3. Try control-driven DATAFLOW only when the locked target capability profile admits the graph's static process calls, channel ownership, feedback/control pattern, interface types and finite invocation lifecycle. Each process-local condition/valid protocol, start/join/stop/close, exact semantic capacity and fault/drain rule remains explicit. An unconstrained pragma does not satisfy the eligibility predicate.
4. Try persistent task library only when its locked profile supports the required interfaces/state/reset, bounded channels, ownership, close/done/cancel controls, and invocation/session lifetime. Streams-only examples do not establish memory or reset support.
5. Otherwise construct the universal fair protocol-machine plan below. If an interface requires a concurrent adapter/component outside the chosen HLS capabilities, its exact integration route must exist in the target profile or the scoped capability fails. Missing direct dataflow eligibility does not remove the source construct.

The universal route is an interleaved microstep controller with task PC/capture registers, logical resource machines, scheduler cursor, and nonblocking external issue/response queues. A step advances one task boundary, commits one resource transaction, progresses one bounded helper, processes a response, or drains one cleanup item. Whole tasks are never called serially to completion. Waiting tasks preserve their frames and yield the execution arbiter. Key permits/leases remain separate ownership state. Finite local atomic operations may reserve their resource while their multicycle helper executes; they cannot retain the global scheduler while waiting for an unbounded environment event.

The target-neutral emitted structure is `manager + single-owner adapters`, with DATAFLOW or an explicitly declared RTL integration boundary providing physical concurrency. The manager uses its own bounded arrays/counters for language queue occupancy/capacity; vendor stream depths/full flags serve only the adapter's physical handshake and cannot redefine source status. An adapter owns one endpoint and sequences request/data/response. Baseline external transfer concurrency is one request per endpoint; higher outstanding counts require the same accounting/progress checks. Response backpressure drains fairly even during stop/fault. Adapter storage/credits are implementation state and cannot enlarge semantic token/publication capacity.

Ordinary pointer/M_AXI access inside one central FSM can stall every task until response. It is admissible only with a proved progress contract independent of blocked source actions. The general route instead has manager→adapter request and adapter→manager response channels, so the manager can execute tasks while the adapter awaits the bus. A separate DMA owner process must not synchronously wait for manager data that the manager cannot produce until an undrained response is consumed. Request/data/response capacities and issue order are explicit. This structure fixes an implementation path now; vendor release-specific process/M_AXI/blackbox legality remains a target capability and later executable probe.

The request-adapter boundary declares exactly where source issue occurs. In the skeleton below, accepted request-queue offer transfers ownership to the adapter and is the semantic issued event; the adapter owes the eventual bus transaction/response even if source cancellation arrives before electrical bus issue. An alternative withdraw-before-bus-issue protocol needs an explicit queued/issued response and abort handshake; it cannot silently discard an accepted request. This definition aligns reference environment events with the actual completion obligation.

## First reproducible validation profile

Propose profile ID `vitis-2025.1-z020-10ns`, with HLS `2025.1` build `6135595`, `vitis-run` build `6137779`, Vivado IP flow, Tcl part spelling `xc7z020clg400-1` (report spelling `xc7z020-clg400-1`), target period `10.00 ns`, clock uncertainty `2.70 ns`, explicit portable ABI/profile versions, and exact installed tool/include/component digests to be recorded at real validation. It is the first validation profile, not a claim that every intended language feature fits Z020; other device/profile records may support larger live state and full-family expansion.

Fresh pinned-source inspection on 2026-10-01 verified those historical values in `spatial-rs@eb49d8bc47bea46c83a7eb26f6a244f6303eebcb:docs/vitis-validation/2026-07-03-current-head-c3e3be5-35-program/SramTileFoldSum32/vitis-both.log:2–27` and `.../MatrixTileMemFoldInPlaceFixPt4x6x5/project/solution1/syn/report/csynth.xml:1–13`. These are historical Rust artifacts. They establish a reproducible proposed tool/part/clock starting point, not a current installation, available device, Python feature, or transferable validation result.

The minimum generated batch recipe is below. Set `PROJECT_DIR`/`ARTIFACT_DIR` from the verified project manifest, not source text. Manifest paths are checked data passed through the tool adapter; no untrusted source text becomes Tcl code. Preserve per-stage logs, generated artifact/report hashes, warnings and request-vs-achieved metrics. Explicit uncertainty avoids inheriting an unrecorded default.

```tcl
open_project -reset $PROJECT_DIR
set_top spatial_kernel
add_files "$ARTIFACT_DIR/kernel.cpp"
add_files -tb "$ARTIFACT_DIR/harness.cpp"
open_solution -reset solution1 -flow_target vivado
set_part xc7z020clg400-1
create_clock -period 10
set_clock_uncertainty 2.70
csim_design
csynth_design
cosim_design -rtl verilog
exit
```

The initial target realization registry admits documented ordinary fixed-width C++ control/arrays and explicit unsigned-bit helpers as emission candidates only after type/width/bounds/order checks; every actual generated feature still passes its C/synthesis/RTL gates. Local protocol-machine variants require finite live-state/resource widths and explicit fault/cleanup paths. External transactions, persistent task libraries, RTL blackbox integration, stream feedback/nonblocking manager-owner arrangements, and vendor numeric substitutions each carry their own release-specific eligibility/probe record. A missing probe is not a validated target capability; source/reference support remains independent.

Fresh primary-document inspection retrieved **UG1399 displayed 2025.1 English**, release date 2025-09-10. The [DATAFLOW directive page](https://docs.amd.com/r/2025.1-English/ug1399-vitis-hls/pragma-HLS-dataflow) lists process shape restrictions. The **explicitly versioned** [2025.1 control-driven limitations page](https://docs.amd.com/r/2025.1-English/ug1399-vitis-hls/Limitations-of-Control-Driven-Task-Level-Parallelism) was independently reopened and its header/version confirmed; its Feedback between Tasks section distinguishes unsupported scalar/array feedback from supported stream feedback with a seed-producing path. An earlier unversioned link was replaced because it can resolve to a newer release. This supports checking the exact feedback/channel form rather than rejecting every feedback graph. The manager/adapter request-response skeleton therefore requires a locked-release smoke test, especially its finite termination, start propagation and stall behavior. The direct 2025.1 nonblocking API pages were inaccessible to the extraction tool; no source fact about their unrestricted synthesis/co-simulation support is asserted here. Later 2025.2/2026.1 documentation cannot prove a 2025.1 feature.

Smoke fixtures must include manager/owner simultaneous launch, one delayed response while an independent task supplies another source token, request and response capacity-one stalls, finite End command, cancellation after request acceptance, required returned ID/error/visibility behavior, and reset/drain. Record C behavior, synthesis topology and RTL progress separately. If the locked release cannot realize the topology, use its exact validated external transaction adapter integration or report that named capability; do not replace it with a blocking central call.

## Integration and fault interface records

`ComponentPlan`/`AdapterPlan` must specify flattened port names/directions/widths, clock/reset domains and polarity, reset retention policy, stable valid/payload rule, ready sampling, request/response ID widths and ordering, capacity/credits, accepted-vs-visible event, error/abort/close/done protocol, storage authority/alias domains, source event projection, reference transition model ID/digest, RTL/HLS artifact hashes and build dependencies. No unresolved `adapter` label can enter an emitted checked plan.

For request/response external engines: request payload remains stable until acceptance; acceptance creates one obligation with activation/generation/request ID; response validates ID/generation and discharges it once; completion/visibility and error bits are distinct fields. If the protocol lacks returned IDs, the plan proves a single owner and in-order response queue with bounded outstanding count. Reset either drains or uses a declared supported abort/epoch protocol; it cannot discard accepted effects silently.

Runtime fault output is a bounded record `(invocation/profile_id, operation_id, fault_code, operand/context_bits, incomplete=true)`. Source maps live on the host. Stop new issues, retain/drain obligations and release ownership before terminal fault status. A C++ exception/assert that disappears under synthesis is not the fault route. Numeric helper faults, bounds/init/generation faults and protocol errors use the same issue/cleanup interface, preserving their source order.

## Memory plan construction and verification

Build a correct baseline before optimizing:

1. **Logical domains.** Collect backings, generations, lifetimes, views, initialized/reset images, capabilities, publication versions, and exact maximum simultaneous live instances. Normalize each view. Record actual invocation alias/address domains and guarded dynamic requirements.
2. **Access/order graph.** Create nodes for address capture, guard/fault, read/write/consume, issue, response, visibility, version publish/release and ownership events. Add task token edges, selected-branch edges, loop-carried distances, joins, protocol dependencies, overlapping snapshot/scatter dependencies and cleanup obligations. Unordered conflicting source accesses reject unless their checked source arbitration/ownership protocol resolves them; physical serialization cannot invent a race policy.
3. **Initial physical map.** One cell per word and one row-major bank is the correct local-memory baseline, with explicit logical bounds/init maps and enough storage for all semantic versions/live instances. Adopted zero-width Bits (empty vector/record) use `ZeroBitLayout(logical_shape,init_index=flat_index,version,generation)` with **no data bank/word/slice**. Their reads/writes still check logical axes/init/capabilities and update initialization/effect versions; never divide by element width or use zero as an address-identity key. Zero-width token channels retain token occupancy/order despite zero payload bits. Separate rows/instances keep generations and versions from aliasing. Published storage retains semantic credit limits. Runtime shapes use a checked maximum-sized arena with logical extents/generations; no bound means no finite local route.
4. **Protocol-owned issue.** Put dynamic local requests behind the finite fair resource machine. Vector/shift atomic actions reserve/snapshot old state then physically execute with no intermediate logical visibility. A protected transfer can hold its declared domains while waiting, as the source already does; it never holds the execution scheduler. All source logical masks gate address/fault/issue before padding or bus conversion.
5. **Physical hazards.** Convert cell access into physical word/slice/version domain. Same-word read-modify-write owns the full read→merge→write transaction. Include DMA, reset/init, replicas and all tasks in that dependency domain. Distinct logical cells sharing a byte are not independent final writes. Keep mutable replica writes visibility-complete before acknowledging the source write.
6. **Bounded schedule.** Derive issue groups from explicit source simultaneous actions and checked candidate overlap, not from every node that happens to be ready. Baseline ordinary accesses serialize through the preserving arbiter; hard simultaneous/II/port requirements may forbid that fallback. Retain admitted W, version credits, effectful lane order and fixed numeric topology.
7. **Check then cost.** Validate map/inverse/ranges, source correspondence, all port matches, guards, order, ownership, version/credit recycling, progress and target capacities; unresolved required obligations stay Unknown and prevent checked emission. Account for full snapshot scratch, init maps, activation state, arbiters, packers, allocator metadata, all physical padding/replicas/versions, and adapter buffers before ranking.

Every layout record contains logical shape/max-shape, packing order/word width, bank function, row function, bit-slice function, inverse/decoder, bank dimensions/padding, replica set/coherence protocol, version slot map and its certificate. For runtime bounds evaluate legal cells within max-shape but gate all accesses by logical shape. The compiler can always construct an injective conservative layout `row=flat_index`, `bank=declared_checked_bank_function`, `slice=one_whole_element`, with per-bank rows sized to maximum flat extent; this may be expensive but does not assume an arbitrary affine bank formula is compact or invertible. The inverse obtains logical coordinates from the row and validates the bank function. Optimized cyclic/block/hierarchical/table-ranked rows are separate candidates with injectivity/range certificates.

For usual cyclic word banking, packing occurs first: `word=floor(flat/P)`, `bank=word mod N`, `row=floor(word/N)`, `slice=(flat mod P)*element_bits`. Inverse is `flat=(row*N+bank)*P+slice/element_bits` on valid slices. Padding stays inaccessible. General affine/hierarchical bank functions may use exact finite enumeration over bounded max-shapes to construct compact per-bank rank tables, with cost/resource accounting; symbolic formula certificates replace enumeration only when verified. No requirement reduces every layout to cyclic banking.

Port feasibility is a finite matching problem for each simultaneous bank/version/phase group: left nodes are active physical accesses, right nodes are concrete port slots, edges encode read/write capability, latency/phase, replica and collision policy. A mixed `RAM_2P` has a read-only and read/write slot; two writes cannot both match even though it has two ports. Read broadcast merges only equal address/version with no intervening write. Replicated writes occupy every live replica's ports. Packed RMW creates read/write phases plus an ownership edge covering both. Overlapped loop candidates expand access phases modulo candidate II and include carried-distance latency edges. `II*d >= L` and aggregate traffic bounds are rejection/lower-bound checks, never sufficient proofs.

Concrete finite issue sets use exact matching/enumeration; reusable affine domains use adopted integer/domain certificates. Indirect addresses with unknown conflicts use a run-time ordered arbiter only where the source permits it and hard constraints still pass. The checker uses source-profile runtime guards for dynamic alias/bounds requirements where adopted. It must not emit a false independence pragma or treat solver timeout as legality. Every transformation declares invalidated certificate IDs; changed lanes/layout/packing/II/version/storage/transfer geometry force the corresponding checks again.

## DSE candidate procedure and statuses

Materialize candidates from an immutable semantic revision and explicit target profile. Choices include legal tile/lane groups, bank/row maps, replicas, packing, RAM resources, issue II, physical version storage and adapter outstanding bounds. Semantic capacity/admission/allocator policy changes are separately checked source profiles with different semantic identity.

Each candidate is `Unverified → CheckedPlan → Estimated → Emitted → VendorValidated → PhysicallyValidated`, with explicit Failed/Unknown at each gate. A candidate is feasible for a requested evidence level only after all requirements at that level are met. `CheckedPlan` certifies construction constraints/proofs, not vendor II or board fit. Cost unknowns remain labeled; a merely estimated plan does not enter a vendor-validated Pareto set.

Use stable Cartesian/structured search enumeration first, then deterministic Pareto filtering on records `(latency/throughput/resource estimate, confidence, required assumptions)`. Cache keys include every semantic/profile, candidate/layout/proof, alias/ABI/address-domain, component/allocator/environment, tool/part/clock and model dependency named in R010. Search workers use private immutable revisions/artifacts. A failed worker does not donate a partially verified candidate. Hard report constraints fail validation; soft preferences report actual achieved values. Physical routing/clock and external bandwidth remain measurements, never solver guarantees.

## Bounded research probes and evidence boundary

The standalone probe in the appendix was executed with local `python3` on 2026-10-01, exit 0. It uses only the standard library. It is a bounded model of the algorithms above, not production Spatial code or a test of xDSL, vendor semantics, HLS legality, arbitrary liveness, or source/builder capture. Its cases cover:

- Fair RR over 28 initial scheduler size/cursor states, including a forever-runnable low slot alongside task/resource/response actions.
- 54 queue/selector/cursor snapshots for two compound selectors plus a direct receiver; each selector belongs to one conflict set and only the committed proposal updates its resource cursor. Sustained three-way contention rotates winners `0,1,2` repeatedly.
- Cancellation injection in Captured/Reserved/Issued/Done, retaining issued completion and old-generation identity.
- Capacity-one producer/consumer interleaving yielding `[11,22]`.
- 144 small cyclic packed layouts with checked inverse and a whole-word packed update yielding `0xC3`.
- FIFOReg reset/consume availability and staggered multi-producer close with one outstanding send.
- Constructive wait-graph classification for delayed external ack, unknown model dependency and closed feedback with an unrelated open endpoint.
- Allocator W=4,N=33 charge17/span33; exact first-fit reuse with fresh identity; separate quota/address exhaustion; free-interval coalescing and zero-bit/zero-extent identity.

These finite checks detect concrete construction mistakes and provide implementer examples. They do not substitute for independent conformance fixtures, source/builder parity, adversarial model exploration, RTL stalls, synthesis, or board evidence. The checked transition tables and source event projection remain the production acceptance authority.

Reproduce by saving the appendix as `/private/tmp/spatial_state_readiness_probe.py` and running `python3 /private/tmp/spatial_state_readiness_probe.py`. The JSON distinguishes the model's evidence class and reports counts/traces. The representative HLS skeleton below is design text only and has not been compiled or synthesized.

## Representative manager/adapter emission skeleton

This illustrates the required concurrency boundary, stable IDs, and nonblocking manager behavior. Numeric type/helper names and port declarations come from the locked target/ABI profile. It deliberately omits no semantic protocol behind a stub: `step_task`, `commit_resource`, and `drain` are generated from the closed transition/PC tables defined above; their concrete per-resource implementations are required before emission eligibility.

```cpp
struct Request { word id, activation, generation, kind, address, data; };
struct Response { word id, activation, generation, value, error, visible; };

void manager(stream<Request>& req, stream<Response>& resp,
             stream<Request>& stop_adapter, Result& result) {
  Machine m = initialize_from_checked_invocation();
  while (!m.terminal_and_drained()) {
    // Staging buffers retain payloads; ready is not source queue occupancy.
    Response response;
    if (!m.response_buffer_full() && resp.read_nb(response))
      m.capture_response(response); // Validate matching obligation when processed.
    if (m.has_stable_pending_adapter_offer()) {
      Request offer = m.pending_offer();
      if (req.write_nb(offer)) m.record_external_issue(offer);
    }
    Action a = m.next_fair_enabled_action();
    switch (a.kind) {
      case TASK_STEP: m.step_task(a); break;
      case RESOURCE:  m.commit_or_step_resource(a); break;
      case RESPONSE:  m.process_response(a); break;
      case CLEANUP:   m.drain(a); break;
      case NONE:      m.retain_quiescent_state(); break;
    }
    // Runtime error/stop flags suppress new issues and retain old obligations.
  }
  // An explicit End command stops the owner adapter only after all responses drain.
  stop_adapter.write(m.adapter_end_command());
  result = m.terminal_result();
}

void dma_owner(stream<Request>& req, stream<Response>& resp,
               stream<Request>& stop_adapter, memory_port memory) {
  bool ended = false;
  while (!ended) {
    Request end;
    if (stop_adapter.read_nb(end)) { ended = true; }
    else {
      Request r;
      if (req.read_nb(r)) {
      // Exactly one owner, one request at a time. The owner may stall on memory;
      // manager remains a separate process and can run/drain all other tasks.
      Response s = perform_checked_bus_transaction(r, memory);
        resp.write(s); // Every issued request has exactly one matching completion.
      }
    }
  }
}

void top(memory_port memory, Result& result) {
  // Generated top obeys the selected profile's canonical DATAFLOW constraints.
  #pragma HLS DATAFLOW
  stream<Request> request, end;
  stream<Response> response;
  manager(request, response, end, result);
  dma_owner(request, response, end, memory);
}
```

A persistent profile instead exposes explicit start/stop/reset/result streams and uses its adopted top control protocol. A platform that cannot synthesize this concurrent owner arrangement must provide the named RTL transaction adapter/integration boundary or reject that hardware capability. A blocking central pointer access is not a substitute. Returned error/visibility/request ID behavior must exist in the real adapter; ordinary C pointer APIs that cannot expose required bus errors receive a more limited capability profile.

## Acceptance gates and remaining real inputs

Before reference support, require complete closed descriptors, source/builder normalized parity, canonical snapshot replay, R003/R008 discriminator traces, independent nontrivial helper/branch/loop/task compositions, exact active faults and committed prefixes, multiple producers/close, allocator address/fragmentation/reuse, and both fair witness and bounded alternate interleavings. Add disjoint-lock/channel progress and same-word RMW across DMA/reset to retain the previously repaired counterexamples.

Before target-plan support, check continuation/live-state layout; issue DAG; every memory map/inverse/port match; semantic capacity/admission/lifetime; component/interface records; complete fault/drain/response state machine; and required capabilities. The baseline must explain a missing route by operation/profile and source location. It cannot merely attach `verify later` to an emitted plan.

Before a hardware capability claim, lock release, device/platform, clock/ABI and concrete adapters; reproduce the emitted owner/manager topology on that release; test bounded/stalled/closed/reset/fault/cancel/duplicate-response cases with projected traces; inspect achieved schedule/resources and hard constraints; perform physical timing/board tests only where those properties are claimed. These actual tool/device results are legitimately future evidence. The target-neutral transition, continuation, allocator, memory construction and route-selection algorithms above do not depend on those measurements and can be reviewed now.

## Appendix: complete bounded probe

The code below is the complete standalone research probe, preserved here so an ephemeral `/private/tmp` path is not its only copy.

```python
"""Bounded research model, not a Spatial compiler or HLS support test."""
from dataclasses import dataclass, replace
from itertools import product
import json


def choose(cursor, enabled, size):
    for offset in range(size):
        index = (cursor + offset) % size
        if index in enabled:
            return index, (index + 1) % size
    return None, cursor


def fairness_probe():
    checked = 0
    for size in range(1, 8):
        for cursor in range(size):
            counts = [0] * size
            for _ in range(3 * size):
                index, cursor = choose(cursor, set(range(size)), size)
                counts[index] += 1
            assert counts == [3] * size
            checked += 1
    # Task 0 is forever-runnable; task 1 still runs, as do response/resource actions.
    cursor, trace = 0, []
    for _ in range(12):
        index, cursor = choose(cursor, {0, 1, 2, 3}, 4)
        trace.append(index)
    assert trace == [0, 1, 2, 3] * 3
    return {"states": checked, "mixed_action_trace": trace}


def compound_probe():
    # Endpoints 0,1 are selectors with fixed priority Q0,Q1. Endpoint 2 receives Q0.
    checked = 0
    for q0_len, q1_len, cursor0, cursor1 in product(range(3), range(3), range(3), range(2)):
        queues = [list(range(q0_len)), list(range(10, 10 + q1_len))]
        preferred = 0 if queues[0] else (1 if queues[1] else None)
        candidates = [set(), set()]
        if preferred is not None:
            candidates[preferred].update({0, 1})
        if queues[0]:
            candidates[0].add(2)
        cursors = [cursor0, cursor1]
        before_cursors = cursors[:]
        reservations = []
        for resource in range(2):
            winner, after_cursor = choose(cursors[resource], candidates[resource], 3 if resource == 0 else 2)
            if winner is not None:
                reservations.append((resource, winner, queues[resource][0], after_cursor))
        # Preferred-resource assignment puts a selector into only one conflict set.
        assert len({winner for _, winner, _, _ in reservations}) == len(reservations)
        assert len({resource for resource, _, _, _ in reservations}) == len(reservations)
        # The canonical witness commits one selected reservation then resnapshots.
        if reservations:
            resource, winner, token, after_cursor = reservations[0]
            before = [q[:] for q in queues]
            assert queues[resource].pop(0) == token
            cursors[resource] = after_cursor
            assert cursors[1 - resource] == before_cursors[1 - resource]
            assert sum(map(len, before)) - sum(map(len, queues)) == 1
        checked += 1
    # Sustained contention on one nonempty queue is RR, not selector priority starvation.
    cursor, winners = 0, []
    for _ in range(9):
        winner, cursor = choose(cursor, {0, 1, 2}, 3)
        winners.append(winner)
    assert winners == [0, 1, 2] * 3
    return {"states": checked, "contended_winners": winners}


@dataclass(frozen=True)
class CancelState:
    phase: str
    pending: int
    committed: int
    owned: bool
    generation: int
    cancel: bool = False


def cancel_probe():
    checked = 0
    for phase in ("Captured", "Reserved", "Issued", "Done"):
        state = CancelState(phase, int(phase == "Issued"), int(phase == "Done"), True, 7)
        state = replace(state, cancel=True)
        if phase in {"Captured", "Reserved"}:
            state = replace(state, phase="Abandoned", owned=False)
            assert state.committed == 0 and state.pending == 0
        elif phase == "Issued":
            assert state.pending == 1 and state.owned
            # Old activation's actual acknowledgement enables release; cancel does not.
            state = replace(state, phase="Done", pending=0, committed=1, owned=False)
        else:
            state = replace(state, owned=False)
        assert state.committed == int(phase in {"Issued", "Done"})
        assert not state.owned and not state.pending
        old_response_generation = state.generation
        restarted_generation = state.generation + 1
        assert old_response_generation != restarted_generation
        checked += 1
    return {"injection_phases": checked, "issued_obligations_retained": True}


def producer_consumer_probe():
    queue, producer_pc, consumer_pc, cursor, output = [], 0, 0, 0, []
    trace = []
    for _ in range(20):
        enabled = set()
        if producer_pc < 2 and len(queue) < 1:
            enabled.add(0)
        if consumer_pc < 2 and queue:
            enabled.add(1)
        action, cursor = choose(cursor, enabled, 2)
        if action is None:
            break
        if action == 0:
            queue.append((11, 22)[producer_pc])
            producer_pc += 1
            trace.append("send")
        else:
            output.append(queue.pop(0))
            consumer_pc += 1
            trace.append("receive")
    assert producer_pc == consumer_pc == 2 and output == [11, 22]
    assert trace == ["send", "receive", "send", "receive"]
    return {"output": output, "trace": trace}


def layout_probe():
    checked = 0
    for extent, banks, cells_per_word in product(range(1, 10), range(1, 5), range(1, 5)):
        # Cyclic word banking: packing precedes bank selection. Cell maps retain slices.
        mapping = []
        for index in range(extent):
            word, cell = divmod(index, cells_per_word)
            bank, row = word % banks, word // banks
            mapping.append((bank, row, cell * 4, cell * 4 + 4))
        assert len(set(mapping)) == extent
        for index, (bank, row, lo, hi) in enumerate(mapping):
            assert ((row * banks + bank) * cells_per_word + lo // 4) == index
            assert hi - lo == 4
        checked += 1
    # Physical-word update keeps both disjoint nibbles when one whole RMW owns the word.
    byte = 0
    for lo, value in ((0, 3), (4, 12)):
        byte = (byte & ~(15 << lo)) | (value << lo)
    assert byte == 0xC3
    return {"layouts": checked, "packed_update": hex(byte)}


def fifo_reg_close_probe():
    # Reset image is stored payload, not a valid token. Capacity is exactly one.
    payload, valid = 0, False
    assert not valid
    payload, valid = 7, True
    result, valid = payload, False
    assert result == 7 and not valid
    assert not valid  # A second read must fault/wait; it cannot repeat 7.
    payload, valid = 0, False
    assert not valid  # Reset does not synthesize a zero token.
    producers = {"p0": "Closed", "p1": "Open"}
    pending_sends = {"p0": 0, "p1": 0}
    queue = []
    def ended():
        return all(s == "Closed" for s in producers.values()) and not any(pending_sends.values()) and not queue
    assert not ended()
    producers["p1"], pending_sends["p1"] = "Closing", 1
    assert not ended()
    queue.append(2)
    pending_sends["p1"], producers["p1"] = 0, "Closed"
    assert not ended()
    assert queue.pop(0) == 2 and ended()
    return {"fifo_reg": "reset empty; one consume", "multi_producer_end": "only closed and drained"}


def wait_graph_probe():
    def classify(edges, start, open_roots, unknown_roots):
        todo, seen = [start], set()
        while todo:
            node = todo.pop()
            if node not in seen:
                seen.add(node)
                todo.extend(edges.get(node, ()))
        if seen & open_roots:
            return "WaitingEnvironment"
        if seen & unknown_roots:
            return "QuiescentUnknown"
        return "Deadlock"
    cycle = {"task": ["queue"], "queue": ["producer"], "producer": ["task"]}
    assert classify(cycle, "task", {"unrelated_external"}, set()) == "Deadlock"
    ack = {"task": ["ack"], "ack": ["external_response"]}
    assert classify(ack, "task", {"external_response"}, set()) == "WaitingEnvironment"
    assert classify(ack, "task", set(), {"external_response"}) == "QuiescentUnknown"
    return {"cases": 3, "unrelated_open_endpoint": "Deadlock"}


def allocator_probe():
    base, quota, arena_span, alignment = 0x1000, 100, 256, 1
    free_ranges, used, serial = [(base, base + arena_span)], 0, 0
    live = {}
    def alloc(count, width):
        nonlocal used, serial, free_ranges
        charge, span = (count * width + 7) // 8, count * ((width + 7) // 8)
        if charge > quota - used:
            return "QuotaExhausted"
        if span == 0:
            serial += 1
            live[serial] = (base, base, charge)
            used += charge
            return serial
        for index, (lo, hi) in enumerate(free_ranges):
            start = ((lo + alignment - 1) // alignment) * alignment
            if start + span <= hi:
                serial += 1
                pieces = ([(lo, start)] if lo < start else []) + ([(start + span, hi)] if start + span < hi else [])
                free_ranges[index:index + 1] = pieces
                live[serial] = (start, start + span, charge)
                used += charge
                return serial
        return "AddressSpaceExhausted"
    def free(handle):
        nonlocal used, free_ranges
        lo, hi, charge = live.pop(handle)
        used -= charge
        if hi > lo:
            free_ranges.append((lo, hi))
            merged = []
            for a, b in sorted(free_ranges):
                if merged and merged[-1][1] == a:
                    merged[-1] = (merged[-1][0], b)
                else:
                    merged.append((a, b))
            free_ranges = merged
    first = alloc(33, 4)
    second = alloc(1, 8)
    assert live[first] == (base, base + 33, 17)
    assert live[second][0] == base + 33  # Not base+17.
    free(first)
    reused = alloc(33, 4)
    assert reused != first and live[reused][0] == base
    free(second)
    free(reused)
    assert free_ranges == [(base, base + arena_span)] and used == 0
    quota = 16
    assert alloc(33, 4) == "QuotaExhausted"
    quota, free_ranges = 100, [(base, base + 32)]
    assert alloc(33, 4) == "AddressSpaceExhausted"
    empty = alloc(0, 4)
    zerobit = alloc(33, 0)
    assert empty != zerobit and used == 0
    assert live[empty] == live[zerobit] == (base, base, 0)
    return {"four_bit_33_cells": {"charge": 17, "span": 33}, "address_reuse_fresh_id": True,
            "quota_vs_address_failure": "distinct", "zero_bit_logical_identity": True}


if __name__ == "__main__":
    print(json.dumps({"evidence": "bounded research model only", "fairness": fairness_probe(),
                      "compound": compound_probe(), "cancel": cancel_probe(),
                      "capacity_one": producer_consumer_probe(), "layout": layout_probe(),
                      "fifo_reg_close": fifo_reg_close_probe(), "wait_graph": wait_graph_probe(),
                      "allocator": allocator_probe()},
                     indent=2, sort_keys=True))

```
