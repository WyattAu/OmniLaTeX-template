#!/usr/bin/env bash
# Build a self-contained Overleaf-compatible zip from the OmniLaTeX repository.
#
# Usage:
#   bash scripts/make-overleaf-zip.sh [--output PATH]
#
# The zip contains everything needed to compile on Overleaf with LuaLaTeX:
#   - omnilatex.cls
#   - lib/ (all 21 modules)
#   - config/ (document types, settings)
#   - lua/ (git-metadata.lua)
#   - Minimal main.tex with instructions
#
# NOT included (Overleaf doesn't need these):
#   - build.py, build.lua, .latexmkrc, flake.nix
#   - tests/, specs/, docs/
#   - examples/ (use the generated template instead)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUTPUT="${1:-overleaf/omnilatex-overleaf.zip}"
TMPDIR="$(mktemp -d)"

trap 'rm -rf "$TMPDIR"' EXIT

echo "Building Overleaf zip..."

# Core class
cp "$REPO_ROOT/omnilatex.cls" "$TMPDIR/"

# Modules
cp -r "$REPO_ROOT/lib" "$TMPDIR/"

# Config (document types + settings, no institutions)
mkdir -p "$TMPDIR/config/document-types"
cp -r "$REPO_ROOT/config/document-types/"*.sty "$TMPDIR/config/document-types/"
cp "$REPO_ROOT/config/document-settings.sty" "$TMPDIR/config/" 2>/dev/null || true

# Lua scripts
mkdir -p "$TMPDIR/lua"
cp "$REPO_ROOT/lua/"*.lua "$TMPDIR/lua/" 2>/dev/null || true

# Sample bibliography
mkdir -p "$TMPDIR/bib"
if [ -f "$REPO_ROOT/examples/minimal-starter/bib/bibliography.bib" ]; then
  cp "$REPO_ROOT/examples/minimal-starter/bib/bibliography.bib" "$TMPDIR/bib/"
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
  \item 46 doctype aliases (thesis, CV, patent, journal, \ldots)
  \item Modern font stack with graceful fallbacks
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

## Full Documentation

- GitHub: https://github.com/WyattAu/OmniLaTeX-template
- All 20 examples: https://github.com/WyattAu/OmniLaTeX-template/tree/main/examples
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
