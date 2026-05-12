---
type: spec
concept: Cppgen per-target dependency files
source_files:
  - "/Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppCodegen.scala:20-82"
  - "/Users/david/Documents/David_code/spatial/src/spatial/codegen/roguegen/RogueCodegen.scala:21-43"
  - "/Users/david/Documents/David_code/spatial/src/spatial/targets/xilinx/KCU1500.scala:6-10"
  - "/Users/david/Documents/David_code/spatial/src/spatial/targets/generic/ASIC.scala:8-24"
  - "/Users/david/Documents/David_code/spatial/src/spatial/Spatial.scala:246-248"
source_notes:
  - "[[other-codegens]]"
hls_status: rework
depends_on:
  - "[[10 - Cppgen]]"
status: draft
---

# Per-Target Files

## Summary

Cppgen's target packaging is controlled by `CppCodegen.copyDependencies`, not by the individual C++ emitters. The method registers fixed dependencies, dispatches on `spatialConfig.target`, registers one software-resource tree, one hardware-resource tree, and one Makefile per target, then appends `build.sbt` and `run.sh` before delegating to `super.copyDependencies(out)` /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppCodegen.scala:20-82. The target matrix is therefore a packaging ABI for generated host projects: a Rust+HLS rewrite can preserve the matrix concept while replacing target contents and Makefile logic /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppCodegen.scala:38-75.

## Syntax or API

Every Cppgen package receives the always-on directories `synth/datastructures`, `synth/SW`, and `synth/scripts` /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppCodegen.scala:25-37. Every Cppgen package also receives `synth/build.sbt` renamed to `build.sbt` at the generated project root and `synth/run.sh` renamed to `run.sh` /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppCodegen.scala:77-79. The target-specific branch uses the same shape for all nine Cppgen targets: `DirDep("synth", "<target>.sw-resources", "../")`, `DirDep("synth", "<target>.hw-resources", "../")`, and `FileDep("synth", "<target>.Makefile", "../", Some("Makefile"))` /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppCodegen.scala:38-75.

## Semantics

The per-target matrix is:

| Spatial target | Software resources | Hardware resources | Makefile |
|---|---|---|---|
| VCS | `vcs.sw-resources` | `vcs.hw-resources` | `vcs.Makefile` as `Makefile` /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppCodegen.scala:39-42 |
| Zynq | `zynq.sw-resources` | `zynq.hw-resources` | `zynq.Makefile` as `Makefile` /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppCodegen.scala:43-46 |
| ZedBoard | `zedboard.sw-resources` | `zedboard.hw-resources` | `zedboard.Makefile` as `Makefile` /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppCodegen.scala:47-50 |
| ZCU | `zcu.sw-resources` | `zcu.hw-resources` | `zcu.Makefile` as `Makefile` /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppCodegen.scala:51-54 |
| CXP | `cxp.sw-resources` | `cxp.hw-resources` | `cxp.Makefile` as `Makefile` /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppCodegen.scala:55-58 |
| AWS_F1 | `aws.sw-resources` | `aws.hw-resources` | `aws.Makefile` as `Makefile` /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppCodegen.scala:59-62 |
| DE1 | `de1.sw-resources` | `de1.hw-resources` | `de1.Makefile` as `Makefile` /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppCodegen.scala:63-66 |
| Arria10 | `arria10.sw-resources` | `arria10.hw-resources` | `arria10.Makefile` as `Makefile` /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppCodegen.scala:67-70 |
| ASIC | `asic.sw-resources` | `asic.hw-resources` | `asic.Makefile` as `Makefile` /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppCodegen.scala:71-74 |

This matrix describes file-copy intent, not target capability. KCU1500 is intentionally absent from the Cppgen switch because `KCU1500.host` returns `"rogue"` and the main Spatial pipeline invokes Cppgen only when synthesis is enabled and `target.host == "cpp"` /Users/david/Documents/David_code/spatial/src/spatial/targets/xilinx/KCU1500.scala:6-10 /Users/david/Documents/David_code/spatial/src/spatial/Spatial.scala:246-248.

There is no default branch in the target match, so the active source only documents packaging for the nine cases listed above /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppCodegen.scala:38-75. A new Rust+HLS target should therefore be added deliberately to a target table or to an equivalent match, rather than relying on a generic fallback (inferred, unverified). The fixed dependencies still apply across all matched targets because they are registered before and after the target-specific branch /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppCodegen.scala:25-37 /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppCodegen.scala:77-82.

## Implementation

`copyDependencies` accumulates `DirDep` and `FileDep` objects in a mutable `dependencies` list; the code comments show older fringe resource entries that are currently disabled, while the active code copies only the generic synth directories, scripts, selected target trees, `build.sbt`, and `run.sh` /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppCodegen.scala:20-37 /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppCodegen.scala:77-82. The output-root parameter is not used directly by the branch logic; it is passed to `super.copyDependencies(out)` after the list is assembled /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppCodegen.scala:20-82.

Roguegen has its own dependency copy path. It always copies `synth/scripts`, `build.sbt`, and `run.sh`, and only branches on `KCU1500` to copy `kcu1500.sw-resources`, `kcu1500.hw-resources`, and `kcu1500.Makefile` /Users/david/Documents/David_code/spatial/src/spatial/codegen/roguegen/RogueCodegen.scala:21-43. This means a KCU1500 Spatial compile goes through the Rogue host packaging path, not through Cppgen's nine-target matrix /Users/david/Documents/David_code/spatial/src/spatial/targets/xilinx/KCU1500.scala:6-10 /Users/david/Documents/David_code/spatial/src/spatial/Spatial.scala:246-248.

ASIC has a target object but incomplete capacity details. It extends `HardwareTarget`, uses `GenericAreaModel`, defines `makeLatencyModel` as `new LatencyModel(xilinx.Zynq)`, declares one `"SRAM"` memory resource with zero area/summary, names itself `"ASIC"`, and sets `burstSize = 512` /Users/david/Documents/David_code/spatial/src/spatial/targets/generic/ASIC.scala:8-24. Therefore ASIC borrows the Zynq latency model even though it has separate Cppgen resource trees and Makefile entries /Users/david/Documents/David_code/spatial/src/spatial/targets/generic/ASIC.scala:11-12 /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppCodegen.scala:71-74.

## Interactions

Cppgen packaging is scheduled after Chisel codegen when synthesis is enabled and the target host is `"cpp"` /Users/david/Documents/David_code/spatial/src/spatial/Spatial.scala:246-247. Rogue packaging is scheduled separately when `target.host == "rogue"` /Users/david/Documents/David_code/spatial/src/spatial/Spatial.scala:247-248. The packaging matrix therefore interacts with target metadata, not merely with CLI flags /Users/david/Documents/David_code/spatial/src/spatial/targets/xilinx/KCU1500.scala:6-10 /Users/david/Documents/David_code/spatial/src/spatial/Spatial.scala:246-248.

## HLS notes

The rewrite should separate target packaging from host-language generation. The current code couples Cppgen to `synth/<target>.*-resources` directory names and Makefile names, but the repeated shape can be preserved as a target descriptor table /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppCodegen.scala:38-75. ASIC needs explicit review because its packaging is target-specific while its latency model is borrowed from Zynq /Users/david/Documents/David_code/spatial/src/spatial/targets/generic/ASIC.scala:11-12 /Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppCodegen.scala:71-74.

The Rogue split is also an HLS packaging warning: a board can be a synthesis target without using the Cpp host path, because `target.host` controls whether Cppgen or Roguegen runs /Users/david/Documents/David_code/spatial/src/spatial/targets/xilinx/KCU1500.scala:6-10 /Users/david/Documents/David_code/spatial/src/spatial/Spatial.scala:246-248. Host selection should remain target metadata in the rewrite, even if the legacy Rogue implementation is retired (inferred, unverified).

## Open questions

See [[open-questions-other-codegens#Q-oc-05]] for whether Rust+HLS should keep the existing `<target>.sw-resources` and `<target>.hw-resources` directory convention or replace it with typed target descriptors.
