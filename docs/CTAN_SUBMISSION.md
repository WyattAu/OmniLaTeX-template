# CTAN Submission Guide

Step-by-step instructions for submitting OmniLaTeX to CTAN.

## 1. Prerequisites

- **CTAN account** — register at https://ctan.org/account if you do not have one
- **TeX Live installation** — a recent TeX Live (2025+) with LuaLaTeX for local testing

## 2. Pre-submission Checklist

### 2.1 Generate the CTAN zip

```bash
bash scripts/make-ctan-zip.sh
```

This creates `omnilatex.zip` in the repository root.

### 2.2 Verify zip contents

```bash
unzip -l omnilatex.zip
```

The zip **must** contain:

| Path | Description |
|------|-------------|
| `omnilatex/omnilatex.cls` | Main document class |
| `omnilatex/lib/` | Module library (27 modules across 9 subdirectories) |
| `omnilatex/config/document-types/` | 23 document type `.sty` files |
| `omnilatex/config/document-settings.sty` | Global settings |
| `omnilatex/bib/bibliography.bib` | Default bibliography |
| `omnilatex/LICENSE` | Apache License 2.0 |
| `omnilatex/README.md` | Package README |
| `omnilatex/CHANGELOG.md` | Changelog |
| `omnilatex/VERSION.md` | Version info |

### 2.3 Run CTAN validation tests

```bash
pytest tests/test_ctan.py
```

All tests must pass.

### 2.4 Verify examples compile on Docker

```bash
docker run -it --rm -v $(pwd):/workspace ghcr.io/wyattau/omnilatex-docker:latest
python build.py build-examples
```

All 39 examples should compile without errors. Alternatively, run the CI pipeline which exercises the full build matrix.

## 3. Submission Process

### 3.1 Upload

1. Go to https://ctan.org/upload
2. Log in with your CTAN account
3. Upload `omnilatex.zip`

### 3.2 Fill in the form

| Field | Value |
|-------|-------|
| **Package name** | `omnilatex` |
| **Version** | (read from `VERSION.md`, e.g. `1.10.0`) |
| **Summary** | `A modular, engineering-grade LaTeX document class supporting 23 document types, 14 languages, and multiple color themes` |
| **Description** | (copy the long description from `README.md`) |
| **License** | Apache-2.0 |
| **CTAN path** | `macros/latex/contrib/omnilatex` |
| **Maintainer** | Wyatt Au |
| **Home page** | https://github.com/WyattAu/OmniLaTeX-template |
| **Topics** | class, document-type, multilingual, template |

### 3.3 Wait for review

CTAN reviewers typically respond within **1–7 days**. They may:

- Request changes to the zip structure or metadata
- Ask for clarification on licensing or dependencies
- Suggest moving files to different CTAN paths

Respond promptly to any feedback. The package will appear on CTAN and in TeX Live after approval.

## 4. Post-submission

### 4.1 Address CTAN feedback

If reviewers request changes:

1. Make the required changes locally
2. Update `CTAN_README.txt` if the README needs revision
3. Re-run `bash scripts/make-ctan-zip.sh`
4. Re-upload the updated zip via https://ctan.org/upload

### 4.2 Announce the release

- Post to [TeX Live mailing list](https://tug.org/mailman/listinfo/tex-live)
- Post to [comp.text.tex](https://groups.google.com/g/comp.text.tex)
- Announce on relevant TeX communities (TeX Stack Exchange, TeX-related Discords)

### 4.3 Update documentation

Once the package is live on CTAN:

- Add `tlmgr install omnilatex` as a primary installation method in `README.md`
- Update `CONTRIBUTING.md` to note CTAN installation
- Add a "CTAN" badge to the repository

## 5. Version Bumps

For each new release:

1. Update `VERSION.md` with the new version and release date
2. Update `CHANGELOG.md` with the release notes
3. Re-run `bash scripts/make-ctan-zip.sh`
4. Verify with `pytest tests/test_ctan.py`
5. Upload the new `omnilatex.zip` to CTAN at https://ctan.org/upload
6. Tag the release in Git (e.g. `git tag v1.11.0`)
