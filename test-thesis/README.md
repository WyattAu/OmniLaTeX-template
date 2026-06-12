# test-thesis

A thesis project built with [OmniLaTeX](https://github.com/WyattAu/OmniLaTeX-template).

## Structure

- `main.tex` — Main document file
- `chapters/` — Thesis chapters (introduction, methodology, results, conclusion)
- `bib/bibliography.bib` — Bibliography database
- `figures/` — Figure assets
- `.latexmkrc` — Build configuration (symlink to OmniLaTeX root)

## Building

```bash
latexmk -lualatex main.tex
```

Or from the OmniLaTeX repo root:

```bash
python build.py build-example test-thesis
```
