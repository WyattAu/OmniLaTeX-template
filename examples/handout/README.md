# Handout

A study handout on Big-O notation with key concepts, reference tables, and practice problems.

## Usage

    latexmk -lualatex main.tex

Or using the build system:

    python build.py build-example handout

## Class Options

| Option | Value | Description |
|--------|-------|-------------|
| doctype | handout | Handout/cheat-sheet doctype |
| language | english | English language support |
| institution | none | No institutional branding |

## Features Demonstrated

- `\keyconcept` environment for highlighted definitions
- `\remember` environment for important takeaways
- Complexity comparison table with `booktabs` rules
- Inline and display mathematics
- Practice problems section
- Further reading references

## Notes

The handout doctype is optimized for concise, scannable reference material. `\keyconcept` boxes draw attention to core definitions and `\remember` boxes highlight actionable advice.
