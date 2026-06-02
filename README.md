# OmniLaTeX

A modular document class for LuaLaTeX, built on KOMA-Script. Supports 27 document types (thesis, article, CV, letter, presentation, poster, exam, book, and more), 20 institution configurations, 18 languages (including CJK and RTL), and reproducible builds via Docker or Nix.

## Quick Start

```bash
git clone https://github.com/WyattAu/OmniLaTeX-template.git
cd OmniLaTeX-template
python build.py build-example minimal-starter
```

The PDF appears in `build/examples/minimal-starter.pdf`.

Or use Docker if you do not have TeX Live installed:

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
...
\end{document}
```

Pick a `doctype` from the list below and an `institution` from `config/institutions/`. Full documentation at `doc/omnilatex-doc.pdf` (254 pages).

### Document Types

`article`, `book`, `thesis`, `dissertation`, `manual`, `report`, `journal`, `letter`, `cv`, `presentation`, `poster`, `exam`, `homework`, `lecture-notes`, `syllabus`, `handout`, `memo`, `cover-letter`, `invoice`, `recipe`, `patent`, `standard`, `white-paper`, `dictionary`, `research-proposal`, `inlinepaper`, `technical-report`.

### Institutions

20 pre-configured institutions in `config/institutions/`: Aalto, Chalmers, Columbia, Harvard, KIT, NTNU, TU Dresden, TUHH, and others. Each provides colors, logos, and translation strings. Copy an existing config to create your own.

### Languages

English, German, French, Spanish, Italian, Portuguese, Russian, Dutch, Polish, Czech, Greek, Turkish, Swedish, Finnish, Danish, Norwegian, Chinese (simplified/traditional), Japanese, Korean, Arabic, Persian, Hebrew, Vietnamese, Hindi, Thai, Bengali.

## Requirements

- **LuaTeX** (LuaHBTeX 1.17+). Part of TeX Live 2024 or newer.
- Python 3.10+ for the build system (`build.py`).
- GNU Make for the test suite.

All LaTeX dependencies are bundled in TeX Live or installed automatically by the Docker image.

## Building

```bash
python build.py build                           # build all examples
python build.py build-example thesis           # build one example
python build.py build-example minimal-starter  # build one example
python build.py build-manual                   # build the 254-page reference manual
```

Use `python build.py --help` for all options.

## Testing

```bash
python -m pytest tests/                         # full suite (815 tests)
python -m pytest tests/test_modules.py          # structural tests only
python -m pytest tests/test_ctan.py             # CTAN package validation
```

## Repository Structure

```
├── omnilatex.cls              # class file
├── lib/                       # 31 modules (layout, typography, graphics, language, etc.)
├── config/
│   ├── document-types/        # doctype profile files (one per document type)
│   └── institutions/          # institution configurations
├── examples/                  # 48 example documents
├── doc/                       # reference manual (254 pages)
├── bib/                       # sample bibliography
├── scripts/                   # build and CI scripts
├── docker/                    # Docker image definition
├── tests/                     # test suite
└── build.py                   # build system entry point
```

## Contributing

Bug reports and pull requests are welcome. Run the test suite before submitting a PR. The CI pipeline must pass (lint → build → test → determinism → performance).

## License

Apache 2.0. See `LICENSE` for details.
