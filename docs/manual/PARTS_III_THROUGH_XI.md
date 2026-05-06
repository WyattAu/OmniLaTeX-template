# Parts III-XI: Remaining Chapter Plans

---

## Part III: Typography & Content

### Chapter 30: Fonts
1. **Font System Architecture** — fontspec, unicode-math, lualatex-math
2. **Default Font Stack** — Libertinus Serif/Sans/Math, Monaspace Neon, Atkinson Hyperlegible Next
3. **Setting Fonts** — `\setMainFont`, `\setSansFont`, `\setMonoFont`, `\setMathFont`
4. **Font Feature Tables** — OpenType features for each font family
5. **Emoji & Icon Fonts** — fontawesome5, `\faIcon{name}`
6. **CJK Fonts** — luatexja-fontspec, Noto CJK families (SC/TC/JP/KR)
7. **RTL Fonts** — Arabic/Hebrew/Persian font fallback chains
8. **Unit Number Font** — `\unitnumberfont` for siunitx
9. **Font Troubleshooting** — Missing glyphs, font substitution warnings

### Chapter 31: Text Formatting
1. **Microtype** — Protrusion, expansion, tracking
2. **Extdash** — `fast\-/paced` hyphenation shortcuts
3. **csquotes** — `\enquote`, nested quotes, language-aware
4. **ragged2e** — `\RaggedRight`, `\RaggedLeft`
5. **Blind Text** — `\Blindtext`, `\Blinddocument`
6. **Line Spacing** — setspaceenhanced, `\linespread`, `\parindent`
7. **Paragraph Spacing** — KOMA parskip options

### Chapter 32: Mathematics
1. **amsmath + unicode-math** — Equation environments, alignment
2. **Auto-Scaling Delimiters** — `\parens`, `\brackets`, `\braces`
3. **Equation Punctuation** — `\eqend`, `\eqcomma`, `\coloneq`
4. **Statistical Macros** — `\mean{}`, `\logmean{}`, `\abs{}`
5. **Number Formatting** — `\circlednum{n}`, `\symbolplaceholder`
6. **Custom Operators** — `\DeclareMathOperator`, `\grad`, `\const`
7. **Quoted Text in Math** — `\qq{text}`
8. **Display Equations** — `empheq`, aligned environments

### Chapter 33: Physical Mathematics
1. **siunitx Setup** — Locale-aware, per-mode=fraction
2. **Core Commands** — `\num`, `\unit`, `\qty`, `\qtyrange`
3. **Custom SI Units** — `\volpercent`, `\watthour`, `\annum`, `\atmosphere`, `\partspermillion`, `\bar`, `\relhumidity`
4. **Custom SI Qualifiers** — `\dryair`, `\water`, `\thermal`
5. **S-Column in Tables** — siunitx column type for aligned numbers
6. **Chemistry** — chemmacros, `\chcpd`, `reaction`, `reactionsgather`, `\chemamount`
7. **Fractions** — xfrac, nicefrac

### Chapter 34: Derivatives & Vector Calculus
1. **Derivative Macros** — `\deriv[deg]{f}{x}`, `\deriv*{f}{x}` (partial), `\fracderiv{f}{x}{t}`, `\timederiv{f}{t}`, `\posderiv{f}{x}`
2. **Vector Macros** — `\vect{v}`, `\nablaoperator[deg]`
3. **Physical Macros** — `\flow{}`, `\difference{}`, `\heatexentry{}`, `\heatexexit{}`, `\temperaturepair{min}{max}`
4. **Convention Tables** — Full reference of all math macros with LaTeX source and rendered output

### Chapter 35: CJK Mathematics
1. **CJK Math Fonts** — luatexja math support
2. **Ruby Annotations** — `\ruby{base}{ruby}`, `\furigana`, `\pinyin`
3. **Vertical Math** — Vertical writing mode for equations
4. **CJK-Latin Spacing** — `\cjklatinspacing`, `\setCJKLatinSpacing`

---

## Part IV: Language & Internationalization

### Chapter 40: I18N System
1. **polyglossia Setup** — Primary and secondary languages
2. **Translation System** — `translations` package, `\GetTranslation`, `\RenewTranslation`
3. **Language Fallback Chain** — English as default, Lean proof reference
4. **Dynamic Switching** — `\begin{english}...\end{english}` inline
5. **Complete Key Table** — All 47 translation keys explained

### Chapter 41: Multilingual Documents
1. **Multi-Language Example** — `examples/multi-language/` walkthrough
2. **Cross-Language References** — cref across language boundaries
3. **Bibliography in Multiple Languages** — biblatex language support

### Chapter 42: RTL Scripts
1. **Arabic** — `\setArabicFont`, Arabic-Indic digits, bidi layout
2. **Hebrew** — `\setHebrewFont`, Hebrew font fallback
3. **Persian** — Persian font fallback, RTL title page
4. **RTL Title Page** — Automatic font override for Arabic/Hebrew/Persian
5. **Inline Direction** — `\LTRinline`, `\RTLinline`
6. **Example Walkthroughs** — rtl-arabic, rtl-hebrew examples

### Chapter 43: CJK Scripts
1. **Chinese (Simplified/Traditional)** — luatexja, Noto CJK SC/TC, `\ruby`
2. **Japanese** — Noto CJK JP, furigana, vertical text
3. **Korean** — Noto CJK KR, Hangul support
4. **Auto-Detection** — `\setCJKScript{sc|tc|jp|kr}`
5. **Vertical Writing** — `vertical` env, `\verticaltext`
6. **CJK-Latin Spacing** — `\cjklatinspacing`
7. **Example Walkthroughs** — cjk-chinese, cjk-japanese, cjk-korean

### Chapter 44: Translation Key Reference
- **Complete table**: All 47 keys × 18 languages (846 translations)
- **Key Descriptions**: What each key means, where it's used
- **Adding New Keys**: `\DeclareTranslation` workflow

---

## Part V: Layout & Structure

### Chapter 50: Page Layout
1. **KOMA Page Geometry** — `\areaset`, DIV, BCOR
2. **Custom Margins** — `\setCustomMargins{L}{R}{T}{B}`
3. **Two-Side Layout** — `twoside` option, header/footer differences
4. **Headers & Footers** — scrlayer-scrpage, automark, `\headerrule`
5. **Landscape Pages** — `landscape` env, `\pdflandscape`
6. **A5 Format** — `a5` class option
7. **Page Numbering** — `\frontmatter` (alpha), `\mainmatter` (arabic), `\backmatter`

### Chapter 51: Sectioning
1. **KOMA Section Hierarchy** — `\part`, `\chapter`, `\section`, `\subsection`, `\subsubsection`, `\paragraph`, `\subparagraph`
2. **Chapter Prefix** — Scaled 4.5x number formatting
3. **Table of Contents** — `\tableofcontents`, depth control
4. **List of Figures/Tables** — `\listoffigures`, `\listoftables`, `\listofexamples`, `\listoflistings`
5. **PDF Bookmarks** — `\pdfbookmark`, bold chapter bookmarks
6. **Unnumbered Chapters** — `\addchap`, `\chapter*`

### Chapter 52: Title Pages
1. **4 Built-in Styles:**
   - `titlestyle=book` — Vertical rule, small caps author
   - `titlestyle=thesis` — Vertical rule, examiners table
   - `titlestyle=simple` — Default KOMA title
   - `titlestyle=TUHH` — TUHH-specific branded title
2. **Custom Title Pages** — How institutions define `\DefineXxxTitleStyle`
3. **Title Page Metadata** — `\title`, `\author`, `\date`, `\publishers`

### Chapter 53: Institutions
1. **16 Institution Configs** — Table with colors, logos, title pages
2. **Creating Your Own** — Step-by-step: create directory, define .sty, add logo, set colors
3. **Logo Management** — SVG logos, `\includesvg`, `\DeclareTranslation{LogoXxx}`
4. **Color Branding** — `\setkomacolor`, primary/secondary colors

---

## Part VI: Figures, Tables & Floats

### Chapter 60: Floats
1. **Float Placement** — KOMA float placement, `floatrow`
2. **Continued Floats** — `\ContinuedFloat` for multi-page figures
3. **Float Footnotes** — `\omnlFloatFootmark`, `\omnlFloatFoottext`
4. **Side Captions** — `\captionof` with minipage layout
5. **Key-Value Float Interface** — `\omnlFigure[caption=..., label=...]`
6. **Float Grid** — `omnlFloatRow[n-cols]` for multi-column float layouts

### Chapter 61: Figures
1. **Images** — `\includegraphics`, path management, `\svgpath`
2. **SVG Graphics** — `\includesvg`, Inkscape integration, `--shell-escape`
3. **TikZ Basics** — Libraries loaded, coordinate systems, basic shapes
4. **Subfigures** — `subfigure` environment, side-by-side figures
5. **Text Over Images** — `\ctrw{text}` (white contour), TikZ overlays
6. **Debugging SVG** — `\debugtikzsvg`

### Chapter 62: Tables
1. **booktabs** — `\toprule`, `\midrule`, `\bottomrule`, no vertical lines
2. **tabularray** — `longtblr`, variable-width columns, siunitx integration
3. **siunitx S-Columns** — Number alignment in tables
4. **Multi-Column Tables** — `\multicolumn`, `\cmidrule`
5. **Rotated Cells** — `\multirotatecell{rows}{text}`
6. **Table Footnotes** — `\TblrNote`, `\TblrRemark`

### Chapter 63: pgfplots
1. **Line & Scatter Plots** — `regularplot` style, custom styles
2. **Bar Charts** — `ybar`, stacked bars
3. **Contour Plots** — `contour gnuplot`, custom functions
4. **Date Plots** — `dateplot` library, ISO 8601
5. **CSV Import** — `\pgfplotstableread`, column selection, filtering
6. **Custom Styles** — `tuftelike`, `arrowplot`, `plainplot`
7. **Color Maps** — `viridis`, `RdYlBu3`, `Set2`
8. **Dual Axes** — Secondary y-axis
9. **Groupplots** — Side-by-side plots with shared axes

### Chapter 64: TikZ Engineering
1. **Flowcharts** — `startstop`, `io`, `process`, `decision` node styles
2. **Circuit Diagrams** — `circuits.ee.IEC`, resistors, batteries, contacts
3. **3D Drawings** — `tdplot`, canvas planes, flow arrows
4. **Custom Thermodynamic Shapes** — valve, pump, compressor, heat exchanger, radiator, boiler, sensor, equalizing tank (with all anchors)
5. **Pipe Networks** — `pipe` node styles, three-way/four-way valves
6. **Control Systems** — Simulink-style blocks, feedback loops, saturation
7. **Annotation Arrows** — `\annotationarrow`, `\wall`, `\flowarrow`

---

## Part VII: References & Glossaries

### Chapter 70: Bibliography
1. **biblatex + biber Setup** — `ext-authoryear`, `introcite=label`, `backref`
2. **Citation Commands** — `\cite`, `\textcite`, `\parencite`, `\footcite`, `\fullcite`
3. **Citation Groups** — `\cites`, `\parencites`, `\textcites`
4. **Per-Chapter Bibliography** — `refsection` vs `refsegment`
5. **Bib File Management** — `\addbibresource`, bib2gls integration
6. **"Further Reading" Section** — `\nocite{*}`, `category=cited/notcategory=cited`

### Chapter 71: Citation Styles
1. **9 Preconfigured Styles:**
   - `ieee`, `acm`, `apa`, `chicago`, `nature`, `science`, `harvard`, `vancouver`, `mla`
2. **`\citationstyle{name}`** — Switching styles per document
3. **Example Comparison** — Same bibliography rendered in all 9 styles

### Chapter 72: Glossaries
1. **glossaries-extra Setup** — nomain, abbreviations, symbols, index, numbers
2. **Custom Glossary Types** — Symbols with units, constants with values, subscripts
3. **Shortcut Commands** — `\sym{}`, `\sub{}`, `\name{}`, `\cons{}`, `\idx{}`, `\abb{}`, `\num{}`
4. **Custom Fields** — `unit`, `specific`, `firstname`, `value`, `international-symbol`
5. **Printing** — `\printunsrtglossary` with custom styles
6. **Subscripts Glossary** — Multi-column subscripts list
7. **Symbol Markers** — `\specificsymbolmark`, `\alternativesymbolmark`
8. **Index** — `\printunsrtindex` with `bookindex` style

### Chapter 73: Cross References
1. **cleveref** — `\cref`, `\Cref`, `\crefname`, `\lcnamecref`, `\cpageref`
2. **Custom crefnames** — For `example`, `code`, `listing` environments
3. **PDF Bookmarks** — hyperref setup, bold chapter bookmarks
4. **Equation References** — `\creflabelformat{equation}{#2#1#3}`

---

## Part VIII: Code & Listings

### Chapter 80: Code Listings
1. **minted Setup** — `manni` style, `leftline`, line numbers, cache
2. **Inline Code** — `\mintinline{python}{...}`
3. **Block Listings** — `\begin{minted}{python}...\end{minted}`
4. **Long Listings** — `longlisting` env, `\inputminted{lua}{file.lua}`
5. **Line Highlighting** — `highlightlines`, `\phstring`, `\phnum`, `\phother`, `\phnote`
6. **Simulink Icons** — `\mtlbsmlkicon{name}`
7. **Language Support** — Python, MATLAB, Lua, Modelica, C/C++, etc.
8. **Accessible Line Numbers** — `\emptyaccsupp`

### Chapter 81: Lua Scripting
1. **Lua in LaTeX** — `\directlua`, `lua`, `\luasetup`
2. **Git Metadata** — `\GitRefName`, `\GitShortSHA`, `\GitLongSHA`, `\BuildDate`
3. **Conditional Compilation** — `BUILD_MODE` env var, `\ifomnilatex@...`
4. **Custom Lua Commands** — Creating new Lua-driven macros
5. **Example:** `lua-showcase` walkthrough

---

## Part IX: Advanced Features

### Chapter 90: Color Themes
1. **7 Palettes** — default, midnight, forest, rose, monochrome, monochrome-dark, sepia
2. **`\usetheme{name}`** — Loading a palette
3. **Dark/Light Mode** — `\darkmode`, `\lightmode`
4. **Per-Slot Overrides** — `\setthemecolor{slot}{color}`
5. **Conditional Theming** — `\ifthememode{dark}{yes}{no}`
6. **tcolorbox Integration** — Themed block environments

### Chapter 91: Boxes & Environments
1. **Example Box** — `example` tcolorbox (auto-counter, LoE, breakable)
2. **Key Concept Box** — `keyconceptbox` (handouts)
3. **Callout Box** — `\callout{title}{text}` (white papers)
4. **Alert/Definition/Note Blocks** — Presentation block envs
5. **Git Verification Box** — `\GitVerificationBox`

### Chapter 92: Censoring
1. **`\censor{text}`** — Black-bar censoring
2. **`\StopCensoring`** — End censoring in document
3. **`\todo{text}`** — TODO notes (conditional on `todonotes` option)
4. **`\censorbox{...}`** — Censored boxes
5. **Blind Text** — `\Blindtext` for placeholder content

### Chapter 93: PDF Accessibility
1. **PDF/UA-1** — `tagpdf` activation
2. **Alt Text** — `\alttext{desc}` for figures, `\tikzalttext{desc}` for TikZ
3. **Accessible Links** — `\accessiblelink{text}{url}{sr-desc}`
4. **Heading Validation** — `\validatstructure`
5. **Contrast Checking** — `\checkcontrast{fg}{bg}`
6. **Reading Order** — `\readingorder{n}`
7. **Language Tags** — `\langtag{lang}{text}`
8. **Example:** `accessibility-test` walkthrough

### Chapter 94: Presentations
(See Chapter 25.1 — same content, different context)

### Chapter 95: Posters
(See Chapter 25.2 — same content, different context)

---

## Part X: Build & Automation

### Chapter 100: Build Modes
1. **`dev` Mode** — 3 latexmk passes, full bib, shell-escape
2. **`prod` Mode** — Full validation, all packages
3. **`ultra` Mode** — 2 passes, no bib (fast iteration)
4. **Mode Comparison Table** — Features per mode
5. **`\OmniDev`/`\OmniProd`/`\OmniUltra`** — Mode detection macros

### Chapter 101: Git Integration
1. **Git Metadata Commands** — All `\Git*` macros
2. **Verification Box** — `\GitVerificationBox` for reproducibility
3. **Build Date** — `\BuildDate`, `\DTMnow`

### Chapter 102: Docker Workflow
1. **Docker Image** — ghcr.io/wyattau/omnilatex-docker, TL2026
2. **Build Commands** — Full docker run examples with all flags
3. **ENTRYPOINT Bypass** — `--entrypoint ""` requirement
4. **Volume Mounting** — Workspace mapping
5. **Font Cache** — Pre-warmed in image

### Chapter 103: Nix Workflow
1. **flake.nix** — texlive packages, dev shell
2. **`nix develop .#`** — Dev shell activation
3. **Lean 4** — `lake build` in dev shell
4. **Reproducibility** — flake.lock

### Chapter 104: CI/CD
1. **9 GitHub Actions Workflows** — Purpose, triggers, key steps
2. **Build Pipeline** — build.yml: build → verify → deploy-pages
3. **Lean CI** — Nix-based proof verification
4. **CTAN Auto-Upload** — 5-phase pipeline with pre-flight validation
5. **CTAN Release** — Tag-triggered GitHub Release
6. **Cross-Platform** — Linux + Windows Docker validation
7. **Docker CI/CD** — Image build, push, digest sync
8. **Integration Matrix** — 13 targeted doctype×language combos
9. **Determinism** — SOURCE_DATE_EPOCH, reproducibility verification

---

## Part XI: Formal Verification

### Chapter 110: Lean 4 Proofs
1. **Why Formal Verification?** — LaTeX templates can have subtle bugs
2. **10 Proof Modules** — Purpose of each:
   | Module | Theorems | What It Proves |
   |---|---|---|
   | BuildModes | 5 | Build mode properties |
   | BuildSystem | 9 | Cache correctness, parallelism |
   | DoctypeClassMapping | 7 | Doctype→class mapping |
   | DocumentSettings | 8 | KOMA class partition |
   | DoctypeResolution | 4 | Alias resolution |
   | FloatInvariant | 2 | Float placement |
   | FontHierarchy | 4 | Strict total order |
   | I18nCompleteness | 3 | Key parity, 846 total |
   | LanguageFallback | 7 | Fallback chain stability |
   | PageGeometry | 5 | Page balance equations |
3. **Proof Structure** — How to read Lean 4 proofs
4. **Extending Proofs** — How to add new theorems

### Chapter 111: Architecture
1. **Module Dependency Graph** — 27 modules, load order
2. **Module Responsibilities** — One paragraph per module
3. **Design Principles** — Single responsibility, optional loading, KOMA integration
