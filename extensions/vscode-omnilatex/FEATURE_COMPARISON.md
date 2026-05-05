# LaTeX Workshop vs OmniLaTeX VS Code Extension — Feature Comparison

## Overview

| Feature | LaTeX Workshop (v10.14.1) | OmniLaTeX (v0.1.0) | Gap |
|---------|--------------------------|---------------------|-----|
| **Purpose** | General-purpose LaTeX IDE extension | Document-class-specific companion for OmniLaTeX | Complementary — not competitive |
| **Lines of code** | ~50k+ (TypeScript) | ~100 (JS) | OmniLaTeX is intentionally lightweight |
| **Dependencies** | 11 runtime deps (pdfjs-dist, mathjax-full, ws, etc.) | 0 runtime deps | OmniLaTeX is dependency-free |
| **Language registrations** | 17 languages (tex, latex, bibtex, context, doctex, pweave, rsweave, etc.) | 0 | OmniLaTeX defers to LW/standard extensions |
| **Syntax grammars** | 17 TextMate grammars | 0 | N/A — OmniLaTeX is a document class, not a language |
| **Commands** | 45+ registered commands | 4 commands | Major — OmniLaTeX needs only class-specific commands |
| **Configuration options** | ~120 settings | 0 | OmniLaTeX should add a few (see v1.0) |
| **Snippets** | 1 generic file (262 lines) + 240+ package completion files | 2 files: latex.json (1 snippet) + omnilatex.json (12 snippets) | OmniLaTeX snippets are class-specific — good |
| **Key bindings** | 30+ keybindings | 0 | Should add 2-3 keybindings for doctype/institution switching |
| **Context menus** | 2 context menu entries (editor/title) | 0 | Should add context menu for doctype switch |
| **Activity bar** | Full activity bar (Commands, Structure, Math Symbols webview) | 0 | N/A — OmniLaTeX doesn't need its own sidebar |
| **PDF viewer** | Built-in webview PDF viewer (custom editor) | 0 | N/A — defers to LaTeX Workshop |
| **Build system** | Full recipe system (latexmk, pdflatex, xelatex, lualatex, tectonic) | Stub (shows info message) | Should integrate with build.py |
| **Auto-build** | On save / on file change | 0 | N/A — defers to LaTeX Workshop |
| **SyncTeX** | Forward/backward search, configurable indicator | 0 | N/A — defers to LaTeX Workshop |
| **Completion providers** | 13 completers (see below) | 0 | Should provide OmniLaTeX class-option completions |
| **Linting** | chktex, lacheck integration + log parser + duplicate label checker | 0 | N/A — defers to LaTeX Workshop |
| **Formatting** | latexindent, tex-fmt integration | 0 | N/A — defers to LaTeX Workshop |
| **BibTeX support** | Citation browser, sort, align, format, check unused | 0 | N/A — defers to LaTeX Workshop |
| **Math rendering** | Hover preview (MathJax), math preview panel (webview) | 0 | N/A — defers to LaTeX Workshop |
| **Word count** | texcount integration | 0 | N/A — defers to LaTeX Workshop |
| **Multi-root workspace** | Full support | Not tested | Should work since OmniLaTeX is workspace-aware |
| **Status bar** | Build status, root file info | Placeholder (broken — `createLanguageStatusItem` used wrong) | Should show current doctype + institution |
| **File watchers** | Comprehensive (file change → rebuild, re-parse, refresh) | None (empty `onDidChangeActiveTextEditor`) | Should watch for doctype/institution changes |
| **Sectioning commands** | Promote/demote/select section | 0 | N/A — generic LaTeX feature |
| **Environment commands** | Navigate, select, wrap, close, toggle equation env | 0 | N/A — generic LaTeX feature |
| **Docker support** | Compile via Docker/Podman | 0 | N/A |
| **texdoc integration** | Show package documentation | 0 | Could add "Show OmniLaTeX docs" command |
| **Code actions** | Quick-fix for LaTeX diagnostics | 0 | N/A |

---

## Commands (45+ in LW, 4 in OmniLaTeX)

| Category | Command | LaTeX Workshop | OmniLaTeX | Priority |
|----------|---------|---------------|-----------|----------|
| **Doctype mgmt** | Switch Document Type | N/A (unique) | `omnilatex.switchDoctype` | **P0** |
| **Doctype mgmt** | Switch Institution | N/A (unique) | `omnilatex.switchInstitution` | **P0** |
| **Doctype mgmt** | Insert OmniLaTeX documentclass | N/A (unique) | N/A (snippet only) | **P1** |
| **Doctype mgmt** | Show available doctypes | N/A (unique) | N/A | **P2** |
| **Doctype mgmt** | Show available institutions | N/A (unique) | N/A | **P2** |
| **Build** | Build current document | `latex-workshop.build` | `omnilatex.build` | **P1** |
| **Build** | Build all examples | N/A | `omnilatex.buildAll` | **P2** |
| **Build** | Build with recipe picker | `latex-workshop.recipes` | N/A | N/A |
| **Build** | Kill compiler | `latex-workshop.kill` | N/A | N/A |
| **Build** | Clean aux files | `latex-workshop.clean` | N/A | N/A |
| **Build** | Save without building | `latex-workshop.saveWithoutBuilding` | N/A | N/A |
| **Build** | Reveal output dir | `latex-workshop.revealOutputDir` | N/A | N/A |
| **View PDF** | View in tab | `latex-workshop.tab` | N/A | N/A |
| **View PDF** | View in browser | `latex-workshop.viewInBrowser` | N/A | N/A |
| **View PDF** | View external | `latex-workshop.viewExternal` | N/A | N/A |
| **View PDF** | Refresh viewer | `latex-workshop.refresh-viewer` | N/A | N/A |
| **SyncTeX** | Forward search | `latex-workshop.synctex` | N/A | N/A |
| **Navigation** | Navigate env pair | `latex-workshop.navigate-envpair` | N/A | N/A |
| **Navigation** | Select env name/content | `latex-workshop.select-envname/content` | N/A | N/A |
| **Navigation** | Wrap env / Close env | `latex-workshop.wrap-env/close-env` | N/A | N/A |
| **Navigation** | Toggle equation env | `latex-workshop.toggle-equation-envname` | N/A | N/A |
| **Navigation** | Select section | `latex-workshop.select-section` | N/A | N/A |
| **Sectioning** | Promote/Demote section | `latex-workshop.promote/demote-sectioning` | N/A | N/A |
| **Citation** | Citation browser | `latex-workshop.citation` | N/A | N/A |
| **Citation** | Insert tex root | `latex-workshop.addtexroot` | N/A | N/A |
| **BibTeX** | Sort/Align/AlignSort | `latex-workshop.bibsort/bibalign/bibalignsort` | N/A | N/A |
| **BibTeX** | Check unused citations | `latex-workshop.checkcitations` | N/A | N/A |
| **Math** | Toggle math preview panel | `latex-workshop.toggleMathPreviewPanel` | N/A | N/A |
| **Math** | Open/Close math panel | `latex-workshop.open/closeMathPreviewPanel` | N/A | N/A |
| **Surround** | Surround with LaTeX cmd | `latex-workshop.surround` | N/A | N/A |
| **Formatting** | Toggle textbf/textit/etc (17 commands) | `latex-workshop.shortcut.*` | N/A | N/A |
| **Info** | Word count | `latex-workshop.wordcount` | N/A | N/A |
| **Info** | Compiler log | `latex-workshop.compilerlog` | N/A | N/A |
| **Info** | Extension log | `latex-workshop.log` | N/A | N/A |
| **Info** | Actions (pick from all) | `latex-workshop.actions` | N/A | N/A |
| **Info** | texdoc | `latex-workshop.texdoc` | N/A | N/A |
| **Info** | texdoc (used packages) | `latex-workshop.texdocUsepackages` | N/A | N/A |
| **Info** | Change/Reset hostname | `latex-workshop.change/resetHostName` | N/A | N/A |
| **Info** | Host port (Live Share) | `latex-workshop.hostPort` | N/A | N/A |
| **DevTools** | Parse log/tex/bib, strip text | `latex-workshop-dev.*` | N/A | N/A |
| **OmniLaTeX-specific** | Show OmniLaTeX docs | N/A | N/A | **P2** |
| **OmniLaTeX-specific** | Validate doctype options | N/A | N/A | **P2** |

---

## Configuration Options (120+ in LW, 0 in OmniLaTeX)

| Option | LaTeX Workshop | OmniLaTeX | Priority |
|--------|---------------|-----------|----------|
| Build command/path | `latex-workshop.latex.tools` (12 default tools) | N/A | N/A |
| Build recipes | `latex-workshop.latex.recipes` (9 default recipes) | N/A | N/A |
| Build recipe default | `latex-workshop.latex.recipe.default` | N/A | N/A |
| External build command | `latex-workshop.latex.external.build.command` | N/A | N/A |
| Auto build on save | `latex-workshop.latex.autoBuild.run` | N/A | N/A |
| Auto build interval | `latex-workshop.latex.autoBuild.interval` | N/A | N/A |
| Auto clean | `latex-workshop.latex.autoClean.run` | N/A | N/A |
| Output dir | `latex-workshop.latex.outDir` | N/A | N/A |
| Aux dir | `latex-workshop.latex.auxDir` | N/A | N/A |
| Root file indicator | `latex-workshop.latex.rootFile.indicator` | N/A | N/A |
| **OmniLaTeX: build.py path** | N/A | N/A | **P1** |
| **OmniLaTeX: auto-detect doctype** | N/A | N/A | **P1** |
| **OmniLaTeX: status bar doctype** | N/A | N/A | **P1** |
| **OmniLaTeX: language options** | N/A | N/A | **P2** |
| PDF viewer type | `latex-workshop.view.pdf.viewer` (tab/browser/external) | N/A | N/A |
| PDF zoom/trim/scroll | `latex-workshop.view.pdf.zoom/trim/scrollMode` | N/A | N/A |
| PDF invert/dark mode | `latex-workshop.view.pdf.invert*` (7 settings) | N/A | N/A |
| PDF sidebar | `latex-workshop.view.pdf.sidebar.*` | N/A | N/A |
| SyncTeX path | `latex-workshop.synctex.path` | N/A | N/A |
| SyncTeX indicator | `latex-workshop.synctex.indicator` | N/A | N/A |
| Linting (chktex/lacheck) | `latex-workshop.linting.*` (10 settings) | N/A | N/A |
| Formatting | `latex-workshop.formatting.*` (6 settings) | N/A | N/A |
| Fix quotes/math | `latex-workshop.format.fixQuotes/Math.enabled` | N/A | N/A |
| Completion triggers | `latex-workshop.intellisense.triggers.latex` | N/A | N/A |
| Citation completion | `latex-workshop.intellisense.citation.*` (5 settings) | N/A | N/A |
| Package completion | `latex-workshop.intellisense.package.*` (6 settings) | N/A | N/A |
| UniMath symbols | `latex-workshop.intellisense.unimathsymbols.enabled` | N/A | N/A |
| Sub/superscript | `latex-workshop.intellisense.subsuperscript.enabled` | N/A | N/A |
| Hover preview | `latex-workshop.hover.preview.*` (9 settings) | N/A | N/A |
| Hover ref/citation/cmd | `latex-workshop.hover.ref/citation/command.enabled` | N/A | N/A |
| BibTeX format | `latex-workshop.bibtex-format.*` (8 settings) | N/A | N/A |
| BibTeX fields | `latex-workshop.bibtex-fields.*` (3 settings) | N/A | N/A |
| Docker | `latex-workshop.docker.*` (3 settings) | N/A | N/A |
| Badbox display | `latex-workshop.message.badbox.show` | N/A | N/A |
| Message filters | `latex-workshop.message.*.exclude` (4 settings) | N/A | N/A |
| Context menu | `latex-workshop.showContextMenu` | N/A | N/A |
| Enter key → \item | `latex-workshop.bind.enter.key` | N/A | N/A |
| Alt keymap | `latex-workshop.bind.altKeymap.enabled` | N/A | N/A |
| Outline sections | `latex-workshop.view.outline.sections` | N/A | N/A |
| Outline floats | `latex-workshop.view.outline.floats.*` (3 settings) | N/A | N/A |
| Smart selection | `latex-workshop.selection.smart.latex.enabled` | N/A | N/A |
| texdoc | `latex-workshop.texdoc.path/args` | N/A | N/A |
| texcount | `latex-workshop.texcount.*` (3 settings) | N/A | N/A |
| Codespaces | `latex-workshop.codespaces.portforwarding.openDelay` | N/A | N/A |

---

## Completion Providers (13 in LW, 0 in OmniLaTeX)

| Provider | LaTeX Workshop | OmniLaTeX | Priority |
|----------|---------------|-----------|----------|
| Commands (879 entries) | `\command` completions from `data/commands.json` | N/A | N/A |
| Environments (62 entries) | `\begin{env}` completions | N/A | N/A |
| Package-specific (240+ files) | Commands/envs from `\usepackage{}` | N/A | N/A |
| **Class options** | Basic class-option completion from `data/classnames.json` | N/A | **P0** — should provide `doctype=`, `institution=`, `language=`, etc. |
| **Doctype values** | N/A | N/A | **P0** — should provide 25 doctype values after `doctype=` |
| **Institution values** | N/A | N/A | **P0** — should provide 14 institution values after `institution=` |
| **Language values** | N/A | N/A | **P1** — should provide language options after `language=` |
| **Color-mode values** | N/A | N/A | **P2** — should provide `dark`, `light`, `auto` |
| At-suggestions (333 entries) | `@`-triggered snippet suggestions | N/A | N/A |
| Citations | BibTeX/biblatex citation browser | N/A | N/A |
| References | `\ref{}`, `\label{}` completion | N/A | N/A |
| Glossary entries | `\gls{}` completion | N/A | N/A |
| File/input | `\input{}`, `\includegraphics{}` path completion | N/A | N/A |
| Sub/superscript | Auto-complete `_`, `^` from project | N/A | N/A |
| Macro | User-defined `\newcommand` completion | N/A | N/A |
| BibTeX entries | `@article`, `@book`, etc. with fields | N/A | N/A |
| Includegraphics preview | Image thumbnail in completion | N/A | N/A |
| Close environment | Suggests closing `\end{env}` | N/A | N/A |
| Argument hints | Shows parameter hints for commands | N/A | N/A |

---

## Key Bindings (30+ in LW, 0 in OmniLaTeX)

| Action | LaTeX Workshop | OmniLaTeX | Priority |
|--------|---------------|-----------|----------|
| Build | `Ctrl+Alt+B` | N/A | N/A |
| Clean | `Ctrl+Alt+C` | N/A | N/A |
| View PDF | `Ctrl+Alt+V` | N/A | N/A |
| SyncTeX | `Ctrl+Alt+J` | N/A | N/A |
| Math preview panel | `Ctrl+Alt+M` | N/A | N/A |
| Activity bar | `Ctrl+Alt+X` | N/A | N/A |
| Promote section | `Ctrl+Alt+[` | N/A | N/A |
| Demote section | `Ctrl+Alt+]` | N/A | N/A |
| Item | `Ctrl+L Ctrl+Enter` | N/A | N/A |
| textbf | `Ctrl+L Ctrl+B` | N/A | N/A |
| textit | `Ctrl+L Ctrl+I` | N/A | N/A |
| emph | `Ctrl+L Ctrl+E` | N/A | N/A |
| texttt | `Ctrl+L Ctrl+T` | N/A | N/A |
| textsc | `Ctrl+L Ctrl+C` | N/A | N/A |
| Surround | `Ctrl+L Ctrl+W` | N/A | N/A |
| Expand selection | `Ctrl+L Ctrl+L` | N/A | N/A |
| **Switch doctype** | N/A | N/A | **P1** — e.g. `Ctrl+Alt+D` |
| **Switch institution** | N/A | N/A | **P1** — e.g. `Ctrl+Alt+I` |
| Enter → \item | `Enter` (configurable) | N/A | N/A |
| Alt+Enter → \item | `Alt+Enter` (configurable) | N/A | N/A |

---

## Snippets

| Snippet File | LaTeX Workshop | OmniLaTeX |
|-------------|---------------|-----------|
| `latex-snippet.json` | 262 lines of generic LaTeX snippets (envs, formatting, math, etc.) | N/A |
| `omnilatex.json` | N/A | 12 OmniLaTeX-specific snippets |
| `latex.json` | N/A | 1 OmniLaTeX documentclass snippet |
| Package-specific (240 files) | 240+ `.json` files with per-package commands/envs | N/A |
| OmniLaTeX `.cwl` | N/A | 127-line CWL file (not yet wired to extension) |

### OmniLaTeX snippet coverage analysis

| Category | LW has | OmniLaTeX has | Gap |
|----------|--------|--------------|-----|
| Document skeleton | Generic | `omnilatex`, `omnilatex-class` | Covered |
| Title/metadata | Generic | `omnilatex-title` | Covered |
| Abstract | Generic | `omnilatex-abstract` | Covered |
| Sections | Generic | `section`, `subsection` | Covered |
| Figure | Generic | `figure` | Covered |
| Table | Generic | `table` | Covered |
| Equation | Generic | `math` | Covered |
| Code listing | Generic | `code` (minted) | Covered |
| Bibliography | Generic | `bibliography` | Covered |
| Todo note | N/A | `todo` | Unique to OmniLaTeX |
| Censor | N/A | `censor` | Unique to OmniLaTeX |
| **Missing OmniLaTeX snippets** | — | — | |
| Algorithm/pseudocode | — | Missing | **P1** |
| Theorem/proof | — | Missing | **P1** |
| Appendix | — | Missing | **P2** |
| Glossary/acronym | — | Missing | **P2** |
| TikZ figure | — | Missing | **P2** |
| Two-column layout | — | Missing | **P3** |
| Header/footer (KOMA) | — | Missing | **P3** |
| Listing with caption | — | Missing (has generic `code`) | **P3** |

---

## Views & Panels

| View | LaTeX Workshop | OmniLaTeX |
|------|---------------|-----------|
| Activity bar | Full sidebar with 3 views: Commands, Structure, Math Symbols | N/A |
| Commands tree | All LW commands organized by category | N/A |
| Structure/Outline | Section hierarchy, floats, labels (TreeDataProvider) | N/A |
| Math Symbols | Webview panel with searchable math symbols | N/A |
| PDF Viewer | Custom editor (`latex-workshop-pdf-hook`) with full PDF rendering | N/A |
| Math Preview Panel | Webview panel rendering math at cursor | N/A |
| Status bar | Build status, root file, language ID | Implemented (language status item) |

---

## Event Handlers

| Handler | LaTeX Workshop | OmniLaTeX |
|---------|---------------|-----------|
| `onDidSaveTextDocument` | Auto-build, lint, word count | None |
| `onDidChangeActiveTextEditor` | Root file detection, outline refresh, status bar | Empty handler (comment only) |
| `onDidChangeTextDocument` | Cache refresh, aggressive intellisense update, lint on type | None |
| `onDidChangeTextEditorSelection` | Outline reveal/follow | None |
| `onDidChangeConfiguration` | Log config changes, re-register triggers | None |
| File watcher | `latex-workshop.latex.watch.delay` — monitors file changes for rebuild | None |

---

## Build System Architecture

### LaTeX Workshop
- **Recipe system**: User-defined recipes combining tools in sequence
- **Default tools**: latexmk, lualatexmk, xelatexmk, pdflatex, bibtex, tectonic
- **Magic comments**: `% !TeX program`, `% !BIB program`
- **External build**: Custom command (Makefile, scripts)
- **Build queue**: Sequential compilation with cancellation support
- **Auto-build**: On save or on file change
- **Clean**: Via latexmk or glob patterns
- **Output/aux dirs**: Configurable with placeholders

### OmniLaTeX
- **Current state**: Stub that shows `showInformationMessage`
- **Target**: Should invoke `python3 build.py build-example <name>` or `python3 build.py build-all`
- **Unique need**: Build example documents by name (LW has no concept of "example builds")

---

## SyncTeX Architecture

### LaTeX Workshop
- Forward search: Editor cursor → PDF position (internal viewer + external via `synctex view`)
- Reverse search: PDF click → editor line (internal viewer ctrl-click/double-click)
- Configurable indicator (none/circle/rectangle)
- Auto-sync after build (configurable)

### OmniLaTeX
- N/A — fully defers to LaTeX Workshop

---

## Multi-root Workspace

| Feature | LaTeX Workshop | OmniLaTeX |
|---------|---------------|-----------|
| Per-workspace config | Yes (`scope: "resource"`) | No config yet |
| Multiple root files | Detected per workspace folder | N/A |
| Subfile support | `\documentclass[main.tex]{subfile}` | N/A |

---

## Extension Dependencies

### LaTeX Workshop
- **Runtime**: cross-spawn, glob, iconv-lite, latex-utensils, mathjax-full, micromatch, pdfjs-dist, tmp, vsls, workerpool, ws
- **Dev**: TypeScript, ESLint, Mocha, unified-latex, esbuild, vscode-test-electron
- **Extension conflicts**: Checks for `tomoki1207.pdf` (vscode-pdf)

### OmniLaTeX
- **Runtime**: None
- **Dev**: @types/node, @types/vscode, typescript
- **Should depend on**: LaTeX Workshop (soft dependency via `extensionDependencies`)

---

## Code Formatting

| Feature | LaTeX Workshop | OmniLaTeX |
|---------|---------------|-----------|
| LaTeX formatting | latexindent, tex-fmt | N/A |
| BibTeX formatting | Built-in sort/align/format | N/A |
| Fix quotes | `"` → ` ``...''` | N/A |
| Fix math delimiters | `$...$` → `\(...\)` | N/A |
| Document formatting provider | Registered for tex/latex/cls/sty/expl3 | N/A |

---

## BibTeX / Biblatex Support

| Feature | LaTeX Workshop | OmniLaTeX |
|---------|---------------|-----------|
| Citation completion | Inline + browser modes | N/A |
| Citation format | author/title/journal/year | N/A |
| BibTeX parsing | Full AST parser (`bibtex.ts`) | N/A |
| BibTeX formatting | Sort, align, deduplicate, field ordering | N/A |
| Unused citation check | Via `checkcites` command | N/A |
| Max file size | 5 MB configurable | N/A |

---

## Math Rendering

| Feature | LaTeX Workshop | OmniLaTeX |
|---------|---------------|-----------|
| Hover preview | MathJax in tooltip, 20-line limit, configurable scale | N/A |
| Math preview panel | Persistent webview panel | N/A |
| Custom commands | Parses `\newcommand` from file + external file | N/A |
| Cursor in preview | Configurable cursor symbol/color | N/A |
| MathJax extensions | 18 loadable extensions | N/A |

---

## Priority Legend

- **P0**: Must have for v1.0 (basic usability)
- **P1**: Should have for v1.0 (important UX)
- **P2**: Nice to have for v1.0
- **P3**: Can defer to v2.0
- **N/A**: Not applicable to OmniLaTeX (e.g., we don't need our own PDF viewer, linter, formatter — LaTeX Workshop handles these)

---

## Recommended v1.0 Feature Set for OmniLaTeX Extension

### P0 — Must Have

1. **Doctype switcher** (command: `omnilatex.switchDoctype`)
   - QuickPick with 25 doctypes, grouped by category (academic, business, personal)
   - Parse `\documentclass[doctype=...]{omnilatex}` and replace
   - Validate doctype exists before switching
   - Show current doctype in status bar

2. **Institution switcher** (command: `omnilatex.switchInstitution`)
   - QuickPick with 14 institutions
   - Parse and replace `institution=...` option
   - Show current institution in status bar

3. **Class-option completion provider**
   - After `\documentclass[` provide: `doctype=`, `institution=`, `language=`, `color-mode=`, `link-style=`, `code-style=`
   - After `doctype=` provide 25 valid doctype values
   - After `institution=` provide 14 valid institution values
   - After `language=` provide language options (read from OmniLaTeX docs)

4. **Working status bar item**
   - Show `OmniLaTeX: thesis | cambridge` (or similar)
   - Click to trigger doctype switcher

5. **Wire up `omnilatex.json` snippets** (currently registered for `latex` language but the file isn't referenced in package.json)

### P1 — Should Have

6. **Build integration** (commands: `omnilatex.build`, `omnilatex.buildAll`)
   - Actually invoke `python3 build.py build-example <name>` via `vscode.tasks` or `child_process`
   - Detect OmniLaTeX workspace root (look for `omnilatex.cls` or `build.py`)
   - QuickPick of example names for `omnilatex.build`

7. **Key bindings**
   - `Ctrl+Alt+D` → switch doctype
   - `Ctrl+Alt+I` → switch institution

8. **Context menu**
   - Right-click in `.tex` file → "OmniLaTeX: Switch Document Type" / "Switch Institution"

9. **Configuration options**
   - `omnilatex.build.pyPath`: Path to build.py (default: auto-detect)
   - `omnilatex.statusBar.show`: Show/hide status bar item (default: true)

10. **Additional OmniLaTeX-specific snippets**
    - Algorithm/pseudocode block
    - Theorem/proof/definition environment
    - Proper OmniLaTeX `\printbibliography` with OmniLaTeX options

11. **OmniLaTeX documentclass snippet** — the existing `omnilatex-class` snippet in `latex.json` is not wired. Register `omnilatex.json` properly and ensure both files are loaded.

### P2 — Nice to Have

12. **Language option completion** — provide language values after `language=`
13. **Validate documentclass options** — warn if invalid `doctype=` or `institution=` value
14. **"Show OmniLaTeX Docs" command** — open local or web documentation
15. **Document outline integration** — parse OmniLaTeX-specific metadata for outline
16. **New file template** — "New OmniLaTeX Document" command that creates a full `.tex` file
17. **OmniLaTeX-specific hover** — hover over `doctype=thesis` shows description of thesis doctype

---

## Recommended v2.0 Feature Set

1. **OmniLaTeX webview panel** — gallery of doctype previews (show rendered examples)
2. **Institution logo preview** — show institution crest/coat of arms
3. **Doctype-specific snippets** — context-aware snippets that change based on current doctype (e.g., thesis-specific snippets like `\chapter`, dissertation-specific front matter)
4. **Full CWL integration** — use `omnilatex.cwl` (127 commands) for completion
5. **OmniLaTeX option validation diagnostic** — underline invalid options with error squiggles
6. **Project template generator** — "New OmniLaTeX Project" with doctype/institution picker, generates folder structure
7. **Overleaf integration** — export OmniLaTeX project for Overleaf compatibility
8. **Color-mode switcher** — toggle dark/light/auto for document class
9. **Build configuration UI** — webview panel to configure OmniLaTeX build options
10. **Multi-file doctype detection** — detect doctype across `\input`/`\include` chain
11. **OmniLaTeX language server** — optional LSP for deep class-option validation
12. **Git integration** — auto-detect `doctype` from branch name or repo config
