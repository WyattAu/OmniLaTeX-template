# Arabic (RTL) Article

Demonstrates right-to-left Arabic language support with bidi text layout.

## Usage

    latexmk -lualatex main.tex

Or using the build system:

    python build.py build-example rtl-arabic

## Class Options

| Option | Value | Description |
|--------|-------|-------------|
| doctype | article | Standard article layout |
| language | arabic | Arabic with bidi support |

## Features Demonstrated

- Right-to-left text direction via bidi package
- Arabic font rendering through polyglossia
- Display mathematics within RTL text context
- Itemize and enumerate lists in Arabic
- Tables with Arabic headings
- Abstract environment in Arabic

## Notes

Arabic text direction is handled automatically by OmniLaTeX's language module. Mathematical equations render left-to-right as expected within the RTL document flow.
