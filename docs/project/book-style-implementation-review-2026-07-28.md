# Chapter-book style implementation review

Status: **local documentation review passed; deployment pending**

Date: **2026-07-28**

Evidence type: `local_check`

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

## Limitations

- This check used the locally generated site before publication.
- Browser rendering was inspected in one Chromium-based surface.
- Production CDN behavior and public URLs must be checked after the Pages
  workflow completes.
- No Python/C++, WSL, Spike, model, timing, or RTL test was run.
