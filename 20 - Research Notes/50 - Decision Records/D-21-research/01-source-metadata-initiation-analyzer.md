---
type: "research"
decision: "D-21"
angle: 1
---

# D-21 Angle 1: Source Metadata and InitiationAnalyzer Contract

## Bottom Line

For [[D-21]], Spatial already separates three compiler-side II concepts, but it does not have a fourth HLS-tool-accepted II. `userII` is the source/user request, `compilerII` is Spatial's analysis result, and `II` is the selected interval that downstream control generation sees. The decision queue asks where to record and reconcile an HLS backend's accepted II against those existing fields (`20 - Research Notes/40 - Decision Queue.md:91-93`). The safest Rust/HLS contract is therefore: keep the three Spatial meanings intact, add an explicit backend-accepted II/provenance slot, and treat mismatches as reportable schedule evidence rather than silently overwriting `compilerII`.

## Metadata Surface

The metadata carriers are in [[10 - Control]]. `BodyLatency` is analysis-set latency for an inner pipe body, `InitiationInterval` is the selected controller II, `UserII` is user-set, and `CompilerII` is analysis-set (`src/spatial/metadata/control/ControlData.scala:144-177`). The accessors make the defaults and names concrete: `bodyLatency` defaults to `Nil`, `II` defaults to `1.0`, `userII` is optional, and `compilerII` defaults to `1.0` (`src/spatial/metadata/control/package.scala:826-839`). User surface syntax enters through `Pipe.II(ii)` and `CtrlOpt.set`, which writes `x.userII = ii.map(_.toDouble)` while also recording the user schedule (`src/spatial/lang/control/Control.scala:22-33`, `src/spatial/lang/control/CtrlOpt.scala:18-22`). That means `userII` should remain a request, not proof that a scheduler achieved that interval.

Schedule context matters. The closed schedule enum includes `Sequenced`, `Pipelined`, `Streaming`, `ForkJoin`, `Fork`, and `PrimitiveBox` (`src/spatial/metadata/control/ControlData.scala:7-14`). Effective level and schedule are derived: blackboxes are inner, Host is outer, and single controllers collapse `Pipelined` to `Sequenced` while looped controllers keep their raw schedule (`src/spatial/metadata/control/package.scala:161-219`). [[30 - Control Semantics]] summarizes the same rule and states the important distinction: `compilerII` is the feasibility estimate, while `II` is the selected schedule interval after user overrides and sequenced collapse (`10 - Spec/20 - Semantics/30 - Control Semantics.md:47-49`).

## InitiationAnalyzer Rules

`InitiationAnalyzer` is the contract source cited by the queue and by [[C0 - Retiming]] (`10 - Spec/40 - Compiler Passes/C0 - Retiming.md:239-266`). For an outer controller, it first visits child blocks, computes `interval = max(1.0, child.II...)`, sets selected `II = userII.getOrElse(interval)`, and sets `compilerII = interval` (`src/spatial/traversal/InitiationAnalyzer.scala:14-20`). Outer `compilerII` is therefore a composition of already-selected child intervals, not a fresh latency calculation.

For an inner controller, it computes each block's `(latency, interval)` with `latencyAndInterval`; that helper derives max path latency and max cycle length, with segmented WAR cycles folded into the compiler interval (`src/spatial/util/modeling.scala:107-124`). The analyzer sums block latencies into `bodyLatency`, folds in blackbox II through `bboxII`, collects positive `iterDiff`s, and sets `compilerII` to `1.0`, `interval`, or `ceil(interval / minIterDiff)` (`src/spatial/traversal/InitiationAnalyzer.scala:23-40`). Selected `II` is then full `latency` for explicitly sequenced controls, otherwise `userII.getOrElse(min(compilerII, latency))` (`src/spatial/traversal/InitiationAnalyzer.scala:36-40`). [[70 - Timing Model]] frames this as timing semantics: II is not just metadata bookkeeping, and HLS should preserve `compilerII`, `userII`, and `bodyLatency` while separately recording backend acceptance (`10 - Spec/20 - Semantics/70 - Timing Model.md:57-65`).

## StateMachine Exception

`StateMachine` bypasses the generic inner/outer rule. The inner case is marked with a TODO to verify generality, then separately measures `notDone`, `action`, and `nextState`, detects action-written memories read by `nextState`, adds hidden state-register write latency, and raises the interval to `actionLatency` when those dependencies exist (`src/spatial/traversal/InitiationAnalyzer.scala:51-80`). It sets selected `II` from `userII.getOrElse(interval)` and `bodyLatency`, but notably does not set `compilerII` in this branch (`src/spatial/traversal/InitiationAnalyzer.scala:77-80`). The outer FSM case similarly computes interval from `notDone`, `nextState`, and child IIs, then sets selected `II` and a two-part `bodyLatency`, also without writing `compilerII` (`src/spatial/traversal/InitiationAnalyzer.scala:82-91`). For D-21, this is a migration hazard: Rust/HLS should decide whether FSM accepted-II reporting keys off selected `II`, a newly computed FSM `compilerII`, or an explicit "compiler estimate unavailable" state.
