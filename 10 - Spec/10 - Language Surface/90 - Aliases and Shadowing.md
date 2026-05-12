---
type: spec
concept: aliases-and-shadowing
source_files:
  - "src/spatial/lang/Aliases.scala:1-199"
  - "src/spatial/lang/api/StaticAPI.scala:1-37"
  - "src/spatial/dsl.scala:1-46"
  - "src/spatial/lang/api/package.scala:1-3"
  - "src/spatial/lang/package.scala:1-5"
  - "src/spatial/lang/api/DebuggingAPI.scala:9-13"
  - "argon/src/argon/lang/Aliases.scala"
source_notes:
  - "[[language-surface]]"
hls_status: rework
depends_on:
  - "[[10 - Controllers]]"
  - "[[20 - Memories]]"
  - "[[30 - Primitives]]"
status: draft
---

# Aliases and Shadowing

## Summary

Spatial's user-facing surface is assembled from three layered alias traits — `InternalAliases`, `ExternalAliases`, `ShadowingAliases` (`src/spatial/lang/Aliases.scala`) — composed with four `StaticAPI` layers (`StaticAPI_Internal`, `StaticAPI_External`, `StaticAPI_Frontend`, `StaticAPI_Shadowing`, `src/spatial/lang/api/StaticAPI.scala`). The two stacks are orthogonal: the alias traits supply *names* (type and val aliases); the StaticAPI traits supply *behavior* (`mux`, `Foreach`, `printArray`, etc.). The top-level entry `spatial.dsl` (`src/spatial/dsl.scala:29`) mixes both top layers and additionally redefines Scala's primitive types (`Int`, `Float`, `Boolean`, `String`, `Array`, `Unit`, `Tuple2`) as their staged Spatial counterparts. The `gen` escape hatch (`Aliases.scala:184-197`) reintroduces `scala.Int`, `scala.Array`, etc. for code that needs Scala-native types inside a `dsl` import scope. A separate `libdsl` (`src/spatial/dsl.scala:9-26`) exposes the same DSL without shadowing — for library writers whose host-side metaprogramming wants to keep using Scala's native types. This entry is `hls_status: rework` because shadowing is a Scala-namespace mechanism with no direct HLS analogue.

## Syntax / API

```scala
// Application code (with shadowing)
import spatial.dsl._

@spatial object MyApp extends SpatialApp {
  val x: Int = 42                 // staged Fix[TRUE,_32,_0]; Aliases.scala:160
  val s: String = "hi"            // staged Text;             Aliases.scala:168
  val a: Array[Int] = Array(1,2)  // host Array[I32];         Aliases.scala:171-172
  val r: Float = 3.14f.to[Float]  // staged Flt[_24,_8];      Aliases.scala:164

  val n: gen.Int = 5              // scala.Int;                Aliases.scala:188
  val name: Label = "mem"         // java.lang.String;         Aliases.scala:169
}

// Library code (no shadowing)
import spatial.libdsl._
val n: Int = 5                  // scala.Int (unchanged)
val a: I32 = 5.to[I32]          // explicit staged spelling
```

## Semantics

### Three alias layers

`src/spatial/lang/Aliases.scala` defines three traits in a strict subtype chain. Each introduces a strictly larger set of names than its parent.

**`InternalAliases`** (`Aliases.scala:7-52`) extends `argon.lang.ExternalAliases` (`Aliases.scala:7`) — note this is argon's *external*, not internal, view, because Spatial's internal code wants the user-facing argon names (`I32`, `Bit`, `Text`, etc.) but not argon's compiler scaffolding. Adds the `Mem`/`LocalMem`/`LocalMem0..5`/`RemoteMem` typeclass aliases (`Aliases.scala:8-17`); existential shorthands `DRAMx`/`SRAMx`/`RegFilex`/`LUTx` (`Aliases.scala:19-22`); the control directive companions `Accel`, `Foreach`, `Reduce`, `Fold`, `MemReduce`, `MemFold`, `FSM`, `Parallel`, `Pipe`, `Sequential`, `Stream`, `Named` (`Aliases.scala:24-36`); and the host tensor aliases `Tensor1..5`, `CSVFile`, `BinaryFile` (`Aliases.scala:39-50`). The `lang` package object extends `StaticAPI_Internal` (`src/spatial/lang/package.scala:4`) which mixes in `InternalAliases`, so any code in `spatial.lang.*` sees this surface for free.

**`ExternalAliases`** (`Aliases.scala:58-153`) extends `InternalAliases` and adds the user-visible memory, primitive, and app-structure names: `SpatialApp`/`SpatialTest`/`SpatialTestbench` (`Aliases.scala:59-61`); the full DRAM/SRAM/RegFile/LUT family with per-rank type aliases and companion `lazy val`s (`Aliases.scala:65-102`); `Frame`, `Blackbox` (`Aliases.scala:78-80, 104`); `MergeBuffer`, `LineBuffer`, `FIFO`, `LIFO`, `Reg`, `FIFOReg`, `LockSRAM`, `LockDRAM`, `Lock` (`Aliases.scala:106-128`); `ArgIn`, `ArgOut`, `HostIO` (`Aliases.scala:129-131`); `StreamIn`, `StreamOut`, `Counter`, `CounterChain`, `Wildcard`, `StreamStruct`, `ForcedLatency` (`Aliases.scala:133-152`). The `spatial.lang.api` package object extends `ExternalAliases` (`src/spatial/lang/api/package.scala:3`).

**`ShadowingAliases`** (`Aliases.scala:156-198`) extends `ExternalAliases` and aggressively redefines Scala's primitive type names at the type level:

| Scala name | Spatial type | Line |
|---|---|---|
| `Char` | `Fix[FALSE,_8,_0]` | `:157` |
| `Byte`/`Short`/`Int`/`Long` | `Fix[TRUE,_8/16/32/64,_0]` | `:158-161` |
| `Half`/`Float`/`Double` | `Flt[_11,_5]`/`Flt[_24,_8]`/`Flt[_53,_11]` | `:163-165` |
| `Boolean` | `argon.lang.Bit` | `:167` |
| `String` | `argon.lang.Text` | `:168` |
| `Array[A]` (+ companion) | `spatial.lang.host.Array[A]` | `:171-172` |
| `Matrix[A]` (+ companion) | `spatial.lang.host.Matrix[A]` | `:173-174` |
| `Tuple2[A,B]` | `argon.lang.Tup2[A,B]` | `:176` |
| `Unit` | `argon.lang.Void` | `:182` |

A single Scala-native escape sneaks into the root: `type Label = java.lang.String` (`Aliases.scala:169`). It exists because once `String` shadows to `Text`, an app writer who needs a host-side string (e.g. `Reg[I32](0, "regName")`) needs *some* name for `java.lang.String`. Other Scala types get no equivalent root-level alias — they're only reachable through `gen` (Q-lang-05).

`Aliases.scala:178-180` also promotes `AxiStream256`, `AxiStream256Bus`, `AxiStream256Data` into the `ShadowingAliases` layer — asymmetric with `AxiStream64`/`AxiStream512` (Q-lang-04).

**The `gen` escape hatch.** Nested inside `ShadowingAliases` is `object gen` (`Aliases.scala:184-197`):

```scala
object gen {
  type Char = scala.Char; type Byte = scala.Byte; type Short = scala.Short
  type Int = scala.Int; type Long = scala.Long
  type Float = scala.Float; type Double = scala.Double
  type Boolean = scala.Boolean
  type String = java.lang.String
  type Array[A] = scala.Array[A]; lazy val Array = scala.Array
  type Unit = scala.Unit
}
```

So `spatial.dsl.gen.Int` is `scala.Int`, even though `spatial.dsl.Int` is staged. Note `Matrix` and `Tuple2` are not in `gen` — only the genuine Scala/Java primitives are reintroduced. `gen` lives inside `ShadowingAliases`, not inside `dsl`, so it is inherited automatically; but `libdsl` cannot reach it (and doesn't need to, since names there are unshadowed already).

### Four StaticAPI layers

`src/spatial/lang/api/StaticAPI.scala:7-36` defines four traits in a strict additive chain:

```
StaticAPI_Internal       (line 7-22)   — InternalAliases + per-topic API mixins
  └─ StaticAPI_External  (line 25)     — adds ExternalAliases
        └─ StaticAPI_Frontend  (line 28-33) — adds SrcCtx/Cast bindings
              └─ StaticAPI_Shadowing  (line 35-36) — adds ShadowingAliases + DebuggingAPI_Shadowing
```

`StaticAPI_Internal` (`StaticAPI.scala:7-22`) mixes `InternalAliases`, `SpatialVirtualization`, `Implicits`, plus `ArrayAPI`/`BitsAPI`/`ControlAPI`/`DebuggingAPI_Internal`/`FileIOAPI`/`MathAPI`/`MiscAPI`/`PriorityDeqAPI`/`MuxAPI`/`ShuffleAPI`/`TensorConstructorAPI`/`TransferAPI`/`TuplesAPI`/`UserData`. The `spatial.lang` package object extends this (`src/spatial/lang/package.scala:4`).

`StaticAPI_External` (`StaticAPI.scala:25`) adds `ExternalAliases`. `StaticAPI_Frontend` (`StaticAPI.scala:28-33`) adds three forge bindings — `type SrcCtx = forge.SrcCtx`, `lazy val SrcCtx = forge.SrcCtx`, `type Cast[A,B] = argon.Cast[A,B]` — used in the implicit parameter lists of every `@api` method. `StaticAPI_Shadowing` (`StaticAPI.scala:35-36`) mixes `ShadowingAliases` and `DebuggingAPI_Shadowing`.

`DebuggingAPI_Shadowing` (`src/spatial/lang/api/DebuggingAPI.scala:11-13`) declares `this: StaticAPI_Shadowing =>` — a self-type that means it can only be mixed into something that *also* extends `StaticAPI_Shadowing`. So `printArray`/`printMatrix`/`printTensor*`/`approxEql`/`checkGold`/`r"..."`/`sleep` are reachable only through `dsl`, not `libdsl`. This is structurally enforced, not a stylistic choice.

### `dsl` vs `libdsl`

`src/spatial/dsl.scala` declares the two top-level entry points:

```scala
trait SpatialDSL extends lang.api.StaticAPI_Frontend                    // dsl.scala:6
object libdsl extends SpatialDSL { /* @spatial, @struct, @streamstruct */ }  // dsl.scala:9-26
object dsl extends SpatialDSL with lang.api.StaticAPI_Shadowing { ... } // dsl.scala:29-46
```

**`libdsl`** (`dsl.scala:9-26`) extends `SpatialDSL` only and declares the three macros `@spatial`/`@struct`/`@streamstruct` (`dsl.scala:15-25`). Under `import spatial.libdsl._`, Scala's `Int`/`Float`/`Boolean`/`String`/`Array`/`Unit`/`Tuple2`/`Matrix` keep their `scala.*` meanings; staged 32-bit ints are spelled `I32`; `printArray`/`sleep`/etc. are unreachable; `gen.*` is unreachable.

**`dsl`** (`dsl.scala:29-46`) extends `SpatialDSL with StaticAPI_Shadowing` and re-declares the same three macro annotations (`dsl.scala:35-45`) — they cannot be inherited because Scala annotation classes are name-position-specific. Under `import spatial.dsl._`: `Int`/`Float`/`Boolean` are the staged Spatial types; `gen.Int`/`gen.Array[gen.Int]` reach the originals; the full debugging family is in scope; `Label = java.lang.String` is the host-string shortcut.

The choice: write `Int` everywhere (and spell `gen.Int` when you need real Scala) vs. predictable Scala behavior (and spell `I32` when you mean staged). Apps inside `Accel{...}` favor the former; libraries mixing host metaprogramming with staged code favor the latter.

## Implementation

**Argon's parallel layering.** `argon.lang` defines its own `InternalAliases`/`ExternalAliases`/`ShadowingAliases` triple. Spatial's `InternalAliases` extends *argon*'s `ExternalAliases` (`Aliases.scala:7`), not its `InternalAliases`. Argon's `ShadowingAliases` is empty — exists as an extension hook (Q-lang-06).

**Why `gen` is a trait member, not a `dsl` member.** Putting `object gen` inside `ShadowingAliases` (`Aliases.scala:184`) means it is inherited by every consumer. Downstream DSLs cannot easily *extend* `gen` without re-declaring it, but the inner Scala-types are stable.

**`lazy val` vs `val`.** Most companion aliases use `lazy val` (`Aliases.scala:24-36, 71-76`) for init-order safety; the singletons being aliased live in other compilation units, so eager access risks NPE. Exception: `val AxiStream256Data` at `Aliases.scala:180` is eager because `@struct` companions are stable.

**`dsl` and `libdsl` cannot be unified.** Scala has no per-import trait opt-in, and macros must live in the same object as the type names because Scala resolves annotations via import scope. Hence both `dsl.scala:15-25` and `dsl.scala:35-45` declare them — Scala constraint, not design preference.

## Interactions

- **`SpatialApp`** — extending classes `import spatial.dsl._` by convention, so the staged-type meaning of `Int`/`Float`/`Boolean` is in scope for the whole app body.
- **`@spatial`/`@struct`/`@streamstruct`** (`dsl.scala:15-25, 35-45`) — declared in *both* `dsl` and `libdsl`; wrap argon/Spatial staging macros and a forge `AppTag`.
- **`spatial.lang.*`** (`src/spatial/lang/package.scala:4`) extends `StaticAPI_Internal`. **`spatial.lang.api.*`** (`src/spatial/lang/api/package.scala:3`) extends `ExternalAliases`.
- **`DebuggingAPI_Shadowing`** (`src/spatial/lang/api/DebuggingAPI.scala:11-13`) — gated behind `this: StaticAPI_Shadowing =>` so debugging helpers are visible only through `dsl`.

## HLS notes

`hls_status: rework`. Shadowing is a Scala-namespace mechanism with no direct HLS analogue. Three options for the Rust port: (1) drop shadowing entirely — provide only the `libdsl` view with explicit names like `I32`/`Bit`/`Text`; (2) mirror via `type Int = Fixed<true, 32, 0>;` modules so users can `use spatial::dsl::*;` or `use spatial::libdsl::*;`; (3) macro re-export — heavier, risks confusing IDEs. The `gen` escape hatch maps cleanly to a sub-module (`spatial::dsl::gen::Int = i32`). `Label = java.lang.String` has no Rust analogue. `AxiStream256` promotion is incidental.

## Open questions

- See `[[open-questions-lang-surface]]` Q-lang-04 (`AxiStream256` asymmetry), Q-lang-05 (`Label` is the only Scala-native type promoted to root of `ShadowingAliases`), Q-lang-06 (empty `argon.lang.ShadowingAliases` — extension hook or vestigial?).
