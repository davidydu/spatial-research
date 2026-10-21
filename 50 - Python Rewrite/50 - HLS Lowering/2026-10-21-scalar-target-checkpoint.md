---
type: implementation-checkpoint
title: "Scalar state and shifts reach generated C++"
project: spatial-python
date: 2026-10-21
status: local-validation
---

Python Spatial now generates C++ for programs that carry a scalar value across
loop iterations and return scalar results. Seeded sums, tiled dot products and
order-sensitive updates use the same compiler rules. Integer shifts also work
through the backend, including the program rejected in the first vendor study.

**These additions are locally validated. Their new HLS synthesis and RTL runs
are pending.** The earlier [[2026-10-21-vitis-rtl-checkpoint|four-kernel hardware checkpoint]] remains the vendor evidence. The instance is stopped; ask David
before using it again.

## What changed

| Addition | What a program can express | What the implementation preserves |
|---|---|---|
| Scalar `InOut[Int]` | Read an initial value, update it through loops/helpers, and return its final value | Shared cell identity, ordered reads/writes, a fresh copied seed for each invocation |
| Scalar `Out[Int]` | Return a result without allocating an output array in source | No host seed; incomplete writes remain incomplete; only successful completion publishes outputs |
| Int shifts with Index counts | Shift by a literal, input-derived or computed count | Signed counts, negative-count faults, large-count zero/sign fill, no narrowing to 32-bit counts |

The compiler lowers scalar cells to one data slot and one initialization slot.
The prepared vendor interface uses the existing memory-port protocol at depth
one. This is an experimental IP interface, not final board/AXI integration.
The language checker and reference engine already defined this scalar behavior;
the extension changes four backend modules without changing language semantics.

The [implementation](https://github.com/davidydu/spatial-py/commit/1e55eb8)
contains general operation rules. Kernel names, lab numbers and whole-program
shapes do not select compiler behavior. This is sequential accumulation;
dedicated Reg, Reduce/Fold and parallel reduction semantics remain future work.

## Programs checked locally

The [prepared development batch](https://github.com/davidydu/spatial-py/tree/work/initial-reference/docs/evidence/scalar-target-demo)
contains **11 projects and 28 cases**. Each case separately matches independent
expected data, initialization and status in Python reference execution, generated
native C++, and the saved wrapper/testbench compiled locally with optimization
and undefined-behavior checks.

| Program family | Distinguishing cases |
|---|---|
| Original shift composition | Signed floor division and shifting, overflow, and an uninitialized read after earlier writes; original source and oracles retained |
| Tiled dot product | Lengths 5, 16 and 33; partial tiles; a helper updating captured scalar state; disabled computation preserving its seed; overflow and a late division fault |
| Ordered scalar update | Branches and helper calls, with an earlier read remaining unchanged after the cell is updated; two seeds and a late fault |
| Seeded sum | Independent scalar input state and scalar output, repeated invocations |
| Tiled map/copy | Lengths 8, 32, 33 and 128, including a tile-capacity comparison at fixed length |

For example, a signed five-element dot product starts from 10 and finishes at 4.
An order-sensitive recurrence starts from 2 and visits 7, 23, 72 and 220. The
recorded differences are 5, 16, 49 and 148, which also checks that an earlier read
keeps its value. On a final division fault, the completed state updates survive
and the unwritten result remains uninitialized.

A separate author then wrote a new directional-follower program after the
implementation was frozen. Its four prewritten cases passed on their first run,
with no compiler or example repair. It combines captured state, shifts, branches,
an SRAM snapshot, overflow, a late division fault and incomplete output. Together
the development and fresh bundles contain **12 projects and 32 cases**, ready
for the next vendor run.

The complete suites pass **1,329 tests from source and 1,329 against an isolated
installed package**. All 110 frozen production files and 80 installed modules
match their recorded hashes. Independent specification, code-quality and final
acceptance reviews found no remaining issue in this increment.

The [compiler evidence](https://github.com/davidydu/spatial-py/blob/work/initial-reference/docs/evidence/task-06c-scalar-target.md)
owns the production freeze, independent fresh-program acceptance, exact test
results, tool versions and file manifests. Development examples are separate
from the fresh acceptance program; passing a repaired former holdout does not
make it a new independent success.

## What we learned about hardware cost

The [saved-report audit](https://github.com/davidydu/spatial-py/blob/work/initial-reference/docs/evidence/task-06c-cost-audit.md)
found separate guard-preflight, copy-preflight, snapshot and write loops in the
earlier Lab 1 synthesis reports. Both preflight scans survived synthesis in that
design. That identifies a concrete question for measurement, not a proven
bottleneck or promised speedup.

The new size variants prepare the next measurements. Static storage counters and
generated source sizes are recorded separately from hardware resources. External
port memories are excluded from the old HLS resource estimates, and transaction
interval is not loop initiation interval. No new timing/resource result is claimed.

## Next

1. With David's authorization, run the saved new projects through vendor C
   simulation, synthesis and RTL co-simulation; retain exact settings and hashes.
2. Compare successful-path size/tile measurements, keeping fault cases separate.
3. Select one general storage or scheduling improvement and verify its behavior
   and measured effect. Any removal of a scan or snapshot must preserve aliases,
   initialization, fault order and earlier writes.

Continue the [[04 - Python Implementation Roadmap|Labs 1–3 progression]] with
local registers/reductions, multidimensional target memory and queue/window
families in small executable increments. Public check/prepare, real simulation
resumption, full checked target planning and board integration remain open.
