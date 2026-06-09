# Academic Beamer Presentation

A comprehensive academic conference presentation showcasing OmniLaTeX's beamer capabilities with the Madrid theme.

## Usage

    latexmk -lualatex main.tex

Or using the build system:

    python build.py build-example beamer-academic

## Class Options

| Option | Value | Description |
|--------|-------|-------------|
| doctype | beamer | Beamer slide presentation |
| beameraspectratio | 169 | 16:9 widescreen aspect ratio |
| beamertheme | Madrid | Madrid beamer theme |
| institution | generic | Generic institutional branding |

## Features Demonstrated

- Two-column layouts with blocks
- TikZ architecture diagrams
- Tables with `\caption`
- Mathematical typesetting (display equations)
- `\usecolortheme{whale}` color theme
- `semiverbatim` code blocks in fragile frames
- Table of contents with `\hideallsubsections`
- Appendix slides with `\allowframebreaks`
- Multiple block variants (block, alertblock, exampleblock)

## Notes

Bibliography support is available but commented out by default. Uncomment the `biblatex` lines and `\addbibresource` to include references.
