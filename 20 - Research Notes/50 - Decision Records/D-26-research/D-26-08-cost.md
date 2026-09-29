---
type: "research"
decision: "D-26"
angle: "8"
discriminates: both
sources:
  - "spatial-rs@eb49d8b:docs/superpowers/plans/2026-07-07-compositional-core-inversion-roadmap.md:101-132"
  - "spatial-rs@eb49d8b:docs/superpowers/plans/2026-07-07-compositional-core-inversion-roadmap.md:134-153"
  - "spatial-rs@eb49d8b:crates/spatial-rs-core/src/compiler.rs:30-67"
  - "spatial-rs@eb49d8b:crates/spatial-rs-core/src/validate.rs:34-64"
  - "spatial-rs@eb49d8b:crates/spatial-rs-core/src/oracle.rs:5-81"
  - "spatial-rs@eb49d8b:crates/spatial-rs-core/src/manifest.rs:7-38"
  - "spatial-rs@eb49d8b:examples/ee109/src/bin/run-vitis-validation.rs:26-81"
  - "spatial-rs@eb49d8b:crates/spatial-rs-core/src/diagnostics.rs:3-23"
  - "spatial-rs@eb49d8b:docs/adr/0002-file-cli-host-runtime.md:454-504"
  - "exo@defe172:src/exo/frontend/pyparser.py:38-91"
  - "allo@094ab41:allo/ir/builder.py:93-115"
verified: ["2026-09-28"]
status: draft
---

## Scope

Compare forward work for all six cells at the same milestone: a general controller-tree representation and interpreter matching the existing 39-program oracle corpus. Preserve that architecture when changing the implementation language. Phase-1 parity is distinct from a shipped structural HLS backend, which the roadmap places in Phase 2. Estimates below are work decomposition and conditional judgments, not measured development hours or a staffing study. Shipping and maintenance obligations are shown separately so that a small prototype is not compared with a fully supported alternative.

## Findings

### A common milestone and common assets

[measured] The current compilation path is parse → constant evaluation → HIR → whole-program classification; it does not itself implement the planned general controller-tree interpreter (`spatial-rs@eb49d8b:crates/spatial-rs-core/src/compiler.rs:30-67`). The roadmap requires general lowering and 39-program interpreter/oracle equality while retaining the old classifier path (`spatial-rs@eb49d8b:docs/superpowers/plans/2026-07-07-compositional-core-inversion-roadmap.md:101-132`). Counting all existing Rust code as completed Phase 1 would therefore overstate the starting advantage.

[measured] Existing scalar and tiled operations have executable oracle functions, and the project has structured port/ABI descriptions and a driver that can generate plans without invoking Vitis (`spatial-rs@eb49d8b:crates/spatial-rs-core/src/oracle.rs:5-81`; `spatial-rs@eb49d8b:crates/spatial-rs-core/src/manifest.rs:7-38`; `spatial-rs@eb49d8b:examples/ee109/src/bin/run-vitis-validation.rs:26-81`). These are useful specifications and reference outputs even when their implementation language is not retained.

[judgment] Credit every cell with the language specification, corpus, expected results, recorded backend idioms, validation criteria, and documented JSON/Tcl interfaces. Retaining an implementation can save adaptation work, but a Python core can reuse the *knowledge and evidence* without retaining Rust as its compiler. Conversely, reusing old HLS evidence does not validate newly emitted HLS: structural backend migration has its own equality and fresh-evidence gates (`spatial-rs@eb49d8b:docs/superpowers/plans/2026-07-07-compositional-core-inversion-roadmap.md:134-153`).

### Forward work by option

[designed] This decomposition holds the target architecture and semantic obligations constant. “Adapt” includes tests and integration; “implement” does not imply starting without the shared specification and oracle outputs. External-parser reuse is conditional on reaching canonical grammar parity, not assumed complete merely because the current CLI accepts fixtures (`spatial-rs@eb49d8b:crates/spatial-rs-core/src/compiler.rs:30-67`).

| Cell | Core and Phase-1 work | Student frontend work | Additional parity/operation obligations |
|---|---|---|---|
| R-X | Implement general Rust tree/interpreter/lowering; adapt reusable analysis facts | Finish canonical external parser and diagnostics | Package CLI; maintain one student corpus |
| R-E | Same Rust semantic milestone | Implement Python surface and unchecked-AST ingress into the same semantic passes | Python-origin locations, packaging/binding boundary, required paired lab/message tests |
| R-B | Same Rust semantic milestone | Finish external frontend and add Python frontend | Two supported surfaces, paired corpus, cross-surface diagnostic parity |
| P-X | Implement Python tree/interpreter/checking; translate or replace reusable Rust analysis | Implement external parser in Python | Reproduce source maps, tests and invocation contracts; package Python tool |
| P-E | Same Python semantic milestone | Implement a Python DSL frontend; host syntax does not supply hardware checking | Define host/accelerator boundary; paired lab/message tests required by this protocol |
| P-B | Same Python semantic milestone | Implement external and embedded frontends | Two surfaces and their parity corpus; one shared semantic implementation |

[precedent-measured] A Python AST frontend still owns source recovery and locations: Exo computes source offsets after obtaining and dedenting the function source (`exo@defe172:src/exo/frontend/pyparser.py:38-91`). Allo dispatches on AST node classes and installs MLIR file locations when available, otherwise unknown locations (`allo@094ab41:allo/ir/builder.py:93-115`). These are concrete work categories for E/B designs, not evidence that their exact implementation can be transplanted into Spatial.

### Three maintenance scenarios

[designed] Scenario 1, **a message is wrong in week 3**: for the current Rust implementation, a maintainer changes the Rust diagnostic construction and releases the rebuilt tool; its diagnostic record already separates code, text, help and labels, but that structure alone is not an externally editable message catalog (`spatial-rs@eb49d8b:crates/spatial-rs-core/src/diagnostics.rs:3-23`). Under an R-E/R-B design with the promised external catalog, a TA could edit catalog text without rebuilding the core; implementing and validating that catalog remains work. Under P-* a TA can edit Python text and distribute a tested package update. For every cell, changing the *condition* that raises the error requires semantic code and regression tests, not only wording changes.

[designed] Scenario 2, **add a construct for a new lab**: all cells need a semantic rule, representation, checker, interpreter behavior, examples and negative tests. X adds grammar/parser work; E adds Python interpretation or builder conventions and source mapping; B needs both ingress paths plus their parity tests. A Python AST parser removes the need to lex Python, not the need to define the new hardware construct. The two concrete source-location implementations demonstrate one part of that remaining obligation (`exo@defe172:src/exo/frontend/pyparser.py:38-91`; `allo@094ab41:allo/ir/builder.py:93-115`). A frontend-only TA change can be sufficient only when the existing core already expresses the construct.

[designed] Scenario 3, **Vitis version bump**: the staff member responsible for tool integration reruns vendor validation and inspects logs/reports regardless of core language. The current driver has explicit tool execution and log/report parsing paths (`spatial-rs@eb49d8b:examples/ee109/src/bin/run-vitis-validation.rs:72-97`). Python may match staff tooling familiarity, but it does not eliminate changed pragmas, report formats, resource estimates or hardware validation. Core-language choice matters when the affected emitter/parser must be patched; stable external bundles can keep ordinary course orchestration independent of that choice.

### Integration depth and implementation-size proxies

[judgment] CLI/JSON integration and a packaged binary keep fewer language-boundary interfaces than an in-process binding. Bindings add wrapper and release obligations; notebooks add source-origin handling even without an embedded frontend. ADR 0002 already separates invocation failures, source diagnostics and backend failures, providing a common contract to preserve across packaging choices (`spatial-rs@eb49d8b:docs/adr/0002-file-cli-host-runtime.md:454-504`). Actual install/release effort across the course platforms remains unmeasured here.

[measured] Counting physical lines, including comments and embedded tests, gives 5,363 for the current `validate.rs`, 1,754 for Exo's `pyparser.py`, and 3,778 for Allo's `builder.py`. The first number is **not the size of an implemented general obligation calculus**: its entry point validates accepted adapter shape and kind (`spatial-rs@eb49d8b:crates/spatial-rs-core/src/validate.rs:34-64`). The Python files are frontend-size proxies with different responsibilities, illustrated by their source and AST handling (`exo@defe172:src/exo/frontend/pyparser.py:38-91`; `allo@094ab41:allo/ir/builder.py:93-115`). Counts were obtained with `len(path.read_text().splitlines())` at the recorded revisions; they are inventory, not person-week estimates or a cross-language productivity ratio.

## Implications

### R-X

Likely the smallest immediate integration surface if maintaining the existing Rust frontend is economical. This is a conditional engineering judgment; its student benefit and canonical-parser completion cost need the surface and error studies.

### R-E

Keeps core implementation reuse while adding a frontend and cross-language provenance. It can address Python-facing course needs, but only if those needs justify that new work. Dropping external files from the public course surface does not remove the protocol's paired-test obligations.

### R-B

Buys both entry paths at a recurring corpus/parity cost. Maintaining both surfaces is a product obligation, not merely adding a Python wrapper once.

### P-X

Preserves the external surface while changing who can maintain the core. It incurs reimplementation/adaptation costs but receives the same specification, oracles and backend evidence as R-X.

### P-E

Could reduce routine staff language switching if the maintaining team actually prefers Python. It still needs a real compiler and precise hardware semantics; AST precedents make this plausible, not free or already validated.

### P-B

Combines Python core ownership with the two-surface maintenance burden. It needs evidence that both audiences justify that burden rather than assuming optionality is costless.

## Evidence against

The apparent Rust reuse advantage may be much smaller than repository size suggests because the planned architecture replaces recognition with general compilation. Conversely, moving to Python may save little if maintaining the semantic rules, numerical behavior and vendor backend dominates language-specific work. No timed implementation trial, TA onboarding study, bus-factor measurement, simulator parity benchmark, or multi-platform release trial was performed. A Python-strong future teaching team can reverse an author-centered cost preference. Missing evidence cannot be scored as proof that either core meets the simulator threshold.

## Open questions

- Who will actually maintain semantic code and releases between course offerings, and in which language are they effective?
- How much existing analysis survives the general IR boundary without preserving the classifier architecture?
- Does the course need one or two public surfaces, and who owns the paired examples/catalog?
- What do the deferred installation, maintainer-error and simulator studies show?

## Confidence

Medium on the work decomposition and current implementation boundaries; low on relative completion time. The source-backed inventories are reproducible, but no measured staffing or delivery-time model supports a numeric cost ranking.
