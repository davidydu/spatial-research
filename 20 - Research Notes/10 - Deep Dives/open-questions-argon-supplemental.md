---
type: open-questions
date_started: 2026-04-25
---

# Argon Supplemental Open Questions

## Q-arg-001 - [2026-04-25] RepeatedTraversal uses the original block for inner pass runs

`RepeatedTraversal.process` carries `var blk = block`, but each wrapped pass is invoked as `pass.run(block)` rather than `pass.run(blk)`. If any wrapped pass transforms the block, the next pass appears to receive the original input instead of the accumulated result.

Source: argon/src/argon/passes/RepeatedTraversal.scala:27-40
Blocked by: Need maintainer intent for repeated traversal fixed-point semantics.
Status: open
Resolution:

## Q-arg-002 - [2026-04-25] Codegen chunking depth and backend size limits

`javaStyleChunk` implements direct emission, one-level chunking, and a two-level fallback, then comments on the unimplemented case where a block exceeds `code_window * code_window * code_window`. Need to identify the real backend compiler limit and whether any current generated blocks can exceed the implemented hierarchy.

Source: argon/src/argon/codegen/Codegen.scala:156-158
Blocked by: Backend-specific codegen usage and generated-file size examples.
Status: open
Resolution:

## Q-arg-003 - [2026-04-25] Flt-to-Fix saturating and unbiased conversions share the same node

`Flt.__toFix`, `Flt.__toFixSat`, `Flt.__toFixUnb`, and `Flt.__toFixUnbSat` all stage `FltToFix` with the target `FixFmt`. Need to know whether saturation and unbiased rounding are intentionally no-ops for floating-to-fixed conversion or whether distinct nodes were omitted.

Source: argon/src/argon/lang/Flt.scala:109-119
Blocked by: Numeric conversion semantics expected by Spatial users.
Status: open
Resolution:

## Q-arg-004 - [2026-04-25] Dynamic Vec indexing falls back to index zero

`Vec.apply(i: I32)` uses the constant index when `i` is a `Const`, but otherwise calls `this.apply(0)`. Need to know whether dynamic vector indexing is deliberately unsupported in Argon or whether a dynamic `VecApply` variant should exist.

Source: argon/src/argon/lang/Vec.scala:59-63
Blocked by: Backend support expectations for dynamic vector indexing.
Status: open
Resolution:
