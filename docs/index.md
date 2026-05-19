# OmniLaTeX

**Universal LaTeX document class** -- 26 doctypes, 21 institutions, 18 languages, 196 Lean 4 theorems.

## Quick Start

```latex
\documentclass[doctype=thesis,institution=tuhh,language=german]{omnilatex}
\begin{document}
\title{My Thesis}
\author{Jane Doe}
\maketitle
\tableofcontents
\chapter{Introduction}
Hello, world.
\end{document}
```

```bash
# Compile with LuaLaTeX
latexmk -lualatex main.tex

# Or use the build tool
python build.py build-example minimal-starter
```

## Installation

| Method | Command |
|--------|---------|
| Docker | `docker run -v $(pwd):/workspace ghcr.io/wyattau/omnilatex-docker:latest` |
| Nix | `nix develop` |
| CTAN | `tlmgr install omnilatex` (pending) |
| Local | TeX Live 2025+ with LuaLaTeX |

## Features

- **26 doctypes** -- thesis, article, book, cv, presentation, letter, memo, invoice, recipe, and more
- **21 institutions** -- ETH, MIT, Stanford, TUHH, TUM, Cambridge, Oxford, Harvard, Yale, Princeton, Columbia, EPFL, CMU, Imperial, TU Delft, Aalto, Chalmers, KIT, NTNU, UofT, Generic
- **18 full translations** -- EN, DE, FR, ES, PT, IT, NL, PL, CZ, EL, TR, RU, VI, HI, SV, FI, DA, NO
- **25 polyglossia languages** -- full script support including CJK, Arabic, Hebrew, Cyrillic
- **196 Lean 4 theorems** -- formal verification of module properties
- **473 pytest tests** -- structural, property-based, visual regression
- **Deterministic builds** -- byte-for-byte reproducible PDFs via `SOURCE_DATE_EPOCH`

## License

Apache 2.0
