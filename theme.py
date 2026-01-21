"""Theme management for map poster styling.

This module provides theme configuration and management functionality,
including loading themes from JSON files and providing fallback defaults.
"""

import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class Theme:
    """Theme configuration for map styling."""

    name: str
    description: str = ""

    # Colors
    bg: str = "#FFFFFF"
    text: str = "#000000"
    gradient_color: str = "#FFFFFF"
    water: str = "#C0C0C0"
    parks: str = "#F0F0F0"

    # Road hierarchy colors
    road_motorway: str = "#0A0A0A"
    road_primary: str = "#1A1A1A"
    road_secondary: str = "#2A2A2A"
    road_tertiary: str = "#3A3A3A"
    road_residential: str = "#4A4A4A"
    road_default: str = "#3A3A3A"

    @classmethod
    def from_json(cls, path: Path) -> "Theme":
        """Load theme from JSON file.

        Args:
            path: Path to JSON theme file

        Returns:
            Theme object

        Raises:
            FileNotFoundError: If theme file doesn't exist
            json.JSONDecodeError: If JSON is invalid
            TypeError: If JSON contains invalid data types
        """
        with open(path, "r") as f:
            data = json.load(f)
        return cls(**data)

    def to_json(self, path: Path) -> None:
        """Save theme to JSON file.

        Args:
            path: Path where JSON file should be saved

        Raises:
            IOError: If file cannot be written
        """
        with open(path, "w") as f:
            json.dump(asdict(self), f, indent=2)

    def validate(self) -> None:
        """Validate theme colors are valid hex codes.

        Raises:
            ValueError: If any color is not a valid hex code
        """
        color_fields = [
            "bg",
            "text",
            "gradient_color",
            "water",
            "parks",
            "road_motorway",
            "road_primary",
            "road_secondary",
            "road_tertiary",
            "road_residential",
            "road_default",
        ]
        for field in color_fields:
            color = getattr(self, field)
            if not re.match(r"^#[0-9A-Fa-f]{6}$", color):
                raise ValueError(f"Invalid color '{color}' for field '{field}'")


class ThemeManager:
    """Manages loading and listing themes."""

    def __init__(self, themes_dir: Path):
        """Initialize theme manager.

        Args:
            themes_dir: Directory containing theme JSON files
        """
        self.themes_dir = themes_dir
        self.themes_dir.mkdir(parents=True, exist_ok=True)

    def list_themes(self) -> list[str]:
        """List all available theme names.

        Returns:
            List of theme names (without .json extension)
        """
        themes = []
        for file in sorted(self.themes_dir.glob("*.json")):
            themes.append(file.stem)
        return themes

    def load_theme(self, name: str) -> Theme:
        """Load theme by name.

        Args:
            name: Theme name (without .json extension)

        Returns:
            Theme object (default theme if loading fails)
        """
        theme_path = self.themes_dir / f"{name}.json"

        if not theme_path.exists():
            print(f"⚠ Theme '{name}' not found, using default")
            return self._default_theme()

        try:
            theme = Theme.from_json(theme_path)
            theme.validate()
            print(f"✓ Loaded theme: {theme.name}")
            if theme.description:
                print(f"  {theme.description}")
            return theme
        except Exception as e:
            print(f"⚠ Error loading theme '{name}': {e}")
            print("  Using default theme")
            return self._default_theme()

    def _default_theme(self) -> Theme:
        """Return default feature-based theme.

        Returns:
            Default Theme object
        """
        return Theme(name="Feature-Based Shading", description="Default theme with road hierarchy coloring")

    def get_theme_info(self, name: str) -> dict[str, str]:
        """Get theme metadata without loading full theme.

        Args:
            name: Theme name (without .json extension)

        Returns:
            Dictionary with 'name' and 'description' keys
        """
        theme_path = self.themes_dir / f"{name}.json"
        try:
            with open(theme_path, "r") as f:
                data = json.load(f)
            return {"name": data.get("name", name), "description": data.get("description", "")}
        except Exception:
            return {"name": name, "description": ""}
