from __future__ import annotations

import tempfile
import warnings
from pathlib import Path
from typing import TYPE_CHECKING

from pins.boards import BaseBoard
from rastr.raster import Raster

if TYPE_CHECKING:
    from collections.abc import Mapping
    from datetime import datetime

    from pins.boards import BaseBoard
    from pins.meta import Meta


def pin_read_raster_tif(
    name: str,
    version: str | None = None,
    hash: str | None = None,  # noqa: A002
    *,
    board: BaseBoard,
) -> Raster:
    """Return the Raster stored in a pin as a GeoTIFF.

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
        The Raster stored in the pin.
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

    return Raster.read_file(filename=filename)


def pin_write_raster_tif(  # noqa: PLR0913
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
        x: A Raster to pin.
        name: Pin name.
        type: File type used to save `x` to disk. Only "tif" is supported.
        title: A title for the pin; most important for shared boards so that others
                can understand what the pin contains. If omitted, a brief description
                of the contents will be automatically generated.
        description: A detailed description of the pin contents.
        metadata: A dictionary containing additional metadata to store with the pin.
                    This gets stored on the Meta.user field.
        versioned: Whether the pin should be versioned. Defaults to versioning, and
                   the alternative is not supported.
        created: Not supported. A date to store in the Meta.created field. This field
                 may be used as part of the pin version name.
        force_identical_write: Not supported. Store the pin even if the pin contents are
                               identical to the last version (compared using the hash).
                               Only the pin contents are compared, not the pin metadata.
                               Defaults to False.
        board: The (geo)pins board to write to.

    Returns:
        Metadata about the stored pin. If `force_identical_write` is False and the
        pin contents are identical to the last version, the last version's metadata
        is returned.
    """
    if type not in (None, "tif"):
        msg = 'Only `type="tif"` is supported for this function.'
        raise ValueError(msg)
    if force_identical_write:
        msg = "`force_identical_write=True` is not supported for Raster pins."
        raise NotImplementedError(msg)
    if versioned is not None:
        msg = "`versioned` is not supported for Raster pins."
        raise NotImplementedError(msg)
    if created is not None:
        msg = "`created` is not supported for Raster pins."
        raise NotImplementedError(msg)

    # Create a temporary file to write the raster
    with tempfile.TemporaryDirectory() as tmpdir:
        tif_path = Path(tmpdir) / f"{name}.tif"
        x.to_file(tif_path)

        with warnings.catch_warnings():
            # Upstream issue relating to opening files without context managers
            warnings.simplefilter("ignore", category=ResourceWarning)

            return board.pin_upload(
                paths=[tif_path.as_posix()],
                name=name,
                title=title,
                description=description,
                metadata=metadata,
            )
