---
layout: page
title: "Lesson 9: YOLO26n Comparison"
permalink: /lessons/09-yolo26n/
---

# Lesson 9: YOLO26n comparison

## Outcome

Reuse the proven stack to measure how a newer detector changes operator
support, host fallback, memory traffic, and accelerator design pressure.

## Step 1 — Freeze the comparison

Use:

- YOLO26n detection
- Fixed batch 1
- Fixed 320x320 input
- Default one-to-one head
- Same test images and calibration policy used for YOLOv8n

Record model/export revisions because YOLO26 is newer and its implementation
may evolve.

## Step 2 — Compare graph structure

Create a table:

| Feature | YOLOv8n | YOLO26n |
|---|---|---|
| Main block | C2f | C3k2 |
| Attention | None in base config | C2PSA |
| Regression bins | DFL, `reg_max=16` | Direct, `reg_max=1` |
| Default NMS | Required | Not required |
| Final selection | Decode + NMS | TopK/Gather-style postprocess |
| Head convolution | Standard legacy path | Includes depthwise path |

Confirm the table against the pinned exported graphs, not documentation alone.

## Step 3 — Reuse common kernels

Measure how much of the YOLOv8n implementation covers:

- Standard Conv
- Depthwise Conv
- Add
- Concat
- Resize
- MaxPool
- SiLU

This is a software-stack portability measurement.

## Step 4 — Study C2PSA

Inventory the attention block operations and tensor shapes. Compare:

- Host fallback
- Lowering attention MatMul to the existing array
- Adding Softmax support
- Extra memory traffic

Do not add attention instructions until the cost and reuse are understood.

## Step 5 — Study end-to-end selection

The official detection code performs score selection with TopK and gathers the
corresponding boxes. Decide:

- Scalar RV64 implementation
- Vector RVV implementation
- NPU command
- Hybrid approach

Compare this with YOLOv8n DFL decode and NMS host cost.

## Step 6 — Publish the comparison

Report:

- Node/operator counts
- NPU coverage percentage by nodes and MACs
- Host fallback nodes
- Peak live memory
- DRAM traffic
- Estimated NPU cycles
- Host work
- Accuracy delta
- Implementation effort

The conclusion may favor different models for different NPU designs.

## Correctness gate

- Both models use equivalent input and evaluation settings.
- All new operators have reference tests.
- Claims are tied to pinned exports.
- Attention and TopK fallback costs are included.
- Licensing and model provenance are recorded.

## Primary references

- [Official YOLO26 documentation](https://docs.ultralytics.com/models/yolo26/)
- [YOLO26 architecture YAML](https://github.com/ultralytics/ultralytics/blob/main/ultralytics/cfg/models/26/yolo26.yaml)
- [Ultralytics architecture guide](https://docs.ultralytics.com/guides/yolo-architecture/)
- [Ultralytics detection head source](https://github.com/ultralytics/ultralytics/blob/main/ultralytics/nn/modules/head.py)
- [Ultralytics ONNX export guide](https://docs.ultralytics.com/integrations/onnx/)
