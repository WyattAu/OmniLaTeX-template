#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

EXAMPLES_DIR="$REPO_ROOT/examples"
ZIP_SCRIPT="$SCRIPT_DIR/make-overleaf-zip.sh"

PASS=0
FAIL=0
SKIP=0
RESULTS=()

echo "=== Overleaf Zip Validation for Gallery Submission ==="
echo ""

if [ ! -d "$EXAMPLES_DIR" ]; then
    echo "Error: examples directory not found at $EXAMPLES_DIR"
    exit 1
fi

validate_zip() {
    local zip_path="$1"
    local example_name="$2"

    if ! unzip -l "$zip_path" | grep -q 'main\.tex$'; then
        echo "  [FAIL] missing main.tex"
        return 1
    fi

    if ! unzip -l "$zip_path" | grep -q 'omnilatex\.cls$'; then
        echo "  [FAIL] missing omnilatex.cls"
        return 1
    fi

    if ! unzip -l "$zip_path" | grep -q '\.sty'; then
        echo "  [FAIL] no .sty files found"
        return 1
    fi

    local main_tex_content
    main_tex_content="$(unzip -p "$zip_path" "*/main.tex" 2>/dev/null || unzip -p "$zip_path" "main.tex" 2>/dev/null)"

    if ! echo "$main_tex_content" | grep -qP '\\documentclass.*\{omnilatex\}'; then
        echo "  [FAIL] main.tex missing \\documentclass referencing omnilatex"
        return 1
    fi

    return 0
}

for example_dir in "$EXAMPLES_DIR"/*/; do
    example_name="$(basename "$example_dir")"

    if [ ! -f "$example_dir/main.tex" ]; then
        echo "[SKIP] $example_name (no main.tex)"
        SKIP=$((SKIP + 1))
        RESULTS+=("SKIP $example_name")
        continue
    fi

    echo "[TEST] $example_name"

    TMPDIR="$(mktemp -d)"
    trap 'rm -rf "$TMPDIR"' EXIT

    "$ZIP_SCRIPT" "$example_name" > /dev/null 2>&1
    zip_path="$REPO_ROOT/omnilatex-overleaf.zip"

    if [ ! -f "$zip_path" ]; then
        echo "  [FAIL] zip was not created"
        FAIL=$((FAIL + 1))
        RESULTS+=("FAIL $example_name (zip not created)")
        rm -rf "$TMPDIR"
        trap - EXIT
        continue
    fi

    cp "$zip_path" "$TMPDIR/validate.zip"
    rm -f "$zip_path"

    if validate_zip "$TMPDIR/validate.zip" "$example_name"; then
        echo "  [PASS] all checks passed"
        PASS=$((PASS + 1))
        RESULTS+=("PASS $example_name")
    else
        FAIL=$((FAIL + 1))
        RESULTS+=("FAIL $example_name")
    fi

    rm -rf "$TMPDIR"
    trap - EXIT
done

echo ""
echo "=== Summary ==="
TOTAL=$((PASS + FAIL))
for result in "${RESULTS[@]}"; do
    echo "  $result"
done
echo ""
echo "Passed:  $PASS/$TOTAL"
echo "Failed:  $FAIL/$TOTAL"
echo "Skipped: $SKIP"

if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
