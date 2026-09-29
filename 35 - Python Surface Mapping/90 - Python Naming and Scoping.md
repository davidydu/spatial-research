---
"type": "python-mapping"
"construct": "cross-cutting: naming, ancestor shadowing forbidden, sibling reuse allowed"
"spec_entry": "[[90 - Aliases and Shadowing]]"
"grammar_rule": "ident; Names, Scope, And Lifetime section"
"external_dsl":
  "concepts_without_hardware_meaning":
  - "Ancestor-shadowing prohibition and sibling-name reuse rule"
  - "One value namespace and DSL-specific binder visibility after initializer"
  - "ASCII identifier/reserved-word policy and separate type/keyword namespace"
"per_style":
  "tracing":
    "expressible": "no"
    "info_preserved":
    - "size_vs_int"
    - "order"
    "error_locus": "silent"
    "silently_divergent":
    - "Python local rebinding loses the previous source binding without an operator hook"
    - "Python if/for/with suites do not create the required lexical child scopes"
    - "An inferred signal name is a display name, not proof of source binding identity"
  "builder":
    "expressible": "yes"
    "info_preserved":
    - "size_vs_int"
    - "scope"
    - "order"
    "error_locus": "ir-check"
    "silently_divergent":
    - "Host aliases and local variable names are not DSL declarations unless explicitly registered"
    - "Pure host initializer arithmetic loses original literal provenance"
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
    - "None in the proposed closed subset; applying Python function-wide name resolution would violate the DSL contract"
"obligations_at_risk":
- "Rules 1/4 declaration identity and earlier-ID facts — under R-B: frontend resolver builds lexical symbols; Rust\
  \ shared-IR checker checks identity/order before proof"
- "Rules 1/4 declaration identity and earlier-ID facts — under P-E: Python DSL resolver builds its own symbol table\
  \ before its obligation checker"
- "Rules 5/8/10/11 lifetime, initialization and iteration-private backing objects — under R-B: Rust checker before\
  \ lowering after lexical region ownership is retained"
- "Rules 5/8/10/11 lifetime, initialization and iteration-private backing objects — under P-E: Python IR checker\
  \ before lowering after lexical region ownership is retained"
- "No duplicates/ancestor shadowing; sibling reuse; after-initializer visibility — under R-B: both frontends resolve\
  \ DSL names before shared-IR checking"
- "No duplicates/ancestor shadowing; sibling reuse; after-initializer visibility — under P-E: Python builder or\
  \ AST resolver before lowering, independently of Python name lookup"
"raters":
- "Codex-A"
"verified": ["2026-09-28"]
"status": "draft"
---
## External DSL form

[precedent-measured] The named EBNF production is `ident`; scope is a semantic section, not another grammar production. `spatial-rs@eb49d8b:docs/language-spec.md:188-196`:

```ebnf
ident              = letter { letter | digit | "_" } ;
```

[precedent-measured] `letter` admits ASCII letters and `_`; reserved words are excluded separately. The normative scope rule is “Duplicate declarations and ancestor shadowing are errors; sibling scopes may reuse a name.” `spatial-rs@eb49d8b:docs/language-spec.md:188-218`, `spatial-rs@eb49d8b:docs/language-spec.md:385-397`.

[precedent-measured] Canonical fragment with nested binders and a local value, quoted from `spatial-rs@eb49d8b:docs/language-spec.md:275-281`; the surrounding example supplies the sizes and memory assumptions at `spatial-rs@eb49d8b:docs/language-spec.md:266-268`:

```spatial
let tiled_sum = fold base in 0..N step TILE init 0 using + {
  load tile <- src[base..base + TILE];
  let tile_sum = reduce lane in 0..TILE par LANES init 0 using + {
    yield tile[lane];
  };
  yield tile_sum;
};
```

[judgment] Shadowing policy, declaration visibility and reserved names are language design choices without direct circuit counterparts. They still affect which symbol a proof/effect refers to. Controller-local allocation does have hardware/semantic meaning because locals are fresh per logical iteration while outer storage is shared: `spatial-rs@eb49d8b:docs/language-spec.md:387-402`.

## Python forms

[precedent-measured] **Tracing, best existing partial form:** Amaranth accepts explicit signal names and otherwise inspects the following bytecode store to infer a name. Its implementation returns a name or fallback; it does not provide the specified lexical symbol table: `amaranth@90449f1:amaranth/hdl/_ast.py:2056-2065`, `amaranth@90449f1:amaranth/tracer.py:16-69`.

```python
from amaranth import Signal
outer = Signal(name="outer")
alias = outer
outer = Signal(name="outer")  # Python rebinding; not a captured DSL redeclaration.
```

[judgment] **Tracing — not expressible for the complete rule using only overloaded expressions/methods and ordinary host bindings.** There is no local-name assignment hook; Python permits rebinding and uses function/module/class blocks, not new scopes for `if`, `for` or `with` suites. Registering explicit symbols/regions is a builder extension; inspecting source is an AST/hybrid extension. This is a boundary of the defined tracing style, not of Python generally. [Python assignment](https://docs.python.org/3/reference/simple_stmts.html#assignment-statements), [execution model: binding and resolution](https://docs.python.org/3/reference/executionmodel.html#naming-and-binding) (accessed 2026-09-28).

[designed] **Builder — yes.** DSL names are explicit strings, handles carry symbol/region identity, and references to expired handles must reject. The builder inserts a name only after lowering its initializer, checks ancestors for duplicates, and treats sibling regions independently. Python `tmp` can be rebound because it is only a host handle. This implements `spatial-rs@eb49d8b:docs/language-spec.md:387-420`.

```python
outer = B.let("outer", B.int(1))
with B.if_stmt(cond) as branch:
    with branch.then_():
        tmp = B.let("tmp", outer + B.int(1))
        output.write(tmp)
    with branch.else_():
        tmp = B.let("tmp", outer - B.int(1))  # Sibling reuse is legal.
        output.write(tmp)
# B.let("outer", ...) inside either branch must reject ancestor shadowing.
# Using either branch's tmp after its region must reject an escaped handle.
```

[designed] **AST — yes.** Capture unexecuted source and replace Python binding resolution with DSL resolution. Both `tmp` annotations are distinct lexical declarations; an inner `outer` declaration rejects. A bare assignment to a declared storage object remains mutation, and an immutable scalar declaration cannot later be assigned. These policies follow `spatial-rs@eb49d8b:docs/language-spec.md:387-397`, `spatial-rs@eb49d8b:docs/language-spec.md:773-791`.

```python
@spatial_ast
def kernel():
    outer: Int = 1
    if cond:
        tmp: Int = outer + 1
        output = tmp
    else:
        tmp: Int = outer - 1
        output = tmp
```

[precedent-measured] Exo provides a real transformed-scope mechanism: annotated declarations create `Sym` objects, each loop pushes/pops its local environment, and each `if` branch gets a separate environment. These are relevant mechanisms, not evidence for the exact no-ancestor-shadowing policy: `exo@defe172:src/exo/frontend/pyparser.py:678-682`, `exo@defe172:src/exo/frontend/pyparser.py:1160-1165`, `exo@defe172:src/exo/frontend/pyparser.py:1215-1252`.

```python
@proc
def branches(flag: bool):
    if flag:
        tmp: i32
    else:
        tmp: i32
```

[judgment] This last snippet uses Exo's inspected declaration/branch syntax as a minimal source form; it was not executed here. No claim is made that its shadowing or identifier rules match Spatial: Exo's symbol-name check itself differs, excluding `_` and using its own regex (`exo@defe172:src/exo/core/prelude.py:9-29`).

## Assessment

[designed] A builder can preserve DSL scope/order/type handles without preserving host source bindings or complete expression spans. The tracing frontmatter therefore omits scope; its `order` is the observed order of DSL object operations only. Amaranth's frame source locator returns filename/line, not full expression spans (`amaranth@90449f1:amaranth/tracer.py:72-77`). AST's all-five preservation is a source/token-backed design, not automatic behavior of a decorator; [Python AST locations](https://docs.python.org/3/library/ast.html#ast.AST) (accessed 2026-09-28).

[designed] Under R-B both frontends must deliver stable lexical symbols, parent regions and declaration ordinals to a Rust checker; under P-E a Python DSL resolver must provide the same information to its checker. Rule 1 normalization and Rule 4 bounds need symbol identity/order; Rules 5/8/10/11 need backing-object identity and iteration-private lifetimes. Python object identity alone does not encode all of those source properties: `spatial-rs@eb49d8b:docs/language-spec.md:433-459`, `spatial-rs@eb49d8b:docs/language-spec.md:481-522`, `spatial-rs@eb49d8b:docs/language-spec.md:533-592`.

[judgment] Silent host rebinding is the tracing first-error rating because it need not report at all. An undefined Python variable can instead raise `NameError`/`UnboundLocalError` at Python time. In the designed builder/AST forms, duplicate names or escaped symbols first fail in DSL resolution/IR checking; later initialization or alias obligations remain IR errors. [Python resolution of names](https://docs.python.org/3/reference/executionmodel.html#resolution-of-names) (accessed 2026-09-28); `spatial-rs@eb49d8b:docs/language-spec.md:385-420`.

## Precedent

[precedent-measured] Source inspection only. Amaranth offers naming heuristics; Calyx has explicit named group construction and an index (`calyx@d6bcdc8:calyx-py/calyx/builder.py:280-303`); Exo offers transformed lexical environments. None of these inspected sources establishes the exact Spatial policy without added checks. Spatial's normative lifetime/definite-assignment rules are at `spatial-rs@eb49d8b:docs/language-spec.md:385-420`; its full obligation calculus remains Specified, not implemented in the current prototype (`spatial-rs@eb49d8b:docs/language-spec.md:1114-1115`). No runtime measurements or independent second rating were performed.
