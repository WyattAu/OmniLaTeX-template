#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# CTAN Automated Upload Script
#
# Uploads omnilatex.zip to CTAN via their web form.
# Uses CTAN's own validation endpoints for pre-flight checks.
#
# Usage:
#   ./scripts/ctan-upload.sh <version> <zip-path> [options]
#
# Options:
#   --dry-run       Validate everything but don't submit
#   --email ADDR    Contact email (required, or set CTAN_EMAIL env)
#   --author NAME   Author name (default: "Wyatt Au")
#   --changelog TXT Announcement text
#
# Environment:
#   CTAN_EMAIL      Contact email for CTAN
#   CTAN_AUTHOR     Author/maintainer name
#
# Exit codes:
#   0  Success
#   1  Validation failure
#   2  CSRF token fetch failure
#   3  Pre-flight validation failure
#   4  Upload rejected by CTAN
#   5  Network error
# ---------------------------------------------------------------------------

set -euo pipefail

# ── Configuration ──────────────────────────────────────────────────────────
CTAN_BASE="https://ctan.org"
PKG_NAME="omnilatex"
CTAN_PATH="macros/latex/contrib/omnilatex"
LICENSE="apache2"
HOMEPAGE="https://github.com/WyattAu/OmniLaTeX-template"
BUG_TRACKER="https://github.com/WyattAu/OmniLaTeX-template/issues"
REPOSITORY="https://github.com/WyattAu/OmniLaTeX-template"
SUPPORT_URL="https://github.com/WyattAu/OmniLaTeX-template/discussions"
SUMMARY="Comprehensive KOMA-Script LaTeX template with 26 document types, 16 institutions, and 18 languages"
DESCRIPTION="OmniLaTeX is a comprehensive KOMA-Script-based LaTeX template providing 26 document types (thesis, dissertation, presentation, CV, white paper, invoice, recipe, and more), 16 institutional configurations, and support for 18 languages with full i18n. It uses a modular architecture with a single class file delegating to specialized modules for fonts, colors, floats, tables, and document types. Designed for both novice and advanced users with sensible defaults and extensive customization. All document types are CI-tested."
USER_AGENT="OmniLaTeX-CTAN-Uploader/1.0 (github.com/WyattAu/OmniLaTeX-template)"

# ── Parse arguments ────────────────────────────────────────────────────────
DRY_RUN=false
VERSION=""
ZIP_PATH=""
EMAIL="${CTAN_EMAIL:-}"
AUTHOR="${CTAN_AUTHOR:-Wyatt Au}"
CHANGELOG=""
ADMIN_NOTE="Uploaded automatically via OmniLaTeX CTAN upload script"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --email)
            EMAIL="$2"
            shift 2
            ;;
        --author)
            AUTHOR="$2"
            shift 2
            ;;
        --changelog)
            CHANGELOG="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 <version> <zip-path> [--dry-run] [--email ADDR] [--author NAME] [--changelog TXT]"
            exit 0
            ;;
        -*)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
        *)
            if [[ -z "$VERSION" ]]; then
                VERSION="$1"
            elif [[ -z "$ZIP_PATH" ]]; then
                ZIP_PATH="$1"
            fi
            shift
            ;;
    esac
done

# ── Validate inputs ────────────────────────────────────────────────────────
log()  { echo "::group::$1"; cat; echo "::endgroup::"; }
info() { echo "[INFO] $*"; }
warn() { echo "::warning::$*"; }
err()  { echo "::error::$*"; }

fail() { err "$*"; exit "$2"; }

if [[ -z "$VERSION" ]]; then
    fail "Version argument required (e.g., 1.14.0)" 1
fi

if [[ -z "$ZIP_PATH" ]]; then
    fail "Zip path argument required" 1
fi

if [[ ! -f "$ZIP_PATH" ]]; then
    fail "Zip file not found: $ZIP_PATH" 1
fi

if [[ ! -s "$ZIP_PATH" ]]; then
    fail "Zip file is empty: $ZIP_PATH" 1
fi

if [[ -z "$EMAIL" ]]; then
    fail "CTAN_EMAIL not set. Use --email or set CTAN_EMAIL env var." 1
fi

# Validate version format (semver-like: X.Y or X.Y.Z)
if ! echo "$VERSION" | grep -qP '^\d+\.\d+(\.\d+)?$'; then
    fail "Invalid version format: $VERSION (expected X.Y or X.Y.Z)" 1
fi

# Validate zip contains omnilatex.cls
if ! unzip -l "$ZIP_PATH" | grep -q 'omnilatex\.cls$'; then
    fail "Zip does not contain omnilatex.cls" 1
fi

# Validate zip contains README
if ! unzip -l "$ZIP_PATH" | grep -qiE '(README\.md|README$)'; then
    warn "Zip does not contain README.md — CTAN requires it"
fi

# Validate zip contains LICENSE
if ! unzip -l "$ZIP_PATH" | grep -qiE '(LICENSE|COPYING)'; then
    warn "Zip does not contain LICENSE file — CTAN requires license indication"
fi

info "Inputs validated: version=$VERSION zip=$ZIP_PATH email=$EMAIL author=$AUTHOR"

# ── Step 1: Check if package already exists on CTAN ────────────────────────
info "Checking if $PKG_NAME exists on CTAN..."
PKG_EXISTS=false
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
    -A "$USER_AGENT" \
    "${CTAN_BASE}/pkg/${PKG_NAME}")

if [[ "$HTTP_CODE" = "200" ]]; then
    PKG_EXISTS=true
    info "Package EXISTS on CTAN — this will be an UPDATE"
elif [[ "$HTTP_CODE" = "404" ]]; then
    info "Package does NOT exist on CTAN — this will be a NEW submission"
else
    warn "Unexpected HTTP $HTTP_CODE from CTAN package check, assuming new package"
fi

# Also check via JSON API (more reliable for existence)
JSON_EXISTS=$(curl -s "${CTAN_BASE}/json/2.0/packages" | \
    python3 -c "
import sys, json
data = json.load(sys.stdin)
matches = [p for p in data if p.get('key') == '${PKG_NAME}']
print('true' if matches else 'false')
" 2>/dev/null || echo "false")

if [[ "$JSON_EXISTS" = "true" ]]; then
    PKG_EXISTS=true
    info "JSON API confirms package exists"
fi

UPDATE_VALUE="false"
if [[ "$PKG_EXISTS" = "true" ]]; then
    UPDATE_VALUE="true"
fi

# ── Step 2: Pre-flight validation via CTAN endpoints ───────────────────────
info "Running pre-flight validation against CTAN endpoints..."

# 2a. Validate package name
info "  Validating package name..."
NAME_OK=$(curl -s -X POST "${CTAN_BASE}/upload/validatePackageName" \
    -d "pkg=${PKG_NAME}&update=${UPDATE_VALUE}" \
    -A "$USER_AGENT" 2>/dev/null || echo "false")

if [[ "$NAME_OK" != "true" ]]; then
    fail "Package name validation failed: CTAN says '$NAME_OK' (is the name taken?)" 3
fi
info "  Package name: OK"

# 2b. Validate version
info "  Validating version..."
VERS_OK=$(curl -s -X POST "${CTAN_BASE}/upload/validatePackageVersion" \
    -d "pkg=${PKG_NAME}&vers=${VERSION}" \
    -A "$USER_AGENT" 2>/dev/null || echo "false")

if [[ "$VERS_OK" != "true" ]]; then
    fail "Version validation failed: version $VERSION already exists or is invalid" 3
fi
info "  Version: OK"

# 2c. Validate CTAN path (only for new packages)
if [[ "$UPDATE_VALUE" = "false" ]]; then
    info "  Validating CTAN path..."
    PATH_OK=$(curl -s -X POST "${CTAN_BASE}/upload/validateCtanPath" \
        -d "ctanPath=${CTAN_PATH}" \
        -A "$USER_AGENT" 2>/dev/null || echo "false")

    if [[ "$PATH_OK" != "true" ]]; then
        fail "CTAN path validation failed: '${CTAN_PATH}' is not a valid CTAN directory" 3
    fi
    info "  CTAN path: OK"
else
    info "  Skipping CTAN path validation (update mode)"
fi

# 2d. Validate URLs are reachable
declare -A URL_CHECKS=(
    ["homepage"]="$HOMEPAGE"
    ["repository"]="$REPOSITORY"
    ["bugs"]="$BUG_TRACKER"
    ["support"]="$SUPPORT_URL"
)
for URL_LABEL in "${!URL_CHECKS[@]}"; do
    URL_VAL="${URL_CHECKS[$URL_LABEL]}"
    URL_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$URL_VAL" 2>/dev/null || echo "000")
    if [[ "$URL_STATUS" != "200" ]]; then
        warn "  ${URL_LABEL} URL returned HTTP ${URL_STATUS}: ${URL_VAL}"
    fi
done
info "  URL reachability: checked"

info "All pre-flight validations passed"

# ── Dry-run exit ───────────────────────────────────────────────────────────
if [[ "$DRY_RUN" = "true" ]]; then
    info "DRY RUN: all validations passed, would upload version $VERSION"
    info "  mode=$( [[ "$UPDATE_VALUE" = "true" ]] && echo 'update' || echo 'new' )"
    info "  pkg=$PKG_NAME vers=$VERSION path=$CTAN_PATH"
    info "  author=$AUTHOR email=$EMAIL license=$LICENSE"
    exit 0
fi

# ── Step 3: Fetch CSRF token ───────────────────────────────────────────────
info "Fetching CSRF ticket from CTAN upload page..."

UPLOAD_PAGE=$(curl -s -c /tmp/ctan-cookies.txt "${CTAN_BASE}/upload" \
    -A "$USER_AGENT" 2>/dev/null)

TICKET=$(echo "$UPLOAD_PAGE" | grep -oP 'name="ticket" type="hidden" value="\K[^"]*' || true)

if [[ -z "$TICKET" ]]; then
    fail "Could not extract CSRF ticket from CTAN upload page. CTAN may have changed their form." 2
fi

info "CSRF ticket: ${TICKET:0:8}... (length ${#TICKET})"

# ── Step 4: Submit upload ──────────────────────────────────────────────────
info "Submitting upload to CTAN..."
info "  Mode: $( [[ "$UPDATE_VALUE" = "true" ]] && echo 'UPDATE' || echo 'NEW PACKAGE' )"
info "  Version: $VERSION"

RESPONSE=$(curl -s -w "\n__HTTP_CODE__%{http_code}" \
    -b /tmp/ctan-cookies.txt \
    -X POST "${CTAN_BASE}/upload" \
    -A "$USER_AGENT" \
    -F "ticket=${TICKET}" \
    -F "update=${UPDATE_VALUE}" \
    -F "validate=false" \
    -F "pkg=${PKG_NAME}" \
    -F "vers=${VERSION}" \
    -F "author=${AUTHOR}" \
    -F "uploader=${AUTHOR}" \
    -F "email=${EMAIL}" \
    -F "summary=${SUMMARY}" \
    -F "description=${DESCRIPTION}" \
    -F "ctanPath=${CTAN_PATH}" \
    -F "licenses=${LICENSE}" \
    -F "announcement=${CHANGELOG}" \
    -F "note=${ADMIN_NOTE}" \
    -F "home=${HOMEPAGE}" \
    -F "bugs=${BUG_TRACKER}" \
    -F "repository=${REPOSITORY}" \
    -F "support=${SUPPORT_URL}" \
    -F "file=@${ZIP_PATH}" \
    2>/dev/null) || fail "Network error during upload" 5

HTTP_CODE=$(echo "$RESPONSE" | grep -oP '__HTTP_CODE__\K\d+')
BODY=$(echo "$RESPONSE" | sed 's/__HTTP_CODE__.*//')

rm -f /tmp/ctan-cookies.txt

# ── Step 5: Parse response ─────────────────────────────────────────────────
info "CTAN response: HTTP ${HTTP_CODE}"

# Save full response for debugging
echo "$BODY" > /tmp/ctan-response.html

# Check for known success patterns
if echo "$BODY" | grep -qi "has been uploaded\|uploaded successfully\|thank you for your contribution"; then
    info "UPLOAD SUCCEEDED — CTAN accepted the package"
    info "CTAN will review and publish it shortly"
    info "  URL: ${CTAN_BASE}/pkg/${PKG_NAME}"
    exit 0
fi

# Check for known failure patterns
if echo "$BODY" | grep -qi "already exists\|version.*already\|duplicate"; then
    err "UPLOAD REJECTED — version $VERSION already exists on CTAN"
    exit 4
fi

if echo "$BODY" | grep -qi "invalid\|required field\|missing\|error"; then
    err "UPLOAD REJECTED — CTAN reported a validation error"
    info "Response excerpt:"
    echo "$BODY" | grep -iP 'error|invalid|required|missing' | head -5 | sed 's/^/  /'
    info "Full response saved to /tmp/ctan-response.html"
    exit 4
fi

if echo "$BODY" | grep -qi "ticket.*invalid\|csrf\|expired"; then
    err "UPLOAD REJECTED — CSRF ticket expired (try again, tokens are short-lived)"
    exit 2
fi

# HTTP-level checks
if [[ "$HTTP_CODE" -ge 200 && "$HTTP_CODE" -lt 300 ]]; then
    info "UPLOAD LIKELY SUCCEEDED (HTTP ${HTTP_CODE}) — check CTAN to confirm"
    info "  URL: ${CTAN_BASE}/pkg/${PKG_NAME}"
    exit 0
fi

if [[ "$HTTP_CODE" -ge 400 && "$HTTP_CODE" -lt 500 ]]; then
    err "UPLOAD REJECTED — HTTP ${HTTP_CODE} (client error)"
    info "Full response saved to /tmp/ctan-response.html"
    exit 4
fi

if [[ "$HTTP_CODE" -ge 500 ]]; then
    err "UPLOAD FAILED — HTTP ${HTTP_CODE} (CTAN server error, retry later)"
    exit 5
fi

# Unknown response — report but don't fail hard
warn "Unexpected response: HTTP ${HTTP_CODE}"
info "Full response saved to /tmp/ctan-response.html"
info "Check ${CTAN_BASE}/pkg/${PKG_NAME} to confirm upload status"
exit 0
