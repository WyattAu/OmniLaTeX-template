# Homework Assignment

A data structures homework with exercises and solutions, demonstrating the homework doctype.

## Usage

    latexmk -lualatex main.tex

Or using the build system:

    python build.py build-example homework

## Class Options

| Option | Value | Description |
|--------|-------|-------------|
| doctype | homework | Homework assignment doctype |
| language | english | English language support |
| institution | none | No institutional branding |

## Features Demonstrated

- `exercise` environment with point values
- `solution` environment with `\showsolutions` toggle
- `verbatim` for pseudocode listings
- Display mathematics (summations, induction proofs)
- `\checkmark` and `\blacksquare` proof markers
- Custom enumerated sub-questions (`(a)`, `(b)`, `(c)`)

## Notes

Solutions are shown by default via `\showsolutions`. Remove or comment out `\showsolutions` in the preamble to hide solutions for the student version.
