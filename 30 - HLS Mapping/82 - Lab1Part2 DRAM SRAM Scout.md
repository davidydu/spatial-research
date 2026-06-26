---
type: hls-mapping
construct: lab1part2-dram-sram-scout
category: rework
status: draft
date: 2026-06-25
stage: 1C
depends_on:
  - "[[80 - Stage1 EE109 HLS Expansion Plan]]"
  - "[[55 - EE109 ABI Manifest v0]]"
  - "[[61 - EE109 Controller Primitive Lowering]]"
  - "[[62 - EE109 Memory Partitioning Lowering]]"
---

# Lab1Part2 DRAM SRAM Scout

## Purpose

This is the Stage 1C scout for the EE109 Lab1Part2 example. It records the exact selected source shape, what the packaged CS217 Spatial flow emits, and the next local HLS implementation boundary.

The key result is: Lab1Part2 is the natural next implementation target, but it is too large to turn on as a single monolithic HLS feature. The next patch should add a local Lab1Part2-like HLS fixture and a fail-closed diagnostic first, then implement the smallest dense DRAM/SRAM path behind that test.

## Source And Run Caveats

Source checkout:

- `/Users/david/Documents/David_code/lab-1-accelerator-bandits-1/src/test/scala/Lab1.scala:67-147`

The lab checkout is not wired to the local Spatial repo. Its `build.sbt` depends on the published CS217 package:

- `/Users/david/Documents/David_code/lab-1-accelerator-bandits-1/build.sbt:14-17`
- dependency: `"edu.stanford.cs.dawn" %% "spatial" % "1.1-cs217"`

Command run:

```bash
SBT_OPTS='-Xmx8G -XX:+UseG1GC' sbt -Dtest.CS217=true '; testOnly Lab1Part2DramSramExample'
```

Result:

- sbt compiled and ran one test successfully.
- The Scala simulation printed the expected vector `[0, 3, 6, ..., 93]` and `PASS: true` in stdout.
- The generated `logs/CS217/Lab1Part2DramSramExample/make.log` says `"Skipping Make"`.
- The generated `logs/CS217/Lab1Part2DramSramExample/run.log` says `"Skipping Run" 3`.

Interpretation: this is valid reconnaissance for source and IR shape, not proof that our local `--hls` backend or any vendor HLS flow accepts Lab1Part2.

## Selected Source Shape

From `Lab1.scala:67-147`:

- `N = 32`, `tileSize = 16`, `type T = Int`.
- Runtime args: `"3"`.
- Host source array: `Array.tabulate[Int](N) { i => i % 256 }`.
- Host input memory: `srcFPGA = DRAM[T](N)`, populated by `setMem(srcFPGA, srcHost)`.
- Host scalar input: `x = ArgIn[T]`, populated by `setArg(x, value)`.
- Accelerator body:
  - `Sequential.Foreach(N by tileSize) { i => ... }`
  - `b1 = SRAM[T](tileSize)`
  - `b1 load srcFPGA(i::i+tileSize)`
  - `b2 = SRAM[T](tileSize)`
  - `Foreach(tileSize by 1) { ii => b2(ii) = b1(ii) * x }`
  - `dstFPGA(i::i+tileSize) store b2`
- Host output memory: `getMem(dstFPGA)`.
- Oracle: `src.map { _ * value }`, so with runtime `3` the expected output is `[0, 3, 6, ..., 93]`.

## Final IR Shape

The final CS217 IR log is:

- `/Users/david/Documents/David_code/lab-1-accelerator-bandits-1/logs/CS217/Lab1Part2DramSramExample/0086_IR.log`

Relevant nodes:

| Surface | Evidence |
|---|---|
| Source DRAM | `DRAMHostNew(List(Const(32)),Const(0))` at `0086_IR.log:60` |
| Destination DRAM | `DRAMHostNew(List(Const(32)),Const(0))` at `0086_IR.log:71` |
| Host source transfer | `SetMem(x215,x214)` at `0086_IR.log:82` |
| Scalar input | `ArgInNew(Const(0))` and `SetReg(x218,x212)` at `0086_IR.log:90,104` |
| Accelerator scope | `AccelScope(Block(Const(())))` at `0086_IR.log:116` |
| Outer tile loop | `UnrolledForeach(... x221 ...)` at `0086_IR.log:164` |
| Input tile SRAM | `SRAMNew(List(Const(16)),SRAM1[Fix[TRUE,_32,_0]])` at `0086_IR.log:206` |
| Dense load marker | `LoweredTransfer(DenseLoad)` and size `(Const(16),Const(1),32)` at `0086_IR.log:241-242` |
| Dense load primitive | `FringeDenseLoad(x215,x225,x226)` at `0086_IR.log:448` |
| Load writeback loop | `UnrolledForeach(... x237 ...)` and `SRAMBankedWrite(x224,...)` at `0086_IR.log:490,607` |
| Output tile SRAM | `SRAMNew(List(Const(16)),SRAM1[Fix[TRUE,_32,_0]])` at `0086_IR.log:629` |
| Inner compute loop | `UnrolledForeach(Set(b223),x247,...)` at `0086_IR.log:678` |
| SRAM read | `SRAMBankedRead(x224,...)` at `0086_IR.log:723` |
| Multiply | `FixMul(x251,x316)` at `0086_IR.log:789` |
| SRAM write | `SRAMBankedWrite(x245,...)` at `0086_IR.log:844` |
| Dense store marker | `LoweredTransfer(DenseStore)` and size `(Const(16),Const(1),32)` at `0086_IR.log:879-880` |
| Store readback loop | `UnrolledForeach(... x268 ...)` and `SRAMBankedRead(x245,...)` at `0086_IR.log:1130,1175` |
| Dense store primitive | `FringeDenseStore(x216,x256,x257,x258)` at `0086_IR.log:1259` |
| Host output transfer | `GetMem(x216,x282)` at `0086_IR.log:1338` |

## Local HLS Backend Gap

The current local `HLSGen` is deliberately still Stage 0 plus constant LUT:

- It validates one `AccelScope`, at least one scalar `ArgIn`, exactly one scalar `ArgOut`, and exactly one kernel `RegWrite` (`HLSGen.scala:146-171`).
- It emits only scalar `s_axilite` ports plus optional static constant LUT arrays (`HLSGen.scala:180-199`).
- Its accepted kernel nodes are scalar `ArgIn`, `ArgOut`, host `SetReg`/`GetReg`, `AccelScope`, `RegRead`, constant `LUTNew`, supported `LUTBankedRead`, `VecApply(..., 0)`, `FixAdd`, and scalar `RegWrite` (`HLSGen.scala:273-349`).
- Everything else inside the kernel is rejected as `unsupported kernel node ...` (`HLSGen.scala:345-346`).

Therefore Lab1Part2 currently requires new local support for:

- Host DRAM ABI: pointer ports, host allocation/test harness buffers, `setMem`, and `getMem`.
- Dense DRAM transfer lowering: enough of `FringeDenseLoad`/`FringeDenseStore` or pre-transfer IR to lower the selected `i::i+tileSize` ranges.
- Local SRAM arrays: fixed-size `SRAM1[Int](16)` allocation, reads, and writes.
- Counted controllers: outer sequential tile loop and inner one-dimensional foreach.
- Integer multiply: `FixMul` for `Int`.
- Independent vector oracle in the HLS harness. The scalar/LUT harness currently computes expected values from the same lowered expression tree, which is acceptable for tracer bullets but weak for memory lowering.

## Proposed Next Slice

Add a local fixture in the Spatial repo before implementing the memory lowering:

- `spatial.tests.ee109.Lab1Part2DramSramExample` or a clearly named `Lab1Part2DramSramMiniExample`.
- Keep `N = 32`, `tileSize = 16`, runtime arg `3`, and oracle `[0, 3, 6, ..., 93]`.
- Run it under `-Dtest.HLS=true` and record the current fail-closed diagnostic.
- Add a negative regression that proves unsupported memory/control nodes do not accidentally emit partial HLS files.

Then implement the narrow lowering in this order:

1. Extend the HLS scanner to collect `DRAMHostNew`, `SetMem`, `GetMem`, `SRAMNew`, `SRAMBankedRead`, `SRAMBankedWrite`, `CounterNew`, `CounterChainNew`, and selected `UnrolledForeach`.
2. Generate a C++ kernel with two pointer ports and one scalar arg:

```cpp
extern "C" void Lab1Part2DramSramExample_kernel(const int *srcFPGA, int *dstFPGA, int x) {
  for (int i = 0; i < 32; i += 16) {
    int b1[16];
    int b2[16];
    for (int ii = 0; ii < 16; ++ii) b1[ii] = srcFPGA[i + ii];
    for (int ii = 0; ii < 16; ++ii) b2[ii] = b1[ii] * x;
    for (int ii = 0; ii < 16; ++ii) dstFPGA[i + ii] = b2[ii];
  }
}
```

3. Generate a host-C++ harness with an independent vector oracle.
4. Keep all non-selected DRAM ranks, dynamic sizes, sparse aliases, FIFO streams, non-unit strides, non-`Int` element types, and overlapping source/destination shapes rejected.

## Documentation Policy

Do not spend time maintaining the public documentation site yet. Keep the Obsidian research vault current because it is the active manager memory for the implementation. Once Lab1Part2 produces host-compiled HLS C++ locally, update public/site docs with a concise status table and the explicit caveat that vendor HLS synthesis is still not covered unless a Vitis/Vivado gate has been added.
