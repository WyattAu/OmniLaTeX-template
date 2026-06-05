# Overleaf Template

To use OmniLaTeX on Overleaf:

1. Upload `omnilatex.cls`, `lib/`, and `config/` to your Overleaf project.
2. Set the compiler to **LuaLaTeX** (Menu → Compiler).
3. Use TeX Live 2025 or later.

Example `main.tex`:

```latex
\documentclass[
    language=english,
    doctype=article,
    institution=none,
]{omnilatex}
\begin{document}
Hello, OmniLaTeX!
\end{document}
```

## Quick Start (Overleaf)

Upload these files:

- `omnilatex.cls`
- `lib/` (entire directory)
- `config/` (entire directory)

Then create your document as shown above.
