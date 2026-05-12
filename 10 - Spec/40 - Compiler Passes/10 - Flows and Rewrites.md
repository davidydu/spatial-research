---
type: spec
concept: flows-and-rewrites
source_files:
  - "src/spatial/Spatial.scala:56-58"
  - "src/spatial/flows/SpatialFlowRules.scala:13-417"
  - "src/spatial/rewrites/SpatialRewriteRules.scala:1-8"
  - "src/spatial/rewrites/AliasRewrites.scala:13-108"
  - "src/spatial/rewrites/CounterIterRewriteRule.scala:12-51"
  - "src/spatial/rewrites/LUTConstReadRewriteRules.scala:10-49"
  - "src/spatial/rewrites/VecConstRewriteRules.scala:10-27"
source_notes:
  - "[[pass-pipeline]]"
hls_status: rework
depends_on:
  - "[[30 - IR]]"
  - "[[Argon Framework Staging]]"
status: draft
---

# Flows and Rewrites

## Summary

Flows and rewrites are the two staging-time metadata/IR-mutation mechanisms Spatial registers with the argon framework before any pass runs. `SpatialFlowRules` installs 9 `@flow` callbacks that fire on every symbol creation, propagating control hierarchy, schedule, accumulator type, and globality metadata. `SpatialRewriteRules` composes 4 trait-based rule sets (`AliasRewrites`, `CounterIterRewriteRule`, `LUTConstReadRewriteRules`, `VecConstRewriteRules`) that intercept and rewrite IR nodes at register time — before they enter the IR graph. Both mechanisms let Spatial specialize argon's generic staging pipeline without a dedicated pass.

## Registration

Two `Spatial` trait overrides wire these into argon's compiler lifecycle (`src/spatial/Spatial.scala:57-58`):

```scala
override def flows(): Unit = SpatialFlowRules(state)
override def rewrites(): Unit = SpatialRewriteRules(state)
```

`SpatialFlowRules` is a `case class SpatialFlowRules(IR: State) extends FlowRules` (`flows/SpatialFlowRules.scala:13`). Instantiation runs its body, which registers each `@flow def` in the argon flow-rule registry. `SpatialRewriteRules` is a composition class with no body: `case class SpatialRewriteRules(IR: State) extends RewriteRules with AliasRewrites with LUTConstReadRewriteRules with VecConstRewriteRules with CounterIterRewriteRule` (`rewrites/SpatialRewriteRules.scala:5-7`). Each mixed-in trait runs its own `IR.rewrites.add[…]` or `@rewrite` registrations on construction.

## Flow rules (`SpatialFlowRules`)

Flow rules fire **at staging time for every new symbol**. Argon invokes all registered `@flow` callbacks when `stage(op)` returns a new symbol. The dispatch is by definition order, so ordering matters: `memories` → `accesses` → `accumulator` → `controlLevel` → `blackbox` → `blockLevel` → `controlSchedule` → `streams` → `globals` (`flows/SpatialFlowRules.scala:14, 21, 44, 69, 289, 305, 331, 389, 406`).

### `memories` (`:14-19`)

Matches `MemAlloc(mem)` vs local/remote/stream-in/stream-out. Side effect: populates the `LocalMemories` and `RemoteMemories` global sets. Downstream consumers: `MemoryAnalyzer.run` (`traversal/MemoryAnalyzer.scala:143`) reads `LocalMemories.all`.

### `accesses` (`:21-42`)

Matches `Accessor(wr, rd)`, `UnrolledAccessor(wr, rd)`, `FieldDeq`, `VerilogCtrlBlackbox`, `Resetter`. Side effects: `w.mem.writers += s`, `r.mem.readers += s`, `mem.resetters += s`. The `VerilogCtrlBlackbox` branch (`:33-37`) additionally inspects a `SimpleStreamStruct` to populate `s.readMems` for any embedded `FIFODeqInterface` reads.

### `accumulator` (`:44-67`)

Two-phase: (1) propagate `s.readUses` from `s.inputs`; (2) if `s` is a `Writer(mem, ...)` or `UnrolledWriter(wr)`, scan `s.readUses` for any read that targets the same memory as the write — if found, set `mem.accumType = AccumType.Fold & mem.accumType` and `s.accumType = AccumType.Fold & s.accumType`. The `&` operator implements the accum-type lattice join. This is the first phase of identifying accumulation patterns for `AccumTransformer` to specialize later (`transform/AccumTransformer.scala:50-110`).

### `controlLevel` (`:69-287`)

By far the largest flow rule (~220 lines). Three cases:
1. `IfThenElse` (`:70-76`): computes `rawChildren` from nested control stmts; marks `Outer` if any child is `!c.isBranch || c.isOuterControl || op.isMemReduce`.
2. `SpatialCtrlBlackboxImpl` (`:77-82`): same as (1) but always `Outer`; throws if empty children.
3. `Control[_]` (`:165-284`): the meat. Computes `rawChildren`, `rawLevel` (Inner vs Outer), sets counter owners (`cchain.owner`, `cchain.rawParent`, `cchain.rawScope`), handles the `OpReduce` special case where `map.result` gets `Ctrl.Node(s, 1)` parent (`:192-200`), then for each block in `ctrl.bodies` sets iter parents and recursively sets `rawParent` and `rawScope` for every stmt (`:203-243`). Finally walks each block's stmts and populates `s.writtenMems`/`s.readMems`/`s.writtenDRAMs`/`s.readDRAMs` (`:247-283`) and sets `s.shouldNotBind` on controllers containing `BreakpointIf`/`ExitIf` (`:279-280`).

### `blackbox` (`:289-303`)

Matches `SpatialBlackboxImpl`, `SpatialBlackboxUse`, `SpatialCtrlBlackboxImpl`, `SpatialCtrlBlackboxUse`. Side effects: for `Impl` variants, sets `c.rawParent = s.toCtrl` for each stmt in `func.stms`; for `Use` variants, calls `bbox.addUserNode(s)`.

### `blockLevel` (`:305-315`)

For each block in `op.blocks`, iterate stmts and set `lhs.blk = Blk.Node(s, bId)`. Also sets `b.blk = Blk.Node(s, -1)` for bound symbols (`:312-314`).

### `controlSchedule` (`:317-373`)

The 6-rule schedule selection. Highlights:
1. `ParallelPipe → ForkJoin`, `Switch → Fork`, `SpatialBlackboxImpl → PrimitiveBox`, `SpatialCtrlBlackboxImpl → Sequenced`, `IfThenElse → Fork`, `SwitchCase → Sequenced`, `DenseTransfer → Pipelined`, `SparseTransfer → Pipelined` (`:332-339`).
2. For general `Control[_]` (`:340-372`): user schedule > compiler schedule > default. Default is `Sequenced` if `isUnitPipe || isAccel`, else `Pipelined`.
3. Corrections: `isSingleControl && Pipelined → Sequenced`; `isSingleChildOuter && Pipelined → Sequenced` (controllers where `isOuterControl && children.size == 1 && toCtrl.children.size == 1 && !hasPrimitives`); `isUnitPipe && Fork → Sequenced` (undoes metadata-transfer corruption from Switch→UnitPipe wrapping in PipeInserter, `:368`).

### `streams` (`:389-396`)

Appends to several global sets based on structural queries: `StreamLoads += s` if `isStreamLoad`, `TileTransfers += s` if `isTileTransfer`, etc. Populates `StreamEnablers` and `StreamHolders`.

### `globals` (`:406-415`)

Three cases:
1. `Impure(_,_)` — do nothing (stateful).
2. `Op(RegRead(reg)) if reg.isArgIn` — `lhs.isGlobal = true`.
3. `Primitive(_)` with all inputs global/fixedBits — `lhs.isGlobal = true` / `lhs.isFixedBits = true`.

The intent: "global" = constant for the duration of main computation (only a function of input args + constants). Critical for downstream DSE and for deciding whether a value can be hoisted.

## Rewrite rules (`SpatialRewriteRules`)

Rewrites fire **at register time**: when argon stages an op that matches a registered pattern, the rewrite intercepts and returns a substitute symbol before the op is inserted into the IR.

Two registration forms exist:
- `@rewrite def name(op: OpType): Sym[_]` — trait-method annotation, expanded by forge macros into a `IR.rewrites.add[OpType]("name", pf)` call (used in `AliasRewrites`).
- `IR.rewrites.add[OpType]("name", { case (op, ctx, _) => … })` — direct registration (used in `CounterIterRewriteRule`, `LUTConstReadRewriteRules`).
- `IR.rewrites.addGlobal("name", { case (op, ctx, _) => … })` — global rule that runs on every op with a matching super-type (used in `VecConstRewriteRules`).

### `AliasRewrites` (`rewrites/AliasRewrites.scala`)

Simplifies `MemDenseAlias` / `MemSparseAlias` projections and their derived length/dim operations.

- `rewriteDenseAlias` (`:37-66`): if any input memory in a `MemDenseAlias` is itself a `MemDenseAlias`, flatten by `zipped.flatMap` over conditions/mems/series, combining conditions with `&` and series with `combineSeries`. Recreates as a single `MemDenseAlias(conds3, mems3, seriess3)` (`:63`). Otherwise returns `Invalid` (no rewrite).
- `combineSeries` (`:17-35`): given two series, produces a combined series with `start = r1.start + r2.start * r1.step`, `end = min(r1.end, r1.start + r2.end * r1.step)`, `step = r1.step * r2.step`, `par = r2.par if r1.par==1 else r1.par`, `isUnit = r1.isUnit || r2.isUnit`.
- `nested_dense_alias` (`:68-70`): the `@rewrite` wrapper that delegates to `rewriteDenseAlias`.
- `mem_start` / `mem_step` / `mem_end` / `mem_par` / `mem_len` / `mem_dim` / `mem_rank` (`:72-106`): 7 `@rewrite` patterns that extract the requested geometry from either a `MemDenseAlias`/`MemSparseAlias`/`MemAlloc`. Each has a 1-dim fallthrough to avoid depending on alias-flattening semantics that haven't been computed.

### `CounterIterRewriteRule` (`rewrites/CounterIterRewriteRule.scala`)

A single global rule `"UnrollLane"` registered via `IR.rewrites.add[FixMod[_,_,_]]` (`:18`). Matches three affine patterns that compute the post-unrolling lane ID from a pre-unroll iterator:
1. `iter % par` where `start == 0 && step == 1` (`:20-22`).
2. `(iter / step) % par` where `start == 0` (`:23-27`).
3. `((iter - start) / step) % par` (general case) (`:28-36`).

All three emit `LaneStatic(iter, List.tabulate(par){i => i})`, bypassing the usual `FixMod` node and providing the unroller with ready-made lane ID information. The match guard relies on `PreunrollIter.unapply` (`:43-50`) which uses `sym.getCounter` to extract the counter's `start`/`end`/`step`/`par` from `IndexCounterInfo` metadata — and only fires when the iter is a bound symbol of a `CounterNew` node whose `lanes.size == par`.

### `LUTConstReadRewriteRules` (`rewrites/LUTConstReadRewriteRules.scala`)

A single rule `"ConstLutRead"` on `LUTBankedRead` (`:13`). When a banked read on an all-constant LUT uses a constant bank address, the rule flattens the ND access into a 1D flat index via `flattenND` (`:42-48`) and emits a `VecAlloc` of the literal values. The rule handles both scalar bank addresses (`:30-38`) and vector-of-scalar bank addresses (the first branch at `:16-30`, which transposes the address list and flattens each row).

The interesting bits:
- `ConstSeq.unapply` (`:51-61`) handles both `Const(FixedPoint)` and `Const(x)` and `VecConst(xs)`, mapping all to `Int`.
- The rule fires only if the LUT elements themselves are constant (`elems(a) match { case Const(c) => c; case c => throw ... }` at `:27`). A non-constant element raises an exception — LUTs with non-constant initialization should never reach this rewrite.

### `VecConstRewriteRules` (`rewrites/VecConstRewriteRules.scala`)

Single global rule `"VecConstProp"` (`:13`) covering binary ops and `FixSRA`:
- `FixSRA(a, b)` with `b` positive shifts right by `y`; negative shifts left by `-y` (`:14-16`).
- Any `Binary[c,r]` op: if both inputs constant, apply `op.unstaged(a, b)` directly; else use `VecConst.broadcast(a, b){(a, b) => op.unstaged(a, b)}` (`:17-24`).

The rule is `addGlobal` rather than per-op because any `Binary` subtype can benefit.

## Metadata side effects

The flow rules are authoritative for the following metadata (file:line citations given as the writing site):

| Metadata | Set by | Where |
|---|---|---|
| `LocalMemories`, `RemoteMemories` | `memories` flow | `flows/SpatialFlowRules.scala:14-19` |
| `mem.writers`, `mem.readers`, `mem.resetters` | `accesses` flow | `:21-42` |
| `s.readUses`, `mem.accumType`, `s.accumType` | `accumulator` flow | `:44-67` |
| `s.rawChildren`, `s.rawLevel` | `controlLevel` flow | `:70-76, 77-82, 167-173` |
| `cchain.owner`, `ctr.rawParent`, `ctr.rawScope` | `controlLevel` flow | `:179-188` |
| `iter.rawParent` (and for UnrolledLoop, `valids.rawParent`) | `controlLevel` flow | `:214-218` |
| `lhs.rawParent`, `lhs.rawScope` | `controlLevel` flow | `:226-242` |
| `s.writtenMems`, `s.readMems`, `s.writtenDRAMs`, `s.readDRAMs`, `s.shouldNotBind` | `controlLevel` flow | `:247-283` |
| `lhs.blk` | `blockLevel` flow | `:307-314` |
| `s.rawSchedule` | `controlSchedule` flow | `:332-368` |
| `StreamLoads`, `TileTransfers`, `StreamParEnqs`, `StreamEnablers`, `StreamHolders` | `streams` flow | `:389-396` |
| `lhs.isGlobal`, `lhs.isFixedBits` | `globals` flow | `:406-415` |

## Interactions

- **`PipeInserter`** reads `isOuterControl` (established by `controlLevel`), `isParallel`/`isStreamControl` (established by `controlSchedule`), and `inHw` (established by ancestor scanning against `AccelScope`) to decide which blocks to recursively wrap.
- **`AccumAnalyzer`** and **`AccumTransformer`** consume `accumType` set in the `accumulator` flow.
- **`UnrollingTransformer`** consumes `cchain.counters` (set up by `controlLevel` for Loop controllers), `isInnerControl`/`isOuterControl` (from `controlLevel`), `rawSchedule` (from `controlSchedule`), and the full set of `rawParent`/`rawScope` to locate symbols in the post-unroll hierarchy.
- **`AccessAnalyzer`** consumes `cchain` structure and walks loop bodies using `iters` from `controlLevel`.
- **`CounterIterRewriteRule`**-emitted `LaneStatic` nodes are consumed by `MemoryUnrolling` when computing per-lane duplicate selection.
- **`AliasRewrites`**-simplified aliases feed into `MemoryDealiasing` (`transform/MemoryDealiasing.scala`), which resolves the remaining alias reads/writes into muxed DRAM accesses before `PipeInserter`.

## Order of operations

Flow rules run in definition order inside the `SpatialFlowRules` class (`:14, 21, 44, 69, 289, 305, 331, 389, 406`). Rewrites, by contrast, can fire in any order depending on which op is being staged; the only guarantee is that all registered rewrites for a given op run before the op is added to the IR, and all flow rules run after the op is added. For ops that can be rewritten AND have flow rules (e.g. a `FixMod` that becomes `LaneStatic`), the rewrite fires first, and the flow rules run on the replacement.

## HLS notes

All flow rules translate to pure metadata computations. A Rust+HLS rewrite can reproduce them as compile-time constexpr functions over the IR node types (the control-hierarchy scan in `controlLevel` is O(n²) naive but most graphs are shallow). The rewrite rules are harder: `AliasRewrites` depends on the specific `MemDenseAlias` / `MemSparseAlias` structure, which is Spatial-specific; `LUTConstReadRewriteRules` depends on the `VecAlloc` / `LUTBankedRead` node pair, which is Spatial-specific. `CounterIterRewriteRule` assumes argon's bound-symbol mechanism for pre-unroll iterators. None are `clean` HLS targets.

## Open questions

- Q-007 (filed 2026-04-23) — the exact semantics of `accumType & accumType` on the `Fold` lattice (the `accumulator` flow uses `&`, but `AccumType`'s algebraic structure isn't documented at the call site).
