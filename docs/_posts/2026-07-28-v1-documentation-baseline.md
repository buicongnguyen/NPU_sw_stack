---
layout: post
title: "V1 documentation release candidate: freezing interfaces before WSL"
date: 2026-07-28 00:00:00 +0900
categories: progress
milestone: D0
record_type: local_check
---

## Objective

Prepare the repository and GitHub Pages source as a readable design release
before installing WSL or running simulator experiments.

## Context and assumptions

The user explicitly deferred WSL setup and experiments. This checkpoint reviews
documentation and local repository structure only. Existing Python/C++ source
files remain scaffolds and are not evidence that an implementation gate passed.

The working tree did not yet have a committed baseline when this post was
written. The documentation-check result below therefore describes the local
working tree, not an immutable Git revision.

## Design work

The site now has:

- A specification map that separates normative contracts, explanations,
  plans, decisions, and evidence
- A guided reading path for the GitHub Pages site
- A memory/execution contract covering guest addresses, submission images,
  command snapshots, scratchpad initialization, atomicity, aliasing, and reset
- A verification plan connecting each contract to future evidence
- Frozen ABI 1.0 command legality, runtime return values, numeric errors,
  reset defaults, counter equations, and compiler scheduling rules
- A source policy that distinguishes moving reading links from immutable
  implementation dependencies

The review also removed contradictions around “one queue” versus one
submission, separate accumulator storage versus scratchpad C tensors, and
generic versus v1 zero-point behavior.

## Reproduction

From the repository root:

```powershell
./scripts/check_docs.ps1
```

## Local check note

Observed on 2026-07-28 in the local Windows working tree:

```text
Documentation checks passed for 42 Markdown files.
```

This is a non-reproducible local check note because no immutable repository
revision or file manifest existed. The check validates front matter, duplicate
permalinks, local file links, Jekyll routes, trailing whitespace, and
unresolved placeholders in public links. It does not build Jekyll, check every
external URL, or prove any runtime component.

## Decisions

- GitHub Pages documentation is the active deliverable.
- The v1 contracts may be reviewed without installing WSL.
- Environment setup, compilation, numerical differential tests, Spike, and
  workloads remain future execution gates.
- No page may present planned test content as observed evidence.

## Next step

Review the site content, publish the `docs/` directory through GitHub Pages
when the repository remote is ready, and keep implementation statuses
unverified. WSL work resumes only after the user provides an environment
update.

## References

- [Specification map](../specification-status.md)
- [Architecture walkthrough](../architecture.md)
- [Memory and execution model](../memory-execution-model.md)
- [Verification plan](../verification-plan.md)
- [Publishing workflow](../publishing.md)
