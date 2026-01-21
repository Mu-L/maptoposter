"""Data fetching module for downloading OSM street networks and features.

This module provides functionality to fetch street network graphs and
geographic features from OpenStreetMap with caching and rate limiting.
"""

import asyncio
import time
from abc import ABC, abstractmethod
from typing import Optional

import osmnx as ox
from geopandas import GeoDataFrame
from networkx import MultiDiGraph

from cache import CacheError, CacheManager


class DataFetcherInterface(ABC):
    """Abstract interface for fetching map data."""

    @abstractmethod
    def fetch_graph(self, point: tuple[float, float], dist: int) -> Optional[MultiDiGraph]:
        """Fetch street network graph.

        Args:
            point: Tuple of (latitude, longitude)
            dist: Distance in meters

        Returns:
            Street network graph or None if fetch fails
        """
        pass

    @abstractmethod
    def fetch_features(
        self, point: tuple[float, float], dist: int, tags: dict[str, str | bool | list[str]], name: str
    ) -> Optional[GeoDataFrame]:
        """Fetch geographic features.

        Args:
            point: Tuple of (latitude, longitude)
            dist: Distance in meters
            tags: OSM tags to filter features
            name: Name of feature type for logging

        Returns:
            GeoDataFrame of features or None if fetch fails
        """
        pass


class OSMDataFetcher(DataFetcherInterface):
    """Fetches data from OpenStreetMap using OSMnx."""

    def __init__(self, cache: CacheManager, graph_rate_limit: float = 0.5, features_rate_limit: float = 0.3) -> None:
        """Initialize data fetcher.

        Args:
            cache: Cache manager for storing results
            graph_rate_limit: Seconds between graph requests
            features_rate_limit: Seconds between feature requests
        """
        self.cache = cache
        self.graph_rate_limit = graph_rate_limit
        self.features_rate_limit = features_rate_limit
        self.last_graph_request: Optional[float] = None
        self.last_features_request: Optional[float] = None

    def _rate_limit_wait(self, request_type: str) -> None:
        """Enforce rate limiting for specific request type.

        Args:
            request_type: Either "graph" or "features"
        """
        if request_type == "graph":
            last_time = self.last_graph_request
            limit = self.graph_rate_limit
        else:
            last_time = self.last_features_request
            limit = self.features_rate_limit

        if last_time is not None:
            elapsed = time.time() - last_time
            if elapsed < limit:
                time.sleep(limit - elapsed)

        if request_type == "graph":
            self.last_graph_request = time.time()
        else:
            self.last_features_request = time.time()

    def _graph_cache_key(self, point: tuple[float, float], dist: int) -> str:
        """Generate cache key for graph.

        Args:
            point: Tuple of (latitude, longitude)
            dist: Distance in meters

        Returns:
            Cache key string
        """
        lat, lon = point
        return f"graph_{lat}_{lon}_{dist}"

    def _features_cache_key(
        self, point: tuple[float, float], dist: int, tags: dict[str, str | bool | list[str]], name: str
    ) -> str:
        """Generate cache key for features.

        Args:
            point: Tuple of (latitude, longitude)
            dist: Distance in meters
            tags: OSM tags dictionary
            name: Feature name

        Returns:
            Cache key string
        """
        lat, lon = point
        tag_str = "_".join(sorted(tags.keys()))
        return f"{name}_{lat}_{lon}_{dist}_{tag_str}"

    def fetch_graph(self, point: tuple[float, float], dist: int) -> Optional[MultiDiGraph]:
        """Fetch street network with caching.

        Args:
            point: Tuple of (latitude, longitude)
            dist: Distance in meters

        Returns:
            Street network graph or None if fetch fails
        """
        cache_key = self._graph_cache_key(point, dist)

        # Check cache
        cached = self.cache.get(cache_key)
        if cached is not None:
            print("✓ Using cached street network")
            return cached

        # Fetch from OSM
        self._rate_limit_wait("graph")

        try:
            G = ox.graph_from_point(point, dist=dist, dist_type="bbox", network_type="all")

            # Cache result
            try:
                self.cache.set(cache_key, G)
            except CacheError as e:
                print(f"Warning: {e}")

            return G

        except Exception as e:
            print(f"OSMnx error while fetching graph: {e}")
            return None

    def fetch_features(
        self, point: tuple[float, float], dist: int, tags: dict[str, str | bool | list[str]], name: str
    ) -> Optional[GeoDataFrame]:
        """Fetch geographic features with caching.

        Args:
            point: Tuple of (latitude, longitude)
            dist: Distance in meters
            tags: OSM tags to filter features
            name: Name of feature type for logging

        Returns:
            GeoDataFrame of features or None if fetch fails
        """
        cache_key = self._features_cache_key(point, dist, tags, name)

        # Check cache
        cached = self.cache.get(cache_key)
        if cached is not None:
            print(f"✓ Using cached {name}")
            return cached

        # Fetch from OSM
        self._rate_limit_wait("features")

        try:
            data = ox.features_from_point(point, tags=tags, dist=dist)

            # Cache result
            try:
                self.cache.set(cache_key, data)
            except CacheError as e:
                print(f"Warning: {e}")

            return data

        except Exception as e:
            print(f"OSMnx error while fetching {name}: {e}")
            return None


class AsyncOSMDataFetcher(OSMDataFetcher):
    """Async version of OSM data fetcher for concurrent requests."""

    async def fetch_all_data(
        self, point: tuple[float, float], dist: int
    ) -> tuple[Optional[MultiDiGraph], Optional[GeoDataFrame], Optional[GeoDataFrame]]:
        """Fetch graph, water, and parks concurrently.

        Args:
            point: Tuple of (latitude, longitude)
            dist: Distance in meters

        Returns:
            Tuple of (graph, water_features, park_features)
        """
        # Note: OSMnx is synchronous, so we use asyncio.to_thread
        # to run blocking calls in thread pool
        tasks = [
            asyncio.to_thread(self.fetch_graph, point, dist),
            asyncio.to_thread(self.fetch_features, point, dist, {"natural": "water", "waterway": "riverbank"}, "water"),
            asyncio.to_thread(self.fetch_features, point, dist, {"leisure": "park", "landuse": "grass"}, "parks"),
        ]

        results = await asyncio.gather(*tasks)
        return results[0], results[1], results[2]
