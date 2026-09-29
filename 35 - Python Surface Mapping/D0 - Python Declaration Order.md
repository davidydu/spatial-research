---
"type": "python-mapping"
"construct": "cross-cutting: declaration-ID order (obligation Rule 4)"
"spec_entry": "[[10 - Effects and Aliasing]]"
"grammar_rule": "declaration-ID order; Rule 4"
"external_dsl":
  "concepts_without_hardware_meaning":
  - "Declaration-ID ordering as a normative proof-algorithm convention"
  - "The restriction that oriented bounds mention only earlier declaration IDs"
  - "Source declaration order is not interchangeable with object allocation order or identifier spelling"
"per_style":
  "tracing":
    "expressible": "awkward"
    "info_preserved":
    - "size_vs_int"
    - "scope"
    - "order"
    "error_locus": "ir-check"
    "silently_divergent":
    - "Object creation order can differ from source binding order after aliases, helpers or host conditionals"
    - "Python rebinding can remove declaration events from the trace"
    - "Host-folded constants lose source dependency information"
  "builder":
    "expressible": "yes"
    "info_preserved":
    - "size_vs_int"
    - "scope"
    - "order"
    "error_locus": "ir-check"
    "silently_divergent":
    - "Allocating IDs on Python object construction instead of ordered DSL declaration attachment would change proof\
      \ order"
    - "Unordered host collections can determine a different declaration sequence"
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
    - "None inside the proposed source-ordered transformed subset; generated declarations need an explicit deterministic\
      \ insertion rule"
"obligations_at_risk":
- "Rule 1 normalized affine term ordering by declaration ID — under R-B: both frontends preserve ordered declarations;\
  \ Rust shared checker assigns or verifies IDs before normalization"
- "Rule 1 normalized affine term ordering by declaration ID — under P-E: Python DSL resolver assigns deterministic\
  \ IDs before its normalizer runs"
- "Rule 4 greatest-ID elimination, coefficient and earlier-ID restrictions — under R-B: Rust shared-IR entails implementation\
  \ before any backend accepts a proof"
- "Rule 4 greatest-ID elimination, coefficient and earlier-ID restrictions — under P-E: Python DSL entails implementation\
  \ before any backend accepts a proof"
- "Rules 5-11 every bounds, initialization, disjointness and schedule proof that calls entails — under R-B: Rust\
  \ shared checker before lowering; no stronger-solver widening"
- "Rules 5-11 every bounds, initialization, disjointness and schedule proof that calls entails — under P-E: Python\
  \ checker before lowering; no stronger-solver widening"
"raters":
- "Codex-A"
"verified": ["2026-09-28"]
"status": "draft"
---
## External DSL form

[precedent-measured] “Declaration-ID order; Rule 4” names a semantic obligation, not a closed-EBNF production. The relevant declaration productions are quoted here rather than inventing a grammar rule: `spatial-rs@eb49d8b:docs/language-spec.md:66-66`, `spatial-rs@eb49d8b:docs/language-spec.md:101-103`.

```ebnf
const_decl         = "const" ident ":" "Size" "=" const_expr ";" ;
let_decl           = memory_decl | value_decl ;
memory_decl        = "let" ident "=" memory_ctor ";" ;
value_decl         = "let" ident [ ":" scalar_type ] "=" expr ";" ;
```

[precedent-measured] Canonical ordered declarations from the spec's requirement fragment: `spatial-rs@eb49d8b:docs/language-spec.md:253-260`.

```spatial
const R: Size = 3;
const C: Size = 4;
inputs { row: Int, col: Int }
requires {
  0 <= row && row < R;
  0 <= col && col < C;
}
```

[precedent-measured] Rule 1 says “Affine terms are sorted by declaration ID and zero coefficients removed.” Rule 4 selects the greatest-ID symbol, permits oriented bounds only through earlier IDs, and restricts the greatest-ID coefficient to `1` or `-1`; other comparisons remain direct facts. `spatial-rs@eb49d8b:docs/language-spec.md:445-459`, `spatial-rs@eb49d8b:docs/language-spec.md:481-505`.

[judgment] This is a proof-language concept without direct hardware meaning, and therefore a cost for the external DSL as well as embeddings. It cannot be replaced by alphabetical ordering or a more powerful solver without changing the stated v1 acceptance contract: `spatial-rs@eb49d8b:docs/language-spec.md:424-443`, `spatial-rs@eb49d8b:docs/language-spec.md:489-505`.

## Python forms

[designed] **Tracing — awkward for source declaration order.** Bare object tracing observes allocations and calls, not every Python binding. The faithful extension records explicit declaration events in an ordered lexical region; those events are builder operations outside the defined expression-only tracing surface. For example, even if prototypes were created in another order, these registrations determine DSL declaration order. This design serves the source visibility rule and Rule 4, `spatial-rs@eb49d8b:docs/language-spec.md:393-397`, `spatial-rs@eb49d8b:docs/language-spec.md:489-499`.

```python
# Proposed extension: these are DSL declaration events, not inferred host stores.
row = T.declare("row", row_prototype)
col = T.declare("col", col_prototype)
T.require(row <= col)
```

[judgment] Unextended tracing is not expressible as exact source-binding observation: `alias = row` and later `row = other` need not call an overloaded method. Python binding/resolution can therefore erase information before IR construction. [Python assignment](https://docs.python.org/3/reference/simple_stmts.html#assignment-statements), [naming and binding](https://docs.python.org/3/reference/executionmodel.html#naming-and-binding) (accessed 2026-09-28). Consistent with the other entries, the frontmatter rates the displayed designed extension: explicit ordered lexical registration preserves DSL scope and declaration order in principle. Bare tracing preserves neither; needing that builder extension is why the expressibility rating remains `awkward`.

[designed] **Builder — yes.** Attach declarations in explicit region order, then assign/verify ordinals before proof normalization; do not assign normative IDs when arbitrary Python wrapper objects happen to be allocated. `B.const`, `B.input` and `B.let` must preserve order, scope and after-initializer visibility. Source dependencies: `spatial-rs@eb49d8b:docs/language-spec.md:393-397`, `spatial-rs@eb49d8b:docs/language-spec.md:445-459`, `spatial-rs@eb49d8b:docs/language-spec.md:489-499`.

```python
R = B.const("R", Size, 3)
C = B.const("C", Size, 4)
row = B.input("row", Int)
col = B.input("col", Int)
B.require(row <= col)
program = B.finish()  # Resolve ordered declarations before normalization.
```

[precedent-measured] Calyx's actual API records input/output declaration insertion by append, and explicit ordered control by Python lists/`seq`; it demonstrates ordered IR construction, not Spatial Rule 4. `calyx@d6bcdc8:calyx-py/calyx/builder.py:164-172`, `calyx@d6bcdc8:calyx-py/calyx/builder.py:1108-1141`, `calyx@d6bcdc8:calyx-py/calyx/builder.py:1757-1766`.

```python
component.control += cb.seq(first_group, second_group)
```

[designed] **AST — yes.** Use source-order declaration traversal with stable lexical identities, retaining original source/tokens before transformations. A reordering optimization must retain these original proof IDs. Typed `Size` declarations are identified before ordinary runtime expressions; markers below are proposed Spatial syntax, not an existing API. Required source order and normalization rules: `spatial-rs@eb49d8b:docs/language-spec.md:201-209`, `spatial-rs@eb49d8b:docs/language-spec.md:393-397`, `spatial-rs@eb49d8b:docs/language-spec.md:445-459`.

```python
@spatial_ast
def kernel(row: Int, col: Int):
    earlier: Int = row + 1
    later: Int = col + 1
    require(earlier <= later)
```

[precedent-measured] Exo creates a fresh `Sym` for each parsed annotated declaration; the symbol has a monotonically incremented identity. This is a useful identity mechanism, not proof of source-local normative ordinal equivalence: its counter is class-wide and its `<` comparison orders by name then ID. `exo@defe172:src/exo/frontend/pyparser.py:1160-1165`, `exo@defe172:src/exo/core/prelude.py:21-42`.

```python
@proc
def example():
    earlier: i32
    later: i32
```

## Assessment

[designed] In R-B, both surfaces must provide the same ordered lexical declaration model and a Rust shared checker must assign or verify stable proof IDs; in P-E, the Python DSL resolver/checker must do the same. These are proposed responsibilities, not properties guaranteed by Rust or Python. Rule 1 normalization, Rule 4 oriented bounds/substitution, and every later `entails` call depend on that model: `spatial-rs@eb49d8b:docs/language-spec.md:429-459`, `spatial-rs@eb49d8b:docs/language-spec.md:481-505`.

[judgment] The direction restriction is concrete: with `id(row) < id(col)`, the fact `row <= col` can orient a lower bound for `col` mentioning earlier `row`; it cannot orient an upper bound for `row` mentioning later `col`. This follows from Rule 4, but does not assert an experimentally demonstrated program-acceptance difference under reordering; direct facts and alternate proof paths can still prove particular goals. `spatial-rs@eb49d8b:docs/language-spec.md:487-505`.

[designed] A builder's `order` rating refers to explicit DSL attachment order, not host allocation time. AST's all-five rating requires original-token retention plus the proposed resolver; Python AST ordered statement lists/locations supply raw material, not Rule 4. Tracing/builder still lose original literal provenance under host evaluation. [Python AST node fields and locations](https://docs.python.org/3/library/ast.html#ast.AST), [Python evaluation order](https://docs.python.org/3/reference/expressions.html#evaluation-order) (accessed 2026-09-28).

[judgment] The first expected report of an unsupported proof is IR-check. A malformed frontend can silently encode incorrect IDs and make that report wrong or absent; the checker needs ordered declarations/provenance to detect the mismatch. Comparing normalized proof traces across equivalent external/builder/AST programs would test this design, but no such experiment was run here. That proposed check follows the fixed acceptance restriction in `spatial-rs@eb49d8b:docs/language-spec.md:424-443`, `spatial-rs@eb49d8b:docs/language-spec.md:481-505`.

## Precedent

[precedent-measured] Source inspection only; Calyx supplies ordered construction and Exo supplies fresh lexical symbols, neither inspected source implements this exact obligation calculus. The Rust prototype itself marks the calculus Specified and says its current facts are partial evidence: `spatial-rs@eb49d8b:docs/language-spec.md:1114-1115`. Accordingly these entries are a single Codex-A draft rating, with no runtime measurements or independent verification claimed.
