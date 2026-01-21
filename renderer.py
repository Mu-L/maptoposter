"""Map rendering functionality.

This module provides the rendering engine for creating map posters with
proper styling, typography, and layout.
"""

from abc import ABC, abstractmethod
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import osmnx as ox
from geopandas import GeoDataFrame
from matplotlib.figure import Figure
from networkx import MultiDiGraph

from theme import Theme
from typography import TypographyManager


class RendererInterface(ABC):
    """Abstract interface for map rendering."""

    @abstractmethod
    def render(
        self,
        graph: MultiDiGraph,
        water: GeoDataFrame | None,
        parks: GeoDataFrame | None,
        city: str,
        country: str,
        point: tuple[float, float],
        theme: Theme,
        output_path: Path,
        output_format: str,
        country_label: str | None = None,
    ) -> None:
        """Render map poster to file.

        Args:
            graph: Street network graph
            water: Water features GeoDataFrame
            parks: Parks features GeoDataFrame
            city: City name
            country: Country name
            point: Coordinates (latitude, longitude)
            theme: Theme configuration
            output_path: Path for output file
            output_format: Output format (png, svg, pdf)
            country_label: Optional country label override
        """
        pass


class StandardRenderer(RendererInterface):
    """Standard map poster renderer."""

    def __init__(self, typography: TypographyManager, figure_size: tuple[float, float] = (12.0, 16.0), dpi: int = 300):
        """Initialize renderer.

        Args:
            typography: Typography manager for fonts
            figure_size: Figure dimensions in inches
            dpi: Resolution for raster outputs
        """
        self.typography = typography
        self.figure_size = figure_size
        self.dpi = dpi

    def _get_edge_colors(self, G: MultiDiGraph, theme: Theme) -> list[str]:
        """Assign colors to edges based on road type.

        Args:
            G: Street network graph
            theme: Theme configuration

        Returns:
            List of color strings for each edge
        """
        edge_colors = []

        for u, v, data in G.edges(data=True):
            highway = data.get("highway", "unclassified")

            # Handle list of highway types
            if isinstance(highway, list):
                highway = highway[0] if highway else "unclassified"

            # Map highway type to color
            if highway in ["motorway", "motorway_link"]:
                color = theme.road_motorway
            elif highway in ["trunk", "trunk_link", "primary", "primary_link"]:
                color = theme.road_primary
            elif highway in ["secondary", "secondary_link"]:
                color = theme.road_secondary
            elif highway in ["tertiary", "tertiary_link"]:
                color = theme.road_tertiary
            elif highway in ["residential", "living_street", "unclassified"]:
                color = theme.road_residential
            else:
                color = theme.road_default

            edge_colors.append(color)

        return edge_colors

    def _get_edge_widths(self, G: MultiDiGraph) -> list[float]:
        """Assign line widths to edges based on road type.

        Args:
            G: Street network graph

        Returns:
            List of line widths for each edge
        """
        edge_widths = []

        for u, v, data in G.edges(data=True):
            highway = data.get("highway", "unclassified")

            if isinstance(highway, list):
                highway = highway[0] if highway else "unclassified"

            # Map highway type to width
            if highway in ["motorway", "motorway_link"]:
                width = 1.2
            elif highway in ["trunk", "trunk_link", "primary", "primary_link"]:
                width = 1.0
            elif highway in ["secondary", "secondary_link"]:
                width = 0.8
            elif highway in ["tertiary", "tertiary_link"]:
                width = 0.6
            else:
                width = 0.4

            edge_widths.append(width)

        return edge_widths

    def _get_crop_limits(self, G: MultiDiGraph, fig: Figure) -> tuple[tuple[float, float], tuple[float, float]]:
        """Calculate crop limits to maintain aspect ratio.

        Args:
            G: Street network graph
            fig: Matplotlib figure

        Returns:
            Tuple of (xlim, ylim) tuples
        """
        # Get node extents
        xs = [data["x"] for _, data in G.nodes(data=True)]
        ys = [data["y"] for _, data in G.nodes(data=True)]
        minx, maxx = min(xs), max(xs)
        miny, maxy = min(ys), max(ys)
        x_range = maxx - minx
        y_range = maxy - miny

        # Calculate aspect ratios
        fig_width, fig_height = fig.get_size_inches()
        desired_aspect = fig_width / fig_height
        current_aspect = x_range / y_range

        center_x = (minx + maxx) / 2
        center_y = (miny + maxy) / 2

        # Adjust to match figure aspect ratio
        if current_aspect > desired_aspect:
            # Too wide, crop horizontally
            desired_x_range = y_range * desired_aspect
            crop_xlim = (center_x - desired_x_range / 2, center_x + desired_x_range / 2)
            crop_ylim = (miny, maxy)
        elif current_aspect < desired_aspect:
            # Too tall, crop vertically
            desired_y_range = x_range / desired_aspect
            crop_xlim = (minx, maxx)
            crop_ylim = (center_y - desired_y_range / 2, center_y + desired_y_range / 2)
        else:
            # Perfect aspect ratio
            crop_xlim = (minx, maxx)
            crop_ylim = (miny, maxy)

        return crop_xlim, crop_ylim

    def _create_gradient_fade(self, ax: plt.Axes, color: str, location: str = "bottom", zorder: int = 10) -> None:
        """Create gradient fade effect.

        Args:
            ax: Matplotlib axes
            color: Color for gradient
            location: 'bottom' or 'top'
            zorder: Z-order for layering
        """
        vals = np.linspace(0, 1, 256).reshape(-1, 1)
        gradient = np.hstack((vals, vals))

        rgb = mcolors.to_rgb(color)
        my_colors = np.zeros((256, 4))
        my_colors[:, 0] = rgb[0]
        my_colors[:, 1] = rgb[1]
        my_colors[:, 2] = rgb[2]

        if location == "bottom":
            my_colors[:, 3] = np.linspace(1, 0, 256)
            extent_y_start = 0.0
            extent_y_end = 0.25
        else:
            my_colors[:, 3] = np.linspace(0, 1, 256)
            extent_y_start = 0.75
            extent_y_end = 1.0

        custom_cmap = mcolors.ListedColormap(my_colors)

        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        y_range = ylim[1] - ylim[0]

        y_bottom = ylim[0] + y_range * extent_y_start
        y_top = ylim[0] + y_range * extent_y_end

        ax.imshow(
            gradient,
            extent=(xlim[0], xlim[1], y_bottom, y_top),
            aspect="auto",
            cmap=custom_cmap,
            zorder=zorder,
            origin="lower",
        )

    def _render_features(
        self, ax: plt.Axes, water: GeoDataFrame | None, parks: GeoDataFrame | None, G_proj: MultiDiGraph, theme: Theme
    ) -> None:
        """Render water and park features.

        Args:
            ax: Matplotlib axes
            water: Water features GeoDataFrame
            parks: Parks features GeoDataFrame
            G_proj: Projected street network graph
            theme: Theme configuration
        """
        # Render water
        if water is not None and not water.empty:
            water_polys = water[water.geometry.type.isin(["Polygon", "MultiPolygon"])]
            if not water_polys.empty:
                try:
                    water_polys = ox.projection.project_gdf(water_polys)
                except Exception:
                    water_polys = water_polys.to_crs(G_proj.graph["crs"])
                water_polys.plot(ax=ax, facecolor=theme.water, edgecolor="none", zorder=1)

        # Render parks
        if parks is not None and not parks.empty:
            parks_polys = parks[parks.geometry.type.isin(["Polygon", "MultiPolygon"])]
            if not parks_polys.empty:
                try:
                    parks_polys = ox.projection.project_gdf(parks_polys)
                except Exception:
                    parks_polys = parks_polys.to_crs(G_proj.graph["crs"])
                parks_polys.plot(ax=ax, facecolor=theme.parks, edgecolor="none", zorder=2)

    def _render_typography(
        self,
        ax: plt.Axes,
        city: str,
        country: str,
        point: tuple[float, float],
        theme: Theme,
        country_label: str | None = None,
    ) -> None:
        """Add text elements to map.

        Args:
            ax: Matplotlib axes
            city: City name
            country: Country name
            point: Coordinates (latitude, longitude)
            theme: Theme configuration
            country_label: Optional country label override
        """
        # City name
        spaced_city = self.typography.format_city_name(city)
        city_font = self.typography.get_city_font(city)
        ax.text(
            0.5,
            0.14,
            spaced_city,
            transform=ax.transAxes,
            color=theme.text,
            ha="center",
            fontproperties=city_font,
            zorder=11,
        )

        # Country name
        country_text = country_label if country_label else country
        country_font = self.typography.get_country_font()
        ax.text(
            0.5,
            0.10,
            country_text.upper(),
            transform=ax.transAxes,
            color=theme.text,
            ha="center",
            fontproperties=country_font,
            zorder=11,
        )

        # Coordinates
        coords_text = self.typography.format_coordinates(*point)
        coords_font = self.typography.get_coords_font()
        ax.text(
            0.5,
            0.07,
            coords_text,
            transform=ax.transAxes,
            color=theme.text,
            alpha=0.7,
            ha="center",
            fontproperties=coords_font,
            zorder=11,
        )

        # Separator line
        ax.plot([0.4, 0.6], [0.125, 0.125], transform=ax.transAxes, color=theme.text, linewidth=1, zorder=11)

        # Attribution
        attr_font = self.typography.get_attribution_font()
        ax.text(
            0.98,
            0.02,
            "© OpenStreetMap contributors",
            transform=ax.transAxes,
            color=theme.text,
            alpha=0.5,
            ha="right",
            va="bottom",
            fontproperties=attr_font,
            zorder=11,
        )

    def render(
        self,
        graph: MultiDiGraph,
        water: GeoDataFrame | None,
        parks: GeoDataFrame | None,
        city: str,
        country: str,
        point: tuple[float, float],
        theme: Theme,
        output_path: Path,
        output_format: str,
        country_label: str | None = None,
    ) -> None:
        """Render complete map poster.

        Args:
            graph: Street network graph
            water: Water features GeoDataFrame
            parks: Parks features GeoDataFrame
            city: City name
            country: Country name
            point: Coordinates (latitude, longitude)
            theme: Theme configuration
            output_path: Path for output file
            output_format: Output format (png, svg, pdf)
            country_label: Optional country label override
        """
        print("Rendering map...")

        # Setup figure
        fig, ax = plt.subplots(figsize=self.figure_size, facecolor=theme.bg)
        ax.set_facecolor(theme.bg)
        ax.set_position((0.0, 0.0, 1.0, 1.0))

        # Project graph
        G_proj = ox.project_graph(graph)

        # Render features (water, parks)
        self._render_features(ax, water, parks, G_proj, theme)

        # Render roads
        print("Applying road hierarchy colors...")
        edge_colors = self._get_edge_colors(G_proj, theme)
        edge_widths = self._get_edge_widths(G_proj)

        # Calculate crop limits
        crop_xlim, crop_ylim = self._get_crop_limits(G_proj, fig)

        # Plot graph
        ox.plot_graph(
            G_proj,
            ax=ax,
            bgcolor=theme.bg,
            node_size=0,
            edge_color=edge_colors,
            edge_linewidth=edge_widths,
            show=False,
            close=False,
        )
        ax.set_aspect("equal", adjustable="box")
        ax.set_xlim(crop_xlim)
        ax.set_ylim(crop_ylim)

        # Add gradients
        self._create_gradient_fade(ax, theme.gradient_color, "bottom", 10)
        self._create_gradient_fade(ax, theme.gradient_color, "top", 10)

        # Add typography
        self._render_typography(ax, city, country, point, theme, country_label)

        # Save
        print(f"Saving to {output_path}...")
        save_kwargs = {"facecolor": theme.bg, "bbox_inches": "tight", "pad_inches": 0.05}

        if output_format.lower() == "png":
            save_kwargs["dpi"] = self.dpi

        plt.savefig(output_path, format=output_format.lower(), **save_kwargs)
        plt.close()

        print(f"✓ Done! Poster saved as {output_path}")
