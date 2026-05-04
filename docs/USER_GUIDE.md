# OmniLaTeX User Guide

## Quick Start

```bash
git clone https://github.com/WyattAu/OmniLaTeX-template.git
cd OmniLaTeX-template
python build.py build-example minimal-starter
```

Output: `build/examples/minimal-starter.pdf`

Requires **TeX Live 2025+** with LuaLaTeX, Python 3.10+, and Git. Alternatively:

```bash
nix develop    # enter the Nix dev shell (all tools pre-installed)
python build.py build-example minimal-starter
```

```bash
docker run -it --rm -v $(pwd):/workspace ghcr.io/wyattau/omnilatex-docker:latest
python build.py build-example minimal-starter
```

## Minimal Document

```latex
\documentclass[doctype=thesis]{omnilatex}
\title{My Document}
\author{Author Name}
\date{\today}

\begin{document}
\maketitle
\tableofcontents

\chapter{Introduction}
Hello, OmniLaTeX.
\end{document}
```

Compile: `latexmk -lualatex main.tex` or `python build.py build-root`

## Document Types

OmniLaTeX provides 26 document type profiles across 3 KOMA-Script base classes.
Switch with `\documentclass[doctype=<type>]{omnilatex}`.

### scrbook (book-class, chapters, twoside)

| Doctype | Description |
|---------|-------------|
| `thesis` | Academic thesis with advisor, committee, declaration of authorship |
| `dissertation` | PhD dissertation with front matter and committee |
| `book` | Book-length document with publisher metadata, edition, ISBN |
| `dictionary` | Dictionary/lexicon with series and publisher info |

### scrreprt (report-class, chapters, open=any)

| Doctype | Description |
|---------|-------------|
| `manual` | Product manual/handbook with version and support info |
| `technicalreport` | Technical report with report number and confidentiality |
| `standard` | Standards document with ICS codes and designation |
| `patent` | Patent specification |
| `research-proposal` | Research proposal with budget and timeline |
| `white-paper` | White paper / position paper |

### scrartcl (article-class, no chapters)

| Doctype | Description |
|---------|-------------|
| `article` | Research article with abstract, keywords, DOI |
| `journal` | Journal article with volume, issue, highlights |
| `inlinepaper` | Compact two-column inline research paper (arXiv style) |
| `cv` | Curriculum vitae with photo, links, and summary |
| `cover-letter` | Cover letter with recipient and sender metadata |
| `poster` | Conference poster (A1 landscape) |
| `presentation` | Presentation slides (KOMA-based) |
| `letter` | Formal letter with recipient, subject, and closing |
| `homework` | Homework assignment with exercises and solutions |
| `exam` | Examination paper with questions and answer spaces |
| `lecture-notes` | Lecture notes with theorem environments |
| `syllabus` | Course syllabus with grading policy and schedule |
| `handout` | Two-column handout with key concept boxes |
| `memo` | Memorandum with TO/FROM/CC/RE fields |
| `invoice` | Commercial invoice |
| `recipe` | Recipe with ingredients and instructions |

### Aliases

Each doctype accepts plural and alternative forms: `doctype=articles`, `doctype=paper`,
`doctype=technical-report`, `doctype=cv`, `doctype=resume`, etc. Over 55 aliases are
recognized (see `omnilatex.cls` for the full list).

## Institutions

OmniLaTeX ships 16 institution configurations. Enable with
`\documentclass[doctype=thesis,institution=<name>]{omnilatex}`.

| Institution | Config | Colors |
|-------------|--------|--------|
| TUHH | `tuhh` | TUHH Blue |
| TUM | `tum` | TUM Blue, Dark Blue, Light Blue |
| ETH Zurich | `eth` | ETH Blue, Dark, Teal |
| MIT | `mit` | MIT Crimson, Cool Gray |
| Stanford | `stanford` | Cardinal, Sandstone, Green |
| Cambridge | `cambridge` | Cambridge Green, Blue |
| Oxford | `oxford` | Oxford Blue, Stone, Red |
| Princeton | `princeton` | Orange, Blue |
| Yale | `yale` | Yale Blue, Gold |
| Harvard | `harvard` | Harvard Crimson |
| Columbia | `columbia` | Columbia Blue |
| CMU | `cmu` | CMU Red, Gray |
| EPFL | `epfl` | EPFL Red |
| Imperial | `imperial` | Imperial Blue, Crimson |
| TU Delft | `tudelft` | TU Delft Cyan, Dark Blue |
| Generic | `generic` | User-defined (template for new institutions) |

Add a new institution:

```bash
python build.py scaffold-institution myuniversity
```

See `config/institutions/README.md` for details.

## Languages

OmniLaTeX uses Polyglossia for language support. Set with
`\documentclass[language=<lang>]{omnilatex}`.

### Primary (full translation support)

| Language | Key |
|----------|-----|
| English | `english` |
| German | `german` |
| French | `french` |
| Spanish | `spanish` |
| Chinese (Simplified) | `chinese` / `simplifiedchinese` |
| Japanese | `japanese` |
| Korean | `korean` |
| Arabic | `arabic` |
| Hebrew | `hebrew` |

### Secondary (standard captions via Polyglossia)

Polish, Dutch, Catalan, Brazilian Portuguese, Italian, Portuguese, Romanian,
Turkish, Greek, Russian, Ukrainian, Czech, Slovak, Slovenian, Serbian, Croatian,
Bulgarian, Mongolian, Persian, Vietnamese, Hindi, Swedish, Finnish, Danish, Norwegian.

### CJK and RTL

Chinese, Japanese, and Korean documents auto-load CJK font support (Haranoaji/Noto
fallback). Arabic, Hebrew, and Persian documents auto-load RTL bidirectional support.

### Adding a language

```bash
python build.py scaffold-language italian
```

## Build System

### build.py

The primary build tool. Run from the repository root.

```bash
# Building
python build.py build-root               # Build root main.tex
python build.py build-example thesis     # Build one example
python build.py build-examples           # Build all 42 examples
python build.py build-examples -j 8      # Parallel build (8 jobs)
python build.py build-examples --force   # Force rebuild (ignore cache)

# Cleaning
python build.py clean                    # Remove all build artifacts
python build.py clean-aux                # Clean auxiliary files only

# Quality
python build.py test                     # Run full test suite
python build.py preflight                # Validate build environment
python build.py doctor                   # Comprehensive health diagnostics
python build.py diff thesis              # Visual regression check (SSIM)

# Utilities
python build.py list-examples            # List all available examples
python build.py watch                    # Watch files and rebuild on change
python build.py init myproject --doctype=article --language=english
python build.py scaffold-institution myuni
python build.py scaffold-language italian
```

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--mode` | `dev` | Build mode: `dev`, `prod`, `ultra` |
| `--verbose` | off | Verbose subprocess output |
| `--timings` | off | Record per-example build metrics |
| `--force` | off | Ignore incremental build cache |
| `-j, --jobs` | auto | Parallel build jobs |
| `--source-date-epoch` | none | Reproducible builds (Unix timestamp) |

### latexmk

Direct latexmk invocation also works:

```bash
latexmk -lualatex -interaction=nonstopmode main.tex
```

The `.latexmkrc` at the project root configures Biber, bib2gls, and LuaLaTeX.

### Nix

```bash
nix develop              # Enter dev shell
nix build .#             # Build default package
nix build .#examples-thesis  # Build a specific example
```

## Configuration Options

All options are passed via `\documentclass[key=value]{omnilatex}`.

### Core Options

| Option | Default | Description |
|--------|---------|-------------|
| `doctype` | `thesis` | Document type profile |
| `language` | `english` | Document language |
| `titlestyle` | `book` | Title page style |
| `institution` | `none` | Institution config |

### Feature Toggles

| Option | Default | Description |
|--------|---------|-------------|
| `enablefonts` | off | Custom font module |
| `enablegraphics` | off | Graphics module (SVG, plots) |
| `enablemath` | on | Math module (amsmath, siunitx) |
| `enabletikz` | on | TikZ module (core TikZ) |
| `enableengineering` | on | Engineering TikZ (thermo, P&ID) |
| `enablecode` | on | Code listings (minted) |
| `enabletables` | on | Table formatting (booktabs) |
| `loadGlossaries` | off | Glossary/acronym support |
| `todonotes` | off | TODO notes |
| `censoring` | off | Redaction/censoring |

### Paper Size

Pass `a5` as an option for A5 paper (sets fontsize=10pt):

```latex
\documentclass[doctype=thesis,a5]{omnilatex}
```

### Color Themes

```latex
\colormode{dark}       % Dark mode
\colormode{light}      % Light mode (default)
\colortheme{midnight}  % Midnight theme
\colortheme{forest}    % Forest theme
\colortheme{rose}      % Rose theme
\colortheme{monochrome} % Monochrome theme
\colortheme{sepia}     % Sepia theme
```

### Citation Styles

```latex
\citationstyle{IEEE}
\citationstyle{APA}
\citationstyle{Nature}
\citationstyle{Chicago}
```

Available: IEEE, ACM, APA, Chicago, Nature, Science, Harvard, Vancouver, MLA.

### Custom Settings

Place a `config/document-settings.sty` in your project to override global settings.
Per-example settings go in `examples/<name>/config/`.

## Project Structure

```
omnilatex.cls                 # Main document class
lib/                          # 27 modules across 9 subdirectories
  core/                       # Build modes, utilities
  layout/                     # Page layout, floats, KOMA-Script, accessibility
  typography/                 # Fonts, math, typesetting, lists
  references/                 # Bibliography, glossary, hyperref, citations
  language/                   # Internationalization (polyglossia, CJK, RTL)
  graphics/                   # Images, SVG, TikZ
  code/                       # Code listings (minted)
  tables/                     # Table formatting
  utils/                      # Colors, themes, TODO notes, censoring
config/
  document-types/             # 26 doctype profiles
  institutions/               # 16 institution configs
examples/                     # 42 example templates
tests/                        # Test suite (pytest + l3build)
specs/                        # Formal specs and Lean 4 proofs
```

## FAQ / Troubleshooting

### "Unknown doctype" warning

Check the doctype spelling. Valid options: `book`, `thesis`, `dissertation`, `manual`,
`article`, `journal`, `inlinepaper`, `technicalreport`, `standard`, `patent`, `cv`,
`cover-letter`, `poster`, `presentation`, `letter`, `dictionary`, `homework`, `exam`,
`research-proposal`, `lecture-notes`, `syllabus`, `handout`, `memo`, `white-paper`,
`invoice`, `recipe`.

### Font warnings (Libertinus, Monaspace)

OmniLaTeX falls back gracefully when fonts are missing. Install optional fonts or
ignore the warnings. Run `python build.py doctor` to check font availability.

### minted / shell-escape errors

Minted requires `-shell-escape`. The `.latexmkrc` enables it by default. If building
manually: `latexmk -lualatex -shell-escape main.tex`. Ensure Pygments is installed.

### Glossary not appearing

Glossaries require bib2gls. Run `biber main && bib2gls main && lualatex main.tex`
manually, or add `loadGlossaries` to your class options.

### CJK characters not rendering

CJK auto-detection requires Haranoaji or Noto CJK fonts (bundled with TeX Live).
Ensure `language=chinese` (or `japanese`/`korean`) is set.

### Overleaf compilation fails

Set compiler to **LuaLaTeX**. Use the Overleaf zip generator:
`bash scripts/make-overleaf-zip.sh thesis`. See `docs/OVERLEAF.md` for details.

### Reproducible builds

Set `SOURCE_DATE_EPOCH` for deterministic PDF output:

```bash
SOURCE_DATE_EPOCH=1700000000 python build.py build-root
```

### Slow compilation

Disable unused modules to speed up builds:

```latex
\documentclass[doctype=thesis,enablecode=false,enableengineering=false]{omnilatex}
```

Use `python build.py build-examples --timings` to identify slow examples.
