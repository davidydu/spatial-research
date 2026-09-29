---
"type": "python-mapping"
"construct": "assignment := and lvalues"
"spec_entry": "[[10 - Effects and Aliasing]]"
"grammar_rule": "assign_stmt, lvalue"
"external_dsl":
  "concepts_without_hardware_meaning":
  - "The separate := token for hardware mutation versus let binding"
  - "Syntactic lvalue category restricting assignment targets"
"per_style":
  "tracing":
    "expressible": "yes"
    "info_preserved":
    - "size_vs_int"
    - "order"
    "error_locus": "ir-check"
    "silently_divergent":
    - "Python = rebinds names instead of mutating a hardware object"
    - "Python indexed = evaluates RHS before target indices"
    - "Pure literal arithmetic is folded before a write method sees it"
  "builder":
    "expressible": "yes"
    "info_preserved":
    - "size_vs_int"
    - "scope"
    - "order"
    "error_locus": "ir-check"
    "silently_divergent":
    - "Host integer/float calculations lose literal provenance before builder calls"
    - "Ordinary = on a Python handle can silently replace that handle"
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
    - "None inside the proposed closed subset; preserving Python assignment order instead of Spatial order would\
      \ be an incorrect lowering"
"obligations_at_risk":
- "Rules 1/4 numeric facts and bounds — under R-B: Rust type/obligation checker before lowering, with frontend-supplied\
  \ lvalue index order"
- "Rules 1/4 numeric facts and bounds — under P-E: Python DSL type/obligation checker before lowering, not Python\
  \ numeric coercion"
- "Rules 5/7/11 RHS initialization, sequential FIFO effects and destination coverage — under R-B: Rust shared-IR\
  \ checker before code generation"
- "Rules 5/7/11 RHS initialization, sequential FIFO effects and destination coverage — under P-E: Python shared-IR\
  \ checker before code generation"
- "Rule 10 lane conflicts plus writable lvalue/type legality — under R-B: Rust checker before lowering; both frontends\
  \ retain target kind and backing identity"
- "Rule 10 lane conflicts plus writable lvalue/type legality — under P-E: Python checker before lowering; builder/AST\
  \ retain target kind and backing identity"
"raters":
- "Codex-A"
"verified": ["2026-09-28"]
"status": "draft"
---
## External DSL form

[precedent-measured] Closed EBNF, `spatial-rs@eb49d8b:docs/language-spec.md:129-139`:

```ebnf
assign_stmt        = lvalue ":=" expr ";" ;
lvalue             = ident | ident index_suffix ;
```

[precedent-measured] Canonical fragment, inside the sample's in-bounds loop and after loading `tile`: `spatial-rs@eb49d8b:docs/language-spec.md:43-49`.

```spatial
tile[lane] := tile[lane] * scale;
```

[judgment] Distinguishing `let` binding from `:=` mutation is an extra surface concept; writable storage and effect order are hardware semantics. Identifier lvalues are scalar output/inout or `Reg`; indexed ones are writable `Dram`, `Sram`, `LineBuffer`, or `RegFile`. Scalar lets, constants, inputs and loop/FSM binders are immutable: `spatial-rs@eb49d8b:docs/language-spec.md:773-791`.

## Python forms

[precedent-measured] **Tracing precedent:** Amaranth uses `.eq()` to construct assignment statements, admitted through augmented assignment into a domain. This is real syntax; its width extension/truncation rules differ from Spatial's type equality and literal coercion: `amaranth@90449f1:amaranth/hdl/_ast.py:1335-1348`, `amaranth@90449f1:examples/basic/alu.py:16-25`, `spatial-rs@eb49d8b:docs/language-spec.md:680-685`.

```python
m.d.comb += output.eq(a + b)
```

[designed] **Tracing — yes with explicit mutation methods.** A dedicated lvalue proxy avoids reading an uninitialized target merely to acquire its address. `at` builds a target reference, `write` commits the captured statement; expression effects remain ordered in the IR. This realizes the target-index-before-RHS contract in `spatial-rs@eb49d8b:docs/language-spec.md:831-837`.

```python
reg.write(src_value)
tile.at(lane).write(tile[lane] * scale)
dst.at(index_queue.deq()).write(value_queue.deq())
```

[designed] **Builder — yes.** A statement call can retain explicit target metadata and effect order, and a block context supplies lexical ownership; ordinary Python bindings still only bind handles. Required order and destination categories come from `spatial-rs@eb49d8b:docs/language-spec.md:788-791`, `spatial-rs@eb49d8b:docs/language-spec.md:831-837`.

```python
with B.block():
    B.assign(B.target(reg), src_value)
    B.assign(B.target(tile, lane), tile[lane] * scale)
    B.assign(B.target(dst, index_queue.deq()), value_queue.deq())
```

[precedent-measured] **AST precedent:** Allo has ordinary indexed assignment in a transformed `while` body and scalar assignment in transformed functions. Its real syntax is shown here; the source inspection does not establish Spatial effect order or immutable-let rules: `allo@094ab41:tests/test_builder.py:243-253`, `allo@094ab41:tests/test_builder.py:287-302`.

```python
def kernel(A: int32[10]):
    i: index = 0
    while i < 10:
        A[i] = i
        i += 1
```

[designed] **AST — yes for the exact contract.** A Spatial transform interprets annotated declarations separately from assignment, resolves lvalue kinds, and explicitly emits index effects before RHS effects, regardless of Python's usual evaluation order. This is proposed functionality, required by `spatial-rs@eb49d8b:docs/language-spec.md:101-103`, `spatial-rs@eb49d8b:docs/language-spec.md:831-837`.

```python
@spatial_ast
def kernel():
    reg: Reg[Int] = 0
    reg = src_value
    tile[lane] = tile[lane] * scale
    dst[index_queue.deq()] = value_queue.deq()
```

[judgment] Native `=` cannot be overloaded to observe a plain local-name rebinding; subscription assignment can reach an object's setter, but Python evaluates its RHS before the target. Thus `dst[q.deq()] = q.deq()` would dequeue in the opposite order if executed as ordinary Python. Python augmented assignment does evaluate the target first, but also performs a read/operation/write unless deliberately overloaded, so it is not automatically a replacement for write-only destinations. [Python assignment](https://docs.python.org/3/reference/simple_stmts.html#assignment-statements), [augmented assignment](https://docs.python.org/3/reference/simple_stmts.html#augmented-assignment-statements), [evaluation order](https://docs.python.org/3/reference/expressions.html#evaluation-order) (accessed 2026-09-28).

## Assessment

[designed] The tracing rating describes the proposed method-call form, not native `=`. It preserves explicit types and captured write order, but not general Python lexical scope, original literal syntax or full spans. Builder adds explicit DSL scope. A token-backed AST implementation can preserve all five fields; it must perform type-directed literal analysis before any host arithmetic executes. Python AST locations are available, while literal context/type checking is separately specified at `spatial-rs@eb49d8b:docs/language-spec.md:682-689`; [Python AST](https://docs.python.org/3/library/ast.html#ast.AST) (accessed 2026-09-28).

[designed] R-B's Rust shared checker and P-E's Python DSL checker must both check target writability/type, Rule 1 value facts, Rule 4 bounds, Rule 5 RHS/source reads before adding destination initialization, Rule 7 intermediate FIFO occupancy and Rule 10 cross-lane conflicts. Rule 11 requires all these derivations before lowering, independent of the host language: `spatial-rs@eb49d8b:docs/language-spec.md:445-459`, `spatial-rs@eb49d8b:docs/language-spec.md:481-522`, `spatial-rs@eb49d8b:docs/language-spec.md:528-532`, `spatial-rs@eb49d8b:docs/language-spec.md:583-592`.

[judgment] The rated first error is IR-check for an immutable/out-of-bounds target in the proposed forms; a frontend can reject some type/category mistakes earlier. Rebinding a host name or computing a literal-only RHS can be silent because no DSL mutation was captured. An executed Python indexed assignment can expose the wrong effect order before an IR checker ever sees it; this differs from a delayed hardware runtime error. Evidence: Python assignment references above and `spatial-rs@eb49d8b:docs/language-spec.md:831-837`.

## Precedent

[precedent-measured] Source/test inspection only. Amaranth proves an explicit assignment-object surface exists; Allo proves statement AST assignment exists, but its builder may build a call RHS before targets (`allo@094ab41:allo/ir/builder.py:1161-1189`), so Spatial ordering is additional work. Current Rust direct reads/writes are Narrow and reference effect rules/full calculus are Specified: `spatial-rs@eb49d8b:docs/language-spec.md:1097-1097`, `spatial-rs@eb49d8b:docs/language-spec.md:1114-1115`. No runtime parity was measured.
