---
type: spec
concept: memories
source_files:
  - "src/spatial/lang/types/Mem.scala:1-325"
  - "src/spatial/lang/DRAM.scala:1-217"
  - "src/spatial/lang/SRAM.scala:1-300"
  - "src/spatial/lang/RegFile.scala:1-207"
  - "src/spatial/lang/Reg.scala:1-111"
  - "src/spatial/lang/FIFO.scala:1-98"
  - "src/spatial/lang/LIFO.scala:1-52"
  - "src/spatial/lang/LineBuffer.scala:1-39"
  - "src/spatial/lang/MergeBuffer.scala:1-34"
  - "src/spatial/lang/LUT.scala:1-265"
  - "src/spatial/lang/LockMem.scala:1-183"
  - "src/spatial/lang/Frame.scala:1-64"
  - "src/spatial/lang/StreamIn.scala:1-28"
  - "src/spatial/lang/StreamOut.scala:1-29"
  - "src/spatial/lang/StreamStruct.scala:1-37"
source_notes:
  - "[[language-surface]]"
hls_status: clean
depends_on:
  - "[[30 - Primitives]]"
status: draft
---

# Memories

## Summary

Spatial memories divide into **remote** (off-chip: `DRAM`, `Frame`, `LockDRAM`) and **local** (on-chip: `SRAM`, `RegFile`, `Reg`, `FIFO`, `LIFO`, `LineBuffer`, `MergeBuffer`, `LUT`, `LockSRAM`, `StreamIn`, `StreamOut`, `StreamStruct`). Every memory class is an `@ref` Scala class backed by an IR symbol and a companion `object` whose `apply` method stages the allocation node. All memories implement a shared `Mem[A, C[_]]` typeclass, which gives the transformers/codegens a uniform `__read`/`__write`/`__reset` entry point. SRAM and RegFile additionally provide ~25 tuning hints (`.buffer`, `.bank`, `.forcebank`, `.nBest`, etc.) that mutate metadata on the symbol.

## Syntax / API

```scala
// Off-chip
val x = DRAM[Int](N)                              // src/spatial/lang/DRAM.scala:42
val y = Frame[Int](64, streamIn)                  // src/spatial/lang/Frame.scala:45
val ld = LockDRAM[Int](N)                         // src/spatial/lang/LockMem.scala:44

// On-chip dense
val s = SRAM[Int](R, C)                           // src/spatial/lang/SRAM.scala:146
val r = Reg[Int](0)                               // src/spatial/lang/Reg.scala:50
val rf = RegFile[Int](R, C)                       // src/spatial/lang/RegFile.scala:93
val lut = LUT[Int](3,3)(1,2,3,4,5,6,7,8,9)        // src/spatial/lang/LUT.scala:56

// On-chip sequential
val q = FIFO[Int](128)                            // src/spatial/lang/FIFO.scala:87
val k = LIFO[Int](128)                            // src/spatial/lang/LIFO.scala:51
val lb = LineBuffer[Int](3, W)                    // src/spatial/lang/LineBuffer.scala:37
val mb = MergeBuffer[Int](4, 2)                   // src/spatial/lang/MergeBuffer.scala:28

// Host I/O
val ai = ArgIn[Int]                               // src/spatial/lang/Reg.scala:102
val ao = ArgOut[Int]                              // src/spatial/lang/Reg.scala:106
val ho = HostIO[Int]                              // src/spatial/lang/Reg.scala:110

// Stream IO
val si = StreamIn[Int](bus)                       // src/spatial/lang/StreamIn.scala:27
val so = StreamOut[Int](bus)                      // src/spatial/lang/StreamOut.scala:28
```

Read/write idioms:

```scala
s(i, j)            // SRAM2.apply → SRAMRead                    (SRAM.scala:208)
s(i, j) = data     // SRAM2.update → SRAMWrite                  (SRAM.scala:211)
r.value; r := x    // Reg.value / :=                            (Reg.scala:16-18)
q.enq(x); q.deq()  // FIFO.enq / deq                            (FIFO.scala:32,53)
k.push(x); k.pop() // LIFO push/pop                             (LIFO.scala:31,37)
rf <<= x           // RegFile1 shift-in                         (RegFile.scala:132)
s.load(dram)       // LocalMem1.load → DenseTransfer            (types/Mem.scala:55-57)
```

## Semantics

### The `Mem[A, C[_]]` typeclass hierarchy

Rooted at `types/Mem.scala:9`. `Mem[A, C[_]]` extends `Top[C[A]]` and carries a `Bits[A]` evidence plus `evMem: C[A] <:< Mem[A,C]`. Split into three branches:

- `TensorMem[A]` (`types/Mem.scala:16-33`) — shaped memories with `dims: Seq[I32]`, `size: I32`, convenience `dim0`…`dim4` accessors (fall through to 1 for lower-rank).
- `RemoteMem[A, C[_]]` (`types/Mem.scala:35-38`) — off-chip.
- `LocalMem[A, C[_]]` (`types/Mem.scala:40-49`) — on-chip, with abstract `__read(addr, ens)`, `__write(data, addr, ens)`, `__reset(ens)`.

Dimensionality is layered on top via `LocalMem0` … `LocalMem5` (`types/Mem.scala:50-122`). Each per-dim trait adds `load(dram)`/`alignload(dram)` and (only `LocalMem1`) `gather(sparseDram)` that stage `DenseTransfer`/`FrameTransmit`/`SparseTransfer` nodes.

`Mem1[A, M1[T]]` … `Mem5` (`types/Mem.scala:125-298`) provide the `apply(...)` slicing overloads that stage `MemDenseAlias`. `Mem5` has ~25 overloads for different mixes of `Idx` and `Rng` arguments (`types/Mem.scala:221-298`). `MemN` (`types/Mem.scala:300-303`) is the N-dimensional escape hatch used by `SRAMN`.

`ReadMem1` … `ReadMem5` (`types/Mem.scala:305-324`) are narrow traits that simply declare `apply(pos: I32): A` and `__read`. Used by `LUT1-5` and `SRAM1-5` for statically-known-rank read access.

### Constructors: the "compile-time const or param" invariant

`SRAM`, `RegFile`, `LUT` constructors check each dimension:

```scala
if (!length.isParam && !length.isConst)
  error(ctx, s"Only compile-time constants and DSE parameters can be used to declare on-chip memories!")
```

Source: `SRAM.scala:141,147-148,154-155,161-163,169-171`; `RegFile.scala:77-78,82-83,87-88,94-95,99-100,106-108,112-114`. LUT does not explicitly check because it only accepts `scala.Int` arguments (`LUT.scala:51-73`). This is a **staging-time invariant** relied on by banking analysis, which assumes known dimensions.

`DRAM` constructors (`DRAM.scala:42-54`) have no such check — DRAM dimensions can be any runtime `I32`.

### Concrete memory classes and stage targets

Each memory class ends in `stage(<node>)` for its allocation:

| DSL | Allocation node | Citation |
|---|---|---|
| `DRAM(...)` | `DRAMHostNew` | `DRAM.scala:42,45,48,51,54` |
| `DRAM1[A]` (accel-alloc) | `DRAMAccelNew` | `DRAM.scala:110,140,166,186,206` |
| `SRAM(...)` | `SRAMNew` | `SRAM.scala:142,149,156,164,172` |
| `Reg[A]` | `RegNew` | `Reg.scala:57` |
| `FIFOReg[A]` | `FIFORegNew` | `Reg.scala:90` |
| `ArgIn`/`ArgOut`/`HostIO` | `ArgInNew`/`ArgOutNew`/`HostIONew` | `Reg.scala:102,106,110` |
| `FIFO(depth)` | `FIFONew` | `FIFO.scala:87` |
| `LIFO(depth)` | `LIFONew` | `LIFO.scala:51` |
| `RegFile(dims)` | `RegFileNew` | `RegFile.scala:79,84,89,96,101,109,115` |
| `LUT(...)(elems*)` | `LUTNew` | `LUT.scala:52,57,62,67,72` |
| `FileLUT(...)(filename)` | `FileLUTNew` | `LUT.scala:161,166,171,176,181` |
| `LineBuffer(r,c)` | `LineBufferNew` | `LineBuffer.scala:37-38` |
| `MergeBuffer(ways,par)` | `MergeBufferNew` | `MergeBuffer.scala:29` |
| `LockDRAM(...)` | `LockDRAMHostNew` | `LockMem.scala:44` |
| `LockSRAM(...)` | `LockSRAMNew` | `LockMem.scala:141` |
| `Lock(depth)` | `LockNew` | `LockMem.scala:181` |
| `Frame(...)` | `FrameHostNew` | `Frame.scala:46,49` |
| `StreamIn(bus)` | `StreamInNew` | `StreamIn.scala:27` |
| `StreamOut(bus)` | `StreamOutNew` | `StreamOut.scala:28` |

## Implementation

### SRAM tuning hints (~25 methods)

`src/spatial/lang/SRAM.scala:54-132` is a wall of hint methods. Each mutates metadata on `this` and returns `me` (the typed self reference) so they can chain:

- **Buffering**: `.buffer` → `isWriteBuffer = true` (`SRAM.scala:58`), `.nonbuffer` → `isNonBuffer = true` (`:60`).
- **Banking style**: `.hierarchical` → `isNoFlatBank` (`:62`), `.flat` → `isNoHierarchicalBank` (`:64`), `.fullfission` → `isFullFission` (`:84`), `.nofission`/`.noduplicate` → `isNoFission` (`:94-95`), `.fullybanked` → `bank(constDims, ...)` (`:126-129`), `.fullybankdim(d)` (`:123`).
- **Banking constraints**: `.nBest` appends `NBestGuess` to `nConstraints` (`:97`), `.nRelaxed` appends `NRelaxed` (`:99`), `.alphaBest`/`.alphaRelaxed` on `alphaConstraints` (`:101-103`), `.noblockcyclic`/`.onlyblockcyclic` (`:105-107`), `.blockcyclic_Bs(bs)` (`:109`), `.effort(e)` (`:111`).
- **Explicit banking**: `.bank(N, B, alpha, P)` sets `explicitBanking` (`:118`), `.forcebank(...)` also sets `forceExplicitBanking = true` (`:120-121`).
- **Merging**: `.mustmerge` → `isMustMerge = true` (`:68`), `.coalesce` → `shouldCoalesce = true` (`:131`).
- **Duplication**: `.axesfission(opts)` sets `duplicateOnAxes` and bumps `bankingEffort` to ≥3 (`:90`).
- **Safety overrides**: `.conflictable` → `shouldIgnoreConflicts = Range(0, rank).toSet` (`:116`), `.dontTouch` → `keepUnused = true` (`:70`), `.dualportedread` → `isDualPortedRead = true` (`:72`).
- **Deprecation throws**: `.nobank`, `.nohierarchical`, `.noflat`, `.nPow2`, `.alphaPow2`, `.dualportedwrite` all `throw new Exception(...)` redirecting to renamed counterparts (`SRAM.scala:73,75-77,79-81`).

Each hint mutates a field defined in `spatial.metadata.memory._`. The DSL layer writes; later passes (banking analysis, unrolling, buffer recompute) read.

### Reg/FIFO/RegFile hint subsets

`Reg` has `.buffer`, `.nonbuffer`, `.conflictable`, `.dontTouch` (`Reg.scala:26-35`). `FIFO` has `.conflictable`, `.noduplicate` (`FIFO.scala:71-73`). `RegFile` has `.buffer`, `.nonbuffer`, `.coalesce`, `.effort`, `.dontTouch` (`RegFile.scala:60-67`). `LockSRAM` has `.buffer`, `.nonbuffer`, `.mustmerge`, `.effort`, `.conflictable` (`LockMem.scala:121-131`).

### `__read`/`__write`/`__reset` typeclass methods

Every concrete local memory implements these to route through its natural read/write node:

- `SRAM.__read` → `SRAMRead`, `__write` → `SRAMWrite`, `__reset` → `void` (`SRAM.scala:134-136`).
- `Reg.__read` → `this.value` (i.e. `RegRead`), `__write` → `RegWrite`, `__reset` → `RegReset` (`Reg.scala:41-43`).
- `FIFO.__read` → `FIFODeq`, `__write` → `FIFOEnq`, `__reset` → `void` (`FIFO.scala:76-78`).
- `LIFO.__read` → `LIFOPop`, `__write` → `LIFOPush`, `__reset` → `void` (`LIFO.scala:46-48`).
- `LUT.__read` → `read(addr, ens)` → `LUTRead`; `__write` errors `"Cannot write to LUT"` (`LUT.scala:41-46`).
- `StreamIn.__write` errors `"Cannot write to StreamIn"` (`StreamIn.scala:19-23`); `StreamOut.__read` symmetric (`StreamOut.scala:19-23`).
- `MergeBuffer.__read` → `MergeBufferDeq`, `__write` → `void` (merge buffers are write-only through `enq(way, data)`, not through the typeclass) — `MergeBuffer.scala:22-24`.
- `LineBuffer.__write` has a shape hack: if `addr.size == 1`, prepends `0.to[I32]` to make it 2-D for the `LineBufferEnq` node (`LineBuffer.scala:17`).

### Auto-set metadata on constructors

`MergeBuffer.apply` auto-sets `isWriteBuffer = true` and `isMustMerge = true` on every freshly-allocated merge buffer (`MergeBuffer.scala:30-31`). `LockSRAM.apply` chain-calls `.conflictable.mustmerge` on the new sym (`LockMem.scala:141`). These are **implicit invariants**: app writers cannot create a `MergeBuffer` without these flags set.

### LUT constant-fold vs FileLUT late-bind

`LUT.fromFile` reads the CSV **at compile time** via `loadCSVNow` (`LUT.scala:119-122,127-130,135-138,143-146,151-154`). Contrast `FileLUT.apply`: it stages `FileLUTNew(filename)` and the read happens at **codegen time** (`LUT.scala:161,166,171,176,181`). These are semantically different — `LUT.fromFile` captures the file snapshot at compile time; `FileLUT` defers loading to generated code.

### DRAM/LockDRAM/Frame comparison errors

`DRAM.eql`/`neql` emit an error and fall through to `super.neql(that)` (`DRAM.scala:29-38`). Same pattern on `LockDRAM` (`LockMem.scala:31-40`) and `Frame` (`Frame.scala:32-41`).

### `RegFileView`, `DRAMSparseTile`, `StreamStruct`

`RegFile2.apply(i, *)` / `(*, i)` return `RegFileView(regfile, addr, axis)` (`RegFile.scala:173-175,195-199`) whose `<<=` stages `RegFileShiftIn`/`RegFileShiftInVector` with the axis set (`RegFile.scala:203-206`).

`DRAM1.apply(addrs: SRAM1[Ind[W]])` etc. (`DRAM.scala:66-88`) stage `MemSparseAlias`. `DRAMSparseTile.scatter(local)` stages `SparseTransfer(isGather = false)` (`DRAM.scala:214-216`).

`StreamStruct[A]` (`StreamStruct.scala:12-29`) is a struct whose field reads are stream dequeues. `field(name)` stages `FieldDeq`, `field_update` stages `FieldEnq` (`StreamStruct.scala:35-36`).

## Interactions

- **`spatial.node.*`**: every `stage(...)` call here names a node from that package.
- **`spatial.metadata.memory.*`**: ~30 metadata fields mutated by the hint methods; fields are defined in that package.
- **Pass pipeline**: `bankingAnalysis` reads every banking hint; `memoryDealiasing` resolves `MemDenseAlias`/`MemSparseAlias`; `bufferRecompute` reads `isWriteBuffer`/`isNonBuffer`; `accumTransformer` reads accumulator patterns.
- **Codegens**: each backend has a per-memory emitter (chiselgen SRAMs, FIFOs, etc.).

## HLS notes

`hls_status: clean`. `SRAM` → `#pragma HLS ARRAY_PARTITION`/`bind_storage`; `Reg` → scalar; `FIFO` → `hls::stream`; `RegFile` → array with `#pragma HLS BIND_STORAGE type=RAM_1WnR`; `LUT` → `const` array; `LockSRAM`/`LockDRAM` → shared memory + arbitration; `StreamIn`/`StreamOut` → `#pragma HLS INTERFACE axis`. Spatial's `N, B, alpha, P` banking scheme is richer than HLS's factor+dim; the Rust rewrite should collapse the 25-method tuning chain into a per-memory config struct.

## Open questions

- See `[[20 - Open Questions]]` Q-013 (hint precedence — what wins if you set both `.fullfission` and `.bank(...)`?), Q-014 (DRAM.scala also tries `super.neql(that)` after erroring; what's the intended evaluation order?).
