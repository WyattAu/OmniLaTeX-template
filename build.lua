-- build.lua — l3build configuration for OmniLaTeX
-- This is a custom configuration for a multi-file template project,
-- not a standard single-package CTAN distribution.

module = "omnilatex"
pkgversion = "2.2.3"
pkgdate = "2026-05-31"

sourcefiles = {
    "omnilatex.cls",
    "lib/**/*.sty",
    "config/**/*.sty",
    "lua/*.lua",
}

installfiles = {
    "omnilatex.cls",
    "lib/**/*.sty",
    "config/**/*.sty",
    "lua/*.lua",
}

testfiles = {"testfiles/*"}

typesetfiles = {
    "doc/omnilatex.tex",
}

tdsroot = ""

typesetexe = "lualatex"
checkexe = "lualatex"
