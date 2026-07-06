---
type: hls-mapping
construct: ee109-hls-lowering-map
category: rework
date: 2026-06-25
status: draft
depends_on:
  - "[[04-ee109-hls-target-corpus]]"
  - "[[50 - EE109 MVP Blocker Matrix]]"
  - "[[55 - EE109 ABI Manifest v0]]"
  - "[[61 - EE109 Controller Primitive Lowering]]"
  - "[[62 - EE109 Memory Partitioning Lowering]]"
---

# EE109 HLS Lowering Map

This is the manager synthesis for the selected EE109 HLS MVP. The detailed evidence lives in the corpus, blocker matrix, ABI manifest, controller lowering, and memory lowering notes. This map is the compact implementation contract: if a construct appears in the selected Stage 0-4 corpus, it gets a first HLS policy here; if it is outside the selected corpus, the HLS path rejects or defers it explicitly.

## Implementation Stages

| Stage | Example | First successful artifact | New surface unlocked |
|---:|---|---|---|
| 0 | `Lab1Part1RegExample` | Scalar HLS kernel plus host oracle | `ArgIn`, `ArgOut`, `setArg`, `getArg`, `Accel`, `RegRead`, `RegWrite`, integer add |
| 1 | Lab 1 dense SRAM/DRAM path | Dense load/store kernel plus array oracle | `DRAM`, `SRAM`, dense ranges, `setMem`, `getMem`, tiled `Foreach` |
| 2 | `Lab2Part4LUT` | Scalar ABI with read-only local table | 2-D `LUT`, dynamic scalar indexing, scalar comparator |
| 3 | `Lab2Part3BasicCondFSM` | Stateful control plus exact 32-element result | `FSM`, `Reg`, conditional local writes, dense store |
| 4 | `Lab3Part1Convolution` | Matrix output checksum match | 2-D DRAM, `LineBuffer`, `RegFile`, `Pipe`, nested `Reduce`, `par`, `mux`, `abs`, partition pragmas |

## Lowering Rows

| Spatial surface | First selected example | HLS representation | Required pragmas or metadata | Unsupported in MVP |
|---|---|---|---|---|
| `@spatial`, `SpatialTest`, `runtimeArgs` | Stage 0 | Use existing staging to obtain the IR and ABI values; generated HLS path does not lower the test class itself into the kernel. | Preserve runtime argument values in the manifest and host oracle. | Non-test app shapes can be added after the selected tests compile. |
| Host `println`, `print`, `assert` | Stage 0 | Keep in the verification harness, not the HLS kernel. | Record expected scalar, array, or checksum result in `ee109_abi_manifest_v0`. | In-kernel print/assert lowering is excluded. |
| `ArgIn[Int]` | Stage 0 | HLS top-level scalar `int` parameter. | `s_axilite` control port; manifest ordinal and source value. | Non-scalar `ArgIn` forms. |
| `ArgOut[Int]` | Stage 0 | HLS top-level scalar output endpoint, initially `int *`. | `s_axilite` control port; manifest comparator. | Multiple output-channel policy beyond selected examples. |
| `setArg`, `getArg` | Stage 0 | Host harness writes scalar inputs before the call and reads scalar outputs after the call. | Manifest transfer order. | Use inside `Accel` is rejected. |
| `DRAM[Int]` | Stage 1 | HLS top-level pointer, flattened row-major for rank 2. | `m_axi` data port plus `s_axilite` pointer/control port. | Accelerator-side DRAM allocation and sparse transfers. |
| `setMem`, `getMem`, `getMatrix` | Stage 1, Stage 4 | Host harness copies dense buffers before or after the HLS call. | Shape, rank, layout, and comparator in the manifest. | File-backed or stream-backed host transfers. |
| `Accel` | Stage 0 | One selected `Accel` becomes one generated HLS top function. | ABI manifest chooses signature and interface pragmas. | `Accel(*)` and stream-backed accelerators. |
| `Foreach` | Stage 1 | Structured `for` loops in source counter order. | `UNROLL factor=P` only when static `par` lanes require it. | Non-affine bounds that cannot become HLS loops. |
| `Sequential.Foreach` | Stage 4 | Ordered non-pipelined `for` loops. | No default `PIPELINE`; nested `par` can still unroll. | `stopWhen` and starvation policies. |
| `Pipe` | Stage 4 | Ordered statement block for unit `Pipe`; pipelined loop when selected source uses `Pipe.Foreach`. | `PIPELINE II=n` only when explicitly requested or selected as safe. | Stream, MOP/POM replication, and `ParallelPipe`. |
| `Reduce` | Stage 4 | Explicit accumulator scalar plus deterministic lane combination. | `UNROLL factor=P` only after a selected static-`par` slice; current scalar reductions stay unit-lane. | Generic `Fold`, generic `MemReduce`, side-effecting map lambdas, non-integer reductions. |
| `FSM` | Stage 3 | Structured `for` or `while` with explicit state update. | Optional `LOOP_TRIPCOUNT` for known bounds. | Multiple-state and back-pressure-driven FSMs. |
| `Reg[Int]` | Stage 3 | Local scalar initialized from reset value. | Guard assignments with enables. | FIFOReg semantics. |
| `SRAM[Int]` | Stage 1 | Local C++ array with static dimensions. | Optional `ARRAY_PARTITION` from observed `par`. | Explicit `.bank`, `.forcebank`, arbitrary banking hints. |
| `LUT[Int]` | Stage 2 | `static const` or `const` local array. | Complete partition for small fully parallel stencil tables. | Writable or file-backed LUTs. |
| `RegFile[Int]` | Stage 4 | Small local array plus generated shift-register update. | Complete partition on Lab3's 3-by-3 accessed dimensions. | Large dynamic RegFiles and general banking search. |
| `LineBuffer[Int]` | Stage 4 | Local circular row buffer over `Kh` rows and `Cmax` columns. | Complete row partition; cyclic column partition by row-load `par`. | Strided and stream-backed line buffers. |
| Dense `load` and `store` | Stage 1 | Explicit copy loops between flattened DRAM pointers and local arrays. | `PIPELINE II=1` when local partitioning can satisfy ports. | Gather/scatter and upper-dimension transfer parallelism. |
| Integer arithmetic | Stage 0 | C++ signed integer expressions, initially `int32_t`/`int` for Spatial `Int`. | Preserve selected bit width in codegen metadata. | Division, modulus, arbitrary fixed point, floating point. |
| Comparisons and Boolean ops | Stage 3 | C++ boolean expressions. | Normalize `>` and `>=` as needed. | Mixed-type comparisons not normalized by staging. |
| `mux` and scalar conditionals | Stage 3, Stage 4 | C++ ternary for side-effect-free values, structured `if` otherwise. | Preserve branch order when effects exist. | `OneHotMux` and priority mux policies. |
| `abs` | Stage 4 | Signed integer ternary `(x < 0) ? -x : x`. | Use unsigned identity only when type evidence says unsigned. | Floating-point or rounding-sensitive absolute value. |
| `par` | Stage 4 | Exact selected Part6 partial-tile loops lower to controller lane unrolling plus local-array partition pragmas. Source admission may use literal row `par 2` / column `par 16` or parser-only `ROW_PAR` / `COL_PAR` aliases resolving to those values. Other `par` sites remain fail-closed. | Rule-based partitioning from the checked lane count; current proven Part6 shape remains row `2` and column `16`. | Full Spatial alpha/N/B banking search, generic schedule inference, dynamic lane counts, and DSE parameter search. |

## Blocking Decisions Already Resolved For The MVP

The Wave 1 artifacts reduce the active blocker set to five local policies:

- D-04: use `ee109_mem_kind_v0` for `Reg`, `SRAM`, `LUT`, `RegFile`, `LineBuffer`, and dense `DRAM`.
- D-05: use one HLS top function per selected `Accel`; do not reuse Chisel/Fringe globals as the HLS contract.
- D-07: use rule-based HLS partitioning from `par`, not full Spatial banking search.
- D-13: preserve observable pipe-holder state for `Reg`, `RegFile`, and `Pipe` before SSA cleanup.
- D-23: use `ee109_abi_manifest_v0` for scalar args, scalar outputs, dense DRAM pointers, and host set/get calls.

## Default Deferrals And Diagnostics

| Encountered construct | MVP diagnostic |
|---|---|
| Streams, external buses, `Accel(*)` | "Streams are outside the selected EE109 HLS subset." |
| Blackboxes, BigIP optional arithmetic | "Blackbox or BigIP lowering is deferred for the EE109 MVP." |
| Floating point, arbitrary custom fixed point, unbiased rounding, FMA policy | "Only the exact `FixPt[TRUE,_24,_8]` MemFold/GEMM canaries are supported; broader numeric policy is deferred." |
| FIFO/LIFO | "FIFO/LIFO lowering is conditional on selecting the Lab 1 FIFO example." |
| Generic `Fold` or `MemReduce` | "Only the exact Lab1 Part6 SRAM-tile fold canary and simple Lab2 all-ones MemReduce/MemFold canaries are supported; broader reduction lowering remains conditional on a selected source shape." |
| Sparse gather/scatter | "Only dense contiguous transfers are supported in the EE109 MVP." |
| Explicit banking hints | "Explicit banking hints are deferred; the MVP uses rule-derived HLS partitions only for selected shapes such as the exact scheduled Part6 canary." |
| DSE/runtime latency model | "Functional HLS generation does not depend on Spatial runtime-model parity." |

## Current Implementation Note

The 2026-07-06 MemReduce explicit-zero-init source-recognition slice does not
change this lowering map. It accepts a proven zero-initialization foreach before
the existing `MemReduceFill v0` reduction shape and preserves the same checked
payload, generated HLS, manifest, dry-run roster, and imported Vitis evidence.
Generic `MemReduce`, arbitrary reduction bodies, and new initialization
semantics remain outside the MVP lowering contract.

The 2026-07-06 Part6 row/column/K-tail par-alias proof slice also does not
change this lowering map. It pins already-supported exact `ROW_PAR=2` /
`COL_PAR=16` source aliases for the scheduled
`MatrixTileMemFoldOuterKRowColTailInPlacePart6ScheduledFixPt33x35x34`
canonical arrow-bulk canary and proves equality with the literal scheduled
source. Generated HLS, manifests, validation membership, dry-run roster, and
imported Vitis evidence remain unchanged.

The 2026-07-06 rank-2 local-compute helper-boundary cleanup does not change
this lowering map. It moves the shared partial-product/C-accumulation proof
wrapper layer into `classifier/rank2_access.rs`, while keeping MemFold syntax,
Tile-K schedule checks, and checked-payload construction in the feature
classifiers. Generated HLS, manifests, validation membership, dry-run roster,
and imported Vitis evidence remain unchanged.

The 2026-07-06 rank-2 tiled-load helper-boundary cleanup also does not change
this lowering map. It moves the shared LHS/RHS local-write/global-read
rank-2 load fact comparison into `classifier/rank2_access.rs`, while keeping
MemFold and Tile-K source syntax, loop/schedule guards, const-symbol lookup,
and checked-payload construction in the feature classifiers. Generated HLS,
manifests, validation membership, dry-run roster, and imported Vitis evidence
remain unchanged.

The 2026-07-06 `ResolvedHir` const-symbol helper cleanup also does not change
this lowering map. It moves the remaining Dense2D/Tile-K const-symbol/value
lookup wrapper from `classifier/tiled2d.rs` into `ResolvedHir`, while keeping
source syntax, role/schedule guards, checked-payload construction, and HLS
emission unchanged. Generated HLS, manifests, validation membership, dry-run
roster, and imported Vitis evidence remain unchanged.

## Next Build Cut

The next implementation cut should be Stage 0 only:

1. Identify the staged `AccelScope` for `Lab1Part1RegExample`.
2. Extract two `ArgInNew` symbols, one `ArgOutNew` symbol, two `SetReg`s, one `GetReg`, and the kernel-body `RegRead`, `FixAdd`, `RegWrite` pattern.
3. Emit the `Lab1Part1RegExample_kernel` C++ shape recorded in [[70 - Lab1Part1 Tracer Bullet]].
4. Run the host oracle with inputs `3`, `5` and expected output `8`.

Stage 1 starts only after Stage 0 is generated from IR rather than hand-written.
