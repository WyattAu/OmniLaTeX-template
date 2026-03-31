# OmniLaTeX API Reference

Auto-generated from module interface contracts.

## omnilatex-base

Core functionality and base setup: build mode detection, conditionals, date/time, spacing.

### Commands

| Command | Signature | Description |
|---------|-----------|-------------|
| `\omnilatex@buildmode` | | Internal macro holding the current build mode string (dev/prod/ultra), set via BUILD_MODE env var or Lua |
| `ifOmniDev` | | Boolean conditional: true when build mode is 'dev' (default) |
| `ifOmniProd` | | Boolean conditional: true when build mode is 'prod' |
| `ifOmniUltra` | | Boolean conditional: true when build mode is 'ultra' |
| `\OmniBuildMode` | | Public accessor that expands to the current build mode string |

## omnilatex-biblio

Bibliography management with biblatex: ext-authoryear style, citation formatting, and uncited works category.

### Environments

| Name | Description |
|------|-------------|
| `bibnonum` | Custom bibliography environment without numbering, based on biblatex list infrastructure |

### Other Exports

| Name | Type | Description |
|------|------|-------------|
| `cited` | bibliography_category | Bibliography category tracking which entries were actually cited vs. only in bib file |
| `notcited` | bibliography_heading | Bibliography heading for uncited works with translated 'Further Reading' section title |
| `subbibliography` | bibliography_heading | Bibliography heading for per-chapter bibliographies using cref to the refsegment |

## omnilatex-boxes

Color boxes and tcolorbox environments: example boxes with auto-counter and Git verification box.

### Commands

| Command | Signature | Description |
|---------|-----------|-------------|
| `\GitVerificationBox` | | Inline tcbox with a hyperlink to verify the current git commit |

### Environments

| Name | Description |
|------|-------------|
| `example` | Numbered tcolorbox example environment with auto-counter, breakable, gray styling, listed in loe |

## omnilatex-colors

Color definitions and named color schemes for diagrams, plots, code, and links.

### Colors

| Name | Description |
|------|-------------|
| `g1` | Gradient shade: black!70 |
| `g2` | Gradient shade: black!55 |
| `g3` | Gradient shade: black!40 |
| `g4` | Gradient shade: black!20 |
| `g5` | Gradient shade: black!10 |
| `g6` | Gradient shade: black!05 |
| `Glass` | Very light blue for diagrams (RGB 170,238,255) |
| `Air` | Light blue for diagrams (RGB 213,246,255) |
| `LightFluid` | Light fluid blue (RGB 148,224,255) |
| `MediumFluid` | Medium fluid blue (RGB 135,178,232) |
| `DarkFluid` | Dark fluid blue (RGB 119,151,197) |
| `HotFluid` | Hot fluid red (RGB 255,128,128) |
| `darklink` | Dark blue link color (RGB 48,62,116) |
| `rdylbu1` | ColorBrewer RdYlBu red (RGB 215,48,39) |
| `rdylbu2` | ColorBrewer RdYlBu orange (RGB 252,141,89) |
| `rdylbu3` | ColorBrewer RdYlBu light yellow (RGB 254,224,144) |
| `rdylbu4` | ColorBrewer RdYlBu light blue (RGB 224,243,248) |
| `rdylbu5` | ColorBrewer RdYlBu medium blue (RGB 145,191,219) |
| `rdylbu6` | ColorBrewer RdYlBu dark blue (RGB 69,117,180) |
| `Set2A` | ColorBrewer Set2 qualitative A (RGB 102,194,165) |
| `Set2B` | ColorBrewer Set2 qualitative B (RGB 252,141,98) |
| `Set2C` | ColorBrewer Set2 qualitative C (RGB 141,160,203) |
| `Set2D` | ColorBrewer Set2 qualitative D (RGB 231,138,195) |
| `Set2E` | ColorBrewer Set2 qualitative E (RGB 166,216,84) |
| `Set2F` | ColorBrewer Set2 qualitative F (RGB 255,217,47) |
| `Set2G` | ColorBrewer Set2 qualitative G (RGB 229,196,148) |
| `Set2H` | ColorBrewer Set2 qualitative H (RGB 179,179,179) |
| `mBlue` | Matlab blue for plots (HTML 0072BD) |
| `mOrange` | Matlab orange for plots (HTML D95319) |
| `mYellow` | Matlab yellow for plots (HTML EDB120) |
| `mPurple` | Matlab purple for plots (HTML 7E2F8E) |
| `mGreen` | Matlab green for plots (HTML 77AC30) |
| `mSky` | Matlab sky blue for plots (HTML 4DBEEE) |
| `mRed` | Matlab red for plots (HTML A2142F) |
| `cRed` | Code annotation red (RGB 209,0,86) |
| `cBlue` | Code annotation blue (RGB 0,130,185) |
| `cGreen` | Code annotation green (RGB 0,128,63) |
| `cOrange` | Code annotation orange (RGB 244,131,66) |
| `DarkLinkGreen` | Demonstration link green (RGB 65,107,60) |
| `kit-blue50` | KIT corporate blue 50% (RGB 0,84,159) |
| `kit-blue40` | KIT corporate blue 40% (RGB 64,127,183) |

## omnilatex-document

Document metadata commands: document type, font size, layout controls, metadata fields, and utility commands.

### Commands

| Command | Signature | Description |
|---------|-----------|-------------|
| `\documenttype` | `{type}` | Set the document type string (e.g., Bachelor Thesis, Master Thesis) |
| `\documentfontsize` | `{size}` | Set document font size via KOMAoptions and recalculate typearea |
| `\documentlayout` | `{layout}` | Set document layout KOMAoptions and recalculate typearea |
| `\documentcolormode` | `{mode}` | Set document color mode (dark/light/color) applied at begin-document |
| `\documentlinespacing` | `{spacing}` | Set line spacing (single/onehalf/double or numeric) applied at begin-document |
| `\documentparspacing` | `{spacing}` | Set paragraph spacing (none/half/full or dimension) applied at begin-document |
| `\documentitemspacing` | `{spacing}` | Set list item spacing (none/compact/normal or dimension) applied at begin-document |
| `\documentfontmode` | `{mode}` | Set document font mode (serif/sans/mono) applied at begin-document |
| `\documentlinkstyle` | `{style}` | Set document link style (color/plain) applied at begin-document |
| `\documentcodestyle` | `{style}` | Set document code listing style (color/bw or minted style name) applied at begin-document |
| `\idnumber` | `{id}` | Set student ID number |
| `\firstexamniner` | `{name}` | Set first examiner name |
| `\secondexamniner` | `{name}` | Set second examiner name |
| `\supervisor` | `{name}` | Set supervisor name |
| `\signaturefield` | `[name]` | Typeset a signature field with lines for name and place/date, defaults to \@author |
| `\iecfeg` | `{text}` | Wraps text in italics for abbreviations like i.e., e.g., c.f. |
| `\adaptedfrom` | | Prints 'Adapted from' or 'Adaptiert von' based on current language |
| `\ctanpackage` | `[url]{package_name}` | Wraps package name as a hyperlink to CTAN (or custom URL) |
| `\sampletext` | | Prints the pangram 'The quick brown Fox jumps over the lazy Dog 13 times!' |

## omnilatex-floats

Float configuration: captions, subfloats, and high-level float wrapper commands with key-value options.

### Commands

| Command | Signature | Description |
|---------|-----------|-------------|
| `\omnlFigure` | `[options]{content}` | High-level figure wrapper with key-value options: placement, caption, short-caption, label, footnote, caption-width, align, caption-position |
| `\omnlTable` | `[options]{content}` | High-level table wrapper with key-value options; defaults to top caption placement |
| `\omnlFloatCaption` | | Manually typeset the float caption when caption-position=manual |
| `\omnlFloatNote` | `{text}` | Adds an unnumbered caption note below the float |
| `\omnlFloatFootmark` | `[number]` | Places a footnote mark inside a float; auto-increments if no number given |
| `\omnlFloatFoottext` | `[number]{text}` | Places footnote text corresponding to omnlFloatFootmark |

### Environments

| Name | Description |
|------|-------------|
| `omnlFloatRow` | Minipage-based row layout for side-by-side floats, default 2 columns |

## omnilatex-fonts

Font configuration and loading for LuaLaTeX: main, mono, sans, math, unit, and icon fonts.

### Commands

| Command | Signature | Description |
|---------|-----------|-------------|
| `\unitnumberfont` | | Font family for typesetting units with siunitx, using Libertinus Serif with upright numbers |

## omnilatex-glossary

Glossary management: symbols, abbreviations, subscripts, constants, index, custom fields, and glossary printing styles.

### Commands

| Command | Signature | Description |
|---------|-----------|-------------|
| `\sym` | `{label}` | Alias for \gls{sym.label} to access symbol glossary entries |
| `\sub` | `{label}` | Alias for \gls{sub.label} to access subscript glossary entries |
| `\name` | `{label}` | Alias for \gls{name.label} to access name glossary entries |
| `\cons` | `{label}` | Alias for \gls{cons.label} to access constant glossary entries |
| `\idx` | `{label}` | Alias for \gls{idx.label} to access index glossary entries |
| `\abb` | `{label}` | Alias for \gls{abb.label} to access abbreviation glossary entries |
| `\symspec` | `[options]{label}` | Shortcut for \glsspecific{sym.label} to access the 'specific' field of a symbol entry |
| `\symprefix` | | Prefix string 'sym.' for symbol glossary labels |
| `\subprefix` | | Prefix string 'sub.' for subscript glossary labels |
| `\nameprefix` | | Prefix string 'name.' for name glossary labels |
| `\constantsprefix` | | Prefix string 'cons.' for constant glossary labels |
| `\indexprefix` | | Prefix string 'idx.' for index glossary labels |
| `\abbreviationprefix` | | Prefix string 'abb.' for abbreviation glossary labels |
| `\glshdrfont` | `{text}` | Font command for glossary table headers (bold) |
| `\specificsymbolmark` | | Mark appended after description for specific symbols (asterisk) |
| `\alternativesymbolmark` | | Separator mark between symbol and its alternative version (slash) |

### Other Exports

| Name | Type | Description |
|------|------|-------------|
| `symbunitlong` | glossary_style | Custom glossary style for symbols with symbol, description, and unit columns |
| `numberlong` | glossary_style | Custom glossary style for constants with symbol, description, value, and unit columns |
| `custom-base` | glossary_style | Base glossary style extending long-name-desc-loc with removed header |
| `subscripts` | glossary_type | Custom glossary type for subscript entries |
| `notprinted` | glossary_type | Glossary type for entries that should not appear in printed output |

## omnilatex-graphics

Image handling, SVG support, graphics paths, contour text, and TikZ+SVG debug helpers.

### Commands

| Command | Signature | Description |
|---------|-----------|-------------|
| `\ctrw` | `{text}` | Black text with white contour outline for legibility on noisy backgrounds |
| `\ctrb` | `{text}` | White text with black contour outline for legibility on noisy backgrounds |
| `\debugtikzsvg` | | Debug overlay for TikZ+SVG alignment: draws grid and position labels over an image node |
| `\mtlbsmlkicon` | `{icon_name}` | Include and scale a MATLAB/Simulink icon from assets/logos/matlab_simulink/ to height of capital X |

## omnilatex-hyperref

Hyperlinks, PDF metadata, bookmarks, cross-references with cleveref, and git metadata integration.

### Commands

| Command | Signature | Description |
|---------|-----------|-------------|
| `\GitRefName` | | Current git reference name (branch/tag), provided by git-metadata.lua or fallback 'n.a.' |
| `\GitShortSHA` | | Short git commit SHA, provided by git-metadata.lua or fallback 'n.a.' |
| `\GitLongSHA` | | Full git commit SHA, provided by git-metadata.lua or fallback 'n.a.' |
| `\GitRepositorySlug` | | Git repository slug, provided by git-metadata.lua or fallback 'n.a.' |
| `\GitProjectName` | | Git project name, provided by git-metadata.lua or fallback 'n.a.' |
| `\GitHostPagesURL` | | Git hosting pages URL, provided by git-metadata.lua or fallback 'n.a.' |
| `\GitHostAPIProvider` | | Git hosting API provider name, provided by git-metadata.lua or fallback 'n.a.' |
| `\GitHostAPIBase` | | Git hosting API base URL, provided by git-metadata.lua or fallback 'n.a.' |
| `\BuildDate` | | Build date, defaults to \today |
| `\BuildDatePDF` | | Build date in PDF format for deterministic metadata |
| `ifboldPDFchapters` | | Boolean conditional controlling whether chapter-level PDF bookmarks are bold |

## omnilatex-i18n

Internationalization: Polyglossia language setup and bilingual (English/German) translations for all UI strings.

### Translations

| Name | Description |
|------|-------------|
| `First` | English: \nth{1}, German: 1. |
| `Second` | English: \nth{2}, German: 2. |
| `Examiner` | English: Examiner, German: Prüfer:in |
| `Supervisor` | English: Supervisor, German: Betreuer:in |
| `CompiledOn` | English: Compiled on, German: Kompiliert am |
| `CensorNotice` | English: CENSORED VERSION, German: ZENSIERTE VERSION |
| `AuthorshipDeclTitle` | English: Declaration of Authorship, German: Erklärung zur Eigenständigkeit |
| `AuthorshipDeclText` | Full declaration of authorship text in both languages |
| `Reaction` | English: Reaction, German: Reaktion |
| `Gloss` | English: Glossary, German: Glossar |
| `BlankPage` | English: Rest of this page intentionally left blank, German: Rest der Seite absichtlich freigelassen |
| `Listing` | English: Code Listing, German: Code |
| `Example` | English: Example, German: Beispiel |
| `Contfoot` | English: Continued on next page, German: Fortgeführt auf der nächsten Seite |
| `Conthead` | English: (Continued), German: (Fortgesetzt) |
| `FurtherReadingTitle` | English: Further Reading, German: Weitere Literatur |
| `Constant` | English: const, German: konst |
| `Unit` | English: Unit, German: Einh. |
| `AdaptedFrom` | English: Adapted from, German: Adaptiert von |

## omnilatex-koma

KOMA-Script customization: chapter formatting, title page styles (thesis/book/TUHH), and TOC configuration.

### Commands

| Command | Signature | Description |
|---------|-----------|-------------|
| `\maketitle` | | Renewed maketitle that renders a custom title page based on omnilatex@titlestyle (thesis/book/TUHH) |

### Other Exports

| Name | Type | Description |
|------|------|-------------|
| `documenttype` | komafont | KOMA font for the document type label on the title page |
| `example` | toc_type | New TOC type 'example' with listname from translations, creating \listofexamples |

## omnilatex-lists

List configuration and custom list environments for standard and compact (table) usage.

### Environments

| Name | Description |
|------|-------------|
| `tabitemize` | Compact single-level itemize list for table cells with no vertical spacing |
| `tabenum` | Compact single-level enumerate list for table cells with no vertical spacing |
| `enumdescript` | Enumerated description list with auto-numbered bold labels (a., b., ...) |

### Other Exports

| Name | Type | Description |
|------|------|-------------|
| `descriptcount` | counter | Counter for enumerated description list items |

## omnilatex-listings

Source code highlighting with minted: configuration, listing environments, and code annotation commands.

### Commands

| Command | Signature | Description |
|---------|-----------|-------------|
| `\emptyaccsupp` | `{content}` | Wraps content with empty ActualText for PDF accessibility (invisible to screen readers) |
| `\phstring` | `{text}` | Highlights text as a string placeholder in red (cRed) |
| `\phnum` | `{text}` | Highlights text as a numeric placeholder in blue (cBlue) |
| `\phother` | `{text}` | Highlights text as other placeholder in green (cGreen) |
| `\phnote` | `{text}` | Highlights text as annotation note in bold orange (cOrange) |

### Environments

| Name | Description |
|------|-------------|
| `longlisting` | Environment for long code listings using captionsetup with type=listing |

## omnilatex-math

Mathematical typesetting: delimiters, chemistry, units, operators, derivatives, statistical/physical notation.

### Commands

| Command | Signature | Description |
|---------|-----------|-------------|
| `\parens` | `{content}` | Auto-scaling paired delimiter for parentheses; starred variant scales with \left/\right |
| `\brackets` | `{content}` | Auto-scaling paired delimiter for square brackets; starred variant scales |
| `\braces` | `{content}` | Auto-scaling paired delimiter for curly braces; starred variant scales |
| `\eqend` | | Inserts comma-period with thin space to end a display equation |
| `\eqcomma` | | Inserts comma with thin space for mid-equation punctuation |
| `\grad` | | Upright 'grad' math operator via DeclareMathOperator |
| `\const` | | Upright 'const.' notation for constant expressions, language-aware |
| `\qq` | `{text}` | Quick quad: inserts \quad\text{#1}\quad for text between equation parts |
| `\chemamount` | `{quantity}{unit}{substance}` | Unified markup for '1.2 ppm CO2' constructs with correct spacing |
| `\circlednum` | `{number}` | Renders a number inside a circle using TikZ circlednum style |
| `\symbolplaceholder` | | Prints a raised dottedsquare as a placeholder for symbols |
| `\meanfmt` | `{variable}` | Mean value formatting: horizontal overbar with adjusted kerning |
| `\mean` | `{variable}` | Mean value with overbar, linked to glossary entry sym.mean |
| `\logmeanfmt` | `{variable}` | Logarithmic mean formatting: tilde over variable |
| `\logmean` | `{variable}` | Logarithmic mean with tilde, linked to glossary entry sym.logmean |
| `\absfmt` | `{content}` | Absolute value paired delimiter using \lvert/\rvert |
| `\abs` | `{content}` | Absolute value with auto-scaling, linked to glossary entry sym.abs |
| `\flowfmt` | `{variable}` | Dotted symbol formatting for flow quantities |
| `\flow` | `{variable}` | Flow notation with dot, linked to glossary entry sym.flow |
| `\differencefmt` | `{variable}` | Delta/difference formatting |
| `\difference` | `{variable}` | Delta notation, linked to glossary entry sym.difference |
| `\nablaoperatorfmt` | `{variable}` | Nabla operator formatting |
| `\nablaoperator` | `[degree]{variable}` | Nabla wrapper with optional degree, linked to glossary entry sym.nabla |
| `\heatexentryfmt` | `{variable}` | Heat exchanger entry formatting (prime suffix) |
| `\heatexentry` | `{variable}` | Heat exchanger entry notation, linked to glossary entry sym.heatexentry |
| `\heatexexitfmt` | `{variable}` | Heat exchanger exit formatting (double-prime suffix) |
| `\heatexexit` | `{variable}` | Heat exchanger exit notation, linked to glossary entry sym.heatexexit |
| `\vectfmt` | `{variable}` | Vector formatting using bold symbol |
| `\vect` | `{variable}` | Vector notation with bold symbol, linked to glossary entry sym.vector |
| `\derivativefmt` | `{variable}` | Upright d derivative formatting |
| `\partialderivativefmt` | `{variable}` | Partial derivative formatting |
| `\deriv` | `[degree]{variable}` | Derivative notation, linked to glossary entry sym.derivative |
| `\deriv*` | `[degree]{variable}` | Partial derivative notation (starred variant), linked to sym.partial_derivative |
| `\fracderiv` | `[degree]{numerator}{denominator}` | Derivative fraction notation |
| `\fracderiv*` | `[degree]{numerator}{denominator}` | Partial derivative fraction notation (starred variant) |
| `\timederiv` | `[degree]{variable}` | Time derivative fraction, denominator is time symbol |
| `\timederiv*` | `[degree]{variable}` | Partial time derivative fraction |
| `\posderiv` | `[degree]{variable}` | Positional derivative fraction, denominator is first Cartesian coordinate |
| `\posderiv*` | `[degree]{variable}` | Partial positional derivative fraction |
| `\temperaturepair` | `{temp1}{temp2}` | Prints temperature range like 45/55 degC using siunitx |

### Environments

| Name | Description |
|------|-------------|
| `reactionsgather` | Chemistry reaction environment like AMSmath gather, with R-tag and equation numbering |
| `reactionsgather*` | Unnumbered chemistry reaction gather environment |

## omnilatex-page

Page layout: headers, footers, page styles using SCRLayer, and deliberately blank page handling.

### Commands

| Command | Signature | Description |
|---------|-----------|-------------|
| `\headerrulelength` | | Length controlling the height of the vertical header rule |
| `\headerrule` | | Draws a vertical rule in the header with height set by \headerrulelength |
| `\blankpage` | | Typesets a centered message on deliberately blank pages using translated BlankPage text |

### Other Exports

| Name | Type | Description |
|------|------|-------------|
| `blank` | pagestyle | Page style for deliberately blank pages, registered as cleardoublepage style |

## omnilatex-tables

Table formatting: booktabs, tabularray, custom column types, and helper commands for rotated multi-row cells.

### Commands

| Command | Signature | Description |
|---------|-----------|-------------|
| `\multirotatecell` | `{rows}{text}` | Rotates text 90 degrees and wraps it in a multirow spanning the given number of rows |

### Other Exports

| Name | Type | Description |
|------|------|-------------|
| `M` | column_type | Centered paragraph column of specified width |

## omnilatex-tikz-core

TikZ/PGFPlots core configuration: libraries, plot cycle lists, global plot settings, and reusable styles.

### Commands

| Command | Signature | Description |
|---------|-----------|-------------|
| `\parsenode` | `[options]text\pgf@nil` | Internal helper for add node at x style: parses label options and text |

### Styles

| Name | Signature | Description |
|------|-----------|-------------|
| `regularplot` | | PGFPlots style for a broadly usable regular plot with grids, thick lines, outside ticks |
| `plainplot` | | PGFPlots style for a clean plot without numerical labels or ticks |
| `tuftelike` | | PGFPlots style inspired by Tufte: minimal ticks, shifted axis lines |
| `arrowplot` | `{arrow_spec}` | PGFPlots style that decorates a path with repeated arrows along its length |
| `log x ticks with fixed point` | | PGFPlots style for logarithmic x-axis with fixed-point labels instead of scientific notation |
| `log y ticks with fixed point` | | PGFPlots style for logarithmic y-axis with fixed-point labels instead of scientific notation |

## omnilatex-tikz-engineering

Engineering shapes, technical diagrams, custom PGF node shapes, and TikZ styles for thermodynamic/mechanical drawings.

### Styles

| Name | Signature | Description |
|------|-----------|-------------|
| `startstop` | | Flow chart style: rounded rectangle, red fill, for start/stop nodes |
| `io` | | Flow chart style: ellipse, blue fill, for input/output nodes |
| `process` | | Flow chart style: rectangle, orange fill, for process nodes |
| `decision` | | Flow chart style: signal shape, green fill, for decision nodes |
| `arrow` | | Flow chart style: thick arrow with stealth tip |
| `symmetrycross` | `[size]` | Rotated cross-out to mark symmetry center in technical drawings |
| `pipecrosssection` | `[size]` | Circle simulating a pipe cross-section with thick border and MediumFluid fill |
| `arrowlabel` | `[position]` | Label style for positioning text along arrows with white background |
| `wall` | `[fill_color]` | Wall style for cross-sections: thick, drawn, with rounded corners |
| `fluid` | `[fill_color]` | Fluid fill style, default MediumFluid |
| `flowarrow` | `{inverse_frequency}{amplitude}` | Squiggly dashed arrow style for flow visualization using snake decoration |
| `annotationarrow` | | Arrow style with thick dot at end, for annotation pointing |
| `origindot` | `[fill_color]` | Small filled circle for coordinate origins |
| `add node at x` | `{x_position}{label_text}` | Place a labeled node at a given x-position on a plot, computing y automatically |
| `shorten <>` | `{length}` | Shorten both ends of a path simultaneously |
| `circlednum` | | Circle shape with draw, white fill, used for circled numbers |
| `boilercylinder` | | Cylinder shape styled as a boiler with shading |
| `equalizing tank` | `[size]` | Circle split node styled as an equalizing tank |
| `pipe` | `[width]` | Double-line pipe style with MediumFluid fill and triangle arrow caps |
| `valve` | `[size]` | Valve node style using custom valve shape, white fill, rotated 90deg |
| `control valve` | `[size]` | Control valve style with semicircle control wheel extension |
| `threeway valve` | `[size]` | Three-way valve style with asymmetrical port layout |
| `fourway valve` | `[size]` | Four-way valve style with symmetrical cross-pattern |
| `threeway control valve` | | Three-way control valve combining threeway valve and control valve features |
| `radiator` | `[size]` | Radiator node style with 3D front/top/right surfaces and vertical slats |
| `vented radiator` | | Radiator with ventilation outlet on top-left corner |
| `pump` | `[size]` | Pump node style: circle with internal triangle |
| `compressor` | `[size]` | Compressor node style: circle with internal zigzag pattern |
| `heat exchanger` | `[size]` | Heat exchanger node with triangle heat symbol and in/out anchors |
| `simple heat exchanger` | `[size]` | Simple heat exchanger: rectangle with diagonal cross |
| `sensor` | `[size]` | Sensor node: vertical stroke with three decreasing horizontal lines |
| `level indicator` | `[size]` | Level indicator: inverted triangle with three decreasing horizontal lines |

### Pics

| Name | Description |
|------|-------------|
| `radiator` | Detailed 3D radiator pic with front/top/right surfaces and named coordinates |
| `TUHHuman` | Stylized human figure pic with TUHH chest emblem |
| `boiler` | Boiler pic using boilercylinder style with contoured text |

## omnilatex-typesetting

Typography helpers: hyphenation, microtype, line spacing, quotation support, and ragged-right text.

### Commands

| Command | Signature | Description |
|---------|-----------|-------------|
| `\mkbegdispquote` | | Renewed to add italic shape at the beginning of display quote environments |

## omnilatex-utils

System utilities, TODO notes, git metadata, keyboard macros, censoring, and miscellaneous packages.

### Commands

| Command | Signature | Description |
|---------|-----------|-------------|
| `\fakeverb` | `{content}` | Typesets argument in ttfont with detokenize, useful for showing verbatim-like text |
