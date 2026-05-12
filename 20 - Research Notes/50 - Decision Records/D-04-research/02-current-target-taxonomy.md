---
type: "research"
decision: "D-04"
angle: 2
---

# Current target memory-resource taxonomy

## Scope and target set

`MemoryResource` is a small target-side contract: each resource has a `name`, an `area(width, depth)` model, a `summary(area)` scalar used for allocation ranking, and a default `minDepth` of `0` unless overridden (`src/spatial/targets/MemoryResource.scala:6-10`). Every `HardwareTarget` must expose `memoryResources` and `defaultResource`, plus an `Area` capacity map over its `AFIELDS` (`src/spatial/targets/HardwareTarget.scala:14-30`, `src/spatial/targets/HardwareTarget.scala:44-45`).

The exported FPGA set is `Zynq`, `ZCU`, `ZedBoard`, `AWS_F1`, `KCU1500`, `CXP`, `DE1`, `Arria10`, and `VCS`; `all` adds `Plasticine`, while `ASIC` is exported as a lazy value but not included in `all` (`src/spatial/targets/package.scala:4-30`).

## Resource lists

| Target family | `memoryResources` order | `defaultResource` | Resource summaries and `minDepth` |
|---|---|---|---|
| `XilinxDevice` | `URAM_RESOURCE`, `BRAM_RESOURCE`, `URAM_RESOURCE_OVERFLOW`, `LUTs_RESOURCE` | `BRAM_RESOURCE` | URAM summarizes `area(URAM)`, min depth 512; BRAM summarizes `ceil(RAM18 / 2) + RAM36`, min depth 32; overflow is also named `URAM`, summarizes `area(URAM)`, min depth 32; LUTs summarizes weighted RAM LUT fields and inherits min depth 0 (`src/spatial/targets/xilinx/XilinxDevice.scala:13-39`, `src/spatial/targets/xilinx/XilinxDevice.scala:120-135`). |
| `AlteraDevice` | same four-item order | `BRAM_RESOURCE` | Same object names, models, summaries, and min-depth rules as `XilinxDevice` (`src/spatial/targets/altera/AlteraDevice.scala:13-39`, `src/spatial/targets/altera/AlteraDevice.scala:121-136`). |
| `EuresysDevice` | same four-item order | `BRAM_RESOURCE` | Same object names, models, summaries, and min-depth rules as `XilinxDevice` (`src/spatial/targets/euresys/EuresysDevice.scala:13-39`, `src/spatial/targets/euresys/EuresysDevice.scala:120-135`). |
| `GenericDevice` | same four-item order | `BRAM_RESOURCE` | Same four active resources as above; it also defines `SRAM_RESOURCE` with zero area and zero summary but does not include it in `memoryResources` (`src/spatial/targets/generic/GenericDevice.scala:13-44`). |
| `ASIC` | `SRAM_RESOURCE` only | `SRAM_RESOURCE` | SRAM area is empty and summary is `0.0`; min depth is inherited as 0 (`src/spatial/targets/generic/ASIC.scala:14-20`). |
| `Plasticine` | `SRAM_RESOURCE` only | `SRAM_RESOURCE` | Same zero-area SRAM behavior as ASIC; capacity is empty (`src/spatial/targets/plasticine/Plasticine.scala:15-26`). |

## Capacity fields

Xilinx targets use the Xilinx field vocabulary from `AFIELDS`, including `RAM18`, `RAM36`, `BRAM`, `URAM`, RAM LUT fields, DSPs, registers, slices, and LUT fields (`src/spatial/targets/xilinx/XilinxDevice.scala:10`). `Zynq` and `ZedBoard` publish `SLICEL`, `SLICEM`, `Slices`, `Regs`, `BRAM`, and `DSPs`, but no `URAM` (`src/spatial/targets/xilinx/Zynq.scala:11-18`, `src/spatial/targets/xilinx/ZedBoard.scala:11-18`). `ZCU` and `KCU1500` publish the same field names, with larger `Regs`, `BRAM`, and `DSPs`, also no `URAM` (`src/spatial/targets/xilinx/ZCU.scala:12-19`, `src/spatial/targets/xilinx/KCU1500.scala:12-19`). `AWS_F1` is the only surveyed target with an explicit `URAM -> 960` capacity, plus `BRAM -> 2160`, `DSPs -> 6840`, `Regs -> 2364480`, and slice fields (`src/spatial/targets/xilinx/AWS_F1.scala:13-21`).

`CXP` uses the same capacity fields and values as `Zynq`/`ZedBoard`, without URAM (`src/spatial/targets/euresys/CXP.scala:11-18`). `VCS` provides very large capacities for slice fields, registers, BRAM, and DSPs, but no URAM (`src/spatial/targets/generic/VCS.scala:14-21`). `DE1`, `Arria10`, `ASIC`, and `Plasticine` have empty capacity maps (`src/spatial/targets/altera/DE1.scala:11-13`, `src/spatial/targets/altera/Arria10.scala:11-13`, `src/spatial/targets/generic/ASIC.scala:26-28`, `src/spatial/targets/plasticine/Plasticine.scala:15`). Missing capacity fields read as the target `AreaFields` default, because model lookup returns the field default when an entry is absent (`models/src/models/Model.scala:25-27`, `src/spatial/targets/HardwareTarget.scala:22`).

## Allocation behavior

`MemoryAllocator` partitions local non-blackbox memories into SRAM-able memories (`SRAM`, `FIFO`, `LIFO`) and non-SRAM memories (`src/spatial/traversal/MemoryAllocator.scala:21-39`). It then iterates `target.memoryResources.dropRight(1)`, computes each candidate's raw memory area using that resource, summarizes it to a scalar, wraps it as `Area(resource.name -> count)`, sorts larger counts first, and assigns only when area fits remaining capacity and bank depth meets `resource.minDepth` (`src/spatial/traversal/MemoryAllocator.scala:56-89`). Capacity is decremented only for these non-final resources (`src/spatial/traversal/MemoryAllocator.scala:85-89`).

The final catch-all is not `defaultResource`; it is `resources.last`. All remaining SRAM-able instances and all non-SRAM duplicate instances are assigned to that last resource without capacity or min-depth checks (`src/spatial/traversal/MemoryAllocator.scala:99-103`). Therefore FPGA-like targets fall back to `LUTs_RESOURCE`, while ASIC and Plasticine fall back to SRAM. `defaultResource` is only the metadata fallback when a `Memory` has no explicit `resourceType` (`src/spatial/metadata/memory/BankingData.scala:180-188`).

## Dead or mismatched definitions

`GenericDevice.SRAM_RESOURCE` appears dead for normal allocation: it is defined but absent from the four-resource list used by `VCS` (`src/spatial/targets/generic/GenericDevice.scala:33-44`). `AlteraDevice` reuses the Xilinx-style field names and memory formulas, and its companion object is marked "Fill me in correctly please"; both concrete Altera targets then provide empty capacities, so their checked URAM/BRAM passes have zero budget and the unchecked final LUT catch-all receives the leftovers (`src/spatial/targets/altera/AlteraDevice.scala:10-39`, `src/spatial/targets/altera/AlteraDevice.scala:89-96`, `src/spatial/targets/altera/DE1.scala:11-13`, `src/spatial/targets/altera/Arria10.scala:11-13`). `URAM_RESOURCE_OVERFLOW` is intentionally a second `URAM` pass with a lower min depth, but it is operational only where `URAM` capacity exists; among surveyed concrete targets, that is `AWS_F1` (`src/spatial/targets/xilinx/XilinxDevice.scala:23-27`, `src/spatial/targets/xilinx/AWS_F1.scala:13-21`).
