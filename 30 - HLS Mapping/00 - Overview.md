---
type: hls-mapping-index
project: spatial-spec
date_started: 2026-04-21
aliases:
  - "30 - HLS Mapping"
---

# HLS Mapping — Overview

Parallel analysis of how each Spatial construct maps (or does not map) onto an HLS target. This folder is **not** the spec; it is the bridge from the spec to a Rust-based compiler that emits HLS C++ instead of Chisel RTL.

## Why a separate folder

Keeping HLS commentary out of `10 - Spec/` means:

- Spec entries describe Spatial *as it is*, which stays stable regardless of rewrite target.
- HLS mapping can be revised independently as the target design evolves.
- A future reader using the spec for a different purpose (e.g., understanding the current Chisel flow, or targeting some other backend) isn't forced through HLS-specific framing.

## Categorization

Older spec entries may still use one of four coarse statuses tracked in spec-entry frontmatter as `hls_status`:

| Status | Meaning | Example (speculative) |
|---|---|---|
| **clean** | Translates directly. Existing HLS pragmas / constructs cover it. | `Foreach` → HLS `for` loop with `#pragma HLS PIPELINE` |
| **rework** | Concept is portable but needs HLS-specific design work. | `Banking metadata` → HLS `#pragma HLS ARRAY_PARTITION` directives derived from banking plan |
| **chisel-specific** | Tied to RTL semantics. Not portable without redesign at a higher level. | Retiming inserted at RTL boundaries; HLS handles pipelining differently |
| **unknown** | Not yet analyzed. Default for any new spec entry. |

For the Rust rewrite, use the more precise labels below in new planning notes:

| Status | Meaning |
|---|---|
| **surface-clean** | The hardware idea maps cleanly to the Rust DSL surface. |
| **semantic-portable** | The Spatial behavior can be preserved in Rust IR. |
| **backend-pending** | HLS lowering still needs a selected design or vendor evidence. |
| **reference-only** | Useful for understanding old Spatial, but not something to port directly. |

## Layout

```
30 - HLS Mapping/
├── 00 - Overview.md              # this file
├── 10 - Clean Mappings.md        # constructs with hls_status: clean
├── 20 - Needs Rework.md          # constructs with hls_status: rework
└── 30 - Chisel-Specific.md       # constructs with hls_status: chisel-specific
```

Each of the three legacy category files is an index: one line per construct, with a wikilink to its spec entry and a brief rationale.

For non-trivial cases, an additional file may be added here with deeper analysis (e.g., `40 - Memory Banking HLS Strategy.md` when the banking discussion gets long). This folder now also contains selected-slice backend contracts such as ABI manifests, lowering maps, blocker matrices, and stability matrices for the Rust/HLS rewrite.

## Contract with the spec

- Every spec entry has a `hls_status` field in frontmatter. Default: `unknown`.
- When a spec entry gets tagged `clean`, `rework`, or `chisel-specific`, add a one-line entry to the corresponding legacy category file here.
- When a Rust rewrite note needs more precision, use `surface-clean`, `semantic-portable`, `backend-pending`, or `reference-only` in prose or local note metadata and explain whether the construct is merely encountered by a fixture, accepted by an adapter, supported semantically, or vendor-HLS validated.
- HLS-mapping notes **do not** redescribe the Spatial construct. They assume the reader has just read the spec entry; they say only what changes for HLS.

## What this folder is not

- Not the full compiler design for the HLS backend. The selected-slice contracts here are planning and evidence records for the Rust rewrite, while the complete compiler architecture belongs in `90 - Meta/` design notes and repo-local docs.
- Not a comparison of HLS tools (Vitis HLS, Catapult, etc.). Specific tool choice is out of scope.
- Not the authoritative decision log about the Rust rewrite. Decisions belong in `90 - Meta/` design notes, with HLS evidence linked from here.

## Current status

- Overview written: 2026-04-21.
- Updated for the Rust/HLS rewrite on 2026-06-27. This folder now includes selected-slice HLS contracts, but `10 - Spec/` remains the semantic reference.
