# Music Typesetting

Demonstrates music notation using the MusiXTeX package within OmniLaTeX.

## Usage

    latexmk -lualatex main.tex

Or using the build system:

    python build.py build-example music

## Class Options

| Option | Value | Description |
|--------|-------|-------------|
| doctype | article | Standard article layout |
| institution | none | No institutional branding |

## Features Demonstrated

- `musixtex` package for music typesetting
- `music` environment with staff notation
- Simple melody (Twinkle Twinkle Little Star)
- Chord symbol notation
- `\setstaffs`, `\setclef`, `\generalmeter`, `\startpiece`/`\endpiece`

## Notes

Requires the `collection-music` package from TeX Live (`tlmgr install collection-music`). MusiXTeX uses its own notation language distinct from LilyPond or ABC notation.
