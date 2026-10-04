---
type: research
title: "Protocol policies and observable boundary cases"
project: spatial-python
date: 2026-10-03
status: research-conclusion
adoption_status: proposed
implementation_status: not-implemented
---

## Question and evidence boundary

Which remaining protocol choices should the Python proposal make explicit, and which review suggestions would change its meaning?

This study follows [[09 - Fable Design Review]] at research commit `a06ccfd`. It compares concrete policies before revising the owning contracts. The current user request authorizes iterative research and proposed-design improvements with Codex and Fable; professor adoption and production implementation remain separate. The proposed transitions below were cross-reviewed. They are not an implemented Spatial simulator or hardware result.

## Proposed choices

| Boundary | Recommended policy | Strongest alternative and tradeoff |
|---|---|---|
| Default channel resource selection | Retain stateful round robin over stable endpoint IDs, with one shared admission cursor and one accepted atomic request per resource epoch | A general bounded-fairness class admits more arbiters but also more observable token orders. That is a separate semantic profile, not an optimization of an exact selector |
| Task scheduling | A weakly fair scheduler chooses a replayable allowed execution; unrelated task steps need not match one canonical witness | A mandatory total task order simplifies replay but would impose extra program ordering and unnecessarily constrain hardware |
| All-false captured conditions of a consuming queue selector | Fault immediately after condition capture, without queue observation, dequeue, wait registration or pointer movement | Permanent wait is representable, but cannot become ready without a new condition evaluation. Returning a fabricated value would be incorrect |
| All-false vector mask | Preserve the existing no-op: no queue observation or cursor movement; a receive returns an all-invalid MaskedVec | Treating it like a consuming queue selector confuses different result types and operations |
| Empty enabled fold into a destination | Evaluate/snapshot the seed and perform its required validity reads, then return it without destination write/publication | Writing the unchanged value creates a distinct observable event and extra ordering work. Disabled invocation remains different: it evaluates nothing |
| Bare register declaration | Use a registered typed-zero reset image when that type has one; otherwise require an explicit supported reset value | Making every bare register uninitialized adds a new migration difference; inventing an unchecked all-zero bit pattern is invalid for types without a zero image |
| Lowered protocol verification | Execute the finite generated ProtocolPlan transition records in a Python plan runner and compare their semantic-event projection before vendor testing | Going directly to vendor simulation makes it harder to distinguish a planning error from an emission or adapter error |

These choices preserve strict fault behavior and the distinction between ordered queues and communicating channels. They do not make arbitrary host Python executable inside kernels.

## Resource selection is separate from task scheduling

R008 names a stateful round-robin channel default. The state blueprint describes a canonical task scheduler and a resource admission cursor. These are different layers. A task scheduling witness must not be used as evidence that a named resource selector may choose arbitrary winners.

The proposed resource policy records an ordered endpoint set and retained cursor `p`, initially zero. At a grant snapshot, filter pending requests by their declared readiness and search that set cyclically from `p`. After a successful atomic request from endpoint `j`, advance to the following endpoint. A failed, infeasible, disabled or cancelled request does not advance the cursor. A compound read/write batch is one explicit request; the runtime cannot merge independent pending operations merely to create progress.

Different task/environment arrival orders can still produce different legal global traces. A hardware arbiter must preserve selection for equivalent visible request histories and progress assumptions. It cannot substitute fixed priority or LRU just because both can be described as fair in some workloads. A separately named arbitration policy can be researched later with its own trace contract and migration examples.

An abstract grant epoch is not a hardware clock. Hardware may commit several operations in one clock when their projected events can be ordered as an allowed sequence of resource transitions, including cursor updates, capacity, old-token behavior and every intervening observable effect. For example, from a queue containing an old token, one dequeue and one enqueue may share a physical clock if their projected order is legal. This does not permit an empty explicit same-request batch to consume its own new push. Thus one abstract grant per resource step does not require one physical request per cycle. A blanket rejection of same-cycle independent enqueue/dequeue would be incorrect; a blanket permission based only on fairness would also be incorrect.

The distinction does not promise clock-cycle latency or fairness for intermittently ready requests. Explicit fixed-priority selectors retain their permitted resource starvation even while task execution is weakly fair.

## Disabled operations and selectors

An enclosing disabled region evaluates none of its inner operands. An enabled vector request evaluates its operands normally; an all-false lane mask then performs no resource action. Its MaskedVec result has no valid payload lane.

A consuming queue selector (fixed-priority, caller-index rotation or stateful round-robin receive) promises one ordinary dequeued value. Its supplied conditions are evaluated once in source order and retained while pending. If all are false, no subsequent change in queue occupancy can enable it. The proposed outcome is a named `NoEnabledCandidate` language fault at that point, before resource occupancy observations, with the captured-condition effects already committed. An explicit source retry loop can request a later reevaluation. If at least one condition is true but all enabled queues are empty, the existing ordered-fault/communicating-wait rule applies. Structural arity/type checks still precede execution.

The current state-blueprint instruction to remove all “all-false operations” is too broad to serve both cases. The revised rule must identify vector masks and consuming queue selectors separately.

Pure `priority_select(flags,values,default)` and `one_hot_select` are a separate value-operation family. With no true flag they keep their explicit default (for example, 7), or the separately requested empty-fault policy. They do not acquire queue requests and are not governed by NoEnabledCandidate. This scope correction came from independent Codex cross-review.

## Empty folds and initialization

The empty-map case still validates the enabled operation and snapshots each selected initialized destination cell in destination-index order. It invokes no mapper, performs no combines, and emits no destination writes or publication. An invalid seed can therefore fault even with an empty map. When the destination has zero cells but the map is nonempty, every active mapper still runs in order, including its effects and faults, with zero destination accesses. These are different dimensions of emptiness.

For a bare `Reg[T]`, the selected default is the type registry's `ZeroImage(T)`, not an arbitrary host constructor. Bool uses false, numeric formats use exact positive zero, raw bits use zero, and admitted aggregates recursively use registered element images. Private typed-cell Index uses exact integer zero. A private MaskedVec image has every lane invalid and a recursively registered canonical zero payload; storing or loading it preserves the validity guards and grants no Bits/materialization capability. A missing element zero image still requires an explicit admitted reset. Private typed-cell storage is distinct from byte-backed host memory and packed payload slots; hardware needs a proved finite Index range and a registered mask-preserving layout, or reports scoped unsupported. A type without a valid registered image must have an explicit supported reset or receive a source diagnostic. The checked allocation records the actual typed reset image, so later passes do not rediscover a default from ambient configuration. This does not make zero a reduction identity.

The original register constructor uses `zero[A]`, while an explicit constructor preserves its supplied reset (`spatial@e7a8f2f:src/spatial/lang/Reg.scala:48-57`, inspected again on 3 October). This is migration evidence, not authority for every generic Python descriptor. SRAM retains explicit uninitialized cells; FIFOReg retains an initially empty availability token even when its stored bits have a reset image.

## Lowered-plan execution gate

The state blueprint already gives ProtocolPlan transitions a semantic-event projection. The proposed refinement is to make those same finite transition records executable in Python before C++ emission. The runner consumes explicit inputs/readiness, advances bounded internal state, records commits, and emits the declared semantic events. It does not parse a second source language or invent new arithmetic rules.

The preceding semantic-region-to-ExecutionProgram lowering needs its own check because both reference execution and planning can share its mistakes. The proposal adds lowering-table coverage, frame/result/token checks and source-event correspondence. For the first ordered subset, a small direct recursive region evaluator is a fixture oracle against the continuation executor; it is not a second supported production simulator. Assignment order, lazy branch effects and nested call/loop returns are the initial discriminators. Queue cases join when their semantic slice exists. Deterministic construction uses checked semantic records; serializing and reparsing them on every run is not required.

This check can catch a lost lane mask, premature publication, incorrect credit return or added internal deadlock before vendor tools enter the path. Shared numeric helpers remain a shared implementation dependency; independent arithmetic vectors are still necessary. Passing plan execution does not establish vendor scheduling, RTL handshakes, timing or hardware resource fit.

## Validation and iteration status

The required discriminators are: competing continuously ready endpoints; a blocked request and unchanged cursor; false scalar conditions versus false vector lanes; empty enabled fold versus disabled invocation; empty destination with an effectful mapper; valid registered zero versus a descriptor lacking one; and a lowered-plan trace mutation that loses a mask or publication event.

The standalone transition probe executed 642 round-robin readiness/cursor snapshots and 15 boundary examples. Expected seed/condition traces are stated separately from the transition functions. A same-history discriminator (prior grants 2,1,0, then all ready) gives round-robin winner 1 versus LRU winner 2. A small projection mutation loses a lane mask and fails its expected trace. These are bounded executable examples of proposed rules, not an implemented scheduler, generated ProtocolPlan, liveness proof or hardware test. The refinement archive preserves the script and JSON results. Independent Codex and final Fable review found these policies coherent after the selector-scope and graceful-stop clarifications recorded in [[11 - Design Refinement Iterations]]. They remain proposed rules; none of these probes implements the full runner or grants professor adoption.
