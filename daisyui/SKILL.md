---
name: daisyui
description: Build and optimize UI with daisyUI for Tailwind CSS projects, including installation, v5 config in CSS, theme setup, component composition, and v4 to v5 migration fixes. Use when the user asks for daisyUI components (navbar, drawer, modal, forms, etc.), theme switching/custom themes, or cleanup of outdated daisyUI class names/config.
---

# daisyUI

Use this workflow to deliver daisyUI changes that match current official docs and avoid stale v4 patterns.

## Workflow

1. Detect project style before editing.
2. If project uses Tailwind CSS v4 style CSS plugins, use:
```css
@import "tailwindcss";
@plugin "daisyui";
```
3. If user is migrating from old `tailwind.config.js` plugin syntax, apply v5 migration guidance from `references/upgrade-notes.md`.
4. Build components with semantic daisyUI classes first (`btn`, `navbar`, `drawer`, `menu`, `input`, etc.), then add Tailwind utilities for spacing/layout.
5. Configure themes in CSS plugin block, and apply with `data-theme` at page or section scope.
6. Validate produced HTML for accessibility semantics (`button`, `label`, `input`, focusable triggers, keyboard navigation).

## Default Patterns

### Install
```bash
npm i -D daisyui@latest
```

### Config in CSS (daisyUI v5)
```css
@import "tailwindcss";
@plugin "daisyui";
```

### Theme setup
```css
@plugin "daisyui" {
  themes: light --default, dark --prefersdark, cupcake, dracula;
}
```

```html
<html data-theme="cupcake">
  <section data-theme="dracula"></section>
</html>
```

### Custom theme
```css
@plugin "daisyui/theme" {
  name: "mytheme";
  default: true;
  prefersdark: false;
}
```

## Component Guidance

1. Prefer composition from official component primitives:
`navbar`, `menu`, `drawer`, `modal`, `card`, `alert`, `tabs`, `table`, `input`, `select`, `textarea`, `toggle`.
2. Keep markup minimal; avoid wrapping every element in utility-heavy containers unless layout requires it.
3. For responsive nav, combine `navbar` + `dropdown` + `menu`.
4. For app-shell layout, combine `drawer` + `menu` + content region.
5. Use `join` for grouped actions/inputs and `fieldset`/`label` for forms.

## Read References As Needed

- Official links and quick config snippets: `references/official-docs.md`
