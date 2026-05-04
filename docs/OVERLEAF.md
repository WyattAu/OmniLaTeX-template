# Using OmniLaTeX on Overleaf

OmniLaTeX works on Overleaf with LuaLaTeX. This guide covers setup for single
and batch projects, manual uploads, font fallbacks, and known limitations.

## Quick Start

1. **Create the zip locally** (see below)
2. **Upload to Overleaf**: Menu -> New Project -> Upload Project
3. **Set compiler**: Menu -> Compiler -> **LuaLaTeX**
4. **Recompile**

That is all you need.

## Creating Overleaf Zips

### Single Example

Use `make-overleaf-zip.sh` to create a zip from any example:

```bash
# Default: thesis example
bash scripts/make-overleaf-zip.sh

# Specific example
bash scripts/make-overleaf-zip.sh article
bash scripts/make-overleaf-zip.sh cv
bash scripts/make-overleaf-zip.sh technical-report
bash scripts/make-overleaf-zip.sh poster
bash scripts/make-overleaf-zip.sh presentation
```

This produces `omnilatex-overleaf.zip` at the repository root.

### All Examples (Batch)

Use `make-overleaf-zip-all.sh` to generate a zip for every example at once:

```bash
bash scripts/make-overleaf-zip-all.sh
```

Output: `build/overleaf-zips/<example-name>.zip` for each example. The script
reports success/failure counts and file sizes.

## What Gets Included

| Path | Description |
|------|-------------|
| `main.tex` | Example document (paths adjusted for flat structure) |
| `omnilatex.cls` | Document class |
| `lib/` | Full module library (27 modules) |
| `config/` | Document-type configs and example settings |
| `bib/` | Bibliography database and glossary files |
| `README.md` | Overleaf-specific instructions |

## What Gets Excluded

Build tooling (`build.py`, `Makefile`), CI configs, Docker files, Nix flakes,
Pages assets, spec files, extensions, and `.github/` are not included.

## Manual Setup

If you prefer to upload files directly instead of using the zip script:

1. Go to [overleaf.com](https://www.overleaf.com) and create a new blank project
2. Upload these files/folders to the project root:
   - `omnilatex.cls`
   - The entire `lib/` directory
   - The entire `config/` directory
   - The entire `bib/` directory
3. Create or upload your `main.tex`
4. If your `main.tex` uses relative paths like `../../omnilatex`, change them to
   just `omnilatex` (since everything is now in the same directory on Overleaf)
5. Set the compiler to **LuaLaTeX**: Menu -> Compiler -> LuaLaTeX
6. Recompile

### Path Adjustments

The zip script automatically adjusts paths. If uploading manually, replace:

```latex
% Before (local repo structure)
\documentclass[../../omnilatex]{omnilatex}
\addbibresource{../../bib/references.bib}

% After (flat Overleaf structure)
\documentclass{omnilatex}
\addbibresource{bib/references.bib}
```

## Upload to Overleaf

1. Go to [overleaf.com](https://www.overleaf.com) and log in
2. Click **New Project** -> **Upload Project**
3. Select `omnilatex-overleaf.zip` (or any generated zip)
4. Set the compiler: click **Menu** (top-left) -> **Compiler** -> **LuaLaTeX**
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
|-----|---------|-----------|
| Serif | Libertinus Serif | Latin Modern Roman -> Computer Modern |
| Sans | Libertinus Sans | Latin Modern Sans -> Computer Modern Sans |
| Mono | Fira Mono | Latin Modern Mono -> Computer Modern Mono |
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

### TeX Live Version

Overleaf may not run the latest TeX Live. OmniLaTeX targets TeX Live 2025. If
a package is too new, you may see "File not found" errors. Most core packages
(KOMA-Script, fontspec, biblatex, hyperref) are available on older versions.

### Shell Escape / Minted

Overleaf supports `minted` but requires shell escape. If you get
"You must invoke LaTeX with the -shell-escape flag":

- Go to **Menu** -> **Compiler**
- Add `-shell-escape` to the compiler flags, or
- Use `\usepackage{listings}` as a fallback (no shell escape needed)

### Glossary Compilation (bib2gls)

Glossaries and acronyms require `bib2gls`, which is available on Overleaf.
Set a custom build sequence:

- **Menu** -> **Compiler** -> **Other**
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
re-run the zip script and re-upload. Overleaf does not support git
integration for custom templates on free plans.

## Tips for Overleaf

### Faster Recompilation

Overleaf caches intermediate files between compiles. If compilation is slow:

1. Remove unused modules (see "Incremental Builds" above)
2. Avoid `\includegraphics` with very large images
3. Use `\include` for chapters so only changed chapters are reprocessed

### Collaboration

Multiple collaborators can edit simultaneously on Overleaf. The zip script
produces a flat directory structure that works well with Overleaf's editor.

### Debugging

If compilation fails on Overleaf but works locally:

1. Check the compiler is set to **LuaLaTeX** (not pdfLaTeX)
2. Check the full error log: Menu -> Logs and Output Files
3. Compare TeX Live versions: Overleaf may have an older version
4. Check if a required package is missing on Overleaf's TeX Live

### Biblatex / Biber

Biber is available on Overleaf. If bibliography doesn't appear:

1. Ensure `\addbibresource{bib/references.bib}` path is correct
2. Set the build sequence to run biber: Menu -> Compiler -> Other
3. Enter: `lualatex main.tex && biber main && lualatex main.tex`
