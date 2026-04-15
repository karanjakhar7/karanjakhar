# DESIGN.md

## Design Goal

The site should feel like a thoughtful personal blog by an engineer: calm, deliberate, readable, and slightly distinctive. It should not feel like a generic startup landing page or a portfolio template.

## Core Principles

- Content first: writing is the product, so layouts should support reading before decoration.
- Quiet confidence: the design should feel warm and composed, not loud or flashy.
- Minimal, not sterile: use restraint, but keep enough texture, contrast, and shape to avoid looking flat.
- Fast by default: no JavaScript unless there is a strong reason.
- Consistent rhythm: spacing, type scale, and card structure should feel systematic across pages.

## Visual Direction

- Palette: warm paper background, deep ink text, teal accent, muted copper highlight.
- Tone: editorial and human, with a small amount of polish from gradients, shadows, and rounded surfaces.
- Contrast: keep body text highly legible; decorative colors should not reduce readability.
- Motion: subtle only. Small hover lifts and simple load-in motion are enough.

## Typography

- Use serif for major headings to create an editorial feel.
- Use sans-serif for body copy, navigation, and UI elements.
- Headlines should feel intentional and spacious, not compressed.
- Body text should optimize for long-form reading: generous line-height, comfortable measure, clear hierarchy.

## Layout Rules

- Keep the main content column narrow on reading pages.
- Use wider layouts only for homepage sections like hero and about.
- Navigation should stay simple and obvious.
- Cards and sections should share the same spacing language and corner radius system.
- Mobile should preserve hierarchy without collapsing into clutter.

## Component Guidance

- Hero: image-led, atmospheric, and text-readable. It should introduce the person and tone quickly.
- About section: personal but concise; image and copy should feel balanced.
- Post lists: title, date, summary, and optional tags are enough.
- Article pages: prioritize title, metadata, and uninterrupted reading flow.
- Footer: simple identity and links, no visual noise.

## Things to Avoid

- Heavy UI chrome or dashboard-like patterns.
- Bright, overly saturated accents.
- Multiple competing accent colors.
- Dense borders or excessive dividers.
- Generic framework aesthetics.
- Adding JS-driven interactions for purely decorative reasons.

## Implementation Notes

- Keep design tokens centralized in `themes/minimal/static/style.css`.
- Prefer evolving the existing token system over hardcoding one-off colors and spacing values.
- Use root-relative links in templates.
- Keep templates semantic and lean; visual complexity should live mostly in CSS.
