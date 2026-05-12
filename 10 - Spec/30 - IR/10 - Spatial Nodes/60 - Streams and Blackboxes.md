---
type: spec
concept: spatial-ir-streams-blackboxes
source_files:
  - "src/spatial/node/StreamIn.scala:1-21"
  - "src/spatial/node/StreamOut.scala:1-28"
  - "src/spatial/node/StreamStruct.scala:1-22"
  - "src/spatial/node/Blackbox.scala:1-63"
  - "src/spatial/node/HierarchyControl.scala:7-15"
  - "src/spatial/node/HierarchyControl.scala:62"
  - "src/spatial/node/HierarchyAccess.scala:79-104"
  - "src/spatial/node/HierarchyAccess.scala:133-148"
  - "src/spatial/node/HierarchyUnrolled.scala:99-103"
  - "src/spatial/node/HierarchyUnrolled.scala:136-139"
  - "src/spatial/lang/StreamIn.scala:9-28"
  - "src/spatial/lang/StreamOut.scala:10-29"
  - "src/spatial/lang/StreamStruct.scala:8-37"
  - "src/spatial/lang/Blackbox.scala:11-119"
  - "src/spatial/lang/Bus.scala:13-87"
  - "src/spatial/metadata/blackbox/BlackboxData.scala:1-18"
  - "src/spatial/metadata/blackbox/package.scala:7-23"
  - "argon/src/argon/node/DSLOp.scala:13-31"
  - "argon/src/argon/node/Enabled.scala:6-21"
source_notes:
  - "[[spatial-ir-nodes]]"
hls_status: rework
depends_on:
  - "[[20 - Memories]]"
  - "[[30 - Memory Accesses]]"
  - "[[10 - Controllers]]"
status: draft
---

# Streams and Blackboxes (IR nodes)

## Summary

This entry covers two related node families: **stream surface ops** — `StreamIn`/`StreamOut` reads/writes plus the `StreamStruct` field-level dequeue/enqueue used to model decoupled multi-field streams — and **blackbox nodes**, the IR mechanism for inserting compiler-opaque hardware blocks (Verilog modules, third-party IPs, GEMM accelerators) into a Spatial program. The two are coupled because Spatial controller-blackboxes pass data through `StreamStruct` ports: `CtrlBlackboxUse[A:StreamStruct, B:StreamStruct]` (`src/spatial/node/Blackbox.scala:40`) is the IR ancestor for any blackbox that exchanges streamed bundles. Stream nodes are a small, regular set built on the `Dequeuer`/`Enqueuer` and `BankedDequeue`/`BankedEnqueue` accessor hierarchies; blackbox nodes form a richer family with three orthogonal axes (Spatial-vs-Verilog, Primitive-vs-Ctrl, Impl-vs-Use) plus the special-case `GEMMBox` and the Spatial-side `EarlyBlackbox` lowering used by `DenseTransfer`/`SparseTransfer`/`FrameTransmit`. For the HLS rewrite, both families are `rework`: streams map to `hls::stream<T>` but the `StreamStruct` field-level decoupling is Spatial-specific, and HLS doesn't have a first-class blackbox concept.

## Syntax / API

### Streams

Stream allocation is documented in [[20 - Memories]]; this entry focuses on the access surface.

- `streamIn.value()` / `streamIn.value(en: Bit)` (`src/spatial/lang/StreamIn.scala:14-15`) → `stage(StreamInRead(this, ens))`. Returns the next dequeued value.
- `streamOut := data` / `streamOut := (data, en)` (`src/spatial/lang/StreamOut.scala:15-16`) → `stage(StreamOutWrite(this, data, ens))`.
- `streamIn.__read(addr, ens)` defaults to `value()` (`StreamIn.scala:18`); `__write` errors out (lines 19-23) — `StreamIn` is read-only.
- `streamOut.__write(data, addr, ens)` stages a `StreamOutWrite` (`StreamOut.scala:24`); `__read` errors out (lines 19-23).
- Banked variants: `StreamInBankedRead(mem, enss)` (`src/spatial/node/StreamIn.scala:16-20`), `StreamOutBankedWrite(mem, data, enss)` (`src/spatial/node/StreamOut.scala:22-27`). Emitted post-unroll only.

### StreamStruct

A `StreamStruct[A]` (`src/spatial/lang/StreamStruct.scala:12-29`) is a struct whose fields are themselves decoupled streams — reading a field is a dequeue on that one field's stream.

- `StreamStruct[S](elems: (String, Sym[_])*)` (`src/spatial/lang/StreamStruct.scala:34`) → `stage(SimpleStreamStruct[S](elems))`. Aggregates per-field syms into a single struct.
- `struct.field[F:Bits](name)` (`StreamStruct.scala:17`) → calls `StreamStruct.field` (line 35) → `stage(FieldDeq[S,F](struct, name, Set[Bit]()))`.
- `struct.field_update[A:Type](name, data)` (`StreamStruct.scala:36`) → `stage(FieldEnq[S,A](struct, name, data))`.

### Blackboxes

Five entry points in `src/spatial/lang/Blackbox.scala:34-119`:

- `Blackbox.SpatialPrimitive[A:Struct, B:Struct](func: A => B)` (lines 41-49) — wrap a Scala lambda as a Spatial-defined primitive blackbox. Stages a `SpatialBlackboxImpl` (the impl handle) which is later instantiated via `bbox.apply(in)` (`SpatialBlackbox.apply`, `lang/Blackbox.scala:15-19`) to produce a `SpatialBlackboxUse`.
- `Blackbox.SpatialController[A:StreamStruct, B:StreamStruct](func: A => B)` (lines 54-62) — same shape as `SpatialPrimitive` but produces a controller-flavored blackbox. Stages `SpatialCtrlBlackboxImpl`; usage stages `SpatialCtrlBlackboxUse`.
- `Blackbox.VerilogPrimitive[A:Struct, B:Struct](inputs)(file, moduleName, latency, pipelineFactor, params)` (lines 70-74) — wrap an external Verilog file. Stages `VerilogBlackbox` directly; metadata `BlackboxConfig` carries the file path, latency, pipeline factor, and parameter map.
- `Blackbox.VerilogController[A:StreamStruct, B:StreamStruct](inputs)(file, moduleName, params)` (lines 90-95) — wrap an external Verilog controller module. Stages `VerilogCtrlBlackbox` and sets `rawLevel = Inner` (line 93) — so the blackbox acts as an inner controller that must be the immediate child of a `Stream` controller (per the doc comment, lines 86-88).
- `Blackbox.GEMM[T:Num](y, a, b, c, alpha, beta, i, j, k, mt, nt)` (lines 101-119) — special-cased matrix multiply blackbox. Stages a `GEMMBox` directly with a synthesized counter chain (line 116). `Blackbox.GEMV` and `Blackbox.CONV` are stubbed (`???`, lines 121-122).
- `Blackbox.getParam[T:Bits](field)` (lines 36-38) → `stage(FetchBlackboxParam[T](field))` — reads a value out of the blackbox parameter map (`BlackboxConfig.params`) at instantiation time.

## Semantics

### Stream allocations

`StreamInNew[A:Bits](bus: Bus)` (`src/spatial/node/StreamIn.scala:7-9`) and `StreamOutNew[A:Bits](bus: Bus)` (`src/spatial/node/StreamOut.scala:7-9`) extend `MemAlloc[A, StreamIn]` / `MemAlloc[A, StreamOut]` with `dims = Seq(I32(1))` — they're rank-1 memories of size 1, but logically streams. The `bus: Bus` field carries the wire-level protocol; the `Bus` type hierarchy lives in `src/spatial/lang/Bus.scala:13-87` and includes `BurstCmdBus`, `BurstAckBus`, `BurstDataBus[A]`, `BurstFullDataBus[A]`, `GatherAddrBus`, `GatherDataBus[A]`, `ScatterCmdBus[A]`, `ScatterAckBus`, `AxiStream64Bus`/`AxiStream256Bus`/`AxiStream512Bus`, `FileBus[A]`, `FileEOFBus[A]`, and `PinBus`.

The DSL types `StreamIn[A]` and `StreamOut[A]` extend **both** `LocalMem0[A, …]` and `RemoteMem[A, …]` (`src/spatial/lang/StreamIn.scala:9`, `src/spatial/lang/StreamOut.scala:10`) — a unique double-mixin among Spatial memories. They behave locally for access (you can `value()` them inside `Accel`) but remotely for lifetime (allocation/deallocation crosses the host/accel boundary).

### `StreamInRead` / `StreamInBankedRead`

```scala
@op case class StreamInRead[A:Bits](mem: StreamIn[A], ens: Set[Bit]) extends Dequeuer[A,A]
```
(`src/spatial/node/StreamIn.scala:11-14`).

A pre-unroll dequeue. Inherits `Dequeuer[A,A]` (`src/spatial/node/HierarchyAccess.scala:92-94`) which inherits `DequeuerLike` with `effects = Effects.Writes(mem)` (line 80) — dequeue mutates the stream's internal state. `addr = Nil`. `ens` is the conjunctive enable.

```scala
@op case class StreamInBankedRead[A:Bits](mem: StreamIn[A], enss: Seq[Set[Bit]])(implicit vT: Type[Vec[A]]) extends BankedDequeue[A]
```
(`StreamIn.scala:16-20`). Post-unroll vectorized dequeue. Returns `Vec[A]`. Inherits `BankedDequeue[A]` (`HierarchyUnrolled.scala:99-103`) which sets `bank = Nil, ofs = Nil` — there's no addressing for a stream. Per-lane enables in `enss`. `Effects.Writes(mem)`.

### `StreamOutWrite` / `StreamOutBankedWrite`

```scala
@op case class StreamOutWrite[A:Bits](mem: StreamOut[A], data: Bits[A], ens: Set[Bit]) extends Enqueuer[A]
```
(`src/spatial/node/StreamOut.scala:11-15`). Pre-unroll enqueue. `Enqueuer[A]` (`HierarchyAccess.scala:136-138`) is a `Writer[A]` with `addr = Nil` and `Effects.Writes(mem)` (line 117).

```scala
@op case class StreamOutBankedWrite[A:Bits](
  mem:  StreamOut[A],
  data: Seq[Sym[A]],
  enss: Seq[Set[Bit]]
)(implicit vT: Type[Vec[A]]) extends BankedEnqueue[A]
```
(`StreamOut.scala:22-27`). Post-unroll vectorized enqueue. `BankedEnqueue[A]` (`HierarchyUnrolled.scala:136-139`) extends `BankedWriter[A]` with `bank = Nil, ofs = Nil`. The doc comment (`StreamOut.scala:17-21`) calls out that `data` is one entry per vector element; `enss` is one entry per element.

### `SimpleStreamStruct`

```scala
@op case class SimpleStreamStruct[S:StreamStruct](elems: Seq[(String, Sym[_])]) extends Primitive[S] {
  override val isTransient: Boolean = true
}
```
(`src/spatial/node/StreamStruct.scala:8-10`).

A compile-time field grouping — `isTransient = true` means it disappears after analysis. The `elems` sequence pairs field names to per-field syms. There's no hardware: a `SimpleStreamStruct` is a typing wrapper. After streamification/blackbox lowering, individual field syms are wired directly into the consuming blackbox or stream surface.

### `FieldDeq` / `FieldEnq`

```scala
@op case class FieldDeq[S, A:Bits](struct: StreamStruct[S], field: String, ens: Set[Bit]) extends EnPrimitive[A] {
  override val isTransient: Boolean = false
  // TODO: Technically this is a mutation but I'm not sure how to apply it to a bound sym for SpatialCtrl blackbox
  // override def effects: Effects = Effects.Writes(struct)
}
```
(`src/spatial/node/StreamStruct.scala:12-16`).

A field-level dequeue: read field `field` from the struct, where reading is a dequeue on that one field's underlying stream. The TODO at lines 14-15 notes that this *should* be a `Effects.Writes(struct)` — semantically a field dequeue mutates the struct's state — but the override is commented out because applying the effect to a bound symbol inside a `SpatialCtrl` blackbox is ambiguous. Currently `FieldDeq` inherits the default pure-primitive effect, which is technically incorrect.

`isTransient = false` is set explicitly (line 13) — overriding the parent default — to flag that this *is* a real hardware operation, not a typing wrapper.

```scala
// TODO: FieldEnq may not actually be used anywhere
@op case class FieldEnq[S, A:Type](struct: StreamStruct[S], field: String, data: A) extends Primitive[Void] {
  override def effects: Effects = Effects.Writes(struct)
  override val canAccel: Boolean = true
}
```
(`StreamStruct.scala:18-22`).

A field-level enqueue with the dual semantics: write `data` into field `field`. Effects are correctly declared as `Effects.Writes(struct)`. The TODO at line 18 flags that `FieldEnq` may be dead code — kept in the IR surface for symmetry but possibly never produced. The `field_update` DSL helper (`src/spatial/lang/StreamStruct.scala:36`) does stage it, so the TODO is conservative.

### Blackbox class hierarchy

The blackbox hierarchy splits along three orthogonal axes: Spatial-vs-Verilog (Scala `Lambda1` body vs external `.v` file referenced through `BlackboxConfig`), Primitive-vs-Ctrl (stateless `Primitive[B]` vs inner-controller `EnControl[B]`), and Impl-vs-Use (allocation handle, one per declaration, vs instantiation, many per Impl).

```
argon.node.Primitive[B]                                        (DSLOp.scala:13)
  spatial.node.PrimitiveBlackboxUse[A:Struct, B:Struct]        (Blackbox.scala:37-39)
    spatial.node.VerilogBlackbox[A,B]                          (Blackbox.scala:51)
    spatial.node.SpatialBlackboxUse[A,B]                       (Blackbox.scala:52)
  spatial.node.FetchBlackboxParam[A]                           (Blackbox.scala:60-62)

spatial.node.Control[R]                                        (HierarchyControl.scala:47)
  spatial.node.FunctionBlackbox[R]                             (Blackbox.scala:8)
    spatial.node.EarlyBlackbox[R]                              (Blackbox.scala:11-16)
      spatial.node.DenseTransfer[A, Dram, Local]               (DenseTransfer.scala:34-44)
      spatial.node.SparseTransfer[A, Local]                    (SparseTransfer.scala:27-44)
      spatial.node.FrameTransmit[A, Frame, Local]              (FrameTransmit.scala:26-43)
    spatial.node.GEMMBox[T]                                    (Blackbox.scala:18-35)

spatial.node.EnControl[B]                                      (HierarchyControl.scala:62)
  spatial.node.CtrlBlackboxUse[A:StreamStruct, B:StreamStruct] (Blackbox.scala:40-45)
    spatial.node.VerilogCtrlBlackbox[A, B]                     (Blackbox.scala:54)
    spatial.node.SpatialCtrlBlackboxUse[A, B]                  (Blackbox.scala:55)

argon.node.Alloc[T]                                            (DSLOp.scala:29-31)
  spatial.node.BlackboxImpl[T, A, B]                           (Blackbox.scala:46-49)
    spatial.node.SpatialBlackboxImpl[A:Struct, B:Struct]       (Blackbox.scala:57)
    spatial.node.SpatialCtrlBlackboxImpl[A:StreamStruct, B]    (Blackbox.scala:58)
```

### `FunctionBlackbox` / `EarlyBlackbox`

```scala
abstract class FunctionBlackbox[R:Type] extends Control[R]

abstract class EarlyBlackbox[R:Type] extends FunctionBlackbox[R] {
  override def cchains = Nil
  override def iters = Nil
  override def bodies = Nil
  @rig def lower(old: Sym[R]): R
}
```
(`src/spatial/node/Blackbox.scala:8-16`).

`FunctionBlackbox` is the abstract root for any controller-style blackbox. `EarlyBlackbox` adds the contract that the node is lowered before DSE — its `lower(old: Sym[R])` method re-stages a real `Stream { ... }` controller body with `Fringe*` DMA nodes. The compiler runs `BlackboxLowering(state, lowerTransfers = false)` (`src/spatial/Spatial.scala:103`) and then `BlackboxLowering(state, lowerTransfers = true)` (line 104) to lower these in two phases. After lowering, the original `EarlyBlackbox` symbols are replaced.

`EarlyBlackbox` returns `cchains = Nil, iters = Nil, bodies = Nil` because the controller shape doesn't matter pre-lowering — the lowering function provides the real structure. Concrete subclasses (`DenseTransfer`/`SparseTransfer`/`FrameTransmit`) — see [[30 - Memory Accesses]] for their lowering details.

### `BlackboxImpl[T, A, B]`

```scala
abstract class BlackboxImpl[T:Type, A:Type, B:Type](func: Lambda1[A, B]) extends Alloc[T] {
  override def effects = Effects.Unique
  override def binds = super.binds + func.input
}
```
(`src/spatial/node/Blackbox.scala:46-49`).

The "implementation" handle is an `Alloc[T]` — a typed allocation of a blackbox handle of type `T`. `T` is `SpatialBlackbox[A, B]` for `SpatialBlackboxImpl` (`Blackbox.scala:57`) and `SpatialCtrlBlackbox[A, B]` for `SpatialCtrlBlackboxImpl` (line 58). `Effects.Unique` prevents CSE — two structurally identical `SpatialBlackbox`s declared at different sites must remain distinct because their RTL emission depends on identity. `binds = super.binds + func.input` records that the lambda's input bound symbol is bound at this scope.

### `PrimitiveBlackboxUse[A:Struct, B:Struct]`

```scala
abstract class PrimitiveBlackboxUse[A:Struct, B:Struct] extends Primitive[B] {
  override def effects = Effects.Unique
}
```
(`Blackbox.scala:37-39`).

A primitive-flavored blackbox usage. `Effects.Unique` again prevents CSE. Concrete subclasses:
- `VerilogBlackbox[A, B](in: Bits[A])` (line 51) — references an external Verilog file via `BlackboxConfig`.
- `SpatialBlackboxUse[A, B](bbox: SpatialBlackbox[A, B], in: Bits[A])` (line 52) — references a `SpatialBlackboxImpl` via the `bbox` field.

The `A`/`B` types must be `Struct` (a typeclass over named-field tuples) — the input/output types are flat structs, not streams.

### `CtrlBlackboxUse[A:StreamStruct, B:StreamStruct]`

```scala
abstract class CtrlBlackboxUse[A:StreamStruct, B:StreamStruct](ens: Set[Bit]) extends EnControl[B] {
  override def iters: Seq[I32] = Seq()
  override def cchains = Seq()
  override def bodies = Seq()
  override def effects = Effects.Unique andAlso Effects.Mutable
}
```
(`Blackbox.scala:40-45`).

A controller-flavored blackbox usage — extends `EnControl[B]` (so it has an `ens: Set[Bit]` field via the `Enabled` mixin, `argon/src/argon/node/Enabled.scala:6-21`). `iters/cchains/bodies` are empty: a ctrl blackbox is an opaque inner controller with no Spatial-visible loop structure. `Effects.Unique andAlso Effects.Mutable` — both no-CSE and "this writes something."

The `A`/`B` types must be `StreamStruct` — the input and output are decoupled-field bundles. Combined with the inner-controller flag set at staging time (`src/spatial/lang/Blackbox.scala:93`: `vbbox.asInstanceOf[Sym[_]].rawLevel = Inner`), this enforces "ctrl blackbox is a leaf inner controller communicating via streams."

Concrete subclasses:
- `VerilogCtrlBlackbox[A, B](ens, in)` (line 54) — Verilog-backed controller blackbox.
- `SpatialCtrlBlackboxUse[A, B](ens, bbox, in)` (line 55) — Spatial-backed controller blackbox usage.

### `GEMMBox`

```scala
@op case class GEMMBox[T:Num](
  cchain: CounterChain,
  y, a, b: SRAM2[T], c, alpha, beta: T,
  i, j, mt, nt: I32,
  iters: Seq[I32]
) extends FunctionBlackbox[Void] {
  override def cchains = Seq(cchain -> iters)
  override def bodies = Nil
  override def effects: Effects = Effects.Writes(y)
}
```
(`src/spatial/node/Blackbox.scala:18-35`).

Special-cased GEMM blackbox. Unlike other blackboxes, `GEMMBox` carries a `CounterChain` and `iters` (lines 19, 30, 32-34) — the loop structure is visible to Spatial. `bodies = Nil` (line 33) — no scheduled body; the loop is opaque to Spatial. `Effects.Writes(y)` — the output SRAM is mutated.

This is staged by `Blackbox.GEMM` at `src/spatial/lang/Blackbox.scala:101-119`:
```scala
val PP: I32 = 1 (1 -> 16)
val ctrP = 1 until k par PP
val cchain = CounterChain(Seq(ctrP))
val iters = Seq(boundVar[I32])
stage(GEMMBox(cchain, y, a, b, c, alpha, beta, i, j, mt, nt, iters))
```
The single counter `ctrP` covers the inner `k` dimension with parallelization parameter `PP` (1 to 16, defaulting to 1). The blackbox doesn't lower — codegen pattern-matches on `GEMMBox` and emits a target-specific GEMM core.

### `FetchBlackboxParam[A:Bits]`

```scala
@op case class FetchBlackboxParam[A:Bits](field: java.lang.String) extends Primitive[A] {
  override def effects = Effects.Unique
}
```
(`Blackbox.scala:60-62`).

A primitive that returns the value of a named parameter from the surrounding blackbox's parameter map. `Effects.Unique` to prevent CSE collapsing two reads of the same parameter (their values may differ if the surrounding blackbox is a different instance).

`Blackbox.getParam[T](field)` (`src/spatial/lang/Blackbox.scala:36-38`) is the user-facing entry point. Codegen (`ChiselGenBlackbox.scala:346`) resolves the param at emission time by reading `lhs.bboxInfo.params.get(field)`.

### `BlackboxConfig` and the `bboxInfo` metadata

```scala
case class BlackboxConfig(
  file: String,
  moduleName: Option[String] = None,
  latency: scala.Int = 1,
  pf: scala.Int = 1,                         // pipeline factor / II
  params: Map[String, AnyVal] = Map()
)

case class BlackboxInfo(cfg: BlackboxConfig) extends Data[BlackboxInfo](SetBy.User)
```
(`src/spatial/metadata/blackbox/BlackboxData.scala:1-18`).

Every blackbox node carries a `BlackboxConfig` via the `bboxInfo` metadata accessor (`src/spatial/metadata/blackbox/package.scala:9-13`):
```scala
def getBboxInfo: Option[BlackboxConfig] = metadata[BlackboxInfo](s).map(_.cfg)
def bboxInfo: BlackboxConfig = getBboxInfo.getOrElse(BlackboxConfig(""))
def bboxInfo_=(cfg: BlackboxConfig): Unit = metadata.add(s, BlackboxInfo(cfg))
def bboxII: Double = if (getBboxInfo.isDefined) bboxInfo.pf else if (isSpatialPrimitiveBlackbox) s.II else 1.0
```

The DSL helpers (`src/spatial/lang/Blackbox.scala:17, 29, 72, 92`) set `bboxInfo` immediately after staging:
```scala
val bbox = stage(SpatialBlackboxUse[A,B](this, in))
bbox.asInstanceOf[Sym[_]].bboxInfo = BlackboxConfig("", None, 0, 0, params)
```
For `Spatial*` blackboxes the file and module name are empty (Spatial owns the implementation); for `Verilog*` blackboxes they are the user-supplied path/name. The `params` map is the parameter dictionary that `FetchBlackboxParam` queries.

### Predicate accessors on blackboxes

`src/spatial/metadata/blackbox/package.scala:19-22` defines four boolean predicates over a Sym:
- `s.isCtrlBlackbox` — true for `VerilogCtrlBlackbox`, `SpatialCtrlBlackboxUse`, `SpatialCtrlBlackboxImpl`.
- `s.isBlackboxImpl` — true for any `BlackboxImpl[_,_,_]` (i.e., `SpatialBlackboxImpl` or `SpatialCtrlBlackboxImpl`).
- `s.isBlackboxUse` — true for any `CtrlBlackboxUse[_,_]`.
- `s.isSpatialPrimitiveBlackbox` — true for `SpatialBlackboxImpl` only.

These are queried by passes that need to skip blackboxes (e.g., `MemoryAllocator.scala:36` filters out `isCtrlBlackbox` memories from SRAM allocation; `MemoryAnalyzer.scala:142-143` partitions memories by `isCtrlBlackbox`).

## Implementation

### Effect classification

| Node | Effects |
|---|---|
| `StreamInRead` | `Effects.Writes(mem)` (`HierarchyAccess.scala:80`, via `DequeuerLike`) |
| `StreamInBankedRead` | `Effects.Writes(mem)` (`HierarchyUnrolled.scala:100`) |
| `StreamOutWrite` | `Effects.Writes(mem)` (`HierarchyAccess.scala:117`, via `Writer`) |
| `StreamOutBankedWrite` | `Effects.Writes(mem)` (`HierarchyUnrolled.scala:122`) |
| `SimpleStreamStruct` | inherit `Primitive` (pure); `isTransient = true` |
| `FieldDeq` | inherit `Primitive` (pure) — `isTransient = false`; TODO note that this should be `Effects.Writes(struct)` |
| `FieldEnq` | `Effects.Writes(struct)` |
| `VerilogBlackbox` / `SpatialBlackboxUse` | `Effects.Unique` (`Blackbox.scala:38`) |
| `VerilogCtrlBlackbox` / `SpatialCtrlBlackboxUse` | `Effects.Unique andAlso Effects.Mutable` (`Blackbox.scala:44`) |
| `SpatialBlackboxImpl` / `SpatialCtrlBlackboxImpl` | `Effects.Unique` (`Blackbox.scala:47`) |
| `GEMMBox` | `Effects.Writes(y)` (`Blackbox.scala:34`) |
| `FetchBlackboxParam` | `Effects.Unique` (`Blackbox.scala:61`) |
| `EarlyBlackbox` (`DenseTransfer`/`SparseTransfer`/`FrameTransmit`) | inherit `Control` block-derived effects (typically mutable) |

### Type-class constraints and erasure

Both `Struct` (used by `PrimitiveBlackboxUse`) and `StreamStruct` (used by `CtrlBlackboxUse`) are typeclasses; they're enforced via implicit evidence at staging time. Once staged, the Sym carries the type but the typeclass evidence is erased — passes that need to verify "this is a struct" must re-look up the evidence via `argon.node.StructAlloc` or similar (imported at `src/spatial/node/Blackbox.scala:5`).

### Stream-struct lowering boundary

`SimpleStreamStruct.isTransient = true` (`StreamStruct.scala:9`) means it folds away during analysis: streamification passes resolve `FieldDeq`/`FieldEnq` against `SimpleStreamStruct.elems` and rewire the underlying per-field syms directly into the consuming blackbox or stream surface. After streamification, `SimpleStreamStruct` is gone; only `FieldDeq`/`FieldEnq` and per-field stream nodes remain.

The TODO on `FieldDeq` (lines 14-15) about effects on bound symbols flags the awkwardness: inside a `SpatialCtrl` blackbox body, the `struct` argument is a `boundVar` (the lambda's input), and attaching `Effects.Writes(struct)` to a bound sym confuses the effect system. The current workaround is to rely on the surrounding blackbox's effects to keep the field-deq nodes alive.

### `EnControl` as blackbox base, dual-mixin streams, blackbox metadata

`CtrlBlackboxUse` extending `EnControl[B]` rather than `Pipeline[B]` is deliberate: ctrl blackboxes have an enable but no implicit "body executes at least once" guarantee — they're driven by upstream stream readiness. `iters/cchains/bodies = Seq()` (`Blackbox.scala:41-43`) means the controller surface is empty; consumers must use `isCtrlBlackbox` rather than walking `bodies` to detect blackbox-ness. `rawLevel = Inner` is set at staging only for `VerilogCtrlBlackbox` (`src/spatial/lang/Blackbox.scala:93`); `SpatialCtrlBlackboxUse` relies on flow rules.

Streams' dual-mixin (`LocalMem0` + `RemoteMem`) lets them be accessed locally (in `Accel`) while having remote-style lifetime. `RemoteMem` types like `DRAM` don't expose `__read`/`__write`/`__reset`; streams override that by also extending `LocalMem0`. The idiom is "logically remote, syntactically local."

`BlackboxConfig` (`metadata/blackbox/BlackboxData.scala:6`) carries `file`, `moduleName: Option[String]`, `latency: Int`, `pf: Int` (pipeline factor / II), `params: Map[String, AnyVal]`. `bboxII` (`metadata/blackbox/package.scala:13`) returns `pf` if set, else `s.II` for Spatial primitive blackboxes, else 1.0. `BlackboxUserNodes` (line 17) holds the list of consuming nodes for `treegen`.

## Interactions

**Written by:**
- DSL streaming surface (`StreamIn.value`, `StreamOut.:=`, `StreamStruct.field`, `field_update`).
- DSL blackbox surface (`Blackbox.SpatialPrimitive`, `SpatialController`, `VerilogPrimitive`, `VerilogController`, `GEMM`, `getParam`).
- Streamification / `transform/StreamTransformer` may rewire streams when promoting controllers to streaming form.
- `transform/blackboxLowering1`, `blackboxLowering2` (`src/spatial/Spatial.scala:103-104`) lower `EarlyBlackbox` subclasses (`DenseTransfer`/`SparseTransfer`/`FrameTransmit`) into `Stream { Fringe* }` controller patterns — see [[30 - Memory Accesses]].

**Read by:**
- `traversal/MemoryAllocator.scala:36` and `traversal/MemoryAnalyzer.scala:142-143` filter out `isCtrlBlackbox` memories from banking analysis.
- `traversal/UseAnalyzer.scala:54` treats `isCtrlBlackbox` syms like controllers for use-tracking.
- `codegen/treegen/TreeGen.scala:160-169` emits per-stream listener/push annotations, branching on `isCtrlBlackbox`.
- `codegen/chiselgen/ChiselGenBlackbox.scala:23, 78, 218, 321, 346` reads `bboxInfo.file/moduleName/params` per blackbox kind to emit Chisel-side instantiations.
- `codegen/chiselgen/ChiselGenController.scala:415` skips standard controller emission for `isFSM` and `isCtrlBlackbox`.
- `codegen/chiselgen/ChiselCodegen.scala:485` returns `true` for `isCtrlBlackbox` — they're emitted directly without traversal.
- `transform/FlatteningTransformer.scala:54, 68, 100, 106` — flatten passes guard against flattening controllers that contain or are blackboxes.
- `codegen/chiselgen/ChiselGenBlackbox.scala:346` matches `FetchBlackboxParam(field)` to read the param at emission time.

**Key invariants:**
- Stream allocations have `dims = Seq(I32(1))` — they're rank-1 size-1 memories; banking analysis must skip them (currently handled by the `RemoteMem` branch and `isCtrlBlackbox` filters).
- `StreamIn`/`StreamOut` extend both `LocalMem0` and `RemoteMem` — passes that pattern-match on memory type must handle this dual mixin.
- `FieldDeq.isTransient = false` is explicitly set despite the parent `Primitive`'s default false — preserve this in the Rust IR rewrite.
- `SimpleStreamStruct.isTransient = true` — it folds away during streamification; do not preserve into RTL.
- Every blackbox use (Verilog or Spatial, primitive or ctrl) carries `Effects.Unique` to prevent CSE.
- `CtrlBlackboxUse.iters/cchains/bodies` are all `Seq()` — pattern-matches on `bodies` must treat ctrl blackboxes as opaque controllers.
- `GEMMBox` is the only `FunctionBlackbox` that doesn't extend `EarlyBlackbox` — codegen handles it directly without lowering.
- `FetchBlackboxParam` returns a value at emission time, not at staging time — the `params` map is read by codegen.
- `bboxInfo` metadata is `SetBy.User` (`BlackboxData.scala:15`) — it's user-supplied and not derived; mirroring transformers must preserve it explicitly.
- `VerilogCtrlBlackbox`'s `rawLevel = Inner` is set at staging time (`lang/Blackbox.scala:93`) — `SpatialCtrlBlackboxUse` does not set this directly, leaving it to flow rules.

## HLS notes

`hls_status: rework`. Stream surfaces map to `hls::stream<T>` (`value()` → `stream.read()`, `:=` → `stream.write()`); `AxiStream*Bus` streams use `#pragma HLS INTERFACE axis`. External Verilog blackboxes (`VerilogBlackbox`/`VerilogCtrlBlackbox`) have no HLS equivalent — integration is at the Vivado IP integrator level. Spatial-defined blackboxes (`SpatialBlackboxImpl`/`SpatialCtrlBlackboxImpl`) have Scala bodies and can inline as ordinary HLS functions during the Rust rewrite. `StreamStruct` field-level decoupling needs lowering to per-field `hls::stream` declarations; `SimpleStreamStruct` disappears. `GEMMBox` emits a vendor GEMM IP or user-defined HLS function. `BlackboxConfig.params` maps to per-IP TCL/pragma configuration.

The Rust rewrite needs: a unified `Stream<T>` representation collapsing `StreamIn`/`StreamOut` to a direction bit; `StreamStruct` resolution to per-field streams; a flatter blackbox surface with `kind` × `level` enums replacing the four-class hierarchy; `FetchBlackboxParam` as a string-keyed lookup at codegen time; preserved `EarlyBlackbox` lowering as a separate Rust pass.

See `30 - HLS Mapping/` for the per-construct categorization.

## Open questions

- Q-irn-07 in `[[open-questions-spatial-ir]]` — `FieldDeq.effects` is conservatively pure, but the TODO comment says it should be `Effects.Writes(struct)`. What concrete bug would arise from setting the correct effect, and is the "bound sym inside SpatialCtrl blackbox" issue the only obstacle?
- Q-irn-08 — `FieldEnq` carries a `// TODO: FieldEnq may not actually be used anywhere` comment but is staged by `StreamStruct.field_update` (`lang/StreamStruct.scala:36`). Is `field_update` reachable from any DSL surface API, or is it dead code that the TODO predates?
- Q-irn-09 — `VerilogCtrlBlackbox` sets `rawLevel = Inner` explicitly at staging (`lang/Blackbox.scala:93`); `SpatialCtrlBlackboxUse` does not. Should the Spatial form also set this directly, or is the flow rule that derives it for Spatial blackboxes load-bearing?
- Q-irn-10 — `GEMMBox` is the only `FunctionBlackbox` that doesn't extend `EarlyBlackbox`. Are there plans for `GEMV`/`CONV`/`SHIFT` (currently stubbed `???` in `lang/Blackbox.scala:121-123`) to follow the same direct-codegen pattern, or will they go through `EarlyBlackbox` lowering?
