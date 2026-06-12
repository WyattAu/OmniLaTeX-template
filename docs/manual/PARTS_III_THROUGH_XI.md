# Parts III-XI: Remaining Chapter Plans

---

## Part III: Typography & Content

### Chapter 30: Fonts

#### 30.1 Font System Architecture

OmniLaTeX uses a deterministic font loading strategy (proven in `FontHierarchy.lean`):

1. **fontspec** -- OpenType font loading for LuaTeX
2. **unicode-math** -- Unicode math symbols with `\setmathfont`
3. **lualatex-math** -- Fixes math-mode accents for LuaTeX
4. **amssymb** -- Additional math symbols

All fonts are loaded by explicit name, not glob-based discovery. The loading order is fixed: main, mono, sans, math. Font fallbacks use `\IfFontExistsTF` for graceful degradation.

#### 30.2 Default Font Stack

| Role | Primary Font | Fallback | Source |
|---|---|---|---|
| Serif (main) | Libertinus Serif | -- | TeX Live (`collection-fontsextra`) |
| Sans-serif | Atkinson Hyperlegible Next | Libertinus Sans | External / TeX Live |
| Monospace | Monaspace Neon | Latin Modern Mono | External / TeX Live |
| Math | Libertinus Math | -- | TeX Live |
| Icons | Font Awesome 5 | -- | TeX Live |
| CJK (SC/TC/JP) | Noto Serif CJK / Noto Sans CJK | Haranoaji Mincho | TeX Live |
| CJK (KR) | Noto Sans CJK KR | Noto Serif CJK KR | TeX Live |
| Arabic | Amiri | Noto Naskh Arabic | External / TeX Live |
| Hebrew | David CLM | Frank Ruehl CLM | External / TeX Live |
| Persian | Amiri | Noto Naskh Arabic | External / TeX Live |

**Font loading code** (from `omnilatex-fonts.sty`):

```latex
% Main font
\setmainfont[Numbers=Lowercase, Scale=MatchLowercase]{Libertinus Serif}

% Monospace with fallback
\IfFontExistsTF{Monaspace Neon}{%
    \setmonofont[Scale=MatchLowercase]{Monaspace Neon}%
}{%
    \setmonofont[Scale=MatchLowercase]{Latin Modern Mono}%
}

% Sans-serif with fallback
\IfFontExistsTF{Atkinson Hyperlegible Next}{%
    \setsansfont{Atkinson Hyperlegible Next}%
}{%
    \setsansfont[Scale=MatchLowercase]{Libertinus Sans}%
}

% Math font
\setmathfont[
    mathrm=sym, mathit=sym, mathsf=sym,
    mathbf=sym, mathtt=sym,
    NFSSFamily=libertinus,
    BoldItalicFont={}, ItalicFont={}, SmallCapsFont={},
]{Libertinus Math}
```

#### 30.3 Font Setter Commands

Users can override any font in the preamble:

```latex
\setMainFont{TeX Gyre Termes}                        % Override serif
\setSansFont{Fira Sans}                               % Override sans
\setMonoFont[Scale=MatchLowercase]{Fira Code}         % Override mono
\setMathFont{TeX Gyre Termes Math}                    % Override math
```

Each setter wraps `fontspec` commands with `\IfFontExistsTF` to produce a warning (not an error) if the font is missing.

**Font feature defaults:**

- `Numbers=Lowercase` -- Old-style (hanging) figures for the main font
- `Scale=MatchLowercase` -- Automatic x-height matching between families
- Math font uses `NFSSFamily=libertinus` -- Required for `chemmacros`/`chemformula` compatibility

#### 30.4 Math Font Configuration

The math font setup uses `unicode-math` with these `NFSSFamily` options:

```latex
\setmathfont[
    mathrm=sym,      % Use sym font for \mathrm
    mathit=sym,      % Use sym font for \mathit
    mathsf=sym,      % Use sym font for \mathsf
    mathbf=sym,      % Use sym font for \mathbf (bold math)
    mathtt=sym,      % Use sym font for \mathtt
    NFSSFamily=libertinus,  % NFSS family name for chemformula
    BoldItalicFont={},      % Suppress missing-shape warnings
    ItalicFont={},
    SmallCapsFont={},
]{Libertinus Math}
```

The `NFSSFamily=libertinus` setting is critical: it maps the Unicode math font to an NFSS family, enabling `\fontfamily{libertinus}\selectfont` in `chemmacros`/`chemformula` for chemical formulas. Without it, chemical formulas would fall back to Computer Modern.

The `lualatex-math` package fixes a LuaTeX-specific bug where `\hat`, `\tilde`, `\vec`, and other math accents produce incorrect output.

#### 30.5 Math Command Availability

With `unicode-math` loaded, traditional LaTeX math commands map to Unicode symbols:

| Traditional | Unicode-Math | Description |
|---|---|---|
| `\mathbf{x}` | `\symbf{x}` | Bold math |
| `\mathbb{R}` | `\symbb{R}` | Blackboard bold |
| `\mathcal{L}` | `\symcal{L}` | Calligraphic |
| `\mathfrak{g}` | `\symfrak{g}` | Fraktur |
| `\mathsf{x}` | `\symsf{x}` | Sans-serif math |
| `\mathtt{x}` | `\symtt{x}` | Monospace math |

The `mathrm=sym` option in `\setmathfont` makes `\mathbf{x}` produce the correct bold Unicode symbol, so both `\mathbf` and `\symbf` work identically.

#### 30.6 Emoji & Icon Fonts

Font Awesome 5 provides icons via `\faIcon{name}`:

```latex
\faIcon{github}    % GitHub icon
\faIcon{envelope}  % Email icon
\faIcon{linkedin}  % LinkedIn icon
```

#### 30.7 CJK Font Loading

CJK fonts are auto-loaded based on the `language` option:

- `chinese`, `simplifiedchinese`, `traditionalchinese` -- Load `omnilatex-cjk` module
- `japanese` -- Load `omnilatex-cjk` module
- `korean` -- Load `omnilatex-cjk` module

The module defines font families with fallback chains:

```latex
% Simplified Chinese
\IfFontExistsTF{Noto Serif CJK SC}{%
    \newfontfamily\cjkfont[Script=CJK]{Noto Serif CJK SC}%
}{%
    \IfFontExistsTF{Haranoaji Mincho}{%
        \newfontfamily\cjkfont[Script=CJK]{Haranoaji Mincho}%
    }{}%
}
```

#### 30.8 RTL Font Loading

Arabic, Hebrew, and Persian fonts are auto-defined when the corresponding language is selected:

| Language | Primary | Fallback | Script tag |
|---|---|---|---|
| Arabic | Amiri | Noto Naskh Arabic | `Script=Arabic` |
| Hebrew | David CLM | Frank Ruehl CLM | `Script=Hebrew` |
| Persian | Amiri | Noto Naskh Arabic | `Script=Arabic` |

Bold variants use `BoldFeatures={FakeBold=2}` since many Arabic/Hebrew fonts lack true bold weights.

#### 30.9 Unit Number Font

The `\unitnumberfont` command (used by siunitx) is defined in the fonts module to ensure consistent font rendering in physical units:

```latex
% In omnilatex-math.sty:
\newfontfamily\unitnumberfont{Libertinus Serif}[
    Numbers=Lowercase,
    Scale=MatchLowercase,
]
```

#### 30.10 Font Troubleshooting

| Issue | Cause | Fix |
|---|---|---|
| `Font 'X' not found` warning | Font not installed | Install the font or accept the fallback |
| `luaotfload: db not found` | Font cache missing | Run `luaotfload-tool --update` |
| Missing bold math symbols | Libertinus Math lacks bold italic | Use `\symbf` instead of `\mathbf` for affected symbols |
| Chemical formulas in wrong font | Missing `NFSSFamily` | Ensure `NFSSFamily=libertinus` in `\setmathfont` |
| CJK glyphs show as boxes | Missing CJK font | Install Noto CJK fonts or Haranoaji |
| Arabic text left-to-right | Missing `omnilatex-rtl` module | Set `language=arabic` to auto-load |
| `ScriptExtensions.txt not found` | Nix/TL2025 path issue | Lua workaround in `omnilatex.cls` patches `kpse.find_file` |

### Chapter 31: Text Formatting

#### 31.1 Microtype

Loaded automatically by `omnilatex-typesetting.sty`. Provides:

- **Character protrusion** -- Extends punctuation slightly into margins for optically justified edges
- **Font expansion** -- Slightly stretches/shrinks characters for better line filling
- **Tracking** -- Inter-character spacing adjustments

Configuration uses the default `microtype` settings for LuaTeX, which are less extensive than the pdfLaTeX version but still provide protrusion and expansion.

#### 31.2 Extdash

Provides hyphenation shortcuts using `fast\-/paced` syntax for en-dashes and em-dashes in running text:

```
fast--paced    % en-dash: fast--paced
fast---paced   % em-dash: fast---paced
```

#### 31.3 csquotes

Language-aware quotation marks via `\enquote{text}`:

```latex
\enquote{Hello world}              % "Hello world" (English)
\enquote[de]{Hallo Welt}            % ,Hallo Welt' (German)
```

Nested quotes are handled automatically:

```latex
\enquote{He said \enquote{hello}}  % "He said 'hello'"
```

#### 31.4 ragged2e

Improved ragged text via `\RaggedRight` and `\RaggedLeft`:

```latex
\RaggedRight   % Left-aligned with better word spacing than \raggedright
\RaggedLeft    % Right-aligned
\RaggedCenter  % Center-aligned (alternative to \centering in some contexts)
```

#### 31.5 Blind Text

Placeholder text for testing layouts:

```latex
\Blindtext[2][3]     % 2 paragraphs, 3 sentences each
\Blinddocument       % Full dummy document with sections and subsections
```

#### 31.6 Line Spacing

Controlled via `setspaceenhanced`:

```latex
\linespread{1.5}     % 1.5x line spacing
\linespread{2.0}     % Double spacing
```

Each doctype profile sets a default: articles use `onehalf`, theses use `onehalf`, manuals use `single`.

#### 31.7 Paragraph Spacing

KOMA parskip options control paragraph separation:

```latex
\KOMAoptions{parskip=half}   % Half-line space between paragraphs (default for articles)
\KOMAoptions{parskip=full}   % Full-line space between paragraphs
\KOMAoptions{parskip=never}  % Indented paragraphs, no extra space
```

### Chapter 32: Mathematics

#### 32.1 amsmath + unicode-math

The math module loads `mathtools` (which loads `amsmath`) and `unicode-math`. Equation environments:

| Environment | Description |
|---|---|
| `equation` | Single numbered equation |
| `equation*` | Single unnumbered equation |
| `align` | Multi-line aligned equations (numbered) |
| `align*` | Multi-line aligned equations (unnumbered) |
| `gather` | Multi-line centered equations (numbered) |
| `multline` | Long equation split across lines |
| `cases` | Cases environment (inside equation) |
| `empheq` | Equations with emphasis boxes |

Tag format uses brackets by default (via `\newtagform{brackets}{[}{]}` and `\usetagform{brackets}`):

```
f(x) = ax^2 + bx + c     [1]
```

Display breaks are allowed (`\allowdisplaybreaks[2]`) with moderate permissiveness.

#### 32.2 Auto-Scaling Delimiters

Defined via `\DeclarePairedDelimiter` from `mathtools`:

```latex
\parens{x}        % (x)     -- fixed size
\parens*{x}       % (x)     -- auto-scaled (like \left( ... \right))
\brackets{x}      % [x]     -- fixed size
\brackets*{x}     % [x]     -- auto-scaled
\braces{x}        % {x}     -- fixed size
\braces*{x}       % {x}     -- auto-scaled
```

Optional sizing argument: `\parens[\big]{x}` for specific sizes.

#### 32.3 Equation Punctuation

```latex
x = 5\eqend           % Period after equation
x = 5\eqcomma         % Comma after equation
y \coloneq x^2 + 1     % Colon-equals definition
```

#### 32.4 Statistical and Physical Macros

```latex
\mean{x}          % Mean: <x>
\logmean{x}{y}    % Logarithmic mean
\abs{x}           % Absolute value: |x|
\circlednum{n}    % Circled number: (1)
\qq{text}         % Quoted text in math mode
\grad             % Gradient operator
\const            % Constant symbol
```

#### 32.5 Custom Operators

```latex
\DeclareMathOperator{\Tr}{Tr}       % Trace operator
\DeclareMathOperator{\diag}{diag}    % Diagonal matrix
```

Pre-defined: `\grad`, `\const`.

#### 32.6 Chemistry

The `chemmacros` package provides chemical notation:

```latex
\ch{H2O}                    % Chemical formula: H2O
\chcpd{NaCl}                % Compound name formatting
\ch{2 H2 + O2 -> 2 H2O}     % Chemical equation (inline)
```

Reaction environments:

```latex
\begin{reaction}
    2 H2 + O2 -> 2 H2O
\end{reaction}
```

Reaction numbering uses `R[n]` prefix (e.g., `R[2.1]` for chapter 2, reaction 1) via custom `before-tag` setting.

### Chapter 33: Physical Mathematics

1. **siunitx Setup** -- Locale-aware, per-mode=fraction
2. **Core Commands** -- `\num`, `\unit`, `\qty`, `\qtyrange`
3. **Custom SI Units** -- `\volpercent`, `\watthour`, `\annum`, `\atmosphere`, `\partspermillion`, `\bar`, `\relhumidity`
4. **Custom SI Qualifiers** -- `\dryair`, `\water`, `\thermal`
5. **S-Column in Tables** -- siunitx column type for aligned numbers
6. **Chemistry** -- chemmacros, `\chcpd`, `reaction`, `reactionsgather`, `\chemamount`
7. **Fractions** -- xfrac, nicefrac

### Chapter 34: Derivatives & Vector Calculus

1. **Derivative Macros** -- `\deriv[deg]{f}{x}`, `\deriv*{f}{x}` (partial), `\fracderiv{f}{x}{t}`, `\timederiv{f}{t}`, `\posderiv{f}{x}`
2. **Vector Macros** -- `\vect{v}`, `\nablaoperator[deg]`
3. **Physical Macros** -- `\flow{}`, `\difference{}`, `\heatexentry{}`, `\heatexexit{}`, `\temperaturepair{min}{max}`
4. **Convention Tables** -- Full reference of all math macros with LaTeX source and rendered output

### Chapter 35: CJK Mathematics

1. **CJK Math Fonts** -- luatexja math support
2. **Ruby Annotations** -- `\ruby{base}{ruby}`, `\furigana`, `\pinyin`
3. **Vertical Math** -- Vertical writing mode for equations
4. **CJK-Latin Spacing** -- `\cjklatinspacing`, `\setCJKLatinSpacing`

---

## Part IV: Language & Internationalization

### Chapter 40: I18N System

1. **polyglossia Setup** -- Primary and secondary languages
2. **Translation System** -- `translations` package, `\GetTranslation`, `\RenewTranslation`
3. **Language Fallback Chain** -- English as default, Lean proof reference
4. **Dynamic Switching** -- `\begin{english}...\end{english}` inline
5. **Complete Key Table** -- All 47 translation keys explained

### Chapter 41: Multilingual Documents

1. **Multi-Language Example** -- `examples/multi-language/` walkthrough
2. **Cross-Language References** -- cref across language boundaries
3. **Bibliography in Multiple Languages** -- biblatex language support

### Chapter 42: RTL Scripts

1. **Arabic** -- `\setArabicFont`, Arabic-Indic digits, bidi layout
2. **Hebrew** -- `\setHebrewFont`, Hebrew font fallback
3. **Persian** -- Persian font fallback, RTL title page
4. **RTL Title Page** -- Automatic font override for Arabic/Hebrew/Persian
5. **Inline Direction** -- `\LTRinline`, `\RTLinline`
6. **Example Walkthroughs** -- rtl-arabic, rtl-hebrew examples

### Chapter 43: CJK Scripts

1. **Chinese (Simplified/Traditional)** -- luatexja, Noto CJK SC/TC, `\ruby`
2. **Japanese** -- Noto CJK JP, furigana, vertical text
3. **Korean** -- Noto CJK KR, Hangul support
4. **Auto-Detection** -- `\setCJKScript{sc|tc|jp|kr}`
5. **Vertical Writing** -- `vertical` env, `\verticaltext`
6. **CJK-Latin Spacing** -- `\cjklatinspacing`
7. **Example Walkthroughs** -- cjk-chinese, cjk-japanese, cjk-korean

### Chapter 44: Translation Key Reference

- **Complete table**: All 47 keys x 18 languages (846 translations)
- **Key Descriptions**: What each key means, where it's used
- **Adding New Keys**: `\DeclareTranslation` workflow

---

## Part V: Layout & Structure

### Chapter 50: Page Layout

1. **KOMA Page Geometry** -- `\areaset`, DIV, BCOR
2. **Custom Margins** -- `\setCustomMargins{L}{R}{T}{B}`
3. **Two-Side Layout** -- `twoside` option, header/footer differences
4. **Headers & Footers** -- scrlayer-scrpage, automark, `\headerrule`
5. **Landscape Pages** -- `landscape` env, `\pdflandscape`
6. **A5 Format** -- `a5` class option
7. **Page Numbering** -- `\frontmatter` (alpha), `\mainmatter` (arabic), `\backmatter`

### Chapter 51: Sectioning

1. **KOMA Section Hierarchy** -- `\part`, `\chapter`, `\section`, `\subsection`, `\subsubsection`, `\paragraph`, `\subparagraph`
2. **Chapter Prefix** -- Scaled 4.5x number formatting
3. **Table of Contents** -- `\tableofcontents`, depth control
4. **List of Figures/Tables** -- `\listoffigures`, `\listoftables`, `\listofexamples`, `\listoflistings`
5. **PDF Bookmarks** -- `\pdfbookmark`, bold chapter bookmarks
6. **Unnumbered Chapters** -- `\addchap`, `\chapter*`

### Chapter 52: Title Pages

1. **4 Built-in Styles:**
   - `titlestyle=book` -- Vertical rule, small caps author
   - `titlestyle=thesis` -- Vertical rule, examiners table
   - `titlestyle=simple` -- Default KOMA title
   - `titlestyle=TUHH` -- TUHH-specific branded title
2. **Custom Title Pages** -- How institutions define `\DefineXxxTitleStyle`
3. **Title Page Metadata** -- `\title`, `\author`, `\date`, `\publishers`

### Chapter 53: Institutions

1. **21 Institution Configs** -- Table with colors, logos, title pages
2. **Creating Your Own** -- Step-by-step: create directory, define .sty, add logo, set colors
3. **Logo Management** -- SVG logos, `\includesvg`, `\DeclareTranslation{LogoXxx}`
4. **Color Branding** -- `\setkomacolor`, primary/secondary colors

---

## Part VI: Figures, Tables & Floats

### Chapter 60: Floats

1. **Float Placement** -- KOMA float placement, `floatrow`
2. **Continued Floats** -- `\ContinuedFloat` for multi-page figures
3. **Float Footnotes** -- `\omnlFloatFootmark`, `\omnlFloatFoottext`
4. **Side Captions** -- `\captionof` with minipage layout
5. **Key-Value Float Interface** -- `\omnlFigure[caption=..., label=...]`
6. **Float Grid** -- `omnlFloatRow[n-cols]` for multi-column float layouts

### Chapter 61: Figures

1. **Images** -- `\includegraphics`, path management, `\svgpath`
2. **SVG Graphics** -- `\includesvg`, Inkscape integration, `--shell-escape`
3. **TikZ Basics** -- Libraries loaded, coordinate systems, basic shapes
4. **Subfigures** -- `subfigure` environment, side-by-side figures
5. **Text Over Images** -- `\ctrw{text}` (white contour), TikZ overlays
6. **Debugging SVG** -- `\debugtikzsvg`

### Chapter 62: Tables

1. **booktabs** -- `\toprule`, `\midrule`, `\bottomrule`, no vertical lines
2. **tabularray** -- `longtblr`, variable-width columns, siunitx integration
3. **siunitx S-Columns** -- Number alignment in tables
4. **Multi-Column Tables** -- `\multicolumn`, `\cmidrule`
5. **Rotated Cells** -- `\multirotatecell{rows}{text}`
6. **Table Footnotes** -- `\TblrNote`, `\TblrRemark`

### Chapter 63: pgfplots

1. **Line & Scatter Plots** -- `regularplot` style, custom styles
2. **Bar Charts** -- `ybar`, stacked bars
3. **Contour Plots** -- `contour gnuplot`, custom functions
4. **Date Plots** -- `dateplot` library, ISO 8601
5. **CSV Import** -- `\pgfplotstableread`, column selection, filtering
6. **Custom Styles** -- `tuftelike`, `arrowplot`, `plainplot`
7. **Color Maps** -- `viridis`, `RdYlBu3`, `Set2`
8. **Dual Axes** -- Secondary y-axis
9. **Groupplots** -- Side-by-side plots with shared axes

### Chapter 64: TikZ Engineering

1. **Flowcharts** -- `startstop`, `io`, `process`, `decision` node styles
2. **Circuit Diagrams** -- `circuits.ee.IEC`, resistors, batteries, contacts
3. **3D Drawings** -- `tdplot`, canvas planes, flow arrows
4. **Custom Thermodynamic Shapes** -- valve, pump, compressor, heat exchanger, radiator, boiler, sensor, equalizing tank (with all anchors)
5. **Pipe Networks** -- `pipe` node styles, three-way/four-way valves
6. **Control Systems** -- Simulink-style blocks, feedback loops, saturation
7. **Annotation Arrows** -- `\annotationarrow`, `\wall`, `\flowarrow`

---

## Part VII: References & Glossaries

### Chapter 70: Bibliography

1. **biblatex + biber Setup** -- `ext-authoryear`, `introcite=label`, `backref`
2. **Citation Commands** -- `\cite`, `\textcite`, `\parencite`, `\footcite`, `\fullcite`
3. **Citation Groups** -- `\cites`, `\parencites`, `\textcites`
4. **Per-Chapter Bibliography** -- `refsection` vs `refsegment`
5. **Bib File Management** -- `\addbibresource`, bib2gls integration
6. **"Further Reading" Section** -- `\nocite{*}`, `category=cited/notcategory=cited`

### Chapter 71: Citation Styles

1. **9 Preconfigured Styles:**
   - `ieee`, `acm`, `apa`, `chicago`, `nature`, `science`, `harvard`, `vancouver`, `mla`
2. **`\citationstyle{name}`** -- Switching styles per document
3. **Example Comparison** -- Same bibliography rendered in all 9 styles

### Chapter 72: Glossaries

1. **glossaries-extra Setup** -- nomain, abbreviations, symbols, index, numbers
2. **Custom Glossary Types** -- Symbols with units, constants with values, subscripts
3. **Shortcut Commands** -- `\sym{}`, `\sub{}`, `\name{}`, `\cons{}`, `\idx{}`, `\abb{}`, `\num{}`
4. **Custom Fields** -- `unit`, `specific`, `firstname`, `value`, `international-symbol`
5. **Printing** -- `\printunsrtglossary` with custom styles
6. **Subscripts Glossary** -- Multi-column subscripts list
7. **Symbol Markers** -- `\specificsymbolmark`, `\alternativesymbolmark`
8. **Index** -- `\printunsrtindex` with `bookindex` style

### Chapter 73: Cross References

1. **cleveref** -- `\cref`, `\Cref`, `\crefname`, `\lcnamecref`, `\cpageref`
2. **Custom crefnames** -- For `example`, `code`, `listing` environments
3. **PDF Bookmarks** -- hyperref setup, bold chapter bookmarks
4. **Equation References** -- `\creflabelformat{equation}{#2#1#3}`

---

## Part VIII: Code & Listings

### Chapter 80: Code Listings

1. **minted Setup** -- `manni` style, `leftline`, line numbers, cache
2. **Inline Code** -- `\mintinline{python}{...}`
3. **Block Listings** -- `\begin{minted}{python}...\end{minted}`
4. **Long Listings** -- `longlisting` env, `\inputminted{lua}{file.lua}`
5. **Line Highlighting** -- `highlightlines`, `\phstring`, `\phnum`, `\phother`, `\phnote`
6. **Simulink Icons** -- `\mtlbsmlkicon{name}`
7. **Language Support** -- Python, MATLAB, Lua, Modelica, C/C++, etc.
8. **Accessible Line Numbers** -- `\emptyaccsupp`

### Chapter 81: Lua Scripting

1. **Lua in LaTeX** -- `\directlua`, `lua`, `\luasetup`
2. **Git Metadata** -- `\GitRefName`, `\GitShortSHA`, `\GitLongSHA`, `\BuildDate`
3. **Conditional Compilation** -- `BUILD_MODE` env var, `\ifomnilatex@...`
4. **Custom Lua Commands** -- Creating new Lua-driven macros
5. **Example:** `lua-showcase` walkthrough

---

## Part IX: Advanced Features

### Chapter 90: Color Themes

1. **7 Palettes** -- default, midnight, forest, rose, monochrome, monochrome-dark, sepia
2. **`\usetheme{name}`** -- Loading a palette
3. **Dark/Light Mode** -- `\darkmode`, `\lightmode`
4. **Per-Slot Overrides** -- `\setthemecolor{slot}{color}`
5. **Conditional Theming** -- `\ifthememode{dark}{yes}{no}`
6. **tcolorbox Integration** -- Themed block environments

### Chapter 91: Boxes & Environments

1. **Example Box** -- `example` tcolorbox (auto-counter, LoE, breakable)
2. **Key Concept Box** -- `keyconceptbox` (handouts)
3. **Callout Box** -- `\callout{title}{text}` (white papers)
4. **Alert/Definition/Note Blocks** -- Presentation block envs
5. **Git Verification Box** -- `\GitVerificationBox`

### Chapter 92: Censoring

1. **`\censor{text}`** -- Black-bar censoring
2. **`\StopCensoring`** -- End censoring in document
3. **`\todo{text}`** -- TODO notes (conditional on `todonotes` option)
4. **`\censorbox{...}`** -- Censored boxes
5. **Blind Text** -- `\Blindtext` for placeholder content

### Chapter 93: PDF Accessibility

1. **PDF/UA-1** -- `tagpdf` activation
2. **Alt Text** -- `\alttext{desc}` for figures, `\tikzalttext{desc}` for TikZ
3. **Accessible Links** -- `\accessiblelink{text}{url}{sr-desc}`
4. **Heading Validation** -- `\validatstructure`
5. **Contrast Checking** -- `\checkcontrast{fg}{bg}`
6. **Reading Order** -- `\readingorder{n}`
7. **Language Tags** -- `\langtag{lang}{text}`
8. **Example:** `accessibility-test` walkthrough

### Chapter 94: Presentations

(See Chapter 25.1 -- same content, different context)

### Chapter 95: Posters

(See Chapter 25.2 -- same content, different context)

---

## Part X: Build & Automation

### Chapter 100: Build Modes

#### 100.1 Build Mode Enum Values

OmniLaTeX defines three build modes, controlled via `--mode` flag, `BUILD_MODE` environment variable, or latexmk's `$build_mode` Perl variable:

| Mode | latexmk `$max_repeat` | `$bibtex_use` | `$biber` | `$do_gls` | Purpose |
|---|---|---|---|---|---|
| `dev` | 6 | 2 | `biber %O %S` | 1 | Fast iteration |
| `prod` | 7 | 2 | `biber --validate-datamodel %O %S` | 1 | Final output |
| `ultra` | 1 | 0 | `true` (no-op) | 0 | Fastest possible |

#### 100.2 Mode Effects

**dev mode** (default):

- 6 latexmk passes -- enough for bibliography and glossary churn
- Full biber support (bibliography resolution)
- Full bib2gls support (glossary resolution)
- `--shell-escape` enabled (SVG, minted)
- No biber datamodel validation (faster iteration on broken .bib entries)
- Suitable for active editing

**prod mode** (CI, final output):

- 7 latexmk passes -- one extra pass for stability verification
- Full biber support with `--validate-datamodel` (catches schema violations)
- Full bib2gls support
- `--shell-escape` enabled
- Biber validates all `.bib` entries against the biblatex datamodel
- Suitable for release builds and CI pipelines

**ultra mode** (fastest):

- 1 latexmk pass only -- no bibliography or glossary resolution
- Biber replaced with `true` (no-op command)
- bib2gls completely disabled (`$do_gls = 0`)
- `--shell-escape` still enabled (minted works)
- Bibliography entries will show as `[?]` -- citations are not resolved
- Glossary entries will be empty
- Suitable for quick proofreading of text/layout changes

#### 100.3 Strictness Levels

Build mode controls strictness progressively:

| Check | dev | prod | ultra |
|---|---|---|---|
| latexmk passes | 6 | 7 | 1 |
| Biber bibliography | Yes | Yes (validated) | No |
| bib2gls glossary | Yes | Yes | No |
| biber datamodel validation | No | Yes | No |
| shell-escape | Yes | Yes | Yes |
| Reference resolution | Yes | Yes | Partial (1 pass) |

#### 100.4 Mode Detection in LaTeX

The build mode is available inside LaTeX documents via conditional macros:

```latex
\ifOmniDev
    % Code only in dev builds
\fi

\ifOmniProd
    % Code only in production builds
\fi

\ifOmniUltra
    % Code only in ultra builds
\fi
```

These macros are defined based on the `BUILD_MODE` environment variable, which is read by `omnilatex.cls` via Lua.

#### 100.5 Source Date Epoch for Reproducibility

OmniLaTeX supports reproducible builds via the `SOURCE_DATE_EPOCH` specification (<https://reproducible-builds.org/specs/source-date-epoch/>).

**How it works:**

1. `build.py` accepts `--source-date-epoch TIMESTAMP` flag
2. The flag sets the `SOURCE_DATE_EPOCH` environment variable
3. `.latexmkrc` reads `SOURCE_DATE_EPOCH` and derives year/month/day:

   ```perl
   if (exists $ENV{SOURCE_DATE_EPOCH} && $ENV{SOURCE_DATE_EPOCH} ne '') {
       my $sde = $ENV{SOURCE_DATE_EPOCH};
       my @t = gmtime($sde);
       $ENV{SOURCE_DATE_EPOCH_YEAR}  = $t[5] + 1900;
       $ENV{SOURCE_DATE_EPOCH_MONTH} = $t[4] + 1;
       $ENV{SOURCE_DATE_EPOCH_DAY}   = $t[3];
   }
   ```

4. The Lua script `git-metadata.lua` freezes `\year`, `\month`, `\day`, `\time` primitives to the epoch values
5. PDF metadata dates are frozen in `omnilatex-hyperref.sty`
6. All subprocess invocations inherit the environment variable

**Usage:**

```bash
# Build with frozen timestamps
python3 build.py build-all --source-date-epoch 1700000000

# Nix builds set this automatically
nix build .#default  # SOURCE_DATE_EPOCH=1700000000
```

**Reproducibility verification:**

The Nix flake includes a reproducibility check (`nix build .#checks.reproducibility`) that:

1. Builds the thesis example with a fixed `SOURCE_DATE_EPOCH`
2. Records the SHA-256 hash of the output PDF
3. Cleans all generated files
4. Rebuilds from scratch
5. Compares the second hash against the first
6. Fails if hashes differ

### Chapter 101: Git Integration

1. **Git Metadata Commands** -- All `\Git*` macros
2. **Verification Box** -- `\GitVerificationBox` for reproducibility
3. **Build Date** -- `\BuildDate`, `\DTMnow`

### Chapter 102: Docker Workflow

1. **Docker Image** -- ghcr.io/wyattau/omnilatex-docker, TL2026
2. **Build Commands** -- Full docker run examples with all flags
3. **ENTRYPOINT Bypass** -- `--entrypoint ""` requirement
4. **Volume Mounting** -- Workspace mapping
5. **Font Cache** -- Pre-warmed in image

### Chapter 103: Nix Workflow

1. **flake.nix** -- texlive packages, dev shell
2. **`nix develop .#`** -- Dev shell activation
3. **Lean 4** -- `lake build` in dev shell
4. **Reproducibility** -- flake.lock

### Chapter 104: CI/CD

1. **15 GitHub Actions Workflows** -- Purpose, triggers, key steps
2. **Build Pipeline** -- build.yml: build, verify, deploy-pages
3. **Lean CI** -- Nix-based proof verification
4. **CTAN Auto-Upload** -- 5-phase pipeline with pre-flight validation
5. **CTAN Release** -- Tag-triggered GitHub Release
6. **Cross-Platform** -- Linux + Windows Docker validation
7. **Docker CI/CD** -- Image build, push, digest sync
8. **Integration Matrix** -- 13 targeted doctype x language combos
9. **Determinism** -- SOURCE_DATE_EPOCH, reproducibility verification

---

## Part XI: Formal Verification

### Chapter 110: Lean 4 Proofs

1. **Why Formal Verification?** -- LaTeX templates can have subtle bugs
2. **10 Proof Modules** -- Purpose of each:
   | Module | Theorems | What It Proves |
   |---|---|---|
   | BuildModes | 5 | Build mode properties |
   | BuildSystem | 9 | Cache correctness, parallelism |
   | DoctypeClassMapping | 7 | Doctype-class mapping |
   | DocumentSettings | 8 | KOMA class partition |
   | DoctypeResolution | 4 | Alias resolution |
   | FloatInvariant | 2 | Float placement |
   | FontHierarchy | 4 | Strict total order |
   | I18nCompleteness | 3 | Key parity, 846 total |
   | LanguageFallback | 7 | Fallback chain stability |
   | PageGeometry | 5 | Page balance equations |
3. **Proof Structure** -- How to read Lean 4 proofs
4. **Extending Proofs** -- How to add new theorems

### Chapter 111: Architecture

1. **Module Dependency Graph** -- 31 modules, load order
2. **Module Responsibilities** -- One paragraph per module
3. **Design Principles** -- Single responsibility, optional loading, KOMA integration
