---
type: "research"
decision: "D-04"
angle: 4
---

# Memory eligibility and non-SRAM catch-all

## Allocator eligibility

The active allocator's specialized-resource gate is intentionally narrow. `canSRAM` returns true only for `mem.isSRAM || mem.isFIFO || mem.isLIFO`, then `LocalMemories.all.filter(!_.isCtrlBlackbox)` is partitioned into `sramAble` and `nonSRAM` before allocation begins (`src/spatial/traversal/MemoryAllocator.scala:21-37`). The predicates themselves are literal type checks: `isSRAM` matches `SRAM`, `isFIFO` matches `FIFO`, and `isLIFO` matches `LIFO` (`src/spatial/metadata/memory/package.scala:392-410`).

That means the allocator can place normal on-chip arrays, local queues, and stacks into earlier target memory resources. It does not treat `Reg`, `FIFOReg`, `RegFile`, `LineBuffer`, `LUT`, `MergeBuffer`, `StreamIn`, `StreamOut`, or `LockSRAM` as SRAM-able, even though the banking pass knows how to configure most of those memory classes (`src/spatial/traversal/MemoryAnalyzer.scala:125-138`). For an HLS taxonomy (unverified), "arrays" should mean Spatial `SRAM` when they need BRAM/URAM eligibility; HLS-like streams implemented as Spatial `FIFO` or `LIFO` are eligible, while boundary `StreamIn`/`StreamOut` are not.

## Resource and depth rules

Each `MemoryResource` has a `name`, `area(width, depth)`, `summary(area)`, and `minDepth`, which defaults to zero (`src/spatial/targets/MemoryResource.scala:6-10`). Hardware targets separately define area fields, a device `capacity`, `memoryResources`, and a `defaultResource` (`src/spatial/targets/HardwareTarget.scala:14-45`). Xilinx-style targets order resources as `URAM`, `BRAM`, `URAM_RESOURCE_OVERFLOW`, then `LUTs`; the min-depths are 512 for first-pass URAM, 32 for BRAM, and 32 for overflow URAM, while `LUTs` inherits the zero default (`src/spatial/targets/xilinx/XilinxDevice.scala:13-39`).

The allocator loops over `resources.dropRight(1)`, so the last resource is excluded from the capacity/min-depth fitting loop (`src/spatial/traversal/MemoryAllocator.scala:56-60`). For each earlier resource it estimates raw memory area, sorts candidate instances by descending raw count, and assigns only if `area <= capacity` and `memoryBankDepth >= resource.minDepth`; accepted assignments subtract from remaining capacity (`src/spatial/traversal/MemoryAllocator.scala:61-99`). Bank depth is computed from the configured `Memory` instance's banking, and raw area multiplies resources per bank by number of banks and buffer depth (`src/spatial/targets/AreaModel.scala:109-153`; `src/spatial/metadata/memory/BankingData.scala:180-199`).

## Final catch-all

The catch-all is unconditional. After all earlier resources are tried, every unassigned SRAM-able duplicate gets `resources.last`, and every duplicate of every `nonSRAM` local memory also gets `resources.last` (`src/spatial/traversal/MemoryAllocator.scala:102-103`). On Xilinx/Generic/Altera/Euresys-style targets this last resource is `LUTs`; on one-resource targets such as Plasticine or ASIC, it is simply that target's only/default SRAM resource (`src/spatial/targets/xilinx/XilinxDevice.scala:33-39`; `src/spatial/targets/plasticine/Plasticine.scala:20-26`; `src/spatial/targets/generic/ASIC.scala:14-20`).

This final assignment does not check remaining capacity, resource summary, or min-depth, because those checks only run inside the `dropRight(1)` loop. The `Memory` object stores the chosen resource as mutable `resourceType`; `resource` otherwise falls back to `spatialConfig.target.defaultResource`, and reports print `inst.resource.name` (`src/spatial/metadata/memory/BankingData.scala:180-189`; `src/spatial/report/MemoryReporter.scala:51-58`). Therefore D-04 should describe the final bucket as "last resource in target order", not as "default resource".

## Local, remote, transient, blackbox

Flow metadata has separate global sets for local and remote memories (`src/spatial/metadata/memory/LocalMemories.scala:6-17`; `src/spatial/metadata/memory/RemoteMemories.scala:6-16`). `SpatialFlowRules.memories` adds `MemAlloc` nodes that are `LocalMem` to `LocalMemories`, control blackboxes to `LocalMemories`, and remote memories or streams to `RemoteMemories` only in a later case (`src/spatial/flows/SpatialFlowRules.scala:14-18`). Since `StreamIn` and `StreamOut` extend both `LocalMem0` and `RemoteMem`, that match order represents them as local for this flow (`src/spatial/lang/StreamIn.scala:9-12`; `src/spatial/lang/StreamOut.scala:10-13`).

DRAM, LockDRAM, and Frame are `RemoteMem`; DRAM host allocations also have zero area, and remote `MemAlloc` nodes have zero area in `AreaModel` (`src/spatial/lang/DRAM.scala:8-18`; `src/spatial/lang/Frame.scala:11-27`; `src/spatial/targets/AreaModel.scala:161-175`). Transient nodes explicitly set `isTransient = true` and are zero-area (`src/spatial/node/Transient.scala:9-18`; `src/spatial/targets/AreaModel.scala:161-167`). Control blackboxes are recognized by `isCtrlBlackbox`, inserted into local memories by flow, and then excluded from allocation by the allocator filter (`src/spatial/metadata/blackbox/package.scala:19-23`; `src/spatial/traversal/MemoryAllocator.scala:35-37`).

## Implications

- HLS arrays (unverified): use `SRAM` for memories that should compete for URAM/BRAM before falling to LUTs.
- Streams: `FIFO` and `LIFO` are SRAM-able; `StreamIn`/`StreamOut` and `FIFOReg` are nonSRAM catch-all.
- Registers and host scalar IO: `Reg`, `ArgIn`, `ArgOut`, and `HostIO` are singleton/global register-like memories, not SRAM-able (`src/spatial/metadata/memory/package.scala:367-374`).
- Line buffers, LUTs, merge buffers: all are configured/banked, but they bypass specialized placement and receive the catch-all resource unless another pass overrides them (`src/spatial/traversal/MemoryAnalyzer.scala:125-138`; `src/spatial/metadata/memory/package.scala:400-427`).
- DRAM/host memories: DRAM/Frame/LockDRAM are remote capacity objects, not local SRAM-resource candidates.
