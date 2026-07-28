---
layout: page
title: "Lesson 6: Tiny CNN Integration"
permalink: /lessons/06-tiny-cnn/
---

# Lesson 6: tiny CNN integration

## Outcome

Run a complete multi-layer quantized CNN through the compiler, RV64 runtime,
Spike, and NPU model before attempting YOLO.

## Proposed network

Use a deliberately small static network:

```text
Input 1x3x32x32
-> Conv3x3 stride 1 + bias + SiLU
-> Conv3x3 stride 2 + bias + SiLU
-> residual block
-> global average pool or fixed reduction
-> GEMM
-> class scores
```

If global pooling is not implemented, execute it on the host and document the
partition.

## Step 1 — Create the floating-point reference

- Generate deterministic weights first.
- Later train or import a tiny model.
- Save all intermediate tensors.
- Define input preprocessing.

Random deterministic weights test infrastructure better than accuracy. A
trained model becomes useful when quantization accuracy is studied.

## Step 2 — Quantize

- Choose calibration inputs.
- Record tensor ranges.
- Start with per-tensor activations.
- Use per-output-channel weight scales if supported.
- Compare every quantized layer with the integer reference.

## Step 3 — Compile and inspect

Publish:

- Graph before and after fusion
- Tile choices
- Buffer lifetime table
- Scratchpad map
- Command disassembly
- Estimated traffic

## Step 4 — Run natively

The native path must pass before Spike is involved. Save intermediate tensors
at graph partition boundaries.

## Step 5 — Run under Spike

The RV64 application:

1. Loads or embeds the input and command buffer.
2. Submits work.
3. Waits with a timeout.
4. Checks output hash or values.
5. Prints machine-readable counters.

## Correctness gate

- Float framework and exported graph agree within tolerance.
- Integer reference and native NPU agree exactly.
- Native and Spike-connected NPU agree exactly.
- Layer-level diagnostics identify the first mismatch.
- Counter JSON is deterministic.

## Why this gate matters for YOLO

It exercises:

- Multiple tensor lifetimes
- Residual addition
- Requantization across layers
- Compiler fusion
- Repeated command execution
- Complete RV64 submission

Debugging these on a 32x32 input is much faster than on a detector graph.

## Primary references

- [ONNX operator specifications](https://onnx.ai/onnx/operators/)
- [ONNX Runtime quantization](https://onnxruntime.ai/docs/performance/model-optimizations/quantization.html)
- [Gemmini software and simulator structure](https://github.com/ucb-bar/gemmini)
