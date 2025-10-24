# OmniLaTeX Float Environment Failure Report

## Summary
- **Issue**: Compiling documents that use the custom `omnlfigure` environment from `lib/layout/omnilatex-floats.sty` fails with the LuaLaTeX error `You can't use 'the letter o' after \the`.
- **Scope**: Reproduces with a single float in isolation (`test-omnlfigure.tex`) as well as during the full book builds.
- **Current Status**: Root cause not yet identified; debugging concentrated within the float option parsing and caption handling code paths.

## Environment
- **Workspace**: `WyattAu/OmniLaTeX-template`
- **Compiler**: `lualatex` (LuaHBTeX, Version 1.22.0 — TeX Live 2025)
- **Primary file under investigation**: `lib/layout/omnilatex-floats.sty`

## Minimal Reproduction
Create `test-omnlfigure.tex`:
```latex
\documentclass{scrbook}
\usepackage{expl3}
\usepackage{graphicx}
\input{lib/layout/omnilatex-floats.sty}
\begin{document}
\begin{omnlfigure}[caption={Ansprüche an die Wissenschaft},label={fig:test}]
  Test
\end{omnlfigure}
\end{document}
```
Compile with:
```bash
lualatex -interaction=nonstopmode -halt-on-error test-omnlfigure.tex
```
Result:
```
! You can't use `the letter o' after \the.
<argument> o
l.10 \end{omnlfigure}
```

## Debugging Timeline
- **Options sanitization**: Removed `capt-of` dependency and ensured no stray apostrophes remain in the optional argument. `\tl_show:N \l__omnilatex_float_options_tl` now prints the clean string `caption={...},label={...}`.
- **Key handlers**: `\keys_set:nn { omnilatex / float } { ... }` confirmed to call the `caption` and `label` handlers in isolation (`minimal-keys.tex` succeeds).
- **Failure locus**: Within `\omnilatex_float_begin:nn()` (`lib/layout/omnilatex-floats.sty`), the call to `\keys_set:nn` still triggers the `\the` error *only when wrapped by the float environment*.
- **Diagnostics added**: Temporary `\typeout` statements in the key handlers and `\tl_show` in `\omnilatex_float_begin:nn` to capture the option list before parsing.

## Observations
- The crash persists even when the float options contain only `caption=` (label removed).
- Running `\keys_set:nn { omnilatex / float } { caption={Test} }` outside of any float environment does *not* crash.
- The error occurs before the caption text is typeset; `\omnilatex_float_typeset_caption:` is never reached when `caption-position` defaults to `bottom`.
- No `\the` commands exist in the float option handling code, suggesting TeX is evaluating an internal counter unexpectedly during option parsing.

### Latest (2025-10-22, afternoon)
- **Environment close regression**: After instrumenting `\omnilatex_float_begin:nn`, the fatal error now reported by `lualatex` is `Environment f undefined`. Inspection shows `\omnilatex_float_end:` (in `lib/layout/omnilatex-floats.sty`) expands to `\__omnilatex_float_end_env:n { f }`, meaning only the first token of `\l__omnilatex_float_type_tl` is passed to the helper. The closing logic currently stringifies the type and loses the remainder of the name.
- **Diagnostics**: Added `\iow_term:x { omnilatex debug: closing type = ... }` immediately before the close to confirm TeX sees the trimmed type value. The message never prints in the failing run, indicating TeX aborts right as the incorrect `\end` control sequence executes.
- **Impact**: This regression hides the original `\the` problem until the closing macro is fixed; resolving the close is a prerequisite before resuming the original investigation.

## Hypotheses Under Investigation
- Interaction between `\keys_set:nn` and grouping within the KOMA `figure` environment leading to counter evaluation with a non-numeric token.
- Hidden expansion within the KOMA float machinery or `caption` package hooks that assumes a numeric counter immediately after the float begins.
- Side effects from `\omnilatex_float_validate:` or the caption-position toggling logic that may modify `\@captype` or reference counters prematurely.
- Incorrect construction of the closing control sequence (`\csname end...
  \endcsname`) causing TeX to execute `\end f` instead of `\end{figure}` when `\omnlfigure` finishes.

## Next Steps
- Instrument the start/end of the `caption` key handler and `\omnilatex_float_validate:` to pinpoint the exact expansion triggering `\the`.
- Attempt a plain `figure` environment using the same caption text to determine whether the issue is specific to OmniLaTeX wrappers or a broader KOMA/caption incompatibility.
- Explore resetting the counter state (e.g., `\setcounter{figure}{0}`) before `\keys_set:nn` to rule out counter contamination.
- Once the failure point is located, remove the temporary diagnostics and re-run the minimal test, followed by `python3 build.py --mode prod build-root`.
- Fix the closing macro to execute the full environment name (i.e., `\csname end\l__omnilatex_float_type_tl\endcsname`) so `\omnlfigure` returns to the original error state and the underlying `\the` issue can be investigated further.

## Files With Temporary Instrumentation
- `lib/layout/omnilatex-floats.sty`: includes `\tl_show` in `\omnilatex_float_begin:nn` and `\typeout` lines in the `caption`/`short-caption`/`label` key handlers. These should be removed after the investigation concludes.

## Related Scripts / Commands
- `test-omnlfigure.tex`: full float reproduction (with caption and label).
- `minimal-keys.tex`: isolates `\keys_set:nn` outside the float environment.
- `lualatex -interaction=nonstopmode -halt-on-error ...`: command used for every test compile.

---
Prepared on 2025-10-22 to capture current understanding of the OmniLaTeX float compilation failure.
