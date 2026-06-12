# Advanced Thesis Template

An advanced thesis template with custom headers/footers, glossary input, multi-chapter structure, and comprehensive front/back matter configuration.

## Key Features

- Custom header/footer with `fancyhdr` (chapter/section marks, page numbers)
- External glossary file input via `\input{glossary}`
- Two-sided layout with binding correction (`BCOR=5mm`)
- Abstract and acknowledgements sections
- List of figures, tables, and abbreviations
- Modular chapter structure with `\include{}`
- Appendices and index generation
- `titlesec` for custom chapter formatting

## Build

```bash
latexmk -lualatex main.tex
```

## File Structure

```
advanced-thesis/
├── main.tex              # Document entry point
├── glossary              # Glossary entries file
├── chapters/
│   ├── 01-introduction.tex
│   ├── 02-literature-review.tex
│   ├── 03-methodology.tex
│   ├── 04-experiments.tex
│   ├── 05-analysis.tex
│   ├── 06-conclusion.tex
│   └── appendix-a.tex
└── README.md
```

## Customization Tips

- Modify `\fancyhead[LE]` and `\fancyhead[RO]` for different header content
- Add glossary entries in the `glossary` file using `\newacronym{}{}{}`
- Adjust `BCOR` value for your binding requirements
- Use `\renewcommand{\headrulewidth}{0pt}` to remove header lines
- Add `\listoflistings` if your thesis includes many code listings
