# Thai Article Example

Demonstrates the `language=thai` class option with an article written in
Thai.

## Usage

    latexmk -lualatex main.tex

## Class Options

- `language=thai` -- Sets the document language via polyglossia
- `doctype=article` -- Uses scrartcl as the base class

## Notes

- Content is written entirely in Thai to demonstrate font coverage,
  line breaking, and caption translation.
- Thai script does not use spaces between words; LuaTeX handles
  word boundary detection for line breaking.
- Font fallback is automatic if primary fonts lack glyphs for the script.
