"""Build cache management mixin.

Provides methods for loading, saving, evicting, and checking the build cache.
The cache maps example names to their source hash, mtimes, and build metadata.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import logging
import threading
from pathlib import Path

import buildlib.config as _cfg

logger = logging.getLogger("omnilatex")


class BuildCacheMixin:
    """Mixin providing build cache operations.

    Requires self.config, self._cache_lock, self._shared_build_cache
    to be set by the inheriting class.
    """

    @staticmethod
    def _hash_for_paths(paths: list[Path]) -> str:
        """Compute SHA-256 hash of all file contents, sorted by path."""
        h = hashlib.sha256()
        for p in sorted(paths):
            if p.exists():
                h.update(p.read_bytes())
        return h.hexdigest()

    @staticmethod
    def _get_mtimes(paths: list[Path]) -> dict[str, float]:
        """Get modification times for all paths. Used for fast cache checks."""
        mtimes: dict[str, float] = {}
        for p in paths:
            if p.exists():
                mtimes[str(p)] = p.stat().st_mtime
        return mtimes

    def _cache_hit(self, example_name: str, source_files: list[Path]) -> bool:
        """Check if cached build is still valid using mtime fast-path.

        Returns True if the cache entry exists, all source file mtimes match
        the cached mtimes, and the output PDF exists. This avoids reading
        every file to compute the full SHA-256 hash when nothing changed.
        """
        with self._cache_lock:
            if self._shared_build_cache is not None:
                cache = self._shared_build_cache
            else:
                cache = self._load_build_cache()
            cached = cache.get(f"examples/{example_name}")

        if not cached:
            return False

        # Fast path: check mtimes first (stat-only, no file reads)
        cached_mtimes = cached.get("mtimes")
        if cached_mtimes:
            current_mtimes = self._get_mtimes(source_files)
            if current_mtimes == cached_mtimes:
                dest_pdf = (
                    _cfg.REPO_ROOT / self.config.build_dir / _cfg.BUILD_EXAMPLES_SUBDIR
                ) / f"{example_name}.pdf"
                return dest_pdf.exists()

        # Slow path: full hash comparison
        source_hash = self._hash_for_paths(source_files)
        dest_pdf = (
            _cfg.REPO_ROOT / self.config.build_dir / _cfg.BUILD_EXAMPLES_SUBDIR
        ) / f"{example_name}.pdf"
        return (
            cached.get("source_hash") == source_hash
            and dest_pdf.exists()
        )

    def _load_build_cache(self) -> dict:
        """Load the build cache from disk. Returns empty dict on missing/corrupt file."""
        cache_path = self.config.build_dir / "build_cache.json"
        if cache_path.exists():
            try:
                return json.loads(cache_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                logger.debug("Failed to load build cache", exc_info=True)
        return {}

    def _evict_cache(
        self, cache: dict, max_entries: int = 100, max_age_days: int = 90
    ) -> dict:
        """Evict stale cache entries: TTL first, then LRU count cap."""
        now = datetime.datetime.now(datetime.timezone.utc)
        cutoff = now - datetime.timedelta(days=max_age_days)
        cutoff_str = cutoff.strftime("%Y-%m-%dT%H:%M:%SZ")

        # Phase 1: Remove expired entries
        to_remove = [
            k
            for k, v in cache.items()
            if k.startswith("examples/") and v.get("build_time", "") < cutoff_str
        ]
        for key in to_remove:
            del cache[key]

        # Phase 2: Cap entry count by LRU (oldest build_time first)
        entries = {k: v for k, v in cache.items() if k.startswith("examples/")}
        if len(entries) > max_entries:
            sorted_keys = sorted(
                entries.keys(), key=lambda k: entries[k].get("build_time", "")
            )
            for key in sorted_keys[: len(entries) - max_entries]:
                del cache[key]

        return cache

    def _save_build_cache(self, cache: dict) -> None:
        """Save the build cache to disk, evicting stale entries first."""
        cache = self._evict_cache(cache)
        cache_path = self.config.build_dir / "build_cache.json"
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(
            json.dumps(cache, indent=2) + "\n",
            encoding="utf-8",
        )

    def cmd_cache_stats(self, _: object | None = None) -> None:
        """Display build cache statistics."""
        self.ui.header("Build Cache Statistics")
        cache_path = _cfg.REPO_ROOT / self.config.build_dir / "build_cache.json"
        if not cache_path.exists():
            self.ui.info("No build cache found.")
            return
        cache_data = self._load_build_cache()
        entries = {k: v for k, v in cache_data.items() if k.startswith("examples/")}
        total_examples = len(self.discover_examples())
        cached_examples = len(entries)
        file_size = cache_path.stat().st_size
        mtimes = [(k, v["build_time"]) for k, v in entries.items() if "build_time" in v]
        mtimes.sort(key=lambda x: x[1])
        self.ui.info(f"Cached entries:    {cached_examples}")
        self.ui.info(f"Cache file size:   {file_size:,} bytes")
        self.ui.info(f"Total examples:    {total_examples}")
        self.ui.info(f"Cached examples:   {cached_examples}/{total_examples}")
        if mtimes:
            self.ui.info(f"Oldest entry:      {mtimes[0][0]} ({mtimes[0][1]})")
            self.ui.info(f"Newest entry:      {mtimes[-1][0]} ({mtimes[-1][1]})")
        self.ui.success("Cache statistics complete.")

    def cmd_cache_clear(self, _: object | None = None) -> None:
        """Delete the build cache file."""
        self.ui.header("Clearing Build Cache")
        cache_path = _cfg.REPO_ROOT / self.config.build_dir / "build_cache.json"
        if cache_path.exists():
            cache_path.unlink()
            self.ui.success(f"Deleted build cache: {cache_path}")
        else:
            self.ui.info("No build cache file to delete.")
