---
type: spec
concept: scalagen-overview
source_files:
  - "spatial/src/spatial/codegen/scalagen/ScalaCodegen.scala:13-95"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenSpatial.scala:1-38"
  - "spatial/argon/src/argon/codegen/Codegen.scala:10-202"
  - "spatial/src/spatial/Spatial.scala:146-252"
source_notes:
  - "[[scalagen-reference-semantics]]"
hls_status: rework
depends_on:
  - "[[00 - Codegen Index]]"
  - "[[20 - Numeric Reference Semantics]]"
  - "[[30 - Memory Simulator]]"
  - "[[40 - FIFO LIFO Stream Simulation]]"
  - "[[50 - Controller Emission]]"
  - "[[60 - Counters and Primitives]]"
status: draft
---

# Scalagen — Overview

## Summary

Scalagen is the Scala simulation backend for Spatial. Its output is a complete, self-contained Scala program that, when compiled and run on a JVM, faithfully simulates a Spatial accelerator's dynamic behavior. **It is the de facto reference implementation for Spatial's dynamic semantics**: when any two backends disagree, scalagen is the ground truth. For the Rust-plus-HLS rewrite, every semantic question (what does `FixRecip` return on zero? what does `SRAMBankedRead` do on an OOB address? what is the bit layout of a packed `FloatPoint`?) has its answer in `ScalaGen*.scala` and in the `emul` runtime. The backend is activated by `--sim` (`spatial/src/spatial/Spatial.scala:281-286`), is mutually exclusive with `--synth`, and is invoked as the codegen pass `scalaCodegen = ScalaGenSpatial(state)` at `spatial/src/spatial/Spatial.scala:153` and dispatched at `spatial/src/spatial/Spatial.scala:245` via `(spatialConfig.enableSim ? scalaCodegen)`.

## Architecture

### Trait composition

`ScalaGenSpatial` is a single case class that mixes in 22 sibling traits (`spatial/src/spatial/codegen/scalagen/ScalaGenSpatial.scala:5-29`):

```scala
case class ScalaGenSpatial(IR: State) extends ScalaCodegen
  with ScalaGenArray
  with ScalaGenBit
  with ScalaGenFixPt
  with ScalaGenFltPt
  with ScalaGenStructs
  with ScalaGenText
  with ScalaGenVoid
  with ScalaGenVar
  with ScalaGenDebugging
  with ScalaGenLIFO
  with ScalaGenController
  with ScalaGenCounter
  with ScalaGenDRAM
  with ScalaGenFIFO
  with ScalaGenReg
  with ScalaGenSeries
  with ScalaGenSRAM
  with ScalaGenVec
  with ScalaGenStream
  with ScalaGenRegFile
  with ScalaGenLineBuffer
  with ScalaGenFileIO
  with ScalaGenDelays
  with ScalaGenLUTs
```

Each trait overrides the base `Codegen.gen(lhs: Sym[_], rhs: Op[_])` method (`spatial/argon/src/argon/codegen/Codegen.scala:89`) with a pattern match over the IR nodes it handles, and calls `super.gen` as a fallthrough. The composition order is irrelevant beyond the requirement that `ScalaGenController` appear late enough to have `ScalaGenStream` and `ScalaGenMemories` in scope. Each trait handles disjoint op families, so there are no overlap conflicts in the trait composition linearization.

### Base trait — `ScalaCodegen`

`trait ScalaCodegen extends Codegen with FileDependencies with NamedCodegen` at `spatial/src/spatial/codegen/scalagen/ScalaCodegen.scala:13`. It sets three overrides on the `argon.codegen.Codegen` base:

1. **Language strings**: `lang = "scala"`, `ext = "scala"` (`ScalaCodegen.scala:14-15`). The base `Codegen` trait uses these to compute `out = genDir/scala/` and `entryFile = "Main.scala"` (`Codegen.scala:14-15`).
2. **`emitHeader`** (`ScalaCodegen.scala:28-33`) injects `import emul._` and `import emul.implicits._` into every emitted file. This makes every `ScalaGen*` emission that references `FixedPoint`, `FloatPoint`, `Bool`, `Counter`, `BankedMemory`, `ShiftableMemory`, `LineBuffer`, `Memory`, `StreamIn`, `StreamOut`, `Ptr`, `OOB`, `DRAMTracker`, `StatTracker`, `Number.*` resolve against the `emul` package — the `emul` runtime is the target vocabulary of scalagen.
3. **`emitEntry`** (`ScalaCodegen.scala:64-73`) wraps the entire emitted block in:

```scala
object Main {
  def main(args: Array[String]): Unit = {
    emitPreMain()
    gen(block)
    emitPostMain()
  }
  emitHelp
}
```

Downstream traits override `emitPreMain` and `emitPostMain` to inject setup (e.g., `ScalaGenMemories.emitPreMain` at `ScalaGenMemories.scala:14-17` emits `OOB.open()`) and teardown (e.g., `OOB.close()`). `emitPostMain` (`ScalaCodegen.scala:59-62`) also conditionally emits `System.out.println(StatTracker)` and `System.out.println(DRAMTracker)` when `enableResourceReporter` is set. `emitHelp` (`ScalaCodegen.scala:75-86`) emits a `def printHelp(): Unit = { ... }` that lists the app's CLI args and a sample command, invoked when the user runs with `--help` or `-h` (`ScalaGenArray.scala:42`).

### Block chunking — `javaStyleChunk`

The JVM imposes a hard 64KB method size limit. For large Spatial apps, the emitted `Main.main` body would exceed this. The base `argon.codegen.Codegen` trait provides `javaStyleChunk` (`spatial/argon/src/argon/codegen/Codegen.scala:107-199`), a generic hierarchical chunker that splits a sequence of statements into nested `object BlockNChunkerM { def gen(): Map[String, Any] = { ... } }` blocks, each under a configurable weight budget. Scalagen integrates this via its override of `gen(b: Block[_], withReturn: Boolean)` at `ScalaCodegen.scala:37-56`:

```scala
override protected def gen(b: Block[_], withReturn: Boolean = false): Unit = {
  def printableStms(stms: Seq[Sym[_]]): Seq[StmWithWeight[Sym[_]]] =
    stms.map{x => StmWithWeight[Sym[_]](x, 1, Seq[String]())}
  def isLive(s: Sym[_], remaining: Seq[Sym[_]]): Boolean =
    !s.isMem && (b.result == s || remaining.exists(_.nestedInputs.contains(s)))
  def branchSfx(s: Sym[_], n: Option[String] = None): String =
    src""""${n.getOrElse(quote(s))}" -> $s"""
  def initChunkState(): Unit = {}

  val hierarchyDepth = (scala.math.log(printableStms(b.stms).map(_.weight).sum) /
                       scala.math.log(CODE_WINDOW)).toInt
  globalBlockID = javaStyleChunk[Sym[_]](
    printableStms(b.stms), CODE_WINDOW, hierarchyDepth, globalBlockID,
    isLive, branchSfx, arg, () => initChunkState
  )(visit _)

  if (withReturn) emit(src"${b.result}")
}
```

`CODE_WINDOW` is taken from `spatialConfig.codeWindow` (`ScalaCodegen.scala:16`). `hierarchyDepth` is `log_{CODE_WINDOW}(total_weight)`, clamped to 0/1/2 depending on block size. The `isLive` predicate (which symbols must be exposed out of a chunk) excludes memory symbols (since they live at file scope) and admits symbols used downstream. `branchSfx` forms map entries keyed by symbol name. The emitted chunk shape at depth 1, per `Codegen.scala:132-155`, is:

```scala
object BlockNChunker0 { // K nodes, W weight
  def gen(): Map[String, Any] = {
    // ... emitted body of K statements ...
    Map[String, Any]("xA" -> xA, "xB" -> xB, ...)  // live outputs
  }
}
val block0chunk0: Map[String, Any] = BlockNChunker0.gen()

object BlockNChunker1 { ... }
val block0chunk1: Map[String, Any] = BlockNChunker1.gen()
// ...
```

Depth 2 adds an inner `Sub0`/`Sub1`/... nesting inside each outer chunk (`Codegen.scala:156-198`). Later references to a chunked symbol go through `ScalaCodegen.named` (`ScalaCodegen.scala:22-26`), which checks the `scoped` map and rewrites `quote(s)` to `block0chunk0("xA").asInstanceOf[Tp]` (the `ScopeInfo.assemble` helper at `Codegen.scala:97-102`).

For the Rust port, chunking is a JVM-specific concern. The Rust-generated simulator does not need this layering; it can emit straightforward functions.

## Emitted file layout

Per `Codegen.process` (`Codegen.scala:75-82`), the top-level entry point writes:

- `$genDir/scala/Main.scala` — the main entry. Contains the full user program with:
  - `import emul._; import emul.implicits._` header (from `ScalaCodegen.emitHeader`)
  - `object Main { def main(args: Array[String]): Unit = { OOB.open(); <body>; OOB.close() } }` structure (from `ScalaCodegen.emitEntry`, `ScalaGenMemories.emitPreMain/emitPostMain`)
  - `def printHelp(): Unit = { ... }` block
- `$genDir/scala/<sym>_kernel.scala` — one file per controller and per memory. Emitted by `ScalaGenController.emitControlObject` (`spatial/src/spatial/codegen/scalagen/ScalaGenController.scala:108-139`) and `ScalaGenMemories.emitMemObject` (`spatial/src/spatial/codegen/scalagen/ScalaGenMemories.scala:61-67`). Per `Codegen.kernel(sym)` at `Codegen.scala:201`, the file path is `${sym}_kernel.scala`. Each kernel file begins with its own `import emul._` header so it compiles independently.
- `$genDir/scala/Structs.scala` — shared case-class declarations for all `Struct[A]` types encountered. Emitted by `ScalaGenStructs.emitDataStructures` (`spatial/src/spatial/codegen/scalagen/ScalaGenStructs.scala:27-36`) via `inGen(getOrCreateStream(out, "Structs.scala"))`. Single file, not per-kernel.
- Dependency copies: `scalagen/sim.Makefile` → `Makefile`, `scalagen/run.sh`, `scalagen/build.sbt`, `scalagen/project/build.properties` → `project/` (`ScalaGenSpatial.scala:31-37`). Plus `synth/scripts` (`ScalaCodegen.scala:89`). These let `make run.sh` just work from the generated directory.

## Composition with `NamedCodegen`

`ScalaCodegen extends NamedCodegen` (`ScalaCodegen.scala:13`). `NamedCodegen` provides name-resolution for delay-line and other aliasing constructs. The key hook is `ScalaCodegen.named(s: Sym[_], id: Int)` at `ScalaCodegen.scala:22-26`, which first consults the chunk-aware `scoped` map (for `javaStyleChunk`-hoisted references) and falls back to `super.named(s, id)` (which consults `NamedCodegen`'s alias map) otherwise. This dual lookup lets a single `quote(s)` call produce the right chunk-qualified or alias-qualified identifier for every symbol regardless of which layer wrote it.

## Ground-truth status for the Rust+HLS target

**This entry is the gateway to the reference semantics.** The subsequent scalagen spec entries (`20 - Numeric Reference Semantics`, `30 - Memory Simulator`, `40 - FIFO LIFO Stream Simulation`, `50 - Controller Emission`, `60 - Counters and Primitives`) define the actual bit-level behavior. The HLS target must match their semantics. In contrast, the emission mechanics documented in this overview (object-wrapping, `javaStyleChunk`, file layout, dependency copies) are scalagen-specific artifacts that the Rust port does not need to inherit.

The single load-bearing responsibility of this overview for the Rust port is the **`emul` runtime contract**: any Rust simulator of Spatial that wants to reuse test vectors from the Scala simulator must produce bit-identical outputs for every op family. The reference definitions are in `spatial/emul/src/emul/`.

## HLS notes

- `chisel-specific` does not apply — scalagen is pure Scala.
- `rework` for this entry's content: the Rust backend must define its own main-entry structure, its own chunking strategy (if any), its own file layout, and its own runtime library. None of `object Main`, `javaStyleChunk`, or `_kernel.scala` file-per-controller carry over.
- The `emul` contract is `rework` — the Rust runtime must provide equivalent types (`FixedPoint`, `FloatPoint`, `Bool`, `BankedMemory`, `ShiftableMemory`, `LineBuffer`, `Counter`, `Ptr`, `OOB`, `StreamIn`, `StreamOut`, `BufferedOut`, `DRAMTracker`, `StatTracker`) matching scalagen's semantics exactly.

## Interactions

- **Upstream**: `argon.codegen.Codegen` base trait (`spatial/argon/src/argon/codegen/Codegen.scala:10-202`); `argon.codegen.FileDependencies`; `spatial.codegen.naming.NamedCodegen`; `spatial.metadata.CLIArgs`; `spatial.util.spatialConfig`.
- **Downstream**: emitted Scala files. No downstream Scala-source consumers.
- **Sibling codegens**: scalagen is dispatched in the same pass pipeline as chiselgen, cppgen, rogueGen, pirgen, tsthgen (`spatial/src/spatial/Spatial.scala:241-252`). At most one primary codegen runs per compilation; `--sim` and `--synth` are mutually exclusive (`Spatial.scala:281-290`). scalagen is the only one that produces a runnable binary without requiring external tool integration.

## Open questions

See `open-questions-scalagen.md` (Q-scal-01 through Q-scal-10) for unresolved semantic questions surfaced during this distillation.
