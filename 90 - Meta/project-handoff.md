---
type: runbook
project: spatial-python
date: 2026-10-17
status: active
---

# Spatial — shared project handoff

Start here in Codex, Claude Code or any other harness. This file preserves the
project context previously carried in chat and private agent memory. Existing
decisions, plans and evidence remain in their owning documents; this is the map
and restart route. No private memory service, old agent session or temporary
directory is required.

## Read only what the next task needs

1. Read [[workflow]] and [[80 - Initial Compiler Goal]] for the current route.
2. For compiler work, read `AGENTS.md` and `PROJECT_STATE.md` on the implementation
   branch, then its active plan and the relevant checkpoint design/evidence.
3. For research, start at [[00 - Python Rewrite Index]] and the relevant study;
   keep decisions in the existing D-number register.
4. For presentation work, read [[05 - Python Professor Brief]],
   [[2026-10-01-python-professor-presentation-outline]] and
   [[70 - Engineering Architecture Map]]. Verify progress against current
   compiler evidence before updating slides.

## Repository map

Local paths below describe the current machine. Use repository URLs and branches
on another machine; do not make another harness depend on these absolute paths.

| Responsibility | Repository / branch | Local checkout |
|---|---|---|
| Research, decisions, specifications, progress | [spatial-research](https://github.com/davidydu/spatial-research), `main` | `/Users/david/Documents/Spatial Research` |
| Python compiler and test evidence | [spatial-py](https://github.com/davidydu/spatial-py/tree/work/initial-reference), `work/initial-reference` | `/Users/david/Documents/David_code/spatial-py/.worktrees/initial-reference` |
| Documentation build and presentation UI | [spatial-research-site](https://github.com/davidydu/spatial-research-site), `main` | `/Users/david/Documents/spatial-research-site` |
| Original Scala source evidence | Local reference clone; see [[reference-clones]] | `/Users/david/Documents/David_code/spatial` |

**Checkout trap:** the outer `David_code/spatial-py` directory is bootstrap
`main`, not the working compiler. Inspect Git status, branch and worktree list
before edits. Use the existing implementation worktree, or check out
`work/initial-reference` on a new machine. Do not merge or restart the compiler
just because the bootstrap checkout has little code. Earlier `spatial-rs` work
and Rust presentations are historical evidence.

## Decisions and user preferences from the conversation

- The professor requested a pure Python rewrite: first explain what Python
  Spatial looks like, then lower it toward HLS. HLS is the agreed eventual
  target; the current reference milestone does not require vendor tools.
- On 17 October David confirmed language/reference coverage before HLS, guided
  by EE109 Labs 1–3 while supporting varied student programs. He corrected an
  initial mention of Lab 4: there are three labs. Use their memory/control/numeric
  patterns to choose small executable increments and require cross-feature
  compositions. Avoid both lab-specific compiler paths and unrelated verifier
  expansion. [[04 - Python Implementation Roadmap]] owns this progression and
  supersedes its earlier option for an S1-only HLS path alongside language work.
- Assume a capable team and capable coding agents. Earlier Rust arguments based
  on maintenance skill or type safety are not grounds to reopen that direction.
- David authorized the initial implementation on 4 October. [[D-27]] owns the
  direction; [[D-28]] and the implementation blueprints describe the detailed
  proposal. User authorization is separate from professor approval of every
  architectural detail. No new implementation approval question was pending for
  continuing the initial goal.
- Research and compare designs before implementation. Implement general rules
  and unfamiliar compositions. A cherry-picked lab example or fixture-specific
  compiler path is not acceptance.
- Use agents for bounded parallel work to control time and cost. The integrating
  agent personally reviews their work. Codex agents are preferred; later user
  messages also authorize Claude Opus 5.5 through `claude2 -p`, with the approved
  account checked locally. Opus supersedes the earlier Fable preference. A
  harness without those tools may use equivalent independent review roles.
- Read local files and use command-line checks by default. Use browser UI when
  visual or interactive inspection is necessary. Preserve coherent Git
  checkpoints under `davidydu`; update research documentation with results.
- Professor-facing material should lead with the big picture, concrete progress
  and links. The main talk is about ten minutes. Explain what Python Spatial is,
  why the plan is feasible, implementation steps and next evidence. The professor
  already knows Spatial; avoid long program walkthroughs or re-arguing HLS.
- Use plain, verbal scripts and explanatory slide text. The requested visual
  direction is restrained, inspired by Thinking Machines Lab. The Excalidraw map
  should support both overview and detail; render and inspect visual changes.
  Interactive illustrations are not executions of the compiler.

## Current checkpoint and next task

Current executed checkpoint: **`spatial-py@1260959`**, verified on 17 October
with **938 source and 938 isolated installed-wheel tests**, CPython 3.14.5.
The actual Lab 1 tiled DRAM/SRAM source completes both independent output vectors through shared
normalization, checked publication, strict host preparation and the generic
reference runner. Seven demands are proved and four enforced by ordered guards.
The [execution evidence](https://github.com/davidydu/spatial-py/blob/d2460e3/docs/evidence/task-05a-reference-execution.md)
records exact scope, source/test hashes, review findings, timings and a fresh
post-freeze composition. The [runnable demo](https://github.com/davidydu/spatial-py/blob/d2460e3/examples/run_lab1_reference.py)
prints the [recorded outputs](https://github.com/davidydu/spatial-py/blob/d2460e3/docs/evidence/lab1-reference-output.json).

This is reference execution, not HLS or full initial-goal completion. Independent
cases cover aliases, signed/rank-2 views, lazy faults, snapshot copies, fresh local
lifetimes and precise committed prefixes. Private ResourceLimit results have no
continuation; do not describe them as resumable simulation.

Ordinary statement branches now pass the original conditional-fault and rank-2
recurrence sources, including full ordered control/memory traces. Separate arm
scopes share canonical arguments without granting missing lexical captures.
A fresh descending-window/alias composition passed three independent scenarios.
The selected-entry preparation repair and 811-test frozen package results are
in [branch evidence](https://github.com/davidydu/spatial-py/blob/10cc1be/docs/evidence/task-05b-statement-branches.md).
The first execution-only checkpoint was `d2460e3` (773 tests per route).

This is the tiled-scale part of Lab 1. Its Reg, FIFO and Reduce/Fold families
remain required. After the current general memory/helper and initial-contract
work, use those gaps, Lab 2 memory reductions/FSM/LUT/fixed-point tiles, and Lab 3
line/shift buffers and convolution to drive language expansion.

Top-level scalar/borrowed helpers now run through explicit CALL with fresh
frame-local bindings, per-call entry checks and cleanup before return. Original
DEV-TILE-TAIL gives `[5,-7,-2147483645,3,1]` (or empty output at n=0);
DEV-LOCAL-BORROW gives `37` after six calls. Both source and independently written
common records match their complete literal traces. The
[helper demo](https://github.com/davidydu/spatial-py/blob/aecacc0/examples/run_helpers_reference.py) and
[recorded results](https://github.com/davidydu/spatial-py/blob/aecacc0/docs/evidence/helper-reference-output.json)
are repeatable. [Helper evidence](https://github.com/davidydu/spatial-py/blob/aecacc0/docs/evidence/task-05c-helper-execution.md)
records the reproduced ordered-call token repair, fresh post-freeze alias/return
composition, unchanged 176-file snapshot and both 870-test results.

Nested scalar/Unit helpers now capture immutable values, SRAM/DRAM handles,
Out/InOut cells and other lexical helpers through the existing source/common/CALL
route. Captures preserve aliases, hidden dimensions, exact call bindings and
local cleanup. The [capture demo](https://github.com/davidydu/spatial-py/blob/1260959/examples/run_captures_reference.py)
and [recorded results](https://github.com/davidydu/spatial-py/blob/1260959/docs/evidence/capture-reference-output.json)
are repeatable. [Capture evidence](https://github.com/davidydu/spatial-py/blob/1260959/docs/evidence/task-05d-lexical-captures.md)
records independent source/common traces, the proportional-work review repair,
fresh first-pass acceptance, and both 938-test results on unchanged 192-file and
65-file manifests. An earlier composition's Unit observation-adapter repair is
retained as a regression, separately from final fresh acceptance.

David authorized continued work on 17 October. **Next implement borrowed helper
results and named borrowed-view locals together**, starting with the
[parent-reviewed next-step note](https://github.com/davidydu/spatial-py/blob/1260959/docs/reviews/2026-10-17-after-capture-execution.md).
Pin the result/owner correspondence and return-boundary design with independent
red tests; reuse existing C4 inference, selected maps and the call interpreter.
Preserve caller-owned views after helper cleanup and reject callee-local escapes,
including inactive alternatives. Meta/static forms, true resumption, artifact
agreement, verified editing and final acceptance remain mandatory. No new approval
is pending.

David asked to be notified when the HLS instance is needed. Complete planned
language/reference support first and keep the instance stopped. Notify him once the scoped target plan, generated HLS source
and testbench are ready for vendor simulation/synthesis; record the installed
toolchain, target device and clock then. The next borrowed-result increment does
not need HLS.

The compiler's tracked
[PROJECT_STATE.md](https://github.com/davidydu/spatial-py/blob/work/initial-reference/PROJECT_STATE.md)
owns the exact active task, reproduction commands and latest deployment record.
Follow its [execution plan](https://github.com/davidydu/spatial-py/blob/work/initial-reference/docs/plans/2026-10-13-reference-execution.md).
No new approval is pending. Check the worktree before editing because another
harness may have advanced beyond this publication. [[80 - Initial Compiler Goal]]
is the published big-picture status; older diagrams and slides can lag actual
compiler evidence.

## Documentation and presentation delivery

The [research site](https://davidydu.github.io/spatial-research-site/) builds from
this vault. The current [Python presentation](https://davidydu.github.io/spatial-research-site/presentation/python/)
lives in the site's `presentation/python/` directory. The deck at `/presentation/`
is the historical Rust-era proposal. The editable diagram and original exports
live under `50 - Python Rewrite/30 - Implementation Design/assets/`; the site
has presentation copies. Keep copies consistent when changing the map.

From the site repository, build against the actual research checkout:

```sh
npm run build:site -- --directory '/Users/david/Documents/Spatial Research'
```

Use the Node/npm versions in the site `package.json`; install dependencies with
`npm ci` when needed. Follow the site README for previews and the publication
workflow. A docs-only Quartz rebuild can remove the presentation from generated
`public/`; `build:site` restores the combined output. Never edit generated output
or a build-time `content/` clone as the source of truth.

Publish in order: implementation checkpoint, research notes, then the site.
Research pushes alone do not immediately deploy the separate site. After the
research push completes, push site changes or dispatch its existing workflow:

```sh
gh workflow run deploy.yml --repo davidydu/spatial-research-site --ref main
```

Use the returned run URL/ID, or locate the newly dispatched run with `gh run list`
and verify its branch/commit, then wait for completion. Check changed live pages
for HTTP 200 and new content markers. A successful build or an old deployed page is
not proof that local changes were published. Validate internal links and anchors;
for presentation changes also inspect layouts, navigation, notes and map controls.

## Keep this context shared

Before ending a checkpoint, record the decision, correction, test evidence,
remaining gates, exact next task and any blocker in the owning tracked files.
Update compiler `PROJECT_STATE.md` for implementation state; update this map for
cross-project workflow/preferences; append dated results to [[progress-log]].
Keep `AGENTS.md` and `CLAUDE.md` as short entry pointers instead of parallel memory
stores. Preserve earlier evidence and mark stale resume documents as historical.

Temporary probe logs and old agent sessions may help an investigation, but
required expectations belong in tracked tests/evidence. Do not copy credentials,
unrelated personal memory or raw private transcripts into these repositories.
Model-specific skills are optional: planning, independent review, meaningful
red/green checks and verification can all be performed from these shared files.
