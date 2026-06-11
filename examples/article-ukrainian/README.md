# Ukrainian Article Example

Demonstrates the `language=ukrainian` class option with an article written in
Ukrainian.

## Usage

    latexmk -lualatex main.tex

## Class Options

- `language=ukrainian` -- Sets the document language via polyglossia
- `doctype=article` -- Uses scrartcl as the base class

## Notes

- Content is written entirely in Ukrainian to demonstrate Cyrillic font
  coverage, hyphenation, and caption translation.
- Ukrainian uses specific Cyrillic characters (i, yi, ye, yo) that
  differ from Russian.
- Font fallback is automatic if primary fonts lack glyphs for the script.
