---
layout: page
title: "Lesson 4: Compiler and Command Stream"
permalink: /lessons/04-compiler/
---

# Lesson 4: compiler and command stream

## Outcome

Lower a small static graph into a deterministic, versioned command buffer that
the native NPU model can execute.

Use the [tiny compiler design](../compiler-design.md) and
[command ABI](../command-abi.md) as the detailed contracts.

## Step 1 — Define a tiny graph format

Start with JSON rather than ONNX. Required concepts:

- Named tensors
- Static shapes
- Element types
- Constant weights
- Ordered nodes
- Graph inputs and outputs

Support only implemented operators. Reject unknown attributes.

## Step 2 — Build a typed IR

Every IR value must have:

```text
shape
element type
layout
quantization parameters
producer
consumers
```

Provide a stable text dump so every compiler pass can be reviewed.

## Step 3 — Implement passes independently

Recommended sequence:

1. Validation
2. Static shape inference
3. Explicit Linear-to-GEMM/bias lowering
4. Quantization validation
5. V1 M/N tiling when required
6. Buffer lifetime analysis
7. Scratchpad allocation
8. Serial DMA/compute scheduling
9. Command emission

Each pass needs before/after fixtures and negative tests.

Constant folding, Conv/BatchNorm folding, and numerical fusion are later
lessons. They are not part of the first explicit MLP compiler.

## Step 4 — Define the binary ABI

Specify:

- Magic and ABI version
- Total byte length
- Little-endian fields
- Command opcode and command byte length
- Alignment
- Reserved fields written as zero
- Error behavior

Do not serialize native C++ structs by copying their memory. Use explicit
encoding helpers and golden byte fixtures.

## Step 5 — Add a disassembler

Example desired output:

```text
0020 DMA_LOAD  guest=0x... spad=0x0000 bytes=256
0040 DMA_LOAD  guest=0x... spad=0x1000 bytes=1024
0060 GEMM      M=8 N=8 K=32 a=0x0000 b=0x1000 c=0x2000
0090 REQUANT   src=0x2000 dst=0x3000 multiplier=... shift=...
00c0 DMA_STORE spad=0x3000 guest=0x... bytes=64
00e0 END
```

Offsets include the 32-byte buffer header and match the ABI 1.0 record sizes.
The binary should never be the only explanation of compiler output.

## Step 6 — Add ONNX as an importer

After the tiny graph works:

- Validate model and opset.
- Invoke or verify shape inference.
- Import only a declared operator subset.
- Convert ONNX layouts/attributes into internal canonical form.
- Produce an operator support and fallback report.

The compiler IR remains independent of ONNX protobuf classes.

## Correctness gate

- Repeated compilation produces identical bytes.
- Every IR pass preserves graph validity.
- The disassembler round-trips or matches golden text.
- Malformed command buffers fail without crashes.
- Address, shape, and byte-size arithmetic checks overflow.
- Tiny JSON and equivalent ONNX graphs lower to equivalent IR.

## Primary references

- [ONNX IR specification](https://onnx.ai/onnx/repo-docs/IR.html)
- [ONNX shape inference](https://onnx.ai/onnx/repo-docs/ShapeInference.html)
- [ONNX operator specifications](https://onnx.ai/onnx/operators/)
