# Frequently Asked Questions

## Installation

### Docker

```bash
docker run -it --rm -v $(pwd):/workspace ghcr.io/wyattau/omnilatex-docker:latest
python build.py build-example thesis
```

The Docker image includes TeX Live 2026, Pygments, and a pre-warmed `luaotfload`
font cache. No local TeX installation required.

### Nix

```bash
nix develop                    # Enter dev shell with all dependencies
nix build .#                   # Build default package
nix build .#examples-thesis    # Build specific example
```

The flake provides a complete development environment. Run `python build.py doctor`
inside the shell to verify.

### TeX Live (manual)

Requirements:

- TeX Live 2025 or later
- Packages: `collection-fontsextra`, `collection-mathscience`, `collection-latexextra`,
  `collection-luatex`, `collection-langother` (for CJK/RTL)
- Python 3.10+ with `pygments` for minted support
- Biber for biblatex

```bash
tlmgr install collection-latexextra collection-luatex collection-fontsextra
pip install pygments
```

### VS Code

1. Install the **LaTeX Workshop** extension.
2. Set the compiler to LuaLaTeX in `.vscode/settings.json`:

```json
{
    "latex-workshop.latex.tools": [
        {
            "name": "lualatex",
            "command": "latexmk",
            "args": ["-lualatex", "-interaction=nonstopmode", "%DOC%"]
        }
    ]
}
```

3. The `%!TEX TS-program = lualatex` magic comment in `main.tex` also triggers LuaLaTeX.

### Overleaf

1. Generate the Overleaf zip: `bash scripts/make-overleaf-zip.sh thesis`
2. Upload to Overleaf: New Project -> Upload Project
3. Set compiler to **LuaLaTeX**: Menu -> Compiler -> LuaLaTeX
4. Recompile

See `docs/OVERLEAF.md` for detailed instructions, font fallback behavior on
Overleaf, and known limitations.

## Compilation

### Why LuaLaTeX only?

OmniLaTeX requires the LuaTeX engine for:

- `fontspec` with OTF/TTF font loading (Libertinus, Monaspace, Atkinson)
- `luaotfload` for font resolution
- `lualatex-math` for math font integration
- `unicode-math` for OpenType math fonts
- Direct Lua access for build mode detection (`BUILD_MODE` environment variable)
- CJK support via `luaotfload` multiscript

The class enforces this with `\RequireLuaTeX`. XeLaTeX and pdfLaTeX will fail.

### Common compilation errors

**"Fatal error occurred, no output PDF file produced"**

Check the log file for the specific error. Common causes:

- Missing fonts: install optional fonts or accept the fallback (Latin Modern).
- Missing Pygments: `pip install pygments` (required by minted).
- Missing `--shell-escape`: the `.latexmkrc` sets this automatically; if calling
  `lualatex` directly, add `-shell-escape`.

**"Font 'Monaspace Neon' not found"**

This is a warning, not a fatal error. OmniLaTeX falls back to Latin Modern Mono.
To install: download from <https://github.com/chriskapp/neon-monospace> and place
the OTF files in `~/.local/share/fonts/`, then run `luaotfload-tool --update`.

**"Module 'omnilatex-xxx' not found"**

Ensure the `lib/` directory is in the TeX search path. If running from the
cloned repository, this should work automatically. If installed via CTAN, verify
with `kpsewhich omnilatex.cls`.

**"Option clash for package fontspec"**

Remove any `\usepackage{fontspec}` from your preamble. OmniLaTeX loads it.

### Build commands

```bash
latexmk -lualatex main.tex                  # Direct latexmk
python build.py build-root                   # Build root main.tex
python build.py build-example thesis         # Build a specific example
python build.py build-examples -j 8          # Build all examples, 8 parallel
python build.py watch                        # Watch and rebuild on changes
python build.py clean                        # Remove build artifacts
```

## Document Types

### How to choose a document type

| Use Case | Doctype | Base Class |
|----------|---------|------------|
| Academic thesis (bachelor/master/PhD) | `thesis` | scrbook |
| PhD dissertation | `dissertation` | scrbook |
| Research paper / preprint | `article` | scrartcl |
| Journal submission | `journal` | scrartcl |
| arXiv-style inline paper | `inlinepaper` | scrartcl |
| Technical report | `technicalreport` | scrreprt |
| Book / monograph | `book` | scrbook |
| Manual / handbook | `manual` | scrreprt |
| Curriculum vitae | `cv` | scrartcl |
| Cover letter | `cover-letter` | scrartcl |
| Patent specification | `patent` | scrreprt |
| Conference poster | `poster` | scrartcl |
| Presentation slides | `presentation` | scrartcl |
| Formal letter | `letter` | scrartcl |
| White paper | `white-paper` | scrartcl |
| Invoice | `invoice` | scrartcl |
| Memo | `memo` | scrartcl |

### How to switch document types

Change the `doctype` option. No other changes required:

```latex
% Switch from thesis to article:
\documentclass[doctype=article]{omnilatex}
```

Note: switching between chapter-based types (`scrbook`/`scrreprt`) and
non-chapter types (`scrartcl`) may require adjusting `\chapter` commands
to `\section` (or vice versa).

### Aliases

OmniLaTeX recognizes over 55 doctype aliases. Examples:

- `thesis`, `theses` -> `thesis`
- `article`, `articles`, `paper`, `papers` -> `article`
- `cv`, `resume`, `resumes`, `curriculumvitae` -> `cv`
- `technicalreport`, `technical-report`, `techreport` -> `technicalreport`

Unknown doctypes produce a warning and fall back to `book`.

## Languages

### Polyglossia vs babel

OmniLaTeX uses **polyglossia** exclusively. `babel` is not loaded and will
conflict if loaded manually. Polyglossia is the standard language package for
LuaLaTeX and provides the same functionality as babel for all supported languages.

Set the language via the `language` class option:

```latex
\documentclass[doctype=thesis,language=german]{omnilatex}
```

### CJK support

CJK support is auto-loaded when `language` is set to `chinese`, `japanese`, or
`korean`. OmniLaTeX pre-configures CJK fonts with fallback chains:

| Language | Primary Font | Fallback |
|----------|-------------|----------|
| Chinese (Simplified) | Noto Serif CJK SC | Haranoaji Mincho |
| Chinese (Traditional) | Noto Serif CJK SC | Haranoaji Mincho |
| Japanese | Noto Serif CJK JP | Haranoaji Mincho |
| Korean | Noto Sans CJK KR | Noto Serif CJK KR |

Fonts are resolved via `\IfFontExistsTF`. Missing fonts produce a warning, not
an error. Install Noto CJK fonts or Haranoaji (bundled with TeX Live) for best results.

### RTL support

RTL support is auto-loaded for `arabic`, `hebrew`, and `persian`. The
`omnilatex-rtl` module configures bidirectional text. RTL fonts use the
same fallback mechanism:

| Language | Primary Font | Fallback |
|----------|-------------|----------|
| Arabic | Amiri | Noto Naskh Arabic |
| Hebrew | David CLM | Frank Ruehl CLM |
| Persian | Amiri | Noto Naskh Arabic |

Override RTL fonts in the preamble:

```latex
\setArabicFont{Scheherazade New}
\setHebrewFont{Ezra SIL}
```

## Institutions

### How to add a new institution

```bash
python build.py scaffold-institution myuniversity
```

This creates `config/institutions/myuniversity/myuniversity.sty` with a
template including color definitions, logo paths, and metadata fields.
Edit the `.sty` file to match your institution's branding.

### Available institutions

21 pre-built configs: TUHH, TUM, ETH Zurich, MIT, Stanford, Cambridge, Oxford,
Princeton, Yale, Harvard, Columbia, CMU, EPFL, Imperial, TU Delft, Aalto,
Chalmers, KIT, NTNU, U of Toronto, Generic.

Enable with:

```latex
\documentclass[doctype=thesis,institution=eth]{omnilatex}
```

### How to customize an institution

Institution configs are standard `.sty` files. Override colors, logos, and
metadata by editing `config/institutions/<name>/<name>.sty`. The file is loaded
after all OmniLaTeX modules, so you can redefine any command or setting.

## Fonts

### Default font stack

| Slot | Primary | Fallback |
|------|---------|----------|
| Serif (main) | Libertinus Serif | (fontspec default) |
| Sans-serif | Atkinson Hyperlegible Next | Libertinus Sans |
| Monospace | Monaspace Neon | Latin Modern Mono |
| Math | Libertinus Math | (unicode-math default) |
| Unit numbers | Libertinus Serif (Uppercase) | (same as main) |

### How to override fonts

```latex
% In preamble, after \documentclass:
\setMainFont{TeX Gyre Termes}
\setSansFont{Fira Sans}
\setMonoFont[Scale=MatchLowercase]{Fira Code}
\setMathFont{TeX Gyre Termes Math}
```

Each setter checks font existence via `\IfFontExistsTF` and warns (not errors)
if the font is missing.

### Fallback behavior

OmniLaTeX never hard-fails on missing fonts. The fallback chain is:

1. Check if the requested font exists (`\IfFontExistsTF`).
2. If not found, issue a `\ClassWarning` with installation instructions.
3. Use the next font in the fallback chain or the fontspec default.

Run `python build.py doctor` to see which fonts are available and which are
falling back.

## Bibliography

### Citation styles

OmniLaTeX provides 9 pre-configured citation styles via `\citationstyle{...}`:

| Style | Type | Example Output |
|-------|------|---------------|
| `IEEE` | Numeric | `[1]` |
| `ACM` | Numeric | `[1]` |
| `APA` | Author-year | `(Smith, 2024)` |
| `Chicago` | Author-year | `(Smith 2024)` |
| `Nature` | Numeric | `[1]` |
| `Science` | Numeric | `[1]` |
| `Harvard` | Author-year | `(Smith, 2024)` |
| `Vancouver` | Numeric | `[1]` |
| `MLA` | Author-page | `(Smith 42)` |

Call in the preamble:

```latex
\citationstyle{IEEE}
```

The default style is `ext-authoryear` with `autocite=footnote` and `backref`.

### natbib vs biblatex

OmniLaTeX uses **biblatex** exclusively. `natbib` is not loaded and should not
be loaded manually (it conflicts with biblatex). If migrating a natbib document,
substitute commands:

| natbib | biblatex |
|--------|----------|
| `\citep{key}` | `\parencite{key}` |
| `\citet{key}` | `\textcite{key}` |
| `\citeauthor{key}` | `\citeauthor{key}` |
| `\citeyear{key}` | `\citeyear{key}` |
| `\citealt{key}` | `\cite{key}` |
| `\citealp{key}` | `\parencite*{key}` |

### Custom bibliography

```latex
% Override biblatex options in preamble:
\ExecuteBibliographyOptions{
    maxnames=3,
    sorting=nyt,
    backref=false,
}

% Custom bibliography environment:
\printbibliography[heading=bibintoc,title={References}]
```

## Troubleshooting

### Analyzing log files

```bash
# Check for errors and warnings:
python build.py doctor

# Search log for specific issues:
grep -i "error\|warning\|fatal" main.log | head -50

# Check font loading:
grep "omnilatex-fonts" main.log

# Check module loading:
grep "omnilatex" main.log | head -30
```

### Common warnings

**"Font 'X' not found. Y font unchanged."**

The specified font is not installed. OmniLaTeX will use a fallback. Either
install the font or override with `\setMainFont{...}` to use a different font.

**"Unknown doctype 'X'"**

The `doctype` value is not recognized. OmniLaTeX falls back to `book`. Check
spelling against the list in the User Guide or `omnilatex.cls`.

**"Option clash for package X"**

Package X is already loaded by OmniLaTeX. Remove the duplicate `\usepackage{X}`
from your preamble.

**"Package biblatex Warning: 'X'"**

Biblatex configuration warnings. Usually non-fatal. Adjust biblatex options
with `\ExecuteBibliographyOptions{...}` in the preamble if needed.

### Build errors

**Exit code 1 with no clear error**

Run with `--verbose`:

```bash
python build.py build-root --verbose
```

Or check `build/build-root/output.log`.

**Minted / Pygments errors**

```bash
pip install pygments          # Install Pygments
# Verify:
python -c "import pygments; print(pygments.__version__)"
```

Minted also requires `--shell-escape`. The `.latexmkrc` sets this automatically.

**Glossary not appearing**

Glossaries require `bib2gls` in addition to Biber:

```bash
biber main && bib2gls main && lualatex main.tex
```

Or use `python build.py build-root` which handles the full build pipeline.

## Performance

### Build speed

Expected compile times (single run, warm cache):

| Document Type | Expected Time |
|---------------|--------------|
| Simple (article, cv, letter) | 15-30s |
| Medium (thesis, book, report) | 30-60s |
| Complex (thesis with TikZ, minted) | 60-120s |

First runs are slower due to `luaotfload` font scanning (~5-10s overhead).

### Speeding up builds

Disable unused modules:

```latex
\documentclass[
    doctype=article,
    enablemath=false,
    enabletikz=false,
    enableengineering=false,
    enablecode=false,
    enabletables=false,
]{omnilatex}
```

Use parallel compilation for multiple documents:

```bash
python build.py build-examples -j 8
```

### Cache usage

OmniLaTeX does not implement custom caching. It relies on:

- **latexmk** dependency tracking (`.fdb_latexmk`) for incremental rebuilds.
- **luaotfload** font cache (`luaotfload-tool --update`) for font resolution.
- **minted** cache (`.minted` directory) for code listing cache.
- **Docker** image with pre-warmed font cache for CI.

### Reproducible builds

```bash
SOURCE_DATE_EPOCH=1700000000 python build.py build-root
```

This produces PDFs with deterministic timestamps, IDs, and font embeddings.
Page counts and file sizes are consistent across machines, though LuaTeX font
subsetting may produce minor differences in the binary layout.

### Profiling

```bash
python build.py --mode prod --timings build-all
```

Outputs `build/metrics.json` with per-example wall-clock time, PDF size, and
package load times.

## Distribution

### CTAN availability

OmniLaTeX is not yet on CTAN. Use the Git repository:

```bash
git clone https://github.com/WyattAu/OmniLaTeX-template.git
```

Once published on CTAN:

```bash
tlmgr install omnilatex
```

### Overleaf compatibility

OmniLaTeX works on Overleaf with the LuaLaTeX compiler. Use the Overleaf zip
generator:

```bash
bash scripts/make-overleaf-zip.sh thesis
```

Known Overleaf limitations:

- Some optional fonts (Monaspace Neon, Atkinson Hyperlegible Next) may not be
  available; OmniLaTeX falls back gracefully.
- `--shell-escape` is enabled by default on Overleaf, so minted works.
- `bib2gls` may not be available; glossary features may require manual workarounds.
