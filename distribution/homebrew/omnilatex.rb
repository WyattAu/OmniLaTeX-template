# typed: false
# frozen_string_literal: true

# OmniLaTeX: Modular LaTeX document class
#
# A modular, engineering-grade LaTeX document class supporting
# 27 document types, 25 languages, and 21 institution configurations.
# Built on KOMA-Script with LuaLaTeX engine.

class Omnilatex < Formula
  desc "Modular LaTeX document class with 27 doctypes, 25 languages"
  homepage "https://github.com/WyattAu/OmniLaTeX-template"
  url "https://github.com/WyattAu/OmniLaTeX-template/archive/refs/tags/v2.4.0.tar.gz"
  sha256 "PLACEHOLDER_SHA256"
  license "Apache-2.0"
  head "https://github.com/WyattAu/OmniLaTeX-template.git", branch: "main"

  depends_on "texlive"
  depends_on "python@3.10"

  def install
    # Install LaTeX files to texmf directory
    texmf_dir = share/"texmf/tex/latex/omnilatex"
    texmf_dir.mkpath

    # Core files
    texmf_dir.install "omnilatex.cls"
    texmf_dir.install "omnilatex.cwl"

    # Modules
    lib_dir = texmf_dir/"lib"
    lib_dir.mkpath
    cp_r "lib", lib_dir.parent

    # Configuration
    config_dir = texmf_dir/"config"
    config_dir.mkpath
    cp_r "config", config_dir.parent

    # Lua extensions
    lua_dir = texmf_dir/"lua"
    lua_dir.mkpath
    cp_r "lua", lua_dir.parent

    # Assets
    assets_dir = texmf_dir/"assets"
    assets_dir.mkpath
    cp_r "assets", assets_dir.parent

    # Bibliography
    bib_dir = texmf_dir/"bib"
    bib_dir.mkpath
    cp_r "bib", bib_dir.parent

    # latexmkrc
    texmf_dir.install ".latexmkrc"

    # Build system
    bin.mkpath
    bin.install "build.py"

    # Examples (for reference)
    examples_dir = share/"omnilatex/examples"
    examples_dir.mkpath
    cp_r "examples", examples_dir.parent

    # Documentation
    doc_dir = share/"omnilatex/doc"
    doc_dir.mkpath
    doc_dir.install "README.md", "LICENSE", "CHANGELOG.md", "VERSION.md"
    doc_dir.install "doc/omnilatex.pdf" if File.exist?("doc/omnilatex.pdf")
  end

  test do
    # Verify installation
    assert_predicate texmf_dir, :exist?, "TeXmf directory should exist"
    assert_predicate texmf_dir/"omnilatex.cls", :exist?, "Main class file should exist"
    assert_predicate texmf_dir/"lib", :exist?, "Modules directory should exist"
    assert_predicate texmf_dir/"config", :exist?, "Config directory should exist"

    # Verify build system
    assert_predicate bin/"build.py", :exist?, "Build script should exist"

    # Test build (requires full TeX Live)
    system "python3", bin/"build.py", "preflight" if system "which lualatex"
  end

  def texmf_dir
    share/"texmf/tex/latex/omnilatex"
  end
end
