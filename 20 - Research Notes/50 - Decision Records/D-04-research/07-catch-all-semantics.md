---
type: "research"
decision: "D-04"
angle: 7
---

# Catch-All Semantics And Alternatives

## Current Catch-All Contract

Spatial's current allocator is explicit but caveated: `process` prints `TODO: un-gut memory allocator`, calls `allocate()`, and returns the block unchanged (`src/spatial/traversal/MemoryAllocator.scala:15-18`). Within that current behavior, the final resource in `target.memoryResources` is not a normal resource. The allocator binds `resources = target.memoryResources`, iterates only `resources.dropRight(1)`, and then assigns all remaining local memory instances to `resources.last` (`src/spatial/traversal/MemoryAllocator.scala:56-59`, `src/spatial/traversal/MemoryAllocator.scala:102-103`).

That means the final list element is a structural catch-all. It does not run the resource's area model, does not compare against remaining capacity, and does not check `minDepth`. The checked resources require both `area <= capacity` and `depth >= resource.minDepth`; skipped memories stay unassigned for later resource passes (`src/spatial/traversal/MemoryAllocator.scala:83-99`). The catch-all assignment bypasses that entire path (`src/spatial/traversal/MemoryAllocator.scala:102-103`).

## Default Resource Is Different

`defaultResource` is not the same as the final catch-all. The target contract exposes both `memoryResources` and `defaultResource` (`src/spatial/targets/HardwareTarget.scala:44-45`). Each banked `Memory` has an optional `resourceType`; `resource` reads `resourceType.getOrElse(spatialConfig.target.defaultResource)` (`src/spatial/metadata/memory/BankingData.scala:180-188`). So `defaultResource` is a metadata fallback for "not yet assigned" or stripped metadata, while `resources.last` is the allocation result for anything the allocator could not place earlier.

On Xilinx-style targets, the list is `URAM_RESOURCE`, `BRAM_RESOURCE`, `URAM_RESOURCE_OVERFLOW`, and `LUTs_RESOURCE`, while `defaultResource` is `BRAM_RESOURCE` (`src/spatial/targets/xilinx/XilinxDevice.scala:33-39`). Thus an allocated leftover becomes "LUTs", not BRAM. On ASIC and Plasticine, the list contains only `SRAM_RESOURCE`, so `dropRight(1)` is empty and the catch-all assigns everything to SRAM (`src/spatial/targets/generic/ASIC.scala:14-20`, `src/spatial/targets/plasticine/Plasticine.scala:20-26`).

## Exhaustion Behavior

For non-final resources, capacity exhaustion is soft. If every candidate is larger than remaining capacity, the allocator skips that resource; individual too-large memories are also skipped (`src/spatial/traversal/MemoryAllocator.scala:70-76`, `src/spatial/traversal/MemoryAllocator.scala:91-95`). The loop itself only runs while `capacity(resource.name) > 0` (`src/spatial/traversal/MemoryAllocator.scala:80`). Exhausted URAM or BRAM therefore does not fail allocation; it just pushes leftovers toward later resources, and ultimately into the unchecked final bucket.

This is not a final whole-design rejection. DSE separately marks a design point valid only when evaluated `area <= capacity` and there are no state errors (`src/spatial/dse/DSEThread.scala:119-123`), but the allocator pass itself emits no error or warning on final catch-all use. Memory reporting will print the chosen resource name for each instance (`src/spatial/report/MemoryReporter.scala:51-58`), which makes the fallback observable after the fact, not preventative.

## HLS Alternatives

The exact Spatial parity option is an unchecked LUT/register fallback: put finite hard memories first and make the last HLS resource an unbounded local fabric bucket. This matches `resources.last`, but it is dangerous for HLS because array binding, scalarization, and fabric-memory inference are vendor heuristics (unverified). It can hide a hard resource miss until synthesis or timing failure.

A warning-only fallback is slightly better but still weak: it preserves compilation, yet lets final artifacts depend on implicit HLS inference (unverified). A hard reject is cleaner for reproducibility: if a memory cannot fit any capacity-tested resource, final synthesis should fail with the instance, requested resource path, modeled demand, and remaining capacity. Automatic spill to DRAM should not be the default, because Spatial's allocator only re-labels local resources and never changes a local memory into remote memory (`src/spatial/traversal/MemoryAllocator.scala:35-40`, `src/spatial/traversal/MemoryAllocator.scala:102-103`); spill would change latency, banking, interface, and data-movement semantics (unverified).

The best compromise is mode-specific behavior. Exploration/DSE can allow the fallback long enough to score or mark the design invalid, matching the existing DSE validity gate (`src/spatial/dse/DSEThread.scala:119-123`). Final HLS synthesis should reject over-budget fallback unless the target declares the catch-all explicitly unbounded, as ASIC and Plasticine effectively do with single-resource SRAM targets (`src/spatial/targets/generic/ASIC.scala:19-28`, `src/spatial/targets/plasticine/Plasticine.scala:15-26`).

## Recommendation

D-04 should not define the final element as "whatever HLS chooses" by default. Define a named catch-all class, for example `hls_auto_local`, with `fallback=true`, `capacity_policy`, and `diagnostic_level`. For simulation or abstract targets, `capacity_policy = unbounded` is acceptable. For final FPGA HLS, use `capacity_policy = checked` or `reject`: LUTRAM and register-backed storage should have real `LUT`/`Reg` capacity fields, and any overflow beyond those fields should be a compile-time error, not an implicit spill.

Keep `defaultResource` as a pre-allocation metadata fallback only. The allocator's final resource should be explicit in reports, counted when possible, and treated as an error boundary for final HLS builds. That preserves Spatial's useful "last resource catches leftovers" shape while avoiding the current unchecked behavior where capacity exhaustion silently becomes LUTs.
