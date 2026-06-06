# watermark

Add watermarks to OmniLaTeX documents.

## Usage

```latex
\useplugin{watermark}

% Add a watermark to every page
\watermark{DRAFT}

% Change color and size
\setWatermarkColor{red!30}
\setWatermarkSize{\fontsize{80}{96}\selectfont}
\watermark{CONFIDENTIAL}

% Remove watermark
\clearWatermark
```

## License

Apache-2.0
