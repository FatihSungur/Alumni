# DESIGN.md

A structured design-system spec for the Alumni project, in the spirit of [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md): meant to be read by whoever (human or AI) implements a new page, so every page ends up visually consistent without having to eyeball an existing one. For *why* these choices were made, see [brand.md](./brand.md); this document is about *how* they're applied.

```yaml
version: 1
name: alumni-design
description: >
  Warm-but-credible alumni tracking platform. Lilac/plum as the structural
  color, burgundy and royal blue as accents, a gold crown/stripe as the one
  signature decorative flourish. Three-tier type system: a decorative display
  face for the handful of big moments, a geometric sans for navigation and the
  logo, and an elegant serif for short captions and buttons.
```

## 1. Visual Theme & Atmosphere

Professional enough to represent a university program, warm enough that alumni want to come back. Avoid: corporate-blue SaaS look, excessive whitespace with no color, anything that reads as a generic admin dashboard. Every page should feel like part of the same site as the homepage, not a bare CRUD scaffold bolted onto it.

## 2. Color Palette & Roles

```yaml
colors:
  primary: "#7c5a94"        # lilac — nav background
  primary-dark: "#4a3359"   # headings, logo-adjacent text
  accent: "#7a2048"         # burgundy — buttons, links, primary actions
  accent-dark: "#5c1836"    # hover state for accent
  logo-blue: "#003da5"      # reserved for the wordmark only
  gold: "#f7d154"           # decorative stripes, frames, crown — never body text
  background: "#faf7fb"     # page background
  surface: "#ffffff"        # cards, tables
  text: "#2e2a30"           # body text
  border: "#b9afc0"         # table/card borders, dividers
```

All defined as CSS custom properties in `static/style.css` under `:root` — a new page should reference `var(--color-*)`, never hardcode a hex value.

## 3. Typography Rules

```yaml
typography:
  display:
    fontFamily: "Shrikhand"
    usage: "h1, h2, h3 only — the slogan and section headings"
  heading:
    fontFamily: "Poppins"
    usage: "nav labels, the logo wordmark"
  elegant:
    fontFamily: "Lora"
    usage: "buttons (italic), short captions (e.g. a feature card's one-line description)"
  body:
    fontFamily: "Inter"
    usage: "default — longer paragraphs, table cells, form labels, everything else"
```

Rule of thumb: the more decorative a font is, the shorter and less frequent its job. Shrikhand never appears in a table cell; Inter never carries the hero slogan.

## 4. Spacing & Rounding

```yaml
spacing:
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 48px
rounded:
  sm: 4px
  md: 8px
```

Use the scale, not arbitrary pixel values — `var(--space-md)` instead of `16px` directly, so a future site-wide density change is a one-line edit.

## 5. Component Stylings

```yaml
components:
  nav:
    background: "{colors.primary}"
    borderBottom: "3px solid {colors.gold}"
    linkFont: "{typography.heading}"
  button-primary:
    background: "{colors.accent}"
    backgroundHover: "{colors.accent-dark}"
    textColor: "#ffffff"
    font: "{typography.elegant}"
    fontStyle: italic
    rounded: "{rounded.sm}"
    padding: "{spacing.sm} {spacing.md}"
  card:
    background: "{colors.surface}"
    border: "1px solid {colors.border}"
    borderTop: "4px solid {colors.gold}"
    rounded: "{rounded.md}"
    padding: "{spacing.md}"
  table:
    background: "{colors.surface}"
    border: "1px solid {colors.border}"
    headerBackground: "{colors.primary}"
    headerTextColor: "#ffffff"
    headerFont: "{typography.heading}"
    cellFont: "{typography.body}"
  form-input:
    border: "1px solid {colors.border}"
    rounded: "{rounded.sm}"
    padding: "{spacing.sm}"
    font: "{typography.body}"
```

`table` and `form-input` are the spec for the rollout to the CRUD pages (users, announcements, job postings, applications) — not yet implemented anywhere, but any new page should match this rather than inventing its own look.

## 6. Layout Principles

- Single centered column, `.container` with `max-width: 960px`, `padding: 0 24px` — defined once in `static/style.css`, reused on every page.
- Every page starts with the same `.site-nav` (see `templates/index.html` for the reference markup) so navigation feels identical everywhere.
- Generous vertical spacing between sections (`--space-xl`), tighter spacing within a component (`--space-sm`/`--space-md`).

## 7. Depth & Elevation

Minimal — this is a flat, content-first design, not a shadow-heavy card UI. The only "elevation" cue is the 1px border + gold top-border accent on cards (see `.feature-card`). Don't add `box-shadow` to match a different aesthetic.

## 8. Do's and Don'ts

- **Do** reuse `.btn`, `.container`, `.site-nav` classes from `static/style.css` rather than writing one-off styles per page.
- **Do** keep the gold color decorative only (stripes, frames, the crown) — never as a text color for body copy (fails contrast on the light background).
- **Don't** introduce a new font without a reason tied to one of the four defined roles.
- **Don't** use `-webkit-text-stroke` outside the logo — it's a deliberate one-off effect, not a reusable text style.

## 9. Responsive Behavior

- Breakpoint-free by design so far: `.feature-grid` uses `repeat(auto-fit, minmax(200px, 1fr))` so cards reflow naturally without a media query.
- `.site-nav .container` is `flex-wrap: wrap`, so nav links drop to a second line on narrow screens instead of overflowing.
- No fixed-width elements anywhere except `.container`'s `max-width`.

## Agent prompt guide

When implementing a new page: import `static/style.css`, wrap content in `.container`, reuse `.site-nav`/`.btn`/`.feature-card` where applicable, style any table/form per section 5 above, and never introduce a color or font outside this document without updating it first.
