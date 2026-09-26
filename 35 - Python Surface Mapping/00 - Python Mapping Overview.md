---
type: python-mapping-index
project: spatial-spec
date_started: 2026-09-25
---

# Python Surface Mapping — Overview

One entry per discriminating construct of the external DSL
(`spatial-rs@29f7bad8:docs/language-spec.md`, closed EBNF), rated under three
Python embedding styles — tracing, builder, AST transform — on the same rubric
as the external DSL itself. Labels are defined in [[conventions]] ("Python
surface mapping labels"). Two independent raters per entry; agreement and
adjudication are recorded here once both ratings exist.

Cells: R-X, R-E, R-B, P-X, P-E, P-B (core Rust/Python × surface external/
embedded/both). This folder is the evidence for D-26 angles 2–4 and becomes the
build spec only if an E or B cell is chosen.

## Embedding styles (summary)

Filled by the main session after Wave 2 from the entries: the allowed-Python
subset per style, the hazards common to all entries, the "silently divergent"
class.

## Coverage

| Entry | Grammar rules | Status |
|---|---|---|
| [[10 - Python Controller Bodies]] | `foreach_ctrl, memreduce_ctrl, memfold_ctrl, reduce_expr, fold_expr, value_block` | skeleton |
| [[20 - Python If Expressions]] | `if_expr, if_stmt` | skeleton |
| [[30 - Python Assignment]] | `assign_stmt, lvalue` | skeleton |
| [[40 - Python FSM]] | `fsm_ctrl` | skeleton |
| [[50 - Python FixPt and Size]] | `fixed_type, const_decl, const_expr` | skeleton |
| [[60 - Python Bulk IO and Views]] | `load_stmt, store_stmt, memory_view, view_suffix, slice, transfer_par` | skeleton |
| [[70 - Python Par and Schedules]] | `schedule, foreach_ctrl (par/tail)` | skeleton |
| [[80 - Python Kernel Ports and Requires]] | `kernel_decl, port_decl, port_type, dram_shape, requires_block` | skeleton |
| [[90 - Python Naming and Scoping]] | `ident; Names, Scope, And Lifetime section` | skeleton |
| [[A0 - Python Size to Int Embedding]] | `const_expr vs expr; E0506` | skeleton |
| [[B0 - Python Literal Typing]] | `value_decl (scalar_type), scalar_literal` | skeleton |
| [[C0 - Python Fifo Deq Timing]] | `primary (.deq()), fifo_enq_stmt` | skeleton |
| [[D0 - Python Declaration Order]] | `declaration-ID order; Rule 4` | skeleton |

Deferred until an E/B cell is chosen: `Lut`/`Reg`/`LineBuffer`/`RegFile`
constructors, `reset_stmt`, `shift_stmt`, `builtin_call`, `.value`, `Bool`,
comments/lexing.
