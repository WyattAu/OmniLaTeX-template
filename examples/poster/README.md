# Academic Poster

A three-column academic conference poster using the poster doctype with pgfplots and TikZ diagrams.

## Usage

    latexmk -lualatex main.tex

Or using the build system:

    python build.py build-example poster

## Class Options

| Option | Value | Description |
|--------|-------|-------------|
| doctype | poster | Conference poster doctype |
| language | english | English language support |
| institution | none | No institutional branding |

## Features Demonstrated

- `posterblock` and `posterblocknotitle` environments
- Three-column layout with `multicols`
- pgfplots accuracy chart with legend
- TikZ architecture diagram with custom node styles
- `columnbreak` for manual column control
- Reference list in poster format

## Notes

The poster doctype is designed for academic conference posters. Content is organized into named blocks within a `multicols` environment. TikZ and pgfplots are loaded automatically by the poster profile.
