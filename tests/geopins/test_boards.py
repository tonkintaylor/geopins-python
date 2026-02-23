from __future__ import annotations

import pandas as pd
import pytest
from pins.boards import BaseBoard
from rastr.raster import Raster

from geopins import GeoBaseBoard


class TestGeoBaseBoard:
    def test_pin_csv(self, tmp_geoboard: GeoBaseBoard):
        # Arrange
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})

        # Act
        with pytest.warns(ResourceWarning):
            # Upstream issue relating to opening files without context managers
            tmp_geoboard.pin_write(df, "test", type="csv")
        out_df = tmp_geoboard.pin_read("test")
        pd.testing.assert_frame_equal(df, out_df)

    def test_pin_raster(self, tmp_geoboard: GeoBaseBoard):
        # Arrange
        raster = Raster.example()

        # Act
        tmp_geoboard.pin_write(raster, "test")  # N.B. type is optional

        # Assert
        # use the verify_type arg - not provided in original pins
        out_raster = tmp_geoboard.pin_read("test", verify_type=Raster)
        assert isinstance(out_raster, Raster)
        assert out_raster == raster

    def test_verify_type_error(self, tmp_geoboard: GeoBaseBoard):
        # Arrange
        raster = Raster.example()

        # Act
        tmp_geoboard.pin_write(raster, "test")

        # Assert
        with pytest.raises(TypeError):
            tmp_geoboard.pin_read("test", verify_type=str)  # wrong type

    def test_base_board_subtype(self, tmp_geoboard: GeoBaseBoard):
        assert isinstance(tmp_geoboard, GeoBaseBoard)
        assert isinstance(tmp_geoboard, BaseBoard)
