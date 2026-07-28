---
layout: page
title: Progress Journal
permalink: /progress/
---

# Progress journal

The journal records decisions and evidence, not only successful outcomes.
Failed experiments are useful when they include enough information to be
reproduced.

Every post declares `record_type`:

- `decision` for scope or design choices
- `local_check` for disclosed, non-reproducible working-tree checks
- `observation` only for results tied to an immutable revision/file manifest
  and artifact hashes

## Entry format

Each entry should include:

1. Objective
2. Context and assumptions
3. Design or implementation
4. Commands used
5. Test evidence
6. Measurements
7. Problems and failed approaches
8. Decisions
9. Next step

## Entries

- [2026-07-28 — GitHub repository and Pages publication observed](_posts/2026-07-28-github-pages-publication.md)
  (`observation`)
- [2026-07-28 — V1 documentation baseline](_posts/2026-07-28-v1-documentation-baseline.md)
  (`local_check`)
- [2026-07-27 — Documentation-first review](_posts/2026-07-27-documentation-first-review.md)
  (`decision`)
- [2026-07-27 — Project kickoff](_posts/2026-07-27-project-kickoff.md)
  (`decision`)
- [2026-07-27 — YOLO target decision](_posts/2026-07-27-yolo-target-decision.md)
  (`decision`)
- [2026-07-27 — Transformer and deformable-convolution branches](_posts/2026-07-27-transformers-and-deformable-conv.md)
  (`decision`)

## Writing a new entry

1. Copy `docs/_drafts/progress-entry-template.md`.
2. Name the copy `docs/_posts/YYYY-MM-DD-short-title.md`.
3. Fill every applicable section.
4. Replace claims such as “works” with commands and observed results.
5. Preview the site or inspect the Markdown.
6. Commit the entry with the code or experiment it describes.
