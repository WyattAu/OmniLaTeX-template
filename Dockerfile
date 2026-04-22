# OmniLaTeX Build Environment
# ============================
# Reproducible Docker image for building OmniLaTeX documents.
#
# Build:  docker build -t omnilatex -f Dockerfile .
# Run:    docker run -it --rm -v $(pwd):/workspace omnilatex
#
# This image includes:
#   - TeX Live 2024 with all required packages
#   - Custom fonts (Monaspace Neon, Atkinson Hyperlegible Next)
#   - Python 3 with Pygments (for minted code listings)
#   - Inkscape (for SVG conversion)
#   - Git (for version metadata)

FROM texlive/texlive:TL2024-historic

LABEL maintainer="Wyatt Au"
LABEL description="OmniLaTeX document build environment"
LABEL org.opencontainers.image.source="https://github.com/WyattAu/OmniLaTeX-template"

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# ── System packages ────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    git \
    inkscape \
    gnuplot \
    curl \
    wget \
    fonts-noto \
    fonts-liberation \
  && rm -rf /var/lib/apt/lists/*

# ── TeX Live packages ──────────────────────────────
# Core packages (scheme-medium provides most)
RUN tlmgr update --self && \
    tlmgr install \
    iftex \
    etoolbox \
    kvoptions \
    setspace \
    setspaceenhanced \
    adjustbox \
    xkeyval \
    import \
    xstring \
    xcolor \
    todonotes \
    hologo \
    censor \
    cancel \
    fontspec \
    amsmath \
    amsfonts \
    amssymb \
    lualatex-math \
    fontawesome5 \
    unicode-math \
    microtype \
    ragged2e \
    blindtext \
    pdflscape \
    url \
    enumitem \
    mathtools \
    chemmacros \
    siunitx \
    eurosym \
    xfrac \
    caption \
    subcaption \
    tcolorbox \
    svg \
    scalerel \
    contour \
    pgfplots \
    tikz-3dplot \
    circuitikz \
    forest \
    minted \
    accsupp \
    fvextra \
    multirow \
    booktabs \
    longtable \
    tabularray \
    hyperref \
    bookmark \
    glossaries-extra \
    biblatex-ext \
    biber \
    bib2gls \
    polyglossia \
    translations \
    tracklang \
    nicefrac \
    empheq \
    fix-cm \
    flafter \
    pgfplotstable \
  && tlmgr path add

# ── Python packages ─────────────────────────────────
RUN pip3 install --break-system-packages --no-cache-dir \
    pygments

# ── Custom fonts ────────────────────────────────────
# Monaspace Neon (monospace/code)
RUN mkdir -p /usr/share/fonts/truetype/monaspace-neon && \
    wget -q "https://github.com/chriskapp/neon-monospace/releases/download/v1.000/MonaspaceNeon-v1.000.zip" \
         -O /tmp/monaspace.zip && \
    unzip -q /tmp/monaspace.zip -d /tmp/monaspace && \
    cp /tmp/monaspace/fonts/otf/*.otf /usr/share/fonts/truetype/monaspace-neon/ && \
    rm -rf /tmp/monaspace.zip /tmp/monaspace && \
    fc-cache -f

# Atkinson Hyperlegible Next (sans-serif)
RUN mkdir -p /usr/share/fonts/truetype/atkinson-hyperlegible && \
    wget -q "https://github.com/BrailleInstitute/Atkinson-Hyperlegible-Next-Font/releases/download/v1.000/Atkinson-Hyperlegible-Next-Font-v1.000.zip" \
         -O /tmp/atkinson.zip && \
    unzip -q /tmp/atkinson.zip -d /tmp/atkinson && \
    cp /tmp/atkinson/fonts/Static/TTF/*.ttf /usr/share/fonts/truetype/atkinson-hyperlegible/ && \
    rm -rf /tmp/atkinson.zip /tmp/atkinson && \
    fc-cache -f

# ── Environment variables ───────────────────────────
ENV IS_OMNILATEX_CONTAINER=true
ENV OMNILATEX_MODE=prod
ENV TEXMFHOME=/usr/share/texmf
ENV PATH="/usr/share/texlive/texmf-dist/scripts/latexmk:${PATH}"

# ── Working directory ──────────────────────────────
WORKDIR /workspace

# Default: build all examples
CMD ["python3", "build.py", "--mode", "prod", "build-examples"]
