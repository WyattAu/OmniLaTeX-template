# OmniLaTeX Minimal Custom Example

This example showcases a minimal document with multiple customizations. It demonstrates how to combine various customization commands to create a compact, sans-serif document using the new customization commands:

- `\documentfontmode{sans}` - Sets sans-serif font family
- `\documentlinespacing{single}` - Uses single line spacing
- `\documentparspacing{none}` - Removes paragraph spacing
- `\documentitemspacing{none}` - Removes item spacing

Build it with `latexmk -lualatex main.tex`.