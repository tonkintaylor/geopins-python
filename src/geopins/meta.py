from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pins.boards import BaseBoard
    from pins.meta import Meta


def get_pinned_file_path(*, meta: Meta, board: BaseBoard) -> Path | list[Path]:
    """Get the path to the main data file for a pin, if it exists.

    Args:
        meta: The pin metadata.
        board: The pins board the pin is stored on.

    Returns:
        The path to the main data file for the pin, or None if it doesn't exist.
    """
    file = meta.file

    pin_path = Path(board.construct_path([meta.name, meta.version.version]))

    if not isinstance(file, str):
        return [pin_path / f for f in file]

    return pin_path / file
