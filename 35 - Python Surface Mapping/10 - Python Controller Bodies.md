---
"type": "python-mapping"
"construct": "controller bodies: foreach / memreduce / memfold / reduce / fold with yield"
"spec_entry": "[[10 - Spec/10 - Language Surface/10 - Controllers|Controllers]]"
"grammar_rule": "foreach_ctrl, memreduce_ctrl, memfold_ctrl, reduce_expr, fold_expr, value_block"
"external_dsl":
  "concepts_without_hardware_meaning":
  - "Separate statement blocks and value blocks with mandatory terminal yield"
  - "Surface-only let and init/using/with/over punctuation; the represented binding, identity, and reduction semantics\
    \ do have hardware meaning"
"per_style":
  "tracing":
    "expressible": "awkward"
    "info_preserved":
    - "size_vs_int"
    - "scope"
    - "order"
    "error_locus": "python-time"
    "silently_divergent":
    - "Pure-Python bound or identity arithmetic is evaluated before tracing"
    - "Native for/yield executes Python iteration/generator semantics; callback tracing must capture one symbolic\
      \ body instead"
  "builder":
    "expressible": "yes"
    "info_preserved":
    - "size_vs_int"
    - "scope"
    - "order"
    "error_locus": "ir-check"
    "silently_divergent":
    - "Host calculations passed as bounds or identities have already lost expression provenance"
    - "A Python if inside a captured body can select elaboration paths unless symbolic truth conversion is rejected"
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
    - "None inside the proposed closed transformed subset; explicitly admitted host escapes would need separate\
      \ checks"
"obligations_at_risk":
- "Rules 3/4/8 domain, divisibility, zero-trip and coverage — under R-B: Rust shared-IR checker before lowering,\
  \ using source-ordered binders supplied by either frontend"
- "Rules 3/4/8 domain, divisibility, zero-trip and coverage — under P-E: Python DSL checker before lowering, not\
  \ the Python range iterator"
- "Rules 5/7/10/11 initialization, FIFO effects, temporary coverage and lane independence — under R-B: Rust shared-IR\
  \ checker before code generation"
- "Rules 5/7/10/11 initialization, FIFO effects, temporary coverage and lane independence — under P-E: Python IR\
  \ checker before code generation"
- "Rules 1/4 plus numeric zero identity and body-effect restrictions — under R-B: frontend retains typed yield/identity\
  \ nodes; Rust type/effect checker checks before lowering"
- "Rules 1/4 plus numeric zero identity and body-effect restrictions — under P-E: Python frontend retains typed\
  \ yield/identity nodes; Python type/effect checker checks before lowering"
"raters":
- "Codex-A"
"verified": ["2026-09-28"]
"status": "draft"
---
## External DSL form

[precedent-measured] Closed EBNF, quoted from `spatial-rs@eb49d8b:docs/language-spec.md:99-100`, `spatial-rs@eb49d8b:docs/language-spec.md:117-123`, and `spatial-rs@eb49d8b:docs/language-spec.md:164-167`:

```ebnf
value_block        = "{" { let_decl | controller | statement }
                     "yield" expr ";" "}" ;
foreach_ctrl       = [ schedule ] "foreach" ident "in" range
                     [ "step" const_expr ]
                     [ "par" const_expr [ "tail" ] ] block ;
memreduce_ctrl     = "memreduce" memory_view "with" memory_view "over"
                     ident "in" range "init" const_expr "using" "+" block ;
memfold_ctrl       = "memfold" memory_view "with" memory_view "over"
                     ident "in" range "using" "+" block ;
reduce_expr        = "reduce" ident "in" range [ "par" const_expr ]
                     "init" const_expr "using" "+" value_block ;
fold_expr          = "fold" ident "in" range [ "step" const_expr ]
                     "init" const_expr "using" "+" value_block ;
```

[precedent-measured] Canonical fragment (with `N=32`, readable `src`, and divisible `LANES=4`), `spatial-rs@eb49d8b:docs/language-spec.md:263-273`:

```spatial
let sum = reduce i in 0..N par LANES init 0 using + {
  yield src[i];
};
```

[judgment] The external surface introduces value-block/statement-block distinctions and `yield` punctuation. Identity, iteration privacy, order and parallel lanes are semantic commitments, not mere syntax costs: `spatial-rs@eb49d8b:docs/language-spec.md:399-402`, `spatial-rs@eb49d8b:docs/language-spec.md:862-910`.

## Python forms

[designed] **Tracing — awkward for the complete construct.** Single-expression contributions fit a lambda, but a general body containing declarations, nested controllers and effects needs a callback function outside the stated tracing subset. `T.capture` below would trace a callback once with symbolic binders and a fresh effect region; it must never run a hardware trip count in Python. The distinction is required by the domain/body semantics at `spatial-rs@eb49d8b:docs/language-spec.md:839-850`, `spatial-rs@eb49d8b:docs/language-spec.md:886-910`.

```python
# Proposed callback-tracing API, not an existing Spatial Python API.
def contribution(i):
    local = src[i] * scale
    return local

def fill(round):
    T.foreach(T.int(0), N, body=lambda i: tmp[i].write(src[round, i]))

T.foreach(T.int(0), N, body=lambda i: dst[i].write(src[i]))
total = T.reduce(T.int(0), N, init=T.size(0), using="+",
                 body=T.capture(contribution))
ordered = T.fold(T.int(0), N, step=T.size(1), init=T.size(0),
                 using="+", body=T.capture(contribution))
T.memreduce(acc, tmp, T.int(0), ROUNDS, init=T.size(0),
            using="+", body=T.capture(fill))
T.memfold(acc, tmp, T.int(0), ROUNDS, using="+", body=T.capture(fill))
```

[judgment] Native Python `yield` is not expressible as a Spatial value-block terminator through operator overloading: it creates/suspends a generator. Lambdas cannot contain statement bodies. These limitations motivate the callback extension, rather than a claim that every Python embedding lacks controllers. [Python yield expressions](https://docs.python.org/3/reference/expressions.html#yield-expressions), [lambdas](https://docs.python.org/3/reference/expressions.html#lambda) (accessed 2026-09-28).

[designed] **Builder — yes.** Explicit regions and yield calls can represent all five forms. Each context below records IR; it does not execute a hardware iteration. The two memory operands remain existing views, with the temporary cleared logically per iteration as required by `spatial-rs@eb49d8b:docs/language-spec.md:414-420`, `spatial-rs@eb49d8b:docs/language-spec.md:886-910`.

```python
with B.foreach(0, N, par=B.size(4)) as i:
    dst[i].write(src[i])
with B.reduce(0, N, init=B.size(0), using="+") as r:
    r.yield_(src[r.index])
with B.fold(0, N, step=B.size(1), init=B.size(0), using="+") as f:
    f.yield_(src[f.index])
with B.memreduce(acc, tmp, 0, ROUNDS, init=B.size(0), using="+") as round:
    with B.foreach(0, N) as i:
        tmp[i].write(src[round, i])
with B.memfold(acc, tmp, 0, ROUNDS, using="+") as round:
    with B.foreach(0, N) as i:
        tmp[i].write(src[round, i])
```

[precedent-measured] Real builder precedent for explicit control, not for Spatial reduction legality: Calyx `static_repeat` and ordered `seq` construct control nodes in `calyx@d6bcdc8:calyx-py/calyx/builder.py:1157-1159`, `calyx@d6bcdc8:calyx-py/calyx/builder.py:1757-1766`.

```python
import calyx.builder as cb
component.control += cb.static_repeat(4, cb.seq(init_group, body_group))
```

[designed] **AST — yes.** A transform can reinterpret ordinary `for`, helper definitions and returns. All shown helpers are DSL syntax markers, resolved before any function body executes; the transform must retain source tokens, resolve `Size` separately, and turn `return` into the terminal value of the captured body. This is an implementation proposal for the grammar above, not current Allo/Spatial support.

```python
@spatial_ast
def kernel():
    for i in foreach(0, N, par=4):
        dst[i] = src[i]
    def term(i):
        local: Int = src[i] * scale
        return local
    total: Int = reduce(0, N, init=0, using="+", body=term)
    ordered: Int = fold(0, N, step=1, init=0, using="+", body=term)
    for round in memreduce(acc, tmp, 0, ROUNDS, init=0, using="+"):
        for i in foreach(0, N):
            tmp[i] = src[round, i]
    for round in memfold(acc, tmp, 0, ROUNDS, using="+"):
        for i in foreach(0, N):
            tmp[i] = src[round, i]
```

[precedent-measured] Allo actually accepts `for` over `range`, `grid`, and `reduction` by AST inspection, and has this reduction-like loop; it is not evidence for Spatial's explicit identity/body-effect contract: `allo@094ab41:allo/ir/builder.py:518-532`, `allo@094ab41:tests/test_schedule_compute.py:10-17`.

```python
def gemm(A: int32[32, 32], B: int32[32, 32]) -> int32[32, 32]:
    C: int32[32, 32] = 0
    for i, j, k in allo.grid(32, 32, 32):
        C[i, j] += A[i, k] * B[k, j]
    return C
```

## Assessment

[designed] Frontmatter preservation rates the proposed complete forms. Tracing/builder retain explicit typed `Size` handles, recorded region scope and captured effect order; they do not recover token-level literals or full expression spans after host evaluation. AST's five entries require an unexecuted source/token-backed frontend; Python provides AST locations, not Spatial typing or legality automatically. [Python AST locations](https://docs.python.org/3/library/ast.html#ast.AST) (accessed 2026-09-28); `spatial-rs@eb49d8b:docs/language-spec.md:393-397`, `spatial-rs@eb49d8b:docs/language-spec.md:667-689`.

[designed] The frontmatter assigns ownership for R-B and P-E: both must check Rules 3/4/8 domain, divisibility, empty-path coverage and stateful fallback; Rules 5/7 track initialization/FIFO state; Rules 10/11 enforce lane independence, body effect limits and complete temporary writes. Neither Python callbacks nor a Rust FFI boundary discharge these obligations. The normative rules are `spatial-rs@eb49d8b:docs/language-spec.md:470-592`; zero identity and reduction-specific restrictions are `spatial-rs@eb49d8b:docs/language-spec.md:880-915`.

[judgment] First-error examples: native symbolic iteration/truth conversion should fail at Python elaboration time in tracing; an incomplete temporary or illegal cross-lane write in either captured form must fail at IR check. Host-folded arithmetic can silently lose the source expression before either checker. The ratings do not claim all misuse has one locus. Python call arguments evaluate before the call: [Python calls](https://docs.python.org/3/reference/expressions.html#calls) (accessed 2026-09-28); symbolic truth rejection is implemented at `amaranth@90449f1:amaranth/hdl/_ast.py:627-639`.

## Precedent

[precedent-measured] Source/test inspection only; no runtime measurements were performed. Calyx demonstrates Python construction of Rust-core control IR, and Allo demonstrates AST loop capture; neither cited example implements the exact five-construct contract. The current Rust prototype marks plain `foreach` Narrow and canonical reductions/folds/memory reductions Specified, with the full obligation engine still Specified: `spatial-rs@eb49d8b:docs/language-spec.md:1101-1115`. These facts do not select a compiler-core language.
