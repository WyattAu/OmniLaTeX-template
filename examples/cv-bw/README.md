# OmniLaTeX CV Black/White Example

This example showcases the CV document type with black and white customizations. It demonstrates how to override default color settings for print-friendly documents using the new customization commands:

- `\documentcolormode{light}` - Sets a light color mode (minimal colors)
- `\documentlinkstyle{plain}` - Removes colored hyperlinks for black text only
- `\documentcodestyle{bw}` - Applies black and white code highlighting

Build it with `latexmk -lualatex main.tex`.