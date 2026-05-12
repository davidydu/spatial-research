---
type: spec
concept: Other non-Chisel codegens
source_files:
  - "/Users/david/Documents/David_code/spatial/src/spatial/codegen/roguegen/RogueCodegen.scala:10-43"
  - "/Users/david/Documents/David_code/spatial/src/spatial/codegen/roguegen/RogueFileGen.scala:7-85"
  - "/Users/david/Documents/David_code/spatial/src/spatial/codegen/tsthgen/TungstenHostCodegen.scala:12-73"
  - "/Users/david/Documents/David_code/spatial/src/spatial/codegen/dotgen/DotCodegen.scala:10-215"
  - "/Users/david/Documents/David_code/spatial/src/spatial/codegen/treegen/TreeGen.scala:19-267"
  - "/Users/david/Documents/David_code/spatial/src/spatial/codegen/dotgen/HtmlIRGenSpatial.scala:10-133"
source_notes:
  - "[[other-codegens]]"
hls_status: rework
depends_on:
  - "[[10 - Cppgen]]"
  - "[[10 - Pirgen]]"
status: draft
---

# Other Codegens

## Summary

This entry covers the non-Chisel, non-Scala execution and visualization backends that sit beside Cppgen and Pirgen. Roguegen emits Python for SLAC Rogue and PyRogue, Tsthgen emits a Tungsten host harness, Dotgen emits Graphviz graphs, Treegen emits a controller-tree HTML report, and `HtmlIRGenSpatial` emits per-symbol IR HTML with dot cross-links and memory access summaries /Users/david/Documents/David_code/spatial/src/spatial/codegen/roguegen/RogueCodegen.scala:10-43 /Users/david/Documents/David_code/spatial/src/spatial/codegen/tsthgen/TungstenHostCodegen.scala:12-73 /Users/david/Documents/David_code/spatial/src/spatial/codegen/dotgen/DotCodegen.scala:10-112 /Users/david/Documents/David_code/spatial/src/spatial/codegen/treegen/TreeGen.scala:19-46 /Users/david/Documents/David_code/spatial/src/spatial/codegen/dotgen/HtmlIRGenSpatial.scala:10-133.

## Syntax or API

### Roguegen

`RogueGen` composes `RogueCodegen`, `RogueFileGen`, `RogueGenCommon`, `RogueGenInterface`, `RogueGenAccel`, `RogueGenDebug`, `RogueGenMath`, and `RogueGenArray`, with a commented-out `RogueGenFileIO` mixin /Users/david/Documents/David_code/spatial/src/spatial/codegen/roguegen/RogueGen.scala:5-13. `RogueCodegen` declares `lang = "rogue"`, `ext = "py"`, and `entryFile = "TopHost.py"` /Users/david/Documents/David_code/spatial/src/spatial/codegen/roguegen/RogueCodegen.scala:10-13. `RogueFileGen` sets `backend = "python"`, emits `TopHost.py` with Rogue, PyRogue, AXI PCIe, time, math, random, struct, and NumPy imports, opens `execute(base, cliargs)`, resets `base.Fpga.SpatialBox`, and prints a start message /Users/david/Documents/David_code/spatial/src/spatial/codegen/roguegen/RogueFileGen.scala:7-44. The same header pass emits `ConnectStreams.py` with Rogue/PyRogue imports plus `FrameSlave` and `FrameMaster`, then opens `connect(base)` /Users/david/Documents/David_code/spatial/src/spatial/codegen/roguegen/RogueFileGen.scala:45-69. `RogueGenInterface.emitFooter` writes `_AccelUnit.py` and declares a PyRogue `AccelUnit` with `Enable`, `Reset`, `Done`, and generated remote variables for args and instrumentation /Users/david/Documents/David_code/spatial/src/spatial/codegen/roguegen/RogueGenInterface.scala:87-150.

### Tsthgen

`TungstenHostGenSpatial` extends `TungstenHostCodegen`, `TungstenHostGenCommon`, `CppGenDebug`, `CppGenMath`, `TungstenHostGenArray`, `CppGenFileIO`, `TungstenHostGenInterface`, and `TungstenHostGenAccel` /Users/david/Documents/David_code/spatial/src/spatial/codegen/tsthgen/TungstenHostGen.scala:6-13. `TungstenHostCodegen` itself extends `FileDependencies with CppCodegen`, declares `lang = "tungsten"`, `ext = "cc"`, `entryFile = "main.cc"`, and redirects `out` to a `src` subdirectory /Users/david/Documents/David_code/spatial/src/spatial/codegen/tsthgen/TungstenHostCodegen.scala:12-17. Its entry emits includes for `repl.h`, `DUT.h`, and `cppgenutil.h`, generates `printHelp`, supports `--gen-link`, creates a `Top`, wraps it in `Module DUT`, runs `REPL`, and calls `gen(block)` from `main` /Users/david/Documents/David_code/spatial/src/spatial/codegen/tsthgen/TungstenHostCodegen.scala:22-63.

### Visualization

`DotCodegen` declares `lang = "info"` and `ext = "dot"`, manages graph scopes, emits `.dot` files, and postprocesses each dot file through `dot -Tsvg -o <htmlPath> <dotPath>` while logging failures to `dot.log` /Users/david/Documents/David_code/spatial/src/spatial/codegen/dotgen/DotCodegen.scala:10-20 /Users/david/Documents/David_code/spatial/src/spatial/codegen/dotgen/DotCodegen.scala:93-112. `TreeGen` declares `entryFile = controller_tree.html` by default and uses jQuery Mobile collapsibles in its HTML header /Users/david/Documents/David_code/spatial/src/spatial/codegen/treegen/TreeGen.scala:19-31 /Users/david/Documents/David_code/spatial/src/spatial/codegen/treegen/TreeGen.scala:181-201. `HtmlIRGenSpatial` defaults to `IR.html`, turns node and bound symbols into links to `IR.html#sym`, and emits dot links when dot generation is enabled /Users/david/Documents/David_code/spatial/src/spatial/codegen/dotgen/HtmlIRGenSpatial.scala:10-22 /Users/david/Documents/David_code/spatial/src/spatial/codegen/dotgen/HtmlIRGenSpatial.scala:59-71.

## Semantics

Roguegen is a KCU1500 legacy host path: `KCU1500.host` returns `"rogue"`, and the main Spatial pipeline chooses Cppgen only when synthesis is enabled and `target.host == "cpp"`, while Roguegen runs when `target.host == "rogue"` /Users/david/Documents/David_code/spatial/src/spatial/targets/xilinx/KCU1500.scala:6-10 /Users/david/Documents/David_code/spatial/src/spatial/Spatial.scala:246-248. Roguegen does not support DRAM host nodes: `DRAMHostNew` throws an exception /Users/david/Documents/David_code/spatial/src/spatial/codegen/roguegen/RogueGenInterface.scala:19-33. It does support frame streams by emitting `FrameMaster` or `FrameSlave` and `pyrogue.streamConnect` calls in `ConnectStreams.py` /Users/david/Documents/David_code/spatial/src/spatial/codegen/roguegen/RogueGenInterface.scala:33-45. Fractional fixed-point values remap to `double`, integer fixed-point values remap to width-named Python-ish strings such as `uint32` and `int64`, and `FltPtType` remaps to `float` /Users/david/Documents/David_code/spatial/src/spatial/codegen/roguegen/RogueGenCommon.scala:58-82.

Tsthgen reuses cppgen debug, math, and file I/O behavior, but changes host memory allocation and simulator entry. Fractional fixed-point remaps to `float` when total width is at most 32 and to `double` when total width is at most 64 /Users/david/Documents/David_code/spatial/src/spatial/codegen/tsthgen/TungstenGenCommon.scala:8-13. `TungstenHostGenInterface` writes host I/O declarations into `hostio.h`, accumulates allocation functions, and emits `AllocAllMems()` in the footer /Users/david/Documents/David_code/spatial/src/spatial/codegen/tsthgen/TungstenHostGenInterface.scala:13-43 /Users/david/Documents/David_code/spatial/src/spatial/codegen/tsthgen/TungstenHostGenInterface.scala:25-37. DRAM allocations add a 64-byte burst alignment pad, round the pointer up to the next burst boundary, and print the allocated address /Users/david/Documents/David_code/spatial/src/spatial/codegen/tsthgen/TungstenHostGenInterface.scala:91-115. `TungstenHostGenArray` mirrors cppgen struct packing with packed structs, field setters, `toRaw`, and an `int128_t` bit constructor, which appears intended to keep Tungsten host structs bit-compatible with PIR-style packed host values (inferred, unverified) /Users/david/Documents/David_code/spatial/src/spatial/codegen/tsthgen/TungstenHostGenArray.scala:22-68.

Dotgen has two views. `DotFlatCodegen` emits `Main.dot`, nests block nodes as dot subgraphs, and gives block nodes `URL = "<sym>.html"` /Users/david/Documents/David_code/spatial/src/spatial/codegen/dotgen/DotFlatCodegen.scala:9-40. `DotHierarchicalCodegen` emits `Top.dot`, creates one scope per block-bearing symbol, and projects cross-scope edges through ancestor branches to the least common shared scope using alias maps /Users/david/Documents/David_code/spatial/src/spatial/codegen/dotgen/DotHierarchicalCodegen.scala:11-33 /Users/david/Documents/David_code/spatial/src/spatial/codegen/dotgen/DotHierarchicalCodegen.scala:38-80. `DotGenSpatial` colors SRAM-like memories forest green, locks crimson, regs chartreuse, FIFOs and streams gold, and DRAMs blueviolet /Users/david/Documents/David_code/spatial/src/spatial/codegen/dotgen/DotGenSpatial.scala:30-42.

Treegen prints a controller cell for each hardware control, includes schedule, op name, level, source context, latency, II, and compiler II mismatch highlighting, and recursively renders nested blocks inside collapsibles /Users/david/Documents/David_code/spatial/src/spatial/codegen/treegen/TreeGen.scala:116-157. It uses a 27-color memory palette for NBuf and single-buffered memory reports, not a 23-color palette as the prompt suggests; see [[open-questions-other-codegens#Q-oc-06]] /Users/david/Documents/David_code/spatial/src/spatial/codegen/treegen/TreeGen.scala:28-32. `HtmlIRGenSpatial` also writes memory nodes to `Mem.html` and embeds writer and reader tables for each memory /Users/david/Documents/David_code/spatial/src/spatial/codegen/dotgen/HtmlIRGenSpatial.scala:94-130.

## Implementation

Roguegen starts an accelerator by reading `Done`, setting `Enable`, polling `Done` every 0.01 seconds, printing every 75 polls, and then printing completion /Users/david/Documents/David_code/spatial/src/spatial/codegen/roguegen/RogueGenAccel.scala:14-32. Tsthgen's accelerator scope just emits `RunAccel()`, while host-side `AssertIf` emits a local `ASSERT` call and records hardware early exits only when inside hardware /Users/david/Documents/David_code/spatial/src/spatial/codegen/tsthgen/TungstenHostGenAccel.scala:13-36.

## Interactions

Rogue dependency copying only has a target-specific branch for KCU1500, where it copies `kcu1500.sw-resources`, `kcu1500.hw-resources`, and `kcu1500.Makefile`; it always copies scripts, `build.sbt`, and `run.sh` /Users/david/Documents/David_code/spatial/src/spatial/codegen/roguegen/RogueCodegen.scala:21-43. Dot and Tree are scheduled before optional Scala, Chisel, Cpp, Rogue, resource, PIR, and Tungsten codegen in the main Spatial pipeline /Users/david/Documents/David_code/spatial/src/spatial/Spatial.scala:240-252.

## HLS notes

Tsthgen is closest to a reusable HLS host idea because it preserves a C++-like host harness and memory allocation path, but its simulator-specific `DUT`, `REPL`, `RunAccel`, and `hostio.h` mechanisms need rework /Users/david/Documents/David_code/spatial/src/spatial/codegen/tsthgen/TungstenHostCodegen.scala:22-63 /Users/david/Documents/David_code/spatial/src/spatial/codegen/tsthgen/TungstenHostGenAccel.scala:13-36. Roguegen is a legacy KCU1500/PyRogue host and should not be treated as a portable HLS host model /Users/david/Documents/David_code/spatial/src/spatial/targets/xilinx/KCU1500.scala:6-10 /Users/david/Documents/David_code/spatial/src/spatial/codegen/roguegen/RogueFileGen.scala:11-69. Visualization codegens are documentation/reporting surfaces; their HLS status is unknown except that their graph algorithms can be retained as compiler diagnostics /Users/david/Documents/David_code/spatial/src/spatial/codegen/dotgen/DotCodegen.scala:93-112 /Users/david/Documents/David_code/spatial/src/spatial/codegen/treegen/TreeGen.scala:181-267.

## Open questions

See [[open-questions-other-codegens#Q-oc-06]] for the Treegen palette-count mismatch and [[open-questions-other-codegens#Q-oc-07]] for whether Rogue frame streams need an HLS-host replacement.
