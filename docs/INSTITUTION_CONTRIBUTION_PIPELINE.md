# Institution Contribution Guide

## Overview

This guide explains how to add a new institution configuration to OmniLaTeX.
Each institution provides custom branding, colors, logos, and translation strings.

## Quick Start

### Option 1: Automated Scaffolding

```bash
python build.py scaffold-institution <institution-name>
```

This creates:

```
config/institutions/<institution-name>/
  <institution-name>.sty          # Institution configuration
  assets/
    logos/<institution-name>/     # Logo directory
```

### Option 2: Manual Creation

1. Copy the generic template:

   ```bash
   cp -r config/institutions/generic config/institutions/<your-institution>
   ```

2. Rename the `.sty` file:

   ```bash
   mv config/institutions/<your-institution>/generic.sty \
      config/institutions/<your-institution>/<your-institution>.sty
   ```

3. Customize the configuration (see below).

## Configuration File Structure

The `.sty` file follows this structure:

```latex
%% <Institution Name> Configuration
%% Path: config/institutions/<name>/<name>.sty

\NeedsTeXFormat{LaTeX2e}
\ProvidesPackage{config/institutions/<name>/<name>}[2026/01/01 Institution Configuration]

%% ── Logo ──────────────────────────────────────────────
\newcommand{\institutionlogo}{}
\newcommand{\institutionlogosmall}{}

%% ── Colors ────────────────────────────────────────────
\definecolor{institutionprimary}{HTML}{XXXXXX}
\definecolor{institutionsecondary}{HTML}{XXXXXX}
\definecolor{institutionaccent}{HTML}{XXXXXX}

%% ── Links ─────────────────────────────────────────────
\newcommand{\institutionurl}{https://example.edu}
\newcommand{\institutionname}{Example University}

%% ── Custom Commands ───────────────────────────────────
% Add institution-specific LaTeX commands here
```

## Required Elements

| Element | Description | Example |
|---------|-------------|---------|
| Package declaration | `\ProvidesPackage` with correct path | `\ProvidesPackage{config/institutions/tum/tum}` |
| Logo commands | `\institutionlogo` and `\institutionlogosmall` | `\newcommand{\institutionlogo}{logo.pdf}` |
| Color definitions | Primary, secondary, accent colors | `\definecolor{institutionprimary}{HTML}{1F407A}` |
| URL | Institution website | `\newcommand{\institutionurl}{https://tum.de}` |
| Name | Full institution name | `\newcommand{\institutionname}{Technical University of Munich}` |

## Logo Requirements

- Format: PDF (recommended) or SVG
- Size: 200-400px wide for main logo, 100-200px for small variant
- Location: `assets/logos/<institution-name>/`
- Naming: `<institution-name>-logo.pdf`, `<institution-name>-logo-small.pdf`

## Color Guidelines

- Use hex color codes (`#RRGGBB`)
- Primary color: Main brand color (used for headings, links)
- Secondary color: Supporting color (used for backgrounds, borders)
- Accent color: Highlight color (used for callouts, emphasis)
- Ensure sufficient contrast for accessibility (WCAG 2.1 AA)

## Testing Your Configuration

1. Create a test document:

   ```latex
   \documentclass[doctype=article,institution=<your-institution>]{omnilatex}
   \begin{document}
   \maketitle
   \section{Test}
   Hello from \institutionname!
   \end{document}
   ```

2. Build the test:

   ```bash
   python build.py build-example <your-institution>-test
   ```

3. Verify the output PDF uses your institution's colors and logo.

## CI Validation

When you submit a pull request, the CI pipeline will:

1. Validate the `.sty` file structure
2. Check that logo files exist
3. Verify color definitions are valid
4. Build the example document
5. Run visual regression tests

## Submission Process

1. Fork the repository
2. Create your institution configuration
3. Add an example document in `examples/`
4. Submit a pull request with:
   - Institution name
   - Logo files (PDF format preferred)
   - Color palette (hex codes)
   - Website URL
   - Brief description

## File Checklist

- [ ] `<name>.sty` file created
- [ ] Logo files in `assets/logos/<name>/`
- [ ] Colors defined (primary, secondary, accent)
- [ ] URL and name set
- [ ] Example document created
- [ ] Documentation updated (if applicable)
