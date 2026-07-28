# Chapter 6 summary and review

## Summary

Compilation is a sequence of checked transformations. Every stage preserves
enough metadata for the next stage and emits a command stream that can be
validated without trusting compiler internals.

## Review questions

1. Why must shape inference happen before tiling?
2. Which information is lost if quantization metadata is treated as an annotation?
3. What is the difference between lowering an operator and scheduling it?
4. Why should emitted commands be read back by an independent validator?
5. Which compiler failures should never become runtime failures?

## Deferred lab

Compile the smallest supported MLP, inspect the serialized bytes, and compare
the decoded command sequence with the expected graph order and memory plan.
