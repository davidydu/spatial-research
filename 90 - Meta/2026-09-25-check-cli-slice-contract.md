---
type: design
project: spatial-spec
date: 2026-09-25
status: approved
approved_by: "David (2026-09-25 session, D-26 decision 2)"
related:
  - "[[2026-09-25-python-rust-architecture-research-design]]"
---

# Slice Contract — `spatial-rs check <file>` (D-26 decision 2)

## Why this slice exists

D-26 angle 3 (error-path study) must compare *real* terminal output across
surfaces. Today the only compile entry points are Cargo tests and the
`ee109-examples` binaries, and diagnostics rendered through the `accel!` macro
carry the source name `<accel-macro-stringify>`. This slice is the single code
exception to the D-26 "no production code" rule: a thin `check` subcommand over
the existing `compile_source` with a text renderer that shows `path:line:col`
and help. It is ADR 0002's `check` pulled forward, not a new design.

## Scope

- New workspace member `crates/spatial-rs-cli` producing the binary
  `spatial-rs` with exactly one subcommand: `check <file>`.
- New `render_text(&[Diagnostic]) -> String` in
  `spatial-rs-core::diagnostics` (shared with future JSON rendering; ADR 0002
  says text renders the same logical records).
- Exit codes per ADR 0002: `0` success (empty stdout, empty stderr); `1`
  diagnostics or source read failure (`spatial:E0801`); `2` usage
  (`spatial:E0800`).
- `rust-version = "1.75"` (EC2 toolchain compatibility); no external crates.

## Explicitly unchanged (honest boundaries)

- No accepted syntax, HIR, checked IR payload, classifier behaviour,
  generated HLS, manifest, validation roster, dry-run roster, or vendor-HLS
  evidence changes. `compile_source` is called, not modified.
- `--diagnostics json`, `build`, and `run` are not implemented; a `check`
  invocation with any other option is `E0800`.
- The `accel!` macro path is untouched; only file-based invocation gets real
  source names.

## Text format (normative for this slice)

One diagnostic renders as:

```text
error[spatial:E0500]: <message>
  --> <path>:<start_line>:<start_column>
   = <primary label message>
   = help: <help>
```

Secondary labels render as additional `  --> path:line:col` + `   = message`
pairs after the primary. A diagnostic without labels omits the `-->` line. A
blank line separates diagnostics. Line and column are one-based as
`SourceFile::line_col` already reports them. This is a subset of the ADR 0002
text contract; the JSON envelope is later work.

## Acceptance

- `cargo test -p spatial-rs-cli --locked` passes with: unit tests for argument
  parsing and `render_text`; integration tests that run the built binary on
  fixture files and assert exit code, stdout emptiness, and stderr content.
- Fixtures: `ok.spatial` (the `ScalarAffine4` roster program, accepted by the
  current classifier) → exit 0; `e0500.spatial` (unresolved DRAM dimension)
  → exit 1 with `error[spatial:E0500]` and `e0500.spatial:<line>:<col>` on
  stderr; a missing path → exit 1 with `spatial:E0801`; no arguments → exit 2
  with `spatial:E0800`.
- Full local gates green: `cargo fmt --all --check`, `cargo test --locked`,
  `cargo clippy --all-targets --locked -- -D warnings`, both `ee109-examples`
  binaries, evidence validator unchanged, `git diff --check`.
- Paired vault progress-log entry with the commit hash and gate transcript.
