---
"type": "python-mapping"
"construct": "fsm controller"
"spec_entry": "[[10 - Spec/10 - Language Surface/10 - Controllers|Controllers]]"
"grammar_rule": "fsm_ctrl"
"external_dsl":
  "concepts_without_hardware_meaning":
  - "A dedicated fsm/in/while/step syntactic form"
  - "Implicit state rebinding exclusively through the step clause rather than an ordinary assignment"
"per_style":
  "tracing":
    "expressible": "awkward"
    "info_preserved":
    - "size_vs_int"
    - "scope"
    - "order"
    "error_locus": "python-time"
    "silently_divergent":
    - "Native while tests Python truth or executes on host values"
    - "Host callback closure rebinding or literal folding can change captured expressions"
  "builder":
    "expressible": "yes"
    "info_preserved":
    - "size_vs_int"
    - "scope"
    - "order"
    "error_locus": "ir-check"
    "silently_divergent":
    - "Python host work in the FSM body executes once during elaboration"
    - "Native Python truth tests inside a region can select host paths"
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
    - "None inside the proposed closed FSM pattern; host escapes would require rejection or explicit separation"
"obligations_at_risk":
- "Rules 1/4/9 affine induction, strict predicate form and nonwrapping step proof — under R-B: Rust shared-IR checker\
  \ before lowering"
- "Rules 1/4/9 affine induction, strict predicate form and nonwrapping step proof — under P-E: Python DSL IR checker\
  \ before lowering"
- "Rules 5/6/7/11 initialization, joins, FIFO state and post-FSM coverage — under R-B: Rust checker before code\
  \ generation using only facts admitted by Rule 9"
- "Rules 5/6/7/11 initialization, joins, FIFO state and post-FSM coverage — under P-E: Python checker before code\
  \ generation using only facts admitted by Rule 9"
- "Immutable Int state, Bool condition, observational init/cond/step and condition-body-step order — under R-B:\
  \ frontend records distinct FSM regions; Rust type/effect checker before lowering"
- "Immutable Int state, Bool condition, observational init/cond/step and condition-body-step order — under P-E:\
  \ Python frontend records distinct FSM regions; Python type/effect checker before lowering"
"raters":
- "Codex-A"
"verified": ["2026-09-28"]
"status": "draft"
---
## External DSL form

[precedent-measured] Closed EBNF, `spatial-rs@eb49d8b:docs/language-spec.md:124-125`:

```ebnf
fsm_ctrl           = "fsm" ident "in" expr "while" expr
                     "step" expr block ;
```

[designed] Canonical-syntax fragment derived from that rule; this example is not quoted as an existing executable test. Assume writable `dst: Dram<Int>[4]`. The strict bound and unit step match Rule 9: `spatial-rs@eb49d8b:docs/language-spec.md:568-582`, `spatial-rs@eb49d8b:docs/language-spec.md:917-924`.

```spatial
fsm state in 0 while state < 4 step state + 1 {
  dst[state] := state;
}
```

[judgment] The dedicated clause syntax and special binder lifetime are additional surface concepts. The sequential condition/body/step ordering and state evolution are substantive semantics: initial state is evaluated before binding; the step observes body writes, state is immutable otherwise, and state can be negative or wrap as `Int`. No v1 FSM schedule annotation exists: `spatial-rs@eb49d8b:docs/language-spec.md:393-397`, `spatial-rs@eb49d8b:docs/language-spec.md:839-843`, `spatial-rs@eb49d8b:docs/language-spec.md:917-924`.

## Python forms

[designed] **Tracing — awkward for arbitrary bodies.** Expression callbacks can describe a condition/step, but a multi-statement body needs a function beyond the stated tracing subset. The proposed tracer must capture three distinct regions, with symbolic state and runtime reads, and reject a state write: `spatial-rs@eb49d8b:docs/language-spec.md:917-924`.

```python
def body(state):
    dst.at(state).write(state)
    reg.write(reg.value + T.int(1))

T.fsm(T.int(0),
      cond=lambda state: state < T.int(4),
      body=T.capture(body),
      step=lambda state: state + T.int(1))
```

[judgment] A native `while state < bound:` is not expressible as symbolic FSM control by operator overloading: Python requires a truth value and executes its loop. Symbolic `__bool__` can fail early but cannot supply a second runtime control path. [Python truth conversion](https://docs.python.org/3/reference/datamodel.html#object.__bool__) (accessed 2026-09-28); the concrete rejection is `amaranth@90449f1:amaranth/hdl/_ast.py:627-639`.

[designed] **Builder — yes.** The body and step are IR regions; the step expression may reference runtime register reads and is evaluated after the body's writes. A builder cannot merely snapshot their Python values. This shape is designed for `spatial-rs@eb49d8b:docs/language-spec.md:839-843`, `spatial-rs@eb49d8b:docs/language-spec.md:917-924`.

```python
with B.fsm(init=B.int(0), name="state") as f:
    f.condition(f.state < B.int(4))
    with f.body():
        dst.at(f.state).write(f.state)
    f.step(f.state + B.int(1))
```

[precedent-measured] Amaranth's actual builder syntax is a named-state FSM; this is a related construct, not the same integer-state/condition/step contract. Its source records named states and rejects undefined/duplicate state labels: `amaranth@90449f1:amaranth/hdl/_dsl.py:450-505`. A real-syntax excerpt from `amaranth@90449f1:examples/basic/fsm.py:29-37`:

```python
with m.FSM() as fsm:
    with m.State("START"):
        with m.If(~self.i):
            m.next = "DATA"
            m.d.sync += [ctr.eq(self.divisor // 2), bit.eq(7)]
```

[precedent-measured] **AST precedent:** Allo's actual `while` test uses this form. Its source builder creates `scf.WhileOp` regions; this establishes AST looping, not Spatial FSM induction or immutable-state enforcement: `allo@094ab41:tests/test_builder.py:287-302`, `allo@094ab41:allo/ir/builder.py:2455-2490`.

```python
def kernel(A: int32[10]):
    i: index = 0
    while i < 10:
        A[i] = i
        i += 1
```

[designed] **AST — yes through a restricted pattern.** `FsmState` is a transform marker: the immediately following `while` becomes an FSM, and its unique final state assignment becomes `step`, not an allowed body mutation. Other assignments to state must reject. The declaration is evaluated before binding and the state goes out of scope after the recognized FSM. These are new transform rules required by `spatial-rs@eb49d8b:docs/language-spec.md:393-397`, `spatial-rs@eb49d8b:docs/language-spec.md:917-924`.

```python
@spatial_ast
def kernel():
    state: FsmState[Int] = 0
    while state < 4:
        dst[state] = state
        state = state + 1
```

## Assessment

[designed] Frontmatter scope/order retention means the designed DSL regions, not Python local scope. Typed handles retain `Size` versus `Int`; tracing/builder cannot reconstruct host-folded literal syntax or exact subexpression spans. AST's all-five rating requires source/token retention and the explicitly described binding transform, not ordinary Python execution. [Python AST locations](https://docs.python.org/3/library/ast.html#ast.AST) (accessed 2026-09-28); `spatial-rs@eb49d8b:docs/language-spec.md:393-397`, `spatial-rs@eb49d8b:docs/language-spec.md:667-689`.

[designed] R-B assigns Rule 9 to a Rust shared-IR checker; P-E needs the same algorithm in its Python DSL checker before lowering. Only strict `state < bound`/`state > bound`, positive exact constant increments/decrements, affine invariant init/bound and the mandated no-wrap proof admit induction. Other predicate/step shapes do not automatically become illegal FSMs; they contribute only one symbolic iteration's facts and no post-FSM coverage. Both cells must reject later obligations that then cannot be derived: `spatial-rs@eb49d8b:docs/language-spec.md:568-592`.

[designed] Types and observational `init`/`cond`/`step` are frontend/type/effect-checker duties, followed by Rules 5/6/7/11 initialization, path, FIFO and output checks. Symbolic native truth testing first fails at Python time; an effectful step, forbidden state write or missing coverage first fails at IR check in the proposed builder/AST forms. Host-only conditions or actions can silently run during construction unless excluded. Sources: `spatial-rs@eb49d8b:docs/language-spec.md:506-532`, `spatial-rs@eb49d8b:docs/language-spec.md:917-924`; Python truth reference above.

## Precedent

[precedent-measured] Source/test inspection only, no runtime measurement. Amaranth proves named FSM builder support; Allo proves transformed `while` support, neither cited source proves Rule 9 equivalence. Current spatial-rs `fsm` is Narrow, with three active bodies and AST/HIR facts; the full calculus and evaluation/effect rules remain Specified: `spatial-rs@eb49d8b:docs/language-spec.md:1108-1115`.
