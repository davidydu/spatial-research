---
type: "research"
decision: "D-04"
angle: 10
---

# Cost/Risk Recommendation Matrix

## Baseline Constraints

Spatial already has a useful allocator contract, but not a portable HLS policy. `MemoryResource` names a storage resource, computes area, summarizes area into a scalar count, and supplies `minDepth` with a default of `0` (`src/spatial/targets/MemoryResource.scala:6-10`). `HardwareTarget` makes resource capacity target-local through `AFIELDS`, `capacity`, `memoryResources`, and `defaultResource` (`src/spatial/targets/HardwareTarget.scala:14`, `src/spatial/targets/HardwareTarget.scala:29-30`, `src/spatial/targets/HardwareTarget.scala:44-45`). Current Xilinx-like targets order memory resources as `URAM_RESOURCE`, `BRAM_RESOURCE`, `URAM_RESOURCE_OVERFLOW`, then `LUTs_RESOURCE`, with BRAM as the metadata default (`src/spatial/targets/xilinx/XilinxDevice.scala:33-39`).

The critical behavioral constraint is catch-all allocation. `MemoryAllocator` copies `target.capacity`, iterates `target.memoryResources.dropRight(1)`, and only assigns a named resource when both capacity and `minDepth` pass (`src/spatial/traversal/MemoryAllocator.scala:46`, `src/spatial/traversal/MemoryAllocator.scala:56-60`, `src/spatial/traversal/MemoryAllocator.scala:85-88`). Anything still unassigned, plus every non-SRAM-able local memory, is assigned to `resources.last` with no further capacity or depth check (`src/spatial/traversal/MemoryAllocator.scala:102-103`). Therefore D-04 must decide what the HLS final resource means, not merely what the first resources are.

## Decision Matrix

| Option | Implementation cost | Main risk | Recommendation |
|---|---:|---|---|
| Reuse current `URAM -> BRAM -> URAM overflow -> LUT` order | Low | Bakes in Xilinx-specific primitive assumptions: URAM depth `512`, BRAM depth `32`, overflow URAM depth `32`, and distributed LUT area models (`src/spatial/targets/xilinx/XilinxDevice.scala:13-31`, `src/spatial/targets/xilinx/XilinxDevice.scala:79-83`). Also makes LUTRAM the silent catch-all. | Do not use as the HLS policy. Reuse only as the default threshold seed. |
| Define HLS-specific `StorageClass` enum | Medium | Can create a second taxonomy if it bypasses `MemoryResource` and `Memory.resource`, which currently stores allocation metadata and falls back to the target default (`src/spatial/metadata/memory/BankingData.scala:186-187`). | Yes, but make it an HLS-facing enum that maps into `MemoryResource` objects. |
| Report-only allocation | Low | Keeps compilation moving, but weakens early capacity/DSE feedback. DSE already treats `area <= capacity` as validity and reports capacity-backed fields (`src/spatial/dse/DSEThread.scala:119-123`). | Not sufficient alone; useful for the final `AUTO` bucket and migration diagnostics. |
| Tool-driven allocation | Medium-high | Requires parsing synthesis/HLS reports after code generation; pragma support, report names, and inferred storage classes vary by vendor and tool version (unverified). | Use as post-build validation, not as the v1 compiler-side allocation source of truth. |
| Strict capacity rejection | Medium | Aligns with current DSE validity, but HLS estimates before synthesis will be approximate and missing capacity fields would produce false failures (unverified). | Defer strict rejection except for explicit hard bindings on known-capacity targets. |
| Hybrid | Medium | Needs a small adapter layer and clearer diagnostics. | Recommended v1. Preserve Spatial's ordered allocator, add HLS-specific resource names, and make the final fallback explicit. |

## Recommended V1 Policy

Adopt a hybrid policy: define an HLS `StorageClass` enum for user-facing and backend-facing intent, but lower it to `MemoryResource` objects so existing metadata, reports, and allocator behavior stay intact. The v1 local-memory classes should be `URAM`, `BRAM`, `LUTRAM`, `REG`, and `AUTO`; only capacity-accounted banked resources should appear before the final catch-all. Start with ordered resources `URAM(minDepth=512)`, `BRAM(minDepth=32)`, optional `URAM_OVERFLOW(minDepth=32)`, optional `LUTRAM(minDepth=0)`, and final `AUTO(minDepth=0)`. The min-depth values are inherited from current Spatial behavior where they exist, while HLS-specific scalar promotion and pragma inference remain tool behavior (unverified).

Capacity fields should match the names consumed by non-final resources, because the allocator wraps each candidate count as `Area(resource.name -> count)` before comparing against remaining capacity (`src/spatial/traversal/MemoryAllocator.scala:62-88`). For v1, use aggregate fields such as `URAM`, `BRAM`, `LUTRAM`, `Regs`, and `DSPs` when the HLS target can provide them; do not expose vendor primitive subfields unless a `summary` function reduces them into the allocation key. This mirrors current BRAM accounting, where `BRAM_RESOURCE.summary` reduces `RAM18` and `RAM36` into a BRAM count (`src/spatial/targets/xilinx/XilinxDevice.scala:18-21`).

The final catch-all should be `AUTO`, not `LUTRAM`. `AUTO` means "emit no hard storage binding and let the HLS tool infer or fail" (unverified). It should be reportable, warnable, and excluded from compile-time capacity rejection. This preserves the existing unconditional final assignment behavior while avoiding the false claim that every leftover memory is distributed RAM.

## Follow-Up Tasks

1. Add an HLS storage-class adapter: `StorageClass -> MemoryResource`, with `AUTO` required to be last.
2. Add HLS target capacity schemas and report import for `URAM`, `BRAM`, `LUTRAM`, `Regs`, and `DSPs`; keep unknown fields report-only until validated.
3. Add diagnostics for memories assigned to `AUTO`, resources skipped by `minDepth`, and resources skipped by capacity.
4. Add allocator tests covering `dropRight(1)`, hard min-depth gates, capacity decrement, and final `AUTO` assignment.
