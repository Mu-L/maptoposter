"""Geocoding module for converting location names to coordinates.

This module provides geocoding functionality with caching and rate limiting
to convert city/country names to geographic coordinates.
"""

import asyncio
import time
from abc import ABC, abstractmethod
from typing import Optional

from geopy.geocoders import Nominatim

from cache import CacheError, CacheManager


class GeocoderInterface(ABC):
    """Abstract interface for geocoding services."""

    @abstractmethod
    def geocode(self, city: str, country: str) -> tuple[float, float]:
        """Get coordinates for a location.

        Args:
            city: City name
            country: Country name

        Returns:
            Tuple of (latitude, longitude)

        Raises:
            ValueError: If location cannot be found
        """
        pass


class NominatimGeocoder(GeocoderInterface):
    """Geocoder using Nominatim service with caching."""

    def __init__(self, cache: CacheManager, user_agent: str, timeout: int = 10, rate_limit: float = 1.0) -> None:
        """Initialize geocoder.

        Args:
            cache: Cache manager for storing results
            user_agent: User agent string for API requests
            timeout: Request timeout in seconds
            rate_limit: Minimum seconds between requests
        """
        self.cache = cache
        self.geolocator = Nominatim(user_agent=user_agent, timeout=timeout)
        self.rate_limit = rate_limit
        self.last_request_time: Optional[float] = None

    def _rate_limit_wait(self) -> None:
        """Enforce rate limiting between requests."""
        if self.last_request_time is not None:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.rate_limit:
                time.sleep(self.rate_limit - elapsed)
        self.last_request_time = time.time()

    def _cache_key(self, city: str, country: str) -> str:
        """Generate cache key for location.

        Args:
            city: City name
            country: Country name

        Returns:
            Cache key string
        """
        return f"coords_{city.lower()}_{country.lower()}"

    def geocode(self, city: str, country: str) -> tuple[float, float]:
        """Get coordinates with caching and rate limiting.

        Args:
            city: City name
            country: Country name

        Returns:
            Tuple of (latitude, longitude)

        Raises:
            ValueError: If location cannot be found or geocoding fails
        """
        cache_key = self._cache_key(city, country)

        # Check cache first
        cached = self.cache.get(cache_key)
        if cached is not None:
            print(f"✓ Using cached coordinates for {city}, {country}")
            return cached

        # Fetch from API
        print(f"Looking up coordinates for {city}, {country}...")
        self._rate_limit_wait()

        try:
            location = self.geolocator.geocode(f"{city}, {country}")

            # Handle async responses if needed
            if asyncio.iscoroutine(location):
                location = asyncio.run(location)

            if location is None:
                raise ValueError(f"Could not find coordinates for {city}, {country}")

            coords = (location.latitude, location.longitude)

            # Display results
            if hasattr(location, "address"):
                print(f"✓ Found: {location.address}")
            print(f"✓ Coordinates: {coords[0]:.4f}, {coords[1]:.4f}")

            # Cache results
            try:
                self.cache.set(cache_key, coords)
            except CacheError as e:
                print(f"Warning: {e}")

            return coords

        except Exception as e:
            raise ValueError(f"Geocoding failed for {city}, {country}: {e}") from e
