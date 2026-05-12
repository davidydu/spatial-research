---
type: hls-mapping-index
project: spatial-spec
date_started: 2026-04-21
---

# HLS Mapping — Overview

Parallel analysis of how each Spatial construct maps (or doesn't) onto an HLS target. This folder is **not** the spec; it's the bridge from the spec to a future Rust-based compiler that emits HLS C++ instead of Chisel RTL.

## Why a separate folder

Keeping HLS commentary out of `10 - Spec/` means:

- Spec entries describe Spatial *as it is*, which stays stable regardless of rewrite target.
- HLS mapping can be revised independently as the target design evolves.
- A future reader using the spec for a different purpose (e.g., understanding the current Chisel flow, or targeting some other backend) isn't forced through HLS-specific framing.

## Categorization

Every Spatial construct gets one of four statuses (tracked in spec-entry frontmatter as `hls_status`):

| Status | Meaning | Example (speculative) |
|---|---|---|
| **clean** | Translates directly. Existing HLS pragmas / constructs cover it. | `Foreach` → HLS `for` loop with `#pragma HLS PIPELINE` |
| **rework** | Concept is portable but needs HLS-specific design work. | `Banking metadata` → HLS `#pragma HLS ARRAY_PARTITION` directives derived from banking plan |
| **chisel-specific** | Tied to RTL semantics. Not portable without redesign at a higher level. | Retiming inserted at RTL boundaries; HLS handles pipelining differently |
| **unknown** | Not yet analyzed. Default for any new spec entry. |

## Layout

```
30 - HLS Mapping/
├── 00 - Overview.md              # this file
├── 10 - Clean Mappings.md        # constructs with hls_status: clean
├── 20 - Needs Rework.md          # constructs with hls_status: rework
└── 30 - Chisel-Specific.md       # constructs with hls_status: chisel-specific
```

Each of the three category files is an index: one line per construct, with a wikilink to its spec entry and a brief rationale.

For non-trivial cases, an additional file may be added here with deeper analysis (e.g., `40 - Memory Banking HLS Strategy.md` when the banking discussion gets long).

## Contract with the spec

- Every spec entry has a `hls_status` field in frontmatter. Default: `unknown`.
- When a spec entry gets tagged `clean`, `rework`, or `chisel-specific`, add a one-line entry to the corresponding file here.
- HLS-mapping notes **do not** redescribe the Spatial construct. They assume the reader has just read the spec entry; they say only what changes for HLS.

## What this folder is not

- Not a design for the HLS backend. That's downstream work.
- Not a comparison of HLS tools (Vitis HLS, Catapult, etc.). Specific tool choice is out of scope.
- Not a decision log about the Rust rewrite. That belongs elsewhere when it happens.

## Current status

- Overview written: 2026-04-21.
- Category files not yet populated (Phase 3 begins after Phase 2 deep-dives stabilize).
