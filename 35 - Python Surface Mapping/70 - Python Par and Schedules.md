---
"type": "python-mapping"
"construct": "par/tail and seq/pipe ii schedule annotations"
"spec_entry": "[[20 - Scheduling Model]]"
"grammar_rule": "schedule, foreach_ctrl (par/tail)"
"external_dsl":
  "concepts_without_hardware_meaning":
  - "The placement of seq/pipe ii before foreach and par/tail after its range is syntax policy."
  - "A closed proof calculus that rejects safe programs outside its derivations is a language acceptance rule, beyond\
    \ a parallelism request."
"per_style":
  "tracing":
    "expressible": "awkward"
    "info_preserved":
    - "literal_types"
    - "size_vs_int"
    - "order"
    "error_locus": "ir-check"
    "silently_divergent":
    - "Running a native Python loop may unroll or execute host work rather than create a symbolic controller."
    - "Host booleans in guards can prune paths before tracing sees them."
  "builder":
    "expressible": "yes"
    "info_preserved":
    - "literal_types"
    - "size_vs_int"
    - "scope"
    - "order"
    "error_locus": "ir-check"
    "silently_divergent":
    - "Raw Python computations of step/par/ii can hide forbidden intermediate const operations."
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
    - "Host-side schedule metaprogramming loses provenance unless explicitly attached to the generated IR."
"obligations_at_risk":
- "Rules 3 and 4: positive step/par/ii and non-tail trip divisibility — under R-B: common Rust const/domain/obligation\
  \ passes before scheduling."
- "Rules 3 and 4: positive step/par/ii and non-tail trip divisibility — under P-E: Python DSL const/domain/obligation\
  \ passes before scheduling."
- "Rules 8, 10 and 11: loop-carried effects, initialization monotonicity, lane disjointness and inactive-tail safety\
  \ — under R-B: shared Rust effect/obligation checker before backend lowering."
- "Rules 8, 10 and 11: loop-carried effects, initialization monotonicity, lane disjointness and inactive-tail safety\
  \ — under P-E: Python effect/obligation checker before backend lowering."
- "Requested II achievement — under R-B: backend scheduler reports diagnostic or warning after static legality."
- "Requested II achievement — under P-E: backend scheduler reports diagnostic or warning after static legality."
"raters":
- "Codex-B"
"verified": ["2026-09-28"]
"status": "draft"
---
## External DSL form
[precedent-measured] Normative grammar, inspected at the pinned revision (spatial-rs@eb49d8b:docs/language-spec.md:116-119):

```ebnf
schedule           = "seq" | "pipe" "ii" const_expr ;
foreach_ctrl       = [ schedule ] "foreach" ident "in" range
                     [ "step" const_expr ]
                     [ "par" const_expr [ "tail" ] ] block ;
```

[precedent-measured] Canonical fragment from `Scale`; `N=32`, `TILE=16`, buffers have the declared extents, and the enclosing load initializes `tile` (spatial-rs@eb49d8b:docs/language-spec.md:35-53):

```spatial
seq foreach base in 0..N step TILE {
  load tile <- src[base..base + TILE];
  foreach lane in 0..TILE par 4 {
    tile[lane] := tile[lane] * scale;
  }
  store dst[base..base + TILE] <- tile;
}
```

[judgment] Lane counts and initiation interval have hardware meaning; keyword placement and the exact accepted proof language do not denote hardware resources. `par` alone promises neither banking nor achieved parallelism (spatial-rs@eb49d8b:docs/language-spec.md:422-431; spatial-rs@eb49d8b:docs/language-spec.md:862-878).

## Python forms

[designed] Tracing is `awkward` for an arbitrary controller body: this nearest form adds an explicit controller/body builder beyond expression tracing. The callback denotes an IR body; it must not execute hardware iterations in Python (spatial-rs@eb49d8b:docs/language-spec.md:839-850; spatial-rs@eb49d8b:docs/language-spec.md:854-878).

```python
loops.foreach(start=Int.literal("0"), end=N, step=Size.literal("1"),
              schedule=Pipe(ii=Size.literal("2")), par=Size.literal("4"),
              tail=True, body=lambda i: tile.at(i).write(tile[i] * scale))
```

[designed] Pure operator hooks cannot capture an ordinary Python `for` statement as a symbolic loop: `for` consumes an iterator under host control ([Python for statement](https://docs.python.org/3/reference/compound_stmts.html#the-for-statement), accessed 2026-09-28). Thus a native statement-preserving `for` is not expressible by tracing alone; callback/control-builder or AST support is the added construct.

[designed] Builder uses a scoped symbolic induction variable. The proposed range is assumed in bounds and initialized; active-tail and dependence proofs still apply (spatial-rs@eb49d8b:docs/language-spec.md:470-480; spatial-rs@eb49d8b:docs/language-spec.md:583-593).

```python
with b.foreach("i", 0, N, step=Size.literal("1"),
               schedule=Pipe(ii=Size.literal("2")),
               par=Size.literal("4"), tail=True) as i:
    b.assign(tile.at(i), tile[i] * scale)
```

[designed] AST uses ordinary statements with a recognized iterator constructor; this is a proposed Spatial frontend, including `tail`, not an existing Allo feature claim (spatial-rs@eb49d8b:docs/language-spec.md:862-878).

```python
@spatial_body
def update():
    for i in foreach(0, N, step=1, schedule="pipe", ii=2, par=4, tail=True):
        tile[i] = tile[i] * scale
```

[precedent-measured] Actual related syntax: Calyx has sequential/parallel control composition; Allo's AST loops accept pipeline/unroll arguments (calyx@d6bcdc8:calyx-py/calyx/builder.py:1739-1766; allo@094ab41:tests/test_schedule_compute.py:391-431).

```python
# Calyx builder, with pre-existing control groups a, b, and c.
cb.seq(a, cb.par(b, c))
# Allo AST form, excerpted from its inline-II test.
def kernel(A: int32[10, 20], B: int32[10, 20]) -> int32[10, 20]:
    C: int32[10, 20] = 0
    for i, j in allo.grid(10, 20, pipeline=4):
        C[i, j] = A[i, j] + B[i, j]
    return C
```

## Assessment

[designed] Frontmatter's `ir-check` means the first report for unproved divisibility or conflicting lane writes. Builders preserve scope only if handle lifetimes and induction-variable use sites are checked; a Python `with` block by itself is not a DSL scope checker. AST source positions can be retained but require explicit IR mapping ([Python AST locations](https://docs.python.org/3/library/ast.html#ast.AST), accessed 2026-09-28; spatial-rs@eb49d8b:docs/language-spec.md:393-401).

[designed] R-B and P-E must implement the same Rule 3 domain arithmetic, Rule 4 entailment, Rule 8 loop transfer and Rule 10 distinct-lane comparison. Pipe cannot silently use the stateful fallback allowed to Seq/Auto; tail masks must restrict all inactive-lane effects. The backend's inability to achieve a legal requested II is a later diagnostic/warning, not permission to alter the program (spatial-rs@eb49d8b:docs/language-spec.md:470-505; spatial-rs@eb49d8b:docs/language-spec.md:533-567; spatial-rs@eb49d8b:docs/language-spec.md:583-593; spatial-rs@eb49d8b:docs/language-spec.md:862-878).

[precedent-measured] Current static `par` is Narrow; canonical `seq`, `pipe ii`, explicit tail masking and the normative proof engine are Specified. Proposed Python expression preservation is not evidence that these Rust checks already exist (spatial-rs@eb49d8b:docs/language-spec.md:1101-1105; spatial-rs@eb49d8b:docs/language-spec.md:1114-1115).

## Precedent

[precedent-measured] The Allo tests inspect generated `pipeline_ii` and `unroll` attributes; their existence establishes source-level schedule representation, not achieved timing or Spatial's masked-lane proof rules. Calyx `par` composes control arms, not Spatial iteration groups. No test or hardware run was performed for this rating (allo@094ab41:tests/test_schedule_compute.py:391-431; calyx@d6bcdc8:calyx-py/calyx/builder.py:1739-1766).
