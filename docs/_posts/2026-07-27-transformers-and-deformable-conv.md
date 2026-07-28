---
layout: post
title: "Capability branches: Transformers and deformable convolution"
date: 2026-07-27 02:00:00 +0900
categories: progress
milestone: phase-0
record_type: decision
---

## Question

Should the NPU plan include Transformer/LLM operations and deformable
convolution?

## Decision

Yes, as gated branches after the shared GEMM/compiler/runtime foundation.
Neither branch blocks the first YOLOv8n target.

## Transformer implication

The MAC array is reusable for linear projections and attention MatMuls, but a
decoder block also needs stable Softmax, RMSNorm, RoPE, causal masks,
elementwise gates, and a KV cache. Prefill can use larger GEMMs, while
one-token decode becomes GEMV- and bandwidth-heavy.

The first target will be one tiny Llama-style decoder block, not a complete
LLM.

## Deformable-convolution implication

Offsets generate data-dependent fractional addresses. Bilinear sampling can
require four bounds-checked input reads per logical sample, and DCNv2 adds a
modulation mask. This behavior cannot be counted as ordinary convolution.

The first implementation will be a correct FP32 host fallback. The first
accelerator experiment will materialize a sampled column buffer and reuse the
existing GEMM.

## References

- [Attention Is All You Need](https://arxiv.org/abs/1706.03762)
- [FlashAttention](https://arxiv.org/abs/2205.14135)
- [ONNX Attention](https://onnx.ai/onnx/operators/onnx__Attention.html)
- [Deformable Convolutional Networks](https://arxiv.org/abs/1703.06211)
- [ONNX DeformConv](https://onnx.ai/onnx/operators/onnx__DeformConv.html)
