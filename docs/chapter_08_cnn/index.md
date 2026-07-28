# Chapter 8: Convolution and tiny CNN

Convolution introduces spatial shapes, padding, stride, channel layout, and
activation fusion. A tiny CNN combines these concerns without the complexity
of a production detector.

## Learning goals

- relate convolution windows to GEMM-like computation;
- track layout and padding through lowering;
- separate NPU-supported work from host fallback;
- use a tiny network as an end-to-end integration gate.

## Progression

```mermaid
flowchart LR
  C["Single convolution"] --> A["Activation / requantization"]
  A --> P["Pooling or reshape"]
  P --> F["Final dense layer"]
  F --> O["Reference comparison"]
```

The tiny CNN is the first checkpoint that exercises multiple operators,
intermediate buffers, and compiler scheduling together.

## Reading path

1. Study [Lesson 6A: convolution](../lessons/03-convolution.md).
2. Continue with [Lesson 6B: tiny CNN](../lessons/06-tiny-cnn.md).
3. Use the [summary and review](review.md) before moving to YOLO.
