---
type: moc
project: spatial-spec
date_started: 2026-04-23
aliases:
  - "70 - Models and DSE"
---

# Models and DSE — Index

Hardware area/latency estimation and design space exploration.

## Sections

- `10 - Area Model.md` — `AreaModel` API (`areaOf`, `areaOfMem`, `areaOfReg`), `NodeParams` op-to-CSV dispatch, per-vendor `summarize` rollup, ML-based `AreaEstimator` usage.
- `20 - Latency Model.md` — `LatencyModel` API (`latencyOfNode`, `parallelModel`/`metaPipeModel`/`sequentialModel`/`streamingModel`/`outerControlModel`), retime-register predicate, `GenericLatencyModel` tile-transfer overlays.
- `30 - Target Hardware Specs.md` — One entry per supported target (Xilinx Zynq/ZCU/ZedBoard/AWS F1/KCU1500, Altera Arria10/DE1, Euresys CXP, Generic/ASIC/VCS, Plasticine). Resource capacity, burstSize, host codegen, clockRate.
- `40 - Design Space Exploration.md` — `DSEAnalyzer`, `ParameterAnalyzer`, `DSEThread`, `HyperMapperThread`, DSE driver flow.
- `50 - Memory Resources.md` — `MemoryResource` taxonomy (URAM/BRAM/URAM_OVERFLOW/LUTs/SRAM) and the allocator's greedy first-fit.
- `60 - CSV Model Format.md` — `SpatialModel` CSV schema, `Param…` columns, FIELDS columns, `NodeModel`/`LinearModel` fit.

## Source

- `src/spatial/targets/` (27 files)
- `models/src/` (13 files)
- `src/spatial/dse/` (18 files)
- [[hardware-targets-coverage]], [[poly-models-dse-coverage]]
