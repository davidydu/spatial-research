---
type: "research"
decision: "D-04"
angle: 8
---

# DSE, Reports, And HLS Reconciliation

## DSE Validity Surface

`DSEThread` makes the target capacity the validity contract: it reads `target.capacity`, derives CSV area headings from `capacity.nonZeroFields`, marks a design valid only when `area <= capacity && !state.hadErrors`, and emits only `area.seq(areaHeading:_*)` into the DSE result row (`src/spatial/dse/DSEThread.scala:48-50`, `src/spatial/dse/DSEThread.scala:119-123`). The area being checked is not a raw memory-allocation table; `DSEAreaAnalyzer` resets and reruns the area model, folds scope areas, then calls `areaModel.summarize(total)` before storing `totalArea` (`src/spatial/dse/DSEAreaAnalyzer.scala:43-55`). For D-04, this means HLS capacity fields must be chosen for the summarized validity surface, not just for allocator internals.

The resource-field vocabulary is target-defined. `HardwareTarget` requires `AFIELDS`, derives `AreaFields` from it, and exposes `capacity: Area` as the device maximum (`src/spatial/targets/HardwareTarget.scala:14`, `src/spatial/targets/HardwareTarget.scala:22`, `src/spatial/targets/HardwareTarget.scala:29`). Xilinx-style targets include primitive memory fields, aggregate `BRAM` and `URAM`, distributed-RAM fields, DSPs, registers, and slice fields in `AFIELDS` (`src/spatial/targets/xilinx/XilinxDevice.scala:10`). Concrete capacity may still publish only a subset: ZCU records `SLICEL`, `SLICEM`, `Slices`, `Regs`, `BRAM`, and `DSPs` (`src/spatial/targets/xilinx/ZCU.scala:12-18`).

## Allocation Metadata

The allocator's taxonomy is `target.memoryResources`. It iterates every resource except the last, computes `rawMemoryArea`, summarizes the result through the resource, wraps it as `Area(resource.name -> count)`, and assigns only when both capacity and `minDepth` pass (`src/spatial/traversal/MemoryAllocator.scala:56-65`, `src/spatial/traversal/MemoryAllocator.scala:80-88`). `MemoryResource.minDepth` defaults to zero, while Xilinx resources set primary URAM to `512`, BRAM to `32`, overflow URAM to `32`, and LUTs leaves the default (`src/spatial/targets/MemoryResource.scala:6-10`, `src/spatial/targets/xilinx/XilinxDevice.scala:13-31`). The final resource is the catch-all: all still-unassigned SRAM-capable instances and all non-SRAM duplicates are assigned `resources.last` with no capacity or depth check (`src/spatial/traversal/MemoryAllocator.scala:102-103`).

Allocated choices live in `Memory.resourceType`; `inst.resource` falls back to the target default when unset (`src/spatial/metadata/memory/BankingData.scala:180-187`). Therefore an HLS backend should record both the compiler's requested resource and whether it was a catch-all/fallback assignment. A fallback assignment is not evidence that the eventual implementation is LUTRAM, registers, BRAM, or URAM; HLS inference can choose differently or fail based on directives and access structure (unverified).

## Current Report Surfaces

`MemoryReporter` is always in the main pass sequence before final IR/codegen, while optional `ResourceReporter` and `ResourceCountReporter` run later behind `--reportArea` and `--countResources` (`src/spatial/Spatial.scala:236-250`, `src/spatial/Spatial.scala:493-499`). `MemoryReporter` writes `Memories.report`, totals estimated memory area with `areaModel.areaOf`, and for every duplicate prints resource name, buffer depth, padding, accumulator status, banks, and port/access detail (`src/spatial/report/MemoryReporter.scala:21-32`, `src/spatial/report/MemoryReporter.scala:51-63`, `src/spatial/report/MemoryReporter.scala:74-83`). This is the most direct pre-HLS memory-allocation audit trail.

The optional resource reports are coarser. `ResourceReporter` has a four-field `ResourceArea(LUT, Reg, BRAM, DSP)` and estimates SRAM-like memories through `LUTs`, `FFs`, `RAMB18`, and `RAMB32` model queries (`src/spatial/codegen/resourcegen/ResourceReporter.scala:17-20`, `src/spatial/codegen/resourcegen/ResourceReporter.scala:76-81`). `ResourceCountReporter` records bit width, dimensions, padding, and depth, but bins SRAM/FIFO/LIFO/LineBuffer/RegFile as `"bram"` and Reg/LUT-style nodes as `"reg"` (`src/spatial/codegen/resourcegen/ResourceCountReporter.scala:60-63`, `src/spatial/codegen/resourcegen/ResourceCountReporter.scala:85-103`). These reports should not replace the allocation manifest.

## Before HLS Reports

Before launching HLS, record a normalized manifest per physical memory duplicate: stable symbol/name, source location, operation type, data width, logical dimensions, padding, banking factors, bank depth, buffer depth, chosen `resource.name`, fallback flag, min-depth threshold, min-depth pass/fail, estimated primitive fields, summarized capacity field, and DSE validity fields. These fields are all recoverable from existing memory metadata and area-model paths (`src/spatial/metadata/memory/BankingData.scala:180-199`, `src/spatial/targets/AreaModel.scala:119-153`). Also record emitted HLS directives, requested binding, partition/reshape directives, and vendor pragma text as separate fields, because directive semantics are backend-specific (unverified).

## After Tool Reports

The existing Vivado template already has a two-stage reconciliation shape: `getReports.tcl` emits synth and implementation timing, flat utilization, hierarchical utilization, and detailed RAM utilization reports (`resources/synth/zcu.hw-resources/build/getReports.tcl:19-30`), and the `reports` make target runs that script (`resources/synth/zcu.hw-resources/build/Makefile:21-22`). The older DSE scraper correlates hierarchical reports back to Spatial symbols and captures `LUTs`, `FFs`, `RAMB32`, `RAMB18`, `URAM`, and `DSPs` (`resources/dse/scrape_node_area.py:30`, `resources/dse/scrape_node_area.py:142-160`, `resources/dse/scrape_node_area.py:175-186`).

For HLS, store raw tool reports plus parsed rows at each stage: HLS estimate, RTL synthesis, and place-and-route where available (unverified). Normalize vendor fields into D-04 taxonomy fields, but preserve original field names and hierarchy paths. Reconciliation should compare estimated vs reported resources per memory when identity survives, and otherwise record many-to-one, one-to-many, or unmatched mappings. If a fallback or `AUTO` memory is reported as BRAM/URAM/LUTRAM, update the reconciled result without rewriting the pre-tool allocation choice.
