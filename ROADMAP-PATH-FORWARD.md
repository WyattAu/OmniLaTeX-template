# OmniLaTeX: Path Forward and Roadmap

**Date:** 2026-05-17 | **Version:** v2.0.0 | **Post-Audit Status:** All systems green

---

## 1. Current State Summary

### 1.1 What Was Audited

A comprehensive audit was performed covering every aspect of the monorepo:

| Area | Status | Details |
|------|--------|---------|
| Test suite | PASS | 442 fast tests, 6 edge case tests, 10 unicode tests, 6 negative tests, 180 Lean 4 theorems (0 sorry), 19 Lean build jobs |
| Code quality | PASS | black, isort, flake8 all clean; no stubs found |
| CI/CD | PASS (with fixes) | 10 GitHub Actions workflows; 3 action versions updated; hardcoded count fixed |
| Documentation | PASS (with fixes) | Stale metrics corrected across README, ROADMAP, ROADMAP-DETAILED, ROADMAP-PRODUCTION |
| Website pages | PASS (with fixes) | 3 missing beamer examples added; navigation consistency fixed; ARIA accessibility added |
| Pre-commit hooks | ADDED | Full pytest + lint + digest validation + semver check on every commit and push |
| Docker digest consistency | PASS | All 8 CI configs use identical sha256 digest |
| Semantic versioning | PASS | v2.0.0 consistent across VERSION.md and build.lua |
| Lean 4 proofs | PASS | 16 modules, 180 theorems, 0 sorry, all compile via lake build |

### 1.2 Issues Found and Fixed

| # | Issue | Severity | File(s) | Fix |
|---|-------|----------|---------|-----|
| 1 | Stale theorem count (198 -> 180) | Medium | README.md, ROADMAP*.md | Updated all references |
| 2 | Stale module count (15 -> 16) | Medium | ROADMAP.md | Updated |
| 3 | Stale test count (389 -> 442) | Medium | README.md, ROADMAP.md | Updated |
| 4 | Wrong i18n language list | High | README.md | Corrected to actual 18 languages |
| 5 | Missing CI workflow in table | Low | README.md | Added visual-regression.yml |
| 6 | Page count test threshold too low | Low | test_visual_regression.py | 100 -> 300 |
| 7 | Outdated docker/metadata-action | Medium | docker-ci.yml | v4 -> v5 |
| 8 | Outdated docker/build-push-action | Medium | docker-ci.yml | v5 -> v6 |
| 9 | Outdated create-pull-request | Medium | docker-digest-sync.yml | v6 -> v7 |
| 10 | Hardcoded sty count in ctan.yml | Low | ctan.yml | Use array length |
| 11 | Excessive docker-ci timeout | Low | docker-ci.yml | 360 -> 180 min |
| 12 | Missing beamer examples in DOCS | Medium | pages/index.html | Added 3 entries |
| 13 | No navigation on gallery.html | High | pages/gallery.html | Added nav links |
| 14 | No navigation on verify.html | High | pages/verify.html | Added full nav bar |
| 15 | Missing ARIA attributes | Medium | pages/*.html | Added role, tabindex, aria-label, main |

### 1.3 Remaining CI/CD Improvements (Not Yet Implemented)

These were identified during the audit but are lower priority:

| # | Improvement | Severity | Effort |
|---|------------|----------|--------|
| R1 | Pin all GitHub Actions to SHA digests (not tags) | High | 2h |
| R2 | Add dependency review action on PRs | High | 1h |
| R3 | Fix coverage check running outside Docker container | Medium | 1h |
| R4 | Add SBOM upload to GitHub Security tab | Medium | 2h |
| R5 | Add .env.docker validation before Docker pull | Low | 1h |
| R6 | Make integration-matrix report job useful | Low | 1h |
| R7 | Add timeout-minutes to Forgejo/Woodpecker/GitLab jobs | Low | 30min |
| R8 | Use full action URLs in Gitea workflow | Low | 30min |
| R9 | Extract "read Docker digest" into composite action | Low | 2h |
| R10 | Reduce fetch-depth: 0 to fetch-depth: 1 where full history not needed | Low | 30min |

---

## 2. Short-Term Path to Production (v1.26.0 -- v1.27.0)

### Phase 1: CTAN Submission (v1.26.0) -- 1 week

This is the critical path. CTAN submission unlocks `tlmgr install omnilatex` for all TeX Live users worldwide.

**Tasks:**

1. Final CTAN metadata review -- verify CTAN_README.txt, README.md, and file layout conform to CTAN guidelines
2. Run `scripts/ctan-upload.sh --dry-run` to validate the submission package
3. Submit via CTAN web form (requires CTAN account and CTAN_EMAIL secret)
4. Monitor CTAN review queue (1-2 weeks typical)
5. Address reviewer feedback
6. Verify `tlmgr install omnilatex` works on clean TeX Live 2026+

**Blockers:** CTAN review is asynchronous and may require changes.

### Phase 2: Ecosystem Distribution (v1.27.0) -- 2-3 weeks

**Tasks:**

1. Submit to Overleaf template gallery (manual web form, 1-2 week review)
2. Publish VS Code extension to marketplace (`vsce publish`)
3. Verify Nix package builds: `nix build .#omnilatex`
4. Update README install section to include CTAN path
5. Update Overleaf documentation with CTAN install instructions

### Phase 3: CI/CD Hardening (ongoing, start now)

**Priority tasks from audit:**

1. Pin all GitHub Actions to SHA digests (R1)
2. Add `actions/dependency-review-action` on PRs (R2)
3. Add SBOM upload step to docker-ci.yml (R4)
4. Add `.env.docker` validation to all workflows (R5)

---

## 3. Medium-Term Feature Expansion (v2.0.0 -- v2.2.0)

### v2.0.0: Beamer Full Class -- 3-4 weeks

Breaking change release. The Beamer module exists (v2.0.0) but needs a standalone document class.

**Tasks:**

1. Design `omnilatex-beamer` document class API
2. Implement class wrapping KOMA-Script beamer patterns
3. Add Beamer-specific options (aspect ratio, navigation symbols, overlays)
4. Create additional Beamer examples (lecture, thesis defense, poster talk)
5. Extend Lean 4 proofs for Beamer class properties
6. Update BREAKING_CHANGES.md for v2.0.0

### v2.1.0: Community and Accessibility -- 3-4 weeks

1. Community institution configs (Aalto, Chalmers, KIT, NTNU, UofT, etc.)
2. NVDA screen reader validation
3. PDF/UA-1 compliance verification
4. Per-doctype citation defaults (IEEE for articles, APA for thesis)
5. Docker font bundling (Monaspace Neon, Atkinson Hyperlegible Next)
6. Performance regression CI gating (fail if compile time regresses >10%)

### v2.2.0: Manual Completion -- 4-6 weeks

1. Expand 12 thin manual chapters to >150 lines each
2. Add index, list of examples, list of listings
3. VS Code extension workflow screenshots
4. TikZ architecture diagrams
5. Cross-reference validation between all manual chapters
6. Publish manual PDF to GitHub Pages

---

## 4. Long-Term Vision (v3.0.0+)

### v3.0.0: Scale and Platform -- 3-6 months

1. Complete manual to 945 pages
2. Web preview via LaTeX WASM (texlive.js) -- MVP for simple documents
3. Rust TUI build tool to replace build.py (faster builds, cross-platform binary)
4. Template gallery website with user submissions via PR workflow
5. Multi-language documentation (ZH, DE, FR)

### Technical Feasibility

| Feature | Feasibility | Notes |
|---------|-------------|-------|
| LaTeX WASM preview | Medium | texlive.js exists; full template compilation in-browser requires significant work |
| Rust TUI | High | build.py is 2094 lines; `clap` for CLI, `rayon` for parallel compilation |
| Template marketplace | High | GitHub Pages + Jekyll; user submissions via PR workflow |
| Multi-language docs | Medium | Requires native speakers for translation quality assurance |

---

## 5. Verification Metrics Dashboard

### Current Metrics (v2.0.0, post-audit)

| Metric | Value | Source |
|--------|-------|--------|
| .sty modules | 28 | `ls lib/**/*.sty \| wc -l` |
| Document types | 26 | `ls config/document-types/*.sty \| wc -l` |
| Doctype aliases | 55+ | `grep omnilatex@setdoctype omnilatex.cls` |
| Example templates | 46 | `ls -d examples/*/ \| wc -l` |
| Institution configs | 21 | `ls -d config/institutions/*/ \| wc -l` |
| Languages (full translations) | 18 | `grep DeclareTranslation lib/language/omnilatex-i18n.sty` |
| Lean 4 proof modules | 16 | `ls specs/proofs/OmniLaTeXProofs/*.lean \| wc -l` |
| Lean 4 theorems | 180 | `grep -c theorem specs/proofs/OmniLaTeXProofs/*.lean` |
| Fast tests | 442 | `pytest tests/ -m "not slow" -q` |
| Institution tests | 16 | `pytest tests/test_institutions.py -q` |
| Edge case tests | 6 | `pytest tests/test_edge_cases.py -m slow -q` |
| Unicode tests | 10 | `pytest tests/test_unicode.py -q` |
| Negative tests | 6 | `pytest tests/test_negative.py -q` |
| Visual regression tests | 4 | `pytest tests/test_visual_regression.py -m slow -q` |
| CI workflows (GitHub) | 10 | `ls .github/workflows/*.yml \| wc -l` |
| CI configs (other) | 4 | Forgejo, Gitea, GitLab, Woodpecker |
| Manual pages | 238 | PDF page count |
| Pre-commit hooks | 10 | trailing-whitespace, end-of-file-fixer, check-yaml, check-toml, black, isort, flake8, markdownlint, pretty-format-yaml, pytest-fast, lean-proofs |
| Pre-push hooks | 4 | pytest, lint, digest validation, semver check |
| Docker digest sync | 8 configs | .env.docker + 7 downstream CI files |

### Target Metrics (v3.0.0)

| Metric | v2.0.0 | v2.0.0 | v3.0.0 |
|--------|---------|---------|---------|
| CTAN availability | Pending | Live | Live |
| Overleaf gallery | No | Submitted | Premium |
| VS Code installs | 0 | 100+ | 1000+ |
| Lean 4 theorems | 180 | 200+ | 300+ |
| Fast tests | 442 | 500+ | 700+ |
| Examples | 46 | 50+ | 60+ |
| Institutions | 21 | 25+ | 40+ |
| Manual pages | 238 | 300+ | 945+ |
| Web preview | No | No | MVP |
| Docker pulls | Tracking | 500+ | 5000+ |

---

## 6. Technical Debt Register

| ID | Description | Priority | Effort | Introduced |
|----|-------------|----------|--------|------------|
| TD-001 | Actions pinned to tags, not SHA digests | High | 2h | v1.0.0 |
| TD-002 | "read Docker digest" pattern duplicated 8 times | Low | 2h | v1.7.0 |
| TD-003 | Coverage check runs outside Docker container | Medium | 1h | v2.0.0 |
| TD-004 | integration-matrix report job is a no-op | Low | 1h | v1.10.0 |
| TD-005 | Gitea workflow uses GitHub action URLs | Low | 30min | v1.7.0 |
| TD-006 | Forgejo/Woodpecker/GitLab have no timeouts | Low | 30min | v1.7.0 |
| TD-007 | No dependency review on PRs | High | 1h | v1.0.0 |
| TD-008 | No SBOM upload to GitHub Security | Medium | 2h | v1.7.0 |
| TD-009 | build.py is Python (slower than native, requires runtime) | Low | 120h | v1.0.0 |
| TD-010 | Manual has 12 thin chapters (<150 lines) | Medium | 16h | v1.17.0 |
| TD-011 | No Dependabot for GitHub Actions | Low | 30min | v1.0.0 |

---

## 7. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| CTAN rejection | Low | High | Pre-run validation script; follow CTAN guidelines strictly |
| TeX Live breaking changes | Medium | High | Pin minimum TL version; test on TL pre-release |
| Lean 4 toolchain breakage | Low | Medium | Pin lean-toolchain; lake-manifest.json in VCS |
| Community contribution quality | Medium | Low | CI validation; contribution guide; review process |
| Maintenance burden | Medium | Medium | Automate dependency updates; limit scope creep |
| WASM performance | High | Medium | Start with simple documents; incremental complexity |

---

## 8. Deployment Status

### GitHub Pages

The repository already has GitHub Pages deployment configured:

- **Workflow:** `.github/workflows/build.yml` (deploy-pages job)
- **Trigger:** Push to `main` branch
- **Content:** `pages/index.html` (PDF Gallery), `pages/gallery.html` (Template Picker), `pages/verify.html` (Build Verification)
- **Artifacts:** `main.pdf` + all example PDFs copied to `github-pages/pdfs/`
- **Permissions:** `pages: write`, `id-token: write`

The landing page (`index.html`) serves as the entry point. No additional deployment to Cloudflare Pages is needed since the repository is hosted on GitHub.

### Forgejo (forgejo.wyattau.com)

The repository has Forgejo CI configs at `.forgejo/workflows/build.yml`. These are maintained via the docker-digest-sync workflow. Forgejo Pages deployment would require a separate CI job if desired, but is not currently configured.

---

## 9. Conclusion

OmniLaTeX is in a strong position for production release:

- **442 tests pass** across 7 test suites with 0 failures
- **180 Lean 4 theorems** provide formal verification with 0 `sorry`
- **10 CI/CD workflows** provide comprehensive automated validation
- **46 example templates** demonstrate all 26 doctypes across 21 institutions
- **18 language translations** provide broad international support
- **Pre-commit and pre-push hooks** prevent regressions from entering the codebase

The critical path is CTAN submission (Phase 1), which unlocks global distribution via `tlmgr install omnilatex`. All prerequisite work (testing, documentation, packaging scripts) is complete.
