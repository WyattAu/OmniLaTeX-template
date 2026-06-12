# Literature Review Template

A systematic literature review demonstrating PRISMA methodology, thematic analysis, synthesis matrices, and gap identification with TikZ diagrams.

## Key Features

- PRISMA-compliant search protocol and flow diagram (TikZ)
- Taxonomy tree diagram for method classification
- Multiple comparison tables (models, benchmarks, augmentation strategies)
- Synthesis matrix mapping papers to aspects
- Critical analysis table with strengths/weaknesses
- Gap analysis table with proposed directions
- `\textcite`, `\parencite`, and `\autoref` citation styles
- Multi-row/multi-column table spanning

## Build

```bash
latexmk -lualatex main.tex
```

## File Structure

```
literature-review/
├── main.tex          # Complete review in one file
└── README.md
```

## Customization Tips

- Adapt the PRISMA flow diagram by modifying TikZ node positions
- Use `\checkmark` and `\sim` symbols in synthesis matrices
- Add new thematic strands as additional `\section{}` blocks
- Extend comparison tables with additional columns for new dimensions
- Use `\textcite{}` for author-prominent and `\parencite{}` for parenthetical citations
