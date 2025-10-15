import pins
from pins.boards import BaseBoard

from geopins.boards import GeoBaseBoard


def patch() -> None:
    """Monkey patches pins boards to support geospatial data types.

    This does not affect any custom board subclasses that provide custom implementations
    of `pin_read` or `pin_write`.
    """

    BaseBoard.pin_read = GeoBaseBoard.pin_read  # pyright: ignore[reportAttributeAccessIssue]
    BaseBoard.pin_write = GeoBaseBoard.pin_write  # pyright: ignore[reportAttributeAccessIssue]
    pins.boards.BaseBoard = GeoBaseBoard
