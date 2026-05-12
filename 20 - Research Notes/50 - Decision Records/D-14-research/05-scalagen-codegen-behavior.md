# ScalaGen/codegen behavior for `Fork`, `ForkJoin`, and `PrimitiveBox`

## Schedule Tags

Spatial's control metadata has six schedule values: `Sequenced`, `Pipelined`, `Streaming`, `ForkJoin`, `Fork`, and `PrimitiveBox` (`src/spatial/metadata/control/ControlData.scala:8-14`). The flow rule assigns the three relevant tags structurally: `ParallelPipe` is always `ForkJoin`, `Switch` and hardware `IfThenElse` are `Fork`, `SpatialBlackboxImpl` is `PrimitiveBox`, `SpatialCtrlBlackboxImpl` is only `Sequenced`, and `SwitchCase` is `Sequenced` (`src/spatial/flows/SpatialFlowRules.scala:317-339`). The effective schedule getter preserves `ForkJoin`, `Fork`, and `PrimitiveBox` even for single-iteration controls, while converting only single `Pipelined` controls back to `Sequenced` (`src/spatial/metadata/control/package.scala:193-217`).

## ScalaGen Semantics

ScalaGen does not consume `rawSchedule` when emitting controller code. Its block generator takes block statements in order and passes them to `visit` through `javaStyleChunk` (`src/spatial/codegen/scalagen/ScalaCodegen.scala:37-53`). `ParallelPipe` simply emits a kernel wrapper, calls `gen(func)`, then marks the control done (`src/spatial/codegen/scalagen/ScalaGenController.scala:187-191`). That is deterministic serialization of the IR block, not a fork/join execution model with concurrent children, arbitrary interleavings, or join-time race semantics.

The only ScalaGen concession to stream-like behavior is separate from `ForkJoin`: for an outer `Streaming` control, `emitControlBlock` detects child controls and, if they read FIFO/stream inputs declared outside the block, wraps each child in a `while (hasItems_child)` loop before moving to the next child (`src/spatial/codegen/scalagen/ScalaGenController.scala:22-49`). This drains one streaming child to completion before the next. It is explicitly a simulation hack, not a parallel schedule.

## `Fork` As Conditional Branch

`Switch` emission is also ordinary Scala control flow. ScalaGen writes an ordered `if` / `else if` chain over the select signals, returns the selected case body, and emits an invalid/null/no-op fallback depending on result type (`src/spatial/codegen/scalagen/ScalaGenController.scala:209-220`). Raw `IfThenElse` emits direct Scala `if (cond) ... else ...` (`src/spatial/codegen/scalagen/ScalaGenController.scala:239-247`). The switch scheduler motions non-`SwitchCase` work out of the switch body, leaving only cases in the switch block (`src/spatial/node/Switch.scala:8-29`). The hardware transformer normally creates mutually exclusive case predicates from nested if/else structure (`src/spatial/transform/SwitchTransformer.scala:77-85`), and the optimizer warns when constant-folding reveals no enabled cases or multiple enabled cases (`src/spatial/transform/SwitchOptimizer.scala:65-68`).

Operationally, Rust should treat `Fork` as conditional choice, not as parallel fork: evaluate selects in source order, execute the first enabled case, and make multiple dynamic selects either a diagnostic or a first-match compatibility mode. HLS should preserve the same one-hot/priority contract, even though Chisel's `Fork` controller can enable selected case slots and declares done when any child finishes (`fringe/src/fringe/templates/Controllers.scala:173-187`).

## `PrimitiveBox`

`PrimitiveBox` is a metadata tag for `SpatialBlackboxImpl`, not a ScalaGen schedule implementation. The blackbox IR distinguishes primitive uses, controlled uses, and Spatial/Verilog implementations (`src/spatial/node/Blackbox.scala:37-58`), but there are no ScalaGen blackbox cases; an unhandled op reaches the base codegen error path when generation is enabled (`argon/src/argon/codegen/Codegen.scala:89-91`). Chisel, by contrast, has explicit primitive Spatial blackbox emission: it creates a Chisel `Module`, reassembles the packed input, recursively emits the Spatial function body, and wires result fields to module outputs (`src/spatial/codegen/chiselgen/ChiselGenBlackbox.scala:166-238`). Verilog blackboxes are also explicit Chisel wrappers around copied Verilog modules (`src/spatial/codegen/chiselgen/ChiselGenBlackbox.scala:20-73`).

For Rust/HLS, `PrimitiveBox` should be atomic at the scheduler boundary: Rust calls a supplied reference function or rejects the box if no model exists; HLS lowers it to an inline function, out-of-line function, or vendor/IP wrapper with declared latency/II. It should not imply child scheduling.

## Rust/HLS Decision

Use Chisel, not ScalaGen, as the schedule-bearing contrast. Chisel instantiates state-machine modules with `lhs.rawSchedule` (`src/spatial/codegen/chiselgen/ChiselGenController.scala:333-358`). Its `ForkJoin` outer controller starts all active children and increments only when all children report iteration done (`fringe/src/fringe/templates/Controllers.scala:141-154`). Therefore define canonical HLS `ForkJoin` as a parallel dataflow region with an explicit join barrier. Rust may offer a deterministic `compat_scalagen_serial` mode for golden-value comparison, but the decision semantics should model same-logical-time child start, explicit data/memory dependences, and join on all enabled children.
