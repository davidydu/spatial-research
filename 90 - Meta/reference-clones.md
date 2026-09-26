---
type: reference
project: spatial-spec
date: 2026-09-25
---

# Reference Clones (D-26 precedent material)

Shallow clones under `David_code/reference/` (outside the vault; never
published). Citations use `<name>@<7-char sha>:<path>:<L1-L2>`; the full SHA
below rebuilds a GitHub blob URL. Re-clone at the same SHA to reproduce.

| name | role in D-26 | upstream | full SHA | cloned | licence |
|---|---|---|---|---|---|
| calyx (+ calyx-py) | Python builder over a Rust compiler core; IR-level boundary | https://github.com/calyxir/calyx | d6bcdc8707fe2f024a7b18a86523bda6f770186a | 2026-09-25 | Copyright 2019 Cornell University (LICENSE) |
| dahlia | external DSL whose type system is the legality checker; emits Calyx | https://github.com/cucapra/dahlia | bd68b131ee14f46dd9d2099f86ead01f7d756a71 | 2026-09-25 | The MIT License (LICENSE) |
| allo | Python AST-transform DSL on MLIR, HLS backend; teaching use | https://github.com/cornell-zhang/allo | 094ab4133e59edabc2911cc5c16a768e11772cbc | 2026-09-25 | Apache License (LICENSE) |
| exo | Python AST-transform DSL; forbids host metaprogramming | https://github.com/exo-lang/exo | defe17283d15553ca9d6ad70b2e9f4c22ff36ce2 | 2026-09-25 | MIT License (LICENSE.md) |
| pymtl3 | all-Python HDL with AST-transformed blocks; course use | https://github.com/pymtl/pymtl3 | c8b349f765d63a215dcd3def8a0c9e42d0bf8f9f | 2026-09-25 | BSD 3-Clause License (LICENSE) |
| amaranth | all-Python HDL; `Value.__bool__` raises; frame-inspection naming | https://github.com/amaranth-lang/amaranth | 90449f1e6d5abdfb8cac7519ac7b34d83a9f42b7 | 2026-09-25 | Copyright (C) 2019-2023 Amaranth HDL con (LICENSE.txt) |
| polars | Rust core + PyO3 bindings exemplar (integration depth I2 only) | https://github.com/pola-rs/polars | 85b52dcdfbc9d5aeaac49c2ae9d063d884118300 | 2026-09-25 | Copyright (c) 2025 Ritchie Vink (LICENSE) |
| spatial-rs | the Rust prototype (local only, not public) | local: David_code/spatial-rs | 29f7bad846c2bbdf00b046c1f37c1abfbc22a180 | 2026-09-25 | — |
| spatial | the original Scala Spatial (local clone of stanford-ppl/spatial + local EE109 lane commit) | https://github.com/stanford-ppl/spatial | e7a8f2f7f776dd0c5ac7fc03f16b3ed4d97021f0 | 2026-09-25 | MIT License (LICENSE) |

By URL only (no clone): HeteroCL, JAX (`TracerBoolConversionError`), Taichi
(Python-scope/Taichi-scope), Triton, TVMScript (round-trippable printer), MLIR
`Location`, Ruff (`maturin bindings = "bin"`), IPython cell magics; Chisel
`SourceInfo` is cited from the local `spatial` clone.

The `spatial-rs` row's upstream column deliberately says `local:` so a reader
knows the link cannot be rebuilt.
