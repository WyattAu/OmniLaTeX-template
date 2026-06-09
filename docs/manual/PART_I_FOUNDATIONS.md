# Part I: Foundations — Detailed Chapter Plans

---

## Chapter 10: Installation

**Purpose:** Get OmniLaTeX running on any platform in under 10 minutes.

**Sections:**

### 10.1 Prerequisites

OmniLaTeX requires LuaTeX as its typesetting engine. All installation methods below satisfy this requirement, but the prerequisites differ:

| Method | OS | Disk Space | Network |
|---|---|---|---|
| Docker | Linux, macOS, Windows | ~8 GB (image) | Pull image once |
| Nix | Linux, macOS | ~2 GB (closure) | First build only |
| TeX Live | Linux, macOS, Windows | ~1 GB (minimal) to ~5 GB (full) | Download packages |
| VS Code DevContainer | Any (with Docker) | ~8 GB (image) | Pull image once |

Required tools regardless of method:

- **Python 3.10+** -- `build.py` is the build orchestrator
- **Git** -- required for git metadata embedding (`\GitRefName`, `\BuildDate`)
- **Pygments** (python package) -- required by the `minted` code highlighting package

### 10.2 Docker Method (Recommended)

Docker provides a self-contained, reproducible build environment. The image bundles TeX Live, Inkscape, Gnuplot, all required fonts, and Python dependencies.

**Pull the image:**

```bash
docker pull ghcr.io/wyattau/omnilatex-docker
```

The image supports multi-architecture builds (linux/amd64, linux/arm64). Docker automatically selects the correct architecture for your host.

**Build a single example:**

```bash
docker run --rm --entrypoint "" \
  -v "$PWD:/workspace" -w /workspace \
  ghcr.io/wyattau/omnilatex-docker \
  python3 build.py build-example article
```

**Build all examples:**

```bash
docker run --rm --entrypoint "" \
  -v "$PWD:/workspace" -w /workspace \
  ghcr.io/wyattau/omnilatex-docker \
  python3 build.py build-all
```

**Volume mount patterns:**

| Pattern | Use Case |
|---|---|
| `-v "$PWD:/workspace"` | Mount the entire repository |
| `-v "$PWD/examples:/workspace/examples"` | Mount only examples |
| `-v "$PWD/build:/build"` | Separate output directory |
| `--user $(id -u):$(id -g)` | Match host UID/GID for file ownership |

**Important notes:**

- The `--entrypoint ""` flag is required to bypass the default latexmk entrypoint
- The default user inside the container is `tex` (UID/GID 1000:1000). Use `--user` to avoid root-owned output files
- The image sets `LANG=C.utf8` and `LC_ALL=C.utf8` for consistent encoding
- Font cache (`luaotfload-tool --update`) is pre-warmed during image build

**ENTRYPOINT bypass:**

The default `ENTRYPOINT` in the Docker image is `/usr/local/bin/entrypoint.sh`, which invokes `latexmk`. To run arbitrary commands (like `build.py` or `bash`), you must override it:

```bash
# Override with --entrypoint (preferred)
docker run --rm --entrypoint "" -v "$PWD:/workspace" -w /workspace \
  ghcr.io/wyattau/omnilatex-docker python3 build.py preflight

# Or use --entrypoint with a command
docker run --rm --entrypoint /bin/bash -v "$PWD:/workspace" -it \
  ghcr.io/wyattau/omnilatex-docker
```

### 10.3 Nix Method

The Nix flake provides a fully reproducible development shell and build targets. It uses `scheme-medium` plus explicitly declared packages (~2 GB) instead of `scheme-full` (~5 GB).

**Enter the development shell:**

```bash
nix develop .
# or equivalently:
nix develop .#devShells.x86_64-linux.default
```

The dev shell provides: TeX Live, Python (with Pygments, pytest, rich), Inkscape, Gnuplot, Lean 4, and GNU Make.

**Build the manual PDF:**

```bash
nix build .#default
# Output: result/omnilatex-manual.pdf
```

**Build the OmniLaTeX package (for local installation):**

```bash
nix build .#omnilatex
# Output: result/tex/latex/omnilatex/
```

**Build individual example PDFs:**

```bash
nix build .#examples-article     # Article example
nix build .#examples-thesis      # Thesis example
nix build .#examples-presentation # Presentation example
nix build .#examples-cv          # CV example
# Full list: article, thesis, presentation, cv, book, report, letter, poster,
#   dissertation, journal, manual, guide, minimal-starter, minimal-custom,
#   technical-report, multi-language, standard, dictionary, cover-letter,
#   cover-letter-formal, cv-twopage, inline-paper, article-color,
#   accessibility-test, citation-styles, color-themes, cjk-chinese,
#   cjk-japanese, cjk-korean, rtl-arabic, rtl-hebrew
```

**Run reproducibility check:**

```bash
nix build .#checks.reproducibility
# Builds thesis example twice and compares SHA-256 hashes
```

**Font note:** Monaspace Neon and Atkinson Hyperlegible Next are not available in nixpkgs. The Nix flake bundles Libertinus (via `collection-fontsextra`) and Font Awesome 5. For the full font stack, use the Docker image or install the missing fonts system-wide.

### 10.4 TeX Live Method

**Full installation (recommended):**

```bash
# Install TeX Live 2026 (adjust installer URL for your platform)
wget https://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz
tar -xf install-tl-unx.tar.gz
cd install-tl-*/
sudo ./install-tl --scheme=full

# Verify
tex --version
latexmk --version
```

**Minimal installation (for CI or constrained environments):**

The minimum required TeX Live packages can be installed selectively. Refer to `flake.nix` for the complete package list. Key packages include:

```
fontspec, unicode-math, amsmath, mathtools, lualatex-math,
libertinus, fontawesome5, siunitx, chemmacros, minted,
biblatex-ext, biber, bib2gls, glossaries-extra,
polyglossia, hyperref, tcolorbox, booktabs, tabularray,
pgfplots, circuitikz, forest, luatexja, tagpdf
```

**CTAN installation (after CTAN publishes):**

```bash
tlmgr install omnilatex
```

**Post-install verification:**

```bash
python3 build.py preflight
```

This checks for: LuaTeX engine, latexmk, Python version, TeX Live version, and critical LaTeX packages (fontspec, unicode-math, hyperref, minted, biblatex, siunitx, circuitikz, forest).

**Platform-specific notes:**

- **Linux:** TeX Live packages are available via most distribution package managers (`texlive-full` on Debian/Ubuntu, `texlive` on Fedora). The distribution packages may lag behind the upstream version.
- **macOS:** MacTeX provides a complete TeX Live installation. Install via Homebrew with `brew install --cask mactex-no-gui` for a lighter install.
- **Windows:** MiKTeX provides on-the-fly package installation. Alternatively, install TeX Live via the Windows installer from tug.org.

### 10.5 VS Code Dev Container

The Dev Container provides a one-click setup for VS Code with all tools pre-configured.

**Setup:**

1. Install Docker and the VS Code "Dev Containers" extension
2. Clone the repository
3. Open the repository in VS Code
4. Run "Dev Containers: Reopen in Container" from the command palette

The Dev Container:

- Uses Docker Compose with the OmniLaTeX Docker image
- Runs `python3 build.py preflight` as a post-creation command
- Sets the working directory to `/workspace`

**Pre-installed VS Code extensions:**

| Extension | Purpose |
|---|---|
| `ms-python.python` | Python language support |
| `james-yu.latex-workshop` | LaTeX compilation and preview |
| `streetsidesoftware.code-spell-checker` | Spell checking |
| `yzhang.markdown-all-in-one` | Markdown editing |
| `znck.grammarly` | Grammar checking |

**LaTeX Workshop recipes:**

The Dev Container configures two LaTeX Workshop recipes:

- **latexmk (dev mode):** Uses `BUILD_MODE=dev` for fast iteration (3 passes, full bib)
- **latexmk (prod mode):** Uses `BUILD_MODE=prod` for production builds (full validation, biber `--validate-datamodel`)

Auto-build is disabled by default (`latex-workshop.latex.autoBuild.run: never`). Trigger builds manually or via `build.py`.

**Standalone `devcontainer.json`:**

Copy `devcontainer.json.example` to `.devcontainer/devcontainer.json` and customize as needed. The example file is identical to the default configuration and serves as a reference.

### 10.6 Verification

After installation, verify the environment:

```bash
# Run preflight checks (tools + packages)
python3 build.py preflight

# Run comprehensive diagnostics
python3 build.py doctor

# Build the minimal starter example
python3 build.py build-example minimal-starter

# Build all examples and verify (full test)
python3 build.py build-all
```

**Expected output from `preflight`:**

```
[INFO]   * LuaTeX engine: Found at /usr/bin/lualatex
[INFO]   * latexmk build tool: Found at /usr/bin/latexmk
[INFO]   * Python >= 3.10: Found Python 3.12.x
[INFO]   * Git CLI: Found at /usr/bin/git
[INFO]   * TeX Live >= 2024: Found TeX Live 2026
[INFO]   * Package fontspec: Found
[INFO]   * Package unicode-math: Found
[INFO]   * Package hyperref: Found
[INFO]   * Package minted: Found
[INFO]   * Package biblatex: Found
[INFO]   * Package siunitx: Found
[INFO]   * Package circuitikz: Found
[INFO]   * Package forest: Found
```

### 10.7 Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `Font 'Monaspace Neon' not found` | Font not installed system-wide | Download from github.com/githubnext/monaspace and install, or use Docker image |
| `Font 'Atkinson Hyperlegible Next' not found` | Font not installed system-wide | Download from github.com/googlefonts/atkinson-hyperlegible-next and install |
| `luaotfload | db: Font names database not found` | Font cache not initialized | Run `luaotfload-tool --update` |
| `minted: ... Pygmentize command not found` | Python Pygments not installed | `pip install Pygments` |
| `kpsewhich: cannot find omnilatex.cls` | OmniLaTeX not in TEXINPUTS | Set `TEXINPUTS` to include the repository root |
| `Permission denied` on output PDFs | Docker runs as root by default | Use `--user $(id -u):$(id -g)` |
| `lualatex: ... FATAL error` | LuaTeX version too old | Upgrade to TeX Live 2024+ |
| `Inkscape conversion failed` | SVG support requires `--shell-escape` | Ensure `--shell-escape` is in latexmk flags (included by default) |
| `biber: ... datamodel validation error` | Bib entry has a schema violation | Fix the `.bib` entry, or use `BUILD_MODE=dev` to skip validation |
| `bib2gls` not found | Glossary processor missing | `tlmgr install bib2gls` |

**Key cross-refs:** Chapter 12 (build system), Chapter 102 (Docker workflow), Chapter 103 (Nix workflow)

---

## Chapter 11: Quick Start

**Purpose:** 5-minute first document. Copy-paste ready.

**Sections:**

### 11.1 Minimal Document

The smallest possible OmniLaTeX document:

```latex
\documentclass{omnilatex}
\begin{document}
Hello, OmniLaTeX!
\end{document}
```

### 11.2 Adding Options

```latex
\documentclass[
    doctype=article,
    language=german,
    institution=tuhh
]{omnilatex}
```

### 11.3 Your First Real Document

Complete article with title, sections, a figure, bibliography. See `examples/minimal-starter/` for a working template.

### 11.4 Building

```bash
python3 build.py build-example article
```

### 11.5 Next Steps

Links to relevant chapters.

**Demonstrates:** `omnilatex.cls` loading, class options, `\section`, `\begin{figure}`, `\cite`

---

## Chapter 12: Build System

**Purpose:** Complete reference for `build.py` and `latexmk`.

### 12.1 build.py Overview

`build.py` is a 679-line Python build orchestrator that manages all OmniLaTeX compilation. It wraps `latexmk` and provides:

- Explicit dev/prod/ultra build modes
- Concurrent example building with a Rich UI
- Incremental builds via source-hash caching (`build_cache.json`)
- Per-example timing metrics
- Interactive terminal menu (TUI)
- Project scaffolding and health diagnostics

### 12.2 Build Commands

Complete command reference:

| Command | Args | Description |
|---|---|---|
| `build.py build-all` | -- | Build root document + all examples |
| `build.py build` | -- | Alias for `build-all` |
| `build.py build-root` | -- | Build root `main.tex` |
| `build.py build-examples` | -- | Build all examples concurrently |
| `build.py build-example` | `<name> [name...]` | Build specific example(s) |
| `build.py clean` | -- | Full cleanup (aux files + build dir) |
| `build.py clean-aux` | -- | Clean auxiliary files only |
| `build.py clean-pdf` | -- | Remove all generated PDFs |
| `build.py clean-example` | `<name> [name...]` | Clean specific example(s) |
| `build.py clean-examples` | -- | Alias for `clean-aux` |
| `build.py list-examples` | -- | List all discovered examples |
| `build.py preflight` | -- | Validate build environment |
| `build.py lint` | -- | Alias for `preflight` |
| `build.py test` | -- | Run test suite (l3build + pytest) |
| `build.py watch` | `[name...]` | Watch files and rebuild on change |
| `build.py doctor` | -- | Comprehensive health diagnostics |
| `build.py diff` | `<name> [--regenerate-references]` | Visual regression comparison |
| `build.py init` | `<name> [--doctype T] [--lang L]` | New project from template |
| `build.py scaffold-institution` | `<name>` | Create institution config |
| `build.py scaffold-language` | `<lang>` | Create language addition guide |

### 12.3 Global Flags

| Flag | Type | Default | Description |
|---|---|---|---|
| `--mode` | `dev`, `prod`, `ultra` | `dev` | Build mode (see Chapter 100) |
| `--force` | flag | off | Ignore incremental build cache |
| `--timings` | flag | off | Write per-example metrics to `build/metrics.json` |
| `--verbose` | flag | off | Show full subprocess output |
| `--source-date-epoch` | int | none | Set `SOURCE_DATE_EPOCH` for reproducible builds |
| `-j`, `--jobs` | int | `min(4, cpu_count)` | Number of parallel build workers |

The `OMNILATEX_VERBOSE=1` environment variable also enables verbose output.

### 12.4 Build Modes

Build modes control latexmk behavior. Set via `--mode` or the `BUILD_MODE` environment variable.

| Mode | latexmk passes | biber | bib2gls | Use Case |
|---|---|---|---|---|
| `dev` | 6 | normal | normal | Fast iteration (default) |
| `prod` | 7 | `--validate-datamodel` | normal | Final output, CI |
| `ultra` | 1 | disabled | disabled | Fastest possible, no bibliography |

Mode detection macros in LaTeX:

```latex
\ifOmniDev  % true in dev mode
\ifOmniProd % true in prod mode
\ifOmniUltra % true in ultra mode
```

### 12.5 Incremental Builds

`build.py` implements source-hash caching to skip unchanged examples:

1. For each example, compute SHA-256 hash of: `main.tex`, all `.bib` files, all `.sty` files, all `.cls` files
2. Compare against cached hash in `build/build_cache.json`
3. If hash matches and output PDF exists, skip the build (cache hit)
4. On successful build, update the cache entry with new hash, PDF size, and build time

Use `--force` to bypass the cache and rebuild everything.

### 12.6 Latexmk Configuration

The `.latexmkrc` file configures latexmk. Key settings:

**Engine:** `$pdf_mode = 4` (LuaTeX). Also supports `$pdf_mode = 5` (XeTeX).

**Shell escape:** Always enabled via `set_tex_cmds("--shell-escape --synctex=0 --file-line-error %O %S")`. Required for:

- SVG conversion via Inkscape
- `minted` code highlighting via Pygments
- Git metadata via Lua scripts

**Biber integration:**

| Mode | `$bibtex_use` | `$biber` command |
|---|---|---|
| `dev` | 2 | `biber %O %S` |
| `prod` | 2 | `biber --validate-datamodel %O %S` |
| `ultra` | 0 | `true` (no-op) |

**bib2gls dependency:** Custom `add_cus_dep('aux', 'glstex', 0, 'run_bib2gls')` rule runs `bib2gls` when `.glstex` is stale. Disabled in `ultra` mode and when `OMNILATEX_SKIP_BIB2GLS=1`.

**Auxiliary file tracking:** Custom extensions registered via `push @generated_exts`: `loe`, `lol`, `lor`, `run.xml`, `glg`, `glstex`. Cleanup pattern: `$clean_ext = "%R-*.glstex %R_contourtmp*.* _minted-%R"`.

**Minted cache:** Excluded from dependency tracking via `$hash_calc_ignore_pattern{'_minted'} = '.*'` to prevent unnecessary re-runs.

**Synctex:** Disabled by default (`--synctex=0`) for CI. VS Code Dev Container uses `--synctex=1` for source-PDF synchronization.

### 12.7 Docker Build Mode

When building inside Docker, the entrypoint wraps latexmk. To use `build.py` inside Docker:

```bash
# Production build
docker run --rm --entrypoint "" \
  -e BUILD_MODE=prod \
  -v "$PWD:/workspace" -w /workspace \
  ghcr.io/wyattau/omnilatex-docker \
  python3 build.py build-all

# Development build (fast)
docker run --rm --entrypoint "" \
  -e BUILD_MODE=dev \
  -v "$PWD:/workspace" -w /workspace \
  ghcr.io/wyattau/omnilatex-docker \
  python3 build.py build-example thesis
```

### 12.8 Nix Build Integration

The Nix flake provides declarative build targets:

- `nix build .#default` -- Build the manual
- `nix build .#omnilatex` -- Build the package (installable `.sty`/`.cls` files)
- `nix build .#examples-<name>` -- Build individual examples
- `nix build .#checks.reproducibility` -- Verify deterministic builds
- `nix build .#checks.formatting` -- Validate Python syntax

All Nix builds set `SOURCE_DATE_EPOCH=1700000000` and `TEXINPUTS=$PWD/:` for reproducibility.

### 12.9 Concurrent Build Configuration

Example builds run concurrently using `ThreadPoolExecutor`:

- Default workers: `min(4, os.cpu_count())` locally, `4` in CI
- Override with `-j N` or `--jobs N`
- Rich UI shows active workers, elapsed time, and live log output
- Falls back to tqdm progress bar if `rich` is not installed
- Thread-safe cache access via `_cache_lock`

### 12.10 Watch Mode

```bash
# Watch all examples and rebuild on change
python3 build.py watch

# Watch specific examples
python3 build.py watch thesis article
```

Uses the `watchdog` library if available, falls back to `inotifywait`. Watches for changes to `.tex`, `.sty`, `.cls`, `.bib`, `.lua`, and `.toml` files.

### 12.11 Build Error Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `PDF not generated` | Compilation failed | Check `main.log` for the first error; run `build.py build-example <name> --verbose` |
| `Undefined control sequence` | Missing package or typo | Verify all `\usepackage` calls; check spelling of commands |
| `Missing character` | Font does not contain glyph | Install the required font or use a fallback |
| `Overfull \hbox` | Line too long | Adjust text, use `microtype` protrusion (enabled by default), or rewrite |
| `multiply-defined references` | Duplicate label | Search for duplicate `\label{}` commands |
| `biber: ERROR - Datamodel validation` | Invalid `.bib` entry | Fix the entry; run `biber --validate-datamodel main` to see details |
| `bib2gls` fails | Missing `.bib` for glossary | Create glossary `.bib` file or set `OMNILATEX_SKIP_BIB2GLS=1` |
| `minted: ... \minted@...` | Pygments not found | Install Pygments: `pip install Pygments` |
| `kpsewhich cannot find` | File not in TEXMF tree | Set `TEXINPUTS=.:<repo_root>:` |
| `Cache hit but PDF missing` | Stale cache | Run `python3 build.py clean` then rebuild |

**Key cross-refs:** Chapter 100 (build modes), Chapter 102 (Docker workflow), Chapter 104 (CI/CD)

---

## Chapter 13: Class Options

**Purpose:** Complete reference for all 15 class options.

### 13.1 Option Loading

Options are passed via `\documentclass[options]{omnilatex}` and processed in this order:

1. `kvoptions` parses all declared options (see reference table below)
2. Undeclared options are collected via `\DeclareDefaultOption` and forwarded to the KOMA base class as user options
3. The `doctype` string is lowercased and matched against the alias table
4. The matched doctype loads its profile `.sty` file, which may pass additional KOMA options

**Example:**

```latex
\documentclass[
    language=german,       % declared option
    doctype=thesis,        % declared option
    twoside,               % undeclared -> forwarded to KOMA
    fontsize=12pt,         % undeclared -> forwarded to KOMA
    a5,                    % void option
]{omnilatex}
```

### 13.2 Complete Option Reference

| Option | Type | Default | Effect | Chapter |
|---|---|---|---|---|
| `language` | string | `english` | Sets document language via polyglossia | Ch 40 |
| `doctype` | string | `thesis` | Selects document type profile (55+ aliases) | Ch 14 |
| `titlestyle` | string | `book` | Title page layout (book, thesis, simple, tuhh) | Ch 52 |
| `institution` | string | `none` | Institution branding config | Ch 53 |
| `censoring` | bool | false | Enable `\censor{}` and related commands | Ch 92 |
| `loadGlossaries` | bool | false | Enable glossaries-extra module | Ch 72 |
| `todonotes` | bool | false | Enable `\todo{}` notes | Ch 92 |
| `enablefonts` | bool | false | Enable extended font features | Ch 30 |
| `enablegraphics` | bool | false | Enable graphics module (TikZ, pgfplots) | Ch 61 |
| `enablemath` | bool | true | Enable math module (amsmath, siunitx, chemmacros) | Ch 32 |
| `enabletikz` | bool | true | Enable TikZ core and pgfplots | Ch 60 |
| `enableengineering` | bool | true | Enable engineering TikZ shapes (circuits, thermodynamics) | Ch 64 |
| `enablecode` | bool | true | Enable minted code listings | Ch 80 |
| `enabletables` | bool | true | Enable tables module (booktabs, tabularray) | Ch 62 |
| `a5` | void | -- | Switch to A5 paper, 10pt font | Ch 50 |

### 13.3 Void Options

The `a5` option is a void option (no value needed). When declared, it:

1. Passes `paper=a5` to the `typearea` package via `\PassOptionsToPackage`
2. Adds `fontsize=10pt` to the KOMA class options

Usage:

```latex
\documentclass[a5]{omnilatex}        % A5, 10pt
\documentclass[a5, doctype=article]{omnilatex}  % A5 article
```

Other common void options that can be passed as undeclared (forwarded to KOMA):

| Option | Effect |
|---|---|
| `twoside` | Two-sided layout with alternating margins |
| `draft` | Draft mode (overfull hbox markers) |
| `final` | Final mode (default) |
| `landscape` | Landscape orientation |
| `open=right` | Chapters open on right-hand pages |
| `open=any` | Chapters open on any page |
| `numbers=noenddot` | No dot after chapter/section numbers |
| `chapterprefix` | Add "Chapter N" prefix |
| `parskip=half` | Half-line paragraph spacing |
| `parskip=full` | Full-line paragraph spacing |
| `titlepage=true` | Separate title page |
| `titlepage=false` | Inline title |
| `bibliography=totoc` | Include bibliography in TOC |
| `listof=totoc` | Include lists (figures, tables) in TOC |

### 13.4 Option Interactions

**Complementary options:**

| Option A | Option B | Interaction |
|---|---|---|
| `doctype=thesis` | `institution=tuhh` | Loads TUHH-specific title page and branding |
| `doctype=thesis` | `titlestyle=TUHH` | Same as above (alternative syntax) |
| `loadGlossaries` | any doctype | Enables `\sym{}`, `\abb{}`, `\sub{}` shortcuts |
| `enablemath` | `doctype=article` | Math module enabled by default |
| `a5` | `doctype=letter` | Compact letter format |

**Conflicting options to avoid:**

| Option A | Option B | Issue |
|---|---|---|
| `doctype=article` + `twoside` | `doctype=inlinepaper` | inlinepaper overrides `twoside` with `titlepage=false` |
| `BUILD_MODE=ultra` | `loadGlossaries=true` | ultra disables bib2gls; glossary entries will be empty |
| `enablemath=false` | any doctype using equations | Math commands will be undefined |
| `enabletikz=false` + `enableengineering=true` | -- | Engineering depends on TikZ core; disable both together |
| `doctype=manual` | `documentfontmode=serif` | Manual profile forces sans-serif font mode |

### 13.5 Boolean Options and Feature Flags

Boolean options (`censoring`, `todonotes`, `loadGlossaries`, `enablefonts`, `enablegraphics`, `enablemath`, `enabletikz`, `enableengineering`, `enablecode`, `enabletables`) control conditional module loading in `omnilatex.cls`:

```latex
% Enable glossaries module (disabled by default)
\documentclass[loadGlossaries]{omnilatex}

% Disable math module (enabled by default)
\documentclass[enablemath=false]{omnilatex}

% Disable multiple modules for minimal builds
\documentclass[enablemath=false,enabletikz=false,enableengineering=false]{omnilatex}
```

The six "enable" options (`enablemath` through `enabletables`) are set to `true` by default for backward compatibility. Disabling them reduces compilation time by skipping the corresponding module:

| Module disabled | Packages skipped |
|---|---|
| `enablemath=false` | mathtools, chemmacros, siunitx, xfrac, eurosym, empheq |
| `enabletikz=false` | omnilatex-graphics, omnilatex-tikz-core (includes pgfplots) |
| `enableengineering=false` | omnilatex-tikz-engineering (circuitikz, 3dplot, forest) |
| `enablecode=false` | omnilatex-listings (minted, accsupp, fvextra) |
| `enabletables=false` | omnilatex-tables (multirow, booktabs, tabularray) |

### 13.6 Custom Options

Project-specific options can be added via `config/document-settings.sty`:

```latex
% config/document-settings.sty
\newcommand{\projectlogo}{\includegraphics[height=1.5cm]{logo.pdf}}
\newcommand{\projectnumber}{PRJ-2026-001}
```

This file is loaded automatically when it exists in the example directory.

**Key cross-refs:** All Part II-V chapters (each option links to its detailed chapter)

---

## Chapter 14: Doctype System

**Purpose:** How the 55+ doctype aliases map to 3 KOMA classes.

**Sections:**

1. **Architecture** — Three-tier system: user alias -> canonical name -> KOMA class
2. **Canonical Doctypes** — Table of 26 canonical names with KOMA base:
   | Canonical | KOMA Class | Category | Chapter |
   |---|---|---|---|
   | `article` | scrartcl | Short documents | Ch 20 |
   | `thesis` | scrbook | Long documents | Ch 22 |
   | `technicalreport` | scrreprt | Reports | Ch 21 |
   | ... | ... | ... | ... |
3. **Alias Table** — Complete mapping of all 55+ aliases to canonical names
4. **KOMA Class Options** — What each base class configures (fontsize, BCOR, DIV, etc.)
5. **Doctype Profiles** — Each `.sty` file in `config/document-types/` explained:
   - What it sets (KOMA options, custom commands)
   - Which class options it passes
   - Example usage
6. **Creating Custom Doctypes** — How to add a new document type profile
7. **Lean Verification** — Reference to `DoctypeClassMapping.lean` and `DocumentSettings.lean` theorems

**Key cross-refs:** Chapter 13 (class options), Chapters 20-25 (per-category doctypes), Chapter 111 (architecture)
