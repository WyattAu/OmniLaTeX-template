---
title: USER GUIDE
---
# OmniLaTeX User Guide

## Quick Start

See the [Quick Start](https://github.com/WyattAu/OmniLaTeX-template/blob/main/README.md#quick-start) section in the main README for clone, build, Docker, and Nix instructions.

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

OmniLaTeX provides 27 document type profiles across 3 KOMA-Script base classes.
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

## Document Type Reference

### article

Base class: `scrartcl`. Research article with abstract, keywords, and DOI support.

```latex
\documentclass[doctype=article]{omnilatex}
\begin{document}
\maketitle
\section{Introduction}
\end{document}
```

### book

Base class: `scrbook`. Full book with chapters, publisher metadata, edition, and ISBN fields.

```latex
\documentclass[doctype=book]{omnilatex}
\begin{document}
\maketitle
\chapter{Chapter One}
\end{document}
```

### report

Base class: `scrreprt`. General-purpose report with chapters, `open=any` page style.

```latex
\documentclass[doctype=report]{omnilatex}
\begin{document}
\maketitle
\chapter{Findings}
\end{document}
```

### thesis

Base class: `scrbook`. Academic thesis with advisor, committee, and declaration of authorship.

```latex
\documentclass[doctype=thesis]{omnilatex}
\begin{document}
\maketitle
\chapter{Introduction}
\end{document}
```

### dissertation

Base class: `scrbook`. PhD dissertation with front matter, committee, and extended metadata.

```latex
\documentclass[doctype=dissertation]{omnilatex}
\begin{document}
\maketitle
\chapter{Introduction}
\end{document}
```

### homework

Base class: `scrartcl`. Homework assignment with numbered exercises and solution environments.

```latex
\documentclass[doctype=homework]{omnilatex}
\begin{document}
\maketitle
\section{Problem 1}
\end{document}
```

### exam

Base class: `scrartcl`. Examination paper with questions, point values, and answer spaces.

```latex
\documentclass[doctype=exam]{omnilatex}
\begin{document}
\maketitle
\section{Section A}
\end{document}
```

### syllabus

Base class: `scrartcl`. Course syllabus with grading policy, schedule, and instructor info.

```latex
\documentclass[doctype=syllabus]{omnilatex}
\begin{document}
\maketitle
\section{Course Overview}
\end{document}
```

### lecture-notes

Base class: `scrartcl`. Lecture notes with theorem, definition, and proof environments.

```latex
\documentclass[doctype=lecture-notes]{omnilatex}
\begin{document}
\maketitle
\section{Topic One}
\end{document}
```

### letter

Base class: `scrartcl`. Formal letter with recipient address, subject line, and closing.

```latex
\documentclass[doctype=letter]{omnilatex}
\begin{document}
\maketitle
Dear Recipient,
\end{document}
```

### memo

Base class: `scrartcl`. Memorandum with TO/FROM/CC/RE header fields.

```latex
\documentclass[doctype=memo]{omnilatex}
\begin{document}
\maketitle
\section{Background}
\end{document}
```

### cover-letter

Base class: `scrartcl`. Cover letter with recipient and sender metadata, single-page layout.

```latex
\documentclass[doctype=cover-letter]{omnilatex}
\begin{document}
\maketitle
Dear Hiring Manager,
\end{document}
```

### cover-letter-formal

Base class: `scrartcl`. Formal variant of cover letter with structured sections.

```latex
\documentclass[doctype=cover-letter-formal]{omnilatex}
\begin{document}
\maketitle
\end{document}
```

### cv

Base class: `scrartcl`. Curriculum vitae with photo, links, summary, and sectioned entries.

```latex
\documentclass[doctype=cv]{omnilatex}
\begin{document}
\maketitle
\section{Experience}
\end{document}
```

### cv-twopage

Base class: `scrartcl`. Two-page CV variant with extended sections.

```latex
\documentclass[doctype=cv-twopage]{omnilatex}
\begin{document}
\maketitle
\section{Experience}
\end{document}
```

### invoice

Base class: `scrartcl`. Commercial invoice with itemized table, totals, and payment terms.

```latex
\documentclass[doctype=invoice]{omnilatex}
\begin{document}
\maketitle
\end{document}
```

### poster

Base class: `scrartcl`. Conference poster in A1 landscape with column layout.

```latex
\documentclass[doctype=poster]{omnilatex}
\begin{document}
\maketitle
\section{Results}
\end{document}
```

### presentation

Base class: `scrartcl`. Presentation slides using KOMA-based layout (non-Beamer).

```latex
\documentclass[doctype=presentation]{omnilatex}
\begin{document}
\maketitle
\section{Slide Title}
\end{document}
```

### beamer

Base class: `beamer`. Beamer-based slides with full theme and overlay support.

```latex
\documentclass[doctype=beamer]{omnilatex}
\begin{document}
\begin{frame}{Title}
Content here.
\end{frame}
\end{document}
```

### research-proposal

Base class: `scrreprt`. Research proposal with budget, timeline, and methodology sections.

```latex
\documentclass[doctype=research-proposal]{omnilatex}
\begin{document}
\maketitle
\chapter{Objectives}
\end{document}
```

### patent

Base class: `scrreprt`. Patent specification with claims, abstract, and formal structure.

```latex
\documentclass[doctype=patent]{omnilatex}
\begin{document}
\maketitle
\chapter{Description}
\end{document}
```

### standard

Base class: `scrreprt`. Standards document with ICS codes and designation fields.

```latex
\documentclass[doctype=standard]{omnilatex}
\begin{document}
\maketitle
\chapter{Scope}
\end{document}
```

### white-paper

Base class: `scrartcl`. White paper / position paper for policy or technology briefings.

```latex
\documentclass[doctype=white-paper]{omnilatex}
\begin{document}
\maketitle
\chapter{Executive Summary}
\end{document}
```

### technical-report

Base class: `scrreprt`. Technical report with report number, confidentiality, and chapters.

```latex
\documentclass[doctype=technical-report]{omnilatex}
\begin{document}
\maketitle
\chapter{Methodology}
\end{document}
```

### journal

Base class: `scrartcl`. Journal article with volume, issue, highlights, and DOI.

```latex
\documentclass[doctype=journal]{omnilatex}
\begin{document}
\maketitle
\section{Abstract}
\end{document}
```

### recipe

Base class: `scrartcl`. Recipe card with ingredients list, instructions, and yield.

```latex
\documentclass[doctype=recipe]{omnilatex}
\begin{document}
\maketitle
\section{Ingredients}
\end{document}
```

### dictionary

Base class: `scrbook`. Dictionary/lexicon with series and publisher info, twoside layout.

```latex
\documentclass[doctype=dictionary]{omnilatex}
\begin{document}
\maketitle
\chapter{A}
\end{document}
```

### handout

Base class: `scrartcl`. Two-column handout with key concept boxes and summary sections.

```latex
\documentclass[doctype=handout]{omnilatex}
\begin{document}
\maketitle
\section{Key Concepts}
\end{document}
```

### manual

Base class: `scrreprt`. Product manual/handbook with version, support info, and chapters.

```latex
\documentclass[doctype=manual]{omnilatex}
\begin{document}
\maketitle
\chapter{Getting Started}
\end{document}
```

## Institutions

OmniLaTeX ships 21 institution configurations. Enable with
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
| Aalto University | `aalto` | Blue/Red |
| Chalmers University of Technology | `chalmers` | Blue/Light Blue |
| Karlsruhe Institute of Technology | `kit` | Green/Black |
| NTNU | `ntnu` | Dark Blue |
| University of Toronto | `uoft` | Navy/Blue |
| Generic | `generic` | User-defined (template for new institutions) |

Add a new institution:

```bash
python build.py scaffold-institution myuniversity
```

See `config/institutions/README.md` for details.

## Languages

OmniLaTeX uses Polyglossia for language support. Set with
`\documentclass[language=<lang>]{omnilatex}`.

### Languages with full OmniLaTeX translations

18 languages have custom UI-string translations (Glossary, Supervisor,
Examiner, compiled-on timestamp, etc.):

| Language | Key | Coverage |
|----------|-----|----------|
| English | `english` | Base (all keys) |
| German | `german` | Base (all keys) |
| French | `french` | Base (all keys) |
| Spanish | `spanish` | Base (all keys) |
| Russian | `russian` | Full (25+ keys) |
| Italian | `italian` | Full (25+ keys) |
| Portuguese | `portuguese` | Full (25+ keys) |
| Dutch | `dutch` | Full (25+ keys) |
| Czech | `czech` | Full (25+ keys) |
| Polish | `polish` | Full (25+ keys) |
| Greek | `greek` | Full (25+ keys) |
| Turkish | `turkish` | Full (25+ keys) |
| Vietnamese | `vietnamese` | Full (25+ keys) |
| Hindi | `hindi` | Full (25+ keys) |
| Swedish | `swedish` | Full (25+ keys) |
| Finnish | `finnish` | Full (25+ keys) |
| Danish | `danish` | Full (25+ keys) |
| Norwegian | `norsk` | Full (25+ keys) |

### Other languages (standard captions via Polyglossia)

Chinese (Simplified + Traditional), Japanese, Korean, Arabic, Hebrew, Persian,
Catalan, Brazilian Portuguese, Romanian, Ukrainian, Slovak, Slovenian,
Serbian, Croatian, Bulgarian, Mongolian.

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
python build.py build-examples           # Build all 48 examples
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

See the [Project Structure](https://github.com/WyattAu/OmniLaTeX-template/blob/main/README.md#project-structure) section in the main README.

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
