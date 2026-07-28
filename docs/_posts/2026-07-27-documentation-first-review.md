---
layout: post
title: "Documentation-first checkpoint and logic review"
date: 2026-07-27 03:00:00 +0900
categories: progress
milestone: documentation-review
record_type: local_check
---

## Objective

Make the complete learning path readable and logically reviewable before
installing WSL2 or building Spike.

## Context and assumptions

The project began with a Windows checkout. Git and Python were available, but
a normal Ubuntu WSL distribution, native C++ toolchain, CMake, and Ninja were
not yet available. Docker was present, but the user chose to focus on
documentation and set up WSL later.

## Hypothesis

If architecture boundaries, execution order, workload targets, numerical
rules, ABI bytes, runtime state, and evidence requirements are explicit, then
implementation can proceed through small gates without using YOLO, Transformer,
or Spike as the first debugging environment.

The hypothesis would be rejected if any later milestone were required to define
the semantics of an earlier one.

## Design or implementation

The documentation now separates:

- NumPy numerical truth
- Portable functional NPU behavior
- RISC-V host/device integration in Spike
- Analytical timing estimates
- Later RTL correlation

It selects a two-layer MLP and tiny CNN as full-stack gates, fixed-shape
YOLOv8n as the first application, and keeps Transformer/deformable convolution
as independent advanced branches.

New stable specifications cover:

- Guided reading order
- Architecture and ownership boundaries
- Deferred WSL2/Spike setup
- Command-buffer fields and validation
- MMIO/runtime state and errors
- Compiler passes and deterministic artifacts
- Experiment evidence and publication

## Reproduction

Documentation validation command:

```powershell
./scripts/check_docs.ps1
```

Repository whitespace check:

```powershell
git diff --check
```

## Local check notes

These results are non-reproducible local check notes because the working tree
had no immutable revision or file manifest. At the first full check:

```text
Documentation checks passed for 37 Markdown files.
```

The checker validated front matter, local Markdown targets, Jekyll routes, and
trailing whitespace. The repository was still entirely untracked, so
`git diff --check` produced no useful tracked diff; this limitation is recorded
instead of treating it as evidence.

After adding the static scaffold review, the closing documentation check
reported:

```text
Documentation checks passed for 38 Markdown files.
```

## Measurements

No NPU performance or model-accuracy measurements were produced at this
checkpoint. Any cycle counts in future documents remain estimates until
correlated with RTL.

## Problems and failed approaches

The initial plan mixed an environment decision with an execution claim: Docker
was available, but that did not mean the project build had passed. The status
vocabulary was corrected to distinguish documented, reviewed, scaffolded,
executed, and verified work.

The implementation plan also duplicated command-header and MMIO details. The
duplicates diverged from the detailed ABI drafts. The plan now points to one
language-neutral command ABI and one MMIO/runtime contract.

## Decisions

- Documentation is the current milestone.
- WSL2 installation and all build gates remain deferred.
- A normal Ubuntu WSL2 distribution will be the preferred interactive Linux
  environment.
- Docker remains an optional reproducibility/CI path.
- No code milestone is complete until the stated command has run and evidence
  is saved.
- YOLOv8n remains the first application; YOLO26n is a later comparison.
- Transformer and deformable convolution remain post-foundation branches.

## Next step

Review the documentation from the Start Here page. When ready, execute only
the WSL2 setup gate and publish the actual environment versions before building
the numerical or Spike milestones.

## References

- [Install WSL](https://learn.microsoft.com/en-us/windows/wsl/install)
- [WSL filesystem guidance](https://learn.microsoft.com/en-us/windows/wsl/filesystems)
- [Spike](https://github.com/riscv-software-src/riscv-isa-sim)
- [GitHub Pages publishing source](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)
