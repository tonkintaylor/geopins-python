from __future__ import annotations

import warnings
from typing import TYPE_CHECKING

from geopins.drivers.exceptions import raise_driver_not_supported
from geopins.drivers.infer import infer_driver_info
from geopins.drivers.raster.filetypes.tif import (
    pin_read_raster_tif,
    pin_write_raster_tif,
)
from geopins.interfaces import PinReadKwargDict, PinWriteKwargDict

if TYPE_CHECKING:
    from collections.abc import Mapping
    from datetime import datetime

    from pins.boards import BaseBoard
    from pins.meta import Meta
    from rastr.raster import Raster


def pin_read_raster(
    name: str,
    version: str | None = None,
    hash: str | None = None,  # noqa: A002
    *,
    board: BaseBoard,
) -> Raster:
    """Return the Raster stored in a pin.

    Args:
        name: Pin name.
        version: A specific pin version to retrieve.
        hash: A hash used to validate the retrieved pin data. If specified, it is
                compared against the `pin_hash` field retrieved by
                `pins.boards.BaseBoard.pin_meta`.
        board: The pins board to read from.


    Returns:
        The Raster stored in the pin.
    """
    return _pin_read_raster(name=name, version=version, hash=hash, board=board)


def _pin_read_raster(
    name: str,
    version: str | None = None,
    hash: str | None = None,  # noqa: A002
    *,
    board: BaseBoard,
    meta: Meta | None = None,
) -> Raster:
    # We have this helper variable to pass meta around internally to avoid unnecessary
    # fetching of metadata (although some level of unnecessary passing is inevitable
    # since the underlying pins call will invoke .pin_fetch again). At least this way
    # we avoid fetching three times!
    if meta is None:
        with warnings.catch_warnings():
            # Upstream issue relating to opening files without context managers
            warnings.simplefilter("ignore", category=ResourceWarning)
            meta = board.pin_fetch(name, version)

    kwargs = PinReadKwargDict(
        name=name,
        version=version,
        hash=hash,
    )

    filetype = infer_driver_info(meta, board=board).filetype

    if filetype == "tif":
        return pin_read_raster_tif(board=board, **kwargs)
    else:
        raise_driver_not_supported(filetype, cls=board.__class__, mode="read")
        raise AssertionError  # Change to assert_never after deprecating 3.11 support


def pin_write_raster(  # noqa: PLR0913
    # N.B. match pins.boards.BaseBoard.pin_write signature
    x: Raster,
    name: str | None = None,
    type: str | None = None,  # noqa: A002
    title: str | None = None,
    description: str | None = None,
    metadata: Mapping | None = None,
    versioned: bool | None = None,  # noqa: FBT001
    created: datetime | None = None,
    *,
    force_identical_write: bool = False,
    board: BaseBoard,
) -> Meta:
    """Write a pin object to the board.

    Args:
        x: A rastr.Raster to pin.
        name: Pin name.
        type: File type used to save `x` to disk. May be "tif" only.
        title: A title for the pin; most important for shared boards so that others
                can understand what the pin contains. If omitted, a brief description
                of the contents will be automatically generated.
        description: A detailed description of the pin contents.
        metadata: A dictionary containing additional metadata to store with the pin.
                    This gets stored on the Meta.user field.
        versioned: Whether the pin should be versioned. Defaults to versioning.
        created: A date to store in the Meta.created field. This field may be used
                    as part of the pin version name.
        force_identical_write: Store the pin even if the pin contents are identical
                                to the last version (compared using the hash). Only
                                the pin contents are compared, not the pin metadata.
                                Defaults to False.
        board: The (geo)pins board to write to.

    Returns:
        Metadata about the stored pin. If `force_identical_write` is False and the
        pin contents are identical to the last version, the last version's metadata
        is returned.
    """
    type_ = type

    kwargs = PinWriteKwargDict(
        name=name,
        type=type_,
        title=title,
        description=description,
        metadata=metadata,
        versioned=versioned,
        created=created,
        force_identical_write=force_identical_write,
    )

    if type_ is None:
        type_ = "tif"  # Default to GeoTIFF for rasters

    if type_ == "tif":
        return pin_write_raster_tif(x, board=board, **kwargs)
    else:
        raise_driver_not_supported(type_, cls=board.__class__, mode="write")
        raise AssertionError  # Change to assert_never after deprecating 3.11 support
