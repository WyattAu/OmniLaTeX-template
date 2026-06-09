# Turkish Article Example

Demonstrates the `language=turkish` class option with an article written in
Turkish.

## Usage

    latexmk -lualatex main.tex

## Class Options

- `language=turkish` -- Sets the document language via polyglossia
- `doctype=article` -- Uses scrartcl as the base class

## Notes

- Content is written entirely in Turkish to demonstrate font coverage,
  hyphenation, and caption translation.
- OmniLaTeX uses polyglossia (not babel) for language support.
- Font fallback is automatic if primary fonts lack glyphs for the script.
