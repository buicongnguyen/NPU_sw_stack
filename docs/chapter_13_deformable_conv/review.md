# Chapter 13 summary and review

## Summary

Deformable convolution changes a regular access pattern into coordinate-driven
sampling. It is therefore a useful test of the boundary between programmable
fallback and accelerator specialization.

## Review questions

1. Which tensors define each sample location?
2. How are coordinates outside the feature map handled?
3. Why does bilinear interpolation require multiple source reads?
4. What makes these reads difficult for a regular systolic dataflow?
5. What evidence would justify specialized gather support?

## Deferred lab

Create small hand-checkable offset cases, including fractional and boundary
coordinates. Compare a scalar reference with each proposed lowering path before
measuring performance.
