# VS Code Extension Marketplace Preparation

## Current Status

The extension exists at `extensions/vscode-omnilatex/` with version 2.1.0.

## Marketplace Publishing Steps

### 1. Install Publishing Tools

```bash
npm install -g @vscode/vsce
```

### 2. Update Version

Update `package.json` version to match the latest release:

```json
{
  "version": "2.4.0"
}
```

### 3. Package Extension

```bash
cd extensions/vscode-omnilatex
vsce package
```

This creates `omnilatex-2.4.0.vsix`.

### 4. Publish to VS Code Marketplace

```bash
# Login with Personal Access Token
vsce login <publisher-name>

# Publish
vsce publish
```

### 5. Publish to Open VSX

```bash
# Install ovsx CLI
npm install -g ovsx

# Login
ovsx login <token>

# Publish
ovsx publish omnilatex-2.4.0.vsix
```

## Extension Features

### Commands

| Command | Description |
|---------|-------------|
| `omnilatex.switchDoctype` | Switch document type |
| `omnilatex.switchInstitution` | Switch institution |
| `omnilatex.build` | Build current document |
| `omnilatex.buildAll` | Build all examples |
| `omnilatex.clean` | Clean build artifacts |
| `omnilatex.test` | Run test suite |
| `omnilatex.preflight` | Check environment |
| `omnilatex.doctor` | Health diagnostics |

### IntelliSense

- `\documentclass` option completion (27 doctypes, 21 institutions)
- `\useplugin` completion (installed plugins)
- Language option completion (25 languages)

### Snippets

- Document templates
- Section structures
- Common environments

## CI/CD for Extension

Add to GitHub Actions:

```yaml
- name: Publish VS Code Extension
  if: startsWith(github.ref, 'refs/tags/v')
  run: |
    cd extensions/vscode-omnilatex
    npm install
    npm run compile
    vsce publish -p ${{ secrets.VSCODE_PAT }}
  env:
    VSCE_PAT: ${{ secrets.VSCODE_PAT }}
```

## Open VSX Publishing

Open VSX is the open-source alternative to the VS Code Marketplace. Used by VSCodium, Gitpod, and other forks.

### Requirements

1. Open VSX account at https://open-vsx.org
2. Publisher token

### Publishing Command

```bash
ovsx publish omnilatex-2.4.0.vsix -p <token>
```

## Testing Before Publishing

```bash
# Install extension locally
code --install-extension omnilatex-2.4.0.vsix

# Test in VS Code
code --disable-extensions --enable-extension=wyattau.omnilatex
```
