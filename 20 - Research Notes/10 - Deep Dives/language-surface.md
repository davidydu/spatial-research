---
type: deep-dive
topic: language-surface
source_files:
  - "src/spatial/dsl.scala"
  - "src/spatial/lang/api/StaticAPI.scala"
  - "src/spatial/lang/Aliases.scala"
  - "src/spatial/lang/api/package.scala"
  - "src/spatial/lang/package.scala"
  - "src/spatial/lang/control/Control.scala"
  - "src/spatial/lang/control/CtrlOpt.scala"
  - "src/spatial/lang/control/AccelClass.scala"
  - "src/spatial/lang/control/ForeachClass.scala"
  - "src/spatial/lang/control/ReduceClass.scala"
  - "src/spatial/lang/control/MemReduceClass.scala"
  - "src/spatial/lang/control/NamedClass.scala"
  - "src/spatial/lang/types/Mem.scala"
  - "src/spatial/lang/SRAM.scala"
  - "src/spatial/lang/DRAM.scala"
  - "src/spatial/lang/Reg.scala"
  - "src/spatial/lang/RegFile.scala"
  - "src/spatial/lang/FIFO.scala"
  - "src/spatial/lang/LIFO.scala"
  - "src/spatial/lang/LUT.scala"
  - "src/spatial/lang/LockMem.scala"
  - "src/spatial/lang/Frame.scala"
  - "src/spatial/lang/LineBuffer.scala"
  - "src/spatial/lang/MergeBuffer.scala"
  - "src/spatial/lang/Counter.scala"
  - "src/spatial/lang/CounterChain.scala"
  - "src/spatial/lang/Bus.scala"
  - "src/spatial/lang/Wildcard.scala"
  - "src/spatial/lang/Box.scala"
  - "src/spatial/lang/Latency.scala"
  - "src/spatial/lang/StreamIn.scala"
  - "src/spatial/lang/StreamOut.scala"
  - "src/spatial/lang/StreamStruct.scala"
  - "src/spatial/lang/api/Implicits.scala"
  - "src/spatial/lang/api/MathAPI.scala"
  - "src/spatial/lang/api/MuxAPI.scala"
  - "src/spatial/lang/api/PriorityDeqAPI.scala"
  - "src/spatial/lang/api/MiscAPI.scala"
  - "src/spatial/lang/api/SpatialVirtualization.scala"
  - "src/spatial/lang/api/DebuggingAPI.scala"
  - "src/spatial/lang/api/ControlAPI.scala"
session: 2026-04-23
status: ready-to-distill
feeds_spec:
  - "[[10 - Controllers]]"
  - "[[20 - Memories]]"
  - "[[30 - Primitives]]"
  - "[[50 - Math and Helpers]]"
  - "[[90 - Aliases and Shadowing]]"
---

# Spatial Language Surface — Deep Dive

The "language surface" is the layer that Spatial application writers touch. Everything under `src/spatial/lang/` plus the top-level `src/spatial/dsl.scala`, `SpatialApp.scala`, `Spatial.scala`, `SpatialConfig.scala` composes that surface. This note walks the layering, then zooms into the three conceptually load-bearing mechanisms:

1. The **StaticAPI stack**: four trait layers that incrementally add capability.
2. The **alias stack**: three trait layers (`InternalAliases`, `ExternalAliases`, `ShadowingAliases`) that project internal names into user-visible names.
3. The **`dsl` vs `libdsl` distinction** and the `gen` escape hatch: how Spatial handles the fact that it wants to shadow Scala's `Int`/`Float`/`Boolean` without losing access to the originals.

## Reading log

Files touched in order: `dsl.scala`, `lang/package.scala`, `lang/api/package.scala`, `lang/api/StaticAPI.scala`, `lang/Aliases.scala`, then the control directives (`control/Control.scala`, `CtrlOpt.scala`, `AccelClass.scala`, `ForeachClass.scala`, `ReduceClass.scala`, `MemReduceClass.scala`, `NamedClass.scala`), memory roots (`types/Mem.scala`, `SRAM.scala`, `DRAM.scala`, `Reg.scala`, `RegFile.scala`, `FIFO.scala`, `LIFO.scala`, `LUT.scala`, `LockMem.scala`, `Frame.scala`, `LineBuffer.scala`, `MergeBuffer.scala`, `StreamIn.scala`, `StreamOut.scala`, `StreamStruct.scala`), primitives (`Counter.scala`, `CounterChain.scala`, `Bus.scala`, `Wildcard.scala`, `Box.scala`, `Latency.scala`), then the per-topic API mixins (`Implicits.scala`, `MathAPI.scala`, `MuxAPI.scala`, `PriorityDeqAPI.scala`, `MiscAPI.scala`, `SpatialVirtualization.scala`, `DebuggingAPI.scala`, `ControlAPI.scala`).

## 1. StaticAPI layering

`src/spatial/lang/api/StaticAPI.scala` defines four traits in a strictly additive stack:

```
StaticAPI_Internal
   └─ StaticAPI_External  (extends Internal)
         └─ StaticAPI_Frontend  (extends External)
               └─ StaticAPI_Shadowing  (extends Frontend)
```

`src/spatial/lang/api/StaticAPI.scala:7-36` is the canonical citation for this stack. Each layer has a specific role:

- **`StaticAPI_Internal`** (`StaticAPI.scala:7-22`) — the "inside-the-compiler" view. Mixes in `InternalAliases` (the type/val aliases that let you say `Accel` rather than `spatial.lang.control.Accel`), `SpatialVirtualization`, `Implicits`, and every per-topic API trait: `utils.Overloads`, `ArrayAPI`, `BitsAPI` (from argon), `ControlAPI`, `DebuggingAPI_Internal`, `FileIOAPI`, `MathAPI`, `MiscAPI`, `PriorityDeqAPI`, `MuxAPI`, `ShuffleAPI`, `TensorConstructorAPI`, `TransferAPI`, `TuplesAPI`, `UserData`. The package object `spatial.lang` extends this trait — `src/spatial/lang/package.scala:4` — so anything inside `spatial.lang` sees the full internal API automatically.

- **`StaticAPI_External`** (`StaticAPI.scala:25`) — adds `ExternalAliases`. The extra mixin is the set of user-visible memory/counter/bus aliases (e.g. `DRAM`, `SRAM`, `Counter`, `StreamIn`, `Blackbox`) that only need to be visible to outside callers. Internal callers don't need them because they use the fully-qualified names. `spatial.lang.api` package object extends `ExternalAliases` (`src/spatial/lang/api/package.scala:3`), so code in `spatial.lang.api` sees these aliases but not the frontend SrcCtx/Cast bindings.

- **`StaticAPI_Frontend`** (`StaticAPI.scala:28-33`) — intended for application writers. Adds exactly three forge bindings: `type SrcCtx = forge.SrcCtx`, `lazy val SrcCtx = forge.SrcCtx`, and `type Cast[A,B] = argon.Cast[A,B]`. These three names are the minimum an app writer needs that isn't already exposed via Argon's own `ExternalAliases`. Notably `StaticAPI_Frontend` does **not** shadow any Scala names; this is the form exposed by `libdsl`.

- **`StaticAPI_Shadowing`** (`StaticAPI.scala:35-36`) — the top of the stack. Adds `ShadowingAliases` (which redefine Scala `Int`/`Float`/`Boolean`/etc.) plus `DebuggingAPI_Shadowing`. The `DebuggingAPI_Shadowing` split is important: `DebuggingAPI_Shadowing` at `src/spatial/lang/api/DebuggingAPI.scala:11-12` is defined with a self-type `this: StaticAPI_Shadowing =>`, which means it can only be mixed into a trait that also mixes `StaticAPI_Shadowing`. In practice that means the "shadowed" printArray, printMatrix, printTensor3/4/5, printSRAM1/2/3, approxEql, checkGold, `r"..."` interpolator, and `sleep` helpers are **only visible through `dsl`**, not `libdsl`. The self-type is inherited from `argon.lang.api.DebuggingAPI_Shadowing`.

The upshot: each layer strictly includes the last, and the layer you pick determines which names collide with Scala's defaults.

## 2. Aliases: three layers

`src/spatial/lang/Aliases.scala` mirrors the StaticAPI stack with three alias traits. The Aliases trait stack is orthogonal to but parallel with the StaticAPI trait stack.

### `InternalAliases` (`Aliases.scala:7-52`)

Contains the type/val aliases that would be circular if qualified directly from inside `spatial.lang.*`. Examples:
- `type Mem[A,C[_]] = spatial.lang.types.Mem[A,C]` (`Aliases.scala:8`).
- `type LocalMem0[A,C[T]<:LocalMem0[T,C]] = spatial.lang.types.LocalMem0[A,C]` (`Aliases.scala:10`).
- `lazy val Accel = spatial.lang.control.Accel` (`Aliases.scala:24`) — so that an app writer typing `Accel { ... }` resolves to the `AccelClass` singleton.
- `lazy val Foreach = spatial.lang.control.Foreach`, `Reduce`, `Fold`, `MemReduce`, `MemFold`, `FSM`, `Parallel`, `Pipe`, `Sequential`, `Stream`, `Named` (`Aliases.scala:25-36`).
- The host tensors: `Tensor1` through `Tensor5` aliasing `spatial.lang.host.{Array, Matrix, Tensor3, Tensor4, Tensor5}` (`Aliases.scala:39-48`).
- `DRAMx`/`SRAMx`/`RegFilex`/`LUTx` existential shortcuts: `type DRAMx[A] = spatial.lang.DRAM[A, C forSome { type C[T] }]` (`Aliases.scala:19-22`). Cited in passes that need to match "any-rank DRAM" without caring about the dim constructor.

`InternalAliases` also extends `argon.lang.ExternalAliases` (`Aliases.scala:7`), which is where you pick up argon's basic type aliases (`Bit`, `Text`, `I32`, `Vec`, `Void`, `Fix`, `Flt`, etc.). So `InternalAliases` really is the "everything except shadowing and the user-facing memory names" surface.

### `ExternalAliases` (`Aliases.scala:58-153`)

Builds on `InternalAliases` and adds the memory, primitive, and app-structure aliases. Examples:
- App types: `type SpatialApp = spatial.SpatialApp`, `type SpatialTest = spatial.SpatialTest`, `type SpatialTestbench = spatial.SpatialTestbench` (`Aliases.scala:59-61`).
- Per-rank memory types: `type DRAM1[A] = spatial.lang.DRAM1[A]` … `DRAM5`, plus the companion `lazy val DRAM1 = spatial.lang.DRAM1` etc. (`Aliases.scala:65-76`). Same pattern for `SRAM`, `RegFile`, `LUT`.
- `lazy val Blackbox = spatial.lang.Blackbox` (`Aliases.scala:104`).
- `MergeBuffer`, `LineBuffer`, `FIFO`, `LIFO`, `Reg`, `FIFOReg`, `LockSRAM`, `LockDRAM`, `Lock` (`Aliases.scala:106-128`).
- `lazy val ArgIn`, `lazy val ArgOut`, `lazy val HostIO` (`Aliases.scala:129-131`).
- `StreamIn`, `StreamOut`, `Counter`, `CounterChain`, `Wildcard`, `StreamStruct`, `ForcedLatency` (`Aliases.scala:133-152`).

Why split `External` from `Internal`? So that `argon.lang` itself can be parameterized against a "compiler-internal view" without accidentally pulling in Spatial-specific memory names. Argon is the staging framework; Spatial is a DSL built on top of it; the separation matters because argon is supposed to be reusable.

### `ShadowingAliases` (`Aliases.scala:156-198`)

This is where Spatial does something deliberately aggressive: it **redefines Scala's primitive type names** at the type level. Examples:
- `type Char = argon.lang.Fix[FALSE,_8,_0]` (`Aliases.scala:157`).
- `type Byte = argon.lang.Fix[TRUE,_8,_0]`, `Short`, `Int = Fix[TRUE,_32,_0]`, `Long = Fix[TRUE,_64,_0]` (`Aliases.scala:158-161`).
- `type Half = argon.lang.Flt[_11,_5]`, `Float = Flt[_24,_8]`, `Double = Flt[_53,_11]` (`Aliases.scala:163-165`).
- `type Boolean = argon.lang.Bit` (`Aliases.scala:167`).
- `type String = argon.lang.Text` (`Aliases.scala:168`).
- `type Label = java.lang.String` (`Aliases.scala:169`) — this is the escape hatch: if you need the Scala/Java string type, use `Label`.
- `type Array[A] = spatial.lang.host.Array[A]` plus `lazy val Array = spatial.lang.host.Array` (`Aliases.scala:171-172`).
- `type Matrix[A] = spatial.lang.host.Matrix[A]` plus companion (`Aliases.scala:173-174`).
- `type Tuple2[A,B] = argon.lang.Tup2[A,B]` (`Aliases.scala:176`).
- `type Unit = argon.lang.Void` (`Aliases.scala:182`).
- AxiStream256 alias hoisted up (`Aliases.scala:178-180`) — unclear why the 256-bit variant is specifically promoted here while 64 and 512 are not (see open question Q-010).

Behind all of this is a nested `object gen` (`Aliases.scala:184-197`) — the escape hatch. It re-exposes the shadowed Scala names:
- `type Char = scala.Char`, `type Byte = scala.Byte`, …, `type Int = scala.Int`, …, `type Boolean = scala.Boolean`, `type String = java.lang.String`, `type Array[A] = scala.Array[A]`, `lazy val Array = scala.Array`, `type Unit = scala.Unit`.

So inside `dsl`-scope code, `Int` is a staged `Fix[TRUE,_32,_0]`, and `gen.Int` is `scala.Int`. Similarly `gen.Array` is a real Scala array (useful for staging-time metadata collection). The `libdsl` view doesn't have `gen` because it doesn't shadow anything in the first place.

## 3. `dsl` vs `libdsl`

The split is declared in `src/spatial/dsl.scala`:

```scala
trait SpatialDSL extends lang.api.StaticAPI_Frontend                  // dsl.scala:6

object libdsl extends SpatialDSL { ... }                              // dsl.scala:9-26

object dsl extends SpatialDSL with lang.api.StaticAPI_Shadowing { ... } // dsl.scala:29-46
```

**Shared (`trait SpatialDSL`)**: `StaticAPI_Frontend`. No Scala shadowing.

**`libdsl` object**: inherits `SpatialDSL` only. Adds the three macro annotation classes: `@spatial` (wraps `AppTag("spatial", "SpatialApp")`), `@struct` (wraps `StagedStructsMacro.impl`), `@streamstruct` (wraps `StagedStreamStructsMacro.impl`) — `dsl.scala:15-25`.

**`dsl` object**: inherits `SpatialDSL with lang.api.StaticAPI_Shadowing` — `dsl.scala:29`. This is where shadowing is opt-in. It re-declares the same three macro annotations (`dsl.scala:35-45`) because Scala annotation classes are position-specific and cannot be inherited.

Practical consequences:

- `import spatial.dsl._` means `Int`, `Float`, `Boolean`, `String`, `Array`, `Matrix`, `Unit`, `Tuple2` refer to staged Spatial types. If you need the Scala originals, say `spatial.dsl.gen.Int`.
- `import spatial.libdsl._` leaves Scala's names alone. To get a staged 32-bit signed int, you'd spell it `I32`. The `@spatial` macro annotation still works because it's defined in the same object.
- Behavior-only: some helpers are **only** reachable through `dsl`. Examples are the `printArray`/`printMatrix`/`printTensor*` family, `sleep`, `checkGold`, and `r"..."` interpolator in `DebuggingAPI_Shadowing` (`src/spatial/lang/api/DebuggingAPI.scala:11-13` plus implementations below). Since `DebuggingAPI_Shadowing` has `this: StaticAPI_Shadowing =>`, `libdsl` cannot pull it in. So the `dsl` vs `libdsl` choice is not purely about visibility — it's also about which convenience APIs are available.

Why the split at all? Spatial is a DSL, not a replacement for Scala. Library authors who want to build libraries on top of Spatial primitives probably don't want their `Int`s to be staged, because they still want to use Scala's integer operations at compile time (loop counters, array indexing, meta-programming). They import `libdsl` and say `I32` when they mean "staged 32-bit int". App authors who are writing the actual accelerator code want the concise syntax, so they import `dsl` and get `Int`-as-staged.

## 4. How control directives tie together

A separate but related piece: the `Directives` base class wires schedule/II/POM/MOP/NoBind/haltIfStarved modifiers and the `CtrlOpt.set` metadata propagation. This drops cleanly into the language surface because user-facing `Pipe`, `Stream`, `Sequential` are instances of it.

- `abstract class Directives(val options: CtrlOpt)` (`Control.scala:9-20`) provides lazy val builders `Foreach`, `Reduce`, `Fold`, `MemReduce`, `MemFold` that take `options` as the initial `CtrlOpt`. So `Pipe.II(3).Foreach(0 until N){ ... }` is really `new Pipe(..., ii = Some(3)).Foreach.apply(ctr){ ... }`.
- `case class CtrlOpt(...)` (`CtrlOpt.scala:8-27`) is the aggregator. `CtrlOpt.set[A](x: Sym[A])` is where metadata is propagated onto the staged control node (`CtrlOpt.scala:18-26`): `x.name`, `x.userSchedule`, `x.userII`, `x.unrollAsMOP`/`unrollAsPOM`, `x.shouldNotBind`, `x.haltIfStarved`.
- `Pipe`, `Stream`, `Sequential` classes (`Control.scala:22-57`) each construct a default `CtrlOpt` preset for their respective schedule (`Pipelined`, `Streaming`, `Sequenced`) and expose builders (`II`, `POM`, `MOP`, `NoBind`, `haltIfStarved`) that return new instances with updated config.
- The singleton objects `Pipe`/`Stream`/`Sequential`/`Accel`/`Foreach`/`Reduce`/`Fold`/`MemReduce`/`MemFold` (`Control.scala:63-72`) are pre-configured class instances, so `Foreach(ctr){...}` works without a `new`.

## 5. Escape-hatch nesting: `dsl`, `libdsl`, `gen`

Putting the three together, there's a three-tier nesting:

```
spatial.dsl           ← apps. Scala Int = Spatial Fix[TRUE,_32,_0]. Has DebuggingAPI_Shadowing helpers.
spatial.dsl.gen       ← escape hatch inside dsl. gen.Int = scala.Int, gen.Array = scala.Array, ...
spatial.libdsl        ← libraries. Scala Int = scala.Int. No shadowing. No DebuggingAPI_Shadowing.
```

It reads as "start at `dsl`, fall through to `dsl.gen` when you need plain Scala, drop down to `libdsl` if you're writing infrastructure that must not shadow". Unfortunately the `gen` object is hidden *inside* `ShadowingAliases` (`Aliases.scala:184`), not in `dsl` itself, so it's only reachable through `spatial.dsl.gen` because `dsl` extends the trait. You cannot reach `gen` from `libdsl`.

## Observations

### StaticAPI stack is actually split into four layers and the reason matters

The stack is not (Internal, External, Frontend) with Shadowing as a free add-on. Shadowing has to come *after* Frontend because `StaticAPI_Shadowing` extends `StaticAPI_Frontend` (`StaticAPI.scala:35`) — you can't have shadowing without the frontend SrcCtx bindings because the debugging API uses `SrcCtx` (the `@virtualize @api` methods in DebuggingAPI inherit implicit SrcCtx from the frontend).

### `InternalAliases` extends argon's `ExternalAliases`, not its `InternalAliases`

`Aliases.scala:7`: `trait InternalAliases extends argon.lang.ExternalAliases`. So Spatial's "internal" view sees argon's "external" alias set. This is a subtle but important asymmetry: Spatial extends the frame that argon exposes externally because argon's `InternalAliases` would pull in things like `CustomBitWidths` directly which Spatial doesn't want duplicated. Argon's external aliases include the numeric type names (`I32`, `Bit`, `Text`, etc.) that every Spatial piece needs.

### `ShadowingAliases` extends `ExternalAliases`, not `InternalAliases`

This means Shadowing is strictly additive over the user-visible surface. If a name is visible through `libdsl` (which uses `ExternalAliases`), it's also visible through `dsl` (which uses `ShadowingAliases`). The only things `ShadowingAliases` adds are the Scala-name overrides.

### The `gen` object lives inside `ShadowingAliases`

`Aliases.scala:184-197` puts the `object gen` declaration inside the trait, not in `dsl.scala`. So `gen` is inherited along with the shadowing aliases. Consequence: if a downstream DSL defines its own Shadowing trait and mixes it in, it automatically gets `gen` too. But it cannot customize what's in `gen` without re-declaring the object (which would shadow the trait's version).

### `Named(name)` is a `Directives` instance

`src/spatial/lang/control/NamedClass.scala:4-9` makes `Named("foo")` an instance of `Directives` with a pre-set name. That's why you can write `Named("foo").Foreach(...)` to stage a controller with the name "foo" attached — the builder methods all resolve through `Directives.lazy val Foreach`.

### User-visible escape-hatch chain

If an app writer needs `scala.Int`:
- Through `dsl`: use `spatial.dsl.gen.Int` (preferred).
- Through `libdsl`: `scala.Int` is already in scope because `libdsl` doesn't shadow.
- Label is a manual alternative for Strings: `Label = java.lang.String` at `Aliases.scala:169`.

### The `Label` alias is a one-off shortcut

There's no `Chr = scala.Char` or `Flt = scala.Float` equivalent to `Label`. Only `Label` gets a direct alias from the root of `ShadowingAliases`. The other Scala types are only accessible via `gen`. `Label` appears this way because the strings used to *name* things (e.g. `Reg[A](zero, "regName")`) are Scala strings, and `String` itself has been shadowed. See open question Q-011.

### AxiStream256 gets a fast-path alias in `ShadowingAliases`

`Aliases.scala:178-180` promotes `AxiStream256`, `AxiStream256Bus`, and `AxiStream256Data` into the shadowing view. This is likely because AxiStream256 is the default bus width for DRAM transfers, but it's inconsistent with AxiStream64 and AxiStream512 which are only reachable through `ExternalAliases`. See open question Q-012.

## Distillation plan

- **`10 - Controllers.md`** — pulls from §4 (control directives), plus `control/*.scala` citations listed in frontmatter.
- **`20 - Memories.md`** — Mem typeclass hierarchy from `types/Mem.scala`, SRAM tuning hints from `SRAM.scala`, all the other memory files.
- **`30 - Primitives.md`** — Counter/CounterChain/Wildcard/Bus/Pin from those files.
- **`50 - Math and Helpers.md`** — pulls `api/MathAPI.scala`, `api/MuxAPI.scala`, `api/PriorityDeqAPI.scala`, `api/MiscAPI.scala`, `Latency.scala`.
- **`90 - Aliases and Shadowing.md`** — the whole §1-3 and §5 story of this note.

## Open questions

- Q-007 (filed today): What is the runtime-behavior-only difference between app code written using `dsl` vs `libdsl`? The stack says shadowing is additive on names, but the `DebuggingAPI_Shadowing` self-type means library code (using `libdsl`) cannot invoke `printArray`/`sleep`/`r"..."` directly. Is this an intentional restriction or historical accident?
- Q-008: `AxiStream256` is aliased into `ShadowingAliases` but `AxiStream64`/`AxiStream512` are not. Why the asymmetry?
- Q-009: `Named(name).Reduce`, `Named(name).Foreach`, `Named(name).Fold`, `Named(name).MemReduce`, `Named(name).MemFold` are not declared explicitly in `NamedClass`. Yet they must work through the `Directives` parent's `lazy val Foreach`/etc. that use the shared `options` (which only has `name` set, nothing else). Verify: does this compose cleanly in real apps?
- Q-010: What's the sharing contract with `argon.lang.ShadowingAliases`? Argon defines its own `ShadowingAliases` (`argon/src/argon/lang/Aliases.scala:178-180`) but it's empty. Is the empty trait intended as a hook for downstream DSLs to fill, or a vestigial remnant?
- Q-011: Why is `Label = java.lang.String` promoted to the root of `ShadowingAliases` while other Scala types are only in `gen`?
- Q-012: `StaticAPI_Frontend` introduces `type Cast[A,B] = argon.Cast[A,B]`. Why is this in the frontend layer rather than `ExternalAliases`?
