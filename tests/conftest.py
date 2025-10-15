from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from pins import board, board_folder

from geopins.boards import GeoBaseBoard

if TYPE_CHECKING:
    from pins.boards import BaseBoard

collect_ignore_glob = ["assets/**"]
pytest_plugins = []


@pytest.fixture(scope="session")
def assets_dir() -> Path:
    """Return a path to the test assets directory."""
    return Path(__file__).parent / "assets"


@pytest.fixture
def tmp_board(tmp_path: Path) -> BaseBoard:
    """Return a board based in a (local) temporary directory."""
    return board_folder(tmp_path.as_posix())


@pytest.fixture
def tmp_geoboard(tmp_path: Path) -> GeoBaseBoard:
    """Return a geo board based in a (local) temporary directory."""
    return board("file", path=tmp_path.as_posix(), board_factory=GeoBaseBoard)  # pyright: ignore[reportReturnType] https://github.com/rstudio/pins-python/issues/347
