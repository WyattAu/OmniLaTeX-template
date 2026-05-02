# Using OmniLaTeX on Overleaf

OmniLaTeX works on Overleaf with LuaLaTeX. This page covers setup, font
fallbacks, zip creation, and known limitations.

## Quick Start

1. **Create the zip locally** (see [Create the Zip](#create-the-zip-locally))
2. **Upload to Overleaf**: Menu → New Project → Upload Project
3. **Set compiler**: Menu → Compiler → **LuaLaTeX**
4. **Recompile**

That is all you need. Everything else is handled by OmniLaTeX.

## Create the Zip Locally

The `make-overleaf-zip.sh` script creates a self-contained zip with a flat
directory structure compatible with Overleaf.

```bash
# Default: thesis example
bash scripts/make-overleaf-zip.sh

# Specific example
bash scripts/make-overleaf-zip.sh article
bash scripts/make-overleaf-zip.sh cv
bash scripts/make-overleaf-zip.sh technical-report
```

This produces `omnilatex-overleaf.zip` at the repository root.

### What Gets Included

| Path | Description |
|---|---|
| `main.tex` | Example document (paths adjusted for flat structure) |
| `omnilatex.cls` | Document class |
| `lib/` | Full module library |
| `config/` | Document-type configs and example settings |
| `bib/` | Bibliography database and glossary files |
| `README.md` | Overleaf-specific instructions |

### What Gets Excluded

Build tooling (`build.py`, `Makefile`), CI configs, Docker files, Nix flakes,
Pages assets, spec files, extensions, and `.github/` are not included.

## Upload to Overleaf

1. Go to [overleaf.com](https://www.overleaf.com) and log in
2. Click **New Project** → **Upload Project**
3. Select `omnilatex-overleaf.zip`
4. Set the compiler: click **Menu** (top-left) → **Compiler** → **LuaLaTeX**
5. Click **Recompile**

## Font Fallback

Overleaf runs TeX Live with a curated set of fonts. OmniLaTeX uses font
fallback chains so documents compile even when preferred fonts are missing.

### Primary Fonts (included in Overleaf TeX Live)

- **Latin text**: Libertinus Serif / Libertinus Sans
- **Math**: Libertinus Math
- **Mono**: Fira Mono

### Fallback Behavior

When a primary font is not available, OmniLaTeX falls back through a chain
of common alternatives:

| Use | Primary | Fallbacks |
|---|---|---|
| Serif | Libertinus Serif | Latin Modern Roman → Computer Modern |
| Sans | Libertinus Sans | Latin Modern Sans → Computer Modern Sans |
| Mono | Fira Mono | Latin Modern Mono → Computer Modern Mono |
| Math | Libertinus Math | Latin Modern Math |

### Custom Fonts

To use a font not bundled with Overleaf, upload the `.ttf` or `.otf` files to
your project root and add a `\setmainfont` call in your preamble:

```latex
\documentclass[doctype=thesis]{omnilatex}
\setmainfont{MyCustomFont}[
  Path = ./fonts/,
  Extension = .otf,
  UprightFont = *-Regular,
  BoldFont = *-Bold,
]
```

## Known Limitations

### Shell Escape / Minted

Overleaf supports `minted` but requires shell escape. If you get
"You must invoke LaTeX with the -shell-escape flag":

- Go to **Menu** → **Compiler**
- Add `-shell-escape` to the compiler flags, or
- Use `\usepackage{listings}` as a fallback (no shell escape needed)

### Glossary Compilation (bib2gls)

Glossaries and acronyms require `bib2gls`, which is available on Overleaf.
Set a custom build sequence:

- **Menu** → **Compiler** → **Other**
- Enter: `lualatex main.tex && biber main && bib2gls main && lualatex main.tex`

### No Local Build Tools

`build.py`, Docker, and Nix are not available on Overleaf. The zip includes
only the TeX source. Compilation is handled entirely by Overleaf's TeX Live.

### File Size Limits

Overleaf free plans have storage limits. If your project exceeds the limit:

- Remove unused files from `lib/` (only if you know which modules you do not need)
- Compress images before uploading
- Consider an Overleaf paid plan

### Incremental Builds

Overleaf recompiles from scratch each time. For large documents with many
chapters, compilation can be slow. Disable unused modules to speed things up:

```latex
\documentclass[
  doctype=thesis,
  enablecode=false,
  enableengineering=false,
]{omnilatex}
```

### Version Sync

The Overleaf zip is a snapshot. To update to a newer OmniLaTeX version,
re-run `make-overleaf-zip.sh` and re-upload. Overleaf does not support git
integration for custom templates on free plans.
