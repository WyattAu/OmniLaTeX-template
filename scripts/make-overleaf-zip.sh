#!/usr/bin/env bash
# Build a self-contained Overleaf-compatible zip from the OmniLaTeX repository.
#
# Usage:
#   bash scripts/make-overleaf-zip.sh [--output PATH]
#
# The zip contains everything needed to compile on Overleaf with LuaLaTeX:
#   - omnilatex.cls
#   - lib/ (all 27 modules across 9 subdirectories)
#   - config/ (document types, settings, 14 institution configs)
#   - lua/ (git-metadata.lua)
#   - examples/ (citation-styles, color-themes)
#   - Minimal main.tex with instructions
#
# NOT included (Overleaf doesn't need these):
#   - build.py, build.lua, .latexmkrc, flake.nix
#   - tests/, specs/, docs/
#   - other examples/ (use the full repo instead)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUTPUT="${1:-$REPO_ROOT/overleaf/omnilatex-overleaf.zip}"
TMPDIR="$(mktemp -d)"

trap 'rm -rf "$TMPDIR"' EXIT

echo "Building Overleaf zip..."

# Core class
cp "$REPO_ROOT/omnilatex.cls" "$TMPDIR/"

# Modules (all subdirectories: code, core, graphics, language, layout,
#          references, tables, typography, utils)
cp -r "$REPO_ROOT/lib" "$TMPDIR/"

# Config (document types + settings + all 14 institution configs)
mkdir -p "$TMPDIR/config/document-types"
cp -r "$REPO_ROOT/config/document-types/"*.sty "$TMPDIR/config/document-types/"
cp "$REPO_ROOT/config/document-settings.sty" "$TMPDIR/config/" 2>/dev/null || true
cp -r "$REPO_ROOT/config/institutions" "$TMPDIR/config/institutions"

# Lua scripts
mkdir -p "$TMPDIR/lua"
cp "$REPO_ROOT/lua/"*.lua "$TMPDIR/lua/" 2>/dev/null || true

# Sample bibliography
mkdir -p "$TMPDIR/bib"
if [ -f "$REPO_ROOT/examples/minimal-starter/bib/bibliography.bib" ]; then
  cp "$REPO_ROOT/examples/minimal-starter/bib/bibliography.bib" "$TMPDIR/bib/"
fi

# ── Select examples ──────────────────────────────────────
# citation-styles
if [ -d "$REPO_ROOT/examples/citation-styles" ]; then
  mkdir -p "$TMPDIR/examples/citation-styles"
  cp "$REPO_ROOT/examples/citation-styles/main.tex" "$TMPDIR/examples/citation-styles/"
  cp "$REPO_ROOT/examples/citation-styles/refs.bib"  "$TMPDIR/examples/citation-styles/"
fi

# color-themes
if [ -d "$REPO_ROOT/examples/color-themes" ]; then
  mkdir -p "$TMPDIR/examples/color-themes"
  cp "$REPO_ROOT/examples/color-themes/main.tex" "$TMPDIR/examples/color-themes/"
fi

# Sample assets (images only, no logos needed for generic template)
mkdir -p "$TMPDIR/assets/images"
if [ -f "$REPO_ROOT/examples/minimal-starter/assets/images/bitmaps/field.jpg" ]; then
  cp "$REPO_ROOT/examples/minimal-starter/assets/images/bitmaps/field.jpg" "$TMPDIR/assets/images/"
fi

# Minimal main.tex
cat > "$TMPDIR/main.tex" << 'TEXEOF'
% OmniLaTeX — Overleaf Template
% Compile with: LuaLaTeX (set in Overleaf menu: Menu → Compiler → LuaLaTeX)
%
% This is a minimal starter template. For more examples, see:
% https://github.com/WyattAu/OmniLaTeX-template/tree/main/examples

\documentclass[
  doctype=article,
  language=english,
]{omnilatex}

% ── Metadata ──────────────────────────────────────────
\title{My Document Title}
\author{Author Name}
\date{\today}

\begin{document}

\maketitle
\tableofcontents

\section{Introduction}

OmniLaTeX is a modular document class for academic and professional documents.

\subsection{Features}

\begin{itemize}
  \item 55 doctype aliases (thesis, CV, patent, journal, \ldots)
  \item 16 document profiles across 3 KOMA-Script base classes
  \item 14 institution configs (TUHH, MIT, Stanford, ETH, \ldots)
  \item Modern font stack with graceful fallbacks
  \item CJK support: Chinese, Japanese, Korean
  \item 9 citation styles (IEEE, ACM, APA, Nature, \ldots)
  \item 6 color themes with dark/light mode
  \item Code listings with syntax highlighting
  \item Mathematical typesetting with unicode-math
  \item TikZ graphics and engineering diagrams
  \item Bibliography management with biblatex
  \item Glossaries with bib2gls
\end{itemize}

\section{Math Example}

\begin{equation}
  E = mc^2
  \label{eq:einstein}
\end{equation}

The fundamental relation between energy and mass, as shown in
Equation~\ref{eq:einstein}.

\section{Code Listing}

\begin{listing}[H]
\begin{minted}{python}
def fibonacci(n: int) -> list[int]:
    """Compute the first n Fibonacci numbers."""
    a, b = 0, 1
    result = []
    for _ in range(n):
        result.append(a)
        a, b = b, a + b
    return result

print(fibonacci(10))
\end{minted}
\caption{Fibonacci sequence in Python}
\end{listing}

\section{Table}

\begin{table}[H]
\centering
\begin{tabular}{lcc}
  \toprule
  \textbf{Document Type} & \textbf{Base Class} & \textbf{Sides} \\
  \midrule
  Thesis        & scrbook  & Two-sided \\
  Article       & scrartcl & One-sided  \\
  CV            & scrartcl & One-sided  \\
  Technical Report & scrreprt & Two-sided \\
  \bottomrule
\end{tabular}
\caption{Sample document types}
\end{table}

\section{Figure}

\begin{figure}[H]
  \centering
  \includegraphics[width=0.6\textwidth]{assets/images/field.jpg}
  \caption{Sample image}
\end{figure}

% ── Bibliography ─────────────────────────────────────
% Uncomment to enable bibliography:
% \printbibliography[heading=bibintoc]

\end{document}
TEXEOF

# README for Overleaf users
cat > "$TMPDIR/README.md" << 'MDEOF'
# OmniLaTeX on Overleaf

## Setup

1. Set the compiler to **LuaLaTeX**: Menu → Compiler → LuaLaTeX
2. Click **Recompile**

## Customization

Change the document type in `main.tex`:

```latex
\documentclass[doctype=thesis]{omnilatex}     % Academic thesis
\documentclass[doctype=cv]{omnilatex}          % CV
\documentclass[doctype=report]{omnilatex}      % Report
```

### Institution Configs (14 available)

```latex
\documentclass[institution=tuhh]{omnilatex}    % TUHH
\documentclass[institution=mit]{omnilatex}     % MIT
\documentclass[institution=stanford]{omnilatex}% Stanford
```

Full list: tuhh, tum, eth, mit, stanford, cambridge, tudelft, oxford,
princeton, yale, cmu, epfl, imperial, generic

### Citation Styles (9 available)

```latex
\citationstyle{ieee}    % IEEE
\citationstyle{apa}     % APA
\citationstyle{nature}  % Nature
```

Full list: ieee, acm, apa, chicago, nature, science, harvard,
vancouver, mla

See `examples/citation-styles/` for a demo.

### Color Themes (6 + dark variants)

```latex
\usetheme{default}        % Clean white, blue accents
\usetheme{midnight}       % Dark navy, cyan accents
\usetheme{monochrome-dark}% Dark mode, no color
```

Full list: default, midnight, forest, rose, monochrome, sepia

See `examples/color-themes/` for a visual comparison.

## Full Documentation

- GitHub: https://github.com/WyattAu/OmniLaTeX-template
- All 24 examples: https://github.com/WyattAu/OmniLaTeX-template/tree/main/examples
MDEOF

# Create zip
mkdir -p "$(dirname "$OUTPUT")"
(cd "$TMPDIR" && zip -r "$OUTPUT" . -x '*.aux' '*.log' '*.out' '*.toc')

SIZE=$(du -h "$OUTPUT" | cut -f1)
echo ""
echo "✓ Created: $OUTPUT ($SIZE)"
echo ""
echo "To use on Overleaf:"
echo "  1. Go to https://www.overleaf.com/project"
echo "  2. Click 'Upload Project'"
echo "  3. Upload the zip file"
echo "  4. Set compiler to LuaLaTeX"
echo "  5. Recompile"
