# Glossary

**ABI**
: Application binary interface. Here, the versioned byte-level command format
  shared by compiler, runtime, and NPU model.

**Accumulator**
: A widened value that collects products before requantization.

**Command buffer**
: A serialized header and sequence of operations consumed by the NPU model.

**DMA**
: Direct memory access used to move tensors between global memory and local
  storage without scalar host copies.

**Functional model**
: A model whose primary obligation is correct architectural behavior, not
  cycle accuracy.

**GEMM**
: General matrix multiplication, written conceptually as \(C = A B\).

**Host fallback**
: An operation executed by the RISC-V host because the NPU path does not
  support it.

**KV cache**
: Saved key and value tensors reused during autoregressive Transformer decode.

**Lowering**
: Replacing a high-level graph operation with operations supported by the
  target execution model.

**MMIO**
: Memory-mapped input/output. Device registers are accessed through reserved
  addresses.

**Normative**
: Defining required behavior. A normative contract takes precedence over an
  illustrative example.

**Quantization**
: Mapping real-valued tensors to discrete integer values with explicit scale,
  zero point, rounding, and saturation rules.

**Requantization**
: Converting a wide accumulated value to an output integer representation.

**RTL**
: Register-transfer level hardware description used for detailed digital
  implementation and simulation.

**Scratchpad**
: Explicitly managed on-device local memory.

**Spike**
: A RISC-V instruction-set simulator used to host the bare-metal runtime path.

**Systolic array**
: A regular processing-element array that moves data rhythmically between
  neighboring elements while accumulating results.

**Tiling**
: Partitioning a larger operation into pieces that fit physical compute and
  storage resources.

**WSL**
: Windows Subsystem for Linux, the deferred environment for Linux builds,
  Spike integration, and implementation experiments.
