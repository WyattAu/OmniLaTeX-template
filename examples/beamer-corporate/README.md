# Corporate Beamer Presentation

A corporate quarterly review presentation using the Berlin theme with beaver colors, demonstrating business-oriented slide patterns.

## Usage

    latexmk -lualatex main.tex

Or using the build system:

    python build.py build-example beamer-corporate

## Class Options

| Option | Value | Description |
|--------|-------|-------------|
| doctype | beamer | Beamer slide presentation |
| beameraspectratio | 169 | 16:9 widescreen aspect ratio |
| beamertheme | Berlin | Berlin beamer theme |
| institution | generic | Generic institutional branding |

## Features Demonstrated

- Three-column metric dashboards
- Feature shipment tracking tables
- `semiverbatim` deployment pipeline listing
- TikZ line chart for team growth visualization
- Risk register table with probability/impact
- `\useoutertheme{infolines}` for navigation footers
- `\usecolortheme{beaver}` red-toned corporate palette
- `alertblock` for slipped items and action items

## Notes

Uses `\useoutertheme{infolines}` and `\setbeamertemplate{footline}[frame number]` for custom footer navigation. Content models a realistic engineering quarterly review format.
