# Korean (CJK) Article

Demonstrates Korean language typesetting with luatexja, including ruby annotations for Hanja and Hangul-Latin mixed text.

## Usage

    latexmk -lualatex main.tex

Or using the build system:

    python build.py build-example cjk-korean

## Class Options

| Option | Value | Description |
|--------|-------|-------------|
| doctype | article | Standard article layout |
| language | korean | Korean with luatexja |
| institution | none | No institutional branding |

## Features Demonstrated

- Korean typesetting via luatexja
- Ruby annotations for Hanja reading (`\ruby` command)
- Hangul-Latin mixed text with automatic spacing
- Display mathematics in Korean context
- Korean technical document conventions

## Notes

Requires luatexja engine support (included in TeX Live). OmniLaTeX handles Hangul-Latin spacing automatically via the luatexja integration.
