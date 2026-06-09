# Citation Styles Example

Demonstrates switching between 9 pre-configured bibliography styles using the `\citationstyle{}` command.

## Usage

    latexmk -xelatex main.tex

Or using the build system:

    python build.py build-example citation-styles

## Class Options

| Option | Value | Description |
|--------|-------|-------------|
| doctype | article | Standard article layout |
| language | english | English language support |
| institution | none | No institutional branding |

## Features Demonstrated

- `\citationstyle{}` command with 9 styles: ieee, acm, apa, chicago, nature, science, harvard, vancouver, mla
- `biblatex` integration via `omnilatex-citations`
- `\cite` and `\ref` commands
- `\printbibliography` for reference list
- External `.bib` file (`refs.bib`)

## Notes

Change the active citation style by commenting/uncommenting the `\citationstyle{...}` line. Requires a `refs.bib` file in the example directory. Uses xelatex by default per the example header.
