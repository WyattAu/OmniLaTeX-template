# Color Themes Preview

A visual comparison of all 6 built-in color themes with dark/light mode toggle and custom color overrides.

## Usage

    latexmk -lualatex main.tex

Or using the build system:

    python build.py build-example color-themes

## Class Options

| Option | Value | Description |
|--------|-------|-------------|
| doctype | article | Standard article layout |
| language | english | English language support |
| institution | none | No institutional branding |
| titlestyle | simple | Simple title page style |

## Features Demonstrated

- All 6 color themes: default, midnight, forest, rose, monochrome, sepia
- Dark/light mode toggle with `\darkmode` and `\lightmode`
- Monochrome dark variant (`monochrome-dark`)
- `\usetheme{}` command for switching themes mid-document
- `\setthemecolor{}` for per-slot color overrides
- Institution color integration behavior
- Hyperlinks, blocks, and emphasis in each theme
- `omnilatex-themes` package

## Notes

Each theme is demonstrated on its own page with consistent element examples for comparison. Available color slots: bg, fg, heading, body, accent, blockbg, blockframe, link, rule, codebg, footernote.
