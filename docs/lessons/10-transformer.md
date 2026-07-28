---
layout: page
title: "Lesson 10: Transformer and LLM Operations"
permalink: /lessons/10-transformer/
---

# Lesson 10: Transformer and LLM operations

## Outcome

Execute one tiny decoder block and explain the architectural differences
between prompt prefill and autoregressive token decode.

Read the full [Transformer capability track](../transformer-track.md).

## Fixed lab configuration

Use synthetic weights and activations first:

| Parameter | Initial value |
|---|---:|
| Batch | 1 |
| Hidden size | 128 |
| Query heads | 4 |
| KV heads | 4 |
| Head dimension | 32 |
| FFN size | 256 |
| Sequence lengths | 1, 16, 64 |
| Layers | 1 |
| Reference dtype | FP32 |
| Seed | 0 |

Do not add a tokenizer, embedding table, sampling loop, or pretrained model to
this first lab. The input is a deterministic tensor with shape `[B, S, H]`.

## T0 — Freeze equations and tensor shapes

Write a shape table before implementing:

```text
X                 [B, S, H]
Q                 [B, QH, S, D]
K, V              [B, KVH, S, D]
scores            [B, QH, S, S]
probabilities     [B, QH, S, S]
attention output  [B, S, H]
FFN gate/up       [B, S, F]
block output      [B, S, H]
```

For the first multi-head version, `QH == KVH`. The grouped-query extension must
state how KV heads are repeated or mapped to query heads.

Deliverable:

```text
docs/specs/tiny-transformer-block.md
```

The specification should define RMSNorm epsilon, RoPE frequency convention,
causal-mask orientation, Softmax axis, and weight-matrix orientation.

## T1 — FP32 RMSNorm

Implement:

```text
rms = sqrt(mean(x^2) + epsilon)
y = weight * x / rms
```

Tests:

- All-zero input
- Constant input
- Large and very small magnitudes
- One row with a hand-calculated result
- Wrong-axis test that would fail if reduction includes sequence or batch

Save maximum absolute and relative error against the selected framework.

## T2 — Q/K/V projections and head reshape

Compute Q, K, and V using explicit FP32 MatMul. Then reshape and transpose into
head-major form.

Record contiguous strides before and after the transformation. A reshape is
metadata-only only when the storage layout permits it; otherwise account for a
transpose/copy.

Gate:

- Projection tensors match the framework.
- Converting to head-major form and back is an identity.
- The graph inventory shows which changes are views and which move bytes.

## T3 — RoPE

Apply rotary position embedding to pairs of Q/K features. Begin with positions
`0..S-1` and no cache offset.

Tests:

- Position zero
- One hand-calculated 2D rotation
- Norm preservation for each rotated pair
- Odd head dimension rejection
- Decode position equal to the existing cache length

Do not hide frequency-base or pair-order conventions inside helper code.

## T4 — Explicit scaled attention

Implement the inspectable algorithm:

```text
scores = Q @ transpose(K)
scores = scores / sqrt(D)
scores = causal_mask(scores)
probabilities = stable_softmax(scores, axis=-1)
context = probabilities @ V
```

Stable Softmax subtracts the row maximum before exponentiation. A masked
future position must receive zero probability.

Tests:

- One-token attention produces probability 1.
- Each unmasked probability row sums to 1 within tolerance.
- No masked value affects the result.
- Very large positive/negative score rows remain finite.
- Framework score, probability, and context tensors match.

Save all three intermediate tensors for one very small case.

## T5 — Output projection and residual

Merge heads, apply the output projection, and add the original residual.

Gate:

- Head merge reverses the earlier split exactly.
- The output projection matches a direct matrix expression.
- Residual input/output shapes are identical.

## T6 — SwiGLU feed-forward block

Implement:

```text
gate = SiLU(X @ W_gate)
up = X @ W_up
hidden = gate * up
down = hidden @ W_down
output = X + down
```

Use the second RMSNorm at the point selected by the frozen pre-norm block
specification. Compare every projection and elementwise result.

## T7 — Compose and replay the FP32 block

Generate one fixture containing inputs, weights, and expected intermediates.
The complete block must be deterministic for sequence lengths 1, 16, and 64.

Required evidence:

- Framework version and configuration
- Tensor names and shapes
- Error summary at each boundary
- Peak temporary bytes for explicit attention
- Hashes of the fixture and output

## T8 — Mixed NPU/host partition

Use the NPU for the linear and matrix operations. Keep RMSNorm, RoPE, mask,
Softmax, SiLU, and elementwise multiplication in the clear FP32 host/reference
path.

Report:

```text
NPU operator count and MACs
host operator count
bytes crossing each partition
integer tensor error
final FP32 block error
estimated NPU cycles
host work excluded from NPU cycle estimate
```

If a host operation consumes an NPU-produced integer tensor, document the
dequantization boundary.

## T9 — KV cache

Allocate separate K and V regions with:

- Maximum sequence length
- Current valid length
- Layer index
- KV head index
- Token position
- Head dimension

First run prefill to populate tokens `0..S-1`. Then process one new token using
only the existing cache plus the new K/V entries.

Tests:

- Empty cache
- First append
- Prefill followed by decode
- Exact maximum capacity
- One-token overflow
- Reset and reuse
- Invalid layer/head/position

The cached decode result must match recomputing attention over the full token
prefix.

## T10 — Prefill versus decode experiment

Measure the two paths separately:

| Measurement | Prefill | Decode |
|---|---:|---:|
| Query length | `S` | 1 |
| KV length | `S` | growing |
| GEMM utilization | record | record |
| Weight bytes | record | record/token |
| KV-cache read bytes | record | record/token |
| Temporary attention bytes | record | record |
| Estimated cycles | record | record/token |

The important lesson is that decode contains GEMV-like `M=1` work and a
growing cache read, so a MAC-rich array may still be underused.

## T11 — Grouped-query attention

Reduce the KV head count from 4 to 1 or 2 while keeping 4 query heads. Define
the query-to-KV head mapping explicitly.

Compare:

- Output correctness
- KV-cache capacity
- Cache bytes read per token
- Projection parameter count
- Any extra broadcast or scheduling work

## T12 — IO-aware attention

Only after explicit attention is correct, implement a tiled exact algorithm
that maintains online row maximum and normalization statistics instead of
materializing the full score/probability matrices.

The gate is numerical agreement with explicit attention plus lower temporary
storage or DRAM traffic. Call it “IO-aware attention” unless the implementation
actually satisfies a named FlashAttention interface and contract.

## First hardware partition

Use the NPU for linear and matrix operations. Execute RMSNorm, RoPE, Softmax,
masking, and SwiGLU in the clear FP32 host/reference path. This makes mixed
execution visible and provides evidence for deciding which vector or special
function unit to add.

## Required experiments

- Sequence 1, 16, and 64
- Prefill versus one-token decode
- Multi-head versus grouped-query attention
- Explicit versus IO-aware attention
- INT8 linear layers with FP32 reductions
- KV-cache layouts
- Array utilization when `M=1`

## Gate

- Framework and FP32 reference match.
- Mixed path has documented numerical error.
- Cache updates are replayable and bounds checked.
- Prefill and decode counters are separate.
- Host fallback is included in coverage.
- Every optimization is compared with the explicit FP32 path.
- Results make no claim about full-model quality or tokens/second.

## Required progress posts

Write at least three posts:

1. `Tiny FP32 decoder block and tensor-shape contract`
2. `Mixed INT8/FP32 partition and error`
3. `KV cache: prefill versus one-token decode`

Add a fourth post for IO-aware attention rather than mixing it into cache
bring-up.

## Primary references

- [Attention Is All You Need](https://arxiv.org/abs/1706.03762)
- [FlashAttention](https://arxiv.org/abs/2205.14135)
- [ONNX Attention](https://onnx.ai/onnx/operators/onnx__Attention.html)
- [ONNX RMSNormalization](https://onnx.ai/onnx/operators/onnx__RMSNormalization.html)
- [Meta Llama 3 implementation](https://github.com/meta-llama/llama3/blob/main/llama/model.py)
- [Current Meta Llama models repository](https://github.com/meta-llama/llama-models)
