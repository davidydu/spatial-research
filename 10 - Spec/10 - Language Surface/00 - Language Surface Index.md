---
type: moc
project: spatial-spec
date_started: 2026-04-23
---

# Language Surface — Index

User-facing DSL API. What an application writer types.

## Sections

- `10 - Controllers.md` — `Accel`, `Foreach`, `Reduce`, `Fold`, `MemReduce`, `MemFold`, `Pipe`, `Stream`, `Sequential`, `Parallel`, `FSM`, `Named`, schedule/II/POM/MOP/NoBind/haltIfStarved modifiers, `ForcedLatency`.
- `20 - Memories.md` — `DRAM`, `SRAM`, `RegFile`, `Reg`, `FIFO`, `LIFO`, `LineBuffer`, `MergeBuffer`, `LUT`/`FileLUT`, `LockMem` family, `Frame`. Dimensionality, constructors, read/write API, tuning hints.
- `30 - Primitives.md` — `Counter`, `CounterChain`, `Wildcard`, `Bus` family (`PinBus`, `AxiStream*`, `BurstCmdBus`, `FileBus`, etc.), `Pin`.
- `40 - Streams and Blackboxes.md` — `StreamIn`, `StreamOut`, `StreamStruct`, `Blackbox`/`SpatialBlackbox`/`SpatialCtrlBlackbox`, `VerilogPrimitive`, `VerilogController`.
- `50 - Math and Helpers.md` — reductions (`sum`, `product`, `reduce`, `reduceTree`), numeric (`min`, `max`, `pow`, `abs`, `exp`, `ln`, `sqrt`, trig), Taylor approximations, `mux`/`oneHotMux`/`priorityMux`, `priorityDeq`/`roundRobinDeq`, `retimeGate`/`retime`.
- `60 - Host and IO.md` — host `Array`, `Matrix`, `Tensor3-5`, `CSVFile`, `BinaryFile`, `TensorData`, `setArg`/`getArg`/`setMem`/`getMem`, CSV/binary/numpy file IO, `setFrame`/`getFrame`.
- `70 - Debugging and Checking.md` — `printArray`/`printMatrix`/`printTensor*`/`printSRAM*`, `approxEql`, `checkGold`, `r"..."` interpolator, unstaged `If`/`IfElse`, `sleep`.
- `80 - Virtualization.md` — `SpatialVirtualization`: `__newVar`/`__assign`/`__ifThenElse`/`__whileDo` (disabled)/`__return` (disabled)/`__throw`, `@virtualize` integration.
- `90 - Aliases and Shadowing.md` — `InternalAliases`/`ExternalAliases`/`ShadowingAliases`, the `gen.*` Scala-native escape hatch, the `dsl` vs `libdsl` distinction.
- `99 - Macros.md` — `@spatial`, `@struct`, `@streamstruct` app-macro annotations.
- [[00 - Standard Library Index|A0 - Standard Library]] — user-callable `spatial.lib.*` templates for BLAS, ML, sort/scan, and meta-programming helpers.

## Top-level plumbing

- **Entry**: `SpatialApp extends Spatial with DSLApp` (`src/spatial/SpatialApp.scala:5`). Users import `spatial.dsl._` (with Scala shadowing) or `spatial.libdsl._` (without).
- **Driver**: `trait Spatial extends Compiler` (`src/spatial/Spatial.scala:33-647`) — declares passes, wires the runPasses DAG, parses CLI, resolves targets.
- **Config**: `class SpatialConfig extends argon.Config` (`src/spatial/SpatialConfig.scala`) — mutable flags controlling every phase.

## Upstream coverage

- [[spatial-lang-coverage]] — Phase 1 coverage note, verified 2026-04-21.
