# German (Formal/Reformed) Article Example

Demonstrates the `language=ngerman` class option with an article written in
German using the reformed (new) spelling rules.

## Usage

    latexmk -lualatex main.tex

## Class Options

- `language=ngerman` -- Sets the document language to new German spelling via polyglossia
- `doctype=article` -- Uses scrartcl as the base class

## Notes

- Content is written entirely in German to demonstrate font coverage,
  hyphenation, and caption translation.
- Uses `ngerman` (new German spelling) rather than `german` (traditional spelling).
- OmniLaTeX uses polyglossia (not babel) for language support.
- Font fallback is automatic if primary fonts lack glyphs for the script.
