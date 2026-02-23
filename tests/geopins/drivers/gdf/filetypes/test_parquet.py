from __future__ import annotations

from typing import TYPE_CHECKING

import geopandas as gpd
import pytest
from pins.meta import Meta

from geopins.boards import GeoBaseBoard

if TYPE_CHECKING:
    from geopins.boards import GeoBaseBoard


def test_round_trip(tmp_geoboard: GeoBaseBoard):
    # Arrange
    gdf = gpd.GeoDataFrame(
        {"id": [1, 2, 3]},
        geometry=gpd.points_from_xy([0, 1, 2], [0, 1, 2]),
        crs="EPSG:4326",
    )

    # Act
    meta = tmp_geoboard.pin_write(gdf, name="test-gdf", type="parquet")
    assert isinstance(meta, Meta)
    retrieved = tmp_geoboard.pin_read("test-gdf", verify_type=gpd.GeoDataFrame)

    # Assert
    assert gdf.equals(retrieved)


def test_force_identical_write_raises(tmp_geoboard: GeoBaseBoard):
    # Arrange
    gdf = gpd.GeoDataFrame(
        {"id": [1, 2, 3]},
        geometry=gpd.points_from_xy([0, 1, 2], [0, 1, 2]),
        crs="EPSG:4326",
    )

    # Act / Assert
    with pytest.raises(NotImplementedError, match="force_identical_write=True"):
        tmp_geoboard.pin_write(
            gdf, name="test-gdf", type="parquet", force_identical_write=True
        )
