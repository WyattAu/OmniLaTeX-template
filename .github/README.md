# GitHub Actions CI/CD

This directory contains GitHub Actions workflows for automated building and testing of the LaTeX template.

## Workflows

### `build.yml`

Automatically builds the LaTeX document and runs validation tests on every push and pull request.

**Features:**
- Compiles the LaTeX document using LuaLaTeX
- Runs automated PDF quality tests
- Uploads PDF artifacts for download
- Python-based test suite validation

**Triggers:**
- Push to `main`, `master`, or `develop` branches
- Pull requests to `main` or `master`
- Manual workflow dispatch

## Setup

No additional setup required - workflows will run automatically once this repository is pushed to GitHub.

## Artifacts

Compiled PDFs are available as workflow artifacts and retained for 30 days.

## Local Testing

To test the build locally before pushing:

```bash
# Build the document
python3 build.py build-tex main.tex

# Run tests
cd tests
poetry install
poetry run pytest -v
```

## Customization

Edit `build.yml` to customize:
- Build triggers
- Artifact retention period
- Additional build steps
- Test configurations
