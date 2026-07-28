---
layout: page
title: YOLO Target Decision
permalink: /yolo-target/
---

# YOLO target decision

## Decision

Use **YOLOv8n detection** as the first complete application target.

Use **YOLO26n detection** as a later comparison target.

Do not begin implementation with either complete model. Begin with individual
operators and advance through the gates in the
[learning path](learning-path.md).

## Why YOLOv8n first

YOLOv8n is a useful bridge between educational kernels and a real deployment:

- The official architecture is primarily convolution, C2f blocks, SPPF,
  nearest-neighbor upsampling, concatenation, and a convolutional detection
  head.
- Its compute-heavy graph maps naturally to an INT8 array.
- Box decoding and NMS can run on the RISC-V host initially.
- It is small enough to simulate at a reduced fixed resolution.
- Its architecture and exported behavior are mature enough for a learning
  project.

Parameter and operation counts vary with the Ultralytics release, input size,
fusion state, and counting convention. This page deliberately does not freeze
a copied number. Gate Y0 records counts produced by the pinned model revision
and the project's fixed input, and later performance claims cite that manifest.

## Why not start with YOLO26n

YOLO26n is attractive because it removes DFL and supports a one-to-one,
NMS-free detection path. The default output is up to 300 detections with shape
`(N, 300, 6)`.

However, the full graph also introduces work beyond a first convolutional NPU:

- A C2PSA attention block
- C3k2 blocks rather than YOLOv8 C2f blocks
- Depthwise-separable classification branches
- End-to-end score selection using TopK and Gather-style operations

YOLO26 therefore removes some postprocessing complexity while adding
accelerator/compiler operator complexity. It is ideal for the second
architecture study, not the first bring-up.

## Target configuration

The initial detector target is:

| Property | Value |
|---|---|
| Model | YOLOv8n detection |
| Input | Fixed `1x3x320x320` NCHW |
| Batch | 1 |
| Classes | 80 COCO classes |
| Weights | Pretrained, downloaded separately |
| NPU arithmetic | Signed INT8 operands, INT32 accumulation |
| Quantization | Static post-training quantization first |
| Graph format | Fixed-shape ONNX |
| Host | Bare-metal RV64 under Spike |
| NPU interface | MMIO command buffer |
| Postprocessing | RISC-V host for DFL decode and NMS |

Why 320x320 first:

- It reduces the functional simulation workload.
- It keeps all major P3/P4/P5 graph structures.
- It makes layer-level debugging faster.
- It avoids claiming standard 640x640 accuracy or performance.

After correctness, repeat selected measurements at 640x640.

## Operator deployment plan

### NPU-required operators

- Conv2D: 1x1 and 3x3
- Bias addition
- SiLU or a documented approximation
- Residual Add
- Concat with explicit memory placement
- MaxPool for SPPF
- Nearest-neighbor Resize/Upsample
- Requantize and clamp
- DMA load/store

The original MLP command set does not need every item in this list. YOLO
support is an ABI capability extension after the first release. In particular,
SiLU, MaxPool, and Resize must not be added to `v0.1` merely because `v1.0`
will need them.

### Compiler transformations

- Fold BatchNorm into Conv weights and bias
- Convert static shapes to explicit tensor descriptors
- Lower convolution to tiled loops or GEMM-like commands
- Fuse Conv + bias + activation where legal
- Allocate skip-connection lifetimes in shared memory
- Partition unsupported nodes to the host

### Host operations in the first version

- Input image resize, letterbox, and normalization
- DFL box decode
- Anchor/stride coordinate construction
- Sigmoid if it is not fused into the NPU path
- Confidence filtering
- Non-maximum suppression
- Drawing or printing detections

Keeping postprocessing on the host is not a failure. Heterogeneous execution is
part of a real accelerator software stack.

## Export-boundary warning

The normal Ultralytics YOLOv8 ONNX export follows the inference path in the
`Detect` module and normally exposes decoded prediction output. It should not
be assumed to expose the three raw per-scale box/class head tensors as model
outputs.

The project must keep two artifacts distinct:

1. **Official fixed-shape export:** used to validate PyTorch versus ONNX
   Runtime behavior.
2. **Partitioned deployment graph:** created by a documented graph-cut or
   export adapter that exposes stable intermediate tensors for the NPU and
   leaves DFL/decode/NMS to the host.

The partition tool must identify boundaries by validated graph values and
shapes, not brittle node numbers copied from one export. Both artifacts need
version, hash, opset, and operator inventories.

## Accuracy and correctness rules

There are two separate comparisons:

### Integer implementation correctness

The compiler, native NPU model, and Spike-connected NPU must agree exactly with
the project's defined integer reference at every graph partition boundary.

### Model accuracy

INT8 detections are not expected to be bit-identical to floating point.
Compare:

- Layer activation error
- Final boxes, scores, and classes on fixed images
- Detection agreement at a chosen confidence threshold
- mAP on a small documented dataset such as COCO8

Static quantization is chosen first because ONNX Runtime recommends static
quantization for CNN models. Calibration data, method, sample count, scale
granularity, and excluded nodes must be recorded.

## Incremental YOLO gates

### Y0 — Host baseline

- Run pinned PyTorch inference.
- Export fixed-shape FP32 ONNX.
- Run ONNX Runtime.
- Compare outputs.
- Save the operator histogram and graph hash.

### Y1 — One convolution

- Extract the first convolution and folded BatchNorm.
- Quantize it.
- Compare reference, native model, and ONNX intermediates.

### Y2 — One C2f block

- Implement split, bottleneck, residual, concat, and fusion convolution.
- Verify every internal tensor.

### Y3 — Backbone

- Run layers through SPPF.
- Record feature maps at P3, P4, and P5.
- Measure peak live memory.

### Y4 — Neck

- Add upsampling, skip tensors, concatenation, and downsampling.
- Verify the three detection feature maps.

### Y5 — Detection convolutions

- Execute box and class convolution branches on the NPU.
- Return raw head tensors to RV64 memory.
- Verify that the graph-cut boundary matches the pinned export and has not been
  invalidated by an exporter upgrade.

### Y6 — Host postprocessing

- Decode boxes and run NMS on the RISC-V host.
- Compare selected detections with the host reference.

### Y7 — End-to-end report

- Run at least one image under Spike.
- Record correctness, accuracy, estimated cycles, utilization, and traffic.
- Publish all assumptions and known unsupported behavior.

## YOLO26 follow-up

After Y7:

1. Export fixed-shape YOLO26n with its default one-to-one head.
2. Inventory C2PSA, depthwise convolution, TopK, and Gather.
3. Reuse all common convolutional kernels.
4. Decide whether attention runs on the NPU or as a host fallback.
5. Compare total operations, memory traffic, fallback time, and graph
   complexity with YOLOv8n.

## Licensing boundary

Ultralytics currently documents YOLOv8 and YOLO26 under AGPL-3.0 and
Enterprise licensing. This project should not vendor Ultralytics source,
pretrained weights, or datasets without an explicit license decision.
Download external assets separately and record their source, version, hash,
and applicable license.

## Target-specific logic review

### Finding YL1 — “Run YOLO” was ambiguous

**Severity:** High

**Resolution:** The target now states model, task, input size, batch, graph
format, arithmetic, host/NPU partition, and postprocessing location.

### Finding YL2 — A full detector is too large for first bring-up

**Severity:** High

**Resolution:** YOLO is preceded by exact integer arithmetic, GEMM, the native
command device, compiler, Spike/runtime integration, convolution, and tiny-CNN
gates, in that dependency order.

### Finding YL3 — Official ONNX output is not the desired raw NPU boundary

**Severity:** High

**Resolution:** Preserve an official baseline export and separately generate a
hashed, reviewed deployment partition with exposed head tensors.

### Finding YL4 — The MLP command set is insufficient for YOLO

**Severity:** Medium

**Resolution:** Add SiLU, MaxPool, Resize, and graph-memory operations only
after `v0.1`; version the ABI capability change.

### Finding YL5 — Host fallback can hide accelerator cost

**Severity:** Medium

**Resolution:** Operator reports include node count, MAC coverage, tensor bytes
crossing partitions, and host work. Unsupported work cannot disappear from
performance reporting.

### Finding YL6 — External model assets affect repository licensing

**Severity:** High

**Resolution:** Do not vendor Ultralytics code, weights, images, or datasets
until their licenses are explicitly reviewed and documented.

## Primary references

- [Official YOLOv8 overview](https://docs.ultralytics.com/models/yolov8/)
- [Official YOLOv8 architecture YAML](https://github.com/ultralytics/ultralytics/blob/main/ultralytics/cfg/models/v8/yolov8.yaml)
- [Ultralytics architecture guide](https://docs.ultralytics.com/guides/yolo-architecture/)
- [Official YOLO26 overview](https://docs.ultralytics.com/models/yolo26/)
- [Official YOLO26 architecture YAML](https://github.com/ultralytics/ultralytics/blob/main/ultralytics/cfg/models/26/yolo26.yaml)
- [Ultralytics detection head source](https://github.com/ultralytics/ultralytics/blob/main/ultralytics/nn/modules/head.py)
- [Ultralytics ONNX export guide](https://docs.ultralytics.com/integrations/onnx/)
- [ONNX Runtime quantization guide](https://onnxruntime.ai/docs/performance/model-optimizations/quantization.html)
