---
type: research
decision: D-13
angle: 10
---

# D-13 Recommendation Matrix

## Evidence Baseline

Q-139 asks whether HLS lowering must preserve `PipeInserter`'s explicit `Reg` / `FIFOReg` / `Var` holders or may erase them into SSA when legal (`Spatial Research/20 - Research Notes/20 - Open Questions.md:1988-1998`). Inner-stage escapees are written inside a generated `Pipe`, read afterward, and downstream users are substituted to the read (`src/spatial/transform/PipeInserter.scala:170-209`; [[01-pipe-inserter-mechanics]]). Holder selection is deliberate: stream-bit escapees use `FIFOReg`, other bit escapees use `Reg`, and non-bit escapees use `Var` (`src/spatial/transform/PipeInserter.scala:256-305`; [[50 - Pipe Insertion]]). The holders are not pure names: `FIFORegDeq` is destructive, `RegWrite` writes memory, and `VarAssign` writes mutable state (`src/spatial/node/Reg.scala:17-47`, `argon/src/argon/node/Var.scala:7-44`; [[02-holder-node-semantics-codegen]]).

## Matrix

| Option | Correctness | Compatibility | HLS Performance | Implementation Cost | Diagnostics / Provenance |
|---|---|---|---|---|---|
| Preserve all holders as semantic | Highest conservative correctness: write/read, reset, enable, and dequeue effects remain observable. Especially protects `FIFOReg` ordering and empty/full behavior (`src/spatial/codegen/chiselgen/ChiselGenMem.scala:202-224`; [[04-tests-apps-evidence]]). | Best match for existing consumers: scheduling, banking, unrolling, reports, Scalagen, and Chiselgen all recognize holder opcodes ([[03-downstream-consumers]]). | Potentially pessimistic. Extra scalar storage or FIFO channels may block HLS collapse to wires/registers. | Medium. Lower each holder directly, but model three families. | Strong. Reports can point to holder id, origin stage, read/write pair, and source context. |
| Optimize all to SSA | Weak correctness. It erases the effect boundary and is unsafe for `FIFOReg` destructive reads and stream pressure (`src/spatial/node/Reg.scala:23-45`; [[06-spec-open-question-contract]]). | Poor. Downstream passes use memory identity, activity lanes, and holder opcodes; early SSA hides those anchors ([[03-downstream-consumers]]). | Best only in trivial cases; unsafe wins do not count. | Low superficially, high later because semantics must be rediscovered through barriers. | Weak. The backend loses a natural explanation for pipe-boundary values. |
| Classify holders by semantics | High if conservative: `FIFOReg` semantic by default; `Reg` semantic when reset, priority, loop lifetime, enable, or scheduling dependence matters; `Var` flattenable only when its rewrite/effect rule proves equivalence (`argon/src/argon/node/Var.scala:15-44`; [[02-holder-node-semantics-codegen]]). | Good. Preserves observable cases while avoiding Chisel-specific artifacts. | Good. Private `Reg`/`Var` escapes can become SSA or scalars; stream tokens stay channels. | Medium-high. Requires a classifier and conservative unknown handling. | Good. Diagnostics should name the class, reason, and blocking effects. |
| HLS-native mapped holders | High when semantic boundaries survive but physical form is native: `FIFOReg` as one-token channel/FIFO, `Reg` as scheduled scalar register, `Var` as local mutable state when not hardware-visible ([[05-hls-alternatives-optimization]]). | Medium-high. Respects Spatial semantics without literal Spatial nodes in final C++/Rust HLS. | Often best practical option: HLS infers registers/channels while barriers remain. | High. Needs target rules for depth, reset, lifetime, dataflow, and deadlock behavior. | Strong if source holder -> HLS object mapping records depth/lifetime. |
| Proof-based elimination | Highest long-term correctness and performance after classification. Eliminate only compiler-created private holders with one dynamic producer and consumer, overwritten before read, no stream parent, no reset/status/priority, and preserved anti-dependencies ([[05-hls-alternatives-optimization]]; [[20 - Scheduling Model]]). | High. Semantic consumers see holders until proof says identity is unneeded. | Best legal performance: SSA only where storage is unobservable. | High. Requires effect, lifetime, control, and provenance proofs. | Best. Each removal can carry a proof certificate or explicit "not eliminated because..." reason. |

## Read Of The Matrix

The options are not fully exclusive. "Preserve all" is the safe baseline, and "optimize all to SSA" should be rejected as a contract because it contradicts source effects and vault specs. The useful design is staged: classify semantics first, map surviving holders to HLS-native constructs, then run proof-based elimination. That resolves the ambiguity in [[50 - Pipe Insertion]], where HLS can often infer registers through SSA but the source and existing backends still make holder effects observable.

## Preliminary Recommendation

Preliminarily choose: **holders are semantic until classified and proven otherwise**. `FIFOReg` should remain observable by default because it carries dequeue/enqueue ordering, activity, and stream-pressure evidence. `Reg` should remain observable across reset, enable, multiple-writer, loop-lifetime, or retiming boundaries, but can become SSA for private one-write/one-read pipe escapes. `Var` is the most plausible SSA candidate, but only when the Argon `VarRead` rewrite/effect model already proves the assign/read pair is local and unconditional. The final D-13 decision should require provenance: original escape symbol, inserted holder kind, parent control, HLS mapping, and any elimination proof.
