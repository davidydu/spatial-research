---
"type": "python-mapping"
"construct": "cross-cutting: deq() consuming at evaluation, statement-end commit"
"spec_entry": "[[80 - Streaming]]"
"grammar_rule": "primary (.deq()), fifo_enq_stmt"
"external_dsl":
  "concepts_without_hardware_meaning":
  - "The primary-expression versus statement boundary, and left-to-right evaluation policy, are language sequencing\
    \ conventions."
  - "Method spellings and semicolon commit boundaries do not themselves specify physical ready/valid or blocking\
    \ hardware timing."
"per_style":
  "tracing":
    "expressible": "yes"
    "info_preserved":
    - "literal_types"
    - "size_vs_int"
    - "order"
    "error_locus": "ir-check"
    "silently_divergent":
    - "Native Python indexed assignment evaluates RHS before target indices, reversing two consuming expressions\
      \ relative to Spatial."
    - "Ordinary and/or can discard or trigger FIFO effects through host truthiness."
    - "An eager host queue implementation would consume while tracing instead of emitting a runtime effect."
  "builder":
    "expressible": "yes"
    "info_preserved":
    - "literal_types"
    - "size_vs_int"
    - "scope"
    - "order"
    "error_locus": "ir-check"
    "silently_divergent":
    - "A builder that reduces enqueue/dequeue to a net count can hide transient underflow."
    - "Host Boolean evaluation before a statement builder sees an expression can lose effect paths."
  "ast":
    "expressible": "yes"
    "info_preserved":
    - "spans"
    - "literal_types"
    - "size_vs_int"
    - "scope"
    - "order"
    "error_locus": "ir-check"
    "silently_divergent":
    - "Executing the original Python assignment instead of interpreting its AST inherits Python RHS-first target\
      \ evaluation."
"obligations_at_risk":
- "Rule 7 plus evaluation order: prove occupancy for ordered consumes/produces, not only net statement deltas —\
  \ under R-B: shared Rust effect/occupancy checker after capture; executor guards every deq defensively."
- "Rule 7 plus evaluation order: prove occupancy for ordered consumes/produces, not only net statement deltas —\
  \ under P-E: Python effect/occupancy checker after capture; executor guards every deq defensively."
- "Rules 6 and 8: join occupancy intervals across paths and analyze loop transfers — under R-B: common Rust obligation\
  \ pass before lowering."
- "Rules 6 and 8: join occupancy intervals across paths and analyze loop transfers — under P-E: Python obligation\
  \ pass before lowering."
- "Rules 10 and 11: same-FIFO lane conflicts and inactive-tail effects — under R-B: shared Rust lane/effect checker\
  \ before scheduling."
- "Rules 10 and 11: same-FIFO lane conflicts and inactive-tail effects — under P-E: Python lane/effect checker before\
  \ scheduling."
- "Immediate deq and delayed enclosing write/enq commit — under R-B: frontend emits ordered effect IR; Rust evaluator/backend\
  \ preserves it during execution."
- "Immediate deq and delayed enclosing write/enq commit — under P-E: frontend emits ordered effect IR; Python evaluator/backend\
  \ preserves it during execution."
"raters":
- "Codex-B"
"verified": ["2026-09-28"]
"status": "draft"
---
## External DSL form
[precedent-measured] Normative grammar, inspected at the pinned revision (spatial-rs@eb49d8b:docs/language-spec.md:135-135; spatial-rs@eb49d8b:docs/language-spec.md:157-161):

```ebnf
fifo_enq_stmt      = ident "." "enq" "(" expr ")" ";" ;
primary            = number | boolean | ident | ident index_suffix
                   | ident "." "value"
                   | ident "." "deq" "(" ")"
                   | builtin_call | reduce_expr | fold_expr | if_expr
                   | "(" expr ")" ;
```

[precedent-measured] Canonical fragment's FIFO load establishes initial occupancy `TILE`; the surrounding loop executes once per element and the outgoing capacity is `TILE` (spatial-rs@eb49d8b:docs/language-spec.md:354-369):

```spatial
let incoming = Fifo<Int>[TILE];
let outgoing = Fifo<Int>[TILE];
load incoming <- src[base..base + TILE];
foreach lane in 0..TILE {
  outgoing.enq(incoming.deq() * scale);
}
store dst[base..base + TILE] <- outgoing;
```

[judgment] FIFO ordering has hardware meaning, but evaluation/commit points are source semantics. The specified model does not claim ready/valid handshaking, blocking behavior or cycle timing; those are deferred (spatial-rs@eb49d8b:docs/language-spec.md:793-799; spatial-rs@eb49d8b:docs/language-spec.md:831-837).

## Python forms

[designed] Tracing emits effectful dequeue nodes chained in evaluation order; it does not pop a host queue. `.enq` seals the enclosing statement. The second line shows the method-call form needed when both destination index and RHS consume; assumptions about queue values/bounds must still be proven (spatial-rs@eb49d8b:docs/language-spec.md:818-837).

```python
outgoing.enq(incoming.deq() * scale)
dst.at(indices.deq()).write(values.deq())
```

[designed] Builder gives each statement an explicit boundary and an ordered destination-before-RHS argument list; the context's exit seals IR, not a host-side queue mutation (spatial-rs@eb49d8b:docs/language-spec.md:831-837).

```python
with b.statement():
    b.enq(outgoing, b.deq(incoming) * scale)
with b.statement():
    b.assign(dst.at(b.deq(indices)), b.deq(values))
```

[designed] AST can use natural assignment but must deliberately lower target indices before RHS to match Spatial. It must never run this body under ordinary Python assignment semantics (spatial-rs@eb49d8b:docs/language-spec.md:831-837).

```python
@spatial_body
def effects():
    outgoing.enq(incoming.deq() * scale)
    dst[indices.deq()] = values.deq()
```

[precedent-measured] Actual Allo AST/dataflow syntax uses typed `Stream` plus `put`/`get`; the excerpt assumes the outer region's stream declaration and dimensions (allo@094ab41:tests/dataflow/test_df_unit.py:13-25):

```python
stream: Stream[UInt(B * 8), 4]

@df.kernel(mapping=[1], args=[A])
def load(local_A: UInt(B * 8)[M, N]):
    for mt, nt in allo.grid(M, N):
        stream.put(local_A[mt, nt])

@df.kernel(mapping=[1], args=[C])
def store(local_C: UInt(B * 8)[M, N]):
    for mt, nt in allo.grid(M, N):
        local_C[mt, nt] = stream.get()
```

## Assessment

[judgment] Python assignment evaluates RHS before target expressions ([Python evaluation order](https://docs.python.org/3/reference/expressions.html#evaluation-order), accessed 2026-09-28). Thus `dst[q.deq()] = q.deq()` reverses which queue item becomes index versus value unless transformed. A tracing `.at(...).write(...)` chain or builder argument order can preserve Spatial sequencing without recovering native statement boundaries (spatial-rs@eb49d8b:docs/language-spec.md:831-835).

[designed] For an empty `q`, `q.enq(q.deq())` must fail at the dequeue even though net occupancy is unchanged; for a full nonempty `q`, the consume precedes the append. The representative first report is `ir-check`, using ordered effects and occupancy proof, with runtime underflow/overflow only defensive. Statement-end transfer bookkeeping must not cancel a consume against a later produce before checking legality (spatial-rs@eb49d8b:docs/language-spec.md:528-532; spatial-rs@eb49d8b:docs/language-spec.md:793-799; spatial-rs@eb49d8b:docs/language-spec.md:831-837).

[designed] Rules 6/8 join and propagate occupancy across branches/loops; Rule 10 treats same-FIFO parallel consume/produce as conflicting after adding each tail mask's active-lane predicate. Masked-off lanes do not execute FIFO effects. R-B and P-E need the same ordered effect IR and proof rules, although one owns them in Rust and the other in Python. None of the proposed Python APIs currently demonstrates those implementations (spatial-rs@eb49d8b:docs/language-spec.md:523-567; spatial-rs@eb49d8b:docs/language-spec.md:583-593; spatial-rs@eb49d8b:docs/language-spec.md:863-878).

[designed] The tracing example retains operation order but not arbitrary source statement spans or lexical scope; explicit builder frames supply scope; AST locations can preserve full source spans if carried through effect lowering ([Python AST](https://docs.python.org/3/library/ast.html#ast.AST), accessed 2026-09-28). Host truth conversion should reject symbolic values before it silently prunes an effectful path; Amaranth's guard is an inspected example of such a failure mode being made explicit (amaranth@90449f1:amaranth/hdl/_ast.py:627-639).

[precedent-measured] Current FIFO enq/deq representation is Narrow, canonical `Fifo` spelling is still Specified, and the general obligation/evaluation contracts remain Specified. Source-level examples are not current compiler or hardware timing measurements (spatial-rs@eb49d8b:docs/language-spec.md:1093-1095; spatial-rs@eb49d8b:docs/language-spec.md:1114-1115).

## Precedent

[precedent-measured] Allo's inspected tests contain stream put/get calls, generated HLS stream assertions, and a separate simulator test. They establish API syntax and checked test intent; these tests were not executed here and do not establish Spatial's intra-statement dequeue exception, static occupancy calculus or nonblocking semantics (allo@094ab41:tests/dataflow/test_df_unit.py:13-31; allo@094ab41:tests/dataflow/test_df_unit.py:42-62). No exact full-contract precedent was established in the inspected sources.
