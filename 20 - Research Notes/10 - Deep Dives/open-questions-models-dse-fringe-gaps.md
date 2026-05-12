---
type: open-questions
topic: models-dse-fringe-gaps
session: 2026-04-24
date_started: 2026-04-24
---

# Open Questions - Models DSE Fringe Gaps

## Q-mdf-01 - 2026-04-24 HLS memory-resource taxonomy and catch-all order

Spatial's allocator treats `target.memoryResources` as an ordered priority list and assigns all unclaimed memories to the final list element. Need define the HLS resource list, minimum-depth rules, capacity fields, and catch-all behavior before porting allocation.

Source: src/spatial/targets/MemoryResource.scala:6-10; src/spatial/targets/HardwareTarget.scala:44-45; src/spatial/traversal/MemoryAllocator.scala:56-103
Blocked by: HLS resource-report schema
Status: open
Resolution:

## Q-mdf-02 - 2026-04-24 GenericDevice SRAM resource is defined but unselected

`GenericDevice` defines `SRAM_RESOURCE`, but its `memoryResources` list uses URAM, BRAM, URAM overflow, and LUTs, with BRAM as the default. Need decide whether this is dead compatibility code or a missed generic-target path before using Generic as an HLS template.

Source: src/spatial/targets/generic/GenericDevice.scala:13-44
Blocked by: generic-target audit
Status: open
Resolution:

## Q-mdf-03 - 2026-04-24 HLS CSV field schema and report mapping

The CSV loader framework transfers, but HLS needs a field schema that maps model outputs to HLS resources and schedule data. Need define area fields, latency fields, and target-specific CSV file names for the HLS backend.

Source: src/spatial/targets/SpatialModel.scala:74-103; src/spatial/targets/AreaModel.scala:18-23; src/spatial/targets/LatencyModel.scala:10-16; src/spatial/targets/HardwareTarget.scala:14-26
Blocked by: HLS report parser design
Status: open
Resolution:

## Q-mdf-04 - 2026-04-24 CSV loader strictness for extra and missing fields

`SpatialModel.loadModels` warns when expected target fields are missing from a CSV, but silently ignores CSV headings not included in `FIELDS`. Need decide whether the HLS loader should preserve this permissive behavior or fail fast on field-schema mismatches.

Source: src/spatial/targets/SpatialModel.scala:86-103
Blocked by: HLS model validation policy
Status: open
Resolution:

## Q-mdf-05 - 2026-04-24 HLS replacement for Chisel instantiation globals

The current instantiation path uses generated Scala, `SpatialIP`, `CommonMain`, and mutable Fringe globals to thread target selection, scalar counts, stream info, allocator count, retiming, and channel assignment. Need design the Rust/HLS equivalent without relying on Chisel elaboration-time mutation.

Source: src/spatial/codegen/chiselgen/ChiselCodegen.scala:129-302; src/spatial/codegen/chiselgen/ChiselGenInterface.scala:121-152; src/spatial/codegen/chiselgen/ChiselGenController.scala:550-581; fringe/src/fringe/SpatialIP.scala:18-40; fringe/src/fringe/globals.scala:7-79
Blocked by: HLS top-level generation design
Status: open
Resolution:

## Q-mdf-06 - 2026-04-24 ArgInterface versus ArgAPI scalar-layout ownership

The requested generated-file list names `ArgInterface.scala`, but source code opens only an empty `object Args` there while `ArgAPI.scala`, Fringe, RegFile, and target AXI4-Lite bridges carry the scalar-layout behavior. Need decide how the spec should name this boundary for the HLS port.

Source: src/spatial/codegen/chiselgen/ChiselCodegen.scala:175-191; src/spatial/codegen/chiselgen/ChiselCodegen.scala:283-285; src/spatial/codegen/chiselgen/ChiselGenInterface.scala:156-187; fringe/src/fringe/Fringe.scala:36-57; fringe/src/fringe/Fringe.scala:112-117; fringe/src/fringe/templates/axi4/AXI4LiteToRFBridge.scala:23-47
Blocked by: HLS host-argument ABI design
Status: open
Resolution:
