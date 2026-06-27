---
type: design
project: spatial-spec
date: 2026-06-27
status: active
depends_on:
  - "[[2026-06-26-rust-ee109-mvp-design]]"
  - "[[2026-06-26-rust-post-m1-next-slice]]"
---

# Rust Lab3 Part1 Convolution Slice Contract

## Decision

Implement `Lab3Part1Convolution` next as one exact semantic kernel in `spatial-rs`, not as generic lowering for `LineBuffer`, `RegFile`, `Reduce`, `mux`, `abs`, or `par`.

This is the smallest slice that advances the current research goal: compile the selected EE109 lab examples from a Spatial-like Rust DSL surface to HLS-style C++ with local host-C++ verification. It intentionally proves functional Lab3 convolution behavior before attempting reusable local-window memory lowering.

## Scope

The Rust parser will accept exactly one whitespace-equivalent canonical source island:

- kernel name: `Lab3Part1Convolution`
- fixed dimensions: `ROWS = 16`, `COLS = 16`, `KH = 3`, `KW = 3`, `CMAX = 16`, `LB_PAR = 8`
- input DRAM: `img: Dram<Int>[ROWS, COLS]`
- output DRAM: `imgOut: Dram<Int>[ROWS, COLS]`
- internal source syntax includes `LineBuffer`, `RegFile`, two 3x3 LUTs, nested reductions, `mux`, `abs`, and row store
- IR collapses this shape to `ProgramKind::Lab3Part1Convolution` plus `Stmt::Lab3Part1Convolution`

The direct semantic IR will record only artifacts that are actually lowered in this slice:

- rank-2 DRAM input/output ABI
- LUT tables `kh` and `kv` with the accelerator coefficients from `Lab3.scala`
- local SRAM-like row buffer `lineOut[16]` if represented in the manifest

It will not add generic `MemoryKind::LineBuffer`, generic `MemoryKind::RegFile`, or generic `Reduce` statements. Those constructs remain unsupported outside the exact canonical Lab3 source.

## Semantics

The generated kernel computes the EE109 Lab3 Sobel-style result over a fixed 16x16 row-major image. Output `(r, c)` uses the causal 3x3 window ending at `(r, c)`, matching the Scala gold formula rather than a centered convolution.

For `r < 2 || c < 2`, output is `0`.

For other positions:

```text
horz = p[r-2,c-2] * 1 + p[r-2,c-1] * 0 + p[r-2,c] * -1
     + p[r-1,c-2] * 2 + p[r-1,c-1] * 0 + p[r-1,c] * -2
     + p[r  ,c-2] * 1 + p[r  ,c-1] * 0 + p[r  ,c] * -1

vert = p[r-2,c-2] * 1 + p[r-2,c-1] * 2 + p[r-2,c] * 1
     + p[r-1,c-2] * 0 + p[r-1,c-1] * 0 + p[r-1,c] * 0
     + p[r  ,c-2] * -1 + p[r  ,c-1] * -2 + p[r  ,c] * -1

out[r,c] = abs(horz) + abs(vert)
```

The canonical EE109 fixture image is `16x16` with `image[i,j] = i * 16` when `4 <= i <= 12` and `4 <= j <= 12`, else `0`. Its expected full-output checksum is `44928`, but Rust tests must compare every pixel because the Scala checksum is weaker than full matrix equality.

## HLS-Style Output

Emit a fixed host ABI:

```cpp
extern "C" void Lab3Part1Convolution_kernel(const int *img, int *imgOut)
```

Required emitted structure:

- `img` uses `m_axi` bundle `gmem0`; `imgOut` uses `m_axi` bundle `gmem1`
- `const int ROWS = 16;`, `const int COLS = 16;`, `const int KH = 3;`, `const int KW = 3;`
- `static const int kh[9] = {1, 0, -1, 2, 0, -2, 1, 0, -1};`
- `static const int kv[9] = {1, 2, 1, 0, 0, 0, -1, -2, -1};`
- loops use `< ROWS`, `< COLS`, `< KH`, and `< KW`
- source index uses `(src_r * COLS) + src_c`
- kernel index uses `(kr * KW) + kc`
- output index uses `(r * COLS) + c`
- border guard is `r < KH - 1 || c < KW - 1`
- integer abs is explicit and output is `ah + av`

This remains a local host-C++ compile/run gate only. It is not Vitis/Vivado synthesis evidence.

## Tests

Add tests before production code:

- parser positive for the exact canonical Lab3 source, despite unsupported tokens inside it
- parser near-miss negatives for changed kernel name, changed dimensions, changed LUT constants, changed border guard, changed output name, and changed store shape
- generic `Reduce`, `RegFile`, `LineBuffer`, and noncanonical rank-2 DRAM still reject with stable diagnostics and non-stale help text
- checked IR validation rejects wrong kind/name, extra ports, wrong DRAM shape, wrong LUT payload, missing `lineOut`, and extra body statements
- manifest records exactly the rank-2 `img` input, rank-2 `imgOut` output, `kh`/`kv` LUTs, and any represented local `lineOut`
- oracle unit tests cover the canonical 16x16 checksum, full matrix equality, non-square row-major canaries, negative-value abs canaries, and impulse anchoring
- HLS string tests pin the signature, pragmas, constants, row-major `COLS` stride, kernel `KW` stride, border guard, abs, and absence of centered/right-bottom border logic
- host-C++ harness compares every output element against the independent Rust oracle and pre-fills output with a sentinel

## Deferred

Do not update the broad documentation site or stability matrix during this slice. After the implementation works, update:

- `spatial-rs/README.md`, because the repo is now beyond the old M1 wording
- `90 - Meta/progress-log.md`, with commit hash, verification commands, review evidence, fail-closed boundary, and the host-C++-only limitation

