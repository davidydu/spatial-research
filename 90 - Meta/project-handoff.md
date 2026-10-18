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

Current executed checkpoint: **`spatial-py@c94d1b0`**, verified on 17 October
with **1156 source tests and 1156 isolated installed-wheel tests**, CPython 3.14.5.
The latest addition is per-call helper specialization. Next: owned regions and
finite static expansion.

**One helper can now use different compile-time settings within one program.**
`Meta[Size]`, `Meta[Integer]` and `Meta[Bool]` configure helper dimensions, local
memory and computation. The shared normalizer creates a concrete helper for each
lexical template and distinct settings; repeated settings reuse it. Calls remain
explicit. Runtime arguments still evaluate once in written order, and nested
helpers can capture settings, values and borrowed memory.

The [tile helper source](https://github.com/davidydu/spatial-py/blob/c94d1b0/examples/kernels/specialized_tiles.py) and
[runner](https://github.com/davidydu/spatial-py/blob/c94d1b0/examples/run_helper_meta_reference.py) call one transform with
tile sizes two and three. Input `[3,5,8,13,21]` produces `[1,3,6,11,19]` and
`[-2,0,3,8,16]` in the same program. A second case checks signed overflow.
Both cases preserve host inputs and clean up each temporary allocation.
See [recorded outputs](https://github.com/davidydu/spatial-py/blob/c94d1b0/docs/evidence/helper-meta-reference-output.json),
[evidence](https://github.com/davidydu/spatial-py/blob/c94d1b0/docs/evidence/task-05h-helper-meta.md),
[reviews](https://github.com/davidydu/spatial-py/blob/c94d1b0/docs/reviews/2026-10-17-helper-meta.md) and the
[fresh composition](https://github.com/davidydu/spatial-py/blob/c94d1b0/docs/evidence/task-05h-helper-meta-acceptance-third.md).
Independent specification/quality review and parent review passed. Frozen files
and all 70 packaged compiler modules match through source and installed-wheel
verification. Existing symbolic slice-equality and pure-tokenless-check limits
remain documented. This is reference execution; static expansion, full lab
coverage and HLS remain unfinished.

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

**Helpers can now return memory windows that the caller keeps using.**
A returned view can be assigned to a named local, passed to another helper,
selected conditionally, read/written or used in a transfer. The chosen storage
and coordinates survive helper cleanup. Returning temporary helper-local memory
rejects, including an inactive return alternative. This lets ordinary tile/window
programs be split into reusable helpers through the shared compiler route.

See the [runnable demo](https://github.com/davidydu/spatial-py/blob/813718f/examples/run_borrowed_views_reference.py),
[Python source](https://github.com/davidydu/spatial-py/blob/813718f/examples/kernels/selected_views.py),
[recorded results](https://github.com/davidydu/spatial-py/blob/813718f/docs/evidence/borrowed-views-reference-output.json),
[review](https://github.com/davidydu/spatial-py/blob/813718f/docs/reviews/2026-10-17-borrowed-result-execution.md) and
[execution evidence](https://github.com/davidydu/spatial-py/blob/813718f/docs/evidence/task-05e-borrowed-results.md).
The demo checks five separate/aliased and nested-helper scenarios. Independent
source/common programs agree on full traces; all eight original borrowed-result
groups now have execution or rejection evidence. Reviews repaired conditional
shape handling, two context-free selection gaps and an older explicit-slice
regression before the final production freeze.
A [separately authored composition](https://github.com/davidydu/spatial-py/blob/813718f/docs/evidence/task-05e-borrowed-acceptance-composition.md)
records its literal expectations and first-run results. Both complete package
routes pass **1019 tests** on unchanged frozen files.

Pure tokenless forwarding still rejects when its entry checks cannot be proved;
ordered helpers retain the existing runtime checks. This is a documented boundary,
not a claim that all helper compositions or the initial compiler are complete.

**Compile-time constants and type aliases now work in executable programs.**
Module constants may refer to later constants; local constants follow lexical
scope. Nested helpers can use them for memory sizes, signatures and calculations
without extra runtime arguments. Closed Int/Index/Bool/Unit aliases also support
conditional type selection. A tiled example combines these features with
captured memory and returned views; its ordinary output is `[1,3,6,11,19,32]`,
and a separate signed-overflow vector also passes.

See the [source](https://github.com/davidydu/spatial-py/blob/316cb7c/examples/kernels/constant_tiles.py),
[runnable demo](https://github.com/davidydu/spatial-py/blob/316cb7c/examples/run_constants_reference.py),
[recorded results](https://github.com/davidydu/spatial-py/blob/316cb7c/docs/evidence/constants-reference-output.json),
[execution evidence](https://github.com/davidydu/spatial-py/blob/316cb7c/docs/evidence/task-05f-constants.md),
[review](https://github.com/davidydu/spatial-py/blob/316cb7c/docs/reviews/2026-10-17-constants.md) and
[fresh composition](https://github.com/davidydu/spatial-py/blob/316cb7c/docs/evidence/task-05f-constants-acceptance-third.md).
Independent specification and quality reviews passed after scope and source/common
parity repairs. An earlier composition used a possibly failing conversion in a
pure helper; its annotation-only repair is retained as regression. A second
case required a test-observer correction and is also regression evidence; a
third independent author supplied fresh acceptance. **1079 source tests and
1079 isolated-wheel tests pass** on unchanged frozen files. The existing canonical verifier and runtime were not expanded.

Next: ordered REGION execution and ownership, then finite `static`/`static_range`
expansion. Preserve fresh declaration identities, lexical capture remapping,
result/borrow ownership and cleanup at each local-memory scope exit. Static
copies must not extend SRAM lifetime to function exit. Validate retained source
and helper recursion before elimination, and charge generated records and integer
growth before allocation. Pin exact one-/two-bound static_range syntax and its
protected Integer binder before implementation.

True resumable budgets, artifact agreement, verified
editing and final whole-goal acceptance remain required. Current private
resource-limit results have no continuation. HLS tools are not needed yet.

David authorized continued implementation; no new approval is pending.

David asked to be notified when the HLS instance is needed. Complete planned
language/reference support first and keep the instance stopped. Notify him once the scoped target plan, generated HLS source
and testbench are ready for vendor simulation/synthesis; record the installed
toolchain, target device and clock then. The next meta/static language increment does
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
