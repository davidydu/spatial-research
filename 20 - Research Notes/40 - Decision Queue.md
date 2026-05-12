---
type: decision-queue
project: spatial-spec
date: 2026-04-25
---

# Decision Queue — Architectural Choices for Rust+HLS Rewrite

25 items requiring user decision before the corresponding subsystem can be re-implemented.

## D-01 — [Q-036] Choose the HLS policy for BigIP optional arithmetic operations and simulator placeholders.
Source: fringe/src/fringe/BigIP.scala:22-105; fringe/src/fringe/targets/BigIPSim.scala:82-96
Decision criteria: User decision: HLS port rejects unsupported BigIP operations, preserves current simulator placeholders, or lowers them to named vendor/library implementations.

## D-02 — [Q-038] Define the grouping contract for priority and round-robin dequeues without relying on hash collisions.
Source: src/spatial/lang/api/PriorityDeqAPI.scala:11,17,26,47,97; src/spatial/metadata/access/AccessData.scala:43; src/spatial/transform/unrolling/MemoryUnrolling.scala:303-304
Decision criteria: User decision: priority/round-robin dequeue grouping preserves hash-based compatibility or introduces an explicit grouped-dequeue IR construct.

## D-03 — [Q-048] Decide whether the HLS frontend preserves Spatial unsupported `while`/`return` behavior.
Source: src/spatial/lang/api/SpatialVirtualization.scala:103-114
Decision criteria: User decision: Rust frontend preserves Spatial unsupported `while`/`return` restrictions or defines new HLS-visible semantics for them.

## D-04 — [Q-079] Define the HLS memory-resource taxonomy and allocator catch-all behavior.
Source: src/spatial/targets/MemoryResource.scala:6-10; src/spatial/targets/HardwareTarget.scala:44-45; src/spatial/traversal/MemoryAllocator.scala:56-103
Decision criteria: User decision: define the HLS memory-resource list, min-depth rules, capacity fields, and final catch-all allocation behavior.

## D-05 — [Q-083] Design the Rust/HLS replacement for Chisel instantiation globals.
Source: src/spatial/codegen/chiselgen/ChiselCodegen.scala:129-302; src/spatial/codegen/chiselgen/ChiselGenInterface.scala:121-152; src/spatial/codegen/chiselgen/ChiselGenController.scala:550-581; fringe/src/fringe/SpatialIP.scala:18-40; fringe/src/fringe/globals.scala:7-79
Decision criteria: User decision: define the Rust/HLS top-level manifest that replaces mutable Chisel/Fringe instantiation globals.

## D-06 — [Q-103] Choose the role of Spatial iteration-diff analysis in the HLS scheduler.
Source: src/spatial/traversal/IterationDiffAnalyzer.scala:17-169; src/spatial/traversal/InitiationAnalyzer.scala:23-41
Decision criteria: User decision: HLS scheduling reuses Spatial `iterDiff`, keeps it diagnostic-only, or replaces it with an HLS dependence/schedule model.

## D-07 — [Q-112] Choose the HLS banking-search pruning and partition-planning strategy.
Source: src/spatial/metadata/memory/BankingData.scala:547-563; src/spatial/traversal/banking/ExhaustiveBanking.scala:392-431; src/spatial/traversal/banking/MemoryConfigurer.scala:610-633
Decision criteria: User decision: HLS banking search reuses Spatial alpha/N/B search, constrains it to HLS partition forms, or replaces it with a new planner.

## D-08 — [Q-116] Choose the latency source for HLS DSE.
Source: src/spatial/dse/LatencyAnalyzer.scala:29-47; src/spatial/dse/DSEAnalyzer.scala:90-147
Decision criteria: User decision: HLS DSE latency comes from Spatial runtime-model parity, HLS reports/simulation, or a new estimator.

## D-09 — [Q-118] Choose deterministic or nondeterministic unbiased rounding for the Rust simulator.
Source: spatial/emul/src/emul/FixedPoint.scala:232-241; spatial/src/spatial/codegen/scalagen/ScalaGenFixPt.scala:111-114
Decision criteria: User decision: unbiased rounding matches JVM RNG nondeterminism, uses a seedable deterministic RNG, or becomes deterministic rounding.

## D-10 — [Q-130] Choose the Rust reference precision for transcendental functions.
Source: spatial/emul/src/emul/Number.scala:97-156
Decision criteria: User decision: Rust numeric runtime matches Scalagen f64 transcendentals, uses per-format MPFR/exact math, or matches synthesized hardware units.

## D-11 — [Q-132] Choose Rust simulator semantics for `breakWhen`.
Source: spatial/src/spatial/codegen/scalagen/ScalaGenController.scala:74-93
Decision criteria: User decision: Rust simulation matches Scalagen end-of-iteration `breakWhen` or synthesized immediate-break behavior.

## D-12 — [Q-137] Choose how Rust ownership handles Spatial mutable aliases.
Source: argon/src/argon/static/Staging.scala:39-75; argon/src/argon/Config.scala:46-47; [[30 - Effects and Aliasing]]
Decision criteria: User decision: Rust IR preserves the `enableMutableAliases` compatibility flag or makes mutable aliasing a hard error.

## D-13 — [Q-139] Choose whether HLS lowering preserves pipe holders as observable state.
Source: src/spatial/transform/PipeInserter.scala:170-209; src/spatial/transform/PipeInserter.scala:256-305; [[50 - Pipe Insertion]]
Decision criteria: User decision: HLS lowering must preserve `Reg`/`FIFOReg`/`Var` pipe holders as observable state or may optimize them to SSA where legal.

## D-14 — [Q-140] Define operational semantics for `Fork`, `ForkJoin`, and `PrimitiveBox`.
Source: src/spatial/metadata/control/ControlData.scala:7-14; src/spatial/metadata/control/package.scala:193-219; [[10 - Control]]
Decision criteria: User decision: define operational semantics for `Fork`, `ForkJoin`, and `PrimitiveBox` schedules in the Rust/HLS scheduler.

## D-15 — [Q-141] Choose simulation semantics for `ParallelPipe`.
Source: spatial/src/spatial/codegen/scalagen/ScalaGenController.scala:187-191; [[50 - Controller Emission]]
Decision criteria: User decision: Rust simulation follows Scalagen sequential `ParallelPipe` execution or models parallel interleaving/back-pressure.

## D-16 — [Q-142] Choose the Rust policy for out-of-bounds simulator versus synthesis behavior.
Source: spatial/emul/src/emul/OOB.scala:19-38; spatial/src/spatial/codegen/scalagen/ScalaGenMemories.scala:36-50; [[30 - Memory Simulator]]
Decision criteria: User decision: Rust offers Scalagen-compatible OOB log/invalid behavior, synthesis assertions, or separate simulator/synthesis modes.

## D-17 — [Q-144] Choose the canonical unbiased rounding policy.
Source: spatial/emul/src/emul/FixedPoint.scala:232-241; [[20 - Numeric Reference Semantics]]
Decision criteria: User decision: unbiased rounding matches nondeterministic Spatial behavior, becomes seedable, or is replaced by deterministic rounding.

## D-18 — [Q-145] Choose whether to reproduce `FloatPoint.clamp` heuristics bit-for-bit.
Source: spatial/emul/src/emul/FloatPoint.scala:335-339; [[20 - Numeric Reference Semantics]]
Decision criteria: User decision: Rust float packing reproduces the `x > 1.9` clamp heuristic bit-for-bit or adopts a cleaner custom-float algorithm with accepted divergence.

## D-19 — [Q-146] Choose fused or unfused FMA precision for Rust+HLS.
Source: spatial/src/spatial/codegen/scalagen/ScalaGenFixPt.scala:150; spatial/src/spatial/codegen/scalagen/ScalaGenReg.scala:57-64; [[60 - Counters and Primitives]]
Decision criteria: User decision: HLS port matches Scalagen unfused multiply-add precision or Chisel/HLS fused FMA precision.

## D-20 — [Q-148] Choose value-only or cycle-aware `DelayLine` semantics.
Source: spatial/src/spatial/codegen/scalagen/ScalaGenDelays.scala:7-15; src/spatial/transform/RetimingTransformer.scala:205-220; [[C0 - Retiming]]
Decision criteria: User decision: Rust simulation is value-only and elides `DelayLine`, or is cycle-aware and models retiming registers.

## D-21 — [Q-149] Define the contract for HLS tool-accepted II versus compiler II metadata.
Source: src/spatial/traversal/InitiationAnalyzer.scala:14-41; [[C0 - Retiming]]
Decision criteria: User decision: define where the flow records and reconciles HLS tool-accepted II versus Spatial `compilerII`/requested II.

## D-22 — [Q-150] Choose FIFO/LIFO/stream elastic simulation versus bounded back-pressure semantics.
Source: spatial/src/spatial/codegen/scalagen/ScalaGenFIFO.scala:41-44; spatial/src/spatial/codegen/scalagen/ScalaGenLIFO.scala:39-44; spatial/src/spatial/codegen/scalagen/ScalaGenStream.scala:92-97; [[40 - FIFO LIFO Stream Simulation]]
Decision criteria: User decision: simulator and HLS semantics use Scalagen elastic queues or bounded FIFO/LIFO/stream back-pressure with overflow checks.

## D-23 — [Q-152] Define the Rust/HLS host ABI manifest.
Source: /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenInterface.scala:138-164; src/spatial/codegen/chiselgen/ChiselGenInterface.scala:156-187; [[10 - Cppgen]]
Decision criteria: User decision: define the Rust/HLS host ABI manifest for scalar args, DRAM pointers, ArgIO/ArgOuts, counters, exits, and streams.

## D-24 — [Q-153] Choose bit-exact or Cppgen-compatible fixed-point host conversion.
Source: /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenCommon.scala:75-100; /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenInterface.scala:42-80; [[10 - Cppgen]]
Decision criteria: User decision: Rust host-side fixed-point conversions match Cppgen double approximations or enforce bit-exact shifted-integer values.

## D-25 — [Q-154] Define multi-true `OneHotMux` semantics.
Source: spatial/src/spatial/codegen/scalagen/ScalaGenBits.scala:30-37; src/spatial/node/Mux.scala:19-37; [[60 - Counters and Primitives]]
Decision criteria: User decision: HLS `OneHotMux` with multiple true selectors matches Scalagen OR-reduce, asserts one-hotness, or defines priority semantics.
