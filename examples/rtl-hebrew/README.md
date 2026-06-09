# Hebrew (RTL) Article

Demonstrates right-to-left Hebrew language support with bidi text layout.

## Usage

    latexmk -lualatex main.tex

Or using the build system:

    python build.py build-example rtl-hebrew

## Class Options

| Option | Value | Description |
|--------|-------|-------------|
| doctype | article | Standard article layout |
| language | hebrew | Hebrew with bidi support |

## Features Demonstrated

- Right-to-left text direction via bidi package
- Hebrew font rendering through polyglossia
- Display mathematics within RTL text context (Euler's identity, Taylor series)
- Itemize and enumerate lists in Hebrew
- Tables with Hebrew headings
- Abstract environment in Hebrew

## Notes

Hebrew text direction is handled automatically by OmniLaTeX's language module. Mathematical equations render left-to-right as expected within the RTL document flow.
