"""Main entry point for the map poster generator.

This module provides the command-line interface and orchestrates the poster
generation workflow using dependency injection.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

# Add parent directory to path if running as script
if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, str(Path(__file__).parent.parent))

from tqdm import tqdm

from cache import CacheManager
from config import Config, load_config
from data_fetching import DataFetcherInterface, OSMDataFetcher
from geocoding import GeocoderInterface, NominatimGeocoder
from output import OutputManager
from renderer import RendererInterface, StandardRenderer
from theme import ThemeManager
from typography import TypographyManager


class PosterGenerator:
    """Main application orchestrator."""

    def __init__(
        self,
        config: Config,
        geocoder: GeocoderInterface,
        data_fetcher: DataFetcherInterface,
        theme_manager: ThemeManager,
        renderer: RendererInterface,
        output_manager: OutputManager,
    ) -> None:
        """Initialize poster generator with dependencies.

        Args:
            config: System configuration
            geocoder: Geocoding service
            data_fetcher: Data fetching service
            theme_manager: Theme manager
            renderer: Map renderer
            output_manager: Output file manager
        """
        self.config = config
        self.geocoder = geocoder
        self.data_fetcher = data_fetcher
        self.theme_manager = theme_manager
        self.renderer = renderer
        self.output_manager = output_manager

    def generate_poster(
        self,
        city: str,
        country: str,
        theme_name: str,
        distance: int,
        output_format: str,
        country_label: Optional[str] = None,
    ) -> Path:
        """Generate a single map poster.

        Args:
            city: City name
            country: Country name
            theme_name: Theme to use
            distance: Map radius in meters
            output_format: Output format (png, svg, pdf)
            country_label: Optional country label override

        Returns:
            Path to generated poster

        Raises:
            ValueError: If geocoding fails
            RuntimeError: If data fetching fails
        """
        print(f"\nGenerating map for {city}, {country}...")

        # Get coordinates
        coords = self.geocoder.geocode(city, country)

        # Fetch data with progress bar
        with tqdm(
            total=3, desc="Fetching map data", unit="step", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}"
        ) as pbar:
            pbar.set_description("Downloading street network")
            graph = self.data_fetcher.fetch_graph(coords, distance)
            if graph is None:
                raise RuntimeError("Failed to retrieve street network data")
            pbar.update(1)

            pbar.set_description("Downloading water features")
            water = self.data_fetcher.fetch_features(
                coords, distance, {"natural": "water", "waterway": "riverbank"}, "water"
            )
            pbar.update(1)

            pbar.set_description("Downloading parks/green spaces")
            parks = self.data_fetcher.fetch_features(coords, distance, {"leisure": "park", "landuse": "grass"}, "parks")
            pbar.update(1)

        print("✓ All data retrieved successfully!")

        # Load theme
        theme = self.theme_manager.load_theme(theme_name)

        # Generate output path
        output_path = self.output_manager.generate_filename(city, theme_name, output_format)

        # Render poster
        self.renderer.render(
            graph, water, parks, city, country, coords, theme, output_path, output_format, country_label
        )

        return output_path

    def generate_all_themes(
        self, city: str, country: str, distance: int, output_format: str, country_label: Optional[str] = None
    ) -> list[Path]:
        """Generate posters for all available themes.

        Args:
            city: City name
            country: Country name
            distance: Map radius in meters
            output_format: Output format (png, svg, pdf)
            country_label: Optional country label override

        Returns:
            List of paths to generated posters
        """
        themes = self.theme_manager.list_themes()
        output_paths = []

        for theme_name in themes:
            output_path = self.generate_poster(city, country, theme_name, distance, output_format, country_label)
            output_paths.append(output_path)

        return output_paths


def create_app() -> PosterGenerator:
    """Factory function to create configured application.

    Returns:
        Configured PosterGenerator instance
    """
    config = load_config()

    # Create cache manager
    cache = CacheManager(config.cache_dir)

    # Create geocoder
    geocoder = NominatimGeocoder(
        cache=cache,
        user_agent=config.geocoding_user_agent,
        timeout=config.geocoding_timeout,
        rate_limit=config.geocoding_rate_limit,
    )

    # Create data fetcher
    data_fetcher = OSMDataFetcher(
        cache=cache, graph_rate_limit=config.graph_rate_limit, features_rate_limit=config.features_rate_limit
    )

    # Create theme manager
    theme_manager = ThemeManager(config.themes_dir)

    # Create typography manager
    typography = TypographyManager(config.fonts_dir)

    # Create renderer
    renderer = StandardRenderer(typography=typography, figure_size=config.default_figure_size, dpi=config.default_dpi)

    # Create output manager
    output_manager = OutputManager(config.output_dir)

    # Create and return app
    return PosterGenerator(
        config=config,
        geocoder=geocoder,
        data_fetcher=data_fetcher,
        theme_manager=theme_manager,
        renderer=renderer,
        output_manager=output_manager,
    )


def print_examples() -> None:
    """Print usage examples."""
    print("""
City Map Poster Generator
=========================

Usage:
  python maptoposter/create_map_poster.py --city <city> --country <country> [options]
  # or
  python -m create_map_poster --city <city> --country <country> [options]

Examples:
  # Iconic grid patterns
  python maptoposter/create_map_poster.py -c "New York" -C "USA" -t noir -d 12000
  python maptoposter/create_map_poster.py -c "Barcelona" -C "Spain" -t warm_beige -d 8000

  # Waterfront & canals
  python maptoposter/create_map_poster.py -c "Venice" -C "Italy" -t blueprint -d 4000
  python maptoposter/create_map_poster.py -c "Amsterdam" -C "Netherlands" -t ocean -d 6000

  # Radial patterns
  python maptoposter/create_map_poster.py -c "Paris" -C "France" -t pastel_dream -d 10000
  python maptoposter/create_map_poster.py -c "Moscow" -C "Russia" -t noir -d 12000

  # Organic old cities
  python maptoposter/create_map_poster.py -c "Tokyo" -C "Japan" -t japanese_ink -d 15000
  python maptoposter/create_map_poster.py -c "Marrakech" -C "Morocco" -t terracotta -d 5000
  python maptoposter/create_map_poster.py -c "Rome" -C "Italy" -t warm_beige -d 8000

  # Coastal cities
  python maptoposter/create_map_poster.py -c "San Francisco" -C "USA" -t sunset -d 10000
  python maptoposter/create_map_poster.py -c "Sydney" -C "Australia" -t ocean -d 12000
  python maptoposter/create_map_poster.py -c "Mumbai" -C "India" -t contrast_zones -d 18000

  # River cities
  python maptoposter/create_map_poster.py -c "London" -C "UK" -t noir -d 15000
  python maptoposter/create_map_poster.py -c "Budapest" -C "Hungary" -t copper_patina -d 8000

  # List themes
  python maptoposter/create_map_poster.py --list-themes

Options:
  --city, -c        City name (required)
  --country, -C     Country name (required)
  --country-label   Override country text displayed on poster
  --theme, -t       Theme name (default: feature_based)
  --all-themes      Generate posters for all themes
  --distance, -d    Map radius in meters (default: 29000)
  --format, -f      Output format: png, svg, pdf (default: png)
  --list-themes     List all available themes

Distance guide:
  4000-6000m   Small/dense cities (Venice, Amsterdam old center)
  8000-12000m  Medium cities, focused downtown (Paris, Barcelona)
  15000-20000m Large metros, full city view (Tokyo, Mumbai)

Available themes can be found in the 'themes/' directory.
Generated posters are saved to 'posters/' directory.
""")


def list_themes(theme_manager: ThemeManager) -> None:
    """List all available themes.

    Args:
        theme_manager: Theme manager instance
    """
    themes = theme_manager.list_themes()
    if not themes:
        print("No themes found in themes directory.")
        return

    print("\nAvailable Themes:")
    print("-" * 60)
    for theme_name in themes:
        info = theme_manager.get_theme_info(theme_name)
        print(f"  {theme_name}")
        print(f"    {info['name']}")
        if info["description"]:
            print(f"    {info['description']}")
        print()


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate beautiful map posters for any city", formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("--city", "-c", type=str, help="City name")
    parser.add_argument("--country", "-C", type=str, help="Country name")
    parser.add_argument(
        "--country-label", dest="country_label", type=str, help="Override country text displayed on poster"
    )
    parser.add_argument("--theme", "-t", type=str, default="feature_based", help="Theme name (default: feature_based)")
    parser.add_argument("--all-themes", dest="all_themes", action="store_true", help="Generate posters for all themes")
    parser.add_argument("--distance", "-d", type=int, default=12000, help="Map radius in meters (default: 29000)")
    parser.add_argument(
        "--format", "-f", default="png", choices=["png", "svg", "pdf"], help="Output format (default: png)"
    )
    parser.add_argument("--list-themes", action="store_true", help="List all available themes")

    args = parser.parse_args()

    # Show examples if no arguments
    if len(sys.argv) == 1:
        print_examples()
        sys.exit(0)

    # Create app
    try:
        app = create_app()
    except Exception as e:
        print(f"✗ Error initializing application: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

    # List themes if requested
    if args.list_themes:
        list_themes(app.theme_manager)
        sys.exit(0)

    # Validate required arguments
    if not args.city or not args.country:
        print("Error: --city and --country are required.\n")
        print_examples()
        sys.exit(1)

    # Validate theme
    available_themes = app.theme_manager.list_themes()
    if not available_themes:
        print("Error: No themes found in themes directory.")
        sys.exit(1)

    if not args.all_themes and args.theme not in available_themes:
        print(f"Error: Theme '{args.theme}' not found.")
        print(f"Available themes: {', '.join(available_themes)}")
        sys.exit(1)

    # Generate posters
    print("=" * 50)
    print("City Map Poster Generator")
    print("=" * 50)

    try:
        if args.all_themes:
            app.generate_all_themes(args.city, args.country, args.distance, args.format, args.country_label)
        else:
            app.generate_poster(args.city, args.country, args.theme, args.distance, args.format, args.country_label)

        print("\n" + "=" * 50)
        print("✓ Poster generation complete!")
        print("=" * 50)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
