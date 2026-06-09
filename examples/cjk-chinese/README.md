# Chinese (CJK) Article

Demonstrates full Chinese language typesetting with luatexja, including mixed CJK-Latin text, pinyin annotations, and math.

## Usage

    latexmk -lualatex main.tex

Or using the build system:

    python build.py build-example cjk-chinese

## Class Options

| Option | Value | Description |
|--------|-------|-------------|
| doctype | article | Standard article layout |
| language | chinese | Chinese (Simplified) with luatexja |
| institution | none | No institutional branding |

## Features Demonstrated

- Chinese typesetting via luatexja (Noto Serif CJK SC)
- CJK-Latin mixed text with automatic spacing
- Pinyin ruby annotations (`\pinyin` command)
- Display mathematics in Chinese context
- Automatic paragraph indentation and full-width punctuation
- Software engineering writing in Chinese

## Notes

Requires luatexja engine support (included in TeX Live). The `\pinyin` command is commented out in the source but documented for use. OmniLaTeX handles CJK-Latin spacing automatically.
