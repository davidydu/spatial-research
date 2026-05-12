---
type: "research"
decision: "D-25"
angle: 6
topic: "risk-failure-modes"
---

# D-25 Angle 6: Risk And Failure Modes

## 1. Baseline Hazard

`oneHotMux` is exposed as a separate API from `priorityMux` (`src/spatial/lang/api/MuxAPI.scala:26-31`), but the current stack does not enforce dynamic one-hotness. The IR rewrite only handles one selector, literal true selectors, and identical values; it warns on multiple statically true selectors but still selects the first literal-true arm (`src/spatial/node/Mux.scala:21-35`). Scalagen collects true lanes and `reduce{_|_}`s them with no zero-true fallback (`src/spatial/codegen/scalagen/ScalaGenBits.scala:30-37`). That makes the core failure mode silent data corruption for multi-true fixed-point values, since fixed-point `|` is a bitwise union (`emul/src/emul/FixedPoint.scala:23-25`); for Bool it is logical OR (`emul/src/emul/Bool.scala:5-8`). The risk is not theoretical: switch optimization and flattening can introduce `oneHotMux` from cases (`src/spatial/transform/SwitchOptimizer.scala:65-79`, `src/spatial/transform/FlatteningTransformer.scala:85-93`), and memory dealiasing uses selector vectors to mux reads, dimensions, addresses, lengths, origins, and pars (`src/spatial/transform/MemoryDealiasing.scala:22-35`, `src/spatial/transform/MemoryDealiasing.scala:75-82`, `src/spatial/transform/MemoryDealiasing.scala:90-127`).

## 2. OR-Reduce And Priority Policies

OR-reduce has the best legacy compatibility and worst corruption story. It matches Scalagen emission (`ScalaGenBits.scala:30-37`) and the unit test's stated gold behavior: "Take all enabled entries and 'or' them together" (`test/spatial/tests/feature/unit/MuxTest.scala:20`, `test/spatial/tests/feature/unit/MuxTest.scala:27`). That minimizes test breakage, but it blesses a result that is semantically unrelated to selection when two non-disjoint data words are enabled. It also strains HLS synthesis assumptions because Chisel emits `Mux1H` for this op (`src/spatial/codegen/chiselgen/ChiselGenMath.scala:226-228`) and the target model records it as `OneHotMux`, not as a general OR tree (`src/spatial/targets/NodeParams.scala:43-45`). Optimization legality is narrow: OR-reduce is legal only if data is really a masked bit set or if compatibility mode promises exact Scalagen replay. Users get few diagnostics, and migration is easy only because it keeps the bug.

Priority semantics is deterministic and ergonomic, but it is a semantic rename, not a cleanup. The codebase already has `PriorityMux`; Scalagen lowers it to ordered `if` / `else if` arms with an invalid fallback (`ScalaGenBits.scala:39-45`), Chisel emits Chisel `PriorityMux` (`ChiselGenMath.scala:230-232`), and the test separately expects "first enabled entry" (`MuxTest.scala:21`, `MuxTest.scala:28-33`). Making `OneHotMux` priority would break current OR-gold tests and any app depending on bit unions, while making switch and alias optimizations legal under a new first-wins contract. It would also hide multi-true bugs unless diagnostics stay on, because dynamic multi-true becomes defined behavior.

## 3. Assert And Invalid/Poison Policies

One-hot assert is the safest default against silent data corruption. It aligns with the name, Chisel `Mux1H` lowering, and optimizers that are apparently trying to encode mutually exclusive cases. It does introduce migration and test risk: `MuxTest` intentionally passes multiple true selectors in the default args (`MuxTest.scala:6`) and validates OR output (`MuxTest.scala:27-40`). Dynamic detection requires generated `popcount(selects) == 1` or equivalent, because current detection only covers literal true selectors at rewrite time (`Mux.scala:23-31`). HLS risk is cost and portability: assertions, failure flags, or synthesis-time assumes must either be supported by the target or compiled out after proof.

Invalid/poison is diagnostically strong but implementation-heavy. It can prevent corrupted results from becoming golden by contaminating downstream values on zero-true or multi-true. However, Scalagen currently has no generic invalid value generator: `invalid(tp)` throws for all types (`ScalaGenBits.scala:24-26`), even though `PriorityMux` emission references invalid as a fallback (`ScalaGenBits.scala:39-45`). That means poison needs typed invalid constructors, propagation rules, reporting, and HLS mapping. Optimization legality also changes: even though `OneHotMux` is a pure primitive (`Mux.scala:19`), poison failure is observable and cannot be erased like an ordinary value rewrite. It is user-friendly in debug traces, but high migration risk for existing tests because many comparisons would need to expect poison instead of numeric values.

## 4. Dual-Mode Migration

Dual-mode has the lowest practical migration risk if the modes are explicit. A `compat_or_reduce` mode preserves Scalagen and current tests for readback, including OR-gold behavior (`MuxTest.scala:20-40`). A `checked_onehot` mode makes Rust/HLS correctness the default and records dynamic violations. Priority should remain an explicit rewrite to `PriorityMux`, not an interpretation switch, because the API and backends already distinguish the two nodes (`MuxAPI.scala:26-31`, `ChiselGenMath.scala:226-232`). The user-ergonomics risk is mode confusion, so emitted reports should name the selected policy per mux, selector count, data type, proof source, and whether checks were static or dynamic.

## 5. Risk Ranking

For final HLS semantics, rank policies by safety as: checked one-hot, invalid/poison, dual-mode checked default with compat escape hatch, priority opt-in, OR-reduce default. OR-reduce is valuable only for legacy replay; priority is valuable only as a deliberate source-level meaning. The critical migration task is to audit generated `oneHotMux` sites from switch flattening, memory dealiasing, streamification, and app code such as the CNN local-data reorder (`test/spatial/tests/apps/Inference.scala:479-484`) so dynamic checks catch true ambiguity instead of breaking legitimate one-hot patterns.
