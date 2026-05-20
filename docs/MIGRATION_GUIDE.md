# Migration Guide

This guide covers migrating existing LaTeX documents from standard document classes
and popular class families to OmniLaTeX.

## Overview

OmniLaTeX replaces the conventional `\documentclass{article}` workflow with a single
universal class that maps to appropriate KOMA-Script base classes. Benefits:

- Eliminates per-class preamble boilerplate (font setup, package loading, caption configuration).
- Consistent interface across all document types via `doctype` key.
- Automatic font stack, bibliography, hyperref, and language configuration.
- Module loading only what is needed; disable unused features to speed compilation.
- 21 pre-built institution configurations.

OmniLaTeX is not a drop-in replacement. It reconfigures defaults (fonts, captions,
spacing) and uses key-value options instead of positional class options. Most
migration work involves removing preamble commands that OmniLaTeX handles automatically
and adjusting the `\documentclass` line.

## Prerequisites

- **TeX Live 2025** or later. OmniLaTeX uses LuaLaTeX-only packages
  (`luaotfload`, `lualatex-math`, `fontspec` with OTF/TTF fonts).
- **LuaLaTeX engine**. XeLaTeX and pdfLaTeX are not supported. The class file
  enforces this via `\RequireLuaTeX`.
- **Biber** for bibliography processing (biblatex backend).
- **Pygments** (Python) if using the `minted` code listing module.

Verify your environment:

```bash
lualatex --version    # Must be LuaHBTeX 1.21+
python build.py doctor
```

## Migration from `article`

### Step 1: Change the document class

Before:

```latex
\documentclass[12pt,a4paper,twoside]{article}
```

After:

```latex
\documentclass[
    doctype=article,
    language=english,
]{omnilatex}
```

OmniLaTeX maps `doctype=article` to `scrartcl` (KOMA-Script article) with
`bibliography=totoc,numbers=noenddot,parskip=half`.

### Step 2: Remove redundant preamble packages

OmniLaTeX auto-loads these. Remove any `\usepackage` lines for them:

| Package | OmniLaTeX Module |
|---------|-----------------|
| `fontspec` | `omnilatex-fonts` |
| `amsmath`, `amssymb`, `unicode-math` | `omnilatex-fonts` |
| `siunitx` | `omnilatex-math` |
| `graphicx` | `omnilatex-base` (via KOMA) |
| `hyperref` | `omnilatex-hyperref` |
| `caption`, `subcaption` | `omnilatex-floats` |
| `booktabs` | `omnilatex-tables` |
| `biblatex` | `omnilatex-biblio` |
| `polyglossia` or `babel` | `omnilatex-i18n` |
| `xcolor` | `omnilatex-colors` |
| `etoolbox` | `omnilatex-base` |
| `microtype` | `omnilatex-typesetting` |
| `fontawesome5` | `omnilatex-fonts` |
| `tikz` | `omnilatex-tikz-core` |
| `minted` | `omnilatex-listings` |
| `import` | `omnilatex-base` |
| `datetime2` | `omnilatex-base` |

### Step 3: Adjust bibliography

Before:

```latex
\usepackage[style=authoryear,backend=biber]{biblatex}
\addbibresource{references.bib}
```

After:

```latex
% No \usepackage{biblatex} needed -- OmniLaTeX loads it
\addbibresource{bib/bibliography.bib}

% Optionally change citation style:
% \citationstyle{IEEE}
```

OmniLaTeX defaults to `style=ext-authoryear` with `autocite=footnote` and
`backref`. To switch styles, call `\citationstyle{...}` in the preamble.

### Step 4: Adjust title and metadata

Before:

```latex
\title{My Paper}
\author{Jane Doe}
\date{\today}
\maketitle
```

After (same commands work; place metadata in `config/document-settings.sty`):

```latex
% In config/document-settings.sty:
\title{My Paper}
\author{Jane Doe}
\date{\DTMtoday{}}

% In main.tex:
\maketitle
```

### Step 5: Remove font configuration

Before:

```latex
\usepackage{fontspec}
\setmainfont{TeX Gyre Pagella}
\setsansfont{TeX Gyre Heros}
\setmonofont{Inconsolata}
```

After:

```latex
% Remove all font configuration lines.
% OmniLaTeX defaults: Libertinus Serif, Atkinson Hyperlegible Next (sans),
% Monaspace Neon (mono), Libertinus Math.
%
% To override (in preamble after \documentclass):
% \setMainFont{TeX Gyre Pagella}
% \setSansFont{TeX Gyre Heros}
% \setMonoFont{Inconsolata}
```

## Migration from `report` / `book`

### Document class mapping

| Standard Class | OmniLaTeX Equivalent |
|---------------|---------------------|
| `\documentclass{report}` | `\documentclass[doctype=technicalreport]{omnilatex}` |
| `\documentclass{book}` | `\documentclass[doctype=book]{omnilatex}` |
| `\documentclass{report}` (thesis) | `\documentclass[doctype=thesis]{omnilatex}` |

### Chapter structure

`\chapter`, `\section`, `\subsection` work identically. OmniLaTeX uses
KOMA-Script's `scrbook`/`scrreprt` as base classes, so the chapter/section
hierarchy is preserved.

Key differences:

- `doctype=thesis` and `doctype=book` use `scrbook` (chapters start on odd pages by default, `open=right`).
- `doctype=technicalreport` and `doctype=manual` use `scrreprt` (chapters start on any page, `open=any`).
- `\chapterprefix` is enabled for book types, disabled for report types.

### Front and back matter

Before:

```latex
\frontmatter
\tableofcontents
\mainmatter
\chapter{Introduction}
...
\backmatter
\appendix
```

After:

```latex
% OmniLaTeX provides the same \frontmatter/\mainmatter/\backmatter commands
% via KOMA-Script. The template organizes content via import:
\begin{document}
\import{content/}{frontmatter}
\import{content/}{mainmatter}
\import{content/}{backmatter}
\end{document}
```

### Binding correction

Before:

```latex
\usepackage[a4paper,left=30mm,right=25mm,top=25mm,bottom=25mm]{geometry}
```

After:

```latex
% Remove geometry. Use KOMA-Script typearea instead:
\documentclass[doctype=thesis,BCOR=5mm]{omnilatex}

% Or override margins in the preamble:
% \setCustomMargins{30mm}{25mm}{25mm}{25mm}
```

## Migration from KOMA-Script (scrartcl, scrreprt, scrbook)

OmniLaTeX is built on KOMA-Script. Most KOMA-Script options pass through to the
underlying base class. The following table maps common KOMA-Script options to
OmniLaTeX equivalents.

### Option mapping

| KOMA-Script Option | OmniLaTeX Equivalent | Notes |
|---|---|---|
| `fontsize=12pt` | `fontsize=12pt` (pass-through) | Supported as passthrough option |
| `parskip=half` | Default for article types | Set automatically per doctype |
| `parskip=full` | `parskip=full` (pass-through) | |
| `numbers=noenddot` | Default for all types | Set automatically |
| `bibliography=totoc` | Default for all types | Set automatically |
| `listof=totoc` | Default for book/report types | Set automatically |
| `chapterprefix=true` | Default for book types | Set automatically |
| `open=right` | Default for book types | Set automatically |
| `open=any` | Default for report types | Set automatically |
| `twoside` | `twoside` (pass-through) | |
| `oneside` | `oneside` (pass-through) | |
| `BCOR=5mm` | `BCOR=5mm` (pass-through) | |
| `DIV=12` | `DIV=12` (pass-through) | |
| `titlepage=true` | Default for most types | |
| `paper=a5` | `a5` (shorthand) | Also sets `fontsize=10pt` |

### KOMA-Script commands

KOMA-Script commands that OmniLaTeX does not redefine continue to work:

- `\KOMAoption{...}{...}` / `\KOMAoptions{...}`
- `\addtokomafont{...}{...}`
- `\setkomafont{...}{...}`
- `\recalctypearea`
- `\dedication{...}`
- `\publishers{...}`

### Module loading

KOMA-Script packages that OmniLaTeX wraps:

| KOMA-Script Package | OmniLaTeX Equivalent | Status |
|---|---|---|
| `scrpage2` / `scrlayer-scrpage` | Loaded by `omnilatex-koma` | Auto-configured |
| `scrhack` | Loaded by `omnilatex-base` | Auto-configured |
| `tocbasic` | Loaded by KOMA-Script base | Available |
| `scrextend` | Loaded by KOMA-Script base | Available |

## Migration from `memoir`

### Key differences

| Feature | memoir | OmniLaTeX |
|---------|--------|-----------|
| Base class | Custom | KOMA-Script (`scrbook`/`scrreprt`/`scrartcl`) |
| Chapter styles | `\chapterstyle{...}` | KOMA-Script `chapterprefix` + `omnilatex-koma` |
| Page styles | `\pagestyle{...}` memoir variants | `scrlayer-scrpage` via `omnilatex-koma` |
| Margin notes | `\sidebar`, `\sidepar` | `\marginpar` (KOMA-Script) |
| Spacing | `\OnehalfSpacing`, `\DoubleSpacing` | `\documentlinespacing{onehalf}` |
| Font size | `\changefontsizes{...}` | `\documentfontsize{12pt}` |
| Table of contents | Memoir's `\maxtocdepth` | KOMA-Script `tocdepth` + `tocbasic` |
| Floats/captions | Memoir's built-in | `caption` package via `omnilatex-floats` |
| Epigraphs | `\epigraph{...}{...}` | Not built-in; add `\usepackage{epigraph}` |

### Command substitution

| memoir Command | OmniLaTeX Equivalent |
|---|---|
| `\OnehalfSpacing` | `\documentlinespacing{onehalf}` |
| `\DoubleSpacing` | `\documentlinespacing{double}` |
| `\SingleSpacing` | `\documentlinespacing{single}` or remove |
| `\checkandfixthelayout` | `\recalctypearea` (KOMA-Script) |
| `\chapterstyle{bianchi}` | Not directly equivalent; use KOMA-Script chapter formatting |
| `\makechapterstyle{...}{...}` | Redefine `\chapterformat` or use `titlesec` |
| `\settypeblocksize{...}{...}{...}` | `\documentlayout{DIV=...}` or `\setCustomMargins{...}` |
| `\setmarginnotes{...}{...}{...}` | KOMA-Script margin note settings |
| `\marginalfootnote` | Standard `\footnote` (KOMA-Script handles margin footnotes) |

## Common Issues and Solutions

### Missing packages

OmniLaTeX auto-loads many common packages. If you see "package already loaded"
warnings, remove the duplicate `\usepackage` call from your preamble. Run
`python build.py doctor` to get a report on which packages OmniLaTeX provides.

### Font changes

OmniLaTeX sets Libertinus Serif / Monaspace Neon / Atkinson Hyperlegible Next /
Libertinus Math by default. Documents that relied on Computer Modern or Latin
Modern will look different.

To revert to a closer-to-default appearance:

```latex
% In preamble:
\setMainFont{Latin Modern Roman}
\setSansFont{Latin Modern Sans}
\setMonoFont{Latin Modern Mono}
\setMathFont{Latin Modern Math}
```

Font override commands check font existence and warn (not error) on missing fonts.

### Option syntax changes

OmniLaTeX uses key-value options exclusively. Positional options from standard
classes are not supported directly.

Before:

```latex
\documentclass[12pt,twoside,draft]{article}
```

After:

```latex
\documentclass[
    doctype=article,
    twoside,
]{omnilatex}
% Note: 'draft' is not a direct OmniLaTeX option.
% Pass it through: OmniLaTeX forwards unknown options to the base KOMA-Script class.
```

Unknown options are forwarded to the underlying KOMA-Script base class via
`\DeclareDefaultOption`. Standard KOMA-Script options (`DIV`, `BCOR`, `twoside`,
`oneside`, `fontsize`, etc.) work as pass-through.

### Bibliography configuration

OmniLaTeX uses `biblatex` with `biber` backend. The `natbib` package is not
loaded. If your document uses `natbib` commands:

| natbib Command | biblatex Equivalent |
|---|---|
| `\citep{...}` | `\parencite{...}` or `\cite[see][]{...}` |
| `\citet{...}` | `\textcite{...}` |
| `\citeauthor{...}` | `\citeauthor{...}` (same) |
| `\citeyear{...}` | `\citeyear{...}` (same) |
| `\citealt{...}` | `\cite{...}` |
| `\citealp{...}` | `\parencite*{...}` |

Switch citation style with `\citationstyle{IEEE}` (available: IEEE, ACM, APA,
Chicago, Nature, Science, Harvard, Vancouver, MLA).

### Float and caption customization

OmniLaTeX pre-configures captions via the `caption` package:

```latex
% Default OmniLaTeX caption settings:
%   format=plain, textformat=period, font=small,
%   labelfont={sf,bf}, labelsep=slash (colon+space)
```

To customize:

```latex
% In preamble:
\captionsetup{
    font=normalsize,
    labelfont={bf},
    labelsep=period,
}
```

Subfigures use `subcaption` (loaded by `omnilatex-floats`). The `subfigure`
and `subfig` packages are not needed and will conflict if loaded.

## Command Reference

### Document structure

| Standard LaTeX | OmniLaTeX |
|---|---|
| `\documentclass{article}` | `\documentclass[doctype=article]{omnilatex}` |
| `\documentclass{report}` | `\documentclass[doctype=technicalreport]{omnilatex}` |
| `\documentclass{book}` | `\documentclass[doctype=book]{omnilatex}` |
| `\documentclass[twoside]{book}` | `\documentclass[doctype=book,twoside]{omnilatex}` |
| `\tableofcontents` | `\tableofcontents` (same) |
| `\listoffigures` | `\listoffigures` (same) |
| `\listoftables` | `\listoftables` (same) |
| `\appendix` | `\appendix` (same) |
| `\frontmatter` | `\frontmatter` (same) |
| `\mainmatter` | `\mainmatter` (same) |
| `\backmatter` | `\backmatter` (same) |

### Typography

| Standard LaTeX | OmniLaTeX |
|---|---|
| `\usepackage{setspace}\onehalfspacing` | `\documentlinespacing{onehalf}` |
| `\usepackage{geometry}` | Remove; use `BCOR`, `DIV`, or `\setCustomMargins` |
| `\usepackage{fontspec}\setmainfont{...}` | `\setMainFont{...}` |
| `\linespread{1.5}` | `\documentlinespacing{1.5}` |

### Cross-references and links

| Standard LaTeX | OmniLaTeX |
|---|---|
| `\usepackage{hyperref}` | Remove; loaded by `omnilatex-hyperref` |
| `\usepackage{cleveref}` | Remove; loaded by `omnilatex-hyperref` |
| `\cref{...}` | `\cref{...}` (same) |
| `\autoref{...}` | `\autoref{...}` (same) |
| `\url{...}` | `\url{...}` (same) |

### Bibliography

| Standard LaTeX | OmniLaTeX |
|---|---|
| `\usepackage[...]{biblatex}` | Remove; loaded by `omnilatex-biblio` |
| `\printbibliography` | `\printbibliography` (same) |
| `\parencite{...}` | `\parencite{...}` (same) |
| `\textcite{...}` | `\textcite{...}` (same) |
| `\bibliography{file}` | `\addbibresource{file.bib}` |
| `\bibliographystyle{plain}` | `\citationstyle{IEEE}` or similar |

### Graphics and floats

| Standard LaTeX | OmniLaTeX |
|---|---|
| `\usepackage{graphicx}` | Remove; loaded by KOMA-Script |
| `\usepackage{caption}` | Remove; loaded by `omnilatex-floats` |
| `\usepackage{subcaption}` | Remove; loaded by `omnilatex-floats` |
| `\usepackage{float}` | Remove; use KOMA-Script float handling |
| `\usepackage{booktabs}` | Remove; loaded by `omnilatex-tables` |

### Math

| Standard LaTeX | OmniLaTeX |
|---|---|
| `\usepackage{amsmath}` | Remove; loaded by `omnilatex-fonts` |
| `\usepackage{amssymb}` | Remove; loaded by `omnilatex-fonts` |
| `\usepackage{mathtools}` | Remove; loaded by `omnilatex-math` |
| `\usepackage{siunitx}` | Remove; loaded by `omnilatex-math` |
| `\usepackage{unicode-math}` | Remove; loaded by `omnilatex-fonts` |

### Code listings

| Standard LaTeX | OmniLaTeX |
|---|---|
| `\usepackage{listings}` | Use `\usepackage{minted}` (loaded by `omnilatex-listings`) or `enablecode=true` |
| `\usepackage{minted}` | Remove; loaded by `omnilatex-listings` when `enablecode=true` (default) |
