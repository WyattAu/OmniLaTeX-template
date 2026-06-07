# OmniLaTeX Build System Improvement Plan

**Date:** 2026-06-07
**Scope:** buildlib/, scripts/, tools/, tests/, CI/CD
**Baseline:** v2.4.1 (1359 tests, 74% buildlib coverage)

---

## Priority 1: Critical Fixes (Week 1)

### 1.1 Fix f-string Bugs in Scripts

**Impact:** Three scripts produce completely wrong output.

| File | Lines | Issue |
|------|-------|-------|
| `scripts/benchmark_examples.py` | 70, 82, 163-254 | Missing `f""` prefixes on 20+ strings |
| `scripts/check_links.py` | 36, 42, 63, 71 | Missing `f""` prefixes on 4 strings |
| `tools/convert_omnl_floats.py` | 103, 119-158, 222, 260, 273 | Missing `f""` prefixes make tool non-functional |

**Action:** Add `f` prefix to all affected strings. Verify with `flake8 --select=F821`.

### 1.2 Fix Thread Safety Bugs in builder.py

**Impact:** Race conditions in concurrent builds.

| Issue | Lines | Fix |
|-------|-------|-----|
| Cache read-modify-write gap | 327-346, 448-461 | Hold `_cache_lock` for entire read-modify-write cycle |
| `_refresh_active` reads dict without lock | 558-564 | Acquire `active_lock` inside `_refresh_active` |

### 1.3 Fix Conditional Import in accessibility_checker.py

**Impact:** Buildlib fails to import if `bs4` not installed.

**Line 22:** `from bs4 import BeautifulSoup` is unconditional.

**Fix:** Wrap in try/except like `diff.py` does with numpy:
```python
try:
    from bs4 import BeautifulSoup
    _HAS_BS4 = True
except ImportError:
    _HAS_BS4 = False
```

### 1.4 Fix Coverage Threshold Mismatch

**Impact:** CI fails at 80% but local config says 72%.

| Location | Current | Target |
|----------|---------|--------|
| `tests/pyproject.toml` `fail_under` | 72 | 75 |
| `.github/workflows/build.yml` line 365 | 80.0 | 75.0 |

### 1.5 Fix Type Hint Errors in config.py

**Line 31:** `cnf_lines: list[str] = None` should be `cnf_lines: list[str] | None = None`.

---

## Priority 2: Architecture Improvements (Week 2-3)

### 2.1 Split _BuildCore God Class

**Current:** 690-line class with 6+ responsibilities.

**Target decomposition:**

| New Class | Responsibility | Lines (est) |
|-----------|---------------|-------------|
| `BuildCache` | load, save, evict, stats, clear | ~100 |
| `ExampleDiscovery` | discover, list, collect source files | ~60 |
| `ConcurrentBuilder` | worker, rich/simple concurrent, build_examples | ~200 |
| `RootBuilder` | build_root, run_with_dashboard | ~100 |
| `CleanupManager` | clean_all, clean_aux, clean_example, clean_pdf | ~50 |

**File:** `buildlib/builder.py` -> split into `buildlib/cache.py`, `buildlib/discovery.py`, `buildlib/concurrent.py`, `buildlib/root.py`, `buildlib/cleanup.py`

### 2.2 Split _Commands Mixin

**Current:** 1611-line mixin with 11+ commands.

**Target decomposition:**

| New Mixin | Commands | Lines (est) |
|-----------|----------|-------------|
| `_WatchMixin` | cmd_watch | ~80 |
| `_DoctorMixin` | cmd_doctor | ~150 |
| `_DiffMixin` | cmd_diff, _diff_two_pdfs, _run_latexdiff, _basic_pdf_compare | ~250 |
| `_ScaffoldMixin` | cmd_scaffold_institution, cmd_scaffold_language | ~150 |
| `_InitMixin` | cmd_init, _create_thesis_structure | ~200 |
| `_CheckLintMixin` | cmd_check, cmd_lint | ~200 |
| `_ExportMixin` | cmd_export | ~150 |
| `_PreflightTestMixin` | cmd_preflight, cmd_test | ~100 |

### 2.3 Break Circular Import

**Current:** `__init__ -> cli -> __init__` (works by accident).

**Fix:** Move `BuildTasks` class definition to `buildlib/tasks.py`. `__init__.py` imports from `tasks.py`.

### 2.4 Move RICH_AVAILABLE to config.py

**Current:** `tui.py` imports from `builder.py` just for a constant.

**Fix:** Define `RICH_AVAILABLE` in `config.py`, import from there in both `builder.py` and `tui.py`.

### 2.5 Make accessibility_checker.py and ssim_benchmark.py Optional

**Current:** Both are in buildlib/ but never used by the build system.

**Options:**
- A) Move to `tools/` (cleaner separation)
- B) Keep in buildlib/ with lazy imports (current pattern for numpy)

**Recommendation:** Move to `tools/` since they are standalone utilities.

---

## Priority 3: Performance (Week 3-4)

### 3.1 Optimize Cache Hash with Mtime Short-Circuit

**Current:** `_hash_for_paths` reads every .sty/.cls file on every cache check.

**Fix:** Store mtimes in cache. Only re-hash if any mtime changed.

```python
def _hash_for_paths(self, paths: list[Path]) -> tuple[str, dict[str, float]]:
    h = hashlib.sha256()
    mtimes = {}
    for p in sorted(paths):
        if p.exists():
            mt = p.stat().st_mtime
            mtimes[str(p)] = mt
            h.update(p.read_bytes())
    return h.hexdigest(), mtimes
```

Cache entry becomes:
```json
{"source_hash": "abc", "mtimes": {"path1": 1234567890.0, ...}, "build_time": "..."}
```

On cache check: if all mtimes match cached mtimes, skip hash computation entirely.

### 3.2 Optimize _get_source_files Glob

**Current:** `repo_root.rglob("*.sty")` scans .git/, node_modules/, build/.

**Fix:** Exclude known non-source directories:
```python
EXCLUDE_DIRS = {".git", "node_modules", "build", ".venv", ".direnv", "__pycache__"}
```

Or use `git ls-files --cached '*.sty' '*.cls'` for a git-aware scan.

### 3.3 Single-Pass Log Parsing

**Current:** `parse_log_for_package_times` iterates log lines twice.

**Fix:** Combine into single pass:
```python
def parse_log_for_package_times(log_content: str) -> dict:
    packages = {}
    total_time = None
    for line in log_content.splitlines():
        m = _PACKAGE_RE.match(line.strip())
        if m:
            packages[m.group(1)] = {"name": m.group(1), "date": m.group(2), ...}
        m = _LOAD_LUC_RE.search(line)
        if m:
            ...
        m = _TOTAL_TIME_RE.search(line)
        if m and "seconds" in line.lower():
            val = float(m.group(1))
            if val > 0.5:
                total_time = val
    return {"packages": packages, "package_count": len(packages), "total_time_s": total_time}
```

### 3.4 Scope clean_pdf Glob

**Current:** `Path(".").rglob("*.pdf")` scans entire repo.

**Fix:** Glob only in `build/` and `examples/`:
```python
for pdf in (self.config.build_dir / "examples").glob("*.pdf"):
    pdf.unlink(missing_ok=True)
for pdf in Path("examples").rglob("*.pdf"):
    pdf.unlink(missing_ok=True)
```

### 3.5 Consolidate CI Docker Pulls

**Current:** Every workflow job pulls the Docker image independently.

**Fix:** Create a composite action `.github/actions/setup-docker/action.yml` that caches the image using `docker/save` and `docker/load`.

---

## Priority 4: UX Improvements (Week 4-5)

### 4.1 Upgrade Rich Dashboard

**Current:** Basic worker list with elapsed time.

**Add:**
- Per-example progress bars (using `latexmk` log parsing for page count)
- ETA estimation from `build/metrics.json` history
- Build speed (examples/minute)
- Cache hit/miss indicators
- Color-coded success/failure summary table

### 4.2 Replace TqdmFallback with Rich-Only

**Current:** Falls back to `TqdmFallback` (bare-bones `sys.stdout.write`).

**Fix:** Rich is already a dependency. Remove `TqdmFallback` entirely. If Rich is unavailable, use simple `print()` statements (no progress bar).

### 4.3 Add Fuzzy Matching to _simple_menu

**Current:** `_rich_menu` has fuzzy matching, `_simple_menu` does not.

**Fix:** Port the fuzzy matching logic (lines 148-152 of tui.py) to `_simple_menu`.

### 4.4 Add Unicode Fallback to TerminalOutput

**Current:** Uses `✓`, `⚠`, `✗` which may not display on all terminals.

**Fix:** Add `use_unicode` parameter:
```python
class TerminalOutput:
    def __init__(self, use_color: bool = True, use_unicode: bool = True):
        self.check = "✓" if use_unicode else "[OK]"
        self.warn = "⚠" if use_unicode else "[WARN]"
        self.cross = "✗" if use_unicode else "[ERR]"
```

### 4.5 Add Progress to cmd_check and cmd_lint

**Current:** No progress feedback for long-running operations.

**Fix:** Use Rich Progress bar:
```python
with Progress() as progress:
    task = progress.add_task("Checking...", total=len(files))
    for f in files:
        check_file(f)
        progress.advance(task)
```

### 4.6 Make SSIM Threshold Configurable

**Current:** Hardcoded `threshold = 0.95` in `cmd_diff`.

**Fix:** Add `--threshold` CLI argument, default 0.95.

---

## Priority 5: Error Handling (Week 5)

### 5.1 Log Tracebacks in cli.py

**Current:** `except Exception as e: ui.error(str(e))` loses traceback.

**Fix:**
```python
except Exception as e:
    ui.error(f"An unexpected error occurred: {e}")
    if os.environ.get("OMNILATEX_VERBOSE") or os.environ.get("CI"):
        import traceback
        traceback.print_exc()
    sys.exit(1)
```

### 5.2 Fix Silent pass in profiler.py

**Line 172-173:** `except Exception: pass`

**Fix:** Add `logging.debug("Failed to parse log", exc_info=True)`.

### 5.3 Fix inotifywait Process Leak

**Current:** Process only terminated on KeyboardInterrupt.

**Fix:** Add `finally: process.terminate()` block.

### 5.4 Fix fitz.open Resource Leak

**Current:** Documents not closed on exception in `_basic_pdf_compare`.

**Fix:** Use try/finally:
```python
doc_a = doc_b = None
try:
    doc_a = fitz.open(str(a))
    doc_b = fitz.open(str(b))
    ...
finally:
    if doc_a: doc_a.close()
    if doc_b: doc_b.close()
```

### 5.5 Fix cmd_doctor Temp File Leak

**Current:** Creates temp .tex file but lualatex creates .aux/.log/.pdf alongside it.

**Fix:** Use `tempfile.TemporaryDirectory()` as context manager.

---

## Priority 6: Testing Improvements (Week 6-7)

### 6.1 Add Concurrency Tests

Create `tests/test_buildlib_concurrency.py`:
- Test `_BuildCore` with multiple threads calling `_compile_example_worker`
- Test cache consistency under concurrent reads/writes
- Test `timings_data` thread safety

### 6.2 Add Watch Mode Tests

Create `tests/test_buildlib_watch.py`:
- Test `cmd_watch` with mocked watchdog events
- Test inotifywait fallback path
- Test debounce logic (1-second cooldown)

### 6.3 Fix Flaky Tests

| Test | Issue | Fix |
|------|-------|-----|
| `test_run_permission_denied` | Passes as root in Docker | Skip when `os.getuid() == 0` |
| `test_example_page_count` | Uses `pytest.skip()` on mismatch | Use `pytest.fail()` for regressions |
| SSIM tests without seeds | Non-deterministic | Add fixed seeds to all random inputs |

### 6.4 Update Pre-commit pytest Hook

**Current:** Hardcoded list of test files (drifts out of sync).

**Fix:** Use collection-based invocation:
```yaml
entry: .venv/bin/python -m pytest tests/ -q --timeout=30 -m "not slow" --tb=short
```

### 6.5 Add Missing Test Coverage

| Gap | Priority |
|-----|----------|
| `cmd_watch` functional tests | High |
| `cmd_export` success paths | Medium |
| Plugin lifecycle (install/upgrade/uninstall) | Medium |
| Graceful degradation without optional deps | Medium |
| `_run_with_dashboard` Rich path | Low |

### 6.6 Add mypy to Pre-commit and CI

```yaml
- repo: https://github.com/pre-commit/mirrors-mypy
  rev: v1.10.0
  hooks:
  - id: mypy
    additional_dependencies: [types-PyYAML]
```

---

## Priority 7: Code Quality (Week 7-8)

### 7.1 Remove Dead Code

| File | Issue |
|------|-------|
| `builder.py` line 8 | `import subprocess` (unused) |
| `profiler.py` line 179 | `import os` (redundant local import) |
| `scripts/sync_versions.py` | `_read_canonical` function (never called) |

### 7.2 Fix Type Hints

| File | Line | Fix |
|------|------|-----|
| `config.py` | 31 | `cnf_lines: list[str] \| None = None` |
| `commands.py` | 336 | `output: str \| None = None` |
| `commands.py` | 399 | `output: str \| None = None, cwd: Path \| None = None` |
| `commands.py` | 482 | `output: str \| None = None` |
| `ui.py` | all methods | Add return type hints |

### 7.3 Add Docstrings

Priority targets:
- `_BuildCore.__init__`, `_hash_for_paths`, `_load_build_cache`, `_save_build_cache`
- `_compile_example_worker`, `build_examples`, `build_root`
- `clean_all`, `clean_aux`, `clean_example`, `clean_pdf`
- `TerminalOutput` class and all methods
- `ProjectConfig` class and methods

### 7.4 Standardize Subprocess Invocation

Document when direct `subprocess.run` is necessary vs. `CommandRunner.run`. Add a `# NOTE:` comment at each direct usage explaining why.

### 7.5 Fix .latexmkrc Issues

| Line | Issue | Fix |
|------|-------|-----|
| 288, 291 | Unquoted `$_[0]` in system call | Quote: `"$ $_[0]"` |
| 293-309 | Mixed indentation | Normalize to consistent indentation |
| 302 | `$ret` scope issue | Move `my $ret` to outer scope |

---

## Priority 8: CI/CD Optimization (Week 8-9)

### 8.1 Consolidate Duplicate Builds

| Workflow | Overlap | Fix |
|----------|---------|-----|
| `build.yml` + `visual-regression.yml` | Both build all examples | Share artifacts from `build.yml` |
| `build.yml` + `performance-regression.yml` | Both build with timings | Share artifacts |
| `build-examples.yml` | 50 separate Docker pulls | Batch into 5 jobs x 10 examples |

### 8.2 Cache Test Dependencies in Docker

**Current:** `pip install` inside Docker on every run.

**Fix:** Create `docker/Dockerfile.test` with test deps pre-installed, or add to main Dockerfile.

### 8.3 Add Security Scanning

```yaml
- name: Bandit security scan
  run: bandit -r buildlib/ -c pyproject.toml

- name: Trivy container scan
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: ${{ steps.digest.outputs.image }}
```

### 8.4 Add Lua Module Tests to CI

**Current:** `scripts/run_module_tests.py` exists but is never invoked in CI.

**Fix:** Add job to `build.yml`:
```yaml
- name: Run Lua module tests
  run: python scripts/run_module_tests.py
```

### 8.5 Tighten Reproducibility Tolerance

**Current:** 3% file size tolerance.

**Fix:** Reduce to 1%, with a documented escape hatch for legitimate variance.

---

## Implementation Order

```
Week 1:  [1.1] f-string fixes, [1.2] thread safety, [1.3] bs4 import, [1.4] coverage threshold
Week 2:  [2.1] Split _BuildCore, [2.3] break circular import, [2.4] RICH_AVAILABLE
Week 3:  [2.2] Split _Commands, [3.1] mtime cache, [3.2] glob optimization
Week 4:  [3.3] single-pass log parse, [3.4] scope clean_pdf, [4.1] Rich dashboard
Week 5:  [4.2-4.6] UX improvements, [5.1-5.5] error handling fixes
Week 6:  [6.1-6.3] concurrency/watch/flaky tests, [7.1-7.2] dead code/type hints
Week 7:  [6.4-6.6] pre-commit/mypy/coverage, [7.3-7.5] docstrings/latexmkrc
Week 8:  [8.1-8.2] CI consolidation, [8.3-8.5] security/Lua/tolerance
Week 9:  Integration testing, documentation updates, release v2.5.0
```

---

## Success Criteria

| Metric | Current | Target (v2.5.0) |
|--------|---------|------------------|
| buildlib coverage | 74% | 82% |
| builder.py coverage | 62% | 80% |
| Thread safety bugs | 2 | 0 |
| f-string bugs in scripts | 24+ | 0 |
| CI wall time (push to main) | ~45 min | ~25 min |
| Rich dashboard features | Basic worker list | ETA, per-example progress, cache stats |
| Pre-commit hooks | 24 | 27 (+mypy, +bandit, +hadolint) |
