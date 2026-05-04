#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

OUTPUT_DIR="$REPO_ROOT/build/overleaf-zips"
mkdir -p "$OUTPUT_DIR"

EXAMPLES_DIR="$REPO_ROOT/examples"
TOTAL=0
SUCCESS=0
FAILED=0

echo "=== OmniLaTeX Overleaf Zip Generator (All Examples) ==="
echo ""

for example_dir in "$EXAMPLES_DIR"/*/; do
    example_name="$(basename "$example_dir")"

    if [ ! -f "$example_dir/main.tex" ]; then
        echo "[SKIP] $example_name (no main.tex)"
        continue
    fi

    TOTAL=$((TOTAL + 1))

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

    cp "$example_dir/main.tex" "$PKG_DIR/main.tex"

    if [ -d "$example_dir/config" ]; then
        cp -r "$example_dir/config/." "$PKG_DIR/config/" 2>/dev/null || true
    fi

    sed -i 's|\.\./\.\./omnilatex|omnilatex|g' "$PKG_DIR/main.tex"
    sed -i 's|\.\./\.\./bib/|bib/|g' "$PKG_DIR/main.tex"
    sed -i 's|\.\./bib/|bib/|g' "$PKG_DIR/main.tex"

    cat > "$PKG_DIR/README.md" <<'OVERLEAF_README'
# OmniLaTeX on Overleaf

A modular, engineering-grade LaTeX document class.

## Setup

1. Upload this zip to Overleaf (Menu -> New Project -> Upload Project)
2. Set compiler to **LuaLaTeX** (Menu -> Compiler -> LuaLaTeX)
3. Click **Recompile**
OVERLEAF_README

    find "$PKG_DIR" -name "*.aux" -o -name "*.log" -o -name "*.pdf" \
      -o -name "*.fdb_*" -o -name "*.fls" -o -name "*.synctex.gz" \
      -o -name "__pycache__" -o -name ".git" -type d \
      -exec rm -rf {} + 2>/dev/null || true

    OUTPUT_ZIP="$OUTPUT_DIR/${example_name}.zip"

    if (cd "$TMPDIR" && zip -r "$OUTPUT_ZIP" omnilatex-overleaf/ -q); then
        SIZE=$(du -sh "$OUTPUT_ZIP" | cut -f1)
        echo "[OK]   $example_name ($SIZE)"
        SUCCESS=$((SUCCESS + 1))
    else
        echo "[FAIL] $example_name"
        FAILED=$((FAILED + 1))
    fi

    rm -rf "$TMPDIR"
    trap - EXIT
done

echo ""
echo "=== Summary ==="
echo "Total:  $TOTAL"
echo "Success: $SUCCESS"
echo "Failed: $FAILED"
echo "Output:  $OUTPUT_DIR/"
