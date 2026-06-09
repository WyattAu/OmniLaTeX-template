# Accessibility Test

Demonstrates PDF/UA-1 tagged PDF support with screen reader compatibility features.

## Usage

    latexmk -lualatex main.tex

Or using the build system:

    python build.py build-example accessibility-test

## Class Options

| Option | Value | Description |
|--------|-------|-------------|
| doctype | article | Standard article layout |
| institution | none | No institutional branding |

## Features Demonstrated

- Tagged PDF (PDF/UA-1) via `tagpdf` package
- `\alttext` and `\tikzalttext` for figure alt text
- `\accessiblelink` for accessible hyperlinks
- `\checkcontrast` for WCAG color contrast checking
- `\readingorder` hints for screen reader content sequence
- `\langtag` for marking passages in different languages
- `\validatstructure` for heading hierarchy validation
- pgfplots chart with accessibility markup

## Notes

Requires TeX Live 2026+ for `\DocumentMetadata` support. The `omnilatex-accessibility` package is loaded explicitly to enable all accessibility features.
