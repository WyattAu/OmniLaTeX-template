# OmniLaTeX Accessibility Guide

OmniLaTeX supports generating tagged PDFs compliant with PDF/UA-1,
the ISO standard for accessible PDF documents. Tagged PDFs are readable
by assistive technologies such as screen readers.

## Quick Start

Add these lines **before** your `\documentclass`:

```latex
\RequirePackage{pdfmanagement-testphase}
\DocumentMetadata{lang=english, pdfversion=2.0}

\documentclass[doctype=article]{omnilatex}

\RequirePackage{config/document-settings}
\RequirePackage{lib/layout/omnilatex-accessibility}
```

Compile with LuaLaTeX:

```bash
lualatex main.tex
```

## How It Works

1. `pdfmanagement-testphase` activates LuaTeX's PDF resource management layer.
2. `\DocumentMetadata` sets PDF metadata (language, version) required for PDF/UA-1.
3. `omnilatex-accessibility.sty` loads `tagpdf` and configures PDF tagging.

### Requirements

- LuaLaTeX engine (already required by OmniLaTeX)
- `tagpdf` package (TeX Live 2024+)
- `pdfmanagement-testphase` package (TeX Live 2020+)

## Alt Text for Figures

WCAG 2.1 AA criterion 1.1.1 requires all non-text content to have text
alternatives. Use `\alttext{description}` before a figure environment:

```latex
\alttext{A scatter plot comparing temperature vs. energy output}
\begin{figure}[htbp]
    \centering
    \includegraphics[width=0.8\textwidth]{chart.pdf}
    \caption{Temperature vs. energy output}
\end{figure}
```

### Alt Text for TikZ Pictures

Use `\tikzalttext{description}` before a `tikzpicture` environment:

```latex
\tikzalttext{A finite state machine with three states: idle, active, done}
\begin{tikzpicture}
    % ...
\end{tikzpicture}
```

## Accessible Links

WCAG 2.1 AA criterion 2.4.4 requires that the purpose of each link can be
determined from the link text alone (or from the link text together with its
programmatically determined link context). Use `\accessiblelink` to provide
a screen reader description:

```latex
\accessiblelink{Visit OmniLaTeX}{https://github.com/WyattAu/OmniLaTeX-template}{Opens the OmniLaTeX GitHub repository}
```

The third argument is shown as a tooltip and read by screen readers.

## Table Accessibility

WCAG 2.1 AA criterion 1.3.1 requires tables to have proper header markup.
The accessibility module automatically tags `tabular` environments with
`role=table`. Ensure you use `\textbf` or semantic markup in the header row:

```latex
\begin{tabular}{lc}
    \toprule
    \textbf{Name} & \textbf{Score} \\
    \midrule
    Alice & 95 \\
    Bob   & 87 \\
    \bottomrule
\end{tabular}
```

## Heading Hierarchy

WCAG 2.1 AA criterion 1.3.1 requires heading levels to be nested correctly
without skipping levels (e.g., H1 → H2 → H3, not H1 → H3).

Use `\validatstructure` at the end of your document to log a structural
check. In OmniLaTeX, `\section` maps to H1, `\subsection` to H2, and so on.

Best practices:
- Use `\section` for top-level headings.
- Use `\subsection` for sub-headings within a section.
- Do not skip from `\section` to `\subsubsection`.

## Color Contrast

WCAG 2.1 AA criterion 1.4.3 requires a contrast ratio of at least 4.5:1
for normal text and 3:1 for large text (18pt+ or 14pt+ bold).

Use `\checkcontrast{background}{foreground}` to log an informational
reminder during compilation:

```latex
\checkcontrast{white}{darkblue}
```

This is an informative check only. Verify exact ratios with a tool such as
the [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/).

## Language Tagging

WCAG 2.1 AA criterion 3.1.2 requires that the human language of each passage
or phrase can be programmatically determined. Use `\langtag{code}{text}` for
passages in a language different from the document's main language:

```latex
\langtag{german}{Vielen Dank für Ihre Aufmerksamkeit}
\langtag{french}{Merci beaucoup}
```

Language codes follow ISO 639-1 (e.g., `en`, `de`, `fr`, `es`, `zh`, `ja`).

## Reading Order

PDF/UA-1 requires a logical reading order. For complex layouts (multi-column,
sidebars, pull quotes), use `\readingorder{n}` to hint at the intended
reading sequence:

```latex
\readingorder{1}
Main content here.

\readingorder{2}
Sidebar content here.
```

## Validation Tools

### PAC 2021 (PDF Accessibility Checker)

The [PAC 2021](https://www.pdf-accessibility.org/en/evaluation-tools.html)
tool from the PDF Association is the standard validator for PDF/UA-1.
It checks tagging, reading order, and metadata.

### Adobe Acrobat Accessibility Checker

Adobe Acrobat Pro includes a built-in accessibility checker:
**Tools > Accessibility > Full Check**.

### NVDA

[NVDA](https://www.nvaccess.org/) is a free, open-source screen reader for
Windows. Test your PDF by opening it in Adobe Reader and navigating with NVDA.

### JAWS

[JAWS](https://www.freedomscientific.com/products/software/jaws/) is a
commercial screen reader for Windows.

### VoiceOver

VoiceOver is built into macOS and iOS. Open the PDF in Preview or Adobe
Reader and navigate with VoiceOver (Cmd+F5).

## Known Limitations

- `tagpdf` is under active development; some complex layouts may produce
  tagging warnings.
- TikZ diagrams and complex floats may need manual tagging adjustments.
- For full PDF/UA-1 compliance, additional metadata (title, author, subject)
  should be set via `\DocumentMetadata`.
- Color contrast checking is informational only; no runtime pixel analysis
  is performed.
- Reading order hints may not be respected by all PDF viewers.
- `\pdftooltip` (used by `\accessiblelink`) requires the `pdfmanagement`
  layer and may not work in all PDF viewers.
