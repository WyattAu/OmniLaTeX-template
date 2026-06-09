# Native Beamer Presentation

A clean OmniLaTeX beamer presentation demonstrating native beamer environments and block variants.

## Usage

    latexmk -lualatex main.tex

Or using the build system:

    python build.py build-example beamer-native

## Class Options

| Option | Value | Description |
|--------|-------|-------------|
| doctype | beamer | Beamer slide presentation |
| language | english | English language support |
| beameraspectratio | 169 | 16:9 widescreen aspect ratio |

## Features Demonstrated

- Table of contents with `\tableofcontents`
- `\section` for slide grouping
- Block variants (block, alertblock, exampleblock)
- Two-column layout using `columns` environment
- `\alert` command for inline emphasis
- Numbered lists with `enumerate`

## Notes

Uses the default beamer theme. Good starting template for customizing beamer presentations with OmniLaTeX.
