---
type: spec
concept: Target Hardware Specs
source_files:
  - "src/spatial/targets/HardwareTarget.scala:7-58"
  - "src/spatial/targets/AreaModel.scala:15-208"
  - "src/spatial/targets/xilinx/XilinxDevice.scala:8-136"
  - "src/spatial/targets/xilinx/XilinxAreaModel.scala:8-108"
  - "src/spatial/targets/xilinx/Zynq.scala:6-19"
  - "src/spatial/targets/xilinx/ZCU.scala:6-20"
  - "src/spatial/targets/xilinx/ZedBoard.scala:6-19"
  - "src/spatial/targets/xilinx/AWS_F1.scala:6-22"
  - "src/spatial/targets/xilinx/KCU1500.scala:6-20"
  - "src/spatial/targets/altera/Arria10.scala:6-14"
  - "src/spatial/targets/altera/DE1.scala:6-14"
  - "src/spatial/targets/euresys/CXP.scala:6-19"
  - "src/spatial/targets/generic/ASIC.scala:8-29"
  - "src/spatial/targets/generic/VCS.scala:8-22"
  - "src/spatial/targets/plasticine/Plasticine.scala:8-28"
  - "src/spatial/targets/package.scala:3-31"
  - "src/spatial/targets/generic/TileLoadModel.scala:16-109"
source_notes:
  - "[[fringe-and-targets]]"
hls_status: rework
hls_reason: "The abstraction is reusable, but resource fields, capacities, reports, and latency data must be redesigned for Rust/HLS"
depends_on:
  - "[[10 - Area Model]]"
  - "[[20 - Latency Model]]"
  - "[[50 - Memory Resources]]"
  - "[[60 - CSV Model Format]]"
status: draft
---

# Target Hardware Specs

## Summary

Spatial has a compiler-side target abstraction distinct from Fringe's Chisel `DeviceTarget`. `HardwareTarget` drives DSE and model loading: it names the target, burst size in bits, area-field schema, latency-field schema, DSP cutoff, clock rate, startup base cycles, resource capacity, area/latency model factories, memory-resource priority list, default memory resource, and analyzer factories (`src/spatial/targets/HardwareTarget.scala:7-58`). This layer does not elaborate hardware; it tells the compiler how much hardware exists and how to estimate generated IR cost.

## Abstract contract

`HardwareTarget` defaults `host` to `"cpp"`, `clockRate` to `150.0f`, and `baseCycles` to `43000` (`src/spatial/targets/HardwareTarget.scala:10-18`). It lazily caches area and latency models, creates implicit field configurations from `AFIELDS` and `LFIELDS`, and requires concrete targets to provide `capacity`, `makeAreaModel`, `makeLatencyModel`, `memoryResources`, and `defaultResource` (`src/spatial/targets/HardwareTarget.scala:19-48`). The public latency fields are `RequiresRegs`, `LatencyOf`, `LatencyInReduce`, `RequiresInReduce`, and `BuiltInLatency` (`src/spatial/targets/HardwareTarget.scala:52-58`).

`AreaModel` is the main target consumer. It names the CSV file from `target.name + "_Area.csv"`, exposes target area fields, dispatches `areaOf` only for hardware-scope nodes, estimates memories with flat banking assumptions and ML LUT/FF estimates, hard-codes RAM36 analytically while forcing RAM18 to zero, maps selected fixed arithmetic to one DSP, and summarizes target-specific area through an abstract `summarize` (`src/spatial/targets/AreaModel.scala:15-35`, `src/spatial/targets/AreaModel.scala:60-92`, `src/spatial/targets/AreaModel.scala:161-208`). The `OpMemReduce` access-unroll case carries a comment saying the formula is definitely wrong (`src/spatial/targets/AreaModel.scala:41-58`).

## Vendor bases

`XilinxDevice` defines the long `AFIELDS` array, `DSP_CUTOFF = 16`, URAM/BRAM/URAM-overflow/LUT memory resources, BRAM as default, BRAM and URAM word-depth models, BRAM/URAM/distributed-memory area models, and Xilinx-specific area and latency model factories (`src/spatial/targets/xilinx/XilinxDevice.scala:8-88`). Its companion object defines all field-name strings and LUT usage for distributed RAM primitives (`src/spatial/targets/xilinx/XilinxDevice.scala:89-136`).

`XilinxAreaModel.summarize` rolls primitive fields into total SLICEM, SLICEL, Slices, Regs, DSPs, BRAM, and URAM. It counts LUT1-3 as half a LUT, LUT4-6 as full LUTs, memory LUTs through the RAM LUT usage map, register-only slices through a `1.9` factor, BRAM as `RAM18/2 + RAM36`, and suppresses the verbose report behind `if (false)` (`src/spatial/targets/xilinx/XilinxAreaModel.scala:8-108`). Altera, Euresys, and Generic device bases largely copy the same Xilinx-style fields, resource order, and memory formulas; Altera and Euresys area models add `model("Fringe")()` and gate the report on `config.enInfo`, while Generic uses the Xilinx-style no-Fringe/no-report shape (`src/spatial/targets/altera/AlteraDevice.scala:8-137`, `src/spatial/targets/euresys/EuresysDevice.scala:8-136`, `src/spatial/targets/generic/GenericDevice.scala:8-140`, `src/spatial/targets/altera/AlteraAreaModel.scala:8-108`, `src/spatial/targets/euresys/EuresysAreaModel.scala:8-108`).

## Concrete targets

The Xilinx family provides five compiler targets. `Zynq` is named `"Zynq"`, uses 512-bit bursts, and has capacity for SLICEL, SLICEM, Slices, Regs, BRAM, and DSPs (`src/spatial/targets/xilinx/Zynq.scala:6-19`). `ZCU` is 512-bit and carries a TODO that resources are cut in half to make HyperMapper work harder on smaller apps (`src/spatial/targets/xilinx/ZCU.scala:6-20`). `ZedBoard` duplicates Zynq capacity with name `"ZedBoard"` (`src/spatial/targets/xilinx/ZedBoard.scala:6-19`). `AWS_F1` uses 512-bit bursts, very large slice/register/BRAM/DSP capacities, and includes `URAM -> 960` (`src/spatial/targets/xilinx/AWS_F1.scala:6-22`). `KCU1500` overrides host codegen to `"rogue"` and otherwise uses a ZCU-like capacity profile (`src/spatial/targets/xilinx/KCU1500.scala:6-20`).

`Arria10` and `DE1` extend `AlteraDevice`, both use 512-bit bursts, and both leave capacity empty with a `Fill me in` placeholder (`src/spatial/targets/altera/Arria10.scala:6-14`, `src/spatial/targets/altera/DE1.scala:6-14`). `CXP` extends `EuresysDevice`, uses 512-bit bursts, and copies a Zynq-like capacity (`src/spatial/targets/euresys/CXP.scala:6-19`). `ASIC` is a generic `HardwareTarget` with no area fields, zero DSP cutoff, `GenericAreaModel`, but a latency model built from `xilinx.Zynq`; it has a single SRAM memory resource and empty capacity (`src/spatial/targets/generic/ASIC.scala:8-29`). `VCS` extends `GenericDevice`, uses 512-bit bursts, and declares pseudo-infinite resource capacities using large constants (`src/spatial/targets/generic/VCS.scala:8-22`). `Plasticine` has no area fields, zero DSP cutoff, 512-bit bursts, `clockRate = 1000.0f`, empty capacity, a Plasticine area model that returns area unchanged, normal latency model, and a single SRAM resource (`src/spatial/targets/plasticine/Plasticine.scala:8-28`, `src/spatial/targets/plasticine/PlasticineAreaModel.scala:8-13`).

`spatial.targets.package` exposes `fpgas` as Zynq, ZCU, ZedBoard, AWS_F1, KCU1500, CXP, DE1, Arria10, and VCS; `Default` is Zynq; aliases expose ASIC and Plasticine, but `all` is `fpgas + Plasticine`, so ASIC is not in the public `all` set (`src/spatial/targets/package.scala:3-31`).

## Known gaps

Generic latency contains an effectively disabled tile-load neural model: `GenericLatencyModel` instantiates `TileLoadModel` and uses `memModel.evaluate`, but `TileLoadModel.init()` is empty and `evaluate` returns `0.0` after a commented-out neural-network body (`src/spatial/targets/generic/GenericLatencyModel.scala:11-68`, `src/spatial/targets/generic/TileLoadModel.scala:16-109`). This means generic tile-load parallel speedup contributes nothing in the current source.

## HLS notes

The `HardwareTarget` idea is reusable, but the field schema is not HLS-ready. HLS needs resource names that match HLS reports, capacities for the intended FPGA or simulator target, memory-resource ordering with an explicit catch-all, and latency/area models trained against the HLS backend. Existing empty capacities, Zynq-borrowed ASIC latency, Xilinx-shaped Altera/Euresys fields, and disabled tile-load modeling are not clean foundations for a Rust/HLS target.

## Open questions

- [[open-questions-fringe-targets#Q-ft-01 - 2026-04-25 Base-cycle consumer for compiler targets|Q-ft-01]]
- [[open-questions-fringe-targets#Q-ft-05 - 2026-04-25 ASIC latency model source|Q-ft-05]]
- [[open-questions-fringe-targets#Q-ft-06 - 2026-04-25 Empty non-Xilinx target capacities|Q-ft-06]]
- [[open-questions-fringe-targets#Q-ft-07 - 2026-04-25 OpMemReduce access-unroll formula|Q-ft-07]]
- [[open-questions-fringe-targets#Q-ft-08 - 2026-04-25 TileLoadModel disabled state|Q-ft-08]]
