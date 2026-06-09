# White Paper

An industry white paper on AI in software development demonstrating the white-paper doctype.

## Usage

    latexmk -lualatex main.tex

Or using the build system:

    python build.py build-example white-paper

## Class Options

| Option | Value | Description |
|--------|-------|-------------|
| doctype | white-paper | White paper doctype |
| language | english | English language support |
| institution | none | No institutional branding |

## Features Demonstrated

- `whitepaperabstract` environment
- `\callout{title}{text}` for key findings
- `keytakeaways` environment for summary points
- `thebibliography` for inline references with `\cite`
- `\addcontentsline` for unnumbered sections in TOC
- Subsection organization with itemized challenges and recommendations

## Notes

Uses inline `thebibliography` rather than biblatex for a self-contained example. The `\callout` and `keytakeaways` environments are specific to the white-paper doctype.
