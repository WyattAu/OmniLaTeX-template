# Advanced Technical Report

A comprehensive technical report with glossary integration, custom tcolorbox environments, sequence diagrams, latency histograms, and multi-format code listings.

## Key Features

- Custom `keyfindingbox`, `definitionbox`, and `notebox` environments
- Glossary terms via `\gls{}` with automatic abbreviation lists
- System architecture, data flow, and sequence diagrams (TikZ)
- IOPS demand plot, confidence intervals, resource utilisation stacked area
- Latency histogram with fitted normal curve
- Colour-coded health indicator and compute utilisation tables
- Resource allocation algorithm with complexity analysis
- Code listings: INI config, HTTP routes, SQL queries via `\inputminted`
- Inline code with `\mintinline{}{}` for quick references
- Margin notes for supplementary commentary

## Build

```bash
latexmk -lualatex main.tex
```

## File Structure

```
advanced-report/
├── main.tex              # Document entry point
├── glossary              # Glossary entries
├── config/macros         # Custom command definitions
├── config/
│   ├── monitoring.ini    # INI config (included in listing)
│   ├── api-routes.http   # HTTP routes (included in listing)
│   └── queries.sql       # SQL queries (included in listing)
└── README.md
```

## Customization Tips

- Define custom tcolorbox environments with `\newtcolorbox{name}{options}`
- Add glossary entries in the `glossary` file using `\newglossaryentry{}{}`
- Use `\inputminted{lang}{file}` to include external code files
- Add `\marginnote{}` for sidebar annotations without footnotes
- Adjust table `\cellcolor` thresholds to match your monitoring alerts
