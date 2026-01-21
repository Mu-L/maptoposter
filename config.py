"""Configuration module for system settings and environment variables.

This module provides centralized configuration management with support for
environment variable overrides and validation.
"""

import os
from dataclasses import dataclass
from pathlib import Path


def _get_default_path(env_var: str, relative_path: str) -> Path:
    """Get default path, checking environment variable first, then using relative path.
    
    Args:
        env_var: Environment variable name
        relative_path: Relative path from this module's directory
        
    Returns:
        Resolved Path object
    """
    if env_var in os.environ:
        return Path(os.environ[env_var])
    
    # Get the directory where this config.py file is located
    module_dir = Path(__file__).parent
    return module_dir / relative_path


@dataclass
class Config:
    """System configuration with defaults."""

    # Directory paths
    cache_dir: Path
    themes_dir: Path
    fonts_dir: Path
    output_dir: Path

    # Geocoding settings
    geocoding_user_agent: str = "city_map_poster"
    geocoding_timeout: int = 10
    geocoding_rate_limit: float = 1.0  # seconds

    # Data fetching settings
    graph_rate_limit: float = 0.5  # seconds
    features_rate_limit: float = 0.3  # seconds

    # Rendering settings
    default_figure_size: tuple[float, float] = (12.0, 16.0)
    default_dpi: int = 300
    default_distance: int = 29000  # meters

    def __init__(
        self,
        cache_dir: Path | None = None,
        themes_dir: Path | None = None,
        fonts_dir: Path | None = None,
        output_dir: Path | None = None,
        geocoding_user_agent: str = "city_map_poster",
        geocoding_timeout: int = 10,
        geocoding_rate_limit: float = 1.0,
        graph_rate_limit: float = 0.5,
        features_rate_limit: float = 0.3,
        default_figure_size: tuple[float, float] = (12.0, 16.0),
        default_dpi: int = 300,
        default_distance: int = 29000,
    ):
        """Initialize configuration with environment variable support.

        Args:
            cache_dir: Cache directory path (defaults to CACHE_DIR env var or ".cache")
            themes_dir: Themes directory path (defaults to THEMES_DIR env var or "themes")
            fonts_dir: Fonts directory path (defaults to FONTS_DIR env var or "fonts")
            output_dir: Output directory path (defaults to OUTPUT_DIR env var or "posters")
            geocoding_user_agent: User agent for geocoding requests
            geocoding_timeout: Timeout for geocoding requests in seconds
            geocoding_rate_limit: Minimum seconds between geocoding requests
            graph_rate_limit: Minimum seconds between graph requests
            features_rate_limit: Minimum seconds between feature requests
            default_figure_size: Default figure size in inches (width, height)
            default_dpi: Default DPI for raster outputs
            default_distance: Default map radius in meters
        """
        self.cache_dir = cache_dir if cache_dir is not None else _get_default_path("CACHE_DIR", ".cache")
        self.themes_dir = themes_dir if themes_dir is not None else _get_default_path("THEMES_DIR", "themes")
        self.fonts_dir = fonts_dir if fonts_dir is not None else _get_default_path("FONTS_DIR", "fonts")
        self.output_dir = output_dir if output_dir is not None else _get_default_path("OUTPUT_DIR", "posters")

        self.geocoding_user_agent = geocoding_user_agent
        self.geocoding_timeout = geocoding_timeout
        self.geocoding_rate_limit = geocoding_rate_limit
        self.graph_rate_limit = graph_rate_limit
        self.features_rate_limit = features_rate_limit
        self.default_figure_size = default_figure_size
        self.default_dpi = default_dpi
        self.default_distance = default_distance

    def validate(self) -> None:
        """Validate configuration values and create directories.

        Raises:
            ValueError: If configuration values are invalid
        """
        # Validate numeric values
        if self.geocoding_timeout <= 0:
            raise ValueError("geocoding_timeout must be positive")
        if self.geocoding_rate_limit < 0:
            raise ValueError("geocoding_rate_limit must be non-negative")
        if self.graph_rate_limit < 0:
            raise ValueError("graph_rate_limit must be non-negative")
        if self.features_rate_limit < 0:
            raise ValueError("features_rate_limit must be non-negative")
        if self.default_dpi <= 0:
            raise ValueError("default_dpi must be positive")
        if self.default_distance <= 0:
            raise ValueError("default_distance must be positive")
        if self.default_figure_size[0] <= 0 or self.default_figure_size[1] <= 0:
            raise ValueError("default_figure_size dimensions must be positive")

        # Create directories if they don't exist
        for dir_path in [self.cache_dir, self.themes_dir, self.fonts_dir, self.output_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)


def load_config() -> Config:
    """Load and validate configuration.

    Returns:
        Validated Config object

    Raises:
        ValueError: If configuration is invalid
    """
    config = Config()
    config.validate()
    return config
