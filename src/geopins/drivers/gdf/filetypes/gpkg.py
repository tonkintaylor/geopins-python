from __future__ import annotations

import tempfile
import warnings
from pathlib import Path
from sqlite3 import connect
from typing import TYPE_CHECKING

import geopandas as gpd

if TYPE_CHECKING:
    from collections.abc import Mapping
    from datetime import datetime

    from geopandas import GeoDataFrame
    from pins.boards import BaseBoard
    from pins.meta import Meta


def pin_read_gdf_gpkg(
    name: str,
    version: str | None = None,
    hash: str | None = None,  # noqa: A002
    *,
    board: BaseBoard,
) -> GeoDataFrame:
    """Return the GeoDataFrame stored in a pin as a GeoPackage.

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

    return gpd.read_file(filename)


def pin_write_gdf_gpkg(  # noqa: PLR0913
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
    if type != "gpkg":
        msg = 'Only `type="gpkg"` is supported for this function.'
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

        path = Path(tmpdir_path) / f"{name}.gpkg"
        x.to_file(path, driver="GPKG")

        # Overwrite the modification time to keep hashing stable and release locks.
        _snapshot_last_change(path=path)

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


def _snapshot_last_change(path: Path) -> None:
    """Set the last_change timestamp to Unix epoch to keep GeoPackage hashing stable."""

    # Avoid `with connect(...)` because the context manager delays handle release on
    # Windows, which keeps the temporary GeoPackage locked during cleanup.
    conn = connect(path.as_posix())
    try:
        conn.execute(
            """
            UPDATE gpkg_contents
            SET last_change = '1970-01-01T00:00:00Z';
            """
        )
        conn.commit()
    finally:
        conn.close()
