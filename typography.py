"""Typography and font management for map posters.

This module handles font loading, text formatting, and dynamic font sizing
for different text elements on the map poster.
"""

from dataclasses import dataclass
from pathlib import Path
from matplotlib.font_manager import FontProperties


@dataclass
class FontSet:
    """Collection of font properties for different weights."""

    bold: FontProperties
    regular: FontProperties
    light: FontProperties

    @classmethod
    def from_files(cls, fonts_dir: Path) -> "FontSet | None":
        """Load Roboto fonts from directory.

        Args:
            fonts_dir: Directory containing font files

        Returns:
            FontSet or None if fonts not found
        """
        font_paths = {
            "bold": fonts_dir / "Roboto-Bold.ttf",
            "regular": fonts_dir / "Roboto-Regular.ttf",
            "light": fonts_dir / "Roboto-Light.ttf",
        }

        # Verify all fonts exist
        for weight, path in font_paths.items():
            if not path.exists():
                print(f"⚠ Font not found: {path}")
                return None

        return cls(
            bold=FontProperties(fname=str(font_paths["bold"])),
            regular=FontProperties(fname=str(font_paths["regular"])),
            light=FontProperties(fname=str(font_paths["light"])),
        )

    @classmethod
    def fallback(cls) -> "FontSet":
        """Create fallback font set using system fonts.

        Returns:
            FontSet using system monospace fonts
        """
        return cls(
            bold=FontProperties(family="monospace", weight="bold"),
            regular=FontProperties(family="monospace", weight="normal"),
            light=FontProperties(family="monospace", weight="light"),
        )


class TypographyManager:
    """Manages font loading and text styling."""

    fonts: FontSet

    def __init__(self, fonts_dir: Path):
        """Initialize typography manager.

        Args:
            fonts_dir: Directory containing font files
        """
        fonts = FontSet.from_files(fonts_dir)
        if fonts is None:
            print("⚠ Using fallback system fonts")
            self.fonts = FontSet.fallback()
        else:
            self.fonts = fonts

    def get_city_font(self, city_name: str, base_size: float = 60.0) -> FontProperties:
        """Get font for city name with dynamic sizing.

        Args:
            city_name: Name of city
            base_size: Base font size in points

        Returns:
            FontProperties with adjusted size
        """
        # Scale down for long city names
        char_count = len(city_name)
        if char_count > 10:
            scale_factor = 10 / char_count
            adjusted_size = max(base_size * scale_factor, 24)
        else:
            adjusted_size = base_size

        # Create new FontProperties with adjusted size
        if hasattr(self.fonts.bold, "get_file"):
            fname = self.fonts.bold.get_file()
            return FontProperties(fname=str(fname), size=adjusted_size)
        else:
            return FontProperties(family="monospace", weight="bold", size=adjusted_size)

    def get_country_font(self, size: float = 22.0) -> FontProperties:
        """Get font for country name.

        Args:
            size: Font size in points

        Returns:
            FontProperties for country text
        """
        if hasattr(self.fonts.light, "get_file"):
            fname = self.fonts.light.get_file()
            return FontProperties(fname=str(fname), size=size)
        else:
            return FontProperties(family="monospace", weight="light", size=size)

    def get_coords_font(self, size: float = 14.0) -> FontProperties:
        """Get font for coordinates.

        Args:
            size: Font size in points

        Returns:
            FontProperties for coordinates text
        """
        if hasattr(self.fonts.regular, "get_file"):
            fname = self.fonts.regular.get_file()
            return FontProperties(fname=str(fname), size=size)
        else:
            return FontProperties(family="monospace", weight="normal", size=size)

    def get_attribution_font(self, size: float = 8.0) -> FontProperties:
        """Get font for attribution text.

        Args:
            size: Font size in points

        Returns:
            FontProperties for attribution text
        """
        if hasattr(self.fonts.light, "get_file"):
            fname = self.fonts.light.get_file()
            return FontProperties(fname=str(fname), size=size)
        else:
            return FontProperties(family="monospace", weight="light", size=size)

    @staticmethod
    def format_city_name(city: str) -> str:
        """Format city name with letter spacing.

        Args:
            city: City name

        Returns:
            Formatted city name with spaces between letters
        """
        return "  ".join(list(city.upper()))

    @staticmethod
    def format_coordinates(lat: float, lon: float) -> str:
        """Format coordinates as string.

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            Formatted coordinate string (e.g., "40.7128° N / 74.0060° W")
        """
        lat_dir = "N" if lat >= 0 else "S"
        lon_dir = "E" if lon >= 0 else "W"
        return f"{abs(lat):.4f}° {lat_dir} / {abs(lon):.4f}° {lon_dir}"
