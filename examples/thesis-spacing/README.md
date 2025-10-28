# OmniLaTeX Thesis Spacing Example

This example showcases the thesis document type with custom spacing customizations. It demonstrates how to override default spacing settings using the new customization commands:

- `\documentlinespacing{double}` - Sets double line spacing for better readability
- `\documentparspacing{full}` - Uses full baseline skip between paragraphs
- `\documentitemspacing{compact}` - Reduces spacing between list items

Build it with `latexmk -lualatex main.tex`.