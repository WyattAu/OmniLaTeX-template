# Contributing to OmniLaTeX

Thank you for your interest in contributing! This guide covers everything
you need to create institution configs, add languages, extend doctypes,
and submit changes.

## Table of Contents

- [Development Setup](#development-setup)
- [Architecture Overview](#architecture-overview)
- [Adding an Institution Config](#adding-an-institution-config)
- [Adding a Language](#adding-a-language)
- [Adding a Document Type](#adding-a-document-type)
- [Code Style](#code-style)
- [Submitting Changes](#submitting-changes)
- [Changelog Format](#changelog-format)

---

## Development Setup

### Option 1: Docker (recommended, zero setup)

```bash
git clone https://github.com/WyattAu/OmniLaTeX-template.git
cd OmniLaTeX-template
docker run -it --rm -v $(pwd):/workspace ghcr.io/wyattau/omnilatex-docker:latest
python build.py test
```

### Option 2: Nix

```bash
git clone https://github.com/WyattAu/OmniLaTeX-template.git
cd OmniLaTeX-template
nix develop
python build.py test
```

### Option 3: Local TeX Live

Requires TeX Live 2024+ with LuaLaTeX, Python 3.10+.

```bash
git clone https://github.com/WyattAu/OmniLaTeX-template.git
cd OmniLaTeX-template
python build.py preflight    # Check your environment
python build.py test
```

---

## Architecture Overview

```
omnilatex.cls                    # Entry point: parses options, resolves doctype,
                                 # loads KOMA-Script base class, loads modules
  │
  ├── config/document-types/*.sty    # Doctype profiles (thesis, article, cv, ...)
  │     Define: page layout, font size, spacing, title page, section depth
  │
  ├── config/institutions/*/NAME.sty # Institution branding (logos, colors, links)
  │     Define: logo paths, color palette, translations, custom commands
  │
  ├── lib/core/                     # Build mode detection, utilities
  ├── lib/layout/                   # Page layout, floats, KOMA-Script config
  ├── lib/typography/               # Fonts, math, typesetting, lists
  ├── lib/references/               # Bibliography, glossary, hyperref
  ├── lib/language/                 # Polyglossia, translations
  ├── lib/graphics/                 # Images, SVG, TikZ
  ├── lib/code/                     # Code listings (minted)
  ├── lib/tables/                   # Table formatting
  └── lib/utils/                    # Colors, TODO notes, censoring
```

### Option Resolution Flow

```
User writes:  \documentclass[doctype=thesis,institution=tuhh,language=german]{omnilatex}
                        │              │                    │
                        ▼              ▼                    ▼
              Resolve alias →  Load config/           Set polyglossia
              "thesis" →       institutions/           default language
              base class       tuhh/tuhh.sty
              "scrbook"
                        │
                        ▼
              Load config/document-types/thesis.sty
              (page layout, font size, title page, spacing)
                        │
                        ▼
              Load 21 modules (conditional on enable* flags)
```

### Key Files

| File | Purpose |
|------|---------|
| `omnilatex.cls` | Document class — option parsing, doctype resolution, module loading |
| `build.lua` | l3build config — unit test runner for LaTeX modules |
| `build.py` | Build orchestrator — compile, test, watch, doctor |
| `.latexmkrc` | latexmk config — compilation flags, SDE support, multi-pass |
| `specs/option_schema.toml` | Formal schema of all 10 options and 46 aliases |
| `specs/module_contracts/*.toml` | Interface contracts for all 21 modules |

---

## Adding an Institution Config

Create a pluggable branding config for a university, company, or organization.

### Step 1: Create the directory

```bash
mkdir -p config/institutions/myuniversity
```

### Step 2: Create the config file

`config/institutions/myuniversity/myuniversity.sty`:

```latex
\NeedsTeXFormat{LaTeX2e}
\ProvidesPackage{config/institutions/myuniversity/myuniversity}[
  2026-01-01 v1.0.0 MyUniversity Institution Configuration
]

% ── Logo ──────────────────────────────────────────────
\DeclareTranslation{english}{LogoInstitution}{%
  \includegraphics[height=3cm]{assets/logos/myuniversity/logo_en}%
}
\DeclareTranslation{german}{LogoInstitution}{%
  \includegraphics[height=3cm]{assets/logos/myuniversity/logo_de}%
}

% ── Links ─────────────────────────────────────────────
\DeclareTranslation{english}{LinkInstitution}{https://www.myuniversity.edu}
\DeclareTranslation{german}{LinkInstitution}{https://www.myuniversity.de}

% ── Colors ────────────────────────────────────────────
\definecolor{universityprimary}{RGB}{0, 63, 114}
\definecolor{universitysecondary}{RGB}{0, 113, 188}

% ── Custom Commands ───────────────────────────────────
% Add any institution-specific commands here.
% These are available in all documents using institution=myuniversity.
```

### Step 3: Add logo assets

```bash
mkdir -p assets/logos/myuniversity
# Place logo_en.pdf and logo_de.pdf here
```

### Step 4: Test it

```latex
% In any example .tex file:
\documentclass[doctype=thesis,institution=myuniversity]{omnilatex}
```

```bash
python build.py build-example minimal-starter
```

### Step 5: Add to integration matrix

Edit `.github/workflows/integration-matrix.yml` and add your institution
to the matrix if desired.

---

## Adding a Language

OmniLaTeX uses [polyglossia](https://ctan.org/pkg/polyglossia) for language
support. Most languages work out of the box — the main task is adding
OmniLaTeX-specific translations (captions, TOC headings, etc.).

### Step 1: Verify polyglossia support

Check that your language is supported by polyglossia:
https://ctan.org/pkg/polyglossia

Most major languages (French, Spanish, Italian, Portuguese, Chinese,
Japanese, Russian, Arabic, etc.) are supported.

### Step 2: Add to secondary languages

Edit `lib/language/omnilatex-i18n.sty`, find the `\setotherlanguages` line,
and add your language:

```latex
\setotherlanguages{german,english,french,spanish}
```

### Step 3: Add OmniLaTeX-specific translations

In `lib/language/omnilatex-i18n.sty`, add translations for any
OmniLaTeX-specific strings:

```latex
% French translations
\DeclareTranslation{french}{First}{1\textsuperscript{re}}
\DeclareTranslation{french}{ListOfFigures}{Liste des figures}
\DeclareTranslation{french}{ListOfTables}{Liste des tableaux}
\DeclareTranslation{french}{Abbreviations}{Abréviations}
% ... add more as needed
```

### Step 4: Test it

```latex
\documentclass[doctype=article,language=french]{omnilatex}
\begin{document}
\tableofcontents
\listoffigures
\end{document}
```

### Step 5: Add to integration matrix

Add the language to the matrix in
`.github/workflows/integration-matrix.yml`.

### Languages that need font support

CJK languages (Chinese, Japanese, Korean) require appropriate fonts.
If the default fonts don't cover your script, add a font override in
the language section of `lib/language/omnilatex-i18n.sty`.

---

## Adding a Document Type

Document types are profiles that configure page layout, font size, spacing,
title page style, and section numbering depth.

### Step 1: Create the profile

`config/document-types/mytype.sty`:

```latex
\NeedsTeXFormat{LaTeX2e}
\ProvidesPackage{config/document-types/mytype}[
  2026-01-01 v1.0.0 OmniLaTeX mytype profile
]

\documenttype{MyType}
\documentfontsize{12pt}
\documentlayout{DIV=12,headinclude=true,footinclude=true}
\KOMAoptions{titlepage=false,twoside=false}
\setcounter{secnumdepth}{3}
\setcounter{tocdepth}{2}

\documentcolormode{color}
\documentlinespacing{onehalf}
\documentparspacing{none}
\documentitemspacing{normal}
\documentfontmode{serif}
\documentlinkstyle{color}
\documentcodestyle{color}

% ── Title Page (optional) ─────────────────────────────
% Remove this section if no custom title page is needed.
% The default KOMA-Script title page will be used instead.
\makeatletter
\newcommand*{\omnilatex@mytypefront}{%
  \begin{titlepage}
    % ... custom title page layout ...
  \end{titlepage}
}
\makeatother
```

### Step 2: Register the doctype alias

Edit `omnilatex.cls`, find the doctype resolution section, and add
your alias:

```latex
% In the \ifdefstring block for the appropriate base class:
\ifdefstring{\omnilatex@doctype}{mytype}{%
  \def\@baseclass{scrartcl}%       % Choose base class
  \def\omnilatex@doctypeprofile{mytype}%
  \omnilatex@doctypematchedtrue
}{}
```

### Step 3: Update specs

Edit `specs/option_schema.toml` to add the new alias.

### Step 4: Create an example

```bash
cp -r examples/minimal-starter examples/mytype
# Edit examples/mytype/main.tex: change doctype=mytype
```

### Step 5: Add a test

Create `testfiles/omnilatex-mytype.lvt` and generate a baseline:
```bash
python scripts/gen_tlg.py omnilatex-mytype
```

### Step 6: Update CHANGELOG.md

Add an entry under `[Unreleased] > Added`.

---

## Code Style

### LaTeX

- **Naming**: Use `omnilatex@` prefix for internal commands (LaTeX2e) or
  `\__omnilatex_module_name:` prefix for LaTeX3/expl3 code
- **Comments**: Use `%` comments to describe sections and non-obvious logic
- **Spacing**: 4-space indentation in LaTeX code
- **No hardcoded values**: Use `\newlength` and configurable dimensions
- **No bare `\def`**: Use `\NewDocumentCommand` (LaTeX3) or `\newcommand`
  for user-facing commands; reserve `\def` for internal macros
- **Expl3 code**: All module internals should use expl3 conventions
  (`\cs_new:Npn`, `\tl_use:N`, etc.)

### Python (`build.py`)

- Follow PEP 8
- Type hints on all function signatures
- Docstrings on all public methods

### TOML (`specs/`)

- Use snake_case for keys
- Include `description` and `source` fields where applicable

---

## Submitting Changes

### Before submitting

1. **Run the full test suite:**
   ```bash
   python build.py test
   ```

2. **Run l3build checks** (if you modified `.sty` or `.cls` files):
   ```bash
   python build.py test --verbose
   ```

3. **Build at least one example** to verify compilation:
   ```bash
   python build.py build-example minimal-starter
   ```

4. **Check for warnings** in the build log:
   ```bash
   python build.py build-example minimal-starter --timings 2>&1 | grep -i warning
   ```

5. **Update CHANGELOG.md** (required for any `.sty`/`.cls` changes)

### Pull Request Checklist

- [ ] Tests pass (`python build.py test`)
- [ ] No new LaTeX warnings in build log
- [ ] CHANGELOG.md updated (if applicable)
- [ ] New files documented in relevant specs
- [ ] Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/)
  format: `feat:`, `fix:`, `docs:`, `ci:`, `chore:`, `test:`

### Commit message format

```
feat(module): add French language support
fix(floats): resolve caption overflow in two-column layout
docs: update README with new examples
ci: add macOS runner to build pipeline
test: add l3build test for glossary module
chore: update flake.lock
```

---

## Changelog Format

This project uses [Keep a Changelog](https://keepachangelog.com/) format.
Update `CHANGELOG.md` for any user-visible change.

```markdown
## [Unreleased]

### Added
- New feature description

### Fixed
- Bug fix description

### Changed
- Breaking or notable change description

### Removed
- Removed feature description
```

CI enforces that `CHANGELOG.md` is updated when `.sty` or `.cls` files
are modified.

---

## Getting Help

- Open a [Discussion](https://github.com/WyattAu/OmniLaTeX-template/discussions)
  for questions
- Open an [Issue](https://github.com/WyattAu/OmniLaTeX-template/issues) for bugs
  or feature requests
- Check existing issues and PRs before starting work — someone may already
  be working on it
