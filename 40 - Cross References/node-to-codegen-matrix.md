---
type: moc
project: spatial-spec
date_started: 2026-04-23
---

# Node → Codegen Emission Matrix

Per-IR-node summary of how each backend emits it. Draft populated from Phase 1 coverage notes; refined during Phase 2 as deep-dives land.

## Controllers

| Node | Chiselgen | Scalagen | Cppgen/Tsthgen (host) | Pirgen | Rogue |
|---|---|---|---|---|---|
| `AccelScope` | `writeKernelClass` emits `AccelUnit.scala`/`AccelWrapper.scala`; wires Fringe I/O | `object Main { def main() { accel_scope_body } }` | host `c1->setNumArgIns/Outs/run()` | PIR `AccelMain extends PIRApp` | `accel.Enable.set(1); while (done==0)` |
| `UnitPipe` | Inner controller module `sm_<sym>.scala` | Inlined kernel `object X_kernel { def run } ` | — (host doesn't emit accel body) | `UnitController` | traversal only (instrumentation counters) |
| `ParallelPipe` | `ParallelPipe` RTL template | emits children in parallel (semantic parallel) | — | `UnitController` + child lanes | — |
| `OpForeach` → `UnrolledForeach` | `UnrolledForeach` RTL with counter chain + datapathEn | `for (i <- ctr) { kernel.run(...) }` | — | `LoopController` + `CounterIter`/`CounterValid` | — |
| `OpReduce` → `UnrolledReduce` | similar + reduction tree | similar with accumulator register | — | `LoopController` with accumulation | — |
| `OpMemReduce` | specialized nested + accumulator writes to SRAM | nested map/acc loops | — | `LoopController` with nested map+reduce | — |
| `StateMachine` | `FSMControl` module, state/nextState regs | `while (notDone(state)) { action(state); state = next(state) }` | — | TODO stub (unsupported) | — |
| `Switch` / `SwitchCase` | `SwitchControl` mux | `(cond1) match { case ... }` | — | `Switch` / `SwitchCase` PIR | — |

## Memories

| Node | Chiselgen | Scalagen | Cppgen/Tsthgen | Pirgen | Rogue |
|---|---|---|---|---|---|
| `SRAMNew` | `BankedSRAM` with `MemParams(Bs, Ns, alphas, Ps)` | `BankedMemory(nBanks × bankDepth)` | — | `SRAM().bank(…).offset(…)` | — |
| `RegNew` / `ArgInNew` / `ArgOutNew` / `HostIONew` | host reg in RegFile slot; accel `FF` + optimized accumulator bundles | `emul.Ptr[A]`; RegAccumOp dispatched to AccumAdd/Mul/Min/Max/FMA | host reg marshalling via `c1->setArg`/`getArg` | `Reg()` / `argIn` / `argOut` / `hostIO` | Python assignment + `setArg`/`getArg` |
| `FIFONew` | `FIFO` template + `FIFOWidthConvert` | `scala.collection.mutable.Queue` | — | `FIFO().depth(size)`; isEmpty/isFull/numel **error out** | — |
| `LIFONew` | `LIFO` template | `scala.collection.mutable.Stack` | — | `LIFO()` + BankedPop/Push only | — |
| `RegFileNew` | `ShiftRegFile` | `emul.ShiftableMemory` (scalar) / flat Array (vector) | — | `RegFile()` + BankedRead/Write Const(0) offset | — |
| `LineBufferNew` | `LineBuffer` template | `emul.LineBuffer` circular row buffer | — | **error**: "Plasticine doesn't support LineBuffer" | — |
| `LUTNew` / `FileLUTNew` | initialized SRAM/ShiftRegFile; file-read at compile/codegen time | `ShiftableMemory` literal; `FileLUT` reads file at sim load | — | `LUT()` / `"file:<filename>"` init | — |
| `MergeBufferNew` | `MergeBuffer` template (ways, par) | not yet covered | — | synthesized `inputFIFO`/`outputFIFO`/`boundFIFO` + LCA placement | — |
| `DRAMHostNew` / `DRAMAccelNew` | `DRAMAllocator` + `DRAMHeap` | flat `emul.Memory` | `c1->malloc` | `DRAM("name").dims(...)` + `dramAddress` | **unsupported** (AXI streams only) |
| `FrameNew` | AXI-Stream connection via Fringe | — | setFrame/getFrame | — | sendFrame/getFrame (pyrogue streams) |
| `StreamInNew` / `StreamOutNew` | AxiStream64/256/512 bus | `emul.StreamIn/StreamOut` with `bitsFromString`/`bitsToString` | — | `FIFO()` + `streamIn`/`streamOut` | TCP client binding |
| `LockSRAMNew` / `LockDRAMNew` / `LockNew` | specialized Chisel templates | simulation stubs | — | `LockMem(is_dram)` + `LockOnKeys` | — |

## Memory Accesses

| Node | Chiselgen | Scalagen | Pirgen |
|---|---|---|---|
| `SRAMRead` / `SRAMBankedRead` | flattens address via banking; banked read muxes N banks | OOB-wrapped `emitBankedLoad` | `MemRead` + `.bank(...).offset(...)` |
| `SRAMWrite` / `SRAMBankedWrite` | banked write strobe | OOB-wrapped `emitBankedStore` | `MemWrite` |
| `RegRead` / `RegWrite` | wire to FF; rewrites to `RegAccumOp`/`FMA` if accumulator cycle | `reg.x` / `reg.x = v` | `MemRead` / `MemWrite` |
| `FIFOEnq` / `FIFODeq` | template enq/deq | `q.enqueue` / `q.dequeue` | `MemRead`/`MemWrite` on FIFO |
| `LIFOEnq` / `LIFODeq` | template | `s.push` / `s.pop` | unsupported for most variants |
| `DenseTransfer` / `SparseTransfer` | lowered to `Fringe*` + burst cmd/data/resp streams (pre-codegen) | stream-driven for-loops | `FringeDenseLoad/Store` with separate offset/size/data/ack streams |
| `FrameTransmit` | AxiStream pack with tid/tdest | — | — |
| `MemDenseAlias` / `MemSparseAlias` | muxed reads from aliased memories | union of aliases | alias dispatch |

## Counters and Iterators

| Node | Chiselgen | Scalagen | Pirgen |
|---|---|---|---|
| `CounterNew` | `CtrObject` instantiation with start/step/max/par | `emul.Counter` | `Counter(par=N).min/step/max` |
| `CounterChainNew` | `CChainObject` | sequence of Counters | `CounterChain` |
| `ForeverNew` | `Forever` counter | `emul.Forever` | unconditional infinite counter |
| `LaneStatic` | constant per-lane value | Array constant | `Const(List(…))` |

## Primitives

| Node | Chiselgen | Scalagen | Pirgen |
|---|---|---|---|
| `FixAdd`/`FixMul`/`FixDiv`/`FixMod`/etc. | `Math.add`/`Math.mul`/`Math.div`/`Math.mod` with per-op latency | `emul.FixedPoint +/-/*/` + saturating/unbiased variants | PIR `OpDef(op=FixAdd).addInput(...).tp(...)` |
| `FltAdd`/`FltMul`/`FltFMA`/etc. | Math.fadd/fmul/ffma via HardFloat | `emul.FloatPoint` | PIR fp ops |
| `Mux` / `OneHotMux` / `PriorityMux` | combinational mux | `if/else if` chain | `Mux` / `OneHotMuxN` |
| `RegAccumOp` / `RegAccumFMA` | `FixFMAAccum` / `FixOpAccum` Bundle + optimized reg bundle | dispatch on `AccumAdd/Mul/Max/Min/FMA` | PIR accumulator semantics |
| `DelayLine` | `getRetimed(x, lat, bp & fp)` or `.DS(lat,…)` shift register | no-op (sim doesn't model latency) | — (PIR has no delay lines; `PIRGenDelays` empty) |
| `RetimeGate` | preserves ordering for retimer | sequencing effect | — |
| `ShuffleCompress` | `ShuffleCompressNetwork` lanes | Array comprehension | TODO |
| `VecAlloc` / `VecApply` / `VecConcat` / `VecSlice` | Chisel Vec[UInt] | Array[A] operations | width-1 only (PIR enforces `assertOne`) |
| `SimpleStruct` / `FieldApply` | packed UInt via `ConvAndCat` | Scala case class | PIR struct (field-flattened) |

## Debugging

| Node | Chiselgen | Scalagen | Cppgen | Rogue |
|---|---|---|---|---|
| `PrintIf` | stubbed (no host prints from accel) | `if (cond) println(...)` | `printf` | Python print |
| `AssertIf` | `Ledger.tieBreakpoint` | `if (cond) assert(...)` | assert | — |
| `BreakpointIf` | `Ledger.tieBreakpoint` | halt flag | early-exit dump | — |
| `ExitIf` | `Ledger.tieBreakpoint` | `System.exit` | early-exit | — |

## Notes

- **Scalagen is reference**: when two backends disagree, Scalagen+emul is ground truth. See [[20 - Scalagen/20 - Numeric Reference Semantics]].
- **Pirgen errors at codegen**: FIFO.isEmpty/isFull/peek/numel/almostEmpty/almostFull and LineBufferNew emit `error(...)` — users see this as a late compile error.
- **Tsthgen is semantically lossy**: all fixed-point types with fractional bits coerced to `float`/`double`. Bit-exact tests must use Scalagen, not Tsthgen.
- **Roguegen has no DRAM**: AXI streams only; user apps with host DRAM won't compile under Rogue.
