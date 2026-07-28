---
layout: page
title: Numerical Contract
permalink: /numerical-contract/
---

# Numerical contract

Status: **v1 normative design and source scaffold; verification deferred**

This is a project-defined integer contract. ONNX affine quantization and
operator specifications inform the real/quantized relationship, but ONNX does
not define this project's accumulator wrap points or fixed-point multiplier
selection.

## Rule provenance

| Rule | Classification |
|---|---|
| `real = scale * (q - zero_point)` | External baseline: affine quantization convention |
| Round-to-nearest, ties-to-even for quantization | External baseline adopted by the project |
| Signed symmetric device tensors | Project decision |
| Wrap after every INT32 accumulation and bias addition | Project decision |
| `multiplier / 2^shift` fixed-point form | Project decision |
| Reject zero-sized device GEMM | Project decision |

## Version 1 types

| Purpose | Type |
|---|---|
| Activation | Signed INT8 |
| Weight | Signed INT8 |
| Bias | Signed INT32 |
| Accumulator | Signed INT32 |
| Serialized byte order | Little-endian |

## Quantization

```text
real = scale * (quantized - zero_point)
```

Version 1 device tensors are signed symmetric and require `zero_point = 0`.
General scalar teaching helpers may accept any signed INT8 zero point, but
nonzero values cannot be serialized into a v1 device command.

Floating-point quantization uses round-to-nearest, ties-to-even, followed by
saturation to `[-128, 127]`.

The scale must be finite and strictly positive, and the real input must be
finite. If the finite division `real/scale` overflows to infinity, quantization
saturates according to the sign rather than attempting an out-of-range
floating-to-integer conversion. NaN, infinite input, zero/negative scale, or an
unrepresentable dequantized result returns the stable `INVALID_NUMERIC_INPUT`
category.

Public v1 dot/GEMM helpers reject a zero-length dot product or any zero
`M`, `N`, or `K`. This matches the command ABI.

## Accumulation

Every INT8 product is widened to INT32. Accumulation uses defined
two's-complement 32-bit wrapping after each addition:

```text
acc = wrap_i32(acc + int32(a) * int32(b))
```

The reference never relies on C++ signed overflow.

INT32 bias addition applies the same `wrap_i32` operation after each bias is
added. ReLU observes the wrapped INT32 value.

## Fixed-point requantization

The effective scale is:

```text
multiplier / 2^shift
```

with:

```text
shift in [0, 62]
multiplier in [1, 2147483647]
zero_point = 0
```

The implementation:

1. Multiplies the INT32 value and signed INT32 multiplier in INT64.
2. Divides by `2^shift` using round-to-nearest, ties-to-even.
3. Adds the output zero point.
4. Saturates to the command-provided signed INT8 interval.

Negative values use the same magnitude-based ties-to-even rule as positive
values.

For an absolute product `p` and divisor `d = 2^shift`, compute integer
`quotient = p / d` and `remainder = p % d`. Increment the quotient when
`remainder > d/2`, or when `remainder == d/2` and the quotient is odd. Restore
the original sign after rounding. `shift=0` is exact and requires no division
rounding.

The INT32-by-INT32 product and the rounded value plus zero point fit in signed
INT64 for all legal v1 fields. Saturation to the command clamp interval occurs
only after rounding and zero-point addition.

## Quantization-parameter derivation

For input scale `s_x`, weight scale `s_w`, and output scale `s_y`:

```text
bias_scale = s_x * s_w
effective_scale = bias_scale / s_y
```

All scales are finite and positive. Bias uses zero point zero and is quantized
with ties-to-even into INT32; a bias outside INT32 range is a compiler error,
not silently saturated.

To encode `effective_scale`, examine shifts from 62 down to 0 and choose the
first for which:

```text
multiplier = round_ties_to_even(effective_scale * 2^shift)
1 <= multiplier <= INT32_MAX
```

This selects the largest legal shift and therefore the finest available binary
resolution. An effective scale with no legal pair is rejected. The compiler
records the real effective scale, selected pair, and approximation error in
its manifest.

## Layout

Reference GEMM stores:

- A as row-major `[M, K]`
- B as row-major `[K, N]`
- C as row-major `[M, N]`
- Bias as `[N]`, broadcast across M

## Planned evidence gate

The shared numerical fixtures are:

```text
tests/fixtures/numerics/requantize.csv
tests/fixtures/numerics/gemm-corpus.csv
```

When execution resumes, run:

```powershell
./scripts/test.ps1 -Group numerics
```

The source scaffold includes shared named requantization cases and a versioned
configuration for 1,000 seeded GEMM cases consumed by both Python and C++.
When executed, the gate will compare outputs and stable error categories,
including INT32 wrap cases and extreme finite quantization inputs.

## Primary references

- [ONNX QLinearMatMul](https://onnx.ai/onnx/operators/onnx__QLinearMatMul.html)
- [ONNX IR specification](https://onnx.ai/onnx/repo-docs/IR.html)

## Deferred numerical contracts

The following require later versioned sections:

- Asymmetric tensor GEMM zero-point correction
- Per-channel convolution scales
- SiLU approximation
- FP16/BF16 mixed precision
- Softmax and normalization
- Deformable-convolution offsets and interpolation

## Continue through the specification

Next specification: [Command-buffer ABI](command-abi.md)
