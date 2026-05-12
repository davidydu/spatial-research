---
type: "research"
decision: "D-04"
angle: 1
---

# Allocator Contract

## Decision Context

Q-079 asks for the HLS memory-resource list, minimum-depth rules, capacity fields, and final catch-all behavior before porting allocation. The current Spatial behavior is concrete but caveated: `MemoryAllocator.process` prints `TODO: un-gut memory allocator`, calls `allocate()`, and returns the input block unchanged (`src/spatial/traversal/MemoryAllocator.scala:15-18`). So D-04 should treat the code below as the executable contract today, not necessarily as proof that this was the intended final allocator.

## Resource Interface

`MemoryResource` is a small target-local contract: each resource has a `name`, must implement `area(width, depth): Area`, must implement `summary(area): Double`, and may override `minDepth`, whose default is `0` (`src/spatial/targets/MemoryResource.scala:6-10`). `HardwareTarget` separately requires a target-wide `capacity: Area`, an ordered `memoryResources: List[MemoryResource]`, and a `defaultResource` (`src/spatial/targets/HardwareTarget.scala:29-30`, `src/spatial/targets/HardwareTarget.scala:44-45`). The selected resource is stored per banked duplicate as `Memory.resourceType`; if unset, `Memory.resource` falls back to `spatialConfig.target.defaultResource` (`src/spatial/metadata/memory/BankingData.scala:180-188`).

For HLS, this means a resource is not just a label. Its `name` is also the key the allocator uses for capacity accounting: for each candidate, the allocator computes a scalar raw count, wraps it as `Area(resource.name -> count)`, checks it against remaining capacity, and subtracts it after assignment (`src/spatial/traversal/MemoryAllocator.scala:62-65`, `src/spatial/traversal/MemoryAllocator.scala:85-89`). Therefore every capacity-tested HLS memory resource needs a capacity field whose name matches the resource name, unless D-04 changes the algorithm.

## Current Algorithm

Allocation starts from `LocalMemories.all.filter(!_.isCtrlBlackbox)`, partitions memories into SRAM-able and non-SRAM groups, and defines SRAM-able as `isSRAM || isFIFO || isLIFO` (`src/spatial/traversal/MemoryAllocator.scala:21-23`, `src/spatial/traversal/MemoryAllocator.scala:35-40`). Only duplicates of SRAM-able memories enter the greedy loop; non-SRAM duplicates are handled later by the catch-all rule (`src/spatial/traversal/MemoryAllocator.scala:38-40`, `src/spatial/traversal/MemoryAllocator.scala:102-103`).

The pass initializes `capacity` from `target.capacity`, binds `resources = target.memoryResources`, and iterates `resources.dropRight(1)` in list order (`src/spatial/traversal/MemoryAllocator.scala:45-59`). The last resource is deliberately excluded from capacity-tested allocation. For each non-final resource, it profiles every still-unassigned duplicate using `areaMetric`, which calls `areaModel.rawMemoryArea(mem, inst, resource)` and then `resource.summary(...)` (`src/spatial/traversal/MemoryAllocator.scala:31-33`, `src/spatial/traversal/MemoryAllocator.scala:62-66`). It then sorts candidates by `-rawCount`, so larger users of the current resource are considered first; the nearby "smallest to largest" comment does not match the implementation (`src/spatial/traversal/MemoryAllocator.scala:31-33`, `src/spatial/traversal/MemoryAllocator.scala:78-81`).

## Assignment Rules

A duplicate is assigned to the current resource only if both checks pass: the single-field `area` is `<= capacity`, and the computed bank depth is at least `resource.minDepth` (`src/spatial/traversal/MemoryAllocator.scala:83-89`). On success, the allocator sets `dup.resourceType = Some(resource)`, decrements `capacity -= area`, and removes the instance from `unassigned` after that resource pass (`src/spatial/traversal/MemoryAllocator.scala:85-99`). On failure, the duplicate remains available for later resources; there is no backtracking, no cross-resource swap, and no later reconsideration once a duplicate has been assigned (`src/spatial/traversal/MemoryAllocator.scala:78-99`).

The built-in FPGA-like taxonomy uses ordered resources `URAM_RESOURCE`, `BRAM_RESOURCE`, `URAM_RESOURCE_OVERFLOW`, then `LUTs_RESOURCE` (`src/spatial/targets/xilinx/XilinxDevice.scala:33-39`; duplicated in `src/spatial/targets/generic/GenericDevice.scala:38-44`, `src/spatial/targets/altera/AlteraDevice.scala:33-39`, and `src/spatial/targets/euresys/EuresysDevice.scala:33-39`). `URAM_RESOURCE` requires `minDepth = 512`; BRAM and URAM-overflow require `minDepth = 32`; LUTs inherit the default `0` (`src/spatial/targets/xilinx/XilinxDevice.scala:13-31`). ASIC and Plasticine instead expose a one-element list containing `SRAM_RESOURCE` (`src/spatial/targets/generic/ASIC.scala:14-20`, `src/spatial/targets/plasticine/Plasticine.scala:20-26`).

## Catch-All Contract

After all capacity-tested resources run, every still-unassigned SRAM-able duplicate is assigned to `resources.last`, and every non-SRAM duplicate is also assigned to `resources.last` (`src/spatial/traversal/MemoryAllocator.scala:102-103`). This final assignment does not check capacity, does not check `minDepth`, and does not compute an area fit. It also implies `memoryResources` must be non-empty, because `resources.last` is used without an assertion (`src/spatial/traversal/MemoryAllocator.scala:56-59`, `src/spatial/traversal/MemoryAllocator.scala:102-103`).

Exact HLS parity would therefore make the final resource an explicit unlimited or deliberately unchecked fallback, with all finite capacity resources before it. If D-04 wants HLS reports to enforce a hard total memory budget, the current Spatial algorithm is insufficient without an added post-allocation validation or a capacity-tested final resource (unverified).
