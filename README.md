# OmniLaTeX

Hard fork on https://collaborating.tuhh.de/m21/public/theses/itt-latex-template. Aim to provide a wide range of LaTeX boilerplates for multiple use case.

## Docker Container as Dev Environment

LaTeX compilation is a complex process to setup, by using a prebuilt image <ghcr.io/wyattau/omnilatex-docker:latest> we can minimize setup and ensure a consistent environment for development.

## CI/CD

Basic scripts had been written to compile for multiple action providers.

## Git Commit SHA Verification

If the CI build is correctly deployed on pages, the <pages/verify.html> will verify the commit SHA of the PDF against the commit SHA of the repository. This is useful to ensure that the PDF was generated from the latest commit of the repository, allowing the viewer to check whether the PDF is up to date.

### Required CI environment variables

- **`CI_COMMIT_REF_NAME` / `GITHUB_REF_NAME` / `GITHUB_HEAD_REF`**: Branch name used for comparison.
- **`CI_COMMIT_SHA` / `GITHUB_SHA`**: Full commit hash embedded into the PDF.
- **`CI_PROJECT_PATH` / `GITHUB_REPOSITORY` / `FORGEJO_REPOSITORY` / `GITEA_REPOSITORY`**: Repository slug (`owner/project`) for metadata and links.
- **`CI_PROJECT_TITLE` / `CI_PROJECT_NAME`** *(optional)*: Human-friendly project title; otherwise derived from the slug.

### Pages deployment URLs

Expose the final Pages origin so the PDF links point to the verification UI:

- GitHub Pages: handled automatically; no extra secret required.
- Cloudflare Pages or other hosts: set one of the following variables during the LaTeX build job so the template knows the public base URL:
  - **`OMNILATEX_VERIFICATION_BASE_URL`** (preferred)
  - **`CF_PAGES_URL`**, **`PAGES_URL`**, **`DEPLOYMENT_URL`**, or **`PAGES_BASE_URL`**

These variables can be supplied via CI secrets or environment configuration on providers like GitHub Actions, GitLab CI, or Forgejo/Gitea runners.
