from __future__ import annotations

from typing import TYPE_CHECKING

import geopandas as gpd
import pandas as pd
import pytest
from pins import board_folder

import geopins

if TYPE_CHECKING:
    from pathlib import Path


class TestPatch:
    def test_original_method_still_available(self, tmp_path: Path):
        # Arrange
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})

        # Act
        geopins.patch()

        # Assert
        # Writing to a board with non-geospatial data should still work
        # Traps are: recursion, trying to access super()
        board = board_folder(tmp_path.as_posix())
        with pytest.warns(ResourceWarning):
            # Upstream issue with hashing a file which isn't closed properly
            # https://github.com/rstudio/pins-python/pull/335
            board.pin_write(df, "test", type="csv")
        assert len(list(tmp_path.iterdir())) == 1
        out_df = board.pin_read("test")
        pd.testing.assert_frame_equal(df, out_df)

    def test_geospatial_methods_available(self, tmp_path: Path):
        # Arrange

        gdf = gpd.GeoDataFrame(
            {"id": [1, 2, 3]},
            geometry=gpd.points_from_xy([0, 1, 2], [0, 1, 2]),
            crs="EPSG:4326",
        )

        # Act
        geopins.patch()

        # Assert
        board = board_folder(tmp_path.as_posix())
        board.pin_write(gdf, "test", type="parquet")
        assert len(list(tmp_path.iterdir())) == 1
        out_gdf = board.pin_read("test")
        assert isinstance(out_gdf, gpd.GeoDataFrame)
        pd.testing.assert_frame_equal(gdf, out_gdf)
        assert out_gdf.geometry.equals(gdf.geometry)
        assert out_gdf.crs == gdf.crs
