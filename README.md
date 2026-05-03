# OmniLaTeX

A modular, engineering-grade LaTeX document class for academic and professional documents. 55+ doctype aliases, 27 modules, 31 example templates, byte-for-byte reproducible builds, and formal Lean 4 verification.

Built on LuaTeX (LuaHBTeX 1.21.0) + KOMA-Script + TeX Live 2025. Compile with `latexmk -lualatex` or `build.py`.

## Why OmniLaTeX

| | OmniLaTeX | Typical template |
|---|---|---|
| **Document types** | 55+ aliases (thesis, CV, patent, journal, ...) | 1–3 |
| **Test coverage** | 239 test cases + 27 l3build modules | 0 |
| **Reproducible builds** | Byte-for-byte deterministic | No |
| **Formal verification** | Lean 4 proofs (8 modules, 13/20 theorems) | No |
| **CI platforms** | 6 GitHub Actions workflows + 4 other platforms | 0–1 |
| **Font fallbacks** | Graceful degradation with warnings | Crash or silent substitution |
| **Institution configs** | 14 pluggable (`config/institutions/`) | Hardcoded |
| **Languages** | 14 via polyglossia (EN, DE, FR, ES, PT, IT, NL, RU, ZH, JA, KO, AR, HE, DA) | 0–2 |
| **Citation styles** | 9 (IEEE, ACM, APA, Chicago, Nature, Science, Harvard, Vancouver, MLA) | 0–1 |
| **Color themes** | 6 + dark/light toggle (default, midnight, forest, rose, monochrome, sepia) | 0 |

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

- **55+ doctype aliases** resolving to 16 document profiles across 3 KOMA-Script base classes
- **27 modular `.sty` packages** with formal interface contracts
- **Lazy module loading** — only load what you need (`enablemath`, `enabletikz`, `enablecode`, ...)
- **Modern font stack** — Libertinus Serif + Math, Monaspace Neon, Atkinson Hyperlegible Next (with graceful fallback)
- **Reproducible builds** — `SOURCE_DATE_EPOCH` support, byte-for-byte deterministic PDFs
- **Multi-language** — 14 languages via polyglossia (EN, DE, FR, ES, PT, IT, NL, DA, RU, ZH, JA, KO, AR, HE); CJK and RTL support auto-loaded per language
- **Institution branding** — 14 pluggable configs in `config/institutions/` (ETH Zürich, TUHH, TUM, MIT, Stanford, Cambridge, TU Delft, Oxford, Princeton, Yale, CMU, EPFL, Imperial, generic)
- **Citation styles** — 9 pre-configured styles via `\citationstyle{}` (IEEE, ACM, APA, Chicago, Nature, Science, Harvard, Vancouver, MLA)
- **Color themes** — 6 themes with dark/light toggle: default, midnight, forest, rose, monochrome, sepia
- **Accessibility** — PDF/UA-1 tagged PDF output via tagpdf
- **CJK support** — automatic CJK font selection for Chinese, Japanese, Korean with Haranoaji/Noto fallback
- **RTL support** — automatic bidirectional text for Arabic and Hebrew
- **Code listings** — syntax highlighting via minted with cached compilation
- **Engineering diagrams** — 1,000+ lines of TikZ shapes: thermodynamics, P&ID, flowcharts
- **Formal verification** — Lean 4 proofs (8 modules, 13/20 theorems proven)
- **Build automation** — `build.py` with watch mode, concurrent builds, timing metrics, and health diagnostics

## Document Types

23 document type profiles across 3 KOMA-Script base classes. Switch with `\documentclass[doctype=<type>]{omnilatex}`.

| Type | Class | Description |
|------|-------|-------------|
| `thesis` | scrbook | Academic thesis with chapters, bibliography, declaration |
| `dissertation` | scrbook | PhD dissertation with front matter and committee |
| `article` | scrartcl | Research article with abstract, keywords, DOI |
| `journal` | scrartcl | Journal article with volume, issue, highlights |
| `inlinepaper` | scrartcl | Compact two-column inline research paper (arXiv style) |
| `book` | scrbook | Book-length document with publisher metadata |
| `manual` | scrreprt | Product manual / handbook with version and support info |
| `technicalreport` | scrreprt | Technical report with report number and confidentiality |
| `standard` | scrreprt | Standards document with ICS codes and designation |
| `patent` | scrreprt | Patent specification |
| `cv` | scrartcl | Curriculum vitae with photo, links, and summary |
| `cover-letter` | scrartcl | Cover letter with recipient and sender metadata |
| `poster` | scrartcl | Conference poster (A1 landscape) |
| `presentation` | scrartcl | Presentation slides (KOMA-based) |
| `letter` | scrartcl | Formal letter with recipient, subject, and closing |
| `dictionary` | scrbook | Dictionary / lexicon with series and publisher |
| `homework` | scrartcl | Homework assignment with exercises and solutions |
| `exam` | scrartcl | Examination paper with questions and answer spaces |
| `research-proposal` | scrreprt | Research proposal with budget and timeline |
| `lecture-notes` | scrartcl | Lecture notes with theorem environments |
| `syllabus` | scrartcl | Course syllabus with grading policy and schedule |
| `handout` | scrartcl | Two-column handout with key concept boxes |
| `memo` | scrartcl | Memorandum with TO/FROM/CC/RE fields |

All options: `language`, `doctype`, `titlestyle`, `institution`, `censoring`, `loadGlossaries`, `todonotes`, `enablefonts`, `enablegraphics`, `enablemath`, `enabletikz`, `enableengineering`, `enablecode`, `enabletables`.

## Languages

OmniLaTeX supports 9 primary languages and 19 secondary languages via Polyglossia:

**Primary (full support with translations):** English, German, French, Spanish, Chinese (Simplified + Traditional), Japanese, Korean, Arabic, Hebrew, Persian

**Secondary (available for inline use):** German (new spelling), Italian, Portuguese, Russian, Dutch, Polish, Czech, Greek, Turkish

## Examples

31 ready-to-use templates in `examples/` (30 compile on TeX Live 2025; `thesis-tuhh` requires TUHH assets):

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
| `cjk-chinese` | article | Chinese document with CJK fonts |
| `cjk-japanese` | article | Japanese document with CJK fonts |
| `cjk-korean` | article | Korean document with CJK fonts |
| `rtl-arabic` | article | Arabic document with RTL support |
| `rtl-hebrew` | article | Hebrew document with RTL support |
| `citation-styles` | article | Demonstrates all 9 citation styles |
| `color-themes` | article | Demonstrates all 6 color themes + dark/light toggle |

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

### CTAN (recommended)

OmniLaTeX is available on CTAN. Install via your TeX distribution's package manager:

```bash
tlmgr install omnilatex
```

After installation, place the document-types and configuration in your project (see [Quick Start](#quick-start)).

### Nix

```bash
git clone https://github.com/WyattAu/OmniLaTeX-template.git
cd OmniLaTeX-template
nix develop    # or: direnv allow
python build.py build-example minimal-starter
```

### Docker

A pre-built multi-arch image (linux/amd64, linux/arm64) with TeX Live 2025, fonts, and all tools. Built with BuildKit and digest-pinned in CI:

```bash
docker run -it --rm -v $(pwd):/workspace ghcr.io/wyattau/omnilatex-docker:latest
python build.py build-example minimal-starter
```

For development, use `docker-compose.yml.example` or `devcontainer.json.example` (VS Code). The Docker image is built automatically via [`.github/workflows/docker-ci.yml`](.github/workflows/docker-ci.yml) on every push to `main` and on version tags. Image digests are synchronized to CI workflows automatically via [`.github/workflows/docker-digest-sync.yml`](.github/workflows/docker-digest-sync.yml).

### Local TeX Live

```bash
tlmgr install luatex latexmk collection-latex collection-bibtexextra \
  collection-mathscience collection-plots fontspec libertinus polyglossia
python build.py build-example minimal-starter
```

### VS Code

The project includes a Dev Container configuration. Open in VS Code with the Dev Containers extension — TeX Live, Python, and all tools are pre-installed. A dedicated [OmniLaTeX VS Code extension](extensions/vscode-omnilatex/) provides doctype picker, institution switcher, and build commands.

### Overleaf

1. Generate a project zip locally: `bash scripts/make-overleaf-zip.sh thesis`
2. Upload to Overleaf: **Menu → New Project → Upload Project**
3. Set compiler to **LuaLaTeX**: **Menu → Compiler → LuaLaTeX**
4. Recompile

See [Overleaf Guide](docs/OVERLEAF.md) for details.

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

### GitHub Actions

6 workflows using digest-pinned Docker images for reproducibility:

| Workflow | Purpose |
|----------|---------|
| `build.yml` | Build all examples and run test suite |
| `cross-platform.yml` | Test across multiple platforms |
| `docker-ci.yml` | Build and push Docker image (multi-arch) |
| `docker-digest-sync.yml` | Sync image digests to CI workflows |
| `lean4-ci.yml` | Compile and verify Lean 4 proofs |
| `integration-matrix.yml` | Cross-version compatibility matrix |

### Other Platforms

| Platform | Config |
|----------|--------|
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
    ├── eth/                     # ETH Zürich branding
    ├── tuhh/                    # TUHH branding
    ├── tum/                     # TU Munich branding
    ├── mit/                     # MIT branding
    ├── stanford/                # Stanford branding
    ├── cambridge/               # Cambridge branding
    ├── tudelft/                 # TU Delft branding
    ├── oxford/                  # Oxford branding
    ├── princeton/               # Princeton branding
    ├── yale/                    # Yale branding
    ├── cmu/                     # CMU branding
    ├── epfl/                    # EPFL branding
    ├── imperial/                # Imperial College London branding
    ├── generic/                 # Customizable template
    └── README.md                # How to add your institution
```

## Project Structure

```
├── omnilatex.cls                # Main document class (363 lines)
├── build.py                     # Build automation
├── build.lua                    # l3build configuration
├── .latexmkrc                   # LaTeX compilation settings
├── flake.nix                    # Nix flake (devShell + checks)
├── config/                      # Document type and institution configs
├── lib/                         # 27 modules across 9 subdirectories
│   ├── core/                    # Build modes, utilities
│   ├── layout/                  # Page layout, floats, KOMA-Script, accessibility
│   ├── typography/              # Fonts, math, typesetting, lists
│   ├── references/              # Bibliography, glossary, hyperref, citations
│   ├── language/                # Internationalization (polyglossia, CJK, RTL)
│   ├── graphics/                # Images, SVG, TikZ
│   ├── code/                    # Code listings (minted)
│   ├── tables/                  # Table formatting
│   └── utils/                   # Colors, themes, TODO notes, censoring
├── lua/                         # Lua scripts (git metadata)
├── examples/                    # 31 example templates
├── specs/                       # Formal specifications and Lean 4 proofs
├── tests/                       # Test suite (l3build + pytest + visual regression)
├── docs/                        # API reference (auto-generated)
└── pages/                       # Web assets (verification page)
```

## Testing

| Suite | Tool | Coverage |
|-------|------|----------|
| Module unit tests | l3build | 27 modules with `.tlg` baselines |
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
