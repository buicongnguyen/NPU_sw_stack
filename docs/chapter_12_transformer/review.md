# Chapter 12 summary and review

## Summary

A decoder block expands the stack from static spatial workloads to
state-bearing sequence execution. GEMM remains central, but cache traffic,
normalization, and attention require new analysis.

## Review questions

1. Why do prefill and decode have different performance characteristics?
2. Which tensors grow with sequence length?
3. What state must survive between decode steps?
4. Which decoder operations can reuse the existing GEMM path?
5. When is host fallback preferable to a new device opcode?

## Deferred lab

Run one tiny decoder block for prefill and a single decode step. Compare exact
intermediates, KV-cache updates, accelerator coverage, and memory traffic.
