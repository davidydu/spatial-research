---
type: implementation-blueprint
title: "Python library implementation and migration recipes"
project: spatial-python
date: 2026-10-01
status: reviewed
adoption_status: proposed
implementation_status: not-implemented
---

## Why this needs its own design

F13 in [[PY-R005 - Full Language Coverage and Migration]] accounts for library files, but file accounting alone does not tell a contributor how to implement their exported operations. Source review found additional concrete families inside those files: pooling, convolution, batch normalization, backward training updates and SVM helpers. This blueprint makes their implementation and deliberate migration choices explicit. It is proposed under [[D-28]], not a literal compatibility promise or a claim of executed Python kernels.

All accelerator library functions are typed declarative source templates under `spatial.lib.*`. They expand through the same checker and core operations as user programs. There is no `is_gemm_application` compiler path. A closed `DefinitionRef` supplies a typed accessor, mapper, predicate, comparator or activation where needed; its capabilities/effects are checked, not assumed from its name. HostML functions become ordinary host helpers, with independent oracle implementations kept separate from production numeric functions.

## Common template rules

Shapes, broadcast axes, transposition, numeric/accumulator formats, reduction policy and mutation/alias rules are explicit parameters. Every arithmetic operator normalizes at its declared type; formulas below specify operator order, not an unrounded real-number shortcut. A nonassociative sum defaults to an ordered fold from typed zero. A lawful or fixed-tree profile is an explicit alternative in semantic identity. Tile and lane choices cannot change this arithmetic policy or contribution effects. A structural sample/window/batch count used as a numeric divisor must be exactly representable in the declared division type: use checked Index embedding and an explicit cast with an exactness check. Otherwise select a wider division type and explicit sum/output casts. This applies to pooling, means, variances and training; an Int8 count of 200 cannot become -56. Empty sums produce typed zero; impossible shapes and invalid divisors diagnose before output writes when they are invocation preconditions.

Array/matrix/tensor operands use logical views, which express increments and leading dimensions rather than retaining unused integer arguments. Loop order is lexicographic over output indices, followed by increasing reduction indices. An in-place operation snapshots every selected input value whose later read could be overwritten; the conservative baseline snapshots the full selected inputs before any output write. Later tiled algorithms must prove equivalent dependence and fault behavior. Overlapping inputs retain shared backing identity. Reject an unsupported alias plan rather than silently assume disjoint buffers.

Template outputs are ordinary declared writes with the standard no-rollback contract. A library may explicitly compute into private scratch then publish, but that is part of its recipe and resource plan, not a universal transaction guarantee. Read-only callbacks may still fault; a declared total-pure callback cannot have a possible language fault. Effectful mapping callbacks execute in the declared contribution order exactly once; they cannot be cached or regrouped as if pure. Tensor-specific routines below require read-only input accessors and state-free activation/comparator helpers; arbitrary effectful computations remain expressible through the general ordered map/fold primitives.

## Pinned callable inventory

This inventory names public source definitions in all nine `src/spatial/lib/` files and the additional `src/spatial/math/LinearAlgebra.scala` evidence file. Nested/private implementation helpers are assigned to their public owner. Commented-out definitions are evidence, not exported capabilities. Source pin: `spatial@e7a8f2f7f776dd0c5ac7fc03f16b3ed4d97021f0`.

| Original file and public definitions | Proposed destination and recipe |
|---|---|
| `BLAS.scala`: Dot, Axpy, Gemm, Gemv, Ger, Scal, Axpby | `spatial.lib.blas` operations in the next section; honor all declared coefficients and logical view strides |
| `LinearAlgebra.scala`: matmult; three gemm overloads; gemm_fpga_fix; maxpool2d; averagepool2d; conv2d; two batchNorm2d overloads | `spatial.lib.linalg`, `spatial.lib.nn`; explicit broadcast/tagged coefficients, pooling/convolution/normalization recipes below |
| `ML.scala`: dp_flat, dp_tiled, sum_flat, sum_tiled, mlp_forward, denselayer, denselayer_backward, loss_squre_backward, identity, identity_backward, relu, relu_backward, SVMR_infer, SVMC_infer, inner_kernel, polynomial_kernel | `spatial.lib.ml`; reduce/map templates, dense/training/SVM recipes and versioned activation helpers |
| `LowPrecision.scala`: ConvertTo8Bit; two quantize overloads; mmlp; addlp; dequant; ConvertTo8Bit_Buggy; testmem; testreg | `spatial.lib.quant`; explicit quantization descriptor/recipes. Bug-labeled conversion and diagnostic test helpers become migration/test fixtures, not default algorithms |
| `Sort.scala`: two mergeSort overloads | Stable merge-sort recipe over local or transferred logical views; no silent length-256 assumption |
| `Scan.scala`: filter; filter_fifo | Distinct mask-map and compact-plus-count recipes; neither is misnamed as a general prefix scan |
| `MetaProgramming.scala`: withEns; MForeach; MReduce; ForeachWithLane; ReduceWithLane; FIFOs constructor/deq/enq | Lexical guards, checked domain/lane expansion and indexed queue-bank selection |
| `HostML.scala`: unstaged_dp; unstaged_denselayer; unstaged_denselayer_backward; unstaged_mlp; unstaged_loss_square; unstaged_loss_square_backward; unstaged_relu; unstaged_identity; unstaged_identity_backward; unstaged_relu_backward; unstaged_inner_kernel; unstaged_polynomial_kernel; unstaged_SVMR_infer; unstaged_SVMC_infer; unstaged_sigmoid | Host wrappers with exact shape checks and the same explicitly selected mathematical purpose; independent reference algorithms may use Python rationals/high precision, with their own numeric policy declared |
| `package.scala`: exports LinearAlgebra, LowPrecision and Scan | Ordinary explicit module exports; no staged global compiler mixin |
| Additional `math/LinearAlgebra.scala`: transpose; gemm | General permutation view/copy and common checked GEMM. Its Blackbox.GEMM route becomes an optional implementation choice with the same manifest/evidence gates |

The public `BoxedC`/`CScalar`/`CVector`/`CMatrix` categories become a closed coefficient-broadcast descriptor. Private `gemm_generalized`, nested accessors, Sort.log and metaprogramming rewrite overrides are implementation mechanisms rather than separate user operations.

## BLAS and matrix templates

Let `Q(op)` mean the adopted per-operation normalization, not a final-only cast. Products use the declared accumulator-input conversion first when its type differs from the element type. Each `sum` below uses the selected explicit reduction policy; the baseline is left-to-right.

| API | Exact baseline recipe |
|---|---|
| `dot(x,y)` | Equal logical length N; ordered fold of `Q(x[i]*y[i])` from zero. N=0 gives zero |
| `scal(alpha,x,out)` | Snapshot required source region, then `out[i]=Q(alpha*x[i])` |
| `axpy(alpha,x,y,out)` | `out[i]=Q(Q(alpha*x[i])+y[i])`; shape equality required |
| `axpby(alpha,x,beta,y,out)` | `out[i]=Q(Q(alpha*x[i])+Q(beta*y[i]))`; preserve two products and one addition |
| `gemm(alpha,A,B,beta,C,out)` | After transpose/view resolution, shapes M×K and K×N. Compute `s=sum_k Q(A[i,k]*B[k,j])`, then `v=Q(Q(s*alpha)+Q(C[i,j]*beta))`, then write `out[i,j]=v` |
| `gemv(alpha,A,x,beta,y,out)` | The same GEMM recurrence for M×N times length N, using the old selected `y[i]` snapshot |
| `ger(alpha,x,y,A,out)` | `out[i,j]=Q(A[i,j]+Q(Q(x[i]*y[j])*alpha))`, snapshot input A; this is a rank-one update |
| `matmult(A,B,out)` | GEMM dot recurrence without alpha/beta/C operations; do not synthesize numeric one in a format unable to represent one |
| `gemm_broadcast(...)` | C is tagged scalar, column-indexed row vector of length N, or M×N matrix. No automatic guessing from shape. `accumulate_out=True` adds the snapshotted old output after the computed v |
| `transpose(A,perm,out)` | Permutation must be a bijection of axes; `out.shape[j]=A.shape[perm[j]]`; invert that mapping for each read. Overlap uses a full selected-value snapshot |

Do not optimize alpha/beta equal zero into skipped operand reads or arithmetic without preserving the declared numeric/fault semantics. Floating `0*Inf` is a useful counterexample. A user can select a separately named no-C matmul routine instead of passing an uninitialized C with beta zero.

**Source disagreements:** original BLAS Dot/Axpy/Scal accept increments but load contiguous tiles; Gemm/Gemv accept alpha/beta and leading dimensions but their bodies do not apply all of them; Ger stores a product rather than the full declared rank-one update (`spatial@e7a8f2f:src/spatial/lib/BLAS.scala:9-31`, `spatial@e7a8f2f:src/spatial/lib/BLAS.scala:61-102`, `spatial@e7a8f2f:src/spatial/lib/BLAS.scala:105-173`). The proposed routines implement the explicit formulas above; migration cannot claim bitwise preservation of those old calls. On-chip GEMM's scalar/vector/matrix C cases and `sumY` are real distinctions (`spatial@e7a8f2f:src/spatial/lib/LinearAlgebra.scala:38-145`). `gemm_fpga_fix` is an old implementation variant, not a separate Python arithmetic contract.

## Convolution, pooling and batch normalization

Use NCHW tensors and explicit shapes. `conv2d` is the usual spatial cross-correlation: for output `(n,o,h,w)`, ordered-fold over `(c,kh,kw)` of `X[n,c,h*sh-pt+kh,w*sw-pl+kw]*K[o,c,kh,kw]`, substituting typed zero only for out-of-image coordinates. Kernel/input channel dimensions must match. Positive strides, nonnegative padding and positive kernel extents are preconditions. Output dimensions are `max(0, floor((input+pad_before+pad_after-kernel)/stride)+1)`; use separate top/bottom/left/right fields. Input padding does not grant a legal memory read. Zero output extents execute no bodies.

For `max_pool2d`, enumerate the same window in `(kh,kw)` order and fold max from the first included element, rather than an invented zero identity. The required `padding_policy` is either `constant(value)` (include the declared value) or `exclude` (omit out-of-bounds points). An empty excluded window faults before its output write. For `average_pool2d`, ordered-sum included values then divide once by the exact included count under the numeric contract; `include_pad` or `exclude_pad` is explicit. Default convenience wrappers use constant zero and include-pad respectively to make legacy padding visible. Formats that cannot represent the divisor must use a declared wider accumulator/division type, then an explicit output cast.

`batch_norm_stats` computes per-channel mean and population variance over lexicographic `(n,h,w)` with a nonempty sample domain. Compute `mean=sum(X)/count`; then `variance=sum(Q((X-mean)*(X-mean)))/count`; then `denom=sqrt(Q(variance+epsilon))`; then `out=Q(Q(Q((X-mean)/denom)*scale)+bias)`. Scalar or per-channel scale/bias is a tagged choice. Epsilon is explicit typed positive input. `batch_norm_inference` takes supplied mean/variance with the same denominator/output rule. No silent intermediate conversion to host or hardware float occurs. Invalid variance/denominator follows the numeric policy, and no statistical guarantee replaces arithmetic conformance.

Original pooling, convolution and both batchNorm2d overloads are source evidence at `spatial@e7a8f2f:src/spatial/lib/LinearAlgebra.scala:260-430`. Their zero padding, tuple use and intermediate Float conversion are not silently inherited. Proposed general padding, full input shapes and explicit normalization types are deliberate reviewed changes.

## Dense layers, training and SVM

`sum_map(N,mapper)` and `dot_map(N,pair_mapper)` use the ordered contribution rules, including exactly-once callback evaluation, empty zero and faults. Tiled wrappers use the same logical sequence and `min(tile,N-base)` tails. Tile size does not redefine a floating reduction tree. A callback is a closed DSL definition with an explicit effect summary.

`dense(W,b,x,activation)` checks W shape I×O, computes each output in increasing o: ordered dot over i, adds b[o], then applies the state-free typed activation. Optional linear-output and nonlinear-output destinations are explicit writes in that order. The array-return convenience expands at the caller into a caller-scope destination allocation followed by an ordinary borrowed-output call; the helper returns only that declared borrowed view. A host construction wrapper may generate this same graph. No ownership transfer of a callee-local allocation is inferred. `mlp` validates the entire layer chain and applies dense layer by layer, with explicitly allocated intermediate storage and per-layer profile/activation IDs. The zero-layer case is an identity copy of the input, not an invalid weights.head access.

`dense_backward` requires positive batch B and matching saved forward tensors. Snapshot W, b, inputs, saved linear/nonlinear values and incoming gradients before mutation. Define `d[b,o]=Q(dactivation(linear[b,o],nonlinear[b,o])*upstream[b,o])`; compute `dx[b,i]=sum_o Q(W_old[i,o]*d[b,o])`; `dw[i,o]=Q(Q(sum_b Q(x[b,i]*d[b,o])/B)*learning_rate)`; `db[o]=Q(Q(sum_b d[b,o]/B)*learning_rate)`. Calculate private gradients before updating W/b in lexicographic order as `Q(W_old-dw)` and `Q(b_old-db)`. The gradient-return variant returns dw/db/dx without updating weights; the update variant is explicit. Store all intermediate types and operation order; do not treat division and multiplication as interchangeable. This deliberately fixes when derivative callbacks run and which weights dx sees.

The original staged backward function computes input gradients before weight/bias updates, and normalizes its batch sums before applying learning rate (`spatial@e7a8f2f:src/spatial/lib/ML.scala:208-256`); the independent host implementation also computes dx from old W (`spatial@e7a8f2f:src/spatial/lib/HostML.scala:41-79`). Those observations motivate the proposed snapshot rule; they are not a general proof that all original training paths agree.

Activation recipes: identity returns input; identity derivative returns typed one or diagnoses an unrepresentable requested derivative type; ReLU is the selected min/max numeric rule with typed zero; its derivative is one for `x>0`, zero otherwise, with NaN behavior following comparison/profile rules. `loss_half_square` computes `0.5*(prediction-label)^2` with an explicitly representable accumulator type; its derivative is `prediction-label`. Sigmoid is the numeric engine's named intrinsic, not an accidental sequence of rounded operations unless a separately named compositional helper is selected.

`svm_regression` ordered-sums `Q(Q(alpha[v]*label[v])*kernel_value[v])`, then adds bias. `svm_classification` returns whether that result is greater than typed zero. Labels are explicit ±1 numeric values; a host Boolean adapter converts them through the declared type and checks representability. `inner_kernel` uses dot; `polynomial_kernel` computes the dot, then adds c, then calls the numeric profile's `pow(base,d)`. A separate integer-power template may expose repeated squaring with its own rounded-operation semantics; it is not assumed equal to the one-rounding mathematical intrinsic. Original staged helpers and host repeated multiplication differ (`spatial@e7a8f2f:src/spatial/lib/ML.scala:269-302`, `spatial@e7a8f2f:src/spatial/lib/HostML.scala:138-149`).

## Quantization

Use `QuantizationSpec(storage_type, accumulator_type, scale, zero_point, rounding, overflow)` with integral fixed storage type (F=0), finite strictly positive rational scale and a raw integer zero point within that storage range. The named `quantize_exact` mapping computes the exact rational input/scale, applies the chosen rounding once, adds zero point in unbounded integer arithmetic, then clamps/wraps/checks to the declared storage range. `dequantize_exact` forms `(q-zero_point)*scale` exactly and normalizes once to its output type. These are explicit library profiles built from the numeric engine, not host float division followed by an implicit cast. A compositional rounded-operator variant has a separate name/profile.

Runtime scale is the registered immutable `quant.scale_ratio.v1` record specified in [[20 - Numeric Engine Blueprint]]: bounded numerator/positive denominator and a bounded binary exponent, normalized exactly. Literal scales are frozen reduced rationals. Width/range derivation, bounded gcd, shifts, quotient/remainder rounding and exact sum/product expansion are specified there; these templates introduce no unbounded accelerator Fraction or hidden host arithmetic. A target must account for those finite intermediate widths.

Calibration is explicit: `symmetric_maxabs` scans finite values in logical order, takes exact maximum magnitude, uses zero-point 0 and symmetric integer range `[-Qmax,Qmax]`, and sets exact scale `maxabs/Qmax`. Empty calibration input rejects. All-zero input returns exact scale 1 and all zero-point outputs, avoiding division by zero. Nonfinite calibration values reject before output writes. The quantized storage type must contain zero point and Qmax>0. The original ConvertTo8Bit and quantize formulas use different scale denominators and can produce zero scale (`spatial@e7a8f2f:src/spatial/lib/LowPrecision.scala:9-107`); migration records the chosen new profile rather than silently replacing it.

`quantized_matmul` subtracts input zero points in the declared wider accumulator type, applies the explicit dot/reduction policy, and produces accumulator values with output scale `scaleA*scaleB` and zero point 0; optional requantization names an output QuantizationSpec. `quantized_add_broadcast` converts each input to its exact rational represented value, adds, then rounds once under the output QuantizationSpec. Axis choice is explicit; row versus column broadcasting cannot be inferred from a Boolean named transpose. Original mmlp and addlp are evidence for distinct scale rules (`spatial@e7a8f2f:src/spatial/lib/LowPrecision.scala:111-147`, `spatial@e7a8f2f:src/spatial/lib/LowPrecision.scala:197-235`). The new exact library profiles are deliberate redesigns and require numeric certificate/target realization where applicable.

`ConvertTo8Bit_Buggy`, testmem and testreg remain linked migration fixtures: the first is visibly labeled defective in source, the second a copy, and the third ordered register writes (`spatial@e7a8f2f:src/spatial/lib/LowPrecision.scala:237-267`, `spatial@e7a8f2f:src/spatial/lib/LowPrecision.scala:300-328`). Do not make a bug-preserving routine the default library entry point.

## Sort, filtering and lane helpers

Stable merge sort snapshots the selected input, creates runs of length one, and doubles run width each pass. Merge two runs with independent cursors, choose the left element on equivalent keys, and copy the remaining suffix. Alternate two scratch views; clamp run ends with min(N,end). N=0/1 is a no-op/copy. Default ascending float sort rejects NaN keys during the initial scan; signed zeros are equivalent and remain stable. A user comparator must supply the declared total-order contract on its admitted domain. Multiway MergeBuffer and tiled/streaming sort are later verified implementations of this same ordering, not the semantic definition. The old local sort fixes a 256-element block (`spatial@e7a8f2f:src/spatial/lib/Sort.scala:11-58`).

`filter_mask` evaluates predicate once per selected input and writes a Bool mask, with an explicit numeric-mask conversion if requested. `filter_compact` captures each input value once in input order, then calls the predicate once on that captured value and retains that same value if accepted. After every predicate and the accepted count are known, it checks destination capacity, writes the compact prefix in that order, and returns count; the destination tail is untouched. Destination capacity is checked before prefix publication; failure preserves predicate effects already committed but no partial prefix writes. This is an explicit library publication policy. Original filter and filter_fifo have different outputs (`spatial@e7a8f2f:src/spatial/lib/Scan.scala:9-38`). A general prefix-scan convenience can be built as an ordered fold publishing each intermediate result, but is a new API, not a falsely attributed legacy feature.

For lane helpers, logical ordinal k maps to index `start+k*step`, lane `k mod par`, and group `k//par`; par>0 and step!=0. Validity uses the signed-step domain predicate, so negative steps and tails work. An invalid lane executes no callback or operand effects. Explicit valid-returning helpers return metadata separately from masked data; no fabricated value becomes usable. `withEns` becomes a lexical lazy guard region. `FIFOs(dup,depth)` becomes a checked queue-bank descriptor; selected index is bounds-checked once, then exactly one endpoint request is made. There is no eager dequeuing from all banks and no implicit addition of placeholder zero values (`spatial@e7a8f2f:src/spatial/lib/MetaProgramming.scala:47-119`).

## Independent acceptance cases

| ID | Concrete expected distinction |
|---|---|
| LIB01 | Integer GEMM A=[ [1,2] ], B=[ [3],[4] ], C=[ [5] ], alpha=2, beta=3 produces 37, not the old coefficient-ignoring product 11 |
| LIB02 | `ger` with old A=[ [7] ], x=[2], y=[3], alpha=4 produces 31; product-only implementation gives 6 |
| LIB03 | Logical strided x=[1,3] from backing [1,99,3], y=[2,4] gives dot 14; contiguous substitution gives 398 |
| LIB04 | Transpose [ [1,2,3],[4,5,6] ] produces shape3×2 with rows [1,4],[2,5],[3,6]; overlapping copy uses the source snapshot |
| LIB05 | Max pool of [-5,-2] without included padding gives -2. With an included zero-padding element it gives 0; policies are explicit |
| LIB06 | 1×1 channel cross-correlation over [ [1,2],[3,4] ] with kernel [ [1,0],[0,-1] ] and no padding gives -3; reversing the kernel changes the result |
| LIB07 | One input, one output, B=1: W=2, bias=1, x=3, identity activation, incoming gradient=4, learning rate=1/2 gives dx=8, dw=6, db=2, new W=-4, new bias=-1; dx must use old W |
| LIB08 | Symmetric all-zero quantization returns scale1 and zero codes. Explicit scale1/2, zero_point0, nearest-even maps [1/4,3/4,-1/4,-3/4] to [0,2,0,-2] |
| LIB09 | Stable sort keys [(2,a),(1,b),(2,c)] produces [(1,b),(2,a),(2,c)]; filter [3,1,4] by >2 gives prefix [3,4], count2, untouched tail |
| LIB10 | Domain start5,end=-1,step=-2,par2 visits indices5,3,1 with lanes0,1,0 and one inactive tail lane; inactive callback consumes nothing |
| LIB11 | F32 dot of [33554432,1,-33554432,1] with four ones gives 1 under ordered fold and 0 under the adjacent-pair fixed tree; tile changes must preserve the selected result |
| LIB12 | Activation/comparator/profile change invalidates library specialization identity; callback-origin diagnostics name both library definition and caller instantiation |

LIB01–LIB11 passed independent rational/array calculations, with standard binary32 pack/unpack for the exact LIB11 discriminator. The saved standalone probe compares those calculations against the explicit values above; it does not execute Spatial source or validate a library implementation. LIB12 remains a designed compiler acceptance case. Later compiler fixtures add zero/odd extents, tails, aliases, nonfinite values, every broadcast/transposition form, active/inactive faults and helper composition. Hardware uses the same expanded core graph and every applicable numeric/protocol/storage gate; these recipes do not bypass target legality.
