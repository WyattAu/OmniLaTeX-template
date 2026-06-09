# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| v2.5.x  | Yes |
| v2.4.x  | Yes |
| v2.3.x  | Yes |
| v2.2.x  | Yes |
| v2.0.x  | Yes |
| v1.x    | No |

## Reporting a Vulnerability

To report a security vulnerability, please use [GitHub Security Advisories](https://github.com/WyattAu/OmniLaTeX-template/security/advisories/new).

Alternatively, email the maintainer directly. Do not open public issues for security vulnerabilities.

## Response Timeline

- Acknowledgment within 48 hours
- Initial assessment within 1 week
- Patch or mitigation within 2 weeks (critical: 48 hours)

## Supply Chain

- Docker images are built from pinned Dockerfile and referenced by SHA-256 digest
- Most GitHub Actions are pinned to commit SHA; `actions/checkout` uses `@v6` tag
- Dependency review runs on every pull request
- `.env.docker` digest is validated by pre-push hook
