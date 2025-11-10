from __future__ import annotations

from time import sleep
from typing import TYPE_CHECKING

import geopandas as gpd
from pins.meta import Meta

from geopins.boards import GeoBaseBoard

if TYPE_CHECKING:
    from geopins.boards import GeoBaseBoard


def test_round_trip(tmp_geoboard: GeoBaseBoard):
    # Arrange
    gdf = gpd.GeoDataFrame(
        {"id": [1, 2, 3]},
        geometry=gpd.points_from_xy([0, 1, 2], [0, 1, 2]),
        crs="EPSG:2193",  # NZGD2000 / New Zealand Transverse Mercator 2000
    )

    # Act
    meta = tmp_geoboard.pin_write(gdf, name="test-gdf", type="gpkg")
    assert isinstance(meta, Meta)
    retrieved = tmp_geoboard.pin_read("test-gdf", verify_type=gpd.GeoDataFrame)

    # Assert
    assert gdf.equals(retrieved)
    assert gdf.crs == retrieved.crs


def test_hash_is_not_dependent_on_file_write_time(tmp_geoboard: GeoBaseBoard):
    # Arrange
    gdf = gpd.GeoDataFrame(
        {"id": [1, 2, 3]},
        geometry=gpd.points_from_xy([0, 1, 2], [0, 1, 2]),
        crs="EPSG:2193",  # NZGD2000 / New Zealand Transverse Mercator 2000
    )

    # Act
    meta1 = tmp_geoboard.pin_write(gdf, name="test-gdf-hash", type="gpkg")
    sleep(1)
    meta2 = tmp_geoboard.pin_write(gdf, name="test-gdf-hash", type="gpkg")

    # Assert
    assert meta1.pin_hash == meta2.pin_hash
