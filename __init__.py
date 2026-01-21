"""Map Poster Generator - Create beautiful map posters for any city.

This package provides a modular system for generating artistic map posters
from OpenStreetMap data. It features:

- Geocoding support for any city/country
- Caching for improved performance
- Multiple visual themes
- Customizable rendering
- Support for PNG, SVG, and PDF output formats

Example usage:
    >>> from maptoposter import create_app
    >>> app = create_app()
    >>> app.generate_poster("Paris", "France", "noir", 10000, "png")

Main components:
    - PosterGenerator: Main orchestrator for poster generation
    - CacheManager: Persistent storage for downloaded data
    - NominatimGeocoder: Location name to coordinates conversion
    - OSMDataFetcher: OpenStreetMap data retrieval
    - ThemeManager: Visual theme management
    - StandardRenderer: Map rendering engine
    - OutputManager: File naming and output management

For command-line usage, see:
    python -m maptoposter.create_map_poster --help
"""

from cache import CacheError, CacheManager
from config import Config, load_config
from create_map_poster import PosterGenerator, create_app
from data_fetching import (
    AsyncOSMDataFetcher,
    DataFetcherInterface,
    OSMDataFetcher,
)
from geocoding import GeocoderInterface, NominatimGeocoder
from output import OutputManager
from renderer import RendererInterface, StandardRenderer
from theme import Theme, ThemeManager
from typography import FontSet, TypographyManager

__version__ = "2.0.0"
__author__ = "Map Poster Generator Contributors"
__license__ = "MIT"

__all__ = [
    # Main application
    "PosterGenerator",
    "create_app",
    # Cache
    "CacheManager",
    "CacheError",
    # Configuration
    "Config",
    "load_config",
    # Geocoding
    "GeocoderInterface",
    "NominatimGeocoder",
    # Data fetching
    "DataFetcherInterface",
    "OSMDataFetcher",
    "AsyncOSMDataFetcher",
    # Themes
    "Theme",
    "ThemeManager",
    # Typography
    "FontSet",
    "TypographyManager",
    # Rendering
    "RendererInterface",
    "StandardRenderer",
    # Output
    "OutputManager",
    # Version
    "__version__",
]
