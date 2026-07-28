# Chapter-book style logic review

Status: **reviewed; implementation approved**

Date: **2026-07-28**

Scope: proposed visual/navigation migration from the current MkDocs layout to a
book-oriented interface inspired by the observed
[HelloAlgo learning page](https://buicongnguyen.github.io/hello-algo/vi/learn/).

## Verdict

No P0 or P1 blocker was found. MkDocs Material already owns the required
semantics—persistent navigation, integrated page headings, mobile drawer,
search, and previous/next links—so the change can remain a theme configuration
and original-CSS update.

## Findings and resolutions

### B1 — The requested chapter pane already exists but is too collapsed

**Finding:** The current left navigation lists chapters but hides most page
links until each group is expanded.

**Resolution:** Enable `navigation.sections` and `navigation.expand`. The long
tree remains usable because its scroll container is independent from the
article.

### B2 — Two sidebars compete with reading width

**Finding:** The primary chapter tree and secondary page TOC leave a narrow
central column at typical laptop widths.

**Resolution:** Enable `toc.integrate`, moving current-page headings into the
left tree and eliminating the persistent right column.

### B3 — Reference similarity must not become source copying

**Finding:** The reference has custom presentation, content, artwork, and
branding that are outside this project's ownership.

**Resolution:** Reuse only general layout behavior. Keep the existing original
NPU logo, palette identity, Markdown, and CSS implementation.

### B4 — Default theme choice should be deterministic

**Finding:** Media-query palettes make the first render follow operating-system
dark mode, while the requested reference is a light reading surface.

**Resolution:** Put the light palette first without a media condition and keep
dark mode as an explicit user toggle.

### B5 — A fully expanded tree can become visually noisy

**Finding:** Seventy-eight pages create a long navigation pane.

**Resolution:** Use compact section labels, restrained spacing, a visible
active-row treatment, and an independent scrollbar. Do not remove pages or
hide the reader's location.

### B6 — Desktop CSS must not break the mobile drawer

**Finding:** Fixed widths, borders, or viewport-height calculations can leak
into the overlay drawer.

**Resolution:** Apply persistent-pane geometry only at the desktop breakpoint.
Let Material retain drawer positioning and interaction below it.

### B7 — Integrated bookmarks must remain understandable

**Finding:** Page headings nested under the active page can be confused with
chapter pages if hierarchy is weak.

**Resolution:** Indent nested links, reduce their size, and retain active
heading tracking through `toc.follow` and `navigation.tracking`.

### B8 — Style deployment does not validate implementation code

**Finding:** A successful visual deployment is documentation evidence only.

**Resolution:** Do not run or change Python/C++/WSL/Spike verification status.

## Acceptance checks

- All chapter sections and page links are visible in the desktop pane.
- The pane scrolls independently while the article scrolls normally.
- In-page headings appear beneath the active page.
- The reading column remains approximately 40–44 rem wide.
- Light mode is the deterministic initial theme; dark mode still works.
- Mobile keeps its menu button and single-column article.
- Search, edit, top, and previous/next controls remain reachable.
- Strict MkDocs and repository documentation checks pass.
