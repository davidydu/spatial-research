---
type: moc
project: spatial-spec
date_started: 2026-04-23
---

# Semantics — Index

Cross-cutting formal semantics. Synthesized from Argon framework, Spatial IR, pass pipeline, and language surface. Drafted last (per [[workflow]] Phase 2 priority 5).

## Sections

- `10 - Effects and Aliasing.md` — Effects lattice, `Impure` wrapper, alias propagation, mutable aliases, atomic writes.
- `20 - Scheduling Model.md` — Scope bundles, `SimpleScheduler` DCE, code motion, `BlockOptions`.
- `30 - Control Semantics.md` — Controller schedules (`Pipelined`, `Sequenced`, `ForkJoin`, `Streaming`, `Fork`), II, parallelization lanes, metapipelining.
- `40 - Memory Semantics.md` — Local vs remote memory invariants, banking contract, duplicates, N-buffering, ports, retiming implications.
- `50 - Data Types.md` — Fixed/float bit-exactness, saturation/unbiased variants, bit-vector semantics.
- `60 - Reduction and Accumulation.md` — `OpReduce`, `OpMemReduce`, accumulator-cycle detection, `RegAccumOp`/`RegAccumFMA`.
- `70 - Timing Model.md` — Latency computation, delay lines, retiming boundaries, pipeline fill/drain, compiler II vs target II.
- `80 - Streaming.md` — `Streaming` controllers, FIFO/stream backpressure semantics, MetaPipe-to-Stream transform.
- `90 - Host-Accel Boundary.md` — `AccelScope`, `ArgIn`/`ArgOut`/`HostIO`, DRAM host↔accel phases, `setArg`/`setMem` bookkeeping.

## Synthesis inputs

- [[10 - Spec/30 - IR/00 - Argon Framework/00 - Argon Index|00 - Argon Index]]
- [[10 - Spec/30 - IR/10 - Spatial Nodes/00 - Spatial Nodes Index|00 - Spatial Nodes Index]]
- [[10 - Spec/40 - Compiler Passes/00 - Pass Pipeline Index|00 - Pass Pipeline Index]]
- [[10 - Spec/10 - Language Surface/00 - Language Surface Index|00 - Language Surface Index]]
