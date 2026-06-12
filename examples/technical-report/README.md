# Technical Report Template

A comprehensive technical report demonstrating executive summaries, multi-chapter analysis, algorithms, glossaries, diagnostic visualisations, and appendices.

## Key Features

- Executive summary chapter with key findings
- pgfplots visualisations: IOPS demand, confidence intervals, diagnostic panels
- System architecture flowchart with highlighted bottlenecks
- Algorithm pseudocode with complexity analysis (`algorithmic`)
- Glossary entries for technical abbreviations (TPS, SLA, IOPS, etc.)
- Multi-panel diagnostic figures with `subcaptionbox`
- Colour-coded health indicator tables
- Long tables spanning multiple pages
- Code listings via `minted` for configuration and scripts
- Margin notes for additional commentary

## Build

```bash
latexmk -lualatex main.tex
```

## File Structure

```
technical-report/
├── main.tex              # Document entry point
├── config/
│   ├── analysis.ini      # Config file (included in listing)
│   └── analysis.py       # Python script (included in listing)
└── README.md
```

## Customization Tips

- Define new glossary entries with `\newglossaryentry{<key>}{type=abbreviations,...}`
- Use `\cellcolor{red!30}` for critical status indicators in tables
- Adjust `\subcaptionbox` widths to control multi-panel layouts
- Add `\marginnote{}` for sidebar commentary without footnotes
- Include external files with `\inputminted{<lang>}{<file>}` for code listings
