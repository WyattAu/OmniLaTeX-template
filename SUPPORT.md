# Support

## Getting Help

- **Documentation:** See [docs/](docs/) for the user guide and gallery
- **Questions:** Open a [Discussion](https://github.com/WyattAu/OmniLaTeX-template/discussions)
- **Bug reports:** Open an [Issue](https://github.com/WyattAu/OmniLaTeX-template/issues)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines, including how to add institution configs, languages, and document types.

## Installation Issues

1. Ensure TeX Live 2025+ is installed with LuaLaTeX support
2. Run `python build.py preflight` to check your environment
3. Check the [CI workflow](.github/workflows/build.yml) for a known-good setup
4. Try the Docker image: `docker run -it --rm -v $(pwd):/workspace ghcr.io/wyattau/omnilatex-docker:latest`
