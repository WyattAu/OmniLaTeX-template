# Minimal Beamer Presentation

The simplest possible OmniLaTeX beamer presentation with default settings.

## Usage

    latexmk -lualatex main.tex

Or using the build system:

    python build.py build-example beamer-minimal

## Class Options

| Option | Value | Description |
|--------|-------|-------------|
| doctype | beamer | Beamer slide presentation |

## Features Demonstrated

- Title page with `\titlepage`
- Bullet-point content slides
- Display mathematics (`equation` environment)

## Notes

This is the minimal starting point for an OmniLaTeX beamer presentation. No theme, aspect ratio, or color options are specified, so all defaults are used.
