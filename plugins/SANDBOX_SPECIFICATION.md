# OmniLaTeX Plugin Sandbox Specification

## Overview

The plugin sandbox restricts third-party plugins to prevent security risks and system instability. Plugins execute in a controlled environment with limited capabilities.

## Security Model

### Principle of Least Privilege

Plugins receive only the capabilities required for their stated function. All capabilities default to denied unless explicitly requested in the plugin manifest.

### Capability Matrix

| Capability | Default | Manifest Key | Description |
|------------|---------|--------------|-------------|
| Shell escape | Denied | `security.shell_escape` | Execute shell commands |
| File write | Denied | `security.file_write` | Write files outside build directory |
| Network access | Denied | (not configurable) | Make HTTP/HTTPS requests |
| File read | Limited | (not configurable) | Read files outside TEXINPUTS |
| Environment variables | Limited | (not configurable) | Access process environment |
| Process execution | Denied | (not configurable) | Fork/exec processes |

### File System Access

| Path | Read | Write | Notes |
|------|------|-------|-------|
| Current directory | Yes | Yes | Build directory only |
| TEXINPUTS paths | Yes | No | TeX input search path |
| Current directory subtree | Yes | Yes | For build outputs |
| `/tmp` | Yes | Yes | Temporary files |
| `~/texmf/` | Yes | No | User texmf tree |
| System paths | Yes | No | `/usr/share/texmf/` etc. |
| Everything else | No | No | Denied |

### Network Access

All network access is blocked at the LaTeX level:

```latex
% This will fail in sandboxed mode
\immediate\write18{curl http://example.com}  % Blocked
\input{|"curl http://example.com"}            % Blocked
```

### Environment Variables

| Variable | Access | Notes |
|----------|--------|-------|
| `PATH` | Read-only | Limited to TeX Live binaries |
| `TEXINPUTS` | Read-only | TeX input search path |
| `HOME` | Read-only | Redirected to temp directory |
| `USER` | Read-only | May be anonymized |
| `CI` | Read-only | CI detection |
| `OMNILATEX_VERBOSE` | Read-only | Verbose mode flag |
| All others | Denied | Not accessible |

## Manifest Declaration

Plugins declare required capabilities in `manifest.toml`:

```toml
[plugin.security]
shell_escape = false    # Set to true if shell escape is required
file_write = false      # Set to true if file write is required
network = false         # Always false (not configurable)
```

### Validation Rules

1. `shell_escape = true` requires explicit user consent during installation
2. `file_write = true` is limited to the build directory
3. `network = true` is rejected (always forced to false)
4. Missing `[plugin.security]` section defaults to all denied

## Enforcement Mechanism

### LaTeX Level

```latex
% In omnilatex.cls, sandbox mode is enabled by default
\RequirePackage{kvoptions}
\DeclareStringOption[restricted]{sandbox}

% Shell escape check
\ifx\omnilatex@sandbox\@empty
  \ClassWarning{omnilatex}{Sandbox mode not configured}%
\fi
```

### Build System Level

```python
# In buildlib/builder.py
SANDBOX_ENV = {
    "TEXINPUTS": os.pathsep.join([".", str(REPO_ROOT), ""]),
    "PATH": os.environ.get("PATH", ""),
    "HOME": tempfile.mkdtemp(),
    "OMNILATEX_SANDBOX": "1",
}

def _create_sandbox_env():
    env = os.environ.copy()
    # Remove sensitive variables
    for key in list(env.keys()):
        if key not in ALLOWED_ENV_VARS:
            del env[key]
    env.update(SANDBOX_ENV)
    return env
```

### CI Level

```yaml
# In GitHub Actions workflow
- name: Build with sandbox
  run: |
    docker run --rm \
      --network none \
      --read-only \
      --tmpfs /tmp:size=100M \
      -v $(pwd):/workspace \
      -w /workspace \
      ghcr.io/wyattau/omnilatex-docker:latest \
      python build.py build-example minimal-starter
```

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Plugin exfiltrates data | Low | High | Network blocked |
| Plugin corrupts system files | Low | High | File write restricted |
| Plugin executes malicious code | Low | Critical | Shell escape blocked |
| Plugin accesses secrets | Low | High | Environment sanitized |
| Plugin causes denial of service | Medium | Medium | Resource limits |

## Testing Sandbox

```bash
# Test a plugin in sandbox mode
python build.py test-plugin <plugin-name> --sandbox

# Verify sandbox restrictions
python build.py verify-sandbox <plugin-name>

# Run with full sandbox logging
python build.py build-example <example> --sandbox --verbose
```
