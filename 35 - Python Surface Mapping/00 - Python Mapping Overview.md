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
surface mapping labels"). The full plan calls for two independent raters per entry; agreement and
adjudication will be recorded here once both ratings exist. The meeting cut
contains one rating per entry, followed by source checking and a separate audit.

Cells: R-X, R-E, R-B, P-X, P-E, P-B (core Rust/Python × surface external/
embedded/both). This folder is the evidence for D-26 angles 2–4 and becomes the
build spec only after an E or B proposal is approved. [[D-26-final-architecture|The current proposal selects R-E]], pending professor approval. These first-rating designs remain evidence, not implemented frontend coverage; the final plan also requires the deferred construct inventory below.

## Embedding styles (summary)

The ratings describe the explicit forms in each entry, including proposed APIs;
they are not measurements of an implemented Spatial Python frontend.

| Style | Allowed subset | Expressibility across 13 entries | All five information categories |
|---|---|---|---|
| Tracing | Expressions, indexing, augmented assignment, method calls | 6 yes, 6 awkward, 1 no (native naming/scope) | 0 entries |
| Builder | Tracing subset plus with-blocks and explicit declaration/control builders | 13 yes | 0 entries; full spans are not automatic |
| AST transform | Ordinary statements interpreted before execution as a closed DSL, with original source/tokens retained | 13 yes, all designed | 13 entries, conditional on the described frontend implementation |

`awkward` means that the example needs a construct outside that style's allowed
subset; it is not an impossibility claim about Python. An explicit literal-tree
wrapper may preserve more information than a bare overloaded expression.
Builder scope means recorded DSL regions, not ordinary Python local scope.
AST ratings require a DSL resolver, typed literals, deterministic declaration
IDs and ordered effect lowering; a decorator or `ast.parse` alone supplies none
of those complete guarantees.

Common silent-divergence hazards are host constant folding and float conversion,
truth conversion/chained comparisons, host loop execution, rebinding a handle
instead of recording a declaration or write, and loss of expression locations.
Native indexed assignment evaluates its RHS before its target, whereas Spatial
requires target indices first; FIFO effects make that difference observable.
Retaining Python-looking syntax while changing scope or order has a teaching
cost even when a transform can implement it faithfully. Entries 30, 90, B0, C0
and D0 give the concrete contracts and pinned evidence.

The external surface also introduces language-only concepts: value-block yields,
`let` versus `:=`, restricted type/const contexts, lexical naming rules, and
proof-sensitive declaration order. These are counted by the same rubric in
[[D-26-02-student-surface-comparison]]. No style is credited with easier learning
from these inventories alone.

Raters: Codex-A rated 10/20/30/40/90/D0; Codex-B rated 50/60/70/80/A0/B0/C0.
Each entry has one rating. Main-session five-claim checks found one corrected
statement about inactive tail lanes (Q167 in [[20 - Open Questions]]). The fresh
citation audit checks support, not inter-rater agreement. A second independent
rating and adjudication remain full-plan work.

## Coverage

| Entry | Grammar rules | Status |
|---|---|---|
| [[10 - Python Controller Bodies]] | `foreach_ctrl, memreduce_ctrl, memfold_ctrl, reduce_expr, fold_expr, value_block` | draft |
| [[20 - Python If Expressions]] | `if_expr, if_stmt` | draft |
| [[30 - Python Assignment]] | `assign_stmt, lvalue` | draft |
| [[40 - Python FSM]] | `fsm_ctrl` | draft |
| [[50 - Python FixPt and Size]] | `fixed_type, const_decl, const_expr` | draft |
| [[60 - Python Bulk IO and Views]] | `load_stmt, store_stmt, memory_view, view_suffix, slice, transfer_par` | draft |
| [[70 - Python Par and Schedules]] | `schedule, foreach_ctrl (par/tail)` | draft |
| [[80 - Python Kernel Ports and Requires]] | `kernel_decl, port_decl, port_type, dram_shape, requires_block` | draft |
| [[90 - Python Naming and Scoping]] | `ident; Names, Scope, And Lifetime section` | draft |
| [[A0 - Python Size to Int Embedding]] | `const_expr vs expr; E0506` | draft |
| [[B0 - Python Literal Typing]] | `value_decl (scalar_type), scalar_literal` | draft |
| [[C0 - Python Fifo Deq Timing]] | `primary (.deq()), fifo_enq_stmt` | draft |
| [[D0 - Python Declaration Order]] | `declaration-ID order; Rule 4` | draft |

Deferred until an E/B cell is chosen: `Lut`/`Reg`/`LineBuffer`/`RegFile`
constructors, `reset_stmt`, `shift_stmt`, `builtin_call`, `.value`, `Bool`,
comments/lexing.
