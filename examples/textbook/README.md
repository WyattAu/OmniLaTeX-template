# Textbook Template

A multi-chapter textbook with learning objectives, definitions, theorems, proofs, algorithms, TikZ diagrams, pgfplots performance comparisons, and graded exercises.

## Key Features

- Learning objectives per chapter with enumerated labels
- Theorem, definition, lemma, and proof environments
- LU factorisation algorithm with `algorithm2e`
- Concept map and data flow diagrams (TikZ)
- Sparse matrix sparsity pattern visualisation
- pgfplots: direct vs. iterative solver scaling, convergence history
- Python code listings via `minted`
- Graded exercises (star levels) with `\resume` numbering
- Key terms glossary with `description` environment

## Build

```bash
latexmk -lualatex main.tex
```

## File Structure

```
textbook/
├── main.tex          # Complete textbook in one file
└── README.md
```

## Customization Tips

- Add learning objectives with `\item[LO1.]` format for consistency
- Use `\begin{proof}[Proof of \autoref{thm:name}]` for named proofs
- Adjust exercise difficulty by adding `\star`, `\star\star`, `\star\star\star` levels
- Modify pgfplots data points to reflect your own benchmarks
- Use `\DontPrintSemicolon` in `algorithm2e` for cleaner pseudocode
