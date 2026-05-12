---
type: conventions
project: spatial-spec
date: 2026-04-21
---

# Conventions

Minimal style/format rules so the vault stays consistent across sessions.

## Frontmatter

Every file has a frontmatter block. `type` is required; other fields depend on `type`.

> **YAML safety.** For list-valued fields, use **block style** (one item per line with `- `) and **quote strings** that contain a colon or wikilink syntax.
>
> - A bare colon inside a flow sequence (`[path:10-20]`) parses as a map entry rather than a scalar.
> - Unquoted `[[wikilink]]` inside a YAML list parses as a **nested list**, not the wikilink string. Obsidian does not auto-resolve wikilinks in that position.
>
> Always quote path-with-line citations and wikilinks when they appear inside lists. See the templates at the bottom of this file for the canonical safe shapes.

### Required types

| type | Used for | Required extra fields |
|---|---|---|
| `moc` | Top-level / folder-level indexes ([[00 - Index]]) | — |
| `design` | One-off design docs ([[2026-04-21-spatial-spec-design]]) | `status`, `approved_by` |
| `runbook` | Operational session-start docs ([[workflow]]) | `load_priority` |
| `conventions` | This file — style / frontmatter / citation rules | `date` |
| `log` | Append-only logs ([[progress-log]]) | — |
| `open-questions` | The unresolved-questions tracker | `date_started` |
| `hls-mapping-index` | Index file for `30 - HLS Mapping/` | `date_started` |
| `coverage` | Phase 1 subagent outputs | `subsystem`, `paths`, `file_count`, `date`, `verified` |
| `deep-dive` | Phase 2 raw reading notes | `topic`, `source_files`, `session`, `status`, `feeds_spec` |
| `spec` | Authoritative spec entries under `10 - Spec/` | `concept`, `source_files`, `source_notes`, `hls_status`, `depends_on`, `status` |
| `hls-mapping` | Non-index entries under `30 - HLS Mapping/` (per-construct) | `construct`, `spec_entry`, `category` |
| `cross-ref` | Navigation matrix: directory → concept mapping, pass orders, node↔codegen matrices | — |

If a new type is needed, add it to this table before using it — the schema is the authoritative list.

## Source code citations

Two forms:

1. **Inline identifiers** — backticks: `` `argon.Op` ``, `` `state.scheduler` ``.
2. **Algorithmic / behavioral claims** — must include a path + line range: `spatial/src/spatial/transform/UnrollingTransformer.scala:42-78`.

If a citation isn't available, tag the claim `(inferred, unverified)` in-prose. Untagged behavioral claims without citations are a style error.

After a re-read confirms a claim, add `verified: <YYYY-MM-DD>` to the entry's frontmatter (list of dates for multiple re-reads).

## Wikilinks

- Between vault files: `[[file stem]]` — stem *includes* the numeric prefix (e.g., `[[40 - Unrolling]]`).
- When the prefix is ugly inline, use aliases: `[[40 - Unrolling|unrolling]]`.
- Source code paths are **not** wikilinks — keep them plain text so they're greppable with normal tools.
- Never use relative paths in wikilinks; Obsidian resolves by stem globally within the vault.

## File and folder naming

- **Folders**: numeric prefix with gap-10 pattern (`00 - Foo`, `10 - Bar`, `20 - Baz`). Gaps let you insert new entries without renumbering.
- **Spec files inside folders**: same pattern.
- **Coverage notes and deep-dive notes**: descriptive kebab-case, no prefix (order-independent): `argon-coverage.md`, `unrolling-transformer.md`.
- **Stems are unique vault-wide.** Two files with the same stem (even in different folders) break wikilinks.

## Status vocabulary

**Spec entries (`status` field):**
- `draft` — written, not re-checked
- `reviewed` — re-read against source, all claims confirmed
- `stable` — reviewed + cross-referenced from multiple places without issue
- `needs-rework` — a downstream reader flagged a problem; fix pending

**Deep-dive notes (`status` field):**
- `draft` — in progress
- `ready-to-distill` — note is complete, ready to feed a spec entry
- `superseded` — spec entry supersedes this note; kept for audit trail

**HLS status (`hls_status` field on spec entries):**
- `clean` — translates directly to HLS
- `rework` — needs HLS-specific design
- `chisel-specific` — tied to RTL semantics; not portable
- `unknown` — not yet analyzed

## Progress log format

Append-only, newest-first within day blocks:

```markdown
## 2026-04-21 — Phase 0-1
- Design doc + workflow committed: [[2026-04-21-spatial-spec-design]]
- Phase 1 dispatched: 10 subagents
- Spot-checks: argon (3/3 OK), forge (2/3 OK — 1 correction filed as Q-003)
- Open Qs logged: Q-001 … Q-007

## 2026-04-22 — Deep dive
- Topic: Argon Symbol/Ref → [[10 - Symbol and Reference System]]
- Opened: Q-008, Q-009 (unclear effect propagation in nested blocks)
```

## Open questions format

```markdown
## Q-014 — [2026-04-22] Threading model of argon.State
Coverage says "implicit singleton per compilation" but scalagen references
a worker-per-thread pattern. Need to verify against State.scala directly.

Source: argon/src/argon/State.scala
Blocked by: —
Status: open | resolved-<date> | out-of-scope
Resolution: (empty until resolved)
```

IDs are zero-padded (Q-001, Q-014, Q-101) for stable sort. Never reuse an ID; resolved entries stay in the file with their resolution noted.

## Note templates

### Spec entry skeleton

```markdown
---
type: spec
concept: <concept>
source_files:
  - "spatial/src/.../<File>.scala:<line-range>"    # always quote; colons break flow syntax
source_notes:
  - "[[<deep-dive-note-stem>]]"                    # always quote wikilinks inside lists
hls_status: unknown
depends_on:
  - "[[<related-concept>]]"
status: draft
---

# <Concept>

## Summary

One paragraph. What this thing is in Spatial, why it exists, where it lives in the compilation pipeline.

## Syntax / API (if applicable)

## Semantics

What this does, formally enough that a Rust reimplementer could match behavior.

## Implementation

How the current Spatial code realizes it. Algorithmic depth. Cite file:line for every claim.

## Interactions

What other parts of the compiler this touches — passes that read/write it, codegens that emit for it.

## HLS notes

Short. If detailed, defer to `30 - HLS Mapping/...`.

## Open questions

Link to `20 - Open Questions.md` entries, if any.
```

### Deep-dive skeleton

```markdown
---
type: deep-dive
topic: <slug>
source_files:
  - "spatial/src/.../<File>.scala"
session: <date>
status: draft
feeds_spec:
  - "[[<spec-entry-stem>]]"
---

# <Topic>

## Reading log
(Files read, in order. Notes as you go.)

## Observations
(Raw findings, quotes, file:line citations.)

## Open questions
(Filed into `20 - Open Questions.md` when the session ends.)

## Distillation plan
(What parts of this note feed which spec entries.)
```
