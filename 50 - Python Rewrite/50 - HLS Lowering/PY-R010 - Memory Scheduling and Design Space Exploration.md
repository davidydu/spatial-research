---
type: deep-dive
title: Memory Scheduling and Design Space Exploration
topic: memory-scheduling-and-design-space-exploration
project: spatial-python
source_files:
  - "spatial@e7a8f2f:src/spatial/metadata/memory/BankingData.scala"
  - "spatial@e7a8f2f:src/spatial/traversal/banking/MemoryConfigurer.scala"
  - "spatial@e7a8f2f:src/spatial/traversal/MemoryAnalyzer.scala"
  - "spatial@e7a8f2f:src/spatial/traversal/BufferRecompute.scala"
  - "spatial@e7a8f2f:src/spatial/dse/DSEThread.scala"
  - "spatial@e7a8f2f:src/spatial/node/DenseTransfer.scala"
  - "spatial@e7a8f2f:src/spatial/node/SparseTransfer.scala"
  - "spatial@e7a8f2f:src/spatial/node/DRAM.scala"
  - "spatial@e7a8f2f:src/spatial/lang/SRAM.scala"
  - "spatial@e7a8f2f:fringe/src/fringe/templates/memory/DRAMAllocator.scala"
  - "spatial@e7a8f2f:src/spatial/codegen/hlsgen/HLSGen.scala"
  - "AMD UG1399 2025.2 English, memory/burst/storage directives, accessed 2026-09-30"
session: 2026-09-30
status: research-conclusion
feeds_spec:
  - "[[40 - Python Compiler and HLS Contract]]"
---

# Memory Scheduling and Design Space Exploration

## Result and authority

Recommend a checked Python memory implementation plan: logical backings/views and ordered requests first; physical banks, packed words, replicas, versions, ports, and DMA engines second; HLS C++/component emission last. Python proves semantic preservation and classifies hard constraints versus preferences. The vendor schedules/binds emitted structures and reports achieved results. Layout, DMA, and DSE cover the full intended memory model, including indirect accesses and dynamic allocation; an unavailable target route produces a capability diagnostic, not a language ban.

This extends [[PY-R009 - HLS Boundary and Control Lowering]] and uses [[PY-R006 - Compiler Architecture and Framework Choice]], [[PY-R007 - Host Workflow Reproducibility and Validation]], and [[PY-R008 - Advanced State and Communication Protocols]]. Those notes own numerical/effect order, invocation aliases, protocol capacity, admission, reset, cancellation, and lifetime. Their semantics are inputs to this study, not optimization knobs.

Original claims cite inspected `spatial@e7a8f2f7f776dd0c5ac7fc03f16b3ed4d97021f0` source. [[70 - Banking]] and [[40 - Design Space Exploration]] are historical reading maps. AMD facts below refer to the displayed **UG1399 2025.2 English** pages, retrieved 2026-09-30. This is a design proposal; no compiler, original application, vendor C simulation, synthesis, RTL, timing, or board experiment was run. Implementation must lock a release, part/platform, clock, ABI, and component set and revalidate each route.

## Decisive original evidence

Original Spatial already distinguishes affine banking, buffering, multiplexed ports, broadcasts, and duplicates. `ModBanking` selects `(alpha·address / B) mod N`; memory instances carry depth, padding, and resource choice. Offset construction handles flat and hierarchical cases but explicitly throws for arbitrary dimension groupings. This is evidence for explicit mappings, not proof that every mapping is complete. (`spatial@e7a8f2f:src/spatial/metadata/memory/BankingData.scala:49-65`; `spatial@e7a8f2f:src/spatial/metadata/memory/BankingData.scala:76-118`; `spatial@e7a8f2f:src/spatial/metadata/memory/BankingData.scala:180-205`; `spatial@e7a8f2f:src/spatial/metadata/memory/BankingData.scala:208-252`.)

The configurer searches views, bank counts, coefficients, and duplication, computes buffer depth, evaluates costs, and selects a scheme. Memory families have different strategies; FIFOs/LIFOs use a configurer marked “No buffering.” BufferRecompute later revises depths and resolves read-port conflicts after transformations. (`spatial@e7a8f2f:src/spatial/traversal/banking/MemoryConfigurer.scala:25-48`; `spatial@e7a8f2f:src/spatial/traversal/banking/MemoryConfigurer.scala:610-668`; `spatial@e7a8f2f:src/spatial/traversal/MemoryAnalyzer.scala:125-138`; `spatial@e7a8f2f:src/spatial/traversal/BufferRecompute.scala:29-46`.)

These algorithms are research evidence. The inspected HLS memory stage is a whole-program recognizer requiring two DRAMs, fixed 16-element tiles, particular counters, and one multiply. It does not establish a general memory emitter. Its restrictions must not become the Python rewrite's coverage boundary. (`spatial@e7a8f2f:src/spatial/codegen/hlsgen/HLSGen.scala:197-213`; `spatial@e7a8f2f:src/spatial/codegen/hlsgen/HLSGen.scala:234-247`.)

## Versioned HLS constraints

| Inspected AMD 2025.2 source | Source fact and consequence for the proposal |
|---|---|
| [ARRAY_PARTITION](https://docs.amd.com/r/2025.2-English/ug1399-vitis-hls/pragma-HLS-array_partition?contentId=VTWLNjG5Wv~QfdSXemYYaw) | Cyclic, block, and complete mappings create smaller memories/registers with additional ports and instance cost. A pragma alone does not prove collision freedom. |
| [ARRAY_RESHAPE](https://docs.amd.com/r/2025.2-English/ug1399-vitis-hls/pragma-HLS-array_reshape) | Reshaping concatenates elements into wider words. Partition/reshape directives are unsupported on top-level M_AXI interfaces. Packing and independent banking therefore need distinct plan fields. |
| [BIND_STORAGE](https://docs.amd.com/r/2025.2-English/ug1399-vitis-hls/pragma-HLS-bind_storage) | RAM_2P permits a read-only port plus a read/write port; RAM_S2P has separate read/write ports; RAM_T2P permits both on both ports. Implementation/latency combinations are restricted. “Dual port” is insufficient as a resource descriptor. |
| [Burst preconditions](https://docs.amd.com/r/2025.2-English/ug1399-vitis-hls/Preconditions-and-Limitations-of-Burst-Transfer?contentId=yS94n~hOvH8h9DKgU0jyfw) | Inference requires one direction, consecutive forward addresses, known length before issue, and no relevant dependence. Conditional accesses and overlapping regions can prevent inference. Preserve guards and use another route when needed. |
| [DEPENDENCE](https://docs.amd.com/r/2025.2-English/ug1399-vitis-hls/pragma-HLS-dependence?contentId=31OAqYpyRZEb9a1Tc5g85A) | Incorrectly negating a real dependence can produce incorrect hardware; bundled M_AXI arguments have directive restrictions. Emit independence assertions only from a proof or validated invocation contract. |
| [Dynamic memory](https://docs.amd.com/r/2025.2-English/ug1399-vitis-hls/Dynamic-Memory-Usage?contentId=LxlXbA7aBsnWhMTfq8Hj1w) | Runtime allocation system calls and dynamically created/destroyed C++ objects require bounded replacements before synthesis. Dynamic Spatial objects need a pool/service protocol, not emitted `malloc`. |
| [Interface configuration](https://docs.amd.com/r/2025.2-English/ug1399-vitis-hls/config_interface) | Outstanding requests imply internal buffers sized from outstanding count × maximum burst length × word size. DMA concurrency consumes storage and can stall; model it explicitly. |

## Checked memory representation

All following contracts are **proposed**. Represent them in the Spatial implementation dialect and verify after every transformation that changes accesses, lanes, versions, or issue order.

| Plan object | Required information |
|---|---|
| Logical memory | Backing/generation, element Bits, extents, view origin/strides, accessible domain, initialization map, lifetime/reset image, ownership/lease rules. Aliases retain one backing identity. |
| Physical layout | Total logical-to-physical map `(bank,row,bit slice)`, inverse/decoder, physical dimensions/padding, packed-word width, RAM type/latency, coherent replicas, version-to-slot map. |
| Access group | Captured address/data/mask, logical iteration/lane order, guards and address domain, read/write dependencies, version, issue/response/visibility events, compatible port slots, arbitration where permitted. |
| DMA/allocator | Transfer geometry, ABI byte mapping, source snapshot or streaming mode, overlap class, requests/data/responses, outstanding bounds, completion/cancel policy; allocation quota/policy, generation, and response endpoint. |
| Obligation/report | Source locations, proof assumptions/results/unknowns, required capabilities, hard schedule constraints, cost confidence, emitted artifact identity, achieved vendor resources/schedule. |

Structural address arithmetic uses mathematical integers followed by checked conversion to the chosen bus/index width. Accelerator integer wrapping must not silently wrap allocation size, stride products, bank rows, or byte addresses. Physical padding never authorizes an out-of-range logical access.

## Proof gates and scheduling

| Gate | Required result before choosing a route |
|---|---|
| Alias and order | Normalize views into backing coordinates and generations. Prove disjointness, preserve happens-before, or implement an explicit lock/arbiter protocol. Unknown alias is not independence. Host preparation validates any declared disjoint-port requirement. |
| Layout correctness | Every legal initialized cell has a reachable representation; distinct logical cells have nonoverlapping physical slices except intentional coherent replicas. Reads decode the same bits; writes update every live replica. Prove physical rows and arithmetic fit. |
| Guards and tails | Inactive lanes issue no request, dequeue, fault, or write. Preserve per-axis bounds and branch laziness; padding is inaccessible. A guard controlling an effect cannot be discarded to help burst inference. |
| Port feasibility | For each bank/version and simultaneous issue set, assign all active operations to compatible ports, including overlapping iterations, DMA, resets, replication writes, and shifts. Equal-address broadcast requires the same logical version and no intervening write. |
| Read/write collision | Same-address accesses obey source order using phases, forwarding, or serialization. Do not inherit RAM collision mode as the language rule. An unordered conflicting task race is rejected, even if one C simulation happens to serialize it. |
| Versions/lifetime | Publish exactly once, keep leases until completion, and recycle slots only after all readers/traffic release them. Preserve invocation/task/persistent reset distinctions. Changing physical depth cannot change semantic credits or introduce deadlock. |
| Transfer overlap | Preserve R008 array snapshot and repeated-address scatter order. Prove a streaming/directional optimization equivalent over the entire transfer, or stage the snapshot before destination writes. Tile-by-tile copying alone does not prove this. |
| Progress and faults | Finite adapter/request capacities admit a progress argument under named environment assumptions. Preflighted array-transfer faults occur before transfer writes. Issued external operations drain according to R008; compiler speculation cannot create extra effects. |

For a scheduled recurrence with carried distance d and feedback latency L, `II*d >= L` is a necessary dependency bound. For uniform single-kind bank traffic, accesses per iteration divided by usable ports gives another necessary lower bound; mixed read/write compatibility and exact cycle phases require assignment, not separate read/write totals. These are compiler calculations, not claims that HLS achieves the bounds.

Nonaffine addresses remain legal. Choose a preserving serialized engine or a resource arbiter when the source permits timing variation and progress remains valid; retain ordered effectful lane/contribution requests. A hard simultaneous-port or II requirement that this route cannot meet fails hardware eligibility. Pure numerical reassociation follows R002 laws/topology, never a banking heuristic. Stop-sensitive admission windows and explicit concurrency are semantic constraints from R008; stalls must not change the admitted/drained effect set.

## Lowering routes across memory families

| Family | Intended route and decisive obligation |
|---|---|
| SRAM, LUT/ROM | Native partition/bind directives when their mapping matches the checked plan. Read-only replication is cheap semantically; mutable duplication needs coherent update distribution and visibility. |
| General affine/hierarchical layouts | Emit separate bank arrays and explicit selectors/row maps when native partitioning cannot express coefficients/blocking. Prove map injectivity, padding, routing, and port demand; no requirement to flatten all layouts into cyclic partition. |
| Indirect/masked accesses | Capture once, guard before request, route through ordered phases/arbiters. Widening a word may require masked update or read-modify-write, which adds dependencies and ports. |
| Reg/RegFile shifts and broadcasts | Registers or bank arrays plus explicit old-state snapshot/shift phases. Initialization, reset, and atomic publication remain source properties; shifting must not read partially updated state. |
| LineBuffer/published blocks | Versioned ring storage with consumer leases and fill/history rules. An HLS PIPO is usable only after showing equivalent publication, lease, and credit behavior. |
| FIFO/LIFO/MergeBuffer/locks | Generated protocol/storage machines or validated RTL components under R009. Vector atomicity, selectors, merge-to-pack staging, lock visibility, and token capacities require adapters; partitioning a C++ array does not implement them. |
| Host/external DRAM | Typed M_AXI or external transaction adapters with checked ABI, ownership, completion, errors, and alias domains. Separate bundles do not prove disjoint physical memory or guaranteed bandwidth. |
| Runtime local dimensions | A maximum-sized arena plus logical shape/generation and invocation-domain checks, or explicit spill/service storage. Accept the hardware profile only within its proved resource domain. Unbounded local storage cannot be promised by a finite FPGA. |
| Dynamic DRAM | Bounded heap/pool controller or host allocator request/response service. Make allocation policy/quota observable through the declared allocator contract; establish Live only on response, initialize the promised image, drain before free, reject stale generations. |

Original accelerator allocation/deallocation nodes are explicit memory effects; the original allocator has request arbitration and heap responses. This supports a service route but does not establish the proposed lifetime contract: its allocation status can update on a request as well as a response. (`spatial@e7a8f2f:src/spatial/node/DRAM.scala:13-31`; `spatial@e7a8f2f:fringe/src/fringe/templates/memory/DRAMAllocator.scala:61-88`.)

Runtime-shaped local arenas are a proposed extension: the original one-dimensional SRAM constructor accepts constants/DSE parameters and diagnoses other lengths. The arena route does not claim inherited support for arbitrary runtime local allocation. (`spatial@e7a8f2f:src/spatial/lang/SRAM.scala:139-142`.)

Default bounded local arenas preserve logical freshness through initialization maps/generations, not mandatory physical clearing of every SRAM cell. Default dynamic DRAM allocation retains R008's typed zero image; clearing costs and completion are explicit. Pool fragmentation and exhaustion follow the chosen deterministic allocator policy or named environment response; a DSE candidate cannot silently substitute a different failure policy. A target with no allocator component rejects that lowering while reference semantics remain available.

## DMA geometry, completion, and overlap

Dense multidimensional views lower into checked contiguous segments plus explicit strided/indirect transactions. R008 array transfers preflight and snapshot selected source values before ordered destination writes; stream transfers capture and commit per item. Zero-length operations issue nothing. Partial tiles issue only valid items. For sub-byte or non-byte-multiple Bits, define an explicit ABI bit packing and byte-enable rule; protect neighboring cells during partial-word updates. Never infer bytes per element with truncating `nbits/8`.

Logical disjointness is insufficient for a packed read-modify-write. Two four-bit cells share one byte: concurrent writes of 3 to the low cell and 12 to the high cell must produce `0xC3`. If both updaters read zero and later serialize only their final writes, `0x03`/`0xC0` loses one update. Require a supported atomic masked write, forwarding/combining of compatible updates, or protection of the whole read→merge→write transaction at physical-word granularity. Every updater, including DMA, replicas, reset/init, and another task, participates in this physical dependency domain. Verify preservation and progress; a logical no-alias assertion cannot remove these implementation hazards.

Original dense lowering computes byte packing, restricts upper-dimensional parallelism, and constructs masked unaligned stores with an outer pipe to retain acknowledgments. Sparse non-PIR lowering repeats the last address/data in padded iterations and assumes one acknowledgment per address. Those are target artifacts, not extra Python logical items or permission to repeat volatile/device transactions. (`spatial@e7a8f2f:src/spatial/node/DenseTransfer.scala:85-98`; `spatial@e7a8f2f:src/spatial/node/DenseTransfer.scala:273-304`; `spatial@e7a8f2f:src/spatial/node/SparseTransfer.scala:108-122`; `spatial@e7a8f2f:src/spatial/node/SparseTransfer.scala:148-167`.)

Dense snapshot overlap may use bounded staging, or a proven directional copy for suitable contiguous one-dimensional views after preflight. General multidimensional aliases use full selected-value staging or an equivalent dependence schedule. Scatter duplicates retain logical last-item-wins order; they cannot issue unordered writes to one address. Gather duplication can reuse a read only within the same stable snapshot. DMA overlap is permitted across proven disjoint domains or explicit dependencies; accepted asynchronous transfers retain ownership until join.

**Manual-burst route.** One owner task per endpoint sequences request, captured data, and completion; write completion includes one returned response per request. Do not overlap dependent read/write lifetimes or bundled endpoints' transactions. Bound issue-ahead so request saturation cannot prevent draining. These constraints come from [Using Manual Burst, UG1399 2025.2](https://docs.amd.com/r/2025.2-English/ug1399-vitis-hls/Using-Manual-Burst?contentId=GZ~rctvGB5Rk7_ULx_dNIw), especially its Methods, Features and Limitations, and Potential Pitfalls sections.

That page gives different cross-process guidance across scopes: **Using Manual Burst in C-Simulation** describes cross-process request/data calls, while **Features and Limitations**, item 9, says they are unsupported and trigger a dataflow-checker error. Simulation support does not establish a synthesizable route. Preserve the single-owner default; cross-process splitting requires an executable probe against the locked release before eligibility. This is an evidential limit, not an observed tool failure. A supplied no-alias assertion or positive-trip-count hint also needs validation; zero-trip source semantics must remain legal.

## DSE ownership and resource gates

Original DSE sets candidate parameters, obtains latency/area estimates, and labels validity using capacity/errors. Scalar, memory, and contention reruns are commented out in the inspected per-point area evaluation. Reusing its “valid” label would not prove Python candidate legality. (`spatial@e7a8f2f:src/spatial/dse/DSEThread.scala:109-123`; `spatial@e7a8f2f:src/spatial/dse/DSEThread.scala:130-150`.)

| Python-owned candidate choices | Required restriction |
|---|---|
| Tiles, unroll factors, bank maps, replicas, word packing, RAM resources, legal issue intervals | Recheck address/tail/numeric laws, dependencies, hard constraints, and changed port sets for every candidate. Tile changes may not alter effect order or numerical topology. |
| Physical buffers, version storage, outstanding transactions | Preserve semantic token/publication capacity and admission. Extra physical slots need credit limiting; fewer slots require a progress/refinement proof. |
| Semantic capacity/admission/allocator policy | Explore only as explicit separately checked program profiles, with new semantic identity and user-visible behavior. These are not implementation-only optimization parameters. |

Candidate processing is: materialize immutable plan → verify all obligations → estimate resources/performance with confidence and unknowns → rank/Pareto-filter → emit → validate vendor C/RTL behavior → inspect synthesis schedule/resource reports → validate physical timing/platform behavior where claimed. Parallel workers receive private snapshots and content-addressed artifacts; incomplete/failed runs cannot enter the feasible set. A solver's timeout is Unknown, not proof.

Resource accounting includes bank padding and primitive granularity, replicas, simultaneously live versions, merge packers, queue metadata, decode/mux/fanout, initialization/reset controllers, snapshot scratch, allocator tables, and DMA buffers. For outstanding count O, burst limit B, and bus word bytes W, budget the documented adapter term `O*B*W` per direction, plus control and other storage, unless a validated buffer override/fabric arrangement replaces it. Lower storage estimates do not establish routing/clock feasibility. Model latency distinguishes issue, external wait, and completion; no fixed DRAM bandwidth or fairness is invented.

Hard II, ports, resource ceilings, or clock requirements fail validation when reports do not meet them. Soft preferences report achieved values. HLS estimates are separate from placed/routed timing and board measurements. Cache identity includes semantic revision/protocol profile, numeric laws, all candidate parameters/proofs/assumptions, ABI/alias domain, allocator/environment contract, component hashes, tool release, part/platform, clock, and model version. No candidate shares “verified” status merely because its source program is unchanged.

## Discriminating acceptance cases and remaining limits

The following are designed expectations, not executed results.

| Case | Required outcome |
|---|---|
| M01: four lanes address `base+2*l`, cyclic four banks, even base | Two reads per used bank. Single-read banks cannot meet one simultaneous issue; choose a proven alternative or reject the hard request. |
| M02: two differently named views overlap | Preserve one backing. Copy `[1,2,3]` to positions 1–3 of `[1,2,3,4]` produces `[1,1,2,3]`; a forward unsnapshotted loop is wrong. |
| M03: scatter addresses `[2,2]`, values `[7,9]` | Final cell 2 is 9. Unordered outstanding writes or silent coalescing across observable effects fail. |
| M04: extent 17, tile 16; extent 0 | One valid tail item and zero inactive effects; zero extent issues no command/ack. No generated `assert(N>0)` may reject the zero case. |
| M05: mutable read replicas | A write followed by any legal replica read returns the new value; premature acknowledgment before replica visibility fails. |
| M06: publication capacity two, physical depth three/one | Three slots expose only two credits; one slot requires a progress proof or rejection. Depth is not free semantic capacity. |
| M07: allocate, alias, free, reallocate same address | Old alias faults by generation; new object reaches Live only after response and promised initialization. Outstanding traffic prevents reuse. |
| M08: all DMA requests issued before any draining, finite adapter | Show bounded admission/progress or reject the plan. A completing unlimited C model does not validate it. |
| M09: conditional faulting/dequeue tail address | Capture and guard in source order; inactive tail never faults/consumes. A performance rewrite cannot move it before its guard. |
| M10: vendor achieves II=2 for hard II=1 | Hardware validation fails; for soft II=1, report achieved II=2 without semantic change. |
| M11: concurrent writes to low/high four-bit cells of one initially zero byte | Writing 3 and 12 yields `0xC3`. Serializing final port writes alone fails; protect/forward/merge the complete packed update across all engines. |

Architecture choices are now explicit. Remaining evidence work is target-specific: native partition/reshape equivalence for selected layouts, masked packed-word updates and RAM collision adapters, reset/init realization, allocator/component and platform coherence contracts, finite-capacity DMA progress, and manual-burst cross-process synthesis eligibility. General alias/injectivity/progress proofs may remain Unknown for an individual program; choose a verified preserving fallback or issue a scoped capability diagnostic. Neither source inspection nor finite acceptance tests certify arbitrary concurrent layouts or a universal cost model.
