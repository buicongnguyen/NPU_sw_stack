# Chapter 7 summary and review

## Summary

The runtime submits a previously validated artifact and reports completion. A
small adapter connects Spike memory and MMIO events to the shared device model,
avoiding a second implementation of the NPU.

## Review questions

1. Why should graph lowering not occur inside the runtime?
2. What must be written before the submission doorbell?
3. Which memory-ordering assumptions require verification?
4. How should invalid device status reach the application?
5. Why is shared model code important for native-versus-Spike comparisons?

## Deferred lab

Submit the same command buffer through the native adapter and the Spike MMIO
adapter. Compare output bytes, status, and the decoded command trace.
