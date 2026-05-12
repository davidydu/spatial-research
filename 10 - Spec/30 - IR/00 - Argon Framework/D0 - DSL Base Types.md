---
type: spec
concept: Argon DSL Base Types
source_files:
  - "argon/src/argon/lang/Top.scala:10-74"
  - "argon/src/argon/lang/Bit.scala:9-51"
  - "argon/src/argon/lang/Fix.scala:8-224"
  - "argon/src/argon/lang/Flt.scala:9-157"
  - "argon/src/argon/lang/Vec.scala:11-228"
  - "argon/src/argon/lang/Struct.scala:7-32"
  - "argon/src/argon/lang/Tup2.scala:6-60"
  - "argon/src/argon/lang/Text.scala:8-35"
  - "argon/src/argon/lang/Var.scala:8-20"
  - "argon/src/argon/lang/Void.scala:6-21"
  - "argon/src/argon/lang/Series.scala:12-54"
  - "argon/src/argon/lang/Aliases.scala:7-180"
  - "argon/src/argon/lang/package.scala:1-3"
  - "argon/src/argon/lang/types/Bits.scala:8-171"
  - "argon/src/argon/lang/types/Arith.scala:7-40"
  - "argon/src/argon/lang/types/Num.scala:8-60"
  - "argon/src/argon/lang/types/Order.scala:7-42"
  - "argon/src/argon/lang/types/CustomBitWidths.scala:5-27"
  - "argon/src/argon/lang/types/CustomBitWidths.scala:28-163"
  - "argon/src/argon/lang/types/CustomBitWidths.scala:165-460"
  - "argon/src/argon/lang/api/package.scala:1-3"
  - "argon/src/argon/lang/api/Implicits.scala:15-405"
  - "argon/src/argon/lang/api/BitsAPI.scala:6-21"
  - "argon/src/argon/lang/api/DebuggingAPI.scala:7-37"
  - "argon/src/argon/lang/api/TuplesAPI.scala:6-17"
  - "argon/src/argon/node/Struct.scala:7-38"
  - "argon/src/argon/node/Var.scala:7-45"
source_notes:
  - "[[argon-framework]]"
hls_status: clean
depends_on:
  - "[[10 - Symbols and Types]]"
  - "[[20 - Ops and Blocks]]"
  - "[[30 - Effects and Aliasing]]"
status: draft
---

# Argon DSL Base Types

## Summary

`argon.lang` is the minimal staged DSL surface that sits above `Ref`, `Type`, `Sym`, and `Op`. The package object exposes `InternalAliases`, while `argon.lang.api` exposes `ExternalAliases`, which separates framework-internal shorthand from application-facing type and value aliases (`argon/src/argon/lang/package.scala:1-3`, `argon/src/argon/lang/api/package.scala:1-3`, `argon/src/argon/lang/Aliases.scala:7-180`). Spatial-specific node types are layered above this base DSL in a different source tree (inferred, unverified here); within Argon, the base surface consists of `Top`, the staged scalar/container types, typeclass traits, literal width singletons, and API implicits.

## Syntax / API

`Top[A]` is the root of staged DSL values: it extends `Ref[Any,A]`, requires evidence that `A` is itself a `Ref`, and defines staged equality/inequality, string concatenation, and generic `toText` conversion (`argon/src/argon/lang/Top.scala:10-24`, `argon/src/argon/lang/Top.scala:43-74`). Equality attempts staged comparison for matching `Top` types, attempts constant conversion when possible, and otherwise warns about unrelated types before falling back to host equality (`argon/src/argon/lang/Top.scala:12-20`, `argon/src/argon/lang/Top.scala:24-61`).

The typeclass tower is staged, not host-only. `Bits[A]` extends `Top[A]` and `Ref[Any,A]` and supplies bit indexing, `msb`, `lsb`, bit slicing, bit reinterpretation, `nbits`, `zero`, `one`, and `random` (`argon/src/argon/lang/types/Bits.scala:8-18`, `argon/src/argon/lang/types/Bits.scala:20-39`, `argon/src/argon/lang/types/Bits.scala:45-101`). `Arith[A]` adds unary negation and `+ - * / %`, plus `neg/add/sub/mul/div/mod/abs/ceil/floor` helpers (`argon/src/argon/lang/types/Arith.scala:7-31`). `Order[A]` adds `<`, `<=`, derived `>` and `>=`, and `min/max` (`argon/src/argon/lang/types/Order.scala:7-34`). `Num[A]` combines `Order`, `Arith`, and `Bits`, adds exponentiation, range constructors, math functions, and conversion hooks to `Fix` and `Flt` (`argon/src/argon/lang/types/Num.scala:8-23`, `argon/src/argon/lang/types/Num.scala:26-50`).

## Semantics

`Bit` is a staged Boolean with bitwise boolean ops, typeclass width one, false/true zero/one, random generation, constant parsing from booleans and numeric/string literals, and a `BitType` extractor (`argon/src/argon/lang/Bit.scala:9-29`, `argon/src/argon/lang/Bit.scala:31-51`). `Fix[S,I,F]` is the central integer/fixed-point staged number: `FixFmt` carries sign, integer-bit, and fraction-bit singleton evidence, reports `nbits = ibits + fbits`, and converts to the emulator `FixFormat`; `Fix` then stages arithmetic, bitwise ops, shifts, comparisons, min/max, random, saturating and unbiased variants, math functions, textual conversion, and conversions to other `Fix` or `Flt` formats (`argon/src/argon/lang/Fix.scala:8-25`, `argon/src/argon/lang/Fix.scala:34-73`, `argon/src/argon/lang/Fix.scala:75-147`, `argon/src/argon/lang/Fix.scala:193-208`). `Flt[M,E]` is an IEEE-like staged float with selectable mantissa and exponent widths, `FltFmt.toEmul`, arithmetic, comparisons, NaN/infinity checks, min/max, random, math functions, textual conversion, and conversions to `Fix` or other `Flt` formats (`argon/src/argon/lang/Flt.scala:9-25`, `argon/src/argon/lang/Flt.scala:29-60`, `argon/src/argon/lang/Flt.scala:62-123`).

`Vec[A]` is both a staged value vector and bit vector abstraction: it is parameterized by a `Bits[A]` element type and width, computes `elems` from staged applies, supports map/zip/reduce, arithmetic when the element type has an `Arith` view, `asBits`, integer and range apply, slicing, concatenation, packing, reverse, equality, `nbits`, zero/one, and random (`argon/src/argon/lang/Vec.scala:11-34`, `argon/src/argon/lang/Vec.scala:35-63`, `argon/src/argon/lang/Vec.scala:69-145`). The companion creates typed vector prototypes, endian-named constructors, empty vectors, allocation from sequences, slices, concatenations, popcount, and reconstruction from bits (`argon/src/argon/lang/Vec.scala:150-228`). A dynamic `I32` vector apply currently returns index zero unless the index is a constant, so dynamic vector indexing is not represented by a distinct node here (`argon/src/argon/lang/Vec.scala:59-63`); see Q-arg-004.

`Struct[A]` is a staged record type with declared `(fieldName, fieldType)` pairs, derived `fieldMap`, staged equality over bit-capable fields, and construction/application/update helpers that stage `SimpleStruct`, `FieldApply`, and `FieldUpdate` nodes (`argon/src/argon/lang/Struct.scala:7-24`, `argon/src/argon/lang/Struct.scala:26-32`). The node layer makes `SimpleStruct` transient and containing of its element symbols, rewrites immutable `FieldApply` on a `SimpleStruct` to the matching field symbol, and marks `FieldUpdate` as a write effect on the struct (`argon/src/argon/node/Struct.scala:7-17`, `argon/src/argon/node/Struct.scala:19-38`). `Tup2[A,B]` is implemented as a two-field struct named `_1` and `_2`, and it lifts arithmetic and bit operations only when both component types expose the required views (`argon/src/argon/lang/Tup2.scala:6-17`, `argon/src/argon/lang/Tup2.scala:25-54`).

`Text` is staged `String`, with staged equality, inequality, concatenation, length, indexing, slicing, constants, and identity `toText` (`argon/src/argon/lang/Text.scala:8-35`). `Var[A]` is the mutable staged variable wrapper with staged `read`, `assign`, and `alloc`; the node layer marks allocation mutable, reads as extracting from the variable, and assignments as writes to the variable (`argon/src/argon/lang/Var.scala:8-20`, `argon/src/argon/node/Var.scala:7-45`). `Void` is staged unit with equality always true against another `Void`, inequality always false, unit constant extraction, and `Void.c` for a staged unit constant (`argon/src/argon/lang/Void.scala:6-21`). `Series[A]` is the staged counter/range value: it stores start, end, step, parallelism, and a unit flag; supports `::`, `by`, `par`, staged `length`, constant-only `meta`, element `at`, and `foreach` lowered through `stageLambda1` and `SeriesForeach` (`argon/src/argon/lang/Series.scala:12-27`, `argon/src/argon/lang/Series.scala:29-54`).

## Implementation

Custom widths are encoded as singleton evidence because Scala has no integer type parameters in this style: `BOOL[T]` wraps a Boolean, `TRUE` and `FALSE` provide signedness evidence, `INT[T]` wraps an `Int`, and named traits define `_0` through `_128` plus selected larger widths `_160`, `_192`, `_200`, `_240`, `_256`, `_512`, and `_1024` (`argon/src/argon/lang/types/CustomBitWidths.scala:5-27`, `argon/src/argon/lang/types/CustomBitWidths.scala:28-163`). Companion objects provide implicit `BOOL_TRUE`, `BOOL_FALSE`, and `INT` instances for those singleton widths, while `CustomBitWidths` re-exports the types and singleton names (`argon/src/argon/lang/types/CustomBitWidths.scala:165-313`, `argon/src/argon/lang/types/CustomBitWidths.scala:316-460`). `InternalAliases` defines `FixPt`, index/range aliases, signed and unsigned integer aliases such as `I32` and `U8`, float aliases `F64/F32/F16`, and typeclass shorthands; `ExternalAliases` adds user-facing aliases for the actual staged classes and companion values (`argon/src/argon/lang/Aliases.scala:7-126`, `argon/src/argon/lang/Aliases.scala:128-175`).

The API layer supplies implicit casts and wrappers rather than new IR types. `Implicits` defines numeric casts across `Fix` and `Flt`, staged string conversion, wrappers for arithmetic and ordering against `VarLike`, literal lifting for host primitives, staged range syntax on `Int`, casts between `Text`, `Bit`, `Fix`, and `Flt`, and implicit lifting from Scala primitives into staged values (`argon/src/argon/lang/api/Implicits.scala:15-60`, `argon/src/argon/lang/api/Implicits.scala:62-140`, `argon/src/argon/lang/api/Implicits.scala:179-245`, `argon/src/argon/lang/api/Implicits.scala:248-405`). `BitsAPI` exposes `zero`, `one`, random generation, concatenation, and popcount; `TuplesAPI` packs and unpacks staged pairs; `DebuggingAPI` stages print, assert, exit, and breakpoint nodes over `Text` and `Bit` (`argon/src/argon/lang/api/BitsAPI.scala:6-21`, `argon/src/argon/lang/api/TuplesAPI.scala:6-17`, `argon/src/argon/lang/api/DebuggingAPI.scala:7-37`).

## Interactions

This entry depends on `[[10 - Symbols and Types]]` because every DSL value is a `Ref` with type evidence, on `[[20 - Ops and Blocks]]` because every API method stages `Op` nodes, and on `[[30 - Effects and Aliasing]]` because mutable objects such as `Var` and `Struct` updates attach effects (`argon/src/argon/lang/Top.scala:10-10`, `argon/src/argon/lang/Var.scala:17-19`, `argon/src/argon/node/Var.scala:7-45`, `argon/src/argon/node/Struct.scala:35-38`).

## HLS notes

The base DSL is HLS-clean. Fixed, integer, float, and bit-vector widths are already explicit in `FixFmt`, `FltFmt`, `Bits.nbits`, and `Vec.width`, so an HLS implementation can map these concepts to native arbitrary-precision integer, fixed-point, and floating-point types; the specific `ap_int` / `ap_fixed` / `ap_float` mapping is target-specific and therefore inferred rather than stated by Argon source (`argon/src/argon/lang/Fix.scala:8-25`, `argon/src/argon/lang/Flt.scala:9-20`, `argon/src/argon/lang/types/Bits.scala:97-101`, `argon/src/argon/lang/Vec.scala:11-14`). The main porting risks are host-language ergonomics: Scala implicit conversions, singleton-width evidence, and `VarLike` lifting need Rust-native or C++-native equivalents (`argon/src/argon/lang/types/CustomBitWidths.scala:165-460`, `argon/src/argon/lang/api/Implicits.scala:248-405`).

## Open questions

- See `[[open-questions-argon-supplemental]]` Q-arg-003: are the `Flt.__toFixSat`, `Flt.__toFixUnb`, and `Flt.__toFixUnbSat` variants intentionally lowered to the same `FltToFix` node as plain `__toFix` (`argon/src/argon/lang/Flt.scala:109-119`)?
- See `[[open-questions-argon-supplemental]]` Q-arg-004: should dynamic `Vec.apply(i: I32)` stage a dynamic index node instead of falling back to element zero when `i` is not a constant (`argon/src/argon/lang/Vec.scala:59-63`)?
