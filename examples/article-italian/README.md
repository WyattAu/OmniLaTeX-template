# Italian Article Example

Demonstrates the `language=italian` class option with an article written in
Italian.

## Usage

    latexmk -lualatex main.tex

## Class Options

- `language=italian` -- Sets the document language via polyglossia
- `doctype=article` -- Uses scrartcl as the base class

## Notes

- Content is written entirely in Italian to demonstrate font coverage,
  hyphenation, and caption translation.
- OmniLaTeX uses polyglossia (not babel) for language support.
- Font fallback is automatic if primary fonts lack glyphs for the script.
