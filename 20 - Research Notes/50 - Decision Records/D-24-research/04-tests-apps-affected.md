---
type: "research"
decision: "D-24"
angle: 4
topic: "tests-apps-affected"
---

# D-24 Angle 4: Tests And Apps Affected

## 1. Scalar Args Are Covered, But Not Sharp

The scalar ABI is visibly exercised, but current assertions mostly compare logical values after the same conversion path. `FixPtArgInOut` parses `-1.5`, writes an `ArgIn[FixPt[TRUE,_28,_4]]`, reads an `ArgOut`, and compares against host gold (`test/spatial/tests/feature/unit/ArgInOut.scala:64-90`). That confirms the register path, but `-1.5` is exactly representable. `HelloSpatial` also has a fractional `ArgIn[FixPt[FALSE,_16,_16]]`, but it sets `7.to[T]` and casts back to `Int`, so it is an affected smoke test, not a D-24 distinguisher (`apps/src/HelloSpatial.scala:10-17`, `apps/src/HelloSpatial.scala:53-58`, `apps/src/HelloSpatial.scala:73-78`). Better scalar candidates are `BasicBLAS`, which sends decimal `0.2` and `0.8` into `ArgIn[T]`, and `SGD_minibatch`, which sends `0.0001` into `ArgIn[FixPt[TRUE,_16,_16]]` (`test/spatial/tests/feature/dense/BasicBLAS.scala:7`, `test/spatial/tests/feature/dense/BasicBLAS.scala:221-251`; `test/spatial/tests/apps/SGD_minibatch.scala:5-8`, `test/spatial/tests/apps/SGD_minibatch.scala:17-29`, `test/spatial/tests/apps/SGD_minibatch.scala:68-82`). Their margins are wide enough to mask one- or many-LSB differences (`BasicBLAS.scala:319-328`; `SGD_minibatch.scala:14`, `:82`).

## 2. DRAM Transfer Tests Hit The Surface

`SmallTypeTransfers` is the main fixed-point transfer fixture: `T1 = FixPt[FALSE,_8,_8]`, `T2 = FixPt[FALSE,_4,_4]`, host arrays of half-step values, `setMem`, `getMem`, and fixed `ArgOut` readback (`test/spatial/tests/feature/transfers/SmallTypeTransfers.scala:5-24`, `:32-43`, `:48-69`). It exercises Cppgen's fractional DRAM rawification, but all values are `0`, `0.5`, `1.0`, or `1.5`, so double-ish and exact scaled-int conversion agree. `UniqueParallelLoad` and `ScatterMixed` use wide `FixPt[TRUE,_32,_32]` DRAM/ArgOut payloads, but the data are integer-valued (`test/spatial/tests/feature/transfers/UniqueParallelLoad.scala:9-15`, `:39-54`; `test/spatial/tests/feature/transfers/ScatterMixed.scala:8-15`, `:46-57`). `TransferStruct` is important because struct fields include `Pixel = FixPt[TRUE,_9,_23]` and `i + 0.5`, then round-trip through `setMem`/`getMatrix` (`test/spatial/tests/feature/transfers/TransferStruct.scala:9-14`, `:29-42`, `:72-91`). It should gain non-binary fractional fields and raw struct goldens.

## 3. Sub-Byte And File I/O Gaps

`TransferSubByteTypes` validates packed `Bit`, `UInt2`, and `UInt4` memory transfers with explicit gold arrays (`test/spatial/tests/feature/transfers/TransferSubByteTypes.scala:13-29`, `:45-63`). It does not cover fractional sub-byte fixed, the exact unsupported case in Cppgen (`src/spatial/codegen/cppgen/CppGenInterface.scala:95-103`, `:120-128`). `BinaryFileIO` writes and reloads `Nibble`, bytes, shorts, ints, and uints, all with `fbits == 0` (`test/spatial/tests/feature/host/BinaryFileIO.scala:5-35`, `:59-72`), while Cppgen binary fixed I/O explicitly scales fractional values on write and divides raw values on read (`src/spatial/codegen/cppgen/CppGenFileIO.scala:40-68`, `:73-86`). `CSVFileIO` covers only `Float` round-trip with epsilon (`test/spatial/tests/feature/host/CSVFileIO.scala:11-28`). CSV fixed tests should target `loadCSV1D[T]`/`writeCSV1D[T]`, because token parsing maps through `token.to[T]` and Cppgen fractional `TextToFix` uses `stod` (`src/spatial/lang/api/FileIOAPI.scala:51-66`, `:72-95`; `src/spatial/codegen/cppgen/CppGenDebug.scala:26`; `src/spatial/codegen/cppgen/CppGenCommon.scala:102-119`).

## 4. App Goldens Are Affected, But Tolerant

CSV-backed fixed apps are the broad regression canaries. `Differentiator` loads `FixPt[TRUE,_16,_16]` data and gold CSVs, transfers through DRAM, then accepts a `0.5` margin (`test/spatial/tests/feature/dense/Differentiator.scala:18-32`, `:73-84`). `MachSuite` SPMV and FFT load fixed CSV inputs/goldens and use margins of `0.2` and `0.01` (`test/spatial/tests/apps/MachSuite.scala:2031-2060`, `:2091-2101`; `test/spatial/tests/apps/MachSuite.scala:2628-2650`, `:2695-2710`). `SGD`/`SVRG` put fixed decimal config values into `ArgIn`s and DRAM, but pass/fail is threshold-based (`test/spatial/tests/apps/SGD.scala:52-61`, `:75-103`, `:179-198`; `test/spatial/tests/apps/SVRG.scala:38-48`, `:63-103`, `:219-235`). These apps should remain compatibility regressions, not primary D-24 oracles.

## 5. Missing Fixtures

Add raw goldens for scalar `setArg/getArg` with non-binary decimals, negative one-LSB values, min/max signed widths, and at least one format where raw precision exceeds `double`'s integer mantissa. Add DRAM fixtures that compare raw bytes as well as logical decimals, including signed readback and endian order. Add binary round-trips for fractional fixed and CSV fixtures with exact expected raw integers versus Cppgen `stod` results. Add fractional sub-byte rejection tests. Add struct field and `toRaw` goldens for fractional fields. Finally, make each fixture declare `conversion_policy`, because Cppgen maps fractional fixed to host `double` while raw transport is shifted integer (`src/spatial/codegen/cppgen/CppGenCommon.scala:36-49`, `:75-90`; `src/spatial/codegen/cppgen/CppGenInterface.scala:42-80`, `:85-131`).
