---
type: "research"
decision: "D-03"
angle: 4
---

# Usage Survey: Apps, Tests, and Migration Pressure

## Scope

Surveyed `apps/src`, `test/spatial/tests`, `pirTest`, and regression lists for user-facing `while`, `do while`, Scala `return`, `FSM`, and `breakWhen` patterns, excluding generated `target` output and ordinary compiler/library implementation code from corpus counts. The baseline language behavior is already explicit elsewhere in the source: Spatial's virtualized frontend rejects `return`, `while`, and `do while` with diagnostics rather than staging them (`src/spatial/lang/api/SpatialVirtualization.scala:103-114`). Forge's default hooks would otherwise macro-expand those constructs back to ordinary Scala control (`forge/src/forge/EmbeddedControls.scala:49-52`, `forge/src/forge/EmbeddedControls.scala:131-144`), so the survey treats raw `while`/`return` in apps/tests as attempted unsupported surface syntax, not as a hidden HLS feature.

## Negative Matches

The app/test corpus does not appear to contain executable user-level `while`, `do while`, or Scala `return`. The only `return`-adjacent executable line found is a final `()` used to force a `Void` result after a `MemReduce`, explicitly documented as avoiding the real return type of the expression rather than returning early (`test/spatial/tests/apps/Inference.scala:482-490`). Other `return` and `while` hits were comments or prose, not code to migrate. This means preserving the current rejection behavior should not break checked-in apps by removing a working construct they currently use.

## Positive Patterns

The live replacement idioms are Spatial-native termination forms. `breakWhen` is a first-class option carried by `Stream` and `Sequential`: the API comments say those controllers break immediately when the register is true and reset the register when the controller finishes (`src/spatial/lang/control/Control.scala:41-56`). The IR stores that register as `stopWhen` on unit pipes and loops (`src/spatial/node/Control.scala:33-50`, `src/spatial/node/Control.scala:121-140`), and metadata exposes it as each controller's breaker/stop condition (`src/spatial/metadata/control/package.scala:423-430`, `src/spatial/metadata/control/package.scala:952-959`).

Tests exercise this surface directly. `Breakpoint` breaks a bounded `Sequential.Foreach` when `stop2` or `stop4` becomes true, and breaks an unbounded `Stream.Foreach(*)` when a FIFO value reaches the target (`test/spatial/tests/feature/control/Breakpoint.scala:62-91`). `StreamPipeFlush` uses an unbounded stream plus a `break` register set after eight output values are drained, which is precisely a structured early-exit loop (`test/spatial/tests/feature/dynamic/StreamPipeFlush.scala:12-49`). `PriorityDeq` uses both `Stream(breakWhen = kill)` and long bounded `Sequential(breakWhen = kill)` loops to stop producer/consumer tests once a kill token arrives (`test/spatial/tests/feature/dynamic/PriorityDeq.scala:48-56`, `test/spatial/tests/feature/dynamic/PriorityDeq.scala:283-307`).

## FSM Workarounds

`FSM` is the more expressive workaround for data-dependent loops. The API stages explicit `notDone`, `action`, and `nextState` lambdas into `StateMachine` (`src/spatial/lang/control/FSM.scala:8-24`), and the node records those three blocks separately (`src/spatial/node/Control.scala:103-118`). CHStone has many hand-lowered while-shaped loops: `next_marker` runs until a marker appears or the input FIFO empties (`test/spatial/tests/apps/CHStone.scala:285-294`), `get_dqt` updates `length` until it reaches zero (`test/spatial/tests/apps/CHStone.scala:297-321`), `get_dht` loops while encoded Huffman table data remains (`test/spatial/tests/apps/CHStone.scala:381-427`), and Huffman decoding uses FSM state named `whilst` until `code <= max_decode` (`test/spatial/tests/apps/CHStone.scala:1140-1158`). MachSuite shows the same pressure in algorithmic kernels: backtracking uses `state != doneState` (`test/spatial/tests/apps/SW.scala:118-140`), KMP preprocessing/search use FSMs around conditions that are commented as `whileCond` (`test/spatial/tests/apps/MachSuite.scala:1315-1323`, `test/spatial/tests/apps/MachSuite.scala:1335-1340`), and graph traversal iterates BFS horizons with `horizon < N_LEVELS` (`test/spatial/tests/apps/MachSuite.scala:3032-3040`).

## D-03 Reading

Current checked-in Spatial apps depend on the restriction in the compatibility sense: they have already been authored against a language where raw `while`/`do while`/`return` are unavailable, and they use `FSM` or `breakWhen` where HLS-visible early exit is needed. Migration pressure is still real, but it is ergonomic rather than breakage-driven. New Rust/HLS-visible `while` semantics would mainly collapse verbose FSM encodings and make source-to-source ports of C/Scala algorithms less contorted (unverified). New `return` semantics have weaker corpus evidence: the surveyed apps do not show early-return workarounds comparable to the `while`-shaped FSMs.

Recommendation for D-03: preserve rejection as the compatibility baseline, but define any new `while` semantics as sugar over the existing `StateMachine`/`stopWhen` model rather than as a separate control primitive. Treat `return` as a separate design question with low app-corpus pressure.
