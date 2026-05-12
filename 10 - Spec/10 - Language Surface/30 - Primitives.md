---
type: spec
concept: primitives
source_files:
  - "src/spatial/lang/Counter.scala:1-29"
  - "src/spatial/lang/CounterChain.scala:1-13"
  - "src/spatial/lang/Wildcard.scala:1-3"
  - "src/spatial/lang/Bus.scala:1-87"
  - "src/spatial/lang/Box.scala:1-7"
  - "src/spatial/lang/api/Implicits.scala:73,77"
source_notes:
  - "[[language-surface]]"
hls_status: clean
depends_on:
  - "[[10 - Controllers]]"
status: draft
---

# Primitives

## Summary

Primitives are the scalar-level building blocks of the Spatial DSL that do not fit cleanly into the Memory or Controller categories: **`Counter`** and **`CounterChain`** (iteration descriptors consumed by `Foreach`, `Reduce`, `MemReduce`), **`Wildcard`** (the `*` sentinel used for full-axis slicing and forever-loops), **`Pin`** (named external I/O wire), the **`Bus`** family (interface descriptors for streaming ports), and **`Box`** (helper base class for typed self-referencing refs). Each compiles down to a small, fixed set of IR nodes: `CounterNew`, `CounterChainNew`, `ForeverNew`, and bus objects that are consumed by `StreamIn`/`StreamOut`/DRAM transfer lowering.

## Syntax / API

```scala
// Counters
val c1 = Counter(0, N, 1, 1)               // src/spatial/lang/Counter.scala:15-23
val c2 = Counter.from(series)              // src/spatial/lang/Counter.scala:25-28
val cc = CounterChain(Seq(c1, c2))         // src/spatial/lang/CounterChain.scala:12

// Wildcard
Foreach(*){ _ => ... }                     // Wildcard implicit → ForeverNew
s(i, *)                                    // Memory full-axis slice

// Bus descriptors (non-staged)
val b1 = Bus("valid", "d0", "d1", "d2")    // src/spatial/lang/Bus.scala:19-20
val b2 = AxiStream64Bus(tid = 0, tdest = 0)// Bus.scala:34
val b3 = AxiStream256Bus(0, 0)             // Bus.scala:42
val b4 = AxiStream512Bus(0, 0)             // Bus.scala:50
val b5 = FileBus[Int]("in.csv")            // Bus.scala:63
val b6 = FileEOFBus[MyStruct]("eof.csv")   // Bus.scala:68
val in = StreamIn[Int](b5)                 // Bus feeds StreamIn/StreamOut

// DRAM-side bus objects (singletons or case classes)
BurstCmdBus                                // Bus.scala:78
BurstAckBus                                // Bus.scala:79
BurstDataBus[Int]()                        // Bus.scala:80
BurstFullDataBus[Int]()                    // Bus.scala:81
GatherAddrBus                              // Bus.scala:83
GatherDataBus[Int]()                       // Bus.scala:84
ScatterCmdBus[Int]()                       // Bus.scala:86
ScatterAckBus                              // Bus.scala:87
```

## Semantics

### Counter

`Counter[A:Num]` (`src/spatial/lang/Counter.scala:9`) is an `@ref class` wrapping a `FixedPointRange` runtime type. The type parameter `A` is the index type (typically `I32`). Two constructors:

```scala
@api def apply[A:Num](start: A, end: A, step: A = null, par: I32 = I32(1)): Counter[A] = {
  val stride: A = Option(step).getOrElse(Num[A].one)
  stage(CounterNew[A](start, end, stride, par))
}
```

Source: `Counter.scala:15-23`. Defaults: `step = null` folds to `Num[A].one`; `par = I32(1)`. The `stride.getOrElse` pattern means `null` is the sentinel for "unit step" — a subtle Scala idiom that could surprise a Rust port.

`Counter.from(series)` (`Counter.scala:25-28`) destructures a `Series[A]` (an argon range type) into `(start, end, step, par)` and constructs a Counter. This is the bridge used by the `SeriesToCounter` implicit in `api/Implicits.scala:77`, which lets users write `0 until N` and get a `Counter[I32]` via `Series` → `Counter` conversion.

Each counter carries a parallelization factor `par` that controls how many parallel lanes are unrolled in the enclosing controller. `ctrParOr1` (used by `ForeachClass.scala:29`) extracts this value with a fallback of 1.

### CounterChain

`CounterChain` (`src/spatial/lang/CounterChain.scala:7-13`) is a tiny wrapper:

```scala
@ref class CounterChain extends Top[CounterChain] with Ref[Array[Range],CounterChain] { ... }
object CounterChain {
  @api def apply(ctrs: Seq[Counter[_]]): CounterChain = stage(CounterChainNew(ctrs))
}
```

It wraps a sequence of `Counter[_]` (existentially typed because different counters may have different numeric types) into a single staged symbol. Controllers like `ForeachClass.apply` call `CounterChain(ctrs)` to package their counters into an IR node before staging the controller (`ForeachClass.scala:28`).

### Wildcard

`class Wildcard` (`src/spatial/lang/Wildcard.scala:3`) is a three-line Scala class — literally just a sentinel type. Its role is two-fold:

1. **Memory slicing**: `Mem2.apply(row: Idx, col: Rng)` etc. (`types/Mem.scala:139-145`) take `Rng` arguments; a `Wildcard` is converted via an extension `*.toSeries` that covers the full axis.
2. **Forever loop**: `api/Implicits.scala:73` defines an implicit conversion `wildcardToForever(w: Wildcard): Counter[I32] = stage(ForeverNew())`. That's how `Foreach(*){ _ => ... }` compiles: the `*` is a `Wildcard`, gets implicitly promoted to a `Counter[I32]` backed by a `ForeverNew` IR node.

`MiscAPI.scala:11` exposes `def * = new Wildcard` so users can type `*` and get a `Wildcard` instance.

### Pin and Bus

`Pin(name: String)` (`src/spatial/lang/Bus.scala:9-11`) is a plain case class — not an IR node. It's a named wire identifier used when constructing `PinBus` instances.

`abstract class Bus extends Mirrorable[Bus]` (`Bus.scala:13-16`) has two abstract-ish members: `@rig def nbits: Int` (the bus width in bits), and `def mirror(f: Tx) = this` (identity mirror — buses are immutable value objects that don't transform under IR rewrites).

Bus is also *not* an IR node; it's a value class threaded through `StreamIn(bus)`/`StreamOut(bus)` and the DRAM transfer nodes. `StreamInNew(bus)` (`StreamIn.scala:27`) carries the bus as a constructor parameter, and the codegen reads it to emit the correct port declarations.

### Bus variants

Concrete bus types fall into three categories:

**Scalar/user-defined buses** (`Bus.scala:18-26`):
- `Bus.apply(valid: Pin, data: Pin*)` → `PinBus(valid, data)`, a general multi-wire bus.
- `PinBus(valid: Pin, data: Seq[Pin])` — `nbits = data.length` (one bit per data pin).

**AXI-Stream buses** (`Bus.scala:28-50`):
- `AxiStream64` / `AxiStream256` / `AxiStream512` are `@struct` case classes carrying `(tdata, tstrb, tkeep, tlast, tid, tdest, tuser)` at 64/256/512-bit data widths. Each has a companion `AxiStreamNData` helper (`Bus.scala:30-32`, `:38-41`, `:46-48`) that constructs the struct with zero-valued auxiliary fields.
- `AxiStream64Bus(tid, tdest)`, `AxiStream256Bus(tid, tdest)`, `AxiStream512Bus(tid, tdest)` are the Bus-typed wrappers (`nbits = 64/256/512`).

**DRAM transfer buses** (`Bus.scala:78-87`):
- `BurstCmdBus` (singleton) and `BurstAckBus` (singleton) — `DRAMBus[BurstCmd]` and `DRAMBus[Bit]`. Read by `DenseTransfer` lowering.
- `BurstDataBus[A]()`, `BurstFullDataBus[A]()` (data + last-bit) — templated on the element type.
- `GatherAddrBus` (singleton), `GatherDataBus[A]()` — for sparse gather lowering.
- `ScatterCmdBus[A]()`, `ScatterAckBus` (singleton) — for sparse scatter lowering.

All five `DRAMBus[A]` variants inherit `nbits: Int = Bits[A].nbits` from `abstract class DRAMBus[A:Bits] extends Bus` (`Bus.scala:57`).

**File-backed buses** (`Bus.scala:63-76`):
- `FileBus[A:Bits](fileName)` reads one element (or one row of struct fields) per CSV line.
- `FileEOFBus[A:Bits](fileName)(implicit state: State)` performs a construction-time check: the struct type's last field must be `Bit`, which will be interpreted as EOF. If not, `state.logError()` is called (`Bus.scala:69-74`). This is a rare case of a DSL-layer constructor doing shape validation on types.

Both `FileBus` and `FileEOFBus` inherit from `Bus` directly — they are not `DRAMBus[A]` because the file is read from the host filesystem, not via DRAM bursts.

### BurstCmd and IssuedCmd structs

Two struct types defined alongside the buses:

```scala
@struct case class BurstCmd(offset: I64, size: I32, isLoad: Bit)   // Bus.scala:52
@struct case class IssuedCmd(size: I32, start: I32, end: I32)      // Bus.scala:53
```

These are the payload types carried on `BurstCmdBus` and as internal fringe-side tracking structs, respectively. They are Argon `@struct` case classes, so they stage as `SimpleStruct` nodes when referenced in user code.

### Box

`abstract class Box[A](implicit ev: A <:< Box[A]) extends Top[A] with Ref[Any, A]` (`src/spatial/lang/Box.scala:5`) is a minimal helper base class used by types that need to be self-referencing refs. `__neverMutable = false` is overridden to allow mutation. Memory classes like `DRAM` do not extend `Box` directly, but the pattern of F-bounded polymorphism (`A <:< Box[A]`) mirrors how `DRAM[A,C]` and `SRAM[A,C]` use their own `evMem: C[A] <:< DRAM[A,C]` evidence.

## Implementation

### Implicit conversions on primitives

`api/Implicits.scala:73` and `:77` define the two key implicit conversions involving primitives:

```scala
@api implicit def wildcardToForever(w: Wildcard): Counter[I32] = stage(ForeverNew())
@api implicit def SeriesToCounter[S:BOOL,I:INT,F:INT](x: Series[Fix[S,I,F]]): Counter[Fix[S,I,F]] = Counter.from(x)
```

The first enables `Foreach(*)`; the second enables `Foreach(0 until N)`. Both are `@api`, meaning they run in staging context and can stage IR nodes.

### Bus is a non-IR value

Importantly, `Bus`/`Pin` are *not* staged. They are Scala values (case classes with `Mirrorable[Bus].mirror = this`). `StreamIn(bus)` / `StreamOut(bus)` / `FrameHostNew` carry them as metadata payloads. When the compiler mirrors a node during a transform, the bus passes through unchanged.

### `AxiStream64Data.apply` pattern

The `AxiStreamNData` helper objects (`Bus.scala:30-32`, `:38-41`, `:46-48`) are `@stateful` so they can call `Bits[U8].from(0)` etc., which requires a staging state. They take just `tdata` and zero-fill the other struct fields. Useful boilerplate helpers for app writers who only care about `tdata`.

### `FileEOFBus` struct shape check

`FileEOFBus[A:Bits]` (`Bus.scala:68-75`) pattern-matches on `Type[A]`:

```scala
Type[A] match {
  case a:Struct[_] if a.fields.last._2 == Type[Bit] =>
  case a =>
    error(s"EOFBus must have struct type with last field in Bit. Got type ${a}")
    state.logError()
}
```

This is a construction-time contract — the bus type must be a struct whose last field is `Bit` — enforced at DSL layer before any IR staging happens. Other bus types do not validate their types this way.

## Interactions

- **`spatial.node.*`**: `CounterNew`, `CounterChainNew`, `ForeverNew` are the only IR nodes staged directly from this surface. Bus objects are passed as constructor args to `StreamInNew`, `StreamOutNew`, `DRAMHostNew`, `FrameHostNew`, and the transfer nodes.
- **`ForeachClass`/`ReduceClass`/`MemReduceClass`**: all call `CounterChain(ctrs)` to build the iteration descriptor.
- **Unroller**: reads each counter's `par` to determine lane count via `ctrParOr1`.
- **Codegens**: AXI-Stream buses are emitted as SystemVerilog interfaces by chiselgen; file-buses open a CSV at runtime in cppgen/scalagen for host-side simulation.

## HLS notes

`hls_status: clean`. `Counter` maps to a C++ loop index with pragmas (`#pragma HLS UNROLL factor=par`). `CounterChain` → nested for loops. `Wildcard`/`ForeverNew` → `while(true)` or `for(;;)`. `PinBus` → GPIO-style port declarations. `AxiStream*Bus` → `hls::stream<ap_axiu<N,...>>` with `#pragma HLS INTERFACE axis`. `BurstCmdBus`/`BurstAckBus` etc. → implementation detail of the memory controller — not user-facing in HLS; the Rust rewrite should probably elide these and use a higher-level burst-transfer abstraction. `FileBus`/`FileEOFBus` are host-side only; in HLS they'd be replaced by testbench file I/O.

## Open questions

- See `[[20 - Open Questions]]` Q-015 (counter step default `null` → `Num.one` convention — how to express in Rust?), Q-016 (why is only `AxiStream256Bus` promoted to `ShadowingAliases` but not `AxiStream64`/`AxiStream512`?).
