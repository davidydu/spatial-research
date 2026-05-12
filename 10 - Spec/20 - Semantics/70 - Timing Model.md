---
type: spec
status: draft
concept: timing-model
source_files:
  - "src/spatial/traversal/RetimingAnalyzer.scala:1-121"
  - "src/spatial/transform/RetimingTransformer.scala:1-271"
  - "src/spatial/transform/DuplicateRetimeStripper.scala:1-36"
  - "src/spatial/traversal/IterationDiffAnalyzer.scala:15-217"
  - "src/spatial/traversal/InitiationAnalyzer.scala:12-101"
  - "src/spatial/util/modeling.scala:560-650"
  - "src/spatial/metadata/retiming/RetimingData.scala:6-53"
  - "src/spatial/metadata/retiming/ValueDelay.scala:5-19"
  - "src/spatial/metadata/retiming/package.scala:9-49"
  - "src/spatial/targets/LatencyModel.scala:10-67"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenDelays.scala:1-16"
source_notes:
  - "[[C0 - Retiming]]"
  - "[[20 - Latency Model]]"
  - "[[40 - Retiming]]"
  - "[[60 - Scopes and Scheduling]]"
  - "[[60 - Counters and Primitives]]"
  - "[[10 - Control]]"
hls_status: chisel-specific
depends_on:
  - "[[C0 - Retiming]]"
  - "[[20 - Latency Model]]"
  - "[[40 - Retiming]]"
  - "[[60 - Scopes and Scheduling]]"
  - "[[10 - Control]]"
---

# Timing Model

## Summary

Spatial timing semantics are a compiler model, not an Argon property. Argon blocks preserve effect order and scope structure in [[60 - Scopes and Scheduling]], but cycle timing is introduced by Spatial retiming, latency models, and initiation analysis. [[C0 - Retiming]] defines the analysis/transform pipeline that computes per-symbol delay and inserts `DelayLine` nodes; [[40 - Retiming]] defines the metadata that stores delay and cycle facts; [[20 - Latency Model]] defines target latency lookup and controller composition formulas; [[10 - Control]] stores `II`, `compilerII`, `userII`, and `bodyLatency`. The model is marked chisel-specific because current delay-line insertion is an RTL implementation technique, while HLS has its own scheduler.

## Formal Semantics

Latency has two layers. A node latency comes from target model lookup unless a forced latency is present. `latencyOf(s, inReduce)` first checks `hasForcedLatency`, then chooses either `latencyInReduce(s)` or `latencyOfNode(s)`; `builtInLatencyOfNode` and `requiresRegisters` are separate CSV fields used by retiming and area accounting (`src/spatial/targets/LatencyModel.scala:17-46`). Controller latency composition is schedule-sensitive: parallel is `max(stages) + node latency`; streaming is `stages.max * (N - 1) * ii + node latency`; metapipe adds `stages.sum`; sequential is `stages.sum * N + node latency` (`src/spatial/targets/LatencyModel.scala:48-66`). These formulas define pipeline fill and drain in the model, not the emitted RTL schedule by themselves.

Retiming metadata stores cycle and delay facts. `Cycle` is removed on transfer and has concrete `WARCycle` and `AAACycle` forms; `FullDelay` is mirrored; `UserInjectedDelay` is analysis-set; `ForcedLatency` is user-set (`src/spatial/metadata/retiming/RetimingData.scala:6-53`). `fullDelay` gives priority to `ForcedLatency`, otherwise reads mirrored `FullDelay` defaulting to `0.0`; `trace` recursively strips `DelayLine(_, data)` nodes (`src/spatial/metadata/retiming/package.scala:9-35`). `ValueDelay` is the transform-time lazy handle for a line: first `value()` call invokes the create closure and memoizes the staged symbol (`src/spatial/metadata/retiming/ValueDelay.scala:5-19`).

Forced user latency enters through the same metadata path as retiming results. `retime(delay, payload)` can stage a user-injected `DelayLine` and mark `userInjectedDelay`, while `ForcedLatency(latency){...}` writes `forcedLatency` on every symbol staged inside a scoped flow (`src/spatial/lang/api/MiscAPI.scala:19-33`, `src/spatial/lang/Latency.scala:7-11`). Because `fullDelay` prioritizes `ForcedLatency`, those user directives override analyzer-computed delay reads in later timing consumers.

`RetimingAnalyzer` computes delays for inner controls when retiming is enabled. Before analysis it resets existing `fullDelay` to zero, then `retimeBlock` gathers nested statements and block results, calls `pipeLatencies`, shifts latencies by the prior block's `lastLatency`, marks cycle members, and writes `fullDelay = latency - latencyOf(s, inReduce)` after scrubbed rounding (`src/spatial/traversal/RetimingAnalyzer.scala:21-55`, `src/spatial/util/modeling.scala:563-567`). For `StateMachine`, a custom push-later pattern retimes only selected blocks (`src/spatial/traversal/RetimingAnalyzer.scala:84-109`). Switches are excluded from the normal inner-control retimer path because they are not seen as inner controllers for PipeRetimer purposes.

`RetimingTransformer` materializes the analyzer's plan. It recomputes adjusted latencies, computes delay lines with `computeDelayLines`, creates or extends `ValueDelay`s, and substitutes consumer inputs through the appropriate line (`src/spatial/transform/RetimingTransformer.scala:205-220`, `src/spatial/util/modeling.scala:570-649`). For each statement, it registers delay substitutions for bit inputs, visits the statement with substitutions, and records the rewritten symbol (`src/spatial/transform/RetimingTransformer.scala:132-154`). Switches are special: each `SwitchCase` result may receive a trailing `DelayLine` so sibling case values align at the switch output (`src/spatial/transform/RetimingTransformer.scala:156-203`). `DuplicateRetimeStripper` canonicalizes adjacent `RetimeGate()` nodes before analysis by emitting only the first in a run (`src/spatial/transform/DuplicateRetimeStripper.scala:10-32`).

`RetimeGate` is a timing boundary. At the IR primitive level it has `Effects.Simple`, so effect scheduling and DCE preserve its relative position; retiming then treats it as a barrier/fence through the pass structure and duplicate stripping (`src/spatial/node/DelayLine.scala:8-14`, `src/spatial/transform/DuplicateRetimeStripper.scala:10-32`). `DelayLine(size, data)` is the concrete latency insertion node, with size zero rewritten to the payload at staging (`src/spatial/node/DelayLine.scala:8-10`). [[50 - Math and Helpers]] describes the user-facing `retime(delay, payload)` and `retimeGate()` hooks.

Delay-line sharing is also semantic. `RetimingTransformer.precomputeDelayLines` scans nested op blocks and materializes lines that need to exist at an outer hierarchy level before visiting sibling blocks, preventing duplicated delay hardware for the same producer and delay (`src/spatial/transform/RetimingTransformer.scala:111-130`). This is why `ValueDelay.alreadyExists` and its memoized `value()` method are part of [[40 - Retiming]], not an incidental implementation detail.

The transform also tracks substitution history so timing rewrites preserve producer identity. `registerDelay` stores all created `ValueDelay`s per traced producer, `substitute` chooses the closest requested delay, and `transformDelayLine` can extend an existing line instead of staging an unrelated new producer (`src/spatial/transform/RetimingTransformer.scala:21-88`). That behavior matters for downstream aliasing and hardware sharing.

II semantics are timing semantics, not only control metadata. `IterationDiffAnalyzer` computes loop-carried distances for accumulation cycles and special-cases `OpMemReduce` to zero and `OpReduce` to one (`src/spatial/traversal/IterationDiffAnalyzer.scala:17-118`, `src/spatial/traversal/IterationDiffAnalyzer.scala:193-210`). `InitiationAnalyzer` sets outer `compilerII` to max child II and inner `compilerII` to `1.0`, `interval`, or `ceil(interval / iterDiff)`; effective `II` then incorporates `userII` and sequenced-schedule overrides (`src/spatial/traversal/InitiationAnalyzer.scala:14-41`). A target-imposed II can still differ at backend level (inferred, unverified for HLS), so Rust should store both compiler-requested and backend-accepted values.

## Reference Implementation

Chisel retiming is the reference for cycle timing. Scalagen is intentionally not cycle-accurate here: `ScalaGenDelays` elides `DelayLine`, emitting a direct value alias for non-constant delay lines (`spatial/src/spatial/codegen/scalagen/ScalaGenDelays.scala:7-15`). [[60 - Counters and Primitives]] records this as a simulator/RTL divergence. Therefore there are two valid references depending on question: dynamic value semantics in Scalagen ignore delays, while RTL timing semantics use retiming metadata and inserted lines.

## HLS Implications

The HLS rewrite should preserve `compilerII`, `userII`, `bodyLatency`, and latency-model composition, but probably should not port Chisel delay-line insertion directly. HLS schedulers insert registers from pipeline pragmas and operator latencies. The Rust compiler can still use `IterationDiffAnalyzer`-style dependence distances to choose II and can use a latency model to report expected cycles. Any simulator mode that claims cycle accuracy must choose whether to match Scalagen delay elision or RTL delay lines.

## Open questions

- [[open-questions-semantics#Q-sem-13 - 2026-04-25 DelayLine simulator parity versus cycle accuracy]] tracks whether Rust simulation should match Scalagen's delay elision or Chisel cycle timing.
- [[open-questions-semantics#Q-sem-14 - 2026-04-25 Target accepted II versus compilerII]] tracks where an HLS backend records the II actually achieved by the tool.
