# daisyUI Official Docs Quick Index

Use these pages as the source of truth when answering daisyUI questions.

## Core Docs

- Home and install snippet: https://daisyui.com/
- Installation docs: https://daisyui.com/docs/install/
- Themes docs: https://daisyui.com/docs/themes/
- v5 upgrade guide: https://daisyui.com/docs/upgrade/
- Changelog: https://daisyui.com/docs/changelog/

## Component Docs

- Component index: https://daisyui.com/components/
- Navbar: https://daisyui.com/components/navbar/
- Drawer: https://daisyui.com/components/drawer/
- Modal: https://daisyui.com/components/modal/
- Menu: https://daisyui.com/components/menu/
- Input: https://daisyui.com/components/input/
- Select: https://daisyui.com/components/select/
- Table: https://daisyui.com/components/table/

## Current Canonical Setup (v5)

```css
@import "tailwindcss";
@plugin "daisyui";
```

Theme configuration example:

```css
@plugin "daisyui" {
  themes: light --default, dark --prefersdark, cupcake;
}
```

Custom theme example:

```css
@plugin "daisyui/theme" {
  name: "mytheme";
  default: true;
  prefersdark: false;
}
```
