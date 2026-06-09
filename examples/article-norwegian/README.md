# Norwegian Article Example

Demonstrates the `language=norsk` class option with an article written in
Norwegian (Bokmål).

## Usage

    latexmk -lualatex main.tex

## Class Options

- `language=norsk` -- Sets the document language to Norwegian (Bokmål) via polyglossia
- `doctype=article` -- Uses scrartcl as the base class

## Notes

- Content is written entirely in Norwegian to demonstrate font coverage,
  hyphenation, and caption translation.
- OmniLaTeX uses polyglossia (not babel) for language support.
- Font fallback is automatic if primary fonts lack glyphs for the script.
