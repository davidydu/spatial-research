---
"type": "python-mapping"
"construct": "if expressions and if statements"
"spec_entry": "[[30 - Control Semantics]]"
"grammar_rule": "if_expr, if_stmt"
"external_dsl":
  "concepts_without_hardware_meaning":
  - "Separate if-statement and if-expression grammar"
  - "Mandatory yield at the end of each value branch and braces/semicolons"
"per_style":
  "tracing":
    "expressible": "awkward"
    "info_preserved":
    - "size_vs_int"
    - "scope"
    - "order"
    "error_locus": "python-time"
    "silently_divergent":
    - "Native conditional expressions and and/or use Python truth testing"
    - "Passing eager effectful expressions to a mux can capture both effects outside branch regions"
    - "Pure-literal conditions or arithmetic are evaluated before tracing"
  "builder":
    "expressible": "yes"
    "info_preserved":
    - "size_vs_int"
    - "scope"
    - "order"
    "error_locus": "ir-check"
    "silently_divergent":
    - "Host work inside each with-block runs during construction of both branches"
    - "A native Python if inside a builder block can silently choose a host-only path"
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
    - "None inside the proposed closed transformed subset; a select-style lowering of effectful branches would be\
      \ a frontend correctness bug"
"obligations_at_risk":
- "Rules 2/4/6 condition facts and branch joins — under R-B: Rust shared-IR checker before lowering after either\
  \ frontend supplies both branch regions"
- "Rules 2/4/6 condition facts and branch joins — under P-E: Python DSL IR checker before lowering after both branch\
  \ regions are captured"
- "Rules 5/7/11 path initialization, output coverage and FIFO intervals — under R-B: Rust checker before code generation;\
  \ runtime checks are defensive only"
- "Rules 5/7/11 path initialization, output coverage and FIFO intervals — under P-E: Python checker before code\
  \ generation; Python truth selection is not the proof"
- "Bool condition, equal result type, exactly-one-branch evaluation — under R-B: frontend retains value blocks and\
  \ Rust type/effect checker validates before lowering"
- "Bool condition, equal result type, exactly-one-branch evaluation — under P-E: Python AST/builder frontend retains\
  \ value blocks and Python checker validates before lowering"
"raters":
- "Codex-A"
"verified": ["2026-09-28"]
"status": "draft"
---
## External DSL form

[precedent-measured] Closed EBNF from `spatial-rs@eb49d8b:docs/language-spec.md:130-130`, `spatial-rs@eb49d8b:docs/language-spec.md:168-169`:

```ebnf
if_stmt            = "if" expr block [ "else" ( block | if_stmt ) ] ;
if_expr            = "if" expr value_block "else"
                     ( value_block | if_expr ) ;
```

[precedent-measured] Canonical fragment, with the surrounding initialized operands assumed by the example: `spatial-rs@eb49d8b:docs/language-spec.md:354-381`.

```spatial
line_out[col] := if row < 2 || col < 2 {
  yield 0;
} else {
  yield magnitude;
};
```

[judgment] `yield` and the statement/value-block grammar distinction add language concepts; choosing one runtime branch is hardware-relevant. Conditions must be `Bool`, value branches have equal types, and only the selected value block executes: `spatial-rs@eb49d8b:docs/language-spec.md:678-685`, `spatial-rs@eb49d8b:docs/language-spec.md:818-824`.

## Python forms

[precedent-measured] **Tracing, pure expression case:** real Amaranth syntax constructs a value mux. This fits a pure value selection, not an effectful Spatial value block: `amaranth@90449f1:amaranth/hdl/_ast.py:1707-1723`.

```python
from amaranth import Mux
selected = Mux((row < 2) | (col < 2), 0, magnitude)
```

[designed] **Tracing, full construct — awkward:** callback definitions and explicit branch capture are required to retain statement regions; each callback is traced into a separate region and only the selected region executes in hardware. This proposed extension realizes `spatial-rs@eb49d8b:docs/language-spec.md:99-100`, `spatial-rs@eb49d8b:docs/language-spec.md:818-824`.

```python
def then_value():
    x = incoming.deq()
    return x

def else_value():
    return T.int(0)

selected = T.if_value(cond, T.capture(then_value), T.capture(else_value))
T.if_stmt(cond, T.capture(write_then), T.capture(write_else))
```

[judgment] Native `a if cond else b` is not expressible as symbolic two-region control by operator overloading alone: Python truth-tests `cond` and evaluates one arm. `Mux(cond, incoming.deq(), 0)` evaluates its arguments before `Mux` can install a branch region. These are distinct problems. [Python conditional expressions](https://docs.python.org/3/reference/expressions.html#conditional-expressions), [calls](https://docs.python.org/3/reference/expressions.html#calls), [truth conversion](https://docs.python.org/3/reference/datamodel.html#object.__bool__) (accessed 2026-09-28). Amaranth explicitly raises on symbolic truth conversion: `amaranth@90449f1:amaranth/hdl/_ast.py:627-639`.

[precedent-measured] **Builder, statement case:** real Amaranth condition contexts capture hardware branches; adapted operand names retain its actual syntax. The example/source show `m.If`, `m.Else`, and domain assignments: `amaranth@90449f1:examples/basic/alu.py:16-25`, `amaranth@90449f1:amaranth/hdl/_dsl.py:331-392`.

```python
with m.If(cond):
    m.d.comb += output.eq(then_value)
with m.Else():
    m.d.comb += output.eq(else_value)
```

[designed] **Builder, value-block extension — yes:** retain yields and effectful statements in branch regions rather than encoding both effects as inputs to a mux. This is additional API work beyond the precedent and follows `spatial-rs@eb49d8b:docs/language-spec.md:99-100`, `spatial-rs@eb49d8b:docs/language-spec.md:823-824`.

```python
with B.if_value(cond) as choice:
    with choice.then_():
        choice.yield_(incoming.deq())
    with choice.else_():
        choice.yield_(B.int(0))
output.write(choice.value)
```

[precedent-measured] **AST, pure expression case:** Allo source uses the following actual syntax, but its `IfExp` builder builds both operands and emits `arith.SelectOp`; it supplies no evidence for laziness of effectful value blocks: `allo@094ab41:tests/test_schedule_compute.py:25-30`, `allo@094ab41:allo/ir/builder.py:2401-2416`.

```python
T2: int32 = A - B if A > B else B - A
```

[designed] **AST, complete value-block form — yes:** capture a source-only local helper and inline its conditional return regions; do not execute it as Python. Ordinary statement `if` can be captured directly. `return` here maps to a branch yield, with separate lexical child scopes and typed result merging; this requires a new transform, informed by `spatial-rs@eb49d8b:docs/language-spec.md:388-397`, `spatial-rs@eb49d8b:docs/language-spec.md:678-685`.

```python
@spatial_ast
def kernel():
    @value_block
    def selected():
        if cond:
            local: Int = incoming.deq()
            return local
        else:
            return 0
    output = selected()
    if flag:
        register = 1
```

## Assessment

[designed] The frontmatter concerns the full construct, so the tracing rating is awkward even though pure mux expressions fit its subset. The designs retain typed handles, branch regions and DSL effect order; ordinary host-folded literals and full spans are absent in tracing/builder. AST's five retained categories require original source/tokens, a Spatial symbol table and type-directed literal handling, beyond simply calling `ast.parse`. [Python AST locations](https://docs.python.org/3/library/ast.html#ast.AST) (accessed 2026-09-28); `spatial-rs@eb49d8b:docs/language-spec.md:682-689`.

[designed] Under R-B the shared Rust checker, and under P-E the Python DSL checker, must apply Rule 2 path facts, Rule 4 entailment and Rule 6 intersection/join, including the incoming false path for an omitted else. Rules 5/7/11 then reject uninitialized reads, uncovered outputs or impossible FIFO intervals before lowering. No branch selected by the host can substitute for analysis of both runtime possibilities: `spatial-rs@eb49d8b:docs/language-spec.md:460-469`, `spatial-rs@eb49d8b:docs/language-spec.md:481-532`, `spatial-rs@eb49d8b:docs/language-spec.md:589-592`.

[judgment] First-error examples differ: native symbolic truth conversion can fail at Python time; incompatible branch types or path initialization fail at IR check; literal-only Python conditions and Python actions executed while constructing both contexts can silently disappear into host behavior. The latter is not a claim that the DSL executes both branches at runtime. Evidence: `amaranth@90449f1:amaranth/hdl/_dsl.py:343-391`, and the Python conditional/call references above.

## Precedent

[precedent-measured] Source/test inspection only; no test execution or performance measurement. Amaranth demonstrates guarded builder statements, Allo demonstrates AST `if` regions and pure conditional selection (`allo@094ab41:allo/ir/builder.py:2419-2453`). Current spatial-rs statement `if` is Narrow; canonical expression `if` with `yield` and the complete calculus are Specified: `spatial-rs@eb49d8b:docs/language-spec.md:1098-1099`, `spatial-rs@eb49d8b:docs/language-spec.md:1114-1115`.
