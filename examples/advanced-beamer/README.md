# Advanced Beamer Presentation

An advanced Beamer presentation with tcolorbox integration, algorithm visualisation, graph subgraph highlighting, proof steps, and row-highlighted tables.

## Key Features

- Overlay-aware `tcolorbox` with `enhanced` skin
- Animated flowchart construction with `\only`
- Step-by-step Dijkstra's algorithm visualisation
- Subgraph highlighting with TikZ `fit` library
- Matrix element colour highlighting across slides
- Proof steps with incremental reveals
- Code listings: Python with line highlighting, Rust iterator
- Tables with `\rowcolor` for emphasis
- Subfigures with timed overlay reveals
- Timed footnotes and bibliography

## Build

```bash
latexmk -lualatex main.tex
```

## File Structure

```
advanced-beamer/
├── main.tex          # Complete presentation in one file
└── README.md
```

## Customization Tips

- Use `\begin{tcolorbox}[enhanced, ...]` for boxes that support beamer overlays
- Add `\only<slide>{...}` inside TikZ for per-slide node changes
- Use `\rowcolor{green!10}` for positive highlights, `red!10` for negative
- Create subgraph highlights with `\node[fit=(a)(b)(c)]` and `\draw[dashed]`
- Add appendix frames after `\appendix` for backup material
