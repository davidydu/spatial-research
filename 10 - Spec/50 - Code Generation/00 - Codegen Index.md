---
type: moc
project: spatial-spec
date_started: 2026-04-23
---

# Code Generation — Index

Backends that emit output from the fully-lowered IR.

## Backends

- `10 - Chiselgen/` — FPGA RTL emission (Chisel 3). The bulky production backend.
- `20 - Scalagen/` — **Reference-semantics emulator**. Ground truth for all other backends — when any two disagree, scalagen+emul is canonical.
- `30 - Cppgen/` — Host-side C++ for CPU+FPGA (AWS F1, Zynq, ZCU, VCS simulation, etc).
- `40 - Pirgen/` — Plasticine CGRA backend. Emits Plasticine IR for a separate compilation stack.
- `50 - Other Codegens.md` — `roguegen` (alternative host for KCU1500), `tsthgen` (Tungsten host), `dotgen`, `treegen`, `resourcegen`, `naming` — visualization, reporting, naming helpers.

## Integration seam

All backends are `argon.codegen.Codegen` subclasses, instantiated in `spatial/Spatial.scala:146-252` and gated by config flags (`enableSynth`, `enableSim`, `enablePIR`, `enableTsth`, `enableDot`, `reportArea`, `countResources`).

## Upstream coverage

- [[codegen-fpga-host-coverage]] — Chiselgen, Cppgen, Dotgen, Treegen, Resourcegen, Naming
- [[codegen-sim-alt-coverage]] — Scalagen, Pirgen, Roguegen, Tsthgen
