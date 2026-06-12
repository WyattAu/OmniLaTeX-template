# Beamer Academic Presentation

A comprehensive Beamer showcase demonstrating overlays, animations, TikZ integration, code listings, and advanced formatting for academic presentations.

## Key Features

- Overlay animations: `\only`, `\uncover`, `\visible`, `\pause`, `\alt`, `\temporal`
- Block environments: standard, alert, example, and custom-coloured blocks
- Theorem and proof environments within slides
- Animated TikZ flowcharts and graph highlighting
- Multi-column layouts with `columns` and `minipage`
- Code listings with line highlighting (Python, LaTeX)
- Step-by-step equation building and matrix element highlighting
- Timed footnotes and bibliography citations
- Appendix slides with reference tables

## Build

```bash
latexmk -lualatex main.tex
```

## File Structure

```
beamer-academic/
├── main.tex          # Complete presentation in one file
└── README.md
```

## Customization Tips

- Change `beamertheme=Madrid` to other themes (e.g., `metropolis`, `AnnArbor`)
- Set `beameraspectratio=169` for widescreen or `43` for standard
- Use `\setbeamercolor` to customize block and text colours
- Add `\appendix` before backup slides for clean navigation
- Use `highlightlines={3-5}` in `lstlisting` to emphasise code sections
