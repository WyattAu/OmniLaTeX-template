"""Unit tests for buildlib.config module."""

from __future__ import annotations

from pathlib import Path

from buildlib.config import (BUILD_EXAMPLES_SUBDIR, FORCE_REBUILD_FLAG,
                             INTERACTION_NONSTOP, LATEXMK_COMMAND,
                             LATEXMK_FORCE_CONTINUE, MAIN_TEX_FILENAME,
                             MINTED_CACHE_SUBDIR, REPO_ROOT,
                             SVG_INKSCAPE_CACHE, ProjectConfig)


class TestConstants:
    """Verify all exported constants have expected values."""

    def test_main_tex_filename(self):
        assert MAIN_TEX_FILENAME == "main.tex"

    def test_latexmk_command(self):
        assert LATEXMK_COMMAND == "latexmk"

    def test_interaction_nonstop(self):
        assert INTERACTION_NONSTOP == "-interaction=nonstopmode"

    def test_force_rebuild_flag(self):
        assert FORCE_REBUILD_FLAG == "-g"

    def test_latexmk_force_continue(self):
        assert LATEXMK_FORCE_CONTINUE == "-f"

    def test_minted_cache_subdir(self):
        assert MINTED_CACHE_SUBDIR == "_minted"

    def test_svg_inkscape_cache(self):
        assert SVG_INKSCAPE_CACHE == "svg-inkscape"

    def test_build_examples_subdir(self):
        assert BUILD_EXAMPLES_SUBDIR == "examples"

    def test_repo_root_is_path(self):
        assert isinstance(REPO_ROOT, Path)

    def test_repo_root_points_to_repo(self):
        """REPO_ROOT should be two levels up from buildlib/."""
        assert (
            REPO_ROOT.name == "OmniLaTeX-template"
            or (REPO_ROOT / "omnilatex.cls").exists()
        )


class TestProjectConfig:
    """Test ProjectConfig dataclass behavior."""

    def test_default_build_dir(self):
        config = ProjectConfig()
        assert config.build_dir == Path("build")

    def test_default_cnf_lines_is_none(self):
        config = ProjectConfig()
        assert config.cnf_lines is None

    def test_custom_build_dir(self):
        config = ProjectConfig(build_dir=Path("custom_build"))
        assert config.build_dir == Path("custom_build")

    def test_is_ci_detects_ci_env(self, monkeypatch):
        monkeypatch.setenv("CI", "true")
        config = ProjectConfig()
        assert config.is_ci() is True

    def test_is_ci_detects_github_actions(self, monkeypatch):
        monkeypatch.delenv("CI", raising=False)
        monkeypatch.setenv("GITHUB_ACTIONS", "true")
        config = ProjectConfig()
        assert config.is_ci() is True

    def test_is_ci_detects_gitlab_ci(self, monkeypatch):
        monkeypatch.delenv("CI", raising=False)
        monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
        monkeypatch.setenv("GITLAB_CI", "true")
        config = ProjectConfig()
        assert config.is_ci() is True

    def test_is_ci_returns_false_when_no_ci_vars(self, monkeypatch):
        monkeypatch.delenv("CI", raising=False)
        monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
        monkeypatch.delenv("GITLAB_CI", raising=False)
        config = ProjectConfig()
        assert config.is_ci() is False

    def test_verbose_enabled_default(self, monkeypatch):
        monkeypatch.delenv("OMNILATEX_VERBOSE", raising=False)
        config = ProjectConfig()
        assert config.verbose_enabled() is False

    def test_verbose_enabled_true_values(self, monkeypatch):
        config = ProjectConfig()
        for val in ["1", "true", "yes", "True", "YES"]:
            monkeypatch.setenv("OMNILATEX_VERBOSE", val)
            assert config.verbose_enabled() is True

    def test_verbose_enabled_false_values(self, monkeypatch):
        config = ProjectConfig()
        for val in ["0", "false", "no", "False", "NO", ""]:
            monkeypatch.setenv("OMNILATEX_VERBOSE", val)
            assert config.verbose_enabled() is False
