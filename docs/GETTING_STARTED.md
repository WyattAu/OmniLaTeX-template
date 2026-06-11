---
title: Getting Started
---

# Getting Started with OmniLaTeX

OmniLaTeX is a universal LaTeX document class supporting 27 doctypes, 21
institutions, and 25 languages. This guide walks you from installation to a
compiled PDF.

## 1. Install

### Option A: Overleaf (quickest)

1. Create a zip locally: `bash scripts/make-overleaf-zip.sh article`
2. On Overleaf: Menu > New Project > Upload Project
3. Set compiler to **LuaLaTeX**: Menu > Compiler > LuaLaTeX
4. Recompile

If OmniLaTeX is on CTAN, it may already be installed on Overleaf. Try
`\documentclass{omnilatex}` directly.

### Option B: Git clone

```bash
git clone https://github.com/WyattAu/OmniLaTeX-template.git
cd OmniLaTeX-template
```

### Option C: TeX Live

```bash
tlmgr install omnilatex
```

### Prerequisites

- TeX Live 2025+ with LuaLaTeX
- `latexmk` (bundled with TeX Live)
- Python 3.10+ (only if using `build.py`)

## 2. Minimal Working Example

Create a file called `main.tex`:

```latex
\documentclass[
    language=english,
    doctype=article,
    institution=none,
]{omnilatex}

\RequirePackage{config/document-settings}
\addbibresource{bib/bibliography.bib}

\begin{document}

\maketitle

\section*{Abstract}
This is my first OmniLaTeX document.

\tableofcontents

\section{Introduction}
Hello, OmniLaTeX~\cite{einstein1905}.

\section{Conclusion}
Everything works.

\printbibliography

\end{document}
```

Set metadata before `\begin{document}`:

```latex
\title{My Document}
\author{Jane Doe}
\date{\today}
```

## 3. Key Configuration Options

All options are passed to `\documentclass` as key-value pairs.

| Option | Values | Default | Purpose |
|--------|--------|---------|---------|
| `doctype` | `article`, `thesis`, `book`, `cv`, `presentation`, `letter`, `memo`, `invoice`, ... | `article` | Document type profile |
| `language` | `english`, `german`, `french`, `spanish`, `chinese`, `arabic`, ... | `english` | Hyphenation and UI strings |
| `institution` | `none`, `tuhh`, `mit`, `stanford`, `eth`, ... | `none` | Institution branding |
| `oneside` / `twoside` | boolean | varies | Page layout |
| `loadGlossaries` | `true` / `false` | `false` | Enable glossary support |
| `titlestyle` | `simple`, `book`, ... | varies | Title page layout |

See the [User Guide](USER_GUIDE.md) for the full list of 27 doctypes and all
available options.

## 4. Building Locally

### latexmk (recommended)

```bash
latexmk -lualatex main.tex
```

`latexmk` handles recompilation automatically when references, citations, or
glossaries change.

### Direct LuaLaTeX

```bash
lualatex main.tex
lualatex main.tex   # run twice for cross-references
```

### build.py

The project includes a Python build tool with incremental caching:

```bash
python build.py build-example minimal-starter   # build a specific example
python build.py build-root                       # build root document
python build.py build                            # build everything
python build.py list-examples                    # list available examples
python build.py watch                            # watch and rebuild on changes
python build.py doctor                           # environment diagnostics
python build.py clean                            # full cleanup
```

Run `python build.py` with no arguments for an interactive menu.

### Docker / Nix

```bash
docker run -v $(pwd):/workspace ghcr.io/wyattau/omnilatex-docker:latest
nix develop
```

## 5. Customization

### Color Themes

OmniLaTeX ships six built-in themes. Apply one with `\usetheme`:

```latex
\usetheme{default}      % white bg, blue accents
\usetheme{midnight}     % navy bg, cyan accents
\usetheme{forest}       % dark green
\usetheme{rose}         % dark pink
\usetheme{monochrome}   % black and white
\usetheme{sepia}        % warm paper tones
```

Override individual color slots after applying a theme:

```latex
\usetheme{default}
\setthemecolor{accent}{red!70!black}
\setthemecolor{link}{teal}
```

Available slots: `bg`, `fg`, `heading`, `body`, `accent`, `blockbg`,
`blockframe`, `link`, `rule`, `codebg`, `footernote`.

Toggle dark/light mode mid-document with `\darkmode` and `\lightmode`.

### Title Page

Set metadata in the preamble and render with `\maketitle`:

```latex
\title{My Thesis}
\subtitle{A Subtitle}
\author{Jane Doe}
\date{\today}
```

Layout varies by doctype and institution.

### Bibliography

OmniLaTeX uses `biblatex` with Biber:

```latex
\addbibresource{bib/bibliography.bib}
```

Cite with `\cite{key}`, `\parencite{key}`, `\textcite{key}`, etc. Print the
bibliography with `\printbibliography`.

## 6. Troubleshooting

**LuaLaTeX not found** -- Ensure TeX Live 2025+ is installed and `lualatex`
is on your PATH (`which lualatex`).

**Missing `config/document-settings`** -- If building outside the repository
structure, ensure the `config/` directory is accessible, or remove the
`\RequirePackage` line.

**Glossary compilation** -- Glossaries require extra passes. Use `latexmk`
(which handles this) or run `lualatex` / `bib2gls` / `lualatex` / `lualatex`
manually.

**Font warnings** -- OmniLaTeX requires LuaLaTeX (pdfLaTeX will not work).
Install TeX Gyre and Latin Modern if fonts are missing, or let fallback fonts
kick in.

**Build cache issues** -- Run `python build.py clean-aux` or
`python build.py clean-example <name>` to clear stale output.

**Reproducible builds** -- Use `python build.py --source-date-epoch=<unix-ts>`
for byte-for-byte reproducibility.

## Next Steps

- [User Guide](USER_GUIDE.md) -- full option reference
- [Overleaf Setup](OVERLEAF.md) -- Overleaf-specific details
- `examples/` -- 48 ready-made example documents
- `python build.py doctor` -- verify your environment
