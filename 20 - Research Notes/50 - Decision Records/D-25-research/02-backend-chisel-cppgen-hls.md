---
type: "research"
decision: "D-25"
angle: 2
topic: "backend-chisel-cppgen-hls"
---

# D-25 Angle 2: Backend Chisel, Cppgen, And HLS Behavior

## 1. IR Baseline

The IR distinguishes the policies syntactically. `oneHotMux` stages `OneHotMux`, while `priorityMux` stages `PriorityMux`; both require `Bits[A]` payloads and simply box the values before staging (`src/spatial/lang/api/MuxAPI.scala:26-31`). The node rewrite is only a partial static cleanup: `OneHotMux` collapses a single selector, a literal-true selector, or identical values; if more than one selector is literally true it warns, then still returns the first literal-true value (`src/spatial/node/Mux.scala:19-35`). `PriorityMux` has the analogous literal-true branch commented out and only folds one selector or identical values (`src/spatial/node/Mux.scala:39-56`). Therefore multi-true dynamic behavior is delegated to backends, not normalized in IR.

## 2. Scalagen And Chiselgen

Scalagen is the only backend here that clearly implements OR-reduce for `OneHotMux`: it emits a `List((sel,d), ...)`, filters true selectors, then calls `.reduce{_|_}` (`src/spatial/codegen/scalagen/ScalaGenBits.scala:30-37`). Dynamic multi-true therefore ORs all selected payloads; dynamic zero-true has no fallback. Scalagen `PriorityMux` is a first-true cascade with an invalid fallback: ordered `if` / `else if`, then `else { invalid(R) }` (`src/spatial/codegen/scalagen/ScalaGenBits.scala:39-45`). The unit test records the same split: "one hot" gold ORs all enabled entries, while priority gold selects the first enabled entry (`test/spatial/tests/feature/unit/MuxTest.scala:20-33`).

Chiselgen lowers the same IR to Chisel primitives, not to Scalagen code. `OneHotMux` becomes `Mux1H(List(sels), List(opts.r))`; `PriorityMux` becomes `PriorityMux(List(sels), List(ForceUInt(opts)))` (`src/spatial/codegen/chiselgen/ChiselGenMath.scala:226-232`). Chisel's public docs say `Mux1H` behavior is undefined if zero or multiple selectors are set, and `PriorityMux` gives priority to the first select ([Chisel mux docs](https://www.chisel-lang.org/docs/explanations/muxes-and-input-selection); [Chisel PriorityMux API](https://www.chisel-lang.org/api/latest/chisel3/util/PriorityMux%24.html)). The Chisel source note likewise says `Mux1H` results are unspecified unless exactly one select is high, while `PriorityMux` assumes multiple select signals can be enabled and gives first priority ([Chisel Mux.scala](https://github.com/chipsalliance/chisel/blob/v7.11.0/src/main/scala/chisel3/util/Mux.scala)). Local Fringe helpers preserve this distinction: `fatMux("PriorityMux", ...)` calls `chisel3.util.PriorityMux`, otherwise it calls `chisel3.util.Mux1H` (`fringe/src/fringe/utils/package.scala:71-82`). So Chisel/RTL expects one-hot for `OneHotMux`; it does not assert one-hotness in the emitted Spatial code.

## 3. Cppgen, Roguegen, And PIR

Cppgen is not a behavioral precedent for D-25. The concrete generator mixes in `CppGenMath`, but that trait handles only ordinary `Mux` as C++ `if` / `else` (`src/spatial/codegen/cppgen/CppGen.scala:5-13`, `src/spatial/codegen/cppgen/CppGenMath.scala:140-142`). There is no cppgen handler for `OneHotMux` or `PriorityMux`; after trait fallthrough, Argon's base codegen throws when generation is enabled and no rule exists (`src/spatial/codegen/cppgen/CppGenMath.scala:158`, `argon/src/argon/codegen/Codegen.scala:89-91`). Roguegen is similar: `RogueGenMath` handles only ordinary `Mux` as a Python conditional expression, and repository search finds no Rogue `OneHotMux` or `PriorityMux` rule (`src/spatial/codegen/roguegen/RogueGen.scala:5-12`, `src/spatial/codegen/roguegen/RogueGenMath.scala:99-112`).

PIR records less semantics than Chisel or Scalagen. `PIRGenBits` emits ordinary `Mux` through `genOp`, and emits one-hot muxes as an op named by arity, `OneHotMux${selects.size}` (`src/spatial/codegen/pirgen/PIRGenBits.scala:10-14`). It has no explicit `PriorityMux` case in that file; generic `genOp` records an `OpDef` name plus product inputs (`src/spatial/codegen/pirgen/PIRGenHelper.scala:78-86`). The area model keeps `Mux`, `OneHotMux`, and `PriorityMux` as separate CSV keys, parameterized by data width or selector-count log (`src/spatial/targets/NodeParams.scala:43-45`). PIR therefore preserves the distinction but does not answer multi-true value semantics in this source slice.

## 4. HLS Mapping Implications

The backend evidence separates three choices. OR-reduce matches Scalagen and `MuxTest`, but not Chisel's documented `Mux1H` contract (`ScalaGenBits.scala:30-37`; `ChiselGenMath.scala:226-229`). Priority matches `PriorityMux`, but would rename `OneHotMux` into an already distinct IR node (`ScalaGenBits.scala:39-45`; `MuxAPI.scala:26-31`). Assertion/proof of exactly one true selector best matches the Chisel/RTL primitive and lets HLS lower one-hot selection as masked OR or a mux tree after a check.

Unverified HLS: vendor tools generally synthesize ordered `if` / `else if` as priority logic and unrolled masked OR as parallel select-and-OR logic, but C `assert`, assumption pragmas, and optimization of one-hot predicates are tool-specific. A portable HLS contract should therefore record the chosen policy per mux: `compat_or_reduce`, `checked_onehot`, or explicit rewrite to `PriorityMux`. Cppgen cannot be used as the HLS reference until it grows real `OneHotMux` and `PriorityMux` lowering.
