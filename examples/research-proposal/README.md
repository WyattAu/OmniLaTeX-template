# Research Proposal

A multi-chapter research proposal on quantum error correction with bibliography, TikZ diagrams, and budget tables.

## Usage

    latexmk -lualatex main.tex

Or using the build system:

    python build.py build-example research-proposal

## Class Options

| Option | Value | Description |
|--------|-------|-------------|
| doctype | research-proposal | Research proposal doctype |
| language | english | English language support |
| institution | none | No institutional branding |
| titlestyle | book | Book-style title page |

## Features Demonstrated

- Multi-chapter structure with `\chapter`
- `\frontmatter`, `\mainmatter`, `\appendix` division
- `biblatex` bibliography with `\cite` commands
- TikZ pipeline diagram (CNN decoder architecture)
- Display mathematics (stabiliser code parameters)
- Multiple tables (code parameters, timeline, budget)
- External `.bib` file (`../../bib/bibliography.bib`)

## Notes

Requires the shared bibliography file at `../../bib/bibliography.bib`. Uses `book` title style for a formal proposal appearance. The document uses a report-style base class.
