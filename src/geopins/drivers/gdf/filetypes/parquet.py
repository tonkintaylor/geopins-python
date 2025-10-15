from __future__ import annotations

import tempfile
import warnings
from pathlib import Path
from typing import TYPE_CHECKING

import geopandas as gpd

if TYPE_CHECKING:
    from collections.abc import Mapping
    from datetime import datetime

    from geopandas import GeoDataFrame
    from pins.boards import BaseBoard
    from pins.meta import Meta


def pin_read_gdf_geoparquet(
    name: str,
    version: str | None = None,
    hash: str | None = None,  # noqa: A002
    *,
    board: BaseBoard,
) -> GeoDataFrame:
    """Return the GeoDataFrame stored in a pin as a GeoParquet.

    Args:
        name: Pin name.
        version: A specific pin version to retrieve.
        hash: A hash used to validate the retrieved pin data. If specified, it is
                compared against the `pin_hash` field retrieved by
                `pins.boards.BaseBoard.pin_meta`.
        verify_type: The expected datatype of the pin. This is mostly useful for
                        typechecked code.
        board: The (geo)pins board to read from.

    Returns:
        The GeoDataFrame stored in the pin.
    """
    with warnings.catch_warnings():
        # Upstream issue relating to opening files without context managers
        warnings.simplefilter("ignore", category=ResourceWarning)
        filenames = board.pin_download(name=name, version=version, hash=hash)

    try:
        (filename,) = filenames
    except ValueError:
        msg = f"Expected 1 file, got {len(filenames)}"
        raise ValueError(msg) from None

    return gpd.read_parquet(filename)


def pin_write_gdf_parquet(  # noqa: PLR0913
    # N.B. match pins.boards.BaseBoard.pin_write signature
    x: GeoDataFrame,
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
    """Write a GeoDataFrame object to the board as a GeoPackage.

    Args:
        x: A GeoDataFrame to pin.
        name: Pin name.
        type: File type used to save `x` to disk. Only "gpkg" is supported.
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
    if type != "parquet":
        msg = 'Only `type="parquet"` is supported for this function.'
        raise ValueError(msg)
    if force_identical_write:
        msg = "`force_identical_write=True` is not supported for GeoDataFrame pins."
        raise NotImplementedError(msg)
    if versioned is not None:
        msg = "`versioned` is not supported for GeoDataFrame pins."
        raise NotImplementedError(msg)
    if created is not None:
        msg = "`created` is not supported for GeoDataFrame pins."
        raise NotImplementedError(msg)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        path = Path(tmpdir_path) / f"{name}.parquet"
        x.to_parquet(path)

        with warnings.catch_warnings():
            # Upstream issue relating to opening files without context managers
            warnings.simplefilter("ignore", category=ResourceWarning)

            return board.pin_upload(
                paths=[path.as_posix()],
                name=name,
                title=title,
                description=description,
                metadata=metadata,
            )
