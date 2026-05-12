---
type: open-questions
topic: fringe-targets
session: 2026-04-25
date_started: 2026-04-25
---

# Open Questions - Fringe Targets

## Q-ft-01 - 2026-04-25 Base-cycle consumer for compiler targets

`HardwareTarget` defines `baseCycles = 43000`, but the source pass for target specs did not identify a consumer. Need verify whether this startup-cycle constant still affects DSE/reporting or is dead compatibility state.

Source: src/spatial/targets/HardwareTarget.scala:17-18
Blocked by: target latency-model audit
Status: open
Resolution:

## Q-ft-02 - 2026-04-25 magPipelineDepth consumer

`DeviceTarget.magPipelineDepth` is exposed through `globals.magPipelineDepth`, and `MAGToAXI4Bridge` reads it into `numPipelinedLevels`, but the bridge body does not use that value afterward. Need decide whether this was intended to insert AXI retiming and whether HLS should ignore or revive it.

Source: fringe/src/fringe/targets/DeviceTarget.scala:18; fringe/src/fringe/globals.scala:15-16; fringe/src/fringe/templates/axi4/MAGToAXI4Bridge.scala:20
Blocked by: AXI timing design
Status: open
Resolution:

## Q-ft-03 - 2026-04-25 AdvancedColored channel assignment status

`AdvancedColored` claims to account for transfer intensity but has a TODO and currently returns the same round-robin assignment shape as `BasicRoundRobin`. Need verify whether any compiler path selects it and whether HLS channel assignment should include the intended advanced policy.

Source: fringe/src/fringe/ChannelAssignment.scala:30-34
Blocked by: channel-assignment selector audit
Status: open
Resolution:

## Q-ft-04 - 2026-04-25 argOutLoopbacksMap ownership

`globals.argOutLoopbacksMap` is counted by `NUM_ARG_LOOPS` but the source pass did not find the writer or runtime semantics. Need identify whether it affects scalar echo/loopback behavior before redesigning the host ABI.

Source: fringe/src/fringe/globals.scala:47-78
Blocked by: chiselgen scalar-layout audit
Status: open
Resolution:

## Q-ft-05 - 2026-04-25 ASIC latency model source

The compiler-side `ASIC` target uses `GenericAreaModel` but constructs its latency model from `xilinx.Zynq`. Need decide whether this is intentional reuse, placeholder behavior, or a bug before deriving HLS/ASIC latency defaults.

Source: src/spatial/targets/generic/ASIC.scala:8-13
Blocked by: target-model policy
Status: open
Resolution:

## Q-ft-06 - 2026-04-25 Empty non-Xilinx target capacities

`Arria10`, `DE1`, and `ASIC` declare empty capacities. Need determine whether DSE can run meaningfully against these targets and whether HLS should fail fast when capacities are empty.

Source: src/spatial/targets/altera/Arria10.scala:11-13; src/spatial/targets/altera/DE1.scala:11-13; src/spatial/targets/generic/ASIC.scala:26-28
Blocked by: HLS target inventory
Status: open
Resolution:

## Q-ft-07 - 2026-04-25 OpMemReduce access-unroll formula

`AreaModel.accessUnrollCount` multiplies by the sum of map and reduce counter-chain parallelism for `OpMemReduce`, with an inline comment saying this is definitely wrong. Need establish the correct formula before relying on memory-area estimates in HLS.

Source: src/spatial/targets/AreaModel.scala:41-58
Blocked by: banking and DSE area-model review
Status: open
Resolution:

## Q-ft-08 - 2026-04-25 TileLoadModel disabled state

`GenericLatencyModel` calls `TileLoadModel.evaluate`, but `TileLoadModel` has the neural-network implementation commented out and returns `0.0`. Need decide whether this model is dead, temporarily disabled, or should be retrained/reimplemented for HLS.

Source: src/spatial/targets/generic/GenericLatencyModel.scala:11-68; src/spatial/targets/generic/TileLoadModel.scala:16-109
Blocked by: HLS latency-model training plan
Status: open
Resolution:

## Q-ft-09 - 2026-04-25 DRAM debug-register cap

`DRAMArbiter` hard-codes `numDebugs = 500` and increments debug signal registration until labels are written, but no assertion was found for overflow beyond the vector size. Need verify whether debug signals can silently exceed the cap.

Source: fringe/src/fringe/templates/dramarbiter/DRAMArbiter.scala:22; fringe/src/fringe/templates/dramarbiter/DRAMArbiter.scala:103-118; fringe/src/fringe/templates/dramarbiter/DRAMArbiter.scala:255-263
Blocked by: debug-register stress test
Status: open
Resolution:

## Q-ft-10 - 2026-04-25 FringeZynq bridge fallback behavior

`FringeZynq` selects AXI-Lite bridge variants for KCU1500, Zynq/ZedBoard, and ZCU, with no default branch for other target classes that may reuse the shell. Need determine whether every target using `FringeZynq` is covered or whether some shells leave register-file wiring unassigned.

Source: fringe/src/fringe/targets/zynq/FringeZynq.scala:79-117; fringe/src/fringe/targets/aws/AWS_F1.scala:9-40
Blocked by: target-shell elaboration audit
Status: open
Resolution:

## Q-ft-11 - 2026-04-25 BigIP optional arithmetic behavior

Many `BigIP` operations default to throwing `Unimplemented`, and several simulation methods for trig/hyperbolic operations return the input with TODO comments. Need decide which operations the HLS rewrite must support, reject, or lower to vendor libraries.

Source: fringe/src/fringe/BigIP.scala:22-105; fringe/src/fringe/targets/BigIPSim.scala:82-96
Blocked by: HLS numeric-library policy
Status: open
Resolution:

## Q-ft-12 - 2026-04-25 IICounter first-cycle issue dependency

`IICounter` has a TODO noting that old behavior issued done on the first cycle and the current switch to `cnt == 0` versus `cnt == ii-1` may break dependent logic. Need confirm the intended initiation-interval handshake before porting controller schedules.

Source: fringe/src/fringe/templates/counters/Counter.scala:121-150
Blocked by: controller timing regression tests
Status: open
Resolution:
