# Change Log

All notable changes to the "OmniLaTeX" extension will be documented in this file.

## [2.0.0] - 2026-05-20

### Added

- IntelliSense completion for all `\documentclass[...]{omnilatex}` options: doctype, institution, language, color-mode, link-style, code-style
- Doctype picker with categorized quick-pick (Academic, Business, Personal) and descriptions for all 26 document types
- Institution switcher supporting 16 institutions (Cambridge, CMU, EPFL, ETH, Harvard, Imperial, MIT, Oxford, Princeton, Stanford, TU Delft, TUHH, TUM, Yale, generic, none)
- Build Example and Build All commands via `build.py` integration
- LaTeX log file diagnostic provider — parses `.log` files for errors and warnings on save/open
- Language status bar item showing current doctype and institution
- Build on save via `latexmk -lualatex` (opt-in via `omnilatex.buildOnSave`)
- Snippet collections for standard LaTeX and OmniLaTeX-specific environments
- Context menu entries for Switch Document Type and Switch Institution
- Configurable settings: status bar visibility, build-on-save, build engine, output directory, completion, and diagnostics
- Keybindings: `Ctrl+Shift+B` (build), `Ctrl+Shift+T` (switch doctype), `Ctrl+Alt+I` (switch institution)
- Marketplace-ready packaging with icon, gallery banner, and `.vscodeignore`

### Changed

- Bumped version to 2.0.0
- Updated keybindings from `Ctrl+Alt` to `Ctrl+Shift` scheme for build and doctype commands
- Enhanced `package.json` with full marketplace metadata (repository, license, homepage, categories, keywords)

## [0.1.0] - 2026-04-26

### Added

- Initial release
- Doctype picker with all 16 OmniLaTeX document types
- Institution switcher (scans `config/institutions/`)
- Language picker with 12 supported languages
- Build commands via integrated terminal (`build.py`)
- Run Diagnostics command (`build.py doctor`)
- Create New Project command (`build.py init`)
- Status bar showing current doctype, language, and institution
- LaTeX snippets for OmniLaTeX documents, titles, abstracts, environments, and more
- Auto-detection of OmniLaTeX projects via `omnilatex.cls`
- Welcome message on first activation
