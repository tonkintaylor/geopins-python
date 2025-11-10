# geopins
<a href="https://github.com/tonkintaylor/geopins/"><img src="https://raw.githubusercontent.com/tonkintaylor/geopins/refs/heads/develop/docs/logo.svg" align="right" height="138" /></a>

[![PyPI Version](https://img.shields.io/pypi/v/geopins.svg)](<https://pypi.python.org/pypi/geopins>)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![usethis](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/usethis-python/usethis-python/main/assets/badge/v1.json)](https://github.com/usethis-python/usethis-python)

The geopins package provides geospatial support for the [Python pins package](https://github.com/rstudio/pins-python). The package publishes data, models, and other Python objects, making it easy to share them across projects and with your colleagues. With `geopins`, there is support for geospatial datatypes (e.g. `geopandas.GeoDatFrame`, and `rastr.Raster`) and filetypes (e.g. `GeoPackage`, and `GeoTIFF`), fully compatible with your existing pins boards.

## Installation

```bash
# With uv
uv add geopins

# With pip
pip install geopins
```

## Quick Start

```python
from pins import board_local

# Patch pins to support geospatial data
import geopins
geopins.patch()

# Define any pins board as usual
b = board_local()

# Save a GeoDataFrame
import geopandas as gpd
gdf = b.pin_write(
    gpd.GeoDataFrame({"x": [1, 2, 3]}, geometry=gpd.points_from_xy([1, 2, 3], [4, 5, 6])),
    "gdf_example",
)

# Read it back
gdf = b.pin_read("gdf_example")

# Save a raster
from rastr.raster import Raster
b.pin_write(Raster.example(), "raster_example")

# Read it back
raster = b.pin_read("raster_example")
```

## Contributing

See the
[CONTRIBUTING.md](https://github.com/usethis-python/usethis-python/blob/main/CONTRIBUTING.md)
file.
