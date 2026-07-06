# Rust Stencil2d v1 Border-Equivalence Slice Contract

Date: 2026-07-05

Rust repo: `/Users/david/Documents/David_code/spatial-rs`

Rust branch: `David/HLS-spatial`

Rust commit: `8916d3f1` (`Accept Stencil2d kernel-bound border spelling`)

## Accepted Slice

The first bounded `Stencil2d v1` slice admits an equivalent source spelling for
the existing 3x3 Sobel top-left zero border:

- literal form remains accepted: `rr < 2 || cc < 2`
- matched kernel-bound form is now accepted:
  `rr < KROWS - 1 || cc < KCOLS - 1`
- commuted OR is accepted when row/column provenance still matches:
  `cc < KCOLS - 1 || rr < KROWS - 1`

All accepted forms rebuild the same checked `Stmt::Stencil2d` payload and the
same HLS/manifest output as the existing alias-constant representative.

## Fail-Closed Boundary

The classifier rejects crossed row/column provenance, such as
`rr < KCOLS - 1 || cc < KROWS - 1`, even though both constants resolve to `3`
in the current canary.

This slice does not add generic Spatial `LineBuffer`, `RegFile`, `Reduce`,
`par`, arbitrary stencil coefficients, dynamic dimensions, alternate border
policies, optimized line-buffer scheduling, board execution, implementation, or
timing-closure evidence.

## Verification

- Red tests first:
  - `cargo test -p spatial-rs-core --locked parse_accel_accepts_stencil2d_kernel_bound_minus_one_border -- --nocapture`
  - `cargo test -p spatial-rs-hls --locked --test m1_codegen stencil2d_kernel_bound_minus_one_border_preserves_exact_hls_and_harness -- --nocapture`
- Targeted green:
  - `cargo test -p spatial-rs-core --locked stencil2d -- --nocapture`
  - `cargo test -p spatial-rs-hls --locked --test m1_codegen stencil2d -- --nocapture`
  - `cargo test -p spatial-rs-hls --locked --test vitis_validation captured_stencil2d_v0_vitis_evidence_parses_for_fourteen_program_validation_set -- --nocapture`
- Full local gates:
  - `cargo test --locked --workspace`
  - `cargo clippy --all-targets --locked -- -D warnings`
  - `cargo fmt --all -- --check`
  - `cargo run -p ee109-examples --locked`
  - `cargo run -p ee109-examples --locked --bin emit-vitis-dry-run`
  - `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --validate-evidence docs/vitis-validation/2026-07-05-current-head-76158dd7-39-program --mode both`
  - `git diff --check`

Evidence boundary: no generated-HLS, manifest, validation-roster, or
vendor-evidence change. No fresh EC2/Vitis execution was required; the active
vendor anchor remains
`docs/vitis-validation/2026-07-05-current-head-76158dd7-39-program/`.

