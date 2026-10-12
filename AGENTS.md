---
draft: true
---

# Working on Spatial Research

Read `90 - Meta/project-handoff.md` first, then `90 - Meta/workflow.md`, the
current Python research index and the task's owning plan/evidence. Those tracked
files carry shared context across Codex, Claude Code and other harnesses.

- New Python research belongs in `50 - Python Rewrite/`; decisions stay in the
  existing D-number register. Preserve original Scala and historical Rust evidence.
- Read files directly; verify source claims and keep research, implementation,
  reference execution and hardware evidence distinct.
- Use bounded independent agents where available; the integrating agent reviews
  their work. See the handoff for current model preferences, replacing old
  Codex-only or Fable-only operational notes.
- The compiler is in a separate `spatial-py` implementation worktree. Read its
  `AGENTS.md` and `PROJECT_STATE.md`; outer bootstrap `main` is not current code.
- Keep context in shared tracked files. Record decisions, corrections, results,
  unresolved issues and next steps before stopping; private memory is supplementary.
- Commit/push coherent checkpoints under the authorized `davidydu` identity.
  Publish research before building/deploying the separate site; verify changed
  live pages. Keep private material and credentials out of Git and the website.

`CLAUDE.md` points here; it is not a competing policy or memory store.
