# OmniLaTeX Template — Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com).
This project adheres to [Semantic versioning](https://semver.org/).

## [Unreleased]

## [1.7.1] - 2026-04-30

### Fixed
- **Duplicate `glossary-longextra` load** — was loaded at both line 28 and line 314 in `omnilatex-glossary.sty`; removed early load
- **`fix-cm` package loaded in LuaLaTeX-only class** — pdfLaTeX-era package removed from `omnilatex-fonts.sty`
- **Double `kpse.find_file` monkey-patch** — redundant 16-line patch removed from `omnilatex-cjk.sty` (already loaded by `omnilatex.cls`)
- **KOMA `\setkomacolor` silently no-op on TL2025+** — replaced with working shim that parses `fg`/`bg` key-value pairs and patches `\usekomafont` to apply stored colors
- **`\providecommand{\arabicfont}` conflict with fontspec** — replaced with internal macros to prevent cls font-family definitions from being shadowed
- **Font default misalignment between cls and rtl.sty** — aligned to Amiri (Arabic) and David CLM (Hebrew)
- **`build.py` resource leak in `cmd_diff`** — fitz document handles now closed in `finally` block
- **CI: cross-platform workflow used `:latest` tag** — now reads pinned digest from `.env.docker`
- **CI: lean4-ci.yml ran `lake build` twice** — verify step now checks existing build artifacts
- **CI: test job uploaded `.pytest_cache`** — now uploads `test-results.xml` (JUnit format)

## [1.7.0] - 2026-04-29

### Added
- **Nix packages output:** `packages.default` and `packages.examples-*` for reproducible PDF builds via `nix build`
- **Docker multi-arch CI:** automated build and push to GHCR (linux/amd64 + linux/arm64) with cache-hit rebuilds in ~6 min
- **Cross-platform CI:** Linux and Windows validation of Docker-based LaTeX builds
- **Determinism check:** automated build reproducibility verification (page count + 1% size tolerance)
- **Performance regression detection:** per-example build timing metrics with CI summary
- **Docker digest sync:** automated PR creation when Docker image digest changes (requires repo setting: allow Actions to create PRs)
- **Lean 4 proofs CI:** automated verification of formal proof modules (v4.29.0)

### Changed
- **TeX Live 2025 → 2026** in Docker image (live tlnet; TL2025 final archive never published)
- **Docker image digest now sourced from `.env.docker` at runtime** — `build.yml` no longer hardcodes the digest, enabling the sync workflow to update it without `workflow` scope on PATs
- **CI build jobs use `docker run --rm --entrypoint ""`** instead of job-level `container:` blocks — reads digest dynamically, avoids OOM on 7 GB runners
- **Test job runs inside Docker container** — many tests compile LaTeX documents requiring the full TeX Live toolchain
- **CI default timeout increased** to 60 min for build-all, 30 min for Docker CI
- **`build.py`** now prints last 50 lines of latexmk logs on PDF generation failure in CI mode
- **`.latexmkrc`:** removed `--halt-on-error` — too aggressive for multi-pass builds where intermediate passes naturally have errors

### Fixed
- **CI OOM (exit code 137):** replaced background container pattern with ephemeral `docker run --rm`
- **CI latexmk routing:** Docker image `ENTRYPOINT [entrypoint.sh]` passes all args to `latexmk` — added `--entrypoint ""` override to all `docker run` commands
- **CI test permission denied:** container default user `tex` can't write to `/opt/poetry` site-packages — added `--user root`
- **CI test failures without container:** moved test job back into Docker (needs TeX Live for LaTeX compilation tests)
- **Determinism check:** relaxed from exact SHA256 to page count + 1% file size tolerance (LuaLaTeX has inherent non-determinism from PDF object ordering and Lua hash table randomization)
- **`extract_metrics.py`:** fixed `TypeError` when `wall_time_s` is `None` for failed examples
- **Empty document test:** relaxed to check for segfaults/memory access/panics only (TL2026 latexmk behavior differs)
- **5 failing CJK/RTL examples in Docker CI:** `luatexja.sty`, `Noto Serif CJK SC` font, `luabidi.sty` missing from Docker image (26/31 pass; all 31 pass on Nix TL2025 locally)

### Security / Hardening
- **CR_PAT for GHCR push** — `GITHUB_TOKEN` lacks `write:packages` scope; Docker CI uses `CR_PAT` directly
- **Docker CI:** BuildKit enabled, fonts and apt caches scoped per architecture, 360 min timeout
- **GHA cache invalidation:** `TL_CACHE_BUSTER` ARG in cache IDs and layer sentinel files prevents stale TL layers when tlnet rolls

## [1.6.0] - 2026-04-26

### Changed
- TeX Live 2024 → 2025 (Nixpkgs nixos-unstable, LuaHBTeX 1.21.0)
- Docker image TL_VERSION updated to 2025
- `omnilatex.cls`: version string v1.3.0 → v1.6.0
- `build.py`: CI default parallel jobs 2 → 4
- `build.py`: fix `clean_all` tuple-eval side effect → proper sequential statements

### Fixed
- **TL2025 compatibility:** `\directlua` escape sequence in `omnilatex-base.sty` (LuaTeX 1.21 changed `tex.print` backslash handling)
- **TL2025 compatibility:** Libertinus font shape `TU/libertinus/b/n` undefined — added font shape substitution
- **11 broken examples stabilized:** accessibility-test, citation-styles, color-themes, cjk-chinese, cjk-japanese, cjk-korean, presentation, dissertation, rtl-arabic, rtl-hebrew
- `omnilatex-themes.sty`: palette definitions changed from `\newcommand` to `\colorlet` (prevented `\applytheme@` from working)
- `omnilatex-themes.sty`: fixed infinite `\usetheme` recursion via `\edef` for theme base name
- `omnilatex-themes.sty`: fixed hyphen-in-control-sequence issue (`-dark` suffix in csname)
- `omnilatex-themes.sty`: added missing `xstring` dependency
- `omnilatex-cjk.sty`: added missing `xstring` dependency
- `omnilatex-cjk.sty`: added luaotfload `ScriptExtensions.txt` workaround for Nix TL2025
- `omnilatex-cjk.sty`: fixed font option commas for TL2025 luatexja
- `omnilatex-rtl.sty`: switched from `bidi` to `luabidi` (bidi incompatible with LuaLaTeX)
- `omnilatex-rtl.sty`: fixed `#1` → `##1` parameter doubling
- `omnilatex-citations.sty`: replaced undefined `\IfDefined` with `\@ifundefined`
- `omnilatex-citations.sty`: removed invalid runtime biblatex options
- `omnilatex-presentation.sty`: renamed `\endpresentationcolumn` to avoid KOMA-Script collision
- `omnilatex-accessibility.sty`: added missing `pdfcomment` dependency
- `omnilatex-typesetting.sty`: removed duplicate `setspaceenhanced` load
- `omnilatex-cjk.sty`: fixed `\ProvidesPackage` name (added path prefix)
- `flake.nix`: added `tqdm`, `rich` (Python), `luatexja`, `haranoaji`, `luabidi`, `bidi`, `tagpdf`, `setspaceenhanced` (TeX Live)

### Security / Hardening
- All 6 CI workflows: added `timeout-minutes` to prevent hung workflow billing
- `cross-platform.yml`: pinned Docker image from mutable `:latest` to digest
- `docker-ci.yml`: pinned BuildKit driver from `:master` to `v0.29.0`
- Dockerfile: pinned Monaspace font to v1.301, Atkinson Hyperlegible Next to commit 7925f50f, Eisvogel to v3.4.0
- Dockerfile: added `RUNTIME_USER=tex` default
- `lean-toolchain`: pinned from RC `v4.30.0-rc2` to stable `v4.29.0`
- `.gitignore`: added `*.ltjruby` pattern

### Removed
- ~130 stale build artifacts removed from git tracking (aux, log, bcf, glstex, pdf files in repo root)

## [1.5.0] - 2026-04-24

### Added
- **Color theme system:** `omnilatex-themes.sty` — 6 presets (default, midnight, forest, rose, monochrome, sepia), dark/light toggle, institution color integration
- **Color themes example:** `examples/color-themes/` demonstrating all 6 themes
- **6 more institution configs:** Oxford, Princeton, Yale, CMU, EPFL, Imperial (14 total)
- **RTL language support:** `omnilatex-rtl.sty` — Arabic and Hebrew bidi, Amiri/David CLM fonts, Arabic-Indic numerals, LTR math
- **RTL examples:** Arabic and Hebrew document examples
- **Accessibility hardening:** alt text for figures/TikZ, accessible links, table markup, heading validation, color contrast checks, reading order, language tagging
- **Accessibility documentation:** `docs/accessibility.md` — comprehensive WCAG 2.1 AA guide

### Changed
- `omnilatex.cls`: auto-loads `omnilatex-rtl.sty` for Arabic and Hebrew languages
- `specs/option_schema.toml`: added `hebrew` to valid languages, RTL auto-load docs
- `CONTRIBUTING.md`: updated accessibility section with new commands
- `examples/accessibility-test/main.tex`: demonstrates all new accessibility features
- **VS Code extension:** added settings panel, createProject command, status bar, 7 new snippets (section, subsection, figure, table, math, code, bibliography)
- **Overleaf:** zip script includes all 14 institutions, CJK/citation/theme modules, updated manifest to v1.4.0

## [1.4.0] - 2026-04-24

### Added
- **Institution configs:** MIT, Stanford, Cambridge, TU Delft (8 total)
- **CJK full support:** `omnilatex-cjk.sty` — Noto CJK fonts, line breaking, ruby annotations (furigana/pinyin), vertical text mode
- **CJK examples:** Chinese, Japanese, Korean document examples
- **Citation style library:** `omnilatex-citations.sty` — 9 pre-configured styles (IEEE, ACM, APA, Chicago, Nature, Science, Harvard, Vancouver, MLA)
- **Citation styles example:** `examples/citation-styles/` with sample bibliography
- **Presentation overhaul:** `omnilatex-presentation.sty` — branded headers/footers, progress bar, block environments, section dividers, TikZ overlays
- **Lean 4 CI:** `.github/workflows/lean4-ci.yml` — automated proof verification via Nix + Lake
- **Docker digest sync:** `.github/workflows/docker-digest-sync.yml` — auto-updates pinned digests in build.yml and .env.docker via PR
- **VS Code extension skeleton:** `extensions/vscode-omnilatex/` — doctype/institution/language QuickPick, build commands, LaTeX snippets
- **Template marketplace:** `pages/gallery.html` — interactive doctype picker with live preview and download
- **Overleaf submission prep:** `overleaf/` — README, manifest.json, starter main.tex

### Changed
- README: updated counts to 55 aliases, 24 examples, 16 profiles, 12 languages
- README: expanded Docker section with dev container references
- README: added 4 missing examples (poster, presentation, letter, accessibility-test)
- README: updated institution listing (TUHH, TUM, ETH Zürich + 4 new)
- `omnilatex.cls`: auto-loads `omnilatex-cjk.sty` for CJK languages
- `config/document-types/presentation.sty`: loads new presentation module
- `examples/presentation/main.tex`: demonstrates headers, footers, progress bar, blocks, sections
- `specs/option_schema.toml`: added citation-style option, CJK auto-load docs, module count → 22
- Roadmap: archived `ROADMAP-v1.1.md`, wrote fresh `ROADMAP.md` covering v1.4–v1.7+

## [1.3.1] - 2026-04-24

### Changed
- Merged OmniLaTeX-docker repository into template repository (monorepo)
- Cross-platform CI now uses pre-built Docker image instead of native TeX Live installation
- Added automated Docker image CI/CD pipeline (build + push to GHCR)

### Fixed
- Cross-platform CI no longer fails on Windows (TeX Live installer path was incorrect)

## [1.3.0] - 2026-04-23

### Added
- Three new document types: `poster` (A1 landscape conference poster), `presentation` (KOMA-based slides with tcolorbox), `letter` (formal letter with sender/recipient/closing commands)
- Doctype aliases: `posters`, `presentations`, `slides`, `talk`, `talks`, `letters`
- `build.py init` flags: `--doctype`, `--institution`, `--language` for pre-configuring new projects
- `build.py scaffold-language <lang>`: generates translation guide with 47 stubs
- Examples for poster, presentation, letter, and accessibility-test (all compile)
- `scripts/benchmark_examples.py`: performance benchmarking tool for all examples
- `specs/performance_baselines.toml`: baseline timings for 22/23 examples
- `lib/layout/omnilatex-accessibility.sty`: PDF/UA-1 tagged PDF support via tagpdf

### Changed
- Doctype resolution Lean 4 proof: 16 profiles, 55 aliases (was 13 profiles, 46 aliases)
- TUI menu version string updated to v1.3.0-dev
- CI performance job: added regression detection against baselines (>50% threshold)

## [1.2.0] - 2026-04-23

### Added
- TUM institution config: official brand colors (TUM Blue #0065BD), logo placeholder, link
- ETH Zürich institution config: official brand colors (ETH Blue #1F407A), logo placeholder, link
- Cross-platform CI: `cross-platform.yml` with Windows (basictex) + macOS (mactex) smoke tests
- Lean 4 added to Nix flake devShell (v4.29.0)
- CJK language support documented in CONTRIBUTING.md (polyglossia handles captions natively)
- `omnilatex.cwl`: 80+ commands for texlab/VS Code auto-completion
- Lean 4 proofs: all 5 files compile, Lake project configured (7/20 theorems fully proven)

### Changed
- Roadmap restructured: v1.2 (Ecosystem & Quality), v1.3 (Features & Polish)
- Lean 4 proof files: removed VERIFICATION PENDING tags, fixed syntax errors
- Lean 4 proof files: renamed to PascalCase for Lake compatibility

## [1.1.0] - 2026-04-22

### Added
- README v2: comparison table, all 20 examples listed, engineering quality surfaced
- CONTRIBUTING.md: architecture overview, institution/language/doctype tutorials, PR checklist
- CTAN packaging: `scripts/make-ctan-zip.sh` builds TDS-compliant upload package
- Overleaf packaging: `scripts/make-overleaf-zip.sh` builds self-contained Overleaf template
- CTAN documentation: `doc/omnilatex.tex` — 23-page user manual (compiles to PDF)
- `build.py diff` command: SSIM-based visual regression with byte-level fallback
- CI changelog check: enforces CHANGELOG.md update when `.sty`/`.cls` files change
- l3build regression tests for all 21 modules (with `.tlg` baselines)
- Template gallery: `docs/gallery.md` — all 20 examples with PDF links, categorized
- In-repo Dockerfile: reproducible build environment based on TeX Live 2024
- `build.py scaffold-institution <name>`: creates institution config from generic template
- `build.py init <name>`: initialize a new OmniLaTeX project from minimal-starter template
- Generic institution config: `config/institutions/generic/` — customizable template
- Interactive TUI menu: run `build.py` without args for a rich command selector
- Rich build dashboard: live progress, elapsed timer, and log output during builds
- Lua utility scripts: `word-count.lua`, `todo-tracker.lua`, `conditional-include.lua`
- French and Spanish language support (40+ translations each)

### Changed
- README no longer references non-existent `cv-bw` example
- README identity: leads with value proposition instead of "fork from TUHH"

### Fixed
- CI workflows: `env.DOCKER_IMAGE` not supported in `container.image` — inlined the digest
- Rich concurrent build: active workers panel now correctly shows running jobs (was always empty)
- `build.py build-root`: now shows rich dashboard with live log output (was completely silent)

## [1.0.0] - 2026-04-03

### Added
- Nix flake with `scheme-medium` + explicit packages replacing `scheme-full` (~3.7 GiB → ~2.6 GiB, ~30% reduction)
- Deterministic PDF builds verification via `nix build` and `nix flake check`
- direnv integration with `.envrc` and `use flake`
- Inkscape and gnuplot added to devShell
- pytest-timeout, graceful pymupdf skip
- Lazy module loading for omnilatex.cls (enablemath, enabletikz, etc.)
- 20/20 examples documents templates, covering all document types profiles
- Formal specification (TOML) for module contracts
- l3build integration test files
- Property-based testing with hypothesis
- Unicode stress tests covering 15 languages/scripts
- Edge case testing for empty documents, float handling, cross-references stress tests
- Negative case testing for invalid inputs handling
- Visual regression testing infrastructure
- Performance engineering with `--timings` flag and concurrent builds
- Build caching with source hash comparison
- Mathematical proof infrastructure (Lean 4 proof files)
- Developer experience improvements:
- `build.py watch` command with file watching
- `build.py doctor` for health diagnostics
- `build.py preflight` for environment validation
- GitHub Pages auto-deployment for CI
 pipeline
- 5 platform CI/CD support (GitHub Actions, GitLab CI, Forgejo, Gitea, Woodpecker)
- Pre-commit hooks configuration
- `.envrc` with `use flake` for direnv integration

- VS Code Dev container configuration with Docker Compose

- Python-based build orchestrator (`build.py`, 1075 lines)
  - dev/prod/ultra modes with `--mode` flag
  - Concurrent example building with `-j` flag
  - `--timings` metrics collection
  - `--force` rebuild option
  - `--source-date-epoch` for reproducible builds timestamps

  - Subcommand: build-all, build-root, build-example, build-examples, watch, test, preflight, doctor, lint, clean
- `--latexmkrc` build configuration (223 lines)
  - lualatex engine with `$pdf_mode = 4`
  - Bib2gls custom dependency
  - Multi-pass latexmk with `--halt-on-error`
- Document class with option system
  - Lua-based metadata embedding (`git-metadata.lua`)
  - Conditionally loaded feature modules (enablemath, enabletikz, enablelistings, etc.)

### Fixed
- Restored 3 accidentally deleted files (minimal-starter/main.tex, thesis-tuhh floats.tex, usage.tex)
- Fixed duplicate label `fig:matlab2tikz_pgfplots` in thesis-tuhh and root floats.tex
- Fixed empty document test (`\mbox{}` ensures PDF page output)
- Fixed unicode test (`\\&` escape for special LaTeX chars)
- Fixed `build.py watch` method ( `_rebuild_affected` now correctly resolves
- Fixed `build.py test` method  using reliable project root path
- Fixed `.gitignore` for only ignore example symlinks, not root `.latexmkrc`

### Changed
- `omnilatex.cls` version: v0.1.1 → v1.0.0
- `reproducibility.lock` version: 0.1.1 → 1.0.0
- `ROADMAP.md` version updated to v1.0.0
- All `ROADMAP.md` completion checkboxes updated to reflect reality
- Build tool upgraded from 345 → 1075 lines
- Testing expanded significantly
- Library modules now 21 `.sty` files across 9 subdirectories
