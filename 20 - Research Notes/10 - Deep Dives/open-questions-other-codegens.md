---
type: open-questions
topic: other-codegens
session: 2026-04-24
date_started: 2026-04-24
---

# Open Questions - Other Codegens

## Q-oc-01 - [2026-04-24] PIRGenSpatial active mixins versus 32-file scope

The source directory has 32 PIR Scala files, but `PIRGenSpatial` actively mixes in `PIRCodegen` plus 21 traits; six traits are visibly commented out. Should the spec describe "32 trait mixins" as shorthand for directory scope, or should it use the source-verified active mixin list only?

Source: /Users/david/Documents/David_code/spatial/src/spatial/codegen/pirgen/PIRGenSpatial.scala:5-32
Blocked by: Historical intent for Plasticine backend documentation
Status: open
Resolution:

## Q-oc-02 - [2026-04-24] PIR LineBuffer error trait is not mixed in

`PIRGenLineBuffer` emits codegen-time `error` calls for line-buffer creation, enqueue, and read, but `PIRGenSpatial` does not mix in `PIRGenLineBuffer`. Should Pirgen fail explicitly on LineBuffer ops, or is fallback unmatched-node behavior intentional?

Source: /Users/david/Documents/David_code/spatial/src/spatial/codegen/pirgen/PIRGenLineBuffer.scala:13-20; /Users/david/Documents/David_code/spatial/src/spatial/codegen/pirgen/PIRGenSpatial.scala:5-32
Blocked by: Plasticine LineBuffer support policy
Status: open
Resolution:

## Q-oc-03 - [2026-04-24] PIR VecSlice argument order and inclusive end

`PIRGenVec` pattern matches `VecSlice(vector, end, start)` and emits `vector.slice(start, end+1)`, while the inline comment says "end is non-inclusive." Which convention should the Rust+HLS spec preserve?

Source: /Users/david/Documents/David_code/spatial/src/spatial/codegen/pirgen/PIRGenVec.scala:19-20
Blocked by: VecSlice IR semantics check outside codegen
Status: open
Resolution:

## Q-oc-04 - [2026-04-24] NamedCodegen mixin list includes ScalaCodegen

The requested note lists ChiselCodegen, ResourceReporter, and ResourceCountReporter as NamedCodegen users, but source also shows `ScalaCodegen extends Codegen with FileDependencies with NamedCodegen`. Should the final spec emphasize all source users or only the non-TreeGen users relevant to reports?

Source: /Users/david/Documents/David_code/spatial/src/spatial/codegen/scalagen/ScalaCodegen.scala:13-25; /Users/david/Documents/David_code/spatial/src/spatial/codegen/chiselgen/ChiselCodegen.scala:17-21; /Users/david/Documents/David_code/spatial/src/spatial/codegen/resourcegen/ResourceReporter.scala:22-24; /Users/david/Documents/David_code/spatial/src/spatial/codegen/resourcegen/ResourceCountReporter.scala:19-21
Blocked by: Spec scoping decision
Status: open
Resolution:

## Q-oc-05 - [2026-04-24] Cppgen target resource directories in Rust+HLS

Cppgen hardcodes nine `<target>.sw-resources`, `<target>.hw-resources`, and `<target>.Makefile` dependency triples. Should the Rust+HLS rewrite preserve these directory names for compatibility, or replace them with typed target descriptors?

Source: /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppCodegen.scala:38-75
Blocked by: Rust+HLS packaging design
Status: open
Resolution:

## Q-oc-06 - [2026-04-24] Treegen palette count differs from requested 23-color statement

The prompt calls out an NBuf 23-color palette, but `TreeGen.memColors` contains 27 literal color strings. Should the spec retain the source-verified count or is there a historical 23-color palette elsewhere?

Source: /Users/david/Documents/David_code/spatial/src/spatial/codegen/treegen/TreeGen.scala:28-32
Blocked by: Historical visualization notes
Status: open
Resolution:

## Q-oc-07 - [2026-04-24] Rogue frame streams versus HLS host replacement

Roguegen rejects `DRAMHostNew` but supports frame streams through `FrameMaster`, `FrameSlave`, and PyRogue connections. Should the HLS host rewrite model frames as streams, host buffers, or unsupported legacy behavior?

Source: /Users/david/Documents/David_code/spatial/src/spatial/codegen/roguegen/RogueGenInterface.scala:32-45
Blocked by: HLS host I/O design
Status: open
Resolution:

## Q-oc-08 - [2026-04-24] ResourceReporter emits text with json extension

`ResourceReporter` declares `ext = "json"` but emits textual controller and area lines, unlike `ResourceCountReporter`, which builds a JSON-shaped object. Should the spec call `ResourceReporter` a text report, a malformed JSON report, or an implementation bug?

Source: /Users/david/Documents/David_code/spatial/src/spatial/codegen/resourcegen/ResourceReporter.scala:22-24; /Users/david/Documents/David_code/spatial/src/spatial/codegen/resourcegen/ResourceReporter.scala:41-48; /Users/david/Documents/David_code/spatial/src/spatial/codegen/resourcegen/ResourceReporter.scala:183-190
Blocked by: Desired report format for rewrite
Status: open
Resolution:
