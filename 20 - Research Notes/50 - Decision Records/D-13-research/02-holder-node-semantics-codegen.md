---
type: research
decision: D-13
angle: 2
---

# Holder Node Semantics And Codegen

## Choice For This Angle

For angle 2, choose: **HLS lowering must preserve `Reg`/`FIFOReg`/`Var` pipe holders as observable state by default**, then add SSA elimination only as a legality-proven optimization. The source model is not just a naming convention. `Reg` and `FIFOReg` are local memories and staged vars, while `Var` is mutable top-level state (`src/spatial/lang/Reg.scala:9-20`, `src/spatial/lang/Reg.scala:68-83`, `argon/src/argon/lang/Var.scala:8-19`). Their node definitions carry allocation, read, write/enqueue, dequeue, and reset effects (`src/spatial/node/Reg.scala:11-47`, `argon/src/argon/node/Var.scala:7-44`). An HLS SSA rewrite is therefore legal only after proving that these effects are observationally redundant; that legality proof is unverified.

## Reg: Single-Slot State

`Reg` imposes non-destructive single-slot state with an initializer and an explicit reset path. The language API stages `RegWrite` for `:=`/`write`, `RegRead` for `.value`, and `RegReset` for reset, including enabled resets (`src/spatial/lang/Reg.scala:15-20`, `src/spatial/lang/Reg.scala:57-65`). The node layer makes writes `Enqueuer`s, makes reads unique/transient readers with no enables, and models reset as a `Resetter` (`src/spatial/node/Reg.scala:17-21`, `src/spatial/node/Reg.scala:29-37`, `src/spatial/node/Reg.scala:47`).

Scala simulation preserves this as mutable storage: `RegNew` emits a `Ptr` object and `initMem`, reads use `.value`, writes call `.set` under the enable, and reset calls `.reset()` under the enable (`src/spatial/codegen/scalagen/ScalaGenReg.scala:15-36`). The emulation pointer stores an `initValue`; `reset()` assigns that initializer back to the current value (`emul/src/emul/Ptr.scala:5-15`). Chisel generation maps ordinary `RegNew` to a `StandardInterface`, emits memory with the init, connects reads through `connectRPort`, writes through `connectWPort`, and reset through `connectReset` (`src/spatial/codegen/chiselgen/ChiselGenCommon.scala:111-120`, `src/spatial/codegen/chiselgen/ChiselGenMem.scala:52-58`, `src/spatial/codegen/chiselgen/ChiselGenMem.scala:227-293`). The underlying `FF` primitive is a `RegInit` whose next value is reset-to-init, enabled write data, or the old value; multiple enabled writes are priority-muxed (`fringe/src/fringe/templates/memory/MemPrimitives.scala:314-326`). HLS equivalence to SSA across reset, priority, or pipeline timing is unverified.

## FIFOReg: One-Element Elastic Holder

`FIFOReg` is the hard case. The surface API defines `.value` as `deq`, `.enq(data)` as enqueue, and deliberately makes `__reset` a no-op (`src/spatial/lang/Reg.scala:73-83`). The node layer separates `FIFORegEnq` from `FIFORegDeq`; dequeue is a unique/transient `Dequeuer` with enables, not a plain read (`src/spatial/node/Reg.scala:23-27`, `src/spatial/node/Reg.scala:39-45`). Metadata also treats FIFOReg as singleton state with destructive reads (`src/spatial/metadata/memory/package.scala:367-413`).

ScalaGen lowers FIFOReg to a mutable `Queue`: enqueue happens only when its enable conjunction is true; dequeue both checks non-empty and removes the element, otherwise returning an invalid value (`src/spatial/codegen/scalagen/ScalaGenFIFO.scala:46-52`). ChiselGen emits FIFOReg through the FIFO memory path, gives it a `FIFOInterface`, and wires enq/deq ports plus access-active bits (`src/spatial/codegen/chiselgen/ChiselGenMem.scala:217-224`, `src/spatial/codegen/chiselgen/ChiselGenCommon.scala:119-120`). The primitive is a one-element valid/data register: writes set data and valid, reads reset valid, output always reflects the stored data, and `empty`, `full`, and `numel` derive from the valid bit (`fringe/src/fringe/templates/memory/MemPrimitives.scala:339-365`; `fringe/src/fringe/templates/memory/SRFF.scala:19-27`). Chisel back-pressure explicitly includes FIFOReg empty/full and active-loopback terms (`src/spatial/codegen/chiselgen/ChiselGenCommon.scala:212-230`, `src/spatial/codegen/chiselgen/ChiselGenCommon.scala:249-272`). Lowering FIFOReg to SSA would erase destructive-read, full/empty, and scheduling pressure unless those are proved irrelevant; that HLS optimization claim is unverified.

## Var: Mutable IR/Simulator Holder

`Var` is not a Spatial hardware memory in the same sense: `VarNew`, `VarRead`, and `VarAssign` all set `canAccel = false`, allocation has `Effects.Mutable`, and assignment has `Effects.Writes(v)` (`argon/src/argon/node/Var.scala:7-14`, `argon/src/argon/node/Var.scala:38-44`). Its read node is transient and rewrites to the most recent same-scope impure assignment when that proof is syntactically available (`argon/src/argon/node/Var.scala:15-36`). ScalaGen still emits a real mutable `Ptr`, with reads as `.value` and writes as `.set` (`src/spatial/codegen/scalagen/ScalaGenVar.scala:9-18`). Chisel debug code emits blank string placeholders for Var operations, and Chisel port/remap cases treat `Var` as `String`, so a hardware realization is not established by this slice (`src/spatial/codegen/chiselgen/ChiselGenDebug.scala:18-20`, `src/spatial/codegen/chiselgen/ChiselCodegen.scala:393-397`). HLS treatment of `Var` as SSA is plausible only when it matches the Var rewrite/effect rules; this is unverified.

## HLS Lowering Rule

The conservative D-13 rule should be: preserve holder nodes first, optimize later. `Reg` may be SSA-replaced only when there is no reset, no host/arg visibility, no multiple-writer priority, and no timing dependence across the generated pipe boundary. `Var` may be flattened when the same-scope rewrite proof already justifies it. `FIFOReg` should normally remain a one-element FIFO with ready/valid-like state, because existing Chisel codegen uses full/empty and active signals for control pressure. These legality conditions are HLS claims and remain unverified.
