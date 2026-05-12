---
type: spec
concept: retiming
source_files:
  - "src/spatial/traversal/RetimingAnalyzer.scala:1-121"
  - "src/spatial/transform/RetimingTransformer.scala:1-271"
  - "src/spatial/transform/DuplicateRetimeStripper.scala:1-36"
  - "src/spatial/traversal/IterationDiffAnalyzer.scala:1-217"
  - "src/spatial/traversal/InitiationAnalyzer.scala:1-101"
  - "src/spatial/traversal/BroadcastCleanup.scala:1-132"
  - "src/spatial/traversal/BufferRecompute.scala:1-54"
  - "src/spatial/util/modeling.scala:560-650"
  - "src/spatial/Spatial.scala:140"
  - "src/spatial/Spatial.scala:213"
  - "src/spatial/Spatial.scala:227-228"
  - "src/spatial/Spatial.scala:231-233"
source_notes:
  - "[[pass-pipeline]]"
hls_status: chisel-specific
depends_on:
  - "[[Controllers]]"
  - "[[70 - Banking]]"
status: draft
---

# Retiming

## Summary

Retiming is the trio of analysis + transform + stripper that makes Spatial inner-pipelined controllers timing-correct: every consumer of a bit-valued input must observe its data at the same global cycle, even when the producer's latency varies. The pass family computes per-symbol delay metadata (`fullDelay`, `inCycle`, `bodyLatency`), uses it to insert `DelayLine(size, data)` nodes that buffer producers to align with their consumers, and then collapses redundant `RetimeGate()` markers. The trio runs **three times** as `RetimingAnalyzer` invocations: first inside `retimeAnalysisPasses` for banking's concurrency rule, second post-DCE/post-unroll, third just before `RetimingTransformer` (`Spatial.scala:140, 213, 227`). Surrounding it: `IterationDiffAnalyzer` derives `iterDiff` for reduce cycles; `InitiationAnalyzer` computes `compilerII`; `BroadcastCleanupAnalyzer` propagates `isBroadcastAddr=false` reverse-stmt-order; `BufferRecompute` rebuilds `depth = max(bufPort)+1` after unrolling.

## `retimeAnalysisPasses` sub-sequence

`lazy val retimeAnalysisPasses = Seq(printer, duplicateRetimeStripper, printer, retimingAnalyzer)` (`Spatial.scala:140`). Every retime-analysis run is preceded by collapsing back-to-back `RetimeGate()` nodes via `DuplicateRetimeStripper`, ensuring the analyzer sees a canonical form. The 4-element seq is consumed at three pipeline points:

1. As a DSE prelude under `enableRuntimeModel` (`Spatial.scala:180`).
2. As the first phase of `bankingAnalysis` (`Spatial.scala:142, 203`) — banking needs provisional `fullDelay`/`inCycle`/`bodyLatency` to evaluate `requireConcurrentPortAccess` cases involving `delayDefined`.
3. As the third invocation, immediately before `RetimingTransformer` (`Spatial.scala:227`).

Plus a fourth, plain-non-seq `retimingAnalyzer` invocation post-DCE/post-unroll (`Spatial.scala:213`).

## `RetimingAnalyzer`

`case class RetimingAnalyzer(IR: State) extends AccelTraversal` (`traversal/RetimingAnalyzer.scala:13`). Gated by `override def shouldRun: Boolean = spatialConfig.enableRetiming` (`:14`); when retiming is disabled (e.g. `--noretime`, `--sim` without `--retime`) the analyzer no-ops.

`preprocess` clears `fullDelay = 0.0` on every stmt with `delayDefined` (`:21-24`):

```scala
override protected def preprocess[R](block: Block[R]): Block[R] = {
  block.nestedStms.collect{case x if (x.delayDefined) => x.fullDelay = 0.0}
  super.preprocess(block)
}
```

This means each of the 3 invocations starts from zero — later invocations don't accumulate bias from earlier ones.

The visitor (`:112-118`) dispatches on control-kind:
- `AccelScope` → `inAccel { analyzeCtrl(lhs,rhs) }`
- `SpatialBlackboxImpl(func)` → `inAccel { analyzeCtrl; lhs.bodyLatency = func.result.fullDelay }`
- `BlackboxImpl[_,_,_]` → `inAccel { analyzeCtrl }`
- Inner control → `analyzeCtrl(lhs, rhs)`
- Anything else → `super.visit(lhs,rhs)`.

`analyzeCtrl` (`:84-109`) sets per-block "wrap" and "push" lists controlling whether each child block is subjected to retiming:

```scala
if ((lhs.isInnerControl || lhs.isBlackboxImpl) && !rhs.isSwitch && inHw) {
  val retimeEnables = rhs.blocks.map{_ => true }.toList
  val retimePushLaterBlock = rhs.blocks.map{_ => false }.toList
  rhs match {
    case _:StateMachine[_] => withRetime(retimeEnables, List(false,true,false)) { super.visit(lhs, rhs) }
    case _ => withRetime(retimeEnables, retimePushLaterBlock) { super.visit(lhs, rhs) }
  }
}
```

Switches are excluded from retiming because they are not "inner controllers from PipeRetimer's point of view" (comment, `:94`).

The retime computation lives in `retimeBlock` (`:26-55`):

1. Collect `scope = block.nestedStms.toSortedSeq` (`:27`).
2. Collect `result` over all nested op-blocks plus the current block (`:28`).
3. Call `pipeLatencies(result, scope, verbose=state.config.enDbg)` to get `(newLatencies, newCycles)` (`:35`).
4. `adjustedLatencies` is `newLatencies` shifted by `lastLatency` (the running cumulative latency of preceding blocks) (`:36`).
5. Update `cycles ++= newCycles.flatMap(_.symbols)` (`:39`).
6. For each symbol, compute `fullDelay = scrubNoise(l - latencyOf(s, inReduce=cycles.contains(s)))` (`:44`):

   ```scala
   adjustedLatencies.toList.map{case (s,l) => s -> scrubNoise(l - latencyOf(s, inReduce = s.inCycle)) }
     .foreach{case (s,l) =>
       s.fullDelay = l
       if (cycles.contains(s)) s.inCycle = true
       …
     }
   ```

7. Store latency for the next block: `lastLatency = adjustedLatencies.toList.map(_._2).sorted.reverse.headOption.getOrElse(0.0)` (`:52`).

`scrubNoise` (`util/modeling.scala:563-567`) rounds `x` to the nearest 1/1000 to avoid floating-point drift (e.g. `1.1999999997 - 0.2 < 1.0`).

## `RetimingTransformer`

`case class RetimingTransformer(IR: State) extends MutateTransformer with AccelTraversal` (`transform/RetimingTransformer.scala:17`). Same `shouldRun = enableRetiming` gate (`:18`).

Per-transformer state (`:25-30`):

- `delayLines: Map[Sym[_], SortedSet[ValueDelay]]` — for each producer, the materialised delay lines indexed by delay amount.
- `delayConsumers: Map[Sym[_], List[ValueDelay]]` — per-reader, the lines this reader consumes.
- `latencies: Map[Sym[_], Double]` — adjusted latency per stmt.
- `cycles: Seq[Sym[_]]` — stmts in retiming cycles.
- `hierarchy: Int` — nesting depth (used to share lines across nested blocks).
- `inInnerScope: Boolean` — true while inside an inner-control block.

### `retimeBlock` and `retimeStms`

`retimeBlock` (`:205-220`) is the entry point invoked when a block has `doWrap = true`:

1. `scope = block.nestedStms`.
2. `result = (scope.flatMap{case Op(d) => d.blocks; case _ => Nil} :+ block).flatMap(exps(_))`.
3. `(_, newCycles) = pipeLatencies(result, scope)` — same routine as the analyzer.
4. `adjustedLatencies` rebuilds latencies from `s.fullDelay + latencyOf(s, inReduce=cycles.contains(s))`.
5. `latencies ++= adjustedLatencies; cycles ++= newCycles.flatMap(_.symbols)`.
6. `isolateSubst() { retimeStms(block) }` (`:219`) — actually rewrite each stmt.

`retimeStms` (`:132-140`) is the inner driver:

```scala
private def retimeStms[A](block: Block[A]): Sym[A] = inBlock(block) {
  inlineWith(block){stms =>
    stms.foreach{
      case Stm(switch, op: Switch[_]) => retimeSwitch(switch, op.asInstanceOf[Switch[Any]])
      case stm => retimeStm(stm)
    }
    f(block.result)
  }
}
```

`inBlock` (`:41-66`) increments `hierarchy`, sets `inInnerScope = true`, calls `findDelayLines(scope)` to compute the lines that need to exist at this hierarchy level, materialises them via `addDelayLine`, executes the inner function, then restores all state on exit.

`retimeStm` (`:142-154`) per-stmt:

1. Compute `inputs = d.bitInputs`.
2. `isolateSubst()` — push a new substitution scope.
3. `registerDelays(reader, inputs)` (`:78-88`) — for each `delayConsumers[reader]` line whose `line.input` is in `inputs`, register `(in -> line.value())`. This is the substitution that re-routes consumers through delay lines.
4. `visit(sym)` — mirror the stmt with substitutions applied.
5. `register(reader -> reader2)` — record the rewrite.

### Switch handling

`retimeSwitch` (`:180-203`) and `retimeSwitchCase` (`:156-178`) handle switches specially. The case body adds a trailing delay line if its result needs to align with sibling cases:

```scala
val size = delayConsumers.getOrElse(switch, Nil).find(_.input == cas).map(_.size).getOrElse(0) +
           delayConsumers.getOrElse(cas, Nil).find(_.input == body.result).map(_.size).getOrElse(0)
if (size > 0) delayLine(size, f(body.result))
else f(body.result)
```

This is the only place where retiming materialises a `DelayLine` directly (rather than going through `findDelayLines`). The rationale: each `SwitchCase` body produces a value; its delay must match the `Switch`'s expected output delay so all cases arrive at the consumer in sync.

### `precomputeDelayLines`

`precomputeDelayLines(op: Op[_])` (`:111-126`) is the cross-block-sharing mechanism:

```scala
private def precomputeDelayLines(op: Op[_]): Unit = {
  hierarchy += 1
  op.blocks.foreach{block =>
    val innerScope = block.nestedStms
    val lines = findDelayLines(innerScope).map(_._2)
    (lines ++ lines.flatMap(_.prev)).filter(_.hierarchy < hierarchy).foreach{line =>
      if (!line.alreadyExists) {
        val dly = line.value()
        …
      }
    }
  }
  hierarchy -= 1
}
```

For each block in `op.blocks`, it finds all delay lines that need to exist *above* the current hierarchy level (i.e. shared across multiple sibling blocks) and materialises them eagerly. This prevents two sibling blocks from each constructing their own copy of the same delay line. `updateNode` (`:127-130`) calls `precomputeDelayLines` whenever `inInnerScope` is true, which means it fires for every Op transformation inside an inner controller.

### `findDelayLines` and `computeDelayLines`

`findDelayLines` (`:32-39`) is a thin wrapper that delegates to `computeDelayLines` (`util/modeling.scala:570-649`). The body of `computeDelayLines`:

1. For each `(reader, d)` in scope, compute `criticalPath = scrubNoise(delayOf(reader) - latencyOf(reader, inReduce))` — when all inputs must arrive (`:618-625`).
2. For each `in` in `d.bitInputs`, compute `latency_required` (`criticalPath`), `latency_achieved` (`delayOf(in)`), `latency_missing` (`retimingDelay(in) - builtInLatencyOf(in)`), `latency_actual = latency_achieved - latency_missing`, and `delay = latency_required.toInt - latency_actual.toInt` (`:628-634`).
3. If `delay != 0`, create a `ValueDelay` via `createValueDelay(input, reader, delay)` (`:589-616`). The function checks `delayLines.getOrElse(input, …)` for an existing line whose `delay <= target`; if found and `size > 0`, returns an "extending" `ValueDelay` chained off the prev. Otherwise creates a fresh delay-line.

The result: each producer-consumer pair with non-zero latency mismatch gets exactly one `ValueDelay`, optionally chained off a shorter pre-existing line. This is what `addDelayLine` (`:90-99`) writes into `delayLines` and `delayConsumers`.

## `DuplicateRetimeStripper`

`case class DuplicateRetimeStripper(IR: State) extends MutateTransformer with AccelTraversal` (`transform/DuplicateRetimeStripper.scala:9`). It only mutates inner-control blocks (`:27-32`):

```scala
case ctrl: Control[_] if lhs.isInnerControl =>
  ctrl.blocks foreach { block => register(block -> stripDuplicateRetimes(block)) }
  super.transform(lhs, rhs)
```

`stripDuplicateRetimes` (`:10-25`) walks the block and emits each `RetimeGate()` only if the previous stmt was not a `RetimeGate()`:

```scala
var previousWasRetime = false
block.stms.foreach {
  case rt@Op(RetimeGate()) =>
    if (!previousWasRetime) super.visit(rt)
    previousWasRetime = true
  case other =>
    super.visit(other)
    previousWasRetime = false
}
```

Back-to-back `RetimeGate() → RetimeGate()` pairs collapse to a single `RetimeGate()`. This matters because each `RetimingAnalyzer` invocation is preceded by a fresh stripping pass (it's at index 1 of `retimeAnalysisPasses`, between two `printer` dumps), ensuring the second and third analyses see a canonical form.

## `IterationDiffAnalyzer`

`case class IterationDiffAnalyzer(IR: State) extends AccelTraversal` (`traversal/IterationDiffAnalyzer.scala:15`). Runs at step 13 inside `bankingAnalysis` (`Spatial.scala:142`).

Per-controller, `findCycles` (`:17-178`) calls `findAccumCycles(stms).accums` and for each `AccumTriple(mem, reader, writer)` computes:

- `selfRelativeData` per iterator: `(personalTicks, stride*par)` (`:34-58`). For static counters, `personalTicks = ceil((end-start)/step) / par`. For dynamic counters there are 4 fallback paths — `enableLooseIterDiffs`, `userII.isDefined`, having a known accum-iter, or generic worst-case — each with a warning.
- `ticks: Map[I32, Int]` — global ticks for an iterator to increment (`:65`).
- `ticksToCoverDist(w, r)` — given write and read access matrices, polyhedral distance between them in tick units (`:76-101`).
- `corners(thisIterWrites, thisIterReads){…}` — compute `ticksToCoverDist` for all 4 corner-pairs (write lane 0/N × read lane 0/N) (`:103-105`).
- `minTicksToOverlap = if all zero, 0; else min of nonzero` (`:111`).

Writes `reader.iterDiff`, `writer.iterDiff`, `mem.iterDiff` (`:115-117`), all updated as `min(current, minTicksToOverlap)` (so the metadata accumulates the tightest iter-diff seen).

For multi-lane reads (`thisIterReads.size > 1`), `findCycles` also computes `segmentMapping` per lane (`:120-167`) — essentially asks "for lane `i+1`, which earlier write lane requires the same address?" and uses `segmentDep = segments(laneDep) + 1` to push lanes forward in pipeline segments. The two example diagrams at `:124-149` document this for `par 2` and `par 3` with a 2-tick offset.

Two special cases for `OpMemReduce` (`iterDiff = 0`, "touch-and-go") and `OpReduce` (`iterDiff = 1`, "always reading and writing to same place") at `:194-205`.

## `InitiationAnalyzer`

`case class InitiationAnalyzer(IR: State) extends AccelTraversal` (`traversal/InitiationAnalyzer.scala:12`). Runs at step 22 (`Spatial.scala:233`) and inside the streamify block (`Spatial.scala:144`).

Outer controllers (`:14-21`):
```scala
val interval = (1.0 +: lhs.children.map{child => child.sym.II }).max
lhs.II = lhs.userII.getOrElse(interval)
lhs.compilerII = interval
```

The `II` of an outer controller is the max of its children's `II`s (clamped to ≥ 1.0).

Inner controllers (`:23-41`) — the core formula:

```scala
val compilerII = if (forceII1) 1.0
                 else if (minIterDiff.isEmpty) interval
                 else if (minIterDiff.get == 1) interval
                 else scala.math.ceil(interval/minIterDiff.get)
lhs.II = if (lhs.getUserSchedule.isDefined && lhs.userSchedule == Sequenced) latency
         else lhs.userII.getOrElse(scala.math.min(compilerII,latency))
lhs.compilerII = compilerII
```

The `compilerII = ceil(interval / iterDiff)` formula: if a reduction has cycle interval `interval` but the iter-diff says writes only need to be visible every `iterDiff` cycles, then the controller can pipeline at `ceil(interval/iterDiff)` instead of `interval`. The `forceII1 = iterdiffs.last <= 0` gate catches `OpMemReduce` (touch-and-go) and forces II=1.

Special case for `StateMachine` (`:52-91`) — separate latency/interval computation accounting for `notDone`/`action`/`nextState` blocks and any read-after-write dependencies between `action` writes and `nextState` reads.

## `BroadcastCleanupAnalyzer`

`case class BroadcastCleanupAnalyzer(IR: State) extends AccelTraversal` (`traversal/BroadcastCleanup.scala:11`). Runs at step 22 (`Spatial.scala:231`) — final pass after retiming.

Per-inner-controller, walks `block.stms.reverse` (reverse stmt order, `:20`) and for each stmt:

- `MemAlloc[_,_]` → `lhs.isBroadcastAddr = false` (`:16`).
- `StatusReader`/`Accumulator`/`BankedEnqueue`/`BankedDequeue` → `sym.isBroadcastAddr = false` and propagate `false` to all `nestedInputs` (`:21-31`).
- `BankedReader` (`:33-67`) — for each lane `i`: if lane is broadcast (`b > 0`), propagate `isBroadcastAddr = true` (with conjunction to existing) to `bank(i).nestedInputs ++ ofs(i).nestedInputs ++ enss(i).nestedInputs`; if not broadcast (`b == 0`), force `isBroadcastAddr = false` to the same set.
- `Writer` / `BankedWriter` analogous (`:68-117`).
- Catch-all (`:118-123`) — if `sym.getBroadcastAddr.isDefined`, propagate `&` (conjunction) of existing and current to inputs.

The reverse-stmt-order walk ensures broadcast-true tags only stick when *every* downstream user is broadcast-compatible; a single broadcast-false consumer eliminates the broadcast on its producer.

## `BufferRecompute`

`case class BufferRecompute(IR: State) extends BlkTraversal` (`traversal/BufferRecompute.scala:13`). Runs at step 19 (`Spatial.scala:222`), between `BindingTransformer` and the optional accumulator specialization.

Per `MemAlloc` (excluding FIFO/NonBuffer/StreamIn/StreamOut/ArgIn/ArgOut/HostIO at `:30`):

1. If `lhs.getDuplicates.isDefined`, call `computeMemoryBufferPorts(lhs, lhs.readers, lhs.writers)` and recompute `depth = bufPorts.maxOrElse(0) + 1` (`:34-35`).
2. If recomputed `depth != lhs.instance.depth`, update each duplicate via `dup.updateDepth(depth)` (`:36-39`).
3. Resolve port conflicts (specifically for MemReduce after unrolling): while `hasPortConflicts(lhs).size > 0`, bump the conflicting reader's `muxPort` to `maxMuxPort + 1` (`:42-47`).

This is needed because post-unroll/post-MemReduce-unrolling can produce different N-buffer depths than what banking computed. Banking ran before unrolling; unrolling created new accesses; the buffer depth must be recomputed from the post-unroll access set.

The port-conflict workaround at `:42-47` is flagged in the source as `Delete once #98 is fixed` — i.e. it's a known kludge.

## Interactions

- **`RetimingAnalyzer` reads**: `pipeLatencies` output (via `util.modeling.pipeLatencies`); `latencyOf(s, inReduce)`; per-stmt `delayDefined`. **Writes**: `fullDelay`, `inCycle`, `bodyLatency`.
- **`RetimingTransformer` reads**: `fullDelay`, `inCycle`, `latencies`, `cycles`. **Writes**: new `DelayLine` nodes; consumer-substitution maps.
- **`DuplicateRetimeStripper` reads**: stmts of inner-control blocks. **Writes**: stripped block (mutates IR shape, no metadata).
- **`IterationDiffAnalyzer` reads**: `affineMatrices` (from banking), `ctrStart`/`ctrEnd`/`ctrStep`, `userII`. **Writes**: `iterDiff` on memory/reader/writer; `segmentMapping` on multi-lane reads.
- **`InitiationAnalyzer` reads**: child `II`, `iterDiff`, `userII`, `userSchedule`, `bboxII`. **Writes**: `II`, `compilerII`, `bodyLatency`.
- **`BroadcastCleanupAnalyzer` reads**: `isBroadcastAddr`, port broadcast info. **Writes**: `isBroadcastAddr` (reverse propagation).
- **`BufferRecompute` reads**: `Duplicates`, `Ports`, reader/writer sets. **Writes**: updated `Duplicates.depth`; possibly bumped `Ports.muxPort`.
- **Order**: `RetimingAnalyzer` runs at steps 13/16/21; `RetimingTransformer` at 21; `BroadcastCleanupAnalyzer` at 22; `BufferRecompute` at 19; `InitiationAnalyzer` at 22 (final) and step 13 (under `enableRuntimeModel`).

## HLS notes

Retiming is **chisel-specific**. The `DelayLine(size, data)` IR node maps directly to a Chisel `ShiftRegister(size, data)` and there is no Vitis HLS analogue — Vitis pipelines via `#pragma HLS pipeline II=N` and lets the scheduler insert registers internally. A Rust+HLS reimplementation would skip the entire retiming trio and rely on HLS's automatic register insertion driven by the `II` annotation from `InitiationAnalyzer`.

`IterationDiffAnalyzer` and `InitiationAnalyzer` (the `compilerII = ceil(interval/iterDiff)` formula) are reusable in HLS — they directly emit `#pragma HLS pipeline II=<N>`. `BroadcastCleanupAnalyzer` is reusable for any banked-memory layout.

`BufferRecompute` is reusable — N-buffer depth is target-agnostic. The port-conflict workaround at `:42-47` should be deleted when issue #98 is fixed.

## Open questions

- `Q-pp-04` — `RetimingAnalyzer.shouldRun = enableRetiming`. When `--noretime` is set (which also disables `enableOptimizedReduce`), do `IterationDiffAnalyzer` and `InitiationAnalyzer` still run? The deep dive doesn't trace this gate.
- `Q-pp-05` — `BufferRecompute` has a `Delete once #98 is fixed` comment for the muxPort-bump workaround. What is issue #98 and what's the proper fix?
- `Q-pp-06` — `RetimingTransformer.precomputeDelayLines` materialises lines for every block in `op.blocks`. For `Switch` ops, `retimeSwitchCase` also adds a trailing `delayLine(size, body.result)`. Are these always disjoint, or can they double-count?
