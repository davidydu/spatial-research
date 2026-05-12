---
type: "research"
decision: "D-25"
angle: 7
topic: "implementation-cost-migration"
---

# D-25 Angle 7: Implementation Cost And Migration

## 1. Cost Boundary

The policy hook is small, but it is hot. The public API already keeps `oneHotMux` and `priorityMux` separate (`src/spatial/lang/api/MuxAPI.scala:26-31`). `OneHotMux.rewrite` folds one selector, literal-true selectors, and identical values, but only warns on multiple literal true selectors before choosing the first one (`src/spatial/node/Mux.scala:21-35`). Dynamic multi-true cases therefore reach backends. Scalagen implements `OneHotMux` as filtered true lanes followed by `reduce{_|_}` (`src/spatial/codegen/scalagen/ScalaGenBits.scala:30-37`), while Chisel uses `Mux1H` and `PriorityMux` separately (`src/spatial/codegen/chiselgen/ChiselGenMath.scala:226-232`). The migration surface includes direct tests (`test/spatial/tests/feature/unit/MuxTest.scala:20-33`), switch lowering (`src/spatial/transform/SwitchOptimizer.scala:65-79`; `src/spatial/transform/FlatteningTransformer.scala:85-95`), alias muxes (`src/spatial/transform/MemoryDealiasing.scala:22-35`; `src/spatial/transform/MemoryDealiasing.scala:90-127`; `src/spatial/transform/MemoryDealiasing.scala:150-159`), streamification (`src/spatial/transform/streamify/HierarchicalToStream.scala:193-203`), and one app-level exact-one use (`test/spatial/tests/apps/Inference.scala:481-483`).

## 2. Policy Cost Matrix

`OR-reduce default` is lowest short-term simulator cost: implement masked raw-value OR, preserve `MuxTest` goldens, and keep Scalagen readback (`ScalaGenBits.scala:30-37`; `MuxTest.scala:20-33`). HLS cost is moderate because the backend must emit masked OR trees rather than trust native one-hot muxes; Chisel precedent currently falls through to `Mux1H` for non-priority fat muxes (`fringe/src/fringe/utils/package.scala:79-81`). Optimizer value is poor: no pass may assume selector exclusivity.

`One-hot assert/reject default` is moderate implementation cost and high semantic payoff. Rust simulation needs `popcount(selects) == 1`, static rejection must upgrade the current warning path (`Mux.scala:25-27`), and HLS debug builds need assertion/failure plumbing. There is local hardware precedent: `AssertIf` ties failed conditions to breakpoints (`src/spatial/codegen/chiselgen/ChiselGenDebug.scala:29-34`). Tests must split legacy OR cases from legal one-hot cases.

`Priority default` is cheap to lower, since the existing `PriorityMux` contract is ordered `if` / `else if` with invalid fallback (`ScalaGenBits.scala:39-45`). It is expensive semantically: it contradicts the dedicated API split (`MuxAPI.scala:26-31`), Chisel's one-hot lowering (`ChiselGenMath.scala:226-232`), and the explicit OR test (`MuxTest.scala:20-33`). Optimizers must preserve lane order, which blocks tree balancing and commutation unless exclusivity is separately proven.

`Dual-mode OR legacy plus strict default/diagnostic` has the highest upfront infra cost but the lowest migration risk. Add a policy enum to Rust simulation and HLS lowering: `strict_onehot`, `compat_or_reduce`, and possibly `priority_as_rewrite`. Record mode, selector count, data type, proof source, and violation counts in manifests/reports. This fits the D-23 manifest shape, which already reserves root `diagnostics`, `compatibility`, and target capability fields (`D-23-research/06-abi-manifest-schema.md:12`) and asks diagnostics to carry source location, op id, dynamic id, policy label, report id, and first-failure records (`D-23-research/06-abi-manifest-schema.md:30`).

`HLS-native` is cheap only as an implementation detail after proof. As a policy, it is high-risk because each tool's `Mux1H`/select lowering may differ on zero-true or multi-true cases. Treat native one-hot, synthesizable assert, and assume support as target capabilities, not semantics.

## 3. Diagnostics, Reports, And Optimizer Assumptions

The Rust simulator should always emit a structured mux event when a strict check fails or when compatibility mode observes `popcount != 1`. Existing warning/error infrastructure has the right shape: warnings can log source context (`argon/src/argon/static/Printing.scala:53-58`), deferred issues become errors if unresolved across pass boundaries (`argon/src/argon/Issue.scala:5-19`; `argon/src/argon/Compiler.scala:84-95`), and codegen reports already support JSON artifacts (`src/spatial/codegen/resourcegen/ResourceReporter.scala:22-24`; `src/spatial/codegen/resourcegen/ResourceCountReporter.scala:19-21`). Optimizers should consume a single fact: `OneHotMux` is exclusive only in `strict_onehot` mode, after static proof, or under an emitted runtime/HLS assert. OR compatibility denies that fact. Priority mode permits first-true reasoning but not commutation.

## 4. Staged Rollout

Stage 0: add policy plumbing and report fields, defaulting to `compat_or_reduce` for readback. Stage 1: run corpus diagnostics, especially switch, dealiasing, streamification, and `Inference` call sites. Stage 2: make `strict_onehot` the Rust/HLS default, keep `compat_or_reduce` behind an explicit flag, and update `MuxTest` into separate OR-compat and strict-violation fixtures. Stage 3: allow HLS-native lowering only when the manifest records proof/check coverage and target capabilities; otherwise lower strict mode to checked masked OR or a checked select tree.
