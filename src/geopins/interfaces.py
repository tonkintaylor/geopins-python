from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from collections.abc import Mapping
    from datetime import datetime


class PinReadKwargDict(TypedDict):
    """Keyword arguments for `pins.boards.BaseBoard.pin_read`."""

    name: str
    version: str | None
    hash: str | None


class PinWriteKwargDict(TypedDict):
    """Keyword arguments for `pins.boards.BaseBoard.pin_write`."""

    name: str | None
    type: str | None
    title: str | None
    description: str | None
    metadata: Mapping | None
    versioned: bool | None
    created: datetime | None
    force_identical_write: bool
