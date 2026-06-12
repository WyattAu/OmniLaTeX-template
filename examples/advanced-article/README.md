# Advanced Article Template

A research article showcasing HeteroGNN with formal proofs, algorithm pseudocode, pgfplots experiments, architecture diagrams, and supplementary material.

## Key Features

- Structured abstract (Background, Methods, Results, Conclusions)
- Formal theorem/proof environments with `\autoref`
- Algorithm pseudocode (`algorithm2e`) with complexity analysis
- pgfplots: bar charts, group plots, dual-axis, pie charts
- Architecture, data flow, and neural network diagrams (TikZ)
- Qualitative result subfigures (2-hop, 3-hop queries)
- Extended results table with Hits@k metrics
- Cross-reference examples demonstrating `\cref`, `\autoref`, `\namecref`
- Python implementation listing via `minted`

## Build

```bash
latexmk -lualatex main.tex
```

## File Structure

```
advanced-article/
├── main.tex          # Complete article in one file
└── README.md
```

## Customization Tips

- Add new theorems with `\newtheorem{name}{Name}[section]`
- Use `\begin{proof}[Proof of \cref{thm:name}}` for labelled proofs
- Adjust pgfplots `ybar` width and `nodes near coords` for readability
- Use `\subcaptionbox{label\label{fig:name}}[width]{content}` for inline subfigures
- Extend the comparison table with additional baseline methods
