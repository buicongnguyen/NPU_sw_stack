---
layout: post
title: "Target decision: simple operators first, YOLOv8n as the first detector"
date: 2026-07-27 01:00:00 +0900
categories: progress
milestone: phase-0
record_type: decision
---

## Question

Should the project goal be simple operations, YOLOv8, or YOLO26?

## Decision

Simple operations are mandatory verification stages. YOLOv8n detection is the
first complete application goal. YOLO26n is a follow-up comparison.

## Reasoning

YOLOv8n is primarily convolutional and allows the initial NPU to focus on
INT8 convolution, activation, residual addition, concatenation, pooling, and
upsampling. DFL box decoding and NMS can run on the RISC-V host.

YOLO26n removes DFL and supports an NMS-free one-to-one head, but it adds a
C2PSA attention block, depthwise head operations, and TopK/Gather-style final
selection. That makes it a useful test of extensibility after the convolutional
stack works.

## Fixed first target

```text
model: YOLOv8n detection
input: 1x3x320x320 NCHW
batch: 1
NPU: signed INT8 with INT32 accumulation
host: RV64 under Spike
postprocessing: host DFL decode and NMS
```

## Implication

The roadmap is now a course with explicit gates:

```text
numerics -> GEMM -> Conv -> compiler -> Spike -> tiny CNN -> YOLOv8n
```

YOLO is not allowed to bypass the smaller correctness stages.

> **Follow-up (2026-07-28):** The dependency review found that this original
> sequence asked the convolution lesson to use compiler machinery before the
> compiler existed. The canonical course now inserts the command/native-device
> and compiler/runtime gates before convolution:
> `baseline -> integers -> GEMM -> commands/native device -> compiler ->
> runtime/Spike -> convolution -> tiny CNN -> YOLOv8n`. See the
> [content and logic review](../project/content-logic-review-2026-07-28.md).

## References

- [YOLOv8 documentation](https://docs.ultralytics.com/models/yolov8/)
- [YOLOv8 architecture](https://github.com/ultralytics/ultralytics/blob/main/ultralytics/cfg/models/v8/yolov8.yaml)
- [YOLO26 documentation](https://docs.ultralytics.com/models/yolo26/)
- [YOLO26 architecture](https://github.com/ultralytics/ultralytics/blob/main/ultralytics/cfg/models/26/yolo26.yaml)
