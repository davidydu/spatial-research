---
type: spec
concept: Memory Resources
source_files:
  - "src/spatial/targets/MemoryResource.scala:6-10"
  - "src/spatial/targets/HardwareTarget.scala:44-45"
  - "src/spatial/targets/xilinx/XilinxDevice.scala:13-83"
  - "src/spatial/targets/xilinx/XilinxDevice.scala:120-135"
  - "src/spatial/targets/generic/GenericDevice.scala:13-88"
  - "src/spatial/targets/altera/AlteraDevice.scala:13-39"
  - "src/spatial/targets/euresys/EuresysDevice.scala:13-39"
  - "src/spatial/targets/generic/ASIC.scala:14-20"
  - "src/spatial/targets/plasticine/Plasticine.scala:20-26"
  - "src/spatial/targets/AreaModel.scala:105-153"
  - "src/spatial/traversal/MemoryAllocator.scala:25-103"
  - "src/spatial/metadata/memory/BankingData.scala:180-188"
source_notes:
  - "[[poly-models-dse]]"
  - "[[fringe-and-targets]]"
hls_status: rework
hls_reason: "HLS resource taxonomy differs"
depends_on:
  - "[[10 - Area Model]]"
  - "[[40 - Design Space Exploration]]"
status: draft
---

# Memory Resources

## Summary

`MemoryResource` is Spatial's compiler-side memory-resource taxonomy: it names a storage class, computes an `Area` for a `(width, depth)` bank, reduces that `Area` to a scalar summary, and supplies an overridable minimum-depth threshold (`src/spatial/targets/MemoryResource.scala:6-10`). `HardwareTarget` makes the taxonomy target-local by requiring each target to expose both an ordered `memoryResources` list and a `defaultResource` fallback (`src/spatial/targets/HardwareTarget.scala:44-45`). `Memory.resource` stores the selected `MemoryResource` on each duplicate and falls back to `spatialConfig.target.defaultResource` when allocation has not set `resourceType` (`src/spatial/metadata/memory/BankingData.scala:180-188`). This makes memory-resource selection a metadata pass over banked memory duplicates, not a top-level singleton registry (`src/spatial/metadata/memory/BankingData.scala:180-188`, `src/spatial/traversal/MemoryAllocator.scala:25-40`).

## Mechanism

`AreaModel.SRAMArea` delegates bank sizing to the selected `MemoryResource.area`, and `rawMemoryBankArea` supplies that call with the memory word width and the `Memory.bankDepth` result (`src/spatial/targets/AreaModel.scala:105-128`). `rawMemoryArea` then multiplies the per-bank resource vector by the duplicate's total bank count and by the buffer depth, so a resource model is always evaluated per physical bank before duplication factors are applied (`src/spatial/targets/AreaModel.scala:145-153`). `MemoryAllocator.areaMetric` summarizes `areaModel.rawMemoryArea(mem, inst, resource)` through `resource.summary`, so allocation compares candidate memories using a resource-specific scalar rather than a uniform field such as slices (`src/spatial/traversal/MemoryAllocator.scala:31-33`).

The allocation pass partitions local non-blackbox memories into SRAM-able memories and everything else; SRAM-able means `isSRAM`, `isFIFO`, or `isLIFO` (`src/spatial/traversal/MemoryAllocator.scala:21-37`). It starts with all duplicates of SRAM-able memories as unassigned `Instance` values and initializes remaining capacity from `target.capacity` (`src/spatial/traversal/MemoryAllocator.scala:38-47`). It iterates `target.memoryResources.dropRight(1)`, so the final list element is not capacity-tested in the loop and instead acts as the catch-all assignment for all remaining SRAM-able and non-SRAM duplicates (`src/spatial/traversal/MemoryAllocator.scala:56-60`, `src/spatial/traversal/MemoryAllocator.scala:102-103`). For each non-final resource, it computes raw counts, wraps each as `Area(resource.name -> count)`, sorts candidates by descending `rawCount`, and assigns a duplicate only when `area <= capacity` and `depth >= resource.minDepth` (`src/spatial/traversal/MemoryAllocator.scala:62-88`). This source behavior means list order is load-bearing, and the source sorts largest raw resource users first even though one nearby comment says "smallest to largest" (`src/spatial/traversal/MemoryAllocator.scala:31-33`, `src/spatial/traversal/MemoryAllocator.scala:78-88`).

## Implementation

`XilinxDevice` defines four resource objects inside the abstract device class: `URAM_RESOURCE`, `BRAM_RESOURCE`, `URAM_RESOURCE_OVERFLOW`, and `LUTs_RESOURCE` (`src/spatial/targets/xilinx/XilinxDevice.scala:8-31`). The Xilinx ordered list is `URAM_RESOURCE`, `BRAM_RESOURCE`, `URAM_RESOURCE_OVERFLOW`, then `LUTs_RESOURCE`, and `defaultResource` is `BRAM_RESOURCE` (`src/spatial/targets/xilinx/XilinxDevice.scala:33-39`). `URAM_RESOURCE` and `URAM_RESOURCE_OVERFLOW` both summarize the `URAM` field, but the primary URAM threshold is `minDepth = 512` while the overflow threshold is `minDepth = 32` (`src/spatial/targets/xilinx/XilinxDevice.scala:13-27`). `BRAM_RESOURCE` summarizes `ceil(RAM18 / 2) + RAM36` and requires `minDepth = 32` (`src/spatial/targets/xilinx/XilinxDevice.scala:18-22`). `LUTs_RESOURCE` computes distributed memory area and summarizes it by multiplying each RAM-LUT primitive count by `RAM_LUT_USAGE` (`src/spatial/targets/xilinx/XilinxDevice.scala:28-31`, `src/spatial/targets/xilinx/XilinxDevice.scala:120-135`).

The Xilinx URAM model uses `cols = ceil(width / 72.0)`, a fixed `uramWordDepth(width) = 4096`, and row count `ceil(depth / wordDepth)` before returning `Area(URAM -> totalURAM)` (`src/spatial/targets/xilinx/XilinxDevice.scala:51-60`). The Xilinx BRAM model uses a width table where one-bit memories get depth 16384, two-bit memories get 8192, widths up to 4 get 4096, widths up to 9 get 2048, widths up to 18 get 1024, and larger widths get 512 (`src/spatial/targets/xilinx/XilinxDevice.scala:41-49`). It then computes BRAM columns as `ceil(width / 18.0)`, splits paired columns into RAM36 and a possible leftover RAM18, multiplies by row count, and returns `Area(RAM18 -> totalRAM18, RAM36 -> totalRAM36)` (`src/spatial/targets/xilinx/XilinxDevice.scala:62-77`). The distributed LUT-memory model uses `ceil(width / 2)` columns, returns `RAM32M` for depths up to 32, and returns `RAM64M * ceil(depth / 64.0)` for deeper memories (`src/spatial/targets/xilinx/XilinxDevice.scala:79-83`).

`GenericDevice`, `AlteraDevice`, and `EuresysDevice` duplicate the same URAM/BRAM/overflow/LUT resource pattern and resource ordering as Xilinx (`src/spatial/targets/generic/GenericDevice.scala:13-44`, `src/spatial/targets/altera/AlteraDevice.scala:13-39`, `src/spatial/targets/euresys/EuresysDevice.scala:13-39`). `GenericDevice` also defines an `SRAM_RESOURCE` with empty area and zero summary, but its own `memoryResources` list does not include that object and its `defaultResource` remains `BRAM_RESOURCE` (`src/spatial/targets/generic/GenericDevice.scala:33-44`). `ASIC` and `Plasticine` each define an in-object `SRAM_RESOURCE`, set it as `defaultResource`, and expose a one-element `memoryResources` list containing that SRAM fallback (`src/spatial/targets/generic/ASIC.scala:14-20`, `src/spatial/targets/plasticine/Plasticine.scala:20-26`).

## Interactions

The allocator is invoked from `MemoryAllocator.process`, which currently prints "TODO: un-gut memory allocator" and then calls `allocate()` before returning the block unchanged (`src/spatial/traversal/MemoryAllocator.scala:12-19`). Banking metadata stores only an optional `resourceType`, so downstream reporters and area queries see the selected resource through `Memory.resource` after allocation or the target default before allocation (`src/spatial/metadata/memory/BankingData.scala:180-188`). The catch-all rule matters because Xilinx-like targets make `LUTs_RESOURCE` the final element, while ASIC and Plasticine make `SRAM_RESOURCE` the only and therefore final element (`src/spatial/targets/xilinx/XilinxDevice.scala:33-39`, `src/spatial/targets/generic/ASIC.scala:19-20`, `src/spatial/targets/plasticine/Plasticine.scala:25-26`).

## HLS notes

The trait shape is reusable for HLS because it separates resource naming, bank-area evaluation, scalar allocation priority, and minimum-depth eligibility (`src/spatial/targets/MemoryResource.scala:6-10`, `src/spatial/traversal/MemoryAllocator.scala:31-33`, `src/spatial/traversal/MemoryAllocator.scala:85-88`). The concrete taxonomy is not portable as-is because the existing resource names and analytic models encode FPGA URAM, BRAM, RAM18/RAM36, and distributed LUT primitives (`src/spatial/targets/xilinx/XilinxDevice.scala:13-83`). An HLS backend should define a new ordered list, new catch-all behavior, and new capacity fields against HLS reports rather than preserving Xilinx LUT-memory buckets (inferred, unverified).

## Open questions

- [[open-questions-models-dse-fringe-gaps#Q-mdf-01 - 2026-04-24 HLS memory-resource taxonomy and catch-all order|Q-mdf-01]]
- [[open-questions-models-dse-fringe-gaps#Q-mdf-02 - 2026-04-24 GenericDevice SRAM resource is defined but unselected|Q-mdf-02]]
