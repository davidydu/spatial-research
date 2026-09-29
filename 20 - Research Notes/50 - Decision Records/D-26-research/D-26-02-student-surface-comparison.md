---
type: "research"
decision: "D-26"
angle: "2"
discriminates: surface-embedding
sources:
  - "spatial@e7a8f2f:test/spatial/tests/ee109/Lab1Part2DramSramExample.scala:1-48"
  - "spatial-rs@eb49d8b:crates/spatial-rs-core/testdata/ee109/lab1_part6_reduce.scala:1-43"
  - "spatial-rs@eb49d8b:crates/spatial-rs-core/testdata/ee109/lab2_part6_gemm_fixed_32.scala:1-68"
  - "spatial-rs@eb49d8b:docs/language-spec.md:22-53"
  - "spatial-rs@eb49d8b:docs/language-spec.md:263-348"
  - "spatial-rs@eb49d8b:docs/language-spec.md:852-915"
  - "calyx@d6bcdc8:calyx-py/test/helloworld.py:6-32"
  - "calyx@d6bcdc8:calyx-py/calyx/builder.py:1314-1369"
  - "calyx@d6bcdc8:calyx-py/calyx/builder.py:1588-1598"
  - "allo@094ab41:examples/machsuite/gemm/gemm_blocked.py:12-37"
  - "exo@defe172:examples/cursors/cursors.py:1-44"
  - "exo@defe172:src/exo/API.py:35-49"
  - "pymtl3@c8b349f:pymtl3/datatypes/PythonBits.py:203-262"
verified: ["2026-09-28"]
status: draft
---
## Scope

Compare the concepts needed to express three accelerator kernels, not typing effort, source length, or compiler implementation cost. Inspection date: 2026-09-28. Appendices reproduce the complete Scala originals and supply complete kernel-facing listings for four alternatives. Host data generation, invocation, and assertions are outside the concept count for every surface; Python imports and decorators needed to define a kernel remain inside it. A supplied runner provides input buffers and checks results.

## Findings

### Workload and preservation boundary

[measured] Lab1Part2 multiplies two 16-element tiles of a 32-element input by a scalar, with two SRAMs and sequential outer traversal; Lab1Part6 uses **nested Fold**, despite its filename containing “reduce”; Lab2Part6 traverses K/M/N tiles, loads existing C, and memory-folds products with lane requests 2 and 16. Sources: spatial@e7a8f2f:test/spatial/tests/ee109/Lab1Part2DramSramExample.scala:6-35; spatial-rs@eb49d8b:crates/spatial-rs-core/testdata/ee109/lab1_part6_reduce.scala:15-29; spatial-rs@eb49d8b:crates/spatial-rs-core/testdata/ee109/lab2_part6_gemm_fixed_32.scala:29-58.

[designed] All alternatives preserve those loop orders and both scale buffers; scalar examples retain ordered folds. GEMM receives runtime M/N/K and initially zero C, corresponding to the original harness. Translation uses matching active SRAM slices, explicit tail masking on parallel lanes, and the original product-by-product memfold, rather than silently replacing it with the spec's Tile-K reduction tree. These are kernel designs, not successful compiler runs; the external forms compose the canonical syntax in spatial-rs@eb49d8b:docs/language-spec.md:263-348.

[measured] Canonical `memfold` requires initialized accumulator elements, completely written matching temporary views, and no accumulator access inside its body; `par ... tail` makes partial lane groups explicit. The Scala `.buffer` annotation has no corresponding spelling in the opened canonical grammar, so these ports do not establish schedule/buffering equivalence. Sources: spatial-rs@eb49d8b:docs/language-spec.md:97-147; spatial-rs@eb49d8b:docs/language-spec.md:868-910; spatial-rs@eb49d8b:crates/spatial-rs-core/testdata/ee109/lab2_part6_gemm_fixed_32.scala:43-55.

### Actual precedents versus proposed APIs

[precedent-measured] Calyx uses `prog.component(...)`, `with comp.group(...) as ...`, and a builder object; its expression operators construct guard AST nodes. This supports the *syntax mechanisms* borrowed below, not the proposed high-level `fold`/`memfold` APIs. Sources: calyx@d6bcdc8:calyx-py/test/helloworld.py:6-32; calyx@d6bcdc8:calyx-py/calyx/builder.py:1314-1369; calyx@d6bcdc8:calyx-py/calyx/builder.py:1588-1598.

[precedent-measured] Allo's blocked GEMM uses typed array annotations, ordinary `for ... in range(...)`, `+=`, and `allo.customize`; Exo uses `@proc` and `for ... in seq(...)`, with its decorator extracting and parsing Python AST. These are real AST-style precedents, without evidence here for Spatial bulk-transfer or memfold constructs. Sources: allo@094ab41:examples/machsuite/gemm/gemm_blocked.py:12-37; exo@defe172:examples/cursors/cursors.py:1-44; exo@defe172:src/exo/API.py:35-49.

[precedent-measured] PyMTL's `Bits.__add__` and `Bits.__mul__` compute width-masked values; that implementation is an arithmetic-overloading precedent, **not evidence of symbolic trace capture**. None of these inspections executed a precedent compiler or validated the proposed programs. Source: pymtl3@c8b349f:pymtl3/datatypes/PythonBits.py:203-262.

[designed] The hypothetical tracing API records callbacks once with symbolic indices; `write` records mutation and `return` supplies a fold contribution. Builder scopes record one controller body; `contribute` supplies its value. The AST API parses function bodies, treats `fold`/`memfold` iterators as intrinsics, and routes `contribute` to the innermost scalar fold. No Python body is advertised as ordinary executable numerical Python, and `spatial_trace`, `spatial_builder`, and `spatial_ast` are proposed names, not implemented packages.

### Concept inventory

[judgment] A concept has hardware meaning when changing it can change numeric behavior, storage, transfers, or scheduling. Surface encodings remain separate: reduction addition has meaning; the word `using` does not. Mutable assignment has meaning; its punctuation is another learnable convention. This test charges the external DSL for `let`, `yield`, `using`, and `:=`, rather than treating purpose-built syntax as free. The inventory is a reproducible rubric, not a measured learning curve.

[designed] Marks indicate occurrence across the three listings collectively, not every program. “✓” means present; “—” absent. Hardware rows preserve algorithm obligations; no-hardware rows count distinct syntax or staging ideas once, including familiar Python ideas. Constructors and type notation are grouped identically across surfaces; ordinary literals, identifiers, calls, and arithmetic precedence are assumed prerequisites and excluded uniformly.

| Concept | Hardware meaning? | Scala | External DSL | Python-tracing | Python-builder | Python-AST |
|---|---|---|---|---|---|---|
| [judgment] Accelerator / host boundary and port direction | yes | ✓ | ✓ | ✓ | ✓ | ✓ |
| [judgment] DRAM versus SRAM placement | yes | ✓ | ✓ | ✓ | ✓ | ✓ |
| [judgment] Static tile size versus runtime matrix dimensions | yes | ✓ | ✓ | ✓ | ✓ | ✓ |
| [judgment] Integer / signed fixed-point width and precision | yes | ✓ | ✓ | ✓ | ✓ | ✓ |
| [judgment] Tiling, half-open ranges, and loop step | yes | ✓ | ✓ | ✓ | ✓ | ✓ |
| [judgment] Indexing, rank, and active memory views | yes | ✓ | ✓ | ✓ | ✓ | ✓ |
| [judgment] Bulk load / store direction | yes | ✓ | ✓ | ✓ | ✓ | ✓ |
| [judgment] Sequential versus automatic controller schedule | yes | ✓ | ✓ | ✓ | ✓ | ✓ |
| [judgment] Requested parallel lanes | yes | ✓ | ✓ | ✓ | ✓ | ✓ |
| [judgment] Tail extent / inactive lane treatment | yes | ✓ | ✓ | ✓ | ✓ | ✓ |
| [judgment] Fold identity and accumulator lifetime | yes | ✓ | ✓ | ✓ | ✓ | ✓ |
| [judgment] Reduction addition and multiplication | yes | ✓ | ✓ | ✓ | ✓ | ✓ |
| [judgment] Existing C initialization for memfold | yes | ✓ | ✓ | ✓ | ✓ | ✓ |
| [judgment] Temporary contribution coverage | yes | ✓ | ✓ | ✓ | ✓ | ✓ |
| [judgment] Explicit buffer annotation | yes | ✓ | — | — | — | — |
| [judgment] State write versus local name binding | yes | ✓ | ✓ | ✓ | ✓ | ✓ |
| [judgment] Binding spelling (`val` / `let` / `=`) | no | ✓ | ✓ | ✓ | ✓ | ✓ |
| [judgment] Block punctuation / indentation | no | ✓ | ✓ | ✓ | ✓ | ✓ |
| [judgment] Constructor / type-parameter notation | no | ✓ | ✓ | ✓ | ✓ | ✓ |
| [judgment] State-write spelling (`:=`, `=`, `write`) | no | ✓ | ✓ | ✓ | ✓ | ✓ |
| [judgment] Reducer attachment (last argument / `using`) | no | ✓ | ✓ | ✓ | ✓ | ✓ |
| [judgment] Explicit value handoff (`yield` / `return` / `contribute`) | no | — | ✓ | ✓ | ✓ | ✓ |
| [judgment] Implicit last-expression result | no | ✓ | — | — | — | — |
| [judgment] Higher-order callbacks / captured names | no | ✓ | — | ✓ | — | — |
| [judgment] Anonymous lambda / placeholder syntax | no | ✓ | — | ✓ | — | — |
| [judgment] Curried argument lists | no | ✓ | — | — | — | — |
| [judgment] Import / namespace setup | no | ✓ | — | ✓ | ✓ | ✓ |
| [judgment] Function definition syntax | no | ✓ | — | ✓ | — | ✓ |
| [judgment] Class / inheritance wrapper | no | ✓ | — | — | — | — |
| [judgment] Annotation / decorator entry point | no | ✓ | — | — | — | ✓ |
| [judgment] Capture phase versus execution phase | no | ✓ | — | ✓ | ✓ | ✓ |
| [judgment] Explicit program-builder handle | no | — | — | ✓ | ✓ | — |
| [judgment] Keyword argument syntax | no | — | — | ✓ | ✓ | ✓ |
| [judgment] Context-manager protocol | no | — | — | — | ✓ | — |
| [judgment] Postponed annotation evaluation | no | — | — | — | — | ✓ |
| **[designed] No-hardware concept count** | **no** | **14** | **6** | **13** | **11** | **12** |

[designed] Appendix D reports each lab separately and enumerates absent rows without changing the union rubric.

[judgment] The counts favor the external surface under this particular inventory, while the smaller differences among Python styles do not establish a teaching winner. AST avoids callback and context-manager mechanics here but adds decorator/source-capture rules; tracing makes closures explicit; builder makes recording scopes explicit. Familiarity may reverse the effective learning cost, and different concept grouping can change the numerical gap.

## Implications

### R-X

[judgment] Benefits from the external surface's six counted conventions; Rust is not the cause. I0, I1, I1′, or notebook packaging would not alter the kernel inventory by themselves.

### R-E

[judgment] Inherits the selected Python style's concepts even with a Rust core. I2 bindings cannot by themselves remove capture semantics, decorators, or context managers.

### R-B

[judgment] Can teach the external subset first and offer Python later, but the two syntaxes need equivalent semantics and teaching materials. This note does not estimate that maintenance cost.

### P-X

[judgment] Has the same student kernel inventory as R-X. This evidence does not discriminate the compiler-core language.

### P-E

[judgment] Matching the external count requires an AST-oriented restricted language that removes six counted host conventions: imports, function wrapper, decorator, keyword-argument machinery, source-capture distinction, and postponed annotations from the student-facing contract. A provided template can hide these without actually eliminating them; any replacement notation must be recounted. Conversely, giving the external DSL these six general-purpose conveniences would bring its count to twelve. That arithmetic is not a recommendation to add them.

### P-B

[judgment] Offers the same surface choice as R-B; a Python implementation does not prove its Python syntax costs less to learn. Nothing here chooses I0 over I2 or notebooks.

## Evidence against

[judgment] The strongest counterargument to my external-first leaning is that the six-versus-eleven-or-twelve comparison treats a familiar `def` as another unit equal to unfamiliar `memfold` syntax. That is not a cognitive measurement. Allo and Exo demonstrate concise ordinary loop and annotation syntax in inspected kernels, while the proposed Python APIs have not received an equivalent design-and-user-testing cycle. Source: allo@094ab41:examples/machsuite/gemm/gemm_blocked.py:12-32; exo@defe172:examples/cursors/cursors.py:1-44.

[measured] The external spec itself labels canonical folds/memfolds as Specified, not general implemented support. Comparing its ideal surface against imagined Python wrappers cannot establish availability or diagnostic quality. Source: spatial-rs@eb49d8b:docs/language-spec.md:1099-1107.

## Open questions

[judgment] A student study should separately test explanation of storage and identities, writing unfamiliar kernels, debugging one tail error, and distinguishing capture from execution. Recount after a real minimal Python prototype exists. Resolve `.buffer` equivalence and fixed-point operation order before numerical or schedule equivalence claims; neither was executed here.

## Confidence

medium — Strong source-level workload and syntax evidence; constructed alternatives, subjective concept granularity, no student observations, and no execution-parity evidence.

## Appendix A — Lab1Part2 dense DRAM/SRAM tiling

### Scala original

[measured] Verbatim source: spatial@e7a8f2f:test/spatial/tests/ee109/Lab1Part2DramSramExample.scala:1-48.

```scala
package spatial.tests.ee109

import spatial.dsl._

@spatial class Lab1Part2DramSramExample extends SpatialTest {
  val N = 32
  type T = Int

  override def runtimeArgs = "3"

  def simpleLoadStore(srcHost: Array[T], value: T) = {
    val tileSize = 16

    val srcFPGA = DRAM[T](N)
    val dstFPGA = DRAM[T](N)
    setMem(srcFPGA, srcHost)

    val x = ArgIn[T]
    setArg(x, value)

    Accel {
      Sequential.Foreach(N by tileSize) { i =>
        val b1 = SRAM[T](tileSize)
        b1 load srcFPGA(i::i + tileSize)

        val b2 = SRAM[T](tileSize)
        Foreach(tileSize by 1) { ii =>
          b2(ii) = b1(ii) * x
        }

        dstFPGA(i::i + tileSize) store b2
      }
    }

    getMem(dstFPGA)
  }

  def main(args: Array[String]): Unit = {
    val value = args(0).to[T]
    val src = Array.tabulate[T](N) { i => i % 256 }
    val dst = simpleLoadStore(src, value)
    val gold = src.map { _ * value }
    val pass = dst.zip(gold) { _ == _ }.reduce { _ && _ }

    println("PASS: " + pass + " (Lab1Part2DramSramExample)")
    assert(pass == 1)
  }
}
```

### External DSL

[designed] Two-buffer adaptation of canonical Scale; no added parallelism. Source: spatial-rs@eb49d8b:docs/language-spec.md:35-53.

```spatial
kernel Lab1Part2 {
  const N: Size = 32;
  const TILE: Size = 16;
  inputs { src: Dram<Int>[N], scale: Int }
  outputs { dst: Dram<Int>[N] }
  accel {
    seq foreach base in 0..N step TILE {
      let b1 = Sram<Int>[TILE];
      let b2 = Sram<Int>[TILE];
      load b1 <- src[base..base + TILE];
      foreach ii in 0..TILE {
        b2[ii] := b1[ii] * scale;
      }
      store dst[base..base + TILE] <- b2;
    }
  }
}
```

### Python tracing

[designed] All APIs are proposed; overloaded indexed arithmetic and symbolic callbacks must be implemented. Arithmetic operator precedent alone: pymtl3@c8b349f:pymtl3/datatypes/PythonBits.py:203-262.

```python
from spatial_trace import Kernel, Dram, Int

k = Kernel("Lab1Part2")
src = k.input("src", Dram(Int, 32))
scale = k.input("scale", Int)
dst = k.output("dst", Dram(Int, 32))

def tile_body(base):
    b1 = k.sram(Int, 16)
    b2 = k.sram(Int, 16)
    k.load(b1, src[base:base + 16])
    k.foreach(0, 16, body=lambda ii: b2.write(ii, b1[ii] * scale))
    k.store(dst[base:base + 16], b2)

k.accel(lambda: k.foreach(0, 32, step=16, schedule="seq", body=tile_body))
```

### Python builder

[designed] High-level controller and memory API.

[precedent-measured] `Builder`, `.component`, and `with ... as ...` structure borrow Calyx syntax, not its lower-level group semantics: calyx@d6bcdc8:calyx-py/test/helloworld.py:6-32.

```python
from spatial_builder import Builder, Dram, Int

prog = Builder()
k = prog.component("Lab1Part2")
src = k.input("src", Dram(Int, 32))
scale = k.input("scale", Int)
dst = k.output("dst", Dram(Int, 32))
with k.accel():
    with k.foreach(0, 32, step=16, schedule="seq") as base:
        b1 = k.sram(Int, 16)
        b2 = k.sram(Int, 16)
        k.load(b1, src[base:base + 16])
        with k.foreach(0, 16) as ii:
            b2[ii] = b1[ii] * scale
        k.store(dst[base:base + 16], b2)
```

### Python AST

[designed] Function body is the accelerator; uninitialized typed SRAM declarations allocate storage.

[precedent-measured] `@proc`, typed parameters, and `for ... in seq(...)` are Exo precedents: exo@defe172:examples/cursors/cursors.py:1-44. Step keywords, ports, and memories here are designed extensions.

```python
from __future__ import annotations
from spatial_ast import proc, In, Out, Dram, Sram, Int, seq, auto, load, store

@proc
def lab1part2(src: In[Dram[Int, 32]], scale: In[Int], dst: Out[Dram[Int, 32]]):
    for base in seq(0, 32, step=16):
        b1: Sram[Int, 16]
        b2: Sram[Int, 16]
        load(b1, src[base:base + 16])
        for ii in auto(0, 16):
            b2[ii] = b1[ii] * scale
        store(dst[base:base + 16], b2)
```

## Appendix B — Lab1Part6 scalar reduction

### Scala original

[measured] Verbatim source: spatial-rs@eb49d8b:crates/spatial-rs-core/testdata/ee109/lab1_part6_reduce.scala:1-43.

```scala
import spatial.dsl._

@spatial class Lab1Part6ReduceExample extends SpatialTest {
    val N = 32
    val tileSize = 16
    type T = Int

    def main(args: Array[String]): Unit = {
        val arraySize = N
        val srcFPGA = DRAM[T](N)
        val src = Array.tabulate[Int](arraySize) { i => i % 256 }
        setMem(srcFPGA, src)
        val destArg = ArgOut[T]

        Accel {
            // First Fold Controller
            val accum = Reg[T](0)
            Sequential.Fold(accum)(N by tileSize) { i =>
                val b1 = SRAM[T](tileSize)
                b1 load srcFPGA(i::i+tileSize)
                // Second Fold Controller. In Scala / Spatial, the last element
                // of a function will be automatically returned (if your function
                // should return anything). Therefore you don't need to write a
                // return at this line explicitly.
                Fold(0)(tileSize by 1) { ii => b1(ii) }{_+_}
            }{_+_}


            destArg := accum.value
        }

        val result = getArg(destArg)
        val gold = src.reduce{_+_}
        println("Gold: " + gold)
        println("Result: : " + result)
        println("")

        val cksum = gold == result
        println("PASS: " + cksum)

        assert(cksum == 1)
    }
}
```

### External DSL

[designed] Complete wrapper around canonical tiled-fold syntax, retaining Fold for the inner controller instead of introducing reassociation. Source: spatial-rs@eb49d8b:docs/language-spec.md:263-281.

```spatial
kernel Lab1Part6 {
  const N: Size = 32;
  const TILE: Size = 16;
  inputs { src: Dram<Int>[N] }
  outputs { result: Int }
  accel {
    let sum = fold base in 0..N step TILE init 0 using + {
      let tile = Sram<Int>[TILE];
      load tile <- src[base..base + TILE];
      let tile_sum = fold ii in 0..TILE init 0 using + {
        yield tile[ii];
      };
      yield tile_sum;
    };
    result := sum;
  }
}
```

### Python tracing

[designed] A callback return is one symbolic contribution; Python does not execute all hardware iterations. No inspected precedent establishes this fold API.

```python
from spatial_trace import Kernel, Dram, Int

k = Kernel("Lab1Part6")
src = k.input("src", Dram(Int, 32))
result = k.output("result", Int)

def tile_sum(base):
    tile = k.sram(Int, 16)
    k.load(tile, src[base:base + 16])
    return k.fold(0, 16, init=0, using="+", body=lambda ii: tile[ii])

def accelerator():
    total = k.fold(0, 32, step=16, init=0, using="+", body=tile_sum)
    result.write(total)

k.accel(accelerator)
```

### Python builder

[designed] Fold handles expose an index inside their scope and the completed value outside it.

[precedent-measured] Context-scoped recording has a Calyx precedent; scalar fold handles do not: calyx@d6bcdc8:calyx-py/calyx/builder.py:1588-1598.

```python
from spatial_builder import Builder, Dram, Int

prog = Builder()
k = prog.component("Lab1Part6")
src = k.input("src", Dram(Int, 32))
result = k.output("result", Int)
with k.accel():
    with k.fold(0, 32, step=16, init=0, using="+") as outer:
        base = outer.index
        tile = k.sram(Int, 16)
        k.load(tile, src[base:base + 16])
        with k.fold(0, 16, init=0, using="+") as inner:
            inner.contribute(tile[inner.index])
        outer.contribute(inner.value)
    result.write(outer.value)
```

### Python AST

[designed] AST fold takes an initialized typed accumulator and writes its final value; `contribute` is a parser intrinsic, not Python generator `yield`.

[precedent-measured] AST extraction by a `@proc` entry point exists in Exo: exo@defe172:src/exo/API.py:35-49; these fold extensions do not claim Exo compatibility.

```python
from __future__ import annotations
from spatial_ast import proc, In, Out, Dram, Sram, Int, fold, contribute, load

@proc
def lab1part6(src: In[Dram[Int, 32]], result: Out[Int]):
    total: Int = 0
    for base in fold(total, 0, 32, step=16, using="+"):
        tile: Sram[Int, 16]
        load(tile, src[base:base + 16])
        tile_sum: Int = 0
        for ii in fold(tile_sum, 0, 16, using="+"):
            contribute(tile[ii])
        contribute(tile_sum)
    result = total
```

## Appendix C — Lab2Part6 tiled fixed-point GEMM with memfold

### Scala original

[measured] Verbatim source; the default harness dimensions are 32 × 32 × 32: spatial-rs@eb49d8b:crates/spatial-rs-core/testdata/ee109/lab2_part6_gemm_fixed_32.scala:1-68.

```scala
import spatial.dsl._

@spatial class Lab2Part6GEMM extends SpatialTest {

  override def runtimeArgs = "32 32 32"

  def main(args: Array[String]): Unit = {

    type T = FixPt[TRUE,_24,_8]

    val M = ArgIn[Int]
    val N = ArgIn[Int]
    val K = ArgIn[Int]
    setArg(M,args(0).to[Int])
    setArg(N,args(1).to[Int])
    setArg(K,args(2).to[Int])

    val a_data = (0::args(0).to[Int], 0::args(2).to[Int]){(i,j) => random[T](3)}
    val b_data = (0::args(2).to[Int], 0::args(1).to[Int]){(i,j) => random[T](3)}
    val c_init = (0::args(0).to[Int], 0::args(1).to[Int]){(i,j) => 0.to[T]}
    val a = DRAM[T](M, K)
    val b = DRAM[T](K, N)
    val c = DRAM[T](M, N)

    setMem(a, a_data)
    setMem(b, b_data)
    setMem(c, c_init)

    val tileM = 16
    val tileN = 16
    val tileK = 16

    Accel {
        Foreach(K by tileK){kk =>
            val numel_k = min(tileK.to[Int], K - kk)
            Foreach(M by tileM){mm =>
                val numel_m = min(tileM.to[Int], M - mm)
                val tileA_sram = SRAM[T](tileM, tileK)
                tileA_sram load a(mm::mm+numel_m, kk::kk+numel_k)
                Foreach(N by tileN){nn =>
                    val numel_n = min(tileN.to[Int], N - nn)
                    val tileB_sram = SRAM[T](tileK, tileN)
                    val tileC_sram = SRAM[T](tileM, tileN).buffer
                    tileB_sram load b(kk::kk+numel_k, nn::nn+numel_n)
                    tileC_sram load c(mm::mm+numel_m, nn::nn+numel_n)
                    MemFold(tileC_sram)(numel_k by 1) { k_idx =>
                      val partial_c = SRAM[T](tileM, tileN)
                      Foreach(numel_m by 1 par 2) { ii =>
                        Foreach(numel_n by 1 par 16) { jj =>
                          partial_c(ii, jj) = tileA_sram(ii, k_idx) * tileB_sram(k_idx, jj)
                        }
                      }
                      partial_c
                    }{ _+_ }
                    c(mm::mm+numel_m, nn::nn+numel_n) store tileC_sram
                }
            }
        }
    }

    val accel_matrix = getMatrix(c)
    val gold_matrix = (0::args(0).to[Int], 0::args(1).to[Int]){(i,j) =>
      Array.tabulate(args(2).to[Int]){k => a_data(i,k) * b_data(k,j)}.reduce{_+_}
    }
    val cksum = accel_matrix.zip(gold_matrix){_==_}.reduce{_&&_}
    assert (cksum == 1)
  }
}
```

### External DSL

[designed] Expanded canonical composition, preserving original kk/mm/nn ordering; C is initialized before invocation. Active views follow spatial-rs@eb49d8b:docs/language-spec.md:303-348 and spatial-rs@eb49d8b:docs/language-spec.md:886-903. No `.buffer` equivalent is asserted.

```spatial
kernel Lab2Part6 {
  const TILE: Size = 16;
  inputs {
    M: Int, N: Int, K: Int,
    a: Dram<FixPt<Signed,24,8>>[M,K],
    b: Dram<FixPt<Signed,24,8>>[K,N]
  }
  inouts { c: Dram<FixPt<Signed,24,8>>[M,N] }
  accel {
    foreach kk in 0..K step TILE {
      let depth = min(TILE, K - kk);
      foreach mm in 0..M step TILE {
        let rows = min(TILE, M - mm);
        let at = Sram<FixPt<Signed,24,8>>[TILE,TILE];
        load at[0..rows,0..depth] <- a[mm..mm + rows,kk..kk + depth];
        foreach nn in 0..N step TILE {
          let cols = min(TILE, N - nn);
          let bt = Sram<FixPt<Signed,24,8>>[TILE,TILE];
          let ct = Sram<FixPt<Signed,24,8>>[TILE,TILE];
          let partial = Sram<FixPt<Signed,24,8>>[TILE,TILE];
          load bt[0..depth,0..cols] <- b[kk..kk + depth,nn..nn + cols];
          load ct[0..rows,0..cols] <- c[mm..mm + rows,nn..nn + cols];
          memfold ct[0..rows,0..cols] with partial[0..rows,0..cols]
              over ki in 0..depth using + {
            foreach ii in 0..rows par 2 tail {
              foreach jj in 0..cols par 16 tail {
                partial[ii,jj] := at[ii,ki] * bt[ki,jj];
              }
            }
          }
          store c[mm..mm + rows,nn..nn + cols] <- ct[0..rows,0..cols];
        }
      }
    }
  }
}
```

### Python tracing

[designed] Symbolic minimum, slices, shape values, and callbacks record the canonical operations; no numerical tracing is claimed. C must be initialized before invocation.

```python
from spatial_trace import Kernel, Dram, Int, FixPt, Signed

k = Kernel("Lab2Part6")
T = FixPt(Signed, 24, 8)
M = k.input("M", Int)
N = k.input("N", Int)
K = k.input("K", Int)
a = k.input("a", Dram(T, M, K))
b = k.input("b", Dram(T, K, N))
c = k.inout("c", Dram(T, M, N))

def k_tile(kk):
    depth = k.min(16, K - kk)
    def m_tile(mm):
        rows = k.min(16, M - mm)
        at = k.sram(T, 16, 16)
        k.load(at[0:rows, 0:depth], a[mm:mm + rows, kk:kk + depth])
        def n_tile(nn):
            cols = k.min(16, N - nn)
            bt = k.sram(T, 16, 16)
            ct = k.sram(T, 16, 16)
            partial = k.sram(T, 16, 16)
            k.load(bt[0:depth, 0:cols], b[kk:kk + depth, nn:nn + cols])
            k.load(ct[0:rows, 0:cols], c[mm:mm + rows, nn:nn + cols])
            def product(ki):
                def row(ii):
                    k.foreach(0, cols, par=16, tail=True,
                              body=lambda jj: partial.write((ii, jj), at[ii, ki] * bt[ki, jj]))
                k.foreach(0, rows, par=2, tail=True, body=row)
            k.memfold(ct[0:rows, 0:cols], partial[0:rows, 0:cols],
                      0, depth, using="+", body=product)
            k.store(c[mm:mm + rows, nn:nn + cols], ct[0:rows, 0:cols])
        k.foreach(0, N, step=16, body=n_tile)
    k.foreach(0, M, step=16, body=m_tile)

k.accel(lambda: k.foreach(0, K, step=16, body=k_tile))
```

### Python builder

[designed] Context scopes record hardware controllers; their bodies run once during construction. C must be initialized before invocation.

[precedent-measured] Calyx provides context-scoped assignment recording, not this GEMM abstraction: calyx@d6bcdc8:calyx-py/calyx/builder.py:1588-1598.

```python
from spatial_builder import Builder, Dram, Int, FixPt, Signed

prog = Builder()
k = prog.component("Lab2Part6")
T = FixPt(Signed, 24, 8)
M = k.input("M", Int)
N = k.input("N", Int)
K = k.input("K", Int)
a = k.input("a", Dram(T, M, K))
b = k.input("b", Dram(T, K, N))
c = k.inout("c", Dram(T, M, N))
with k.accel():
    with k.foreach(0, K, step=16) as kk:
        depth = k.min(16, K - kk)
        with k.foreach(0, M, step=16) as mm:
            rows = k.min(16, M - mm)
            at = k.sram(T, 16, 16)
            k.load(at[0:rows, 0:depth], a[mm:mm + rows, kk:kk + depth])
            with k.foreach(0, N, step=16) as nn:
                cols = k.min(16, N - nn)
                bt = k.sram(T, 16, 16)
                ct = k.sram(T, 16, 16)
                partial = k.sram(T, 16, 16)
                k.load(bt[0:depth, 0:cols], b[kk:kk + depth, nn:nn + cols])
                k.load(ct[0:rows, 0:cols], c[mm:mm + rows, nn:nn + cols])
                with k.memfold(ct[0:rows, 0:cols], partial[0:rows, 0:cols],
                               0, depth, using="+") as ki:
                    with k.foreach(0, rows, par=2, tail=True) as ii:
                        with k.foreach(0, cols, par=16, tail=True) as jj:
                            partial[ii, jj] = at[ii, ki] * bt[ki, jj]
                k.store(c[mm:mm + rows, nn:nn + cols], ct[0:rows, 0:cols])
```

### Python AST

[designed] Postponed annotations let the AST parser resolve dependent dimensions without Python evaluating parameter names during function definition. Memfold and parallel-tail iterators are designed intrinsics, and C is preinitialized.

[precedent-measured] Typed matrix parameters, nested loop blocks, and indexed products have an Allo precedent: allo@094ab41:examples/machsuite/gemm/gemm_blocked.py:12-32. The port, SRAM, fixed-point spelling, and memfold constructs above are not claimed as Allo syntax.

```python
from __future__ import annotations
from spatial_ast import proc, In, InOut, Dram, Sram, Int, FixPt, Signed
from spatial_ast import auto, memfold, load, store, minimum

@proc
def lab2part6(M: In[Int], N: In[Int], K: In[Int],
              a: In[Dram[FixPt[Signed, 24, 8], M, K]],
              b: In[Dram[FixPt[Signed, 24, 8], K, N]],
              c: InOut[Dram[FixPt[Signed, 24, 8], M, N]]):
    for kk in auto(0, K, step=16):
        depth = minimum(16, K - kk)
        for mm in auto(0, M, step=16):
            rows = minimum(16, M - mm)
            at: Sram[FixPt[Signed, 24, 8], 16, 16]
            load(at[0:rows, 0:depth], a[mm:mm + rows, kk:kk + depth])
            for nn in auto(0, N, step=16):
                cols = minimum(16, N - nn)
                bt: Sram[FixPt[Signed, 24, 8], 16, 16]
                ct: Sram[FixPt[Signed, 24, 8], 16, 16]
                partial: Sram[FixPt[Signed, 24, 8], 16, 16]
                load(bt[0:depth, 0:cols], b[kk:kk + depth, nn:nn + cols])
                load(ct[0:rows, 0:cols], c[mm:mm + rows, nn:nn + cols])
                for ki in memfold(ct[0:rows, 0:cols], partial[0:rows, 0:cols],
                                  0, depth, using="+"):
                    for ii in auto(0, rows, par=2, tail=True):
                        for jj in auto(0, cols, par=16, tail=True):
                            partial[ii, jj] = at[ii, ki] * bt[ki, jj]
                store(c[mm:mm + rows, nn:nn + cols], ct[0:rows, 0:cols])
```

## Appendix D — Per-lab concept counts and absence audit

[designed] These are static counts of the written examples under the unchanged nineteen-row no-hardware inventory, not runtime measurements or student learning results. Each cell below reports **count; additional absent rows**, beyond its surface's always-absent rows in the next table. “None” means the lab uses that surface's complete union inventory.

| Lab | Scala | External DSL | Python-tracing | Python-builder | Python-AST |
|---|---|---|---|---|---|
| [designed] Lab1Part2 | **12**; N5, N7 | **4**; N5, N6 | **11**; N5, N6 | **9**; N5, N6 | **10**; N5, N6 |
| [designed] Lab1Part6 | **14**; none | **6**; none | **13**; none | **11**; none | **12**; none |
| [designed] Lab2Part6 | **14**; none | **5**; N6 | **12**; N6 | **10**; N6 | **11**; N6 |

[designed] For every lab/style, the complete absent set is the union of the following always-absent set and that cell's additional absent set. The count equals nineteen minus the size of that complete set; equivalently, subtract additional absences from the surface's original union count.

| Surface | Original union count | Always-absent no-hardware rows |
|---|---|---|
| [designed] Scala | 14 | N6, N16, N17, N18, N19 |
| [designed] External DSL | 6 | N7, N8, N9, N10, N11, N12, N13, N14, N15, N16, N17, N18, N19 |
| [designed] Python-tracing | 13 | N7, N10, N13, N14, N18, N19 |
| [designed] Python-builder | 11 | N7, N8, N9, N10, N12, N13, N14, N19 |
| [designed] Python-AST | 12 | N7, N8, N9, N10, N13, N16, N18 |

[designed] IDs follow exactly the existing no-hardware rows' order; abbreviated names below introduce no new grouping.

| ID | Existing concept row |
|---|---|
| N1 | Binding spelling |
| N2 | Block punctuation / indentation |
| N3 | Constructor / type-parameter notation |
| N4 | State-write spelling |
| N5 | Reducer attachment |
| N6 | Explicit value handoff |
| N7 | Implicit last-expression result |
| N8 | Higher-order callbacks / captured names |
| N9 | Anonymous lambda / placeholder syntax |
| N10 | Curried argument lists |
| N11 | Import / namespace setup |
| N12 | Function definition syntax |
| N13 | Class / inheritance wrapper |
| N14 | Annotation / decorator entry point |
| N15 | Capture phase versus execution phase |
| N16 | Explicit program-builder handle |
| N17 | Keyword argument syntax |
| N18 | Context-manager protocol |
| N19 | Postponed annotation evaluation |

[designed] Lab1Part2 has no accelerator reduction, so reducer attachment is absent everywhere. Its Scala controller callbacks have no value-producing result; the host-side `getMem` return and verification reduction are excluded consistently with Scope. Scala curried controller calls remain present. The other surfaces need no `yield`, `return`, or `contribute` in this accelerator.

[designed] Lab1Part6 uses scalar contribution handoff in all four alternatives and implicit last-expression results in Scala. Lab2Part6 contributes through temporary memory writes; those count as N4, not an additional N6 handoff. The original Scala memfold does return `partial_c` as its last expression, so N7 remains present there. Python AST postponed annotations are counted in all three supplied listings because each includes that declaration; these counts do not assume students have already learned it in an earlier lab.
