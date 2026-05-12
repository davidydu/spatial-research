---
type: "research"
decision: "D-11"
angle: 9
---

# Precedent and HLS Patterns for Early Exit

## 1. Spatial Baseline

Spatial precedent is structured, controller-local early exit rather than arbitrary host-language control flow. D-03 is useful background: source `while`, `do while`, and early `return` are rejected before they become Spatial IR, while supported dynamic control is expressed through `Foreach`, `FSM`, and `breakWhen`/`stopWhen` ([[D-03]]). That matters for D-11 because `breakWhen` is not a syntactic `break`; it is an explicit stop register carried by `UnitPipe`, `OpForeach`, `OpReduce`, `OpMemReduce`, and unrolled loop nodes (`src/spatial/node/Control.scala:33-139`). The public API comments for `Stream(breakWhen)` and `Sequential(breakWhen)` say the controller breaks immediately and resets the register on controller finish (`src/spatial/lang/control/Control.scala:41-56`).

## 2. C-Style Break at Top or Body

C/HLS frontends commonly model `break` as control-flow inside a loop CFG, either by checking a guard at the top of the next iteration or by branching out from a body point (unverified). That distinction is exactly the D-11 fault line. ScalaGen's loop-shaped lowering is top-tested: forever loops become `while(hasItems && !stopWhen.value)`, and bounded loops become `takeWhile(!stopWhen.value)` (`src/spatial/codegen/scalagen/ScalaGenController.scala:74-95`). If the loop body sets the stop register, the current Scala iteration can still complete. By contrast, a body-position `break` in C-like semantics would skip later statements in the same iteration (unverified). Therefore "support break" is too coarse: D-11 must name whether the observable commit point is next-iteration guard, body-point exit, or hardware controller kill.

## 3. Ready/Valid Stream Termination

Dataflow DSLs and HLS stream designs often use ready/valid protocols plus an out-of-band done, last, or empty condition to terminate a stream region (unverified). Spatial has several local versions of that pattern. Fringe app streams are `Decoupled` command/data channels, generic streams carry a `last` bit, and AXI-stream IO appears as ready/valid-style bundles (`fringe/src/fringe/FringeBundles.scala:41-88`, `fringe/src/fringe/FringeBundles.scala:193-207`, `fringe/src/fringe/AccelTopInterface.scala:16-18`). Chisel stream reads drive `ready` from enables and `datapathEn`, while stream writes drive `valid` from `datapathEn`, issue, enables, and backpressure (`src/spatial/codegen/chiselgen/ChiselGenStream.scala:34-45`, `src/spatial/codegen/chiselgen/ChiselGenStream.scala:139-167`). Scala simulation, however, often uses queues: stream input termination is `.nonEmpty`, and outer stream controls can run children until readable inputs are exhausted (`src/spatial/codegen/scalagen/ScalaGenController.scala:14-37`; `emul/src/emul/Stream.scala:5-51`). This precedent says stream termination is protocol-shaped, not just loop-shaped.

## 4. Stop Flags and Controller Kill

The strongest local pattern for early exit is a stop flag consumed by the controller state machine. Metadata can recover a controller's breaker from `stopWhen`, and `UseAnalyzer` marks that register as `isBreaker` so it is preserved rather than treated as an unused register (`src/spatial/metadata/control/package.scala:423-431`, `src/spatial/traversal/UseAnalyzer.scala:54-63`). ChiselGen reads the stop register, connects its reset to controller done, and assigns it to `sm.io.break` (`src/spatial/codegen/chiselgen/ChiselGenController.scala:312-315`). Fringe controllers then OR `io.break` into active resets, iter-done/done sets, child acknowledgement, and inner-controller done behavior (`fringe/src/fringe/templates/Controllers.scala:105-117`, `fringe/src/fringe/templates/Controllers.scala:129-139`, `fringe/src/fringe/templates/Controllers.scala:212-269`). This is more like a controller kill/finish signal than a source-level loop branch.

## 5. Simulator-vs-Hardware Correlation and D-11 Implications

The direct precedent is mixed but explicit. ScalaGen warns that Scala break occurs at loop end while `--synth` break occurs immediately (`src/spatial/codegen/scalagen/ScalaGenController.scala:75-93`). Hardware codegen and Fringe implement a break signal that participates in controller completion and datapath gating, while Scala queue/counter simulation implements a top-tested loop. General HLS practice also treats simulator/hardware correlation as a first-class requirement for side effects, streams, and trip counts (unverified).

D-11 should therefore avoid describing the choice as merely "breakWhen support." The decision should pick one normative commit model: Scalagen-compatible next-iteration guard, Chisel/HLS-compatible immediate controller break, or dual mode. Precedent favors immediate break for architectural semantics because the API comments, IR field, metadata, Chisel wiring, and Fringe controller all point that way. If legacy Scala golden compatibility matters, keep it as an explicit compatibility mode and add diagnostics for post-break side effects that would differ under immediate hardware termination.
