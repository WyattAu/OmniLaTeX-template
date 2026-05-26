# OmniLaTeX

**Universal LaTeX document class** -- 27 doctypes, 21 institutions, 25 languages, 198 Lean 4 theorems.

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

- **27 doctypes** -- thesis, article, book, cv, presentation, letter, memo, invoice, recipe, and more
- **21 institutions** -- ETH, MIT, Stanford, TUHH, TUM, Cambridge, Oxford, Harvard, Yale, Princeton, Columbia, EPFL, CMU, Imperial, TU Delft, Aalto, Chalmers, KIT, NTNU, UofT, Generic
- **25 full translations** -- EN, DE, FR, ES, PT, IT, NL, PL, CZ, EL, TR, RU, VI, HI, SV, FI, DA, NO, and more
- **25 polyglossia languages** -- full script support including CJK, Arabic, Hebrew, Cyrillic
- **198 Lean 4 theorems** -- formal verification of module properties
- **815 pytest tests** -- structural, property-based, visual regression, edge cases
- **Deterministic builds** -- byte-for-byte reproducible PDFs via `SOURCE_DATE_EPOCH`

## Web Tools

| Tool | Description |
|------|-------------|
| [PDF Gallery](gallery-app.html) | Browse all 48 example PDFs with category filtering and lightbox viewer |
| [Template Picker](gallery.html) | Interactive template, language, and institution selector |
| [Build Verification](verify.html) | Verify PDF build provenance against Git commit history |

## License

Apache 2.0
