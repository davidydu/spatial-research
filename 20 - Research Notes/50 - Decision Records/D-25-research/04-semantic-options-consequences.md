---
type: "research"
decision: "D-25"
angle: 4
topic: "semantic-options-consequences"
---

# D-25 Angle 4: Semantic Options And Value-Level Consequences

## 1. Evidence Boundary

D-25 is not choosing an API shape; `oneHotMux[A:Bits](sels, vals)` already stages `OneHotMux` over any `Bits[A]` payload (`src/spatial/lang/api/MuxAPI.scala:26-28`; `src/spatial/node/Mux.scala:19`). The conflict is semantic. Scalagen emits `collect{case (sel, d) if sel => d}.reduce{_|_}` (`src/spatial/codegen/scalagen/ScalaGenBits.scala:30-37`), while the IR rewrite folds a literal-true selector to the first literal-true value and only warns when more than one literal selector is true (`src/spatial/node/Mux.scala:21-30`). The semantics spec already calls this a Rust divergence because dynamic multi-true selectors can reach Scalagen and become a bitwise union (`10 - Spec/20 - Semantics/50 - Data Types.md:58`). Chiselgen emits `Mux1H`, not a priority cascade, for `OneHotMux` (`src/spatial/codegen/chiselgen/ChiselGenMath.scala:226-229`).

## 2. OR-Reduce Compatibility

OR-reduce gives maximal Scalagen and test compatibility. `MuxTest` explicitly describes one-hot mux as "Take all enabled entries and 'or' them together" and computes gold with `reduce{_|_}` (`test/spatial/tests/feature/unit/MuxTest.scala:20-28`). For `Bool` payloads, this is logical OR and validity conjunction: `Bool.|` returns value OR but `valid && valid` (`emul/src/emul/Bool.scala:7`). A multi-true selector with one invalid `Bool` payload therefore poisons the result even if another true payload is valid true. Selector validity is weaker: emitted Scala `if sel` uses `Bool.value` through the implicit conversion, not `toValidBoolean` (`emul/src/emul/implicits.scala:8`; `emul/src/emul/Bool.scala:13-14`).

For `FixedPoint`, OR-reduce is raw storage union, not numeric selection: `FixedPoint.|` ORs the scaled integer values and conjuncts validity (`emul/src/emul/FixedPoint.scala:23-25`). That can create an arbitrary fixed value, especially across signed fractional formats. For `FloatPoint`, current Scalagen has no direct `|`; the spec records that float `OneHotMux` would fail to compile (`10 - Spec/50 - Code Generation/20 - Scalagen/60 - Counters and Primitives.md:62-64`). Thus pure OR compatibility is only fully defined for `Bool` and fixed-like scalar payloads unless the HLS port adds a raw-bit OR layer.

## 3. One-Hot Assertion Or Rejection

Assertion/rejection says `OneHotMux` is defined only when exactly one selector is true. This best matches the operator name, the Q-154 problem statement, and Chisel `Mux1H` intent (`20 - Research Notes/20 - Open Questions.md:2180-2190`; `src/spatial/codegen/chiselgen/ChiselGenMath.scala:226-229`). It also makes optimization assumptions clean: passes and HLS can treat selector predicates as mutually exclusive, avoid priority ordering, and lower to parallel select-and-OR hardware without defining multi-true value synthesis. The cost is migration: existing tests or apps that intentionally use OR behavior, like `MuxTest`, must become an explicit `orReduce(selects.zip(vals))` idiom rather than `oneHotMux`.

Diagnostics should distinguish static and dynamic violations. Static multiple literal true selectors already warn but then first-true-fold, which is not OR semantics (`src/spatial/node/Mux.scala:25-30`). A stricter policy should upgrade that to a compile error or a named compatibility warning. Dynamic violations need a simulator assertion and an optional synthesized HLS assertion in debug builds; release builds may record `assume_one_hot`.

## 4. Priority-First Semantics

Priority-first makes `OneHotMux` behave like `PriorityMux`: first true wins, no raw bit blending. Scalagen already emits `PriorityMux` as an if/else cascade with invalid fallback (`src/spatial/codegen/scalagen/ScalaGenBits.scala:39-45`), and the API separately exposes `priorityMux` (`src/spatial/lang/api/MuxAPI.scala:30-32`). Applying priority semantics to `OneHotMux` would align with the current literal-true rewrite but contradict dynamic Scalagen, `MuxTest`, and Chisel `Mux1H`. It also bakes selector order into optimization: the HLS backend cannot commute lanes, balance trees freely, or treat selectors as exclusive unless it separately proves exclusivity.

Priority is attractive for `FloatPoint`, `Vec`, and `Struct` because it selects whole values without inventing bitwise OR for types that lack `|`. But that argument mostly says the user should have written `priorityMux`. Reusing the one-hot spelling for ordered arbitration would hide bugs in alias and switch lowering, where one-hot conditions are meant to encode exclusivity (`src/spatial/transform/MemoryDealiasing.scala:22-35`; `src/spatial/transform/SwitchOptimizer.scala:64-79`).

## 5. Invalid/Poison And Aggregates

Invalid/poison semantics defines multi-true as no value, not a blended value. This is strongest for diagnostics and optimizer contracts: HLS may assume the multi-true path is unreachable after emitting a checked simulator assertion. The downside is that Spatial invalid is value-specific, not a uniform poison lattice: `Bool(false,false)`, `FixedPoint.invalid`, `FloatPoint.invalid`, struct-recursive invalid, and vector invalid are emitted by different codegen hooks (`src/spatial/codegen/scalagen/ScalaGenBit.scala:21-23`; `src/spatial/codegen/scalagen/ScalaGenFixPt.scala:26-28`; `src/spatial/codegen/scalagen/ScalaGenFltPt.scala:32-34`; `src/spatial/codegen/scalagen/ScalaGenStructs.scala:11-13`; `src/spatial/codegen/scalagen/ScalaGenVec.scala:14-16`).

For aggregates, a raw-bit OR policy must specify packing. `Struct.asBits` concatenates bit fields and `recastUnchecked` slices them back by field size (`argon/src/argon/lang/types/Bits.scala:71-82`, `:148-170`); `Vec.fromBits` slices each element by `A.nbits` (`argon/src/argon/lang/Vec.scala:217-226`). That can define HLS raw OR for `Struct`/`Vec`, but it must carry validity separately because fixed and float `.bits` paths can lose invalidity (`emul/src/emul/FixedPoint.scala:45`; `emul/src/emul/FloatPoint.scala:216`, `:435-459`). Recommendation pressure: use `assert_one_hot` as the architectural HLS contract, keep `or_reduce_compat` only as an explicit Scalagen legacy mode, and reserve `poison_on_violation` for optimization after diagnostics prove or check exclusivity.
