#!/usr/bin/env python3
"""Generate .tlg baselines by compiling .lvt files and normalizing logs.

This mimics l3build's normalize_log function from l3build-check.lua.
"""

import re
import subprocess
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESTFILES = os.path.join(ROOT, "testfiles")
WORKDIR = "/tmp/l3test_gen"

MAXPRINTLINE = 79  # LuaTeX default


def normalize_log(content):
    """Simplified version of l3build's normalize_log for LuaTeX."""
    lines = content.split("\n")
    result = []
    prestart = True
    skipping = False
    drop_fd = False
    lastline = ""

    for raw_line in lines:
        if raw_line == "START-TEST-LOG":
            prestart = False
            continue
        elif raw_line == "END-TEST-LOG" or raw_line.startswith("Here is how much of"):
            break
        elif raw_line == "OMIT":
            skipping = True
            continue
        elif raw_line == "TIMO" or raw_line.endswith("TIMO"):
            skipping = False
            continue

        if prestart or skipping:
            continue

        # Handle wrapped lines: if line is exactly MAXPRINTLINE chars and
        # doesn't end with "...", it wraps to the next line
        if len(raw_line) == MAXPRINTLINE and not raw_line.endswith("..."):
            lastline = (lastline or "") + raw_line
            continue

        line = (lastline or "") + raw_line
        lastline = ""

        # Skip \openout lines
        if re.match(r"^\\openout\d\d? = ", line):
            continue

        # Skip empty lines
        if not line.strip():
            continue

        # Zap line numbers from \show
        line = re.sub(r"^l\.\d+ ", "l. ...", line)

        # Zap ./ at begin of filename
        line = re.sub(r"\(\./", "(", line)

        # Zap full paths: (/full/path/file.ext -> (../file.ext
        # Pattern: any path with a file extension
        path_pat = r"[a-zA-Z]?:?/[^ ()<>]*/([^/()]+\.\w+)"
        line = re.sub(r"\(" + path_pat, r"(../\1", line)
        line = re.sub(r"<" + path_pat + r">", r"<../\1>", line)
        line = re.sub(r"from " + path_pat + r"$", r"from ../\1", line)
        line = re.sub(r": " + path_pat + r"\)", r": ../\1)", line)
        # Root cache directory
        line = re.sub(
            r'Root cache directory is "' + path_pat + r'"',
            r'Root cache directory is ".../\1"',
            line,
        )

        # Handle dates: YYYY/MM/DD or YYYY-MM-DD -> ....-..-..
        if re.search(r"[^<]\d{4}[/\-]\d{2}[/\-]\d{2}", line):
            line = re.sub(r"\d{4}[/\-]\d{2}[/\-]\d{2}", "....-..-..", line)
            # Semantic version strings near dates
            line = re.sub(r"v\d+\.\d+\.\d+[\d\w.+\-]*", "v...", line)
            line = re.sub(r"v\d+\.?\d?\d?\w?", "v...", line)

        # Zap "on input line N" and "on line N"
        line = re.sub(r"on input line \d+", "on input line ...", line)
        line = re.sub(r"on line \d+", "on line ...", line)
        # LaTeX wrapped line number: (typearea)   1234. -> (typearea)   ....
        m = re.match(r"^(\(\w+\))\s+\d+\.$", line)
        if m:
            line = re.sub(r"\d+\.", "....", line)

        # Handle register allocation: \count123 -> \count...
        regtypes = [
            "attribute",
            "box",
            "count",
            "dimen",
            "insert",
            "language",
            "muskip",
            "read",
            "skip",
            "toks",
            "write",
        ]
        for rt in regtypes:
            if re.match(r"^\\(" + rt + r")\d+$", line):
                line = re.sub(r"\d+$", "...", line)

        # Drop .fd file lines
        if re.match(r"^ *\([./\w]+\.fd[^)]*$", line):
            drop_fd = True
            continue
        if drop_fd:
            if re.match(r" *\)", line):
                drop_fd = False
            continue

        result.append(line)

    return "\n".join(result) + "\n"


def main():
    os.makedirs(WORKDIR, exist_ok=True)
    os.chdir(WORKDIR)

    tests = [
        "omnilatex-base",
        "omnilatex-fonts",
        "omnilatex-tables",
        "omnilatex-document",
        "omnilatex-floats",
        "omnilatex-hyperref",
        "omnilatex-i18n",
        "omnilatex-math",
    ]

    for name in tests:
        src = os.path.join(TESTFILES, f"{name}.lvt")
        shutil.copy2(src, f"./{name}.lvt")

        try:
            subprocess.run(
                [
                    "lualatex",
                    "--interaction=nonstopmode",
                    "--halt-on-error",
                    f"{name}.lvt",
                ],
                capture_output=True,
                text=True,
                timeout=90,
            )
        except subprocess.TimeoutExpired:
            print(f"TIMEOUT: {name}")
            continue

        logpath = f"{name}.log"
        if os.path.exists(logpath):
            with open(logpath) as f:
                content = f.read()

            normalized = normalize_log(content)

            tlgpath = os.path.join(TESTFILES, f"{name}.tlg")
            with open(tlgpath, "w") as f:
                f.write(normalized)
            nlines = len(normalized.splitlines())
            print(f"OK: {name} ({nlines} lines)")
        else:
            print(f"FAIL: {name} - no log")


if __name__ == "__main__":
    main()
