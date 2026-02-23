from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from pins.meta import Meta
from rastr.raster import Raster

from geopins.boards import GeoBaseBoard

if TYPE_CHECKING:
    from geopins.boards import GeoBaseBoard


def test_round_trip(tmp_geoboard: GeoBaseBoard):
    # Arrange
    raster = Raster.example()

    # Act
    meta = tmp_geoboard.pin_write(raster, name="test-raster", type="tif")
    assert isinstance(meta, Meta)
    retrieved = tmp_geoboard.pin_read("test-raster", verify_type=Raster)

    # Assert
    assert raster == retrieved


def test_force_identical_write_raises(tmp_geoboard: GeoBaseBoard):
    # Arrange
    raster = Raster.example()

    # Act / Assert
    with pytest.raises(NotImplementedError, match="force_identical_write=True"):
        tmp_geoboard.pin_write(
            raster, name="test-raster", type="tif", force_identical_write=True
        )
