# ScalaGen current `breakWhen` semantics

## 1. The lowering site

Current ScalaGen handles `breakWhen` only when emitting unrolled foreach/reduce loops. In `emitUnrolledLoop`, the controller first walks each counter in the chain and branches on `ctrs(i).isForever` (src/spatial/codegen/scalagen/ScalaGenController.scala:58-62). For both `UnrolledForeach` and `UnrolledReduce`, a defined `stopWhen` triggers the same warning: `breakWhen detected!  Note scala break occurs at the end of the loop, while --synth break occurs immediately` (ScalaGenController.scala:75-80, 88-93). That warning is the strongest in-tree statement of the intended mismatch: Scala simulation is acknowledged as end-of-iteration, while synthesized hardware is intended to break immediately. The public API docs also describe `Stream(breakWhen=...)` and `Sequential(breakWhen=...)` as immediate-break controllers (src/spatial/lang/control/Control.scala:41-46, 53-56), and ChiselGen wires `stopWhen` into the controller state machine's break input (src/spatial/codegen/chiselgen/ChiselGenController.scala:312-315). ScalaGen's implementation, however, is top-tested.

## 2. Forever-counter shape

For forever counters, ScalaGen does not emit `Forever().takeWhile`. It synthesizes a Scala `while` loop directly. First it builds `hasItems_$lhs`: if the loop reads streams/FIFOs/merge buffers, `hasItems` is the disjunction of their `.nonEmpty`; if not, it emits `def hasItems_$lhs: Boolean = true` (ScalaGenController.scala:61-72). With `stopWhen`, the generated loop is `while(hasItems_$lhs && !stopWhen.value) { ... }` (ScalaGenController.scala:74-80). Without `stopWhen`, it is only `while(hasItems_$lhs) {` (ScalaGenController.scala:81).

Inside that forever loop, ScalaGen emits constant loop metadata: every iter symbol becomes `FixedPoint.fromInt(1)`, and every valid symbol becomes `Bool(true,true)` (ScalaGenController.scala:83-84). The body is emitted only after all loop headers have been opened, via `func`, and each loop is closed after `emitControlIncrement` (ScalaGenController.scala:101-104). There is no generated intra-body test of `stopWhen`.

## 3. Standard-counter shape

For non-forever counters, ScalaGen delegates to the emulation counter. With `stopWhen`, it emits `$cchain($i).takeWhile(!stopWhen.value){case (is,vs) => ... }`; otherwise it emits `$cchain($i).foreach{case (is,vs) => ... }` (ScalaGenController.scala:87-95). The generated iter and valid symbols then come from the arrays passed by the counter: `val iter = is(j)` and `val valid = vs(j)` (ScalaGenController.scala:96-97).

`ScalaGenCounter` maps Spatial counters and counter chains to the emulation `Counterlike` API: `CounterNew` becomes `Counter(...)`, `CounterChainNew` becomes `Array[Counterlike](...)`, and `ForeverNew` becomes `Forever()` (src/spatial/codegen/scalagen/ScalaGenCounter.scala:9-18). The standard emulation `Counter.takeWhile` is also top-tested: `while (range-test && continue) { ... func(vec, valids); i += fullStep }` (emul/src/emul/Counter.scala:24-32). Since `continue` is by-name, `!stopWhen.value` is re-read for each loop test, but only before entering the next body. `Forever.takeWhile` has the same shape, `while (true & continue) { func(vec, valids) }`, even though ScalaGen's forever branch currently bypasses it (emul/src/emul/Counter.scala:45-51).

## 4. `hasItems` and stop timing

`hasItems` is a loop-entry condition, not an immediate kill signal. `getReadStreamsAndFIFOs` collects stream inputs, FIFOs, and merge buffers read by a controller, excluding DRAM-backed stream inputs (ScalaGenController.scala:14-18). Outer stream controls also wrap child controls in `while (hasItems_child)` to exhaust readable inputs before moving on (ScalaGenController.scala:22-35). For forever loops, the same idea becomes `hasItems_$lhs && !stopWhen.value` at the top of the generated `while` (ScalaGenController.scala:63-80). If loop body code writes the break register, ScalaGen's `RegWrite` becomes an immediate `reg.set(v)` on an emulation pointer, and `RegRead`/`.value` reads that pointer (src/spatial/codegen/scalagen/ScalaGenReg.scala:31-39; emul/src/emul/Ptr.scala:5-15). But because the only `stopWhen` read is in the next loop guard or `takeWhile` guard, that new value affects only the next attempted iteration.

## 5. D-11 implications

For Q-132, the current ScalaGen oracle is end-of-iteration semantics. Rust simulation should match that behavior if D-11 prioritizes compatibility with existing Scala simulation output: when the body sets `breakWhen`, the current iteration completes, including body side effects and counter increment/close behavior, and the break is observed at the next loop test. This applies to forever loops through the generated `while`, and to standard counters through `Counter.takeWhile`.

If D-11 instead chooses synthesized immediate-break semantics, that is an intentional divergence from current ScalaGen. The warning text already admits this split, so ScalaGen should not be treated as a hardware-faithful oracle for these tests. A low-risk decision is to make Rust default to current ScalaGen semantics for differential testing, while naming any immediate-break mode as hardware-oriented and separately tested.
