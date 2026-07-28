---
layout: page
title: "Lesson 3: Convolution and Graph Lowering"
permalink: /lessons/03-convolution/
---

# Lesson 3: convolution and graph lowering

## Outcome

Execute quantized Conv2D and the core building blocks needed by a small CNN and
YOLOv8n.

## Step 1 — Specify Conv2D

Begin with:

- NCHW input
- OIHW weights
- Batch 1
- Groups 1
- Dilation 1
- Static padding and stride
- 1x1 and 3x3 kernels

Add grouped/depthwise convolution only when a target graph requires it.

## Step 2 — Implement a direct reference

Use explicit loops over:

```text
N, OC, OH, OW, IC, KH, KW
```

The direct implementation is slow but makes padding and indexing observable.

## Step 3 — Compare lowering choices

Implement or model:

- Direct tiled convolution
- `im2col + GEMM`
- Implicit GEMM without materializing full `im2col`

Compare temporary memory, repeated input reads, compiler complexity, and reuse.
The first NPU command can use explicit lowering, but the documentation must
show its memory cost.

## Step 4 — Fold BatchNorm

Inference BatchNorm can be folded into convolution weights and bias. Verify:

- Float Conv + BatchNorm versus folded float Conv
- Quantized folded Conv versus integer reference
- Per-output-channel weight scales

Never assume fusion is correct only because final network output looks close.

## Step 5 — Add CNN building blocks

In order:

1. Bias
2. SiLU
3. Residual Add
4. Concat
5. MaxPool
6. Nearest-neighbor Resize

Concat and residual connections are primarily memory-lifetime problems for the
compiler, not new MAC operations.

## Step 6 — Implement a miniature C2f-like block

Use a small channel count and spatial size. Save each internal tensor:

- Initial split
- Bottleneck convolution outputs
- Residual output
- Concatenated tensor
- Final convolution

This is the rehearsal for the YOLOv8 C2f block.

## Correctness gate

- Direct and lowered Conv2D agree.
- Odd dimensions, stride 2, and padding are tested.
- BatchNorm folding has independent tests.
- Fusion does not change the integer contract.
- Intermediate block tensors agree, not just final output.

## Performance questions

- When does materialized `im2col` dominate memory traffic?
- How much reuse comes from 1x1 versus 3x3 convolution?
- Which tensor should remain in scratchpad?
- What peak live memory is created by skip connections?

## Primary references

- [ONNX Conv specification](https://onnx.ai/onnx/operators/onnx__Conv.html)
- [ONNX QLinearConv specification](https://onnx.ai/onnx/operators/onnx__QLinearConv.html)
- [YOLOv8 architecture YAML](https://github.com/ultralytics/ultralytics/blob/main/ultralytics/cfg/models/v8/yolov8.yaml)
- [Ultralytics architecture guide](https://docs.ultralytics.com/guides/yolo-architecture/)
