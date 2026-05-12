---
type: moc
project: spatial-spec
date_started: 2026-04-23
---

# Metadata — Index

Per-symbol metadata attached by staging, analyses, and transformers. Categories mirror `src/spatial/metadata/*`.

## Categories

- `10 - Control.md` — `rawLevel`/`rawSchedule`/`rawChildren`/`rawParent`/`rawScope`/`blk`, `userSchedule`/`userII`, `haltIfStarved`, `unrollAsMOP`/`unrollAsPOM`, `shouldNotBind`, control-hierarchy inference (`isInnerControl`/`isOuterControl`/`isFork`/`isStreamControl`).
- `20 - Access.md` — `accessPattern`, `affineMatrices`, `residual`, `modulus`, `residualGenerators`, `dispatch`, `port`, `groupId`, `isBroadcastAddr`, `isDephasedAccess`.
- `30 - Memory.md` — `duplicates`, `instance` (`Memory`/`BankingData`), `depth`, `Bs`/`alphas`/`Ps`/`nBanks`, `resourceType`, `isNBuffered`, `isDualPortedRead`, `keepUnused`, `hotSwapPairings`, `explicitBanking`, `fullyBankDims`, `bankingEffort`, `hierarchical`/`flat`, `isWriteBuffer`/`isNonBuffer`, `isMustMerge`, `shouldIgnoreConflicts`.
- `40 - Retiming.md` — `fullDelay`, `inCycle`, `bodyLatency`, `II`/`compilerII`, `userInjectedDelay`, `forcedLatency`, `hasForcedLatency`.
- `50 - Bounds.md` — `getBound`, `Expect`, `UpperBound`, `rangeParamDomain`, `explicitParamDomain`.
- `60 - Math.md` — `canFuseAsFMA`, rewrite-tracking fields, `specializationFuse`.
- `70 - Params.md` — param domains, nConstraints/alphaConstraints, DSE-specific parameter data.
- `80 - Types.md` — staged-type classification (`isBits`/`FixPtType`/`isFix`/`isFlt`/`isBit`).
- `90 - Blackbox.md` — `bboxInfo`, `BlackboxConfig`, blackbox-use uses.
- `A0 - Debug.md` — `CLIArgs`, `instrumentCounters`, `isInstrumented`, `earlyExits`.
- `B0 - Rewrites.md` — metadata tracking rewrite history.
- `C0 - Transform.md` — metadata that records transformation traces (unrolling lanes, dispatch assignments, etc).

## Source

- `src/spatial/metadata/` (per-category files)
- [[spatial-ir-coverage]] — Phase 1 coverage note
