# Article Template

A comprehensive showcase article demonstrating advanced OmniLaTeX features including pgfplots, commutative diagrams, code listings, algorithms, and complex tables.

## Key Features

- Complex pgfplots: line/scatter plots, bar charts, heatmaps, dual-axis, contour, pie charts
- Commutative diagrams via `tikz-cd` (exact sequences, pushouts)
- Algorithm pseudocode with complexity analysis (`algorithm2e`)
- Multi-language code listings (Python, Rust, SQL) with `minted`
- Multirow/multicolumn tables, coloured cells, long tables
- Subfigures, TikZ neural network and circuit diagrams
- `cleveref` cross-references and `biblatex` citations
- Custom mathematical operators and theorem environments

## Build

```bash
latexmk -lualatex main.tex
```

## File Structure

```
article/
├── main.tex          # Single-file article with all demonstrations
└── README.md
```

## Customization Tips

- Define domain-specific operators in the preamble (e.g., `\DeclareMathOperator`)
- Use `\theoremstyle{remark}` for non-numbered remarks
- Adjust pgfplots `width` to fit your column layout
- Switch `minted` styles by changing the `style` parameter
- Add `\subcaptionbox` for inline subfigures without separate environments
