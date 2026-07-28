# Chapter 5 summary and review

## Summary

The ABI describes bytes, while the memory model describes what referenced
regions mean during execution. Both are needed for deterministic host/device
interaction.

## Review questions

1. Why should a device validate the entire command envelope before executing it?
2. Which fields allow an older reader to reject an incompatible buffer?
3. When is overlap between input and output memory legal?
4. What is the difference between scratchpad capacity and a global address?
5. How is completion made visible to the host?

## Deferred lab

Serialize one valid buffer and mutate its version, length, opcode, alignment,
and address bounds independently. Confirm that Python and C++ reject the same
cases with stable status codes.
