---
name: Salesforce Release Intelligence
description: Automated pipeline for extracting and classifying Salesforce Release Notes — MkDocs Material docs, interactive dashboard, REST/GraphQL API
colors:
  primary: "#6750A4"
  primary-container: "#EADDFF"
  on-primary: "#FFFFFF"
  on-primary-container: "#21005D"
  secondary: "#625B71"
  secondary-container: "#E8DEF8"
  on-secondary: "#FFFFFF"
  on-secondary-container: "#1D192B"
  tertiary: "#7D5260"
  tertiary-container: "#FFD8E4"
  on-tertiary: "#FFFFFF"
  on-tertiary-container: "#31111D"
  error: "#BA1A1A"
  error-container: "#FFDAD6"
  on-error: "#FFFFFF"
  on-error-container: "#410002"
  background: "#FDF7FF"
  on-background: "#1C1B1F"
  surface: "#FDF7FF"
  on-surface: "#1C1B1F"
  surface-variant: "#E7E0EC"
  on-surface-variant: "#49454F"
  outline: "#79747E"
  outline-variant: "#CAC4D0"
  shadow: "#000000"
  scrim: "#000000"
  inverse-surface: "#313033"
  inverse-on-surface: "#F4EFF4"
  inverse-primary: "#D0BCFF"
  primary-fixed: "#EADDFF"
  primary-fixed-dim: "#D0BCFF"
  on-primary-fixed: "#21005D"
  on-primary-fixed-variant: "#4F378B"
  secondary-fixed: "#E8DEF8"
  secondary-fixed-dim: "#CCC2DC"
  on-secondary-fixed: "#1D192B"
  on-secondary-fixed-variant: "#4A4458"
  tertiary-fixed: "#FFD8E4"
  tertiary-fixed-dim: "#EFB8C8"
  on-tertiary-fixed: "#31111D"
  on-tertiary-fixed-variant: "#633B48"
  surface-dim: "#DDD8DE"
  surface-bright: "#FDF7FF"
  surface-container-low: "#F5EEFA"
  surface-container: "#EFE9F5"
  surface-container-high: "#E9E3EF"
  surface-container-highest: "#E4DEEA"
typography:
  display:
    fontFamily: "'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
    fontSize: "3.5rem"
    fontWeight: 400
    lineHeight: 1.1
    letterSpacing: "-0.02em"
  headline:
    fontFamily: "'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
    fontSize: "2.5rem"
    fontWeight: 400
    lineHeight: 1.2
    letterSpacing: "0em"
  title:
    fontFamily: "'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
    fontSize: "1.75rem"
    fontWeight: 500
    lineHeight: 1.3
    letterSpacing: "0em"
  body:
    fontFamily: "'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: "0.01em"
  label:
    fontFamily: "'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
    fontSize: "0.875rem"
    fontWeight: 500
    lineHeight: 1.5
    letterSpacing: "0.05em"
    textTransform: "uppercase"
  mono:
    fontFamily: "'Roboto Mono', 'Fira Code', 'JetBrains Mono', monospace"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: 1.6
    letterSpacing: "0em"
rounded:
  sm: "4px"
  md: "8px"
  lg: "12px"
  xl: "16px"
  full: "9999px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "24px"
  xl: "32px"
  xxl: "48px"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    rounded: "{rounded.md}"
    padding: "10px 24px"
    typography: "{typography.label}"
  button-primary-hover:
    backgroundColor: "{colors.primary-fixed-dim}"
    textColor: "{colors.on-primary-fixed}"
  button-secondary:
    backgroundColor: "{colors.secondary-container}"
    textColor: "{colors.on-secondary-container}"
    rounded: "{rounded.md}"
    padding: "10px 24px"
    typography: "{typography.label}"
  button-secondary-hover:
    backgroundColor: "{colors.secondary-fixed-dim}"
  button-outlined:
    backgroundColor: "transparent"
    textColor: "{colors.primary}"
    rounded: "{rounded.md}"
    padding: "10px 24px"
    border: "1px solid {colors.outline}"
    typography: "{typography.label}"
  card-elevated:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.lg}"
    padding: "{spacing.md}"
    shadow: "0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06)"
  card-outlined:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.lg}"
    padding: "{spacing.md}"
    border: "1px solid {colors.outline-variant}"
  input-field:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.md}"
    padding: "12px 16px"
    border: "1px solid {colors.outline}"
    typography: "{typography.body}"
  input-field-focus:
    border: "2px solid {colors.primary}"
    boxShadow: "0 0 0 3px {colors.primary-container}"
  nav-tab:
    backgroundColor: "{colors.surface-variant}"
    textColor: "{colors.on-surface-variant}"
    rounded: "{rounded.md}"
    padding: "8px 16px"
    typography: "{typography.label}"
  nav-tab-active:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
  heatmap-cell:
    rounded: "{rounded.sm}"
    typography: "{typography.mono}"
  stat-card:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.lg}"
    padding: "{spacing.md}"
    textAlign: "center"
  banner-hero:
    rounded: "{rounded.md}"
    shadow: "0 2px 8px rgba(0,0,0,0.15)"
---

# Design System: Salesforce Release Intelligence

## Overview

**Creative North Star: "The Technical Archive"**

This design system serves a **Read-mode** product: the visitor's success is *understanding* — comprehending release scope, finding specific features, comparing versions, and tracking feature evolution. The aesthetic is deliberately restrained: a technical reference that feels like a well-maintained archive. Dense information is organized, not decorated.

The MkDocs Material foundation provides battle-tested accessibility, responsive behavior, and search — we layer only what the product needs: a randomized hero banner, enhanced search with Salesforce terminology synonyms, and an interactive dashboard with tabs, tables, and a confidence heatmap.

**Key Characteristics:**
- Material 3 color system (deep purple primary, amber accent) — semantic, not decorative
- Roboto type stack — system-native, highly legible at density
- 8px base spacing rhythm — consistent across docs, dashboard, API responses
- Elevation via subtle shadows (1–3px) and tonal containers — flat by default, depth on interaction
- Rounded corners at 8px (cards), 4px (chips/heat cells), 12px (containers) — gentle, not pill-shaped
- Interactive states communicate through color shifts, not motion — hover = container color, focus = primary ring

## Colors

Material 3 tonal palette with deep purple primary (`#6750A4`) and amber accent — chosen for technical credibility, not brand expression. The full tonal ramp (primary-fixed → on-primary-fixed-variant) enables automatic light/dark theming via MkDocs Material's `scheme: default` / `scheme: slate` toggle.

### Primary
- **Deep Technical Purple** (`#6750A4`): Primary actions, active nav tabs, focus rings, dashboard stat numbers, heatmap high-confidence hue anchor. Used sparingly — ≤10% of any screen — as the "one voice" of action.

### Secondary
- **Muted Purple-Gray** (`#625B71`): Secondary actions, outlined buttons, supporting UI chrome. De-emphasized by default.

### Tertiary
- **Warm Berry** (`#7D5260`): Tertiary accents, heatmap mid-range, occasional highlight. Rare — reserved for semantic "warmth" in data viz.

### Neutral
- **Cool White** (`#FDF7FF` / `background`): Page background, surface base.
- **Deep Charcoal** (`#1C1B1F` / `on-background`): Primary body text.
- **Surface Variant** (`#E7E0EC` / `surface-variant`): Inactive tab backgrounds, table headers, filter chips, input borders at rest.
- **On Surface Variant** (`#49454F` / `on-surface-variant`): Secondary text, placeholder text, inactive icons.
- **Outline** (`#79747E`): Input borders, card outlines, table dividers.
- **Outline Variant** (`#CAC4D0`): Subtle dividers, disabled borders.

### Named Rules
**The One Voice Rule.** The primary accent (`#6750A4`) appears on ≤10% of any given screen — stat numbers, active tab, focus ring, primary button. Its rarity is the signal.

**The Semantic Heatmap Rule.** Heatmap cells use HSL hue interpolation (green → red) for confidence, *not* the primary/secondary/tertiary palette. Dataviz color is independent of UI color.

**The Dark Mode Parity Rule.** All tokens have light/dark variants via Material 3 tonal palettes. No manual dark overrides — the scheme toggle handles inversion.

## Typography

**Display Font:** Roboto (system fallback: -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif)
**Body Font:** Roboto (same stack)
**Label/Mono Font:** Roboto Mono (fallback: Fira Code, JetBrains Mono, monospace)

**Character:** Roboto is the Material reference — neutral, highly legible at small sizes, available everywhere. Roboto Mono for code, data tables, heatmap values. No custom fonts to load; zero layout shift.

### Hierarchy
- **Display** (400, 3.5rem/56px, 1.1, -0.02em): Page hero only (dashboard title, docs h1). Rare.
- **Headline** (400, 2.5rem/40px, 1.2): Section headers in docs, dashboard panel titles.
- **Title** (500, 1.75rem/28px, 1.3): Card titles, category names, release names.
- **Body** (400, 1rem/16px, 1.5, 0.01em): All prose, table cells, search results, API descriptions. Max line length 65–75ch via MkDocs Material container.
- **Label** (500, 0.875rem/14px, 1.5, 0.05em, uppercase): Buttons, tabs, filter labels, stat labels, navigation.
- **Mono** (400, 0.875rem/14px, 1.6): Heatmap cell values, code snippets, JSON exports, CSV columns, feature IDs.

### Named Rules
**The Density-First Rule.** Body at 16px/1.5 line-height enables dense tables without crowding. Never increase body size for "readability" — increase container width instead.

**The Uppercase Label Rule.** All interactive labels (buttons, tabs, selects) use `text-transform: uppercase` with 0.05em tracking. This distinguishes action from content at a glance.

## Layout

**Grid:** MkDocs Material's 76.8rem (1228.8px) max container with 1.5rem side gutters. Dashboard uses 1100px max container for tighter data density.

**Spacing Rhythm:** 8px base unit (`spacing.sm`). All padding, margins, gaps are multiples: 4, 8, 16, 24, 32, 48. No magic numbers.

**Breakpoints** (inherited from Material):
- `< 600px`: Mobile — stacked tabs, single-column tables (horizontal scroll), banner full-width
- `600–900px`: Tablet — two-column stats, tabs horizontal
- `> 900px`: Desktop — three+ stat cards, full dashboard, side navigation

**Density:** High. Tables use 8px vertical padding, 10px horizontal. Cards 16px. Stats 16px gap. The dashboard fits 500 rows in a 500px scrollable card.

**Responsive Behavior:**
- Hero banner: `max-width: 960px`, centered, `border-radius: 8px`, fades in
- Tabs: flex-wrap on mobile, equal-width on desktop
- Tables: `overflow-x: auto` with sticky headers
- Heatmap: `grid-template-columns: repeat(auto-fill, minmax(40px, 1fr))` — cells shrink to 40px minimum

## Elevation & Depth

**Philosophy:** Flat by default. Depth appears only as response to state (hover, focus, active) or to separate overlapping surfaces (cards over page). No ambient shadows on static content.

### Shadow Vocabulary
- **Card Rest** (`0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06)`): Default card elevation (`card-elevated`).
- **Card Hover** (`0 4px 12px rgba(0,0,0,0.12)`): Table row hover, card hover — subtle lift.
- **Banner** (`0 2px 8px rgba(0,0,0,0.15)`): Hero banner only — slightly deeper to ground the random image.
- **Focus Ring** (`0 0 0 3px {colors.primary-container}`): Keyboard focus on inputs, buttons, links — high contrast, primary-tinted.
- **Dropdown/Overlay** (`0 8px 24px rgba(0,0,0,0.16)`): Not currently used; reserved for future menus.

### Named Rules
**The Flat-By-Default Rule.** Surfaces are flat at rest. Shadows appear only as response to state (hover, focus, active) or to separate overlapping surfaces. No "card shadow" as decoration.

**The Focus Ring Is Primary Rule.** All keyboard focus uses the primary container color (`#EADDFF` light / `#D0BCFF` dark) at 3px spread. Never the default browser outline.

## Shapes

**Form Language:** Gently rounded — 8px on cards and containers, 4px on chips/buttons/heat cells, 12px on major panels. Never fully pill-shaped (`full` only for theoretical badges not yet used).

**Borders:** 1px solid `outline-variant` (`#CAC4D0`) for outlined cards and input fields at rest. No borders on elevated cards (shadow separates).

**Clipping:** `overflow: hidden` on cards with sticky table headers. `border-radius` clips children.

**Recurring Geometry:** Heatmap cells are perfect squares (`aspect-ratio: 1`) at minimum 40px — a grid of confidence. Stat cards are equal-width flex items with centered content.

## Components

### Buttons
**Character:** Tactile and confident — primary fills with brand purple, secondary uses tonal container, outlined shows intent without weight.

- **Shape:** 8px radius (`rounded.md`), 10px×24px padding, label typography (uppercase, 14px, 500 weight)
- **Primary:** `background: primary`, `color: on-primary` → hover: `primary-fixed-dim` / `on-primary-fixed`
- **Secondary:** `background: secondary-container`, `color: on-secondary-container` → hover: `secondary-fixed-dim`
- **Outlined:** Transparent, `border: 1px solid outline`, `color: primary` — hover adds `primary-container` tint
- **Focus:** 3px primary-container ring on all variants
- **Transition:** `background 0.2s, transform 0.2s` (primary only: `translateY(-2px)` on hover)

### Tabs (Navigation)
**Character:** Segmented control — inactive tabs sit in surface-variant, active tab fills primary.

- **Shape:** 8px radius, 8px×16px padding, label typography
- **Inactive:** `background: surface-variant`, `color: on-surface-variant`
- **Active:** `background: primary`, `color: on-primary`
- **No underline, no border** — fill change is the signal
- **Mobile:** `flex-wrap: wrap`, `gap: 4px`

### Cards / Containers
- **Elevated** (`card-elevated`): White surface, 12px radius, 16px padding, dual shadow (rest). Used for dashboard panels, stats, search results.
- **Outlined** (`card-outlined`): White surface, 12px radius, 16px padding, 1px `outline-variant` border. Used for comparison tables, heatmap wrapper.
- **Internal Padding:** 16px (`spacing.md`) standard. Tables inside cards: 0 padding (table fills card).

### Inputs / Fields
- **Shape:** 8px radius, 12px×16px padding, 1px `outline` border, body typography
- **Focus:** 2px `primary` border + 3px `primary-container` ring
- **Placeholder:** `on-surface-variant` at 0.5 opacity, italic
- **Select:** Same as input, native dropdown arrow

### Heatmap Cells
**Signature Component** — the visual heartbeat of the dashboard compare view.

- **Shape:** 4px radius, perfect square (`aspect-ratio: 1`), minimum 40px
- **Typography:** Mono 10px, centered, white text, 600 weight
- **Color:** HSL hue interpolation — `hue = confidence * 1.2` (0% → 120° green, 100% → 120°... wait, 100*1.2=120, so it's green→yellow→orange→red as confidence increases? Actually the code does `hue = heat * 1.2` where heat is 0-100, so 0→0° (red), 100→120° (green). That's inverted — low confidence = red, high = green. Correct.)
- **Tooltip:** Native CSS `::after` on hover — shows category name, feature count, confidence %
- **No hover state change** — tooltip is the interaction

### Stat Cards
- **Shape:** 12px radius, 16px padding, centered content
- **Number:** 24px, 700 weight, primary color (`#2563EB` in dashboard — note: this is a hardcoded blue, not the design token primary)
- **Label:** 11px, `on-surface-variant`, uppercase
- **Gap:** 16px between cards

### Banner Hero
- **Shape:** 8px radius, `max-width: 960px`, centered, `margin: 1.5rem auto 2rem`
- **Shadow:** `0 2px 8px rgba(0,0,0,0.15)` — the deepest shadow in the system
- **Transition:** `opacity 0.4s ease-in-out` — fades in on load
- **Randomized:** Two banner assets (`banner1.png`, `banner2.png`) chosen client-side

### Search Enhancements (MkDocs Material Extension)
- **Fuzzy Score Badge:** `★ {score}` top-right of result, `accent-fg-color`, 10px, 600 weight, 0.6 opacity
- **Highlight:** `mark` elements use `accent-fg-color` background, white text, 2px radius, 600 weight
- **Placeholder:** Italic, `default-fg-color--light` at 0.5 opacity → 0.3 on focus
- **Synonym Expansion:** 71 Salesforce-term canonical mappings (LWC, Apex, Flow, Agentforce, etc.)

### Tables
- **Header:** `surface-variant` background, `on-surface-variant` text, 600 weight, sticky top
- **Rows:** 8px×10px padding, `outline` bottom border, hover: `background: #F8FAFC` (hardcoded near-white)
- **Typography:** Body 13px (slightly smaller than default 16px for density)
- **Delta Column (Compare):** Green (`#16A34A`) for positive, Red (`#DC2626`) for negative, Gray (`#64748B`) for zero — 600 weight

## Do's and Don'ts

### Do:
- **Do** use the full Material 3 tonal palette for light/dark parity — never hand-write dark overrides.
- **Do** reserve primary purple (`#6750A4`) for ≤10% of screen — active tab, focus ring, primary button, stat numbers.
- **Do** use HSL hue interpolation for dataviz (heatmap) independent of UI palette.
- **Do** keep body at 16px/1.5 line-height — density enables scanability in tables.
- **Do** use uppercase label typography (14px, 500, 0.05em tracking) for all interactive labels.
- **Do** use 8px base spacing rhythm — all padding/margin/gap are multiples of 8px.
- **Do** use Roboto + Roboto Mono — zero font load, zero layout shift, system-native.
- **Do** make cards flat at rest — elevation only on hover/focus/active.
- **Do** use 3px primary-container focus ring on all interactive elements.
- **Do** keep heatmap cells square (aspect-ratio: 1, min 40px) with mono typography.

### Don't:
- **Don't** introduce custom fonts — the system is Roboto-only by design.
- **Don't** use primary purple for decorative accents, backgrounds, or large areas.
- **Don't** add shadows to static cards — elevation is state-responsive only.
- **Don't** use pill-shaped (full) radius — max 12px on major containers.
- **Don't** hardcode colors in components that should use tokens (exception: dashboard's hardcoded `#2563EB` stat blue and `#F8FAFC` hover — these should be migrated to tokens).
- **Don't** break the 8px spacing rhythm with magic numbers.
- **Don't** use the UI palette (purple/amber) for data visualization — heatmap uses semantic HSL.
- **Don't** add motion beyond the banner's 0.4s fade-in and button 0.2s transitions.
- **Don't** omit focus styles — the 3px primary ring is the accessibility contract.
- **Don't** nest components beyond card → table → row → cell — flat hierarchy.