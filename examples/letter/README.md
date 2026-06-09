# Formal Letter

An academic job application letter demonstrating the letter doctype with sender/recipient layout.

## Usage

    latexmk -lualatex main.tex

Or using the build system:

    python build.py build-example letter

## Class Options

| Option | Value | Description |
|--------|-------|-------------|
| doctype | letter | Formal letter doctype |
| language | english | English language support |
| institution | none | No institutional branding |

## Features Demonstrated

- `\lettersender{}` for sender address block
- `\letterrecipient{}` for recipient address block
- `\lettersubject{}` for subject line
- `\letterdate{}` for custom date
- `\letteropening{}` for salutation
- `\letterclosingblock` for signature block
- `\euro{}` currency symbol

## Notes

The letter doctype provides a complete formal letter layout with sender/recipient blocks, subject line, and closing block. The content models an academic job application.
