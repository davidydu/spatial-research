---
type: deep-dive
title: "Independent protocol and HLS review"
topic: independent-python-protocol-and-hls-review
project: spatial-python
session: 2026-09-30
status: research-conclusion
source_files: []
source_notes:
  - "[[PY-R003 - Control Memory and Effects]]"
  - "[[PY-R008 - Advanced State and Communication Protocols]]"
  - "[[PY-R009 - HLS Boundary and Control Lowering]]"
  - "[[PY-R010 - Memory Scheduling and Design Space Exploration]]"
  - "[[30 - Python State and Protocol Contract]]"
  - "[[40 - Python Compiler and HLS Contract]]"
feeds_spec: []
---

## Scope and result

This review independently examines the six non-authored documents listed above, including the manager's progress-refinement and model-registry repairs. It evaluates proposed contracts and lowering obligations, not an implemented simulator/compiler, vendor run, or original-backend equivalence. Counterexamples below are designed expectations; none is reported as an executed hardware failure. Only this review note was edited.

The reviewed architecture preserves logical backing identity, capacity, order, admission, and outstanding obligations through an explicit implementation plan. Three concrete findings were reported to the manager, repaired on disk, and independently reread. No material finding from this review remains open. These findings concern specific transitions rather than general objections to HLS.

## Findings and repair verification

**P01 — keyed locks cannot become a global critical-section lock merely because no throughput is requested. Closed after repair.** Task A acquires key A and waits for a token. Task B acquires disjoint key B, sends that token, and releases. The keyed source can progress; a single lock held through A's whole region blocks B and introduces deadlock. R008 previously conditioned serialization on concurrency/throughput requirements alone. The manager added a progress/refinement requirement, the exact counterexample, and the distinction between serial request arbitration and serializing entire ownership regions. Verified in [[PY-R008 - Advanced State and Communication Protocols|R008]]. A future test must retain both disjoint protected domains and the blocking channel, rather than replace the section with a nonblocking increment.

**P02 — retaining an inert view must not silently strengthen deallocation policy. Closed after repair.** Consider `v=A.view(); free(A); allocate(A); read(v)`. R008 invalidated old views and required a stale-generation failure; the condensed state contract formerly required no live dependent views at free, ambiguously rejecting the program earlier. Both now distinguish stored inert descriptors from active ownership/read/transfer leases. Free drains active obligations and invalidates the old generation; retaining a descriptor alone does not prevent free. Subsequent stale use faults or receives a statically provable stale-use diagnostic. Address reuse never revives it. Verified in [[PY-R008 - Advanced State and Communication Protocols|R008]] and [[30 - Python State and Protocol Contract|state contract]].

**P03 — packed-word read-modify-write must serialize the entire sequence, not only individual writes. Closed after repair.** Two disjoint four-bit logical cells initially share byte zero. Concurrent updates to values 3 and 12 can both read zero, then write `0x03` and `0xC0`, losing one update. Required final byte is `0xC3`. Logical disjointness and serialized RAM write-port issue are insufficient. R010 now requires atomic masked update, forwarding/combining, or protection spanning the whole physical-word read/merge/write. All task/DMA/replica/reset/init updaters participate, and preservation/progress remain required. Verified the new rule at [[PY-R010 - Memory Scheduling and Design Space Exploration|R010]] and matching M11 at R010:151. This closes a proposed-lowering gap; it is not evidence of tested RTL correctness.

## Existing repairs and decisive acceptance cases

The manager's **progress repair is verified** in [[PY-R009 - HLS Boundary and Control Lowering|R009]], state contract:28, and compiler contract:75. A capacity-one producer sends 11 then 22 while its consumer receives twice. An implementation emitting only the first send and remaining busy forever fails, although its event prefix is legal. Completion/deadlock/fairness obligations distinguish finite stalls, internal infinite stuttering, and legitimate indefinite external waiting. Fixed-priority starvation remains permitted where the source explicitly selects it; it is not accidentally upgraded to fair arbitration.

The **model-registry repair is verified** in [[PY-R008 - Advanced State and Communication Protocols|R008]], state contract:57, and compiler contract:65. A model reading a later ambient host `gain` would otherwise change cached meaning. IR now contains versioned IDs/code/dependency hashes, and the reviewed registry uses explicit invocation state/environment resources. Missing or changed dependencies diagnose/invalidate; registry admission remains a declared trust boundary, not an automatic proof of arbitrary Python purity.

The following cross-document checks are coherent and should remain mandatory during implementation:

| Discriminator | Preserved requirement |
|---|---|
| Capacity-one channel, atomic vector send of two | Permanent capacity error; replacing it with scalar sends changes the operation. Independent scalar producer/consumer interleavings remain legal. |
| One merge input, capacity one, frame count two, vector output two | Commit first consume into the packer, freeing space for the second token; publish atomically afterward. Requiring both tokens resident first introduces deadlock. Cancellation traces abandoned staged tokens. |
| Two publication credits reduced to one physical slot | Producer publishes twice before signaling its consumer. Shrinking storage can block before the signal; R008/R010 require progress/refinement proof or rejection. Extra physical slots retain semantic credit limits. |
| `stop=true` followed by `dst=7` | Graceful stop completes the admitted body; cancel before the store may suppress it. Window W and refill checkpoints are semantic. II/unroll changes cannot silently alter the admitted/drained set. |
| Snapshot overlap and duplicate scatter | Copy `[1,2,3]` rightward produces `[1,1,2,3]`; writes to address 2 with values 7 then 9 finish at 9. Physical tiling, replicas, and outstanding transactions preserve that order. |
| Cancel after DMA issue or external acceptance | Drain or a declared abort protocol remains owed; committed effects survive. Restart cannot reuse backing/credits while old completions remain outstanding. |
| Runnable forever task with lower task ID | Canonical scheduling must still satisfy declared weak fairness; ID tie-breaking cannot starve another continuously runnable task. |

R003's ordered effects, active-only faults, aliases, and assignment sequencing integrate with R008's richer protocol rules. R009 requires a concrete concurrent/component route and synthesizable error/drain behavior. R010 rechecks every candidate's layout, ports, replicas, ownership, semantic credits, and DMA geometry; it distinguishes hard requirements from preferences. None treats successful unlimited C simulation as bounded hardware evidence.

## Remaining implementation gate

Retain all three repaired counterexamples. Convert the discriminators into independent state/event expectations and bounded adversarial schedules, with source/builder parity and stalled-interface RTL checks. The proposed contracts are coherent for this reviewed foundation; their acceptance does not establish universal liveness, arbitrary layout proofs, target resource fit, or achieved II. Unknown obligations still require a proved preserving fallback or capability diagnostic.
