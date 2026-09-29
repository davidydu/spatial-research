---
"type": "python-mapping"
"construct": "load/store arrows, memory views, slices, transfer par"
"spec_entry": "[[60 - Host and IO]]"
"grammar_rule": "load_stmt, store_stmt, memory_view, view_suffix, slice, transfer_par"
"external_dsl":
  "concepts_without_hardware_meaning":
  - "The load/store keywords and <- punctuation are alternate surface spellings for transfer direction."
  - "Exact selector count and rejection of omitted axes are language rules beyond the hardware idea of a memory\
    \ view."
"per_style":
  "tracing":
    "expressible": "yes"
    "info_preserved":
    - "literal_types"
    - "size_vs_int"
    - "order"
    "error_locus": "ir-check"
    "silently_divergent":
    - "Raw Python endpoint arithmetic runs before view capture."
    - "Using host arrays rather than DSL handles invokes their own slicing/copy/broadcast behavior."
  "builder":
    "expressible": "yes"
    "info_preserved":
    - "literal_types"
    - "size_vs_int"
    - "scope"
    - "order"
    "error_locus": "ir-check"
    "silently_divergent":
    - "Host-computed bounds lose source expression structure before builder invocation."
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
    - "Values imported from host code remain a staging boundary; native host slicing outside the transformed body\
      \ is not a Spatial view."
"obligations_at_risk":
- "Rules 1-5 and 11: endpoint capability, equal type/rank/extents, bounds and source initialization — under R-B:\
  \ shared Rust view/type and obligation passes after either frontend, before lowering."
- "Rules 1-5 and 11: endpoint capability, equal type/rank/extents, bounds and source initialization — under P-E:\
  \ Python view/type and obligation passes after capture, before lowering."
- "Rules 3, 4, 8 and 10: transfer factor divisibility, tail masks, lane disjointness and coverage — under R-B: shared\
  \ Rust legality pass; backend later reports schedule feasibility."
- "Rules 3, 4, 8 and 10: transfer factor divisibility, tail masks, lane disjointness and coverage — under P-E: Python\
  \ legality pass; backend later reports schedule feasibility."
- "Rule 7: FIFO transfer occupancy at every intermediate step — under R-B: shared Rust effect pass at check time;\
  \ executor adds defensive guards."
- "Rule 7: FIFO transfer occupancy at every intermediate step — under P-E: Python effect pass at check time; executor\
  \ adds defensive guards."
"raters":
- "Codex-B"
"verified": ["2026-09-28"]
"status": "draft"
---
## External DSL form
[precedent-measured] Normative grammar, inspected at the pinned revision (spatial-rs@eb49d8b:docs/language-spec.md:131-134; spatial-rs@eb49d8b:docs/language-spec.md:141-147):

```ebnf
load_stmt          = "load" memory_view "<-" memory_view
                     [ transfer_par ] ";" ;
store_stmt         = "store" memory_view "<-" memory_view
                     [ transfer_par ] ";" ;
memory_view        = ident [ view_suffix ] ;
view_suffix        = "[" slice { "," slice } "]" ;
slice              = expr | range ;
range              = expr ".." expr ;
index_suffix       = "[" expr { "," expr } "]" ;
transfer_par       = "par" ( const_expr | par_vector ) [ "tail" ] ;
par_vector         = "[" const_expr { "," const_expr } "]" ;
```

[precedent-measured] Canonical fragment assumes equal element types, matching rank-2 extents, initialized source regions and proven in-bounds endpoints (spatial-rs@eb49d8b:docs/language-spec.md:936-944):

```spatial
load tile[0..rows, 0..cols] <- src[row0..row0 + rows, col0..col0 + cols];
store dst[row0..row0 + rows, col0..col0 + cols] <- tile[0..rows, 0..cols];
```

[judgment] Views and transfer lanes have hardware meaning; `<-` and the exact-rank/no-implicit-axis convention are source choices. They remove host slicing defaults but require learning their own rules (spatial-rs@eb49d8b:docs/language-spec.md:928-934; spatial-rs@eb49d8b:docs/language-spec.md:971-977).

## Python forms

[designed] Tracing uses destination-receiver method calls so destination bounds are captured before source bounds. Handles denote views, never host array copies; factors are Size nodes. The vector/tail suffix shown is an extension of the canonical fragment under the normative transfer rule (spatial-rs@eb49d8b:docs/language-spec.md:963-977).

```python
tile[0:rows, 0:cols].load_from(
    src[row0:row0 + rows, col0:col0 + cols], par=(P0, P1), tail=True
)
dst[row0:row0 + rows, col0:col0 + cols].store_from(tile[0:rows, 0:cols])
```

[designed] Builder makes the transfer operation explicit with destination first; registered handles and the enclosing builder frame retain scope (spatial-rs@eb49d8b:docs/language-spec.md:385-401; spatial-rs@eb49d8b:docs/language-spec.md:963-969).

```python
b.load(tile[0:rows, 0:cols],
       src[row0:row0 + rows, col0:col0 + cols], par=(P0, P1), tail=True)
b.store(dst[row0:row0 + rows, col0:col0 + cols], tile[0:rows, 0:cols])
```

[designed] AST retains explicit load/store calls: ordinary slice assignment alone would leave endpoint direction and transfer schedule implicit. Its checker rejects steps, omitted selectors and broadcasting instead of inheriting host array behavior (spatial-rs@eb49d8b:docs/language-spec.md:928-961).

```python
@spatial_body
def transfers():
    load(tile[0:rows, 0:cols],
         src[row0:row0 + rows, col0:col0 + cols], par=(P0, P1), tail=True)
    store(dst[row0:row0 + rows, col0:col0 + cols], tile[0:rows, 0:cols])
```

[precedent-measured] Exo has actual AST-transformed windows; this inspected test uses a slice at a procedure boundary (exo@defe172:tests/test_codegen.py:135-144):

```python
@proc
def callee(N: size, A: [f32][N]):
    for i in seq(0, N):
        A[i] = 0.0

@proc
def caller():
    A: f32[100]
    callee(10, A[10:20])
```

## Assessment

[designed] All three forms can retain backing-object identity, scalar-axis collapse, bounds, element type and destination/source order. Complete source spans require AST plus source mapping; operator tracing alone sees evaluated bound objects. Python passes slice descriptors to subscription methods, permitting custom view rules ([Python subscriptions](https://docs.python.org/3/reference/expressions.html#subscriptions), accessed 2026-09-28). AST locations can support precise diagnostics if propagated ([Python AST](https://docs.python.org/3/library/ast.html#ast.AST), accessed 2026-09-28). Preservation claims are implementation requirements, not current support (spatial-rs@eb49d8b:docs/language-spec.md:928-969).

[designed] The representative misuse is unequal retained extents: its first report is `ir-check` in each proposal. The same pass must reject wrong endpoint kinds, uninitialized reads and unproved bounds; invocation shape validation cannot replace these proofs. R-B places the authority in its shared Rust core, P-E in a Python DSL checker. Rules 4/5/7/8/10/11 cover rectangle containment, initialization/coverage, FIFO intervals and lane effects (spatial-rs@eb49d8b:docs/language-spec.md:481-567; spatial-rs@eb49d8b:docs/language-spec.md:583-593; spatial-rs@eb49d8b:docs/language-spec.md:946-977).

[judgment] A slice producing the right shape is insufficient: regular transfers snapshot before writes, FIFO transfers stream element by element, and LineBuffer row loads shift after a snapshot. All forms need these distinct effect nodes, with checks before scheduling (spatial-rs@eb49d8b:docs/language-spec.md:954-969).

[precedent-measured] Current whole-view rank-1 transfer support is Narrow; generic rank-2, scalar/range rank collapse and suffix/vector/tail forms remain Specified. The general obligation calculus and evaluation/effect rules also remain Specified (spatial-rs@eb49d8b:docs/language-spec.md:1109-1115).

## Precedent

[precedent-measured] Exo windows preserve an aliasing view through nested slicing and scalar-axis selection in the inspected test; omitted endpoints are accepted there, unlike Spatial's exact selector syntax. This supplies a Python window precedent, not bulk DMA arrows, transfer `par`, or Spatial proof equivalence (exo@defe172:tests/test_codegen.py:757-769; spatial-rs@eb49d8b:docs/language-spec.md:928-934). No precedent test was executed for this rating.
