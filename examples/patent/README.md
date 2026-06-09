# Patent Application

A patent application template following standard patent specification structure.

## Usage

    latexmk -lualatex main.tex

Or using the build system:

    python build.py build-example patent

## Class Options

| Option | Value | Description |
|--------|-------|-------------|
| doctype | patent | Patent specification doctype |
| language | english | English language support |
| institution | none | No institutional branding |
| titlestyle | book | Book-style title page |
| oneside | — | Single-sided printing |

## Features Demonstrated

- Standard patent section structure (Field, Background, Summary, Drawings, Detailed Description, Claims, Abstract)
- Independent and dependent claim numbering
- Embodiment subsections
- Table of contents

## Notes

This is a structural template with placeholder content. Replace the placeholder text with actual patent specification content. The `titlestyle=book` and `oneside` options give a formal document appearance.
