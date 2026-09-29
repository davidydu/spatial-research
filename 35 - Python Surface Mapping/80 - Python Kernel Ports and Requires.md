---
"type": "python-mapping"
"construct": "kernel declaration, ports, DRAM shapes, requires"
"spec_entry": "[[90 - Host-Accel Boundary]]"
"grammar_rule": "kernel_decl, port_decl, port_type, dram_shape, requires_block"
"external_dsl":
  "concepts_without_hardware_meaning":
  - "One kernel per source file, ordered declaration blocks, and globally reserved keywords are packaging and parsing\
    \ policy."
  - "Declaration-before-use for runtime dimensions and the restricted requirement-expression grammar are language\
    \ rules, beyond port direction and shape."
"per_style":
  "tracing":
    "expressible": "awkward"
    "info_preserved":
    - "literal_types"
    - "size_vs_int"
    - "order"
    "error_locus": "ir-check"
    "silently_divergent":
    - "Python chained comparisons and and/or request host truth values before a requirement node is complete."
    - "A requirement evaluated on a host scalar becomes a one-time Boolean rather than an invocation predicate."
  "builder":
    "expressible": "yes"
    "info_preserved":
    - "literal_types"
    - "size_vs_int"
    - "scope"
    - "order"
    "error_locus": "ir-check"
    "silently_divergent":
    - "Host Boolean conditions can discard predicates before the builder receives them; symbolic __bool__ must reject."
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
    - "Host-side decorators or defaults can execute before AST capture unless the frontend isolates their evaluation."
"obligations_at_risk":
- "Port directions, earlier-name resolution, requirement grammar and Bool typing — under R-B: each frontend records\
  \ declarations; the shared Rust resolver/type checker validates before IR acceptance."
- "Port directions, earlier-name resolution, requirement grammar and Bool typing — under P-E: Python DSL resolver/type\
  \ checker validates after capture, before lowering."
- "Rules 1, 2, 4 and 11: admitted requires facts justify bounds and all-path output coverage — under R-B: shared\
  \ Rust obligation pass before scheduling, using the closed calculus only."
- "Rules 1, 2, 4 and 11: admitted requires facts justify bounds and all-path output coverage — under P-E: Python\
  \ obligation pass before scheduling, using the closed calculus only."
- "Positive resolved shapes, checked products, exact buffer lengths and E0607 false requirement — under R-B: generated\
  \ host wrapper/interpreter checks the typed manifest at invocation before accelerator allocation."
- "Positive resolved shapes, checked products, exact buffer lengths and E0607 false requirement — under P-E: Python\
  \ or generated host entry checks the same typed manifest at invocation before accelerator allocation."
"raters":
- "Codex-B"
"verified": ["2026-09-28"]
"status": "draft"
---
## External DSL form
[precedent-measured] Normative grammar, inspected at the pinned revision (spatial-rs@eb49d8b:docs/language-spec.md:63-65; spatial-rs@eb49d8b:docs/language-spec.md:70-76):

```ebnf
kernel_decl        = "kernel" ident "{" { const_decl }
                     [ inputs_block ] [ outputs_block ] [ inouts_block ]
                     [ requires_block ] accel_block "}" ;
port_body          = "{" [ port_decl { "," port_decl } ] "}" ;
port_decl          = ident ":" port_type ;
port_type          = scalar_type | "Dram" "<" scalar_type ">" dram_shape ;
dram_shape         = "[" port_dim { "," port_dim } "]" ;
port_dim           = const_expr ;
requires_block     = "requires" "{" { requirement } "}" ;
requirement        = requirement_expr ";" ;
```

[precedent-measured] Canonical kernel-field fragment supplies preconditions for later indexed reads; the constants and inputs have no free names (spatial-rs@eb49d8b:docs/language-spec.md:248-260):

```spatial
const R: Size = 3;
const C: Size = 4;
inputs { row: Int, col: Int }
requires {
  0 <= row && row < R;
  0 <= col && col < C;
}
```

[precedent-measured] A separate canonical port fragment permits earlier scalar-input names as DRAM extents; invocation supplies positive dimensions and exactly matching flat-buffer lengths (spatial-rs@eb49d8b:docs/language-spec.md:236-246):

```spatial
inputs { rows: Int, cols: Int, src: Dram<Int>[rows, cols] }
outputs { dst: Dram<Int>[rows, cols] }
```

[judgment] Direction, extent and preconditions describe execution contracts. One-file packaging, declaration-block order, and contextual resolution of a bare dimension name are additional surface concepts (spatial-rs@eb49d8b:docs/language-spec.md:58-75; spatial-rs@eb49d8b:docs/language-spec.md:201-209).

## Python forms

[designed] Tracing the predicates is possible; declaring the enclosing kernel, named ports and signature requires explicit builder metadata, hence `awkward` for tracing alone. Each `require` here is an ordered, separately stored predicate; no Python `and` is involved (spatial-rs@eb49d8b:docs/language-spec.md:724-736).

```python
k = Kernel("Checked")
rows = k.input("rows", Int)
cols = k.input("cols", Int)
src = k.input("src", Dram(Int, shape=(rows, cols)))
dst = k.output("dst", Dram(Int, shape=(rows, cols)))
k.require(rows > 0)
k.require(cols > 0)
```

[designed] Builder records scope, declaration order, directions and the requirement AST, then enters the accelerator body. The shape/require checks occur on invocation, not while these symbolic ports are declared (spatial-rs@eb49d8b:docs/language-spec.md:727-751).

```python
with b.kernel("Checked") as k:
    rows = k.input("rows", Int)
    cols = k.input("cols", Int)
    src = k.input("src", Dram(Int, shape=(rows, cols)))
    dst = k.output("dst", Dram(Int, shape=(rows, cols)))
    k.require(rows > 0)
    k.require(cols > 0)
    with k.accel():
        body.emit(src, dst)
```

[designed] AST parses the function's signature and assertions without executing them as ordinary Python. Recognized annotation markers supply direction and preserve earlier-parameter references. The body is assumed to provide complete output coverage (spatial-rs@eb49d8b:docs/language-spec.md:201-209; spatial-rs@eb49d8b:docs/language-spec.md:727-751).

```python
@spatial_kernel
def Checked(rows: In[Int], cols: In[Int],
            src: In[Dram[Int, rows, cols]], dst: Out[Dram[Int, rows, cols]]):
    assert rows > 0
    assert cols > 0
    body(src, dst)
```

[precedent-measured] Actual partial precedents: Calyx builder ports use explicit names/bitwidths; Exo transforms function annotations and an initial assertion (calyx@d6bcdc8:calyx-py/calyx/builder.py:115-136; exo@defe172:tests/test_codegen.py:757-765).

```python
# Calyx builder
comp.input("rows", 32)
comp.output("result", 32)
# Exo AST form (body excerpt)
@proc
def bar(n: size, dst: f32[n, n, n]):
    assert n >= 8
    w1 = dst[2:, 3, 1:]
    w2 = w1[0:, 4]
    for n in seq(0, 4):
        w2[n] = 42.0
```

## Assessment

[designed] `error_locus: ir-check` names the first report for a DRAM shape referencing a later or wrong-kind binding, or a requirement reading memory. A well-typed requirement that is false for supplied data is instead `runtime`/E0607, before accelerator state exists. These must remain separate diagnostics in both cells (spatial-rs@eb49d8b:docs/language-spec.md:201-209; spatial-rs@eb49d8b:docs/language-spec.md:727-751).

[judgment] Tracing/builders cannot overload Python's chained-comparison control flow into a complete symbolic requirement; symbolic truth conversion should raise. See [Python comparisons](https://docs.python.org/3/reference/expressions.html#comparisons), accessed 2026-09-28. Amaranth implements that guard (amaranth@90449f1:amaranth/hdl/_ast.py:627-639). AST transformation can reject chains or lower explicitly permitted Boolean syntax before host evaluation; acceptance of Python syntax must not enlarge Spatial's normative requirement node set (spatial-rs@eb49d8b:docs/language-spec.md:727-736; spatial-rs@eb49d8b:docs/language-spec.md:826-829).

[designed] Rule 2 admits only prescribed true-path facts from requirements; Rules 1/4 decide which arithmetic/inequalities remain usable. Passing an arbitrary host `assert` or stronger external solver cannot widen static acceptance. R-B needs one authoritative Rust pass for both surfaces; P-E needs its own equivalent Python pass plus manifest-driven invocation checks (spatial-rs@eb49d8b:docs/language-spec.md:422-469; spatial-rs@eb49d8b:docs/language-spec.md:481-505; spatial-rs@eb49d8b:docs/language-spec.md:589-593). Proposed AST span preservation requires source positions to survive lowering, not only function names ([Python AST](https://docs.python.org/3/library/ast.html#ast.AST), accessed 2026-09-28).

[precedent-measured] Current kernel/ordered-block parsing is Implemented, direction/static-shape handling Narrow, and `requires` plus runtime extents Specified. General proof enforcement remains Specified (spatial-rs@eb49d8b:docs/language-spec.md:1074-1082; spatial-rs@eb49d8b:docs/language-spec.md:1114-1115).

## Precedent

[precedent-measured] Exo demonstrates dependent shape syntax and source assertions; Calyx demonstrates explicit port metadata. Neither cited source establishes Spatial port nonaliasing, E0607 ordering, run-data shape validation, or its restricted proof calculus. The Exo test even reuses `n` as a loop name, a reminder that syntax similarity does not establish identical scope policy (exo@defe172:tests/test_codegen.py:757-769; calyx@d6bcdc8:calyx-py/calyx/builder.py:115-136; spatial-rs@eb49d8b:docs/language-spec.md:385-397). These are inspected precedents, not executed measurements.
