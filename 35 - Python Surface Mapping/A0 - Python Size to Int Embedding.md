---
"type": "python-mapping"
"construct": "cross-cutting: the Size to Int checked embedding (E0506)"
"spec_entry": "[[50 - Data Types]]"
"grammar_rule": "const_expr vs expr; E0506"
"external_dsl":
  "concepts_without_hardware_meaning":
  - "Separate const_expr and expr categories, declaration-before-use, and an implicit context-dependent embedding\
    \ are language staging concepts."
  - "The E0506 diagnostic identifier is compiler interface policy, not a hardware construct."
"per_style":
  "tracing":
    "expressible": "yes"
    "info_preserved":
    - "literal_types"
    - "size_vs_int"
    - "order"
    "error_locus": "ir-check"
    "silently_divergent":
    - "Using a plain Python int for Size erases the origin needed for a use-site E0506 diagnostic."
    - "Wrapping only the final result cannot detect checked-Size overflow or underflow in earlier host operations."
  "builder":
    "expressible": "yes"
    "info_preserved":
    - "literal_types"
    - "size_vs_int"
    - "scope"
    - "order"
    "error_locus": "ir-check"
    "silently_divergent":
    - "Builder arguments computed as ordinary Python integers may already have lost their Size expression tree."
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
    - "Imported host integer constants lack Size declaration provenance unless explicitly marked and validated."
"obligations_at_risk":
- "E0506: Size in runtime expr becomes Int only when value <= Int::MAX — under R-B: shared Rust typed-use checking\
  \ after name/const resolution and before lowering."
- "E0506: Size in runtime expr becomes Int only when value <= Int::MAX — under P-E: Python DSL typed-use checking\
  \ after name/const resolution and before lowering."
- "Rules 1 and 4: do not treat wrapping runtime Int arithmetic as unbounded proof arithmetic — under R-B: shared\
  \ Rust obligation pass after embedding."
- "Rules 1 and 4: do not treat wrapping runtime Int arithmetic as unbounded proof arithmetic — under P-E: Python\
  \ obligation pass after embedding."
- "Rule 3 domain construction and static-step embedding — under R-B: Rust domain/type passes check the Int boundary\
  \ before deriving widened loop progressions."
- "Rule 3 domain construction and static-step embedding — under P-E: Python DSL domain/type passes check the Int\
  \ boundary before deriving widened loop progressions."
"raters":
- "Codex-B"
"verified": ["2026-09-28"]
"status": "draft"
---
## External DSL form
[precedent-measured] Normative grammar, inspected at the pinned revision (spatial-rs@eb49d8b:docs/language-spec.md:149-161; spatial-rs@eb49d8b:docs/language-spec.md:171-176):

```ebnf
expr               = logical_or ;
logical_or         = logical_and { "||" logical_and } ;
logical_and        = equality { "&&" equality } ;
equality           = comparison [ ( "==" | "!=" ) comparison ] ;
comparison         = additive [ ( "<" | "<=" | ">" | ">=" ) additive ] ;
additive           = multiplicative { ( "+" | "-" ) multiplicative } ;
multiplicative     = unary { ( "*" | "/" | "%" ) unary } ;
unary              = ( "!" | "-" ) unary | primary ;
primary            = number | boolean | ident | ident index_suffix
                   | ident "." "value"
                   | ident "." "deq" "(" ")"
                   | builtin_call | reduce_expr | fold_expr | if_expr
                   | "(" expr ")" ;
const_expr         = const_additive ;
const_additive     = const_term { ( "+" | "-" ) const_term } ;
const_term         = const_primary { ( "*" | "/" | "%" ) const_primary } ;
const_primary      = integer | ident | "(" const_expr ")" | const_builtin ;
const_builtin      = ( "min" | "max" | "ceil_div" )
                     "(" const_expr "," const_expr ")" ;
```

[precedent-measured] `E0506` is a typed-use rule, not an EBNF production. The canonical `Scale` excerpt uses `TILE` both as a static shape and as a runtime range endpoint (spatial-rs@eb49d8b:docs/language-spec.md:37-48; spatial-rs@eb49d8b:docs/language-spec.md:602-605):

```spatial
const TILE: Size = 16;
// Inside accel, with the surrounding canonical initialization:
let tile = Sram<Int>[TILE];
foreach lane in 0..TILE par 4 {
  tile[lane] := tile[lane] * scale;
}
```

[judgment] This fragment requires the surrounding load from the full example before its reads. Static shape and runtime bound are different uses even when they name the same constant; the source grammar split is a language staging rule (spatial-rs@eb49d8b:docs/language-spec.md:43-50; spatial-rs@eb49d8b:docs/language-spec.md:712-718).

## Python forms

[designed] Tracing keeps a domain-tagged Size node and makes the checked runtime use explicit. This example is intentionally rejected at `as_int()`: the static constant is within u64, while its runtime use exceeds signed-32 range (spatial-rs@eb49d8b:docs/language-spec.md:597-605).

```python
N = Size.literal("2147483648")
value = N.as_int()  # Proposed checked embedding node; E0506 at IR check.
```

[designed] Builder records an explicit typed-use node, retaining a link to the declaration and the runtime use. `b.embed_int` cannot be a host truncating cast (spatial-rs@eb49d8b:docs/language-spec.md:602-605; spatial-rs@eb49d8b:docs/language-spec.md:712-718).

```python
with b.kernel("Boundary"):
    N = b.const_size("N", b.literal("2147483648"))
    with b.accel():
        value = b.let("value", b.embed_int(N), type=Int)
```

[designed] AST retains the implicit spelling while resolving the identifier differently by use position. Its checker inserts the same embedding node and reports the runtime use span (spatial-rs@eb49d8b:docs/language-spec.md:712-718).

```python
@spatial_kernel
def Boundary():
    N: Size = 2147483648
    with accel():
        value: Int = N
```

[precedent-measured] Exo provides a real typed-size/index precedent, but no identical E0506 operation is established by the inspected sources (exo@defe172:tests/test_codegen.py:118-127; exo@defe172:src/exo/frontend/typecheck.py:38-49):

```python
@proc
def callee(N: size, A: [f32][N]):
    for i in seq(0, N):
        A[i] = 0.0
```

## Assessment

[designed] All three styles can preserve Size versus Int if they prohibit implicit conversion to host integers. The proposed wrapper/builder forms lack automatic exact expression spans; AST nodes can carry those through lowering ([Python AST locations](https://docs.python.org/3/library/ast.html#ast.AST), accessed 2026-09-28). Host `int` has no signed-32 range restriction ([Python data model](https://docs.python.org/3/reference/datamodel.html#the-standard-type-hierarchy), accessed 2026-09-28); its successful computation is not evidence of a valid embedding (spatial-rs@eb49d8b:docs/language-spec.md:597-617).

[designed] The first report for the shown misuse is `ir-check`, in the typed-use phase, after successful const evaluation. A literal defaulting directly to Int is a different typing path. Likewise an outer FixPt expectation does not turn a named Size into a FixPt literal: it synthesizes Int, and nonliteral mixed numeric types do not implicitly convert (spatial-rs@eb49d8b:docs/language-spec.md:643-648; spatial-rs@eb49d8b:docs/language-spec.md:666-718).

[designed] R-B's shared checker and P-E's Python checker must both implement the boundary before Rule 1/4 numeric-fact analysis and Rule 3 domain derivation. Proof arithmetic is unbounded, runtime Int arithmetic wraps, and loop progression is widened only after valid endpoint/step typing; these are three distinct domains (spatial-rs@eb49d8b:docs/language-spec.md:445-458; spatial-rs@eb49d8b:docs/language-spec.md:470-480; spatial-rs@eb49d8b:docs/language-spec.md:854-860).

[precedent-measured] At the pinned compiler revision, E0500-E0505 const work is Narrow, but E0506 typed runtime embedding is explicitly open and constants still lower through host-width aliases. No present E0506 success/failure behavior is inferred from these designed examples (spatial-rs@eb49d8b:docs/language-spec.md:1078-1080).

## Precedent

[precedent-measured] Exo's checker distinguishes size/index arguments from numeric values and preserves size/index categories in admissible affine arithmetic, rejecting nonconstant indexing multiplication. This establishes that a Python AST frontend can represent separate domains; it does not prove Spatial's u64-to-i32 boundary, exact diagnostic or checked const evaluation (exo@defe172:src/exo/frontend/typecheck.py:38-72; exo@defe172:src/exo/frontend/typecheck.py:501-538). No runtime tests were run for this first rating.
