---
type: "research"
decision: "D-04"
angle: 5
---

# HLS Memory Taxonomy Candidates

## Local Anchor

D-04 / Q-079 should define an HLS-facing taxonomy, but the local Spatial behavior is a useful guardrail. Spatial separates local memories from remote memories: `MemoryOps` recognizes SRAM, RegFile, LineBuffer, FIFO/LIFO/FIFOReg, Reg, and LUT as memory primitives, while DRAM plus host-facing registers/streams are remote/global memory forms (`src/spatial/metadata/memory/package.scala:333`, `src/spatial/metadata/memory/package.scala:335`, `src/spatial/metadata/memory/package.scala:339`, `src/spatial/metadata/memory/package.scala:367`, `src/spatial/metadata/memory/package.scala:389`). Local capacity is dimensional: `TensorMem.size` is the product of dimensions (`src/spatial/lang/types/Mem.scala:18`), and concrete allocators expose dimensional constructors for SRAM, RegFile, LUT, FIFO, and DRAM (`src/spatial/lang/SRAM.scala:139`, `src/spatial/lang/RegFile.scala:75`, `src/spatial/lang/LUT.scala:50`, `src/spatial/node/FIFO.scala:7`, `src/spatial/lang/DRAM.scala:40`).

## Candidate Categories

- **Registers / scalar storage.** Covers scalar `Reg`, `FIFOReg`, host `ArgIn` / `ArgOut` / `HostIO`, and HLS scalarized storage. Spatial allocates `Reg` through `RegNew` and counts `RegNew` / `FIFORegNew` as `"reg"` in the resource-count reporter (`src/spatial/lang/Reg.scala:48`, `src/spatial/codegen/resourcegen/ResourceCountReporter.scala:96`). HLS scalar promotion from tiny arrays is tool behavior and should be marked (unverified).
- **LUTRAM / distributed RAM.** Covers small local memories implemented in LUT fabric. Spatial targets include a `LUTs_RESOURCE` backed by `distributedMemoryModel`, and LUTs are also an explicit read-only local memory form (`src/spatial/targets/xilinx/XilinxDevice.scala:28`, `src/spatial/lang/LUT.scala:12`). Vitis terms such as `LUTRAM` and Intel terms such as MLAB/ALM-backed memory are (unverified).
- **BRAM.** Covers block RAM local memories. Spatial's coarse count reporter bins SRAM, FIFO, LIFO, LineBuffer, and RegFile as `"bram"` (`src/spatial/codegen/resourcegen/ResourceCountReporter.scala:86`), while the detailed reporter estimates LUTs, FFs, and BRAM for SRAM, RegFile, LineBuffer, and FIFO (`src/spatial/codegen/resourcegen/ResourceReporter.scala:76`).
- **URAM.** Covers UltraRAM-like deep on-chip storage. Spatial Xilinx-style targets expose URAM before BRAM in `memoryResources`, with a separate overflow resource used after BRAM (`src/spatial/targets/xilinx/XilinxDevice.scala:33`). URAM availability outside Xilinx/Vitis is (unverified).
- **HLS stream / FIFO.** Covers depth-bearing FIFOs and stream endpoints. Spatial FIFO depth is a first-class allocation dimension (`src/spatial/node/FIFO.scala:7`), and stream control treats FIFO, FIFOReg, StreamIn, and StreamOut as read/write streams (`src/spatial/metadata/control/package.scala:1360`, `src/spatial/metadata/control/package.scala:1377`). `StreamIn` and `StreamOut` are both local and remote in Spatial (`src/spatial/lang/StreamIn.scala:9`, `src/spatial/lang/StreamOut.scala:10`).
- **External DRAM / interface.** Covers off-chip memory and interface-only resources. Spatial DRAM is a `RemoteMem`, host DRAM carries dimensions, accel DRAM carries rank placeholders, and remote memory has no modeled area cost (`src/spatial/lang/DRAM.scala:8`, `src/spatial/node/DRAM.scala:11`, `src/spatial/node/DRAM.scala:13`, `src/spatial/targets/AreaModel.scala:167`). HLS interface names such as AXI `m_axi` or Intel memory interfaces are (unverified).

## Depth And Capacity Fields

The taxonomy should store capacity in neutral fields before mapping to vendor counts: `element_width_bits`, `logical_dims`, `logical_elements`, `bank_count`, `physical_depth_per_bank`, `buffer_depth`, `total_bits`, and optional `vendor_block_count`. Spatial's physical instance metadata already carries `banking`, `depth`, `padding`, and accumulator type, with a resource override slot (`src/spatial/metadata/memory/BankingData.scala:180`, `src/spatial/metadata/memory/BankingData.scala:186`). Its area model multiplies resource-per-bank by total banks and buffer depth (`src/spatial/targets/AreaModel.scala:145`, `src/spatial/targets/AreaModel.scala:146`, `src/spatial/targets/AreaModel.scala:151`).

Minimum-depth rules should be separate from total capacity. Spatial's base `MemoryResource.minDepth` defaults to `0`, while Xilinx-style targets set URAM min depth to `512`, BRAM to `32`, and URAM overflow to `32` (`src/spatial/targets/MemoryResource.scala:9`, `src/spatial/targets/xilinx/XilinxDevice.scala:13`, `src/spatial/targets/xilinx/XilinxDevice.scala:18`, `src/spatial/targets/xilinx/XilinxDevice.scala:23`). Spatial also has `sramThreshold = 1` as a separate "BRAM over Registers" hint (`src/spatial/SpatialConfig.scala:63`), so D-04 should not collapse scalarization threshold and BRAM/URAM minimum-depth thresholds into one field.

## Binding And Partition Forms

Vendor binding and partitioning should be modeled as modifiers, not primary categories. Spatial exposes `.par`, `.bank`, `.forcebank`, `.fullybankdim`, `.fullybanked`, `.dualportedread`, `.buffer`, `.nonbuffer`, `.hierarchical`, `.flat`, and fission controls on local SRAMs (`src/spatial/lang/SRAM.scala:21`, `src/spatial/lang/SRAM.scala:58`, `src/spatial/lang/SRAM.scala:61`, `src/spatial/lang/SRAM.scala:72`, `src/spatial/lang/SRAM.scala:83`, `src/spatial/lang/SRAM.scala:117`, `src/spatial/lang/SRAM.scala:120`, `src/spatial/lang/SRAM.scala:122`). HLS directives such as Vitis `bind_storage`, `array_partition`, `array_reshape`, or Intel-specific memory attributes are (unverified); record them as `binding_directive`, `partition_kind`, `partition_factor`, `partition_dim`, and `requested_port_model`.

## Catch-All Allocation Behavior

Spatial's allocator tries all target memory resources except the last one, assigning only when modeled area fits remaining capacity and depth meets `minDepth` (`src/spatial/traversal/MemoryAllocator.scala:56`, `src/spatial/traversal/MemoryAllocator.scala:59`, `src/spatial/traversal/MemoryAllocator.scala:85`). Any unassigned SRAM-able instance, and every non-SRAM local instance, is finally assigned to `resources.last` (`src/spatial/traversal/MemoryAllocator.scala:102`). For Xilinx-style targets that last resource is `LUTs_RESOURCE` (`src/spatial/targets/xilinx/XilinxDevice.scala:33`). Therefore the HLS taxonomy should include an explicit **fallback soft local memory** bucket with `fallback=true`, instead of silently relabeling unknowns as BRAM.
