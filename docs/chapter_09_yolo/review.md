# Chapter 9 summary and review

## Summary

A fixed YOLOv8n configuration turns the educational stack into a coherent
application study. Supported compute runs on the NPU; decode and NMS can remain
on the host while the accelerator boundary matures.

## Review questions

1. Why must preprocessing be part of the reproducible input contract?
2. Which output should be compared before decode and NMS?
3. How can fallback hide poor accelerator coverage?
4. Which measurements distinguish transfer cost from array execution?
5. Why is YOLO26 a comparison target rather than a replacement mid-project?

## Deferred lab

Capture a fixed model artifact and input set, compare intermediate tensors with
the reference, then report coverage and timing only after all correctness gates
pass.
