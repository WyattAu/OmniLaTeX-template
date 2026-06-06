# Changelog

## v2.4.1 (2026-06-06)

### Fixed

- **builder.py discover_examples()**: Changed from relative `Path('examples')` to `REPO_ROOT / 'examples'` (tests failed when run from `tests/` directory)
- **test_ssim_benchmark.py**: Added missing `import numpy` in try block (was setting `_HAS_NUMPY = True` unconditionally)
- **WCAG compliance**: Added `aria-label` to card elements in `index.js` and `gallery.js` for screen reader accessibility
- **Focus indicators**: Restored `outline: 2px solid var(--accent)` on select focus in `gallery.css` (was `outline:none`)
- **verify.js**: Replaced HTML entity `&mdash;` with unicode `\u2014` in `textContent` assignment
- **CI/CD security**: Pinned `dependabot/fetch-metadata` to SHA `d7267f607e` (was unpinned `@v2`)
- **CI/CD timeouts**: Reduced `performance-regression.yml` from 90m to 45m, `docker-ci.yml` from 180m to 120m
- **setup-texlive**: Replaced hardcoded TeX Live year `2026` with dynamic `ls | sort -r | head -1` detection
- **GitLab templates**: Removed hardcoded `/assign @alex`; added top-level headings for markdownlint compliance

### Added

- **test_buildlib_coverage.py**: 50 new tests for builder cache eviction, source files, compile worker, profiler edge cases
- **test_coverage_batch2.py**: 70+ new tests for TUI menus (mocked input), commands helpers, diff modes, scaffold commands
- **Design tokens applied**: Spatial Materialism depth/transition tokens, Amoebic UI blob shapes/pill radii, Brutalist typography scale and border weights used in `style.css`, `gallery.css`, `index.css`
- **CTAN package**: Updated with latest .cls, .sty, lua/ files; fixed missing lua/ directory in zip
- **Overleaf package**: Updated manifest.json version to 2.4.0

### Changed

- **Test count**: 1234 -> 1334 fast tests (+100 new tests)
- **buildlib coverage**: 64% -> 73% (new threshold: 72%)
- **Inline CSS removed**: ~500 lines of duplicate `<style>` blocks removed from `index.html`, `gallery.html`, `verify.html`
- **ROADMAP.md**: Updated metrics, technical debt register (items #15, #23 corrected to 73%), release cadence

---

## v2.4.0 (2026-06-05)

### Fixed

- **All 50 examples now build in CI**: Removed all 6 example exclusions (accessibility-test, cjk-japanese, rtl-hebrew, beamer-defense, beamer-corporate, beamer-academic)
- **accessibility-test**: Removed `\RequirePackage{pdfmanagement-testphase}` (now in LaTeX kernel for TL2026); fixed BCP 47 language tag (`lang=en` not `lang=english`)
- **Color mode `bw`**: Added support for `bw` color mode in document settings (used by CV and manual doctypes) — sets `colorlinks=false` for print-friendly output
- **Link style `black`**: Added support for `black` link style in document settings (used by manual doctype) — sets black link/url/cite colors
- **CTAN test SIGPIPE**: Disabled `pipefail` for `unzip | head` pipe in `make-ctan-zip.sh` to prevent exit code 141
- **CTAN test subprocess**: Captured subprocess output in test fixture to avoid SIGPIPE in test environment
- **Pre-commit hooks**: Fixed `e.g.`/`i.e.` comma issues across all `lib/*.sty` files; fixed YAML duplicate key in `.pre-commit-config.yaml`
- **translations package**: Registered `simplifiedchinese` and `traditionalchinese` with `\DeclareLanguage` (not natively supported by translations v2.0)
- **Docker: Hebrew fonts**: Symlinked culmus fonts to texmf-local tree so fontspec finds David CLM
- **Docker: luaotfload**: Added `luaotfload-tool --update --force` after font installation
- **build-examples.yml**: Fixed `grep -vE ""` bug that filtered out all examples (empty regex matches everything)

### Added

- **Music example**: New `examples/music/` using musixtex, justifying `collection-music` in TeX Live profile
- **Title translations**: Added for all 26 languages (48 translation keys each, perfect parity)

### Changed

- **CI: Node.js 24**: Updated all 13 GitHub Actions to Node.js 24-compatible versions (deadline June 16, 2026)
- **CI: Local actions**: Updated `setup-python` (v5→v6.2.0), `setup-texlive/cache` (v4→v5.0.5), TeX Live version (2025→2026)
- **CI: docker/setup-buildx-action**: Removed deprecated `install: true` input
- **CI: actions/github-script**: Updated v7→v9
- **Pre-commit hooks**: Added exclude patterns for example/doc/test files in LaTeX-specific hooks (american-eg-ie, cleveref, csquotes, tilde-cite, unique-labels, consistent-spelling, ensure-labels)
- **Docker: Culmus fonts**: Separate RUN layer with apt cache mount to avoid cache invalidation
- **Dependabot**: Merged 13 stale PRs (pytest, pymupdf, python-dateutil, papersize, ipython, @types/node, @types/vscode, actions/upload-artifact, docker/build-push-action, docker/setup-buildx-action, actions/dependency-review-action, softprops/action-gh-release)

---

## v2.3.0 (2026-06-01)

### Fixed

- **Text leaks**: Eliminated `] 1 ] 1` tokens from `\provideenvironment`, glue leaks from `\ltjsetparameter{xkanjiskip}`, and Hebrew alef font warmup leak in PDF output
- **Presentation module**: Auto-load `omnilatex-presentation.sty` when `doctype=presentation` (was never loaded, causing 117 undefined environment errors)
- **setkomacolor shim**: Replaced broken `\futurelet`/`\@for` parser with clean `\@gobbletwo` no-op (KOMA removed both the writer and reader in TL2025+)
- **CJK font fallback**: Docker image now symlinks system Noto CJK fonts into TeX Live texmf-local tree; previously 3183 missing Hangul glyphs and 81 polyglossia errors
- **Hebrew font fallback**: Added Noto Sans Hebrew as third fallback; `\setsansfont` override fixes polyglossia sffamily check
- **thesis-tuhh SVG**: CI build now copies pre-converted `_svg-raw.pdf` files from `svg-inkscape/` subdirectories
- **Stale metadata**: Default title changed from institute-specific to "OmniLaTeX Example Document"
- **Missing `\endinput`**: Added to 15 example `.sty` files

### Changed

- CI: `actions/checkout` upgraded to v6 (Node.js 24 support)
- CI: `build-examples.yml` SVG path fix
- Docker: UTF-8 locale, font cache updates, `luaotfload-tool --update`
- `.env.docker`: Pinned manifest digest with correct multi-arch hash

---

See `CHANGELOG/v2.2.3.md` for previous release.
