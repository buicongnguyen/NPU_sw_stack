---
layout: post
title: GitHub repository and Pages publication observed
date: 2026-07-28
categories: [progress, documentation]
record_type: observation
---

# GitHub repository and Pages publication observed

## Objective

Record the first public repository and documentation deployment as reproducible
project evidence without implying that the NPU implementation works.

## Immutable context

- Repository: <https://github.com/buicongnguyen/NPU_sw_stack>
- Reviewed source revision:
  [`3b08e96a591707823c7f5b57c0d7457f2513d834`](https://github.com/buicongnguyen/NPU_sw_stack/commit/3b08e96a591707823c7f5b57c0d7457f2513d834)
- Documentation workflow:
  [`30335780398`](https://github.com/buicongnguyen/NPU_sw_stack/actions/runs/30335780398)
- Published site: <https://buicongnguyen.github.io/NPU_sw_stack/>

## Observed results

The GitHub Actions run completed both jobs successfully:

1. `build` checked out the revision, installed pinned top-level documentation
   dependencies, ran the repository checker, built MkDocs in strict mode,
   configured Pages, and uploaded the site artifact.
2. `deploy` published that artifact to the `github-pages` environment.

The production URL returned HTTP 200 and displayed the `From Graph to NPU`
homepage. Desktop and narrow responsive layouts were inspected in the browser.

## What this proves

- The referenced documentation revision builds and deploys through the declared
  GitHub Pages workflow.
- The public repository and chapter book are reachable at the recorded URLs.

## What this does not prove

- Python or C++ numerical correctness
- Docker, WSL, or sanitizer behavior
- Compiler, runtime, MMIO, Spike, YOLO, Transformer, or DeformConv execution
- Timing accuracy or RTL correlation

Those implementation claims remain deferred.

## Next step

Apply the [post-deployment logic review](../project/post-deployment-logic-review-2026-07-28.md)
and [post-deployment static code review](../project/post-deployment-code-review-2026-07-28.md),
then begin executable review only after WSL is ready.
