---
layout: page
title: "Lesson 1: Integer Inference"
permalink: /lessons/01-integer-inference/
---

# Lesson 1: integer inference

## Outcome

Define and test the exact integer arithmetic that every compiler, simulator,
and RTL implementation must follow.

## Step 1 — Define a tensor contract

Version one should state:

| Property | Initial choice |
|---|---|
| Activation type | Signed INT8 |
| Weight type | Signed INT8 |
| Bias type | Signed INT32 |
| Accumulator | Signed INT32 |
| Byte order | Little-endian |
| GEMM layout | Row-major A, B, and C |
| Later Conv layout | NCHW activation and OIHW weight, when frozen |
| Rounding | Nearest, ties-to-even |
| Accumulator overflow | Wrap modulo `2^32` after every addition |
| INT8 output overflow | Saturate to the commanded clamp interval |

These are v1 project decisions in the
[numerical contract](../numerical-contract.md). Changing
one requires a version change or explicit compatibility rule.

## Step 2 — Understand affine quantization

Represent a real value approximately as:

```text
real_value = scale * (quantized_value - zero_point)
```

Begin with symmetric signed quantization:

```text
zero_point = 0
```

Then add asymmetric activations as a separate experiment. Separating the two
prevents zero-point correction terms from obscuring the first GEMM.

## Step 3 — Implement scalar helpers

Implement and test:

- Quantize FP32 to INT8
- Dequantize INT8 to FP32
- Saturating cast
- Widening multiply
- INT32 accumulation
- Fixed-point requantization
- Rounding ties

Boundary vectors must include:

```text
-128, -127, -1, 0, 1, 126, 127
```

Also test accumulator values around INT32 limits and positive/negative
halfway-rounding cases.

## Step 4 — Implement a dot product

Reference equation:

```text
acc = 0
for k:
    acc = wrap_i32(acc + int32(a[k]) * int32(b[k]))
acc = wrap_i32(acc + bias)
q = saturate(round(acc * effective_scale))
```

Use a higher-precision host calculation to locate the exact additions that
cross an INT32 boundary, then verify that the reference wraps at each specified
point. Higher precision is a diagnostic oracle; it does not replace v1 wrap
semantics.

## Step 5 — Differential testing

Compare:

1. Clear Python reference
2. Vectorized NumPy implementation
3. Portable C++ implementation

Test:

- Hand-written boundary cases
- All short combinations where practical
- At least 1,000 seeded random vectors
- Different K lengths
- Positive and negative biases
- Scales above and below one

Every random failure must print a replayable seed and full input.

## Correctness gate

- The numerical contract is documented in one authoritative file.
- Python and C++ agree exactly.
- Rounding ties and saturation boundaries have named tests.
- No test relies on host signed-integer overflow.
- Tests are deterministic.

## What to explain in the progress article

- Why INT8 multiplication uses a wider accumulator
- Why zero must be representable
- Why rounding mode affects layer-by-layer agreement
- Difference between implementation correctness and model accuracy
- Which choices match ONNX and which are project-specific

## Primary references

- [ONNX Runtime quantization guide](https://onnxruntime.ai/docs/performance/model-optimizations/quantization.html)
- [ONNX QLinearMatMul specification](https://onnx.ai/onnx/operators/onnx__QLinearMatMul.html)
- [ONNX QuantizeLinear specification](https://onnx.ai/onnx/operators/onnx__QuantizeLinear.html)
- [ONNX DequantizeLinear specification](https://onnx.ai/onnx/operators/onnx__DequantizeLinear.html)
