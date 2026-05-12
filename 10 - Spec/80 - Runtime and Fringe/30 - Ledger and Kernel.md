---
type: spec
concept: Ledger and Kernel
source_files:
  - "fringe/src/fringe/templates/Ledger.scala:67-326"
  - "fringe/src/fringe/templates/ModuleParams.scala:8-16"
  - "fringe/src/fringe/SpatialBlocks.scala:20-172"
  - "fringe/src/fringe/templates/Controllers.scala:9-332"
  - "fringe/src/fringe/templates/counters/Counter.scala:477-563"
  - "fringe/src/fringe/templates/memory/DRAMAllocator.scala:30-50"
  - "fringe/src/fringe/templates/memory/MemInterfaceType.scala:12-220"
  - "fringe/src/fringe/templates/memory/MergeBuffer.scala:306-369"
  - "fringe/src/fringe/globals.scala:26-31"
  - "src/spatial/codegen/chiselgen/ChiselGenController.scala:102-134"
source_notes:
  - "[[fringe-and-targets]]"
hls_status: chisel-specific
hls_reason: "Ledger and Kernel are Chisel module-boring/elaboration scaffolding; HLS needs an explicit connectivity graph instead"
depends_on:
  - "[[40 - Controller Emission]]"
  - "[[40 - Hardware Templates]]"
status: draft
---

# Ledger and Kernel

## Summary

`Ledger` and `Kernel` are the Chiselgen support layer for modular controller emission. Generated controller kernels are not always emitted as one flat module; when `globals.enableModular` is true, ports used inside nested kernels must be recorded and later bored through module boundaries. `Ledger` is the mutable registry for that cross-kernel connectivity, while `Kernel.configure` wires each generated kernel's state machine, counter chains, parent/child signals, and streaming special cases (`fringe/src/fringe/templates/Ledger.scala:71-326`, `fringe/src/fringe/SpatialBlocks.scala:96-172`). The global modular flag defaults to true in `fringe.globals` (`fringe/src/fringe/globals.scala:26-31`).

## Ledger registry

`ControllerStack.stack` stores the active kernel ancestry as `KernelHash` values (`fringe/src/fringe/templates/Ledger.scala:67-69`). `Ledger` defines `OpHash`, `KernelHash`, `BoreMap`, verbose debug output, a global `connections: HashMap[OpHash, BoreMap]`, and separate maps for instrumentation counter IDs and breakpoint IDs below kernels (`fringe/src/fringe/templates/Ledger.scala:71-86`, `fringe/src/fringe/templates/Ledger.scala:156-158`). Its header comment walks through a nested kernel tree and shows the intended inclusive accumulation: a port used in a leaf is registered for that leaf and for each ancestor kernel on the stack, so module exits know which signals to expose (`fringe/src/fringe/templates/Ledger.scala:7-66`).

`ExposedPorts` is the per-kernel payload. It tracks read ports, write ports, struct fields, broadcast read/write ports, reset, output, access-active inputs, stage-control ports, merge enqueue/dequeue/bound/init ports, and allocator/deallocator ports (`fringe/src/fringe/templates/Ledger.scala:87-118`). It can test for emptiness, merge another exposed-port set into itself, and log non-empty categories when verbose debugging is enabled (`fringe/src/fringe/templates/Ledger.scala:119-154`).

Registry operations are small but load-bearing. `lookup(op)` returns the exposed ports for the current stack head if a mapping exists, otherwise a new empty set (`fringe/src/fringe/templates/Ledger.scala:175-179`). `substitute(oldHash, newHash)` rekeys an existing op map and merges with a current map, which compensates when generated modules end up with different hash identities (`fringe/src/fringe/templates/Ledger.scala:181-190`). `enter(ctrl, name)` and `exit()` push and pop the global controller stack during traversal (`fringe/src/fringe/templates/Ledger.scala:315-323`).

The `connect*` methods are the write side. `connectRPort`, `connectWPort`, `connectStructPort`, `connectBroadcastW/R`, `connectReset`, `connectOutput`, `connectAccessActivesIn`, `connectStageCtrl`, `connectMergeEnq/Deq/Bound/Init`, and `connectAllocDealloc` all check `globals.enableModular`, get or create the op's `BoreMap`, and add the relevant port to every kernel currently on the implicit stack (`fringe/src/fringe/templates/Ledger.scala:193-290`). `tieInstrCtr`, `connectInstrCtrs`, `tieBreakpoint`, and `connectBreakpoints` use the same stack idea for instrumentation counters and breakpoint signals (`fringe/src/fringe/templates/Ledger.scala:292-313`). `DRAMAllocatorIO.connectAlloc` and `connectDealloc` are representative clients: they write a lane's app request and then call `Ledger.connectAllocDealloc(this.hashCode, lane)` (`fringe/src/fringe/templates/memory/DRAMAllocator.scala:30-50`).

## Kernel scaffold

`CtrObject` captures counter start/stop/step values as either static `Option[Int]` or dynamic `FixedPoint`, plus parallelism, width, and forever status (`fringe/src/fringe/SpatialBlocks.scala:20-31`). `CChainObject` constructs a `CounterChain`, sets dynamic stops/strides/starts into its setup ports, and enables saturation (`fringe/src/fringe/SpatialBlocks.scala:33-44`). The `CounterChainInterface` exposes setup starts/stops/strides, `saturate`, `isStream`, reset/enable, and a `CChainOutput` with counts, out-of-bounds flags, noop, done, and saturated (`fringe/src/fringe/templates/counters/Counter.scala:477-492`). `CounterChain` instantiates one `SingleCounter` per dimension, enables outer counters from inner `done`, computes aggregate done/saturated/noop, and flattens counts into output lanes (`fringe/src/fringe/templates/counters/Counter.scala:500-563`).

`Kernel` is not itself a Chisel `Module`; it is an abstract container around wires, a `GeneralControl`, an `IICounter`, optional counter chains, and parent/child metadata (`fringe/src/fringe/SpatialBlocks.scala:74-115`). Its `InputKernelSignals` carry state-machine outputs into the concrete kernel, including done/mask/II signals, backpressure/forwardpressure, datapath enable, state, child enables/selects/acks, and counter outputs; `OutputKernelSignals` carry child done/masks, next/init state, done condition, cchain enables, and streaming counter-copy done signals back outward (`fringe/src/fringe/SpatialBlocks.scala:47-72`).

`configure` wires a kernel after construction. It feeds cchain outputs and switch select vectors into the kernel, connects state-machine state, next/init/done condition, enable outs, child acks, done/mask inputs, backpressure, reset, parent ack, base enable, datapath enable, II counter, and counter-chain enable/reset (`fringe/src/fringe/SpatialBlocks.scala:117-158`). Streaming outer controllers are special: `ctrCopyDone` is routed through `mySignalsOut`, child counter chains receive per-child enables, and a streaming parent either receives cchain-enable pulses or child copy-done pulses depending on whether the parent has a counter chain (`fringe/src/fringe/SpatialBlocks.scala:159-170`).

## Control templates and parameters

`ControlInterface` is the common state-machine port set: enable/done/reset, counter done/inc/reset, parent ack, backpressure, break, child done/mask inputs, child enable/ack outputs, switch selects, FSM state, and streaming `ctrCopyDone` (`fringe/src/fringe/templates/Controllers.scala:9-43`). `ControlParams` records schedule, depth, FSM/passthrough flags, state width, case count, latency, and name; `Sched` has `Sequenced`, `Pipelined`, `Streaming`, `Fork`, and `ForkJoin` singleton objects (`fringe/src/fringe/templates/Controllers.scala:45-67`). `OuterControl` pattern-matches the schedule and builds child synchronization, active/done SRFFs, counter increments, datapath enable, done, and done latch (`fringe/src/fringe/templates/Controllers.scala:69-252`). `InnerControl` is the simpler local controller for a single body, with optional passthrough and FSM modes (`fringe/src/fringe/templates/Controllers.scala:256-332`).

`ModuleParams` is a second process-global mutable registry. It stores `HashMap[String, Any]`, adds only the first payload for a name, and retrieves payloads by exact name (`fringe/src/fringe/templates/ModuleParams.scala:8-16`). It is an elaboration-time parameter side channel rather than a typed API.

## HLS notes

For HLS, this should become an explicit connectivity and scheduling graph. The meaningful semantics are ancestor-inclusive port exposure, controller schedule modes, counter-chain progression, II gating, and streaming copy-done behavior. Hash-code identity, mutable singleton maps, Chisel boring, and insert-once `Any` parameters are implementation artifacts that should not survive the rewrite.

## Open questions

- None beyond the consolidated connectivity questions in [[20 - Open Questions]].
