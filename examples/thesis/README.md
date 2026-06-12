# Thesis Template

A complete thesis template demonstrating front matter, chapters, back matter, glossaries, and index generation.

## Key Features

- Front matter with title page, table of contents, list of figures/tables/algorithms
- Automatic glossary and acronym list generation
- Multi-chapter structure with `\include{}` for modular content
- Bibliography via `biblatex` with shared `.bib` file
- Index generation with `\makeindex` and `\printindex`
- Appendix and back matter support

## Build

```bash
latexmk -lualatex main.tex
```

## File Structure

```
thesis/
├── main.tex              # Document entry point
├── config/
│   ├── document-settings # Package options and settings
│   └── macros            # Custom commands
├── chapters/
│   ├── 01-introduction.tex
│   ├── 02-background.tex
│   ├── 03-methodology.tex
│   ├── 04-results.tex
│   ├── 05-discussion.tex
│   ├── 06-conclusion.tex
│   └── 07-appendix.tex
└── README.md
```

## Customization Tips

- Change `institution=none` to your university for branded title pages
- Set `language=german` or other languages for automatic localization
- Add `\listofalgorithms` if your thesis uses algorithm environments
- Modify `config/macros` to define domain-specific commands
- Adjust `BCOR` binding correction in `\documentclass` options
