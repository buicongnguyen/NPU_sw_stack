# Chapter-book style migration plan

Status: **implemented locally; deployment pending**

Date: **2026-07-28**

Reference inspected:
[`buicongnguyen.github.io/hello-algo/vi/learn/`](https://buicongnguyen.github.io/hello-algo/vi/learn/)

## Objective

Make the NPU book feel like a continuous technical book rather than a generic
documentation portal:

- keep a persistent, independently scrollable chapter tree on desktop;
- show chapter sections and their pages without repeated expansion clicks;
- expose in-page bookmarks through the same left navigation;
- keep the reading column centered and comfortable;
- preserve a compact chapter drawer on phones and tablets.

The result should use this repository's original logo, colors, text, MkDocs
configuration, and CSS. It should not copy HelloAlgo source, prose, images,
fonts, or branded components.

## Observed reference pattern

At the reviewed desktop viewport, the reference presents:

| Element | Approximate behavior |
|---|---|
| Header | Sticky, 64 px high, quiet light surface |
| Chapter pane | About 280 px wide, sticky, independently scrollable |
| Reading column | About 820 px wide with generous margins |
| Chapter groups | Always visible, compact uppercase labels |
| Current page | Blue-tinted row with a strong left accent |
| Page sequence | Previous/next controls after the article |
| Small screens | Menu button replaces the persistent pane |

These observations are design inputs, not copied implementation values.

## Current-site gap

The current MkDocs site already provides a primary navigation tree, right-side
table of contents, search, mobile drawer, and previous/next footer. The main
differences are:

1. chapter groups are collapsed by default;
2. in-page bookmarks occupy a separate right column;
3. system dark preference can make the first visit visually unlike the
   reference;
4. the desktop chapter pane is narrower and visually less distinct;
5. active-page and section hierarchy need stronger book-like treatment.

## Implementation plan

### 1. Navigation behavior

Enable Material for MkDocs features:

- `navigation.sections` for visible chapter group boundaries;
- `navigation.expand` so chapter pages are immediately browsable;
- `toc.integrate` so current-page headings appear as bookmarks inside the left
  tree;
- keep `navigation.footer`, `navigation.top`, and `toc.follow`.

### 2. Reading layout

On desktop:

- allow the main grid to use the viewport width;
- reserve about 14 rem (approximately 280 px) for the chapter pane;
- center the article at a maximum of about 42 rem (approximately 840 px);
- give the chapter pane its own border, background, and scrollbar;
- keep the header sticky and visually quiet.

On smaller screens:

- retain MkDocs' accessible menu button and overlay drawer;
- remove desktop-only borders and fixed widths;
- keep touch targets readable;
- avoid horizontal article overflow.

### 3. Visual hierarchy

- Make light mode the deterministic first palette while retaining a manual dark
  toggle.
- Use small uppercase chapter labels.
- Render links as rounded rows.
- Mark the active page with a blue tint and left inset bar.
- Use a pale reading canvas and white/light article surfaces without copying
  reference branding.

### 4. Validation

1. Run the repository documentation checker.
2. Build with `mkdocs build --strict`.
3. Inspect the home page and a long specification at desktop width.
4. Confirm the left pane scrolls independently.
5. Confirm the active page and integrated heading bookmarks are visible.
6. Inspect the mobile header, drawer trigger, article width, and footer.
7. Publish through a pull request, then inspect the production deployment.

## Non-goals

- Combining all chapters into one generated HTML file
- Copying the reference site's custom framework or CSS
- Changing chapter content, normative contracts, or implementation status
- Running the deferred NPU implementation tests
