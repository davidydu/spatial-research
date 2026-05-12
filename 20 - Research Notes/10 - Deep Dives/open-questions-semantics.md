---
type: open-questions
topic: semantics
session: 2026-04-25
date_started: 2026-04-25
---

# Open Questions - Semantics

## Q-sem-01 - 2026-04-25 Atomic write recursion depth

`recurseAtomicLookup` is named recursively but appears to peel only one `AtomicRead` level before alias expansion. Confirm whether nested atomic reads should recurse to the outermost mutable container.

Source: `argon/src/argon/static/Staging.scala:245-250`; [[30 - Effects and Aliasing]]
Blocked by: main-session source review
Status: open
Resolution:

## Q-sem-02 - 2026-04-25 Mutable aliases in Rust ownership terms

Argon allows mutable alias errors to be disabled by `enableMutableAliases`. Decide whether the Rust port preserves this compatibility flag or makes mutable aliasing a hard error.

Source: `argon/src/argon/static/Staging.scala:39-75`; `argon/src/argon/Config.scala:46-47`; [[30 - Effects and Aliasing]]
Blocked by: Rust IR ownership design
Status: open
Resolution:

## Q-sem-03 - 2026-04-25 Default scheduler motion semantics

`SimpleScheduler` accepts `allowMotion` but always returns no motioned syms. The default scheduler branch also chooses `SimpleScheduler` on both sides. Decide whether to delete motion machinery or implement a real motion scheduler in Rust.

Source: `argon/src/argon/schedule/SimpleScheduler.scala:10-31`; `argon/src/argon/static/Scoping.scala:56-78`; [[60 - Scopes and Scheduling]]
Blocked by: scheduling design
Status: open
Resolution:

## Q-sem-04 - 2026-04-25 Pipe holder observability in HLS

`PipeInserter` routes escaping stage values through `Reg`, `FIFOReg`, or `Var` holders. Determine which holder effects must remain visible when HLS could otherwise schedule SSA values without explicit holders.

Source: `src/spatial/transform/PipeInserter.scala:170-209`; `src/spatial/transform/PipeInserter.scala:256-305`; [[50 - Pipe Insertion]]
Blocked by: HLS lowering design
Status: open
Resolution:

## Q-sem-05 - 2026-04-25 Operational meaning of Fork, ForkJoin, and PrimitiveBox

`CtrlSchedule` enumerates `ForkJoin`, `Fork`, and `PrimitiveBox`, but lower-level entries document mainly enum membership and consumers. Need a precise operational definition before treating these as first-class HLS schedules.

Source: `src/spatial/metadata/control/ControlData.scala:7-14`; `src/spatial/metadata/control/package.scala:193-219`; [[10 - Control]]
Blocked by: pass/codegen source review
Status: open
Resolution:

## Q-sem-06 - 2026-04-25 Scalagen parallel pipe serial execution

Scalagen emits `ParallelPipe` bodies sequentially, while hardware interprets parallelism structurally. Decide whether Rust simulation matches Scalagen source order or models parallel interleaving/back-pressure.

Source: `spatial/src/spatial/codegen/scalagen/ScalaGenController.scala:187-191`; [[50 - Controller Emission]]
Blocked by: simulator policy
Status: open
Resolution:

## Q-sem-07 - 2026-04-25 OOB simulator versus synthesized hardware

Scalagen logs OOB reads/writes and returns invalid/discards writes; hardware behavior is not naturally the same. Decide whether Rust offers Scalagen-compatible OOB plus stricter synthesis assertions.

Source: `spatial/emul/src/emul/OOB.scala:19-38`; `spatial/src/spatial/codegen/scalagen/ScalaGenMemories.scala:36-50`; [[30 - Memory Simulator]]
Blocked by: simulator/synthesis mode split
Status: open
Resolution:

## Q-sem-08 - 2026-04-25 LockDRAM fallback banking semantics

LockDRAM accessors fall back to unit banking, dispatch `{0}`, and a default port. Clarify whether this is required semantics or a temporary compatibility path.

Source: `src/spatial/metadata/memory/package.scala:168-245`; [[30 - Memory]]
Blocked by: LockDRAM design review
Status: open
Resolution:

## Q-sem-09 - 2026-04-25 Unbiased rounding nondeterminism

`FixedPoint.unbiased` calls `scala.util.Random.nextFloat()`, so unbiased fixed-point operations are nondeterministic. Decide whether Rust matches nondeterminism, seeds it, or replaces it with deterministic rounding.

Source: `spatial/emul/src/emul/FixedPoint.scala:232-241`; [[20 - Numeric Reference Semantics]]
Blocked by: simulator reproducibility policy
Status: open
Resolution:

## Q-sem-10 - 2026-04-25 FloatPoint clamp heuristics

`FloatPoint.clamp` includes an unexplained `x > 1.9` subnormal guard. Confirm whether this heuristic is required for bit compatibility or can be replaced by a cleaner custom-float algorithm.

Source: `spatial/emul/src/emul/FloatPoint.scala:335-339`; [[20 - Numeric Reference Semantics]]
Blocked by: numeric conformance tests
Status: open
Resolution:

## Q-sem-11 - 2026-04-25 FMA fused versus Scalagen unfused semantics

Scalagen emits `FixFMA` and `RegAccumFMA` as multiply-then-add, while Chisel hardware FMA may preserve fused precision. Decide whether Rust simulator and HLS backend match Scalagen or hardware.

Source: `spatial/src/spatial/codegen/scalagen/ScalaGenFixPt.scala:150`; `spatial/src/spatial/codegen/scalagen/ScalaGenReg.scala:57-64`; [[60 - Counters and Primitives]]
Blocked by: numeric backend policy
Status: open
Resolution:

## Q-sem-12 - 2026-04-25 AccumType lattice contradiction

Requested semantics say `Fold > Reduce > Buff > None > Unknown`, but the metadata entry reports source behavior `Fold > Buff > Reduce > None > Unknown`. Decide which order is authoritative.

Source: `src/spatial/metadata/memory/AccumulatorData.scala:11-45`; [[30 - Memory]]
Blocked by: source intent review
Status: open
Resolution:

## Q-sem-13 - 2026-04-25 DelayLine simulator parity versus cycle accuracy

Scalagen elides `DelayLine`, while Chisel retiming inserts real delay registers. Decide whether Rust simulation is value-only Scalagen-compatible or cycle-aware.

Source: `spatial/src/spatial/codegen/scalagen/ScalaGenDelays.scala:7-15`; `src/spatial/transform/RetimingTransformer.scala:205-220`; [[C0 - Retiming]]
Blocked by: simulator scope
Status: open
Resolution:

## Q-sem-14 - 2026-04-25 Target accepted II versus compilerII

Spatial records `compilerII` and selected `II`, but an HLS tool may accept, relax, or reject the requested II. Decide where the Rust+HLS flow records target-accepted II.

Source: `src/spatial/traversal/InitiationAnalyzer.scala:14-41`; [[C0 - Retiming]]
Blocked by: HLS reporting integration
Status: open
Resolution:

## Q-sem-15 - 2026-04-25 FIFO and LIFO elastic simulator versus back-pressure

Scalagen FIFO/LIFO/Stream enqueues grow queues without size checks; RTL/HLS queues should be bounded and back-pressured. Decide simulator policy and test expectations.

Source: `spatial/src/spatial/codegen/scalagen/ScalaGenFIFO.scala:41-44`; `spatial/src/spatial/codegen/scalagen/ScalaGenLIFO.scala:39-44`; `spatial/src/spatial/codegen/scalagen/ScalaGenStream.scala:92-97`; [[40 - FIFO LIFO Stream Simulation]]
Blocked by: simulator policy
Status: open
Resolution:

## Q-sem-16 - 2026-04-25 FieldDeq missing write effect

`StreamStruct.field` is documented as a dequeue, but `FieldDeq` does not currently declare `Effects.Writes(struct)`. Decide whether the effect system should model field dequeues as mutations.

Source: `src/spatial/node/StreamStruct.scala:12-16`; `src/spatial/lang/StreamStruct.scala:17-36`; [[60 - Streams and Blackboxes]]
Blocked by: effect-system/source review
Status: open
Resolution:

## Q-sem-17 - 2026-04-25 HLS host ABI manifest

Cppgen and Chiselgen emit `ArgAPI` manifests for scalar args, DRAM pointers, ArgIOs, ArgOuts, instrumentation, and exits. Decide the equivalent manifest format for Rust+HLS.

Source: `/Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenInterface.scala:138-164`; `src/spatial/codegen/chiselgen/ChiselGenInterface.scala:156-187`; [[10 - Cppgen]]
Blocked by: host runtime design
Status: open
Resolution:

## Q-sem-18 - 2026-04-25 Fixed-point host conversion parity

Cppgen maps fractional fixed-point host expressions to `double` while transfers use shifted raw integers. Decide whether the Rust host side should match Cppgen approximation or enforce bit-exact fixed-point values.

Source: `/Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenCommon.scala:75-100`; `/Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenInterface.scala:42-80`; [[10 - Cppgen]]
Blocked by: host numeric design
Status: open
Resolution:

## Q-sem-19 - 2026-04-25 OneHotMux multi-true semantics

Scalagen implements `OneHotMux` by collecting true lanes and reducing data with bitwise OR. This is only valid when exactly one selector is true and can be semantically wrong for multiple true lanes. Decide whether Rust matches Scalagen or asserts one-hotness.

Source: `spatial/src/spatial/codegen/scalagen/ScalaGenBits.scala:30-37`; `src/spatial/node/Mux.scala:19-37`; [[60 - Counters and Primitives]]
Blocked by: primitive semantics policy
Status: open
Resolution:
