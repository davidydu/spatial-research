---
type: moc
project: spatial-spec
date_started: 2026-04-23
---

# Runtime and Fringe — Index

Runtime software/HDL that the emitted accelerator binds against for host communication, DRAM streaming, and board control.

## Sections

- `10 - Fringe Architecture.md` — `SpatialIP`, `AbstractAccelUnit`, `DeviceTarget`, target-specific fringe shells, globals, channel assignment, and `bug239_hack`.
- `20 - DRAM Arbiter and AXI.md` — `DRAMArbiter`, `StreamArbiter`, AXI command split/issue, AXI4 bundles, and MAG-to-AXI bridge.
- `30 - Ledger and Kernel.md` — `Ledger` cross-kernel port boring, `Kernel.configure`, `ModuleParams`, controller templates, counters, and DRAM interface binding.
- `40 - Hardware Templates.md` — memory primitives, counters, controllers, n-buffer/regfile/accum templates, retiming helpers, and allocator-facing template metadata.
- `50 - BigIP and Arithmetic.md` — `BigIP` abstract arithmetic service, per-target subclasses, simulator arithmetic, fixed/floating conversion, and vendored Berkeley HardFloat.
- `60 - Instantiation.md` — `Instantiator.scala` + `AccelWrapper.scala` + `AccelUnit.scala` emission from ChiselGen.

## Source

- `fringe/src/` (149 files — largest single subsystem)
- [[fringe-coverage]]
