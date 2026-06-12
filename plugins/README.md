# Plugin Catalog

## Color Themes

### Solarized (`plugins/color-themes/solarized.sty`)

Based on Ethan Schoonover's Solarized color palette. Provides a calm, eye-friendly color scheme with carefully chosen contrast ratios.

```latex
\usepackage{plugins/color-themes/solarized}
```

**Colors:** Base03-Base3 (16 shades), Yellow, Orange, Red, Magenta, Violet, Blue, Cyan, Green

### Nord (`plugins/color-themes/nord.sty`)

Based on the Nord color palette by Arctic Ice Studio. An arctic, north-bluish clean and elegant theme.

```latex
\usepackage{plugins/color-themes/nord}
```

**Colors:** Nord0-Nord6 (grays), Nord7-Nord15 (accent colors)

### GitHub Dark (`plugins/color-themes/github-dark.sty`)

Based on GitHub's dark mode color palette. Modern, developer-friendly theme.

```latex
\usepackage{plugins/color-themes/github-dark}
```

**Colors:** Canvas, FG, Border, Accent, Success, Attention, Danger variants

## Using Color Themes

1. Add `\usepackage{plugins/color-themes/THEME_NAME}` after `\documentclass`
2. The theme automatically applies colors to:
   - Section headings
   - Hyperlinks (links, URLs, citations)
   - Table rules
3. Override individual colors by redefining them after the package load

## Creating Custom Themes

Create a `.sty` file in `plugins/color-themes/` following this template:

```latex
\NeedsTeXFormat{LaTeX2e}
\ProvidesPackage{plugins/color-themes/mytheme}[YYYY-MM-DD v1.0.0 My Theme]

\RequirePackage{xcolor}

% Define your palette
\definecolor{my-primary}{HTML}{#HEXCODE}
\definecolor{my-secondary}{HTML}{#HEXCODE}

% Apply to document elements
\addtokomafont{section}{\color{my-primary}}
\hypersetup{linkcolor=my-primary, urlcolor=my-secondary}
\arrayrulecolor{my-secondary}

\endinput
```
