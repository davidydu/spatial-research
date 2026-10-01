---
type: deep-dive
title: "PY-R003 — Control, memory, and effects"
topic: python-control-memory-effects
project: spatial-python
session: 2026-09-30
status: research-conclusion
source_files:
  - "spatial@e7a8f2f:test/spatial/tests/feature/control/FIFOBranch.scala:9-35"
  - "spatial@e7a8f2f:test/spatial/tests/feature/control/ReduceTiny.scala:7-37"
  - "spatial@e7a8f2f:test/spatial/tests/ee109/Lab1Part2DramSramExample.scala:21-43"
  - "spatial@e7a8f2f:src/spatial/lang/control/Control.scala:9-72"
  - "spatial@e7a8f2f:src/spatial/lang/control/ReduceClass.scala:37-96"
  - "spatial@e7a8f2f:src/spatial/node/Control.scala:33-143"
  - "spatial@e7a8f2f:src/spatial/node/HierarchyAccess.scala:17-137"
  - "spatial@e7a8f2f:src/spatial/node/HierarchyMemory.scala:9-98"
  - "spatial@e7a8f2f:argon/src/argon/Effects.scala:20-96"
  - "spatial@e7a8f2f:argon/src/argon/static/Staging.scala:195-261"
  - "spatial@e7a8f2f:argon/src/argon/schedule/SimpleScheduler.scala:18-30"
  - "spatial@e7a8f2f:src/spatial/flows/SpatialFlowRules.scala:317-372"
  - "spatial@e7a8f2f:src/spatial/transform/unrolling/ReduceUnrolling.scala:15-123"
  - "spatial@e7a8f2f:src/spatial/codegen/scalagen/ScalaGenController.scala:14-247"
  - "spatial@e7a8f2f:src/spatial/codegen/scalagen/ScalaGenFIFO.scala:18-52"
  - "spatial@e7a8f2f:emul/src/emul/Counter.scala:10-53"
  - "spatial@e7a8f2f:emul/src/emul/OOB.scala:19-38"
  - "spatial@e7a8f2f:src/spatial/executor/scala/memories/ScalaQueue.scala:8-25"
  - "spatial@e7a8f2f:src/spatial/codegen/chiselgen/ChiselGenCommon.scala:212-279"
  - "spatial-rs@eb49d8b:docs/language-spec.md:385-420"
  - "spatial-rs@eb49d8b:docs/language-spec.md:506-593"
  - "spatial-rs@eb49d8b:docs/language-spec.md:722-924"
  - "https://docs.python.org/3.14/reference/expressions.html#evaluation-order (accessed 2026-09-30)"
  - "https://docs.python.org/3.14/reference/simple_stmts.html#augmented-assignment-statements (accessed 2026-09-30)"
feeds_spec:
  - "[[30 - Python State and Protocol Contract]]"
---

## Conclusion and authority

Propose a Python semantic model with lexical regions, explicit mutable-object identities, path-sensitive effects, ordered exactly-once contribution evaluation, and a separate representation for communicating tasks. Keep functional execution, scheduling requests, and scheduled hardware execution distinct. An implementation may optimize the first only under a semantic preservation obligation; a serial replay does not establish the behavior of the third.

The immediate discriminating case is [[PY-E001 - Initial Example Corpus|E3]]. Original Spatial permits a FIFO-consuming reduction body, so a Python rule that allows only read-only reduction bodies would reject an original regression case. The relevant distinction is between the contribution region's effects and the pure combination operation's numerical order. Original source: `spatial@e7a8f2f:test/spatial/tests/feature/control/FIFOBranch.scala:16-27`; earlier Rust restriction: `spatial-rs@eb49d8b:docs/language-spec.md:905-910`.

This is a proposed conclusion for PY-Q002, PY-Q004, and the control/effect part of PY-Q005 in [[02 - Python Open Questions]]. It does not adopt an API, implement a compiler, settle arithmetic reassociation, or establish HLS support. [[PY-R001 - Programming Model Study]] supplies the compared surfaces. This note supplies their candidate common effect contract and identifies where original behavior, the earlier Rust redesign, and Python recommendations differ.

## Evidence boundary

The original checkout was read at full revision `e7a8f2f7f776dd0c5ac7fc03f16b3ed4d97021f0`; the Rust checkout was read at `eb49d8bc47bea46c83a7eb26f6a244f6303eebcb`. Citations use the repository's seven-character convention. Relevant original specification pages were consulted for navigation: control, scheduling, effects/aliasing, memory, Scalagen controllers, and FIFO simulation. Claims below were then checked directly against source. Original specification prose calling Scalagen normative is historical evidence, not authority to copy every simulator choice into Python.

No original application, compiler, optional Scala executor, hardware simulation, or Python Spatial compiler was run for this study. Expected Spatial values and traces are calculations under stated rules. The only execution was a small language-only assignment-order probe under installed CPython 3.14.5, described below; it is not a compiler prototype or Spatial conformance run. “Original source” means inspected constructors, transforms, and emitters; it does not mean a measured generated artifact. “Earlier Rust design” means the checked-in normative document, whose own status table marks general reference/effect rules and the obligation calculus Specified: `spatial-rs@eb49d8b:docs/language-spec.md:1114-1115`.

## What original Spatial actually records

### Effects and aliases precede scheduling

Original source. Argon effects contain flags for uniqueness, motion barriers, simple/global effects, allocation, and possible exceptions, together with mutable read/write sets and dependency records. Writes, allocation, and possible exceptions prevent the ordinary idempotence/CSE classification; reading alone does not. Effect composition unions read/write sets, with separate treatment of allocation mutability. These are static summaries, not instructions to execute every summarized branch. Sources: `spatial@e7a8f2f:argon/src/argon/Effects.scala:20-50`, `spatial@e7a8f2f:argon/src/argon/Effects.scala:77-96`.

Original source. A dequeue is a reader with a write effect on its queue; an enqueue is a writer. Status observations and ordinary memory reads acquire mutable-input read effects during staging. `computeEffects` propagates writes through aliases and adds mutable reads before finding dependencies. This makes `isEmpty` followed by dequeue a state-dependent computation, and makes two dequeues mutations even if their returned values are unused. Sources: `spatial@e7a8f2f:src/spatial/node/HierarchyAccess.scala:17-21`, `spatial@e7a8f2f:src/spatial/node/HierarchyAccess.scala:65-81`, `spatial@e7a8f2f:src/spatial/node/HierarchyAccess.scala:115-137`, `spatial@e7a8f2f:argon/src/argon/Op.scala:100-104`, `spatial@e7a8f2f:argon/src/argon/static/Staging.scala:230-261`.

Original source. Default block scheduling preserves the surviving source-ordered statement vector and performs reverse liveness-based DCE only on idempotent statements. A block summary removes reads/writes on allocations local to the scope from its external summary, while retaining the internal effect records. Thus “no external mutation” does not imply an internally empty body. Sources: `spatial@e7a8f2f:argon/src/argon/schedule/SimpleScheduler.scala:18-30`, `spatial@e7a8f2f:argon/src/argon/schedule/Scheduler.scala:14-25`.

Original source. Alias hints distinguish equal results, contained objects, extracted objects, and copied containers, and write propagation follows alias metadata. Dense and sparse memory views explicitly alias their underlying memories. Spatial enables mutable aliases in its settings, overriding Argon's default prohibition. A Python memory view must therefore retain backing-object identity; treating each view as fresh storage would change the program. Sources: `spatial@e7a8f2f:argon/src/argon/Op.scala:48-98`, `spatial@e7a8f2f:src/spatial/node/HierarchyMemory.scala:48-63`, `spatial@e7a8f2f:src/spatial/node/HierarchyMemory.scala:81-98`, `spatial@e7a8f2f:src/spatial/Spatial.scala:596-598`.

One source-reading caution matters here. The comments over `effectDependencies` describe most-recent hazards, but the implementation scans `state.impure.filter` and uses `find`; the staging vector is appended with `:+=`. This study relies on the presence of hazard dependencies and retained statement order, not an unverified claim that this code always selects the last preceding writer. Sources: `spatial@e7a8f2f:argon/src/argon/static/Staging.scala:120-129`, `spatial@e7a8f2f:argon/src/argon/static/Staging.scala:195-226`.

### Controllers are regions plus schedule facts

Original source. `Foreach` binds symbolic iterators and stages one body. `Reduce` records contribution, accumulator load, combine, and accumulator store regions, plus separate identity and fold fields. FSM records separate condition, action, and next-state regions. This region structure is useful for Python regardless of source capture versus a builder. Sources: `spatial@e7a8f2f:src/spatial/lang/control/ForeachClass.scala:26-32`, `spatial@e7a8f2f:src/spatial/lang/control/ReduceClass.scala:37-52`, `spatial@e7a8f2f:src/spatial/lang/control/FSM.scala:18-23`, `spatial@e7a8f2f:src/spatial/node/Control.scala:57-117`.

| Controller | Original represented fact | Generated Scalagen behavior | Python recommendation |
| --- | --- | --- | --- |
| `Sequential` | User schedule `Sequenced`; ordinary unit body or directives for counted controllers | Executes emitted bodies without modeling cycles | Ordered regions and explicit completion barriers |
| `Pipe` | User schedule `Pipelined` and optional requested II | Uses the same functional body emission for unit controllers | Preserve dependence order; record a schedule request separately |
| `Parallel` | `ParallelPipe`; flow assigns `ForkJoin` | Emits its body with `gen(func)` | Preserve children as a fork/join task group; serial replay only for proven independent effects |
| `Foreach` | Counter chain and bound body | Unrolled counters expose lane values and valid bits | Logical domain plus lane groups, masks, and effect obligations |
| `Reduce` / `Fold` | Contribution, combine, load/store, identity and fold fields | Executes the transformed unrolled body | Separate contribution effects from numeric combination topology |
| FSM | Start, condition, action, next-state regions | Start once; condition, action, next-state, state assignment repeatedly | Preserve that functional sequence, with a distinct schedule/liveness contract |

Sources for the table: `spatial@e7a8f2f:src/spatial/lang/control/Control.scala:22-57`, `spatial@e7a8f2f:src/spatial/lang/control/Parallel.scala:9-12`, `spatial@e7a8f2f:src/spatial/lang/control/CtrlOpt.scala:18-25`, `spatial@e7a8f2f:src/spatial/flows/SpatialFlowRules.scala:331-367`, `spatial@e7a8f2f:src/spatial/codegen/scalagen/ScalaGenController.scala:180-207`, `spatial@e7a8f2f:src/spatial/codegen/scalagen/ScalaGenController.scala:224-235`.

Original source. Bare `Foreach` and `Reduce` are not universally sequenced controllers. Flow rules choose Pipelined for otherwise-unscheduled controls other than Accel/UnitPipe, then collapse single controls and qualifying single-child outer controls to Sequenced. The metadata accessor's Sequenced fallback alone does not describe the actual normal flow. ParallelPipe is explicitly ForkJoin. Sources: `spatial@e7a8f2f:src/spatial/flows/SpatialFlowRules.scala:331-367`, `spatial@e7a8f2f:src/spatial/metadata/control/package.scala:193-219`.

Original source. Full/partial unrolling substitutes lanes and may produce UnitPipe, UnrolledForeach, or ParallelPipe compositions. Reduction unrolling evaluates mapped values into a reduction tree and separates first-iteration seed behavior from later accumulator combination. An explicit register reset is not automatically a contribution or fold seed. These are compiler transformations, not evidence that all original reductions evaluate a strict Python left fold. Sources: `spatial@e7a8f2f:src/spatial/transform/unrolling/ForeachUnrolling.scala:21-84`, `spatial@e7a8f2f:src/spatial/transform/unrolling/ReduceUnrolling.scala:55-79`, `spatial@e7a8f2f:src/spatial/transform/unrolling/ReduceUnrolling.scala:106-123`, `spatial@e7a8f2f:src/spatial/transform/unrolling/ReduceUnrolling.scala:152-167`, `spatial@e7a8f2f:src/spatial/transform/unrolling/ReduceUnrolling.scala:201-223`.

## Following the two discriminating examples

### FIFOBranch: original source to simulator operations

Original source. The fixture creates FIFO1/FIFO2 of depth 128, fills them with indices over two runtime counts, then reduces over their summed count. The contribution chooses FIFO2 only when FIFO1 is empty. It uses `Reduce(Reg[Int])`, not a constant-identity reduction. Its host reference computes two array sums, and its supplied runtime counts are 13 and 25. Sources: `spatial@e7a8f2f:test/spatial/tests/feature/control/FIFOBranch.scala:5-6`, `spatial@e7a8f2f:test/spatial/tests/feature/control/FIFOBranch.scala:9-35`.

Original source chain:

1. Each enqueue/dequeue is staged as an effectful memory access; `isEmpty` is a status observation: `spatial@e7a8f2f:src/spatial/lang/FIFO.scala:16-20`, `spatial@e7a8f2f:src/spatial/lang/FIFO.scala:31-56`.
2. The explicit-accumulator overload records neither an identity nor fold initialization, while the default Reg constructor supplies a zero reset value: `spatial@e7a8f2f:src/spatial/lang/control/ReduceClass.scala:78-87`, `spatial@e7a8f2f:src/spatial/lang/Reg.scala:48-57`.
3. Hardware `IfThenElse` becomes Switch/SwitchCase with branch enables. Flattening/motion is conditional on statements being enable-free and idempotent; a dequeue does not meet that test: `spatial@e7a8f2f:src/spatial/transform/SwitchTransformer.scala:44-84`, `spatial@e7a8f2f:src/spatial/util/package.scala:11-18`, `spatial@e7a8f2f:src/spatial/node/HierarchyAccess.scala:78-81`.
4. Unrolling maps FIFODeq/FIFOEnq into banked access nodes carrying enable sets, and mapped reduction values feed the combine: `spatial@e7a8f2f:src/spatial/transform/unrolling/MemoryUnrolling.scala:509-538`, `spatial@e7a8f2f:src/spatial/transform/unrolling/ReduceUnrolling.scala:106-119`.
5. Scalagen emits lazy `if`/`else if` selected case bodies and a runtime `isEmpty` observation. Banked dequeue executes enabled lanes in the emitted lane sequence, consuming only when nonempty; otherwise it returns invalid data: `spatial@e7a8f2f:src/spatial/codegen/scalagen/ScalaGenController.scala:209-219`, `spatial@e7a8f2f:src/spatial/codegen/scalagen/ScalaGenController.scala:239-247`, `spatial@e7a8f2f:src/spatial/codegen/scalagen/ScalaGenFIFO.scala:18-20`, `spatial@e7a8f2f:src/spatial/codegen/scalagen/ScalaGenFIFO.scala:33-44`.

This supports lazy consuming branches and the accumulator/identity distinction. It does not prove a universal generated cycle trace, the final controller schedule after every pass, or the behavior of modified parallel-lane variants. No generated IR was captured here.

### Precise proposed E3 effect trace

Proposed Python rule. For the corpus comparison, use an ordered reference domain: each fill region completes, then contribution indices run in increasing order and complete their selected effects exactly once. Record events as `(ordinal, region, logical_iteration, object_id, operation, value, before, after)`. `before`/`after` record queue length or register state; branch events record the observed predicate and chosen region. This trace has no cycle field. A later scheduled trace adds clock/handshake information rather than pretending the ordinal is time.

For counts `a=13`, `b=25`, the following is the exact schema of the proposed trace; the indexed rows expand to individual events:

| Phase | Indexed event sequence | State transition |
| --- | --- | --- |
| Allocate | Allocate Q1(128), Q2(128), A(reset=0) | Q1=[], Q2=[], A=0 |
| Fill Q1 | For `j=0..12`: `Produce(Q1,j)` | Length `j -> j+1`; contents become `[0,..,12]` |
| Fill Q2 | For `j=0..24`: `Produce(Q2,j)` | Length `j -> j+1`; contents become `[0,..,24]` |
| Reduce `k=0..12` | `ObserveEmpty(Q1)=false`; select else; `Consume(Q1)=k`; `Yield(k)`; seed/combine A | Q1 length `13-k -> 12-k`; Q2 remains 25 |
| Reduce `k=13..37` | `ObserveEmpty(Q1)=true`; select then; `Consume(Q2)=k-13`; `Yield(k-13)`; combine A | Q1 stays 0; Q2 length `38-k -> 37-k` |
| Complete | Publish reduction result; `Write(result,378)` | Both queues empty; A/result=378 |

The reference arithmetic here is ordinary exact addition over these small values. The first nonempty no-identity contribution seeds A; the initial register zero is not an additional contribution. A after index `k<13` is `k*(k+1)/2`; A after `k>=13`, with `j=k-13`, is `78+j*(j+1)/2`. At `k=12`, FIFO1's observation is false while its length is 1; after its consume length is 0. At `k=13`, the observation becomes true and FIFO2 supplies 0. There are exactly 38 produces, 38 empty observations, 38 selected consumes, and 38 contributions. The untaken branch contributes no consume event.

This trace is proposed reference semantics, not a measured original run. The source-derived expected final sum is 378. Draining Q2 first and Q1 second would produce the same sum and final lengths, but violate the selected branch sequence. Therefore final sums and final queue lengths alone are insufficient acceptance evidence.

For general nonnegative counts within capacity, the relation before contribution `k`, `0 <= k <= a+b`, is `len(Q1)=max(a-k,0)` and `len(Q2)=b-max(k-a,0)`. For `k<a+b`, either Q1 is nonempty or Q1 is empty and Q2 is nonempty. This is a proposed loop invariant, not a hardcoded FIFOBranch recognizer. Independent occupancy intervals followed by a branch join may lose the necessary correlation; the checker needs a relational proof, an explicit reusable precondition/guard, or a declared dynamic-check execution capability. It must report an unsupported proof rather than claim that every runtime-count FIFO loop is unsafe.

The supplied fixture does not decide empty no-identity reduction behavior. With `a=b=0`, the original host gold uses array reductions and is itself not a useful empty-domain oracle. Python should require a nonempty-domain precondition for a no-identity reduction, or an explicit empty-result alternative. An identity-bearing reduction can instead return its identity, subject to the separately reviewed numeric contract. Source boundary: `spatial@e7a8f2f:test/spatial/tests/feature/control/FIFOBranch.scala:21-31`; original no-identity field selection: `spatial@e7a8f2f:src/spatial/lang/control/ReduceClass.scala:78-87`.

### ReduceTiny: ordering without consuming state

Original source. A 1×16 SRAM is allocated, sixteen cells are written, then the contribution region reads `(0,i)` and the reduction result is written to an output. The constant overload records the reduction identity separately from fold initialization. Sources: `spatial@e7a8f2f:test/spatial/tests/feature/control/ReduceTiny.scala:7-15`, `spatial@e7a8f2f:src/spatial/lang/control/ReduceClass.scala:55-62`.

Proposed Python trace. Allocate V with sixteen uninitialized cells; execute `Write(V[0,i],i)` for each `i=0..15`; establish fill completion; execute sixteen `Read(V[0,i])` and contribution events; execute pure combines under the chosen numeric topology; publish 120 and write the output. The crucial obligation is that the fill completes before the reduction observes its cells. A controller boundary alone is not enough if a later scheduler overlaps dependent regions without preserving that obligation.

The sum 120 does not distinguish left fold from tree reduction, just as 378 does not establish FIFO branch consumption order. Initialization/bounds checks, trace shape, and reduction arithmetic must be checked separately. Neighboring `ReduceAccumTiny` provides explicit-register and `par 2` cases, but no execution result is inferred from its existence: `spatial@e7a8f2f:test/spatial/tests/feature/control/ReduceTiny.scala:27-37`.

## Memory, dimensions, and errors

Original source. Local memories expose local read/write/reset hooks; remote memories have a distinct type role. Dense load/store is a transfer operation with mutation on the destination and alias-derived reads on mutable inputs. A dense memory alias stores ranges and backing memories; the transfer lowers those ranges into offsets, dimensions, strides, counters, and fringe streams. Sources: `spatial@e7a8f2f:src/spatial/lang/types/Mem.scala:35-56`, `spatial@e7a8f2f:src/spatial/node/HierarchyMemory.scala:48-69`, `spatial@e7a8f2f:src/spatial/node/DenseTransfer.scala:34-62`, `spatial@e7a8f2f:src/spatial/node/DenseTransfer.scala:79-124`, `spatial@e7a8f2f:argon/src/argon/static/Staging.scala:230-233`.

Original source. SRAM APIs check address rank. One-dimensional allocation explicitly requests a compile-time constant/DSE parameter extent; the inspected multidimensional constructor's error guard conjoins invalid-axis conditions. Thus the intended static-shape restriction is visible, but those hand-written guards alone do not establish that every mixed static/runtime shape is rejected. DRAM host constructors take staged dimensions and zero initialization. Sources: `spatial@e7a8f2f:src/spatial/lang/SRAM.scala:33-51`, `spatial@e7a8f2f:src/spatial/lang/SRAM.scala:138-155`, `spatial@e7a8f2f:src/spatial/lang/DRAM.scala:40-54`.

Original source. Emulated counters produce groups of `par` iterator values with individual valid bits and support positive or negative step direction; source validity is computed before executing the group. Generated memory/FIFO operations receive enable sets. This is evidence for masked logical lanes, not permission to execute an inactive lane's effectful address or value computation eagerly. Sources: `spatial@e7a8f2f:emul/src/emul/Counter.scala:10-32`, `spatial@e7a8f2f:src/spatial/codegen/scalagen/ScalaGenController.scala:86-105`, `spatial@e7a8f2f:src/spatial/codegen/scalagen/ScalaGenFIFO.scala:33-44`, `spatial@e7a8f2f:emul/src/emul/BankedMemory.scala:28-43`.

Original source. SRAM simulation initializes physical storage with invalid values, uses padded/banked dimensions, and catches physical array OOB accesses. It does not provide the proposed Python per-axis logical bounds/definite-initialization contract. Bank flattening zips coordinates with strides; two different logical coordinates can map to the same physical index if per-axis bounds are not separately enforced. Sources: `spatial@e7a8f2f:src/spatial/codegen/scalagen/ScalaGenSRAM.scala:14-17`, `spatial@e7a8f2f:src/spatial/codegen/scalagen/ScalaGenMemories.scala:92-108`, `spatial@e7a8f2f:src/spatial/codegen/scalagen/ScalaGenMemories.scala:144-158`, `spatial@e7a8f2f:emul/src/emul/BankedMemory.scala:23-43`.

Original source. Generated DRAM simulation allocates the logical dimension product plus one burst of extra backing storage. OOB wrappers catch a physical exception, warn, substitute invalid on reads, and discard writes; emul OOB helpers log and return invalid/discard writes. Padding is therefore not a logical authorization to address beyond the user shape. Sources: `spatial@e7a8f2f:src/spatial/codegen/scalagen/ScalaGenDRAM.scala:16-22`, `spatial@e7a8f2f:src/spatial/codegen/scalagen/ScalaGenMemories.scala:36-58`, `spatial@e7a8f2f:emul/src/emul/OOB.scala:19-38`.

Proposed Python rules. Carry rank, logical extents, strides, retained/dropped axes, element type, access capability, and backing-object identity explicitly. Local physical capacity must be statically resolved per axis for hardware-oriented allocation; external logical extents may be invocation-dependent under checked shape requirements. All active accesses check logical per-axis bounds before flattening. Do not inherit negative host indexing, silent truncation of coordinate lists, wraparound shape products, or simulator burst padding as language behavior. Empty transfer views may be well-defined even when zero-capacity physical memories are unsupported; distinguish these cases in diagnostics.

Proposed Python rules. E1's original two buffers are declared inside the tile loop and fully written before use: `spatial@e7a8f2f:test/spatial/tests/ee109/Lab1Part2DramSramExample.scala:21-32`. Give a block-local object a fresh logical identity/state on block entry, including each logical loop iteration. Hardware may reuse an allocation only when no escaped reference, initialization dependence, or overlap changes observable behavior. This is a deliberate logical-lifetime rule. It is not established by the original simulator, which emits memory singleton objects; SRAM emission does not create a new array per logical iteration. Sources for that limitation: `spatial@e7a8f2f:src/spatial/codegen/scalagen/ScalaGenMemories.scala:61-67`, `spatial@e7a8f2f:src/spatial/codegen/scalagen/ScalaGenMemories.scala:150-159`, `spatial@e7a8f2f:src/spatial/codegen/scalagen/ScalaGenSRAM.scala:14-17`.

Proposed Python rules. Uninitialized SRAM/output cells remain uninitialized until definitely written; a Reg reset value initializes that register; FIFO allocation begins empty. A read of an uninitialized cell or an active logical OOB access reports a source-located diagnostic. Input/inout initialization and output completion are explicit port contracts. These match parts of the earlier Rust redesign, not the original invalid-data/zero-backed simulation defaults. Earlier Rust design: `spatial-rs@eb49d8b:docs/language-spec.md:399-412`, `spatial-rs@eb49d8b:docs/language-spec.md:769-799`.

Proposed lifetime distinction. Fresh logical allocation applies to entering the declaring region, not every simulator tick or every nested child activation. A Reg/FIFO declared outside a repeated body retains its state across that body's iterations. State declared at task activation entry survives suspension/resumption of that task. Scratch SRAM inside a tile body has a new initialization map each logical tile iteration even if a physical array is reused. Invocation-local state is fresh on a new invocation; module/persistent state, if supported, needs an explicit lifetime and reset trigger. A blanket reset of all local objects at every controller step would erase intended recurrence and streaming state.

The lifetime discriminator is a three-iteration ordered loop. Reg(reset=0) declared outside the loop, then incremented each iteration, has values 1,2,3 and final 3. The same declaration inside the loop yields 1 on each iteration. Repeating an invocation yields final 3 again for invocation-local state; an explicitly persistent outer register could yield 6 on the second invocation, only under its separately declared retention/reset contract. A FIFO outside a repeated producer/consumer body likewise retains unconsumed tokens; a FIFO constructed inside each iteration begins empty each time under the proposal. These are proposed outcomes, not verified original outcomes.

Original lifetime evidence still to close includes declaration versus emitted initialization/reset for Reg/FIFO, allocation motion, stream FIFO initialization, hardware reset wiring, and the host invocation boundary. Reg Scalagen emits an initialization call where the declaration executes, while the memory object is emitted separately; hardware memory reset is not generally asserted just because a parent controller advances. Sources: `spatial@e7a8f2f:src/spatial/codegen/scalagen/ScalaGenReg.scala:14-36`, `spatial@e7a8f2f:emul/src/emul/Ptr.scala:5-15`, `spatial@e7a8f2f:src/spatial/codegen/chiselgen/ChiselGenMem.scala:201-237`, `spatial@e7a8f2f:src/spatial/transform/AllocMotion.scala:16-56`; next source boundary `src/spatial/transform/streamify/FIFOInitializer.scala`. Full review must separate logical construction, constructor initialization, explicit reset, controller restart, accelerator reset, and module persistence.

Proposed transfer rule. Evaluate endpoints once, require compatible element types and retained logical extents, and represent the affected source/destination regions. For ordinary array/view transfers, recommend a source snapshot followed by destination writes; a FIFO endpoint instead has ordered one-at-a-time consume/produce events. This is the earlier Rust redesign, not proof that arbitrary original overlapping transfers already behave that way. Snapshot semantics make future overlap handling explicit and cannot be silently replaced by a streaming copy that observes its own writes. Sources for the earlier design: `spatial-rs@eb49d8b:docs/language-spec.md:963-985`. E1 uses matching 16-element views and buffers and needs load/compute/store completion dependencies; its nonoverlapping transfer shape does not decide the overlap question.

Tails require two distinct policies. A partial lane group needs an active mask; a partial final tile needs a shorter explicit view or an explicit padding contract. Masking loop indices does not make an oversized `src[base:base+tile]` transfer legal. The original E1 has 32 elements and 16-element tiles, so it establishes neither policy for a remainder: `spatial@e7a8f2f:test/spatial/tests/ee109/Lab1Part2DramSramExample.scala:6-12`, `spatial@e7a8f2f:test/spatial/tests/ee109/Lab1Part2DramSramExample.scala:22-31`.

## Three original execution models that must stay separate

| Subject | Generated Scalagen/emul | Optional Scala executor | Chisel/scheduled hardware evidence |
| --- | --- | --- | --- |
| FIFO capacity/empty access | Mutable Queue; enqueue has no capacity guard; empty banked dequeue yields invalid | ScalaQueue uses declared capacity and throws on full enqueue/empty dequeue | Capacity/status ports and enabled read/write ports; streaming pressure depends on active accesses |
| Parallel children | Emitted sequential body traversal | StreamUnitPipeExecutor ticks child executors | ForkJoin template activates children and synchronizes their completion |
| Streaming progression | Outer stream children are run to input exhaustion before proceeding; source comments explicitly warn about feedback | Pipeline stall logic inspects enabled queue accesses; this note does not certify that implementation | Ready/valid and FIFO full/empty pressure are wired conditionally by stream ancestry/blackbox context |
| `breakWhen` | Counted/forever unrolled loops warn about iteration-end simulation versus immediate synthesis; UnitPipe emission ignores its stop field | Stop fields exist in executor matches; full cancellation behavior not traced here | Controller break input is wired from stop register and stop reset is connected to controller completion |

Sources: `spatial@e7a8f2f:src/spatial/codegen/scalagen/ScalaGenFIFO.scala:18-44`; `spatial@e7a8f2f:src/spatial/executor/scala/memories/ScalaQueue.scala:8-25`; `spatial@e7a8f2f:src/spatial/executor/scala/resolvers/FIFOResolver.scala:12-26`; `spatial@e7a8f2f:src/spatial/codegen/scalagen/ScalaGenController.scala:22-44`; `spatial@e7a8f2f:src/spatial/codegen/scalagen/ScalaGenController.scala:75-94`; `spatial@e7a8f2f:src/spatial/codegen/scalagen/ScalaGenController.scala:180-190`; `spatial@e7a8f2f:src/spatial/executor/scala/ControlExecutor.scala:207-234`; `spatial@e7a8f2f:src/spatial/executor/scala/ExecPipeline.scala:185-214`; `spatial@e7a8f2f:src/spatial/codegen/chiselgen/ChiselGenCommon.scala:249-279`; `spatial@e7a8f2f:src/spatial/codegen/chiselgen/ChiselGenController.scala:308-315`; `spatial@e7a8f2f:fringe/src/fringe/templates/Controllers.scala:141-153`.

The optional executor is explicitly gated before unrolling in the original pass pipeline, while generated Scalagen sees transformed controllers. It cannot be silently substituted as proof of generated Scalagen behavior: `spatial@e7a8f2f:src/spatial/Spatial.scala:202-219`.

Original source. Hardware pressure is branch/access sensitive: an empty queue need not stall a controller when that queue's dequeue is inactive, and a full queue need not stall an inactive enqueue. The relevant generated expressions are gated by stream ancestry or blackbox context. It would be incorrect to generalize them into “every FIFO operation blocks everywhere” or to require every branch-mentioned queue to be nonempty. Sources: `spatial@e7a8f2f:src/spatial/codegen/chiselgen/ChiselGenCommon.scala:212-232`, `spatial@e7a8f2f:src/spatial/codegen/chiselgen/ChiselGenCommon.scala:249-279`, `spatial@e7a8f2f:src/spatial/codegen/chiselgen/ChiselGenMem.scala:321-331`.

Proposed Python rule. Choose and expose a simulation model rather than claiming generic “original-compatible simulation.” A legacy comparison mode, if implemented, must identify the original model/pass configuration and invalid-data policy. The new default must have its own adopted contract. Bounded queue diagnostics below are a recommendation, not an inference from the generated Queue implementation. The stricter optional executor is corroborating evidence of an existing disagreement, not a vote deciding the new language.

## Proposed effect and region contract

The following rules are design recommendations, pending adoption. They are not implementation claims.

1. **Object identity.** Every allocation/port owns one identity. A view is `(backing_id, coordinate_map, shape, capability, lifetime)`; aliases share state and initialization bits. Two views are independent only when their evaluated regions are proven disjoint. Conditional views carry alternative backing identities and path guards, rather than inventing a new mutable object.
2. **Region ownership.** Each operation belongs to one lexical region with a parent, binders, ordered children, yielded values, and an explicit external effect summary. Local allocations are hidden from that external summary but remain internal events. Values cannot escape a region without a declared result/carry operation; controller binders cannot be used outside their body.
3. **Effect vocabulary.** Keep `Read`, `Write`, `ObserveStatus`, `Consume`, `Produce`, `Allocate`, `Reset`, `Shift`, and `MayTrap`, with backing identity, logical region, guard, and source span. Dequeue is a consume plus state mutation; FIFO status is an observation of a state version. Reset/shift change the whole affected region and its initialization map. Do not collapse a FIFO effect into an anonymous array read or only a net occupancy delta.
4. **Runtime choice.** Evaluate a branch condition once against current state and execute exactly one selected region. Keep both branches in captured IR and in conservative static summaries. Preserve their guarded effects and mutually exclusive control. A static may-write union is not a runtime execution schedule.
5. **Order.** Preserve lexical statement order for dependent effects and left-to-right expression operands/call arguments. For Python source ordinary assignment, evaluate the RHS before the target's receiver/indices, then commit the write. For augmented assignment, evaluate the target once and read its old value before evaluating the RHS, then combine/write using the Spatial type's arithmetic. A consuming primary acts at its represented evaluation point. This follows the visible source syntax's evaluation model and avoids introducing an invisible Rust-order exception. A builder must emit the equivalent explicit temporary/effect sequence; a target-first method chain can express a different sequence and is not automatically equivalent. Primary sources: [Python evaluation order](https://docs.python.org/3.14/reference/expressions.html#evaluation-order), [augmented assignment](https://docs.python.org/3.14/reference/simple_stmts.html#augmented-assignment-statements) (accessed 2026-09-30). The older target-before-RHS rule remains labeled historical redesign: `spatial-rs@eb49d8b:docs/language-spec.md:831-837`.
6. **Exactly once.** A selected effect may not be duplicated, dropped, CSEd, or speculated into another branch. Unused dequeues still consume. Ordinary reads may be reused only when backing object, addressed region, guard, and observed state version agree; memory/status reads cannot be hoisted across a relevant write/consume/produce. Possible faults also prevent speculation into an untaken branch.
7. **Contribution versus combine.** Ordered contributions may read/write/consume permitted state exactly once; the enclosing reduction owns its accumulator. The combine region must be pure for tree/reassociation modes. Mapper side effects never become reorderable merely because combine is associative. Accumulator reads/writes by the mapper require an explicitly different recurrence contract and otherwise reject. Numeric identities, topology, normalization, empty domains, and original Fold compatibility belong to the arithmetic study.
8. **Shape and initialization.** Bounds are per logical axis; an active read must be initialized. A branch join retains only definite initialization common to all reachable paths. A potentially zero-trip loop does not establish post-loop initialization without a proof. A view write updates the backing object's corresponding region, including observations through aliases.
9. **Tails.** Inactive lanes execute no reads, writes, FIFO effects, or effectful address/value expressions. Mask before entering their logical region. Tail extent policy belongs to the view/transfer contract and remains visible in the IR.
10. **Scheduling preservation.** `Sequential` prohibits logical iteration/group overlap. `Pipe` requests overlap subject to dependence, visibility, numerical, and resource constraints. Requested II is separate from achieved II. `Parallel` is a fork/join structure, not a synonym for lane unrolling or an ordinary statement list.

Observed language-only probe. Under CPython 3.14.5, a queue containing [0,5] and an eight-cell list executing `dst[q.deq()] = q.deq()` produced consumes 0 then 5 and wrote `dst[5]=0`. An instrumented `a[index()] += rhs()` recorded target index, target read, RHS, and target write, with the index evaluated once. These observations check the source-language distinction only; they do not implement either Spatial frontend. A source/builder equivalent can explicitly bind the RHS value first, bind the index second, then write. With a two-cell destination, the ordinary assignment instead consumes both values and faults on index 5 before committing any destination write; the historical target-first rule would have written `dst[0]=5`.

Proposed fault policy. A failing active operation halts the reference run and publishes no successful result. Earlier completed effects remain visible in its diagnostic trace; no transactional rollback is implied. The failing enclosing write/produce does not commit. This makes an RHS-first assignment that later faults on its target explainable: the RHS's successful consumes occurred before the fault.

The earlier Rust rule requiring static discharge by one fixed obligation calculus is a possible checked profile, not a reason to define all Python Spatial programs by that prover's limitations. It explicitly rejects missing derivations even when a stronger prover could establish safety: `spatial-rs@eb49d8b:docs/language-spec.md:583-593`. Python must distinguish an invalid program, an unsupported analysis, and an unsupported backend capability.

Proposed capability policy. A reference interpreter can evaluate supported dynamic domains with checks at active operations and invocation requirements. A checked compilation profile must discharge safety/initialization obligations by proof, an adopted guarded execution rule, or explicit invocation preconditions; unresolved obligations receive a diagnostic and never silently disappear during lowering. A hardware profile separately requires a defined schedule/handshake implementation. Running a guarded reference program does not prove it compilable to hardware. Initial support may be bounded, but its data model must represent ordinary composition and communicate limitations by feature, not recognize whole-program families.

## Explicit concurrency and streaming need a task graph

Proposed architecture requirement. Preserve an ordered region graph for functional semantics and a communicating task graph for explicit concurrency. Tasks retain program counters/continuations, ports, child controls, completion/join conditions, and channel endpoints. Channels retain capacity, token order, producer/consumer roles, arbitration, and readiness. A successful channel action produces one linearized consume/produce event; a blocked attempt produces no mutation. Functional scheduling order and cycle time remain distinct trace fields.

For independent Parallel children, a deterministic serial replay can be one representative functional trace because effects commute. It is insufficient for communicating children. For example, a producer that sends two tokens through a capacity-one channel and a concurrent consumer that receives two tokens can complete by interleaving. Running the whole producer before the consumer would block at the second send. Increasing the channel to an unbounded queue hides the capacity dependency. This is a proposed counterexample, not an original runtime measurement.

Recommend bounded, checked queue actions in ordered regions and explicitly blocking channel actions in communicating task regions. The domain/endpoint contract must be visible in the representation: an empty ordered dequeue is a diagnostic, while a task receive may suspend until a producer advances. A full ordered enqueue is a diagnostic; a task send may suspend. A quiescent graph with unfinished tasks and no possible internal/external progress is a deadlock diagnostic; absence of external input alone may instead be a defined waiting state. Do not switch between these meanings merely because one simulator happens to run children serially.

This recommendation deliberately separates bounded safety from legacy elastic Queue replay. Full Spatial streaming needs agreed rules for simultaneous enqueue/dequeue, full/empty boundary handshakes, branch-local readiness, multiple producers/readers, fairness, feedback, finite termination, forever controllers, and cancellation/drain. The graph representation can carry them before an HLS emitter is selected, but this bounded study does not settle all of those transition rules. Explicit stream/task constructs must report unsupported semantics until the applicable contract and implementation exist; silently executing them as ordered loops is unacceptable.

Likewise, `breakWhen` must identify a checkpoint/cancellation policy and the fate of already-issued effects. Recommend iteration-boundary stop for the simple ordered reference profile, and a separately defined scheduled cancellation/drain policy for immediate hardware stop. This is a deliberate split. Original API comments promise immediate stop/reset, while generated Scalagen warns about loop-end behavior and drops stopWhen on UnitPipe emission. Sources: `spatial@e7a8f2f:src/spatial/lang/control/Control.scala:41-56`, `spatial@e7a8f2f:src/spatial/codegen/scalagen/ScalaGenController.scala:75-94`, `spatial@e7a8f2f:src/spatial/codegen/scalagen/ScalaGenController.scala:180-184`.

## Original, Rust, and Python ledger

| Topic | Original inspected behavior | Earlier Rust redesign | Python recommendation/status |
| --- | --- | --- | --- |
| Effectful reduction body | FIFOBranch consumes in the map region | `reduce` body read-only/private; `fold` allows ordered mutation | Preserve ordered effectful contributions; combine topology remains separate. Proposed |
| Register reset vs reduce seed | Explicit accumulator has no identity/fold field; first partial group ignores old accumulator | Explicit zero-init additive reduction | Keep reset, identity, seed, and existing accumulator distinct. Proposed |
| FIFO overflow/underflow | Generated elastic Queue / invalid empty result; optional executor is bounded/throwing | Static occupancy proof, defensive runtime faults; hardware blocking deferred | Adopt explicit bounded ordered queues and communicating channel contracts; legacy comparison separately labeled. Proposed |
| Branch execution | Lazy emitted If/Switch; effectful cases retain enables | Exactly one branch, path-sensitive facts | Preserve guarded regions and lazy effects. Proposed |
| Assignment order | No claim of Scala/Python assignment equivalence from this corpus | Target indices before RHS | Python ordinary assignment RHS first; augmented assignment target once before RHS; builder uses explicit equivalent effect order. Proposed redesign |
| Parallel/control default | Parallel=ForkJoin; bare counted controls initially default Pipelined | Auto/Seq/Pipe between groups; no full stream semantics | Preserve task/fork/join representation and dependence obligations. Proposed |
| Local lifetime | Staged allocation, generated memory objects; physical reuse/buffering in compiler | Fresh logical locals per body entry | Use fresh logical state; resource reuse must preserve it. Proposed redesign |
| Aliases | Mutable dense/sparse aliases are enabled | Backing-region disjointness; distinct ports nonalias | Preserve view alias identity; define port alias contract and validate it. Proposed |
| SRAM initialization | Invalid-filled simulated storage | Definitely initialized reads only | Source-located uninitialized-read fault; checked profile requires proof/guard. Proposed redesign |
| OOB/padding | Logs/warns, invalid/discard; DRAM extra burst backing | In-bounds static obligations | Logical per-axis checks; padding remains physical. Proposed redesign |
| Tails | Counter lane valid bits | Explicit tail request; divisibility otherwise | Explicit masks and view extents; no inactive effect. Proposed |
| FSM | Typed Bits state; condition/action/next regions; Scalagen while | Int-only state, observational init/condition/step, bounded induction calculus | Preserve general state/region representation; adopt effect restrictions per mode, not Int-only language scope. Further evidence required |
| Break/forever | Immediate API promise, loop-end sim warning, heuristic input exhaustion | No full stream/backpressure v1 | Explicit stop/checkpoint/drain semantics and environment model. Further evidence required |

Original evidence for these rows is detailed above. Earlier Rust source ranges: effect/reduction rules `spatial-rs@eb49d8b:docs/language-spec.md:816-924`; object/lifetime/bounds rules `spatial-rs@eb49d8b:docs/language-spec.md:399-420`, `spatial-rs@eb49d8b:docs/language-spec.md:722-799`; tails and schedules `spatial-rs@eb49d8b:docs/language-spec.md:862-878`; deferred hardware stream behavior and narrow-family limits `spatial-rs@eb49d8b:docs/language-spec.md:1117-1124`.

## Counterexamples and proposed acceptance cases

All cases below are expected behavior under the proposal, not executed conformance tests. Numeric values are small exact integers; production assertions must also use the adopted numeric policy.

| Case | Required observation / decision | Bug exposed |
| --- | --- | --- |
| E3 counts 13,25 | Exact Q1-then-Q2 trace above, result 378, no untaken dequeue | Same sum despite wrong consumption order |
| Branch with Q1=[7], Q2=[101], select Q1 because Q1 nonempty | Return 7; Q1 empty; Q2 still [101] | Eager evaluation of both branch values |
| Same branch with Q2=[] | Selected Q1 read succeeds; no Q2 fault | Speculative untaken dequeue/fault |
| `q.enq(q.deq())`, q empty | Fault at consume; no append | Checking only net occupancy zero |
| Same expression, capacity 1 and q=[9] | Consume 9, then produce 9; final q=[9] | Checking enqueue capacity before evaluating value |
| Two source dequeues from q=[11,22], first result unused | Second returns 22; q empty; two consume events | DCE/CSE of consuming reads |
| Consume in target and value: q=[0,5], eight-cell dst, `dst[q.deq()] = q.deq()` | Recommended Python order gives `dst[5]=0`; historical target-first gives `dst[0]=5`; builder equivalence requires RHS temporary first | Undocumented frontend evaluation-order difference |
| Same assignment with two-cell dst | Consume RHS 0, consume target index 5, then logical OOB; no destination write; target-first would write `dst[0]=5` | Wrong sequencing can turn a required fault into apparent success |
| `dst[index()] += rhs()` | Evaluate target once, read target, evaluate RHS, combine/write | Replacing augmented assignment with a duplicated target or ordinary assignment |
| Status read after consume from q=[1] | Before empty=false; after empty=true | CSE/hoisting observations across queue mutation |
| One branch initializes V[0], other does not; later read | Reject unchecked read / require guard; no assumed initialization | Union instead of intersection at branch join |
| `alias=V[1:3]`; write alias[0] then read V[1] | Read updated value; same backing identity | Treating a view as a copy |
| Shape (2,3), coordinate (0,3) | Logical OOB even if flattening points into backing allocation | Flat-only bounds checking |
| E1 size 30/tile 16 without shorter last view | Reject oversized final transfer; explicit clipped view can be analyzed | Inferring a tail policy from divisible E1 |
| Five iterations with par=4 and explicit tail | Exactly five active effects; final inactive lanes emit none | Masking only destination writes |
| Parallel tasks sharing capacity-one channel | Requires communicating graph model; serial replay is insufficient | Elastic or serial execution hiding backpressure |
| Two parallel lanes consume same FIFO without a specified vector/arbitrated order | Reject that scheduling capability until order is defined/proved | Assuming associativity resolves mapper races |
| FIFOBranch counts outside 0..128 | Invocation requirement failure or active bounded-queue diagnostic | Inheriting unbounded generated Queue |
| E3 zero total with no identity | Nonempty-domain requirement or explicit empty alternative | Confusing Reg reset with identity |
| Reg(reset=0) inside versus outside repeated loop | Inside yields 1 each iteration; outside yields 1,2,3; repeated invocation follows its declared local/persistent lifetime | Blanket freshness erasing loop-carried or persistent state |
| Stop write followed by another effect in a body | Outcome fixed by explicit checkpoint/drain contract, not guessed from simulator | Claiming immediate hardware cancellation from loop-end replay |

Acceptance should check the represented region/effect program, event order/state, faults, and final outputs. The effect trace should identify source span, branch, object, logical iteration/lane, and transition, and support repeated kernel invocations to check lifetime/reset behavior. A source sketch compiling as ordinary Python is not evidence for these conditions.

## Exact remaining full-Spatial research obligations

These are required follow-on families for the full rewrite, not permanent exclusions justified by the initial corpus. Paths below identify existing source boundaries; detailed uninspected behavior remains open.

| Family and primary source | Question that must be answered before full support | Required discriminator |
| --- | --- | --- |
| Priority/round-robin dequeue: `spatial@e7a8f2f:src/spatial/lang/api/PriorityDeqAPI.scala:10-50`, `spatial@e7a8f2f:src/spatial/lang/api/PriorityDeqAPI.scala:55-104`; priority hardware read `spatial@e7a8f2f:src/spatial/codegen/chiselgen/ChiselGenMem.scala:324-326` | Arbitration snapshot, all-empty behavior, conditional eligibility, and rotation state; extra empty enable is inserted at codegen | Two simultaneously eligible inputs; empty preferred input; changing iter/enable; exactly one consume |
| FIFO vectors/multiple ports and LIFO: `spatial@e7a8f2f:src/spatial/lang/FIFO.scala:37-49`, `spatial@e7a8f2f:src/spatial/codegen/scalagen/ScalaGenLIFO.scala:18-43` | Lane packing/compaction, port order, simultaneous actions, stack ordering, overflow | Sparse active masks; consume/produce at full and empty boundaries; vector tails |
| Locks and lock memories: `spatial@e7a8f2f:src/spatial/node/LockMem.scala:19-38`, `spatial@e7a8f2f:src/spatial/node/LockMem.scala:138-147` | Ownership/key lifetime, exclusion, acquire/release points, arbitration, and memory visibility | Competing keys/tasks, aliases to locked regions, waiting/deadlock |
| MergeBuffer: `spatial@e7a8f2f:src/spatial/node/MergeBuffer.scala:8-28`; template `fringe/src/fringe/templates/memory/MergeBuffer.scala` | Way bounds/init, selection/order, producer readiness, capacity meaning, simultaneous traffic | Multiple ways ready, bound transitions, exhausted way, backpressure |
| LineBuffer/RegFile: `spatial@e7a8f2f:src/spatial/node/LineBuffer.scala:7-30`, `spatial@e7a8f2f:src/spatial/codegen/scalagen/ScalaGenLineBuffer.scala:21-50`, `spatial@e7a8f2f:emul/src/emul/LineBuffer.scala:14-59`; `src/spatial/node/RegFile.scala` | Shift/swap versus fresh-object semantics, initialization, buffered versions and window coordinates; original LineBuffer starts invalid, Rust proposes zero-filled | First partial window, row shift under masks, multiple buffers, reuse across invocation |
| FSM and forever controllers: `spatial@e7a8f2f:src/spatial/lang/control/FSM.scala:8-23`, `spatial@e7a8f2f:src/spatial/node/Control.scala:103-117`, `spatial@e7a8f2f:src/spatial/codegen/scalagen/ScalaGenController.scala:60-84` | General Bits state, observational vs consuming condition/next regions, termination, environment starvation, fairness | Effectful condition, state wider/different than Int, feedback FIFO, finite input with forever control |
| `breakWhen` and cancellation: `spatial@e7a8f2f:test/spatial/tests/feature/control/Breakpoint.scala:62-93`, `spatial@e7a8f2f:src/spatial/codegen/chiselgen/ChiselGenController.scala:312-315` | Checkpoint, already-issued effects, outstanding transfer acknowledgements, stop reset and nested children | Stop between writes, stop with in-flight FIFO/DRAM traffic, repeated restart |
| External streams/structured blackbox channels: `src/spatial/node/StreamIn.scala`, `src/spatial/node/StreamOut.scala`, `src/spatial/node/StreamStruct.scala`, `src/spatial/node/Blackbox.scala`; `spatial@e7a8f2f:src/spatial/codegen/chiselgen/ChiselGenCommon.scala:249-278` | Environment traces, structured-field coherence, task handshakes, ready/valid timing, blocked vs ended input | Delayed input/output readiness; multiple fields; no-progress classification |
| Dense/sparse transfers and dynamic/locked DRAM: `spatial@e7a8f2f:src/spatial/node/DenseTransfer.scala:79-124`, `src/spatial/node/SparseTransfer.scala`, `spatial@e7a8f2f:src/spatial/node/DRAM.scala:11-38` | Aliasing and overlap, snapshot versus stream transfer, sparse address consumption, allocation ownership, bus packing/alignment | Overlapping views, repeated/sparse addresses, unequal transfer extents, partial burst/tail |
| Physical memory versions/banking and schedules: `src/spatial/traversal/banking/MemoryConfigurer.scala`, `src/spatial/transform/BufferRecompute.scala`, `src/spatial/transform/RetimingTransformer.scala`; `spatial@e7a8f2f:fringe/src/fringe/templates/Controllers.scala:96-153` | Dependency-preserving buffering, loop overlap, fairness, memory-port conflicts and actual II | Read-after-write across overlapped iterations, N-buffer reuse, independent child ordering |

The task graph must express these protocols at the architecture level before the overall full-Spatial design is called complete. Each protocol then needs transition rules, fault/wait behavior, simulator semantics, and backend-preservation obligations. Only their HLS mapping may wait until the later HLS wave. A target's inability to realize a protocol is a capability boundary; it does not license erasing the source construct or quietly lowering it to a different controller.

## Distillation and unresolved limits

**Follow-up:** [[PY-R008 - Advanced State and Communication Protocols]] now defines the advanced transitions identified above. [[PY-R009 - HLS Boundary and Control Lowering]] and [[PY-R010 - Memory Scheduling and Design Space Exploration]] give their target obligations, including safety and progress refinement. The family questions above are the study history; their proposed answers are now in those notes and [[30 - Python State and Protocol Contract]].

The adopted specification should eventually separate: logical execution/effects; storage identity/lifetime/capabilities; dimensions/views/transfers; controllers and contribution regions; communicating tasks/channels; diagnostics/proof profiles; and scheduled/backend semantics. The findings now feed proposed contracts with adoption and implementation status explicitly separate; no adopted language support is claimed.

The bounded conclusion is decisive on lazy branches, dequeue mutation, preservation of aliases, separation of contribution effects from pure reduction arithmetic, and the need to represent explicit task concurrency. Original-generated simulator invalid/OOB behavior, FIFO elasticity, scalar-fold order, and immediate cancellation must not be copied as unnamed defaults. Remaining evidence is explicit: transformed IR and fresh application runs, optional-executor checks, executable arbitration/stream/lock/window conformance, repeated-invocation lifetime cases, and scheduled/backend trace comparisons. Completing this bounded study is progress toward the full language; it is not evidence that the initial three examples establish full-Spatial semantics.
