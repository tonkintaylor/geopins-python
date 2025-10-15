from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, Any, TypeVar, overload

from geopandas import GeoDataFrame
from pins.boards import BaseBoard
from rastr.raster import Raster

from geopins.drivers.gdf.dispatch import _pin_read_gdf, pin_write_gdf
from geopins.drivers.infer import infer_driver_info
from geopins.drivers.raster.dispatch import _pin_read_raster, pin_write_raster
from geopins.interfaces import PinReadKwargDict, PinWriteKwargDict

if TYPE_CHECKING:
    from collections.abc import Mapping
    from datetime import datetime

    from pins.meta import Meta


_T = TypeVar("_T")

# Unpatched methods
base_board_pin_write = BaseBoard.pin_write
base_board_pin_read = BaseBoard.pin_read


class GeoBaseBoard(BaseBoard):
    """A base class for geospatially-enabled pins boards."""

    @overload
    def pin_read(
        self,
        name: str,
        version: str | None = None,
        hash: str | None = None,
        *,
        verify_type: type[_T],
    ) -> _T: ...
    @overload
    def pin_read(
        self,
        name: str,
        version: str | None = None,
        hash: str | None = None,
        *,
        verify_type: None = None,
    ) -> Any: ...
    def pin_read(
        self,
        name: str,
        version: str | None = None,
        hash: str | None = None,  # noqa: A002
        *,
        verify_type: type[_T] | None = None,
    ) -> _T | Any:
        """Return the data stored in a pin.

        Args:
            name: Pin name.
            version: A specific pin version to retrieve.
            hash: A hash used to validate the retrieved pin data. If specified, it is
                  compared against the `pin_hash` field retrieved by
                  `pins.boards.BaseBoard.pin_meta`.
            verify_type: The expected datatype of the pin. This is mostly useful for
                         typechecked code.

        Returns:
            The data stored in the pin.
        """
        kwargs = PinReadKwargDict(
            name=name,
            version=version,
            hash=hash,
        )

        with warnings.catch_warnings():
            # Upstream issue relating to opening files without context managers
            warnings.simplefilter("ignore", category=ResourceWarning)
            meta = self.pin_fetch(name, version)

        driver_info = infer_driver_info(meta, board=self)
        if driver_info.dtype == "gdf":
            value = _pin_read_gdf(board=self, **kwargs, meta=meta)
        elif driver_info.dtype == "raster":
            value = _pin_read_raster(board=self, **kwargs, meta=meta)
        elif driver_info.dtype is None:
            # Otherwise use the default pins implementation.

            # N.B. don't use super(), since we monkeypatch BaseBoard.pin_read and super
            # would try to reference _its_ parent class... but it has none.
            # This is safe to do since there are no other subclasses of BaseBoard
            # which override pin_read. This limitation is documented in .patch().
            with warnings.catch_warnings():
                # Upstream issue relating to opening files without context managers
                warnings.simplefilter("ignore", category=ResourceWarning)
                value = base_board_pin_read(self=self, **kwargs)
        else:
            # Change to assert_never after deprecating 3.11 support
            raise AssertionError

        # N.B. this logic isn't in the original pins implementation, and doesn't make
        # much sense to contribute upstream since Python pins tries tries not to diverge
        # too much from R pins. But it's useful for type safety here.
        if verify_type is not None and not isinstance(value, verify_type):
            msg = f"Expected pin '{name}' to be a {verify_type}, got {type(value)}"
            raise TypeError(msg)
        return value

    def pin_write(  # noqa: PLR0913
        # N.B. match pins.boards.BaseBoard.pin_write signature
        self,
        x: Any,
        name: str | None = None,
        type: str | None = None,  # noqa: A002
        title: str | None = None,
        description: str | None = None,
        metadata: Mapping | None = None,
        versioned: bool | None = None,  # noqa: FBT001
        created: datetime | None = None,
        *,
        force_identical_write: bool = False,
    ) -> Meta:
        """Write a pin object to the board.

        Args:
            x: An object (e.g. a geopandas GeoDataFrame or rastr Raster) to pin.
            name: Pin name.
            type: File type used to save `x` to disk. May be "gpkg", "tif", "csv",
                  "arrow", "parquet", "joblib", or "json".
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

        Returns:
            Metadata about the stored pin. If `force_identical_write` is False and the
            pin contents are identical to the last version, the last version's metadata
            is returned.
        """
        kwargs = PinWriteKwargDict(
            name=name,
            type=type,
            title=title,
            description=description,
            metadata=metadata,
            versioned=versioned,
            created=created,
            force_identical_write=force_identical_write,
        )
        if isinstance(x, GeoDataFrame):
            return pin_write_gdf(x, board=self, **kwargs)
        elif isinstance(x, Raster):
            return pin_write_raster(x, board=self, **kwargs)
        else:
            # Otherwise use the default pins implementation.

            # N.B. don't use super(), since we monkeypatch BaseBoard.pin_read and super
            # would try to reference _its_ parent class... but it has none.
            # This is safe to do since there are no other subclasses of BaseBoard
            # which override pin_read. This limitation is documented in .patch().
            return base_board_pin_write(x=x, self=self, **kwargs)
