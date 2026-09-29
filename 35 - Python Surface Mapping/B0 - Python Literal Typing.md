---
"type": "python-mapping"
"construct": "cross-cutting: bidirectional literal typing / check-mode propagation"
"spec_entry": "[[50 - Data Types]]"
"grammar_rule": "value_decl (scalar_type), scalar_literal"
"external_dsl":
  "concepts_without_hardware_meaning":
  - "Bidirectional synthesize/check modes and literal-only classification are type-system concepts beyond the numeric\
    \ hardware format."
  - "Optional let annotations, decimal-default rejection, and the signed minimum literal exception are source-language\
    \ rules."
"per_style":
  "tracing":
    "expressible": "yes"
    "info_preserved":
    - "literal_types"
    - "size_vs_int"
    - "order"
    "error_locus": "ir-check"
    "silently_divergent":
    - "Bare literal-only subexpressions compute under Python before an overloaded operand is involved."
    - "Decimal float ingress loses the exact source token; casting its final value does not restore contextual per-literal\
      \ conversion."
  "builder":
    "expressible": "yes"
    "info_preserved":
    - "literal_types"
    - "size_vs_int"
    - "scope"
    - "order"
    "error_locus": "ir-check"
    "silently_divergent":
    - "Passing an already folded Python value erases literal-only structure and intermediate per-operator normalization."
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
    - "Keeping only ast.Constant.value loses exact decimal spelling; the proposed implementation must retain the\
      \ original source segment."
"obligations_at_risk":
- "Expected-type propagation, literal-only classification and exact signed-literal checking — under R-B: shared\
  \ Rust bidirectional type checker over preserved expression trees from both frontends."
- "Expected-type propagation, literal-only classification and exact signed-literal checking — under P-E: Python\
  \ DSL bidirectional type checker after AST or graph capture."
- "Same-type operators, exact rational ingress, floor conversion and per-operator wrap — under R-B: shared Rust\
  \ typed IR checker and evaluator/lowering, before and during execution respectively."
- "Same-type operators, exact rational ingress, floor conversion and per-operator wrap — under P-E: Python typed\
  \ IR checker and evaluator/lowering, before and during execution respectively."
- "Rules 1 and 4: only range-proven arithmetic contributes affine facts — under R-B: common Rust obligation pass\
  \ after types are fixed."
- "Rules 1 and 4: only range-proven arithmetic contributes affine facts — under P-E: Python obligation pass after\
  \ types are fixed."
"raters":
- "Codex-B"
"verified": ["2026-09-28"]
"status": "draft"
---
## External DSL form
[precedent-measured] Normative grammar, inspected at the pinned revision (spatial-rs@eb49d8b:docs/language-spec.md:103-103; spatial-rs@eb49d8b:docs/language-spec.md:178-181; spatial-rs@eb49d8b:docs/language-spec.md:184-186):

```ebnf
value_decl         = "let" ident [ ":" scalar_type ] "=" expr ";" ;
scalar_type        = "Int" | "Bool" | fixed_type ;
fixed_type         = "FixPt" "<" signedness "," positive_integer ","
                     positive_integer ">" ;
signedness         = "Signed" | "Unsigned" ;
scalar_literal     = [ "-" ] number | boolean ;
number             = integer [ "." integer ] ;
boolean            = "true" | "false" ;
```

[precedent-measured] Canonical annotated literal from the expression-typing contract (spatial-rs@eb49d8b:docs/language-spec.md:687-693):

```spatial
let gain: FixPt<Signed,24,8> = 1.5;
```

[judgment] The annotation describes the numeric representation. Synthesizing versus checking, classifying literal-only trees and rejecting context-free decimals are additional language concepts the external DSL also teaches (spatial-rs@eb49d8b:docs/language-spec.md:682-710).

## Python forms

[designed] Tracing builds an untyped literal-expression tree first; `.check` propagates the expected type through the whole tree. It must not first evaluate `0.75 * 2` as host arithmetic (spatial-rs@eb49d8b:docs/language-spec.md:682-705).

```python
gain = FixPt(Signed, 24, 8).check(Literal("1.5"))
x = FixPt(Signed, 4, 1).check(Literal("0.75") * Literal("2"))
```

[designed] Builder preserves the same deferred expression tree and declares the expected type at the binding site (spatial-rs@eb49d8b:docs/language-spec.md:682-705).

```python
gain = b.let("gain", b.literal("1.5"), type=FixPt(Signed, 24, 8))
x = b.let("x", b.literal("0.75") * b.literal("2"), type=FixPt(Signed, 4, 1))
```

[designed] AST reads the original tokens and annotation before host execution, and implements Spatial check-mode propagation rather than Python runtime typing (spatial-rs@eb49d8b:docs/language-spec.md:682-710).

```python
@spatial_body
def constants():
    gain: FixPt[Signed, 24, 8] = 1.5
    x: FixPt[Signed, 4, 1] = 0.75 * 2
```

[precedent-measured] Actual partial precedents cover all three mechanisms: Amaranth's shaped constant, Calyx's sized constant expression, and Allo's annotated local (amaranth@90449f1:amaranth/hdl/_ast.py:1550-1618; calyx@d6bcdc8:calyx-py/calyx/builder.py:1700-1707; allo@094ab41:tests/test_types.py:287-294).

```python
# Amaranth operator-valued constant
c = Const(3, 8)
# Calyx builder constant
c = cb.const(8, 3)
# Allo AST annotation
Ty = Fixed(8, 3)
def kernel(A: Ty) -> int32:
    B: Ty = 0
    if A > B and A > 0:
        B = A
    return B
```

## Assessment

[judgment] From the specified floor ingress rule, the designed `x` above is `1`: in check mode `0.75` becomes `0.5` at one fractional bit, then multiplication by `2` yields `1`. Host-first evaluation would produce `1.5` and a different final value. This is specification arithmetic, not a measured run (spatial-rs@eb49d8b:docs/language-spec.md:634-648; spatial-rs@eb49d8b:docs/language-spec.md:695-705). Python evaluates call arguments before calling the DSL ([Python calls](https://docs.python.org/3/reference/expressions.html#calls), accessed 2026-09-28).

[designed] The representative error is a context-free decimal or negative unsigned literal, first reported at `ir-check`. The proposal retains literal_types only with explicit literal trees for tracing/builders or token-backed AST nodes. Source positions support exact ranges but `ast.Constant` alone is not an exact decimal-token store ([Python AST](https://docs.python.org/3/library/ast.html#ast.AST), accessed 2026-09-28). Requiring explicit wrappers is within the allowed expression/call subset, so it is `yes` here, with extra syntax cost stated separately (spatial-rs@eb49d8b:docs/language-spec.md:687-710).

[designed] Both cells must propagate expected types through assignments, constructors, branch yields and literal-only operands; preserve the `-2147483648` exception; and reject nonliteral mixed types. Rules 1/4 may derive affine facts only after the chosen runtime type's possible wrapping is accounted for. R-B's shared Rust checker and P-E's Python checker carry identical obligations (spatial-rs@eb49d8b:docs/language-spec.md:445-458; spatial-rs@eb49d8b:docs/language-spec.md:643-648; spatial-rs@eb49d8b:docs/language-spec.md:682-720).

[precedent-measured] Current integer type/literals are Implemented, but decimal fixed-point literals and complete numeric operator semantics are Specified; annotated Python examples do not demonstrate these features in the current Rust source path (spatial-rs@eb49d8b:docs/language-spec.md:1083-1089; spatial-rs@eb49d8b:docs/language-spec.md:1114-1115).

## Precedent

[precedent-measured] Allo's inspected constant visitor initially assigns `int32`/`float32`; this is not evidence for Spatial's no-default decimal rule or its exact bidirectional algorithm. Amaranth's shaped constants mask/normalize to width, whereas Spatial rejects out-of-range ingress. Calyx's explicit width is another representation precedent, not a literal-ingress proof (allo@094ab41:allo/ir/infer.py:176-189; amaranth@90449f1:amaranth/hdl/_ast.py:1594-1618; calyx@d6bcdc8:calyx-py/calyx/builder.py:1700-1707; spatial-rs@eb49d8b:docs/language-spec.md:643-648). All evidence is source inspection; no runtime or teaching measurement was made.
