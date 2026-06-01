# Changelog

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
