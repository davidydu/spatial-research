---
type: research
decision: D-01
angle: 7
title: HLS Native Math Support for Spatial BigIP Ops
date: 2026-04-25
---

## 1. Native operators

- **Vivado HLS:** plain C/C++ `+`, `-`, `*`, `/` synthesize for integers, `ap_int`, `ap_fixed`, `float`, and `double`. Integer `%` is native; `%` on `ap_fixed` is version-sensitive (unverified). `a*b+c` is legal source for FMA-like hardware, but exact fused semantics require `hls::fma` or binding control (unverified). `fix2flt`/`flt2fix` map to casts, assignment, or `to_float()`/`to_double()`.
- **Vitis HLS:** same source-level operators, plus current `ap_float<W,E>` supports binary `+`, `-`, `*`, `/`, assignment forms, comparisons, `hls::sqrt`, `hls::fma`, `hls::abs`, and `ap_float_acc<>`. Floating accumulation can be written as `sum += x`; `syn.op` can select `facc`, `fmacc`, or `fmadd`.
- **Intel Quartus HLS:** native C++ arithmetic works for integer and `float`/`double`; `ac_int`/`ac_fixed` provide overloaded arithmetic including `+`, `-`, `*`, `/`, and `%` (unverified for all fixed formats). `hls_float` supports `+`, `-`, `*`, `/`, assignment operators, comparisons, unary signs, and explicit `add/sub/mul/div`.

## 2. `hls_math.h` / math namespaces

AMD/Xilinx `hls_math.h` supports standard `math.h`/`cmath` synthesis and optional `hls::` calls. Current Vitis includes trig (`acos`, `asin`, `atan`, `atan2`, `cos`, `sin`, `sincos`, `tan`, plus pi variants), hyperbolic (`acosh`, `asinh`, `atanh`, `cosh`, `sinh`, `tanh`), exponentials (`exp`, `exp2`, `exp10`, `expm1`, `frexp`, `ldexp`, `modf`), logs (`log`, `log10`, `log1p`, `ilogb`), power (`cbrt`, `hypot`, `pow`, `rsqrt`, `sqrt`), error, rounding, remainder, min/max, classification, comparison, and other functions including `abs`, `divide`, `fabs`, `fma`, `fract`, `mad`, `recip`. Vivado HLS 2019-era UG902 appears to expose essentially the same list; older Vivado releases had a smaller table and some functions implemented through LogiCORE IP (unverified). Main AMD gap for this op set: no explicit `log2` in the documented HLS math list; use `log(x)/log(2)` or custom IP if exact behavior matters. No `sigmoid`.

Intel uses `HLS/math.h` for FPGA versions of supported `math.h` functions. The documented float/double subset includes `sin`, `cos`, `tan`, hyperbolics including `tanh`, `exp`, `exp2`, `exp10`, `log`, `log2`, `log10`, `pow`, `sqrt`, `fmod`, and `fma`; gaps include several rounding/comparison helpers. `HLS/extendedmath.h` adds `sincos`, pi-scaled trig, `pown`, `powr`, `rsqrt`, `mad`, `rootn`, `maxmag`, and `minmag`. `HLS/ac_fixed_math.h` adds fixed `sqrt`, reciprocal, reciprocal sqrt, sin/cos, log, and exp. `HLS/hls_float_math.h` adds `ihc_sqrt`, `ihc_recip`, `ihc_rsqrt`, exp/log/log2/log10/log1p, `ihc_pow`, and trig functions.

## 3. Fixed-point support

Xilinx `ap_fixed<W,I,Q,O,N>` supports overloaded arithmetic, automatic binary-point alignment, and quantization/overflow on assignment or initialization. Rounding modes include `AP_RND`, `AP_RND_ZERO`, `AP_RND_MIN_INF`, `AP_RND_INF`, `AP_RND_CONV` (ties-to-even/unbiased), `AP_TRN`, and `AP_TRN_ZERO`; overflow modes include `AP_SAT`, `AP_SAT_ZERO`, `AP_SAT_SYM`, `AP_WRAP`, and `AP_WRAP_SM`. Vitis fixed-point math functions are limited to documented width ranges and do not honor `Q`, `O`, or `N` during the function calculation, only when assigning the result.

Intel `ac_fixed<N,I,S,Q,O>` has analogous quantization and saturation/wrap modes (`AC_RND_CONV` and `AC_SAT*` names are unverified but standard AC-style). Its fixed math header is much narrower than AMD's fixed math list: no fixed `tan`, `tanh`, or `pow` primitive in the documented set.

## 4. Float support

Vivado/Vitis synthesize `float` and `double` with partial IEEE-754 compliance and infer floating-point IP cores for add, multiply, divide, sqrt, and some math functions; users normally do not instantiate those IPs manually. Vitis `ap_float` is current-tool support, not legacy Vivado (unverified). It uses AMD floating-point IP at RTL generation, has round-to-nearest-even as the only documented rounding mode, no subnormal support, and no automatic conversion from `ap_float` to native `float`. For `ap_float`, basic arithmetic, `sqrt`, `fma`, `abs`, and accumulation are direct; broader transcendentals are not direct (unverified).

Intel `float`/`double` math should include `HLS/math.h` so calls bind to hardware versions. Intel `hls_float` uses `HLS/hls_float.h` for operators and `HLS/hls_float_math.h` for transcendentals; it supports explicit precision/accuracy controls and RNE/RZERO rounding.

## 5. Implications for D-01

Direct HLS equivalents exist for `+`, `-`, `*`, `/`, integer `%`, `fadd`, `fmul`, `fdiv`, `fix2flt`, `flt2fix`, and normal `fltaccum` by `+=`. Header-level direct equivalents exist for `sqrt`, `1/sqrt`/`rsqrt`, `exp`, `ln`/`log`, `sin`, `cos`, `tan`, `tanh`, `pow`, and FMA (`fma`/`mad` or `a*b+c` with binding caveats). `recip` is direct in AMD HLS math and Intel `hls_float_math`; for Intel plain floats, `1/x` is the portable HLS expression. `log2` is direct in Intel math but an AMD gap. `sigmoid` has no native primitive; implement as `1/(1+exp(-x))` or route to a custom/CORDIC/IP path. Thus, most Spatial BigIP ops do not need explicit vendor IP instantiation; explicit IP remains useful only for unsupported ops, exact latency/resource control, or numeric behavior outside HLS-library guarantees.
