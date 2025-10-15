from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Literal

import geopandas as gpd

if TYPE_CHECKING:
    from pins.meta import Meta


@dataclass
class DriverInfo:
    """Information about a geopins driver.

    Attributes:
        dtype: The geopins datatype, e.g. "gdf" or "raster". None if not a geopins type,
               e.g. a standard dataframe pin.
        filetype: The underlying filetype, e.g. "gpkg", "parquet", or "tif".
    """

    dtype: Literal["gdf", "raster"] | None
    filetype: str


def infer_driver_info(meta: Meta) -> DriverInfo:
    """Infer the Python datatype and underlying filetype from the pin metadata.

    Args:
        meta: The pin metadata.

    Returns:
        The geopin type, or `None` if the type is not a geopin-specific type, e.g.
        a standard json/csv/etc pin.
    """

    file = meta.file

    if not isinstance(file, str):
        return DriverInfo(dtype=None, filetype=meta.type)

    ext = Path(file).suffix

    if ext == ".tif":
        return DriverInfo(dtype="raster", filetype="tif")
    elif ext == ".gpkg":
        return DriverInfo(dtype="gdf", filetype="gpkg")
    elif ext == "parquet":
        # Need to check if it's a geoparquet - pandas also uses .parquet
        try:
            gpd.read_parquet(file, columns=[])
        except ValueError as err:
            if "Missing geo metadata" in str(err):
                return DriverInfo(dtype=None, filetype=meta.type)
            raise
        else:
            return DriverInfo(dtype="gdf", filetype="parquet")
    else:
        return DriverInfo(dtype=None, filetype=meta.type)
