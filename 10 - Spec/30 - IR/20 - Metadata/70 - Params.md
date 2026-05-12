---
type: spec
concept: Params metadata
source_files:
  - "src/spatial/metadata/params/DSEData.scala:9-219"
  - "src/spatial/metadata/params/ParamDomain.scala:6-44"
  - "src/spatial/metadata/params/package.scala:11-53"
source_notes:
  - "No prior deep-dive note; written directly from source."
hls_status: rework
depends_on:
  - "[[00 - Metadata Index]]"
status: draft
---

# Params

## Summary

Params metadata is the DSE-facing metadata group for parameter sets, top-controller selection, memory-contention scores, restriction predicates, parameter domains, and current parameter values. The global sets `IgnoreParams`, `TileSizes`, `ParParams`, and `PipelineParams` all store `Set[Sym[_]]` and expose `all` plus `+=` appenders through global metadata (src/spatial/metadata/params/DSEData.scala:9-56). `TopCtrl` stores one top controller symbol, while `Restrictions` stores a global set of `Restrict` predicates (src/spatial/metadata/params/DSEData.scala:58-88).

## Fields

- `IgnoreParams`, `TileSizes`, `ParParams`, `PipelineParams`, `TopCtrl`, and `Restrictions` use `GlobalData.Flow`, so their transfer policy is global flow metadata rather than per-symbol mirroring or removal (src/spatial/metadata/params/DSEData.scala:15-18; src/spatial/metadata/params/DSEData.scala:27-30; src/spatial/metadata/params/DSEData.scala:40-43; src/spatial/metadata/params/DSEData.scala:52-55; src/spatial/metadata/params/DSEData.scala:64-67; src/spatial/metadata/params/DSEData.scala:84-87).
- `MemoryContention(contention)` uses `SetBy.Analysis.Self`, and the package getter defaults missing contention to `0` (src/spatial/metadata/params/DSEData.scala:70-76; src/spatial/metadata/params/package.scala:27-29).
- `RangeParamDomain(min, step, max)` and `ExplicitParamDomain(values)` use `SetBy.User`, so user metadata owns the legal parameter domain definitions (src/spatial/metadata/params/ParamDomain.scala:6-22).
- `IntParamValue(v)`, `SchedParamValue(v)`, and `ParamPrior(prior)` use `SetBy.Analysis.Self`, though the package currently implements integer value access through bounds and schedule value access through raw control schedule metadata (src/spatial/metadata/params/ParamDomain.scala:24-44; src/spatial/metadata/params/package.scala:31-44).

## Implementation

`Restrict` is a sealed product-backed predicate interface with an `evaluate()` method, dependency collection over `Sym[_]` product fields, and `dependsOnlyOn` as a dependency-set filter (src/spatial/metadata/params/DSEData.scala:91-95). Its concrete predicates cover less-than, less-equal, divisibility, divisibility by a constant, divisibility of a ceiling quotient, product less-than, and equal-or-one checks (src/spatial/metadata/params/DSEData.scala:104-137). `Restrict.ParamValue.v` calls `x.toInt`, so restriction evaluation relies on the type helper and bounds path for integer extraction (src/spatial/metadata/params/DSEData.scala:96-103; src/spatial/metadata/types.scala:38-42).

`Prior` has `Gaussian`, `Exponential`, `Decay`, and `Uniform` cases, and `SpaceType` has `Ordinal(prior)` and `Categorical(prior)` cases (src/spatial/metadata/params/DSEData.scala:139-147). `Domain[T]` stores a name, id, options, setter, getter, and space type, then exposes indexed lookup, current value, indexed setting, direct value setting, unsafe value setting, and length (src/spatial/metadata/params/DSEData.scala:149-155). `Domain.filter` mutates the active state through the domain setter while testing candidates, so filtering is stateful by design (src/spatial/metadata/params/DSEData.scala:157-160; src/spatial/metadata/params/DSEData.scala:167-167). Integer-domain construction adjusts a `Range` whose start is not step-aligned by adding the original start after the aligned range, while `restricted` also tests whether that original start satisfies the condition (src/spatial/metadata/params/DSEData.scala:189-217).

`ParamDomainOps.getParamDomain` gives explicit domains precedence over range domains, and `paramDomain` defaults to `Left((1,1,1))` when neither is present (src/spatial/metadata/params/package.scala:11-18). The explicit and range setters add their respective `Data` wrappers, while contention uses the same normal metadata path (src/spatial/metadata/params/package.scala:19-29). `getIntValue`, `intValue`, `setIntValue`, and `intValue_=` delegate to `p.getBound`, `p.bound.toInt`, and `p.bound = Expect(d)` rather than reading or writing `IntParamValue` directly (src/spatial/metadata/params/package.scala:31-35). Schedule values are raw control schedules through `getRawSchedule`, `rawSchedule`, `rawSchedule = d`, and `finalizeRawSchedule(d)` (src/spatial/metadata/params/package.scala:37-41). `getPrior` defaults to `Uniform`, and `prior_=` writes `ParamPrior(pr)` (src/spatial/metadata/params/package.scala:43-44).

## Interactions

Params depends on bounds for integer parameter value storage because `ParamDomainOps` imports bounds and stores integer values as `Expect` bounds (src/spatial/metadata/params/package.scala:6; src/spatial/metadata/params/package.scala:31-35). Params depends on control metadata for schedule-valued parameters because `SchedParamValue` is typed as `CtrlSchedule` and the package reads or writes raw control schedules (src/spatial/metadata/params/ParamDomain.scala:34-42; src/spatial/metadata/params/package.scala:37-41).

## HLS notes

DSE domains and restrictions should probably stay compiler-side in Rust+HLS, while concrete selected parameter values should lower into HLS constants or schedule choices only after the parameter search has selected them (inferred, unverified). The current Scala implementation stores integer values through bounds rather than through `IntParamValue`, so the rewrite should resolve whether `IntParamValue` is dead, legacy, or consumed outside this file (src/spatial/metadata/params/ParamDomain.scala:24-32; src/spatial/metadata/params/package.scala:31-35).

## Open questions

- Q-meta-15 asks whether `IntParamValue` and `SchedParamValue` are intentionally bypassed by the package accessors or are legacy metadata shells (src/spatial/metadata/params/ParamDomain.scala:24-42; src/spatial/metadata/params/package.scala:31-41).
