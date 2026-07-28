# Chapter-book style implementation review

Status: **local and production documentation review passed**

Date: **2026-07-28**

Evidence type: `local_check` plus production deployment observation

Scope: generated MkDocs site for the book-style configuration and original CSS
changes. This is not an NPU implementation review.

## Verdict

No P0 or P1 visual/navigation defect was found. The generated site now presents
the requested persistent chapter pane and continuous scrolling reading layout
while preserving mobile navigation.

## Desktop checks

At a `1280 × 720` viewport:

| Check | Observed |
|---|---|
| Header | Sticky, 64 px high |
| Primary chapter pane | 280 px wide |
| Chapter-pane viewport | 656 px high |
| Chapter content height | 4,200 px |
| Chapter overflow | Independent vertical `auto` scroll |
| Article | 840 px wide and centered |
| Secondary/right sidebar | Not present |
| Chapter groups | Expanded with visible section labels |
| Current page | Blue active row with left accent |
| Current-page headings | Integrated beneath the active page |

The numerical-contract page exposed eleven in-page bookmark links in the left
tree, including Rule provenance, Quantization, Accumulation, Layout, and
Continue reading.

## Mobile checks

At a `390 × 844` viewport:

- the article remained single-column;
- the rendered article width was 343 px;
- no horizontal page overflow was observed;
- the header retained the menu, title, palette, and search controls;
- opening the menu displayed the active chapter, current page, and sibling
  pages in a focused drawer;
- the background overlay and drawer interaction remained intact.

The palette control switched from the default light scheme to the slate scheme
and back. The observed main background changed from `rgb(244, 247, 251)` to
`rgb(17, 23, 34)`, and the active navigation treatment remained distinct.

## Build checks

- `scripts/check_docs.ps1` passed.
- `mkdocs build --strict` passed.
- All new plan/review pages were included in explicit navigation.

## Production observation

- Pull request
  [#2](https://github.com/buicongnguyen/NPU_sw_stack/pull/2) merged the change at
  revision
  [`47897a9`](https://github.com/buicongnguyen/NPU_sw_stack/commit/47897a993a4676dd9a90e7b8bef2a7987c0b96e1).
- GitHub Pages workflow run
  [`30337855340`](https://github.com/buicongnguyen/NPU_sw_stack/actions/runs/30337855340)
  completed successfully.
- The public numerical-contract page returned the deployed stylesheet and
  reproduced the 64 px header, 280 px independently scrolling chapter pane,
  840 px article, integrated bookmarks, and absent right sidebar.
- The public review page and canonical book URL returned successfully.

## Limitations

- Browser rendering was inspected in one Chromium-based surface.
- No Python/C++, WSL, Spike, model, timing, or RTL test was run.
