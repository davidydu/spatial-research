---
type: spec
concept: scalagen-controller-emission
source_files:
  - "spatial/src/spatial/codegen/scalagen/ScalaGenController.scala:1-251"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenControl.scala:1-12"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenStream.scala:18-20"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenMemories.scala:61-67"
  - "spatial/src/spatial/codegen/scalagen/ScalaCodegen.scala:64-86"
  - "spatial/argon/src/argon/codegen/Codegen.scala:201-202"
source_notes:
  - "[[scalagen-reference-semantics]]"
hls_status: rework
depends_on:
  - "[[10 - Overview]]"
  - "[[30 - Memory Simulator]]"
  - "[[40 - FIFO LIFO Stream Simulation]]"
  - "[[60 - Counters and Primitives]]"
status: draft
---

# Controller Emission

## Summary

Every Spatial controller (AccelScope, UnitPipe, ParallelPipe, UnrolledForeach, UnrolledReduce, Switch, SwitchCase, StateMachine, IfThenElse) is emitted as a separate `object X_kernel { def run(captured): T = if (en) { body } else null.asInstanceOf[T] }`, with the enclosing scope emitting `val $lhs = X_kernel.run($inputs)`. **This is the kernelization layer that makes scalagen scalable** — each controller becomes its own compilation unit, sidestepping JVM method-size limits.

This entry defines per-controller emission, captured-input computation, the outer-stream HACK, unrolled-loop and break-when handling, and the `emitControlDone`/`emitControlIncrement` hooks. **For the Rust+HLS reimplementation, the file-per-controller layout is scalagen-specific (a JVM workaround); the body semantics are reference behavior that must be preserved.**

## `emitControlObject` shape

`spatial/src/spatial/codegen/scalagen/ScalaGenController.scala:108-139` is the core kernelization helper. Steps:

1. **Compute captured inputs** (`:111-113`): `inputs = (lhs.nonBlockInputs ++ block.nestedInputs).diff(op.binds).filterNot(_.isMem || _.isValue)`. Memories are referenced by file-scope name; iterators are produced inside the kernel's own loop emission; constants are inlined.
2. **Compute enable gate** (`:117-118`): when `ens` is non-empty, body becomes `if (${and(ens)}) { body } else null.asInstanceOf[T]`. Works because the kernel return value is consumed only when `ens` is true.
3. **Emit kernel file** (`:123-136`) via `inGen(kernel(lhs))`, where `kernel(sym) = sym.toString + "_kernel.scala"` (`spatial/argon/src/argon/codegen/Codegen.scala:201`). Each kernel file has its own `import emul._; import emul.implicits._` header. The shape is `object ${lhs}_kernel { def run(captured): T = if (ens) { body } else null.asInstanceOf[T] }`, with BEGIN/END comment markers.
4. **Append line-buffer swap** (`:131`): line buffers registered as "swappers" of this controller (via `mem.swappers` metadata; see `ScalaGenLineBuffer.scala:77-81`) get a `$lhs.swap()` after the body. See [[30 - Memory Simulator|line buffer]].
5. **Emit caller-side dispatch** (`:138`): the enclosing scope emits `val $lhs = ${lhs}_kernel.run($inputs)`.

The `inGen(kernel(lhs))` routes the emission stream to a separate file, so `Main.scala` only contains the dispatch line, not the kernel body.

## Per-controller emission

`ScalaGenController.gen` (`spatial/src/spatial/codegen/scalagen/ScalaGenController.scala:141-250`) dispatches by IR node:

### `AccelScope`

`ScalaGenController.scala:142-178`. The top-level Accel block. Wrapped in `try { ... } catch { case x: Exception if x.getMessage == "exit" => ... }` for graceful shutdown via "exit"-tagged exception. Inside the kernel body (`:144-177`): `StatTracker.pushState(true)` / `popState()` bracket gated on `--resource-reporter`; `globalMems = true` flips memory-emission to `if ($lhs == null) x` form for lazy init (`ScalaGenMemories.scala:24`); `gen(func)` emits the body (the commented-out `lhs.willRunForever` path at `:147-164` is currently disabled with `if (true)`). After body: `streamOuts.foreach{x => emit(src"$x.dump()")}` for non-DRAMBus streams (`:166-168`); `bufferedOuts.foreach{buff => emit(src"$buff.close()")}` (`:170`); `globalMems = false`. `AccelScope` always has `ens = Set.empty`, so no gate.

### `UnitPipe` and `ParallelPipe`

**UnitPipe** (`ScalaGenController.scala:180-184`): emits `emitControlBlock(lhs, func); emitControlDone(lhs)`. **ParallelPipe** (`:187-191`): emits `gen(func); emitControlDone(lhs)` — uses `gen(func)` directly (no outer-stream pumping). **The simulator runs parallel children sequentially**; parallelism is hardware-only.

### `UnrolledForeach` and `UnrolledReduce`

`ScalaGenController.scala:193-207`. Both delegate to `emitUnrolledLoop(lhs, cchain, iters, valids){ emitControlBlock(lhs, func) }` followed by `emitControlDone(lhs)`. `emitUnrolledLoop` (`:51-106`) handles counter chain emission per counter (`:60-99`):

- **Forever counter** (`:61-85`): if the controller has stream/FIFO inputs, emit `def hasItems_$lhs: Boolean = stream.nonEmpty || ...` and loop `while (hasItems_$lhs) { ... }`; otherwise `def hasItems_$lhs = true` (`:71`). Break-when handling (`:74-82`): with a `stopWhen` Bit, emit a warning `"breakWhen detected! Note scala break occurs at the end of the loop, while --synth break occurs immediately"` and use `while(hasItems_$lhs && !${stopWhen.get}.value)`. The forever-counter body emits dummy `val $iter = FixedPoint.fromInt(1)` / `val $valid = Bool(true,true)` (`:83-84`).
- **Standard counter** (`:86-98`): with `stopWhen`, `$cchain($i).takeWhile(!${stopWhen.get}.value){case (is,vs) => ...}`; without, `$cchain($i).foreach{case (is,vs) => ...}`. The `(is, vs)` destructuring exposes the per-lane vectors of `Counter` (see [[60 - Counters and Primitives]]). Iters: `val $iter = is($j)`; valids: `val $valid = vs($j)`.

After the body, `emitControlIncrement(lhs, is); close("}")` per level (`:102-105`). `emitControlIncrement` is a no-op hook (`ScalaGenControl.scala:10`) that downstream traits can override.

### `Switch`, `SwitchCase`, `StateMachine`, `IfThenElse`

**Switch** (`ScalaGenController.scala:209-222`): if-else cascade over `selects(i)` with each case body's return value. Else branch: `invalid(R)` for Bits, `()` for Void, `null.asInstanceOf[R]` otherwise (`:216-218`). The `SwitchCase` IR node itself is a no-op (`:222`); its body is consumed by parent `Switch.cases(i).body`.

**StateMachine** (`ScalaGenController.scala:224-237`): emits `var $state: T = $start`, `def notDone() = { ret(notDone) }`, then `while(notDone()) { gen(action); gen(nextState); $state = ${nextState.result} }`. Inner blocks emit inline.

**IfThenElse** (`ScalaGenController.scala:239-247`): plain `if (cond) { thenp } else { elsep }` with each branch returning its block result.

## `emitControlBlock` and the outer-stream HACK

`emitControlBlock(lhs, block)` (`spatial/src/spatial/codegen/scalagen/ScalaGenController.scala:22-49`) decides between sequential and outer-stream emission. The outer-stream branch (`:23-45`) is the explicit HACK. For `lhs.isOuterStreamControl`:

1. Iterate over the block's statements, finding children of `lhs`.
2. For each child, compute `inputs = getReadStreamsAndFIFOs(stm.toCtrl) diff block.nestedStms.toSet` — external read-stream/FIFO inputs (`:30`).
3. If `inputs.nonEmpty`: pump via `while (hasItems_${lhs}_$stm) { visit(stm) }` where `hasItems_X_Y = stream.nonEmpty || ...` (`:34-37`).
4. Otherwise: `visit(stm)` once (`:40`).

This drain-each-child-then-advance order **does not match the hardware semantics** of concurrent stream-coupled execution with back-pressure. The comment at `:33` is explicit: *"Note that this won't work for cases with feedback, but this is disallowed for now anyway"*. See Q-scal-05.

For non-outer-stream controllers, `gen(block)` visits statements in source order without pumping (`:47`).

## Captured-input computation

The `inputs: Seq[Sym[_]]` at `ScalaGenController.scala:111-113` deserves attention. `nonBlockInputs` are the op's non-block inputs (e.g., for `UnrolledForeach`, that's `ens ++ cchain ++ ... iters ++ valids ++ stopWhen`); `block.nestedInputs` is every symbol used inside but defined outside; `op.binds` are op-introduced symbols (loop iterators, switch binds, state-machine variables); the `isMem || isValue` filter excludes memories (file-scope) and compile-time constants (inlined). The remaining inputs are the closure for `_kernel.run(...)`.

The `useMap` mechanism at `:120-122`, `:137` handles symbols that are themselves chunked: a captured input with a `scoped` map entry (from `javaStyleChunk`, see [[10 - Overview]]) has its mapping temporarily removed during kernel emission so the input is referenced by its original name, then restored after.

## `emitControlDone` and `emitControlIncrement` hooks

`ScalaGenControl` (`spatial/src/spatial/codegen/scalagen/ScalaGenControl.scala:6-12`) declares two no-op hooks: `emitControlDone(ctrl)` and `emitControlIncrement(ctrl, iter)`. `emitControlDone` is called at end-of-kernel for `UnitPipe`/`ParallelPipe`/`UnrolledForeach`/`UnrolledReduce`/`Switch`/`StateMachine` (`ScalaGenController.scala:184`, `:191`, `:198`, `:206`, `:219`, `:236`). `emitControlIncrement` is called per iteration (`:103`). Standard scalagen does not override them; they exist as extension points (e.g., for cycle-tracking variants). `ScalaGenStream.emitControlDone` (`ScalaGenStream.scala:18-20`) calls `super` — currently a no-op chain.

## Kernel emission interaction with `globalMems` and breakWhen divergence

`emitMemObject` (`ScalaGenMemories.scala:61-67`) emits each memory in its own `_kernel.scala` file. When `globalMems` is true (set during `AccelScope` body, `ScalaGenController.scala:146`), `emitMem` uses `if ($lhs == null) x` for lazy initialization (`ScalaGenMemories.scala:24`); when false, memory ops are inlined as `val x = ...`. This split lets the Accel block reference memories that are top-level Scala objects without re-creating them per controller invocation.

The `breakWhen` warning at `ScalaGenController.scala:76`, `:79`, `:89`, `:92` flags a real semantic divergence: **scalagen** evaluates `while(hasItems_$lhs && !${stopWhen.get}.value)` at the *start* of each iteration, so once `stopWhen` becomes true mid-iteration, the current iteration completes and one more outer check runs; **chiselgen/RTL** asserts the break combinationally and transitions to done in the same cycle. Tests using `breakWhen` produce different outputs across backends. See Q-scal-15.

## Ground-truth status

Reference semantics: per-controller closure is `object X_kernel { def run(captured): T }` with captured set `(nonBlockInputs ++ nestedInputs) diff binds`, minus memories/constants; enable gate is `if (and(ens)) { body } else null.asInstanceOf[T]`; outer-stream pump drains each child to exhaustion (semantically incorrect for feedback); forever loop is `while (hasItems)` driven by stream nonemptiness; Switch is if-else cascade with type-appropriate else; StateMachine is `var state; while(notDone()) { ... }`; break-when has one-extra-iteration divergence from RTL.

The Rust port should preserve these semantics; kernelization-into-files is JVM-specific and not required.

## HLS notes

`rework`. The file-per-controller layout is a JVM method-size workaround; in Rust, controllers can be functions. The HLS target generates RTL state machines where Switch becomes a multiplexer and StateMachine an FSM; emit-as-Scala-control-flow does not map. The outer-stream HACK is a known-limited simulation; the HLS target must implement concurrent-with-back-pressure coupling. The break-when end-of-iteration divergence requires the Rust simulator to choose match-scalagen or match-RTL based on test policy.

## Interactions

- **Upstream**: control metadata (`isOuterStreamControl`, `children`, `op.binds`, `nonBlockInputs`, `nestedInputs`); `mem.swappers` for line-buffer swap; `enableResourceReporter`.
- **Downstream**: kernel files compile alongside `Main.scala` via sbt; each calls `emul.Counter`/`emul.BankedMemory`/etc.
- **Sibling**: [[60 - Counters and Primitives]] for `Counter.foreach`/`takeWhile`; [[40 - FIFO LIFO Stream Simulation]] for `getReadStreamsAndFIFOs`.

## Open questions

- Q-scal-05 — Outer-stream HACK and feedback loops.
- Q-scal-08 — `RegAccumOp` throws on `AccumFMA` (upstream invariant).
- Q-scal-15 — `breakWhen` end-of-iteration vs immediate-break.

See `open-questions-scalagen.md`.
