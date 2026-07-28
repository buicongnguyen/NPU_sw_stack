# Chapter 1 summary and review

## Summary

The graph-to-NPU path is intentionally layered. Each layer has a small,
testable responsibility, and serialized boundaries prevent host and device
assumptions from drifting silently.

## Review questions

1. Which layer decides whether an operator is supported?
2. Which layer decides how a supported operator is tiled?
3. Why should the Spike path reuse the native functional model?
4. What information belongs in a command buffer rather than in host pointers?
5. Which downstream components are affected by a numerical-contract change?

## Design exercise

Draw the ownership chain for one tensor from graph input to device scratchpad.
Mark every point at which shape, address, scale, or lifetime is validated. Save
the result for comparison after the runtime lab is available.
