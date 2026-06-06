# OmniLaTeX Plugin System Specification

## Overview

The plugin system enables third-party extensions to OmniLaTeX without modifying the core class. Plugins are self-contained LaTeX packages that follow a standardized manifest format.

## Plugin Manifest (manifest.toml)

Every plugin must include a `manifest.toml` at its root:

```toml
[plugin]
name = "my-plugin"
version = "1.0.0"
description = "Brief description of what the plugin does"
author = "Author Name"
license = "Apache-2.0"
homepage = "https://github.com/author/plugin-name"

[plugin.requirements]
omnilatex = ">=2.4.0"
texlive = ">=2024"
engine = "lualatex"
python = false

[plugin.dependencies]
# Other plugins this plugin depends on
# name = ">=version"

[plugin.conflicts]
# Plugins that cannot coexist
# name = "*"

[plugin.files]
# Main .sty file to load
main = "omnilatex-plugin-my-plugin.sty"

# Optional: additional files to install
assets = ["assets/logo.pdf"]
docs = ["README.md"]

[plugin.security]
# Security sandbox settings
shell_escape = false
file_write = false
network = false
```

## Plugin File Structure

```
omnilatex-plugin-<name>/
  manifest.toml           # Plugin manifest (required)
  omnilatex-plugin-<name>.sty  # Main LaTeX file (required)
  README.md               # Documentation (recommended)
  LICENSE                 # License file (required)
  assets/                 # Optional assets
    logo.pdf
  docs/                   # Optional documentation
    usage.md
```

## Plugin Loading

Plugins are loaded via the `\useplugin` command:

```latex
\documentclass[doctype=article]{omnilatex}
\RequirePackage{config/document-settings}

% Load a plugin
\useplugin{my-plugin}

% Load with options
\useplugin[verbose=true]{my-plugin}

% List available plugins
\listplugins
```

## Plugin Search Path

Plugins are searched in the following order:

1. Current document directory
2. `TEXINPUTS` paths
3. `~/texmf/tex/latex/omnilatex-plugin-*/`
4. System-wide `texmf-local/tex/latex/omnilatex-plugin-*/`

## Plugin Registry

The official plugin registry is hosted at:

```
https://github.com/WyattAu/omnilatex-plugins
```

### Registry Structure

```
omnilatex-plugins/
  registry.toml           # Master registry index
  plugins/
    <name>/
      manifest.toml       # Plugin manifest
      omnilatex-plugin-<name>.sty  # Plugin source
      README.md
      LICENSE
```

### registry.toml Format

```toml
[registry]
version = "1.0.0"
last_updated = "2026-06-06"

[[plugin]]
name = "my-plugin"
version = "1.0.0"
description = "Brief description"
author = "Author Name"
homepage = "https://github.com/author/plugin"
license = "Apache-2.0"
omnilatex_min = "2.4.0"
tags = ["utility", "formatting"]
```

## Security Sandbox

Plugins execute in a sandboxed environment:

| Capability | Default | Configurable |
|------------|---------|--------------|
| Shell escape | No | Yes (manifest) |
| File write | No | Yes (manifest) |
| Network access | No | No |
| File read | Limited | No |
| Environment variables | Limited | No |

### Sandbox Rules

1. **No shell escape** unless explicitly enabled in manifest
2. **No file writes** outside the build directory
3. **No network access** (prevents data exfiltration)
4. **File read** limited to TEXINPUTS paths
5. **Environment variables** limited to PATH and TEXINPUTS

## Creating a Plugin

### Step 1: Scaffold

```bash
python build.py scaffold-plugin <plugin-name>
```

This creates:

```
omnilatex-plugin-<name>/
  manifest.toml
  omnilatex-plugin-<name>.sty
  README.md
  LICENSE
```

### Step 2: Implement

Edit `omnilatex-plugin-<name>.sty` to add your functionality.

### Step 3: Test

```bash
# Test the plugin loads correctly
python build.py test-plugin <plugin-name>

# Test in a sample document
cd examples/minimal-starter
# Add \useplugin{<name>} to main.tex
python build.py build-example minimal-starter
```

### Step 4: Publish

1. Create a GitHub repository
2. Add to the plugin registry via pull request
3. Tag a release

## Plugin API

Plugins have access to these OmniLaTeX internals:

### Commands

| Command | Description |
|---------|-------------|
| `\omnilatex@plugin@name` | Current plugin name |
| `\omnilatex@plugin@version` | Current plugin version |
| `\omnilatex@plugin@options` | Plugin options |

### Hooks

| Hook | When | Description |
|------|------|-------------|
| `omnilatex@before@document` | Before `\begin{document}` | Pre-document setup |
| `omnilatex@after@document` | After `\end{document}` | Post-document cleanup |
| `omnilatex@before@title` | Before `\maketitle` | Title customization |
| `omnilatex@before@section` | Before each section | Section hooks |

### Example Plugin

```latex
% omnilatex-plugin-example.sty
\NeedsTeXFormat{LaTeX2e}
\ProvidesPackage{omnilatex-plugin-example}[2026/01/01 Example Plugin]

% Hook into section formatting
\AddToHook{omnilatex@before@section}{%
  \ClassInfo{omnilatex}{Plugin: Section started}%
}

% Provide a custom command
\newcommand{\examplecommand}{%
  This is an example command from the plugin.%
}
```
