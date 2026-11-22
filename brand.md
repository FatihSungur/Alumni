# Brand

This document captures the Alumni project's visual identity — the raw decisions (colors, fonts, logo) that every page should follow. See [DESIGN.md](./DESIGN.md) for how this identity gets applied in practice (components, layout, spacing).

## Name & tone

**Alumni** — a graduate/alumni tracking platform for a university program. The tone is warm but credible: it should feel like a place alumni want to stay connected to, not a dry internal admin tool.

## Color palette

| Role | Color | Hex |
|---|---|---|
| Primary (nav, headings background) | Lilac | `#7c5a94` |
| Primary dark (headings, text accents) | Deep plum | `#4a3359` |
| Accent (buttons, links) | Burgundy | `#7a2048` |
| Logo wordmark | Royal blue | `#003da5` |
| Gold (crown/logo, decorative stripes and frames) | Gold | `#f7d154` |
| Background | Off-white | `#faf7fb` |
| Surface (cards, tables) | White | `#ffffff` |
| Text | Charcoal | `#2e2a30` |
| Border/neutral | Muted gray-lilac | `#b9afc0` |

All of these are defined as CSS custom properties in `static/style.css` (`--color-*`), so every page pulls from the same source instead of hardcoding hex values.

## Typography

Three fonts, each with a specific job — never mixed outside their role:

- **Shrikhand** (`--font-family-display`) — the hero slogan and section headings (`h1`/`h2`/`h3`). A bold, poster-style display font for the handful of places that need real visual weight.
- **Poppins** (`--font-family-heading`) — nav labels and the "Alumni" logo wordmark. Geometric and bold, but still legible at small sizes (Shrikhand is too decorative to read well that small).
- **Lora** (`--font-family-elegant`) — buttons (italic) and short captions (e.g. feature card descriptions). An elegant serif, close to Times New Roman, used anywhere text should feel more "classic" than functional.
- **Inter** (`--font-family`) — the default: longer body paragraphs and anything not covered above.

## Logo

A text wordmark: **"Alumni"** (capital A, rest lowercase) in `--font-family-heading` (Poppins), filled in royal blue (`#003da5`) with a gold text-stroke outline. A gold crown (inspired by Real Madrid's crest — a banded base, five points, a small ball on each tip) sits fused into the upper half of the lettering, as if the letters rise out of/into the crown rather than sitting below a separate badge. Lives in `templates/index.html` as inline SVG (`.logo`, `.logo-sun`, `.logo-text` in `static/style.css`) so it can be colored with the same CSS variables as the rest of the site.

## Decorative accents

A muted-to-vivid gold (`--color-gold`) is used sparingly as a signature accent, never as a primary color: a thin stripe under the nav bar, a divider under the hero slogan, and a top-border accent on feature cards.
