# Chapter 8 summary and review

## Summary

Convolution extends the GEMM foundation with spatial indexing and layout
semantics. The tiny CNN proves that several lowered operations and intermediate
lifetimes compose correctly.

## Review questions

1. Which convolution parameters alter output shape?
2. Why is tensor layout a compiler/device contract?
3. What makes im2col simple but potentially expensive?
4. Which intermediate tensors are candidates for scratchpad reuse?
5. What must match before the tiny CNN checkpoint passes?

## Deferred lab

Compare direct reference convolution with its lowered NPU sequence on boundary
padding and partial-channel cases, then run the complete tiny CNN.
