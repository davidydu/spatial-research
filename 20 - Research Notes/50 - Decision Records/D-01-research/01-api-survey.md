---
type: "research"
decision: "D-01"
angle: 1
---

## Method Inventory

| Method signature | Class | Semantics |
|---|---|---|
| `def getConst[T<:Data](sig: T): Option[BigInt]` | concrete-with-default | Extracts literal `UInt`/`SInt` values, otherwise `None` (BigIP.scala:9-13). |
| `def divide(dividend: UInt, divisor: UInt, latency: Int, flow: Bool, myName: String): UInt` | abstract | Unsigned division IP hook (BigIP.scala:15-15). |
| `def divide(dividend: SInt, divisor: SInt, latency: Int, flow: Bool, myName: String): SInt` | abstract | Signed division IP hook (BigIP.scala:16-16). |
| `def mod(dividend: UInt, divisor: UInt, latency: Int, flow: Bool, myName: String): UInt` | abstract | Unsigned modulo IP hook (BigIP.scala:17-17). |
| `def mod(dividend: SInt, divisor: SInt, latency: Int, flow: Bool, myName: String): SInt` | abstract | Signed modulo IP hook (BigIP.scala:18-18). |
| `def multiply(a: UInt, b: UInt, latency: Int, flow: Bool, myName: String): UInt` | abstract | Unsigned multiplication IP hook (BigIP.scala:19-19). |
| `def multiply(a: SInt, b: SInt, latency: Int, flow: Bool, myName: String): SInt` | abstract | Signed multiplication IP hook (BigIP.scala:20-20). |
| `def sqrt(a: UInt, latency: Int, flow: Bool, myName: String): UInt` | concrete-with-default | Integer square root; default throws `Unimplemented("sqrt")` (BigIP.scala:22-23). |
| `def sin(a: UInt, latency: Int, myName: String): UInt` | concrete-with-default | Sine; default throws `Unimplemented("sin")` (BigIP.scala:25-25). |
| `def cos(a: UInt, latency: Int, myName: String): UInt` | concrete-with-default | Cosine; default throws `Unimplemented("cos")` (BigIP.scala:26-26). |
| `def atan(a: UInt, latency: Int, myName: String): UInt` | concrete-with-default | Arctangent; default throws `Unimplemented("ata")` (BigIP.scala:27-27). |
| `def sinh(a: UInt, latency: Int, myName: String): UInt` | concrete-with-default | Hyperbolic sine; default throws `Unimplemented("sin")` (BigIP.scala:28-28). |
| `def cosh(a: UInt, latency: Int, myName: String): UInt` | concrete-with-default | Hyperbolic cosine; default throws `Unimplemented("cos")` (BigIP.scala:29-29). |
| `def log2(a: UInt, latency: Int, flow: Bool, myName: String): UInt` | concrete-with-default | Base-2 logarithm; default throws `Unimplemented("log2")` (BigIP.scala:31-31). |
| `def fadd(a: UInt, b: UInt, m: Int, e: Int, latency: Int, flow: Bool, myName: String): UInt` | abstract | Floating-point addition (BigIP.scala:33-34). |
| `def fsub(a: UInt, b: UInt, m: Int, e: Int, latency: Int, flow: Bool, myName: String): UInt` | abstract | Floating-point subtraction (BigIP.scala:36-37). |
| `def fmul(a: UInt, b: UInt, m: Int, e: Int, latency: Int, flow: Bool, myName: String): UInt` | abstract | Floating-point multiplication (BigIP.scala:39-40). |
| `def fdiv(a: UInt, b: UInt, m: Int, e: Int, latency: Int, flow: Bool, myName: String): UInt` | abstract | Floating-point division (BigIP.scala:42-43). |
| `def flt(a: UInt, b: UInt, m: Int, e: Int, latency: Int, flow: Bool, myName: String): Bool` | abstract | Floating less-than comparison (BigIP.scala:45-46). |
| `def fgt(a: UInt, b: UInt, m: Int, e: Int, latency: Int, flow: Bool, myName: String): Bool` | abstract | Floating greater-than comparison (BigIP.scala:48-49). |
| `def fge(a: UInt, b: UInt, m: Int, e: Int, latency: Int, flow: Bool, myName: String): Bool` | abstract | Floating greater-or-equal comparison (BigIP.scala:51-52). |
| `def fle(a: UInt, b: UInt, m: Int, e: Int, latency: Int, flow: Bool, myName: String): Bool` | abstract | Floating less-or-equal comparison (BigIP.scala:54-55). |
| `def fne(a: UInt, b: UInt, m: Int, e: Int, latency: Int, flow: Bool, myName: String): Bool` | abstract | Floating inequality comparison (BigIP.scala:57-58). |
| `def feq(a: UInt, b: UInt, m: Int, e: Int, latency: Int, flow: Bool, myName: String): Bool` | abstract | Floating equality comparison (BigIP.scala:60-61). |
| `def fabs(a: UInt, m: Int, e: Int, latency: Int, flow: Bool, myName: String): UInt` | concrete-with-default | Floating absolute value; default throws (BigIP.scala:63-64). |
| `def fexp(a: UInt, m: Int, e: Int, latency: Int, flow: Bool, myName: String): UInt` | concrete-with-default | Floating natural exponentiation; default throws (BigIP.scala:66-67). |
| `def ftanh(a: UInt, m: Int, e: Int, latency: Int, flow: Bool, myName: String): UInt` | concrete-with-default | Floating hyperbolic tangent; default throws (BigIP.scala:69-70). |
| `def fsigmoid(a: UInt, m: Int, e: Int, latency: Int, flow: Bool, myName: String): UInt` | concrete-with-default | Floating sigmoid; default throws (BigIP.scala:72-73). |
| `def fln(a: UInt, m: Int, e: Int, latency: Int, flow: Bool, myName: String): UInt` | concrete-with-default | Floating natural log; default throws (BigIP.scala:75-76). |
| `def frec(a: UInt, m: Int, e: Int, latency: Int, flow: Bool, myName: String): UInt` | concrete-with-default | Floating reciprocal; default throws (BigIP.scala:78-79). |
| `def fsqrt(a: UInt, m: Int, e: Int, latency: Int, flow: Bool, myName: String): UInt` | concrete-with-default | Floating square root; default throws (BigIP.scala:81-83). |
| `def frsqrt(a: UInt, m: Int, e: Int, latency: Int, flow: Bool, myName: String): UInt` | concrete-with-default | Floating reciprocal square root; default throws (BigIP.scala:85-86). |
| `def ffma(a: UInt, b: UInt, c: UInt, m: Int, e: Int, latency: Int, flow: Bool, myName: String): UInt` | concrete-with-default | Floating fused multiply-add; default throws (BigIP.scala:88-89). |
| `def fix2flt(a: UInt, sign: Boolean, dec: Int, frac: Int, man: Int, exp: Int, latency: Int, flow: Bool, myName: String): UInt` | concrete-with-default | Fixed-to-float conversion; default throws (BigIP.scala:91-92). |
| `def fix2fix(a: UInt, sign1: Boolean, dec1: Int, frac1: Int, sign2: Boolean, dec2: Int, frac2: Int, latency: Int, flow: Bool, rounding: RoundingMode, saturating: OverflowMode, myName: String): UInt` | concrete-with-default | Fixed-to-fixed conversion; default throws (BigIP.scala:94-95). |
| `def flt2fix(a: UInt, man: Int, exp: Int, sign: Boolean, dec: Int, frac: Int, latency: Int, flow: Bool, rounding: RoundingMode, saturating: OverflowMode, myName: String): UInt` | concrete-with-default | Float-to-fixed conversion; default throws (BigIP.scala:97-98). |
| `def flt2flt(a: UInt, man1: Int, exp1: Int, man2: Int, exp2: Int, latency: Int, flow: Bool, myName: String): UInt` | concrete-with-default | Float-to-float conversion; default throws (BigIP.scala:100-101). |
| `def fltaccum(a: UInt, en: Bool, last: Bool, m: Int, e: Int, latency: Int, flow: Bool, myName: String): UInt` | concrete-with-default | Floating accumulation; default throws (BigIP.scala:103-104). |

No method is classified as always-overridden from this file alone; there are no subclasses or override sites in BigIP.scala.

## Abstract Surface

Counts: 38 methods total; 16 abstract methods with no default implementation; 22 concrete methods with defaults; 0 always-overridden methods evidenced in this file.

Every concrete target subclass must implement these no-body methods: `divide(UInt)`, `divide(SInt)`, `mod(UInt)`, `mod(SInt)`, `multiply(UInt)`, `multiply(SInt)` (BigIP.scala:15-20), plus `fadd`, `fsub`, `fmul`, `fdiv`, `flt`, `fgt`, `fge`, `fle`, `fne`, and `feq` (BigIP.scala:33-61). Defaults exist for `getConst` (BigIP.scala:9-13), integer/transcendental helpers `sqrt`, `sin`, `cos`, `atan`, `sinh`, `cosh`, `log2` (BigIP.scala:22-31), and the remaining floating/conversion hooks `fabs`, `fexp`, `ftanh`, `fsigmoid`, `fln`, `frec`, `fsqrt`, `frsqrt`, `ffma`, `fix2flt`, `fix2fix`, `flt2fix`, `flt2flt`, `fltaccum` (BigIP.scala:63-104).

## Coverage Gap

If a target subclass omits one of the 16 abstract overrides, the gap is a Scala type/compile-time issue for any concrete subclass: these declarations have no method body in the abstract base (BigIP.scala:15-20, BigIP.scala:33-61). The file provides no runtime stub, no empty wire, and no fallback expression for those methods. By contrast, omitted overrides for the concrete optional hooks compile against the base default; except for `getConst`, those defaults throw `Unimplemented(op)`, whose message is defined by the local exception case class as `"$op is not implemented for the given target."` (BigIP.scala:7-13, BigIP.scala:22-104).

## Implications for D-01

BigIP.scala already distinguishes mandatory lowering surface from optional arithmetic/IP surface: core integer division/mod/multiply and basic floating arithmetic/comparisons are abstract, while more specialized arithmetic defaults to explicit `Unimplemented` exceptions. For the Rust+HLS port, this supports rejecting missing mandatory ops at compile/interface time, while representing optional ops as explicit unsupported placeholders unless a target elects to lower them to vendor IP.
