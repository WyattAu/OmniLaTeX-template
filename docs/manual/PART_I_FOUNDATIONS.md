# Part I: Foundations — Detailed Chapter Plans

---

## Chapter 10: Installation

**Purpose:** Get OmniLaTeX running on any platform in under 10 minutes.

**Sections:**
1. **Prerequisites** — Docker (recommended), Nix (alternative), TeX Live 2026 (manual)
2. **Docker Method** — Pull image, verify, first build
   ```
   docker pull ghcr.io/wyattau/omnilatex-docker
   docker run --rm --entrypoint "" -v "$PWD:/workspace" -w /workspace \
     ghcr.io/wyattau/omnilatex-docker python3 build.py build-all
   ```
3. **Nix Method** — `nix develop .#`, `lake build` for Lean
4. **TeX Live Method** — `tlmgr install omnilatex` (after CTAN publishes)
5. **DevContainer** — VS Code one-click setup
6. **Verification** — Run test suite, check all 43 examples build
7. **Troubleshooting** — Common issues table (missing fonts, permission errors, memory)

**Key cross-refs:** Chapter 12 (build system), Chapter 102 (Docker workflow), Chapter 103 (Nix workflow)

---

## Chapter 11: Quick Start

**Purpose:** 5-minute first document. Copy-paste ready.

**Sections:**
1. **Minimal Document** — Smallest possible OmniLaTeX document
   ```latex
   \documentclass{omnilatex}
   \begin{document}
   Hello, OmniLaTeX!
   \end{document}
   ```
2. **Adding Options** — Language, doctype, institution
3. **Your First Real Document** — Complete article with title, sections, a figure, bibliography
4. **Building** — `build.py build-example article`
5. **Next Steps** — Links to relevant chapters

**Demonstrates:** `omnilatex.cls` loading, class options, `\section`, `\begin{figure}`, `\cite`

---

## Chapter 12: Build System

**Purpose:** Complete reference for `build.py` and `latexmk`.

**Sections:**
1. **build.py Overview** — Python build orchestrator, 2060 lines, all commands
2. **Build Commands** — Table of all commands with examples:
   | Command | Description |
   |---|---|
   | `build.py build-all` | Build root + all 43 examples |
   | `build.py build-examples` | Build all examples only |
   | `build.py build-example <name>` | Build single example |
   | `build.py build-root` | Build root document |
   | `build.py clean` | Remove build artifacts |
   | `build.py clean-aux` | Remove only auxiliary files |
   | `build.py list` | List all examples |
3. **Global Flags** — `--mode`, `--force`, `--timings`, `--verbose`, `--source-date-epoch`
4. **Build Modes** — `dev` (3 passes), `prod` (full validation), `ultra` (2 passes, no bib)
5. **Incremental Builds** — Source hash caching, `build_cache.json`, cache hit/miss logic
6. **latexmk Configuration** — `.latexmkrc`, interaction modes, output directory
7. **Parallel Builds** — 4 concurrent workers, `--force` bypass
8. **Performance** — Full build-all in ~14 minutes, per-example timing

**Key cross-refs:** Chapter 100 (build modes), Chapter 102 (Docker workflow), Chapter 104 (CI/CD)

---

## Chapter 13: Class Options

**Purpose:** Complete reference for all 15 class options.

**Sections:**
1. **Option Loading** — How `\documentclass[options]{omnilatex}` works
2. **Option Reference Table:**
   | Option | Type | Default | Chapter |
   |---|---|---|---|
   | `language` | string | `english` | Ch 40 |
   | `doctype` | string | `thesis` | Ch 14 |
   | `institution` | string | `none` | Ch 53 |
   | `titlestyle` | string | `book` | Ch 52 |
   | `censoring` | bool | false | Ch 92 |
   | `loadGlossaries` | bool | false | Ch 72 |
   | `todonotes` | bool | false | Ch 92 |
   | `enablefonts` | bool | false | Ch 30 |
   | `enablegraphics` | bool | false | Ch 61 |
   | `enablemath` | bool | true | Ch 32 |
   | `enabletikz` | bool | true | Ch 60 |
   | `enableengineering` | bool | true | Ch 64 |
   | `enablecode` | bool | true | Ch 80 |
   | `enabletables` | bool | true | Ch 62 |
   | `a5` | void | — | Ch 50 |
3. **Option Combinations** — Common patterns, conflicts to avoid
4. **Custom Options** — How to add project-specific options via `document-settings.sty`

**Key cross-refs:** All Part II-V chapters (each option links to its detailed chapter)

---

## Chapter 14: Doctype System

**Purpose:** How the 55+ doctype aliases map to 3 KOMA classes.

**Sections:**
1. **Architecture** — Three-tier system: user alias → canonical name → KOMA class
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
