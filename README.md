# OmniLaTeX

[![Build](https://github.com/WyattAu/OmniLaTeX-template/actions/workflows/build.yml/badge.svg)](https://github.com/WyattAu/OmniLaTeX-template/actions/workflows/build.yml)
[![Lean 4 Proofs](https://github.com/WyattAu/OmniLaTeX-template/actions/workflows/lean4-ci.yml/badge.svg)](https://github.com/WyattAu/OmniLaTeX-template/actions/workflows/lean4-ci.yml)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-2106+-successgreen)](https://github.com/WyattAu/OmniLaTeX-template/tree/main/tests)
[![Coverage](https://img.shields.io/badge/buildlib_coverage-86%25-green)](https://github.com/WyattAu/OmniLaTeX-template/tree/main/buildlib)
[![Overleaf](https://img.shields.io/badge/Overleaf-47A141?logo=overleaf&logoColor=white)](https://www.overleaf.com/latex/templates?q=omnilatex)

A modular document class for LuaLaTeX, built on KOMA-Script. One class, 30 document types, 21 institutions, 25+ languages. Switch between thesis, CV, poster, or invoice by changing a single option.

## Quick Start

```bash
git clone https://github.com/WyattAu/OmniLaTeX-template.git
cd OmniLaTeX-template
python build.py build-example minimal-starter
```

PDF appears in `build/examples/minimal-starter.pdf`.

Or use Docker (no TeX Live required):

```bash
docker run -it --rm -v $(pwd):/workspace ghcr.io/wyattau/omnilatex-docker:latest
python build.py build-example minimal-starter
```

## Usage

```latex
\documentclass[
    language=english,
    doctype=article,
    institution=none,
]{omnilatex}

\RequirePackage{config/document-settings}

\begin{document}
\maketitle
\section{Introduction}
Your content here.
\end{document}
```

Pick a `doctype` from the list below and an `institution` from `config/institutions/`. Full documentation at `doc/omnilatex-doc.pdf` (254 pages).

## Features

- **27 document types** -- thesis, article, CV, letter, presentation, poster, exam, book, invoice, patent, and more
- **21 institution configs** -- TUHH, TUM, ETH, MIT, Harvard, Oxford, and 15 more with branded colors and logos
- **25+ languages** -- English, German, Chinese (simplified/traditional), Japanese, Korean, Arabic, Hebrew, and more. CJK and RTL with automatic font fallback
- **Color themes** -- Built-in palettes, dark mode, and per-institution branding via simple `\definecolor` commands
- **Citation styles** -- IEEE, ACM, APA, Chicago, Nature, Science, Harvard, Vancouver, MLA
- **Reproducible builds** -- Docker multi-arch (amd64/arm64) and Nix flakes for deterministic output
- **Formal verification** -- 301 theorems across 29 Lean 4 proof modules
- **VS Code extension** -- Doctype picker, institution switcher, build commands, log diagnostics
- **Build system** -- Python CLI with parallel compilation, caching, profiling, and SSIM visual regression

## Document Types

`article`, `book`, `thesis`, `dissertation`, `manual`, `report`, `journal`, `letter`, `cv`, `presentation`, `poster`, `exam`, `homework`, `lecture-notes`, `syllabus`, `handout`, `memo`, `cover-letter`, `invoice`, `recipe`, `patent`, `standard`, `white-paper`, `dictionary`, `research-proposal`, `inlinepaper`, `technical-report`.

## Institutions

Aalto, Cambridge, Chalmers, CMU, Columbia, EPFL, ETH Zurich, Generic, Harvard, Imperial, KIT, MIT, NTNU, Oxford, Princeton, Stanford, TU Delft, TUHH, TUM, U of T, Yale. Copy any config to create your own.

## Languages

English, German, French, Spanish, Italian, Portuguese, Russian, Dutch, Polish, Czech, Greek, Turkish, Swedish, Finnish, Danish, Norwegian, Chinese (simplified/traditional), Japanese, Korean, Arabic, Persian, Hebrew, Vietnamese, Hindi, Thai, Bengali.

## Requirements

- **LuaTeX** (LuaHBTeX 1.21+). Part of TeX Live 2025 or newer.
- **Python 3.10+** for the build system (`build.py`).

All LaTeX dependencies are bundled in TeX Live or installed automatically by the Docker image.

## Building

```bash
python build.py build                           # build all 92 examples
python build.py build-example thesis           # build one example
python build.py build-manual                   # build the 254-page reference manual
python build.py doctor                         # check build environment
```

## Testing

```bash
python -m pytest tests/                         # full suite (1814+ tests)
python -m pytest tests/ -m "not slow"           # fast suite (no compilation)
```

## Repository Structure

```
omnilatex.cls              # class file
lib/                       # 31 modules (layout, typography, graphics, language, etc.)
config/
  document-types/          # doctype profiles (one per document type)
  institutions/            # institution configs (colors, logos, translations)
examples/                  # 87 example documents
doc/                       # reference manual (254 pages)
bib/                       # sample bibliography
buildlib/                  # Python build system (9 modules, 78% coverage)
extensions/                # VS Code extension
web/                       # Astro documentation site
lean/                      # Lean 4 formal verification (29 modules, 301 theorems)
scripts/                   # CI, validation, and utility scripts
tests/                     # test suite (1814+ tests)
docker/                    # Docker image definition
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup instructions, coding conventions, and PR workflow.

## License

Apache 2.0. See `LICENSE` for details.
