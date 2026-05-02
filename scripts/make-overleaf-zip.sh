#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

EXAMPLE_NAME="${1:-thesis}"
EXAMPLE_DIR="$REPO_ROOT/examples/$EXAMPLE_NAME"

if [ ! -d "$EXAMPLE_DIR" ]; then
    echo "Error: example '$EXAMPLE_NAME' not found at $EXAMPLE_DIR"
    echo "Available examples:"
    ls "$REPO_ROOT/examples/" | grep -v '^\.' | sed 's/^/  /'
    exit 1
fi

if [ ! -f "$EXAMPLE_DIR/main.tex" ]; then
    echo "Error: main.tex not found in $EXAMPLE_DIR"
    exit 1
fi

TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT

PKG_DIR="$TMPDIR/omnilatex-overleaf"
mkdir -p "$PKG_DIR"

cp "$REPO_ROOT/omnilatex.cls" "$PKG_DIR/"

cp -r "$REPO_ROOT/lib" "$PKG_DIR/lib"

mkdir -p "$PKG_DIR/config/document-types"
cp "$REPO_ROOT/config/document-settings.sty" "$PKG_DIR/config/" 2>/dev/null || true
cp -r "$REPO_ROOT/config/document-types/." "$PKG_DIR/config/document-types/"

mkdir -p "$PKG_DIR/bib"
cp -r "$REPO_ROOT/bib/." "$PKG_DIR/bib/"

cp "$EXAMPLE_DIR/main.tex" "$PKG_DIR/main.tex"

if [ -d "$EXAMPLE_DIR/config" ]; then
    cp -r "$EXAMPLE_DIR/config/." "$PKG_DIR/config/" 2>/dev/null || true
fi

sed -i 's|\.\./\.\./omnilatex|omnilatex|g' "$PKG_DIR/main.tex"
sed -i 's|\.\./\.\./bib/|bib/|g' "$PKG_DIR/main.tex"
sed -i 's|\.\./bib/|bib/|g' "$PKG_DIR/main.tex"

cat > "$PKG_DIR/README.md" <<'OVERLEAF_README'
# OmniLaTeX on Overleaf

A modular, engineering-grade LaTeX document class.

## Setup

1. Upload this zip to Overleaf (Menu → New Project → Upload Project)
2. Set compiler to **LuaLaTeX** (Menu → Compiler → LuaLaTeX)
3. Click **Recompile**

## Directory Structure

```
main.tex              Your document (edit this)
omnilatex.cls         Document class
lib/                  Module library (do not edit)
config/               Document settings
bib/                  Bibliography files
```

## Customization

Edit `\documentclass` options in `main.tex`:

```latex
\documentclass[doctype=thesis, language=english]{omnilatex}
```

See the full documentation at https://github.com/WyattAu/OmniLaTeX-template
OVERLEAF_README

find "$PKG_DIR" -name "*.aux" -o -name "*.log" -o -name "*.pdf" \
  -o -name "*.fdb_*" -o -name "*.fls" -o -name "*.synctex.gz" \
  -o -name "__pycache__" -o -name ".git" -type d \
  -exec rm -rf {} + 2>/dev/null || true

cd "$TMPDIR"
zip -r "$REPO_ROOT/omnilatex-overleaf.zip" omnilatex-overleaf/

SIZE=$(du -sh "$REPO_ROOT/omnilatex-overleaf.zip" | cut -f1)
echo "Created omnilatex-overleaf.zip ($SIZE) from example: $EXAMPLE_NAME"
echo "Location: $REPO_ROOT/omnilatex-overleaf.zip"
echo ""
echo "Contents:"
unzip -l "$REPO_ROOT/omnilatex-overleaf.zip" | tail -5
