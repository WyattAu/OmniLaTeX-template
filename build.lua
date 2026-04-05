-- build.lua — l3build configuration for OmniLaTeX
-- This is a custom configuration for a multi-file template project,
-- not a standard single-package CTAN distribution.

module = "omnilatex"
pkgversion = "1.0.0"
pkgdate = "2026-04-03"

sourcefiles = {
    "omnilatex.cls",
    "lib/**/*.sty",
    "config/**/*.sty",
    "lua/*.lua",
    "*.latexmkrc",
}

installfiles = {
    "omnilatex.cls",
    "lib/**/*.sty",
}

testfiles = {"testfiles/*"}

typesetfiles = {
    "examples/thesis/main.tex",
}

tdsroot = ""

typesetexe = "lualatex"
checkexe = "lualatex"
