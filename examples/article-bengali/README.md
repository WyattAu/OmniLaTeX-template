# Bengali Article Example

Demonstrates the `language=bengali` class option with an article written in
Bengali (Bangla).

## Usage

    latexmk -lualatex main.tex

## Class Options

- `language=bengali` -- Sets the document language via polyglossia
- `doctype=article` -- Uses scrartcl as the base class

## Notes

- Content is written entirely in Bengali to demonstrate font coverage,
  vowel sign positioning, and caption translation.
- Bengali script uses complex conjunct consonants that require
  proper OpenType shaping support from the font.
- Font fallback is automatic if primary fonts lack glyphs for the script.
