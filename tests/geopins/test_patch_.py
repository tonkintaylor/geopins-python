from __future__ import annotations

from typing import TYPE_CHECKING

import geopandas as gpd
import pandas as pd
import pytest

import geopins

if TYPE_CHECKING:
    from pins.boards import BaseBoard


class TestPatch:
    def test_original_method_still_available(self, tmp_board: BaseBoard):
        # Arrange
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})

        # Act
        geopins.patch()

        # Assert
        # Writing to a board with non-geospatial data should still work
        # Traps are: recursion, trying to access super()
        with pytest.warns(ResourceWarning):
            # Upstream issue relating to opening files without context managers
            tmp_board.pin_write(df, "test", type="csv")

        out_df = tmp_board.pin_read("test")
        pd.testing.assert_frame_equal(df, out_df)

    def test_geospatial_methods_available(self, tmp_board: BaseBoard):
        # Arrange

        gdf = gpd.GeoDataFrame(
            {"id": [1, 2, 3]},
            geometry=gpd.points_from_xy([0, 1, 2], [0, 1, 2]),
            crs="EPSG:4326",
        )

        # Act
        geopins.patch()

        # Assert
        tmp_board.pin_write(gdf, "test", type="parquet")
        out_gdf = tmp_board.pin_read("test")
        assert isinstance(out_gdf, gpd.GeoDataFrame)
        pd.testing.assert_frame_equal(gdf, out_gdf)
        assert out_gdf.geometry.equals(gdf.geometry)
        assert out_gdf.crs == gdf.crs
