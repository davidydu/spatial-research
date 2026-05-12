---
type: spec
concept: host-and-io-language-surface
source_files:
  - "src/spatial/lang/Aliases.scala:38-50"
  - "src/spatial/lang/host/Array.scala:1-231"
  - "src/spatial/lang/host/Matrix.scala:1-102"
  - "src/spatial/lang/host/Tensor3.scala:1-87"
  - "src/spatial/lang/host/Tensor4.scala:1-98"
  - "src/spatial/lang/host/Tensor5.scala:1-101"
  - "src/spatial/lang/host/CSVFile.scala:1-10"
  - "src/spatial/lang/host/BinaryFile.scala:1-9"
  - "src/spatial/lang/host/TensorData.scala:1-5"
  - "src/spatial/lang/api/TransferAPI.scala:1-88"
  - "src/spatial/lang/api/FileIOAPI.scala:1-137"
  - "src/spatial/lang/api/TensorConstructorAPI.scala:1-79"
  - "src/spatial/lang/api/ArrayAPI.scala:1-17"
source_notes:
  - "[[language-surface]]"
hls_status: rework
depends_on:
  - "[[20 - Memories]]"
  - "[[50 - Math and Helpers]]"
  - "[[90 - Aliases and Shadowing]]"
status: draft
---

# Host and IO

## Summary

Spatial exposes host-side collections as staged references, not plain Scala collections. `Tensor1[A]` is an alias for `spatial.lang.host.Array[A]`, `Tensor2[A]` is an alias for `Matrix[A]`, and `Tensor3` through `Tensor5` alias their host tensor classes (`src/spatial/lang/Aliases.scala:38-48`). `CSVFile` and `BinaryFile` are host reference shells used by the file IO API (`src/spatial/lang/Aliases.scala:49-50`, `src/spatial/lang/host/CSVFile.scala:7-9`, `src/spatial/lang/host/BinaryFile.scala:7-8`). Transfer APIs bridge host tensors to `Reg`, `Frame`, `DRAM`, and `LockDRAM` through staged nodes (`src/spatial/lang/api/TransferAPI.scala:9-88`). File APIs cover constant loading, CSV token streams, binary files, NumPy placeholders, and raw ASCII text preloads (`src/spatial/lang/api/FileIOAPI.scala:11-137`).

## Syntax or API

```scala
val a = Tensor1.tabulate(n){ i => f(i) }      // Array.scala:206-231
a.length; a(i); a(i) = data                  // Array.scala:14-21
a.foreach(f); a.map(f); a.zip(b)(f)          // Array.scala:23-48
a.reduce(f); a.fold(init)(f); a.filter(p)    // Array.scala:50-102
a.flatMap(f); a.mkString(", "); a.reshape(r,c) // Array.scala:104-130
a.toeplitz(fr,fc,ir,ic,sr,sc)                // Array.scala:150-174
a ++ b                                       // Array.scala:176-179

val m = Tensor2.tabulate(r,c){(i,j) => f(i,j)} // Matrix.scala:72-85
m(i,j); m.flatten; m.t; m.reorder(Seq(1,0))   // Matrix.scala:28-63

setArg(reg, v); getArg(reg)                  // TransferAPI.scala:9-25
setMem(dram, data); getMem(dram)             // TransferAPI.scala:37-55
loadCSV1D[T](name); writeCSV2D(m, name)      // FileIOAPI.scala:50-96
```

## Semantics

`host.Array[A]` is a `@ref` class over `scala.Array[Any]`, is mutable according to `__neverMutable = false`, and requires a `Type[A]` instance (`src/spatial/lang/host/Array.scala:9-13`). `length`, `apply`, and `update` stage `ArrayLength`, `ArrayApply`, and `ArrayUpdate` nodes (`src/spatial/lang/host/Array.scala:14-21`). `foreach`, `map`, `zip`, `reduce`, `fold`, `filter`, and `flatMap` each build bound variables and staged lambdas before staging the corresponding array node, so host collection combinators are staged computations over host arrays (`src/spatial/lang/host/Array.scala:23-58`, `src/spatial/lang/host/Array.scala:87-110`). Numeric helpers `sum`, `product`, `min`, and `max` delegate to `fold` or `reduce` with `Num[A]` operations (`src/spatial/lang/host/Array.scala:78-81`). `forall`, `exists`, and `indexOf` are derived combinators; `indexOf` is virtualized and finds the minimum nonnegative index after filtering (`src/spatial/lang/host/Array.scala:112-115`).

Array text and shape views are also staged. `mkString` stages `ArrayMkString`, and `toText` delegates to `mkString(", ")` (`src/spatial/lang/host/Array.scala:117-123`, `src/spatial/lang/host/Array.scala:187`). `reshape` validates that the product of requested dimensions equals the source length with `assertIf`, then constructs `Tensor2`, `Tensor3`, `Tensor4`, or `Tensor5` views over the same data (`src/spatial/lang/host/Array.scala:125-148`). `++` builds a new tabulated array of combined length and chooses from the left or right side with `ifThenElse` (`src/spatial/lang/host/Array.scala:176-179`). `Array.tabulate`, `fill`, `empty`, `apply`, and `fromSeq` stage `MapIndices`, `ArrayNew`, or `ArrayFromSeq` (`src/spatial/lang/host/Array.scala:206-231`). `ArrayAPI` adds flattening for nested `Tensor1[Tensor1[A]]` via `flatMap` and `charArrayToString` through `CharArrayToText` (`src/spatial/lang/api/ArrayAPI.scala:7-16`).

`toeplitz` deserves special attention because it encodes layout math. It computes `pad0 = filterdim0 - 1 - (stride0-1)` and `pad1 = filterdim1 - 1 - (stride1-1)`, then computes output rows and columns from image, filter, pad, and stride values (`src/spatial/lang/host/Array.scala:150-157`). The generated matrix data is `Tensor1.tabulate(out_rows * out_cols)`, with `i = k / out_cols`, `j = k % out_cols`, slide-row/slide-col corrections, and a `filter_base` that selects either `this(filter_i * filterdim1 + filter_j)` or `0.to[A]` (`src/spatial/lang/host/Array.scala:158-173`). The source comment still says "TODO: Incorporate stride", even though stride participates in padding and slide offsets, so the exact stride contract is tracked as Q-lang-10 (`src/spatial/lang/host/Array.scala:151-164`).

`Matrix[A]` is a `Struct[Matrix[A]]` with fields `data`, `rows`, and `cols`, and `data` is a host `Array[A]` (`src/spatial/lang/host/Matrix.scala:7-18`). `apply(i,j)` and `update(i,j,elem)` use row-major indexing `i*cols + j`, `flatten` returns `data`, `length` is `rows * cols`, and higher-order methods delegate to `data` (`src/spatial/lang/host/Matrix.scala:19-52`). `t` builds `Matrix.tabulate(cols, rows){(i,j) => apply(j,i)}`, and `reorder` creates a new two-dimensional range and remaps indices through the supplied ordering (`src/spatial/lang/host/Matrix.scala:54-63`). `Matrix.apply` constructs a `Struct`, `tabulate` maps a linear index to `(i,j)`, `fill` delegates to `tabulate`, and `fromSeq` flattens nested sequences (`src/spatial/lang/host/Matrix.scala:72-101`).

`Tensor3`, `Tensor4`, and `Tensor5` repeat the same struct pattern: each has a `data` field plus dimension fields, row-major `apply`, `flatten`, `length`, `foreach`, `map`, `zip`, `reduce`, and `reorder` (`src/spatial/lang/host/Tensor3.scala:7-60`, `src/spatial/lang/host/Tensor4.scala:7-72`, `src/spatial/lang/host/Tensor5.scala:7-73`). Their companions construct structs and tabulate linear indices into multidimensional coordinates (`src/spatial/lang/host/Tensor3.scala:63-83`, `src/spatial/lang/host/Tensor4.scala:75-97`, `src/spatial/lang/host/Tensor5.scala:76-99`). `Tensor3.update` uses `i*dim1*dim2 + j*dim1 + k`, while `Tensor3.apply` uses `i*dim1*dim2 + j*dim2 + k`; that mismatch is tracked as Q-lang-11 (`src/spatial/lang/host/Tensor3.scala:28-31`).

## Implementation

`TransferAPI` has scalar overloads for `setArg`: literals are converted with the register's `Bits[A].from`, while staged values are unboxed before `SetReg` is staged (`src/spatial/lang/api/TransferAPI.scala:9-19`). `getArg` stages `GetReg` (`src/spatial/lang/api/TransferAPI.scala:21-25`). `setFrame` and `setMem` stage `SetFrame` and `SetMem`; `getFrame` and `getMem` allocate a `Tensor1.empty` of `frame.size` or `dram.dims.prodTree`, stage the get node, and return the host array (`src/spatial/lang/api/TransferAPI.scala:27-45`). LockDRAM variants stage `SetLockMem` and `GetLockMem` in the same shape (`src/spatial/lang/api/TransferAPI.scala:47-55`). Matrix and higher-rank tensor transfers flatten on set and reconstruct tensor views with DRAM dimensions on get (`src/spatial/lang/api/TransferAPI.scala:57-86`).

`FileIOAPI.parseValue` parses `Bit`, `Fix`, `Flt`, and semicolon-separated `Struct` values recursively, reporting an error before rethrowing if parsing fails (`src/spatial/lang/api/FileIOAPI.scala:11-34`). `loadConstants` calls `loadCSVNow` immediately and wraps parsed values in `Tensor1.apply` (`src/spatial/lang/api/FileIOAPI.scala:36-39`). CSV file ops stage open/read/write/close nodes and map tokens through casts for `loadCSV1D` and `loadCSV2D`; the 2D loader reads all tokens by element delimiter, row tokens by newline delimiter, and sets columns to `all_tokens.length / row_tokens.length` (`src/spatial/lang/api/FileIOAPI.scala:41-67`). CSV writers format `Fix` and `Flt` specially when an optional format is supplied (`src/spatial/lang/api/FileIOAPI.scala:69-96`). Binary file ops stage open/read/write/close nodes, `loadNumpy1D/2D` stage placeholder nodes, and `loadDRAMWithASCIIText` opens a binary file, stages `LoadDRAMWithASCIIText`, and closes the file (`src/spatial/lang/api/FileIOAPI.scala:98-136`). `readBinary` accepts `isASCIITextFile` but does not use it in the staged call; this is tracked as Q-lang-12 (`src/spatial/lang/api/FileIOAPI.scala:98-100`).

`TensorConstructorAPI` turns `Series` tuples into tensor constructors. A one-dimensional series calls `Tensor1.tabulate(len){i => func(domain.at(i))}`, while two through five dimensions compute lengths from each series and use `Tensor2.tabulate` through `Tensor5.tabulate` (`src/spatial/lang/api/TensorConstructorAPI.scala:8-20`, `src/spatial/lang/api/TensorConstructorAPI.scala:27-68`). The two through five dimensional constructors also expose `foreach` by nesting `Series.foreach` calls and returning `void` after each user function invocation (`src/spatial/lang/api/TensorConstructorAPI.scala:22-24`, `src/spatial/lang/api/TensorConstructorAPI.scala:35-76`).

## Interactions

Host tensors are the payload type used by `TransferAPI`, `FileIOAPI`, `DebuggingAPI`, and shadowing aliases. The aliases make `Tensor1` through `Tensor5` available without shadowing, while `ShadowingAliases` separately maps `Array[A]` and `Matrix[A]` to the host collection classes in `dsl` scope (`src/spatial/lang/Aliases.scala:38-48`, `src/spatial/lang/Aliases.scala:171-174`). `TensorData(shape, data)` is a runtime companion case class with a Scala `Seq[Int]` shape and a host `Array[Any]` payload; the file contains no staged methods (`src/spatial/lang/host/TensorData.scala:1-5`).

## HLS notes

`hls_status: rework`. Host tensors and file handles are staging-time/runtime support structures, not accelerator datapath structures (`src/spatial/lang/host/Array.scala:9-21`, `src/spatial/lang/host/CSVFile.scala:7-9`). HLS should preserve transfer and file APIs at the host boundary, but tensor combinators likely lower either to C++ host code or to existing staged IR nodes rather than HLS kernels (inferred, unverified). `toeplitz`, CSV parsing, and raw ASCII DRAM preload need explicit port decisions because each embeds host-side convenience behavior in the language surface (`src/spatial/lang/host/Array.scala:150-174`, `src/spatial/lang/api/FileIOAPI.scala:11-39`, `src/spatial/lang/api/FileIOAPI.scala:129-136`).

## Open questions

- See `[[open-questions-lang-surface]]` Q-lang-10 (`toeplitz` stride contract), Q-lang-11 (`Tensor3.update` indexing mismatch), and Q-lang-12 (`readBinary` unused `isASCIITextFile` parameter).
