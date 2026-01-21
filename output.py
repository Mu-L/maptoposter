"""Output file management for map posters.

This module handles output file naming, path generation, and directory management.
"""

from datetime import datetime
from pathlib import Path


class OutputManager:
    """Manages output file paths and naming."""

    def __init__(self, output_dir: Path):
        """Initialize output manager.

        Args:
            output_dir: Directory for saving posters
        """
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_filename(self, city: str, theme_name: str, output_format: str) -> Path:
        """Generate unique output filename.

        Args:
            city: City name
            theme_name: Theme name
            output_format: File format (png, svg, pdf)

        Returns:
            Full path for output file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        city_slug = city.lower().replace(" ", "_")
        ext = output_format.lower()
        filename = f"{city_slug}_{theme_name}_{timestamp}.{ext}"
        return self.output_dir / filename
