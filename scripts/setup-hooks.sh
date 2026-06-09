#!/usr/bin/env bash
# Install git hooks from scripts/hooks/ into .git/hooks/.
# Run this after cloning the repository.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

HOOKS="pre-push"

for hook in $HOOKS; do
    src="$REPO_ROOT/scripts/hooks/$hook"
    dst="$REPO_ROOT/.git/hooks/$hook"
    if [ -f "$src" ]; then
        cp "$src" "$dst"
        chmod +x "$dst"
        echo "Installed $hook"
    else
        echo "WARNING: $src not found, skipping"
    fi
done

echo "Git hooks installed. Run 'git push --no-verify' to bypass."
