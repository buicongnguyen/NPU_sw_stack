---
layout: page
title: Executable Milestone Plan
permalink: /execution-plan/
---

# Executable milestone plan

This page converts the architecture roadmap into commands, files, tests, and
evidence. A milestone is complete only when its exit command succeeds from a
clean checkout.

Execution status: **documentation release active; E0 and later execution
deferred by user decision**. The files and commands below are the reviewed
implementation contract, not evidence that a gate passed. Follow the
[WSL2 setup guide](setup-wsl.md) when execution resumes.

## Last audited execution environment

Audited on 2026-07-27:

This is a historical observation, not a claim about the reader's current
machine. The environment has not been re-audited because setup and experiments
are deferred until the user provides an update.

| Capability | Result | Decision |
|---|---|---|
| Git | Available | Local repository initialized on `main` |
| Python | 3.13.5 | Run Python tools and tests locally |
| NumPy | 2.2.6 | Pin project dependencies before release |
| Native C++ compiler | Not installed | Defer until normal Ubuntu WSL2 setup |
| CMake/Ninja on host | Not installed | Install inside WSL2 later |
| WSL Linux distribution | Only `docker-desktop` | Install normal Ubuntu later |
| Docker | Client/server 29.6.1 | Available fallback, not the current focus |

An initial C++ container file exists, but it has not passed the E0 exit gate.
Once WSL2 is available, prefer a Linux-native build and keep Docker as an
optional CI/reproducibility path. Spike remains unpinned until E5 selects and
records a reviewed full commit.

## Status vocabulary

- `planned`: documented but implementation has not started.
- `in progress`: files exist but the exit gate is not green.
- `complete`: exit gate passed and evidence is recorded.
- `blocked`: a named external dependency prevents meaningful progress.

## Evidence convention

Human explanations live in dated posts under `docs/_posts/`. Machine-readable
results live under:

```text
out/evidence/<milestone>/
```

The `out/` tree is generated and ignored by Git. A small, reviewed result may
be copied to `docs/assets/data/` only when its generating command and Git
revision are documented.

Every evidence manifest should contain:

```json
{
  "milestone": "E1",
  "git_revision": "working-tree or commit SHA",
  "command": "...",
  "environment": {},
  "seed": 0,
  "tests": {},
  "artifacts": {}
}
```

## D0 — Readable documentation release

Status: **published**

Deliverables:

- GitHub Pages home and guided reading path
- Specification/authority map
- Architecture, numerical, command, memory/execution, MMIO/runtime, compiler,
  and verification contracts
- Reviewed milestone plan, risks, workload decisions, lessons, references, and
  publication instructions
- Clear labels separating project decisions, external baselines, planned
  evidence, and observations

Exit command:

```powershell
./scripts/check_docs.ps1
```

Exit gate:

- Local links and MkDocs navigation resolve.
- No unexplained owner/repository placeholder appears in a public link.
- Normative documents do not contradict one another.
- Every implementation claim remains labeled unverified until an execution
  manifest exists.
- The Pages source can be published from `docs/` without WSL or experiment
  setup.

## E0 — Reproducible foundation

Status: **scaffolded, execution deferred**

### Deliverables

```text
CMakeLists.txt
pyproject.toml
requirements-dev.txt
tools/docker/Dockerfile
docs/setup-wsl.md
scripts/bootstrap.ps1
scripts/build.ps1
scripts/test.ps1
scripts/common.ps1
scripts/test_native_command.ps1
.github/workflows/ci.yml
```

### Commands

Current Windows/Docker scaffold:

```powershell
./scripts/bootstrap.ps1
./scripts/build.ps1
./scripts/test.ps1 -Group tooling
./scripts/test.ps1
```

When WSL execution begins, add and document a Linux-native bootstrap/build/test
entry point instead of requiring a PowerShell-to-Docker round trip.

### Exit gate

- Python environment is created from pinned requirements.
- Native WSL C++ build passes.
- Docker C++ image and smoke test pass if Docker is advertised as a supported
  path; Docker is not required to begin the WSL learning path.
- C++ smoke test runs in every environment claimed as supported.
- Python smoke test runs.
- Documentation check passes.
- Commands are safe to run repeatedly.

### Required article

`Phase 0: reproducible Python and C++ build`

## E1 — Exact INT8 numerical contract

Status: **scaffolded, execution deferred**

### Deliverables

```text
python/npu_lab/numerics.py
include/npu/numerics.h
src/numerics.cpp
tests/python/test_numerics.py
tests/cpp/test_numerics.cpp
tests/fixtures/numerics/
docs/numerical-contract.md
```

### Required functions

- Saturating INT8 cast
- Round-to-nearest, ties-to-even
- Symmetric quantize/dequantize
- INT8 dot product with INT32 accumulation
- Fixed-point requantization
- Reference GEMM

### Tests

- Named boundaries around `-128`, `127`, and INT32 limits
- Positive and negative rounding ties
- Zero-length rejection where applicable
- At least 1,000 seeded random cases
- Shared golden vectors consumed by Python and C++

### Exit gate

```powershell
./scripts/test.ps1 -Group numerics
```

Python and C++ must produce byte-identical golden output.

## E2 — Versioned command ABI

Status: **design documented; implementation planned**

### Deliverables

```text
docs/command-abi.md
docs/mmio-runtime.md
docs/lessons/03-commands-memory.md
include/npu/abi.h
src/abi.cpp
python/npu_lab/abi.py
tests/fixtures/abi/
tests/python/test_abi.py
tests/cpp/test_abi.cpp
```

### Version 1 commands

- `DMA_LOAD`
- `DMA_STORE`
- `GEMM_I8_I8_I32`
- `ADD_BIAS_I32`
- `RELU_I32`
- `REQUANTIZE_I32_I8`
- `BARRIER`
- `END`

### Rules

- Little-endian explicit encoding
- Fixed-width fields
- 16-byte command alignment
- Reserved fields written as zero
- Checked address-plus-size arithmetic
- Unknown opcode/version rejection
- No native-struct serialization

### Exit gate

```powershell
./scripts/test.ps1 -Group abi
```

Python and C++ parse the same golden buffers and reject the same malformed
buffers.

## E3 — Native functional NPU

Status: **design documented; implementation planned**

### Deliverables

```text
include/npu/model.h
src/model.cpp
tools/npu_native.cpp
python/npu_lab/reference_model.py
tests/cpp/test_model.cpp
tests/python/test_reference_model.py
```

### Model state

- Guest-memory callback or byte array
- 64 KiB scratchpad
- Busy/complete/error status
- Deterministic counters
- Structured error code and failing command index

### Counter fields

- MACs
- Estimated cycles
- DRAM read/write bytes
- Command count
- Derived array utilization in the evidence manifest

Functional output must not change when timing parameters change.

### Exit gate

```powershell
./scripts/test.ps1 -Group native-model
```

A handcrafted command buffer performs:

```text
DMA_LOAD A/B/bias
-> GEMM_I8_I8_I32
-> ADD_BIAS_I32
-> RELU_I32
-> REQUANTIZE_I32_I8
-> DMA_STORE
-> END
```

and matches the integer reference.

## E4 — Tiny graph compiler and two-layer MLP

Status: **design documented; implementation planned**

### Deliverables

```text
python/npu_lab/compiler.py
python/npu_lab/cli.py
workloads/mlp/two_layer.json
tests/python/test_compiler.py
tests/end_to_end/test_mlp.py
```

### Compiler stages

```text
JSON parse
-> schema validation
-> static shape inference
-> tensor lifetime analysis
-> scratchpad allocation
-> command scheduling
-> binary emission
-> disassembly
```

### Exit gate

```powershell
./scripts/test.ps1 -Group mlp
```

One command generates deterministic inputs, golden output, guest memory,
command bytes, disassembly, and result manifest. The C++ native runner and
Python reference model agree exactly.

## E5 — Spike and RV64 runtime

Status: **planned**

### Risk-reduction order

1. Build pinned Spike and RV64 compiler in Linux container.
2. Run RV64 hello world.
3. Load minimal MMIO plug-in.
4. Prove guest-memory read/write.
5. Implement driver registers and fences.
6. Attach the existing portable NPU model.

### Deliverables

```text
third_party/manifest.cmake
simulators/spike_plugin/
runtime/include/npu_runtime.h
runtime/baremetal/
firmware/linker/
tests/spike/
```

### Exit gate

```powershell
./scripts/test.ps1 -Group spike
```

The RV64 application submits the E4 command buffer under Spike and prints the
same output hash and counter values as the native runner.

If Spike guest-memory access is unsuitable, document the failed proof and use
a bounded shared-memory aperture for ABI version 1.

## E6 — Tiny CNN

Status: **planned**

Add Conv2D, BatchNorm folding, SiLU, residual Add, and a small multi-layer
network. This is the first complete convolutional stack gate.

Exit command:

```powershell
./scripts/test.ps1 -Group tiny-cnn
```

## E7 — YOLOv8n

Status: **planned**

Follow [Lesson 7](lessons/07-yolov8n.md). Preserve the
official fixed-shape ONNX baseline and generate a separate, hashed deployment
partition.

Sub-gates:

```text
Y0 host baseline
Y1 first Conv
Y2 one C2f block
Y3 backbone
Y4 neck
Y5 raw detection heads
Y6 RV64 decode/NMS
Y7 end-to-end report
```

Exit command after all sub-gates:

```powershell
./scripts/test.ps1 -Group yolov8n
```

## E8 — Advanced branches

Status: **planned**

Independent branches after the common stack:

- RTL correlation
- YOLO26n comparison
- Tiny Transformer decoder
- Deformable convolution
- Linux/QEMU driver

Each branch has its own lesson and must not silently expand an earlier exit
gate.

## Per-change workflow

For each smallest verifiable change:

1. Update the status and acceptance test here.
2. Add a failing test.
3. Implement the smallest behavior.
4. Run the focused test.
5. Run all earlier milestone gates.
6. Run `./scripts/check_docs.ps1`.
7. Write or update a progress article with observed output.
8. Review ABI, bounds, determinism, and performance claims.
9. Commit code and evidence together after user approval or explicit publish
   request.

## Execution order rule

Never implement a later application operator to bypass an earlier red gate.
For example:

- Do not debug YOLO quantization before scalar rounding tests pass.
- Do not debug Spike before the native command model passes.
- Do not add FlashAttention before explicit attention is correct.
- Do not add a deformable gather engine before host fallback semantics pass.
