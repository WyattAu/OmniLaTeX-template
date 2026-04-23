# OmniLaTeX Template — Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com).
This project adheres to [Semantic versioning](https://semver.org/).

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

## [Unreleased]

### Added
- Three new document types: `poster` (A1 landscape conference poster), `presentation` (KOMA-based slides with tcolorbox), `letter` (formal letter with sender/recipient/closing commands)
- Doctype aliases: `posters`, `presentations`, `slides`, `talk`, `talks`, `letters`
- `build.py init` flags: `--doctype`, `--institution`, `--language` for pre-configuring new projects
- Examples for poster, presentation, and letter doctypes (all compile successfully)
- `scripts/benchmark_examples.py`: performance benchmarking tool for all examples
- `specs/performance_baselines.toml`: baseline timings for 22/23 examples
- `lib/layout/omnilatex-accessibility.sty`: PDF/UA-1 tagged PDF support via tagpdf
- `examples/accessibility-test/`: working tagged PDF example

### Changed
- Doctype resolution Lean 4 proof: 16 profiles, 55 aliases (was 13 profiles, 46 aliases)
- TUI menu version string updated to v1.3.0-dev

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
