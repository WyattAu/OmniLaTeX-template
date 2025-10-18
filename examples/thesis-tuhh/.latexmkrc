#!/bin/env perl

# ======================================================================================
# Example-specific latexmkrc for thesis-tuhh
# ======================================================================================
# This configuration sources the root .latexmkrc and can add example-specific overrides

# CRITICAL: Set TEXINPUTS to include the root directory
# This MUST be done before loading root config
# The notation means: current dir (.), then root recursively (../..///), then system paths (:)
ensure_path('TEXINPUTS', '../..///:');

# Also set it directly for the environment
$ENV{'TEXINPUTS'} = '.:../..///:' . ($ENV{'TEXINPUTS'} || '');

# Load root configuration
do '../../.latexmkrc';

# Example-specific overrides can be added here if needed
# For example:
# $max_repeat = 8;  # Override if this example needs more runs

# This example uses the default settings from root
