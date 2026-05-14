---
type: spec
concept: controllers
aliases:
  - "10 - Controllers"
source_files:
  - "src/spatial/lang/control/Control.scala:9-72"
  - "src/spatial/lang/control/CtrlOpt.scala:8-27"
  - "src/spatial/lang/control/AccelClass.scala:8-20"
  - "src/spatial/lang/control/ForeachClass.scala:9-35"
  - "src/spatial/lang/control/ReduceClass.scala:9-97"
  - "src/spatial/lang/control/MemReduceClass.scala:11-104"
  - "src/spatial/lang/control/NamedClass.scala:4-9"
  - "src/spatial/lang/control/Parallel.scala:9-14"
  - "src/spatial/lang/control/FSM.scala:8-25"
  - "src/spatial/lang/Latency.scala:7-11"
source_notes:
  - "[[language-surface]]"
hls_status: clean
depends_on:
  - "[[30 - Primitives]]"
  - "[[20 - Memories]]"
  - "[[90 - Aliases and Shadowing]]"
status: draft
---

# Controllers

## Summary

Controllers are the control-flow constructs of Spatial: `Accel`, `Foreach`, `Reduce`, `Fold`, `MemReduce`, `MemFold`, `Pipe`, `Stream`, `Sequential`, `Parallel`, `FSM`, and `Named`. They are the DSL-surface names an app writer uses to stage control IR nodes (`AccelScope`, `OpForeach`, `OpReduce`, `OpMemReduce`, `UnitPipe`, `ParallelPipe`, `StateMachine`). Each controller is implemented as a small wrapper that invokes `stage(...)` on a node and, via the `CtrlOpt.set` callback, attaches scheduling metadata (schedule type, II, POM/MOP unroll style, no-bind, halt-if-starved). The lazy-val builder pattern (`Directives` base class) lets the user chain modifiers — `Pipe.II(3).POM.Foreach(0 until N){ ... }` — without mutating state or constructing explicit types.

## Syntax / API

User-facing names (aliased via `InternalAliases` — `src/spatial/lang/Aliases.scala:24-36`):

```scala
Accel { ... }                             // src/spatial/lang/control/AccelClass.scala:17
Accel(*) { ... }                          // src/spatial/lang/control/AccelClass.scala:11-14
Foreach(ctr){ i => ... }                  // src/spatial/lang/control/ForeachClass.scala:10
Foreach(c0, c1){ (i,j) => ... }           // src/spatial/lang/control/ForeachClass.scala:14
Reduce(zero){ ctr => ... }{ _ + _ }       // src/spatial/lang/control/ReduceClass.scala:78-84
Fold(zero){ ctr => ... }{ _ + _ }         // src/spatial/lang/control/ReduceClass.scala:90-97
MemReduce(accum){ ctr => ... }{ _ + _ }   // src/spatial/lang/control/MemReduceClass.scala:96-99
MemFold(accum){ ctr => ... }{ _ + _ }     // src/spatial/lang/control/MemReduceClass.scala:101-104
Pipe { ... }                              // src/spatial/lang/control/Control.scala:24-27
Stream { ... }                            // src/spatial/lang/control/Control.scala:37
Sequential { ... }                        // src/spatial/lang/control/Control.scala:51
Parallel { ... }                          // src/spatial/lang/control/Parallel.scala:10-13
FSM(init){ notDone }{ action }{ next }    // src/spatial/lang/control/FSM.scala:9-16
Named("foo").Pipe { ... }                 // src/spatial/lang/control/NamedClass.scala:6
```

Modifier chain (applies to `Pipe`, plus haltIfStarved on `Stream`):

- `.II(n)` — `src/spatial/lang/control/Control.scala:29`. Sets initiation interval.
- `.POM` — `Control.scala:30`. Unroll as parallel of metapipes.
- `.MOP` — `Control.scala:31`. Unroll as metapipe of parallels.
- `.NoBind` — `Control.scala:32`. Forbid controller binding.
- `.haltIfStarved` — `Control.scala:33` (Pipe) and `Control.scala:47` (Stream). Stop controller when its FIFO inputs run dry.

## Semantics

A controller stages one IR node. The node captures: **schedule** (`Pipelined`/`Streaming`/`Sequenced`, preset on `Directives` at class-level — `Control.scala:23,35,49`); **initiation interval** (`options.ii` → `x.userII = ii.map(_.toDouble)`, `CtrlOpt.scala:21`); **unroll style** (MOP/POM bit, `CtrlOpt.scala:22-23`); **no-bind** and **halt-if-starved** flags (`CtrlOpt.scala:24-25`); **name** (`CtrlOpt.scala:20`); **stop-when register** (passed into the node constructor, not via metadata — `Control.scala:25-27,46`).

The body is always staged via `stageBlock`/`stageLambda1`/`stageLambda2` so the effects and symbol graph are captured as a nested block.

`Accel` is special. `AccelClass.apply(scope)` (`AccelClass.scala:17-19`) stages `AccelScope(stageBlock { scope; void })`. `Accel(*)(scope)` (`AccelClass.scala:11-14`) wraps the scope in `Stream.Foreach(*){ _ => scope }` — an implicit infinite outer stream loop.

`FSM` stages a `StateMachine` node built from three staged lambdas plus an initial state (`FSM.scala:18-23`): bound variable, not-done predicate, action, next-state.

## Implementation

### The `Directives` pattern

`abstract class Directives(val options: CtrlOpt)` (`src/spatial/lang/control/Control.scala:9-20`) is the base class for everything schedule-aware. It provides:

```scala
lazy val Foreach   = new ForeachClass(options)      // Control.scala:10
lazy val Reduce    = new ReduceClass(options)       // Control.scala:11
lazy val Fold      = new FoldClass(options)         // Control.scala:12
lazy val MemReduce = new MemReduceClass(options)    // Control.scala:13
lazy val MemFold   = new MemFoldClass(options)      // Control.scala:14
```

The `lazy val` is important: it lets `Pipe.II(3).Foreach(...)` work because `.II(3)` returns a new `Pipe` with an updated `CtrlOpt`, and that `Pipe`'s `.Foreach` builder picks up the updated options. Each `lazy val` is memoized per-instance so re-access returns the same `ForeachClass`.

`Directives` also owns `unit_pipe` — the shared helper for staging a `UnitPipe`:

```scala
@rig protected def unit_pipe(func: => Any, ens: Set[Bit] = Set.empty, stopWhen: Option[Reg[Bit]] = None): Void = {
  val block = stageBlock{ func; void }
  stageWithFlow(UnitPipe(Set.empty, block, stopWhen)){pipe => options.set(pipe) }
}
```

Source: `Control.scala:16-19`. The `stageWithFlow` form runs `options.set(pipe)` immediately after staging so metadata lands on the freshly-created symbol.

### `Pipe`, `Stream`, `Sequential`

Each of these is a class that constructs a default `CtrlOpt` for its schedule (`Control.scala:22-57`):

```scala
class Pipe(name, ii, directive, nobind, stopWhen, haltIfStarved)
    extends Directives(CtrlOpt(name, Some(Pipelined), ii, stopWhen = stopWhen,
                               mop = directive == Some(MetapipeOfParallels),
                               pom = directive == Some(ParallelOfMetapipes),
                               nobind = nobind, haltIfStarved = haltIfStarved))
```

`Control.scala:22-23`. The modifier chain (`II`, `POM`, `MOP`, `NoBind`, `haltIfStarved`) returns a new `Pipe` each time: e.g. `def II(ii: Int) = new Pipe(name, Some(ii), directive, nobind, stopWhen, haltIfStarved)` — `Control.scala:29`. No mutation; only re-construction.

`Stream` is simpler: only name, stopWhen, haltIfStarved (`Control.scala:35-48`). It does **not** have `.II`, `.POM`, `.MOP`, `.NoBind` — those only make sense for Pipelined schedules. `Sequential` similarly lacks them (`Control.scala:49-57`).

The singleton objects provide the default-configured instance:

```scala
object Pipe extends Pipe(ii = None, name = None, directive = None, nobind = false, stopWhen = None, haltIfStarved = false)   // Control.scala:63
object Sequential extends Sequential(name = None, stopWhen = None, haltIfStarved = false)                                   // Control.scala:64
object Stream extends Stream(name = None, stopWhen = None, haltIfStarved = false)                                           // Control.scala:65
```

So when a user types `Pipe { ... }` (no modifiers), they hit the `Pipe` singleton's `apply(func)` which is inherited from the `Pipe` class: `Control.scala:25` → `unit_pipe(func, stopWhen = stopWhen)`.

### `CtrlOpt.set`: the metadata propagation point

```scala
case class CtrlOpt(name, sched, ii, stopWhen, mop, pom, nobind, haltIfStarved) {
  def set[A](x: Sym[A]): Unit = {
    name.foreach{n => x.name = Some(n) }
    sched.foreach{s => x.userSchedule = s }
    x.userII = ii.map(_.toDouble)
    if (mop) x.unrollAsMOP
    if (pom) x.unrollAsPOM
    if (nobind) x.shouldNotBind = true
    if (haltIfStarved) x.haltIfStarved = true
  }
}
```

Source: `CtrlOpt.scala:8-27`. Every controller that uses `stageWithFlow(...)` passes a closure that calls `options.set(pipe)`, which is what actually writes metadata onto the freshly-staged control symbol. This is the canonical DSL-layer-to-metadata channel; there is no other path from `Pipe.II(n)` to the symbol's `userII` field.

### `Foreach` iter-counter binding

`ForeachClass.apply(ctrs)(func)` stages `OpForeach`. Each iter is tagged with its counter via `i.counter = IndexCounterInfo(ctr, Seq.tabulate(ctr.ctrParOr1){i => i})` (`ForeachClass.scala:29`). The unroller reads this metadata to know how many lanes each iter produces. Same binding in `ReduceClass.apply` (`ReduceClass.scala:44`) and `MemReduceClass.apply` (`MemReduceClass.scala:61-62`).

### `Reduce` explicit accumulator: the "hack"

`ReduceClass.apply[A](zero: Sym[A])` (`ReduceClass.scala:81-84`) pattern-matches on `Op(RegRead(reg))`. If the zero is `reg.value`, `reg` is treated as the accumulator; otherwise it falls back to `ReduceConstant`. Commented in-source as `TODO[4]: Hack to get explicit accum`.

### `MemReduce` builds a second counter chain from the accumulator

`MemReduceAccum.apply` (`MemReduceClass.scala:33-93`) queries the accumulator's `sparseRank`, `sparseStarts()`, `sparseSteps()`, `sparseEnds()`, `sparsePars()` metadata (`MemReduceClass.scala:38-42`) to build a reduction counter chain:

```scala
val ctrsRed = (0 to acc.sparseRank.length-1).map{ i =>
    Counter[I32](start = 0, step = strides(rankSeq(i)),
                 end = ends(rankSeq(i)) - starts(rankSeq(i)), par = pars(rankSeq(i)))
}
```

Source: `MemReduceClass.scala:52-54`. Then stages five blocks (`mapBlk`, `redBlk`, `resLd`, `accLd`, `accSt`) into `OpMemReduce`. Note: the DSL layer inspects banking metadata at stage-time — a layering violation.

### `Named`, `FSM`, `Parallel`, `ForcedLatency`

`NamedClass(name)` (`NamedClass.scala:4-9`) extends `Directives(CtrlOpt(Some(name),None,None,None))` and re-exposes `.Accel`/`.Pipe`/`.Stream`/`.Sequential` as lazy vals with the name preset. `.Foreach`/`.Reduce` inherit from `Directives`.

`FSM.apply` (`FSM.scala:9-16`) has two overloads (lifted vs raw state type); both call `fsm(...)` at `FSM.scala:18-23`, staging a `StateMachine`. No builder chain — FSM is standalone.

`Parallel.apply(scope)` (`Parallel.scala:10-13`) stages `ParallelPipe` directly with no metadata, no `stageWithFlow`.

`ForcedLatency(latency)(block)` (`Latency.scala:7-11`) wraps a block with `argon.withFlow("ForcedLatency", x => x.forcedLatency = latency)` so every symbol staged inside gets the metadata. Used by `priorityDeq` and `roundRobinDeq` (`api/PriorityDeqAPI.scala:12,28,56`).

## Interactions

- **`spatial.node.*`**: each controller `stage(...)` call names a node defined there (`AccelScope`, `OpForeach`, `OpReduce`, `OpMemReduce`, `UnitPipe`, `ParallelPipe`, `StateMachine`).
- **`spatial.metadata.control.*`**: every metadata field written by `CtrlOpt.set` is defined in `spatial.metadata.control._` (imported at `Control.scala:6`). The `IndexCounterInfo` metadata assigned in `ForeachClass`/`ReduceClass`/`MemReduceClass` is also defined there.
- **Pass pipeline**: the `unrollTransformer` reads `userSchedule`, `userII`, `unrollAsMOP`/`unrollAsPOM`, `IndexCounterInfo`, and `shouldNotBind` to drive its decisions. The `bindingTransformer` reads `shouldNotBind`. The `retiming` passes read `forcedLatency`.
- **Codegens**: all backends pattern-match on the control node types. `chiselgen`, `scalagen`, and `pirgen` each emit differently for `Pipelined`/`Streaming`/`Sequenced` schedules.

## HLS notes

`hls_status: clean`. Controllers map cleanly to HLS pragmas: `Pipe.II(n).Foreach` → `#pragma HLS PIPELINE II=n`; `Sequential.Foreach` → unpipelined for-loop; `Stream`/`Parallel` → `#pragma HLS DATAFLOW`; `Reduce`/`MemReduce` → reduction via loop-carried register; `FSM` → HLS state machine. The main translation challenge is that `IndexCounterInfo` metadata has no direct HLS analogue — the Rust rewrite should flatten iter/lane pairs into a rank-2 loop nest at IR level.

## Open questions

- See `[[20 - Open Questions]]` Q-007 (dsl vs libdsl runtime differences) and Q-009 (Named directive builder composition).
