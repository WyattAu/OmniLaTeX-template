# Japanese (CJK) Article

Demonstrates Japanese language typesetting with luatexja, including furigana annotations and CJK-Latin mixed text.

## Usage

    latexmk -lualatex main.tex

Or using the build system:

    python build.py build-example cjk-japanese

## Class Options

| Option | Value | Description |
|--------|-------|-------------|
| doctype | article | Standard article layout |
| language | japanese | Japanese with luatexja |
| institution | none | No institutional branding |

## Features Demonstrated

- Japanese typesetting via luatexja
- Furigana ruby annotations (`\furigana` command)
- CJK-Latin mixed text with quarter-em spacing
- Display mathematics in Japanese context
- Vertical writing mode reference (commented out)
- Japanese paragraph formatting (one-character indent)

## Notes

Requires luatexja engine support (included in TeX Live). Vertical writing mode requires `luatexja-patch` which is disabled for TeX Live 2025 compatibility.
