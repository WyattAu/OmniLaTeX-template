# Lab Report Template

A scientific lab report demonstrating structured abstracts, materials/methods, results with pgfplots, statistical analysis, and error propagation.

## Key Features

- Structured abstract with Objective, Methods, Results, Conclusion
- SI unit typesetting via `siunitx`
- pgfplots absorption spectra, bar charts, and scatter plots
- Subfigure layouts for method comparison
- Statistical analysis with paired t-test and Cohen's d
- Error propagation equations
- Multirow tables for multi-species data
- Equipment and materials tables
- Analysis code in verbatim/minted blocks

## Build

```bash
latexmk -lualatex main.tex
```

## File Structure

```
lab-report/
├── main.tex          # Complete lab report in one file
└── README.md
```

## Customization Tips

- Use `\SI{value}{\unit}` for consistent unit formatting
- Add `\SIrange{min}{max}{\unit}` for range expressions
- Use `subfigure` environments for side-by-side plot comparisons
- Define custom equation labels for cross-referencing in error analysis
- Include `\appendix` sections for raw data and sample calculations
