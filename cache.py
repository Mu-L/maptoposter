"""Cache module for persistent storage of downloaded data.

This module provides caching functionality for geocoding results and OSM data
to avoid redundant API calls and improve performance.
"""

import pickle
from hashlib import md5
from pathlib import Path
from typing import Any


class CacheError(Exception):
    """Raised when cache operations fail."""

    pass


class CacheManager:
    """Manages caching of data to disk using pickle."""

    def __init__(self, cache_dir: Path) -> None:
        """Initialize cache manager.

        Args:
            cache_dir: Directory path for cache storage
        """
        self.cache_dir = Path(cache_dir)
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise CacheError(f"Failed to create cache directory '{cache_dir}': {e}") from e

    def _cache_key_to_filename(self, key: str) -> str:
        """Convert cache key to safe filename using MD5 hash.

        Args:
            key: Cache key string

        Returns:
            Hashed filename with .pkl extension
        """
        return md5(key.encode()).hexdigest() + ".pkl"

    def get(self, key: str) -> Any | None:
        """Retrieve cached data.

        Args:
            key: Cache key

        Returns:
            Cached object or None if not found

        Raises:
            CacheError: If deserialization fails
        """
        filename = self._cache_key_to_filename(key)
        cache_path = self.cache_dir / filename

        if not cache_path.exists():
            return None

        try:
            with open(cache_path, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            raise CacheError(f"Failed to load cached data for key '{key}': {e}") from e

    def set(self, key: str, value: Any) -> None:
        """Store data in cache.

        Args:
            key: Cache key
            value: Object to cache

        Raises:
            CacheError: If serialization or file write fails
        """
        filename = self._cache_key_to_filename(key)
        cache_path = self.cache_dir / filename

        try:
            with open(cache_path, "wb") as f:
                pickle.dump(value, f, protocol=pickle.HIGHEST_PROTOCOL)
        except Exception as e:
            raise CacheError(f"Failed to cache data for key '{key}': {e}") from e

    def exists(self, key: str) -> bool:
        """Check if cache key exists.

        Args:
            key: Cache key

        Returns:
            True if cached data exists, False otherwise
        """
        filename = self._cache_key_to_filename(key)
        cache_path = self.cache_dir / filename
        return cache_path.exists()

    def clear(self) -> None:
        """Remove all cached data.

        Raises:
            CacheError: If clearing cache fails
        """
        try:
            for cache_file in self.cache_dir.glob("*.pkl"):
                cache_file.unlink()
        except Exception as e:
            raise CacheError(f"Failed to clear cache directory '{self.cache_dir}': {e}") from e
