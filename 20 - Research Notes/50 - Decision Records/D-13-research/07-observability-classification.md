# Holder Observability Classification

## PipeInserter Boundary

`PipeInserter` creates an explicit holder boundary only for values that escape an inner stage. Inside `wrapInner`, it identifies non-void stage nodes whose consumers leave the stage or whose symbol is the block result, emits a generated `Pipe { ... }`, writes each escaping value to a holder inside that pipe, then reads the holder afterward and registers the original symbol to the read result (`src/spatial/transform/PipeInserter.scala:170-201`). The holder kind is type/schedule driven: bit-valued escapes under stream control use `FIFOReg`; other bit-valued escapes use `Reg`; non-bit escapes use `Var` (`src/spatial/transform/PipeInserter.scala:256-260`). Thus the baseline IR is not "pure SSA plus a name"; it is an allocation plus ordered write/read nodes.

The only clearly SSA-like case is a **value-only handoff**: one inner-stage producer, one post-pipe consumer, a write that dominates the read, no stream parent, no reset/read-before-write observation, and no use of the holder identity by analysis, naming, or debug output. That is a legality proof, not the default interpretation of the transformed IR. The pass itself also has an ordering hook for transient reads: stage placement treats stage writes as dependencies of later transient nodes, called out in-code as a special case for ordered `RegRead`s (`src/spatial/transform/PipeInserter.scala:117-124`). More generally, Argon effect scheduling records WAR, RAW/WAW, and allocation-before-access hazards as anti-dependencies (`argon/src/argon/static/Staging.scala:194-233`).

## Reg and FIFOReg

`Reg` is the ordinary cycle/state holder. Its node layer defines `RegNew(init)`, `RegWrite`, `RegRead`, and `RegReset`; reads are transient but also `Unique`, while writes and resets inherit memory-write effects through the access base classes (`src/spatial/node/Reg.scala:11-47`; `src/spatial/node/HierarchyAccess.scala:30-35`, `src/spatial/node/HierarchyAccess.scala:115-138`). The language API exposes `value`, `write`, `:=`, `reset`, and `alloc(reset)`, so a `Reg` is observable as mutable state whenever reads/writes/resets survive lowering (`src/spatial/lang/Reg.scala:15-20`, `src/spatial/lang/Reg.scala:57-65`). Scalagen materializes it as a `Ptr`, initializes it, reads `.value`, and writes `.set(...)` (`src/spatial/codegen/scalagen/ScalaGenReg.scala:15-36`).

`FIFOReg` is stronger: it is a stream/back-pressure boundary, not merely a value latch. `FIFORegNew`, `FIFORegEnq`, and `FIFORegDeq` are distinct node forms; dequeue is transient and `Unique`, but it is a `Dequeuer`, whose effect is a write to the memory because the read is destructive (`src/spatial/node/Reg.scala:12`, `src/spatial/node/Reg.scala:23-45`; `src/spatial/node/HierarchyAccess.scala:78-93`). The API exposes `enq`/`deq` rather than `write`/`read`, and reset is a no-op at the language level (`src/spatial/lang/Reg.scala:68-99`). Existing codegen treats it as queue/FIFO state: Scalagen emits a mutable queue with guarded enqueue/dequeue (`src/spatial/codegen/scalagen/ScalaGenFIFO.scala:46-52`), while Chiselgen emits FIFO-interface accesses, access activity lanes, and forward/back-pressure predicates for `FIFORegNew` alongside ordinary FIFOs (`src/spatial/codegen/chiselgen/ChiselGenMem.scala:217-224`; `src/spatial/codegen/chiselgen/ChiselGenCommon.scala:247-272`).

## Var Holders

`Var` is the non-bit escape path. `PipeInserter` allocates it with `Var.alloc(None)`, reads with `Var.read`, and writes with `Var.assign(x, data.unbox)` (`src/spatial/transform/PipeInserter.scala:298-314`). Argon defines `VarNew` as mutable and not accelerator-capable, `VarAssign` as a write effect on the variable, and `VarRead` as transient with a local rewrite to the most recent assignment in the current scope (`argon/src/argon/node/Var.scala:7-45`). Its API is staged variable read/assign (`argon/src/argon/lang/Var.scala:13-19`), and Scalagen emits a `Ptr`, possibly null-initialized, with `.value` and `.set(...)` (`src/spatial/codegen/scalagen/ScalaGenVar.scala:14-18`).

This makes non-bit `Var` a different observability class from `Reg`. It is not a bit-level storage primitive that an HLS backend should blindly map to a hardware register. If the non-bit value is structurally pure and the write/read pair is a value-only handoff, SSA is likely the natural lowering. If the value has mutable identity, alias-sensitive structure, source-ordered assignment, or read-before-write/reset behavior, the backend must preserve the variable semantics or reject/lower the non-bit type explicitly.

## Policy Classes

| Observability class | Reg | FIFOReg | Var |
|---|---|---|---|
| Value-only handoff | SSA-eligible with dominance/no-identity proof. | Rare; only with proof that stream semantics are absent. | SSA-eligible for pure non-bit values. |
| Cycle/state boundary | Preserve as state when write/read/reset survives. | Preserve; queue state plus destructive read. | Preserve only as variable semantics, not bit storage. |
| Stream/back-pressure boundary | Not the selected stream holder. | Preserve by default under stream control. | Not applicable unless non-bit stream protocol is modeled separately. |
| Reset/init | Preserve if init/reset can be observed; otherwise dead after proven dominating write. | Preserve allocation/init semantics where backend models them; dequeue-before-enqueue is observable. | `None` init/read-before-write semantics require care. |
| Effect ordering | Preserve when effects/anti-deps order surrounding nodes. | Preserve: enq/deq are effectful and pressure-aware. | Preserve assignment/read ordering unless rewrite proof applies. |
| Debug/naming | Names may be metadata unless diagnostics/codegen parity requires them. | Same, plus FIFO access names. | Names are mostly compiler/debug metadata. |
| Non-bit semantics | Not applicable. | Not applicable. | Primary hard case: structural identity/aliasing may block SSA. |

Named codegen reinforces the debug/naming category by assigning stable `reg`, `fiforeg`, read/write, and enq/deq names to these holders and accesses (`src/spatial/codegen/naming/NamedCodegen.scala:41-56`).
