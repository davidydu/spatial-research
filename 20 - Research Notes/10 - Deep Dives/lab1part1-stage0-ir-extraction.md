---
type: deep-dive
topic: lab1part1-stage0-ir-extraction
status: draft
date: 2026-06-25
---

# Lab1Part1 Stage 0 IR Extraction

This note records the exact staged IR contract for generating the first EE109 HLS scalar kernel from `Lab1Part1RegExample`. It is based on the tracer-bullet note, the frontend-to-IR deep dive, the Lab source, the first useful IR log `0001_IR.log`, the final useful IR log `0090_IR.log`, and the node definitions for `ArgInNew`, `ArgOutNew`, `SetReg`, `GetReg`, `RegRead`, `RegWrite`, `FixAdd`, and `AccelScope`.

The important stability fact is that the semantic shape is unchanged from the earliest useful IR to the latest useful IR. Symbol IDs are rewritten, and late metadata is richer, but the extractor should rely on op shape, block membership, memory roles, types, and names rather than literal `x` numbers.

## Exact node pattern

The source surface is:

- `type T = Int`, which stages as `Fix[TRUE,_32,_0]`.
- `runtimeArgs = "3 5"`, `N = args(0).to[T]`, and `M = args(1).to[T]`.
- Two `ArgIn[T]` values named `argRegIn0` and `argRegIn1`.
- One `ArgOut[T]` value named `argRegOut`.
- One `Accel { ... }` body that reads both inputs, adds them, and writes the output.
- A host oracle after `Accel`: `getArg(argRegOut)`, `gold = M + N`, print, compare, assert.

Required Stage 0 graph:

| Role | Earliest useful IR, `0001_IR.log` | Latest useful IR, `0090_IR.log` | Contract |
|---|---|---|---|
| Input argument parse | `x2 = TextToFix(x1,TRUE,_32,_0)` named `N`; `x4 = TextToFix(x3,TRUE,_32,_0)` named `M` | `x71 = TextToFix(x70,TRUE,_32,_0)` named `N`; `x73 = TextToFix(x72,TRUE,_32,_0)` named `M` | Host values for harness are signed 32-bit fixed integers. The codegen may use them for the C++ test wrapper, not for the kernel body. |
| Scalar input 0 | `x5 = ArgInNew(Const(0))`, name `argRegIn0`, type `Reg[Fix[TRUE,_32,_0]]`, readers `Set(x10)`, writers `Set(x7)` | `x74 = ArgInNew(Const(0))`, name `argRegIn0`, type `Reg[Fix[TRUE,_32,_0]]`, readers `Set(x79)`, writers `Set(x76)` | One scalar HLS input port. The initializer is `Const(0)` and can be ignored for generated kernel behavior. |
| Scalar input 1 | `x6 = ArgInNew(Const(0))`, name `argRegIn1`, type `Reg[Fix[TRUE,_32,_0]]`, readers `Set(x11)`, writers `Set(x8)` | `x75 = ArgInNew(Const(0))`, name `argRegIn1`, type `Reg[Fix[TRUE,_32,_0]]`, readers `Set(x80)`, writers `Set(x77)` | Second scalar HLS input port. Preserve source order from the top-level block or use names to make the ABI deterministic. |
| Host setup | `x7 = SetReg(x5,x2)` and `x8 = SetReg(x6,x4)` | `x76 = SetReg(x74,x71)` and `x77 = SetReg(x75,x73)` | Host-side argument setup only. It must occur before `AccelScope`; it is not a kernel assignment. |
| Scalar output | `x9 = ArgOutNew(Const(0))`, name `argRegOut`, type `Reg[Fix[TRUE,_32,_0]]`, readers `Set(x15)`, writers `Set(x13)` | `x78 = ArgOutNew(Const(0))`, name `argRegOut`, type `Reg[Fix[TRUE,_32,_0]]`, readers `Set(x83)`, writers `Set(x82)` | One scalar HLS output port. Stage 0 can lower it as an output pointer or reference in generated C++. |
| Kernel boundary | `x14 = AccelScope(Block(Const(())))`, effects `unique=true, simple=true, reads={x5,x6,x9}, writes={x9}`, `ReadMems(Set(x5,x6))`, `WrittenMems(Set(x9))` | `x46 = AccelScope(Block(Const(())))`, effects `unique=true, simple=true, reads={x74,x75,x78}, writes={x78}`, `ReadMems(Set(x74,x75))`, `WrittenMems(Set(x78))` | Exactly one Stage 0 kernel boundary. Its single block is the HLS top function body. |
| Kernel read 0 | In `x14` block 0: `x10 = RegRead(x5)`, name `argRegIn0Value`, type `Fix[TRUE,_32,_0]` | In `x46` block 0: `x79 = RegRead(x74)`, type `Fix[TRUE,_32,_0]`, `ProgramOrder(0)` | Read from an `ArgInNew` register. Lower as use of the scalar input value. |
| Kernel read 1 | In `x14` block 0: `x11 = RegRead(x6)`, name `argRegIn1Value`, type `Fix[TRUE,_32,_0]` | In `x46` block 0: `x80 = RegRead(x75)`, type `Fix[TRUE,_32,_0]`, `ProgramOrder(1)` | Read from the second `ArgInNew` register. Lower as use of the scalar input value. |
| Kernel add | In `x14` block 0: `x12 = FixAdd(x10,x11)`, type `Fix[TRUE,_32,_0]` | In `x46` block 0: `x81 = FixAdd(x79,x80)`, type `Fix[TRUE,_32,_0]`, `ProgramOrder(2)` | Signed 32-bit integer addition for Stage 0. This is the only HLS arithmetic op in the kernel body. |
| Kernel write | In `x14` block 0: `x13 = RegWrite(x9,x12,Set())` | In `x46` block 0: `x82 = RegWrite(x78,x81,Set())`, `ProgramOrder(3)` | Write the sum to the `ArgOutNew` register. The enable set is empty, so the assignment is unconditional. |
| Host result read | `x15 = GetReg(x9)`, name `argRegOutResult` | `x83 = GetReg(x78)` | Host-side result retrieval after `AccelScope`; it belongs in the harness, not the generated HLS body. |
| Host oracle | `x20 = FixAdd(x4,x2)`, `x25 = FixEql(x20,x15)`, `x30 = AssertIf(Set(),x25,None)` | `x88 = FixAdd(x73,x71)`, `x93 = FixEql(x88,x83)`, `x98 = AssertIf(Set(),x93,Some(...))` | Ignore for kernel emission. It can be used to derive the sample expected result: `3 + 5 = 8`. |
| Local memory set | `LocalMemories(Set(x5, x6, x9))` | `LocalMemories(Set(x74, x75, x78))` | Stage 0 has only the three scalar ABI registers. No SRAM, DRAM, FIFO, RegFile, stream, or local array is present. |

The body block must contain the kernel statements in this dataflow:

```text
ArgInNew(argRegIn0) --RegRead--+
                               +-- FixAdd -- RegWrite --> ArgOutNew(argRegOut)
ArgInNew(argRegIn1) --RegRead--+
```

The generated Stage 0 C++ behavior is equivalent to:

```cpp
*argRegOut = argRegIn0 + argRegIn1;
```

## Stable extraction API candidates

The extractor should inspect the in-memory IR through existing Argon/Spatial structures rather than parse log text.

Recommended API surface:

| Need | In-memory API candidate |
|---|---|
| Walk the top-level program | `Block[_].stms` for top-level order; `Block[_].nestedStms` only for recursive searches. |
| Match staged operations | `sym.op` and `case Op(...)` patterns such as `case Op(ArgInNew(init))`, `case Op(AccelScope(block))`, `case Op(RegRead(reg))`, `case Op(FixAdd(a,b))`, `case Op(RegWrite(reg,data,ens))`. |
| Traverse controller body | `case Op(AccelScope(block))` exposes `block`; use `block.stms` for direct body order and `block.result` for the block result. `AccelScope` also exposes `bodies = Seq(PseudoStage(Nil -> block))` and no counters. |
| Identify scalar ABI memories | Import `spatial.metadata.memory._` and use `reg.isArgIn`, `reg.isArgOut`, `reg.isHostIO`, `reg.isReg`, `reg.readers`, and `reg.writers`. |
| Identify control and block membership | Import `spatial.metadata.control._` and use `sym.parent`, `sym.scope`, `sym.blk`, `accel.readMems`, `accel.writtenMems`, and optional `sym.progorder`. Late IR has `ProgramOrder(0..3)`, but `block.stms` already gives enough order for this example. |
| Inspect dependencies | Use `sym.inputs`, `sym.nonBlockInputs`, `sym.blocks`, and `sym.consumers`. For this pattern, `FixAdd` inputs are the two `RegRead` symbols, and `RegWrite` inputs include the output register and the sum. |
| Inspect types and names | Use `sym.tp` for `Fix[TRUE,_32,_0]` and `Reg[Fix[TRUE,_32,_0]]`; use `sym.name`, `sym.nameOr(default)`, and memory `explicitName` when present. Names are useful for stable C++ parameter spelling, while op role and top-level order are the semantic source of truth. |
| Preserve host sample values | The host setup is visible as `SetReg(argRegIn0,N)` and `SetReg(argRegIn1,M)`. The parsed `N` and `M` nodes are `TextToFix` from `InputArguments`, and the source `runtimeArgs` supplies `"3 5"` for the initial harness. |

The relevant node definitions confirm the Stage 0 assumptions:

- `ArgInNew` and `ArgOutNew` are `RegAlloc` nodes with `dims = Nil`, so Stage 0 scalar args have no address dimensions.
- `SetReg(mem,data)` and `GetReg(mem)` are addressless host transfer nodes with empty enables.
- `RegRead(mem)` is an addressless reader with empty enables, transient behavior, and a unique read effect.
- `RegWrite(mem,data,ens)` is an enqueuer-style writer; in this lab its enable set is `Set()`.
- `FixAdd(a,b)` is fixed-point addition with zero identity and associative metadata; for `Fix[TRUE,_32,_0]` Stage 0 lowers it to signed 32-bit integer addition.
- `AccelScope(block)` is a `Pipeline` with no iterators, one pseudo-stage body, no counter chains, and a simple effect that keeps the top accelerator boundary alive.

## Failure diagnostics for non-Stage-0 shapes

The Stage 0 extractor should fail before generating partial C++ when any required shape is absent or broadened. Suggested diagnostics:

| Diagnostic | Trigger |
|---|---|
| `E_STAGE0_ACCEL_COUNT` | The top-level block has zero `AccelScope` nodes or more than one `AccelScope` node. |
| `E_STAGE0_ACCEL_BODY` | The selected `AccelScope` does not have exactly one direct body block or has nested child controllers. |
| `E_STAGE0_ARGINS` | The program does not have exactly two `ArgInNew(Const(0))` scalar registers used by kernel `RegRead` nodes. |
| `E_STAGE0_ARGOUTS` | The program does not have exactly one `ArgOutNew(Const(0))` scalar register written inside the accelerator and read by one host `GetReg` after the accelerator. |
| `E_STAGE0_HOST_SETUP` | An `ArgInNew` lacks a top-level `SetReg` before the accelerator, has multiple setup writes, or the setup write is inside hardware. |
| `E_STAGE0_HOST_READBACK` | The `ArgOutNew` lacks a top-level `GetReg` after the accelerator or the readback occurs inside hardware. |
| `E_STAGE0_BODY_OPS` | The accelerator block has operations other than two `RegRead`s from ArgIns, one `FixAdd`, and one `RegWrite` to the ArgOut. |
| `E_STAGE0_DATAFLOW` | The `FixAdd` operands are not the two kernel `RegRead` symbols, or the `RegWrite` data is not the `FixAdd` result. |
| `E_STAGE0_TYPES` | Any ABI register or arithmetic value is not `Fix[TRUE,_32,_0]` or `Reg[Fix[TRUE,_32,_0]]`. |
| `E_STAGE0_MEMORY_KIND` | Any `DRAM`, `SRAM`, `RegFile`, `FIFO`, `StreamIn`, `StreamOut`, dense transfer, sparse transfer, or addressable local memory appears in the selected kernel path. |
| `E_STAGE0_ENABLES` | `RegRead`, `SetReg`, `GetReg`, or the output `RegWrite` requires non-empty enables. |
| `E_STAGE0_ORACLE_IN_KERNEL` | `PrintIf`, `FixEql`, `AssertIf`, text conversion, or host `gold` computation appears inside the `AccelScope`. |

The diagnostics should include the offending symbol, its op, and `SrcCtx` when available. They should also report whether the offending symbol is top-level host code or inside the `AccelScope`, because the same op can be acceptable in host code and unsupported in the kernel.

## Minimal metadata needed, and what can be ignored for Stage 0

Needed for Stage 0 extraction:

| Fact | Minimal source |
|---|---|
| Kernel boundary | Direct `Op(AccelScope(block))` match in the top-level `Block.stms`. |
| Kernel body order | `block.stms`, with optional cross-check against late `ProgramOrder`. |
| ABI input and output roles | `Op(ArgInNew(_))`, `Op(ArgOutNew(_))`, plus `isArgIn` and `isArgOut` helpers. |
| Dataflow | `RegRead(mem)`, `FixAdd(a,b)`, `RegWrite(mem,data,ens)`, `SetReg(mem,data)`, `GetReg(mem)`, and each symbol's inputs. |
| Types | `sym.tp` on ABI registers and arithmetic values. Stage 0 accepts only `Reg[Fix[TRUE,_32,_0]]` and `Fix[TRUE,_32,_0]`. |
| Names | `sym.name` or `sym.nameOr(default)` for `argRegIn0`, `argRegIn1`, `argRegOut`, `N`, and `M`. Use deterministic fallbacks if names are absent. |
| Host harness values | Source `runtimeArgs = "3 5"` and the `SetReg` connections from `N` and `M` to the two ArgIns. |
| Ordering across host and kernel | Top-level order in `Block.stms`, plus read/write effects as a sanity check: `SetReg` before `AccelScope`, `AccelScope` before `GetReg`. |
| Useful diagnostics | `SrcCtx`, `sym.parent`, `sym.scope`, and `sym.blk` for explaining where an unsupported symbol occurs. |

Useful but not semantically required:

- `ReadMems(Set(...))` and `WrittenMems(Set(...))` on `AccelScope`; these are good cross-checks for the two input regs and one output reg.
- `Readers` and `Writers` metadata on the ABI regs; these are good cross-checks for the SetReg, RegRead, RegWrite, and GetReg connections.
- `LocalMemories(Set(...))`; this is a convenient whole-program sanity check that the only local memories are the three ABI registers.

Ignored for Stage 0:

- Late banking and port metadata such as `Duplicates`, `BroadcastAddress`, `Dispatch`, `GroupId`, `Ports`, and `SegmentMapping`.
- Retiming and performance metadata such as `BodyLatency`, `CompilerII`, `InitiationInterval`, `FullDelay`, and tree annotations.
- Alias history such as `Aliases: 0035: ...` and `OriginalSym` when the direct graph already has the current symbols.
- C++/Chisel/PIR backend-specific lowering details, including AXI-lite spelling. Stage 0 only needs a scalar behavioral kernel plus a normal C++ harness.
- Host print and assert lowering. `PrintIf`, text conversions, `FixEql`, and `AssertIf` are test-envelope nodes after `GetReg`; they are not part of the kernel body.
- Any memory system features beyond scalar ABI registers: DRAM, SRAM, FIFO, RegFile, LUT, dense load/store, sparse load/store, streams, banking, unrolling, loops, and controller scheduling beyond the single `AccelScope`.

Stage 0 should therefore be a narrow recognizer: two scalar ArgIns, one scalar ArgOut, one `AccelScope`, two in-kernel reads, one in-kernel `FixAdd`, one unconditional in-kernel write, and host setup/readback outside the accelerator.
