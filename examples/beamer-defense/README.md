# Thesis Defense Beamer Presentation

A thesis defense presentation with the Copenhagen theme, illustrating academic defense structure with equations and proof formalism.

## Usage

    latexmk -lualatex main.tex

Or using the build system:

    python build.py build-example beamer-defense

## Class Options

| Option | Value | Description |
|--------|-------|-------------|
| doctype | beamer | Beamer slide presentation |
| beameraspectratio | 169 | 16:9 widescreen aspect ratio |
| beamertheme | Copenhagen | Copenhagen beamer theme |
| language | english | English language support |

## Features Demonstrated

- Defense-style structure (introduction, background, methodology, results, conclusion)
- TikZ architecture diagrams with custom node styles
- Display mathematics (formal reproducibility theorem)
- `semiverbatim` code listing for property-based testing
- Verification results tables
- `\usetikzlibrary{arrows.meta,positioning,shapes}`
- Appendix with backup slides
- `\useoutertheme{infolines}` for progress footer

## Notes

TUHH institutional branding is referenced in the institute field. The `\titlegraphic` line for logo inclusion is commented out and can be enabled by uncommenting.
