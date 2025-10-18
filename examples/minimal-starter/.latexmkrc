#!/bin/env perl

# ======================================================================================
# Example-specific latexmkrc for minimal-starter
# ======================================================================================

# CRITICAL: Set TEXINPUTS to include the root directory
# This allows LaTeX to find lib/ modules and omnilatex.cls
ensure_path('TEXINPUTS', '../..///:');

# Also set it directly for the environment
$ENV{'TEXINPUTS'} = '.:../..///:' . ($ENV{'TEXINPUTS'} || '');

# Load root configuration
do '../../.latexmkrc';

# Minimal starter uses default settings
