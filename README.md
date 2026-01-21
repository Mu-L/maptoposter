# City Map Poster Generator

Generate beautiful, minimalist map posters for any city in the world.

<img src="posters/singapore_neon_cyberpunk_20260118_153328.png" width="250">
<img src="posters/dubai_midnight_blue_20260118_140807.png" width="250">

## Examples


| Country      | City           | Theme           | Poster |
|:------------:|:--------------:|:---------------:|:------:|
| USA          | San Francisco  | sunset          | <img src="posters/san_francisco_sunset_20260118_144726.png" width="250"> |
| Spain        | Barcelona      | warm_beige      | <img src="posters/barcelona_warm_beige_20260118_140048.png" width="250"> |
| Italy        | Venice         | blueprint       | <img src="posters/venice_blueprint_20260118_140505.png" width="250"> |
| Japan        | Tokyo          | japanese_ink    | <img src="posters/tokyo_japanese_ink_20260118_142446.png" width="250"> |
| India        | Mumbai         | contrast_zones  | <img src="posters/mumbai_contrast_zones_20260118_145843.png" width="250"> |
| Morocco      | Marrakech      | terracotta      | <img src="posters/marrakech_terracotta_20260118_143253.png" width="250"> |
| Singapore    | Singapore      | neon_cyberpunk  | <img src="posters/singapore_neon_cyberpunk_20260118_153328.png" width="250"> |
| Australia    | Melbourne      | forest          | <img src="posters/melbourne_forest_20260118_153446.png" width="250"> |
| UAE          | Dubai          | midnight_blue   | <img src="posters/dubai_midnight_blue_20260118_140807.png" width="250"> |

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Command Line

```bash
# From the maptoposter directory
python create_map_poster.py --city <city> --country <country> [options]

# Or as a Python module
python -m maptoposter.create_map_poster --city <city> --country <country> [options]
```

### As a Python Module

```python
from maptoposter import create_app

# Create configured application
app = create_app()

# Generate a single poster
output_path = app.generate_poster(
    city="Paris",
    country="France",
    theme_name="noir",
    distance=10000,
    output_format="png"
)

# Generate posters for all themes
output_paths = app.generate_all_themes(
    city="Tokyo",
    country="Japan",
    distance=15000,
    output_format="png"
)
```

### Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--city` | `-c` | City name | required |
| `--country` | `-C` | Country name | required |
| **OPTIONAL:** `--latitude` | | Latitude (overrides geocoded latitude) | |
| **OPTIONAL:** `--longitude` | | Longitude (overrides geocoded longitude) | |
| **OPTIONAL:** `--name` | | Override display name (city display on poster) | |
| **OPTIONAL:** `--country-label` | | Override display country (country display on poster) | |
| **OPTIONAL:** `--theme` | `-t` | Theme name | feature_based |
| **OPTIONAL:** `--distance` | `-d` | Map radius in meters | 29000 |
| **OPTIONAL:** `--list-themes` | | List all available themes | |
| **OPTIONAL:** `--all-themes` | | Generate posters for all available themes | |

### Examples

```bash
# Iconic grid patterns
python create_map_poster.py -c "New York" -C "USA" -t noir -d 12000           # Manhattan grid
python create_map_poster.py -c "Barcelona" -C "Spain" -t warm_beige -d 8000   # Eixample district

# Waterfront & canals
python create_map_poster.py -c "Venice" -C "Italy" -t blueprint -d 4000       # Canal network
python create_map_poster.py -c "Amsterdam" -C "Netherlands" -t ocean -d 6000  # Concentric canals
python create_map_poster.py -c "Dubai" -C "UAE" -t midnight_blue -d 15000     # Palm & coastline

# Radial patterns
python create_map_poster.py -c "Paris" -C "France" -t pastel_dream -d 10000   # Haussmann boulevards
python create_map_poster.py -c "Moscow" -C "Russia" -t noir -d 12000          # Ring roads

# Organic old cities
python create_map_poster.py -c "Tokyo" -C "Japan" -t japanese_ink -d 15000    # Dense organic streets
python create_map_poster.py -c "Marrakech" -C "Morocco" -t terracotta -d 5000 # Medina maze
python create_map_poster.py -c "Rome" -C "Italy" -t warm_beige -d 8000        # Ancient layout

# Coastal cities
python create_map_poster.py -c "San Francisco" -C "USA" -t sunset -d 10000    # Peninsula grid
python create_map_poster.py -c "Sydney" -C "Australia" -t ocean -d 12000      # Harbor city
python create_map_poster.py -c "Mumbai" -C "India" -t contrast_zones -d 18000 # Coastal peninsula

# River cities
python create_map_poster.py -c "London" -C "UK" -t noir -d 15000              # Thames curves
python create_map_poster.py -c "Budapest" -C "Hungary" -t copper_patina -d 8000  # Danube split

# List available themes
python create_map_poster.py --list-themes

# Use explicit coordinates instead of geocoding
python create_map_poster.py --latitude 48.8566 --longitude 2.3522 --name "Paris Center" -t sunset -d 10000


# Generate posters for every theme
python create_map_poster.py -c "Tokyo" -C "Japan" --all-themes
```

### Distance Guide

| Distance | Best for |
|----------|----------|
| 4000-6000m | Small/dense cities (Venice, Amsterdam center) |
| 8000-12000m | Medium cities, focused downtown (Paris, Barcelona) |
| 15000-20000m | Large metros, full city view (Tokyo, Mumbai) |

## Themes

17 themes available in `themes/` directory:

| Theme | Style |
|-------|-------|
| `feature_based` | Classic black & white with road hierarchy |
| `gradient_roads` | Smooth gradient shading |
| `contrast_zones` | High contrast urban density |
| `noir` | Pure black background, white roads |
| `midnight_blue` | Navy background with gold roads |
| `blueprint` | Architectural blueprint aesthetic |
| `neon_cyberpunk` | Dark with electric pink/cyan |
| `warm_beige` | Vintage sepia tones |
| `pastel_dream` | Soft muted pastels |
| `japanese_ink` | Minimalist ink wash style |
| `forest` | Deep greens and sage |
| `ocean` | Blues and teals for coastal cities |
| `terracotta` | Mediterranean warmth |
| `sunset` | Warm oranges and pinks |
| `autumn` | Seasonal burnt oranges and reds |
| `copper_patina` | Oxidized copper aesthetic |
| `monochrome_blue` | Single blue color family |

## Output

Posters are saved to `posters/` directory with format:
```
{city}_{theme}_{YYYYMMDD_HHMMSS}.png
```

## Adding Custom Themes

Create a JSON file in `themes/` directory:

```json
{
  "name": "My Theme",
  "description": "Description of the theme",
  "bg": "#FFFFFF",
  "text": "#000000",
  "gradient_color": "#FFFFFF",
  "water": "#C0C0C0",
  "parks": "#F0F0F0",
  "road_motorway": "#0A0A0A",
  "road_primary": "#1A1A1A",
  "road_secondary": "#2A2A2A",
  "road_tertiary": "#3A3A3A",
  "road_residential": "#4A4A4A",
  "road_default": "#3A3A3A"
}
```

## Project Structure

```
maptoposter/
├── __init__.py                   # Package initialization & public API
├── create_map_poster.py          # Main CLI entry point
├── cache.py                      # Caching system
├── config.py                     # Configuration management
├── geocoding.py                  # Location geocoding
├── data_fetching.py              # OSM data retrieval
├── theme.py                      # Theme management
├── typography.py                 # Font & text handling
├── renderer.py                   # Map rendering engine
├── output.py                     # Output file management
├── themes/                       # Theme JSON files
├── fonts/                        # Roboto font files
├── posters/                      # Generated posters
├── .cache/                       # Cached data (auto-created)
├── test_*.py                     # Unit tests
├── test_integration.py           # Integration tests
├── test_backward_compatibility.py # Compatibility tests
└── README.md
```

## Hacker's Guide

Quick reference for contributors who want to extend or modify the system.

### Architecture Overview (v2.0 - Refactored)

```
┌─────────────────────┐
│  PosterGenerator    │  Main orchestrator with dependency injection
│  (create_app())     │
└──────────┬──────────┘
           │
           ├──▶ CacheManager ──────────┐
           │                           │
           ├──▶ NominatimGeocoder ─────┤ Uses cache
           │                           │
           ├──▶ OSMDataFetcher ────────┘
           │
           ├──▶ ThemeManager
           │
           ├──▶ TypographyManager
           │
           ├──▶ StandardRenderer
           │
           └──▶ OutputManager
```

### Modular Design

The refactored system uses **dependency injection** and **separation of concerns**:

| Module | Responsibility | Key Classes |
|--------|----------------|-------------|
| `cache.py` | Data persistence | `CacheManager`, `CacheError` |
| `config.py` | Configuration | `Config`, `load_config()` |
| `geocoding.py` | Location lookup | `GeocoderInterface`, `NominatimGeocoder` |
| `data_fetching.py` | OSM data retrieval | `DataFetcherInterface`, `OSMDataFetcher`, `AsyncOSMDataFetcher` |
| `theme.py` | Visual styling | `Theme`, `ThemeManager` |
| `typography.py` | Font management | `FontSet`, `TypographyManager` |
| `renderer.py` | Map visualization | `RendererInterface`, `StandardRenderer` |
| `output.py` | File management | `OutputManager` |
| `create_map_poster.py` | CLI & orchestration | `PosterGenerator`, `create_app()` |

### Key Classes & Methods

| Class/Method | Purpose | Modify when... |
|--------------|---------|----------------|
| `PosterGenerator.generate_poster()` | Main orchestration | Changing workflow |
| `NominatimGeocoder.geocode()` | City → lat/lon via Nominatim | Switching geocoding provider |
| `OSMDataFetcher.fetch_graph()` | Download street network | Changing data source |
| `StandardRenderer.render()` | Main rendering pipeline | Adding new map layers |
| `StandardRenderer._get_edge_colors()` | Road color by OSM highway tag | Changing road styling |
| `StandardRenderer._get_edge_widths()` | Road width by importance | Adjusting line weights |
| `StandardRenderer._create_gradient_fade()` | Top/bottom fade effect | Modifying gradient overlay |
| `ThemeManager.load_theme()` | JSON theme → Theme object | Adding new theme properties |
| `TypographyManager.get_city_font()` | Dynamic font sizing | Changing text styling |

### Rendering Layers (z-order)

```
z=11  Text labels (city, country, coords)
z=10  Gradient fades (top & bottom)
z=3   Roads (via ox.plot_graph)
z=2   Parks (green polygons)
z=1   Water (blue polygons)
z=0   Background color
```

### OSM Highway Types → Road Hierarchy

```python
# In StandardRenderer._get_edge_colors() and _get_edge_widths()
motorway, motorway_link     → Thickest (1.2), darkest
trunk, primary              → Thick (1.0)
secondary                   → Medium (0.8)
tertiary                    → Thin (0.6)
residential, living_street  → Thinnest (0.4), lightest
```

### Extending the System

**Add a new geocoding provider:**
```python
# In geocoding.py
class MyGeocoder(GeocoderInterface):
    def geocode(self, city: str, country: str) -> tuple[float, float]:
        # Your implementation
        pass

# In create_map_poster.py create_app()
geocoder = MyGeocoder(cache=cache, ...)
```

**Add a custom renderer:**
```python
# In renderer.py
class MinimalistRenderer(RendererInterface):
    def render(self, graph, water, parks, city, country, point, theme, output_path, output_format, country_label=None):
        # Your custom rendering logic
        pass

# In create_map_poster.py create_app()
renderer = MinimalistRenderer(typography=typography, ...)
```

### Adding New Features

**New map layer (e.g., railways):**
```python
# In StandardRenderer.render(), after fetching parks:
# Add to PosterGenerator.generate_poster():
railways = self.data_fetcher.fetch_features(
    coords,
    distance,
    {'railway': 'rail'},
    'railways'
)

# Then in StandardRenderer._render_features():
if railways is not None and not railways.empty:
    railways_polys = railways[railways.geometry.type.isin(['Polygon', 'MultiPolygon'])]
    if not railways_polys.empty:
        railways_polys = ox.projection.project_gdf(railways_polys)
        railways_polys.plot(ax=ax, facecolor=theme.railway, edgecolor='none', zorder=2.5)
```

**New theme property:**
1. Add to `Theme` dataclass in `theme.py`: `railway: str = "#FF0000"`
2. Add to theme JSON files: `"railway": "#FF0000"`
3. Use in renderer: `theme.railway`

### Typography Positioning

All text uses `transform=ax.transAxes` (0-1 normalized coordinates):
```
y=0.14  City name (spaced letters)
y=0.125 Decorative line
y=0.10  Country name
y=0.07  Coordinates
y=0.02  Attribution (bottom-right)
```

### Useful OSMnx Patterns

```python
# Get all buildings
buildings = ox.features_from_point(point, tags={'building': True}, dist=dist)

# Get specific amenities
cafes = ox.features_from_point(point, tags={'amenity': 'cafe'}, dist=dist)

# Different network types
G = ox.graph_from_point(point, dist=dist, network_type='drive')  # roads only
G = ox.graph_from_point(point, dist=dist, network_type='bike')   # bike paths
G = ox.graph_from_point(point, dist=dist, network_type='walk')   # pedestrian
```

### Performance Tips

- Large `dist` values (>20km) = slow downloads + memory heavy
- **Caching is automatic** - coordinates and OSM data are cached in `.cache/` directory
- Use `network_type='drive'` instead of `'all'` for faster renders (modify in `OSMDataFetcher`)
- Reduce `dpi` from 300 to 150 for quick previews (pass to `StandardRenderer`)
- Clear cache with: `rm -rf maptoposter/.cache/`

### Testing

Run the comprehensive test suite:
```bash
# All tests (144 tests)
pytest

# With coverage report
pytest --cov=maptoposter --cov-report=html

# Specific test files
pytest test_cache.py
pytest test_integration.py
pytest test_backward_compatibility.py

# Type checking
mypy maptoposter/

# Linting
flake8 maptoposter/ --max-line-length=120

# Code formatting
black maptoposter/ --line-length=120
```

### Version History

- **v2.0.0** (2025) - Complete refactoring with modular architecture, dependency injection, 96% test coverage
- **v1.0.0** (2024) - Original monolithic implementation