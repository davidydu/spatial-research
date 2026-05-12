---
type: "research"
decision: "D-20"
angle: 2
---

# D-20 Angle 2: RetimingTransformer and Scheduling Role

## Bottom Line

For [[D-20]], `DelayLine` should be treated as both, but not uniformly. A compiler-created `DelayLine` is a [[scheduling artifact]]: it is inserted by `RetimingTransformer` to make values arrive at the scheduled consumer time. In emitted hardware it is still real sequential state, but its semantic trace is the original value, not a source-level storage object. A user-created `retime(delay, payload)` is different: it is explicit [[semantic state]] in the hardware timing contract and is tagged as user-injected (`src/spatial/lang/api/MiscAPI.scala:23-31`, `src/spatial/metadata/retiming/package.scala:30-31`).

## Scheduling Source

The final pass order makes the role clear: `RetimingAnalyzer` runs, then `RetimingTransformer`, then `RetimeReporter`, then schedule finalization by `InitiationAnalyzer` (`src/spatial/Spatial.scala:226-233`). Retiming is gated by `enableRetiming` (`src/spatial/transform/RetimingTransformer.scala:17-18`, `src/spatial/SpatialConfig.scala:61-69`).

`RetimingAnalyzer` computes schedule positions with `pipeLatencies`, then writes `s.fullDelay = l`; if a symbol is in a cycle it also marks `s.inCycle = true` (`src/spatial/traversal/RetimingAnalyzer.scala:35-49`). `FullDelay` is documented as "delay of the given symbol from the start of its parent controller" and defaults to zero; the accessor is overridden by `ForcedLatency` when present (`src/spatial/metadata/retiming/RetimingData.scala:43-53`, `src/spatial/metadata/retiming/package.scala:15-21`). `InitiationAnalyzer` later recomputes block latency and interval from `latencyAndInterval`, stores `bodyLatency`, and chooses `II` (`src/spatial/traversal/InitiationAnalyzer.scala:23-40`). That means `fullDelay` is a local timing coordinate, while `bodyLatency`/`II` are controller-level scheduling summaries.

## DelayLine Creation

`RetimingTransformer` asks `computeDelayLines` for the missing alignment registers, passing known latencies, hierarchy, existing lines, and cycle symbols, plus a closure that stages `DelayLine(size, f(data))` (`src/spatial/transform/RetimingTransformer.scala:32-39`). The local `delayLine` helper only accepts `Bits` payloads, stages the `DelayLine`, and gives the new symbol a `_d<size>` name (`src/spatial/transform/RetimingTransformer.scala:68-74`).

The key equation is in `computeDelayLines`: for each reader, the target input arrival is `delayOf(reader) - latencyOf(reader)`, adjusted for reduction-cycle latency; for each bit input it subtracts already-achieved delay and any built-in template latency, then creates a `ValueDelay` when the integer delay is nonzero (`src/spatial/util/modeling.scala:570-648`). `ValueDelay` lazily creates and caches the actual symbol, and can extend a previous delay line instead of duplicating it (`src/spatial/metadata/retiming/ValueDelay.scala:5-18`, `src/spatial/util/modeling.scala:599-615`). During statement rewriting, `registerDelays` substitutes the delayed value only for the consumer being retimed (`src/spatial/transform/RetimingTransformer.scala:78-87`, `src/spatial/transform/RetimingTransformer.scala:142-152`). Precomputation exists because nested blocks may need the same delay symbol visible from an outer scope (`src/spatial/transform/RetimingTransformer.scala:102-125`).

## Gates And Cycles

`retimeGate()` stages a `RetimeGate`, an effectful void primitive (`src/spatial/lang/api/MiscAPI.scala:19-21`, `src/spatial/node/DelayLine.scala:12-13`). Gates affect scheduling in two ways. First, accumulation-cycle discovery refuses to connect a read/write pair across a gate (`src/spatial/util/modeling.scala:165-179`). Second, `pushRetimeGates` pushes nodes after the gate so they occur after the latest node before it (`src/spatial/util/modeling.scala:401-424`). A later sanity check enforces that any delayed statement after a gate has `fullDelay` greater than the pre-gate latest delay (`src/spatial/traversal/CompilerSanityChecks.scala:129-147`). Cycles themselves are returned by `pipeLatencies` as `WARCycle`/`AAACycle` records and feed both latency-in-reduce selection and II estimation (`src/spatial/metadata/retiming/RetimingData.scala:13-40`, `src/spatial/util/modeling.scala:516-559`).

## Semantic Classification

The `DelayLine` IR node is a primitive whose zero-size form rewrites to its input (`src/spatial/node/DelayLine.scala:8-10`). Its `trace` recursively strips delay lines back to the underlying data (`src/spatial/metadata/retiming/package.scala:23-28`). Scala and C++ codegen emit `DelayLine` as a plain assignment, while Chisel emits a retimed wire through `DL(..., delay)` and updates `maxretime` (`src/spatial/codegen/scalagen/ScalaGenDelays.scala:9-13`, `src/spatial/codegen/cppgen/CppGenDebug.scala:55`, `src/spatial/codegen/chiselgen/ChiselGenDelay.scala:16-30`). Also, model parameters report automatic `DelayLine` depth as zero unless `userInjectedDelay` is set (`src/spatial/targets/NodeParams.scala:41`).

So the decision rule is: preserve user-injected `retime` as semantic temporal state; treat transformer-injected `DelayLine` as compiler scheduling state that lowers to physical registers. HLS should therefore model automatic delay lines as schedule alignment obligations, not as user-visible memories, while retaining user retimes as observable timing directives.
