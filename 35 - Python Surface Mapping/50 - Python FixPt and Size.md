---
"type": "python-mapping"
"construct": "FixPt<S,I,F> types and compile-time Size constants"
"spec_entry": "[[50 - Data Types]]"
"grammar_rule": "fixed_type, const_decl, const_expr"
"external_dsl":
  "concepts_without_hardware_meaning":
  - "Reserved type names, angle brackets, semicolon declarations, and a separate const-expression grammar are language\
    \ conventions, not circuit components."
  - "One namespace with declaration-before-use and a ban on ancestor shadowing is a source-language discipline."
"per_style":
  "tracing":
    "expressible": "yes"
    "info_preserved":
    - "literal_types"
    - "size_vs_int"
    - "order"
    "error_locus": "ir-check"
    "silently_divergent":
    - "Unwrapped literal-only arithmetic executes as Python before capture."
    - "A Python float loses the original decimal token before a fixed-point constructor sees it."
  "builder":
    "expressible": "yes"
    "info_preserved":
    - "literal_types"
    - "size_vs_int"
    - "scope"
    - "order"
    "error_locus": "ir-check"
    "silently_divergent":
    - "Raw Python arithmetic passed to a builder is already evaluated; explicit literal/Size nodes are required."
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
    - "Host-computed constants captured from outside the transformed source have lost their original expression\
      \ and literal provenance."
"obligations_at_risk":
- "Checked u64 Size evaluation and positive use sites — under R-B: shared Rust const/type checker after either frontend;\
  \ the Python adapter retains Size nodes and declaration order."
- "Checked u64 Size evaluation and positive use sites — under P-E: Python DSL const/type checker after graph or\
  \ AST capture, before lowering; Python int arithmetic alone does not discharge this."
- "FixPt parameter, ingress, and same-type rules — under R-B: shared Rust typed IR checker before lowering; frontend\
  \ preserves exact decimal tokens and explicit rounding/overflow fields."
- "FixPt parameter, ingress, and same-type rules — under P-E: Python typed IR checker before lowering, with exact-rational\
  \ conversion and per-operator normalization."
- "Rules 1 and 4: retain numeric facts only when no wrapping is established — under R-B: shared Rust obligation\
  \ pass before scheduling."
- "Rules 1 and 4: retain numeric facts only when no wrapping is established — under P-E: Python obligation pass\
  \ before scheduling."
"raters":
- "Codex-B"
"verified": ["2026-09-28"]
"status": "draft"
---
## External DSL form
[precedent-measured] Normative grammar, inspected at the pinned revision (spatial-rs@eb49d8b:docs/language-spec.md:66-66; spatial-rs@eb49d8b:docs/language-spec.md:171-176; spatial-rs@eb49d8b:docs/language-spec.md:179-181):

```ebnf
const_decl         = "const" ident ":" "Size" "=" const_expr ";" ;
const_expr         = const_additive ;
const_additive     = const_term { ( "+" | "-" ) const_term } ;
const_term         = const_primary { ( "*" | "/" | "%" ) const_primary } ;
const_primary      = integer | ident | "(" const_expr ")" | const_builtin ;
const_builtin      = ( "min" | "max" | "ceil_div" )
                     "(" const_expr "," const_expr ")" ;
fixed_type         = "FixPt" "<" signedness "," positive_integer ","
                     positive_integer ">" ;
signedness         = "Signed" | "Unsigned" ;
```

[precedent-measured] Canonical declarations, excerpted from the complete example and the literal-typing example; the `let` belongs inside `accel` (spatial-rs@eb49d8b:docs/language-spec.md:36-44; spatial-rs@eb49d8b:docs/language-spec.md:687-693):

```spatial
const N: Size = 32;
let gain: FixPt<Signed,24,8> = 1.5;
```

[judgment] The frontmatter's extra concepts concern spelling, lexical scope, and staging boundaries; fixed-point format and static capacity have hardware meaning. The no-shadowing/declaration-order discipline is additional language policy (spatial-rs@eb49d8b:docs/language-spec.md:22-33; spatial-rs@eb49d8b:docs/language-spec.md:385-397).

## Python forms

[designed] Tracing: retain typed domain objects and exact token strings. Ordinary bindings below name handles; arithmetic on those handles builds expressions. This preserves the specified distinction without claiming an existing Spatial Python API (spatial-rs@eb49d8b:docs/language-spec.md:595-605; spatial-rs@eb49d8b:docs/language-spec.md:624-660).

```python
N = Size.literal("32")
T = FixPt(Signed, 24, 8)
gain = T.literal("1.5")
```

[designed] Builder: lexical frames and checked declarations are explicit (spatial-rs@eb49d8b:docs/language-spec.md:385-397; spatial-rs@eb49d8b:docs/language-spec.md:643-660).

```python
with b.kernel("Typed"):
    N = b.const_size("N", b.literal("32"))
    with b.accel():
        gain = b.let("gain", b.literal("1.5"), type=FixPt(Signed, 24, 8))
```

[designed] AST: the transform treats the preamble as kernel constants and the nested body as accelerator scope, preserving original numeric tokens as well as the AST. Reading only `ast.Constant.value` is insufficient for exact decimal ingress. Source positions are available through [Python AST node locations](https://docs.python.org/3/library/ast.html#ast.AST), accessed 2026-09-28; the type contract is spatial-rs@eb49d8b:docs/language-spec.md:643-648.

```python
@spatial_kernel
def Typed():
    N: Size = 32
    with accel():
        gain: FixPt[Signed, 24, 8] = 1.5
```

[precedent-measured] Actual related forms: Calyx exposes a signed fixed multiplier constructor; Allo exposes total-bit/fraction-bit fixed types and AST annotations. These are partial precedents, not evidence for Spatial's combined Size and FixPt rules (calyx@d6bcdc8:calyx-py/calyx/builder.py:614-621; allo@094ab41:allo/ir/types.py:215-255; allo@094ab41:tests/test_types.py:287-298).

```python
# Calyx builder: comp is a ComponentBuilder.
comp.pipelined_fp_smult("mul", 32, 24, 8)
# Allo AST style: excerpt of test_fixed_compare.
Ty = Fixed(8, 3)
def kernel(A: Ty) -> int32:
    B: Ty = 0
    if A > B and A > 0:
        B = A
    return B
```

## Assessment

[designed] Frontmatter rates the proposed strict forms: explicit literal nodes retain contextual literal types; distinct Size nodes retain staging; builders carry scope IDs; AST capture can retain all five categories. Tracing alone does not recover original expression spans or lexical declarations. For an out-of-range ingress or invalid width, the first semantic report is `ir-check`; malformed Python calls may fail earlier at Python time. These are design assignments, grounded in the required checks, not measured diagnostics (spatial-rs@eb49d8b:docs/language-spec.md:595-605; spatial-rs@eb49d8b:docs/language-spec.md:626-648).

[judgment] Bare Python integers have unbounded range and Python real literals become host values; wrappers are needed before arithmetic, not after. See [Python numeric types](https://docs.python.org/3/reference/datamodel.html#the-standard-type-hierarchy), accessed 2026-09-28. Consequently `Size(2**64 - 1 + 1)` cannot reconstruct whether the source overflowed in a forbidden intermediate operation (spatial-rs@eb49d8b:docs/language-spec.md:597-605).

[designed] Both R-B and P-E must enforce the same const/type restrictions and the same Rules 1/4 numeric-fact calculus. Neither Rust nor Python host arithmetic establishes the language's overflow policy. A wrapping runtime expression must lose an affine value fact unless the prescribed proof succeeds (spatial-rs@eb49d8b:docs/language-spec.md:422-458; spatial-rs@eb49d8b:docs/language-spec.md:481-505). The enforcement owners and phases are recorded separately above.

[precedent-measured] Current support is narrower: const evaluation is Narrow, E0506 remains open, full fixed types/decimal literals/explicit policy fields are Specified, and the normative calculus is not yet the implemented derivation engine (spatial-rs@eb49d8b:docs/language-spec.md:1078-1089; spatial-rs@eb49d8b:docs/language-spec.md:1114-1115).

## Precedent

[precedent-measured] Allo's `Fixed(bits, fracs)` would require `bits = I + F` when mapping Spatial's parameters; its inspected comparison test explicitly leaves fixed-type lowering unresolved. Calyx's primitive builder proves parameterized fixed arithmetic can be represented in Python, not that it checks Spatial ingress or Size rules (allo@094ab41:allo/ir/types.py:215-255; allo@094ab41:tests/test_types.py:287-298; calyx@d6bcdc8:calyx-py/calyx/builder.py:614-650). Evidence here is source/test inspection only; no runtime measurement or independent agreement is claimed.
