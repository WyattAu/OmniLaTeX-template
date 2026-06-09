# Invoice

A professional service invoice with line items, tax calculation, and payment details.

## Usage

    latexmk -lualatex main.tex

Or using the build system:

    python build.py build-example invoice

## Class Options

| Option | Value | Description |
|--------|-------|-------------|
| doctype | invoice | Commercial invoice doctype |
| language | english | English language support |
| institution | none | No institutional branding |

## Features Demonstrated

- `\invoiceitem{description}{quantity}{unit_price}` command
- Subtotal, tax, and total calculation table
- Payment details section with `description` list
- Notes section with terms and conditions
- Custom tabular layout for line items

## Notes

The `\invoiceitem` command automatically calculates the line total (quantity times unit price). Currency formatting is manual in the totals section.
