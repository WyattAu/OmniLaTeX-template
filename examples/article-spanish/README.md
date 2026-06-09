# Spanish Article Example

Demonstrates the `language=spanish` class option with an article written in
Spanish.

## Usage

    latexmk -lualatex main.tex

## Class Options

- `language=spanish` -- Sets the document language via polyglossia
- `doctype=article` -- Uses scrartcl as the base class

## Notes

- Content is written entirely in Spanish to demonstrate font coverage,
  hyphenation, and caption translation.
- OmniLaTeX uses polyglossia (not babel) for language support.
- Font fallback is automatic if primary fonts lack glyphs for the script.
