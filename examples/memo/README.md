# Internal Memo

A software engineering process update memo demonstrating the memo doctype.

## Usage

    latexmk -lualatex main.tex

Or using the build system:

    python build.py build-example memo

## Class Options

| Option | Value | Description |
|--------|-------|-------------|
| doctype | memo | Internal memo doctype |
| language | english | English language support |
| institution | none | No institutional branding |

## Features Demonstrated

- Memo title page with author and subject
- Numbered action items and proposed changes
- Tool adoption table with `booktabs` rules
- `description` list for timeline entries
- Action items with role-based assignments

## Notes

The memo doctype provides a clean, professional layout suitable for internal communications. The date is left empty in `\date{}` to be auto-filled by `\today` if needed.
