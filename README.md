# OmniLaTeX

A modular, engineering-grade LaTeX document class for academic and professional documents. 55 doctype aliases, 21 modules, 24 example templates, byte-for-byte reproducible builds, and 239 test cases.

Built on LuaLaTeX + KOMA-Script. Compile with `latexmk -lualatex` or `build.py`.

## Why OmniLaTeX

| | OmniLaTeX | Typical template |
|---|---|---|
| **Document types** | 55 aliases (thesis, CV, patent, journal, ...) | 1–3 |
| **Test coverage** | 239 test cases + 21 l3build modules | 0 |
| **Reproducible builds** | Byte-for-byte deterministic | No |
| **Formal verification** | Lean 4 proofs | No |
| **CI platforms** | 5 (GitHub, GitLab, Gitea, Forgejo, Woodpecker) | 0–1 |
| **Font fallbacks** | Graceful degradation with warnings | Crash or silent substitution |
| **Institution configs** | Pluggable (`config/institutions/`) | Hardcoded |

## Quick Start

```bash
git clone https://github.com/WyattAu/OmniLaTeX-template.git
cd OmniLaTeX-template
python build.py build-example minimal-starter
```

PDF output: `build/examples/minimal-starter.pdf`

Or use Docker (no local TeX Live needed):

```bash
docker run -it --rm -v $(pwd):/workspace ghcr.io/wyattau/omnilatex-docker:latest
python build.py build-example minimal-starter
```

## Features

- **55 doctype aliases** resolving to 16 document profiles across 3 KOMA-Script base classes
- **21 modular `.sty` packages** with formal interface contracts
- **Lazy module loading** — only load what you need (`enablemath`, `enabletikz`, `enablecode`, ...)
- **Modern font stack** — Libertinus Serif + Math, Monaspace Neon, Atkinson Hyperlegible Next (with graceful fallback)
- **Reproducible builds** — `SOURCE_DATE_EPOCH` support, byte-for-byte deterministic PDFs
- **Multi-language** — 12 languages via polyglossia (EN, DE, FR, ES, PT, IT, NL, RU, ZH, JA, KO, AR); infrastructure for 80+ more
- **Institution branding** — pluggable configs in `config/institutions/` (TUHH, TUM, ETH Zürich included)
- **Code listings** — syntax highlighting via minted with cached compilation
- **Engineering diagrams** — 1,000+ lines of TikZ shapes: thermodynamics, P&ID, flowcharts
- **Build automation** — `build.py` with watch mode, concurrent builds, timing metrics, and health diagnostics

## Document Types

```latex
\documentclass[doctype=thesis]{omnilatex}           % Academic thesis
\documentclass[doctype=dissertation]{omnilatex}      % Dissertation
\documentclass[doctype=article]{omnilatex}           % Article
\documentclass[doctype=cv]{omnilatex}                % Curriculum vitae
\documentclass[doctype=patent]{omnilatex}            % Patent application
\documentclass[doctype=technicalreport]{omnilatex}   % Technical report
\documentclass[doctype=manual]{omnilatex}            % Manual / handbook
\documentclass[doctype=standard]{omnilatex}          % Standards document
\documentclass[doctype=book]{omnilatex}              % Book
\documentclass[doctype=journal]{omnilatex}           % Journal article
\documentclass[doctype=cover-letter]{omnilatex}      % Cover letter
\documentclass[doctype=dictionary]{omnilatex}        % Dictionary / lexicon
\documentclass[doctype=inlinepaper]{omnilatex}       % Inline research paper
\documentclass[doctype=poster]{omnilatex}            % Conference poster
\documentclass[doctype=presentation]{omnilatex}      % Presentation slides
\documentclass[doctype=letter]{omnilatex}            % Formal letter
```

All options: `language`, `doctype`, `titlestyle`, `institution`, `censoring`, `loadGlossaries`, `todonotes`, `enablefonts`, `enablegraphics`, `enablemath`, `enabletikz`, `enableengineering`, `enablecode`, `enabletables`.

## Examples

24 ready-to-use templates in `examples/`:

| Example | Doctype | Description |
|---------|---------|-------------|
| `minimal-starter` | thesis | Minimal starter demonstrating all major features |
| `minimal-custom` | thesis | Minimal template showing customization options |
| `thesis` | thesis | Generic thesis template |
| `thesis-tuhh` | thesis | TUHH-specific thesis with institutional branding |
| `thesis-spacing` | thesis | Thesis with custom line spacing |
| `dissertation` | dissertation | Dissertation document |
| `article` | article | Standard article format |
| `article-color` | article | Article with color configuration |
| `inline-paper` | inlinepaper | Inline research paper |
| `journal` | journal | Journal / magazine article |
| `book` | book | Book-length document |
| `cv` | cv | Curriculum vitae template |
| `cv-twopage` | cv | Two-page CV variant |
| `cover-letter` | cover-letter | Cover letter template |
| `cover-letter-formal` | cover-letter | Formal cover letter variant |
| `manual` | manual | Manual / handbook document |
| `technical-report` | technical-report | Technical report format |
| `standard` | standard | Standards document |
| `dictionary` | dictionary | Dictionary / lexicon |
| `multi-language` | article | Multilingual document (English/German) |
| `poster` | poster | Conference poster (A1 landscape) |
| `presentation` | presentation | Presentation slides (KOMA-based) |
| `letter` | letter | Formal letter |
| `accessibility-test` | article | Tagged PDF (PDF/UA-1) via tagpdf |

```bash
python build.py build-example <name>
python build.py build-examples   # build all
```

## Font System

| Font | Role | Required? |
|------|------|-----------|
| **Libertinus Serif** + **Math** | Main text + mathematics | Yes — bundled with TeX Live |
| **Monaspace Neon** | Monospace / code listings | Optional — falls back to Latin Modern Mono |
| **Atkinson Hyperlegible Next** | Sans-serif elements | Optional — falls back to Libertinus Sans |

Missing optional fonts trigger a `\ClassWarning` and degrade gracefully. Run `build.py doctor` to check font availability. See `assets/fonts/README.md` for manual installation instructions.

## Installation

### Prerequisites

- TeX Live 2025+ with LuaLaTeX (`tlmgr install scheme-medium`)
- Python 3.10+ (for `build.py` and test suite)
- Git

### Nix (recommended)

```bash
git clone https://github.com/WyattAu/OmniLaTeX-template.git
cd OmniLaTeX-template
nix develop    # or: direnv allow
python build.py build-example minimal-starter
```

### Docker

A pre-built image with TeX Live, fonts, and all tools:

```bash
docker run -it --rm -v $(pwd):/workspace ghcr.io/wyattau/omnilatex-docker:latest
python build.py build-example minimal-starter
```

For development, use `docker-compose.yml.example` or `devcontainer.json.example` (VS Code). The Docker image is built automatically via [`.github/workflows/docker-ci.yml`](.github/workflows/docker-ci.yml) on every push to `main` and on version tags.

### Local TeX Live

```bash
tlmgr install luatex latexmk collection-latex collection-bibtexextra \
  collection-mathscience collection-plots fontspec libertinus polyglossia
python build.py build-example minimal-starter
```

### VS Code

The project includes a Dev Container configuration. Open in VS Code with the Dev Containers extension — TeX Live, Python, and all tools are pre-installed.

## Build Script

```bash
python build.py build-example thesis     # Build one example
python build.py build-examples           # Build all examples
python build.py build-root               # Build root document
python build.py build-examples -j 4      # Parallel build (4 jobs)
python build.py build-examples --force   # Force rebuild (clean aux files)
python build.py watch                    # Watch for changes, rebuild
python build.py test                     # Run full test suite
python build.py preflight                # Validate environment
python build.py doctor                   # Health diagnostics
python build.py diff <example>           # Visual regression check
python build.py clean                    # Remove build artifacts
```

## CI/CD Integration

Built-in pipelines for 5 platforms:

| Platform | Config |
|----------|--------|
| GitHub Actions | `.github/workflows/build.yml` |
| GitLab CI | `.gitlab/ci/pipeline.yml` |
| Gitea | `.gitea/workflows/build.yml` |
| Forgejo | `.forgejo/workflows/build.yml` |
| Woodpecker | `.woodpecker/workflows/pipeline.yml` |

### Environment Variables

- `CI_COMMIT_SHA` / `GITHUB_SHA` — Commit hash (embedded in PDF metadata)
- `CI_COMMIT_REF_NAME` / `GITHUB_REF_NAME` — Branch name
- `CI_PROJECT_PATH` / `GITHUB_REPOSITORY` — Repository slug
- `SOURCE_DATE_EPOCH` — Unix timestamp for reproducible builds

### Pages Deployment

Set the public base URL for PDF verification:
- GitHub Pages: automatic
- Other: set `OMNILATEX_VERIFICATION_BASE_URL`, `CF_PAGES_URL`, or `PAGES_URL`

## PDF Verification

Commit SHA verification embeds a verification link in each PDF. Access at `pages/verify.html`.

## Configuration

Customize documents through configuration files:

```
config/
├── document-settings.sty        # Global settings
├── document-types/
│   ├── thesis.sty               # Thesis profile
│   ├── article.sty              # Article profile
│   └── ...                      # 16 document type profiles
└── institutions/
    ├── tuhh/                    # TUHH branding
    ├── tum/                     # TU Munich branding
    ├── eth/                     # ETH Zürich branding
    ├── generic/                 # Customizable template
    └── README.md                # How to add your institution
```

## Project Structure

```
├── omnilatex.cls                # Main document class (249 lines)
├── build.py                     # Build automation (1,857 lines)
├── build.lua                    # l3build configuration
├── .latexmkrc                   # LaTeX compilation settings (260 lines)
├── flake.nix                    # Nix flake (devShell + checks)
├── config/                      # Document type and institution configs
├── lib/                         # 21 modules across 9 subdirectories
│   ├── core/                    # Build modes, utilities
│   ├── layout/                  # Page layout, floats, KOMA-Script
│   ├── typography/              # Fonts, math, typesetting, lists
│   ├── references/              # Bibliography, glossary, hyperref
│   ├── language/                # Internationalization (polyglossia)
│   ├── graphics/                # Images, SVG, TikZ
│   ├── code/                    # Code listings (minted)
│   ├── tables/                  # Table formatting
│   └── utils/                   # Colors, TODO notes, censoring
├── lua/                         # Lua scripts (git metadata)
├── examples/                    # 24 example templates
├── specs/                       # Formal specifications and Lean 4 proofs
├── tests/                       # Test suite (l3build + pytest + visual regression)
├── docs/                        # API reference (auto-generated)
└── pages/                       # Web assets (verification page)
```

## Testing

| Suite | Tool | Coverage |
|-------|------|----------|
| Module unit tests | l3build | 21 modules with `.tlg` baselines |
| Property-based tests | hypothesis + pytest | 92 doctype × language combinations |
| Unicode stress tests | pytest | 10 scripts (CJK, RTL, emoji, combining) |
| Edge case tests | pytest | Empty, large, nested documents |
| Negative tests | pytest | Invalid inputs, missing resources |
| Visual regression | SSIM comparison | PDF layout comparison |
| Module smoke tests | Python | 10 build-mode combinations |
| Reproducibility | Nix check | Byte-for-byte deterministic builds |

```bash
python build.py test              # Run all tests
python build.py test --verbose    # Verbose output
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Adding institution configs, languages, and doctypes
- Development setup (Docker, Nix, local TeX Live)
- PR checklist and code style conventions

## License

Apache License 2.0 — see [LICENSE](LICENSE).

## Acknowledgments

- Originally forked from the [TUHH LaTeX Template](https://collaborating.tuhh.de/m21/public/theses/itt-latex-template)
- Built with KOMA-Script, LaTeX3/expl3, polyglossia, minted, biblatex, TikZ, and the TeX Live ecosystem
